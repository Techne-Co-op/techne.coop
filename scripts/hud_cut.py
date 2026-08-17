#!/usr/bin/env python3
"""
hud_cut.py · the transducer's cut · TRANSDUCER v0.2 section 5 (drafted, not adopted)

Reads the repository alone and rewrites the snapshot block embedded in
intranet/hud/index.html, so the instrument renders a dated cut of the
real record rather than a hand-taken copy. The page renders that block
and nothing else; the cut carries the commit it was taken at.

The walkaway contract (TRANSDUCER section 5): the cut is computable from
the public repository alone, on fresh infrastructure, with no key. Run
twice at the same commit, the embedded block is byte-identical (keys
sorted, no clock consulted; the only dates are the commits' own).

Refusals honoured here, not only on the surface (TRANSDUCER section 9):
  R2  no per-author figure is computed, ever; author names never leave
      git's output because they are never asked for.
  R5  no percentages, no scores; counts and named states only.
  R6  the two-pile taxonomy of the tending view is a frame, not a
      reading; the surface attributes it as the instrument's drafting.

This script is a drafted artifact of an unadopted module. Its CI wiring
(T-03 of the module) and its ledger graft wait on adoption; running it
by hand and committing the refreshed page is the interim practice.
"""

import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PAGE = REPO / "intranet" / "hud" / "index.html"

# The currency gate's own commits (TR-03) are the instrument's
# heartbeat, not the record's work: the generator ignores them, and
# normalises the page's own size to its size net of the cut it
# carries, so a cut committed at commit M and re-read at the refresh
# commit R computes byte-identically. Without both, the instrument
# counting its own heartbeat would never converge.
REFRESH_MARK = "hud: cut retaken"

# The two piles of the tending lens. A frame, not a reading: TRANSDUCER-D4
# elects whether it survives. Tending = work on the workshop itself;
# growing = work on what lives in it. Classification is by path.
TENDING_PREFIXES = ("scripts/", ".github/", "assets/", "supabase/")
TENDING_FILES = {
    "AGENTS.md", "README.md", "RUN.md", "CONTRIBUTORS.md",
    "STATUS.md", "index.json", "rdm-ledger.yaml", "CNAME",
    "favicon.png", "favicon.svg", ".gitignore",
}


def git(*args):
    return subprocess.run(
        ["git", "-C", str(REPO), *args],
        capture_output=True, text=True, check=True,
    ).stdout


def tracked_files():
    files = []
    for line in git("ls-tree", "-r", "-l", "HEAD").splitlines():
        meta, path = line.split("\t", 1)
        parts = meta.split()
        if parts[1] != "blob":
            continue
        size = int(parts[3])
        if path == "intranet/hud/index.html":
            blob = git("show", f"HEAD:{path}")
            m = re.search(r'(<script id="snapshot" type="application/json">)(.*?)(</script>)',
                          blob, re.S)
            if m:
                size = len(blob.encode()) - len(m.group(2).encode())
        files.append({"path": path, "size": size})
    files.sort(key=lambda f: (-f["size"], f["path"]))
    return files


def history():
    """Commit history without authors: dates, merge-ness, files touched.
    R2: %an is never in the format string."""
    out = git("log", "--name-only", "--date-order",
              "--pretty=format:%x01%H%x00%cI%x00%P%x00%s")
    commits = []
    for entry in out.split("\x01"):
        lines = entry.splitlines()
        if not lines or not lines[0].strip():
            continue
        head = lines[0].split("\x00")
        if head[3].startswith(REFRESH_MARK):
            continue
        files = [l for l in lines[1:] if l.strip()]
        commits.append({
            "date": head[1][:10],
            "merge": len(head[2].split()) > 1,
            "files": files,
        })
    return commits


