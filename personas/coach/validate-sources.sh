#!/usr/bin/env bash
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
(cd "$root" && shasum -a 256 -c checksums.sha256)
expected=6
test "$(find "$root/sources" -type f -name '*.txt' | wc -l | tr -d ' ')" = "$expected"
for source in "$root"/sources/*.txt; do
  test -s "$source"
  tmp="$(mktemp)"
  cp "$source" "$tmp"
  printf x >> "$tmp"
  ! printf '%s  %s\n' "$(shasum -a 256 "$source" | cut -d' ' -f1)" "$tmp" | shasum -a 256 -c -
  rm -f "$tmp"
done
