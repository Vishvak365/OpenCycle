"""Export enclosure + mechanical parts as base64 STL bundle for the viewer (viewer/meshes.json)."""
import base64
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "cad"))
import cadquery as cq  # noqa: E402
from model import build  # noqa: E402

KEEP = ["battery", "display", "display_active_area", "lens_mask", "cover_lens", "foam_gasket", "buttons", "front_keys", "key_primary",
        "oring", "usb_flap", "speaker", "speaker_membrane"]

parts, shells = build()
out = {}
with tempfile.TemporaryDirectory() as tmp:
    for name, wp in [(k, parts[k]) for k in KEEP] + list(shells.items()):
        f = Path(tmp) / f"{name}.stl"
        fine = name in shells
        cq.exporters.export(wp, str(f), tolerance=0.015 if fine else 0.04, angularTolerance=0.08 if fine else 0.2)
        out[name] = base64.b64encode(f.read_bytes()).decode()
(ROOT / "viewer" / "meshes.json").write_text(json.dumps(out))
print("wrote viewer/meshes.json", len(out), "meshes")
