"""OpenCycle bike computer - parametric CadQuery model.

Run:  python model.py            -> writes ../out/step, ../out/stl, parts.json
Edit dimensions in params.py, then re-run.
"""
import json
import math
from pathlib import Path

import cadquery as cq

from params import *  # noqa: F401,F403

OUT = Path(__file__).resolve().parent.parent / "out"


# ----------------------------------------------------------------- helpers
def rrect(w, h, t, r, x0=0.0, y0=0.0, z0=0.0):
    """Rounded-corner block with its min corner at (x0, y0, z0)."""
    s = cq.Workplane("XY").box(w, h, t, centered=False)
    if r > 0:
        s = s.edges("|Z").fillet(min(r, w / 2 - 0.01, h / 2 - 0.01))
    return s.translate((x0, y0, z0))


def block(w, h, t, x0, y0, z0):
    return cq.Workplane("XY").box(w, h, t, centered=False).translate((x0, y0, z0))


def outline(inset=0.0, t=1.0, z0=0.0):
    """Body plan outline offset inward by `inset`."""
    return rrect(BODY_W - 2 * inset, BODY_H - 2 * inset, t,
                 max(CORNER_R - inset, 0.5), inset, inset, z0)


CAVITY_INSET_BACK = (BODY_W - (PCB_W + 2 * CLEAR + 0.2)) / 2      # ~2.7
LENS_W = BODY_W - 2 * LENS_INSET
LENS_H = BODY_H - LENS_INSET - LENS_Y0                             # lens stops above the key row
LENS_R = CORNER_R - LENS_INSET
BEZEL_INNER_INSET = LENS_INSET + 1.5                               # 1.5 mm ledge
FACE_T = 1.5                                                       # bezel face thickness around the keys
KEY_HOLE_CLEAR = 0.25

PCB_HOLES = [
    (PCB_X0 + PCB_HOLE_INSET, PCB_Y0 + PCB_HOLE_INSET),
    (PCB_X0 + PCB_W - PCB_HOLE_INSET, PCB_Y0 + PCB_HOLE_INSET),
    (PCB_X0 + PCB_HOLE_INSET, PCB_Y0 + PCB_H - PCB_HOLE_INSET),
    (PCB_X0 + PCB_W - PCB_HOLE_INSET, PCB_Y0 + PCB_H - PCB_HOLE_INSET),
]


