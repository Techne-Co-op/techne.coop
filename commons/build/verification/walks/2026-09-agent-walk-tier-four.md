# Verification walk · Agent walk, tier four (16 cards) · agent-walked

Standing: evidence sheet, unsigned. Walked by a Fable 5.1 session under Nou's orchestration on 2026-09-03, against main at 891a46163d26acba038934689398dc068b66b2ca. Every verdict below is the walker's proposal; a card is verified only when the steward reads its evidence and says the word (Verification Spec; instructions section 12). Nothing in this sheet changes a ledger mark.

How this sheet was made. Public pages were read with `curl -sL` and rendered with headless Chromium. Measurements (element positions, computed fonts, scroll widths, focus state, the view-transition event) were taken over the Chrome DevTools Protocol from a Node script at `/home/openclaw/shots/walk-X-38/cdp.mjs`, with device metrics set to 1280x900, 1920x1080, or 390x844. Every 390px render is emulated at 390px, not a phone. Renders without a `techne-mode` key in localStorage are the default mode, which is light; dark renders planted `techne-mode=dark` before load. Signed-in surfaces were rendered under the stub harness (`scripts/cis-harness/stub.py`), which plants a fixture session as Todd Youngblood, steward and director, and answers every CIS call from fixtures; nothing reached the live CIS, and every such step says "rendered under the stub harness, fixture data". No form was submitted, no sign-in link sent, no live row written. Screenshots are under `/home/openclaw/shots/walk-X-38/` and are not committed. Cards are quoted from `commons/build/verification/cards.json`. Where a card asks for a judgement of taste or a real phone, the mechanical part was done and the rest is written down as the steward's.

## U-09 · The launch page joins the site
claim: "The launch page is the site's front page and must route a visitor everywhere they may need."
steps:
- Step 1, `curl -sL https://techne.coop/` (200, 43,874 bytes) and the render at `/home/openclaw/shots/walk-X-38/U-09-front.png`, signed out, 1280x900, light.
- Step 2, the primary hero action is `<a class="btn primary" href="#ways">Become a member</a>`. The anchor is live: `<section class="band" data-tint="rose" id="ways">` exists on the page, headed "Start wherever feels right." It is the ways-in section of the front page, not the join surface (`/commons/join/`). The join surface is reached from the later section `#hello` ("Want to be part of it?"), which links `/commons/join/`.
- Step 3, the three ways-in cards link `/participation/#community`, `/participation/#coworking` and `/participation/#cooperative`; `curl -sL https://techne.coop/participation/` returns 200 and the page carries `id="community"`, `id="coworking"` and `id="cooperative"` targets (the Community Participant, Co-working Participant and Cooperative Member cards).
- Step 4, links on the page: the topbar (injected by `/assets/topbar.js`) carries `/`, `/about/`, `/participation/`, `/commons/`, `/intranet/`; the footer carries `/participation/`, `/commons/join/`, `/commons/gatherings/`, `/intranet/`, `/commons/`, `/commons/build/`, `/legal/`, `/legal/#formation`. Not linked from the front page: `/design-system/`, `/commons/prd/stories/`, `/participation/detail/` (reachable one step further, from `/participation/`).
proposed verdict: fails
one sentence: U-09 fails as the walker reads step 2: the primary hero action "Become a member" lands on the front page's own `#ways` section (a live anchor, not a dead one) rather than on the join surface, while the three ways-in cards and the topbar and footer route as the card asks.
residue for the steward: decide whether landing on `#ways` satisfies "lands on the join surface"; if it does, the card holds on the walker's other evidence.

