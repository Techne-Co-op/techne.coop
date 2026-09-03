# Verification walk - Tier two - the lexicon and the ledger - agent-walked

Standing: evidence sheet, unsigned. Walked by a Fable 5.1 session under Nou's orchestration on 2026-09-03, against main at 654a796 (the live site served the same bytes for every page checked: `/commons/build/lexicon/`, `/commons/build/`, `/commons/`, and `/legal/` were byte-identical to the worktree). Every verdict below is the walker's proposal; a card is verified only when the steward reads its evidence and says the word (Verification Spec; instructions section 12). Nothing in this sheet changes a ledger mark.

Method: public pages fetched with `curl -sL` and read as text; renders taken with headless Chromium at 1280x900 into `/home/openclaw/shots/walk-X-38/` (not committed); signed-in surfaces rendered under the stub harness on fixture data; GitHub read through the REST API with a read token; the ledger read from the worktree file `rdm-ledger.yaml`. No form was submitted, no message sent, no live row read or written.

## L-01 - Lexicon v2
claim: "The claim: the estate keeps one dictionary, and a word it has stopped using still answers to the word that replaced it."
steps:
- Fetched `https://techne.coop/commons/build/lexicon/` (200, 43,111 bytes). Render: `/home/openclaw/shots/walk-X-38/L-01.png`.
- Looked up the five words. Each carries its own definition entry on the page: piece ("The unit of work: one complete thing a pair of hands can make in a session, carrying an address, an intent, citations, a readiness condition, a deliverable, an acceptance, and its honest status."), bed ("A prepared ground where ordered pieces grow toward their proof"), proof ("The human act that closes a bed"), graft ("The act by which an adopted module joins its pieces into the Almanac"), tally ("The reading computed over events").
- Concordance table at section 9. Row for packet reads retired "packet", evolved "piece", note "unit of work; one piece per branch". Row for gate reads retired "gate", evolved "proof", note "the Gate Book becomes the Proof Book; G addresses unchanged". Fourteen rows in the table, including train to bed, splice to graft, fold to tally, slice to capability, emits to yields.
proposed verdict: holds
one sentence: L-01 holds: all five working words carry a definition and the concordance names piece for packet and proof for gate.
residue for the steward: none.

## L-02 - The Almanac
claim: "The claim: the Almanac speaks the current vocabulary throughout, and a retired word survives on it only inside a quotation of an older record."
steps:
- Fetched `https://techne.coop/commons/build/` (200, 186,551 bytes). Render: `/home/openclaw/shots/walk-X-38/L-02.png`.
- Read three bed narrations: the Ground ("The bed the beds are made in"), Belong ("Pieces grow in order; the proof closes the bed"), Gather ("then the proof"). No retired word in any of the three narrations. Agent's reading.
- Find-on-page for packet (case-insensitive, whole word) over the page text: 3 hits, all in card intent lines, none marked as a quotation. G0's card reads "Security floor attested as an event per VS v1 §6. Gate: human attestation recorded. Opens every slice train." (the ledger's own intent field for G0 reads "Opens every slice train."; the page adds "Gate: human attestation recorded." from the ledger's gate field). X-01's card reads "(error_log as its own follow-on packet)"; that phrase appears once in the ledger, in X-01's resolution, not in its intent. X-07's card reads "a packet whose status has opened must not carry an unresolved escalation card"; that sentence is in X-07's resolution in the ledger. G0's card ready line reads "slice trains open".
- Find-on-page for slice: 3 hits (G0 intent, G0 ready line, U-03 intent "the five-slice draft"). Find-on-page for gate in the old sense: G0's "Gate: human attestation recorded."; every other hit is the sign-in gate, the auth gate, or the CI gate, which are current senses.
- Also seen, outside the card's three words: SUB-01's card reads "Emits repo tree, validator, generated index.json and STATUS.md" and SUB-02's reads "the governing emissions"; the concordance retires emits for yields.
proposed verdict: fails
one sentence: L-02 fails as the card is written: packet, slice, and gate in the old sense each appear in card intent lines for G0, X-01, X-07, and U-03 that carry the ledger's historical wording but are not marked as quotations, so a reader meets them in the page's own voice.
residue for the steward: decide whether a hand-kept card intent that repeats a verified entry's wording counts as a quotation of a historical record (the Lexicon's own law says verified entries keep their words); if it does, the verdict is holds and the residue is the unmarked quotation, not the word.

