/* ============================================================
   sky.js · the sky that computes · emission of U-25 (drafted)
   A page that carries the sunset sweep may let the sky set its
   emphasis. This script resolves where the day stands over
   Boulder (40.015 N, 105.27 W) and writes one attribute,
   data-sky, on the document: sunrise, day, sunset, or night.
   The page's own CSS decides what, if anything, that means;
   every rule reads the standing --sun-* tokens and nothing else.

   Progressive enhancement only. With scripting off the attribute
   is never written, no selector matches, and the page keeps its
   static sweep. The instrument fails toward the evening the
   estate already renders.

   Dependency free. No build step. No network request. The solar
   arithmetic is the compact NOAA approximation: fractional year,
   declination, equation of time, and the hour angle at the
   standard zenith of 90.833 degrees. Sunrise and sunset fall out
   as minutes of the UTC day, and the comparison happens in UTC,
   so no timezone conversion can be wrong. If the arithmetic
   fails anyhow, four fixed windows on America/Denver civil time
   stand in, and if even the timezone database is absent, the
   device clock does.

   Usage, in <head>, after the mode boot:
     <script src="/assets/sky.js" defer></script>

   Specified at techne.coop/design-system (v6 addendum, drafted).
   The Common Record Series · RegenHub, LCA · August 2026
   ============================================================ */
(function () {
  'use strict';

  var LAT = 40.015, LNG = -105.27;

  /* sunrise and sunset as minutes of the UTC day, NOAA compact form */
  function solarEvents(now) {
    var start = Date.UTC(now.getUTCFullYear(), 0, 0);
    var doy = Math.floor((now.getTime() - start) / 86400000);
    var g = 2 * Math.PI / 365 * (doy - 1 + (now.getUTCHours() - 12) / 24);
    var decl = 0.006918
      - 0.399912 * Math.cos(g) + 0.070257 * Math.sin(g)
      - 0.006758 * Math.cos(2 * g) + 0.000907 * Math.sin(2 * g)
      - 0.002697 * Math.cos(3 * g) + 0.00148 * Math.sin(3 * g);
    var eqtime = 229.18 * (0.000075
      + 0.001868 * Math.cos(g) - 0.032077 * Math.sin(g)
      - 0.014615 * Math.cos(2 * g) - 0.040849 * Math.sin(2 * g));
    var latr = LAT * Math.PI / 180;
    var zen = 90.833 * Math.PI / 180;
    var cosHa = Math.cos(zen) / (Math.cos(latr) * Math.cos(decl))
      - Math.tan(latr) * Math.tan(decl);
    if (cosHa < -1 || cosHa > 1) return null; /* no rise or set today */
    var haMin = Math.acos(cosHa) * 180 / Math.PI * 4;
    var noon = 720 - 4 * LNG - eqtime;
    return { rise: noon - haMin, set: noon + haMin };
  }

  /* signed distance in minutes from event e to the current minute,
     folded onto (-720, 720] so midnight cannot split a window */
  function since(cur, e) {
    var d = (cur - e) % 1440;
    if (d > 720) d -= 1440;
    if (d <= -720) d += 1440;
    return d;
  }

  function computedState(now) {
    var ev = solarEvents(now);
    if (!ev || !isFinite(ev.rise) || !isFinite(ev.set)) return null;
    var cur = now.getUTCHours() * 60 + now.getUTCMinutes();
    var r = since(cur, ev.rise), s = since(cur, ev.set);
    if (r >= -40 && r <= 50) return 'sunrise';
    if (s >= -50 && s <= 40) return 'sunset';
    return (r > 0 && s < 0) ? 'day' : 'night';
  }

  /* the graceful floor: four fixed windows on the civil clock */
  function fixedState(now) {
    var h = now.getHours();
    try {
      h = parseInt(new Intl.DateTimeFormat('en-US', {
        timeZone: 'America/Denver', hour: 'numeric', hourCycle: 'h23'
      }).format(now), 10);
      if (!isFinite(h)) h = now.getHours();
    } catch (e) { h = now.getHours(); }
    if (h >= 5 && h < 8) return 'sunrise';
    if (h >= 8 && h < 19) return 'day';
    if (h >= 19 && h < 22) return 'sunset';
    return 'night';
  }

  function tint() {
    var now = new Date(), state;
    try { state = computedState(now); } catch (e) { state = null; }
    if (!state) state = fixedState(now);
    document.documentElement.setAttribute('data-sky', state);
  }

  tint();
  /* the sky moves slowly; look up again every ten minutes */
  setInterval(tint, 600000);
})();
