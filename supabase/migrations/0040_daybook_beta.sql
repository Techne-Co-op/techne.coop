-- 0040 · daybook beta relations (test surface, not the record)
--
-- Five relations backing the Daybook beta at journal.techne.coop, per
-- DAYBOOK_BETA.md §3. Every one carries a beta_ prefix and none of them is
-- a record class: nothing here is cited by an instrument, nothing here is
-- adopted, and the whole surface drops in one statement (see the tail of
-- this file). The record classes in public are untouched by this migration.
--
-- Why prefixed tables in public rather than a beta schema: PostgREST on
-- this project exposes db_schema = 'public,graphql_public'. A separate
-- schema would be invisible over REST until that project setting changed,
-- which restarts PostgREST on the live CIS. Row-level security is per
-- table, so the prefix costs namespace tidiness and nothing else.
--
-- Identity reuses the CIS helpers as they stand: app_agent_id() resolves
-- auth.uid() to an agents row, app_is_member() checks an active membership.
-- The beta invents no permission, which is Principle 1 of the PRD.
--
-- Applied to the live CIS via the Management API 2026-08-31.

-- The permanent citable address, assigned at append.
create sequence if not exists public.beta_event_address_seq;

-- The one growing table. No updated_at exists: rows are never edited and
-- corrections are new rows carrying the proposal they rejected.
create table if not exists public.beta_events (
  id              uuid primary key default gen_random_uuid(),
  at              timestamptz not null default now(),
  agent_id        uuid not null references public.agents(id),
  kind            text not null check (kind in (
                    'entry.written',
                    'inference.confirmed', 'inference.corrected',
                    'thread.named', 'thread.joined', 'thread.merged',
                    'thread.split', 'thread.rested',
                    'wager.sealed', 'wager.resolved',
                    'question.owned', 'question.resolved',
                    'contest.filed', 'gathering.held',
                    'demo.promised', 'demo.reported',
                    'rereading.held', 'curation.shelved')),
  body            jsonb not null default '{}'::jsonb,
  about_event_id  uuid references public.beta_events(id),
  address         text not null unique
                    default ('§' || nextval('public.beta_event_address_seq'))
);

comment on table public.beta_events is
  'Daybook beta. Append-only. Not a record class: nothing here is adopted or cited by an instrument.';
comment on column public.beta_events.address is
  'The citable §-address, assigned at append and permanent.';
comment on column public.beta_events.about_event_id is
  'Confirmation or correction points at an entry; a resolution points at a wager. The chain is the audit.';

create index if not exists beta_events_agent_at on public.beta_events (agent_id, at desc);
create index if not exists beta_events_about on public.beta_events (about_event_id);

-- mentions (event → agent) and cites (event → event address).
create table if not exists public.beta_edges (
  id          uuid primary key default gen_random_uuid(),
  from_event  uuid not null references public.beta_events(id) on delete cascade,
  rel         text not null check (rel in ('mentions', 'cites')),
  to_agent    uuid references public.agents(id),
  to_address  text,
  check ((rel = 'mentions' and to_agent is not null and to_address is null)
      or (rel = 'cites'    and to_address is not null and to_agent is null))
);

create index if not exists beta_edges_from on public.beta_edges (from_event);

-- A row exists only once a member names the thread. No state column: a
-- forming thread is not here at all.
create table if not exists public.beta_threads (
  id        text primary key,
  name      text not null,
  named_by  uuid not null references public.agents(id),
  named_at  timestamptz not null default now()
);

-- A word joins by use. Voices, counts and spread are folds, computed and
-- never assigned, so they are not columns here.
create table if not exists public.beta_terms (
  term            text primary key,
  first_event_id  uuid not null references public.beta_events(id)
);

-- D-03. A staged inference is not a record class: no address, no append
-- discipline, freely updated and deleted, and readable only by the member
-- whose session wrote it.
create table if not exists public.beta_staging (
  id              uuid primary key default gen_random_uuid(),
  agent_id        uuid not null references public.agents(id),
  at              timestamptz not null default now(),
  body            jsonb not null default '{}'::jsonb,
  about_event_id  uuid references public.beta_events(id)
);

create index if not exists beta_staging_agent on public.beta_staging (agent_id);

