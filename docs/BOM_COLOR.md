# Colour-display build — sourced BOM (v0.2 candidate)

Checked 2026-09-30. Prices are qty-1 USD; stock changes daily. **Two sites: Mouser (everything but one part) + Digi-Key (barometer).**

Architecture: ESP32-S3 (Wi-Fi + BLE, UI, logging) + nRF52832 module as ANT+/BLE sensor coprocessor over UART + u-blox M10 GPS + 2.4" 240×320 IPS TFT (1200 nit).

## Parts

| Ref | Part (MPN) | Job | Buy | Price | Stock | Key specs for layout (source) |
|---|---|---|---|---|---|---|
| U1 | Espressif **ESP32-S3-WROOM-1-N16R8** | Main MCU, Wi-Fi, BLE, USB | [Mouser 356-ESP32S3WRM1N16R8](https://www.mouser.com/c/?q=ESP32-S3-WROOM-1-N16R8) | $6.72 | 47,727 | 25.5 × 18 × 3.1 mm, PCB antenna at the short end, 16 MB flash + 8 MB PSRAM. KiCad `RF_Module:ESP32-S3-WROOM-1`. |
| U2 | Ezurio **BL652-SA-01-T/R** | nRF52832: ANT+ and BLE sensors | [Mouser 239-BL652-SA-01-T/R](https://www.mouser.com/c/?q=BL652-SA-01) | $10.40 | 5,583 | 14 × 10 mm body, integrated antenna. KiCad `RF_Module:Laird_BL652` (39 pads). Program via SWD (Tag-Connect pads). |
| U3 | u-blox **MAX-M10S-00B** | GPS | [Mouser 377-MAX-M10S-00B](https://www.mouser.com/c/?q=MAX-M10S-00B) | $9.12 | 2,746 | 9.7 × 10.1 × 2.5 mm LCC-18. KiCad `RF_GPS:ublox_MAX`. |
| AE1 | Taoglas **DSGP.1575.15.4.A.02** | GPS patch antenna | [Mouser 960-DSGP157515.4.A02](https://www.mouser.com/c/?q=DSGP.1575.15.4.A.02) | $7.46 | 331 | 15 × 15 × 4 mm, SMT: pin 1 RF feed, pins 2–9 ground; tested on a 50 × 50 mm ground plane; place centred on ground. |
| LCD | Newhaven **NHD-2.4-240320AF-CSXP** | 2.4" IPS TFT 240×320, ST7789VI | [Mouser 763-24240320AFCSXP](https://www.mouser.com/c/?q=NHD-2.4-240320AF-CSXP) | $15.86 | 1,032 | Outline 42.80 × 59.91 × 2.55 mm; LCD active area 36.72 wide (38.42 polariser, 38.92 bezel opening). 40-pin 0.5 mm FFC (**bottom contact**), 4-wire SPI with IM2..IM0 = 1,1,0. Logic 3.3 V ~10 mA. Backlight: 4 LED cathodes + 1 anode, 3.0 V typ, 160 mA for 1200 cd/m². ([datasheet](https://newhavendisplay.com/content/specs/NHD-2.4-240320AF-CSXP.pdf)) |
| J3 | Hirose **FH12-40S-0.5SH(55)** | Display FFC connector, 40 pos, bottom contact | [Mouser 798-FH12-40S-0.5SH55](https://www.mouser.com/c/?q=FH12-40S-0.5SH(55)) | $2.50 | 25,967 | KiCad `Connector_FFC-FPC:Hirose_FH12-40S-0.5SH_1x40-1MP_P0.50mm_Horizontal`. (Newhaven suggests Molex 54132-4062, also bottom contact, Mouser 538-54132-4062, $2.42.) |
| Q1 | Diodes **DMG2302UK-7** | Backlight PWM switch (low side) | [Mouser 621-DMG2302UK-7](https://www.mouser.com/c/?q=DMG2302UK-7) | $0.39 | 238,766 | SOT-23, 20 V, 2.8 A, Vgs(th) 0.3 V. Plus 4 ballast resistors, one per cathode. |
| U4 | Lite-On **LTR-303ALS-01** | Ambient light: auto-dims the backlight | [Mouser 859-LTR-303ALS-01](https://www.mouser.com/c/?q=LTR-303ALS-01) | $0.68 | 29,622 | 2 × 2 mm ChipLED-6, I²C. KiCad `OptoDevice:Lite-On_LTR-303ALS-01`. Needs a window in the lens mask. |
| U5 | Bosch **BMP581** | Barometer (altitude, climb) | [Digi-Key 828-BMP581CT-ND](https://www.digikey.com/en/products/result?keywords=BMP581) | $3.07 | 462 | LGA-10, 2.0 × 2.0 × 0.75 mm. Land pattern from SparkFun's production board: pads 0.275 × 0.25 mm at ±0.7625 mm / 0.5 mm pitch. I²C 0x46/0x47 by SDO. (Mouser: 0 stock.) |
| ~~U6~~ | ~~Bosch BMA400~~ (dropped for v0.2) | Accelerometer, wake on motion | [Mouser 262-BMA400](https://www.mouser.com/c/?q=BMA400) | $2.21 | 104,096 | LGA-12, 2 × 2 × 0.95 mm. **Pin table still to transcribe from datasheet §7.** Can be dropped (power button covers wake). |
| U7 | Analog Devices **MAX98357AETE+T** | I²S class-D amp | [Mouser 700-MAX98357AETE+T](https://www.mouser.com/c/?q=MAX98357AETE%2BT) | $4.08 | 10,971 | TQFN-16 3 × 3 mm. Mouser flags it as being phased out of their catalogue; Digi-Key also stocks it. |
| LS1 | Same Sky **CMS-151125-078L100** | Speaker, 8 Ω 0.7 W, IP67 | [Mouser 490-CMS151125078L100](https://www.mouser.com/c/?q=CMS-151125-078L100) | $2.96 | 597 | 15 × 11 × 2.5 mm, 32 AWG wire leads, 91 dBA, resonance ~1 kHz in 1 cc. ([datasheet](https://www.mouser.com/datasheet/3/6118/1/cms-151125-078x-67.pdf)) |
| U8 | Microchip **MCP73831T-2ACI/OT** | Li-ion charger, 500 mA | [Mouser 579-MCP73831T-2ACIOT](https://www.mouser.com/c/?q=MCP73831T-2ACI%2FOT) | $0.76 | 116,042 | SOT-23-5. |
| U9 | Diodes **AP7361C-33ER-13** | 3.3 V LDO, 1 A (ESP32 Wi-Fi peaks) | [Mouser 621-AP7361C-33ER-13](https://www.mouser.com/c/?q=AP7361C-33ER-13) | $0.50 | 14,945 | SOT-223R-3 (6.5 × 7 × 1.8 mm). (TI TLV75733 was out of stock.) |
| J1 | GCT **USB4105-GF-A** | USB-C (charging + ESP32 native USB for flashing) | [Mouser 640-USB4105-GF-A](https://www.mouser.com/c/?q=USB4105-GF-A) | $0.80 | 420,427 | KiCad `Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal`. |
| D1 | ST **USBLC6-2SC6** | USB ESD | [Mouser 511-USBLC6-2SC6](https://www.mouser.com/c/?q=USBLC6-2SC6) | $0.49 | 81,014 | SOT-23-6. |
| SW1–3 | Alps **SKRTLAE010** | Side buttons | [Mouser 688-SKRTLA](https://www.mouser.com/c/?q=SKRTLAE010) | $0.34 | 2,396 | 4.5 × 3.55 × 3.3 mm, 1.6 N. KiCad footprint exists. |
| BT1 | Adafruit **258** LiPo 1200 mAh | Battery (protected) | [Mouser 485-258](https://www.mouser.com/c/?q=adafruit%20258) | $9.95 | 388 | 34 × 62 × 5 mm, 23 g, JST-PH 2-pin, protection cuts at 3.0 V ([Adafruit spec](https://www.adafruit.com/product/258)). |
| J2 | JST **S2B-PH-SM4-TB(LF)(SN)** | Battery connector (matches Adafruit JST-PH) | [Mouser 306-S2BPHSM4TBLFSN](https://www.mouser.com/c/?q=S2B-PH-SM4-TB) | $0.49 | 269 | KiCad `Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal`. |
| D2 | Lite-On **LTST-C191KGKT** | Charge LED | [Mouser 859-LTST-C191KGKT](https://www.mouser.com/c/?q=LTST-C191KGKT) | $0.15 | 1.19 M | 0603. |
| — | Passives (Samsung CL05/CL10, Yageo RC0402) | Decoupling, pull-ups, dividers | Mouser | ~$3 total | stock | Standard 0402/0603; exact MPN list generated with the schematic. |

**Removed from the mono design:** nRF52840 module, 16 MB external flash (ESP32 module has it), 5 V boost + inductor, five level shifters, Sharp LCD and its FPC connector.

## Rough cost

~$85–90 per unit in parts (qty 1), before PCB and case. Parts-only, that's about the same as the mono build; the colour display is cheaper than the Sharp, but the ANT+ coprocessor and bigger MCU add it back.

## Battery life estimate (colour)

| Load | Avg current |
|---|---|
| GPS | 7–8 mA |
| ESP32-S3 (BLE, UI, logging; Wi-Fi only for sync) | 15–25 mA |
| BL652 ANT+/BLE sensors | 1–2 mA |
| TFT logic | ~10 mA (datasheet typ.) |
| Backlight, auto-dimmed by the light sensor | 20–80 mA (160 mA at full 1200 nit) |
| **Total** | **~55–125 mA** |

With the 1200 mAh cell that's **~10–22 h**. Garmin-class numbers need a transflective panel or aggressive dimming.

## Fit notes for the PCB redesign

- The ESP32-S3 module (25.5 × 18 × 3.1) is the largest part. With the 5 mm Adafruit cell, back-side parts up to ~3.3 mm can sit *over* the battery (1.5 floor + 5.0 cell + 0.3 gap + 3.1 module ≈ PCB at z 10), so the stack still works.
- The display is 2.55 mm thick vs. 1.7 mm for the Sharp: the body grows ~0.9 mm (16 → ~17 mm).
- The outline (42.8 × 59.91) fits the existing display pocket width; height is 3 mm shorter.
- The ESP32 antenna end and the BL652 antenna need board-edge placement with copper keep-outs, well away from the GPS patch.

## Display mechanical data (Newhaven drawing Rev 2B, 03/11/2025)

All mm, tolerance ±0.3 unless noted. "Front view" = looking at the screen.

| Feature | Value |
|---|---|
| Outline | 42.80 ± 0.2 wide × 59.91 ± 0.2 tall × 2.55 ± 0.2 thick |
| Bezel opening | 38.92 × 51.16; margins 1.94 left/right, 1.92 top |
| Polariser | 38.42 × 50.66; margins 2.19 left/right, 2.17 top |
| Active area | 36.72 × 48.96; margins 3.04 left/right, 3.02 top, 7.93 bottom; AA centre 27.50 below the top edge |
| Frame | SUS304 stainless, 0.15 mm |
| FFC exit | Bottom edge. EMI-shielded section 39.0 ± 0.2 wide, 13.2 long; then the tail narrows to 20.5 ± 0.07 wide |
| FFC tail position (unfolded, front view) | Tail left edge 11.15 ± 0.3 from the outline's left edge; tail end 30.0 ± 0.5 below the panel's bottom edge |
| Contacts | 40 fingers, 0.50 ± 0.05 pitch, 0.35 ± 0.03 wide, span 19.50 ± 0.05; pin 1 at the **left** in front view; stiffener (PI) 0.30 ± 0.03 thick on the side opposite the contacts; stiffened length ≥ 5.5; 2 × R0.3 corners |
| Folded behind the panel (rear view) | Contacts end 27.80 ± 0.3 above the panel's bottom edge; tail 11.15 ± 0.3 from the rear-view left edge; pin 40 at the left, pin 1 at the right; fold adds ≤ 0.8 behind the panel; bend radius ~(2.43) |
| Backlight | 4 LEDs in parallel (LEDK1–4 cathodes, common LEDA anode), 3.0 V typ, 160 mA total |

Pinout (pin: signal): 1 GND · 2–5 NC (touch, unused) · 6 SDO · 7 VDD · 8 VDDI · 9 SDA · 10 CSX · 11 DCX · 12 WRX · 13 RDX · 14–29 DB0–DB15 · 30 RESX · 31–33 IM0–IM2 · 34–37 LEDK1–4 · 38 LEDA · 39 GND · 40 TE.
4-wire SPI: IM2..IM0 = 1,1,0. Unused DB0–DB15 are tied to GND per the ST7789 datasheet.

Layout consequence: with the FFC folded behind the display, the bottom-contact FH12-40S goes on the PCB front face, oriented so the cable enters from the bottom edge of the device. Its contact row sits ~27.8 mm above the display's bottom edge, 11.15 mm in from the right edge when viewed from the front.

## Still to confirm before layout

1. ~~Display FFC tail~~ — done (table above).
2. **Accelerometer:** dropping the BMA400 for v0.2. The power button handles wake, and it removes a part whose pinout we haven't verified.
3. **Taoglas patch land pattern:** the pad sizes are only in the datasheet's figures (§8.1–8.4 of the [Taoglas datasheet](https://www.taoglas.com/datasheets/DSGP.1575.15.4.A.02.pdf)), not in its text. Needs a screenshot of the composite footprint diagram.
