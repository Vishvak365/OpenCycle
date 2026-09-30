// OpenCycle device UI — reference renderer for the 2.7" Sharp memory LCD.
//
// Everything here is drawn the way the firmware will draw it:
//   * native resolution 240 x 400 (panel mounted portrait), 1 bit per pixel
//   * no greys: tones are ordered-dither patterns (Bayer 4x4), exactly what the panel can show
//   * fonts are OFL faces (Barlow Condensed / Barlow Semi Condensed) that get converted
//     to 1-bpp bitmap fonts with lv_font_conv for LVGL; the browser's anti-aliased glyphs
//     are thresholded at 50% here, which is what a 1-bpp conversion produces
//   * the frame buffer is 240*400/8 = 12,000 bytes; a full redraw over 8 MHz SPI is ~13 ms
//
// API
//   const dev = createDevice();            // offscreen 240x400 1-bit device
//   dev.render(screenId, t, data)          // draw one frame (t = seconds)
//   dev.bits                               // Uint8Array(96000), 1 = black pixel
//   dev.blit(ctx, scale, look)             // paint as a reflective LCD at integer scale
//
// Screens: 'ride', 'map', 'climb', 'workout', 'status', plus the 'lap' overlay.
// Change layouts here; the product page and the 3D model both render from this file.

export const W = 240, H = 400;
export const SCREENS = [
  { id: 'ride', name: 'Ride', desc: 'Speed first, then power and heart rate. Power bar shows the current training zone.' },
  { id: 'map', name: 'Navigation', desc: 'Heading-up map from on-device vector tiles, the route drawn heavy, turn cue on top.' },
  { id: 'climb', name: 'Climb', desc: 'Upcoming climb profile, shaded by grade, with distance and height left to the top.' },
  { id: 'workout', name: 'Workout', desc: 'Structured interval with target band, live power, and time left in the step.' },
  { id: 'status', name: 'Sensors', desc: 'Paired sensors, GPS fix, battery and phone link at a glance.' },
  { id: 'lap', name: 'Lap alert', desc: 'Full-width alert when you hit the lap button, then it slides away.' },
];

const DISPLAY = '"Barlow Condensed", "Arial Narrow", sans-serif';
const LABEL = '"Barlow Semi Condensed", "Arial Narrow", sans-serif';
export async function fontsReady() {
  if (!document.fonts) return;
  await Promise.all([
    document.fonts.load(`700 100px ${DISPLAY}`), document.fonts.load(`600 40px ${DISPLAY}`),
    document.fonts.load(`600 14px ${LABEL}`), document.fonts.load(`500 14px ${LABEL}`),
  ]).catch(() => {});
}

// ---------------------------------------------------------------- 1-bit primitives
const BAYER = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5];

