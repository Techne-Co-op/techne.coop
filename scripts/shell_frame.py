#!/usr/bin/env python3
"""shell_frame.py - the frame is written, not hand-kept (U-19).

U-18 made the frame's appearance load with the document, so the
@view-transition opt-in is present at pagereveal and transitions run.
The furniture itself was still raised by a deferred script, so the two
named elements, cis-topbar and cis-side, did not exist at pagereveal
and the browser had nothing to morph. It fell back to a whole-root
cross fade, which is a transition of the page rather than of the frame.

U-19 puts the frame in the markup. That would ordinarily mean the same
block copied into thirteen documents, which is the failure this estate
has already paid for twice: nine surfaces each hand-rolling a content
width until U-20 wrote measure_audit.py, and twenty-four ledger marks
drifting until X-19. A copy nothing checks is a copy that drifts.

So the frame is generated from one manifest, assets/shell-map.json, and
written into a marked block on every surface that loads shell.js. The
block is regenerated rather than edited, exactly as validate.py writes
the Almanac's ledger-state block, and --check refuses a stale copy in
CI. The surface list is derived from the repository, never hardcoded,
so a new surface cannot be forgotten and a retired one cannot linger.

  python3 scripts/shell_frame.py            write the blocks
  python3 scripts/shell_frame.py --check    refuse a stale block
  python3 scripts/shell_frame.py --self-test  prove the check refuses

The gate is not here. The frame's markup is inert; whether it paints is
decided before the first paint by assets/shell-gate.js and the
html:not([data-cis="in"]) rules in assets/shell.css.

The Common Record Series · RegenHub, LCA · August 2026
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, 'assets', 'shell-map.json')

OPEN_START = '<!-- generated:shell-frame -- written by scripts/shell_frame.py; do not edit by hand -->'
OPEN_END = '<!-- /generated:shell-frame -->'
CLOSE_START = '<!-- generated:shell-frame-close -- written by scripts/shell_frame.py; do not edit by hand -->'
CLOSE_END = '<!-- /generated:shell-frame-close -->'

BODY_RE = re.compile(r'<body[^>]*>')
FOOTER_RE = re.compile(r'^([ \t]*)<footer\b', re.M)
"""A block is stripped together with the newline that follows it, so a
strip and a re-render return the document to exactly where it started.
Leaving the newline behind made rendering non-idempotent, which meant
every run rewrote every surface and the freshness check could never be
green twice. Caught by the self-test below, not by reading."""
OPEN_BLOCK_RE = re.compile(re.escape(OPEN_START) + r'.*?' + re.escape(OPEN_END) + r'\n?', re.S)
CLOSE_BLOCK_RE = re.compile(re.escape(CLOSE_START) + r'.*?' + re.escape(CLOSE_END) + r'\n?', re.S)

findings = []


def note(msg):
    findings.append(msg)


"""A surface is a document that *loads* the shell, which is a script
tag, not a document that *mentions* it. commons/ui/ and design-system/
both describe the shell at length and one of them prints an escaped
worked example of the very tag; a substring test hands them a members'
frame they must never carry, since both are public pages that load
topbar.js instead. Matching the tag rather than the path is the whole
difference between eleven surfaces and thirteen."""
SCRIPT_RE = re.compile(r'<script\s[^>]*src="/assets/shell\.js"[^>]*>')


def is_public(text):
    """A public page (U-15) carries data-public on the shell tag. Signed
    out it keeps its own topbar and shows no members' furniture at all;
    a members' surface signed out still shows the topbar above the gate
    card. That is three states, and the third is why the frame carries
    the flag in its own class: shell.css must be able to tell them
    apart before the first paint, and a deferred script cannot."""
    m = SCRIPT_RE.search(text)
    return bool(m and 'data-public' in m.group(0))


def surfaces(root=ROOT):
    """Every document that loads the shell. Derived, never listed."""
    out = []
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in ('.git', '.wt', 'node_modules', '.scratch')]
        for name in files:
            if not name.endswith('.html'):
                continue
            path = os.path.join(base, name)
            with open(path, encoding='utf-8') as fh:
                if SCRIPT_RE.search(fh.read()):
                    out.append(path)
    return sorted(out)


def icon(svg):
    return (
        '<svg class="lucide" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" '
        'aria-hidden="true">' + svg + '</svg>'
    )


"""The mode toggle names the mode the press switches to: moon and
"Dark" while the page is light, sun and "Light" while it is dark.
Both states are in the markup and shell.css gates them on
html[data-mode], so the control is right before shell.js wires the
click. Lucide sun and moon, per the U-08 icon amendment; the icon is
decorative beside its word."""
MOON = '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>'
SUN = ('<circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/>'
       '<path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/>'
       '<path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/>'
       '<path d="m19.07 4.93-1.41 1.41"/>')
MODE_BUTTON = (
    '<button type="button" class="cis-mode" aria-label="toggle light and dark mode">'
    '<span class="cis-mode-to-dark">' + icon(MOON) + 'Dark</span>'
    '<span class="cis-mode-to-light">' + icon(SUN) + 'Light</span>'
    '</button>'
)


def open_block(manifest, public=False):
    """The topbar, the map, and the two wrappers the page content sits in.

    Written flat and without the active mark: which item is active is a
    property of the reader's address, not of the document, so shell.js
    marks it after the gate has opened. The chip reads not signed in
    until the session is resolved, which is what a document with no
    session honestly says.
    """
    L = [OPEN_START]
    L.append('<header class="cis-topbar' + (' cis-public' if public else '') + '">')
    L.append('  <a class="cis-brand" href="/intranet/">Techne<span class="cis-brand-suffix"> &middot; intranet</span></a>')
    L.append('  <div class="cis-topbar-right">')
    L.append('    <button type="button" class="cis-menu" id="cis-menu-btn" aria-expanded="false" aria-controls="cis-map" aria-label="show the intranet map">Menu</button>')
    L.append('    <button type="button" class="cis-bell" aria-expanded="false" aria-controls="cis-notices" aria-label="notices addressed to you">Notices</button>')
    L.append('    <span class="cis-chip" id="cis-member-chip">not signed in</span>')
    L.append('    ' + MODE_BUTTON)
    L.append('  </div>')
    L.append('</header>')
    L.append('<div class="cis-body">')
    L.append('<nav class="cis-side" id="cis-map" aria-label="intranet">')
    for grp in manifest:
        steward = grp.get('steward')
        pad = '  ' if steward else ''
        if steward:
            L.append('  <div id="cis-steward-nav" style="display:none">')
        if grp.get('group'):
            L.append(pad + '  <div class="cis-group">' + grp['group'] + '</div>')
        for it in grp['items']:
            cls = ' class="cis-out"' if it.get('outside') else ''
            tint = ' data-tint="' + it['tint'] + '"' if it.get('tint') else ''
            body = icon(it['icon']) if it.get('icon') else ''
            L.append(pad + '  <a href="' + it['href'] + '"' + cls + tint + '>' + body + it['label'] + '</a>')
        if steward:
            L.append('  </div>')
    L.append('  <a class="cis-out cis-home" href="/">&#8592; techne.coop</a>')
    L.append('  <div class="cis-side-you">signed in</div>')
    L.append('</nav>')
    L.append('<div class="cis-main">')
    L.append(OPEN_END)
    return '\n'.join(L)


def close_block():
    """Closes .cis-main and .cis-body.

    Placed before the page's own footer where it has one, so the footer
    spans the whole frame rather than the column beside the map. That is
    the placement shell.js used to reach by lifting the footer out of
    the column after the fact (U-15).
    """
    return CLOSE_START + '\n</div><!-- .cis-main -->\n</div><!-- .cis-body -->\n' + CLOSE_END


def render(text, manifest, path='<memory>'):
    """Return text with both blocks present and current."""
    text = OPEN_BLOCK_RE.sub('', text)
    text = CLOSE_BLOCK_RE.sub('', text)

    m = BODY_RE.search(text)
    if not m:
        note('%s: no <body> tag' % path)
        return None
    text = text[:m.end()] + '\n' + open_block(manifest, is_public(text)) + text[m.end():]

    tail_from = text.index(OPEN_END) + len(OPEN_END)
    fm = FOOTER_RE.search(text, tail_from)
    if fm:
        at = fm.start()
    else:
        at = text.rfind('</body>')
        if at < 0:
            note('%s: no </body> tag' % path)
            return None
    return text[:at] + close_block() + '\n' + text[at:]


def run(check=False):
    with open(MANIFEST, encoding='utf-8') as fh:
        manifest = json.load(fh)
    paths = surfaces()
    if not paths:
        note('no surface loads /assets/shell.js; the frame would be written nowhere')
        return
    stale = 0
    for path in paths:
        with open(path, encoding='utf-8') as fh:
            before = fh.read()
        after = render(before, manifest, os.path.relpath(path, ROOT))
        if after is None:
            continue
        if after == before:
            continue
        stale += 1
        if check:
            note('%s: frame block stale or missing' % os.path.relpath(path, ROOT))
        else:
            with open(path, 'w', encoding='utf-8') as fh:
                fh.write(after)
    if not check:
        print('shell-frame: %d surface(s), %d rewritten' % (len(paths), stale))


DOC = (
    '<!doctype html><html><head>'
    '<script src="/assets/shell.js" defer></script>'
    '</head><body>\n<main>page</main>\n<footer>foot</footer>\n</body></html>'
)


def self_test():
    """Each case is a way this check could quietly stop checking."""
    with open(MANIFEST, encoding='utf-8') as fh:
        manifest = json.load(fh)
    fails = []

    full = render(DOC, manifest)
    if full is None or OPEN_START not in full or CLOSE_START not in full:
        fails.append('a bare document does not receive both blocks')
    else:
        print('self-test: a bare document receives both blocks')

    if render(full, manifest) != full:
        fails.append('rendering a rendered document is not stable')
    else:
        print('self-test: rendering is idempotent')

    if full.index(CLOSE_START) > full.index('<footer'):
        fails.append('the close block does not precede the footer')
    else:
        print('self-test: the close block precedes the footer')

    nofoot = DOC.replace('\n<footer>foot</footer>', '')
    r = render(nofoot, manifest)
    if r is None or r.index(CLOSE_START) > r.index('</body>'):
        fails.append('without a footer the close block does not precede </body>')
    else:
        print('self-test: without a footer the close block precedes </body>')

    tampered = full.replace('Techne<span', 'Tampered<span', 1)
    if render(tampered, manifest) == tampered:
        fails.append('a tampered block is not detected')
    else:
        print('self-test: a tampered block is refused')

    dropped = OPEN_BLOCK_RE.sub('', full)
    if render(dropped, manifest) == dropped:
        fails.append('a deleted block is not detected')
    else:
        print('self-test: a deleted block is refused')

    if render('<html><head></head></html>', manifest) is not None:
        fails.append('a document with no body is not refused')
    else:
        findings.clear()
        print('self-test: a document with no body is refused')

    print('self-test: %d failure(s) over 7 case(s)' % len(fails))
    for f in fails:
        print('  ' + f)
    return 1 if fails else 0


if __name__ == '__main__':
    if '--self-test' in sys.argv:
        sys.exit(self_test())
    check = '--check' in sys.argv
    run(check=check)
    if findings:
        for f in findings:
            print('shell-frame: ' + f)
        print('shell-frame: %d finding(s)' % len(findings))
        sys.exit(1)
    if check:
        print('shell-frame: 0 finding(s)')
