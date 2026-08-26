#!/usr/bin/env python3
"""
sms05_probe.py · SMS-05 · the intranet binding ceremony, walked
=================================================================
The battery for `commons/authority-map/0029_phone_bindings_intranet.sql`,
in the shape `scripts/rls_probe.py` established: a fresh substrate, the
policy chain applied, Supabase's `auth.uid()` shimmed to a
transaction-local GUC, and every assertion citing what it is holding.

Why this file exists rather than a paragraph in a design page. The
migration it exercises moves an authentication anchor, and three of its
properties are the kind that pass review by reading and fail in
practice:

  1. the two verified bindings that already exist must survive, keep
     routing, and not be silently rewritten;
  2. `code_hash` must be unreadable by the member whose code it is,
     because a readable hash of six digits is the code, and a member who
     can read it can bind a number they never held;
  3. a member's read of `phone_events` must close at both ends of their
     binding, so a number that changes hands hands over no history.

Each is a probe below. A green run says nothing about anything not
listed here; in particular it says nothing about the relay, the carrier,
or whether the migration has been applied to the live CIS, which as of
this file it has not.

Usage:  python3 scripts/sms05_probe.py
Needs:  a scratch Postgres at $PGURL. Everything it does is destructive
        to that database and harmless anywhere else.

Authored-by: Nou / SMS-05
"""

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
PGURL = os.environ.get("PGURL", "postgresql://postgres:postgres@localhost:5432/postgres")

# ---------- fixture cast (fixed UUIDs; auth_user_id = agent id) ----------
MEM1 = "00000000-0000-4000-8000-000000000002"   # binds, revokes, rebinds
MEM2 = "00000000-0000-4000-8000-000000000003"   # takes the number over
MEM3 = "00000000-0000-4000-8000-000000000004"   # walks into the rate limit
APP = "00000000-0000-4000-8000-000000000001"    # applicant, not a member

LEGACY_A = "+13035059612"                       # a pre-SMS-05 buzz binding
LEGACY_B = "+19705551234"                       # a second one
CEREMONY = "+14155550100"                       # the number this walk binds
FRESH = "+14155550199"                          # MEM3's rate-limit target

CODE = "123456"

BOOTSTRAP = """
create role anon nologin;
create role authenticated nologin;
create role authenticator nologin;
create schema auth;
create function auth.uid() returns uuid
language sql stable as
$$ select nullif(current_setting('app.uid', true), '')::uuid $$;
"""

MIGRATIONS = [
    "commons/im/0001_substrate.sql",
    "commons/authority-map/0002_policies.sql",
    "commons/authority-map/0026_phone_events.sql",
    "commons/authority-map/0027_phone_relay_role.sql",
    "commons/authority-map/0028_phone_bindings.sql",
    "commons/authority-map/0029_phone_bindings_intranet.sql",
]

SEED = f"""
insert into agents (id, kind, display_name) values
  ('{APP}',  'person', 'Probe Applicant'),
  ('{MEM1}', 'person', 'Probe Member One'),
  ('{MEM2}', 'person', 'Probe Member Two'),
  ('{MEM3}', 'person', 'Probe Member Three');
update agents set auth_user_id = id;

insert into memberships (agent_id, state) values
  ('{APP}',  'applied'),
  ('{MEM1}', 'active'),
  ('{MEM2}', 'active'),
  ('{MEM3}', 'active');
"""

# The two bindings that already exist on the live CIS, in the shape 0028
# minted them: a key, a number, no agent, no origin column at the time.
# Seeded AFTER 0029 so they carry the default origin, which is what the
# live rows will carry the moment the migration applies.
LEGACY = f"""
insert into phone_bindings
  (member_pubkey, peer_e164, status, verified_at, buzz_channel_id)
values
  (repeat('a', 64), '{LEGACY_A}', 'verified', now() - interval '2 days', 'chan-a'),
  (repeat('b', 64), '{LEGACY_B}', 'verified', now() - interval '1 day',  'chan-b');
"""


def psql(sql):
    """Run sql through psql; return (returncode, data_lines, stderr)."""
    cmd = ["psql", PGURL, "-v", "ON_ERROR_STOP=1", "-q", "-t", "-A", "-f", "-"]
    r = subprocess.run(cmd, input=sql, capture_output=True, text=True)
    lines = [line for line in r.stdout.splitlines() if line.strip()]
    return r.returncode, lines, r.stderr


