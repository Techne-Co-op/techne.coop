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

## Who the frame says is texting

Every dispatch opens with one bracketed line naming the sender and the
evidence behind the name. It used to read `[SMS from steward, tier 1
read-only, peer=...]` for **every** inbound, whoever sent it, because the
label was a constant in `dispatch_to_nou()` while the binding the relay
had just resolved was thrown away before dispatch. A correctly bound
member therefore arrived wearing the steward's name. That is an identity
defect, not a cosmetic one, and it was live until this change.

`_sender_frame()` now has three states and always says which one it is
in:

| what the relay knows | what the frame says |
| --- | --- |
| a verified `phone_bindings` row | `SMS from verified bound member <first 16 hex of member_pubkey>, peer=..., binding verified by ceremony` |
| looked, found no binding, number is in `QUO_ALLOWLIST` | `SMS from an allowlisted number, peer=..., no binding and no key evidence` |
| the binding directory could not be read | `SMS from peer=..., identity unknown: ... treat the sender as unidentified` |

Two rules hold across all three. **Tier is asserted, identity is not.**
`tier 1 read-only` is a property of the channel and is true of every SMS
turn, so the frame keeps saying it. Who the person is comes only from a
binding, so the frame asserts a name only where a binding produced one.
And **the failure state is its own state.** A lookup that raised is not a
lookup that found nothing, so the frame does not round the first down to
the second; it says the identity is unknown. This follows the rule
already governing the gate, that a router outage narrows the service to
tier one and never widens it. The narrowing now reaches the frame as
well as the gate.

There is no default label. An unbound peer cannot be described as anyone,
and the word `steward` can never appear in a frame built without a
binding. Tests hold that line directly.

What this does **not** fix: an SMS sender id is spoofable, so the phone
number is still the whole credential behind a binding. Moving the
ceremony to a signed-in intranet session is issue #247 and is not
attempted here.

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

# --- tier two (SMS-03), all optional; absent = pure tier one ---
CIS_PHONE_ROUTER_KEY=<phone_router scoped key; SELECT on verified bindings only>
CIS_PHONE_BINDER_KEY=<phone_binder scoped key; ceremony writes>
BUZZ_CEREMONY_CHANNEL_ID=<comma-separated channels where !bind / !verify are answered>
BUZZ_OWNER_PUBKEY=<steward hex pubkey, seated in every binding room>
BUZZ_AGENT_PUBKEY=<agent hex pubkey, filtered from ceremony echo>
BUZZ_PRIVATE_KEY=<agent Nostr key for the buzz CLI>
BUZZ_AUTH_TAG=<NIP-OA owner attestation for the buzz CLI>
BUZZ_RELAY_URL=wss://buzz.techne.coop
BUZZ_CLI=/home/openclaw/bin/buzz
```

Tier two adds the SMS-02 design's ceremony and routing (see
/commons/build/sms-bindings/): `!bind +1XXXXXXXXXX` in the ceremony
channel sends a one-time code over the line; `!verify <code>` from the
same Nostr key completes the binding, and the service creates a private
channel seating the member, the agent, and the steward. A verified
binding admits a number the same way the tier-one allowlist does; STOP
from a bound number revokes the binding and sends the one confirmation
the carrier rules require. A `phone_router` outage narrows the service
to tier one; it never widens it.

`BUZZ_CEREMONY_CHANNEL_ID` takes a comma-separated list, and the service
watches all of them. One shared ceremony room would mean every `!bind`
posts a member's phone number where the other members can read it, so
each member gets a private room and the list is how the service learns
about them. A single id still works and is read as a list of one.

The poll loop widens with the same set. Quo's `participants` filter is an
exact conversation match rather than an OR, so the service issues one
request per number, over the allowlist plus every verified binding.
Widening the gate alone would not have been enough: a number the poll
never queries is a member whose text the service never sees.

`CIS_PHONE_RELAY_KEY` is a Supabase secret API key bound to the
`phone_relay` Postgres role. That role has INSERT-only on `phone_events`
and no other table privileges anywhere in the CIS; RLS on `phone_events`
carries one policy (`phone_relay_insert`) that permits inserts and
nothing else. A leak of this key lets an attacker append log rows to
`phone_events`; it cannot read the log back, tamper with existing rows,
or reach any other table. The service_role key is never held by the
relay.

## Reply length is a bill

Quo charges $0.01 per outbound segment on every API-sent message, drawn
from a prepaid credit balance that fails closed: when it runs dry the API
returns `402 Not Enough Credits` on every send and the reply is composed
and lost. That happened live on 2026-08-25, mid-conversation, with no
warning anywhere in the dashboard. Keep auto-recharge on.

A segment is 160 GSM-7 characters, or **70** if the message contains even
one character outside that set. The service defends the bill twice:

- The dispatch frame asks for one or two sentences under 300 characters,
  plain ASCII, and tells the model why.
- `to_gsm7()` folds the reply before it is measured or sent, so smart
  quotes, em dashes, and emoji cannot silently double the cost. The
  character counts in `split_for_sms()` are the counts the carrier bills.

`NOU_SMS_PART_CHARS` (default 320) and `NOU_SMS_MAX_PARTS` (default 2) cap
the worst case at four segments, four cents, per reply. Overflow is
dropped and the member is told so, never truncated silently.

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
