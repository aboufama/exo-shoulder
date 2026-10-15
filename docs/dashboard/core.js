/* Shared helpers, calculations and the time-chart used by every tab. Everything shared lives on window.EXO. */
dash.calc('summary', {
  inputs: ['morphs', 'sweeps', 'cad', 'reqs', 'events'],
  title: 'Headline numbers',
  description: 'Concept-bench leader (verified, claimed, best sweep configuration) against the 3R baseline, best built 3-DOF R1, requirements passing on the best design, and the newest result time.',
  fn: (morphs, sweeps, cad, reqs, events) => {
    const real = (rows) => rows.filter((r) => r.empty !== true);
    morphs = real(morphs); sweeps = real(sweeps); cad = real(cad); reqs = real(reqs); events = real(events);
    const live = (m) => !m.is_baseline && !['dead', 'refuted', 'duplicate'].includes(m.status);
    const base = morphs.find((m) => m.is_baseline) || {};
    const best = (rows, f) => rows.filter((m) => m[f] !== null && m[f] !== undefined).sort((a, b) => a[f] - b[f])[0] || {};
    const ver = best(morphs.filter((m) => live(m) && ['verified', 'gpu', 'cad'].includes(m.status)), 'v_gap');
    const cla = best(morphs.filter(live), 'gap');
    const swp = best(morphs.filter(live), 'sweep_gap');
    const bg = base.gap ?? null, d = (v) => (v === undefined || v === null || bg === null ? null : Math.round((v - bg) * 100) / 100);
    const cad3 = cad.filter((c) => c.req === 'R1' && c.dof === 3 && c.rules === 'current').sort((a, b) => b.value - a.value)[0] || {};
    const times = [...sweeps.map((s) => s.t), ...events.map((e) => e.time), ...cad.map((c) => c.time)].filter(Boolean).sort();
    const bestEv = (m) => [m.v_gap, m.gap, m.sweep_gap].filter((v) => v !== null && v !== undefined)[0];
    return [{
      base_id: base.id ?? null, base_gap: bg,
      ver_id: ver.id ?? null, ver_name: ver.name ?? null, ver_gap: ver.v_gap ?? null, ver_delta: d(ver.v_gap),
      claim_id: cla.id ?? null, claim_name: cla.name ?? null, claim_gap: cla.gap ?? null, claim_delta: d(cla.gap),
      sweep_id: swp.id ?? null, sweep_name: swp.name ?? null, sweep_gap: swp.sweep_gap ?? null, sweep_delta: d(swp.sweep_gap), sweep_t: swp.sweep_t ?? null,
      n_beating: bg === null ? 0 : morphs.filter((m) => live(m) && bestEv(m) !== undefined && bestEv(m) < bg).length,
      cad_r1: cad3.value ?? null, cad_r1_design: cad3.design ?? null, cad_r1_time: cad3.time ?? null,
      reqs_pass: reqs.filter((r) => r.state === 'pass').length, reqs_total: reqs.length, reqs_design: (reqs.find((r) => r.design) || {}).design ?? null,
      t_last: times.length ? times[times.length - 1] : null
    }];
  }
});

dash.calc('funnel', {
  inputs: ['morphs'],
  title: 'Morphology pipeline',
  description: 'How many catalogue morphologies (no duplicates, no baseline) reached each stage: ideated, modelled (a model being swept), screened (a claimed bench row), verified, GPU sweep, CAD.',
  fn: (morphs) => {
    const ms = morphs.filter((m) => !m.is_baseline && m.status !== 'duplicate');
    const at = (sts) => ms.filter((m) => sts.includes(m.status)).length;
    const after = ['screened', 'verified', 'refuted', 'dead', 'gpu', 'cad'];
    return [
      { stage: 'ideated', n: ms.length },
      { stage: 'modelled', n: ms.filter((m) => m.status !== 'ideated' || m.n_configs > 0).length },
      { stage: 'screened', n: ms.filter((m) => after.includes(m.status) && m.gap !== null).length },
      { stage: 'verified', n: at(['verified', 'gpu', 'cad']) },
      { stage: 'GPU', n: at(['gpu', 'cad']) },
      { stage: 'CAD', n: at(['cad']) }
    ];
  }
});

