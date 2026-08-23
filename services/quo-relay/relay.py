"""Shared relay logic: allowlist gate, Nou dispatch, reply, phone_events write.

Both poll.py and webhook.py call handle_inbound(). It is idempotent on
quo_message_id via the unique constraint on phone_events; a duplicate
inbound is a no-op (logged as such and no reply is sent).

STOP short-circuits before dispatch and clears the sender from the
in-memory session cache. Because no binding table exists in this tier,
STOP does not write to any binding record; it is a session reset only.

Nothing here fails open. A failure to write to phone_events, a failure
to reach Nou, or a failure to POST the reply all abort the turn and
leave nothing acted. The record is the truth; if it did not land in
phone_events, it did not happen.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import time
from dataclasses import dataclass, field
from typing import Optional

import requests

log = logging.getLogger("quo-relay")

QUO_API_BASE = "https://api.quo.com/v1"
STOP_TOKENS = {"stop", "unsubscribe", "cancel", "end", "quit"}


@dataclass
class Config:
    quo_api_key: str
    phone_number_id: str
    line_e164: str
    allowlist: frozenset[str]
    cis_url: str
    cis_phone_relay_key: str
    # SMS-03 tier two. All optional: absent, the service runs pure
    # tier one and touches neither phone_bindings nor the Buzz relay.
    cis_phone_router_key: str = ""
    cis_phone_binder_key: str = ""
    ceremony_channel_id: str = ""
    owner_pubkey: str = ""
    agent_pubkey: str = ""

    @property
    def tier2(self) -> bool:
        return bool(self.cis_phone_router_key)

    @classmethod
    def from_env(cls) -> "Config":
        required = ["QUO_API_KEY", "QUO_PHONE_NUMBER_ID", "QUO_LINE_E164",
                    "QUO_ALLOWLIST", "CIS_URL", "CIS_PHONE_RELAY_KEY"]
        missing = [k for k in required if not os.environ.get(k)]
        if missing:
            raise RuntimeError(f"missing env: {', '.join(missing)}")
        return cls(
            quo_api_key=os.environ["QUO_API_KEY"],
            phone_number_id=os.environ["QUO_PHONE_NUMBER_ID"],
            line_e164=os.environ["QUO_LINE_E164"],
            allowlist=frozenset(
                x.strip() for x in os.environ["QUO_ALLOWLIST"].split(",") if x.strip()
            ),
            cis_url=os.environ["CIS_URL"],
            cis_phone_relay_key=os.environ["CIS_PHONE_RELAY_KEY"],
            cis_phone_router_key=os.environ.get("CIS_PHONE_ROUTER_KEY", ""),
            cis_phone_binder_key=os.environ.get("CIS_PHONE_BINDER_KEY", ""),
            ceremony_channel_id=os.environ.get("BUZZ_CEREMONY_CHANNEL_ID", ""),
            owner_pubkey=os.environ.get("BUZZ_OWNER_PUBKEY", ""),
            agent_pubkey=os.environ.get("BUZZ_AGENT_PUBKEY", ""),
        )


@dataclass
class InboundMessage:
    """Normalised inbound as extracted from either poll or webhook."""
    quo_message_id: str
    conversation_id: str
    peer_e164: str
    text: str
    created_at: str
    raw: dict = field(default_factory=dict)


# --- persistence -----------------------------------------------------------

def log_event(cfg: Config, *, direction: str, peer: str, content: str,
              quo_message_id: Optional[str] = None,
              conversation_id: Optional[str] = None,
              status: Optional[str] = None, error: Optional[str] = None,
              payload: Optional[dict] = None) -> bool:
    """Write one phone_events row via the Supabase REST API.

    Returns False on duplicate (unique quo_message_id already present) or
    write failure. Callers must check the return value; on False, do not
    proceed with any further side effect.
    """
    url = f"{cfg.cis_url}/rest/v1/phone_events"
    body = {
        "direction": direction,
        "peer_e164": peer,
        "content": content,
        "quo_message_id": quo_message_id,
        "conversation_id": conversation_id,
        "status": status,
        "error": error,
        "payload": payload or {},
    }
    headers = {
        "apikey": cfg.cis_phone_relay_key,
        "Authorization": f"Bearer {cfg.cis_phone_relay_key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }
    r = requests.post(url, headers=headers, json=body, timeout=10)
    if r.status_code == 409:
        log.info("phone_events duplicate on %s, skipping", quo_message_id)
        return False
    if not r.ok:
        log.error("phone_events write failed: %s %s", r.status_code, r.text)
        return False
    return True


# --- dispatch --------------------------------------------------------------

def dispatch_to_nou(peer: str, text: str) -> str:
    """Hand the inbound to Nou and return the reply.

    Placeholder shape for the first PR: shells out to the openclaw CLI
    with a one-shot agent turn. Conversation history is not threaded
    in this PR; each inbound is a fresh call. When the ACP bridge
    integration lands, this function is the one seam that changes.

    The prompt is deliberately terse and includes the tier constraints
    inline. Nou is expected to know its identity and voice from core
    memory; this is just the payload frame.
    """
    prompt = (
        f"[SMS from steward, tier 1 read-only, peer={peer}]\n\n{text}\n\n"
        "Reply in one to three sentences. No markdown. No headers. "
        "Never quote a confidential record, another member's contact "
        "detail, or an unpublished treasury figure. If the ask needs a "
        "write, say so and stop."
    )
    cmd = [os.environ.get("NOU_ACP_COMMAND", "openclaw"),
           "agent", "--agent", os.environ.get("NOU_AGENT_ID", "main"),
           "-m", prompt]
    result = subprocess.run(
        cmd, capture_output=True, text=True,
        timeout=int(os.environ.get("NOU_DISPATCH_TIMEOUT_SEC", "180")),
    )
    if result.returncode != 0:
        raise RuntimeError(f"nou dispatch failed: {result.stderr[:400]}")
    reply = result.stdout.strip()
    if not reply:
        raise RuntimeError("nou dispatch returned empty reply")
    # SMS body cap: soft 320 chars (~2 segments), hard 4096. Trim safely.
    if len(reply) > 320:
        reply = reply[:317] + "..."
    return reply


# --- reply -----------------------------------------------------------------

def send_reply(cfg: Config, peer: str, content: str) -> dict:
    """POST /v1/messages. Returns the API response body on success.

    Raises on any non-2xx; callers log_event(direction='out') only after
    this returns successfully. status='sent' from the API is the send
    accept, not delivery; a later delivered/undelivered lands via a
    separate status event we do not consume in this PR.
    """
    r = requests.post(
        f"{QUO_API_BASE}/messages",
        headers={"Authorization": cfg.quo_api_key, "Content-Type": "application/json"},
        json={"from": cfg.line_e164, "to": [peer], "content": content},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()["data"]


# --- the whole turn --------------------------------------------------------

def handle_inbound(cfg: Config, msg: InboundMessage,
                   router=None, binder=None, bridge=None) -> None:
    """One inbound message, start to finish. Never raises to the caller.

    Every branch writes at least one phone_events row so a walker can
    audit what the service did with each message.

    Tier two (SMS-03): when router/binder/bridge are supplied and the
    peer holds a verified binding, the exchange is mirrored into the
    binding's private Buzz channel and STOP revokes the binding with
    the one confirmation the carrier rules require. Unbound peers fall
    through to the tier-one allowlist path unchanged.
    """
    peer = msg.peer_e164

    # Log the inbound first, unconditionally. If this write fails or is a
    # duplicate we abort; both are correct outcomes.
    if not log_event(cfg, direction="in", peer=peer, content=msg.text,
                     quo_message_id=msg.quo_message_id,
                     conversation_id=msg.conversation_id,
                     status="received", payload=msg.raw):
        return

    binding = None
    if router is not None:
        try:
            binding = router.lookup_verified_by_e164(peer)
        except Exception as e:
            # Fail closed on the widening: a router outage narrows the
            # service to tier one, never widens it.
            log.error("binding lookup failed, tier-one path only: %s", e)

    # Gate. A verified binding admits; otherwise the tier-one allowlist
    # decides. Unknown numbers: log the drop, no reply, no oracle.
    if binding is None and peer not in cfg.allowlist:
        log_event(cfg, direction="in", peer=peer, content="",
                  status="ignored_not_allowlisted",
                  conversation_id=msg.conversation_id)
        return

    # STOP. Bound peer: revoke the binding and send the one required
    # confirmation (design §4). Tier-one peer: honoured silently, as
    # SMS-01 shipped it, because there is no binding to revoke.
    if msg.text.strip().lower() in STOP_TOKENS:
        if binding is not None and binder is not None:
            try:
                binder.revoke(binding["id"], "sms_stop")
                api_resp = send_reply(
                    cfg, peer, "Unsubscribed. Your Techne binding is revoked; "
                    "no further messages. Re-bind any time from Buzz.")
                log_event(cfg, direction="out", peer=peer,
                          content="stop_confirmation",
                          quo_message_id=api_resp.get("id"),
                          conversation_id=api_resp.get("conversationId"),
                          status="stop_confirmed")
                if bridge is not None and binding.get("buzz_channel_id"):
                    bridge.post(binding["buzz_channel_id"],
                                "[bridge] STOP received; binding revoked.")
            except Exception as e:
                log.exception("stop revocation failed")
                log_event(cfg, direction="in", peer=peer, content=msg.text,
                          status="stop_revoke_failed", error=str(e)[:400],
                          conversation_id=msg.conversation_id)
            return
        log_event(cfg, direction="in", peer=peer, content=msg.text,
                  status="stopped", conversation_id=msg.conversation_id)
        return

    # Mirror the inbound into the bound room before dispatch, framed as
    # bridged (design §5): provenance, not authority.
    channel = binding.get("buzz_channel_id") if binding else None
    if bridge is not None and channel:
        bridge.post(channel, f"[SMS · {peer}] {msg.text}")

    # Dispatch.
    try:
        reply = dispatch_to_nou(peer, msg.text)
    except Exception as e:
        log.exception("dispatch failed")
        log_event(cfg, direction="in", peer=peer, content=msg.text,
                  status="dispatch_failed", error=str(e)[:400],
                  conversation_id=msg.conversation_id)
        return

    # Reply.
    try:
        api_resp = send_reply(cfg, peer, reply)
    except Exception as e:
        log.exception("send_reply failed")
        log_event(cfg, direction="out", peer=peer, content=reply,
                  status="send_failed", error=str(e)[:400],
                  conversation_id=msg.conversation_id)
        return

    log_event(cfg, direction="out", peer=peer, content=reply,
              quo_message_id=api_resp.get("id"),
              conversation_id=api_resp.get("conversationId"),
              status=api_resp.get("status"),
              payload=api_resp)

    # Mirror the reply into the room, so phone and room hold one
    # transcript. Logged to phone_events already; the room copy is a
    # convenience view and its failure does not undo the send.
    if bridge is not None and channel:
        bridge.post(channel, reply)
