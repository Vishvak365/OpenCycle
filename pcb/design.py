"""OpenCycle main board - single source of truth for parts, nets and placement.

Coordinates are KiCad board coordinates in mm (x right, y DOWN), viewed from
the FRONT (display side = F.Cu). Board outline x 3..49, y 3..83, which maps to
the enclosure CAD as  cad_x = x,  cad_y = 86 - y.

side: "F" = front/top (faces display), "B" = back (faces battery).
pins: symbol pin *name* (or number) -> net.
"""

FP = "/usr/share/kicad/footprints/"

# (ref, value, symbol lib, symbol, footprint lib, footprint, lcsc, side, x, y, rot, pins, note)
PARTS = []


def part(ref, value, sym, fp, lcsc, side, x, y, rot, pins, note=""):
    sl, sn = sym.split(":")
    fl, fn = fp.split(":")
    PARTS.append(dict(ref=ref, value=value, slib=sl, sym=sn, flib=fl, fp=fn, lcsc=lcsc,
                      side=side, x=x, y=y, rot=rot, pins=pins, note=note))


R0402 = "Resistor_SMD:R_0402_1005Metric"
C0402 = "Capacitor_SMD:C_0402_1005Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"

# ------------------------------------------------------------------ MCU
part("U1", "MDBT50Q-1MV2", "RF_Module:MDBT50Q-1MV2", "RF_Module:Raytac_MDBT50Q", "", "B", 15.2, 15.8, 0, {
    "GND": "GND", "VDD": "+3V3", "VDDH": "+3V3", "VBUS": "VBUS", "D-": "USB_DN", "D+": "USB_DP",
    "SWDIO": "SWDIO", "SWDCLK": "SWDCLK", "P0.18": "~RESET", "P1.00": "SWO",
    "P0.13": "DISP_SCLK_3V", "P0.15": "DISP_SI_3V", "P0.17": "DISP_SCS_3V",
    "P0.20": "DISP_EXTCOM_3V", "P0.22": "DISP_ON_3V", "P0.24": "DISP_PWR_EN",
    "P0.19": "FLASH_CLK", "P0.25": "FLASH_CS", "P0.21": "FLASH_IO0", "P0.23": "FLASH_IO1",
    "P1.02": "FLASH_IO2", "P1.04": "FLASH_IO3",
    "P0.06": "GNSS_RXD", "P0.08": "GNSS_TXD", "P0.07": "GNSS_PPS", "P0.05": "GNSS_EXTINT",
    "P0.04": "GNSS_RST",
    "P0.26": "I2C_SDA", "P0.27": "I2C_SCL", "P0.28": "IMU_INT1",
    "P0.02": "BTN_PAGE", "P0.03": "BTN_START", "P0.29": "BTN_POWER",
    "P0.31": "VBAT_SENSE",
    "P1.01": "I2S_BCLK", "P1.03": "I2S_LRCLK", "P1.05": "I2S_DIN", "P1.06": "AMP_EN",
}, "nRF52840 module, BLE 5 + ANT+. Not stocked at LCSC: JLC global sourcing or hand-place.")
part("C1", "10uF", "Device:C", C0603, "C19702", "B", 23.6, 23.0, 90, {"1": "+3V3", "2": "GND"})
part("C2", "100nF", "Device:C", C0402, "C1525", "B", 22.3, 23.0, 90, {"1": "+3V3", "2": "GND"})
part("C3", "4.7uF", "Device:C", C0402, "C23733", "B", 25.3, 23.0, 90, {"1": "VBUS", "2": "GND"})

# GPIO choice is optimised by assign_pins.py (shortest routes); pinmap.json overrides the defaults above
import json as _json
from pathlib import Path as _Path
_pm = _Path(__file__).with_name("pinmap.json")
if _pm.exists():
    _u1 = PARTS[0]["pins"]
    _fixed = {k: v for k, v in _u1.items() if not k.startswith("P") or k in ("P0.18", "P1.00")}
    PARTS[0]["pins"] = {**_fixed, **_json.loads(_pm.read_text())}

