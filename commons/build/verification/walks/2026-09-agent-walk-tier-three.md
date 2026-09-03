# Verification walk - Agent walk, tier three (9 cards) - agent-walked

Standing: evidence sheet, unsigned. Walked by a Fable 5.1 session under Nou's orchestration on 2026-09-03, against main at 27b3906 (the live `/intranet/hud/` served bytes identical to the worktree file, md5 3f37cb00). Every verdict below is the walker's proposal; a card is verified only when the steward reads its evidence and says the word (Verification Spec; instructions section 12). Nothing in this sheet changes a ledger mark.

Method: public pages fetched with `curl -sL`; signed-in surfaces rendered under the stub harness on fixture data (ports 8899 and 8898), driven through the Chrome DevTools Protocol so a view could be selected and a row clicked; renders in `/home/openclaw/shots/walk-X-38/` (not committed), emulated at 1280x900 unless stated, default light mode; GitHub Actions read through the REST API with a read token; the ledger's history read from `git log` over `rdm-ledger.yaml` in the worktree. No form was submitted, no sign-in link requested, no live row written. One anonymous read-only PostgREST call was made and is named under A-02.

## A-02 - The desk
claim: "The claim: a member can give a Direction from a page, watch what became of it, and read the rule behind a refusal, with no administrator standing in the middle."
steps:
- Rendered `http://localhost:8899/_boot.html#/intranet/direct/` under the stub harness, fixture data (`A-02-direct.png`, `A-02-arc.png`). The page renders as Todd Youngblood with the give form (brief, kind, code the agent may work in, button "Give the Direction") and a "Your Directions" arc. The fixture's one Direction renders as an arc card carrying kind, repository, time, and "event 00000000", with the state chip "given" and no beats beneath it. The stub's `direction_standing` fixture lacks the fields the page reads, so the standing row shows "undefined of undefined" for "yours still running" and "yours given today": a harness gap, not a page defect.
- The standing Direction d6e22f76-d6b0-4805-885e-68d0f90c96a2 was not read. An anonymous GET on `/rest/v1/events?id=eq.d6e22f76-...` returned 200 with an empty array: the row is not anon-readable, and the page's own text says it shows the giver their own Directions only. Reading its arc from given onward needs Todd signed in. No Direction was given: that would write to the live record.
- The rule behind a refusal, from the page source: the give form's footer says "Three things a Direction can never do: move money, reach any system outside the list above, or merge its own work into the cooperative's code. These limits are written in Common Agency §11" with a link to `/commons/agency/`. A refusal beat renders "Turned down. The rule it would have broken:" followed by the rule the verb returned (`p.rule`) as plain text, with "one of the standing limits" as the fallback when the verb sent none, and a refusal at give time shows the verb's own error text under the button. The rule's text is reachable from the page through the Common Agency link; the refusal beat itself cites the rule by name but does not link it. No refusal exists in the fixtures, so the beat was read in source, not rendered.
proposed verdict: deferred
one sentence: A-02 is deferred: the surface renders and the rule text is reachable from the page through Common Agency §11, but the standing Direction's arc from given onward and a rendered refusal need a signed-in person and a real event.
residue for the steward: sign in, read the arc of d6e22f76 and confirm it shows more than existence; if a refusal exists on the record, confirm its beat names a rule you can find at /commons/agency/ from the citation alone.

## TR-04 - The surface, deployed
claim: "The claim: the transducer is live at its address and stamps every view with the commit it was cut from, so a reader can tell whether the figures are today's."
steps:
- Fetched `https://techne.coop/intranet/hud/` (200); md5 3f37cb00baf2a401b4ed0a1534db22ed, identical to the worktree file at 27b3906. Rendered under the stub harness, fixture session (`TR-04-hud.png`); the HUD's figures come from the cut embedded in the page, not from the CIS.
- The stamp line, quoted from the render: "a dated cut of main · read 2026-09-03 at de4ca8914fc1 · current only by re-reading". The embedded snapshot's `generated` field reads "2026-09-03 at de4ca8914fc1". The stamp stays visible above all six views; the Succession render (`TR-10-succession-clean.png`) shows the same line.
- Commit list for main, read through the API: main's head is 27b3906, whose parent is de4ca89. 27b3906 is the gate's own commit "hud: cut retaken at de4ca89 (TR-03)", made by workflow run 88 at 06:40 UTC on 2026-09-03, so the stamp names the merge the cut was taken at and sits one commit behind head by construction, same day.
proposed verdict: holds
one sentence: TR-04 holds: the live page stamps "2026-09-03 at de4ca8914fc1", and de4ca89 is the parent of main's head, the head itself being the gate's refresh commit for that cut.
residue for the steward: none.