def ledger_entries():
    """The ledger read per section, in its own mark grammar (JC-1)."""
    text = (REPO / "rdm-ledger.yaml").read_text()
    entries = []
    bed = None
    for chunk in re.split(r"\n(?=\S|  - address: )", text):
        pass  # placeholder to keep structure simple below
    lines = text.splitlines()
    block = []
    def flush():
        if not block:
            return
        b = "\n".join(block)
        a = re.match(r"\s*- address: (\S+)", b)
        t = re.search(r"^\s+title: (.+)$", b, re.M)
        s = re.search(r"^\s+status: (.+)$", b, re.M)
        if not (a and t and s):
            return
        intent = ""
        mi = re.search(r"^\s+intent: >?\s*\n((?:\s{6,}.+\n?)+)", b, re.M)
        if mi:
            intent = " ".join(l.strip() for l in mi.group(1).splitlines())
        else:
            mi = re.search(r"^\s+intent: (.+)$", b, re.M)
            if mi:
                intent = mi.group(1).strip()
        ready = ""
        mr = re.search(r"^\s+ready_when: >?\s*\n((?:\s{6,}.+\n?)+)", b, re.M)
        if mr:
            ready = " ".join(l.strip() for l in mr.group(1).splitlines())
        else:
            mr = re.search(r"^\s+ready_when: (.+)$", b, re.M)
            if mr:
                ready = mr.group(1).strip()
        cites = 0
        mc = re.search(r"^\s+cites: \[(.*?)\]", b, re.M)
        if mc and mc.group(1).strip():
            cites = len([c for c in mc.group(1).split(",") if c.strip()])
        status = s.group(1).strip()
        if status.startswith("open"):
            mark = status.split("·", 1)[1].strip() if "·" in status else "open"
        else:
            mark = status
        entries.append({
            "id": a.group(1), "title": t.group(1).strip(),
            "status": status, "mark": mark, "bed": bed or "unfiled",
            "intent": intent[:260], "cites": cites, "ready": ready[:160],
        })
    for line in lines:
        m = re.match(r"^(\w[\w-]*):\s*$", line)
        if m:
            flush(); block.clear()
            bed = m.group(1)
            continue
        if re.match(r"^  - address: ", line):
            flush(); block.clear()
        block.append(line)
    flush()
    return entries


def journeys():
    """The passage lens, read from the participation stories page until
    the journeys register (JOURNEYS J-01) exists (JC-2 of the module).
    Personas are arrival classes, never members."""
    page = REPO / "commons" / "prd" / "stories" / "index.html"
    steps, personas = {}, []
    if not page.exists():
        return {"steps": steps, "personas": personas, "reading": "missing"}
    html = page.read_text()

    def strip(t):
        t = re.sub(r"<[^>]+>", " ", t)
        t = t.replace("&middot;", "·").replace("&amp;", "&")
        t = t.replace("&rsquo;", "’").replace("&ldquo;", "“")
        t = t.replace("&rdquo;", "”").replace("&mdash;", ", ")
        return re.sub(r"\s+", " ", t).strip()

    for sec in re.split(r'<section class="sec"', html)[1:]:
        h2 = re.search(r"<h2>(.*?)</h2>", sec, re.S)
        if not h2:
            continue
        sec_name = strip(h2.group(1))
        for block in re.split(r'<div class="story">', sec)[1:]:
            sid_m = re.match(r'<div class="sid">([^<]+)</div>', block)
            sent_m = re.search(r'<div class="sent">(.*?)</div>', block, re.S)
            prove_m = re.search(r'<b>Proven when</b>(.*?)</div>', block, re.S)
            chip_m = re.search(
                r'<span class="chip ([a-z]+)"><span class="dot"></span>(.*?)</span>',
                block, re.S)
            surf_m = re.search(r'<span class="surf">(.*?)</span>', block, re.S)
            if not (sid_m and sent_m and chip_m):
                continue
            sid = sid_m.group(1).strip()
            chip_text = strip(chip_m.group(2))
            note = chip_text.split("·", 1)[1].strip() if "·" in chip_text else ""
            steps[sid] = {
                "id": sid, "sentence": strip(sent_m.group(1)),
                "proven": strip(prove_m.group(1)) if prove_m else "",
                "state": chip_m.group(1), "note": note,
                "surface": strip(surf_m.group(1)) if surf_m else "",
                "sec": sec_name,
            }
        day = re.search(r'<div class="dayone">(.*?)</div>\s*(?:<div class="story">|</section>)', sec, re.S)
        if day:
            block = day.group(1)
            paras = re.findall(r'<p(?: class="(stop)")?>(.*?)</p>', block, re.S)
            narrative_parts, stop_parts = [], []
            order = []
            for cls, body in paras:
                txt = strip(body)
                if cls == "stop":
                    stop_parts.append(txt)
                else:
                    narrative_parts.append(txt)
                for group in re.findall(r"\(([^)]*[A-Z]-\d+[^)]*)\)", body):
                    for ref in re.findall(r"[A-Z]-\d+", group):
                        if ref not in order:
                            order.append(ref)
            personas.append({
                "sec": sec_name,
                "passage": order,
                "narrative": " ".join(narrative_parts)[:900],
                "stopnote": " ".join(stop_parts)[:500],
            })
    for p in personas:
        p["passage"] = [r for r in p["passage"] if r in steps]
    return {
        "steps": steps, "personas": personas,
        "reading": "commons/prd/stories/ parsed at this cut; the journeys "
                   "register (JOURNEYS J-01) is the source this lens waits on",
    }


