"""Generate the KiCad schematic (opencycle.kicad_sch) from design.py.

The schematic is "label-connected": every symbol from design.py is placed in a functional block and
each connected pin gets a net label with the same net name as on the board; unconnected pins get a
no-connect flag. It is generated from the same table as the PCB, so it cannot drift from it, and
`check_netlist.py` proves that by comparing KiCad's netlist export with the board.

python gen_schematic.py        -> opencycle.kicad_sch (+ lib tables for opening in KiCad)
"""
import copy
import uuid
from pathlib import Path

from kiutils.symbol import SymbolLib

import design as D
from symlib import lib_path

HERE = Path(__file__).parent
G = 2.54

# functional blocks, drawn left-to-right, top-to-bottom on an A1 sheet
BLOCKS = [
    ("Main MCU (ESP32-S3)", ["U1", "C1", "C2", "R1", "C3", "J5"]),
    ("ANT+ / BLE coprocessor", ["U2", "C4", "C5", "J4"]),
    ("GPS", ["U3", "C6", "C7", "AE1"]),
    ("Display 2.4 in TFT + backlight", ["J3", "C9", "C10", "R5", "R6", "R7", "R8", "Q1", "R9", "R10"]),
    ("USB-C, charger, battery, 3.3 V", ["J1", "R11", "R12", "D2", "R13", "R14", "C14", "U6", "R15", "C15", "C16",
                                        "J2", "Q2", "U5", "C11", "C12", "C13", "R16", "R17", "C17", "R18", "R19",
                                        "D1", "R2"]),
    ("Sensors", ["U4", "C8", "R3", "R4", "U8", "C20"]),
    ("Audio", ["U7", "C18", "C19", "R20", "LS1"]),
    ("Keys", ["SW1", "SW2", "SW3", "SW4", "SW5", "R21", "R22", "R23", "R24", "R25"]),
]
POWER_FLAG_NETS = ["GND", "VBUS", "BATT+"]      # +3V3 and VBAT are driven by the LDO / charger outputs


def uid():
    return str(uuid.uuid4())


def snap(v):
    return round(v / 1.27) * 1.27


class Sym:
    def __init__(self, libname, name):
        L = SymbolLib.from_file(lib_path(libname))
        s = next(x for x in L.symbols if x.entryName == name)
        base = next(x for x in L.symbols if x.entryName == s.extends) if s.extends else s
        flat = copy.deepcopy(base)
        if s is not base:        # derived symbol: keep the derived properties
            flat.properties = copy.deepcopy(s.properties)
        flat.libraryNickname = libname
        flat.entryName = name
        flat.extends = None
        for u in flat.units:
            u.entryName = name
            u.libraryNickname = None
        self.flat = flat
        self.lib_id = f"{libname}:{name}"
        self.pins = []
        for u in flat.units:
            for p in u.pins:
                self.pins.append((p.number, p.name, p.position.X, p.position.Y, p.position.angle or 0, p.length))
        xs = [p[2] for p in self.pins] or [0]
        ys = [p[3] for p in self.pins] or [0]
        self.bbox = (min(xs), min(ys), max(xs), max(ys))


def label_dir(angle):
    # pin angle = direction from the connection point into the body; the label goes the other way
    return {0: (180, "right"), 180: (0, "left"), 90: (270, "left"), 270: (90, "left")}[int(angle) % 360]


