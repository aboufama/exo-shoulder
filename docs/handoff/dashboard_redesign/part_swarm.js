
  /* ---------- leader ---------- */
  function drawHero() {
    const card = $('leader-card'), body = $('leader-body'), st = stOf('ranking', 'summary');
    body.replaceChildren(); body.classList.toggle('dash-skeleton', st === 'loading');
    card.setAttribute('data-win', '0');
    if (st !== 'ok') { if (st !== 'loading') body.appendChild(el('div', 'sw-msg sw-failed', 'Failed to load')); return; }
    const R = rowsOf('ranking'), S = rowsOf('summary')[0] || {}, base = R.find((r) => r.is_baseline), lead = R.find((r) => r.rank === 1);
    const main = el('div', 'sw-hero-main'), side = el('div', 'sw-hero-side');
    body.append(main, side);
    if (!lead) {
      main.appendChild(el('div', 'sw-badges')).appendChild(el('span', 'sw-badge', 'No leader yet'));
      main.appendChild(el('h3', 'sw-hero-name', 'Nothing on the bench yet'));
      const p = el('p', 'sw-verdict', 'The leader appears here as soon as the first morphology is screened. ');
      if (base && base.gap !== null) { p.append('The bar to beat: the 3R baseline’s gap of '); p.appendChild(mark(el('b', null, gapf(base.gap)), 'ranking', 'gap', 'id=' + enc(base.id))); p.append(' points.'); }
      else p.append('The 3R baseline has not been measured on the bench yet.');
      main.appendChild(p);
    } else {
      const win = lead.winner, W = 'id=' + enc(lead.id), sol = solid(lead);
      card.setAttribute('data-win', win ? '1' : '0');
      const badges = main.appendChild(el('div', 'sw-badges'));
      badges.appendChild(el('span', win && sol ? 'sw-badge sw-badge-acc' : win ? 'sw-badge sw-badge-line sw-badge-claim' : 'sw-badge', '#1 Leader'));
      badges.appendChild(lead.verified ? el('span', 'sw-badge sw-badge-ok', '✓ Verified') : el('span', 'sw-badge sw-badge-claim', lead.remeasured ? 'Re-measured, verdict pending' : 'Claimed: not re-measured yet'));
      if (S.leader_since && Date.now() - date(S.leader_since) < 3 * 3600e3) {
        const nb = badges.appendChild(el('span', 'sw-badge sw-badge-new', 'NEW · took the lead '));
        const ts = nb.appendChild(mark(el('time', null, ago(S.leader_since)), 'summary', 'leader_since', 0)); ts.setAttribute('datetime', S.leader_since); ts.title = tUTC(date(S.leader_since));
      }
      badges.appendChild(el('span', win ? 'sw-badge sw-badge-line' : 'sw-badge', win ? 'Beats the 3R baseline' : 'Does not beat the 3R baseline yet'));
      main.appendChild(mark(el('h3', 'sw-hero-name', lead.name), 'ranking', 'name', W));
      const sub = main.appendChild(el('p', 'sw-hero-sub'));
      const bits = [];
      if (lead.family) bits.push([mark(el('span', null, lead.family), 'ranking', 'family', W)]);
      if (lead.lens) bits.push(['lens: ', mark(el('span', null, lead.lens), 'ranking', 'lens', W)]);
      if (lead.active_dof !== null) {
        const b = [mark(el('span', null, String(lead.active_dof)), 'ranking', 'active_dof', W), ' active DOF'];
        if (lead.passive_dof) b.push(' + ', mark(el('span', null, String(lead.passive_dof)), 'ranking', 'passive_dof', W), ' passive');
        bits.push(b);
      }
      if (lead.n_configs !== null) bits.push([mark(el('span', null, String(lead.n_configs)), 'ranking', 'n_configs', W), ' configurations tried']);
      bits.forEach((b, i) => { if (i) sub.append(' · '); sub.append(...b); });
      const gr = main.appendChild(el('div', 'sw-gaprow'));
      const big = mark(el('span', 'sw-big', gapf(lead.gap)), 'ranking', 'gap', W); big.setAttribute('data-win', win ? '1' : '0'); if (win && !sol) big.style.opacity = 0.6; gr.appendChild(big);
      const cap = gr.appendChild(el('span', 'sw-bigcap'));
      cap.appendChild(el('span', null, 'points short of the bench targets · lower is better'));
      if (base && base.gap !== null) {
        const l2 = cap.appendChild(el('span')); l2.append('3R baseline: '); l2.appendChild(mark(el('b', null, gapf(base.gap)), 'ranking', 'gap', 'id=' + enc(base.id)));
        if (S.margin !== null && S.margin !== undefined) {
          l2.append(' · ');
          l2.appendChild(mark(el('b', S.margin > 0 ? 'sw-acc' : null, F1(Math.abs(S.margin))), 'summary', 'margin', 0));
          l2.append(S.margin > 0 ? ' points better' : ' points behind');
        }
      }
      if (lead.remeasured && lead.claimed_gap !== null && lead.claimed_gap !== lead.gap) {
        const c3 = cap.appendChild(el('span')); c3.append('verifier’s number; its own agent claimed '); c3.appendChild(mark(el('span', null, gapf(lead.claimed_gap)), 'ranking', 'claimed_gap', W));
      }
      const met = main.appendChild(el('div', 'sw-meters'));
      [['inband14', 'Metal 2–14 mm from skin', 0.9], ['follow', 'Motion frames followed', 0.95], ['reach', 'Everyday poses reached', 0.9]].forEach(([f, label, tgt]) => {
        const v = num(lead[f]), bv = base ? num(base[f]) : null, m = met.appendChild(el('div', 'sw-meter'));
        const top = m.appendChild(el('div', 'sw-meter-top')); top.appendChild(el('span', null, label)); top.appendChild(mark(el('b', null, pct(v)), 'ranking', f, W));
        const tr = m.appendChild(el('div', 'sw-track')), fill = tr.appendChild(el('div', 'sw-fill'));
        fill.style.width = ((v || 0) * 100) + '%'; fill.setAttribute('data-better', v !== null && (bv === null || v > bv) ? '1' : '0');
        const tt = tr.appendChild(el('i', 'sw-tick sw-tick-t')); tt.style.left = (tgt * 100) + '%';
        if (bv !== null) { const tb = tr.appendChild(el('i', 'sw-tick sw-tick-b')); tb.style.left = (bv * 100) + '%'; }
        const c = m.appendChild(el('div', 'sw-meter-cap')); c.append('target ' + P0(tgt));
        if (bv !== null) { c.append(' · baseline '); c.appendChild(mark(el('span', null, pct(bv)), 'ranking', f, 'id=' + enc(base.id))); }
      });
      const key1 = main.appendChild(el('div', 'sw-key'));
      [['sw-kbar', 'leader (accent where it is better than the baseline)'], ['sw-ktick sw-tick-t', 'target'], ['sw-ktick sw-tick-b', '3R baseline'], ['', 'higher is better on all three']].forEach(([c, t]) => {
        const sp = key1.appendChild(el('span')); if (c) sp.appendChild(el('i', c)); sp.append(t);
      });
      if (lead.verdict || lead.note) {
        const v = main.appendChild(el('p', 'sw-verdict'));
        if (lead.verdict) { v.append('Verdict: '); v.appendChild(mark(el('b', null, lead.verdict), 'ranking', 'verdict', W)); }
        if (lead.note) { if (lead.verdict) v.append(' · '); v.appendChild(mark(el('span', null, lead.note), 'ranking', 'note', W)); }
      }
    }
    side.appendChild(el('h3', 'sw-side-h', 'Runners-up'));
    const runners = R.filter((r) => r.rank !== null && r.rank > 1).sort((a, b) => a.rank - b.rank).slice(0, 5);
    if (!runners.length) { side.appendChild(el('p', 'sw-note', lead ? 'No other morphology is ranked yet.' : 'Ranked morphologies appear here.')); return; }
    const ol = side.appendChild(el('ol', 'sw-runners'));
    runners.forEach((r) => {
      const c = cls(r), li = ol.appendChild(el('li', 'sw-runner')), W = 'id=' + enc(r.id); li.setAttribute('data-win', c === 'win' ? '1' : c === 'claim' ? 'claim' : '0');
      const rk = li.appendChild(el('span', 'sw-runner-rank', '#')); rk.appendChild(mark(el('span', null, String(r.rank)), 'ranking', 'rank', W));
      const nm = li.appendChild(el('span', 'sw-runner-name')); nm.appendChild(mark(el('span', null, r.name), 'ranking', 'name', W));
      if (c === 'win') nm.appendChild(el('small', null, 'beats the baseline · ' + (r.verified ? 'verified' : 're-measured')));
      else if (c === 'claim') { const ch = nm.appendChild(el('span', 'sw-chip', 'claimed: beats the baseline, not re-measured')); ch.setAttribute('data-s', 'claim'); }
      else nm.appendChild(el('small', null, r.verified ? 'verified' : STATUS_WORDS[r.status] || r.status));
      const g = li.appendChild(el('span', 'sw-runner-gap')); g.appendChild(mark(el('span', null, gapf(r.gap)), 'ranking', 'gap', W)); g.appendChild(el('small', null, ' pts'));
    });
  }

  /* ---------- record over time ---------- */
  let metric = 'gap';
  (function () {
    const seg = $('record-metric');
    Object.values(MET).forEach((M) => { const b = el('button', null, M.short); b.type = 'button'; b.dataset.m = M.key; b.setAttribute('aria-pressed', String(M.key === metric)); seg.appendChild(b); });
    seg.addEventListener('click', (ev) => { const b = ev.target.closest('button[data-m]'); if (!b) return; metric = b.dataset.m; seg.querySelectorAll('button').forEach((x) => x.setAttribute('aria-pressed', String(x === b))); drawRecord(); });
  })();
  function drawRecord() {
    const M = MET[metric], box = $('record-chart'), st = stOf('ranking', 'records'), isGap = M.key === 'gap';
    $('record-dir').textContent = M.dir < 0 ? '↓ lower is better' : '↑ higher is better';
    $('record-note').textContent = 'Each dot is one morphology, placed at the time the bench screened it, at its ' + M.title + ' (the verifier’s number where it re-measured one). The solid step line is the record: the best so far, stepping each time a morphology beats it; it is dashed where the record holder’s number is still its own agent’s claim. ' +
      (isGap ? 'Dot colour: does it beat the 3R baseline’s gap? ' : 'Dot colour still means “beats the 3R baseline overall (on gap)”; the shaded band is where a dot is better than the baseline on this one measure. ') + M.what + ' Times in UTC.';
    const R = rowsOf('ranking'), base = R.find((r) => r.is_baseline), bv = base ? num(base[M.key]) : null;
    const pts = R.filter((r) => !r.is_baseline && r.t_screened && num(r[M.key]) !== null);
    const kItems = isGap ? [['win', 'beats the baseline (re-measured)'], ['claim', 'beats it, claimed'], ['other', 'does not beat it'], ['out', 'refuted or dropped']]
      : [['win', 'beats the baseline overall (gap), re-measured'], ['claim', 'beats it overall, claimed'], ['other', 'does not beat it overall'], ['out', 'refuted or dropped']];
    const keyItems = [['record', 'record (best so far)'], ['recclaim', 'record set by a claim']].concat(kItems);
    if (bv !== null) keyItems.push(['baseline', '3R baseline'], ['zone', isGap ? 'better than the baseline' : 'better than the baseline on this measure']);
    keyItems.push(['target', M.targetText]);
    if (!ready(box, st, pts.length ? null : 'Nothing screened yet. A dot appears here for each morphology the bench measures, and the record line steps as better ones arrive.')) { key($('record-key'), keyItems); return; }
    if (!box.clientWidth) return;
    const narrow = box.clientWidth < 560, H = narrow ? 290 : 350, { svg, W } = frame(box, H);
    const recs = rowsOf('records').filter((r) => r.metric === M.key && r.t).map((r) => ({ ...r, tt: +date(r.t), v: num(r.value) })).sort((a, b) => a.tt - b.tt);
    const live = pts.filter((r) => !['refuted', 'dead'].includes(r.status)).map((r) => num(r[M.key]));
    const [lo, hi] = robust(live.length ? live : pts.map((r) => num(r[M.key])), [M.target, bv].concat(recs.map((r) => r.v)).filter((v) => v !== null), 0, isGap ? undefined : 1);
    const mt = 26, mb = 26;
    const y = d3.scaleLinear([lo, hi], [H - mb, mt]), Y = yTicks(svg, y, narrow ? 4 : 6, M.axis);
    // the baseline and target are named in the right margin, outside the data
    const rl = [];
    if (bv !== null) rl.push({ v: bv, a: narrow ? 'baseline' : '3R baseline', b: M.fmt(bv), c: 'var(--color-fg)' });
    if (M.target >= lo && M.target <= hi) rl.push({ v: M.target, a: M.targetText.split(' ')[0], b: M.axis(M.target), c: 'var(--color-ok)' });
    const mr = rl.length ? Math.ceil(d3.max(rl, (l) => Math.max(measure(svg, l.a), measure(svg, l.b)))) + 12 : 10, ml = Math.ceil(Y.w) + 12;
    const ts = pts.map((r) => +date(r.t_screened)), x = d3.scaleUtc(timeDomain(ts), [ml, W - mr]);
    const g = svg.append('g'), cy = (v) => y(Math.max(lo, Math.min(hi, v)));
    drawGridY(g, y, Y.t, M.axis, ml, W - mr);
    drawTimeX(g, x, H - mb, svg);
    g.append('text').attr('x', 0).attr('y', 12).text(M.axisTitle + (M.dir < 0 ? ' ↓' : ' ↑'));
    const obst = [];
    if (bv !== null) {
      const yb = cy(bv), z0 = M.dir < 0 ? yb : mt, z1 = M.dir < 0 ? H - mb : yb;
      g.append('rect').attr('x', ml).attr('width', W - mr - ml).attr('y', Math.min(z0, z1)).attr('height', Math.abs(z1 - z0)).style('fill', ACC()).style('fill-opacity', 0.07);
      g.append('line').attr('x1', ml).attr('x2', W - mr).attr('y1', yb).attr('y2', yb).style('stroke', 'var(--color-fg)').style('stroke-width', 1.5).style('stroke-dasharray', '6 4');
    }
    if (M.target >= lo && M.target <= hi) g.append('line').attr('x1', ml).attr('x2', W - mr).attr('y1', y(M.target)).attr('y2', y(M.target)).style('stroke', 'var(--color-ok)').style('stroke-width', 1.5).style('stroke-dasharray', '6 4');
    const rtaken = [];
    rl.sort((a, b) => cy(a.v) - cy(b.v)).forEach((l) => {
      const yy = nudgeY(cy(l.v), 26, W - mr + 2, W, rtaken, 0, H - mb + 12);
      rtaken.push([W - mr + 2, yy - 13, W, yy + 13]);
      g.append('text').attr('x', W - mr + 6).attr('y', yy - 2).style('fill', l.c).style('font-weight', 600).text(l.a);
      g.append('text').attr('x', W - mr + 6).attr('y', yy + 11).style('fill', l.c).text(l.b);
    });
    if (recs.length) {
      const P = recs.map((r) => [x(r.tt), cy(r.v)]), gl = g.append('g');
      recs.forEach((r, i) => {
        const x1 = i + 1 < recs.length ? P[i + 1][0] : W - mr, seg = (i ? [[P[i][0], P[i - 1][1]]] : []).concat([P[i], [x1, P[i][1]]]);
        gl.append('path').attr('d', d3.line()(seg)).style('fill', 'none').style('stroke', 'var(--color-fg)').style('stroke-width', 2).style('stroke-opacity', 0.85)
          .style('stroke-dasharray', r.claimed ? '5 4' : null).attr('stroke-linejoin', 'round');
        obst.push(...pathBoxes(seg));
      });
    }
    const order = { other: 0, out: 1, claim: 2, win: 3 }, rad = narrow ? 4.5 : 5.5;
    const D = pts.map((r) => { const v = num(r[M.key]); return { r, c: cls(r), lead: r.rank === 1, x: x(+date(r.t_screened)), y: cy(v), v, clip: v > hi ? 1 : v < lo ? -1 : 0 }; })
      .sort((a, b) => order[a.c] - order[b.c] || a.lead - b.lead);
    D.forEach((d) => { if (d.clip) d.y = d.clip > 0 ? mt - 2 : H - mb + 2; });
    const gd = g.append('g');
    gd.selectAll('circle').data(D.filter((d) => !d.clip)).join('circle').attr('cx', (d) => d.x).attr('cy', (d) => d.y).call(dotStyle, rad);
    D.filter((d) => d.clip).forEach((d) => tri(gd, d.x, d.y + (d.clip > 0 ? 4 : -4), d.clip > 0 ? 0 : 180, 'var(--color-fg-muted)'));
    const nclip = D.filter((d) => d.clip).length;
    if (nclip) keyItems.push(['clip', nclip + ' off the scale (hover for the value)']);
    D.forEach((d) => obst.push(dotBox(d.x, d.y, d.lead ? rad + 4.5 : rad)));
    const leadD = D.find((d) => d.lead);
    if (leadD && !leadD.clip) g.append('circle').attr('cx', leadD.x).attr('cy', leadD.y).attr('r', rad + 4.5).style('fill', 'none').style('stroke', leadD.c === 'win' || leadD.c === 'claim' ? ACC() : 'var(--color-fg)').style('stroke-width', 1.5);
    const labelled = [];
    if (leadD && !leadD.clip) labelled.push(leadD);
    recs.map((r) => r.id).reverse().forEach((id) => { const d = D.find((q) => q.r.id === id); if (d && !d.clip && !labelled.includes(d)) labelled.push(d); });
    const items = labelled.slice(0, narrow ? 4 : 7).map((d) => ({ x: d.x, y: d.y, r: d.lead ? rad + 4.5 : rad, text: short(d.r.name, narrow ? 20 : 30) }));
    placeLabels(g.append('g'), svg, items, [ml, mt - 4, W - mr, H - mb], obst);
    hover(svg, D.map((d) => ({ x: d.x, y: d.y, r: d.lead ? rad + 1.5 : rad, d })), (ev, p) => morphTip(ev, p.d.r));
    key($('record-key'), keyItems);
  }

  /* ---------- where each lands ---------- */
  function drawLands() {
    const box = $('lands-chart'), st = stOf('ranking'), R = rowsOf('ranking');
    const pts = R.filter((r) => num(r.reach) !== null && num(r.inband14) !== null), base = pts.find((r) => r.is_baseline);
    const keyItems = [['win', 'beats the baseline (re-measured)'], ['claim', 'beats it, claimed'], ['other', 'does not beat it'], ['out', 'refuted or dropped'], ['base', '3R baseline'], ['corner', 'both targets met']];
    if (!ready(box, st, pts.filter((r) => !r.is_baseline).length ? null : 'Nothing screened yet. Each screened morphology lands here by its reach and its share of metal 2–14 mm from the skin.')) { key($('lands-key'), keyItems); return; }
    if (!box.clientWidth) return;
    const narrow = box.clientWidth < 480, H = Math.round(Math.max(280, Math.min(420, box.clientWidth * 0.7))), { svg, W } = frame(box, H);
    const live = pts.filter((r) => !['refuted', 'dead'].includes(r.status));
    const x0 = robust((live.length ? live : pts).map((r) => num(r.reach)), [0.9], 0, 1)[0], y0 = robust((live.length ? live : pts).map((r) => num(r.inband14)), [0.9], 0, 1)[0];
    const mt = 12, mb = 38, y = d3.scaleLinear([y0, 1], [H - mb, mt]), Y = yTicks(svg, y, 5, P0);
    const ml = Math.ceil(Y.w) + 28, mr = 14, x = d3.scaleLinear([x0, 1], [ml, W - mr]);
    const g = svg.append('g');
    drawGridY(g, y, Y.t, P0, ml, W - mr);
    x.ticks(narrow ? 4 : 6).forEach((v) => {
      g.append('line').attr('x1', x(v)).attr('x2', x(v)).attr('y1', mt).attr('y2', H - mb).style('stroke', 'var(--cds-chart-grid)');
      g.append('text').attr('x', x(v)).attr('y', H - mb + 15).attr('text-anchor', 'middle').text(P0(v));
    });
    g.append('text').attr('x', (ml + W - mr) / 2).attr('y', H - 4).attr('text-anchor', 'middle').text('everyday arm poses reached →');
    g.append('text').attr('transform', `translate(11,${(mt + H - mb) / 2}) rotate(-90)`).attr('text-anchor', 'middle').text('metal 2–14 mm from the skin →');
    const cx0 = x(0.9), cy0 = y(0.9);
    g.append('rect').attr('x', cx0).attr('y', mt).attr('width', Math.max(0, W - mr - cx0)).attr('height', Math.max(0, cy0 - mt)).style('fill', 'var(--color-ok)').style('fill-opacity', 0.12);
    g.append('path').attr('d', `M${cx0},${H - mb}V${cy0}M${ml},${cy0}H${W - mr}`).style('stroke', 'var(--color-ok)').style('stroke-width', 1.2).style('stroke-dasharray', '5 4').style('fill', 'none');
    const obst = [];
    const ct = 'both targets', ctw = measure(svg, ct);
    if (W - mr - cx0 > ctw + 8 && cy0 - mt > 16) { g.append('text').attr('class', 'sw-lab-m').attr('x', W - mr - 4).attr('y', mt + 13).attr('text-anchor', 'end').style('fill', 'var(--color-ok)').text(ct); obst.push([W - mr - 8 - ctw, mt, W - mr, mt + 16]); }
    const rad = narrow ? 4.5 : 5.5, order = { other: 0, out: 1, claim: 2, win: 3, base: 4 };
    const D = pts.map((r) => {
      const rv = num(r.reach), iv = num(r.inband14), cxv = rv < x0 ? -1 : 0, cyv = iv < y0 ? -1 : 0;
      return { r, c: cls(r), lead: r.rank === 1, x: cxv ? ml - 1 : x(rv), y: cyv ? H - mb + 1 : y(iv), clip: cxv || cyv, cx: cxv, cy: cyv };
    }).sort((a, b) => order[a.c] - order[b.c] || a.lead - b.lead);
    const gd = g.append('g');
    gd.selectAll('circle').data(D.filter((d) => d.c !== 'base' && !d.clip)).join('circle').attr('cx', (d) => d.x).attr('cy', (d) => d.y).call(dotStyle, rad);
    D.filter((d) => d.clip).forEach((d) => tri(gd, d.x + (d.cx ? 4 : 0), d.y - (d.cy && !d.cx ? 4 : 0), d.cx ? -90 : 180, d.c === 'win' || d.c === 'claim' ? ACC() : 'var(--color-fg-muted)'));
    const nclip = D.filter((d) => d.clip).length;
    if (nclip) keyItems.push(['clip', nclip + ' off the scale (drawn at the edge; hover for the value)']);
    D.forEach((d) => obst.push(dotBox(d.x, d.y, d.lead ? rad + 4.5 : d.c === 'base' ? rad + 1 : rad)));
    if (base) {
      const d = D.find((q) => q.c === 'base');
      if (!d.clip) gd.append('path').attr('transform', `translate(${d.x},${d.y})`).attr('d', d3.symbol(d3.symbolDiamond, 110)()).style('fill', 'var(--color-fg)').style('stroke', 'var(--color-panel)').style('stroke-width', 1.5);
    }
    const leadD = D.find((d) => d.lead);
    if (leadD && !leadD.clip) g.append('circle').attr('cx', leadD.x).attr('cy', leadD.y).attr('r', rad + 4.5).style('fill', 'none').style('stroke', ACC()).style('stroke-width', 1.5);
    const lab = D.filter((d) => !d.clip && (d.c === 'base' || d.lead)).concat(D.filter((d) => !d.clip && (d.c === 'win' || d.c === 'claim') && !d.lead).sort((a, b) => a.r.rank - b.r.rank))
      .slice(0, narrow ? 4 : 7).map((d) => ({ x: d.x, y: d.y, r: d.lead ? rad + 4.5 : rad, text: d.c === 'base' ? '3R baseline' : short(d.r.name, narrow ? 18 : 26) }));
    placeLabels(g.append('g'), svg, lab, [ml, 0, W - mr, H - mb], obst);
    hover(svg, D.map((d) => ({ x: d.x, y: d.y, r: rad, d })), (ev, p) => morphTip(ev, p.d.r));
    key($('lands-key'), keyItems);
  }

  /* ---------- optimisation inside each morphology ---------- */
  function drawTuning() {
    const box = $('tuning-chart'), st = stOf('sweeps', 'ranking'), R = rowsOf('ranking'), byId = new Map(R.map((r) => [r.id, r]));
    const base = R.find((r) => r.is_baseline), bv = base ? num(base.gap) : null;
    const groups = d3.groups(rowsOf('sweeps').filter((s) => num(s.best_gap) !== null && byId.has(s.id)), (s) => s.id)
      .map(([id, ss]) => ({ id, r: byId.get(id), pts: ss.map((s) => ({ k: num(s.k), v: num(s.best_gap), g: num(s.gap) })).sort((a, b) => a.k - b.k) }));
    const keyItems = [['lead', 'leader'], ['winline', 'beats the baseline'], ['otherline', 'others'], ['outline', 'refuted or dropped (dashed)'], ['vring', 'verifier’s re-measured gap'], ['baseline', '3R baseline']];
    if (!ready(box, st, groups.length ? null : 'No sweep recorded yet. Each morphology’s optimisation trace appears here as its agent tunes it.')) { key($('tuning-key'), keyItems); return; }
    if (!box.clientWidth) return;
    const narrow = box.clientWidth < 480, H = Math.round(Math.max(280, Math.min(420, box.clientWidth * 0.7))), { svg, W } = frame(box, H);
    // y: 0 (every target met) up to about 1.5x the baseline; the long first climbs of poor configurations are clipped
    const ends = groups.map((gr) => gr.pts[gr.pts.length - 1].v);
    let hi = robust(ends, [0, bv].filter((v) => v !== null), 0)[1];
    if (bv !== null) hi = Math.max(Math.min(hi, bv * 1.5), bv * 1.15);
    hi = Math.max(hi, (d3.max(groups.filter((gr) => gr.r.rank !== null && gr.r.rank <= 6), (gr) => gr.pts[gr.pts.length - 1].v) || 0) * 1.08);
    const mt = 22, mb = 30, y = d3.scaleLinear([0, hi], [H - mb, mt]), Y = yTicks(svg, y, 5, d3.format('~f'));
    // x: from the sweeps that show on the scale; one far longer than the rest is cut at ~1.5x the 90th-percentile length
    const vis = groups.filter((gr) => gr.pts.some((p) => p.v <= hi)), lens = vis.map((gr) => gr.pts[gr.pts.length - 1].k).sort(d3.ascending);
    const kmax = Math.max(2, Math.min(d3.max(lens) || 2, Math.max(10, Math.ceil(1.5 * (d3.quantile(lens, 0.9) || 2)))));
    const hl = vis.filter((gr) => gr.r.winner || gr.r.rank === 1).sort((a, b) => a.r.rank - b.r.rank).slice(0, narrow ? 4 : 6);
    const lw = d3.max(hl, (gr) => measure(svg, short(gr.r.name, narrow ? 14 : 22), 'sw-lab')) || 0;
    const ml = Math.ceil(Y.w) + 12, bl = bv !== null && bv <= hi ? Math.max(measure(svg, narrow ? 'baseline' : '3R baseline'), measure(svg, F1(bv))) + 12 : 0;
    const mr = Math.max(bl, hl.some((gr) => gr.pts[gr.pts.length - 1].k >= kmax * 0.6) ? lw + 14 : 0, 12);
    const x = d3.scaleLinear([1, kmax], [ml, W - mr]);
    const g = svg.append('g');
    drawGridY(g, y, Y.t, d3.format('~f'), ml, W - mr);
    x.ticks(narrow ? 4 : 6).filter((v) => Number.isInteger(v)).forEach((v) => g.append('text').attr('x', x(v)).attr('y', H - mb + 15).attr('text-anchor', 'middle').text(v));
    g.append('line').attr('x1', ml).attr('x2', W - mr).attr('y1', H - mb).attr('y2', H - mb).style('stroke', 'var(--cds-chart-axis)');
    g.append('text').attr('x', W - mr).attr('y', H - 2).attr('text-anchor', 'end').text('configurations tried →');
    g.append('text').attr('x', 0).attr('y', 11).text('best gap so far (points) ↓');
    const cid = 'swclip' + Math.random().toString(36).slice(2, 8);
    svg.append('clipPath').attr('id', cid).append('rect').attr('x', ml).attr('y', mt - 2).attr('width', W - mr - ml + 1).attr('height', H - mb - mt + 4);
    const taken = [];
    if (bv !== null && bv <= hi) {
      g.append('line').attr('x1', ml).attr('x2', W - mr).attr('y1', y(bv)).attr('y2', y(bv)).style('stroke', 'var(--color-fg)').style('stroke-width', 1.5).style('stroke-dasharray', '6 4');
      g.append('text').attr('x', W - mr + 6).attr('y', y(bv) - 2).style('fill', 'var(--color-fg)').style('font-weight', 600).text(narrow ? 'baseline' : '3R baseline');
      g.append('text').attr('x', W - mr + 6).attr('y', y(bv) + 11).style('fill', 'var(--color-fg)').text(F1(bv));
      taken.push([W - mr + 2, y(bv) - 13, W, y(bv) + 14]);
    }
    const line = d3.line().x((p) => x(p.k)).y((p) => y(Math.min(p.v, hi * 1.02))).curve(d3.curveStepAfter);
    const lines = g.append('g').attr('clip-path', `url(#${cid})`);
    const style = (gr) => (gr.r.rank === 1 ? [ACC(), 2.75, 1] : gr.r.winner ? [ACC(), 1.6, gr.r.remeasured || gr.r.verified ? 0.75 : 0.45] : ['var(--color-fg-muted)', 1.2, 0.45]);
    const sorted = groups.slice().sort((a, b) => (style(a)[1] - style(b)[1]));
    lines.selectAll('path').data(sorted).join('path').attr('d', (gr) => line(gr.pts)).style('fill', 'none')
      .style('stroke', (gr) => style(gr)[0]).style('stroke-width', (gr) => style(gr)[1]).style('stroke-opacity', (gr) => style(gr)[2])
      .style('stroke-dasharray', (gr) => (['refuted', 'dead'].includes(gr.r.status) ? '3 3' : null)).attr('stroke-linejoin', 'round');
    // sweeps that run past the cut: an arrow at the edge
    const longer = groups.filter((gr) => gr.pts[gr.pts.length - 1].k > kmax && gr.pts.some((p) => p.v <= hi));
    longer.forEach((gr) => {
      const p = gr.pts.filter((q) => q.k <= kmax).pop(); if (!p) return;
      g.append('text').attr('x', W - mr - 2).attr('y', y(Math.min(p.v, hi))).attr('dy', '0.32em').attr('text-anchor', 'end').style('fill', style(gr)[0]).text('→');
    });
    if (longer.length) keyItems.push(['', '→ continues past the edge (' + longer.length + ')']);
    const startAbove = groups.filter((gr) => gr.pts[0].v > hi && gr.pts[gr.pts.length - 1].v <= hi).length, allAbove = groups.filter((gr) => gr.pts[gr.pts.length - 1].v > hi);
    allAbove.forEach((gr) => { const k = Math.min(gr.pts[gr.pts.length - 1].k, kmax); tri(g, x(k), mt - 2, 0, 'var(--color-fg-muted)', 40); });
    if (startAbove) keyItems.push(['clip', startAbove + (startAbove === 1 ? ' sweep starts' : ' sweeps start') + ' above the top']);
    if (allAbove.length) keyItems.push(['clip', allAbove.length + (allAbove.length === 1 ? ' sweep stays' : ' sweeps stay') + ' above the top (hover the ▲)']);
    // the verifier's gap at the end of each re-measured trace
    groups.filter((gr) => gr.r.remeasured && num(gr.r.gap) !== null && num(gr.r.gap) <= hi).forEach((gr) => {
      const k = Math.min(gr.pts[gr.pts.length - 1].k, kmax);
      g.append('circle').attr('cx', x(k)).attr('cy', y(gr.r.gap)).attr('r', 4.5).style('fill', 'var(--color-panel)').style('fill-opacity', 0.6).style('stroke', 'var(--color-fg)').style('stroke-width', 1.4);
      taken.push(dotBox(x(k), y(gr.r.gap), 5));
    });
    // end labels at each highlighted line's real end
    const labs = hl.map((gr) => { const p = gr.pts[gr.pts.length - 1], k = Math.min(p.k, kmax); return { gr, x: x(k), y: y(Math.min(p.v, hi)), text: short(gr.r.name, narrow ? 14 : 22) }; }).sort((a, b) => a.y - b.y);
    labs.forEach((l) => {
      g.append('circle').attr('cx', l.x).attr('cy', l.y).attr('r', l.gr.r.rank === 1 ? 4 : 3).style('fill', ACC());
      const w = measure(svg, l.text, 'sw-lab'), x0 = l.x + 7, yy = nudgeY(l.y, 13, x0 - 1, x0 + w + 1, taken, mt - 6, H - mb);
      taken.push([x0 - 1, yy - 6.5, x0 + w + 1, yy + 6.5]);
      if (Math.abs(yy - l.y) > 4) g.append('path').attr('d', `M${l.x + 3},${l.y}L${x0 - 2},${yy}`).style('stroke', ACC()).style('stroke-opacity', 0.5).style('fill', 'none');
      g.append('text').attr('class', 'sw-lab').attr('x', x0).attr('y', yy).attr('dy', '0.32em').style('fill', ACC()).text(l.text);
    });
    const P = []; groups.forEach((gr) => gr.pts.forEach((p) => { if (p.v <= hi && p.k <= kmax) P.push({ x: x(p.k), y: y(p.v), r: 2, gr, p }); }));
    allAbove.forEach((gr) => { const p = gr.pts[gr.pts.length - 1]; P.push({ x: x(Math.min(p.k, kmax)), y: mt - 2, r: 4, gr, p }); });
    hover(svg, P, (ev, h) => {
      const L = [['Configuration', String(h.p.k) + ' of ' + h.gr.pts[h.gr.pts.length - 1].k], ['Best gap so far (its own agent)', gapf(h.p.v) + ' pts'], ['This configuration', h.p.g === null ? '–' : gapf(h.p.g) + ' pts']];
      if (h.gr.r.remeasured) L.push(['Verifier’s gap', gapf(h.gr.r.gap) + ' pts']);
      showTip(ev, h.gr.r.name, standing(h.gr.r), L);
    }, 18);
    key($('tuning-key'), keyItems);
  }

  /* ---------- claimed vs re-measured ---------- */
  function drawVerifier() {
    const box = $('verifier-chart'), st = stOf('ranking'), R = rowsOf('ranking');
    const base = R.find((r) => r.is_baseline), bv = base ? num(base.gap) : null;
    const rows = R.filter((r) => !r.is_baseline && r.remeasured && num(r.claimed_gap) !== null && num(r.gap) !== null).sort((a, b) => a.gap - b.gap);
    key($('verifier-key'), [['hollowdot', 'claimed by its own agent'], ['filldot', 're-measured'], ['win', 're-measured and beats the baseline']].concat(bv !== null ? [['baseline', '3R baseline']] : []));
    if (!ready(box, st, rows.length ? null : 'Nothing re-measured yet. Each claimed winner shows here once the verifier has measured it again.')) return;
    if (!box.clientWidth) return;
    const narrow = box.clientWidth < 480, rh = 26, H = rows.length * rh + 48, { svg, W } = frame(box, H);
    const nameMax = narrow ? 16 : 26, lw = d3.max(rows, (r) => measure(svg, short(r.name, nameMax))) || 0, sw = measure(svg, 'refuted') + 10;
    const ml = Math.min(W * 0.42, lw + 12), mr = sw + 8, mt = 6, yb = H - 36;
    const [lo, hi] = robust(rows.flatMap((r) => [r.claimed_gap, r.gap]), [0, bv].filter((v) => v !== null), 0);
    const x = d3.scaleLinear([lo, hi], [ml, W - mr]), g = svg.append('g'), cl = (v) => x(Math.max(lo, Math.min(hi, v)));
    x.ticks(narrow ? 4 : 6).forEach((v) => {
      g.append('line').attr('x1', x(v)).attr('x2', x(v)).attr('y1', mt).attr('y2', yb).style('stroke', 'var(--cds-chart-grid)');
      g.append('text').attr('x', x(v)).attr('y', yb + 14).attr('text-anchor', 'middle').text(d3.format('~f')(v));
    });
    g.append('text').attr('x', (ml + W - mr) / 2).attr('y', H - 4).attr('text-anchor', 'middle').text('gap to the bench targets (points) · lower is better');
    if (bv !== null) g.append('line').attr('x1', x(bv)).attr('x2', x(bv)).attr('y1', mt - 2).attr('y2', yb).style('stroke', 'var(--color-fg)').style('stroke-width', 1.5).style('stroke-dasharray', '5 3');
    const P = [];
    rows.forEach((r, i) => {
      const yy = mt + i * rh + rh / 2, a = cl(r.claimed_gap), b = cl(r.gap), c = cls(r), win = c === 'win' || c === 'claim';
      g.append('text').attr('x', ml - 10).attr('y', yy).attr('dy', '0.32em').attr('text-anchor', 'end').style('fill', 'var(--color-fg)').text(short(r.name, nameMax));
      g.append('line').attr('x1', a).attr('x2', b).attr('y1', yy).attr('y2', yy).style('stroke', win ? ACC() : 'var(--color-fg-muted)').style('stroke-width', 2).style('stroke-opacity', 0.6);
      g.append('circle').attr('cx', a).attr('cy', yy).attr('r', 4.5).style('fill', 'var(--color-panel)').style('stroke', 'var(--color-fg-muted)').style('stroke-width', 1.5);
      g.append('circle').attr('cx', b).attr('cy', yy).attr('r', 5).style('fill', win ? ACC() : 'var(--color-fg)');
      const v = r.status === 'refuted' ? ['refuted', 'var(--color-bad)'] : r.verified ? ['verified', 'var(--color-ok)'] : ['pending', 'var(--color-fg-muted)'];
      g.append('text').attr('x', W - mr + 8).attr('y', yy).attr('dy', '0.32em').style('fill', v[1]).style('font-weight', 600).text(v[0]);
      P.push({ x: a, y: yy, r: 4.5, d: r }, { x: b, y: yy, r: 5, d: r });
    });
    hover(svg, P, (ev, p) => morphTip(ev, p.d), 16);
  }

  /* ---------- pipeline ---------- */
  const STAGES = { ideated: ['Ideated', 'written up'], screened: ['Screened', 'measured on the bench'], verified: ['Verified', 're-measured, held up'], gpu: ['GPU search', 'short GPU sweep'], cad: ['Keep-out CAD', 'built as CAD'], judged: ['Judged', 'real requirement judges'] };
  function drawPipeline() {
    const box = $('pipeline-bars'), st = stOf('funnel'), F = rowsOf('funnel');
    box.replaceChildren(); box.classList.toggle('dash-skeleton', st === 'loading');
    if (st !== 'ok') { if (st !== 'loading') box.appendChild(el('div', 'sw-msg sw-failed', 'Failed to load')); return; }
    const max = d3.max(F, (r) => num(r.n)) || 0;
    if (!max) { box.appendChild(el('div', 'sw-msg', 'No morphology ideated yet.')); return; }
    F.forEach((r) => {
      const row = box.appendChild(el('div', 'sw-fun-row')), s = STAGES[r.stage] || [r.stage, ''];
      const lab = row.appendChild(el('div', 'sw-fun-label')); lab.appendChild(el('span', null, s[0])); lab.appendChild(el('small', null, s[1]));
      const tr = row.appendChild(el('div', 'sw-fun-track')), bar = tr.appendChild(el('div', 'sw-fun-bar'));
      bar.style.width = (100 * num(r.n) / max) + '%'; bar.setAttribute('data-zero', num(r.n) ? '0' : '1');
      row.appendChild(mark(el('span', 'sw-fun-n', String(r.n)), 'funnel', 'n', 'stage=' + enc(r.stage)));
    });
  }

  /* ---------- table ---------- */
  const COLS = [
    { f: 'rank', label: '#', num: true }, { f: 'name', label: 'Morphology' }, { f: 'family', label: 'Family', sec: true }, { f: 'status', label: 'Status', wide: true },
    { f: 'gap', label: 'Gap ↓', num: true, bar: 'gap' },
    { f: 'inband14', label: 'In-band 14 mm ↑', num: true, bar: 'share', tgt: 0.9, wide: true }, { f: 'reach', label: 'Reach ↑', num: true, bar: 'share', tgt: 0.9, wide: true },
    { f: 'follow', label: 'Follow ↑', num: true, bar: 'share', tgt: 0.95, wide: true },
    { f: '', label: 'In-band · reach · follow ↑', num: true, narrow: true },
    { f: 'inband10', label: 'In-band 10 mm ↑', num: true, sec: true }, { f: 'contact', label: 'Contact ↓', num: true, sec: true },
    { f: 'n_configs', label: 'Configs', num: true, sec: true }, { f: 'verdict', label: 'Verdict', sec: true }
  ];
  const colCls = (c) => [c.num ? 'sw-num' : '', c.sec ? 'sw-sec' : '', c.wide ? 'sw-wide' : '', c.narrow ? 'sw-narrow' : ''].filter(Boolean).join(' ');
  const TOP = 15;
  let sortF = 'rank', sortDir = 1, query = '', showAll = false;
  (function () {
    const tr = document.createElement('tr');
    COLS.forEach((c) => {
      const th = el('th', colCls(c)); if (c.f) th.setAttribute('data-field', c.f); th.scope = 'col';
      if (c.f) { const b = el('button', null, c.label); b.type = 'button'; b.dataset.f = c.f; th.appendChild(b); }
      else th.appendChild(el('span', 'sw-thlab', c.label));
      tr.appendChild(th);
    });
    $('table').querySelector('thead').appendChild(tr);
    $('table').querySelector('thead').addEventListener('click', (ev) => {
      const b = ev.target.closest('button[data-f]'); if (!b) return;
      if (sortF === b.dataset.f) sortDir = -sortDir; else { sortF = b.dataset.f; sortDir = ['inband14', 'inband10', 'reach', 'follow', 'n_configs'].includes(sortF) ? -1 : 1; }
      drawTable();
    });
    $('table-search').addEventListener('input', (ev) => { query = ev.target.value.trim().toLowerCase(); drawTable(); });
    $('table-more').addEventListener('click', () => { showAll = !showAll; drawTable(); });
    const k = $('table-key');
    [['sw-kbar', 'accent edge and gap: beats the 3R baseline (lighter: claimed, not re-measured)'], ['sw-ktick2', 'target'], ['sw-ktick3', 'its own agent’s claim, where the verifier re-measured it']].forEach(([c, t]) => {
      const sp = k.appendChild(el('span')); sp.appendChild(el('i', c)); sp.append(t);
    });
  })();
  function drawTable() {
    const tb = $('table').querySelector('tbody'), st = stOf('ranking'), R = rowsOf('ranking'), S = rowsOf('summary')[0];
    $('table').querySelectorAll('th[data-field]').forEach((th) => th.setAttribute('aria-sort', th.getAttribute('data-field') === sortF ? (sortDir > 0 ? 'ascending' : 'descending') : 'none'));
    tb.replaceChildren(); $('table-more').hidden = true;
    const box = $('table').parentElement; box.classList.toggle('dash-skeleton', st === 'loading');
    const cnt = $('table-count'); cnt.replaceChildren();
    if (st !== 'ok' || !R.length) {
      const tr = tb.appendChild(el('tr')), td = tr.appendChild(el('td')); td.colSpan = COLS.length;
      if (st !== 'loading') td.appendChild(el('div', st === 'ok' ? 'sw-msg' : 'sw-msg sw-failed', st === 'ok' ? 'No morphology ideated yet.' : 'Failed to load'));
      return;
    }
    const base = R.find((r) => r.is_baseline), bv = base ? num(base.gap) : null;
    const gmax = robust(R.map((r) => num(r.gap)).filter((v) => v !== null), [bv].filter((v) => v !== null), 0)[1] || 1;
    const match = (r) => !query || [r.name, r.family, r.lens, r.status, r.verdict, r.note, r.winner ? 'winner beats baseline' : '', r.is_baseline ? 'baseline' : ''].join(' ').toLowerCase().includes(query);
    const split = (sortF === 'rank' || sortF === 'gap') && base && bv !== null;
    let rows = R.filter((r) => match(r) && !(split && r.is_baseline));
    const val = (r) => { const v = r[sortF]; return v === null || v === undefined || v === '' ? null : v; };
    rows.sort((a, b) => {
      const va = val(a), vb = val(b); if (va === null && vb === null) return 0; if (va === null) return 1; if (vb === null) return -1;
      return sortDir * (typeof va === 'number' && typeof vb === 'number' ? va - vb : String(va).localeCompare(String(vb)));
    });
    const nMorph = rows.filter((r) => !r.is_baseline).length, limited = !showAll && !query && rows.length > TOP;
    const shown = limited ? rows.slice(0, TOP) : rows;
    cnt.append(String(shown.filter((r) => !r.is_baseline).length) + ' of ');
    if (S) cnt.appendChild(mark(el('span', null, String(S.n_total)), 'summary', 'n_total', 0)); else cnt.append(String(nMorph));
    cnt.append(' morphologies shown' + (query ? ' (search: ' + nMorph + ' match)' : ''));
    if (rows.length > TOP && !query) { $('table-more').hidden = false; $('table-more').textContent = showAll ? 'Show the top ' + TOP + ' only' : 'Show all ' + rows.length + ' rows'; }
    // where the baseline sits in this order: everything above it beats it
    let divAt = -1;
    const better = (r) => (sortF === 'rank' ? r.rank !== null && r.winner === true : num(r.gap) !== null && num(r.gap) < bv);
    if (split) {
      divAt = sortDir > 0 ? shown.findIndex((r) => !better(r)) : shown.findIndex((r) => better(r));
      if (divAt < 0) divAt = sortDir > 0 ? (shown.length < rows.length ? -1 : shown.length) : shown.filter((r) => r[sortF] !== null).length;
    }
    const nBetter = rows.filter(better).length;
    const divider = () => {
      const tr = tb.appendChild(el('tr', 'sw-divider')), td = tr.appendChild(el('td')); td.colSpan = COLS.length;
      td.append('— 3R baseline, gap ');
      td.appendChild(mark(el('b', null, gapf(bv)), 'ranking', 'gap', 'id=' + enc(base.id)));
      td.append(!nBetter ? ': nothing beats it yet —' : sortF === 'rank' ? (sortDir > 0 ? ': everything above beats it —' : ': everything below beats it —')
        : (sortDir > 0 ? ': everything above has a smaller gap —' : ': everything below has a smaller gap —'));
    };
    shown.forEach((r, i) => {
      if (i === divAt) divider();
      const tr = tb.appendChild(el('tr')), c = cls(r), W = 'id=' + enc(r.id); tr.setAttribute('data-key', r.id); tr.setAttribute('data-c', c); if (r.is_baseline) tr.className = 'sw-base';
      COLS.forEach((col) => {
        const td = tr.appendChild(el('td', colCls(col))), v = col.f ? r[col.f] : null;
        if (col.f === 'rank') td.textContent = r.rank ? String(r.rank) : '';
        else if (col.f === 'name') { td.className += ' sw-name'; td.textContent = r.name; }
        else if (col.f === 'family') { td.className += ' sw-fam'; td.textContent = r.family || ''; }
        else if (col.f === 'status') { const ch = td.appendChild(el('span', 'sw-chip', r.status)); ch.setAttribute('data-s', r.is_baseline ? 'base' : r.status); ch.title = r.is_baseline ? 'the 3R baseline' : STATUS_WORDS[r.status] || ''; }
        else if (col.bar) {
          const cb = td.appendChild(el('div', 'sw-cb')), nv = num(v);
          cb.appendChild(el('span', col.f === 'gap' ? 'sw-gapv' : null, nv === null ? '–' : col.bar === 'gap' ? gapf(nv) : pct(nv)));
          const t = cb.appendChild(el('div', 'sw-mtrack')), w = (q) => Math.min(100, 100 * (col.bar === 'gap' ? q / gmax : q));
          if (nv !== null) { const f = t.appendChild(el('div', 'sw-mfill')); f.setAttribute('data-c', c); f.style.width = w(nv) + '%'; }
          if (col.tgt) { const k = t.appendChild(el('i', 'sw-mtick')); k.style.left = (col.tgt * 100) + '%'; }
          if (col.f === 'gap' && r.remeasured && r.claimed_gap !== null && r.claimed_gap !== r.gap) { const k = t.appendChild(el('i', 'sw-mclaim')); k.style.left = w(r.claimed_gap) + '%'; td.title = 'its own agent claimed ' + gapf(r.claimed_gap); }
        } else if (col.narrow) {
          const d = td.appendChild(el('div', 'sw-cb3'));
          [['inband14', 'in-band'], ['reach', 'reach'], ['follow', 'follow']].forEach(([f, lab]) => {
            const s = d.appendChild(el('span')); s.appendChild(mark(el('b', null, num(r[f]) === null ? '–' : P0(num(r[f]))), 'ranking', f, W)); s.appendChild(el('small', null, lab));
          });
        } else if (col.f === 'inband10' || col.f === 'contact') td.textContent = num(v) === null ? '' : pct(v);
        else td.textContent = v === null || v === undefined ? '' : String(v);
      });
    });
    if (divAt === shown.length && shown.length) divider();
  }
