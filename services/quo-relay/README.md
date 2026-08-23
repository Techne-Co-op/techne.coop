# quo-relay · SMS-01

The steward's phone line answered by Nou. First tier of the plan at
[#191](https://github.com/Techne-Co-op/techne.coop/issues/191): owner-only,
read-only, over SMS.

Two runtime shapes ship in this directory:

- **poll.py** : a persistent poll loop against `GET /v1/messages` on the
  Quo API. No inbound HTTP, no DNS, no Cloudflare. Runs on noesis as a
  systemd user unit. **This is the shape that deploys first**; it is what
  the initial merge turns on.
- **webhook.py** : a signature-verified webhook receiver for
  `message.received`. Not deployed by this PR. Ships in a follow-up when
  DNS (`sms.techne.coop`) and Cloudflare fronting exist; the code is here
  so the two shapes can be reviewed side by side and the poll loop can be
  retired cleanly.

Both shapes share `relay.py`, which holds the allowlist gate, the Nou
session dispatch, the reply path, and the `phone_events` writes. The
tests exercise `relay.py`.

## The tier this ships

Read-only, steward-only, from `+13035059612`. Every other sender is
dropped before dispatch; the drop is logged as a `phone_events` row with
`direction='in'`, `status='ignored'`, and no reply. `STOP` from the
steward clears the in-memory session cache and skips the dispatch;
because there is no binding table yet, `STOP` does not need to write
anywhere.

What this tier does NOT do, restated so no drift is possible:

- No answering anyone but the steward.
- No writes to the CIS. Nou answers about the record as the steward may
  already read it under §18.1, never wider.
- No confidential records under §18.2, no other member's contact detail,
  no unpublished treasury figure.
- No agent-initiated outbound. The service only replies to a message the
  steward sent first in the same conversation.
- No cross-conversation memory persistence: each conversation is a fresh
  Nou session bounded to the steward's messages in that conversation. The
  `phone_events` table is the record; the session is transient.

## Environment

`/etc/default/nou-quo-relay` (mode 600, owned by the service user):

```
QUO_API_KEY=<from ~/.config/secrets/quo.env.gpg>
QUO_PHONE_NUMBER_ID=PNK5N9GAMW
QUO_LINE_E164=+19702927888
QUO_ALLOWLIST=+13035059612
QUO_POLL_INTERVAL_SEC=15
QUO_WEBHOOK_SIGNING_KEY=<set only when webhook.py ships>
CIS_URL=https://ujujwgopdwirebgcpekc.supabase.co
CIS_PHONE_RELAY_KEY=<from ~/.config/secrets/nou-phone-relay.env.gpg>
NOU_ACP_COMMAND=openclaw
NOU_ACP_ARGS=acp
```

`CIS_PHONE_RELAY_KEY` is a Supabase secret API key bound to the
`phone_relay` Postgres role. That role has INSERT-only on `phone_events`
and no other table privileges anywhere in the CIS; RLS on `phone_events`
carries one policy (`phone_relay_insert`) that permits inserts and
nothing else. A leak of this key lets an attacker append log rows to
`phone_events`; it cannot read the log back, tamper with existing rows,
or reach any other table. The service_role key is never held by the
relay.

`QUO_API_KEY`, `QUO_ALLOWLIST`, and `CIS_PHONE_RELAY_KEY` never appear in
logs. `QUO_ALLOWLIST` is a comma-separated E.164 list; the poll loop and
the webhook both compare exact strings, no normalisation.

## Deploy · poll mode

```
sudo cp systemd/nou-quo-relay.service /etc/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now nou-quo-relay.service
journalctl --user -u nou-quo-relay -f
```

Health check: `curl -s http://127.0.0.1:9631/health` returns
`{"status":"ok","last_poll_at":"..."}` when the loop has run at least
once. The port is loopback only in poll mode.

## Deploy · webhook mode (later)

Requires `sms.techne.coop` A/AAAA to Cloudflare, an origin rule to
noesis:9631, and a signing key set on the Quo webhook. Verification
follows OpenPhone's HMAC-SHA256 scheme; see `webhook.py` for the exact
header names. Turn off the poll loop when the webhook goes live; both
running at once will double-log inbound messages (the unique constraint
on `phone_events.quo_message_id` protects against double-writes, but the
service will emit warnings on every collision).

## What ships next

- Verified-phone column on `profiles` and binding state machine (schema,
  stop card, needs a named human).
- Second-factor for Tier 2 acts (Buzz DM challenge is cheapest; passkey
  is general). See issue #191 comments for the full design.
- Multi-signature for Tier 3.

None of the above is in this PR.
