/* Built CAD tab: every judged requirement over time (small multiples on one time axis), yes/no requirements as strips,
   and the GPU search evaluator's own estimates. The 3-D reach view is reach3d.js. */
(function () {
  const X = window.EXO, el = X.el, mark = X.mark;
  const MINIS = [
    ['R1', 'Skin 2-14 mm from the metal', 'hi', 'pct'], ['R1-aim', 'Skin 2-10 mm (the 1 cm aim)', 'hi', 'pct'], ['R3', 'Follows the arm', 'hi', 'pct'],
    ['R4', 'Overhead works', 'hi', 'pct'], ['R16', 'Everyday arm poses reached', 'hi', 'pct'], ['R2', 'No part enters the body', 'lo', 'mm'],
    ['R6', 'No interference between moving parts', 'lo', 'mm'], ['R8', 'Custom-part mass', 'lo', 'g'], ['R9', 'Strength safety factor (FEA)', 'hi', ''],
    ['R10', 'Base slip on the scapula', 'lo', 'mm'], ['R11', 'Pressure the exo adds on the cuff', 'lo', 'kPa']];
  const BOOLS = [['R7', 'Every custom part is one valid solid'], ['R17', 'Moves freely unpowered']];
  let show4 = false;
  const btn4 = document.getElementById('cad-show4');
  btn4.addEventListener('click', () => { show4 = !show4; btn4.setAttribute('aria-pressed', String(show4)); X.tabs.cad(); });
  const fmtV = (v, u) => (v === null || v === undefined ? '–' : u === 'pct' ? X.pct(v) : d3.format(v < 10 ? '.2~f' : '.1~f')(v) + (u ? ' ' + u : ''));
  const opTxt = (op) => (op === '>=' ? '≥' : op === '<=' ? '≤' : '=');

  function minis() {
    const grid = document.getElementById('cad-grid');
    const st = X.st('cad');
    grid.classList.toggle('dash-skeleton', st === 'loading');
    grid.querySelectorAll(':scope > .sw-msg').forEach((e) => e.remove());
    const C = X.rows('cad').filter((c) => show4 || c.dof === 3);
    if (st !== 'ok' || !C.length) {
      grid.querySelectorAll('.sw-mini').forEach((e) => e.remove());
      if (st !== 'loading') grid.appendChild(el('div', st === 'ok' ? 'sw-msg' : 'sw-msg sw-failed', st === 'ok' ? 'No judged design yet.' : 'Failed to load'));
      return;
    }
    const xd = X.timeDomain(C.map((c) => X.date(c.time)));
    MINIS.forEach(([rid, title, dir, unit]) => {
      let card = document.getElementById('cad-' + rid);
      if (!card) {
        card = el('div', 'sw-mini'); card.id = 'cad-' + rid;
        const h = el('div', 'sw-mini-head'); const t = el('h3', 'sw-mini-title'); t.append(el('span', 'sw-req', rid), document.createTextNode(title)); h.appendChild(t);
        h.appendChild(el('span', 'sw-dir', dir === 'hi' ? '↑ higher is better' : '↓ lower is better'));
        card.appendChild(h); card.appendChild(el('div', 'sw-stats')); const ch = el('div', 'sw-mchart'); card.appendChild(ch);
        grid.appendChild(card);
      }
      const rows = C.filter((c) => c.req === rid).sort((a, b) => (a.time < b.time ? -1 : a.time > b.time ? 1 : 0));
      const stats = card.querySelector('.sw-stats'), ch = card.querySelector('.sw-mchart');
      stats.replaceChildren();
      const any = X.rows('cad').find((c) => c.req === rid);
      const thr = any ? any.threshold : null, op = any ? any.op : '';
      if (!rows.length) { X.ready(ch, 'ok', 'Not judged yet' + (thr !== null ? ` (pass ${opTxt(op)} ${fmtV(thr, unit)})` : '')); return; }
      const r3 = rows.filter((c) => c.dof === 3), latest = (r3.length ? r3 : rows)[(r3.length ? r3 : rows).length - 1];
      const cur = r3.filter((c) => c.rules === 'current');
      const best = cur.length ? cur.reduce((a, c) => ((dir === 'hi' ? c.value > a.value : c.value < a.value) ? c : a)) : null;
      const stat = (label, c) => {
        const s = el('div', 'sw-stat'); if (c) s.dataset.ok = c.ok ? '1' : '0';
        s.appendChild(c ? mark(el('b', null, fmtV(c.value, unit)), 'cad', 'value', `design=${X.enc(c.design)}&req=${X.enc(rid)}`) : el('b', null, '–'));
        s.appendChild(el('span', null, label + (c ? ' · ' + X.short(c.design, 26) : ''))); stats.appendChild(s);
      };
      stat('latest', latest); stat('best, current rules', best);
      const ts = el('div', 'sw-stat'); ts.appendChild(el('b', null, (thr !== null ? opTxt(op) + ' ' + fmtV(thr, unit) : '–'))); ts.appendChild(el('span', null, 'pass')); stats.appendChild(ts);
      if (!X.ready(ch, 'ok', null)) return;
      const vals = rows.map((c) => c.value);
      let dom;
      if (unit === 'pct') dom = [0, 1];
      else { const hi = Math.max(thr !== null ? thr * (dir === 'lo' ? 4 : 1.4) : 1, d3.quantile(vals.slice().sort(d3.ascending), 0.75) * 1.15); dom = [0, hi]; }
      let run = null; const steps = [];
      r3.forEach((c) => { if (run === null || (dir === 'hi' ? c.value > run : c.value < run)) { run = c.value; steps.push({ t: X.date(c.time), v: c.value }); } });
      const dots = rows.map((c) => ({ t: X.date(c.time), v: c.value, r: 3.5, shape: c.level === 'Full CAD' ? 'circle' : 'square',
        fill: c.level === 'Full CAD' ? (c.dof === 3 ? 'var(--color-fg)' : 'var(--cds-chart-muted)') : 'none', stroke: c.dof === 3 ? 'var(--color-fg)' : 'var(--cds-chart-muted)',
        opacity: c.rules === 'older' ? 0.35 : 1, head: X.tUTC(X.date(c.time)),
        tip: [c.design, [rid, fmtV(c.value, unit)], ['pass', c.ok ? 'yes' : 'no'], ['level', c.level + ', ' + c.dof + ' DOF'], ['judging rules', c.rules], ['source', c.src]] }));
      X.timeChart(ch, { H: 170, x: xd, y: { domain: dom, fmt: unit === 'pct' ? d3.format('.0%') : d3.format('~g') },
        refs: thr !== null && thr >= dom[0] && thr <= dom[1] ? [{ v: thr, label: 'pass', cls: 'sw-tgt' }] : [],
        lines: [{ pts: steps, color: X.acc(), width: 2, extend: true }], dots });
    });
    X.key(document.getElementById('cad-key'), [['line', X.acc(), 'best 3-DOF so far'], ['dot', 'var(--color-fg)', 'full CAD'], ['square', 'var(--color-fg)', 'keep-out CAD'],
      show4 ? ['dot', 'var(--cds-chart-muted)', '4 DOF (never joined to the 3-DOF line)'] : null, ['dash', 'var(--color-ok)', 'pass threshold'], ['tri', 'var(--color-fg)', 'off the scale (hover for the value)']]);
  }

  function bools() {
    const box = document.getElementById('cad-bools');
    box.replaceChildren();
    const st = X.st('cad');
    box.classList.toggle('dash-skeleton', st === 'loading');
    if (st !== 'ok') { if (st !== 'loading') box.appendChild(el('div', 'sw-msg sw-failed', 'Failed to load')); return; }
    const C = X.rows('cad').filter((c) => show4 || c.dof === 3);
    BOOLS.forEach(([rid, title]) => {
      box.appendChild(el('div', 'sw-strip-h', rid + ' ' + title + ' (yes / no, oldest first)'));
      const row = el('div', 'sw-strip-row');
      const rs = C.filter((c) => c.req === rid).sort((a, b) => (a.time < b.time ? -1 : 1));
      if (!rs.length) row.appendChild(el('span', 'sw-empty', 'not judged yet'));
      rs.forEach((c) => {
        const chip = el('span', 'sw-yn'); chip.dataset.v = c.value ? 'yes' : 'no'; chip.dataset.dof = String(c.dof);
        chip.appendChild(el('b', null, c.value ? 'yes' : 'no'));
        chip.appendChild(el('small', null, X.short(c.design, 30) + ' · ' + d3.utcFormat('%b %-d %H:%M')(new Date(c.time))));
        row.appendChild(chip);
      });
      box.appendChild(row);
    });
  }

  function gpu() {
    const grid = document.getElementById('gpu-grid');
    const st = X.st('gpu_evals', 'gpu_searches');
    grid.classList.toggle('dash-skeleton', st === 'loading');
    grid.querySelectorAll(':scope > .sw-msg').forEach((e) => e.remove());
    const E = X.rows('gpu_evals').filter((r) => show4 || r.dof === 3), S = X.rows('gpu_searches').filter((r) => show4 || r.dof === 3 || r.dof === null);
    if (st !== 'ok' || (!E.length && !S.length)) {
      grid.replaceChildren();
      if (st !== 'loading') grid.appendChild(el('div', st === 'ok' ? 'sw-msg' : 'sw-msg sw-failed', st === 'ok' ? 'No GPU search results yet.' : 'Failed to load'));
      return;
    }
    const xd = X.timeDomain(E.map((r) => X.date(r.time)).concat(S.map((r) => X.date(r.time))));
    const specs = [
      ['gpu-ib', 'Evaluator in-band 14 mm', E, 'inband14', 0.9, (r) => [r.candidate, ['in-band 14', X.pct(r.inband14)], ['follow', X.pct(r.follow)], ['workspace', X.pct(r.workspace)], ['maps', r.maps]]],
      ['gpu-ws', 'Evaluator workspace followed', E, 'workspace', 0.9, (r) => [r.candidate, ['workspace', X.pct(r.workspace)], ['in-band 14', X.pct(r.inband14)], ['overhead follow', X.pct(r.overhead_follow)]]],
      ['gpu-fit', 'Search job final fitness', S, 'fit', null, (r) => ['search ' + r.search + ', job ' + r.job, ['fitness', d3.format('.3f')(r.fit)], ['follow', X.pct(r.follow)], ['evaluations', d3.format(',')(r.evals || 0)], ['minutes', d3.format('.0f')((r.secs || 0) / 60)], ['device', r.device]]]];
    specs.forEach(([id, title, rows, f, thr, tipf]) => {
      let card = document.getElementById(id);
      if (!card) {
        card = el('div', 'sw-mini'); card.id = id;
        const h = el('div', 'sw-mini-head'); h.appendChild(el('h3', 'sw-mini-title', title)); card.appendChild(h);
        card.appendChild(el('div', 'sw-stats')); card.appendChild(el('div', 'sw-mchart')); grid.appendChild(card);
      }
      const ch = card.querySelector('.sw-mchart'), stats = card.querySelector('.sw-stats');
      stats.replaceChildren();
      const rs = rows.filter((r) => r[f] !== null).sort((a, b) => (a.time < b.time ? -1 : 1));
      if (!rs.length) { X.ready(ch, 'ok', 'No results yet.'); return; }
      const best = rs.reduce((a, r) => (r[f] > a[f] ? r : a));
      const ds = id === 'gpu-fit' ? 'gpu_searches' : 'gpu_evals';
      const s = el('div', 'sw-stat');
      s.appendChild(mark(el('b', null, f === 'fit' ? d3.format('.3f')(best[f]) : X.pct(best[f])), ds, f, id === 'gpu-fit' ? `search=${X.enc(best.search)}&job=${best.job}` : `candidate=${X.enc(best.candidate)}&time=${X.enc(best.time)}`));
      s.appendChild(el('span', null, 'best · ' + X.short(id === 'gpu-fit' ? 'search ' + best.search : best.candidate, 30))); stats.appendChild(s);
      const n = el('div', 'sw-stat'); n.appendChild(el('b', null, String(rs.length))); n.appendChild(el('span', null, id === 'gpu-fit' ? 'jobs' : 'evaluations')); stats.appendChild(n);
      if (!X.ready(ch, 'ok', null)) return;
      let run = null; const steps = [];
      rs.forEach((r) => { if (run === null || r[f] > run) { run = r[f]; steps.push({ t: X.date(r.time), v: r[f] }); } });
      const top = f === 'fit' ? Math.max(0.1, d3.max(rs, (r) => r[f]) * 1.15) : 1;
      X.timeChart(ch, { H: 170, x: xd, y: { domain: [0, top], fmt: f === 'fit' ? d3.format('.2~f') : d3.format('.0%') },
        refs: thr !== null ? [{ v: thr, label: 'target 90%', cls: 'sw-tgt' }] : [],
        lines: [{ pts: steps, color: X.acc(), width: 2, extend: true }],
        dots: rs.map((r) => ({ t: X.date(r.time), v: r[f], r: 3, fill: r.dof === 3 ? 'var(--color-fg)' : 'var(--cds-chart-muted)', opacity: 0.75, head: X.tUTC(X.date(r.time)) + ' (commit)', tip: tipf(r) })) });
    });
    X.key(document.getElementById('gpu-key'), [['line', X.acc(), 'best so far'], ['dot', 'var(--color-fg)', '3-DOF candidate'], show4 ? ['dot', 'var(--cds-chart-muted)', '4-DOF candidate'] : null, ['dash', 'var(--color-ok)', '90% target of the matching requirement (R1, R16)']]);
  }

  X.tabs.cad = () => { minis(); bools(); gpu(); if (window.__swDraw3d) window.__swDraw3d(); };
})();
