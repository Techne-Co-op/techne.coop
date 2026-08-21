-- 0025_agreement_comments_and_dated_signing.sql
-- B-08: comment and countersign
--
-- The agreements bed could hold an instrument and record that a member had
-- signed it. It could not hold what anyone said about the instrument before
-- signing, and it could not record the date a signer attested to, only the
-- timestamp the row was written. Both gaps show as soon as an agreement is
-- negotiated rather than adopted: a statement of work travels between parties,
-- collects remarks, and is executed on a date the parties name.
--
-- This migration adds the two acts.
--
--   1. Commenting. A recorded remark on a versioned instrument, by a person,
--      addressable in reply, never edited and never deleted. Withdrawal is a
--      compensating act, in keeping with Law I (the record corrects, it does
--      not mutate).
--   2. Dated signing. The signature keeps signed_at as the moment the record
--      was written and gains signed_on, the date the signer attests to, plus
--      the capacity in which they sign. The two are distinct facts and the
--      record should not conflate them.
--
-- Cites: IM v0.1 section 2, section 4, section 5 (agreements as versioned
-- instruments; events; signing is a human act and the row is its evidence);
-- AM v0.1 section 5 (signatures policy, mirrored here); 0003_sign_agreement
-- (the definer pattern); 0011_agreements_typing (agreement_kind, the
-- acknowledgement act, and the guard that a signature is for a contract).
--
-- STATUS: DRAFTED. Not applied. Schema is a stop-card matter under BP, and no
-- live schema change is made here without a named human. Project when adopted:
-- ujujwgopdwirebgcpekc (techne-coop-cis).

-- ---------- 1 - dated signing ----------
-- signed_at is when the record was written. signed_on is the date the signer
-- attests to. For a member signing in the browser they are the same day; for a
-- countersigned instrument that arrives executed, they are not, and the
-- difference is the whole point of holding both.
alter table signatures
  add column if not exists signed_on date;
comment on column signatures.signed_on is
  'The date the signer attests to, distinct from signed_at, which is when the record was written. Null means the two are the same and signed_at governs. B-08.';

alter table signatures
  add column if not exists capacity text;
comment on column signatures.capacity is
  'The capacity in which the signer signs: member, officer, director, or a named counterparty role. Held as text; no role registry is asserted here. B-08.';

-- signed_on may not run ahead of the record. Held at the definer function
-- rather than as a check constraint: the comparison needs a time zone, and a
-- time zone conversion is stable, not immutable, so Postgres refuses it in a
-- check. The guard lives in sign_agreement below, which is the only granted
-- write path.

-- ---------- 2 - the comment ----------
-- One remark on one version of one instrument. in_reply_to threads a remark to
-- an earlier one on the same agreement; the trigger below enforces that. body
-- is never updated: RLS grants select and insert only, and there is no update
-- policy, matching signatures and acknowledgements.
create table if not exists agreement_comments (
  id            uuid primary key default gen_random_uuid(),
  agreement_id  uuid not null references agreements(id),
  agent_id      uuid not null references agents(id),
  in_reply_to   uuid references agreement_comments(id),
  body          text not null check (length(btrim(body)) between 1 and 8000),
  created_at    timestamptz not null default now(),
  withdraws     uuid references agreement_comments(id),
  event_id      uuid references events(id)
);
comment on table agreement_comments is
  'A recorded remark on a versioned instrument. Never edited, never deleted; a withdrawal is a new row citing the one it withdraws, per Law I. B-08.';
comment on column agreement_comments.withdraws is
  'Set on a withdrawal row, naming the remark it retires. The original stays on the record. B-08.';

create index if not exists agreement_comments_by_agreement
  on agreement_comments (agreement_id, created_at);

-- a reply and a withdrawal both stay on the instrument they were made on.
create or replace function public.agreement_comment_same_instrument()
returns trigger
language plpgsql
as $$
declare
  v_parent uuid;
