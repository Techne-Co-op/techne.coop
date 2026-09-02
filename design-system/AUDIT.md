# Design audit

Written by scripts/design_audit.py at commit c26c00e over 105 tracked pages. Regenerate rather than edit: `python3 scripts/design_audit.py --report design-system/AUDIT.md`.

Every check names its source in the design system or in commons.css. A mechanical finding is one `--fix` applies; a judgment finding waits on a person. legal/ is reported and never fixed; design-system/ is exempt from the color checks only, as in token_audit.py.

## By check

| check | rule | source | pages | mechanical | judgment | observed |
|---|---|---|---:|---:|---:|---:|
| head-charset | charset meta | design-system#seo, required head block 1 | 0 | 0 | 0 | 0 |
| head-viewport | viewport meta | design-system#seo, required head block 1 | 0 | 0 | 0 | 0 |
| head-color-scheme | color-scheme meta | design-system#seo, required head block 1 | 9 | 0 | 9 | 0 |
| head-title | title carries the Techne pattern | design-system#seo, title pattern | 2 | 0 | 2 | 0 |
| head-description | description meta present | design-system#seo, required head block 2 | 4 | 0 | 4 | 0 |
| head-canonical | canonical link present | design-system#seo, required head block 2 | 14 | 0 | 14 | 0 |
| head-og | Open Graph block complete | design-system#seo, required head block 3 | 19 | 0 | 19 | 0 |
| head-favicon | favicon linked from root | design-system#seo, required head block 4 | 15 | 0 | 15 | 0 |
| head-mode-boot | mode flash prevention inline before CSS | design-system#seo, required head block 5 | 2 | 0 | 2 | 0 |
| type-faces | two faces only: Libre Baskerville and IBM Plex Mono | design-system#type, X-06 decision 2026-07-20 | 16 | 0 | 16 | 0 |
| type-scale | font sizes among the sizes commons.css uses | observed convention only; no scale is adopted (v6 reverted, PR 276) | 97 | 0 | 0 | 97 |
| token-layer | page defines both mode palettes or links commons.css | design-system#tokens; AGENTS.md REPO | 2 | 0 | 2 | 0 |
| token-private | custom properties the canonical layer does not name | observed convention only; commons/ui/commons.css is the token layer | 78 | 0 | 0 | 78 |
| color-hex | hex only inside a custom-property definition | token_audit.py X-06 | 0 | 0 | 0 | 0 |
| color-function | no rgb()/rgba()/hsl() literal outside a token definition | design-system#tokens: never past a token to a literal | 9 | 0 | 30 | 0 |
| color-named | no named CSS color outside a token definition | design-system#tokens: never past a token to a literal | 1 | 0 | 1 | 0 |
| skeleton-container | one of the three containers: wrap, wrap-hud, wrap-frame | design-system#layout; commons.css the two grammars | 19 | 0 | 19 | 0 |
| skeleton-footer | a footer element closes the page | observed convention: commons.css footer; notice_audit.py | 20 | 0 | 20 | 0 |
| skeleton-frame | exactly one of topbar.js or shell.js | design-system#topbar; validate.py U-13 | 0 | 0 | 0 | 0 |

Rule findings: 153 on 65 of 105 pages; 0 mechanical, 153 judgment. Observations, not counted: 175.

## By page

