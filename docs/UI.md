# On-device UI — "Lucent"

**Status:** design reference. It renders in the browser only; there is no firmware yet. Pixel values here were checked against the renderer, not against a real panel.

- **Source of truth:** [`viewer/ui/screens_color.js`](../viewer/ui/screens_color.js). The 3D viewer and the screenshots below both render from it, and the firmware (LVGL 9 on the ESP32-S3) is meant to port it 1:1. If this document and the code disagree, the code wins, so fix the document.
- **Screenshots:** [`docs/ui/`](ui/). `overview.png` shows every screen in a device frame with the three front keys. Each screen also has `<id>.png` (1×) and `<id>@3x.png` (nearest neighbour). Every frame is quantised to RGB565 before export, so gradient banding in the PNGs is what the panel will show.
  - Regenerate: serve the repo root with `python3 -m http.server 8765`, then run `node docs/ui/shoot.mjs`. This needs Playwright with Chromium, installed locally or globally.
  - [`docs/ui/harness.html`](ui/harness.html) sets the frame time used for each screen.
  - [`docs/ui/make_fonts.py`](ui/make_fonts.py) rebuilds the bundled fonts.
- **Replaces "Meridian".** The earlier neon, chamfered language was dropped after owner review ("like Tron… trying way too hard"). The API, screen ids, soft-key mapping and data model are unchanged.
- The monochrome renderer for the old Sharp memory LCD, `viewer/ui/screens.js`, is legacy.

![overview](ui/overview.png)

## Display facts

| | |
|---|---|
| Panel | 2.4" IPS TFT, ST7789, 1200 nit |
| Resolution | **240 × 320 px, portrait**, ≈ 166 ppi (1 px ≈ 0.153 mm) |
| Colour | RGB565 (16-bit) |
| Frame buffer | 150 KB. Use two partial draw buffers (240 × 40) in internal RAM. Keep the wallpaper, fonts and A8 bitmaps in flash or PSRAM |
| Input | 3 unlabelled front keys under the screen (L / C / R), a left side button (power/back) and a right side button (menu) |

## 1. Design language: Lucent

*Frosted glass floating over deep colour.* Lucent borrows the calm of Apple's Liquid Glass and watchOS widgets, and builds it only from things a microcontroller can draw cheaply and honestly.

Principles:

1. **Function first.** Every data page has one hero number (80 px, ≈ 8.9 mm cap height) and a small set of tiles. Values are white, labels are grey, and units are dimmer still. A rider should be able to read the screen in half a second at speed and in sunlight.
2. **Glass, not glow.** Content sits on translucent rounded panels over a soft, dark backdrop. Depth comes from layering, a fill gradient, a 1 px inner edge and a 1 px top highlight. Nothing is blurred at runtime and nothing glows.
3. **Colour means something.** The chrome is neutral. Chroma appears only for effort zones, gradient, the route and selection (one blue accent), and status (good / warn / bad). The one ambient use of colour is the **zone light**, a soft wash in the current zone colour behind the glass. It is still information: the whole page warms as your effort climbs.
4. **Soft geometry.** Large radii (18 px cards, 14 px tiles, full capsules for keys, chips and gauges). No chamfers, ticks or brackets.
5. **Quiet motion.** Things slide and settle without bounce. The only loop is the heartbeat, which beats at your real heart rate.
6. **Keys are glass pills** centred over the physical keys. The primary action is the one near-white pill.

## 2. Palette

Values are snapped to RGB565 (truncation, the same as `lv_color_to_16`). The hex column is what the panel shows. Put them in one `theme.h` table. Where translucency is used, it is written as an opacity (`opa`) on top of these colours. It is never baked into a new colour.

