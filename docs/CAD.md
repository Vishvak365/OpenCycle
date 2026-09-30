# Enclosure CAD

All dimensions live in `cad/params.py`; geometry in `cad/model.py`; interference checks in `cad/check_fit.py`.

```bash
cd cad
python3 model.py        # writes out/step/*.step and out/stl/*.stl (+ full assemblies as STEP)
python3 check_fit.py    # must print OK for standard / aero / rugged
```

## Stack, back to front (z, mm)

| z | Layer |
|---|---|
| −3.0 → 0.0 | Garmin quarter-turn boss (approximate — verify against a known mount) |
| 0.0 → 1.5 | Back shell floor, speaker grille slots |
| 1.6 → 9.6 | LiPo pouch 30 × 48 × 8 |
| 1.8 → 5.3 | Speaker 11 × 15 × 3.5 (beside the battery) |
| 7.5 → 10.0 | Back-side modules |
| 10.0 → 11.0 | PCB |
| 11.0 | Case split line with O-ring |
| 12.8 → 13.3 | Foam ring |
| 13.3 → 15.0 | Sharp memory LCD |
| 15.0 → 16.0 | Cover lens (black mask printed on the underside) |

## Variants

- **Standard:** 1.5 mm back-edge radius, 1.2 mm front radius.
- **Aero:** 4.5 mm back-edge radius, 2.5 mm front radius.
- **Rugged:** standard shells plus a 2 mm TPU bumper with raised corner guards, a 0.6 mm lens lip, and knurled button covers.

## Printing notes

- Print both shells face-down (back shell on its back face, bezel on its front face): 0.2 mm layers, 4 walls, 30% gyroid.
- PETG or ASA for summer heat; PLA can creep on a black device in sun.
- Bumper and button covers in TPU 95A.
- Cover lens: 1.0 mm chemically strengthened glass or polycarbonate, cut to 48 × 82 mm with 5 mm corners.
- Seal: 1.2 mm O-ring cord in the groove at the split line; barometer vent needs a breathable membrane sticker.
