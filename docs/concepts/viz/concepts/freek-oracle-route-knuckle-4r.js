/* freek-oracle-route-knuckle-4r - the FREE-K ORACLE BOUND (an instrument, never a claim) on skinnormal-shortk's k33 chain,
 * with link 2 bent in planform into an anterior corridor (route {"rA": 0}).
 * J1 (O20, GH ray) -> link 1a -> K (O20, SENSED, counted: in the bound K is picked PER POSE by an oracle on the legal
 * self-motion [5.5-deg floor, stop B]; no unpowered mechanism can do that) -> link 1b -> J2 (O20, GH ray, own-angle slot)
 * -> link 2 (corridor bar) -> J3 (O20, skin-normal tilt) -> member 3 -> flat two-pin knee (MR63ZZ pairs) -> cuff.
 * This PREVIEW shows CELL B (the built determination): K on stop A inside [thLo, thHi], J2 on its stop past it with K at the
 * minimal opening, and wherever J3's own angle passes q3max 86 deg K opens further to hold it (frozen exact 17.35 connected);
 * the oracle's per-pose pick needs the skin distance and is not reproduced here. Bound: frozen exact Bench(110,360) connected 17.25 plain / 21.46 near-touch (kit 18.61 at the same shape).
 * Geometry exported from docs/concepts/models/freek-oracle-route-knuckle-4r.py (viz mode, fit on Bench(60,160)).
 * Red = K would pass stop B / the knee outside its window. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"q3max": 86, "az1": 101.6411, "el1": 67.8564, "az2": 44.3978, "el2": 43.8721, "wd": 66.5965, "wa": -9.6278, "b3": 0.4, "lE": 73.8692, "lc": 28.6946, "phiE": 1.3552, "phib": -53.1496, "stk": 5.791, "ang_min": 26.1449, "bk1": 32.0, "bk2": 52.0, "sK": -1.0, "a1max": 76.0441, "smlo": 7.8286, "smhi": 7.877, "capK": 6.0};
  const G = {"u": [[0.07606, 0.92624, 0.36918], [-0.46498, 0.65068, 0.60034], [-0.1212, -0.18362, 0.9755]], "uK": [-0.12993, 0.98171, -0.13915], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-0.52423, -16.62839, -3.1952]], "sa": [0.02264, -0.983, -0.18222], "st": [0.99237, -0.0, 0.12329], "sn": [-0.1212, -0.18362, 0.9755], "A": [37.912, 58.5], "branch": -1.0, "m": [-15.40291, 0.88702, 0.0], "f": [49.11, 60.91, 79.0], "fK": 56.66, "capK": 6.0, "tr": 84.21, "tp": 2.646, "RUN": 0.5, "SING": 5.5, "hr": [10.0, 10.0, 10.0], "A0": [2.8814, -89.22125, -16.43669], "A0m": [3.41293, -74.08025, -13.52056], "Bm": [-18.98381, -90.99658, -19.48745], "eE": [0.0461, -0.98272, -0.17926], "eK": [-0.78052, -0.58953, -0.20794], "psiA": -50.2809, "dKB": 82.0, "thLo": 28.4166, "thHi": 88.535, "q2s": [89.3267, -21.3537], "L1a": [[-0.66, 49.9, 7.89], [-1.93, 54.09, 5.51], [-2.92, 57.86, 3.73]], "L1b": [[-13.51, 57.52, 2.63], [-14.46, 51.71, 6.57], [-16.71, 51.3, 10.85], [-18.53, 50.82, 14.36], [-20.68, 49.65, 18.75], [-22.62, 47.8, 23.03], [-24.93, 47.58, 27.32]], "L2": [[-28.44, 33.32, 45.42], [-27.01, 29.45, 46.05], [-26.96, 26.55, 49.75], [-26.74, 23.36, 53.31], [-26.36, 20.52, 55.9], [-25.82, 17.47, 58.26], [-24.57, 14.75, 60.26], [-24.87, 12.04, 62.09], [-24.44, 8.99, 63.82], [-22.97, 5.65, 65.08], [-21.77, 1.98, 66.18], [-20.41, -1.73, 66.9], [-18.97, -5.47, 67.39], [-16.92, -9.34, 67.28], [-16.32, -13.38, 68.18], [-15.61, -16.8, 72.07], [-15.38, -19.62, 75.12], [-15.05, -22.61, 78.09]]};
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
  /** free-K closure (J2 off its stop) at a given K opening dK (deg): the (a1e, a2) dyad on the arm's J3 axis, same branch */
  function freeAt(Q, dK) {
    const [u1, u2, u3] = u, w = M.mulv(Q, u3), RK = M.rot(uK, dK), v2 = M.mulv(RK, u2), v3 = M.mulv(RK, u3);
    const c12 = dot(u1, v2), b1 = dot(w, u1), b2 = cb(a2), det = 1 - c12 * c12, al = (b1 - c12 * b2) / det, be = (b2 - c12 * b1) / det;
    const cr = V.cross(u1, v2), g2 = (1 - al * al - be * be - 2 * al * be * c12) / dot(cr, cr);
    let pick = null;
    for (const sg of [1, -1]) {
      const z = V.madd(V.add(V.scale(u1, al), V.scale(v2, be)), cr, sg * Math.sqrt(Math.max(g2, 0)));
      const q1 = K.axisAngle(u1, z, w), q2 = K.axisAngle(v2, v3, z), p2 = M.mulv(M.rot(u1, q1), v2);
      const br = Math.sign(dot(p2, V.cross(u1, w)));
      if (pick === null || br === G.branch) pick = [q1, q2];
    }
    return { q1: pick[0], dK, q2: pick[1], ok: g2 > 0, L: { state: 2 } };
  }
  const q3of = (Q, k) => K.axisAngle(u[2], vref, M.mulv(M.T(M.mul(M.mul(M.rot(u[0], k.q1), M.rot(uK, k.dK)), M.rot(u[1], k.q2))), M.mulv(Q, vref)));
  /** CELL B: J3's own-angle dowel stop at P.q3max (deg, the model's convention); past it K opens (0.5-deg steps up to stop B) to hold q3 = q3max */
  function law(Q) {
    let k = ik(Q), q3 = q3of(Q, k), stopped = false;
    if (k.ok && P.q3max !== undefined && q3 > P.q3max) {
      const sp = Math.sign(G.psiA); let found = null;
      for (let d = Math.abs(k.dK); d <= G.dKB + 1e-9; d += 0.5) {
        const f = freeAt(Q, sp * d); if (!f.ok) continue; const q3f = q3of(Q, f);
        if (q3f <= P.q3max) { found = [f, q3f]; break; }
      }
      if (found) { k = found[0]; q3 = found[1]; } else stopped = true;
    }
    return { k, q3, stopped };
  }
  function solve(ctx) {
    const Q = Qof(ctx), lw = law(Q), k = lw.k, q3 = lw.q3, X = chain(k.q1, k.dK, k.q2, q3);
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
    const Q = Qof(ctx), lw = law(Q), k = lw.k;
    if (lw.stopped) return `J3 on its q3max stop (${P.q3max} deg): K would pass stop B`;
    if (!k.ok) return k.L.state ? `J2 on its q2 stop: K would pass stop B (a1max ${P.a1max} deg)` : 'chain cannot close';
    const F = fk(q), sv = M.mulv(M.T(Q), F.t3), kn = knee([V.dot(sv, sa), V.dot(sv, st)]);
    if (!kn.span) return 'knee span: the drift is beyond lE + lc';
    if (kn.ang < P.ang_min || kn.ang > 180 - P.ang_min) return `knee angle ${kn.ang.toFixed(0)} deg outside [${P.ang_min}, ${180 - P.ang_min}]`;
    return null;
  };
  const closes = (q, ctx) => { const r = C.residual(q, ctx); return Math.max(...r.map(Math.abs)) <= 0.5; };
  const solveC = (ctx, qPrev) => { const q = solve(ctx); return (!qPrev || closes(q, ctx)) ? q : K.dls(C, ctx, qPrev, { iters: 40 }).q; };
  const C = {
    id: 'freek-oracle-route-knuckle-4r', name: 'Free-K oracle bound row, previewed as its CELL B: sensed knuckle 4R + J3 own-angle stop at q3max 86 (K opens to hold it)',
    dof: { active: 4, passive: 2 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'K (sensed; spring to stop A, opened by J2 stop or J3 q3max stop)', 'J2', 'J3', 'knee pin a', 'knee pin b'], qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve: solveC,
    residual: (q, ctx) => { const F = fk(q); return M.rotErrDeg(F.R5, Qof(ctx)).concat(F.t5); },
    check,
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), F = fk(q);
      const on = (R, p) => W(M.mulv(R, p)), I = M.I3();
      const h1 = { kind: 'hub', role: 'active', name: 'J1 (axis on a GH ray)', c: W(V.scale(u[0], G.f[0])), axis: Wd(u[0]), r: rad, h: hub };
      const hK = { kind: 'hub', role: 'active', name: 'K (O20, sensed; cell B: opened by the J2 stop or the J3 q3max stop)', c: on(F.R1, V.scale(uK, G.fK)), axis: Wd(M.mulv(F.R1, uK)), r: rad, h: hub + (G.capK || 0) };
      const h2 = { kind: 'hub', role: 'active', name: 'J2 (axis on a GH ray, dowel-in-slot stop on q2)', c: on(F.R1b, V.scale(u[1], G.f[1])), axis: Wd(M.mulv(F.R1b, u[1])), r: rad, h: hub };
      const h3 = { kind: 'hub', role: 'active', name: 'J3 (skin-normal tilt, line misses GH; cell B dowel stop at q3max 86)', c: on(F.R12, V.madd(c[2], u[2], G.f[2])), axis: Wd(M.mulv(F.R12, u[2])), r: rad, h: hub,
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
        { kind: 'arc', role: 'link', name: 'link 2 (12 x 3 Ti bar, anterior planform corridor, fitted)', pts: G.L2.map(p => on(F.R12, p)), r: 2.5 },
        h3,
        { kind: 'link', role: 'link', name: 'E strap (member 3: hub 3 lower plate -> pin a)', a: rim, b: lvl(F.pa, G.tr + 1.5), r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'knee pin a (MR63ZZ pair, parallel to J3)', c: lvl(F.pa, G.tr), axis: n3, r: 6, h: P.stk, p0: lvl(F.pa, G.tr) },
        { kind: 'link', role: 'link', name: 'knee link (flat Ti plate)', a: lvl(F.pa, kz), b: lvl(F.pb, kz), r: 3 },
        { kind: 'hub', role: 'passive', name: 'knee pin b (MR63ZZ pair, parallel to J3)', c: lvl(F.pb, G.tr), axis: n3, r: 6, h: P.stk, p0: lvl(F.pb, G.tr) },
        { kind: 'plate', role: 'fixed-arm', name: 'arm pad (on the cuff / BOTTOM)', c: padC, z: padN, x: arm(sa), size: [14, 14], t: G.tp },
        { kind: 'link', role: 'fixed-arm', name: 'BOTTOM bar to the cuff (schematic)', a: V.madd(padC, padN, -2), b: lat, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: V.scale(ctx.armAxis, 155), axis: ctx.armAxis, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  };
  K.register(C);
})();