| Token | Hex | RGB565 | Use |
|---|---|---|---|
| `night` | `#081429` | `0x08A5` | backdrop top; lap sheet base |
| `deep` | `#000810` | `0x0042` | backdrop bottom; scrim |
| `glowA` | `#293C84` | `0x29F0` | backdrop cool light (baked, top left) |
| `glowB` | `#084952` | `0x0A4A` | backdrop teal light (baked, bottom right) |
| `ink` | `#080C10` | `0x0862` | label on the prominent key, icon on light tiles, knob ring |
| `text` | `#F7F7FF` | `0xF7BF` | numerals, primary text, prominent key fill |
| `text2` | `#ADB2C6` | `0xAD98` | labels, secondary text |
| `text3` | `#6B7584` | `0x6BB0` | units, captions, inactive |
| `glass` | `#FFFFFF` | `0xFFFF` | glass fill / edge / highlight (always with an opa) |
| `mapGlass` | `#101821` | `0x10C4` | card fill over the live map (opa 78–84 %) |
| `accent` | `#0886FF` | `0x0C3F` | route ahead, selection, progress, rider |
| `good` | `#31D35A` | `0x368B` | on target, faster, GPS OK |
| `warn` | `#FF9E08` | `0xFCE1` | off target, slower, low battery |
| `bad` | `#FF4539` | `0xFA27` | compass north, errors |
| `z1` | `#8C96A5` | `0x8CB4` | Z1 recovery |
| `z2` | `#0886FF` | `0x0C3F` | Z2 endurance |
| `z3` | `#31D35A` | `0x368B` | Z3 tempo |
| `z4` | `#FFD708` | `0xFEA1` | Z4 threshold |
| `z5` | `#FF9E08` | `0xFCE1` | Z5 VO2 max |
| `z6` | `#FF4539` | `0xFA27` | Z6 anaerobic |
| `z7` | `#BD59F7` | `0xBADE` | Z7 neuromuscular |
| `mapBg` / `road` / `roadMajor` | `#181821` / `#292C39` / `#39414A` | `0x18C4` / `0x2967` / `0x3A09` | map ground and streets |
| `water` / `park` | `#102039` / `#102821` | `0x1107` / `0x1144` | map areas |
| `routeDone` / `routeEdge` | `#5A6173` / `#083C84` | `0x5B0E` / `0x09F0` | travelled route; 2 px darker edge of the route ahead |

The zone colours follow Apple's dark-mode system colours, so they are familiar and hold up against the dark backdrop. The same colours carry across scales:

- HR zones use `z1 z2 z3 z5 z6`.
- Gradient uses `z3` (< 3 %), `z4` (< 6 %), `z5` (< 9 %), `z6` (< 12 %) and `z7` (steeper).
- The accent is the same blue as `z2`. The two never compete on one screen: the map has no zones, and zone screens use no accent.

## 3. Type

One OFL family: **Inter** (rsms/inter). It is a neutral grotesk close to SF Pro in spirit.

- **Inter Display** (optical size 32) is used for numerals ≥ 20 px.
- **Inter** (optical size 14) is used for text.
- Static TTFs are built from the Google Fonts variable font by `docs/ui/make_fonts.py`, which:
  - instances the two optical sizes at weights 500 and 600,
  - **freezes tabular figures into the cmap**, so changing numbers never jitter (lv_font_conv does not apply OpenType features), and
  - subsets the fonts to the ranges below.
- The files live in `viewer/ui/fonts/`, with the licence in `OFL-Inter.txt`.
- Letter-spacing maps to LVGL `text_letter_space`. Negative values are fine.

| Token | Face | Weight | px | Tracking | Use |
|---|---|---|---|---|---|
| `hero` | Inter Display | 600 | 80 | −2 | ride speed, heart rate |
| `heroDec` | Inter Display | 600 | 44 | −1 | decimal part of the hero (".3"), on the same baseline |
| `xl` | Inter Display | 600 | 52 | −1.5 | lap time, summary distance |
| `timer` | Inter Display | 600 | 34 | −0.8 | workout countdown inside the ring |
| `lg` | Inter Display | 600 | 30 | −0.5 | power value, turn distance |
| `md` | Inter Display | 600 | 24 | −0.5 | tile values (also 20–21 px variants for 3-up tiles) |
| `sm` | Inter | 600 | 17 | 0 | compact values (lap stats, climb title) |
| `title` | Inter | 600 | 15 | 0 | list items, workout step |
| `body` | Inter | 500 | 13 | 0 | units after big numbers, secondary text |
| `label` | Inter | 600 | 11 | +0.3 | UPPERCASE field labels |
| `key` | Inter | 600 | 12 | 0 | soft-key labels (Title Case) |
| `caption` | Inter | 500 | 10–11 | 0 | axes, sub-lines, time-in-zone rows |

