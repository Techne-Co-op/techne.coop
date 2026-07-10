-- ============================================================
-- 0002_policies.sql · emission of AM v0.1 · Drafted
-- The Common Record Series · RegenHub, LCA · July 2026
-- The document governs; this migration distills. Applying it
-- flips rls-audit from deny-all to the AM v0.1 §5 matrix.
-- Anchors cite Bylaws v2.1 as published at
-- techne.coop/legal/bylaws; the status discrepancy between the
-- instrument (Ratified July 2026) and the legal index (Drafted)
-- is filed at AM v0.1 §1a and does not alter these citations.
-- Tax identifiers appear in NO table and NO policy (§1.13;
-- AM v0.1 §4). The instrument (Nou) holds no role and no grant.
-- ============================================================

-- ---------- IM v0.2 addenda, carried openly (AM v0.1 §9) ----------
-- Identity binding: the visibility function must know who asks.
comment on table agents is 'Identity spine; one row per participant across every relationship state. IM v0.1 §5; auth binding per AM v0.1 §9.';
alter table agents add column auth_user_id uuid unique;

-- Appointments: classes live on memberships (§1.1); offices do not.
-- Grounds: director §3.1; secretary §4.5; treasurer §4.4; steward
-- §4.1 and §1.13 (delegating Board resolution: Anticipated).
create type appointment as enum ('director','secretary','treasurer','steward');
create table role_grants (
  id         uuid primary key default gen_random_uuid(),
  agent_id   uuid not null references agents(id),
  role       appointment not null,
  granted_at timestamptz not null default now(),
  revoked_at timestamptz,
  event_id   uuid references events(id)   -- the recording event; grants are event-based
);
comment on table role_grants is 'Board appointments per Bylaws §3.1, §4.1, §4.4, §4.5; authority is event-based and time-bound (AM v0.1 §3, §9).';
alter table role_grants enable row level security;

-- ---------- helpers (security definer, stable) ----------
create or replace function app_agent_id() returns uuid
language sql stable security definer set search_path = public as $$
  select id from agents where auth_user_id = auth.uid()
$$;

create or replace function app_is_member() returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from memberships m
    where m.agent_id = app_agent_id() and m.state = 'active')
$$;

create or replace function app_is_applicant() returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from memberships m
    where m.agent_id = app_agent_id() and m.state = 'applied')
$$;

create or replace function app_has_role(r appointment) returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from role_grants g
    where g.agent_id = app_agent_id() and g.role = r and g.revoked_at is null)
$$;

create or replace function app_is_officer() returns boolean
language sql stable security definer as $$
  select app_has_role('secretary') or app_has_role('treasurer')
$$;

create or replace function app_is_overseer() returns boolean
language sql stable security definer as $$
  select app_has_role('director') or app_is_officer() or app_has_role('steward')
$$;

-- ---------- role_grants ----------
-- §3.1, §4.1: the Board manages; grants are read by members
-- (offices are public inside the cooperative) and written by directors.
create policy role_grants_member_read on role_grants
  for select using (app_is_member() or agent_id = app_agent_id());
-- §3.8: the Board elects officers; recording the grant is a directorial write.
create policy role_grants_director_write on role_grants
  for all using (app_has_role('director')) with check (app_has_role('director'));

-- ---------- agents ----------
-- §2.9: the membership list is a member right, electronic on request.
create policy agents_member_read on agents
  for select using (app_is_member() or app_is_overseer() or id = app_agent_id());
-- §1.13: each member keeps their own record current; self-update of display.
create policy agents_self_update on agents
  for update using (id = app_agent_id()) with check (id = app_agent_id());

-- ---------- agreements ----------
-- Art. XVI: every member receives the bylaws and amendments;
-- §1.2.9: the duty to abide presumes the right to read. Applicants
-- read what they would sign (§1.3.1(d)).
create policy agreements_read on agreements
  for select using (app_is_member() or app_is_applicant() or app_is_overseer());
-- §4.5(b): the Secretary is custodian of the corporate records.
create policy agreements_officer_write on agreements
  for all using (app_is_officer()) with check (app_is_officer());

-- ---------- memberships ----------
-- §2.9 list right; §18.1 own record.
create policy memberships_read on memberships
  for select using (app_is_member() or app_is_overseer() or agent_id = app_agent_id());
-- §1.3, §1.7, §1.8: admission, withdrawal, suspension, termination are
-- acts of the Board and its authorized steward; the automaton trigger
-- enforces legality regardless of writer (IM v0.1 §6).
create policy memberships_write on memberships
  for all using (app_has_role('director') or app_has_role('steward'))
  with check (app_has_role('director') or app_has_role('steward'));

-- ---------- stock_ledger ----------
-- §1.11 one vote; §1.6 transfer restrictions; holder and Board read.
create policy stock_self_read on stock_ledger
  for select using (agent_id = app_agent_id() or app_has_role('director') or app_is_officer());
