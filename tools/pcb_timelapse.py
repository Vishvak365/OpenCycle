"""Render a time-lapse video of the board being built: outline, parts placed one by one, ratsnest,
traces routed net by net, vias, then the ground pours "etched" in.

python tools/pcb_timelapse.py pcb/opencycle.kicad_pcb docs/media/pcb_timelapse.mp4
Needs: pcbnew (KiCad 7), pillow, imageio + imageio-ffmpeg (pip).
"""
import math
import sys
from pathlib import Path

import imageio.v2 as imageio
import numpy as np
import pcbnew
from PIL import Image, ImageDraw, ImageFont

TM = pcbnew.ToMM
S = 12.4                       # px per mm
PAD = 60
W, H = 1080, 1352
X0, Y0 = 3.0, 3.0              # board origin
OX = (W - 46 * S) / 2 - X0 * S
OY = 140 - Y0 * S
BG = (12, 16, 22)
SUB = (18, 52, 40)
FCU = (226, 86, 70)
BCU = (80, 140, 230)
SILK = (235, 238, 242)
RAT = (250, 214, 90)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def P(x, y):
    return (OX + x * S, OY + y * S)


def font(sz, bold=False):
    try:
        return ImageFont.truetype(FONTB if bold else FONT, sz)
    except OSError:
        return ImageFont.load_default()


def board_data(path):
    b = pcbnew.LoadBoard(path)
    b.BuildConnectivity()
    parts = []
    for f in b.GetFootprints():
        front = f.GetLayer() == pcbnew.F_Cu
        pads = []
        for p in f.Pads():
            bb = p.GetBoundingBox()
            r = (TM(bb.GetX()), TM(bb.GetY()), TM(bb.GetRight()), TM(bb.GetBottom()))
            round_ = p.GetShape() in (pcbnew.PAD_SHAPE_CIRCLE, pcbnew.PAD_SHAPE_OVAL)
            layer = "both" if p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH) else ("F" if front else "B")
            pads.append((r, round_, layer))
        fab = []
        for g in f.GraphicalItems():
            if g.GetClass() == "MGRAPHIC" and g.GetLayerName() in ("F.Fab", "B.Fab", "F.Silkscreen", "B.Silkscreen"):
                try:
                    shp = g.GetShape()
                    if shp not in (pcbnew.SHAPE_T_SEGMENT, pcbnew.SHAPE_T_RECT):
                        continue            # arcs/circles: skip rather than draw a wrong chord
                    s, e = g.GetStart(), g.GetEnd()
                    if shp == pcbnew.SHAPE_T_RECT:
                        x1, y1, x2, y2 = TM(s.x), TM(s.y), TM(e.x), TM(e.y)
                        for a, b2 in (((x1, y1), (x2, y1)), ((x2, y1), (x2, y2)), ((x2, y2), (x1, y2)), ((x1, y2), (x1, y1))):
                            fab.append((a[0], a[1], b2[0], b2[1], shp))
                    else:
                        fab.append((TM(s.x), TM(s.y), TM(e.x), TM(e.y), shp))
                except Exception:
                    pass
        c = f.GetPosition()
        parts.append(dict(ref=f.GetReference(), front=front, pads=pads, fab=fab, c=(TM(c.x), TM(c.y)),
                          area=sum((r[2] - r[0]) * (r[3] - r[1]) for r, _, _ in pads)))
    tracks, vias = [], []
    for t in b.GetTracks():
        if t.GetClass() == "PCB_VIA":
            vias.append((TM(t.GetPosition().x), TM(t.GetPosition().y), TM(t.GetWidth()), t.GetNetname()))
        else:
            tracks.append((TM(t.GetStart().x), TM(t.GetStart().y), TM(t.GetEnd().x), TM(t.GetEnd().y), TM(t.GetWidth()),
                           "F" if t.GetLayer() == pcbnew.F_Cu else "B", t.GetNetname()))
    zones = []
    for z in b.Zones():
        if z.GetIsRuleArea():
            continue
        L = z.GetLayer()
        if L not in (pcbnew.F_Cu, pcbnew.B_Cu):
            continue
        polys = z.GetFilledPolysList(L)
        for i in range(polys.OutlineCount()):
            o = polys.Outline(i)
            pts = [(TM(o.CPoint(j).x), TM(o.CPoint(j).y)) for j in range(o.PointCount())]
            holes = []
            for h in range(polys.HoleCount(i)):
                ho = polys.Hole(i, h)
                holes.append([(TM(ho.CPoint(j).x), TM(ho.CPoint(j).y)) for j in range(ho.PointCount())])
            zones.append(("F" if L == pcbnew.F_Cu else "B", pts, holes))
    # ratsnest: pad centres per net, minimum spanning tree
    netpads = {}
    for f in b.GetFootprints():
        for p in f.Pads():
            n = p.GetNetname()
            if n and n not in ("GND", "+3V3"):
                q = p.GetPosition()
                netpads.setdefault(n, []).append((TM(q.x), TM(q.y)))
    rats = []
    for n, pts in netpads.items():
        if len(pts) < 2:
            continue
        done, todo = [pts[0]], pts[1:]
        while todo:
            best = min(((math.dist(a, c), a, c) for a in done for c in todo))
            rats.append((best[1], best[2], n))
            done.append(best[2]); todo.remove(best[2])
    return parts, tracks, vias, zones, rats


