"""Fan out every SMD pad on the plane nets (GND, +3V3) to its inner plane with a short stub and a via.

Freerouting does not reliably drop vias from small SMD pads to planes, so this runs before autorouting.
For each pad it tries via positions around the pad (8 directions, growing distance) and keeps the first
one with clearance to every other-net pad, via and track, outside the via keep-outs. Stubs and vias are
locked so the autorouter leaves them alone.

python fanout.py in.kicad_pcb out.kicad_pcb
"""
import math
import sys
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).parent))
import design as D  # noqa: E402

TM, MM = pcbnew.ToMM, pcbnew.FromMM
VIA_D, VIA_DRILL, STUB = 0.5, 0.3, 0.25
CLR = 0.2                     # a little above the 0.15 mm rule
SKIP_REFS = {"AE1"}           # patch ground pads join the F.Cu pour; stitching vias are added under the patch instead


def rect(item, grow=0.0):
    bb = item.GetBoundingBox()
    return (TM(bb.GetX()) - grow, TM(bb.GetY()) - grow, TM(bb.GetRight()) + grow, TM(bb.GetBottom()) + grow)


def pt_in(r, x, y):
    return r[0] <= x <= r[2] and r[1] <= y <= r[3]


def seg_hits(r, a, b, steps=12):
    return any(pt_in(r, a[0] + (b[0] - a[0]) * k / steps, a[1] + (b[1] - a[1]) * k / steps) for k in range(steps + 1))


def rect_hits_circle(r, x, y, rad):
    cx = min(max(x, r[0]), r[2]); cy = min(max(y, r[1]), r[3])
    return math.hypot(cx - x, cy - y) < rad


