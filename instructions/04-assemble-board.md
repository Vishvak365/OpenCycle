# 4 · Assemble the board

Use the assembly drawings: [`pcb/fab/assembly_front.pdf`](../pcb/fab/assembly_front.pdf) and [`pcb/fab/assembly_back.pdf`](../pcb/fab/assembly_back.pdf) (reference designators are on the fab layer, not the silkscreen). The BOM with designators: [`pcb/fab/bom_jlcpcb.csv`](../pcb/fab/bom_jlcpcb.csv).

The board has parts on both sides. Solder the **back first** with normal paste, then the **front with low-temperature paste**, so the first side never re-melts.

## 1 · Back side (battery side) — SAC305 paste, stencil, hot plate

Parts: U1 ESP32-S3 module, U2 BL652, U8 BMP581, U7 MAX98357A, U6 charger, Q2, D2, J1 USB-C, J2 JST-PH, SW4/SW5 side switches, and all back-side passives.

1. Tape the board down, align the **bottom** stencil, spread paste once.
2. Place parts with tweezers. Orientation: pin-1 marks per `assembly_back.pdf`. The ESP32 antenna overhangs nothing — it ends flush with the right board edge; the BL652 antenna end is at the left edge.
3. Reflow on the hot plate (back side up). Let it cool completely.
4. Inspect: no bridges on the BMP581 and the QFN; ESP32 and BL652 castellations wetted along every edge; USB-C shell tabs soldered.

## 2 · Front side (display side) — low-temperature paste (Sn42Bi58), hot air

Parts: AE1 GPS patch, U3 MAX-M10S, J3 FFC connector, U4 light sensor, D1 LED, U5 LDO, Q1 + R5–R10 backlight, SW1–SW3 key switches, front-side passives.

1. Support the board on a frame so the back-side parts hang free; align the **top** stencil and paste.
2. Place parts. **J3**: latch side toward the bottom edge, pin 1 on the left. **AE1**: the feed side (single small pad) faces the GPS module on the left. **SW1–SW3** are turned 90° (that's intentional).
3. Reflow with hot air (or an iron for the leaded parts). Keep the back side below ~180 °C.
4. Solder the speaker leads to the LS1 pads on the back (red = +, marked "+") once the case is ready (step 6).

## Check

- No solder bridges anywhere on J3 (0.5 mm pitch) — use flux and a drag tip if needed.
- Nothing is tall enough to foul the case: all parts are within the height zones the placement check enforces; if you substitute a part, check its height against `docs/CAD.md`.
