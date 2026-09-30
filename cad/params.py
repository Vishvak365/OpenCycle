"""OpenCycle bike computer - all dimensions in millimetres.

Coordinate system (device lying face-up on a table):
  X = width  (left/right when you look at the screen)
  Y = height (bottom edge with USB-C at Y=0, top edge at Y=BODY_H)
  Z = depth  (back of the body at Z=0, front glass at Z=BODY_D;
              the Garmin mount boss sits at negative Z)

Component dimensions are nominal datasheet values. Verify every one
against the exact part you buy before ordering PCBs or printing cases.
"""

# ---------------------------------------------------------------- body
BODY_W = 52.0          # X
BODY_H = 92.4          # Y  (v0.2: 15 mm top band for the 12 mm GPS patch)
BODY_D = 17.0          # Z, back face to front of cover lens (v0.2: TFT is 2.55 mm thick)
CORNER_R = 7.0         # plan-view corner radius
WALL = 1.5             # shell wall / floor thickness
SPLIT_Z = 11.0         # front bezel / back shell split plane
CLEAR = 0.3            # general part-to-case clearance

# ------------------------------------------------------ Garmin mount boss
# Approximate male quarter-turn interface. Cross-check against a
# published Garmin-compatible mount model before relying on the fit.
MOUNT_D = 21.0         # boss diameter
MOUNT_H = 3.0          # boss height (below Z=0)
MOUNT_TAB_SPAN = 27.0  # tip-to-tip across the two tabs
MOUNT_TAB_W = 7.0
MOUNT_TAB_T = 1.6      # tab thickness at the tip of the boss
MOUNT_CY = BODY_H * 0.55

# --------------------------------------------------------------- PCB
PCB_W, PCB_H, PCB_T = 46.0, 86.4, 1.0
PCB_R = 4.0
PCB_Z = 10.0                       # back face of PCB
PCB_X0 = (BODY_W - PCB_W) / 2      # 3.0
PCB_Y0 = (BODY_H - PCB_H) / 2      # 3.0
PCB_HOLE_D = 2.2                   # M2 clearance
PCB_HOLE_INSET = 3.5

# --------------------------------- display (Newhaven NHD-2.4-240320AF-CSXP)
# 2.4" IPS TFT, 240 x 320 portrait. Numbers from Newhaven drawing Rev 2B.
DISP_W, DISP_H, DISP_T = 42.80, 59.91, 2.55
DISP_ACTIVE_W, DISP_ACTIVE_H = 36.72, 48.96
DISP_AA_DX, DISP_AA_DY = 3.04, 7.93          # active area offset from the outline's left / bottom edge
DISP_TOP_BAND = 15.6                          # body top edge to display top edge (patch + 0.3 mm edge clearance)
DISP_X0 = (BODY_W - DISP_W) / 2               # 4.6
DISP_Y0 = BODY_H - DISP_TOP_BAND - DISP_H     # 17.09
DISP_Z = BODY_D - 1.0 - DISP_T                # sits against the lens: 13.45
DISP_FFC_W = 20.5                             # FFC tail width; exits the bottom edge, folds behind
DISP_FFC_X0 = DISP_X0 + DISP_W - 11.15 - DISP_FFC_W   # tail is 11.15 from the left edge in rear view

# ------------------------------------------------------------ cover lens
LENS_T = 1.0
LENS_Z = BODY_D - LENS_T           # 16.0
LENS_INSET = 2.0                   # bezel lip around the lens
LENS_Y0 = 14.5                     # lens stops above the front key row

# ------------------------------------------------------------- foam gasket
FOAM_T = 0.5
FOAM_W = 2.0

# ------------------------------------------------------------ battery (LiPo)
BATT_W, BATT_H, BATT_T = 34.0, 62.0, 5.0     # Adafruit 258, 1200 mAh, protected (Mouser 485-258)
BATT_X0 = (BODY_W - BATT_W) / 2
BATT_Y0 = 20.5
BATT_POCKET = 0.5                            # floor thinned to 1.0 mm under the cell
BATT_Z = WALL - BATT_POCKET + 0.1

