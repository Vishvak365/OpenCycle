// OpenCycle device UI — "LUCENT" design language, reference renderer for the v0.2 colour display
// (2.4" IPS TFT, ST7789, 240 x 320 portrait, RGB565, ~166 ppi).
//
// Lucent: frosted-glass panels floating over a deep, softly lit backdrop. Calm and modern, with
// colour only where it means something (effort zones, gradient, route, alerts).
//
// This file is the spec that the firmware (LVGL 9 on the ESP32-S3) ports 1:1. It is organised the
// way the firmware theme will be:
//
//   C        palette      every colour is snapped to RGB565, so the preview shows what the panel shows
//   TYPE     type scale   Inter + Inter Display (one OFL family), a fixed set of sizes = lv_font_conv fonts
//   S, R     spacing, radii  4 px grid
//   GLASS    glass recipes  fill gradient + hairline border + top highlight, as LVGL style values
//   components            backdrop, glass, statusBar, keys (glass pills), field, gauge, ring, chip, icons
//   DRAW.<id>             one function per screen, built only from the components
//
// Honesty rules for the preview (see docs/UI.md, "Glass in LVGL"):
//   - no blur anywhere at runtime. The backdrop is a pre-rendered, already-soft bitmap (baked with an
//     ordered dither, as the firmware asset will be); glass is a translucent fill over it.
//   - the zone "light" is a soft A8 bitmap recoloured at runtime (LVGL image_recolor), not a blur.
//   - every frame is quantised to RGB565 at the end, like the panel.
//   - only rounded rects, 1 px borders, 2-stop vertical gradients with per-stop opacity, arcs with
//     round caps, lines, images and text. Corner radii are circular (LVGL has no squircle).
//
// API (used by viewer/index.html and docs/ui/harness.html — keep it stable)
//   const dev = createDevice();      // offscreen 240x320 canvas
//   dev.render(screenId, t)          // one full frame; t = seconds, every animation is a pure fn of t
//   dev.canvas                       // the canvas, for textures and previews
//   SOFTKEYS[screenId]               // the three key labels for that screen, PRIMARY[screenId] = accent key
//   await fontsReady()               // loads the bundled OFL fonts with the FontFace API

export const W = 240, H = 320, BAR = 28;

export const SCREENS = [
  { id: 'ride', name: 'Ride', desc: 'Speed on a glass card, power with its zone gauge, then heart rate, cadence, distance and time. The backdrop glows softly in your power-zone colour.' },
  { id: 'hr', name: 'Heart', desc: 'Heart rate with a live pulse and the five-zone gauge, time spent in each zone, and ride averages.' },
  { id: 'climb', name: 'Climb', desc: 'The climb ahead coloured by gradient, where you are on it, and what is left to the top.' },
  { id: 'map', name: 'Navigation', desc: 'Heading-up dark map with the route in blue and the next turn on a translucent card. Keys: zoom out, re-centre, zoom in.' },
  { id: 'workout', name: 'Workout', desc: 'Interval countdown in a progress ring, your power against the target window, and the whole session below.' },
  { id: 'status', name: 'Sensors', desc: 'Paired sensors with signal strength, GPS fix, phone link and battery, as one grouped glass list.' },
  { id: 'lap', name: 'Lap alert', desc: 'Press LAP: a glass sheet slides over the ride page with deltas to the last lap, then slides away on a visible timer.' },
  { id: 'summary', name: 'Ride summary', desc: 'End-of-ride card: distance, the elevation trace, key averages and PRs. Save is the primary key.' },
  { id: 'menu', name: 'Menu', desc: 'Right side button opens it. Glass rows; left/right keys move the selection, centre opens.' },
  { id: 'boot', name: 'Boot', desc: 'Power-on: the backdrop fades up, the wordmark settles, a slim progress bar reports GPS and sensors.' },
];

// Three labels per screen, left / centre / right key. PRIMARY is the index of the prominent (filled) key, -1 = none.
export const SOFTKEYS = {
  ride: ['LAP', 'PAGE', 'PAUSE'], lap: ['LAP', 'PAGE', 'PAUSE'], climb: ['LAP', 'PAGE', 'PAUSE'], hr: ['LAP', 'PAGE', 'PAUSE'],
  map: ['ZOOM OUT', 'CENTRE', 'ZOOM IN'], workout: ['SKIP', 'PAGE', 'PAUSE'], status: ['SCAN', 'PAGE', 'PAIR'],
  summary: ['DISCARD', 'PAGE', 'SAVE'], menu: ['PREV', 'OPEN', 'NEXT'], boot: ['', '', ''],
};
export const PRIMARY = { ride: 2, lap: 2, climb: 2, hr: 2, workout: 2, status: 2, summary: 2, map: -1, menu: 1, boot: -1 };
// the PAGE key cycles these data pages (page dots in the status bar)
export const PAGES = ['ride', 'hr', 'climb', 'map', 'workout', 'status'];

// ---------------------------------------------------------------- palette
// Snap a colour to RGB565 the way lv_color_to_16 does (truncate), then expand back to 8 bit for display.
export function to565(hex) {
  const n = parseInt(hex.slice(1), 16), r = n >> 16, g = (n >> 8) & 255, b = n & 255;
  return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3);
}
function q(hex) {
  const v = to565(hex), r5 = v >> 11, g6 = (v >> 5) & 63, b5 = v & 31;
  const r = (r5 << 3) | (r5 >> 2), g = (g6 << 2) | (g6 >> 4), b = (b5 << 3) | (b5 >> 2);
  return '#' + [r, g, b].map((x) => x.toString(16).padStart(2, '0')).join('').toUpperCase();
}
const RAW = {
  // backdrop (baked into the wallpaper bitmap)
  deep: '#060910',     // bottom of the backdrop
  night: '#0F1628',    // top of the backdrop
  glowA: '#2B3F86',    // cool light, top left
  glowB: '#0E4A57',    // teal light, bottom right
  // ink and text
  ink: '#0A0D14',      // text on light (prominent key, chips)
  text: '#F4F6FA',     // primary text and numerals
  text2: '#A9B2C0',    // labels, secondary text
  text3: '#6B7485',    // units, captions, tertiary
  glass: '#FFFFFF',    // glass is white at low opacity (see GLASS)
  mapGlass: '#141821', // translucent card over the live map
  // one accent
  accent: '#0A84FF',   // route, selection, progress
  // status
  good: '#30D158', warn: '#FF9F0A', bad: '#FF453A',
  // effort spectrum: seven power zones; HR uses z1 z2 z3 z5 z6; gradient uses z3..z7
  z1: '#8E96A3', z2: '#0A84FF', z3: '#30D158', z4: '#FFD60A', z5: '#FF9F0A', z6: '#FF453A', z7: '#BF5AF2',
  // map (Apple-Maps-dark-like, low chroma so the route and the glass carry the screen)
  mapBg: '#181B22', block: '#1D2129', road: '#2A2F39', roadMajor: '#3A404C', water: '#132338', park: '#172A21',
  routeDone: '#586070', routeEdge: '#0B3D80',
};
export const C = Object.fromEntries(Object.entries(RAW).map(([k, v]) => [k, q(v)]));
const ZONES = [C.z1, C.z2, C.z3, C.z4, C.z5, C.z6, C.z7];
export const POWER_ZONES = [ // Coggan, fraction of FTP
  { n: 'Z1', name: 'Recovery', lo: 0, hi: 0.55 }, { n: 'Z2', name: 'Endurance', lo: 0.55, hi: 0.75 },
  { n: 'Z3', name: 'Tempo', lo: 0.75, hi: 0.90 }, { n: 'Z4', name: 'Threshold', lo: 0.90, hi: 1.05 },
  { n: 'Z5', name: 'VO2 max', lo: 1.05, hi: 1.20 }, { n: 'Z6', name: 'Anaerobic', lo: 1.20, hi: 1.50 },
  { n: 'Z7', name: 'Neuromuscular', lo: 1.50, hi: 9 },
];
export const HR_ZONES = [ // fraction of max HR
  { n: 'Z1', name: 'Easy', lo: 0.5, hi: 0.6 }, { n: 'Z2', name: 'Endurance', lo: 0.6, hi: 0.7 },
  { n: 'Z3', name: 'Tempo', lo: 0.7, hi: 0.8 }, { n: 'Z4', name: 'Threshold', lo: 0.8, hi: 0.9 },
  { n: 'Z5', name: 'Max', lo: 0.9, hi: 1.0 },
];
const HR_COL = [C.z1, C.z2, C.z3, C.z5, C.z6];
export const gradeColor = (g) => g < 3 ? C.z3 : g < 6 ? C.z4 : g < 9 ? C.z5 : g < 12 ? C.z6 : C.z7;
const powerZone = (w, ftp) => Math.max(0, POWER_ZONES.findIndex((z) => w / ftp < z.hi));
const hrZone = (b, max) => Math.max(0, Math.min(4, HR_ZONES.findIndex((z) => b / max < z.hi)));

