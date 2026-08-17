-- ============================================================
-- 0023_gatherings_host_write_bound.sql
-- DRAFT. APPROVED DIRECTION. NOT YET APPLIED.
--
-- The direction is on the record. The steward (Todd Youngblood)
-- gave it in Buzz #intranet-dev on 2026-08-17T19:00:50Z, event
-- 5964c4ce86f71bac1714f55cc7683f90359a0aed86475181b2b368ce4243334e,
-- and the same message delegated the proceed call, which Nou
-- exercised the same day in the same thread. That pair, the
-- steward's delegation and Nou's exercised call, is the adoption
-- authority for this draft's direction. There was no board vote
-- and this file claims none.
--
-- It has still not been applied to the live CIS (ujujwgopdwirebgcpekc)
-- and it is not in the migration chain that scripts/rls_probe.py
-- stands in CI. Application is Nou's act, not a build agent's, and
-- nothing here is true of the record until it happens (BP v2).
--
-- 0021 and 0022 are reserved by the almanac for V-01 and V-02
-- (rdm-ledger.yaml, "Migration 0021 staged with its probe cells"
-- and "Migration 0022 staged with its probe cells"), so this
-- draft takes 0023 and does not claim their numbers.
-- ============================================================

-- ---------- the finding ----------
-- P-08 reported, and the live database confirms, that
-- gatherings_host_write admits a write from an authenticated
-- agent who is bound to an agents row but holds no active
-- membership. The policy as emitted by 0002_policies.sql
-- (commons/authority-map/0002_policies.sql, the gatherings and
-- sessions block, anchored there on Bylaws §2.1) carries the same
-- clause twice, for all, on gatherings:
--
--     using      (host_agent_id = app_agent_id() or app_has_role('steward'))
--     with check (host_agent_id = app_agent_id() or app_has_role('steward'))
--
-- Read live on 2026-08-17 against project ujujwgopdwirebgcpekc
-- (pg_policies, tablename = 'gatherings'), the deployed policy is
-- the same text with the enum cast the catalog adds:
--
--   qual       ((host_agent_id = app_agent_id()) OR app_has_role('steward'::appointment))
--   with_check ((host_agent_id = app_agent_id()) OR app_has_role('steward'::appointment))
--
-- app_agent_id() (0002_policies.sql, helpers block) returns the
-- agents row bound to auth.uid() and asks nothing about
-- membership state. So an applicant with a session and an agents
-- binding satisfies host_agent_id = app_agent_id() by naming
-- themselves host, and the WITH CHECK admits the insert. The
-- AM v0.1 section 5 matrix gives the gatherings applicant cell as
-- a dash, and the section 6 gather-paths family grants the
-- calendar to members. The policy is wider than the document.
--
-- The house pattern for exactly this shape is already in 0002.
-- opportunities_author_write, anchored on PRD v0.3 §4 Find,
-- carries the membership test in its WITH CHECK and not in its
-- USING:
--
--     using      (author_agent_id = app_agent_id())
--     with check (author_agent_id = app_agent_id() and app_is_member())
--
-- This draft brings gatherings to that pattern and changes
-- nothing else. It is a narrowing: no cell of section 5 gains a
-- capability, and one cell stops granting what the document
-- never granted.

-- ---------- what this draft does not change ----------
-- USING is left alone deliberately. A member who hosts a
-- gathering and then lapses should still read and close the row
-- they own; the narrowing belongs on the creation of new state,
-- which is what WITH CHECK governs.
--
-- sessions_host_write needs no companion change: its subquery
-- against gatherings runs under gatherings_member_read, which
-- already requires app_is_member() or app_is_overseer(), so a
-- bound non-member sees no gathering to hang a session on.
--
-- Adjacent and NOT addressed here, recorded for the steward
-- rather than fixed by an agent: events_scoped_insert
-- (0002_policies.sql, events block) admits any bound agent as
-- actor for kinds matching '^(signature|registration|
-- opportunity|gathering)\.' without a membership test. Whether
-- that is the same defect or a deliberate width is a reading of
-- AM v0.1 section 7, and it is not this draft's to decide.
--
-- Since answered by the steward's direction of 2026-08-17 cited
-- above, which asked for a per-kind narrowing. It is drafted as
-- 0024_events_scoped_insert_narrowed.sql, a companion to this
-- file and not a change to it.

-- ---------- the correction ----------
-- Anchors unchanged: Bylaws v2.1 section 2.1 (the host holds the
-- gathering; the steward may act as host); AM v0.1 section 5
-- gatherings row; AM v0.1 section 6 gather paths.

drop policy if exists gatherings_host_write on gatherings;

-- Bylaws §2.1: the host creates and manages their gathering, and
-- the steward may act as host. A host is a member (AM v0.1 §5:
-- the applicant cell on gatherings is a dash), so the check that
-- admits new rows says so. Art. XV is untouched: nothing here
-- widens the anon column.
create policy gatherings_host_write on gatherings
  for all
  using (host_agent_id = app_agent_id() or app_has_role('steward'))
  with check (
    (host_agent_id = app_agent_id() and app_is_member())
    or app_has_role('steward')
  );
