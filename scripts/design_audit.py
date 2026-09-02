#!/usr/bin/env python3
"""Design audit (U-32) -- is the design system applied, page by page?

The estate has no build step and no shared public stylesheet: every page
inlines the token layer and its own rules, and the design system at
/design-system/ is a reference a person reads. The audits already in CI
each hold one line: token_audit.py (hex and token drift), measure_audit.py
(the frame measure), shell_frame.py (the frame markup), notice_audit.py
(the formation notice), em_dash_audit.py, and the validator's one-frame
rule. Nothing reads a page whole against the system, so a page can pass
every check and still not look like the estate: a head block missing its
Open Graph tags, a third typeface, a container width nobody chose, a size
off the scale, an rgba() literal where a token should be.

This script reads every served page against design-system/AGENT-DIRECTIONS.md,
the instruction-shaped form of the system, and reports by check. Every
rule it applies is traceable to the design-system page or to
commons/ui/commons.css, the canonical token layer; where a rule is a
convention observed on main rather than a written one, the check says so.

Three classes of finding, named in the output:

  mechanical  the fix is unambiguous and --fix applies it: a missing
              favicon link, color-scheme meta, canonical, Open Graph
              block derived from tags the page already carries, the mode
              boot script, or a hex literal that equals a token of the
              same mode and becomes var().
  judgment    the fix needs a person or a decision: a missing
              description (someone must write it), a third typeface, an
              rgba() literal, a container that is none of the three
              grammars.
  observed    not a rule the system states, only a convention read off
              commons.css: a size off the sizes the layer uses, a custom
              property the layer does not name. Reported so the drift is
              visible; never counted as a failure, because the system has
              not decided the question. A type scale was drafted at v6 and
              reverted on the steward's word (PR 276), so this script does
              not pretend one exists.

Scope: every HTML page git tracks. Exemptions match token_audit.py and
are named per VS v1 section 9: legal/ carries the formation-era record
verbatim and is reported but never fixed; design-system/ is the palette
constitution and is exempt from the color checks only.

  python3 scripts/design_audit.py            findings to stdout, exit 1 on any
  python3 scripts/design_audit.py --report design-system/AUDIT.md
  python3 scripts/design_audit.py --fix      apply the mechanical fixes
  python3 scripts/design_audit.py --json     machine-readable findings

The Common Record Series · RegenHub, LCA · September 2026
"""
import argparse
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
COMMONS = REPO_ROOT / 'commons/ui/commons.css'
NEVER_FIX = ('legal/',)
COLOR_EXEMPT = ('design-system/', 'legal/')
# Verbatim source artifacts, exempt by exact path as in validate.py: a
# document committed unaltered so a page can be checked against its source
# is held byte for byte, never audited as an authored page and never fixed.
VERBATIM = {
    'commons/governance/model-v4/governance-model-v4.html',
}

HEX_RE = re.compile(r'#[0-9a-fA-F]{3,8}\b')
FUNC_COLOR_RE = re.compile(r'\b(?:rgba?|hsla?)\(')
NAMED_COLOR_RE = re.compile(r'(?<![\w-])(white|black|red|green|blue|orange|yellow|purple|gray|grey|silver|gold)(?![\w-])', re.I)
STYLE_BLOCK_RE = re.compile(r'<style[^>]*>(.*?)</style>', re.DOTALL | re.IGNORECASE)
STYLE_ATTR_RE = re.compile(r'style="([^"]*)"')
HEAD_RE = re.compile(r'<head[^>]*>(.*?)</head>', re.DOTALL | re.IGNORECASE)
TITLE_RE = re.compile(r'<title>(.*?)</title>', re.DOTALL | re.IGNORECASE)
META_RE = re.compile(r'<meta\s+[^>]*>', re.IGNORECASE)
LINK_RE = re.compile(r'<link\s+[^>]*>', re.IGNORECASE)
ATTR_RE = re.compile(r'([\w:-]+)\s*=\s*"([^"]*)"')
FONT_LINK_RE = re.compile(r'fonts\.googleapis\.com/css2?\?([^"]*)"')
SIZE_RE = re.compile(r'(\d*\.?\d+)(px|rem)')
ALLOWED_FACES = {'Libre Baskerville', 'IBM Plex Mono'}
CONTAINERS = ('wrap-frame', 'wrap-hud', 'wrap')

