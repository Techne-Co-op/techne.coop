#!/usr/bin/env python3
"""BP v1 section 6 as a check: no em dashes in authored documents.

Two exemptions, and they are the same exemption stated twice. Text the
cooperative may not reformat is exempt: the ratified instruments under
legal/, which carry the original instrument text, and verbatim quotation
set apart in a .said block, which carries what a person actually said.
Repunctuating either would edit a record to satisfy a style rule.
Everything else, including the authored framing around a quotation, is
checked.
"""
import re
import subprocess
import sys

SAID = re.compile(r'<div class="said">.*?</div>', re.S)

files = subprocess.run(
    ["git", "ls-files", "*.html", "*.md"],
    capture_output=True, text=True, check=True,
).stdout.split()

bad = []
for path in files:
    if path.startswith("legal/"):
        continue
    try:
        text = open(path, encoding="utf-8").read()
    except (UnicodeDecodeError, FileNotFoundError):
        continue
    authored = SAID.sub(lambda m: " " * (m.end() - m.start()), text)
    for n, line in enumerate(authored.split("\n"), 1):
        if "—" in line:
            bad.append(f"{path}:{n}: {line.strip()[:120]}")

if bad:
    print("\n".join(bad))
    print("::error::em dash found; use commas, colons, or restructure (BP v1 section 6)")
    sys.exit(1)
print(f"em dash audit: {len(files)} files, clean")
