#!/usr/bin/env python3
import re, tarfile
from pathlib import Path

root = Path(__file__).resolve().parent
archive = next((root / "sources").glob("bips-*.tar.gz"))
allowed = {"BSD-2-Clause", "BSD-3-Clause", "CC0-1.0", "CC-BY-4.0", "MIT", "PD", "OPL"}
rows = []
with tarfile.open(archive) as tar:
    for member in sorted((m for m in tar.getmembers() if re.search(r"/bip-\d+.*\.mediawiki$", m.name)), key=lambda m: m.name):
        text = tar.extractfile(member).read().decode("utf-8", "replace")
        number = re.search(r"bip-(\d+)", member.name).group(1).lstrip("0") or "0"
        title = (re.search(r"^  Title:\s*(.+)$", text, re.M) or [None, "Untitled"])[1].strip()
        declaration = (re.search(r"^  License:\s*(.+)$", text, re.M) or [None, "missing"])[1].strip()
        tokens = set(re.findall(r"(?:BSD-[23]-Clause|CC0-1\.0|CC-BY-4\.0|MIT|PD|OPL)", declaration))
        status = "included" if tokens and tokens <= allowed else "reference-only"
        rows.append((int(number), title, declaration, status))
out = ["# BIP rights manifest", "", "| BIP | Title | License declaration | Status | Canonical URL |", "| ---: | --- | --- | --- | --- |"]
for number, title, declaration, status in rows:
    out.append(f"| {number} | {title.replace('|', '\\|')} | {declaration.replace('|', '\\|')} | {status} | https://github.com/bitcoin/bips/blob/3a10b5b5f0a7586df8928d580a3009744ebb2079/bip-{number:04}.mediawiki |")
(root / "BIP-RIGHTS.md").write_text("\n".join(out) + "\n")
print(f"included={sum(r[3]=='included' for r in rows)} quarantined={sum(r[3]!='included' for r in rows)}")