| page | frame | layer | container | faces | findings |
|---|---|---|---|---|---|
| about/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | token-private(1), type-scale(1) |
| accounting/counsel-memo/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | color-function(17), skeleton-footer(1), token-private(1), type-scale(1) |
| accounting/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | skeleton-footer(1), token-private(1), type-scale(1) |
| commonplace/index.html | topbar | inline | - | IBM Plex Mono,Libre Baskerville | skeleton-container(1), token-private(1), type-scale(1) |
| commons/agency/grants/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | token-private(1), type-scale(1) |
| commons/agency/index.html | topbar | inline | wrap | IBM Plex Mono,Inter,Libre Baskerville | skeleton-footer(1), token-private(1), type-faces(1), type-scale(1) |
| commons/agreements/board-originated/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | type-scale(1) |
| commons/agreements/comment-and-countersign/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | type-scale(1) |
| commons/agreements/index.html | shell | inline | main=wrap-frame | IBM Plex Mono,Libre Baskerville | color-function(2), token-private(1), type-scale(1) |
| commons/authority-map/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | clean |
| commons/bp/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | head-title(1) |
| commons/build/gates/index.html | topbar | inline | - | IBM Plex Mono,Libre Baskerville | skeleton-container(1), token-private(1), type-scale(1) |
| commons/build/index.html | shell+topbar (public) | inline | - | IBM Plex Mono,Libre Baskerville | skeleton-container(1), token-private(1), type-scale(1) |
| commons/build/instructions/index.html | topbar | inline | - | IBM Plex Mono,Libre Baskerville | skeleton-container(1), token-private(1), type-scale(1) |
| commons/build/launch/index.html | topbar | inline | wrap | IBM Plex Mono,Inter,Libre Baskerville | skeleton-footer(1), token-private(1), type-faces(1), type-scale(1) |
| commons/build/lexicon/index.html | topbar | inline | - | IBM Plex Mono,Libre Baskerville | skeleton-container(1), token-private(1), type-scale(1) |
| commons/build/run-through/index.html | topbar | inline | - | IBM Plex Mono,Libre Baskerville | skeleton-container(1), token-private(1), type-scale(1) |
| commons/build/run-through/organizers/index.html | topbar | inline | - | IBM Plex Mono,Libre Baskerville | skeleton-container(1), token-private(1), type-scale(1) |
| commons/build/sms-05-ceremony/index.html | topbar | inline | wrap | IBM Plex Mono,Inter,Libre Baskerville | skeleton-footer(1), token-private(1), type-faces(1), type-scale(1) |
| commons/build/sms-bindings/index.html | topbar | inline | wrap | IBM Plex Mono,Inter,Libre Baskerville | skeleton-footer(1), token-private(1), type-faces(1), type-scale(1) |
| commons/build/verification/index.html | topbar | inline | - | IBM Plex Mono,Libre Baskerville | skeleton-container(1), token-private(1), type-scale(1) |
| commons/build/walkthrough/index.html | topbar | inline | - | IBM Plex Mono,Libre Baskerville | skeleton-container(1), token-private(1), type-scale(1) |
| commons/directory/index.html | shell | inline | main=wrap-frame | IBM Plex Mono,Libre Baskerville | color-function(2), token-private(1), type-scale(1) |
| commons/gatherings/index.html | shell | inline | main=wrap-frame | IBM Plex Mono,Libre Baskerville | color-function(2), token-private(1), type-scale(1) |
| commons/governance/egress/index.html | topbar | inline | wrap | IBM Plex Mono,Inter,Libre Baskerville | skeleton-footer(1), token-private(1), type-faces(1), type-scale(1) |
| commons/governance/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | head-description(1), head-og(1), type-scale(1) |
| commons/governance/model-v4/governance-model-v4.html | verbatim | - | verbatim | - | clean |
| commons/governance/model-v5/index.html | topbar | inline | - | IBM Plex Mono,Libre Baskerville | skeleton-container(1), token-private(1), type-scale(1) |
| commons/governance/order-of-proceeding/index.html | topbar | inline | wrap | IBM Plex Mono,Inter,Libre Baskerville | skeleton-footer(1), token-private(1), type-faces(1), type-scale(1) |
| commons/governance/rules-of-order/index.html | topbar | inline | wrap | IBM Plex Mono,Inter,Libre Baskerville | skeleton-footer(1), token-private(1), type-faces(1), type-scale(1) |
| commons/im/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | type-scale(1) |
| commons/index.html | shell+topbar (public) | inline | - | IBM Plex Mono,Libre Baskerville | skeleton-container(1), token-private(1), type-scale(1) |
| commons/intelligences/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | color-function(2), token-private(1), type-scale(1) |
| commons/join/index.html | topbar | inline | - | IBM Plex Mono,Libre Baskerville | skeleton-container(1), type-scale(1) |
| commons/lp/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | token-private(1) |
| commons/matrix/index.html | topbar | inline | wrap | IBM Plex Mono,Inter,Libre Baskerville | skeleton-footer(1), token-private(1), type-faces(1), type-scale(1) |
| commons/opportunities/index.html | shell | inline | main=wrap-frame | IBM Plex Mono,Libre Baskerville | token-private(1), type-scale(1) |
| commons/patronage/counting-rules/index.html | topbar | inline | wrap | IBM Plex Mono,Inter,Libre Baskerville | skeleton-footer(1), token-private(1), type-faces(1), type-scale(1) |
| commons/patronage/index.html | topbar | inline | wrap | IBM Plex Mono,Inter,Libre Baskerville | skeleton-footer(1), token-private(1), type-faces(1), type-scale(1) |
| commons/prd/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | type-scale(1) |
| commons/prd/stories/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | head-description(1), head-og(1), type-scale(1) |
| commons/publishing/index.html | topbar | inline | wrap | IBM Plex Mono,Inter,Libre Baskerville | skeleton-footer(1), token-private(1), type-faces(1), type-scale(1) |
| commons/series/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | type-scale(1) |
| commons/standing/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | head-description(1), head-og(1), type-scale(1) |
| commons/transducer/a1/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | type-scale(1) |
| commons/transducer/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | type-scale(1) |
| commons/treasury/handbook/brief/index.html | topbar | inline | wrap | IBM Plex Mono,Inter,Libre Baskerville | skeleton-footer(1), token-private(1), type-faces(1), type-scale(1) |
| commons/treasury/handbook/briefing/index.html | topbar | inline | wrap | IBM Plex Mono,Inter,Libre Baskerville | skeleton-footer(1), token-private(1), type-faces(1), type-scale(1) |
| commons/treasury/handbook/index.html | topbar | inline | wrap | IBM Plex Mono,Inter,Libre Baskerville | skeleton-footer(1), token-private(1), type-faces(1), type-scale(1) |
| commons/treasury/index.html | topbar | inline | wrap | IBM Plex Mono,Inter,Libre Baskerville | skeleton-footer(1), token-private(1), type-faces(1), type-scale(1) |
| commons/treasury/policy/index.html | topbar | inline | wrap | IBM Plex Mono,Inter,Libre Baskerville | skeleton-footer(1), token-private(1), type-faces(1), type-scale(1) |
| commons/ui/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | token-private(1) |
| commons/vs/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | token-private(1) |
| community-of-practice/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | token-private(1), type-scale(1) |
| daybook/index.html | topbar | inline | - | IBM Plex Mono,Libre Baskerville | skeleton-container(1), token-private(1), type-scale(1) |
| design-system/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | token-private(1), type-scale(1) |
| encyclopedia/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | token-private(1), type-scale(1) |
| federation/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | type-scale(1) |
| index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | color-named(1), token-private(1), type-scale(1) |
| intranet/direct/index.html | shell | inline | main=wrap-frame | IBM Plex Mono,Libre Baskerville | token-private(1), type-scale(1) |
| intranet/federation/index.html | shell | inline | main=wrap-frame | IBM Plex Mono,Libre Baskerville | token-private(1), type-scale(1) |
| intranet/hud/index.html | topbar | inline | - | IBM Plex Mono,Libre Baskerville | color-function(2), skeleton-container(1), skeleton-footer(1), type-scale(1) |
| intranet/hud/mobile/index.html | topbar | - | - | - | color-function(1), head-mode-boot(1), skeleton-container(1), skeleton-footer(1), token-layer(1), type-scale(1) |
| intranet/index.html | shell | inline | main=wrap-frame | IBM Plex Mono,Libre Baskerville | token-private(1), type-scale(1) |
| intranet/legal/index.html | shell | inline | wrap,main=wrap-frame | IBM Plex Mono,Libre Baskerville | head-title(1), token-private(1), type-scale(1) |
| intranet/programs/index.html | shell | inline | main=wrap-frame | IBM Plex Mono,Libre Baskerville | color-function(1), token-private(1), type-scale(1) |
| intranet/record/index.html | shell | inline | main=wrap-frame | IBM Plex Mono,Libre Baskerville | color-function(1), token-private(1), type-scale(1) |
| intranet/revenue/index.html | shell | inline | main=wrap-frame | IBM Plex Mono,Libre Baskerville | token-private(1), type-scale(1) |
| intranet/share/index.html | shell | inline | main=wrap-frame | IBM Plex Mono,Libre Baskerville | token-private(1), type-scale(1) |
| intranet/treasury/index.html | shell | inline | main=wrap-frame | IBM Plex Mono,Libre Baskerville | token-private(1), type-scale(1) |
| intranet/verification/index.html | shell | inline | main=wrap-frame | IBM Plex Mono,Libre Baskerville | token-private(1), type-scale(1) |
| journal/draft/2026-08-20-techne-foundation/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | token-private(1), type-scale(1) |
| journal/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | token-private(1), type-scale(1) |
| launch/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | token-private(1), type-scale(1) |
| legal/board-memo-2026-08-19/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | head-canonical(1), head-favicon(1), head-og(1), type-scale(1) |
| legal/bylaws-analysis/changes/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | head-canonical(1), head-color-scheme(1), head-favicon(1), head-og(1), token-private(1), type-scale(1) |
| legal/bylaws-analysis/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | head-canonical(1), head-color-scheme(1), head-favicon(1), head-og(1), token-private(1), type-scale(1) |
| legal/bylaws-revision-1/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | head-canonical(1), head-favicon(1), head-og(1), type-scale(1) |
| legal/bylaws/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | head-canonical(1), head-color-scheme(1), head-favicon(1), head-og(1), token-private(1), type-scale(1) |
| legal/change-log/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | head-canonical(1), head-favicon(1), head-og(1), type-scale(1) |
| legal/community-supporter/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | head-canonical(1), head-color-scheme(1), head-favicon(1), head-og(1), token-private(1), type-scale(1) |
| legal/corrections/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | token-private(1), type-scale(1) |
| legal/counsel-memo/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | head-canonical(1), head-color-scheme(1), head-favicon(1), head-og(1), token-private(1), type-scale(1) |
| legal/first-meeting/confirmation/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | token-private(1), type-scale(1) |
| legal/first-meeting/index.html | topbar | inline | - | IBM Plex Mono,Libre Baskerville | skeleton-container(1), token-private(1) |
| legal/guild-participation-terms/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | head-canonical(1), head-favicon(1), head-og(1), type-scale(1) |
| legal/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | token-private(1), type-scale(1) |
| legal/maturity-model/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | token-private(1), type-scale(1) |
| legal/maturity-model/specification/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | token-private(1), type-scale(1) |
| legal/membership-agreement-analysis/changes/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | head-canonical(1), head-color-scheme(1), head-favicon(1), head-og(1), token-private(1), type-scale(1) |
| legal/membership-agreement-analysis/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | head-canonical(1), head-color-scheme(1), head-favicon(1), head-og(1), token-private(1), type-scale(1) |
| legal/membership-agreement/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | head-canonical(1), head-color-scheme(1), head-favicon(1), head-og(1), token-private(1), type-scale(1) |
| legal/minute-protocol/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | head-canonical(1), head-description(1), head-favicon(1), head-og(1), type-scale(1) |
| legal/participation-framework-amendment/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | head-canonical(1), head-favicon(1), head-og(1), type-scale(1) |
| legal/participation/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | head-og(1) |
| legal/privacy/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | token-private(1), type-scale(1) |
| legal/record-audit/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | token-private(1), type-scale(1) |
| legal/summary-of-changes/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | head-color-scheme(1), head-favicon(1), head-og(1), token-private(1), type-scale(1) |
| legal/terms/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | token-private(1), type-scale(1) |
| participation/detail/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | type-scale(1) |
| participation/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | type-scale(1) |
| philosoraptor/1/evening/index.html | topbar | inline | - | IBM Plex Mono,Libre Baskerville | skeleton-container(1), token-private(1), type-scale(1) |
| philosoraptor/1/evening/live/hud/index.html | topbar | - | - | IBM Plex Mono,Libre Baskerville | head-mode-boot(1), skeleton-container(1), token-layer(1), type-scale(1) |
| philosoraptor/1/evening/live/index.html | topbar | inline | - | IBM Plex Mono,Libre Baskerville | skeleton-container(1), token-private(1), type-scale(1) |
| what-grows/index.html | topbar | inline | wrap | IBM Plex Mono,Libre Baskerville | token-private(1), type-scale(1) |