# ---------------------------------------------------------- internal parts
def internal_parts():
    p = {}

    pcb = rrect(PCB_W, PCB_H, PCB_T, PCB_R, PCB_X0, PCB_Y0, PCB_Z)
    for (x, y) in PCB_HOLES:
        pcb = pcb.cut(cq.Workplane("XY").circle(PCB_HOLE_D / 2)
                      .extrude(PCB_T + 2).translate((x, y, PCB_Z - 1)))
    p["pcb"] = pcb

    # back-side modules (hang below the PCB, toward the battery)
    back_z = lambda t: PCB_Z - t
    for m in (ESP, BLE, GNSS, JST):
        z0 = back_z(m["t"]) if m["side"] == "B" else PCB_Z + PCB_T
        p[m["name"]] = block(m["w"], m["h"], m["t"], m["x0"], m["y0"], z0)
    p["usb_c"] = block(USBC["w"], USBC["h"], USBC["t"], (BODY_W - USBC["w"]) / 2, USB_Y0, back_z(USBC["t"]))

    # front-side small chips under the display (<=0.9 mm tall)
    chips = [("baro", 2, 2, 12, 30), ("light", 2, 2, 18, 30),
             ("charger", 2.5, 2.5, 26, 30), ("amp", 3, 3, 32, 30)]
    small = None
    for (_, w, h, x, y) in chips:
        c = block(w, h, 0.9, x, y, PCB_Z + PCB_T)
        small = c if small is None else small.union(c)
    p["sensors_power_ics"] = small

    # side-actuated tact switches (Alps SKRTLAE010) on the PCB back, stems 0.1 mm from the plungers
    sw = None
    for y in BTN_RIGHT_Y:
        s_ = block(2.56, 4.5, 3.55, 45.2, y - 2.25, PCB_Z - 3.55).union(block(0.83, 2.0, 1.2, 47.76, y - 1.0, PCB_Z - 2.4))
        sw = s_ if sw is None else sw.union(s_)
    for y in BTN_LEFT_Y:
        sw = sw.union(block(2.56, 4.5, 3.55, 4.24, y - 2.25, PCB_Z - 3.55)).union(
            block(0.83, 2.0, 1.2, 3.41, y - 1.0, PCB_Z - 2.4))
    p["tact_switches"] = sw
    # top-actuated switches under the three front keys
    fsw = None
    for x in KEY_X:
        f = block(3.2, 4.2, KEY_SW_T, x - 1.6, KEY_Y - 2.1, PCB_Z + PCB_T)     # PTS810 turned 90 deg on the board
        fsw = f if fsw is None else fsw.union(f)
    p["front_switches"] = fsw

    p["gnss_patch_antenna"] = block(ANT["w"], ANT["h"], ANT["t"],
                                    ANT_X0, ANT_Y0, PCB_Z + PCB_T)

    p["battery"] = rrect(BATT_W, BATT_H, BATT_T, 1.5, BATT_X0, BATT_Y0, BATT_Z)

    dx0 = DISP_X0
    foam_outer = rrect(DISP_W, DISP_H, FOAM_T, 1.0, dx0, DISP_Y0, DISP_Z - FOAM_T)
    foam_inner = rrect(DISP_W - 2 * FOAM_W, DISP_H - 2 * FOAM_W, FOAM_T + 1, 0.5,
                       dx0 + FOAM_W, DISP_Y0 + FOAM_W, DISP_Z - FOAM_T - 0.5)
    p["foam_gasket"] = foam_outer.cut(foam_inner)

    p["display"] = rrect(DISP_W, DISP_H, DISP_T, 1.0, dx0, DISP_Y0, DISP_Z)
    # active area as a separate very thin part so the viewer can colour it
    aa_x0, aa_y0 = DISP_X0 + DISP_AA_DX, DISP_Y0 + DISP_AA_DY
    p["display_active_area"] = block(DISP_ACTIVE_W, DISP_ACTIVE_H, 0.05, aa_x0, aa_y0,
                                     DISP_Z + DISP_T - 0.05)

    p["cover_lens"] = rrect(LENS_W, LENS_H, LENS_T, LENS_R, LENS_INSET, LENS_Y0, LENS_Z)

    # black print on the underside of the lens, open over the active area
    mask = rrect(LENS_W, LENS_H, 0.05, LENS_R, LENS_INSET, LENS_Y0, LENS_Z)
    mask = mask.cut(block(DISP_ACTIVE_W + 0.6, DISP_ACTIVE_H + 0.6, 1, aa_x0 - 0.3, aa_y0 - 0.3, LENS_Z - 0.5))
    for (wx, wy, wd) in (WIN_SENSOR, WIN_LED):     # clear windows over the light sensor and charge LED
        mask = mask.cut(cq.Workplane("XY").circle(wd / 2).extrude(1).translate((wx, wy, LENS_Z - 0.5)))
    p["lens_mask"] = mask

    # buttons (plungers through the side walls)
    btn = None
    wall_in = CAVITY_INSET_BACK
    for y in BTN_RIGHT_Y:
        b = rrect(wall_in + BTN_PROUD + 0.6, BTN_L, BTN_T, 1.0,
                  BODY_W - wall_in - 0.6, y - BTN_L / 2, BTN_Z - BTN_T / 2)
        btn = b if btn is None else btn.union(b)
    for y in BTN_LEFT_Y:
        btn = btn.union(rrect(wall_in + BTN_PROUD + 0.6, BTN_L, BTN_T, 1.0,
                              -BTN_PROUD, y - BTN_L / 2, BTN_Z - BTN_T / 2))
    p["buttons"] = btn

    # front soft keys: a round cap with a retaining flange under the bezel face
    def key(x):
        base = PCB_Z + PCB_T + KEY_SW_T
        cap = cq.Workplane("XY").circle(KEY_D / 2).extrude(BODY_D + KEY_PROUD - base).translate((x, KEY_Y, base))
        cap = cap.faces(">Z").edges().fillet(0.6)
        flange = cq.Workplane("XY").circle(KEY_D / 2 + 0.8).extrude(0.8).translate((x, KEY_Y, base))
        return cap.union(flange)
    p["front_keys"] = key(KEY_X[0]).union(key(KEY_X[1]))
    p["key_primary"] = key(KEY_X[2])          # right key (start / pause), accent colour

    spk = rrect(SPK_W, SPK_H, SPK_T, 1.2, SPK_X0, SPK_Y0, SPK_Z)
    p["speaker"] = spk
    p["speaker_membrane"] = rrect(SPK_W - 2.5, SPK_H - 2.5, 0.05, 0.8, SPK_X0 + 1.25, SPK_Y0 + 1.25, SPK_Z - 0.05)
    p["oring"] = oring()
    p["usb_flap"] = rrect(13.0, 0.8, 6.0, 0.35, (BODY_W - 13) / 2, -0.8, USB_Z - 3.0)
    p["display_ffc"] = block(DISP_FFC_W, 27.8, 0.3, DISP_FFC_X0, DISP_Y0 + 0.5, PCB_Z + PCB_T + 1.0)
    return p


