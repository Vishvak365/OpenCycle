"""Export the printable parts, oriented for printing, into print/ (STL) and print/step/ (STEP).

python tools/export_print.py

Orientation rules (FDM, 0.2 mm layers, no supports unless noted in print/README.md):
  back shells   rim on the bed (open side down) -> floor, grille and mount boss print as bridges/top surfaces
  front bezels  front face on the bed           -> the visible face gets the smooth bed finish
  key caps      flange on the bed
  side buttons  lying on their long side
  bumper/covers TPU, as modelled (bumper standing on its lower edge)
"""
import sys
from pathlib import Path

import cadquery as cq

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "cad"))
from model import build  # noqa: E402
from params import BODY_D  # noqa: E402

OUT = ROOT / "print"


def to_bed(wp):
    bb = wp.val().BoundingBox()
    return wp.translate((-bb.xmin, -bb.ymin, -bb.zmin))


def flip(wp):          # rotate 180 deg about X: top becomes bottom
    return wp.rotate((0, 0, 0), (1, 0, 0), 180)


def main():
    parts, shells = build()
    jobs = {
        # file name: (solid, orientation fn, material, note)
        "back_shell_standard": (shells["std_back_shell"], flip, "PETG or PLA", "rim down"),
        "front_bezel_standard": (shells["std_front_bezel"], flip, "PETG or PLA", "front face down"),
        "back_shell_aero": (shells["aero_back_shell"], flip, "PETG or PLA", "rim down"),
        "front_bezel_aero": (shells["aero_front_bezel"], flip, "PETG or PLA", "front face down"),
        "bumper_rugged": (shells["rugged_bumper"], lambda w: w, "TPU 95A", "as modelled"),
        "button_covers_rugged": (shells["rugged_button_covers"], lambda w: w, "TPU 95A", "as modelled"),
        "key_caps_x2": (parts["front_keys"], lambda w: w, "PETG or PLA (any colour)", "flange down"),
        "key_cap_primary": (parts["key_primary"], lambda w: w, "PETG or PLA (accent colour)", "flange down"),
        "side_buttons_x2": (parts["buttons"], lambda w: w, "PETG or TPU", "flat, as modelled"),
        "usb_flap": (parts["usb_flap"], lambda w: w.rotate((0, 0, 0), (1, 0, 0), 90), "TPU 95A", "flat"),
    }
    (OUT / "step").mkdir(parents=True, exist_ok=True)
    rows = []
    for name, (solid, orient, mat, note) in jobs.items():
        s = to_bed(orient(solid))
        cq.exporters.export(s, str(OUT / f"{name}.stl"), tolerance=0.02, angularTolerance=0.1)
        cq.exporters.export(solid, str(OUT / "step" / f"{name}.step"))
        bb = s.val().BoundingBox()
        rows.append((name, mat, note, f"{bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f}", s.val().Volume() / 1000))
    # laser-cut / non-printed parts as STEP (and DXF outline for the lens)
    for name in ("cover_lens", "lens_mask"):
        cq.exporters.export(parts[name], str(OUT / "step" / f"{name}.step"))
    cq.exporters.export(cq.Workplane("XY").add(parts["cover_lens"].faces("<Z").val()), str(OUT / "cover_lens_outline.dxf"))
    for r in rows:
        print(f"{r[0]:24s} {r[1]:28s} {r[2]:16s} {r[3]:>20s} mm  {r[4]:5.1f} cm3")
    return rows


if __name__ == "__main__":
    main()
