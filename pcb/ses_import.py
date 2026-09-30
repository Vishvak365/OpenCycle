"""Import a Freerouting/Specctra session (.ses) into a KiCad board without the GUI.

KiCad 7's pcbnew.ImportSpecctraSES() needs the editor window, so this reads the SES routes directly:
wires -> PCB_TRACK segments, vias -> PCB_VIA (through, 0.5/0.3 mm). SES y axis points up (y = -KiCad y).
"""
import re
import sys

import pcbnew


def tokens(s):
    return re.findall(r'"[^"]*"|\(|\)|[^\s()]+', s)


def parse(tok, i=0):
    out = []
    while i < len(tok):
        t = tok[i]
        if t == "(":
            sub, i = parse(tok, i + 1)
            out.append(sub)
        elif t == ")":
            return out, i + 1
        else:
            out.append(t.strip('"'))
            i += 1
    return out, i


def find(node, key):
    return [n for n in node if isinstance(n, list) and n and n[0] == key]


def import_ses(board, ses_path, via_d=0.5, via_drill=0.3):
    tree, _ = parse(tokens(open(ses_path).read()))
    sess = tree[0]
    routes = find(sess, "routes")[0]
    res = find(routes, "resolution")[0]
    scale = {"um": 1e-3, "mm": 1.0, "mil": 0.0254}[res[1]] / float(res[2])      # file units -> mm
    layers = {board.GetLayerName(l): l for l in range(pcbnew.PCB_LAYER_ID_COUNT)}
    nets = board.GetNetsByName()
    n_tr = n_via = 0
    for net in find(find(routes, "network_out")[0], "net"):
        name = net[1]
        ni = nets[name] if nets.has_key(name) else None
        for w in find(net, "wire"):
            path = find(w, "path")[0]
            layer, width = layers[path[1]], float(path[2]) * scale
            pts = [(float(path[i]) * scale, -float(path[i + 1]) * scale) for i in range(3, len(path) - 1, 2)]
            for a, b in zip(pts, pts[1:]):
                t = pcbnew.PCB_TRACK(board)
                t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(a[0]), pcbnew.FromMM(a[1])))
                t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(b[0]), pcbnew.FromMM(b[1])))
                t.SetWidth(pcbnew.FromMM(width)); t.SetLayer(layer)
                if ni:
                    t.SetNet(ni)
                board.Add(t); n_tr += 1
        for v in find(net, "via"):
            x, y = float(v[2]) * scale, -float(v[3]) * scale
            via = pcbnew.PCB_VIA(board)
            via.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
            via.SetWidth(pcbnew.FromMM(via_d)); via.SetDrill(pcbnew.FromMM(via_drill))
            via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); via.SetViaType(pcbnew.VIATYPE_THROUGH)
            if ni:
                via.SetNet(ni)
            board.Add(via); n_via += 1
    return n_tr, n_via


if __name__ == "__main__":
    b = pcbnew.LoadBoard(sys.argv[1])
    print(import_ses(b, sys.argv[2]))
    b.Save(sys.argv[3])
