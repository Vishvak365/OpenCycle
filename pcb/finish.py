"""Add planes / pours, fill zones, run DRC.

python finish.py routed.kicad_pcb opencycle.kicad_pcb
"""
import json
import sys
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).parent))
import design as D  # noqa: E402

MM = lambda v: pcbnew.FromMM(float(v))  # noqa: E731


def add_zone(b, net, layer, priority, clearance=0.2, min_w=0.2, thermal=True):
    x0, y0 = D.BOARD["x0"] - 1, D.BOARD["y0"] - 1
    x1, y1 = x0 + D.BOARD["w"] + 2, y0 + D.BOARD["h"] + 2
    z = pcbnew.ZONE(b)
    z.SetLayer(layer)
    z.SetNet(b.FindNet(net))
    ol = z.Outline()
    ol.NewOutline()
    for (x, y) in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]:
        ol.Append(MM(x), MM(y))
    z.SetAssignedPriority(priority) if hasattr(z, "SetAssignedPriority") else z.SetPriority(priority)
    z.SetLocalClearance(MM(clearance))
    z.SetMinThickness(MM(min_w))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL if thermal else pcbnew.ZONE_CONNECTION_FULL)
    z.SetThermalReliefGap(MM(0.25))
    z.SetThermalReliefSpokeWidth(MM(0.3))
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    b.Add(z)
    return z


def finish(src, dst):
    b = pcbnew.LoadBoard(src)
    add_zone(b, "GND", pcbnew.In1_Cu, 0)
    add_zone(b, "+3V3", pcbnew.In2_Cu, 0)
    add_zone(b, "GND", pcbnew.F_Cu, 0)
    add_zone(b, "GND", pcbnew.B_Cu, 0)
    filler = pcbnew.ZONE_FILLER(b)
    filler.Fill(b.Zones())
    b.Save(dst)
    rpt = str(Path(dst).with_name("drc_report.txt"))
    ok = pcbnew.WriteDRCReport(b, rpt, pcbnew.EDA_UNITS_MILLIMETRES, True)
    return rpt, ok


if __name__ == "__main__":
    rpt, ok = finish(sys.argv[1], sys.argv[2])
    print("DRC report:", rpt, ok)