## U-14 · The front door, briefer
claim: "The front door was cut to a hero that reads in one breath plus three sections."
steps:
- Step 1, the hero markup (`section.hero`): eyebrow "technē · the old word for craft", `h1` "A community of practice, held in common." with the alt line "Soil, not a firm.", one paragraph of two sentences ("A cooperative in downtown Boulder where makers of many crafts work side by side, bring care to how technology gets made, and own the tools that come out of it. The doors are open."), then a `div.opened` panel ("The doors opened · August 14, 2026 · 1515 Walnut Street · Boulder, Colorado · Nothing ended that day. A workshop started keeping its own record.") and two actions. There is no countdown element on the page; the opened panel stands where the card expects one. Reading aloud is the steward's; the agent's reading is that the hero is a title, two sentences, a dated panel, and two buttons. Renders: `/home/openclaw/shots/walk-X-38/U-09-front.png` (1280) and `/home/openclaw/shots/walk-X-38/U-14-front-390.png` (emulated at 390px, not a phone).
- Step 2, sections below the hero, counted from the markup: five. `#ground` "Three words carry most of what we mean.", `#grows` "Four things take shape here, and each feeds the next.", `#shown` "Watch it form.", `#ways` "Start wherever feels right.", `#hello` "Want to be part of it?". The card names three (the workshop, the ways in, the join card).
- Step 3, both hero actions are in-page anchors: "Become a member" to `#ways` and "Start from the words we use" to `#ground`; both ids exist on the page.
proposed verdict: fails
one sentence: U-14 fails as written: the hero is two sentences plus title and two actions, and both actions land on real sections, but the page below the hero now carries five sections rather than three, and the countdown has become a "doors opened" panel.
residue for the steward: say whether the card's count of three still binds the page after the sections added since, or whether the card is to be re-pointed.

## P-10 · The front door reads like a front door
claim: "The participation front door should open with an action, not an explanation."
steps:
- Step 1, `curl -sL https://techne.coop/participation/` (200); render `/home/openclaw/shots/walk-X-38/P-10-participation.png`. Under the masthead ("The ways in", four sentences of lead) the first section is "Ways you can start now", two cards each ending in an action ("Come by", "Take a desk"). The first section is the doors.
- Step 2, the four standing questions are not on `/participation/`. They stand on `/participation/detail/` under the heading "The same four questions, for every way in", once, as the table's column heads: "A vote in how it runs", "A stake that grows", "A share of what it earns", "What it costs", with the statutory class term once beneath each way in ("Community Participant Class Three, at the hub", "Co-working Participant Class Two", "Guild Participant Class Three, virtual", "Cooperative Member Class One", "Investor Member Class Four").
- Step 3, the class set is rendered once as cards on `/participation/` (Community Participant, Co-working Participant, the guild card marked "Being built · not open yet", Cooperative Member, and Investor Member as a paragraph) and once in the `table.matrix` on `/participation/detail/`. Across the two pages there is no third rendering.
proposed verdict: holds
one sentence: P-10 holds as the walker reads it: the front door opens on two doors with actions, and the four questions and the class table now live once each on the detail page behind it, which is where P-11 moved them.
residue for the steward: the card places steps 2 and 3 on the front door; say whether their move to `/participation/detail/` under P-11 satisfies the card or wants the card re-pointed.

## P-11 · The door and the room behind it
claim: "The claim: the participation front door holds doors and nothing else; everything a visitor might want to study moved to a page behind it."
steps:
- Step 1, `/participation/` sections counted from the markup: three (`aria-labelledby="h-access"` "Ways you can start now", `h-patron` "Becoming an owner", `h-more` "The rest of it"). No `<table>` on the page, no timeline, no pathway prose; the word "pathway" does not occur, and "timeline" occurs once, in the pointer sentence to the detail page.
- Step 2, the first section's cards carry the actions "Come by" and "Take a desk"; nothing that is not a door sits between the masthead and them.
- Step 3, `/participation/detail/` (200), render `/home/openclaw/shots/walk-X-38/P-11-detail.png`: `table.matrix` with five ways in; `details.disclose` summarised "How participation becomes ownership · the two pathways" holding "At a desk" and "Anywhere on the access track"; and the timeline as steps "~90 days Relationship", "Day 0 Admission", "Each year Accumulation" and on. The walker did not diff the two pages against their pre-move state, so "content lost in the move" is not asserted either way.
- Step 4, footers: `/participation/`, `/participation/detail/` and `/` each end with "Called to order RegenHub, LCA is called to order: the board is seated and the governing instruments are board-adopted, with member ratification anticipated. Read the formation notice, which is right wherever a page disagrees with it."
proposed verdict: holds
one sentence: P-11 holds: the front door is three sections of doors with no table, timeline or pathway prose, the detail page carries the table, the two pathways and the timeline, and all three footers carry the formation line.
residue for the steward: none for the doors; whether anything was lost in the move is a comparison against the earlier page the walker did not make.