## L-04 - The companions
claim: "The claim: the four companion pages use the Almanac's words with the Almanac's meanings, so a reader does not have to learn the vocabulary twice."
steps:
- Fetched the four (all 200): `/commons/build/gates/` 30,794 bytes, `/commons/build/run-through/` 34,081, `/commons/build/instructions/` 76,468, `/commons/build/launch/` 21,654. Render of the Proof Book: `/home/openclaw/shots/walk-X-38/L-04-gates.png`.
- proof: Proof Book, "the attestation to speak, and the procedure that writes it into the record"; run-through, "sets up the three proof attestations that are ready"; instructions, "proof consistency on every change"; launch, "the first grant opens A-03, A-04, and the agency proof". All four use proof as the human act that closes a bed.
- bed: Proof Book, "the module document that governs its bed"; run-through, "Three acts verify the bed"; instructions, "164 work pieces and proofs across sixteen beds"; launch, "Each releases a bed behind it: the counting rules open the Share bed". All four use bed as the ordered run of pieces.
- mark: Proof Book, "Align the legal index and the instrument on one mark"; run-through, "the bylaws mark itself resolved 2026-07-22"; instructions, "status: The honest mark. Marks: drafted, anticipated, open"; launch, "every status here is the mark carried in rdm-ledger.yaml". All four use mark as the status a ledger entry carries. The Proof Book and run-through apply it to a legal instrument's status mark, which is the same sense on a different shelf.
proposed verdict: holds
one sentence: L-04 holds: proof, bed, and mark carry the Almanac's meanings on all four companions, with phrasing that differs and meaning that does not. Agent's reading.
residue for the steward: none.

## L-05 - The series speaks
claim: "The claim: the governing documents define the vocabulary the pages use, so no page leans on a word that is nowhere defined."
steps:
- Fetched the four (all 200): `/commons/bp/` 33,016 bytes, `/commons/vs/` 32,550, `/commons/prd/` 47,008, `/commons/series/` 32,836. Render of BP: `/home/openclaw/shots/walk-X-38/L-05-bp.png`.
- piece: defined in BP v2 section 3, "The work piece", which reads "The piece replaces the milestone-in-wave as the unit of work. It is a validated YAML entry in the ledger, small enough for one session to advance and complete enough for a stranger to pick up." and then lists its fields (address, intent, cites, and so on).
- acceptance: defined in VS v2 section 3, "Proving a piece": "A piece's acceptance field is its test statement, written so this document can check it. For capability work, the member-capability sentences of PRD v0.4 §4 are the acceptance language verbatim". PRD v0.4 states the same at its own section 4 note ("The acceptance criteria for each capability are its plain-language member sentences in §4").
- emission: zero hits for emission or emissions across all four documents. The concordance on the Lexicon retires emits for yields, so the current word is yield. yield: the series overview shelf reads "UI and IM each carry a yield"; BP section 1 reads "this contract yields a machine-facing distillation"; VS reads "the workflow it yields". No sentence in the four documents states what a yield is; the definition lives on the Lexicon (yield entry) and not in the series. The instructions page under /commons/build/ still uses "emissions" once (see L-02 note on SUB-02).
proposed verdict: holds
one sentence: L-05 holds for piece and acceptance, both defined in the series; the card's third candidate, emission, is a retired word that the series no longer uses, and its replacement, yield, is used by the series and defined on the Lexicon rather than in the series. Agent's reading.
residue for the steward: decide whether a word the series uses but only the Lexicon defines satisfies "defined in the governing documents". If the Lexicon does not count, the verdict is fails on yield. Also the card's own text names emission as a candidate; a retired word on a card is a run-book defect to report.

