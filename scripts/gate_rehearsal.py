#!/usr/bin/env python3
"""Gate rehearsal (G-B, G-G) -- the mechanical half of the Gate Book.

Runs every Belong and Gather sentence of PRD v0.3 section 4 as a
committed, sequential assertion against a fresh substrate with the
full policy chain applied: the same journey the August 14 gates
demonstrate with people, exercised here by machine so the ceremony
never discovers a defect. This is the with-their-slices suite
arriving with its slices (VS v1 closing note).

Unlike the probe matrix (scripts/rls_probe.py), which proves each
authority cell in isolation and rolls everything back, the rehearsal
commits each beat: the newcomer who signs in beat three is the same
row that appeared in beat one, because a journey is a sequence, not a
matrix.

One beat is named-deferred, not faked: onboarding through
apply_for_membership() waits for the function's source to land in the
repository (the X-09 restore-completeness card). Its stand-in is a
seeded applied membership, and the beat activates the day the
migration exists.

Personas run through the same auth.uid() shim as the probe matrix.
Usage: PGURL=postgres://... python3 scripts/gate_rehearsal.py
"""
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PGURL = os.environ.get("PGURL", "postgresql://postgres:postgres@localhost:5432/postgres")

STEWARD  = "00000000-0000-4000-a000-000000000001"
NEWCOMER = "00000000-0000-4000-a000-000000000002"
HOST     = "00000000-0000-4000-a000-000000000003"   # the second party; hosts Gather
AGR      = "00000000-0000-4000-a000-000000000101"
GAT      = "00000000-0000-4000-a000-000000000201"
SES      = "00000000-0000-4000-a000-000000000202"

BOOTSTRAP = """
create role anon nologin;
create role authenticated nologin;
create schema auth;
create function auth.uid() returns uuid
language sql stable as
$$ select nullif(current_setting('app.uid', true), '')::uuid $$;
"""

MIGRATIONS = [
    "commons/im/0001_substrate.sql",
    "commons/authority-map/0002_policies.sql",
    "commons/authority-map/0003_sign_agreement.sql",
    "commons/authority-map/0005_matrix_conformance.sql",
]

SEED = f"""
insert into agents (id, kind, display_name) values
  ('{STEWARD}',  'person', 'Rehearsal Steward'),
  ('{NEWCOMER}', 'person', 'Rehearsal Newcomer'),
  ('{HOST}',     'person', 'Rehearsal Host');
update agents set auth_user_id = id;
insert into role_grants (agent_id, role) values ('{STEWARD}', 'steward');
insert into memberships (agent_id, state) values
  ('{NEWCOMER}', 'applied'),
  ('{HOST}',     'active');
insert into agreements (id, code, title, version, effective_date) values
  ('{AGR}', 'BYLAWS', 'Rehearsal Bylaws', 'v2.1', '2026-07-01');
"""


def psql(sql):
    r = subprocess.run(["psql", PGURL, "-v", "ON_ERROR_STOP=1", "-q", "-t", "-A", "-f", "-"],
                       input=sql, capture_output=True, text=True)
    lines = [l for l in r.stdout.splitlines() if l.strip()]
    return r.returncode, lines, r.stderr


def as_persona(uid, sql):
    """One committed transaction as the persona: a beat, not a probe."""
    return psql(
        "begin;\n"
        f"select set_config('app.uid', '{uid}', true);\n"
        "set local role authenticated;\n"
        f"{sql};\ncommit;"
    )


failures = []

def beat(n, sentence, ok, detail):
    mark = "PASS" if ok else "FAIL"
    print(f"{mark} beat {n}: {sentence} [{detail}]")
    if not ok:
        failures.append(n)