MODE_BOOT = """<script>
  (function () {
    var stored = null;
    try { stored = localStorage.getItem('techne-mode'); } catch(e) {}
    var m = stored || (matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
    document.documentElement.setAttribute('data-mode', m);
  })();
</script>"""
FAVICON = ('<link rel="icon" type="image/svg+xml" href="/favicon.svg">\n'
           '<link rel="alternate icon" type="image/png" href="/favicon.png" sizes="32x32">')
COLOR_SCHEME = '<meta name="color-scheme" content="dark light">'
OG_DEFAULT_IMAGE = 'https://techne.coop/assets/og-default.png'


# ---------- css helpers (shared shape with token_audit.py) ----------

def norm(value):
    return value.lower().replace(' ', '').replace('"', '').replace("'", '')


def mode_scope(selector):
    s = selector.lower()
    if 'data-mode="dark"' in s or "data-mode='dark'" in s or '.mode-dark' in s:
        return 'dark'
    if 'data-mode="light"' in s or "data-mode='light'" in s or '.mode-light' in s:
        return 'light'
    if ':root' in s:
        return 'root'
    return None


def parse_css(css):
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
    for block in re.finditer(r'([^{}]+)\{([^{}]*)\}', css):
        selector = block.group(1).strip()
        for decl in block.group(2).split(';'):
            if ':' not in decl:
                continue
            prop, _, value = decl.partition(':')
            yield selector, prop.strip(), value.strip()


def font_sizes(css):
    """Every px or rem size a page states in font or font-size, as px."""
    out = []
    for sel, prop, val in parse_css(css):
        if prop == 'font-size' or prop == 'font':
            m = SIZE_RE.search(val)
            if not m:
                continue
            n, unit = float(m.group(1)), m.group(2)
            out.append(round(n * 16, 2) if unit == 'rem' else n)
    return out


def commons_layer():
    tokens = {}
    css = COMMONS.read_text()
    for sel, prop, val in parse_css(css):
        if prop.startswith('--'):
            sc = mode_scope(sel)
            if sc:
                tokens[(sc, prop)] = norm(val)
    scale = sorted(set(font_sizes(css)))
    return tokens, scale


def tracked_pages():
    out = subprocess.run(['git', '-C', str(REPO_ROOT), 'ls-files', '-z', '*.html'],
                         capture_output=True, text=True, check=True).stdout
    return sorted(p for p in out.split('\0') if p)


# ---------- the checks ----------

class Finding:
    __slots__ = ('page', 'check', 'kind', 'detail')

    def __init__(self, page, check, kind, detail):
        self.page, self.check, self.kind, self.detail = page, check, kind, detail

    def row(self):
        return {'page': self.page, 'check': self.check, 'kind': self.kind, 'detail': self.detail}


CHECKS = {
    # id: (title, source)
    'head-charset':      ('charset meta', 'design-system#seo, required head block 1'),
    'head-viewport':     ('viewport meta', 'design-system#seo, required head block 1'),
    'head-color-scheme': ('color-scheme meta', 'design-system#seo, required head block 1'),
    'head-title':        ('title carries the Techne pattern', 'design-system#seo, title pattern'),
    'head-description':  ('description meta present', 'design-system#seo, required head block 2'),
    'head-canonical':    ('canonical link present', 'design-system#seo, required head block 2'),
    'head-og':           ('Open Graph block complete', 'design-system#seo, required head block 3'),
    'head-favicon':      ('favicon linked from root', 'design-system#seo, required head block 4'),
    'head-mode-boot':    ('mode flash prevention inline before CSS', 'design-system#seo, required head block 5'),
    'type-faces':        ('two faces only: Libre Baskerville and IBM Plex Mono', 'design-system#type, X-06 decision 2026-07-20'),
    'type-scale':        ('font sizes among the sizes commons.css uses', 'observed convention only; no scale is adopted (v6 reverted, PR 276)'),
    'token-layer':       ('page defines both mode palettes or links commons.css', 'design-system#tokens; AGENTS.md REPO'),
    'token-private':     ('custom properties the canonical layer does not name', 'observed convention only; commons/ui/commons.css is the token layer'),
    'color-hex':         ('hex only inside a custom-property definition', 'token_audit.py X-06'),
    'color-function':    ('no rgb()/rgba()/hsl() literal outside a token definition', 'design-system#tokens: never past a token to a literal'),
    'color-named':       ('no named CSS color outside a token definition', 'design-system#tokens: never past a token to a literal'),
    'skeleton-container': ('one of the three containers: wrap, wrap-hud, wrap-frame', 'design-system#layout; commons.css the two grammars'),
    'skeleton-footer':   ('a footer element closes the page', 'observed convention: commons.css footer; notice_audit.py'),
    'skeleton-frame':    ('exactly one of topbar.js or shell.js', 'design-system#topbar; validate.py U-13'),
}


