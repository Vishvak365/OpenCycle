"""Where every part on the v0.2 board comes from. Single source for the BOM files and docs/sourcing/.

checked: date the price/stock was read from the distributor (qty-1 USD). "typical" = commodity part,
price not re-checked (always stocked in the millions); verify in the cart.
Two vendors cover everything: Mouser (most parts) and Digi-Key (BMP581, patch antenna, P-FET).
"""

MOUSER = "https://www.mouser.com/c/?q={}"
DIGIKEY = "https://www.digikey.com/en/products/result?keywords={}"

S = {
    # mpn: (vendor, vendor part number, price, stock_seen, checked, datasheet, description)
    "ESP32-S3-WROOM-1-N16R8": ("Mouser", "356-ESP32S3WRM1N16R8", 6.72, 47727, "2026-09-30",
                               "https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf",
                               "ESP32-S3 module, 16 MB flash, 8 MB octal PSRAM, PCB antenna"),
    "BL652-SA-01-T/R": ("Mouser", "239-BL652-SA-01-T/R", 10.40, 5583, "2026-09-30",
                        "https://www.ezurio.com/wireless-modules/bluetooth-modules/bluetooth-5-modules/bl652-series-bluetooth-v5-nfc-module",
                        "Ezurio (Laird) BL652, nRF52832 module, integrated antenna"),
    "MAX-M10S-00B": ("Mouser", "377-MAX-M10S-00B", 9.12, 2746, "2026-09-30",
                     "https://content.u-blox.com/sites/default/files/MAX-M10S_DataSheet_UBX-20035208.pdf",
                     "u-blox M10 GNSS module, LCC-18"),
    "DSGP.1575.12.4.A.02": ("Digi-Key", "DSGP.1575.12.4.A.02", 4.25, 1474, "2026-09-30",
                            "https://www.taoglas.com/datasheets/DSGP.1575.12.4.A.02.pdf",
                            "Taoglas 12 x 12 x 4 mm GPS L1 / Galileo E1 ceramic patch, SMT"),
    "NHD-2.4-240320AF-CSXP": ("Mouser", "763-24240320AFCSXP", 15.86, 1032, "2026-09-30",
                              "https://newhavendisplay.com/content/specs/NHD-2.4-240320AF-CSXP.pdf",
                              "Newhaven 2.4 in IPS TFT 240 x 320, ST7789, 1200 nit, 40-pin FFC"),
    "FH12-40S-0.5SH(55)": ("Mouser", "798-FH12-40S-0.5SH55", 2.50, 25967, "2026-09-30",
                           "https://www.hirose.com/product/series/FH12", "Hirose 40-pin 0.5 mm bottom-contact FFC connector"),
    "DMG2302UK-7": ("Mouser", "621-DMG2302UK-7", 0.39, 238766, "2026-09-30",
                    "https://www.diodes.com/assets/Datasheets/DMG2302UK.pdf", "N-MOSFET 20 V SOT-23 (backlight PWM)"),
    "LTR-303ALS-01": ("Mouser", "859-LTR-303ALS-01", 0.68, 29622, "2026-09-30",
                      "https://optoelectronics.liteon.com/upload/download/DS86-2013-0004/LTR-303ALS-01_DS_V1.pdf",
                      "Lite-On ambient light sensor, I2C"),
    "BMP581": ("Digi-Key", "828-BMP581CT-ND", 3.07, 462, "2026-09-30",
               "https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp581-ds004.pdf",
               "Bosch barometric pressure sensor, LGA-10 2 x 2 mm"),
    "MAX98357AETE+T": ("Mouser", "700-MAX98357AETE+T", 4.08, 10971, "2026-09-30",
                       "https://www.analog.com/media/en/technical-documentation/data-sheets/MAX98357A-MAX98357B.pdf",
                       "I2S class-D amplifier, TQFN-16"),
    "CMS-151125-078L100": ("Mouser", "490-CMS151125078L100", 2.96, 597, "2026-09-30",
                           "https://www.mouser.com/datasheet/3/6118/1/cms-151125-078x-67.pdf",
                           "Same Sky 15 x 11 x 2.5 mm speaker, 8 ohm 0.7 W, IP67, wire leads"),
    "MCP73831T-2ACI/OT": ("Mouser", "579-MCP73831T-2ACIOT", 0.76, 116042, "2026-09-30",
                          "https://ww1.microchip.com/downloads/en/DeviceDoc/MCP73831-Family-Data-Sheet-DS20001984H.pdf",
                          "Li-ion charger 4.20 V, SOT-23-5"),
    "AP7361C-33E-13": ("Mouser", "621-AP7361C-33E-13", 0.52, 733, "2026-09-30",
                       "https://www.diodes.com/assets/Datasheets/AP7361C.pdf", "3.3 V 1 A LDO, SOT-223"),
    "USB4105-GF-A": ("Mouser", "640-USB4105-GF-A", 0.80, 420427, "2026-09-30",
                     "https://gct.co/files/drawings/usb4105.pdf", "GCT USB-C receptacle, USB 2.0, top mount"),
    "USBLC6-2SC6": ("Mouser", "511-USBLC6-2SC6", 0.49, 81014, "2026-09-30",
                    "https://www.st.com/resource/en/datasheet/usblc6-2.pdf", "USB ESD protection, SOT-23-6"),
    "SKRTLAE010": ("Mouser", "688-SKRTLA", 0.34, 2396, "2026-09-30",
                   "https://tech.alpsalpine.com/e/products/detail/SKRTLAE010/", "Alps side-actuated tact switch"),
    "PTS810 SJM 250 SMTR LFS": ("Mouser", "611-PTS810SJM250SMTR", 0.52, 30244, "2026-09-30",
                                "https://www.ckswitches.com/media/1476/pts810.pdf", "C&K top-actuated tact switch 4.2 x 3.2 x 2.5 mm"),
    "S2B-PH-SM4-TB(LF)(SN)": ("Mouser", "306-S2BPHSM4TBLFSN", 0.49, 269, "2026-09-30",
                              "https://www.jst-mfg.com/product/pdf/eng/ePH.pdf", "JST PH 2-pin side-entry SMT header"),
    "LTST-C191KGKT": ("Mouser", "859-LTST-C191KGKT", 0.15, 1190000, "2026-09-30",
                      "https://optoelectronics.liteon.com/upload/download/DS22-2000-229/LTST-C191KGKT.pdf", "Green LED 0603"),
    "DMG2305UX-7": ("Digi-Key", "DMG2305UX-7DICT-ND", 0.30, 75458, "2026-09-30",
                    "https://www.diodes.com/assets/Datasheets/DMG2305UX.pdf", "P-MOSFET 20 V 4.2 A SOT-23 (reverse battery)"),
    # commodity passives (Mouser; always stocked)
    "CL05B104KO5NNNC": ("Mouser", "187-CL05B104KO5NNNC", 0.10, None, "typical", "", "100 nF 16 V X7R 0402"),
    "CL05A105KO5NNNC": ("Mouser", "187-CL05A105KO5NNNC", 0.10, None, "typical", "", "1 uF 16 V X5R 0402"),
    "CL10A475KO8NNNC": ("Mouser", "187-CL10A475KO8NNNC", 0.10, None, "typical", "", "4.7 uF 16 V X5R 0603"),
    "CL10A106KP8NNNC": ("Mouser", "187-CL10A106KP8NNNC", 0.12, None, "typical", "", "10 uF 10 V X5R 0603"),
    "CL21A226MAQNNNE": ("Mouser", "187-CL21A226MAQNNNE", 0.22, None, "typical", "", "22 uF 25 V X5R 0805"),
}
import design as _D  # noqa: E402

