# Paykit status

**Status on 25 September 2026:** Paykit's latest public release is **0.1.0-rc55**, published 15 September. The `rc` label means release candidate, not a stable 1.0 declaration. This page records public implementation status only; the excluded draft protocol page remains excluded from Jeb's corpus.

Paykit lets apps discover where a Pubky identity can receive payment and exchange payment-related metadata such as requests, proofs, receipts, and receipt access. Apps and wallets retain control over actual payment execution and policy. rc55 added one-shot identity-record republishing from Swift and Kotlin without restoring a secret or session; it rebroadcasts the newest signed identity record unchanged.

In the Marketplace staging system, Paykit supplies Bitcoin payment-request and wallet handoff plumbing. The real Bitkit wallet leg has been exercised in staging, but Bitcoin settlement there uses regtest and Marketplace remains pre-production.

Sources: [Paykit repository](https://github.com/pubky/paykit-rs), [rc55 release](https://github.com/pubky/paykit-rs/releases/tag/v0.1.0-rc55), [Marketplace status](https://github.com/BitcoinErrorLog/pubky-marketplace).
