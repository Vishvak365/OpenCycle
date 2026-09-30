"""OpenCycle main board v0.2 (colour build) - single source of truth for parts, nets and placement.

Coordinates are KiCad board coordinates in mm (x right, y DOWN), viewed from the FRONT
(display side = F.Cu). Board outline x 3..49, y 3..89.4, which maps to the enclosure CAD as
    cad_x = x,  cad_y = 92.4 - y          (see cad/params.py)
side: "F" = front (faces the display), "B" = back (faces the battery). Back-side x is still
given as seen from the front.

part(ref, value, symbol, footprint, side, x, y, rot, pins, note, mpn=..., mfr=..., h=height_mm)
pins: symbol pin name (or number) -> net name, None = deliberately unconnected.

Pinouts were checked against these documents (2026-09-30):
  ESP32-S3-WROOM-1 datasheet v1.x (strapping pins GPIO0/3/45/46; IO35-37 used by octal PSRAM on N16R8)
  Newhaven NHD-2.4-240320AF-CSXP rev 7 (4-wire SPI: IM2..0 = 1,1,0; pin 11 = SCL, pin 12 = DCX;
      RDX, DB0-DB15, IM0 to GND per the 4-wire wiring diagram)
  u-blox MAX-M10S data sheet UBX-20035208 R02 (pin 15 is "Reserved": leave open; V_IO tied to VCC)
  Bosch BMP581 BST-BMP581-DS004-13 Table 28 (1 VDDIO, 2 SCK, 3 VSS, 4 SDI, 5 SDO, 6 CSB, 7 INT,
      8 VSS, 9 VSS, 10 VDD); I2C: CSB to VDDIO, SDO to GND -> address 0x46, INT to GND (disabled)
  Taoglas DSGP.1575.12.4.A.02 §6.5 footprint (pin 1 feed, 2-9 ground)
  Diodes AP7361C (SOT-223 'E': 1 IN, 2 GND/tab, 3 OUT)
"""

FP = "/usr/share/kicad/footprints/"

PARTS = []


def part(ref, value, sym, fp, side, x, y, rot, pins, note="", mpn="", mfr="", h=1.0, dnp=False):
    sl, sn = sym.split(":")
    fl, fn = fp.split(":")
    PARTS.append(dict(ref=ref, value=value, slib=sl, sym=sn, flib=fl, fp=fn, side=side, x=x, y=y, rot=rot,
                      pins=pins, note=note, mpn=mpn, mfr=mfr, h=h, dnp=dnp))


R0402 = "Resistor_SMD:R_0402_1005Metric"
R0603 = "Resistor_SMD:R_0603_1608Metric"
C0402 = "Capacitor_SMD:C_0402_1005Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"
C0805 = "Capacitor_SMD:C_0805_2012Metric"

# common passives (Mouser-stocked MPNs; see docs/sourcing/bom-v0.2.md)
CAP = {
    "100nF": ("CL05B104KO5NNNC", "Samsung", C0402, 0.55),
    "1uF": ("CL05A105KO5NNNC", "Samsung", C0402, 0.55),
    "4.7uF": ("CL10A475KO8NNNC", "Samsung", C0603, 0.9),
    "10uF": ("CL10A106KP8NNNC", "Samsung", C0603, 0.9),
    "22uF": ("CL21A226MAQNNNE", "Samsung", C0805, 1.35),
}
RES = {
    "33R": "RC0603FR-0733RL", "100R": "RC0402FR-07100RL", "1k": "RC0402FR-071KL", "2k": "RC0402FR-072KL",
    "4.7k": "RC0402FR-074K7L", "5.1k": "RC0402FR-075K1L", "10k": "RC0402FR-0710KL", "100k": "RC0402FR-07100KL",
    "1M": "RC0402FR-071ML", "0R": "RC0402JR-070RL",
}


def C(ref, val, side, x, y, rot, a, b="GND", note=""):
    mpn, mfr, fp, h = CAP[val]
    part(ref, val, "Device:C", fp, side, x, y, rot, {"1": a, "2": b}, note, mpn, mfr, h)


def R(ref, val, side, x, y, rot, a, b, note=""):
    fp = R0603 if val == "33R" else R0402
    part(ref, val, "Device:R", fp, side, x, y, rot, {"1": a, "2": b}, note, RES[val], "Yageo", 0.55)