def audit_page(rel, text, tokens, scale):
    findings = []
    fixes = []           # (kind, payload) applied by --fix
    exempt_color = rel.startswith(COLOR_EXEMPT)
    if rel in VERBATIM:
        return [], [], {'container': 'verbatim', 'faces': '-', 'frame': 'verbatim', 'layer': '-'}
    head_m = HEAD_RE.search(text)
    head = head_m.group(1) if head_m else ''
    metas = {}
    for m in META_RE.finditer(head):
        attrs = dict(ATTR_RE.findall(m.group(0)))
        key = attrs.get('name') or attrs.get('property') or attrs.get('charset', '').lower() and 'charset'
        if key:
            metas[key] = attrs.get('content', '')
    links = [dict(ATTR_RE.findall(l.group(0))) for l in LINK_RE.finditer(head)]
    rels = defaultdict(list)
    for l in links:
        rels[l.get('rel', '')].append(l)

    never_fix = rel.startswith(NEVER_FIX)

    def add(check, kind, detail=''):
        if kind == 'mechanical' and never_fix:
            kind, detail = 'judgment', detail + ' (mechanical elsewhere; legal/ is never fixed by script)'
        findings.append(Finding(rel, check, kind, detail))

    # --- head ---
    if 'charset' not in metas:
        add('head-charset', 'judgment', 'no charset meta')
    if 'viewport' not in metas:
        add('head-viewport', 'judgment', 'no viewport meta')
    if 'color-scheme' not in metas:
        add('head-color-scheme', 'mechanical', 'add ' + COLOR_SCHEME)
        fixes.append(('color-scheme', None))
    tm = TITLE_RE.search(head)
    title = ' '.join(tm.group(1).split()) if tm else ''
    if not title:
        add('head-title', 'judgment', 'no title')
    elif 'Techne' not in title and 'RegenHub' not in title:
        add('head-title', 'judgment', f'title names neither Techne nor RegenHub: {title[:60]}')
    if 'description' not in metas or not metas['description'].strip():
        add('head-description', 'judgment', 'no description meta; a person writes it')
    canonical = next((l.get('href') for l in rels.get('canonical', [])), None)
    expected_canonical = 'https://techne.coop/' + rel[:-len('index.html')] if rel.endswith('index.html') else 'https://techne.coop/' + rel
    if not canonical:
        add('head-canonical', 'mechanical', f'add canonical {expected_canonical}')
        fixes.append(('canonical', expected_canonical))
        canonical = expected_canonical
    og_missing = [k for k in ('og:type', 'og:url', 'og:title', 'og:description', 'og:site_name', 'og:image') if k not in metas]
    if og_missing:
        if title and metas.get('description'):
            add('head-og', 'mechanical', 'missing ' + ', '.join(og_missing) + '; derived from title, description, canonical')
            fixes.append(('og', {'missing': og_missing, 'title': title, 'description': metas.get('description', ''), 'url': canonical}))
        else:
            add('head-og', 'judgment', 'missing ' + ', '.join(og_missing) + '; no description to derive from')
    fav = [l for l in rels.get('icon', []) if l.get('href') == '/favicon.svg']
    if not fav:
        add('head-favicon', 'mechanical', 'add the two favicon links')
        fixes.append(('favicon', None))
    boot_missing = "localStorage.getItem('techne-mode')" not in head and 'localStorage.getItem("techne-mode")' not in head

    # --- type ---
    faces = set()
    for m in FONT_LINK_RE.finditer(head):
        for fam in re.findall(r'family=([^&]+)', m.group(1)):
            faces.add(fam.split(':')[0].replace('+', ' '))
    extra = faces - ALLOWED_FACES
    if extra:
        add('type-faces', 'judgment', 'loads ' + ', '.join(sorted(extra)))
    css_all = '\n'.join(sm.group(1) for sm in STYLE_BLOCK_RE.finditer(text))
    for sel, prop, val in parse_css(css_all):
        if prop == 'font-family' or prop == 'font':
            for face in re.findall(r"['\"]([^'\"]+)['\"]", val):
                if face not in ALLOWED_FACES and face not in ('SFMono-Regular', 'Georgia', 'Consolas'):
                    add('type-faces', 'judgment', f'{sel} names {face}')
    sizes = Counter(font_sizes(css_all))
    off = sorted(s for s in sizes if s not in scale)
    if off:
        add('type-scale', 'observed', 'not among the commons sizes: ' + ', '.join(f'{s:g}px' for s in off))

    # --- tokens ---
    defined = defaultdict(dict)
    links_commons = 'commons/ui/commons.css' in text
    for sel, prop, val in parse_css(css_all):
        if prop.startswith('--'):
            sc = mode_scope(sel)
            if sc:
                defined[sc][prop] = norm(val)
    has_layer = '--bg' in defined['dark'] and '--bg' in defined['light']
    if not has_layer and not links_commons:
        add('token-layer', 'judgment', 'defines no dark and light palette and does not link commons.css')
    if boot_missing:
        if has_layer:
            add('head-mode-boot', 'mechanical', 'add the mode boot script before the first stylesheet')
            fixes.append(('mode-boot', None))
        else:
            add('head-mode-boot', 'judgment', 'no mode boot, and no light palette for it to select; decide the page\'s mode rule first')
    private = sorted({p for sc in defined for p in defined[sc] if (sc, p) not in tokens and ('root', p) not in tokens})
    if private and has_layer:
        add('token-private', 'observed', ', '.join(private))

    # --- color literals ---
    if not exempt_color:
        for sm in STYLE_BLOCK_RE.finditer(text):
            for sel, prop, val in parse_css(sm.group(1)):
                if prop.startswith('--'):
                    continue
                if HEX_RE.search(val):
                    swap = None
                    for hx in HEX_RE.findall(val):
                        sc = mode_scope(sel) or 'dark'
                        names = [n for (s, n), v in tokens.items() if s in (sc, 'root') and v == hx.lower()]
                        if names:
                            swap = (hx, names[0])
                    if swap:
                        add('color-hex', 'mechanical', f'{sel} {{ {prop}: {val} }} -> var({swap[1]})')
                        fixes.append(('hex', {'sel': sel, 'prop': prop, 'val': val, 'hex': swap[0], 'token': swap[1]}))
                    else:
                        add('color-hex', 'judgment', f'{sel} {{ {prop}: {val} }}')
                if FUNC_COLOR_RE.search(val):
                    add('color-function', 'judgment', f'{sel} {{ {prop}: {val[:60]} }}')
                if prop in ('color', 'background', 'background-color', 'border', 'border-color', 'fill', 'stroke', 'outline') and NAMED_COLOR_RE.search(val):
                    add('color-named', 'judgment', f'{sel} {{ {prop}: {val[:60]} }}')
        for m in STYLE_ATTR_RE.finditer(text):
            if HEX_RE.search(m.group(1)):
                add('color-hex', 'judgment', 'style attribute: ' + m.group(1)[:60])
            if FUNC_COLOR_RE.search(m.group(1)):
                add('color-function', 'judgment', 'style attribute: ' + m.group(1)[:60])

    # --- skeleton ---
    has_shell = 'src="/assets/shell.js"' in text
    has_topbar = 'src="/assets/topbar.js"' in text
    data_public = bool(re.search(r'<script[^>]+src="/assets/shell\.js"[^>]*\sdata-public', text))
    framed = has_shell and not data_public
    body_classes = set(re.findall(r'class="([^"]*)"', text))
    used = [c for c in CONTAINERS if any(re.search(r'(^|\s)' + re.escape(c) + r'(\s|$)', bc) for bc in body_classes)]
    # a framed surface carries the measure on its main rule and
    # measure_audit.py proves it agrees with .wrap-frame (U-20)
    if framed and re.search(r'^(?:main|\.intranet-main)\s*\{[^}]*max-width:\s*70rem', css_all, re.M):
        used.append('main=wrap-frame')
    if not used:
        add('skeleton-container', 'judgment', 'none of wrap, wrap-hud, wrap-frame, or the framed main measure')
    if '<footer' not in text.lower():
        add('skeleton-footer', 'judgment', 'no footer element')
    if has_shell and has_topbar and not data_public:
        add('skeleton-frame', 'judgment', 'loads both frames without data-public')
    elif not has_shell and not has_topbar:
        add('skeleton-frame', 'judgment', 'loads neither frame')

    return findings, fixes, {'container': ','.join(used) or '-', 'faces': ','.join(sorted(faces)) or '-',
                             'frame': 'shell+topbar (public)' if data_public and has_topbar else 'shell' if has_shell else 'topbar' if has_topbar else '-',
                             'layer': 'inline' if has_layer else 'commons.css' if links_commons else '-'}


