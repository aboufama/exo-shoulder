
  /* ---------- built CAD over time ---------- */
  const JM = [
    { k: 'r1_14', req: 'R1', title: 'Skin within 2–14 mm of the metal', dir: 1, goal: 0.9, desc: 'Share of the skin under the metal that stays 2–14 mm from it while the exo follows the motions. Pass: 90% or more.' },
    { k: 'r1_10', req: 'R1-aim', title: 'Skin within 2–10 mm (your 1 cm aim)', dir: 1, goal: 0.9, desc: 'The same share inside 2–10 mm, the 1 cm rule itself. Aim: 90% or more.' },
    { k: 'follow', req: 'R3', title: 'Follows the arm', dir: 1, goal: 0.95, desc: 'Share of motion frames in which the exo moves with the arm instead of stopping it. Pass: 95% or more.' },
    { k: 'overhead_14', req: 'R4', title: 'Overhead', dir: 1, goal: 0.8, desc: 'Score on the raise-overhead motion: follow the arm up and stay within 14 mm of the skin. Pass: 80% or more.' },
    { k: 'range_r16', req: 'R16', title: 'Everyday arm poses reached', dir: 1, goal: 0.9, desc: 'Share of everyday arm poses the built exo reaches with no skin contact and no parts colliding. Pass: 90% or more.' },
    { k: 'parts_mm', req: 'R6', title: 'Parts hitting each other', dir: -1, goal: 0.15, unit: 'mm', desc: 'Deepest overlap between two moving parts over all motions, in millimetres. Pass: 0.15 mm or less.' }
  ];
  let cadMode = 'dof', show4 = false;
  $('cad-mode').addEventListener('click', (ev) => { const b = ev.target.closest('button[data-m]'); if (!b) return; cadMode = b.dataset.m; $('cad-mode').querySelectorAll('button').forEach((x) => x.setAttribute('aria-pressed', String(x === b))); drawCad(); });
  $('cad-show4').addEventListener('click', () => { show4 = !show4; $('cad-show4').setAttribute('aria-pressed', String(show4)); drawCad(); });
  const jfmt = (m, v) => (v === null || v === undefined ? '–' : m.unit ? d3.format(num(v) < 1 ? '.2f' : '.1f')(num(v)) + ' mm' : P1(num(v)));
  const jpass = (m, v) => (v === null || v === undefined ? null : m.dir > 0 ? num(v) >= m.goal : num(v) <= m.goal);
  const LEVEL_COL = () => ({ 'Full CAD': dash.colors[3], 'Keep-out CAD': dash.colors[1] });
  function sstyle(r) {
    // 3 DOF: solid; 4 DOF: dashed with hollow dots, and never joined to 3-DOF designs
    const four = Number(r.dof) !== 3;
    if (cadMode === 'dof') return { g: 'd' + r.dof, col: four ? 'var(--color-fg-muted)' : 'var(--color-fg)', four };
    return { g: (r.level || 'CAD') + '|' + r.dof, col: LEVEL_COL()[r.level] || 'var(--color-fg-muted)', four };
  }
  function cadKey(J, anyRules, anyClip) {
    const items = [];
    if (cadMode === 'dof') {
      if (J.some((r) => Number(r.dof) === 3)) items.push(['series', '3 DOF (your goal)', 'var(--color-fg)']);
      if (J.some((r) => Number(r.dof) !== 3)) items.push(['series4', '4 DOF (dashed, hollow)', 'var(--color-fg-muted)']);
    } else {
      ['Full CAD', 'Keep-out CAD'].forEach((lv) => { if (J.some((r) => r.level === lv)) items.push(['series', lv === 'Full CAD' ? 'Full CAD (real joints)' : 'Keep-out CAD (quick slabs)', LEVEL_COL()[lv]]); });
      if (J.some((r) => Number(r.dof) !== 3)) items.push(['series4', '4 DOF: dashed, hollow', 'var(--color-fg-muted)']);
    }
    items.push(['target', 'pass line']);
    if (anyRules) items.push(['rules', 'judging rules changed'], ['faded', 'judged before it (not comparable)']);
    if (anyClip) items.push(['clip', 'off the scale (value written beside it)']);
    key($('cad-key'), items);
  }
  function drawCad() {
    const st = stOf('judged', 'judged_stats', 'reqs'), J = rowsOf('judged').filter((r) => r.time && (show4 || Number(r.dof) === 3)), S = rowsOf('judged_stats'), scope = show4 ? 'all' : '3';
    const since = (m) => { const q = rowsOf('reqs').find((r) => r.req === m.req); return q && q.rules_since ? q.rules_since : null; };
    const ts = J.map((r) => +date(r.time)), dom = ts.length ? timeDomain(ts) : [new Date(), new Date()];
    let anyRules = false, anyClip = false;
    JM.forEach((m) => {
      const card = $('cad-' + m.k); card.replaceChildren();
      const head = card.appendChild(el('div', 'sw-mini-head')), h = head.appendChild(el('h3', 'sw-mini-title'));
      h.appendChild(el('span', 'sw-req', m.req)); h.append(m.title);
      head.appendChild(el('span', 'sw-dir', m.dir > 0 ? '↑ higher is better' : '↓ lower is better'));
      card.appendChild(el('p', 'sw-mini-desc', m.desc));
      const rs = since(m), stats = card.appendChild(el('div', 'sw-stats')), srow = S.find((r) => r.metric === m.k && r.scope === scope);
      const W = 'metric=' + m.k + '&scope=' + scope;
      [['latest', 'latest', srow ? srow.latest_design : ''], ['best', rs ? 'best, current rules' : 'best so far', srow ? srow.best_design : '']].forEach(([f, label, design]) => {
        const s = stats.appendChild(el('div', 'sw-stat')), v = srow ? srow[f] : null, ok = jpass(m, v);
        if (ok !== null) s.setAttribute('data-ok', ok ? '1' : '0');
        s.appendChild(mark(el('b', st === 'loading' ? 'dash-skeleton' : null, st === 'loading' ? '—' : jfmt(m, v)), 'judged_stats', f, W));
        const sp = s.appendChild(el('span', null, label)); if (design) sp.title = design;
      });
      const gl = stats.appendChild(el('div', 'sw-stat')); gl.appendChild(el('b', null, m.unit ? m.goal + ' mm' : P0(m.goal))); gl.appendChild(el('span', null, 'pass line'));
      const box = card.appendChild(el('div', 'sw-mchart')), pts = J.filter((r) => r[m.k] !== null && r[m.k] !== undefined);
      if (!ready(box, st, pts.length ? null : 'Not judged on any ' + (show4 ? '' : '3-DOF ') + 'design yet.')) return;
      if (!box.clientWidth) return;
      const H = 160, { svg, W: Wd } = frame(box, H), g = svg.append('g'), mt = 10, mb = 22;
      const vals = pts.map((r) => num(r[m.k]));
      let lo, hi;
      if (m.unit) { const v = vals.slice().sort(d3.ascending); lo = 0; hi = Math.max(m.goal * 1.5, Math.min(d3.max(v) * 1.08, Math.max(m.goal * 4, d3.quantile(v, 0.75) * 2.5))); }
      else [lo, hi] = robust(vals, [m.goal], 0, 1);
      const y = d3.scaleLinear([lo, hi], [H - mb, mt]), fmt = m.unit ? d3.format('~r') : P0, ticks = y.ticks(4), cl = (v) => Math.max(lo, Math.min(hi, v));
      const ml = Math.ceil(d3.max(ticks, (v) => measure(svg, fmt(v))) || 0) + 10, mr = 8;
      const x = d3.scaleUtc(dom, [ml, Wd - mr]);
      drawGridY(g, y, ticks, fmt, ml, Wd - mr);
      if (m.goal >= lo && m.goal <= hi) g.append('line').attr('x1', ml).attr('x2', Wd - mr).attr('y1', y(m.goal)).attr('y2', y(m.goal)).style('stroke', 'var(--color-ok)').style('stroke-width', 1.5).style('stroke-dasharray', '5 4');
      drawTimeX(g, x, H - mb, svg);
      const obst = [];
      if (rs && +date(rs) > +dom[0] && +date(rs) < +dom[1]) {
        anyRules = true;
        const xr = x(+date(rs));
        g.append('line').attr('x1', xr).attr('x2', xr).attr('y1', mt - 4).attr('y2', H - mb).style('stroke', 'var(--color-fg-muted)').style('stroke-width', 1.2).style('stroke-dasharray', '2 3');
        const t = 'rules changed', tw = measure(svg, t), left = xr + 4 + tw > Wd - mr;
        g.append('text').attr('class', 'sw-lab-m').attr('x', left ? xr - 4 : xr + 4).attr('y', mt + 4).attr('text-anchor', left ? 'end' : 'start').text(t);
        obst.push(left ? [xr - 6 - tw, mt - 6, xr, mt + 7] : [xr, mt - 6, xr + 6 + tw, mt + 7]);
      }
      const old = (r) => !!rs && r.time < rs, P = [], clips = [];
      d3.groups(pts, (r) => sstyle(r).g).forEach(([, grp]) => {
        grp = grp.slice().sort((a, b) => +date(a.time) - +date(b.time));
        const sty = sstyle(grp[0]), xy = grp.map((r) => [x(+date(r.time)), y(cl(num(r[m.k])))]);
        for (let i = 1; i < xy.length; i++) if (xy[i][0] - xy[i - 1][0] < 6) xy[i][0] = xy[i - 1][0] + 6;   // judged minutes apart: side by side
        [grp.map((r, i) => i).filter((i) => old(grp[i])), grp.map((r, i) => i).filter((i) => !old(grp[i]))].forEach((idx, part) => {
          if (idx.length > 1) g.append('path').attr('d', d3.line()(idx.map((i) => xy[i]))).style('fill', 'none').style('stroke', sty.col).style('stroke-width', 2)
            .style('stroke-opacity', part === 0 ? 0.3 : 0.85).style('stroke-dasharray', sty.four ? '5 4' : null).attr('stroke-linejoin', 'round').attr('stroke-linecap', sty.four ? 'butt' : 'round');
        });
        grp.forEach((r, i) => {
          const v = num(r[m.k]), clip = v > hi ? 1 : v < lo ? -1 : 0, op = old(r) ? 0.3 : 1;
          if (clip) {
            const yy = clip > 0 ? mt - 2 : H - mb + 2;
            tri(g, xy[i][0], yy + (clip > 0 ? 4 : -4), clip > 0 ? 0 : 180, sty.col).style('fill-opacity', op);
            clips.push({ x: xy[i][0], y: yy + (clip > 0 ? 4 : -4), clip, text: jfmt(m, v), op });
            P.push({ x: xy[i][0], y: yy, r: 4, row: r });
          } else {
            g.append('circle').attr('cx', xy[i][0]).attr('cy', xy[i][1]).attr('r', 4).style('fill', sty.four ? 'var(--color-panel)' : sty.col).style('fill-opacity', sty.four ? 1 : op)
              .style('stroke', sty.four ? sty.col : 'var(--color-panel)').style('stroke-width', sty.four ? 1.6 : 1.2).style('stroke-opacity', sty.four ? op : 1);
            P.push({ x: xy[i][0], y: xy[i][1], r: 4, row: r });
          }
          obst.push(dotBox(xy[i][0], clip ? (clip > 0 ? mt + 2 : H - mb - 2) : xy[i][1], 4));
        });
      });
      // values of clipped dots, each beside its own triangle, clear of the other marks
      clips.forEach((c) => {
        anyClip = true;
        const w = measure(svg, c.text) + 4, h = 12;
        const spots = c.clip > 0 ? [[6, 3], [-6 - w, 3], [6, 15], [-6 - w, 15], [6, 27], [-6 - w, 27]] : [[6, -15], [-6 - w, -15], [6, -27], [-6 - w, -27]];
        for (const [dx, dy] of spots) {
          const b = [c.x + dx, c.y + dy - h / 2, c.x + dx + w, c.y + dy + h / 2];
          if (b[0] < ml || b[2] > Wd - mr || obst.some((o) => overlap(o, b))) continue;
          obst.push(b);
          g.append('text').attr('class', 'sw-lab-m').attr('x', b[0] + 2).attr('y', c.y + dy).attr('dy', '0.32em').style('opacity', c.op < 1 ? 0.6 : 1).text(c.text);
          break;
        }
      });
      hover(svg, P, (ev, p) => showTip(ev, p.row.design, tUTC(date(p.row.time)) + ' · ' + p.row.level + ' · ' + p.row.dof + ' DOF' + (old(p.row) ? ' · judged under older rules' : ''),
        [[m.req + ' ' + m.title.toLowerCase(), jfmt(m, p.row[m.k])], ['Judges run', p.row.judges || '–'], ['All judges run', yes(p.row.complete) ? 'yes' : 'no']]), 20);
    });
    cadKey(J, anyRules, anyClip);
    drawStrip();
  }
  function drawStrip() {
    const box = $('cad-moves_freely'), st = stOf('judged');
    const J = rowsOf('judged').filter((r) => r.time && r.moves_freely !== null && r.moves_freely !== undefined && (show4 || Number(r.dof) === 3)).sort((a, b) => (a.time < b.time ? -1 : 1));
    box.replaceChildren(); box.classList.toggle('dash-skeleton', st === 'loading');
    const head = box.appendChild(el('div', 'sw-mini-head')), h = head.appendChild(el('h3', 'sw-mini-title'));
    h.appendChild(el('span', 'sw-req', 'R17')); h.append('Moves freely unpowered');
    head.appendChild(el('span', 'sw-dir', 'yes is the pass'));
    box.appendChild(el('p', 'sw-mini-desc', 'Whether your arm alone drives the unpowered chain through every motion (no stall, no sagging spare joint). One chip per judged design, oldest first' + (show4 ? '; dashed: 4 DOF.' : '.')));
    if (st !== 'ok') { if (st !== 'loading') box.appendChild(el('div', 'sw-msg sw-failed', 'Failed to load')); return; }
    if (!J.length) { box.appendChild(el('div', 'sw-msg', 'Not judged on any ' + (show4 ? '' : '3-DOF ') + 'design yet.')); return; }
    const row = box.appendChild(el('div', 'sw-strip-row')), hm = d3.utcFormat('%H:%M');
    J.forEach((r) => {
      const v = yes(r.moves_freely), c = row.appendChild(el('span', 'sw-yn')); c.setAttribute('data-v', v ? 'yes' : 'no'); c.setAttribute('data-dof', String(r.dof));
      c.appendChild(mark(el('b', null, v ? 'yes' : 'no'), 'judged', 'moves_freely', 'design=' + enc(r.design)));
      c.appendChild(el('small', null, hm(date(r.time)) + ' · ' + r.design));
      c.title = tUTC(date(r.time)) + ' · ' + r.level + ' · ' + r.dof + ' DOF';
    });
  }

  /* ---------- requirement board ---------- */
  const GLYPH = { pass: '✓ ', fail: '✗ ' };
  function drawBoard() {
    const box = $('reqs-board'), st = stOf('reqs'), R = rowsOf('reqs'), S = rowsOf('reqs_summary')[0], sum = $('reqs-sum');
    box.replaceChildren(); sum.replaceChildren(); box.classList.toggle('dash-skeleton', st === 'loading');
    if (st !== 'ok') { if (st !== 'loading') box.appendChild(el('div', 'sw-msg sw-failed', 'Failed to load')); return; }
    if (!R.length) { box.appendChild(el('div', 'sw-msg', 'No requirement judged yet.')); return; }
    if (S) { sum.appendChild(mark(el('b', null, String(S.n_pass)), 'reqs_summary', 'n_pass', 0)); sum.append(' of '); sum.appendChild(mark(el('b', null, String(S.n_total)), 'reqs_summary', 'n_total', 0)); sum.append(' pass'); }
    R.forEach((r) => {
      const W = 'req=' + enc(r.req), settled = r.state === 'pass' || r.state === 'fail', t = box.appendChild(el('div', 'sw-rq')); t.setAttribute('data-s', settled ? r.state : 'open');
      const top = t.appendChild(el('div', 'sw-rq-top'));
      top.appendChild(mark(el('span', 'sw-rq-id', r.req), 'reqs', 'req', W));
      const s = top.appendChild(el('span', 'sw-st')); s.setAttribute('data-s', settled ? r.state : 'open');
      if (GLYPH[r.state]) s.appendChild(el('span', null, GLYPH[r.state])).setAttribute('aria-hidden', 'true');
      s.appendChild(mark(el('span', null, r.state), 'reqs', 'state', W));
      t.appendChild(mark(el('div', 'sw-rq-name', r.name), 'reqs', 'name', W));
      const v = t.appendChild(el('div', 'sw-rq-val'));
      if (settled && r.best) { v.append('best '); v.appendChild(mark(el('b', null, r.best), 'reqs', 'best', W)); v.append(' · '); }
      v.append('target '); v.appendChild(mark(el('span', null, r.target), 'reqs', 'target', W));
      if (settled && r.design) t.appendChild(mark(el('div', 'sw-rq-design', r.design), 'reqs', 'design', W));
      if (r.note) t.appendChild(mark(el('div', 'sw-rq-note', r.note), 'reqs', 'note', W));
      if (r.older_best) { const o = t.appendChild(el('div', 'sw-rq-old')); o.append('older rules: '); o.appendChild(mark(el('span', null, r.older_best), 'reqs', 'older_best', W)); }
    });
  }

  /* ---------- log ---------- */
  let logKind = 'all';
  $('log-kind').addEventListener('click', (ev) => { const b = ev.target.closest('button[data-k]'); if (!b) return; logKind = b.dataset.k; drawLog(); });
  function drawLog() {
    const list = $('log-list'), st = stOf('events'), E = rowsOf('events').slice().sort((a, b) => (a.time < b.time ? 1 : -1));
    const kinds = ['all'].concat(Array.from(new Set(E.map((e) => e.kind))).sort()), seg = $('log-kind');
    if (seg.children.length !== kinds.length || kinds.some((k, i) => seg.children[i].dataset.k !== k)) seg.replaceChildren(...kinds.map((k) => { const b = el('button', null, k === 'all' ? 'everything' : k); b.type = 'button'; b.dataset.k = k; return b; }));
    if (!kinds.includes(logKind)) logKind = 'all';
    seg.querySelectorAll('button').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.k === logKind)));
    list.replaceChildren(); list.classList.toggle('dash-skeleton', st === 'loading');
    if (st !== 'ok') { if (st !== 'loading') list.appendChild(el('li', 'sw-msg sw-failed', 'Failed to load')); return; }
    const rows = E.filter((e) => logKind === 'all' || e.kind === logKind);
    if (!rows.length) { list.appendChild(el('li', 'sw-msg', 'Nothing logged yet.')); return; }
    rows.forEach((e) => {
      const li = list.appendChild(el('li')); li.setAttribute('data-k', e.kind);
      const t = li.appendChild(el('span', 'sw-log-t')); t.appendChild(el('span', null, tUTC(date(e.time)))); t.appendChild(el('small', null, ago(e.time)));
      li.appendChild(el('span')).appendChild(el('span', 'sw-chip', e.kind)).setAttribute('data-k', e.kind);
      li.appendChild(el('span', 'sw-log-e', e.event));
    });
  }

  /* ---------- tabs, links, drawing ---------- */
  const TABS = ['swarm', 'cad', 'log'];
  let tab = 'swarm', pending = null;
  const h0 = location.hash.slice(1), t0el = h0 ? document.getElementById(h0) : null;
  if (t0el && page.contains(t0el)) { const sec = TABS.includes(h0) ? t0el : t0el.closest('.sw-page'); if (sec) tab = sec.id; if (!TABS.includes(h0)) pending = t0el; }
  function show(t, link) {
    tab = t;
    TABS.forEach((k) => { $(k).hidden = k !== t; const b = $('tab-' + k); b.setAttribute('aria-selected', String(k === t)); b.tabIndex = k === t ? 0 : -1; });
    hideTip();
    if (link) dash.setLink(t);
    drawTab();
  }
  document.querySelector('.sw-tabs').addEventListener('click', (ev) => { const b = ev.target.closest('button[data-tab]'); if (b) show(b.dataset.tab, true); });
  document.querySelector('.sw-tabs').addEventListener('keydown', (ev) => {
    const i = TABS.indexOf(tab), d = ev.key === 'ArrowRight' ? 1 : ev.key === 'ArrowLeft' ? -1 : 0; if (!d) return;
    const n = TABS[(i + d + TABS.length) % TABS.length]; show(n, true); $('tab-' + n).focus();
  });
  function drawTab() {
    if (tab === 'swarm') { drawHero(); drawRecord(); drawLands(); drawTuning(); drawVerifier(); drawPipeline(); drawTable(); }
    else if (tab === 'cad') { drawCad(); drawBoard(); if (window.__swDraw3d) window.__swDraw3d(); }
    else drawLog();
  }
  function drawAll() { drawHeader(); drawTab(); if (pending) { const p = pending; pending = null; requestAnimationFrame(() => p.scrollIntoView()); } }
  TABS.forEach((k) => { $(k).hidden = k !== tab; $('tab-' + k).setAttribute('aria-selected', String(k === tab)); });
  window.__swTab = () => tab;
  dash.onData(drawAll);
  setInterval(() => { drawHeader(); if (tab === 'log') drawLog(); }, 60000);
})();
</script>
