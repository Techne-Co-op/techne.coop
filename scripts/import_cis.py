#!/usr/bin/env python3
"""CIS import (X-09) -- the restore half of the walkaway rehearsal.

Replays an export taken by scripts/export_cis.py into a fresh
substrate: per-table JSON in FK-safe order, inserted through
jsonb_populate_recordset so every column round-trips exactly. The
target database must already carry the schema (0001, the portable
addenda, 0004); this script moves data only.

Usage: PGURL=postgres://... python3 scripts/import_cis.py <exportdir>
"""
import os
import subprocess
import sys
from pathlib import Path

PGURL = os.environ.get("PGURL", "postgresql://postgres:postgres@localhost:5432/postgres")

TABLES = [
    "agents", "agreements", "memberships", "stock_ledger", "applications",
    "gatherings", "sessions", "events", "signatures", "registrations",
    "attendance", "opportunities", "responses", "role_grants",
]

TAG = "$cis_import$"


def main():
    if len(sys.argv) < 2:
        print("usage: import_cis.py <exportdir>", file=sys.stderr)
        sys.exit(2)
    exportdir = Path(sys.argv[1])
    for t in TABLES:
        payload = (exportdir / f"{t}.json").read_text().strip()
        if TAG in payload:
            print(f"import failed on {t}: payload collides with quote tag", file=sys.stderr)
            sys.exit(1)
        sql = (f"insert into public.{t} "
               f"select * from jsonb_populate_recordset(null::public.{t}, {TAG}{payload}{TAG}::jsonb);")
        r = subprocess.run(["psql", PGURL, "-v", "ON_ERROR_STOP=1", "-q", "-f", "-"],
                           input=sql, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"import failed on {t}:\n{r.stderr}", file=sys.stderr)
            sys.exit(1)
        print(f"{t}: imported")


if __name__ == "__main__":
    main()
