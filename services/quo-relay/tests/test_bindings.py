"""Unit tests for the SMS-03 ceremony and tier-two routing. No network."""

from __future__ import annotations

import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bindings import Ceremony, _hash  # noqa: E402
from relay import Config, InboundMessage, handle_inbound  # noqa: E402

OWNER = "99" + "0" * 62
AGENT = "ea" + "0" * 62
MEMBER = "ab" + "0" * 62


@pytest.fixture
def cfg():
    return Config(
        quo_api_key="k", phone_number_id="PN", line_e164="+19702927888",
        allowlist=frozenset({"+13035059612"}), cis_url="https://cis.test",
        cis_phone_relay_key="sb_relay", cis_phone_router_key="sb_router",
        cis_phone_binder_key="sb_binder", ceremony_channel_id="CH-CEREMONY",
        owner_pubkey=OWNER, agent_pubkey=AGENT)


def _ceremony(store=None, send_sms=None, bridge=None):
    store = store or MagicMock()
    send_sms = send_sms or MagicMock(return_value="QM1")
    bridge = bridge or MagicMock()
    return Ceremony(store, send_sms, bridge), store, send_sms, bridge


def test_bind_sends_challenge_and_records_pending():
    c, store, send_sms, _ = _ceremony()
    store.lookup_verified_by_pubkey.return_value = None
    store.lookup_verified_by_e164.return_value = None
    store.challenges_today.return_value = 0
    reply = c.handle_message(MEMBER, "!bind +13035551234", "EV1", OWNER, AGENT)
    send_sms.assert_called_once()
    assert "+13035551234" in send_sms.call_args[0][0]
    store.insert_pending.assert_called_once()
    assert "challenge sent" in reply


def test_bind_refused_when_number_already_bound():
    c, store, send_sms, _ = _ceremony()
    store.lookup_verified_by_pubkey.return_value = None
    store.lookup_verified_by_e164.return_value = {"id": "B1"}
    reply = c.handle_message(MEMBER, "!bind +13035551234", "EV1", OWNER, AGENT)
    send_sms.assert_not_called()
    assert "already holds a live binding" in reply


def test_bind_rate_limited():
    c, store, send_sms, _ = _ceremony()
    store.lookup_verified_by_pubkey.return_value = None
    store.lookup_verified_by_e164.return_value = None
    store.challenges_today.return_value = 3
    reply = c.handle_message(MEMBER, "!bind +13035551234", "EV1", OWNER, AGENT)
    send_sms.assert_not_called()
    assert "limit" in reply


def test_verify_good_code_creates_channel_and_marks_verified():
    c, store, _, bridge = _ceremony()
    store.pending_for_pubkey.return_value = {
        "id": "B1", "peer_e164": "+13035551234", "code_hash": _hash("123456"),
        "requested_at": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())}
    bridge.create_binding_channel.return_value = "CH-NEW"
    reply = c.handle_message(MEMBER, "!verify 123456", "EV2", OWNER, AGENT)
    store.mark_verified.assert_called_once_with("B1", "EV2")
    bridge.create_binding_channel.assert_called_once()
    store.set_channel.assert_called_once_with("B1", "CH-NEW")
    assert "verified" in reply
    # The room name carries the binding id, so two numbers ending in the
    # same four digits cannot collide on one channel name.
    assert bridge.create_binding_channel.call_args.kwargs["seed"] == "B1"
    # And the room opens with the ceremony stated, so a later reader does
    # not have to infer the member's standing from a phone number.
    seeded = bridge.post.call_args.args[1]
    assert "Binding ceremony complete" in seeded
    assert MEMBER in seeded and "+13035551234" in seeded


def test_verify_without_channel_posts_no_note():
    c, store, _, bridge = _ceremony()
    store.pending_for_pubkey.return_value = {
        "id": "B1", "peer_e164": "+13035551234", "code_hash": _hash("123456"),
        "requested_at": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())}
    bridge.create_binding_channel.return_value = None
    reply = c.handle_message(MEMBER, "!verify 123456", "EV2", OWNER, AGENT)
    bridge.post.assert_not_called()
    assert "could not be created" in reply


def test_verify_wrong_code_rejected():
    c, store, _, bridge = _ceremony()
    store.pending_for_pubkey.return_value = {
        "id": "B1", "peer_e164": "+13035551234", "code_hash": _hash("123456"),
        "requested_at": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())}
    reply = c.handle_message(MEMBER, "!verify 999999", "EV2", OWNER, AGENT)
    store.mark_verified.assert_not_called()
    assert "does not match" in reply


def test_verify_expired_code_revokes():
    c, store, _, _ = _ceremony()
    store.pending_for_pubkey.return_value = {
        "id": "B1", "peer_e164": "+13035551234", "code_hash": _hash("123456"),
        "requested_at": "2026-08-01T00:00:00"}
    reply = c.handle_message(MEMBER, "!verify 123456", "EV2", OWNER, AGENT)
    store.revoke.assert_called_once_with("B1", "expired")
    assert "expired" in reply