dash.calc('cad_record', {
  inputs: ['cad'],
  title: 'Built CAD R1 record',
  description: 'Each time a judged 3-DOF design set a new best R1 (share of skin 2-14 mm from the metal), in judge-time order.',
  fn: (cad) => {
    cad = cad.filter((r) => r.empty !== true);
    let best = null; const out = [];
    cad.filter((c) => c.req === 'R1' && c.dof === 3).sort((a, b) => (a.time < b.time ? -1 : a.time > b.time ? 1 : 0)).forEach((c) => {
      if (best === null || c.value > best) { best = c.value; out.push({ time: c.time, design: c.design, level: c.level, value: c.value, rules: c.rules }); }
    });
    return out;
  }
});

(function () {
  const X = (window.EXO = window.EXO || {});
  const num = (v) => (v === null || v === undefined || v === '' || !isFinite(Number(v)) ? null : Number(v));
  const P1 = d3.format('.1%'), F1 = d3.format('.1f'), F2 = d3.format('.2f');
  X.num = num;
  X.pct = (v) => (num(v) === null ? '–' : P1(num(v)));
  X.gapf = (v) => (num(v) === null ? '–' : F2(num(v)));
  X.f1 = (v) => (num(v) === null ? '–' : F1(num(v)));
  X.date = (s) => (s ? new Date(s) : null);
  X.tUTC = d3.utcFormat('%b %-d, %H:%M UTC');
  X.enc = (v) => encodeURIComponent(String(v));
  X.short = (s, n) => { s = String(s || ''); return s.length > n ? s.slice(0, n - 1) + '…' : s; };
  X.acc = () => dash.colors[0];
  document.getElementById('sw-page').style.setProperty('--sw-accent', dash.colors[0]);
  X.ago = (s) => {
    const t = X.date(s); if (!t || isNaN(t)) return '';
    const m = Math.max(0, (Date.now() - t) / 60000);
    if (m < 1.5) return 'just now'; if (m < 90) return Math.round(m) + ' min ago';
    const h = m / 60; if (h < 36) return (h < 10 ? F1(h).replace(/\.0$/, '') : Math.round(h)) + ' h ago';
    return Math.round(h / 24) + ' days ago';
  };
  X.el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text !== undefined && text !== null) e.textContent = text; return e; };
  X.mark = (e, src, field, where) => {
    e.setAttribute('data-source', src); if (field) e.setAttribute('data-field', field);
    if (typeof where === 'number') e.setAttribute('data-row', String(where)); else if (where) e.setAttribute('data-where', where);
    return e;
  };
  X.rows = (id) => { const d = dash.data(id); return d.status === 'ok' && Array.isArray(d.data) ? d.data.filter((r) => r.empty !== true) : []; };
  X.st = (...ids) => { const s = ids.map((i) => dash.data(i).status); return s.find((x) => x !== 'ok' && x !== 'loading') || (s.includes('loading') ? 'loading' : 'ok'); };
  /* box state: loading -> skeleton, error -> one failed line, ok + empty message -> a designed empty state */
  X.ready = (box, st, emptyMsg) => {
    box.querySelectorAll(':scope > .sw-msg').forEach((e) => e.remove());
    box.classList.toggle('dash-skeleton', st === 'loading');
    if (st === 'ok' && !emptyMsg) return true;
    box.querySelectorAll(':scope > svg, :scope > .sw-tip').forEach((e) => e.remove());
    if (st !== 'loading') box.appendChild(X.el('div', st === 'ok' ? 'sw-msg' : 'sw-msg sw-failed', st === 'ok' ? emptyMsg : 'Failed to load'));
    return false;
  };
  X.frame = (box, H) => {
    const W = Math.max(240, box.clientWidth);
    let svg = d3.select(box).select(':scope > svg');
    if (svg.empty()) svg = d3.select(box).append('svg').attr('class', 'sw-svg').attr('width', '100%');
    svg.attr('viewBox', `0 0 ${W} ${H}`).attr('height', H).selectAll('*').remove();
    return { svg, W, H };
  };
  X.measure = (svg, s, cls) => { const t = svg.append('text').attr('class', cls || null).text(s); const w = t.node().getComputedTextLength(); t.remove(); return w; };

  /* ---------- tooltip that stays inside its box */
  X.tip = (box) => {
    let t = box.querySelector(':scope > .sw-tip');
    if (!t) { t = X.el('div', 'sw-tip'); t.hidden = true; box.appendChild(t); }
    return {
      show(px, py, head, lines) {
        t.replaceChildren();
        if (head) t.appendChild(X.el('div', 'sw-tip-s', head));
        (lines || []).forEach((l) => {
          if (typeof l === 'string') { t.appendChild(X.el('div', 'sw-tip-h', l)); return; }
          const r = X.el('div', 'sw-tip-r'); r.appendChild(X.el('span', null, l[0])); r.appendChild(X.el('span', null, l[1])); t.appendChild(r);
        });
        t.hidden = false;
        const bw = box.clientWidth, tw = t.offsetWidth, th = t.offsetHeight;
        let x = px + 14; if (x + tw > bw) x = Math.max(0, px - 14 - tw);
        let y = py - th - 10; if (y < 0) y = py + 14;
        t.style.left = x + 'px'; t.style.top = y + 'px';
      },
      hide() { t.hidden = true; }
    };
  };

  /* ---------- adaptive UTC time axis: 10 minutes to months, never more labels than fit */
  const IV = [[d3.utcMinute, 1], [d3.utcMinute, 2], [d3.utcMinute, 5], [d3.utcMinute, 10], [d3.utcMinute, 15], [d3.utcMinute, 30],
    [d3.utcHour, 1], [d3.utcHour, 2], [d3.utcHour, 3], [d3.utcHour, 6], [d3.utcHour, 12], [d3.utcDay, 1], [d3.utcDay, 2],
    [d3.utcWeek, 1], [d3.utcMonth, 1], [d3.utcMonth, 3], [d3.utcYear, 1]];
  X.timeDomain = (times) => {
    const ts = times.filter((t) => t && !isNaN(t)).map((t) => +t);
    if (!ts.length) { const n = Date.now(); return [new Date(n - 3600e3), new Date(n)]; }
    let a = d3.min(ts), b = d3.max(ts);
    const span = b - a, pad = Math.max(span * 0.04, 2 * 60e3);
    a -= pad; b += pad;
    if (b - a < 20 * 60e3) { const c = (a + b) / 2; a = c - 10 * 60e3; b = c + 10 * 60e3; }
    return [new Date(a), new Date(b)];
  };
  X.timeAxis = (g, x, y0, svg) => {
    const [a, b] = x.domain(), inner = Math.abs(x.range()[1] - x.range()[0]);
    const maxN = Math.max(2, Math.floor(inner / 62));
    let ticks = [], unit = 'time';
    for (const [iv, k] of IV) {
      const t = iv.every(k).range(a, new Date(+b + 1));
      if (t.length <= maxN) { ticks = t; unit = iv === d3.utcMinute || iv === d3.utcHour ? 'time' : 'day'; break; }
    }
    if (!ticks.length) { const t = d3.utcYear.range(a, b); const s = Math.ceil(t.length / maxN); ticks = t.filter((_, i) => i % s === 0); unit = 'day'; }
    const fT = d3.utcFormat('%H:%M'), fD = d3.utcFormat('%b %-d');
    g.append('line').attr('class', 'sw-axis-line').attr('x1', x.range()[0]).attr('x2', x.range()[1]).attr('y1', y0).attr('y2', y0);
    let prevDay = null;
    ticks.forEach((t, i) => {
      const tx = x(t);
      g.append('line').attr('class', 'sw-axis-line').attr('x1', tx).attr('x2', tx).attr('y1', y0).attr('y2', y0 + 4);
      const day = fD(t);
      const tt = g.append('text').attr('x', tx).attr('y', y0 + 16).attr('text-anchor', 'middle');
      if (unit === 'time') {
        tt.text(fT(t));
        if (day !== prevDay) g.append('text').attr('class', 'sw-date').attr('x', tx).attr('y', y0 + 30).attr('text-anchor', 'middle').text(i === 0 ? day + ' UTC' : day);
      } else tt.text(i === 0 ? day + ' UTC' : day);
      prevDay = day;
    });
  };

  /* ---------- the one time chart (records, curves, small multiples)
     cfg: {H, x:[Date,Date], y:{domain, scale:'lin'|'symlog', ticks, fmt, label}, refs:[{v,label,cls}],
           lines:[{pts:[{t,v}], color, width, dash, opacity, step, extend, split:{v, below, color}}],
           dots:[{t,v,r,shape,fill,stroke,opacity,head,tip}], notes:[{t,v,text,color}], ends:[{v,text,color}]} */
  X.timeChart = (box, cfg) => {
    const { svg, W, H } = X.frame(box, cfg.H);
    const yfmt = cfg.y.fmt || ((v) => String(v));
    const yt = cfg.y.ticks || (cfg.y.scale === 'symlog' ? [] : d3.scaleLinear().domain(cfg.y.domain).ticks(cfg.H < 200 ? 3 : 5));
    const ml = Math.ceil(Math.max(24, ...yt.map((v) => X.measure(svg, yfmt(v))))) + 10;
    const refW = Math.max(0, ...(cfg.refs || []).flatMap((r) => String(r.label || '').split('|').map((t) => X.measure(svg, t))));
    const endTexts = (cfg.ends || []).map((e) => e.text);
    const endW = Math.min(W * 0.34, Math.max(0, ...endTexts.map((s) => X.measure(svg, s))));
    const mr = Math.ceil(Math.max(10, endW + 12, Math.min(refW + 10, W * 0.3)));
    const mt = cfg.y.label ? 24 : 12, mb = 36;
    const x = d3.scaleUtc(cfg.x, [ml, W - mr]);
    const y = (cfg.y.scale === 'symlog' ? d3.scaleSymlog().constant(cfg.y.c || 10) : d3.scaleLinear()).domain(cfg.y.domain).range([H - mb, mt]);
    const [ylo, yhi] = [Math.min(...cfg.y.domain), Math.max(...cfg.y.domain)];
    const cy = (v) => y(Math.max(ylo, Math.min(yhi, v)));
    const id = 'c' + Math.random().toString(36).slice(2, 8);
    svg.append('clipPath').attr('id', id).append('rect').attr('x', ml).attr('y', mt - 1).attr('width', W - mr - ml).attr('height', H - mb - mt + 2);
    const grid = svg.append('g').attr('class', 'sw-grid');
    yt.forEach((v) => {
      grid.append('line').attr('x1', ml).attr('x2', W - mr).attr('y1', y(v)).attr('y2', y(v));
      svg.append('text').attr('x', ml - 8).attr('y', y(v)).attr('dy', '0.32em').attr('text-anchor', 'end').text(yfmt(v));
    });
    if (cfg.y.label) svg.append('text').attr('x', 0).attr('y', 11).text(cfg.y.label);
    X.timeAxis(svg.append('g'), x, H - mb, svg);
    const refLabs = [];
    (cfg.refs || []).forEach((r) => {
      if (r.v < ylo || r.v > yhi) return;
      svg.append('line').attr('class', r.cls || 'sw-ref').attr('x1', ml).attr('x2', W - mr).attr('y1', y(r.v)).attr('y2', y(r.v));
      if (r.label) refLabs.push({ y: y(r.v), text: r.label });
    });
    refLabs.sort((a, b) => a.y - b.y).forEach((l, i, A) => { if (i && l.y - A[i - 1].y < 13) l.y = A[i - 1].y + 13; });
    if (!(cfg.ends || []).length) refLabs.forEach((l) => {
      const parts = String(l.text).split('|'), t = svg.append('text').attr('class', 'sw-lab-m').attr('x', W - mr + 6).attr('y', l.y - (parts.length > 1 ? 3 : -4));
      parts.forEach((p, i) => t.append('tspan').attr('x', W - mr + 6).attr('dy', i ? '1.15em' : 0).text(p));
    });
    const plot = svg.append('g').attr('clip-path', `url(#${id})`);
    (cfg.lines || []).forEach((L) => {
      let pts = L.pts.filter((p) => p.t && p.v !== null && p.v !== undefined);
      if (!pts.length) return;
      if (L.extend) pts = pts.concat([{ t: L.extend === true ? cfg.x[1] : L.extend, v: pts[pts.length - 1].v }]);
      const gen = d3.line().x((p) => x(p.t)).y((p) => Math.max(mt - 40, Math.min(H + 40, y(p.v)))).curve(L.step === false ? d3.curveLinear : d3.curveStepAfter);
      const draw = (g, color) => g.append('path').attr('d', gen(pts)).attr('fill', 'none').attr('stroke', color).attr('stroke-width', L.width || 2)
        .attr('stroke-linecap', 'round').attr('stroke-linejoin', 'round').attr('stroke-dasharray', L.dash || null).attr('opacity', L.opacity ?? 1);
      draw(plot, L.color);
      if (L.split && L.split.v >= ylo && L.split.v <= yhi) {
        const sid = id + 's' + Math.random().toString(36).slice(2, 6), yv = y(L.split.v);
        const r = svg.append('clipPath').attr('id', sid).append('rect').attr('x', ml).attr('width', W - mr - ml);
        if (L.split.below) r.attr('y', yv).attr('height', Math.max(0, H - mb - yv + 2)); else r.attr('y', mt - 2).attr('height', Math.max(0, yv - mt + 2));
        draw(plot.append('g').attr('clip-path', `url(#${sid})`), L.split.color);
      }
    });
    const dotsG = svg.append('g');
    const pick = [];
    let nclip = 0;
    (cfg.dots || []).forEach((d) => {
      if (!d.t || d.v === null || d.v === undefined) return;
      const px = x(d.t), off = d.v > yhi ? 1 : d.v < ylo ? -1 : 0, py = cy(d.v), r = d.r || 3.5;
      if (off) nclip += 1;
      if (off && cfg.hideOff) return;
      let s;
      if (off) s = dotsG.append('path').attr('d', `M${px - 4},${py + (off > 0 ? 3 : -3)}L${px + 4},${py + (off > 0 ? 3 : -3)}L${px},${py + (off > 0 ? -4 : 4)}Z`);
      else if (d.shape === 'diamond') s = dotsG.append('path').attr('d', `M${px},${py - r * 1.4}L${px + r * 1.4},${py}L${px},${py + r * 1.4}L${px - r * 1.4},${py}Z`);
      else if (d.shape === 'square') s = dotsG.append('rect').attr('x', px - r).attr('y', py - r).attr('width', 2 * r).attr('height', 2 * r).attr('rx', 1);
      else s = dotsG.append('circle').attr('cx', px).attr('cy', py).attr('r', r);
      s.attr('fill', d.fill || 'none').attr('stroke', d.stroke || 'none').attr('stroke-width', d.sw || 1.5).attr('opacity', d.opacity ?? 1);
      if (d.tip) pick.push({ px, py, d });
    });
    /* annotations: try four spots around the point, never over another label or outside the plot */
    const boxes = [];
    (cfg.notes || []).forEach((n) => {
      const px = x(n.t), py = cy(n.v), w = X.measure(svg, n.text, 'sw-lab') + 2, h = 13;
      const below = [[8, 18], [-8 - w, 18], [8, 32], [-8 - w, 32]], above = [[8, -8], [-8 - w, -8], [8, -22], [-8 - w, -22]];
      const spots = cfg.noteSide === 'above' ? above.concat(below) : below.concat(above);
      let best = null;
      for (const [dx, dy] of spots) {
        const bx = px + dx, by = py + dy - 10;
        if (bx < ml || bx + w > W - 2 || by < 0 || by + h > H - mb) continue;
        if (boxes.some((b) => bx < b.x + b.w && bx + w > b.x && by < b.y + b.h && by + h > b.y)) continue;
        if ((cfg.dots || []).some((d) => d.r >= 4 && d.t && d.v !== null && Math.abs(x(d.t) - (bx + w / 2)) < w / 2 + 4 && Math.abs(cy(d.v) - (by + h / 2)) < h / 2 + 4)) continue;
        best = { x: bx, y: by, w, h }; break;
      }
      if (!best) return;
      boxes.push(best);
      svg.append('text').attr('class', 'sw-lab').attr('x', best.x).attr('y', best.y + 10).style('fill', n.color || null).style('font-weight', n.bold ? 600 : null).text(n.text);
    });
    /* end labels, pushed apart */
    const ends = (cfg.ends || []).map((e) => ({ y: cy(e.v), text: e.text, color: e.color })).sort((a, b) => a.y - b.y);
    ends.forEach((e, i) => { if (i && e.y - ends[i - 1].y < 13) e.y = ends[i - 1].y + 13; });
    const over = ends.length ? ends[ends.length - 1].y - (H - mb) : 0;
    if (over > 0) ends.forEach((e) => { e.y -= over; });
    ends.forEach((e) => {
      const t = svg.append('text').attr('class', 'sw-lab-m').attr('x', W - mr + 6).attr('y', e.y).attr('dy', '0.32em').style('fill', e.color || null).text(e.text);
      let s = e.text; while (t.node().getComputedTextLength() > mr - 8 && s.length > 4) { s = s.slice(0, -2); t.text(s + '…'); }
    });
    /* hover: nearest point inside 28 px */
    const tip = X.tip(box);
    const ring = svg.append('circle').attr('r', 7).attr('fill', 'none').attr('stroke', 'var(--color-fg)').attr('stroke-width', 1.5).attr('visibility', 'hidden');
    const del = pick.length ? d3.Delaunay.from(pick, (p) => p.px, (p) => p.py) : null;
    svg.on('pointermove', (ev) => {
      if (!del) return;
      const [mx, my] = d3.pointer(ev);
      const k = del.find(mx, my), p = pick[k];
      if (!p || Math.hypot(p.px - mx, p.py - my) > 28) { tip.hide(); ring.attr('visibility', 'hidden'); return; }
      ring.attr('cx', p.px).attr('cy', p.py).attr('visibility', 'visible');
      const sx = box.clientWidth / W;
      tip.show(p.px * sx, p.py * sx, p.d.head, p.d.tip);
    }).on('pointerleave', () => { tip.hide(); ring.attr('visibility', 'hidden'); });
    return { x, y, W, H, nclip, ml, mr };
  };

  /* ---------- key items */
  X.key = (box, items) => {
    box.replaceChildren();
    items.filter(Boolean).forEach(([kind, color, label]) => {
      const s = X.el('span');
      const sv = d3.select(s).append('svg').attr('width', 18).attr('height', 12);
      if (kind === 'line') sv.append('line').attr('x1', 1).attr('x2', 17).attr('y1', 6).attr('y2', 6).attr('stroke', color).attr('stroke-width', 2).attr('stroke-linecap', 'round');
      else if (kind === 'dash') sv.append('line').attr('x1', 1).attr('x2', 17).attr('y1', 6).attr('y2', 6).attr('stroke', color).attr('stroke-width', 1.5).attr('stroke-dasharray', '4 3');
      else if (kind === 'dot') sv.append('circle').attr('cx', 9).attr('cy', 6).attr('r', 4).attr('fill', color);
      else if (kind === 'ring') sv.append('circle').attr('cx', 9).attr('cy', 6).attr('r', 4).attr('fill', 'none').attr('stroke', color).attr('stroke-width', 1.5);
      else if (kind === 'small') sv.append('circle').attr('cx', 9).attr('cy', 6).attr('r', 2.2).attr('fill', color);
      else if (kind === 'diamond') sv.append('path').attr('d', 'M9,1L14,6L9,11L4,6Z').attr('fill', color);
      else if (kind === 'square') sv.append('rect').attr('x', 5).attr('y', 2).attr('width', 8).attr('height', 8).attr('fill', 'none').attr('stroke', color).attr('stroke-width', 1.5);
      else if (kind === 'tri') sv.append('path').attr('d', 'M5,9L13,9L9,2Z').attr('fill', color);
      else if (kind === 'box') sv.append('rect').attr('x', 1).attr('y', 1).attr('width', 16).attr('height', 10).attr('fill', color).attr('opacity', 0.25);
      s.appendChild(X.el('span', null, label));
      box.appendChild(s);
    });
  };
  X.tabs = {};
  X.active = () => (document.querySelector('.sw-tab[aria-selected="true"]') || {}).dataset?.tab || 'leader';
  window.__swTab = () => X.active();
})();