## Detail

### head-color-scheme: color-scheme meta

Source: design-system#seo, required head block 1.

- `legal/bylaws-analysis/changes/index.html` (judgment): add <meta name="color-scheme" content="dark light"> (mechanical elsewhere; legal/ is never fixed by script)
- `legal/bylaws-analysis/index.html` (judgment): add <meta name="color-scheme" content="dark light"> (mechanical elsewhere; legal/ is never fixed by script)
- `legal/bylaws/index.html` (judgment): add <meta name="color-scheme" content="dark light"> (mechanical elsewhere; legal/ is never fixed by script)
- `legal/community-supporter/index.html` (judgment): add <meta name="color-scheme" content="dark light"> (mechanical elsewhere; legal/ is never fixed by script)
- `legal/counsel-memo/index.html` (judgment): add <meta name="color-scheme" content="dark light"> (mechanical elsewhere; legal/ is never fixed by script)
- `legal/membership-agreement-analysis/changes/index.html` (judgment): add <meta name="color-scheme" content="dark light"> (mechanical elsewhere; legal/ is never fixed by script)
- `legal/membership-agreement-analysis/index.html` (judgment): add <meta name="color-scheme" content="dark light"> (mechanical elsewhere; legal/ is never fixed by script)
- `legal/membership-agreement/index.html` (judgment): add <meta name="color-scheme" content="dark light"> (mechanical elsewhere; legal/ is never fixed by script)
- `legal/summary-of-changes/index.html` (judgment): add <meta name="color-scheme" content="dark light"> (mechanical elsewhere; legal/ is never fixed by script)

### head-title: title carries the Techne pattern

Source: design-system#seo, title pattern.

- `commons/bp/index.html` (judgment): title names neither Techne nor RegenHub: Build Protocol &middot; BP v2
- `intranet/legal/index.html` (judgment): title names neither Techne nor RegenHub: Legal &middot; Intranet

### head-description: description meta present

Source: design-system#seo, required head block 2.

- `commons/governance/index.html` (judgment): no description meta; a person writes it
- `commons/prd/stories/index.html` (judgment): no description meta; a person writes it
- `commons/standing/index.html` (judgment): no description meta; a person writes it
- `legal/minute-protocol/index.html` (judgment): no description meta; a person writes it

### head-canonical: canonical link present

Source: design-system#seo, required head block 2.

- `legal/board-memo-2026-08-19/index.html` (judgment): add canonical https://techne.coop/legal/board-memo-2026-08-19/ (mechanical elsewhere; legal/ is never fixed by script)
- `legal/bylaws-analysis/changes/index.html` (judgment): add canonical https://techne.coop/legal/bylaws-analysis/changes/ (mechanical elsewhere; legal/ is never fixed by script)
- `legal/bylaws-analysis/index.html` (judgment): add canonical https://techne.coop/legal/bylaws-analysis/ (mechanical elsewhere; legal/ is never fixed by script)
- `legal/bylaws-revision-1/index.html` (judgment): add canonical https://techne.coop/legal/bylaws-revision-1/ (mechanical elsewhere; legal/ is never fixed by script)
- `legal/bylaws/index.html` (judgment): add canonical https://techne.coop/legal/bylaws/ (mechanical elsewhere; legal/ is never fixed by script)
- `legal/change-log/index.html` (judgment): add canonical https://techne.coop/legal/change-log/ (mechanical elsewhere; legal/ is never fixed by script)
- `legal/community-supporter/index.html` (judgment): add canonical https://techne.coop/legal/community-supporter/ (mechanical elsewhere; legal/ is never fixed by script)
- `legal/counsel-memo/index.html` (judgment): add canonical https://techne.coop/legal/counsel-memo/ (mechanical elsewhere; legal/ is never fixed by script)
- `legal/guild-participation-terms/index.html` (judgment): add canonical https://techne.coop/legal/guild-participation-terms/ (mechanical elsewhere; legal/ is never fixed by script)
- `legal/membership-agreement-analysis/changes/index.html` (judgment): add canonical https://techne.coop/legal/membership-agreement-analysis/changes/ (mechanical elsewhere; legal/ is never fixed by script)
- `legal/membership-agreement-analysis/index.html` (judgment): add canonical https://techne.coop/legal/membership-agreement-analysis/ (mechanical elsewhere; legal/ is never fixed by script)
- `legal/membership-agreement/index.html` (judgment): add canonical https://techne.coop/legal/membership-agreement/ (mechanical elsewhere; legal/ is never fixed by script)
- `legal/minute-protocol/index.html` (judgment): add canonical https://techne.coop/legal/minute-protocol/ (mechanical elsewhere; legal/ is never fixed by script)
- `legal/participation-framework-amendment/index.html` (judgment): add canonical https://techne.coop/legal/participation-framework-amendment/ (mechanical elsewhere; legal/ is never fixed by script)

### head-og: Open Graph block complete

Source: design-system#seo, required head block 3.

- `commons/governance/index.html` (judgment): missing og:type, og:url, og:title, og:description, og:site_name, og:image; no description to derive from
- `commons/prd/stories/index.html` (judgment): missing og:type, og:url, og:title, og:description, og:site_name, og:image; no description to derive from
- `commons/standing/index.html` (judgment): missing og:type, og:url, og:title, og:description, og:site_name, og:image; no description to derive from
- `legal/board-memo-2026-08-19/index.html` (judgment): missing og:type, og:url, og:title, og:description, og:site_name, og:image; derived from title, description, canonical (mechanical elsewhere; legal/ is never fixed by script)
- `legal/bylaws-analysis/changes/index.html` (judgment): missing og:type, og:url, og:title, og:description, og:site_name, og:image; derived from title, description, canonical (mechanical elsewhere; legal/ is never fixed by script)
- `legal/bylaws-analysis/index.html` (judgment): missing og:type, og:url, og:title, og:description, og:site_name, og:image; derived from title, description, canonical (mechanical elsewhere; legal/ is never fixed by script)
- `legal/bylaws-revision-1/index.html` (judgment): missing og:type, og:url, og:title, og:description, og:site_name, og:image; derived from title, description, canonical (mechanical elsewhere; legal/ is never fixed by script)
- `legal/bylaws/index.html` (judgment): missing og:type, og:url, og:title, og:description, og:site_name, og:image; derived from title, description, canonical (mechanical elsewhere; legal/ is never fixed by script)
- `legal/change-log/index.html` (judgment): missing og:type, og:url, og:title, og:description, og:site_name, og:image; derived from title, description, canonical (mechanical elsewhere; legal/ is never fixed by script)
- `legal/community-supporter/index.html` (judgment): missing og:type, og:url, og:title, og:description, og:site_name, og:image; derived from title, description, canonical (mechanical elsewhere; legal/ is never fixed by script)
- `legal/counsel-memo/index.html` (judgment): missing og:type, og:url, og:title, og:description, og:site_name, og:image; derived from title, description, canonical (mechanical elsewhere; legal/ is never fixed by script)
- `legal/guild-participation-terms/index.html` (judgment): missing og:type, og:url, og:title, og:description, og:site_name, og:image; derived from title, description, canonical (mechanical elsewhere; legal/ is never fixed by script)
- `legal/membership-agreement-analysis/changes/index.html` (judgment): missing og:type, og:url, og:title, og:description, og:site_name, og:image; derived from title, description, canonical (mechanical elsewhere; legal/ is never fixed by script)
- `legal/membership-agreement-analysis/index.html` (judgment): missing og:type, og:url, og:title, og:description, og:site_name, og:image; derived from title, description, canonical (mechanical elsewhere; legal/ is never fixed by script)
- `legal/membership-agreement/index.html` (judgment): missing og:type, og:url, og:title, og:description, og:site_name, og:image; derived from title, description, canonical (mechanical elsewhere; legal/ is never fixed by script)
- `legal/minute-protocol/index.html` (judgment): missing og:type, og:url, og:title, og:description, og:site_name, og:image; no description to derive from
- `legal/participation-framework-amendment/index.html` (judgment): missing og:type, og:url, og:title, og:description, og:site_name, og:image; derived from title, description, canonical (mechanical elsewhere; legal/ is never fixed by script)
- `legal/participation/index.html` (judgment): missing og:type, og:url, og:title, og:description, og:site_name, og:image; derived from title, description, canonical (mechanical elsewhere; legal/ is never fixed by script)
- `legal/summary-of-changes/index.html` (judgment): missing og:type, og:image; derived from title, description, canonical (mechanical elsewhere; legal/ is never fixed by script)

