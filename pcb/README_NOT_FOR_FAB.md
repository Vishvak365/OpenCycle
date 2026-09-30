# OpenCycle main board — CONCEPT ONLY, DO NOT ORDER

**Status (2026-09-29): presentable concept board. It is not electrically complete and must not be sent to JLCPCB.**

## What is real
- Board outline, 4-layer stackup (F / GND / 3V3 / B), 1.0 mm, M2 holes: match the enclosure CAD.
- Placement of all 65 parts is deliberate and passes courtyard / battery / speaker / standoff checks (`check_place.py`).
- Nets are defined from datasheet reference circuits in `design.py`; MCU pins picked by geometry (`assign_pins.py`).
- Routing by `router.py` (custom grid router) + GND/3V3 plane pours (`finish.py`).

## What is NOT done (come back to this)
1. **12 connections unrouted** (see `routed.unrouted.json`): SPK+/SPK-, several display lines, I2C_SCL, BOOST_FB, USB_DP_C, GNSS_RST/TXD, SWDCLK.
2. **DRC not clean**: ~295 violations in `final.drc.txt`. Known causes: netclass clearance applied as 0.2 (not the intended 0.15), fan-out tracks too close to neighbouring pads, duplicate vias from older runs, switch footprint NPTH pegs near pads, silkscreen overlaps.
3. **No schematic yet** (.kicad_sch / PDF), so nothing has been reviewed by a human.
4. **Parts swaps agreed but not applied** (Digi-Key/Mouser sourcing):
   - Barometer BMP280 -> ST LPS22HH
   - USB-C HRO TYPE-C-31-M-12 -> GCT USB4105-GF-A
   - Inductor Sunlord SWPA3012 -> Taiyo Yuden NR3015 4.7 uH
   - GPS patch: pin-fed placeholder -> Taoglas DSGP.1575.15.4.A.02 (SMT feed)
   - Module: keep Raytac MDBT50Q (buy from SparkFun) or change to u-blox NINA-B306 (needs a new footprint)
   - Battery: Jauch LP603048 (6 mm) or LP103048 (10 mm, thicker case) — undecided
5. **Open design questions**: Sharp LCD 5 V logic thresholds (level shifters kept to be safe), JST-SH battery polarity, GNSS V_BCKP from 3V3, baro vent in case, RF keep-outs around nRF antenna and patch reviewed by eye only, 50-ohm RF_IN trace not impedance-controlled.

## Before any order
Apply swaps -> re-place -> route to 100% -> DRC 0 errors -> generate schematic -> human review (power, RF, pinout) -> Gerbers/BOM/CPL.
