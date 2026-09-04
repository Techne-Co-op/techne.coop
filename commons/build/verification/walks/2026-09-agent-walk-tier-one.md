# Verification walk · Agent walk, tier one (11 cards) · agent-walked

Standing: evidence sheet, unsigned. Walked by a Fable 5.1 session under Nou's orchestration on 2026-09-02, against main at 08bc3d32daedde7140dbbca1a7c8f40a8bd8feda. Every verdict below is the walker's proposal; a card is verified only when the steward reads its evidence and says the word (Verification Spec; instructions section 12). Nothing in this sheet changes a ledger mark.

How this sheet was made. Public pages were read with `curl -sL` and rendered with headless Chromium at 1280x900 in the default mode (no `techne-mode` key in localStorage, so light). Signed-in surfaces were rendered under the stub harness (`scripts/cis-harness/stub.py`), which plants a fixture session as Todd Youngblood and answers every CIS call from fixtures; nothing reached the live CIS. GitHub Actions and pull requests were read through the REST API. The one anonymous PostgREST read was against the member-readable `events` endpoint and returned an empty set. Screenshots are under `/home/openclaw/shots/walk-X-38/` and are not committed. The cards are quoted from `commons/build/verification/cards.json`; the steward's own walk of this tier on 2026-08-26 (walk 02) is not consulted here, so this sheet is an independent reading.

## FORMATION-01 · The site stops saying it is operating
claim: "No page may claim the cooperative is operating or its instruments ratified."
steps:
- Step 1, `curl -sL https://techne.coop/legal/` and the render at `/home/openclaw/shots/walk-X-38/FORMATION-01-legal.png`. The page is now titled "The filed instruments." and carries three rows (Articles of Organization, EIN, Trade Name registration), every one marked "Filed". The page says of that mark: "It is the only mark on this page, because only filed instruments are published here." The instrument rows with the drafted mark are no longer on /legal/; the page points members to "the legal shelf on the intranet" (/intranet/legal/). Rendered under the stub harness, fixture data, /intranet/legal/ carries the Bylaws and Membership Agreement rows marked "Drafted" (seventeen "Drafted" marks on the shelf, including the commentary rows) and the sentence "Bylaws and the Membership Agreement remain Drafted, Schedule A is still unexecuted"; screenshot `/home/openclaw/shots/walk-X-38/FORMATION-01-intranet-legal.png`. So the step's check is met on the shelf, not on /legal/ where the card places it.
- Step 2, https://techne.coop/legal/#formation. The anchor `id="formation"` exists. The notice reads, in part: "RegenHub, LCA has been called to order. The Articles are filed with the Colorado Secretary of State. The board was seated at its special meeting of August 14, 2026, confirmed August 19, 2026, and its officers are in office [...] Member ratification of the Bylaws and Membership Agreement is anticipated, not yet held, and no member has been admitted." The counsel memo at /legal/counsel-memo/ says of the instruments: "received verbal ratification at the June 2026 board meeting, pending your feedback before execution." The notice's "board-adopted, with member ratification anticipated" is consistent with the memo; whether it is "in the counsel memo's words" is a reading the steward should make, since the two texts differ in wording.
- Step 3, `curl -sL https://techne.coop/` and `https://techne.coop/commons/`, grepped for operating, ratified, in effect. The front page says "are adopted and authorized by the board; member ratification is anticipated. No member has been admitted yet". /commons/ uses "operates" only of the membership relay ("a membership relay the cooperative operates") and of terms a book "operates on"; no sentence on either page says the cooperative is operating or its instruments ratified.
proposed verdict: holds
one sentence: FORMATION-01 holds: no public page claims the cooperative operating or its instruments ratified, and the drafted marks now live on the intranet legal shelf rather than on /legal/, which the card's first step does not anticipate.
residue for the steward: read the formation notice against the counsel memo and say whether it is in the memo's words; decide whether the card's first step should be re-pointed at /intranet/legal/.