## TR-08 - The walk
claim: "The claim: the guided walk can teach someone who has never seen the estate what each view shows and what it refuses to show, in under three minutes."
steps:
- Rendered the HUD under the stub harness. The walk opens by itself on first load ("THE WALK · 1 OF 7", card "Volunteered attention") and is also reachable from "start here". Stepped it with "next" seven times through the DevTools Protocol; the counter ran 1 of 7 to 7 of 7 with no error (`TR-08-walk-7.png`).
- The seven cards, from the page's `WALK` array: "Volunteered attention"; "A tool alongside, not in place of"; "Journeys"; "Standing"; "Maturation"; "Tending"; "Composition". Five of the six views get a card; the Succession view has none in the array.
- The walk's text is about 259 words including its source lines. At a reading-aloud pace of 130 to 160 words a minute that is under two minutes of speech before any time spent looking; the timer and the reading aloud are the steward's.
- What the walker retained, as an agent's reading and not the card's test: Journeys shows each way in and where it stops, refusing to show people; Standing shows one cross-section, refusing to show time; Maturation shows how far each piece came, refusing to rank; Tending shows when work happened and which pile, refusing counts per person; Composition shows files by size and revision, refusing to treat size as merit. The walk did not teach what Succession shows or refuses; that view's own subtitle does ("a step back is a correction, kept visible").
proposed verdict: deferred
one sentence: TR-08 is deferred: the walk runs end to end in seven cards and reads well under three minutes by word count, but what a person retains is the card's test and only a person can say it.
residue for the steward: take the walk with a timer, say what each view shows and refuses, and note that the walk has no card for Succession.

## TR-10 - The seam
claim: "The claim: the succession view shows the flat layer and a piece's backward steps plainly enough that a reader finds them without being told where to look."
steps:
- Rendered the Succession view under the stub harness (`TR-10-succession-clean.png`, `TR-10-F01-panel.png`). The view opens with five metric tiles ("ledger revisions read 189", "transitions recovered 135", "corrections 3", "median days to verified 10", "holding their first mark 14") and a reading line, then the piece strips grouped by bed, 186 rows.
- The flat layer: the page presents it as the tile "holding their first mark · 14 · since the ledger's first day" and the sentence "14 pieces have held their first mark since the ledger's first day: that flat layer waits on a person adopting, attesting, or deciding, and is not a backlog." There is no separate strip under the main figure; the flat pieces sit in their bed groups as single-colour bars. Found by the walker in the first screen, reading the tiles; how long a person takes is theirs to time.
- Opened F-01's panel by clicking its row. The panel, quoted: "PIECE F-01 / Every state observed, in order. Days are floors at the ledger's grain. / 2026-07-10 · anticipated 12 days / 2026-07-22 · in-session 2 days / 2026-07-24 · verified 0 days / 2026-07-24 · in-session 0 days / 2026-07-24 · verified at least 41 days". The backward step (verified to in-session on 2026-07-24) is readable from the panel alone. The view's right-hand column before any row is clicked also lists "THE CORRECTIONS": "F-01 · 2026-07-24 verified → in-session", "X-01 · 2026-07-20 in-review → anticipated", "X-02 · 2026-07-24 verified → in-session".
proposed verdict: deferred
one sentence: TR-10 is deferred: the flat layer and F-01's backward steps are both on the view and the panel names the steps without the ledger, but the card's test is a reader finding them unprompted, and the card's own description of the flat layer as a strip under the main figure does not match the page, which shows it as a tile and a sentence.
residue for the steward: open the Succession view without hints, time the find, and say F-01's backward step from the panel; decide whether the card's "strip under the main figure" should be re-cut to the tile and sentence the page carries.

