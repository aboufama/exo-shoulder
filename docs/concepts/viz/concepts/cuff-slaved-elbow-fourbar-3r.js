/* cuff-slaved-elbow-fourbar-3r - a 4R path J1 -(d0)- A0 -(L)- A1 -(d1)- J3 at the cap pole with NO metal on a J2 axis:
 * the elbow (A0 on link 1, A1 on the coupler) is SLAVED by crank B, which runs from a third pin B0 on crank A (an
 * L-plate: A0, A1, B0) to a pin B1 on the arm end, by deg from J3 (the arm-end tab B1 -> J3 is one body with hub 3's
 * lower plate and the K7 neck). In the arm frame the loop crank A - coupler - arm - crank B is a spherical four-bar
 * (ground J3-B1); crank A's third pin A0 must meet link 1 (the 2R J1-A0-A1). Per frame ONE unknown, the coupler spin
 * sigma about J3: A1 = arc d1 from J3 at sigma from the down-arm direction, A0 = the 2R closure (branch s2), B0 on crank
 * A, and the loop equation angle(B0, B1) = rho (root on slope branch sgn nearest `home`, bisected) - exactly the model's
 * solve() (docs/concepts/models/cuff-slaved-elbow-fourbar-3r.py). Working range (check): 2R margin >= 5 deg, loop slope
 * |df/dsigma| >= sin 8 deg, four-bar transmissions at A1 / B0 in [30, 150] deg, pins >= 22 deg apart. 3 ACTIVE (J1, A0,
 * J3) + 3 PASSIVE pins (A1, B0, B1), 0 passive translations, six O20 v5 stacks. Drawn at the screen's best HONEST
 * config (kit 107.61 on Bench(60,160) fast, 117.08 frozen exact Bench(110,360); DEAD at gate 0, plain cap 3R 63.18 through
 * the same kit); hub levels = the kit's fitted K4 levels for that config (J1 54, A0 97, A1 108, B0 137, B1 70, J3 71 mm). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = K.D2R;
  const P = { az: 43.15, el: 59.93, wd: 92.03, wa: -9.03,
              d0: 30.085, L: 29.850, d1: 73.727, sb: 40.525, db: 44.167, rho: 60.674, bx: -166.287, by: 22.0, home: 95.870, s2: -1, sgn: -1,
              MU: 30, MARGIN: 5, PINSEP: 22,
              lv: { J1: 54, A0: 97, A1: 108, B0: 137, B1: 70, J3: 71 }, hub_r: 10, stack: 12.25, neck_deg: 25, cuff_at: 165 };
  const ID = 'cuff-slaved-elbow-fourbar-3r', NAME = 'Cuff-slaved elbow: 4R path at the cap pole, elbow slaved to an arm-cuff pin';
  const ang = (u, v) => V.angle(u, v);
  const gcv = (c, ref, psi, d) => {
    c = V.unit(c); const t0 = V.unit(V.reject(ref, c));
    const t = V.add(V.scale(t0, Math.cos(psi * D2R)), V.scale(V.cross(c, t0), Math.sin(psi * D2R)));
    return V.add(V.scale(c, Math.cos(d * D2R)), V.scale(V.unit(t), Math.sin(d * D2R)));
  };
  const vang = (c, u, v) => ang(V.reject(u, c), V.reject(v, c));
  function geo(sig, ctx) {
    const J1 = V.unit(M.mulv(ctx.S, K.bvec(P.az, P.el))), w = V.unit(M.mulv(ctx.H, K.wdir(P.wd, P.wa))), dn = M.mulv(ctx.H, [0, -1, 0]);
    const A1 = gcv(w, dn, sig, P.d1), cl = K.circInt(J1, P.d0, A1, P.L, P.s2), A0 = cl.p;
    const B0 = gcv(A0, A1, P.sb, P.db), B1 = gcv(w, dn, P.bx, P.by);
    const mg = K.foldMargin(J1, A1, P.d0, P.L);
    return { J1, w, A0, A1, B0, B1, ok: cl.ok && mg >= P.MARGIN, mg, f: ang(B0, B1) - P.rho };
  }
  function solveSig(ctx, prev) {
    const f = s => { const g = geo(s, ctx); return g.ok ? g.f : NaN; };
    let best = null;
    for (let s = -180; s < 180; s += 2) {
      const a = f(s), b = f(s + 2);
      if (!isFinite(a) || !isFinite(b) || Math.sign(a) === Math.sign(b) || Math.sign(b - a) !== P.sgn || Math.abs(b - a) > 90) continue;
      const ref = prev === undefined ? P.home : prev, d = Math.abs(K.wrap180(s + 1 - ref));
      if (!best || d < best.d) best = { d, lo: s, hi: s + 2, flo: a };
    }
    if (!best) return prev === undefined ? P.home : prev;
    let { lo, hi, flo } = best;
    for (let i = 0; i < 30; i++) { const m = 0.5 * (lo + hi), fm = f(m); if (isFinite(fm) && Math.sign(fm) === Math.sign(flo)) { lo = m; flo = fm; } else hi = m; }
    return 0.5 * (lo + hi);
  }
  K.register({
    id: ID, name: NAME,
    dof: { active: 3, passive: 3 },
    params: P,
    q0: ctx => [solveSig(ctx)],
    qNames: ['coupler spin sigma about J3 (sets J1, A0 and the passive pins)'], qUnits: ['deg'], resUnits: ['deg'],
    solve: (ctx, qPrev) => [solveSig(ctx, P.home)],
    residual: (q, ctx) => { const g = geo(q[0], ctx); return [g.ok ? g.f : 90]; },
    check: (q, ctx) => {
      const g = geo(q[0], ctx);
      if (!g.ok) return `elbow 2R J1-A0-A1 outside its window (margin ${g.mg.toFixed(1)} deg < 5)`;
      const dfd = Math.abs(geo(q[0] + 0.5, ctx).f - geo(q[0] - 0.5, ctx).f);
      if (dfd < Math.sin(8 * D2R)) return 'slave loop near its singularity (|df/dsigma| < sin 8 deg)';
      let tr = Math.min(vang(g.A1, g.w, g.B0), vang(g.B0, g.A1, g.B1)); tr = Math.min(tr, 180 - tr);
      if (tr < P.MU) return `four-bar transmission ${tr.toFixed(0)} deg (toggle)`;
      const sep = Math.min(ang(g.J1, g.A0), ang(g.A0, g.B0), ang(g.A1, g.B0), ang(g.B0, g.B1));
      if (sep < P.PINSEP - 1e-6) return `pins ${sep.toFixed(0)} deg apart (< 22)`;
      return null;
    },
    parts: (q, ctx) => partsOf(geo(q[0], ctx), ctx)
  });
  function partsOf(G, ctx) {
    const L = P.lv, h = P.stack, top = n => L[n] + 3.15, harm = ctx.armAxis, ng = P.neck_deg * D2R;
    const ax = { J1: G.J1, A0: G.A0, A1: G.A1, B0: G.B0, B1: G.B1, J3: G.w };
    const nk = V.unit(V.add(V.scale(G.w, Math.cos(ng)), V.scale(V.unit(V.reject(harm, G.w)), Math.sin(ng))));
    const neckEnd = V.scale(nk, L.J3 + 1), cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47);
    const hub = (n, role, label) => ({ kind: 'hub', role, name: label, c: V.scale(ax[n], L[n]), axis: ax[n], r: P.hub_r, h });
    const arc = (role, name, a, b, r0, r1) => ({ kind: 'arc', role, name, u: ax[a], v: ax[b], r0, r1, r: 2.5 });
    return [
      { kind: 'plate', role: 'fixed-scapula', name: 'base (scapula handler)', c: V.scale(G.J1, L.J1 - 3), z: G.J1, x: ctx.attach.scapDir([1, 0, 0]), size: [46, 32], t: 3 },
      hub('J1', 'active', 'J1 (O20 hub)'),
      arc('link', 'link 1', 'J1', 'A0', top('J1'), L.A0),
      hub('A0', 'active', 'A0 (elbow, active)'),
      arc('link', 'crank A (A0 to A1)', 'A0', 'A1', top('A0'), L.A1),
      arc('link', 'crank A (A0 to B0)', 'A0', 'B0', top('A0'), top('B0')),
      hub('A1', 'passive', 'A1 (coupler pin)'), hub('B0', 'passive', 'B0 (slave pin on crank A)'),
      arc('link', 'crank B (slave crank)', 'B0', 'B1', L.B0, L.B1),
      hub('B1', 'passive', 'B1 (arm-cuff pin)'),
      arc('fixed-arm', 'arm-end tab B1 to J3', 'B1', 'J3', top('B1'), L.J3),
      arc('link', 'coupler (A1 to J3)', 'A1', 'J3', top('A1'), top('J3')),
      hub('J3', 'active', 'J3 (O20 hub)'),
      { kind: 'arc', role: 'fixed-arm', name: 'neck', u: G.w, v: nk, r0: L.J3 + 1, r1: L.J3 + 1, r: 3 },
      { kind: 'link', role: 'fixed-arm', name: 'neck to cuff', a: neckEnd, b: cuffTop, r: 3 },
      { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
      { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
    ];
  }
})();
