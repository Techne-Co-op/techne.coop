-- 0030_program_revenue.sql · T-08 · the program revenue registry
--
-- Not applied. Drafted at the steward's direction of 2026-08-26 (the
-- MRR dashboard ask, LCA finance thread). Applying it to the live CIS
-- is a schema act and a stop card under BP: it needs a named human.
-- The agent that drafted this file did not run it anywhere.
--
-- WHAT THIS IS, and what it is not
--
--   The cooperative's recurring revenue lives in several systems at
--   once: regenhub.xyz subscriptions in the member system Aaron is
--   building, legacy members paying by hand or by crypto outside any
--   system, the maker node outside both, and techne.coop dues once the
--   dues schedule records. A recurring-revenue figure that flattens
--   those into one number destroys the distinction the figure exists
--   to steer by: migration into a system is not growth, and an
--   attested number is not a read.
--
--   So this migration gives each Program a registry of NAMED
--   SUBSCRIPTION TIERS, and beside it a store of READINGS: how many
--   subscriptions stood active on a tier, at what monthly price, read
--   from which system, at what time, on what basis. Recurring revenue
--   is then a fold over the latest reading per live tier, and every
--   line of the fold keeps its provenance.
--
--   In TREASURY §9's own grammar: a reading is an outside observation,
--   not a fact in the log. It is neither a movement nor a meaning, so
--   nothing here writes to events except the two registry acts, which
--   are acts of declaration, not of money. No money moves through this
--   schema; no balance is stored anywhere in it (IM Law VII); Xero
--   remains the book of account and the record remains the ledger.
--   The CIS holds the registry and the mapping. It does not become a
--   second book beside the book.
--
--   A tier belongs to a Program, and a Program is an agents row with
--   kind='program' (0001 Law I; 0012). PATRONAGE §10's rule stands
--   unmoved: no capital or allocation verb arrives here, and the
--   tiers' prices are offers, not obligations; the obligation grammar
--   waits on the dues schedule instrument (T-02, T-07 standing).
--
-- Anchors: TREASURY §9, §9a; IM v0.1 Laws I, IV, VII, X; Bylaws v2.1
-- §18.1 as carried by 0002 (the member's standing right to read the
-- record their membership concerns); Bylaws §3.1 and §4.1 (the Board
-- manages; officers act) as the overseer guard for the registry acts.

-- ============================================================
-- §1 · the registry: named tiers, offered by Programs
-- ============================================================

create table if not exists revenue_tiers (
  id                uuid primary key default gen_random_uuid(),
  program_agent_id  uuid not null references agents(id),
  name              text not null,
  monthly_usd       numeric(14,2) not null check (monthly_usd >= 0),
  source            text not null,
  offered_at        timestamptz not null default now(),
  retired_at        timestamptz,
  note              text
);

comment on table revenue_tiers is
  'T-08: named monthly subscription tiers offered by Programs. A registry of offers, never of obligations; prices, never balances (IM Law VII). The dues schedule instrument, when it records, is what makes expectation computable.';
comment on column revenue_tiers.source is
  'The system of record for subscriptions on this tier: regenhub.xyz, stripe, or attested when no system holds them and a named human vouches the count. Free text naming the seam, so a reading can be checked against the thing it read.';
comment on column revenue_tiers.retired_at is
  'A retired tier leaves the fold but keeps its rows; history is not editable (IM Law I).';

-- One live tier name per Program. Partial, so retired history
-- accumulates freely under reused names.
create unique index revenue_tiers_live_name
  on revenue_tiers (program_agent_id, lower(name))
  where retired_at is null;

-- ============================================================
-- §2 · the readings: observations beside the record
-- ============================================================

create table if not exists revenue_readings (
  id            uuid primary key default gen_random_uuid(),
  tier_id       uuid not null references revenue_tiers(id),
  active_count  integer not null check (active_count >= 0),
  mrr_usd       numeric(14,2) not null check (mrr_usd >= 0),
  basis         text not null check (basis in ('live', 'attested')),
  source        text not null,
  read_at       timestamptz not null default now(),
  runner        text,
  note          text
);

