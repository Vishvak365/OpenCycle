"""Grid maze router for the OpenCycle board (2 signal layers + GND/3V3 planes).

- 0.1 mm grid, 8-direction moves, vias between F.Cu and B.Cu
- GND and +3V3 pads get a short fan-out track + via to the inner planes
- every other net is routed as a growing tree (pad -> nearest routed copper)
- clearances are enforced with margins above the DRC rule; KiCad DRC is the final check

python router.py in.kicad_pcb out.kicad_pcb [stage]   stage = fanout | power | all
"""
import heapq
import json
import math
import sys
import time
from pathlib import Path

import numba
import numpy as np
import pcbnew
from PIL import Image, ImageDraw
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).parent))
import design as D  # noqa: E402

RES = 0.1
GX0, GY0 = 2.5, 2.5
W, H = int(round(47 / RES)) + 1, int(round(81 / RES)) + 1
CLR = 0.2          # routing clearance (DRC rule is 0.15)
EDGE = 0.35        # copper to board edge
VIA_D, VIA_DRILL = 0.5, 0.3
TRACK = 0.2
FAN_W = 0.25
VIA_COST = 25.0
TM = pcbnew.ToMM
MM = lambda v: pcbnew.FromMM(float(v))
LAYERS = [pcbnew.F_Cu, pcbnew.B_Cu]


def to_px(x, y):
    return (x - GX0) / RES, (y - GY0) / RES


def to_mm(ix, iy):
    return GX0 + ix * RES, GY0 + iy * RES


def disk(r_cells):
    r = int(math.ceil(r_cells))
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    return (xx * xx + yy * yy) <= r_cells * r_cells + 1e-6


def poly_to_pts(ps):
    out = []
    for i in range(ps.OutlineCount()):
        o = ps.Outline(i)
        out.append([to_px(TM(o.CPoint(j).x), TM(o.CPoint(j).y)) for j in range(o.PointCount())])
    return out


def raster(polys):
    img = Image.new("1", (W, H), 0)
    dr = ImageDraw.Draw(img)
    for pts in polys:
        if len(pts) >= 3:
            dr.polygon([(x, y) for x, y in pts], fill=1, outline=1)
    return np.array(img, dtype=bool)


@numba.njit(cache=True)
def astar(block, viaok, starts, target, x0, y0, x1, y1, via_cost, allow_via, tx0, ty0, tx1, ty1):
    L, Hh, Ww = block.shape
    INF = 1e18
    dist = np.full(block.shape, INF)
    par = np.full(block.shape, -1, dtype=np.int64)
    heap = [(0.0, np.int64(0))]
    heap.pop()
    for s in starts:
        l = s // (Hh * Ww); r = s % (Hh * Ww); y = r // Ww; x = r % Ww
        dist[l, y, x] = 0.0
        heapq.heappush(heap, (0.0, s))
    dxs = np.array([1, -1, 0, 0, 1, 1, -1, -1])
    dys = np.array([0, 0, 1, -1, 1, -1, 1, -1])
    cst = np.array([1.0, 1.0, 1.0, 1.0, 1.41421356, 1.41421356, 1.41421356, 1.41421356])
    found = -1
    while len(heap) > 0:
        f, cur = heapq.heappop(heap)
        l = cur // (Hh * Ww); r = cur % (Hh * Ww); y = r // Ww; x = r % Ww
        g = dist[l, y, x]
        # heuristic: octile distance to target bbox
        hx = max(tx0 - x, 0, x - tx1); hy = max(ty0 - y, 0, y - ty1)
        hh = max(hx, hy) + 0.41421356 * min(hx, hy)
        if f > g + hh + 1e-9:
            continue
        if target[l, y, x]:
            found = cur
            break
        # direction of arrival for a small turn penalty
        pd = -1
        p = par[l, y, x]
        if p >= 0:
            pl = p // (Hh * Ww); pr = p % (Hh * Ww); py = pr // Ww; px = pr % Ww
            if pl == l:
                for k in range(8):
                    if px + dxs[k] == x and py + dys[k] == y:
                        pd = k
        for k in range(8):
            nx = x + dxs[k]; ny = y + dys[k]
            if nx < x0 or nx > x1 or ny < y0 or ny > y1:
                continue
            if block[l, ny, nx]:
                continue
            if k >= 4:  # no corner cutting
                if block[l, y, nx] and block[l, ny, x]:
                    continue
            ng = g + cst[k] + (0.35 if (pd >= 0 and pd != k) else 0.0)
            if ng < dist[l, ny, nx]:
                dist[l, ny, nx] = ng
                par[l, ny, nx] = cur
                hx = max(tx0 - nx, 0, nx - tx1); hy = max(ty0 - ny, 0, ny - ty1)
                hh = max(hx, hy) + 0.41421356 * min(hx, hy)
                heapq.heappush(heap, (ng + hh, np.int64(l * Hh * Ww + ny * Ww + nx)))
        if allow_via and viaok[y, x]:
            nl = 1 - l
            if not block[nl, y, x]:
                ng = g + via_cost
                if ng < dist[nl, y, x]:
                    dist[nl, y, x] = ng
                    par[nl, y, x] = cur
                    heapq.heappush(heap, (ng + hh, np.int64(nl * Hh * Ww + y * Ww + x)))
    if found < 0:
        return np.zeros(0, dtype=np.int64)
    path = [found]
    c = found
    while True:
        l = c // (Hh * Ww); r = c % (Hh * Ww); y = r // Ww; x = r % Ww
        p = par[l, y, x]
        if p < 0:
            break
        path.append(p)
        c = p
    out = np.empty(len(path), dtype=np.int64)
    for i in range(len(path)):
        out[i] = path[len(path) - 1 - i]
    return out


