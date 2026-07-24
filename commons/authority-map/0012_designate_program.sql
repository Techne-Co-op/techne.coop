-- 0012_designate_program.sql · F-05 · the designation act
--
-- Beat 11 of the run-through asked the steward to bring a Program into
-- being by hand, an insert typed into the SQL editor. An act the rules
-- care about should not require a database console: the same act now
-- stands behind a verb, guarded where the interface cannot forget it,
-- and recorded as an event like every other act (Law X, people decide;
-- Law IV, cite as you enforce).
--
-- The shape of a Program is unchanged and deliberately thin. PATRONAGE
-- §4 makes a Program an agent, and §7 puts its substance, purpose,
-- Coordinator, active Primitives, weights, funding bounds, in the
-- payload of its POLICY-PATRONAGE adoption event, read from the version
-- in force at call time. So designation carries only what a Program has
-- before any policy governs it: a name, and a sentence about what it is
-- for. Everything else extends later through the adoption event that
-- 0010 already reads, with no schema change here and none needed then.
-- No programs table is created: identity lives in agents (Law I), and a
-- second table would be a second truth.
--
-- Two declarations:
--
--   designate_program() · a steward or director act. Inserts the agent
--   row and records program.designated concerning it. Idempotent by
--   name: designating a Program that already stands returns the one
--   that stands rather than a twin.
--
--   programs_roster() · re-declared so a Program in formation shows the
--   purpose its designation carried. Before this, purpose was read only
--   from the adoption payload, so a designated Program sat nameless of
--   intent until its policy adopted. The adoption payload still wins
--   where both exist; nothing is stored twice.
--
-- Anchors: Bylaws §3.1 and §4.1 (the Board manages; officers act),
-- carried here as the overseer guard already defined by 0002.
-- Cites: PATRONAGE §4, §6, §7, §8; IM v0.1 Law I, Law IV, Law X.

-- ---------- the designation act ----------
create or replace function designate_program(p_display_name text, p_purpose text default null)
returns uuid
language plpgsql security definer set search_path = public as $$
declare
  v_actor   uuid := app_agent_id();
  v_name    text := nullif(btrim(p_display_name), '');
  v_purpose text := nullif(btrim(p_purpose), '');
  v_program uuid;
begin
  if v_actor is null then
    raise exception 'Sign in first: no agent is bound to this session (B-01).';
  end if;

  -- Designating a Program is a governing act, not a member courtesy.
  if not app_is_overseer() then
    raise exception 'Designating a Program is a steward or director act (Bylaws sections 3.1 and 4.1).';
  end if;

  if v_name is null then
    raise exception 'A Program needs a name.';
  end if;

  -- One name, one Program. An existing one is returned, never doubled.
  select id into v_program
  from agents
  where kind = 'program' and lower(display_name) = lower(v_name)
  limit 1;
  if v_program is not null then
    return v_program;
  end if;

  insert into agents (kind, display_name)
  values ('program', v_name)
  returning id into v_program;

  insert into events (occurred_at, actor_agent_id, kind, agent_id, payload)
  values (
    now(), v_actor, 'program.designated', v_program,
    jsonb_build_object('display_name', v_name, 'purpose', v_purpose)
  );

  return v_program;
end $$;
comment on function designate_program(text, text) is
  'A Program enters the record by a steward or director act: the agent row and the program.designated event together, per PATRONAGE section 4 and Bylaws sections 3.1 and 4.1. Idempotent by name. Substance arrives later in the POLICY-PATRONAGE adoption payload (section 7); designation carries only name and purpose.';
revoke execute on function designate_program(text, text) from public, anon;
grant execute on function designate_program(text, text) to authenticated;

-- ---------- the roster read, re-declared ----------
-- Unchanged but for the purpose fallback: a Program in formation now
-- shows the intent its designation carried, so the surface is honest
-- about what a thing is for before its policy governs it.
create or replace function programs_roster()
returns table (
  program_agent_id     uuid,
  display_name         text,
  purpose              text,
  standing             text,
  coordinator_agent_id uuid,
  coordinator_name     text,
  policy_code          text,
  policy_version       text,
  active_primitives    jsonb,
  weights              jsonb
)
language sql stable security definer set search_path = public as $$
  with adoption as (
    select distinct on (e.agent_id)
      e.agent_id, e.agreement_id, e.payload
    from events e
    where e.kind = 'agreement.adopted'
      and not exists (select 1 from events c where c.corrects = e.id)
      and exists (select 1 from agents p where p.id = e.agent_id and p.kind = 'program')
    order by e.agent_id, e.recorded_at desc
  ),
  designation as (
    select distinct on (e.agent_id)
      e.agent_id, e.payload
    from events e
    where e.kind = 'program.designated'
      and not exists (select 1 from events c where c.corrects = e.id)
    order by e.agent_id, e.recorded_at desc
  )
  select
    p.id,
    p.display_name,
    coalesce(ad.payload->>'purpose', dg.payload->>'purpose'),
    case when ad.agent_id is null then 'in formation' else 'in force' end,
    (ad.payload->>'coordinator_agent_id')::uuid,
    c.display_name,
    ag.code,
    ag.version,
    ad.payload->'active_primitives',
    ad.payload->'weights'
  from agents p
  left join adoption ad on ad.agent_id = p.id
  left join designation dg on dg.agent_id = p.id
  left join agreements ag on ag.id = ad.agreement_id
  left join agents c on c.id = (ad.payload->>'coordinator_agent_id')::uuid
  where p.kind = 'program'
  order by p.display_name
$$;
comment on function programs_roster() is
  'The Programs view roster read, per the PATRONAGE section 15 visibility decision (definer functions at launch, 2026-07-22): each Program with its standing and the recognition parameters of the version in force. Purpose falls back to the designation event while a Program is in formation (F-05). Returns summaries only; widens no row access.';
revoke execute on function programs_roster() from public, anon;
grant execute on function programs_roster() to authenticated;