comment on table revenue_readings is
  'T-08: subscription counts as read, at a time, from a source, on a basis. live means a system reported it through a seam; attested means a named human vouched it and the note says who. Observations beside the record, never events (TREASURY §9). Rows accumulate; the dashboard folds the latest per tier.';
comment on column revenue_readings.mrr_usd is
  'The monthly recurring figure this reading contributes, normally active_count times the tier price at read time. Carried explicitly rather than recomputed so a proration or discount a source reports survives verbatim.';

create index revenue_readings_tier_read
  on revenue_readings (tier_id, read_at desc);

-- ============================================================
-- §3 · row security, and the creation defaults stripped first
-- ============================================================
-- Supabase grants anon and authenticated every table privilege at
-- creation. 0026 and 0028 left those defaults in place and 0029 had
-- to strip them later; this migration strips them at birth, exactly
-- as 0009 did for profiles, so the grants under the policies are
-- never wider than the policies.

revoke all on revenue_tiers from anon, authenticated;
revoke all on revenue_readings from anon, authenticated;

alter table revenue_tiers enable row level security;
alter table revenue_readings enable row level security;

grant select on revenue_tiers to authenticated;
grant select on revenue_readings to authenticated;

-- The member cut: every authenticated member reads the registry and
-- the readings. Tier lines are organization aggregates; no member
-- name, id, or per-member amount exists in either table, which is the
-- §9a visibility default the statements store already stages.
-- Bylaws v2.1 §18.1: the member's standing right to read the record.
create policy revenue_tiers_member_read
  on revenue_tiers for select
  to authenticated
  using (true);

-- Bylaws v2.1 §18.1, the same member cut as the registry above.
create policy revenue_readings_member_read
  on revenue_readings for select
  to authenticated
  using (true);

-- No client insert, update, or delete policy exists on either table.
-- The registry moves only through the two definer acts below; the
-- readings enter only by the management channel under the steward's
-- custody, the 0019 shape (IM Law X: the instrument holds no grant
-- and the browser holds no pen).

-- ============================================================
-- §4 · the registry acts
-- ============================================================

-- ---------- declaring a tier ----------
create or replace function declare_revenue_tier(
  p_program uuid,
  p_name text,
  p_monthly_usd numeric,
  p_source text,
  p_note text default null
)
returns uuid
language plpgsql security definer set search_path = public as $$
declare
  v_actor uuid := app_agent_id();
  v_name  text := nullif(btrim(p_name), '');
  v_src   text := nullif(btrim(p_source), '');
  v_tier  uuid;
begin
  if v_actor is null then
    raise exception 'Sign in first: no agent is bound to this session (B-01).';
  end if;

  -- Declaring what a Program offers is a governing act, not a member
  -- courtesy (Bylaws sections 3.1 and 4.1, the 0012 shape).
  if not app_is_overseer() then
    raise exception 'Declaring a tier is a steward or director act (Bylaws sections 3.1 and 4.1).';
  end if;

  if not exists (select 1 from agents where id = p_program and kind = 'program') then
    raise exception 'No Program stands under that id; designate it first (0012).';
  end if;
  if v_name is null then
    raise exception 'A tier needs a name.';
  end if;
  if p_monthly_usd is null or p_monthly_usd < 0 then
    raise exception 'A tier needs a monthly price of zero or more.';
  end if;
  if v_src is null then
    raise exception 'A tier needs a source: the system of record its subscriptions live in, or attested.';
  end if;

  insert into revenue_tiers (program_agent_id, name, monthly_usd, source, note)
  values (p_program, v_name, p_monthly_usd, v_src, nullif(btrim(p_note), ''))
  returning id into v_tier;

  insert into events (occurred_at, actor_agent_id, kind, agent_id, payload)
  values (
    now(), v_actor, 'revenue.tier_declared', p_program,
    jsonb_build_object('tier_id', v_tier, 'name', v_name,
                       'monthly_usd', p_monthly_usd, 'source', v_src)
  );

  return v_tier;
end $$;
comment on function declare_revenue_tier(uuid, text, numeric, text, text) is
  'T-08: a Program declares a named monthly subscription tier, by a steward or director act. The row and the revenue.tier_declared event arrive together. An offer, never an obligation; no money moves.';
