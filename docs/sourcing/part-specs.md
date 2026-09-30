# Part specs

Engineering data for every part considered. Units are mm unless noted. "Verified" / "Library" / "Open" are explained in [README.md](README.md).

---

## Colour build (v0.2)

### ESP32-S3-WROOM-1-N16R8 — main MCU
- Buy: Mouser 356-ESP32S3WRM1N16R8, $6.72, 47,727 in stock (Verified). Digi-Key ~$6.76.
- Size: **25.5 × 18.0 × 3.1**, PCB antenna at one short end (Verified, Mouser).
- Memory: 16 MB quad-SPI flash, 8 MB octal PSRAM. Dual-core LX7 at 240 MHz, 512 KB SRAM.
- Radio: Wi-Fi 802.11 b/g/n, BLE 5.0, 20.5 dBm. **No ANT+.**
- Supply: 3.0–3.6 V; Wi-Fi transmit peaks ~500 mA, so the regulator must handle 1 A.
- Operating temperature −40 to +65 °C (N16R8 variant).
- Interfaces: native USB (flash and debug over USB-C, no programmer needed), SPI, I²C, I²S, UART, PWM.
- Footprint: KiCad `RF_Module:ESP32-S3-WROOM-1`, 62 pads, fab body 18.1 × 25.6 (Library). Keep copper off every layer under the antenna and ≥ 15 mm clear around it where possible; antenna end at a board edge.
- Boot: GPIO0 strap (tie to a side button); EN with 10 k + 1 µF RC.

### Ezurio (Laird) BL652-SA-01-T/R — ANT+ / BLE coprocessor
- Buy: Mouser 239-BL652-SA-01-T/R, $10.40, 5,583 in stock (Verified). Newark $9.46. Digi-Key T/R ~$11.61 (1000 MOQ).
- Chip: Nordic nRF52832 (Mouser lists the part as Bluetooth v4.2; the chip supports BLE 5 with Nordic SoftDevices, including the ANT variants S212/S332).
- Size: fab body 14.1 × 10.1 (Library), integrated antenna, NFC pins.
- Footprint: KiCad `RF_Module:Laird_BL652`, 39 pads (Library).
- Programming: SWD via Tag-Connect pads, or from the ESP32 later.
- Link to ESP32: UART (TX/RX, optional RTS/CTS) plus a reset line.
- Note: ANT SoftDevices need Garmin's ANT+ licence for commercial products; free for development and hobby use.

### u-blox MAX-M10S-00B — GPS
- Buy: Mouser 377-MAX-M10S-00B, $9.12 (2,746 at the second check, 16,866 at the first); Digi-Key 672-MAX-M10S-00B-CT-ND $11.42, 4,987 (Verified). LCSC C4153167.
- Size: 9.7 × 10.1 × ~2.5, LCC-18 (Verified/Library). KiCad `RF_GPS:ublox_MAX`.
- Constellations: GPS, Galileo, BeiDou, GLONASS, QZSS, NavIC. Integrated TCXO, LNA, SAW.
- Pins (KiCad symbol): 1 GND, 2 TXD, 3 RXD, 4 TIMEPULSE, 5 EXTINT, 6 V_BCKP, 7 VCC_IO, 8 VCC, 9 RESET_N, 10 GND, 11 RF_IN, 12 GND, 13 LNA_EN, 14 VCC_RF, 15 VIO_SEL, 16 SDA, 17 SCL, 18 SAFEBOOT_N.
- Power: ~25 mW continuous tracking (u-blox figure); Mouser lists "100 mA" as the maximum operating current.
- RF: 50 Ω RF_IN; for a passive patch, leave VCC_RF and LNA_EN open.

