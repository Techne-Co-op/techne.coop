# Two Named Sunset Palettes — a proposal

**Status: drafted, not adopted.** Staged with the U-24 packet (design-system v5), 2026-08-18. Also recorded, with live swatches, in the proposal section of techne.coop/design-system/. Until a steward adopts one, the v4 sunset range remains the only range a page may use.

The idea: the estate's sunset range is one specific evening. These are two others — complete token sets, either able to stand where the standing range stands, as distinct artistic directions rather than variations.

## Vermilion Hour — the warm direction

The last hour over red rock: iron and vermilion out of the cliff face, ember and amber in the air, gold at the rim, and one bruised violet where the shadow already is. Warmer and deeper than the standing range, which reads as sky; this one reads as stone holding the day's heat.

| token | canonical | dark-mode text | light-mode text |
|---|---|---|---|
| `--verm-dusk` | `#6E4E88` | `#A98CCB` | `#5A3F76` |
| `--verm-iron` | `#A04A48` | `#D18B89` | `#8F3E3C` |
| `--verm-vermilion` | `#C25B3F` | `#E08D74` | `#96422C` |
| `--verm-ember` | `#D97E48` | `#E8A170` | `#8F5426` |
| `--verm-amber` | `#E8A45C` | `#ECB278` | `#855417` |
| `--verm-gold` | `#F2C878` | `#F2C878` | `#7A5A12` |

## Juniper Twilight — the cool direction

The high desert after the color leaves the sky: cold night blue, slate, one green the landscape actually holds (juniper on the far slope), then lilac gray, shell, and the pale gold of the afterglow. Cooler and quieter than the standing range; it reads as air, altitude, and the first cold hour. Named "twilight," not "dawn," because the design system already keeps a dawn range and this is not it.

| token | canonical | dark-mode text | light-mode text |
|---|---|---|---|
| `--jun-night` | `#46567E` | `#8FA3CE` | `#3C4A70` |
| `--jun-slate` | `#64789E` | `#93A9D0` | `#465A85` |
| `--jun-juniper` | `#6E8C80` | `#8FB2A4` | `#3F5C50` |
| `--jun-lilac` | `#988FB4` | `#AFA6CC` | `#5C5478` |
| `--jun-shell` | `#C4AD9A` | `#C4AD9A` | `#6E5A44` |
| `--jun-pale-gold` | `#E4CD9C` | `#E4CD9C` | `#6E5C24` |

## Contrast record

Checked by script, 2026-08-18: WCAG 2.1 relative-luminance contrast for every text-safe value against all three grounds of its mode (`--bg`, `--inset`, `--surface`; dark `#0F0F12`/`#08080A`/`#16161B`, light `#F7F5F0`/`#EBE7DF`/`#FCFBF8`).

- **All 24 text values pass AA for body text (>= 4.5:1).**
- Worst pair on the board: Vermilion Hour light-mode `--verm-ember-t` at **4.92:1** against `--inset`. Everything else is 5.16:1 or better; dark mode's floor is 6.27:1.
- Both canonical ramps are strictly ordered by luminance, so a sequential scale degrades to grayscale and reads for colorblind viewers — the same discipline the standing range keeps.
- Canonical stops are atmosphere and data only; only a `-t` value may color type. Same rules as the standing range: never a control, never the sign of a number.

## Selection mechanism (specified, not built)

Mirrors the mode toggle exactly:

- `localStorage` key `techne-palette`, values `vermilion` | `juniper`, unset = the standing range.
- A boot script beside the existing `techne-mode` script sets `data-palette` on `<html>` before first paint.
- CSS remaps the six `--sun-*` and six `--sun-*-t` properties under `html[data-palette="..."]` — every page written against the token names inherits the choice with no markup change.

Alternative seam: resolve from the local clock (Juniper Twilight night-into-dawn, Vermilion Hour through the evening, standing range through the day), with the stored key always winning over the clock. Either way it is one script and one attribute, no dependency. Building it is a separate piece with its own address; naming a palette in public is the steward's call.