def oring():
    mid = (CAVITY_INSET_BACK) / 2
    outer = outline(mid - ORING_W / 2, ORING_D, SPLIT_Z - ORING_D)
    inner = outline(mid + ORING_W / 2, ORING_D + 1, SPLIT_Z - ORING_D - 0.5)
    return outer.cut(inner)


# ------------------------------------------------------------------ shells
def mount_boss():
    cx, cy = BODY_W / 2, MOUNT_CY
    boss = cq.Workplane("XY").circle(MOUNT_D / 2).extrude(MOUNT_H).translate((cx, cy, -MOUNT_H))
    tabs = (cq.Workplane("XY").rect(MOUNT_TAB_SPAN, MOUNT_TAB_W).extrude(MOUNT_TAB_T)
            .edges("|Z").fillet(1.5).translate((cx, cy, -MOUNT_H)))
    neck = cq.Workplane("XY").circle(MOUNT_D / 2 - 2.5).extrude(0.01)
    return boss.union(tabs)


def back_shell(back_fillet=1.5):
    s = outline(0, SPLIT_Z, 0)
    s = s.faces("<Z").edges().fillet(back_fillet)
    cav = outline(CAVITY_INSET_BACK, SPLIT_Z, WALL)
    s = s.cut(cav)
    # 0.5 mm pocket for the cell (floor stays 1.0 mm) - more room between the cell and the ESP32 module
    s = s.cut(rrect(BATT_W + 0.6, BATT_H + 0.6, BATT_POCKET + 0.01, 1.8, BATT_X0 - 0.3, BATT_Y0 - 0.3, WALL - BATT_POCKET))
    # O-ring groove in the top rim
    s = s.cut(oring_groove())
    # PCB standoffs with M2 pilot holes
    for (x, y) in PCB_HOLES:
        post = cq.Workplane("XY").circle(2.4).extrude(PCB_Z - WALL).translate((x, y, WALL))
        hole = cq.Workplane("XY").circle(0.8).extrude(PCB_Z).translate((x, y, WALL))
        s = s.union(post).cut(hole)
    # speaker grille: slots through the floor under the speaker
    for i in range(GRILLE_SLOTS):
        y = SPK_Y0 + 2.5 + i * (SPK_H - 5) / (GRILLE_SLOTS - 1)
        s = s.cut(rrect(SPK_W - 4.5, 0.9, WALL + 2, 0.44, SPK_X0 + 2.25, y - 0.45, -1))
    # barometer vent (0.8 mm) in the right wall, behind a membrane sticker
    s = s.cut(cq.Workplane("YZ").circle(0.4).extrude(6).translate((BODY_W - 5, 44.0, 8.5)))
    s = s.union(mount_boss())
    s = s.cut(button_holes()).cut(usb_hole())
    return s


