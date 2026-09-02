AGENT DIRECTIONS · the design system as instructions
techne.coop/design-system/AGENT-DIRECTIONS.md · U-32 · September 2026

READ    this file is the design system rewritten as directions an
        agent follows while writing or editing any page served from
        techne.coop. it adds no rule. every line below cites where
        the rule already stands. two sources govern, in this order:

        1. commons/ui/commons.css  the token layer and the shared
           patterns. canonical for every VALUE: a hex, a size, a
           spacing step, a face. scripts/token_audit.py refuses a
           page whose inline copy disagrees with it.
        2. /design-system/          the reference a person reads.
           canonical for every USAGE rule: what blue is for, where
           the sunset range may appear, how a head block is built.

        where this file and either source disagree, the source wins
        and this file is the defect. report it.

        the estate is static html on GitHub Pages. no build step, no
        framework, no shared public stylesheet: every page inlines
        the token layer and its own rules (AGENTS.md REPO). you are
        writing one self-contained document that must look like the
        others without loading anything they load.

STAND   decide nothing this file does not decide. the following are
        open and are not yours: a palette other than the v4 sunset
        range (Vermilion Hour and Juniper Twilight are proposals,
        /design-system/#palettes); a type scale (v6 drafted one and
        was reverted, PR 276); a new token; a fourth container; a
        third typeface. if a page needs one, file a stop card
        (AGENTS.md STOP) and use what exists.


