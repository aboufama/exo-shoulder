/* skinnormal-shortk-knuckle-4r - near-touch-robust redundant 4R (Keemink layout, determined spare): pick1's sensed-knuckle
 * chain (J1 / J2 on GH rays, J3 tilted toward the skin normal, a flat two-pin knee closing member 3 on the cuff) with a SHORT
 * knuckle K (O20, SENSED = active under the 2026-10-17 ruling; clock spring preloaded onto stop A, cap +6 mm) splitting
 * link 1, and a dowel-in-slot stop on J2's OWN angle q2. Inside [thLo, thHi] K stays on stop A (a rigid 3R); past it J2
 * sits on its stop and the arm opens K to the smallest rotation that closes the chain (closed form, <= stop B).
 * Exactly docs/concepts/models/skinnormal-shortk-knuckle-4r.py (pick1's kitrule harness, phys 1, priced stops) at the repaired skinnormal seed (stop B a1max 64.84)
 * (axes, hub levels, knee frames, q2 stops, strap centrelines exported from the model's fit on Bench(60,160)).
 * Red = K would pass stop B / the knee outside its window. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 94.8966, "el1": 68.0169, "az2": 46.348, "el2": 43.1623, "wd": 66.2813, "wa": -9.5402, "b3": 0.3653, "lE": 73.8692, "lc": 28.6946, "phiE": 1.3552, "phib": -53.1496, "stk": 5.791, "ang_min": 26.1449, "bk1": 29.6527, "bk2": 40.7017, "sK": -1.0, "a1max": 64.8444, "smlo": 6.9468, "smhi": 11.326, "capK": 6.0};
  const G = {"u": [[0.03195, 0.92729, 0.37297], [-0.44705, 0.6452, 0.61956], [-0.12127, -0.20912, 0.97034]], "uK": [-0.32318, 0.94632, 0.00495], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-0.57654, -15.11473, -3.32948]], "sa": [0.02593, -0.97789, -0.20751], "st": [0.99228, -0.0, 0.12401], "sn": [-0.12127, -0.20912, 0.97034], "A": [35.404, 58.636], "branch": -1.0, "m": [-12.88056, 0.98495, 0.0], "f": [49.61, 61.16, 79.81], "fK": 56.06, "capK": 6.0, "tr": 85.61, "tp": 2.646, "RUN": 0.5, "SING": 5.5, "hr": [10.0, 10.0, 10.0], "A0": [3.07217, -87.33045, -18.43692], "A0m": [3.71547, -74.73469, -15.64197], "Bm": [-18.62253, -91.56314, -22.06044], "eE": [0.04939, -0.97762, -0.20452], "eK": [-0.77847, -0.58647, -0.22368], "psiA": -61.0332, "dKB": 75.3961, "thLo": 30.1782, "thHi": 82.7142, "q2s": [94.5875, -5.233], "L1a": [[-6.25, 49.13, 11.38], [-8.1, 52.13, 10.52], [-10.23, 55.7, 9.57]], "L1b": [[-27.05, 47.95, 29.27], [-24.92, 46.52, 24.8], [-24.12, 47.39, 21.82], [-23.6, 47.94, 19.88], [-22.76, 48.6, 16.97], [-21.84, 49.05, 14.06], [-22.32, 52.79, 11.95]], "L2": [[-27.6, 33.19, 46.79], [-26.7, 29.84, 48.21], [-26.29, 26.46, 51.2], [-26.0, 23.13, 54.56], [-25.74, 20.33, 57.34], [-25.3, 17.29, 59.84], [-24.89, 13.9, 61.39], [-23.93, 11.4, 62.99], [-22.97, 8.83, 64.66], [-22.25, 5.18, 65.55], [-20.98, 1.49, 66.19], [-19.73, -2.21, 66.84], [-18.31, -6.25, 67.05], [-16.76, -9.71, 67.35], [-15.75, -13.61, 68.53], [-15.51, -17.46, 72.68], [-15.31, -20.3, 75.69], [-15.01, -23.32, 78.6]]};
  const u = G.u, c = G.c, uK = G.uK, sn = G.sn, sa = G.sa, st = G.st, a1 = G.A[0], a2 = G.A[1], hub = 12.25, rad = 10;
  const wrapR = a => { a = (a + Math.PI) % (2 * Math.PI); return (a < 0 ? a + 2 * Math.PI : a) - Math.PI; };
  const pe = P.phiE * D2R, pb = P.phib * D2R, lE = P.lE, lc = P.lc;
  const A02 = [G.m[0] + lE * Math.cos(pe), G.m[1] + lE * Math.sin(pe)], B2 = [A02[0] + lc * Math.cos(pb), A02[1] + lc * Math.sin(pb)];
  const kbr = Math.sign(wrapR(pe - Math.atan2(B2[1] - G.m[1], B2[0] - G.m[0]))) || 1;
  const vref = V.unit(V.cross(u[2], [0.3, 0.5, 0.8]));
  const cb = x => Math.cos(x * D2R), sb = x => Math.sin(x * D2R);
  /** physical J2 stop: th (deg) inside [thLo, thHi] -> K on stop A (state 0); else J2 locked on its q2 stop, K opens */
  const dot = V.dot;
  function ik(Q) {
    const [u1, u2, u3] = u, w = M.mulv(Q, u3), th = V.angle(w, u1);
    if (th >= G.thLo && th <= G.thHi) {
      const c12 = dot(u1, u2), b1 = dot(w, u1), b2 = cb(a2), det = 1 - c12 * c12;
      const al = (b1 - c12 * b2) / det, be = (b2 - c12 * b1) / det, cr = V.cross(u1, u2);
      const g2 = (1 - al * al - be * be - 2 * al * be * c12) / dot(cr, cr);
      let pick = null;
      for (const sg of [1, -1]) {
        const z = V.madd(V.add(V.scale(u1, al), V.scale(u2, be)), cr, sg * Math.sqrt(Math.max(g2, 0)));
        const q1 = K.axisAngle(u1, z, w), q2 = K.axisAngle(u2, u3, z), p2 = M.mulv(M.rot(u1, q1), u2);
        const br = Math.sign(dot(p2, V.cross(u1, w)));
        if (pick === null || br === G.branch) pick = [q1, q2];
      }
      return { q1: pick[0], dK: 0, q2: pick[1], ok: g2 > 0, L: { state: 0 } };
    }
    const state = th > G.thHi ? 1 : -1, q2s = state === 1 ? G.q2s[1] : G.q2s[0], p = M.mulv(M.rot(u2, q2s), u3);
    const A0 = dot(u1, uK) * dot(uK, p), Bk = dot(u1, p) - A0, Ck = dot(u1, V.cross(uK, p));
    const x = (cb(th) - A0) / Math.hypot(Bk, Ck), f0 = Math.atan2(Ck, Bk) / D2R, sp = Math.sign(G.psiA);
    let dK = sp * G.dKB, ok = false;
    if (Math.abs(x) <= 1) {
      const g = Math.acos(x) / D2R; let best = Infinity;
      for (const r0 of [f0 - g, f0 + g]) { const r = K.wrap180(r0); if (r * sp >= -1e-9 && Math.abs(r) < best) best = Math.abs(r); }
      if (best <= G.dKB + 1e-9) { dK = sp * best; ok = true; }
    }
    const q1 = K.axisAngle(u1, M.mulv(M.rot(uK, dK), p), w);
    return { q1, dK, q2: q2s, ok, L: { state } };
  }
  function chain(q1, dK, q2, q3) {
    const R1 = M.rot(u[0], q1), R1b = M.mul(R1, M.rot(uK, dK)), R12 = M.mul(R1b, M.rot(u[1], q2)), R3 = M.rot(u[2], q3), R123 = M.mul(R12, R3);
    const t3 = M.mulv(R12, V.sub(c[2], M.mulv(R3, c[2])));
    return { R1, R1b, R12, R123, t3 };
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
    const Q = Qof(ctx), k = ik(Q), R12 = M.mul(M.mul(M.rot(u[0], k.q1), M.rot(uK, k.dK)), M.rot(u[1], k.q2));
    const q3 = K.axisAngle(u[2], vref, M.mulv(M.T(R12), M.mulv(Q, vref))), X = chain(k.q1, k.dK, k.q2, q3);
    const sv = M.mulv(M.T(Q), X.t3), s = [V.dot(sv, sa), V.dot(sv, st), V.dot(sv, sn)], kn = knee(s);
    const R = x => K.wrap180(x / D2R);
    return [k.q1, k.dK, k.q2, K.wrap180(q3 + kn.phi / D2R), R(wrapR(kn.psi - pb - kn.phi)), R(wrapR(kn.psi - pb))];
  }
  function fk(q) {
    const X = chain(q[0], q[1], q[2], q[3]), Rm3 = X.R123, pa = V.add(M.mulv(Rm3, G.A0), X.t3);
    const R6 = M.mul(Rm3, M.rot(sn, q[4])), t6 = V.sub(pa, M.mulv(R6, G.A0m));
    const pbW = V.add(M.mulv(R6, G.Bm), t6), R5 = M.mul(R6, M.rot(sn, -q[5])), t5 = V.sub(pbW, M.mulv(R5, G.Bm));
    return Object.assign(X, { Rm3, R6, t6, R5, t5, pa, pb: pbW });
  }
  const check = (q, ctx) => {
    const Q = Qof(ctx), k = ik(Q);
    if (!k.ok) return k.L.state ? `J2 on its q2 stop: K would pass stop B (a1max ${P.a1max} deg)` : 'chain cannot close';
    const F = fk(q), sv = M.mulv(M.T(Q), F.t3), kn = knee([V.dot(sv, sa), V.dot(sv, st)]);
    if (!kn.span) return 'knee span: the drift is beyond lE + lc';
    if (kn.ang < P.ang_min || kn.ang > 180 - P.ang_min) return `knee angle ${kn.ang.toFixed(0)} deg outside [${P.ang_min}, ${180 - P.ang_min}]`;
    return null;
  };
  const closes = (q, ctx) => { const r = C.residual(q, ctx); return Math.max(...r.map(Math.abs)) <= 0.5; };
  const solveC = (ctx, qPrev) => { const q = solve(ctx); return (!qPrev || closes(q, ctx)) ? q : K.dls(C, ctx, qPrev, { iters: 40 }).q; };
  const C = {
    id: 'skinnormal-shortk-knuckle-4r', name: 'Short sensed knuckle 4R on the pin knee: spring-held K (sensed) in link 1, J2 dowel stop on q2',
    dof: { active: 4, passive: 2 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'K (sensed, spring + stops)', 'J2', 'J3', 'knee pin a', 'knee pin b'], qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve: solveC,
    residual: (q, ctx) => { const F = fk(q); return M.rotErrDeg(F.R5, Qof(ctx)).concat(F.t5); },
    check,
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), F = fk(q);
      const on = (R, p) => W(M.mulv(R, p)), I = M.I3();
      const h1 = { kind: 'hub', role: 'active', name: 'J1 (axis on a GH ray)', c: W(V.scale(u[0], G.f[0])), axis: Wd(u[0]), r: rad, h: hub };
      const hK = { kind: 'hub', role: 'active', name: 'K (O20, sensed; clock-spring cap, stop A)', c: on(F.R1, V.scale(uK, G.fK)), axis: Wd(M.mulv(F.R1, uK)), r: rad, h: hub + (G.capK || 0) };
      const h2 = { kind: 'hub', role: 'active', name: 'J2 (axis on a GH ray, dowel-in-slot stop on q2)', c: on(F.R1b, V.scale(u[1], G.f[1])), axis: Wd(M.mulv(F.R1b, u[1])), r: rad, h: hub };
      const h3 = { kind: 'hub', role: 'active', name: 'J3 (skin-normal tilt, line misses GH)', c: on(F.R12, V.madd(c[2], u[2], G.f[2])), axis: Wd(M.mulv(F.R12, u[2])), r: rad, h: hub,
                   p0: on(F.R12, c[2]) };
      const n3 = Wd(M.mulv(F.Rm3, sn)), lvl = (p, h) => V.madd(W(p), n3, h), kz = G.tr + G.tp + G.RUN + G.tp / 2;
      const rim = W(V.add(M.mulv(F.Rm3, V.add(V.madd(c[2], sn, G.f[2] + 1.5), V.scale(G.eE, rad))), F.t3));
      const arm = p => M.mulv(ctx.H, p), padC = arm(V.madd(G.Bm, sn, G.tr + G.tp / 2)), padN = M.mulv(ctx.H, sn), lat = arm([G.Bm[0], -150, 50]);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base on the scapula handler', c: V.madd(h1.c, h1.axis, -3), z: h1.axis, x: ctx.attach.scapDir([1, 0, 0]), size: [40, 30], t: 3 },
        h1,
        { kind: 'arc', role: 'link', name: 'link 1a (12 x 3 strap, J1 -> K)', pts: (G.L1a.length ? G.L1a : [V.scale(u[0], G.f[0]), V.scale(uK, G.fK)]).map(p => on(F.R1, p)), r: 2.5 },
        hK,
        { kind: 'arc', role: 'link', name: 'link 1b (12 x 3 strap, K -> J2)', pts: G.L1b.map(p => on(F.R1b, p)), r: 2.5 },
        h2,
        { kind: 'arc', role: 'link', name: 'link 2 (12 x 3 strap, fitted)', pts: G.L2.map(p => on(F.R12, p)), r: 2.5 },
        h3,
        { kind: 'link', role: 'link', name: 'E strap (member 3: hub 3 lower plate -> pin a)', a: rim, b: lvl(F.pa, G.tr + 1.5), r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'knee pin a (iglidur pin, parallel to J3)', c: lvl(F.pa, G.tr), axis: n3, r: 6, h: P.stk, p0: lvl(F.pa, G.tr) },
        { kind: 'link', role: 'link', name: 'knee link (flat Ti plate)', a: lvl(F.pa, kz), b: lvl(F.pb, kz), r: 3 },
        { kind: 'hub', role: 'passive', name: 'knee pin b (iglidur pin, parallel to J3)', c: lvl(F.pb, G.tr), axis: n3, r: 6, h: P.stk, p0: lvl(F.pb, G.tr) },
        { kind: 'plate', role: 'fixed-arm', name: 'arm pad (on the cuff / BOTTOM)', c: padC, z: padN, x: arm(sa), size: [14, 14], t: G.tp },
        { kind: 'link', role: 'fixed-arm', name: 'BOTTOM bar to the cuff (schematic)', a: V.madd(padC, padN, -2), b: lat, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: V.scale(ctx.armAxis, 155), axis: ctx.armAxis, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  };
  K.register(C);
})();