def main():
    global ROOT
    parts = {p["ref"]: p for p in D.PARTS}
    placed = [r for _, refs in BLOCKS for r in refs]
    missing = [r for r in parts if r not in placed and not r.startswith("FID")]
    assert not missing, f"not placed in a schematic block: {missing}"
    syms, out, texts = {}, [], []
    ROOT = uid()
    page_w, page_h = 841.0, 594.0             # A1 landscape
    LBL = 26.0                                 # room for net labels either side of a symbol
    MAX_H = 150.0                              # column height before wrapping within a block
    bx, by, row_h = 25.4, 35.0, 0.0
    for title, refs in BLOCKS:
        items = []
        for r in refs:
            p = parts[r]
            key = f'{p["slib"]}:{p["sym"]}'
            if key not in syms:
                syms[key] = Sym(p["slib"], p["sym"])
            items.append((r, syms[key]))
        # lay the block out in columns (relative coordinates), then place it
        cols, col, h = [], [], 0.0
        for r, s_ in items:
            x0, y0, x1, y1 = s_.bbox
            sh = (y1 - y0) + 12.7
            if col and h + sh > MAX_H:
                cols.append(col); col, h = [], 0.0
            col.append((r, s_, h)); h += sh
        cols.append(col)
        widths = [max((s_.bbox[2] - s_.bbox[0]) + 2 * LBL for _, s_, _ in c) for c in cols]
        heights = [max(yy + (s_.bbox[3] - s_.bbox[1]) + 12.7 for _, s_, yy in c) for c in cols]
        bw, bh = sum(widths), max(heights) + 12
        if bx + bw > page_w - 20 and bx > 25.4:
            bx, by, row_h = 25.4, by + row_h + 20, 0.0
        texts.append((title, bx, by))
        cx = bx
        for c, w in zip(cols, widths):
            for r, s_, yy in c:
                x0, y0, x1, y1 = s_.bbox
                sx = snap(cx + LBL - x0)
                sy = snap(by + 12 + yy + y1)          # symbol y axis points up
                place(out, parts[r], s_, sx, sy, ROOT)
            cx += w
        bx += bw + 20
        row_h = max(row_h, bh)
    # power flags
    pf = Sym("power", "PWR_FLAG")
    syms["power:PWR_FLAG"] = pf
    fx, fy = page_w - 170, page_h - 45
    texts.append(("Power flags (tell ERC these nets are driven)", fx - 5, fy - 20))
    for i, net in enumerate(POWER_FLAG_NETS):
        x, y = snap(fx + i * 22.86), snap(fy)
        out.append(sym_inst(pf, f"#FLG{i + 1:02d}", "PWR_FLAG", "", x, y, ROOT, in_bom=False, on_board=False))
        out.append(label(net, x, y, 270, "left"))
    body = [f'(kicad_sch (version 20230121) (generator eeschema)\n  (uuid {ROOT})\n  (paper "A1")\n',
            '  (title_block (title "OpenCycle main board v0.2") (date "2026-09-30") (rev "A")\n'
            '    (comment 1 "Generated from pcb/design.py by gen_schematic.py - do not edit by hand")\n'
            '    (comment 2 "Nets connect by label name; every net name matches the PCB"))\n',
            "  (lib_symbols\n"]
    for s_ in syms.values():
        body.append(s_.flat.to_sexpr(indent=4) + "\n")
    body.append("  )\n")
    for t, x, y in texts:
        body.append(f'  (text "{t}" (at {snap(x)} {snap(y)} 0)\n    (effects (font (size 3 3) (thickness 0.6) bold) (justify left bottom))\n    (uuid {uid()})\n  )\n')
    body.extend(out)
    body.append('  (sheet_instances (path "/" (page "1")))\n)\n')
    (HERE / "opencycle.kicad_sch").write_text("".join(body))
    print("wrote opencycle.kicad_sch:", len(parts), "parts")


def label(net, x, y, ang, just):
    return (f'  (label "{net}" (at {x:.2f} {y:.2f} {ang}) (fields_autoplaced)\n'
            f'    (effects (font (size 1.27 1.27)) (justify {just} bottom))\n    (uuid {uid()})\n  )\n')


def sym_inst(s, ref, value, fp, x, y, root, in_bom=True, on_board=True, mpn="", mfr="", dnp=False):
    props = [("Reference", ref, 0, -3), ("Value", value, 0, 3), ("Footprint", fp, 0, 0), ("Datasheet", "", 0, 0)]
    if mpn:
        props += [("MPN", mpn, 0, 0), ("Manufacturer", mfr, 0, 0)]
    pr = []
    for i, (k, v, dx, dy) in enumerate(props):
        hide = "" if k in ("Reference", "Value") else " hide"
        py = s.bbox[1] - 3.81 if k == "Reference" else s.bbox[3] + 3.81
        pr.append(f'    (property "{k}" "{v}" (at {x:.2f} {y - (s.bbox[3] + 2.54) if k == "Reference" else y - s.bbox[1] + 2.54:.2f} 0)\n'
                  f'      (effects (font (size 1.27 1.27)){hide})\n    )\n')
    pins = "".join(f'    (pin "{p[0]}" (uuid {uid()}))\n' for p in s.pins)
    return (f'  (symbol (lib_id "{s.lib_id}") (at {x:.2f} {y:.2f} 0) (unit 1)\n'
            f'    (in_bom {"yes" if in_bom else "no"}) (on_board {"yes" if on_board else "no"}) (dnp {"yes" if dnp else "no"})\n'
            f'    (uuid {uid()})\n' + "".join(pr) + pins +
            f'    (instances\n      (project "opencycle"\n        (path "/{ROOT}" (reference "{ref}") (unit 1))\n      )\n    )\n  )\n')


ROOT = None


def place(out, p, s, x, y, root):
    global ROOT
    ROOT = root
    fp = f'{p["flib"]}:{p["fp"]}'
    out.append(sym_inst(s, p["ref"], p["value"], fp, x, y, root, mpn=p["mpn"], mfr=p["mfr"],
                        in_bom=bool(p["mpn"])))
    # net per pin number (design.py keys are pin names or numbers)
    by_name = {}
    for num, name, *_ in s.pins:
        by_name.setdefault(name, []).append(num)
        by_name.setdefault(num, []).append(num)
    net_of = {}
    for key, net in p["pins"].items():
        for num in by_name[key]:
            net_of[num] = net
    seen = set()
    for num, name, px, py, ang, ln in s.pins:
        ax, ay = x + px, y - py
        k = (round(ax, 2), round(ay, 2))
        net = net_of.get(num)
        if k in seen:            # stacked pins (e.g. 8 antenna ground pads) share one label
            continue
        seen.add(k)
        if net:
            a, j = label_dir(ang)
            out.append(label(net, ax, ay, a, j))
        else:
            out.append(f'  (no_connect (at {ax:.2f} {ay:.2f}) (uuid {uid()}))\n')


if __name__ == "__main__":
    main()
