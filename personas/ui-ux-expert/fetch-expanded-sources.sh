#!/usr/bin/env bash
# Fetches exact, allowlisted UI/UX source bytes. Run with --verify to check them.
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
out="$root/sources/expanded"
manifest="$root/expanded-checksums.sha256"

if [[ "${1:-}" == "--verify" ]]; then
  (cd "$root" && shasum -a 256 -c "$(basename "$manifest")")
  exit 0
fi

mkdir -p "$out"
while IFS=$'\t' read -r id url; do
  [[ -n "$id" ]] || continue
  tmp="$(mktemp "$out/$id.tmp.XXXXXX")"
  curl --fail --location --proto '=https' --tlsv1.2 --retry 3 --retry-delay 1 \
    --connect-timeout 20 --user-agent 'JebPersonaCorpus/1.0' "$url" --output "$tmp"
  mv "$tmp" "$out/$id.html"
done <<'SOURCES'
wai-tutorials	https://www.w3.org/WAI/tutorials/
wai-tutorial-images	https://www.w3.org/WAI/tutorials/images/
wai-tutorial-tables	https://www.w3.org/WAI/tutorials/tables/
wai-tutorial-menus	https://www.w3.org/WAI/tutorials/menus/
wai-tutorial-forms	https://www.w3.org/WAI/tutorials/forms/
wai-tutorial-carousels	https://www.w3.org/WAI/tutorials/carousels/
wai-tutorial-page-structure	https://www.w3.org/WAI/tutorials/page-structure/
aria-authoring-practices	https://www.w3.org/WAI/ARIA/apg/
understanding-wcag-2.2	https://www.w3.org/WAI/WCAG22/Understanding/
govuk-design-system	https://design-system.service.gov.uk/
govuk-components	https://design-system.service.gov.uk/components/
govuk-patterns	https://design-system.service.gov.uk/patterns/
govuk-styles	https://design-system.service.gov.uk/styles/
uswds-documentation	https://designsystem.digital.gov/how-to-use-uswds/
uswds-components	https://designsystem.digital.gov/components/overview/
uswds-design-principles	https://designsystem.digital.gov/design-principles/
SOURCES

(
  cd "$root"
  shasum -a 256 sources/expanded/*.html > "$(basename "$manifest")"
)
