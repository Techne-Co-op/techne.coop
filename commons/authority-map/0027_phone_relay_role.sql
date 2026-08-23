-- 0027_phone_relay_role.sql · SMS-01 · scoped writer for the quo-relay
-- Follow-up to 0026. The floor tier of the relay was drafted to write
-- with the service_role key; the steward's read of the PR asked for a
-- narrower hand before it went live. This migration is that hand.
--
-- The service_role key bypasses row-level security and reads every
-- table in the CIS. A leak of it from a small always-on Python service
-- on a shared VM is a full compromise of the record. The relay only
-- needs to append rows to one table, so it gets exactly that and
-- nothing more.
--
-- Shape:
--   role phone_relay: nologin, noinherit, not a superuser. Cannot be
--     used to sign in on its own; assumed by PostgREST via SET ROLE
--     when a request presents an API key whose JWT template names it.
--   grant phone_relay TO authenticator: gives PostgREST the ability to
--     assume the role at request time. Without this membership the
--     API returns 42501 "permission denied to set role".
--   grant INSERT ON phone_events TO phone_relay: the only table
--     privilege this role holds anywhere in the database. No SELECT
--     on phone_events (so the log is write-only from this key), no
--     UPDATE or DELETE (append-only in practice, not just in comment
--     form), and nothing on any other table.
--   policy phone_relay_insert: RLS is on and has no policies, so a
--     bare INSERT still fails. This policy permits INSERT from the
--     phone_relay role with no row-shape restriction; the table's
--     check constraints (E.164 shape, direction enum, length cap) do
--     the shape-of-a-row validation.
--
-- The service_role key remains the sole reader of phone_events, used
-- by a walker or a member-facing query when Phase 1 proper lands.
-- Nothing about the read path changes here.
--
-- Applied to the live CIS by the steward as part of the SMS-01 deploy;
-- corresponding Supabase secret API key (JWT template role=phone_relay)
-- lives at ~/.config/secrets/nou-phone-relay.env.gpg on the relay host.
-- Not adopted; drafted, deployed to enable the tier-1 read.

create role phone_relay nologin noinherit;
grant phone_relay to authenticator;

grant insert on table phone_events to phone_relay;
-- No SELECT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER: only INSERT.
-- No usage on any schema beyond public (default), and no grants on any
-- other table.

-- Anchor: append-only recording of the co-op line is a housekeeping
-- act by an agent under owner authority (Bylaws v2.1 §2.1); this policy
-- grants that seat to the phone_relay role and nothing else. Art. XV
-- (records) untouched: read remains service_role only.
create policy phone_relay_insert on phone_events
  for insert to phone_relay
  with check (true);
-- The row-shape check clauses on phone_events (peer_e164 E.164 regex,
-- direction in ('in','out'), content length) do the validation. The
-- policy adds no further restriction because the relay is trusted to
-- write what it received; the log is a truthful transcript, not a
-- filtered one.
