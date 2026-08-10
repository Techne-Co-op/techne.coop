/* ============================================================
   shell.js · the CIS shell · emission of U-01, extended by U-04
   One persistent frame over every signed-in surface: topbar,
   the complete grouped map, the member chip, the mode toggle,
   and a section context strip, injected from the manifest
   below. Fulfils and supersedes the nav.js behaviour specified
   at techne.coop/design-system (CIS Primary Navigation).

   U-04: the shell owns the auth gate. Signed out, the frame
   shows only the topbar and the standard gate card; the map is
   for members. The gate sends the magic link itself through
   the GoTrue REST endpoint, so pages carry no gate of their
   own. A magic-link landing (tokens in the address) renders as
   signing-in, never as signed-out.

   Dependency free. No build step. The page remains a readable
   document without it. Pages keep their own data loading; the
   shell reads the session, it never creates a second client.
   CSS stays inline per page per the SUB-02 consumption card; the
   frame's own appearance is assets/shell.css, which must load with
   the document rather than after it (U-18).

   U-18: the shell also declares where the map can take a member, so
   the browser can fetch the next surface before the click instead of
   after it. See speculate() below.

   Usage, in <head> after the error boundary:
     <link rel="stylesheet" href="/assets/shell.css">
     <script src="/assets/shell.js" defer></script>

   The Common Record Series · RegenHub, LCA · August 2026
   ============================================================ */
