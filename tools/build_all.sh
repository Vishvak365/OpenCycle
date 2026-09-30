#!/usr/bin/env bash
# Rebuild everything from source: enclosure -> board -> routing -> checks -> fab files -> viewer assets.
# Needs: Python 3.11 + cadquery numpy scipy numba pillow kiutils cairosvg imageio imageio-ffmpeg, KiCad 7 (pcbnew),
#        Java 17+ and xvfb (Freerouting, downloaded on first run). See docs/SETUP.md.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== CAD: enclosure, fit checks"
( cd cad && python3 model.py >/dev/null && python3 check_fit.py )

echo "== PCB: build from design.py, placement checks"
( cd pcb && python3 build_pcb.py && python3 check_place.py )

echo "== PCB: plane fan-out, Freerouting, pours + stitching, DRC"
( cd pcb && python3 fanout.py placed.kicad_pcb fanned.kicad_pcb \
         && python3 autoroute.py fanned.kicad_pcb routed.kicad_pcb 60 \
         && python3 finish.py routed.kicad_pcb opencycle.kicad_pcb )
grep -E "^\*\* Found" pcb/drc_report.txt

echo "== Schematic (generated) + netlist check against the board"
( cd pcb && python3 gen_schematic.py && python3 check_netlist.py )

echo "== Real board vs enclosure (3D)"
( cd cad && python3 board_fit.py ../pcb/opencycle.kicad_pcb )

echo "== Fab outputs, BOM docs, printable parts"
( cd pcb && python3 export_fab.py )
python3 tools/gen_bom_md.py
python3 tools/export_print.py >/dev/null

echo "== Viewer assets + time-lapse"
( cd pcb && python3 export_viewer.py opencycle.kicad_pcb )
python3 tools/export_meshes.py
python3 tools/pcb_timelapse.py pcb/opencycle.kicad_pcb docs/media/pcb_timelapse.mp4
echo "done: open viewer/index.html through a local web server (python3 -m http.server -d viewer)"