# ============================================================ main MCU (back, antenna at the right edge)
ESP_PINS = {
    "GND": "GND", "3V3": "+3V3", "EN": "ESP_EN",
    "IO0": "KEY_L",            # strapping: low at reset = download mode (hold left key)
    "IO1": "VBAT_SENSE", "IO2": "VBUS_SENSE",      # ADC1
    "IO3": "AMP_EN",           # strapping (JTAG source, ignored unless eFuse set); 100k pull-down
    "IO4": "KEY_C", "IO5": "KEY_R", "IO6": "BTN_PWR", "IO7": "BTN_MENU",   # RTC GPIOs: wake from deep sleep
    "IO8": "I2C_SDA", "IO18": "I2C_SCL",
    "IO9": "LCD_DC", "IO10": "LCD_CS", "IO11": "LCD_MOSI", "IO12": "LCD_SCK",   # FSPI IO_MUX pins
    "IO13": "LCD_TE", "IO14": "LCD_RST", "IO21": "LCD_BL",
    "IO15": "I2S_BCLK", "IO16": "I2S_LRCLK", "IO17": "I2S_DIN",
    "IO19": "USB_DN", "IO20": "USB_DP",
    "IO38": "GPS_TX", "IO39": "GPS_RX", "IO40": "GPS_RST", "IO48": "GPS_EXTINT",
    "IO41": "BLE_TX", "IO42": "BLE_RX", "IO47": "BLE_RST",
    "IO35": None, "IO36": None, "IO37": None,      # octal PSRAM on N16R8 - not available
    "IO45": None, "IO46": None,                    # strapping pins, left at their internal pull-downs
    "TXD0": "CON_TX", "RXD0": "CON_RX",
}
ESP_X, ESP_Y = 36.25, 21.0
part("U1", "ESP32-S3-WROOM-1-N16R8", "RF_Module:ESP32-S3-WROOM-1", "RF_Module:ESP32-S3-WROOM-1", "B",
     ESP_X, ESP_Y, 90, ESP_PINS,
     "Main MCU: UI, logging, Wi-Fi, BLE, native USB. PCB antenna at the right board edge with a copper keep-out.",
     "ESP32-S3-WROOM-1-N16R8", "Espressif", 3.25)
C("C1", "22uF", "B", 21.6, 14.6, 90, "+3V3")
C("C2", "100nF", "B", 21.6, 17.4, 90, "+3V3")
R("R1", "10k", "B", 21.6, 26.4, 90, "+3V3", "ESP_EN", "EN pull-up")
C("C3", "1uF", "B", 21.6, 28.6, 90, "ESP_EN", "GND", "EN reset delay (10k x 1uF)")

# ============================================================ ANT+ / BLE sensor coprocessor (back, antenna at the left edge)
part("U2", "BL652-SA-01", "RF_Bluetooth:BL652", "RF_Module:Laird_BL652", "B", 11.05, 22.0, 180, {
    "GND": "GND", "VDD": "+3V3", "SWDIO": "BLE_SWDIO", "SWDCLK": "BLE_SWDCLK",
    "SIO_21": "BLE_RST",       # nRF52832 P0.21 = nRESET
    "SIO_06": "BLE_TX", "SIO_08": "BLE_RX",       # module UART (Laird default TX/RX pins)
    **{k: None for k in ["SIO_24", "SIO_23", "SIO_22", "SIO_20", "SIO_18", "SIO_16", "SIO_14", "SIO_12", "SIO_11",
                         "SIO_10/NFC2", "SIO_09/NFC1", "SIO_07", "SIO_05/AIN3", "SIO_04/AIN2", "SIO_03/AIN1",
                         "SIO_02/AIN0", "SIO_01", "SIO_00", "SIO_13", "SIO_15", "SIO_17", "SIO_19",
                         "SIO_31/AIN7", "SIO_30/AIN6", "SIO_29/AIN5", "SIO_28/AIN4", "SIO_27", "SIO_26", "SIO_25"]},
}, "nRF52832 module running an ANT+/BLE sensor bridge; talks to the ESP32 over UART.", "BL652-SA-01-T/R", "Ezurio", 2.2)
C("C4", "10uF", "B", 13.6, 29.4, 0, "+3V3")
C("C5", "100nF", "B", 16.2, 29.4, 0, "+3V3")
part("J4", "SWD (BL652)", "Connector:Conn_ARM_SWD_TagConnect_TC2030-NL",
     "Connector:Tag-Connect_TC2030-IDC-NL_2x03_P1.27mm_Vertical", "B", 12.5, 33.6, 0, {
         "VCC": "+3V3", "SWDIO": "BLE_SWDIO", "~{RESET}": "BLE_RST", "SWCLK": "BLE_SWDCLK", "GND": "GND",
         "SWO": None}, "Tag-Connect pads: programs the BL652. Nothing to assemble.", "", "", 0.0)