def test_non_command_message_ignored():
    c, store, send_sms, _ = _ceremony()
    assert c.handle_message(MEMBER, "hello there", "EV1", OWNER, AGENT) is None
    send_sms.assert_not_called()


def _msg(peer, text="hi", mid="M1"):
    return InboundMessage(quo_message_id=mid, conversation_id="C1",
                          peer_e164=peer, text=text,
                          created_at="2026-08-23T01:00Z")


@patch("relay.log_event", return_value=True)
@patch("relay.dispatch_to_nou", return_value="pong")
@patch("relay.send_reply", return_value={"id": "OUT", "status": "sent",
                                          "conversationId": "C1"})
def test_bound_peer_mirrors_to_channel(send, dispatch, log, cfg):
    router, bridge = MagicMock(), MagicMock()
    router.lookup_verified_by_e164.return_value = {
        "id": "B1", "member_pubkey": MEMBER, "peer_e164": "+13035551234",
        "buzz_channel_id": "CH-1"}
    handle_inbound(cfg, _msg("+13035551234"), router=router,
                   binder=MagicMock(), bridge=bridge)
    dispatch.assert_called_once()
    send.assert_called_once()
    # inbound mirrored + reply mirrored, both labelled as SMS traffic so
    # the room does not read one answer as two.
    posted = [c.args for c in bridge.post.call_args_list]
    assert posted[0][0] == "CH-1" and posted[0][1].startswith("[SMS \u00b7 +1")
    assert posted[1] == ("CH-1", "[SMS \u00b7 out] pong")


@patch("relay.log_event", return_value=True)
@patch("relay.dispatch_to_nou")
@patch("relay.send_reply", return_value={"id": "OUT", "status": "sent",
                                          "conversationId": "C1"})
def test_stop_from_bound_peer_revokes_and_confirms(send, dispatch, log, cfg):
    router, binder = MagicMock(), MagicMock()
    router.lookup_verified_by_e164.return_value = {
        "id": "B1", "member_pubkey": MEMBER, "peer_e164": "+13035551234",
        "buzz_channel_id": "CH-1"}
    handle_inbound(cfg, _msg("+13035551234", text="STOP"), router=router,
                   binder=binder, bridge=MagicMock())
    binder.revoke.assert_called_once_with("B1", "sms_stop")
    send.assert_called_once()          # the one required confirmation
    dispatch.assert_not_called()


@patch("relay.log_event", return_value=True)
@patch("relay.dispatch_to_nou")
@patch("relay.send_reply")
def test_unbound_unknown_peer_still_silently_dropped(send, dispatch, log, cfg):
    router = MagicMock()
    router.lookup_verified_by_e164.return_value = None
    handle_inbound(cfg, _msg("+19995551212"), router=router,
                   binder=MagicMock(), bridge=MagicMock())
    dispatch.assert_not_called()
    send.assert_not_called()
    statuses = [c.kwargs["status"] for c in log.call_args_list]
    assert statuses == ["received", "ignored_not_allowlisted"]


@patch("relay.log_event", return_value=True)
@patch("relay.dispatch_to_nou", return_value="pong")
@patch("relay.send_reply", return_value={"id": "OUT", "status": "sent",
                                          "conversationId": "C1"})
def test_router_outage_narrows_to_tier_one(send, dispatch, log, cfg):
    """A router failure must not widen access, only narrow it."""
    router = MagicMock()
    router.lookup_verified_by_e164.side_effect = RuntimeError("cis down")
    # Allowlisted steward still works on the tier-one path.
    handle_inbound(cfg, _msg("+13035059612"), router=router,
                   binder=MagicMock(), bridge=MagicMock())
    dispatch.assert_called_once()
    # A bound-but-not-allowlisted member is dropped during the outage.
    dispatch.reset_mock()
    handle_inbound(cfg, _msg("+13035551234", mid="M2"), router=router,
                   binder=MagicMock(), bridge=MagicMock())
    dispatch.assert_not_called()


@patch("relay.log_event", return_value=True)
@patch("relay.dispatch_to_nou", return_value="pong")
@patch("relay.send_reply", return_value={"id": "OUT", "status": "sent",
                                          "conversationId": "C1"})
def test_bound_peer_dispatch_carries_the_room_as_history(send, dispatch, log, cfg):
    router, bridge = MagicMock(), MagicMock()
    router.lookup_verified_by_e164.return_value = {
        "id": "B1", "member_pubkey": MEMBER, "peer_e164": "+13035551234",
        "buzz_channel_id": "CH-1"}
    bridge.recent.return_value = [
        {"author": AGENT, "content": "[SMS · +13035551234] how much?"},
        {"author": AGENT, "content": "[SMS · out] a cent or two"},
    ]
    handle_inbound(cfg, _msg("+13035551234"), router=router,
                   binder=MagicMock(), bridge=bridge)
    history = dispatch.call_args.args[3]
    assert "them: how much?" in history and "you: a cent or two" in history