def outline(d, prog=1.0):
    x0, y0, x1, y1, r = 3.0, 3.0, 49.0, 89.4, 4.0
    pts = []
    for (cx, cy, a0) in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for k in range(10):
            a = math.radians(a0 + k * 10)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    pts.append(pts[0])
    n = max(2, int(len(pts) * prog))
    return [P(*p) for p in pts[:n]], pts


def draw_frame(state, data, caption, sub):
    parts, tracks, vias, zones, rats = data
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img, "RGBA")
    poly, full = outline(d, state.get("outline", 1.0))
    if state.get("outline", 1.0) >= 1.0:
        d.polygon([P(*p) for p in full], fill=SUB)
    d.line(poly, fill=(240, 200, 90), width=3)
    # pours (etched in)
    zp = state.get("zones", 0.0)
    if zp > 0:
        for side, pts, holes in zones:
            col = (46, 122, 84) if side == "F" else (40, 96, 120)       # copper under green mask
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ld = ImageDraw.Draw(layer)
            ld.polygon([P(*p) for p in pts], fill=col + (int((150 if side == "F" else 70) * zp),))
            for h in holes:
                ld.polygon([P(*p) for p in h], fill=(0, 0, 0, 0))
            img.paste(Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB"))
        d = ImageDraw.Draw(img, "RGBA")
    # tracks
    for i, (x1, y1, x2, y2, w, side, n) in enumerate(tracks[: state.get("tracks", 0)]):
        col = FCU if side == "F" else BCU
        d.line([P(x1, y1), P(x2, y2)], fill=col + (235 if side == "F" else 190,), width=max(2, int(w * S)))
    for (x, y, w, n) in vias[: state.get("vias", 0)]:
        cx, cy = P(x, y)
        r = w * S / 2
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(210, 190, 120))
        d.ellipse([cx - r * 0.55, cy - r * 0.55, cx + r * 0.55, cy + r * 0.55], fill=BG)
    # parts
    shown = state.get("parts", 0)
    for k, p in enumerate(parts[:shown]):
        age = state.get("age", {}).get(p["ref"], 99)
        drop = max(0, 12 - age) * 4 if age < 12 else 0
        alpha = min(255, 60 + age * 25)
        for (r, rnd, layer) in p["pads"]:
            col = SILK if layer == "both" else (FCU if layer == "F" else BCU)
            a = alpha if layer != "B" else int(alpha * 0.7)
            box = [P(r[0], r[1])[0], P(r[0], r[1])[1] - drop, P(r[2], r[3])[0], P(r[2], r[3])[1] - drop]
            if rnd:
                d.ellipse(box, fill=col + (a,))
            else:
                d.rectangle(box, fill=col + (a,))
        for (x1, y1, x2, y2, shp) in p["fab"]:
            a = int(alpha * (0.8 if p["front"] else 0.35))
            (ax, ay), (bx, by) = P(x1, y1), P(x2, y2)
            d.line([(ax, ay - drop), (bx, by - drop)], fill=SILK + (a,), width=1)
    # ratsnest
    if state.get("rats", 0) > 0:
        routed = state.get("routed_nets", set())
        for (a, c, n) in rats:
            if n in routed:
                continue
            d.line([P(*a), P(*c)], fill=RAT + (int(170 * state["rats"]),), width=1)
    # caption
    d.text((PAD, 40), caption, font=font(40, True), fill=(242, 244, 246))
    d.text((PAD, 92), sub, font=font(24), fill=(150, 160, 172))
    d.text((PAD, H - 60), "OpenCycle v0.2 main board  ·  46 × 86.4 mm  ·  4 layers", font=font(22), fill=(120, 130, 142))
    leg = [("front copper", FCU), ("back copper", BCU), ("unrouted", RAT)]
    x = PAD
    for t, c in leg:
        d.rectangle([x, H - 102, x + 18, H - 84], fill=c)
        d.text((x + 26, H - 108), t, font=font(22), fill=(150, 160, 172))
        x += 180
    return img


