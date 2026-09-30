# Roadmap

## v0.2 prototype (now)
- [x] Colour build parts chosen, pinouts verified against datasheets, all parts priced with links.
- [x] Enclosure v0.2 (52 × 92.4 × 17 mm), fit-checked against the real board; print files.
- [x] Board routed, DRC clean, schematic generated + netlist-matched, ERC clean; Gerbers, BOM, CPL.
- [x] Screen design language (Lucent) with 10 screens and an LVGL recipe.
- [ ] Order parts + boards, print, assemble, bring up ([instructions/](../instructions/README.md)).
- [ ] Measure: GPS fix / C/N0 in the case, BLE + Wi-Fi range, backlight current and temperature, battery life.

## Firmware (after the UI is final)
- [ ] ESP-IDF + LVGL: display, ride screen, page model, soft-key bar.
- [ ] GPS + FIT logging; BMP581 altitude; light-sensor backlight.
- [ ] BL652 ANT+/BLE bridge firmware + UART protocol.
- [ ] Map tiles and navigation; audio prompts.

## App
- [ ] Route import, tile generation, ride sync (React Native or Web Bluetooth).

## v0.3 ideas
- Power-path charger (run from USB without cycling the battery).
- Pin-fed or larger GPS patch if reception in the case is weak.
- Transflective display option if one becomes buyable in small quantities.
