// Render the dashboard with the type's real runtime (harness/serve.py) and screenshot every tab.
//   node docs/dashboard/harness/shot.mjs [out dir] [--status ok|loading|error] [--data DIR] [--tabs leader,bench] [--widths 1280,400] [--themes light,dark]
// Prints, per shot: page errors and console errors/warnings (the platform-only serif font, served at /_runtime/ on
// claude.ai, cannot load offline and is reported once as 'env'), horizontal overflow, and what the runtime itself
// wrote to the reader's runs document (flagged marks, code errors).
import { spawn } from 'node:child_process';
import { createRequire } from 'node:module';
import path from 'node:path';
import fs from 'node:fs';
import net from 'node:net';
const require = createRequire(import.meta.url);
let pw;
try { pw = require('playwright'); } catch { pw = require('/opt/node22/lib/node_modules/playwright'); }
const here = path.dirname(new URL(import.meta.url).pathname);
const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const out = args[0] && !args[0].startsWith('--') ? args[0] : '/tmp/dash_shots';
const status = opt('--status', 'ok'), tag = opt('--tag', status === 'ok' ? '' : status + '_');
const tabs = opt('--tabs', 'leader,bench,cad,reqs,log').split(','), widths = opt('--widths', '1280,400').split(',').map(Number), themes = opt('--themes', 'light,dark').split(',');
fs.mkdirSync(out, { recursive: true });
const port = await new Promise((res) => { const s = net.createServer(); s.listen(0, () => { const p = s.address().port; s.close(() => res(p)); }); });
const srvArgs = [path.join(here, 'serve.py'), '--port', String(port), '--status', status];
if (opt('--data')) srvArgs.push('--data', opt('--data'));
const srv = spawn('python3', srvArgs, { stdio: ['ignore', 'pipe', 'inherit'] });
await new Promise((res) => srv.stdout.once('data', res));
const browser = await pw.chromium.launch();
let envNoted = false, total = 0;
for (const theme of themes) for (const w of widths) for (const tab of tabs) {
  const ctx = await browser.newContext({ viewport: { width: w, height: 900 }, colorScheme: theme === 'dark' ? 'dark' : 'light' });
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', (e) => errs.push('pageerror: ' + e.message));
  p.on('console', (m) => {
    const t = m.text();
    if (/serif face did not load|_runtime\/|Failed to load resource: the server responded with a status of 404/.test(t)) { if (!envNoted) { console.log('env (offline only):', t.slice(0, 120)); envNoted = true; } return; }
    if (m.type() === 'error' || m.type() === 'warning') errs.push(m.type() + ': ' + t.slice(0, 300));
  });
  await p.goto(`http://127.0.0.1:${port}/#${tab}`);
  await p.evaluate((th) => document.documentElement.setAttribute('data-theme', th), theme);
  await p.waitForTimeout(status === 'loading' ? 2500 : 3500);
  const btn = await p.$(`#tab-${tab}`); if (btn) { await btn.click(); await p.waitForTimeout(1200); }
  const f = path.join(out, `${tag}${tab}_${w}_${theme}.png`);
  // the runtime scrolls the page inside its own content box: grow the viewport to that box's full height first
  const fullH = await p.evaluate(() => { const c = document.querySelector('[data-appifact-content]'); return c ? Math.ceil(c.scrollHeight + c.getBoundingClientRect().top) : document.documentElement.scrollHeight; });
  await p.setViewportSize({ width: w, height: Math.min(Math.max(900, fullH + 24), 16000) });
  await p.waitForTimeout(700);
  await p.screenshot({ path: f, fullPage: true });
  const info = await p.evaluate(() => {
    const runs = window.__store && [...window.__store].find(([k]) => k.endsWith('/runs'));
    const r = runs ? runs[1] : null;
    const c = document.querySelector('[data-appifact-content]');
    return { overflow: Math.max(document.documentElement.scrollWidth - innerWidth, c ? c.scrollWidth - c.clientWidth : 0), h: document.documentElement.scrollHeight,
      flagged: r ? r.flagged || 0 : null, marks: r && r.marks ? r.marks.slice(0, 6) : [], codeErrors: r && r.errors ? r.errors : [],
      sources: r && r.datasets ? Object.fromEntries(Object.entries(r.datasets).map(([k, v]) => [k, v.status + (v.rows !== undefined ? ':' + v.rows : '')])) : null };
  });
  total += errs.length + (info.codeErrors || []).length;
  console.log(path.basename(f), JSON.stringify({ overflow: info.overflow, h: info.h, flagged: info.flagged }), errs.length ? '\n  ' + errs.join('\n  ') : 'no console errors');
  if (info.marks.length) console.log('  flagged marks:', JSON.stringify(info.marks));
  if (info.codeErrors.length) console.log('  code errors:', JSON.stringify(info.codeErrors));
  await ctx.close();
}
await browser.close();
srv.kill();
console.log('TOTAL console/page/code errors:', total);
