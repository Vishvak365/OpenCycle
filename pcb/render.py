"""Render the board to SVG (front and back) with copper, mask, silk and ratsnest."""
import sys
from pathlib import Path

import pcbnew

TM = pcbnew.ToMM
COL = {
    "board": "#0f3d2b", "edge": "#c8d0c0",
    "F.Cu": "#d9a441", "B.Cu": "#5aa0d8", "pad": "#e6c46a", "via": "#cfd6de",
    "zoneF": "#1d5a3f", "zoneB": "#1a4c5c", "silk": "#f2f2ec", "rat": "#ff4fa3", "crt": "#89a397",
}


def poly_paths(ps):
    out = []
    for i in range(ps.OutlineCount()):
        o = ps.Outline(i)
        pts = [o.CPoint(j) for j in range(o.PointCount())]
        if pts:
            out.append("M" + " L".join(f"{TM(p.x):.3f},{TM(p.y):.3f}" for p in pts) + " Z")
        for h in range(ps.HoleCount(i)):
            hh = ps.Hole(i, h)
            pts = [hh.CPoint(j) for j in range(hh.PointCount())]
            if pts:
                out.append("M" + " L".join(f"{TM(p.x):.3f},{TM(p.y):.3f}" for p in pts) + " Z")
    return " ".join(out)


def mst_rats(board, skip=("GND", "+3V3")):
    import math
    nets = {}
    for fp in board.GetFootprints():
        for p in fp.Pads():
            n = p.GetNetname()
            if n and n not in skip:
                q = p.GetPosition(); nets.setdefault(n, []).append((TM(q.x), TM(q.y)))
    lines = []
    for n, pts in nets.items():
        if len(pts) < 2:
            continue
        inn = {0}; rest = set(range(1, len(pts)))
        while rest:
            best = min(((i, j) for i in inn for j in rest), key=lambda ij: math.dist(pts[ij[0]], pts[ij[1]]))
            lines.append((*pts[best[0]], *pts[best[1]])); inn.add(best[1]); rest.discard(best[1])
    return lines


def ratsnest(board):
    board.BuildConnectivity()
    conn = board.GetConnectivity()
    lines = []
    for code in range(1, board.GetNetCount()):
        try:
            rn = conn.GetRatsnestForNet(code)
            if rn is None:
                continue
            for e in rn.GetEdges():
                if e.IsVisible():
                    a, b = e.GetSourcePos(), e.GetTargetPos()
                    lines.append((TM(a.x), TM(a.y), TM(b.x), TM(b.y)))
        except Exception:
            pass
    return lines


def render(board, side="F", show_rats=True, rats=None):
    cu = pcbnew.F_Cu if side == "F" else pcbnew.B_Cu
    other = pcbnew.B_Cu if side == "F" else pcbnew.F_Cu
    silk = pcbnew.F_SilkS if side == "F" else pcbnew.B_SilkS
    crt = pcbnew.F_CrtYd if side == "F" else pcbnew.B_CrtYd
    parts = []
    # board body
    outline = pcbnew.SHAPE_POLY_SET()
    board.GetBoardPolygonOutlines(outline)
    parts.append(f'<path d="{poly_paths(outline)}" fill="{COL["board"]}" stroke="{COL["edge"]}" stroke-width="0.15"/>')
    # zones on this side
    for z in board.Zones():
        if z.GetIsRuleArea():
            continue
        if z.IsOnLayer(cu):
            fp = z.GetFilledPolysList(cu)
            if fp.OutlineCount():
                parts.append(f'<path d="{poly_paths(fp)}" fill="{COL["zoneF" if side=="F" else "zoneB"]}" fill-rule="evenodd"/>')
    # other-side tracks faintly
    for t in board.GetTracks():
        if t.GetClass() == "PCB_TRACK" and t.GetLayer() == other:
            a, b = t.GetStart(), t.GetEnd()
            parts.append(f'<line x1="{TM(a.x):.3f}" y1="{TM(a.y):.3f}" x2="{TM(b.x):.3f}" y2="{TM(b.y):.3f}" stroke="{COL["B.Cu" if side=="F" else "F.Cu"]}" stroke-opacity="0.22" stroke-width="{TM(t.GetWidth()):.3f}" stroke-linecap="round"/>')
    for t in board.GetTracks():
        if t.GetClass() == "PCB_TRACK" and t.GetLayer() == cu:
            a, b = t.GetStart(), t.GetEnd()
            parts.append(f'<line x1="{TM(a.x):.3f}" y1="{TM(a.y):.3f}" x2="{TM(b.x):.3f}" y2="{TM(b.y):.3f}" stroke="{COL["F.Cu" if side=="F" else "B.Cu"]}" stroke-width="{TM(t.GetWidth()):.3f}" stroke-linecap="round"/>')
    # pads
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if not pad.IsOnLayer(cu):
                continue
            ps = pcbnew.SHAPE_POLY_SET()
            pad.TransformShapeToPolygon(ps, cu, 0, pcbnew.FromMM(0.01))
            parts.append(f'<path d="{poly_paths(ps)}" fill="{COL["pad"]}"/>')
            if pad.HasHole():
                p = pad.GetPosition(); d = TM(pad.GetDrillSize().x)
                parts.append(f'<circle cx="{TM(p.x):.3f}" cy="{TM(p.y):.3f}" r="{d/2:.3f}" fill="#0b0d0c"/>')
    for t in board.GetTracks():
        if t.GetClass() == "PCB_VIA":
            p = t.GetPosition()
            parts.append(f'<circle cx="{TM(p.x):.3f}" cy="{TM(p.y):.3f}" r="{TM(t.GetWidth())/2:.3f}" fill="{COL["via"]}"/>'
                         f'<circle cx="{TM(p.x):.3f}" cy="{TM(p.y):.3f}" r="{TM(t.GetDrillValue())/2:.3f}" fill="#0b0d0c"/>')
    # courtyards + refs
    for fp in board.GetFootprints():
        if (fp.GetLayer() == pcbnew.F_Cu) != (side == "F") or fp.GetReference().startswith("H"):
            continue
        c = fp.GetCourtyard(crt)
        if c.OutlineCount():
            parts.append(f'<path d="{poly_paths(c)}" fill="none" stroke="{COL["crt"]}" stroke-width="0.06" stroke-dasharray="0.3 0.2"/>')
        p = fp.GetPosition()
        tx = TM(p.x)
        tr = f' transform="translate({2*tx:.3f},0) scale(-1,1)"' if side == "B" else ""
        parts.append(f'<text x="{tx:.3f}" y="{TM(p.y)+0.3:.3f}" font-size="0.9" text-anchor="middle" fill="{COL["silk"]}" font-family="monospace"{tr}>{fp.GetReference()}</text>')
    if show_rats:
        for (x1, y1, x2, y2) in (rats if rats is not None else mst_rats(board)):
            parts.append(f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="{COL["rat"]}" stroke-width="0.07"/>')
    g = "\n".join(parts)
    wrap = f'<g transform="translate(52,0) scale(-1,1)">{g}</g>' if side == "B" else f"<g>{g}</g>"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="1 1 50 84" width="500" height="840">'
            f'{wrap}</svg>')


if __name__ == "__main__":
    src = sys.argv[1]
    outdir = Path(sys.argv[2]); outdir.mkdir(parents=True, exist_ok=True)
    b = pcbnew.LoadBoard(src)
    for s in ("F", "B"):
        (outdir / f"{'front' if s=='F' else 'back'}.svg").write_text(render(b, s))
    print("rats", len(mst_rats(b)))
