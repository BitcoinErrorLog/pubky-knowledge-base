#!/usr/bin/env python3
"""Validate the Coach corpus structure, provenance, scope, and body hashes."""
from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent
REQUIRED = (
    "title",
    "author",
    "date",
    "original_url",
    "archive_url",
    "source_collection",
    "rights_status",
    "retrieval_date",
    "checksum",
)
EXPECTED = {
    "epictetus-encheiridion-long.md",
    "franklin-autobiography-virtues.md",
    "william-james-principles-chapter-04-habit.md",
    "arnold-bennett-how-to-live-on-24-hours-a-day.md",
    *(f"marcus-aurelius-meditations-book-{number:02d}-long.md" for number in range(1, 13)),
    *(f"seneca-moral-letter-{number:03d}-gummere.md" for number in range(1, 14)),
}
GUTENBERG_MARKERS = (
    "*** START OF",
    "*** END OF",
    "PROJECT GUTENBERG EBOOK",
    "Project Gutenberg EBook",
    "Project Gutenberg License",
)


def split_document(path: Path) -> tuple[str, str]:
    data = path.read_text()
    if not data.startswith("---\n") or data.count("---\n") < 2:
        return "", data
    frontmatter, body = data.split("---\n", 2)[1:]
    return frontmatter, body.lstrip("\n")


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    sources_path = root / "SOURCES.md"
    sources = sources_path.read_text() if sources_path.exists() else ""
    actual = {path.name for path in root.glob("*.md") if path.name != "SOURCES.md"}
    if actual != EXPECTED:
        errors.append(
            f"document set mismatch: missing={sorted(EXPECTED - actual)}, "
            f"unexpected={sorted(actual - EXPECTED)}"
        )

    for name in sorted(EXPECTED & actual):
        path = root / name
        frontmatter, body = split_document(path)
        if not frontmatter:
            errors.append(f"{name}: missing frontmatter")
            continue
        for field in REQUIRED:
            if not re.search(rf"^{field}:", frontmatter, re.MULTILINE):
                errors.append(f"{name}: missing {field}")
        checksum = re.search(
            r'^checksum: "sha256:([0-9a-f]{64})"$', frontmatter, re.MULTILINE
        )
        if not checksum or checksum.group(1) != hashlib.sha256(body.encode()).hexdigest():
            errors.append(f"{name}: checksum mismatch")
        if not body.strip():
            errors.append(f"{name}: empty body")
        if name not in sources:
            errors.append(f"{name}: missing SOURCES.md register entry")
        if any(marker.casefold() in body.casefold() for marker in GUTENBERG_MARKERS):
            errors.append(f"{name}: contains Gutenberg boilerplate marker")
        if "public domain worldwide" not in frontmatter:
            errors.append(f"{name}: missing worldwide public-domain basis")

        if name == "epictetus-encheiridion-long.md":
            if (
                "George Long" not in frontmatter
                or "died 1879" not in frontmatter
                or any(label in frontmatter for label in ("Higginson", "Salomon", "Casaubon"))
            ):
                errors.append(f"{name}: edition or translator is mislabelled")
            if not body.startswith("THE ENCHEIRIDION, OR MANUAL."):
                errors.append(f"{name}: body is not the Encheiridion")
        elif name.startswith("marcus-aurelius-"):
            if "George Long" not in frontmatter or "first published 1862" not in frontmatter:
                errors.append(f"{name}: missing Long 1862 translation identity")
            if not body.startswith("BOOK "):
                errors.append(f"{name}: body is not a Meditations book")
        elif name.startswith("seneca-"):
            if "Richard M. Gummere" not in frontmatter or "died 1936" not in frontmatter:
                errors.append(f"{name}: missing Gummere translation identity")
        elif name == "franklin-autobiography-virtues.md":
            if "Harvard Classics" not in frontmatter or "Charles W. Eliot" not in frontmatter:
                errors.append(f"{name}: missing named 1909 edition")
        elif name == "william-james-principles-chapter-04-habit.md":
            if not body.startswith("CHAPTER IV.") or re.search(r"^CHAPTER V\.", body, re.MULTILINE):
                errors.append(f"{name}: body is not limited to Chapter IV, Habit")
        elif name == "arnold-bennett-how-to-live-on-24-hours-a-day.md":
            if "First published 1908" not in frontmatter:
                errors.append(f"{name}: missing 1908 edition identity")
    return errors