# ============================================================ GPS (front, top band, left of the patch)
part("U3", "MAX-M10S", "RF_GPS:MAX-M10S", "RF_GPS:ublox_MAX", "F", 14.3, 9.6, 0, {
    "GND": "GND", "TXD": "GPS_TX", "RXD": "GPS_RX", "TIMEPULSE": None, "EXTINT": "GPS_EXTINT",
    "V_BCKP": "+3V3", "VCC_IO": "+3V3", "VCC": "+3V3", "~{RESET}": "GPS_RST", "RF_IN": "RF_IN",
    "LNA_EN": None, "VCC_RF": None, "VIO_SEL": None, "SDA": None, "SCL": None, "~{SAFEBOOT}": None,
}, "u-blox M10. Pin 15 is 'Reserved' on the MAX-M10S (KiCad names it VIO_SEL): left open.",
    "MAX-M10S-00B", "u-blox", 2.5)
C("C6", "10uF", "F", 11.4, 16.9, 0, "+3V3")
C("C7", "100nF", "F", 14.4, 16.9, 0, "+3V3")
part("AE1", "DSGP.1575.12.4.A.02", "OpenCycle:DSGP.1575.12.4.A.02", "OpenCycle:Taoglas_DSGP.1575.12.4.A.02_12x12mm",
     "F", 26.0, 9.4, -90, {"FEED": "RF_IN", "GND": "GND"},
     "12 mm ceramic patch, feed toward the receiver. RF_IN is a short hand-placed 0.2 mm trace over the In1 ground plane.",
     "DSGP.1575.12.4.A.02", "Taoglas", 4.0)

# ============================================================ status window parts (front, top band, right)
part("D1", "Green", "Device:LED", "LED_SMD:LED_0603_1608Metric", "F", 37.0, 9.4, 0, {"K": "CHG_STAT", "A": "LED_A"},
     "Charge LED behind the lens window (lit while charging).", "LTST-C191KGKT", "Lite-On", 0.8)
R("R2", "1k", "F", 37.0, 11.4, 0, "VBUS", "LED_A")
part("U4", "LTR-303ALS-01", "Sensor_Optical:LTR-303ALS-01", "OptoDevice:Lite-On_LTR-303ALS-01", "F", 40.8, 9.4, 0, {
    "VDD": "+3V3", "NC": None, "GND": "GND", "SCL": "I2C_SCL", "INT": None, "SDA": "I2C_SDA"},
    "Ambient light sensor behind the lens window; auto-dims the backlight. I2C 0x29.", "LTR-303ALS-01", "Lite-On", 0.7)
C("C8", "100nF", "F", 40.8, 12.2, 0, "+3V3")
R("R3", "4.7k", "F", 37.0, 13.4, 0, "+3V3", "I2C_SDA")
R("R4", "4.7k", "F", 39.2, 13.9, 0, "+3V3", "I2C_SCL")

# ============================================================ display (front, FFC folded behind the panel)
DISP = {"Pin_1": "GND", "Pin_2": None, "Pin_3": None, "Pin_4": None, "Pin_5": None, "Pin_6": None,
        "Pin_7": "+3V3", "Pin_8": "+3V3", "Pin_9": "LCD_MOSI", "Pin_10": "LCD_CS", "Pin_11": "LCD_SCK",
        "Pin_12": "LCD_DC", "Pin_13": "GND", "Pin_30": "LCD_RST", "Pin_31": "GND", "Pin_32": "+3V3", "Pin_33": "+3V3",
        "Pin_34": "LED_K1", "Pin_35": "LED_K2", "Pin_36": "LED_K3", "Pin_37": "LED_K4", "Pin_38": "VBAT",
        "Pin_39": "GND", "Pin_40": "LCD_TE", "MountPin": "GND"}
DISP.update({f"Pin_{i}": "GND" for i in range(14, 30)})      # DB0-DB15 unused in SPI mode
part("J3", "FH12-40S-0.5SH(55)", "Connector_Generic_MountingPin:Conn_01x40_MountingPin",
     "Connector_FFC-FPC:Hirose_FH12-40S-0.5SH_1x40-1MP_P0.50mm_Horizontal", "F", 26.0, 48.7, 0, DISP,
     "Newhaven NHD-2.4-240320AF-CSXP, bottom-contact FFC. Pin 1 left. Cable enters from below after folding behind the panel.",
     "FH12-40S-0.5SH(55)", "Hirose", 2.0)
