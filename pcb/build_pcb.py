"""Build the OpenCycle board from design.py: outline, stackup, footprints, nets.

python build_pcb.py            -> placed.kicad_pcb (placed, unrouted)
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


def patch_antenna_fp():
    """15 x 15 mm ceramic patch with a single feed pin."""
    LOCAL_LIB.mkdir(exist_ok=True)
    fp = pcbnew.FOOTPRINT(None)
    fp.SetFPID(pcbnew.LIB_ID("OpenCycle", "Patch_15x15_Feed"))
    fp.SetReference("AE**")
    fp.SetValue("Patch_15x15_Feed")
    pad = pcbnew.PAD(fp)
    pad.SetNumber("A")
    pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
    pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    pad.SetSize(pcbnew.VECTOR2I(MM(1.6), MM(1.6)))
    pad.SetDrillSize(pcbnew.VECTOR2I(MM(1.0), MM(1.0)))
    pad.SetLayerSet(pad.PTHMask())
    pad.SetPosition(V(0, 1.8))
    fp.Add(pad)
    for layer, half in [(pcbnew.F_Fab, 7.5), (pcbnew.F_SilkS, 7.65), (pcbnew.F_CrtYd, 7.75)]:
        r = pcbnew.FP_SHAPE(fp)
        r.SetShape(pcbnew.SHAPE_T_RECT)
        r.SetStart(V(-half, -half))
        r.SetEnd(V(half, half))
        r.SetLayer(layer)
        r.SetWidth(MM(0.12 if layer != pcbnew.F_CrtYd else 0.05))
        fp.Add(r)
    io = pcbnew.PCB_IO() if hasattr(pcbnew, "PCB_IO") else pcbnew.PCB_PLUGIN()
    io.FootprintSave(str(LOCAL_LIB), fp)
    return fp


def speaker_pads_fp():
    fp = pcbnew.FOOTPRINT(None)
    fp.SetFPID(pcbnew.LIB_ID("OpenCycle", "SpeakerPads_2.6mm"))
    fp.SetReference("LS**"); fp.SetValue("SpeakerPads_2.6mm")
    for i, x in enumerate((-1.3, 1.3), 1):
        pad = pcbnew.PAD(fp)
        pad.SetNumber(str(i)); pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        pad.SetShape(pcbnew.PAD_SHAPE_ROUNDRECT); pad.SetRoundRectRadiusRatio(0.25)
        pad.SetSize(pcbnew.VECTOR2I(MM(1.8), MM(2.2)))
        pad.SetLayerSet(pad.SMDMask()); pad.SetPosition(V(x, 0))
        fp.Add(pad)
    r = pcbnew.FP_SHAPE(fp); r.SetShape(pcbnew.SHAPE_T_RECT)
    r.SetStart(V(-2.6, -1.5)); r.SetEnd(V(2.6, 1.5)); r.SetLayer(pcbnew.F_CrtYd); r.SetWidth(MM(0.05))
    fp.Add(r)
    t = pcbnew.FP_TEXT(fp); t.SetText("+"); t.SetPosition(V(-1.3, -2.0)); t.SetLayer(pcbnew.F_SilkS)
    t.SetTextSize(pcbnew.VECTOR2I(MM(0.8), MM(0.8))); fp.Add(t)
    io = pcbnew.PCB_IO() if hasattr(pcbnew, "PCB_IO") else pcbnew.PCB_PLUGIN()
    io.FootprintSave(str(LOCAL_LIB), fp)


def load_fp(lib, name):
    if lib == "OpenCycle":
        return pcbnew.FootprintLoad(str(LOCAL_LIB), name)
    return pcbnew.FootprintLoad(D.FP + lib + ".pretty", name)


def pin_map(p):
    """symbol pin name/number -> list of pad numbers."""
    by_name = {}
    for num, name, *_ in sym_pins(p["slib"], p["sym"]):
        by_name.setdefault(name, []).append(num)
        by_name.setdefault(num, []).append(num)
    out = {}
    for key, net in p["pins"].items():
        if key not in by_name:
            raise KeyError(f"{p['ref']}: symbol {p['sym']} has no pin '{key}'")
        for num in by_name[key]:
            out[num] = net
    names = {n for n, *_ in sym_pins(p["slib"], p["sym"])}
    missing = names - set(out)
    if missing and p["ref"] != "U1":
        raise KeyError(f"{p['ref']}: pins not assigned {sorted(missing)}")
    return out


def build():
    patch_antenna_fp()
    speaker_pads_fp()
    b = pcbnew.BOARD()
    b.SetCopperLayerCount(4)
    ds = b.GetDesignSettings()
    ds.SetBoardThickness(MM(D.BOARD["thickness"]))
    ds.m_TrackMinWidth = MM(0.15)
    ds.m_MinClearance = MM(0.15)
    ds.m_ViasMinSize = MM(0.45)
    ds.m_MinThroughDrill = MM(0.25)
    ds.m_CopperEdgeClearance = MM(0.3)
    ds.m_HoleClearance = MM(0.09)      # library switch footprints put NPTH pegs 0.1 mm from their pads
    ds.m_HoleToHoleMin = MM(0.25)
    nc = ds.m_NetSettings.m_DefaultNetClass
    nc.SetClearance(MM(0.15))
    nc.SetTrackWidth(MM(0.2))
    nc.SetViaDiameter(MM(0.5))
    nc.SetViaDrill(MM(0.3))
    for i, name in [(pcbnew.In1_Cu, "In1.Cu"), (pcbnew.In2_Cu, "In2.Cu")]:
        b.SetLayerType(i, pcbnew.LT_POWER)

    # outline
    x0, y0, w, h, r = (D.BOARD[k] for k in ("x0", "y0", "w", "h", "r"))
    x1, y1 = x0 + w, y0 + h

    def seg(a, c):
        s = pcbnew.PCB_SHAPE(b)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(V(*a)); s.SetEnd(V(*c))
        s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(MM(0.1)); b.Add(s)

    def arc(c, start, mid_angle_end):
        s = pcbnew.PCB_SHAPE(b)
        s.SetShape(pcbnew.SHAPE_T_ARC)
        s.SetCenter(V(*c)); s.SetStart(V(*start)); s.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(mid_angle_end, pcbnew.DEGREES_T))
        s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(MM(0.1)); b.Add(s)

    seg((x0 + r, y0), (x1 - r, y0)); seg((x1, y0 + r), (x1, y1 - r))
    seg((x1 - r, y1), (x0 + r, y1)); seg((x0, y1 - r), (x0, y0 + r))
    arc((x1 - r, y0 + r), (x1 - r, y0), 90)
    arc((x1 - r, y1 - r), (x1, y1 - r), 90)
    arc((x0 + r, y1 - r), (x0 + r, y1), 90)
    arc((x0 + r, y0 + r), (x0, y0 + r), 90)

    nets = {}

    def net(name):
        if name not in nets:
            n = pcbnew.NETINFO_ITEM(b, name)
            b.Add(n)
            nets[name] = n
        return nets[name]

    for p in D.PARTS:
        fp = load_fp(p["flib"], p["fp"])
        fp.SetReference(p["ref"])
        fp.SetValue(p["value"])
        fp.SetPosition(V(p["x"], p["y"]))
        fp.SetOrientationDegrees(p["rot"])
        if p["lcsc"]:
            fp.SetField("LCSC", p["lcsc"]) if hasattr(fp, "SetField") else None
        pm = pin_map(p)
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

    for i, (hx, hy) in enumerate(D.HOLES, 1):
        fp = load_fp("MountingHole", "MountingHole_2.2mm_M2_Pad_Via")
        fp.SetReference(f"H{i}")
        fp.SetPosition(V(hx, hy))
        for pad in fp.Pads():
            pad.SetNet(net("GND"))
        b.Add(fp)
        fp.Reference().SetVisible(False)

    # board marking
    t = pcbnew.PCB_TEXT(b)
    t.SetText("OpenCycle v0.1")
    t.SetPosition(V(26, 30)); t.SetLayer(pcbnew.B_SilkS)
    t.SetTextSize(pcbnew.VECTOR2I(MM(1.2), MM(1.2))); t.SetTextThickness(MM(0.18))
    t.SetMirrored(True)
    b.Add(t)
    return b


if __name__ == "__main__":
    board = build()
    out = HERE / "placed.kicad_pcb"
    board.Save(str(out))
    print("saved", out, "footprints", len(board.GetFootprints()), "nets", board.GetNetCount())
