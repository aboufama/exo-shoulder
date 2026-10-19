// node shot.mjs <base url> <out dir> <tag>: each tab at 1400 and 420 px (full page) + dark at 1400; prints page errors
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
const [base, out, tag] = process.argv.slice(2);
const b = await chromium.launch();
for (const [w, theme] of [[1400, ''], [420, ''], [1400, 'dark']]) {
  for (const tab of ['swarm', 'cad', 'log']) {
    const p = await b.newPage({ viewport: { width: w, height: 1000 } });
    const errs = [];
    p.on('pageerror', (e) => errs.push('pageerror: ' + e.message));
    p.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') errs.push(m.type() + ': ' + m.text()); });
    await p.goto(`${base}/${theme ? 'dark' : 'index'}.html#${tab}`); await p.waitForTimeout(900);
    const btn = await p.$(`#tab-${tab}`); if (btn) { await btn.click(); await p.waitForTimeout(700); }
    const f = `${out}/${tag}_${tab}_${w}${theme ? '_dark' : ''}.png`;
    await p.screenshot({ path: f, fullPage: true });
    const info = await p.evaluate(() => ({ overflow: document.documentElement.scrollWidth - innerWidth, h: document.documentElement.scrollHeight, link: window.__link || '' }));
    console.log(f.split('/').pop(), JSON.stringify(info), errs.length ? '\n  ' + errs.join('\n  ') : 'no errors');
    await p.close();
  }
}
await b.close();