## TR-09 - The succession derivation
claim: "The claim: the history drawn for a piece is its true history: every state it actually held, in the order it held them, including the times it moved backwards and the times it moved twice in one day."
steps:
- Read the drawn histories from the embedded cut (the strips' titles and the panel) for F-01, B-02, A-02, and X-07 under the stub harness; the generator is `scripts/hud_cut.py`, whose `succession()` walks every revision of `rdm-ledger.yaml` and appends a state whenever a piece's mark or status differs from the last one seen.
- Recovered each piece's status independently from `git log --reverse -- rdm-ledger.yaml` in the worktree (189 revisions), reading the `status:` line under the address at every revision. F-01: 2026-07-10 anticipated (35dd3c7); 2026-07-22 open · in-session (b50b50c); 2026-07-24 open · verified (0dbaad1); 2026-07-24 open · in-session (608de1d); 2026-07-24 open · verified (eab7170). The drawn history for F-01 has the same five states in the same order, with the backward step drawn and the three moves on 2026-07-24 drawn as three.
- B-02 from git: anticipated 07-10, in-session 07-12, verified 07-12; drawn: the same three, the two moves on 07-12 drawn as two. X-07 from git: anticipated 07-10, in-review 07-20, verified 07-20; drawn: the same. A-02 from git: anticipated 07-27, in-session 07-27, delivered 08-13; drawn: the same, the two moves on 07-27 drawn as two.
- The view's tile reads "transitions recovered 135 · no day collapsed, no path smoothed" and 43 of 186 pieces carry two or more states on one day in the cut. The card asks for three pieces the walker remembers; the walker remembers none and compared four against the record instead.
proposed verdict: holds
one sentence: TR-09 holds: for F-01, B-02, X-07, and A-02 the drawn states match the ledger's own git history state for state, F-01's backward step is drawn as a step back, and every same-day pair is drawn as two.
residue for the steward: none, unless the steward wants to pick pieces from memory as the card asks.

## TR-02 - The generator
claim: "The claim: the generator reads the repository alone, with no key and no clock, so the same commit always yields exactly the same cut. The figures cannot shift with who ran it or when."
steps:
- Read the transducer-currency workflow through the API: workflow id 336510303, 88 runs since run 1 on 2026-08-17, all on push. Read the job logs of runs 88, 87, 86, 85, 4, 3, 2, and 1.
- Run 88 (id 33724314227, head de4ca89, 2026-09-03 06:40 UTC), job "the-cut", step "commit the refreshed cut, if the record moved": printed "[main 27b3906] hud: cut retaken at de4ca89 (TR-03)" and pushed "de4ca89..27b3906 main -> main". The record had moved, so the step committed rather than printing the sentence the card names. Every one of the eight runs read did the same: each is a merge, each merge moves the record, so every run so far has taken a fresh cut. The line "the cut is already current" is in the workflow's step source (quoted from the log: `echo "the cut is already current"`) but no run on the record has printed it, because the gate's own refresh commit does not trigger a run and no run has been re-run on an unmoved record.
- The controlled proof is the card's own quotation: "run today on a fresh clone of the public repository, no key: two runs at 42f1e52, SHA-256 7a98674f, both times, byte-identical." Read from the card; not reproduced.
- The generator's code reads only `git` output (`git log`, `git show`, `git ls-files`) and the ledger; `succession()` states "no clock is consulted" and takes dates from the commits.
proposed verdict: fails
one sentence: TR-02 fails as written: the step the card sends the reader to has never printed "the cut is already current" in 88 runs, because each run is a merge that moves the record, so the determinism witness the card promises on a run page is not on any run page.
residue for the steward: decide whether to re-cut the card to a witness that exists (the "current: the cut matches the record" line the audit step prints after the refresh, or a manual re-run of the workflow on an unmoved main), or to trigger one re-run so the sentence appears on the record.

## TR-03 - The currency gate
claim: "The claim: the figures on the transducer cannot go stale quietly. On every merge CI retakes the cut and then refuses to pass if what the page carries does not match the record beside it."
steps:
- Newest run of transducer-currency: run 88, id 33724314227, head de4ca89, conclusion success, 2026-09-03 06:40 UTC. Steps: "retake the cut at this merge" success; "commit the refreshed cut, if the record moved" success; "the audit · the cut beside this commit is current" success.
- The audit step's log, quoted: "current: the cut matches the record at de4ca8914fc1". The retake step printed "cut taken at de4ca8914fc1 (2026-09-03T00:40:19-06:00): 206 files, 183 pieces, 669 commits".
- The refusal on the record: run 81 (id 33658515366, head 1dc6199, 2026-09-02 17:01 UTC) failed at the audit step with "STALE: the embedded cut does not match the record at 65a80270c67d; run scripts/hud_cut.py and commit (TR-03)", exit code 1, when two merges landed 14 seconds apart and the second moved the record under the first's cut. Runs 82, 73, and 72 failed one step earlier ("error: could not apply ... hud: cut retaken", a rebase conflict between two gates pushing at once) and their audit step was skipped. The card's quoted controlled refusal ("seeded stale cut ... exits 1 with the STALE message") was read from the card, not reproduced.
proposed verdict: holds
one sentence: TR-03 holds: run 88 is green with the audit printing "current: the cut matches the record at de4ca8914fc1", and the refusal is on the record in run 81's STALE failure, not only in the card's quotation.
residue for the steward: none; note for the record that concurrent merges can fail the gate's commit step with a rebase conflict, which the next merge clears.

## U-15 - The intranet walkthrough, answered
claim: "The claim: the eleven asks the steward recorded while walking the intranet on 2026-08-07 were answered on the surface, not filed away."
steps:
- Signed out: rendered `http://localhost:8899/intranet/` without the fixture session (`U-15-gate-signed-out.png`). The gate reads "Member intranet / For cooperative members. Enter your email address and we will send a sign-in link. No password to manage. / continues to Overview / EMAIL ADDRESS / Send sign-in link". The "Link sent." line exists in `assets/shell.js` (the sent panel: "Link sent." then "Check your email and open the link to continue. You can close this tab." and a "Send another link" button). Not taken: pressing the button would send a sign-in email.
- Signed in under the stub harness, fixture data (`U-15-overview.png`, `U-15-overview-tall.png`): one Directory entry in the map and one "The members" door. Admissions appears only as a card under "The steward's desk" that links to `/commons/directory/` ("Admissions · the assigned hand", pending count 2 from fixtures, "Admit or decline someone from the panel at the top of the directory"); there is no separate Admissions door or page.
- Footer: bounding box left 0, width 1265 of a 1280 viewport (the rest is the scrollbar), so it spans the frame under both the sidebar and the content column.
- Door order against the map. Doors, in order: Agreements, Directory, the front door (join), Gatherings, Opportunities, Programs, Your share, Direction; then under the steward's desk: Admissions (to the directory), Treasury. Map, in order: Overview, Agreements, Directory, Gatherings, Opportunities, Programs, Your share, The Desk, Revenue, Direction, The record, Legal, Federation, The Commonplace Book, The walk, The Almanac. The member doors follow the map's order with the join form inserted after Directory (the map has no join entry). The map lists The Desk and Revenue before Direction; the doors put Direction among the member doors and Treasury under the steward's desk after it, and carry no Revenue door.
proposed verdict: deferred
one sentence: U-15 is deferred: one directory, no Admissions door beside it, and a footer spanning the frame all hold under the stub, but "Link sent" needs a link sent, and the steward must say whether Treasury sitting after Direction in the doors, against the map's Desk-Revenue-Direction order, is one order or two.
residue for the steward: request a link signed out and read the door; rule on the Treasury and Direction order between doors and map.

## X-21 - The walkthrough that needs two people
claim: "The claim: the two-person script is written well enough that two people who are not its author can walk it end to end without asking anyone a question."
steps:
- Fetched `https://techne.coop/commons/build/walkthrough/` (200, 35,449 bytes). Headings: "One Sitting, Two People"; "What is waiting, and what it is waiting for"; "The cast, the bench, the hour"; "Act one · the front door"; acts two to four; "After the walk · what is recorded, and by whom".
- Read act one in full: eight beats, each with a driver ("the second", "steward", "both"), a spoken sentence in italics for the proof beats, an instruction, and a named evidence item E-01 to E-08. The cast section settles the two roles, the evidence folder, and the hour ("Budget ninety minutes for the four acts"), and names one thing to settle before beat one: whether the second person joins as a real member or a named test identity.
- Agent's reading of legibility, beat by beat. Beats 1, 3, 5, 6, 7, and 8 name the page, the act, and the evidence and could be executed as written. Two beats would send the pair to the author: beat 2, "Pick up the phone. The intake notice should already be in the Telegram sink", presumes the steward knows which phone and which Telegram chat the sink is and that it is delivering that day, and names nothing to do if the notice is absent; beat 4, "Open the directory. The Admissions panel stands at the top", is executable, but beat 3 before it has the second person sign in as "applied" and then the steward admits in beat 4, while beat 5 onward assumes an admitted member, so the pair must know that the second person has to reload or re-sign in after admission (the intranet's own notice says "Reload the page first" for an unlinked sign-in) and the script does not say so.
- Not the card's test but seen: the walkthrough reads under the estate's retired vocabulary in places ("G-B attestation", "proof" used correctly; "the Proof Book" linked).
proposed verdict: deferred
one sentence: X-21 is deferred: act one is executable as written for six of eight beats by an agent's reading, with beat 2 (which phone, which sink, what if nothing arrives) and the reload after admission between beats 4 and 5 as the two beats a pair might have to ask about, and the judgement of a reader is the steward's to make.
residue for the steward: read act one as the second person and say whether beats 2 and 4 to 5 would stop you.