// ---------------------------------------------------------------- type scale
// One OFL family: Inter (text, opsz 14) and Inter Display (numerals, opsz 32), both with tabular
// figures frozen in (docs/ui/make_fonts.py). [family, weight, px, letter-space px]
const DISP = '"Inter Display", "Inter", system-ui, sans-serif';
const TEXT = '"Inter", system-ui, sans-serif';
export const TYPE = {
  hero: [DISP, 600, 80, -2],    // ride speed, heart rate
  heroDec: [DISP, 600, 44, -1], // decimal part of a hero value (".7"), same baseline
  xl: [DISP, 600, 52, -1.5],    // lap time, summary distance
  timer: [DISP, 600, 34, -0.8],   // workout countdown in the ring
  lg: [DISP, 600, 30, -0.5],    // power value, turn distance
  md: [DISP, 600, 24, -0.5],    // field values
  sm: [TEXT, 600, 17, 0],       // compact values (lists, chips, grids)
  title: [TEXT, 600, 15, 0],    // titles, list items
  body: [TEXT, 500, 13, 0],     // secondary text, units after big numbers
  label: [TEXT, 600, 11, 0.3],  // UPPERCASE field labels
  key: [TEXT, 600, 12, 0],      // soft-key labels
  caption: [TEXT, 500, 10, 0],  // axis numbers, tiny notes
};

// ---------------------------------------------------------------- spacing and radii
export const S = { unit: 4, margin: 8, gutter: 6, pad: 12, statusH: 22, keyY: H - BAR, keyH: 22, keyW: 70 };
export const R = { card: 18, field: 14, row: 14, pill: 11, chip: 8, tile: 9 };

// ---------------------------------------------------------------- glass recipes
// Each maps 1:1 to one LVGL style (+ a second object for the top highlight, see docs/UI.md).
//   top/bot: fill colour opacity at the top and bottom stop (bg_grad, VER, per-stop opa)
//   edge:    1 px border, all sides (border_opa)        hi: 1 px top highlight (border_side TOP)
export const GLASS = {
  card: { col: C.glass, top: 0.15, bot: 0.07, edge: 0.10, hi: 0.34 },      // default panel over the backdrop
  field: { col: C.glass, top: 0.12, bot: 0.06, edge: 0.09, hi: 0.28 },     // smaller tiles
  raised: { col: C.glass, top: 0.26, bot: 0.16, edge: 0.14, hi: 0.50 },    // selection, focused row
  key: { col: C.glass, top: 0.18, bot: 0.10, edge: 0.12, hi: 0.40 },       // soft-key pills
  prominent: { col: C.text, top: 0.96, bot: 0.90, edge: 0, hi: 0 },        // primary key: near-white, dark label
  map: { col: C.mapGlass, top: 0.84, bot: 0.78, edge: 0.10, hi: 0.26, edgeCol: C.glass }, // over the live map
  sheet: { col: C.night, top: 1, bot: 1, edge: 0.14, hi: 0.45, edgeCol: C.glass },  // lap sheet
};

// ---------------------------------------------------------------- fonts
const FONT_FILES = [
  ['Inter', 'Inter-Medium.ttf', '500'], ['Inter', 'Inter-SemiBold.ttf', '600'],
  ['Inter Display', 'InterDisplay-Medium.ttf', '500'], ['Inter Display', 'InterDisplay-SemiBold.ttf', '600'],
];
let fontsPromise = null;
export function fontsReady() {
  if (fontsPromise) return fontsPromise;
  if (typeof FontFace === 'undefined' || typeof document === 'undefined' || !document.fonts) return (fontsPromise = Promise.resolve());
  fontsPromise = Promise.all(FONT_FILES.map(([fam, file, weight]) => {
    const f = new FontFace(fam, `url(${new URL(`./fonts/${file}`, import.meta.url).href})`, { weight });
    return f.load().then((ff) => { document.fonts.add(ff); }).catch(() => {});
  })).then(() => {});
  return fontsPromise;
}

