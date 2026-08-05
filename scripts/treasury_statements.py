#!/usr/bin/env python3
"""
treasury_statements.py · T-07 · the statements runner

Generates the monthly statement snapshot the statements view renders
(TR §9a): read-only pulls from Xero (the accrual authority), Stripe
(the processor), Mercury (the bank rail), and the Safe (on-chain,
keyless), assembled into one aggregate payload per month and upserted
into treasury_statements (0019).

Read-only by construction: every credential this runner holds can only
read. It writes one place, the statements store, which is an
observation table beside the record, never the events log (TR §9).
Payloads carry organization aggregates only: no member names, ids, or
per-member amounts (the §9a member cut).

Usage:
  python3 scripts/treasury_statements.py 2026-05 2026-06 2026-07
  RAILS_ENV=... NOTICES_ENV=... to override the credential stores.

Credentials (never in this repository):
  rails store   MERCURY_TOKEN, STRIPE_KEY, XERO_CLIENT_ID, XERO_CLIENT_SECRET
  notices store SUPABASE_ACCESS_TOKEN (management channel, the only writer)

Authored-by: build-agent / T-07
"""

import base64
import calendar
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

RAILS_ENV = os.environ.get("RAILS_ENV", os.path.expanduser("~/.config/secrets/techne-rails.env.gpg"))
NOTICES_ENV = os.environ.get("NOTICES_ENV", os.path.expanduser("~/.config/secrets/techne-notices.env.gpg"))
SUPABASE_PROJECT = "ujujwgopdwirebgcpekc"
SAFE_ADDRESS = "0xA594263e0449A28eAEf5BA6420E81cC1996b7782"


def load_env(path):
    out = subprocess.run(["gpg", "-d", path], capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"cannot decrypt {path}")
    return dict(line.split("=", 1) for line in out.stdout.strip().split("\n") if "=" in line)