(function () {
  'use strict';

  /* U-15: a page may declare itself public with data-public on the
     script tag. Signed out, such a page is left exactly as authored,
     no gate, no frame; signed in, it gains the members' frame so the
     map never disappears under a reader's feet. */
  var PUBLIC = !!(document.currentScript && document.currentScript.hasAttribute('data-public'));

  var SUPABASE_URL = 'https://ujujwgopdwirebgcpekc.supabase.co';
  var ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVqdWp3Z29wZHdpcmViZ2NwZWtjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM3ODc3ODIsImV4cCI6MjA5OTM2Mzc4Mn0.v6atltp9vbEj0RN2stSuDrzOdWVHB9GGR6rwPCwBNEk';
  var TOKEN_KEY = 'sb-ujujwgopdwirebgcpekc-auth-token';
  var ROLE_CACHE_KEY = 'cis-shell-identity';
  var ROLE_CACHE_MS = 5 * 60 * 1000;

  /* ---------- the manifest ----------
     Each section declares its slice and its tint, a stop on the
     sunset sweep. The taxonomy is the deployed grouping, adopted
     over the five-slice draft per the U-03 card. Grammar and the
     table reads were carried here and shown in the strip until
     U-05: true of the build, and nothing a member came to read.
     The section keeps its name and its colour. */
  var MAP = [
    { group: null, items: [
      { href: '/intranet/', label: 'Overview', icon: '<circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/>', tint: 'gold' }
    ]},
    { group: 'Belong', items: [
      { href: '/commons/agreements/', label: 'Agreements', icon: '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/>', tint: 'amber' },
      { href: '/commons/directory/', label: 'Directory', icon: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>', tint: 'amber' }
    ]},
    { group: 'Gather', items: [
      { href: '/commons/gatherings/', label: 'Gatherings', icon: '<path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/>', tint: 'coral' }
    ]},
    { group: 'Find one another', items: [
      { href: '/commons/opportunities/', label: 'Opportunities', icon: '<path d="m3 11 18-5v12L3 14v-3z"/><path d="M11.6 16.8a3 3 0 1 1-5.8-1.6"/>', tint: 'rose' },
      { href: '/intranet/programs/', label: 'Programs', icon: '<rect x="16" y="16" width="6" height="6" rx="1"/><rect x="2" y="16" width="6" height="6" rx="1"/><rect x="9" y="2" width="6" height="6" rx="1"/><path d="M5 16v-3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3"/><path d="M12 12V8"/>', tint: 'rose' }
    ]},
    { group: 'See your share', items: [
      { href: '/intranet/share/', label: 'Your share', icon: '<path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/>', tint: 'violet' }
    ]},
    { group: 'Treasury', items: [
      { href: '/intranet/treasury/', label: 'The Desk', icon: '<line x1="3" x2="21" y1="22" y2="22"/><line x1="6" x2="6" y1="18" y2="11"/><line x1="10" x2="10" y1="18" y2="11"/><line x1="14" x2="14" y1="18" y2="11"/><line x1="18" x2="18" y1="18" y2="11"/><polygon points="12 2 20 7 4 7"/>', tint: 'violet' }
    ]},
    { group: 'Common agency', items: [
      { href: '/intranet/direct/', label: 'Direction', icon: '<path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/>', tint: 'blue' }
    ]},
    { group: 'The record', items: [
      { href: '/commons/', label: 'The Commonplace Book', icon: '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>', tint: 'blue' },
      { href: '/commons/build/', label: 'The Almanac', icon: '<path d="M14.106 5.553a2 2 0 0 0 1.788 0l3.659-1.83A1 1 0 0 1 21 4.619v12.764a1 1 0 0 1-.553.894l-4.553 2.277a2 2 0 0 1-1.788 0l-4.212-2.106a2 2 0 0 0-1.788 0l-3.659 1.83A1 1 0 0 1 3 19.381V6.618a1 1 0 0 1 .553-.894l4.553-2.277a2 2 0 0 1 1.788 0z"/><path d="M15 5.764v15"/><path d="M9 3.236v15"/>', tint: 'blue' }
    ]}
  ];

  /* ---------- frame styles ----------
     Moved to assets/shell.css by U-18. A stylesheet injected by a
     deferred script arrives after the first paint, and the
     @view-transition opt-in it carried was therefore never present
     at the moment the browser reads it, which is pagereveal, before
     any deferred script has run. Every cross-document transition on
     this estate was skipped, and every skip rejected with AbortError
     "Transition was skipped". The appearance now loads with the
     document and this file keeps only the behaviour.

     Pages carry, in <head> and before this script:
       <link rel="stylesheet" href="/assets/shell.css">
     ---------- */

  /* ---------- the transition's own promises ----------
     A cross-document view transition carries ready, finished, and
     updateCallbackDone promises. When a transition is superseded,
     the reader clicks the next section before the last one settled,
     the browser skips it and those promises reject with AbortError
     "Transition was skipped". That is the API working as specified,
     not an application fault; left untouched it surfaces as an
     unhandled rejection and the error boundary alarms the member
     over an animation. Claim them here, at the source, and a skip
     stays what it is: nothing. */
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

  /* ---------- speculation (U-18) ----------
     The members' surfaces are separate documents, and a navigation
     between them is a document load: the frame is raised again, the
     fonts are resolved again, the page's own reads are issued again.
     That is what made the intranet feel like it reloaded, because it
     did. Rather than dissolve the estate into a client-side router,
     which would cost the property that every page remains a readable
     document, the shell tells the browser where the member is likely
     to go and lets it do the work before the click.

     Eagerness is moderate: the browser acts on hover or pointerdown,
     not on sight, so a member who reads the Overview without touching
     the map costs the record nothing. The candidates come from the
     manifest, which is already the one true list of where the map can
     take you, minus the page we are on.

     Read-only by construction. Every write on these surfaces sits
     behind a click handler; the reads a prerender issues are the same
     reads the click would have issued a moment later, under the same
     row security. Browsers without the API ignore the element. */
  function speculate() {
    try {
      if (!(window.HTMLScriptElement && HTMLScriptElement.supports &&
            HTMLScriptElement.supports('speculationrules'))) return;
      var here = normalize(location.pathname);
      var urls = [];
      MAP.forEach(function (grp) {
        grp.items.forEach(function (it) {
          if (it.outside) return;
          if (normalize(it.href) === here) return;
          if (urls.indexOf(it.href) < 0) urls.push(it.href);
        });
      });
      if (!urls.length) return;
      var s = document.createElement('script');
      s.type = 'speculationrules';
      s.textContent = JSON.stringify({
        prerender: [{ source: 'list', urls: urls, eagerness: 'moderate' }]
      });
      document.head.appendChild(s);
    } catch (e) {
      if (window.Techne && Techne.record) Techne.record('handled', 'shell speculation: ' + (e && e.message ? e.message : e));
    }
  }

  /* ---------- session, read not owned ---------- */
  function session() {
    try {
      var raw = localStorage.getItem(TOKEN_KEY);
      if (!raw) return null;
      var t = JSON.parse(raw);
      if (!t || !t.access_token || !t.user) return null;
      if (t.expires_at && t.expires_at * 1000 < Date.now() - 60000) return null;
      return t;
    } catch (e) { return null; }
  }

  /* a magic-link landing carries its tokens in the address; the page's
     own client stores the session a beat after we run. Signing in, not
     signed out. */
  function authCallbackPending() {
    var h = location.hash + location.search;
    return /access_token=|refresh_token=|type=magiclink|type=signup|type=recovery|[?&#]code=/.test(h);
  }

  function fetchIdentity(sess, done) {
    try {
      var cached = JSON.parse(sessionStorage.getItem(ROLE_CACHE_KEY) || 'null');
      if (cached && cached.uid === sess.user.id && Date.now() - cached.t < ROLE_CACHE_MS) {
        done(cached); return;
      }
    } catch (e) {}
    var headers = { apikey: ANON_KEY, Authorization: 'Bearer ' + sess.access_token };
    fetch(SUPABASE_URL + '/rest/v1/agents?auth_user_id=eq.' + sess.user.id + '&select=id,display_name', { headers: headers })
      .then(function (r) { return r.json(); })
      .then(function (agents) {
        var self = Array.isArray(agents) && agents.length ? agents[0] : null;
        if (!self) { done({ uid: sess.user.id, roles: [], t: Date.now() }); return; }
        return fetch(SUPABASE_URL + '/rest/v1/role_grants?agent_id=eq.' + self.id + '&revoked_at=is.null&select=role', { headers: headers })
          .then(function (r) { return r.json(); })
          .then(function (grants) {
            var id = {
              uid: sess.user.id, agentId: self.id, displayName: self.display_name,
              roles: Array.isArray(grants) ? grants.map(function (g) { return g.role; }) : [],
              t: Date.now()
            };
            try { sessionStorage.setItem(ROLE_CACHE_KEY, JSON.stringify(id)); } catch (e) {}
            done(id);
          });
      })
      .catch(function (e) {
        if (window.Techne && Techne.record) Techne.record('handled', 'shell identity: ' + (e && e.message ? e.message : e));
        done(null);
      });
  }

  /* ---------- build ---------- */
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text) n.textContent = text;
    return n;
  }

  function normalize(p) {
    if (!p) return '/';
    if (p.charAt(p.length - 1) !== '/') p += '/';
    return p;
  }

  function activeItem() {
    var here = normalize(location.pathname);
    for (var i = 0; i < MAP.length; i++) {
      for (var j = 0; j < MAP[i].items.length; j++) {
        var it = MAP[i].items[j];
        if (!it.noactive && !it.outside && normalize(it.href) === here) return it;
      }
    }
    return null;
  }

  function sliceOf(item) {
    var slice = null;
    MAP.forEach(function (grp) { if (grp.items.indexOf(item) >= 0) slice = grp.group; });
    return slice;
  }

  function toggleMode() {
    var html = document.documentElement;
    var next = html.dataset.mode === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-mode', next);
    try { localStorage.setItem('techne-mode', next); } catch (e) {}
  }

  /* ---------- notices (X-12) ----------
     The member's rail: events addressed to this member by someone
     else's act, read through events_read exactly as 0002 scopes it.
     The rail is the log itself; this panel only renders it. Unseen
     is a device-local cutoff, honestly per-device, never state the
     record has to carry. */
  var NOTICE_KINDS = ['opportunity.responded', 'registration.registered',
                      'registration.cancelled', 'membership.admitted'];
  var SEEN_KEY = 'cis-notices-seen';

  function noticeText(ev) {
    var p = ev.payload || {};
    if (ev.kind === 'opportunity.responded')
      return (p.responder || 'A member') + ' responded to “' + (p.title || 'your opportunity') + '”';
    if (ev.kind === 'registration.registered')
      return (p.registrant || 'A member') + ' registered for “' + (p.title || 'your gathering') + '”';
    if (ev.kind === 'registration.cancelled')
      return (p.registrant || 'A member') + ' cancelled their registration for “' + (p.title || 'your gathering') + '”';
    if (ev.kind === 'membership.admitted')
      return 'You were admitted to membership';
    return ev.kind;
  }

  function noticeHref(ev) {
    if (ev.kind === 'opportunity.responded') return '/commons/opportunities/';
    if (ev.kind === 'membership.admitted') return '/commons/agreements/';
    return '/commons/gatherings/';
  }

  function noticeWhen(iso) {
    var then = new Date(iso).getTime();
    var mins = Math.floor((Date.now() - then) / 60000);
    if (mins < 1) return 'just now';
    if (mins < 60) return mins + 'm ago';
    var hours = Math.floor(mins / 60);
    if (hours < 48) return hours + 'h ago';
    return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  }

  function initNotices(bell, agentId, token) {
    var url = SUPABASE_URL + '/rest/v1/events'
      + '?agent_id=eq.' + agentId
      + '&actor_agent_id=neq.' + agentId
      + '&kind=in.(' + NOTICE_KINDS.map(function (k) { return '"' + k + '"'; }).join(',') + ')'
      + '&select=id,occurred_at,kind,payload&order=occurred_at.desc&limit=12';
    fetch(url, { headers: { apikey: ANON_KEY, Authorization: 'Bearer ' + token } })
      .then(function (r) { return r.json(); })
      .then(function (rows) {
        if (!Array.isArray(rows)) return;
        var seen = 0;
        try { seen = parseInt(localStorage.getItem(SEEN_KEY) || '0', 10) || 0; } catch (e) {}
        var fresh = rows.filter(function (ev) {
          return new Date(ev.occurred_at).getTime() > seen;
        }).length;

        bell.textContent = fresh > 0 ? 'Notices · ' + fresh : 'Notices';
        bell.classList.toggle('cis-has', fresh > 0);
        bell.style.display = 'inline-block';

        var panel = el('div', 'cis-notices');
        panel.id = 'cis-notices';
        panel.setAttribute('aria-label', 'notices');
        panel.appendChild(el('div', 'cis-notices-head', 'Notices · what concerns you'));
        if (!rows.length) {
          panel.appendChild(el('div', 'cis-notices-empty',
            'Nothing yet. Responses to your opportunities and registrations for your gatherings land here.'));
        }
        rows.forEach(function (ev) {
          var a = el('a', 'cis-notice' +
            (new Date(ev.occurred_at).getTime() > seen ? ' cis-new' : ''));
          a.href = noticeHref(ev);
          a.appendChild(el('div', 'cis-notice-line', noticeText(ev)));
          a.appendChild(el('div', 'cis-notice-when', noticeWhen(ev.occurred_at)));
          panel.appendChild(a);
        });
        document.body.appendChild(panel);

        var setOpen = function (open) {
          panel.classList.toggle('cis-open', open);
          bell.setAttribute('aria-expanded', open ? 'true' : 'false');
          if (open) {
            try { localStorage.setItem(SEEN_KEY, String(Date.now())); } catch (e) {}
            bell.textContent = 'Notices';
            bell.classList.remove('cis-has');
          }
        };
        bell.addEventListener('click', function (e) {
          e.stopPropagation();
          setOpen(!panel.classList.contains('cis-open'));
        });
        document.addEventListener('click', function (e) {
          if (panel.classList.contains('cis-open') && !panel.contains(e.target)) setOpen(false);
        });
        document.addEventListener('keydown', function (e) {
          if (e.key === 'Escape' && panel.classList.contains('cis-open')) {
            setOpen(false); bell.focus();
          }
        });
      })
      .catch(function (e) {
        if (window.Techne && Techne.record) Techne.record('handled', 'shell notices: ' + (e && e.message ? e.message : e));
      });
  }

  /* ---------- the gate (U-04) ----------
     The one standard: the card. Label, heading, body, the
     destination line read from the manifest, the email field,
     the primary action, the status line, and the sent state. */
  function buildGate(active) {
    var gate = el('div', 'cis-gate');
    var card = el('div', 'cis-gate-card');
    if (active) card.style.setProperty('--cis-tint', 'var(--cis-' + active.tint + ')');

    card.appendChild(el('span', 'cis-gate-label', 'Techne · RegenHub, LCA'));
    card.appendChild(el('h1', 'cis-gate-h', 'Member intranet'));
    card.appendChild(el('p', 'cis-gate-body', 'For cooperative members. Enter your email address and we will send a sign-in link. No password to manage.'));
    if (active) {
      var dest = el('div', 'cis-gate-dest');
      dest.appendChild(el('span', 'cis-mark'));
      var slice = sliceOf(active);
      dest.appendChild(el('span', null, 'continues to ' + (slice ? slice + ' · ' : '') + active.label));
      card.appendChild(dest);
    }

    var form = el('div');
    var lab = el('label', null, 'EMAIL ADDRESS');
    lab.setAttribute('for', 'cis-gate-email');
    var input = el('input');
    input.type = 'email'; input.id = 'cis-gate-email';
    input.placeholder = 'you@example.com';
    input.setAttribute('autocomplete', 'email');
    var btn = el('button', 'cis-gate-btn', 'Send sign-in link');
    btn.type = 'button';
    var status = el('div', 'cis-gate-status');
    form.appendChild(lab); form.appendChild(input); form.appendChild(btn); form.appendChild(status);

    var sent = el('div');
    sent.style.display = 'none';
    var sentLine = el('p', 'cis-gate-status ok', 'Link sent.');
    sentLine.style.marginTop = '0';
    sent.appendChild(sentLine);
    sent.appendChild(el('p', 'cis-gate-body', 'Check your email and open the link to continue. You can close this tab.'));
    var again = el('button', 'cis-gate-again', 'Send another link');
    again.type = 'button';
    sent.appendChild(again);

    function send() {
      var email = input.value.trim();
      if (!email) { status.textContent = 'Enter an email address.'; status.className = 'cis-gate-status err'; return; }
      btn.disabled = true;
      status.textContent = 'Sending…'; status.className = 'cis-gate-status';
      var redirect = location.origin + location.pathname;
      fetch(SUPABASE_URL + '/auth/v1/otp?redirect_to=' + encodeURIComponent(redirect), {
        method: 'POST',
        headers: { apikey: ANON_KEY, 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email, create_user: true, gotrue_meta_security: {} })
      }).then(function (r) {
        if (r.ok) { form.style.display = 'none'; sent.style.display = ''; }
        else {
          return r.json().catch(function () { return {}; }).then(function (body) {
            if (window.Techne && Techne.record) Techne.record('handled', 'gate otp: ' + (body.msg || body.error_description || r.status));
            status.textContent = 'Could not send the sign-in link. Check the address and try again.';
            status.className = 'cis-gate-status err';
            btn.disabled = false;
          });
        }
      }).catch(function () {
        status.textContent = 'Could not reach the record. Try again in a moment.';
        status.className = 'cis-gate-status err';
        btn.disabled = false;
      });
    }
    btn.addEventListener('click', send);
    input.addEventListener('keydown', function (e) { if (e.key === 'Enter') send(); });
    again.addEventListener('click', function () { form.style.display = ''; sent.style.display = 'none'; btn.disabled = false; status.textContent = ''; });

    card.appendChild(form);
    card.appendChild(sent);
    gate.appendChild(card);
    return gate;
  }

  function build() {
    if (document.querySelector('.cis-topbar')) return;
    var sess = session();
    var pending = !sess && authCallbackPending();
    var signedIn = !!sess || pending;
    if (!signedIn && PUBLIC) return;

    /* U-15: a public page has already raised its own topbar (U-13).
       When the members' frame takes the page over, that bar is
       superseded, not stacked above the content it framed. */
    if (PUBLIC) {
      var pub = document.querySelector('.tc-topbar');
      if (pub && pub.parentNode) pub.parentNode.removeChild(pub);
    }

    var active = activeItem();

    /* topbar */
    var topbar = el('header', 'cis-topbar');
    var brand = el('a', 'cis-brand', 'Techne');
    brand.appendChild(el('span', 'cis-brand-suffix', ' · intranet'));
    brand.href = '/intranet/';
    var right = el('div', 'cis-topbar-right');
    var menuBtn = null;
    if (signedIn) {
      menuBtn = el('button', 'cis-menu', 'Menu');
      menuBtn.type = 'button';
      menuBtn.id = 'cis-menu-btn';
      menuBtn.setAttribute('aria-expanded', 'false');
      menuBtn.setAttribute('aria-controls', 'cis-map');
      menuBtn.setAttribute('aria-label', 'show the intranet map');
      right.appendChild(menuBtn);
    }
    var bell = null;
    if (signedIn) {
      bell = el('button', 'cis-bell', 'Notices');
      bell.type = 'button';
      bell.setAttribute('aria-expanded', 'false');
      bell.setAttribute('aria-controls', 'cis-notices');
      bell.setAttribute('aria-label', 'notices addressed to you');
      right.appendChild(bell);
    }
    var chip = el('span', 'cis-chip');
    chip.id = 'cis-member-chip';
    chip.textContent = sess && sess.user.email ? sess.user.email
      : (pending ? 'signing in…' : 'not signed in');
    var mode = el('button', 'cis-mode', '◐');
    mode.type = 'button';
    mode.setAttribute('aria-label', 'toggle light and dark mode');
    mode.addEventListener('click', toggleMode);
    right.appendChild(chip); right.appendChild(mode);
    topbar.appendChild(brand); topbar.appendChild(right);

    var main = el('div', 'cis-main');
    var frame = el('div', 'cis-body');
    var body = document.body;
    var foot = null;

    if (signedIn) {
      /* the members' frame: map, context strip, the page */
      var side = el('nav', 'cis-side');
      side.id = 'cis-map';
      side.setAttribute('aria-label', 'intranet');
      var here = normalize(location.pathname);
      MAP.forEach(function (grp) {
        var wrap = grp.steward ? el('div') : side;
        if (grp.steward) { wrap.id = 'cis-steward-nav'; wrap.style.display = 'none'; }
        if (grp.group) wrap.appendChild(el('div', 'cis-group', grp.group));
        grp.items.forEach(function (it) {
          var a = el('a');
          a.href = it.href;
          if (it.icon) {
            var ic = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            ic.setAttribute('class', 'lucide');
            ic.setAttribute('viewBox', '0 0 24 24');
            ic.setAttribute('fill', 'none');
            ic.setAttribute('stroke', 'currentColor');
            ic.setAttribute('stroke-width', '1.5');
            ic.setAttribute('stroke-linecap', 'round');
            ic.setAttribute('stroke-linejoin', 'round');
            ic.setAttribute('aria-hidden', 'true');
            ic.innerHTML = it.icon;
            a.appendChild(ic);
          }
          a.appendChild(document.createTextNode(it.label));
          if (it.outside) a.className = 'cis-out';
          if (!it.noactive && !it.outside && normalize(it.href) === here) {
            a.className = 'active';
            a.setAttribute('aria-current', 'page');
          }
          wrap.appendChild(a);
        });
        if (grp.steward) side.appendChild(wrap);
      });
      var home = el('a', 'cis-out cis-home', '← techne.coop');
      home.href = '/';
      side.appendChild(home);
      /* on a phone the topbar has no room for the member chip; the
         map drawer carries the identity line instead */
      side.appendChild(el('div', 'cis-side-you',
        sess && sess.user.email ? sess.user.email : 'signed in'));

      var context = null;
      if (active) {
        context = el('div', 'cis-context');
        context.style.setProperty('--cis-tint', 'var(--cis-' + active.tint + ')');
        context.appendChild(el('span', 'cis-mark'));
        var slice = sliceOf(active);
        context.appendChild(el('span', 'cis-addr', (slice ? slice + ' · ' : '') + active.label));
      }

      while (body.firstChild) main.appendChild(body.firstChild);
      if (context) main.insertBefore(context, main.firstChild);
      /* the footer belongs to the whole frame, not the column beside
         the map (U-15) */
      foot = main.querySelector('footer');
      frame.appendChild(side);
      frame.appendChild(main);

      /* the drawer. Wide screens ignore all of this: the map is simply
         there, and the button is display:none. */
      if (menuBtn) {
        var setOpen = function (open) {
          side.classList.toggle('cis-open', open);
          menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
          menuBtn.textContent = open ? 'Close' : 'Menu';
        };
        menuBtn.addEventListener('click', function () {
          setOpen(!side.classList.contains('cis-open'));
        });
        /* following a link should not leave the drawer standing open
           over the page it just went to */
        side.addEventListener('click', function (e) {
          if (e.target && e.target.tagName === 'A') setOpen(false);
        });
        document.addEventListener('keydown', function (e) {
          if (e.key === 'Escape' && side.classList.contains('cis-open')) {
            setOpen(false); menuBtn.focus();
          }
        });
      }
    } else {
      /* signed out: the topbar and the gate; the map is for members */
      var parked = el('div', 'cis-parked');
      while (body.firstChild) parked.appendChild(body.firstChild);
      main.appendChild(buildGate(active));
      main.appendChild(parked);
      frame.appendChild(main);
    }

    body.appendChild(topbar);
    body.appendChild(frame);
    if (foot) body.appendChild(foot);

    /* identity: chip detail and the steward group */
    function resolveIdentity(s) {
      window.cisUser = { userId: s.user.id, email: s.user.email || null };
      chip.textContent = s.user.email || 'signed in';
      fetchIdentity(s, function (id) {
        if (!id) return;
        window.cisUser = {
          userId: id.uid, email: s.user.email || null,
          agentId: id.agentId || null, displayName: id.displayName || null,
          roles: id.roles || []
        };
        if (id.displayName) {
          chip.textContent = '';
          var b = document.createElement('b');
          b.textContent = id.displayName;
          chip.appendChild(b);
          chip.appendChild(document.createTextNode(' · ' + (s.user.email || '')));
        }
        if ((id.roles || []).indexOf('steward') >= 0 || (id.roles || []).indexOf('director') >= 0) {
          var sw = document.getElementById('cis-steward-nav');
          if (sw) sw.style.display = '';
        }
        if (bell && id.agentId) initNotices(bell, id.agentId, s.access_token);
        document.dispatchEvent(new CustomEvent('cis:user', { detail: window.cisUser }));
      });
    }

    if (sess) {
      resolveIdentity(sess);
    } else if (pending) {
      /* the page's client is exchanging the link; watch for the session */
      var tries = 0;
      var wait = setInterval(function () {
        var s = session();
        tries += 1;
        if (s) { clearInterval(wait); resolveIdentity(s); }
        else if (tries > 25) {
          clearInterval(wait);
          chip.textContent = 'not signed in';
          document.dispatchEvent(new CustomEvent('cis:user', { detail: null }));
        }
      }, 400);
    } else {
      window.cisUser = null;
      document.dispatchEvent(new CustomEvent('cis:user', { detail: null }));
    }

    /* Only a member gets speculation: there is nothing behind the gate
       to fetch ahead for a reader who is not signed in. A document that
       is itself being prerendered waits until it is activated, so the
       browser is never asked to nest one speculation inside another. */
    if (signedIn) {
      if (document.prerendering) {
        document.addEventListener('prerenderingchange', speculate, { once: true });
      } else {
        speculate();
      }
    }
  }

  /* the auth state can change under us in another tab */
  window.addEventListener('storage', function (e) {
    if (e.key === TOKEN_KEY) {
      var chip = document.getElementById('cis-member-chip');
      var s = session();
      if (chip) chip.textContent = s && s.user.email ? s.user.email : 'not signed in';
    }
  });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', build);
  } else {
    build();
  }
})();
