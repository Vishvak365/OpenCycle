// Render every Meridian screen to docs/ui/*.png with Playwright (Chromium).
//   python3 -m http.server 8765          (from the repo root)
//   NODE_PATH=$(npm root -g) node docs/ui/shoot.mjs [http://localhost:8765]
// Optional: SHOOT_FRAMES="map:0,map:5" also writes those frames (3x) to docs/ui/frames/ for checking motion.
import { createRequire } from 'module';
import { writeFileSync, mkdirSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); } catch { // fall back to a global install
  const { execSync } = require('child_process');
  ({ chromium } = require(join(execSync('npm root -g').toString().trim(), 'playwright')));
}
const here = dirname(fileURLToPath(import.meta.url));
const base = process.argv[2] || 'http://localhost:8765';

const browser = await chromium.launch();
const page = await browser.newPage();
page.on('console', (m) => console.log('[page]', m.text()));
page.on('pageerror', (e) => console.log('[pageerror]', e.message));
await page.goto(`${base}/docs/ui/harness.html`);
await page.waitForFunction(() => window.ready === true, null, { timeout: 20000 });

const save = (file, url) => writeFileSync(file, Buffer.from(url.split(',')[1], 'base64'));
const shots = await page.evaluate(() => window.shots());
for (const [name, url] of Object.entries(shots)) save(join(here, name), url);
console.log('wrote', Object.keys(shots).length, 'files');

if (process.env.SHOOT_FRAMES) {
  mkdirSync(join(here, 'frames'), { recursive: true });
  for (const spec of process.env.SHOOT_FRAMES.split(',')) {
    const [id, t] = spec.split(':');
    save(join(here, 'frames', `${id}_${t}.png`), await page.evaluate(([i, tt]) => window.frameAt(i, tt), [id, +t]));
  }
}
await browser.close();