begin
  foreach v_parent in array array[new.in_reply_to, new.withdraws] loop
    if v_parent is not null then
      if not exists (
        select 1 from agreement_comments
        where id = v_parent and agreement_id = new.agreement_id
      ) then
        raise exception 'cited comment % is not on agreement %', v_parent, new.agreement_id;
      end if;
    end if;
  end loop;
  return new;
end;
$$;

drop trigger if exists agreement_comments_same_instrument on agreement_comments;
create trigger agreement_comments_same_instrument
  before insert on agreement_comments
  for each row execute function public.agreement_comment_same_instrument();

alter table agreement_comments enable row level security;

-- Who reads a remark. The bed is the members' own reading room: a remark on an
-- instrument is readable by every active member, because every member is
-- entitled to read what binds them and what was said about it before it bound
-- them (bylaws section 1.2.9). Directors and officers read regardless of
-- membership state.
-- §1.2.9, §2.8: a member reads what binds them and what was said about it; the
-- row is its own evidence. Art. XVI.
create policy agreement_comments_read on agreement_comments
  for select using (
    app_has_role('director')
    or app_is_officer()
    or exists (
      select 1 from memberships m
      where m.agent_id = app_agent_id() and m.state = 'active'
    )
  );

-- Who writes one. A member speaks in their own name and nobody else's.
-- §1.2.9: the member records their own remark, nobody else's. Art. XVI.
create policy agreement_comments_self_insert on agreement_comments
  for insert with check (agent_id = app_agent_id());