def parse_marks(text):
    """Address -> (status, mark) from one ledger revision, by the same
    light grammar ledger_entries() reads. Order of appearance kept."""
    out = []
    cur_addr = None
    for line in text.splitlines():
        m = re.match(r"^  - address: (\S+)", line)
        if m:
            cur_addr = m.group(1)
            continue
        m = re.match(r"^\s+status: (.+)$", line)
        if m and cur_addr:
            status = m.group(1).strip()
            if status.startswith("open"):
                mark = status.split("\u00b7", 1)[1].strip() if "\u00b7" in status else "open"
            else:
                mark = status
            out.append((cur_addr, status, mark))
            cur_addr = None
    return out


def succession():
    """The transition recovered from the ledger's own history
    (TRANSDUCER-A1 section 2). The extraction discipline of section 3:
    every distinct state a piece is observed to hold, in the order
    observed, including several on one date. Never collapse a day,
    never order by mark, never smooth. Dates are the commits' own;
    no clock is consulted."""
    revs = []
    out = git("log", "--reverse", "--pretty=%H%x00%cs", "--", "rdm-ledger.yaml")
    for line in out.splitlines():
        if line.strip():
            h, d = line.split("\x00")
            revs.append((h, d))
    pieces = {}
    order = []
    for h, d in revs:
        try:
            text = git("show", f"{h}:rdm-ledger.yaml")
        except subprocess.CalledProcessError:
            continue
        for addr, status, mark in parse_marks(text):
            if addr not in pieces:
                pieces[addr] = []
                order.append(addr)
            hist = pieces[addr]
            if not hist or hist[-1]["mark"] != mark or hist[-1]["status"] != status:
                hist.append({"date": d, "status": status, "mark": mark})
    return {
        "revisions": len(revs),
        "first": revs[0][1] if revs else "",
        "last": revs[-1][1] if revs else "",
        "pieces": [{"id": a, "states": pieces[a]} for a in order],
    }


