# UI/UX Expert source register

This register governs reuse of the source payloads in this directory. The
retrieved HTML files are the corpus text; the adjacent Markdown records provide
the required provenance frontmatter. Run `./fetch-sources.sh --verify` to
check the committed payloads against `checksums.sha256`. Running the script
without an argument retrieves the current canonical bytes and regenerates that
checksum file; a changed upstream document requires a rights and provenance
review before its new bytes are committed.

| ID | Stored payload | Work and edition | Rights and use | Canonical URL | Retrieved | SHA-256 |
| --- | --- | --- | --- | --- | --- | --- |
| `govuk-design-principles` | `sources/govuk-design-principles.html` | *Government Design Principles*, published 2012-04-03, modified 2025-04-02 in the retrieved GOV.UK metadata | Open Government Licence v3.0; verbatim copy. Attribute © Crown copyright, Government Digital Service; do not imply endorsement. | <https://www.gov.uk/guidance/government-design-principles> | 2026-09-28 | `be26f4e018aff861a6e69844ca3f1ce7c557b80e728d5f346101a7e6e1d9a900` |
| `govuk-user-research` | `sources/govuk-user-research.html` | *How user research improves service design*, published 2016-04-08, modified 2017-03-23 in the retrieved GOV.UK metadata | Open Government Licence v3.0; verbatim copy. Attribute © Crown copyright, Government Digital Service; do not imply endorsement. | <https://www.gov.uk/service-manual/user-research/how-user-research-improves-service-design> | 2026-09-28 | `33b2b8341b6d1386164b81d0d2f296c751876513e69265cbbd9795ca0e39ba6f` |
| `wcag-2.2` | `sources/wcag-2.2.html` | *Web Content Accessibility Guidelines (WCAG) 2.2*, W3C Recommendation, 2023-10-05 | W3C Document License; complete unmodified reference copy only. The source URL, status, and rights notice remain in the stored document. No adapted WCAG text is created here. | <https://www.w3.org/TR/WCAG22/> | 2026-09-28 | `6e3c5fe397257cae509a2fb4752b73062cf8cbeb92c2cec618989b17e4cf7057` |

## Reference-only material

The following sources informed corpus selection but are not copied into this
directory:

| Source | Reason |
| --- | --- |
| WAI guidance other than a page explicitly carrying CC BY 4.0 | WAI pages commonly use the W3C Document License. They require an individual immutable-copy assessment before addition. |
| Digital.gov usability topic pages | The topic collection has no verified blanket clearance for contractor or third-party material. |
| US Web Design System | Most project material is CC0, but dependencies, fonts, icons, and assets have file-level notices. No subset has been inventoried for this corpus. |
| Named-designer heuristics and proprietary design courses | Not cleared for redistribution or ingestion. |
