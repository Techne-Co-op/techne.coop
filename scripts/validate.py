#!/usr/bin/env python3
"""
validate.py · SUB-01 emission · BP v1
Validates almanac-ledger.yaml: schema compliance, dependency acyclicity,
gating consistency. Exits non-zero on any violation.
Authored-by: build-agent / SUB-01
"""

import sys
import re
import json
from pathlib import Path

# Use PyYAML if available; fall back to a minimal safe loader for CI environments
# that may not have it pre-installed. The fallback covers the almanac-ledger.yaml format.
try:
    import yaml as _yaml
    def _load_yaml(text):
        return _yaml.safe_load(text)
except ImportError:
    # Minimal YAML loader: handles the subset used in almanac-ledger.yaml.
    # Delegates to a robust third-party parser if one is importable.
    try:
        import tomllib  # Python 3.11+; not YAML but confirms stdlib is modern
        del tomllib
    except ImportError:
        pass

    def _load_yaml(text):
        """
        Very minimal YAML parser sufficient for almanac-ledger.yaml.
        Supports: top-level mappings, list items with mappings, scalar values,
        multi-line folded scalars (>), block scalars (|), inline lists.
        Not a general YAML parser -- only suitable for the ledger format.
        Falls back to subprocess if pyyaml is on PATH.
        """
        import subprocess, tempfile, os
        # Try: python3 -c "import yaml" via subprocess (e.g. system python)
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                f.write(text)
                fname = f.name
            result = subprocess.run(
                ['python3', '-c',
                 f'import yaml, json, sys; d=yaml.safe_load(open("{fname}")); print(json.dumps(d))'],
                capture_output=True, text=True, timeout=10
            )
            os.unlink(fname)
            if result.returncode == 0:
                return json.loads(result.stdout)
        except Exception:
            pass
        raise ImportError(
            "PyYAML is required: pip install pyyaml\n"
            "In CI, add: pip install pyyaml before running validate.py"
        )

REPO_ROOT = Path(__file__).parent.parent
LEDGER_PATH = REPO_ROOT / "almanac-ledger.yaml"

VALID_STATUSES = {"drafted", "anticipated", "filed"}
REQUIRED_FIELDS = {"address", "title", "intent", "status", "deliverable", "acceptance"}
PROOF_ADDRESSES = {"G0", "G-B", "G-G", "G-F", "G-S", "G-T", "G-R", "G-A", "G-L"}

errors = []
warnings = []


def html_pages():
    """The repository's HTML pages, as tracked paths.

    X-04 enumerates by walking the tree so exhaustiveness holds by
    construction, and a bare walk was right while the tree held only the
    repository. It stopped being right once local work parked sibling
    checkouts inside it: git worktrees under .wt/ put several hundred
    copies of every page on the walk, and a manifest regenerated in that
    tree claims pages the repository does not have. Asking git for the
    tracked pages keeps the guarantee, since a page added by a pull
    request is committed before CI reads it, and makes the manifest a
    claim about the repository rather than about one working directory.

    Falls back to the walk, minus dot-directories, where git is not
    available to answer.
    """
    import subprocess
    try:
        out = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "ls-files", "-z", "*.html"],
            capture_output=True, check=True,
        ).stdout.decode()
        tracked = sorted(p for p in out.split("\0") if p)
        if tracked:
            return tracked
        warn("git reported no tracked HTML pages; falling back to the tree walk")
    except (OSError, subprocess.CalledProcessError):
        warn("git could not enumerate tracked pages; falling back to the tree walk")
    return sorted(
        str(p.relative_to(REPO_ROOT))
        for p in REPO_ROOT.rglob("*.html")
        if not any(part.startswith(".") for part in p.relative_to(REPO_ROOT).parts)
    )


def err(msg):
    errors.append(msg)
    print(f"ERROR: {msg}", file=sys.stderr)


def warn(msg):
    warnings.append(msg)
    print(f"WARN:  {msg}")


def load_ledger():
    if not LEDGER_PATH.exists():
        err(f"ledger not found: {LEDGER_PATH}")
        return None
    with open(LEDGER_PATH) as f:
        return _load_yaml(f.read())


def collect_pieces(ledger):
    pieces = {}
    for section_key, items in ledger.items():
        if not isinstance(items, list):
            continue
        for item in items:
            addr = item.get("address")
            if not addr:
                err(f"piece in section '{section_key}' missing address")
                continue
            if addr in pieces:
                err(f"duplicate address: {addr}")
            pieces[addr] = item
    return pieces


