# On-device UI

Source: [`viewer/ui/screens.js`](../viewer/ui/screens.js). The viewer and the 3D model both render from it, and firmware will port it.

## Display facts

- Sharp LS027B7DH01A, mounted portrait: **240 × 400 px**, 1 bit per pixel, reflective, no backlight.
- Active area 35 × 59 mm (~6.9 px/mm, ~174 ppi).
- Frame buffer 12,000 bytes. Full redraw ≈ 13 ms at 8 MHz SPI; only changed lines need sending.
- EXTCOMIN must toggle ~1 Hz (hardware pin, EXTMODE tied high).

## Rules for screens

1. **Two colours only.** Tones are 4 × 4 ordered-dither patterns (`d.dither(x, y, w, h, level 0–16, polygon?)`).
2. **Fonts:** Barlow Condensed (numbers, 600/700) and Barlow Semi Condensed (labels, 500/600), both OFL. On device they become 1-bpp LVGL fonts via `lv_font_conv`. Keep labels ≥ 11 px, uppercase with 1.2 px tracking.
3. **Hierarchy:** one hero number per screen, then a 2 × 2 grid, then a footer (distance + elapsed time). Rules are 2 px.
4. **Inversion = urgency.** Turn cues and alerts use white-on-black bars; nothing else does.
5. **Motion:** only what the panel can do at ~30 fps: slides, counters, map scroll. No fades.
6. Page dots at the bottom show position in the page cycle (the Page button advances).

## Screens

| id | Screen | Data |
|---|---|---|
| `ride` | Speed hero, power-zone bar, power / HR / cadence / grade, distance + time | GPS, sensors |
| `map` | Heading-up vector map, route casing, turn cue banner, north pointer, speed + distance to finish | On-device tiles from the phone app |
| `climb` | Climb profile shaded by grade, rider marker, distance and height left | Route elevation |
| `workout` | Step countdown, target power band, live power + HR, workout overview bars | Structured workout file |
| `status` | Paired sensors, GPS fix, phone link, battery estimate | System |
| `lap` | Slide-down lap summary overlay | Lap button |

## Adding a screen

1. Add `{ id, name, desc }` to `SCREENS`.
2. Add `DRAW.<id> = (d, t, data) => { ... }` using only `d.rect`, `d.hline`, `d.vline`, `d.text`, `d.label`, `d.dither`, and canvas paths via `d.g` in pure black/white.
3. Check it at "Actual size" in the viewer.
