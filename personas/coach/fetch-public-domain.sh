#!/usr/bin/env bash
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
out="$root/sources"
mkdir -p "$out"
while IFS=$'\t' read -r id url; do
  curl --fail --location --proto '=https' --tlsv1.2 "$url" -o "$out/$id.txt"
done <<'SOURCES'
epictetus-enchiridion-long	https://www.gutenberg.org/files/45109/45109-0.txt
marcus-aurelius-long	https://www.gutenberg.org/files/2680/2680-0.txt
franklin-autobiography	https://www.gutenberg.org/files/148/148-0.txt
william-james-habit	https://www.gutenberg.org/files/57628/57628-0.txt
arnold-bennett-24-hours	https://www.gutenberg.org/files/2274/2274.txt
samuel-smiles-self-help	https://www.gutenberg.org/files/935/935-0.txt
SOURCES
(cd "$root" && shasum -a 256 sources/*.txt > checksums.sha256)
