# 3D viewer

Two static pages (three.js r160 from jsDelivr via an import map), sharing the same generated assets:

- `viewer/index.html` — the studio viewer: finishes, variants, exploded view, PCB net explorer, every Lucent screen.
- `viewer/product.html` — the product page: a scroll-driven tour (hero → shells → exploded → board → back) with the device in a sticky studio stage, the live Lucent UI with working soft keys, specs and build steps. Serve the folder and open `/product.html`.

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