C("C9", "10uF", "F", 18.6, 43.4, 90, "+3V3")
C("C10", "100nF", "F", 20.6, 43.4, 90, "+3V3")
# backlight: LEDA from VBAT, each cathode through 33R to a PWM low-side switch.
# (VBAT 4.2 V - Vf 2.7 V min) / 33R = 45 mA per LED max (datasheet max 200 mA total); ~21 mA typ at 3.7 V.
for i, x in enumerate((31.6, 33.3, 35.0, 36.7), 1):
    R(f"R{4 + i}", "33R", "F", x, 43.6, 90, f"LED_K{i}", "BL_SW", f"Backlight LED {i} ballast (0603 for dissipation)")
part("Q1", "DMG2302U", "Transistor_FET:DMG2302U", "Package_TO_SOT_SMD:SOT-23", "F", 40.2, 43.8, 0,
     {"G": "BL_G", "S": "GND", "D": "BL_SW"}, "Backlight PWM switch", "DMG2302UK-7", "Diodes", 1.1)
R("R9", "100R", "F", 40.2, 40.6, 0, "LCD_BL", "BL_G")
R("R10", "100k", "F", 43.4, 43.8, 90, "BL_G", "GND", "Backlight off while the ESP32 boots")

# ============================================================ 3.3 V regulator (front, left, under the display)
part("U5", "AP7361C-33E", "Regulator_Linear:AP7361C-33E", "Package_TO_SOT_SMD:SOT-223-3_TabPin2", "F", 9.2, 33.0, 0,
     {"VI": "VBAT", "GND": "GND", "VO": "+3V3"}, "1 A LDO (ESP32 Wi-Fi peaks ~500 mA)", "AP7361C-33E-13", "Diodes", 1.8)
C("C11", "10uF", "F", 11.0, 27.6, 0, "VBAT")
C("C12", "22uF", "F", 6.6, 39.2, 90, "+3V3")
C("C13", "100nF", "F", 8.8, 39.2, 90, "+3V3")

# ============================================================ USB-C, charger, battery (back, bottom)
part("J1", "USB4105-GF-A", "Connector:USB_C_Receptacle_USB2.0_16P",
     "Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal", "B", 26.0, 86.6, 0, {
         "GND": "GND", "VBUS": "VBUS", "CC1": "CC1", "CC2": "CC2", "D+": "USB_DP_C", "D-": "USB_DN_C",
         "SBU1": None, "SBU2": None, "SHIELD": "GND"}, "USB 2.0 (ESP32 native USB) + charging", "USB4105-GF-A", "GCT", 3.3)
R("R11", "5.1k", "B", 19.8, 84.2, 90, "CC1", "GND")
R("R12", "5.1k", "B", 32.2, 84.2, 90, "CC2", "GND")
part("D2", "USBLC6-2SC6", "Power_Protection:USBLC6-2SC6", "Package_TO_SOT_SMD:SOT-23-6", "B", 26.0, 79.8, 0,
     {"I/O1": "USB_DP_C", "GND": "GND", "I/O2": "USB_DN_C", "VBUS": "VBUS"}, "USB ESD", "USBLC6-2SC6", "ST", 1.1)
R("R13", "0R", "B", 22.6, 78.2, 90, "USB_DP_C", "USB_DP", "USB D+ link (0R, lets the ESD part sit next to the connector)")
R("R14", "0R", "B", 29.4, 78.2, 90, "USB_DN_C", "USB_DN")
C("C14", "4.7uF", "B", 19.8, 80.6, 90, "VBUS")
part("U6", "MCP73831-2", "Battery_Management:MCP73831-2-OT", "Package_TO_SOT_SMD:SOT-23-5", "B", 34.6, 78.4, 0, {
    "STAT": "CHG_STAT", "V_{SS}": "GND", "V_{BAT}": "VBAT", "V_{DD}": "VBUS", "PROG": "CHG_PROG"},
    "Li-ion charger, 4.20 V, 500 mA", "MCP73831T-2ACI/OT", "Microchip", 1.1)
