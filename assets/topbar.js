/* ============================================================
   topbar.js · the public topbar · emission of U-13
   One primary navigation for every public surface: the same
   frame on every page, injected from the manifest below, so
   contents and size cannot drift page to page. The geometry
   matches the CIS shell topbar (48px, hairline, surface), so
   crossing between the public face and the signed-in surface
   the bar reads as one element. Specified at
   techne.coop/design-system (Site Navigation · The Topbar).

   Dependency free. No build step. The page remains a readable
   document without it. Tokens are self-contained (--tc-*),
   resolved from data-mode with the design-system values, so
   the bar renders identically over any page token vocabulary.

   Usage, in <head>:
     <script src="/assets/topbar.js" defer></script>

   Signed-in surfaces load /assets/shell.js instead, never both.

   The Common Record Series · RegenHub, LCA · August 2026
   ============================================================ */
(function () {
  'use strict';

  /* ---------- the launch switch ----------
     From 2026-08-10 to the public launch on 14 August 2026 the
     bar was withheld: the script still loaded on every page (the
     one-frame rule, U-13, is satisfied by the script, not by the
     element) and still resolved the mode before first paint, but
     it built nothing. The estate was under construction, and a
     map is a claim about what is finished.

     Restored on launch day, 2026-08-14, per the steward's call
     of 2026-08-10 that set the date. The switch is kept rather
     than deleted: it is the one hand that takes the public map
     off every page at once, should that ever be wanted again. */
  var OFFER_MAP = true;

  /* ---------- the manifest ----------
     The public map, complete. A page never edits this list;
     the bar is the same bar everywhere it appears.

     Legal came off the bar on 2026-08-14 at the steward's call.
     The instruments are not a destination a reader arrives
     wanting; they are what a reader checks, and the bar is for
     the three ways into the cooperative. Legal keeps two routes
     from the bottom of every page: the footer's Legal
     instruments link where a page carries the four-column
     footer, and the formation notice, which every page carries
     and which points at /legal/#formation. Removing a link from
     the map does not remove it from the estate: fifty-five
     pages link into /legal/ in their prose. */
  var LINKS = [
    { href: '/participation/', label: 'Participation' },
    { href: '/commons/', label: 'The commons' },
    { href: '/intranet/', label: 'Intranet' }
  ];

  /* mode, resolved before first paint where the page's own boot
     has not already done it */
  var html = document.documentElement;
  if (!html.getAttribute('data-mode')) {
    var stored = null;
    try { stored = localStorage.getItem('techne-mode'); } catch (e) {}
    var m = stored || (window.matchMedia && matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
    html.setAttribute('data-mode', m);
  }

  /* ---------- frame styles ----------
     Self-contained: --tc-* only, values from the design-system
     token tables, dark and light. Geometry mirrors .cis-topbar. */
  var CSS = [
    'html[data-mode="dark"]{--tc-surface:#16161B;--tc-line:#2A2A30;--tc-ember:#C4956A;--tc-ember-text:#D4A57A;--tc-muted:#8A857E;--tc-heading:#E8E4DF;}',
    'html[data-mode="light"]{--tc-surface:#FCFBF8;--tc-line:#D8D3C8;--tc-ember:#8A6A4A;--tc-ember-text:#6F5436;--tc-muted:#646058;--tc-heading:#1A1A1F;}',
    '@view-transition{navigation:auto;}',
    '@media (prefers-reduced-motion:reduce){@view-transition{navigation:none;}}',
    '.tc-topbar{view-transition-name:tc-topbar;display:flex;align-items:center;gap:20px;padding:0 20px;height:48px;border-bottom:1px solid var(--tc-line);background:var(--tc-surface);position:sticky;top:0;z-index:40;box-sizing:border-box;font-size:16px;}',
    '.tc-brand{font-family:"IBM Plex Mono","SFMono-Regular",Consolas,monospace;font-size:.78rem;color:var(--tc-ember);letter-spacing:.08em;text-decoration:none;white-space:nowrap;}',
    '.tc-nav{flex:1;min-width:0;}',
    '.tc-nav ul{display:flex;align-items:center;gap:18px;list-style:none;margin:0;padding:0;overflow-x:auto;scrollbar-width:none;}',
    '.tc-nav ul::-webkit-scrollbar{display:none;}',
    '.tc-nav a{font-family:"IBM Plex Mono","SFMono-Regular",Consolas,monospace;font-size:.72rem;letter-spacing:.04em;color:var(--tc-muted);text-decoration:none;white-space:nowrap;padding:4px 0;}',
    '.tc-nav a:hover{color:var(--tc-heading);}',
    '.tc-nav a[aria-current]{color:var(--tc-ember-text);}',
    '.tc-mode{font-family:"IBM Plex Mono","SFMono-Regular",Consolas,monospace;font-size:.7rem;color:var(--tc-muted);background:none;border:1px solid var(--tc-line);padding:3px 10px;cursor:pointer;letter-spacing:.04em;}',
    '.tc-mode:hover{color:var(--tc-ember);border-color:var(--tc-ember);}',
    '@media print{.tc-topbar{display:none;}}'
  ].join('\n');

  var style = document.createElement('style');
  style.textContent = CSS;
  (document.head || document.documentElement).appendChild(style);

  /* a superseded cross-document view transition rejects with
     AbortError by specification; claim the promises so a skip
     stays silent (after the shell's practice) */
  (function tameTransitions() {
    function tame(vt) {
      if (!vt) return;
      var quiet = function () {};
      if (vt.ready && vt.ready.catch) vt.ready.catch(quiet);
      if (vt.finished && vt.finished.catch) vt.finished.catch(quiet);
      if (vt.updateCallbackDone && vt.updateCallbackDone.catch) vt.updateCallbackDone.catch(quiet);
    }
    window.addEventListener('pagereveal', function (e) { tame(e.viewTransition); });
    window.addEventListener('pageswap', function (e) { tame(e.viewTransition); });
  })();

  /* ---------- build ---------- */
  function build() {
    if (!OFFER_MAP) return;
    if (document.querySelector('.tc-topbar')) return;

    var bar = document.createElement('header');
    bar.className = 'tc-topbar';

    var brand = document.createElement('a');
    brand.className = 'tc-brand';
    brand.href = '/';
    brand.textContent = 'Techne';
    bar.appendChild(brand);

    var nav = document.createElement('nav');
    nav.className = 'tc-nav';
    nav.setAttribute('aria-label', 'Site navigation');
    var ul = document.createElement('ul');
    var path = location.pathname;
    LINKS.forEach(function (item) {
      var li = document.createElement('li');
      var a = document.createElement('a');
      a.href = item.href;
      a.textContent = item.label;
      if (item.href !== '/intranet/' && path.indexOf(item.href) === 0) {
        a.setAttribute('aria-current', path === item.href ? 'page' : 'true');
      }
      li.appendChild(a);
      ul.appendChild(li);
    });
    nav.appendChild(ul);
    bar.appendChild(nav);

    var mode = document.createElement('button');
    mode.className = 'tc-mode';
    mode.type = 'button';
    mode.textContent = '◐';
    mode.setAttribute('aria-label', 'Toggle light and dark mode');
    mode.addEventListener('click', function () {
      var next = html.getAttribute('data-mode') === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-mode', next);
      try { localStorage.setItem('techne-mode', next); } catch (e) {}
    });
    bar.appendChild(mode);

    document.body.insertBefore(bar, document.body.firstChild);
  }

  if (document.body) build();
  else document.addEventListener('DOMContentLoaded', build);
})();