### head-favicon: favicon linked from root

Source: design-system#seo, required head block 4.

- `legal/board-memo-2026-08-19/index.html` (judgment): add the two favicon links (mechanical elsewhere; legal/ is never fixed by script)
- `legal/bylaws-analysis/changes/index.html` (judgment): add the two favicon links (mechanical elsewhere; legal/ is never fixed by script)
- `legal/bylaws-analysis/index.html` (judgment): add the two favicon links (mechanical elsewhere; legal/ is never fixed by script)
- `legal/bylaws-revision-1/index.html` (judgment): add the two favicon links (mechanical elsewhere; legal/ is never fixed by script)
- `legal/bylaws/index.html` (judgment): add the two favicon links (mechanical elsewhere; legal/ is never fixed by script)
- `legal/change-log/index.html` (judgment): add the two favicon links (mechanical elsewhere; legal/ is never fixed by script)
- `legal/community-supporter/index.html` (judgment): add the two favicon links (mechanical elsewhere; legal/ is never fixed by script)
- `legal/counsel-memo/index.html` (judgment): add the two favicon links (mechanical elsewhere; legal/ is never fixed by script)
- `legal/guild-participation-terms/index.html` (judgment): add the two favicon links (mechanical elsewhere; legal/ is never fixed by script)
- `legal/membership-agreement-analysis/changes/index.html` (judgment): add the two favicon links (mechanical elsewhere; legal/ is never fixed by script)
- `legal/membership-agreement-analysis/index.html` (judgment): add the two favicon links (mechanical elsewhere; legal/ is never fixed by script)
- `legal/membership-agreement/index.html` (judgment): add the two favicon links (mechanical elsewhere; legal/ is never fixed by script)
- `legal/minute-protocol/index.html` (judgment): add the two favicon links (mechanical elsewhere; legal/ is never fixed by script)
- `legal/participation-framework-amendment/index.html` (judgment): add the two favicon links (mechanical elsewhere; legal/ is never fixed by script)
- `legal/summary-of-changes/index.html` (judgment): add the two favicon links (mechanical elsewhere; legal/ is never fixed by script)

### head-mode-boot: mode flash prevention inline before CSS

Source: design-system#seo, required head block 5.

- `intranet/hud/mobile/index.html` (judgment): no mode boot, and no light palette for it to select; decide the page's mode rule first
- `philosoraptor/1/evening/live/hud/index.html` (judgment): no mode boot, and no light palette for it to select; decide the page's mode rule first

### type-faces: two faces only: Libre Baskerville and IBM Plex Mono

Source: design-system#type, X-06 decision 2026-07-20.

- `commons/agency/index.html` (judgment): loads Inter
- `commons/build/launch/index.html` (judgment): loads Inter
- `commons/build/sms-05-ceremony/index.html` (judgment): loads Inter
- `commons/build/sms-bindings/index.html` (judgment): loads Inter
- `commons/governance/egress/index.html` (judgment): loads Inter
- `commons/governance/order-of-proceeding/index.html` (judgment): loads Inter
- `commons/governance/rules-of-order/index.html` (judgment): loads Inter
- `commons/matrix/index.html` (judgment): loads Inter
- `commons/patronage/counting-rules/index.html` (judgment): loads Inter
- `commons/patronage/index.html` (judgment): loads Inter
- `commons/publishing/index.html` (judgment): loads Inter
- `commons/treasury/handbook/brief/index.html` (judgment): loads Inter
- `commons/treasury/handbook/briefing/index.html` (judgment): loads Inter
- `commons/treasury/handbook/index.html` (judgment): loads Inter
- `commons/treasury/index.html` (judgment): loads Inter
- `commons/treasury/policy/index.html` (judgment): loads Inter

### type-scale: font sizes among the sizes commons.css uses

Source: observed convention only; no scale is adopted (v6 reverted, PR 276).

