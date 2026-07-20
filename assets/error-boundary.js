/* Techne error boundary and observability -- packet X-01
 *
 * Intent (RDM v1 X-01): errors surface to the steward without leaking to the
 * member. An unhandled error produces a log entry, not a stack trace to the
 * member.
 *
 * No dependencies, no build step. Loaded first in <head> on every interactive
 * surface so the global handlers install before any application code runs.
 *
 * Boundary of this packet: the steward-visible persistence sink (an error_log
 * table with row security in the CIS project) is a schema decision and is
 * filed as an open escalation card, not invented here. Until it lands, every
 * captured error is written as one structured line on the console channel,
 * which the browser observability layer retains. Replace persist() to attach
 * the server sink; no call site changes.
 */
(function () {
  'use strict';
  var NS = (window.Techne = window.Techne || {});
  if (NS._boundaryInstalled) { return; }
  NS._boundaryInstalled = true;

  // --- observability sink -------------------------------------------------
  function persist(entry) {
    try {
      console.error('[techne:error]', JSON.stringify(entry));
    } catch (_) {
      console.error('[techne:error]', entry && entry.message);
    }
    // SINK SEAM (X-01 escalation): when the steward error_log lands, send
    // `entry` to it here. One place, no call site changes.
  }

  function record(kind, message, detail) {
    var entry = {
      kind: kind,
      message: String(message == null ? 'unknown error' : message).slice(0, 500),
      page: location.pathname,
      at: new Date().toISOString()
    };
    if (detail && detail.stack) { entry.stack = String(detail.stack).slice(0, 2000); }
    if (detail && detail.source) { entry.source = detail.source; }
    persist(entry);
    return entry;
  }
  NS.record = record;

  // --- member-facing fallback --------------------------------------------
  // The member never sees a stack trace. One quiet banner, shown once, in the
  // house style: design-system tokens, no emoji, no em dash.
  var shown = false;
  function notifyMember() {
    if (shown) { return; }
    shown = true;
    var el = document.createElement('div');
    el.setAttribute('role', 'alert');
    el.style.cssText = [
      'position:fixed', 'left:16px', 'right:16px', 'bottom:16px',
      'max-width:520px', 'margin:0 auto', 'z-index:2147483647',
      'font:400 13px/1.6 ui-monospace,"IBM Plex Mono",monospace',
      'background:var(--surface,#16161B)', 'color:var(--text,#e8e6e1)',
      'border:1px solid var(--warn,#c98a3a)', 'border-radius:8px',
      'padding:12px 14px'
    ].join(';');
    el.textContent = 'Something did not load correctly. A steward has been notified. You can reload the page.';
    function place() { (document.body || document.documentElement).appendChild(el); }
    if (document.body) { place(); } else { document.addEventListener('DOMContentLoaded', place); }
  }
  NS.notifyMember = notifyMember;

  // --- report: for handled errors at call sites ---------------------------
  // Replaces raw `alert(error.message)` leaks. Logs the real detail for the
  // steward; returns a plain member message the caller renders in house style.
  // Never surfaces the internal message.
  NS.report = function (err, memberMessage) {
    record('handled', (err && err.message) || err, { stack: err && err.stack });
    return memberMessage || 'Something went wrong. Please try again, or contact a steward.';
  };

  // --- global boundary ----------------------------------------------------
  window.addEventListener('error', function (e) {
    record('uncaught', e.message, {
      stack: e.error && e.error.stack,
      source: (e.filename || '') + ':' + (e.lineno || 0)
    });
    notifyMember();
  });
  window.addEventListener('unhandledrejection', function (e) {
    var r = e.reason;
    record('unhandledrejection', (r && r.message) || r, { stack: r && r.stack });
    notifyMember();
  });
})();
