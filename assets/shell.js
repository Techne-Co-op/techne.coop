/* ============================================================
   shell.js · the CIS shell · emission of U-01
   One persistent frame over every signed-in surface: topbar,
   the complete grouped map, the member chip, the mode toggle,
   and a section context strip, injected from the manifest
   below. Fulfils and supersedes the nav.js behaviour specified
   at techne.coop/design-system (CIS Primary Navigation).

   Dependency free. No build step. The page remains a readable
   document without it. Pages keep their own auth gates; the
   shell reads the session, it never creates a second client.
   CSS stays inline per page per the SUB-02 consumption card;
   the shell carries only its own frame styles.

   Usage, in <head> after the error boundary:
     <script src="/assets/shell.js" defer></script>

   The Common Record Series · RegenHub, LCA · July 2026
   ============================================================ */
(function () {
  'use strict';

  var SUPABASE_URL = 'https://ujujwgopdwirebgcpekc.supabase.co';
  var ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVqdWp3Z29wZHdpcmViZ2NwZWtjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM3ODc3ODIsImV4cCI6MjA5OTM2Mzc4Mn0.v6atltp9vbEj0RN2stSuDrzOdWVHB9GGR6rwPCwBNEk';
  var TOKEN_KEY = 'sb-ujujwgopdwirebgcpekc-auth-token';
  var ROLE_CACHE_KEY = 'cis-shell-identity';
  var ROLE_CACHE_MS = 5 * 60 * 1000;

  /* ---------- the manifest ----------
     Each section declares its slice, tint (the sunset sweep),
     grammar (document or instrument, UI v1 the two grammars),
     and the reads it makes against the record. The taxonomy is
     the deployed grouping, adopted over the five-slice draft
     per the U-03 card. */
  var MAP = [
    { group: null, items: [
      { href: '/intranet/', label: 'Overview', tint: 'gold',
        grammar: 'instrument', reads: 'agents, events, agreements' }
    ]},
    { group: 'Belong', items: [
      { href: '/commons/agreements/', label: 'Agreements', tint: 'amber',
        grammar: 'document', reads: 'agreements, signatures' },
      { href: '/commons/directory/', label: 'Directory', tint: 'amber',
        grammar: 'document', reads: 'agents, memberships, profiles' }
    ]},
    { group: 'Gather', items: [
      { href: '/commons/gatherings/', label: 'Gatherings', tint: 'coral',
        grammar: 'document', reads: 'gatherings, registrations, presence' }
    ]},
    { group: 'Find one another', items: [
      { href: '/commons/opportunities/', label: 'Opportunities', tint: 'rose',
        grammar: 'document', reads: 'opportunities, responses' },
      { href: '/intranet/programs/', label: 'Programs', tint: 'rose',
        grammar: 'document', reads: 'programs roster, affiliations' }
    ]},
    { group: 'Treasury', items: [
      { href: '/intranet/treasury/', label: 'The Desk', tint: 'violet',
        grammar: 'instrument', reads: 'treasury events, instruments' }
    ]},
    { group: 'Steward', steward: true, items: [
      { href: '/commons/directory/', label: 'Admissions', tint: 'ember',
        grammar: 'instrument', reads: 'memberships, applications', noactive: true }
    ]},
    { group: 'The record', items: [
      { href: '/commons/', label: 'The Commonplace Book', tint: 'blue', outside: true },
      { href: '/commons/build/', label: 'Living roadmap', tint: 'blue', outside: true }
    ]}
  ];

  /* ---------- frame styles ----------
     Values mirror commons.css (the distillation of the live
     constitution); everything structural leans on the page's
     own inline v4 tokens. cis- custom properties only, so no
     collision with page token blocks. */
  var CSS = [
    'html[data-mode="dark"]{--cis-gold:#EAB668;--cis-amber:#E5A562;--cis-coral:#DE8872;--cis-rose:#CF7C9A;--cis-violet:#9E86C4;--cis-blue:#8FAEE0;--cis-ember:#D4A57A;}',
    'html[data-mode="light"]{--cis-gold:#87621F;--cis-amber:#8C581D;--cis-coral:#9C4636;--cis-rose:#8C3D58;--cis-violet:#4C3870;--cis-blue:#3A5694;--cis-ember:#6F5436;}',
    '@view-transition{navigation:auto;}',
    '@media (prefers-reduced-motion:reduce){@view-transition{navigation:none;}}',
    '.cis-topbar{view-transition-name:cis-topbar;display:flex;align-items:center;justify-content:space-between;gap:12px;padding:0 20px;height:48px;border-bottom:1px solid var(--line);background:var(--surface);position:sticky;top:0;z-index:40;}',
    '.cis-brand{font-family:var(--mono);font-size:.78rem;color:var(--ember);letter-spacing:.08em;text-decoration:none;white-space:nowrap;}',
    '.cis-topbar-right{display:flex;align-items:center;gap:10px;min-width:0;}',
    '.cis-chip{font-family:var(--mono);font-size:.68rem;color:var(--muted);border:1px solid var(--line);padding:3px 10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:46vw;}',
    '.cis-chip b{color:var(--heading);font-weight:500;}',
    '.cis-mode{font-family:var(--mono);font-size:.7rem;color:var(--muted);background:none;border:1px solid var(--line);padding:3px 10px;cursor:pointer;letter-spacing:.04em;}',
    '.cis-mode:hover{color:var(--ember);border-color:var(--ember);}',
    '.cis-body{display:flex;align-items:stretch;min-height:calc(100vh - 49px);}',
    '.cis-side{view-transition-name:cis-side;width:212px;flex-shrink:0;background:var(--surface);border-right:1px solid var(--line);padding:20px 0 32px;position:sticky;top:49px;align-self:flex-start;height:calc(100vh - 49px);overflow-y:auto;}',
    '.cis-side .cis-group{padding:6px 16px 4px;font-family:var(--mono);font-size:.62rem;letter-spacing:.1em;color:var(--faint);text-transform:uppercase;margin-top:14px;}',
    '.cis-side a{display:block;padding:7px 16px;font-family:var(--mono);font-size:.78rem;color:var(--muted);text-decoration:none;letter-spacing:.03em;border-left:2px solid transparent;}',
    '.cis-side a:hover{color:var(--ember);background:var(--surface);}',
    '.cis-side a.active{color:var(--ember);border-left-color:var(--ember);background:linear-gradient(to right, color-mix(in srgb, var(--ember) 10%, transparent), transparent);}',
    '.cis-side a.cis-out{color:var(--faint);}',
    '.cis-side .cis-home{margin-top:20px;}',
    '.cis-main{flex:1;min-width:0;}',
    '.cis-context{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 14px;padding:9px 24px;border-bottom:1px solid var(--line);background:var(--bg);font-family:var(--mono);font-size:.64rem;letter-spacing:.06em;color:var(--muted);}',
    '.cis-context .cis-mark{width:8px;height:8px;flex:none;align-self:center;background:var(--cis-tint,var(--ember));}',
    '.cis-context .cis-addr{color:var(--cis-tint,var(--ember));text-transform:uppercase;letter-spacing:.1em;}',
    '.cis-context .cis-meta{color:var(--faint);}',
    '@media (max-width:760px){',
    '.cis-body{flex-direction:column;}',
    '.cis-side{position:static;width:100%;height:auto;border-right:none;border-bottom:1px solid var(--line);padding:8px 0;display:flex;flex-wrap:wrap;align-items:center;}',
    '.cis-side .cis-group{margin-top:0;padding:4px 10px;}',
    '.cis-side a{padding:6px 10px;font-size:.72rem;border-left:none;}',
    '.cis-side a.active{background:none;}',
    '.cis-side .cis-home{margin-top:0;}',
    '.cis-context{padding:8px 16px;}',
    '}'
  ].join('\n');

  var style = document.createElement('style');
  style.textContent = CSS;
  (document.head || document.documentElement).appendChild(style);

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

  function toggleMode() {
    var html = document.documentElement;
    var next = html.dataset.mode === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-mode', next);
    try { localStorage.setItem('techne-mode', next); } catch (e) {}
  }

  function build() {
    if (document.querySelector('.cis-topbar')) return;
    var sess = session();
    var active = activeItem();

    /* topbar */
    var topbar = el('header', 'cis-topbar');
    var brand = el('a', 'cis-brand', 'Techne · intranet');
    brand.href = '/intranet/';
    var right = el('div', 'cis-topbar-right');
    var chip = el('span', 'cis-chip');
    chip.id = 'cis-member-chip';
    chip.textContent = sess && sess.user.email ? sess.user.email : 'not signed in';
    var mode = el('button', 'cis-mode', '◐');
    mode.type = 'button';
    mode.setAttribute('aria-label', 'toggle light and dark mode');
    mode.addEventListener('click', toggleMode);
    right.appendChild(chip); right.appendChild(mode);
    topbar.appendChild(brand); topbar.appendChild(right);

    /* sidebar */
    var side = el('nav', 'cis-side');
    side.setAttribute('aria-label', 'intranet');
    var here = normalize(location.pathname);
    MAP.forEach(function (grp) {
      var wrap = grp.steward ? el('div') : side;
      if (grp.steward) { wrap.id = 'cis-steward-nav'; wrap.style.display = 'none'; }
      if (grp.group) wrap.appendChild(el('div', 'cis-group', grp.group));
      grp.items.forEach(function (it) {
        var a = el('a', null, it.label);
        a.href = it.href;
        if (it.outside) a.className = 'cis-out';
        if (!it.noactive && !it.outside && normalize(it.href) === here) a.className = 'active';
        wrap.appendChild(a);
      });
      if (grp.steward) side.appendChild(wrap);
    });
    var home = el('a', 'cis-out cis-home', '← techne.coop');
    home.href = '/';
    side.appendChild(home);

    /* context strip */
    var context = null;
    if (active) {
      context = el('div', 'cis-context');
      context.style.setProperty('--cis-tint', 'var(--cis-' + active.tint + ')');
      var slice = null;
      MAP.forEach(function (grp) { if (grp.items.indexOf(active) >= 0) slice = grp.group; });
      context.appendChild(el('span', 'cis-mark'));
      context.appendChild(el('span', 'cis-addr', (slice ? slice + ' · ' : '') + active.label));
      context.appendChild(el('span', 'cis-meta', active.grammar + ' grammar'));
      if (active.reads) context.appendChild(el('span', 'cis-meta', 'reads: ' + active.reads));
    }

    /* re-parent the page into the frame */
    var main = el('div', 'cis-main');
    var body = document.body;
    while (body.firstChild) main.appendChild(body.firstChild);
    if (context) main.insertBefore(context, main.firstChild);
    var frame = el('div', 'cis-body');
    frame.appendChild(side);
    frame.appendChild(main);
    body.appendChild(topbar);
    body.appendChild(frame);

    /* identity: chip detail and the steward group */
    window.cisUser = sess ? { userId: sess.user.id, email: sess.user.email || null } : null;
    if (sess) {
      fetchIdentity(sess, function (id) {
        if (!id) return;
        window.cisUser = {
          userId: id.uid, email: sess.user.email || null,
          agentId: id.agentId || null, displayName: id.displayName || null,
          roles: id.roles || []
        };
        if (id.displayName) {
          chip.textContent = '';
          var b = document.createElement('b');
          b.textContent = id.displayName;
          chip.appendChild(b);
          chip.appendChild(document.createTextNode(' · ' + (sess.user.email || '')));
        }
        if ((id.roles || []).indexOf('steward') >= 0 || (id.roles || []).indexOf('director') >= 0) {
          var sw = document.getElementById('cis-steward-nav');
          if (sw) sw.style.display = '';
        }
        document.dispatchEvent(new CustomEvent('cis:user', { detail: window.cisUser }));
      });
    } else {
      document.dispatchEvent(new CustomEvent('cis:user', { detail: null }));
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
