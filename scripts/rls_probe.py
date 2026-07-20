#!/usr/bin/env python3
"""RLS probe matrix (X-08) -- AM v0.1 section 5, VS v1 section 2.

Stands a fresh substrate, applies the policy chain, seeds a fixture
cast, then probes every cell of the AM v0.1 section 5 matrix: each
role against each of the thirteen launch tables, plus the
capital_accounts caption, the role_grants addendum (AM v0.1 section
9), and the anon column. Every probe cites its cell or anchor.

Probe discipline:
- Cells state guarantees, scoped by the policies of section 6 and the
  write paths of section 7 (the matrix lead says so). Positive probes
  assert stated capabilities; negative probes assert the boundaries an
  anchor names: the anon column, cross-agent visibility on self cells,
  and writes the anchors assign to a narrower hand (stock to the
  Secretary per 4.5(e), agreements to officers per 4.5(b), attendance
  to recorder per 2.7, membership lifecycle to director or steward
  per 1.7 and 1.8).
- Every write probe runs inside a transaction and rolls back: the
  fixture state is identical for every probe, and order carries no
  meaning.
- Supabase's auth.uid() is shimmed to a transaction-local GUC
  (app.uid); policies and definer functions run unmodified.

Runs in CI against the postgres:16 service (PGURL) and locally
against any empty postgres database.
"""
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PGURL = os.environ.get("PGURL", "postgresql://postgres:postgres@localhost:5432/postgres")

# ---------- fixture cast (fixed UUIDs; auth_user_id = agent id) ----------
APP  = "00000000-0000-4000-8000-000000000001"   # applicant (membership: applied)
MEM1 = "00000000-0000-4000-8000-000000000002"   # member; host; author; shareholder
MEM2 = "00000000-0000-4000-8000-000000000003"   # member; registrant; responder; signer
MEM3 = "00000000-0000-4000-8000-000000000004"   # member, plain
DIR  = "00000000-0000-4000-8000-000000000005"   # director (role grant only)
SEC  = "00000000-0000-4000-8000-000000000006"   # secretary
TRE  = "00000000-0000-4000-8000-000000000007"   # treasurer
STE  = "00000000-0000-4000-8000-000000000008"   # steward

AGR  = "00000000-0000-4000-8000-000000000101"   # the seeded agreement
GAT  = "00000000-0000-4000-8000-000000000201"   # gathering hosted by MEM1
SES  = "00000000-0000-4000-8000-000000000202"   # its session
OPP  = "00000000-0000-4000-8000-000000000301"   # opportunity authored by MEM1

BOOTSTRAP = """
create role anon nologin;
create role authenticated nologin;
create schema auth;
create function auth.uid() returns uuid
language sql stable as
$$ select nullif(current_setting('app.uid', true), '')::uuid $$;
"""

SEED = f"""
insert into agents (id, kind, display_name) values
  ('{APP}',  'person', 'Probe Applicant'),
  ('{MEM1}', 'person', 'Probe Member One'),
  ('{MEM2}', 'person', 'Probe Member Two'),
  ('{MEM3}', 'person', 'Probe Member Three'),
  ('{DIR}',  'person', 'Probe Director'),
  ('{SEC}',  'person', 'Probe Secretary'),
  ('{TRE}',  'person', 'Probe Treasurer'),
  ('{STE}',  'person', 'Probe Steward');
update agents set auth_user_id = id;

insert into memberships (agent_id, state) values
  ('{APP}',  'applied'),
  ('{MEM1}', 'active'),
  ('{MEM2}', 'active'),
  ('{MEM3}', 'active');

insert into role_grants (agent_id, role) values
  ('{DIR}', 'director'),
  ('{SEC}', 'secretary'),
  ('{TRE}', 'treasurer'),
  ('{STE}', 'steward');

insert into agreements (id, code, title, version, effective_date) values
  ('{AGR}', 'PROBE-BYLAWS', 'Probe Bylaws', 'v1', '2026-07-01');

insert into stock_ledger (agent_id) values ('{MEM1}');

insert into applications (agent_id, note) values ('{APP}', 'probe application');

insert into gatherings (id, title, host_agent_id) values
  ('{GAT}', 'Probe Gathering', '{MEM1}');
insert into sessions (id, gathering_id, starts_at) values
  ('{SES}', '{GAT}', '2026-08-14T19:00:00Z');
insert into registrations (session_id, agent_id) values ('{SES}', '{MEM2}');
insert into attendance (session_id, agent_id, recorded_by) values
  ('{SES}', '{MEM2}', '{MEM1}');

insert into opportunities (id, author_agent_id, kind, title) values
  ('{OPP}', '{MEM1}', 'work', 'Probe Opportunity');
insert into responses (opportunity_id, agent_id, note) values
  ('{OPP}', '{MEM2}', 'probe response');

insert into signatures (agent_id, agreement_id) values ('{MEM2}', '{AGR}');

insert into events (occurred_at, actor_agent_id, kind, agent_id, book_delta, tax_delta) values
  (now(), '{STE}', 'capital.contribution', '{MEM1}', 100.00, 100.00),
  (now(), '{STE}', 'capital.contribution', '{MEM2}', 250.00, 250.00);
insert into events (occurred_at, actor_agent_id, kind, agent_id) values
  (now(), '{STE}', 'membership.applied', '{APP}');
"""

