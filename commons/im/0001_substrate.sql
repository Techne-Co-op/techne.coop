-- ============================================================
-- 0001_substrate.sql · emission of IM v0.1 · Drafted
-- The Common Record Series · RegenHub, LCA · July 2026
-- The document governs; this migration distills.
-- Bylaw anchors below cite the DRAFTED bylaws v2 and harden
-- at ratification (R1). RLS is ENABLED with NO POLICIES:
-- deny-by-default until the Authority Map (AM) lands.
-- Deferred by design: policies (AM), seeds (simulation rule),
-- executable invariant checks (VS), per-table exports (Law XI
-- duty, packet work). No stored balances exist anywhere.
-- ============================================================

create extension if not exists pgcrypto;

-- ---------- vocabulary ----------
create type book_kind        as enum ('entity','host');            -- Law IX
create type agent_kind       as enum ('person','cooperative','program','partner','instrument');
create type membership_state as enum ('applied','active','suspended','withdrawn','terminated','redeemed'); -- Law VI, admission subset; full FSM constants harden at R1
create type share_status     as enum ('issued','redeemed');
create type opportunity_kind as enum ('play','practice','work');
create type opportunity_state as enum ('open','resolved','withdrawn');
create type registration_state as enum ('registered','cancelled');
create type provenance_kind  as enum ('real','illustrative');      -- three-axis: authored
create type settlement_kind  as enum ('settled','anticipated','open'); -- three-axis: authored
-- temporal state is never stored: derived from the clock at read time (PRD v0.3 §5)

-- ---------- primitives: agents & agreements ----------
create table agents (
  id           uuid primary key default gen_random_uuid(),
  kind         agent_kind not null,
  display_name text not null,
  created_at   timestamptz not null default now()
);
comment on table agents is 'Identity spine; one row per participant across every relationship state. IM v0.1 §5.';

create table agreements (
  id             uuid primary key default gen_random_uuid(),
  code           text not null,                 -- e.g. BYLAWS, MEMBER-AGMT, POLICY-PATRONAGE
  title          text not null,
  version        text not null,
  effective_date date,
  settlement     settlement_kind not null default 'anticipated',
  uri            text,
  supersedes     uuid references agreements(id),
  unique (code, version)
);
comment on table agreements is 'First-class, versioned, effective-dated instruments; computations bind to the version in force. IM v0.1 §2, §5.';

-- ---------- belong ----------
create table memberships (
  id               uuid primary key default gen_random_uuid(),
  agent_id         uuid not null references agents(id),
  member_class     text,                        -- held as text: class structure Open (PRD v0.3 §11 Q4)
  state            membership_state not null default 'applied',
  entered_state_at timestamptz not null default now()
);
comment on table memberships is 'Membership relation and Law VI lifecycle state. Cites bylaws §1.1–1.4 (Drafted).';

create table stock_ledger (
  id          uuid primary key default gen_random_uuid(),
  agent_id    uuid not null references agents(id),
  share_class text not null default 'voting',
  status      share_status not null default 'issued',
  issued_at   timestamptz not null default now()
);
comment on table stock_ledger is 'Issued shares by class. Conservation: one voting share per voting member. IM v0.1 §6.';
create unique index one_voting_share_per_member
  on stock_ledger (agent_id)
  where (share_class = 'voting' and status = 'issued');

create table signatures (
  id           uuid primary key default gen_random_uuid(),
  agent_id     uuid not null references agents(id),
  agreement_id uuid not null references agreements(id),
  signed_at    timestamptz not null default now(),
  event_id     uuid                              -- the recording event; FK added after events exists
);
comment on table signatures is 'Signing is a human act; the row is its evidence. IM v0.1 §5.';

create table applications (
  id           uuid primary key default gen_random_uuid(),
  agent_id     uuid not null references agents(id),
  submitted_at timestamptz not null default now(),
  note         text
);
comment on table applications is 'Admission intake at the front of the Law VI automaton; salvaged from the Hub application form.';

-- ---------- the event log (Law I) ----------
create table events (
  id                uuid primary key default gen_random_uuid(),
  occurred_at       timestamptz not null,
  recorded_at       timestamptz not null default now(),
  actor_agent_id    uuid references agents(id),   -- who acted; human actor required where bylaws assign the act to a person
  book              book_kind not null default 'entity',
  kind              text not null,                -- e.g. membership.transition, signature.recorded, capital.contribution, opportunity.resolved
  agent_id          uuid references agents(id),   -- whom it concerns
  agreement_id      uuid references agreements(id),
  resource          text,                         -- resource designator; typed resource registry arrives with its slice
  payload           jsonb,
  prior             jsonb,                        -- prior value where a governed record changed (Law/P09)
  corrects          uuid references events(id),   -- compensating correction, never a mutation
  book_delta        numeric(14,2),                -- capital events: Law VII, both deltas even when equal
  tax_delta         numeric(14,2),
  valuation_method  text,                         -- A04: FMV at contribution; revaluation only by explicit event
  valuation_approver_agent_id uuid references agents(id),
  provenance        provenance_kind not null default 'real',
  settlement        settlement_kind not null default 'settled'
);
comment on table events is 'Single source of truth; state(t)=fold(events). Append-only, corrections compensate. IM v0.1 §4.';