def main(src, dst):
    b = pcbnew.LoadBoard(src)
    x0, y0 = D.BOARD["x0"], D.BOARD["y0"]
    x1, y1 = x0 + D.BOARD["w"], y0 + D.BOARD["h"]
    pads = [p for f in b.GetFootprints() for p in f.Pads()]
    no_via = [k["rect"] for k in D.KEEPOUTS] + [k["rect"] for k in D.NO_TRACKS_B]
    no_track_f = [k["rect"] for k in D.NO_TRACKS_F]
    no_track_b = [k["rect"] for k in D.NO_TRACKS_B]
    holes = [(hx, hy) for hx, hy in D.HOLES]
    vias = [(TM(t.GetPosition().x), TM(t.GetPosition().y), t.GetNetname()) for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]
    tracks = [(TM(t.GetStart().x), TM(t.GetStart().y), TM(t.GetEnd().x), TM(t.GetEnd().y), TM(t.GetWidth()), t.GetNetname(),
               t.GetLayer()) for t in b.GetTracks() if t.GetClass() != "PCB_VIA"]
    added = failed = 0
    fails = []
    # escapes for boxed-in signal pads: straight out, away from the part centre, then a via
    for ref, num, sw, direction in D.ESCAPES:
        f = b.FindFootprintByReference(ref)
        p = next(q for q in f.Pads() if q.GetNumber() == num)
        c, fc = p.GetPosition(), f.GetPosition()
        dx, dy = TM(c.x - fc.x), TM(c.y - fc.y)
        if direction:
            ux, uy = direction
        elif abs(dx) >= abs(dy):
            ux, uy = (1 if dx > 0 else -1), 0
        else:
            ux, uy = 0, (1 if dy > 0 else -1)
        L = 1.25
        vx, vy = TM(c.x) + ux * L, TM(c.y) + uy * L
        layer = pcbnew.F_Cu if p.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
        t = pcbnew.PCB_TRACK(b)
        t.SetStart(c); t.SetEnd(pcbnew.VECTOR2I(MM(vx), MM(vy))); t.SetWidth(MM(sw)); t.SetLayer(layer)
        t.SetNet(p.GetNet()); t.SetLocked(True); b.Add(t)
        v = pcbnew.PCB_VIA(b)
        v.SetPosition(pcbnew.VECTOR2I(MM(vx), MM(vy))); v.SetWidth(MM(0.45)); v.SetDrill(MM(0.25))
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(p.GetNet()); v.SetLocked(True); b.Add(v)
        vias.append((vx, vy, p.GetNetname()))
        tracks.append((TM(c.x), TM(c.y), vx, vy, sw, p.GetNetname(), layer))
    for f in b.GetFootprints():
        if f.GetReference() in SKIP_REFS:
            continue
        for p in f.Pads():
            net = p.GetNetname()
            if net not in D.PLANE_NETS or p.GetAttribute() not in (pcbnew.PAD_ATTRIB_SMD, pcbnew.PAD_ATTRIB_CONN):
                continue
            pr0 = rect(p)
            if f.GetReference() == "U5" and (pr0[2] - pr0[0]) * (pr0[3] - pr0[1]) > 6.0:
                continue          # regulator tab: gets in-pad thermal vias below
            layer = pcbnew.F_Cu if p.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
            cx, cy = TM(p.GetPosition().x), TM(p.GetPosition().y)
            pr = rect(p)
            hw, hh = (pr[2] - pr[0]) / 2, (pr[3] - pr[1]) / 2
            fc = f.GetPosition()
            away = math.atan2(cy - TM(fc.y), cx - TM(fc.x))
            dirs = sorted(range(8), key=lambda k: abs(math.remainder(k * math.pi / 4 - away, 2 * math.pi)))
            best = None
            for extra in (0.45, 0.6, 0.8, 1.0, 1.3, 1.6, 2.0):
                for k in dirs:
                    a = k * math.pi / 4
                    dx, dy = math.cos(a), math.sin(a)
                    # distance from the pad centre to its edge in this direction, plus clearance for the via
                    t_edge = min(hw / abs(dx) if abs(dx) > 1e-6 else 1e9, hh / abs(dy) if abs(dy) > 1e-6 else 1e9)
                    vx, vy = cx + dx * (t_edge + extra), cy + dy * (t_edge + extra)
                    if not (x0 + 0.6 <= vx <= x1 - 0.6 and y0 + 0.6 <= vy <= y1 - 0.6):
                        continue
                    if any(pt_in(r, vx, vy) or rect_hits_circle(r, vx, vy, VIA_D / 2) for r in no_via):
                        continue
                    if any(math.hypot(vx - hx, vy - hy) < 2.6 for hx, hy in holes):
                        continue
                    ok = True
                    for q in pads:
                        if q.GetNetname() == net and q.GetParent().GetReference() == f.GetReference():
                            continue
                        r = rect(q)
                        if rect_hits_circle(r, vx, vy, VIA_D / 2 + CLR) and q.GetNetname() != net:
                            ok = False; break
                        if q.GetNetname() != net and q.IsOnLayer(layer) and seg_hits(rect(q, STUB / 2 + CLR), (cx, cy), (vx, vy)) \
                                and q is not p:
                            ok = False; break
                        if q.GetNetname() == net and rect_hits_circle(r, vx, vy, VIA_D / 2 + 0.05):
                            ok = False; break        # no via-in-pad
                    if not ok:
                        continue
                    if any(math.hypot(vx - ux, vy - uy) < VIA_D + CLR for ux, uy, _ in vias):
                        continue
                    if any(_seg_dist((vx, vy), (tx1, ty1), (tx2, ty2)) < VIA_D / 2 + tw / 2 + CLR
                           for tx1, ty1, tx2, ty2, tw, tn, tl in tracks if tn != net):
                        continue
                    stub_rects = no_track_f if layer == pcbnew.F_Cu else no_track_b
                    if any(seg_hits(r, (cx, cy), (vx, vy)) for r in stub_rects):
                        continue
                    best = (vx, vy)
                    break
                if best:
                    break
            if not best:
                failed += 1; fails.append(f"{f.GetReference()}.{p.GetNumber()} {net}")
                continue
            vx, vy = best
            t = pcbnew.PCB_TRACK(b)
            t.SetStart(p.GetPosition()); t.SetEnd(pcbnew.VECTOR2I(MM(vx), MM(vy)))
            t.SetWidth(MM(STUB)); t.SetLayer(layer); t.SetNet(p.GetNet()); t.SetLocked(True); b.Add(t)
            v = pcbnew.PCB_VIA(b)
            v.SetPosition(pcbnew.VECTOR2I(MM(vx), MM(vy))); v.SetWidth(MM(VIA_D)); v.SetDrill(MM(VIA_DRILL))
            v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetViaType(pcbnew.VIATYPE_THROUGH)
            v.SetNet(p.GetNet()); v.SetLocked(True); b.Add(v)
            vias.append((vx, vy, net))
            tracks.append((cx, cy, vx, vy, STUB, net, layer))
            added += 1
    # SOT-223 regulator tab: three thermal vias inside the tab pad
    for f in b.GetFootprints():
        if f.GetReference() != "U5":
            continue
        tab = max(f.Pads(), key=lambda q: (rect(q)[2] - rect(q)[0]) * (rect(q)[3] - rect(q)[1]))
        c = tab.GetPosition()
        for dx, dy in ((0, -1.0), (0, 0), (0, 1.0)):
            v = pcbnew.PCB_VIA(b)
            v.SetPosition(pcbnew.VECTOR2I(c.x + MM(dx), c.y + MM(dy))); v.SetWidth(MM(VIA_D)); v.SetDrill(MM(VIA_DRILL))
            v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(tab.GetNet()); v.SetLocked(True); b.Add(v)
    # stitching vias under the patch ground (between its ground pads), tying the F.Cu pour to the In1 plane
    ae = b.FindFootprintByReference("AE1")
    gnd = b.FindNet("GND")
    ac = ae.GetPosition()
    for dx, dy in ((-2.25, -2.25), (2.25, -2.25), (-2.25, 2.25), (2.25, 2.25)):
        vx, vy = TM(ac.x) + dx, TM(ac.y) + dy
        # through-via: must clear every non-GND pad on BOTH sides (the ESP32 sits behind the patch)
        if any(q.GetNetname() != "GND" and rect_hits_circle(rect(q), vx, vy, VIA_D / 2 + CLR) for q in pads):
            continue
        v = pcbnew.PCB_VIA(b)
        v.SetPosition(pcbnew.VECTOR2I(ac.x + MM(dx), ac.y + MM(dy))); v.SetWidth(MM(VIA_D)); v.SetDrill(MM(VIA_DRILL))
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(gnd); v.SetLocked(True); b.Add(v)
    b.Save(dst)
    print(f"fan-out: {added} vias, {failed} pads without a spot")
    for s in fails:
        print("  no spot:", s)


def _seg_dist(p, a, c):
    ax, ay = a; cx, cy = c; px, py = p
    L2 = (cx - ax) ** 2 + (cy - ay) ** 2
    t = 0 if L2 == 0 else max(0, min(1, ((px - ax) * (cx - ax) + (py - ay) * (cy - ay)) / L2))
    return math.hypot(px - (ax + t * (cx - ax)), py - (ay + t * (cy - ay)))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
