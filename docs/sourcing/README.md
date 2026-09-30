# Sourcing

Everything gathered while choosing and pricing parts. **Snapshot date: 2026-09-29/30 (v0.2 board parts re-checked 2026-09-30).** Prices are qty-1 USD, and stock moves daily, so re-check before ordering.

| File | Contents |
|---|---|
| [bom-v0.2.md](bom-v0.2.md) | **The board you order.** Every part on the v0.2 board plus the off-board items, with Mouser/Digi-Key part numbers, links, prices, stock and datasheets, grouped by function, with a cost roll-up. Generated from `pcb/design.py` + `pcb/sourcing.py`. |
| [../../pcb/fab/bom_distributors.csv](../../pcb/fab/bom_distributors.csv) | Same list as a spreadsheet, with quantities for 5 boards (import into a Mouser/Digi-Key cart). |
| [part-specs.md](part-specs.md) | Per-part engineering data for both builds: dimensions, pinouts, footprints, supply, datasheet links, and what's verified vs. still open. |
| [bom-mono-v0.1.md](bom-mono-v0.1.md) | The original Sharp memory-LCD build: LCSC (JLCPCB) numbers, then the Digi-Key/Mouser pricing pass. |
| [displays.md](displays.md) | Every display option looked at (mono, colour MIP, e-paper, TFT, OLED), with sources, prices, power, and availability. |
| [stock-issues-and-alternatives.md](stock-issues-and-alternatives.md) | Parts that were out of stock or rejected, why, and what replaced them. |
| [power-budget.md](power-budget.md) | Current-draw estimates and battery-life tables for both builds. |
| [market-reference.md](market-reference.md) | Commercial bike computers and existing open-source projects used as reference points. |

## Ordering rules

- Use at most three reputable vendors: **Mouser** (primary), **Digi-Key** (secondary), **Adafruit** (breakouts and dev hardware). Avoid marketplace sellers for production parts.
- Two vendors cover the v0.2 board: **Mouser** (everything else) and **Digi-Key** (BMP581, Taoglas 12 mm patch, DMG2305UX P-FET).
- Order the thin-stock parts first: BMP581 (462 at Digi-Key), AP7361C-33E-13 (733 at Mouser), JST-PH SMT header (269 at Mouser), speaker (597 at Mouser).
- Buy spares of the MAX98357A now; Mouser is dropping it from its catalogue.

## Verification levels used in these docs

- **Verified:** read from the distributor page or the manufacturer datasheet/drawing during this pass.
- **Library:** geometry taken from the official KiCad library footprint (assumed correct, not re-checked against the datasheet).
- **Open:** still needs checking; listed at the end of each file.
