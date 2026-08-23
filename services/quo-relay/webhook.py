"""HTTP webhook receiver for message.received. NOT DEPLOYED BY THIS PR.

Present here so the two runtime shapes can be reviewed together and so
the poll loop can be retired cleanly when DNS and Cloudflare fronting
land. Do not enable this and poll.py at the same time; the phone_events
unique constraint on quo_message_id protects the record, but the service
emits warnings on every collision.

Signature scheme follows OpenPhone's HMAC-SHA256 over the raw request
body, base64-encoded, delivered in the openphone-signature header. See
quo.com/docs for the current header names; verify at deploy time.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import os
from typing import Optional

from flask import Flask, request, jsonify, abort

from relay import Config, InboundMessage, handle_inbound

log = logging.getLogger("quo-relay.webhook")

app = Flask(__name__)
_cfg: Optional[Config] = None
_signing_key: Optional[bytes] = None


def _init() -> None:
    global _cfg, _signing_key
    _cfg = Config.from_env()
    key_hex = os.environ.get("QUO_WEBHOOK_SIGNING_KEY", "")
    if not key_hex:
        raise RuntimeError("QUO_WEBHOOK_SIGNING_KEY must be set for webhook mode")
    _signing_key = bytes.fromhex(key_hex)


def _verify(body: bytes, sig_header: str) -> bool:
    """Constant-time HMAC-SHA256 check.

    OpenPhone signs the raw body; the header carries the base64 digest.
    Any tolerance for header case or padding lives here, not in callers.
    """
    if not sig_header:
        return False
    expected = base64.b64encode(
        hmac.new(_signing_key, body, hashlib.sha256).digest()).decode()
    return hmac.compare_digest(expected, sig_header.strip())


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/quo/inbound", methods=["POST"])
def inbound():
    body = request.get_data()
    sig = request.headers.get("openphone-signature", "")
    if not _verify(body, sig):
        log.warning("signature verification failed")
        abort(401)

    payload = json.loads(body)
    if payload.get("type") != "message.received":
        return jsonify(ignored=True)

    d = payload.get("data", {})
    msg = InboundMessage(
        quo_message_id=d["id"],
        conversation_id=d.get("conversationId", ""),
        peer_e164=d["from"],
        text=d.get("text", ""),
        created_at=d.get("createdAt", ""),
        raw=d,
    )
    handle_inbound(_cfg, msg)
    return jsonify(ok=True)


if __name__ == "__main__":
    logging.basicConfig(level=os.environ.get("QUO_LOG_LEVEL", "INFO"))
    _init()
    app.run(host="127.0.0.1", port=int(os.environ.get("QUO_HEALTH_PORT", "9631")))
