-- 0007_apply_for_membership.sql
-- X-09 restore-completeness card, executed: this function existed only
-- in the live CIS since B-02 (2026-07-12), never captured as a
-- migration. A walkaway-restored database carried the tables and the
-- fold but not the front door. Captured 2026-07-21 verbatim via
-- pg_get_functiondef under the steward-issued PAT; grants read from
-- pg_proc.proacl the same day. Already live: applying this file to the
-- CIS is a no-op by design (create or replace, identical body).
--
-- Anchors: Bylaws section 1.2 (eligibility to apply), section 1.3.1(d)
-- (the applicant's own statement). The email travels in the event
-- payload, which is where the notices rail (X-02) reads it.

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
end $function$;


-- the public door: the join page calls this with the anon key, before
-- any authentication exists to bind. Faithful to live proacl.
grant execute on function public.apply_for_membership(text, text, text) to anon, authenticated;