class Router:
    def __init__(self, board):
        self.b = board
        self.netcode = {str(n): board.GetNetcodeFromNetname(str(n)) for n in board.GetNetsByName().keys() if str(n)}
        self.cu = np.zeros((2, H, W), dtype=np.int32)       # copper owner per cell
        self.center = np.zeros((2, H, W), dtype=np.int32)   # centreline/pad cells per net
        self.keep = np.zeros((2, H, W), dtype=bool)         # hard keep-outs
        self.smdpads = np.zeros((H, W), dtype=bool)          # any SMD pad (no vias here)
        self.vias = np.zeros((H, W), dtype=bool)             # via centres (hole spacing)
        self.cellpad = {}                                    # flat cell (with layer) -> pad dict
        self.tree = {}
        self.pads = []   # (netname, layers, cells(flat idx list), center mm, pad)
        self.log = []
        self.failed = []
        self._build()

    # ------------------------------------------------------------------ setup
    def _build(self):
        b = self.b
        outline = pcbnew.SHAPE_POLY_SET()
        b.GetBoardPolygonOutlines(outline)
        inside = raster(poly_to_pts(outline))
        dt = ndimage.distance_transform_edt(inside) * RES
        self.edge_dt = dt
        for L in range(2):
            self.keep[L] |= dt < EDGE
        for fp in b.GetFootprints():
            for z in fp.Zones():
                if z.GetIsRuleArea():
                    m = raster(poly_to_pts(z.Outline()))
                    for L, lay in enumerate(LAYERS):
                        if z.IsOnLayer(lay) and (z.GetDoNotAllowTracks() or z.GetDoNotAllowCopperPour()):
                            self.keep[L] |= m
            if fp.GetReference().startswith("AE"):
                # no front copper other than the feed under the patch body
                bb = fp.GetBoundingBox(False, False)
                x0, y0 = to_px(TM(bb.GetX()), TM(bb.GetY()))
                x1, y1 = to_px(TM(bb.GetRight()), TM(bb.GetBottom()))
                self.keep[0, int(y0):int(y1) + 1, int(x0):int(x1) + 1] = True
            for pad in fp.Pads():
                layers = [L for L, lay in enumerate(LAYERS) if pad.IsOnLayer(lay)]
                if pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH or not layers:
                    if pad.HasHole():
                        p = pad.GetPosition()
                        r = TM(pad.GetDrillSize().x) / 2 + CLR
                        cx, cy = to_px(TM(p.x), TM(p.y))
                        yy, xx = np.ogrid[:H, :W]
                        m = (xx - cx) ** 2 + (yy - cy) ** 2 <= (r / RES) ** 2
                        self.keep[0] |= m; self.keep[1] |= m
                    continue
                ps = pcbnew.SHAPE_POLY_SET()
                lay = LAYERS[layers[0]]
                pad.TransformShapeToPolygon(ps, lay, 0, MM(0.005))
                m = raster(poly_to_pts(ps))
                if not m.any():
                    p = pad.GetPosition(); cx, cy = to_px(TM(p.x), TM(p.y))
                    m[int(round(cy)), int(round(cx))] = True
                name = pad.GetNetname()
                code = pad.GetNetCode() if name else -2
                for L in layers:
                    self.cu[L][m] = code
                    if name:
                        self.center[L][m] = code
                if pad.GetAttribute() == pcbnew.PAD_ATTRIB_SMD:
                    self.smdpads |= m
                if name:
                    idx = np.flatnonzero(m)
                    p = pad.GetPosition()
                    pd = dict(net=name, layers=layers, cells=idx,
                              pos=(TM(p.x), TM(p.y)), smd=pad.GetAttribute() == pcbnew.PAD_ATTRIB_SMD,
                              ref=fp.GetReference(), num=pad.GetNumber())
                    self.pads.append(pd)
                    for L in layers:
                        for c in idx:
                            self.cellpad[int(c) + L * H * W] = pd
        self.cu[self.keep] = np.where(self.cu[self.keep] == 0, -1, self.cu[self.keep])

    # ------------------------------------------------------------------ helpers
    def blocked(self, code, width):
        r = (width / 2 + CLR) / RES
        st = disk(r)
        out = np.empty((2, H, W), dtype=bool)
        for L in range(2):
            other = (self.cu[L] != 0) & (self.cu[L] != code)
            out[L] = ndimage.binary_dilation(other, structure=st) | self.keep[L]
            # a track centre must also stay off the board edge by width/2
            out[L] |= self.edge_dt < EDGE + width / 2
            out[L][self.center[L] == code] = False
        return out

    def via_ok(self, code):
        st = disk((VIA_D / 2 + CLR) / RES)
        ok = np.ones((H, W), dtype=bool)
        for L in range(2):
            other = (self.cu[L] != 0) & (self.cu[L] != code)
            ok &= ~ndimage.binary_dilation(other, structure=st)
            ok &= ~self.keep[L]
            ok &= self.edge_dt >= EDGE + VIA_D / 2
        ok &= ~ndimage.binary_dilation(self.smdpads, structure=disk((VIA_D / 2 + 0.1) / RES))
        ok &= ~ndimage.binary_dilation(self.vias, structure=disk(0.62 / RES))
        return ok

    def paint_path(self, code, cells, width):
        """cells: array of flat indices (l,y,x). Paint copper and centreline."""
        L_ = cells // (H * W); r = cells % (H * W); ys = r // W; xs = r % W
        st = disk(width / 2 / RES)
        for L in range(2):
            m = np.zeros((H, W), dtype=bool)
            sel = L_ == L
            m[ys[sel], xs[sel]] = True
            self.center[L][m] = code
            self.cu[L][ndimage.binary_dilation(m, structure=st) & (self.cu[L] == 0)] = code

    def paint_via(self, code, x, y):
        cx, cy = to_px(x, y)
        self.vias[int(round(cy)), int(round(cx))] = True
        yy, xx = np.ogrid[:H, :W]
        m = (xx - cx) ** 2 + (yy - cy) ** 2 <= (VIA_D / 2 / RES) ** 2
        for L in range(2):
            self.cu[L][m & (self.cu[L] == 0)] = code
            self.center[L][m] = code

    # ------------------------------------------------------------------ board output
    def add_track(self, net, L, a, c, width):
        if math.dist(a, c) < 1e-4:
            return
        t = pcbnew.PCB_TRACK(self.b)
        t.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1])))
        t.SetEnd(pcbnew.VECTOR2I(MM(c[0]), MM(c[1])))
        t.SetWidth(MM(width)); t.SetLayer(LAYERS[L])
        t.SetNet(self.b.FindNet(net))
        self.b.Add(t)

    def add_via(self, net, p):
        v = pcbnew.PCB_VIA(self.b)
        v.SetPosition(pcbnew.VECTOR2I(MM(p[0]), MM(p[1])))
        v.SetWidth(MM(VIA_D)); v.SetDrill(MM(VIA_DRILL))
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        v.SetNet(self.b.FindNet(net))
        self.b.Add(v)

    def emit(self, net, path, width, start_pos=None, end_pos=None):
        """Turn a cell path into tracks and vias; merge collinear steps."""
        pts = []
        for c in path:
            L = int(c // (H * W)); r = int(c % (H * W)); y = r // W; x = r % W
            pts.append((L, x, y))
        segs = []
        cur = [pts[0]]
        for p in pts[1:]:
            q = cur[-1]
            if p[0] != q[0]:
                segs.append(cur); cur = [p]; continue
            if len(cur) >= 2:
                d0 = (q[1] - cur[-2][1], q[2] - cur[-2][2]); d1 = (p[1] - q[1], p[2] - q[2])
                if d0 != d1:
                    segs.append(cur); cur = [q, p]; continue
            cur.append(p)
        segs.append(cur)
        # a run of equal-layer segments; via between runs where layer changes
        prev_end = None
        for i, s in enumerate(segs):
            L = s[0][0]
            a = to_mm(s[0][1], s[0][2]); c = to_mm(s[-1][1], s[-1][2])
            if len(s) >= 2:
                self.add_track(net, L, a, c, width)
            if prev_end is not None and prev_end[0] != L:
                self.add_via(net, a)
                self.paint_via(self.netcode[net], *a)
            prev_end = (L, c)
        for cell, (L, x, y) in ((int(path[0]), pts[0]), (int(path[-1]), pts[-1])):
            pd = self.cellpad.get(cell)
            if pd is not None and pd["net"] == net:
                self.add_track(net, L, pd["pos"], to_mm(x, y), min(width, 0.25))

    # ------------------------------------------------------------------ routing
    def search(self, code, starts, target, width, allow_via=True, margin=10.0):
        blk = self.blocked(code, width)
        vok = self.via_ok(code) if allow_via else np.zeros((H, W), dtype=bool)
        tl, ty, tx = np.nonzero(target)
        if len(tx) == 0:
            return None
        sl = starts // (H * W); sr = starts % (H * W); sy = sr // W; sx = sr % W
        for L, yy, xx in zip(sl, sy, sx):
            blk[L, yy, xx] = False
        m = margin / RES
        x0 = int(max(0, min(tx.min(), sx.min()) - m)); x1 = int(min(W - 1, max(tx.max(), sx.max()) + m))
        y0 = int(max(0, min(ty.min(), sy.min()) - m)); y1 = int(min(H - 1, max(ty.max(), sy.max()) + m))
        path = astar(blk, vok, starts.astype(np.int64), target, x0, y0, x1, y1, VIA_COST, allow_via,
                     int(tx.min()), int(ty.min()), int(tx.max()), int(ty.max()))
        if len(path) == 0 and margin < 40:
            return self.search(code, starts, target, width, allow_via, margin=60)
        return path if len(path) else None

    def pad_starts(self, pad):
        cells = []
        for L in pad["layers"]:
            cells.append(pad["cells"] + L * H * W)
        if "extra" in pad:
            cells.append(pad["extra"])
        return np.concatenate(cells)

    def escape(self, ref="U1"):
        """Dog-bone escape (short track + via) for signal pads on the module's inner rows."""
        fp = self.b.FindFootprintByReference(ref)
        inner_nums = set()
        for q in fp.Pads():
            loc = q.GetPos0()
            if not (abs(TM(loc.x)) > 4.5 or TM(loc.y) > 7.0):
                inner_nums.add(q.GetNumber())
        n = 0
        for pad in self.pads:
            if pad["ref"] != ref or pad["num"] not in inner_nums or pad["net"] in D.PLANE_NETS:
                continue
            code = self.netcode[pad["net"]]
            vok = self.via_ok(code)
            target = np.zeros((2, H, W), dtype=bool)
            L = pad["layers"][0]
            target[L] = vok
            own = np.zeros(H * W, dtype=bool); own[pad["cells"]] = True
            target[L] &= ~ndimage.binary_dilation(own.reshape(H, W), structure=disk(0.35 / RES))
            path = self.search(code, self.pad_starts(pad), target, TRACK, allow_via=False, margin=2.5)
            if path is None:
                continue
            r = path[-1] % (H * W)
            vpos = to_mm(r % W, r // W)
            self.emit(pad["net"], path, TRACK, start_pos=pad["pos"])
            self.add_via(pad["net"], vpos)
            self.paint_path(code, path, TRACK)
            self.paint_via(code, *vpos)
            pad["extra"] = np.concatenate([path, np.array([r, r + H * W])])
            n += 1
        self.log.append(f"escape: {n} module pads dog-boned")

    def fanout(self, planes=("GND", "+3V3")):
        n = 0
        for pad in self.pads:
            if pad["net"] not in planes or not pad["smd"]:
                continue
            code = self.netcode[pad["net"]]
            vok = self.via_ok(code)
            target = np.zeros((2, H, W), dtype=bool)
            L = pad["layers"][0]
            target[L] = vok
            # don't land the via on the pad itself
            own = np.zeros(H * W, dtype=bool); own[pad["cells"]] = True
            target[L] &= ~ndimage.binary_dilation(own.reshape(H, W), structure=disk(0.35 / RES))
            path = self.search(code, self.pad_starts(pad), target, FAN_W, allow_via=False, margin=3.0)
            if path is None:
                self.failed.append(("fanout", pad["ref"], pad["num"], pad["net"]))
                continue
            end = path[-1]; r = end % (H * W)
            vpos = to_mm(r % W, r // W)
            self.emit(pad["net"], path, FAN_W, start_pos=pad["pos"])
            self.add_via(pad["net"], vpos)
            self.paint_path(code, path, FAN_W)
            self.paint_via(code, *vpos)
            n += 1
        self.log.append(f"fan-out: {n} plane vias")

    def route_net(self, net):
        code = self.netcode[net]
        width = D.POWER_NETS.get(net, TRACK)
        pads = [p for p in self.pads if p["net"] == net]
        if len(pads) < 2:
            return True
        tree = np.zeros((2, H, W), dtype=bool)
        first = pads[0]
        for L in first["layers"]:
            tree[L].flat[first["cells"]] = True
        if "extra" in first:
            tree.reshape(-1)[first["extra"]] = True
        todo = pads[1:]
        ok = True
        while todo:
            # nearest pad to the tree
            todo_ids = {id(q) for q in todo}
            tpos = [q["pos"] for q in pads if id(q) not in todo_ids]
            todo.sort(key=lambda p: min(math.dist(p["pos"], q) for q in tpos))
            p = todo.pop(0)
            # already touching the tree (e.g. multi-pad pins)?
            if any(tree[L].flat[p["cells"]].any() for L in p["layers"]):
                if "extra" in p:
                    tree.reshape(-1)[p["extra"]] = True
                continue
            path = self.search(code, self.pad_starts(p), tree, width)
            if path is None:
                self.failed.append(("net", net, p["ref"], p["num"]))
                ok = False
                for L in p["layers"]:
                    tree[L].flat[p["cells"]] = True
                continue
            self.emit(net, path, width, start_pos=p["pos"])
            self.paint_path(code, path, width)
            L_ = path // (H * W); r = path % (H * W)
            tree.reshape(2, -1)[L_, r] = True
            for L in p["layers"]:
                tree[L].flat[p["cells"]] = True
            if "extra" in p:
                tree.reshape(-1)[p["extra"]] = True
        return ok

    def signal_order(self, first=()):
        nets = sorted({p["net"] for p in self.pads} - set(D.PLANE_NETS))

        def span(n):
            pts = [p["pos"] for p in self.pads if p["net"] == n]
            return sum(math.dist(pts[0], q) for q in pts[1:])
        inner = []
        for p in self.pads:
            if p["ref"] == "U1" and p["net"] in nets and p["net"] not in first and p["net"] not in inner:
                fp = self.b.FindFootprintByReference("U1")
                pad = [q for q in fp.Pads() if q.GetNumber() == p["num"]][0]
                loc = pad.GetPos0()
                if not (abs(TM(loc.x)) > 4.5 or TM(loc.y) > 7.0):
                    inner.append(p["net"])
        first = tuple(first) + tuple(inner)
        power = [n for n in nets if n in D.POWER_NETS and n not in first]
        rest = sorted([n for n in nets if n not in D.POWER_NETS and n not in first], key=span)
        return list(first) + power + rest


def run(src, dst, stage="all", first=()):
    b = pcbnew.LoadBoard(src)
    R = Router(b)
    t0 = time.time()
    R.fanout()
    R.escape()
    if stage in ("power", "all"):
        order = R.signal_order(first)
        for net in order:
            if stage == "power" and net not in D.POWER_NETS:
                continue
            R.route_net(net)
    R.log.append(f"routed in {time.time() - t0:.0f} s, failed: {len(R.failed)}")
    b.Save(dst)
    return R


def best_of(src, dst, passes=10):
    """Route, then re-route with the failed nets first; keep the best pass."""
    first, best = [], None
    for i in range(passes):
        tmp = dst + f".pass{i}"
        R = run(src, tmp, "all", tuple(first))
        nfail = len(R.failed)
        print(f"pass {i}: {nfail} failed {[f[1] for f in R.failed]}", flush=True)
        if best is None or nfail < best[0]:
            best = (nfail, tmp, R)
        if nfail == 0:
            break
        for f in R.failed:
            n = f[1] if f[0] == "net" else f[3]
            if n in first:
                first.remove(n)
            first.insert(0, n)
        first = first[:12]
    import shutil
    shutil.copy(best[1], dst)
    Path(dst).with_suffix(".unrouted.json").write_text(json.dumps(best[2].failed))
    return best[2]


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    R = best_of(src, dst)
    print("\n".join(R.log))
    print("FAILED", json.dumps(R.failed))
