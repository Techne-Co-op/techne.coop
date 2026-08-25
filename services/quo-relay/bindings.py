"""SMS-03 ceremony and binding lookup, per the SMS-02 design (§3, §4).

The ceremony lives in Buzz channels (the harness drops non-owner DMs by
design). A member posts `!bind +1XXXXXXXXXX` in the ceremony channel;
the service sends a one-time code over the co-op line, and the member
posts `!verify <code>` back in the same channel under the same Nostr
key. Possession of the phone is proven by receiving the code; control
of the key is proven by the relay-verified signature on the reply.
Caller-ID never enters the proof.

All CIS access here uses the phone_binder scoped key (SELECT, INSERT,
UPDATE on phone_bindings only). The routing path in relay.py uses the
narrower phone_router key.
"""

from __future__ import annotations

import hashlib
import logging
import re
import secrets
import time
from typing import Optional

import requests

log = logging.getLogger("quo-relay.bindings")

BIND_RE = re.compile(r"^!bind\s+(\+[1-9][0-9]{7,14})\s*$")
VERIFY_RE = re.compile(r"^!verify\s+([0-9]{6})\s*$")

CODE_TTL_SEC = 600            # design §3: single-use, expiring in ten minutes
MAX_CHALLENGES_PER_DAY = 3    # design §3: at most three sends per number per day


def _binding_note(row: dict, pubkey: str) -> str:
    """The first message in a binding room: what the ceremony proved."""
    return (
        "Binding ceremony complete.\n\n"
        f"Number: {row['peer_e164']}\n"
        f"Member key: {pubkey}\n"
        f"Verified: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n"
        f"Binding id: {row['id']}\n\n"
        "This room is the transcript for that number. Texts arriving from "
        "it are from a member who proved control of the number with a "
        "one-time code and answered from the key above; they are not an "
        "unknown caller and not the steward. Lines prefixed [SMS] are "
        "mirrored phone traffic, not fresh channel messages. STOP by SMS "
        "revokes the binding."
    )


