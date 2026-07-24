-- 0011_agreements_typing.sql
-- B-07: the agreements shelf, complete and correctly typed
--
-- The shelf held one row, the Bylaws, and offered a signature on it, so the
-- Bylaws read as the member agreement a person signs. In truth the
-- Membership Agreement binds by signature and the Bylaws bind by ratification
-- and membership (Art. XVI). This migration types every agreement by how it
-- binds, adds the acknowledgement act for the documents that bind without a
-- signature, seeds the canonical set from techne.coop/legal, and holds space
-- for the policies still to come.
--
-- Decision (Todd Youngblood, 2026-07-24): Option A. Members SIGN contracts;
-- members ACKNOWLEDGE governance and policy; templates are reference and do
-- not appear on the personal shelf. Distinct acts, distinct events:
-- signature.signed (unchanged) and agreement.acknowledged (new).
--
-- Cites: IM v0.1 section 2, section 5 (agreements as versioned instruments);
-- AM v0.1 section 5 (signatures policy, mirrored for acknowledgements);
-- bylaws Art. XVI, section 1.2.9 (every member receives and reads what binds
-- them), section 2.8. Project: ujujwgopdwirebgcpekc

-- ---------- 1 - the kind of binding ----------
do $$ begin
  if not exists (select 1 from pg_type where typname = 'agreement_kind') then
    create type agreement_kind as enum ('contract','governance','policy','template');
  end if;
end $$;

alter table agreements
  add column if not exists kind agreement_kind not null default 'contract';
comment on column agreements.kind is
  'How the instrument binds: contract is signed; governance and policy are acknowledged; template is reference and stays off the personal shelf. B-07 Option A. Bylaws Art. XVI, section 2.8.';

-- ---------- 2 - the acknowledgement act ----------
-- Mirrors signatures: the lighter recorded act for a document that binds
-- without a signature. One per agent per agreement; the row is its evidence.
create table if not exists acknowledgements (
  id              uuid primary key default gen_random_uuid(),
  agent_id        uuid not null references agents(id),
  agreement_id    uuid not null references agreements(id),
  acknowledged_at timestamptz not null default now(),
  event_id        uuid references events(id),
  unique (agent_id, agreement_id)
);
comment on table acknowledgements is
  'Acknowledgement of a governance or policy instrument; the act for documents that bind without a signature. Mirrors signatures. B-07; bylaws Art. XVI, section 1.2.9.';

alter table acknowledgements enable row level security;

-- §1.2.9, §2.8: acknowledging is the member's own act; the row is its
-- evidence (§2.8), readable by the member (§1.2.9), the Board, and the officers.
create policy acknowledgements_self on acknowledgements
  for select using (agent_id = app_agent_id() or app_has_role('director') or app_is_officer());
-- §1.2.9: the member records their own acknowledgement, nobody else's.
create policy acknowledgements_self_insert on acknowledgements
  for insert with check (agent_id = app_agent_id());

-- ---------- 3 - acknowledge_agreement, the definer act ----------
-- Parallels sign_agreement (0003): resolve caller, guard kind, insert the
-- acknowledgement and its event, link them atomically. Runs as definer so the
-- event_id link is written where RLS grants the member insert only.
create or replace function public.acknowledge_agreement(p_agreement_id uuid)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_agent_id uuid;
  v_kind     agreement_kind;
  v_ack_id   uuid;
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
  if v_kind not in ('governance','policy') then
    raise exception 'acknowledgement is for governance and policy instruments; a % is signed', v_kind;
  end if;

  if exists (
    select 1 from acknowledgements
    where agent_id = v_agent_id and agreement_id = p_agreement_id
  ) then
    raise exception 'agreement already acknowledged by this agent';
  end if;

  insert into acknowledgements (agent_id, agreement_id, acknowledged_at)
  values (v_agent_id, p_agreement_id, v_now)
  returning id into v_ack_id;

  insert into events (
    occurred_at, kind, actor_agent_id, agent_id, agreement_id,
    provenance, settlement, payload
  ) values (
    v_now, 'agreement.acknowledged', v_agent_id, v_agent_id, p_agreement_id,
    'real', 'settled', jsonb_build_object('acknowledgement_id', v_ack_id)
  ) returning id into v_event_id;

  update acknowledgements set event_id = v_event_id where id = v_ack_id;

  return jsonb_build_object(
    'acknowledgement_id', v_ack_id,
    'event_id',           v_event_id,
    'acknowledged_at',    v_now
  );
