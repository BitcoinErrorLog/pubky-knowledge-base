#!/usr/bin/env python3
"""Validate the Diogenes Book VI testimony corpus."""
from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent
NAMES = ("antisthenes", "diogenes", "monimus", "onesicritus", "crates", "metrocles", "hipparchia", "menippus", "menedemus")
EXPECTED = {f"diogenes-laertius-book-06-{i:02d}-{name}-yonge.md" for i, name in enumerate(NAMES, 1)}
EXPECTED.add("diogenes-laertius-book-06-10-notes-yonge.md")
REQUIRED = ("title", "author", "date", "original_url", "archive_url", "source_collection", "rights_status", "retrieval_date", "checksum")
MARKERS = ("*** START OF", "*** END OF", "PROJECT GUTENBERG EBOOK", "Project Gutenberg License")


def split(path: Path) -> tuple[str, str]:
    data = path.read_text()
    if not data.startswith("---\n") or data.count("---\n") < 2:
        return "", data
    frontmatter, body = data.split("---\n", 2)[1:]
    return frontmatter, body.lstrip("\n")


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    sources = (root / "SOURCES.md").read_text() if (root / "SOURCES.md").exists() else ""
    actual = {path.name for path in root.glob("*.md") if path.name != "SOURCES.md"}
    if actual != EXPECTED:
        errors.append(f"document set mismatch: missing={sorted(EXPECTED-actual)}, unexpected={sorted(actual-EXPECTED)}")
    if "later testimony" not in sources or "not writing authored by Diogenes" not in sources:
        errors.append("SOURCES.md must label Book VI as later testimony, not Diogenes-authored text")
    if "Charles Duke Yonge died in 1891" not in sources:
        errors.append("SOURCES.md must state Yonge's worldwide public-domain basis")

    for name in sorted(EXPECTED & actual):
        frontmatter, body = split(root / name)
        if not frontmatter:
            errors.append(f"{name}: missing frontmatter")
            continue
        for field in REQUIRED:
            if not re.search(rf"^{field}:", frontmatter, re.MULTILINE):
                errors.append(f"{name}: missing {field}")
        checksum = re.search(r'^checksum: "sha256:([0-9a-f]{64})"$', frontmatter, re.MULTILINE)
        if not checksum or checksum.group(1) != hashlib.sha256(body.encode()).hexdigest():
            errors.append(f"{name}: checksum mismatch")
        if not body.strip():
            errors.append(f"{name}: empty body")
        if name not in sources:
            errors.append(f"{name}: missing SOURCES.md register entry")
        if "Charles Duke Yonge" not in frontmatter or "died 1891" not in frontmatter:
            errors.append(f"{name}: missing Yonge translation identity")
        if "public domain worldwide" not in frontmatter:
            errors.append(f"{name}: missing worldwide public-domain status")
        if any(marker.casefold() in body.casefold() for marker in MARKERS):
            errors.append(f"{name}: contains Gutenberg boilerplate")
        is_notes = name.endswith("-10-notes-yonge.md")
        if (not is_notes and not body.startswith("BOOK VI.\n\n")) or "BOOK VII." in body:
            errors.append(f"{name}: body falls outside Book VI")
        if is_notes:
            if not body.startswith("[54]") or re.search(r"^\[81\]", body, re.MULTILINE):
                errors.append(f"{name}: body is not limited to Book VI notes 54-80")
        else:
            expected_heading = "THE LIFE OF MENEDEMUS." if name.endswith("-menedemus-yonge.md") else f"LIFE OF {name.split('-')[-2].upper()}."
            if expected_heading not in body:
                errors.append(f"{name}: body heading does not match file label")
    return errors


def mutation_test() -> None:
    target = "diogenes-laertius-book-06-02-diogenes-yonge.md"
    cases = [
        ("document set", lambda r: (r / target).unlink(), "document set mismatch"),
        ("frontmatter", lambda r: (r / target).write_text((r / target).read_text().replace('author: "Diogenes Laërtius; translated by Charles Duke Yonge"\n', "")), "missing author"),
        ("checksum", lambda r: (r / target).write_text((r / target).read_text() + "x"), "checksum mismatch"),
        ("register", lambda r: (r / "SOURCES.md").write_text((r / "SOURCES.md").read_text().replace(f"`{target}`", "`removed.md`")), "missing SOURCES.md"),
        ("boilerplate", lambda r: (r / target).write_text((r / target).read_text() + "\n*** END OF THE PROJECT GUTENBERG EBOOK ***\n"), "Gutenberg boilerplate"),
        ("edition", lambda r: (r / target).write_text((r / target).read_text().replace("Charles Duke Yonge", "Unknown")), "Yonge translation identity"),
        ("book scope", lambda r: (r / target).write_text((r / target).read_text() + "\nBOOK VII.\n"), "outside Book VI"),
        ("heading", lambda r: (r / target).write_text((r / target).read_text().replace("LIFE OF DIOGENES.", "LIFE OF CRATES.")), "heading does not match"),
    ]
    for label, mutate, expected in cases:
        with tempfile.TemporaryDirectory() as temp:
            fixture = Path(temp) / "corpus"
            shutil.copytree(ROOT, fixture, ignore=shutil.ignore_patterns("__pycache__"))
            mutate(fixture)
            failures = validate(fixture)
            assert any(expected in failure for failure in failures), f"{label} mutation accepted: {failures}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mutation-test", action="store_true")
    args = parser.parse_args()
    if args.mutation_test:
        mutation_test()
        print("mutation tests: PASS (8 validation-rule mutations rejected)")
    failures = validate(ROOT)
    if failures:
        print("\n".join(failures))
        raise SystemExit(1)
    print(f"Diogenes corpus: PASS ({len(EXPECTED)} Book VI source documents)")