1. CHOOSE THE GRAMMAR FIRST

        every page is one of four shapes. name it in the page's
        head comment, then build only that shape.
        (/design-system/#layout; commons.css "the two grammars")

        document      a reading column, prose-forward, scrolls.
                      container .wrap, max-width 920px, padding
                      0 var(--s5). masthead .mast, sections .sec.
                      most pages under /commons/, /legal/, /about/.
        instrument    widescreen, no-scroll intent, mono-forward.
                      container .wrap-hud, max-width 1600px.
                      the HUD surfaces under /intranet/hud/.
        framed        a signed-in members' surface inside the shell.
                      <main> carries the frame measure (section 4c),
                      never a class, never a pixel cap. every card
                      list is a .frame-grid. scripts/measure_audit.py
                      refuses drift.
        display       the front page only. max-width 70rem, gutters
                      clamp(var(--s5), 5vw, var(--s7)), interior
                      prose measures in ch. do not make a second one
                      without a stop card.

        a page loads exactly one frame (/design-system/#topbar;
        validate.py U-13): /assets/topbar.js for a public page,
        /assets/shell.css + /assets/shell.js for a signed-in page.
        a record page the members' map points at may load shell.js
        with data-public and keep topbar.js (U-15). no page carries
        an inline topbar of its own.


2. THE HEAD BLOCK, IN THIS ORDER

        copy this block. change only the marked values.
        (/design-system/#seo "Required <head> block")

        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="color-scheme" content="dark light">
        <title>PAGE NAME &middot; Techne</title>
        <meta name="description" content="ONE OR TWO SENTENCES, 120 TO 160 CHARACTERS">
        <link rel="canonical" href="https://techne.coop/PATH/">
        <meta property="og:type" content="website">
        <meta property="og:url" content="https://techne.coop/PATH/">
        <meta property="og:title" content="PAGE NAME · Techne">
        <meta property="og:description" content="SAME AS DESCRIPTION OR TIGHTER">
        <meta property="og:site_name" content="Techne">
        <meta property="og:image" content="https://techne.coop/assets/og-default.png">
        <link rel="icon" type="image/svg+xml" href="/favicon.svg">
        <link rel="alternate icon" type="image/png" href="/favicon.png" sizes="32x32">
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=IBM+Plex+Mono:ital,wght@0,300;0,400;0,500&display=swap" rel="stylesheet">
        <script>
          (function () {
            var stored = null;
            try { stored = localStorage.getItem('techne-mode'); } catch(e) {}
            var m = stored || (matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
            document.documentElement.setAttribute('data-mode', m);
          })();
        </script>
        <script src="/assets/topbar.js" defer></script>      public page
        <style> ... the token layer, then the page's rules ... </style>

        rules the block carries:
        - title pattern is "Page name · Techne"; the homepage alone
          is "Techne · technology as craft · Boulder"; a reference
          page is "Descriptor · Techne".
        - the description is distinct from every other page's, active
          voice, no "welcome to", leads with what the page holds.
        - the mode boot script is inline and sits BEFORE the first
          stylesheet or <style>. it prevents a flash of the wrong
          mode. never load it from a file.
        - a signed-in page replaces the topbar line with
          <link rel="stylesheet" href="/assets/shell.css"> then
          <script src="/assets/shell.js" defer></script>, after the
          error boundary, in that order (/design-system/#nav "Usage").
        - a members' surface adds <meta name="robots" content="noindex, nofollow">.
        - og:image is never omitted; fall back to the default.
        - fonts: the two families above and no other. Inter is
          retired (X-06, 2026-07-20). do not add Georgia to the link;
          it is a local fallback inside --serif only.


3. THE TOKEN LAYER

        3a. inline it verbatim. copy the three blocks below from
            commons/ui/commons.css into the page's <style> as its
            first rules: :root, html[data-mode="dark"],
            html[data-mode="light"]. do not retype values. do not
            omit a token you think the page will not use. token_audit
            refuses a copy whose value differs from commons.css.

        3b. never write a color literal outside a custom-property
            definition. no hex, no rgb(), no rgba(), no hsl(), no
            named color. a rule reads var(--name). token_audit refuses
            hex; this file extends the same rule to every literal
            form (/design-system/#tokens: "a component should never
            reach past a token to a literal hex").

        3c. if a page needs a tint of a token, derive it from the
            token in CSS: color-mix(in srgb, var(--ember) 12%, transparent).
            if a page must name that derivation, define it as a
            custom property whose value is itself built from tokens,
            and say in a comment which token it derives from.

        3d. the vocabulary. names are the contract; values resolve by
            mode. (commons.css :root and the two mode blocks;
            /design-system/#core, #light, #tokens)

            ground   --bg page ground · --inset wells, deepest ground ·
                     --surface cards and panels · --raised elevated
                     surfaces, hovered controls, table headers
            lines    --line hairline, the common divider · --rule the
                     heavier scope rule
            type     --heading titles · --text body copy · --muted
                     secondary text and labels · --faint decorative,
                     never load-bearing
            accent   --blue PRIMARY: edges, focus, primary action ·
                     --blue-text the readable form: links, type ·
                     --ember SECONDARY: section marks, provenance
                     edge, structure · --ember-text the readable form:
                     addresses, code
            state    --ok green: operational, verified, ratified, live ·
                     --info blue: in review, informational, simulated ·
                     --warn red: pending, rejected, wants attention
            sunset   --sun-gold --sun-amber --sun-coral --sun-rose
                     --sun-violet --sun-blue, mode-invariant, atmosphere
                     and data only; --sun-*-t the text-safe form per
                     mode, the only sunset value that may color type
            heat     --heat-1 .. --heat-5, the warm five as a magnitude
                     scale for encodings
            spacing  --s1 4px --s2 8px --s3 12px --s4 16px --s5 24px
                     --s6 32px --s7 48px --s8 64px. every margin,
                     padding, and gap is one of these or a clamp()
                     between two of them.
            motion   --dur .4s --micro .16s --ease cubic-bezier(.4,0,.2,1)
            faces    --serif "Libre Baskerville",Georgia,serif ·
                     --mono "IBM Plex Mono","SFMono-Regular",Consolas,monospace


4. THE PAGE SKELETON

        4a. document grammar. (commons.css masthead, sections, footer;
            /design-system/#components "Document page header")

            <body>
            <div class="wrap">
              <header class="mast">
                <div class="kick">SERIES &middot; DOCUMENT CODE</div>
                <h1>Title</h1>
                <p class="dek">One sentence of what the page holds.</p>
                <div class="meta"><span><b>v0.1</b></span><span>2026-09-02</span><span class="em">drafted</span></div>
              </header>

              <section class="sec" id="ADDRESS">
                <div class="addr">1</div>
                <h2>Section title</h2>
                <p class="lead">First paragraph.</p>
                <h3>a lowercase mono subhead</h3>
                <p>Body.</p>
              </section>

              <footer>
                <div class="row">
                  <span>SERIES NAME</span><span>document code</span><span>techne.coop/PATH</span><span>RegenHub, LCA &middot; Boulder, Colorado</span>
                </div>
                <div class="formation-foot"><span class="ff-mark">Called to order</span>RegenHub, LCA is called to order: the board is seated and the governing instruments are board-adopted, with member ratification anticipated. Read the <a href="/legal/#formation">formation notice</a>, which is right wherever a page disagrees with it.</div>
              </footer>
            </div>
            </body>

            - every section has an id that is its citable address,
              and .addr shows it. a section may take data-tint="gold"
              (or amber, coral, rose, violet, blue) to set --shue and
              --shue-t for its rule and address; walk the sweep in
              order, warm to cool, one stop per section
              (/design-system/#desert "The descent").
            - h2 sits on a 3px left border in the section's stop;
              h3 is 13px mono lowercase with a 1px bottom border.
            - prose measure inside a section is 68ch (.sec p).
            - the formation notice is the last thing in the footer,
              prose byte-identical to the copy above. only the CSS
              around it may differ. scripts/notice_audit.py checks
              every page.

        4b. instrument grammar. <div class="wrap-hud"> holding
            .stage, .tile, table.dt, .gauge, .heat, .bars as
            commons.css defines them. mono-forward, tabular numerals
            (.num), no-scroll intent.

        4c. framed grammar. (/design-system/#layout)

            <main> carries this rule, copied verbatim into the page:

            main { width:100%; max-width:70rem; margin-inline:auto;
                   padding-block:clamp(var(--s5), 3.5vw, var(--s7));
                   padding-inline:clamp(var(--s4), 3vw, var(--s6)); }

            every list of cards:
            <div class="frame-grid"> ... </div>
            <div class="frame-grid" style="--grid-min:150px"> ... </div>   dense numeric tiles only

            .frame-grid { display:grid;
              grid-template-columns:repeat(auto-fill, minmax(min(var(--grid-min, 300px), 100%), 1fr));
              gap:var(--s4); align-items:start; }

            do not give main a max-width in px. do not write a
            viewport breakpoint that changes a column count. do not
            introduce a second width. the measure audit fails the
            build on all three. prose inside the frame keeps 68ch.


5. COMPONENTS, BY CLASS NAME

        use the class as commons.css spells it; copy its rule into
        the page unchanged. (commons.css sections named in brackets)

        status chip    <span class="chip filed|ratified|drafted|anticipated|open|role"><span class="dot"></span>word</span>
                       always a word and a square mark; never color
                       alone. green carries filed and ratified, blue
                       carries drafted, red carries open; the word
                       carries the distinction. blocked is not a sixth
                       mark: it wears open and names its blocker.
                       [status chips]
        chip row       <div class="chiprow"> ... </div>
        provenance     <span class="prov"><b>source</b> &middot; date &middot; kind</span>   [provenance]
        button         <button class="btn primary|secondary" type="button">   32px, 2px radius,
                       primary reads blue, secondary reads ember, neither fills a panel  [buttons]
        record panel   .record > .rh (.rt title, .ra address) + .rb body   [record panel]
        excerpt        .excerpt > .xrow (.xd date, .xe text)
        anatomy        .anatomy > .an-row (.f field, .v value)
        register row   .reg > .reg-row (.no, .t, .d)                          [registers]
        definition     .def > .def-row (.t with .k kicker, .d)
        twin panels    .twin > .panel.decide / .panel.escalate (.ph .pt, .pb) [twin panels]
        escalation     .esc > .k + .er (.f, .v)                                [escalation card]
        memorandum     .memo > .k + p                                          [memorandum]
        metric tile    .tile > .tl label, .tf figure (mono, tabular), .ts sub  [instrument grammar]
        data table     table.dt; th lowercase mono; td.r right, td.s serif; tr.total
        agent block    pre.agent, the machine-facing block on a page
        term hint      <span class="term"><button type="button" aria-expanded="false">word</button>
                         <span class="term-card" role="note">definition ... <a href="/commons/build/lexicon/">Lexicon</a></span></span>
                       plus <script src="/assets/hints.js" defer>. never a title attribute.  [term hints]
        disclosure     <details class="disclose"><summary>one line <span class="sum-note">note</span></summary>
                         <div class="disclose-body">depth</div></details>     [disclosure]
        form           <form> > .field (label[for] + control + .field-hint) + .form-status[aria-live="polite"]
                       submit is the form's own event; the status line exists from first paint  [forms]
        participation  .pgrid > .pcard[data-tint] (.p-track, .p-class, .p-name, .p-price or .p-cost,
                       ul > li.yes|li.no, .p-admit, .p-act); .curve > .c-step   [participation cards]
        states         .skel loading (never a spinner) · .absence a sentence naming why and what it waits on ·
                       .first-run one dismissable orientation card   [states]
        icon           <svg class="lucide" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                         stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                       from the Lucide set, inlined, decorative beside a word, never a meaning alone.
                       sizes: 16px default, .lg 22px, .ico-well 44px well  [icons]
        sweep tint     data-tint="gold|amber|coral|rose|violet|blue" on a section, card, or container
                       sets --shue and --shue-t for everything inside  [sweep assignment]


6. COLOR RULES

        (/design-system/#core, #state, #desert)

        - blue is what a reader DOES: links, focus, primary action.
          ember is the cooperative's MARK on structure: section
          rules, addresses, provenance edges, code. read together;
          neither stands alone.
        - the three earth states appear only on instruments and
          chips. they never tint a panel or a heading. each is
          always paired with a word and a square mark.
        - the sunset range is atmosphere and data. it never colors a
          control, never carries the sign of a number, never tints
          body copy. type in a sunset stop uses the -t variant.
        - a tinted page walks the sweep top to bottom, warm to cool,
          one stop per section, via data-tint.
        - the desert register (horizon lines, the wash at four
          percent or less mixed from tokens) is guidance for a new
          public display surface and the question a review asks; it
          is not required of an existing page. do not retrofit it.
        - the v4 sunset range is the only range a page may use.
          Vermilion Hour and Juniper Twilight are proposals; adoption
          is the steward's word. never define --verm-* or --jun-*
          on a page.
        - dark is the default mode; light is a first-class mode, not
          an afterthought. every token you use must resolve in both.
          check both before opening a PR.


7. TYPE RULES

        (/design-system/#type; commons.css base)

        - two faces. Libre Baskerville is the document voice: body,
          headings, deks. IBM Plex Mono is the interface layer:
          labels, kickers, addresses, hashes, data, chips, footers.
        - body is font:400 16px/1.75 var(--serif) on a document page.
        - use the sizes commons.css already uses; there is no adopted
          scale, so a new size is a design decision (STAND). the
          sizes in force: 9, 9.5, 10, 10.5, 11, 11.5, 12, 12.5, 13,
          13.5, 14, 15, 16, 17, 17.5, 19, 24, 25, 28, 30, 38 px, and
          .68rem, .85em, 1.75rem where commons.css states them.
        - mono labels are uppercase with letter-spacing .08em to
          .12em (kickers) or lowercase (h3, table heads). pick the
          one commons.css uses for that component.
        - em is italic in --heading. code is mono in --ember-text on
          --inset. links underline, offset 3px, thicken on hover.


8. CONTENT AND REGISTER

        (/design-system/#standards; AGENTS.md STYLE, MARK)

        - no emoji, anywhere, ever. CI refuses it.
        - no em dashes in authored pages. CI refuses them. legal/
          and verbatim .said quotation are the named exemptions.
        - Subchapter K vocabulary only. the retired cooperative-tax
          terms are listed in CONTRIBUTORS.md and CI refuses them
          (style-lint, vocabulary quarantine); this file does not
          repeat them because the same check would read it.
        - every claim about an instrument wears its status mark:
          drafted, anticipated, open, filed, ratified. a draft says
          it is a draft in its masthead meta and its chip.
        - a member-facing surface speaks the cooperative's language:
          no packet addresses, table names, or project references
          on a member's page (U-05). those live in the almanac and
          the ledger.
        - arrows and geometry as Unicode text (U+2192, U+25C8), never
          the emoji variants.


9. ACCESSIBILITY, NON-NEGOTIABLE

        (commons.css base, icons, forms; /design-system/#forms)

        - :focus-visible outline 2px solid var(--blue), offset 2px.
          never remove it.
        - never meaning by color alone: a word and a mark beside
          every state.
        - every inline icon is aria-hidden="true" beside its word.
        - every label bound with for; every hint under its field;
          the status line aria-live="polite" and present from first
          paint.
        - reduced motion honored: the page carries
          @media (prefers-reduced-motion: reduce){ * { transition:none !important; animation:none !important; } }
        - contrast: type on a ground is a token pair that commons.css
          already puts together; the -t sunset variants pass AA on
          --bg, --inset, and --surface in their mode. do not invent
          a new pair.
        - html carries lang="en" and color-scheme:light dark.


10. DO / DO NOT

        DO                                       DO NOT
        copy the token blocks verbatim           retype a value from memory
        read var(--name) everywhere              write #hex, rgba(), or "white"
        pick one of the four grammars            invent a fifth container width
        load topbar.js or shell.js               write an inline topbar
        put the mode boot inline before CSS      leave a mode flash
        use the classes commons.css names        rename a pattern for one page
        give sections ids and .addr              make a heading with no address
        walk the sweep in order, one stop each   let a section borrow a neighbor's stop
        use --sun-*-t for type                   color type with a canonical stop
        pair every state with a word and mark    carry a state by color alone
        keep the formation notice byte-identical paraphrase the notice
        write a distinct description             copy another page's description
        derive a tint with color-mix from tokens define a new hex for a tint
        end with the footer and the notice       end on a bare </div>
        check both modes                         ship a page seen only in dark
        file a stop card for anything open       adopt a palette, a scale, a face


11. VERIFY BEFORE THE PR

        run from the repository root, on the branch. name the
        commit the checks ran against in the PR. a green check is
        silence about everything it does not check (AGENTS.md CHECK).

        git add PATH/index.html                    new pages first, then
        python3 scripts/validate.py                ledger, index.json, STATUS.md, one-frame rule
        python3 scripts/token_audit.py             hex outside a token; drift against commons.css
        python3 scripts/measure_audit.py           the framed measure and the frame grid
        python3 scripts/shell_frame.py --check     the generated frame block is current
        python3 scripts/em_dash_audit.py           no em dashes
        python3 scripts/almanac_audit.py           the cards answer to the ledger
        python3 scripts/notice_audit.py            the formation notice on every page, byte-identical
        python3 scripts/design_audit.py            this file, as a check: head block, faces,
                                                   containers, literals, footer, frame
        grep -rnP "[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}]" --include='*.html' --include='*.md' .   emoji

        then, by eye, in both modes:
        - the masthead, one section, the footer, on a phone width and a desk.
        - focus rings on every control by keyboard.
        - the page next to a neighbor in the same grammar: same
          measure, same kicker, same rule weight.

        the PR body names: the address, the grammar, every check
        and its result, and any finding you left as judgment.
        merge is adoption; a draft stays a draft until a person
        adopts it.


12. WHERE THIS FILE STOPS

        a page that follows every line above will look like the
        estate. it will not be good on its own; the register in
        /design-system/#desert is what makes a page good, and that
        is read, not copied. when the reference page and this file
        disagree, the reference and commons.css govern; fix this
        file in the same PR and say so.

        scripts/design_audit.py reads every tracked page against
        this file and writes design-system/AUDIT.md. regenerate the
        report when you change a rule here.
