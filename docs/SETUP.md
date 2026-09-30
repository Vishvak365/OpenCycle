# Toolchain setup

Tested on Ubuntu 24.04 with Python 3.11.

```bash
# KiCad 7 (provides the `pcbnew` Python module, symbol + footprint libraries)
sudo apt-get install -y --no-install-recommends kicad kicad-footprints kicad-symbols

# Python packages
pip install cadquery numpy scipy numba pillow kiutils cairosvg
```

Notes:
- The PCB scripts import `pcbnew`, which ships with KiCad and is only importable from the system Python that KiCad was built for.
- `pcb/design.py` expects KiCad libraries at `/usr/share/kicad/footprints/` and `/usr/share/kicad/symbols/`. On macOS/Windows, change `FP` in `design.py` and `LIB` in `symlib.py`.
- Scripts target the **KiCad 7** Python API (`FP_SHAPE`, `GetPos0`). KiCad 8 renamed some of these; porting is a small job.
- The viewer needs only a static file server: `python3 -m http.server -d viewer`.
