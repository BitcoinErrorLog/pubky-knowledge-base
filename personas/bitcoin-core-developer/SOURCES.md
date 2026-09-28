# Bitcoin Core Developer source register

Pinned archives:

- Bitcoin Core v31.1, `9be056a8a72b624dae9623b2f7bded92c2a21c91` (MIT): source,
  `doc/`, and release notes.
- BIPs, `3a10b5b5f0a7586df8928d580a3009744ebb2079`: pending per-file
  SPDX validation.
- Bitcoin Optech, `dde4704ac894fc59829b283e5e9c8c4b8e50dcec` (MIT site text).

`validate-sources.py` checks archive hashes and fails closed when any BIP lacks
a `License:` field. The pinned BIP tree currently fails that condition, so no
BIP text is approved for retrieval until the per-file rights manifest
quarantines or resolves every missing declaration.
