# 3D viewer

`viewer/index.html` is a single static page (three.js r160 from jsDelivr via an import map).

Inputs (all generated, don't hand-edit):
- `meshes.json` — base64 STL of enclosure and mechanical parts (`tools/export_meshes.py`).
- `pcb.json` — parts (position, size, side, nets), tracks, vias, pads, unrouted nets (`pcb/export_viewer.py`).
- `pcb_{front,back}_{color,orm}.png` — board textures at 24 px/mm: solder mask, copper under mask, ENIG pads, silk. ORM = (occlusion, roughness, metalness).
- `ui/screens.js` — device screen renderer, drawn onto the 3D display and the "On-device screens" section.

Rendering notes:
- ACES tone mapping, RoomEnvironment reflections, soft shadow on a shadow-catcher floor.
- Printed parts use a patched `MeshPhysicalMaterial` that perturbs normals with 0.2 mm layer lines on walls and 45° top-skin lines on flat faces (object-space z = print direction), with derivative-based fading to avoid aliasing.
- Board components are procedural boxes sized from courtyards with type-specific materials (tin cans, epoxy, ceramic, nylon). Swap in KiCad 3D models (`kicad-packages3d`, STEP → GLB) for higher fidelity.
- URL hashes: `#board`, `#exploded` open those views directly.

Serve locally: `python3 -m http.server -d viewer 8000`.
