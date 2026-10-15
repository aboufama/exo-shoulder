
(function () {
  const page = document.getElementById('sw-page');
  const $ = (id) => document.getElementById(id);
  const num = (v) => (v === null || v === undefined || v === '' || !isFinite(Number(v)) ? null : Number(v));
  const yes = (v) => v === true || v === 'true' || v === 1;
  const P1 = d3.format('.1%'), P0 = d3.format('.0%'), F1 = d3.format('.1f');
  const pct = (v) => (num(v) === null ? '–' : P1(num(v)));
  const gapf = (v) => (num(v) === null ? '–' : F1(num(v)));
  const tUTC = d3.utcFormat('%b %-d, %H:%M UTC');
  const date = (s) => (s ? new Date(s) : null);
  const enc = (v) => encodeURIComponent(String(v));
  const short = (s, n) => { s = String(s || ''); return s.length > n ? s.slice(0, n - 1) + '…' : s; };
  const ACC = () => dash.colors[0];
  page.style.setProperty('--sw-accent', dash.colors[0]);

  function ago(s) {
    const t = date(s); if (!t || isNaN(t)) return '';
    const m = Math.max(0, (Date.now() - t) / 60000);
    if (m < 1.5) return 'just now'; if (m < 90) return Math.round(m) + ' min ago';
    const h = m / 60; if (h < 36) return (h < 10 ? F1(h).replace(/\.0$/, '') : Math.round(h)) + ' h ago';
    return Math.round(h / 24) + ' days ago';
  }
  function el(tag, cls, text) { const e = document.createElement(tag); if (cls) e.className = cls; if (text !== undefined && text !== null) e.textContent = text; return e; }
  function mark(e, src, field, where) {
    e.setAttribute('data-source', src); if (field) e.setAttribute('data-field', field);
    if (typeof where === 'number') e.setAttribute('data-row', String(where)); else if (where) e.setAttribute('data-where', where);
    return e;
  }
  function stOf(...ids) { const s = ids.map((i) => dash.data(i).status); return s.find((x) => x !== 'ok' && x !== 'loading') || (s.includes('loading') ? 'loading' : 'ok'); }
  const rowsOf = (id) => { const d = dash.data(id); return d.status === 'ok' && Array.isArray(d.data) ? d.data : []; };
  function ready(box, st, emptyMsg) {
    box.querySelectorAll(':scope > .sw-msg').forEach((e) => e.remove());
    box.classList.toggle('dash-skeleton', st === 'loading');
    if (st === 'ok' && !emptyMsg) return true;
    box.querySelectorAll(':scope > svg').forEach((e) => e.remove());
    if (st !== 'loading') box.appendChild(el('div', st === 'ok' ? 'sw-msg' : 'sw-msg sw-failed', st === 'ok' ? emptyMsg : 'Failed to load'));
    return false;
  }
  function frame(box, H) {
    const W = Math.max(240, box.clientWidth);
    let svg = d3.select(box).select(':scope > svg');
    if (svg.empty()) svg = d3.select(box).append('svg').attr('class', 'sw-svg').attr('width', '100%');
    svg.attr('viewBox', `0 0 ${W} ${H}`).attr('height', H).selectAll('*').remove();
    return { svg, W, H };
  }
  function measure(svg, s, cls) { const t = svg.append('text').attr('class', cls || null).text(s); const w = t.node().getComputedTextLength(); t.remove(); return w; }
  function robust(vals, refs, lo0, hi0) {
    const v = vals.filter(Number.isFinite).sort(d3.ascending), r = refs.filter(Number.isFinite), all = v.concat(r);
    if (!all.length) return [lo0 ?? 0, hi0 ?? 1];
    let lo = d3.min(all), hi = d3.max(all);
    if (v.length >= 5) {
      const a = Math.min(d3.quantile(v, 0.1), ...r), b = Math.max(d3.quantile(v, 0.9), ...r), span = (b - a) || Math.abs(b) || 1;
      hi = Math.min(hi, b + 0.45 * span); lo = Math.max(lo, a - 0.45 * span);
    }
    const pad = ((hi - lo) || Math.abs(hi) || 1) * 0.07;
    lo -= pad; hi += pad;
    if (lo0 !== undefined) lo = Math.max(lo0, lo); if (hi0 !== undefined) hi = Math.min(hi0, hi);
    return [lo, hi];
  }
  const overlap = (a, b) => a[0] < b[2] && b[0] < a[2] && a[1] < b[3] && b[1] < a[3];
  const dotBox = (x, y, r) => [x - r - 1, y - r - 1, x + r + 1, y + r + 1];
  function pathBoxes(pts) {
    // thin boxes along a polyline (step lines are axis-aligned, so these are exact)
    const out = [];
    for (let i = 1; i < pts.length; i++) {
      const [a, b] = [pts[i - 1], pts[i]];
      out.push([Math.min(a[0], b[0]) - 2, Math.min(a[1], b[1]) - 2, Math.max(a[0], b[0]) + 2, Math.max(a[1], b[1]) + 2]);
    }
    return out;
  }
  function placeLabels(g, svg, items, bounds, obstacles) {
    // items: {x, y, r, text}; every dot (its own too), line and earlier label is an obstacle. Near spots first; a farther
    // spot gets a thin leader line to its dot; no clean spot: the label is dropped (the tooltip still names the dot).
    const near = [[1, -1], [1, 1], [-1, -1], [-1, 1]], far = [];
    [22, 36].forEach((d) => [[1, -1], [1, 1], [-1, -1], [-1, 1], [0, -1], [0, 1]].forEach(([sx, sy]) => far.push([sx, sy, d])));
    items.forEach((it) => {
      const w = measure(svg, it.text, 'sw-lab'), h = 12, r = (it.r || 5) + 3;
      const cands = near.map(([sx, sy]) => [sx, sy, 0]).concat(far);
      for (const [sx, sy, d] of cands) {
        let x0, y0;
        if (sx === 0) { x0 = it.x - w / 2; y0 = sy < 0 ? it.y - r - d - h : it.y + r + d; }
        else { x0 = sx > 0 ? it.x + r + d * 0.7 : it.x - r - d * 0.7 - w; y0 = sy < 0 ? it.y - r * 0.4 - d * 0.7 - h : it.y + r * 0.4 + d * 0.7; }
        const b = [x0 - 2, y0 - 1, x0 + w + 2, y0 + h + 1];
        if (b[0] < bounds[0] || b[2] > bounds[2] || b[1] < bounds[1] || b[3] > bounds[3] || obstacles.some((o) => overlap(o, b))) continue;
        obstacles.push(b);
        if (d) {
          const cx = Math.max(b[0], Math.min(b[2], it.x)), cy = Math.max(b[1], Math.min(b[3], it.y)), L = Math.hypot(cx - it.x, cy - it.y) || 1;
          g.append('line').attr('x1', it.x + (cx - it.x) * (r - 1) / L).attr('y1', it.y + (cy - it.y) * (r - 1) / L).attr('x2', cx).attr('y2', cy)
            .style('stroke', 'var(--color-fg-muted)').style('stroke-width', 0.8).style('stroke-opacity', 0.7);
        }
        g.append('text').attr('class', 'sw-lab').attr('x', x0).attr('y', y0 + h - 2).text(it.text);
        return;
      }
    });
  }
  function nudgeY(y, h, x0, x1, taken, lo, hi) {
    // nearest free vertical slot for a label box [x0, y - h/2, x1, y + h/2]
    for (let k = 0; k < 40; k++) {
      const dy = (k % 2 ? 1 : -1) * Math.ceil(k / 2) * 4, yy = Math.max(lo + h / 2, Math.min(hi - h / 2, y + dy)), b = [x0, yy - h / 2, x1, yy + h / 2];
      if (!taken.some((o) => overlap(o, b))) return yy;
    }
    return y;
  }
  function yTicks(svg, y, n, fmt) { const t = y.ticks(n); return { t, w: d3.max(t, (v) => measure(svg, fmt(v))) || 0 }; }
  function drawGridY(g, y, ticks, fmt, x0, x1) {
    ticks.forEach((v) => {
      g.append('line').attr('x1', x0).attr('x2', x1).attr('y1', y(v)).attr('y2', y(v)).style('stroke', 'var(--cds-chart-grid)');
      g.append('text').attr('x', x0 - 6).attr('y', y(v)).attr('dy', '0.32em').attr('text-anchor', 'end').text(fmt(v));
    });
  }
  function timeDomain(ts) {
    // pad a time span; a lone dot (or a span under 3 h) gets a 3-hour window so the axis reads in hours, not minutes
    const t0 = d3.min(ts), t1 = d3.max(ts), span = t1 - t0, total = Math.max(span * 1.08, 3 * 3600e3), pad = (total - span) / 2;
    return [new Date(t0 - pad), new Date(t1 + pad)];
  }
  function drawTimeX(g, x, yb, svg) {
    const [a, b] = x.domain(), span = b - a, inner = x.range()[1] - x.range()[0];
    const hm = d3.utcFormat('%H:%M'), day = d3.utcFormat('%b %-d');
    const f = span < 6 * 864e5 ? (t) => (t.getUTCHours() === 0 && t.getUTCMinutes() === 0 ? day(t) : hm(t)) : day;
    const w = Math.max(measure(svg, 'Oct 15'), measure(svg, '00:00')) + 22, maxN = Math.max(2, Math.floor(inner / w));
    let n = maxN, t = x.ticks(n);
    while (t.length > maxN && n > 1) { n--; t = x.ticks(n); }          // d3 can return about twice the count asked for
    if (t.length > maxN) { const k = Math.ceil(t.length / maxN); t = t.filter((_, i) => i % k === 0); }
    t.forEach((v) => {
      g.append('text').attr('x', x(v)).attr('y', yb + 16).attr('text-anchor', 'middle').text(f(v));
      g.append('line').attr('x1', x(v)).attr('x2', x(v)).attr('y1', yb).attr('y2', yb + 4).style('stroke', 'var(--cds-chart-axis)');
    });
    g.append('line').attr('x1', x.range()[0]).attr('x2', x.range()[1]).attr('y1', yb).attr('y2', yb).style('stroke', 'var(--cds-chart-axis)');
  }
  const tri = (sel, x, y, dir, fill, size) => sel.append('path').attr('transform', `translate(${x},${y}) rotate(${dir})`).attr('d', d3.symbol(d3.symbolTriangle, size || 46)()).style('fill', fill);

  /* ---------- tooltip ---------- */
  const tip = el('div', 'sw-tip'); tip.hidden = true; page.appendChild(tip);
  function showTip(ev, head, sub, lines) {
    tip.replaceChildren(el('div', 'sw-tip-h', head));
    if (sub) tip.appendChild(el('div', 'sw-tip-s', sub));
    lines.forEach(([k, v]) => { const r = el('div', 'sw-tip-r'); r.append(el('span', null, k), el('span', null, v)); tip.appendChild(r); });
    tip.hidden = false;
    const pr = page.getBoundingClientRect(); let x = ev.clientX - pr.left + 14, y = ev.clientY - pr.top + 14;
    if (x + tip.offsetWidth > page.clientWidth) x = Math.max(0, ev.clientX - pr.left - tip.offsetWidth - 14);
    tip.style.left = x + 'px'; tip.style.top = y + 'px';
  }
  const hideTip = () => { tip.hidden = true; };
  function hover(svg, pts, onHit, maxD) {
    const ring = svg.append('circle').attr('r', 0).style('fill', 'none').style('stroke', 'var(--color-fg)').style('stroke-width', 2).style('pointer-events', 'none');
    if (!pts.length) return;
    const del = d3.Delaunay.from(pts, (p) => p.x, (p) => p.y);
    const move = (ev) => {
      const [mx, my] = d3.pointer(ev, svg.node()), i = del.find(mx, my), p = pts[i];
      if (p && Math.hypot(p.x - mx, p.y - my) < (maxD || 26)) { ring.attr('cx', p.x).attr('cy', p.y).attr('r', (p.r || 5) + 3.5); onHit(ev, p); }
      else { ring.attr('r', 0); hideTip(); }
    };
    svg.on('pointermove', move).on('pointerdown', move).on('pointerleave', () => { ring.attr('r', 0); hideTip(); });
  }

  /* ---------- vocabulary ---------- */
  const MET = {
    gap: { key: 'gap', short: 'Gap', title: 'gap to the bench targets', axisTitle: 'gap to the bench targets (points)', dir: -1, target: 0, fmt: (v) => F1(v) + ' pts', axis: d3.format('~f'), targetText: 'target 0',
      what: 'Gap = points short of the three bench targets (metal 2–14 mm from the skin 90%, follow 95%, reach 90%), plus 1 point per % of poses with metal inside the body; 0 means every target is met.' },
    inband14: { key: 'inband14', short: 'In-band 14 mm', title: 'share of metal 2–14 mm from the skin', axisTitle: 'metal 2–14 mm from the skin (%)', dir: 1, target: 0.9, fmt: P1, axis: P0, targetText: 'target 90%',
      what: 'In-band 14 mm = share of the mechanism’s metal that stays 2–14 mm from the skin while it follows the motions (your 1 cm rule, passing at 14 mm). Target 90%.' },
    inband10: { key: 'inband10', short: 'In-band 10 mm', title: 'share of metal 2–10 mm from the skin', axisTitle: 'metal 2–10 mm from the skin (%)', dir: 1, target: 0.9, fmt: P1, axis: P0, targetText: 'aim 90%',
      what: 'In-band 10 mm = share of the mechanism’s metal inside 2–10 mm of the skin, your 1 cm aim. Aim 90%.' },
    reach: { key: 'reach', short: 'Reach', title: 'share of everyday arm poses reached', axisTitle: 'everyday arm poses reached (%)', dir: 1, target: 0.9, fmt: P1, axis: P0, targetText: 'target 90%',
      what: 'Reach = share of everyday arm poses the mechanism can take without its metal entering the body. Target 90%.' },
    follow: { key: 'follow', short: 'Follow', title: 'share of motion frames followed', axisTitle: 'motion frames followed (%)', dir: 1, target: 0.95, fmt: P1, axis: P0, targetText: 'target 95%',
      what: 'Follow = share of motion-clip frames the mechanism follows instead of stopping at a joint limit or in the body. Target 95%.' }
  };
  const STATUS_WORDS = { ideated: 'written up, not measured yet', modelling: 'its agent is building the model', screened: 'measured on the bench', verified: 're-measured by the verifier and held up',
    refuted: 'the verifier’s numbers did not hold the claim', dead: 'dropped', gpu: 'in a short GPU search', cad: 'being built as keep-out CAD', judged: 'scored by the real requirement judges' };
  const solid = (r) => r.verified || r.remeasured;                 // the verifier stands behind the number
  const cls = (r) => (r.is_baseline ? 'base' : ['refuted', 'dead'].includes(r.status) ? 'out' : r.winner ? (solid(r) ? 'win' : 'claim') : 'other');
  function standing(r) {
    const c = cls(r);
    if (c === 'base') return 'The current 3R design: the bar to beat';
    if (c === 'win') return 'Beats the baseline · ' + (r.verified ? 'verified' : 're-measured, verdict pending');
    if (c === 'claim') return 'Beats the baseline · claimed, not re-measured yet';
    if (c === 'out') return r.status === 'refuted' ? 'Refuted: the verifier’s numbers did not hold the claim' : 'Dropped';
    return (r.gap === null ? STATUS_WORDS[r.status] || r.status : 'Does not beat the baseline') + (r.verified ? ' · verified' : r.remeasured ? ' · re-measured' : '');
  }
  function morphTip(ev, r) {
    const L = [['Gap', gapf(r.gap) + ' pts' + (r.remeasured && r.claimed_gap !== null && r.claimed_gap !== r.gap ? ' (claimed ' + gapf(r.claimed_gap) + ')' : '')],
      ['In-band 14 mm', pct(r.inband14)], ['In-band 10 mm', pct(r.inband10)], ['Reach', pct(r.reach)], ['Follow', pct(r.follow)], ['Contact', pct(r.contact)]];
    if (r.n_configs !== null && r.n_configs !== undefined) L.push(['Configurations tried', String(r.n_configs)]);
    if (r.t_screened) L.push(['Screened', tUTC(date(r.t_screened))]);
    L.push(['Status', r.status]);
    showTip(ev, r.name, (r.rank ? '#' + r.rank + ' · ' : '') + standing(r), L);
  }
  function dotStyle(sel, rad) {
    sel.attr('r', (d) => (d.lead ? rad + 1.5 : rad))
      .style('fill', (d) => (d.c === 'win' || d.c === 'claim' ? ACC() : d.c === 'out' ? 'var(--color-panel)' : 'var(--color-fg-muted)'))
      .style('fill-opacity', (d) => (d.c === 'claim' ? 0.3 : d.c === 'other' ? 0.55 : 1))
      .style('stroke', (d) => (d.c === 'claim' ? ACC() : d.c === 'out' ? 'var(--color-fg-muted)' : 'var(--color-panel)'))
      .style('stroke-width', (d) => (d.c === 'claim' || d.c === 'out' ? 1.6 : 1.2))
      .style('stroke-dasharray', (d) => (d.c === 'claim' ? '2.5 1.5' : null));
  }
  const line20 = (s, stroke, w, dash, op) => s.append('line').attr('x1', 0).attr('x2', 20).attr('y1', 6).attr('y2', 6).style('stroke', stroke).style('stroke-width', w).style('stroke-dasharray', dash || null).style('stroke-opacity', op || 1);
  const KEYS = {
    win: (s) => s.append('circle').attr('cx', 6).attr('cy', 6).attr('r', 5).style('fill', ACC()),
    claim: (s) => s.append('circle').attr('cx', 6).attr('cy', 6).attr('r', 4.5).style('fill', ACC()).style('fill-opacity', 0.3).style('stroke', ACC()).style('stroke-width', 1.6).style('stroke-dasharray', '2.5 1.5'),
    other: (s) => s.append('circle').attr('cx', 6).attr('cy', 6).attr('r', 5).style('fill', 'var(--color-fg-muted)').style('fill-opacity', 0.55),
    out: (s) => s.append('circle').attr('cx', 6).attr('cy', 6).attr('r', 4.5).style('fill', 'none').style('stroke', 'var(--color-fg-muted)').style('stroke-width', 1.6),
    base: (s) => s.append('path').attr('transform', 'translate(6,6)').attr('d', d3.symbol(d3.symbolDiamond, 70)()).style('fill', 'var(--color-fg)'),
    baseline: (s) => line20(s, 'var(--color-fg)', 1.5, '5 3'),
    target: (s) => line20(s, 'var(--color-ok)', 1.5, '5 3'),
    rules: (s) => s.append('line').attr('x1', 6).attr('x2', 6).attr('y1', 0).attr('y2', 12).style('stroke', 'var(--color-fg-muted)').style('stroke-width', 1.2).style('stroke-dasharray', '2 2'),
    record: (s) => s.append('path').attr('d', 'M0,2H8V10H20').style('fill', 'none').style('stroke', 'var(--color-fg)').style('stroke-width', 2),
    recclaim: (s) => s.append('path').attr('d', 'M0,2H8V10H20').style('fill', 'none').style('stroke', 'var(--color-fg)').style('stroke-width', 2).style('stroke-dasharray', '3 2.5'),
    zone: (s) => s.append('rect').attr('width', 14).attr('height', 12).attr('rx', 2).style('fill', ACC()).style('fill-opacity', 0.12),
    corner: (s) => s.append('rect').attr('width', 14).attr('height', 12).attr('rx', 2).style('fill', 'var(--color-ok)').style('fill-opacity', 0.16),
    clip: (s) => s.append('path').attr('transform', 'translate(6,7)').attr('d', d3.symbol(d3.symbolTriangle, 40)()).style('fill', 'var(--color-fg-muted)'),
    lead: (s) => line20(s, ACC(), 2.75),
    winline: (s) => line20(s, ACC(), 1.6, null, 0.75),
    otherline: (s) => line20(s, 'var(--color-fg-muted)', 1.2, null, 0.5),
    outline: (s) => line20(s, 'var(--color-fg-muted)', 1.2, '3 3', 0.6),
    vring: (s) => s.append('circle').attr('cx', 6).attr('cy', 6).attr('r', 4.5).style('fill', 'var(--color-panel)').style('stroke', 'var(--color-fg)').style('stroke-width', 1.5),
    hollowdot: (s) => s.append('circle').attr('cx', 6).attr('cy', 6).attr('r', 4.5).style('fill', 'var(--color-panel)').style('stroke', 'var(--color-fg-muted)').style('stroke-width', 1.5),
    filldot: (s) => s.append('circle').attr('cx', 6).attr('cy', 6).attr('r', 5).style('fill', 'var(--color-fg)'),
    fg3: (s) => { line20(s, 'var(--color-fg)', 2); s.append('circle').attr('cx', 10).attr('cy', 6).attr('r', 3.5).style('fill', 'var(--color-fg)'); },
    faded: (s) => { line20(s, 'var(--color-fg)', 2, null, 0.3); s.append('circle').attr('cx', 10).attr('cy', 6).attr('r', 3.5).style('fill', 'var(--color-fg)').style('fill-opacity', 0.3); }
  };
  const WIDE = ['baseline', 'target', 'record', 'recclaim', 'lead', 'winline', 'otherline', 'outline', 'fg3', 'faded', 'series', 'series4'];
  function key(box, items) {
    box.replaceChildren();
    items.forEach(([k, label, color]) => {
      const s = el('span');
      if (!k) { s.appendChild(document.createTextNode(label)); box.appendChild(s); return; }
      const svg = d3.select(s).append('svg').attr('width', WIDE.includes(k) ? 20 : 12).attr('height', 12).attr('aria-hidden', 'true');
      if (k === 'series' || k === 'series4') { line20(svg, color, 2, k === 'series4' ? '4 3' : null); svg.append('circle').attr('cx', 10).attr('cy', 6).attr('r', 3.5).style('fill', k === 'series4' ? 'var(--color-panel)' : color).style('stroke', color).style('stroke-width', 1.5); }
      else if (color) svg.append('circle').attr('cx', 6).attr('cy', 6).attr('r', 5).style('fill', color); else KEYS[k](svg);
      s.appendChild(document.createTextNode(label)); box.appendChild(s);
    });
  }

  /* ---------- header ---------- */
  function freshState() {
    const ms = dash.data('meta').status, M = rowsOf('meta')[0], sst = stOf('summary');
    if (ms === 'error' || sst === 'error') return 'bad';
    if (ms !== 'ok' || !M || !M.built_at) return 'idle';
    return Date.now() - date(M.built_at) > 30 * 60e3 ? 'warn' : 'ok';
  }
  function drawFresh() {
    const M = rowsOf('meta')[0], F = rowsOf('freshness')[0], ms = dash.data('meta').status, fst = stOf('freshness');
    const b = $('fresh-built'), t = $('fresh-t'), st = freshState();
    b.classList.toggle('dash-skeleton', ms === 'loading'); t.classList.toggle('dash-skeleton', fst === 'loading');
    b.textContent = M && M.built_at ? ago(M.built_at) : ms === 'loading' ? '—' : ms === 'ok' || ms === 'missing' ? 'unknown' : 'failed to load';
    if (M && M.built_at) { b.setAttribute('datetime', M.built_at); b.title = tUTC(date(M.built_at)) + (st === 'warn' ? ' – more than 30 min ago: the page may be behind the swarm' : ''); }
    t.textContent = F && F.t_last ? ago(F.t_last) : fst === 'loading' ? '—' : fst === 'ok' ? 'none yet' : 'failed to load';
    if (F && F.t_last) { t.setAttribute('datetime', F.t_last); t.title = tUTC(date(F.t_last)); }
    $('fresh').setAttribute('data-state', st);
    const lf = $('log-fresh'); lf.replaceChildren(); lf.setAttribute('data-state', st);
    if (M && M.built_at) { lf.append('data refreshed '); lf.appendChild(mark(el('time', null, ago(M.built_at)), 'meta', 'built_at', 0)); }
    if (F && F.t_last) { lf.append((M && M.built_at ? ' · ' : '') + 'last activity '); lf.appendChild(mark(el('time', null, ago(F.t_last)), 'freshness', 't_last', 0)); }
  }
  function drawHeader() {
    const st = stOf('summary'), S = rowsOf('summary')[0], take = $('takeaway');
    take.replaceChildren();
    if (st !== 'ok' || !S) { take.appendChild(el('span', st === 'loading' ? 'dash-skeleton' : null, st === 'loading' ? '—' : 'The swarm’s numbers did not load.')); }
    else {
      const b = (field, text, acc) => mark(el('b', acc ? 'sw-acc' : null, text), 'summary', field, 0), t = (s) => document.createTextNode(s);
      const base = S.baseline_gap !== null ? [t('the 3R baseline is '), b('baseline_gap', gapf(S.baseline_gap))] : [t('the 3R baseline has not been measured on the bench yet')];
      if (!S.n_screened) take.append(t('No morphology measured on the bench yet ('), b('n_total', String(S.n_total)), t(' ideated so far). '),
        ...(S.baseline_gap !== null ? [t('The bar to beat: the 3R baseline, '), b('baseline_gap', gapf(S.baseline_gap)), t(' points short of the bench targets.')] : [t('The 3R baseline has not been measured on the bench yet either.')]));
      else if (!S.n_winners) take.append(t('No morphology beats the baseline yet. Closest: '), b('leader_name', S.leader_name || '–'), t(', '), b('leader_gap', gapf(S.leader_gap)),
        t(' points short of the bench targets; '), ...base, t('. '), b('n_screened', String(S.n_screened)), t(' of '), b('n_total', String(S.n_total)), t(' morphologies screened.'));
      else take.append(t('Leader: '), b('leader_name', S.leader_name, true), t(', '), b('leader_gap', gapf(S.leader_gap), true), t(' points short of the bench targets – '), ...base, t('. '),
        b('n_screened', String(S.n_screened)), t(' of '), b('n_total', String(S.n_total)), t(' morphologies screened; '), b('n_winners', String(S.n_winners), true),
        t(S.n_winners === 1 ? ' beats the baseline (' : ' beat the baseline ('), b('n_verified_winners', String(S.n_verified_winners)), t(' verified).'));
    }
    drawFresh();
  }
