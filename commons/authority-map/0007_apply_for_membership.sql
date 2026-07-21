-- 0007_apply_for_membership.sql
-- X-09 escalation resolution: restore completeness for the front door
--
-- apply_for_membership(), the SECURITY DEFINER function B-02 built,
-- existed only in the live CIS — never captured as a migration file.
-- sign_agreement() was captured (0003); this one was not. A
-- walkaway-restored database would carry the tables and the fold but
-- not the front door. Per the card's adopted default, the source below
-- is the live definition, exported verbatim via
--   select pg_get_functiondef(oid) from pg_proc
--   where proname = 'apply_for_membership';
-- Faithful by construction. Reconstruction from the B-02 resolution
-- is the fallback if the live source is ever lost, which is exactly
-- the condition this file exists to prevent.
--
-- One atomic act: agent, application, membership in applied state,
-- and the recording event, whose payload carries the applicant email
-- for the X-02 notices rail.
--
-- Cites: Bylaws §1.2 (eligibility to apply), §1.3.1(d) (applicant's
-- statement), IM §4 (events); X-09 escalation card (restore
-- completeness).
-- Retrieved: 2026-07-21  Project: ujujwgopdwirebgcpekc (techne-coop-cis)

CREATE OR REPLACE FUNCTION public.apply_for_membership(p_display_name text, p_email text, p_note text DEFAULT NULL::text)
 RETURNS jsonb
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
declare
  v_agent_id      uuid;
  v_app_id        uuid;
  v_membership_id uuid;
  v_event_id      uuid;
begin
  -- §1.2: every person eligible for membership may apply.
  -- §1.3.1(d): application includes the applicant's statement.
  insert into agents (kind, display_name)
  values ('person', p_display_name)
  returning id into v_agent_id;

  insert into applications (agent_id, note)
  values (v_agent_id, p_note)
  returning id into v_app_id;

  insert into memberships (agent_id, state)
  values (v_agent_id, 'applied')
  returning id into v_membership_id;

  insert into events (
    occurred_at, kind, agent_id, provenance, settlement, payload
  ) values (
    now(),
    'membership.applied',
    v_agent_id,
    'real',
    'settled',
    jsonb_build_object(
      'display_name', p_display_name,
      'email',        p_email,
      'note',         p_note,
      'application_id', v_app_id,
      'membership_id',  v_membership_id
    )
  )
  returning id into v_event_id;

  return jsonb_build_object(
    'agent_id',       v_agent_id,
    'application_id', v_app_id,
    'event_id',       v_event_id,
    'status',         'received'
  );
end $function$
