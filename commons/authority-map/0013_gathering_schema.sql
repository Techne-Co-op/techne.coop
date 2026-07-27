-- 0013_gathering_schema.sql · G-04 · what a gathering says about itself
--
-- A gathering carried a title and a host and nothing else, so the calendar
-- could say when a thing happened and who held it, but not what it was or
-- where to stand. Two columns close that, and the surface gains the act
-- that was missing: a member schedules a gathering from the calendar
-- rather than from a database console.
--
-- No verb and no policy change. The authority already reads correctly:
-- 0002's gatherings_host_write lets a member write a gathering they host
-- and lets a steward act for any, and sessions_host_write follows the
-- gathering. The Gather train writes its rows from the client under those
-- policies, as the Find train does, and records the act as an event the
-- same way (F-01, F-03). This migration is columns and comments only.
--
-- Cites: PRD v0.3 section 4 Gather; Bylaws section 2.1 (the host holds the
-- gathering); IM v0.1 Law I (the act lands as an event).

alter table gatherings
  add column if not exists description text,
  add column if not exists location    text;

comment on column gatherings.description is
  'What the gathering is, in the host''s words: enough for a member to know whether to come. G-04.';
comment on column gatherings.location is
  'Where to stand: a room at 1515 Walnut, an address, or a link for a gathering held at distance. Free text on purpose; the cooperative meets in more kinds of place than an enum would hold. G-04.';
