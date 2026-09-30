# Firmware plan (not started)

## Stack

- **nRF Connect SDK (Zephyr)** on the nRF52840: FreeRTOS-like scheduling, BLE stack, drivers.
- **Display:** Zephyr's `ls0xx` Sharp memory-display driver + **LVGL**. Port `viewer/ui/screens.js` screen by screen.
- **Storage:** LittleFS on the 16 MB QSPI flash. Rides as FIT files (Garmin FIT SDK), routes as GPX, map tiles as pre-rendered 1-bit vector/bitmap tiles pushed by the phone app.
- **GPS:** UBX protocol over UART, 1 Hz while riding; u-blox power-save when stopped.
- **Sensors:** BLE heart rate / cycling power / CSC profiles; ANT+ via Nordic's ANT SoftDevice (licence key needed for commercial use).
- **Audio:** I²S to the MAX98357A; short PCM clips in flash for alerts and turn prompts.

## Pin map

Generated: `pcb/pinmap.json` (GPIO → net). Fixed pins: SWDIO/SWDCLK, P0.18 = reset, P1.00 = SWO, USB D+/D−, VBUS.

## Bring-up order

1. nRF52840 DK + Adafruit/SIKTEC Sharp 2.7" breakout: hello world, then the `ride` screen.
2. GPS over UART (breakout), FIT logging to flash.
3. BLE sensors, then ANT+.
4. Custom board: power rails, SWD via Tag-Connect, each peripheral in turn.
