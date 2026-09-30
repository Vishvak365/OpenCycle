# Mono build (v0.1) — Sharp memory LCD

The first design, as implemented in `pcb/design.py`. Kept for reference; the current direction is the [colour build](bom-colour-v0.2.md).

## LCSC / JLCPCB numbers (first pass, for JLC assembly)

| Ref | Part | LCSC | Notes |
|---|---|---|---|
| U1 | Raytac MDBT50Q-1MV2 | — | Not stocked by LCSC; JLC global sourcing or hand-place |
| U2 | u-blox MAX-M10S-00B | C4153167 | Verified |
| U3 | Winbond W25Q128JVSIQ | C97521 | |
| J1 | HRO TYPE-C-31-M-12 | C165948 | |
| D1 | USBLC6-2SC6 | C7519 | |
| J2 | JST SM02B-SRSS-TB | C160402 | |
| U4 | MCP73831T-2ACI/OT | C424093 | Verified |
| U5 | XC6220B331MR-G | C86534 | Verified |
| U6 | TPS61220DCKR | C15421 | TPS61222 not found at LCSC |
| L1 | Sunlord SWPA3012S4R7MT | C83415 | |
| U7–U11 | SN74LV1T34DCKR | C78541 | Verified |
| J3 | Hirose FH12-10S-0.5SH(55) | C506791 | Verified |
| U12 | Bosch BMP280 | C83291 | |
| U13 | ST LIS3DH | C15134 | |
| U14 | MAX98357AETE+T | C910544 | Verified |
| SW1–3 | Alps SKRTLAE010 | C110293 | Verified |
| AE1 | 15 mm patch | — | Hand-solder |
| LS1 | 11 × 15 speaker | — | Ole Wolff OWS-111535TA-8A at LCSC C5705967 (~$1.44) |
| D2 | Green 0603 LED | C72043 | |
| Passives | 100 nF C1525 · 1 µF C52923 · 4.7 µF C23733 · 10 µF 0603 C19702 · 10 k C25744 · 5.1 k C25905 · 4.7 k C25900 · 2 k C4109 · 1 k C11702 · 1 M C26083 · 100 k C25741 | | 110 k: match by value |

## Digi-Key / Mouser pass (qty 1)

| Part | Where | Price | Stock |
|---|---|---|---|
| MAX-M10S-00B | Mouser 377-MAX-M10S-00B / DK 672-MAX-M10S-00B-CT-ND | $9.12 / $11.42 | 16,866 / 4,987 |
| Taoglas DSGP.1575.15.4.A.02 | DK 931-DSGP.1575.15.4.A.02TR-ND | $5.43 | 427 |
| W25Q128JVSIQ | DK 256-W25Q128JVSIQTR-ND / Mouser 454-W25Q128JVSIQTR | $2.88 / $3.94 | 85,500 / 5,302 |
| GCT USB4105-GF-A | DK 2073-USB4105-GF-ADKR-ND | $0.80 | 121,048 |
| MAX98357AETE+T | DK MAX98357AETE+TCT-ND | $3.73 | 30,936 |
| Hirose FH12-10S-0.5SH(55) | DK/Mouser 798-FH12-10S-0.5SH55 | $1.75 | 6,378 |
| Alps SKRTLAE010 | Digi-Key | ~$0.34 | 432 |
| LIS3DHTR | Mouser 511-LIS3DHTR | $1.94 | 150 (DK 0) |
| Sharp LS027B7DH01 | DK 425-2907-ND | $32.24 | 0, 28-week lead |
| Raytac MDBT50Q-1MV2 | SparkFun WRL-21605 | $8.95 | in stock |
| u-blox NINA-B306-00B (alt. module) | DK ~$8.11–9.93 / Mouser $8.12–8.65 | | DK 203 |

Estimated parts cost: **$85–95 per unit** at qty 1, excluding PCB and case.

## Swaps agreed for v0.1 (not applied to the board)
BMP280 → LPS22HH · HRO USB-C → GCT USB4105 · Sunlord inductor → Taiyo Yuden NR3015 4.7 µH · pin-fed patch → Taoglas DSGP (SMT). LPS22HH later turned out to be out of stock everywhere mainstream; see [stock-issues-and-alternatives.md](stock-issues-and-alternatives.md).
