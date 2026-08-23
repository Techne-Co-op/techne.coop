-- 0028_phone_bindings.sql · SMS-03 · the binding table minted
-- The stop card from issue #191 said schema against the live CIS
-- needs a named human. The steward took it up on 2026-08-23 (DM,
-- 04:07 UTC: "you should have credentials for the migrations work
-- yourself. Please merge under your grant and begin build."). This
-- migration mints the sketch from the SMS-02 design page
-- (/commons/build/sms-bindings/, §4) without structural change.
--
-- A binding is a member's twice-signed claim: this person receives
-- at this number (proven by receiving a challenge code over the
-- co-op line) and this person signs with this key (proven by the
-- Nostr signature on the reply that carries the code back). The row
-- stores the evidence trail: the challenge's phone_events id and
-- the request/response Nostr event ids. Fully replayable from the
-- two logs.
--
-- Sibling of phone_events, not a column on profiles, for the
-- reasons 0026 recorded: state and evidence do not fit a column,
-- and the deferred verified-phone column becomes a view over this
-- table if it ever lands.

create table phone_bindings (
  id                 uuid primary key default gen_random_uuid(),
  member_pubkey      text not null check (member_pubkey ~ '^[0-9a-f]{64}$'),
  peer_e164          text not null check (peer_e164 ~ '^\+[1-9][0-9]{7,14}$'),
  status             text not null default 'pending'
                     check (status in ('pending','verified','revoked')),
  code_hash          text,
  challenge_event_id uuid references phone_events(id),
  request_event_id   text,
  response_event_id  text,
  buzz_channel_id    text,
  requested_at       timestamptz not null default now(),
  verified_at        timestamptz,
  revoked_at         timestamptz,
  revoke_reason      text
    check (revoke_reason is null or
           revoke_reason in ('sms_stop','member_request','steward','expired'))
);
comment on table phone_bindings is
  'SMS-03: verified bindings between a member''s Nostr key and an E.164 number, minted from the SMS-02 design (§4). One live binding per number and per key; revoked rows accumulate as history. The evidence for a binding is the challenge row in phone_events plus the two member-signed Nostr events.';
comment on column phone_bindings.code_hash is
  'SHA-256 of the one-time challenge code. Set while pending; cleared on verify. The plaintext code is never stored.';
comment on column phone_bindings.buzz_channel_id is
  'The dedicated private Buzz channel created on verification. Text, not uuid: the relay names channels with its own id scheme.';

create unique index phone_bindings_live_e164
  on phone_bindings (peer_e164) where status = 'verified';
create unique index phone_bindings_live_pubkey
  on phone_bindings (member_pubkey) where status = 'verified';
create index phone_bindings_peer_idx on phone_bindings (peer_e164, status);

alter table phone_bindings enable row level security;

-- Two narrow hands, per the design's role split (§4):
--
-- phone_router: the routing path. May learn who is bound and to
-- which channel, nothing else, so a leak of the router's key
-- discloses the roster but cannot forge, revoke, or read messages.
create role phone_router nologin noinherit;
grant phone_router to authenticator;
grant select on table phone_bindings to phone_router;
-- Anchor: reading a member's own standing to route their own
-- messages is ministerial recordkeeping (Bylaws v2.1 Art. XV);
-- the router sees only verified rows, never pending secrets.
create policy phone_router_select on phone_bindings
  for select to phone_router
  using (status = 'verified');

-- phone_binder: the ceremony service. Creates pending rows, flips
-- them to verified or revoked, and must read pending rows to check
-- a code hash. No DELETE: revocation is a status, history stays.
create role phone_binder nologin noinherit;
grant phone_binder to authenticator;
grant select, insert, update on table phone_bindings to phone_binder;
-- Anchor: recording and revoking a member's own channel binding is
-- the member's act on their own record (Bylaws v2.1 Art. XV); the
-- binder executes the member's twice-signed ceremony and nothing
-- of its own.
create policy phone_binder_all on phone_bindings
  for all to phone_binder
  using (true) with check (true);