## P-09 · The two tracks told apart
claim: "The claim: the participation content lives in exactly one place, and the legal path points at it rather than keeping a second copy that can drift away from the first."
steps:
- Step 1, `/participation/` (200) and `/legal/participation/` (200, 5,751 bytes); renders `/home/openclaw/shots/walk-X-38/P-10-participation.png` and `/home/openclaw/shots/walk-X-38/P-09-legal-participation.png`.
- Step 2, `/legal/participation/` is a pointer: its only heading is "This page has moved." and its text says "Participation levels are described in one place now, at techne.coop/participation" and "one of them had to become a pointer. This one did, on August 12, 2026." No class names, no rates on the page (zero occurrences of "Community Participant", "$25", "$250", "$100").
- Step 3, `/legal/` (200), render `/home/openclaw/shots/walk-X-38/P-09-legal.png`: the page is titled "The filed instruments." and carries no row for the Guild Participation Terms; the word "Guild" does not occur on it. The page says "only filed instruments are published here" and points members to "the legal shelf on the intranet". Rendered under the stub harness, fixture data, `/intranet/legal/` carries the row "Guild Participation Terms · DRAFTED · NOT A MEMBER · The instrument for the virtual way in: Guild Participants, Class Three in the guild", render `/home/openclaw/shots/walk-X-38/P-09-intranet-legal.png`.
- Step 4, neither `/participation/` nor `/legal/participation/` shows a progress figure toward membership; `/participation/detail/` says outright "Nothing on this site will show you a score, a progress bar, or a percentage toward membership". `/participation/` does list the community tiers as "$25, $50, or $100 a month. Threshold, Footing, Standing." and the card says "None of these makes you an owner of the cooperative, and none of them is a lesser version of one."
proposed verdict: holds
one sentence: P-09 holds: the legal path is a dated pointer with no second copy, no page shows progress toward membership, and the Guild Participation Terms row stands marked Drafted on the intranet shelf rather than on `/legal/`, which now carries filed instruments only.
residue for the steward: say whether the three named community tiers with their prices read as a price ladder in the card's sense, and whether the Guild row's move to `/intranet/legal/` satisfies step 3.

## U-11 · The member surface speaks one language
claim: "The claim: nothing a member reads carries the build's private shorthand. No piece addresses, no migration numbers, no raw event ids in the words on the page."
steps:
- Step 1, rendered under the stub harness, fixture data: `/intranet/` ("Member intranet"), `/intranet/share/` ("Your share"), `/intranet/record/` ("The record"), `/intranet/treasury/` ("Treasury"), `/intranet/programs/` ("Programs"); renders `/home/openclaw/shots/walk-X-38/U-11-<surface>-1280.png`.
- Step 2, the rendered text of each surface was searched for piece addresses (`[A-Z]{1,4}-\d\d`), four-digit migration numbers, UUIDs and long hex strings. Overview, share and programs: none. Record: one, "The unresolved reading is logged at DOC-01·08." Treasury: nine, in member-facing prose, for example "when the card processor is connected (T-02)", "appears when the payment step is built (T-04)", "whether they belong to the cooperative (AC-03)", "once it has been checked and signed off (T-03)", "the step that shares out surplus (S-03, under the patronage rules)". No migration numbers, UUIDs or hashes on any of the five.
- Step 3, computed styles across the five: h1 in Libre Baskerville on every surface; buttons in IBM Plex Mono on every surface (programs adds one serif button); button radius 0 or 2px; card radius 0 or 2px; focus outline `rgb(74, 111, 176) solid 2px` on every surface; topbar 48px and side map 212px on every surface. Whether they look like one product is a reader's judgement; the agent's reading is that they do.
proposed verdict: fails
one sentence: U-11 fails: the treasury surface carries nine piece addresses (T-02, T-03, T-04, AC-03, S-03) and the record surface one (DOC-01·08) in the words on the page, while the five surfaces share type, radius and focus ring.
residue for the steward: look at the five and say whether they are one product; the leak finding stands on its own.