## DOC-01 · The correction log opens
claim: "The correction log holds the estate's known wrong claims, each with its standing."
steps:
- Step 1, `curl -sL https://techne.coop/legal/corrections/`, 200; render at `/home/openclaw/shots/walk-X-38/DOC-01-corrections.png`.
- Step 2, counted `div.item` blocks by section: eighteen under "Open items" and three under the closed section, twenty-one in all against the card's "eight at drafting". Every one of the twenty-one names its location and date, has a "Reads" and a "But" or "What the instrument says" row, and every open item carries a "What closes it" row naming the closing act and its owner (the standing lines read "Open · for counsel", "Open · for the board", "Open · for the steward", "Reading · for the steward", and so on).
- Step 3, closed items. DOC-01·04, ·06 and ·07 in the closed section each carry a "Closed by" row, for example ·06: "Closed by Both surfaces corrected: the instrument named properly, the directors claim removed, and the document number carried on the index." DOC-01·17, ·18 and ·19 are marked "Closed · corrected 2026-08-21" but sit in the "Open items" section; each names its closing act in its "What closes it" row followed by "Done 2026-08-21" (·17: "The roster published on the legal shelf at The board and its officers"). No item is marked closed without a named act. That three closed items sit under the open heading is a placement defect on the page, not a missing act.
proposed verdict: holds
one sentence: DOC-01 holds: twenty-one items, every one stating what was claimed, what the record holds, and who closes it, and every closed item naming its closing act, with three closed items still listed under the open heading.
residue for the steward: none for the verdict; the placement of DOC-01·17 to ·19 under "Open items" is reported as a page defect.

## U-10 · The front door tells the truth
claim: "A visitor must reach class self-selection in one step and enroll along an open track."
steps:
- Step 1, https://techne.coop/ links to /participation/ (hrefs found: /participation/, /participation/#community, /participation/#cooperative, /participation/#coworking), one step; render `/home/openclaw/shots/walk-X-38/U-10-front.png`.
- Step 2, https://techne.coop/participation/ carries Community Participant ("$25, $50, or $100 a month"), Co-working Participant ("$250 a month at a hot desk. $500 and up for a dedicated desk"), Cooperative Member ("$100 one-time share [...] plus $100" a year in dues), and Investor Member (capital, no vote, terms by the board); render `/home/openclaw/shots/walk-X-38/U-10-participation.png`.
- Step 3, https://techne.coop/commons/join/. Four radio inputs (`way-community`, `way-coworking`, `way-cooperative`, `way-investor`), each wrapped in its own `label` element; `name`, `email` and `note` are bound by `label for=`; a status line `div#form-status` with `aria-live="polite"` and an error notice with `role="alert"`. Community and Co-working are marked "open now"; render `/home/openclaw/shots/walk-X-38/U-10-join.png`. The form was not submitted.
- Step 4, the join page says the Hub Participation Agreement "is drafted and still with counsel" and that the Participation Framework "is listed with every other instrument on the legal shelf", linking /legal/ and /legal/#formation; no instrument text is restated. Class self-selection is the join form; the participation page is a comparison surface.
proposed verdict: holds
one sentence: U-10 holds: the front page reaches /participation/ in one click, four classes with costs are compared there, and the join form offers labelled class selection with a live status line and links the instruments rather than restating them.
residue for the steward: none.

## U-07 · The parked door
claim: "The Share door is parked honestly: it names what is absent and whose act it waits on."
steps:
- Step 1, rendered under the stub harness, fixture data. The intranet map at `http://localhost:8899/_boot.html#/intranet/` carries the "See your share" group with the door "Your share" linking /intranet/share/ (render `/home/openclaw/shots/walk-X-38/U-07-map.png`); the share page rendered at `/home/openclaw/shots/walk-X-38/U-07-share.png`.
- Step 2, the page reads: "using whichever counting rules the Board has put in force. It has not put any in force yet, so every figure is zero." and "There is no form to fill in until the Board adopts the rules." and, in the notice, "The Board has not adopted COUNTING-RULES v1 [...] so every figure below is zero because there is no rule to count by, not because you have done nothing." It links the counting rules at /commons/patronage/counting-rules/ and the patronage document. The absence is placed on the Board's pending act and nothing suggests an administrator withholding. The page does not name S-01 or S-02 anywhere in its source (`grep -c 'S[-‑–]0[12]' intranet/share/index.html` returns 0, and no U-07 either); the file was last rewritten 2026-09-02 by U-32.
proposed verdict: fails
one sentence: U-07 fails on the card's second step as written: the page places the absence on the Board's unadopted counting rules and links them, but it no longer names S-01 or S-02, so one of the three things the step asks for is not on the page.
residue for the steward: decide whether the claim holds in plain words without the packet addresses (the page says what is absent and whose act it waits on) or whether the addresses must return; the walker proposes the verdict against the step as written.

