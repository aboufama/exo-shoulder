/* 3-D 'where your arm can go' view (ported from the round-1 redesign): one dot per R16 workspace pose of a built design. */
dash.calc('cov3d_share', {
  inputs: ['cov3d'], title: 'Everyday poses reached, per built design',
  description: 'Per design: the share of its judged everyday arm poses that pass R16, and the share blocked by each reason (a pose can be blocked by two).',
  fn: (cov3d) => {
    const by = new Map();
    cov3d.filter((r) => r.empty !== true).forEach((r) => { if (!by.has(r.design)) by.set(r.design, []); by.get(r.design).push(r); });
    return Array.from(by, ([design, rs]) => ({
      design, poses: rs.length,
      share: rs.filter((r) => r.pass === true || r.pass === 'true').length / rs.length,
      parts: rs.filter((r) => String(r.reason).includes('part interference')).length / rs.length,
      body: rs.filter((r) => String(r.reason).includes('body contact')).length / rs.length,
      chain: rs.filter((r) => String(r.reason).includes('chain does not close')).length / rs.length
    }));
  }
});
(function () {
  const card = document.getElementById('reach3d-card'), view = document.getElementById('reach3d-view'), sel = document.getElementById('reach3d-design');
  const pct = d3.format('.1%'), mm = (v) => d3.format(v < 1 ? '.2f' : '.1f')(v) + ' mm';
  const truthy = (v) => v === true || v === 'true' || v === 1 || v === '1';
  const num = (v) => (v === null || v === undefined || v === '' ? null : Number(v));
  // The schematic body, a drawing (not data): millimetres in the rig's thorax frame (x forward, y up, z right; origin = right
  // shoulder centre). Capsules [a, b, radius]; a === b is a ball.
  const ARM = 325, FORE = 250, FIT = 405, C0 = [0, -40, -60];
  const BODY = [
    [[16, 232, -174], [16, 232, -174], 84], [[98, 220, -174], [98, 220, -174], 14], [[0, 50, -174], [10, 140, -174], 48],
    [[-4, -14, -30], [-4, -14, -318], 58], [[8, -70, -116], [8, -220, -120], 102], [[8, -70, -232], [8, -220, -228], 102],
    [[4, -220, -128], [0, -300, -136], 94], [[4, -220, -220], [0, -300, -212], 94], [[-4, -6, -348], [-10, -150, -356], 42]
  ];
  const REST = { x: 0, y: -0.985, z: 0.174, fx: 1, fy: 0, fz: 0 };
  const VIEWS = { q: [35, 20], front: [0, 0], side: [90, 0], back: [180, 0], top: [0, 90] };
  const LABELS = [[[0, 1, 0], 'overhead'], [[1, 0, 0], 'forward'], [[0, 0, 1], 'to the side'], [[-1, 0, 0], 'behind'], [[0.5, 0, -0.866], 'across'], [[0, -1, 0], 'down']];
  const RINGS = [(a) => [Math.sin(a), 0, Math.cos(a)], (a) => [0, Math.cos(a), Math.sin(a)], (a) => [Math.cos(a), Math.sin(a), 0]];
  const D2R = Math.PI / 180;
  let yaw = VIEWS.q[0], pitch = VIEWS.q[1], design = null, hover = null, only = null, picks = [], P = null, anim = null;
  const tip = document.createElement('div'); tip.className = 'c3-tip'; tip.hidden = true; card.appendChild(tip);
  const svg = d3.create('svg').attr('width', '100%').attr('tabindex', 0).attr('role', 'img').attr('aria-label', 'Your body from outside, with one dot per everyday arm pose around the right shoulder');
  const gBack = svg.append('g'), gBody = svg.append('g'), gFront = svg.append('g'), gLab = svg.append('g');
  const dot3 = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  const norm = (a) => { const l = Math.hypot(a[0], a[1], a[2]) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
  function camera(W, H) {
    const t = yaw * D2R, p = pitch * D2R, ct = Math.cos(t), st = Math.sin(t), cp = Math.cos(p), sp = Math.sin(p);
    const u = [st, 0, -ct], v = [-sp * ct, cp, -sp * st], w = [cp * ct, sp, cp * st], s = Math.min(W, H) / (2 * FIT);
    const pr = (q) => { const d = [q[0] - C0[0], q[1] - C0[1], q[2] - C0[2]]; return [W / 2 + s * dot3(d, u), H / 2 - s * dot3(d, v), dot3(d, w)]; };
    return { s, w, pr, gh: pr([0, 0, 0]) };
  }
  function planeWords(pl, el) {
    if (el < 10) return 'arm down by your side'; if (el >= 150) return 'overhead';
    if (pl <= -60) return 'behind you'; if (pl < -20) return 'back and out'; if (pl < 20) return 'out to the side';
    if (pl < 70) return 'forward and out'; if (pl <= 110) return 'forward'; return 'across your body';
  }
  const shade = (k) => `color-mix(in srgb, var(--color-fg) ${Math.round(k)}%, var(--color-panel))`;
  const keyBox = document.getElementById('reach3d-key');
  [['var(--color-ok)', 1, 'reached'], ['var(--color-bad)', 1, 'blocked'], ['var(--color-fg-muted)', 0.35, 'faded: far side of the shoulder']].forEach(([c, o, t]) => {
    const s = document.createElement('span'), i = document.createElement('i'); i.className = 'c3-dot'; i.style.background = c; i.style.opacity = o; s.append(i, document.createTextNode(t)); keyBox.appendChild(s);
  });
  card.querySelectorAll('.c3-reason .c3-dot').forEach((d) => { d.style.background = 'var(--color-bad)'; });

  function draw() {
    const D = dash.data('cov3d'), C = dash.data('cov3d_share');
    const rowsAll = D.status === 'ok' && Array.isArray(D.data) ? D.data.filter((r) => r.empty !== true) : [];
    const designs = Array.from(new Set(rowsAll.map((r) => r.design)));
    if (!designs.includes(design)) { design = designs.length ? designs[designs.length - 1] : null; hover = null; }
    const opts = designs.slice().reverse();
    if (sel.options.length !== opts.length || opts.some((d, i) => sel.options[i].value !== d)) sel.replaceChildren(...opts.map((d) => { const r = rowsAll.find((x) => x.design === d); return new Option(r.label || d, d); }));
    sel.value = design || ''; sel.disabled = designs.length < 2;
    const cs = C.status === 'ok' ? C.data.find((r) => r.design === design) : null;
    const fill = (id, f, fmt) => {
      const e = document.getElementById(id); e.setAttribute('data-where', 'design=' + encodeURIComponent(design || ''));
      if (cs) { e.classList.remove('dash-skeleton'); e.textContent = fmt(num(cs[f])); } else { e.classList.toggle('dash-skeleton', C.status === 'loading'); e.textContent = '—'; }
    };
    fill('reach3d-share', 'share', pct); fill('reach3d-n', 'poses', d3.format(','));
    ['parts', 'body', 'chain'].forEach((k) => fill('reach3d-' + k, k, pct));
    const share = document.getElementById('reach3d-share'); share.style.color = cs && num(cs.share) >= 0.9 ? 'var(--color-ok)' : 'var(--color-fg)';
    const rd = rowsAll.find((r) => r.design === design);
    ['level', 'id'].forEach((f) => { const e = document.getElementById('reach3d-' + f); e.setAttribute('data-where', 'design=' + encodeURIComponent(design || '')); e.textContent = rd ? (f === 'id' ? rd.design : rd.level) : ''; });
    card.querySelectorAll('.c3-reason').forEach((b) => b.setAttribute('aria-pressed', String(only === b.dataset.r)));
    view.querySelectorAll('.sw-msg').forEach((e) => e.remove());
    if (D.status !== 'ok' || !rowsAll.length) {
      svg.remove(); view.classList.toggle('dash-skeleton', D.status === 'loading');
      if (D.status !== 'loading') { const f = document.createElement('div'); f.className = D.status === 'ok' ? 'sw-msg' : 'sw-msg sw-failed'; f.style.minHeight = '20rem'; f.textContent = D.status === 'ok' ? 'No built design has been judged over the everyday poses yet.' : 'Failed to load'; view.appendChild(f); }
      return;
    }
    view.classList.remove('dash-skeleton');
    if (!view.clientWidth) return;
    if (!svg.node().isConnected) view.appendChild(svg.node());
    const W = Math.max(260, view.clientWidth), H = Math.round(Math.min(W, 560, Math.max(340, W * 0.92)));
    svg.attr('viewBox', `0 0 ${W} ${H}`).attr('height', H);
    const cam = camera(W, H), s = cam.s, pr = cam.pr, R = ARM, rows = rowsAll.filter((r) => r.design === design);
    const groups = d3.group(rows, (r) => [num(r.x), num(r.y), num(r.z)].join(','));
    const dots = rows.map((r) => {
      const d = [num(r.x), num(r.y), num(r.z)], f = [num(r.fx), num(r.fy), num(r.fz)], n = groups.get(d.join(',')).length;
      let q = d;
      if (n > 1) { const fd = dot3(f, d), fp = norm([f[0] - fd * d[0], f[1] - fd * d[1], f[2] - fd * d[2]]), k = Math.tan((n > 2 ? 8 : 5) * D2R); q = norm([d[0] + k * fp[0], d[1] + k * fp[1], d[2] + k * fp[2]]); }
      const p = pr([R * q[0], R * q[1], R * q[2]]);
      return { r, d, f, p, back: p[2] < cam.gh[2], ok: truthy(r.pass), why: String(r.reason || '') };
    });
    const arm = hover ? hover.r : REST, ad = norm([num(arm.x), num(arm.y), num(arm.z)]), af = norm([num(arm.fx), num(arm.fy), num(arm.fz)]);
    const E = [ARM * ad[0], ARM * ad[1], ARM * ad[2]], Wr = [E[0] + FORE * af[0], E[1] + FORE * af[1], E[2] + FORE * af[2]];
    const hand = [Wr[0] + 30 * af[0], Wr[1] + 30 * af[1], Wr[2] + 30 * af[2]];
    const caps = BODY.map(([a, b, r]) => ({ a: pr(a), b: pr(b), r, arm: false }))
      .concat([[[0, 0, 0], E, 44], [E, Wr, 36], [hand, hand, 38]].map(([a, b, r]) => ({ a: pr(a), b: pr(b), r, arm: true })));
    const hit = (c, x, y) => {
      const ax = c.b[0] - c.a[0], ay = c.b[1] - c.a[1], l2 = ax * ax + ay * ay;
      const t = l2 > 1e-9 ? Math.max(0, Math.min(1, ((x - c.a[0]) * ax + (y - c.a[1]) * ay) / l2)) : 0;
      const dx = (x - c.a[0] - t * ax) / s, dy = (y - c.a[1] - t * ay) / s, e2 = c.r * c.r - dx * dx - dy * dy;
      return e2 > 0 ? c.a[2] + t * (c.b[2] - c.a[2]) + Math.sqrt(e2) : null;
    };
    const segd = (c, x, y) => { const ax = c.b[0] - c.a[0], ay = c.b[1] - c.a[1], l2 = ax * ax + ay * ay, t = l2 > 1e-9 ? Math.max(0, Math.min(1, ((x - c.a[0]) * ax + (y - c.a[1]) * ay) / l2)) : 0; return [c.a[0] + t * ax, c.a[1] + t * ay]; };
    const n = caps.length, after = caps.map(() => []), deg = caps.map(() => 0);
    for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) {
      const A = caps[i], B = caps[j];
      let pa = [(A.a[0] + A.b[0]) / 2, (A.a[1] + A.b[1]) / 2], pb;
      for (let it = 0; it < 4; it++) { pb = segd(B, pa[0], pa[1]); pa = segd(A, pb[0], pb[1]); }
      if (Math.hypot(pa[0] - pb[0], pa[1] - pb[1]) / s >= A.r + B.r) continue;
      const k = A.r / (A.r + B.r), x = pa[0] + k * (pb[0] - pa[0]), y = pa[1] + k * (pb[1] - pa[1]), ha = hit(A, x, y), hb = hit(B, x, y);
      if (ha === null || hb === null) continue;
      if (ha < hb) { after[i].push(j); deg[j]++; } else { after[j].push(i); deg[i]++; }
    }
    const mid = (c) => (c.a[2] + c.b[2]) / 2, order = [], done = caps.map(() => false);
    while (order.length < n) {
      let pick = -1;
      for (let i = 0; i < n; i++) if (!done[i] && deg[i] === 0 && (pick < 0 || mid(caps[i]) < mid(caps[pick]))) pick = i;
      if (pick < 0) for (let i = 0; i < n; i++) if (!done[i] && (pick < 0 || mid(caps[i]) < mid(caps[pick]))) pick = i;
      done[pick] = true; order.push(caps[pick]); after[pick].forEach((j) => deg[j]--);
    }
    const dz = d3.extent(caps, (c) => mid(c)), lum = d3.scaleLinear(dz[0] === dz[1] ? [dz[0] - 1, dz[1]] : dz, [25, 14]);
    const capPath = (c) => `M${c.a[0]},${c.a[1]}L${c.b[0] + (Math.hypot(c.b[0] - c.a[0], c.b[1] - c.a[1]) < 0.01 ? 0.01 : 0)},${c.b[1]}`;
    const layers = caps.filter((c) => !c.arm).map((c) => ({ c, edge: true })).concat(order.flatMap((c) => (c.arm ? [{ c, edge: true }, { c }] : [{ c }])));
    gBody.selectAll('path').data(layers).join('path').attr('d', (l) => capPath(l.c)).attr('fill', 'none').attr('stroke-linecap', 'round')
      .style('stroke', (l) => (l.edge ? shade(l.c.arm ? 55 : 42) : shade(l.c.arm ? lum(mid(l.c)) + 11 : lum(mid(l.c)))))
      .attr('stroke-width', (l) => 2 * l.c.r * s + (l.edge ? 2 : 0));
    const ring = (fn) => { const pts = d3.range(0, 97).map((i) => { const a = (i / 96) * 2 * Math.PI, q = fn(a); return pr([R * q[0], R * q[1], R * q[2]]); }); const fr = [], bk = [];
      for (let i = 0; i < 96; i++) (pts[i][2] + pts[i + 1][2] >= 2 * cam.gh[2] ? fr : bk).push(`M${pts[i][0]},${pts[i][1]}L${pts[i + 1][0]},${pts[i + 1][1]}`); return [fr.join(''), bk.join('')]; };
    const rs = RINGS.map(ring), rDot = Math.max(3.4, Math.min(6.5, s * 13));
    gBack.selectAll('circle.c3-globe').data([0]).join('circle').attr('class', 'c3-globe').attr('cx', cam.gh[0]).attr('cy', cam.gh[1]).attr('r', R * s)
      .style('fill', 'color-mix(in srgb, var(--color-fg) 3%, transparent)').style('stroke', 'var(--cds-chart-grid)').attr('stroke-width', 1);
    gBack.selectAll('path.c3-ring').data(rs).join('path').attr('class', 'c3-ring').attr('d', (d) => d[1]).attr('fill', 'none').style('stroke', 'var(--cds-chart-grid)').attr('stroke-width', 1).attr('stroke-dasharray', '2 3');
    gFront.selectAll('path.c3-ring').data(rs).join('path').attr('class', 'c3-ring').attr('d', (d) => d[0]).attr('fill', 'none').style('stroke', 'var(--cds-chart-axis)').attr('stroke-opacity', 0.45).attr('stroke-width', 1);
    const isOn = (o) => (only === null ? true : !o.ok && o.why.includes(only === 'parts' ? 'part interference' : only === 'body' ? 'body contact' : 'chain does not close'));
    dots.forEach((o) => { o.hid = !o.back && caps.some((c) => { const h = hit(c, o.p[0], o.p[1]); return h !== null && h > o.p[2] + 2; }); });
    const sorted = dots.slice().sort((a, b) => a.p[2] - b.p[2]);
    const dotAttrs = (selc) => selc.attr('cx', (o) => o.p[0]).attr('cy', (o) => o.p[1])
      .attr('r', (o) => (hover && o.r === hover.r ? rDot * 1.55 : o.back ? rDot * 0.8 : rDot))
      .style('fill', (o) => (o.ok ? 'var(--color-ok)' : 'var(--color-bad)'))
      .attr('fill-opacity', (o) => (!isOn(o) ? 0.1 : o.back ? 0.32 : o.hid ? 0.4 : 0.95))
      .style('stroke', (o) => (hover && o.r === hover.r ? 'var(--color-fg)' : 'var(--color-panel)'))
      .attr('stroke-width', (o) => (hover && o.r === hover.r ? 2 : o.back ? 0.5 : 1)).attr('stroke-opacity', (o) => (isOn(o) || (hover && o.r === hover.r) ? 1 : 0.2));
    gBack.selectAll('circle.c3-d').data(sorted.filter((o) => o.back), (o) => o.r.k).join('circle').attr('class', 'c3-d').call(dotAttrs);
    gFront.selectAll('circle.c3-d').data(sorted.filter((o) => !o.back), (o) => o.r.k).join('circle').attr('class', 'c3-d').call(dotAttrs);
    if (hover) gFront.selectAll('circle.c3-d').filter((o) => o.r === hover.r).raise();
    gLab.selectAll('text').data(LABELS).join('text').each(function ([q, t]) {
      const p = pr([R * 1.2 * q[0], R * 1.2 * q[1], R * 1.2 * q[2]]);
      const e = d3.select(this).attr('y', Math.max(10, Math.min(H - 10, p[1]))).attr('dy', '0.35em').attr('text-anchor', 'middle').attr('opacity', p[2] >= cam.gh[2] ? 0.95 : 0.4).text(t);
      const hw = this.getComputedTextLength() / 2 + 8; e.attr('x', Math.max(hw, Math.min(W - hw, p[0])));
    });
    picks = dots; P = { W, H, gh: cam.gh, elbow: pr(E), hand: pr(Wr) };
  }
  function pickAt(x, y) {
    let best = null, bd = 18;
    picks.forEach((o) => { if (!isFinite(o.p[0])) return; const d = Math.hypot(o.p[0] - x, o.p[1] - y) + (o.back ? 7 : 0) + (o.hid ? 3 : 0); if (d < bd) { bd = d; best = o; } });
    return best;
  }
  const read = document.getElementById('reach3d-read');
  function idle() { read.textContent = ''; const d = document.createElement('div'); d.className = 'c3-read-idle'; d.textContent = 'Tap a dot: your arm moves there, and a red one says why it is blocked.'; read.appendChild(d); }
  function showTip(o) {
    const narrow = getComputedStyle(read).display !== 'none', box = narrow ? read : tip;
    tip.hidden = true;
    if (!o) { if (narrow) idle(); return; }
    const r = o.r, pl = num(r.plane_deg), el = num(r.elev_deg), ax = num(r.axial_deg);
    box.textContent = '';
    const add = (t, c) => { const d = document.createElement('div'); if (c) d.className = c; d.textContent = t; box.appendChild(d); };
    add(`Raised ${el}°, ${planeWords(pl, el)}`, 'c3-tip-h');
    add(`Plane ${pl}° · upper arm turned ${Math.abs(ax)}° ${ax > 0 ? 'in' : ax < 0 ? 'out' : ''}`.trim() + ` · elbow ${num(r.flex_deg)}°`);
    if (o.ok) add('Reached', 'c3-tip-ok');
    else {
      add('Blocked', 'c3-tip-bad');
      if (o.why.includes('chain does not close')) add('The joints cannot get the cuff to this pose.');
      if (o.why.includes('body contact')) { const bp = String(r.body_part || 'a part'); add(`${bp.charAt(0).toUpperCase() + bp.slice(1)} would press ${mm(num(r.body_mm))} into your body.`); }
      if (o.why.includes('part interference')) add(`Two parts collide: ${r.parts_pair || 'moving parts'}, ${mm(num(r.parts_mm))} overlap.`);
    }
    if (narrow) return;
    tip.hidden = false;
    const cr = card.getBoundingClientRect(), vr = svg.node().getBoundingClientRect(), k = vr.width / P.W, tw = tip.offsetWidth, th = tip.offsetHeight;
    const keep = [o.p, P.gh, P.elbow, P.hand].map((q) => [vr.left + q[0] * k, vr.top + q[1] * k]);
    let best = null, bd = -1;
    [[vr.left + 6, vr.top + 6], [vr.right - 6 - tw, vr.top + 6], [vr.left + 6, vr.bottom - 6 - th], [vr.right - 6 - tw, vr.bottom - 6 - th]].forEach(([x, y]) => {
      const d = Math.min(...keep.map(([qx, qy]) => Math.hypot(Math.max(x - qx, 0, qx - x - tw), Math.max(y - qy, 0, qy - y - th))));
      if (d > bd) { bd = d; best = [x, y]; }
    });
    tip.style.left = Math.max(4, best[0] - cr.left) + 'px'; tip.style.top = Math.max(4, best[1] - cr.top) + 'px';
  }
  const local = (ev) => { const b = svg.node().getBoundingClientRect(), k = P ? P.W / b.width : 1; return [(ev.clientX - b.left) * k, (ev.clientY - b.top) * k]; };
  const setView = (name) => card.querySelectorAll('#reach3d-views button').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.v === name)));
  let drag = null;
  svg.on('pointerdown', (ev) => { if (anim) { anim.stop(); anim = null; } drag = { x: ev.clientX, y: ev.clientY, yaw, pitch, moved: false, id: ev.pointerId }; });
  svg.on('pointermove', (ev) => {
    if (drag && drag.id === ev.pointerId && (ev.buttons || ev.pointerType !== 'mouse')) {
      const dx = ev.clientX - drag.x, dy = ev.clientY - drag.y;
      if (!drag.moved && Math.hypot(dx, dy) > 4) { drag.moved = true; svg.node().setPointerCapture(ev.pointerId); svg.classed('c3-drag', true); hover = null; showTip(null); setView(null); }
      if (drag.moved) { yaw = drag.yaw + dx * 0.5; pitch = Math.max(-90, Math.min(90, drag.pitch + dy * 0.5)); draw(); }
      return;
    }
    const o = pickAt(...local(ev)); if (o !== hover) { hover = o; draw(); } showTip(o);
  });
  const end = (ev) => {
    if (drag && !drag.moved && ev.type === 'pointerup') { const o = pickAt(...local(ev)); hover = o; draw(); showTip(o); }
    if (drag && drag.moved && svg.node().releasePointerCapture) svg.node().releasePointerCapture(drag.id);
    drag = null; svg.classed('c3-drag', false);
  };
  svg.on('pointerup', end).on('pointercancel', end);
  svg.on('pointerleave', (ev) => { if (drag && drag.moved) return; if (ev.pointerType === 'mouse') { hover = null; showTip(null); draw(); } });
  svg.on('keydown', (ev) => {
    const k = { ArrowLeft: [-15, 0], ArrowRight: [15, 0], ArrowUp: [0, 15], ArrowDown: [0, -15] }[ev.key]; if (!k) return;
    ev.preventDefault(); yaw += k[0]; pitch = Math.max(-90, Math.min(90, pitch + k[1])); setView(null); draw();
  });
  card.querySelectorAll('#reach3d-views button').forEach((b) => b.addEventListener('click', () => {
    const [ty, tp] = VIEWS[b.dataset.v]; setView(b.dataset.v); if (anim) anim.stop();
    const y0 = yaw, p0 = pitch, dyaw = ((((ty - y0) % 360) + 540) % 360) - 180;
    if (!window.matchMedia('(prefers-reduced-motion: no-preference)').matches) { yaw = y0 + dyaw; pitch = tp; draw(); return; }
    anim = d3.timer((t) => { const e = d3.easeCubicOut(Math.min(1, t / 450)); yaw = y0 + dyaw * e; pitch = p0 + (tp - p0) * e; draw(); if (e >= 1) { anim.stop(); anim = null; } });
  }));
  card.querySelectorAll('.c3-reason').forEach((b) => b.addEventListener('click', () => { only = only === b.dataset.r ? null : b.dataset.r; draw(); }));
  sel.addEventListener('change', () => { design = sel.value; hover = null; only = null; showTip(null); draw(); });
  window.__swDraw3d = () => { hover = null; draw(); showTip(null); };
  dash.onData(() => { if (window.__swTab && window.__swTab() !== 'cad') return; window.__swDraw3d(); });
})();