-- §4.5(e): the Secretary keeps the stock transfer books.
create policy stock_secretary_write on stock_ledger
  for all using (app_has_role('secretary')) with check (app_has_role('secretary'));

-- ---------- signatures ----------
-- §1.3.1(d), §2.8: signing is the signer's act; the row is its evidence.
create policy signatures_self on signatures
  for select using (agent_id = app_agent_id() or app_has_role('director') or app_is_officer());
create policy signatures_self_insert on signatures
  for insert with check (agent_id = app_agent_id());

-- ---------- applications ----------
-- §1.2, §1.3: applicants write their application; the steward manages
-- intake; the Board decides admission.
create policy applications_read on applications
  for select using (agent_id = app_agent_id() or app_is_overseer());
create policy applications_self_insert on applications
  for insert with check (agent_id = app_agent_id());
create policy applications_steward_write on applications
  for update using (app_has_role('steward') or app_has_role('director'))
  with check (app_has_role('steward') or app_has_role('director'));

-- ---------- events (the log) ----------
-- §18.1, §6.2.1: an agent reads what concerns them, capital included;
-- §3.1, §4.4: the Board and Treasurer read all, for the decisions and
-- custody the instrument assigns them.
create policy events_read on events
  for select using (
    agent_id = app_agent_id()
    or actor_agent_id = app_agent_id()
    or app_has_role('director') or app_is_officer()
  );
-- Member-actionable kinds only; every other write path is a definer
-- function or an overseer act. Laws II and X; AM v0.1 §7.
create policy events_scoped_insert on events
  for insert with check (
    (actor_agent_id = app_agent_id()
      and kind ~ '^(signature|registration|opportunity|gathering)\.')
    or app_is_overseer()
  );

-- ---------- gatherings & sessions ----------
-- §2.1: meetings and community happenings; members see the calendar,
-- hosts and the steward keep it.
create policy gatherings_member_read on gatherings
  for select using (app_is_member() or app_is_overseer());
create policy gatherings_host_write on gatherings
  for all using (host_agent_id = app_agent_id() or app_has_role('steward'))
  with check (host_agent_id = app_agent_id() or app_has_role('steward'));
create policy sessions_member_read on sessions
  for select using (app_is_member() or app_is_overseer());
create policy sessions_host_write on sessions
  for all using (
    app_has_role('steward') or exists (select 1 from gatherings g
      where g.id = gathering_id and g.host_agent_id = app_agent_id()))
  with check (
    app_has_role('steward') or exists (select 1 from gatherings g
      where g.id = gathering_id and g.host_agent_id = app_agent_id()));

-- ---------- registrations ----------
-- PRD v0.3 §4 Gather: register and cancel without asking anyone.
create policy registrations_scoped on registrations
  for select using (
    agent_id = app_agent_id() or app_is_overseer()
    or exists (select 1 from sessions s join gatherings g on g.id = s.gathering_id
               where s.id = session_id and g.host_agent_id = app_agent_id()));
create policy registrations_self_write on registrations
  for insert with check (agent_id = app_agent_id() and app_is_member());
create policy registrations_self_update on registrations
  for update using (agent_id = app_agent_id()) with check (agent_id = app_agent_id());

-- ---------- attendance ----------
-- §2.7: presence serves quorum; recorded by host or steward, read by self.
create policy attendance_scoped_read on attendance
  for select using (agent_id = app_agent_id() or app_is_overseer()
    or exists (select 1 from sessions s join gatherings g on g.id = s.gathering_id
               where s.id = session_id and g.host_agent_id = app_agent_id()));
create policy attendance_recorder_write on attendance
  for insert with check (
    app_has_role('steward') or exists (select 1 from sessions s join gatherings g on g.id = s.gathering_id
               where s.id = session_id and g.host_agent_id = app_agent_id()));

-- ---------- opportunities & responses ----------
-- PRD v0.3 §4 Find: governed records with an author and a lifecycle.
create policy opportunities_member_read on opportunities
  for select using (app_is_member() or app_is_overseer());
create policy opportunities_author_write on opportunities
  for all using (author_agent_id = app_agent_id())
  with check (author_agent_id = app_agent_id() and app_is_member());
-- §18.2 sensibility: a response is between responder and author.
create policy responses_scoped_read on responses
  for select using (
    agent_id = app_agent_id() or app_is_overseer()
    or exists (select 1 from opportunities o
               where o.id = opportunity_id and o.author_agent_id = app_agent_id()));
create policy responses_self_insert on responses
  for insert with check (agent_id = app_agent_id() and app_is_member());

-- ---------- grants: the matrix rides on authenticated ----------
grant usage on schema public to authenticated;
grant select, insert, update on all tables in schema public to authenticated;
grant select on capital_accounts to authenticated;
-- anon receives nothing: the public surface is the website
-- (Art. XV; the legal page), not an anonymous database role.