alter table signatures
  add constraint signatures_event_fk foreign key (event_id) references events(id);

create or replace function events_refuse_mutation() returns trigger
language plpgsql as $$
begin
  raise exception 'events is append-only (IM v0.1 §4, Law I): corrections are compensating rows';
end $$;
create trigger events_append_only
  before update or delete on events
  for each row execute function events_refuse_mutation();

-- ---------- lifecycle legality (Law VI) ----------
create or replace function memberships_check_transition() returns trigger
language plpgsql as $$
begin
  if tg_op = 'UPDATE' and new.state is distinct from old.state then
    if not (
      (old.state = 'applied'   and new.state in ('active','withdrawn')) or
      (old.state = 'active'    and new.state in ('suspended','withdrawn','terminated')) or
      (old.state = 'suspended' and new.state in ('active','terminated')) or
      (old.state in ('withdrawn','terminated') and new.state = 'redeemed')
    ) then
      raise exception 'illegal membership transition % -> % (IM v0.1 §6, Law VI)', old.state, new.state;
    end if;
    new.entered_state_at := now();
    -- gating windows and the human-actor requirement are checked at the
    -- application layer until AM lands, then enforced by policy + event.
  end if;
  return new;
end $$;
create trigger memberships_transition
  before update on memberships
  for each row execute function memberships_check_transition();

-- ---------- gather ----------
create table gatherings (
  id            uuid primary key default gen_random_uuid(),
  title         text not null,
  host_agent_id uuid not null references agents(id),
  agreement_id  uuid references agreements(id),   -- hosted under a named agreement or policy
  created_at    timestamptz not null default now()
);
create table sessions (
  id           uuid primary key default gen_random_uuid(),
  gathering_id uuid not null references gatherings(id),
  starts_at    timestamptz not null,
  ends_at      timestamptz
);
create table registrations (
  id         uuid primary key default gen_random_uuid(),
  session_id uuid not null references sessions(id),
  agent_id   uuid not null references agents(id),
  state      registration_state not null default 'registered',
  at         timestamptz not null default now(),
  unique (session_id, agent_id)
);
create table attendance (
  id                 uuid primary key default gen_random_uuid(),
  session_id         uuid not null references sessions(id),
  agent_id           uuid not null references agents(id),
  recorded_at        timestamptz not null default now(),
  recorded_by        uuid references agents(id),
  unique (session_id, agent_id)
);
comment on table attendance is 'Presence recorded where the record counts it. Cites bylaws §2.7 (Drafted).';

-- ---------- find one another ----------
create table opportunities (
  id              uuid primary key default gen_random_uuid(),
  author_agent_id uuid not null references agents(id),
  kind            opportunity_kind not null,
  title           text not null,
  body            text,
  state           opportunity_state not null default 'open',
  opened_at       timestamptz not null default now(),
  resolved_at     timestamptz
);
comment on table opportunities is 'Governed records with an author and a lifecycle, never a ranked feed. Resolutions are events, not a table. PRD v0.3 §4, IM v0.1 §5.';
create table responses (
  id             uuid primary key default gen_random_uuid(),
  opportunity_id uuid not null references opportunities(id),
  agent_id       uuid not null references agents(id),
  at             timestamptz not null default now(),
  note           text
);

-- ---------- see your share: a view, not a table (Law VII) ----------
create view capital_accounts as
  select agent_id,
         sum(book_delta) as book_balance,
         sum(tax_delta)  as tax_balance
  from events
  where kind like 'capital.%'
  group by agent_id;
comment on view capital_accounts is 'One account per member, two projections, both folds. STUB: allocation logic blocked · Q3 (PRD v0.3 §11).';

-- ---------- visibility: enabled, denying, awaiting AM (Law V) ----------
alter table agents        enable row level security;
alter table agreements    enable row level security;
alter table memberships   enable row level security;
alter table stock_ledger  enable row level security;
alter table signatures    enable row level security;
alter table applications  enable row level security;
alter table events        enable row level security;
alter table gatherings    enable row level security;
alter table sessions      enable row level security;
alter table registrations enable row level security;
alter table attendance    enable row level security;
alter table opportunities enable row level security;
alter table responses     enable row level security;
-- no policies in this migration: deny-by-default is the honest
-- posture until the Authority Map cites its bylaw anchors (AM v0.1).