## U-12 · Two faces, no third
claim: "The claim: the estate sets its type in exactly two faces, the serif and the mono, and no third face survives anywhere in the system."
steps:
- Step 1, `/design-system/#type` reads: "Libre Baskerville carries the document voice and IBM Plex Mono carries the interface layer, labels, hashes, and the status bar: two faces" and "Re-emitted per U-12: Inter is retired from this page, from commons.css, and from the specimens below; the third face loads nowhere the system governs. Formation-era commons documents that inlined it stand until each page's own re-emission." Render `/home/openclaw/shots/walk-X-38/U-12-design-system.png`.
- Step 2, computed `font-family` read over every text-bearing element on `/`, `/participation/`, `/legal/`, `/commons/`, `/design-system/` and `/commons/prd/stories/`: exactly two values on every page, `"Libre Baskerville", Georgia, serif` and `"IBM Plex Mono", SFMono-Regular, Consolas, monospace`; h1 and body paragraphs are Libre Baskerville. `document.fonts` reports only IBM Plex Mono and Libre Baskerville loaded. Every Google Fonts request on the ten fetched pages names only those two families.
- Step 3, one stray declaration in the fetched set: the host's 404 page (`/join/`, not a page of the estate) sets `"Helvetica Neue", Helvetica, Arial, sans-serif`. No page loads or declares Inter.
proposed verdict: holds
one sentence: U-12 holds: the design system names the two faces, six public pages compute to exactly those two, and only the host's 404 page declares anything else.
residue for the steward: none.

## U-13 · One primary navigation for the public face
claim: "The claim: every public page carries the same single navigation bar, and no page carries a second one of its own."
steps:
- Step 1, six public pages: `/`, `/participation/`, `/legal/`, `/commons/`, `/design-system/`, `/commons/prd/stories/`.
- Step 2, on each, `.tc-topbar` is present at top 0, height 48px, `position: sticky`, text "Techne About Participation Commons Intranet" plus the mode control. Dark mode (localStorage `techne-mode=dark`) on `/` and `/legal/`: `data-mode="dark"`, body background `rgb(15, 15, 18)`, the same 48px topbar; renders `/home/openclaw/shots/walk-X-38/U-13-front-dark.png` and `/home/openclaw/shots/walk-X-38/U-13-legal-dark.png`.
- Step 3, `nav` elements per page: one (`nav.tc-nav`, "Site navigation") on five pages; two on `/commons/`, the second being the intranet map `nav.cis-side` at height 0 and `display: none` while signed out. No page renders a second visible bar.
proposed verdict: holds
one sentence: U-13 holds: the same 48px sticky topbar renders on six public pages in light and dark, and the only second nav element, the hidden member map on `/commons/`, does not render for a signed-out reader.
residue for the steward: none.

## U-20 · The frame measure
claim: "The claim: the framed pages share one text column, so the estate reads as one document rather than nine differently sized ones."
steps:
- Step 1, `/commons/` and `/legal/` at 390x844, 1280x900 and 1920x1080; renders `/home/openclaw/shots/walk-X-38/U-20-{commons,legal}-{390,1280,1920}.png`.
- Step 2, measured position of the h1 and the ancestor carrying the max-width. `/commons/` sits in the shell frame: `div.mast` with `max-width: 860px`, left-aligned at x=0, so the h1 starts at x=24 (390), x=77 (1280), x=115 (1920). `/legal/` uses `div.wrap` with `max-width: 780px`, centred, so the h1 starts at x=20 (390), x=267 (1280), x=587 (1920). At 1280 the two columns are 706px and 732px wide and their left edges differ by 190px; at 1920 by 472px. The design system's layout section says the container of every framed surface is `main.wrap-frame`; neither page uses that class (it appears only in `design-system/index.html`).
- Step 3, `document.documentElement.scrollWidth` equals the viewport width at every width on both pages: nothing scrolls sideways.
proposed verdict: fails
one sentence: U-20 fails as measured: nothing scrolls sideways, but `/commons/` reads in a left-aligned 860px shell frame and `/legal/` in a centred 780px column, and the two columns do not sit alike at any of the three widths.
residue for the steward: say whether `/legal/` is still a framed page in the card's sense (it loads neither `shell.css` nor `shell.js`); if it is not, the card wants a different second page.