## L-06 - The modules speak
claim: "The claim: the three module specifications were rewritten into the current vocabulary and published as new versions, and each page says so on its face."
steps:
- Fetched the three (all 200). Line under the title: `/commons/patronage/` reads "PATRONAGE v0.4 · module specification · enabling the Program Stack"; `/commons/treasury/` reads "TREASURY v0.1.5 · module specification · the movement layer"; `/commons/agency/` reads "AGY v0.2 · a proposal · the member's hand on the instrument". Renders: `/home/openclaw/shots/walk-X-38/L-06-patronage.png`, `L-06-treasury.png`, `L-06-agency.png`.
- Last line of each. Patronage ends "2026-07-22, amended 2026-07-27, re-cut August 2026, v0.4 against COUNTING-RULES v2 on issue #212, 2026-08-21", matching the card's expected tail word for word. Treasury's tail carries "supersedes TREASURY v0.1.4 · adopted by the steward, August 2026 · ... re-cut 2026-08-13". Agency's tail carries "Drafted, open to discussion, nothing herein adopted · ... 2026-07-27, re-cut August 2026".
- Read one paragraph of each in the current vocabulary (patronage's tail line "yields, anticipated, 000N_patronage_verbs.sql and the §14 graft as taken"; treasury's "the four joint contracts"; agency's citation list "U-01 through U-04 as built: the shell, the session, the gate"). The three read in the Almanac's register: yields, graft, bed, proof. Agent's reading. One thing seen: the treasury tail line reads "complementary to PATRONAGE v0.3" while the published patronage page is v0.4.
proposed verdict: holds
one sentence: L-06 holds: each page states its version under the title and carries its own re-cut in its tail, and the prose reads as one book with the Almanac, with one stale cross-reference (treasury naming PATRONAGE v0.3) to report. Agent's reading.
residue for the steward: read a paragraph of each as a reader; the walker's judgement of "one book" is an agent's.

## X-14 - The build surface agrees
claim: "The claim: the Almanac is a reading of the ledger and not a second record, so no page under /commons/build/ may state a count the ledger contradicts."
steps:
- On `https://techne.coop/commons/build/`: the proofs list is headed "The ten proofs · each attested as an event, none authored as a date" and lists ten rows: G0, G-B, G-G, G-F, G-S, G-T, G-R, G-A, G-L, G-V. The Belong bed section carries nine piece cards, B-01 through B-09, plus the proof card G-B. Headline counts: 35 drafted, 40 anticipated, 108 open, 49 verified, "level with the ledger at 6c1a6d9 (X-34)".
- Rendered `http://localhost:8899/_boot.html#/intranet/hud/` under the stub harness, fixture data, fixture session as Todd Youngblood. Render: `/home/openclaw/shots/walk-X-38/X-14-hud.png`. The HUD opened on its first view (journeys); the Maturation view (button "02 · the work") is selected by a click the headless render did not make, so the figures below were read from the page's own embedded cut, the same JSON the Maturation view draws its bed bars from: generated "2026-09-02 at 3a1a28301ded", beds: proofs 10, belong 9 (also: cross_cutting 36, shell 21, series 11, lexicon 9, treasury 9, find 5, ground 5, share 3).
- Ledger file at 654a796: proofs bed holds ten addresses, G0, G-B, G-G, G-F, G-S, G-T, G-R, G-A, G-L, G-I; belong bed holds nine, B-01 through B-09; 183 items in total.
- Both numbers agree three ways: proofs 10 on the Almanac, 10 in the HUD cut, 10 in the ledger; Belong 9, 9, 9.
- Seen, not the card's test: the Almanac's ten-proof list carries G-V and not G-I, while the ledger's proofs bed carries G-I and not G-V (G-V sits in the ledger's standing bed). The count agrees; the membership of the list does not. G-I has its own card on the Almanac in the transducer section.
proposed verdict: holds
one sentence: X-14 holds on the numbers: ten proofs and nine Belong pieces on the Almanac, ten and nine on the ledger's side, with the proofs list carrying G-V where the ledger's proofs bed carries G-I.
residue for the steward: open the HUD signed in and read the Maturation view with his own eyes, since the walker read the HUD's embedded cut rather than the rendered view; decide whether the G-V for G-I substitution in the ten-proof list is a drift to file.