def check_schema(pieces):
    """Every piece has required fields; status is valid or open."""
    for addr, p in pieces.items():
        for field in REQUIRED_FIELDS:
            if field not in p:
                err(f"{addr}: missing required field '{field}'")
        status = p.get("status", "")
        if not status:
            err(f"{addr}: empty status")
        elif not (
            status in VALID_STATUSES
            or status.startswith("open ·")
            or status == "open"
        ):
            err(f"{addr}: invalid status '{status}' (expected: drafted | anticipated | filed | open · <blocker>)")


def check_cites(pieces):
    """Every cite references a known address."""
    all_addresses = set(pieces.keys())
    for addr, p in pieces.items():
        cites = p.get("cites", []) or []
        for cited in cites:
            if cited not in all_addresses:
                err(f"{addr}: cites unknown address '{cited}'")


def check_acyclicity(pieces):
    """No circular dependencies in cites."""
    # Build adjacency: address -> set of cites
    adj = {addr: set(p.get("cites", []) or []) for addr, p in pieces.items()}

    def dfs(node, visited, stack):
        visited.add(node)
        stack.add(node)
        for neighbor in adj.get(node, set()):
            if neighbor not in adj:
                continue  # unknown cite already caught by check_cites
            if neighbor not in visited:
                if dfs(neighbor, visited, stack):
                    return True
            elif neighbor in stack:
                err(f"cycle detected involving: {node} -> {neighbor}")
                return True
        stack.discard(node)
        return False

    visited = set()
    for addr in adj:
        if addr not in visited:
            dfs(addr, visited, set())


def check_gating(pieces):
    """Proof addresses exist; blocked pieces name their blocker."""
    for addr, p in pieces.items():
        status = p.get("status", "")
        if status.startswith("open ·"):
            blocker = status[len("open ·"):].strip()
            if not blocker:
                err(f"{addr}: open status must name a blocker: 'open · <blocker>'")
        ready = p.get("ready_when", "") or ""
        # Check proof references in ready_when
        for proof in PROOF_ADDRESSES:
            if proof in ready and proof not in pieces:
                err(f"{addr}: ready_when references undefined proof '{proof}'")


def check_done_requires_verified(pieces):
    """A piece with status 'filed' must not depend on an un-filed upstream."""
    for addr, p in pieces.items():
        if p.get("status") == "filed":
            cites = p.get("cites", []) or []
            for cited in cites:
                upstream = pieces.get(cited, {})
                if upstream.get("status") not in ("filed", "drafted"):
                    warn(
                        f"{addr}: filed but cites '{cited}' which is '{upstream.get('status','?')}'"
                    )


def check_decision_coherence(pieces):
    """X-07: every stop card on an opened piece carries a recorded decision.

    A stop card is a piece's `escalation` field, in the standing-in /
    found / the-question / a-default shape of BP v1 §2 (see SUB-03 for the
    convention). It is resolved when a decision is recorded: a `decision` key
    inside the escalation mapping, or a sibling `decision` field on the piece.
    A piece that has opened (status begins 'open') must not carry an unresolved
    stop card: the decision is recorded before the blocked piece opens.
    """
    for addr, p in pieces.items():
        esc = p.get("escalation")
        if not esc:
            continue
        resolved = False
        if isinstance(esc, dict):
            resolved = bool(str(esc.get("decision", "") or "").strip())
        if not resolved:
            resolved = bool(str(p.get("decision", "") or "").strip())
        if p.get("status", "").startswith("open") and not resolved:
            err(
                f"{addr}: opened piece carries an unresolved stop card; "
                f"record its decision before it opens (BP v1 §2, X-07)"
            )


def generate_ledger_state(pieces):
    """Write the Almanac's headline counts from the ledger.

    The Almanac is authored prose, but its headline numbers are a claim
    about the ledger, and a hand-kept claim drifts: it read 40 items when
    the ledger held 59. Only the marked block is generated; everything
    else on the page stays the author's. X-10.
    """
    page = REPO_ROOT / "commons/build/index.html"
    if not page.exists():
        return
    drafted = sum(1 for p in pieces.values() if p.get("status") == "drafted")
    anticipated = sum(1 for p in pieces.values() if p.get("status") == "anticipated")
    open_n = sum(1 for p in pieces.values() if str(p.get("status", "")).startswith("open"))
    verified = sum(1 for p in pieces.values() if "verified" in str(p.get("status", "")))
    block = (
        "<!-- generated:ledger-state -- written by scripts/validate.py; do not edit by hand -->\n"
        f'    <span class="stat-chip drafted"><span class="n">{drafted}</span>&thinsp;drafted</span>\n'
        f'    <span class="stat-chip anticipated"><span class="n">{anticipated}</span>&thinsp;anticipated</span>\n'
        f'    <span class="stat-chip open"><span class="n">{open_n}</span>&thinsp;open</span>\n'
        f'    <span class="stat-chip verified"><span class="n">{verified}</span>&thinsp;verified</span>\n'
        "<!-- /generated:ledger-state -->"
    )
    text = page.read_text()
    new, n = re.subn(
        r"<!-- generated:ledger-state.*?/generated:ledger-state -->",
        lambda _m: block, text, count=1, flags=re.S)
    if n != 1:
        warn("commons/build/index.html: no generated:ledger-state block; counts not refreshed")
        return
    if new != text:
        page.write_text(new)
        print(f"wrote {page}")