end;
$$;

grant execute on function public.acknowledge_agreement(uuid) to authenticated;

-- ---------- 4 - the signature refuses the wrong kind ----------
-- sign_agreement (0003) unchanged in shape; the one addition is the kind
-- guard, so a governance or policy instrument can no longer be signed. This
-- is the correction B-07 exists for: the Bylaws are acknowledged, not signed.
create or replace function public.sign_agreement(p_agreement_id uuid)
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

  if exists (
    select 1 from signatures
    where agent_id = v_agent_id and agreement_id = p_agreement_id
  ) then
    raise exception 'agreement already signed by this agent';
  end if;

  insert into signatures (agent_id, agreement_id, signed_at)
  values (v_agent_id, p_agreement_id, v_now)
  returning id into v_sig_id;

  insert into events (
    occurred_at, kind, actor_agent_id, agent_id, agreement_id,
    provenance, settlement, payload
  ) values (
    v_now, 'signature.signed', v_agent_id, v_agent_id, p_agreement_id,
    'real', 'settled', jsonb_build_object('signature_id', v_sig_id)
  ) returning id into v_event_id;

  update signatures set event_id = v_event_id where id = v_sig_id;

  return jsonb_build_object(
    'signature_id', v_sig_id,
    'event_id',     v_event_id,
    'signed_at',    v_now
  );
end;
$$;

grant execute on function public.sign_agreement(uuid) to authenticated;

-- ---------- 5 - seed the canonical set ----------
-- Idempotent: reclassify the Bylaws row already on record, add the Membership
-- Agreement it was standing in for, and enter the rest from techne.coop/legal.
-- Values marked PROVISIONAL await the steward's confirmation before merge
-- (the legal documents carry an Effective Date placeholder and an adoption
-- month, not a semantic version). The Secretary is custodian of the record
-- (section 4.5(b)); these versions and dates are his to confirm or correct.

-- the Bylaws: governance. Bind by ratification and membership, not signature.
update agreements
   set kind = 'governance',
       uri  = 'https://techne.coop/legal/bylaws'
 where code = 'BYLAWS';

-- the Membership Agreement: the contract a member signs. PROVISIONAL v1 /
-- 2026-06-01, from "adopted June 2026" on the legal page.
insert into agreements (code, title, version, effective_date, settlement, uri, kind)
values ('MEMBER-AGMT', 'Hub Membership Agreement', 'v1', '2026-06-01', 'settled',
        'https://techne.coop/legal/membership-agreement', 'contract')
on conflict (code, version) do update
   set title = excluded.title, kind = excluded.kind, uri = excluded.uri,
       effective_date = excluded.effective_date, settlement = excluded.settlement;

-- Participation terms: policy, acknowledged. PROVISIONAL v1 / 2026-06-24,
-- from "Adopted by board resolution, June 24, 2026."
insert into agreements (code, title, version, effective_date, settlement, uri, kind)
values ('PARTICIPATION', 'Participation Terms', 'v1', '2026-06-24', 'settled',
        'https://techne.coop/legal/participation', 'policy')
on conflict (code, version) do update
   set title = excluded.title, kind = excluded.kind, uri = excluded.uri,
       effective_date = excluded.effective_date, settlement = excluded.settlement;

-- Community Supporter: template. A form for a non-member supporter, held in
-- the versioned record but off the personal shelf.
insert into agreements (code, title, version, effective_date, settlement, uri, kind)
values ('COMMUNITY-SUPPORTER', 'Community Supporter Agreement', 'v1', '2026-06-01', 'settled',
        'https://techne.coop/legal/community-supporter', 'template')
on conflict (code, version) do update
   set title = excluded.title, kind = excluded.kind, uri = excluded.uri,
       effective_date = excluded.effective_date, settlement = excluded.settlement;

-- the policies still to come: space held, acknowledged when they take effect.
-- Anticipated, no effective date; the shelf shows them as coming, no action.
insert into agreements (code, title, version, effective_date, settlement, uri, kind)
values
  ('TOS',     'Terms of Service', 'v1', null, 'anticipated', null, 'policy'),
  ('PRIVACY', 'Privacy Policy',   'v1', null, 'anticipated', null, 'policy'),
  ('CODE-OF-CONDUCT', 'Code of Conduct', 'v1', null, 'anticipated', null, 'policy')
on conflict (code, version) do update
   set title = excluded.title, kind = excluded.kind, settlement = excluded.settlement;