MIGRATIONS = [
    "commons/im/0001_substrate.sql",
    "commons/authority-map/0002_policies.sql",
    "commons/authority-map/0003_sign_agreement.sql",
    "commons/authority-map/0005_matrix_conformance.sql",
]


def psql(sql, quiet=True):
    """Run sql through psql; return (returncode, data_lines, stderr)."""
    cmd = ["psql", PGURL, "-v", "ON_ERROR_STOP=1", "-q", "-t", "-A", "-f", "-"]
    r = subprocess.run(cmd, input=sql, capture_output=True, text=True)
    lines = [l for l in r.stdout.splitlines() if l.strip()]
    return r.returncode, lines, r.stderr


def run_probe(persona_role, uid, sql):
    script = "begin;\n"
    if uid:
        script += f"select set_config('app.uid', '{uid}', true);\n"
    script += f"set local role {persona_role};\n{sql};\nrollback;"
    rc, lines, err = psql(script)
    # the set_config select emits one data line; drop it
    if uid and lines:
        lines = lines[1:]
    return rc, lines, err


# ---------- the probe register ----------
# (id, persona, uid, sql, expect, cite)
# expect: ('count', n) exact | ('count>=', n) | ('write_ok',) needs a
# RETURNING row | ('write_deny',) error or zero rows | ('deny',) error.
P = []

def probe(pid, role, uid, sql, expect, cite):
    P.append((pid, role, uid, sql, expect, cite))

# ---- anon: reads nothing anywhere (section 5 caption; Art. XV) ----
for t in ["agents", "agreements", "memberships", "stock_ledger", "signatures",
          "applications", "events", "gatherings", "sessions", "registrations",
          "attendance", "opportunities", "responses", "capital_accounts"]:
    probe(f"anon-{t}", "anon", None, f"select count(*) from {t}",
          ("deny",), "s5 caption: public reads nothing; Art. XV")

# ---- agents: - | self | R, self W | R | R | R ----
probe("agents-applicant-self", "authenticated", APP,
      "select count(*) from agents", ("count", 1), "s5 agents/applicant: self; 18.1")
probe("agents-member-read", "authenticated", MEM1,
      "select count(*) from agents", ("count", 8), "s5 agents/member: R; 2.9")
probe("agents-member-self-update", "authenticated", MEM1,
      f"update agents set display_name = 'Probe One Renamed' where id = '{MEM1}' returning 1",
      ("write_ok",), "s5 agents/member: self W; 1.13")
probe("agents-member-cross-update", "authenticated", MEM1,
      f"update agents set display_name = 'x' where id = '{MEM2}' returning 1",
      ("write_deny",), "s5 agents/member: self W only; 1.13")
for r, uid in [("director", DIR), ("officer", SEC), ("steward", STE)]:
    probe(f"agents-{r}-read", "authenticated", uid,
          "select count(*) from agents", ("count", 8), f"s5 agents/{r}: R; 2.9")

# ---- agreements: - | R | R | R | R, W | R ----
for r, uid in [("applicant", APP), ("member", MEM1), ("director", DIR),
               ("officer", SEC), ("steward", STE)]:
    probe(f"agreements-{r}-read", "authenticated", uid,
          "select count(*) from agreements", ("count", 1),
          f"s5 agreements/{r}: R; Art. XVI, 1.2.9")
