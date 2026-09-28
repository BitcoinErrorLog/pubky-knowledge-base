#!/usr/bin/env python3
"""Validate Sun Tzu corpus provenance, attribution, and source integrity."""
from __future__ import annotations

import argparse
import hashlib
import re
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent
REQUIRED = ("title", "author", "date", "original_url", "archive_url", "source_collection", "rights_status", "retrieval_date", "checksum")
BANNED = ("[编辑]", "返回頂部", "维基百科條目", "Lionel Giles", "THE ART OF WAR")

def validate(root: Path) -> list[str]:
    errors: list[str] = []
    sources = (root / "SOURCES.md").read_text() if (root / "SOURCES.md").exists() else ""
    chapters = sorted(root.glob("chapter-*.md"))
    if len(chapters) != 13:
        errors.append(f"expected 13 chapter files, found {len(chapters)}")
    if "Giles" not in sources or "reference-only" not in sources:
        errors.append("SOURCES.md must state that Giles is reference-only")
    for path in chapters:
        data = path.read_text()
        if not data.startswith("---\n") or data.count("---\n") < 2:
            errors.append(f"{path.name}: missing frontmatter")
            continue
        frontmatter, body = data.split("---\n", 2)[1:]
        body = body.lstrip("\n")
        for field in REQUIRED:
            if not re.search(rf"^{field}:", frontmatter, re.M):
                errors.append(f"{path.name}: missing {field}")
        checksum = re.search(r'^checksum: "sha256:([0-9a-f]{64})"$', frontmatter, re.M)
        if not checksum or checksum.group(1) != hashlib.sha256(body.encode()).hexdigest():
            errors.append(f"{path.name}: checksum mismatch")
        if not body.strip():
            errors.append(f"{path.name}: empty body")
        if "public domain" not in frontmatter.lower() or "CC BY-SA" not in frontmatter:
            errors.append(f"{path.name}: incomplete rights attribution")
        if any(term in body for term in BANNED):
            errors.append(f"{path.name}: prohibited site or translation text")
        if path.stem not in sources:
            errors.append(f"{path.name}: missing SOURCES.md register entry")
    return errors

def mutation_test() -> None:
    with tempfile.TemporaryDirectory() as temp:
        fixture = Path(temp)
        (fixture / "SOURCES.md").write_text("Giles reference-only\n")
        (fixture / "chapter-01.md").write_text("---\ntitle: x\n---\n\n")
        assert validate(fixture), "validator accepted intentionally malformed corpus"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mutation-test", action="store_true")
    args = parser.parse_args()
    if args.mutation_test:
        mutation_test()
        print("mutation test: PASS (malformed fixture rejected)")
    errors = validate(ROOT)
    if errors:
        print("\n".join(errors))
        raise SystemExit(1)
    print("Sun Tzu corpus: PASS (13 attributed non-empty chapter bodies; checksums and rights register verified)")