lv_font_conv (4 bpp), for example:

```bash
# numerals only (hero, heroDec, xl, timer, lg): digits . : − + % and space
lv_font_conv --bpp 4 --size 80 --no-compress --format lvgl --font InterDisplay-SemiBold.ttf \
  -r 0x20,0x25,0x2B,0x2D-0x3A,0x2212 -o font_hero_80.c
# text faces: printable ASCII plus · × – — ’ … • ← ↑ → ↓ − ° and NBSP
lv_font_conv --bpp 4 --size 13 --format lvgl --font Inter-Medium.ttf \
  -r 0x20-0x7E,0xA0,0xB0,0xB7,0xD7,0x2013,0x2014,0x2019,0x2022,0x2026,0x2190-0x2193,0x2212 -o font_body_13.c
```

Budget: about 14 fonts. The numeral-only faces are small (the 80 px face is about 25 KB at 4 bpp), and the text faces run 8–20 KB each. All of them fit in flash (XIP).

## 4. Spacing, radii, layout grid

| Token | Value | Notes |
|---|---|---|
| grid | 4 px | all offsets are multiples of 2, most of 4 |
| `margin` | 8 px | screen edge to card; content column x 8..232 (224 px) |
| `gutter` | 6 px | between tiles; two-up tile = 109 px, three-up = 70/71/71 px |
| `pad` | 12 px | card inner padding (text starts at card x + 12) |
| status bar | y 0..22 | clock at x 14 baseline 15; page dots centred at y 8; battery at x 203 |
| content | y 24..288 | nothing is drawn below y 288 except the keys |
| key area | y 292..320 (`BAR` = 28) | pills at y 295, 70 × 22, centred on x 40 / 120 / 200 |
| `R.card` | 18 | hero and large cards (sheet 22) |
| `R.field` | 14 | tiles, list rows (`R.row`) |
| `R.pill` | 11 | keys (= half height); chips and gauge segments are capsules too |
| `R.tile` | 9 | 26–28 px icon tiles |

## 5. Glass in LVGL (how every effect is built)

LVGL 9 has no backdrop blur, and we do not want one: it would mean reading back the frame buffer and running a multi-pass filter on every refresh. Lucent fakes glass with three honest layers.

### 5.1 Backdrop, pre-rendered and already soft

The backdrop is a full-screen `lv_image` of a 240 × 320 RGB565 bitmap in flash (150 KB, `LV_COLOR_FORMAT_RGB565`). The bitmap is:

- a vertical gradient `night → deep`,
- plus two large radial lights (`glowA` at (30, 20) r 230, opa 55 %; `glowB` at (230, 300) r 210, opa 45 %),
- baked offline with a **4 × 4 ordered dither**, so the gradient does not band in 565.

The renderer bakes the same bitmap once at start-up (`bakeWallpaper`). Because the backdrop is already blurry, a translucent panel over it looks frosted: there is no detail behind it that would reveal the missing blur.

### 5.2 Zone light (ride, heart, climb, workout)

The zone light is a soft wash in the current zone colour behind the glass.

- One 240 × 200 **A8** bitmap with a radial falloff (≈ 47 KB, 1, 0.55 at 45 % radius, 0 at the edge) is drawn as an `lv_image` with `image_recolor` = zone colour and `image_opa` = 24 % (12 % on the workout page, 22 % on climb).
- Changing zone only changes a style property. The bitmap never changes.
- It is blended at runtime without dither, so expect slight banding (visible in the renders).

### 5.3 Glass panel

A glass panel is one `lv_obj` plus one child for the highlight:

