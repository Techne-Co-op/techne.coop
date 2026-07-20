-- 0004_export_views.sql
-- X-03: per-table export views for the walkaway rehearsal (VS v1 §8).
--
-- One security-invoker view per base table of IM v0.1, in the `export` schema,
-- projecting the full row set. capital_accounts is a derived fold (Law VII, no
-- stored balance) reconstructed on restore, so it is NOT exported. Only base
-- tables carry the state and the event log the walkaway replays.
--
-- security_invoker means each view respects the querying role's row security.
-- A full export is taken as the service role: the walkaway / disaster-recovery
-- path, which is infrastructure, not a member capability. No grants are added
-- here, so no new visibility is created.
--
-- Cites: IM v0.1 (the base tables), VS v1 §8 (the walkaway procedure).
-- Status: DRAFT. Applied to the CIS project on organizer review (Tier B).
--
-- ESCALATION (X-03, recorded in rdm-ledger.yaml):
--   1. Applying this migration to the live CIS project is an infrastructure act
--      for the steward, not the agent.
--   2. Confirm the export audience is service-role / DR only (this file's
--      assumption) versus a steward- or member-facing download, which would
--      need an Authority Map anchor and could change these projections
--      (for example, redaction of applicant contact details).
--   3. Pin the export-format and SHA convention SUB-05 used (the recorded
--      baseline SHA is not the hash of the JSON tables), so the export producer
--      and the X-09 walkaway agree on what is hashed.

create schema if not exists export;
comment on schema export is 'Per-table export projections for the VS v1 §8 walkaway rehearsal. Read-only, security_invoker; a full export runs as the service role.';

create view export.agents with (security_invoker = on) as select * from public.agents;
comment on view export.agents is 'Export projection of public.agents (X-03).';

create view export.agreements with (security_invoker = on) as select * from public.agreements;
comment on view export.agreements is 'Export projection of public.agreements (X-03).';

create view export.memberships with (security_invoker = on) as select * from public.memberships;
comment on view export.memberships is 'Export projection of public.memberships (X-03).';

create view export.stock_ledger with (security_invoker = on) as select * from public.stock_ledger;
comment on view export.stock_ledger is 'Export projection of public.stock_ledger (X-03).';

create view export.signatures with (security_invoker = on) as select * from public.signatures;
comment on view export.signatures is 'Export projection of public.signatures (X-03).';

create view export.applications with (security_invoker = on) as select * from public.applications;
comment on view export.applications is 'Export projection of public.applications (X-03).';

create view export.events with (security_invoker = on) as select * from public.events;
comment on view export.events is 'Export projection of public.events, the append-only log (X-03).';

create view export.gatherings with (security_invoker = on) as select * from public.gatherings;
comment on view export.gatherings is 'Export projection of public.gatherings (X-03).';

create view export.sessions with (security_invoker = on) as select * from public.sessions;
comment on view export.sessions is 'Export projection of public.sessions (X-03).';

create view export.registrations with (security_invoker = on) as select * from public.registrations;
comment on view export.registrations is 'Export projection of public.registrations (X-03).';

create view export.attendance with (security_invoker = on) as select * from public.attendance;
comment on view export.attendance is 'Export projection of public.attendance (X-03).';

create view export.opportunities with (security_invoker = on) as select * from public.opportunities;
comment on view export.opportunities is 'Export projection of public.opportunities (X-03).';

create view export.responses with (security_invoker = on) as select * from public.responses;
comment on view export.responses is 'Export projection of public.responses (X-03).';

-- role_grants arrived as an AM v0.1 §9 addendum (0002), after the
-- thirteen IM base tables this file first enumerated. Board
-- appointments are governance state the walkaway must reconstruct,
-- so the projection joins the set. Added under X-03 while this file
-- remains a draft, before any live application.
create view export.role_grants with (security_invoker = on) as select * from public.role_grants;
comment on view export.role_grants is 'Export projection of public.role_grants, the appointments addendum (X-03).';
