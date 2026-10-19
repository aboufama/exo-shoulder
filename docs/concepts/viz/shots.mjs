// shots.mjs - screenshots of the built gallery (dist/index.html) for given concepts at 2 poses each, assembled into a
// contact sheet, plus full-page shots (desktop light / dark, phone 400 px) and every console error.
//   node docs/concepts/viz/shots.mjs [--out DIR] [--poses overhead,behind] [id ...]     (default: every concept with a preview)
// Needs playwright-core (or playwright) resolvable: set PW_MODULE to its path if it is not installed next to this file.
// Chromium from PLAYWRIGHT_BROWSERS_PATH; HTTPS_PROXY (if set) is passed to the browser for the two CDN scripts.
import fs from 'fs';
import path from 'path';
import url from 'url';
import { createRequire } from 'module';

const HERE = path.dirname(url.fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); if (i < 0) return d; const v = args[i + 1]; args.splice(i, 2); return v; };
const OUT = opt('--out', path.join(HERE, 'dist', 'shots'));
const POSES = opt('--poses', 'overhead,behind').split(',');
let pw;
for (const m of [process.env.PW_MODULE, 'playwright-core', 'playwright', '/opt/node22/lib/node_modules/playwright'].filter(Boolean)) {
  try { pw = require(m); break; } catch (e) { /* next */ }
}
if (!pw) { console.error('playwright-core not found: npm install playwright-core in a scratch dir and set PW_MODULE'); process.exit(2); }
const { chromium } = pw;
fs.mkdirSync(OUT, { recursive: true });

const dist = fs.readFileSync(path.join(HERE, 'dist', 'index.html'), 'utf8');
// the Artifact host wraps the page in this skeleton
const wrapped = `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top);padding-bottom:env(safe-area-inset-bottom)}body{margin:0;font:14px system-ui}img{max-width:100%}[hidden]{display:none!important}</style>
</head><body>${dist}</body></html>`;
const launch = { args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] };
if (process.env.HTTPS_PROXY) launch.proxy = { server: process.env.HTTPS_PROXY };
const browser = await chromium.launch(launch);
const errors = [];
async function open(viewport, scheme) {
  const ctx = await browser.newContext({ viewport, colorScheme: scheme, deviceScaleFactor: 1, reducedMotion: 'reduce' });
  const page = await ctx.newPage();
  page.on('console', m => { if ((m.type() === 'error' || m.type() === 'warning') && !/document\.write/.test(m.text())) errors.push(`[${scheme} ${viewport.width}] ${m.type()}: ${m.text().slice(0, 300)}`); });
  page.on('pageerror', e => errors.push(`[${scheme} ${viewport.width}] pageerror: ${e.message}`));
  page.on('requestfailed', r => errors.push(`[${scheme} ${viewport.width}] requestfailed: ${r.url()} ${r.failure() && r.failure().errorText}`));
  await page.setContent(wrapped, { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForFunction(() => window.GALLERY, null, { timeout: 30000 });
  await page.waitForTimeout(400);
  return { ctx, page };
}
const { page, ctx } = await open({ width: 1440, height: 900 }, 'light');
const ids = args.length ? args : await page.evaluate(() => Object.keys(window.KIN.concepts));
const tiles = [];
for (const id of ids) {
  for (const pose of POSES) {
    const info = await page.evaluate(([id, pose]) => {
      window.GALLERY.select(id); const k = window.GALLERY.keyFrame[pose]; window.GALLERY.setFrame((k || 0) + 3);
      return { loop: document.getElementById('loop-text').textContent, detail: document.getElementById('loop-detail').textContent };
    }, [id, pose]);
    await page.waitForTimeout(150);
    const f = path.join(OUT, `${id}__${pose}.png`);
    await page.locator('#stage').screenshot({ path: f });
    tiles.push({ id, pose, f, info });
  }
}
await page.screenshot({ path: path.join(OUT, 'page_desktop_light.png') });
await ctx.close();
const d = await open({ width: 1440, height: 900 }, 'dark');
await d.page.evaluate(() => { window.GALLERY.setFrame(window.GALLERY.keyFrame.overhead + 3); });
await d.page.screenshot({ path: path.join(OUT, 'page_desktop_dark.png') });
const wide = await d.page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
await d.ctx.close();
const m = await open({ width: 400, height: 860 }, 'light');
await m.page.screenshot({ path: path.join(OUT, 'page_phone_light.png'), fullPage: true });
const wideM = await m.page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
await m.page.click('#mode-timeline'); await m.page.waitForTimeout(300);
await m.page.screenshot({ path: path.join(OUT, 'page_phone_timeline.png'), fullPage: true });
await m.ctx.close();

// contact sheet: one row per concept, one column per pose
const cols = POSES.length, sheet = await browser.newPage({ viewport: { width: 520 * cols + 40, height: 600 } });
const cell = t => `<figure><img src="data:image/png;base64,${fs.readFileSync(t.f).toString('base64')}"><figcaption><b>${t.id}</b> · ${t.pose} · ${t.info.loop}<br><small>${t.info.detail}</small></figcaption></figure>`;
await sheet.setContent(`<!doctype html><style>body{margin:16px;font:12px monospace;background:#fff}div{display:grid;grid-template-columns:repeat(${cols},500px);gap:12px}
img{width:500px;height:auto;border:1px solid #ccc}figure{margin:0}figcaption{padding:2px 0}</style><div>${tiles.map(cell).join('')}</div>`);
const sheetPath = path.join(OUT, 'contact_sheet.png');
await sheet.screenshot({ path: sheetPath, fullPage: true });
await browser.close();
console.log(JSON.stringify({ contact_sheet: sheetPath, tiles: tiles.map(t => ({ id: t.id, pose: t.pose, loop: t.info.loop, detail: t.info.detail })),
  horizontal_scroll: { desktop_dark: wide, phone: wideM }, console_errors: errors }, null, 1));
