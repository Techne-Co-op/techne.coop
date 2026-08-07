-- 0020 · gatherings archive (U-15)
-- The host may set a gathering aside without deleting it: the row
-- stays, the record keeps it, the calendar stops showing it. The
-- act itself is recorded as a gathering.archived event by the page.
-- Additive only. RLS already grants the host ALL on the row
-- (gatherings_host_write); no policy change needed.
-- Applied to the live CIS via the Management API 2026-08-07.

alter table public.gatherings
  add column if not exists archived_at timestamptz;

comment on column public.gatherings.archived_at is
  'Set by the host to retire the gathering from the calendar. The row and its history remain; nothing is deleted.';