// ---------------------------------------------------------------- helpers
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const lerp = (a, b, k) => a + (b - a) * k;
export const EASE = {
  out: (k) => 1 - Math.pow(1 - clamp(k, 0, 1), 3),                         // lv_anim_path_ease_out
  inOut: (k) => { k = clamp(k, 0, 1); return k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2; },
  // critically-damped settle (no bounce) — lv_anim_path_custom_bezier3(0.2, 0.9, 0.3, 1.0) is close
  settle: (k) => { k = clamp(k, 0, 1); return 1 - Math.pow(1 - k, 4); },
};
function rgba(hex, a) {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${n >> 16},${(n >> 8) & 255},${n & 255},${a})`;
}
const fmtTime = (s) => { s = Math.max(0, Math.floor(s)); const h = Math.floor(s / 3600), m = Math.floor(s / 60) % 60, x = s % 60; return h ? `${h}:${String(m).padStart(2, '0')}:${String(x).padStart(2, '0')}` : `${m}:${String(x).padStart(2, '0')}`; };
const titleCase = (s) => s.toLowerCase().replace(/(^|\s)\S/g, (m) => m.toUpperCase());

// ---------------------------------------------------------------- backdrop (pre-rendered wallpaper)
// Firmware asset: one 240 x 320 RGB565 bitmap in flash (150 KB), generated offline with a 4x4 ordered
// dither so the soft gradients do not band. Here it is generated once, identically.
const BAYER = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5];
function bakeWallpaper(draw) {
  const cv = (typeof OffscreenCanvas !== 'undefined') ? new OffscreenCanvas(W, H) : Object.assign(document.createElement('canvas'), { width: W, height: H });
  const g = cv.getContext('2d', { willReadFrequently: true });
  draw(g);
  const im = g.getImageData(0, 0, W, H), p = im.data;
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    const i = (y * W + x) * 4, th = (BAYER[(y & 3) * 4 + (x & 3)] + 0.5) / 16;
    const r5 = Math.min(31, Math.floor(p[i] / 255 * 31 + th)), g6 = Math.min(63, Math.floor(p[i + 1] / 255 * 63 + th)), b5 = Math.min(31, Math.floor(p[i + 2] / 255 * 31 + th));
    p[i] = (r5 << 3) | (r5 >> 2); p[i + 1] = (g6 << 2) | (g6 >> 4); p[i + 2] = (b5 << 3) | (b5 >> 2); p[i + 3] = 255;
  }
  return im;
}
function blob(g, x, y, r, col, a) { // soft light: radial falloff (firmware: A8 bitmap with this profile)
  const gr = g.createRadialGradient(x, y, 0, x, y, r);
  gr.addColorStop(0, rgba(col, a)); gr.addColorStop(0.45, rgba(col, a * 0.55)); gr.addColorStop(1, rgba(col, 0));
  g.fillStyle = gr; g.fillRect(0, 0, W, H);
}
const WALLPAPERS = {
  deep: (g) => {
    const gr = g.createLinearGradient(0, 0, 0, H); gr.addColorStop(0, C.night); gr.addColorStop(1, C.deep);
    g.fillStyle = gr; g.fillRect(0, 0, W, H);
    blob(g, 30, 20, 230, C.glowA, 0.55);
    blob(g, 230, 300, 210, C.glowB, 0.45);
  },
};

// ---------------------------------------------------------------- device
export function createDevice() {
  const canvas = (typeof OffscreenCanvas !== 'undefined') ? new OffscreenCanvas(W, H) : Object.assign(document.createElement('canvas'), { width: W, height: H });
  const g = canvas.getContext('2d', { willReadFrequently: true });
  let wall = null;
  const d = {
    g, canvas, W, H,
    rect(x, y, w, h, c) { g.fillStyle = c; g.fillRect(Math.round(x), Math.round(y), Math.round(w), Math.round(h)); },
    rrect(x, y, w, h, r, c) { g.fillStyle = c; g.beginPath(); g.roundRect(x, y, w, h, Math.min(r, h / 2, w / 2)); g.fill(); },
    text(s, x, y, type, c = C.text, align = 'left', alpha = 1) {
      const [fam, wt, px, ls] = type;
      g.fillStyle = c; g.font = `${wt} ${px}px ${fam}`; g.textAlign = align; g.textBaseline = 'alphabetic';
      if ('letterSpacing' in g) g.letterSpacing = `${ls}px`;
      const a0 = g.globalAlpha; g.globalAlpha = a0 * alpha;
      const w = g.measureText(s).width;
      const off = align === 'center' ? ls / 2 : align === 'right' ? ls : 0; // trailing letter-space compensation
      g.fillText(s, Math.round(x + off), Math.round(y));
      g.globalAlpha = a0;
      if ('letterSpacing' in g) g.letterSpacing = '0px';
      return w - ls;
    },
    measure(s, type) { const [fam, wt, px, ls] = type; g.font = `${wt} ${px}px ${fam}`; if ('letterSpacing' in g) g.letterSpacing = `${ls}px`; const w = g.measureText(s).width; if ('letterSpacing' in g) g.letterSpacing = '0px'; return w - ls; },
    label(s, x, y, c = C.text2, align = 'left') { return d.text(s.toUpperCase(), x, y, TYPE.label, c, align); },
    line(pts, w, c, alpha = 1) { const a0 = g.globalAlpha; g.globalAlpha = a0 * alpha; g.strokeStyle = c; g.lineWidth = w; g.lineCap = 'round'; g.lineJoin = 'round'; g.beginPath(); pts.forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.stroke(); g.globalAlpha = a0; },
    dot(x, y, r, c, alpha = 1) { const a0 = g.globalAlpha; g.globalAlpha = a0 * alpha; g.fillStyle = c; g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fill(); g.globalAlpha = a0; },
    backdrop(name = 'deep') { if (!wall) wall = bakeWallpaper(WALLPAPERS[name]); g.putImageData(wall, 0, 0); },
    render(id, t, data = demoData(t)) {
      g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.setLineDash([]);
      d.backdrop();
      (DRAW[id] || DRAW.ride)(d, t, data, id);
      if (id === 'lap') DRAW.lapOverlay(d, t, data);
      softkeys(d, SOFTKEYS[id] || SOFTKEYS.ride, PRIMARY[id] ?? 2, t, id === 'map' ? 'map' : 'key');
      quantise565(g);
      return canvas;
    },
  };
  return d;
}
// the panel is RGB565: truncate every pixel like the LVGL blender does (no dither at runtime)
function quantise565(g) {
  const im = g.getImageData(0, 0, W, H), p = im.data;
  for (let i = 0; i < p.length; i += 4) {
    const r = p[i] & 0xF8, gg = p[i + 1] & 0xFC, b = p[i + 2] & 0xF8;
    p[i] = r | (r >> 5); p[i + 1] = gg | (gg >> 6); p[i + 2] = b | (b >> 5); p[i + 3] = 255;
  }
  g.putImageData(im, 0, 0);
}

// ---------------------------------------------------------------- demo ride data (deterministic)
export function demoData(t) {
  const n = (a, f, p = 0) => a * Math.sin(t * f + p);
  const secs = 5902 + Math.floor(t);
  return {
    clock: '7:42', battery: 82, sats: 14,
    speed: 21.7 + n(0.9, 0.7) + n(0.3, 2.3), avgSpeed: 18.9,
    power: Math.round(252 + n(20, 1.1) + n(8, 3.7)), ftp: 265,
    hr: Math.round(152 + n(3, 0.23)), hrMax: 188,
    cad: Math.round(91 + n(3, 0.9)), grade: 4.2 + n(0.6, 0.3),
    dist: 31.4 + t * 0.006, elapsed: secs,
  };
}

// ---------------------------------------------------------------- icons (firmware: A8 bitmaps, recoloured)
function icon(d, kind, x, y, s, col) {
  const g = d.g; g.save(); g.translate(x, y); g.scale(s / 20, s / 20);
  g.fillStyle = g.strokeStyle = col; g.lineWidth = 2.2; g.lineCap = 'round'; g.lineJoin = 'round';
  const P = (pts, fill = true) => { g.beginPath(); pts.forEach(([a, b], i) => i ? g.lineTo(a, b) : g.moveTo(a, b)); g.closePath(); fill ? g.fill() : g.stroke(); };
  if (kind === 'heart') { g.beginPath(); g.moveTo(10, 18); g.bezierCurveTo(-3, 9, 1, -1, 10, 5); g.bezierCurveTo(19, -1, 23, 9, 10, 18); g.fill(); }
  if (kind === 'bolt') { g.lineWidth = 1.2; P([[12, 0], [3, 11], [9, 11], [7, 20], [17, 8], [11, 8], [13, 0]]); P([[12, 0], [3, 11], [9, 11], [7, 20], [17, 8], [11, 8], [13, 0]], false); }
  if (kind === 'crank') { g.beginPath(); g.arc(10, 10, 7.5, 0, 7); g.stroke(); g.beginPath(); g.moveTo(10, 10); g.lineTo(15, 16); g.stroke(); g.beginPath(); g.arc(10, 10, 2.5, 0, 7); g.fill(); }
  if (kind === 'sat') { g.beginPath(); g.arc(10, 12, 3, 0, 7); g.fill(); for (const r of [7, 11]) { g.beginPath(); g.arc(10, 12, r, -2.5, -0.64); g.stroke(); } }
  if (kind === 'phone') { g.lineWidth = 2; g.beginPath(); g.roundRect(5, 1, 10, 18, 2.5); g.stroke(); g.fillRect(8.5, 15, 3, 1.6); }
  if (kind === 'batt') { g.lineWidth = 1.8; g.beginPath(); g.roundRect(1, 5, 16, 10, 2.5); g.stroke(); g.beginPath(); g.roundRect(17.5, 8, 2, 4, 1); g.fill(); g.beginPath(); g.roundRect(3.5, 7.5, 9, 5, 1); g.fill(); }
  if (kind === 'radar') { g.beginPath(); g.arc(10, 17, 2.6, 0, 7); g.fill(); for (const r of [7.5, 13]) { g.beginPath(); g.arc(10, 17, r, -2.3, -0.84); g.stroke(); } }
  if (kind === 'route') { g.beginPath(); g.moveTo(4, 17); g.bezierCurveTo(4, 8, 16, 12, 16, 3); g.stroke(); g.beginPath(); g.arc(4, 17, 2.6, 0, 7); g.fill(); g.beginPath(); g.arc(16, 3, 2.6, 0, 7); g.fill(); }
  if (kind === 'bike') { g.lineWidth = 1.9; g.beginPath(); g.arc(4.5, 13, 4, 0, 7); g.stroke(); g.beginPath(); g.arc(15.5, 13, 4, 0, 7); g.stroke(); g.beginPath(); g.moveTo(4.5, 13); g.lineTo(8, 6); g.lineTo(14, 6); g.lineTo(15.5, 13); g.moveTo(8, 6); g.lineTo(10, 13); g.lineTo(14, 6); g.stroke(); }
  if (kind === 'chart') { for (const [a, b] of [[2, 11], [8, 6], [14, 2]]) { g.beginPath(); g.roundRect(a, b, 4, 18 - b, 1.5); g.fill(); } }
  if (kind === 'sun') { g.beginPath(); g.arc(10, 10, 4, 0, 7); g.fill(); for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4; g.beginPath(); g.moveTo(10 + Math.cos(a) * 7, 10 + Math.sin(a) * 7); g.lineTo(10 + Math.cos(a) * 9, 10 + Math.sin(a) * 9); g.stroke(); } }
  if (kind === 'sliders') { for (const [yy, xx] of [[4, 13], [10, 6], [16, 11]]) { g.lineWidth = 1.8; g.beginPath(); g.moveTo(1, yy); g.lineTo(19, yy); g.stroke(); g.beginPath(); g.arc(xx, yy, 3, 0, 7); g.fill(); } }
  if (kind === 'flag') { g.beginPath(); g.roundRect(3, 1, 2.2, 18, 1); g.fill(); P([[5, 2], [17, 2], [14, 6.5], [17, 11], [5, 11]]); }
  if (kind === 'loc') { P([[18, 2], [2, 9], [10, 10], [11, 18]]); }
  if (kind === 'mountain') P([[0, 18], [7, 5], [11, 11], [14, 7], [20, 18]]);
  g.restore();
}

// ---------------------------------------------------------------- components

// Glass panel. LVGL: lv_obj, radius r, bg_color/bg_grad_color = recipe col, bg_grad_dir VER,
// stop opa top→bot, border 1 px (edge), plus a child with border_side TOP (hi). No blur, no shadow.
export function glass(d, x, y, w, h, r, kind = 'card', tint) {
  const k = GLASS[kind] || GLASS.card, g = d.g, col = tint || k.col;
  r = Math.min(r, h / 2, w / 2);
  const gr = g.createLinearGradient(0, y, 0, y + h);
  gr.addColorStop(0, rgba(col, k.top)); gr.addColorStop(1, rgba(col, k.bot));
  g.fillStyle = gr; g.beginPath(); g.roundRect(x, y, w, h, r); g.fill();
  if (k.edge) { g.strokeStyle = rgba(k.edgeCol || col, k.edge); g.lineWidth = 1; g.beginPath(); g.roundRect(x + 0.5, y + 0.5, w - 1, h - 1, r - 0.5); g.stroke(); }
  if (k.hi) { // top highlight: top edge and the upper half of both corner arcs
    const rr = r - 0.5, x0 = x + 0.5, x1 = x + w - 0.5, y0 = y + 0.5;
    g.strokeStyle = rgba(k.edgeCol || col, k.hi); g.lineWidth = 1; g.beginPath();
    g.arc(x0 + rr, y0 + rr, rr, Math.PI * 1.25, Math.PI * 1.5); g.lineTo(x1 - rr, y0);
    g.arc(x1 - rr, y0 + rr, rr, Math.PI * 1.5, Math.PI * 1.75); g.stroke();
  }
}

// Zone light: soft coloured light behind the glass, telling the zone without a word.
// Firmware: one 240 x 200 A8 bitmap (radial falloff, 47 KB) drawn with image_recolor = zone colour, image_opa.
function zoneLight(d, col, a = 0.24, x = 70, y = 40, r = 190) { blob(d.g, x, y, r, col, a); }

// Status bar, 22 px: clock | page dots or title | location + battery
function statusBar(d, data, id, title = '') {
  d.text(data.clock, 14, 15, [TEXT, 600, 13, 0], C.text);
  const pi = PAGES.indexOf(id === 'lap' ? 'ride' : id);
  if (title) d.text(title, W / 2, 15, [TEXT, 600, 12, 0], C.text, 'center');
  else if (pi >= 0) { // page control: 5 px dots, 5 px gap, current = 14 px capsule
    const ws = PAGES.map((_, i) => i === pi ? 14 : 5), tot = ws.reduce((a, b) => a + b, 0) + 5 * (ws.length - 1);
    let x = Math.round(W / 2 - tot / 2);
    ws.forEach((w, i) => { d.rrect(x, 8, w, 5, 2.5, i === pi ? C.text : rgba(C.text, 0.3)); x += w + 5; });
  }
  // battery: 21 x 10 rounded outline, 2 px cap, fill = level
  const bx = W - 14 - 23, by = 6;
  d.g.strokeStyle = rgba(C.text, 0.45); d.g.lineWidth = 1; d.g.beginPath(); d.g.roundRect(bx + 0.5, by + 0.5, 20, 10, 3); d.g.stroke();
  d.rrect(bx + 21.5, by + 3.5, 1.5, 4, 0.75, rgba(C.text, 0.45));
  d.rrect(bx + 2, by + 2, Math.round(17 * data.battery / 100), 7, 1.5, data.battery > 20 ? C.text : C.warn);
  d.text(`${data.battery}`, bx - 5, 15, [TEXT, 600, 11, 0], C.text2, 'right');
  const tw = d.measure(`${data.battery}`, [TEXT, 600, 11, 0]);
  icon(d, 'loc', bx - 5 - tw - 15, 5, 11, C.text);
}

// Soft keys: three glass pills (70 x 22, radius 11) centred over the physical keys (thirds of 240 px)
// at y 295. Primary = prominent near-white pill with an ink label.
export function softkeys(d, labels, primary = 2, t = 0, kind = 'key') {
  const y = S.keyY + 3, cw = W / 3;
  labels.forEach((s, i) => {
    if (!s) return;
    const cx = Math.round(cw * i + cw / 2), x = cx - S.keyW / 2, prim = i === primary;
    glass(d, x, y, S.keyW, S.keyH, R.pill, prim ? 'prominent' : kind);
    const col = prim ? C.ink : C.text;
    const glyph = s === 'PAUSE' ? 'pause' : s === 'START' ? 'play' : s === 'ZOOM OUT' ? 'minus' : s === 'ZOOM IN' ? 'plus' : s === 'CENTRE' ? 'target' : '';
    const txt = glyph === 'minus' || glyph === 'plus' ? 'Zoom' : titleCase(s);
    const tw = d.measure(txt, TYPE.key), gw = glyph ? 13 : 0, x0 = Math.round(cx - (tw + gw) / 2), cy = y + 11;
    d.text(txt, x0 + gw, cy + 4.5, TYPE.key, col);
    const g = d.g; g.fillStyle = g.strokeStyle = col; g.lineCap = 'round';
    if (glyph === 'pause') { d.rrect(x0, cy - 5, 3, 10, 1, col); d.rrect(x0 + 5, cy - 5, 3, 10, 1, col); }
    if (glyph === 'play') { g.beginPath(); g.moveTo(x0, cy - 5); g.lineTo(x0 + 8, cy); g.lineTo(x0, cy + 5); g.closePath(); g.fill(); }
    if (glyph === 'minus' || glyph === 'plus') { d.rrect(x0, cy - 1, 9, 2, 1, col); if (glyph === 'plus') d.rrect(x0 + 3.5, cy - 4.5, 2, 9, 1, col); }
    if (glyph === 'target') { g.lineWidth = 1.6; g.beginPath(); g.arc(x0 + 4.5, cy, 4, 0, 7); g.stroke(); d.dot(x0 + 4.5, cy, 1.6, col); }
  });
}

// Field: glass tile, UPPERCASE label top-left, value bottom-left in TYPE.md (unit after in body/text3).
// An optional colour dot before the label carries meaning (zone), the value itself stays white.
function field(d, x, y, w, h, label, value, unit, { dot, type = TYPE.md, valueCol = C.text, extra, kind = 'field' } = {}) {
  glass(d, x, y, w, h, R.field, kind);
  let lx = x + S.pad;
  if (dot) { d.dot(lx + 3, y + 10, 3, dot); lx += 10; }
  d.label(label, lx, y + 14);
  const by = y + h - 8;
  const vw = d.text(value, x + S.pad - 1, by, type, valueCol);
  if (unit) d.text(unit, x + S.pad + vw + 3, by, TYPE.body, C.text3);
  if (extra) extra(x, y, w, h);
}

// Zone chip: coloured dot + "Z4 Threshold" in the zone colour, right- or left-aligned
function zoneChip(d, x, y, n, name, col, align = 'right') {
  const s = `${n} ${name}`, w = d.measure(s, TYPE.label.map((v, i) => i === 3 ? 0.2 : v));
  const x0 = align === 'right' ? x - w : x + 10;
  d.dot(x0 - 7, y - 4, 3, col);
  d.text(s, x0, y, [TEXT, 600, 11, 0.2], col);
}

// Gauge: a row of capsule segments (one lv_obj each, radius = h/2, 2 px apart). The active segment is
// at full opacity, the others at 40 %. The marker is a white knob with a 2 px ink ring (lv_obj, circle).
function gauge(d, x, y, w, { min, max, value, bands, h = 6, window, knob = true }) {
  const X = (v) => x + (w * (clamp(v, min, max) - min)) / (max - min);
  let active = -1;
  bands.forEach(([a, b, col], i) => {
    const on = value >= a && value < b; if (on) active = i;
    const x0 = Math.round(X(a)) + (i ? 1 : 0), x1 = Math.round(X(b)) - (i < bands.length - 1 ? 1 : 0);
    d.rrect(x0, y, Math.max(h, x1 - x0), h, h / 2, rgba(col, on || (window && col === window[2]) ? 1 : 0.4));
  });
  if (window) { // target window: 1.5 px white outline capsule around the range
    const x0 = Math.round(X(window[0])) - 2, x1 = Math.round(X(window[1])) + 2, g = d.g;
    g.strokeStyle = rgba(C.text, 0.85); g.lineWidth = 1.5; g.beginPath(); g.roundRect(x0 + 0.5, y - 2.5, x1 - x0 - 1, h + 5, (h + 5) / 2); g.stroke();
  }
  if (knob) { const nx = X(value); d.dot(nx, y + h / 2, h / 2 + 4, rgba(C.ink, 0.7)); d.dot(nx, y + h / 2, h / 2 + 2.5, C.text); }
  return active;
}

// Ring: lv_arc, round caps, neutral track (white at 12 %: a tinted track goes muddy over the dark backdrop)
function ring(d, cx, cy, r, wdt, frac, col) {
  const g = d.g; g.lineCap = 'round'; g.lineWidth = wdt;
  g.strokeStyle = rgba(C.text, 0.12); g.beginPath(); g.arc(cx, cy, r, 0, Math.PI * 2); g.stroke();
  if (frac > 0.002) { g.strokeStyle = col; g.beginPath(); g.arc(cx, cy, r, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * frac); g.stroke(); }
  g.lineCap = 'butt';
}

// Chip: small capsule with a tinted fill (colour at 22 %) and a coloured label — PRs, category, deltas
function chip(d, x, y, s, col, { align = 'left', ic, h = 18 } = {}) {
  const tw = d.measure(s, [TEXT, 600, 11, 0]), iw = ic ? 14 : 0, w = tw + iw + 16;
  const x0 = align === 'right' ? x - w : x;
  d.rrect(x0, y, w, h, h / 2, rgba(col, 0.22));
  if (ic) icon(d, ic, x0 + 8, y + h / 2 - 5.5, 11, col);
  d.text(s, x0 + 8 + iw, y + h / 2 + 4, [TEXT, 600, 11, 0], col);
  return w;
}

// Hero value: integer part in TYPE.hero, decimal part in TYPE.heroDec on the same baseline.
function hero(d, v, decimals, x, by, col = C.text) {
  const s = v.toFixed(decimals), [ip, dp] = s.split('.');
  const wi = d.text(ip, x, by, TYPE.hero, col);
  let w = wi;
  if (dp) w += 1 + d.text('.' + dp, x + wi + 1, by, TYPE.heroDec, col);
  return w;
}

function beat(d, x, y, t, bpm, col, s = 12) {
  const ph = (t * bpm / 60) % 1, k = Math.exp(-ph * 7);
  const sz = s * (1 + 0.14 * k);
  d.g.globalAlpha = 0.6 + 0.4 * k; icon(d, 'heart', x + (s - sz) / 2, y + (s - sz) / 2, sz, col); d.g.globalAlpha = 1;
}

// ---------------------------------------------------------------- screens
const DRAW = {};
const M = S.margin, CW = W - 2 * M;                  // content x 8..232
const HALF = (CW - S.gutter) / 2;                    // 109 px two-up tile

DRAW.ride = (d, t, data, id = 'ride') => {
  const pz = powerZone(data.power, data.ftp), zc = ZONES[pz];
  zoneLight(d, zc);
  statusBar(d, data, id);
  // speed card 8,26 224x98
  glass(d, M, 26, CW, 92, R.card);
  d.label('Speed', M + S.pad, 43);
  const up = data.speed >= data.avgSpeed;
  const avg = `avg ${data.avgSpeed}`, aw = d.measure(avg, TYPE.body);
  d.text(avg, W - M - S.pad, 43, TYPE.body, C.text2, 'right');
  d.text(up ? '↑' : '↓', W - M - S.pad - aw - 3, 43, TYPE.body, up ? C.good : C.warn, 'right');
  const hw = hero(d, data.speed, 1, M + S.pad - 3, 107);
  d.text('mph', M + S.pad + hw + 2, 107, TYPE.body, C.text3);
  // power card 8,124 224x62: label + zone, value + %FTP, 7-zone gauge
  const f = data.ftp;
  glass(d, M, 124, CW, 62, R.card);
  d.label('Power 3s', M + S.pad, 140);
  zoneChip(d, W - M - S.pad, 140, POWER_ZONES[pz].n, POWER_ZONES[pz].name, zc);
  const pw = d.text(String(data.power), M + S.pad - 1, 167, TYPE.lg);
  d.text('W', M + S.pad + pw + 3, 167, TYPE.body, C.text3);
  d.text(`${Math.round(data.power / f * 100)}% FTP`, W - M - S.pad, 167, TYPE.body, C.text2, 'right');
  gauge(d, M + S.pad, 174, CW - 2 * S.pad, { min: 0, max: f * 1.6, value: data.power, h: 5,
    bands: POWER_ZONES.map((z, i) => [z.lo * f, Math.min(z.hi, 1.6) * f + (i === 6 ? 1 : 0), ZONES[i]]) });
  // 2 x 2 fields, 109 x 46, 6 px gutter: y 192 and 242 (bottom 288, 7 px above the keys)
  const hz = hrZone(data.hr, data.hrMax), x2 = M + HALF + S.gutter;
  field(d, M, 192, HALF, 46, 'Heart', String(data.hr), 'bpm', { dot: HR_COL[hz] });
  field(d, x2, 192, HALF, 46, 'Cadence', String(data.cad), 'rpm');
  field(d, M, 242, HALF, 46, 'Distance', data.dist.toFixed(1), 'mi');
  field(d, x2, 242, HALF, 46, 'Time', fmtTime(data.elapsed), '');
};

DRAW.hr = (d, t, data) => {
  const hz = hrZone(data.hr, data.hrMax), col = HR_COL[hz];
  zoneLight(d, col);
  statusBar(d, data, 'hr');
  glass(d, M, 26, CW, 112, R.card);
  d.label('Heart rate', M + S.pad, 44);
  zoneChip(d, W - M - S.pad, 44, HR_ZONES[hz].n, HR_ZONES[hz].name, col);
  const hw = hero(d, data.hr, 0, M + S.pad - 3, 112);
  d.text('bpm', M + S.pad + hw + 2, 112, TYPE.body, C.text3);
  beat(d, W - M - S.pad - 24, 66, t, data.hr, col, 24);
  const m = data.hrMax;
  gauge(d, M + S.pad, 122, CW - 2 * S.pad, { min: 0.5 * m, max: m, value: data.hr, h: 5,
    bands: HR_ZONES.map((z, i) => [z.lo * m, z.hi * m + (i === 4 ? 1 : 0), HR_COL[i]]) });
  // time in zone: 5 rows x 16 px
  glass(d, M, 144, CW, 94, R.card);
  d.label('Time in zone', M + S.pad, 161);
  const tiz = [412, 2210, 2485, 1175, 214 + Math.floor(t)], tot = tiz.reduce((a, b) => a + b, 0), mx = Math.max(...tiz);
  tiz.forEach((s, i) => {
    const y = 168 + i * 14, cur = i === hz, bw = 110;
    d.text(HR_ZONES[i].n, M + S.pad, y + 9, [TEXT, 600, 10, 0], cur ? C.text : C.text3);
    d.rrect(42, y + 3, bw, 6, 3, rgba(C.text, 0.08));
    d.rrect(42, y + 3, Math.max(6, Math.round(bw * s / mx)), 6, 3, rgba(HR_COL[i], cur ? 1 : 0.55));
    d.text(fmtTime(s), 196, y + 9, [TEXT, 600, 10, 0], cur ? C.text : C.text2, 'right');
    d.text(`${Math.round(s / tot * 100)}%`, W - M - S.pad, y + 9, [TEXT, 500, 10, 0], C.text3, 'right');
  });
  field(d, M, 244, HALF, 44, 'Avg', '141', 'bpm');
  field(d, M + HALF + S.gutter, 244, HALF, 44, 'Max', '171', 'bpm');
};

DRAW.climb = (d, t, data) => {
  const g = d.g;
  const prog = 0.18 + (t * 0.02) % 0.7;
  const n = 30, grades = Array.from({ length: n }, (_, i) => 3.2 + 4.8 * Math.abs(Math.sin(i * 0.33 + 0.6)) + (i > 19 ? 3.2 : 0) + (i > 26 ? 2 : 0));
  const fi = prog * n, i0 = Math.floor(fi);
  const gr = grades[Math.min(n - 1, i0)];
  zoneLight(d, gradeColor(gr), 0.22);
  statusBar(d, data, 'climb');
  // title row
  d.text('Hawk Hill', M + 4, 45, [TEXT, 600, 17, 0], C.text);
  chip(d, W - M, 31, 'Cat 3', C.z5, { align: 'right' });
  d.text('Climb 2 of 3', W - M - 60, 44, TYPE.body, C.text2, 'right');
  // three tiles 70/71/71 x 52
  const fy = 54, fh = 52, fw = [70, 71, 71];
  const tt = [DISP, 600, 21, -0.3];
  field(d, M, fy, fw[0], fh, 'Grade', gr.toFixed(1), '%', { dot: gradeColor(gr), type: tt });
  field(d, M + 76, fy, fw[1], fh, 'To top', (1.62 * (1 - prog)).toFixed(2), 'mi', { type: tt });
  field(d, M + 153, fy, fw[2], fh, 'Gain', String(Math.round(612 * (1 - prog))), 'ft', { type: tt });
  // profile card 8,112 224x176
  glass(d, M, 112, CW, 176, R.card);
  d.label('Profile', M + S.pad, 129);
  d.text(`${Math.round(612 * (1 - prog))} ft to go`, W - M - S.pad, 129, TYPE.body, C.text2, 'right');
  const px0 = 20, px1 = 220, base = 256, top = 162;
  let e = 0; const el = [0]; grades.forEach((q2) => { e += q2; el.push(e); });
  const X = (i) => px0 + (px1 - px0) * i / n, Y = (v) => base - (base - top) * v / e;
  for (let k = 1; k <= 3; k++) d.rect(px0, Math.round(base - (base - top) * k / 4), px1 - px0, 1, rgba(C.text, 0.06));
  for (let i = 0; i < n; i++) {
    const c = gradeColor(grades[i]), done = i < i0;
    const yA = Y(el[i]), yB = Y(el[i + 1]);
    const gd = g.createLinearGradient(0, Math.min(yA, yB), 0, base);
    gd.addColorStop(0, rgba(done ? C.text3 : c, done ? 0.45 : 0.85)); gd.addColorStop(1, rgba(done ? C.text3 : c, done ? 0.08 : 0.18));
    g.fillStyle = gd; g.beginPath(); g.moveTo(X(i), base); g.lineTo(X(i), yA); g.lineTo(X(i + 1), yB); g.lineTo(X(i + 1), base); g.closePath(); g.fill();
    d.line([[X(i), yA], [X(i + 1), yB]], 2, done ? C.text3 : c);
  }
  icon(d, 'flag', px1 - 8, top - 22, 14, C.text);
  d.rect(px0, base, px1 - px0, 1, rgba(C.text, 0.25));
  ['0', '0.4', '0.8', '1.2', '1.6 mi'].forEach((s, k) => d.text(s, px0 + (px1 - px0) * k / 4, base + 16, TYPE.caption, C.text3, k === 0 ? 'left' : k === 4 ? 'right' : 'center'));
  // rider: white dot with an accent ring and a hairline drop to the axis
  const mx = X(fi), my = Y(el[i0] + (el[Math.min(n, i0 + 1)] - el[i0]) * (fi - i0));
  d.rect(Math.round(mx), my, 1, base - my, rgba(C.text, 0.5));
  d.dot(mx, my, 7.5, C.accent); d.dot(mx, my, 4.5, C.text);
};

// ---- map
const STREETS = [];
for (let i = -7; i <= 7; i++) { STREETS.push([[i * 90, -1000], [i * 90, 1000]]); STREETS.push([[-1000, i * 110 + 20], [1000, i * 110 + 20]]); }
const MAJOR = [[[-1000, -500], [1000, 300]], [[-270, -1000], [-270, 1000]]];
const ROUTE = [[0, -900], [0, 130], [180, 130], [180, 900]];
const PARKS = [[[100, -420], [260, -420], [260, -250], [100, -250]], [[-330, 250], [-110, 250], [-110, 480], [-330, 480]], [[370, 360], [520, 360], [520, 580], [370, 580]]];
const RIVER = [[-1000, -700], [-400, -650], [-150, -760], [300, -690], [1000, -760], [1000, -1000], [-1000, -1000]];
function routePos(s) {
  for (let i = 0; i < ROUTE.length - 1; i++) {
    const [ax, ay] = ROUTE[i], [bx, by] = ROUTE[i + 1]; const L = Math.hypot(bx - ax, by - ay);
    if (s <= L) return { x: ax + (bx - ax) * s / L, y: ay + (by - ay) * s / L, h: Math.atan2(bx - ax, by - ay), seg: i, left: L - s, s };
    s -= L;
  }
  return { x: 180, y: 900, h: 0, seg: 2, left: 0, s };
}
DRAW.map = (d, t, data) => {
  const g = d.g;
  const s = 830 + ((t * 38) % 190);
  const p = routePos(s);
  const zoom = 1 + 0.15 * Math.sin(t * 0.35);
  const k = 0.5 * zoom, cx = W / 2, cy = 200;
  const tf = (x, y) => { const dx = x - p.x, dy = y - p.y; const c = Math.cos(p.h), sn = Math.sin(p.h); return [cx + (dx * c - dy * sn) * k, cy - (dx * sn + dy * c) * k]; };
  const poly = (pts, col) => { g.fillStyle = col; g.beginPath(); pts.forEach(([x, y], i) => { const [u, v] = tf(x, y); i ? g.lineTo(u, v) : g.moveTo(u, v); }); g.closePath(); g.fill(); };
  const path = (pts, wdt, col, a = 1, cap = 'round') => { g.globalAlpha = a; g.strokeStyle = col; g.lineWidth = wdt; g.lineCap = cap; g.lineJoin = 'round'; g.beginPath(); pts.forEach(([x, y], i) => { const [u, v] = tf(x, y); i ? g.lineTo(u, v) : g.moveTo(u, v); }); g.stroke(); g.globalAlpha = 1; };
  d.rect(0, 0, W, H, C.mapBg);
  poly(RIVER, C.water); for (const pk of PARKS) poly(pk, C.park);
  for (const st of STREETS) path(st, 6 * zoom, C.road, 1, 'butt');
  for (const st of MAJOR) path(st, 10 * zoom, C.roadMajor, 1, 'butt');
  // route: travelled part grey; ahead = accent with a darker 2 px edge (two stroked lines, no glow)
  const done = [], ahead = []; let acc = 0;
  for (let i = 0; i < ROUTE.length - 1; i++) {
    const [ax, ay] = ROUTE[i], [bx, by] = ROUTE[i + 1], L = Math.hypot(bx - ax, by - ay);
    if (acc + L <= s) { done.push(ROUTE[i]); } else if (acc >= s) { ahead.push(ROUTE[i]); } else { done.push(ROUTE[i]); done.push([p.x, p.y]); ahead.push([p.x, p.y]); }
    acc += L;
  }
  ahead.push(ROUTE[ROUTE.length - 1]);
  path(done, 6, C.routeDone);
  path(ahead, 10, C.routeEdge); path(ahead, 6, C.accent);
  // turn point
  const turn = p.seg === 0 ? ROUTE[1] : ROUTE[2];
  const [tx, ty] = tf(turn[0], turn[1]);
  d.dot(tx, ty, 6, C.text); d.dot(tx, ty, 3.5, C.accent);
  // rider: heading cone + white-ringed accent dot (Apple-style location puck)
  const cone = g.createLinearGradient(0, cy - 34, 0, cy);
  cone.addColorStop(0, rgba(C.accent, 0)); cone.addColorStop(1, rgba(C.accent, 0.45));
  g.fillStyle = cone; g.beginPath(); g.moveTo(cx, cy); g.arc(cx, cy, 34, -Math.PI / 2 - 0.45, -Math.PI / 2 + 0.45); g.closePath(); g.fill();
  d.dot(cx, cy, 10, rgba(C.ink, 0.35)); d.dot(cx, cy, 9, C.text); d.dot(cx, cy, 6.5, C.accent);
  // turn card 8,8 224x70 (map glass: translucent fill, no blur)
  const next = p.seg === 0 ? { dist: p.left, dir: 'right', road: 'Grand St' } : p.seg === 1 ? { dist: p.left, dir: 'left', road: 'Jersey Ave' } : { dist: 0, dir: 'straight', road: 'Jersey Ave' };
  const feet = Math.max(0, Math.round(next.dist * 3.28 / 10) * 10);
  glass(d, M, M, CW, 70, 20, 'map');
  d.rrect(M + 8, M + 8, 54, 54, 14, C.accent);
  g.strokeStyle = g.fillStyle = C.text; g.lineWidth = 5; g.lineCap = 'round'; g.lineJoin = 'round';
  const ax = M + 35, ay = M + 52;
  g.beginPath(); g.moveTo(ax, ay); g.lineTo(ax, 38);
  if (next.dir === 'right') { g.arcTo(ax, 30, ax + 8, 30, 8); g.lineTo(ax + 11, 30); g.stroke(); g.beginPath(); g.moveTo(ax + 10, 22); g.lineTo(ax + 19, 30); g.lineTo(ax + 10, 38); g.closePath(); g.fill(); }
  else if (next.dir === 'left') { g.arcTo(ax, 30, ax - 8, 30, 8); g.lineTo(ax - 11, 30); g.stroke(); g.beginPath(); g.moveTo(ax - 10, 22); g.lineTo(ax - 19, 30); g.lineTo(ax - 10, 38); g.closePath(); g.fill(); }
  else { g.lineTo(ax, 28); g.stroke(); g.beginPath(); g.moveTo(ax - 8, 30); g.lineTo(ax, 20); g.lineTo(ax + 8, 30); g.closePath(); g.fill(); }
  g.lineCap = 'butt'; g.lineJoin = 'miter';
  const big = feet >= 1000;
  const fw = d.text(big ? (feet / 5280).toFixed(1) : String(feet), M + 72, M + 36, TYPE.lg, C.text);
  d.text(big ? 'mi' : 'ft', M + 75 + fw, M + 36, TYPE.body, C.text2);
  d.text(data.clock, W - M - 12, M + 20, [TEXT, 600, 11, 0], C.text3, 'right');
  const turnTxt = `${next.dir === 'straight' ? 'Continue on' : next.dir === 'right' ? 'Right onto' : 'Left onto'} `;
  const t1 = d.text(turnTxt, M + 72, M + 56, TYPE.body, C.text2);
  d.text(next.road, M + 72 + t1 + 1, M + 56, [TEXT, 600, 13, 0], C.text);
  // compass 212,100 (heading-up map: red N needle rotated by -heading)
  const nx = W - M - 16, ny = 102;
  glass(d, nx - 16, ny - 16, 32, 32, 16, 'map');
  g.save(); g.translate(nx, ny); g.rotate(-p.h); g.fillStyle = C.bad; g.beginPath(); g.moveTo(0, -13); g.lineTo(3.5, -8); g.lineTo(-3.5, -8); g.closePath(); g.fill(); g.restore();
  d.text('N', nx, ny + 4, [TEXT, 600, 11, 0], C.text, 'center');
  // bottom tiles 8,242 and 124,242 (108 x 46)
  const by = 242;
  glass(d, M, by, 108, 46, R.field, 'map');
  d.label('Speed', M + S.pad, by + 15);
  const sw = d.text(data.speed.toFixed(1), M + S.pad - 1, by + 37, TYPE.md, C.text);
  d.text('mph', M + S.pad + sw + 3, by + 37, TYPE.body, C.text3);
  glass(d, W - M - 108, by, 108, 46, R.field, 'map');
  d.label('Arrive 8:21', W - M - 108 + S.pad, by + 15, C.accent);
  const dw = d.text('12.4', W - M - 108 + S.pad - 1, by + 37, TYPE.md, C.text);
  d.text('mi', W - M - 108 + S.pad + dw + 3, by + 37, TYPE.body, C.text3);
  // scale bar, top-left under the turn card
  const sb = 30;
  d.rrect(M + 6, 100, sb, 2, 1, rgba(C.text, 0.8)); d.rrect(M + 6, 96, 2, 6, 1, rgba(C.text, 0.8)); d.rrect(M + 4 + sb, 96, 2, 6, 1, rgba(C.text, 0.8));
  d.text(`${Math.round(240 / zoom / 10) * 10} ft`, M + 12 + sb, 104, TYPE.caption, C.text, 'left');
};

DRAW.workout = (d, t, data) => {
  const len = 600, rem = len - ((t * 4 + 198) % len);
  const lo = 240, hi = 262, pw = Math.round(data.power - 2);
  const on = pw >= lo && pw <= hi, tc = C.z4;
  zoneLight(d, tc, 0.12, 120, 110, 170);
  statusBar(d, data, 'workout');
  // header: step and next
  d.label('Step 4 of 7', M + 4, 40);
  d.text('Sweet spot', M + 4, 57, TYPE.title, C.text);
  d.label('Next', W - M - 4, 40, C.text2, 'right');
  d.text('Rest 5:00', W - M - 4, 57, TYPE.title, C.text2, 'right');
  // ring: interval progress
  const cx = 120, cy = 116, r = 50;
  ring(d, cx, cy, r, 10, 1 - rem / len, tc);
  d.text('Interval 2/3', cx, cy - 19, [TEXT, 600, 10, 0], C.text2, 'center');
  d.text(fmtTime(rem), cx, cy + 12, TYPE.timer, C.text, 'center');
  d.text(`of ${fmtTime(len)}`, cx, cy + 28, [TEXT, 500, 10, 0], C.text3, 'center');
  // target card 8,176 224x70: label + status chip, power + heart, target gauge
  glass(d, M, 176, CW, 70, R.card);
  d.label(`Target ${lo}–${hi} W`, M + S.pad, 193);
  chip(d, W - M - S.pad + 4, 181, on ? 'On target' : pw < lo ? `Push +${lo - pw}` : `Ease −${pw - hi}`, on ? C.good : C.warn, { align: 'right' });
  const vw = d.text(String(pw), M + S.pad - 1, 222, TYPE.lg);
  d.text('W', M + S.pad + vw + 3, 222, TYPE.body, C.text3);
  const hr = data.hr + 4, hz = hrZone(hr, data.hrMax);
  const bw2 = d.measure('bpm', [TEXT, 500, 11, 0]);
  d.text('bpm', W - M - S.pad, 222, [TEXT, 500, 11, 0], C.text3, 'right');
  const hw2 = d.text(String(hr), W - M - S.pad - bw2 - 3, 222, TYPE.md, C.text, 'right');
  beat(d, W - M - S.pad - bw2 - hw2 - 20, 205, t, hr, HR_COL[hz], 14);
  gauge(d, M + S.pad, 231, CW - 2 * S.pad, { min: 180, max: 320, value: pw, h: 5, window: [lo, hi, tc],
    bands: [[180, lo, C.text3], [lo, hi, tc], [hi, 321, C.text3]] });
  // session card 8,252 224x36: step blocks, height = intensity
  glass(d, M, 252, CW, 36, R.field);
  const steps = [[300, 0.45, C.z2], [600, 0.92, C.z4], [300, 0.5, C.z2], [600, 0.92, C.z4], [300, 0.5, C.z2], [600, 0.92, C.z4], [300, 0.4, C.z1]];
  const tot = steps.reduce((a, [s2]) => a + s2, 0), cx0 = M + 10, cw = CW - 20, cb = 281, ch = 20;
  const at = 300 + 600 + 300 + (len - rem);
  let x = cx0, acc = 0;
  steps.forEach(([s2, h, c]) => {
    const w = cw * s2 / tot, hh = Math.round(ch * h);
    const past = acc + s2 <= at, cur = acc <= at && at < acc + s2;
    d.rrect(Math.round(x), cb - hh, Math.round(w) - 2, hh, 3, past ? rgba(C.text, 0.16) : rgba(c, cur ? 1 : 0.7));
    x += w; acc += s2;
  });
  const mx = Math.round(cx0 + cw * at / tot);
  d.rrect(mx - 1, cb - ch - 3, 2, ch + 3, 1, C.text);
};

DRAW.status = (d, t, data) => {
  statusBar(d, data, 'status');
  const rows = [
    ['heart', C.z6, 'Heart rate', 'Polar H10 · ANT+', `${data.hr}`, 4],
    ['bolt', C.z4, 'Power', 'Assioma Duo · ANT+', `${data.power} W`, 3],
    ['radar', C.z5, 'Radar', 'Varia RTL515 · ANT+', 'Clear', 4],
    ['sat', C.z3, 'GPS', '3D fix · 3 systems', `${data.sats}`, 4],
    ['phone', C.accent, 'Phone', 'OpenCycle app · BLE', 'Linked', 2],
    ['batt', C.good, 'Battery', `About ${Math.round(data.battery / 100 * 20)} h left`, `${data.battery}%`, -1],
  ];
  // one grouped glass list 8,28 224x260, rows 43 px, hairlines inset to the text column
  const y0 = 28, rh = 43;
  glass(d, M, y0, CW, rh * rows.length + 2, R.card);
  rows.forEach(([ic, col, name, sub, val, bars], i) => {
    const y = y0 + 1 + i * rh;
    if (i) d.rect(52, y, W - M - 52, 1, rgba(C.text, 0.08));
    d.rrect(M + 10, y + 8, 28, 28, R.tile, col);
    icon(d, ic, M + 16, y + 14, 16, ic === 'bolt' || ic === 'batt' ? C.ink : C.text);
    d.text(name, 52, y + 20, TYPE.title, C.text);
    d.text(sub, 52, y + 35, [TEXT, 500, 11, 0], C.text2);
    d.text(val, 202, y + 21, [TEXT, 600, 13, 0], C.text, 'right');
    if (bars >= 0) for (let b = 0; b < 4; b++) d.rrect(208 + b * 5, y + 21 - 4 - b * 3, 3, 4 + b * 3, 1, b < bars ? C.text : rgba(C.text, 0.2));
    else { d.rrect(208, y + 12, 18, 9, 2, rgba(C.text, 0.2)); d.rrect(208, y + 12, Math.round(18 * data.battery / 100), 9, 2, C.good); }
  });
};

DRAW.lap = (d, t, data) => DRAW.ride(d, t, data, 'ride');
DRAW.lapOverlay = (d, t) => {
  // timeline (s): 0 → 0.35 slide in (settle, no bounce), hold, 4.4 → 4.75 slide out; loops every 6 s
  const ph = t % 6, hgt = 184;
  const k = ph < 0.35 ? EASE.settle(ph / 0.35) : ph < 4.4 ? 1 : 1 - EASE.inOut((ph - 4.4) / 0.35);
  if (k <= 0.001) return;
  const y = Math.round(lerp(-hgt - 10, 26, k)), g = d.g;
  // dim the ride page (lv_obj full-screen, bg ink, opa 45 %) — not blur
  d.rect(0, 0, W, H - BAR, rgba(C.deep, 0.5 * k));
  // sheet: dark glass (opaque enough to read over anything) with a soft pre-rendered shadow
  g.save(); g.shadowColor = rgba('#000000', 0.45); g.shadowBlur = 18; g.shadowOffsetY = 6;
  d.rrect(M, y, CW, hgt, 22, rgba(C.night, 0.01)); g.restore();
  glass(d, M, y, CW, hgt, 22, 'sheet');
  glass(d, M, y, CW, hgt, 22, 'card');
  // header
  chip(d, M + S.pad, y + 12, 'Lap 4', C.accent, { ic: 'flag' });
  d.text('vs lap 3', W - M - S.pad, y + 25, TYPE.body, C.text2, 'right');
  // lap time + delta
  const tw = d.text('8:12', M + S.pad - 2, y + 86, TYPE.xl, C.text);
  d.text('.4', M + S.pad + tw, y + 86, TYPE.lg, C.text2);
  d.text('faster', W - M - S.pad, y + 64, [TEXT, 600, 11, 0], C.good, 'right');
  d.text('−0:14', W - M - S.pad, y + 84, TYPE.sm, C.good, 'right');
  // stats row: three columns, hairline dividers
  d.rect(M + S.pad, y + 100, CW - 2 * S.pad, 1, rgba(C.text, 0.1));
  const stats = [['Speed', '20.8', '+0.6', C.good], ['Power', '247', '+9', C.good], ['Heart', '151', '+4', C.warn]];
  stats.forEach(([l, v, dl, c], i) => {
    const x = M + S.pad + i * 72;
    if (i) d.rect(x - 7, y + 110, 1, 40, rgba(C.text, 0.1));
    d.label(l, x, y + 122);
    const vw = d.text(v, x, y + 146, TYPE.sm, C.text);
    d.text(dl, x + vw + 3, y + 146, [TEXT, 600, 10, 0], c);
  });
  // auto-dismiss timer: capsule shrinking over the hold
  const hold = clamp((ph - 0.35) / 4.05, 0, 1), bw = CW - 2 * S.pad;
  d.rrect(M + S.pad, y + hgt - 16, bw, 4, 2, rgba(C.text, 0.12));
  d.rrect(M + S.pad, y + hgt - 16, Math.max(4, Math.round(bw * (1 - hold))), 4, 2, rgba(C.text, 0.7));
};

DRAW.summary = (d, t, data) => {
  const g = d.g;
  statusBar(d, data, 'summary', 'Ride complete');
  d.text('Sat 27 Sep · Hudson loop', M + 4, 42, TYPE.body, C.text2);
  // hero distance
  const dw = d.text('48.2', M + 2, 94, TYPE.xl, C.text);
  d.text('mi', M + 6 + dw, 94, TYPE.title, C.text3);
  chip(d, W - M - 4, 62, '3 PRs', C.z4, { align: 'right', ic: 'flag' });
  // elevation card 8,106 224x70; trace draws left→right over the first 1.5 s of each 6 s loop
  const ex0 = M, ew = CW, ey = 106, eh = 70;
  glass(d, ex0, ey, ew, eh, R.card);
  d.label('Elevation', ex0 + S.pad, ey + 17);
  d.text('3,412 ft', ex0 + ew - S.pad, ey + 17, [TEXT, 600, 11, 0], C.text, 'right');
  const px0 = ex0 + S.pad, pw = ew - 2 * S.pad, pb = ey + eh - 8, ph = 36;
  const pts = Array.from({ length: 61 }, (_, i) => { const u = i / 60; return [px0 + pw * u, pb - ph * (0.12 + 0.35 * Math.sin(u * 5.2 + 0.4) ** 2 + 0.45 * Math.exp(-((u - 0.62) ** 2) / 0.006) + 0.05 * Math.sin(u * 40))]; });
  const rev = clamp(EASE.inOut((t % 6) / 1.5), 0, 1);
  g.save(); g.beginPath(); g.rect(px0 - 2, ey, pw * rev + 4, eh); g.clip();
  const gd = g.createLinearGradient(0, pb - ph, 0, pb); gd.addColorStop(0, rgba(C.accent, 0.6)); gd.addColorStop(1, rgba(C.accent, 0.04));
  g.fillStyle = gd; g.beginPath(); g.moveTo(px0, pb); pts.forEach(([x, y]) => g.lineTo(x, y)); g.lineTo(px0 + pw, pb); g.closePath(); g.fill();
  d.line(pts, 2, C.accent);
  g.restore();
  // 3 x 2 stat grid: 70/71/71 x 50 tiles (field component, 20 px values)
  // units live in the labels: a 71 px tile cannot take "17.9 mph" at 20 px
  const cells = [['Moving', '4:12', ''], ['Avg mph', '17.9', ''], ['Avg W', '198', ''],
    ['NP W', '231', ''], ['Avg bpm', '141', ''], ['TSS', '212', '']];
  cells.forEach(([l, v, u], i) => {
    const x = M + (i % 3) * 76 + (i % 3 ? 1 : 0), y = 182 + Math.floor(i / 3) * 56;
    field(d, x, y, i % 3 ? 71 : 70, 50, l, v, u, { type: [DISP, 600, 20, -0.3] });
  });
};

DRAW.menu = (d, t, data) => {
  statusBar(d, data, 'menu', 'Menu');
  const items = [['bike', 'Ride profiles', 'Road · 6 pages'], ['route', 'Navigate', 'Hudson loop · 48 mi'], ['chart', 'Workouts', 'Sweet spot 3×10'],
    ['radar', 'Sensors', '5 paired'], ['sun', 'Display', 'Auto · 80%'], ['sliders', 'Settings', 'v0.2 · mph']];
  // selection steps every 1.5 s and glides 220 ms
  const step = Math.floor(t / 1.5), ph = (t / 1.5) % 1;
  const cur = step % items.length, prev = (step + items.length - 1) % items.length;
  const k = EASE.out(ph * 1.5 / 0.22);
  const y0 = 28, rh = 43;
  const selY = y0 + lerp(prev === items.length - 1 && cur === 0 ? cur : prev, cur, k) * rh;
  items.forEach((_, i) => glass(d, M, y0 + i * rh, CW, rh - 5, R.row, 'field'));
  glass(d, M, selY, CW, rh - 5, R.row, 'raised');
  items.forEach(([ic, name, sub], i) => {
    const y = y0 + i * rh, sel = i === cur && k > 0.5;
    d.rrect(M + 8, y + 6, 26, 26, R.tile, sel ? C.accent : rgba(C.text, 0.12));
    icon(d, ic, M + 13, y + 11, 16, C.text);
    d.text(name, 46, y + 17, TYPE.title, C.text);
    d.text(sub, 46, y + 31, [TEXT, 500, 11, 0], C.text2);
    const g = d.g; g.strokeStyle = sel ? C.text : C.text3; g.lineWidth = 2; g.lineCap = 'round'; g.lineJoin = 'round';
    g.beginPath(); g.moveTo(217, y + 14); g.lineTo(221, y + 19); g.lineTo(217, y + 24); g.stroke(); g.lineCap = 'butt';
  });
};

DRAW.boot = (d, t) => {
  const g = d.g, ph = t % 6;
  // 0–0.8 s backdrop fades up from black; 0.5–1.3 s mark + wordmark settle; 1.2–4.6 s progress; 5.2–6 fade out
  const inA = EASE.out(ph / 0.8), out = clamp((ph - 5.2) / 0.8, 0, 1);
  d.rect(0, 0, W, H, rgba('#000000', 1 - inA * (1 - out)));
  const a = clamp((ph - 0.5) / 0.8, 0, 1) * (1 - out), rise = Math.round(10 * (1 - EASE.settle((ph - 0.5) / 0.8)));
  const cy = 132 + rise;
  g.globalAlpha = a;
  // mark: a glass disc with a white ring and one accent dot — "the cycle"
  glass(d, 120 - 34, cy - 34, 68, 68, 34, 'card');
  g.strokeStyle = C.text; g.lineWidth = 5; g.lineCap = 'round';
  g.beginPath(); g.arc(120, cy, 17, -Math.PI / 2 + 0.55, Math.PI * 1.5 - 0.1); g.stroke(); g.lineCap = 'butt';
  d.dot(120, cy - 17, 4, C.accent);
  d.text('OpenCycle', 120, cy + 70, [DISP, 600, 28, -0.5], C.text, 'center');
  g.globalAlpha = 1;
  // progress
  const pa = clamp((ph - 1.2) / 0.3, 0, 1) * (1 - out);
  const prog = EASE.inOut(clamp((ph - 1.2) / 3.4, 0, 1));
  g.globalAlpha = pa;
  d.rrect(80, 236, 80, 4, 2, rgba(C.text, 0.16));
  d.rrect(80, 236, Math.max(4, Math.round(80 * prog)), 4, 2, C.text);
  const msg = ph < 2.2 ? 'Finding satellites' : ph < 3.2 ? 'Connecting sensors' : ph < 4.4 ? 'Linking phone' : 'Ready';
  d.text(msg, 120, 260, [TEXT, 500, 11, 0], C.text2, 'center');
  g.globalAlpha = 1;
};