# ------------------------------------------------------------------ GNSS
part("U2", "MAX-M10S", "RF_GPS:MAX-M10S", "RF_GPS:ublox_MAX", "C4153167", "B", 28.2, 15.6, 0, {
    "GND": "GND", "TXD": "GNSS_TXD", "RXD": "GNSS_RXD", "TIMEPULSE": "GNSS_PPS",
    "EXTINT": "GNSS_EXTINT", "V_BCKP": "+3V3", "VCC_IO": "+3V3", "VCC": "+3V3",
    "~{RESET}": "GNSS_RST", "RF_IN": "RF_IN", "LNA_EN": None, "VCC_RF": None,
    "VIO_SEL": None, "SDA": None, "SCL": None, "~{SAFEBOOT}": None,
}, "u-blox M10, passive patch antenna on RF_IN")
part("C4", "10uF", "Device:C", C0603, "C19702", "B", 29.6, 23.2, 0, {"1": "+3V3", "2": "GND"})
part("C5", "100nF", "Device:C", C0402, "C1525", "B", 32.8, 23.2, 0, {"1": "+3V3", "2": "GND"})
part("AE1", "GNSS patch 15x15x4", "Device:Antenna", "OpenCycle:Patch_15x15_Feed", "", "F", 26.0, 11.3, 0,
     {"A": "RF_IN"}, "Passive ceramic patch, 1575 MHz. Hand-solder after assembly.")

# ------------------------------------------------------------------ flash
part("U3", "W25Q128JVSIQ", "Memory_Flash:W25Q128JVS", "Package_SO:SOIC-8_5.23x5.23mm_P1.27mm",
     "C97521", "B", 41.0, 14.2, 0, {
         "~{CS}": "FLASH_CS", "DO(IO1)": "FLASH_IO1", "IO2": "FLASH_IO2", "GND": "GND",
         "DI(IO0)": "FLASH_IO0", "CLK": "FLASH_CLK", "IO3": "FLASH_IO3", "VCC": "+3V3"},
     "16 MB QSPI NOR for rides, routes and map tiles")
part("C6", "100nF", "Device:C", C0402, "C1525", "B", 41.0, 19.0, 0, {"1": "+3V3", "2": "GND"})

# ------------------------------------------------------------------ USB-C
part("J1", "USB-C", "Connector:USB_C_Receptacle_USB2.0_16P",
     "Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12", "C165948", "B", 26.0, 79.4, 0, {
         "GND": "GND", "VBUS": "VBUS", "CC1": "CC1", "CC2": "CC2", "D+": "USB_DP_C",
         "D-": "USB_DN_C", "SBU1": None, "SBU2": None, "SHIELD": "GND"})
part("R1", "5.1k", "Device:R", R0402, "C25905", "B", 19.2, 77.0, 90, {"1": "CC1", "2": "GND"})
part("R2", "5.1k", "Device:R", R0402, "C25905", "B", 32.8, 77.0, 90, {"1": "CC2", "2": "GND"})
part("D1", "USBLC6-2SC6", "Power_Protection:USBLC6-2SC6", "Package_TO_SOT_SMD:SOT-23-6", "C7519",
     "F", 26.0, 79.4, 0, {"I/O1": "USB_DP_C", "GND": "GND", "I/O2": "USB_DN_C", "VBUS": "VBUS"},
     "USB ESD; nRF side of D+/D- taken from the same pads")

# ------------------------------------------------------------------ battery + charger
part("J2", "Battery", "Connector_Generic_MountingPin:Conn_01x02_MountingPin",
     "Connector_JST:JST_SH_SM02B-SRSS-TB_1x02-1MP_P1.00mm_Horizontal", "C160402", "B", 13.0, 79.6, 180,
     {"Pin_1": "VBAT", "Pin_2": "GND", "MountPin": "GND"},
     "Check the battery lead polarity before plugging in; JST-SH pinouts are not standardised.")
part("U4", "MCP73831-2", "Battery_Management:MCP73831-2-OT", "Package_TO_SOT_SMD:SOT-23-5", "C424093",
     "F", 13.0, 60.0, 0, {"STAT": "CHG_STAT", "V_{SS}": "GND", "V_{BAT}": "VBAT", "V_{DD}": "VBUS",
                          "PROG": "CHG_PROG"}, "500 mA Li-ion charger")