```c
// recipe: GLASS.card (values from screens_color.js)
lv_style_set_radius(&st_glass, 18);
lv_style_set_bg_color(&st_glass, lv_color_white());
lv_style_set_bg_grad(&st_glass, &grad_glass);      // VER, stop0 = white opa 38 (15 %), stop1 = white opa 18 (7 %)
lv_style_set_bg_opa(&st_glass, LV_OPA_COVER);      // per-stop opa carries the translucency (LVGL 9 grad stops have opa)
lv_style_set_border_width(&st_glass, 1);
lv_style_set_border_color(&st_glass, lv_color_white());
lv_style_set_border_opa(&st_glass, 26);            // 10 %: the inner edge
lv_style_set_shadow_width(&st_glass, 0);           // no shadow on panels
// highlight child: same size, IGNORE_LAYOUT, not clickable
lv_style_set_bg_opa(&st_hi, LV_OPA_TRANSP);
lv_style_set_border_side(&st_hi, LV_BORDER_SIDE_TOP);
lv_style_set_border_width(&st_hi, 1);
lv_style_set_border_opa(&st_hi, 87);               // 34 %: the specular line along the top edge
lv_style_set_radius(&st_hi, 18);
```

If the gradient stop opacities misbehave on a given LVGL build, the fallback is a flat `bg_opa` at the average value (≈ 11 %). This loses a little depth but nothing else.

| Recipe | Fill top → bottom | Edge | Highlight | Used for |
|---|---|---|---|---|
| `card` | white 15 % → 7 % | 10 % | 34 % | hero, power, lists, profile |
| `field` | white 12 % → 6 % | 9 % | 28 % | tiles, menu rows |
| `raised` | white 26 % → 16 % | 14 % | 50 % | selected menu row |
| `key` | white 18 % → 10 % | 12 % | 40 % | soft-key pills |
| `prominent` | `text` 96 % → 90 % | — | — | primary key (ink label) |
| `map` | `mapGlass` 84 % → 78 % | white 10 % | white 26 % | cards and keys over the live map: **plain translucent fill, no blur** |
| `sheet` | `night` 100 % (opaque), then `card` on top | white 14 % | white 45 % | lap sheet (must read over anything) |

**Shadows:** only the lap sheet has one (`shadow_width 18`, `shadow_ofs_y 6`, black opa 45 %). It is drawn only while the sheet is visible. LVGL caches shadow shapes (`LV_DRAW_SW_SHADOW_CACHE_SIZE`), so set that cache to at least 22 so the sheet's corner shadow is reused while it slides.

**Corners:** LVGL radii are circular arcs, not Apple's continuous-curvature squircle. At 14–22 px on this panel the difference is sub-pixel, so we accept it.

### 5.4 Components

| Component | LVGL |
|---|---|
| **Field (tile)** | glass `field`, UPPERCASE `label` at (x+12, y+14), value baseline at y+h−8, unit after it in `body`/`text3`. An optional 3 px zone dot before the label carries meaning. The value stays white |
| **Gauge** | a row of capsule `lv_obj`s, one per zone (radius = h/2, 5 px tall, 2 px apart). The active one is at opa 100 %, the others at 40 %. The knob is a circle `lv_obj` (white, r 5.5) over an `ink` circle at 70 % (r 7). A target window is a transparent capsule with a 1.5 px white border at 85 % |
| **Ring** | `lv_arc`, width 10, `arc_rounded`, background arc white at 12 %, indicator in the zone colour |
| **Chip** | capsule 18 px tall, fill = colour at 22 %, label 11 px/600 in the colour, optional 11 px icon |
| **Key pill** | glass `key` 70 × 22 radius 11, label `key` Title Case, optional 8–10 px glyph (pause bars, −, +, ◎). The primary is `prominent` with an `ink` label |
| **Status bar** | clock 13/600 at (14, 15); page control = 5 px dots at 30 %, the current one a 14 × 5 capsule; battery = 21 × 10 rounded outline at 45 % with a level fill (warn under 20 %) |
| **Icons** | A8 bitmaps drawn with `image_recolor`, 11–26 px |

## 6. Screens

The coordinates below are for the 240 × 320 frame. Every screen reserves y 292..320 for the key pills, and content ends at y 288 or above.

### ride — keys: Lap · Page · **Pause**
- Zone light in the current power-zone colour.
- **Speed card** (8, 26, 224 × 92):
  - `SPEED` label at (20, 43); trend `↑ avg 18.9` on the right (arrow in `good`/`warn`).
  - Hero `22` + `.3` with its baseline at y 107, x 17; `mph` after it in `body`/`text3`.
