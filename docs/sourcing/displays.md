# Display options

## Comparison

| Option | Colour | Direct sun | Night | Screen power | Refresh | Price | Board impact |
|---|---|---|---|---|---|---|---|
| Sharp LS027B7DH01A memory LCD (2.7", 400×240) | 1-bit | Excellent | Needs front light | ~0.05–0.2 mW | Fast | $15–35 | 5 V: boost + 5 level shifters |
| JDI LPM027M128C colour MIP (2.7", 400×240) | 8 colours | Excellent | Front-light versions exist | ~0.1–0.5 mW | Fast | $25–65 | 3.0 V: no boost/shifters |
| E-paper 2.9" (296×128) | 1-bit / 4-grey | Excellent | Needs light | ~0 static | 0.3 s partial, 1–2 s full | $10–20 | Small |
| Transflective colour TFT (2.0–2.4") | Full | Good (backlight off) | Backlight | 15–30 mW + backlight | Fast | $15–35 | Bigger MCU |
| **IPS TFT, high brightness (chosen for v0.2)** | Full | OK at 1200 nit, backlight-hungry | Great | ~33 mW logic + up to ~500 mW backlight | Fast | ~$16 | Bigger MCU |
| OLED | Full | Poor | Great | 20–150 mW | Fast | $5–20 | Colour panels ≤ ~1.5" |

## Sources found

**Sharp LS027B7DH01(A)**
- [AliExpress LS027B7DH01A](https://www.aliexpress.com/item/1005005611440829.html) · [Tindie SIKTEC board](https://www.tindie.com/products/siktec/new-sharp-memory-lcd-27inch-400x240-display-ls027/) · [Amazon](https://www.amazon.com/2-7in-400X240-LS027B7DH01A-LS027B7DH01-Display/dp/B0F1FRLBHP)
- [Adafruit 4694 breakout](https://adafruit.com/product/4694): $44.95, out of stock at the check; includes 3 V regulator, 5 V boost, level shifting.
- Digi-Key LS027B7DH01 425-2907-ND: $32.24, 0 stock, 28-week lead. Mouser lists 852-LS027B7DH01 (stock not shown).
- Pinout verified from the Sharp datasheet (alldatasheet mirror). Used in the Playdate.

**JDI LPM027M128C (colour MIP)**
- [AliExpress](https://www.aliexpress.com/item/1005009104635881.html) · [Switch Science](https://www.switch-science.com/catalog/5395/): ¥9,460, sold out / discontinued; confirms **3.0 V supply** and a backlight.
- Reference projects: [pizero_bikecomputer](https://github.com/hishizuka/pizero_bikecomputer/blob/master/doc/hardware_installation.md) uses this panel; drivers [JDI_MIP_Display](https://github.com/Gbertaz/JDI_MIP_Display), [memory-lcd-spi](https://github.com/andelf/memory-lcd-spi).

**E-paper**
- [2.9" partial refresh 4-grey (AliExpress)](https://www.aliexpress.com/i/3256801652983286.html) · [2.9" 296×128 (AliExpress)](https://www.aliexpress.com/item/32811674328.html) · [GDEY029T94 with touch and front light](https://buyepaper.com/products/gdey029t94-ft01)

**Transflective / sunlight-readable TFT**
- [DisplayModule 2.0" transflective ST7789](https://www.displaymodule.com/products/2-0-inch-240x320-tft-st7789-spi-mcu-rgb-dm-tft20-435)
- Newhaven [NHD-2.4-240320CF-CSXN#-F](https://newhavendisplay.com/2-4-inch-sunlight-readable-tft-without-touchscreen/): 1000 nit, transmissive TN, parallel only, $16.64, same 42.8 × 59.91 × 2.55 outline.
- Newhaven [2.4" sunlight-readable resistive](https://newhavendisplay.com/2-4-inch-sunlight-readable-resistive-tft-display/).
- Many AliExpress "sunlight readable" listings are just bright transmissive panels.

**IPS TFT (+ touch)**
- **[Newhaven NHD-2.4-240320AF-CSXP](https://newhavendisplay.com/2-4-tft-lcd-ips-high-brightness-display/)**: IPS, 1200 nit, SPI, $13.94 direct / $15.86 Mouser. Full data in [part-specs.md](part-specs.md).
- [Adafruit 2090 2.8" + cap touch](https://adafruit.com/product/2090): $29.95, CST026 touch, 4-LED backlight, board 81.3 × 62.5.
- [Waveshare 2.8" ST7789 + touch](https://www.waveshare.com/2.8inch-capacitive-touch-lcd.htm) · [BuyDisplay 2.8" ST7789V capacitive](https://www.buydisplay.com/2-8-inch-tft-lcd-display-capacitive-touch-screen-st7789v-spi-240x320) · [AliExpress search](https://www.aliexpress.com/w/wholesale-2.8-capacitive-touch-screen.html)

## Why IPS TFT for v0.2
It's cheap, in stock at Mouser, well documented (drawing, pinout, backlight data), SPI with ST7789 (LVGL driver exists), and the same outline family as Newhaven's sunlight-readable TN panel. The cost is backlight power; the ambient-light sensor handles auto-dimming.
