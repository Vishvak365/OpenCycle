# 5 · Bring-up (first power-on)

Do these in order and stop at the first failure. Numbers are what the design expects; small deviations are fine.

## Before any power

1. Visual inspection under magnification, both sides.
2. Resistance to GND (meter, board unpowered): **VBAT** (C16), **+3V3** (C12), **VBUS** (C14) — each should read more than ~1 kΩ after the caps charge. A few ohms = short; find it before continuing.
3. **Battery polarity:** with the meter on the Adafruit 258 plug, find the red (+) lead. Compare with J2: **pin 2 = +, pin 1 = −** (see `assembly_back.pdf`). If the cable is the other way round, move the two crimp pins in the JST housing (lift the latch tabs) rather than forcing it. Q2 protects the board if you get it wrong, but check anyway.

## Power from a bench supply (no battery yet)

4. Supply **3.7 V, 100 mA current limit** into J2 (+ on pin 2). Expect < 60 mA once the ESP32 idles. +3V3 must read 3.30 V ± 2 % at C12. VBAT at C16 reads the supply voltage (Q2 conducting).
5. **Do not plug in USB-C while the bench supply is connected**: the charger would try to charge the supply. The board has no USB-to-system power path — it always runs from VBAT (battery), and USB only charges the battery and carries data.
6. Disconnect the supply and connect the real battery (polarity checked in step 3). Current draw at idle matches step 4.

## ESP32

7. Connect USB-C to a computer (battery connected): a new USB device `303a:1001` (Espressif USB JTAG/serial) appears.
8. `esptool.py --chip esp32s3 flash_id` → reports a 16 MB flash; `esptool.py chip_id` works. If the chip does not show up: hold the **left front key** (IO0) while re-applying power to force download mode.
9. Flash a test build that: prints over USB serial, toggles `LCD_BL` (IO21), scans I²C (IO8/IO18) → expect **0x29** (LTR-303) and **0x46** (BMP581).

## Display

10. Plug the display FFC into J3 (contacts facing the board, latch closed), init the ST7789 in 4-wire SPI (SCK IO12, MOSI IO11, CS IO10, DC IO9, RST IO14), draw colour bars. Raise the backlight PWM slowly and check the panel stays cool at 100 %.

## GPS

11. Open UART on IO38 (RX) / IO39 (TX) at 9600 baud: NMEA sentences appear within a second of power-up. Outdoors with a clear sky: a 3D fix within ~30–60 s cold.

## BL652 (ANT+/BLE)

12. Connect the Tag-Connect TC2030-NL cable to **J4** and a SWD probe. `nrfjprog --readregs` (or pyOCD) must find an nRF52832. Flash a UART echo test; check it answers the ESP32 on IO41/IO42.

## Audio, keys, charging

13. Enable the amp (IO3 high) and play a 1 kHz tone over I²S (IO15/16/17) → speaker plays.
14. Each key pulls its GPIO low: KEY_L IO0, KEY_C IO4, KEY_R IO5, BTN_PWR IO6, BTN_MENU IO7.
15. With USB-C plugged in and the battery not full: the charge LED lights; battery current ≈ 500 mA while charging (CC phase); VBAT_SENSE (IO1) reads about half the battery voltage.

Write down anything that deviates in an issue or in `docs/DECISIONS.md`.
