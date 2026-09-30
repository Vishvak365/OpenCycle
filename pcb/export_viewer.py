"""Export board data + realistic textures for the three.js viewer.

Writes ../viewer/pcb.json and ../viewer/pcb_{front,back}_{color,orm}.png
"""
import json
import math
import sys
from pathlib import Path

import pcbnew
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
import design as D  # noqa: E402

TM = pcbnew.ToMM
OUT = Path(__file__).parent.parent / "viewer"
PX = 24                      # pixels per mm
X0, Y0, BW, BH = D.BOARD["x0"], D.BOARD["y0"], D.BOARD["w"], D.BOARD["h"]
Wpx, Hpx = int(BW * PX), int(BH * PX)

MASK = (18, 72, 44)          # green solder mask over bare laminate
MASK_CU = (34, 104, 62)      # mask over copper (lighter)
GOLD = (214, 176, 94)        # ENIG pads
SILK = (236, 238, 230)


def px(x, y, side):
    u = (x - X0) * PX
    if side == "B":
        u = Wpx - u          # texture for the back is seen from behind
    return (u, (y - Y0) * PX)


def poly_pts(ps, side):
    out = []
    for i in range(ps.OutlineCount()):
        o = ps.Outline(i)
        out.append(([px(TM(o.CPoint(j).x), TM(o.CPoint(j).y), side) for j in range(o.PointCount())],
                    [[px(TM(ps.Hole(i, h).CPoint(j).x), TM(ps.Hole(i, h).CPoint(j).y), side)
                      for j in range(ps.Hole(i, h).PointCount())] for h in range(ps.HoleCount(i))]))
    return out


def draw_polys(dr, polys, fill, hole_fill):
    for outer, holes in polys:
        if len(outer) > 2:
            dr.polygon(outer, fill=fill)
        for h in holes:
            if len(h) > 2:
                dr.polygon(h, fill=hole_fill)


