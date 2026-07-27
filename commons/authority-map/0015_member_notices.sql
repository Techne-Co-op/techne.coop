-- 0015_member_notices.sql · X-12 · the member's rail
-- Law I holds that every relationship between records is itself an event,
-- yet a response landed as a row alone and a registration never spoke at
-- all. The author learned nothing unless they went and looked; the host
-- counted heads by refreshing. Two definer triggers close the gap: the
-- relationship lands in the log addressed to the member it concerns
-- (agent_id) and acted by the member who made it (actor_agent_id).
-- events_read (0002) already gives an agent sight of what concerns them
-- per §18.1, so the rail rides authority that has stood since the
-- substrate; no policy changes here.
--
-- The notice is renderable from the event alone: each trigger carries the
-- actor's display name and the record's title into the payload at the
-- moment of the act, the same denormalization apply_for_membership (0007)
-- and the scheduling act (0013) already practice. No event is addressed
-- to its own actor: a host registering for their own gathering stays
-- silent, because a notice about your own act is noise, not news.
--
-- Restores replay these rows, they do not relive them: import_cis.py sets
-- session_replication_role to replica so the triggers speak only for live
-- acts, and the walkaway stays byte-identical.
--
-- Anchors: an agent reads what concerns them per §18.1 and AM v0.1 §18.2;
-- the calendar and its host per §2.1; notices per §2.4 and Art. X.
-- Applied to the live CIS by the steward on adoption (Tier B: trigger
-- surface only, no policy or schema change).

-- §18.2: the author of an opportunity is party to every response on it;
-- the response event is addressed to them.
create or replace function public.notify_opportunity_response() returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into events (occurred_at, actor_agent_id, agent_id, kind, payload)
  select now(), new.agent_id, o.author_agent_id, 'opportunity.responded',
         jsonb_build_object(
           'opportunity_id', o.id,
           'title',          o.title,
           'response_id',    new.id,
           'responder',      (select display_name from agents where id = new.agent_id))
    from opportunities o
   where o.id = new.opportunity_id
     and o.author_agent_id <> new.agent_id;
  return new;
end $$;

comment on function public.notify_opportunity_response() is
  'X-12 member notices: a response lands in the log addressed to the author. AM v0.1 §18.2; Bylaws §2.4, Art. X; Law I.';

create trigger responses_notify
  after insert on responses
  for each row
  execute function public.notify_opportunity_response();

-- §2.1: the host keeps their gathering; each turn of a registration is
-- addressed to them. The WHEN guard keeps a no-op update silent.
create or replace function public.notify_registration_turn() returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into events (occurred_at, actor_agent_id, agent_id, kind, payload)
  select now(), new.agent_id, g.host_agent_id, 'registration.' || new.state,
         jsonb_build_object(
           'gathering_id', g.id,
           'title',        g.title,
           'session_id',   new.session_id,
           'registrant',   (select display_name from agents where id = new.agent_id))
    from sessions s
    join gatherings g on g.id = s.gathering_id
   where s.id = new.session_id
     and g.host_agent_id <> new.agent_id;
  return new;
end $$;

comment on function public.notify_registration_turn() is
  'X-12 member notices: each registration turn lands in the log addressed to the host. Bylaws §2.1, §2.4, Art. X; Law I.';

create trigger registrations_notify_insert
  after insert on registrations
  for each row
  execute function public.notify_registration_turn();

create trigger registrations_notify_turn
  after update of state on registrations
  for each row
  when (old.state is distinct from new.state)
  execute function public.notify_registration_turn();