export function createDevice() {
  const cv = (typeof OffscreenCanvas !== 'undefined') ? new OffscreenCanvas(W, H) : Object.assign(document.createElement('canvas'), { width: W, height: H });
  const g = cv.getContext('2d', { willReadFrequently: true });
  const bits = new Uint8Array(W * H);
  // tone layer: red channel = dither level * 16, applied after thresholding (like a pattern fill pass)
  const tc = (typeof OffscreenCanvas !== 'undefined') ? new OffscreenCanvas(W, H) : Object.assign(document.createElement('canvas'), { width: W, height: H });
  const tg = tc.getContext('2d', { willReadFrequently: true });

  const api = {
    g, bits, W, H,
    clear() {
      g.setTransform(1, 0, 0, 1, 0, 0); g.fillStyle = '#fff'; g.fillRect(0, 0, W, H);
      tg.fillStyle = '#000'; tg.fillRect(0, 0, W, H);
    },
    ink(on = true) { g.fillStyle = g.strokeStyle = on ? '#000' : '#fff'; },
    rect(x, y, w, h, on = true) {
      x = Math.round(x); y = Math.round(y); w = Math.round(w); h = Math.round(h);
      api.ink(on); g.fillRect(x, y, w, h);
      if (!on) { tg.fillStyle = '#000'; tg.fillRect(x, y, w, h); }
    },
    hline(x, y, w, t = 1, on = true) { api.rect(x, y, w, t, on); },
    vline(x, y, h, t = 1, on = true) { api.rect(x, y, t, h, on); },
    text(s, x, y, size, { font = DISPLAY, weight = 700, align = 'left', on = true, spacing = 0, base = 'alphabetic' } = {}) {
      api.ink(on); g.font = `${weight} ${size}px ${font}`; g.textAlign = align; g.textBaseline = base;
      if ('letterSpacing' in g) g.letterSpacing = `${spacing}px`;
      g.fillText(s, Math.round(x), Math.round(y));
      const w = g.measureText(s).width;
      if ('letterSpacing' in g) g.letterSpacing = '0px';
      return w;
    },
    label(s, x, y, opts = {}) { return api.text(s.toUpperCase(), x, y, opts.size || 13, { font: LABEL, weight: 600, spacing: 1.2, ...opts }); },
    // dither: level 0..16 (16 = solid), optional polygon; ORed onto the 1-bit buffer after drawing
    dither(x, y, w, h, level, path) {
      tg.fillStyle = `rgb(${Math.min(255, level * 16)},0,0)`;
      if (path) { tg.beginPath(); path.forEach(([px, py], i) => (i ? tg.lineTo(px, py) : tg.moveTo(px, py))); tg.closePath(); tg.fill(); }
      else tg.fillRect(Math.round(x), Math.round(y), Math.round(w), Math.round(h));
    },
    finish() {
      const d = g.getImageData(0, 0, W, H).data;
      const t = tg.getImageData(0, 0, W, H).data;
      for (let i = 0, p = 0; i < bits.length; i++, p += 4) {
        let on = (d[p] * 0.3 + d[p + 1] * 0.59 + d[p + 2] * 0.11) < 128;
        if (!on && t[p] > 0) { const lvl = Math.round(t[p] / 16); const x = i % W, y = (i / W) | 0; on = BAYER[(y & 3) * 4 + (x & 3)] < lvl; }
        bits[i] = on ? 1 : 0;
      }
      return bits;
    },
    // paint the 1-bit buffer as a reflective memory LCD at an integer scale
    blit(ctx, scale = 2, look = {}) {
      const off = look.off || [196, 201, 190], on = look.on || [30, 33, 31], grid = look.grid ?? 0.06;
      const img = ctx.createImageData(W * scale, H * scale);
      const o = img.data;
      for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
        const c = bits[y * W + x] ? on : off;
        for (let sy = 0; sy < scale; sy++) for (let sx = 0; sx < scale; sx++) {
          const edge = scale >= 3 && (sx === scale - 1 || sy === scale - 1) ? 1 - grid : 1;
          const i = ((y * scale + sy) * W * scale + x * scale + sx) * 4;
          o[i] = c[0] * edge; o[i + 1] = c[1] * edge; o[i + 2] = c[2] * edge; o[i + 3] = 255;
        }
      }
      ctx.putImageData(img, 0, 0);
    },
    render(id, t, data = demoData(t)) {
      api.clear();
      (DRAW[id] || DRAW.ride)(api, t, data);
      if (id === 'lap' || data.lapAlert) DRAW.lapOverlay(api, t, data);
      return api.finish();
    },
  };
  return api;
}

// ---------------------------------------------------------------- demo ride data (deterministic)
export function demoData(t) {
  const n = (a, f, p = 0) => a * Math.sin(t * f + p);
  const secs = 5902 + Math.floor(t);
  return {
    clock: '7:42', battery: 96, sats: 4,
    speed: 21.7 + n(0.9, 0.7) + n(0.3, 2.3), power: Math.round(238 + n(22, 1.1) + n(9, 3.7)),
    hr: Math.round(146 + n(3, 0.23)), cad: Math.round(91 + n(3, 0.9)), grade: 4.2 + n(0.6, 0.3),
    dist: 31.4 + t * 0.006, elapsed: `${Math.floor(secs / 3600)}:${String(Math.floor(secs / 60) % 60).padStart(2, '0')}:${String(secs % 60).padStart(2, '0')}`,
    ftp: 260, zone: 3,
  };
}

