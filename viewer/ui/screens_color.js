// OpenCycle device UI — "MERIDIAN" design language, reference renderer for the v0.2 colour display
// (Newhaven NHD-2.4-240320AF-CSXP, 2.4" IPS TFT, ST7789, 240 x 320 portrait, RGB565).
//
// This file is the spec the firmware (LVGL 9 on the ESP32-S3) ports 1:1. It is organised like the
// firmware theme will be:
//
//   C        palette      every colour is RGB565-exact, so the preview equals the panel
//   TYPE     type scale   two OFL families, a fixed set of sizes (each becomes one lv_font_conv font)
//   S        spacing      4 px grid, 8 px screen margin, 4 px gutter, 8 px chamfer ("notch")
//   components            statusBar, softkeys, panel (notched rect), field, rail (the Meridian tick
//                         scale), ring (round tick bezel + arc), chip, icons
//   DRAW.<id>             one function per screen, using only the components + primitives
//
// Only primitives LVGL 9 draws natively are used: filled rects, the 45-degree corner notch (rect +
// corner triangle), 1-3 px lines, arcs, 2-stop horizontal/vertical gradients, flat text, opacity.
// "Glows" are 2-3 stacked translucent strokes, never blur. See docs/UI.md.
//
// API (used by viewer/index.html — keep it stable)
//   const dev = createDevice();      // offscreen 240x320 canvas
//   dev.render(screenId, t)          // draw one full frame; t = seconds, every animation is a pure fn of t
//   dev.canvas                       // the canvas, for textures and previews
//   SOFTKEYS[screenId]               // the three key labels for that screen
//   await fontsReady()               // loads the bundled OFL fonts with the FontFace API

export const W = 240, H = 320, BAR = 28;

export const SCREENS = [
  { id: 'ride', name: 'Ride', desc: 'Speed hero over the Meridian rail: the needle reads power against your seven zones, and the whole hero glows in the current zone colour.' },
  { id: 'hr', name: 'Heart', desc: 'Heart rate hero with a live pulse, the five-zone rail, and time spent in each zone this ride.' },
  { id: 'climb', name: 'Climb', desc: 'Upcoming climb profile coloured by gradient, your position on it, and what is left to the top.' },
  { id: 'map', name: 'Navigation', desc: 'Dark heading-up map with the route as a light trace and the next turn in a notched cue card. Keys: zoom out, re-centre, zoom in.' },
  { id: 'workout', name: 'Workout', desc: 'Interval countdown inside a chronograph bezel, a target power window on the rail, and the whole session below.' },
  { id: 'status', name: 'Sensors', desc: 'Paired sensors with signal strength, GPS fix, phone link and battery.' },
  { id: 'lap', name: 'Lap alert', desc: 'Press LAP: a notched summary card drops over the ride page with deltas to the last lap, then retracts on a visible timer.' },
  { id: 'summary', name: 'Ride summary', desc: 'End-of-ride card: distance, the elevation trace, key averages and PRs. Save is the primary key.' },
  { id: 'menu', name: 'Menu', desc: 'Right side button opens it. Notched selection bar, left/right keys move, centre opens.' },
  { id: 'boot', name: 'Boot', desc: 'Power-on: the bezel ticks sweep in, the wordmark lands, sensors and GPS report in on the rail.' },
];

// Three labels per screen, left / centre / right key. PRIMARY marks which key is the accent (filled) key.
export const SOFTKEYS = {
  ride: ['LAP', 'PAGE', 'PAUSE'], lap: ['LAP', 'PAGE', 'PAUSE'], climb: ['LAP', 'PAGE', 'PAUSE'], hr: ['LAP', 'PAGE', 'PAUSE'],
  map: ['ZOOM −', 'CENTRE', 'ZOOM +'], workout: ['SKIP', 'PAGE', 'PAUSE'], status: ['SCAN', 'PAGE', 'PAIR'],
  summary: ['DISCARD', 'PAGE', 'SAVE'], menu: ['PREV', 'OPEN', 'NEXT'], boot: ['', '', ''],
};
export const PRIMARY = { ride: 2, lap: 2, climb: 2, hr: 2, workout: 2, status: 2, summary: 2, map: -1, menu: 1, boot: -1 };
// the PAGE key cycles these data pages (page dots in the status bar)
export const PAGES = ['ride', 'hr', 'climb', 'map', 'workout', 'status'];

// ---------------------------------------------------------------- palette (RGB565-exact; hex = what the panel shows)
export const C = {
  bg: '#080808',      // 0x0841  ink: screen background
  s1: '#101821',      // 0x10C4  surface: panels, cards
  s2: '#182029',      // 0x1905  raised: keycaps, overlays
  s3: '#212C39',      // 0x2167  track: empty gauge / rail track
  line: '#293039',    // 0x2987  hairlines, dividers
  dim: '#4A5563',     // 0x4AAC  minor ticks, inactive glyphs
  mute: '#8C96A5',    // 0x8CB4  labels, units
  text: '#EFF7F7',    // 0xEFBE  primary text and needles
  ion: '#39E7EF',     // 0x3F3D  signature accent: primary key, route, focus, rider
  ionDim: '#105963',  // 0x12CC  accent at rest: travelled route, key locator
  pause: '#FFB221',   // 0xFD84  paused / warning state
  // effort spectrum — seven power zones; HR uses z1..z5, gradient uses z3..z7
  z1: '#7B8E9C', z2: '#427DFF', z3: '#21D79C', z4: '#F7D329', z5: '#FF8A21', z6: '#FF3C52', z7: '#C64DFF',
  // map
  mapBg: '#081018', road: '#212831', roadMajor: '#293842', water: '#082031', park: '#102418',
};
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
// NUM = Saira Condensed (numerals), UI = Chakra Petch (labels/text). [family, weight, px, letter-space]
const NUM = '"Saira Condensed", "Arial Narrow", sans-serif';
const UI = '"Chakra Petch", "Arial", sans-serif';
export const TYPE = {
  hero: [NUM, 700, 112, 0],   // ride speed, HR hero
  dec: [NUM, 700, 56, 0],     // the decimal part of a hero value (".3"), baseline-aligned
  xl: [NUM, 700, 60, 0],      // lap time, summary distance
  timer: [NUM, 700, 50, 0],   // workout countdown inside the bezel
  lg: [NUM, 700, 38, 0],      // grid fields
  md: [NUM, 700, 30, 0],      // turn distance, secondary values
  sm: [NUM, 600, 22, 0],      // footer values, chips, list values
  xs: [NUM, 600, 17, 0],      // tiny values (status bar battery %, axis)
  title: [UI, 700, 16, 0],    // screen/section titles, list items
  body: [UI, 600, 13, 0],     // secondary text
  label: [UI, 600, 11, 1],    // UPPERCASE micro labels
  key: [UI, 700, 12, 1],      // soft-key labels
  axis: [UI, 600, 10, 0],     // tick numbers only
};
// ---------------------------------------------------------------- spacing
export const S = { unit: 4, margin: 8, gutter: 4, notch: 8, statusH: 18, radius: 0, hair: 1 };

