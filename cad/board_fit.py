"""3D fit check of the REAL board against the enclosure.

Every footprint on the board becomes a box (pads + fab outline in plan, datasheet height from
pcb/design.py) on its side of the PCB, and is intersected with the case shells and the big
mechanical parts. Run after any board or case change:

    python board_fit.py ../pcb/opencycle.kicad_pcb     (or ../pcb/placed.kicad_pcb)
"""
import sys
from pathlib import Path

import cadquery as cq
import pcbnew

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "pcb"))
import design as D  # noqa: E402
from check_place import body  # noqa: E402
from model import build  # noqa: E402
from params import BODY_H, PCB_T, PCB_Z  # noqa: E402

TOL = 0.05   # mm3
AGAINST = ["battery", "speaker", "display", "foam_gasket", "display_ffc", "front_keys", "key_primary", "buttons",
           "cover_lens", "oring"]
# intended contacts: key caps sit on their switches, side plungers touch the side switch stems
ALLOWED = {("SW1", "front_keys"), ("SW2", "front_keys"), ("SW3", "key_primary"),
           ("J3", "display_ffc")}          # the FFC tail plugs into J3


def board_boxes(path):
    b = pcbnew.LoadBoard(str(path))
    parts = {p["ref"]: p for p in D.PARTS}
    out = {}
    for f in b.GetFootprints():
        ref = f.GetReference()
        if ref not in parts or parts[ref]["h"] <= 0.05:
            continue
        x0, y0, x1, y1 = body(f)
        h = parts[ref]["h"]
        front = f.GetLayer() == pcbnew.F_Cu
        z0 = PCB_Z + PCB_T if front else PCB_Z - h
        cy0, cy1 = BODY_H - y1, BODY_H - y0
        out[ref] = cq.Workplane("XY").box(x1 - x0, cy1 - cy0, h, centered=False).translate((x0, cy0, z0))
    return out


def main(path):
    parts, shells = build()
    boxes = board_boxes(path)
    variants = {"standard": ["std_back_shell", "std_front_bezel"], "aero": ["aero_back_shell", "aero_front_bezel"],
                "rugged": ["std_back_shell", "std_front_bezel", "rugged_bumper"]}
    bad = []
    for ref, bx in boxes.items():
        bb = bx.val().BoundingBox()
        targets = {n: parts[n] for n in AGAINST}
        for v in variants.values():
            targets.update({n: shells[n] for n in v})
        for name, solid in targets.items():
            if (ref, name) in ALLOWED:
                continue
            ob = solid.val().BoundingBox()
            if bb.xmax < ob.xmin or ob.xmax < bb.xmin or bb.ymax < ob.ymin or ob.ymax < bb.ymin or \
               bb.zmax < ob.zmin or ob.zmax < bb.zmin:
                continue
            vol = bx.intersect(solid).val().Volume()
            if vol > TOL:
                bad.append((ref, name, round(vol, 2)))
    for r in bad:
        print("INTERFERENCE", *r)
    print(f"board fit: {'OK' if not bad else f'{len(bad)} problems'} ({len(boxes)} parts checked)")
    return not bad


if __name__ == "__main__":
    ok = main(sys.argv[1] if len(sys.argv) > 1 else HERE.parent / "pcb" / "placed.kicad_pcb")
    raise SystemExit(0 if ok else 1)