// ---------------------------------------------------------------- shared chrome
function statusBar(d, data) {
  d.text(data.clock, 10, 22, 20, { weight: 600 });
  // GPS bars
  for (let i = 0; i < 4; i++) { const h = 4 + i * 3; (i < data.sats ? d.rect : (x, y, w, hh) => { d.rect(x, y, w, hh); d.rect(x + 1, y + 1, w - 2, hh - 2, false); })(150 + i * 6, 20 - h, 4, h); }
  // battery
  d.rect(186, 9, 40, 14); d.rect(188, 11, 36, 10, false); d.rect(226, 13, 3, 6);
  d.rect(190, 13, Math.round(32 * data.battery / 100), 6);
  d.hline(0, 30, W, 2);
}
function pageDots(d, idx, n = 5) {
  const x0 = W / 2 - (n * 10) / 2;
  for (let i = 0; i < n; i++) { if (i === idx) d.rect(x0 + i * 10, 391, 6, 4); else { d.rect(x0 + i * 10 + 2, 392, 2, 2); } }
}
function field(d, x, y, w, label, value, unit, size = 64) {
  d.label(label, x + 10, y + 18);
  const vw = d.text(value, x + 8, y + 18 + size * 0.86, size);
  if (unit) d.text(unit, x + 12 + vw, y + 18 + size * 0.86, 16, { font: LABEL, weight: 600 });
}

// ---------------------------------------------------------------- screens
const DRAW = {};

DRAW.ride = (d, t, data) => {
  statusBar(d, data);
  d.label('Speed', 10, 52); d.label('mph', 230, 52, { align: 'right' });
  d.text(data.speed.toFixed(1), 120, 168, 118, { align: 'center' });
  // power zone bar: 7 zones, current highlighted, marker at current power
  const zx = 10, zw = 220, zy = 186;
  for (let i = 0; i < 7; i++) {
    const x = zx + i * (zw / 7);
    if (i + 1 === data.zone) d.rect(x + 1, zy, zw / 7 - 2, 10); else d.dither(x + 1, zy, zw / 7 - 2, 10, 5);
  }
  const frac = Math.min(1, data.power / (data.ftp * 1.6));
  d.rect(zx + frac * zw - 1, zy - 5, 3, 20);
  d.hline(0, 206, W, 2); d.vline(119, 206, 164, 2); d.hline(0, 288, W, 2);
  field(d, 0, 206, 120, 'Power', String(data.power), 'W', 58);
  field(d, 120, 206, 120, 'Heart', String(data.hr), '', 58);
  field(d, 0, 288, 120, 'Cadence', String(data.cad), '', 58);
  field(d, 120, 288, 120, 'Grade', data.grade.toFixed(1), '%', 58);
  d.hline(0, 370, W, 2);
  d.text(`${data.dist.toFixed(1)} mi`, 10, 388, 18, { weight: 600 }); d.text(data.elapsed, 230, 388, 18, { weight: 600, align: 'right' });
  pageDots(d, 0);
};

