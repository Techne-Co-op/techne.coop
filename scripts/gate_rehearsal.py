#!/usr/bin/env python3
"""Gate rehearsal (G-B, G-G, G-F) -- the mechanical half of the Gate Book.

Runs every Belong, Gather, and Find sentence of PRD v0.3 section 4 as
a committed, sequential assertion against a fresh substrate with the
full policy chain applied: the same journey the gates demonstrate
with people, exercised here by machine so the ceremony never
discovers a defect. This is the with-their-slices suite arriving with
its slices (VS v1 closing note).

Unlike the probe matrix (scripts/rls_probe.py), which proves each
authority cell in isolation and rolls everything back, the rehearsal
commits each beat: the newcomer who signs in beat three is the same
row that appeared in beat one, because a journey is a sequence, not a
matrix.

The onboarding beat runs through the real front door the moment
0007_apply_for_membership.sql exists in the migration chain (it was
captured from the live CIS under the X-09 restore-completeness card);
if the file is ever absent the beat defers by name rather than fake a
pass. The seeded applied membership stands in for the later beats
either way, so the journey never depends on the door.

Personas run through the same auth.uid() shim as the probe matrix.
Usage: PGURL=postgres://... python3 scripts/gate_rehearsal.py
"""
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PGURL = os.environ.get("PGURL", "postgresql://postgres:postgres@localhost:5432/postgres")

STEWARD   = "00000000-0000-4000-a000-000000000001"
NEWCOMER  = "00000000-0000-4000-a000-000000000002"
HOST      = "00000000-0000-4000-a000-000000000003"   # the second party; hosts Gather, responds in Find
BYSTANDER = "00000000-0000-4000-a000-000000000004"   # a plain member, party to nothing; proves 18.2 scoping
AGR      = "00000000-0000-4000-a000-000000000101"
GAT      = "00000000-0000-4000-a000-000000000201"
SES      = "00000000-0000-4000-a000-000000000202"
OPP      = "00000000-0000-4000-a000-000000000301"

BOOTSTRAP = """
create role anon nologin;
create role authenticated nologin;
-- mirror the platform default the live CIS carries: anon holds usage
-- on the schema (pg_namespace.nspacl, read 2026-07-21); table grants
-- still exclude anon, so anon reads nothing (0002 closing note).
grant usage on schema public to anon;
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
    "commons/authority-map/0008_admissions.sql",
]
FRONT_DOOR = "commons/authority-map/0007_apply_for_membership.sql"
if (REPO_ROOT / FRONT_DOOR).exists():
    MIGRATIONS.append(FRONT_DOOR)

SEED = f"""
insert into agents (id, kind, display_name) values
  ('{STEWARD}',   'person', 'Rehearsal Steward'),
  ('{NEWCOMER}',  'person', 'Rehearsal Newcomer'),
  ('{HOST}',      'person', 'Rehearsal Host'),
  ('{BYSTANDER}', 'person', 'Rehearsal Bystander');