def generate_status_md(pieces):
    """Write STATUS.md summarizing ledger state."""
    status_path = REPO_ROOT / "STATUS.md"
    drafted = [a for a, p in pieces.items() if p.get("status") == "drafted"]
    anticipated = [a for a, p in pieces.items() if p.get("status") == "anticipated"]
    open_pieces = [a for a, p in pieces.items() if p.get("status", "").startswith("open")]
    filed = [a for a, p in pieces.items() if p.get("status") == "filed"]

    lines = [
        "<!-- STATUS.md generated by scripts/validate.py -- do not edit by hand -->",
        "# STATUS.md · Common Record Series · ALM v2",
        "",
        f"Generated from almanac-ledger.yaml. {len(pieces)} items total.",
        "",
        f"| status | count |",
        f"|--------|-------|",
        f"| drafted | {len(drafted)} |",
        f"| anticipated | {len(anticipated)} |",
        f"| open | {len(open_pieces)} |",
        f"| filed | {len(filed)} |",
        "",
        "## Drafted",
        "",
    ]
    for a in sorted(drafted):
        p = pieces[a]
        lines.append(f"- **{a}** {p.get('title','')} -- {p.get('intent','')[:80]}")

    lines += ["", "## Open", ""]
    for a in sorted(open_pieces):
        p = pieces[a]
        lines.append(f"- **{a}** {p.get('status','')} -- {p.get('title','')}")

    lines += ["", "## Anticipated", ""]
    for a in sorted(anticipated):
        p = pieces[a]
        lines.append(f"- **{a}** {p.get('title','')}")

    if filed:
        lines += ["", "## Filed", ""]
        for a in sorted(filed):
            p = pieces[a]
            lines.append(f"- **{a}** {p.get('title','')}")

    lines += ["", "---", "", "*RegenHub, LCA -- Boulder, Colorado -- July 2026*", ""]

    status_path.write_text("\n".join(lines))
    print(f"wrote {status_path}")


def generate_index_json(pieces):
    """Write index.json, the document manifest (X-04): every HTML page in the
    repository, enumerated by walking the tree, so exhaustiveness holds by
    construction. The committed manifest must match the tree: a stale
    index.json is an error, not a silent regeneration, so CI catches a page
    added without refreshing the manifest."""
    import json
    index_path = REPO_ROOT / "index.json"

    html_files = html_pages()
    index = {
        "generated": "scripts/validate.py",
        "series": "ALM v2",
        "ledger_items": len(pieces),
        "pages": html_files,
    }
    content = json.dumps(index, indent=2)

    stale = not index_path.exists() or index_path.read_text() != content
    index_path.write_text(content)
    print(f"wrote {index_path} ({len(html_files)} pages)")
    if stale:
        err("index.json was stale or missing; refreshed. Commit the regenerated manifest (X-04).")


