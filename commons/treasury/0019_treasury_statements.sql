-- 0019_treasury_statements.sql · T-07 · the statements store
--
-- The statements view (TR §9a, T-07) derives the cooperative's monthly
-- picture from three sources: the record, the instruments in force, and
-- the reads. The record's events do not yet exist (T-02 forward) and the
-- §9 rail reads have no seam deployed (T-06), so the first statements
-- arrive by the third source alone: rail-derived snapshots, generated
-- read-only from Stripe, Mercury, Xero, and the Safe by the runner at
-- scripts/treasury_statements.py, staged 2026-08-05 on the steward's
-- direction ahead of T-01's board act, in T-01's own precedent.
--
-- Two shapes worth naming:
--
--   A statement here is an outside observation, not a fact in the log.
--   TR §9 draws the line: a balance read "is neither a movement nor a
--   meaning, so nothing here is written to the log." This table holds
--   observations beside the record, exactly as §9 describes, and writes
--   nothing to events. When T-02 and T-03 land, the record's own folds
--   take over the flow and close columns, and these rows remain what
--   they were: the rails as read, at a time, by a runner with no keys
--   to move anything.
--
--   The audience is the §9a member cut, staged. Every payload carries
--   organization aggregates only: no member names, no member ids, no
--   per-member amounts. The select policy below therefore admits every
--   authenticated member, which is precisely the visibility default
--   §9a stages and the board act confirms (TR §9a; the §14 open-books
--   item stays open). Writes come only through the management channel
--   under the steward's custody; no client role can insert, update, or
--   delete, so the surface cannot be written from the browser at all.
--
-- Anchors: TR §9, §9a, §14; IM v0.1 Laws IV, X; Bylaws v2.1 §18.1 as
-- carried by 0002 (the member's standing right to read the record his
-- membership concerns).

create table if not exists treasury_statements (
  id            uuid primary key default gen_random_uuid(),
  month         text not null unique
                check (month ~ '^[0-9]{4}-[0-9]{2}$'),
  payload       jsonb not null,
  generated_at  timestamptz not null default now(),
  runner        text not null default 'scripts/treasury_statements.py',
  note          text
);

comment on table treasury_statements is
  'Monthly rail-derived statement snapshots (TR §9a). Observations beside the record, never events. Aggregates only; member-cut visible.';

alter table treasury_statements enable row level security;

-- The member cut: every authenticated member reads the aggregate
-- statements. Staged §9a default; the board act confirms (TR §9a, §14).
create policy treasury_statements_member_read
  on treasury_statements for select
  to authenticated
  using (true);

-- No insert, update, or delete policy exists for any client role:
-- rows enter only by the management channel under the steward's
-- custody (TR §9a architecture; IM Law X, the instrument holds no
-- grant and the browser holds no pen).