- `about/index.html` (observed): not among the commons sizes: 18px, 20px, 36px
- `accounting/counsel-memo/index.html` (observed): not among the commons sizes: 8.8px, 9.28px, 9.6px, 9.92px, 10.4px, 13.12px, 13.28px, 13.44px, 13.76px, 14.4px, 14.72px, 15.2px, 16.8px
- `accounting/index.html` (observed): not among the commons sizes: 9.6px, 10.4px, 13.76px, 15.04px, 27.2px
- `commonplace/index.html` (observed): not among the commons sizes: 9.6px, 9.92px, 10.4px, 10.56px, 11.2px, 13.6px, 14.08px, 14.4px, 14.72px, 15.04px, 15.2px, 15.68px, 16.8px, 18.4px, 32px
- `commons/agency/grants/index.html` (observed): not among the commons sizes: 18px, 20px, 23px, 36px
- `commons/agency/index.html` (observed): not among the commons sizes: 16.5px, 21px, 27px, 34px
- `commons/agreements/board-originated/index.html` (observed): not among the commons sizes: 14.5px
- `commons/agreements/comment-and-countersign/index.html` (observed): not among the commons sizes: 14.5px
- `commons/agreements/index.html` (observed): not among the commons sizes: 11.2px, 11.52px, 12.48px, 12.8px, 13.6px, 14.08px, 14.4px, 15.68px, 21.6px
- `commons/build/gates/index.html` (observed): not among the commons sizes: 9.6px, 9.92px, 10.4px, 11.52px, 11.84px, 14.08px, 14.72px, 15.04px, 16.8px, 23.2px, 27.2px, 28.8px
- `commons/build/index.html` (observed): not among the commons sizes: 9.6px, 9.92px, 10.4px, 11.2px, 11.52px, 12.48px, 12.8px, 14.4px, 16.8px, 22.4px
- `commons/build/instructions/index.html` (observed): not among the commons sizes: 9.6px, 9.92px, 10.4px, 11.2px, 11.52px, 12.48px, 13.12px, 13.44px, 14.08px, 14.4px, 15.04px, 16.8px, 23.2px, 27.2px, 28.8px
- `commons/build/launch/index.html` (observed): not among the commons sizes: 16.5px, 21px, 27px, 34px
- `commons/build/lexicon/index.html` (observed): not among the commons sizes: 9.92px, 10.4px, 12.48px, 12.8px, 13.6px, 14.08px, 15.04px, 16.8px, 23.2px, 27.2px, 28.8px
- `commons/build/run-through/index.html` (observed): not among the commons sizes: 9.6px, 9.92px, 10.4px, 11.52px, 11.84px, 14.08px, 14.72px, 15.04px, 16.8px, 23.2px, 27.2px, 28.8px
- `commons/build/run-through/organizers/index.html` (observed): not among the commons sizes: 9.92px, 10.4px, 11.2px, 11.52px, 11.84px, 14.08px, 14.4px, 16.32px, 16.8px, 23.2px, 27.2px, 28.8px
- `commons/build/sms-05-ceremony/index.html` (observed): not among the commons sizes: 16.5px, 21px, 27px, 34px
- `commons/build/sms-bindings/index.html` (observed): not among the commons sizes: 16.5px, 21px, 27px, 34px
- `commons/build/verification/index.html` (observed): not among the commons sizes: 9.6px, 9.92px, 10.4px, 13.44px, 14.08px, 14.4px, 14.72px, 15.04px, 16.8px, 23.2px, 25.6px, 27.2px, 28.8px
- `commons/build/walkthrough/index.html` (observed): not among the commons sizes: 9.6px, 9.92px, 10.4px, 11.52px, 11.84px, 14.08px, 14.72px, 15.04px, 16.8px, 23.2px, 27.2px, 28.8px
- `commons/directory/index.html` (observed): not among the commons sizes: 10.08px, 10.24px, 10.56px, 11.2px, 11.52px, 12.48px, 12.8px, 13.6px, 14.08px, 14.4px, 15.2px, 19.2px, 21.6px
- `commons/gatherings/index.html` (observed): not among the commons sizes: 10.08px, 10.4px, 11.2px, 11.52px, 12.48px, 12.8px, 13.6px, 14.08px, 14.4px, 15.2px, 17.6px, 21.6px
- `commons/governance/egress/index.html` (observed): not among the commons sizes: 16.5px, 21px, 27px, 34px
- `commons/governance/index.html` (observed): not among the commons sizes: 14.5px, 15.5px, 22px, 34px
- `commons/governance/model-v5/index.html` (observed): not among the commons sizes: 9.28px, 9.6px, 9.92px, 10.24px, 10.4px, 10.56px, 11.2px, 11.52px, 12.16px, 12.48px, 13.12px, 13.44px, 13.6px, 14.72px, 16.8px, 17.92px
- `commons/governance/order-of-proceeding/index.html` (observed): not among the commons sizes: 16.5px, 21px, 27px, 34px
- `commons/governance/rules-of-order/index.html` (observed): not among the commons sizes: 16.5px, 21px, 27px, 34px
- `commons/im/index.html` (observed): not among the commons sizes: 14.5px
- `commons/index.html` (observed): not among the commons sizes: 9.6px, 9.92px, 10.24px, 10.4px, 10.56px, 12.48px, 14.08px, 14.72px, 16.8px, 18px, 18.88px, 32px
- `commons/intelligences/index.html` (observed): not among the commons sizes: 8px, 12.8px, 13.12px, 13.44px, 13.76px, 14.72px, 15.2px, 15.68px, 16.32px, 16.8px, 18.4px, 20px, 24.8px, 30.4px
- `commons/join/index.html` (observed): not among the commons sizes: 9.92px, 11.2px, 11.52px, 12.8px, 13.12px, 13.6px, 14.4px, 15.2px, 20px
- `commons/matrix/index.html` (observed): not among the commons sizes: 16.5px, 21px, 27px, 34px
- `commons/opportunities/index.html` (observed): not among the commons sizes: 10.4px, 11.2px, 11.52px, 12.8px, 13.6px, 14.08px, 14.4px, 14.72px, 15.2px, 16.8px, 21.6px
- `commons/patronage/counting-rules/index.html` (observed): not among the commons sizes: 16.5px, 21px, 27px, 34px
- `commons/patronage/index.html` (observed): not among the commons sizes: 16.5px, 21px, 27px, 34px
- `commons/prd/index.html` (observed): not among the commons sizes: 36px
- `commons/prd/stories/index.html` (observed): not among the commons sizes: 14.5px, 22px
- `commons/publishing/index.html` (observed): not among the commons sizes: 16.5px, 21px, 27px, 34px
- `commons/series/index.html` (observed): not among the commons sizes: 14.5px
- `commons/standing/index.html` (observed): not among the commons sizes: 14.5px, 15.5px, 22px, 34px
- `commons/transducer/a1/index.html` (observed): not among the commons sizes: 14.5px, 15.5px, 22px, 34px
- `commons/transducer/index.html` (observed): not among the commons sizes: 14.5px, 15.5px, 22px, 34px
- `commons/treasury/handbook/brief/index.html` (observed): not among the commons sizes: 16.5px, 21px, 27px, 34px
- `commons/treasury/handbook/briefing/index.html` (observed): not among the commons sizes: 15.5px, 16.5px, 21px, 27px, 29px, 34px
- `commons/treasury/handbook/index.html` (observed): not among the commons sizes: 16.5px, 21px, 27px, 34px
- `commons/treasury/index.html` (observed): not among the commons sizes: 16.5px, 21px, 27px, 34px
- `commons/treasury/policy/index.html` (observed): not among the commons sizes: 16.5px, 21px, 27px, 34px
- `community-of-practice/index.html` (observed): not among the commons sizes: 18px, 36px
- `daybook/index.html` (observed): not among the commons sizes: 9.6px, 9.92px, 10.4px, 10.56px, 11.2px, 13.6px, 14.08px, 14.4px, 14.72px, 15.04px, 15.2px, 15.68px, 16.8px, 18.4px, 32px
- `design-system/index.html` (observed): not among the commons sizes: 18px, 26px, 27px, 34px
- `encyclopedia/index.html` (observed): not among the commons sizes: 8.5px, 18px, 32px
- `federation/index.html` (observed): not among the commons sizes: 16.5px, 18px, 26px
- `index.html` (observed): not among the commons sizes: 18px, 21px, 22px, 34px
- `intranet/direct/index.html` (observed): not among the commons sizes: 9.92px, 10.4px, 10.56px, 11.2px, 11.52px, 12.8px, 13.6px, 14.08px, 15.2px, 21.6px
- `intranet/federation/index.html` (observed): not among the commons sizes: 10.4px, 11.2px, 11.52px, 14.08px, 14.4px, 15.2px, 16.32px, 21.6px
- `intranet/hud/index.html` (observed): not among the commons sizes: 12.48px, 21px, 26px
- `intranet/hud/mobile/index.html` (observed): not among the commons sizes: 8.5px, 15.5px, 18px, 21px
- `intranet/index.html` (observed): not among the commons sizes: 10.4px, 11.2px, 11.52px, 12.8px, 13.12px, 13.6px, 14.4px, 22.4px, 25.6px
- `intranet/legal/index.html` (observed): not among the commons sizes: 11.2px, 12.8px
- `intranet/programs/index.html` (observed): not among the commons sizes: 9.92px, 10.4px, 11.2px, 11.52px, 12.8px, 13.6px, 14.08px, 14.4px, 14.72px, 15.2px, 16.8px, 21.6px
- `intranet/record/index.html` (observed): not among the commons sizes: 9.92px, 10.4px, 11.2px, 11.52px, 12.8px, 13.6px, 14.08px, 14.4px, 14.72px, 15.2px, 16.8px, 21.6px
- `intranet/revenue/index.html` (observed): not among the commons sizes: 9.6px, 9.92px, 10.4px, 11.2px, 11.52px, 12.48px, 12.8px, 13.6px, 14.08px, 14.72px, 15.2px, 18.4px, 20px, 21.6px
- `intranet/share/index.html` (observed): not among the commons sizes: 10.4px, 10.56px, 11.2px, 11.52px, 12.48px, 13.12px, 14.08px, 14.72px, 20px, 21.6px, 25.6px
- `intranet/treasury/index.html` (observed): not among the commons sizes: 9.92px, 10.4px, 11.2px, 11.52px, 12.48px, 12.8px, 13.6px, 14.08px, 14.72px, 15.2px, 18.4px, 20px, 21.6px
- `intranet/verification/index.html` (observed): not among the commons sizes: 9.6px, 9.92px, 10.4px, 10.56px, 11.2px, 11.52px, 11.84px, 12.8px, 13.44px, 13.76px, 14.08px, 14.72px, 18.4px, 22.4px, 25.6px
- `journal/draft/2026-08-20-techne-foundation/index.html` (observed): not among the commons sizes: 18px, 26px, 36px
- `journal/index.html` (observed): not among the commons sizes: 18px, 26px, 36px
- `launch/index.html` (observed): not among the commons sizes: 14.5px, 18px, 20px, 36px
- `legal/board-memo-2026-08-19/index.html` (observed): not among the commons sizes: 14.5px, 15.5px, 22px, 34px
- `legal/bylaws-analysis/changes/index.html` (observed): not among the commons sizes: 8.8px, 9.12px, 9.28px, 9.6px, 9.92px, 11.2px, 12.16px, 12.8px, 13.28px, 13.44px, 13.92px, 14.08px, 17.6px
- `legal/bylaws-analysis/index.html` (observed): not among the commons sizes: 8.96px, 9.28px, 9.6px, 9.92px, 10.4px, 11.52px, 12.8px, 12.96px, 13.12px, 13.28px, 13.44px, 13.6px, 14.08px, 14.72px, 18.4px, 26.4px
- `legal/bylaws-revision-1/index.html` (observed): not among the commons sizes: 14.5px, 15.5px, 22px, 34px
- `legal/bylaws/index.html` (observed): not among the commons sizes: 8.64px, 8.96px, 9.28px, 9.6px, 9.92px, 11.52px, 12.48px, 12.8px, 13.12px, 13.76px, 13.92px, 14.08px, 23.2px
- `legal/change-log/index.html` (observed): not among the commons sizes: 14.5px, 15.5px, 22px, 34px
- `legal/community-supporter/index.html` (observed): not among the commons sizes: 8.64px, 8.96px, 9.6px, 9.92px, 10.4px, 11.2px, 11.52px, 12.48px, 12.8px, 13.12px, 13.76px, 13.92px, 14.08px, 23.2px
- `legal/corrections/index.html` (observed): not among the commons sizes: 18px, 20px
- `legal/counsel-memo/index.html` (observed): not among the commons sizes: 8.8px, 9.28px, 9.6px, 10.4px, 13.12px, 13.28px, 13.92px, 14.08px, 14.4px, 14.72px, 15.36px
- `legal/first-meeting/confirmation/index.html` (observed): not among the commons sizes: 18px, 32px
- `legal/guild-participation-terms/index.html` (observed): not among the commons sizes: 14.5px, 15.5px, 22px, 34px
- `legal/index.html` (observed): not among the commons sizes: 18px, 32px
- `legal/maturity-model/index.html` (observed): not among the commons sizes: 15.5px, 18px, 22px
- `legal/maturity-model/specification/index.html` (observed): not among the commons sizes: 14.5px, 16.5px, 21px
- `legal/membership-agreement-analysis/changes/index.html` (observed): not among the commons sizes: 8.8px, 9.12px, 9.28px, 9.6px, 9.92px, 11.2px, 12.8px, 13.28px, 13.44px, 13.92px, 14.08px, 17.6px
- `legal/membership-agreement-analysis/index.html` (observed): not among the commons sizes: 8.96px, 9.28px, 9.6px, 9.92px, 10.4px, 11.52px, 12.8px, 12.96px, 13.12px, 13.28px, 13.44px, 13.6px, 14.08px, 14.72px, 18.4px, 26.4px
- `legal/membership-agreement/index.html` (observed): not among the commons sizes: 8.64px, 8.96px, 9.28px, 9.6px, 9.92px, 11.52px, 12.48px, 12.8px, 13.12px, 13.76px, 13.92px, 14.08px, 23.2px
- `legal/minute-protocol/index.html` (observed): not among the commons sizes: 14.5px, 15.5px, 22px, 34px
- `legal/participation-framework-amendment/index.html` (observed): not among the commons sizes: 14.5px, 15.5px, 22px, 34px
- `legal/privacy/index.html` (observed): not among the commons sizes: 18px, 20px
- `legal/record-audit/index.html` (observed): not among the commons sizes: 18px, 20px
- `legal/summary-of-changes/index.html` (observed): not among the commons sizes: 8.32px, 8.64px, 8.8px, 8.96px, 9.28px, 9.6px, 9.92px, 10.08px, 11.52px, 12.48px, 13.12px, 13.28px, 13.92px, 14.08px, 14.88px, 30.4px
- `legal/terms/index.html` (observed): not among the commons sizes: 18px, 20px
- `participation/detail/index.html` (observed): not among the commons sizes: 14.5px, 16.5px, 18px, 26px
- `participation/index.html` (observed): not among the commons sizes: 14.5px, 16.5px, 18px, 26px
- `philosoraptor/1/evening/index.html` (observed): not among the commons sizes: 18px, 22px, 34px
- `philosoraptor/1/evening/live/hud/index.html` (observed): not among the commons sizes: 18px
- `philosoraptor/1/evening/live/index.html` (observed): not among the commons sizes: 14.5px, 18px, 22px, 34px
- `what-grows/index.html` (observed): not among the commons sizes: 18px, 21px, 36px

