# Build instructions — OpenCycle v0.2

The path from this repo to a working bike computer. Follow the files in order; each one ends with a check you should pass before moving on.

| Step | File | Time | Cost (first unit) |
|---|---|---|---|
| 1 | [01-order-parts.md](01-order-parts.md) — electronics from Mouser + Digi-Key, battery, lens, small hardware, tools | 1 h to order, ~1 week to arrive | ~$89 parts + tools |
| 2 | [02-order-pcb.md](02-order-pcb.md) — boards (and optionally assembly) from JLCPCB | 30 min to order, 1–2 weeks | ~$25–40 for 5 bare boards + stencil |
| 3 | [03-print-case.md](03-print-case.md) — shells, keys, buttons | ~5 h printer time | ~$1 filament |
| 4 | [04-assemble-board.md](04-assemble-board.md) — solder both sides | 3–5 h | — |
| 5 | [05-bring-up.md](05-bring-up.md) — first power-on, rail checks, each chip answers | 2 h | — |
| 6 | [06-final-assembly.md](06-final-assembly.md) — display, lens, battery, close the case | 1 h | — |
| 7 | [07-next-steps.md](07-next-steps.md) — firmware plan, UI, open questions | — | — |

Order steps 1 and 2 on the same day; print the case while you wait.

Everything referenced here is generated and committed: Gerbers and BOMs in [`pcb/fab/`](../pcb/fab), print files in [`print/`](../print), the parts list with links in [`docs/sourcing/bom-v0.2.md`](../docs/sourcing/bom-v0.2.md).