## U-06 · The frame on a narrow screen
claim: "The claim: on a phone the member's page opens on the page they came for, with the map tucked into a drawer that gets out of the way once used."
steps:
- Step 1, rendered under the stub harness, fixture data, emulated at 390px, not a phone: `http://localhost:8899/_boot.html#/intranet/`; render `/home/openclaw/shots/walk-X-38/U-06-intranet-390-initial.png`.
- Step 2, the topbar's bottom edge is at y=48 and the first text of the page (the "Techne · RegenHub, LCA" kicker) at y=106, the h1 at y=131; nothing is under the bar. The map (`nav.cis-side`) is closed by stylesheet at this width (`max-height: 0; overflow: hidden`, shell.css).
- Step 3, clicked `#cis-menu-btn` ("Menu"): `.cis-side` gained `cis-open` and the button `aria-expanded="true"`; render `/home/openclaw/shots/walk-X-38/U-06-intranet-390-open.png` shows the map as a full-width list under the bar. Clicked it again: `cis-open` removed.
- Step 4, opened it once more and clicked the map's "Your share" link: the page landed on `/intranet/share/` (h1 "Your share") with `.cis-side` not carrying `cis-open`; render `/home/openclaw/shots/walk-X-38/U-06-intranet-390-after-destination.png`.
proposed verdict: deferred
one sentence: U-06 holds under emulation: the page begins under the bar, the Menu control opens and closes the map, and after a destination is tapped the drawer is closed over the page it landed on; the card asks for a phone.
residue for the steward: repeat on a phone, signed in, or say that 390px emulation satisfies the card.

