# OpenCycle main board v0.2 — status

**Ready to order a first prototype run** (5 boards): routed, DRC clean, schematic generated and netlist-matched, parts sourced, fab files exported. **Not yet built or tested** — treat the first run as a prototype and follow [`../instructions/05-bring-up.md`](../instructions/05-bring-up.md).

| What | Where |
|---|---|
| Board | `opencycle.kicad_pcb` (+ `.kicad_pro`, `.kicad_dru`, `fp-lib-table`, `sym-lib-table`: opens in KiCad 7+) |
| Schematic | `opencycle.kicad_sch`, PDF in `fab/opencycle_schematic.pdf` |
| Gerbers + drill | `fab/opencycle_v0.2_gerbers.zip` (upload to JLCPCB as-is) |
| Assembly | `fab/bom_jlcpcb.csv`, `fab/cpl_jlcpcb.csv`, `fab/assembly_front.pdf`, `fab/assembly_back.pdf` |
| Order list | `fab/bom_distributors.csv` and [`../docs/sourcing/bom-v0.2.md`](../docs/sourcing/bom-v0.2.md) |
| Checks | `drc_report.txt`, `erc_report.txt`, `check_place.py`, `check_netlist.py`, `../cad/board_fit.py` |

Everything is generated from `design.py` — do not hand-edit the board and then regenerate, you will lose the edit. If you do route by hand in KiCad, stop using the pipeline for that board and say so in `docs/DECISIONS.md`.

## Verified

- Pinouts of every IC/module against the manufacturer datasheet (see the header of `design.py` for the list and `docs/sourcing/part-specs.md` for details). Two errors in earlier notes were found and fixed: the BMP581 pin order and MAX-M10S pin 15.
- Land patterns drawn from datasheet drawings for the BMP581 and the Taoglas 12 mm patch; all other footprints from the KiCad 7 library.
- Mechanical fit of every real part (datasheet heights) against the enclosure, display, folded FFC, battery and speaker.
- DRC 0 errors / 0 unconnected; ERC 0 errors; schematic netlist == board netlist.

## Not verified (look at these before ordering / during bring-up)

1. **RF performance** of all three antennas (GPS patch ground is 46 mm wide and cut by the radio keep-outs; Taoglas characterised it on 50 × 50 mm). Expect to tune firmware (GPS LNA gain) and possibly move to a pin-fed patch later.
2. **Battery polarity** of the Adafruit lead vs. J2 (pin 1 −, pin 2 +). Q2 blocks a reversed cell, but measure before plugging in.
3. **JLCPCB rotation offsets** in `cpl_jlcpcb.csv` — JLC's preview shows each part; fix any that are rotated (common for SOT-23, QFN and connectors) in their tool before paying.
4. **RF_IN impedance**: 0.2 mm on the 1.0 mm JLC04101H-3313 stack-up is close to 50 Ω; confirm with the JLC impedance calculator or ask for impedance control.
5. **Backlight brightness** with 33 Ω ballasts: ≤ 45 mA per LED in the worst case (4.2 V, Vf 2.7 V), ~21 mA typical, so full brightness is only reached on a full battery. Don't lower the ballasts unless firmware caps the PWM duty from VBAT_SENSE: at 22 Ω the worst case is 68 mA per LED, above the 50 mA per-LED limit.
6. **Charging while running:** there is no USB power path — the system always runs from VBAT and the MCP73831 charges the cell and feeds the load in parallel (the same approach as Adafruit Feather boards). While the device is on and plugged in, the charger may not terminate (it holds 4.20 V). Fine for a few hours of charging; a power-path charger (e.g. BQ24072) is the v0.3 upgrade if this matters.
7. **Firmware**: nothing is written yet; the pin map is in `docs/HARDWARE.md`.