def http_json(url, headers=None, data=None, ipv4=False, timeout=45):
    # Mercury's token is IP-whitelisted to this host's IPv4; curl -4 pins the route.
    if ipv4:
        cmd = ["curl", "-4", "-s", "--max-time", str(timeout), url]
        for k, v in (headers or {}).items():
            cmd += ["-H", f"{k}: {v}"]
        return json.loads(subprocess.run(cmd, capture_output=True, text=True).stdout)
    req = urllib.request.Request(url, data=data, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def month_bounds(month):
    y, m = int(month[:4]), int(month[5:7])
    last = calendar.monthrange(y, m)[1]
    return f"{y:04d}-{m:02d}-01", f"{y:04d}-{m:02d}-{last:02d}"


# ---------- Xero: the accrual authority ----------

def xero_token(env):
    basic = base64.b64encode(f"{env['XERO_CLIENT_ID']}:{env['XERO_CLIENT_SECRET']}".encode()).decode()
    d = http_json("https://identity.xero.com/connect/token",
                  headers={"Authorization": f"Basic {basic}",
                           "Content-Type": "application/x-www-form-urlencoded"},
                  data=b"grant_type=client_credentials")
    return d["access_token"]


def xero_report(token, name, params):
    q = urllib.parse.urlencode(params)
    d = http_json(f"https://api.xero.com/api.xro/2.0/Reports/{name}?{q}",
                  headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
    return d["Reports"][0]


def flatten(report):
    rows = []
    def walk(rs, section=""):
        for row in rs:
            title = row.get("Title", "")
            if row.get("Cells"):
                rows.append({"section": section,
                             "cells": [c.get("Value", "") for c in row["Cells"]]})
            if row.get("Rows"):
                walk(row["Rows"], title or section)
    walk(report.get("Rows", []))
    return rows


def totals_of(rows):
    out = {}
    for r in rows:
        head = str(r["cells"][0])
        if head.startswith("Total ") or head in ("Net Profit", "Gross Profit", "Net Assets"):
            try:
                out[head] = float(str(r["cells"][1]).replace(",", ""))
            except (ValueError, IndexError):
                pass
    return out


def read_xero(env, month):
    first, last = month_bounds(month)
    token = xero_token(env)
    pnl = flatten(xero_report(token, "ProfitAndLoss", {"fromDate": first, "toDate": last}))
    bs = flatten(xero_report(token, "BalanceSheet", {"date": last}))
    bank = flatten(xero_report(token, "BankSummary", {"fromDate": first, "toDate": last}))
    custody = []
    for r in bank:
        c = r["cells"]
        if len(c) >= 5 and c[0] and c[0] not in ("Bank Accounts",):
            try:
                custody.append({"account": c[0],
                                "open": float(str(c[1]).replace(",", "")),
                                "in": float(str(c[2]).replace(",", "")),
                                "out": float(str(c[3]).replace(",", "")),
                                "close": float(str(c[4]).replace(",", ""))})
            except ValueError:
                continue
    receivables = xero_receivables(token)
    return {"read_at": now_iso(),
            "receivables": receivables,
            "pnl_totals": totals_of(pnl),
            "pnl_lines": [r for r in pnl if r["section"] in ("Income", "Less Operating Expenses",
                                                             "Operating Expenses", "Expenses",
                                                             "Less Cost of Sales", "Cost of Sales")],
            "position_totals": totals_of(bs),
            "bank_summary": custody}


def xero_receivables(token):
    """Outstanding sales invoices at read time: number, dates, amount due,
    age past due. Contact names are deliberately not stored; the payload is
    member-readable and the section 9a member cut carries no names."""
    q = urllib.parse.quote('Type=="ACCREC" && Status=="AUTHORISED" && AmountDue>0')
    d = http_json(f"https://api.xero.com/api.xro/2.0/Invoices?where={q}",
                  headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
    today = datetime.now(timezone.utc).date()
    out = []
    for inv in d.get("Invoices", []):
        due = (inv.get("DueDateString") or inv.get("DateString") or "")[:10]
        try:
            age = (today - datetime.fromisoformat(due).date()).days
        except ValueError:
            age = None
        out.append({"invoice": inv.get("InvoiceNumber"),
                    "issued": (inv.get("DateString") or "")[:10],
                    "due": due,
                    "amount_due": inv.get("AmountDue"),
                    "days_past_due": age})
    out.sort(key=lambda r: r.get("due") or "")
    return {"as_of": now_iso(), "count": len(out),
            "total_due": round(sum(r["amount_due"] or 0 for r in out), 2),
            "invoices": out}


# ---------- Stripe: the processor ----------

def read_stripe(env, month):
    first, last = month_bounds(month)
    gte = int(datetime.fromisoformat(first + "T00:00:00+00:00").timestamp())
    y, m = int(month[:4]), int(month[5:7])
    nm = f"{y + 1}-01-01" if m == 12 else f"{y}-{m + 1:02d}-01"
    lt = int(datetime.fromisoformat(nm + "T00:00:00+00:00").timestamp())
    headers = {"Authorization": "Bearer " + env["STRIPE_KEY"]}
    by_type, count, starting_after, has_more = {}, 0, None, True
    payments = []
    while has_more:
        url = (f"https://api.stripe.com/v1/balance_transactions?limit=100"
               f"&created[gte]={gte}&created[lt]={lt}")
        if starting_after:
            url += f"&starting_after={starting_after}"
        d = http_json(url, headers=headers)
        for t in d.get("data", []):
            by_type[t["type"]] = by_type.get(t["type"], 0) + t["amount"]
            count += 1
            starting_after = t["id"]
            # itemize member payments: date, gross, fee, net; never a name
            if t["type"] in ("charge", "payment"):
                payments.append({
                    "date": datetime.fromtimestamp(t["created"], tz=timezone.utc).strftime("%Y-%m-%d"),
                    "gross": round(t["amount"] / 100, 2),
                    "fee": round(t["fee"] / 100, 2),
                    "net": round(t["net"] / 100, 2),
                    "kind": (t.get("description") or "payment")[:40]})
        has_more = d.get("has_more", False)
    payments.sort(key=lambda p: p["date"])
    return {"read_at": now_iso(), "transaction_count": count,
            "by_type_usd": {k: round(v / 100, 2) for k, v in sorted(by_type.items())},
            "payments": payments}


# ---------- Mercury: the bank rail ----------

def read_mercury(env, month):
    first, last = month_bounds(month)
    headers = {"Authorization": "Bearer " + env["MERCURY_TOKEN"],
               "User-Agent": "techne-cis-read/1.0"}
    accounts = http_json("https://api.mercury.com/api/v1/accounts",
                         headers=headers, ipv4=True).get("accounts", [])
    out = []
    for a in accounts:
        tx = http_json(f"https://api.mercury.com/api/v1/account/{a['id']}/transactions"
                       f"?start={first}&end={last}&limit=500",
                       headers=headers, ipv4=True).get("transactions", [])
        register = []
        for t in sorted(tx, key=lambda x: x.get("postedAt") or x.get("createdAt") or ""):
            cp = (t.get("counterpartyName") or "").strip()
            # the member cut carries no payer names: inbound counterparties
            # other than the processor are genericized (section 9a)
            if t["amount"] > 0 and "STRIPE" not in cp.upper():
                cp = "inbound payment"
            register.append({"date": (t.get("postedAt") or t.get("createdAt") or "")[:10],
                             "amount": t["amount"], "counterparty": cp[:30]})
        out.append({"account": a.get("name"), "kind": a.get("kind"),
                    "transaction_count": len(tx),
                    "inflow": round(sum(t["amount"] for t in tx if t["amount"] > 0), 2),
                    "outflow": round(sum(-t["amount"] for t in tx if t["amount"] < 0), 2),
                    "balance_at_read": a.get("availableBalance"),
                    "register": register})
    return {"read_at": now_iso(), "accounts": out}


# ---------- Safe: on-chain, keyless, current holdings only ----------

def read_safe():
    holdings = []
    for chain, host in [("mainnet", "safe-transaction-mainnet.safe.global"),
                        ("optimism", "safe-transaction-optimism.safe.global")]:
        try:
            bal = http_json(f"https://{host}/api/v1/safes/{SAFE_ADDRESS}/balances/",
                            headers={"Accept": "application/json"})
            for b in bal:
                tok = b.get("token") or {}
                sym = tok.get("symbol") or "ETH"
                # aggregate the recognized treasury assets; unsolicited airdrop
                # tokens are not holdings and are excluded by symbol allowlist
                if sym not in ("USDC", "DAI", "ETH"):
                    continue
                amount = int(b["balance"]) / 10 ** tok.get("decimals", 18)
                if amount > 0.001:
                    holdings.append({"chain": chain, "asset": sym, "amount": round(amount, 2)})
        except Exception:
            holdings.append({"chain": chain, "asset": "read_failed", "amount": 0})
    return {"read_at": now_iso(), "address": SAFE_ADDRESS, "holdings": holdings,
            "note": "current holdings at read time; month-end on-chain history awaits T-03"}


def safe_transfers(month):
    """The month's on-chain transfers, recognized assets only, with tx hashes
    so every row links its chain's explorer (the institute precedent)."""
    rows = []
    for chain, host, explorer in [
            ("mainnet", "safe-transaction-mainnet.safe.global", "https://etherscan.io/tx/"),
            ("optimism", "safe-transaction-optimism.safe.global", "https://optimistic.etherscan.io/tx/")]:
        try:
            d = http_json(f"https://{host}/api/v1/safes/{SAFE_ADDRESS}/transfers/?limit=100",
                          headers={"Accept": "application/json"})
            for t in d.get("results", []):
                when = (t.get("executionDate") or "")[:10]
                if not when.startswith(month):
                    continue
                tok = t.get("tokenInfo") or {}
                sym = tok.get("symbol") or ("ETH" if t.get("type") == "ETHER_TRANSFER" else "?")
                if sym not in ("USDC", "DAI", "ETH"):
                    continue
                dec = tok.get("decimals", 18)
                amt = round(int(t.get("value") or 0) / 10 ** dec, 2)
                outbound = (t.get("from") or "").lower() == SAFE_ADDRESS.lower()
                other = (t.get("to") if outbound else t.get("from")) or ""
                rows.append({"date": when, "chain": chain, "asset": sym,
                             "amount": -amt if outbound else amt,
                             "counterparty": other[:8] + "\u2026" + other[-4:] if len(other) > 14 else other,
                             "tx": explorer + (t.get("transactionHash") or "")})
        except Exception:
            continue
    rows.sort(key=lambda r: r["date"])
    return rows


# ---------- assemble and store ----------

def build_statement(rails, month):
    return {
        "month": month,
        "generated_at": now_iso(),
        "basis": ("cash observations from the rails; accrual figures are Xero's, cited not "
                  "restated; provisional, no Reconciliation Window attested (TR §8, §9a)"),
        "custody_note": ("custody lines shown separately pending the scoping determination "
                         "(accounting counsel memo AC-03); the sponsor-era account is not "
                         "presumed the cooperative's"),
        "xero": read_xero(rails, month),
        "stripe": read_stripe(rails, month),
        "mercury": read_mercury(rails, month),
        "safe": read_safe(),
        "safe_transfers": safe_transfers(month),
    }


def upsert(notices_env, month, payload):
    sql = ("insert into treasury_statements (month, payload) values (%s, %s::jsonb) "
           "on conflict (month) do update set payload = excluded.payload, "
           "generated_at = now()")
    # the management channel is the only writer; parameters inlined with
    # dollar-quoting because the query endpoint takes one SQL string
    body = sql.replace("%s", "$q$" + month + "$q$", 1).replace(
        "%s", "$j$" + json.dumps(payload) + "$j$", 1)
    r = subprocess.run(
        ["curl", "-s", "-X", "POST",
         f"https://api.supabase.com/v1/projects/{SUPABASE_PROJECT}/database/query",
         "-H", f"Authorization: Bearer {notices_env['SUPABASE_ACCESS_TOKEN']}",
         "-H", "Content-Type: application/json", "-H", "User-Agent: techne-cis",
         "-d", json.dumps({"query": body})],
        capture_output=True, text=True)
    if '"error"' in r.stdout or "message" in r.stdout[:80]:
        sys.exit(f"upsert failed for {month}: {r.stdout[:300]}")


def main():
    months = sys.argv[1:]
    if not months:
        sys.exit("usage: treasury_statements.py YYYY-MM [YYYY-MM ...]")
    rails = load_env(RAILS_ENV)
    notices = load_env(NOTICES_ENV)
    for month in months:
        stmt = build_statement(rails, month)
        upsert(notices, month, stmt)
        x, s, m = stmt["xero"], stmt["stripe"], stmt["mercury"]
        net = x["pnl_totals"].get("Net Profit", x["pnl_totals"].get("Gross Profit"))
        cash = x["position_totals"].get("Total Cash and Cash Equivalents")
        print(f"{month}: stored · book net {net} · book cash EOM {cash} · "
              f"stripe {s['transaction_count']} txns · mercury "
              f"{sum(a['transaction_count'] for a in m['accounts'])} txns")


if __name__ == "__main__":
    main()
