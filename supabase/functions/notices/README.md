# notices · X-02 · deployment

The notices rail in steward steps. The repo carries everything;
these steps wire it to the world.

Two sinks (2026-07-21 amendment): the steward intake notice rides
Telegram; the applicant acknowledgment rides Resend email. Each
activates when its secrets are present. The email sink waits on
techne.coop domain verification (DNS is managed outside the
steward's reach); the Telegram sink does not wait with it.

## 1. Telegram (steward notice: live first)

- Create the bot with @BotFather; record the HTTP API token.
- The steward opens the bot and presses Start (a bot cannot message
  anyone who has not messaged it first).
- Read the chat id from `getUpdates` on the Bot API.

## 2. Resend (applicant acknowledgment: when DNS lands)

- Create the Resend account (free tier covers present volume).
- Verify the sending domain (techne.coop) in Resend: two DNS records,
  placed by whoever manages the zone.
- Copy the API key. It goes into Supabase secrets, never into a file.

## 3. Function

From a checkout, with the Supabase CLI logged in:

```
supabase functions deploy notices --project-ref ujujwgopdwirebgcpekc
supabase secrets set --project-ref ujujwgopdwirebgcpekc \
  TELEGRAM_BOT_TOKEN=... \
  TELEGRAM_CHAT_ID=... \
  RESEND_API_KEY=... \
  NOTICES_FROM="Techne <notices@techne.coop>" \
  STEWARD_EMAIL=...
```

Set what exists; omit what doesn't. The function names any gap in the
steward notice rather than dropping it. (SUPABASE_URL and
SUPABASE_SERVICE_ROLE_KEY are provided to the function by the
platform.)

## 4. Trigger

Apply `supabase/migrations/0006_notices_rail.sql` in the SQL editor.
It enables pg_net and adds the events trigger; it carries no secret.

## Acceptance (X-02)

Submit the live join form. The steward receives the intake notice on
Telegram; if the email sink is configured, the applicant address
receives the acknowledgment. That delivery is the acceptance:
admission notice delivered on the membership.state transition to
applied.

## Note on the applicant address

The function reads the address from the event payload's `email`
field, falling back to the application row. If B-02's
apply_for_membership() stores the email elsewhere, adjust the lookup
in index.ts once its source lands in the repository (the X-09
restore-completeness card).