def mutation_test() -> None:
    mutations = [
        (
            "document set",
            lambda root: (root / "seneca-moral-letter-013-gummere.md").unlink(),
            "document set mismatch",
        ),
        (
            "frontmatter field",
            lambda root: (root / "epictetus-encheiridion-long.md").write_text(
                (root / "epictetus-encheiridion-long.md")
                .read_text()
                .replace('author: "Epictetus; translated by George Long"\n', "")
            ),
            "missing author",
        ),
        (
            "checksum",
            lambda root: (root / "marcus-aurelius-meditations-book-01-long.md").write_text(
                (root / "marcus-aurelius-meditations-book-01-long.md").read_text() + "x"
            ),
            "checksum mismatch",
        ),
        (
            "non-empty body",
            lambda root: (root / "seneca-moral-letter-001-gummere.md").write_text(
                (root / "seneca-moral-letter-001-gummere.md").read_text().split("---\n", 2)[0]
                + "---\n"
                + (root / "seneca-moral-letter-001-gummere.md")
                .read_text()
                .split("---\n", 2)[1]
                + "---\n\n"
            ),
            "empty body",
        ),
        (
            "source register",
            lambda root: (root / "SOURCES.md").write_text(
                (root / "SOURCES.md")
                .read_text()
                .replace("`franklin-autobiography-virtues.md`", "`removed.md`")
            ),
            "missing SOURCES.md register entry",
        ),
        (
            "Gutenberg boilerplate",
            lambda root: (root / "arnold-bennett-how-to-live-on-24-hours-a-day.md").write_text(
                (root / "arnold-bennett-how-to-live-on-24-hours-a-day.md").read_text()
                + "\n*** END OF THE PROJECT GUTENBERG EBOOK ***\n"
            ),
            "Gutenberg boilerplate marker",
        ),
        (
            "worldwide rights",
            lambda root: (root / "franklin-autobiography-virtues.md").write_text(
                (root / "franklin-autobiography-virtues.md")
                .read_text()
                .replace("public domain worldwide", "public domain")
            ),
            "missing worldwide public-domain basis",
        ),
        (
            "edition identity",
            lambda root: (root / "epictetus-encheiridion-long.md").write_text(
                (root / "epictetus-encheiridion-long.md")
                .read_text()
                .replace("George Long", "Thomas Wentworth Higginson")
            ),
            "edition or translator is mislabelled",
        ),
        (
            "chapter scope",
            lambda root: (root / "william-james-principles-chapter-04-habit.md").write_text(
                (root / "william-james-principles-chapter-04-habit.md").read_text()
                + "\nCHAPTER V.\n"
            ),
            "not limited to Chapter IV",
        ),
    ]
    for label, mutate, expected_error in mutations:
        with tempfile.TemporaryDirectory() as temp:
            fixture = Path(temp) / "corpus"
            shutil.copytree(ROOT, fixture, ignore=shutil.ignore_patterns("__pycache__"))
            mutate(fixture)
            errors = validate(fixture)
            assert any(expected_error in error for error in errors), (
                f"{label} mutation was accepted; expected {expected_error!r}, got {errors!r}"
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mutation-test", action="store_true")
    args = parser.parse_args()
    if args.mutation_test:
        mutation_test()
        print("mutation tests: PASS (9 validation-rule mutations rejected)")
    failures = validate(ROOT)
    if failures:
        print("\n".join(failures))
        raise SystemExit(1)
    print(f"Coach corpus: PASS ({len(EXPECTED)} source documents)")
