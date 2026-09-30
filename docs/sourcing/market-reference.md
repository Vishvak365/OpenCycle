# Market reference

Prices as seen 2026-09-29.

## Commercial bike computers

| Device | Price seen | Screen | Notes |
|---|---|---|---|
| [GEOID CC700 Pro](https://bicyclingaustralia.com.au/?p=42178) | $69–85 AliExpress sale ([Slickdeals $68.90](https://slickdeals.net/f/20018094-geoid-cc700-pro-bike-computer-gps-2-8-touchscreen-navigation-69-free-shipping-68-9)); ~$99 list | 2.8" colour touch, 240 × 320 | Dual-band GNSS, offline maps, Wi-Fi/BLE/ANT+, IPX7, 8 GB, DJI camera control ([specs](https://e-katalog.kz/GEOID-CC700-PRO.htm)). Weak: resolution, contrast, no live tracking. |
| GEOID CC700 (non-Pro) | ~$52–60 | 2.8" colour, buttons | |
| [iGPSPORT iGS630S](https://force.dev.programia.eu/EN/bike-computer-igpsport-igs630s) | ~$160–200 | 2.8" colour 240 × 400, buttons | Dual-band, 45 h battery. [iGS630 review](https://thesweetcyclists.com/igpsport-igs630-gps-bike-computer-review/) (35 h, $219 list). |
| [Magene C606 / V2](https://the5krunner.com/2024/03/14/magene-c606-review/) | ~$160 | 2.8" colour touch | Climb tracker, radar, workouts; app rough. [C606 V2 features](https://bike-addict.co.za/products/magene-c606-v2-smart-gps-bike-computer). |
| Coospo BC107 / CS300 | < £100 ([road.cc](https://road.cc/buyers-guide/best-cheap-cycling-computers)) | mono / 2.4" colour | Budget. |
| Garmin Edge 540 / 1050 | ~$300 / $700 | 2.6" / 3.5" colour | Reference for features and battery (~26 h on the 540). |

Takeaway: a DIY build doesn't beat these on price. At one unit, a CC700-class device costs ~$95–165 in parts plus ~$100–300 in prototype overhead. The case for OpenCycle is open firmware, repairability, battery life (mono), and learning.

## Open-source projects

| Project | Hardware | Notes |
|---|---|---|
| [OpenTrailPaper](https://www.cnx-software.com/2026/09/05/opentrailpaper-transforms-lilygo-t5-e-paper-s3-pro-devkit-into-a-diy-e-paper-bike-computer/) | LILYGO T5 E-Paper S3 Pro (ESP32-S3, 4.7" e-paper, M10/L76K GNSS) | Offline maps, GPX, FIT, BLE sensors, phone apps; < 8 h battery; 129 × 69 × 11 dev kit. |
| [bike-computer-32](https://github.com/lspr98/bike-computer-32) | ESP32-C3 | OSM offline maps, GPX rendering. |
| [Yōkai](https://github.com/mrmattuschka/yokai) | ESP32 + e-paper | Komoot BLE navigation display, no GPS. |
| [ESP32 GPS bike computer (Printables)](https://www.printables.com/model/147944-gps-bicycle-computer-w-esp32-speedometer-sd-loggin) | ESP32, 128 × 64 LCD | SD logging, Qi charging. |
| [HITSZ Bike-Computer](https://github.com/MaxwellJay256/Bike-Computer) | ESP32, ESP-IDF | Student project. |
| [pizero_bikecomputer](https://github.com/hishizuka/pizero_bikecomputer) | Raspberry Pi Zero + JDI colour MIP | Mature software; reference for the MIP panel. |
