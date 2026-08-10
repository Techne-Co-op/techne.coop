#!/usr/bin/env python3
"""Almanac card audit (X-17) -- BP v2, SER v0.3.

The Almanac is authored prose over a generated spine. The headline
counts are written from the ledger by the validator and proven fresh in
CI (X-10), but the cards below them are hand-kept, and hand-kept claims
drift. Twice now they have: X-14 found the page narrating seven beds
where the ledger held nine, and X-17 found fifty addresses standing in
the ledger with no card here at all, alongside seven cards carrying a
mark the ledger contradicts, in both directions.

This reads both and reports the difference. It does not author
anything: what a card says is the steward's call, and this checks only
that a card exists for every address and that the mark it wears is the
mark the ledger carries.

Two checks:

1. Coverage. Every address in rdm-ledger.yaml has a card on the page,
   and no card names an address the ledger does not hold.
2. Marks. Each card's chip carries the ledger's status for that
   address.

Exit non-zero on any finding. Not wired into CI by the piece that wrote
it: a new gate in launch week is a hazard, and the teeth are filed as
their own piece for after launch. Run it by hand after any ledger
change that adds or moves an address.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LEDGER = REPO_ROOT / 'rdm-ledger.yaml'
ALMANAC = REPO_ROOT / 'commons/build/index.html'

ROW = re.compile(
    r'<span class="pkt-addr">([^<]+)</span>'
    r'.*?<span class="chip \w+"><span class="dot"></span>([^<]+)</span>',
    re.S,
)


def load_ledger():
    try:
        import yaml
    except ImportError:
        sys.stderr.write('almanac-audit: PyYAML required\n')
        raise SystemExit(2)
    doc = yaml.safe_load(LEDGER.read_text(encoding='utf-8'))
    marks = {}
    for entries in doc.values():
        for entry in entries:
            marks[entry['address']] = entry['status']
    return marks


def normalise(text):
    """The card writes its mark for a reader; compare the part that carries
    the claim. 'open · in session' and 'open · in-session' are one mark."""
    text = text.replace('&middot;', '·').replace('&nbsp;', ' ')
    return ' '.join(text.split()).replace('-', ' ')


def main():
    marks = load_ledger()
    page = ALMANAC.read_text(encoding='utf-8')
    cards = {addr.strip(): chip.strip() for addr, chip in ROW.findall(page)}

    findings = []
    for address in sorted(set(marks) - set(cards)):
        findings.append(f'{address}: in the ledger, no card on the Almanac')
    for address in sorted(set(cards) - set(marks)):
        findings.append(f'{address}: carded on the Almanac, not in the ledger')
    for address in sorted(set(marks) & set(cards)):
        claim = marks[address].split('·')[-1].strip()
        if normalise(claim) not in normalise(cards[address]):
            findings.append(
                f'{address}: ledger says "{marks[address]}", '
                f'the card says "{normalise(cards[address])}"'
            )

    for finding in findings:
        print(f'almanac-audit: {finding}')
    print(f'almanac-audit: {len(findings)} finding(s) '
          f'over {len(marks)} addresses')
    return 1 if findings else 0


if __name__ == '__main__':
    raise SystemExit(main())
