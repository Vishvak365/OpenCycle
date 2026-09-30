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
BODY_H = 86.0          # Y
BODY_D = 16.0          # Z, back face to front of cover lens
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
PCB_W, PCB_H, PCB_T = 46.0, 80.0, 1.0
PCB_R = 4.0
PCB_Z = 10.0                       # back face of PCB
PCB_X0 = (BODY_W - PCB_W) / 2      # 3.0
PCB_Y0 = (BODY_H - PCB_H) / 2      # 3.0
PCB_HOLE_D = 2.2                   # M2 clearance
PCB_HOLE_INSET = 3.5

# ------------------------------------------------ display (Sharp LS027B7DH01)
# Mounted portrait: 400x240 landscape panel rotated 90 degrees.
DISP_W, DISP_H, DISP_T = 42.8, 62.8, 1.7
DISP_ACTIVE_W, DISP_ACTIVE_H = 35.0, 59.0
DISP_Y0 = 4.0
DISP_Z = 13.3

# ------------------------------------------------------------ cover lens
LENS_T = 1.0
LENS_Z = BODY_D - LENS_T           # 15.0
LENS_INSET = 2.0                   # bezel lip around the lens

# ------------------------------------------------------------- foam gasket
FOAM_T = 0.5
FOAM_W = 2.0

# ------------------------------------------------------------ battery (LiPo)
BATT_W, BATT_H, BATT_T = 30.0, 48.0, 8.0     # 30 x 48 pouch (803048 ~1100 mAh; 10 mm cell needs a thicker case)
BATT_X0 = 8.0
BATT_Y0 = 12.3
BATT_Z = WALL + 0.1

# ------------------------------------- modules on PCB back side (Z below PCB)
NRF = dict(name="nrf52840", w=10.0, h=15.5, t=2.2)     # e.g. Raytac MDBT50Q
GNSS = dict(name="gnss_max_m10s", w=10.0, h=10.1, t=2.5)
USD = dict(name="microsd", w=14.0, h=15.0, t=1.8)
USBC = dict(name="usb_c", w=9.0, h=7.3, t=3.2)

# ------------------------------------------------ front-side (Z above PCB)
ANT = dict(name="gnss_patch_antenna", w=15.0, h=15.0, t=4.0)
ANT_Y0 = 67.2

# ------------------------------------------------------------- buttons
BTN_L, BTN_T, BTN_PROUD = 8.0, 3.0, 1.0      # length (Y), thickness (Z), protrusion
BTN_Z = 8.5                                  # button centre height
BTN_RIGHT_Y = (52.0, 36.0)       # upper: lap/page, lower: start/stop
BTN_LEFT_Y = (52.0,)             # power / backlight

# ------------------------------------------------------------- USB-C port
USB_CUT_W, USB_CUT_H = 10.0, 4.2
USB_Z = PCB_Z - USBC["t"] / 2               # port centre height

# ------------------------------------------------------- O-ring groove
ORING_W, ORING_D = 1.2, 0.8

# ------------------------------------------------------- rugged bumper
BUMPER_T = 2.0

# ------------------------------------------------------------- speaker
SPK_W, SPK_H, SPK_T = 11.0, 15.0, 3.5       # 11 x 15 x 3.5 mm micro speaker, fires through the floor
SPK_X0, SPK_Y0 = 38.2, 15.5
SPK_Z = WALL + 0.3                          # sits on a 0.3 mm foam gasket
GRILLE_SLOTS = 5
