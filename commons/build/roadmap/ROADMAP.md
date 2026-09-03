<!-- standing: drafted. A plan prepared by the agent at the steward's direction; it adopts nothing. Public copy of the working plan; the working queue is not here. -->

# The commons build to public beta: plan and roadmap

*Prepared 2026-09-02 by Nou for Todd Youngblood, on his direction in #intranet-dev (relay event `cd4530fc…73fe1a`, 19:15 UTC): orchestrate and schedule the completion of techne.coop/commons/build to public beta, from today's report, with Fable 5.1 sub-agents on a 45-minute automation. Ground truth: `almanac-ledger.yaml` at origin/main `08bc3d3` (validator green, 178 packets, run 2026-09-02); the agent's status report of the same day (workspace, not public); the build instructions at `commons/build/instructions/`. Strict register: every claim about a packet cites its ledger status; the definition of public beta in §1 is a proposal until the steward adopts it by merging §13 of the instructions.*

## 1. What public beta means here

No instrument on the estate defines "public beta". Searched 2026-09-02: no page, packet, or document under `techne.coop/` uses the phrase. So this plan proposes one, and the steward's merge of the instructions §13 adopts it. Until then it is Nou's definition.

**Public beta is the state in which every surface a member can reach says truthfully what it is, every agent-completable piece is delivered and green, the four proofs that wait on no board act are attested, and the beds that wait on the board are marked as waiting rather than missing.** Concretely, six conditions:

| # | condition | whose act | measured by |
|---|---|---|---|
| B1 | Every `open · delivered` piece that one person can walk alone has a verdict: verified, or a named defect filed as a packet. | the steward, walking (X-22 sittings) | ledger marks; `packet.verified` events; the walk page |
| B2 | Every agent-completable piece in §3 is delivered on main with the full CI battery green. | agents, under the merge grant | `scripts/validate.py`, `verify.yml`, one reader over each batch |
| B3 | G-B, G-G, G-F attested; G-L attested once L-01 through L-06 are verified. | the steward (G-B needs a second person) | `gate.attested` events |
| B4 | The Almanac prose and the instructions page state the ledger's state on the day, and the record-keeping loop (R-01, R-02) is live so a board meeting and its minute have a place in the record. | agents; the Secretary writes the first row | the pages; `minutes.*` events |
| B5 | The public surfaces carry one beta mark that says what is and is not in force (share, treasury, standing, guild, matrix waiting on board acts), in words the steward chose. | drafted by an agent, named by the steward | the mark on `/commons/` and `/commons/build/` |
| B6 | No stale claim: no page says a thing is adopted, live, or verified that the ledger and the record do not say. | agents audit; the steward rules on contradictions | X-18 almanac audit; the U-32 design audit; a manual claims pass |

Out of public beta by definition, and stated on the beta mark rather than hidden: the share bed (S-01..03), treasury movement (T-02..T-07, T-05), standing (V-*), guild (P-01..P-06), matrix (M-*), agency A-03/A-04, the two unapplied migrations (0029, 0030), and everything `anticipated` on a board adoption. A faster fleet does not move a human boundary (instructions §8).

## 2. Where the build stands (2026-09-02, ledger at 08bc3d3)

178 packets: 49 verified, 50 delivered, 6 open on a named condition, 40 anticipated, 33 drafted. The member-facing beds (ground, belong, gather, find, shell) are built and mostly verified. The money and ownership beds are zeros waiting on board acts. Eleven series documents are drafted because no human act has adopted any. Detail and the page-by-page intranet walk: the agent's report of 2026-09-02, held in its workspace.

Corrections to the report since it was written: PR #228 (walks 01 and 02) merged 2026-08-26, so its fourteen verified marks are already in the 49. The 2026-08-21 draft minutes were held as an informational record, not minutes, by the Secretary on 2026-09-02; minutes proper number one, the founding record of 2026-08-14.

## 3. Agent-completable work, in batches

Each batch is one worktree, one branch named by address, one pull request with a manifest, one fresh-context reader over the union before the PR opens, validator and style-lint green locally before push, the full battery green before merge. Merge is the act of adoption; under the standing merge grant Nou merges and reports each merge in #intranet-dev, or holds the PR for the steward where the batch touches a public claim (Tier C) or anything §2 of the instructions says to stop on.

