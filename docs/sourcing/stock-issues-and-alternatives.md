# Stock issues and alternatives

What didn't work out during sourcing, and what replaced it. Stock status as of 2026-09-29/30.

| Wanted | Problem | Replacement | Notes |
|---|---|---|---|
| Raytac MDBT50Q-1MV2 (nRF52840) | Not at Digi-Key/Mouser | SparkFun WRL-21605 ($8.95) for v0.1; v0.2 moves to ESP32-S3 + BL652 | u-blox NINA-B306 is stocked at DK/Mouser but has no KiCad footprint |
| Sharp LS027B7DH01 | Digi-Key 0 stock, 28-week lead; Adafruit breakout out of stock | Colour TFT for v0.2 | Tindie / AliExpress remain for the mono build |
| JDI LPM027M128C | Switch Science discontinued; AliExpress only | Not used | Best power profile of any colour option |
| Bosch BMP280 (bare) | Digi-Key 0, 10k MOQ | → LPS22HH (v0.1 plan) → BMP581 (v0.2) | |
| ST LPS22HHTR | Mouser/Digi-Key/Newark 0; Future Electronics 6,795 | BMP581 | |
| ST LPS22DFTR | Mouser 0 until Apr 2027 | BMP581 | |
| Infineon DPS368 / DPS310 | Mouser 0 (DPS368 495 due Oct 2026); DPS310 0 at DK | BMP581 | |
| Bosch BMP390 | Mouser 16-week lead | BMP581 | |
| Bosch BMP581 | Mouser 0 (159,933 on order) | **Digi-Key 828-BMP581CT-ND, 462 in stock** | Second vendor needed for this one part |
| ST LIS3DHTR | Mouser 0 (123,866 on order, 24-week lead); Digi-Key 0 | BMA400 (Mouser, 104k) — then dropped for v0.2 | |
| ST LIS2DH12TR | Mouser 0 until Apr 2027 | — | |
| Bosch BMA400 | In stock, but the pin table couldn't be read from the datasheet text | Dropped for v0.2 | Power button handles wake |
| TI TLV75733PDBVR | Mouser 0 until Dec 2026 | Diodes AP7361C-33ER-13 (1 A, SOT-223) | |
| JST SM02B-SRSS-TB | Mouser 0 until Dec 2026 | JST S2B-PH-SM4-TB (matches the Adafruit battery's JST-PH) | |
| Taoglas DSGP patch | Mouser 331 only | Abracon APAE1575R1540AZDB2F-T (pin-fed, $2.11, 1,218) as backup | Abracon datasheet lacks pin position |
| HRO TYPE-C-31-M-12 | Not at US distributors | GCT USB4105-GF-A | |
| Sunlord SWPA3012 inductor | Not at US distributors | Taiyo Yuden NR3015 (v0.1); not needed in v0.2 | |
| MAX98357AETE+T | Mouser says it will stop carrying it | Still in stock at Mouser (10,971) and Digi-Key (30,936) | Buy spares |
| Same Sky speaker variants | -078L100-67 is SMT, non-stocked, 500 MOQ | -078L100 (wires) or -078SP-67 (pads) | |
| Freerouting (autorouter) | Maven/GitHub release downloads blocked in the build environment | Custom router in `pcb/router.py` | Environment issue, not a sourcing one |
