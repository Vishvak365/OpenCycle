# Enclosure CAD (v0.2)

All dimensions: [`cad/params.py`](../cad/params.py). Geometry: [`cad/model.py`](../cad/model.py). Checks: [`cad/check_fit.py`](../cad/check_fit.py) (placeholder assembly) and [`cad/board_fit.py`](../cad/board_fit.py) (every real board part vs. the case). Print files: [`print/`](../print/README.md).

```bash
cd cad
python3 model.py                                   # out/step/*.step, out/stl/*.stl, full assemblies as STEP
python3 check_fit.py                               # must print OK for standard / aero / rugged
python3 board_fit.py ../pcb/opencycle.kicad_pcb    # must print "board fit: OK"
python3 ../tools/export_print.py                   # print-oriented STLs + STEP into print/
```

Body: **52 × 92.4 × 17 mm**, 7 mm plan radius, Garmin quarter-turn boss on the back.

## Stack, back to front (z, mm)

| z | Layer |
|---|---|
| −3.0 → 0.0 | Garmin quarter-turn boss (approximate — verify against a known mount before relying on it) |
| 0.0 → 1.5 | Back shell floor (1.0 mm under the battery pocket), speaker grille slots |
| 1.1 → 6.1 | LiPo 34 × 62 × 5 mm (Adafruit 258) in a 0.5 mm floor pocket |
| 1.8 → 4.3 | Speaker 15 × 11 × 2.5 mm (fires through the floor grille) |
| 6.75 → 10.0 | Back-side parts (ESP32 module 3.25 mm tall over the battery, 0.65 mm clearance) |
| 10.0 → 11.0 | PCB |
| 11.0 | Case split line with the O-ring |
| 11.0 → 13.0 | Front-side parts (≤ 2.15 mm under the display, ≤ 1.3 mm under the folded FFC); key switches 2.5 mm |
| 12.95 → 13.45 | Foam ring |
| 13.45 → 16.0 | Newhaven 2.4" TFT (2.55 mm) |
| 16.0 → 17.0 | Cover lens, black mask on the underside with windows for the screen, light sensor and charge LED |

## Front layout (CAD coordinates, y up from the bottom edge)

- Display outline x 4.6 → 47.4, y 16.89 → 76.8 (top band 15.6 mm); active area 36.72 × 48.96 mm.
- 12 mm GPS patch centre (27.2, 83.0), tucked under the lens ledge in a relief pocket in the bezel.
- Front keys: 9 mm caps at x 13.76 / 26.0 / 38.24, y 8.7, 0.8 mm proud; each sits on a PTS810 switch with a retaining flange under the 1.5 mm bezel face.
- Side buttons at y 58.4 (left: power/back, right: menu); switch stems 0.1 mm from the plungers.
- USB-C mouth 2.1 mm behind the case face with a 12.8 × 7.0 × 1.9 mm counterbore so any USB-C plug overmold reaches.
- Barometer vent: 0.8 mm hole in the right wall at y 44 (cover with a breathable PTFE sticker).

## Variants

- **Standard:** 1.5 mm back-edge radius, 1.2 mm front radius.
- **Aero:** 4.5 mm back-edge radius, 2.5 mm front radius.
- **Rugged:** standard shells + 2 mm TPU bumper with corner guards, 0.6 mm lens lip, knurled TPU button covers.

Printing: see [`print/README.md`](../print/README.md).
