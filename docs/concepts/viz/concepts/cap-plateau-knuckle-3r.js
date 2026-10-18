/* cap-plateau-knuckle-3r (round 14, pick 2: the cap-seat lens gate 0) at its measured cell C (the best cap proxy): the lead's
 * slaved-knuckle chain moved to the posterolateral CAP POLE. J1 (O20, scapula-fixed) on top of the shoulder over the lateral
 * scapular spine / posterior acromion, link 1a -> K (O20, PASSIVE, slaved to th = angle(J1, J3) by the two-sided dwell law
 * a1e = clip(max(lo, th - off, lo + (f - th)), lo, cap)) -> link 1b -> J2 -> link 2 -> J3 (humerus-fixed) -> neck -> cuff.
 * Every axis passes through GH (the paired-kit instrument: no cuff knee, no drift). 3 active (J1, J2, J3), K passive and
 * determined by the law (GHOST: cell C's two-lobe K drive does not exist), 0 passive translations.
 * Best searched cell-C config (271 tries on the 1 mm near-touch objective, Bench(60,160) fast): plain 27.13 fast, frozen exact
 * Bench(110,360) 32.08 vs the equal-effort control (lead seats / law, same instrument) 30.59 - DEAD (247 taken < 279; ghost
 * drive). Kinematic 275/360 ws, 110/110 clips at m 5 + 0.23 K play; hub levels 51 / 59 / 60 / 65 mm from the fit. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const P = { az1: 60.358, el1: 66.589, d3: 99.680, a3: -6.539, lo: 26.378, off: 38.635, cap: 54.564, f: 31.393, a2: 46.009, bk1: 25.835, bk2: 34.179,
              sK: -1, sigma: -1, margin: 5.23,
              lev: { hub1: 51, hubK: 59, hub2: 60, hub3: 65 }, hub_r: 10, stack: 12.25, neck_deg: 25, cuff_at: 165 };
  const u1 = V.unit(K.bvec(P.az1, P.el1)), u3 = V.unit(K.wdir(P.d3, P.a3));
  const ref1 = V.unit(V.reject([0, 0, 1], u1)), v0 = V.unit(V.reject([1, 0, 0], u3));
  const law = th => Math.min(P.cap, Math.max(P.lo, th - P.off, P.lo + (P.f - th)));
  const Qof = ctx => M.mul(M.T(ctx.S), ctx.H);
  function geo(ctx) {
    const Q = Qof(ctx), w = M.mulv(Q, u3), th = V.angle(u1, w), a1e = law(th);
    const c2 = K.circInt(u1, a1e, w, P.a2, P.sigma), cK = K.circInt(u1, P.bk1, c2.p, P.bk2, P.sK);
    return { Q, w, th, a1e, p2: c2.p, pK: cK.p, ok: c2.ok && cK.ok };
  }
  function solve(ctx) {
    const g = geo(ctx);
    return [K.axisAngle(u1, ref1, g.pK), K.axisAngle(g.pK, u1, g.p2), K.axisAngle(g.p2, g.pK, g.w), K.axisAngle(g.w, g.p2, M.mulv(g.Q, v0))];
  }
  function fk(q) {
    const pK = K.onCone(u1, ref1, P.bk1, q[0]), p2 = K.onCone(pK, u1, P.bk2, q[1]), p3 = K.onCone(p2, pK, P.a2, q[2]);
    const v = K.onCone(p3, p2, 90, q[3]);
    return { pK, p2, p3, v };
  }
  const C = {
    id: 'cap-plateau-knuckle-3r',
    name: 'Cap-pole slaved knuckle 3R, cell C (two-sided dwell K law; ghost drive; 3 active, K slaved)',
    dof: { active: 3, passive: 1 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'K (passive, slaved to th by the two-sided law)', 'J2', 'J3'], qUnits: ['deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'deg', 'deg'],
    solve: ctx => solve(ctx),
    residual: (q, ctx) => {
      const g = geo(ctx), F = fk(q), x = V.cross(F.p3, g.w);
      return [x[0] * K.R2D, x[1] * K.R2D, x[2] * K.R2D, K.wrap180(K.axisAngle(g.w, F.v, M.mulv(g.Q, v0))), V.angle(u1, F.p2) - law(g.th)];
    },
    check: (q, ctx) => {
      const g = geo(ctx), lo = Math.abs(g.a1e - P.a2) + P.margin, hi = Math.min(g.a1e + P.a2, 360 - g.a1e - P.a2) - P.margin;
      if (!g.ok) return 'chain cannot close';
      if (g.th < lo) return `folded side: th ${g.th.toFixed(1)} < ${lo.toFixed(1)} (5 deg + K play from the J2 fold)`;
      if (g.th > hi) return `stretched side: th ${g.th.toFixed(1)} > ${hi.toFixed(1)} (K on stop B, J2 at its 5 deg margin)`;
      return null;
    },
    parts: (q, ctx) => {
      const S = ctx.S, Wd = v => M.mulv(S, v), F = fk(q), L = P.lev, h = P.stack;
      const p1 = Wd(u1), pK = Wd(F.pK), p2 = Wd(F.p2), p3 = Wd(F.p3), harm = ctx.armAxis, ng = P.neck_deg * K.D2R;
      const nk = V.unit(V.add(V.scale(p3, Math.cos(ng)), V.scale(V.unit(V.reject(harm, p3)), Math.sin(ng))));
      const neckEnd = V.scale(nk, L.hub3 + 1), cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base on the scapula handler (at the J1 hub ring)', c: V.scale(p1, L.hub1 - 3), z: p1, x: ctx.attach.scapDir([1, 0, 0]), size: [40, 30], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1 (O20, cap pole: posterolateral acromion / lateral spine)', c: V.scale(p1, L.hub1), axis: p1, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 1a (12 x 3 strap, J1 -> K)', u: p1, v: pK, r0: L.hub1 + 7, r1: L.hubK + 1, r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'K (O20, passive, slaved: dwell on stop A for th 29.6-66.2, opens on both sides; GHOST drive)', c: V.scale(pK, L.hubK), axis: pK, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 1b (12 x 3 strap, K -> J2)', u: pK, v: p2, r0: L.hubK + 7, r1: L.hub2 + 1, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2 (O20, plateau level)', c: V.scale(p2, L.hub2), axis: p2, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 2 (12 x 3 strap, over link 1a and the neck)', u: p2, v: p3, r0: L.hub2 + 7, r1: L.hub3 + 7, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3 (O20, humerus-fixed axis on a GH ray)', c: V.scale(p3, L.hub3), axis: p3, r: P.hub_r, h },
        { kind: 'arc', role: 'fixed-arm', name: 'neck (14 x 6)', u: p3, v: nk, r0: L.hub3 + 1, r1: L.hub3 + 1, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'neck to cuff / BOTTOM', a: neckEnd, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  };
  K.register(C);
})();
