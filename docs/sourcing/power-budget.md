# Power budget

Estimates from datasheets and typical figures; replace with measurements once hardware exists.

## Mono build (nRF52840 + Sharp memory LCD)

| Load | Avg current while riding |
|---|---|
| GPS (MAX-M10S, continuous) | 7–8 mA |
| nRF52840: BLE/ANT+ sensors, logging | 1.5–3 mA |
| Sharp LCD + 5 V boost, 1–2 updates/s | 0.1–0.2 mA |
| Sensors, flash, LDO Iq, battery divider | ~0.1 mA |
| **Total** | **~10–11 mA** |

| Battery | Ride time |
|---|---|
| 30 × 48 × 6 (~850 mAh) | ~70–80 h |
| 30 × 48 × 8 (~1100 mAh) | ~90–100 h |
| 30 × 48 × 10 (~1500 mAh) | ~130 h |

Standby with GPS off: tens of µA (months).

## Colour build (ESP32-S3 + BL652 + IPS TFT)

| Load | Avg current while riding |
|---|---|
| GPS | 7–8 mA |
| ESP32-S3: BLE, UI, logging; Wi-Fi only to sync | 15–25 mA |
| BL652 ANT+/BLE sensor links | 1–2 mA |
| TFT logic (ST7789, datasheet typ.) | ~10 mA |
| Backlight, auto-dimmed (full = 160 mA / 1200 nit) | 20–80 mA |
| **Total** | **~55–125 mA** |

| Battery | Ride time |
|---|---|
| Adafruit 258, 1200 mAh (34 × 62 × 5) | ~10–22 h |
| Adafruit 328, 2500 mAh (needs a thicker case) | ~20–45 h |

The backlight dominates. The levers are auto-dimming (ambient light sensor), a lower default brightness, a shorter screen timeout, and later a transflective panel.

## Reference points
- Garmin Edge 540: ~26 h rated. Coros Dura: ~120 h with solar.
- ESP32-S3 Wi-Fi transmit peaks ~500 mA, which sets the 1 A LDO choice.
