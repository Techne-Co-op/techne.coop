-- 0005_matrix_conformance.sql
-- X-08: two gaps between the AM v0.1 §5 matrix (the document) and the
-- deployed emissions (the code), found by the probe matrix and closed
-- here. The document governs; the emission conforms.
--
-- 1. capital_accounts was created (IM v0.1) as a default view, which
--    postgres runs with the OWNER's row security. Owned by postgres,
--    it bypassed RLS entirely: any authenticated reader folded every
--    member's balances. The §5 caption requires the view to fold only
--    what the events policy already shows the asker. security_invoker
--    makes the fold run as the asker.
--
-- 2. The §5 matrix grants the steward R on events (§4.1 operational
--    oversight; the steward writes lifecycle events per §1.7-1.8 and
--    must read what they wrote). events_read named directors and
--    officers only. An additive policy closes the cell.
--
-- Cites: AM v0.1 §5 (matrix, caption), §6 (capital views), Bylaws
-- §4.1, §5.3, §6.2.1, §18.1.
-- Drafted for adoption by review of the X-08 pull request; applied to
-- the live CIS by the steward on adoption.

alter view capital_accounts set (security_invoker = on);
comment on view capital_accounts is 'One account per member, two projections, both folds, running as the asker: the fold shows only what the events policy shows (AM v0.1 §5 caption; Bylaws §18.1, §6.2.1). STUB: allocation logic blocked · Q3 (PRD v0.3 §11).';

-- §4.1: the steward holds operational oversight and reads the log the
-- matrix row assigns them (AM v0.1 §5 events/steward: R).
create policy events_steward_read on events
  for select using (app_has_role('steward'));
