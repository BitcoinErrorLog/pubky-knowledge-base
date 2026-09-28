#!/usr/bin/env python3
"""Fetch allowlisted UI/UX leaves and write matching provenance frontmatter."""
from __future__ import annotations

import hashlib
import pathlib
import re
import subprocess
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
RAW = ROOT / "sources" / "leaves"
META = ROOT / "records"
SEEDS = {
    "w3c-wcag": (
        "https://www.w3.org/WAI/WCAG22/Understanding/",
        re.compile(r'^https://www\.w3\.org/WAI/WCAG22/Understanding/'),
        "w3c-document-license-immutable-copy",
    ),
    "w3c-apg": (
        "https://www.w3.org/WAI/ARIA/apg/patterns/",
        re.compile(r'^https://www\.w3\.org/WAI/ARIA/apg/patterns/'),
        "w3c-document-license-immutable-copy",
    ),
    "govuk": (
        "https://design-system.service.gov.uk/components/",
        re.compile(r'^https://design-system\.service\.gov\.uk/(?:components|patterns)/'),
        "open-government-licence-v3",
    ),
    "uswds": (
        "https://designsystem.digital.gov/components/overview/",
        re.compile(r'^https://designsystem\.digital\.gov/components/'),
        "uswds-public-domain-with-file-level-exclusions",
    ),
}

def get(url: str) -> bytes:
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "JebPersonaCorpus/1.0"}), timeout=30).read()

def links(base: str, body: bytes, allowed: re.Pattern[str]) -> list[str]:
    from urllib.parse import urljoin
    return sorted({u.split("#")[0] for u in (urljoin(base, x.decode()) for x in re.findall(rb'href=["\']([^"\']+)', body)) if allowed.match(u.split("#")[0])})

def save(collection: str, url: str, rights: str, body: bytes) -> None:
    key = hashlib.sha256(url.encode()).hexdigest()[:16]
    RAW.mkdir(parents=True, exist_ok=True); META.mkdir(parents=True, exist_ok=True)
    raw = RAW / f"{collection}-{key}.html"; raw.write_bytes(body)
    digest = hashlib.sha256(body).hexdigest()
    (META / f"{collection}-{key}.md").write_text(
        f"---\ntitle: \"verbatim upstream HTML\"\nauthor: \"{collection}\"\ndate: \"2026-09-28\"\noriginal_url: \"{url}\"\narchive_url: null\nsource_collection: \"{collection}\"\nrights_status: \"{rights}\"\nretrieval_date: \"2026-09-28\"\nchecksum: \"{digest}\"\n---\n\nExact payload: `../sources/leaves/{raw.name}`.\n",
        encoding="utf-8")

def main() -> None:
    if sys.argv[1:] == ["--verify"]:
        for record in META.glob("*.md"):
            raw = RAW / record.read_text().split("sources/leaves/")[1].split("`")[0]
            assert hashlib.sha256(raw.read_bytes()).hexdigest() in record.read_text(), record
        return
    for collection, (seed, allowed, rights) in SEEDS.items():
        index = get(seed); save(collection, seed, rights, index)
        for url in links(seed, index, allowed):
            save(collection, url, rights, get(url))

if __name__ == "__main__":
    main()
