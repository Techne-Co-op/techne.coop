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
    cis_service_role_key: str
    nou_acp_command: str = "openclaw"
    nou_acp_args: tuple[str, ...] = ("acp",)

    @classmethod
    def from_env(cls) -> "Config":
        required = ["QUO_API_KEY", "QUO_PHONE_NUMBER_ID", "QUO_LINE_E164",
                    "QUO_ALLOWLIST", "CIS_URL", "CIS_SERVICE_ROLE_KEY"]
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
            cis_service_role_key=os.environ["CIS_SERVICE_ROLE_KEY"],
            nou_acp_command=os.environ.get("NOU_ACP_COMMAND", "openclaw"),
            nou_acp_args=tuple(os.environ.get("NOU_ACP_ARGS", "acp").split()),
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
        "apikey": cfg.cis_service_role_key,
        "Authorization": f"Bearer {cfg.cis_service_role_key}",
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
    with a one-shot prompt that carries the sender and the message.
    Conversation history is not threaded in this PR; each inbound is a
    fresh call. When the ACP bridge integration lands, this function is
    the one seam that changes.

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
    result = subprocess.run(
        [os.environ.get("NOU_ACP_COMMAND", "openclaw"), "--prompt", prompt],
        capture_output=True, text=True, timeout=60,
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

def handle_inbound(cfg: Config, msg: InboundMessage) -> None:
    """One inbound message, start to finish. Never raises to the caller.

    Every branch writes at least one phone_events row so a walker can
    audit what the service did with each message.
    """
    peer = msg.peer_e164

    # Log the inbound first, unconditionally. If this write fails or is a
    # duplicate we abort; both are correct outcomes.
    if not log_event(cfg, direction="in", peer=peer, content=msg.text,
                     quo_message_id=msg.quo_message_id,
                     conversation_id=msg.conversation_id,
                     status="received", payload=msg.raw):
        return

    # Allowlist gate. Not on the list: log the drop, do not reply, do not
    # dispatch. Silence to unknown numbers is a feature, not a defect.
    if peer not in cfg.allowlist:
        log_event(cfg, direction="in", peer=peer, content="",
                  status="ignored_not_allowlisted",
                  conversation_id=msg.conversation_id)
        return

    # STOP: skip dispatch, do not reply. STOP is honoured silently in this
    # tier because there is no binding to revoke; a courteous confirmation
    # lands when Phase 1 proper adds bindings.
    if msg.text.strip().lower() in STOP_TOKENS:
        log_event(cfg, direction="in", peer=peer, content=msg.text,
                  status="stopped", conversation_id=msg.conversation_id)
        return

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
