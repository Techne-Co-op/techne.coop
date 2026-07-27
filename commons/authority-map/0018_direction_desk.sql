-- 0018_direction_desk.sql · A-02 · what the desk may read
--
-- The desk (AGY §8) shows a member the bounds before they act: the
-- Estate list in force, the flooding bounds, and how much of their own
-- allowance stands. Those parameters live in the AGY-ESTATE adoption
-- event, which concerns the cooperative rather than the member, so the
-- standing events_read policy does not show them. This is the same
-- visibility cell PATRONAGE §6 and §8 named, and it takes the same
-- route the steward decided for those on 2026-07-22: a definer function
-- returning exactly the summary the surface needs, widening no row
-- access, with the AM v0.2 addendum named as the durable form.
--
-- The member's arc needs nothing here: every direction.* event concerns
-- the directing member, so events_read already shows it whole.
--
-- One function. Its defaults are the verb's defaults (0017), read from
-- the same place by the same rule, so the page cannot promise a bound
-- the verb would not enforce.
--
-- Anchors: AGY §7, §8, §15; PATRONAGE §15 visibility decision as
-- recorded 2026-07-22; IM v0.1 Law IV.

create or replace function direction_standing()
returns table (
  repositories   jsonb,
  live_bound     int,
  day_bound      int,
  live_now       int,
  given_today    int,
  policy_code    text,
  policy_version text
)
language plpgsql stable security definer set search_path = public as $$
declare
  v_self   uuid := app_agent_id();
  v_policy jsonb;
  v_agr_id uuid;
begin
  if v_self is null then
    raise exception 'Sign in first: no agent is bound to this session (B-01).';
  end if;

  select e.payload, e.agreement_id into v_policy, v_agr_id
  from events e
  join agreements a on a.id = e.agreement_id
  where e.kind = 'agreement.adopted'
    and a.code = 'AGY-ESTATE'
    and not exists (select 1 from events c where c.corrects = e.id)
  order by e.recorded_at desc
  limit 1;

  return query
  select
    coalesce(v_policy->'repositories', '["techne.coop"]'::jsonb),
    coalesce((v_policy->>'live_bound')::int, 2),
    coalesce((v_policy->>'day_bound')::int, 5),
    (select count(*)::int from events g
      where g.kind = 'direction.given' and g.agent_id = v_self
        and not exists (
          select 1 from events c
          where c.kind in ('direction.completed', 'direction.refused', 'direction.halted')
            and c.payload->>'direction_id' = g.id::text)),
    (select count(*)::int from events g
      where g.kind = 'direction.given' and g.agent_id = v_self
        and g.recorded_at >= date_trunc('day', now())),
    (select code from agreements where id = v_agr_id),
    (select version from agreements where id = v_agr_id);
end $$;
comment on function direction_standing() is
  'The desk reads the bounds before a member acts: the Estate list and the flooding bounds of the AGY-ESTATE version in force, with the AGY defaults until it adopts, and the caller''s own live and daily counts. Definer, per the PATRONAGE section 15 visibility decision of 2026-07-22; returns a summary and widens no row access (A-02, AGY sections 7, 8, 15).';
revoke execute on function direction_standing() from public, anon;
grant execute on function direction_standing() to authenticated;
