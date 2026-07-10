# techne.coop

Source for [techne.coop](https://techne.coop) — the virtual home of **Techne**, a community of practice for technology as craft. Operated by **RegenHub, LCA** (Colorado Limited Cooperative Association, SOS #20261163853). GitHub Pages, `main` branch, custom domain.

---

## What Techne Is

*Techne* is the old Greek word for craft, art, skill — the root beneath technique and technology. It names a cooperative studio in Boulder, Colorado and the network it tends: a community of practice for the UX designer, the database engineer, and the person who has never been told the word technologist applies to them.

The cooperative's public benefit: **cultivating scenius** — the collective intelligence that arises when skilled people share a commons.

Techne is soil, not plant. It provides infrastructure (space, legal structure, planning, capital access) for autonomous ventures. The ventures grow in the field; the cooperative holds the conditions.

---

## The Commons

The commons section of this site (`/commons/`) is called **The Commonplace Book** — the cooperative's shared record, after the centuries-old practice of keeping what matters, organized for use, in one place everyone can read.

It is built on the **Common Information System (CIS)**, a cooperative-grade database that holds the authoritative state of the cooperative: who the members are, what agreements bind them, what events have taken place, and what each person's share of the work and the results amounts to. Every figure is traceable to the events that produced it. Every rule is traceable to the governing document that established it.

The Commonplace Book opens in four slices:

| Slice | A member can |
|---|---|
| Belong | Read every agreement that binds them. Sign the membership agreement. Join the directory. Complete onboarding without a meeting. |
| Gather | See upcoming events. Register and cancel without asking anyone. Have attendance counted where the record counts it. |
| Find one another | Browse and post open offers. See what an invitation led to when the parties choose to record it. |
| See your share | See their contribution history, their capital account, and follow any figure to the events and policy that produced it. |

---

## The Common Record Series

The CIS build is organized by **The Common Record Series** — eleven governing artifacts, dependency-ordered, with no dates. Dependency is the schedule.

| Code | Artifact | Status |
|---|---|---|
| SER | Series Overview | Drafted |
| PRD | Product Requirements v0.3 | Drafted |
| IM | Information Model & Invariants | Drafted |
| AM | Authority Map | Drafted |
| BP | Build Protocol | Drafted |
| VS | Verification Spec | Drafted |
| UI | Interface Tokens & Patterns | Drafted |
| RDM | Roadmap | Drafted |
| LP | Landing Page | Drafted |
| NC | Nou Charter v2 | Anticipated |
| OR | Operations Runbook | Anticipated |

The living roadmap is at [techne.coop/commons/build/](https://techne.coop/commons/build/) — 40 packets across 7 trains (SUB, Belong, Gather, Find, Share, Cross-cutting), 7 drafted series documents, 23 anticipated, 10 open.

Build instructions for agents: [techne.coop/commons/build/instructions/](https://techne.coop/commons/build/instructions/)

---

## Site Structure

```
/                         Landing page — Techne, opening August 14, 2026
/commons/                 The Commonplace Book — cooperative shared record
/commons/series/          The Common Record Series (SER v0.2)
/commons/build/           Living Roadmap (RDM v1 · packet ledger)
/commons/build/instructions/  Agent instructions (BP v1 · RDM v1 · UI v1)
/design-system/           Techne v4 token and pattern reference
/legal/                   Formation documents
/intranet/                Member intranet (authenticated)
/encyclopedia/            Techne vocabulary
/assets/                  Shared fonts, icons
```

---

## Agent-Driven Build

This repository is built under **BP v1** (Build Protocol). The operating contract lives at `AGENTS.md` in the root, where agent harnesses load it automatically. BP v1 governs; `AGENTS.md` summarizes.

Key rules:
- One packet per branch, named by the packet address (e.g. `SUB-01`, `B-03`)
- Commits carry authorship trailer: `Authored-by: build-agent / <packet-address>`
- Agents decide inside cited constraints; they stop and file an escalation card at the boundary
- Nothing becomes a record or policy until an organizer adopts it by visible act
- The validator must be green before any merge

Read `AGENTS.md` before opening the code. Read the packet and every artifact it cites before any file.

---

## Related Repositories

| Repo | Domain | Purpose |
|---|---|---|
| [Techne-Co-op/techne.coop](https://github.com/Techne-Co-op/techne.coop) | techne.coop | This repo — main co-op site and commons |
| [Techne-Co-op/journal](https://github.com/Techne-Co-op/journal) | journal.techne.coop | Daybook — studio journal and working notes |
| [RegenHub-Boulder/techne.institute](https://github.com/RegenHub-Boulder/techne.institute) | techne.institute | Legal documents (being retired; /intranet migrating here) |
| [Techne-Co-op/cis-reference](https://github.com/Techne-Co-op/cis-reference) | — | CIS schema and policy reference (live Supabase fetch) |

---

## Design System

Techne v4. Tokens at [techne.coop/design-system/](https://techne.coop/design-system/).

- **Type:** Libre Baskerville (serif, narrative) + IBM Plex Mono (labels, instruments)
- **Ground:** `#0F0F12` dark / `#F7F5F0` light — warm-neutral
- **Accent:** `--ember` `#C4956A` (primary) + `--blue` `#6A8AC4` (interactive)
- **Two grammars:** document (prose-first, 760-920px, serif body) and instrument (data-first, full-width, mono base)
- **Mode:** `localStorage('techne-mode')`, `data-mode` on `<html>`, set early in a blocking script

---

## Contributing

See [CONTRIBUTORS.md](./CONTRIBUTORS.md).

*RegenHub, LCA · Boulder, Colorado · Public benefit: cultivating scenius.*