// procedural street grid in "map metres"; the route runs up the middle with two turns
const STREETS = [];
for (let i = -6; i <= 6; i++) { STREETS.push([[i * 90, -900], [i * 90, 900]]); STREETS.push([[-900, i * 110 + 20], [900, i * 110 + 20]]); }
STREETS.push([[-900, -500], [900, 300]]);   // a diagonal avenue
const ROUTE = [[0, -900], [0, 130], [180, 130], [180, 900]];
const PARKS = [[[100, -420], [260, -420], [260, -250], [100, -250]], [[-330, 250], [-110, 250], [-110, 480], [-330, 480]]];
const RIVER = [[-900, -700], [-400, -650], [-150, -760], [300, -690], [900, -760], [900, -900], [-900, -900]];
function routePos(s) {   // position + heading along ROUTE at arc length s
  for (let i = 0; i < ROUTE.length - 1; i++) {
    const [ax, ay] = ROUTE[i], [bx, by] = ROUTE[i + 1]; const L = Math.hypot(bx - ax, by - ay);
    if (s <= L) return { x: ax + (bx - ax) * s / L, y: ay + (by - ay) * s / L, h: Math.atan2(bx - ax, by - ay), seg: i, left: L - s };
    s -= L;
  }
  return { x: 180, y: 900, h: 0, seg: 2, left: 0 };
}
DRAW.map = (d, t, data) => {
  const s = 820 + ((t * 42) % 320);           // ride along, loop near the turn
  const p = routePos(s);
  const k = 0.55;                              // px per map metre
  const cx = W / 2, cy = 270;
  const g = d.g;
  const tf = (x, y) => { const dx = x - p.x, dy = y - p.y; const c = Math.cos(p.h), sn = Math.sin(p.h); return [cx + (dx * c - dy * sn) * k, cy - (dx * sn + dy * c) * k]; };
  // water and parks as dither tones
  d.dither(0, 0, W, H, 4, RIVER.map(([x, y]) => tf(x, y)));
  for (const pk of PARKS) d.dither(0, 0, W, H, 3, pk.map(([x, y]) => tf(x, y)));
  // streets
  g.lineCap = 'square'; d.ink(true); g.lineWidth = 2;
  for (const st of STREETS) { g.beginPath(); st.forEach(([x, y], i) => { const [u, v] = tf(x, y); i ? g.lineTo(u, v) : g.moveTo(u, v); }); g.stroke(); }
  // route: white casing then heavy black line
  g.lineJoin = 'round'; g.lineCap = 'round';
  for (const [wdt, on] of [[13, false], [8, true]]) { d.ink(on); g.lineWidth = wdt; g.beginPath(); ROUTE.forEach(([x, y], i) => { const [u, v] = tf(x, y); i ? g.lineTo(u, v) : g.moveTo(u, v); }); g.stroke(); }
  // rider chevron
  d.ink(true); g.beginPath(); g.moveTo(cx, cy - 14); g.lineTo(cx + 10, cy + 10); g.lineTo(cx, cy + 4); g.lineTo(cx - 10, cy + 10); g.closePath(); g.fill();
  d.ink(false); g.lineWidth = 2; g.stroke();
  // turn cue banner (inverted)
  d.rect(0, 0, W, 78);
  const next = p.seg === 0 ? { dist: p.left, dir: 'right', road: 'Grand St' } : p.seg === 1 ? { dist: p.left, dir: 'left', road: 'Jersey Ave' } : { dist: 0, dir: 'straight', road: 'Jersey Ave' };
  const feet = Math.max(0, Math.round(next.dist * 3.28 / 10) * 10);
  // arrow icon
  d.ink(false); g.lineWidth = 6; g.lineCap = 'butt'; g.lineJoin = 'miter';
  g.beginPath(); g.moveTo(30, 66); g.lineTo(30, 34);
  if (next.dir === 'right') { g.lineTo(48, 34); g.stroke(); g.beginPath(); g.moveTo(46, 24); g.lineTo(58, 34); g.lineTo(46, 44); g.closePath(); g.fill(); }
  else if (next.dir === 'left') { g.lineTo(12, 34); g.stroke(); g.beginPath(); g.moveTo(14, 24); g.lineTo(2, 34); g.lineTo(14, 44); g.closePath(); g.fill(); }
  else { g.stroke(); g.beginPath(); g.moveTo(20, 34); g.lineTo(30, 20); g.lineTo(40, 34); g.closePath(); g.fill(); }
  d.text(feet >= 1000 ? `${(feet / 5280).toFixed(1)} mi` : `${feet} ft`, 70, 44, 38, { on: false });
  d.text(`${next.dir === 'straight' ? 'Continue on' : next.dir === 'right' ? 'Right onto' : 'Left onto'} ${next.road}`, 72, 68, 17, { font: LABEL, weight: 600, on: false });
  // bottom strip
  d.rect(0, 350, W, 50, false); d.hline(0, 350, W, 2);
  const sw = d.text(data.speed.toFixed(1), 10, 385, 30); d.label('mph', 16 + sw, 385, { size: 11 });
  d.text('12.4 mi', 230, 372, 18, { weight: 600, align: 'right' }); d.label('to finish · 0:41', 230, 388, { size: 11, align: 'right' });
  // north pointer
  const [nx, ny] = [W - 20, 100]; d.rect(nx - 13, ny - 13, 26, 26, false); g.lineWidth = 2; d.ink(true); g.strokeRect(nx - 12, ny - 12, 24, 24);
  const a = -p.h; g.beginPath(); g.moveTo(nx + Math.sin(a) * 8, ny - Math.cos(a) * 8); g.lineTo(nx + Math.sin(a + 2.5) * 6, ny - Math.cos(a + 2.5) * 6); g.lineTo(nx + Math.sin(a - 2.5) * 6, ny - Math.cos(a - 2.5) * 6); g.closePath(); g.fill();
  pageDots(d, 1);
};

