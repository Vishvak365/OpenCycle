# Roadmap

## Board v0.1 → orderable
- [ ] Resolve open decisions in DECISIONS.md (module source, battery, assembly route).
- [ ] Apply agreed part swaps in `pcb/design.py` (footprints + symbols).
- [ ] Generate the schematic (`.kicad_sch`) from `design.py`; export PDF.
- [ ] Route to 100% (fix router or hand-finish in KiCad); DRC 0 errors.
- [ ] Human review: power path, RF keep-outs and 50 Ω feed, display pinout and voltages, battery polarity.
- [ ] Gerbers, drill, BOM, pick-and-place.

## Enclosure
- [ ] Sync with the final board (USB-C position for USB4105, switch height, battery choice).
- [ ] Verify the Garmin mount against a known-good model; test-print.
- [ ] Front light option.

## Firmware
- [ ] DK + display breakout: `ride` screen in LVGL.
- [ ] GPS + FIT logging; BLE sensors; ANT+.
- [ ] Map tiles and navigation.

## App
- [ ] Route import, tile generation, ride sync (React Native or Web Bluetooth).