### token-layer: page defines both mode palettes or links commons.css

Source: design-system#tokens; AGENTS.md REPO.

- `intranet/hud/mobile/index.html` (judgment): defines no dark and light palette and does not link commons.css
- `philosoraptor/1/evening/live/hud/index.html` (judgment): defines no dark and light palette and does not link commons.css

### token-private: custom properties the canonical layer does not name

Source: observed convention only; commons/ui/commons.css is the token layer.

- `about/index.html` (observed): --blue-dim, --ember-dim, --info-dim, --ok-dim, --on-accent, --sky-glow, --sky-line, --warn-dim
- `accounting/counsel-memo/index.html` (observed): --border, --border-dim, --gold, --moss, --plum, --rust, --sky, --text-dim, --text-muted, --text-warm
- `accounting/index.html` (observed): --border, --border-dim, --gold, --text-dim, --text-muted, --text-warm
- `commonplace/index.html` (observed): --ok-dim, --sky-line, --warn-dim
- `commons/agency/grants/index.html` (observed): --blue-dim, --ember-dim, --info-dim, --ok-dim, --on-accent, --sky-glow, --sky-line, --warn-dim
- `commons/agency/index.html` (observed): --amber, --coral, --gold, --rose, --sans, --sky-line, --twilight
- `commons/agreements/index.html` (observed): --ok-dim, --on-accent
- `commons/build/gates/index.html` (observed): --ok-dim, --sky-line, --warn-dim
- `commons/build/index.html` (observed): --ember-dim, --info-dim, --ok-dim, --warn-dim
- `commons/build/instructions/index.html` (observed): --ember-dim, --info-dim, --ok-dim, --warn-dim
- `commons/build/launch/index.html` (observed): --sans, --sky-line
- `commons/build/lexicon/index.html` (observed): --ok-dim, --sky-line, --warn-dim
- `commons/build/run-through/index.html` (observed): --ok-dim, --sky-line, --warn-dim
- `commons/build/run-through/organizers/index.html` (observed): --ok-dim, --sky-line, --warn-dim
- `commons/build/sms-05-ceremony/index.html` (observed): --sans
- `commons/build/sms-bindings/index.html` (observed): --sans
- `commons/build/verification/index.html` (observed): --ok-dim, --sky-line, --warn-dim
- `commons/build/walkthrough/index.html` (observed): --ok-dim, --sky-line, --warn-dim
- `commons/directory/index.html` (observed): --ok-dim, --on-accent, --warn-dim
- `commons/gatherings/index.html` (observed): --ok-dim, --on-accent, --warn-dim
- `commons/governance/egress/index.html` (observed): --sans, --sky-line
- `commons/governance/model-v5/index.html` (observed): --blue-dim, --k-amber, --k-blue, --k-coral, --k-gold, --k-green, --k-rose, --k-violet
- `commons/governance/order-of-proceeding/index.html` (observed): --sans, --sky-line
- `commons/governance/rules-of-order/index.html` (observed): --sans, --sky-line
- `commons/index.html` (observed): --blue-dim, --ember-dim, --ok-dim, --on-accent
- `commons/intelligences/index.html` (observed): --face-display, --face-doc, --face-ui, --sab, --sal, --sar, --sat, --tap, --vh
- `commons/lp/index.html` (observed): --sans
- `commons/matrix/index.html` (observed): --amber, --coral, --gold, --rose, --sans, --sky-line, --twilight
- `commons/opportunities/index.html` (observed): --ok-dim, --on-accent, --warn-dim
- `commons/patronage/counting-rules/index.html` (observed): --sans, --sky-line
- `commons/patronage/index.html` (observed): --amber, --coral, --gold, --rose, --sans, --sky-line, --twilight
- `commons/publishing/index.html` (observed): --amber, --coral, --gold, --rose, --sans, --sky-line, --twilight
- `commons/treasury/handbook/brief/index.html` (observed): --sans, --sky-line
- `commons/treasury/handbook/briefing/index.html` (observed): --sans, --sky-line
- `commons/treasury/handbook/index.html` (observed): --sans, --sky-line
- `commons/treasury/index.html` (observed): --amber, --coral, --gold, --rose, --sans, --sky-line, --twilight
- `commons/treasury/policy/index.html` (observed): --sans, --sky-line
- `commons/ui/index.html` (observed): --sans
- `commons/vs/index.html` (observed): --sans
- `community-of-practice/index.html` (observed): --blue-dim, --ember-dim, --info-dim, --ok-dim, --on-accent, --sky-glow, --sky-line, --warn-dim
- `daybook/index.html` (observed): --ok-dim, --sky-line, --warn-dim
- `design-system/index.html` (observed): --dawn-gold, --dawn-indigo, --dawn-lilac, --dawn-rose, --dawn-shell, --dawn-slate
- `encyclopedia/index.html` (observed): --blue-dim, --ember-dim
- `index.html` (observed): --blue-dim, --ember-dim, --info-dim, --ok-dim, --on-accent, --sky-glow, --sky-line, --warn-dim
- `intranet/direct/index.html` (observed): --blue-dim, --ember-dim, --info-dim, --ok-dim, --on-accent, --warn-dim
- `intranet/federation/index.html` (observed): --blue-dim, --ember-dim, --info-dim, --ok-dim, --on-accent, --warn-dim
- `intranet/index.html` (observed): --blue-dim, --ember-dim, --info-dim, --ok-dim, --on-accent, --warn-dim
- `intranet/legal/index.html` (observed): --blue-dim, --ember-dim, --info-dim, --ok-dim, --on-accent, --warn-dim
- `intranet/programs/index.html` (observed): --blue-dim, --ember-dim, --info-dim, --ok-dim, --on-accent, --warn-dim
- `intranet/record/index.html` (observed): --blue-dim, --ember-dim, --info-dim, --ok-dim, --on-accent, --warn-dim
- `intranet/revenue/index.html` (observed): --blue-dim, --ember-dim, --info-dim, --ok-dim, --on-accent, --warn-dim
- `intranet/share/index.html` (observed): --blue-dim, --ember-dim, --info-dim, --ok-dim, --on-accent, --warn-dim
- `intranet/treasury/index.html` (observed): --blue-dim, --ember-dim, --info-dim, --ok-dim, --on-accent, --warn-dim
- `intranet/verification/index.html` (observed): --blue-dim, --ember-dim, --info-dim, --ok-dim, --on-accent, --warn-dim
- `journal/draft/2026-08-20-techne-foundation/index.html` (observed): --blue-dim, --ember-dim, --info-dim, --ok-dim, --on-accent, --sky-glow, --sky-line, --warn-dim
- `journal/index.html` (observed): --blue-dim, --ember-dim, --info-dim, --ok-dim, --on-accent, --sky-glow, --sky-line, --warn-dim
- `launch/index.html` (observed): --blue-dim, --ember-dim, --info-dim, --ok-dim, --on-accent, --sky-glow, --sky-line, --warn-dim
- `legal/bylaws-analysis/changes/index.html` (observed): --border, --border-dim, --gold, --moss, --rust, --sky, --text-dim, --text-muted, --text-warm
- `legal/bylaws-analysis/index.html` (observed): --border, --border-dim, --gold, --moss, --rust, --sky, --text-dim, --text-muted, --text-warm
- `legal/bylaws/index.html` (observed): --blue-dim, --ember-dim
- `legal/community-supporter/index.html` (observed): --blue-dim, --ember-dim
- `legal/corrections/index.html` (observed): --ember-dim, --ok-text, --warn-text
- `legal/counsel-memo/index.html` (observed): --border, --border-dim, --gold, --moss, --plum, --rust, --sky, --text-dim, --text-muted, --text-warm
- `legal/first-meeting/confirmation/index.html` (observed): --blue-dim, --ember-dim, --ok-dim, --ok-text
- `legal/first-meeting/index.html` (observed): --blue-dim, --ember-dim
- `legal/index.html` (observed): --blue-dim, --ember-dim, --ok-dim, --ok-text
- `legal/maturity-model/index.html` (observed): --blue-dim, --ember-dim, --ok-dim, --ok-text, --warn-text
- `legal/maturity-model/specification/index.html` (observed): --ok-text, --warn-text
- `legal/membership-agreement-analysis/changes/index.html` (observed): --border, --border-dim, --gold, --moss, --rust, --sky, --text-dim, --text-muted, --text-warm
- `legal/membership-agreement-analysis/index.html` (observed): --border, --border-dim, --gold, --moss, --rust, --sky, --text-dim, --text-muted, --text-warm
- `legal/membership-agreement/index.html` (observed): --blue-dim, --ember-dim
- `legal/privacy/index.html` (observed): --ember-dim, --ok-text, --warn-text
- `legal/record-audit/index.html` (observed): --ember-dim, --ok-text, --warn-text
- `legal/summary-of-changes/index.html` (observed): --border, --border-dim, --gold, --moss, --rust, --sky, --text-dim, --text-muted, --text-warm
- `legal/terms/index.html` (observed): --ember-dim, --ok-text, --warn-text
- `philosoraptor/1/evening/index.html` (observed): --ok-dim, --warn-dim
- `philosoraptor/1/evening/live/index.html` (observed): --dawn-gold, --dawn-indigo, --dawn-lilac, --dawn-rose, --dawn-shell, --dawn-slate
- `what-grows/index.html` (observed): --blue-dim, --ember-dim, --info-dim, --ok-dim, --on-accent, --sky-glow, --sky-line, --warn-dim

