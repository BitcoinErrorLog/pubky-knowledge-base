# Pubky Locks

**Status on 25 September 2026:** Locks is public, active commerce infrastructure used by the pre-production Marketplace stack. Its in-app surfaces support password and payment-based unlocking, receipt submission, grant handling, and locked-content state. That does not make the whole stack production-ready for real funds.

Locks is an authorization layer for content, subscriptions, memberships, and digital goods. A compatible app presents a lock, obtains proof such as a password or Paykit receipt, sends a proof bundle for verification, and receives an unlock grant. In Pubky App work this enables locked content and collections and connects payment receipts to access decisions.

Marketplace composes Locks with Paykit for its staged purchase journey. Bitcoin is regtest, fiat processors are test/sandbox, and the Marketplace status explicitly requires independent security review before real funds.

Sources: [Locks repository](https://github.com/pubky/locks), [public Locks README and design](https://github.com/pubky/locks), [Marketplace project status](https://github.com/BitcoinErrorLog/pubky-marketplace), [Pubky App collections issue](https://github.com/pubky/pubky-app/issues/1466).
