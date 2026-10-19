/* proximal-j3-geodesic-knuckle-3r at its frozen-exact best ghost config (CMA k211: wd 71.9 / wa -9.7, knee lE 90.2 lc 22.2 at stk 6.0; Bench(110,360) exact frozen 16.52, 271 taken, 4 contacts; DEAD at gate 1 - takes 271 < 274, envsel 19.75): the long 32/48 K-dyad knuckle chain (pick3's J1 on the acromion top,
 * hub 2 posterolateral) with J3's seat moved up the lateral deltoid (the J1-J3 geodesic's arm end), the two-pin knee re-fit at
 * the MR63ZZ stack (stk 6.0), K slaved to th by the hub-2 law. GHOST: the K drive (gate 2: pinned-horn desmo or in-band RSSR)
 * is not placed, so no drive part is drawn. 3 active (J1, J2, J3), K slaved, pin knee outside the count.
 * Geometry from docs/concepts/models/proximal-j3-geodesic-knuckle-3r.py (mode viz). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 95.3275, "el1": 67.6601, "az2": 46.3741, "el2": 41.5718, "wd": 71.8879, "wa": -9.7321, "b3": 0.3445, "lE": 90.2078, "lc": 22.196, "phiE": 3.7737, "phib": -56.1306, "stk": 6.0, "ang_min": 22.2576, "bk1": 32.0, "bk2": 48.0, "sK": -1, "a1max": 74.5, "smhi": 14.0617, "smlo": 5.0333, "capK": 6.0, "law_mode": "seg", "kA": 2.3647, "t1": 6.0, "kB": 2.3647, "smt": 8.0, "kK": 2.3647, "i_rock": 6.0, "r_horn": 15.25, "r_lobe": 8.0, "arm_lo": 1.0};
  const G = {"u": [[0.03529, 0.92495, 0.37846], [-0.45242, 0.62069, 0.64036], [-0.10257, -0.14954, 0.98342]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-2.69443, -12.09595, -2.12039]], "uK": [-0.2729, 0.95893, -0.07735], "sa": [0.01551, -0.98876, -0.14874], "st": [0.9946, 0.0, 0.10374], "sn": [-0.10257, -0.14954, 0.98342], "A": [36.823, 54.315], "branch": -1.0, "m": [-10.77219, 2.89308, 0.0], "f": [50.55, 62.35, 76.2], "fK": 57.25, "capK": 6.0, "tr": 79.28, "tp": 2.75, "RUN": 0.5, "A0": [4.60702, -101.09599, -14.89258], "A0m": [7.31738, -90.44493, -12.99024], "Bm": [-10.82086, -102.6757, -16.74192], "eE": [0.08094, -0.98661, -0.14159], "psiA": -53.7191, "thLo": 22.5253, "thHi": 77.0769, "q2s": [98.8563, -0.893], "lawTh": [77.077, 78.111, 79.178, 80.276, 81.402, 82.556, 83.735, 84.937, 86.16, 87.403, 88.664, 89.941, 91.233, 92.537, 93.851, 95.175, 96.506, 97.842, 99.182, 100.523, 101.865, 103.204, 104.539, 105.868, 107.189, 108.5, 109.799, 111.083, 112.35, 113.597, 114.823, 116.024, 117.198, 118.342, 119.453, 120.528, 121.564, 122.558, 123.506, 124.406, 125.254, 126.046], "lawDK": [-0.0, -1.892, -3.784, -5.675, -7.567, -9.459, -11.351, -13.242, -15.134, -17.026, -18.918, -20.809, -22.701, -24.593, -26.485, -28.376, -30.268, -32.16, -34.052, -35.943, -37.835, -39.727, -41.619, -43.51, -45.402, -47.294, -49.186, -51.078, -52.969, -54.861, -56.753, -58.645, -60.536, -62.428, -64.32, -66.212, -68.103, -69.995, -71.887, -73.779, -75.67, -77.562], "lawQ2": [-0.893, -1.693, -2.493, -3.293, -4.093, -4.893, -5.693, -6.493, -7.293, -8.093, -8.893, -9.693, -10.493, -11.293, -12.093, -12.893, -13.693, -14.493, -15.293, -16.093, -16.893, -17.693, -18.493, -19.293, -20.093, -20.893, -21.693, -22.493, -23.293, -24.093, -24.893, -25.693, -26.493, -27.293, -28.093, -28.893, -29.693, -30.493, -31.293, -32.093, -32.893, -33.693], "emb": "rod", "rocker": [-23.394, 48.517, 28.471], "rockerAx": [-0.38398, 0.79635, 0.46731], "rodA": [-41.323, 51.043, 12.646], "rodB": [-23.742, 60.948, -19.048], "armA": [-23.394, 48.517, 28.471], "armB": [-39.019, 46.265, 9.842], "L1a": [[-1.86, 50.75, 9.69], [-5.43, 54.56, 5.26], [-4.33, 48.49, 8.77], [-8.75, 57.61, 4.95], [-7.15, 50.3, 8.59], [-6.57, 49.66, 12.79], [-10.45, 53.4, 8.57]], "L1b": [[-23.32, 56.73, 4.72], [-22.57, 49.61, 9.37], [-24.23, 48.22, 14.55], [-25.81, 46.49, 19.75], [-27.31, 44.41, 25.01], [-21.49, 57.31, 5.45], [-20.73, 49.68, 9.94], [-22.34, 48.26, 15.06], [-23.91, 46.62, 20.25], [-25.36, 44.55, 25.47], [-19.66, 57.89, 6.18], [-18.86, 49.56, 10.45], [-20.56, 48.46, 15.61], [-22.18, 47.02, 20.86], [-23.66, 45.1, 26.16], [-17.82, 58.47, 6.91], [-17.06, 49.51, 10.97], [-18.82, 48.72, 16.18], [-20.46, 47.43, 21.48], [-21.94, 45.6, 26.82]], "L2": [[-31.09, 32.41, 48.91], [-28.56, 22.83, 54.76], [-26.65, 13.37, 62.01], [-23.25, 2.51, 66.4], [-18.5, -8.72, 66.98], [-27.19, 28.49, 48.89], [-25.94, 20.27, 56.93], [-23.56, 10.48, 63.4], [-19.64, -0.47, 66.33], [-16.44, -12.72, 73.46], [-25.14, 26.51, 51.9], [-23.37, 17.75, 59.25], [-20.32, 7.54, 64.24], [-16.1, -3.35, 66.08], [-26.03, 34.61, 50.35], [-23.21, 24.65, 55.38], [-20.99, 15.35, 62.28], [-17.4, 4.72, 66.1], [-12.96, -6.3, 67.42]]};
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
    const state = th > G.thHi ? 1 : -1;
    if (state === -1) { const q2s = G.q2s[0], p = M.mulv(M.rot(u2, q2s), u3); return { q1: K.axisAngle(u1, p, w), dK: 0, q2: q2s, ok: false, L: { state } }; }
    // stretched: invert the tabulated law th(t) -> (q2, dK)
    const T = G.lawTh, n = T.length; let j = 0;
    while (j < n - 2 && T[j + 1] < th) j++;
    const ok = th <= T[n - 1], a = Math.max(0, Math.min(1, (th - T[j]) / Math.max(T[j + 1] - T[j], 1e-9)));
    const q2s = G.lawQ2[j] + a * (G.lawQ2[j + 1] - G.lawQ2[j]), dK = G.lawDK[j] + a * (G.lawDK[j + 1] - G.lawDK[j]);
    const p = M.mulv(M.rot(u2, q2s), u3), q1 = K.axisAngle(u1, M.mulv(M.rot(uK, dK), p), w);
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
    if (!k.ok) return k.L.state === 1 ? 'past the K stroke cap / stop B' : (k.L.state === -1 ? 'folded side: J2 on its dowel (no tooth)' : 'chain cannot close');
    const F = fk(q), sv = M.mulv(M.T(Q), F.t3), kn = knee([V.dot(sv, sa), V.dot(sv, st)]);
    if (!kn.span) return 'knee span: the drift is beyond lE + lc';
    if (kn.ang < P.ang_min || kn.ang > 180 - P.ang_min) return `knee angle ${kn.ang.toFixed(0)} deg outside [${P.ang_min}, ${180 - P.ang_min}]`;
    return null;
  };
  const closes = (q, ctx) => { const r = C.residual(q, ctx); return Math.max(...r.map(Math.abs)) <= 0.5; };
  const solveC = (ctx, qPrev) => { const q = solve(ctx); return (!qPrev || closes(q, ctx)) ? q : K.dls(C, ctx, qPrev, { iters: 40 }).q; };
  const C = {
    id: 'proximal-j3-geodesic-knuckle-3r', name: 'Proximal-J3 geodesic knuckle: 32/48 K dyad, J3 seat up the lateral deltoid, knee re-fit at stk 6.0 (3 active; K slaved, drive not placed: ghost)',
    dof: { active: 3, passive: 3 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'K (passive, slaved to th by the K drive - gate 2, not drawn)', 'J2', 'J3', 'knee pin a', 'knee pin b'], qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve: solveC,
    residual: (q, ctx) => { const F = fk(q); return M.rotErrDeg(F.R5, Qof(ctx)).concat(F.t5); },
    check,
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), F = fk(q);
      const on = (R, p) => W(M.mulv(R, p)), I = M.I3();
      const h1 = { kind: 'hub', role: 'active', name: 'J1 (axis on a GH ray)', c: W(V.scale(u[0], G.f[0])), axis: Wd(u[0]), r: rad, h: hub };
      const hK = { kind: 'hub', role: 'passive', name: 'K (O20, passive, slaved by the K drive; drive not placed in this ghost)', c: on(F.R1, V.scale(uK, G.fK)), axis: Wd(M.mulv(F.R1, uK)), r: rad, h: hub + (G.capK || 0) };
      const h2 = { kind: 'hub', role: 'active', name: 'J2 (axis on a GH ray; folded dowel stop, drive stop B)', c: on(F.R1b, V.scale(u[1], G.f[1])), axis: Wd(M.mulv(F.R1b, u[1])), r: rad, h: hub };
      const h3 = { kind: 'hub', role: 'active', name: 'J3 (skin-normal tilt, line misses GH)', c: on(F.R12, V.madd(c[2], u[2], G.f[2])), axis: Wd(M.mulv(F.R12, u[2])), r: rad, h: hub,
                   p0: on(F.R12, c[2]) };
      const n3 = Wd(M.mulv(F.Rm3, sn)), lvl = (p, h) => V.madd(W(p), n3, h), kz = G.tr + G.tp + G.RUN + G.tp / 2;
      const rim = W(V.add(M.mulv(F.Rm3, V.add(V.madd(c[2], sn, G.f[2] + 1.5), V.scale(G.eE, rad))), F.t3));
      const arm = p => M.mulv(ctx.H, p), padC = arm(V.madd(G.Bm, sn, G.tr + G.tp / 2)), padN = M.mulv(ctx.H, sn), lat = arm([G.Bm[0], -150, 50]);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base on the scapula handler', c: V.madd(h1.c, h1.axis, -3), z: h1.axis, x: ctx.attach.scapDir([1, 0, 0]), size: [40, 30], t: 3 },
        h1,
        { kind: 'arc', role: 'link', name: 'link 1a (8 x 3 strap, J1 -> K)', pts: (G.L1a.length ? G.L1a : [V.scale(u[0], G.f[0]), V.scale(uK, G.fK)]).map(p => on(F.R1, p)), r: 2.5 },
        hK,
        { kind: 'arc', role: 'link', name: 'link 1b (8 x 3 strap, K -> J2)', pts: G.L1b.map(p => on(F.R1b, p)), r: 2.5 },
        h2,
        { kind: 'arc', role: 'link', name: 'link 2 (8 x 3 strap, fitted)', pts: G.L2.map(p => on(F.R12, p)), r: 2.5 },
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
