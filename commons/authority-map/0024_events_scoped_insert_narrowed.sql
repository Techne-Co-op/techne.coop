-- ============================================================
-- 0024_events_scoped_insert_narrowed.sql
-- DRAFT. APPROVED DIRECTION. NOT YET APPLIED.
--
-- The direction is on the record. The steward (Todd Youngblood)
-- gave it in Buzz #intranet-dev on 2026-08-17T19:00:50Z, event
-- 5964c4ce86f71bac1714f55cc7683f90359a0aed86475181b2b368ce4243334e:
-- a guest may see some privacy-aware records and may navigate the
-- intranet, but a guest performs no CRUD; public events are held
-- on Luma, not here. The same message delegated the proceed call,
-- and Nou exercised that delegated call the same day in the same
-- thread. That pair, the steward's delegation and Nou's exercised
-- call, is the adoption authority for this draft's direction.
-- There was no board vote and this file claims none.
--
-- Still a draft in the sense BP v2 means it: the file has not been
-- applied to the live CIS (ujujwgopdwirebgcpekc) and it is not in
-- the migration chain scripts/rls_probe.py stands in CI. Nou
-- applies it, not a build agent.
--
-- 0021 and 0022 are reserved by the almanac for V-01 and V-02;
-- 0023 carries the gatherings_host_write narrowing. This draft
-- takes 0024.
-- ============================================================

-- ---------- the finding ----------
-- 0023 recorded this one adjacent and left it for the steward:
-- events_scoped_insert (commons/authority-map/0002_policies.sql
-- lines 146 to 151, the events block) admits any bound agent as
-- actor for four kind families without asking about membership:
--
--     with check (
--       (actor_agent_id = app_agent_id()
--         and kind ~ '^(signature|registration|opportunity|gathering)\.')
--       or app_is_overseer()
--     )
--
-- Read live on 2026-08-17 against project ujujwgopdwirebgcpekc
-- (pg_policies, tablename = 'events'), the deployed policy is that
-- text verbatim. Repo and database agree.
--
-- app_agent_id() (0002_policies.sql lines 35 to 38) returns the
-- agents row bound to auth.uid() and asks nothing about membership
-- state. So an applicant, or any A-5 arrival with a session and an
-- agents binding, may write a gathering.scheduled or an
-- opportunity.resolved event into the log. AM v0.1 section 5 gives
-- the applicant cell on gatherings and on opportunities as a dash.
-- The policy is wider than the document, in the same way and for
-- the same reason as the gatherings defect 0023 corrects.

-- ---------- who actually writes these kinds ----------
-- The narrowing is only safe if it breaks no legitimate writer.
-- Every writer of an events row in this repository was read before
-- this draft was written, and they fall into two classes.
--
-- Class one, definer functions and definer triggers. These do not
-- consult events_scoped_insert at all:
--
--   membership.applied
--     commons/authority-map/0007_apply_for_membership.sql line 40,
--     inside apply_for_membership, declared SECURITY DEFINER at
--     line 17.
--   signature.*
--     commons/authority-map/0003_sign_agreement.sql line 50,
--     inside sign_agreement, declared definer at line 16.
--   registration.*
--     commons/authority-map/0015_member_notices.sql line 65,
--     inside notify_registration_turn, declared definer at line
--     61, fired by the triggers at lines 82 to 91. The kind
--     is 'registration.' || new.state.
--   opportunity.responded
--     commons/authority-map/0015_member_notices.sql line 36,
--     inside notify_opportunity_response, definer at line 32,
--     fired by the trigger at lines 52 to 55.
--   the rest
--     0008 line 46, 0010 line 107, 0011 lines 99 and 160, 0012
--     line 74, 0017 line 133, all inside definer functions.
--
-- Read live on 2026-08-17: pg_proc gives prosecdef true and
-- proowner postgres for apply_for_membership, sign_agreement,
-- notify_registration_turn, notify_opportunity_response,
-- app_agent_id and app_is_member. pg_class gives events,
-- gatherings and opportunities as owned by postgres with
-- relforcerowsecurity false. A definer function owned by the table
-- owner, on a table that does not force row security, is not
-- subject to the table's policies. So none of class one can be
-- narrowed by anything this file does.
--
-- Class two, the client trains, which do consult the policy. There
-- are exactly three call sites in the whole repository, and they
-- write two kind families between them:
--
--   gathering.scheduled
--     commons/gatherings/index.html lines 723 to 728, after the
--     gatherings and sessions inserts in the same handler.
--   gathering.archived
--     commons/gatherings/index.html lines 752 to 756, in
--     archiveGathering.
--   opportunity.resolved and opportunity.withdrawn
--     commons/opportunities/index.html lines 438 to 443, written
--     as 'opportunity.' || finalState.
--
-- 0013_gathering_schema.sql lines 12 to 14 says this out loud:
-- the Gather train writes its rows from the client under 0002's
-- policies and records the act as an event the same way the Find
-- train does.
--
-- In all three, the actor is already required to be a member by
-- the policy governing the row the event is about.
-- opportunities_author_write (0002_policies.sql lines 204 to 206)
-- carries app_is_member() in its WITH CHECK today. With 0023
-- applied, gatherings_host_write does the same. So the membership
-- test this draft adds to the event is a test those actors already
-- pass. Nothing that works stops working; what stops is the case
-- where a non-member writes a log entry about a row they were
-- never able to create.

-- ---------- what this draft does not change ----------
-- The signature and registration families keep their branch
-- untouched, exactly as it stands. They have no client-side writer
-- at all, so narrowing them would be a change with no subject, and
-- removing them would be a wider claim than the direction carries.
-- Recorded for the steward rather than acted on by an agent: those
-- two families could be dropped from the member branch entirely
-- without affecting any writer in this repository. Whether the
-- branch is dead width or a reserved surface is a reading of
-- AM v0.1 section 7, and it is not this draft's to decide.
--
-- The overseer branch is untouched. events_read and
-- events_steward_read are untouched. No SELECT path moves, which
-- is what keeps the guest posture intact: a guest reads what the
-- privacy-aware read policies already allow and may navigate, and
-- gains no write. Art. XV is untouched and the anon column stays
-- empty; 0002_policies.sql lines 217 to 222 grant the write
-- surface to authenticated only, so the guest posture is enforced
-- twice over.

-- ---------- the correction ----------
-- Anchors unchanged: IM v0.1 Laws II and X (the act lands as an
-- event; the recorded actor is the asker); AM v0.1 section 7
-- (member-actionable kinds); AM v0.1 section 5, the events,
-- gatherings and opportunities rows; Bylaws v2.1 section 2.1 and
-- PRD v0.3 section 4 Find.

drop policy if exists events_scoped_insert on events;

-- AM v0.1 §7: member-actionable kinds only, and for the two
-- families a member acts on from the client, the actor is a
-- member (Bylaws v2.1 §2.1). Every other write path is a
-- definer function or an overseer act. Art. XV untouched.
create policy events_scoped_insert on events
  for insert with check (
    (actor_agent_id = app_agent_id()
      and kind ~ '^(gathering|opportunity)\.'
      and app_is_member())
    or (actor_agent_id = app_agent_id()
      and kind ~ '^(signature|registration)\.')
    or app_is_overseer()
  );
