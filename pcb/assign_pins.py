"""Choose nRF52840 GPIOs by geometry: each MCU signal gets the free module pad
closest to where that signal goes (Hungarian assignment). Writes pinmap.json,
which design.py uses for U1.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pcbnew
from scipy.optimize import linear_sum_assignment

sys.path.insert(0, str(Path(__file__).parent))
import design as D  # noqa: E402
from symlib import pins as sym_pins  # noqa: E402

TM = pcbnew.ToMM
FIXED = {"GND", "VDD", "VDDH", "VBUS", "D-", "D+", "SWDIO", "SWDCLK", "P0.18", "P1.00"}
RESERVED = {"P0.00", "P0.01", "P0.09", "P0.10", "P0.18", "P1.00"}   # 32k xtal, NFC, reset, SWO
ANALOG = {"P0.02", "P0.03", "P0.04", "P0.05", "P0.28", "P0.29", "P0.30", "P0.31"}
INNER_PENALTY = 3.0


def main(board_path):
    b = pcbnew.LoadBoard(board_path)
    u1 = b.FindFootprintByReference("U1")
    num2name = {n: nm for n, nm, *_ in sym_pins("RF_Module", "MDBT50Q-1MV2")}
    pads = {}
    for p in u1.Pads():
        name = num2name.get(p.GetNumber())
        if name and name.startswith("P") and name not in RESERVED:
            q = p.GetPosition()
            local = p.GetPos0()
            inner = not (abs(TM(local.x)) > 4.5 or TM(local.y) > 7.0)
            pads[name] = ((TM(q.x), TM(q.y)), inner)
    u1_part = next(p for p in D.PARTS if p["ref"] == "U1")
    signals = [net for key, net in u1_part["pins"].items() if key not in FIXED and net]
    dest = {}
    for fp in b.GetFootprints():
        if fp.GetReference() == "U1":
            continue
        for p in fp.Pads():
            if p.GetNetname() in signals:
                q = p.GetPosition()
                dest.setdefault(p.GetNetname(), []).append((TM(q.x), TM(q.y)))
    names = sorted(pads)
    cost = np.zeros((len(signals), len(names)))
    for i, s in enumerate(signals):
        pts = dest[s]
        cx = sum(x for x, _ in pts) / len(pts); cy = sum(y for _, y in pts) / len(pts)
        for j, n in enumerate(names):
            (px, py), inner = pads[n]
            c = math.dist((px, py), (cx, cy)) + (INNER_PENALTY if inner else 0)
            if s == "VBAT_SENSE" and n not in ANALOG:
                c += 1e6
            cost[i, j] = c
    r, c = linear_sum_assignment(cost)
    mapping = {names[j]: signals[i] for i, j in zip(r, c)}
    out = Path(__file__).parent / "pinmap.json"
    out.write_text(json.dumps(dict(sorted(mapping.items())), indent=1))
    print(json.dumps(mapping, indent=0))


if __name__ == "__main__":
    main(sys.argv[1])
