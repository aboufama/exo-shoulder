/* slotted-eccentric-pin-knee-3r - the verified pin knee (skin-normal-3r-pin-knee, k4598) + the ECCENTRIC of
 * slotted-eccentric-j2-3r beside hub 2 (catalogue slotted-eccentric-pin-knee-3r, round 4, ideated; gated on the slot
 * gate of slotted-eccentric-j2-3r, never run). Chain: scapula handler -> J1 (ACTIVE, O20, GH ray) -> link 1 (carries the
 * roller stud F1, MR52ZZ) -> J2 (ACTIVE, O20, GH ray) -> crank 2a (arc 25) -> K (PASSIVE, O11 MR63ZZ pair, SLAVED to q2:
 * the slotted lever on link 2b rides F1) -> link 2b (arc 75) -> J3 (ACTIVE, O20, axis tilted b3 toward the skin normal,
 * line misses GH) -> E strap -> cuff knee pin a (PASSIVE) -> knee link -> pin b (PASSIVE) -> arm pad on BOTTOM / cuff.
 * 3 active, 3 passive rotations (K slaved, pins a / b set by the planar closure), 0 passive translations. The slot makes
 * the J2-J3 arc a2e a function of th = angle(J1, J3): here a2e = soft clip of [a2 + (th - th_home)] into [58, 85] deg
 * (w 4), so the home pose is exactly k4598's geometry (exported in skin-normal-3r-pin-knee.js) and the arc follows th
 * away from the fold; a loop screen over Amin 52-66, Amax 85-102, slope 0.5-1 and the K branch took 120 of 141 frames
 * at these values. Not modelled: the slot's lock-angle gate and part clearances (the spec's model / verifier). Red =
 * within 5 deg of the eccentric's J2 fold, K at its own fold, or the cuff knee outside [30, 150] deg / its span. Hub K
 * and the stud F1 levels are schematic (hub 2 face + 4 / + 3 mm). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 105.7561, "el1": 65.5039, "az2": 17.6992, "el2": 56.2778, "wd": 76.4693, "wa": -13.3241, "b3": 0.3251, "lE": 42.1129, "lc": 24.9243, "phiE": 1.5471, "phib": -55.8565, "stk": 5.0, "ang_min": 30.0, "Amin": 58, "Amax": 85, "w": 4, "sl": 1, "bK": 25, "cK": 75, "sK": 1, "margin": 5, "dF": 22, "gF": 70};
  const G = {"u":[[0.11259,0.90999,0.39905],[-0.55153,0.78573,0.28009],[-0.18127,-0.0897,0.97933]],"c":[[0.0,0.0,0.0],[0.0,0.0,-0.0],[-2.054,-10.279,-1.322]],"sa":[0.01633,-0.99597,-0.0882],"st":[0.9833,0.0,0.182],"sn":[-0.18127,-0.0897,0.97933],"A":[40.122,72.314],"branch":-1.0,"m":[-8.635,2.252,0.0],"f":[49.94,60.85,72.02],"tr":78.51,"tp":2.25,"RUN":0.5,"SING":10.0,"hr":[10.0,10.0,10.0],"A0":[-0.249,-52.206,-4.828],"A0m":[1.825,-43.607,-3.656],"Bm":[-18.231,-57.539,-8.644],"eE":[0.04287,-0.99561,-0.08325],"eK":[-0.80465,-0.55901,-0.20013],"L1":[[-4.67,48.27,20.11],[-6.34,46.38,19.14],[-8.34,47.13,19.26],[-10.35,47.56,19.24],[-12.52,48.36,19.37],[-14.66,48.75,19.32],[-17.21,50.16,19.67],[-20.37,52.71,20.44],[-23.75,55.12,21.13]],"L2":[[-37.22,47.08,28.45],[-33.87,40.9,29.01],[-33.63,38.68,31.94],[-33.71,36.79,35.18],[-33.69,34.76,38.4],[-33.45,32.45,41.43],[-33.11,30.01,44.42],[-32.72,27.47,47.4],[-32.18,24.74,50.26],[-31.51,21.87,53.03],[-30.96,18.99,56.13],[-29.5,15.51,57.64],[-28.64,12.29,60.39],[-26.79,8.62,61.11],[-25.24,5.07,62.5],[-23.31,1.45,62.92],[-22.47,-2.24,66.5],[-22.45,-6.58,73.41]]};
  const u = G.u, c = G.c, sn = G.sn, sa = G.sa, st = G.st, a1 = G.A[0], hub = 12.25, rad = 10;
  const wrapR = a => { a = (a + Math.PI) % (2 * Math.PI); return (a < 0 ? a + 2 * Math.PI : a) - Math.PI; };
  const pe = P.phiE * D2R, pb = P.phib * D2R, lE = P.lE, lc = P.lc;
  const A02 = [G.m[0] + lE * Math.cos(pe), G.m[1] + lE * Math.sin(pe)], B2 = [A02[0] + lc * Math.cos(pb), A02[1] + lc * Math.sin(pb)];
  const kbr = Math.sign(wrapR(pe - Math.atan2(B2[1] - G.m[1], B2[0] - G.m[0]))) || 1;
  const vref = V.unit(V.cross(u[2], [0.3, 0.5, 0.8]));
  // the eccentric: the J2-J3 arc follows the slot law a2e(th), th = angle(J1, J3); at the pin knee's home th0 it is the
  // pin knee's a2 (so the home geometry is k4598's), soft-clipped into [Amin, Amax] (the slot's ends)
  const sp = x => Math.log1p(Math.exp(-Math.abs(x))) + Math.max(x, 0), th0 = V.angle(u[0], u[2]);
  function a2e(th) { const lo = P.Amin, hi = P.Amax, w = P.w, x = G.A[1] + P.sl * (th - th0); return lo + w * sp((x - lo) / w) - w * sp((x - hi) / w); }
  const uK = K.circInt(u[1], P.bK, u[2], P.cK, P.sK).p;                 // knee K home axis (crank 2a arc bK, link 2b arc cK)
  const uF = K.onCone(u[1], u[0], P.dF, P.gF);                          // roller stud F1 on link 1, beside hub 2 (home)
  /** eccentric IK: Q -> J1, J2 (crank), K (slaved) from the closures; fold / knee-K gates */
  function ik(Q) {
    const w = M.mulv(Q, u[2]), th = V.angle(w, u[0]), ae = a2e(th);
    const c2 = K.circInt(u[0], a1, w, ae, G.branch), p2 = c2.p, cK = K.circInt(p2, P.bK, w, P.cK, P.sK), pK = cK.p;
    const q1 = K.axisAngle(u[0], u[1], p2), R1 = M.rot(u[0], q1);
    const q2 = K.axisAngle(u[1], uK, M.mulv(M.T(R1), pK)), R2a = M.mul(R1, M.rot(u[1], q2));
    const qK = K.axisAngle(uK, u[2], M.mulv(M.T(R2a), w));
    const margin = Math.min(th - Math.abs(a1 - ae), a1 + ae - th), mK = Math.min(ae - Math.abs(P.bK - P.cK), P.bK + P.cK - ae);
    return { q1, q2, qK, th, ae, ok: c2.ok && cK.ok && margin >= P.margin && mK >= 3, margin, mK, c2ok: c2.ok };
  }
  /** member transforms: J1, J2, K lines pass GH (rotations); J3's line through c3 (offset) */
  function chain(q1, q2, qK, q3) {
    const R1 = M.rot(u[0], q1), R2a = M.mul(R1, M.rot(u[1], q2)), R12 = M.mul(R2a, M.rot(uK, qK)), R3 = M.rot(u[2], q3), R123 = M.mul(R12, R3);
    const t3 = M.mulv(R12, V.sub(c[2], M.mulv(R3, c[2])));
    return { R1, R2a, R12, R123, t1: [0, 0, 0], t2: [0, 0, 0], t3 };
  }
  function knee(s) {
    const vx = B2[0] - s[0], vy = B2[1] - s[1], d = Math.hypot(vx, vy), gam = Math.atan2(vy, vx);
    const ca = (lE * lE + d * d - lc * lc) / (2 * lE * Math.max(d, 1e-9)), al = Math.acos(Math.max(-1, Math.min(1, ca)));
    const th = gam + kbr * al, pa = [s[0] + lE * Math.cos(th), s[1] + lE * Math.sin(th)];
    const wx = B2[0] - pa[0], wy = B2[1] - pa[1], psi = Math.atan2(wy, wx);
    const cosk = ((s[0] - pa[0]) * wx + (s[1] - pa[1]) * wy) / (lE * lc), ang = Math.acos(Math.max(-1, Math.min(1, cosk))) / D2R;
    return { th, pa, psi, ang, d, phi: wrapR(th - pe), span: d >= Math.abs(lE - lc) + 1 && d <= lE + lc - 1 };
  }
  const Qof = ctx => M.mul(M.T(ctx.S), ctx.H);
  function solve(ctx) {
    const Q = Qof(ctx), k = ik(Q), X0 = chain(k.q1, k.q2, k.qK, 0);
    const q3 = K.axisAngle(u[2], vref, M.mulv(M.T(X0.R12), M.mulv(Q, vref))), X = chain(k.q1, k.q2, k.qK, q3);
    const sv = M.mulv(M.T(Q), X.t3), s = [V.dot(sv, sa), V.dot(sv, st), V.dot(sv, sn)], kn = knee(s);
    const R = x => K.wrap180(x / D2R);
    return [k.q1, k.q2, k.qK, K.wrap180(q3 + kn.phi / D2R), R(wrapR(kn.psi - pb - kn.phi)), R(wrapR(kn.psi - pb))];
  }
  function fk(q) {
    const X = chain(q[0], q[1], q[2], q[3]), Rm3 = X.R123;
    const pa = V.add(M.mulv(Rm3, G.A0), X.t3);
    const R6 = M.mul(Rm3, M.rot(sn, q[4])), t6 = V.sub(pa, M.mulv(R6, G.A0m));
    const pbW = V.add(M.mulv(R6, G.Bm), t6), R5 = M.mul(R6, M.rot(sn, -q[5])), t5 = V.sub(pbW, M.mulv(R5, G.Bm));
    return Object.assign(X, { Rm3, R6, t6, R5, t5, pa, pb: pbW });
  }
  const check = (q, ctx) => {
    const Q = Qof(ctx), k = ik(Q);
    if (!k.c2ok || k.margin < 0) return 'J2 fold: the J1-J3 angle is outside the eccentric window';
    if (k.margin < P.margin) return `J2 within ${k.margin.toFixed(0)} deg of its fold (>= ${P.margin})`;
    if (k.mK < 3) return 'knee K at its own fold (crank 2a + link 2b span)';
    const F = fk(q), sv = M.mulv(M.T(Q), F.t3), kn = knee([V.dot(sv, sa), V.dot(sv, st)]);
    if (!kn.span) return 'cuff knee span: the drift is beyond lE + lc';
    if (kn.ang < P.ang_min || kn.ang > 180 - P.ang_min) return `cuff knee angle ${kn.ang.toFixed(0)} deg outside [${P.ang_min}, ${180 - P.ang_min}]`;
    return null;
  };
  const closes = (q, ctx) => { const r = C.residual(q, ctx); return Math.max(...r.map(Math.abs)) <= 0.5; };
  const solveC = (ctx, qPrev) => { const q = solve(ctx); return (!qPrev || closes(q, ctx)) ? q : K.dls(C, ctx, qPrev, { iters: 40 }).q; };
  const C = {
    id: 'slotted-eccentric-pin-knee-3r', name: 'Pin-knee 3R + slotted-lever eccentric J2 (K slaved to q2)',
    dof: { active: 3, passive: 3 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'J2 (crank 2a)', 'K (slaved by the slot)', 'J3', 'knee pin a', 'knee pin b'], qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve: solveC,
    residual: (q, ctx) => { const F = fk(q); return M.rotErrDeg(F.R5, Qof(ctx)).concat(F.t5); },
    check,
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), F = fk(q);
      const on = (R, t, p) => W(V.add(M.mulv(R, p), t)), I = M.I3(), Z = [0, 0, 0];
      const p1 = Wd(u[0]), p2 = Wd(M.mulv(F.R1, u[1])), pK = Wd(M.mulv(F.R2a, uK)), pF = Wd(M.mulv(F.R1, uF)), ax3 = Wd(M.mulv(F.R12, u[2]));
      const f = G.f, fK = f[1] + 4;
      const h3c = on(F.R12, F.t2, V.madd(c[2], u[2], f[2]));
      const n3 = Wd(M.mulv(F.Rm3, sn)), lvl = (p, h) => V.madd(W(p), n3, h), kz = G.tr + G.tp + G.RUN + G.tp / 2;
      const rim = on(F.Rm3, F.t3, V.add(V.madd(c[2], sn, f[2] + 1.5), V.scale(G.eE, rad)));
      const arm = p => M.mulv(ctx.H, p), padC = arm(V.madd(G.Bm, sn, G.tr + G.tp / 2)), padN = M.mulv(ctx.H, sn), lat = arm([G.Bm[0], -150, 50]);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base on the scapula handler', c: V.scale(p1, f[0] - 3), z: p1, x: ctx.attach.scapDir([1, 0, 0]), size: [40, 30], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1 (O20, GH ray)', c: V.scale(p1, f[0]), axis: p1, r: rad, h: hub },
        { kind: 'arc', role: 'link', name: 'link 1 (8 x 3, carries roller stud F1)', pts: G.L1.map(p => on(F.R1, F.t1, p)), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2 (O20, GH ray)', c: V.scale(p2, f[1]), axis: p2, r: rad, h: hub },
        { kind: 'hub', role: 'passive', name: 'roller stud F1 (MR52ZZ on link 1)', c: V.scale(pF, f[1] + 3), axis: pF, r: 3.5, h: 6 },
        { kind: 'arc', role: 'link', name: 'crank 2a (J2 -> K, arc 25)', u: p2, v: pK, r0: f[1] + hub + 1, r1: fK + 1, r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'knee K (O11 MR63ZZ pair, slaved to q2)', c: V.scale(pK, fK), axis: pK, r: 5.5, h: 9 },
        { kind: 'arc', role: 'link', name: 'slotted lever on link 2b (rides F1)', u: pK, v: pF, r0: fK + 9.5, r1: f[1] + 9.5, r: 1.8 },
        { kind: 'arc', role: 'link', name: 'link 2b (K -> J3, flies over the knee and pad)', pts: K.greatArc(pK, V.unit(h3c), fK + 9.5, V.norm(h3c) + hub + 1), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3 (skin-normal tilt, line misses GH)', c: h3c, axis: ax3, r: rad, h: hub, p0: on(F.R12, F.t2, c[2]) },
        { kind: 'link', role: 'link', name: 'E strap (member 3 -> pin a)', a: rim, b: lvl(F.pa, G.tr + 1.5), r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'cuff knee pin a (parallel to J3)', c: lvl(F.pa, G.tr), axis: n3, r: 6, h: P.stk, p0: lvl(F.pa, G.tr) },
        { kind: 'link', role: 'link', name: 'cuff knee link (flat Ti plate)', a: lvl(F.pa, kz), b: lvl(F.pb, kz), r: 3 },
        { kind: 'hub', role: 'passive', name: 'cuff knee pin b (parallel to J3)', c: lvl(F.pb, G.tr), axis: n3, r: 6, h: P.stk, p0: lvl(F.pb, G.tr) },
        { kind: 'plate', role: 'fixed-arm', name: 'arm pad (on the cuff / BOTTOM)', c: padC, z: padN, x: arm(sa), size: [14, 14], t: G.tp },
        { kind: 'link', role: 'fixed-arm', name: 'BOTTOM bar to the cuff (schematic)', a: V.madd(padC, padN, -2), b: lat, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: V.scale(ctx.armAxis, 155), axis: ctx.armAxis, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  };
  K.register(C);
})();
