"""Write the local footprints in pcb/OpenCycle.pretty as plain KiCad 7 S-expressions.

Taoglas_DSGP.1575.12.4.A.02_12x12mm   Taoglas datasheet §6.5: 8 x 3.0 mm square ground pads on a 4.5 mm grid,
                                      2.0 x 2.0 mm feed pad centred at (0, +4.9), 0.5 mm copper keep-out ring
                                      around the feed. Antenna centre = footprint origin, feed toward +y.
Bosch_LGA-10_2x2mm_P0.5mm_BMP581      Bosch BST-BMP581-DS004-13 §8.1-8.2: package pads 0.25 x 0.275 at
                                      +/-0.7625 mm, land = pad + 25 um per side; top view, pin 1 top-left;
                                      no solder mask under the body.
SpeakerPads_2.6mm                     two 1.8 x 2.2 mm pads for the speaker leads, 2.6 mm apart.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "OpenCycle.pretty"


def pad(num, x, y, w, h, shape="roundrect", rr=0.1, layers='"F.Cu" "F.Paste" "F.Mask"', extra=""):
    rr_s = f" (roundrect_rratio {rr})" if shape == "roundrect" else ""
    return f'  (pad "{num}" smd {shape} (at {x:g} {y:g}) (size {w:g} {h:g}) (layers {layers}){rr_s}{extra})\n'


def rect(layer, x0, y0, x1, y1, w):
    return f'  (fp_rect (start {x0:g} {y0:g}) (end {x1:g} {y1:g}) (stroke (width {w:g}) (type solid)) (fill none) (layer "{layer}"))\n'


def text(kind, t, x, y, layer, size=1.0, hide=False):
    h = " hide" if hide else ""
    return (f'  (fp_text {kind} "{t}" (at {x:g} {y:g}) (layer "{layer}"){h}\n'
            f'    (effects (font (size {size:g} {size:g}) (thickness {size * 0.15:g}))))\n')


def module(name, body, descr, tags, attr="smd"):
    return (f'(footprint "{name}" (version 20221018) (generator opencycle_gen_footprints) (layer "F.Cu")\n'
            f'  (descr "{descr}")\n  (tags "{tags}")\n  (attr {attr})\n' + body + ")\n")


def taoglas():
    b = text("reference", "REF**", 0, -7.2, "F.SilkS") + text("value", "DSGP.1575.12.4.A.02", 0, 7.9, "F.Fab")
    b += text("user", "FEED", 0, 6.9, "F.Fab", 0.5)
    for n, (x, y) in {"2": (-4.5, -4.5), "3": (0, -4.5), "4": (4.5, -4.5), "5": (-4.5, 0), "6": (0, 0),
                      "7": (4.5, 0), "8": (-4.5, 4.5), "9": (4.5, 4.5)}.items():
        b += pad(n, x, y, 3.0, 3.0, rr=0.05)
    b += pad("1", 0, 4.9, 2.0, 2.0, rr=0.05)
    b += rect("F.Fab", -6, -6, 6, 6, 0.1) + rect("F.SilkS", -6.2, -6.2, 6.2, 6.2, 0.12)
    b += rect("F.CrtYd", -6.25, -6.25, 6.25, 6.25, 0.05)
    # copper keep-out ring around the feed pad (datasheet: 0.5 mm)
    b += ('  (zone (net 0) (net_name "") (layer "F.Cu") (hatch edge 0.5) (connect_pads (clearance 0))\n'
          '    (min_thickness 0.25) (filled_areas_thickness no)\n'
          '    (keepout (tracks allowed) (vias not_allowed) (pads allowed) (copperpour not_allowed) (footprints allowed))\n'
          '    (fill (thermal_gap 0.5) (thermal_bridge_width 0.5))\n'
          '    (polygon (pts (xy -1.5 3.4) (xy 1.5 3.4) (xy 1.5 6.4) (xy -1.5 6.4)))\n  )\n')
    return module("Taoglas_DSGP.1575.12.4.A.02_12x12mm", b,
                  "Taoglas DSGP.1575.12.4.A.02 12x12x4 mm GNSS patch, land pattern per datasheet section 6.5",
                  "GNSS GPS patch antenna Taoglas")


def bmp581():
    b = text("reference", "REF**", 0, -1.8, "F.SilkS", 0.6) + text("value", "BMP581", 0, 1.9, "F.Fab", 0.5)
    P = 0.7625
    row, col = (0.30, 0.325), (0.325, 0.30)
    pads = {"10": (-0.5, -P, row), "9": (0.0, -P, row), "8": (0.5, -P, row),
            "1": (-P, -0.25, col), "2": (-P, 0.25, col),
            "3": (-0.5, P, row), "4": (0.0, P, row), "5": (0.5, P, row),
            "7": (P, -0.25, col), "6": (P, 0.25, col)}
    for n, (x, y, (w, h)) in pads.items():
        b += pad(n, x, y, w, h, shape="rect", extra=" (solder_mask_margin 0.02)")
    b += rect("F.Fab", -1, -1, 1, 1, 0.1) + rect("F.CrtYd", -1.3, -1.3, 1.3, 1.3, 0.05)
    b += '  (fp_circle (center -1.35 -1.05) (end -1.25 -1.05) (stroke (width 0.12) (type solid)) (fill none) (layer "F.SilkS"))\n'
    # Bosch: no solder mask under the sensor -> one mask opening over the body
    b += ('  (fp_poly (pts (xy -1.02 -1.02) (xy 1.02 -1.02) (xy 1.02 1.02) (xy -1.02 1.02))'
          ' (stroke (width 0) (type solid)) (fill solid) (layer "F.Mask"))\n')
    return module("Bosch_LGA-10_2x2mm_P0.5mm_BMP581", b,
                  "Bosch BMP581 LGA-10 2.0x2.0 mm, land pattern per datasheet BST-BMP581-DS004-13 section 8.2",
                  "BMP581 LGA barometer")


def speaker():
    b = text("reference", "REF**", 0, -2.4, "F.SilkS", 0.8) + text("value", "SpeakerPads", 0, 2.4, "F.Fab", 0.6)
    b += pad("1", -1.3, 0, 1.8, 2.2, rr=0.25, layers='"F.Cu" "F.Mask"')
    b += pad("2", 1.3, 0, 1.8, 2.2, rr=0.25, layers='"F.Cu" "F.Mask"')
    b += text("user", "+", -1.3, -1.9, "F.SilkS", 0.8)
    b += rect("F.CrtYd", -2.6, -1.5, 2.6, 1.5, 0.05)
    return module("SpeakerPads_2.6mm", b, "Two hand-solder pads for speaker leads", "speaker pads")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for name, fn in [("Taoglas_DSGP.1575.12.4.A.02_12x12mm", taoglas), ("Bosch_LGA-10_2x2mm_P0.5mm_BMP581", bmp581),
                     ("SpeakerPads_2.6mm", speaker)]:
        (OUT / f"{name}.kicad_mod").write_text(fn())
    print("wrote", OUT)