## U-17 · The intranet in the hand
claim: "The claim: the members' surfaces behave in one hand. Nothing scrolls sideways, and no field is small enough to make the phone zoom in when you tap it."
steps:
- Step 1, rendered under the stub harness, fixture data, emulated at 390px, not a phone: overview, share, record, treasury, programs; renders `/home/openclaw/shots/walk-X-38/U-11-<surface>-390.png` and `/home/openclaw/shots/walk-X-38/U-17-record-390.png`.
- Step 2, layout width against the 390px visual viewport. Overview, share, treasury, programs: `scrollWidth` 390, no sideways movement. Record: the layout viewport widened to 421px (`innerWidth` 421, `visualViewport.width` 390), which is 31px of sideways travel; the cause is `table.state` (the "Document · Who may change it · Where it stands today · What it would take to change it" table), 404px wide with its right edge at x=420. On programs, the two "Affiliate" buttons extend to x=412 but the page clips them rather than scrolling.
- Step 3, computed font size of every visible input, select, textarea and button. No text field under 16px on any surface; the only controls under 16px are buttons (topbar Menu, Notices, Dark and sign-out at 11.2px; the programs surface's designate and affiliate buttons at 11.52px). Phones zoom on focus of text fields, not buttons, so no field on these surfaces should trigger it. Whether a phone does is the steward's to see.
proposed verdict: fails
one sentence: U-17 fails on one surface: the record page lays out 31px wider than a 390px viewport because its governance table does not fit, while the other four surfaces stay within the width and no text field on any of the five is under 16px.
residue for the steward: swipe the five on a phone; the record table is the one to look at first.

## U-19 · The frame before the paint
claim: "The claim: the frame is in the page before any script runs, and a signed-out reader never sees the member map, not even for a single frame."
steps:
- Step 1, rendered under the stub harness, fixture data: `/intranet/` signed in shows `data-cis="in"`, the 48px `.cis-topbar` ("Techne · intranet · Notices · Todd Youngblood · todd@example.org · Dark") and the 212px map with 17 links; render `/home/openclaw/shots/walk-X-38/U-19-intranet-stub.png`. The shipped markup, read with scripts disabled from the stub's copy of the repo, already contains the topbar and the 17-link `nav.cis-side`; the frame is in the HTML, not raised by script. A hard reload watched by eye is the steward's.
- Step 2, `https://techne.coop/intranet/` live, signed out, scripts on: `data-cis="out"`, `.cis-side` at `display: none`, width 0; the page shows the sign-in card ("Member intranet · For cooperative members. Enter your email address and we will send a sign-in link") and the topbar reads "not signed in"; render `/home/openclaw/shots/walk-X-38/U-19-intranet-signed-out.png`. The same URL with scripts disabled: `.cis-side` still `display: none`; render `/home/openclaw/shots/walk-X-38/U-19-intranet-signed-out-nojs.png`.
- Step 3, the gate is in the stylesheet, which is linked in the head: shell.css line 91, `html:not([data-cis="in"]) .cis-side { display: none; }`, with the comment that the test is the absence of `in`, so the map stays hidden until a script proves a session. The walker cannot capture a single frame between first paint and stylesheet application; the rule's placement is the evidence that there is none.
proposed verdict: holds
one sentence: U-19 holds on the walker's evidence: the frame and map ship in the markup, and the map is hidden by a stylesheet rule that holds until a script sets `data-cis="in"`, so a signed-out load with or without scripts never showed it.
residue for the steward: hard-reload a members' surface signed in and watch for a frameless flash; the stylesheet rule is the walker's reason to expect none.

## U-18 · The frame that never held
claim: "The claim: moving between two pages of the estate now carries a view transition, which it never did before, and the fix is measurable rather than a matter of taste."
steps:
- Step 1, desktop Chromium (headless, 1280x900) opened `https://techne.coop/commons/` and navigated by `location.assign` to `https://techne.coop/commons/build/`.
- Step 2, a listener planted before the new document loaded recorded, at `pagereveal`, `viewTransition: true` with a stylesheet carrying `@view-transition` present, and zero `unhandledrejection` events. On the destination the topbar computes `view-transition-name: tc-topbar`. The rule lives in `topbar.js` (`@view-transition{navigation:auto;}`, off under reduced motion) and in shell.css lines 55 to 68. The walker cannot perceive the transition by eye from a headless render.
- Step 3, the measurement matches the one the card quotes.
proposed verdict: holds
one sentence: U-18 holds on the measurement: a navigation from `/commons/` to `/commons/build/` reports `viewTransition: true` at `pagereveal` with the stylesheet present and no unhandled rejection.
residue for the steward: none, unless he wants to watch the topbar by eye.

## U-08 · The pattern library grows
claim: "The claim: the design system documents the patterns the surfaces actually use, and those patterns still work for a reader whose scripts do not run."
steps:
- Step 1, `/design-system/` sections found: `#icons` "Icon System" (one `<pre>` block with the inline Lucide SVG markup), `#hints` "Term Hints & Disclosure" (two `<pre>` blocks: the `span.term` with its button and `span.term-card`, and `details.disclose` with its summary), `#participation` "Participation Cards", `#forms` "Forms & States". The participation section describes the card's anatomy by class name (`.pgrid`, `.pcard`, `.p-track`, `.p-class`, `.p-name`, `.p-price` or `.p-cost`, `li.yes`, `li.no`, `.p-admit`, `.p-act`) and says the member curve "renders as .curve steps: when, what, one sentence"; the forms section describes `.field > label`, `.field-hint`, `.form-status`, `.skel`, `.absence` and `.first-run` the same way. Neither carries a `<pre>` markup block or a rendered example. There is no section headed for the member curve or for states on their own; they are lines inside the participation and forms sections.
- Step 2, `/participation/` with script execution disabled (no topbar was injected, confirming scripts were off): the "Patronage" term's card computed `display: none` before, `display: block` while the pointer hovered the button (`/home/openclaw/shots/walk-X-38/U-08-hint-hover-nojs.png`), `none` after; a Tab keypress from the preceding link put focus on the button with `:focus-visible` true and the card at `display: block` (`/home/openclaw/shots/walk-X-38/U-08-hint-focus-nojs.png`). The rule is CSS: `.term:hover > .term-card, .term > button:focus-visible + .term-card { display: block; }`.
- Step 3, `/participation/detail/` with scripts disabled: `details.disclose` is a native `<details>`; clicking its summary set `open` true and showed the body (`/home/openclaw/shots/walk-X-38/U-08-details-open-nojs.png`), a second click set it false.
proposed verdict: fails
one sentence: U-08 fails on the first step as the walker reads it: term hints and the disclosure work with scripts off and their markup is shown, but the participation card, member curve, forms and states sections describe their patterns by class name without showing markup.
residue for the steward: say whether a class-by-class anatomy counts as "show its markup"; steps 2 and 3 hold on the walker's evidence either way.

## P-07 · The participation stories
claim: "The claim: the stories page describes what a person can do today and marks everything else as waiting, rather than describing a system that does not exist yet."
steps:
- Step 1, `curl -sL https://techne.coop/commons/prd/stories/` (200, 58,132 bytes); render `/home/openclaw/shots/walk-X-38/P-07-stories.png`.
- Step 2, the level machinery: C-1 ("A community participant can enroll at the level that fits, Threshold, Footing, or Standing") and the day-one passage above it says "enrollment lands without a level and a steward carries it out of band until the level machinery is built (C-1)". The class personas: "no class-scoped persona has walked any of this in the rehearsal, so what a community participant can do is inferred from the member's walk rather than proven on their own, until P-03 lands (C-2, C-4)". Both read as waiting.
- Step 3, the carrier, E-9, is marked "Proposed · STANDING · P-05 designation" and carries the clause "designation itself stays name and purpose only, exactly as F-4 provides"; the path tally, B-7, is marked "Proposed · GUILD P-04 path tally" and carries "The tally is self-facing and never comparative; eligibility is a condition, not a target, which is how this story and X-3 hold together." The page does not use the words "reconciliation" or "2026-08-09"; the commit that published it (99585d2, 2026-08-09, "P-07: the participation stories, the capability register") names these two clauses as the reconciliations: "E-9 reconciled with F-4 by the carrier act beside the designation; B-7 and X-3 reconciled by the self-facing clause". The page's own dating line reads "Statuses shown are as of August 2026 and follow the Almanac; where a story waits, the chip names what it waits on."
proposed verdict: holds
one sentence: P-07 holds: the level machinery and the class personas read as waiting, and the carrier and the path tally each carry the reconciling clause the 2026-08-09 commit names, marked Proposed.
residue for the steward: none, beyond confirming that the two clauses are the reconciliation notes the card means.

## P-08 · The day-one journeys
claim: "The claim: every kind of arrival has an honest account of a first sitting, in which each claim either points at a story on the page or names the piece it is waiting on."
steps:
- Step 1, read passage A, "The stranger at the door", end to end: "A stranger arrives holding nothing and can read everything that would bind them [...] (A-1). If they decide, they apply at the front door in one sitting [...] (A-2). Within moments the steward hears it on the notices rail (A-3). Where it stops: nothing comes back to them. The acknowledgment to the applicant's own inbox waits on the mail seam clearing DNS (A-4), so from where the applicant stands, the first thing the cooperative does is go quiet."
- Step 2, each of its four claims cites a story on the page: A-1 marked "Live · /participation · /legal · /commons", A-2 "Live · /commons/join", A-3 "Live · notices rail", A-4 "Anticipated · DNS · notices rail". No claim in the passage lacks a story or a named wait.
- Step 3, the guild hand-off note is a paragraph in passage B: "Where it stops, and this one is worse than waiting: the participation index today invites a reader to join the guild and hands them to a way the front door does not carry, so the very first step of this sequence refuses without saying so, on the live site. Until the board adopts and P-02 builds the fifth way, the honest guild day one is that it cannot begin." The P3 refusal is the chip "Live · refusal · STANDING P3 · R1" on H-1 in section H and the sentence "the origin conferring no standing (P3, R1)". The page has no `<details>` element, so neither is collapsed.
proposed verdict: holds
one sentence: P-08 holds: passage A's four claims each cite a story with a standing, and the guild hand-off and the P3 refusal are in plain body text and chips rather than behind a disclosure.
residue for the steward: read the other four day-one passages if he wants the claim proven for every arrival; the walker read one, as the card asks.

## Tally

Cards walked: 16. Proposed holds: 9 (P-10, P-11, P-09, U-12, U-13, U-19, U-18, P-07, P-08). Proposed fails: 6 (U-09, U-14, U-11, U-20, U-17, U-08). Deferred: 1.

- U-06 deferred: the card asks for a phone; the walk was at 390px emulation and held there.

Of the six proposed fails, three rest on a reading the steward may overrule (U-09's landing on `#ways`, U-14's section count, U-08's anatomy-without-markup) and three on a measurement (U-11's addresses in treasury and record copy, U-20's two columns, U-17's record table at 421px).

Not taken: U-15 is not in this group; no sign-in link was sent; no form was submitted; no live row was read or written for any card in this tier.

Page defects seen on the way, reported not fixed: `/intranet/treasury/` and `/intranet/record/` carry piece addresses in member copy (U-11); `/intranet/record/` overflows a 390px viewport by 31px through `table.state` (U-17); `/commons/` renders em dashes in its lead and body prose (the phrase "The cooperative's shared record" is followed by an em dash before "named after"), against the house style; the front page's primary action goes to an in-page section rather than the join surface (U-09); the host's 404 page (`/join/`) sets Helvetica.

Checks run in this worktree at 891a461 with this sheet added: `scripts/validate.py`: "validate: 182 packets", rewrote STATUS.md and index.json without change, "validation passed (0 warning(s))"; `scripts/em_dash_audit.py`: "122 files, clean" (the three `&mdash;` entities on `/commons/` are outside what it flags); `scripts/almanac_audit.py`: "0 finding(s) over 182 addresses"; `scripts/verification_cards.py --check`: "cards.json is current".
