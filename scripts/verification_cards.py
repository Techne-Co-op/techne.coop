#!/usr/bin/env python3
"""The verification cards, extracted (X-28) -- BP v2, VS v2 section 2.

The run-book at /commons/build/verification/ is the authored page: a
walker reads it, walks it, and speaks the verdicts into a recording.
X-28 adds a second surface for the same walk, behind the intranet gate,
where the walker clicks the verdict instead of speaking it. Two surfaces
carrying the same fifty-two cards is two places for the cards to drift,
and a hand-kept second copy would drift the way the almanac cards drifted
before X-18 gave them teeth.

So there is no second copy. This script reads the run-book and writes
commons/build/verification/cards.json, which the intranet surface
renders. The run-book stays the authored source; the JSON is generated
and proven fresh in CI, the way STATUS.md and index.json are.

Normalisations applied on the way out, each a defect in the source
markup that would render wrong rather than a change of meaning:

  * doubled anchors. The run-book carries <a href="U"><a href="U">U</a></a>
    in most step lines. Collapsed to one anchor. The run-book itself is
    not touched by this piece; the defect is reported, not absorbed.
  * bare angle placeholders. "run <n>", "read <date> at <hash>" parse as
    unknown tags and vanish. Escaped so the reader sees them.

Run with --check to prove the committed JSON matches what this writes.
"""
import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNBOOK = REPO_ROOT / 'commons/build/verification/index.html'
CARDS = REPO_ROOT / 'commons/build/verification/cards.json'

PART = re.compile(
    r'<div class="part">\s*'
    r'<div class="part-k">(?P<kicker>.*?)</div>\s*'
    r'<h3>(?P<title>.*?)</h3>\s*'
    r'<p>(?P<blurb>.*?)</p>\s*'
    r'</div>',
    re.S,
)

SECTION = re.compile(
    r'<section class="sec">\s*'
    r'<div class="addr">(?P<addr>.*?)</div>\s*'
    r'<h2>(?P<title>.*?)</h2>',
    re.S,
)

LEAD = re.compile(r'<p class="lead">(.*?)</p>', re.S)
NEED = re.compile(r'<div class="need"><span class="k">.*?</span>(.*?)</div>', re.S)

PIECE = re.compile(
    r'<div class="piece" id="(?P<id>[^"]+)">\s*'
    r'<div class="piece-head">'
    r'<span class="addr-chip">(?P<addr>[^<]*)</span>'
    r'<span class="piece-title">(?P<title>.*?)</span>'
    r'</div>\s*'
    r'<p class="ctx">(?P<ctx>.*?)</p>\s*'
    r'<ol class="steps">(?P<steps>.*?)</ol>\s*'
    r'<p class="say">(?P<say>.*?)</p>\s*'
    r'</div>',
    re.S,
)

CLUSTER = re.compile(r'<h3 style="[^"]*">(.*?)</h3>', re.S)
STEP = re.compile(r'<li>(.*?)</li>', re.S)
DOUBLED_ANCHOR = re.compile(r'<a href="([^"]*)">\s*<a href="[^"]*">(.*?)</a>\s*</a>', re.S)
BARE_ANGLE = re.compile(r'<(n|date|hash)>')

# Every card either holds or fails, except an attestation, which is
# given or is not ready. Deferred is available on both: the run-book's
# rule is that skipping is fine and skipping silently is not.
VERDICTS_WALK = ['holds', 'fails', 'deferred']
VERDICTS_ATTEST = ['attested', 'not ready', 'deferred']


def clean(fragment):
    """Normalise an authored fragment for re-rendering."""
    prev = None
    out = fragment.strip()
    while prev != out:
        prev = out
        out = DOUBLED_ANCHOR.sub(r'<a href="\1">\2</a>', out)
    out = BARE_ANGLE.sub(r'&lt;\1&gt;', out)
    return re.sub(r'\s+', ' ', out).strip()


def extract():
    html = RUNBOOK.read_text(encoding='utf-8')

    # The document is a flat sequence: a part block introduces a tier,
    # then one or more sections carry its cards. Walking the markers in
    # source order is enough; nothing here nests.
    marks = []
    for m in PART.finditer(html):
        marks.append((m.start(), 'part', m))
    for m in SECTION.finditer(html):
        marks.append((m.start(), 'section', m))
    for m in CLUSTER.finditer(html):
        marks.append((m.start(), 'cluster', m))
    for m in PIECE.finditer(html):
        marks.append((m.start(), 'piece', m))
    marks.sort(key=lambda t: t[0])

    groups = []
    pending_part = None
    group = None
    cluster = None

    for _, kind, m in marks:
        if kind == 'part':
            pending_part = {
                'kicker': clean(m.group('kicker')),
                'title': clean(m.group('title')),
                'blurb': clean(m.group('blurb')),
            }
        elif kind == 'section':
            tail = html[m.end():]
            nxt = SECTION.search(tail)
            body = tail[:nxt.start()] if nxt else tail
            lead = LEAD.search(body)
            need = NEED.search(body)
            group = {
                'addr': clean(m.group('addr')),
                'title': clean(m.group('title')),
                'part': pending_part,
                'lead': clean(lead.group(1)) if lead else None,
                'need': clean(need.group(1)) if need else None,
                # The two clusters that cannot be walked alone are the two
                # that carry a "what you need" block naming a second person.
                # The markup already says it; nothing needs a second list.
                'two_person': bool(need),
                'cards': [],
            }
            pending_part = None
            cluster = None
            groups.append(group)
        elif kind == 'cluster':
            cluster = clean(m.group(1))
        elif kind == 'piece':
            if group is None:
                raise SystemExit('verification-cards: a card before any section')
            say = clean(m.group('say'))
            group['cards'].append({
                'address': clean(m.group('addr')),
                'title': clean(m.group('title')),
                'context': clean(m.group('ctx')),
                'steps': [clean(s) for s in STEP.findall(m.group('steps'))],
                'say': say,
                'verdicts': VERDICTS_ATTEST if 'attested' in say else VERDICTS_WALK,
                'cluster': cluster,
            })

    groups = [g for g in groups if g['cards']]
    cards = [c for g in groups for c in g['cards']]
    addresses = [c['address'] for c in cards]
    if len(addresses) != len(set(addresses)):
        raise SystemExit('verification-cards: the run-book carries an address twice')
    if not cards:
        raise SystemExit('verification-cards: no cards found; the run-book markup moved')

    return {
        'note': 'Generated by scripts/verification_cards.py from '
                'commons/build/verification/index.html. Do not hand-edit: '
                'edit the run-book and regenerate.',
        'source': 'commons/build/verification/index.html',
        'count': len(cards),
        'groups': groups,
    }


def render(data):
    return json.dumps(data, indent=1, ensure_ascii=False) + '\n'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--check', action='store_true',
                    help='fail if the committed JSON is not what this writes')
    args = ap.parse_args()

    text = render(extract())

    if args.check:
        if not CARDS.exists():
            sys.stderr.write('verification-cards: cards.json is missing\n')
            return 1
        if CARDS.read_text(encoding='utf-8') != text:
            sys.stderr.write(
                'verification-cards: cards.json is stale; run '
                'python3 scripts/verification_cards.py and commit\n')
            return 1
        sys.stdout.write('verification-cards: cards.json is current\n')
        return 0

    CARDS.write_text(text, encoding='utf-8')
    data = json.loads(text)
    sys.stdout.write('verification-cards: wrote %s (%d cards, %d groups)\n'
                     % (CARDS.relative_to(REPO_ROOT), data['count'], len(data['groups'])))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