def textures(b, side):
    cu = pcbnew.F_Cu if side == "F" else pcbnew.B_Cu
    silk = pcbnew.F_SilkS if side == "F" else pcbnew.B_SilkS
    col = Image.new("RGB", (Wpx, Hpx), MASK)
    orm = Image.new("RGB", (Wpx, Hpx), (255, 90, 0))      # R=ao, G=roughness, B=metalness
    dc, do = ImageDraw.Draw(col), ImageDraw.Draw(orm)
    # copper under mask (zones + tracks)
    for z in b.Zones():
        if not z.GetIsRuleArea() and z.IsOnLayer(cu):
            draw_polys(dc, poly_pts(z.GetFilledPolysList(cu), side), MASK_CU, MASK)
    for t in b.GetTracks():
        if t.GetClass() == "PCB_TRACK" and t.GetLayer() == cu:
            a, c = t.GetStart(), t.GetEnd()
            w = max(1, int(TM(t.GetWidth()) * PX))
            pa, pc = px(TM(a.x), TM(a.y), side), px(TM(c.x), TM(c.y), side)
            dc.line([pa, pc], fill=MASK_CU, width=w)
            for p in (pa, pc):
                dc.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=MASK_CU)
    # slight emboss of copper under mask
    col = Image.blend(col, col.filter(ImageFilter.GaussianBlur(0.8)), 0.35)
    dc = ImageDraw.Draw(col)
    # exposed pads
    for fp in b.GetFootprints():
        for pad in fp.Pads():
            if not pad.IsOnLayer(cu):
                continue
            ps = pcbnew.SHAPE_POLY_SET()
            pad.TransformShapeToPolygon(ps, cu, 0, pcbnew.FromMM(0.005))
            pp = poly_pts(ps, side)
            draw_polys(dc, pp, GOLD, GOLD)
            draw_polys(do, pp, (255, 70, 255), (255, 70, 255))
            if pad.HasHole():
                p = pad.GetPosition(); r = TM(pad.GetDrillSize().x) / 2 * PX
                c = px(TM(p.x), TM(p.y), side)
                dc.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=(20, 20, 18))
    for t in b.GetTracks():
        if t.GetClass() == "PCB_VIA":
            p = t.GetPosition(); c = px(TM(p.x), TM(p.y), side)
            r = TM(t.GetWidth()) / 2 * PX; rd = TM(t.GetDrillValue()) / 2 * PX
            dc.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=MASK_CU)   # tented vias
            dc.ellipse([c[0] - rd, c[1] - rd, c[0] + rd, c[1] + rd], fill=(26, 60, 38))
    # silkscreen: reference designators + outlines
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", int(0.75 * PX))
        big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(1.6 * PX))
    except OSError:
        font = big = ImageFont.load_default()
    for fp in b.GetFootprints():
        on = (fp.GetLayer() == pcbnew.F_Cu) == (side == "F")
        if not on or fp.GetReference().startswith("H"):
            continue
        for g in fp.GraphicalItems():
            if g.GetLayer() == silk and g.GetClass() in ("FP_SHAPE", "PCB_SHAPE"):
                try:
                    ps = pcbnew.SHAPE_POLY_SET()
                    g.TransformShapeToPolygon(ps, silk, 0, pcbnew.FromMM(0.02))
                    draw_polys(dc, poly_pts(ps, side), SILK, SILK)
                except Exception:
                    pass
        cy = fp.GetCourtyard(pcbnew.F_CrtYd if side == "F" else pcbnew.B_CrtYd)
        bb = cy.BBox() if cy.OutlineCount() else fp.GetBoundingBox(False, False)
        x, y = TM(bb.GetX() + bb.GetWidth() // 2), TM(bb.GetBottom()) + 0.25
        p = px(x, y, side)
        dc.text(p, fp.GetReference(), fill=SILK, font=font, anchor="mt")
    if side == "B":
        dc.text(px(23.0, 44.0, side), "OpenCycle", fill=SILK, font=big, anchor="mm")
        dc.text(px(23.0, 47.0, side), "v0.1 CONCEPT - NOT FOR FAB", fill=SILK, font=font, anchor="mm")
    else:
        dc.text(px(26.0, 50.5, side), "OpenCycle v0.1", fill=SILK, font=font, anchor="mm")
    col.save(OUT / f"pcb_{'front' if side == 'F' else 'back'}_color.png", optimize=True)
    orm.save(OUT / f"pcb_{'front' if side == 'F' else 'back'}_orm.png", optimize=True)


KIND = {
    "U1": ("module", 2.2, "nRF52840 Bluetooth + ANT+ module: the brain"),
    "U2": ("can", 2.4, "GPS receiver (u-blox M10)"),
    "AE1": ("patch", 4.0, "15 mm ceramic GPS patch antenna"),
    "U3": ("soic", 1.9, "16 MB flash: rides, routes, map tiles"),
    "J1": ("usbc", 3.2, "USB-C charging and data"),
    "J2": ("jst", 2.9, "Battery connector"),
    "J3": ("fpc", 2.0, "Display ribbon connector"),
    "J4": ("pads", 0.0, "Tag-Connect programming pads"),
    "U4": ("sot", 1.1, "Li-ion charger, 500 mA"),
    "U5": ("sot", 1.1, "3.3 V regulator (LDO)"),
    "U6": ("sot", 1.0, "5 V boost for the display"),
    "L1": ("inductor", 1.2, "Boost inductor 4.7 uH"),
    "D1": ("sot", 1.1, "USB ESD protection"),
    "D2": ("led", 0.6, "Charge LED"),
    "U12": ("lga", 0.8, "Barometer: altitude and climb"),
    "U13": ("lga", 1.0, "Accelerometer: wake on motion"),
    "U14": ("qfn", 0.75, "Class-D speaker amp (I2S)"),
    "LS1": ("pads", 0.0, "Speaker lead pads"),
}
for i in range(7, 12):
    KIND[f"U{i}"] = ("sot", 1.0, "3.3 V to 5 V level shifter for the display")
for sw, t in (("SW1", "Page / lap button"), ("SW2", "Start / stop button"), ("SW3", "Power button")):
    KIND[sw] = ("switch", 3.5, t)


def export(board_path):
    b = pcbnew.LoadBoard(board_path)
    for s in ("F", "B"):
        textures(b, s)
    parts = []
    notes = {p["ref"]: p for p in D.PARTS}
    for fp in b.GetFootprints():
        ref = fp.GetReference()
        if ref.startswith("H"):
            continue
        side = "F" if fp.GetLayer() == pcbnew.F_Cu else "B"
        # body size from pads + courtyard, in footprint-local orientation
        cy = fp.GetCourtyard(pcbnew.F_CrtYd if side == "F" else pcbnew.B_CrtYd)
        bb = cy.BBox() if cy.OutlineCount() else fp.GetBoundingBox(False, False)
        w, h = TM(bb.GetWidth()), TM(bb.GetHeight())
        c = (TM(bb.GetX() + bb.GetWidth() // 2), TM(bb.GetY() + bb.GetHeight() // 2))
        if ref.startswith(("R", "C")):
            kind, height = ("res" if ref[0] == "R" else "cap"), (0.35 if "0402" in fp.GetFPIDAsString() else 0.8)
            desc = {"R": "Resistor", "C": "Capacitor"}[ref[0]]
        else:
            kind, height, desc = KIND.get(ref, ("ic", 1.0, ""))
        nets = sorted({p.GetNetname() for p in fp.Pads() if p.GetNetname()})
        rot = fp.GetOrientationDegrees()
        # body box is the courtyard shrunk by 0.35 mm margin
        parts.append(dict(ref=ref, value=fp.GetValue(), side=side, kind=kind, h=height,
                          cx=round(c[0], 3), cy=round(c[1], 3), w=round(max(w - 0.7, 0.4), 3),
                          d=round(max(h - 0.7, 0.4), 3), rot=rot, desc=desc,
                          note=notes.get(ref, {}).get("note", ""), mpn=notes.get(ref, {}).get("value", ""),
                          nets=nets))
    tracks = []
    for t in b.GetTracks():
        if t.GetClass() == "PCB_TRACK":
            a, c = t.GetStart(), t.GetEnd()
            tracks.append([t.GetNetname(), "F" if t.GetLayer() == pcbnew.F_Cu else "B",
                           round(TM(a.x), 3), round(TM(a.y), 3), round(TM(c.x), 3), round(TM(c.y), 3),
                           round(TM(t.GetWidth()), 3)])
    vias = [[t.GetNetname(), round(TM(t.GetPosition().x), 3), round(TM(t.GetPosition().y), 3)]
            for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]
    pads = []
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if p.GetNetname():
                q = p.GetPosition()
                side = "F" if p.IsOnLayer(pcbnew.F_Cu) else "B"
                pads.append([p.GetNetname(), fp.GetReference(), p.GetNumber(), side,
                             round(TM(q.x), 3), round(TM(q.y), 3)])
    unrouted = json.loads((Path(board_path).parent / "routed.unrouted.json").read_text())
    data = dict(board=D.BOARD, holes=D.HOLES, parts=parts, tracks=tracks, vias=vias, pads=pads,
                unrouted=[u[1] for u in unrouted])
    (OUT / "pcb.json").write_text(json.dumps(data, separators=(",", ":")))
    print("parts", len(parts), "tracks", len(tracks), "vias", len(vias))


if __name__ == "__main__":
    export(sys.argv[1])