def check_lexicon_schema(pieces):
    """The lexicon rides in two forms and they must agree (L-09): the prose
    page at commons/build/lexicon/index.html governs, and the machine-readable
    register at commons/build/lexicon/lexicon.json distills it for any system
    that needs the vocabulary as data rather than prose. A schema artifact
    that drifts from its page is worse than no artifact: it exports a
    vocabulary the register no longer speaks. So the check is set equality,
    both directions: every span.k term on the page appears in the JSON, and
    every JSON term appears on the page. The JSON also carries a version and
    a source path; a missing field is an error, not a warning."""
    import re as _re
    page_path = REPO_ROOT / "commons" / "build" / "lexicon" / "index.html"
    json_path = REPO_ROOT / "commons" / "build" / "lexicon" / "lexicon.json"
    if not json_path.exists():
        err("commons/build/lexicon/lexicon.json: missing; the lexicon's machine-readable register (L-09)")
        return
    try:
        doc = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as e:
        err(f"commons/build/lexicon/lexicon.json: unparseable ({e})")
        return
    for field in ("artifact", "version", "source", "terms"):
        if field not in doc:
            err(f"lexicon.json: missing field '{field}' (L-09)")
    if doc.get("source") != "commons/build/lexicon/index.html":
        err("lexicon.json: source must name the governing page (L-09)")
    def _norm(t):
        t = _re.sub(r"<[^>]+>", "", t)
        return t.replace("&middot;", "·").replace("&sect;", "§").strip()
    html = page_path.read_text(encoding="utf-8")
    page_terms = set()
    for m in _re.finditer(r'<div class="condition"><span class="k">(.*?)</span>', html, _re.S):
        page_terms.add(_norm(m.group(1)))
    json_terms = set()
    for t in doc.get("terms", []):
        if not isinstance(t, dict) or "term" not in t or "gloss" not in t or "section" not in t:
            err("lexicon.json: each term carries term, gloss, section (L-09)")
            continue
        json_terms.add(t["term"])
    for missing in sorted(page_terms - json_terms):
        err(f"lexicon.json: page defines '{missing}' but the artifact omits it (L-09)")
    for extra in sorted(json_terms - page_terms):
        err(f"lexicon.json: artifact carries '{extra}' but the page does not define it (L-09)")


def check_one_navigation(pieces):
    """One primary navigation per page (U-13): every HTML page loads exactly
    one of the two shared frames, /assets/shell.js (signed-in) or
    /assets/topbar.js (public), and no page carries an inline topbar of its
    own. Drift between hand-rolled topbars is what this check retires.

    One page may carry both (U-15): a record page the members' map points
    at declares shell.js data-public, so it renders exactly as authored to
    the public and gains the members' frame to a member. Only one bar is
    ever on screen; shell.js retires the public topbar when it takes over.

    Verbatim source artifacts are exempt by exact path. A document supplied
    from outside and committed so a page can be checked against its source is
    held byte for byte; adding the house frame to one would edit the evidence.
    The same reasoning already exempts legal/ from the em dash rule and the
    counsel memo from the vocabulary quarantine: an instrument carried
    verbatim is not an authored page of this site. Each exemption is named
    here, one path at a time, and nothing is exempt by pattern."""
    import re as _re
    verbatim = {
        # governance-model-v4, supplied by the steward on 2026-08-17 and
        # committed unaltered so GOV can be read against its own source.
        "commons/governance/model-v4/governance-model-v4.html",
    }
    shell_re = _re.compile(r'<script[^>]+src="/assets/shell\.js"')
    public_re = _re.compile(r'<script[^>]+src="/assets/shell\.js"[^>]*\sdata-public')
    topbar_re = _re.compile(r'<script[^>]+src="/assets/topbar\.js"')
    inline_re = _re.compile(r'class="topbar"|class="nav-links"|class="top-nav"')
    for rel in html_pages():
        if rel in verbatim:
            continue
        p = REPO_ROOT / rel
        text = p.read_text(encoding="utf-8", errors="replace")
        has_shell = bool(shell_re.search(text))
        has_topbar = bool(topbar_re.search(text))
        if has_shell and has_topbar and not public_re.search(text):
            err(f"{rel}: loads both shell.js and topbar.js; a page carries one frame (U-13)")
        elif not has_shell and not has_topbar:
            err(f"{rel}: loads neither shell.js nor topbar.js; every page carries one primary navigation (U-13)")
        if inline_re.search(text):
            err(f"{rel}: carries an inline topbar (class topbar/nav-links/top-nav); the shared frame supersedes it (U-13)")


def main():
    ledger = load_ledger()
    if ledger is None:
        sys.exit(1)

    pieces = collect_pieces(ledger)
    if not pieces:
        err("no pieces found in ledger")
        sys.exit(1)

    print(f"validate: {len(pieces)} pieces")

    check_schema(pieces)
    check_cites(pieces)
    check_acyclicity(pieces)
    check_gating(pieces)
    check_done_requires_verified(pieces)
    check_decision_coherence(pieces)
    check_one_navigation(pieces)
    check_lexicon_schema(pieces)

    generate_status_md(pieces)
    generate_ledger_state(pieces)
    generate_index_json(pieces)

    if errors:
        print(f"\nvalidation failed: {len(errors)} error(s)", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"validation passed ({len(warnings)} warning(s))")
        sys.exit(0)


if __name__ == "__main__":
    main()
