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
IO = pcbnew.PCB_IO() if hasattr(pcbnew, "PCB_IO") else pcbnew.PCB_PLUGIN()


def _rect(fp, layer, x0, y0, x1, y1, w):
    r = pcbnew.FP_SHAPE(fp)
    r.SetShape(pcbnew.SHAPE_T_RECT)
    r.SetStart(V(x0, y0)); r.SetEnd(V(x1, y1))
    r.SetLayer(layer); r.SetWidth(MM(w))
    fp.Add(r)


def _pad(fp, num, x, y, w, h, shape=pcbnew.PAD_SHAPE_ROUNDRECT, ratio=0.1, mask_margin=None, paste=True):
    pad = pcbnew.PAD(fp)
    pad.SetNumber(num)
    pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    pad.SetShape(shape)
    if shape == pcbnew.PAD_SHAPE_ROUNDRECT:
        pad.SetRoundRectRadiusRatio(ratio)
    pad.SetSize(pcbnew.VECTOR2I(MM(w), MM(h)))
    ls = pad.SMDMask()
    if not paste:
        ls.RemoveLayer(pcbnew.F_Paste)
    pad.SetLayerSet(ls)
    pad.SetPosition(V(x, y))
    if mask_margin is not None:
        pad.SetLocalSolderMaskMargin(MM(mask_margin))
    fp.Add(pad)
    return pad


def _fp(name, ref):
    fp = pcbnew.FOOTPRINT(None)
    fp.SetFPID(pcbnew.LIB_ID("OpenCycle", name))
    fp.SetReference(ref); fp.SetValue(name)
    return fp


def taoglas_patch_fp():
    """Taoglas DSGP.1575.12.4.A.02 land pattern (datasheet §6.5): eight 3x3 mm ground pads on a 4.5 mm grid,
    a 2x2 mm feed pad with a 0.5 mm copper keep-out ring. Antenna centre at the origin, feed toward +y."""
    fp = _fp("Taoglas_DSGP.1575.12.4.A.02_12x12mm", "AE**")
    grid = [(-4.5, -4.5, "2"), (0, -4.5, "3"), (4.5, -4.5, "4"), (-4.5, 0, "5"), (0, 0, "6"), (4.5, 0, "7"),
            (-4.5, 4.5, "8"), (4.5, 4.5, "9")]
    for x, y, n in grid:
        _pad(fp, n, x, y, 3.0, 3.0, ratio=0.05)
    _pad(fp, "1", 0, 4.9, 2.0, 2.0, ratio=0.05)
    # copper keep-out around the feed (all copper layers of this side)
    z = (pcbnew.FP_ZONE if hasattr(pcbnew, "FP_ZONE") else pcbnew.ZONE)(fp)
    z.SetIsRuleArea(True)
    z.SetDoNotAllowCopperPour(True); z.SetDoNotAllowTracks(False); z.SetDoNotAllowVias(True)
    z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
    z.SetLayer(pcbnew.F_Cu)
    ol = z.Outline(); ol.NewOutline()
    for x, y in [(-1.5, 3.4), (1.5, 3.4), (1.5, 6.4), (-1.5, 6.4)]:
        ol.Append(MM(x), MM(y))
    fp.Add(z)
    for layer, half, w in [(pcbnew.F_Fab, 6.0, 0.1), (pcbnew.F_SilkS, 6.2, 0.12), (pcbnew.F_CrtYd, 6.25, 0.05)]:
        _rect(fp, layer, -half, -half, half, half, w)
    t = pcbnew.FP_TEXT(fp); t.SetText("FEED"); t.SetPosition(V(0, 6.9)); t.SetLayer(pcbnew.F_Fab)
    t.SetTextSize(pcbnew.VECTOR2I(MM(0.6), MM(0.6))); fp.Add(t)
    IO.FootprintSave(str(LOCAL_LIB), fp)


