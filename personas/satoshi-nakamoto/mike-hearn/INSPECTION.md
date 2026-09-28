# Correspondence corpus inspection

Inspection date: 2026-09-28

Authoritative sources:

- https://plan99.net/~mike/satoshi-emails/
- https://mmalmi.github.io/satoshi/

## End-to-end record inspection

Each main section below was checked from its explicit source message boundary and sender header through the end of the source body. Quoted/replied-to text and adjacent non-Satoshi messages were checked against the labelled context section.

| Record | Source ID | Verdict |
| --- | --- | --- |
| `mike-hearn/0001.md` | `thread1-message02` | PASS — explicit Satoshi sender; authored body only in main |
| `mike-hearn/0002.md` | `thread1-message05` | PASS — Mike attribution and quoted questions excluded from main |
| `mike-hearn/0003.md` | `thread1-message06` | PASS — explicit Satoshi sender; complete authored body |
| `mike-hearn/0004.md` | `thread1-message08` | PASS — explicit Satoshi sender; preceding Mike message in context |
| `mike-hearn/0005.md` | `thread1-message10` | PASS — explicit Satoshi sender; Mike transaction details in context |
| `mike-hearn/0006.md` | `thread1-message12` | PASS — explicit Satoshi sender; quoted Mike body excluded |
| `mike-hearn/0007.md` | `thread1-message14` | PASS — explicit Satoshi sender; complete authored body |
| `mike-hearn/0008.md` | `thread2-message02` | PASS — explicit Satoshi sender; complete authored body |
| `mike-hearn/0009.md` | `thread3-message02` | PASS — explicit Satoshi sender; Satoshi's attached patch remains in main; Mike's Java paragraph is context only |
| `mike-hearn/0010.md` | `thread3-message04` | PASS — explicit Satoshi sender; client-progress prose is context only |
| `mike-hearn/0011.md` | `thread3-message06` | PASS — explicit Satoshi sender; testnet-spend prose is context only |
| `mike-hearn/0012.md` | `thread3-message08` | PASS — explicit Satoshi sender; `secp256k1` question is context only |
| `mike-hearn/0013.md` | `thread4-message02` | PASS — explicit Satoshi sender; BitCoinJ release prose is context only |
| `mike-hearn/0014.md` | `thread4-message04` | PASS — explicit Satoshi sender; complete authored body |
| `mike-hearn/0015.md` | `thread5-message02` | PASS — explicit Satoshi sender; complete authored contract explanation |
| `mike-hearn/0016.md` | `thread5-message04` | PASS — explicit Satoshi sender; `BitcoinJ` is genuinely in Satoshi's reply; `rejoining the community` is context only |
| `martti-malmi/0001.md` | `email-1` | PASS — beginning sample; Martti quote excluded from main |
| `martti-malmi/0047.md` | `email-80` | PASS — early-middle sample; explicit Satoshi class and From header; historical credential redacted |
| `martti-malmi/0094.md` | `email-168` | PASS — late-middle sample; Martti quote excluded from main |
| `martti-malmi/0141.md` | `email-260` | PASS — end sample; quoted request in context; encrypted historical credentials redacted |

## Source classification findings

- Malmi source: 260 message elements classified; 144 elements have both `message` and `satoshi` class tokens and an explicit Satoshi From header.
- `email-204`, `email-232`, and `email-238` are Satoshi-classed forwards with no newly authored Satoshi body. They are preserved as context but do not produce empty/header-only records.
- Malmi output: 141 substantive Satoshi-authored records.
- Hearn source: 33 explicit message tables classified by rendered sender header; 16 have Satoshi Nakamoto as sender.
- Hearn output: 16 Satoshi-authored records.

## Prior contamination diagnostic

Commit `0f733ee` was read only as a diagnostic. Its Hearn `0010` main section begins with Mike Hearn's client implementation prose. The corresponding phrases are absent from the new main sections:

- `mike-hearn/0010.md`: no `BitcoinJ`
- `mike-hearn/0011.md`: no `my app`
- `mike-hearn/0012.md`: no `secp256k1`
- `mike-hearn/0016.md`: no `rejoining the community`

The legitimate Satoshi-authored `BitcoinJ` reference in `mike-hearn/0016.md` remains and is emitted by the validator as a manual-inspection flag.

## Verdict

BLOCKED-REVIEW