def oring_groove():
    mid = CAVITY_INSET_BACK / 2
    outer = outline(mid - ORING_W / 2 - 0.05, ORING_D + 0.1, SPLIT_Z - ORING_D)
    inner = outline(mid + ORING_W / 2 + 0.05, ORING_D + 2, SPLIT_Z - ORING_D - 1)
    return outer.cut(inner)


def button_holes(extra=0.3):
    h = None
    for y in BTN_RIGHT_Y:
        c = block(10, BTN_L + extra * 2, BTN_T + extra * 2,
                  BODY_W - 6, y - BTN_L / 2 - extra, BTN_Z - BTN_T / 2 - extra)
        h = c if h is None else h.union(c)
    for y in BTN_LEFT_Y:
        h = h.union(block(10, BTN_L + extra * 2, BTN_T + extra * 2,
                          -4, y - BTN_L / 2 - extra, BTN_Z - BTN_T / 2 - extra))
    return h


def usb_hole():
    hole = rrect(USB_CUT_W, 10, USB_CUT_H, 1.5, (BODY_W - USB_CUT_W) / 2, -5, USB_Z - USB_CUT_H / 2)
    # counterbore on the outside: USB-C plug overmolds are up to 12.35 x 6.5 mm (spec max)
    cb = rrect(USB_CBORE_W, USB_CBORE_D + 3, USB_CBORE_H, 2.0, (BODY_W - USB_CBORE_W) / 2, -3, USB_Z - USB_CBORE_H / 2)
    return hole.union(cb)


def front_bezel(front_fillet=1.2):
    t = BODY_D - SPLIT_Z
    s = outline(0, t, SPLIT_Z)
    s = s.faces(">Z").edges().fillet(front_fillet)
    # lens pocket
    s = s.cut(rrect(LENS_W + 0.2, LENS_H + 0.2, LENS_T + 1, LENS_R + 0.1,
                    LENS_INSET - 0.1, LENS_Y0 - 0.1, LENS_Z))
    # window behind the lens (display, top band), leaving a 1.5 mm ledge for the lens
    top = BODY_H - BEZEL_INNER_INSET
    s = s.cut(rrect(BODY_W - 2 * BEZEL_INNER_INSET, top - (LENS_Y0 + 1.5), t + 1, LENS_R - 1.5,
                    BEZEL_INNER_INSET, LENS_Y0 + 1.5, SPLIT_Z - 0.5))
    # hollow under the key-row face so the bezel is a 1.5 mm shell there
    lower = outline(CAVITY_INSET_BACK, t + 1, SPLIT_Z - 0.5).intersect(
        block(BODY_W, LENS_Y0 + 1.5, BODY_D - FACE_T - SPLIT_Z + 0.5, 0, 0, SPLIT_Z - 0.5))
    s = s.cut(lower)
    # relief over the GPS patch: the lens ledge stays, the patch tucks under it
    s = s.cut(block(ANT["w"] + 4, 6, LENS_Z - 0.7 - SPLIT_Z + 0.5, (BODY_W - ANT["w"] - 4) / 2,
                    top - 2, SPLIT_Z - 0.5))
    # key holes
    for x in KEY_X:
        s = s.cut(cq.Workplane("XY").circle(KEY_D / 2 + KEY_HOLE_CLEAR).extrude(4)
                  .translate((x, KEY_Y, BODY_D - FACE_T - 1)))
    # tongue that presses the O-ring
    mid = CAVITY_INSET_BACK / 2
    tongue = outline(mid - 0.4, 0.4, SPLIT_Z - 0.4).cut(outline(mid + 0.4, 2, SPLIT_Z - 1))
    return s.union(tongue).cut(usb_hole())       # the USB counterbore crosses the split line


def aero_back_shell():
    # softer, larger back-edge radius (wall stays >= 1.5 mm)
    return back_shell(back_fillet=4.5)


