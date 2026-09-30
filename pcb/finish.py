"""Planes and pours, ground stitching, clean-up, DRC.

python finish.py routed.kicad_pcb opencycle.kicad_pcb

1. re-applies the design rules (KiCad 7 keeps them in the project file, which the DSN/SES round trip loses)
2. zones: In1 GND plane, In2 +3V3 plane, GND pours on F.Cu and B.Cu (solid pad connections)
3. removes dangling autorouter vias
4. stitches the outer GND pours to the In1 plane with vias on a 2.5 mm grid wherever both pours have room
5. refills and writes drc_report.txt
"""
import math
import os
import sys
from pathlib import Path

os.environ.setdefault("KICAD7_FOOTPRINT_DIR", "/usr/share/kicad/footprints")
os.environ.setdefault("KICAD7_SYMBOL_DIR", "/usr/share/kicad/symbols")
import pcbnew  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
import design as D  # noqa: E402

MM = lambda v: pcbnew.FromMM(float(v))  # noqa: E731
TM = pcbnew.ToMM


def add_zone(b, net, layer, priority, clearance=0.2, min_w=0.2, thermal=False):
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
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)      # solid: small SMD pads, 2 spokes would starve
    z.SetThermalReliefGap(MM(0.25))
    z.SetThermalReliefSpokeWidth(MM(0.3))
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    b.Add(z)
    return z


def remove_dangling(b):
    """Iteratively remove unlocked track ends and vias that connect to nothing (autorouter leftovers)."""
    pads = [p for f in b.GetFootprints() for p in f.Pads()]
    removed = 0
    while True:
        items = list(b.GetTracks())
        ends = {}
        for t in items:
            if t.GetClass() == "PCB_VIA":
                continue
            for pt in (t.GetStart(), t.GetEnd()):
                ends.setdefault((pt.x, pt.y, t.GetLayer()), []).append(t)
        vias = {(v.GetPosition().x, v.GetPosition().y): v for v in items if v.GetClass() == "PCB_VIA"}
        kill = []
        for t in items:
            if t.IsLocked():
                continue
            if t.GetClass() == "PCB_VIA":
                pos = t.GetPosition()
                layers = {L for L in (pcbnew.F_Cu, pcbnew.B_Cu) if (pos.x, pos.y, L) in ends}
                on_pad = any(p.GetNetCode() == t.GetNetCode() and p.HitTest(pos) for p in pads)
                if len(layers) < 2 and not on_pad and t.GetNetname() not in D.PLANE_NETS:
                    kill.append(t)
                continue
            for pt in (t.GetStart(), t.GetEnd()):
                key = (pt.x, pt.y, t.GetLayer())
                connected = len(ends.get(key, [])) > 1 or (pt.x, pt.y) in vias or \
                    any(p.GetNetCode() == t.GetNetCode() and p.IsOnLayer(t.GetLayer()) and p.HitTest(pt) for p in pads)
                if not connected and t.GetNetname() not in D.PLANE_NETS:
                    kill.append(t); break
        if not kill:
            return removed
        for t in kill:
            b.Remove(t)
        removed += len(kill)


def _seg_dist(p, a, c):
    ax, ay = a; cx, cy = c; px, py = p
    L2 = (cx - ax) ** 2 + (cy - ay) ** 2
    t = 0 if L2 == 0 else max(0, min(1, ((px - ax) * (cx - ax) + (py - ay) * (cy - ay)) / L2))
    return math.hypot(px - (ax + t * (cx - ax)), py - (ay + t * (cy - ay)))


def _via_ok(b, x, y, gnd_code, pads, tracks, vias, holes, keep):
    if any(r[0] - 0.5 <= x <= r[2] + 0.5 and r[1] - 0.5 <= y <= r[3] + 0.5 for r in keep):
        return False
    if any(math.hypot(x - vx, y - vy) < 0.9 for vx, vy in vias) or any(math.hypot(x - hx, y - hy) < 1.3 for hx, hy in holes):
        return False
    for bb, code in pads:
        cx = min(max(x, bb[0]), bb[2]); cy = min(max(y, bb[1]), bb[3])
        if code != gnd_code and math.hypot(cx - x, cy - y) < 0.5:
            return False
        if code == gnd_code and math.hypot(cx - x, cy - y) < 0.3:
            return False
    for (a, c, w, code) in tracks:
        if code != gnd_code and _seg_dist((x, y), a, c) < 0.25 + w / 2 + 0.2:
            return False
    return True


