# Bill of materials — board v0.2 (colour build)

_Generated from `pcb/design.py` + `pcb/sourcing.py` by `tools/gen_bom_md.py`. Do not edit by hand._

Prices are quantity-1 USD. **Checked** = read from the distributor on that date; **typical** = commodity part stocked in the millions, price not re-read. Stock moves daily: check the cart before you order.

Machine-readable versions: [`pcb/fab/bom_distributors.csv`](../../pcb/fab/bom_distributors.csv) (order list) and [`pcb/fab/bom_jlcpcb.csv`](../../pcb/fab/bom_jlcpcb.csv) (assembly).

## Radios and GPS

| Refs | Qty | Part | MPN | Buy | Price | Checked | Notes |
|---|---|---|---|---|---|---|---|
| AE1 | 1 | Taoglas 12 x 12 x 4 mm GPS L1 / Galileo E1 ceramic patch, SMT | `DSGP.1575.12.4.A.02` | [Digi-Key DSGP.1575.12.4.A.02](https://www.digikey.com/en/products/result?keywords=DSGP.1575.12.4.A.02) · [datasheet](https://www.taoglas.com/datasheets/DSGP.1575.12.4.A.02.pdf) | $4.25 | 2026-09-30, 1,474 in stock | 12 mm ceramic patch, feed toward the receiver. RF_IN is a short hand-placed 0.2 mm trace over the In1 ground plane. |
| U1 | 1 | ESP32-S3 module, 16 MB flash, 8 MB octal PSRAM, PCB antenna | `ESP32-S3-WROOM-1-N16R8` | [Mouser 356-ESP32S3WRM1N16R8](https://www.mouser.com/c/?q=356-ESP32S3WRM1N16R8) · [datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf) | $6.72 | 2026-09-30, 47,727 in stock | Main MCU: UI, logging, Wi-Fi, BLE, native USB. PCB antenna at the right board edge with a copper keep-out. |
| U2 | 1 | Ezurio (Laird) BL652, nRF52832 module, integrated antenna | `BL652-SA-01-T/R` | [Mouser 239-BL652-SA-01-T/R](https://www.mouser.com/c/?q=239-BL652-SA-01-T/R) · [datasheet](https://www.ezurio.com/wireless-modules/bluetooth-modules/bluetooth-5-modules/bl652-series-bluetooth-v5-nfc-module) | $10.40 | 2026-09-30, 5,583 in stock | nRF52832 module running an ANT+/BLE sensor bridge; talks to the ESP32 over UART. |
| U3 | 1 | u-blox M10 GNSS module, LCC-18 | `MAX-M10S-00B` | [Mouser 377-MAX-M10S-00B](https://www.mouser.com/c/?q=377-MAX-M10S-00B) · [datasheet](https://content.u-blox.com/sites/default/files/MAX-M10S_DataSheet_UBX-20035208.pdf) | $9.12 | 2026-09-30, 2,746 in stock | u-blox M10. Pin 15 is 'Reserved' on the MAX-M10S (KiCad names it VIO_SEL): left open. |

## Display and backlight

| Refs | Qty | Part | MPN | Buy | Price | Checked | Notes |
|---|---|---|---|---|---|---|---|
| J3 | 1 | Hirose 40-pin 0.5 mm bottom-contact FFC connector | `FH12-40S-0.5SH(55)` | [Mouser 798-FH12-40S-0.5SH55](https://www.mouser.com/c/?q=798-FH12-40S-0.5SH55) · [datasheet](https://www.hirose.com/product/series/FH12) | $2.50 | 2026-09-30, 25,967 in stock | Newhaven NHD-2.4-240320AF-CSXP, bottom-contact FFC. Pin 1 left. Cable enters from below after folding behind the panel. |
| Q1 | 1 | N-MOSFET 20 V SOT-23 (backlight PWM) | `DMG2302UK-7` | [Mouser 621-DMG2302UK-7](https://www.mouser.com/c/?q=621-DMG2302UK-7) · [datasheet](https://www.diodes.com/assets/Datasheets/DMG2302UK.pdf) | $0.39 | 2026-09-30, 238,766 in stock | Backlight PWM switch |
| R5, R6, R7, R8 | 4 | Yageo resistor 33R 0603 | `RC0603FR-0733RL` | [Mouser 603-RC0603FR-0733RL](https://www.mouser.com/c/?q=603-RC0603FR-0733RL) | $0.10 | typical | Backlight LED 1 ballast (0603 for dissipation) |
| R9 | 1 | Yageo resistor 100R 0402 | `RC0402FR-07100RL` | [Mouser 603-RC0402FR-07100RL](https://www.mouser.com/c/?q=603-RC0402FR-07100RL) | $0.10 | typical |  |
| R10 | 1 | Yageo resistor 100k 0402 | `RC0402FR-07100KL` | [Mouser 603-RC0402FR-07100KL](https://www.mouser.com/c/?q=603-RC0402FR-07100KL) | $0.10 | typical | Backlight off while the ESP32 boots |

## Power, USB, battery

| Refs | Qty | Part | MPN | Buy | Price | Checked | Notes |
|---|---|---|---|---|---|---|---|
| D1 | 1 | Green LED 0603 | `LTST-C191KGKT` | [Mouser 859-LTST-C191KGKT](https://www.mouser.com/c/?q=859-LTST-C191KGKT) · [datasheet](https://optoelectronics.liteon.com/upload/download/DS22-2000-229/LTST-C191KGKT.pdf) | $0.15 | 2026-09-30, 1,190,000 in stock | Charge LED behind the lens window (lit while charging). |
| D2 | 1 | USB ESD protection, SOT-23-6 | `USBLC6-2SC6` | [Mouser 511-USBLC6-2SC6](https://www.mouser.com/c/?q=511-USBLC6-2SC6) · [datasheet](https://www.st.com/resource/en/datasheet/usblc6-2.pdf) | $0.49 | 2026-09-30, 81,014 in stock | USB ESD |
| J1 | 1 | GCT USB-C receptacle, USB 2.0, top mount | `USB4105-GF-A` | [Mouser 640-USB4105-GF-A](https://www.mouser.com/c/?q=640-USB4105-GF-A) · [datasheet](https://gct.co/files/drawings/usb4105.pdf) | $0.80 | 2026-09-30, 420,427 in stock | USB 2.0 (ESP32 native USB) + charging |
| J2 | 1 | JST PH 2-pin side-entry SMT header | `S2B-PH-SM4-TB(LF)(SN)` | [Mouser 306-S2BPHSM4TBLFSN](https://www.mouser.com/c/?q=306-S2BPHSM4TBLFSN) · [datasheet](https://www.jst-mfg.com/product/pdf/eng/ePH.pdf) | $0.49 | 2026-09-30, 269 in stock | JST-PH battery socket for the Adafruit 258 cell. Pin 1 = -, pin 2 = + (common JST-PH LiPo convention). Q2 blocks a reversed battery; still check polarity with a meter before first plug-in. |
| Q2 | 1 | P-MOSFET 20 V 4.2 A SOT-23 (reverse battery) | `DMG2305UX-7` | [Digi-Key DMG2305UX-7DICT-ND](https://www.digikey.com/en/products/result?keywords=DMG2305UX-7DICT-ND) · [datasheet](https://www.diodes.com/assets/Datasheets/DMG2305UX.pdf) | $0.30 | 2026-09-30, 75,458 in stock | Reverse-battery protection (P-FET, gate to GND) |
| R2 | 1 | Yageo resistor 1k 0402 | `RC0402FR-071KL` | [Mouser 603-RC0402FR-071KL](https://www.mouser.com/c/?q=603-RC0402FR-071KL) | $0.10 | typical |  |
| R11, R12 | 2 | Yageo resistor 5.1k 0402 | `RC0402FR-075K1L` | [Mouser 603-RC0402FR-075K1L](https://www.mouser.com/c/?q=603-RC0402FR-075K1L) | $0.10 | typical |  |
| R13, R14 | 2 | Yageo resistor 0R 0402 | `RC0402JR-070RL` | [Mouser 603-RC0402JR-070RL](https://www.mouser.com/c/?q=603-RC0402JR-070RL) | $0.10 | typical | USB D+ link (0R, lets the ESD part sit next to the connector) |
| R15 | 1 | Yageo resistor 2k 0402 | `RC0402FR-072KL` | [Mouser 603-RC0402FR-072KL](https://www.mouser.com/c/?q=603-RC0402FR-072KL) | $0.10 | typical | 500 mA charge current |
| R16, R17 | 2 | Yageo resistor 1M 0402 | `RC0402FR-071ML` | [Mouser 603-RC0402FR-071ML](https://www.mouser.com/c/?q=603-RC0402FR-071ML) | $0.10 | typical | Battery voltage divider |
| R18, R19 | 2 | Yageo resistor 100k 0402 | `RC0402FR-07100KL` | [Mouser 603-RC0402FR-07100KL](https://www.mouser.com/c/?q=603-RC0402FR-07100KL) | $0.10 | typical | USB present detect |
| U5 | 1 | 3.3 V 1 A LDO, SOT-223 | `AP7361C-33E-13` | [Mouser 621-AP7361C-33E-13](https://www.mouser.com/c/?q=621-AP7361C-33E-13) · [datasheet](https://www.diodes.com/assets/Datasheets/AP7361C.pdf) | $0.52 | 2026-09-30, 733 in stock | 1 A LDO (ESP32 Wi-Fi peaks ~500 mA) |
| U6 | 1 | Li-ion charger 4.20 V, SOT-23-5 | `MCP73831T-2ACI/OT` | [Mouser 579-MCP73831T-2ACIOT](https://www.mouser.com/c/?q=579-MCP73831T-2ACIOT) · [datasheet](https://ww1.microchip.com/downloads/en/DeviceDoc/MCP73831-Family-Data-Sheet-DS20001984H.pdf) | $0.76 | 2026-09-30, 116,042 in stock | Li-ion charger, 4.20 V, 500 mA |

## Sensors

| Refs | Qty | Part | MPN | Buy | Price | Checked | Notes |
|---|---|---|---|---|---|---|---|
| R3, R4 | 2 | Yageo resistor 4.7k 0402 | `RC0402FR-074K7L` | [Mouser 603-RC0402FR-074K7L](https://www.mouser.com/c/?q=603-RC0402FR-074K7L) | $0.10 | typical |  |
| U4 | 1 | Lite-On ambient light sensor, I2C | `LTR-303ALS-01` | [Mouser 859-LTR-303ALS-01](https://www.mouser.com/c/?q=859-LTR-303ALS-01) · [datasheet](https://optoelectronics.liteon.com/upload/download/DS86-2013-0004/LTR-303ALS-01_DS_V1.pdf) | $0.68 | 2026-09-30, 29,622 in stock | Ambient light sensor behind the lens window; auto-dims the backlight. I2C 0x29. |
| U8 | 1 | Bosch barometric pressure sensor, LGA-10 2 x 2 mm | `BMP581` | [Digi-Key 828-BMP581CT-ND](https://www.digikey.com/en/products/result?keywords=828-BMP581CT-ND) · [datasheet](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp581-ds004.pdf) | $3.07 | 2026-09-30, 462 in stock | Barometer, I2C 0x46. No vias/traces under it (Bosch). Next to the vent in the right wall. |

## Audio

| Refs | Qty | Part | MPN | Buy | Price | Checked | Notes |
|---|---|---|---|---|---|---|---|
| LS1 | 1 | Same Sky 15 x 11 x 2.5 mm speaker, 8 ohm 0.7 W, IP67, wire leads | `CMS-151125-078L100` | [Mouser 490-CMS151125078L100](https://www.mouser.com/c/?q=490-CMS151125078L100) · [datasheet](https://www.mouser.com/datasheet/3/6118/1/cms-151125-078x-67.pdf) | $2.96 | 2026-09-30, 597 in stock | Pads for the speaker's 32 AWG leads (red = +). |
| R20 | 1 | Yageo resistor 100k 0402 | `RC0402FR-07100KL` | [Mouser 603-RC0402FR-07100KL](https://www.mouser.com/c/?q=603-RC0402FR-07100KL) | $0.10 | typical | Amp off until firmware enables it |
| U7 | 1 | I2S class-D amplifier, TQFN-16 | `MAX98357AETE+T` | [Mouser 700-MAX98357AETE+T](https://www.mouser.com/c/?q=700-MAX98357AETE+T) · [datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/MAX98357A-MAX98357B.pdf) | $4.08 | 2026-09-30, 10,971 in stock | I2S class-D amp, 12 dB (GAIN to GND); SD_MODE high = left channel |

## Keys

| Refs | Qty | Part | MPN | Buy | Price | Checked | Notes |
|---|---|---|---|---|---|---|---|
| R1, R21, R22, R23, R24, R25 | 6 | Yageo resistor 10k 0402 | `RC0402FR-0710KL` | [Mouser 603-RC0402FR-0710KL](https://www.mouser.com/c/?q=603-RC0402FR-0710KL) | $0.10 | typical | Key pull-ups |
| SW1, SW2, SW3 | 3 | C&K top-actuated tact switch 4.2 x 3.2 x 2.5 mm | `PTS810 SJM 250 SMTR LFS` | [Mouser 611-PTS810SJM250SMTR](https://www.mouser.com/c/?q=611-PTS810SJM250SMTR) · [datasheet](https://www.ckswitches.com/media/1476/pts810.pdf) | $0.52 | 2026-09-30, 30,244 in stock | Front soft key (KEY_L). Top-actuated, 2.5 mm tall. Turned 90 deg so the USB-C locating pegs clear its pads. |
| SW4, SW5 | 2 | Alps side-actuated tact switch | `SKRTLAE010` | [Mouser 688-SKRTLA](https://www.mouser.com/c/?q=688-SKRTLA) · [datasheet](https://tech.alpsalpine.com/e/products/detail/SKRTLAE010/) | $0.34 | 2026-09-30, 2,396 in stock | Left side: power / back |

## Capacitors

| Refs | Qty | Part | MPN | Buy | Price | Checked | Notes |
|---|---|---|---|---|---|---|---|
| C1, C12 | 2 | 22 uF 25 V X5R 0805 | `CL21A226MAQNNNE` | [Mouser 187-CL21A226MAQNNNE](https://www.mouser.com/c/?q=187-CL21A226MAQNNNE) | $0.22 | typical |  |
| C2, C5, C7, C8, C10, C13, C17, C19, C20 | 9 | 100 nF 16 V X7R 0402 | `CL05B104KO5NNNC` | [Mouser 187-CL05B104KO5NNNC](https://www.mouser.com/c/?q=187-CL05B104KO5NNNC) | $0.10 | typical |  |
| C3 | 1 | 1 uF 16 V X5R 0402 | `CL05A105KO5NNNC` | [Mouser 187-CL05A105KO5NNNC](https://www.mouser.com/c/?q=187-CL05A105KO5NNNC) | $0.10 | typical | EN reset delay (10k x 1uF) |
| C4, C6, C9, C11, C18 | 5 | 10 uF 10 V X5R 0603 | `CL10A106KP8NNNC` | [Mouser 187-CL10A106KP8NNNC](https://www.mouser.com/c/?q=187-CL10A106KP8NNNC) | $0.12 | typical |  |
| C14, C15, C16 | 3 | 4.7 uF 16 V X5R 0603 | `CL10A475KO8NNNC` | [Mouser 187-CL10A475KO8NNNC](https://www.mouser.com/c/?q=187-CL10A475KO8NNNC) | $0.10 | typical |  |

## Off the board

| Item | Qty | Buy | Price | Notes |
|---|---|---|---|---|
| Newhaven 2.4 in IPS TFT 240 x 320, ST7789, 1200 nit, 40-pin FFC | 1 | [Mouser 763-24240320AFCSXP](https://www.mouser.com/c/?q=763-24240320AFCSXP) · [datasheet](https://newhavendisplay.com/content/specs/NHD-2.4-240320AF-CSXP.pdf) | $15.86 | checked 2026-09-30, 1,032 in stock. Plugs into J3. |
| Adafruit 258 LiPo 1200 mAh 34 x 62 x 5 mm, protected, JST-PH | 1 | Mouser 485-258 | $9.95 | checked 2026-09-30, 388 in stock |
| M2 x 5 mm pan-head screws (stainless) | 4 | any e.g. McMaster 92000A017 | $0.10 | PCB to back shell |
| M2 x 6 mm pan-head screws (stainless) | 4 | any | $0.10 | front bezel to back shell (through the corner posts) |
| 1.0 mm clear acrylic or polycarbonate cover lens, 48.0 x 75.9 mm, 5 mm corner radius | 1 | SendCutSend / Ponoko cad/out/stl/cover_lens.step | $3.00 | black mask: vinyl or paint on the inside, window per cad/out/stl/lens_mask.stl |
| Closed-cell foam tape 0.5 mm, 2 mm strips | 1 | any | $1.00 | display gasket |
| Nitrile O-ring cord 1.2 mm | 1 | any | $1.00 | case seal, ~280 mm length, ends glued |
| Breathable PTFE vent sticker, 3-5 mm | 1 | any e.g. Amazon 'ePTFE vent patch' | $0.50 | over the 0.8 mm barometer vent |
| Acoustic mesh / speaker membrane 12 x 9 mm | 1 | any | $0.50 | under the speaker grille |
| PLA / PETG / TPU filament | 1 | any | $2.00 | ~35 g for a standard case |

## Cost for one unit (parts only)

| Vendor | Subtotal |
|---|---|
| Mouser | $72.95 |
| Digi-Key | $7.62 |
| any | $5.80 |
| SendCutSend / Ponoko | $3.00 |
| **Total** | **$89.37** |

Not included: PCBs (JLCPCB, 5 boards 4-layer 1.0 mm ≈ $15–25 + shipping), stencil (≈ $8), tools (see [instructions/01-order-parts.md](../../instructions/01-order-parts.md)).