DRAW.climb = (d, t, data) => {
  statusBar(d, data);
  d.label('Climb 2 / 3', 10, 52); d.label('Palisades', 230, 52, { align: 'right' });
  const prog = (t * 0.02) % 1;
  const left = 0.8 * (1 - prog);
  const lw = d.text(left.toFixed(2), 10, 118, 64); d.text('mi to top', 18 + lw, 118, 18, { font: LABEL, weight: 600 });
  // profile: 30 segments, fill dither by grade
  const px0 = 10, px1 = 230, base = 300, top = 150, n = 30;
  const grades = Array.from({ length: n }, (_, i) => 3 + 5 * Math.abs(Math.sin(i * 0.37 + 0.6)) + (i > 18 ? 2 : 0));
  let e = 0; const el = [0]; grades.forEach((gr) => { e += gr; el.push(e); });
  const maxE = e;
  const X = (i) => px0 + (px1 - px0) * i / n, Y = (v) => base - (base - top) * v / maxE;
  for (let i = 0; i < n; i++) {
    const lvl = grades[i] > 8 ? 16 : grades[i] > 6 ? 10 : grades[i] > 4 ? 6 : 3;
    d.dither(0, 0, W, H, lvl, [[X(i), base], [X(i), Y(el[i])], [X(i + 1), Y(el[i + 1])], [X(i + 1), base]]);
  }
  const g = d.g; d.ink(true); g.lineWidth = 3; g.lineJoin = 'round'; g.beginPath(); el.forEach((v, i) => (i ? g.lineTo(X(i), Y(v)) : g.moveTo(X(i), Y(v)))); g.stroke();
  d.hline(px0, base, px1 - px0, 2);
  // rider marker
  const fi = prog * n, i0 = Math.floor(fi), fr = fi - i0;
  const mx = X(fi), my = Y(el[i0] + (el[Math.min(n, i0 + 1)] - el[i0]) * fr);
  d.vline(mx - 1, my - 26, 26, 3);
  g.beginPath(); g.arc(mx, my, 7, 0, Math.PI * 2); d.ink(false); g.fill(); d.ink(true); g.lineWidth = 3; g.stroke();
  // legend
  [['<4%', 3], ['4-6', 6], ['6-8', 10], ['8%+', 16]].forEach(([s, l], i) => { d.dither(12 + i * 56, 312, 14, 10, l); d.rect(12 + i * 56, 312, 14, 1); d.text(s, 30 + i * 56, 322, 13, { font: LABEL, weight: 600 }); });
  d.hline(0, 334, W, 2); d.vline(119, 334, 50, 2);
  d.label('Avg grade', 10, 352); d.text('6.4%', 10, 380, 26);
  d.label('Height left', 130, 352); d.text(`${Math.round(212 * (1 - prog))} ft`, 130, 380, 26);
  pageDots(d, 2);
};

DRAW.workout = (d, t, data) => {
  statusBar(d, data);
  d.label('Interval 3 / 6', 10, 52); d.label('Sweet spot', 230, 52, { align: 'right' });
  const rem = 300 - Math.floor(t * 4) % 300;
  d.text(`${Math.floor(rem / 60)}:${String(rem % 60).padStart(2, '0')}`, 120, 140, 88, { align: 'center' });
  d.label('left in step', 120, 162, { align: 'center' });
  // target band bar
  const x0 = 14, x1 = 226, lo = 235, hi = 255, min = 150, max = 330;
  const X = (w) => x0 + (x1 - x0) * (w - min) / (max - min);
  d.rect(x0, 196, x1 - x0, 30); d.rect(x0 + 2, 198, x1 - x0 - 4, 26, false);
  d.dither(X(lo), 198, X(hi) - X(lo), 26, 8);
  const pw = data.power; d.rect(X(pw) - 2, 188, 5, 46);
  d.text(`${lo}–${hi} W target`, 120, 252, 16, { font: LABEL, weight: 600, align: 'center' });
  d.hline(0, 266, W, 2);
  d.label('Power', 10, 286); d.text(String(pw), 10, 348, 64); d.text('W', 14 + d.g.measureText(String(pw)).width, 348, 16, { font: LABEL, weight: 600 });
  d.label('Heart', 150, 286); d.text(String(data.hr), 150, 348, 40);
  // steps overview
  const steps = [[60, 0.35], [300, 0.9], [120, 0.5], [300, 0.9], [120, 0.5], [300, 0.9], [120, 0.5], [300, 0.9], [240, 0.3]];
  const tot = steps.reduce((a, [s]) => a + s, 0); let x = 10;
  steps.forEach(([s, h], i) => { const w = 220 * s / tot; const hh = 18 * h; if (i === 3) d.rect(x, 384 - hh, w - 1, hh); else d.dither(x, 384 - hh, w - 1, hh, 6); x += w; });
  pageDots(d, 3);
};

