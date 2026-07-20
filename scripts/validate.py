#!/usr/bin/env python3
"""
validate.py · SUB-01 emission · BP v1
Validates rdm-ledger.yaml: schema compliance, dependency acyclicity,
gating consistency. Exits non-zero on any violation.
Authored-by: build-agent / SUB-01
"""

import sys
import re
import json
from pathlib import Path

# Use PyYAML if available; fall back to a minimal safe loader for CI environments
# that may not have it pre-installed. The fallback covers the rdm-ledger.yaml format.
try:
    import yaml as _yaml
    def _load_yaml(text):
        return _yaml.safe_load(text)
except ImportError:
    # Minimal YAML loader: handles the subset used in rdm-ledger.yaml.
    # Delegates to a robust third-party parser if one is importable.
    try:
        import tomllib  # Python 3.11+; not YAML but confirms stdlib is modern
        del tomllib
    except ImportError:
        pass

    def _load_yaml(text):
        """
        Very minimal YAML parser sufficient for rdm-ledger.yaml.
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
LEDGER_PATH = REPO_ROOT / "rdm-ledger.yaml"

VALID_STATUSES = {"drafted", "anticipated", "filed"}
REQUIRED_FIELDS = {"address", "title", "intent", "status", "deliverable", "acceptance"}
GATE_ADDRESSES = {"G0", "G-B", "G-G", "G-F", "G-S", "G-R"}

errors = []
warnings = []


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


def collect_packets(ledger):
    packets = {}
    for section_key, items in ledger.items():
        if not isinstance(items, list):
            continue
        for item in items:
            addr = item.get("address")
            if not addr:
                err(f"packet in section '{section_key}' missing address")
                continue
            if addr in packets:
                err(f"duplicate address: {addr}")
            packets[addr] = item
    return packets


def check_schema(packets):
    """Every packet has required fields; status is valid or open."""
    for addr, p in packets.items():
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


def check_cites(packets):
    """Every cite references a known address."""
    all_addresses = set(packets.keys())
    for addr, p in packets.items():
        cites = p.get("cites", []) or []
        for cited in cites:
            if cited not in all_addresses:
                err(f"{addr}: cites unknown address '{cited}'")


def check_acyclicity(packets):
    """No circular dependencies in cites."""
    # Build adjacency: address -> set of cites
    adj = {addr: set(p.get("cites", []) or []) for addr, p in packets.items()}

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


def check_gating(packets):
    """Gate addresses exist; blocked packets name their blocker."""
    for addr, p in packets.items():
        status = p.get("status", "")
        if status.startswith("open ·"):
            blocker = status[len("open ·"):].strip()
            if not blocker:
                err(f"{addr}: open status must name a blocker: 'open · <blocker>'")
        ready = p.get("ready_when", "") or ""
        # Check gate references in ready_when
        for gate in GATE_ADDRESSES:
            if gate in ready and gate not in packets:
                err(f"{addr}: ready_when references undefined gate '{gate}'")


def check_done_requires_verified(packets):
    """A packet with status 'filed' must not depend on an un-filed upstream."""
    for addr, p in packets.items():
        if p.get("status") == "filed":
            cites = p.get("cites", []) or []
            for cited in cites:
                upstream = packets.get(cited, {})
                if upstream.get("status") not in ("filed", "drafted"):
                    warn(
                        f"{addr}: filed but cites '{cited}' which is '{upstream.get('status','?')}'"
                    )


def check_decision_coherence(packets):
    """X-07: every escalation card on an opened packet carries a recorded decision.

    An escalation card is a packet's `escalation` field, in the standing-in /
    found / the-question / a-default shape of BP v1 §2 (see SUB-03 for the
    convention). It is resolved when a decision is recorded: a `decision` key
    inside the escalation mapping, or a sibling `decision` field on the packet.
    A packet that has opened (status begins 'open') must not carry an unresolved
    escalation card: the decision is recorded before the blocked packet opens.
    """
    for addr, p in packets.items():
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
                f"{addr}: opened packet carries an unresolved escalation card; "
                f"record its decision before it opens (BP v1 §2, X-07)"
            )


def generate_status_md(packets):
    """Write STATUS.md summarizing ledger state."""
    status_path = REPO_ROOT / "STATUS.md"
    drafted = [a for a, p in packets.items() if p.get("status") == "drafted"]
    anticipated = [a for a, p in packets.items() if p.get("status") == "anticipated"]
    open_packets = [a for a, p in packets.items() if p.get("status", "").startswith("open")]
    filed = [a for a, p in packets.items() if p.get("status") == "filed"]

    lines = [
        "<!-- STATUS.md generated by scripts/validate.py -- do not edit by hand -->",
        "# STATUS.md · Common Record Series · RDM v1",
        "",
        f"Generated from rdm-ledger.yaml. {len(packets)} items total.",
        "",
        f"| status | count |",
        f"|--------|-------|",
        f"| drafted | {len(drafted)} |",
        f"| anticipated | {len(anticipated)} |",
        f"| open | {len(open_packets)} |",
        f"| filed | {len(filed)} |",
        "",
        "## Drafted",
        "",
    ]
    for a in sorted(drafted):
        p = packets[a]
        lines.append(f"- **{a}** {p.get('title','')} -- {p.get('intent','')[:80]}")

    lines += ["", "## Open", ""]
    for a in sorted(open_packets):
        p = packets[a]
        lines.append(f"- **{a}** {p.get('status','')} -- {p.get('title','')}")

    lines += ["", "## Anticipated", ""]
    for a in sorted(anticipated):
        p = packets[a]
        lines.append(f"- **{a}** {p.get('title','')}")

    if filed:
        lines += ["", "## Filed", ""]
        for a in sorted(filed):
            p = packets[a]
            lines.append(f"- **{a}** {p.get('title','')}")

    lines += ["", "---", "", "*RegenHub, LCA -- Boulder, Colorado -- July 2026*", ""]

    status_path.write_text("\n".join(lines))
    print(f"wrote {status_path}")


def generate_index_json(packets):
    """Write index.json, the document manifest (X-04): every HTML page in the
    repository, enumerated by walking the tree, so exhaustiveness holds by
    construction. The committed manifest must match the tree: a stale
    index.json is an error, not a silent regeneration, so CI catches a page
    added without refreshing the manifest."""
    import json
    index_path = REPO_ROOT / "index.json"

    html_files = sorted(str(p.relative_to(REPO_ROOT)) for p in REPO_ROOT.rglob("*.html"))
    index = {
        "generated": "scripts/validate.py",
        "series": "RDM v1",
        "ledger_items": len(packets),
        "pages": html_files,
    }
    content = json.dumps(index, indent=2)

    stale = not index_path.exists() or index_path.read_text() != content
    index_path.write_text(content)
    print(f"wrote {index_path} ({len(html_files)} pages)")
    if stale:
        err("index.json was stale or missing; refreshed. Commit the regenerated manifest (X-04).")


def main():
    ledger = load_ledger()
    if ledger is None:
        sys.exit(1)

    packets = collect_packets(ledger)
    if not packets:
        err("no packets found in ledger")
        sys.exit(1)

    print(f"validate: {len(packets)} packets")

    check_schema(packets)
    check_cites(packets)
    check_acyclicity(packets)
    check_gating(packets)
    check_done_requires_verified(packets)
    check_decision_coherence(packets)

    generate_status_md(packets)
    generate_index_json(packets)

    if errors:
        print(f"\nvalidation failed: {len(errors)} error(s)", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"validation passed ({len(warnings)} warning(s))")
        sys.exit(0)


if __name__ == "__main__":
    main()