## P-12 · One notice, one place
claim: "One formation notice, one form: a footer line everywhere, no strips."
steps:
- Step 1, fetched /legal/, /legal/counsel-memo/ and /legal/corrections/.
- Step 2, the only formation-related classes on each of the three pages are `formation-foot` (and `formation-note` for the long-form notice on /legal/); no `formation-strip` or strip block. The footer line is identical on all three: "Called to order RegenHub, LCA is called to order: the board is seated and the governing instruments are board-adopted, with member ratification anticipated. Read the formation notice, which is right wherever a page disagrees with it." The same footer line appears on /, /commons/, /participation/, /commons/patronage/ and /commons/treasury/.
- Step 3, /legal/#formation: the long-form notice under "Where the cooperative stands" is intact (quoted under FORMATION-01 step 2); render `/home/openclaw/shots/walk-X-38/P-12-counsel-memo.png` for the memo.
proposed verdict: holds
one sentence: P-12 holds: the three legal pages carry the one-line footer notice and no strip, and the long-form notice at /legal/#formation is intact.
residue for the steward: none.

## X-13 · The documents agree
claim: "The three module documents agree with the built estate."
steps:
- Step 1, https://techne.coop/commons/patronage/ names /intranet/share/ eight times, including "the fold surface address follows the built door at /intranet/share/ (U-07)" and S-02's deliverable "/intranet/share/ over capital_accounts"; render `/home/openclaw/shots/walk-X-38/X-13-patronage.png`.
- Step 2, https://techne.coop/commons/treasury/ says "the deployed map (U-03) settled the public name as plain Treasury, with The Desk as its door." The shell's sidebar (intranet/index.html and every intranet page) carries a "Treasury" group with the door "The Desk" linking /intranet/treasury/, and the stub render of the map shows "TREASURY / The Desk"; render `/home/openclaw/shots/walk-X-38/X-13-treasury.png`.
- Step 3, amendment lines. Patronage: chip "amended 2026-07-27 · the address follows the built door" in the paragraph citing U-07, and the colophon "2026-07-22, amended 2026-07-27, re-cut August 2026, v0.4 against COUNTING-RULES v2 on issue #212, 2026-08-21". Treasury: chip "amended 2026-07-27 · naming settled by the record" in the paragraph citing U-03, and the colophon "2026-07-22, amended 2026-08-05, re-cut 2026-08-13". Each chip carries a date; the piece address (U-07, U-03) sits in the sentence the chip closes rather than inside the chip. The card names three module documents and points at two; the third was not identified and not walked.
proposed verdict: holds
one sentence: X-13 holds on the two documents the card points at: patronage names /intranet/share/, treasury's "The Desk" matches the shell, and each amendment line is dated with its piece address in the sentence beside it.
residue for the steward: name the third module document and check its amendment lines; say whether an address beside the chip rather than inside it satisfies the step.