### color-function: no rgb()/rgba()/hsl() literal outside a token definition

Source: design-system#tokens: never past a token to a literal.

- `accounting/counsel-memo/index.html` (judgment): .badge-blocking { background: rgba(154,90,90,0.18) }
- `accounting/counsel-memo/index.html` (judgment): .badge-blocking { border: 1px solid rgba(154,90,90,0.3) }
- `accounting/counsel-memo/index.html` (judgment): .badge-advisable { background: rgba(196,149,106,0.12) }
- `accounting/counsel-memo/index.html` (judgment): .badge-advisable { border: 1px solid rgba(196,149,106,0.25) }
- `accounting/counsel-memo/index.html` (judgment): .badge-clarifying { background: rgba(90,122,154,0.12) }
- `accounting/counsel-memo/index.html` (judgment): .badge-clarifying { border: 1px solid rgba(90,122,154,0.25) }
- `accounting/counsel-memo/index.html` (judgment): .badge-resolved { background: rgba(106,138,94,0.12) }
- `accounting/counsel-memo/index.html` (judgment): .badge-resolved { border: 1px solid rgba(106,138,94,0.25) }
- `accounting/counsel-memo/index.html` (judgment): .mat-btn.active[data-filter="all"] { background: rgba(200,188,168,0.10) }
- `accounting/counsel-memo/index.html` (judgment): .mat-btn.active[data-filter="all"] { border-color: rgba(200,188,168,0.3) }
- `accounting/counsel-memo/index.html` (judgment): .mat-btn.active[data-filter="blocking"] { background: rgba(154,90,90,0.15) }
- `accounting/counsel-memo/index.html` (judgment): .mat-btn.active[data-filter="blocking"] { border-color: rgba(154,90,90,0.4) }
- `accounting/counsel-memo/index.html` (judgment): .mat-btn.active[data-filter="advisable"] { background: rgba(196,149,106,0.12) }
- `accounting/counsel-memo/index.html` (judgment): .mat-btn.active[data-filter="advisable"] { border-color: rgba(196,149,106,0.35) }
- `accounting/counsel-memo/index.html` (judgment): .mat-btn.active[data-filter="clarifying"] { background: rgba(90,122,154,0.12) }
- `accounting/counsel-memo/index.html` (judgment): .mat-btn.active[data-filter="clarifying"] { border-color: rgba(90,122,154,0.35) }
- `accounting/counsel-memo/index.html` (judgment): style attribute: display:block;margin-top:0.6rem;padding-top:0.6rem;border-to
- `commons/agreements/index.html` (judgment): .sign-btn:hover { background: rgba(196,149,106,0.10) }
- `commons/agreements/index.html` (judgment): .notice.err { background: rgba(196,106,106,0.10) }
- `commons/directory/index.html` (judgment): .cis-drawer-backdrop { background: rgba(0,0,0,0.45) }
- `commons/directory/index.html` (judgment): .notice.info { background: rgba(106,138,196,0.10) }
- `commons/gatherings/index.html` (judgment): .notice.info { background: rgba(106,138,196,0.10) }
- `commons/gatherings/index.html` (judgment): .cis-drawer-backdrop { background: rgba(0,0,0,0.45) }
- `commons/intelligences/index.html` (judgment): .scrim { background: rgba(8,8,10,.66) }
- `commons/intelligences/index.html` (judgment): html[data-mode="light"] .scrim { background: rgba(26,26,31,.42) }
- `intranet/hud/index.html` (judgment): .glpop { box-shadow: 0 8px 30px rgba(0,0,0,.35) }
- `intranet/hud/index.html` (judgment): .coach { box-shadow: 0 10px 34px rgba(0,0,0,.42) }
- `intranet/hud/mobile/index.html` (judgment): #hudroot aside { box-shadow: 0 -12px 34px rgba(0,0,0,.35) }
- `intranet/programs/index.html` (judgment): .cis-drawer-backdrop { background: rgba(0,0,0,0.45) }
- `intranet/record/index.html` (judgment): .cis-drawer-backdrop { background: rgba(0,0,0,0.45) }

