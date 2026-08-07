/* ============================================================
   hints.js · term hints · emission of U-08
   A word that carries weight takes its definition where it
   stands. Markup per commons.css (.term / .term-card):

     <span class="term">
       <button type="button" aria-expanded="false">patronage</button>
       <span class="term-card" role="note">...</span>
     </span>

   This script manages tap-to-open, Escape, outside taps, and
   aria-expanded. Without it the card still shows on hover and
   keyboard focus through commons.css alone; with it, touch
   readers get the same definition. Dependency free, no build
   step. Never a title attribute: those reach neither touch
   nor keyboard.
   The Common Record Series · RegenHub, LCA · August 2026
   ============================================================ */
(function () {
  'use strict';

  function closeAll(except) {
    document.querySelectorAll('.term.open').forEach(function (t) {
      if (t === except) return;
      t.classList.remove('open');
      var b = t.querySelector('button');
      if (b) b.setAttribute('aria-expanded', 'false');
    });
  }

  function init() {
    var terms = document.querySelectorAll('.term');
    terms.forEach(function (t, i) {
      var btn = t.querySelector('button');
      var card = t.querySelector('.term-card');
      if (!btn || !card) return;
      if (!card.id) card.id = 'term-card-' + (i + 1);
      btn.setAttribute('aria-expanded', 'false');
      btn.setAttribute('aria-describedby', card.id);
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        var open = !t.classList.contains('open');
        closeAll(t);
        t.classList.toggle('open', open);
        btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
    });
    document.addEventListener('click', function (e) {
      if (!e.target.closest || !e.target.closest('.term')) closeAll(null);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        var open = document.querySelector('.term.open button');
        closeAll(null);
        if (open) open.focus();
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
