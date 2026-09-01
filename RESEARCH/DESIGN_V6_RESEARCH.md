# Design system v6: research

Two strands, then a synthesis against v5. Commissioned by the steward through Nou, September 2026. Sources were fetched and read unless marked *snippet only*, in which case the page was seen in search results and could not be opened; nothing below is invented, and where a claim could not be verified it says so.

Rules this file keeps: no em dashes (CI style lint), no emoji, and no claim about what an instrument says without its source.

## Strand A: the visual signature of default LLM web design

### Sources

1. Eduardo Calvo, "AI Design Slop: Why AI-Generated UI Looks Generic, and the Fix", SmoothUI, 2026-06-24. https://smoothui.dev/blog/ai-design-slop
   Purple-to-cyan hero gradients, glassmorphism with a neon glow, six identical cards each with an icon, a heading, and two lines, bounce-on-hover, missing focus states, WCAG contrast failures, undesigned empty and error states. Explains the look as the model reaching for the most statistically common pattern.
2. Yusuf, "AI Slop Fonts and Gradients: The Tells That Give Away AI Design", 925 Studios, 2026-06-14. https://www.925studios.co/blog/ai-slop-design-tells
   Four clustered tells: Inter everywhere; indigo-to-purple gradients traced to Tailwind's `indigo-500`; three rounded cards in a row; weightless copy ("Build faster. Ship smarter.") with thin interchangeable line icons. "All of them together is the AI fingerprint."
