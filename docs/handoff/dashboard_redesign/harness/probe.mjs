// node probe.mjs <base url> <out dir>: hover checks + loading/error states + mark audit
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
const [base, out] = process.argv.slice(2);
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1400, height: 1000 } });
const errs = []; p.on('pageerror', (e) => errs.push(e.message));
await p.goto(base + '/index.html'); await p.waitForTimeout(800);
// hover the leader's ring in the record chart
const box = await p.locator('#record-chart svg').boundingBox();
await p.locator('#record-chart').scrollIntoViewIfNeeded();
const pt = await p.evaluate(() => { const c = [...document.querySelectorAll('#record-chart svg circle')].find((e) => e.__data__ && e.__data__.lead); const r = c.getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2]; });
await p.mouse.move(pt[0], pt[1]); await p.waitForTimeout(300);
await p.locator('#record-card').screenshot({ path: out + '/hover_record.png' });
console.log('tip:', await p.evaluate(() => document.querySelector('.sw-tip').innerText.replace(/\n/g, ' | ')));
// metric switch
await p.click('#record-metric button[data-m="inband14"]'); await p.waitForTimeout(300);
await p.locator('#record-card').screenshot({ path: out + '/record_inband14.png' });
// tuning hover
await p.locator('#tuning-chart').scrollIntoViewIfNeeded(); const tb = await p.locator('#tuning-chart svg').boundingBox(); await p.mouse.move(tb.x + tb.width * 0.5, tb.y + tb.height * 0.7); await p.waitForTimeout(300);
console.log('tuning tip:', await p.evaluate(() => (document.querySelector('.sw-tip').hidden ? '(none)' : document.querySelector('.sw-tip').innerText.replace(/\n/g, ' | '))));
// sort table by reach, search
await p.click('#table th[data-field="reach"] button'); await p.fill('#table-search', 'verified'); await p.waitForTimeout(300);
console.log('table:', await p.evaluate(() => document.getElementById('table-count').textContent + ' first=' + document.querySelector('#table tbody tr').dataset.key));
// mark audit: every data-where / data-row mark resolves to a row
const audit = await p.evaluate(() => {
  const bad = [];
  document.querySelectorAll('[data-source][data-field]').forEach((e) => {
    const src = e.getAttribute('data-source'), f = e.getAttribute('data-field'), d = dash.data(src);
    if (d.status !== 'ok') return;
    const rows = d.data; let row = null;
    if (e.hasAttribute('data-row')) row = rows[+e.getAttribute('data-row')];
    else if (e.hasAttribute('data-where')) { const w = new URLSearchParams(e.getAttribute('data-where')); row = rows.find((r) => [...w].every(([k, v]) => String(r[k]) === v)); }
    else if (e.tagName !== 'TH' && e.tagName !== 'SELECT') return;
    if (e.tagName === 'TH') { if (!(f in (rows[0] || {}))) bad.push('th ' + src + '.' + f); return; }
    if (!row) bad.push('no row: ' + src + ' ' + f + ' ' + (e.getAttribute('data-where') || e.getAttribute('data-row')));
    else if (!(f in row)) bad.push('no field: ' + src + '.' + f);
  });
  return { n: document.querySelectorAll('[data-source]').length, bad };
});
console.log('marks', audit.n, 'problems', JSON.stringify(audit.bad.slice(0, 10)));
for (const tab of ['cad']) { await p.click('#tab-' + tab); await p.waitForTimeout(500); }
 
const cpt = await p.evaluate(() => { const c = document.querySelector('#cad-r1_14 svg circle[r="4"]'); const r = c.getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2]; });
await p.mouse.move(cpt[0], cpt[1]); await p.waitForTimeout(300);
console.log('cad tip:', await p.evaluate(() => document.querySelector('.sw-tip').innerText.replace(/\n/g, ' | ')));
await p.click('#cad-show4'); await p.click('#cad-mode button[data-m="level"]'); await p.waitForTimeout(400);
await p.locator('#cadtime-card').screenshot({ path: out + '/cad_level_4dof.png' });
for (const st of ['loading', 'error']) {
  const q = await b.newPage({ viewport: { width: 1000, height: 900 } }); const e2 = []; q.on('pageerror', (e) => e2.push(e.message));
  await q.goto(base + '/index.html?status=' + st); await q.waitForTimeout(600);
  await q.screenshot({ path: out + '/state_' + st + '.png', fullPage: false }); console.log(st, e2.length ? e2 : 'no errors');
  await q.click('#tab-cad'); await q.waitForTimeout(300); await q.click('#tab-log'); await q.waitForTimeout(300); console.log(st, 'tabs', e2.length ? e2 : 'no errors');
}
console.log('errors', errs);
await b.close();
