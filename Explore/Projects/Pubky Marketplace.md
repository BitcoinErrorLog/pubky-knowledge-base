# Pubky Marketplace

**Status:** pre-production and deployed to staging at [shop.pubky.app](https://shop.pubky.app/marketplace). Do not treat it as ready for real funds: Bitcoin runs on regtest, fiat checkout uses Stripe test mode and PayPal sandbox, and no independent security review has been completed.

## What users can do

Sellers can create a shop, publish seller-owned listings, set fixed prices or auctions, manage inventory and drops, and progress orders. Buyers can discover listings, make offers or proxy bids, check out, follow order state, leave attested reviews after purchase, and use encrypted buyer-seller messaging in durable modes. Buyers and sellers keep signed portable order receipts on their own Homeservers.

The transaction service is server-authoritative for offers, auctions, orders, returns, payments, notifications, and role-scoped projections. Marketplace records are indexed by a dedicated Nexus deployment; the shared official Nexus does not yet include those marketplace endpoints. Payment rails compose Locks and Paykit, with a real Bitkit wallet-leg staging proof, but the environment is still pre-production.

The separate `@bitcoinerrorlog/pubky-shop` package reached 0.1.5 on 22 September. It provides inventory, JSON/CSV codecs, and import manifests used by Shop.

Sources: [project map and status](https://github.com/BitcoinErrorLog/pubky-marketplace), [transaction service](https://github.com/BitcoinErrorLog/pubky-marketplace-service), [Shop SDK](https://github.com/BitcoinErrorLog/pubky-shop), [Shop releases](https://github.com/BitcoinErrorLog/pubky-shop/releases), [live staging client](https://shop.pubky.app/marketplace).
