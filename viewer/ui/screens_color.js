// OpenCycle device UI — reference renderer for the v0.2 colour display
// (Newhaven NHD-2.4-240320AF-CSXP, 2.4" IPS TFT, ST7789, 240 x 320, portrait).
//
// Drawn the way the firmware (LVGL on the ESP32-S3) will draw it:
//   * native resolution 240 x 320, RGB565 on the panel (262K colours in 18-bit mode)
//   * a 28 px soft-key bar at the bottom labels the three unlabelled front keys;
//     each screen defines its own three labels (e.g. ride: LAP / PAGE / PAUSE,
//     map: zoom out / re-centre / zoom in)
//   * fonts are OFL faces (Barlow Condensed / Barlow Semi Condensed) converted with
//     lv_font_conv at 4 bpp; the browser's anti-aliasing here is a fair stand-in
//   * frame buffer 240*320*2 = 150 KB (in PSRAM); full redraw at 40 MHz SPI is ~31 ms
//
// API
//   const dev = createDevice();      // offscreen 240x320 canvas
//   dev.render(screenId, t)          // draw one frame (t = seconds)
//   dev.canvas                       // the canvas, for textures and previews
//   SOFTKEYS[screenId]               // the three key labels for that screen
//
// Screens: 'ride', 'map', 'climb', 'workout', 'status', plus the 'lap' overlay.
// The product page and the 3D model both render from this file.

export const W = 240, H = 320, BAR = 28;
export const SCREENS = [
  { id: 'ride', name: 'Ride', desc: 'Speed first, then power, heart rate, cadence and grade, each in its own colour. Power bar shows the training zone.' },
  { id: 'map', name: 'Navigation', desc: 'Heading-up map with the route in orange and the turn cue on top. The keys become zoom out, re-centre, zoom in.' },
  { id: 'climb', name: 'Climb', desc: 'Upcoming climb profile coloured by gradient, your position, and what is left to the top.' },
  { id: 'workout', name: 'Workout', desc: 'Time left in the interval, a target power band with a live marker, and the session chart.' },
  { id: 'status', name: 'Sensors', desc: 'Paired sensors, GPS fix, battery and phone link at a glance.' },
  { id: 'lap', name: 'Lap alert', desc: 'Full-width lap summary that slides down when you press LAP, then slides away.' },
];
export const SOFTKEYS = {
  ride: ['LAP', 'PAGE ›', 'PAUSE'], lap: ['LAP', 'PAGE ›', 'PAUSE'], climb: ['LAP', 'PAGE ›', 'PAUSE'],
  map: ['zoom-', 'centre', 'zoom+'], workout: ['SKIP', 'PAGE ›', 'PAUSE'], status: ['SCAN', 'PAGE ›', 'PAIR'],
};

// palette (RGB565-safe values; the firmware keeps these in one theme table)
export const C = {
  bg: '#0e1217', panel: '#161c24', bar: '#171d25', line: '#242b34', mute: '#8b97a4', text: '#f2f4f6',
  org: '#f08a3c', red: '#ff6b6b', grn: '#6fd08c', blu: '#3d9be0', yel: '#f2c94c', pur: '#b58cf0',
  map: '#e8ebe4', road: '#ffffff', roadEdge: '#cfd4cc', park: '#c5e0bb', water: '#b9d7ee',
};
const ZONES = ['#8b97a4', '#3d9be0', '#6fd08c', '#f2c94c', '#f08a3c', '#ff6b6b', '#b58cf0'];

const DISPLAY = '"Barlow Condensed", "Arial Narrow", sans-serif';
const LABEL = '"Barlow Semi Condensed", "Arial Narrow", sans-serif';
export async function fontsReady() {
  if (!document.fonts) return;
  await Promise.all([
    document.fonts.load(`700 100px ${DISPLAY}`), document.fonts.load(`600 40px ${DISPLAY}`),
    document.fonts.load(`600 14px ${LABEL}`), document.fonts.load(`500 14px ${LABEL}`),
  ]).catch(() => {});
}