def stitch(b, pitch=2.5, margin=0.55):
    """GND vias on a grid wherever both outer GND pours are solid around the point, then at least one via
    in every outer GND pour island that has none."""
    gnd = b.FindNet("GND")
    fills = {}
    for z in b.Zones():
        if z.GetIsRuleArea() or z.GetNetname() != "GND" or z.GetLayer() not in (pcbnew.F_Cu, pcbnew.B_Cu):
            continue
        fills[z.GetLayer()] = z.GetFilledPolysList(z.GetLayer())
    keep = [k["rect"] for k in D.KEEPOUTS] + [k["rect"] for k in D.NO_TRACKS_B]
    pads = []
    for f in b.GetFootprints():
        for p in f.Pads():
            bb = p.GetBoundingBox()
            pads.append(((TM(bb.GetX()), TM(bb.GetY()), TM(bb.GetRight()), TM(bb.GetBottom())), p.GetNetCode()))
    tracks = [((TM(t.GetStart().x), TM(t.GetStart().y)), (TM(t.GetEnd().x), TM(t.GetEnd().y)), TM(t.GetWidth()), t.GetNetCode())
              for t in b.GetTracks() if t.GetClass() != "PCB_VIA"]
    vias = [(TM(t.GetPosition().x), TM(t.GetPosition().y)) for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]
    holes = [(TM(p.GetPosition().x), TM(p.GetPosition().y)) for f in b.GetFootprints() for p in f.Pads()
             if p.GetDrillSize().x > 0]
    code = gnd.GetNetCode()

    def inside(poly, x, y, m):
        return all(poly.Contains(pcbnew.VECTOR2I(MM(x + dx), MM(y + dy))) for dx, dy in
                   ((0, 0), (m, 0), (-m, 0), (0, m), (0, -m), (m * .7, m * .7), (-m * .7, m * .7), (m * .7, -m * .7), (-m * .7, -m * .7)))

    def add(x, y):
        v = pcbnew.PCB_VIA(b)
        v.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y))); v.SetWidth(MM(0.5)); v.SetDrill(MM(0.3))
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(gnd); b.Add(v)
        vias.append((x, y))

    n = 0
    x = D.BOARD["x0"] + 1.5
    while x < D.BOARD["x0"] + D.BOARD["w"] - 1.4:
        y = D.BOARD["y0"] + 1.5
        while y < D.BOARD["y0"] + D.BOARD["h"] - 1.4:
            if len(fills) == 2 and all(inside(p, x, y, margin) for p in fills.values()) and \
                    _via_ok(b, x, y, code, pads, tracks, vias, holes, keep):
                add(x, y); n += 1
            y += pitch
        x += pitch
    # islands: every filled outline on F/B needs a via (or a PTH) inside it
    for L, poly in fills.items():
        for i in range(poly.OutlineCount()):
            o = poly.Outline(i)
            bb = o.BBox()
            has = any(o.PointInside(pcbnew.VECTOR2I(MM(vx), MM(vy))) for vx, vy in vias + holes)
            if has:
                continue
            X0, Y0, X1, Y1 = TM(bb.GetX()), TM(bb.GetY()), TM(bb.GetRight()), TM(bb.GetBottom())
            done = False
            yy = Y0 + 0.4
            while yy < Y1 and not done:
                xx = X0 + 0.4
                while xx < X1 and not done:
                    single = pcbnew.SHAPE_POLY_SET(); single.AddOutline(o)
                    if inside(single, xx, yy, 0.45) and _via_ok(b, xx, yy, code, pads, tracks, vias, holes, keep):
                        add(xx, yy); n += 1; done = True
                    xx += 0.25
                yy += 0.25
    return n


def finish(src, dst):
    from build_pcb import apply_rules
    b = pcbnew.LoadBoard(src)
    apply_rules(b)
    have = {(z.GetLayer(), z.GetNetname()) for z in b.Zones() if not z.GetIsRuleArea()}
    for net, layer in (("GND", pcbnew.In1_Cu), ("+3V3", pcbnew.In2_Cu), ("GND", pcbnew.F_Cu), ("GND", pcbnew.B_Cu)):
        if (layer, net) not in have:
            add_zone(b, net, layer, 0)
    for z in b.Zones():
        if not z.GetIsRuleArea():
            z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    print("removed dangling track/via pieces:", remove_dangling(b))
    filler = pcbnew.ZONE_FILLER(b)
    filler.Fill(b.Zones())
    print("stitching vias:", stitch(b))
    filler.Fill(b.Zones())
    b.Save(dst)
    # reload so the project file and the custom rules (opencycle.kicad_dru) are picked up for DRC
    Path(dst).with_suffix(".kicad_dru").write_text((Path(__file__).parent / "rules.kicad_dru").read_text())
    b = pcbnew.LoadBoard(dst)
    rpt = str(Path(dst).with_name("drc_report.txt"))
    ok = pcbnew.WriteDRCReport(b, rpt, pcbnew.EDA_UNITS_MILLIMETRES, True)
    return rpt, ok


if __name__ == "__main__":
    rpt, ok = finish(sys.argv[1], sys.argv[2])
    print("DRC report:", rpt, ok)
