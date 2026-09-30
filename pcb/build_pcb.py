"""Build the OpenCycle v0.2 board from design.py: outline, stackup, footprints, nets, keep-outs.

python build_pcb.py            -> placed.kicad_pcb (placed, unrouted except the RF feed)
"""
import sys
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).parent))
import design as D  # noqa: E402
from symlib import pins as sym_pins  # noqa: E402

HERE = Path(__file__).parent
MM = pcbnew.FromMM
V = lambda x, y: pcbnew.VECTOR2I(MM(x), MM(y))  # noqa: E731
LOCAL_LIB = HERE / "OpenCycle.pretty"


def load_fp(lib, name):
    if lib == "OpenCycle":
        return pcbnew.FootprintLoad(str(LOCAL_LIB), name)
    return pcbnew.FootprintLoad(D.FP + lib + ".pretty", name)


def pin_map(p):
    """symbol pin name/number -> {pad number: net}; every symbol pin must be listed in design.py."""
    by_name = {}
    spins = sym_pins(p["slib"], p["sym"])
    for num, name, *_ in spins:
        by_name.setdefault(name, []).append(num)
        by_name.setdefault(num, []).append(num)
    out, listed = {}, set()
    for key, net in p["pins"].items():
        if key not in by_name:
            raise KeyError(f"{p['ref']}: symbol {p['sym']} has no pin '{key}'")
        for num in by_name[key]:
            out[num] = net
            listed.add(num)
    missing = {n for n, *_ in spins} - listed
    if missing:
        raise KeyError(f"{p['ref']}: pins not assigned in design.py: {sorted(missing)}")
    return out


def rule_area(b, rect, layers, name, tracks=True, vias=True, pour=True, footprints=False):
    z = pcbnew.ZONE(b)
    z.SetIsRuleArea(True)
    z.SetZoneName(name)
    z.SetDoNotAllowCopperPour(pour); z.SetDoNotAllowTracks(tracks); z.SetDoNotAllowVias(vias)
    z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(footprints)
    ls = pcbnew.LSET()
    for L in layers:
        ls.AddLayer(L)
    z.SetLayerSet(ls)
    ol = z.Outline(); ol.NewOutline()
    x0, y0, x1, y1 = rect
    for x, y in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]:
        ol.Append(MM(x), MM(y))
    b.Add(z)