-- ---------- 3 - comment_on_agreement, the definer act ----------
-- Parallels sign_agreement (0003) and acknowledge_agreement (0011): resolve the
-- caller, guard the citations, write the remark and its event, link them
-- atomically. Definer because the event_id link is an update, and RLS grants
-- the member insert only.
create or replace function public.comment_on_agreement(
  p_agreement_id uuid,
  p_body         text,
  p_in_reply_to  uuid default null,
  p_withdraws    uuid default null
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_agent_id   uuid;
  v_comment_id uuid;
  v_event_id   uuid;
  v_now        timestamptz := now();
begin
  v_agent_id := app_agent_id();
  if v_agent_id is null then
    raise exception 'not authenticated as a known agent';
  end if;

  if not exists (select 1 from agreements where id = p_agreement_id) then
    raise exception 'agreement not found: %', p_agreement_id;
  end if;

  -- a withdrawal retires your own remark, not somebody else's.
  if p_withdraws is not null then
    if not exists (
      select 1 from agreement_comments
      where id = p_withdraws and agent_id = v_agent_id
    ) then
      raise exception 'a remark may only be withdrawn by the person who made it';
    end if;
    if exists (select 1 from agreement_comments where withdraws = p_withdraws) then
      raise exception 'remark % is already withdrawn', p_withdraws;
    end if;
  end if;

  insert into agreement_comments
    (agreement_id, agent_id, in_reply_to, withdraws, body, created_at)
  values
    (p_agreement_id, v_agent_id, p_in_reply_to, p_withdraws, p_body, v_now)
  returning id into v_comment_id;

  insert into events (
    occurred_at, kind, actor_agent_id, agent_id, agreement_id,
    provenance, settlement, payload
  ) values (
    v_now,
    case when p_withdraws is null then 'agreement.commented' else 'agreement.comment_withdrawn' end,
    v_agent_id, v_agent_id, p_agreement_id,
    'real', 'settled',
    jsonb_build_object(
      'comment_id',  v_comment_id,
      'in_reply_to', p_in_reply_to,
      'withdraws',   p_withdraws
    )
  ) returning id into v_event_id;

  update agreement_comments set event_id = v_event_id where id = v_comment_id;

  return jsonb_build_object(
    'comment_id', v_comment_id,
    'event_id',   v_event_id,
    'created_at', v_now
  );
end;
$$;

grant execute on function public.comment_on_agreement(uuid, text, uuid, uuid) to authenticated;

-- ---------- 4 - sign_agreement carries the date and the capacity ----------
-- Shape unchanged from 0011: resolve the caller, guard the kind, refuse a
-- second signature, write the signature and its event, link them. The two new
-- parameters default to null, so every existing caller keeps working and gets
-- the previous behaviour exactly.
create or replace function public.sign_agreement(
  p_agreement_id uuid,
  p_signed_on    date default null,
  p_capacity     text default null
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_agent_id uuid;
  v_kind     agreement_kind;
  v_sig_id   uuid;
  v_event_id uuid;
  v_now      timestamptz := now();
begin
  v_agent_id := app_agent_id();
  if v_agent_id is null then
    raise exception 'not authenticated as a known agent';
  end if;

  select kind into v_kind from agreements where id = p_agreement_id;
  if v_kind is null then
    raise exception 'agreement not found: %', p_agreement_id;
  end if;
  if v_kind <> 'contract' then
    raise exception 'a signature is for a contract; a % is acknowledged', v_kind;
  end if;

  if p_signed_on is not null and p_signed_on > (v_now at time zone 'UTC')::date then
    raise exception 'a signature may not be dated ahead of the record';
  end if;

  if exists (
    select 1 from signatures
    where agent_id = v_agent_id and agreement_id = p_agreement_id
  ) then
    raise exception 'agreement already signed by this agent';
  end if;

  insert into signatures (agent_id, agreement_id, signed_at, signed_on, capacity)
  values (v_agent_id, p_agreement_id, v_now, p_signed_on, p_capacity)
  returning id into v_sig_id;

  insert into events (
    occurred_at, kind, actor_agent_id, agent_id, agreement_id,
    provenance, settlement, payload
  ) values (
    v_now, 'signature.signed', v_agent_id, v_agent_id, p_agreement_id,
    'real', 'settled',
    jsonb_build_object(
      'signature_id', v_sig_id,
      'signed_on',    p_signed_on,
      'capacity',     p_capacity
    )
  ) returning id into v_event_id;

  update signatures set event_id = v_event_id where id = v_sig_id;

  return jsonb_build_object(
    'signature_id', v_sig_id,
    'event_id',     v_event_id,
    'signed_at',    v_now,
    'signed_on',    coalesce(p_signed_on, (v_now at time zone 'UTC')::date),
    'capacity',     p_capacity
  );
end;
$$;

grant execute on function public.sign_agreement(uuid, date, text) to authenticated;

-- ---------- 5 - the statement of work enters the shelf ----------
-- SOW-2 with Gitcoin: a sponsorship the cooperative would hold as a program,
-- drafted 2026-08-19 and not yet presented to the counterparty. It enters the
-- record as an anticipated contract so that it can be read and commented on by
-- members before it travels, and signed with a date when it is executed.
--
-- Revised to v0.3-draft on 2026-08-21: the draft carried into the cooperatives
-- channel that morning by ClaudeJi, naming a $35,000 sponsorship redirected
-- from the Cooperation Games budget, three workstreams, and a program hold of
-- 10 to 20 percent. Still unpresented: the named recipients, Kevin, Matilda
-- and Julia, have not seen this version.
--
-- Deliberately no uri and no body text: the terms are unpresented and the
-- estate is public. The row names the instrument and its standing. The text
-- follows when the counterparty has seen it and the steward says it may.
-- This migration is unapplied, so the version moves in place rather than
-- adding a second row; once applied, a revision is a new insert.
insert into agreements (code, title, version, effective_date, settlement, uri, kind)
values ('SOW-GITCOIN-2',
        'Statement of Work 2, Gitcoin sponsorship',
        'v0.3-draft', null, 'anticipated', null, 'contract')
on conflict (code, version) do update
   set title = excluded.title, kind = excluded.kind,
       settlement = excluded.settlement;
