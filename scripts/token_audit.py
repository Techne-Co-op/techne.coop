#!/usr/bin/env python3
"""Token audit (X-06) -- UI v1, VS v1.

Two checks over every HTML page and commons.css:

1. Hex discipline: a hex color literal may appear only where a custom
   property is defined (--name: #...). Everywhere else, page CSS must
   reference the token layer with var(). Acceptance: no hard-coded hex
   values in page CSS (X-06).

2. Drift: a page that inlines the token layer must agree with
   commons.css. A custom property whose name matches a commons.css
   token in the same mode scope but carries a different value is drift
   (UI v1 section 1: drift between any copy and the document is a
   defect; detection assigned to X-06 by the SUB-02 decision record).

   Scope: every shared token, typefaces included. The type question on
   the X-06 escalation card was decided 2026-07-20 (adopt the deployed
   practice: Libre Baskerville and IBM Plex Mono, two faces), so
   font-stack drift is a defect like any other.

Exit non-zero on any finding. Exemptions are named per VS v1 section 9:

- design-system/ is the palette constitution: hex values are its subject
  matter, the source the tokens distill from. Auditing it against itself
  would be circular.
- legal/ carries the formation-era record: ratified instruments and
  commentary migrated verbatim with their own self-contained styling,
  consistent with the em-dash exemption in style-lint. The record is
  not reformatted to match a design system adopted after its creation.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXEMPT = ('design-system/', 'legal/')
HEX_RE = re.compile(r'#[0-9a-fA-F]{3,8}\b')
STYLE_BLOCK_RE = re.compile(r'<style[^>]*>(.*?)</style>', re.DOTALL | re.IGNORECASE)
STYLE_ATTR_RE = re.compile(r'style="([^"]*)"')

def norm(value):
    """Compare token values ignoring case, whitespace, and quote style."""
    return value.lower().replace(' ', '').replace('"', '').replace("'", '')

def mode_scope(selector):
    s = selector.lower()
    if 'data-mode="dark"' in s or "data-mode='dark'" in s: return 'dark'
    if 'data-mode="light"' in s or "data-mode='light'" in s: return 'light'
    if ':root' in s: return 'root'
    return None

def parse_css(css):
    """Yield (selector, property, value) with comments stripped."""
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
    for block in re.finditer(r'([^{}]+)\{([^{}]*)\}', css):
        selector = block.group(1).strip()
        for decl in block.group(2).split(';'):
            if ':' not in decl: continue
            prop, _, value = decl.partition(':')
            yield selector, prop.strip(), value.strip()

def audit():
    findings = []
    tokens = {}          # (scope, name) -> value from commons.css
    ccss = REPO_ROOT / 'commons/ui/commons.css'
    if ccss.exists():
        for sel, prop, val in parse_css(ccss.read_text()):
            if prop.startswith('--'):
                sc = mode_scope(sel)
                if sc: tokens[(sc, prop)] = norm(val)
            elif HEX_RE.search(val):
                findings.append(f"commons.css: hex outside a token definition: {prop}: {val}")

    for page in sorted(REPO_ROOT.rglob('*.html')):
        rel = str(page.relative_to(REPO_ROOT))
        if rel.startswith(EXEMPT):
            continue
        text = page.read_text()
        for m in STYLE_ATTR_RE.finditer(text):
            if HEX_RE.search(m.group(1)):
                findings.append(f"{rel}: hex in a style attribute: {m.group(1)[:60]}")
        for sm in STYLE_BLOCK_RE.finditer(text):
            for sel, prop, val in parse_css(sm.group(1)):
                if prop.startswith('--'):
                    sc = mode_scope(sel)
                    if sc:
                        canon = tokens.get((sc, prop))
                        mine = norm(val)
                        if canon is not None and mine != canon:
                            findings.append(f"{rel}: token drift in {sc}: {prop}: {val} (commons.css: {tokens[(sc, prop)]})")
                elif HEX_RE.search(val):
                    findings.append(f"{rel}: hex outside a token definition: {sel} {{ {prop}: {val} }}")
    return findings

if __name__ == '__main__':
    findings = audit()
    for f in findings: print(f)
    print(f"token-audit: {len(findings)} finding(s)")
    sys.exit(1 if findings else 0)