# ---------- the mechanical fixes ----------

def apply_fixes(rel, text, fixes):
    if rel.startswith(NEVER_FIX) or rel in VERBATIM:
        return text, 0
    applied = 0
    head_m = HEAD_RE.search(text)
    if not head_m:
        return text, 0
    head = head_m.group(1)
    for kind, payload in fixes:
        if kind == 'color-scheme':
            vm = re.search(r'<meta name="viewport"[^>]*>', head)
            anchor = vm.group(0) if vm else None
            if anchor:
                head = head.replace(anchor, anchor + '\n' + COLOR_SCHEME, 1); applied += 1
        elif kind == 'canonical':
            dm = re.search(r'<meta name="description"[^>]*>', head)
            tm = TITLE_RE.search(head)
            anchor = dm.group(0) if dm else tm.group(0) if tm else None
            if anchor:
                head = head.replace(anchor, anchor + f'\n<link rel="canonical" href="{payload}">', 1); applied += 1
        elif kind == 'og':
            og_title = payload['title'].replace('&middot;', '\u00b7').replace('&amp;', '&')
            tag = {
                'og:type': 'website', 'og:url': payload['url'], 'og:title': og_title,
                'og:description': payload['description'], 'og:site_name': 'Techne', 'og:image': OG_DEFAULT_IMAGE,
            }
            block = '\n'.join(f'<meta property="{k}" content="{tag[k]}">' for k in payload['missing'])
            cm = re.search(r'<link rel="canonical"[^>]*>', head)
            anchor = cm.group(0) if cm else TITLE_RE.search(head).group(0)
            head = head.replace(anchor, anchor + '\n' + block, 1); applied += 1
        elif kind == 'favicon':
            ogs = list(re.finditer(r'<meta property="og:[^>]*>', head))
            cm = re.search(r'<link rel="canonical"[^>]*>', head)
            anchor = ogs[-1].group(0) if ogs else cm.group(0) if cm else TITLE_RE.search(head).group(0)
            head = head.replace(anchor, anchor + '\n' + FAVICON, 1); applied += 1
        elif kind == 'mode-boot':
            first = re.search(r'<link[^>]*stylesheet[^>]*>|<style', head)
            if first:
                head = head[:first.start()] + MODE_BOOT + '\n' + head[first.start():]; applied += 1
        elif kind == 'hex':
            old = f"{payload['prop']}:{payload['val']}"
            # the declaration as written on the page may carry spaces; match loosely
            pat = re.compile(re.escape(payload['prop']) + r'\s*:\s*' + re.escape(payload['val']).replace(re.escape(payload['hex']), '(' + re.escape(payload['hex']) + ')'))
            new_text, n = pat.subn(lambda m: m.group(0).replace(payload['hex'], f"var({payload['token']})"), text, count=1)
            if n:
                text = new_text; applied += 1
            continue
    text = text[:head_m.start(1)] + head + text[head_m.end(1):]
    return text, applied


