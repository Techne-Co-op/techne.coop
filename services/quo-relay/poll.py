"""Poll loop against Quo /v1/messages. First-tier deploy for SMS-01.

Runs forever, polling every QUO_POLL_INTERVAL_SEC (default 15s). On each
tick, fetches the most recent inbound messages since the last-seen
cursor, hands each to relay.handle_inbound(), and updates the cursor.

The cursor is persisted to STATE_PATH so a restart does not replay the
whole conversation history through the model. On first start with no
state file, the cursor initialises to now(), so nothing pre-existing is
processed; the operator sends a fresh test message to prove the loop.

Health: an HTTP endpoint on 127.0.0.1:9631 returns the last-poll time
and error count. Systemd health checks read this.
"""

from __future__ import annotations

import json
import logging
import os
import signal
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import requests

from relay import QUO_API_BASE, Config, InboundMessage, handle_inbound

log = logging.getLogger("quo-relay.poll")

STATE_PATH = Path(os.environ.get(
    "QUO_POLL_STATE_PATH", "/var/lib/nou-quo-relay/poll-cursor.json"))
POLL_INTERVAL_SEC = int(os.environ.get("QUO_POLL_INTERVAL_SEC", "15"))
HEALTH_PORT = int(os.environ.get("QUO_HEALTH_PORT", "9631"))

_state = {"last_poll_at": None, "last_error": None, "errors_total": 0,
          "cursor_iso": None}
_shutdown = threading.Event()


def load_cursor() -> str:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())["cursor_iso"]
    now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    save_cursor(now_iso)
    return now_iso


def save_cursor(cursor_iso: str) -> None:
    STATE_PATH.write_text(json.dumps({"cursor_iso": cursor_iso}))
    _state["cursor_iso"] = cursor_iso


def fetch_new(cfg: Config, since_iso: str) -> list[InboundMessage]:
    """One page of inbounds after since_iso, oldest first, direction=in only.

    The Quo API returns most-recent-first; we reverse to process in order.
    A single-page cap keeps a long silence from flooding on first tick.
    """
    r = requests.get(
        f"{QUO_API_BASE}/messages",
        params={"phoneNumberId": cfg.phone_number_id,
                "participants": list(cfg.allowlist),
                "maxResults": 50, "since": since_iso},
        headers={"Authorization": cfg.quo_api_key},
        timeout=10,
    )
    r.raise_for_status()
    data = r.json().get("data", [])
    out: list[InboundMessage] = []
    for m in reversed(data):
        if m.get("direction") != "incoming":
            continue
        if m.get("createdAt", "") <= since_iso:
            continue
        out.append(InboundMessage(
            quo_message_id=m["id"],
            conversation_id=m.get("conversationId", ""),
            peer_e164=m["from"],
            text=m.get("text", ""),
            created_at=m["createdAt"],
            raw=m,
        ))
    return out


def poll_tick(cfg: Config) -> None:
    cursor = _state["cursor_iso"] or load_cursor()
    msgs = fetch_new(cfg, cursor)
    for m in msgs:
        handle_inbound(cfg, m)
        # Advance the cursor per-message so a crash mid-batch does not
        # replay earlier messages on restart.
        save_cursor(m.created_at)
    _state["last_poll_at"] = time.strftime(
        "%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class Health(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        if self.path != "/health":
            self.send_response(404); self.end_headers(); return
        body = json.dumps({
            "status": "ok" if _state["last_poll_at"] else "starting",
            "last_poll_at": _state["last_poll_at"],
            "cursor_iso": _state["cursor_iso"],
            "errors_total": _state["errors_total"],
            "last_error": _state["last_error"],
        }).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args, **_kw):
        pass  # silence access log; journald has it


def serve_health() -> None:
    httpd = HTTPServer(("127.0.0.1", HEALTH_PORT), Health)
    httpd.serve_forever()


def main() -> int:
    logging.basicConfig(
        level=os.environ.get("QUO_LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s %(message)s")
    cfg = Config.from_env()
    _state["cursor_iso"] = load_cursor()

    signal.signal(signal.SIGTERM, lambda *_: _shutdown.set())
    signal.signal(signal.SIGINT,  lambda *_: _shutdown.set())

    threading.Thread(target=serve_health, daemon=True).start()

    log.info("poll loop starting: interval=%ds, cursor=%s, allowlist=%d",
             POLL_INTERVAL_SEC, _state["cursor_iso"], len(cfg.allowlist))

    while not _shutdown.is_set():
        try:
            poll_tick(cfg)
        except Exception as e:
            log.exception("poll_tick failed")
            _state["errors_total"] += 1
            _state["last_error"] = str(e)[:200]
        _shutdown.wait(POLL_INTERVAL_SEC)

    log.info("poll loop stopped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