probe("agreements-secretary-write", "authenticated", SEC,
      f"update agreements set title = 'Probe Bylaws (amended)' where id = '{AGR}' returning 1",
      ("write_ok",), "s5 agreements/officer: W; 4.5(b)")
probe("agreements-treasurer-write", "authenticated", TRE,
      f"update agreements set title = 'Probe Bylaws (amended)' where id = '{AGR}' returning 1",
      ("write_ok",), "s5 agreements/officer: W; 4.5(b), app_is_officer")
for r, uid in [("member", MEM1), ("director", DIR), ("steward", STE)]:
    probe(f"agreements-{r}-write-deny", "authenticated", uid,
          f"update agreements set title = 'x' where id = '{AGR}' returning 1",
          ("write_deny",), "s5 agreements: W is the officer's; 4.5(b)")

# ---- memberships: - | self | R | R, W | R | R, W ----
probe("memberships-applicant-self", "authenticated", APP,
      "select count(*) from memberships", ("count", 1), "s5 memberships/applicant: self; 18.1")
for r, uid in [("member", MEM1), ("director", DIR), ("officer", SEC), ("steward", STE)]:
    probe(f"memberships-{r}-read", "authenticated", uid,
          "select count(*) from memberships", ("count", 4), f"s5 memberships/{r}: R; 2.9")
for r, uid in [("director", DIR), ("steward", STE)]:
    probe(f"memberships-{r}-write", "authenticated", uid,
          f"update memberships set state = 'suspended' where agent_id = '{MEM3}' returning 1",
          ("write_ok",), f"s5 memberships/{r}: W; 1.7, 1.8")
probe("memberships-officer-write-deny", "authenticated", SEC,
      f"update memberships set state = 'suspended' where agent_id = '{MEM3}' returning 1",
      ("write_deny",), "s5 memberships/officer: R only; 1.7, 1.8 assign lifecycle to Board and steward")
probe("memberships-member-write-deny", "authenticated", MEM1,
      f"update memberships set state = 'withdrawn' where agent_id = '{MEM1}' returning 1",
      ("write_deny",), "s7: withdrawal lands by notice and recorded actor, not self-service row edit; 1.7.1")

# ---- stock_ledger: - | - | self | R | R, W | - ----
probe("stock-applicant-none", "authenticated", APP,
      "select count(*) from stock_ledger", ("count", 0), "s5 stock/applicant: -")
probe("stock-member-self", "authenticated", MEM1,
      "select count(*) from stock_ledger", ("count", 1), "s5 stock/member: self; 1.11")
probe("stock-member-cross-none", "authenticated", MEM3,
      "select count(*) from stock_ledger", ("count", 0), "s5 stock/member: self only; 1.6")
for r, uid in [("director", DIR), ("secretary", SEC), ("treasurer", TRE)]:
    probe(f"stock-{r}-read", "authenticated", uid,
          "select count(*) from stock_ledger", ("count", 1), f"s5 stock: Board and officers read; 1.11")
probe("stock-steward-none", "authenticated", STE,
      "select count(*) from stock_ledger", ("count", 0), "s5 stock/steward: -")
probe("stock-secretary-write", "authenticated", SEC,
      f"insert into stock_ledger (agent_id) values ('{MEM2}') returning 1",
      ("write_ok",), "s5 stock/officer: W, scoped to the Secretary by 4.5(e)")
probe("stock-treasurer-write-deny", "authenticated", TRE,
      f"insert into stock_ledger (agent_id) values ('{MEM3}') returning 1",
      ("write_deny",), "s6 stock custody: written by the Secretary who keeps the transfer books; 4.5(e)")
probe("stock-member-write-deny", "authenticated", MEM2,
      f"insert into stock_ledger (agent_id) values ('{MEM2}') returning 1",
      ("write_deny",), "s5 stock/member: self read only")

# ---- signatures: - | self W | self, self W | R | R | - ----
probe("signatures-applicant-write", "authenticated", APP,
      f"insert into signatures (agent_id, agreement_id) values ('{APP}', '{AGR}') returning 1",
      ("write_ok",), "s5 signatures/applicant: self W; 1.3.1(d)")
probe("signatures-applicant-cross-none", "authenticated", APP,
      f"select count(*) from signatures where agent_id = '{MEM2}'", ("count", 0),
      "s5 signatures: self means the row concerns the asker")
probe("signatures-member-self", "authenticated", MEM2,
      "select count(*) from signatures", ("count", 1), "s5 signatures/member: self; 2.8")
