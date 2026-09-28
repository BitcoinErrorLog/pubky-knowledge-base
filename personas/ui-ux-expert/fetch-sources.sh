#!/usr/bin/env bash
# Fetches exact canonical source bytes used by this corpus.
set -euo pipefail

root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
sources="$root/sources"
checksums="$root/checksums.sha256"

declare -a ids=(
  govuk-design-principles
  govuk-user-research
  wcag-2.2
)
declare -a urls=(
  "https://www.gov.uk/guidance/government-design-principles"
  "https://www.gov.uk/service-manual/user-research/how-user-research-improves-service-design"
  "https://www.w3.org/TR/WCAG22/"
)

if [[ "${1:-}" == "--verify" ]]; then
  (cd "$root" && shasum -a 256 -c "$(basename "$checksums")")
  exit 0
fi

mkdir -p "$sources"
for i in "${!ids[@]}"; do
  target="$sources/${ids[$i]}.html"
  temporary="$(mktemp "${target}.tmp.XXXXXX")"
  trap 'rm -f "$temporary"' EXIT
  curl --fail --location --proto '=https' --tlsv1.2 \
    --retry 3 --retry-delay 1 --connect-timeout 20 \
    --user-agent 'JebPersonaCorpus/1.0 (+https://github.com/BitcoinErrorLog/pubky-knowledge-base)' \
    "${urls[$i]}" --output "$temporary"
  mv "$temporary" "$target"
  trap - EXIT
done

(
  cd "$root"
  shasum -a 256 "sources/"*.html > "$(basename "$checksums")"
)
