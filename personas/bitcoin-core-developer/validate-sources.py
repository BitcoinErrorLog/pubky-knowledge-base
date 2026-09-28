#!/usr/bin/env python3
import hashlib, pathlib, sys, tarfile
root = pathlib.Path(__file__).resolve().parent
for line in (root / "checksums.sha256").read_text().splitlines():
    digest, path = line.split(maxsplit=1)
    assert hashlib.sha256((root / path).read_bytes()).hexdigest() == digest
with tarfile.open(root / "sources" / "bips-3a10b5b5.tar.gz") as archive:
    bips = [m for m in archive.getmembers() if "/bip-" in m.name and m.name.endswith(".mediawiki")]
    assert bips, "no BIP sources"
    assert all(b"License:" in archive.extractfile(m).read() for m in bips), "BIP lacks License field"
print("validated")