probe("signatures-member-write", "authenticated", MEM1,
      f"insert into signatures (agent_id, agreement_id) values ('{MEM1}', '{AGR}') returning 1",
      ("write_ok",), "s5 signatures/member: self W; 1.3.1(d)")
probe("signatures-member-forge-deny", "authenticated", MEM1,
      f"insert into signatures (agent_id, agreement_id) values ('{MEM2}', '{AGR}') returning 1",
      ("write_deny",), "s7: signing is the signer's act; 1.3.1(d), 2.8")
probe("signatures-director-read", "authenticated", DIR,
      "select count(*) from signatures", ("count", 1), "s5 signatures/director: R")
probe("signatures-officer-read", "authenticated", SEC,
      "select count(*) from signatures", ("count", 1), "s5 signatures/officer: R")
probe("signatures-steward-none", "authenticated", STE,
      "select count(*) from signatures", ("count", 0), "s5 signatures/steward: -")

# ---- applications: - | self, self W | self | R | R | R, W ----
probe("applications-applicant-self", "authenticated", APP,
      "select count(*) from applications", ("count", 1), "s5 applications/applicant: self; 1.3.1(d)")
probe("applications-applicant-write", "authenticated", APP,
      f"insert into applications (agent_id, note) values ('{APP}', 'second probe') returning 1",
      ("write_ok",), "s5 applications/applicant: self W; 1.2")
probe("applications-member-none", "authenticated", MEM1,
      "select count(*) from applications", ("count", 0), "s5 applications/member: self (has none)")
for r, uid in [("director", DIR), ("officer", SEC), ("steward", STE)]:
    probe(f"applications-{r}-read", "authenticated", uid,
          "select count(*) from applications", ("count", 1), f"s5 applications/{r}: R; 1.3.3")
probe("applications-steward-write", "authenticated", STE,
      "update applications set note = 'reviewed by steward probe' returning 1",
      ("write_ok",), "s5 applications/steward: W; 1.3.3 intake")
probe("applications-officer-write-deny", "authenticated", SEC,
      "update applications set note = 'x' returning 1",
      ("write_deny",), "s5 applications/officer: R only; intake is the steward's, decision the Board's; 1.3.3, 1.7")

# ---- events: - | - | self, scoped W | R | R | R, W ----
probe("events-applicant-cross-none", "authenticated", APP,
      f"select count(*) from events where agent_id = '{MEM2}'", ("count", 0),
      "s5 events/applicant: -; 18.1 grants only own record")
probe("events-member-self", "authenticated", MEM1,
      f"select count(*) from events where agent_id = '{MEM1}'", ("count", 1),
      "s5 events/member: self; 18.1, 6.2.1")
probe("events-member-cross-none", "authenticated", MEM1,
      f"select count(*) from events where agent_id = '{MEM2}'", ("count", 0),
      "s5 events/member: self only; 18.2")
probe("events-member-scoped-write", "authenticated", MEM1,
      f"insert into events (occurred_at, actor_agent_id, kind, agent_id) "
      f"values (now(), '{MEM1}', 'registration.registered', '{MEM1}') returning 1",
      ("write_ok",), "s5 events/member: scoped W; Laws II and X, s7 member-actionable kinds")
probe("events-member-kind-deny", "authenticated", MEM1,
      f"insert into events (occurred_at, actor_agent_id, kind, agent_id) "
      f"values (now(), '{MEM1}', 'membership.applied', '{MEM1}') returning 1",
      ("write_deny",), "s7: membership acts belong to the Board and steward; 1.3, 1.7")
probe("events-member-actor-deny", "authenticated", MEM1,
      f"insert into events (occurred_at, actor_agent_id, kind, agent_id) "
      f"values (now(), '{MEM2}', 'registration.registered', '{MEM2}') returning 1",
      ("write_deny",), "s7: the recorded actor is the asker; Law X")
for r, uid in [("director", DIR), ("officer", SEC), ("steward", STE)]:
    probe(f"events-{r}-read", "authenticated", uid,
          "select count(*) from events", ("count>=", 3), f"s5 events/{r}: R; 3.1, 4.4, 4.1")
probe("events-steward-write", "authenticated", STE,
      f"insert into events (occurred_at, actor_agent_id, kind, agent_id) "
      f"values (now(), '{STE}', 'membership.applied', '{APP}') returning 1",
      ("write_ok",), "s5 events/steward: W; s7 overseer acts")