### color-named: no named CSS color outside a token definition

Source: design-system#tokens: never past a token to a literal.

- `index.html` (judgment): .btn.primary:hover { background: color-mix(in srgb, var(--blue) 88%, white) }

### skeleton-container: one of the three containers: wrap, wrap-hud, wrap-frame

Source: design-system#layout; commons.css the two grammars.

- `commonplace/index.html` (judgment): none of wrap, wrap-hud, wrap-frame, or the framed main measure
- `commons/build/gates/index.html` (judgment): none of wrap, wrap-hud, wrap-frame, or the framed main measure
- `commons/build/index.html` (judgment): none of wrap, wrap-hud, wrap-frame, or the framed main measure
- `commons/build/instructions/index.html` (judgment): none of wrap, wrap-hud, wrap-frame, or the framed main measure
- `commons/build/lexicon/index.html` (judgment): none of wrap, wrap-hud, wrap-frame, or the framed main measure
- `commons/build/run-through/index.html` (judgment): none of wrap, wrap-hud, wrap-frame, or the framed main measure
- `commons/build/run-through/organizers/index.html` (judgment): none of wrap, wrap-hud, wrap-frame, or the framed main measure
- `commons/build/verification/index.html` (judgment): none of wrap, wrap-hud, wrap-frame, or the framed main measure
- `commons/build/walkthrough/index.html` (judgment): none of wrap, wrap-hud, wrap-frame, or the framed main measure
- `commons/governance/model-v5/index.html` (judgment): none of wrap, wrap-hud, wrap-frame, or the framed main measure
- `commons/index.html` (judgment): none of wrap, wrap-hud, wrap-frame, or the framed main measure
- `commons/join/index.html` (judgment): none of wrap, wrap-hud, wrap-frame, or the framed main measure
- `daybook/index.html` (judgment): none of wrap, wrap-hud, wrap-frame, or the framed main measure
- `intranet/hud/index.html` (judgment): none of wrap, wrap-hud, wrap-frame, or the framed main measure
- `intranet/hud/mobile/index.html` (judgment): none of wrap, wrap-hud, wrap-frame, or the framed main measure
- `legal/first-meeting/index.html` (judgment): none of wrap, wrap-hud, wrap-frame, or the framed main measure
- `philosoraptor/1/evening/index.html` (judgment): none of wrap, wrap-hud, wrap-frame, or the framed main measure
- `philosoraptor/1/evening/live/hud/index.html` (judgment): none of wrap, wrap-hud, wrap-frame, or the framed main measure
- `philosoraptor/1/evening/live/index.html` (judgment): none of wrap, wrap-hud, wrap-frame, or the framed main measure

### skeleton-footer: a footer element closes the page

Source: observed convention: commons.css footer; notice_audit.py.

- `accounting/counsel-memo/index.html` (judgment): no footer element
- `accounting/index.html` (judgment): no footer element
- `commons/agency/index.html` (judgment): no footer element
- `commons/build/launch/index.html` (judgment): no footer element
- `commons/build/sms-05-ceremony/index.html` (judgment): no footer element
- `commons/build/sms-bindings/index.html` (judgment): no footer element
- `commons/governance/egress/index.html` (judgment): no footer element
- `commons/governance/order-of-proceeding/index.html` (judgment): no footer element
- `commons/governance/rules-of-order/index.html` (judgment): no footer element
- `commons/matrix/index.html` (judgment): no footer element
- `commons/patronage/counting-rules/index.html` (judgment): no footer element
- `commons/patronage/index.html` (judgment): no footer element
- `commons/publishing/index.html` (judgment): no footer element
- `commons/treasury/handbook/brief/index.html` (judgment): no footer element
- `commons/treasury/handbook/briefing/index.html` (judgment): no footer element
- `commons/treasury/handbook/index.html` (judgment): no footer element
- `commons/treasury/index.html` (judgment): no footer element
- `commons/treasury/policy/index.html` (judgment): no footer element
- `intranet/hud/index.html` (judgment): no footer element
- `intranet/hud/mobile/index.html` (judgment): no footer element

