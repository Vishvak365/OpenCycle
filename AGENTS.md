# AGENTS.md — working on OpenCycle

Read this first. It tells an AI agent (or a new human contributor) where the truth lives, how to rebuild, and what not to break.

## The one-paragraph summary

OpenCycle is a DIY GPS bike computer (v0.2: ESP32-S3 + BL652 for ANT+ + u-blox M10 + 2.4" colour IPS TFT, 52 × 92.4 × 17 mm printed case). **Everything is generated from source files**: the enclosure from `cad/params.py` + `cad/model.py`, the board *and* its schematic from `pcb/design.py`, the BOMs from `pcb/design.py` + `pcb/sourcing.py`, the viewer assets from all of them. Never hand-edit generated outputs (`pcb/opencycle.kicad_pcb`, `pcb/opencycle.kicad_sch`, `pcb/fab/*`, `docs/sourcing/bom-v0.2.md`, `print/*`, `viewer/meshes.json`, `viewer/pcb.json`, `viewer/pcb_*.png`, `docs/media/*`). Change the source, then run `tools/build_all.sh`.

## Sources of truth

| Topic | File | Notes |
|---|---|---|
| Enclosure dimensions | `cad/params.py` | Coordinate system documented at the top. Body 52 × 92.4 × 17 mm. |
| Enclosure geometry | `cad/model.py` | Case variants: standard, aero, rugged. |
| Mechanical fit | `cad/check_fit.py`, `cad/board_fit.py` | Both must print OK after any change. `board_fit.py` checks every real board part (datasheet heights) against the case. |
| Parts, nets, placement, rules | `pcb/design.py` | One `part(...)` call per component, with MPN and height. Keep-outs, height zones, escapes and design rules live here too. |
| Local symbols / footprints | `pcb/lib/gen_symbols.py`, `pcb/lib/gen_footprints.py` | BMP581 and Taoglas patch, drawn from the manufacturers' drawings. |
| Where parts are bought | `pcb/sourcing.py` | Vendor part numbers, prices, stock, date checked, datasheets. |
| Screen UI | `viewer/ui/screens_color.js` + `docs/UI.md` | "Lucent" design language, 240 × 320 RGB565, LVGL-implementable. The firmware will port this. |
| Decisions / open questions | `docs/DECISIONS.md` | Append to it; don't rewrite history. |
| How to build one | `instructions/` | Order → PCB → print → assemble → bring-up → close. |

## Coordinate systems (important)

- **CAD** (mm): x = width (0..52), y = height (0 = bottom edge with USB-C, 92.4 = top), z = depth (0 = back face, 17 = front of the lens). The Garmin mount boss is at negative z.
- **KiCad board** (mm): x right, **y down**, viewed from the front (display side = F.Cu). Board outline x 3..49, y 3..89.4.
- Conversion: `cad_x = kicad_x`, `cad_y = 92.4 - kicad_y`. PCB back face at `cad_z = 10`, front at `11`.
- Back-side (B.Cu) parts hang toward the battery: ≤ 3.3 mm over the battery pocket; front parts ≤ 2.15 mm under the display and ≤ 1.3 mm under the folded display FFC (`design.HEIGHT_ZONES`, enforced by `check_place.py`).

## Rebuild

```bash
./tools/build_all.sh          # full pipeline, ~10 min (Freerouting dominates)
```

Individual steps are in `docs/PCB.md` and `docs/CAD.md`. Required tools: `docs/SETUP.md` (KiCad 7 for the pipeline; the KiCad 9 CLI is optional, used only for ERC).

## Rules for changes

1. **Mechanical changes:** edit `cad/params.py`, run `cad/check_fit.py` and `cad/board_fit.py`, then `tools/export_meshes.py` and `tools/export_print.py`.
2. **Board changes:** edit `pcb/design.py` → `build_pcb.py` → `check_place.py` must say `placement OK` → `fanout.py` → `autoroute.py` → `finish.py`; `pcb/drc_report.txt` must show **0 errors and 0 unconnected**; `gen_schematic.py` + `check_netlist.py` must say `netlist match`; then `export_fab.py`.
3. If a board part moves, check the matching enclosure feature (key caps, side plungers, USB-C cut-out, patch relief, lens windows, standoffs) and update `cad/params.py`.
4. **Pinouts:** never trust a KiCad symbol alone for a new part — read the manufacturer's pin table (two symbol/notes errors were caught this way: BMP581 order, MAX-M10S pin 15). Record the source in the header of `design.py`.
5. **UI changes:** keep to what LVGL 9 on an ESP32-S3 can draw 1:1 — no real-time blur; the glass recipe is in `docs/UI.md` §5. Render screenshots with `docs/ui/shoot.mjs`.
6. **Public repo:** never commit personal information, credentials, or local absolute paths. Commit messages carry no AI co-author trailers.
7. **Honesty about status:** anything not verified (RF performance, rotations in the CPL, battery lead polarity, anything not built) must be marked as such in docs. `pcb/README.md` holds the current list.

## Current state (keep this section up to date)

- Enclosure: v0.2, 52 × 92.4 × 17 mm, three variants, fit-checked against placeholders **and** the real routed board; print-ready STLs in `print/`.
- PCB: v0.2 routed, **DRC 0 errors / 0 unconnected**, schematic generated and netlist-matched, ERC 0 errors, Gerbers/BOM/CPL in `pcb/fab/`. Not yet built. See `pcb/README.md`.
- Sourcing: every part priced with links (Mouser + Digi-Key), `docs/sourcing/bom-v0.2.md`, ~$89 per unit in parts.
- UI: "Lucent" (glass, Inter), 10 screens rendered in `docs/ui/`.
- Viewer: three.js page with the v0.2 case, the real routed board, net explorer, Lucent screens; PCB time-lapse in `docs/media/`.
- Firmware: not started (owner is finishing the UI first). Plan in `docs/FIRMWARE.md`.
