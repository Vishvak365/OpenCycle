# Hardware (board v0.2, colour build)

Source of truth: [`pcb/design.py`](../pcb/design.py). Schematic: [`pcb/fab/opencycle_schematic.pdf`](../pcb/fab/opencycle_schematic.pdf) (generated from the same table, netlist-checked against the board). Prices, links and stock: [`sourcing/bom-v0.2.md`](sourcing/bom-v0.2.md).

## Block diagram

```
USB-C ─ ESD ─┬─ VBUS ── MCP73831 charger ──┐                  ┌─ AP7361C 3.3 V LDO ── +3V3 plane ─┐
             │                              ├── VBAT ─────────┼─ MAX98357A amp ── speaker          │
             └─ D+/D- (0R) ─ ESP32 USB      │                 └─ TFT backlight (4 × 33 R, PWM FET)  │
JST-PH ─ BATT+ ─ P-FET (reverse-battery) ───┘                                                      │
                                                                                                   │
   ┌──────────────── ESP32-S3-WROOM-1-N16R8 (UI, logging, Wi-Fi, BLE, USB) ◄──────────────────────┘
   │  SPI  ──► Newhaven 2.4" IPS TFT (ST7789, 240 × 320) via 40-pin FFC
   │  UART ──► u-blox MAX-M10S GPS ◄── 12 mm Taoglas patch
   │  UART ──► BL652 (nRF52832): ANT+ and BLE sensor bridge   [SWD on Tag-Connect J4]
   │  I²C  ──► BMP581 barometer, LTR-303 ambient light
   │  I²S  ──► MAX98357A class-D amp
   │  GPIO ◄── 3 front soft keys + 2 side buttons, battery / USB sense (ADC)
```

## Parts and why

| Ref | Part | Job | Why this one |
|---|---|---|---|
| U1 | Espressif ESP32-S3-WROOM-1-N16R8 | Main MCU: UI (LVGL), logging, Wi-Fi sync, BLE, native USB | Enough RAM (8 MB PSRAM) for two 150 KB frame buffers and map tiles; USB flashing without a programmer. Antenna at the right board edge. |
| U2 | Ezurio BL652-SA (nRF52832) | ANT+ and BLE sensor bridge | The ESP32 has no ANT+. Pre-certified module with integrated antenna at the left edge. |
| U3 | u-blox MAX-M10S | GPS / Galileo / BeiDou / GLONASS | Lowest-power receiver in its class (~25 mW tracking). |
| AE1 | Taoglas DSGP.1575.12.4.A.02 | 12 × 12 mm ceramic GPS patch | Best reception that fits the 15.6 mm top band; land pattern from the Taoglas datasheet. |
| J3 | Hirose FH12-40S-0.5SH(55) | 40-pin FFC connector for the display | Bottom contact, matches the Newhaven tail after it folds behind the panel. |
| — | Newhaven NHD-2.4-240320AF-CSXP | 2.4" IPS TFT 240 × 320, 1200 nit | In stock at Mouser, datasheet with full drawing; readable in daylight at full backlight. |
| Q1, R5–R10 | DMG2302UK + 4 × 33 Ω (0603) | Backlight PWM | LEDA from VBAT: ≤ 45 mA per LED even at 4.2 V with the lowest Vf (datasheet max 50 mA per LED / 200 mA total); ~21 mA typ. at 3.7 V. |
| U4 | Lite-On LTR-303ALS | Ambient light → auto backlight | Biggest lever on battery life with a TFT. Sits under a clear window in the lens mask. |
| U8 | Bosch BMP581 | Barometer: altitude, climb | Best-in-class noise; the only well-stocked option (Digi-Key). Next to the case vent. |
| U7 | MAX98357A | I²S class-D amp | Real sampled audio (alerts, turn prompts). |
| LS1 | Same Sky CMS-151125-078L100 | 15 × 11 mm IP67 speaker | Fires through the back-shell grille. |
| U6 | MCP73831-2 | Li-ion charger, 500 mA (R15 = 2 k) | Simple, proven. |
| U5 | Diodes AP7361C-33E (SOT-223) | 3.3 V, 1 A LDO | ESP32 Wi-Fi peaks ~500 mA. Note: the "E" (not "ER") package, pin 1 IN / 2 GND / 3 OUT. |
| Q2 | DMG2305UX | Reverse-battery protection | P-FET, gate to ground: a reversed cell can't damage the board. |
| J1, D2 | GCT USB4105 + USBLC6-2SC6 | USB-C with ESD | 5.1 k CC pull-downs for 5 V from any USB-C charger. |
| J2 | JST S2B-PH-SM4-TB | Battery socket | Matches the Adafruit 258 cell's JST-PH plug. Pin 1 −, pin 2 +. |
| SW1–SW3 | C&K PTS810 (2.5 mm) | Front soft keys | Top-actuated; the display draws their labels. |
| SW4, SW5 | Alps SKRTLAE010 | Side buttons (power/back, menu) | Side-actuated, sits behind the wall plungers. |
| J4, J5 | Tag-Connect TC2030-NL pads | BL652 SWD / ESP32 recovery UART | Nothing to assemble; one cable for all boards. |