# ---------- report ----------

def commit():
    return subprocess.run(['git', '-C', str(REPO_ROOT), 'rev-parse', '--short', 'HEAD'],
                          capture_output=True, text=True).stdout.strip()


def render_report(pages, findings, facts):
    by_check = defaultdict(list)
    for f in findings:
        by_check[f.check].append(f)
    lines = []
    lines.append('# Design audit')
    lines.append('')
    lines.append(f'Written by scripts/design_audit.py at commit {commit()} over {len(pages)} tracked pages. '
                 'Regenerate rather than edit: `python3 scripts/design_audit.py --report design-system/AUDIT.md`.')
    lines.append('')
    lines.append('Every check names its source in the design system or in commons.css. A mechanical finding is one '
                 '`--fix` applies; a judgment finding waits on a person. legal/ is reported and never fixed; '
                 'design-system/ is exempt from the color checks only, as in token_audit.py.')
    lines.append('')
    lines.append('## By check')
    lines.append('')
    lines.append('| check | rule | source | pages | mechanical | judgment | observed |')
    lines.append('|---|---|---|---:|---:|---:|---:|')
    for cid, (title, source) in CHECKS.items():
        fs = by_check.get(cid, [])
        pg = len({f.page for f in fs})
        mech = sum(1 for f in fs if f.kind == 'mechanical')
        jud = sum(1 for f in fs if f.kind == 'judgment')
        obs = sum(1 for f in fs if f.kind == 'observed')
        lines.append(f'| {cid} | {title} | {source} | {pg} | {mech} | {jud} | {obs} |')
    lines.append('')
    rule_findings = [f for f in findings if f.kind != 'observed']
    lines.append(f'Rule findings: {len(rule_findings)} on {len({f.page for f in rule_findings})} of {len(pages)} pages; '
                 f'{sum(1 for f in findings if f.kind == "mechanical")} mechanical, '
                 f'{sum(1 for f in findings if f.kind == "judgment")} judgment. '
                 f'Observations, not counted: {sum(1 for f in findings if f.kind == "observed")}.')
    lines.append('')
    lines.append('## By page')
    lines.append('')
    lines.append('| page | frame | layer | container | faces | findings |')
    lines.append('|---|---|---|---|---|---|')
    per_page = defaultdict(list)
    for f in findings:
        per_page[f.page].append(f)
    for p in pages:
        fs = per_page.get(p, [])
        fx = facts[p]
        summary = ', '.join(f'{c}({n})' for c, n in sorted(Counter(f.check for f in fs).items())) or 'clean'
        lines.append(f'| {p} | {fx["frame"]} | {fx["layer"]} | {fx["container"]} | {fx["faces"]} | {summary} |')
    lines.append('')
    lines.append('## Detail')
    lines.append('')
    for cid, (title, source) in CHECKS.items():
        fs = by_check.get(cid, [])
        if not fs:
            continue
        lines.append(f'### {cid}: {title}')
        lines.append('')
        lines.append(f'Source: {source}.')
        lines.append('')
        for f in fs:
            d = f.detail.replace('|', '\\|')
            lines.append(f'- `{f.page}` ({f.kind}): {d}')
        lines.append('')
    return '\n'.join(lines) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--report', metavar='PATH', help='write the markdown report here')
    ap.add_argument('--fix', action='store_true', help='apply the mechanical fixes in place')
    ap.add_argument('--json', action='store_true', help='print findings as JSON')
    ap.add_argument('--quiet', action='store_true')
    args = ap.parse_args()

    tokens, scale = commons_layer()
    pages = tracked_pages()
    findings, facts, all_fixes = [], {}, {}
    for rel in pages:
        text = (REPO_ROOT / rel).read_text()
        fs, fixes, fx = audit_page(rel, text, tokens, scale)
        findings.extend(fs)
        facts[rel] = fx
        all_fixes[rel] = fixes

    if args.fix:
        touched = 0
        for rel, fixes in all_fixes.items():
            if not fixes:
                continue
            path = REPO_ROOT / rel
            text = path.read_text()
            new, n = apply_fixes(rel, text, fixes)
            if n and new != text:
                path.write_text(new)
                touched += 1
                print(f'fixed: {rel} ({n} change(s))')
        print(f'design-audit: fixed {touched} page(s); re-run to see what remains')
        return 0

    if args.json:
        print(json.dumps([f.row() for f in findings], indent=1))
    elif not args.quiet:
        for f in findings:
            print(f'{f.page}: {f.check} [{f.kind}]: {f.detail}')
    if args.report:
        out = REPO_ROOT / args.report
        out.write_text(render_report(pages, findings, facts))
        print(f'wrote {out}')
    mech = sum(1 for f in findings if f.kind == 'mechanical')
    jud = sum(1 for f in findings if f.kind == 'judgment')
    obs = sum(1 for f in findings if f.kind == 'observed')
    rule = [f for f in findings if f.kind != 'observed']
    print(f'design-audit: {len(rule)} finding(s) on {len({f.page for f in rule})} of {len(pages)} pages '
          f'({mech} mechanical, {jud} judgment); {obs} observation(s) not counted; '
          f'commons sizes {", ".join(f"{s:g}" for s in scale)}')
    return 1 if rule else 0


if __name__ == '__main__':
    sys.exit(main())