def bmp581_fp():
    """Bosch BMP581 LGA-10 2.0x2.0 mm, land pattern per datasheet §8.2 (package pads +25 um per side),
    top view. Pin 1 top-left. No solder mask under the sensor (mask opening over the whole body)."""
    fp = _fp("Bosch_LGA-10_2x2mm_P0.5mm_BMP581", "U**")
    row = (0.30, 0.325)      # top/bottom row pads: w x h
    col = (0.325, 0.30)      # side pads
    P = 0.7625
    pads = {"8": (0.5, -P, row), "9": (0.0, -P, row), "10": (-0.5, -P, row),
            "1": (-P, -0.25, col), "2": (-P, 0.25, col),
            "3": (-0.5, P, row), "4": (0.0, P, row), "5": (0.5, P, row),
            "7": (P, -0.25, col), "6": (P, 0.25, col)}
    for n, (x, y, (w, h)) in pads.items():
        _pad(fp, n, x, y, w, h, shape=pcbnew.PAD_SHAPE_RECT, mask_margin=0.02)
    _rect(fp, pcbnew.F_Fab, -1.0, -1.0, 1.0, 1.0, 0.1)
    _rect(fp, pcbnew.F_CrtYd, -1.3, -1.3, 1.3, 1.3, 0.05)
    s = pcbnew.FP_SHAPE(fp); s.SetShape(pcbnew.SHAPE_T_CIRCLE); s.SetCenter(V(-1.35, -1.05)); s.SetEnd(V(-1.25, -1.05))
    s.SetLayer(pcbnew.F_SilkS); s.SetWidth(MM(0.12)); fp.Add(s)
    IO.FootprintSave(str(LOCAL_LIB), fp)


def speaker_pads_fp():
    fp = _fp("SpeakerPads_2.6mm", "LS**")
    for i, x in enumerate((-1.3, 1.3), 1):
        _pad(fp, str(i), x, 0, 1.8, 2.2, ratio=0.25, paste=False)
    _rect(fp, pcbnew.F_CrtYd, -2.6, -1.5, 2.6, 1.5, 0.05)
    t = pcbnew.FP_TEXT(fp); t.SetText("+"); t.SetPosition(V(-1.3, -2.0)); t.SetLayer(pcbnew.F_SilkS)
    t.SetTextSize(pcbnew.VECTOR2I(MM(0.8), MM(0.8))); fp.Add(t)
    IO.FootprintSave(str(LOCAL_LIB), fp)


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
    LOCAL_LIB.mkdir(exist_ok=True)
    taoglas_patch_fp(); bmp581_fp(); speaker_pads_fp()
    b = pcbnew.BOARD()
    b.SetCopperLayerCount(4)
    ds = b.GetDesignSettings()
    ds.SetBoardThickness(MM(D.BOARD["thickness"]))
    ds.m_TrackMinWidth = MM(0.127)
    ds.m_MinClearance = MM(0.127)
    ds.m_ViasMinSize = MM(0.45)
    ds.m_MinThroughDrill = MM(0.25)
    ds.m_CopperEdgeClearance = MM(0.3)
    ds.m_HoleClearance = MM(0.2)
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
        # the library ESP32 footprint carries a 48 x 21 mm antenna keep-out; design.py defines an edge keep-out instead
        for z in list(fp.Zones()):
            if p["ref"] == "U1":
                fp.Remove(z)
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
        fp.Reference().SetTextSize(pcbnew.VECTOR2I(MM(0.6), MM(0.6)))
        fp.Reference().SetTextThickness(MM(0.1))
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
        rule_area(b, k["rect"], [pcbnew.F_Cu], k["name"], pour=False)
    for k in D.NO_TRACKS_B:
        rule_area(b, k["rect"], [pcbnew.B_Cu], k["name"], pour=True)

    # RF feed: patch feed pad -> MAX-M10S RF_IN, short 0.2 mm trace on F.Cu (hand-placed, marked locked)
    feed = next(p for p in b.FindFootprintByReference("AE1").Pads() if p.GetNumber() == "1").GetPosition()
    rfin = next(p for p in b.FindFootprintByReference("U3").Pads() if p.GetNumber() == "11").GetPosition()
    fx, fy, rx, ry = (pcbnew.ToMM(v) for v in (feed.x, feed.y, rfin.x, rfin.y))
    pts = [(fx, fy), (fx - 0.6, fy), (rx + 0.6 + abs(ry - fy) * 0 , fy)]
    # a 45-degree jog from the feed row to the RF_IN row
    mid_x = rx + 0.6 + abs(ry - fy)
    pts = [(fx, fy), (mid_x, fy), (rx + 0.6, ry), (rx, ry)] if mid_x < fx else [(fx, fy), (rx, ry)]
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
