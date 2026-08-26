"""Unit tests for the poll loop's reach. No network.

Two defects of 2026-08-24 live here as regressions: the Quo query was
scoped to the tier-one allowlist, so a bound member's SMS was never
fetched; and the ceremony tick trusted an inclusive cursor, so the last
message of every tick was processed twice.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from poll import Tier2, fetch_new, poll_participants  # noqa: E402
from relay import Config  # noqa: E402


@pytest.fixture
def cfg():
    return Config(
        quo_api_key="k",
        phone_number_id="PNK5N9GAMW",
        line_e164="+19702927888",
        allowlist=frozenset({"+13035059612"}),
        cis_url="https://cis.test",
        cis_phone_relay_key="sb_secret_test",
    )


def _tier2(bindings):
    t = MagicMock()
    t.router.verified_bindings.return_value = bindings
    return t


def test_participants_include_verified_bindings(cfg):
    t = _tier2([{"peer_e164": "+15135931721"}])
    assert poll_participants(cfg, t) == ["+13035059612", "+15135931721"]


def test_participants_fall_back_to_allowlist_on_router_outage(cfg):
    t = MagicMock()
    t.router.verified_bindings.side_effect = RuntimeError("down")
    assert poll_participants(cfg, t) == ["+13035059612"]


def test_participants_tier_one_alone(cfg):
    assert poll_participants(cfg, None) == ["+13035059612"]


def _page(*texts):
    r = MagicMock()
    r.json.return_value = {"data": [
        {"id": f"M{i}", "conversationId": "C", "from": frm,
         "direction": "incoming", "text": t, "createdAt": ts}
        for i, (frm, t, ts) in enumerate(texts)]}
    return r


def test_fetch_new_queries_each_number_separately(cfg):
    """Quo's `participants` is an exact conversation match, not an OR:
    one request per number, or the second number is never read."""
    pages = [_page(("+13035059612", "steward", "2026-08-24T18:00:00Z")),
             _page(("+15135931721", "Hello!", "2026-08-24T17:49:04Z"))]
    with patch("poll.requests.get", side_effect=pages) as get:
        msgs = fetch_new(cfg, "2026-08-24T17:00:00Z",
                         ["+13035059612", "+15135931721"])
    assert [c.kwargs["params"]["participants"] for c in get.call_args_list] == [
        ["+13035059612"], ["+15135931721"]]
    # Merged and ordered oldest first across both conversations.
    assert [m.text for m in msgs] == ["Hello!", "steward"]


def test_fetch_new_drops_outbound_and_anything_at_or_before_cursor(cfg):
    page = _page(("+13035059612", "old", "2026-08-24T17:00:00Z"),
                 ("+13035059612", "new", "2026-08-24T18:00:00Z"))
    page.json.return_value["data"][0]["direction"] = "outgoing"
    with patch("poll.requests.get", return_value=page):
        msgs = fetch_new(cfg, "2026-08-24T17:30:00Z", ["+13035059612"])
    assert [m.text for m in msgs] == ["new"]


def test_already_seen_is_idempotent_and_bounded(tmp_path):
    t = object.__new__(Tier2)
    t.seen_path = tmp_path / "ceremony-seen.json"
    t.seen = []
    assert t._already_seen("e1") is False
    assert t._already_seen("e1") is True     # the inclusive-cursor replay
    assert t._already_seen("e2") is False
    for i in range(600):
        t._already_seen(f"x{i}")
    assert len(t.seen) == 500
    assert t.seen_path.exists()