# ------------------------------------------------ board parts (from pcb/design.py; cad_y = BODY_H - kicad_y)
# x0/y0 = lower-left corner in CAD coordinates, t = height above/below the PCB face.
ESP = dict(name="esp32_s3_wroom_1", w=25.5, h=18.0, t=3.25, x0=23.5, y0=BODY_H - 30.0, side="B")   # antenna at the right edge
BLE = dict(name="bl652", w=14.0, h=10.0, t=2.2, x0=3.0, y0=BODY_H - 27.0, side="B")                # antenna at the left edge
GNSS = dict(name="gnss_max_m10s", w=9.7, h=10.1, t=2.5, x0=9.45, y0=BODY_H - 14.65, side="F")
JST = dict(name="battery_jst_ph", w=7.6, h=7.9, t=6.0, x0=39.2, y0=BODY_H - 81.95, side="B")
USBC = dict(name="usb_c", w=8.94, h=7.36, t=3.26)
USB_Y0 = BODY_H - 90.28                       # receptacle mouth (KiCad y 90.28) -> 2.12 mm behind the case face

# ------------------------------------------------ front-side (Z above PCB)
ANT = dict(name="gnss_patch_antenna", w=12.0, h=12.0, t=4.0)   # Taoglas DSGP.1575.12.4.A.02
ANT_X0 = 27.2 - 6.0                                            # patch centre at KiCad (27.2, 9.4)
ANT_Y0 = BODY_H - 9.4 - 6.0                                    # 77.0
# lens-mask windows in the top band (centres, CAD coords) over the light sensor and the charge LED
WIN_SENSOR = (40.8, BODY_H - 9.4, 1.6)
WIN_LED = (37.0, BODY_H - 9.4, 1.2)

# ------------------------------------------------------------- buttons
# Front: three unlabelled soft keys under the screen, labels drawn on the display.
KEY_D = 9.0                                   # key cap diameter
KEY_Y = 8.7                                   # key centre height
KEY_X = tuple(DISP_X0 + DISP_AA_DX + DISP_ACTIVE_W * (i + 0.5) / 3 for i in range(3))  # under each label cell
KEY_PROUD = 0.8                               # above the front face
KEY_SW_T = 2.5                                # C&K PTS810 top-actuated tact switch, 4.2 x 3.2 x 2.5 mm
# Sides: left = power / back, right = menu.
BTN_L, BTN_T, BTN_PROUD = 8.0, 3.0, 1.0      # length (Y), thickness (Z), protrusion
BTN_Z = 8.5                                  # button centre height
BTN_RIGHT_Y = (BODY_H - 34.0,)   # menu (SW5 at KiCad y 34.0)
BTN_LEFT_Y = (BODY_H - 34.0,)    # power / back (SW4)

# ------------------------------------------------------------- USB-C port
USB_CUT_W, USB_CUT_H = 10.0, 4.2
USB_Z = PCB_Z - USBC["t"] / 2               # port centre height
USB_CBORE_W, USB_CBORE_H, USB_CBORE_D = 12.8, 7.0, 1.9   # outside pocket so the plug overmold reaches the port

# ------------------------------------------------------- O-ring groove
ORING_W, ORING_D = 1.2, 0.8

# ------------------------------------------------------- rugged bumper
BUMPER_T = 2.0

# ------------------------------------------------------------- speaker
SPK_W, SPK_H, SPK_T = 15.0, 11.0, 2.5       # Same Sky CMS-151125-078L100, fires through the floor
SPK_X0, SPK_Y0 = (BODY_W - SPK_W) / 2, 8.0
SPK_Z = WALL + 0.3                          # sits on a 0.3 mm foam gasket
GRILLE_SLOTS = 5
