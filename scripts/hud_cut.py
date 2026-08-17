#!/usr/bin/env python3
"""
hud_cut.py · the transducer's cut · TRANSDUCER v0.2 §5 (drafted, not adopted)

Reads the repository alone and writes one data file, intranet/hud/cut.json.
The page at /intranet/hud/ renders that file and nothing else. The cut
carries the commit it was taken at, so every view can show its date.

The walkaway contract (TRANSDUCER §5): the cut is computable from the
public repository alone, on fresh infrastructure, with no key. Run twice
against the same commit, the file is byte-identical (keys sorted, no
timestamps other than the commit's own).

Refusals honoured here, not only on the surface (TRANSDUCER §9):
  R2  no per-author figures are computed, ever; author names never
      leave git's output because they are never asked for.
  R5  no percentages, no scores; counts and named states only.
  R6  the two-pile taxonomy of the tending view is a frame, not a
      reading; it is carried under "frame" keys so the surface can
      attribute it as the instrument's drafting.

This script is a drafted artifact of an unadopted module. Its CI wiring
(T-03) and its ledger graft wait on adoption; running it by hand and
committing the cut alongside a change is the interim practice.
"""

import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "intranet" / "hud" / "cut.json"

# The two piles of the tending view. A frame, not a reading: TRANSDUCER-D4
# elects whether it survives. Tending = work on the workshop itself;
# growing = work on what lives in it. Classification is by path prefix.
TENDING_PREFIXES = (
    "scripts/", ".github/", "assets/", "supabase/",
)
TENDING_FILES = {
    "AGENTS.md", "README.md", "RUN.md", "CONTRIBUTORS.md",
    "STATUS.md", "index.json", "rdm-ledger.yaml", "CNAME",
    "favicon.png", "favicon.svg",
}


def git(*args):
    return subprocess.run(
        ["git", "-C", str(REPO), *args],
        capture_output=True, text=True, check=True,
    ).stdout


def head_stamp():
    line = git("log", "-1", "--pretty=%H%x00%cI%x00%s").strip()
    full, date, subject = line.split("\x00")
    count = int(git("rev-list", "--count", "HEAD").strip())
    return {
        "commit": full[:12],
        "date": date,
        "subject": subject,
        "commit_count": count,
    }


def composition():
    """Every tracked file: bytes and revision count. Blind to whether
    any of it is finished, or good."""
    sizes = {}
    for line in git("ls-tree", "-r", "-l", "HEAD").splitlines():
        # <mode> <type> <hash> <size>\t<path>
        meta, path = line.split("\t", 1)
        parts = meta.split()
        if parts[1] != "blob":
            continue
        sizes[path] = int(parts[3])

    revisions = defaultdict(int)
    current = None
    for line in git("log", "--name-only", "--pretty=format:%x01").splitlines():
        if line == "\x01" or line == "":
            continue
        revisions[line] += 1

    by_dir = defaultdict(lambda: {"files": 0, "bytes": 0, "revisions": 0})
    for path, size in sizes.items():
        top = path.split("/", 1)[0] if "/" in path else "(root)"
        d = by_dir[top]
        d["files"] += 1
        d["bytes"] += size
        d["revisions"] += revisions.get(path, 0)

    most_revised = sorted(
        ((revisions.get(p, 0), p) for p in sizes),
        reverse=True,
    )[:12]
    heaviest = sorted(((s, p) for p, s in sizes.items()), reverse=True)[:12]

    return {
        "tracked_files": len(sizes),
        "tracked_bytes": sum(sizes.values()),
        "directories": {
            k: by_dir[k] for k in sorted(by_dir)
        },
        "most_revised": [
            {"path": p, "revisions": n} for n, p in most_revised
        ],
        "heaviest": [
            {"path": p, "bytes": s} for s, p in heaviest
        ],
    }


def maturation():
    """The ledger read in its own mark grammar. Blind to effort,
    difficulty, and duration. The ledger is the source and this view
    yields to it entirely (JC-1)."""
    text = (REPO / "rdm-ledger.yaml").read_text()
    entries = []
    blocks = re.split(r"\n\s+- address: ", text)[1:]
    for block in blocks:
        addr = block.split("\n", 1)[0].strip()
        t = re.search(r"^\s+title: (.+)$", block, re.M)
        s = re.search(r"^\s+status: (.+)$", block, re.M)
        if not (t and s):
            continue
        title, status = t.group(1).strip(), s.group(1).strip()
        if status.startswith("open"):
            mark = status.split("·", 1)[1].strip() if "·" in status else "open"
            state = "open"
        else:
            state, mark = status, None
        entries.append({"address": addr, "title": title,
                        "state": state, "mark": mark})

    beds = defaultdict(lambda: defaultdict(int))
    for e in entries:
        prefix = e["address"].split("-", 1)[0]
        label = e["mark"] if e["mark"] else e["state"]
        beds[prefix][label] += 1

    totals = defaultdict(int)
    for e in entries:
        totals[e["mark"] if e["mark"] else e["state"]] += 1

    return {
        "pieces": len(entries),
        "totals": dict(sorted(totals.items())),
        "beds": {k: dict(sorted(v.items())) for k, v in sorted(beds.items())},
        "entries": entries,
    }


