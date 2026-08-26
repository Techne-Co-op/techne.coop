-- 0030_verdict_rail.sql · X-32 · the verdict rail
--
-- Decision: the steward's direction (2026-08-26, DM), after his walk
-- of tier one had to be carried into the record by copying text out
-- of a browser and pasting it into a chat. His question was the
-- right one: if the goal is a cybernetic LCA, why is the walk page
-- not queryable. This migration is the answer's write half.
--
-- The distinction the walk surface (X-28) collapsed, restated:
--
--   A verdict is testimony, not adoption. "The ledger moves by pull
--   request" is a rule about adoption and it stands: a mark is an
--   act, and a human carries it. It does not follow that the
--   testimony must go unrecorded. What a member saw when they walked
--   a piece is exactly the kind of thing a record should hold, and
--   holding it moves nothing on its own.
--
--   Verb-only by construction. events_scoped_insert (0002, narrowed
--   at 0024) admits members to signature, registration, opportunity
--   and gathering kinds; verdict.* is not among them, so the
--   deployed policy set already refuses the direct write and this
--   migration widens nothing. The verb is the only door (AM v0.1
--   section 7), the same shape A-01 gave the direction rail.
--
--   No read widening, deliberately. Every verdict.spoken event
--   carries the speaking member as agent_id, so the standing
--   events_read policy (0002) already shows a walker their own walk
--   and shows directors and officers all of them. That is enough for
--   the board to query the walk and for a walker to resume one. It
--   is NOT enough for members to read each other's verdicts. Whether
--   the walk is common to the membership is a governance question
--   about what the cooperative shows itself, and it is not taken
--   here. Adding it later is one policy, no change to this verb.
--
--   The sentence is required. The run-book has always warned that a
--   verdict without a sentence tells the record what happened and
--   not what was seen. A warning that the record does not enforce is
--   a suggestion. Here it is a refusal.
--
--   Speaking again is not an error. A piece may be walked in more
--   than one sitting, by more than one member, and a walker may
--   revise. Each speaking is its own event; nothing is overwritten.
--   The latest un-corrected speaking by a member about a piece is
--   that member's standing verdict, which is how the rest of the
--   record already reads itself (see the AGY-ESTATE lookup in 0017).
--   Corrections use the standing corrects column, not an update.
--
--   The verb does not know the ledger. Addresses live in
--   rdm-ledger.yaml and the cards in commons/build/verification/,
--   neither of which the database reads. So the verb checks the
--   shape of an address and not its existence, and the walk surface,
--   which does hold the card list, refuses an unknown address before
--   it ever calls. A verdict against a retired address is a stale
--   trace, not a corrupt one, and the reading side can say so.
--
-- Anchors: X-28 (the walk surface), A-01 and 0017 (the verb pattern),
-- AM v0.1 section 7, Bylaws sections 18.1 and 6.2.1 (events_read).
-- Not adopted; drafted. Applied to the live CIS by the steward.

-- ---------- the verdict act ----------
create or replace function record_verdict(
  p_address  text,
  p_verdict  text,
  p_sentence text,
  p_walk     text default null
) returns uuid
language plpgsql security definer set search_path = public as $$
declare
  v_actor    uuid := app_agent_id();
  v_address  text := upper(btrim(coalesce(p_address, '')));
  v_verdict  text := lower(btrim(coalesce(p_verdict, '')));
  v_sentence text := nullif(btrim(coalesce(p_sentence, '')), '');
  v_walk     text := nullif(btrim(coalesce(p_walk, '')), '');
  v_id       uuid;
begin
  if v_actor is null then
    raise exception 'Sign in first: no agent is bound to this session (B-01).';
  end if;

  if not app_is_member() then
    raise exception 'A verdict is a member act: walking a piece and saying what you saw is membership work (X-28).';
  end if;

  if v_address = '' then
    raise exception 'A verdict names the piece it concerns: give the address on the card.';
  end if;

  if v_address !~ '^[A-Z][A-Z0-9]*(-[A-Z0-9]+)*$' then
    raise exception 'Address % is not the shape of a ledger address, for example U-09 or FORMATION-01.', v_address;
  end if;

  if v_verdict not in ('holds', 'fails', 'not ready', 'deferred', 'attested') then
    raise exception 'A verdict is one of five words, holds, fails, not ready, deferred, or attested (X-28); % is not one of them.', v_verdict;
  end if;

  if v_sentence is null then
    raise exception 'A verdict needs a sentence: what you saw, in your words. A verdict without one tells the record what happened and not what was seen (X-28).';
  end if;

  if char_length(v_sentence) > 2000 then
    raise exception 'The sentence runs to % characters and the bound is 2000: say what you saw, not everything you know.', char_length(v_sentence);
  end if;

  insert into events (occurred_at, actor_agent_id, kind, agent_id, payload)
  values (
    now(), v_actor, 'verdict.spoken', v_actor,
    jsonb_build_object(
      'address',  v_address,
      'verdict',  v_verdict,
      'sentence', v_sentence,
      'walk',     v_walk
    )
  )
  returning id into v_id;

  return v_id;
end $$;
comment on function record_verdict(text, text, text, text) is
  'A member''s verdict on a walked piece enters the record: one verdict.spoken event concerning the speaking member (X-28). Testimony, not adoption; the ledger mark still moves by pull request. The sentence is required. The verb is the only door; refusals cite their rules (X-32).';
revoke execute on function record_verdict(text, text, text, text) from public, anon;
grant execute on function record_verdict(text, text, text, text) to authenticated;

-- ---------- reading the walk back ----------
-- One row per member per address: their latest un-corrected speaking.
-- The view carries no policy of its own; it reads events and inherits
-- events_read, so a walker sees their own walk and directors and
-- officers see every walk. Nothing is widened by defining it.
create or replace view standing_verdicts
with (security_invoker = true) as
select distinct on (e.agent_id, e.payload->>'address')
  e.id            as event_id,
  e.agent_id      as walker_agent_id,
  e.payload->>'address'  as address,
  e.payload->>'verdict'  as verdict,
  e.payload->>'sentence' as sentence,
  nullif(e.payload->>'walk', '') as walk,
  e.occurred_at,
  e.recorded_at
from events e
where e.kind = 'verdict.spoken'
  and not exists (select 1 from events c where c.corrects = e.id)
order by e.agent_id, e.payload->>'address', e.recorded_at desc;
comment on view standing_verdicts is
  'The latest un-corrected verdict each member has spoken about each address (X-32). Reads through events_read: a walker sees their own walk, directors and officers see all of them. A row is testimony and not a mark; the ledger is the mark.';
