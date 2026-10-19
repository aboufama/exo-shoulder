// Cheap local motion preview (no paid compute): plays a film plan in pipeline/full-exo/film.html (the same plan, matte
// black faceless mannequin and part materials the Blender film uses) in headless Chromium and saves PNG stills of chosen
// frames plus a low-res MP4 of the whole plan. Needs the viewer served: (cd pipeline/full-exo && python3 -m http.server 4199)
//
//   NODE_PATH=$(npm root -g) node tools/preview_film.mjs <film plan, relative to full-exo> <out dir> [--port 4199]
//       [--frames 0,40,80] [--every 2] [--w 1280 --h 720] [--fps 15]
// --frames: stills (film frame numbers, default 6 evenly spaced per shot, 'none' = no stills); --every N: MP4 from every Nth frame (0 = no MP4)
import { createRequire } from 'node:module';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
const { chromium } = createRequire(import.meta.url)('playwright');                        // global install: NODE_PATH=$(npm root -g)

const args = process.argv.slice(2); const opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? args[i + 1] : d; };
const [plan, out] = args; if (!plan || !out) { console.error('usage: preview_film.mjs <plan> <out dir> [...]'); process.exit(1); }
const port = +opt('port', 4199), W = +opt('w', 1280), H = +opt('h', 720), every = +opt('every', 2), fps = +opt('fps', 15);
fs.mkdirSync(out, { recursive: true });
// three.js comes from the CDN: Chromium picks up the session's HTTPS_PROXY by itself (an explicit Playwright proxy gets 405)
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: W, height: H } });
page.on('pageerror', e => console.error('page error:', e.message));
const t0 = Date.now();
await page.goto(`http://localhost:${port}/film.html?film=${encodeURIComponent(plan)}`);
await page.waitForFunction(() => window.__film && window.__film.NF > 0, null, { timeout: 180000 });
await page.addStyleTag({ content: '.bar { display: none !important; }' });                   // keep the caption, hide the controls
const NF = await page.evaluate(() => window.__film.NF);
const shots = JSON.parse(fs.readFileSync(path.join('pipeline/full-exo', plan), 'utf8')).shots;
let frames = opt('frames', '');
if (frames === 'none') frames = [];
else if (frames) frames = frames.split(',').map(Number);
else { frames = []; let T = 0; for (const s of shots) { const n = s.f1 - s.f0 + 1; for (let k = 0; k < 6; k++) frames.push(T + Math.round(k * (n - 1) / 5)); T += n; } }
await page.evaluate(() => window.__film.stop && window.__film.stop());                       // software WebGL: no continuous render loop, one draw per frame
const go = async f => { await page.evaluate(f => { window.__film.go(f); window.__film.draw ? window.__film.draw() : null; }, f); };
for (const f of frames) { await go(f); await page.screenshot({ path: path.join(out, `still_${String(f).padStart(4, '0')}.png`), timeout: 180000 }); }
console.log(`${frames.length} stills of ${NF} frames in ${((Date.now() - t0) / 1000).toFixed(0)} s -> ${out}`);
if (every > 0) {
  const mp4 = path.join(out, 'preview.mp4');
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-', '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2',
                              '-c:v', 'libx264', '-crf', '23', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', mp4], { stdio: ['pipe', 'inherit', 'inherit'] });
  const t1 = Date.now(); let n = 0;
  for (let f = 0; f < NF; f += every) { await go(f); ff.stdin.write(await page.screenshot({ type: 'png', timeout: 180000 })); n++; }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
  console.log(`preview.mp4: ${n} frames (every ${every}, ${fps} fps = ${(n / fps).toFixed(1)} s) in ${((Date.now() - t1) / 1000).toFixed(0)} s -> ${mp4}`);
}
await browser.close();
