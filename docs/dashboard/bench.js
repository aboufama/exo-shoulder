/* Concept bench tab: optimisation curves per morphology, reach vs in-band scatter, pipeline funnel, the table. */
(function () {
  const X = window.EXO, el = X.el, mark = X.mark;
  const DROPPED = ['dead', 'refuted', 'duplicate'];
  const evidence = (m) => (m.v_gap !== null ? { kind: 'verified', gap: m.v_gap, reach: m.v_reach ?? m.reach, ib: m.v_inband14 ?? m.inband14, follow: m.v_follow ?? m.follow, contact: m.v_contact ?? m.contact }
    : m.gap !== null ? { kind: 'claimed', gap: m.gap, reach: m.reach, ib: m.inband14, follow: m.follow, contact: m.contact }
      : m.sweep_gap !== null ? { kind: 'sweep', gap: m.sweep_gap, reach: m.sweep_reach, ib: m.sweep_inband14, follow: m.sweep_follow, contact: m.sweep_contact } : null);
  X.evidence = evidence;

  function curves() {
    const box = document.getElementById('curves-chart');
    const st = X.st('sweeps', 'morphs');
    const S = X.rows('sweeps').filter((s) => s.best_gap !== null), M = X.rows('morphs');
    const base = (M.find((m) => m.is_baseline) || {}).gap ?? null;
    if (!X.ready(box, st, S.length ? null : 'No morphology has a measured configuration yet. Each agent first builds and checks its model; its curve appears here with its first bench result (usually within the hour of a restart).')) { X.key(document.getElementById('curves-key'), []); return; }
    const byId = d3.group(S, (s) => s.id), mm = new Map(M.map((m) => [m.id, m]));
    const ids = [...byId.keys()].sort((a, b) => d3.min(byId.get(a), (s) => s.best_gap) - d3.min(byId.get(b), (s) => s.best_gap));
    const xd = X.timeDomain(S.map((s) => X.date(s.t)));
    const top = Math.min(1000, Math.max(base !== null ? base * 2 : 100, d3.max(S, (s) => s.best_gap)));
    const ticks = [0, 10, 20, 30, 50, 70, 100, 150, 200, 300, 500, 1000].filter((v) => v <= top * 1.02);
    let ci = 0;
    const color = new Map(ids.map((id) => {
      const best = d3.min(byId.get(id), (s) => s.best_gap), m = mm.get(id) || {};
      return [id, base !== null && best < base && !DROPPED.includes(m.status) && ci < 8 ? dash.colors[ci++] : 'var(--cds-chart-muted)'];
    }));
    const lines = [], dots = [], ends = [];
    ids.slice().reverse().forEach((id) => {
      const rows = byId.get(id).slice().sort((a, b) => (a.t < b.t ? -1 : 1)), m = mm.get(id) || { name: id, status: '' };
      const steps = rows.filter((s, i) => i === 0 || s.best_gap < rows[i - 1].best_gap);
      const c = color.get(id), dead = DROPPED.includes(m.status);
      lines.push({ pts: steps.map((s) => ({ t: X.date(s.t), v: s.best_gap })).concat([{ t: X.date(rows[rows.length - 1].t), v: rows[rows.length - 1].best_gap }]), color: c, width: c.startsWith('var(--cds') ? 1.5 : 2.25, dash: dead ? '5 4' : null, opacity: dead ? 0.7 : 1 });
      steps.forEach((s) => dots.push({ t: X.date(s.t), v: s.best_gap, r: 2.5, fill: c, head: X.tUTC(X.date(s.t)), tip: [m.name, ['best gap so far', X.gapf(s.best_gap)], ['configurations so far', String(rows.filter((r) => r.t <= s.t).length)], ['status', m.status]] }));
      const last = rows[rows.length - 1];
      ends.push({ v: last.best_gap, text: X.short(m.name, 26) + ' ' + X.f1(last.best_gap), color: c.startsWith('var(--cds') ? null : c });
    });
    if (base !== null) ends.push({ v: base, text: '3R baseline ' + X.gapf(base) });
    X.timeChart(box, {
      H: Math.max(320, Math.min(520, 120 + ids.length * 16)), x: xd,
      y: { domain: [0, top], scale: 'symlog', c: 10, ticks, fmt: d3.format('~g'), label: 'best gap so far (compressed above 30)' },
      refs: [base !== null ? { v: base, label: '3R baseline|' + X.gapf(base), cls: 'sw-ref' } : null, { v: 0, label: 'target 0', cls: 'sw-tgt' }].filter(Boolean),
      lines, dots, ends: box.clientWidth > 520 ? ends : []
    });
    X.key(document.getElementById('curves-key'), [['line', dash.colors[0], 'below the 3R baseline (one colour each)'], ['line', 'var(--cds-chart-muted)', 'at or above it'],
      ['dash', 'var(--cds-chart-muted)', 'dropped or refuted'], ['dash', 'var(--cds-chart-reference)', '3R baseline'], box.clientWidth > 520 ? null : ['small', 'var(--cds-chart-muted)', 'tap a line for its name']]);
  }

  function lands() {
    const box = document.getElementById('lands-chart');
    const st = X.st('morphs');
    const M = X.rows('morphs');
    const pts = M.filter((m) => !m.is_baseline && m.status !== 'duplicate').map((m) => ({ m, e: evidence(m) })).filter((p) => p.e && p.e.reach !== null && p.e.ib !== null);
    const base = M.find((m) => m.is_baseline);
    if (!X.ready(box, st, pts.length || base ? null : 'No morphology measured yet.')) { X.key(document.getElementById('lands-key'), []); return; }
    const { svg, W, H } = X.frame(box, 300);
    const ml = 44, mr = 14, mt = 26, mb = 40;
    const x = d3.scaleLinear([0, 1], [ml, W - mr]), y = d3.scaleLinear([0, 1], [H - mb, mt]);
    const acc = X.acc(), bg = base ? base.gap : null;
    svg.append('rect').attr('x', x(0.9)).attr('y', y(1)).attr('width', x(1) - x(0.9)).attr('height', y(0.9) - y(1)).attr('fill', 'var(--color-ok)').attr('opacity', 0.18);
    svg.append('text').attr('class', 'sw-lab-m').attr('x', x(0.9) - 4).attr('y', y(1) + 10).attr('text-anchor', 'end').text('both targets');
    [0, 0.25, 0.5, 0.75, 1].forEach((v) => {
      svg.append('line').attr('class', 'sw-axis-line').attr('opacity', 0.35).attr('x1', ml).attr('x2', W - mr).attr('y1', y(v)).attr('y2', y(v));
      svg.append('text').attr('x', ml - 6).attr('y', y(v)).attr('dy', '0.32em').attr('text-anchor', 'end').text(d3.format('.0%')(v));
      svg.append('text').attr('x', x(v)).attr('y', H - mb + 16).attr('text-anchor', 'middle').text(d3.format('.0%')(v));
    });
    svg.append('text').attr('x', W - mr).attr('y', H - 6).attr('text-anchor', 'end').text('reach (share of workspace poses) →');
    svg.append('text').attr('x', ml).attr('y', 10).text('↑ in-band 14 mm (share of skin 2-14 mm)');
    const pick = [];
    const add = (px, py, d) => pick.push({ px, py, d });
    if (base && base.reach !== null) {
      const px = x(base.reach), py = y(base.inband14);
      svg.append('path').attr('d', `M${px},${py - 7}L${px + 7},${py}L${px},${py + 7}L${px - 7},${py}Z`).attr('fill', 'none').attr('stroke', 'var(--color-fg)').attr('stroke-width', 1.75);
      svg.append('text').attr('class', 'sw-lab').attr('x', px + 10).attr('y', py + 4).text('3R baseline');
      add(px, py, ['3R baseline', ['gap', X.gapf(base.gap)], ['reach', X.pct(base.reach)], ['in-band 14', X.pct(base.inband14)], ['follow', X.pct(base.follow)], ['contact', X.pct(base.contact)]]);
    }
    const ranked = pts.slice().sort((a, b) => a.e.gap - b.e.gap);
    ranked.slice().reverse().forEach(({ m, e }) => {
      const px = x(Math.max(0, Math.min(1, e.reach))), py = y(Math.max(0, Math.min(1, e.ib)));
      const win = bg !== null && e.gap < bg && !DROPPED.includes(m.status), c = win ? acc : 'var(--cds-chart-muted)';
      const r = e.kind === 'sweep' ? 3 : 5;
      svg.append('circle').attr('cx', px).attr('cy', py).attr('r', r).attr('fill', e.kind === 'claimed' ? 'var(--color-panel)' : c).attr('stroke', c).attr('stroke-width', e.kind === 'claimed' ? 2 : 0).attr('opacity', DROPPED.includes(m.status) ? 0.5 : 1);
      add(px, py, [m.name, ['evidence', e.kind === 'sweep' ? 'best sweep configuration' : e.kind], ['gap', X.gapf(e.gap)], ['reach', X.pct(e.reach)], ['in-band 14', X.pct(e.ib)], ['follow', X.pct(e.follow)], ['contact', X.pct(e.contact)], ['status', m.status]]);
    });
    const used = base && base.reach !== null ? [{ x: x(base.reach) + 10, y: y(base.inband14) + 4, w: 70 }] : [];
    ranked.slice(0, 3).forEach(({ m, e }) => {
      const px = x(Math.max(0, Math.min(1, e.reach))), py = y(Math.max(0, Math.min(1, e.ib))), t = X.short(m.name, 28), w = X.measure(svg, t, 'sw-lab');
      let lx = px + 8 + w > W - mr ? px - 8 - w : px + 8, ly = py - 8;
      let n = 0; while (n++ < 6 && used.some((u) => Math.abs(u.y - ly) < 13 && lx < u.x + u.w && lx + w > u.x)) ly += 14;
      used.push({ x: lx, y: ly, w });
      svg.append('text').attr('class', 'sw-lab').attr('x', lx).attr('y', ly).text(t);
    });
    const tip = X.tip(box), del = d3.Delaunay.from(pick, (p) => p.px, (p) => p.py);
    svg.on('pointermove', (ev) => {
      const [mx, my] = d3.pointer(ev), p = pick[del.find(mx, my)];
      if (!p || Math.hypot(p.px - mx, p.py - my) > 24) { tip.hide(); return; }
      const s = box.clientWidth / W; tip.show(p.px * s, p.py * s, null, p.d);
    }).on('pointerleave', () => tip.hide());
    X.key(document.getElementById('lands-key'), [['dot', acc, 'verified, beats the baseline'], ['ring', acc, 'claimed'], ['small', acc, 'best sweep config'], ['dot', 'var(--cds-chart-muted)', 'at or above the baseline gap'], ['box', 'var(--color-ok)', 'targets: 90% / 90%']]);
  }

  function funnel() {
    const box = document.getElementById('funnel-bars');
    box.replaceChildren();
    const st = X.st('funnel');
    box.classList.toggle('dash-skeleton', st === 'loading');
    if (st !== 'ok') { if (st !== 'loading') box.appendChild(el('div', 'sw-msg sw-failed', 'Failed to load')); return; }
    const F = X.rows('funnel'), top = Math.max(1, ...F.map((r) => r.n));
    let worst = -1, wi = -1;
    F.forEach((r, i) => { if (i && F[i - 1].n > 0) { const lost = (F[i - 1].n - r.n) / F[i - 1].n; if (lost > worst && F[i - 1].n - r.n > 0) { worst = lost; wi = i; } } });
    const why = { ideated: 'in the catalogue', modelled: 'model built, sweeping', screened: 'claimed bench row', verified: 're-measured', GPU: 'GPU sweep', CAD: 'keep-out CAD built' };
    F.forEach((r, i) => {
      const row = el('div', 'sw-fun-row');
      const lab = el('div', 'sw-fun-label'); lab.appendChild(el('span', null, r.stage)); lab.appendChild(el('small', null, why[r.stage] || ''));
      const tr = el('div', 'sw-fun-track'), bar = el('div', 'sw-fun-bar');
      bar.style.width = (100 * r.n / top) + '%'; if (!r.n) bar.dataset.zero = '1';
      if (i === wi) bar.style.background = 'var(--cds-chart-status-critical)';
      tr.appendChild(bar);
      const n = mark(el('span', 'sw-fun-n', String(r.n)), 'funnel', 'n', 'stage=' + X.enc(r.stage));
      row.append(lab, tr, n);
      if (i && F[i - 1].n > 0) row.title = '';
      box.appendChild(row);
      if (i < F.length - 1 && r.n > 0) {
        const lost = r.n - F[i + 1].n;
        const s = el('div', 'sw-fun-row'); s.appendChild(el('span')); s.appendChild(el('small', 'sw-empty', lost > 0 ? `${lost} not yet past this step (${d3.format('.0%')(lost / r.n)})` : 'all moved on'));
        box.appendChild(s);
      }
    });
  }

  /* ---------- table */
  const COLS = [
    ['name', 'Morphology', 'txt', ''], ['status', 'Status', 'txt', ''], ['sweep_gap', 'Sweep best gap', 'gap', ''], ['gap', 'Claimed gap', 'gap', ''], ['v_gap', 'Verified gap', 'gap', ''],
    ['reach', 'Reach', 'pct', 'sw-hide-n'], ['v_reach', 'Reach, verified', 'pct', 'sw-hide-n'], ['inband14', 'In-band 14', 'pct', 'sw-hide-n'], ['v_inband14', 'In-band 14, verified', 'pct', 'sw-sec'],
    ['follow', 'Follow', 'pct', 'sw-sec'], ['contact', 'Contact', 'pct', 'sw-sec'], ['n_configs', 'Configs', 'int', 'sw-sec'], ['family', 'Family', 'txt', 'sw-sec'], ['lens', 'Lens', 'txt', 'sw-sec'],
    ['t_last', 'Last activity', 'time', 'sw-hide-n'], ['id', 'Id', 'txt', 'sw-sec']];
  let sortCol = null, sortDir = 1;
  const ORDER = ['cad', 'gpu', 'verified', 'screened', 'modelling', 'ideated', 'refuted', 'dead', 'duplicate'];
  const fmtCell = (v, t) => (v === null || v === undefined || v === '' ? '' : t === 'gap' ? X.gapf(v) : t === 'pct' ? X.pct(v) : t === 'time' ? d3.utcFormat('%b %-d %H:%M')(new Date(v)) : String(v));
  function table() {
    const tbl = document.getElementById('table'), thead = tbl.querySelector('thead'), tbody = tbl.querySelector('tbody');
    const st = X.st('morphs'), boxEl = document.getElementById('table-box');
    boxEl.classList.toggle('dash-skeleton', st === 'loading');
    boxEl.querySelectorAll('.sw-msg').forEach((e) => e.remove());
    if (st !== 'ok') { tbody.replaceChildren(); if (st !== 'loading') boxEl.appendChild(el('div', 'sw-msg sw-failed', 'Failed to load')); return; }
    const M = X.rows('morphs');
    const q = document.getElementById('table-search').value.trim().toLowerCase();
    if (!thead.children.length) {
      const tr = el('tr');
      COLS.forEach(([f, label, t, cls]) => {
        const th = el('th', (t === 'txt' ? '' : 'sw-num ') + cls); th.setAttribute('data-field', f);
        const b = el('button', null, label); b.type = 'button';
        b.addEventListener('click', () => { if (sortCol === f) sortDir = -sortDir; else { sortCol = f; sortDir = t === 'txt' || t === 'gap' ? 1 : -1; } table(); });
        th.appendChild(b); tr.appendChild(th);
      });
      thead.appendChild(tr);
    }
    thead.querySelectorAll('th').forEach((th) => th.setAttribute('aria-sort', th.getAttribute('data-field') === sortCol ? (sortDir > 0 ? 'ascending' : 'descending') : 'none'));
    let rows = M.filter((m) => !q || [m.name, m.id, m.family, m.lens, m.status, m.verdict].join(' ').toLowerCase().includes(q));
    const bestOf = (m) => { const e = evidence(m); return e ? e.gap : Infinity; };
    const cmp = (a, b) => {
      if (!sortCol) {
        const oa = ORDER.indexOf(a.status), ob = ORDER.indexOf(b.status);
        const ga = a.is_baseline ? a.gap : bestOf(a), gb = b.is_baseline ? b.gap : bestOf(b);
        if (DROPPED.includes(a.status) !== DROPPED.includes(b.status)) return DROPPED.includes(a.status) ? 1 : -1;
        return ga - gb || oa - ob || a.id.localeCompare(b.id);
      }
      let va = a[sortCol], vb = b[sortCol];
      if (a.is_baseline && sortCol === 'sweep_gap') va = a.gap;
      if (b.is_baseline && sortCol === 'sweep_gap') vb = b.gap;
      const na = va === null || va === undefined || va === '', nb = vb === null || vb === undefined || vb === '';
      if (na !== nb) return na ? 1 : -1;
      if (na) return a.id.localeCompare(b.id);
      return (typeof va === 'number' ? va - vb : String(va).localeCompare(String(vb))) * sortDir || a.id.localeCompare(b.id);
    };
    rows.sort(cmp);
    tbody.replaceChildren();
    const base = M.find((m) => m.is_baseline);
    rows.forEach((m) => {
      const tr = el('tr'); tr.setAttribute('data-key', m.id);
      if (m.is_baseline) tr.className = 'sw-base';
      const e = evidence(m);
      tr.dataset.c = m.is_baseline ? 'base' : DROPPED.includes(m.status) ? 'out' : e && base && e.gap < base.gap ? (e.kind === 'verified' ? 'win' : 'claim') : '';
      COLS.forEach(([f, , t, cls]) => {
        const td = el('td', (t === 'txt' ? '' : 'sw-num ') + cls + (f === 'name' ? ' sw-name' : f === 'id' ? ' sw-id' : ''));
        if (f === 'status') { const c = el('span', 'sw-chip', m.status); c.dataset.s = m.is_baseline ? 'base' : m.status; td.appendChild(c); }
        else { td.textContent = fmtCell(m[f], t); if (t === 'gap') td.classList.add('sw-gapv'); }
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
    document.getElementById('table-count').textContent = `${rows.length} of ${M.length} shown`;
  }
  document.getElementById('table-search').addEventListener('input', () => table());

  X.tabs.bench = () => { curves(); lands(); funnel(); table(); };
})();