def journeys():
    """Each arrival class walking its first sitting, read from the
    participation stories page. Half this derivation is a promise: it
    parses an authored page until the journeys register (JOURNEYS J-01)
    exists (JC-2). Blind to any individual; personas are arrival
    classes, never members."""
    page = REPO / "commons" / "prd" / "stories" / "index.html"
    if not page.exists():
        return {"source": None, "classes": []}
    html = page.read_text()

    classes = []
    sections = re.split(r'<section class="sec"', html)[1:]
    for sec in sections:
        h2 = re.search(r"<h2>(.*?)</h2>", sec, re.S)
        if not h2:
            continue
        name = re.sub(r"<[^>]+>", "", h2.group(1))
        name = re.sub(r"\s+", " ", name).replace("&middot;", "·").strip()
        sids = re.findall(r'<div class="sid">([^<]+)</div>', sec)
        chips = re.findall(r'<span class="chip ([a-z]+)"', sec)
        stops = re.findall(
            r'<p class="stop"><b>([^<]*)</b>\s*(.*?)</p>', sec, re.S)
        stop_texts = []
        for lead, body in stops:
            t = re.sub(r"<[^>]+>", "", lead + " " + body)
            t = re.sub(r"\s+", " ", t).strip()
            stop_texts.append(t[:280] + ("…" if len(t) > 280 else ""))
        chip_counts = defaultdict(int)
        for c in chips:
            chip_counts[c] += 1
        classes.append({
            "name": name,
            "stories": len(sids),
            "standing": dict(sorted(chip_counts.items())),
            "stops": stop_texts,
        })

    return {
        "source": "commons/prd/stories/index.html",
        "derivation": "parsed from an authored page; the journeys "
                      "register this view should read is JOURNEYS J-01, "
                      "not yet landed",
        "classes": classes,
    }


def tending():
    """The rhythm of the work: commits per week, and the two piles.
    Blind to who did how much, deliberately and permanently (R2):
    no author is ever read."""
    weeks = defaultdict(lambda: {"commits": 0, "tending": 0, "growing": 0})
    entries = git("log", "--name-only", "--pretty=format:%x01%cI").split("\x01")
    for entry in entries:
        lines = [l for l in entry.splitlines() if l.strip()]
        if not lines:
            continue
        date = lines[0].strip()
        files = lines[1:]
        # ISO week key from the committer date, no clock consulted
        year, month, day = date[:10].split("-")
        import datetime
        wk = datetime.date(int(year), int(month), int(day)).isocalendar()
        key = f"{wk[0]}-W{wk[1]:02d}"
        w = weeks[key]
        w["commits"] += 1
        is_tending = bool(files) and all(
            f in TENDING_FILES or f.startswith(TENDING_PREFIXES)
            for f in files
        )
        w["tending" if is_tending else "growing"] += 1

    return {
        "frame": "the two piles, tending the place itself and growing "
                 "what lives in it, are the instrument's taxonomy, "
                 "drafted not adopted (TRANSDUCER-D4)",
        "weeks": {k: weeks[k] for k in sorted(weeks)},
    }


def standing(comp, mat):
    """The whole cut across as concentric rings. The only view in which
    the dimensions can contradict one another in a single figure. Blind
    to change over time; a cross-section is one moment."""
    gates = [e for e in mat["entries"]
             if e["address"].startswith("G-") or e["address"] == "G0"]
    pages = len(git("ls-files", "*.html").split())
    return {
        "rings": {
            "history_commits": None,  # filled from the stamp by main()
            "documents": sum(1 for e in mat["entries"]
                             if e["state"] == "drafted"),
            "pieces": mat["pieces"],
            "proofs": {
                "named": len(gates),
                "attested": sum(1 for e in gates if e["mark"] == "attested"),
            },
            "published_pages": pages,
        },
    }


def main():
    stamp = head_stamp()
    comp = composition()
    mat = maturation()
    st = standing(comp, mat)
    st["rings"]["history_commits"] = stamp["commit_count"]
    cut = {
        "instrument": "the transducer",
        "module": "TRANSDUCER v0.2 (drafted, not adopted)",
        "stamp": stamp,
        "standing": st,
        "composition": comp,
        "maturation": mat,
        "journeys": journeys(),
        "tending": tending(),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(cut, indent=1, sort_keys=True,
                              ensure_ascii=True) + "\n")
    print(f"cut taken at {stamp['commit']} ({stamp['date']}) -> {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    sys.exit(main())