- **Power card** (8, 124, 224 × 62):
  - `POWER 3S` label at y 140; zone chip (`● Z4 Threshold` in the zone colour) right-aligned.
  - `275` in `lg` with its baseline at y 167, then `W`; `104% FTP` on the right.
  - 7-zone gauge at (20, 174, 200 × 5); the axis runs from 0 to 1.6 × FTP.
- **Tiles**, 109 × 46: Heart (zone dot) at (8, 192), Cadence at (123, 192), Distance at (8, 242), Time at (123, 242).

### hr — keys: Lap · Page · **Pause**
- Zone light in the HR-zone colour.
- **HR card** (8, 26, 224 × 112):
  - Label and zone chip at y 44.
  - Hero with its baseline at y 112, then `bpm`.
  - Heart icon 24 px at (196, 66). It beats at the measured BPM (scale 1 → 1.14, opa 60 → 100 %, exp decay).
  - 5-zone gauge at (20, 122).
- **Time in zone card** (8, 144, 224 × 94): 5 rows at a 14 px pitch from y 168. Each row has:
  - the zone name (10 px),
  - a capsule bar at x 42 (110 × 6, zone colour at 55 %, the current zone at 100 %, on a white 8 % track),
  - the time right-aligned at x 196,
  - the share of the ride at x 220.
- **Tiles**: Avg at (8, 244) and Max at (123, 244), 109 × 44.

### climb — keys: Lap · Page · **Pause**
- Zone light in the current gradient colour (22 %).
- **Title row**: `Hawk Hill` (17/600) at (12, 45); `Climb 2 of 3` in `body`; `Cat 3` chip (`z5`) right-aligned at y 31.
- **Tiles** (y 54, h 52, widths 70/71/71 at x 8/84/161): Grade (gradient-colour dot), To top, Gain. Values use Display 21 px.
- **Profile card** (8, 112, 224 × 176):
  - `PROFILE` label, and `ft to go` on the right.
  - The profile spans x 20..220, y 162..256. Each segment is filled with a vertical gradient in its gradient colour (85 % → 18 %) and has a 2 px top line.
  - Ridden segments go grey (`text3`, 45 % → 8 %).
  - 1 px guides at white 6 %; the axis line at white 25 %; axis labels in `caption` at y 272.
  - Summit flag at the top right.
  - Rider: accent dot (r 7.5) with a white core (r 4.5), and a 1 px white 50 % drop line to the axis.

### map — keys: − Zoom · ◎ Centre · + Zoom (no primary)
- **Map**: full-bleed, heading-up, at k = 0.5 × zoom around the rider at (120, 200).
  - Streets are 6 px `road` and arterials 10 px `roadMajor`, with `water` and `park` areas.
  - Route ahead: 10 px `routeEdge` under 6 px `accent`. Travelled route: 6 px `routeDone`.
  - Rider puck: a white disc (r 9) with an accent core (r 6.5), and a 34 px heading cone (accent 45 % → 0, one `lv_image` A8).
- **Turn card** (8, 8, 224 × 70, `map` glass, r 20):
  - Accent tile 54 × 54 r 14 at (16, 16) with a 5 px white rounded arrow.
  - Distance in `lg` at (80, 44).
  - `Right onto` (`text2`) followed by the **street** (13/600) at y 64.
  - Clock at the top right in 11 px `text3`.
- **Scale bar** at (14, 96), with its label to the right.
- **Compass** (`map` glass disc, 32 px) at (216, 102). The red N needle rotates by −heading.
- **Bottom tiles** (`map` glass, 108 × 46) at (8, 242) and (124, 242): Speed, and `ARRIVE 8:21` (accent label) with distance to go.
- The key pills use the `map` glass recipe here, so they read over the map.

### workout — keys: Skip · Page · **Pause**
- Zone light in the target colour at 12 %, centred on the ring.
- **Header**: `STEP 4 OF 7` label and `Sweet spot` (`title`) on the left; `NEXT` and `Rest 5:00` on the right.
- **Ring** at centre (120, 116), r 50, width 10, showing interval progress:
  - `Interval 2/3` (10/600) at y 97.
  - Countdown in `timer` with its baseline at y 128.
  - `of 10:00` at y 144.
