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
POWER_FLAG_NETS = ["GND", "+3V3", "VBAT", "VBUS", "BATT+"]


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
    parts = {p["ref"]: p for p in D.PARTS}
    placed = [r for _, refs in BLOCKS for r in refs]
    missing = [r for r in parts if r not in placed and not r.startswith("FID")]
    assert not missing, f"not placed in a schematic block: {missing}"
    syms = {}
    out, libsyms = [], {}
    root = uid()
    x_cursor, y_top = 25.4, 30.48
    col_w = 0
    row_y = y_top
    page_w, page_h = 841.0, 594.0
    texts = []
    bx = 25.4
    by = 30.48
    block_row_h = 0
    for title, refs in BLOCKS:
        # measure the block: symbols stacked in columns, each column up to ~250 mm tall
        items = []
        for r in refs:
            p = parts[r]
            key = f'{p["slib"]}:{p["sym"]}'
            if key not in syms:
                syms[key] = Sym(p["slib"], p["sym"])
            items.append((r, syms[key]))
        col_x, col_y, col_width, block_w, block_h = bx, by + 10, 0, 0, 0
        positions = []
        for r, s in items:
            x0, y0, x1, y1 = s.bbox
            w = (x1 - x0) + 2 * 24          # room for labels on both sides
            h = (y1 - y0) + 14
            if col_y + h > by + 10 + 230 and col_y > by + 10:
                col_x += col_width; col_y = by + 10; col_width = 0
            positions.append((r, s, snap(col_x + 24 - x0), snap(col_y - y0 * -1 + 7 if False else col_y + y1 + 7)))
            col_y += h
            col_width = max(col_width, w)
            block_w = max(block_w, col_x + col_width - bx)
            block_h = max(block_h, col_y - by)
        if bx + block_w > page_w - 20 and bx > 25.4:
            bx = 25.4; by += block_row_h + 15; block_row_h = 0
            # re-run this block at the new origin
            positions = [(r, s, snap(x - (col_x - 25.4) * 0 + 0), y) for r, s, x, y in positions]
            shift_x = 25.4 - positions[0][2] + (positions[0][2] - 25.4) if False else None
            dx = None
        texts.append((title, bx, by + 4))
        for r, s, x, y in positions:
            place(out, parts[r], s, x, y, root)
        bx += block_w + 15
        block_row_h = max(block_row_h, block_h)
    # power flags
    fx, fy = page_w - 120, page_h - 60
    pf = Sym("power", "PWR_FLAG")
    syms["power:PWR_FLAG"] = pf
    for i, net in enumerate(POWER_FLAG_NETS):
        x, y = snap(fx + i * 20.32), snap(fy)
        ref = f"#FLG{i + 1:02d}"
        out.append(sym_inst(pf, ref, "PWR_FLAG", "", x, y, root, in_bom=False, on_board=False))
        out.append(label(net, x, y, 90, "left"))
    texts.append(("Power flags (tell ERC these nets are driven)", fx - 5, fy - 15))

    body = []
    body.append(f'(kicad_sch (version 20230121) (generator eeschema)\n  (uuid {root})\n  (paper "A1")\n')
    body.append('  (title_block (title "OpenCycle main board v0.2") (date "2026-09-30") (rev "A")\n'
                '    (comment 1 "Generated from pcb/design.py by gen_schematic.py - do not edit by hand")\n'
                '    (comment 2 "Nets connect by label name; each net name matches the PCB"))\n')
    body.append("  (lib_symbols\n")
    for s in syms.values():
        body.append(s.flat.to_sexpr(indent=4) + "\n")
    body.append("  )\n")
    for t, x, y in texts:
        body.append(f'  (text "{t}" (at {snap(x)} {snap(y)} 0)\n    (effects (font (size 3 3) (thickness 0.6) bold) (justify left bottom))\n    (uuid {uid()})\n  )\n')
    body.extend(out)
    body.append(f'  (sheet_instances (path "/" (page "1")))\n)\n')
    (HERE / "opencycle.kicad_sch").write_text("".join(body))
    print("wrote opencycle.kicad_sch with", sum(1 for _ in out), "items")


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
