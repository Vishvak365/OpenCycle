# Toolchain setup

Tested on Ubuntu 24.04, Python 3.11, KiCad 7.0.11.

```bash
# KiCad 7 (pcbnew Python module, kicad-cli, symbol + footprint libraries)
sudo apt-get install -y --no-install-recommends kicad kicad-footprints kicad-symbols

# Python packages
pip install cadquery numpy scipy numba pillow kiutils cairosvg imageio imageio-ffmpeg

# Freerouting (autorouter): needs Java 17+ and a virtual display for headless runs
sudo apt-get install -y openjdk-21-jre-headless xvfb
# pcb/autoroute.py downloads freerouting-1.9.0.jar into pcb/ on first run (git-ignored)

# Optional: KiCad 9 CLI for ERC only (KiCad 7's CLI has no ERC). Extract it next to KiCad 7
# instead of upgrading, because the pipeline scripts use the KiCad 7 Python API.
#   add the kicad-9.0-releases PPA, `apt-get download kicad`, `dpkg -x kicad_*.deb /opt/kicad9`,
#   then: LD_LIBRARY_PATH=/opt/kicad9/usr/lib/x86_64-linux-gnu /opt/kicad9/usr/bin/kicad-cli sch erc ...
```

Notes:
- The PCB scripts import `pcbnew`, which ships with KiCad and targets the **KiCad 7** API (`FP_SHAPE`, `FP_ZONE`, `SetProperty`). KiCad 8/9 renamed some of these; porting is a small job.
- `pcb/design.py` expects KiCad libraries at `/usr/share/kicad/footprints/` and `/usr/share/kicad/symbols/`. On macOS/Windows change `FP` in `design.py` and `LIB` in `symlib.py`.
- The board opens in KiCad 7+ directly (`pcb/opencycle.kicad_pro`); `fp-lib-table` and `sym-lib-table` in `pcb/` point at the local library.
- Viewer and UI renders: a static file server (`python3 -m http.server -d viewer`); screenshots use Playwright + Chromium (`docs/ui/shoot.mjs`).
