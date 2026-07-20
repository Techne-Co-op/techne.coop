#!/usr/bin/env python3
"""CIS export producer (X-03) -- VS v1 section 8, the walkaway path.

Takes a full per-table export through the export.* views and records
the SHA convention the X-03 decision pinned, superseding the ad-hoc
hash SUB-05 recorded:

  THE FORMAT, pinned by decision (X-03 escalation card, 2026-07-20):
  - one file per table: exports/<table>.json
  - file content: the text of  select jsonb_agg(to_jsonb(t) order by t.id)
    from export.<table> t  -- postgres jsonb text form, which sorts
    object keys canonically and renders numerics exactly -- followed
    by a single newline. An empty table is the literal  []  plus
    newline.
  - per-table SHA: sha256 over the exact file bytes.
  - exports/manifest.json: {"tables": {name: sha}} with sorted keys,
    two-space indent, trailing newline. Nothing time-dependent enters
    the manifest: the same data always yields the same bytes. The
    manifest SHA (sha256 over the manifest file bytes) is THE export
    SHA that gets recorded; the recording event carries the timestamp.

Audience, pinned by the same decision: service-role / disaster
recovery only. This producer runs as the service role (or any role
whose row security shows the full set: the CI substrate's superuser).
No member or steward download path exists until an Authority Map
anchor grants one.

Usage: PGURL=postgres://... python3 scripts/export_cis.py [outdir]
Prints one line per table and the manifest SHA last.
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

PGURL = os.environ.get("PGURL", "postgresql://postgres:postgres@localhost:5432/postgres")

# FK-safe restore order; the importer replays this list top to bottom.
TABLES = [
    "agents", "agreements", "memberships", "stock_ledger", "applications",
    "gatherings", "sessions", "events", "signatures", "registrations",
    "attendance", "opportunities", "responses", "role_grants",
]


def fetch(table):
    sql = f"select coalesce(jsonb_agg(to_jsonb(t) order by t.id), '[]'::jsonb) from export.{table} t"
    r = subprocess.run(["psql", PGURL, "-v", "ON_ERROR_STOP=1", "-q", "-t", "-A", "-c", sql],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"export failed on {table}:\n{r.stderr}", file=sys.stderr)
        sys.exit(1)
    return r.stdout.strip() + "\n"


def main():
    outdir = Path(sys.argv[1] if len(sys.argv) > 1 else "exports")
    outdir.mkdir(parents=True, exist_ok=True)
    shas = {}
    for t in TABLES:
        content = fetch(t)
        path = outdir / f"{t}.json"
        path.write_text(content)
        shas[t] = hashlib.sha256(content.encode()).hexdigest()
        rows = len(json.loads(content))
        print(f"{t}: {rows} row(s) sha256:{shas[t][:16]}")

    manifest = json.dumps({"tables": shas}, sort_keys=True, indent=2) + "\n"
    (outdir / "manifest.json").write_text(manifest)
    manifest_sha = hashlib.sha256(manifest.encode()).hexdigest()
    print(f"manifest sha256:{manifest_sha}")


if __name__ == "__main__":
    main()
