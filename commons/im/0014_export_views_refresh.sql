-- 0014_export_views_refresh.sql · X-11 · the export follows the substrate
--
-- A view defined as `select *` freezes its column list when it is created.
-- 0004 defined the export projections that way, so a column added to a base
-- table afterwards never reaches its export view, and the walkaway carries a
-- narrower row than the record holds. G-04 added description and location to
-- gatherings and export.gatherings kept the old five columns: an export and
-- restore would have returned every gathering without what it is or where to
-- stand, silently, since nothing compares the two.
--
-- Recreating the view re-expands the star. Appending columns is the one shape
-- CREATE OR REPLACE VIEW accepts, and the new columns are at the end.
--
-- The instance is one view; the class is closed in the gate rehearsal, which
-- now applies 0004 and asserts every export projection carries its base
-- table's columns exactly. A drift becomes a failed build rather than a
-- quiet loss discovered at restore.
--
-- Cites: VS v1 section 8 (the walkaway procedure); X-03 (the export views);
-- IM v0.1 Law I (the record is what the export carries).

create or replace view export.gatherings with (security_invoker = on) as
  select * from public.gatherings;
comment on view export.gatherings is
  'Export projection of public.gatherings (X-03), re-expanded after G-04 added description and location (X-11).';
