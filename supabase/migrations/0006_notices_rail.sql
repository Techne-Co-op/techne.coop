-- 0006_notices_rail.sql · X-02 · Notices v1
-- The email rail: a database trigger forwards admission events to the
-- notices edge function, which delivers the transactional email. The
-- trigger carries no secret: the anon key it sends is the same public
-- key every page already embeds, and the function does its privileged
-- work with its own service credentials, held in Supabase secrets
-- under the reference-not-value rule.
--
-- Rail shape (X-02 escalation card, decided 2026-07-20): Resend on
-- the free tier, called from the notices edge function, triggered by
-- the insert of a membership.applied event. One seam: swap the sender
-- inside the function, nothing here changes.
--
-- Anchors: notices per Bylaws §2.4 and Art. X; admission intake per
-- §1.3.3 (the steward manages intake, so the steward is notified).
-- Applied to the live CIS by the steward on adoption (Tier B: touches
-- the events table's trigger surface, no policy or schema change).

create extension if not exists pg_net;

create or replace function notify_notices_rail() returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  perform net.http_post(
    url     := 'https://ujujwgopdwirebgcpekc.supabase.co/functions/v1/notices',
    headers := jsonb_build_object(
      'Content-Type', 'application/json',
      'Authorization', 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVqdWp3Z29wZHdpcmViZ2NwZWtjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM3ODc3ODIsImV4cCI6MjA5OTM2Mzc4Mn0.v6atltp9vbEj0RN2stSuDrzOdWVHB9GGR6rwPCwBNEk'
    ),
    body    := jsonb_build_object('event', to_jsonb(new))
  );
  return new;
end $$;

comment on function notify_notices_rail() is 'X-02 Notices v1: forwards admission events to the notices edge function. Bylaws §2.4, Art. X, §1.3.3.';

create trigger events_notices_rail
  after insert on events
  for each row
  when (new.kind = 'membership.applied')
  execute function notify_notices_rail();