part("R3", "2k", "Device:R", R0402, "C4109", "F", 13.0, 62.8, 0, {"1": "CHG_PROG", "2": "GND"})
part("C7", "4.7uF", "Device:C", C0402, "C23733", "F", 9.6, 60.0, 90, {"1": "VBUS", "2": "GND"})
part("C8", "4.7uF", "Device:C", C0402, "C23733", "F", 16.4, 60.0, 90, {"1": "VBAT", "2": "GND"})
part("D2", "Green", "Device:LED", "LED_SMD:LED_0603_1608Metric", "C72043", "F", 10.0, 55.6, 0,
     {"K": "CHG_STAT", "A": "LED_A"}, "Charge indicator")
part("R4", "1k", "Device:R", R0402, "C11702", "F", 10.0, 53.6, 0, {"1": "VBUS", "2": "LED_A"})

# ------------------------------------------------------------------ 3.3 V LDO
part("U5", "XC6220B331MR", "Regulator_Linear:XC6220B331MR", "Package_TO_SOT_SMD:SOT-23-5", "C86534",
     "F", 22.6, 60.0, 0, {"VIN": "VBAT", "GND": "GND", "CE": "VBAT", "NC": None, "VOUT": "+3V3"},
     "700 mA LDO, 8 uA Iq")
part("C9", "1uF", "Device:C", C0402, "C52923", "F", 19.0, 60.0, 90, {"1": "VBAT", "2": "GND"})
part("C10", "10uF", "Device:C", C0603, "C19702", "F", 26.3, 60.0, 90, {"1": "+3V3", "2": "GND"})

# ------------------------------------------------------------------ 5 V for display
part("U6", "TPS61220DCK", "Regulator_Switching:TPS61220DCK", "Package_TO_SOT_SMD:SOT-363_SC-70-6",
     "C15421", "F", 32.0, 60.0, 0, {"VIN": "+3V3", "FB": "BOOST_FB", "GND": "GND", "VOUT": "+5V_DISP",
                                    "L": "BOOST_SW", "EN": "DISP_PWR_EN"}, "Boost to 5.05 V for the memory LCD")
part("L1", "4.7uH", "Device:L", "Inductor_SMD:L_Sunlord_SWPA3012S", "C83415", "F", 37.2, 60.0, 90,
     {"1": "+3V3", "2": "BOOST_SW"}, "SWPA3012S4R7MT, 3 x 3 x 1.2 mm")
part("C11", "10uF", "Device:C", C0603, "C19702", "F", 32.0, 63.2, 0, {"1": "+5V_DISP", "2": "GND"})
part("C12", "4.7uF", "Device:C", C0402, "C23733", "F", 28.6, 60.0, 90, {"1": "+3V3", "2": "GND"})
part("R5", "1M", "Device:R", R0402, "C26083", "F", 31.0, 56.8, 0, {"1": "+5V_DISP", "2": "BOOST_FB"})
part("R6", "110k", "Device:R", R0402, "", "F", 33.6, 56.8, 0, {"1": "BOOST_FB", "2": "GND"},
     "Vout = 0.5 V x (1 + R5/R6) = 5.05 V")
part("R7", "1M", "Device:R", R0402, "C26083", "F", 28.4, 56.8, 0, {"1": "DISP_PWR_EN", "2": "GND"},
     "Keeps boost off while the MCU boots")

# ------------------------------------------------------------------ level shifters 3.3 -> 5 V
shift = [("U7", "DISP_SCLK"), ("U8", "DISP_SI"), ("U9", "DISP_SCS"), ("U10", "DISP_EXTCOM"),
         ("U11", "DISP_ON")]
