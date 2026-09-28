#!/usr/bin/env python3
"""Build the Malmi and Hearn Satoshi correspondence collections."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import date
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

MALMI_URL = "https://mmalmi.github.io/satoshi/"
HEARN_ROOT = "https://plan99.net/~mike/satoshi-emails/"
HERE = Path(__file__).resolve().parent
HEARN_DIR = HERE.parent / "mike-hearn"
RETRIEVAL_DATE = date.today().isoformat()
USER_AGENT = "pubky-knowledge-base-corpus-builder/1.0"


@dataclass
class Node:
    tag: str
    attrs: dict[str, str]
    parent: "Node | None" = None
    children: list["Node | str"] = field(default_factory=list)


class TreeParser(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("document", {})
        self.stack = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = Node(tag.lower(), {k.lower(): v or "" for k, v in attrs}, self.stack[-1])
        self.stack[-1].children.append(node)
        if tag.lower() not in self.VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag.lower() not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                return

    def handle_data(self, data: str) -> None:
        self.stack[-1].children.append(data)


def fetch(url: str) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8", "replace")


def walk(node: Node):
    yield node
    for child in node.children:
        if isinstance(child, Node):
            yield from walk(child)


def class_tokens(node: Node) -> set[str]:
    return set(node.attrs.get("class", "").split())


def first_descendant(node: Node, predicate) -> Node:
    return next(item for item in walk(node) if item is not node and predicate(item))


def render_text(node: Node, skip=None) -> str:
    chunks: list[str] = []

    def visit(item: Node | str) -> None:
        if isinstance(item, str):
            chunks.append(item)
            return
        if skip is not None and skip(item):
            return
        if item.tag == "br":
            chunks.append("\n")
            return
        for child in item.children:
            visit(child)
        if item.tag in {"div", "p", "blockquote", "tr"}:
            chunks.append("\n")

    visit(node)
    return normalize_text("".join(chunks))


def normalize_text(value: str) -> str:
    value = value.replace("\r\n", "\n").replace("\r", "\n").replace("\xa0", " ")
    value = "\n".join(line.rstrip() for line in value.splitlines())
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def iso_date(value: str) -> str:
    cleaned = re.sub(r"^[A-Za-z]{3},\s*", "", value.strip())
    try:
        return parsedate_to_datetime(cleaned).isoformat()
    except (TypeError, ValueError):
        return value.strip()


@dataclass
class Message:
    source_id: str
    sender: str
    date: str
    subject: str
    raw_body: str
    authored: str
    quoted: str
    url: str

    def checksum(self) -> str:
        canonical = json.dumps(
            {
                "date": self.date,
                "raw_body": self.raw_body,
                "sender": self.sender,
                "source_id": self.source_id,
                "subject": self.subject,
                "url": self.url,
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        return "sha256:" + hashlib.sha256(canonical).hexdigest()


ATTRIBUTION = re.compile(
    r"(?i)^(?:on .+,\s*)?(?:quoting\s+.+|.+\b(?:wrote|writes|said)):\s*$"
)
ORIGINAL_MARKER = re.compile(r"(?i)^[- ]{2,}(?:begin forwarded message|original message|forwarded message)")


def redact_historical_credentials(value: str) -> str:
    value = re.sub(
        r"-----BEGIN PGP (MESSAGE|PUBLIC KEY BLOCK)-----.*?-----END PGP \1-----",
        "[REDACTED: historical key or encrypted credential material]",
        value,
        flags=re.S,
    )
    value = re.sub(r'(?i)(password\s+")([^"]+)(")', r"\1[REDACTED]\3", value)
    value = re.sub(r"(?im)^(\s*pw:\s*).+$", r"\1[REDACTED]", value)
    value = re.sub(r"(?im)^(\s*u:\s*).+$", r"\1[REDACTED]", value)
    value = re.sub(
        r"(?im)^(\s*b244765(?:ro|rw|admin)\s+)\S+\s*$",
        r"\1[REDACTED]",
        value,
    )
    value = re.sub(
        r"(?i)(admin account password is\s+)\S+",
        r"\1[REDACTED]",
        value,
    )
    value = re.sub(r"(?i)(with\s+admin/)\S+(\s+as login)", r"\1[REDACTED]\2", value)
    return normalize_text(value)


def escape_git_marker_lines(value: str) -> str:
    return "\n".join(
        f" {line}" if re.match(r"^(?:<{7}|={7}|>{7})", line) else line
        for line in value.splitlines()
    )


def split_plain_reply(body: str) -> tuple[str, str]:
    lines = body.splitlines()
    context_indices: set[int] = set()
    forwarded = False
    paragraph_start = 0
    for index in range(len(lines) + 1):
        if index < len(lines) and lines[index].strip():
            continue
        paragraph = range(paragraph_start, index)
        paragraph_lines = [lines[candidate] for candidate in paragraph]
        if any(ORIGINAL_MARKER.match(line.strip()) for line in paragraph_lines):
            forwarded = True
        is_quote = (
            forwarded
            or any(line.lstrip().startswith(">") for line in paragraph_lines)
            or any(ATTRIBUTION.match(line.strip()) for line in paragraph_lines)
        )
        if is_quote:
            context_indices.update(paragraph)
        paragraph_start = index + 1
    main = normalize_text("\n".join(line for i, line in enumerate(lines) if i not in context_indices))
    context = normalize_text("\n".join(line for i, line in enumerate(lines) if i in context_indices))
    return main, context


def parse_malmi(html: str) -> list[Message]:
    parser = TreeParser()
    parser.feed(html)
    messages: list[Message] = []
    for element in walk(parser.root):
        tokens = class_tokens(element)
        if element.tag != "div" or "message" not in tokens:
            continue
        if not ({"satoshi", "sirius"} & tokens):
            continue
        source_id = element.attrs.get("id", "")
        header = first_descendant(element, lambda node: node.tag == "div" and "header" in class_tokens(node))
        fields: dict[str, str] = {}
        for row in header.children:
            if not isinstance(row, Node) or row.tag != "div":
                continue
            text = render_text(row)
            if ":" in text:
                key, value = text.split(":", 1)
                fields[key.strip().lower()] = value.strip()
        body_node = first_descendant(element, lambda node: node.tag == "div" and "body" in class_tokens(node))
        pre = next((node for node in walk(body_node) if node is not body_node and node.tag == "pre"), None)
        raw = render_text(pre or body_node)
        sender = fields.get("from", "")
        authored, quoted = split_plain_reply(redact_historical_credentials(raw))
        messages.append(
            Message(
                source_id=source_id,
                sender=sender,
                date=iso_date(fields.get("date", "")),
                subject=fields.get("subject", ""),
                raw_body=raw,
                authored=authored,
                quoted=quoted,
                url=f"{MALMI_URL}#{source_id}",
            )
        )
    return messages


def direct_child_nodes(node: Node, tag: str) -> list[Node]:
    return [child for child in node.children if isinstance(child, Node) and child.tag == tag]


def parse_hearn_thread(html: str, thread: int) -> list[Message]:
    parser = TreeParser()
    parser.feed(html)
    tables = [
        node
        for node in walk(parser.root)
        if node.tag == "table" and "message" in class_tokens(node)
    ]
    messages: list[Message] = []
    page_title = ""
    title_node = next((node for node in walk(parser.root) if node.tag == "title"), None)
    if title_node:
        page_title = re.sub(r"^Gmail\s*-\s*", "", render_text(title_node))
    for number, table in enumerate(tables, 1):
        sender_node = first_descendant(table, lambda node: node.tag == "b")
        sender = render_text(sender_node)
        rows = [node for node in walk(table) if node.tag == "tr"]
        header_text = render_text(rows[0]) if rows else ""
        date_match = re.search(
            r"(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun),\s+[A-Z][a-z]{2}\s+\d{1,2},\s+\d{4}\s+at\s+\d{1,2}:\d{2}\s+[AP]M",
            header_text,
        )
        if not date_match:
            raise ValueError(f"thread {thread} message {number}: missing explicit date header")
        body_node = first_descendant(
            table,
            lambda node: node.tag == "div" and "overflow" in node.attrs.get("style", ""),
        )

        def quote_node(node: Node) -> bool:
            return node.tag == "blockquote" or bool(
                class_tokens(node) & {"gmail_quote", "gmail_extra", "yahoo_quoted"}
            )

        raw = render_text(body_node)
        authored = render_text(body_node, skip=quote_node).replace("[Quoted text hidden]", "")
        authored = normalize_text(
            "\n".join(line for line in authored.splitlines() if not ATTRIBUTION.match(line.strip()))
        )
        quoted_parts = [render_text(node) for node in walk(body_node) if node is not body_node and quote_node(node)]
        quoted = normalize_text("\n\n".join(part for part in quoted_parts if part))
        messages.append(
            Message(
                source_id=f"thread{thread}-message{number:02d}",
                sender=sender,
                date=iso_date(date_match.group(0).replace(" at ", " ")),
                subject=page_title,
                raw_body=raw,
                authored=authored,
                quoted=quoted,
                url=f"{HEARN_ROOT}thread{thread}.html#message-{number}",
            )
        )
    return messages


def yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def contextualize(messages: list[Message], satoshi_test) -> dict[str, list[str]]:
    contexts: dict[str, list[str]] = {message.source_id: [] for message in messages if satoshi_test(message)}
    pending: list[str] = []
    last_satoshi: Message | None = None
    for message in messages:
        if satoshi_test(message):
            contexts[message.source_id].extend(pending)
            pending.clear()
            last_satoshi = message
            if message.quoted:
                contexts[message.source_id].append(
                    f"Quoted/replied-to text within {message.source_id}:\n\n"
                    f"{escape_git_marker_lines(message.quoted)}"
                )
        else:
            pending.append(
                f"Source message {message.source_id}, From: {message.sender}:\n\n"
                f"{escape_git_marker_lines(redact_historical_credentials(message.raw_body))}"
            )
    if pending:
        if last_satoshi is None:
            raise ValueError("source has non-Satoshi messages but no Satoshi message")
        contexts[last_satoshi.source_id].extend(pending)
    return contexts


def write_collection(
    directory: Path,
    messages: list[Message],
    satoshi_test,
    collection: str,
    correspondent: str,
    rights: str,
) -> int:
    directory.mkdir(parents=True, exist_ok=True)
    for old in directory.glob("[0-9][0-9][0-9][0-9].md"):
        old.unlink()
    contexts = contextualize(messages, satoshi_test)
    selected = [message for message in messages if satoshi_test(message)]
    for index, message in enumerate(selected, 1):
        if not message.authored.strip():
            raise ValueError(f"{message.source_id}: empty Satoshi-authored body")
        body = [
            "---",
            f"title: {yaml_string(message.subject)}",
            "author: Satoshi Nakamoto",
            f"date: {yaml_string(message.date)}",
            f"original_url: {yaml_string(message.url)}",
            f"archive_url: {yaml_string(message.url)}",
            f"source_collection: {yaml_string(collection)}",
            f"rights_status: {yaml_string(rights)}",
            f"retrieval_date: {yaml_string(RETRIEVAL_DATE)}",
            f"checksum: {yaml_string(message.checksum())}",
            f"source_id: {yaml_string(message.source_id)}",
            "---",
            "",
            "## Satoshi Nakamoto",
            "",
            message.authored,
        ]
        context = contexts[message.source_id]
        if context:
            body.extend(["", f"## Context ({correspondent})", "", "\n\n---\n\n".join(context)])
        (directory / f"{index:04d}.md").write_text("\n".join(body).rstrip() + "\n", encoding="utf-8")
    return len(selected)


def main() -> None:
    malmi_messages = parse_malmi(fetch(MALMI_URL))
    hearn_messages: list[Message] = []
    for thread in range(1, 6):
        hearn_messages.extend(parse_hearn_thread(fetch(f"{HEARN_ROOT}thread{thread}.html"), thread))

    malmi_count = write_collection(
        HERE,
        malmi_messages,
        lambda message: "satoshi" in message.sender.lower() and bool(message.authored.strip()),
        "martti-malmi-correspondence",
        "Martti Malmi",
        "Recipient-published correspondence; original-work rights remain with authors",
    )
    hearn_count = write_collection(
        HEARN_DIR,
        hearn_messages,
        lambda message: message.sender.strip().lower() == "satoshi nakamoto" and bool(message.authored.strip()),
        "mike-hearn-correspondence",
        "Mike Hearn",
        "Recipient-published correspondence; original-work rights remain with authors",
    )
    print(
        f"generated malmi={malmi_count} hearn={hearn_count} "
        f"source_messages_malmi={len(malmi_messages)} source_messages_hearn={len(hearn_messages)}"
    )


if __name__ == "__main__":
    main()