def rugged_bumper():
    z0, top = 0.8, BODY_D + 0.6          # raised 0.6 mm lip protects the lens
    outer = outline(-BUMPER_T, top - z0, z0)
    outer = outer.edges("|Z").fillet(0.01) if False else outer
    inner = outline(-0.05, top - z0 + 2, z0 - 1)
    ring = outer.cut(inner)
    # front lip wraps 1 mm over the bezel edge
    lip = outline(-BUMPER_T, 0.6, BODY_D).cut(outline(1.0, 2, BODY_D - 0.5))
    ring = ring.union(lip)
    # corner guards
    for (x, y) in [(CORNER_R * 0.55, CORNER_R * 0.55), (BODY_W - CORNER_R * 0.55, CORNER_R * 0.55),
                   (CORNER_R * 0.55, BODY_H - CORNER_R * 0.55),
                   (BODY_W - CORNER_R * 0.55, BODY_H - CORNER_R * 0.55)]:
        dx = -1 if x < BODY_W / 2 else 1
        dy = -1 if y < BODY_H / 2 else 1
        g = (cq.Workplane("XY").circle(5.5).extrude(top - z0)
             .translate((x + dx * 1.2, y + dy * 1.2, z0)))
        ring = ring.union(g.cut(outline(-0.05, top, z0 - 1)))
    # openings for buttons (knurled covers) and USB-C
    ring = ring.cut(button_holes(extra=0.6)).cut(
        rrect(USB_CUT_W + 4, 12, USB_CUT_H + 3.5, 2.0,
              (BODY_W - USB_CUT_W - 4) / 2, -6, USB_Z - (USB_CUT_H + 3.5) / 2))
    return ring


def knurled_button_covers():
    cov = None
    for (x0, ys, sgn) in [(BODY_W + BUMPER_T - 0.8, BTN_RIGHT_Y, 1), (-BUMPER_T - 0.6, BTN_LEFT_Y, -1)]:
        for y in ys:
            c = rrect(1.4, BTN_L + 1.0, BTN_T + 1.0, 0.6, x0, y - (BTN_L + 1) / 2, BTN_Z - (BTN_T + 1) / 2)
            for i in range(4):  # ridges
                c = c.union(block(0.5, 0.8, BTN_T + 1.0, x0 + (1.3 if sgn > 0 else -0.4),
                                  y - 3.6 + i * 2.2, BTN_Z - (BTN_T + 1) / 2))
            cov = c if cov is None else cov.union(c)
    return cov


# --------------------------------------------------------------------- run
def build():
    parts = internal_parts()
    shells = {
        "std_back_shell": back_shell(),
        "std_front_bezel": front_bezel(),
        "aero_back_shell": aero_back_shell(),
        "aero_front_bezel": front_bezel(front_fillet=2.5),
        "rugged_bumper": rugged_bumper(),
        "rugged_button_covers": knurled_button_covers(),
    }
    return parts, shells


def export(parts, shells):
    (OUT / "step").mkdir(parents=True, exist_ok=True)
    (OUT / "stl").mkdir(parents=True, exist_ok=True)
    meta = {}
    for name, wp in {**parts, **shells}.items():
        cq.exporters.export(wp, str(OUT / "step" / f"{name}.step"))
        cq.exporters.export(wp, str(OUT / "stl" / f"{name}.stl"),
                            tolerance=0.05, angularTolerance=0.2)
        bb = wp.val().BoundingBox()
        meta[name] = dict(volume_mm3=round(wp.val().Volume(), 1),
                          bbox=[round(v, 2) for v in (bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax)])
    # full assemblies as single STEP files
    for variant, names in {
        "assembly_standard": ["std_back_shell", "std_front_bezel"],
        "assembly_aero": ["aero_back_shell", "aero_front_bezel"],
        "assembly_rugged": ["std_back_shell", "std_front_bezel", "rugged_bumper", "rugged_button_covers"],
    }.items():
        a = cq.Assembly(name=variant)
        for n, wp in parts.items():
            a.add(wp, name=n)
        for n in names:
            a.add(shells[n], name=n)
        a.save(str(OUT / "step" / f"{variant}.step"))
    (OUT / "parts.json").write_text(json.dumps(meta, indent=1))
    return meta


if __name__ == "__main__":
    parts, shells = build()
    meta = export(parts, shells)
    for k, v in meta.items():
        print(f"{k:24s} {v['volume_mm3']:>9} mm3  bbox {v['bbox']}")