for i, (ref, sig) in enumerate(shift):
    x = 16.0 + i * 5.0
    part(ref, "SN74LV1T34DCK", "Logic_LevelTranslator:SN74LV1T34DCK",
         "Package_TO_SOT_SMD:SOT-353_SC-70-5", "C78541", "F", x, 66.6, 0,
         {"NC": None, "A": sig + "_3V", "GND": "GND", "Y": sig, "VCC": "+5V_DISP"},
         "3.3 V to 5 V buffer for the memory LCD inputs")
    part(f"C{13 + i}", "100nF", "Device:C", C0402, "C1525", "F", x + 2.4, 66.6, 90,
         {"1": "+5V_DISP", "2": "GND"})

# ------------------------------------------------------------------ display connector
part("J3", "LS027B7DH01", "Connector_Generic_MountingPin:Conn_01x10_MountingPin",
     "Connector_FFC-FPC:Hirose_FH12-10S-0.5SH_1x10-1MP_P0.50mm_Horizontal", "C506791", "F", 26.0, 71.6, 0, {
         "Pin_1": "DISP_SCLK", "Pin_2": "DISP_SI", "Pin_3": "DISP_SCS", "Pin_4": "DISP_EXTCOM",
         "Pin_5": "DISP_ON", "Pin_6": "+5V_DISP", "Pin_7": "+5V_DISP", "Pin_8": "+5V_DISP",
         "Pin_9": "GND", "Pin_10": "GND", "MountPin": "GND"},
     "Sharp 2.7 in memory LCD. Pin 8 EXTMODE high = EXTCOMIN pin drives COM inversion.")
part("C18", "1uF", "Device:C", C0402, "C52923", "F", 32.6, 70.4, 90, {"1": "+5V_DISP", "2": "GND"})

# ------------------------------------------------------------------ sensors
part("U12", "BMP280", "Sensor_Pressure:BMP280",
     "Package_LGA:Bosch_LGA-8_2x2.5mm_P0.65mm_ClockwisePinNumbering", "C83291", "F", 20.0, 40.0, 0, {
         "GND": "GND", "CSB": "+3V3", "SDI": "I2C_SDA", "SCK": "I2C_SCL", "SDO": "GND",
         "VDDIO": "+3V3", "VDD": "+3V3"}, "Barometric altitude, I2C 0x76. Needs a vent in the case.")
part("C19", "100nF", "Device:C", C0402, "C1525", "F", 20.0, 43.0, 0, {"1": "+3V3", "2": "GND"})
part("U13", "LIS3DH", "Sensor_Motion:LIS3DH", "Package_LGA:LGA-16_3x3mm_P0.5mm", "C15134", "F", 28.0, 40.0, 0, {
    "VDD_IO": "+3V3", "NC": None, "SCL/SPC": "I2C_SCL", "GND": "GND", "SDA/SDI/SDO": "I2C_SDA",
    "SDO/SA0": "+3V3", "CS": "+3V3", "INT2": None, "INT1": "IMU_INT1", "ADC3": None, "VDD": "+3V3",
    "ADC2": None, "ADC1": None}, "Accelerometer for wake-on-motion, I2C 0x19")
part("C20", "100nF", "Device:C", C0402, "C1525", "F", 28.0, 43.4, 0, {"1": "+3V3", "2": "GND"})
part("R8", "4.7k", "Device:R", R0402, "C25900", "F", 24.0, 36.0, 0, {"1": "+3V3", "2": "I2C_SDA"})
part("R9", "4.7k", "Device:R", R0402, "C25900", "F", 24.0, 37.4, 0, {"1": "+3V3", "2": "I2C_SCL"})

# ------------------------------------------------------------------ battery sense
part("R10", "1M", "Device:R", R0402, "C26083", "F", 14.0, 48.0, 90, {"1": "VBAT", "2": "VBAT_SENSE"})
part("R11", "1M", "Device:R", R0402, "C26083", "F", 15.4, 48.0, 90, {"1": "VBAT_SENSE", "2": "GND"})
part("C21", "100nF", "Device:C", C0402, "C1525", "F", 16.8, 48.0, 90, {"1": "VBAT_SENSE", "2": "GND"})

# ------------------------------------------------------------------ buttons (side-actuated)
part("SW1", "Page/lap", "Switch:SW_Push", "Button_Switch_SMD:SW_Push_1P1T-MP_NO_Horizontal_Alps_SKRTLAE010",
     "C110293", "B", 46.8, 34.0, 90, {"1": "BTN_PAGE", "2": "GND"}, "Right side, upper")
