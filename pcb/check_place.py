"""Placement checks for the v0.2 board.

- courtyard overlaps per side
- parts inside the board outline
- height limits from the enclosure stack (design.HEIGHT_ZONES)
- nothing but copper-free parts inside the antenna keep-outs
- standoff / screw-head clearance around the mounting holes
- front parts outside the bezel opening (3.5 mm from the body edge = 0.5 mm from the board edge)
"""
import itertools
import sys
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).parent))
import design as D  # noqa: E402

TM = pcbnew.ToMM
PART = {p["ref"]: p for p in D.PARTS}


def _union(boxes):
    return (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))


def _bb(item):
    bb = item.GetBoundingBox()
    return (TM(bb.GetX()), TM(bb.GetY()), TM(bb.GetRight()), TM(bb.GetBottom()))


def body(fp):
    """pads + fab outline (the physical part), without courtyard margin or text"""
    boxes = [_bb(p) for p in fp.Pads()]
    boxes += [_bb(g) for g in fp.GraphicalItems()
              if g.GetClass() != "MTEXT" and g.GetLayerName() in ("F.Fab", "B.Fab")]
    return _union(boxes)


def court(fp):
    if fp.GetReference() == "U1":      # library courtyard includes the 48 x 21 mm antenna keep-out
        x0, y0, x1, y1 = body(fp)
        return (x0 - 0.25, y0 - 0.25, x1 + 0.25, y1 + 0.25)
    boxes = [_bb(g) for g in fp.GraphicalItems()
             if g.GetClass() != "MTEXT" and g.GetLayerName() in ("F.Courtyard", "B.Courtyard")]
    return _union(boxes) if boxes else body(fp)


def overlap(a, b, m=0.0):
    return a[0] < b[2] - m and b[0] < a[2] - m and a[1] < b[3] - m and b[1] < a[3] - m


def run(path):
    b = pcbnew.LoadBoard(path)
    issues = []
    fps = [f for f in b.GetFootprints() if not f.GetReference().startswith("H")]
    side = {f.GetReference(): ("F" if f.GetLayer() == pcbnew.F_Cu else "B") for f in fps}
    for s in "FB":
        on = [f for f in fps if side[f.GetReference()] == s]
        boxes = {f.GetReference(): court(f) for f in on}
        for a, c in itertools.combinations(boxes, 2):
            if overlap(boxes[a], boxes[c]):
                issues.append(f"{s}: courtyard overlap {a} / {c}")
    X0, Y0 = D.BOARD["x0"], D.BOARD["y0"]
    X1, Y1 = X0 + D.BOARD["w"], Y0 + D.BOARD["h"]
    for f in fps:
        ref, s = f.GetReference(), side[f.GetReference()]
        bx = body(f)
        h = PART[ref]["h"]
        overhang = 1.0 if ref == "J1" else 0.05          # USB-C mouth sits at the case opening
        if bx[0] < X0 - 0.05 or bx[2] > X1 + 0.05 or bx[1] < Y0 - 0.05 or bx[3] > Y1 + overhang:
            issues.append(f"{s}: {ref} outside the board {tuple(round(v, 2) for v in bx)}")
        for zs, rect, hmax, why in D.HEIGHT_ZONES:
            if zs == s and overlap(bx, rect) and h > hmax + 1e-6 and ref != "J3":
                issues.append(f"{s}: {ref} is {h} mm tall inside a {hmax} mm zone ({why})")
        for k in D.KEEPOUTS:
            if overlap(bx, k["rect"]) and ref not in ("U1", "U2"):
                issues.append(f"{s}: {ref} inside keep-out '{k['name']}'")
        if s == "F" and (bx[0] < X0 + 0.5 or bx[2] > X1 - 0.5 or bx[1] < Y0 + 0.5) and ref != "AE1":
            issues.append(f"F: {ref} under the bezel ledge {tuple(round(v, 2) for v in bx)}")
        for (hx, hy) in D.HOLES:
            r = 2.4 if s == "B" else 2.1        # back: shell standoff; front: M2 screw head
            if overlap(bx, (hx - r, hy - r, hx + r, hy + r)):
                issues.append(f"{s}: {ref} overlaps the standoff/screw at {hx},{hy}")
    # through-holes (NPTH pegs, PTH) go through the board: nothing on the other side may sit on them
    for f in fps:
        for pad in f.Pads():
            if pad.GetAttribute() not in (pcbnew.PAD_ATTRIB_NPTH, pcbnew.PAD_ATTRIB_PTH) or pad.GetDrillSize().x == 0:
                continue
            hx, hy = TM(pad.GetPosition().x), TM(pad.GetPosition().y)
            r = TM(pad.GetDrillSize().x) / 2 + 0.2
            for g in fps:
                if g is f or side[g.GetReference()] == side[f.GetReference()]:
                    continue
                if overlap(body(g), (hx - r, hy - r, hx + r, hy + r)):
                    issues.append(f"hole of {f.GetReference()} at ({hx:.2f},{hy:.2f}) under {g.GetReference()} on the other side")
    return issues


if __name__ == "__main__":
    iss = run(sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent / "placed.kicad_pcb"))
    print("\n".join(iss) if iss else "placement OK")
