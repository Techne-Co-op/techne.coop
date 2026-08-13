/* ============================================================
   shell-gate.js · the pre-paint gate · emission of U-19

   The map is for members, so the decision to show it has to be
   made before the first paint, not after. This file is loaded
   synchronously in the head, ahead of the body, and does exactly
   one thing: it reads the session the document can read without
   a network call and marks the document element.

     data-cis="in"   a member, or a magic-link landing mid-exchange
     data-cis="out"  everyone else, including any failure

   shell.css hides the frame unless the mark reads in, so a reader
   who is not signed in never paints a members' map, and neither
   does a reader with scripting off. Failure is closed by
   construction: the attribute is written out first and only
   raised to in on a positive read.

   Not deferred, and not merged into shell.js, because a deferred
   script runs after pagereveal and after the first paint, which
   is the whole defect U-18 and U-19 exist to correct.

   The Common Record Series · RegenHub, LCA · August 2026
   ============================================================ */
(function () {
  'use strict';
  var TOKEN_KEY = 'sb-ujujwgopdwirebgcpekc-auth-token';
  var html = document.documentElement;
  html.setAttribute('data-cis', 'out');
  try {
    var h = location.hash + location.search;
    if (/access_token=|refresh_token=|type=magiclink|type=signup|type=recovery|[?&#]code=/.test(h)) {
      html.setAttribute('data-cis', 'in');
      return;
    }
    var raw = localStorage.getItem(TOKEN_KEY);
    if (!raw) return;
    var t = JSON.parse(raw);
    if (!t || !t.access_token || !t.user) return;
    if (t.expires_at && t.expires_at * 1000 < Date.now() - 60000) return;
    html.setAttribute('data-cis', 'in');
  } catch (e) {
    html.setAttribute('data-cis', 'out');
  }
})();
