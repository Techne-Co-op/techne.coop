"""SMS-03 Buzz bridge: the quo-relay's hand on the relay, via the buzz CLI.

The harness never auto-publishes; every post here is an explicit
`buzz messages send` under the agent's key, exactly how the estate
already publishes turns. Delivery evidence is the CLI's accepted JSON,
never the fact that a function returned.

Channel model, verified against the Buzz source (SMS-02 design §5):
a private channel is a relay-database row with enforced membership;
the creator becomes owner and may add members. The bridge creates one
private channel per verified binding and seats exactly three keys:
the bound member, the agent, and the owner-steward.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
from typing import Optional

log = logging.getLogger("quo-relay.bridge")

BUZZ_CMD = os.environ.get("BUZZ_CLI", os.path.expanduser("~/bin/buzz"))


def _run(args: list[str], timeout: int = 30) -> Optional[dict]:
    """Run the buzz CLI, return parsed JSON on success, None on failure."""
    try:
        result = subprocess.run([BUZZ_CMD, *args], capture_output=True,
                                text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as e:
        log.error("buzz cli failed to run: %s", e)
        return None
    if result.returncode != 0:
        log.error("buzz cli exit %d: %s", result.returncode,
                  result.stderr[:400] or result.stdout[:400])
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        log.error("buzz cli returned non-JSON: %s", result.stdout[:200])
        return None


class BuzzBridge:
    def __init__(self, agent_pubkey: str):
        self.agent_pubkey = agent_pubkey

    def create_binding_channel(self, member_pubkey: str, owner_pubkey: str,
                               label: str) -> Optional[str]:
        """Create the private room for a binding; returns channel id or None."""
        created = _run(["channels", "create", "--name", f"sms-{label}",
                        "--type", "stream", "--visibility", "private"])
        if not created:
            return None
        channel_id = created.get("channel_id") or created.get("id")
        if not channel_id:
            log.error("channel create returned no id: %s", created)
            return None
        for pk in (member_pubkey, owner_pubkey):
            added = _run(["channels", "add-member", "--channel", channel_id,
                          "--pubkey", pk])
            if not added:
                log.error("add-member %s to %s failed", pk[:12], channel_id)
        return channel_id

    def post(self, channel_id: str, content: str) -> bool:
        """Post into a channel under the agent's key. True only on accept."""
        sent = _run(["messages", "send", "--channel", channel_id,
                     "--content", content])
        ok = bool(sent and sent.get("accepted"))
        if not ok:
            log.error("post to %s not accepted: %s", channel_id, sent)
        return ok

    def get_since(self, channel_id: str, since_ts: int) -> list[dict]:
        """Messages in a channel since a unix timestamp, oldest first.

        Returns [] on any failure: a poll that reads nothing routes
        nothing, which is the safe direction.
        """
        got = _run(["messages", "get", "--channel", channel_id,
                    "--since", str(since_ts)])
        if not got:
            return []
        # The CLI returns a bare JSON list of events (verified live
        # 2026-08-23): id, pubkey, content, created_at, kind, tags.
        msgs = got if isinstance(got, list) else got.get("messages", [])
        out = []
        for m in msgs:
            out.append({
                "event_id": m.get("event_id") or m.get("id", ""),
                "author": m.get("author_pubkey") or m.get("pubkey", ""),
                "content": m.get("content", ""),
                "created_at": int(m.get("created_at", 0)),
            })
        out.sort(key=lambda m: m["created_at"])
        return out
