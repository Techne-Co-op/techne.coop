-- 0009_profiles.sql · B-06 · the profile grows beyond a name
-- Decision: the steward's direction (2026-07-22): the directory
-- profile extends to images, bio, links, location, pronouns, and an
-- email whose visibility the owner controls. Two choices are carried
-- openly rather than slipped:
--
--   not evented · profile is presentation state, not record. Edits
--   are plain writes with no event row, by decision; the record's
--   fold-over-events claim does not extend to self-description. The
--   same standing applies to display_name (B-05).
--
--   crafts are inferred, not declared · no crafts column exists.
--   What a member practices is read from the record itself
--   (gatherings hosted, presence, opportunities, signatures) and,
--   when the S train opens, from contributions and patronage
--   activity. The profile view renders the inference; the schema
--   holds no self-declared taxonomy.
--
-- The email column is the one guarded cell: column privilege keeps
-- it out of every client select, and profile_email() serves it only
-- to the owner, or to an active member when the owner has said so.
-- Anchors: the directory as a member right per Bylaws §2.9, §1.13;
-- own-record reads per §18.1; the profile as self-controlled per the
-- B-05 acceptance ("a profile you control"). IM addendum, Tier B
-- under BP v1 §6, recorded for adoption into IM v0.2 alongside the
-- §9 additions of AM v0.1.
-- The storage half guards on the storage schema existing, so the
-- chain applies clean on CI substrates that carry no Supabase
-- storage.

create table profiles (
  agent_id      uuid primary key references agents(id),
  bio           text check (char_length(bio) <= 1200),
  links         jsonb not null default '[]'::jsonb,
  location      text check (char_length(location) <= 120),
  pronouns      text check (char_length(pronouns) <= 40),
  email         text check (char_length(email) <= 254),
  email_visible boolean not null default false,
  avatar_path   text check (char_length(avatar_path) <= 200),
  updated_at    timestamptz not null default now()
);
comment on table profiles is 'Self-description satellite of agents: presentation state, not record; edits are not evented by decision (B-06, 2026-07-22). One row per agent, owner-written. Bylaws §2.9, §1.13, §18.1.';
comment on column profiles.email is 'Guarded cell: column privilege withholds it from client selects; served only by profile_email() per the owner''s visibility choice.';

alter table profiles enable row level security;

-- links: an array of {label, url} pairs, at most six, http(s) only
alter table profiles add constraint profiles_links_shape check (
  jsonb_typeof(links) = 'array' and jsonb_array_length(links) <= 6
);

create or replace function profiles_touch() returns trigger
language plpgsql as $$
begin
  new.updated_at := now();
  return new;
end $$;
create trigger profiles_touch before update on profiles
  for each row execute function profiles_touch();

-- ---------- the matrix cells (AM v0.1 §5, profiles addendum) ----------
-- member: R · self W; applicant: self; public: nothing.
-- §2.9 the membership list as a member right; §18.1 own record
create policy profiles_member_read on profiles
  for select using (app_is_member() or agent_id = app_agent_id());
-- §1.13 the register; §18.1: each agent writes only their own row
create policy profiles_self_insert on profiles
  for insert with check (agent_id = app_agent_id());
-- §1.13 the register; §18.1: each agent writes only their own row
create policy profiles_self_update on profiles
  for update using (agent_id = app_agent_id())
  with check (agent_id = app_agent_id());

-- the guarded cell: grants are column-level only, because a
-- table-level SELECT would override any column revoke; email and
-- its switch move solely through the definer functions below.
-- Supabase default privileges grant ALL on new tables to anon and
-- authenticated at creation; strip that first or the column
-- discipline below is decoration (found on the live apply,
-- 2026-07-22; plain-postgres CI carries no such defaults)
revoke all on table profiles from anon, authenticated;
grant select (agent_id, bio, links, location, pronouns, email_visible, avatar_path, updated_at)
  on profiles to authenticated;
grant insert (agent_id, bio, links, location, pronouns, avatar_path)
  on profiles to authenticated;
-- agent_id rides the update grant because PostgREST upserts set every
-- supplied column; the with-check pins it to the asker, so the grant
-- concedes nothing
grant update (agent_id, bio, links, location, pronouns, avatar_path)
  on profiles to authenticated;

-- ---------- email, by the owner's word ----------
create or replace function public.profile_email(p_agent_id uuid)
returns text
language sql stable security definer
set search_path = public
as $$
  select p.email from profiles p
   where p.agent_id = p_agent_id
     and (p.agent_id = app_agent_id()
          or (p.email_visible and app_is_member()))
$$;
comment on function public.profile_email(uuid) is 'B-06: the guarded cell served on the owner''s terms: self always; an active member only when email_visible.';
revoke all on function public.profile_email(uuid) from public, anon;
grant execute on function public.profile_email(uuid) to authenticated;

create or replace function public.set_profile_email(p_email text, p_visible boolean)
returns void
language plpgsql security definer
set search_path = public
as $$
declare
  v_agent uuid := app_agent_id();
begin
  if v_agent is null then
    raise exception 'no agent bound to this session';
  end if;
  insert into profiles (agent_id, email, email_visible)
  values (v_agent, nullif(trim(p_email), ''), coalesce(p_visible, false))
  on conflict (agent_id) do update
    set email = excluded.email,
        email_visible = excluded.email_visible;
end $$;
comment on function public.set_profile_email(text, boolean) is 'B-06: the one write path for the guarded cell; the owner sets address and visibility together.';
revoke all on function public.set_profile_email(text, boolean) from public, anon;
grant execute on function public.set_profile_email(text, boolean) to authenticated;

-- ---------- avatars: a private shelf, owner-hung, member-seen ----------
do $$
begin
  if exists (select 1 from information_schema.tables
              where table_schema = 'storage' and table_name = 'buckets') then

    insert into storage.buckets (id, name, public)
    values ('avatars', 'avatars', false)
    on conflict (id) do nothing;

    -- §2.9 members see one another; §18.1 the owner sees their own
    drop policy if exists avatars_member_read on storage.objects;
    create policy avatars_member_read on storage.objects
      for select using (
        bucket_id = 'avatars'
        and (app_is_member() or app_is_applicant()
             or split_part(name, '/', 1) = app_agent_id()::text)
      );

    -- §1.13, §18.1: the owner hangs their own image, nobody else's
    drop policy if exists avatars_self_write on storage.objects;
    create policy avatars_self_write on storage.objects
      for insert with check (
        bucket_id = 'avatars'
        and split_part(name, '/', 1) = app_agent_id()::text
      );

    -- §1.13, §18.1: the owner replaces their own image, nobody else's
    drop policy if exists avatars_self_update on storage.objects;
    create policy avatars_self_update on storage.objects
      for update using (
        bucket_id = 'avatars'
        and split_part(name, '/', 1) = app_agent_id()::text
      );

    -- §1.13, §18.1: the owner takes down their own image, nobody else's
    drop policy if exists avatars_self_delete on storage.objects;
    create policy avatars_self_delete on storage.objects
      for delete using (
        bucket_id = 'avatars'
        and split_part(name, '/', 1) = app_agent_id()::text
      );
  end if;
end $$;
