-- 0016_notices_rail_kinds.sql · X-12 · the rail widens its ear
-- The notices trigger (0006) listened for one kind. The member's rail
-- (0015) now lands four more in the log, and the away-channel half of
-- X-12 wants them forwarded to the notices function, which emails the
-- concerned member once the sending domain verifies (X-02 amendment
-- pattern: a sink activates when its secrets exist; until then the
-- function answers quietly and the in-app rail carries the whole load).
-- Recreating the trigger is the one way to widen a WHEN clause.
--
-- Anchors: notices per Bylaws §2.4 and Art. X; intake per §1.3.3.
-- Applied to the live CIS by the steward on adoption (Tier B: touches
-- the events table's trigger surface, no policy or schema change).
-- Not in the CI chain: pg_net and the deployed function exist only in
-- the live project, the same standing 0006 has.

drop trigger if exists events_notices_rail on events;

create trigger events_notices_rail
  after insert on events
  for each row
  when (new.kind in (
    'membership.applied',
    'membership.admitted',
    'opportunity.responded',
    'registration.registered',
    'registration.cancelled'
  ))
  execute function notify_notices_rail();
