#!/usr/bin/env bash
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
(cd "$root" && shasum -a 256 -c checksums.sha256)
tmp="$(mktemp)"
cp "$root/sources/epictetus-enchiridion-long.txt" "$tmp"
printf x >> "$tmp"
! printf '%s  %s\n' "$(shasum -a 256 "$root/sources/epictetus-enchiridion-long.txt" | cut -d' ' -f1)" "$tmp" | shasum -a 256 -c -
rm -f "$tmp"
