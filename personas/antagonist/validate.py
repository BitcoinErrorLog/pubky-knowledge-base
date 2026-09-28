#!/usr/bin/env python3
"""Validate the Antagonist corpus provenance, scope, and integrity."""
from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent
REQUIRED = ("title", "author", "date", "original_url", "archive_url", "source_collection", "rights_status", "retrieval_date", "checksum")
EXPECTED = {
    *(f"aristotle-rhetoric-book-01-part-{n:02d}-roberts.md" for n in range(1, 16)),
    *(f"aristotle-rhetoric-book-02-part-{n:02d}-roberts.md" for n in range(1, 27)),
    *(f"aristotle-rhetoric-book-03-part-{n:02d}-roberts.md" for n in range(1, 20)),
    "schopenhauer-art-of-controversy-saunders-1896.md",
    "mill-on-liberty-chapter-02.md",
    "bacon-novum-organum-idols-devey.md",
}
MARKERS = ("*** START OF", "*** END OF", "PROJECT GUTENBERG EBOOK", "Project Gutenberg License")
FICTION = ("Othello", "Paradise Lost", "Moby-Dick", "Dracula")


def split(path: Path) -> tuple[str, str]:
    data = path.read_text()
    if not data.startswith("---\n") or data.count("---\n") < 2:
        return "", data
    frontmatter, body = data.split("---\n", 2)[1:]
    return frontmatter, body.lstrip("\n")


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    sources = (root / "SOURCES.md").read_text() if (root / "SOURCES.md").exists() else ""
    actual = {p.name for p in root.glob("*.md") if p.name != "SOURCES.md"}
    if actual != EXPECTED:
        errors.append(f"document set mismatch: missing={sorted(EXPECTED-actual)}, unexpected={sorted(actual-EXPECTED)}")
    if "reference-only" not in sources or "Pickard-Cambridge died in 1957" not in sources:
        errors.append("SOURCES.md must keep Pickard-Cambridge reference-only with death date")
    if any(title not in sources for title in FICTION):
        errors.append("SOURCES.md must explicitly exclude the literary-villain sources")

    for name in sorted(EXPECTED & actual):
        frontmatter, body = split(root / name)
        if not frontmatter:
            errors.append(f"{name}: missing frontmatter")
            continue
        for field in REQUIRED:
            if not re.search(rf"^{field}:", frontmatter, re.MULTILINE):
                errors.append(f"{name}: missing {field}")
        match = re.search(r'^checksum: "sha256:([0-9a-f]{64})"$', frontmatter, re.MULTILINE)
        if not match or match.group(1) != hashlib.sha256(body.encode()).hexdigest():
            errors.append(f"{name}: checksum mismatch")
        if not body.strip():
            errors.append(f"{name}: empty body")
        if name not in sources:
            errors.append(f"{name}: missing SOURCES.md register entry")
        if "public domain worldwide" not in frontmatter:
            errors.append(f"{name}: missing worldwide public-domain basis")
        if any(marker.casefold() in body.casefold() for marker in MARKERS):
            errors.append(f"{name}: contains Gutenberg boilerplate")
        if any(title.casefold() in body.casefold() for title in FICTION):
            errors.append(f"{name}: contains prohibited literary-villain material")

        if name.startswith("aristotle-rhetoric-"):
            if "W. Rhys Roberts" not in frontmatter or "died 1940" not in frontmatter:
                errors.append(f"{name}: missing Roberts translation identity")
            if not re.match(r"^BOOK [IVX]+\n\nPart \d+", body):
                errors.append(f"{name}: body is not one Rhetoric part")
        elif name.startswith("schopenhauer-"):
            if "T. Bailey Saunders" not in frontmatter or "died 1928" not in frontmatter:
                errors.append(f"{name}: missing Saunders 1896 translation identity")
        elif name.startswith("mill-"):
            if not body.startswith("CHAPTER II.") or re.search(r"^CHAPTER III\.", body, re.MULTILINE):
                errors.append(f"{name}: body is not limited to On Liberty chapter II")
        elif name.startswith("bacon-"):
            if "Joseph Devey" not in frontmatter or "died 1897" not in frontmatter:
                errors.append(f"{name}: missing Devey translation identity")
            if not body.startswith("XXXVIII.") or re.search(r"^LXIX\.", body, re.MULTILINE):
                errors.append(f"{name}: body is not limited to aphorisms XXXVIII-LXVIII")
    return errors


def mutation_test() -> None:
    target = "aristotle-rhetoric-book-01-part-01-roberts.md"
    cases = [
        ("document set", lambda r: (r / target).unlink(), "document set mismatch"),
        ("frontmatter", lambda r: (r / target).write_text((r / target).read_text().replace('author: "Aristotle; translated by W. Rhys Roberts"\n', "")), "missing author"),
        ("checksum", lambda r: (r / target).write_text((r / target).read_text() + "x"), "checksum mismatch"),
        ("register", lambda r: (r / "SOURCES.md").write_text((r / "SOURCES.md").read_text().replace(f"`{target}`", "`removed.md`")), "missing SOURCES.md"),
        ("boilerplate", lambda r: (r / target).write_text((r / target).read_text() + "\n*** END OF THE PROJECT GUTENBERG EBOOK ***\n"), "Gutenberg boilerplate"),
        ("fiction", lambda r: (r / target).write_text((r / target).read_text() + "\nOthello\n"), "literary-villain material"),
        ("translation", lambda r: (r / target).write_text((r / target).read_text().replace("W. Rhys Roberts", "Unknown")), "Roberts translation identity"),
        ("scope", lambda r: (r / "mill-on-liberty-chapter-02.md").write_text((r / "mill-on-liberty-chapter-02.md").read_text() + "\nCHAPTER III.\n"), "limited to On Liberty chapter II"),
    ]
    for label, mutate, expected in cases:
        with tempfile.TemporaryDirectory() as temp:
            fixture = Path(temp) / "corpus"
            shutil.copytree(ROOT, fixture, ignore=shutil.ignore_patterns("__pycache__"))
            mutate(fixture)
            found = validate(fixture)
            assert any(expected in error for error in found), f"{label} mutation accepted: {found}"


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
    print(f"Antagonist corpus: PASS ({len(EXPECTED)} source documents)")