### Taoglas DSGP.1575.15.4.A.02 — GPS patch antenna (SMT)
- Buy: Mouser 960-DSGP157515.4.A02, $7.46, 331 in stock; Digi-Key 931-DSGP.1575.15.4.A.02TR-ND $5.43, 427 (Verified).
- Size **15 × 15 × 4**, 3.3 g, ceramic, passive. GPS L1 / Galileo E1, 1575.42 ± 1.023 MHz.
- Gain 2.6 dBi peak, −1.76 dB average, 67 % efficiency, measured on a **50 × 50 mm ground plane**. Taoglas recommends a symmetric ground plane with the antenna centred.
- Pins: 1 = RF feed, 2–9 = ground (SMT pads).
- **Open:** land-pattern dimensions exist only in the datasheet figures (§8.1 copper keep-out, §8.2 paste, §8.3 solder mask, §8.4 composite). [Datasheet](https://www.taoglas.com/datasheets/DSGP.1575.15.4.A.02.pdf).
- Alternative: Abracon APAE1575R1540AZDB2F-T, pin-fed 15 × 15 × 4, 1.2 dBic, Mouser 815-1575R1540AZDB2FT, $2.11, 1,218 in stock. Its datasheet doesn't give the pin position; a distributor listing mentions an SMA, so confirm the variant before using it.

### Newhaven NHD-2.4-240320AF-CSXP — 2.4" IPS TFT
- Buy: Mouser 763-24240320AFCSXP, **$15.86, 1,032 in stock** (Verified). Digi-Key: 0 in stock ($16.91). Newhaven direct $13.94. Touch variants: resistive -T $20.12, capacitive -CTP $32.08.
- Technology: IPS, transmissive, normally black, anti-glare; 1200 cd/m²; contrast 1500; 80° viewing all round; 262K colours; −20 to +70 °C operating.
- Controller: Sitronix ST7789VI. Interfaces: 8/16-bit 8080 parallel, 3/4-wire SPI.
- Mechanical (Verified, drawing Rev 2B 03/11/2025):
  - Outline 42.80 ± 0.2 × 59.91 ± 0.2 × 2.55 ± 0.2.
  - Bezel opening 38.92 × 51.16 (margins 1.94 sides, 1.92 top). Polariser 38.42 × 50.66 (2.19 / 2.17). Active area 36.72 × 48.96 (3.04 sides, 3.02 top, 7.93 bottom); active-area centre 27.50 below the top edge.
  - SUS304 frame 0.15.
  - FFC exits the bottom edge: EMI-shielded section 39.0 ± 0.2 wide, 13.2 long, then a tail 20.5 ± 0.07 wide. Unfolded, the tail end is 30.0 ± 0.5 below the panel; tail left edge 11.15 ± 0.3 from the outline's left edge (front view).
  - Contacts: 40 × 0.35 ± 0.03 wide at 0.50 ± 0.05 pitch (span 19.50 ± 0.05); pin 1 on the left in front view; PI stiffener 0.30 ± 0.03 on the opposite side; stiffened length ≥ 5.5; R0.3 corners.
  - Folded behind the panel: contact end 27.80 ± 0.3 above the panel's bottom edge; 11.15 ± 0.3 from the rear-view left edge; pin 40 left, pin 1 right; ≤ 0.8 extra thickness behind the panel; bend ~2.43.
- Pinout (Verified): 1 GND · 2–5 NC · 6 SDO · 7 VDD (3.3 V) · 8 VDDI (1.65–3.6 V) · 9 SDA · 10 CSX · 11 DCX/SCL · 12 WRX/DCX · 13 RDX · 14–29 DB0–DB15 · 30 RESX · 31–33 IM0–IM2 · 34–37 LEDK1–4 · 38 LEDA · 39 GND · 40 TE.
- 4-wire SPI: IM0 = 0, IM1 = 1, IM2 = 1.
- Logic supply ~10 mA typ (5–15 mA).
- Backlight: 4 LEDs in parallel, common anode, Vf 2.7 / 3.0 / 3.4 V (min/typ/max), If 160 mA typ, 200 mA max, 50,000 h to half brightness.
- Recommended connector: Molex 54132-4062 (bottom contact).
- [Datasheet](https://newhavendisplay.com/content/specs/NHD-2.4-240320AF-CSXP.pdf) · [Product page](https://newhavendisplay.com/2-4-tft-lcd-ips-high-brightness-display/). The drawing carries Newhaven's "do not reproduce" notice, so only the numbers are transcribed here.

### Hirose FH12-40S-0.5SH(55) — display FFC connector
- Buy: Mouser 798-FH12-40S-0.5SH55, $2.50, 25,967 (Verified). Bottom contact, right angle, ZIF, 0.5 mm pitch, gold, 500 mA, −40 to +85 °C.
- Footprint: KiCad `Connector_FFC-FPC:Hirose_FH12-40S-0.5SH_1x40-1MP_P0.50mm_Horizontal` (Library).
- Newhaven's recommended alternative: Molex 54132-4062, Mouser 538-54132-4062, $2.42, 30,165 in stock, bottom contact (no KiCad footprint).

### Diodes DMG2302UK-7 — backlight switch
- Mouser 621-DMG2302UK-7, $0.39, 238,766 (Verified). N-channel, SOT-23, 20 V, 2.8 A, 90 mΩ, Vgs(th) 0.3 V, 660 mW.
- Circuit: LEDA from 3.3 V (or VBAT); each LEDKx through its own ballast resistor to the drain; PWM on the gate from the ESP32 (LEDC peripheral).

### Lite-On LTR-303ALS-01 — ambient light sensor
- Mouser 859-LTR-303ALS-01, $0.68, 29,622 (Verified). I²C, 0.01–64k lux, 50/60 Hz flicker rejection, −30 to +70 °C.
- Footprint: KiCad `OptoDevice:Lite-On_LTR-303ALS-01` (Library), 2 × 2 ChipLED-6. Needs a clear window in the lens mask.

### Bosch BMP581 — barometer
- Buy: **Digi-Key 828-BMP581CT-ND, $3.07, 462** (Verified). Mouser 262-BMP581: 0 in stock, 159,933 on order.
- Package: 10-pin metal-lid LGA, 2.0 × 2.0 (1.9–2.1), height 0.75 typ (0.7–0.8) (Verified, datasheet).
- Pins (Verified): 1 VDDIO · 2 SDI · 3 SDO (I²C address select) · 4 CSB · 5 GND · 6 VDD · 7 SCK · 8 INT · 9 GND · 10 VDDIO.
- Supply: VDD 1.71–3.6 V, VDDIO 1.08–3.6 V. I²C address 0x46 (SDO = 0) or 0x47 (SDO = 1); SPI up to 12 MHz; I3C.
- Land pattern (from SparkFun's production BMP581 board, Eagle package "BMP581"): pads 0.275 × 0.25; side columns at x = ±0.7625 with y = −0.5 / 0 / +0.5; top/bottom rows at y = ±0.7625 with x = ±0.25 (pads rotated 0.25 × 0.275). Silk box 2.2 × 2.2. **Check SparkFun's pad numbering against Bosch's pin 1 before use.**
- Needs a vent to outside air: a hole in the case with a breathable membrane.

### Analog Devices / Maxim MAX98357AETE+T — I²S class-D amp
- Mouser 700-MAX98357AETE+T, $4.08, 10,971 (Verified; Mouser says it will stop carrying it). Digi-Key MAX98357AETE+TCT-ND $3.73, 30,936. LCSC C910544.
- TQFN-16 3 × 3, EP. 2.5–5.5 V supply (run from VBAT). 3.2 W into 4 Ω; ~1 W into 8 Ω at 3.7 V. THD+N 0.013 %.
- Pins (KiCad symbol): 1 DIN · 2 GAIN_SLOT · 3 GND · 4 SD_MODE · 7/8 VDD · 9 OUTP · 10 OUTN · 11/15 GND · 14 LRCLK · 16 BCLK · 17 EP (GND) · 5/6/12/13 NC.
- Gain: GAIN_SLOT to GND = 12 dB, to VDD = 6 dB, open = 9 dB, 100 k to GND = 15 dB, 100 k to VDD = 3 dB. SD_MODE high = left channel; low = shutdown.

### Same Sky CMS-151125-078L100 — speaker
- Mouser 490-CMS151125078L100, $2.96, 597 (Verified). Variants: -078S-67 spring contacts $2.25 (890); -078SP-67 solder pads $2.99 (1,392); -078L100A-67 wire + Molex 51021 $3.15 (796).
- **15 × 11 × 2.5**, 8 Ω, 0.7 W rated / 1.0 W max, 88–94 dB SPL (91 typ), resonance 800–1,200 Hz in a 1 cc enclosure, 100 Hz–20 kHz, IP67 front, PEEK cone, NdFeB magnet (Verified, datasheet).
- Polarity: cone moves forward with positive DC on "+".
- L100 = 32 AWG UL1571 wire leads, no connector. [Datasheet](https://www.mouser.com/datasheet/3/6118/1/cms-151125-078x-67.pdf).

### Microchip MCP73831T-2ACI/OT — charger
- Mouser 579-MCP73831T-2ACIOT, $0.76, 116,042 (Verified). LCSC C424093. SOT-23-5, 4.20 V, 15–500 mA set by R_PROG (2 kΩ → 500 mA), 3.75–6 V input.

### Diodes AP7361C-33ER-13 — 3.3 V LDO
- Mouser 621-AP7361C-33ER-13, $0.50, 14,945 (Verified). 1 A, SOT-223R-3 (~6.5 × 7 × 1.8).
- Chosen because TI TLV75733PDBVR (1 A, SOT-23-5, 25 µA Iq, $0.36) had 0 stock until Dec 2026.

### GCT USB4105-GF-A — USB-C receptacle
- Mouser 640-USB4105-GF-A, $0.80, 420,427; Digi-Key 2073-USB4105-GF-ADKR-ND $0.80, 121,048 (Verified). USB 2.0, 16 contacts, top mount, right angle, 5 A.
- Footprint: KiCad `Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal` (Library).

### ST USBLC6-2SC6 — USB ESD
- Mouser 511-USBLC6-2SC6, $0.49, 81,014 (Verified). LCSC C7519. SOT-23-6, 5.25 V working, 3.5 pF, 15 kV.

### Alps SKRTLAE010 — side buttons
- Mouser 688-SKRTLA, $0.34, 2,396; Digi-Key ~$0.34, 432 (Verified). LCSC C110293.
- **4.5 × 3.55 × 3.3**, 1.6 N (160 gf), 100k cycles, −20 to +70 °C, guide bosses (NPTH pegs). Footprint: KiCad `Button_Switch_SMD:SW_Push_1P1T-MP_NO_Horizontal_Alps_SKRTLAE010` (Library). Its pegs sit 0.1 from its own pads, which triggers a hole-clearance DRC warning.

### Adafruit 258 — LiPo battery
- Mouser 485-258, $9.95, 388 (Verified). **34 × 62 × 5, 1200 mAh**, 23 g, 3.7 V nominal, JST-PH 2-pin, protection circuit (over-charge, over-discharge at 3.0 V, short). Charge at ≤ 500 mA (Verified, Adafruit).
- Other Mouser cells: TinyCircuits ASR00012 1000 mAh $9.95; TinyCircuits ASR00036 850 mAh $8.49; Adafruit 328 2500 mAh $14.95.

### JST S2B-PH-SM4-TB(LF)(SN) — battery connector
- Mouser 306-S2BPHSM4TBLFSN, $0.49, **269** (Verified). Matches the Adafruit JST-PH lead. KiCad `Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal`.
- **Check polarity:** Adafruit's JST-PH pinout differs from some other vendors' batteries.

### Lite-On LTST-C191KGKT — LED
- Mouser 859-LTST-C191KGKT, $0.15, 1.19 M (Verified). 0603, green 571 nm, 2 V, 20 mA, 35 mcd.

---

## Mono build (v0.1) parts not reused

| Part | Data |
|---|---|
| Sharp LS027B7DH01A | 2.7" 400 × 240 memory LCD, 1-bit. Pins 1 SCLK, 2 SI, 3 SCS, 4 EXTCOMIN, 5 DISP, 6 VDDA, 7 VDD, 8 EXTMODE, 9 VSS, 10 VSSA (Verified). 5 V panel (VDD/VDDA). Module ~62.8 × 42.82 × 1.6. Hirose FH12-10S-0.5SH connector. |
| Raytac MDBT50Q-1MV2 | nRF52840 module, 10 × 15.5 × 2.05, KiCad `RF_Module:Raytac_MDBT50Q`, 61 pads. SparkFun WRL-21605 $8.95; TME $6.92–9.45; not stocked at Digi-Key/Mouser. |
| Winbond W25Q128JVSIQ | 16 MB NOR, SOIC-8 208 mil. Digi-Key $2.88 (85,500); Mouser $3.94. LCSC C97521. |
| TI TPS61220DCKR | Adjustable boost, SC-70-6. LCSC C15421. Vout = 0.5 × (1 + R1/R2). |
| TI SN74LV1T34DCKR | Single buffer with TTL-level inputs (3.3 → 5 V), SC-70-5. LCSC C78541. |
| Torex XC6220B331MR-G | 700 mA LDO, 8 µA Iq, SOT-23-5. LCSC C86534. |
| Sunlord SWPA3012S4R7MT | 4.7 µH, 3 × 3 × 1.2. LCSC C83415. |
| ST LIS3DHTR | Accelerometer, LGA-16 3 × 3. Mouser $1.94 (150, then 0); Digi-Key 0. |
| Bosch BMP280 | Barometer, LGA-8 2 × 2.5. LCSC C83291; Digi-Key 0 stock / 10k MOQ. |
| Ole Wolff OWS-111535W50A-8 | 11 × 15 × 3.5 speaker, 8 Ω 1 W, 100 Hz–20 kHz, Digi-Key (price not shown). |
| Jauch LP603048JK+PCM / LP103048JU+PCM | 6 × 30 × 48 (~850 mAh) / 10 × 30 × 48 (~1500 mAh) LiPo with protection and wires, Digi-Key. |

## Open items
1. Taoglas land pattern: needs the §8.4 composite figure.
2. BMP581 pad numbering vs. Bosch pin 1: confirm the SparkFun package orientation.
3. BL652 ANT SoftDevice: confirm S212/S332 support on the BL652 (flash size 512 KB), plus licensing.
