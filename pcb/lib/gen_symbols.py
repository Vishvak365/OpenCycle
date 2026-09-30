"""Write pcb/lib/OpenCycle.kicad_sym: symbols for parts KiCad 7 does not ship.

BMP581   Bosch datasheet BST-BMP581-DS004-13, Table 28 (pin description)
DSGP12   Taoglas DSGP.1575.12.4.A.02 datasheet §6.1: pin 1 = RF feed, pins 2-9 = ground
"""
from pathlib import Path

SYMS = {
    "BMP581": dict(ref="U", fp="OpenCycle:Bosch_LGA-10_2x2mm_P0.5mm_BMP581",
                   ds="https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp581-ds004.pdf",
                   desc="Barometric pressure sensor, I2C/SPI/I3C, LGA-10 2x2 mm",
                   left=[("1", "VDDIO", "power_in"), ("10", "VDD", "power_in"), ("6", "CSB", "input"),
                         ("5", "SDO", "bidirectional")],
                   right=[("2", "SCK", "input"), ("4", "SDI", "bidirectional"), ("7", "INT", "output")],
                   bottom=[("3", "VSS", "power_in"), ("8", "VSS", "power_in"), ("9", "VSS", "power_in")]),
    "DSGP.1575.12.4.A.02": dict(ref="AE", fp="OpenCycle:Taoglas_DSGP.1575.12.4.A.02_12x12mm",
                   ds="https://www.taoglas.com/datasheets/DSGP.1575.12.4.A.02.pdf",
                   desc="GPS L1 / Galileo E1 passive ceramic patch antenna 12x12x4 mm, SMT",
                   left=[("1", "FEED", "passive")], right=[],
                   bottom=[(str(i), "GND", "passive") for i in range(2, 10)]),
}


def pin(num, name, typ, x, y, ang, hide=False):
    return (f'      (pin {typ} line (at {x:.2f} {y:.2f} {ang}) (length 2.54){" hide" if hide else ""}\n'
            f'        (name "{name}" (effects (font (size 1.27 1.27))))\n'
            f'        (number "{num}" (effects (font (size 1.27 1.27)))))\n')


def symbol(name, s):
    n = max(len(s["left"]), len(s["right"]), 2)
    h = (n + 1) * 2.54
    w = 15.24
    out = [f'  (symbol "{name}" (in_bom yes) (on_board yes)\n',
           f'    (property "Reference" "{s["ref"]}" (at 0 {h/2+2.54:.2f} 0) (effects (font (size 1.27 1.27))))\n',
           f'    (property "Value" "{name}" (at 0 {-h/2-5.08:.2f} 0) (effects (font (size 1.27 1.27))))\n',
           f'    (property "Footprint" "{s["fp"]}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))\n',
           f'    (property "Datasheet" "{s["ds"]}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))\n',
           f'    (property "ki_description" "{s["desc"]}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))\n',
           f'    (symbol "{name}_0_1"\n      (rectangle (start {-w/2:.2f} {h/2:.2f}) (end {w/2:.2f} {-h/2:.2f})'
           f' (stroke (width 0.254) (type default)) (fill (type background))))\n',
           f'    (symbol "{name}_1_1"\n']
    for i, (num, nm, typ) in enumerate(s["left"]):
        out.append(pin(num, nm, typ, -w / 2 - 2.54, h / 2 - 2.54 * (i + 1), 0))
    for i, (num, nm, typ) in enumerate(s["right"]):
        out.append(pin(num, nm, typ, w / 2 + 2.54, h / 2 - 2.54 * (i + 1), 180))
    bot = s["bottom"]
    for i, (num, nm, typ) in enumerate(bot):
        stacked = len({nm for _, nm, _ in bot}) == 1 and len(bot) > 3   # e.g. 8 ground pads -> one stacked pin
        x = 0 if (len(bot) == 1 or stacked) else -w / 2 + 2.54 + i * (w - 5.08) / max(1, len(bot) - 1)
        x = round(x / 2.54) * 2.54
        out.append(pin(num, nm, typ, x, -h / 2 - 2.54, 90))
    out.append("    )\n  )\n")
    return "".join(out)


txt = "(kicad_symbol_lib (version 20220914) (generator opencycle_gen_symbols)\n"
for k, v in SYMS.items():
    txt += symbol(k, v)
txt += ")\n"
Path(__file__).with_name("OpenCycle.kicad_sym").write_text(txt)
print("wrote OpenCycle.kicad_sym", list(SYMS))
