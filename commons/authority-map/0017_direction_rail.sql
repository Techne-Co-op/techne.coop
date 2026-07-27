-- 0017_direction_rail.sql · A-01 · the direction rail
--
-- Common Agency (AGY, adopted 2026-07-27) makes direction a recorded,
-- member-common act: any patron member may set the instrument working,
-- on the record, within the declared Scope. This migration lands the
-- rail's write path and nothing else: one verb, one event kind entering
-- by it, refusals citing their rules. The desk (A-02), the instrument's
-- own grant (A-03), and the run harness (A-04) follow behind it.
--
-- Three shapes are worth naming:
--
--   Verb-only by construction. events_scoped_insert (0002) admits
--   members to signature, registration, opportunity, and gathering
--   kinds; direction.* is not among them, so the deployed policy set
--   already refuses the direct write and this migration widens
--   nothing. The verb is the only door (AM v0.1 §7; AGY §6).
--
--   The arc concerns the member. Every direction.* event carries the
--   directing member as agent_id, so the standing events_read policy
--   (Bylaws §18.1, §6.2.1) already shows a member their whole arc,
--   given through halted, with no read widening. Closing events
--   reference the opening one by payload.direction_id. The commons
--   shelf of AGY §8 waits on the §15 visibility decision and is
--   deliberately absent here.
--
--   Policy from the record, defaults until then. The Estate list and
--   the flooding bounds belong to the AGY-ESTATE instrument, which is
--   A-03's deliverable. Until it adopts, the verb holds the document's
--   own opening values: techne.coop alone (AGY §7), two live and five
--   a day (AGY §15, the drafter's cut, pending the steward's number).
--   When the instrument adopts, its latest un-corrected adoption
--   payload governs and the defaults retire without a code change.
--
-- At R0 (AGY §12) the agent-side kinds, direction.accepted, refused,
-- completed, and halted, enter by the steward's hand under the
-- standing overseer branch of events_scoped_insert; no grant exists
-- and none is taken here. The first grant is A-03's decision, routed,
-- not presumed.
--
-- Anchors: AGY §5, §6, §7, §11, §15; AM v0.1 §7; IM v0.1 Laws II, IV, X.

-- ---------- the direction act ----------
create or replace function give_direction(
  p_brief        text,
  p_kind         text,
  p_repositories text[] default '{}',
  p_reply_to     uuid   default null
) returns uuid
language plpgsql security definer set search_path = public as $$
declare
  v_actor      uuid := app_agent_id();
  v_brief      text := nullif(btrim(p_brief), '');
  v_kind       text := lower(btrim(coalesce(p_kind, '')));
  v_policy     jsonb;
  v_estate     jsonb;
  v_live_bound int;
  v_day_bound  int;
  v_repo       text;
  v_live       int;
  v_today      int;
  v_id         uuid;
begin
  if v_actor is null then
    raise exception 'Sign in first: no agent is bound to this session (B-01).';
  end if;

  if not app_is_member() then
    raise exception 'Direction is a member act: an active membership holds the pen (AGY section 6).';
  end if;

  if v_brief is null then
    raise exception 'A Direction needs a brief: the work, in your words (AGY section 5).';
  end if;

  if v_kind not in ('draft', 'build', 'survey', 'answer') then
    raise exception 'A Direction is one of four kinds, draft, build, survey, or answer (AGY section 7).';
  end if;

  -- Policy from the record: the AGY-ESTATE instrument's version in
  -- force, or the document's own opening values until it adopts.
  select e.payload into v_policy
  from events e
  join agreements a on a.id = e.agreement_id
  where e.kind = 'agreement.adopted'
    and a.code = 'AGY-ESTATE'
    and not exists (select 1 from events c where c.corrects = e.id)
  order by e.recorded_at desc
  limit 1;

  v_estate     := coalesce(v_policy->'repositories', '["techne.coop"]'::jsonb);
  v_live_bound := coalesce((v_policy->>'live_bound')::int, 2);
  v_day_bound  := coalesce((v_policy->>'day_bound')::int, 5);

  foreach v_repo in array p_repositories loop
    if not (v_estate ? v_repo) then
      raise exception 'Repository % is not on the Estate list (AGY section 7): the list grows by amendment, not by request.', v_repo;
    end if;
  end loop;

  if p_reply_to is not null then
    if not exists (
      select 1 from events
      where id = p_reply_to and kind = 'direction.given' and agent_id = v_actor
    ) then
      raise exception 'reply_to names one of your own Directions (AGY section 5).';
    end if;
  end if;

  -- The flooding bounds (AGY section 15): counts, not currency. A
  -- Direction is live until an event closes it by direction_id.
  select count(*) into v_live
  from events g
  where g.kind = 'direction.given'
    and g.agent_id = v_actor
    and not exists (
      select 1 from events c
      where c.kind in ('direction.completed', 'direction.refused', 'direction.halted')
        and c.payload->>'direction_id' = g.id::text
    );
  if v_live >= v_live_bound then
    raise exception 'You hold % live Direction(s), and the bound is % (AGY section 15): a Direction closes when it completes, refuses, or halts.', v_live, v_live_bound;
  end if;

  select count(*) into v_today
  from events g
  where g.kind = 'direction.given'
    and g.agent_id = v_actor
    and g.recorded_at >= date_trunc('day', now());
  if v_today >= v_day_bound then
    raise exception 'You have given % Direction(s) today, and the bound is % (AGY section 15).', v_today, v_day_bound;
  end if;

  insert into events (occurred_at, actor_agent_id, kind, agent_id, payload)
  values (
    now(), v_actor, 'direction.given', v_actor,
    jsonb_build_object(
      'brief',        v_brief,
      'kind',         v_kind,
      'repositories', to_jsonb(p_repositories),
      'reply_to',     p_reply_to
    )
  )
  returning id into v_id;

  return v_id;
end $$;
comment on function give_direction(text, text, text[], uuid) is
  'A patron member''s Direction enters the record: one direction.given event concerning the directing member, per AGY sections 5 and 6. The Estate list and the flooding bounds are read from the AGY-ESTATE instrument''s version in force, with the document''s own opening values as defaults until it adopts (AGY sections 7 and 15). The verb is the only door; refusals cite their rules (A-01).';
revoke execute on function give_direction(text, text, text[], uuid) from public, anon;
grant execute on function give_direction(text, text, text[], uuid) to authenticated;