3. prg.sh, "Why Your AI Keeps Building the Same Purple Gradient Website", 2025-10-26. https://prg.sh/ramblings/Why-Your-AI-Keeps-Building-the-Same-Purple-Gradient-Website
   Inter or Roboto, purple gradients on white, centered hero and CTA, three feature boxes with icons, rounded corners on everything, shadows at exactly 0.1 opacity. Root cause: the model returns the median of every Tailwind tutorial scraped from GitHub. Discussed on Hacker News 2026-01-07 (https://news.ycombinator.com/item?id=46532362; thread body returned 429, comments unverified).
4. Paul Bakaus, "Slop", Impeccable, undated. https://impeccable.style/slop/
   The most granular catalogue found, 66 patterns: purple-to-blue gradients, glassmorphism and neon glow, side-tab colored borders on cards, hairline border plus wide soft shadow, over-rounded 24px+ blob cards, kicker and pill-chip eyebrows above the H1, icon tiles stacked above headings, italic-serif display accents, overused faces (Inter, Geist, Space Grotesk, Instrument Serif), radial gradient halos, dark mode with glowing box shadows, gradient text on headings and metrics, cream and beige as the "tasteful" default, nested cards, identical card grids, monotonous spacing, hero-metric template, pulsing status dots, fake cursors, marquees, bounce and elastic easing, em dash overuse, SaaS buzzwords.
5. Alan West, "Why Every AI-Built Website Looks the Same (Blame Tailwind's Indigo-500)", DEV Community, 2026-03-25. https://dev.to/alanwest/why-every-ai-built-website-looks-the-same-blame-tailwinds-indigo-500-3h2p
   Purple gradient, Inter, rounded cards with subtle shadows, `border-radius: 0.5rem` on everything, three-column feature grid with icons, gradient text in the hero. "The AI isn't designing. It's averaging," with the feedback loop as output re-enters training data.
6. Developers Digest (research by Adrian Krebs), "AI Design Slop: 16 Patterns That Out Your App as Vibe-Coded", 2026-04-22. https://www.developersdigest.tech/blog/ai-design-slop-and-how-to-spot-it
   Inter for everything; Space Grotesk, Instrument Serif, Geist combos; italic-serif accent word; "VibeCode Purple"; permanent dark mode with grey body text; gradients everywhere; colored glows; centered hero; badge above the H1; colored top and left card borders; identical icon-on-top feature cards; 1-2-3 step sequences; stat banner rows; sidebar navigation with emoji icons; all-caps section labels.
7. Mfonobong Umondia for Google Developer Group, "Why AI Websites All Look the Same and How to Build Something Different", DEV Community, August 29 (year not shown; 2025 or 2026). https://dev.to/gdg/why-ai-websites-all-look-the-same-and-how-to-build-something-different-1gan
   Oversized centered hero, purple-to-blue glow behind everything, three or four rounded feature cards, logo rows, testimonials in soft-shadow boxes, single indigo accent on white, Inter, Poppins, Manrope, generous radius, bento grids, glassmorphism, floating dashboard mockups, animated backgrounds, and the fixed order hero, social proof, features, testimonials, pricing, FAQ.
8. Adam Wathan (Tailwind CSS), X post, August 2025. https://x.com/adamwathan/status/1953510802159219096. *Snippet only*; quoted by sources 2, 3, and 5: an apology for making every Tailwind UI button `bg-indigo-500`, "leading to every AI generated UI on earth also being indigo." The canonical origin story for the purple tell.
9. Kate Moran, Raluca Budiu, Sarah Gibbons, "State of UX 2026: Design Deeper to Differentiate", Nielsen Norman Group, 2026-01-16. https://www.nngroup.com/articles/state-of-ux-2026/
   No tell list; the institutional framing. "Anyone will be able to make a decent-looking UI (at least from a distance)" because UI is cheaper to produce through standardization; "if you're just slapping together components from a design system, you're already replaceable by AI."

Not verifiable: Yuwen Lu, "Signs of vibe coded UI" (X article, 402); Mohit Phogat, Medium, August 2026 (403). No Smashing Magazine or CSS-Tricks piece cataloguing these tells was found; NN/g is the closest authoritative institution.

### Consolidated checklist

| tell | named by |
|---|---|
| purple or indigo to blue (or cyan) gradient, especially behind a hero | 1, 2, 3, 4, 5, 6, 7, 8 |
| Inter (also Roboto, Poppins, Manrope, Geist, Space Grotesk) as the default face | 2, 3, 4, 5, 6, 7 |
| glassmorphism, frosted cards, neon glow | 1, 4, 7 |
| three (or N identical) feature cards in a row, icon on top | 1, 2, 3, 5, 6, 7 |
| centered hero headline and CTA | 3, 5, 6, 7 |
| gradient text on headings or metrics | 4, 5 |
| rounded corners on everything; 24px+ blobs | 3, 4, 5, 7 |
| low-opacity shadows; hairline border plus wide soft shadow | 3, 4, 5, 7 |
| colored top or left card border as a side-tab accent | 4, 6 |
| bento grids; identical card grids | 7, 4 |
| emoji as icons | 6 |
| thin interchangeable line icons | 2 |
| eyebrow, kicker, or pill badge above the H1 | 4, 6 |
| italic serif accent word in the hero | 4, 6 |
| dark mode with glowing box shadows and grey low-contrast body | 4, 6 |
| radial halos, animated backgrounds | 4, 7 |
| the fixed skeleton: hero, logos, features, testimonials, pricing, FAQ | 7, 5 |
| stat banner rows, 1-2-3 step sequences, hero-metric template | 4, 6 |
| nested cards; monotonous symmetrical spacing | 4 |
| pulsing dots, fake cursors, marquees, bounce and elastic easing | 1, 4 |
| weightless copy, SaaS buzzwords, em dash overuse | 2, 4 |
| cream or beige as the "tasteful" escape default | 4 |
| missing focus, empty, and error states; WCAG failures | 1, 6 |

The lesson the sources agree on is not any one item. Source 2 says it outright: it is the combination, unreasoned, that is the fingerprint. A kicker above a heading is a century of editorial convention; a kicker above a heading over a purple gradient in Inter beside three rounded cards is the median of a corpus.

## Strand B: the Southwest as a source, and the appropriation line

### Geometry, structure, and the color of place

10. Lauren Fuka, "Object Monday: Two Grey Hills Navajo weaving", Maxwell Museum of Anthropology, UNM, 2020-05-11. https://maxwellmuseum.unm.edu/news-events/news/object-monday-two-grey-hills-navajo-weaving
    Two Grey Hills (c. 1910-15): intricate geometric designs with four-fold symmetry, undyed handspun wool in natural greys, browns, black, and white obtained by carding, very high weft count. The museum text is technical and historical and assigns no symbolic meaning to the motifs.
11. Jill Ahlberg Yohe, "Situated Flow: A Few Thoughts on Reweaving Meaning in the Navajo Spirit Pathway", Museum Anthropology Review, Indiana University. https://scholarworks.iu.edu/journals/index.php/mar/article/view/1033/2037
    The ch'ihónít'i ("a way out") is a contrasting line from the inner design to the border, woven so the weaver can separate herself from a product made to sell. Cites Gladys Reichard on the buyer's perpetual "But what does it mean?" and the fact that weavers often hold designs as personal or family practice rather than a symbol code. The key scholarly source for treating the spirit line as a culturally specific practice, not a device.
12. Donna Baldwin, "A Brief History of Navajo Rug Weaving", Sharlot Hall Museum, 2024-09-06. https://archives.sharlothallmuseum.org/articles/days-past-articles/1/a-brief-history-of-navajo-rug-weaving
    The named regional styles (Two Grey Hills, Ganado Red, Storm, Eye Dazzler) crystallized through trading-post marketing by Hubbell and J. B. Moore in the late 1800s. The named styles are a specific Diné-and-trader lineage, not a generic Southwest look.
13. "Sikyátki Polychrome", American Southwest Virtual Museum, Northern Arizona University. https://swvirtualmuseum.nau.edu/wp/index.php/artifacts/pottery/jeddito-yellow-ware/sikyatki-polychrome/
    Hopi Mesas, AD 1375-1625: yellow-to-cream body, black, brown, and red paint; early geometric, later life forms. The Nampeyo revival of this ware is the basis of modern Hopi pottery.
14. "Acoma Pottery", Sky City Cultural Center and Haak'u Museum, Pueblo of Acoma. https://skycityacoma.org/acoma-pueblo/acoma-pottery/
    Thin walls, fluted rims, black fine-line and orange-black polychrome on white; hatching "to symbolize rain, lightning, thunderclouds, and mountains"; designs shaped by the cycle of life, water, and the sky. A tribally authored source stating that Acoma geometry carries meaning.
15. "Taos Pueblo World Heritage Site", National Park Service. https://www.nps.gov/articles/000/taos-pueblo-world-heritage-site.htm (UNESCO listing https://whc.unesco.org/en/list/492/, inscribed 1992; returned 403 on fetch)
    Sun-dried adobe, walls 70 cm at the base tapering to 35 cm, a stacked and stepped-back form five to six storeys high. The terraced setback massing is the physical origin of the stepped Pueblo silhouette.
16. Edith Cherry and James See, "Chaco Culture National Historical Park", The Guide to New Mexico Architecture, 2022-11-27. https://nmarchitectureguide.org/2022/10/28/chaco-culture-national-historical-park/
    Core-and-veneer walls with shaped, matched face stones; five recognized masonry types; banding by rows of slightly darker or thinner stones; at Chetro Ketl, large blocks alternating with rows of small tablet-shaped stones. Strata-like banding produced by construction, not iconography.
17. Pat Finn, "Fifty Shades of Brown: An Architect's Guide to Santa Fe", Architizer Journal, undated. https://architizer.com/blog/inspiration/stories/architects-guide-to-santa-fe-new-mexico/
    Pueblo Revival: stepped massing, rounded corners, battered walls, projecting vigas, codified by Isaac Rapp (La Fonda, 1922); the 1957 ordinance drafted under John Gaw Meem mandates Pueblo, Pueblo-Spanish, and Territorial styles in the historic district; locals argue whether a brown is "too orange." The Santa Fe palette is itself a twentieth-century civic construction layered on Pueblo forms.
18. "Georgia O'Keeffe: Abstraction", Whitney Museum audio guide, 2009. https://whitney.org/guides/4 ; "Georgia O'Keeffe: Ghost Ranch Views", Georgia O'Keeffe Museum. https://www.okeeffemuseum.org/exhibitions/georgia-okeeffe-ghost-ranch-views/
    Her late vocabulary of geometric color and flat planes, adobe facades in reds and whites, simplified abstractions of Pedernal, the red hills, cliffs, and badlands. The model for a non-Native abstraction of landform and light rather than of Indigenous pattern.

Color of place: no authoritative design-scholarship source for a canonical adobe, sandstone, turquoise, sage, dusk palette was found; what exists is decor and paint-vendor copy (*snippet only*: bigoxprinting.com, santafe-painters.com). The better anchors are 17 (earth tones by ordinance), 10 (undyed wool greys and browns), 13 (yellow, black, red), and 18 (red hills, blue sky).

### The appropriation line

19. Indian Arts and Crafts Act of 1990, U.S. Department of the Interior, Indian Arts and Crafts Board. https://www.doi.gov/iacb/act
    A truth-in-advertising statute: illegal to sell any product "in a manner that falsely suggests it is Indian produced, an Indian product, or the product of a particular Indian or Indian tribe." The law does not forbid making Indian-style objects; it forbids implying Native origin or using tribal names deceptively.
20. Navajo Nation v. Urban Outfitters, Inc., D.N.M., 2016-09-19, NARF National Indian Law Library bulletin. https://www.narf.org/nill/bulletins/federal/documents/navajo_nation_v_urban_outfitters_2016.html
    Summary judgment for the Nation against the genericness and abandonment defenses to its NAVAJO mark; settled November 2016 with a license and supply agreement (Indianz, *snippet only*). A tribal name is a protectable mark, not a style adjective.
21. Kate Nelson, "Who Owns the Zia Sun Symbol?", New Mexico Magazine, 2019-01-08, updated 2021-12-07. https://www.newmexicomagazine.org/blog/post/favorite-sun/
    Harry Mera copied the symbol from a Zia Fire Society pot for the 1925 state flag without asking the Pueblo, whose members could not then vote. Zia Pueblo holds it was taken illegally, pursues trademark and legislative protection, and runs a voluntary system in which users seek advice on the depiction and contribute to a scholarship fund. Related NCAI resolution and the 2014 report to the New Mexico Legislature's Indian Affairs Committee could not be opened (timeout, 403); details from snippets are unverified.
22. Adrienne Keene (Cherokee Nation), "Cultural appropriation reinforces past wrongs", Indianz.com, 2015-08-04. https://indianz.com/News/2015/08/04/adrienne-keene-cultural-approp.asp
    "The difference is one of power." "Each image or design comes from a particular tribe, often even a particular family, and we should have the ability to share, or not share, as we see fit." Blanket labels (Navajo, Aztec, tribal) erase that specificity.
23. Maria C. Hunt, "The Pendleton Problem", Dwell, 2020-09-14. https://www.dwell.com/article/cultural-appropriation-home-decor-pendleton-60491a02
    Diné weaver Venancio Aragon, Pawnee artist Bunky Echo-Hawk, and Louie Gong (Nooksack) on trade blankets: not binary, but the line is who designs, who profits, and who controls the narrative.
24. Gabriel S. Galanda, "Unwarranted: Violating the Federal Indian Arts and Crafts Act", Galanda Broadman, 2016-06-21. https://www.galandabroadman.com/blog/2016/6/pendleton-is-the-urban-outfitters-of-150-years-ago
    After a 2013 settlement Pendleton relabeled products "Native American Inspired"; Galanda argues that phrasing can still violate 25 U.S.C. 305e when the design vocabulary itself signals tribal authorship. "Inspired" is not a safe harbor.
25. Eighth Generation, "About Us", Snoqualmie Tribe-owned, founded 2008 by Louie Gong. https://eighthgeneration.com/pages/about-us
    "Inspired Natives, not Native-inspired." Also Beyond Buckskin (Jessica Metcalfe), appropriation archive: http://www.beyondbuckskin.com/search/label/appropriation
26. Shannon Burke, "The Commodified Kokopelli", Georgetown, 2019. https://kokopelli.georgetown.domains/a-huge-misunderstanding/
    The commercial flute player is a misattribution of the Hopi katsina Kookopölö; Hopi scholar Alph Secakuku (1995): "He is not a Flute player." A katsina is a religious being and is off limits.

Bethany Yellowtail (Apsáalooke and Northern Cheyenne): profiles at PBS SoCal Artbound and LAist, *snippet only*, report she designs for all people but from a tribe where headdresses are reserved for specific people, and that KTZ's 2015 copy of her Crow-inspired dress reignited the debate. No primary quote could be fetched.

### The line this system draws

A non-Native design system may draw from the physical and geological Southwest and from technique in general:

- terraced setback massing and battered walls as landform and architecture (15, 17);
- strata and masonry banding, which construction and erosion produce rather than iconography (16);
- adobe, sandstone, undyed-wool greys and browns, red hill and blue sky, and the light of dusk as gradient (10, 17, 18);
- flat-plane color abstraction of landform in the O'Keeffe manner (18);
- weaving as a general technique: warp and weft, the twill diagonal every loom in the world makes (10, as structure only).

It must not reproduce culturally owned or sacred material:

- the named Diné regional styles and their signature compositions (Two Grey Hills, Ganado, Eye Dazzler, Storm), the stepped diamond and serrated figure as a composition, and the spirit line (10, 11, 12);
- Acoma, Zuni, and Hopi pottery motifs, including fine-line hatching as a figure and Sikyátki forms, which the Pueblo of Acoma states carry meaning (13, 14);
- katsina figures and the commercial Kokopelli (26); the Zia sun (21); the stepped-cloud or terrace-cloud motif as a symbol;
- any tribal name, "Navajo print," or "Native-inspired" label in a token name, a class name, or a caption (19, 20, 24).

The test v6 applies to every motif: if it can be named after a people, a pueblo, a trading post, or a ceremony, it does not enter. If it can only be named after a landform, a light, a wall, or a machine, it may. Where the cooperative ever wants Indigenous pattern on its estate, the documented path is licensing or collaboration with named Native designers on their terms (23, 25), never adaptation, and that is a steward's decision, not a stylesheet's.

Three consequences for the ornament layer:

- Stepped forms enter only as horizontal landform profiles: runs of unequal length, one direction, never symmetrical, never mirrored into a diamond, never nested. A bench, not a blanket.
- Hatching enters only as twill, a diagonal structure with no figure, no border, no center, at a strength below notice.
- No token, class, or caption names a Nation. The vocabulary is strata, terrace, descent, field, weave, grain, tick, ground, wash.

## Synthesis against v5

### What the research indicts

- **The type specimen block.** v5's specimens name "Georgia · 2.2rem" for a display heading while the page renders Libre Baskerville at 34px and commons.css sets 38px; the specimens are a leftover from a retired face. Not a slop tell but a defect of the same kind: a default nobody chose. Replaced by a named scale.
- **No radius rule.** 2px is written as a literal roughly thirty times across the reference and commons.css, and pages under commons/ drift to 4, 5, 6, and 8px. Source 3, 4, 5, 7 name rounding-by-default as the fingerprint. v6 tokens the radius at 2px for controls and 0 for everything else.
- **The side-tab accent on cards.** Sources 4 and 6 name a colored top or left border on every card as a tell. v5's participation card and the front page's cards carry a 2px tinted top border. v6 keeps the left rule only where it means provenance (the provenance chip, the excerpt, the escalation card) and replaces the tinted top bar on section cards with the terrace edge, a shape that says which section a card belongs to.
- **`--info` equals `--blue`.** A condition wearing the action color. The three earth states were meant to sit on instruments and never on controls; giving "in review" the link color breaks that in the other direction. v6 moves `--info` to the violet text-safe stop.
- **The eyebrow everywhere.** Sources 4 and 6 name the kicker above the H1. v5 uses the eyebrow on every section head. v6 keeps it, because on this estate the eyebrow is the citable address, which is a reason; and removes it from places where it carried nothing but a mood (the design-system's own masthead kicker becomes the address line).
- **Grey body on dark.** Source 6 names low-contrast grey body on permanent dark. v5's dark `--text` at #CFCBC4 on #0F0F12 is 11.8:1 (checked by script, WCAG 2.1 relative luminance); but `--muted` is used as the body color of lede paragraphs on the front page, at 5.2:1 on the dark ground, and a lede in the label color is the pattern the source names. v6 says: `--muted` is for labels and secondary lines, never a lede.
- **Six content measures in live use** (70rem, 1060, 920, 860, 800, 780). Not a slop tell, but monotony's opposite defect: nothing decided. v6 names three.

### What the research vindicates

- **Two faces, neither of them Inter.** Libre Baskerville and IBM Plex Mono are the opposite of the default (sources 2, 3, 5, 6, 7). Kept.
- **A warm, low-saturation palette with no purple gradient.** The sunset range runs through violet, but as one stop of six in a luminance-ordered sweep, never as a hero glow. The horizon line is the register's argument against the halo. Kept, and the strata register is built from the same tokens.
- **No glassmorphism, no shadows, no gradient text, no bento.** v5 has none of them; commons.css carries not one box-shadow. Vindicated, written down as rules so they cannot arrive by accident.
- **No emoji, Lucide inlined and always beside a word.** Vindicated by source 6.
- **The honest states.** v5's `.absence`, `.skel`, and `.first-run` answer source 1 directly; v6 gives absence a designed room (the dry wash).
- **Reduced motion honored; motion only on color and opacity.** Sources 1 and 4 name bounce and marquee. v6 writes the rule that nothing translates, scales, or reveals on scroll.
- **The parchment ground.** Source 4 names cream as an escape default. On this estate it is not an escape: it is the color of the place, and the record of that decision is v4. Kept, with the caution noted.
