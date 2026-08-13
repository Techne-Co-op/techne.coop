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
     Lives in assets/shell-map.json and is rendered into each
     surface's markup by scripts/shell_frame.py (U-19). This script
     reads the map the document brought rather than keeping a copy,
     because two copies of one manifest is the drift this estate has
     paid for before: the section's slice, tint, and label all come
     from the rendered nav. */

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
      var side = document.getElementById('cis-map');
      var links = side ? side.querySelectorAll('a') : [];
      for (var i = 0; i < links.length; i++) {
        var a = links[i];
        if (a.classList.contains('cis-out')) continue;
        var href = a.getAttribute('href');
        if (normalize(href) === here) continue;
        if (urls.indexOf(href) < 0) urls.push(href);
      }
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
    var side = document.getElementById('cis-map');
    if (!side) return null;
    var here = normalize(location.pathname);
    var links = side.querySelectorAll('a');
    for (var i = 0; i < links.length; i++) {
      var a = links[i];
      if (a.classList.contains('cis-out')) continue;
      if (normalize(a.getAttribute('href')) !== here) continue;
      var slice = null;
      var n = a.previousElementSibling;
      while (n) {
        if (n.classList && n.classList.contains('cis-group')) { slice = n.textContent; break; }
        n = n.previousElementSibling;
      }
      return { el: a, label: a.textContent, tint: a.getAttribute('data-tint') || 'ember', slice: slice };
    }
    return null;
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
      dest.appendChild(el('span', null, 'continues to ' + (active.slice ? active.slice + ' · ' : '') + active.label));
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
    /* U-19: the frame is in the markup, written by scripts/shell_frame.py
       from assets/shell-map.json. This script no longer raises furniture;
       it adopts what the document already carries: marks the active item,
       fills the chip, wires the drawer, the bell, the mode toggle, and
       the gate card. A surface without the static frame is a build error
       the shell cannot repair, so it is reported, not patched over. */
    var topbar = document.querySelector('.cis-topbar');
    var side = document.getElementById('cis-map');
    var main = document.querySelector('.cis-main');
    if (!topbar || !side || !main) {
      if (window.Techne && Techne.record) Techne.record('handled', 'shell: static frame missing (U-19)');
      return;
    }

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
    var here = normalize(location.pathname);
    var chip = document.getElementById('cis-member-chip');
    var menuBtn = document.getElementById('cis-menu-btn');
    var bell = topbar.querySelector('.cis-bell');
    var mode = topbar.querySelector('.cis-mode');
    if (mode) mode.addEventListener('click', toggleMode);

    if (chip) {
      chip.textContent = sess && sess.user.email ? sess.user.email
        : (pending ? 'signing in…' : 'not signed in');
    }

    if (signedIn) {
      /* the active item, on the map the document brought */
      if (active && active.el) {
        active.el.classList.add('active');
        active.el.setAttribute('aria-current', 'page');
      }
      var you = side.querySelector('.cis-side-you');
      if (you) you.textContent = sess && sess.user.email ? sess.user.email : 'signed in';

      if (active) {
        var context = el('div', 'cis-context');
        context.style.setProperty('--cis-tint', 'var(--cis-' + active.tint + ')');
        context.appendChild(el('span', 'cis-mark'));
        context.appendChild(el('span', 'cis-addr', (active.slice ? active.slice + ' · ' : '') + active.label));
        main.insertBefore(context, main.firstChild);
      }

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
      /* signed out on a members' surface: the topbar and the gate; the
         map and the page's content are withheld. The content is parked
         inside the main column rather than removed, the U-04 shape. */
      var parked = el('div', 'cis-parked');
      while (main.firstChild) parked.appendChild(main.firstChild);
      main.appendChild(buildGate(active));
      main.appendChild(parked);
    }

    /* identity: chip detail and the steward group */
    function resolveIdentity(s) {
      window.cisUser = { userId: s.user.id, email: s.user.email || null };
      if (chip) chip.textContent = s.user.email || 'signed in';
      fetchIdentity(s, function (id) {
        if (!id) return;
        window.cisUser = {
          userId: id.uid, email: s.user.email || null,
          agentId: id.agentId || null, displayName: id.displayName || null,
          roles: id.roles || []
        };
        if (id.displayName && chip) {
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
        if (s) {
          clearInterval(wait);
          document.documentElement.setAttribute('data-cis', 'in');
          resolveIdentity(s);
        } else if (tries > 25) {
          clearInterval(wait);
          document.documentElement.setAttribute('data-cis', 'out');
          if (chip) chip.textContent = 'not signed in';
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