## X-15 - The register bridge
claim: "The claim: this revision changed the Almanac's framing words only. Not one address, mark, count or citation moved with them."
steps:
- Dek under the title: "The plan of the build as an almanac: every piece with an address, a readiness condition, its citations into the series, and an honest mark. No dates: work waits on conditions the way sowing waits on soil, never on the calendar. The register is the build's own, held in the Lexicon".
- Caveat under the dek (class state-caveat): "This page is authored prose over a generated spine: the headline counts above are written from the ledger by the validator and proven current in CI (X-10). The cards below are hand-kept, and drift between the two is the recurring defect of this estate. X-14 reconciled them in July and X-17 again in August".
- Framing judgement: the dek and caveat read as chosen language in the cooperative's register (almanac, sowing, soil, honest mark, spine), not interface labels. Agent's reading.
- X-14 above proposes holds on the numbers, so the record underneath was not disturbed as far as this walk read it.
proposed verdict: holds
one sentence: X-15 holds on the framing: the dek and caveat read as the cooperative's own register, and X-14's numbers stood. Agent's reading.
residue for the steward: the framing judgement is a reader's; the walker gave one sentence.

## X-16 - The estate reads true
claim: "The claim: the three documents a new contributor reads first cite the document versions that actually exist, so nobody is sent to a retired one."
steps:
- Read README.md, CONTRIBUTORS.md, and RUN.md from the worktree at 654a796, which is origin/main, the commit GitHub renders.
- README series table: SER v0.3, PRD v0.4, IM v0.1, AM v0.1, BP v2, VS v2, UI v1, ALM v2 "(supersedes RDM v1, the Roadmap)", NC v2. The map of the estate reads "/commons/series/ The Common Record Series (SER v0.3)" and "/commons/build/ The Almanac (ALM v2 · the piece ledger)", and "/commons/build/instructions/ Agent instructions (BP v2 · ALM v2 · UI v1)".
- CONTRIBUTORS.md names BP v2 at lines 3, 9, 98, and 179 ("It summarizes BP v2, the single governing document for all work in this repository"). No other version cited.
- RUN.md line 5 reads "contract: AGENTS.md (BP v2), read it first and entire."; line 54 cites AM v0.1. No other version cited.
- The only retired version named in the three files is RDM v1, inside README's supersession note, which names it as retired.
proposed verdict: holds
one sentence: X-16 holds: the three files cite SER v0.3, ALM v2, BP v2, VS v2, and PRD v0.4, and RDM v1 appears only as the thing ALM v2 supersedes.
residue for the steward: none.

## X-17 - The second resync
claim: "The claim: every address in the ledger has a card on the Almanac and every card carries the mark the ledger carries, and a check in CI now refuses any drift between them, so this stays true without anyone re-checking by hand."
steps:
- `GET /repos/Techne-Co-op/techne.coop/actions/runs?branch=main&per_page=10`. Newest completed verify run on main: run id 33709552410, workflow "verify", head 3a1a283, started 2026-09-03T02:57:13Z, conclusion success. (654a796 is a generated HUD refresh commit on top of 3a1a283 and did not trigger verify.)
- `GET /repos/Techne-Co-op/techne.coop/actions/runs/33709552410/jobs`: job "style-lint", conclusion success, completed 2026-09-03T02:57:28Z. Step "the cards answer to the ledger, the ledger to the repository (X-18)": success, completed 02:57:23Z. Neighbouring steps in the same job: "the almanac audit still refuses (X-18)" success; "the walk's cards answer to the run-book (X-28)" success. All nine jobs in the run succeeded (ledger-validate, schema-lint, style-lint, db-verify, restore-test, rls-audit, generated-freshness, sms05-ceremony, gate-rehearsal).
- Locally in the worktree, `python3 scripts/almanac_audit.py` reported "0 finding(s) over 183 addresses".
proposed verdict: holds
one sentence: X-17 holds: verify run 33709552410 on main, run 2026-09-03 at 02:57 UTC (the evening of September 2 in Boulder), has the X-18 step green in the style-lint job.
residue for the steward: none.

