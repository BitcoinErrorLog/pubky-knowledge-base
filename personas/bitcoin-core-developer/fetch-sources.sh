#!/usr/bin/env bash
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
out="$root/sources"
mkdir -p "$out"
fetch() { curl --fail --location --proto '=https' --tlsv1.2 --retry 3 "$1" -o "$2"; }
# Pinned Core v31.1: includes COPYING, doc/, and doc/release-notes/.
fetch "https://codeload.github.com/bitcoin/bitcoin/tar.gz/9be056a8a72b624dae9623b2f7bded92c2a21c91" "$out/bitcoin-core-v31.1.tar.gz"
# Pinned BIPs and Optech site trees; validator rejects BIPs without SPDX metadata.
fetch "https://codeload.github.com/bitcoin/bips/tar.gz/3a10b5b5f0a7586df8928d580a3009744ebb2079" "$out/bips-3a10b5b5.tar.gz"
fetch "https://codeload.github.com/bitcoinops/bitcoinops.github.io/tar.gz/dde4704ac894fc59829b283e5e9c8c4b8e50dcec" "$out/optech-dde4704a.tar.gz"
(cd "$root" && shasum -a 256 sources/*.tar.gz > checksums.sha256)
