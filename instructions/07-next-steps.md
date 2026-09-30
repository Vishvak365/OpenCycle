# 7 · Next steps

## Firmware (not started — by design)

The owner wants to finish the UI design before firmware work starts. When it does:

- **ESP32-S3:** ESP-IDF + LVGL 9. Display ST7789 over SPI at 40–80 MHz with two PSRAM frame buffers; the UI spec is [`docs/UI.md`](../docs/UI.md) (Lucent) and the reference renderer is `viewer/ui/screens_color.js`. Pin map: [`docs/HARDWARE.md`](../docs/HARDWARE.md).
- **Storage:** FIT files for rides (Garmin FIT SDK), GPX routes, map tiles; LittleFS on the 16 MB flash.
- **GPS:** UBX over UART; power-save / backup mode when stopped.
- **BL652:** Nordic SDK with the ANT+BLE SoftDevice (S332): forwards heart-rate, power, cadence and radar data to the ESP32 over UART. Read the ANT licence terms before publishing firmware.
- **Phone app:** routes, tile generation, ride sync (Web Bluetooth or React Native).

## Hardware follow-ups after the first build

- Measure GPS time-to-fix and C/N0 in the case; BLE/Wi-Fi range with the case closed.
- Measure backlight current and panel temperature at 100 % PWM; adjust the 33 Ω ballasts if needed.
- Check the Garmin mount fit; tweak `cad/params.py`.
- Choose a licence (CERN-OHL-S for hardware + MIT for software is the working plan).

Open questions live in [`docs/DECISIONS.md`](../docs/DECISIONS.md).
