# PCB (v0.2)

Status: **routed, DRC clean, schematic netlist-matched, fab files exported.** Not yet built. Review checklist and what is still unverified: [`pcb/README.md`](../pcb/README.md).

## Stack-up and rules

- 4 layers, 1.0 mm FR-4: F.Cu (front, display side) / In1 GND plane / In2 +3V3 plane / B.Cu (back, battery side). Order as JLCPCB **JLC04101H-3313** (or any 1.0 mm 4-layer).
- Outline 46 × 86.4 mm, 4 mm corner radius. M2 plated holes at (6.5, 6.5), (45.5, 6.5), (6.5, 85.9), (45.5, 85.9).
- Rules: 0.15 mm clearance / 0.2 mm default track, vias 0.5 / 0.3 mm, 0.3 mm copper to edge, min drill 0.2 mm (only the ESP32 thermal-pad vias). Power: VBAT / BATT+ / VBUS 0.5 mm, +3V3 0.4 mm, backlight 0.4 mm, speaker 0.3 mm.
- RF_IN (patch → GPS) is a 4 mm, 0.2 mm-wide trace on F.Cu directly over the In1 ground plane (≈ 50 Ω on a 0.1 mm prepreg; check with the JLC impedance calculator for the stack-up you order).
- Board coordinates: KiCad x right, y down, seen from the front. Enclosure CAD: `cad_x = x`, `cad_y = 92.4 − y`.

## Pipeline (all scripted; `tools/build_all.sh` runs it)

```bash
cd pcb
python3 build_pcb.py                       # design.py -> placed.kicad_pcb (+ local footprints, keep-outs, RF feed)
python3 check_place.py                     # courtyards, enclosure height zones, keep-outs, holes vs. other side
python3 fanout.py placed.kicad_pcb fanned.kicad_pcb      # escapes + a via for every GND / +3V3 pad
python3 autoroute.py fanned.kicad_pcb routed.kicad_pcb 60  # Freerouting 1.9 (headless) round trip
python3 finish.py routed.kicad_pcb opencycle.kicad_pcb   # rules, planes, pours, stitching, clean-up, DRC
python3 gen_schematic.py && python3 check_netlist.py     # schematic from design.py; netlist == board
python3 export_fab.py                      # Gerbers, drill, BOMs, CPL, assembly PDFs -> pcb/fab/
python3 export_viewer.py opencycle.kicad_pcb             # viewer/pcb.json + textures
```

| Script | What it does |
|---|---|
| `design.py` | Every part: symbol, footprint, side, position, rotation, pin → net, MPN, height. Keep-outs, height zones, rules. |
| `lib/gen_symbols.py`, `lib/gen_footprints.py` | Local symbols/footprints KiCad doesn't ship: BMP581 (from Bosch's drawing), Taoglas 12 mm patch (from Taoglas's drawing), speaker pads. |
| `check_place.py` | Fails on courtyard overlaps, parts too tall for the enclosure zone they sit in, parts in antenna keep-outs, screw/standoff clashes, through-holes under parts on the other side. |
| `fanout.py` | Stubs + vias from every plane pad to its plane, via-in-pad for the LDO tab, escapes for boxed-in pads (BMP581 I²C, backlight anode), stitching vias under the patch. |
| `autoroute.py` + `ses_import.py` | DSN export with net classes, Freerouting headless, SES import without the KiCad GUI. |
| `finish.py` | Re-applies the design rules, pours, removes dangling autorouter pieces, stitches outer GND pours to In1 on a 2.5 mm grid and into every island, DRC with `rules.kicad_dru`. |
| `gen_schematic.py`, `check_netlist.py` | Label-connected schematic from the same table; KiCad netlist export compared pin-by-pin with the board. |
| `export_fab.py`, `sourcing.py` | Fab package and distributor BOM (prices, links, stock). |

## Placement

- **Front, top band (above the display):** 12 mm patch (centre-right), MAX-M10S left of it (short RF feed), charge LED and light sensor on the right under lens-mask windows.
- **Front, under the display (≤ 2.15 mm tall; ≤ 1.3 mm under the folded FFC):** display connector J3 in the centre, LDO + caps on the left, backlight FET and ballasts on the right.
- **Front, bottom band:** three PTS810 keys under the key caps (turned 90° so the USB-C locating pegs clear them).
- **Back, top:** ESP32 module (antenna at the right edge) and BL652 (antenna at the left edge), each with a keep-out on every layer.
- **Back, middle (over the battery, ≤ 3.3 mm):** passives, Tag-Connect pads, side switches at the edges, BMP581 at the right edge beside the case vent.
- **Back, bottom:** USB-C (mouth 0.9 mm past the board edge), ESD, charger, reverse-battery FET, JST-PH socket, amp and speaker pads.

## Verification results (committed with the board)

| Check | Result | File |
|---|---|---|
| Placement (courtyards, heights, keep-outs, holes) | placement OK | `pcb/check_place.py` |
| KiCad DRC | **0 errors, 0 unconnected**, 6 warnings (ESP32 footprint deliberately differs from the library: keep-out replaced; 4 × module silk clipped at the board edge; 1 redundant BMP581 escape via on SDA, connected on B.Cu only, harmless) | `pcb/drc_report.txt` |
| Schematic vs. board | **netlist match: 55 nets, 282 pin connections** | `pcb/check_netlist.py` |
| ERC (KiCad 9 CLI) | **0 errors**; 3 explained warnings (BMP581 SDO/INT tied to GND, amp thermal pad) + library-table notices | `pcb/erc_report.txt` |
| Real parts vs. enclosure (3D) | **board fit OK** (67 parts, all three case styles) | `cad/board_fit.py` |