def _hash(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


class BindingStore:
    """phone_bindings access under a scoped key (binder or router)."""

    def __init__(self, cis_url: str, key: str):
        self.base = f"{cis_url}/rest/v1/phone_bindings"
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }

    def _get(self, params: dict) -> list[dict]:
        r = requests.get(self.base, headers=self.headers, params=params, timeout=10)
        r.raise_for_status()
        return r.json()

    def lookup_verified_by_e164(self, e164: str) -> Optional[dict]:
        rows = self._get({"peer_e164": f"eq.{e164}", "status": "eq.verified"})
        return rows[0] if rows else None

    def lookup_verified_by_pubkey(self, pubkey: str) -> Optional[dict]:
        rows = self._get({"member_pubkey": f"eq.{pubkey}", "status": "eq.verified"})
        return rows[0] if rows else None

    def verified_bindings(self) -> list[dict]:
        return self._get({"status": "eq.verified"})

    def pending_for_pubkey(self, pubkey: str) -> Optional[dict]:
        rows = self._get({"member_pubkey": f"eq.{pubkey}", "status": "eq.pending",
                          "order": "requested_at.desc", "limit": "1"})
        return rows[0] if rows else None

    def challenges_today(self, e164: str) -> int:
        since = time.strftime("%Y-%m-%dT00:00:00Z", time.gmtime())
        rows = self._get({"peer_e164": f"eq.{e164}",
                          "requested_at": f"gte.{since}", "select": "id"})
        return len(rows)

    def insert_pending(self, pubkey: str, e164: str, code: str,
                       request_event_id: str,
                       challenge_event_id: Optional[str]) -> None:
        r = requests.post(self.base, headers={**self.headers,
                          "Prefer": "return=minimal"}, json={
            "member_pubkey": pubkey, "peer_e164": e164,
            "status": "pending", "code_hash": _hash(code),
            "request_event_id": request_event_id,
            "challenge_event_id": challenge_event_id,
        }, timeout=10)
        r.raise_for_status()

    def _patch(self, binding_id: str, body: dict) -> None:
        r = requests.patch(f"{self.base}?id=eq.{binding_id}",
                           headers={**self.headers, "Prefer": "return=minimal"},
                           json=body, timeout=10)
        r.raise_for_status()

    def mark_verified(self, binding_id: str, response_event_id: str) -> None:
        self._patch(binding_id, {
            "status": "verified", "code_hash": None,
            "response_event_id": response_event_id,
            "verified_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        })

    def set_channel(self, binding_id: str, channel_id: str) -> None:
        self._patch(binding_id, {"buzz_channel_id": channel_id})

    def revoke(self, binding_id: str, reason: str) -> None:
        self._patch(binding_id, {
            "status": "revoked", "revoke_reason": reason,
            "revoked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        })


class Ceremony:
    """Drives the bind/verify flow from ceremony-channel messages.

    The caller feeds it relay messages (author pubkey + content + event
    id); it answers with a reply text to post back into the channel, or
    None for messages that are not ceremony commands.
    """

    def __init__(self, store: BindingStore, send_sms, bridge):
        self.store = store          # BindingStore with the binder key
        self.send_sms = send_sms    # (e164, text) -> phone_events id or None
        self.bridge = bridge        # BuzzBridge, for channel creation

    def handle_message(self, author_pubkey: str, content: str,
                       event_id: str, owner_pubkey: str,
                       agent_pubkey: str) -> Optional[str]:
        m = BIND_RE.match(content.strip())
        if m:
            return self._start(author_pubkey, m.group(1), event_id)
        m = VERIFY_RE.match(content.strip())
        if m:
            return self._verify(author_pubkey, m.group(1), event_id,
                                owner_pubkey, agent_pubkey)
        return None

    def _start(self, pubkey: str, e164: str, event_id: str) -> str:
        if self.store.lookup_verified_by_pubkey(pubkey):
            return "you already hold a verified binding. STOP by SMS or ask the steward to revoke it before binding again."
        if self.store.lookup_verified_by_e164(e164):
            return "that number already holds a live binding. Re-binding a number that moves between members carries delay and notice (issue #191); ask the steward."
        if self.store.challenges_today(e164) >= MAX_CHALLENGES_PER_DAY:
            return "challenge limit reached for that number today. Try again tomorrow."
        code = f"{secrets.randbelow(1000000):06d}"
        # send_sms returns truthy on carrier accept (the Quo message id
        # when available), falsy on failure. The phone_events row is the
        # durable record either way; challenge_event_id stays null
        # because the INSERT-only relay key cannot read the id back.
        sent = self.send_sms(
            e164,
            f"Techne binding code: {code}. Post '!verify {code}' in the Buzz ceremony channel within 10 minutes. Not requested? Ignore this.")
        if not sent:
            return "could not send the challenge SMS; nothing was recorded. Try again."
        self.store.insert_pending(pubkey, e164, code, event_id, None)
        return f"challenge sent to {e164[:3]}...{e164[-4:]}. Post !verify <code> here within 10 minutes, from this same key."

    def _verify(self, pubkey: str, code: str, event_id: str,
                owner_pubkey: str, agent_pubkey: str) -> str:
        row = self.store.pending_for_pubkey(pubkey)
        if not row:
            return "no pending challenge for your key. Start with !bind +1XXXXXXXXXX."
        age = time.time() - time.mktime(time.strptime(
            row["requested_at"][:19], "%Y-%m-%dT%H:%M:%S"))
        if age > CODE_TTL_SEC:
            self.store.revoke(row["id"], "expired")
            return "that challenge expired. Start again with !bind."
        if _hash(code) != row["code_hash"]:
            return "code does not match. Check the SMS and try !verify again."
        self.store.mark_verified(row["id"], event_id)
        channel_id = self.bridge.create_binding_channel(
            member_pubkey=pubkey, owner_pubkey=owner_pubkey,
            label=row["peer_e164"][-4:],
            seed=str(row["id"]).replace("-", "")[:6])
        if channel_id:
            self.store.set_channel(row["id"], channel_id)
            # Seed the room with what the ceremony established. A reader
            # arriving later - member, steward, or an agent session with
            # no memory of the ceremony - should find the binding stated
            # rather than have to infer it from a phone number, which is
            # how a verified member once got read as an intruder here
            # (2026-08-24).
            self.bridge.post(channel_id, _binding_note(row, pubkey))
            return (f"verified. {row['peer_e164']} is bound to your key. "
                    f"Your private SMS room is open; texts to the co-op line "
                    f"from your number now land there. STOP by SMS revokes.")
        return ("verified, but the private channel could not be created; "
                "the binding stands and the room will be retried. "
                "Tell the steward if this persists.")