# ---- gatherings: - | - | R, host W | R | R | R, W ----
probe("gatherings-applicant-none", "authenticated", APP,
      "select count(*) from gatherings", ("count", 0), "s5 gatherings/applicant: -")
for r, uid in [("member", MEM3), ("director", DIR), ("officer", SEC), ("steward", STE)]:
    probe(f"gatherings-{r}-read", "authenticated", uid,
          "select count(*) from gatherings", ("count", 1), f"s5 gatherings/{r}: R; 2.1")
probe("gatherings-host-write", "authenticated", MEM1,
      f"update gatherings set title = 'Probe Gathering (renamed)' where id = '{GAT}' returning 1",
      ("write_ok",), "s5 gatherings/member: host W; 2.1")
probe("gatherings-nonhost-write-deny", "authenticated", MEM2,
      f"update gatherings set title = 'x' where id = '{GAT}' returning 1",
      ("write_deny",), "s5 gatherings: host W means the host; 2.1")
probe("gatherings-steward-write", "authenticated", STE,
      f"update gatherings set title = 'Probe Gathering (steward)' where id = '{GAT}' returning 1",
      ("write_ok",), "s5 gatherings/steward: W; 2.1 the steward may act as host")
probe("gatherings-director-write-deny", "authenticated", DIR,
      f"update gatherings set title = 'x' where id = '{GAT}' returning 1",
      ("write_deny",), "s5 gatherings/director: R only; 2.1 keeps the calendar with hosts and steward")

# ---- sessions: - | - | R, host W | R | R | R, W ----
probe("sessions-applicant-none", "authenticated", APP,
      "select count(*) from sessions", ("count", 0), "s5 sessions/applicant: -")
for r, uid in [("member", MEM3), ("director", DIR), ("officer", SEC), ("steward", STE)]:
    probe(f"sessions-{r}-read", "authenticated", uid,
          "select count(*) from sessions", ("count", 1), f"s5 sessions/{r}: R; 2.1")
probe("sessions-host-write", "authenticated", MEM1,
      f"insert into sessions (gathering_id, starts_at) values ('{GAT}', now()) returning 1",
      ("write_ok",), "s5 sessions/member: host W; 2.1")
probe("sessions-nonhost-write-deny", "authenticated", MEM2,
      f"insert into sessions (gathering_id, starts_at) values ('{GAT}', now()) returning 1",
      ("write_deny",), "s5 sessions: host W means the host; 2.1")
probe("sessions-steward-write", "authenticated", STE,
      f"insert into sessions (gathering_id, starts_at) values ('{GAT}', now()) returning 1",
      ("write_ok",), "s5 sessions/steward: W; 2.1")
probe("sessions-director-write-deny", "authenticated", DIR,
      f"insert into sessions (gathering_id, starts_at) values ('{GAT}', now()) returning 1",
      ("write_deny",), "s5 sessions/director: R only; 2.1")

# ---- registrations: - | - | self, self W, host R | R | R | R ----
probe("registrations-member-self", "authenticated", MEM2,
      "select count(*) from registrations", ("count", 1), "s5 registrations/member: self")
probe("registrations-member-cross-none", "authenticated", MEM3,
      "select count(*) from registrations", ("count", 0), "s5 registrations/member: self; 18.2")
probe("registrations-host-read", "authenticated", MEM1,
      "select count(*) from registrations", ("count", 1), "s5 registrations/member: host R; 2.1")
probe("registrations-member-write", "authenticated", MEM3,
      f"insert into registrations (session_id, agent_id) values ('{SES}', '{MEM3}') returning 1",
      ("write_ok",), "s5 registrations/member: self W; PRD v0.3 s4 Gather")
probe("registrations-member-cancel", "authenticated", MEM2,
      f"update registrations set state = 'cancelled' where agent_id = '{MEM2}' returning 1",
      ("write_ok",), "s5 registrations/member: self W; PRD v0.3 s4 Gather")
probe("registrations-applicant-write-deny", "authenticated", APP,
      f"insert into registrations (session_id, agent_id) values ('{SES}', '{APP}') returning 1",
      ("write_deny",), "s5 registrations/applicant: -; registration is a member capability")
probe("registrations-steward-write-deny", "authenticated", STE,
      f"insert into registrations (session_id, agent_id) values ('{SES}', '{STE}') returning 1",
      ("write_deny",), "s5 registrations/steward: R only; self W requires membership")