## U-21 - The commons page speaks the current book
claim: "The claim: /commons/ shows each capability with the mark the ledger actually holds, unrounded and unflattered, in the current vocabulary."
steps:
- Fetched `https://techne.coop/commons/` (200, 36,957 bytes). Render: `/home/openclaw/shots/walk-X-38/U-21.png`. Four capabilities with marks: Belong "Built and walked · proof awaits attestation"; Gather "Built and walked · proof awaits attestation"; Find one another "Built · one beat wants a second member"; See your share "After the counting rules adopt".
- Spot-check against the ledger file at 654a796 (the HUD under the stub draws from the same cut; see X-14 for how it was read): G-B anticipated and B-01 through B-07 verified, matching "built and walked, proof awaits attestation"; G-F anticipated with F-02 at "open · delivered", matching "one beat wants a second member"; S-01 and S-02 at "open · Q3" with G-S anticipated, matching "After the counting rules adopt". No mark rounded up; the page distinguishes walked from attested and built from walked.
- The page names the intranet ("The intranet is where a member reads and writes this one, behind sign-in") and carries a section "How it is steered" with the steered garden reading ("A garden under a gardener's hand is a steered system").
- Links: 30 in-estate paths, every one returned 200 by `curl` (/, /commonplace/, /commons/..., /intranet/..., /federation/, /legal/). Two links leave the estate to GitHub issues #217 and #218 in the federation section, and two to Google Fonts. The card says each link must land inside the estate; the two issue links are the estate's own repository, which the walker reads as inside the estate. Agent's reading.
- Seen, not the card's test: the page renders em dashes in its lead and in the Find capability sentence (the words "Browse open offers and invitations" are followed by an em dash before "to play, practice, and work"), already reported by the tier-four walk.
proposed verdict: holds
one sentence: U-21 holds: the four marks match the ledger's side unrounded, the page names the intranet and the steered garden, and every in-estate link answers 200.
residue for the steward: rule on whether links to the cooperative's own GitHub issues count as inside the estate; click the links himself if he wants the render checked rather than the status code.

## U-22 - The Commonplace, published
claim: "The claim: the fifteen formation conversations were published whole at techne.coop/commonplace, losing no entries and claiming no more authority than the source claims."
steps:
- Fetched `https://techne.coop/commonplace/` (200, 81,354 bytes). Render: `/home/openclaw/shots/walk-X-38/U-22.png`.
- Movements: five headings, "Movement I" through "Movement V". Entries: 79 elements with class entry; the page states "Seventy-nine entries" and "Fifteen meetings · August 2025 to February 2026".
- Spot-read three entries: "Resources, Events, Agents" ("An accounting ontology from William McCarthy's 1982 work"), the public benefit entity entry ("Any Colorado cooperative can form as a public benefit entity"), and "Single source of truth". The walker has no memory of the source summaries to read them against; that reading needs the steward.
- Standing: a section headed "Its standing" reads "Not a governing instrument. It binds nothing. What binds is the legal record; what the build answers to is the Almanac; what a word means now is the Lexicon." and "Held as a lens". The "Before you read" section says "Recorded is not verbatim" and "It carries no names".
- Author of the lens: the commonplace page does not name the steward anywhere; its footer reads "Assembled from the meeting summaries · working draft". The naming is on `/commons/`, which reads "The steward asks that it be read as the lens the rest of the work is perceived through".
- `/commons/` links to `/commonplace/` and says what it is: "The Commonplace is what was said in them: seventy-nine entries gathered from the meeting summaries" and "That book is a formation record and it governs nothing."
proposed verdict: deferred
one sentence: U-22 stands on everything mechanical (five movements, 79 entries, standing stated, /commons/ links and describes it), but the page itself does not name the steward as the author of the lens, and the spot-read against the source needs a person who has read the source.
residue for the steward: spot-read three entries against the meeting summaries; decide whether the steward being named on /commons/ rather than on /commonplace/ satisfies "the page ... names the steward as the author of the lens".

