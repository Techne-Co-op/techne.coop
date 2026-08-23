-- 0026_phone_events.sql · SMS-01 · the steward's phone line speaks
-- Decision: the steward's direction (2026-08-22, DM): put the co-op
-- agent behind the co-op phone number under the same authority as
-- the owner-only Buzz seat. First tier is the steward alone. This
-- migration adds only the log of what crossed the line; no schema
-- on profiles, no binding, no member scoping.
--
-- Sibling of events, not a column of profiles. Two reasons kept
-- honest: no member has a bound phone yet, so an agent_id column
-- would be null for every row; and this table records an external
-- carrier's traffic, not a member's act on the record. The join
-- key back to a member arrives with the verified-phone column when
-- Phase 1 proper lands (issue #191), which is a stop card and needs
-- a named human. Nothing here waits on that.
--
-- Append-only by discipline, not by trigger. The service inserts;
-- nothing updates or deletes in normal operation. RLS enabled with
-- no policies: no client selects. The service role bypasses RLS
-- and is the sole reader. A future member-scoped read arrives with
-- Phase 1 and is not sketched here.
--
-- Restores replay these rows as data, not as calls. The service's
-- reply path is idempotent on quo_message_id, so a replayed inbound
-- does not re-send. The unique constraint on quo_message_id is the
-- teeth.
--
-- Anchors: the plan at issue #191; the tiered security model in its
-- 2026-08-19 comments; the Buzz owner-allowlist analogue at
-- ~/bin/nou-buzz-harness.sh. Not adopted; drafted. Applied to the
-- live CIS by the steward on adoption.

create table phone_events (
  id              uuid primary key default gen_random_uuid(),
  occurred_at     timestamptz not null default now(),
  direction       text not null check (direction in ('in', 'out')),
  peer_e164       text not null check (peer_e164 ~ '^\+[1-9][0-9]{7,14}$'),
  content         text not null check (char_length(content) <= 4096),
  quo_message_id  text unique,
  conversation_id text,
  status          text,
  error           text,
  payload         jsonb not null default '{}'::jsonb
);
comment on table phone_events is
  'SMS-01: append-only log of every inbound and outbound message on the co-op phone line. One row per carrier message. Owner reads only; no client policies. Sibling of events, not of profiles.';
comment on column phone_events.peer_e164 is
  'The other end of the exchange in E.164 (+CCXXXXXXXXXX). For direction=in this is the sender; for out it is the recipient. The co-op line itself is implicit.';
comment on column phone_events.quo_message_id is
  'Quo API message id. Unique so a replayed inbound webhook does not double-log; the service is idempotent on this key.';
comment on column phone_events.payload is
  'The full carrier payload as received, retained verbatim for audit. Redact secrets from the source before writing.';

create index phone_events_occurred_idx on phone_events (occurred_at desc);
create index phone_events_peer_idx     on phone_events (peer_e164, occurred_at desc);

alter table phone_events enable row level security;
-- No policies. Service role reads and writes; every other role sees nothing.
-- A future member-scoped read arrives with the verified-phone column (issue
-- #191, Phase 1 proper) and belongs in the migration that adds the binding.
