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
import re
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

    @property
    def ceremony_channel_ids(self) -> tuple[str, ...]:
        """BUZZ_CEREMONY_CHANNEL_ID accepts a comma-separated list so each
        member can hold a private ceremony room (a number posted in !bind
        must not be readable by other members)."""
        return tuple(
            x.strip() for x in self.ceremony_channel_id.split(",") if x.strip()
        )

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

def _sender_frame(peer: str, binding: Optional[dict]) -> str:
    """One line naming who this text is from, and on what evidence.

    A verified binding is an identity claim the ceremony actually made:
    the member proved control of the number by code and answered from
    their own Nostr key. The allowlist is weaker - a number in the
    service env, nothing else - and says so.
    """
    if binding and binding.get("member_pubkey"):
        return (f"SMS from verified bound member {binding['member_pubkey'][:16]}, "
                f"peer={peer}, binding verified by ceremony, tier 1 read-only. "
                f"This is not the steward unless that key is the steward's")
    return (f"SMS from an allowlisted number, peer={peer}, "
            f"no binding and no key evidence, tier 1 read-only")


def dispatch_to_nou(peer: str, text: str,
                    binding: Optional[dict] = None) -> str:
    """Hand the inbound to Nou and return the reply.

    Placeholder shape for the first PR: shells out to the openclaw CLI
    with a one-shot agent turn. Conversation history is not threaded
    in this PR; each inbound is a fresh call. When the ACP bridge
    integration lands, this function is the one seam that changes.

    The prompt is deliberately terse and includes the tier constraints
    inline. Nou is expected to know its identity and voice from core
    memory; this is just the payload frame.

    The frame names who actually texted. It used to say "from steward"
    for every peer, so a correctly bound member arrived wearing the
    steward's label and the agent read the mismatch as an intruder
    (Aaron Neyer, 2026-08-24). A frame that can only describe one person
    is wrong in both directions: it slanders a member, and it would have
    handed a stranger the steward's standing.
    """
    prompt = (
        f"[{_sender_frame(peer, binding)}]\n\n{text}\n\n"
        "Reply in one or two sentences and stay under 300 characters. "
        "Every 160 characters is a billed segment, so length costs money "
        "on every answer; a third sentence is almost always the one to "
        "cut. Put the answer first; drop the preamble, the caveats that "
        "change nothing, and the closing summary. If the full answer will "
        "not fit, give the one-line version and offer the rest on Buzz. "
        "Plain ASCII only: no markdown, no headers, no emoji, no curly "
        "quotes, no em dashes. One non-ASCII character drops the segment "
        "size from 160 to 70 and more than doubles the cost. "
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
    return reply


# --- length ----------------------------------------------------------------

# A modern handset concatenates segments, so the cap is about money rather
# than about the carrier: Quo bills $0.01 per 160-character GSM-7 segment of
# every API-sent message, and the balance running dry fails every send with
# a 402 and no warning (2026-08-25). Two parts of two segments each puts the
# worst case at four cents a reply. Split on sentence boundaries and never
# emit a trailing ellipsis: a reply either ends where a sentence ends or the
# member is told plainly that the rest was dropped.
SMS_PART_CHARS = int(os.environ.get("NOU_SMS_PART_CHARS", "320"))
SMS_MAX_PARTS = int(os.environ.get("NOU_SMS_MAX_PARTS", "2"))

# One non-GSM-7 character re-encodes the WHOLE message at 70 chars per
# segment, so a single curly quote or em dash can more than double the cost
# of an otherwise plain reply. The model is told to write ASCII; this is the
# belt to that suspenders, applied before the split so the length maths and
# the billing agree.
_GSM_SUBSTITUTIONS = {
    "\u2018": "'", "\u2019": "'", "\u201a": "'", "\u201b": "'",
    "\u201c": '"', "\u201d": '"', "\u201e": '"',
    "\u2013": "-", "\u2014": "-", "\u2015": "-", "\u2212": "-",
    "\u2026": "...", "\u2022": "*", "\u2192": "->", "\u00d7": "x",
    "\u00a0": " ", "\u2009": " ", "\u202f": " ",
}

# The GSM 03.38 basic set plus its extension characters. Anything outside
# this set forces UCS-2 encoding on the entire message.
_GSM7_CHARS = frozenset(
    "@\u00a3$\u00a5\u00e8\u00e9\u00f9\u00ec\u00f2\u00c7\n\u00d8\u00f8\r"
    "\u00c5\u00e5\u0394_\u03a6\u0393\u039b\u03a9\u03a0\u03a8\u03a3\u0398"
    "\u039e\u00c6\u00e6\u00df\u00c9 !\"#\u00a4%&'()*+,-./0123456789:;<=>?"
    "\u00a1ABCDEFGHIJKLMNOPQRSTUVWXYZ\u00c4\u00d6\u00d1\u00dc\u00a7"
    "\u00bfabcdefghijklmnopqrstuvwxyz\u00e4\u00f6\u00f1\u00fc\u00e0"
    "^{}\\[~]|\u20ac"
)


def to_gsm7(text: str) -> str:
    """Fold a reply down to characters that bill at 160 per segment.

    Known punctuation is substituted for its ASCII equivalent; anything
    else outside the GSM-7 set (emoji, accented letters, symbols) is
    dropped rather than transliterated, because a mangled word is easier
    for a member to read past than a doubled bill is to notice.
    """
    for bad, good in _GSM_SUBSTITUTIONS.items():
        text = text.replace(bad, good)
    kept = "".join(c for c in text if c in _GSM7_CHARS)
    return re.sub(r"[ \t]{2,}", " ", kept).strip()


_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


def split_for_sms(reply: str,
                  part_chars: int = SMS_PART_CHARS,
                  max_parts: int = SMS_MAX_PARTS) -> list[str]:
    """Split a reply into whole-sentence parts fitting the per-part cap.

    Never cuts a sentence in half unless a single sentence exceeds the cap,
    in which case it breaks on a word boundary. If the reply needs more than
    max_parts, the overflow is dropped and the last part says so, because a
    silent truncation reads as a complete answer when it is not.

    The reply is folded to GSM-7 first, so the character counts here are the
    counts the carrier bills on.
    """
    reply = to_gsm7(reply)
    if not reply:
        raise ValueError("reply held nothing sendable after GSM-7 folding")
    if len(reply) <= part_chars:
        return [reply]

    pieces: list[str] = []
    for sentence in _SENTENCE_END.split(reply):
        while len(sentence) > part_chars:
            cut = sentence.rfind(" ", 0, part_chars)
            if cut <= 0:
                cut = part_chars
            pieces.append(sentence[:cut].strip())
            sentence = sentence[cut:].strip()
        if sentence:
            pieces.append(sentence)

    parts: list[str] = []
    for piece in pieces:
        if parts and len(parts[-1]) + 1 + len(piece) <= part_chars:
            parts[-1] = f"{parts[-1]} {piece}"
        else:
            parts.append(piece)

    if len(parts) > max_parts:
        dropped = len(parts) - max_parts
        parts = parts[:max_parts]
        note = f"[{dropped} more part(s) not sent; ask and I will continue]"
        if len(parts[-1]) + 1 + len(note) <= part_chars:
            parts[-1] = f"{parts[-1]} {note}"
        else:
            # The note goes as its own short message rather than displacing
            # content the member would otherwise have received.
            parts.append(note)
    return parts


# --- reply -----------------------------------------------------------------

def send_reply(cfg: Config, peer: str, content: str) -> dict:
    """POST /v1/messages. Returns the API response body on success.

    Raises on any non-2xx; callers log_event(direction='out') only after
    this returns successfully. status='sent' from the API is the send
    accept, not delivery; a later delivered/undelivered lands via a
    separate status event we do not consume in this PR.

    The response body is logged on failure. The status line alone is not
    enough to act on: a 402 says only "Payment Required", while the body
    says the credit balance is empty, which is a different fix from an
    unpaid invoice and cost ten minutes to find by hand on 2026-08-25.
    """
    r = requests.post(
        f"{QUO_API_BASE}/messages",
        headers={"Authorization": cfg.quo_api_key, "Content-Type": "application/json"},
        json={"from": cfg.line_e164, "to": [peer], "content": content},
        timeout=10,
    )
    if r.status_code >= 400:
        log.error("quo send %s: %s", r.status_code, r.text[:400])
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
        reply = dispatch_to_nou(peer, msg.text, binding)
    except Exception as e:
        log.exception("dispatch failed")
        log_event(cfg, direction="in", peer=peer, content=msg.text,
                  status="dispatch_failed", error=str(e)[:400],
                  conversation_id=msg.conversation_id)
        return

    # Reply. Long answers go as ordered parts, each its own logged send;
    # the last response is the one carried into the event below.
    parts: list[str] = []
    try:
        parts = split_for_sms(reply)
        for part in parts[:-1]:
            resp = send_reply(cfg, peer, part)
            log_event(cfg, direction="out", peer=peer, content=part,
                      quo_message_id=resp.get("id"),
                      conversation_id=resp.get("conversationId"),
                      status=resp.get("status"), payload=resp)
        api_resp = send_reply(cfg, peer, parts[-1])
        reply = parts[-1]
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
    #
    # The prefix matters: an unlabelled copy of an SMS reply reads in the
    # room as though the agent answered twice, once by text and once in
    # channel (steward's report, 2026-08-25). It is one answer, shown
    # where it was sent. Every part is mirrored, not just the last, or
    # the room holds a shorter transcript than the phone does.
    if bridge is not None and channel:
        bridge.post(channel, "[SMS \u00b7 out] " + " ".join(parts))