def as_member(uid, sql):
    """One statement as `authenticated`, with auth.uid() shimmed. Rolled back."""
    script = ("begin;\n"
              f"select set_config('app.uid', '{uid}', true);\n"
              f"set local role authenticated;\n{sql};\nrollback;")
    rc, lines, err = psql(script)
    return rc, lines[1:], err


def as_member_commit(uid, sql):
    """The same, committed: the ceremony walk has to accumulate state."""
    script = ("begin;\n"
              f"select set_config('app.uid', '{uid}', true);\n"
              f"set local role authenticated;\n{sql};\ncommit;")
    rc, lines, err = psql(script)
    return rc, lines[1:], err


def as_router(sql):
    script = f"begin;\nset local role phone_router;\n{sql};\nrollback;"
    return psql(script)


FAILURES = []
COUNT = 0


def check(pid, cite, ok, got):
    global COUNT
    COUNT += 1
    if not ok:
        FAILURES.append((pid, cite, got))


def expect_value(pid, cite, rc, lines, want):
    check(pid, cite, rc == 0 and lines and lines[0] == str(want),
          f"rc={rc} got={lines[:1]} want={want}")


def expect_deny(pid, cite, rc, lines):
    check(pid, cite, rc != 0, f"rc={rc} rows={lines[:1]}")


def verb(uid, sql):
    """Call a security definer verb and return its jsonb status field."""
    rc, lines, err = as_member_commit(uid, f"select ({sql})->>'status'")
    return rc, (lines[0] if lines else None), err


def verb_reason(uid, sql):
    rc, lines, err = as_member_commit(uid, f"select coalesce(({sql})->>'reason','')")
    return rc, (lines[0] if lines else None), err


def sql_scalar(sql):
    rc, lines, err = psql(sql)
    return lines[0] if rc == 0 and lines else None