R("R15", "2k", "B", 34.6, 81.2, 0, "CHG_PROG", "GND", "500 mA charge current")
C("C15", "4.7uF", "B", 31.4, 78.4, 90, "VBUS")
C("C16", "4.7uF", "B", 37.6, 81.8, 90, "VBAT")
part("J2", "S2B-PH-SM4-TB", "Connector_Generic_MountingPin:Conn_01x02_MountingPin",
     "Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal", "B", 43.6, 78.0, 90,
     {"Pin_1": "GND", "Pin_2": "BATT+", "MountPin": "GND"},
     "JST-PH battery socket for the Adafruit 258 cell. Pin 1 = -, pin 2 = + (common JST-PH LiPo convention). "
     "Q2 blocks a reversed battery; still check polarity with a meter before first plug-in.",
     "S2B-PH-SM4-TB(LF)(SN)", "JST", 6.0)
part("Q2", "DMG2305UX", "Transistor_FET:DMG2301L", "Package_TO_SOT_SMD:SOT-23", "B", 36.0, 74.6, 0,
     {"G": "GND", "D": "BATT+", "S": "VBAT"}, "Reverse-battery protection (P-FET, gate to GND)", "DMG2305UX-7", "Diodes", 1.1)
R("R16", "1M", "B", 30.0, 40.0, 90, "VBAT", "VBAT_SENSE", "Battery voltage divider")
R("R17", "1M", "B", 31.4, 40.0, 90, "VBAT_SENSE", "GND")
C("C17", "100nF", "B", 32.8, 40.0, 90, "VBAT_SENSE")
R("R18", "100k", "B", 34.6, 40.0, 90, "VBUS", "VBUS_SENSE", "USB present detect")
R("R19", "100k", "B", 36.0, 40.0, 90, "VBUS_SENSE", "GND")

# ============================================================ audio (back, bottom left, next to the speaker)
part("U7", "MAX98357A", "Audio:MAX98357A", "Package_DFN_QFN:TQFN-16-1EP_3x3mm_P0.5mm_EP1.23x1.23mm", "B", 11.6, 79.0, 0, {
    "DIN": "I2S_DIN", "OUTN": "SPK-", "GND": "GND", "NC": None, "LRCLK": "I2S_LRCLK", "BCLK": "I2S_BCLK",
    "PAD": "GND", "GAIN_SLOT": "GND", "~{SD_MODE}": "AMP_EN", "VDD": "VBAT", "OUTP": "SPK+"},
    "I2S class-D amp, 12 dB (GAIN to GND); SD_MODE high = left channel", "MAX98357AETE+T", "Analog Devices", 0.8)
C("C18", "10uF", "B", 7.8, 75.4, 90, "VBAT")
C("C19", "100nF", "B", 9.6, 75.4, 90, "VBAT")
R("R20", "100k", "B", 14.6, 76.0, 90, "AMP_EN", "GND", "Amp off until firmware enables it")
part("LS1", "CMS-151125-078L100", "Device:Speaker", "OpenCycle:SpeakerPads_2.6mm", "B", 12.0, 84.6, 0,
     {"1": "SPK+", "2": "SPK-"}, "Pads for the speaker's 32 AWG leads (red = +).", "CMS-151125-078L100", "Same Sky", 0.1)

# ============================================================ sensors (back, right edge near the case vent)
part("U8", "BMP581", "OpenCycle:BMP581", "OpenCycle:Bosch_LGA-10_2x2mm_P0.5mm_BMP581", "B", 45.6, 48.4, 0, {
    "VDDIO": "+3V3", "VDD": "+3V3", "CSB": "+3V3", "SDO": "GND", "SCK": "I2C_SCL", "SDI": "I2C_SDA",
    "INT": "GND", "VSS": "GND"},
    "Barometer, I2C 0x46. No vias/traces under it (Bosch). Next to the vent in the right wall.", "BMP581", "Bosch", 0.8)
C("C20", "100nF", "B", 45.6, 51.4, 0, "+3V3")

# ============================================================ keys
KEY_Y = 92.4 - 8.7          # cad KEY_Y = 8.7
for ref, net, x in (("SW1", "KEY_L", 13.76), ("SW2", "KEY_C", 26.0), ("SW3", "KEY_R", 38.24)):
    part(ref, "PTS810", "Switch:SW_Push", "Button_Switch_SMD:SW_SPST_PTS810", "F", x, KEY_Y, 0, {"1": net, "2": "GND"},
         f"Front soft key ({net}). Top-actuated, 2.5 mm tall.", "PTS810 SJM 250 SMTR LFS", "C&K", 2.5)
part("SW4", "SKRTLAE010", "Switch:SW_Push", "Button_Switch_SMD:SW_Push_1P1T-MP_NO_Horizontal_Alps_SKRTLAE010", "B",
     5.45, 34.0, 90, {"1": "BTN_PWR", "2": "GND"}, "Left side: power / back", "SKRTLAE010", "Alps Alpine", 3.55)