def stats(files, commits, entries):
    total_bytes = sum(f["size"] for f in files)
    ext_count, ext_bytes = defaultdict(int), defaultdict(int)
    for f in files:
        name = f["path"].rsplit("/", 1)[-1]
        ext = name.rsplit(".", 1)[-1] if "." in name else "(none)"
        ext_count[ext] += 1
        ext_bytes[ext] += f["size"]

    churn, dir_churn, dow, daily = (defaultdict(int) for _ in range(4))
    piles_total = {"tend": 0, "grow": 0}
    piles_dow = defaultdict(lambda: {"tend": 0, "grow": 0})
    for c in commits:
        d = date(*map(int, c["date"].split("-")))
        day_name = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][d.weekday()]
        dow[day_name] += 1
        daily[c["date"]] += 1
        for f in c["files"]:
            churn[f] += 1
            top = f.split("/", 1)[0] if "/" in f else "(root)"
            dir_churn[top] += 1
            pile = ("tend" if f in TENDING_FILES
                    or f.startswith(TENDING_PREFIXES) else "grow")
            piles_total[pile] += 1
            piles_dow[day_name][pile] += 1

    tracked = {f["path"] for f in files}
    beds = defaultdict(int)
    for e in entries:
        beds[e["bed"]] += 1
    grounds = sorted({f["path"].split("/", 1)[0]
                      for f in files if "/" in f["path"]} | {"(root)"})

    dates = sorted(daily)
    last = dates[-1] if dates else ""
    last_d = date(*map(int, last.split("-"))) if last else None
    last7 = sum(n for dstr, n in daily.items()
                if last_d and (last_d - date(*map(int, dstr.split("-")))).days < 7)

    return {
        "totalBytes": total_bytes,
        "fileCount": len(files),
        "ext": sorted(ext_count.items(), key=lambda x: (-x[1], x[0])),
        "extBytes": dict(ext_bytes),
        "churn": sorted(((f, n) for f, n in churn.items() if f in tracked),
                        key=lambda x: (-x[1], x[0]))[:20],
        "dirChurn": sorted(dir_churn.items(), key=lambda x: (-x[1], x[0])),
        "dow": dict(dow),
        "daily": dict(daily),
        "beds": sorted(beds.items(), key=lambda x: (-x[1], x[0])),
        "commits": len(commits),
        "merges": sum(1 for c in commits if c["merge"]),
        "first": dates[0] if dates else "",
        "last": last,
        "last7": last7,
        "ledgerRevisions": churn.get("rdm-ledger.yaml", 0),
        "piles": {
            "total": piles_total,
            "dow": {k: piles_dow[k] for k in sorted(piles_dow)},
            "week_ground": grounds,
        },
    }


def main():
    head = ""
    for line in git("log", "--pretty=%H%x00%cI%x00%s").splitlines():
        h, ci, subj = line.split("\x00")
        if not subj.startswith(REFRESH_MARK):
            head = [h, ci]
            break
    files = tracked_files()
    commits = history()
    entries = ledger_entries()
    snap = {
        "generated": f"{head[1][:10]} at {head[0][:12]}",
        "repo": "Techne-Co-op/techne.coop",
        "branch": "main",
        "files": files,
        "ledger": entries,
        "journeys": journeys(),
        "succession": succession(),
        "stats": stats(files, commits, entries),
    }
    payload = json.dumps(snap, sort_keys=True, ensure_ascii=True,
                         separators=(",", ": "))
    page = PAGE.read_text()
    if "--check" in sys.argv:
        m = re.search(r'<script id="snapshot" type="application/json">(.*?)</script>',
                      page, re.S)
        if m and m.group(1) == payload:
            print(f"current: the cut matches the record at {head[0][:12]}")
            return 0
        print(f"STALE: the embedded cut does not match the record at "
              f"{head[0][:12]}; run scripts/hud_cut.py and commit (TR-03)")
        return 1
    new = re.sub(
        r'(<script id="snapshot" type="application/json">).*?(</script>)',
        lambda m: m.group(1) + payload + m.group(2),
        page, count=1, flags=re.S,
    )
    if new == page:
        print("snapshot block unchanged (same cut)")
    PAGE.write_text(new)
    print(f"cut taken at {head[0][:12]} ({head[1]}): "
          f"{len(files)} files, {len(entries)} pieces, {len(commits)} commits")


if __name__ == "__main__":
    sys.exit(main())
