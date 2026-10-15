/* Leader tab: the concept-bench leader against the 3R baseline and the target, headline figures, and the two records over time. */
(function () {
  const X = window.EXO, el = X.el, mark = X.mark;
  const LIVE = (m) => !m.is_baseline && !['dead', 'refuted', 'duplicate'].includes(m.status);

  function hero() {
    const box = document.getElementById('hero-body'), card = document.getElementById('hero-card');
    box.replaceChildren();
    const st = X.st('summary', 'morphs');
    box.classList.toggle('dash-skeleton', st === 'loading');
    if (st !== 'ok') { if (st !== 'loading') box.appendChild(el('div', 'sw-msg sw-failed', 'Failed to load')); return; }
    const s = X.rows('summary')[0] || {}, M = X.rows('morphs');
    const base = s.base_gap, win = s.ver_gap !== null && base !== null && s.ver_gap < base;
    card.dataset.win = win ? '1' : '0';
    const main = el('div', 'sw-hero-main'), side = el('div', 'sw-hero-side');
    box.append(main, side);
    const badges = el('div', 'sw-badges');
    main.appendChild(badges);
    if (s.ver_id) {
      badges.appendChild(el('span', 'sw-badge sw-badge-ok', 'verified'));
      if (win) badges.appendChild(el('span', 'sw-badge sw-badge-acc', 'beats the 3R baseline'));
      main.appendChild(mark(el('p', 'sw-hero-name', s.ver_name), 'summary', 'ver_name', 0));
      const row = el('div', 'sw-gaprow');
      const big = mark(el('span', 'sw-big', X.gapf(s.ver_gap)), 'summary', 'ver_gap', 0); big.dataset.win = win ? '1' : '0';
      const cap = el('span', 'sw-bigcap');
      cap.appendChild(el('span', null, 'gap, re-measured by the verifier'));
      const l2 = el('span'); l2.append(mark(el('b', win ? 'sw-acc' : null, X.gapf(Math.abs(s.ver_delta))), 'summary', 'ver_delta', 0), document.createTextNode(win ? ' below the 3R baseline' : ' above the 3R baseline'));
      cap.appendChild(l2);
      row.append(big, cap); main.appendChild(row);
    } else {
      badges.appendChild(el('span', 'sw-badge', 'no verified leader yet'));
      main.appendChild(el('p', 'sw-hero-name', 'No morphology has a verified bench result yet'));
      main.appendChild(el('p', 'sw-hero-sub', 'A result counts once the verifier re-measures the agent’s claim on the full bench. Until then the best evidence is below.'));
    }
    /* candidates that are not verified yet */
    const cands = [];
    if (s.sweep_id && s.sweep_id !== s.ver_id && (!s.ver_id || s.sweep_gap < s.ver_gap)) cands.push(['sweep', s.sweep_name, s.sweep_gap, s.sweep_delta, 'sweep_gap', 'sweep_delta', 'best sweep configuration (live, unreviewed)']);
    if (s.claim_id && s.claim_id !== s.ver_id && (!s.ver_id || s.claim_gap < s.ver_gap) && (base === null || s.claim_gap < base || !s.sweep_id)) cands.push(['claim', s.claim_name, s.claim_gap, s.claim_delta, 'claim_gap', 'claim_delta', 'best claimed row (waiting for the verifier)']);
    cands.forEach(([k, name, g, dlt, fg, fd, what]) => {
      const c = el('div', 'sw-cand');
      const t = el('span'); t.append(document.createTextNode(what + ': '), mark(el('b', null, name), 'summary', k === 'sweep' ? 'sweep_name' : 'claim_name', 0));
      const v = el('span'); v.append(document.createTextNode('gap '), mark(el('b', null, X.gapf(g)), 'summary', fg, 0), document.createTextNode(base !== null ? (dlt < 0 ? ', ' : ', ') : ''));
      if (base !== null) { v.append(mark(el('b', null, X.gapf(Math.abs(dlt))), 'summary', fd, 0), document.createTextNode(dlt < 0 ? ' below the baseline' : ' above the baseline')); }
      c.append(t, v); main.appendChild(c);
    });
    /* the scale: target 0 ... baseline ... */
    if (base !== null) {
      const sc = el('div', 'sw-scale'); sc.appendChild(el('div', 'sw-scale-track'));
      const vals = [base, s.ver_gap, s.sweep_gap, s.claim_gap].filter((v) => v !== null);
      const top = Math.max(base * 1.4, ...vals.filter((v) => v < base * 3)) * 1.05;
      const put = (v, k, label, up) => {
        if (v === null || v === undefined) return;
        const f = Math.max(0, Math.min(1, v / top));
        const m = el('div', 'sw-scale-m'); m.dataset.k = k; m.style.left = (100 * f) + '%';
        if (f < 0.12) m.dataset.edge = 'l'; if (f > 0.88) m.dataset.edge = 'r'; if (up) m.dataset.up = '1';
        m.appendChild(el('span', null, label)); sc.appendChild(m);
      };
      put(0, 'target', 'target 0');
      put(base, 'base', '3R baseline ' + X.gapf(base), true);
      if (s.ver_gap !== null) put(s.ver_gap, 'best', 'verified ' + X.gapf(s.ver_gap));
      else if (s.sweep_gap !== null) put(s.sweep_gap, 'claim', 'best sweep ' + X.gapf(s.sweep_gap));
      main.appendChild(sc);
      const legend = el('p', 'sw-hero-sub');
      legend.append(document.createTextNode('gap = 100 × (shortfall of in-band 14 mm below 90% + of follow below 95% + of reach below 90%) + 100 × contact. Baseline: '),
        mark(el('b', null, X.gapf(base)), 'morphs', 'gap', 'id=' + X.enc(s.base_id)), document.createTextNode(', the champion 3R idealised on the same bench.'));
      main.appendChild(legend);
    }
    /* side: who beats the baseline now */
    side.appendChild(el('h3', 'sw-side-h', 'Below the baseline now'));
    const best = (m) => (m.v_gap !== null ? ['verified', m.v_gap, 'v_gap'] : m.gap !== null ? ['claimed', m.gap, 'gap'] : m.sweep_gap !== null ? ['sweep', m.sweep_gap, 'sweep_gap'] : null);
    const rows = M.filter(LIVE).map((m) => [m, best(m)]).filter(([, b]) => b && base !== null && b[1] < base).sort((a, b) => a[1][1] - b[1][1]);
    if (!rows.length) side.appendChild(el('p', 'sw-empty', base === null ? 'No baseline row yet.' : 'None yet: every morphology measured so far is at or above the baseline gap.'));
    const ol = el('ol', 'sw-runners');
    rows.slice(0, 6).forEach(([m, b], i) => {
      const li = el('li', 'sw-runner'); li.dataset.win = b[0] === 'verified' ? '1' : 'claim';
      li.appendChild(el('span', 'sw-runner-rank', '#' + (i + 1)));
      const nm = el('span', 'sw-runner-name'); nm.appendChild(mark(el('span', null, m.name), 'morphs', 'name', 'id=' + X.enc(m.id)));
      const ch = el('span', 'sw-chip', b[0]); ch.dataset.s = b[0] === 'verified' ? 'win' : 'claim'; nm.appendChild(ch);
      li.appendChild(nm);
      li.appendChild(mark(el('span', 'sw-runner-gap', X.gapf(b[1])), 'morphs', b[2], 'id=' + X.enc(m.id)));
      ol.appendChild(li);
    });
    side.appendChild(ol);
    if (rows.length > 6) side.appendChild(el('p', 'sw-empty', `and ${rows.length - 6} more in the Concept bench tab`));
  }

  function kpis() {
    const box = document.getElementById('kpis');
    box.replaceChildren();
    const st = X.st('summary', 'funnel');
    box.classList.toggle('dash-skeleton', st === 'loading');
    if (st !== 'ok') { if (st !== 'loading') box.appendChild(el('div', 'sw-msg sw-failed', 'Failed to load')); return; }
    const s = X.rows('summary')[0] || {}, F = X.rows('funnel');
    const tile = (label, valEl, sub, good) => {
      const t = el('div', 'sw-kpi'); t.appendChild(el('span', 'sw-kpi-l', label));
      valEl.classList.add('sw-kpi-v'); if (good !== undefined) valEl.dataset.good = good ? '1' : '0';
      t.appendChild(valEl); if (sub) t.appendChild(sub); box.appendChild(t);
    };
    const f = (stage) => F.find((r) => r.stage === stage) || { n: 0 };
    tile('Morphologies ideated', mark(el('span', null, String(f('ideated').n)), 'funnel', 'n', 'stage=ideated'), (() => { const p = el('span', 'sw-kpi-s'); p.append(mark(el('span', null, String(f('modelled').n)), 'funnel', 'n', 'stage=modelled'), document.createTextNode(' modelled')); return p; })());
    tile('Screened on the bench', mark(el('span', null, String(f('screened').n)), 'funnel', 'n', 'stage=screened'), (() => { const p = el('span', 'sw-kpi-s'); p.append(mark(el('span', null, String(f('verified').n)), 'funnel', 'n', 'stage=verified'), document.createTextNode(' verified')); return p; })());
    tile('Below the 3R baseline', mark(el('span', null, String(s.n_beating ?? 0)), 'summary', 'n_beating', 0), el('span', 'sw-kpi-s', 'morphologies, best evidence'), (s.n_beating || 0) > 0 ? true : undefined);
    tile('Best built R1 (3 DOF)', mark(el('span', null, X.pct(s.cad_r1)), 'summary', 'cad_r1', 0), (() => { const p = el('span', 'sw-kpi-s'); p.append(document.createTextNode('pass 90% · '), mark(el('span', null, s.cad_r1_design || '–'), 'summary', 'cad_r1_design', 0)); return p; })(), s.cad_r1 !== null && s.cad_r1 >= 0.9);
    tile('Requirements passing', (() => { const v = el('span'); v.append(mark(el('span', null, String(s.reqs_pass ?? '–')), 'summary', 'reqs_pass', 0), document.createTextNode(' / '), mark(el('span', null, String(s.reqs_total ?? '–')), 'summary', 'reqs_total', 0)); return v; })(),
      (() => { const p = el('span', 'sw-kpi-s'); p.append(mark(el('span', null, s.reqs_design || '–'), 'summary', 'reqs_design', 0)); return p; })());
  }

  function record() {
    const box = document.getElementById('record-chart');
    const st = X.st('sweeps', 'morphs');
    const S = X.rows('sweeps'), M = X.rows('morphs');
    const base = (M.find((m) => m.is_baseline) || {}).gap ?? null;
    const scored = S.filter((s) => s.gap !== null);
    if (!X.ready(box, st, scored.length ? null : 'No configuration measured yet. The swarm is (re)starting: each morphology agent first builds and checks its model, so the first bench results usually arrive within the hour.' + (base !== null ? ' The bar to beat is the 3R baseline, gap ' + X.gapf(base) + '.' : ''))) { X.key(document.getElementById('record-key'), []); return; }
    const name = new Map(M.map((m) => [m.id, m.name]));
    const recs = scored.filter((s) => s.is_record);
    const times = scored.map((s) => X.date(s.t)).concat(M.filter((m) => m.v_gap !== null && m.t_screened).map((m) => X.date(m.t_screened)));
    const xd = X.timeDomain(times);
    const cur = recs[recs.length - 1];
    const top = Math.max(base !== null ? base * 1.6 : 0, cur ? cur.record_gap * 1.3 : 0, 20);
    const acc = X.acc();
    const dots = scored.map((s) => ({ t: X.date(s.t), v: s.gap, r: 2, fill: 'var(--cds-chart-muted)', opacity: 0.55, head: X.tUTC(X.date(s.t)),
      tip: [name.get(s.id) || s.id, ['gap', X.gapf(s.gap)], ['best of this morphology so far', X.gapf(s.best_gap)], ['in-band 14 / reach / follow', [X.pct(s.inband14), X.pct(s.reach), X.pct(s.follow)].join(' · ')], ['contact', X.pct(s.contact)]] }));
    recs.forEach((s) => dots.push({ t: X.date(s.t), v: s.gap, r: 4, fill: base !== null && s.gap < base ? acc : 'var(--color-fg)', head: X.tUTC(X.date(s.t)),
      tip: ['New record: ' + (name.get(s.id) || s.id), ['gap', X.gapf(s.gap)], ['vs the 3R baseline', base === null ? '–' : (s.gap < base ? '−' : '+') + X.gapf(Math.abs(s.gap - base))], ['in-band 14 / reach / follow', [X.pct(s.inband14), X.pct(s.reach), X.pct(s.follow)].join(' · ')], ['contact', X.pct(s.contact)]] }));
    M.filter((m) => m.v_gap !== null && m.t_screened && !m.is_baseline).forEach((m) => dots.push({ t: X.date(m.t_screened), v: m.v_gap, r: 4.5, shape: 'diamond', fill: base !== null && m.v_gap < base ? acc : 'var(--color-fg)', head: X.tUTC(X.date(m.t_screened)), tip: ['Verified: ' + m.name, ['re-measured gap', X.gapf(m.v_gap)], ['claimed gap', X.gapf(m.gap)]] }));
    const notes = [];
    if (cur) notes.push({ t: X.date(cur.t), v: cur.gap, text: X.short(name.get(cur.id) || cur.id, 34) + ' ' + X.gapf(cur.gap), color: base !== null && cur.gap < base ? acc : null, bold: true });
    const firstBelow = base !== null ? recs.find((s) => s.gap < base) : null;
    if (firstBelow && firstBelow !== cur) notes.push({ t: X.date(firstBelow.t), v: firstBelow.gap, text: 'first below the baseline' });
    const r = X.timeChart(box, {
      H: 300, x: xd, hideOff: true,
      y: { domain: [0, top], fmt: (v) => d3.format('~g')(v), label: 'gap (lower is better)' },
      refs: [base !== null ? { v: base, label: '3R baseline|' + X.gapf(base), cls: 'sw-ref' } : null, { v: 0, label: 'target 0', cls: 'sw-tgt' }].filter(Boolean),
      lines: [{ pts: recs.map((s) => ({ t: X.date(s.t), v: s.record_gap })), color: 'var(--color-fg)', width: 2.25, extend: true, split: base !== null ? { v: base, below: true, color: acc } : null }],
      dots, notes
    });
    X.key(document.getElementById('record-key'), [
      ['line', 'var(--color-fg)', 'record so far'], base !== null ? ['line', acc, 'record below the 3R baseline'] : null,
      ['dot', acc, 'new record'], ['small', 'var(--cds-chart-muted)', 'one configuration'], ['diamond', 'var(--color-fg)', 'verified (re-measured)'],
      base !== null ? ['dash', 'var(--cds-chart-reference)', '3R baseline'] : null, ['dash', 'var(--color-ok)', 'target 0'],
      r.nclip ? ['tri', 'var(--cds-chart-muted)', r.nclip + ' configuration' + (r.nclip === 1 ? '' : 's') + ' above the top of the scale'] : null
    ]);
  }

  function cadRecord() {
    const box = document.getElementById('cadrec-chart');
    const st = X.st('cad', 'cad_record');
    const C = X.rows('cad').filter((c) => c.req === 'R1' && c.dof === 3), R = X.rows('cad_record');
    if (!X.ready(box, st, C.length ? null : 'No built 3-DOF design has an R1 judge result yet.')) { X.key(document.getElementById('cadrec-key'), []); return; }
    const acc = X.acc();
    const xd = X.timeDomain(C.map((c) => X.date(c.time)));
    const cur = R[R.length - 1];
    const dots = C.map((c) => ({ t: X.date(c.time), v: c.value, r: 4, shape: c.level === 'Full CAD' ? 'circle' : 'square',
      fill: c.level === 'Full CAD' ? 'var(--color-fg)' : 'none', stroke: 'var(--color-fg)', opacity: c.rules === 'older' ? 0.35 : 1, head: X.tUTC(X.date(c.time)),
      tip: [c.design, ['R1 (2-14 mm)', X.pct(c.value)], ['level', c.level], ['judging rules', c.rules === 'older' ? 'older (before a judge change)' : 'current']] }));
    R.forEach((c) => dots.push({ t: X.date(c.time), v: c.value, r: 4.5, fill: acc, head: X.tUTC(X.date(c.time)), tip: ['New R1 record: ' + c.design, ['R1', X.pct(c.value)], ['level', c.level]] }));
    X.timeChart(box, {
      H: 260, x: xd,
      y: { domain: [0, 1], fmt: d3.format('.0%'), label: 'R1, share of skin 2-14 mm from the metal' },
      refs: [{ v: 0.9, label: 'pass 90%', cls: 'sw-tgt' }], noteSide: 'above',
      lines: [{ pts: R.map((c) => ({ t: X.date(c.time), v: c.value })), color: acc, width: 2.25, extend: true }],
      dots, notes: cur ? [{ t: X.date(cur.time), v: cur.value, text: X.short(cur.design, 30) + ' ' + X.pct(cur.value), color: acc, bold: true }] : []
    });
    X.key(document.getElementById('cadrec-key'), [['line', acc, 'best 3-DOF R1 so far'], ['dot', 'var(--color-fg)', 'full CAD'], ['square', 'var(--color-fg)', 'keep-out CAD'], ['dash', 'var(--color-ok)', 'pass line 90%']]);
  }

  X.tabs.leader = () => { hero(); kpis(); record(); cadRecord(); };
})();
