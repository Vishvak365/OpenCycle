# OpenCycle

An open-source GPS bike computer you can print, solder, and flash yourself.

- **Screen:** 2.7" Sharp memory LCD, 400 × 240, 1-bit, sunlight-readable, microwatt power.
- **Brain:** nRF52840 (Bluetooth LE + ANT+), u-blox M10 GPS, 16 MB flash, barometer, accelerometer, speaker.
- **Battery:** ~90–130 h estimated ride time, depending on the cell.
- **Case:** FDM-printed, 86 × 52 × 16 mm, Garmin quarter-turn mount, three case styles.
- **Everything is generated from code:** the enclosure (CadQuery), the board (KiCad 7 via Python), and the interactive 3D viewer (three.js).

> **Status: concept / pre-prototype.** The enclosure model is complete and fit-checked. The PCB is a *presentable concept*: parts are placed, but it is **not fully routed, not DRC-clean, and has no schematic yet**. **Do not order boards from this repo.** See [`pcb/README_NOT_FOR_FAB.md`](pcb/README_NOT_FOR_FAB.md).

## What's here

| Path | What it is |
|---|---|
| `cad/` | Parametric enclosure and mechanical parts (CadQuery). `params.py` holds every dimension. |
| `pcb/` | Board generated from `design.py` (parts, nets, placement), a custom router, and DRC/zone tooling. |
| `viewer/` | Interactive 3D product viewer (three.js), PCB net explorer, and the on-device screen designs (`viewer/ui/screens.js`). |
| `tools/` | `build_all.sh` rebuilds CAD → PCB → viewer assets. |
| `docs/` | Hardware, PCB, CAD, UI, and decision docs. Start with [`docs/README.md`](docs/README.md). |
| `AGENTS.md` | Instructions for AI coding agents (and humans) picking the project up. |

## Quick start

```bash
# view the product (no build needed; the generated assets are committed)
python3 -m http.server -d viewer 8000     # then open http://localhost:8000

# rebuild everything (needs CadQuery + KiCad 7 python; see docs/SETUP.md)
./tools/build_all.sh
```

## Roadmap (short)

1. Finish the board: apply the agreed part swaps, route to 100%, DRC clean, schematic, human review.
2. Prototype firmware on an nRF52840 DK + Sharp display breakout (Zephyr / nRF Connect SDK, LVGL).
3. First board order, print the case, bring-up.
4. Companion phone app: routes, map tiles, ride sync.

Full list in [`docs/ROADMAP.md`](docs/ROADMAP.md).

## License

Not chosen yet. The likely plan is CERN-OHL-S for hardware and MIT for software. Until a license file is added, all rights are reserved by the author.
