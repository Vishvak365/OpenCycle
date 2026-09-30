# Hardware

## Block diagram (in words)

USB-C → ESD → Li-ion charger → battery → 3.3 V LDO → everything.
3.3 V → 5 V boost → Sharp memory LCD (through five 3.3→5 V buffers).
nRF52840 module talks to: GPS (UART), flash (QSPI), barometer + accelerometer (I²C), display (SPI-like), speaker amp (I²S), buttons (GPIO), USB (native).

## Parts and why

| Ref | Part | Job | Why this one |
|---|---|---|---|
| U1 | Raytac MDBT50Q-1MV2 | nRF52840 module: BLE 5 + ANT+, 1 MB flash, 256 KB RAM | Pre-certified module, integrated antenna, KiCad footprint exists. |
| U2 | u-blox MAX-M10S | GPS / Galileo / BeiDou / GLONASS receiver | ~25 mW tracking; the main reason battery life is ~100 h. |
| AE1 | 15 × 15 × 4 mm ceramic patch | GPS antenna | Planned: Taoglas DSGP.1575.15.4.A.02 (SMT feed). Footprint is still a pin-fed placeholder. |
| U3 | Winbond W25Q128JV | 16 MB QSPI NOR flash | Rides (FIT), routes (GPX), map tiles. Replaced an earlier microSD (no case slot to seal). |
| J1 | USB-C receptacle | Charging + data | Planned swap to GCT USB4105-GF-A (Digi-Key stock). |
| D1 | USBLC6-2SC6 | USB ESD protection | Standard. |
| U4 | MCP73831-2 | Li-ion charger, 500 mA | Simple, well known. Sets current with R3 = 2 k. |
| U5 | XC6220B331 | 3.3 V LDO, 700 mA, 8 µA Iq | Low standby drain. |
| U6 + L1 | TPS61220 + 4.7 µH | 5 V boost for the display | Sharp LS027 needs 5 V. Adjustable: R5/R6 set 5.05 V. |
| U7–U11 | SN74LV1T34 ×5 | 3.3 V → 5 V logic buffers | Display inputs are 5 V logic. Removable if a 3 V panel is chosen. |
| J3 | Hirose FH12-10S-0.5SH | Display FPC connector | Matches the LS027B7DH01 tail. |
| U12 | BMP280 → **LPS22HH** (planned) | Barometer: altitude, climb | BMP280 bare IC is out of stock at US distributors. |
| U13 | LIS3DH | Accelerometer | Wake on motion. |
| U14 | MAX98357A | I²S class-D amp, ~1 W into 8 Ω | Real sampled audio instead of buzzer beeps. |
| LS1 | 11 × 15 × 3.5 mm 8 Ω 1 W micro speaker | Alerts, turn prompts | E.g. Ole Wolff OWS-111535W50A-8. Wired to pads, fires through a grille in the back shell. |
| SW1–3 | Alps SKRTLAE010 | Side-push buttons | Page/lap and start/stop on the right, power on the left. |
| J2 | JST-SH 2-pin | Battery connector | Check lead polarity: JST-SH battery pinouts are not standardised. |
| J4 | Tag-Connect TC2030-NL | SWD programming pads | Nothing to assemble. |

## Display options considered

| Option | Colour | Sun | Power | Notes |
|---|---|---|---|---|
| **Sharp LS027B7DH01A (chosen)** | 1-bit | Excellent | ~0.1 mW | 5 V panel, needs boost + buffers. |
| JDI LPM027M128C colour MIP | 8 colours | Excellent | ~0.1–0.5 mW | 3 V: would remove boost + buffers. Hard to source (Switch Science discontinued). |
| E-paper 2.9" | 1-bit / grey | Excellent | ~0 static | Too slow for 1 Hz ride data. |
| Transflective colour TFT | full | Good | 15–30 mW + backlight | Needs a bigger MCU. |
| IPS TFT + touch | full | Poor | 100–300 mW | ~15–25 h battery. |

## Power budget (estimate, riding)

| Load | Avg current |
|---|---|
| GPS continuous tracking | 7–8 mA |
| nRF52840 + BLE/ANT+ sensors + logging | 1.5–3 mA |
| Display + boost (1–2 updates/s) | 0.1–0.2 mA |
| Sensors, flash, LDO, dividers | ~0.1 mA |
| **Total** | **~10–11 mA** |

| Battery | Est. ride time |
|---|---|
| 30 × 48 × 6 mm (~850 mAh, Jauch LP603048) | ~70–80 h |
| 30 × 48 × 8 mm (~1100 mAh) — current CAD | ~90–100 h |
| 30 × 48 × 10 mm (~1500 mAh, Jauch LP103048) | ~130 h (case +2 mm) |

The speaker is negligible on average. No front light yet, so the screen is unreadable in the dark.

## Sourcing (Digi-Key / Mouser, checked 2026-09-29) — full detail in [sourcing/](sourcing/README.md)

Verified: MAX-M10S (Mouser $9.12), Taoglas patch (Digi-Key $5.43), W25Q128JVSIQ ($2.88), GCT USB4105 ($0.80), MAX98357A ($3.73), Hirose FH12-10S ($1.75), SKRTLAE010 (~$0.34, low stock), LIS3DHTR (Mouser $1.94).
Problems: the Sharp LS027 showed 0 stock / 28-week lead at Digi-Key; the MDBT50Q is not stocked by Digi-Key or Mouser (SparkFun $8.95 in stock); bare BMP280 is out of stock (swap to LPS22HH).
Rough parts cost at qty 1: **$85–95** per unit, excluding PCB and case.