def build():
    import subprocess
    subprocess.run([sys.executable, str(HERE / "lib" / "gen_footprints.py")], check=True)
    b = pcbnew.BOARD()
    b.SetCopperLayerCount(4)
    ds = b.GetDesignSettings()
    ds.SetBoardThickness(MM(D.BOARD["thickness"]))
    ds.m_TrackMinWidth = MM(0.127)
    ds.m_MinClearance = MM(0.127)
    ds.m_ViasMinSize = MM(0.45)
    ds.m_MinThroughDrill = MM(0.2)          # ESP32 footprint thermal vias; JLC 4-layer minimum is 0.2 mm
    ds.m_CopperEdgeClearance = MM(0.3)
    ds.m_HoleClearance = MM(0.19)           # GCT USB4105 library footprint has 0.194 mm NPTH-to-pad
    ds.m_HoleToHoleMin = MM(0.25)
    ds.m_SilkClearance = MM(0.0)
    nc = ds.m_NetSettings.m_DefaultNetClass
    nc.SetClearance(MM(0.15))
    nc.SetTrackWidth(MM(0.2))
    nc.SetViaDiameter(MM(0.5))
    nc.SetViaDrill(MM(0.3))
    for i in (pcbnew.In1_Cu, pcbnew.In2_Cu):
        b.SetLayerType(i, pcbnew.LT_POWER)

    # outline (rounded rectangle)
    x0, y0, w, h, r = (D.BOARD[k] for k in ("x0", "y0", "w", "h", "r"))
    x1, y1 = x0 + w, y0 + h

    def seg(a, c):
        s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(V(*a)); s.SetEnd(V(*c)); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(MM(0.1)); b.Add(s)

    def arc(c, start):
        s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_ARC)
        s.SetCenter(V(*c)); s.SetStart(V(*start)); s.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T))
        s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(MM(0.1)); b.Add(s)

    seg((x0 + r, y0), (x1 - r, y0)); seg((x1, y0 + r), (x1, y1 - r))
    seg((x1 - r, y1), (x0 + r, y1)); seg((x0, y1 - r), (x0, y0 + r))
    arc((x1 - r, y0 + r), (x1 - r, y0)); arc((x1 - r, y1 - r), (x1, y1 - r))
    arc((x0 + r, y1 - r), (x0 + r, y1)); arc((x0 + r, y0 + r), (x0, y0 + r))

    nets = {}

    def net(name):
        if name not in nets:
            n = pcbnew.NETINFO_ITEM(b, name)
            b.Add(n); nets[name] = n
        return nets[name]

    for p in D.PARTS:
        fp = load_fp(p["flib"], p["fp"])
        fp.SetReference(p["ref"])
        fp.SetValue(p["value"])
        fp.SetPosition(V(p["x"], p["y"]))
        fp.SetOrientationDegrees(p["rot"])
        if p["mpn"]:
            fp.SetProperty("MPN", p["mpn"]); fp.SetProperty("Manufacturer", p["mfr"])
        if not p["mpn"] or p["ref"].startswith("FID"):
            fp.SetAttributes(fp.GetAttributes() | pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES)
        # the library ESP32 footprint carries a 48 x 21 mm antenna keep-out zone and courtyard;
        # design.py defines an edge keep-out instead and the courtyard becomes the module outline + 0.25 mm
        if p["ref"] == "U1":
            for z in list(fp.Zones()):
                fp.Remove(z)
            for g in list(fp.GraphicalItems()):
                if g.GetLayer() == pcbnew.F_CrtYd:
                    fp.Remove(g)
            r = pcbnew.FP_SHAPE(fp); r.SetShape(pcbnew.SHAPE_T_RECT)
            r.SetStart0(V(-9.3, -13.05)); r.SetEnd0(V(9.3, 13.05)); r.SetLayer(pcbnew.F_CrtYd); r.SetWidth(MM(0.05))
            fp.Add(r); r.SetDrawCoord()
        pm = pin_map(p) if p["pins"] else {}
        for pad in fp.Pads():
            num = pad.GetNumber()
            if num == "":
                continue
            n = pm.get(num)
            if n is None and num == "MP":
                n = "GND"
            if n:
                pad.SetNet(net(n))
        b.Add(fp)
        if p["side"] == "B":
            fp.Flip(fp.GetPosition(), True)
        fp.Reference().SetTextSize(pcbnew.VECTOR2I(MM(0.8), MM(0.8)))
        fp.Reference().SetTextThickness(MM(0.15))
        fp.Value().SetVisible(False)
        if p["ref"].startswith(("FID", "J4", "J5")):
            fp.Reference().SetVisible(False)

    for i, (hx, hy) in enumerate(D.HOLES, 1):
        fp = load_fp("MountingHole", "MountingHole_2.2mm_M2_Pad_Via")
        fp.SetReference(f"H{i}")
        fp.SetPosition(V(hx, hy))
        for pad in fp.Pads():
            pad.SetNet(net("GND"))
        b.Add(fp)
        fp.Reference().SetVisible(False)

    # keep-outs
    allcu = [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu]
    for k in D.KEEPOUTS:
        rule_area(b, k["rect"], allcu, k["name"])
    for k in D.NO_TRACKS_F:
        rule_area(b, k["rect"], [pcbnew.F_Cu], k["name"], vias=False, pour=False)
    for k in D.NO_TRACKS_B:
        rule_area(b, k["rect"], [pcbnew.B_Cu], k["name"], pour=True)

    # RF feed: patch feed pad -> MAX-M10S RF_IN, short 0.2 mm trace on F.Cu (hand-placed, marked locked)
    feed = next(p for p in b.FindFootprintByReference("AE1").Pads() if p.GetNumber() == "1").GetPosition()
    rfin = next(p for p in b.FindFootprintByReference("U3").Pads() if p.GetNumber() == "11").GetPosition()
    fx, fy, rx, ry = (pcbnew.ToMM(v) for v in (feed.x, feed.y, rfin.x, rfin.y))
    # feed pad -> left along the feed row -> down beside the receiver -> into RF_IN (clear of the ground pads)
    # vertical run centred in the gap between the RF_IN pad and the nearest patch ground pad
    rf_pad = next(p for p in b.FindFootprintByReference("U3").Pads() if p.GetNumber() == "11")
    x_left = pcbnew.ToMM(rf_pad.GetBoundingBox().GetRight())
    x_right = min(pcbnew.ToMM(p.GetBoundingBox().GetX()) for p in b.FindFootprintByReference("AE1").Pads()
                  if p.GetNumber() != "1" and pcbnew.ToMM(p.GetBoundingBox().GetBottom()) > fy)
    jog = round((x_left + x_right) / 2, 3)
    pts = [(fx, fy), (jog, fy), (jog, ry), (rx, ry)]
    for a, c in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(b)
        t.SetStart(V(*a)); t.SetEnd(V(*c)); t.SetWidth(MM(0.2)); t.SetLayer(pcbnew.F_Cu)
        t.SetNet(net("RF_IN")); t.SetLocked(True); b.Add(t)

    # board marking
    for text, pos, layer, size in [("OpenCycle v0.2", (26, 58.0), pcbnew.B_SilkS, 1.4),
                                   ("github.com/Vishvak365/OpenCycle", (26, 60.2), pcbnew.B_SilkS, 0.8),
                                   ("rev A  2026-09", (26, 62.0), pcbnew.B_SilkS, 0.7)]:
        t = pcbnew.PCB_TEXT(b)
        t.SetText(text); t.SetPosition(V(*pos)); t.SetLayer(layer)
        t.SetTextSize(pcbnew.VECTOR2I(MM(size), MM(size))); t.SetTextThickness(MM(size * 0.15))
        t.SetMirrored(layer == pcbnew.B_SilkS)
        b.Add(t)
    return b


if __name__ == "__main__":
    board = build()
    out = HERE / "placed.kicad_pcb"
    board.Save(str(out))
    print("saved", out, "footprints", len(board.GetFootprints()), "nets", board.GetNetCount())
