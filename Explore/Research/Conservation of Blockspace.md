# Conservation of Blockspace

John Carvalho (BitcoinErrorLog), listed as CEO on the [Synonym team page](https://synonym.to/team), is the named author of *Credible Exit and the Law of Conservation of Blockspace*, version 1.10.3, dated May 2026. The public site is [blockspace.science](https://blockspace.science/). The paper, the interactive toy, and the site text live in [BitcoinErrorLog/conservation-of-blockspace](https://github.com/BitcoinErrorLog/conservation-of-blockspace) at commit `f90bb0b2d5658e0f9953906308670a71350b7a2a`. This page reports that publication. It does not adopt the paper as a Synonym product specification.

See [[John Carvalho]] for his other public work.

## Thesis

In the paper, John Carvalho argues that Bitcoin layers can increase cooperative payment throughput, while non-custodial safety still depends on the base layer when users must enforce without cooperation. He defines an **exit unit** as the minimal unilateral enforcement trace for a distinct claim. Human users, wallets, channels, VTXOs, or accounts map onto exit units according to the protocol and wallet topology. He defines **credible exit** here as the ability to confirm, without cooperation, the transaction set that secures an operator-independent Layer 1 claim inside a usable safety window `W′`, with non-dust value remaining.

He calls the **Law of Conservation of Blockspace** a finite-window block-weight accounting bound. For a simultaneous exit cohort with per-exit-unit enforcement weights `e_i`, the paper requires `Σ_i N_i e_i ≤ ρ · C_max(W′)`. `ρ` bounds the fraction of physical block capacity he treats as usable for those enforcement packages under relay, policy, fee-bumping, and miner selection. `C_max(W′)` is `(4,000,000 − w_cb) × W′` weight units, with coinbase overhead `w_cb` approximately 2,000 wu. He says the bound is a necessary condition for worst-case non-cooperative exit. He says it does not forecast average payment throughput.

The tradeoff he draws is the window, not new blockspace. The paper uses three named windows: 137 blocks as a fast-exit stress case (about one day), 2,016 blocks as the 14-day layer benchmark, and 4,032 blocks as a 28-day slow-settlement runway. Longer windows raise how many exit units fit by delaying settlement.

At `ρ = 0.8`, the paper’s window table gives these simultaneous exit-unit ceilings. Each entry is `floor(0.8 · (4,000,000 − 2,000) · W′ / e)`. Lightning weights are his declared reference profile. He says the Ark-style and operator-assisted columns are illustrative templates until a concrete construction supplies a measured enforcement trace.

| Window | Lightning active stress (`e = 5848`) | Lightning idle (`e = 2360`) | Ark-style template (`e = 3200`) | Operator-assisted template (`e = 3400`) |
| --- | ---: | ---: | ---: | ---: |
| 137 blocks | 74,928 | 185,669 | 136,931 | 128,876 |
| 2,016 blocks | 1,102,594 | 2,732,192 | 2,014,992 | 1,896,463 |
| 4,032 blocks | 2,205,189 | 5,464,385 | 4,029,984 | 3,792,926 |

The abstract rounds the 14-day, `ρ = 0.8` row to about 1.1 million Lightning HTLC-stress exit units, 2.0 million Ark-style exit units, or 1.9 million operator-assisted exit units. He writes that those capacities are purchased with time.

He also says the familiar one-day range of about 66 thousand to about 232 thousand is only the fast-exit envelope: 65,562 active HTLC-stress exits at `ρ = 0.7`, versus 232,087 idle exits at `ρ = 1.0`. He says that range should not be read as the default limit for every layer.

The paper’s limitations section says the result is a static block-weight accounting bound under stated relay, topology, and efficiency assumptions. It is not a mempool simulator, a fee-equilibrium model, or a proof about average-case payment throughput. Cooperative closes, watchtowers, and operator-mediated exits can reduce observed contention, and he places them outside the unilateral envelope unless each exit unit can still secure an operator-independent Layer 1 claim alone. He says policy work such as package relay and cluster mempool can change `ρ`. He says it does not remove the inequality for a simultaneous cohort with a positive unilateral footprint.

The knowledge-base page [[CredibleExit|Credible Exit]] uses that phrase for leaving a Pubky host with data and identity. In this paper, John Carvalho uses it for a timed, unilateral Bitcoin settlement claim.

## Site sections

The repository README maps the learning path. These routes returned HTTP 200 on 28 September 2026:

- [Start](https://blockspace.science/) — the site’s opening claim, in the page source: “Bitcoin has a size,” layers do not create blockspace, and they coordinate trust around it. The same page states the conservation inequality and points to the toy, trust networks, protocols, and the paper.
- [Paper](https://blockspace.science/paper) — embedded PDF, with downloads of [v1.10.3 PDF](https://blockspace.science/blockspace-conservation-may-2026-v1.10.3.pdf) and [TeX](https://blockspace.science/blockspace-conservation-may-2026.tex).
- [Toy](https://blockspace.science/toy) — calculator for `ρ`, `W′`, per-exit-unit weight, and demand, using the paper’s window presets.
- [Trust Networks](https://blockspace.science/trust-network) — the site’s claim that layers scale coordination because users believe the fallback still works, and that scarce fallback makes the trust model the product model.
- [Protocols](https://blockspace.science/protocols) — Lightning, Ark-style, factories, BitVM-class, and operator-assisted systems compared by common path, failure path, `W′`, `e`, and trust dependency.
- [Methods](https://blockspace.science/methods) — definitions of `C_max`, `ρ`, and `N_max`, plus the three named windows.
- [FAQ](https://blockspace.science/faq) — short answers, including his distinction between scaling coordination and scaling unilateral settlement.
- [Objections](https://blockspace.science/objections) — the hostile-read memo. It answers “are you saying layers are useless?” with: layers can scale the common path; they do not scale Bitcoin’s unilateral settlement surface. It also separates credit, custody, operator coordination, and unilateral settlement.
- [Review](https://blockspace.science/review) — a peer-review checklist for the inequality, `ρ`, and the positive unilateral footprint.
- [References](https://blockspace.science/references) — bibliography grouped by what each source is used to support.

## Sources

- [Paper TeX, abstract and title](https://github.com/BitcoinErrorLog/conservation-of-blockspace/blob/f90bb0b2d5658e0f9953906308670a71350b7a2a/blockspace-conservation-may-2026.tex#L24-L40)
- [Conservation principle](https://github.com/BitcoinErrorLog/conservation-of-blockspace/blob/f90bb0b2d5658e0f9953906308670a71350b7a2a/blockspace-conservation-may-2026.tex#L148-L170)
- [Window table](https://github.com/BitcoinErrorLog/conservation-of-blockspace/blob/f90bb0b2d5658e0f9953906308670a71350b7a2a/blockspace-conservation-may-2026.tex#L258-L298)
- [Limitations](https://github.com/BitcoinErrorLog/conservation-of-blockspace/blob/f90bb0b2d5658e0f9953906308670a71350b7a2a/blockspace-conservation-may-2026.tex#L319-L328)
- [Repository README](https://github.com/BitcoinErrorLog/conservation-of-blockspace/blob/f90bb0b2d5658e0f9953906308670a71350b7a2a/README.md)
- [Start page source](https://github.com/BitcoinErrorLog/conservation-of-blockspace/blob/f90bb0b2d5658e0f9953906308670a71350b7a2a/src/pages/Overview.tsx)
- [Objections memo](https://github.com/BitcoinErrorLog/conservation-of-blockspace/blob/f90bb0b2d5658e0f9953906308670a71350b7a2a/docs/HOSTILE_REVIEW.md)
- [Live PDF](https://blockspace.science/blockspace-conservation-may-2026-v1.10.3.pdf)