## Tally

Cards walked: 9. Proposed holds: 3 (TR-04, TR-09, TR-03). Proposed fails: 1 (TR-02). Deferred: 5.

- A-02 deferred: the standing Direction's arc and a rendered refusal need a signed-in person; the row is not anon-readable and giving a Direction would write to the live record.
- TR-08 deferred: what the walker retains is the test, and only a person can say it; the walk runs end to end and reads under two minutes by word count.
- TR-10 deferred: the find without hints and the saying aloud are a person's; also the card describes a strip the page does not have.
- U-15 deferred: "Link sent" needs a link sent, and the door order against the map needs a ruling.
- X-21 deferred: legibility as a reader is the steward's judgement; the agent's reading names two beats.

The one proposed fail, TR-02, rests on the card sending the reader to a log line that no run has printed; the generator's determinism is not in doubt from the code and the card's own quoted proof, only the witness the card names.

Not taken: no sign-in link was requested; no Direction was given; no form was submitted; no live row was written; the one live read was an anonymous GET that returned an empty array.

Page defects and card defects seen on the way, reported not fixed: the HUD's walk has no card for the Succession view; the TR-10 card describes the flat layer as "the strip under the main figure" while the page shows it as a tile and a sentence; the TR-02 card names a log line that has not appeared in 88 runs; the stub harness's `direction_standing` fixture lacks `live_now`, `live_bound`, `given_today`, and `day_bound`, so the desk's standing row renders "undefined of undefined" under the harness (harness, not page); the intranet map has no entry for the join form that the doors carry.

Checks run in this worktree at 27b3906 with this sheet added: `scripts/validate.py`: "validation passed (0 warning(s))", STATUS.md and index.json rewritten without change; `scripts/em_dash_audit.py`: "124 files, clean"; `scripts/almanac_audit.py`: "0 finding(s) over 183 addresses"; `scripts/verification_cards.py --check`: "cards.json is current".
