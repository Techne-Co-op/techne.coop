-- 0029_phone_bindings_intranet.sql · SMS-05 · the ceremony moves to
-- the intranet, and the binding anchors to the member the record knows
--
-- Not applied. Drafted against issue #247 and the SMS-05 design page at
-- /commons/build/sms-04-ceremony/. Applying it to the live CIS is a
-- schema act and a stop card under BP: it needs a named human. The
-- agent that drafted this file did not run it anywhere.
--
-- WHAT IS WRONG TODAY, stated before what changes
--
--   1. A binding anchors to a Nostr key (0028, member_pubkey NOT NULL)
--      and to an E.164 number. Neither is an identity the record holds.
--      There is no column anywhere in the CIS that maps a Nostr pubkey
--      to an agents row; verified against the live database 2026-08-26,
--      the only column in any table matching pubkey or nostr is
--      phone_bindings.member_pubkey itself. So a binding today names a
--      key the record cannot resolve to a person.
--   2. The ceremony presumes Buzz membership, which is a higher
--      friction door than the phone line it gates (#247).
--   3. phone_events carries RLS with one policy, phone_relay_insert
--      (0027), and no SELECT policy for anyone. A member cannot read
--      their own messages. 0026 said the member-scoped read arrives
--      with the binding; this is that migration.
--   4. anon and authenticated hold every table privilege on both
--      phone_events and phone_bindings, because the Supabase creation
--      defaults were never stripped the way 0009 strips them. Nothing
--      is readable today only because RLS has no permissive policy for
--      those roles. The moment one exists, the grants underneath are
--      already wide, DELETE and UPDATE included. This migration adds
--      the first such policy, so it strips the defaults first, exactly
--      as 0009 did for profiles.
--
-- WHAT THIS MIGRATION DOES
--
--   Extends phone_bindings rather than superseding it. The evidence
--   trail, the roles, the router policy, the partial unique indexes,
--   and every verified row all stand. Three columns arrive (agent_id,
--   origin, and the code's expiry and attempt counters), member_pubkey
--   becomes optional, and a row must carry at least one anchor.
--
--   PRESERVATION, which is the load-bearing property. Every existing
--   row keeps its status. The two verified bindings live on 2026-08-26
--   remain verified, keep their pubkey, take origin='buzz', and take a
--   NULL agent_id, because no mapping from pubkey to agent exists to
--   backfill from. phone_router_select reads status='verified' and is
--   untouched, so routing for those numbers does not change by one
--   row. Naming which agent each of those two keys is belongs to a
--   human and is decision SMS5-D3 on the design page; it is a data
--   act, not a schema act, and it is deliberately not attempted here.
--
--   The member's own hands arrive as three security definer verbs, in
--   the shape apply_for_membership (0007) established: the member
--   holds no INSERT or UPDATE on the table at all, and every write
--   goes through a verb that resolves the actor with app_agent_id().
--
-- Anchors: Bylaws v2.1 §18.1, an agent's own record; §1.13, the
-- register; §2.1, housekeeping under owner authority. AM v0.1 §5.
-- Issue #247 for the direction; #191 for the tier model; #240 for the
-- session strategy the binding keys.

-- ============================================================
-- §1 · the anchor the intranet knows
-- ============================================================

alter table phone_bindings
  add column agent_id uuid references agents(id);
comment on column phone_bindings.agent_id is
  'SMS-05: the member the intranet authenticated, resolved through app_agent_id() at ceremony time. Null on rows minted by the Buzz ceremony before SMS-05, which anchor on member_pubkey alone; naming those is a human act, not a backfill.';

alter table phone_bindings
  add column origin text not null default 'buzz'
  check (origin in ('buzz', 'intranet', 'steward'));
comment on column phone_bindings.origin is
  'SMS-05: which ceremony minted the row. buzz is the SMS-03 key-signed ceremony and is the default so existing rows are described truthfully; intranet is the magic-link session ceremony; steward is a binding a named human entered by hand, which carries no possession proof of its own and says so.';

alter table phone_bindings
  add column code_expires_at timestamptz;
comment on column phone_bindings.code_expires_at is
  'SMS-05: when the outstanding one-time code stops being accepted. Set by the sender when the code goes out, cleared on verify. Expiry is enforced in phone_bind_confirm() rather than by a sweep, so a code is dead the moment it is late even if nothing has run.';

alter table phone_bindings
  add column code_attempts smallint not null default 0;
comment on column phone_bindings.code_attempts is
  'SMS-05: failed confirmations against the outstanding code. phone_bind_confirm() refuses at five and retires the row, so a six digit code cannot be walked.';

alter table phone_bindings
  add column code_sent_at timestamptz;
comment on column phone_bindings.code_sent_at is
  'SMS-05: when the challenge SMS was accepted by the carrier. Null while a request waits for the sender to pick it up.';

-- The key stops being mandatory. A member who has never touched Buzz
-- has no key to offer, which is the whole complaint in #247.
alter table phone_bindings
  alter column member_pubkey drop not null;

-- But a row with neither anchor names nobody, and would be a binding
-- to a phone number alone, which is the credential #247 exists to
-- stop trusting.
alter table phone_bindings
  add constraint phone_bindings_anchor_present
  check (agent_id is not null or member_pubkey is not null);

-- An intranet ceremony that produced no agent_id produced nothing.
alter table phone_bindings
  add constraint phone_bindings_intranet_has_agent
  check (origin <> 'intranet' or agent_id is not null);

-- ============================================================
-- §2 · the states the intranet ceremony passes through
-- ============================================================
-- 0028 knew three states. The intranet ceremony adds the moment
-- between a member asking and a code existing: the database cannot
-- send an SMS, so a request sits until the relay picks it up, mints
-- the code, and moves the row to pending. Two more terminal states
-- name the two ways a ceremony dies without a binding.

alter table phone_bindings
  drop constraint phone_bindings_status_check;
alter table phone_bindings
  add constraint phone_bindings_status_check
  check (status in ('requested', 'pending', 'verified', 'revoked', 'expired', 'failed'));
comment on column phone_bindings.status is
  'SMS-05: requested, the member asked and no code exists yet; pending, a code is out and unexpired; verified, the code came back; revoked, a live binding was ended; expired, the code went stale or the attempts ran out; failed, the challenge could not be sent. Only verified admits a number.';

alter table phone_bindings
  drop constraint phone_bindings_revoke_reason_check;
alter table phone_bindings
  add constraint phone_bindings_revoke_reason_check
  check (revoke_reason is null or
         revoke_reason in ('sms_stop', 'member_request', 'steward',
                           'expired', 'attempts', 'send_failed',
                           'number_reassigned', 'rebind'));
comment on column phone_bindings.revoke_reason is
  'SMS-05: why a row left the live set. member_request is the member ending their own binding on the intranet or by STOP; number_reassigned is a steward act when a number demonstrably moved to another person; rebind is the old row retiring as a member binds a different number.';

-- One live binding per member, the same shape 0028 gave the key and
-- the number. Partial, so the revoked history accumulates freely, and
-- null agent_id rows do not collide because nulls are distinct.
create unique index phone_bindings_live_agent
  on phone_bindings (agent_id) where status = 'verified';

create index phone_bindings_agent_idx on phone_bindings (agent_id, status);
create index phone_bindings_open_idx
  on phone_bindings (status, requested_at) where status in ('requested', 'pending');

-- ============================================================
-- §3 · strip the creation defaults before the first policy exists
-- ============================================================
-- Supabase grants ALL on a new table to anon and authenticated at
-- creation. 0009 found this the hard way on the live apply and said
-- so: strip it first, or the column discipline below is decoration.
-- 0026 and 0028 did not strip, and were safe only because neither
-- table carried a permissive policy for those roles. §4 adds the
-- first one, so the grants stop being harmless here.

revoke all on table phone_events   from anon, authenticated;
revoke all on table phone_bindings from anon, authenticated;

-- A member reads their own binding, and never the secret that proves
-- it. code_hash is a SHA-256 of six digits, which is to say it is the
-- code: anyone who can read it can finish a ceremony without ever
-- receiving the SMS, and the possession proof is gone. It is withheld
-- by column privilege, the way profiles.email is (0009).
grant select (id, agent_id, member_pubkey, peer_e164, status, origin,
              requested_at, code_sent_at, code_expires_at,
              verified_at, revoked_at, revoke_reason, buzz_channel_id)
  on phone_bindings to authenticated;

-- The member's own messages, and not the carrier's envelope. payload
-- holds the raw provider record and error holds operational text;
-- neither is the member's correspondence and both can carry service
-- detail that is nobody's own record.
grant select (id, occurred_at, direction, peer_e164, content,
              quo_message_id, conversation_id, status)
  on phone_events to authenticated;

-- ============================================================
-- §4 · the member reads their own record
-- ============================================================

-- Anchor: an agent's own record is theirs to read, Bylaws v2.1 §18.1;
-- the register per §1.13. A member sees their own bindings, every
-- state, including the ones that failed, because a ceremony that went
-- wrong is a thing that happened to them.
create policy phone_bindings_self_read on phone_bindings
  for select to authenticated
  using (agent_id = app_agent_id());

-- The log has no agent column, so ownership is read through the
-- binding that was live when the message crossed. The window is closed
-- at both ends deliberately: a member reads the traffic on their number
-- for exactly the period their binding covered it, so a number that
-- changes hands does not hand its history to the new holder, and does
-- not take the old holder's history away either.
--
-- Anchor: an agent's own record is theirs to read, Bylaws v2.1 §18.1;
-- the read 0026 deferred to the migration that would bind a member.
create policy phone_events_self_read on phone_events
  for select to authenticated
  using (exists (
    select 1 from phone_bindings b
     where b.agent_id = app_agent_id()
       and b.peer_e164 = phone_events.peer_e164
       and b.verified_at is not null
       and phone_events.occurred_at >= b.verified_at
       and phone_events.occurred_at < coalesce(b.revoked_at, now())
  ));

-- No INSERT, UPDATE, or DELETE policy for authenticated on either
-- table, and no grant either. Every member write travels through the
-- verbs in §5. This is not a convenience: a member who could UPDATE
-- phone_bindings could set their own status to verified.

-- ============================================================
-- §5 · the member's three hands
-- ============================================================
-- Shape per 0007: security definer, search_path pinned, the actor
-- resolved with app_agent_id() and never passed in as an argument.

create or replace function public.phone_bind_request(p_e164 text)
  returns jsonb
  language plpgsql
  security definer
  set search_path to 'public'
as $$
declare
  v_agent   uuid;
  v_id      uuid;
  v_today   int;
  v_mine    int;
begin
  -- §18.1: the act is the member's own, on their own record.
  v_agent := app_agent_id();
  if v_agent is null then
    return jsonb_build_object('status', 'refused', 'reason', 'no_agent');
  end if;
  -- §1.13, §2.9: the register is the members'. A person whose
  -- membership is not active does not bind a number to it.
  if not app_is_member() then
    return jsonb_build_object('status', 'refused', 'reason', 'not_a_member');
  end if;
  if p_e164 !~ '^\+[1-9][0-9]{7,14}$' then
    return jsonb_build_object('status', 'refused', 'reason', 'not_e164');
  end if;

  if exists (select 1 from phone_bindings
              where agent_id = v_agent and status = 'verified') then
    return jsonb_build_object('status', 'refused', 'reason', 'already_bound');
  end if;
  if exists (select 1 from phone_bindings
              where peer_e164 = p_e164 and status = 'verified') then
    -- Deliberately the same answer as a free number would give at the
    -- next step, so this verb is not an oracle for who holds what.
    return jsonb_build_object('status', 'refused', 'reason', 'number_unavailable');
  end if;

  select count(*) into v_today from phone_bindings
   where peer_e164 = p_e164 and requested_at > now() - interval '24 hours';
  if v_today >= 3 then
    return jsonb_build_object('status', 'refused', 'reason', 'number_rate_limit');
  end if;

  select count(*) into v_mine from phone_bindings
   where agent_id = v_agent and requested_at > now() - interval '24 hours';
  if v_mine >= 5 then
    return jsonb_build_object('status', 'refused', 'reason', 'member_rate_limit');
  end if;

  insert into phone_bindings (agent_id, peer_e164, status, origin)
  values (v_agent, p_e164, 'requested', 'intranet')
  returning id into v_id;

  insert into events (occurred_at, kind, agent_id, actor_agent_id,
                      provenance, settlement, payload)
  values (now(), 'phone.binding.requested', v_agent, v_agent,
          'real', 'settled',
          jsonb_build_object('binding_id', v_id, 'origin', 'intranet'));

  return jsonb_build_object('status', 'requested', 'binding_id', v_id);
end $$;
comment on function public.phone_bind_request(text) is
  'SMS-05: a signed-in member asks for a code on a number. Writes the request and nothing else; the database cannot send an SMS, so the sender picks the row up and mints the code. The number never enters the event payload, only the binding row.';

create or replace function public.phone_bind_confirm(p_binding uuid, p_code text)
  returns jsonb
  language plpgsql
  security definer
  set search_path to 'public'
as $$
declare
  v_agent uuid;
  v_row   phone_bindings%rowtype;
begin
  -- §18.1: only the member whose ceremony this is may finish it.
  v_agent := app_agent_id();
  if v_agent is null then
    return jsonb_build_object('status', 'refused', 'reason', 'no_agent');
  end if;

  select * into v_row from phone_bindings
   where id = p_binding and agent_id = v_agent for update;
  if not found then
    return jsonb_build_object('status', 'refused', 'reason', 'not_found');
  end if;
  if v_row.status <> 'pending' then
    return jsonb_build_object('status', 'refused', 'reason', 'not_pending');
  end if;
  if v_row.code_expires_at is null or v_row.code_expires_at < now() then
    update phone_bindings set status = 'expired', code_hash = null,
           revoke_reason = 'expired', revoked_at = now()
     where id = p_binding;
    return jsonb_build_object('status', 'expired');
  end if;
  if v_row.code_attempts >= 5 then
    update phone_bindings set status = 'expired', code_hash = null,
           revoke_reason = 'attempts', revoked_at = now()
     where id = p_binding;
    return jsonb_build_object('status', 'expired', 'reason', 'attempts');
  end if;

  -- sha256() is in pg_catalog from Postgres 11 and needs no extension,
  -- so the pinned search_path above cannot break the comparison. It is
  -- the same digest the relay computes in Python.
  if v_row.code_hash is distinct from
     encode(sha256(convert_to(p_code, 'UTF8')), 'hex') then
    update phone_bindings set code_attempts = code_attempts + 1
     where id = p_binding;
    return jsonb_build_object('status', 'refused', 'reason', 'code_mismatch',
                              'attempts_left', 4 - v_row.code_attempts);
  end if;

  update phone_bindings
     set status = 'verified', verified_at = now(), code_hash = null,
         code_expires_at = null
   where id = p_binding;

  insert into events (occurred_at, kind, agent_id, actor_agent_id,
                      provenance, settlement, payload)
  values (now(), 'phone.binding.verified', v_agent, v_agent,
          'real', 'settled',
          jsonb_build_object('binding_id', p_binding, 'origin', v_row.origin));

  return jsonb_build_object('status', 'verified', 'binding_id', p_binding);
end $$;
comment on function public.phone_bind_confirm(uuid, text) is
  'SMS-05: the member types the code back on the surface they are signed in to. Possession of the number is proven by the code; identity is proven by the session. Five wrong answers retire the row.';

create or replace function public.phone_bind_revoke(p_binding uuid)
  returns jsonb
  language plpgsql
  security definer
  set search_path to 'public'
as $$
declare
  v_agent uuid;
  v_row   phone_bindings%rowtype;
begin
  -- §18.1: ending a binding on one's own record is the member's act,
  -- and turning the channel off is never the dangerous direction
  -- (issue #191, 2026-08-19).
  v_agent := app_agent_id();
  if v_agent is null then
    return jsonb_build_object('status', 'refused', 'reason', 'no_agent');
  end if;

  select * into v_row from phone_bindings
   where id = p_binding and agent_id = v_agent for update;
  if not found then
    return jsonb_build_object('status', 'refused', 'reason', 'not_found');
  end if;
  if v_row.status not in ('requested', 'pending', 'verified') then
    return jsonb_build_object('status', 'refused', 'reason', 'not_live');
  end if;

  update phone_bindings
     set status = 'revoked', revoked_at = now(),
         revoke_reason = 'member_request', code_hash = null,
         code_expires_at = null
   where id = p_binding;

  insert into events (occurred_at, kind, agent_id, actor_agent_id,
                      provenance, settlement, payload)
  values (now(), 'phone.binding.revoked', v_agent, v_agent,
          'real', 'settled',
          jsonb_build_object('binding_id', p_binding,
                             'reason', 'member_request',
                             'origin', v_row.origin));

  return jsonb_build_object('status', 'revoked', 'binding_id', p_binding);
end $$;
comment on function public.phone_bind_revoke(uuid) is
  'SMS-05: the member ends their own binding from the surface that made it. Revocation is a status and a timestamp; the row and its evidence stay, and the member keeps their read of the traffic the binding covered.';

-- The verbs are for members, not for the public door. anon holds none
-- of them: unlike apply_for_membership, every one of these presumes a
-- session that already resolves to an agent.
revoke execute on function public.phone_bind_request(text)         from public, anon;
revoke execute on function public.phone_bind_confirm(uuid, text)   from public, anon;
revoke execute on function public.phone_bind_revoke(uuid)          from public, anon;
grant  execute on function public.phone_bind_request(text)         to authenticated;
grant  execute on function public.phone_bind_confirm(uuid, text)   to authenticated;
grant  execute on function public.phone_bind_revoke(uuid)          to authenticated;

-- ============================================================
-- §6 · what this migration does not do
-- ============================================================
-- No backfill of agent_id on the two pre-SMS-05 verified rows: there
-- is nothing in the record to backfill from, and guessing which
-- person a Nostr key is would be the agent asserting an identity
-- binding, which is exactly the act #247 says belongs to a ceremony.
--
-- No change to phone_router_select, phone_binder_all, or
-- phone_relay_insert. The routing path, the ceremony service, and the
-- log writer keep the hands 0027 and 0028 gave them.
--
-- No retirement of the Buzz ceremony. Whether it survives as a
-- steward-only fallback is decision SMS5-D1 and belongs to the
-- steward; this file leaves origin='buzz' a legal value so that
-- either answer applies without another migration.
--
-- No write tier. A verified binding still admits a number to the
-- read-only tier and nothing above it, unchanged from #191 and #240.
