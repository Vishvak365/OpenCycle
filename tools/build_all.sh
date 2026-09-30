#!/usr/bin/env bash
# Rebuild everything: enclosure CAD -> board -> routing -> viewer assets.
# Needs: Python 3.11, cadquery, numpy, scipy, numba, pillow, kiutils, and KiCad 7 (pcbnew Python module).
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== CAD: enclosure and parts"
( cd cad && python3 model.py && python3 check_fit.py )

echo "== PCB: place, pick MCU pins, re-place"
( cd pcb && python3 build_pcb.py && python3 assign_pins.py placed.kicad_pcb && python3 build_pcb.py && python3 check_place.py )

echo "== PCB: route (several passes, keeps the best), pours, DRC"
( cd pcb && python3 router.py placed.kicad_pcb routed.kicad_pcb && python3 finish.py routed.kicad_pcb opencycle.kicad_pcb )

echo "== Viewer assets"
( cd pcb && python3 export_viewer.py opencycle.kicad_pcb )
python3 tools/export_meshes.py
echo "done: open viewer/index.html through a local web server (python3 -m http.server -d viewer)"