- **Target card** (8, 176, 224 × 70):
  - `TARGET 240–262 W` label; status chip on the right (`On target` in `good`, or `Push +n` / `Ease −n` in `warn`).
  - Power in `lg` with its baseline at y 222.
  - Heart value `md` with a beating icon, right-aligned.
  - Full-width gauge at y 231: neutral grey outside the window, the target colour inside it, and a white window outline.
- **Session card** (8, 252, 224 × 36): steps as rounded blocks whose height is the intensity. Past steps are white 16 %, the current one is its colour at full, and future ones are at 70 %. A 2 px white "now" line marks the position.

### status (sensors) — keys: Scan · Page · **Pair**
- One grouped glass list (8, 28, 224 × 260) with six 43 px rows. Hairlines (white 8 %) are inset to x 52.
- Each row has:
  - a 28 px coloured icon tile (r 9, white glyph; `ink` glyph on yellow and green),
  - the name (`title`) and a sub-line (11 px `text2`),
  - the value right-aligned at x 202,
  - 4 signal bars at x 208 (white; empty bars at 20 %), or a battery capsule.

### lap (overlay on ride) — keys: Lap · Page · **Pause**
- **Timeline** (loops every 6 s):
  - 0–0.35 s: the sheet slides from above to y 26 (`settle`, no bounce).
  - It holds until 4.4 s.
  - 4.4–4.75 s: it slides out (`inOut`).
- **Scrim**: `deep` at 50 % × progress over y 0..292.
- **Sheet** (8, 26, 224 × 184, r 22, `sheet` + `card` glass, the only shadow in the UI):
  - Header: `Lap 4` chip (accent, flag icon) and `vs lap 3` on the right.
  - Lap time in `xl` with its baseline at y+86, plus `.4` in `lg` `text2`.
  - `faster` and `−0:14` in `good` on the right.
  - Hairline, then 3 stat columns (Speed / Power / Heart), each with its delta in `good` or `warn`.
  - Auto-dismiss capsule (4 px) at y+168 that shrinks over the hold.

### summary — keys: Discard · Page · **Save**
- **Status title**: `Ride complete`.
- **Header**: `Sat 27 Sep · Hudson loop` (`body`, `text2`) at y 42.
- **Distance**: `48.2` in `xl` with its baseline at y 94, then `mi`. A `3 PRs` chip (`z4`, flag icon) sits on the right at y 62.
- **Elevation card** (8, 106, 224 × 70):
  - Label and `3,412 ft`.
  - The trace is a 2 px accent line with an accent fill (60 % → 4 %).
  - The trace draws itself left to right over 1.5 s.
- **3 × 2 tiles** (70/71/71 × 50, rows at y 182 and 238): Moving, Avg mph, Avg W, NP W, Avg bpm, TSS. The units are in the labels because a 71 px tile cannot fit "17.9 mph" at 20 px.

### menu — keys: Prev · **Open** · Next
- **Status title**: `Menu`.
- **Rows**: six glass `field` rows (224 × 38, r 14) at a 43 px pitch from y 28.
- **Selection**: a `raised` glass row that glides 220 ms (`ease_out`) to the new row.
- **Each row**: a 26 px icon tile (white 12 %, or accent when selected), the name (`title`) at y+17, a sub-line (11 px) at y+31, and a chevron at x 217–221.

### boot — no keys
- **Timeline** (6 s loop):
  - 0–0.8 s: the backdrop fades up from black.
  - 0.5–1.3 s: the mark and wordmark fade in and rise 10 px (`settle`).
  - 1.2–4.6 s: the progress runs.
  - 5.2–6 s: everything fades out.
- **Mark**: a 68 px glass disc at (120, 132), holding a 5 px white ring (r 17) with a small gap and an accent dot at the top.
- **Wordmark**: `OpenCycle` in Inter Display 28/600 with its baseline at y 202.
- **Progress**: an 80 × 4 capsule at (80, 236).
- **Status line** (11 px `text2`) at y 260: `Finding satellites` → `Connecting sensors` → `Linking phone` → `Ready`.

