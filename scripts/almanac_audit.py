#!/usr/bin/env python3
"""Almanac audit (X-17, X-18, X-19) -- BP v2, SER v0.3, VS v2 section 9.

The Almanac is authored prose over a generated spine. The headline
counts are written from the ledger by the validator and proven fresh in
CI (X-10), but the cards below them are hand-kept, and hand-kept claims
drift. Twice now they have: X-14 found the page narrating seven beds
where the ledger held nine, and X-17 found fifty addresses standing in
the ledger with no card here at all, alongside seven cards carrying a
mark the ledger contradicts, in both directions.

X-17 wrote the first two checks and deliberately left them out of CI: a
new way for CI to fail in launch week is a hazard, and the teeth were
filed as X-18. This is X-18, and it carries a third check X-17 did not
have.

The third check exists because of what X-19 found. The card audit
reported zero findings over 122 addresses on the morning the ledger was
discovered to be wrong in twenty-four places, including two merged
pieces that held no address at all. The cards were faithful. The ledger
was not. A page can only be as true as the record it reads, so the
record itself is now read against the repository.

Three checks:

1. Coverage. Every address in the ledger has a card on the page, and no
   card names an address the ledger does not hold.
2. Marks. Each card's chip carries the ledger's status for that address.
3. Repository. Every address-shaped branch merged into this history has
   an address in the ledger. A piece is named by the branch that built
   it, so a merged branch wearing a piece's name and holding no address
   is a piece the record lost. FORMATION-01 and DOC-01 were both lost
   that way for a day.

Check 3 reads git history, so it needs the full history: a shallow
clone has no merge commits to read. The workflow fetches depth 0 for
this job. Run with --self-test to prove all three still have teeth.

This audit does not author anything. What a card says is the steward's
call; this checks only that a card exists, that the mark it wears is
the mark the ledger carries, and that no merged piece is missing from
the ledger entirely.
"""
import argparse
import re
import subprocess
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

MERGE_SUBJECT = re.compile(r'^Merge pull request #\d+ from [^/]+/(.+)$')

# An address is upper case, digits, and hyphens: U-01, X-17, MM-01,
# SUB-02, G-B, DOC-01, FORMATION-01, AGY, GUILD, STANDING. A branch
# carrying anything else is prose work rather than a piece, and this
# estate has sixty of those in its history: fix/ci-green,
# accounting-counsel-memo, T-06-balance-view, STANDING-v03. They are
# out of scope by shape rather than by a list that would need keeping.
ADDRESS_SHAPE = re.compile(r'^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*$')


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


def read_cards(page):
    return {addr.strip(): chip.strip() for addr, chip in ROW.findall(page)}


def merged_branches(revision='HEAD'):
    """The branch names of every merge commit in this history.

    Returns None when the history cannot be read, which is how a
    shallow clone or a non-repository checkout announces itself. The
    caller decides whether that is a finding or a skip; it is a finding
    in CI, because the workflow asks for the depth the check needs.
    """
    try:
        result = subprocess.run(
            ['git', 'log', '--merges', '--format=%s', revision],
            cwd=REPO_ROOT, capture_output=True, text=True, check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    names = set()
    for line in result.stdout.splitlines():
        found = MERGE_SUBJECT.match(line.strip())
        if found:
            names.add(found.group(1))
    return names


def normalise(text):
    """The card writes its mark for a reader; compare the part that carries
    the claim. 'open · in session' and 'open · in-session' are one mark."""
    text = text.replace('&middot;', '·').replace('&nbsp;', ' ')
    return ' '.join(text.split()).replace('-', ' ')


def check_coverage(marks, cards):
    findings = []
    for address in sorted(set(marks) - set(cards)):
        findings.append(f'{address}: in the ledger, no card on the Almanac')
    for address in sorted(set(cards) - set(marks)):
        findings.append(f'{address}: carded on the Almanac, not in the ledger')
    return findings


def check_marks(marks, cards):
    findings = []
    for address in sorted(set(marks) & set(cards)):
        claim = marks[address].split('·')[-1].strip()
        if normalise(claim) not in normalise(cards[address]):
            findings.append(
                f'{address}: ledger says "{marks[address]}", '
                f'the card says "{normalise(cards[address])}"'
            )
    return findings


def check_repository(marks, branches):
    if branches is None:
        return ['the git history could not be read, so no merged piece '
                'was checked against the ledger; this check needs the '
                'full history, not a shallow clone']
    findings = []
    for branch in sorted(branches):
        if not ADDRESS_SHAPE.match(branch):
            continue
        if branch not in marks:
            findings.append(
                f'{branch}: merged into main, no address in the ledger'
            )
    return findings


def self_test():
    """Prove each check refuses what it exists to refuse.

    X-18's acceptance asks for a live regression test rather than an
    assertion that the gate works. Each case below is the exact defect
    the estate has already shipped once.
    """
    cases = []

    # X-17's finding: an address in the ledger with no card.
    cases.append((
        'coverage, ledger side',
        check_coverage({'U-99': 'drafted'}, {}),
    ))
    # The mirror: a card for an address the ledger does not hold.
    cases.append((
        'coverage, page side',
        check_coverage({}, {'U-99': 'drafted'}),
    ))
    # X-14's finding: a card wearing a mark the ledger contradicts.
    cases.append((
        'marks',
        check_marks({'U-99': 'open · verified'},
                    {'U-99': 'open &middot; in session'}),
    ))
    # X-19's finding: a merged piece with no address at all.
    cases.append((
        'repository',
        check_repository({}, {'DOC-01', 'fix/ci-green'}),
    ))
    # And the shape rule: prose branches are not pieces and must not
    # be reported, or the check would cry sixty times.
    quiet = check_repository({}, {'fix/ci-green', 'T-06-balance-view',
                                  'accounting-counsel-memo'})

    failures = []
    for name, findings in cases:
        if not findings:
            failures.append(f'{name}: the check passed what it must refuse')
        else:
            print(f'self-test: {name}: refused, "{findings[0]}"')
    if quiet:
        failures.append(f'shape: a prose branch was reported, "{quiet[0]}"')
    else:
        print('self-test: shape: prose branches stay quiet')

    for failure in failures:
        print(f'self-test: {failure}')
    print(f'self-test: {len(failures)} failure(s) over '
          f'{len(cases) + 1} case(s)')
    return 1 if failures else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true',
                        help='prove the three checks still refuse')
    args = parser.parse_args()
    if args.self_test:
        return self_test()

    marks = load_ledger()
    cards = read_cards(ALMANAC.read_text(encoding='utf-8'))
    branches = merged_branches()

    findings = (check_coverage(marks, cards)
                + check_marks(marks, cards)
                + check_repository(marks, branches))

    for finding in findings:
        print(f'almanac-audit: {finding}')
    print(f'almanac-audit: {len(findings)} finding(s) '
          f'over {len(marks)} addresses')
    return 1 if findings else 0


if __name__ == '__main__':
    raise SystemExit(main())
