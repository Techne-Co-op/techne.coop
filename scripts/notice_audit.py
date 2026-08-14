#!/usr/bin/env python3
"""Formation notice audit -- BP v2, VS v2 section 9.

The site has no build step and no shared public stylesheet, so the
formation strip is a verbatim copy on every public page it covers. Verbatim
copies drift: U-20 found four different widths where one measure was meant,
and this audit exists so the same thing cannot happen to a legal disclosure.

The notice is a short footer line, one form only. The steward directed it out
of the top banner on 2026-08-12 for the public pages, and on 2026-08-13 for
the pages under legal/ as well: P-11 had kept the banner there on the agent's
own reasoning, and the steward overturned it. One notice, one place.

Coverage is now every page in the estate, discovered rather than listed. The
hand-maintained list was the defect: it held seventeen pages out of fifty-five,
so the notice that "is right wherever a page disagrees with it" was absent from
every page under commons/, intranet/, accounting/, encyclopedia/, commonplace/
and design-system/ -- including /commons/join/, which the front page links to
twice and which is where a stranger types their name. A list a person maintains
by hand drifts at the rate it costs nothing; discovery cannot.

Three checks:

1. Coverage. Every HTML page in the estate carries the footer line. Nothing is
   excluded: this site is served whole and publicly, so any page is a page a
   reader can land on first.
2. Sameness. Its prose is byte-identical everywhere. Only the surrounding CSS
   may differ, because the estate carries two token families and a copy must
   use the names its own page defines.
3. No survivals. No page anywhere carries the retired top strip. A banner that
   creeps back onto one page is exactly the drift this audit exists to catch,
   and it would be invisible in a diff of twenty files.

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


def discover():
    """Every HTML page in the estate, in a stable order.

    Worktrees under .wt/ are checkouts of other branches, not pages of this
    one, and are skipped. Everything else counts.
    """
    return sorted(
        path.relative_to(REPO_ROOT).as_posix()
        for path in REPO_ROOT.rglob("*.html")
        if ".wt/" not in path.relative_to(REPO_ROOT).as_posix()
    )


COVERED = discover()

LONG_FORM = "legal/index.html"

FOOT_RE = re.compile(
    r'<div class="formation-foot"[^>]*>(.*?)</div>', re.S
)


def check(findings, covered, pattern, label):
    """Coverage and sameness for one form of the notice."""
    seen = {}
    for rel in covered:
        path = REPO_ROOT / rel
        if not path.exists():
            findings.append(f"{rel}: covered page does not exist")
            continue
        match = pattern.search(path.read_text())
        if not match:
            findings.append(f"{rel}: carries no formation {label}")
            continue
        seen[rel] = match.group(1).strip()

    if seen:
        ref_rel = next(r for r in covered if r in seen)
        ref = seen[ref_rel]
        for rel, body in seen.items():
            if body != ref:
                findings.append(
                    f"{rel}: formation {label} differs from {ref_rel}; "
                    f"the prose is one text, copied, not edited per page"
                )
    return len(seen)


def main():
    findings = []
    n = check(findings, COVERED, FOOT_RE, "footer line")

    # The retired banner must not survive anywhere, covered or not.
    for rel in COVERED:
        if "formation-strip" in (REPO_ROOT / rel).read_text():
            findings.append(
                f"{rel}: carries the retired formation strip; the notice is a "
                f"footer line, one form only"
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
    print(f"notice-audit: {len(findings)} finding(s) over {n} pages")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