| batch | address | what | tier | est. | depends on |
|---|---|---|---|---|---|
| 0 | X-33 | The road to public beta: instructions §13 carrying §1 and §4 of this plan, the packet, its almanac card. | A | half a day | nothing |
| 1a to 1d | X-38 | The agent walk (added 2026-09-02 at the steward's ask): the 48 single-player cards of `/intranet/verification/` walked by a Fable 5.1 session per tier, each producing an unsigned evidence sheet under `commons/build/verification/walks/` with a proposed verdict per card and the residue a person must still take. No ledger mark changes; the steward's reading of a sheet is the verifying act, and a PR per signed sitting flips the marks. Tiers one and four first; two and three after X-34. | A | half a day each | tiers two and three on batch 1 |
| 1 | X-34 | The third resync: `commons/build/index.html` "Where the build stands" recut from 2026-08-17 to the ledger of the day (proofs bed now ten addresses, the R bed, the count line); instructions §4's counts (still "126 items") brought level; the X-18 audit green. Pattern: X-14, X-17. | A | one day | batch 0 |
| 2 | R-01 | The minute book, no schema: a Minutes section on `/commons/gatherings/` for sessions titled "Board ·", listing `minutes.drafted` and `minutes.adopted` events, with an overseer-only form writing the two kinds through the overseer branch of `events_scoped_insert` (0024). New bed `record`. First checks: the live events read policy for overseer-written kinds, and whether a `secretary` role exists in `role_grants` (report §5, unverified). If a member cannot read them, the list shows to overseers only and says so. | A (no migration, no policy change) | one day | batch 1 |
| 3 | R-02 | `/intranet/record/` rewired: the minute book read from `minutes.*` events; offices and roster from `role_grants`; attendance per board meeting from `attendance`; the GOV v0.1 parliamentary model moved under a design-note heading; the footer-versus-table contradiction on the Bylaws' standing put to the steward as a stop card with a default. | A, one stop card | one to two days | batch 2 |
| 4 | X-35 | The beta mark: one component on `/commons/` and `/commons/build/` naming what is in force and what waits, drafted with the wording as a stop card. Held for the steward's word on the words (instructions §2: public names and claims are his). | C | half a day | batches 1 to 3 |
| 5 | X-36 | The claims pass: every public and intranet page read for a claim of adopted, live, verified, or in force that the ledger or the record does not support; each finding filed as a correction on the page it sits on, with the page's own change note; the U-32 design audit and the X-18 almanac audit green. | A, stop cards where a claim is the steward's | one to two days | batch 1 |
| 6 | L-07 | The machinery renames, per election D3: file and identifier renames with every reference updated in one commit. `ready_when` L-06 merged, which it is. Last on purpose: it touches the most files and gains nothing a member sees. Held until batches 1 to 5 are merged. | A | one day | batch 5 |
| 7 | X-37 | The walk's evidence sheet for the four proofs: the run-through steps for G-B, G-G, G-F, G-L as a printable sitting with the attestation text and the recording procedure the Proof Book already carries, so the steward's afternoon is the only input left. | A | half a day | batch 2 |

Not batch candidates, with the reason from the ledger:

- **TR-05, TR-06, TR-07, TR-01** wait on TR-02 verified or a TRANSDUCER decision. TR-02 is `open · delivered`; the verified word is the steward's (instructions §12 names this packet).
- **X-20** changes the ledger grammar: Tier B, needs decision X-20-D1 recorded.
- **B-08** delivers migration 0025; **SMS-05** migration 0029; **X-32** migration 0030. Each is a schema act against the live CIS by a named human; no test project exists.
- **A-03, A-04** wait on the first grant, the steward's decision, routed to the board if he routes it. A-03 is also the board question (may a non-human agent hold scoped authority).
- **S-*, T-02..T-07, V-*, P-01..P-06, M-*, G-S, G-T, G-V** wait on board adoptions named in their `ready_when`.
- **G-A** needs a member who is not the steward. **X-21's** five beats need a second human.
- **U-29, U-32, MM, ROO, ORDER, EGRESS, PUB, STANDING, GUILD, MATRIX, TRANSDUCER, A-05, L-09, X-23..X-26, X-28..X-30, SMS-02** are `drafted` documents: they exist and govern nothing until a human adopts them. No agent act changes that mark.

## 4. Human blockers, by whose act

Ordered by what it unblocks. Each is one act; none needs construction first.

**The steward, Todd Youngblood**

1. **Sign the walk.** 50 packets stand `open · delivered`; X-22 organised them into sittings and `/intranet/verification/` holds 58 cards. Amended 2026-09-02 at the steward's ask (thread event `7e1f39ea…`): an agent walks the 48 single-player cards first (X-38, four sittings, one evidence sheet each under `commons/build/verification/walks/`), so the steward's act becomes reading each card's evidence and saying the word, not taking the steps. The word stays his (instructions §12); a PR per signed sitting flips the marks (the #228 pattern). What no agent can take: the three two-person cards, the six attestations (a countersigning member), the phone-in-hand steps unless he accepts 390px emulation, and any step that sends a message. Unblocks B1.
2. **Attest G-B, G-G, G-F** on the run-through; G-B wants a second person present. Unblocks B3 and the Find proof chain.
3. **Say the verified word on TR-02** (and then TR-03, TR-04, TR-09, TR-10). Opens TR-05, TR-06 and the G-I proof.
4. **Choose the beta mark's words** (batch 4). Public names are his under instructions §2.
5. **Rule on the Bylaws standing contradiction** that R-02 files: the footer says the governing instruments are board-adopted; the page's table says Bylaws v2.1 drafted, not in effect. One reading, his.
6. **Apply or refuse migrations 0029 and 0030** against the live CIS, or name who does. 0030 makes the walk queryable (X-32). Not required for beta; required for B1 to stop depending on copy-and-paste.
7. **Decide A-03**, the first grant, or route it to the board. Not required for beta; named because the Direction page tells members the agent "is not yet cleared to work in any code".
8. **Record X-20-D1** if the ledger grammar is to change before beta. Default: not before beta (the packet's own ready_when says so).

**The Secretary (Todd, in that office)**

9. **Write the first minutes row** once R-01 lands: `minutes.adopted` pointing at the founding record of 2026-08-14 (sha256 `655ddd28…98f13`), the one minute proper. Unblocks B4's second half.

**The board**

10. **COUNTING-RULES v1** (S-01, S-02, since 2026-07-24); **TREASURY-POLICY** (T-01, since 2026-07-22); **redeemability with counsel** (T-05); **STANDING, GUILD, MATRIX, TRANSDUCER** adoptions; **the series documents** (eleven, drafted). None gates beta under §1; all are named on the beta mark as waiting.

**A second human**

11. A member who is not the steward: respond to his opportunity posting (F-02), attend the G-B attestation, direct the instrument for G-A. X-21 is the script.

## 5. The schedule

Every 45 minutes, automation `commons-build-beta-runner` (OpenClaw scheduler, isolated session; every sub-agent spawned with the Fable 5.1 model named explicitly) runs its pass brief (workspace): read the batch queue, take the first batch whose dependencies are merged and which no run holds, spawn one Fable 5.1 build sub-agent with the brief template, wait for it, spawn one fresh-context reader over the union, open the PR, post the batch report in #intranet-dev, update the queue. A run that finds nothing runnable says so once and exits. A run that finds the queue empty posts the completion note and disables the automation. Three consecutive runs with no progress disable it and say why.

Rate: one batch per run at most. Batches take longer than 45 minutes; the lock in the queue stops the next run from starting the same batch, and a run that is still building when its 40-minute timeout arrives leaves the sub-agent running (it is its own session) and the next run picks up the report. Nothing in this loop merges a Tier C batch, applies a migration, writes to the live CIS, or takes a governance act.

Cost, stated: this loop is the class of load that exhausted the agent's model plan once before, on 2026-08-28. The queue is bounded and the loop ends itself. If the steward wants it slower, one word changes the interval.

## 6. What this plan does not do

It does not define beta for anyone but this build. It moves no human boundary: the board's adoptions, the steward's verified word, the second human's presence stay where the ledger puts them. It opens no migration. It adopts nothing; every batch is a pull request, and merge is the act.

*This copy is the plan as published to the estate at commons/build/roadmap/; the working queue, the runner brief, and the sub-agent brief templates live in the agent's workspace and are not part of the public record. Instructions §13 carries the six conditions and the human blockers; this page carries the whole.*