## MM-01 - The horizon enters the shelf
claim: "The claim: the maturity model sits on the legal shelf where a reader can find it, labelled as something the cooperative has not adopted."
steps:
- Fetched `https://techne.coop/legal/maturity-model/` (200, 16,881 bytes) and its specification subpage `/legal/maturity-model/specification/` (200, 27,187 bytes). Both render: `/home/openclaw/shots/walk-X-38/MM-01-model.png`, `MM-01-spec.png`. The model page's own dek reads "This is a model for discussion. Nothing here is decided." and its kicker reads "Legal · Horizon".
- Fetched `https://techne.coop/legal/` (200, 16,448 bytes, byte-identical to the worktree). Render: `/home/openclaw/shots/walk-X-38/MM-01-legal.png`. The page has no Horizon section and no link to either maturity-model page: zero occurrences of "maturity-model" and zero of "horizon" in its markup. Its heading reads "The filed instruments." and its dek "What this cooperative has filed with a government, and nothing else." Commit cf30ac9 "legal: simplify the public page (#234)" and bddae05 "legal: split the public filings from the intranet full record" moved the full shelf behind sign-in.
- The Horizon section now sits on `/intranet/legal/` (read from the worktree file, not rendered signed in): heading "The Horizon · How the cooperative could grow", placed after "Corrections and open readings", which follows the four Layer groups. Both pages are linked there. The note reads "Everything above is an instrument or a reading of one. What follows is neither. The maturity model is research prepared for members to discuss ... Nobody has adopted it. It is not a governing document and it is not legal or tax advice, and nothing on these two pages binds anyone."
- Seen, not the card's test: `/legal/maturity-model/` renders em dashes in its dek and body ("not by stretching one entity to do everything, but by adding sibling entities"), against the house style.
proposed verdict: fails
one sentence: MM-01 fails as written: the public shelf at /legal/ no longer carries a Horizon section or any link to the maturity model, which has moved with its unadopted note to /intranet/legal/, so the card's second step cannot be taken on the page it names.
residue for the steward: decide whether the card should be re-cut to /intranet/legal/, where the section, both links, and the unadopted note are present in the order the card describes, or whether the public shelf should carry the Horizon again.

## Tally

Cards walked: 12. Proposed holds: 9 (L-01, L-04, L-05, L-06, X-14, X-15, X-16, X-17, U-21). Proposed fails: 2 (L-02, MM-01). Deferred: 1.

- U-22 deferred: the spot-read against the meeting summaries needs a person who has read the source, and the page does not itself name the steward as the author of the lens.

Of the two proposed fails, both rest on a reading the steward may overrule: L-02 on whether an unmarked card intent that repeats a verified entry's wording is a quotation, and MM-01 on whether the card should follow the Horizon section to /intranet/legal/. Two of the holds carry a question for the steward: L-05 on whether the Lexicon's definition of yield counts as the series defining it, and U-21 on whether links to the repository's own issues land inside the estate.

Not taken: no sign-in link was sent; no form was submitted; no live row was read or written; the HUD was rendered under the stub harness on fixture data and its figures read from the page's embedded cut rather than the Maturation view a click selects.

Page defects seen on the way, reported not fixed: the Almanac's SUB-01 and SUB-02 cards use "Emits" and "emissions", retired for yields; the Almanac's ten-proof list carries G-V where the ledger's proofs bed carries G-I; the treasury page's tail names "PATRONAGE v0.3" while patronage publishes v0.4; the L-05 card itself names "emission", a retired word, as a candidate; the MM-01 card sends the walker to a Horizon section that /legal/ no longer carries; `/legal/maturity-model/` and `/commons/` render em dashes in prose.

Checks run in this worktree at 654a796 with this sheet added: `scripts/validate.py`: "validate: 183 packets", rewrote STATUS.md and index.json without change, "validation passed (0 warning(s))"; `scripts/em_dash_audit.py`: "124 files, clean" after one line of this sheet was reworded so as not to reproduce the em dash it reports; `scripts/almanac_audit.py`: "0 finding(s) over 183 addresses"; `scripts/verification_cards.py --check`: "cards.json is current".