for r, uid in [("director", DIR), ("officer", SEC), ("steward", STE)]:
    probe(f"registrations-{r}-read", "authenticated", uid,
          "select count(*) from registrations", ("count", 1), f"s5 registrations/{r}: R")

# ---- attendance: - | - | self, host W | R | R | R, W ----
probe("attendance-member-self", "authenticated", MEM2,
      "select count(*) from attendance", ("count", 1), "s5 attendance/member: self; 2.7")
probe("attendance-member-cross-none", "authenticated", MEM3,
      "select count(*) from attendance", ("count", 0), "s5 attendance/member: self; 18.2")
probe("attendance-host-write", "authenticated", MEM1,
      f"insert into attendance (session_id, agent_id, recorded_by) values ('{SES}', '{MEM3}', '{MEM1}') returning 1",
      ("write_ok",), "s5 attendance/member: host W; 2.7")
probe("attendance-self-report-deny", "authenticated", MEM3,
      f"insert into attendance (session_id, agent_id, recorded_by) values ('{SES}', '{MEM3}', '{MEM3}') returning 1",
      ("write_deny",), "s6 gather paths: recorded by host or steward, not self-reported; 2.7")
probe("attendance-steward-write", "authenticated", STE,
      f"insert into attendance (session_id, agent_id, recorded_by) values ('{SES}', '{MEM3}', '{STE}') returning 1",
      ("write_ok",), "s5 attendance/steward: W; 2.7")
probe("attendance-director-write-deny", "authenticated", DIR,
      f"insert into attendance (session_id, agent_id, recorded_by) values ('{SES}', '{MEM3}', '{DIR}') returning 1",
      ("write_deny",), "s5 attendance/director: R only; 2.7 assigns recording to host and steward")
for r, uid in [("director", DIR), ("officer", SEC)]:
    probe(f"attendance-{r}-read", "authenticated", uid,
          "select count(*) from attendance", ("count", 1), f"s5 attendance/{r}: R")

# ---- opportunities: - | - | R, author W | R | R | R ----
probe("opportunities-applicant-none", "authenticated", APP,
      "select count(*) from opportunities", ("count", 0), "s5 opportunities/applicant: -")
for r, uid in [("member", MEM3), ("director", DIR), ("officer", SEC), ("steward", STE)]:
    probe(f"opportunities-{r}-read", "authenticated", uid,
          "select count(*) from opportunities", ("count", 1), f"s5 opportunities/{r}: R; PRD v0.3 s4 Find")
probe("opportunities-author-write", "authenticated", MEM1,
      f"update opportunities set title = 'Probe Opportunity (revised)' where id = '{OPP}' returning 1",
      ("write_ok",), "s5 opportunities/member: author W")
probe("opportunities-nonauthor-write-deny", "authenticated", MEM2,
      f"update opportunities set title = 'x' where id = '{OPP}' returning 1",
      ("write_deny",), "s5 opportunities: author W means the author")
probe("opportunities-steward-write-deny", "authenticated", STE,
      f"update opportunities set title = 'x' where id = '{OPP}' returning 1",
      ("write_deny",), "s5 opportunities/steward: R only")
probe("opportunities-member-post", "authenticated", MEM3,
      f"insert into opportunities (author_agent_id, kind, title) values ('{MEM3}', 'play', 'Probe Post') returning 1",
      ("write_ok",), "s5 opportunities/member: author W; PRD v0.3 s4")
probe("opportunities-applicant-post-deny", "authenticated", APP,
      f"insert into opportunities (author_agent_id, kind, title) values ('{APP}', 'play', 'x') returning 1",
      ("write_deny",), "s5 opportunities/applicant: -")

# ---- responses: - | - | scoped R, self W | R | R | R ----
probe("responses-responder-read", "authenticated", MEM2,
      "select count(*) from responses", ("count", 1), "s5 responses/member: scoped R (responder)")
probe("responses-author-read", "authenticated", MEM1,
      "select count(*) from responses", ("count", 1), "s5 caption: responder and the opportunity's author; 18.2")
probe("responses-third-none", "authenticated", MEM3,
      "select count(*) from responses", ("count", 0), "s5 responses/member: scoped; 18.2")
probe("responses-member-write", "authenticated", MEM3,
      f"insert into responses (opportunity_id, agent_id, note) values ('{OPP}', '{MEM3}', 'probe') returning 1",
      ("write_ok",), "s5 responses/member: self W; 18.2")
