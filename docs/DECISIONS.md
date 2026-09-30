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

## Open

- Module source: MDBT50Q from SparkFun (no board change) vs u-blox NINA-B306 (Digi-Key/Mouser, needs a new footprint).
- Battery: 6 mm (~850 mAh, 16 mm case) vs 8 mm (~1100 mAh, current) vs 10 mm (~1500 mAh, +2 mm case).
- Sharp LS027 availability (Digi-Key showed 0 stock / 28-week lead). Fallbacks: Mouser, Tindie, AliExpress.
- Assembly: JLCPCB PCBA (needs LCSC part numbers) vs hand/US assembly from Digi-Key parts.
- Front light for night riding.
- License (likely CERN-OHL-S hardware + MIT software).

- 2026-09-30 — Colour display direction (candidate v0.2): ESP32-S3-WROOM-1-N16R8 + BL652 (nRF52832) as ANT+ coprocessor + Newhaven NHD-2.4-240320AF-CSXP IPS TFT. Parts sourced from Mouser + Digi-Key only; see sourcing/bom-colour-v0.2.md. Why: colour UI, Wi-Fi, LVGL headroom; ANT+ kept via coprocessor. Cost: ~10–22 h battery vs ~100 h.
