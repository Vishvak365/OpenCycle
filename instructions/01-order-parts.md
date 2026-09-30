# 1 · Order the parts

The full list with prices, stock and links: [`docs/sourcing/bom-v0.2.md`](../docs/sourcing/bom-v0.2.md). The same list as a spreadsheet with quantities for **5 boards** (plus spares for tiny passives): [`pcb/fab/bom_distributors.csv`](../pcb/fab/bom_distributors.csv).

## Electronics — two carts

1. **Mouser** (almost everything, ~$73 per unit): open the CSV, filter `Vendor = Mouser`, and paste *Vendor part number* + *Qty to order* into Mouser's **BOM Tool** (or Quick Order). This includes the display (NHD-2.4-240320AF-CSXP) and the Adafruit 258 battery.
2. **Digi-Key** (~$8 per unit): BMP581 barometer, Taoglas DSGP.1575.12.4.A.02 patch antenna, DMG2305UX-7 P-FET.

Order the thin-stock parts first and buy spares: BMP581 (hard to hand-solder — get 2 extra), MAX98357A (Mouser is phasing it out), AP7361C-33E-13, the JST PH socket, the speaker.

**Don't substitute:** `AP7361C-33E-13` (SOT-223, pin 1 = IN). The similar `AP7361C-33ER-13` has a different pin order and would be wired wrong.

## Mechanical bits

| Item | Where | Notes |
|---|---|---|
| Cover lens, 1.0 mm clear acrylic/PC, 48.0 × 75.9 mm, 5 mm corners | SendCutSend / Ponoko (upload `print/cover_lens_outline.dxf`) | Or cut from a 1 mm sheet with a knife and file. |
| Black vinyl or paint for the lens mask | any | Mask template: `print/step/lens_mask.step` (screen window + two small windows top-right). |
| M2 × 5 mm + M2 × 6 mm pan-head screws | any | 4 of each. |
| 1.2 mm nitrile O-ring cord (~280 mm) | any | Case seal. |
| 0.5 mm closed-cell foam tape | any | 2 mm strips around the display. |
| ePTFE vent sticker (3–5 mm) | any | Over the barometer vent hole. |
| Acoustic mesh 12 × 9 mm | any | Under the speaker grille. |

## Tools (one-time)

- Soldering iron with a fine tip, flux, 0.3 mm solder, tweezers, magnifier or microscope.
- **Hot plate or hot-air station** + the JLC stencil (step 2): needed for the BMP581 (LGA-10), MAX98357A (QFN), ESP32 module ground pad.
- Solder paste: SAC305 for the back side, **low-temperature (Sn42Bi58, 138 °C)** for the front side (see step 4).
- Multimeter; a current-limited bench supply (or a USB-C power meter).
- **Tag-Connect TC2030-IDC-NL** cable + a SWD probe (J-Link EDU Mini, or an nRF52 DK) to program the BL652. The ESP32 flashes over USB-C.
- USB-C data cable.