probe("responses-applicant-write-deny", "authenticated", APP,
      f"insert into responses (opportunity_id, agent_id, note) values ('{OPP}', '{APP}', 'x') returning 1",
      ("write_deny",), "s5 responses/applicant: -")
for r, uid in [("director", DIR), ("officer", SEC), ("steward", STE)]:
    probe(f"responses-{r}-read", "authenticated", uid,
          "select count(*) from responses", ("count", 1), f"s5 responses/{r}: R")

# ---- capital_accounts: the caption; folds only what events shows ----
probe("capital-member-self-only", "authenticated", MEM1,
      f"select count(*) from capital_accounts", ("count", 1),
      "s5 caption: the capital view folds only what the events policy already shows the asker; 18.1, 6.2.1")
probe("capital-member-own-row", "authenticated", MEM1,
      f"select count(*) from capital_accounts where agent_id = '{MEM1}'", ("count", 1),
      "s6 capital views: a member's fold is theirs; 5.1")
probe("capital-director-all", "authenticated", DIR,
      "select count(*) from capital_accounts", ("count", 2),
      "s6 capital views: the Board and Treasurer read all; 5.3, 4.4")
probe("capital-applicant-none", "authenticated", APP,
      "select count(*) from capital_accounts", ("count", 0),
      "s5 caption; an applicant has no capital events")

# ---- role_grants (AM v0.1 s9 addendum) ----
probe("rolegrants-member-read", "authenticated", MEM1,
      "select count(*) from role_grants", ("count", 4),
      "s9: offices are public inside the cooperative; 3.1, 4.1")
probe("rolegrants-steward-self", "authenticated", STE,
      "select count(*) from role_grants", ("count", 1),
      "role_grants_member_read: a non-member role holder sees their own grant")
probe("rolegrants-director-write", "authenticated", DIR,
      f"insert into role_grants (agent_id, role) values ('{MEM3}', 'steward') returning 1",
      ("write_ok",), "3.8: the Board elects; recording the grant is a directorial write")
probe("rolegrants-steward-write-deny", "authenticated", STE,
      f"insert into role_grants (agent_id, role) values ('{MEM3}', 'steward') returning 1",
      ("write_deny",), "3.8: grants are written by directors")
probe("rolegrants-member-write-deny", "authenticated", MEM1,
      f"insert into role_grants (agent_id, role) values ('{MEM1}', 'director') returning 1",
      ("write_deny",), "3.8: grants are written by directors")


def main():
    # ---------- stand the environment ----------
    rc, _, err = psql(BOOTSTRAP)
    if rc != 0:
        print(f"bootstrap failed:\n{err}", file=sys.stderr); sys.exit(1)
    for m in MIGRATIONS:
        rc, _, err = psql((REPO_ROOT / m).read_text())
        if rc != 0:
            print(f"migration {m} failed:\n{err}", file=sys.stderr); sys.exit(1)
    rc, _, err = psql(SEED)
    if rc != 0:
        print(f"seed failed:\n{err}", file=sys.stderr); sys.exit(1)

    # ---------- probe ----------
    failures = []
    for pid, role, uid, sql, expect, cite in P:
        rc, lines, err = run_probe(role, uid, sql)
        kind = expect[0]
        if kind == "count":
            ok = rc == 0 and lines and lines[0].isdigit() and int(lines[0]) == expect[1]
            got = f"rc={rc} rows={lines[:1]}"
        elif kind == "count>=":
            ok = rc == 0 and lines and lines[0].isdigit() and int(lines[0]) >= expect[1]
            got = f"rc={rc} rows={lines[:1]}"
        elif kind == "write_ok":
            ok = rc == 0 and len(lines) >= 1
            got = f"rc={rc} returned={len(lines)}"
        elif kind == "write_deny":
            ok = rc != 0 or len(lines) == 0
            got = f"rc={rc} returned={len(lines)}"
        elif kind == "deny":
            ok = rc != 0
            got = f"rc={rc}"
        else:
            ok, got = False, f"unknown expectation {kind}"
        if not ok:
            failures.append((pid, cite, got, err.strip().splitlines()[-1:] if err else []))

    print(f"rls-probe: {len(P)} probes, {len(failures)} failure(s)")
    for pid, cite, got, err in failures:
        print(f"FAIL {pid} [{cite}] {got} {err}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