-- Append-only, enforced by the database rather than by convention. The
-- prototype edits an appended row in place when a forming thread is named
-- (daybook/index.html:1033); against this table that raises, which is the
-- correct outcome and a known piece of work on the client.
create or replace function public.beta_events_refuse_mutation()
returns trigger language plpgsql as $$
begin
  raise exception 'beta_events is append-only: corrections are compensating rows (DAYBOOK_BETA.md §3)';
end $$;

drop trigger if exists beta_events_no_mutation on public.beta_events;
create trigger beta_events_no_mutation
  before update or delete on public.beta_events
  for each row execute function public.beta_events_refuse_mutation();

alter table public.beta_events  enable row level security;
alter table public.beta_edges   enable row level security;
alter table public.beta_threads enable row level security;
alter table public.beta_terms   enable row level security;
alter table public.beta_staging enable row level security;

-- Members read the beta; members append under their own identity only.
drop policy if exists beta_events_member_read on public.beta_events;
-- Anchor: DAYBOOK_BETA.md §3. No bylaw governs this policy; beta_events is not a record class. Membership is the read gate, as the intranet has it.
create policy beta_events_member_read on public.beta_events
  for select using (app_is_member());

drop policy if exists beta_events_self_append on public.beta_events;
-- Anchor: DAYBOOK_BETA.md §3. Not a record class. A member appends only under their own identity; the beta invents no permission (PRD §4, Principle 1).
create policy beta_events_self_append on public.beta_events
  for insert with check (agent_id = app_agent_id() and app_is_member());

drop policy if exists beta_edges_member_read on public.beta_edges;
-- Anchor: DAYBOOK_BETA.md §3. Not a record class. Edges are readable exactly as the events they hang from.
create policy beta_edges_member_read on public.beta_edges
  for select using (app_is_member());

drop policy if exists beta_edges_self_append on public.beta_edges;
-- Anchor: DAYBOOK_BETA.md §3. Not a record class. An edge may only be hung from an event the member themselves appended.
create policy beta_edges_self_append on public.beta_edges
  for insert with check (app_is_member() and exists (
    select 1 from public.beta_events e
     where e.id = from_event and e.agent_id = app_agent_id()));

drop policy if exists beta_threads_member_read on public.beta_threads;
-- Anchor: DAYBOOK_BETA.md §3. Not a record class. A thread exists only once a member names it, and then it is common.
create policy beta_threads_member_read on public.beta_threads
  for select using (app_is_member());

drop policy if exists beta_threads_self_name on public.beta_threads;
-- Anchor: DAYBOOK_BETA.md §3. Not a record class. Naming is an act, so the namer is the member doing it.
create policy beta_threads_self_name on public.beta_threads
  for insert with check (named_by = app_agent_id() and app_is_member());

drop policy if exists beta_terms_member_read on public.beta_terms;
-- Anchor: DAYBOOK_BETA.md §3. Not a record class. A word joins the vocabulary by use, and the vocabulary is common.
create policy beta_terms_member_read on public.beta_terms
  for select using (app_is_member());

drop policy if exists beta_terms_member_append on public.beta_terms;
-- Anchor: DAYBOOK_BETA.md §3. Not a record class. Any member may bring a word in by using it.
create policy beta_terms_member_append on public.beta_terms
  for insert with check (app_is_member());

-- Staging is self only, in both directions and for every command. Another
-- member's staged inference is unqueryable, not merely unshown.
drop policy if exists beta_staging_self on public.beta_staging;
-- Anchor: DAYBOOK_DECISIONS.md D-03, and DAYBOOK_BETA.md §3. Not a record class. Self only in both directions: another member's staged inference is unqueryable, not merely unshown.
create policy beta_staging_self on public.beta_staging
  for all using (agent_id = app_agent_id())
  with check (agent_id = app_agent_id());

grant select, insert on public.beta_events  to authenticated;
grant select, insert on public.beta_edges   to authenticated;
grant select, insert on public.beta_threads to authenticated;
grant select, insert on public.beta_terms   to authenticated;
grant select, insert, update, delete on public.beta_staging to authenticated;
grant usage on sequence public.beta_event_address_seq to authenticated;

-- anon reads and writes nothing here. Signing in is the door.
revoke all on public.beta_events, public.beta_edges, public.beta_threads,
              public.beta_terms, public.beta_staging from anon;

-- The undo, in full:
--   drop table if exists public.beta_staging, public.beta_edges,
--     public.beta_terms, public.beta_events, public.beta_threads cascade;
--   drop function if exists public.beta_events_refuse_mutation();
--   drop sequence if exists public.beta_event_address_seq;
