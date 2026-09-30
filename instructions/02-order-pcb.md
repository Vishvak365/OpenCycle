# 2 · Order the boards (JLCPCB)

Upload [`pcb/fab/opencycle_v0.2_gerbers.zip`](../pcb/fab/opencycle_v0.2_gerbers.zip) at jlcpcb.com → *Order now*. It detects 4 layers and a 46 × 86.4 mm board.

| Option | Choose | Why |
|---|---|---|
| Layers | 4 | GND and 3.3 V planes |
| Thickness | **1.0 mm** | The enclosure stack is built around 1.0 mm |
| Impedance control / stack-up | **JLC04101H-3313** (or ask for impedance control) | The GPS feed (RF_IN) is a 0.2 mm trace over In1; check ~50 Ω in JLC's calculator |
| Surface finish | **ENIG** | Flat pads for the LGA barometer, QFN amp and 0.5 mm FFC connector |
| Via covering | Tented | Default |
| Min via / hole | 0.3 mm vias; the ESP32 thermal pad has 0.2 mm holes (JLC standard for 4-layer) | |
| Mark on PCB ("order number") | "Specify a location" or "Remove" | The back is crowded |
| Stencil | **Yes**, framework-less, top **and** bottom (or two stencils) | Needed for paste on both sides |
| Quantity | 5 | |

## If JLCPCB should assemble it (optional)

Upload [`pcb/fab/bom_jlcpcb.csv`](../pcb/fab/bom_jlcpcb.csv) and [`pcb/fab/cpl_jlcpcb.csv`](../pcb/fab/cpl_jlcpcb.csv). JLC matches parts by the *Manufacturer Part Number* column. Expect some parts to be "global sourcing" or not stocked (the BL652, the Taoglas patch, the BMP581); either let JLC source them or send them your own (consigned parts).

**Check every rotation in JLC's 3D preview before paying** — KiCad and JLC disagree on the zero orientation of some packages (SOT-23, QFN, connectors). Pin 1 dots must match the silkscreen/assembly drawing.

Two sides of assembly costs more; a cheaper split is JLC for the back side (modules, QFN, LGA) and your iron for the front side.

## Check before paying

- JLC's Gerber viewer shows the rounded 46 × 86.4 mm outline, four M2 holes, and antenna cut-outs in the inner planes at the left and right edges.
- Four copper layers present (F.Cu, In1 GND, In2 3V3, B.Cu).
