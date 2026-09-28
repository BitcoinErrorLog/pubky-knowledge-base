#!/usr/bin/env python3
import hashlib, tarfile
from pathlib import Path

root = Path(__file__).resolve().parent
archive = root / "sources" / "optech-dde4704a.tar.gz"
out = root / "optech-newsletters"
out.mkdir(exist_ok=True)
rows = []
with tarfile.open(archive) as tar:
    for member in tar.getmembers():
        if "/_posts/" not in member.name or "newsletter" not in member.name or not member.name.endswith(".md"):
            continue
        body = tar.extractfile(member).read()
        name = member.name.rsplit("/", 1)[-1]
        (out / name).write_bytes(body)
        rows.append((name, hashlib.sha256(body).hexdigest()))
(root / "optech-newsletters.sha256").write_text("".join(f"{d}  optech-newsletters/{n}\n" for n, d in sorted(rows)))
print(len(rows))
