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


def fetch_new(cfg: Config, since_iso: str,
              participants: list[str] | None = None) -> list[InboundMessage]:
    """One page of inbounds after since_iso, oldest first, direction=in only.

    The Quo API returns most-recent-first; we reverse to process in order.
    A single-page cap keeps a long silence from flooding on first tick.

    `participants` is the set of numbers whose conversations are read:
    the tier-one allowlist plus every verified binding (SMS-03). The
    query has to be widened, not just the gate in handle_inbound: a
    number absent here is never fetched, so a bound member's text is
    invisible to the service no matter what the gate would allow.
    Defaults to the allowlist alone, which is the tier-one behaviour.

    One request per number, because Quo's `participants` is an exact
    conversation match, not an OR: passing two numbers asks for the
    group conversation between both and returns nothing (verified
    against the live API 2026-08-24). The page cap is per number.

    No `since` param on the API call: Quo's `since=` filters the wrong
    direction (returns messages BEFORE the timestamp, not after), so
    passing the cursor as `since` causes the newest inbound to be
    excluded from the response entirely. Local `createdAt <= since_iso`
    filter below is the source of truth; a 50-message page cap keeps
    the first-tick blast bounded either way.
    """
    out: list[InboundMessage] = []
    for number in (participants or list(cfg.allowlist)):
        r = requests.get(
            f"{QUO_API_BASE}/messages",
            params={"phoneNumberId": cfg.phone_number_id,
                    "participants": [number],
                    "maxResults": 50},
            headers={"Authorization": cfg.quo_api_key},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json().get("data", [])
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
    out.sort(key=lambda m: m.created_at)
    return out


def poll_participants(cfg: Config, tier2=None) -> list[str]:
    """Allowlist plus every verified binding, deduplicated.

    A router outage falls back to the allowlist alone: the service
    narrows to tier one, never widens, same rule as the gate.
    """
    numbers = list(cfg.allowlist)
    if tier2 is not None:
        try:
            for b in tier2.router.verified_bindings():
                e164 = b.get("peer_e164")
                if e164 and e164 not in numbers:
                    numbers.append(e164)
        except Exception as e:
            log.error("binding poll failed, allowlist only this tick: %s", e)
    return numbers


def poll_tick(cfg: Config, tier2=None) -> None:
    cursor = _state["cursor_iso"] or load_cursor()
    msgs = fetch_new(cfg, cursor, poll_participants(cfg, tier2))
    for m in msgs:
        if tier2 is not None:
            handle_inbound(cfg, m, router=tier2.router,
                           binder=tier2.binder, bridge=tier2.bridge)
        else:
            handle_inbound(cfg, m)
        # Advance the cursor per-message so a crash mid-batch does not
        # replay earlier messages on restart.
        save_cursor(m.created_at)
    if tier2 is not None:
        tier2.tick()
    _state["last_poll_at"] = time.strftime(
        "%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class Tier2:
    """SMS-03: the Buzz side of the loop.

    Each tick, after the Quo poll: read new messages in the ceremony
    channel and feed them to the Ceremony; read new messages in every
    bound channel and bridge the bound member's own posts out as SMS.
    Buzz cursors live next to the Quo cursor in the state directory so
    a restart does not replay ceremonies or resend SMS.
    """

    def __init__(self, cfg: Config):
        from bindings import BindingStore, Ceremony
        from bridge import BuzzBridge
        self.cfg = cfg
        self.router = BindingStore(cfg.cis_url, cfg.cis_phone_router_key)
        self.binder = BindingStore(cfg.cis_url, cfg.cis_phone_binder_key)
        self.bridge = BuzzBridge(cfg.agent_pubkey)
        self.ceremony = Ceremony(self.binder, self._send_sms, self.bridge)
        self.cursor_path = STATE_PATH.parent / "buzz-cursors.json"
        self.cursors: dict[str, int] = {}
        if self.cursor_path.exists():
            self.cursors = json.loads(self.cursor_path.read_text())
        # Event ids already handled. The cursor alone cannot carry this:
        # `buzz messages get --since` is inclusive of its second and the
        # cursor is set to the newest message's own created_at, so the
        # last message of every tick comes back once more. Left to the
        # cursor, one !bind sent two challenge SMS (2026-08-24).
        self.seen_path = STATE_PATH.parent / "ceremony-seen.json"
        self.seen: list[str] = []
        if self.seen_path.exists():
            self.seen = json.loads(self.seen_path.read_text())

    def _save_cursors(self) -> None:
        self.cursor_path.write_text(json.dumps(self.cursors))

    def _already_seen(self, event_id: str) -> bool:
        if event_id in self.seen:
            return True
        self.seen.append(event_id)
        del self.seen[:-500]
        self.seen_path.write_text(json.dumps(self.seen))
        return False

    def _cursor(self, channel: str) -> int:
        # First sight of a channel starts at now: nothing pre-existing
        # is ceremonially processed or bridged, same rule as the Quo
        # cursor's first start.
        if channel not in self.cursors:
            self.cursors[channel] = int(time.time())
            self._save_cursors()
        return self.cursors[channel]

    def _send_sms(self, e164: str, text: str):
        """Challenge sender for the ceremony; logs like every outbound.

        Returns the Quo message id (truthy) on carrier accept, None on
        failure. The phone_events row is the durable record.
        """
        from relay import log_event, send_reply
        try:
            api = send_reply(self.cfg, e164, text)
        except Exception as e:
            log.error("challenge send failed: %s", e)
            return None
        log_event(self.cfg, direction="out", peer=e164,
                  content="binding_challenge",
                  quo_message_id=api.get("id"),
                  conversation_id=api.get("conversationId"),
                  status="challenge_sent")
        return api.get("id") or True

    def tick(self) -> None:
        self._ceremony_tick()
        self._bridge_tick()

    def _ceremony_tick(self) -> None:
        for ch in self.cfg.ceremony_channel_ids:
            since = self._cursor(ch)
            for m in self.bridge.get_since(ch, since):
                self.cursors[ch] = max(self.cursors[ch], m["created_at"])
                if m["author"] == self.cfg.agent_pubkey:
                    continue
                if self._already_seen(m["event_id"]):
                    continue
                try:
                    reply = self.ceremony.handle_message(
                        m["author"], m["content"], m["event_id"],
                        self.cfg.owner_pubkey, self.cfg.agent_pubkey)
                except Exception:
                    log.exception("ceremony message failed")
                    reply = "ceremony error; nothing was recorded. Try again."
                if reply:
                    self.bridge.post(ch, reply)
        self._save_cursors()

    def _bridge_tick(self) -> None:
        from relay import log_event, send_reply
        try:
            bindings = self.router.verified_bindings()
        except Exception as e:
            log.error("bindings poll failed: %s", e)
            return
        for b in bindings:
            ch = b.get("buzz_channel_id")
            if not ch:
                continue
            since = self._cursor(ch)
            for m in self.bridge.get_since(ch, since):
                self.cursors[ch] = max(self.cursors[ch], m["created_at"])
                # Only the bound member's own messages bridge outward,
                # and only to their own number (design §5).
                if m["author"] != b["member_pubkey"]:
                    continue
                # Same inclusive-cursor replay as the ceremony: without
                # this, the last room post of a tick bridges out twice.
                if self._already_seen(m["event_id"]):
                    continue
                try:
                    api = send_reply(self.cfg, b["peer_e164"], m["content"][:1600])
                except Exception as e:
                    log.error("room->phone send failed: %s", e)
                    continue
                log_event(self.cfg, direction="out", peer=b["peer_e164"],
                          content=m["content"][:4096],
                          quo_message_id=api.get("id"),
                          conversation_id=api.get("conversationId"),
                          status="bridged_from_buzz",
                          payload={"buzz_event_id": m["event_id"]})
            self._save_cursors()


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

    tier2 = None
    if cfg.tier2:
        tier2 = Tier2(cfg)
        log.info("tier two active: ceremony channel %s",
                 cfg.ceremony_channel_id or "(unset)")

    log.info("poll loop starting: interval=%ds, cursor=%s, allowlist=%d",
             POLL_INTERVAL_SEC, _state["cursor_iso"], len(cfg.allowlist))

    while not _shutdown.is_set():
        try:
            poll_tick(cfg, tier2)
        except Exception as e:
            log.exception("poll_tick failed")
            _state["errors_total"] += 1
            _state["last_error"] = str(e)[:200]
        _shutdown.wait(POLL_INTERVAL_SEC)

    log.info("poll loop stopped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
