-- 0008_admissions.sql · B-01, B-02 follow-on · the steward's desk becomes an act
-- Decision: steward feedback in the run-through (2026-07-22): the desk
-- was SQL and a UUID hunt for facts the system already holds. Two
-- pieces close it:
--
--   admit_member(agent) · admission recorded as one act: the state
--   transition and its membership.admitted event land together, actor
--   captured, the same atomic pattern as sign_agreement (0003). The
--   lifecycle automaton (IM v0.1 §6) still enforces legality
--   regardless of caller.
--
--   bind on first sign-in · B-01's intent ("wire the identity binding
--   to sign-in") completing itself: when a new sign-in's address
--   matches exactly one unbound agent whose membership.applied event
--   carries that address, the binding is made. The magic link proved
--   control of the address; the application claimed it. Ambiguity
--   binds nothing.
--
-- Anchors: admission per Bylaws §1.3 (the Board decides, §1.3.1(e));
-- the steward manages intake per §1.3.3 and the membership-liaison
-- shape of §1.13; the Board's operational hands per §3.1. Binding per
-- B-01 (auth flow binding auth_user_id to agents).
-- The trigger half guards on auth.users existing, so the chain applies
-- clean on CI substrates that carry only the auth.uid() shim.

create or replace function public.admit_member(p_agent_id uuid)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_actor uuid := app_agent_id();
  v_event uuid;
begin
  if not (app_has_role('steward') or app_has_role('director')) then
    raise exception 'admission is recorded by the Board''s assigned hand (Bylaws 1.3, 3.1)';
  end if;

  update memberships set state = 'active'
   where agent_id = p_agent_id and state = 'applied';
  if not found then
    raise exception 'no applied membership for this agent';
  end if;

  insert into events (occurred_at, actor_agent_id, agent_id, kind, payload)
  values (now(), v_actor, p_agent_id, 'membership.admitted',
          jsonb_build_object('agent_id', p_agent_id))
  returning id into v_event;

  return jsonb_build_object('admitted', p_agent_id, 'event_id', v_event);
end $$;

comment on function public.admit_member(uuid) is 'B-02 follow-on: admission as one act, flip and event together, steward or director only. Bylaws §1.3, §1.3.3, §3.1.';

revoke all on function public.admit_member(uuid) from public;
grant execute on function public.admit_member(uuid) to authenticated;

do $$
begin
  if exists (select 1 from information_schema.tables
              where table_schema = 'auth' and table_name = 'users') then

    create or replace function public.bind_agent_on_signin() returns trigger
    language plpgsql security definer set search_path = public as $fn$
    declare
      v_agent uuid;
      v_count int;
    begin
      select count(distinct e.agent_id) into v_count
        from events e
        join agents a on a.id = e.agent_id
       where e.kind = 'membership.applied'
         and e.payload->>'email' = new.email
         and a.auth_user_id is null;

      if v_count = 1 then
        select distinct e.agent_id into v_agent
          from events e
          join agents a on a.id = e.agent_id
         where e.kind = 'membership.applied'
           and e.payload->>'email' = new.email
           and a.auth_user_id is null;
        update agents set auth_user_id = new.id where id = v_agent;
      end if;
      return new;
    end $fn$;

    comment on function public.bind_agent_on_signin() is 'B-01 completing itself: the first sign-in with an applied address becomes its agent. Exactly-one match or nothing.';

    drop trigger if exists agents_bind_on_signin on auth.users;
    create trigger agents_bind_on_signin
      after insert on auth.users
      for each row execute function public.bind_agent_on_signin();
  end if;
end $$;
