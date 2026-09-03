# Intranet plain-speak pass: shared brief

Commissioned by Todd Youngblood, #intranet-dev, 2026-08-26. Position: **Co-op Principle 5
(Education, Training, and Information)**. The reader is an incoming cooperative member on
their first visit. They should be able to tell, within seconds, what this page is, what it
shows them, and what they can do next.

## What to change

1. **Jargon**: replace or gloss every term a new member would not know on sight. Prefer
   plain replacement; where the term is load-bearing (a ledger address, an adopted
   instrument name, a defined lexicon term), keep the term and gloss it inline on first use.
2. **Conditional sentences**: rewrite "if/when/should X, then Y" constructions as direct
   second-person instructions ("Do X. If you can't, Y.").
3. **Abstractions**: render abstract states as visible status indicators (badges, dots,
   labels) using the page's existing CSS tokens and badge classes. Do not invent a new
   visual language; read the page's own stylesheet and reuse it.
4. **Orientation block**: near the top of the page, a short "What this page is / What you
   can do here" block in the page's existing card idiom.

## Hard bounds

- **You may re-present a status. You may never re-state one.** If the page says a piece is
  `draft`, it stays `draft`. You change how it looks, never what it claims.
- **Never edit the ledger** (`almanac-ledger.yaml`) or any adopted instrument text.
- If a page contradicts the ledger or an adopted instrument, **report it, do not fix it**.
- **No em dashes** in authored copy (CI style-lint).
- **Targeted edits only.** Never rewrite a whole file or emit the full file as output. Use
  small, surgical string replacements. This matters most on the large pages.

## Verification

Run `python3 scripts/validate.py` from the worktree root before you finish. It must pass.
