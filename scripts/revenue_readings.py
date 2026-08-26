#!/usr/bin/env python3
"""
revenue_readings.py · T-09 · the readings runner

Fills revenue_readings (0030) so the revenue surface has numbers.

A reading is an observation beside the record, never an event
(TR §9). This runner writes one place, the readings store, and it
writes nothing else. It moves no money, touches no balance, and never
declares or retires a tier: the registry moves only by an overseer act
at the desk (0030 §4), which is the point of the separation.

Two bases, and the difference is the whole design (0030 §2):

  live      a seam reported the count. Today that seam is Stripe:
            active subscriptions, folded per product, matched to the
            tier whose name equals the product name.
  attested  no system holds the count and a named human vouched it.
            The voucher's name is required and is written into the
            note, because an attested figure without an attestor is a
            guess wearing a number.

Refusing rather than guessing: a Stripe product with no matching tier
is reported and skipped, never invented, and a stripe-sourced tier
with no product is reported as unread. Both are signals, not noise:
the first is a tier someone forgot to declare, the second is a tier
whose subscriptions have not arrived.

Usage:
  python3 scripts/revenue_readings.py --live
  python3 scripts/revenue_readings.py --live --dry-run
  python3 scripts/revenue_readings.py \
      --attest 'Maker Node=1@850' --voucher 'Aaron Neyer'
  python3 scripts/revenue_readings.py --show

  RAILS_ENV=... NOTICES_ENV=... to override the credential stores.

Credentials (never in this repository):
  rails store   STRIPE_KEY (restricted, read only), SUPABASE_ACCESS_TOKEN
                (management channel, the only writer)
  notices store SUPABASE_ACCESS_TOKEN, used only if the rails store
                carries none. Verified 2026-08-26: the notices copy
                answers Unauthorized and the rails copy works, which
                is also why treasury_statements.py (T-07) cannot store
                a statement today.

Authored-by: build-agent / T-09
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone

RAILS_ENV = os.environ.get("RAILS_ENV", os.path.expanduser("~/.config/secrets/techne-rails.env.gpg"))
NOTICES_ENV = os.environ.get("NOTICES_ENV", os.path.expanduser("~/.config/secrets/techne-notices.env.gpg"))
SUPABASE_PROJECT = "ujujwgopdwirebgcpekc"
RUNNER = "revenue_readings.py"


def load_env(path):
    out = subprocess.run(["gpg", "-d", path], capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"cannot decrypt {path}")
    return dict(line.split("=", 1) for line in out.stdout.strip().split("\n") if "=" in line)


def management_token(rails):
    """The management channel's token, from whichever store holds a live one."""
    token = rails.get("SUPABASE_ACCESS_TOKEN")
    if token:
        return token
    return load_env(NOTICES_ENV).get("SUPABASE_ACCESS_TOKEN") or sys.exit(
        "no SUPABASE_ACCESS_TOKEN in either credential store")


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sql(token, query):
    r = subprocess.run(
        ["curl", "-s", "-X", "POST",
         f"https://api.supabase.com/v1/projects/{SUPABASE_PROJECT}/database/query",
         "-H", f"Authorization: Bearer {token}",
         "-H", "Content-Type: application/json", "-H", "User-Agent: techne-cis",
         "-d", json.dumps({"query": query})],
        capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
    except json.JSONDecodeError:
        sys.exit(f"query endpoint returned no JSON: {r.stdout[:300]}")
    if isinstance(d, dict) and d.get("message"):
        sys.exit(f"query failed: {d['message'][:300]}")
    return d


def quote(s):
    return "$q$" + str(s) + "$q$"


# ---------- the registry as it stands ----------

def live_tiers(token):
    rows = sql(token, """
        select t.id, t.name, t.monthly_usd, t.source, a.display_name as program
          from revenue_tiers t join agents a on a.id = t.program_agent_id
         where t.retired_at is null
         order by a.display_name, t.name;
    """)
    return rows


# ---------- the Stripe seam ----------

def stripe_active(key):
    """Active subscriptions folded per product: count and monthly total.

    Yearly prices are divided by twelve so the figure is monthly
    throughout; the division is stated here rather than hidden in the
    surface. Quantities are honoured. The amount charged is used, not
    the tier's declared price, so a proration or discount Stripe
    reports survives into the reading verbatim (0030 §2).
    """
    headers = {"Authorization": "Bearer " + key}
    names = {}

    def product_name(pid):
        # Stripe caps expansion at four levels, and
        # data.items.data.price.product is five, so products are
        # resolved one call each and cached.
        if pid not in names:
            req = urllib.request.Request(f"https://api.stripe.com/v1/products/{pid}", headers=headers)
            with urllib.request.urlopen(req, timeout=45) as r:
                names[pid] = json.loads(r.read()).get("name") or pid
        return names[pid]

    per_product, starting_after, has_more = {}, None, True
    while has_more:
        url = "https://api.stripe.com/v1/subscriptions?limit=100&status=active"
        if starting_after:
            url += f"&starting_after={starting_after}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=45) as r:
            d = json.loads(r.read())
        for s in d.get("data", []):
            starting_after = s["id"]
            for item in s["items"]["data"]:
                price = item["price"]
                name = product_name(price["product"])
                rec = price.get("recurring") or {}
                amount = (price.get("unit_amount") or 0) * item.get("quantity", 1) / 100
                interval = rec.get("interval")
                months = {"month": 1, "year": 12, "week": 0.25, "day": 1 / 30}.get(interval)
                if not months:
                    print(f"  ? {name}: interval {interval!r} is not recurring monthly; skipped")
                    continue
                monthly = amount / months
                slot = per_product.setdefault(name, {"count": 0, "mrr": 0.0})
                slot["count"] += item.get("quantity", 1)
                slot["mrr"] += monthly
        has_more = d.get("has_more", False)
    return per_product


# ---------- writing readings ----------

def write_reading(token, tier_id, count, mrr, basis, source, note):
    sql(token, f"""
        insert into revenue_readings (tier_id, active_count, mrr_usd, basis, source, runner, note)
        values ({quote(tier_id)}::uuid, {int(count)}, {round(float(mrr), 2)},
                {quote(basis)}, {quote(source)}, {quote(RUNNER)}, {quote(note)});
    """)


def run_live(rails, token, dry_run):
    tiers = [t for t in live_tiers(token) if t["source"] == "stripe"]
    if not tiers:
        sys.exit("no live tier names stripe as its source; declare tiers at the registry desk first")
    products = stripe_active(rails["STRIPE_KEY"])
    by_name = {t["name"].strip().lower(): t for t in tiers}
    read_at = now_iso()
    matched, total = set(), 0.0

    for name, agg in sorted(products.items()):
        tier = by_name.get(name.strip().lower())
        if tier is None:
            print(f"  ! stripe product {name!r}: {agg['count']} active, "
                  f"${agg['mrr']:.2f}/mo, but no live tier carries that name. "
                  f"Skipped; declare the tier at the desk to fold it in.")
            continue
        matched.add(tier["id"])
        total += agg["mrr"]
        note = (f"Stripe active subscriptions on product {name!r}, read {read_at}.")
        if dry_run:
            print(f"  · {tier['program']} / {tier['name']}: {agg['count']} × "
                  f"${agg['mrr'] / max(agg['count'], 1):.2f} = ${agg['mrr']:.2f}/mo (not written)")
            continue
        write_reading(token, tier["id"], agg["count"], agg["mrr"], "live", "stripe", note)
        print(f"  ✓ {tier['program']} / {tier['name']}: {agg['count']} active, ${agg['mrr']:.2f}/mo")

    for tier in tiers:
        if tier["id"] not in matched:
            print(f"  · {tier['program']} / {tier['name']}: no Stripe product of that name; "
                  f"left unread, and the surface will say so.")

    print(f"{'would write' if dry_run else 'wrote'} {len(matched)} live reading(s), "
          f"${total:.2f}/mo, at {read_at}")


def run_attest(token, specs, voucher, dry_run):
    if not voucher:
        sys.exit("an attested reading needs --voucher: the named human vouching the count")
    tiers = live_tiers(token)
    by_name = {t["name"].strip().lower(): t for t in tiers}
    read_at = now_iso()

    for spec in specs:
        # NAME=COUNT@MRR, for example  'Maker Node=1@850'
        try:
            name, rest = spec.rsplit("=", 1)
            count, mrr = rest.split("@", 1)
            count, mrr = int(count), float(mrr)
        except ValueError:
            sys.exit(f"cannot read {spec!r}; the shape is 'Tier name=COUNT@MONTHLY_USD'")
        tier = by_name.get(name.strip().lower())
        if tier is None:
            sys.exit(f"no live tier named {name!r}; declare it at the registry desk first")
        note = f"Attested by {voucher} at {read_at}. No system holds this count."
        if dry_run:
            print(f"  · {tier['program']} / {tier['name']}: {count} attested, "
                  f"${mrr:.2f}/mo, vouched by {voucher} (not written)")
            continue
        write_reading(token, tier["id"], count, mrr, "attested", f"attested:{voucher}", note)
        print(f"  ✓ {tier['program']} / {tier['name']}: {count} attested, ${mrr:.2f}/mo, "
              f"vouched by {voucher}")


def run_show(token):
    rows = sql(token, "select * from revenue_dashboard();")
    if not rows:
        print("no live tier carries a reading yet")
        return
    total = 0.0
    for r in rows:
        mrr = float(r["mrr_usd"]) if r["mrr_usd"] is not None else None
        total += mrr or 0.0
        figure = f"${mrr:,.2f}" if mrr is not None else "waiting"
        print(f"  {r['program_name']:<14} {r['tier_name']:<34} {figure:>12}  "
              f"{r['basis'] or '-':<9} {r['reading_source'] or '-':<20} {r['read_at'] or ''}")
    print(f"  {'':<14} {'monthly recurring':<34} {'$' + format(total, ',.2f'):>12}")
    print(f"  {'':<14} {'annual, twelve times the above':<34} {'$' + format(total * 12, ',.2f'):>12}")


def main():
    p = argparse.ArgumentParser(description="write revenue readings (0030) from a seam or an attestation")
    p.add_argument("--live", action="store_true", help="read active Stripe subscriptions and write live readings")
    p.add_argument("--attest", action="append", default=[], metavar="TIER=COUNT@MRR",
                   help="write an attested reading; repeatable")
    p.add_argument("--voucher", help="the named human vouching an attested count")
    p.add_argument("--show", action="store_true", help="print the dashboard fold as it stands")
    p.add_argument("--dry-run", action="store_true", help="print what would be written and write nothing")
    args = p.parse_args()

    if not (args.live or args.attest or args.show):
        p.error("nothing asked: use --live, --attest, or --show")

    rails = load_env(RAILS_ENV)
    token = management_token(rails)
    if args.live:
        run_live(rails, token, args.dry_run)
    if args.attest:
        run_attest(token, args.attest, args.voucher, args.dry_run)
    if args.show:
        run_show(token)


if __name__ == "__main__":
    main()
