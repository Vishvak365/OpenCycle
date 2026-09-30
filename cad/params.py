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
DISP_TOP_BAND = 15.4                          # body top edge to display top edge
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
BATT_Z = WALL + 0.1

# ------------------------------------- modules on PCB back side (Z below PCB)
# Placeholder positions for the v0.2 board; the real placement comes from pcb/design.py.
ESP = dict(name="esp32_s3_wroom_1", w=18.0, h=25.5, t=3.1, x0=8.0, y0=58.0)   # antenna end at the top
BLE = dict(name="bl652", w=10.0, h=14.0, t=2.2, x0=38.0, y0=68.0)
GNSS = dict(name="gnss_max_m10s", w=9.7, h=10.1, t=2.5, x0=27.0, y0=72.0)
USBC = dict(name="usb_c", w=9.0, h=7.3, t=3.2)

# ------------------------------------------------ front-side (Z above PCB)
ANT = dict(name="gnss_patch_antenna", w=12.0, h=12.0, t=4.0)   # Taoglas DSGP.1575.12.4.A.02 class
ANT_Y0 = DISP_Y0 + DISP_H + 0.3                                  # just above the display: 77.3

# ------------------------------------------------------------- buttons
# Front: three unlabelled soft keys under the screen, labels drawn on the display.
KEY_D = 9.0                                   # key cap diameter
KEY_Y = 8.7                                   # key centre height
KEY_X = tuple(DISP_X0 + DISP_AA_DX + DISP_ACTIVE_W * (i + 0.5) / 3 for i in range(3))  # under each label cell
KEY_PROUD = 0.8                               # above the front face
KEY_SW_T = 1.5                                # top-actuated tact switch height (part still to source)
# Sides: left = power / back, right = menu.
BTN_L, BTN_T, BTN_PROUD = 8.0, 3.0, 1.0      # length (Y), thickness (Z), protrusion
BTN_Z = 8.5                                  # button centre height
BTN_RIGHT_Y = (58.9,)            # menu
BTN_LEFT_Y = (58.9,)             # power / back

# ------------------------------------------------------------- USB-C port
USB_CUT_W, USB_CUT_H = 10.0, 4.2
USB_Z = PCB_Z - USBC["t"] / 2               # port centre height

# ------------------------------------------------------- O-ring groove
ORING_W, ORING_D = 1.2, 0.8

# ------------------------------------------------------- rugged bumper
BUMPER_T = 2.0

# ------------------------------------------------------------- speaker
SPK_W, SPK_H, SPK_T = 15.0, 11.0, 2.5       # Same Sky CMS-151125-078L100, fires through the floor
SPK_X0, SPK_Y0 = (BODY_W - SPK_W) / 2, 8.0
SPK_Z = WALL + 0.3                          # sits on a 0.3 mm foam gasket
GRILLE_SLOTS = 5
