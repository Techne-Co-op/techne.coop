-- 0003_sign_agreement.sql
-- B-04 escalation resolution: atomic signature capture
--
-- Replaces the three-step browser flow (INSERT signatures, INSERT events,
-- PATCH signatures.event_id) with a single SECURITY DEFINER function.
-- The PATCH step was blocked by RLS — signatures_self covers SELECT and
-- INSERT only, no UPDATE. This function runs as the definer and links
-- event_id atomically, eliminating the partial-write failure mode.
--
-- Cites: AM v0.1 §5 (signatures policy), IM §4 (events), bylaws Art. XVI
-- Applied: 2026-07-12  Project: ujujwgopdwirebgcpekc (techne-coop-cis)

create or replace function public.sign_agreement(p_agreement_id uuid)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_agent_id  uuid;
  v_sig_id    uuid;
  v_event_id  uuid;
  v_now       timestamptz := now();
begin
  -- resolve calling agent
  v_agent_id := app_agent_id();
  if v_agent_id is null then
    raise exception 'not authenticated as a known agent';
  end if;

  -- guard: agreement must exist
  if not exists (select 1 from agreements where id = p_agreement_id) then
    raise exception 'agreement not found: %', p_agreement_id;
  end if;

  -- guard: idempotent — do not double-sign
  if exists (
    select 1 from signatures
    where agent_id = v_agent_id and agreement_id = p_agreement_id
  ) then
    raise exception 'agreement already signed by this agent';
  end if;

  -- 1. insert signature
  insert into signatures (agent_id, agreement_id, signed_at)
  values (v_agent_id, p_agreement_id, v_now)
  returning id into v_sig_id;

  -- 2. insert event
  insert into events (
    occurred_at, kind,
    actor_agent_id, agent_id, agreement_id,
    provenance, settlement, payload
  ) values (
    v_now, 'signature.signed',
    v_agent_id, v_agent_id, p_agreement_id,
    'real', 'settled',
    jsonb_build_object('signature_id', v_sig_id)
  ) returning id into v_event_id;

  -- 3. link event back to signature (requires definer privilege — UPDATE not in RLS)
  update signatures
  set event_id = v_event_id
  where id = v_sig_id;

  return jsonb_build_object(
    'signature_id', v_sig_id,
    'event_id',     v_event_id,
    'signed_at',    v_now
  );
end;
$$;

grant execute on function public.sign_agreement(uuid) to authenticated;
