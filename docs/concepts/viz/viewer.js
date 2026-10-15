/* viewer.js - the concept gallery page: turns KIN concept descriptors into three.js meshes on a primitive mannequin,
 * plays the motion loop, lists every concept (window.CONCEPT_META, written by build.py), shows the info panel and the
 * per-frame loop-closure indicator, and a Timeline mode that steps through the concepts in the order they were
 * screened. Needs THREE (r128) + THREE.OrbitControls, KIN (kin.js) and the concept files. Browser only. */
(function () {
  'use strict';
  if (typeof document === 'undefined') return;
  const KIN = window.KIN, V = KIN.V, META = window.CONCEPT_META || { concepts: [], built: '' };
  const $ = s => document.querySelector(s);
  const el = (tag, cls, txt) => { const e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; };
  const score = gap => (gap == null ? null : 100 * (1 - gap / 275));
  const fmt = (x, d = 1) => (x == null || !isFinite(x) ? '–' : x.toFixed(d));
  const pctf = x => (x == null ? '–' : `${Math.round(100 * x)} %`);
  const STATUS_ORDER = ['verified', 'screened', 'refuted', 'dead', 'modelling', 'ideated'];
  const STATUS_LABEL = { verified: 'Verified', screened: 'Screened', refuted: 'Refuted', dead: 'Dead', modelling: 'Modelling', ideated: 'Ideated' };
  const reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ------------------------------------------------------------------ theme tokens -> scene colours
  const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim() || '#888';
  const C = {};
  function readTheme() {
    for (const k of ['scene', 'body', 'body-2', 'accent', 'orange', 'metal', 'scap', 'armfix', 'axis', 'ink', 'muted', 'line', 'ok', 'warn', 'bad', 'panel'])
      C[k] = new THREE.Color(css(`--${k}`));
  }

  // ------------------------------------------------------------------ three.js scene
  let renderer, scene, camera, controls, stageEl, partsGroup, axesGroup, man = {};
  const unitCyl = () => new THREE.CylinderGeometry(1, 1, 1, 28, 1);
  const GEO = {};
  function geo(name) {
    if (GEO[name]) return GEO[name];
    const g = { cyl: () => unitCyl(), rod: () => new THREE.CylinderGeometry(1, 1, 1, 10, 1), box: () => new THREE.BoxGeometry(1, 1, 1),
                sph: () => new THREE.SphereGeometry(1, 20, 14) }[name]();
    GEO[name] = g; return g;
  }
  const MAT = {};
  function mats() {
    const std = (c, m, r, extra) => new THREE.MeshStandardMaterial(Object.assign({ color: c, metalness: m, roughness: r }, extra || {}));
    MAT.active = std(C.accent, 0.25, 0.42);
    MAT.passive = std(C.orange, 0.05, 0.62);
    MAT.link = std(C.metal, 0.35, 0.5);
    MAT['fixed-scapula'] = std(C.scap, 0.3, 0.5);
    MAT['fixed-arm'] = std(C.armfix, 0.25, 0.55, { side: THREE.DoubleSide });
    MAT.body = std(C.body, 0.0, 0.95);
    MAT.body2 = std(C['body-2'], 0.0, 0.95);
    MAT.axis = new THREE.LineBasicMaterial({ color: C.axis, transparent: true, opacity: 0.75 });
    MAT.gh = std(C.accent, 0.1, 0.6);
  }
  function retheme() {
    readTheme(); if (!renderer) return;
    scene.background = C.scene;
    const set = (m, c) => m && m.color.copy(c);
    set(MAT.active, C.accent); set(MAT.passive, C.orange); set(MAT.link, C.metal); set(MAT['fixed-scapula'], C.scap);
    set(MAT['fixed-arm'], C.armfix); set(MAT.body, C.body); set(MAT.body2, C['body-2']); set(MAT.axis, C.axis);
    drawTimeline();
  }

  const _m = new THREE.Matrix4(), _y = new THREE.Vector3(0, 1, 0), _v = new THREE.Vector3();
  const vec = a => new THREE.Vector3(a[0], a[1], a[2]);
  function placeBetween(mesh, a, b, r) {                        // unit cylinder along y from a to b, radius r
    const d = V.sub(b, a), L = V.norm(d) || 1e-6;
    mesh.position.set((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2);
    mesh.quaternion.setFromUnitVectors(_y, _v.set(d[0] / L, d[1] / L, d[2] / L));
    mesh.scale.set(r, L, r);
  }
  function placeBasis(mesh, c, ex, ey, ez, sx, sy, sz) {
    _m.makeBasis(vec(ex), vec(ey), vec(ez)); mesh.quaternion.setFromRotationMatrix(_m);
    mesh.position.set(c[0], c[1], c[2]); mesh.scale.set(sx, sy, sz);
  }
  function basisZX(z, x) {                                       // orthonormal (x, y, z) from a normal z and a hint x
    const ez = V.unit(z); let ex = V.reject(x || V.perp(ez), ez); if (V.norm(ex) < 1e-6) ex = V.perp(ez);
    ex = V.unit(ex); return [ex, V.cross(ez, ex), ez];
  }

  // ---- updatable tube (arcs, rails): N segments x M sides, positions rewritten in place
  function makeTube(N, M) {
    const g = new THREE.BufferGeometry(), pos = new Float32Array((N + 1) * M * 3), idx = [];
    for (let i = 0; i < N; i++) for (let j = 0; j < M; j++) {
      const a = i * M + j, b = i * M + (j + 1) % M, c = (i + 1) * M + j, d = (i + 1) * M + (j + 1) % M;
      idx.push(a, c, b, b, c, d);
    }
    g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setIndex(idx); g.userData = { N, M };
    return g;
  }
  function resample(pts, N) {
    const L = [0]; for (let i = 1; i < pts.length; i++) L.push(L[i - 1] + V.norm(V.sub(pts[i], pts[i - 1])));
    const tot = L[L.length - 1] || 1e-9, out = []; let k = 0;
    for (let i = 0; i <= N; i++) {
      const s = tot * i / N; while (k < pts.length - 2 && L[k + 1] < s) k++;
      const seg = (L[k + 1] - L[k]) || 1e-9; out.push(V.lerp(pts[k], pts[Math.min(k + 1, pts.length - 1)], Math.min(1, (s - L[k]) / seg)));
    }
    return out;
  }
  function updateTube(g, pts, r) {
    const { N, M } = g.userData, P = resample(pts, N), pos = g.attributes.position.array;
    let nPrev = null;
    for (let i = 0; i <= N; i++) {
      const t = V.unit(V.sub(P[Math.min(N, i + 1)], P[Math.max(0, i - 1)]));
      let n = nPrev ? V.reject(nPrev, t) : V.perp(t); if (V.norm(n) < 1e-6) n = V.perp(t); n = V.unit(n); nPrev = n;
      const b = V.cross(t, n);
      for (let j = 0; j < M; j++) {
        const a = 2 * Math.PI * j / M, o = (i * M + j) * 3, cs = Math.cos(a) * r, sn = Math.sin(a) * r;
        pos[o] = P[i][0] + n[0] * cs + b[0] * sn; pos[o + 1] = P[i][1] + n[1] * cs + b[1] * sn; pos[o + 2] = P[i][2] + n[2] * cs + b[2] * sn;
      }
    }
    g.attributes.position.needsUpdate = true; g.computeVertexNormals(); g.computeBoundingSphere();
  }
  const arcPoints = d => d.pts || KIN.greatArc(d.u, d.v, d.r0, d.r1, 40).map(p => V.add(p, d.c || [0, 0, 0]));
  function railPoints(d) {
    const k = V.unit(d.axis), e = V.unit(V.reject(d.ref, k)), f = V.cross(k, e), o = [], n = 48;
    for (let i = 0; i <= n; i++) {
      const a = (d.a0 + (d.a1 - d.a0) * i / n) * KIN.D2R;
      o.push(V.add(d.c, V.add(V.scale(e, d.rho * Math.cos(a)), V.scale(f, d.rho * Math.sin(a)))));
    }
    return o;
  }

  // ---- descriptor -> object (built once per concept), update(d) every frame
  function build(d) {
    const mat = MAT[d.role] || MAT.link, grp = new THREE.Group(), add = (g, m) => { const x = new THREE.Mesh(g, m || mat); grp.add(x); return x; };
    let up;
    switch (d.kind) {
      case 'hub': {
        const m = add(geo('cyl')), line = new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(), new THREE.Vector3()]), MAT.axis);
        axesGroup.add(line);
        up = q => {
          const ax = V.unit(q.axis), h = q.h || 12, r = q.r || 10;
          placeBetween(m, q.c, V.madd(q.c, ax, h), r);
          const p0 = q.p0 || [0, 0, 0], end = V.madd(q.c, ax, h + 14), s = V.dot(V.sub(p0, q.c), ax), a = V.madd(q.c, ax, Math.min(s, 0));
          line.geometry.setFromPoints([vec(a), vec(end)]);
        };
        grp.userData.dispose = () => { axesGroup.remove(line); line.geometry.dispose(); };
        break;
      }
      case 'link': { const m = add(geo('rod')); up = q => placeBetween(m, q.a, q.b, q.r || 2.5); break; }
      case 'arc': case 'rail': {
        const g = makeTube(d.kind === 'rail' ? 64 : 40, 10), m = add(g);
        up = q => updateTube(g, q.kind === 'rail' ? railPoints(q) : arcPoints(q), q.r || (q.kind === 'rail' ? 2.6 : 2.5));
        grp.userData.dispose = () => g.dispose();
        break;
      }
      case 'carriage': case 'plate': {
        const m = add(geo('box'));
        up = q => {
          const z = q.z, [ex, ey, ez] = basisZX(z, q.x);
          const s = q.size || [20, 16, 8], sz = q.kind === 'plate' ? (q.t || 3) : (s[2] || 8);
          placeBasis(m, q.c, ex, ey, ez, s[0], s[1], sz);
        };
        break;
      }
      case 'slider': {
        const rod = add(geo('rod')), blk = add(geo('box'));
        up = q => {
          placeBetween(rod, q.a, q.b, q.r || 1.6);
          const x = V.unit(V.sub(q.b, q.a)), [ex, ey, ez] = basisZX(q.z ? V.reject(q.z, x) : V.perp(x), x);
          const s = q.size || [12, 10, 5]; placeBasis(blk, q.at, ex, ey, ez, s[0], s[1], s[2]);
        };
        break;
      }
      case 'telescope': {
        const o = add(geo('cyl')), i = add(geo('cyl'));
        up = q => {
          const dir = V.unit(V.sub(q.b, q.a)), sp = q.split;
          placeBetween(o, q.a, V.madd(q.a, dir, sp), q.r0 || 5);
          placeBetween(i, V.madd(q.a, dir, sp * 0.5), q.b, q.r1 || 3.2);
        };
        break;
      }
      case 'strap': {
        const full = d.a0 == null || d.a1 == null;
        const g = new THREE.CylinderGeometry(1, 1, 1, 48, 1, true, full ? 0 : d.a0 * KIN.D2R, full ? Math.PI * 2 : (d.a1 - d.a0) * KIN.D2R);
        const m = add(g);
        up = q => {
          const ax = V.unit(q.axis), ref = V.unit(V.reject(q.ref || V.perp(ax), ax)), xl = V.cross(ax, ref);
          placeBasis(m, q.c, xl, ax, ref, q.r, q.w || 20, q.r);
        };
        grp.userData.dispose = () => g.dispose();
        break;
      }
      case 'ring': {
        const g = new THREE.TorusGeometry(1, Math.max(0.02, (d.t || 3) / d.r), 10, 56), m = add(g);
        up = q => { const [ex, ey, ez] = basisZX(q.axis, q.ref); placeBasis(m, q.c, ex, ey, ez, q.r, q.r, q.r); };
        grp.userData.dispose = () => g.dispose();
        break;
      }
      case 'point': { const m = add(geo('sph'), d.name === 'GH centre' ? MAT.gh : mat); up = q => { m.position.set(...q.p); m.scale.setScalar(q.r || 4); }; break; }
      default: up = () => {};
    }
    grp.userData.update = up; grp.userData.kind = d.kind; return grp;
  }

  // ---- mannequin (primitives sized from body_mesh.json; matte, low contrast)
  function loft(rows, seg) {                                    // rows: [y, cx, hx, cz, hz] bottom -> top, elliptic rings
    const g = new THREE.BufferGeometry(), pos = [], idx = [], n = seg || 40;
    rows.forEach(([y, cx, hx, cz, hz]) => { for (let j = 0; j < n; j++) { const a = 2 * Math.PI * j / n; pos.push(cx + hx * Math.cos(a), y, cz + hz * Math.sin(a)); } });
    for (let i = 0; i < rows.length - 1; i++) for (let j = 0; j < n; j++) {
      const a = i * n + j, b = i * n + (j + 1) % n, c = a + n, d = b + n; idx.push(a, b, c, b, d, c);
    }
    const nb = rows.length * n; pos.push(rows[0][1], rows[0][0] - 4, rows[0][3]); pos.push(rows[rows.length - 1][1], rows[rows.length - 1][0] + 2, rows[rows.length - 1][3]);
    for (let j = 0; j < n; j++) { idx.push(nb, (j + 1) % n, j); const t = (rows.length - 1) * n; idx.push(nb + 1, t + j, t + (j + 1) % n); }
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals(); return g;
  }
  function buildMannequin() {
    const trunk = new THREE.Group(), mz = KIN.BODY.mid_z;
    const T = [[-760, 20, 70, mz, 110], [-700, 15, 105, mz, 160], [-560, 12, 98, mz, 148], [-420, 22, 112, mz, 160], [-280, 30, 128, mz, 176],
               [-150, 28, 128, mz, 182], [-60, 18, 118, mz, 176], [0, 4, 100, mz, 150], [40, -4, 82, mz, 120], [70, 8, 58, mz, 70]];
    trunk.add(new THREE.Mesh(loft(T), MAT.body));
    trunk.add(new THREE.Mesh(loft([[55, 24, 50, mz, 54], [150, 30, 48, mz, 50]], 28), MAT.body));
    const head = new THREE.Mesh(geo('sph'), MAT.body); head.position.set(36, 228, mz); head.scale.set(98, 118, 78); trunk.add(head);
    // left arm at rest (mirror of the right arm's rest pose about the midline)
    const A = KIN.armFrames(KIN.KEYS[0].pose), mir = p => [p[0], p[1], 2 * mz - p[2]];
    const ghL = mir([0, 0, 0]), eL = mir(A.elbow), wL = mir(A.wrist);
    const lsh = new THREE.Mesh(geo('sph'), MAT.body); lsh.position.set(...ghL); lsh.scale.setScalar(46); trunk.add(lsh);
    const lu = new THREE.Mesh(geo('cyl'), MAT.body); placeBetween(lu, ghL, eL, 40); trunk.add(lu);
    const lf = new THREE.Mesh(geo('cyl'), MAT.body); placeBetween(lf, eL, wL, 31); trunk.add(lf);
    const le = new THREE.Mesh(geo('sph'), MAT.body); le.position.set(...eL); le.scale.setScalar(36); trunk.add(le);
    const lh = new THREE.Mesh(geo('sph'), MAT.body); const hd = V.unit(V.sub(wL, eL)); lh.position.set(...V.madd(wL, hd, 55)); lh.scale.set(30, 30, 30); trunk.add(lh);
    scene.add(trunk); man.trunk = trunk;
    // right arm: deltoid cap, upper arm, elbow, forearm, hand (updated per frame)
    const mk = (g, m) => { const x = new THREE.Mesh(geo(g), m || MAT.body2); scene.add(x); return x; };
    man.delt = mk('sph'); man.delt.scale.setScalar(45);
    man.ua = mk('cyl'); man.el = mk('sph'); man.el.scale.setScalar(35); man.fa = mk('cyl'); man.hand = mk('sph');
  }
  function poseMannequin(ctx) {
    man.trunk.position.set(-ctx.lift[0], -ctx.lift[1], -ctx.lift[2]);
    const E = ctx.elbow, W = ctx.wrist, ax = ctx.armAxis;
    man.delt.position.set(...V.scale(ax, 6));
    placeBetween(man.ua, V.scale(ax, 10), E, 39);
    man.el.position.set(...E);
    placeBetween(man.fa, E, W, 30);
    const fd = V.unit(V.sub(W, E)), hc = V.madd(W, fd, 58);
    const [ex, ey, ez] = basisZX(ctx.elbowAxis, fd);
    placeBasis(man.hand, hc, ex, ey, ez, 62, 34, 16);
  }

  // ------------------------------------------------------------------ state
  const frames = KIN.motion(240), ctxs = frames.map(f => KIN.makeCtx(f.pose, f.t));
  const state = { id: null, sol: null, objs: [], frame: 0, playing: !reduced, fps: 40, mode: 'gallery', tlIndex: 0, tlTimer: 0, axes: true, acc: 0, last: 0 };
  const metaById = {}; META.concepts.forEach(m => { metaById[m.id] = m; });
  const hasPreview = id => !!KIN.concepts[id];

  function clearParts() {
    for (const g of state.objs) { if (g.userData.dispose) g.userData.dispose(); partsGroup.remove(g); }
    state.objs = [];
  }
  function selectConcept(id, opts) {
    opts = opts || {};
    if (!metaById[id] && !KIN.concepts[id]) id = defaultId();
    state.id = id; clearParts(); state.sol = null;
    const c = KIN.concepts[id];
    if (c) {
      try {
        state.sol = KIN.run(c, frames).frames;
        const d0 = c.parts(state.sol[0].q, state.sol[0].ctx);
        state.objs = d0.map(d => { const g = build(d); partsGroup.add(g); return g; });
      } catch (e) { console.error(`concept ${id}:`, e); state.sol = null; clearParts(); state.err = String(e.message || e); }
    }
    if (!opts.keepHash) { try { history.replaceState(null, '', '#' + id); } catch (e) { /* sandboxed */ } }
    renderInfo(); markList(); renderFrame(true);
  }
  function defaultId() {
    const withP = META.concepts.filter(m => hasPreview(m.id) && m.gap != null).sort((a, b) => a.gap - b.gap);
    return (withP[0] || META.concepts[0] || { id: KIN.order[0] }).id;
  }

  // ------------------------------------------------------------------ per-frame rendering
  function renderFrame(force) {
    const i = state.frame, ctx = ctxs[i];
    poseMannequin(ctx);
    const c = KIN.concepts[state.id];
    if (c && state.sol) {
      const s = state.sol[i];
      try {
        const ds = c.parts(s.q, s.ctx);
        ds.forEach((d, k) => { const g = state.objs[k]; if (g) g.userData.update(d); });
      } catch (e) { /* shown by the indicator */ }
      setIndicator(s);
    } else setIndicator(null);
    $('#scrub').value = String(i);
    const f = frames[i], ph = phaseOf(i);
    $('#phase').textContent = ph;
    $('#poseval').textContent = `plane ${fmt(f.pose.plane, 0)}°  elev ${fmt(f.pose.elev, 0)}°  axial ${fmt(f.pose.axial, 0)}°  elbow ${fmt(f.pose.flex, 0)}°`;
    renderer.render(scene, camera);
  }
  const keyFrame = {}; frames.forEach((f, i) => { if (f.key && keyFrame[f.key] == null) keyFrame[f.key] = i; });
  function phaseOf(i) {
    const f = frames[i]; if (f.key) return (KIN.KEYS.find(k => k.key === f.key) || {}).label;
    const a = KIN.KEYS[f.seg], b = KIN.KEYS[f.seg + 1];
    const nm = k => (k.via ? (k.key === 'rest2' ? 'Rest' : 'lowering') : k.label.toLowerCase());
    return `${a.via ? 'Lowering' : a.label} → ${nm(b)}`;
  }
  function setIndicator(s) {
    const box = $('#loop'), t = $('#loop-text'), d = $('#loop-detail');
    box.classList.remove('ok', 'warn', 'bad', 'none');
    if (!s) {
      box.classList.add('none');
      t.textContent = hasPreview(state.id) ? 'Preview failed to load' : 'No 3D preview yet';
      d.textContent = hasPreview(state.id) ? (state.err || '') : 'The mannequin runs the motion loop alone. The idea is described in the panel.';
      return;
    }
    const res = `residual ${fmt(s.resMm, 2)} mm / ${fmt(s.resDeg, 2)}°`;
    if (!s.closes) { box.classList.add('bad'); t.textContent = 'Does not close the loop'; d.textContent = `${res}${s.reason ? ' · ' + s.reason : ''}`; }
    else if (!s.inRange) { box.classList.add('warn'); t.textContent = 'Closes, outside its working range'; d.textContent = `${s.reason} · ${res}`; }
    else { box.classList.add('ok'); t.textContent = 'Closes the loop'; d.textContent = `${res} · ${s.how}`; }
  }

  function tick(now) {
    requestAnimationFrame(tick);
    if (!state.last) state.last = now;
    const dt = Math.min(0.1, (now - state.last) / 1000); state.last = now;
    let changed = false;
    if (state.playing) {
      state.acc += dt * state.fps;
      while (state.acc >= 1) {
        state.acc -= 1; state.frame = (state.frame + 1) % frames.length; changed = true;
        if (state.mode === 'timeline' && state.frame === 0) { stepTimeline(1); return; }
      }
    }
    controls.update();
    if (changed) renderFrame(); else renderer.render(scene, camera);
  }

  // ------------------------------------------------------------------ list, search, info
  function groupList() {
    const q = ($('#search').value || '').trim().toLowerCase(), box = $('#list'); box.textContent = '';
    let shown = 0;
    for (const st of STATUS_ORDER) {
      const rows = META.concepts.filter(m => m.status === st && (!q || `${m.id} ${m.name} ${m.family} ${m.lens}`.toLowerCase().includes(q)));
      if (!rows.length) continue;
      rows.sort((a, b) => (a.gap == null) - (b.gap == null) || (a.gap || 0) - (b.gap || 0) || a.name.localeCompare(b.name));
      const sec = el('section', 'grp'), h = el('h3', 'grp-h');
      h.append(el('span', `pill s-${st}`, STATUS_LABEL[st] || st), el('span', 'grp-n', String(rows.length)));
      sec.append(h);
      const ul = el('ul', 'items');
      for (const m of rows) {
        const li = el('li'), b = el('button', 'item'); b.type = 'button'; b.dataset.id = m.id;
        const top = el('span', 'item-top'), nm = el('span', 'item-name', m.short || m.name);
        top.append(nm);
        const sc = score(m.gap), vs = score(m.v_gap);
        if (sc != null) top.append(el('span', 'item-score', fmt(sc)));
        const sub = el('span', 'item-sub');
        sub.append(el('span', 'item-id', m.id), el('span', 'item-dof', `${m.active_dof ?? '?'}A${m.passive_dof ? '+' + m.passive_dof + 'P' : ''}`));
        if (vs != null) sub.append(el('span', 'item-v', `ver. ${fmt(vs)}`));
        if (hasPreview(m.id)) sub.append(el('span', 'item-3d', '3D'));
        b.append(top, sub); li.append(b); ul.append(li); shown++;
      }
      sec.append(ul); box.append(sec);
    }
    if (!shown) box.append(el('p', 'empty', 'No concept matches that search. Try a family such as "rail", "SPM" or "3R".'));
    markList();
  }
  function markList() {
    document.querySelectorAll('.item').forEach(b => b.setAttribute('aria-current', b.dataset.id === state.id ? 'true' : 'false'));
    $('#list-count').textContent = `${META.concepts.length} concepts · ${META.concepts.filter(m => hasPreview(m.id)).length} with a 3D preview`;
  }
  function renderInfo() {
    const m = metaById[state.id] || { id: state.id, name: (KIN.concepts[state.id] || {}).name || state.id };
    const c = KIN.concepts[state.id];
    $('#i-name').textContent = m.name; $('#i-id').textContent = m.id;
    $('#stage-name').textContent = (c && c.name) || m.short || m.name;
    const st = $('#i-status'); st.className = `pill s-${m.status || 'ideated'}`; st.textContent = STATUS_LABEL[m.status] || m.status || '–';
    const sc = score(m.gap), vs = score(m.v_gap);
    $('#i-score').textContent = sc == null ? '–' : fmt(sc);
    $('#i-score-note').textContent = sc == null ? 'not benchmarked yet' : `gap ${fmt(m.gap, 2)}`;
    $('#i-vscore').textContent = vs == null ? '–' : fmt(vs);
    $('#i-vscore-note').textContent = vs == null ? 'no verifier re-run' : `gap ${fmt(m.v_gap, 2)}`;
    const a = m.active_dof ?? (c && c.dof.active), p = m.passive_dof ?? (c && c.dof.passive);
    $('#i-dof').textContent = `${a ?? '?'} active · ${p ?? '?'} passive`;
    const chips = $('#stage-dof'); chips.textContent = '';
    chips.append(el('span', 'chip chip-a', `${a ?? '?'} active`), el('span', 'chip chip-p', `${p ?? '?'} passive`));
    $('#i-family').textContent = [m.family, m.lens].filter(Boolean).join(' · ') || '–';
    $('#i-idea').textContent = m.description || '–';
    $('#i-limiter-h').textContent = m.verdict ? 'Verdict and limiter' : 'Main risk';
    $('#i-limiter').textContent = m.verdict || m.main_risk || '–';
    $('#i-topology').textContent = m.topology || '–';
    const met = $('#i-metrics'); met.textContent = '';
    if (m.gap != null) for (const [k, v] of [['Reach', m.reach], ['Follow', m.follow], ['In band 2–14', m.inband14], ['In band 2–10', m.inband10], ['Contact', m.contact]]) {
      const d = el('div', 'met'); d.append(el('dt', null, k), el('dd', null, pctf(v))); met.append(d);
    }
    met.hidden = m.gap == null;
    const pv = $('#i-preview');
    if (c && state.sol) {
      const n = state.sol.length, cl = state.sol.filter(s => s.closes).length, ir = state.sol.filter(s => s.closes && s.inRange).length;
      pv.textContent = `Preview: ${c.solve ? 'closed-form' : 'numeric'} solution; closes on ${cl} of ${n} loop frames, ${ir} inside the working range.`;
    } else pv.textContent = c ? 'Preview: failed to run (see console).' : 'No 3D preview for this concept yet.';
    $('#i-doc').textContent = m.doc || '';
    $('#i-times').textContent = [m.t_ideated && `ideated ${m.t_ideated.slice(0, 16).replace('T', ' ')} UTC`, m.t_screened && `screened ${m.t_screened.slice(0, 16).replace('T', ' ')} UTC`].filter(Boolean).join(' · ');
    if (state.mode === 'timeline') drawTimeline();
  }

  // ------------------------------------------------------------------ timeline (evolution) mode
  const TL = META.concepts.filter(m => m.t_screened).sort((a, b) => a.t_screened.localeCompare(b.t_screened));
  function setMode(mode) {
    state.mode = mode; document.body.dataset.mode = mode;
    $('#mode-gallery').setAttribute('aria-pressed', String(mode === 'gallery'));
    $('#mode-timeline').setAttribute('aria-pressed', String(mode === 'timeline'));
    $('#timeline').hidden = mode !== 'timeline';
    if (mode === 'timeline') {
      const k = TL.findIndex(m => m.id === state.id); state.tlIndex = k >= 0 ? k : 0;
      state.frame = 0; selectConcept(TL[state.tlIndex].id); drawTimeline();
    }
  }
  function stepTimeline(dir) {
    if (!TL.length) return;
    state.tlIndex = (state.tlIndex + dir + TL.length) % TL.length; state.frame = 0; state.acc = 0;
    selectConcept(TL[state.tlIndex].id); drawTimeline();
  }
  function drawTimeline() {
    const cv = $('#tl-canvas'); if (!cv || state.mode !== 'timeline') return;
    const w = cv.clientWidth, h = cv.clientHeight, dpr = window.devicePixelRatio || 1;
    cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr);
    const g = cv.getContext('2d'); g.setTransform(dpr, 0, 0, dpr, 0, 0); g.clearRect(0, 0, w, h);
    const pad = { l: 34, r: 12, t: 12, b: 20 }, sc = TL.map(m => score(m.gap));
    const lo = 0, hi = 100, X = i => pad.l + (w - pad.l - pad.r) * (TL.length < 2 ? 0.5 : i / (TL.length - 1)), Y = s => pad.t + (h - pad.t - pad.b) * (1 - (s - lo) / (hi - lo));
    g.font = '11px "IBM Plex Mono", ui-monospace, monospace'; g.textBaseline = 'middle';
    for (const s of [0, 25, 50, 75, 100]) {
      g.strokeStyle = css('--line'); g.lineWidth = 1; g.beginPath(); g.moveTo(pad.l, Y(s)); g.lineTo(w - pad.r, Y(s)); g.stroke();
      g.fillStyle = css('--muted'); g.textAlign = 'right'; g.fillText(String(s), pad.l - 6, Y(s));
    }
    let best = null, prevY = null; g.strokeStyle = css('--accent'); g.lineWidth = 2; g.beginPath();
    sc.forEach((s, i) => {
      if (s == null) return; best = best == null ? s : Math.max(best, s); const x = X(i), y = Y(best);
      if (prevY == null) g.moveTo(x, y); else { g.lineTo(x, prevY); g.lineTo(x, y); } prevY = y;
    });
    g.stroke();
    sc.forEach((s, i) => {
      if (s == null) return; const m = TL[i], cur = i === state.tlIndex;
      g.fillStyle = css(m.status === 'verified' ? '--ok' : m.status === 'dead' || m.status === 'refuted' ? '--muted' : '--accent');
      g.beginPath(); g.arc(X(i), Y(s), cur ? 6 : 3.5, 0, Math.PI * 2); g.fill();
      if (cur) { g.strokeStyle = css('--ink'); g.lineWidth = 1.5; g.stroke(); }
    });
    g.fillStyle = css('--muted'); g.textAlign = 'left'; g.textBaseline = 'alphabetic';
    g.fillText('score in screening order · line = best so far', pad.l, h - 5);
    const m = TL[state.tlIndex];
    $('#tl-label').textContent = m ? `${state.tlIndex + 1} / ${TL.length} · ${m.t_screened.slice(5, 16).replace('T', ' ')} UTC · ${m.short || m.name} · score ${fmt(score(m.gap))}` : '';
  }

  // ------------------------------------------------------------------ boot
  function boot() {
    readTheme(); mats();
    stageEl = $('#stage');
    renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
    renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));
    stageEl.prepend(renderer.domElement); renderer.domElement.id = 'gl';
    scene = new THREE.Scene(); scene.background = C.scene;
    camera = new THREE.PerspectiveCamera(30, 1, 10, 20000);
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.target.set(0, -25, -40); controls.enableDamping = true; controls.dampingFactor = 0.12;
    controls.minDistance = 250; controls.maxDistance = 4000;
    scene.add(new THREE.HemisphereLight(0xffffff, 0x80878d, 0.62));
    const key = new THREE.DirectionalLight(0xffffff, 0.5); key.position.set(900, 1100, 700); scene.add(key);
    const rim = new THREE.DirectionalLight(0xffffff, 0.22); rim.position.set(-900, 400, -600); scene.add(rim);
    partsGroup = new THREE.Group(); axesGroup = new THREE.Group(); scene.add(partsGroup, axesGroup);
    buildMannequin();
    let framed = false;
    const fit = () => {
      const w = stageEl.clientWidth, h = stageEl.clientHeight; if (!w || !h) return;
      renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
      if (!framed) {                                           // shoulder close-up from front-right-above; farther on narrow screens
        framed = true; const d = 960 / Math.min(1, camera.aspect * 1.15), dir = V.unit([0.5, 0.4, 0.77]), t = controls.target;
        camera.position.set(t.x + dir[0] * d, t.y + dir[1] * d, t.z + dir[2] * d); controls.update();
      }
      renderer.render(scene, camera);
    };
    if (window.ResizeObserver) new ResizeObserver(fit).observe(stageEl); else window.addEventListener('resize', fit);
    fit();

    // controls
    $('#scrub').max = String(frames.length - 1);
    $('#scrub').addEventListener('input', e => { state.frame = +e.target.value; setPlaying(false); renderFrame(); });
    $('#play').addEventListener('click', () => setPlaying(!state.playing));
    document.querySelectorAll('[data-pose]').forEach(b => b.addEventListener('click', () => {
      const k = keyFrame[b.dataset.pose]; if (k == null) return; state.frame = k + 3; setPlaying(false); renderFrame();
    }));
    $('#axes').addEventListener('change', e => { axesGroup.visible = e.target.checked; renderFrame(); });
    $('#search').addEventListener('input', groupList);
    $('#list').addEventListener('click', e => {
      const b = e.target.closest('.item'); if (!b) return;
      if (state.mode === 'timeline') setMode('gallery');
      selectConcept(b.dataset.id);
      if (window.matchMedia('(max-width: 760px)').matches) { $('#list-wrap').open = false; stageEl.scrollIntoView({ block: 'start' }); }
    });
    $('#mode-gallery').addEventListener('click', () => setMode('gallery'));
    $('#mode-timeline').addEventListener('click', () => setMode('timeline'));
    $('#tl-prev').addEventListener('click', () => stepTimeline(-1));
    $('#tl-next').addEventListener('click', () => stepTimeline(1));
    window.addEventListener('hashchange', () => { const id = decodeURIComponent(location.hash.slice(1)); if (id && id !== state.id) selectConcept(id, { keepHash: true }); });
    if (window.matchMedia) {
      const mq = window.matchMedia('(prefers-color-scheme: dark)'); if (mq.addEventListener) mq.addEventListener('change', retheme);
      if (window.matchMedia('(max-width: 760px)').matches) $('#list-wrap').open = false;
    }
    new MutationObserver(retheme).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    window.addEventListener('resize', drawTimeline);

    groupList();
    const h = decodeURIComponent((location.hash || '').slice(1));
    selectConcept(h && (metaById[h] || KIN.concepts[h]) ? h : defaultId(), { keepHash: !h });
    setPlaying(state.playing);
    $('#built').textContent = META.built ? `Data as of ${META.built}` : '';
    requestAnimationFrame(tick);
    window.GALLERY = { select: selectConcept, setFrame: i => { state.frame = i; setPlaying(false); renderFrame(); }, keyFrame, state, frames };
  }
  function setPlaying(p) {
    state.playing = p; const b = $('#play');
    b.setAttribute('aria-pressed', String(p)); b.querySelector('.lbl').textContent = p ? 'Pause' : 'Play';
    b.querySelector('.ico').textContent = p ? '❚❚' : '▶';
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
