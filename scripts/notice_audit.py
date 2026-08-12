#!/usr/bin/env python3
"""Formation notice audit -- BP v2, VS v2 section 9.

The site has no build step and no shared public stylesheet, so the
formation strip is a verbatim copy on every public page it covers. Verbatim
copies drift: U-20 found four different widths where one measure was meant,
and this audit exists so the same thing cannot happen to a legal disclosure.

Two checks:

1. Coverage. Every page named in COVERED carries the strip.
2. Sameness. The strip's prose is byte-identical on every page that carries
   it. Only the surrounding CSS may differ, because the estate carries two
   token families and a copy must use the names its own page defines.

The long form of the notice lives at legal/index.html#formation and is the
copy that governs when a page disagrees with it; this audit checks that it
is present but does not police its wording, which is the steward's.

Exit non-zero on any finding. Deliberately not wired into CI: a new gate in
launch week is a hazard, and the estate made that call once already for the
almanac audit (X-17). Run it by hand after touching any covered page.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

COVERED = [
    "index.html",
    "participation/index.html",
    "legal/index.html",
    "legal/bylaws/index.html",
    "legal/bylaws-analysis/index.html",
    "legal/bylaws-analysis/changes/index.html",
    "legal/community-supporter/index.html",
    "legal/corrections/index.html",
    "legal/counsel-memo/index.html",
    "legal/maturity-model/index.html",
    "legal/maturity-model/specification/index.html",
    "legal/membership-agreement/index.html",
    "legal/membership-agreement-analysis/index.html",
    "legal/membership-agreement-analysis/changes/index.html",
    "legal/participation/index.html",
    "legal/summary-of-changes/index.html",
]

LONG_FORM = "legal/index.html"

STRIP_RE = re.compile(
    r'<aside class="formation-strip"[^>]*>(.*?)</aside>', re.S
)


def main():
    findings = []
    seen = {}

    for rel in COVERED:
        path = REPO_ROOT / rel
        if not path.exists():
            findings.append(f"{rel}: covered page does not exist")
            continue
        text = path.read_text()
        match = STRIP_RE.search(text)
        if not match:
            findings.append(f"{rel}: carries no formation strip")
            continue
        seen[rel] = match.group(1).strip()

    if seen:
        # The first page in COVERED order is the reference copy.
        ref_rel = next(r for r in COVERED if r in seen)
        ref = seen[ref_rel]
        for rel, body in seen.items():
            if body != ref:
                findings.append(
                    f"{rel}: formation strip differs from {ref_rel}; "
                    f"the prose is one text, copied, not edited per page"
                )

    long_form = REPO_ROOT / LONG_FORM
    if long_form.exists():
        text = long_form.read_text()
        if 'id="formation"' not in text:
            findings.append(
                f"{LONG_FORM}: the long-form notice anchor id=formation is "
                f"missing; every strip links to it"
            )
    else:
        findings.append(f"{LONG_FORM}: missing")

    for f in findings:
        print(f"notice-audit: {f}")
    print(f"notice-audit: {len(findings)} finding(s) over {len(COVERED)} pages")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