// ---------------------------------------------------------------- fonts
const FONT_FILES = [
  ['Saira Condensed', 'SairaCondensed-Medium.ttf', '500'], ['Saira Condensed', 'SairaCondensed-SemiBold.ttf', '600'],
  ['Saira Condensed', 'SairaCondensed-Bold.ttf', '700'],
  ['Chakra Petch', 'ChakraPetch-Medium.ttf', '500'], ['Chakra Petch', 'ChakraPetch-SemiBold.ttf', '600'],
  ['Chakra Petch', 'ChakraPetch-Bold.ttf', '700'],
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
  overshoot: (k) => { k = clamp(k, 0, 1); const c = 1.4; return 1 + (c + 1) * Math.pow(k - 1, 3) + c * Math.pow(k - 1, 2); },
};
function rgba(hex, a) {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${n >> 16},${(n >> 8) & 255},${n & 255},${a})`;
}
const fmtTime = (s) => { s = Math.max(0, Math.floor(s)); const h = Math.floor(s / 3600), m = Math.floor(s / 60) % 60, x = s % 60; return h ? `${h}:${String(m).padStart(2, '0')}:${String(x).padStart(2, '0')}` : `${m}:${String(x).padStart(2, '0')}`; };

// ---------------------------------------------------------------- device
export function createDevice() {
  const canvas = (typeof OffscreenCanvas !== 'undefined') ? new OffscreenCanvas(W, H) : Object.assign(document.createElement('canvas'), { width: W, height: H });
  const g = canvas.getContext('2d');
  const d = {
    g, canvas, W, H,
    rect(x, y, w, h, c) { g.fillStyle = c; g.fillRect(Math.round(x), Math.round(y), Math.round(w), Math.round(h)); },
    // notched rect: 45-degree corner cuts of size n on the corners listed ('tl','tr','br','bl')
    notch(x, y, w, h, c, n = S.notch, corners = 'tr') {
      g.fillStyle = c; g.beginPath();
      const has = (k) => corners.includes(k);
      g.moveTo(x + (has('tl') ? n : 0), y);
      g.lineTo(x + w - (has('tr') ? n : 0), y); if (has('tr')) g.lineTo(x + w, y + n);
      g.lineTo(x + w, y + h - (has('br') ? n : 0)); if (has('br')) g.lineTo(x + w - n, y + h);
      g.lineTo(x + (has('bl') ? n : 0), y + h); if (has('bl')) g.lineTo(x, y + h - n);
      g.lineTo(x, y + (has('tl') ? n : 0)); g.closePath(); g.fill();
    },
    text(s, x, y, type, c = C.text, align = 'left', alpha = 1) {
      const [fam, wt, px, ls] = type;
      g.fillStyle = c; g.font = `${wt} ${px}px ${fam}`; g.textAlign = align; g.textBaseline = 'alphabetic';
      if ('letterSpacing' in g) g.letterSpacing = `${ls}px`;
      const a0 = g.globalAlpha; g.globalAlpha = a0 * alpha;
      // letter-spacing adds a trailing gap; compensate so centred/right text sits true
      const w = g.measureText(s).width;
      const off = align === 'center' ? ls / 2 : align === 'right' ? ls : 0;
      g.fillText(s, Math.round(x + off), Math.round(y));
      g.globalAlpha = a0;
      if ('letterSpacing' in g) g.letterSpacing = '0px';
      return w - ls;
    },
    measure(s, type) { const [fam, wt, px, ls] = type; g.font = `${wt} ${px}px ${fam}`; if ('letterSpacing' in g) g.letterSpacing = `${ls}px`; const w = g.measureText(s).width; if ('letterSpacing' in g) g.letterSpacing = '0px'; return w - ls; },
    label(s, x, y, c = C.mute, align = 'left') { return d.text(s.toUpperCase(), x, y, TYPE.label, c, align); },
    line(pts, w, c, alpha = 1) { const a0 = g.globalAlpha; g.globalAlpha = a0 * alpha; g.strokeStyle = c; g.lineWidth = w; g.lineCap = 'round'; g.lineJoin = 'round'; g.beginPath(); pts.forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.stroke(); g.globalAlpha = a0; },
    dot(x, y, r, c, alpha = 1) { const a0 = g.globalAlpha; g.globalAlpha = a0 * alpha; g.fillStyle = c; g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fill(); g.globalAlpha = a0; },
    vgrad(x, y, w, h, c0, c1) { const gr = g.createLinearGradient(0, y, 0, y + h); gr.addColorStop(0, c0); gr.addColorStop(1, c1); g.fillStyle = gr; g.fillRect(x, y, w, h); },
    hgrad(x, y, w, h, c0, c1) { const gr = g.createLinearGradient(x, 0, x + w, 0); gr.addColorStop(0, c0); gr.addColorStop(1, c1); g.fillStyle = gr; g.fillRect(x, y, w, h); },
    render(id, t, data = demoData(t)) {
      g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.setLineDash([]);
      d.rect(0, 0, W, H, C.bg);
      (DRAW[id] || DRAW.ride)(d, t, data, id);
      if (id === 'lap') DRAW.lapOverlay(d, t, data);
      softkeys(d, SOFTKEYS[id] || SOFTKEYS.ride, PRIMARY[id] ?? 2, t);
      return canvas;
    },
  };
  return d;
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

// ---------------------------------------------------------------- icons (firmware: 1-bit/A8 bitmaps, recoloured)
function icon(d, kind, x, y, s, col) {
  const g = d.g; g.save(); g.translate(x, y); g.scale(s / 20, s / 20);
  g.fillStyle = g.strokeStyle = col; g.lineWidth = 2.4; g.lineCap = 'round'; g.lineJoin = 'round';
  const P = (pts, fill = true) => { g.beginPath(); pts.forEach(([a, b], i) => i ? g.lineTo(a, b) : g.moveTo(a, b)); g.closePath(); fill ? g.fill() : g.stroke(); };
  if (kind === 'heart') { g.beginPath(); g.moveTo(10, 18); g.bezierCurveTo(-3, 9, 1, -1, 10, 5); g.bezierCurveTo(19, -1, 23, 9, 10, 18); g.fill(); }
  if (kind === 'bolt') P([[12, 0], [3, 11], [9, 11], [7, 20], [17, 8], [11, 8], [13, 0]]);
  if (kind === 'crank') { g.beginPath(); g.arc(10, 10, 7.5, 0, 7); g.stroke(); g.beginPath(); g.moveTo(10, 10); g.lineTo(15, 16); g.stroke(); g.beginPath(); g.arc(10, 10, 2.5, 0, 7); g.fill(); }
  if (kind === 'sat') { g.beginPath(); g.arc(10, 12, 3, 0, 7); g.fill(); for (const r of [7, 11]) { g.beginPath(); g.arc(10, 12, r, -2.5, -0.64); g.stroke(); } }
  if (kind === 'phone') { g.lineWidth = 2; g.strokeRect(5, 1, 10, 18); g.fillRect(8, 15, 4, 2); }
  if (kind === 'batt') { g.lineWidth = 2; g.strokeRect(1, 5, 16, 10); g.fillRect(17, 8, 2.5, 4); g.fillRect(3.5, 7.5, 9, 5); }
  if (kind === 'radar') { g.beginPath(); g.arc(10, 18, 3, 0, 7); g.fill(); for (const r of [8, 14]) { g.beginPath(); g.arc(10, 18, r, -2.2, -0.94); g.stroke(); } }
  if (kind === 'light') { P([[3, 6], [12, 3], [12, 17], [3, 14]]); g.beginPath(); g.moveTo(15, 5); g.lineTo(19, 3); g.moveTo(15, 10); g.lineTo(20, 10); g.moveTo(15, 15); g.lineTo(19, 17); g.stroke(); }
  if (kind === 'route') { g.beginPath(); g.moveTo(4, 17); g.bezierCurveTo(4, 8, 16, 12, 16, 3); g.stroke(); g.beginPath(); g.arc(4, 17, 2.6, 0, 7); g.arc(16, 3, 2.6, 0, 7); g.fill(); }
  if (kind === 'bike') { g.lineWidth = 2; g.beginPath(); g.arc(4.5, 13, 4, 0, 7); g.stroke(); g.beginPath(); g.arc(15.5, 13, 4, 0, 7); g.stroke(); g.beginPath(); g.moveTo(4.5, 13); g.lineTo(8, 6); g.lineTo(14, 6); g.lineTo(15.5, 13); g.moveTo(8, 6); g.lineTo(10, 13); g.lineTo(14, 6); g.stroke(); }
  if (kind === 'chart') { g.fillRect(2, 11, 4, 7); g.fillRect(8, 6, 4, 12); g.fillRect(14, 2, 4, 16); }
  if (kind === 'gear') { g.lineWidth = 2.6; g.beginPath(); g.arc(10, 10, 5, 0, 7); g.stroke(); for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4; g.beginPath(); g.moveTo(10 + Math.cos(a) * 7, 10 + Math.sin(a) * 7); g.lineTo(10 + Math.cos(a) * 9.5, 10 + Math.sin(a) * 9.5); g.stroke(); } }
  if (kind === 'sun') { g.beginPath(); g.arc(10, 10, 4, 0, 7); g.fill(); for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4; g.beginPath(); g.moveTo(10 + Math.cos(a) * 7, 10 + Math.sin(a) * 7); g.lineTo(10 + Math.cos(a) * 9.5, 10 + Math.sin(a) * 9.5); g.stroke(); } }
  if (kind === 'sliders') { for (const [yy, xx] of [[4, 13], [10, 6], [16, 11]]) { g.lineWidth = 2; g.beginPath(); g.moveTo(1, yy); g.lineTo(19, yy); g.stroke(); g.beginPath(); g.arc(xx, yy, 3.2, 0, 7); g.fill(); } }
  if (kind === 'flag') { g.fillRect(3, 1, 2.4, 18); P([[5, 2], [18, 2], [14, 7], [18, 12], [5, 12]]); }
  if (kind === 'mountain') P([[0, 18], [7, 5], [11, 11], [14, 7], [20, 18]]);
  g.restore();
}

// ---------------------------------------------------------------- components

// Status bar, 18 px: clock | page dashes (or title) | GPS + battery
function statusBar(d, data, id, title = '') {
  d.text(data.clock, S.margin, 13, TYPE.xs, C.mute);
  const pi = PAGES.indexOf(id);
  if (title) d.label(title, W / 2, 13, C.text, 'center');
  else if (pi >= 0) {
    // page dashes: current = 14 px ion, others 5 px dim, 3 px gap
    const ws = PAGES.map((_, i) => i === pi ? 14 : 5), tot = ws.reduce((a, b) => a + b, 0) + 3 * (ws.length - 1);
    let x = Math.round(W / 2 - tot / 2);
    ws.forEach((w, i) => { d.rect(x, 7, w, 3, i === pi ? C.ion : C.dim); x += w + 3; });
  }
  // GPS: three rising bars
  for (let i = 0; i < 3; i++) d.rect(180 + i * 4, 11 - i * 3, 3, 3 + i * 3, i < 3 ? C.mute : C.dim);
  // battery: 17 x 8 body, 2 px cap, fill in text colour (pause colour under 20 %)
  const bx = 194, by = 5;
  d.g.strokeStyle = C.mute; d.g.lineWidth = 1; d.g.strokeRect(bx + 0.5, by + 0.5, 16, 8); d.rect(bx + 17, by + 3, 2, 3, C.mute);
  d.rect(bx + 2, by + 2, Math.round(13 * data.battery / 100), 5, data.battery > 20 ? C.text : C.pause);
  d.text(`${data.battery}`, W - S.margin, 13, TYPE.xs, C.mute, 'right');
}

// Soft-key bar, 28 px at y 292: three keycaps, each centred over its physical key.
// Keycap: 72 x 20 at (cell+4, 296), bottom corners notched 6 px ("pointing" at the key);
// a 16 x 2 locator tick at y 318 sits exactly above the key. Primary key = filled ion, dark label.
export function softkeys(d, labels, primary = 2, t = 0) {
  const y = H - BAR, cw = W / 3;
  d.rect(0, y, W, BAR, C.bg);
  d.rect(0, y, W, 1, C.line);
  labels.forEach((s, i) => {
    const x0 = Math.round(cw * i), cx = x0 + cw / 2;
    const prim = i === primary && s;
    if (s) d.notch(x0 + 4, y + 4, cw - 8, 20, prim ? C.ion : C.s2, 6, 'bl br');
    d.rect(cx - 8, H - 2, 16, 2, prim ? C.ion : s ? C.dim : C.line);
    if (!s) return;
    const col = prim ? C.bg : C.text;
    const glyph = s === 'PAUSE' ? 'pause' : s === 'START' ? 'play' : s === 'PAGE' ? 'chev' : s === 'LAP' ? 'lap' : s.startsWith('ZOOM') ? (s.endsWith('+') ? 'plus' : 'minus') : s === 'CENTRE' ? 'target' : '';
    const txt = s.startsWith('ZOOM') ? 'ZOOM' : s;
    const tw = d.measure(txt, TYPE.key), gw = glyph ? 12 : 0, tot = tw + gw;
    const tx = cx - tot / 2 + (glyph && glyph !== 'chev' && glyph !== 'plus' && glyph !== 'minus' ? gw : 0);
    const gx = glyph === 'chev' || glyph === 'plus' || glyph === 'minus' ? tx + tw + 5 : cx - tot / 2;
    const cy = y + 14;
    d.text(txt, tx, cy + 4.5, TYPE.key, col);
    const g = d.g; g.fillStyle = g.strokeStyle = col; g.lineWidth = 2; g.lineCap = 'butt';
    if (glyph === 'pause') { d.rect(gx, cy - 5, 3, 10, col); d.rect(gx + 5, cy - 5, 3, 10, col); }
    if (glyph === 'play') { g.beginPath(); g.moveTo(gx, cy - 5); g.lineTo(gx + 8, cy); g.lineTo(gx, cy + 5); g.closePath(); g.fill(); }
    if (glyph === 'chev') { g.beginPath(); g.moveTo(gx, cy - 4); g.lineTo(gx + 4, cy); g.lineTo(gx, cy + 4); g.stroke(); }
    if (glyph === 'plus' || glyph === 'minus') { d.rect(gx, cy - 1, 8, 2, col); if (glyph === 'plus') d.rect(gx + 3, cy - 4, 2, 8, col); }
    if (glyph === 'lap') { d.rect(gx, cy - 5, 2, 10, col); g.beginPath(); g.moveTo(gx + 2, cy - 5); g.lineTo(gx + 9, cy - 5); g.lineTo(gx + 7, cy - 2.5); g.lineTo(gx + 9, cy); g.lineTo(gx + 2, cy); g.closePath(); g.fill(); }
    if (glyph === 'target') { g.lineWidth = 1.6; g.beginPath(); g.arc(gx + 4, cy, 3, 0, 7); g.stroke(); d.rect(gx + 3, cy - 6, 2, 2, col); d.rect(gx + 3, cy + 4, 2, 2, col); d.rect(gx - 2, cy - 1, 2, 2, col); d.rect(gx + 8, cy - 1, 2, 2, col); }
  });
}

// Field: notched panel, 2 px colour spine, UPPERCASE label top-left, big value bottom-left.
// unitPos 'after' puts the unit after the value (body font), 'label' puts it top-right in the label row.
function field(d, x, y, w, h, label, value, unit, col, { type = TYPE.lg, spine = col, extra, unitPos = 'after' } = {}) {
  d.notch(x, y, w, h, C.s1);
  d.rect(x, y, 2, h, spine);
  d.label(label, x + 10, y + 14);
  const by = y + h - 6;
  const vw = d.text(value, x + 9, by, type, col);
  if (unit && unitPos === 'after') d.text(unit, x + 13 + vw, by, TYPE.body, C.mute);
  if (unit && unitPos === 'label') d.label(unit, x + w - 10, y + 14, C.mute, 'right');
  if (extra) extra(x, y, w, h);
}

// Hero value: integer part in TYPE.hero, decimal part in TYPE.dec on the same baseline, centred as a unit.
function hero(d, v, decimals, cx, by, col) {
  const s = v.toFixed(decimals), [ip, dp] = s.split('.');
  const wi = d.measure(ip, TYPE.hero), wd = dp ? d.measure('.' + dp, TYPE.dec) + 2 : 0;
  const x = Math.round(cx - (wi + wd) / 2);
  d.text(ip, x, by, TYPE.hero, col);
  if (dp) d.text('.' + dp, x + wi + 2, by, TYPE.dec, col);
  return { x, w: wi + wd };
}

// Footer row, 28 px at y 262: equal cells, label left, value right-aligned, 1 px dividers.
function footer(d, items, y = 263) {
  const cw = (W - 12) / items.length;
  d.rect(6, y - 1, W - 12, 1, C.line);
  items.forEach(([l, v, u], i) => {
    const x = 6 + i * cw;
    if (i) d.rect(Math.round(x), y + 5, 1, 19, C.line);
    d.label(l, x + (i ? 8 : 2), y + 20);
    const uw = u ? d.measure(u, TYPE.body) + 3 : 0;
    d.text(v, x + cw - (i === items.length - 1 ? 2 : 8) - uw, y + 22, TYPE.sm, C.text, 'right');
    if (u) d.text(u, x + cw - (i === items.length - 1 ? 2 : 8), y + 22, TYPE.body, C.mute, 'right');
  });
}

// The Meridian rail — the signature component. A tick scale with a segmented colour band and a needle.
//   ticks: minor 1x3 px (dim), major 1x6 px (mute) above the band; band h px, segments 1 px apart,
//   active segment at full opacity, others at 28 %; needle 2 px text-colour with a 7x5 cap and a
//   two-layer glow (10 px @ 18 %, 6 px @ 35 %) in the active colour.
function rail(d, x, y, w, { min, max, value, bands, minor, major, h = 6, needle = true, window }) {
  const X = (v) => x + (w * (clamp(v, min, max) - min)) / (max - min);
  // ticks
  for (let v = Math.ceil(min / minor) * minor; v <= max + 1e-6; v += minor) {
    const isMaj = Math.abs(v / major - Math.round(v / major)) < 1e-6;
    d.rect(Math.round(X(v)) - (v >= max ? 1 : 0), y + (isMaj ? 0 : 3), 1, isMaj ? 6 : 3, isMaj ? C.mute : C.dim);
  }
  const by = y + 9;
  d.rect(x, by, w, h, C.s3);
  let active = -1;
  bands.forEach(([a, b, col], i) => {
    const on = value >= a && value < b;
    if (on) active = i;
    const x0 = Math.round(X(a)) + (i ? 1 : 0), x1 = Math.round(X(b));
    d.g.globalAlpha = on ? 1 : 0.28; d.rect(x0, by, x1 - x0, h, col); d.g.globalAlpha = 1;
  });
  if (window) { // target window: the band inside is always lit, bracketed 3 px above and below
    const [a, b, col] = window, x0 = Math.round(X(a)), x1 = Math.round(X(b));
    d.rect(x0, by - 3, x1 - x0, h + 6, col);
    d.rect(x0, by - 3, 2, h + 6, col); d.rect(x1 - 2, by - 3, 2, h + 6, col);
  }
  if (!needle) return active;
  // needle: 2 px text colour, cut out of the band by a 1 px ink gap each side, 7x5 cap on top
  const nx = Math.round(X(value));
  d.rect(nx - 2, by - 1, 4, h + 2, C.bg);
  d.rect(nx - 1, y - 1, 2, h + 13, C.text);
  const g = d.g; g.fillStyle = C.text; g.beginPath(); g.moveTo(nx - 4, y - 6); g.lineTo(nx + 4, y - 6); g.lineTo(nx, y - 1); g.closePath(); g.fill();
  return active;
}

// Round bezel: 60 ticks (every 5th major) between r0 and r1, then a progress arc. (lv_scale round + lv_arc)
function bezel(d, cx, cy, r, frac, col, { sweep = 1, ticks = 60, lit, track = true } = {}) {
  const g = d.g;
  for (let i = 0; i < ticks * sweep; i++) {
    const a = -Math.PI / 2 + (i / ticks) * Math.PI * 2, maj = i % 5 === 0;
    const r0 = r + 5, r1 = r + (maj ? 12 : 9);
    const on = lit !== undefined ? i / ticks < lit : false;
    g.strokeStyle = on ? col : maj ? C.mute : C.dim; g.lineWidth = maj ? 2 : 1; g.lineCap = 'butt';
    g.beginPath(); g.moveTo(cx + Math.cos(a) * r0, cy + Math.sin(a) * r0); g.lineTo(cx + Math.cos(a) * r1, cy + Math.sin(a) * r1); g.stroke();
  }
  g.lineCap = 'butt';
  if (track) { g.strokeStyle = C.s3; g.lineWidth = 8; g.beginPath(); g.arc(cx, cy, r - 2, 0, Math.PI * 2); g.stroke(); }
  if (frac > 0) {
    const a0 = -Math.PI / 2, a1 = a0 + Math.PI * 2 * frac;
    g.strokeStyle = rgba(col, 0.25); g.lineWidth = 14; g.beginPath(); g.arc(cx, cy, r - 2, a0, a1); g.stroke();
    g.strokeStyle = col; g.lineWidth = 8; g.beginPath(); g.arc(cx, cy, r - 2, a0, a1); g.stroke();
    // end cap: 3 px text-colour mark
    g.strokeStyle = C.text; g.lineWidth = 8; g.beginPath(); g.arc(cx, cy, r - 2, a1 - 0.03, a1); g.stroke();
  }
}

// Chip: small notched pill with label and value (used over the map)
function chip(d, x, y, w, h, c = C.s1) { d.notch(x, y, w, h, rgba(c, 0.92), 6, 'tr bl'); }

// Zone badge: "Z4" block in zone colour with dark text + name
function zoneBadge(d, x, y, n, name, col) {
  const bw = d.measure(n, TYPE.label) + 8;
  d.notch(x, y - 10, bw, 13, col, 4, 'tr');
  d.text(n, x + 4, y, TYPE.label, C.bg);
  d.label(name, x + bw + 5, y, col);
}

// Halo: zone light rising to the rail and falling off below it — two stacked 2-stop vertical
// gradients (lv style bg_grad VER, colour → colour with opa 0 → a → 0).
function halo(d, y0, ym, y1, col, a = 0.2) {
  d.vgrad(0, y0, W, ym - y0, rgba(col, 0), rgba(col, a));
  d.vgrad(0, ym, W, y1 - ym, rgba(col, a), rgba(col, 0));
}

// ---------------------------------------------------------------- screens
const DRAW = {};

DRAW.ride = (d, t, data, id = 'ride') => {
  const pz = powerZone(data.power, data.ftp), zc = ZONES[pz];
  halo(d, 20, 150, 176, zc, 0.2);
  statusBar(d, data, id);
  // hero: speed (layout: label row y 31, hero baseline 114)
  d.label('Speed', S.margin, 31);
  const up = data.speed >= data.avgSpeed, g = d.g;
  g.fillStyle = up ? C.z3 : C.z5; g.beginPath();
  if (up) { g.moveTo(58, 31); g.lineTo(62, 24); g.lineTo(66, 31); } else { g.moveTo(58, 24); g.lineTo(62, 31); g.lineTo(66, 24); }
  g.fill();
  d.label(`avg ${data.avgSpeed}`, 70, 31);
  d.label('mph', W - S.margin, 31, C.mute, 'right');
  hero(d, data.speed, 1, W / 2, 114, C.text);
  // Meridian rail: power against the seven zones
  const f = data.ftp;
  zoneBadge(d, S.margin, 130, POWER_ZONES[pz].n, POWER_ZONES[pz].name, zc);
  d.label(`${Math.round(data.power / f * 100)}% FTP`, W - S.margin, 130, C.mute, 'right');
  rail(d, S.margin, 139, W - 2 * S.margin, { min: 0, max: f * 1.6, value: data.power, minor: 25, major: 100,
    bands: POWER_ZONES.map((z, i) => [z.lo * f, Math.min(z.hi, 1.6) * f + (i === 6 ? 1 : 0), ZONES[i]]) });
  // 2 x 2 grid: 112 x 48 fields, 4 px gutter
  const gx0 = 6, gw = 112, gy0 = 160, gh = 48;
  const hz = hrZone(data.hr, data.hrMax);
  field(d, gx0, gy0, gw, gh, 'Power 3s', String(data.power), 'W', zc);
  field(d, gx0 + gw + 4, gy0, gw, gh, 'Heart', String(data.hr), 'bpm', HR_COL[hz], { extra: (x, y) => beat(d, x + gw - 24, y + 22, t, data.hr, HR_COL[hz], 14) });
  field(d, gx0, gy0 + gh + 4, gw, gh, 'Cadence', String(data.cad), 'rpm', C.text, { spine: C.dim });
  field(d, gx0 + gw + 4, gy0 + gh + 4, gw, gh, 'Grade', data.grade.toFixed(1), '%', gradeColor(data.grade));
  footer(d, [['Dist', data.dist.toFixed(1), 'mi'], ['Time', fmtTime(data.elapsed), '']]);
};
function beat(d, x, y, t, bpm, col, s = 12) {
  const ph = (t * bpm / 60) % 1, k = Math.exp(-ph * 7);
  const sz = s * (1 + 0.18 * k);
  d.g.globalAlpha = 0.55 + 0.45 * k; icon(d, 'heart', x + (s - sz) / 2, y + (s - sz) / 2, sz, col); d.g.globalAlpha = 1;
}

DRAW.hr = (d, t, data) => {
  const hz = hrZone(data.hr, data.hrMax), col = HR_COL[hz];
  halo(d, 20, 150, 176, col, 0.2);
  statusBar(d, data, 'hr');
  d.label('Heart rate', S.margin, 31); d.label('bpm', W - S.margin, 31, C.mute, 'right');
  const hv = hero(d, data.hr, 0, W / 2 - 10, 114, col);
  beat(d, hv.x + hv.w + 6, 44, t, data.hr, col, 22);
  zoneBadge(d, S.margin, 130, HR_ZONES[hz].n, HR_ZONES[hz].name, col);
  d.label(`${Math.round(data.hr / data.hrMax * 100)}% max`, W - S.margin, 130, C.mute, 'right');
  const m = data.hrMax;
  rail(d, S.margin, 139, W - 2 * S.margin, { min: 0.5 * m, max: m, value: data.hr, minor: 5, major: 20,
    bands: HR_ZONES.map((z, i) => [z.lo * m, z.hi * m + (i === 4 ? 1 : 0), HR_COL[i]]) });
  // time in zone: 5 rows x 18 px from y 176
  d.label('Time in zone', S.margin, 174); d.label('of ride', W - S.margin, 174, C.dim, 'right');
  const tiz = [412, 2210, 2485, 1175, 214 + Math.floor(t)], tot = tiz.reduce((a, b) => a + b, 0), mx = Math.max(...tiz);
  tiz.forEach((s, i) => {
    const y = 182 + i * 16, cur = i === hz;
    d.text(HR_ZONES[i].n, S.margin, y + 10, TYPE.label, cur ? col : C.mute);
    d.rect(30, y + 2, 118, 9, C.s1);
    d.g.globalAlpha = cur ? 1 : 0.55; d.rect(30, y + 2, Math.max(2, Math.round(118 * s / mx)), 9, HR_COL[i]); d.g.globalAlpha = 1;
    d.text(fmtTime(s), 196, y + 11, TYPE.xs, cur ? C.text : C.mute, 'right');
    d.text(`${Math.round(s / tot * 100)}%`, W - S.margin, y + 11, TYPE.xs, C.dim, 'right');
  });
  footer(d, [['Avg', '141', 'bpm'], ['Max', '171', 'bpm']]);
};

DRAW.climb = (d, t, data) => {
  const g = d.g;
  statusBar(d, data, 'climb');
  const prog = 0.18 + (t * 0.02) % 0.7;
  const n = 30, grades = Array.from({ length: n }, (_, i) => 3.2 + 4.8 * Math.abs(Math.sin(i * 0.33 + 0.6)) + (i > 19 ? 3.2 : 0) + (i > 26 ? 2 : 0));
  const fi = prog * n, i0 = Math.floor(fi);
  const gr = grades[Math.min(n - 1, i0)];
  // title row
  d.text('HAWK HILL', S.margin, 40, TYPE.title, C.text);
  const cat = 'CAT 3', cw = d.measure(cat, TYPE.label) + 10;
  d.notch(W - S.margin - cw, 28, cw, 15, C.s2, 4, 'tr'); d.text(cat, W - S.margin - cw / 2, 39, TYPE.label, C.z5, 'center');
  d.label('2 of 3', W - S.margin - cw - 6, 40, C.mute, 'right');
  // stats: three notched fields
  const fy = 48, fh = 54, fw = 74;
  field(d, 6, fy, fw, fh, 'Grade', gr.toFixed(1), '%', gradeColor(gr));
  field(d, 6 + fw + 4, fy, fw, fh, 'To top', (1.62 * (1 - prog)).toFixed(2), 'mi', C.text, { spine: C.dim, type: TYPE.md });
  field(d, 6 + 2 * (fw + 4), fy, fw + 4, fh, 'Gain left', String(Math.round(612 * (1 - prog))), 'ft', C.text, { spine: C.dim, type: TYPE.md });
  // profile
  const px0 = 8, px1 = 232, base = 228, top = 122;
  let e = 0; const el = [0]; grades.forEach((q) => { e += q; el.push(e); });
  const X = (i) => px0 + (px1 - px0) * i / n, Y = (v) => base - (base - top) * v / e;
  // horizontal guide lines every 25 % of height
  for (let k = 1; k <= 3; k++) d.rect(px0, Math.round(base - (base - top) * k / 4), px1 - px0, 1, rgba(C.line, 0.7));
  for (let i = 0; i < n; i++) {
    const c = gradeColor(grades[i]), done = i < i0;
    const yA = Y(el[i]), yB = Y(el[i + 1]);
    const gd = g.createLinearGradient(0, Math.min(yA, yB), 0, base);
    gd.addColorStop(0, rgba(c, done ? 0.35 : 0.95)); gd.addColorStop(1, rgba(c, done ? 0.06 : 0.22));
    g.fillStyle = gd; g.beginPath(); g.moveTo(X(i), base); g.lineTo(X(i), yA); g.lineTo(X(i + 1), yB); g.lineTo(X(i + 1), base); g.closePath(); g.fill();
    d.line([[X(i), yA], [X(i + 1), yB]], 2, done ? C.dim : c);
    if (i) d.rect(Math.round(X(i)), Math.round(Math.max(yA, yB)), 1, base - Math.max(yA, yB), C.bg);
  }
  // summit flag
  icon(d, 'flag', px1 - 14, top - 18, 14, C.text);
  // distance axis (rail ticks)
  d.rect(px0, base, px1 - px0, 1, C.mute);
  for (let k = 0; k <= 16; k++) { const x = Math.round(px0 + (px1 - px0) * k / 16); d.rect(Math.min(x, px1 - 1), base + 1, 1, k % 4 ? 3 : 6, k % 4 ? C.dim : C.mute); }
  ['0', '0.4', '0.8', '1.2', '1.6 mi'].forEach((s, k) => d.text(s, px0 + (px1 - px0) * k / 4, base + 17, TYPE.axis, C.mute, k === 0 ? 'left' : k === 4 ? 'right' : 'center'));
  // rider
  const mx = X(fi), my = Y(el[i0] + (el[Math.min(n, i0 + 1)] - el[i0]) * (fi - i0));
  g.setLineDash([2, 3]); d.line([[mx, my], [mx, base]], 1, C.ion); g.setLineDash([]);
  d.dot(mx, my, 11, C.ion, 0.18); d.dot(mx, my, 7, C.ion, 0.35); d.dot(mx, my, 4.5, C.ion); d.dot(mx, my, 1.8, C.bg);
  const pw = 30, pxl = clamp(mx - pw / 2, px0, px1 - pw);
  d.notch(pxl, my - 27, pw, 13, C.ion, 4, 'tr'); d.text('YOU', pxl + pw / 2, my - 17, TYPE.label, C.bg, 'center');
  // bottom row
  footer(d, [['Speed', data.speed.toFixed(1), ''], ['VAM', '1120', 'm/h']]);
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
  const k = 0.5 * zoom, cx = W / 2, cy = 196;
  const tf = (x, y) => { const dx = x - p.x, dy = y - p.y; const c = Math.cos(p.h), sn = Math.sin(p.h); return [cx + (dx * c - dy * sn) * k, cy - (dx * sn + dy * c) * k]; };
  const poly = (pts, col) => { g.fillStyle = col; g.beginPath(); pts.forEach(([x, y], i) => { const [u, v] = tf(x, y); i ? g.lineTo(u, v) : g.moveTo(u, v); }); g.closePath(); g.fill(); };
  const path = (pts, wdt, col, a = 1, cap = 'round') => { g.globalAlpha = a; g.strokeStyle = col; g.lineWidth = wdt; g.lineCap = cap; g.lineJoin = 'round'; g.beginPath(); pts.forEach(([x, y], i) => { const [u, v] = tf(x, y); i ? g.lineTo(u, v) : g.moveTo(u, v); }); g.stroke(); g.globalAlpha = 1; };
  g.save(); g.beginPath(); g.rect(0, 0, W, H - BAR); g.clip();
  d.rect(0, 0, W, H, C.mapBg);
  poly(RIVER, C.water); for (const pk of PARKS) poly(pk, C.park);
  for (const st of STREETS) path(st, 6 * zoom, C.road, 1, 'butt');
  for (const st of MAJOR) path(st, 10 * zoom, C.roadMajor, 1, 'butt');
  // route: travelled part dim, ahead part = ion with two-layer glow
  const done = [], ahead = []; let acc = 0;
  for (let i = 0; i < ROUTE.length - 1; i++) {
    const [ax, ay] = ROUTE[i], [bx, by] = ROUTE[i + 1], L = Math.hypot(bx - ax, by - ay);
    if (acc + L <= s) { done.push(ROUTE[i]); } else if (acc >= s) { ahead.push(ROUTE[i]); } else { done.push(ROUTE[i]); done.push([p.x, p.y]); ahead.push([p.x, p.y]); }
    acc += L;
  }
  ahead.push(ROUTE[ROUTE.length - 1]);
  path(done, 5, C.ionDim);
  path(ahead, 16, C.ion, 0.12); path(ahead, 10, C.ion, 0.25); path(ahead, 5, C.ion);
  // turn point marker
  const turn = p.seg === 0 ? ROUTE[1] : ROUTE[2];
  const [tx, ty] = tf(turn[0], turn[1]);
  d.dot(tx, ty, 6, C.bg); d.dot(tx, ty, 4, C.text);
  // rider: halo + chevron (text fill, bg outline)
  d.dot(cx, cy, 18, C.ion, 0.12); d.dot(cx, cy, 11, C.ion, 0.22);
  g.fillStyle = C.text; g.strokeStyle = C.bg; g.lineWidth = 2.5; g.lineJoin = 'round';
  g.beginPath(); g.moveTo(cx, cy - 12); g.lineTo(cx + 9, cy + 9); g.lineTo(cx, cy + 4); g.lineTo(cx - 9, cy + 9); g.closePath(); g.stroke(); g.fill();
  // north pointer (heading-up map): chip with N and a needle rotated by -heading
  const nx = 220, ny = 84;
  d.dot(nx, ny, 13, C.s1, 0.92); g.strokeStyle = C.line; g.lineWidth = 1; g.beginPath(); g.arc(nx, ny, 13, 0, 7); g.stroke();
  g.save(); g.translate(nx, ny); g.rotate(-p.h); g.fillStyle = C.z6; g.beginPath(); g.moveTo(0, -11); g.lineTo(3.5, -6); g.lineTo(-3.5, -6); g.closePath(); g.fill(); g.restore();
  d.text('N', nx, ny + 5, TYPE.label, C.text, 'center');
  // scale bar
  const sb = 34; chip(d, 6, 72, 82, 20);
  d.rect(12, 85, sb, 2, C.text); d.rect(12, 80, 2, 7, C.text); d.rect(12 + sb - 2, 80, 2, 7, C.text);
  d.text(`${Math.round(240 / zoom / 10) * 10} ft`, 12 + sb + 4, 87, TYPE.axis, C.text);
  // turn cue card
  const next = p.seg === 0 ? { dist: p.left, dir: 'right', road: 'Grand St' } : p.seg === 1 ? { dist: p.left, dir: 'left', road: 'Jersey Ave' } : { dist: 0, dir: 'straight', road: 'Jersey Ave' };
  const feet = Math.max(0, Math.round(next.dist * 3.28 / 10) * 10);
  d.notch(0, 0, W, 64, C.s1, 12, 'br');
  d.notch(6, 6, 52, 52, C.ion, 8, 'tr');
  g.strokeStyle = g.fillStyle = C.bg; g.lineWidth = 5; g.lineCap = 'butt'; g.lineJoin = 'miter';
  const ax = 28, ay = 50;
  g.beginPath(); g.moveTo(ax, ay); g.lineTo(ax, 28);
  if (next.dir === 'right') { g.lineTo(40, 28); g.stroke(); g.beginPath(); g.moveTo(39, 19); g.lineTo(50, 28); g.lineTo(39, 37); g.closePath(); g.fill(); }
  else if (next.dir === 'left') { g.moveTo(ax + 2.5, 28); g.lineTo(16, 28); g.stroke(); g.beginPath(); g.moveTo(17, 19); g.lineTo(6 + 8, 28); g.lineTo(17, 37); g.closePath(); g.fill(); }
  else { g.lineTo(ax, 24); g.stroke(); g.beginPath(); g.moveTo(ax - 9, 26); g.lineTo(ax, 14); g.lineTo(ax + 9, 26); g.closePath(); g.fill(); }
  const big = feet >= 1000;
  const fw = d.text(big ? (feet / 5280).toFixed(1) : String(feet), 68, 38, TYPE.lg, C.text);
  d.text(big ? 'mi' : 'ft', 72 + fw, 38, TYPE.body, C.mute);
  d.text(`${next.dir === 'straight' ? 'Continue on' : next.dir === 'right' ? 'Right onto' : 'Left onto'} ${next.road}`, 68, 55, TYPE.body, C.text);
  d.text(data.clock, W - S.margin, 18, TYPE.xs, C.mute, 'right');
  // countdown bar to the turn along the card's bottom edge
  const frac = clamp(1 - next.dist / 400, 0, 1);
  d.rect(0, 62, Math.round((W - 12) * frac), 2, C.ion);
  // bottom chips
  chip(d, 6, 244, 84, 42);
  d.label('mph', 14, 258);
  d.text(data.speed.toFixed(1), 13, 283, TYPE.md, C.text);
  chip(d, 150, 244, 84, 42);
  d.label('ETA 8:21', 226, 258, C.ion, 'right');
  const w2 = d.measure('mi', TYPE.body);
  d.text('mi', 226, 283, TYPE.body, C.mute, 'right'); d.text('12.4', 223 - w2, 283, TYPE.md, C.text, 'right');
  g.restore();
};

DRAW.workout = (d, t, data) => {
  const g = d.g;
  statusBar(d, data, 'workout');
  const len = 600, rem = len - ((t * 4 + 198) % len);
  const lo = 240, hi = 262, pw = Math.round(data.power - 2);
  const on = pw >= lo && pw <= hi, tc = C.z4;
  // corners
  d.label('Step 4/7', S.margin, 31); d.text('Sweet', S.margin, 47, TYPE.body, C.text); d.text('spot', S.margin, 62, TYPE.body, C.text);
  d.label('Next', W - S.margin, 31, C.mute, 'right'); d.text('Rest', W - S.margin, 47, TYPE.body, C.text, 'right'); d.text('5:00', W - S.margin, 62, TYPE.body, C.mute, 'right');
  // bezel ring: lv_scale (round) + lv_arc
  const cx = 120, cy = 110, r = 52;
  bezel(d, cx, cy, r, 1 - rem / len, tc, { lit: 1 - rem / len });
  d.label('Int 2/3', cx, cy - 23, C.mute, 'center');
  d.text(fmtTime(rem), cx, cy + 16, TYPE.timer, C.text, 'center');
  d.label(`of ${fmtTime(len)}`, cx, cy + 32, C.mute, 'center');
  // target rail
  const ry = 186;
  d.label(`Target ${lo}–${hi} W`, S.margin, ry);
  d.label(on ? 'On target' : pw < lo ? 'Push +' + (lo - pw) : 'Ease −' + (pw - hi), W - S.margin, ry, on ? C.z3 : C.pause, 'right');
  rail(d, S.margin, ry + 10, W - 2 * S.margin, { min: 150, max: 350, value: pw, minor: 10, major: 50,
    bands: [[150, lo, C.dim], [lo, hi, tc], [hi, 351, C.z5]], window: [lo, hi, tc] });
  // fields
  const fy = 216, fh = 44;
  field(d, 6, fy, 112, fh, 'Power 3s', String(pw), 'W', on ? tc : C.pause, { type: TYPE.md });
  const hz = hrZone(data.hr + 4, data.hrMax);
  field(d, 122, fy, 112, fh, 'Heart', String(data.hr + 4), 'bpm', HR_COL[hz], { type: TYPE.md, extra: (x, y) => beat(d, x + 94, y + 7, t, data.hr + 4, HR_COL[hz], 12) });
  // session chart
  const steps = [[300, 0.45, C.z2], [600, 0.92, C.z4], [300, 0.5, C.z2], [600, 0.92, C.z4], [300, 0.5, C.z2], [600, 0.92, C.z4], [300, 0.4, C.z1]];
  const tot = steps.reduce((a, [s]) => a + s, 0), cx0 = 6, cw = 228, cb = 289, ch = 22;
  const at = 300 + 600 + 300 + (len - rem);
  let x = cx0, acc = 0;
  steps.forEach(([s, h, c]) => {
    const w = cw * s / tot, hh = Math.round(ch * h);
    const past = acc + s <= at, cur = acc <= at && at < acc + s;
    d.g.globalAlpha = past ? 0.3 : cur ? 1 : 0.6; d.rect(Math.round(x), cb - hh, Math.round(w) - 1, hh, c); d.g.globalAlpha = 1;
    x += w; acc += s;
  });
  const mx = Math.round(cx0 + cw * at / tot);
  d.rect(mx - 1, cb - ch - 4, 2, ch + 4, C.text);
  g.fillStyle = C.text; g.beginPath(); g.moveTo(mx - 4, cb - ch - 8); g.lineTo(mx + 4, cb - ch - 8); g.lineTo(mx, cb - ch - 3); g.closePath(); g.fill();
};

DRAW.status = (d, t, data) => {
  statusBar(d, data, 'status');
  const rows = [
    ['heart', C.z6, 'Heart rate', 'Polar H10 · ANT+', `${data.hr}`, 4],
    ['bolt', C.z4, 'Power', 'Assioma Duo · ANT+', `${data.power}`, 3],
    ['radar', C.z5, 'Radar', 'Varia RTL515 · ANT+', 'clear', 4],
    ['sat', C.z3, 'GNSS', '3D fix · 3 systems', `${data.sats}`, 4],
    ['phone', C.ion, 'Phone', 'OpenCycle app · BLE', 'linked', 2],
    ['batt', C.text, 'Battery', `~${Math.round(data.battery / 100 * 20)} h left`, `${data.battery}%`, -1],
  ];
  const y0 = 24, rh = 42;
  rows.forEach(([ic, col, name, sub, val, bars], i) => {
    const y = y0 + i * (rh + 2);
    d.notch(6, y, 228, rh, C.s1);
    d.rect(6, y, 2, rh, col);
    d.notch(14, y + 7, 28, 28, rgba(col, 0.16), 5, 'tr');
    icon(d, ic, 18, y + 11, 20, col);
    d.text(name, 50, y + 19, TYPE.title, C.text);
    d.text(sub, 50, y + 34, TYPE.body, C.mute);
    d.text(val, 203, y + 21, TYPE.sm, C.text, 'right');
    if (bars >= 0) for (let b = 0; b < 4; b++) d.rect(210 + b * 5, y + 21 - 4 - b * 3, 3, 4 + b * 3, b < bars ? col : C.s3);
    else { d.rect(210, y + 8, 18, 13, C.s3); d.rect(210, Math.round(y + 8 + 13 * (1 - data.battery / 100)), 18, Math.round(13 * data.battery / 100), C.text); }
  });
};

DRAW.lap = (d, t, data) => DRAW.ride(d, t, data, 'ride');
DRAW.lapOverlay = (d, t) => {
  // timeline (s): 0 → 0.4 drop in (overshoot), hold, 4.4 → 4.8 retract (ease in); loops every 6 s
  const ph = t % 6;
  const hgt = 176;
  let k = ph < 0.4 ? EASE.overshoot(ph / 0.4) : ph < 4.4 ? 1 : 1 - EASE.out((ph - 4.4) / 0.4);
  if (k <= 0.001) return;
  const y = Math.round(-hgt + hgt * k);
  const g = d.g;
  // scrim over the ride page
  d.rect(0, 0, W, H - BAR, rgba(C.bg, 0.55 * clamp(k, 0, 1)));
  d.notch(0, Math.min(0, y), W, hgt + Math.max(0, y), C.s2, 14, 'br');   // overshoot grows the card, never uncovers the top
  d.rect(0, y + hgt - 3, W - 14, 3, C.ion);
  // flash on arrival: ion outline fading 0.4 → 1.0 s
  const fl = clamp(1 - (ph - 0.4) / 0.6, 0, 1);
  if (fl > 0 && ph < 1.2) { d.rect(0, y, W, hgt - 3, rgba(C.ion, 0.12 * fl)); }
  // header
  d.notch(S.margin, y + 24, 48, 16, C.ion, 5, 'tr');
  d.text('LAP 4', S.margin + 24, y + 36, TYPE.label, C.bg, 'center');
  d.label('vs lap 3', W - S.margin, y + 36, C.mute, 'right');
  // lap time + delta
  d.text('8:12', S.margin, y + 102, TYPE.xl, C.text);
  const tw = d.measure('8:12', TYPE.xl);
  d.text('.4', S.margin + tw + 2, y + 102, TYPE.md, C.mute);
  d.label('faster', W - S.margin, y + 72, C.z3, 'right');
  d.text('−0:14', W - S.margin, y + 100, TYPE.md, C.z3, 'right');
  // stats row (lap averages)
  const stats = [['Speed', '20.8', '+0.6', C.z3], ['Power', '247', '+9', C.z3], ['Heart', '151', '+4', C.z5]];
  stats.forEach(([l, v, dl, c], i) => {
    const x = S.margin + i * 78;
    if (i) d.rect(x - 8, y + 116, 1, 38, C.line);
    d.label(l, x, y + 126);
    const vw = d.text(v, x, y + 152, TYPE.sm, C.text);
    d.text(dl, x + vw + 4, y + 152, TYPE.body, c);
  });
  // auto-dismiss timer: hairline shrinking under the card over the hold
  const hold = clamp((ph - 0.4) / 4.0, 0, 1);
  d.rect(0, y + hgt, Math.round((W - 14) * (1 - hold)), 2, C.text);
};

DRAW.summary = (d, t, data) => {
  const g = d.g;
  statusBar(d, data, 'summary', 'Ride complete');
  d.label('Sat 27 Sep · Hudson loop', S.margin, 36);
  // hero distance
  const dw = d.text('48.2', S.margin - 2, 92, TYPE.xl, C.text);
  d.text('mi', S.margin + dw + 2, 92, TYPE.title, C.mute);
  // PR chip
  const pr = '3 PRs'; const pw = d.measure(pr, TYPE.label) + 30;
  d.notch(W - S.margin - pw, 56, pw, 20, C.z4, 6, 'tr');
  icon(d, 'flag', W - S.margin - pw + 6, 59, 13, C.bg);
  d.text(pr, W - S.margin - pw + 22, 70, TYPE.label, C.bg);
  d.text('4:12:08 moving', W - S.margin, 92, TYPE.body, C.mute, 'right');
  // elevation trace with ion fill; drawn left→right over the first 1.5 s of each 6 s loop
  const ex0 = 6, ew = 228, eb = 150, eh = 44;
  const pts = Array.from({ length: 61 }, (_, i) => { const u = i / 60; return [ex0 + ew * u, eb - eh * (0.15 + 0.35 * Math.sin(u * 5.2 + 0.4) ** 2 + 0.45 * Math.exp(-((u - 0.62) ** 2) / 0.006) + 0.05 * Math.sin(u * 40))]; });
  const rev = clamp(EASE.inOut(((t % 6)) / 1.5), 0, 1);
  const upto = ex0 + ew * rev;
  d.notch(ex0, 102, ew, 58, C.s1);
  g.save(); g.beginPath(); g.rect(ex0, 100, upto - ex0, 62); g.clip();
  const gd = g.createLinearGradient(0, eb - eh, 0, eb); gd.addColorStop(0, rgba(C.ion, 0.45)); gd.addColorStop(1, rgba(C.ion, 0.02));
  g.fillStyle = gd; g.beginPath(); g.moveTo(ex0, eb); pts.forEach(([x, y]) => g.lineTo(x, y)); g.lineTo(ex0 + ew, eb); g.closePath(); g.fill();
  d.line(pts, 2, C.ion);
  g.restore();
  d.label('Climbed', ex0 + 10, 117); d.text('3,412 ft', ex0 + 72, 117, TYPE.body, C.text);
  d.label('max 612', ex0 + ew - 12, 116, C.mute, 'right');
  // 3 x 2 stat grid
  // spec sheet: 2 x 3 rows of 112 x 38, label left, value right (TYPE.sm + unit in TYPE.axis)
  const cells = [['Speed', '17.9', '', C.text], ['Power', '198', 'W', C.z3], ['NP', '231', 'W', C.z4],
    ['Avg HR', '141', '', C.z3], ['kJ', '2904', '', C.text], ['TSS', '212', '', C.z5]];
  cells.forEach(([l, v, u, c], i) => {
    const x = 6 + (i % 2) * 116, y = 168 + Math.floor(i / 2) * 41;
    d.notch(x, y, 112, 38, C.s1);
    d.rect(x, y, 2, 38, c === C.text ? C.dim : c);
    d.label(l, x + 10, y + 23);
    const uw = u ? d.measure(u, TYPE.axis) + 3 : 0;
    d.text(v, x + 104 - uw, y + 27, TYPE.sm, c, 'right');
    if (u) d.text(u, x + 104, y + 27, TYPE.axis, C.mute, 'right');
  });
};

DRAW.menu = (d, t, data) => {
  statusBar(d, data, 'menu', 'Menu');
  const items = [['bike', 'Ride profiles', 'Road · 6 pages'], ['route', 'Navigate', 'Hudson loop · 48 mi'], ['chart', 'Workouts', 'Sweet spot 3×10'],
    ['radar', 'Sensors', '5 paired'], ['sun', 'Display', 'Auto · 80 %'], ['sliders', 'Settings', 'v0.2 · units mph']];
  // selection steps every 1.5 s, slides 180 ms
  const step = Math.floor(t / 1.5), ph = (t / 1.5) % 1;
  const cur = step % items.length, prev = (step + items.length - 1) % items.length;
  const k = EASE.out(ph * 1.5 / 0.18);
  const y0 = 26, rh = 43;
  const selY = y0 + lerp(prev === items.length - 1 && cur === 0 ? cur : prev, cur, k) * rh;
  items.forEach(([ic, name, sub], i) => { const y = y0 + i * rh; d.notch(6, y, 228, rh - 3, C.s1); });
  d.notch(6, selY, 228, rh - 3, C.ion, S.notch, 'tr');
  items.forEach(([ic, name, sub], i) => {
    const y = y0 + i * rh, sel = i === cur && k > 0.5;
    const fg = sel ? C.bg : C.text;
    icon(d, ic, 16, y + 10, 20, sel ? C.bg : C.ion);
    d.text(name, 46, y + 18, TYPE.title, fg);
    d.text(sub, 46, y + 33, TYPE.body, sel ? C.bg : C.mute, 'left', sel ? 0.75 : 1);
    const g = d.g; g.strokeStyle = sel ? C.bg : C.dim; g.lineWidth = 2; g.lineCap = 'butt';
    g.beginPath(); g.moveTo(218, y + 14); g.lineTo(223, y + 20); g.lineTo(218, y + 26); g.stroke();
  });
};

DRAW.boot = (d, t) => {
  const g = d.g, ph = t % 6;
  const cx = 120, cy = 118, r = 62;
  // 0–1.2 s: bezel ticks sweep in; 0.9–1.5 s: wordmark; 1.5–4.5 s: checks; 4.5–5.2 s hold; 5.2–6 fade
  const out = clamp((ph - 5.2) / 0.8, 0, 1);
  g.globalAlpha = 1 - out;
  const sweep = EASE.out(ph / 1.2);
  bezel(d, cx, cy, r, 0, C.ion, { sweep, lit: clamp((ph - 1.5) / 3, 0, 1), track: false });
  g.globalAlpha = 1 - out;
  // mark: notched square "O" with an ion needle (the logo)
  const mk = EASE.overshoot((ph - 0.6) / 0.5);
  if (mk > 0) {
    g.save(); g.translate(cx, cy - 4); g.scale(mk, mk);
    // the mark: a notched square ring (stroked, so it fades cleanly) — firmware: one A8 bitmap
    g.strokeStyle = C.text; g.lineWidth = 9; g.lineJoin = 'miter';
    g.beginPath(); g.moveTo(-17.5, -17.5); g.lineTo(8, -17.5); g.lineTo(17.5, -8); g.lineTo(17.5, 17.5); g.lineTo(-8, 17.5); g.lineTo(-17.5, 8); g.closePath(); g.stroke();
    g.restore();
    g.globalAlpha = (1 - out) * clamp(mk, 0, 1);
    d.rect(cx - 1, cy - 44, 2, 22, C.ion);
    g.fillStyle = C.ion; g.beginPath(); g.moveTo(cx - 5, cy - 48); g.lineTo(cx + 5, cy - 48); g.lineTo(cx, cy - 42); g.closePath(); g.fill();
    g.globalAlpha = 1 - out;
  }
  const wa = clamp((ph - 0.9) / 0.6, 0, 1);
  g.globalAlpha = (1 - out) * wa;
  d.text('OPENCYCLE', cx, 222 + Math.round(8 * (1 - EASE.out(wa))), [UI, 700, 24, 4], C.text, 'center');
  d.label('Meridian UI · v0.2', cx, 240, C.mute, 'center');
  g.globalAlpha = 1 - out;
  // checks along a rail
  const checks = [['GNSS', 1.8], ['Sensors', 2.6], ['Phone', 3.4], ['Ready', 4.2]];
  const ry = 264, rx = 20, rw = 200;
  d.rect(rx, ry, rw, 2, C.s3);
  const prog = clamp((ph - 1.5) / 2.7, 0, 1);
  d.rect(rx, ry, Math.round(rw * prog), 2, C.ion);
  checks.forEach(([s, at], i) => {
    const x = rx + rw * (i + 1) / checks.length, done = ph >= at;
    d.rect(Math.round(x) - 1, ry - 3, 2, 8, done ? C.ion : C.dim);
    d.text(s.toUpperCase(), x - rw / checks.length / 2, ry + 18, TYPE.axis, done ? C.text : C.dim, 'center');
  });
  g.globalAlpha = 1;
};