function icon(d, kind, x, y) {
  const g = d.g; d.ink(true);
  if (kind === 'heart') { g.beginPath(); g.moveTo(x + 10, y + 18); g.bezierCurveTo(x - 6, y + 6, x + 2, y - 4, x + 10, y + 4); g.bezierCurveTo(x + 18, y - 4, x + 26, y + 6, x + 10, y + 18); g.fill(); }
  if (kind === 'bolt') { g.beginPath(); g.moveTo(x + 12, y - 2); g.lineTo(x + 3, y + 11); g.lineTo(x + 10, y + 11); g.lineTo(x + 7, y + 20); g.lineTo(x + 17, y + 6); g.lineTo(x + 10, y + 6); g.closePath(); g.fill(); }
  if (kind === 'crank') { g.lineWidth = 3; g.beginPath(); g.arc(x + 10, y + 9, 8, 0, Math.PI * 2); g.stroke(); g.beginPath(); g.moveTo(x + 10, y + 9); g.lineTo(x + 18, y + 17); g.stroke(); }
  if (kind === 'sat') { g.lineWidth = 3; g.beginPath(); g.arc(x + 10, y + 9, 3, 0, Math.PI * 2); g.fill(); for (const r of [7, 11]) { g.beginPath(); g.arc(x + 10, y + 9, r, -2.4, -0.7); g.stroke(); } }
  if (kind === 'phone') { g.lineWidth = 2; g.strokeRect(x + 4, y - 1, 12, 20); g.fillRect(x + 8, y + 14, 4, 2); }
  if (kind === 'batt') { g.lineWidth = 2; g.strokeRect(x + 1, y + 2, 17, 12); g.fillRect(x + 18, y + 5, 2, 6); g.fillRect(x + 3, y + 4, 12, 8); }
}
DRAW.status = (d, t, data) => {
  statusBar(d, data);
  d.label('Sensors and status', 10, 52);
  const rows = [
    ['heart', 'Heart rate', 'Polar H10', `${data.hr} bpm`, true],
    ['bolt', 'Power', 'Assioma Duo', `${data.power} W`, true],
    ['crank', 'Cadence', 'from power meter', `${data.cad} rpm`, true],
    ['sat', 'GPS', '3D fix · 4 systems', '14 sat', true],
    ['phone', 'Phone', 'OpenCycle app', 'synced', true],
    ['batt', 'Battery', '~92 h left', `${data.battery}%`, true],
  ];
  rows.forEach(([ic, name, sub, val], i) => {
    const y = 64 + i * 52;
    icon(d, ic, 10, y + 12);
    d.text(name, 44, y + 22, 20, { weight: 700 });
    d.text(sub, 44, y + 40, 14, { font: LABEL, weight: 500 });
    d.text(val, 230, y + 30, 20, { weight: 600, align: 'right' });
    d.hline(10, y + 50, 220, 1);
  });
  const blink = Math.floor(t * 2) % 2;
  d.label(blink ? 'Searching for sensors' : 'Searching for sensors .', 120, 384, { align: 'center', size: 11 });
  pageDots(d, 4);
};
DRAW.lap = (d, t, data) => { DRAW.ride(d, t, data); };
DRAW.lapOverlay = (d, t, data) => {
  const ph = (t % 5) / 5;                     // slide in, hold, slide out
  const k = ph < 0.12 ? ph / 0.12 : ph > 0.85 ? 1 - (ph - 0.85) / 0.15 : 1;
  const hgt = 176, y = -hgt + Math.round(hgt * (1 - Math.pow(1 - Math.max(0, Math.min(1, k)), 3)));
  if (y <= -hgt) return;
  d.rect(0, y, W, hgt); d.hline(0, y + hgt, W, 3, false); d.hline(0, y + hgt + 3, W, 2);
  d.label('Lap 4', 12, y + 26, { on: false, size: 14 });
  d.text('8:12', 12, y + 96, 72, { on: false });
  d.label('lap time', 12, y + 116, { on: false, size: 11 });
  const cols = [['Avg speed', '20.8'], ['Avg power', '241 W'], ['Avg HR', '149']];
  cols.forEach(([l, v], i) => { const x = 12 + i * 76; d.label(l, x, y + 142, { on: false, size: 10 }); d.text(v, x, y + 166, 22, { on: false }); });
};
