#!/usr/bin/env python3
"""Validate the rights-safe Cypherpunk Archivist reference register."""
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent
IDS = (
    "hughes-cypherpunk-manifesto",
    "may-crypto-anarchist-manifesto",
    "may-cyphernomicon",
    "cypherpunks-mailing-list",
    "metzdowd-cryptography-list",
    "cypherpunks-anti-license",
    "cryptoparty-handbook",
    "eff-surveillance-self-defense",
)


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    source_path = root / "SOURCES.md"
    sources = source_path.read_text() if source_path.exists() else ""
    body_files = sorted(path.name for path in root.glob("*.md") if path.name != "SOURCES.md")
    if body_files:
        errors.append(f"uncleared source bodies present: {body_files}")
    for source_id in IDS:
        if f"`{source_id}`" not in sources:
            errors.append(f"missing rights-register item: {source_id}")
    if sources.count("Reference-only") != len(IDS):
        errors.append("every named item must remain explicitly reference-only")
    if "applies to code, not to the manifesto's prose" not in sources:
        errors.append("Hughes manifesto must not inherit the text's code-use statement")
    if "non-profit and educational" not in sources or "cannot support this corpus" not in sources:
        errors.append("May reuse restriction must remain explicit")
    if "does not provide a blanket redistribution licence" not in sources:
        errors.append("Cypherpunks archive must remain metadata-only")
    if "does not itself identify the anti-License text" not in sources:
        errors.append("anti-License self-dedication uncertainty must remain explicit")
    if "Do not imitate any named participant" not in sources:
        errors.append("living-person voice-imitation boundary missing")
    return errors


def mutation_test() -> None:
    cases = [
        (
            "uncleared body",
            lambda root: (root / "hughes.md").write_text("uncleared text\n"),
            "uncleared source bodies",
        ),
        (
            "register completeness",
            lambda root: (root / "SOURCES.md").write_text(
                (root / "SOURCES.md").read_text().replace(
                    "`may-crypto-anarchist-manifesto`", "`removed`"
                )
            ),
            "missing rights-register item",
        ),
        (
            "rights class",
            lambda root: (root / "SOURCES.md").write_text(
                (root / "SOURCES.md").read_text().replace("**Reference-only.**", "**Copied.**", 1)
            ),
            "explicitly reference-only",
        ),
        (
            "licence interpretation",
            lambda root: (root / "SOURCES.md").write_text(
                (root / "SOURCES.md")
                .read_text()
                .replace("applies to code, not to the manifesto's prose", "licenses all prose")
            ),
            "must not inherit",
        ),
        (
            "voice boundary",
            lambda root: (root / "SOURCES.md").write_text(
                (root / "SOURCES.md")
                .read_text()
                .replace("Do not imitate any named participant", "Imitate participants")
            ),
            "voice-imitation boundary",
        ),
    ]
    for label, mutate, expected in cases:
        with tempfile.TemporaryDirectory() as temp:
            fixture = Path(temp) / "corpus"
            shutil.copytree(ROOT, fixture, ignore=shutil.ignore_patterns("__pycache__"))
            mutate(fixture)
            failures = validate(fixture)
            assert any(expected in failure for failure in failures), (
                f"{label} mutation accepted: {failures}"
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mutation-test", action="store_true")
    args = parser.parse_args()
    if args.mutation_test:
        mutation_test()
        print("mutation tests: PASS (5 validation-rule mutations rejected)")
    failures = validate(ROOT)
    if failures:
        print("\n".join(failures))
        raise SystemExit(1)
    print(f"Cypherpunk Archivist corpus: PASS (0 copied bodies; {len(IDS)} references)")