## ESP32-S3 pin map

| GPIO | Net | Notes |
|---|---|---|
| IO0 | KEY_L | Strapping pin: hold the left key while resetting = download mode |
| IO1 / IO2 | VBAT_SENSE / VBUS_SENSE | ADC1 (1 M/1 M and 100 k/100 k dividers) |
| IO3 | AMP_EN | Strapping pin (JTAG source, only with eFuse); 100 k pull-down keeps the amp off at boot |
| IO4 / IO5 | KEY_C / KEY_R | RTC GPIOs: can wake from deep sleep |
| IO6 / IO7 | BTN_PWR / BTN_MENU | RTC GPIOs |
| IO8 / IO18 | I2C_SDA / I2C_SCL | 4.7 k pull-ups; BMP581 0x46, LTR-303 0x29 |
| IO9–IO14 | LCD_DC, CS, MOSI, SCK, TE, RST | IO10–IO12 are the FSPI IO_MUX pins (fast SPI) |
| IO21 | LCD_BL | Backlight PWM (LEDC) |
| IO15–IO17 | I2S_BCLK, LRCLK, DIN | |
| IO19 / IO20 | USB D− / D+ | Native USB (serial/JTAG + flashing) |
| IO38 / IO39 / IO40 / IO48 | GPS_TX (in) / GPS_RX (out) / GPS_RST / GPS_EXTINT | |
| IO41 / IO42 / IO47 | BLE_TX (in) / BLE_RX (out) / BLE_RST | BL652 UART on SIO_06 / SIO_08, reset on SIO_21 |
| TXD0 / RXD0 / EN | Console / reset | On Tag-Connect J5 for recovery |
| IO35–IO37 | — | Used by the octal PSRAM on the N16R8, not available |
| IO45 / IO46 | — | Strapping pins, left at their default pull-downs |

## Power budget (estimate, riding)

| Load | Avg current |
|---|---|
| GPS continuous tracking | 7–8 mA |
| ESP32-S3 (UI, BLE, logging; Wi-Fi only to sync) | 15–25 mA |
| BL652 ANT+/BLE sensors | 1–2 mA |
| TFT logic | ~10 mA |
| Backlight (auto-dimmed) | 20–85 mA (≤ 180 mA at 100 % PWM on a full battery) |
| **Total** | **~55–130 mA** |

With the 1200 mAh cell: **~10–22 h**. Sleep: ESP32 deep sleep + GPS backup mode + BL652 System OFF, in the tens of µA (plus the LDO's quiescent current). Details: [`sourcing/power-budget.md`](sourcing/power-budget.md).

## Things a reviewer should look at first

1. RF: the ESP32 and BL652 antennas are at the board edges with keep-outs, but the case walls and battery are close; the GPS patch ground is smaller than Taoglas's 50 × 50 mm test board. Nothing is measured yet.
2. Battery polarity at J2 (see [`instructions/05-bring-up.md`](../instructions/05-bring-up.md)); Q2 protects the board either way.
3. Backlight current: firmware should cap the PWM duty on a full battery if the panel gets warm.
4. The BMP581 INT pin is tied to ground (Bosch-recommended when unused): firmware must keep `INT_CONFIG.int_en = 0`.
