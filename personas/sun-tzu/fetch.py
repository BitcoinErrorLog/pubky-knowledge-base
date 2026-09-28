#!/usr/bin/env python3
"""Fetch and materialize the thirteen received chapters of 孫子兵法."""
from __future__ import annotations

import hashlib
import html
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
SOURCE_URL = "https://zh.wikisource.org/w/api.php?action=parse&page=%E5%AD%AB%E5%AD%90%E5%85%B5%E6%B3%95&prop=text&format=json"
PAGE_URL = "https://zh.wikisource.org/wiki/%E5%AD%AB%E5%AD%90%E5%85%B5%E6%B3%95"
CALTHROP_URL = "https://www.gutenberg.org/files/44024/44024-0.txt"
CALTHROP_ARCHIVE_URL = "https://archive.org/details/bookofwarmilitar00caltiala"
RETRIEVAL_DATE = "2026-09-28"
CHAPTER_RE = re.compile(r"^(始計|作戰|謀攻|軍形|兵勢|虛實|軍爭|九變|行軍|地形|九地|火攻|用間)第[一二三四五六七八九十]+$", re.M)
CALTHROP_HEADINGS = (
    "PRELIMINARY RECKONING", "OPERATIONS OF WAR", "THE ATTACK BY STRATAGEM",
    "THE ORDER OF BATTLE", "THE SPIRIT OF THE TROOPS", "EMPTINESS AND STRENGTH",
    "BATTLE TACTICS", "THE NINE CHANGES", "MOVEMENT OF TROOPS", "GROUND",
    "THE NINE GROUNDS", "ASSAULT BY FIRE", "THE EMPLOYMENT OF SPIES",
)

def clean_rendered_html(markup: str) -> str:
    markup = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", markup, flags=re.S | re.I)
    markup = re.sub(r"<br\s*/?>", "\n", markup, flags=re.I)
    markup = re.sub(r"</(p|div|h[1-6]|li|tr|table|section|blockquote)>", "\n", markup, flags=re.I)
    text = html.unescape(re.sub(r"<[^>]+>", "", markup)).replace("\xa0", " ")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text[text.index("始計第一"):]
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line not in {"[编辑]", "返回頂部"} and "返回頂部" not in line and "维基" not in line]
    return "\n\n".join(line for line in lines if line).strip() + "\n"

def frontmatter(title: str, checksum: str, *, calthrop: bool = False) -> str:
    author = "Sun Tzu (attributed); translated by E. F. Calthrop" if calthrop else "Sun Tzu (attributed)"
    original_url = CALTHROP_URL if calthrop else f"{PAGE_URL}#{title}"
    archive_url = CALTHROP_ARCHIVE_URL if calthrop else PAGE_URL
    collection = "Project Gutenberg ebook 44024, transcribed from Calthrop's 1908 London edition" if calthrop else "Chinese Wikisource rendered ancient-text transcription"
    rights = "Calthrop died in 1915; his 1908 English translation is public domain worldwide under ordinary life-plus-70 terms" if calthrop else "Ancient underlying text is public domain; rendered Wikisource transcription is CC BY-SA 3.0"
    date = "1908 Calthrop edition" if calthrop else f"Ancient text; rendered revision retrieved {RETRIEVAL_DATE}"
    return f'''---
title: "{title}"
author: "{author}"
date: "{date}"
original_url: "{original_url}"
archive_url: "{archive_url}"
source_collection: "{collection}"
rights_status: "{rights}"
retrieval_date: "{RETRIEVAL_DATE}"
checksum: "sha256:{checksum}"
---

'''

def split_chapters(text: str) -> list[tuple[str, str]]:
    positions = [(m.start(), m.group(0)) for m in CHAPTER_RE.finditer(text)]
    if len(positions) != 13:
        raise ValueError(f"expected 13 received chapters, found {len(positions)}")
    return [(title, text[start:(positions[i + 1][0] if i + 1 < len(positions) else len(text))].strip() + "\n") for i, (start, title) in enumerate(positions)]

def calthrop_chapters(text: str) -> list[tuple[str, str]]:
    text = text.replace("\r\n", "\n")
    start = text.index("I\n\nPRELIMINARY RECKONING", 1_000)
    text = text[start:text.index("THE SAYINGS OF WUTZU", start)]
    matches = []
    for index, heading in enumerate(CALTHROP_HEADINGS, start=1):
        match = re.search(rf"^{['I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII','XIII'][index - 1]}\s*\n+\s*{re.escape(heading)}[ \t]*$", text, re.M)
        if not match:
            raise ValueError(f"missing Calthrop chapter {index}: {heading}")
        matches.append((match.start(), f"{index}. {heading}"))
    return [(title, re.sub(r"\[\d+\]", "", text[start:(matches[i + 1][0] if i + 1 < len(matches) else len(text))]).strip() + "\n") for i, (start, title) in enumerate(matches)]

def main() -> None:
    request = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "pubky-knowledge-base-corpus-fetch/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        markup = json.load(response)["parse"]["text"]["*"]
    chapters = split_chapters(clean_rendered_html(markup))
    with urllib.request.urlopen(urllib.request.Request(CALTHROP_URL, headers={"User-Agent": "pubky-knowledge-base-corpus-fetch/1.0"}), timeout=30) as response:
        calthrop = calthrop_chapters(response.read().decode("utf-8"))
    for path in ROOT.glob("chapter-*.md"):
        path.unlink()
    for path in ROOT.glob("calthrop-chapter-*.md"):
        path.unlink()
    rows = []
    for index, (title, body) in enumerate(chapters, start=1):
        checksum = hashlib.sha256(body.encode()).hexdigest()
        filename = f"chapter-{index:02d}.md"
        (ROOT / filename).write_text(frontmatter(title, checksum) + body)
        rows.append(f"| sun-tzu-chapter-{index:02d} | *孫子兵法* — {title} | Ancient underlying text is public domain; rendered transcription is CC BY-SA 3.0. | Yes | [{title}]({PAGE_URL}#{title}), retrieved {RETRIEVAL_DATE}; site navigation and annotations excluded. | `sha256:{checksum}` |")
    for index, (title, body) in enumerate(calthrop, start=1):
        checksum = hashlib.sha256(body.encode()).hexdigest()
        filename = f"calthrop-chapter-{index:02d}.md"
        (ROOT / filename).write_text(frontmatter(title, checksum, calthrop=True) + body)
        rows.append(f"| calthrop-chapter-{index:02d} | Calthrop, *The Book of War* — {title} | Calthrop died in 1915; his 1908 translation is public domain worldwide under ordinary life-plus-70 terms. | Yes | [Gutenberg 44024]({CALTHROP_URL}), transcribed from [Internet Archive's 1908 scan]({CALTHROP_ARCHIVE_URL}); retrieved {RETRIEVAL_DATE}. Introductory/editorial and Wutzu material excluded. | `sha256:{checksum}` |")
    (ROOT / "SOURCES.md").write_text("# Sun Tzu sources\n\n| ID | Item | Rights basis | Copied text | Provenance | SHA-256 |\n| --- | --- | --- | --- | --- | --- |\n" + "\n".join(rows) + "\n\nCalthrop's 1908 translation is retained as an English companion to the original Chinese; its vocabulary and rendering choices differ from Lionel Giles's translation. Reference-only: Lionel Giles’s 1910 English translation is public domain in the United States but remains copyright-protected in ordinary life-plus-70 jurisdictions until 2029; its body is not copied. [Gutenberg record](https://www.gutenberg.org/ebooks/132). [Britannica](https://www.britannica.com/biography/Sunzi) is reference-only.\n")

if __name__ == "__main__":
    main()
