# notices · X-02 · deployment

The email rail in three steward steps. The repo carries everything;
these steps wire it to the world.

## 1. Resend

- Create the Resend account (free tier covers present volume).
- Verify the sending domain (techne.coop) in Resend: two DNS records.
- Copy the API key. It goes into Supabase secrets, never into a file.

## 2. Function

From a checkout, with the Supabase CLI logged in:

```
supabase functions deploy notices --project-ref ujujwgopdwirebgcpekc
supabase secrets set --project-ref ujujwgopdwirebgcpekc \
  RESEND_API_KEY=... \
  NOTICES_FROM="Techne <notices@techne.coop>" \
  STEWARD_EMAIL=...
```

(SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are provided to the
function by the platform.)

## 3. Trigger

Apply `supabase/migrations/0006_notices_rail.sql` in the SQL editor.
It enables pg_net and adds the events trigger; it carries no secret.

## Acceptance (X-02)

Submit the live join form. The applicant address receives the
acknowledgment; STEWARD_EMAIL receives the intake notice. That
delivery is the acceptance: admission notice delivered on the
membership.state transition to applied.

## Note on the applicant address

The function reads the address from the event payload's `email`
field, falling back to the application row. If B-02's
apply_for_membership() stores the email elsewhere, adjust the lookup
in index.ts once its source lands in the repository (the X-09
restore-completeness card).
