# Firmware plan (not started)

The owner is finishing the UI design first; nothing here is implemented yet.

## Stack

- **ESP32-S3 (main MCU):** ESP-IDF (FreeRTOS) + **LVGL 9**. ST7789 over SPI (FSPI IO_MUX pins, 40–80 MHz), two 150 KB frame buffers in PSRAM, partial refresh. Port `viewer/ui/screens_color.js` screen by screen following `docs/UI.md` (Lucent).
- **Storage:** LittleFS on the module's 16 MB flash (app partitions + data). Rides as FIT (Garmin FIT SDK), routes as GPX, map tiles pre-rendered by the phone app.
- **GPS (MAX-M10S):** UBX over UART (IO38 RX / IO39 TX), 1 Hz while riding; software backup when stopped; EXTINT on IO48 to wake it.
- **ANT+ / BLE sensors:** the **BL652 (nRF52832)** runs Nordic's SoftDevice S332 (ANT + BLE) as a sensor bridge and streams parsed data (HR, power, cadence, speed, radar) to the ESP32 over UART (IO41 RX / IO42 TX, reset IO47). Programmed over SWD through Tag-Connect J4. ANT licence terms must be checked before publishing.
- **BLE to the phone + Wi-Fi sync:** ESP32 native radios.
- **Sensors:** BMP581 (I²C 0x46, keep INT disabled — the pin is grounded) for altitude/climb; LTR-303 (0x29) for backlight auto-dimming.
- **Audio:** I²S (IO15/16/17) to the MAX98357A, amp enable on IO3; short PCM clips for alerts and turn prompts.
- **Keys:** five inputs with 10 k pull-ups; RTC-capable GPIOs so any key can wake from deep sleep. Holding the left key (IO0) at reset enters the ROM bootloader.
- **Power:** VBAT_SENSE (IO1, ÷2) and VBUS_SENSE (IO2, ÷2) on ADC1; backlight PWM on IO21 with a duty cap from VBAT_SENSE.

Full pin map: [`HARDWARE.md`](HARDWARE.md#esp32-s3-pin-map).

## Bring-up order

Follow [`instructions/05-bring-up.md`](../instructions/05-bring-up.md): rails → ESP32 over USB → I²C scan → display → GPS NMEA → BL652 over SWD → audio → keys → charging.