## A-01 · The direction rail
claim: "Directions enter by verb only; refusals cite rules. Proven by the RLS probe matrix."
steps:
- Step 1, PR 75 "A-01: the direction rail", merged 2026-07-27 (https://github.com/Techne-Co-op/techne.coop/pull/75); its body lists ten probe cells including "direct insert denied, verb entry for a member, applicant denied". `commons/authority-map/0017_direction_rail.sql` on main defines `give_direction(...)` as `security definer` with refusals that cite their rules, for example "Direction is a member act: an active membership holds the pen (AGY section 6)." and "A Direction is one of four kinds, draft, build, survey, or answer (AGY section 7)." The probe cells live in `scripts/rls_probe.py` lines 503 to 511: `direction-member-direct-insert-deny` (expects `write_deny`, "the verb is the only door"), `direction-member-verb-ok`, `direction-applicant-deny`. The rls-audit job, step "probe the matrix", is green in verify run #612 (id 33658539674, main at 65a8027, 2026-09-02).
- Step 2, the live Direction d6e22f76. An anonymous read of `events?kind=like.direction.*` returned `[]` (HTTP 200): the row is member-readable only, and this walker holds no member session. Not read.
proposed verdict: deferred
one sentence: A-01 is deferred: the verb, its rule-citing refusals, and the bare-table refusal are on main and the probe matrix is green in run #612, but the standing Direction d6e22f76 can only be confirmed alive by a signed-in person.
residue for the steward: sign in, open the Direction door, confirm d6e22f76 is your Direction and lives, and cite the id aloud.

## L-03 · The ledger speaks
claim: "The ledger and validator evolved together; verified entries are byte-stable."
steps:
- Step 1, `GET /repos/Techne-Co-op/techne.coop/actions/runs?branch=main`. The latest verify run on main is #612, id 33658539674, on commit 65a8027, 2026-09-02, conclusion success. Job "ledger-validate", step "validate packet ledger": success.
- Step 2, main's head at the time of this walk is 08bc3d3 ("hud: cut retaken at 1dc6199 (TR-03)"); the only run on that sha is "pages build and deployment" (#397, success). Run #612 is therefore one commit behind head. `validate.py` run locally in this worktree at 08bc3d3 is recorded in the tally below.
proposed verdict: holds
one sentence: L-03 holds: ledger-validate is green on main's latest verify run, #612 on 65a8027, one commit behind head, and the validator is green locally at head.
residue for the steward: say the run number aloud; note the head commit carried no verify run.

## X-18 · The cards answer to the ledger, the ledger to the repository
claim: "The audits have teeth, and the teeth are tested."
steps:
- Step 1, verify run #612, job "style-lint", success, with steps 10 "the almanac audit still refuses (X-18)" and 11 "the cards answer to the ledger, the ledger to the repository (X-18)" both success, followed by step 12 "the walk's cards answer to the run-book (X-28)".
- Step 2, `scripts/almanac_audit.py` on main defines `self_test()` (line 156) and the `--self-test` flag (line 211); `.github/workflows/verify.yml` runs `python3 scripts/almanac_audit.py --self-test` (line 327) then `python3 scripts/almanac_audit.py` (line 334), and checks out with full history because "the almanac audit's third check reads merge commits" (line 265).
proposed verdict: holds
one sentence: X-18 holds: style-lint in run #612 runs the almanac audit's self-test and the audit itself, both green, and both are wired in verify.yml.
residue for the steward: none.

## X-19 · The ledger answers to the repository
claim: "Twenty-four wrong marks were corrected and the ledger now answers to the repository."
steps:
- Step 1, PR 127 "X-19: the ledger answers to the repository", merged 2026-08-13 (https://github.com/Techne-Co-op/techne.coop/pull/127). Its body: "Twenty-four marks corrected." with "Seven merged pieces stood at drafted (P-07 through P-12, MM-01)", "Seventeen stood at open · in-session", "Two merged pieces held no address at all. FORMATION-01 (PR #120) and DOC-01 (PR #122)".
- Step 2, the third check (merged branch names against the ledger) is the same step 11 of style-lint in run #612, green, and verify.yml's checkout comment names it as reading merge commits.
proposed verdict: holds
one sentence: X-19 holds: the PR records the twenty-four corrections by class, and the branch-against-ledger check runs in CI and is green on run #612.
residue for the steward: none.

## X-11 · The export follows the substrate
claim: "Export views follow the substrate; CI refuses a column left behind."
steps:
- Step 1, verify run #612: job "db-verify" success (steps "assert · append-only (Law I)" through "assert · rls everywhere, denying (Law V)"), job "restore-test" success (steps "apply substrate", "load restore baseline", "verify row counts match baseline", "verify fold matches (capital_accounts)", "sha comparison", "export machinery (X-03)"). Job "gate-rehearsal", step "rehearse the gates": success.
- Step 2, PR 67 "X-11: the export follows the substrate", merged 2026-07-27 (https://github.com/Techne-Co-op/techne.coop/pull/67). Its note: "the gate rehearsal now applies 0004 + 0014 and adds beat 14, which compares every export.* view against its public.* base table and fails if any column is missing." On main, `scripts/gate_rehearsal.py` line 369 carries "beat 14 · the export carries the whole row (X-11)". The original regression run from July was not located through the API listing; the PR note is what was read.
proposed verdict: holds
one sentence: X-11 holds: db-verify and restore-test are green on run #612, and the PR note and beat 14 in the gate rehearsal are the refusal case, green in the same run.
residue for the steward: none.

## Tally

Cards walked: 11. Proposed holds: 9. Proposed fails: 1. Deferred: 1.

- U-07 fails as proposed: the share page no longer names S-01 or S-02.
- A-01 deferred: the live Direction d6e22f76 needs a signed-in person.

Page defects seen on the way, reported not fixed: DOC-01·17, ·18 and ·19 are marked closed and listed under "Open items" on /legal/corrections/; FORMATION-01's first step points at /legal/ for drafted rows that now live on /intranet/legal/; the "transducer-currency" workflow is failing on main (runs #81 and #82, 2026-09-02), outside this tier's cards.

Checks run in this worktree at 08bc3d3 with the X-38 packet added: `scripts/validate.py` reported "index.json was stale or missing; refreshed" on its first run and rewrote STATUS.md, index.json and the almanac counts, then "validation passed (0 warning(s))" over 180 packets; `scripts/em_dash_audit.py`: "120 files, clean"; `scripts/almanac_audit.py`: "0 finding(s) over 180 addresses", and its `--self-test`: "0 failure(s) over 5 case(s)"; `scripts/verification_cards.py --check`: "cards.json is current".

## Addendum · 2026-09-04 · the three page defects answered (X-39)

Added under X-39 against main at e10ce84. The walk above is not rewritten; this section answers its last paragraph and nothing else. No verdict, no ledger mark, and no claim on any page changes here.

**DOC-01, the placement.** DOC-01·17, ·18 and ·19 are moved from "Open items" to "Struck and closed" on /legal/corrections/, and the closed section carries a dated change note saying they moved and that their text was not rewritten. The walk's reading stands: this was a placement defect on the page, not a missing act.

**FORMATION-01, the pointer.** The card's first step now sends the walker, signed in, to /intranet/legal/ for the instrument rows carrying the drafted mark, and says that those rows moved off /legal/, which carries the filed instruments alone. The tier-one lead now names FORMATION-01 among the cards that need a sign-in, beside U-07 and X-13. `commons/build/verification/cards.json` was regenerated by `scripts/verification_cards.py`; the run-book stays the authored source.

**transducer-currency, runs #81 and #82.** Read, not repaired, because the cause was two merges landing fourteen seconds apart and not a defect in the gate. PR #277 merged at 1dc6199 and PR #278 at 65a8027 on 2026-09-02, and the concurrency group serialised the two runs rather than cancelling either.

- Run #81 (id 33658515366, head 1dc6199) regenerated the cut, committed it as "hud: cut retaken at 1dc6199", then `git pull --rebase origin main` picked up 65a8027 and rebased that commit onto it, pushing 08bc3d3. The audit step then read the working tree it had just rebased and reported, correctly, `STALE: the embedded cut does not match the record at 65a80270c67d`. The cut the job computed was true of the commit it checked out and false of the commit it ended on.
- Run #82 (id 33658539590, head 65a8027) regenerated its own cut, committed "hud: cut retaken at 65a8027", and failed one step earlier: `git pull --rebase origin main` hit `CONFLICT (content): Merge conflict in intranet/hud/index.html` against run #81's push, since both jobs had rewritten the same line. The audit step was skipped.

Both failures are the same race and neither left the estate stale. The next push retook the cut: run #83 (0b80eb1) and run #84 (c39a6e0) are green, and every run since through #94 (c142601) is green. `python3 scripts/hud_cut.py --check` in this worktree at e10ce84 returns "current: the cut matches the record at c14260122a20". The cause does not persist, so this batch leaves the workflow alone. What would make it persist is the same pattern again, two merges to main inside the gate's run time; if that recurs, the fix is the gate's to make, not this page's, and it belongs to TR-03.
