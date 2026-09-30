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
from check_place import body  # noqa: E402

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
    for d in b.GetDrawings():
        if d.GetClass() == "PCB_TEXT" and d.GetLayer() == silk:
            q = d.GetPosition()
            sz = TM(d.GetTextHeight())
            try:
                f2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", max(8, int(sz * PX * 1.1)))
            except OSError:
                f2 = font
            dc.text(px(TM(q.x), TM(q.y), side), d.GetText(), fill=SILK, font=f2, anchor="mm")
    col.save(OUT / f"pcb_{'front' if side == 'F' else 'back'}_color.png", optimize=True)
    orm.save(OUT / f"pcb_{'front' if side == 'F' else 'back'}_orm.png", optimize=True)


KIND = {
    "U1": ("module", "ESP32-S3 module: UI, logging, Wi-Fi, BLE, native USB"),
    "U2": ("module", "BL652 (nRF52832): ANT+ and BLE sensor bridge"),
    "U3": ("can", "GPS receiver (u-blox MAX-M10S)"),
    "AE1": ("patch", "12 mm ceramic GPS patch antenna (Taoglas)"),
    "U4": ("ic", "Ambient light sensor: auto-dims the backlight"),
    "U5": ("sot223", "3.3 V regulator, 1 A (LDO)"),
    "U6": ("ic", "Li-ion charger, 500 mA"),
    "U7": ("qfn", "Class-D speaker amp (I2S)"),
    "U8": ("lga", "Barometer: altitude and climb"),
    "J1": ("usbc", "USB-C: charging, flashing, data"),
    "J2": ("jst", "Battery connector (JST-PH)"),
    "J3": ("fpc", "Display FFC connector, 40 pins"),
    "J4": ("pads", "Tag-Connect pads: program the BL652"),
    "J5": ("pads", "Tag-Connect pads: ESP32 console / recovery"),
    "D1": ("led", "Charge LED (behind the lens window)"),
    "D2": ("ic", "USB ESD protection"),
    "Q1": ("ic", "Backlight PWM switch"),
    "Q2": ("ic", "Reverse-battery protection"),
    "LS1": ("pads", "Speaker lead pads"),
    "SW1": ("switch", "Left front key"), "SW2": ("switch", "Centre front key"), "SW3": ("switch", "Right front key"),
    "SW4": ("switch", "Left side button: power / back"), "SW5": ("switch", "Right side button: menu"),
}


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
        if ref.startswith("FID"):
            continue
        x0, y0, x1, y1 = body(fp)
        w, h = x1 - x0, y1 - y0
        c = ((x0 + x1) / 2, (y0 + y1) / 2)
        height = notes[ref]["h"] if ref in notes else 1.0
        if ref.startswith(("R", "C")):
            kind = "res" if ref[0] == "R" else "cap"
            desc = {"R": "Resistor", "C": "Capacitor"}[ref[0]]
        else:
            kind, desc = KIND.get(ref, ("ic", ""))
        nets = sorted({p.GetNetname() for p in fp.Pads() if p.GetNetname()})
        rot = fp.GetOrientationDegrees()
        # body box is the courtyard shrunk by 0.35 mm margin
        parts.append(dict(ref=ref, value=fp.GetValue(), side=side, kind=kind, h=height,
                          cx=round(c[0], 3), cy=round(c[1], 3), w=round(max(w, 0.4), 3),
                          d=round(max(h, 0.4), 3), rot=rot, desc=desc,
                          note=notes.get(ref, {}).get("note", ""), mpn=notes.get(ref, {}).get("mpn", ""),
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
    data = dict(board=D.BOARD, holes=D.HOLES, cad_h=D.CAD_H, parts=parts, tracks=tracks, vias=vias, pads=pads,
                unrouted=[])        # DRC: 0 unconnected (pcb/drc_report.txt)
    (OUT / "pcb.json").write_text(json.dumps(data, separators=(",", ":")))
    print("parts", len(parts), "tracks", len(tracks), "vias", len(vias))


if __name__ == "__main__":
    export(sys.argv[1])
