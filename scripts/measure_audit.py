#!/usr/bin/env python3
"""Frame measure audit (U-20) -- UI v1, VS v1.

The nine surfaces the shell frames must all carry the same content
measure. They did not: before U-20 they carried 720, 1040, 1080, 1120,
and one page with no cap at all, because each hand-rolled its own
container rule and the token layer had no container to offer them.

UI v1 section 1 says drift between any copy and the document is a
defect. The layer now defines .wrap-frame in commons/ui/commons.css and
the pages inline it verbatim, because the frame must be correct at first
paint and the shell's stylesheet is not page-scoped. Verbatim copies
drift silently, which is exactly how the four widths appeared, so this
check proves they still agree.

Two checks:

1. Every framed surface declares the container, and its declarations
   match .wrap-frame in commons.css property for property.
2. No framed surface reintroduces a fixed pixel cap on that container,
   which is how the estate lost the measure the first time.

Exit non-zero on any finding. Scope is named per VS v1 section 9: only
the surfaces the shell frames are audited, identified by their own
markup rather than a hand-kept list, so a new framed surface is covered
the day it ships and cannot be forgotten.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
COMMONS = REPO_ROOT / 'commons/ui/commons.css'

# The container carries these; a page may add nothing and omit nothing.
CHECKED = ('width', 'max-width', 'margin-inline', 'padding-block', 'padding-inline')

# A page is framed when it loads the shell without declaring itself public.
# data-public pages keep their own layout signed out and are not framed.
SHELL = re.compile(r'<script src="/assets/shell\.js"([^>]*)>')


def decls(block):
    out = {}
    for decl in block.split(';'):
        if ':' not in decl:
            continue
        prop, _, val = decl.partition(':')
        out[prop.strip()] = ' '.join(val.split())
    return out


def canonical():
    css = COMMONS.read_text()
    m = re.search(r'\.wrap-frame\s*\{([^}]*)\}', css)
    if not m:
        return None
    return {k: v for k, v in decls(m.group(1)).items() if k in CHECKED}


def framed_pages():
    for page in sorted(REPO_ROOT.rglob('*.html')):
        text = page.read_text()
        m = SHELL.search(text)
        if m and 'data-public' not in m.group(1):
            yield page, text


def audit():
    findings = []
    canon = canonical()
    if not canon:
        return ['commons/ui/commons.css: .wrap-frame is not defined; the layer '
                'must carry the measure the pages copy']
    missing = [p for p in CHECKED if p not in canon]
    if missing:
        findings.append(f"commons.css: .wrap-frame omits {', '.join(missing)}")

    seen = 0
    for page, text in framed_pages():
        rel = str(page.relative_to(REPO_ROOT))
        # the page's own top-level container rule: main, or the dashboard's
        m = re.search(r'^(?:main|\.intranet-main)\s*\{([^}]*)\}', text, re.M)
        if not m:
            findings.append(f"{rel}: framed by the shell but declares no content measure")
            continue
        seen += 1
        mine = decls(m.group(1))
        for prop, want in canon.items():
            got = mine.get(prop)
            if got is None:
                findings.append(f"{rel}: content measure omits {prop} (commons.css: {want})")
            elif got != want:
                findings.append(f"{rel}: content measure drift in {prop}: {got} (commons.css: {want})")
        cap = mine.get('max-width', '')
        if re.search(r'\d+px', cap):
            findings.append(f"{rel}: content measure pinned to a pixel cap ({cap}); "
                            f"the measure is fluid by decision U-20")

    if seen == 0:
        findings.append('no framed surfaces found; the audit is not exercising anything')
    return findings


if __name__ == '__main__':
    found = audit()
    for f in found:
        print(f)
    print(f"measure-audit: {len(found)} finding(s)")
    sys.exit(1 if found else 0)
