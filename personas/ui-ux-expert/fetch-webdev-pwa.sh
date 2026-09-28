#!/usr/bin/env bash
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
out="$root/sources/webdev-pwa"
mkdir -p "$out"
while IFS=$'\t' read -r id url; do
  curl --fail --location --proto '=https' --tlsv1.2 "$url" -o "$out/$id.html"
done <<'SOURCES'
pwa-overview	https://web.dev/learn/pwa/
pwa-welcome	https://web.dev/learn/pwa/welcome/
pwa-installation	https://web.dev/learn/pwa/installation/
pwa-service-workers	https://web.dev/learn/pwa/service-workers/
SOURCES
(cd "$root" && shasum -a 256 sources/webdev-pwa/*.html > webdev-pwa-checksums.sha256)