update agents set auth_user_id = id;
insert into role_grants (agent_id, role) values ('{STEWARD}', 'steward');
insert into memberships (agent_id, state) values
  ('{NEWCOMER}',  'applied'),
  ('{HOST}',      'active'),
  ('{BYSTANDER}', 'active');
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

    # -- beat 0 · the front door ---------------------------------------
    if (REPO_ROOT / FRONT_DOOR).exists():
        rc, lines, err = psql(
            "begin;\nset local role anon;\n"
            "select apply_for_membership('Rehearsal Applicant', "
            "'applicant@rehearsal.test', 'came in through the front door');\ncommit;")
        beat(0, "a member can complete onboarding without a meeting",
             rc == 0 and lines and "received" in lines[-1], f"anon applied, rc={rc}")
        rc, lines, _ = psql(
            "select count(*) from memberships m join agents a on a.id = m.agent_id "
            "where a.display_name = 'Rehearsal Applicant' and m.state = 'applied'")
        beat(0.1, "the application, membership, and event land atomically (1.2, 1.3.1(d))",
             rc == 0 and lines and lines[-1] == "1", f"applied memberships: {lines[-1] if lines else '?'}")
        rc, lines, _ = psql(
            "select count(*) from events where kind = 'membership.applied' "
            "and payload ->> 'email' = 'applicant@rehearsal.test'")
        beat(0.2, "the event carries the address the notices rail reads (X-02 seam)",
             rc == 0 and lines and lines[-1] == "1", f"applied events with email: {lines[-1] if lines else '?'}")
    else:
        print("DEFERRED beat 0: 'complete onboarding without a meeting' waits on "
              "apply_for_membership() landing in the repository (X-09 card); "
              "its stand-in is the seeded applied membership")

    # -- beat 1 · the steward admits, one act: flip and event (0008) ----
    rc, lines, err = as_persona(HOST,
        f"select admit_member('{NEWCOMER}')")
    beat(1, "admission is refused to hands the Board has not assigned (1.3, 3.1)",
         rc != 0 and "assigned hand" in err, "non-steward admit refused")
    rc, lines, _ = as_persona(STEWARD,
        f"select admit_member('{NEWCOMER}')")
    beat(1.1, "admission is the act of the Board's assigned hand (1.3, 1.7)",
         rc == 0 and lines and "admitted" in lines[-1], f"steward admitted rc={rc}")
    rc, lines, _ = psql(
        f"select count(*) from events where kind = 'membership.admitted' and agent_id = '{NEWCOMER}'")
    beat(1.2, "the admission and its event land together (0008, the 0003 pattern)",
         rc == 0 and lines[-1] == "1", f"admitted events: {lines[-1] if lines else '?'}")

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

    # -- beat 9 · post an offer or a need (F-01) ----------------------
    rc, lines, _ = as_persona(NEWCOMER,
        f"insert into opportunities (id, author_agent_id, kind, title, body) "
        f"values ('{OPP}', '{NEWCOMER}', 'work', 'Rehearsal Opportunity', "
        f"'posted in the rehearsal') returning 1")
    beat(9, "a member can post an offer or a need",
         rc == 0 and len(lines) == 2, f"posted rc={rc}")
    rc, lines, _ = as_persona(HOST,
        "select count(*) from opportunities where kind = 'work' and state = 'open'")
    beat(9.1, "a member can browse open invitations by kind (18.1)",
         rc == 0 and lines[-1] == "1", f"open work postings visible: {lines[-1] if lines else '?'}")

    # -- beat 10 · respond, scoped between responder and author (F-02) -
    rc, lines, _ = as_persona(HOST,
        f"insert into responses (opportunity_id, agent_id, note) "
        f"values ('{OPP}', '{HOST}', 'answering the rehearsal call') returning 1")
    beat(10, "a member can answer an open opportunity",
         rc == 0 and len(lines) == 2, f"responded rc={rc}")
    rc, lines, _ = as_persona(NEWCOMER,
        f"select count(*) from responses where opportunity_id = '{OPP}'")
    beat(10.1, "the author sees the response",
         rc == 0 and lines[-1] == "1", f"author sees: {lines[-1] if lines else '?'}")
    rc, lines, _ = as_persona(BYSTANDER,
        f"select count(*) from responses where opportunity_id = '{OPP}'")
    beat(10.2, "a member who is party to neither side sees nothing (18.2)",
         rc == 0 and lines[-1] == "0", f"bystander sees: {lines[-1] if lines else '?'}")

    # -- beat 11 · resolution as an event, never a table (F-03) --------
    rc, lines, _ = as_persona(HOST,
        f"update opportunities set state = 'resolved', resolved_at = now() "
        f"where id = '{OPP}' returning 1")
    beat(11, "only the author closes their posting",
         len(lines) < 2, "non-author close matched no rows")
    rc, lines, _ = as_persona(NEWCOMER,
        f"update opportunities set state = 'resolved', resolved_at = now() "
        f"where id = '{OPP}' returning 1")
    beat(11.1, "a member can close an invitation when it resolves",
         rc == 0 and len(lines) == 2, f"resolved rc={rc}")
    rc, lines, _ = as_persona(NEWCOMER,
        f"insert into events (occurred_at, actor_agent_id, agent_id, kind, payload) "
        f"values (now(), '{NEWCOMER}', '{NEWCOMER}', 'opportunity.resolved', "
        f"jsonb_build_object('opportunity_id', '{OPP}', 'note', 'it led somewhere')) returning 1")
    beat(11.2, "the outcome lands as an event, never a table (Law I)",
         rc == 0 and len(lines) == 2, f"resolution event rc={rc}")
    rc, lines, _ = as_persona(BYSTANDER,
        "select count(*) from events where kind = 'opportunity.resolved'")
    beat(11.3, "the outcome is the parties' to read (18.2; events_read)",
         rc == 0 and lines[-1] == "0", f"bystander reads: {lines[-1] if lines else '?'}")
    rc, lines, _ = as_persona(HOST,
        f"select count(*) from opportunities where id = '{OPP}' and state = 'resolved'")
    beat(11.4, "the board shows the closed state to every member, from the row itself",
         rc == 0 and lines[-1] == "1", f"resolved visible: {lines[-1] if lines else '?'}")

    # -- beat 12 · the record coheres, the whole journey in the log ----
    rc, lines, _ = as_persona(STEWARD,
        "select count(*) from events where kind = 'signature.signed'")
    beat(12, "the steward reads the whole journey in the log (4.1; 0005)",
         rc == 0 and lines[-1] == "1", f"signature events: {lines[-1] if lines else '?'}")
    rc, lines, _ = psql("select count(*) from signatures where event_id is null")
    beat(12.1, "no signature stands without its recording event",
         rc == 0 and lines[-1] == "0", f"unlinked: {lines[-1] if lines else '?'}")

    print(f"gate-rehearsal: {'FAILED on beats ' + str(failures) if failures else 'every sentence holds'}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
