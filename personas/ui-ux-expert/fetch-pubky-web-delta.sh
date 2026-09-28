#!/usr/bin/env bash
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
out="$root/sources/pubky-web"
sha="ddf07d1c5d50a5498ba128960365ae82ccdef271"
mkdir -p "$out"
while IFS=$'\t' read -r id url; do
  curl --fail --location --proto '=https' --tlsv1.2 "$url" -o "$out/$id"
done <<SOURCES
components.md	https://raw.githubusercontent.com/BitcoinErrorLog/pubky-app/$sha/docs/components.md
component-testing.md	https://raw.githubusercontent.com/BitcoinErrorLog/pubky-app/$sha/docs/component-testing.md
address-autocomplete-design.md	https://raw.githubusercontent.com/BitcoinErrorLog/pubky-app/$sha/docs/ecommerce/address-autocomplete-design.md
checkout-address-design.md	https://raw.githubusercontent.com/BitcoinErrorLog/pubky-app/$sha/docs/ecommerce/checkout-address-design.md
local-pickup-design.md	https://raw.githubusercontent.com/BitcoinErrorLog/pubky-app/$sha/docs/ecommerce/local-pickup-design.md
SOURCES
(cd "$root" && shasum -a 256 sources/pubky-web/* > pubky-web-checksums.sha256)
