# 3D viewer

`viewer/index.html` is a single static page (three.js r160 from jsDelivr via an import map).

Inputs (all generated, don't hand-edit):
- `meshes.json` — base64 STL of the enclosure and mechanical parts (`tools/export_meshes.py`).
- `pcb.json` — every board part (position, size, side, height, nets, MPN), tracks, vias and pads (`pcb/export_viewer.py`, from the routed `pcb/opencycle.kicad_pcb`).
- `pcb_{front,back}_{color,orm}.png` — board textures at 24 px/mm: solder mask, copper under mask, ENIG pads, silkscreen. ORM = (occlusion, roughness, metalness).
- `ui/screens_color.js` + `ui/fonts/` — the Lucent screen renderer, drawn onto the 3D display and the "On-device screens" section.

Rendering notes:
- ACES tone mapping, RoomEnvironment reflections, soft shadow on a shadow-catcher floor.
- Printed parts use a patched `MeshPhysicalMaterial` that perturbs normals with 0.2 mm layer lines on walls and 45° top-skin lines on flat faces.
- The display is emissive (not tone-mapped) so its colours match the renderer.
- Board components are procedural boxes sized from each footprint's pads + fab outline, with heights from `design.py`.
- URL hashes: `#board`, `#exploded` open those views directly.

Serve locally: `python3 -m http.server -d viewer 8000`.
