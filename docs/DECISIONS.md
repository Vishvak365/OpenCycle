# Decisions and open questions

Append new entries at the bottom. Format: date — decision — why.

## Decided

- 2026-09-29 — Build a custom device rather than buy (a GEOID CC700 Pro is ~$70 and a DIY unit costs more). Why: open-source project and learning; target long battery life and open firmware as differentiators.
- 2026-09-29 — Sharp 2.7" memory LCD (1-bit) for v1. Why: sunlight-readable, microwatt power, proven in hobby projects. Colour MIP (JDI) is the v2 candidate.
- 2026-09-29 — nRF52840 module (Raytac MDBT50Q) for BLE + ANT+. Why: pre-certified, one chip for both sensor protocols.
- 2026-09-29 — u-blox MAX-M10S GPS. Why: lowest-power multi-constellation receiver in its class.
- 2026-09-29 — 16 MB QSPI flash instead of microSD. Why: no card slot to seal in a printed case.
- 2026-09-29 — Add I²S speaker (MAX98357A + 11 × 15 mm speaker, ~$4). Cost: battery narrowed from 34 to 30 mm.
- 2026-09-29 — 4-layer board with GND and 3V3 planes. Why: RF parts and routing density.
- 2026-09-29 — Source from Digi-Key/Mouser where possible. Swaps agreed: BMP280 → LPS22HH, HRO USB-C → GCT USB4105, Sunlord inductor → Taiyo Yuden NR3015, GPS patch → Taoglas DSGP.1575.15.4.A.02.

## Open (as of 2026-09-29, v0.1; superseded by the v0.2 decisions below)

- Module source: MDBT50Q from SparkFun (no board change) vs u-blox NINA-B306 (Digi-Key/Mouser, needs a new footprint).
- Battery: 6 mm (~850 mAh, 16 mm case) vs 8 mm (~1100 mAh, current) vs 10 mm (~1500 mAh, +2 mm case).
- Sharp LS027 availability (Digi-Key showed 0 stock / 28-week lead). Fallbacks: Mouser, Tindie, AliExpress.
- Assembly: JLCPCB PCBA (needs LCSC part numbers) vs hand/US assembly from Digi-Key parts.
- Front light for night riding.
- License (likely CERN-OHL-S hardware + MIT software).

- 2026-09-30 — Colour display direction (candidate v0.2): ESP32-S3-WROOM-1-N16R8 + BL652 (nRF52832) as ANT+ coprocessor + Newhaven NHD-2.4-240320AF-CSXP IPS TFT. Parts sourced from Mouser + Digi-Key only; see sourcing/bom-colour-v0.2.md (since replaced by sourcing/bom-v0.2.md). Why: colour UI, Wi-Fi, LVGL headroom; ANT+ kept via coprocessor. Cost: ~10–22 h battery vs ~100 h.
- 2026-09-30 — Front layout: buttons on the front, under the screen; keep a 12 mm ceramic patch GPS antenna under the top band (~15 mm top border, ~52 × 92 mm body) rather than a chip antenna. Why: best GPS reception; the owner accepted the taller top band. Power button on the left side. Button arrangement still being chosen from the D1–D4 mockups.
- 2026-09-30 — Controls: three unlabelled front soft keys under the screen, with context labels drawn in a bar at the bottom of the display (e.g. ride: Lap / Page / Start; map: zoom out / re-centre / zoom in), plus two side buttons (left: power/back, right: menu). Five switches total.
- 2026-09-30 — Colour build (v0.2) is the design going forward: ESP32-S3-WROOM-1-N16R8 + BL652 (ANT+/BLE) + MAX-M10S + Newhaven NHD-2.4-240320AF-CSXP. The mono v0.1 files stay in git history only. Why: owner chose colour + Wi-Fi; ANT+ kept via the BL652.
- 2026-09-30 — Screen UI language "Lucent" (glass cards over deep navy, Inter, colour only for meaning) replaces the first colour pass "Meridian". Why: owner found Meridian too Tron-like; asked for Apple Liquid Glass but more functional. Glass is faked without blur so LVGL can reproduce it 1:1 (docs/UI.md §5).
- 2026-09-30 — GPS antenna: Taoglas DSGP.1575.12.4.A.02 (12 × 12 × 4 mm SMT patch, Digi-Key) under a 15.6 mm top band, fed by a 4 mm trace from the MAX-M10S next to it. Why: best reception that still fits the band; the land pattern comes from the Taoglas datasheet §6.5.
- 2026-09-30 — Front soft keys: C&K PTS810 top-actuated switches (4.2 × 3.2 × 2.5 mm), mounted rotated 90° so the USB-C receptacle's locating pegs clear the centre switch. Side buttons stay Alps SKRTLAE010.
- 2026-09-30 — Radios at opposite edges: ESP32 antenna at the right edge, BL652 antenna at the left edge, each with a copper keep-out on all layers; the GPS patch sits between them at the top.
- 2026-09-30 — Protection and power: P-FET (DMG2305UX) reverse-battery protection, 1 A AP7361C LDO, MCP73831 500 mA charger, backlight from VBAT through four 33 Ω 0603 ballasts and a PWM FET (≤ 45 mA per LED worst case, within the panel's 200 mA total).
- 2026-09-30 — Battery: Adafruit 258 (1200 mAh, 34 × 62 × 5 mm, protected, JST-PH) in a 0.5 mm floor pocket. Connector wired pin 1 = −, pin 2 = + (common JST-PH LiPo convention); Q2 blocks a reversed cell.
- 2026-09-30 — Programming: ESP32 over native USB-C; BL652 over SWD with a Tag-Connect TC2030-NL footprint (no connector to buy per board). A second TC2030 footprint carries the ESP32 UART0/EN/IO0 for recovery.
- 2026-09-30 — Board process: 4 layers (In1 GND, In2 +3V3), 1.0 mm, 0.15 mm clearance, 0.5/0.3 mm vias, 0.2 mm drills in the ESP32 thermal pad. Routed with Freerouting after a scripted fan-out; DRC 0 errors / 0 unconnected; schematic generated from the same table and netlist-checked against the board.
- 2026-09-30 — Sourcing: two vendors. Mouser for almost everything, Digi-Key for the BMP581, the 12 mm patch and the DMG2305UX. JLCPCB for bare boards (+ stencil); assembly by hand/hot plate or by a US assembler from the distributor BOM (JLC PCBA possible via MPN matching, not verified part by part).

## Open (as of 2026-09-30, after the v0.2 board)

- First prototype bring-up: nothing is built yet. See instructions/05-bring-up.md for the checklist.
- GPS/Wi-Fi/BLE antenna performance is not measured; the patch ground plane is far smaller than Taoglas's 50 × 50 mm test board.
- Battery polarity: check the Adafruit lead against J2 with a meter before first plug-in (Q2 protects either way).
- License (CERN-OHL-S for hardware + MIT for software suggested).
- Front light for night riding is not needed with the backlit TFT; dropped.
