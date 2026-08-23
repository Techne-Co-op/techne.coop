"""Unit tests for relay dispatch decisions. No network.

Every network call in relay.py is monkeypatched; these tests exercise
the branching logic (allowlist, STOP, error paths) and the phone_events
write shape, not the HTTP transport.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from relay import Config, InboundMessage, handle_inbound  # noqa: E402


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


def _msg(peer="+13035059612", text="hi", mid="M1"):
    return InboundMessage(quo_message_id=mid, conversation_id="C1",
                          peer_e164=peer, text=text, created_at="2026-08-22T21:40Z")


@patch("relay.log_event", return_value=True)
@patch("relay.dispatch_to_nou", return_value="pong")
@patch("relay.send_reply", return_value={"id": "OUT", "status": "sent",
                                          "conversationId": "C1"})
def test_allowlisted_message_dispatches_and_replies(send, dispatch, log, cfg):
    handle_inbound(cfg, _msg())
    dispatch.assert_called_once()
    send.assert_called_once_with(cfg, "+13035059612", "pong")
    # in-row, out-row.
    assert log.call_count == 2
    directions = [c.kwargs["direction"] for c in log.call_args_list]
    assert directions == ["in", "out"]


@patch("relay.log_event", return_value=True)
@patch("relay.dispatch_to_nou")
@patch("relay.send_reply")
def test_non_allowlisted_is_silently_dropped(send, dispatch, log, cfg):
    handle_inbound(cfg, _msg(peer="+19995551212"))
    dispatch.assert_not_called()
    send.assert_not_called()
    # in-row (received) + in-row (ignored).
    assert log.call_count == 2
    statuses = [c.kwargs["status"] for c in log.call_args_list]
    assert statuses == ["received", "ignored_not_allowlisted"]


@patch("relay.log_event", return_value=True)
@patch("relay.dispatch_to_nou")
@patch("relay.send_reply")
def test_stop_from_allowlisted_skips_dispatch(send, dispatch, log, cfg):
    handle_inbound(cfg, _msg(text="STOP"))
    dispatch.assert_not_called()
    send.assert_not_called()
    statuses = [c.kwargs["status"] for c in log.call_args_list]
    assert statuses == ["received", "stopped"]


@patch("relay.log_event", return_value=True)
@patch("relay.dispatch_to_nou", side_effect=RuntimeError("boom"))
@patch("relay.send_reply")
def test_dispatch_failure_logs_and_does_not_reply(send, dispatch, log, cfg):
    handle_inbound(cfg, _msg())
    send.assert_not_called()
    statuses = [c.kwargs["status"] for c in log.call_args_list]
    assert statuses == ["received", "dispatch_failed"]
    assert "boom" in log.call_args_list[-1].kwargs["error"]


@patch("relay.log_event", return_value=False)  # duplicate on inbound
@patch("relay.dispatch_to_nou")
@patch("relay.send_reply")
def test_duplicate_inbound_short_circuits(send, dispatch, log, cfg):
    handle_inbound(cfg, _msg())
    dispatch.assert_not_called()
    send.assert_not_called()
    assert log.call_count == 1  # only the failed insert attempt


@patch("relay.log_event", return_value=True)
@patch("relay.dispatch_to_nou", return_value="pong")
@patch("relay.send_reply", side_effect=RuntimeError("carrier down"))
def test_send_failure_logs_out_row_as_send_failed(send, dispatch, log, cfg):
    handle_inbound(cfg, _msg())
    statuses = [c.kwargs["status"] for c in log.call_args_list]
    assert statuses == ["received", "send_failed"]
    directions = [c.kwargs["direction"] for c in log.call_args_list]
    assert directions == ["in", "out"]


def test_webhook_signature_verifies_openphone_scheme():
    """Exercised for its own sake; webhook.py is not deployed yet."""
    import base64, hashlib, hmac
    from webhook import _verify
    key = bytes.fromhex("aa" * 32)
    body = b'{"type":"message.received","data":{}}'
    sig = base64.b64encode(hmac.new(key, body, hashlib.sha256).digest()).decode()
    import webhook
    webhook._signing_key = key
    assert _verify(body, sig)
    assert not _verify(body, "wrong")
    assert not _verify(body + b"tamper", sig)
