-- 0010_programs_view.sql · F-04 · the Programs view
-- PATRONAGE §4, §6, §8; the §15 visibility decision as recorded:
--
--   decision · Definer functions at launch; the AM v0.2 addendum
--   granting member read on the opportunity and agreement event
--   namespaces is named as the durable form and staged for the AM's
--   next version. Default adopted by Todd Youngblood 2026-07-22.
--
-- Three declarations, no schema change, per the module's own §2:
--
--   the affiliation verb · opportunity.affiliated lands as a verb so
--   the author-or-Coordinator rule is enforced somewhere the
--   interface cannot forget it (PATRONAGE §10). Revocation is a
--   compensating event through the standing corrects reference; no
--   erase exists.
--
--   the roster read · programs_roster() returns each Program agent
--   with its policy standing, Coordinator, and recognition
--   parameters, read from the version in force at call time; nothing
--   is stored twice (Law IV, Law V).
--
--   the affiliation fold · program_affiliations() returns the
--   current Opportunity-to-Program relationships as a fold over
--   opportunity.affiliated events, honoring corrections.
--
-- Convention pinned here, cited by the roster read: a Program
-- policy's agreement.adopted event sets agent_id to the Program
-- agent it governs, carries the machine-readable parameters in its
-- payload (coordinator_agent_id among them), and references its
-- POLICY-PATRONAGE-<program> agreements row (PATRONAGE §7).
-- Until such an event exists a Program stands 'in formation' and
-- carries no rates; the surface says so honestly.
--
-- The capital and allocation verbs of PATRONAGE §10 are NOT here.
-- They are S-01's emission, behind the Q3 counting rules and their
-- own explicit word; money is a stop-and-ask category (BP v1).
-- Anchors: Principle 07 (democratic by default) for the reads;
-- Bylaws §18.2 sensibility carried from the Find policies; Law X
-- (the instrument holds no role and no grant).

-- ---------- the coordinator of record ----------
-- The Coordinator named by the version in force for a Program;
-- null while the Program is in formation. Definer so the read does
-- not require row access to another member's adoption events.
create or replace function program_coordinator(p_program uuid) returns uuid
language sql stable security definer set search_path = public as $$
  select (e.payload->>'coordinator_agent_id')::uuid
  from events e
  where e.kind = 'agreement.adopted'
    and e.agent_id = p_program
    and e.payload ? 'coordinator_agent_id'
    and not exists (select 1 from events c where c.corrects = e.id)
  order by e.recorded_at desc
  limit 1
$$;
comment on function program_coordinator(uuid) is
  'The coordinator_agent_id carried by the latest uncorrected agreement.adopted event concerning the Program. PATRONAGE §6: a creature of the policy, not an office.';

-- ---------- the affiliation verb ----------
create or replace function affiliate_opportunity(p_opportunity uuid, p_program uuid)
returns uuid
language plpgsql security definer set search_path = public as $$
declare
  v_actor    uuid := app_agent_id();
  v_author   uuid;
  v_title    text;
  v_kind     agent_kind;
  v_existing uuid;
  v_event    uuid;
begin
  if v_actor is null then
    raise exception 'Sign in first: no agent is bound to this session (B-01).';
  end if;
  if not app_is_member() and not app_is_overseer() then
    raise exception 'Affiliating requires an active membership (Bylaws §18.2).';
  end if;

  select kind into v_kind from agents where id = p_program;
  if v_kind is null or v_kind <> 'program' then
    raise exception 'The target is not a Program agent (PATRONAGE §4).';
  end if;

  select author_agent_id, title into v_author, v_title
  from opportunities where id = p_opportunity;
  if v_author is null then
    raise exception 'No such opportunity.';
  end if;

  if v_actor <> v_author
     and v_actor is distinct from program_coordinator(p_program)
     and not app_is_overseer() then
    raise exception 'Only the Opportunity author or the Program Coordinator may affiliate (PATRONAGE §4).';
  end if;

  -- an affiliation that already stands is returned, not duplicated
  select e.id into v_existing
  from events e
  where e.kind = 'opportunity.affiliated'
    and e.agent_id = p_program
    and (e.payload->>'opportunity_id')::uuid = p_opportunity
    and not exists (select 1 from events c where c.corrects = e.id)
  limit 1;
  if v_existing is not null then
    return v_existing;
  end if;

  insert into events (occurred_at, actor_agent_id, kind, agent_id, payload)
  values (
    now(), v_actor, 'opportunity.affiliated', p_program,
    jsonb_build_object('opportunity_id', p_opportunity, 'title', v_title)
  )
  returning id into v_event;
  return v_event;
end $$;
comment on function affiliate_opportunity(uuid, uuid) is
  'One Opportunity joins one Program, per PATRONAGE §4 and §5: an event concerning the Program, the opportunity in its payload, written only by the author, the Coordinator of record, or an overseer. Revocation is a compensating event via corrects.';
revoke execute on function affiliate_opportunity(uuid, uuid) from public, anon;
grant execute on function affiliate_opportunity(uuid, uuid) to authenticated;

-- ---------- the roster read ----------
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
  )
  select
    p.id,
    p.display_name,
    ad.payload->>'purpose',
    case when ad.agent_id is null then 'in formation' else 'in force' end,
    (ad.payload->>'coordinator_agent_id')::uuid,
    c.display_name,
    ag.code,
    ag.version,
    ad.payload->'active_primitives',
    ad.payload->'weights'
  from agents p
  left join adoption ad on ad.agent_id = p.id
  left join agreements ag on ag.id = ad.agreement_id
  left join agents c on c.id = (ad.payload->>'coordinator_agent_id')::uuid
  where p.kind = 'program'
  order by p.display_name
$$;
comment on function programs_roster() is
  'The Programs view''s roster read, per the §15 visibility decision (definer functions at launch, 2026-07-22): each Program with its standing and the recognition parameters of the version in force. Returns summaries only; widens no row access. PATRONAGE §8, Principle 07.';
revoke execute on function programs_roster() from public, anon;
grant execute on function programs_roster() to authenticated;

-- ---------- the affiliation fold ----------
create or replace function program_affiliations()
returns table (
  opportunity_id   uuid,
  program_agent_id uuid,
  event_id         uuid,
  affiliated_at    timestamptz
)
language sql stable security definer set search_path = public as $$
  select distinct on ((e.payload->>'opportunity_id')::uuid)
    (e.payload->>'opportunity_id')::uuid,
    e.agent_id,
    e.id,
    e.recorded_at
  from events e
  where e.kind = 'opportunity.affiliated'
    and not exists (select 1 from events c where c.corrects = e.id)
  order by (e.payload->>'opportunity_id')::uuid, e.recorded_at desc
$$;
comment on function program_affiliations() is
  'The current Opportunity-to-Program relationships as a read-time fold over opportunity.affiliated events, honoring corrections; the board''s view of an Opportunity''s Program per PATRONAGE §4. An affiliation traces to the event that made it (F-04 acceptance).';
revoke execute on function program_affiliations() from public, anon;
grant execute on function program_affiliations() to authenticated;
