# Contributing to techne.coop

This repository is a cooperative project, built under the **Build Protocol (BP v1)**. Contributions come in two forms: work by human organizers, and work by build agents under organizer direction. Both paths end at the same place: a pull request, reviewed by an organizer, merged only with the validator green.

---

## The operating contract

Read `AGENTS.md` before anything else. It summarizes BP v1, the single governing document for all work in this repository. BP v1 governs; `AGENTS.md` summarizes. When the two disagree, file the conflict and follow BP v1.

The full agent instructions, including design system alignment and ledger orientation, are at [techne.coop/commons/build/instructions/](https://techne.coop/commons/build/instructions/).

---

## Human organizers

Organizers are the decision-making body. They record outcomes, approve merges, adopt drafts, and own the work. They are the only parties who may:

- Record a decision in the D-series
- Adopt an agent-authored document as a record or policy
- Merge a pull request
- Change the status of a series artifact

**Current organizers:** Todd Youngblood (Ventures & Operations Steward), Aaron G Neyer, Benjamin Ross, Jonathan Borichevskiy, Kevin Owocki, Lucian Hymer, Neil Mackay Yarnal, Savannah Kruger.

**Primary build contact:** Todd Youngblood. Schema, authority, design decisions, public naming, and anything touching money or membership standing all go to Todd.

### Human contribution path

1. Open an issue describing the change or the problem. Name the packet address if one exists.
2. Branch from `main` using the packet address as the branch name (e.g. `SUB-01`, `B-03`).
3. Work inside the cited constraints of the packet.
4. Open a pull request. State what was decided within scope and what was escalated.
5. Wait for organizer review. Tier A (work within cited scope): one organizer approves. Tier B (schema, authority, money, membership): organizer review plus a decision record. Tier C (series artifacts): Todd approves.
6. Merge only with the validator green.

---

## Build agents

Build agents are session-scoped instruments  --  capabilities without authority. They hold no standing between sessions and presume no memory. Their entire working context is assembled from the series artifacts and the packet in hand.

### Session start (every session, every time)

1. Read `AGENTS.md` at the repository root.
2. Read the series overview at [techne.coop/commons/series/](https://techne.coop/commons/series/).
3. Read the living roadmap at [techne.coop/commons/build/](https://techne.coop/commons/build/).
4. Read the packet you are working, and every artifact it cites, in full.
5. Only then, open the code.

### What agents decide

Inside a packet's cited constraints, agents decide freely: code structure, query shape, test arrangement, file layout, internal naming, draft copy, order of their own steps.

### What agents escalate

Agents stop and file an escalation card for anything touching:
- Permissions or visibility not already in the Authority Map
- Schema changes not already in the Information Model
- Money, membership standing, or governance semantics
- New dependencies (package, service, font, endpoint)
- Conflicts between cited artifacts
- Public names and public claims
- Anything where the bylaws are silent

**Escalation card shape:**

```
standing in:  <packet address and step>
found:        <what was encountered, with artifact citations>
the question: <the smallest question whose answer unblocks the work  --  one question>
a default:    <proposed answer, marked as a proposal>
```

### Agent commit convention

```
<brief imperative summary>

Packet: <address>
Authored-by: build-agent / <address>
```

---

## Vocabulary

Subchapter K throughout: **distributive share**, **capital account**, **allocation**.

Never use: patronage dividend, written notice of allocation, per-unit retain, users, engagement, event/content, funnel/convert, stake/investment, exclusive/free.

No emoji. No em dashes. No exclamation points. Italics for key terms in running prose, not bold. Status chips on every claim that has a status.

---

## Design system

Techne v4. Two grammars:

- **Document:** Libre Baskerville body, 16px, 1.75 line-height, 760-920px max-width. For series artifacts, onboarding pages, the instructions page.
- **Instrument:** IBM Plex Mono base, 13px, dense, full-width. For HUDs, dashboards, the build page.

Full reference: [techne.coop/design-system/](https://techne.coop/design-system/) and [techne.coop/commons/build/instructions/#s6](https://techne.coop/commons/build/instructions/#s6).

---

## Status marks

Every claim wears its mark:

| Mark | Meaning |
|---|---|
| Filed | Estate practice confirmed and carried |
| Ratified | Adopted by the members or board |
| Drafted | Exists and governs; may still change before ratification |
| Anticipated | Defined, upstream must clear first |
| Open · (blocker) | Blocked; the mark names what blocks it |

---

## The ledger

The roadmap lives at `commons/build/index.html` and reads from `rdm-ledger.yaml`. Do not edit the living roadmap directly  --  it is generated from the ledger and the series. The validator enforces schema compliance, dependency acyclicity, and gating consistency on every change.

Current state (July 2026): 7 drafted series documents · 23 anticipated packets · 10 open conditions.

The one immediately workable packet: **SUB-01**  --  stand the repository on the estate layout with the validator reshaped to slices.

---

*RegenHub, LCA · Boulder, Colorado · BP v1 · July 2026*
