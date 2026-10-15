/* fraction-pauldron - graded telescoping lames on a gimbal (catalogue fraction-pauldron, models/fraction-pauldron.py;
 * dead at gap 92.32: sweeps/fraction-pauldron.json k140, rev 2). A lobster-tail pauldron: the scapula plate and N - 1
 * = 4 lames telescope about ONE scapula-fixed axis x (ddir(lat 25, lon 15), through GH); lame k turns the fraction
 * g_k = (k / 5)^1.25 of the outer angle alpha, held there by a rolling cage between lames k - 1 and k + 1 (bearing-cage
 * principle: exact, holonomic, PASSIVE); the tip lame (g = 1) carries J2, an O20 hub about z (perpendicular to x,
 * angle beta); arm strap A runs from J2 to a carriage on a humerus-fixed arc rail around the arm (cone 60 deg about
 * the humerus axis, twist psi = J3). 3 ACTIVE (alpha, beta, psi = Fick / Cardan angles of the arm about x, then its
 * twist), 4 PASSIVE (the inner lames). Closed form = the model's cardan(): beta from the arm's polar angle about x,
 * alpha its azimuth, psi the remaining roll about the rest arm axis a0. Lame layout = the model's layout() (cage races,
 * overlap 12 deg, hub 10 deg past the tip's last race, plate anchor 20 deg); stroke [amin, amax] = the 0.08 / 0.92
 * quantiles of alpha and the rail = the 0.03 / 0.97 quantiles of psi, over the loop (the model takes them over the
 * bench poses). Not taken: gimbal lock (arm within 12 deg of +-x), alpha off the stroke, psi off the rail. Lames
 * stacked 2.6 mm apart from a 58 mm plate (schematic; the model fits one radius per lame). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D = K.D2R;
  const P = { x_lat: 25, x_lon: 15, n: 5, expo: 1.25, side: 1, ov: 12, pitch: 0, ls: 20, hub_gap: 10, hub_ext: 10, w: 8,
              gamma: 60, lock: 12, cov: 0.92, rcov: 0.97, R0: 58, step: 2.6, railR: 72, cuff_at: 165 };
  const ddir = (lat, lon) => [Math.cos(lat * D) * Math.cos(lon * D), Math.sin(lat * D), Math.cos(lat * D) * Math.sin(lon * D)];
  const x = ddir(P.x_lat, P.x_lon), DOWN = [0, -1, 0];
  const ctx0 = K.makeCtx(K.KEYS[0].pose), Q0 = M.mul(M.T(ctx0.S), ctx0.Hb), a0 = M.mulv(Q0, DOWN);  // rest arm (body_pose axis)
  const z0 = V.unit(V.cross(x, a0)), zs = z0[2] >= 0 ? 1 : -1, zz = V.scale(z0, zs), th0 = V.angle(a0, x);
  const cdir = V.add(V.scale(a0, Math.cos(P.gamma * D)), V.scale(zz, Math.sin(P.gamma * D)));       // carriage on A
  const g = [0]; for (let k = 1; k < P.n; k++) g.push(Math.pow(k / P.n, P.expo)); g.push(1);
  const Rc = (al, be) => M.mul(M.rot(x, al), M.rot(z0, -be));
  function cardan(ctx, qp) {                               // alpha, beta, psi (deg) of the arm in the scapula frame
    const Q = M.mul(M.T(ctx.S), ctx.Hb), a = M.mulv(Q, DOWN), be = th0 - V.angle(a, x);
    let al = K.axisAngle(x, M.mulv(M.rot(z0, -be), a0), a);
    const R = M.mul(M.mul(M.T(Rc(al, be)), Q), M.T(Q0)), v = V.perp(a0);
    let ps = K.axisAngle(a0, v, M.mulv(R, v));
    if (qp) { al = qp[0] + K.wrap180(al - qp[0]); ps = qp[2] + K.wrap180(ps - qp[2]); }
    return [al, be, ps];
  }
  // stroke and rail span from the loop (the model's design(): quantiles over the poses away from gimbal lock)
  const q = (arr, p) => { const s = [...arr].sort((u, w) => u - w); return s[Math.round(p * (s.length - 1))]; };
  const AL = [], PS = []; let prev = null;
  for (const f of K.motion(120)) { const c = cardan(K.makeCtx(f.pose), prev); prev = c; const th = th0 - c[1]; if (th >= P.lock && th <= 180 - P.lock) { AL.push(c[0]); PS.push(c[2]); } }
  const amin = q(AL, 1 - P.cov), amax = q(AL, P.cov), plo = q(PS, 1 - P.rcov), phi = q(PS, P.rcov);
  // the model's layout(): cage races and each stage's own azimuth interval on the circle about x
  const own = (() => {
    const n = g.length - 1, sd = P.side, Dk = [null], ext = [], race = [];
    for (let k = 1; k <= n; k++) Dk.push((g[k] - g[k - 1]) * (amax - amin));
    for (let k = 0; k <= n; k++) { ext.push([]); race.push([]); }
    const ref = sd > 0 ? amin : amax;
    for (let k = 1; k < n; k++) {
      const c = (k - 1) * P.pitch; ext[k].push([c - P.ov / 2, c + P.ov / 2]);
      const rlo = [c - P.ov / 2, c + P.ov / 2 + Dk[k]]; race[k - 1].push(rlo); ext[k - 1].push(rlo);
      const rhi = [c - P.ov / 2 - Dk[k + 1], c + P.ov / 2]; race[k + 1].push(rhi); ext[k + 1].push(rhi);
    }
    const top = Math.max(...ext[n].map(e => e[1])), hub = top + P.hub_gap; ext[n].push([top, hub + P.hub_ext]);
    const lo0 = Math.min(...ext[0].map(e => e[0])); ext[0].push([lo0 - P.ls, lo0]);
    const shift = sd * ref - hub;
    return ext.map((E, k) => {
      const lo = Math.min(...E.map(e => e[0])) + shift, hi = Math.max(...E.map(e => e[1])) + shift;
      return [sd * lo - g[k] * ref, sd * hi - g[k] * ref].sort((u, w) => u - w);
    });
  })();
  const nm = g.map((_, k) => k === 0 ? 'scapula plate' : k === g.length - 1 ? 'tip lame (alpha)' : `lame ${k} (cage-set)`);

  K.register({
    id: 'fraction-pauldron',
    name: 'Fraction pauldron: graded lames',
    dof: { active: 3, passive: g.length - 2 },
    params: Object.assign({ amin, amax, plo, phi, fractions: g }, P),
    q0: ctx => { const c = cardan(ctx); return c.concat(g.slice(1, -1).map(f => f * c[0])); },
    qNames: ['alpha (telescope)', 'beta (J2)', 'psi (cuff rail)'].concat(g.slice(1, -1).map((f, k) => `lame ${k + 1} (${f.toFixed(2)} alpha)`)),
    qUnits: new Array(g.length + 1).fill('deg'), resUnits: new Array(g.length + 1).fill('deg'),
    solve: (ctx, qp) => { const c = cardan(ctx, qp); return c.concat(g.slice(1, -1).map(f => f * c[0])); },
    residual: (qv, ctx) => {
      const R = M.mul(M.mul(M.mul(ctx.S, Rc(qv[0], qv[1])), M.rot(a0, qv[2])), Q0);
      return M.rotErrDeg(R, ctx.Hb).concat(g.slice(1, -1).map((f, k) => qv[3 + k] - f * qv[0]));
    },
    check: (qv) => {
      const th = th0 - qv[1];
      if (th < P.lock || th > 180 - P.lock) return 'gimbal lock: the arm is near the telescope axis';
      if (qv[0] < amin || qv[0] > amax) return 'telescope at its stroke end';
      if (qv[2] < plo || qv[2] > phi) return 'carriage past the end of the cuff rail';
      return null;
    },
    parts: (qv, ctx) => {
      const S = ctx.S, X = M.mulv(S, x), out = [], al = qv[0], fr = [0].concat(qv.slice(3), [al]);
      g.forEach((f, k) => out.push({ kind: 'strap', role: k === 0 ? 'fixed-scapula' : k === g.length - 1 ? 'active' : 'passive', name: nm[k],
        c: [0, 0, 0], axis: X, ref: M.mulv(S, M.mulv(M.rot(x, fr[k]), zz)), r: P.R0 + k * P.step, w: P.w, a0: own[k][0], a1: own[k][1] }));
      const Rt = M.mul(S, Rc(qv[0], qv[1])), zT = M.mulv(S, M.mulv(M.rot(x, al), zz)), rT = P.R0 + (g.length - 1) * P.step;
      const cA = M.mulv(Rt, cdir), Hb = ctx.Hb;
      const railPt = p => V.scale(M.mulv(Hb, M.mulv(M.T(Q0), M.mulv(M.rot(a0, -p), cdir))), P.railR);
      const rail = []; for (let i = 0; i <= 30; i++) rail.push(railPt(plo - 8 + (phi - plo + 16) * i / 30));
      const tan = V.unit(V.sub(railPt(qv[2] + 1), railPt(qv[2] - 1))), armB = M.mulv(Hb, DOWN), mid = railPt((plo + phi) / 2);
      const cuffC = V.scale(armB, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(mid, armB)), 47);
      out.push({ kind: 'hub', role: 'active', name: 'J2 (beta) on the tip lame', c: V.scale(zT, rT + 1), axis: zT, r: 10, h: 12.25 },
        { kind: 'arc', role: 'link', name: 'arm strap A', u: zT, v: cA, r0: rT + 4.2, r1: P.railR + 4, r: 2.5 },
        { kind: 'carriage', role: 'active', name: 'J3 carriage (psi)', c: V.scale(cA, P.railR + 3), x: tan, z: cA, size: [16, 10, 6] },
        { kind: 'arc', role: 'fixed-arm', name: 'cuff arc rail', pts: rail, r: 2.6 },
        { kind: 'link', role: 'fixed-arm', name: 'neck to BOTTOM', a: mid, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: armB, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 });
      return out;
    }
  });
})();
