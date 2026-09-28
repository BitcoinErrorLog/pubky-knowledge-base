#!/usr/bin/env python3
"""Independently validate the Malmi and Hearn correspondence records."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

MALMI_URL = "https://mmalmi.github.io/satoshi/"
HEARN_ROOT = "https://plan99.net/~mike/satoshi-emails/"
ROOT = Path(__file__).resolve().parents[1]
MALMI_DIR = ROOT / "martti-malmi"
HEARN_DIR = ROOT / "mike-hearn"
USER_AGENT = "pubky-knowledge-base-independent-validator/1.0"
FOREIGN_PATTERNS = {
    "bitcoinj": re.compile(r"\bbitcoinj\b", re.I),
    "secp256k1": re.compile(r"\bsecp256k1\b", re.I),
    "rejoining-the-community": re.compile(r"\brejoining the community\b", re.I),
    "hearn-java-paragraph": re.compile(r"\bI have been working on a Java implementation\b", re.I),
}
ATTRIBUTION = re.compile(r"(?i)^(?:on .+,\s*)?(?:quoting\s+.+|.+\b(?:wrote|writes|said)):\s*$")
FORWARD = re.compile(r"(?i)^[- ]{2,}(?:begin forwarded message|original message|forwarded message)")


@dataclass
class Element:
    name: str
    attrs: dict[str, str]
    parent: "Element | None" = None
    content: list["Element | str"] = field(default_factory=list)


class IndependentHTML(HTMLParser):
    SINGLETON = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.document = Element("document", {})
        self.open = [self.document]

    def handle_starttag(self, tag, attrs):
        child = Element(tag.lower(), {key.lower(): value or "" for key, value in attrs}, self.open[-1])
        self.open[-1].content.append(child)
        if child.name not in self.SINGLETON:
            self.open.append(child)

    def handle_endtag(self, tag):
        for position in range(len(self.open) - 1, 0, -1):
            if self.open[position].name == tag.lower():
                self.open = self.open[:position]
                break

    def handle_data(self, data):
        self.open[-1].content.append(data)


def descendants(root: Element):
    yield root
    for item in root.content:
        if isinstance(item, Element):
            yield from descendants(item)


def classes(element: Element) -> set[str]:
    return set(element.attrs.get("class", "").split())


def clean(value: str) -> str:
    value = value.replace("\r\n", "\n").replace("\r", "\n").replace("\xa0", " ")
    value = "\n".join(line.rstrip() for line in value.splitlines())
    return re.sub(r"\n{3,}", "\n\n", value).strip()


def text(element: Element, omit=None) -> str:
    output: list[str] = []

    def collect(item):
        if isinstance(item, str):
            output.append(item)
        elif omit is not None and omit(item):
            return
        elif item.name == "br":
            output.append("\n")
        else:
            for nested in item.content:
                collect(nested)
            if item.name in {"div", "p", "blockquote", "tr"}:
                output.append("\n")

    collect(element)
    return clean("".join(output))


def download(url: str) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8", "replace")


def one(root: Element, test) -> Element:
    return next(element for element in descendants(root) if element is not root and test(element))


def split_quoted_plain(body: str) -> tuple[str, str]:
    lines = body.splitlines()
    foreign: set[int] = set()
    after_forward = False
    start = 0
    for end in range(len(lines) + 1):
        if end < len(lines) and lines[end].strip():
            continue
        block = list(range(start, end))
        values = [lines[index] for index in block]
        if any(FORWARD.match(value.strip()) for value in values):
            after_forward = True
        if (
            after_forward
            or any(value.lstrip().startswith(">") for value in values)
            or any(ATTRIBUTION.match(value.strip()) for value in values)
        ):
            foreign.update(block)
        start = end + 1
    authored = clean("\n".join(value for index, value in enumerate(lines) if index not in foreign))
    quoted = clean("\n".join(value for index, value in enumerate(lines) if index in foreign))
    return authored, quoted


def independently_redact_credentials(value: str) -> str:
    value = re.sub(
        r"-----BEGIN PGP (MESSAGE|PUBLIC KEY BLOCK)-----.*?-----END PGP \1-----",
        "[REDACTED: historical key or encrypted credential material]",
        value,
        flags=re.S,
    )
    substitutions = (
        (r'(?i)(password\s+")([^"]+)(")', r"\1[REDACTED]\3"),
        (r"(?im)^(\s*pw:\s*).+$", r"\1[REDACTED]"),
        (r"(?im)^(\s*u:\s*).+$", r"\1[REDACTED]"),
        (r"(?im)^(\s*b244765(?:ro|rw|admin)\s+)\S+\s*$", r"\1[REDACTED]"),
        (r"(?i)(admin account password is\s+)\S+", r"\1[REDACTED]"),
        (r"(?i)(with\s+admin/)\S+(\s+as login)", r"\1[REDACTED]\2"),
    )
    for pattern, replacement in substitutions:
        value = re.sub(pattern, replacement, value)
    return clean(value)


@dataclass
class Original:
    source_id: str
    sender: str
    authored: str
    raw: str
    date: str
    subject: str
    url: str

    def digest(self) -> str:
        payload = {
            "date": self.date,
            "raw_body": self.raw,
            "sender": self.sender,
            "source_id": self.source_id,
            "subject": self.subject,
            "url": self.url,
        }
        canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        return "sha256:" + hashlib.sha256(canonical).hexdigest()


def source_date(value: str) -> str:
    from email.utils import parsedate_to_datetime

    value = re.sub(r"^[A-Za-z]{3},\s*", "", value.strip()).replace(" at ", " ")
    try:
        return parsedate_to_datetime(value).isoformat()
    except (TypeError, ValueError):
        return value


def derive_malmi() -> tuple[list[Original], int]:
    parser = IndependentHTML()
    parser.feed(download(MALMI_URL))
    originals: list[Original] = []
    classified = 0
    for message in descendants(parser.document):
        tokens = classes(message)
        if message.name != "div" or not {"message", "satoshi"}.issubset(tokens):
            continue
        classified += 1
        header = one(message, lambda element: element.name == "div" and "header" in classes(element))
        fields: dict[str, str] = {}
        for row in header.content:
            if isinstance(row, Element) and row.name == "div":
                rendered = text(row)
                if ":" in rendered:
                    key, value = rendered.split(":", 1)
                    fields[key.strip().lower()] = value.strip()
        if "satoshi" not in fields.get("from", "").lower():
            raise ValueError(f"{message.attrs.get('id')}: satoshi class has non-Satoshi From header")
        body = one(message, lambda element: element.name == "div" and "body" in classes(element))
        pre = next((element for element in descendants(body) if element is not body and element.name == "pre"), body)
        raw = text(pre)
        authored, _ = split_quoted_plain(independently_redact_credentials(raw))
        if not authored:
            continue
        source_id = message.attrs["id"]
        originals.append(
            Original(
                source_id,
                fields["from"],
                authored,
                raw,
                source_date(fields.get("date", "")),
                fields.get("subject", ""),
                f"{MALMI_URL}#{source_id}",
            )
        )
    return originals, classified


def derive_hearn() -> tuple[list[Original], int]:
    originals: list[Original] = []
    classified = 0
    for thread in range(1, 6):
        parser = IndependentHTML()
        parser.feed(download(f"{HEARN_ROOT}thread{thread}.html"))
        title_element = next((element for element in descendants(parser.document) if element.name == "title"), None)
        subject = re.sub(r"^Gmail\s*-\s*", "", text(title_element)) if title_element else ""
        messages = [
            element
            for element in descendants(parser.document)
            if element.name == "table" and "message" in classes(element)
        ]
        for number, message in enumerate(messages, 1):
            classified += 1
            sender = text(one(message, lambda element: element.name == "b"))
            first_row = one(message, lambda element: element.name == "tr")
            date_match = re.search(
                r"(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun),\s+[A-Z][a-z]{2}\s+\d{1,2},\s+\d{4}\s+at\s+\d{1,2}:\d{2}\s+[AP]M",
                text(first_row),
            )
            if not date_match:
                raise ValueError(f"thread{thread}-message{number:02d}: missing date in message header")
            body = one(message, lambda element: element.name == "div" and "overflow" in element.attrs.get("style", ""))

            def quoted(element: Element) -> bool:
                return element.name == "blockquote" or bool(
                    classes(element) & {"gmail_quote", "gmail_extra", "yahoo_quoted"}
                )

            raw = text(body)
            authored = text(body, omit=quoted).replace("[Quoted text hidden]", "")
            authored = clean(
                "\n".join(line for line in authored.splitlines() if not ATTRIBUTION.match(line.strip()))
            )
            if sender.strip().lower() != "satoshi nakamoto":
                continue
            if not authored:
                raise ValueError(f"thread{thread}-message{number:02d}: empty Satoshi body")
            source_id = f"thread{thread}-message{number:02d}"
            originals.append(
                Original(
                    source_id,
                    sender,
                    authored,
                    raw,
                    source_date(date_match.group(0)),
                    subject,
                    f"{HEARN_ROOT}thread{thread}.html#message-{number}",
                )
            )
    return originals, classified


@dataclass
class Record:
    path: Path
    metadata: dict[str, str]
    main: str


def read_record(path: Path) -> Record:
    source = path.read_text(encoding="utf-8")
    match = re.fullmatch(r"---\n(.*?)\n---\n\n## Satoshi Nakamoto\n\n(.*)", source, re.S)
    if not match:
        raise ValueError(f"{path}: malformed frontmatter or missing main heading")
    metadata: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, separator, raw_value = line.partition(":")
        if not separator:
            raise ValueError(f"{path}: malformed metadata line")
        try:
            metadata[key] = json.loads(raw_value.strip())
        except json.JSONDecodeError:
            metadata[key] = raw_value.strip()
    body = match.group(2)
    main = body.split("\n## Context (", 1)[0].rstrip()
    return Record(path, metadata, main)


def load_records(directory: Path) -> list[Record]:
    return [read_record(path) for path in sorted(directory.glob("[0-9][0-9][0-9][0-9].md"))]


def validate_set(
    label: str, originals: list[Original], records: list[Record], notices: list[str]
) -> list[str]:
    errors: list[str] = []
    original_map = {item.source_id: item for item in originals}
    seen: dict[str, Path] = {}
    for record in records:
        source_id = record.metadata.get("source_id", "")
        if source_id in seen:
            errors.append(f"DUPLICATE_SOURCE {label} {source_id} {seen[source_id]} {record.path}")
            continue
        seen[source_id] = record.path
        original = original_map.get(source_id)
        if original is None:
            errors.append(f"EXTRA_RECORD {label} {record.path} source_id={source_id}")
            continue
        if record.metadata.get("author") != "Satoshi Nakamoto":
            errors.append(f"SENDER_MISMATCH {label} {record.path} author={record.metadata.get('author')!r}")
        if record.metadata.get("original_url") != original.url:
            errors.append(f"PROVENANCE_MISMATCH {label} {record.path}")
        if record.metadata.get("checksum") != original.digest():
            errors.append(f"CHECKSUM_MISMATCH {label} {record.path}")
        main = clean(record.main)
        if not main:
            errors.append(f"EMPTY_BODY {label} {record.path}")
        if re.fullmatch(r"(?:From|To|Date|Subject):.*", main, re.I | re.S):
            errors.append(f"HEADER_ONLY_BODY {label} {record.path}")
        for line in main.splitlines():
            if line.lstrip().startswith(">"):
                errors.append(f"QUOTE_IN_MAIN {label} {record.path}")
                break
            if ATTRIBUTION.match(line.strip()):
                errors.append(f"ATTRIBUTION_IN_MAIN {label} {record.path}: {line.strip()}")
                break
        if main != clean(original.authored):
            errors.append(f"CONTENT_MISMATCH {label} {record.path} source_id={source_id}")
        if label == "hearn":
            for phrase, pattern in FOREIGN_PATTERNS.items():
                if pattern.search(main):
                    notices.append(
                        f"FOREIGN_TEXT_MANUAL_INSPECTION {label} {record.path} phrase={phrase}"
                    )
    for source_id in sorted(set(original_map) - set(seen)):
        errors.append(f"MISSING_RECORD {label} source_id={source_id}")
    return errors


def main() -> int:
    options = argparse.ArgumentParser()
    options.add_argument("--mutation-test", action="store_true")
    args = options.parse_args()
    malmi_originals, malmi_classified = derive_malmi()
    hearn_originals, hearn_classified = derive_hearn()
    malmi_records = load_records(MALMI_DIR)
    hearn_records = load_records(HEARN_DIR)
    if args.mutation_test:
        if not hearn_records:
            print("MUTATION_SETUP_FAILED no Hearn record", file=sys.stderr)
            return 2
        target = hearn_records[0]
        target.main += (
            "\n\nI have been working on a Java implementation of the simplified payment "
            "verification, with an eye to building a client that runs on Android phones."
        )
        print(f"MUTATION injected Mike Hearn paragraph into {target.path}")
    notices: list[str] = []
    errors = validate_set("malmi", malmi_originals, malmi_records, notices)
    errors.extend(validate_set("hearn", hearn_originals, hearn_records, notices))
    for notice in notices:
        print(notice)
    if errors:
        for error in errors:
            print(error)
        print(
            f"FAIL errors={len(errors)} malmi={len(malmi_records)}/{len(malmi_originals)} "
            f"hearn={len(hearn_records)}/{len(hearn_originals)} "
            f"classified_source_messages=malmi:{malmi_classified},hearn:{hearn_classified} "
            f"manual_flags={len(notices)}"
        )
        return 1
    print(
        f"PASS errors=0 malmi={len(malmi_records)}/{len(malmi_originals)} "
        f"hearn={len(hearn_records)}/{len(hearn_originals)} "
        f"classified_source_messages=malmi:{malmi_classified},hearn:{hearn_classified} "
        f"manual_flags={len(notices)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