def main():
    for step_sql, label in [(BOOTSTRAP, "bootstrap")] + \
            [((REPO_ROOT / m).read_text(), m) for m in MIGRATIONS] + [(SEED, "seed")]:
        rc, _, err = psql(step_sql)
        if rc != 0:
            print(f"{label} failed:\n{err}", file=sys.stderr)
            sys.exit(1)

    # -- beat 0 · named deferral -------------------------------------
    print("DEFERRED beat 0: 'complete onboarding without a meeting' waits on "
          "apply_for_membership() landing in the repository (X-09 card); "
          "its stand-in is the seeded applied membership")

    # -- beat 1 · the steward admits (lifecycle by the assigned hand) --
    rc, lines, _ = as_persona(STEWARD,
        f"update memberships set state = 'active' where agent_id = '{NEWCOMER}' returning 1")
    beat(1, "admission is the act of the Board's assigned hand (1.3, 1.7)",
         rc == 0 and len(lines) == 2, f"steward flipped applied to active, rc={rc}")

    # -- beat 2 · read every agreement that binds them -----------------
    rc, lines, _ = as_persona(NEWCOMER,
        "select count(*) from agreements where version is not null and effective_date is not null")
    beat(2, "a member can read every agreement that binds them, version and standing marked",
         rc == 0 and lines[-1] == "1", f"agreements visible: {lines[-1] if lines else '?'}")

    # -- beat 3 · sign, atomically, and see it recorded ----------------
    rc, lines, err = as_persona(NEWCOMER,
        f"select sign_agreement('{AGR}')")
    beat(3, "a member can sign the membership agreement and see the signature recorded",
         rc == 0 and lines and "signature_id" in lines[-1], f"rc={rc}")
    rc, lines, _ = as_persona(NEWCOMER,
        f"select count(*) from signatures where agent_id = '{NEWCOMER}' and event_id is not null")
    beat(3.1, "the signature and its event are linked in one act (B-04 decision)",
         rc == 0 and lines[-1] == "1", f"linked signatures: {lines[-1] if lines else '?'}")
    rc, lines, err = as_persona(NEWCOMER, f"select sign_agreement('{AGR}')")
    beat(3.2, "signing is idempotent: a second signature is refused, not duplicated",
         rc != 0 and "already signed" in err, "double-sign refused")

    # -- beat 4 · appear in the directory with a profile they control --
    rc, lines, _ = as_persona(NEWCOMER,
        f"update agents set display_name = 'Rehearsal Newcomer (settled in)' "
        f"where id = '{NEWCOMER}' returning 1")
    beat(4, "a member can appear in the directory with a profile they control",
         rc == 0 and len(lines) == 2, f"self-edit rc={rc}")
    rc, lines, _ = as_persona(NEWCOMER,
        f"update agents set display_name = 'x' where id = '{HOST}' returning 1")
    beat(4.1, "and only the profile they control (1.13)",
         len(lines) < 2, "cross-edit matched no rows")

    # -- beat 5 · host an event under a named agreement or policy ------
    rc, lines, _ = as_persona(HOST,
        f"insert into gatherings (id, title, host_agent_id, agreement_id) "
        f"values ('{GAT}', 'Rehearsal Gathering', '{HOST}', '{AGR}') returning 1")
    beat(5, "a member can host an event under a named agreement or policy",
         rc == 0 and len(lines) == 2, f"gathering created rc={rc}")
    rc, lines, _ = as_persona(HOST,
        f"insert into sessions (id, gathering_id, starts_at) "
        f"values ('{SES}', '{GAT}', '2026-08-14T19:00:00-06:00') returning 1")
    beat(5.1, "the host schedules the session (2.1)",
         rc == 0 and len(lines) == 2, f"session created rc={rc}")

    # -- beat 6 · see upcoming events and sessions ---------------------
    rc, lines, _ = as_persona(NEWCOMER,
        f"select count(*) from sessions s join gatherings g on g.id = s.gathering_id "
        f"where g.agreement_id is not null")
    beat(6, "a member can see upcoming events and sessions",
         rc == 0 and lines[-1] == "1", f"sessions visible: {lines[-1] if lines else '?'}")

    # -- beat 7 · register, and cancel, without asking anyone ----------
    rc, lines, _ = as_persona(NEWCOMER,
        f"insert into registrations (session_id, agent_id) values ('{SES}', '{NEWCOMER}') returning 1")
    beat(7, "a member can register without asking anyone",
         rc == 0 and len(lines) == 2, f"registered rc={rc}")
    rc, lines, _ = as_persona(NEWCOMER,
        f"update registrations set state = 'cancelled' where agent_id = '{NEWCOMER}' returning 1")
    beat(7.1, "and cancel without asking anyone",
         rc == 0 and len(lines) == 2, f"cancelled rc={rc}")
    rc, lines, _ = as_persona(NEWCOMER,
        f"update registrations set state = 'registered' where agent_id = '{NEWCOMER}' returning 1")
    beat(7.2, "and return; the cycle is preserved, not deleted (Law I)",
         rc == 0 and len(lines) == 2, f"re-registered rc={rc}")

    # -- beat 8 · attendance counted where the record counts it --------
    rc, lines, _ = as_persona(HOST,
        f"insert into attendance (session_id, agent_id, recorded_by) "
        f"values ('{SES}', '{NEWCOMER}', '{HOST}') returning 1")
    beat(8, "a member can have attendance counted where the record counts it",
         rc == 0 and len(lines) == 2, f"host recorded rc={rc}")
    rc, lines, err = as_persona(NEWCOMER,
        f"insert into attendance (session_id, agent_id, recorded_by) "
        f"values ('{SES}', '{HOST}', '{NEWCOMER}') returning 1")
    beat(8.1, "presence is recorded by host or steward, never self-reported (2.7)",
         rc != 0, "self-report refused")

    # -- beat 9 · the record coheres ------------------------------------
    rc, lines, _ = as_persona(STEWARD,
        "select count(*) from events where kind = 'signature.signed'")
    beat(9, "the steward reads the whole journey in the log (4.1; 0005)",
         rc == 0 and lines[-1] == "1", f"signature events: {lines[-1] if lines else '?'}")
    rc, lines, _ = psql("select count(*) from signatures where event_id is null")
    beat(9.1, "no signature stands without its recording event",
         rc == 0 and lines[-1] == "0", f"unlinked: {lines[-1] if lines else '?'}")

    print(f"gate-rehearsal: {'FAILED on beats ' + str(failures) if failures else 'every sentence holds'}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