for _v, _mpn in _D.RES.items():
    _size = "0603" if _v == "33R" else "0402"
    S[_mpn] = ("Mouser", f"603-{_mpn}", 0.10, None, "typical", "", f"Yageo resistor {_v} {_size}")

# things that are not on the board
EXTRA = [
    # (item, qty, vendor, vendor pn / link, unit price, note)
    ("Adafruit 258 LiPo 1200 mAh 34 x 62 x 5 mm, protected, JST-PH", 1, "Mouser", "485-258", 9.95, "checked 2026-09-30, 388 in stock"),
    ("M2 x 5 mm pan-head screws (stainless)", 4, "any", "e.g. McMaster 92000A017", 0.10, "PCB to back shell"),
    ("M2 x 6 mm pan-head screws (stainless)", 4, "any", "", 0.10, "front bezel to back shell (through the corner posts)"),
    ("1.0 mm clear acrylic or polycarbonate cover lens, 48.0 x 75.9 mm, 5 mm corner radius", 1,
     "SendCutSend / Ponoko", "cad/out/stl/cover_lens.step", 3.00, "black mask: vinyl or paint on the inside, window per cad/out/stl/lens_mask.stl"),
    ("Closed-cell foam tape 0.5 mm, 2 mm strips", 1, "any", "", 1.00, "display gasket"),
    ("Nitrile O-ring cord 1.2 mm", 1, "any", "", 1.00, "case seal, ~280 mm length, ends glued"),
    ("Breathable PTFE vent sticker, 3-5 mm", 1, "any", "e.g. Amazon 'ePTFE vent patch'", 0.50, "over the 0.8 mm barometer vent"),
    ("Acoustic mesh / speaker membrane 12 x 9 mm", 1, "any", "", 0.50, "under the speaker grille"),
    ("PLA / PETG / TPU filament", 1, "any", "", 2.00, "~35 g for a standard case"),
]


def lookup(mpn):
    return S.get(mpn)


def link(mpn):
    s = S.get(mpn)
    if not s:
        return ""
    vendor, pn = s[0], s[1]
    return (MOUSER if vendor == "Mouser" else DIGIKEY).format(pn.replace(" ", "%20").replace("#", "%23"))
