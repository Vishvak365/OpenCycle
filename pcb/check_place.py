"""Placement checks: courtyard overlaps per side, battery keep-out, board bounds."""
import itertools
import sys
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).parent))
import design as D  # noqa: E402

TM = pcbnew.ToMM


def court(fp, side_layer):
    cy = fp.GetCourtyard(side_layer)
    if cy.OutlineCount() == 0:
        bb = fp.GetBoundingBox(False, False)
        return (TM(bb.GetX()), TM(bb.GetY()), TM(bb.GetRight()), TM(bb.GetBottom()))
    bb = cy.BBox()
    return (TM(bb.GetX()), TM(bb.GetY()), TM(bb.GetRight()), TM(bb.GetBottom()))


def overlap(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def run(path):
    b = pcbnew.LoadBoard(path)
    b.BuildConnectivity()
    issues = []
    fps = list(b.GetFootprints())
    for side, lay in (("F", pcbnew.F_CrtYd), ("B", pcbnew.B_CrtYd)):
        on = [f for f in fps if (f.GetLayer() == pcbnew.F_Cu) == (side == "F") and not f.GetReference().startswith("H")]
        boxes = {f.GetReference(): court(f, lay) for f in on}
        for a, c in itertools.combinations(boxes, 2):
            if overlap(boxes[a], boxes[c]):
                issues.append(f"{side}: courtyard overlap {a} / {c}")
        for ref, bx in boxes.items():
            if bx[0] < D.BOARD["x0"] - 0.01 or bx[2] > D.BOARD["x0"] + D.BOARD["w"] + 0.8 or \
               bx[1] < D.BOARD["y0"] - 0.8 or bx[3] > D.BOARD["y0"] + D.BOARD["h"] + 0.8:
                issues.append(f"{side}: {ref} beyond board edge {tuple(round(v,2) for v in bx)}")
            if side == "B" and overlap(bx, D.BATTERY_KEEPOUT):
                issues.append(f"B: {ref} inside battery keep-out {tuple(round(v,2) for v in bx)}")
            if side == "B" and overlap(bx, D.SPEAKER_KEEPOUT):
                issues.append(f"B: {ref} inside speaker keep-out {tuple(round(v,2) for v in bx)}")
    # holes vs parts (2.4 mm boss radius each side)
    for (hx, hy) in D.HOLES:
        hb = (hx - 2.4, hy - 2.4, hx + 2.4, hy + 2.4)
        for f in fps:
            if f.GetReference().startswith("H"):
                continue
            lay = pcbnew.F_CrtYd if f.GetLayer() == pcbnew.F_Cu else pcbnew.B_CrtYd
            if overlap(court(f, lay), hb):
                issues.append(f"{f.GetReference()} overlaps standoff at {hx},{hy}")
    return issues


if __name__ == "__main__":
    iss = run(sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent / "placed.kicad_pcb"))
    print("\n".join(iss) if iss else "placement OK")
