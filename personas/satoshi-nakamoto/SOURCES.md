# Satoshi Nakamoto source register

This directory is a rights-separated source register for a historical AI portrayal. The repository's root MIT licence applies only to repository tooling and original metadata/documentation. It does not license source works referenced or stored here.

Each item is preserved verbatim from its stated primary, archival, or recipient-controlled source. Its file-level `rights_status`, source URL, archive URL, retrieval date, and SHA-256 checksum identify the work actually fetched. Material excluded for disputed authorship, compromise, forgery, privacy, or missing provenance is never stored as a corpus item.

## Collection policy

| Collection | Coverage baseline | Storage mode | Rights status | Canonical source |
| --- | ---: | --- | --- | --- |
| Bitcoin whitepaper | 1 work | Verbatim | Publicly distributed source text; file records PDF hash | https://bitcoin.org/bitcoin.pdf |
| BitcoinTalk | 539 SNI records | Verbatim | SNI archival text; original work rights remain item-specific | https://satoshi.nakamotoinstitute.org/posts/bitcointalk/ |
| P2P Foundation forum | 3 authenticated February 2009 posts | Verbatim | SNI archival text; original work rights remain item-specific | https://satoshi.nakamotoinstitute.org/posts/p2pfoundation/ |
| Cryptography mailing list | 18 index entries | Verbatim | SNI archival text; original work rights remain item-specific | https://satoshi.nakamotoinstitute.org/emails/cryptography/ |
| bitcoin-list / SourceForge | 16 index entries | Verbatim | SNI archival text; original work rights remain item-specific | https://satoshi.nakamotoinstitute.org/emails/bitcoin-list/ |
| P2P Research list | 5 index entries | Verbatim | SNI archival text; original work rights remain item-specific | https://satoshi.nakamotoinstitute.org/emails/p2p-research/ |
| Martti Malmi correspondence | 141 substantive Satoshi-authored records from 144 explicit `message satoshi` elements; 3 forward-only elements with no newly authored Satoshi body omitted | Satoshi text in main; non-Satoshi and quoted material labelled context | Recipient-published correspondence; original-work rights remain with authors | https://mmalmi.github.io/satoshi/ |
| Mike Hearn correspondence | 16 Satoshi-authored records from 33 explicitly sender-classified source messages | Satoshi text in main; non-Satoshi and quoted material labelled context | Recipient-published correspondence; original-work rights remain with authors | https://plan99.net/~mike/satoshi-emails/ |
| Bitcoin source and release artefacts, 0.1–0.3.x | 3 hash-qualified snapshots | Verbatim | MIT/X11 only, preserving notices | https://github.com/bitcoin/bitcoin |
| COPA v Wright judgment | 2 provenance passages | Verbatim judgment extract | Quoted in judgment; not represented as a full email | https://www.judiciary.uk/judgments/copa-v-wright/ |

## Hard exclusions

- Craig Wright-origin material, alleged Satoshi documents, and litigation-only copies.
- Post-2011 account activity, including the disputed 2014 P2P Foundation post and known account compromise activity.
- Leaked or hacked correspondence, credentials, addresses, keys, wallet claims, unpublished attachments, and court-exhibit scans without a recipient-controlled original publication.
- Modern quote compilations, translations without separate clearance, commentary, and third-party text quoted within a Satoshi message.

## Explicitly unavailable

- Hal Finney and Gavin Andresen correspondence: no recipient-controlled publication or court-record extract containing the email text was located in this bounded source sweep.
- Adam Back correspondence: SNI’s full email index contains only Cryptography, bitcoin-list, and P2P Research collections, not an Adam Back collection. The High Court judgment records Back’s August 2008 and January 2009 exchanges but does not reproduce the full email text. Two judgment passages are retained only as judicial provenance records.

## Required fields and verification

Each item records the original URL, archive URL when different, timestamp if recoverable, collection, rights status, retrieval date, and SHA-256 of the fetched item or canonical metadata representation. Source IDs remain stable across re-fetches. Collection coverage must distinguish visible/retrievable records from inaccessible or deleted material.

## Merge record

The attribution-validated Satoshi corpus was fast-forwarded to `main` at `f70df76e7966f9636f343308097ebc619bf45e6a` on 2026-09-28. The post-separation validator checked 599 items with zero failures.

Commit `53768f2` received SHIP attribution review in commit comment `202408877`. The accepted correspondence coverage is 141 Malmi records and 16 Hearn records, with three forward-only Malmi messages omitted because they contain no newly authored Satoshi body.