part("SW2", "Start/stop", "Switch:SW_Push", "Button_Switch_SMD:SW_Push_1P1T-MP_NO_Horizontal_Alps_SKRTLAE010",
     "C110293", "B", 46.8, 50.0, 90, {"1": "BTN_START", "2": "GND"}, "Right side, lower")
part("SW3", "Power", "Switch:SW_Push", "Button_Switch_SMD:SW_Push_1P1T-MP_NO_Horizontal_Alps_SKRTLAE010",
     "C110293", "B", 5.2, 34.0, -90, {"1": "BTN_POWER", "2": "GND"}, "Left side")

# ------------------------------------------------------------------ audio
part("U14", "MAX98357A", "Audio:MAX98357A", "Package_DFN_QFN:TQFN-16-1EP_3x3mm_P0.5mm_EP1.23x1.23mm",
     "C910544", "F", 44.0, 61.0, 0, {
         "DIN": "I2S_DIN", "OUTN": "SPK-", "GND": "GND", "NC": None, "LRCLK": "I2S_LRCLK",
         "BCLK": "I2S_BCLK", "PAD": "GND", "GAIN_SLOT": "GND", "~{SD_MODE}": "AMP_EN",
         "VDD": "VBAT", "OUTP": "SPK+"},
     "I2S class-D amp, 12 dB gain (GAIN to GND), left channel when AMP_EN is high")
part("C22", "10uF", "Device:C", C0603, "C19702", "F", 44.0, 57.2, 0, {"1": "VBAT", "2": "GND"})
part("C23", "100nF", "Device:C", C0402, "C1525", "F", 41.2, 59.2, 90, {"1": "VBAT", "2": "GND"})
part("R12", "100k", "Device:R", R0402, "C25741", "F", 41.2, 63.0, 90, {"1": "AMP_EN", "2": "GND"},
     "Amp stays off until firmware enables it")
part("LS1", "8R 1W 11x15", "Device:Speaker", "OpenCycle:SpeakerPads_2.6mm", "", "B", 44.2, 72.2, 0,
     {"1": "SPK+", "2": "SPK-"},
     "Micro speaker, 11 x 15 x 3.5 mm, 8 ohm 1 W (e.g. Ole Wolff OWS-111535W50A-8). Leads soldered to pads; "
     "sits beside the battery, fires through a grille in the back shell.")

# ------------------------------------------------------------------ programming
part("J4", "SWD", "Connector:Conn_ARM_SWD_TagConnect_TC2030-NL",
     "Connector:Tag-Connect_TC2030-IDC-NL_2x03_P1.27mm_Vertical", "", "F", 11.0, 27.0, 0, {
         "VCC": "+3V3", "SWDIO": "SWDIO", "~{RESET}": "~RESET", "SWCLK": "SWDCLK", "GND": "GND",
         "SWO": "SWO"}, "Tag-Connect pads only, nothing to assemble")

# ------------------------------------------------------------------ mounting holes (M2, plated, GND)
HOLES = [(6.5, 6.5), (45.5, 6.5), (6.5, 79.5), (45.5, 79.5)]

BOARD = dict(x0=3.0, y0=3.0, w=46.0, h=80.0, r=4.0, thickness=1.0)

# nets that get fat tracks
POWER_NETS = {"VBAT": 0.4, "VBUS": 0.4, "+5V_DISP": 0.3, "BOOST_SW": 0.4, "RF_IN": 0.3, "SPK+": 0.25, "SPK-": 0.25}
PLANE_NETS = {"GND": "In1.Cu", "+3V3": "In2.Cu"}

# Back-side area occupied by the LiPo (component keep-out), in board coords
BATTERY_KEEPOUT = (8.0, 25.7, 38.0, 73.7)   # 30 x 48 x 8 mm pouch (803048)
SPEAKER_KEEPOUT = (38.6, 55.0, 49.3, 70.8)  # 11 x 15 x 3.5 mm speaker, back side
