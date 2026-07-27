#!/usr/bin/env python3
"""Rail poll (A-04) -- the queue read, and nothing more.

AGY section 6 gives dispatch two honest routes and defaults to the
poll: the instrument already wakes on a schedule, so it reads the
rail on its standing rhythm and takes up what it finds. This script
is that read. It opens nothing, accepts nothing, and writes nothing.

An open Direction is a direction.given with no closing event naming
it. Closing kinds are direction.completed, direction.refused, and
direction.halted, each carrying payload.direction_id. That shape is
the verb's own (0017_direction_rail.sql), so the poll and the bound
agree by construction rather than by a second definition.

Read-only by design. The harness that acts on what this returns is a
separate step, and under the R0 form of AGY section 12 it prepares a
close for the steward rather than writing one: the instrument holds
no grant until the AM v0.2 addendum adopts.

Usage:
  SUPABASE_ACCESS_TOKEN=... python3 scripts/rail_poll.py [--json]

Environment:
  SUPABASE_ACCESS_TOKEN  Supabase Management API token (required)
  CIS_PROJECT_REF        project ref; defaults to the live CIS
"""
import json
import os
import sys
import urllib.request

PROJECT_REF = os.environ.get("CIS_PROJECT_REF", "ujujwgopdwirebgcpekc")
TOKEN = os.environ.get("SUPABASE_ACCESS_TOKEN", "")

OPEN_DIRECTIONS = """
select
  g.id,
  g.recorded_at,
  g.agent_id,
  a.display_name as directed_by,
  g.payload->>'kind'         as kind,
  g.payload->>'brief'        as brief,
  g.payload->'repositories'  as repositories
from events g
left join agents a on a.id = g.agent_id
where g.kind = 'direction.given'
  and not exists (
    select 1 from events c
    where c.kind in ('direction.completed','direction.refused','direction.halted')
      and c.payload->>'direction_id' = g.id::text
  )
order by g.recorded_at asc;
"""


def query(sql):
    """Run one read against the CIS. Cloudflare rejects urllib without a
    User-Agent, so the header is not optional."""
    req = urllib.request.Request(
        f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query",
        data=json.dumps({"query": sql}).encode(),
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "techne-rail-poll/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def main():
    if not TOKEN:
        print("rail_poll: SUPABASE_ACCESS_TOKEN is unset", file=sys.stderr)
        return 2

    rows = query(OPEN_DIRECTIONS)
    if not isinstance(rows, list):
        print(f"rail_poll: unexpected response: {rows}", file=sys.stderr)
        return 1

    if "--json" in sys.argv:
        print(json.dumps(rows, indent=2, default=str))
        return 0

    if not rows:
        print("rail: no open Directions.")
        return 0

    print(f"rail: {len(rows)} open Direction(s).")
    for r in rows:
        repos = r.get("repositories") or []
        if isinstance(repos, str):
            repos = json.loads(repos)
        brief = " ".join((r.get("brief") or "").split())
        if len(brief) > 160:
            brief = brief[:157] + "..."
        print("")
        print(f"  {r['id']}")
        print(f"    given    {r['recorded_at']} by {r.get('directed_by') or r['agent_id']}")
        print(f"    kind     {r.get('kind')}")
        print(f"    estate   {', '.join(repos) if repos else 'the record alone'}")
        print(f"    brief    {brief}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