def main():
    rc, _, err = psql(BOOTSTRAP)
    if rc != 0:
        print(f"bootstrap failed:\n{err}", file=sys.stderr)
        sys.exit(1)
    for m in MIGRATIONS:
        rc, _, err = psql((REPO_ROOT / m).read_text())
        if rc != 0:
            print(f"migration {m} failed:\n{err}", file=sys.stderr)
            sys.exit(1)
    for block in (SEED, LEGACY):
        rc, _, err = psql(block)
        if rc != 0:
            print(f"seed failed:\n{err}", file=sys.stderr)
            sys.exit(1)

    # ---------------------------------------------------------------
    # 1 · preservation. The migration that orphans an existing binding
    #     is a defect, not a migration.
    # ---------------------------------------------------------------
    expect_value("preserve-verified", "0029 §1: existing rows keep their status",
                 0, [sql_scalar("select count(*) from phone_bindings "
                                "where status = 'verified' and agent_id is null "
                                "and member_pubkey is not null")], 2)
    expect_value("preserve-origin", "0029 §1: the default describes them truthfully",
                 0, [sql_scalar("select count(*) from phone_bindings "
                                "where origin = 'buzz'")], 2)
    rc, lines, _ = as_router("select count(*) from phone_bindings")
    expect_value("preserve-routing", "0028 phone_router_select: unchanged",
                 rc, lines, 2)

    # ---------------------------------------------------------------
    # 2 · the anchor constraints. A row that names nobody is not a
    #     binding, and an intranet ceremony without an agent produced
    #     nothing.
    # ---------------------------------------------------------------
    rc, lines, _ = psql(f"insert into phone_bindings (peer_e164, status) "
                        f"values ('{FRESH}', 'requested')")
    expect_deny("anchor-required", "0029 §1: phone_bindings_anchor_present", rc, lines)
    rc, lines, _ = psql(f"insert into phone_bindings (peer_e164, status, origin) "
                        f"values ('{FRESH}', 'requested', 'intranet')")
    expect_deny("intranet-needs-agent", "0029 §1: phone_bindings_intranet_has_agent",
                rc, lines)

    # ---------------------------------------------------------------
    # 3 · the ceremony, walked as the member walks it.
    # ---------------------------------------------------------------
    rc, status, err = verb(APP, f"phone_bind_request('{CEREMONY}')")
    check("request-applicant-refused", "0029 §5: §1.13, §2.9 the register is the members'",
          status == "refused", f"rc={rc} status={status} {err.strip()[-120:]}")

    rc, status, _ = verb(MEM1, "phone_bind_request('not-a-number')")
    check("request-shape", "0029 §5: E.164 or nothing", status == "refused",
          f"status={status}")

    rc, status, _ = verb(MEM1, f"phone_bind_request('{CEREMONY}')")
    check("request-ok", "0029 §5: a signed-in member asks", status == "requested",
          f"rc={rc} status={status}")

    bid = sql_scalar(f"select id from phone_bindings where peer_e164 = '{CEREMONY}' "
                     f"and agent_id = '{MEM1}'")
    check("request-anchored", "0029 §1: the row carries the member the intranet knows",
          bid is not None, f"binding_id={bid}")
    expect_value("request-evented", "0029 §5: the ceremony is in the record",
                 0, [sql_scalar("select count(*) from events "
                                "where kind = 'phone.binding.requested'")], 1)

    # The sender's step. In production this is the relay, holding the
    # phone_binder key and the carrier credential; here it is one
    # statement, because what is under test is the schema, not the relay.
    psql(f"""update phone_bindings
                set status = 'pending',
                    code_hash = encode(sha256(convert_to('{CODE}', 'UTF8')), 'hex'),
                    code_sent_at = now(),
                    code_expires_at = now() + interval '10 minutes'
              where id = '{bid}'""")

    rc, status, _ = verb(MEM1, f"phone_bind_confirm('{bid}', '000000')")
    check("confirm-wrong-code", "0029 §5: a wrong code refuses",
          status == "refused", f"status={status}")
    expect_value("confirm-attempt-counted", "0029 §1: code_attempts",
                 0, [sql_scalar(f"select code_attempts from phone_bindings "
                                f"where id = '{bid}'")], 1)

    rc, status, _ = verb(MEM2, f"phone_bind_confirm('{bid}', '{CODE}')")
    check("confirm-not-yours", "0029 §5: §18.1, only the member whose ceremony it is",
          status == "refused", f"status={status}")

    rc, status, _ = verb(MEM1, f"phone_bind_confirm('{bid}', '{CODE}')")
    check("confirm-ok", "0029 §5: possession by code, identity by session",
          status == "verified", f"rc={rc} status={status}")
    expect_value("confirm-clears-secret", "0029 §5: the code does not outlive the ceremony",
                 0, [sql_scalar(f"select count(*) from phone_bindings "
                                f"where id = '{bid}' and code_hash is null")], 1)

    # ---------------------------------------------------------------
    # 4 · the secret the member may not read.
    # ---------------------------------------------------------------
    rc, lines, _ = as_member(MEM1, "select code_hash from phone_bindings")
    expect_deny("code-hash-withheld", "0029 §3: column privilege, as profiles.email",
                rc, lines)
    rc, lines, _ = as_member(MEM1, "select count(*) from phone_bindings")
    expect_value("self-read-own", "0029 §4: §18.1 own record", rc, lines, 1)
    rc, lines, _ = as_member(MEM3, "select count(*) from phone_bindings")
    expect_value("self-read-not-others", "0029 §4: and only their own", rc, lines, 0)

    # ---------------------------------------------------------------
    # 5 · no hand on the table itself.
    # ---------------------------------------------------------------
    rc, lines, _ = as_member(MEM1, f"update phone_bindings set status = 'verified' "
                                   f"where id = '{bid}' returning 1")
    check("no-direct-update", "0029 §4: every member write goes through a verb",
          rc != 0 or len(lines) == 0, f"rc={rc} rows={len(lines)}")
    rc, lines, _ = as_member(MEM1, f"insert into phone_bindings "
                                   f"(agent_id, peer_e164, status, origin) values "
                                   f"('{MEM1}', '{FRESH}', 'verified', 'intranet') returning 1")
    check("no-direct-insert", "0029 §4: a member cannot mint their own binding",
          rc != 0 or len(lines) == 0, f"rc={rc} rows={len(lines)}")
    rc, status, _ = verb(MEM1, f"phone_bind_request('{FRESH}')")
    check("one-live-binding", "0029 §2: one live binding per member",
          status == "refused", f"status={status}")

    # ---------------------------------------------------------------
    # 6 · the member reads their own messages, and the window closes.
    # ---------------------------------------------------------------
    psql(f"""insert into phone_events (occurred_at, direction, peer_e164, content) values
             (now() - interval '1 hour', 'in',  '{CEREMONY}', 'before the binding'),
             (now(),                     'in',  '{CEREMONY}', 'inside the binding'),
             (now(),                     'in',  '{LEGACY_A}', 'someone else entirely')""")
    rc, lines, _ = as_member(MEM1, "select count(*) from phone_events")
    expect_value("events-self-read", "0029 §4: §18.1, the log has no agent column",
                 rc, lines, 1)
    rc, lines, _ = as_member(MEM3, "select count(*) from phone_events")
    expect_value("events-not-others", "0029 §4: an unbound member reads nothing",
                 rc, lines, 0)
    rc, lines, _ = as_member(MEM1, "select payload from phone_events")
    expect_deny("events-payload-withheld", "0029 §3: the envelope is not the correspondence",
                rc, lines)

    # ---------------------------------------------------------------
    # 7 · revocation, and a number that changes hands.
    # ---------------------------------------------------------------
    rc, status, _ = verb(MEM1, f"phone_bind_revoke('{bid}')")
    check("revoke-ok", "0029 §5: turning the channel off is never the dangerous direction",
          status == "revoked", f"rc={rc} status={status}")
    psql(f"""insert into phone_events (occurred_at, direction, peer_e164, content)
             values (now(), 'in', '{CEREMONY}', 'after the revocation')""")
    rc, lines, _ = as_member(MEM1, "select count(*) from phone_events")
    expect_value("events-window-closes", "0029 §4: the window is closed at both ends",
                 rc, lines, 1)

    rc, status, _ = verb(MEM2, f"phone_bind_request('{CEREMONY}')")
    check("rebind-after-revoke", "0029 §5: a revoked number is free again",
          status == "requested", f"status={status}")
    bid2 = sql_scalar(f"select id from phone_bindings where peer_e164 = '{CEREMONY}' "
                      f"and agent_id = '{MEM2}'")
    psql(f"""update phone_bindings
                set status = 'pending',
                    code_hash = encode(sha256(convert_to('{CODE}', 'UTF8')), 'hex'),
                    code_expires_at = now() + interval '10 minutes'
              where id = '{bid2}'""")
    rc, status, _ = verb(MEM2, f"phone_bind_confirm('{bid2}', '{CODE}')")
    check("rebind-verified", "0029 §5: the second holder's own ceremony",
          status == "verified", f"status={status}")
    rc, lines, _ = as_member(MEM2, "select count(*) from phone_events")
    expect_value("no-inherited-history", "0029 §4: the new holder inherits nothing",
                 rc, lines, 0)
    rc, lines, _ = as_member(MEM1, "select count(*) from phone_events")
    expect_value("history-kept", "0029 §4: and the old holder loses nothing",
                 rc, lines, 1)

    # ---------------------------------------------------------------
    # 8 · the rate limit on code sends.
    # ---------------------------------------------------------------
    for i in range(3):
        verb(MEM3, f"phone_bind_request('{FRESH}')")
    rc, reason, _ = verb_reason(MEM3, f"phone_bind_request('{FRESH}')")
    check("number-rate-limit", "0029 §5: three per number per day (#247 question 3)",
          reason == "number_rate_limit", f"reason={reason}")

    # ---------------------------------------------------------------
    # 9 · preservation again, at the end rather than the beginning.
    #     Everything above ran; the two rows that were here first are
    #     still here, still verified, still routing.
    # ---------------------------------------------------------------
    rc, lines, _ = as_router("select count(*) from phone_bindings where agent_id is null")
    expect_value("preserve-at-the-end", "0029 §6: no backfill, no orphan", rc, lines, 2)

    print(f"sms05-probe: {COUNT} probes, {len(FAILURES)} failure(s)")
    for pid, cite, got in FAILURES:
        print(f"FAIL {pid} [{cite}] {got}")
    sys.exit(1 if FAILURES else 0)


if __name__ == "__main__":
    main()