part("SW5", "SKRTLAE010", "Switch:SW_Push", "Button_Switch_SMD:SW_Push_1P1T-MP_NO_Horizontal_Alps_SKRTLAE010", "B",
     46.55, 34.0, -90, {"1": "BTN_MENU", "2": "GND"}, "Right side: menu", "SKRTLAE010", "Alps Alpine", 3.55)
R("R21", "10k", "B", 25.0, 36.0, 90, "+3V3", "KEY_L", "Key pull-ups")
R("R22", "10k", "B", 26.4, 36.0, 90, "+3V3", "KEY_C")
R("R23", "10k", "B", 27.8, 36.0, 90, "+3V3", "KEY_R")
R("R24", "10k", "B", 29.2, 36.0, 90, "+3V3", "BTN_PWR")
R("R25", "10k", "B", 30.6, 36.0, 90, "+3V3", "BTN_MENU")

# ============================================================ ESP32 console / recovery (Tag-Connect footprint, back)
part("J5", "Console", "Connector_Generic:Conn_01x06", "Connector:Tag-Connect_TC2030-IDC-NL_2x03_P1.27mm_Vertical", "B",
     36.0, 34.0, 0, {"Pin_1": "+3V3", "Pin_2": "CON_TX", "Pin_3": "ESP_EN", "Pin_4": "CON_RX", "Pin_5": "GND",
                     "Pin_6": "KEY_L"},
     "ESP32 UART0 + EN + IO0 for recovery (normal flashing is over USB-C). Nothing to assemble.", "", "", 0.0)

# ============================================================ fiducials (3 per side, for machine assembly)
for i, (side, x, y) in enumerate((("F", 19.6, 88.0), ("F", 32.4, 88.0), ("F", 4.6, 45.0),
                                   ("B", 16.0, 88.4), ("B", 36.0, 88.4), ("B", 4.6, 60.0)), 1):
    part(f"FID{i}", "Fiducial", "Mechanical:Fiducial", "Fiducial:Fiducial_0.75mm_Mask1.5mm", side, x, y, 0, {},
         "", "", "", 0.0)

# ------------------------------------------------------------------ board
HOLES = [(6.5, 6.5), (45.5, 6.5), (6.5, 85.9), (45.5, 85.9)]
BOARD = dict(x0=3.0, y0=3.0, w=46.0, h=86.4, r=4.0, thickness=1.0)
CAD_H = 92.4          # enclosure body height: cad_y = CAD_H - y

POWER_NETS = {"VBAT": 0.5, "BATT+": 0.5, "VBUS": 0.5, "+3V3": 0.4, "BL_SW": 0.4, "SPK+": 0.3, "SPK-": 0.3,
              "USB_DP": 0.2, "USB_DN": 0.2, "RF_IN": 0.2}
PLANE_NETS = {"GND": "In1.Cu", "+3V3": "In2.Cu"}

# Keep-outs (board coords). "all": no copper on any layer (antennas).
KEEPOUTS = [
    dict(name="ESP32 antenna", rect=(42.3, 10.5, 49.5, 31.0), layers="all"),
    dict(name="BL652 antenna", rect=(2.5, 15.0, 9.0, 29.0), layers="all"),
]
NO_TRACKS_F = [dict(name="under patch", rect=(20.2, 3.6, 31.8, 15.2))]   # no F.Cu tracks under the ceramic
NO_TRACKS_B = [dict(name="under BMP581", rect=(44.4, 47.2, 46.8, 49.6))]

# Height limits (side, rect, max height mm) - from the enclosure stack in cad/params.py
HEIGHT_ZONES = [
    ("F", (4.6, 15.5, 47.4, 75.6), 2.15, "under the display (display back at z 13.45, PCB front at 11.0)"),
    ("F", (6.5, 62.3, 45.5, 76.6), 1.3, "under the folded FFC (wide shielded section)"),
    ("F", (15.6, 53.3, 36.4, 62.3), 1.3, "under the FFC tail"),
    ("B", (9.0, 9.9, 43.0, 71.9), 3.3, "over the battery (pocketed floor, 0.6 mm margin)"),
    ("B", (18.5, 73.4, 33.5, 84.4), 5.0, "over the speaker"),
]
BATTERY_KEEPOUT = (9.0, 9.9, 43.0, 71.9)
SPEAKER_KEEPOUT = (18.5, 73.4, 33.5, 84.4)
