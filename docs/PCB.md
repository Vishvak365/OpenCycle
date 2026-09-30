# PCB

> Concept board — **not for fabrication.** Status and to-do list: [`../pcb/README_NOT_FOR_FAB.md`](../pcb/README_NOT_FOR_FAB.md).

## Stack-up and rules

- 4 layers, 1.0 mm: F.Cu (signals, front/display side) / In1 GND plane / In2 +3V3 plane / B.Cu (signals, battery side).
- Outline 46 × 80 mm, 4 mm corner radius, M2 plated holes at (6.5, 6.5), (45.5, 6.5), (6.5, 79.5), (45.5, 79.5).
- Intended rules: 0.2 mm tracks, 0.15 mm clearance (router uses 0.2 for margin), vias 0.5 / 0.3 mm, 0.3 mm copper-to-edge.
- Power nets: VBAT / VBUS / BOOST_SW 0.4 mm; +5V_DISP / RF_IN 0.3 mm; speaker 0.25 mm.

## Pipeline

```bash
cd pcb
python3 build_pcb.py                       # design.py -> placed.kicad_pcb
python3 assign_pins.py placed.kicad_pcb    # choose nRF GPIOs by geometry -> pinmap.json
python3 build_pcb.py                       # rebuild with the new pin map
python3 check_place.py                     # courtyards, battery/speaker keep-outs, standoffs
python3 router.py placed.kicad_pcb routed.kicad_pcb     # ~10 passes, keeps the best
python3 finish.py routed.kicad_pcb opencycle.kicad_pcb  # planes, pours, zone fill, drc_report.txt
python3 export_viewer.py opencycle.kicad_pcb            # viewer/pcb.json + textures
```

## Placement concept

- **Back (battery side), top third:** nRF52840 module (antenna toward the top edge, keep-out honoured), GPS receiver, flash.
- **Back, edges:** three side switches, USB-C at the bottom edge, battery connector bottom-left, speaker pads bottom-right.
- **Back, middle:** battery pocket (no parts) and speaker pocket (no parts).
- **Front (display side):** GPS patch antenna top-centre over solid ground; power (charger, LDO, boost) mid-lower; level shifters in a row above the display connector; sensors mid-board; speaker amp right; Tag-Connect pads top-left.
- Front components must stay under ~1.8 mm (display sits 2.3 mm above the PCB).

## The router (`router.py`)

A purpose-built grid maze router, because Freerouting wasn't available:

- 0.1 mm grid, 8-direction A* (numba-compiled), vias between F.Cu and B.Cu, small turn penalty.
- GND and +3V3 pads get a short fan-out + via to the inner planes first.
- Module inner-row pads get "dog-bone" escapes (short track + via) before routing.
- Nets are routed as growing trees; power nets first, then signals by length; failed nets are moved to the front and the board is re-routed (best of 10 passes).

Known weaknesses: fine-pitch escapes are crowded around U1; the result still needs manual clean-up in KiCad. Swapping to Freerouting or hand-routing is a reasonable next step.

## Known issues

See `pcb/drc_report.txt` and `pcb/routed.unrouted.json`. Summary:
- 12 unrouted connections (speaker leads, some display lines, I2C_SCL, BOOST_FB, USB_DP_C, GNSS_RST/TXD, SWDCLK).
- Clearance netclass saved as 0.2 mm, not the intended 0.15, which inflates the violation count.
- Some fan-out tracks within 0.18 mm of neighbouring pads; a few duplicate or dangling vias.
- Switch footprint NPTH pegs sit 0.1 mm from their own pads (library footprint, per datasheet).
- RF_IN is not impedance-controlled; the patch/nRF keep-outs were checked by eye only.