## 7. Soft-key mapping

| Screen | Left | Centre | Right (primary unless noted) |
|---|---|---|---|
| ride, hr, climb, lap | Lap | Page | **Pause** |
| map | Zoom out | Centre | Zoom in (no primary) |
| workout | Skip | Page | **Pause** |
| status | Scan | Page | **Pair** |
| summary | Discard | Page | **Save** |
| menu | Prev | **Open** (centre is primary) | Next |
| boot | — | — | — |

`Page` cycles through ride → hr → climb → map → workout → status (`PAGES`). The left side button is back/power, and the right side button opens the menu. A key press gives feedback: the pill flips to `raised` for 120 ms. This is not shown in the renders.

## 8. Motion

All motion is a pure function of `t` in the renderer. The firmware uses `lv_anim` with the named path.

| What | Duration | Path |
|---|---|---|
| lap sheet in / out | 350 / 350 ms | `settle` (≈ `ease_out` quartic, no overshoot) / `ease_in_out` |
| menu selection glide | 220 ms | `ease_out` |
| page change | 200 ms cross-fade of the content layer (optional; a hard cut is fine) | `ease_out` |
| heartbeat | 60 / BPM | exp decay, scale 1.14 → 1 |
| summary trace reveal | 1.5 s | `ease_in_out` |
| zone light colour change | 400 ms | recolour cross-fade (`image_recolor` animated) |
| boot | 6 s | see above |

## 9. Constraints and open risks

- **Blending cost.** Every glass pixel is an alpha blend over the backdrop, which is also a blend over the zone light. When a number changes, LVGL redraws that area: image → A8 recolour blend → gradient fill → border → text.
  - The ESP32-S3 with software rendering should manage the per-second updates easily.
  - Full-screen redraws (page change, lap sheet slide) are about 3 blend passes over 76,800 px, estimated at 25–40 ms per frame. Not yet measured. If it is too slow, drop the lap sheet to an 8 fps slide or pre-render the static card chrome into an `lv_canvas` layer.
- **Gradient stop opacity.** The glass relies on LVGL 9 gradients having per-stop `opa`. The fallback (flat `bg_opa`) is documented in 5.3.
- **Banding.** The runtime blends are not dithered (LVGL 9 removed `LV_DITHER_GRADIENT`), so the zone light shows faint 565 steps. The baked backdrop is dithered. If the banding is objectionable on the real panel, bake one dithered backdrop per zone colour (7 × 150 KB = 1 MB flash) and drop the runtime A8 light.
- **Sunlight.** The design has dark translucent panels on a 1200-nit IPS. White numerals on about 15 % glass stay high contrast. But the `text3` units (≈ 4.2:1 on glass) and 10 px captions are the weakest elements, and need checking outdoors on the real panel. A light theme is *not* implemented. The tokens allow one: the backdrop becomes a pale bitmap, the glass becomes black at 4–8 % with a white 60 % highlight, and the text flips. This is untested.
- **Glyph coverage.** The fonts are subset to the ranges in section 3. Street names with accents (é, ü, ß…) need `0xA0–0xFF` added to the text faces (≈ +6 KB each).
- **Map rendering.** The live vector map with 6–10 px roads, round joins and translucent cards over it is the heaviest screen, and has not been profiled. Tiles and style are not decided (see `docs/FIRMWARE.md`).
- **Nothing here is verified on hardware.** Pixel sizes, contrast and timing are from the browser renderer only.

## Adding a screen

1. Add `{ id, name, desc }` to `SCREENS`, labels to `SOFTKEYS`, and the primary index to `PRIMARY` (and to `PAGES` if `Page` should reach it).
2. Write `DRAW.<id>(d, t, data)` using only `glass`, `field`, `gauge`, `ring`, `chip`, `icon` and text tokens. Keep content inside y 24..288.
3. Add a representative time to `SHOT_T` in `docs/ui/harness.html`, run `node docs/ui/shoot.mjs`, and look at the 1× PNG before committing.