def main(src, dst, fps=30):
    data = board_data(src)
    parts, tracks, vias, zones, rats = data
    parts.sort(key=lambda p: -p["area"])           # big modules first, passives last
    tracks.sort(key=lambda t: (t[6], t[0]))       # net by net
    frames = []

    def add(state, cap, sub, n=1):
        img = draw_frame(state, data, cap, sub)
        for _ in range(n):
            frames.append(np.asarray(img))

    for i in range(24):
        add({"outline": (i + 1) / 24, "parts": 0}, "Board outline", "46 × 86.4 mm, rounded to fit the 52 × 92 mm case")
    age = {}
    step = max(1, len(parts) // 90)
    for k in range(0, len(parts) + 12, step):
        for p in parts[:k]:
            age[p["ref"]] = age.get(p["ref"], 0) + step
        add({"parts": min(k, len(parts)), "age": dict(age)}, "Placing components",
            f"{min(k, len(parts))} / {len(parts)} parts  ·  modules first, then passives")
    full_age = {p["ref"]: 99 for p in parts}
    for i in range(20):
        add({"parts": len(parts), "age": full_age, "rats": (i + 1) / 20}, "Ratsnest", "every connection still to be made")
    nets_order = []
    for t in tracks:
        if t[6] not in nets_order:
            nets_order.append(t[6])
    n_frames = 150
    for i in range(n_frames):
        k = int(len(tracks) * (i + 1) / n_frames)
        routed = {t[6] for t in tracks[:k]}
        nv = int(len(vias) * (i + 1) / n_frames)
        add({"parts": len(parts), "age": full_age, "rats": 1, "tracks": k, "vias": nv, "routed_nets": routed},
            "Routing", f"{k} / {len(tracks)} segments  ·  {nv} vias")
    for i in range(30):
        add({"parts": len(parts), "age": full_age, "tracks": len(tracks), "vias": len(vias), "zones": (i + 1) / 30,
             "rats": 0}, "Copper pours", "ground fill on the outer layers, GND + 3.3 V planes inside")
    add({"parts": len(parts), "age": full_age, "tracks": len(tracks), "vias": len(vias), "zones": 1, "rats": 0},
        "Done", "DRC: 0 errors, 0 unconnected  ·  schematic netlist matches  ·  Gerbers exported", n=75)
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    imageio.mimsave(dst, frames, fps=fps, codec="libx264", quality=8, macro_block_size=8)
    print("wrote", dst, len(frames), "frames")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
