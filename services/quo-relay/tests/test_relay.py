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

from relay import (  # noqa: E402
    _GSM7_CHARS,
    SMS_MAX_PARTS,
    SMS_PART_CHARS,
    Config,
    InboundMessage,
    SMS_HISTORY_CHARS,
    SMS_HISTORY_MESSAGES,
    _render_history,
    _sender_frame,
    dispatch_to_nou,
    handle_inbound,
    split_for_sms,
    to_gsm7,
)


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


# --- segment cost ----------------------------------------------------------
# Every 160 GSM-7 characters is a billed segment, and one non-GSM character
# re-encodes the whole message at 70. These guard the cost of a reply, not
# its correctness.

def test_gsm7_folding_substitutes_known_punctuation():
    folded = to_gsm7("He said “no—really” and left…")
    assert folded == 'He said "no-really" and left...'
    assert all(c in _GSM7_CHARS for c in folded)


def test_gsm7_folding_drops_emoji_rather_than_paying_ucs2_for_it():
    assert to_gsm7("done \U0001f680 shipped") == "done shipped"


def test_split_folds_before_measuring_so_counts_are_billable_counts():
    assert split_for_sms("café — ‘ok’") == ["café - 'ok'"]


def test_split_defaults_cap_a_reply_at_four_segments():
    assert SMS_PART_CHARS * SMS_MAX_PARTS <= 640


def test_split_tells_the_member_when_it_dropped_the_overflow():
    long_reply = " ".join(f"Sentence number {i} runs on for a while." for i in range(40))
    parts = split_for_sms(long_reply)
    assert len(parts) <= SMS_MAX_PARTS + 1
    assert "not sent" in parts[-1]


def test_split_refuses_a_reply_that_folds_away_to_nothing():
    with pytest.raises(ValueError):
        split_for_sms("\U0001f680\U0001f680")


# --- who is texting --------------------------------------------------------
# The frame used to say "from steward" for every peer, which read a
# correctly bound member as an intruder (2026-08-24).

def test_frame_names_a_bound_member_and_denies_them_the_steward_label():
    frame = _sender_frame("+15135931721", {"member_pubkey": "3e748f43fe80e8e2"})
    assert "verified bound member" in frame
    assert "3e748f43fe80e8e2" in frame
    assert "not the steward" in frame


def test_frame_says_plainly_when_a_peer_carries_no_key_evidence():
    frame = _sender_frame("+13035059612", None)
    assert "allowlisted number" in frame
    assert "no binding and no key evidence" in frame
    assert "steward" not in frame


def test_frame_says_identity_unknown_when_the_directory_could_not_be_read():
    """A lookup that failed is not a lookup that found nothing."""
    frame = _sender_frame("+13035059612", None, identity_unknown=True)
    assert "identity unknown" in frame
    assert "unidentified" in frame
    # It must not report the absence of a binding it never got to seek.
    assert "no binding and no key evidence" not in frame


@pytest.mark.parametrize("binding,unknown", [
    (None, False),                  # allowlisted, looked, found nothing
    (None, True),                   # directory unreadable
    ({}, False),                    # a row carrying no key is not an identity
    ({"member_pubkey": ""}, True),  # empty key, and the lookup failed too
])
def test_no_frame_without_a_binding_can_say_steward(binding, unknown):
    """The word is an identity claim. Without a key there is nothing to
    make it on, and the relay must never make it by default."""
    frame = _sender_frame("+19995551212", binding, identity_unknown=unknown)
    assert "steward" not in frame.lower()


def test_the_dispatch_prompt_carries_the_frame_it_was_given():
    """The frame is only worth building if it reaches the agent."""
    seen = {}

    class _Result:
        returncode = 0
        stdout = "pong"
        stderr = ""

    def _fake_run(cmd, **kwargs):
        seen["prompt"] = cmd[-1]
        return _Result()

    with patch("relay.subprocess.run", _fake_run):
        dispatch_to_nou("+13035551234", "hi",
                        {"member_pubkey": "3e748f43fe80e8e2c0ff"}, "")
    assert seen["prompt"].startswith("[SMS from verified bound member "
                                     "3e748f43fe80e8e2")

    with patch("relay.subprocess.run", _fake_run):
        dispatch_to_nou("+13035059612", "hi", None, "", True)
    assert "identity unknown" in seen["prompt"].split("]")[0]
    assert "steward" not in seen["prompt"].split("]")[0].lower()


# --- conversation memory ---------------------------------------------------
# The binding room is the SMS conversation's memory: a one-shot dispatch
# holds no state, so continuity is the room read back.

AGENT = "ea11b8c9"


def test_history_reads_speakers_from_the_mirror_prefix_not_the_author():
    # Both halves are posted under the agent's key; author alone would
    # call the member's own texts ours.
    msgs = [{"author": AGENT, "content": "[SMS · +15135931721] how much?"},
            {"author": AGENT, "content": "[SMS · out] a cent or two"}]
    assert _render_history(msgs, AGENT) == "them: how much?\nyou: a cent or two"


def test_history_marks_unmirrored_room_posts_as_room_posts():
    msgs = [{"author": AGENT, "content": "line is out of credits"},
            {"author": "3e748f43", "content": "ok thanks"}]
    rendered = _render_history(msgs, AGENT)
    assert "you, in the Buzz room: line is out of credits" in rendered
    assert "them, in the Buzz room: ok thanks" in rendered


def test_history_is_bounded_in_messages_and_in_characters():
    msgs = [{"author": AGENT, "content": f"[SMS · out] {i} " + "x" * 900}
            for i in range(SMS_HISTORY_MESSAGES + 10)]
    lines = _render_history(msgs, AGENT).split("\n")
    assert len(lines) == SMS_HISTORY_MESSAGES
    assert all(len(line) <= SMS_HISTORY_CHARS + len("you: ") for line in lines)
    assert lines[0].startswith("you: 10 ")  # oldest kept, not oldest overall


def test_history_skips_empty_and_prefix_only_messages():
    msgs = [{"author": AGENT, "content": "[SMS · out]"},
            {"author": AGENT, "content": "   "},
            {"author": AGENT, "content": "[SMS · out] real"}]
    assert _render_history(msgs, AGENT) == "you: real"


@patch("relay.log_event", return_value=True)
@patch("relay.dispatch_to_nou", return_value="pong")
@patch("relay.send_reply", return_value={"id": "OUT", "status": "sent",
                                          "conversationId": "C1"})
def test_dispatch_gets_no_history_when_the_peer_has_no_room(send, dispatch, log, cfg):
    handle_inbound(cfg, _msg())
    assert dispatch.call_args.args[3] == ""