export function createDevice() {
  const canvas = (typeof OffscreenCanvas !== 'undefined') ? new OffscreenCanvas(W, H) : Object.assign(document.createElement('canvas'), { width: W, height: H });
  const g = canvas.getContext('2d');
  const d = {
    g, canvas, W, H,
    rect(x, y, w, h, c) { g.fillStyle = c; g.fillRect(Math.round(x), Math.round(y), Math.round(w), Math.round(h)); },
    rrect(x, y, w, h, r, c) { g.fillStyle = c; g.beginPath(); g.roundRect(x, y, w, h, r); g.fill(); },
    text(s, x, y, size, c = C.text, { font = DISPLAY, weight = 700, align = 'left', spacing = 0 } = {}) {
      g.fillStyle = c; g.font = `${weight} ${size}px ${font}`; g.textAlign = align; g.textBaseline = 'alphabetic';
      if ('letterSpacing' in g) g.letterSpacing = `${spacing}px`;
      g.fillText(s, Math.round(x), Math.round(y));
      const w = g.measureText(s).width;
      if ('letterSpacing' in g) g.letterSpacing = '0px';
      return w;
    },
    label(s, x, y, opts = {}) { return d.text(s.toUpperCase(), x, y, opts.size || 12, opts.c || C.mute, { font: LABEL, weight: 600, spacing: 1.1, ...opts }); },
    render(id, t, data = demoData(t)) {
      g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1;
      d.rect(0, 0, W, H, C.bg);
      (DRAW[id] || DRAW.ride)(d, t, data);
      if (id === 'lap') DRAW.lapOverlay(d, t, data);
      softkeys(d, SOFTKEYS[id] || SOFTKEYS.ride);
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
    clock: '7:42', battery: 96, sats: 4,
    speed: 21.7 + n(0.9, 0.7) + n(0.3, 2.3), power: Math.round(238 + n(22, 1.1) + n(9, 3.7)),
    hr: Math.round(146 + n(3, 0.23)), cad: Math.round(91 + n(3, 0.9)), grade: 4.2 + n(0.6, 0.3),
    dist: 31.4 + t * 0.006, elapsed: `${Math.floor(secs / 3600)}:${String(Math.floor(secs / 60) % 60).padStart(2, '0')}:${String(secs % 60).padStart(2, '0')}`,
    ftp: 260,
  };
}

// ---------------------------------------------------------------- shared chrome
function statusBar(d, data, title = '') {
  const g = d.g;
  d.rect(0, 0, W, 20, C.bg); d.rect(0, 20, W, 1, C.line);
  d.text(data.clock, 8, 15, 15, C.mute, { weight: 600 });
  if (title) d.label(title, W / 2, 15, { align: 'center', c: C.text, size: 12 });
  // GPS dot
  g.fillStyle = C.grn; g.beginPath(); g.arc(186, 10, 3.5, 0, 7); g.fill();
  // battery
  g.strokeStyle = C.mute; g.lineWidth = 1; g.strokeRect(194.5, 5.5, 18, 10); d.rect(213, 8, 2, 5, C.mute);
  d.rect(196, 7, Math.round(15 * data.battery / 100), 7, data.battery > 20 ? C.mute : C.red);
  d.text(`${data.battery}`, 234, 15, 13, C.mute, { weight: 600, align: 'right' });
}
function softkeys(d, labels) {
  const g = d.g, y = H - BAR, cw = W / 3;
  d.rect(0, y, W, BAR, C.bar); d.rect(0, y, W, 1, C.line);
  labels.forEach((s, i) => {
    const cx = cw * i + cw / 2, cy = y + BAR / 2 + 1;
    if (i) d.rect(cw * i, y + 5, 1, BAR - 10, C.line);
    const col = i === 2 && s !== 'zoom+' && s !== 'PAIR' ? C.org : C.text;
    g.strokeStyle = g.fillStyle = col; g.lineWidth = 2;
    if (s === 'zoom-' || s === 'zoom+') {
      const plus = s === 'zoom+';
      const w = d.text('ZOOM', cx + (plus ? -7 : 7), cy + 5, 14, col, { align: 'center', spacing: 1 });
      const ix = plus ? cx - 7 + w / 2 + 9 : cx + 7 - w / 2 - 9;
      g.beginPath(); g.moveTo(ix - 4, cy); g.lineTo(ix + 4, cy); if (plus) { g.moveTo(ix, cy - 4); g.lineTo(ix, cy + 4); } g.stroke();
    } else if (s === 'centre') {
      g.lineWidth = 1.6; g.beginPath(); g.arc(cx - 26, cy, 4, 0, 7); g.stroke();
      g.beginPath(); g.moveTo(cx - 26, cy - 7); g.lineTo(cx - 26, cy - 4.5); g.moveTo(cx - 26, cy + 4.5); g.lineTo(cx - 26, cy + 7);
      g.moveTo(cx - 33, cy); g.lineTo(cx - 30.5, cy); g.moveTo(cx - 21.5, cy); g.lineTo(cx - 19, cy); g.stroke();
      d.text('CENTRE', cx + 6, cy + 5, 14, col, { align: 'center', spacing: 1 });
    } else d.text(s, cx, cy + 5, 14, col, { align: 'center', spacing: 1 });
  });
}
function field(d, x, y, w, h, label, value, unit, col, size = 44) {
  d.label(label, x + 8, y + 15);
  const vw = d.text(value, x + 7, y + 15 + size * 0.9, size, col);
  if (unit) d.text(unit, x + 10 + vw, y + 15 + size * 0.9, 14, C.mute, { font: LABEL, weight: 600 });
}

// ---------------------------------------------------------------- screens
const DRAW = {};

DRAW.ride = (d, t, data) => {
  statusBar(d, data);
  d.label('Speed · mph', 8, 36); d.label(`avg 18.9`, 232, 36, { align: 'right' });
  d.text(data.speed.toFixed(1), W / 2, 124, 100, C.text, { align: 'center' });
  // power zones: 7 blocks, current one lit, marker at the current power
  const zx = 8, zw = 224, zy = 134, zone = Math.min(6, Math.floor(data.power / data.ftp * 5.2));
  for (let i = 0; i < 7; i++) {
    const x = zx + i * (zw / 7);
    d.g.globalAlpha = i === zone ? 1 : 0.28; d.rrect(x + 1, zy, zw / 7 - 2, 7, 2, ZONES[i]); d.g.globalAlpha = 1;
  }
  const frac = Math.min(1, data.power / (data.ftp * 1.6));
  d.rrect(zx + frac * zw - 1.5, zy - 3, 3, 13, 1, C.text);
  d.rect(0, 148, W, 1, C.line); d.rect(W / 2, 148, 1, 144, C.line); d.rect(0, 220, W, 1, C.line);
  field(d, 0, 148, 120, 72, 'Power · 3s', String(data.power), 'W', C.org);
  field(d, 120, 148, 120, 72, 'Heart', String(data.hr), 'bpm', C.red);
  field(d, 0, 220, 120, 72, 'Cadence', String(data.cad), 'rpm', C.text);
  field(d, 120, 220, 120, 72, 'Grade', data.grade.toFixed(1), '%', C.grn);
};

// procedural street grid in "map metres"; the route runs up the middle with two turns
const STREETS = [];
for (let i = -6; i <= 6; i++) { STREETS.push([[i * 90, -900], [i * 90, 900]]); STREETS.push([[-900, i * 110 + 20], [900, i * 110 + 20]]); }
STREETS.push([[-900, -500], [900, 300]]);
const ROUTE = [[0, -900], [0, 130], [180, 130], [180, 900]];
const PARKS = [[[100, -420], [260, -420], [260, -250], [100, -250]], [[-330, 250], [-110, 250], [-110, 480], [-330, 480]]];
const RIVER = [[-900, -700], [-400, -650], [-150, -760], [300, -690], [900, -760], [900, -900], [-900, -900]];
function routePos(s) {
  for (let i = 0; i < ROUTE.length - 1; i++) {
    const [ax, ay] = ROUTE[i], [bx, by] = ROUTE[i + 1]; const L = Math.hypot(bx - ax, by - ay);
    if (s <= L) return { x: ax + (bx - ax) * s / L, y: ay + (by - ay) * s / L, h: Math.atan2(bx - ax, by - ay), seg: i, left: L - s };
    s -= L;
  }
  return { x: 180, y: 900, h: 0, seg: 2, left: 0 };
}
DRAW.map = (d, t, data) => {
  const g = d.g;
  const s = 820 + ((t * 42) % 320);
  const p = routePos(s);
  const zoom = 1 + 0.18 * Math.sin(t * 0.35);          // gentle zoom so the keys' job reads
  const k = 0.5 * zoom, cx = W / 2, cy = 214;
  const tf = (x, y) => { const dx = x - p.x, dy = y - p.y; const c = Math.cos(p.h), sn = Math.sin(p.h); return [cx + (dx * c - dy * sn) * k, cy - (dx * sn + dy * c) * k]; };
  const poly = (pts, col) => { g.fillStyle = col; g.beginPath(); pts.forEach(([x, y], i) => { const [u, v] = tf(x, y); i ? g.lineTo(u, v) : g.moveTo(u, v); }); g.closePath(); g.fill(); };
  const line = (pts, wdt, col) => { g.strokeStyle = col; g.lineWidth = wdt; g.beginPath(); pts.forEach(([x, y], i) => { const [u, v] = tf(x, y); i ? g.lineTo(u, v) : g.moveTo(u, v); }); g.stroke(); };
  g.save(); g.beginPath(); g.rect(0, 0, W, H - BAR); g.clip();
  d.rect(0, 0, W, H, C.map);
  poly(RIVER, C.water); for (const pk of PARKS) poly(pk, C.park);
  g.lineCap = 'butt';
  for (const st of STREETS) line(st, 9 * zoom, C.roadEdge);
  for (const st of STREETS) line(st, 7 * zoom, C.road);
  g.lineJoin = 'round'; g.lineCap = 'round';
  line(ROUTE, 13, '#ffffff'); line(ROUTE, 9, C.org);
  // rider arrow
  g.fillStyle = C.blu; g.strokeStyle = '#ffffff'; g.lineWidth = 2.5; g.lineJoin = 'round';
  g.beginPath(); g.moveTo(cx, cy - 13); g.lineTo(cx + 10, cy + 10); g.lineTo(cx, cy + 4); g.lineTo(cx - 10, cy + 10); g.closePath(); g.fill(); g.stroke();
  // scale bar
  d.rrect(176, 72, 56, 17, 3, 'rgba(14,18,23,0.82)');
  g.strokeStyle = C.text; g.lineWidth = 1.5; g.beginPath(); g.moveTo(181, 80); g.lineTo(181, 84); g.lineTo(203, 84); g.lineTo(203, 80); g.stroke();
  d.text(`${Math.round(200 / zoom / 10) * 10} ft`, 207, 85, 11, C.text, { font: LABEL, weight: 600 });
  // turn cue
  d.rect(0, 0, W, 64, C.blu);
  const next = p.seg === 0 ? { dist: p.left, dir: 'right', road: 'Grand St' } : p.seg === 1 ? { dist: p.left, dir: 'left', road: 'Jersey Ave' } : { dist: 0, dir: 'straight', road: 'Jersey Ave' };
  const feet = Math.max(0, Math.round(next.dist * 3.28 / 10) * 10);
  g.strokeStyle = g.fillStyle = '#ffffff'; g.lineWidth = 5; g.lineCap = 'round'; g.lineJoin = 'round';
  g.beginPath(); g.moveTo(26, 54); g.lineTo(26, 28);
  if (next.dir === 'right') { g.lineTo(42, 28); g.stroke(); g.beginPath(); g.moveTo(40, 19); g.lineTo(51, 28); g.lineTo(40, 37); g.closePath(); g.fill(); }
  else if (next.dir === 'left') { g.lineTo(10, 28); g.stroke(); g.beginPath(); g.moveTo(12, 19); g.lineTo(1, 28); g.lineTo(12, 37); g.closePath(); g.fill(); }
  else { g.stroke(); g.beginPath(); g.moveTo(17, 28); g.lineTo(26, 15); g.lineTo(35, 28); g.closePath(); g.fill(); }
  const fw = d.text(feet >= 1000 ? (feet / 5280).toFixed(1) : String(feet), 62, 38, 36, '#ffffff');
  d.text(feet >= 1000 ? 'mi' : 'ft', 66 + fw, 38, 17, '#e4f1fb', { weight: 600 });
  d.text(`${next.dir === 'straight' ? 'Continue on' : next.dir === 'right' ? 'Right onto' : 'Left onto'} ${next.road}`, 63, 56, 15, '#e4f1fb', { font: LABEL, weight: 600 });
  // speed + distance chips
  const sw = 64;
  d.rrect(6, 250, sw + 10, 34, 4, 'rgba(14,18,23,0.86)');
  const w1 = d.text(data.speed.toFixed(1), 11, 278, 28); d.label('mph', 14 + w1, 278, { size: 10 });
  d.rrect(162, 256, 72, 28, 4, 'rgba(14,18,23,0.86)');
  d.text('12.4', 168, 277, 20); d.label('mi left', 198, 277, { size: 10 });
  g.restore();
};

DRAW.climb = (d, t, data) => {
  const g = d.g;
  statusBar(d, data, 'Climb 2 / 3');
  d.text('Hawk Hill', 8, 42, 18, C.text, { weight: 600 });
  const prog = (t * 0.02) % 1;
  const n = 26, grades = Array.from({ length: n }, (_, i) => 3 + 5 * Math.abs(Math.sin(i * 0.37 + 0.6)) + (i > 16 ? 2.5 : 0));
  const fi = prog * n, i0 = Math.floor(fi);
  const gradeNow = grades[Math.min(n - 1, i0)];
  const gcol = (gr) => gr < 5 ? C.grn : gr < 7 ? C.yel : gr < 9 ? C.org : C.red;
  d.rect(0, 50, W, 1, C.line); d.rect(80, 50, 1, 62, C.line); d.rect(160, 50, 1, 62, C.line); d.rect(0, 112, W, 1, C.line);
  field(d, 0, 50, 80, 62, 'Grade', gradeNow.toFixed(1), '%', gcol(gradeNow), 36);
  field(d, 80, 50, 80, 62, 'To top', (0.9 * (1 - prog)).toFixed(1), 'mi', C.text, 36);
  field(d, 160, 50, 80, 62, 'To go', String(Math.round(486 * (1 - prog))), 'ft', C.text, 36);
  // profile
  const px0 = 8, px1 = 232, base = 238, top = 128;
  let e = 0; const el = [0]; grades.forEach((gr) => { e += gr; el.push(e); });
  const X = (i) => px0 + (px1 - px0) * i / n, Y = (v) => base - (base - top) * v / e;
  for (let i = 0; i < n; i++) {
    g.globalAlpha = i < fi ? 0.4 : 1; g.fillStyle = gcol(grades[i]);
    g.beginPath(); g.moveTo(X(i), base); g.lineTo(X(i), Y(el[i])); g.lineTo(X(i + 1), Y(el[i + 1])); g.lineTo(X(i + 1), base); g.closePath(); g.fill();
  }
  g.globalAlpha = 1; d.rect(px0, base, px1 - px0, 1, C.line);
  const mx = X(fi), my = Y(el[i0] + (el[Math.min(n, i0 + 1)] - el[i0]) * (fi - i0));
  g.strokeStyle = C.text; g.lineWidth = 1.5; g.setLineDash([3, 3]); g.beginPath(); g.moveTo(mx, my - 24); g.lineTo(mx, base); g.stroke(); g.setLineDash([]);
  g.fillStyle = C.blu; g.strokeStyle = '#fff'; g.lineWidth = 2; g.beginPath(); g.arc(mx, my, 5.5, 0, 7); g.fill(); g.stroke();
  [['<5%', C.grn], ['5-7', C.yel], ['7-9', C.org], ['9%+', C.red]].forEach(([s, c], i) => { d.rrect(10 + i * 56, 245, 12, 8, 2, c); d.text(s, 26 + i * 56, 253, 12, C.mute, { font: LABEL, weight: 600 }); });
  d.rect(0, 260, W, 1, C.line); d.rect(W / 2, 260, 1, 32, C.line);
  d.label('Speed', 8, 274, { size: 10 }); d.text(data.speed.toFixed(1), 8, 290, 17 + 2);
  d.label('VAM', 128, 274, { size: 10 }); d.text('1,120', 128, 290, 19);
};

DRAW.workout = (d, t, data) => {
  const g = d.g;
  statusBar(d, data, 'Sweet spot 3×10');
  d.label('Interval 2 of 3', 8, 36); d.label('left', 232, 36, { align: 'right' });
  const rem = 402 - Math.floor(t * 4) % 402;
  d.text(`${Math.floor(rem / 60)}:${String(rem % 60).padStart(2, '0')}`, W / 2, 106, 76, C.text, { align: 'center' });
  const lo = 250, hi = 270, min = 150, max = 350, x0 = 8, x1 = 232;
  const X = (w) => x0 + (x1 - x0) * (w - min) / (max - min);
  const on = data.power >= lo && data.power <= hi;
  d.label(`Target ${lo}–${hi} W`, 8, 126); d.label(on ? 'on target' : data.power < lo ? 'go harder' : 'ease off', 232, 126, { align: 'right', c: on ? C.grn : C.yel });
  d.rrect(x0, 134, x1 - x0, 14, 3, '#2a323d'); d.rect(X(lo), 134, X(hi) - X(lo), 14, C.grn);
  const pw = Math.round(data.power + 18);
  const mx = X(Math.max(min, Math.min(max, pw)));
  g.fillStyle = C.text; g.beginPath(); g.moveTo(mx - 6, 128); g.lineTo(mx + 6, 128); g.lineTo(mx, 136); g.closePath(); g.fill(); d.rect(mx - 1, 134, 2, 16, C.text);
  d.rect(0, 158, W, 1, C.line); d.rect(W / 2, 158, 1, 68, C.line); d.rect(0, 226, W, 1, C.line);
  field(d, 0, 158, 120, 68, 'Power · 3s', String(pw), 'W', C.org);
  field(d, 120, 158, 120, 68, 'Heart', String(data.hr + 6), 'bpm', C.red);
  const steps = [[60, 0.4], [600, 0.9], [300, 0.5], [600, 0.9], [300, 0.5], [600, 0.9], [240, 0.35]];
  const tot = steps.reduce((a, [s]) => a + s, 0); let x = 8;
  const at = 60 + 600 + 300 + 600 - rem * 1.49;
  steps.forEach(([s, h]) => { const w = 224 * s / tot, hh = 44 * h; g.globalAlpha = (x - 8) / 224 * tot < at ? 0.45 : 1; d.rect(x, 284 - hh, w - 1, hh, h > 0.8 ? C.org : '#3a4452'); g.globalAlpha = 1; x += w; });
  d.rect(8 + 224 * at / tot, 234, 2, 52, C.text);
};

function icon(d, kind, x, y, col) {
  const g = d.g; g.fillStyle = g.strokeStyle = col; g.lineWidth = 2.5; g.lineCap = 'round';
  if (kind === 'heart') { g.beginPath(); g.moveTo(x + 10, y + 17); g.bezierCurveTo(x - 5, y + 6, x + 2, y - 3, x + 10, y + 4); g.bezierCurveTo(x + 18, y - 3, x + 25, y + 6, x + 10, y + 17); g.fill(); }
  if (kind === 'bolt') { g.beginPath(); g.moveTo(x + 12, y - 2); g.lineTo(x + 3, y + 10); g.lineTo(x + 10, y + 10); g.lineTo(x + 7, y + 19); g.lineTo(x + 17, y + 6); g.lineTo(x + 10, y + 6); g.closePath(); g.fill(); }
  if (kind === 'crank') { g.beginPath(); g.arc(x + 10, y + 8, 7, 0, 7); g.stroke(); g.beginPath(); g.moveTo(x + 10, y + 8); g.lineTo(x + 17, y + 15); g.stroke(); }
  if (kind === 'sat') { g.beginPath(); g.arc(x + 10, y + 9, 3, 0, 7); g.fill(); for (const r of [7, 11]) { g.beginPath(); g.arc(x + 10, y + 9, r, -2.4, -0.7); g.stroke(); } }
  if (kind === 'phone') { g.lineWidth = 2; g.strokeRect(x + 5, y - 1, 11, 19); g.fillRect(x + 8.5, y + 13, 4, 2); }
  if (kind === 'batt') { g.lineWidth = 2; g.strokeRect(x + 1, y + 2, 16, 11); g.fillRect(x + 17, y + 5, 2, 5); g.fillRect(x + 3, y + 4, 11, 7); }
}
DRAW.status = (d, t, data) => {
  statusBar(d, data, 'Sensors');
  const rows = [
    ['heart', C.red, 'Heart rate', 'Polar H10 · ANT+', `${data.hr}`],
    ['bolt', C.org, 'Power', 'Assioma Duo · ANT+', `${data.power} W`],
    ['crank', C.text, 'Cadence', 'from power meter', `${data.cad}`],
    ['sat', C.grn, 'GPS', '3D fix · 4 systems', '14 sats'],
    ['phone', C.blu, 'Phone', 'OpenCycle app · BLE', 'synced'],
    ['batt', C.mute, 'Battery', '~16 h left', `${data.battery}%`],
  ];
  rows.forEach(([ic, col, name, sub, val], i) => {
    const y = 24 + i * 44;
    icon(d, ic, 8, y + 12, col);
    d.text(name, 38, y + 20, 17, C.text, { weight: 700 });
    d.text(sub, 38, y + 36, 12, C.mute, { font: LABEL, weight: 500 });
    d.text(val, 232, y + 27, 18, C.text, { weight: 600, align: 'right' });
    d.rect(8, y + 43, 224, 1, C.line);
  });
};
DRAW.lap = (d, t, data) => { DRAW.ride(d, t, data); };
DRAW.lapOverlay = (d, t) => {
  const ph = (t % 5) / 5;
  const k = ph < 0.12 ? ph / 0.12 : ph > 0.85 ? 1 - (ph - 0.85) / 0.15 : 1;
  const hgt = 150, y = -hgt + Math.round(hgt * (1 - Math.pow(1 - Math.max(0, Math.min(1, k)), 3)));
  if (y <= -hgt) return;
  d.rect(0, y, W, hgt, C.org); d.rect(0, y + hgt, W, 2, C.bg);
  d.label('Lap 4', 10, y + 22, { c: '#1a0d04', size: 13 });
  d.text('8:12', 10, y + 86, 66, '#1a0d04');
  d.label('lap time', 12, y + 102, { c: '#3d2210', size: 11 });
  [['Avg speed', '20.8'], ['Avg power', '241 W'], ['Avg HR', '149']].forEach(([l, v], i) => {
    const x = 10 + i * 78; d.label(l, x, y + 122, { c: '#3d2210', size: 10 }); d.text(v, x, y + 143, 20, '#1a0d04');
  });
};