revoke execute on function declare_revenue_tier(uuid, text, numeric, text, text) from public, anon;
grant execute on function declare_revenue_tier(uuid, text, numeric, text, text) to authenticated;

-- ---------- retiring a tier ----------
create or replace function retire_revenue_tier(p_tier uuid)
returns uuid
language plpgsql security definer set search_path = public as $$
declare
  v_actor uuid := app_agent_id();
  v_program uuid;
begin
  if v_actor is null then
    raise exception 'Sign in first: no agent is bound to this session (B-01).';
  end if;
  if not app_is_overseer() then
    raise exception 'Retiring a tier is a steward or director act (Bylaws sections 3.1 and 4.1).';
  end if;

  update revenue_tiers
     set retired_at = now()
   where id = p_tier and retired_at is null
  returning program_agent_id into v_program;
  if v_program is null then
    raise exception 'No live tier stands under that id.';
  end if;

  insert into events (occurred_at, actor_agent_id, kind, agent_id, payload)
  values (now(), v_actor, 'revenue.tier_retired', v_program,
          jsonb_build_object('tier_id', p_tier));

  return p_tier;
end $$;
comment on function retire_revenue_tier(uuid) is
  'T-08: a tier leaves the live fold by a steward or director act; its rows and readings remain (IM Law I).';
revoke execute on function retire_revenue_tier(uuid) from public, anon;
grant execute on function retire_revenue_tier(uuid) to authenticated;

-- ============================================================
-- §5 · the dashboard fold
-- ============================================================
-- Security invoker on purpose: both tables are already member-readable
-- under the policies above, so the fold claims no authority the reader
-- lacks. It exists so the surface asks one question, not three.

create or replace function revenue_dashboard()
returns table (
  program_agent_id uuid,
  program_name     text,
  tier_id          uuid,
  tier_name        text,
  monthly_usd      numeric,
  tier_source      text,
  active_count     integer,
  mrr_usd          numeric,
  basis            text,
  reading_source   text,
  read_at          timestamptz
)
language sql stable set search_path = public as $$
  select
    t.program_agent_id,
    a.display_name,
    t.id,
    t.name,
    t.monthly_usd,
    t.source,
    r.active_count,
    r.mrr_usd,
    r.basis,
    r.source,
    r.read_at
  from revenue_tiers t
  join agents a on a.id = t.program_agent_id
  left join lateral (
    select rr.active_count, rr.mrr_usd, rr.basis, rr.source, rr.read_at
    from revenue_readings rr
    where rr.tier_id = t.id
    order by rr.read_at desc
    limit 1
  ) r on true
  where t.retired_at is null
  order by a.display_name, t.name;
$$;
comment on function revenue_dashboard() is
  'T-08: the latest reading per live tier, one row each, with its price, basis, source, and read time. The recurring-revenue figure is the sum of mrr_usd over these rows, and every line keeps the provenance the sum would otherwise destroy.';
revoke execute on function revenue_dashboard() from public, anon;
grant execute on function revenue_dashboard() to authenticated;

-- ---------- the trend fold ----------
-- Month by month, the sum of each tier's last reading within that
-- month. A month with no reading on a tier carries that tier at zero
-- rather than at its last known value, so the strip never invents
-- persistence a source did not report.
create or replace function revenue_trend()
returns table (
  month    text,
  mrr_usd  numeric
)
language sql stable set search_path = public as $$
  with monthly as (
    select
      rr.tier_id,
      to_char(date_trunc('month', rr.read_at), 'YYYY-MM') as month,
      rr.mrr_usd,
      row_number() over (
        partition by rr.tier_id, date_trunc('month', rr.read_at)
        order by rr.read_at desc
      ) as rn
    from revenue_readings rr
  )
  select month, sum(mrr_usd)
  from monthly
  where rn = 1
  group by month
  order by month;
$$;
comment on function revenue_trend() is
  'T-08: recurring revenue by month, the last reading per tier within each month summed. Absent readings count zero; the strip reports reads, never extrapolations.';
revoke execute on function revenue_trend() from public, anon;
grant execute on function revenue_trend() to authenticated;
