/* desmo-vrocker-longdyad-knuckle-3r at its gate-3 ghost cell onset14-cap56 (DEAD at gate 3; gate 1 fails with the spec's own parts): the spiral-lobe chain on the
 * 32/48 K dyad (stop B 74.5), linear hub-2 law kK 2.5 past the onset margin, K capped at the conjugate-lobe stroke. Drive (schematic):
 * crank on link 1b beside hub 2 (MR63ZZ pair); its V short arm carries two O2.5 pins riding two stacked open lobe tracks on hub 2's
 * cap ring (one pushes each way); its long arm's slotted tip rides a nose dowel on link 1a (pinned horn). No spring, roller, rod or
 * ball link. 3 active (J1, J2, J3), K slaved, not read; pin knee. Geometry from docs/concepts/models/desmo-vrocker-longdyad-knuckle-3r.py (mode viz). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 95.3275, "el1": 67.6601, "az2": 46.3741, "el2": 41.5718, "wd": 66.0692, "wa": -10.7812, "b3": 0.3246, "lE": 67.832, "lc": 21.5474, "phiE": -2.7863, "phib": -57.916, "stk": 4.8534, "ang_min": 25.2189, "bk1": 32.0, "bk2": 48.0, "sK": -1, "a1max": 74.5, "smhi": 14.0, "smlo": 5.0333, "capK": 6.0, "law_mode": "seg", "kA": 2.5, "t1": 6.0, "kB": 2.5, "smt": 8.0, "kK": 2.5, "i_rock": 6.0, "r_horn": 15.25, "r_lobe": 8.0, "arm_lo": 1.0};
  const G = {"u": [[0.03529, 0.92495, 0.37846], [-0.45858, 0.62409, 0.63262], [-0.13867, -0.23452, 0.96217]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-0.8423, -13.51955, -3.41666]], "uK": [-0.26528, 0.96065, -0.08229], "sa": [0.03345, -0.97211, -0.23212], "st": [0.98977, -0.0, 0.14265], "sn": [-0.13867, -0.23452, 0.96217], "A": [36.823, 58.27], "branch": -1.0, "m": [-11.56648, 1.32047, 0.0], "f": [50.55, 61.6, 80.6], "fK": 57.25, "capK": 6.0, "tr": 88.82, "tp": 2.177, "RUN": 0.5, "A0": [-1.83935, -79.38185, -19.61369], "A0m": [-0.91934, -68.13795, -16.74049], "Bm": [-18.60621, -79.26391, -22.00147], "eE": [-0.0147, -0.97096, -0.23878], "psiA": -53.7191, "thLo": 26.4797, "thHi": 81.093, "q2s": [101.5774, 1.6627], "lawTh": [81.093, 82.159, 83.262, 84.399, 85.569, 86.769, 87.997, 89.252, 90.531, 91.832, 93.153, 94.493, 95.848, 97.218, 98.6, 99.992, 101.392, 102.798, 104.208, 105.619, 107.03, 108.438, 109.841, 111.236, 112.622, 113.994, 115.351, 116.69, 118.008], "lawDK": [-0.0, -2.0, -4.0, -6.0, -8.0, -10.0, -12.0, -14.0, -16.0, -18.0, -20.0, -22.0, -24.0, -26.0, -28.0, -30.0, -32.0, -34.0, -36.0, -38.0, -40.0, -42.0, -44.0, -46.0, -48.0, -50.0, -52.0, -54.0, -56.0], "lawQ2": [1.663, 0.863, 0.063, -0.737, -1.537, -2.337, -3.137, -3.937, -4.737, -5.537, -6.337, -7.137, -7.937, -8.737, -9.537, -10.337, -11.137, -11.937, -12.737, -13.537, -14.337, -15.137, -15.937, -16.737, -17.537, -18.337, -19.137, -19.937, -20.737], "emb": "rod", "rocker": [-23.152, 48.152, 27.549], "rockerAx": [-0.38514, 0.80103, 0.45828], "rodA": [-40.798, 50.766, 11.423], "rodB": [-23.05, 61.089, -19.454], "armA": [-23.152, 48.152, 27.549], "armB": [-38.488, 45.96, 8.674], "L1a": [[-1.68, 50.77, 9.63], [-5.15, 54.6, 5.14], [-4.13, 48.37, 8.64], [-8.45, 57.67, 4.78], [-6.96, 50.36, 8.44], [-6.45, 49.71, 12.66], [-10.23, 53.48, 8.37]], "L1b": [[-23.21, 56.87, 4.75], [-22.38, 49.12, 9.48], [-24.15, 47.59, 14.78], [-25.92, 45.87, 20.17], [-28.33, 44.87, 26.31], [-20.76, 53.63, 7.05], [-21.14, 48.69, 11.81], [-23.03, 47.45, 17.21], [-24.83, 45.78, 22.71], [-28.51, 46.9, 30.43], [-18.43, 50.31, 9.03], [-20.08, 48.65, 14.23], [-21.92, 47.34, 19.68], [-23.64, 45.53, 25.22], [-17.72, 58.59, 7.04], [-17.08, 49.44, 11.25], [-18.99, 48.58, 16.65], [-20.81, 47.27, 22.19], [-23.05, 46.52, 28.51]], "L2": [[-31.75, 32.32, 47.45], [-29.45, 22.55, 52.31], [-28.34, 13.43, 59.35], [-25.73, 2.91, 63.73], [-22.2, -8.23, 66.14], [-20.21, -22.13, 75.1], [-28.12, 25.94, 50.38], [-27.68, 17.59, 58.73], [-25.43, 7.29, 64.07], [-21.78, -3.8, 66.24], [-18.25, -15.63, 69.48], [-26.9, 29.35, 48.63], [-26.32, 21.23, 56.62], [-24.72, 11.56, 63.38], [-21.62, 0.61, 67.12], [-17.36, -10.64, 67.67], [-26.89, 34.24, 49.08], [-24.99, 24.72, 54.54], [-23.85, 15.71, 62.27], [-21.35, 5.09, 67.7], [-17.41, -6.33, 69.52], [-14.12, -19.63, 76.57]], "vrPV": [-27.767, 51.207, 28.274], "vrAx": [-0.429, 0.791, 0.437], "pinA": [-29.38, 47.816, 35.429], "pinB": [-31.917, 46.139, 32.873], "nose": [-9.298, 59.739, -24.847], "noseRoot": [-12.859, 59.602, -14.97], "track": [-29.798, 40.552, 41.106], "kcap": 56.0};
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
    if (!k.ok) return k.L.state === 1 ? 'past the drive stop (conjugate-lobe cap / stop B)' : (k.L.state === -1 ? 'folded side: J2 on its dowel (no tooth)' : 'chain cannot close');
    const F = fk(q), sv = M.mulv(M.T(Q), F.t3), kn = knee([V.dot(sv, sa), V.dot(sv, st)]);
    if (!kn.span) return 'knee span: the drift is beyond lE + lc';
    if (kn.ang < P.ang_min || kn.ang > 180 - P.ang_min) return `knee angle ${kn.ang.toFixed(0)} deg outside [${P.ang_min}, ${180 - P.ang_min}]`;
    return null;
  };
  const closes = (q, ctx) => { const r = C.residual(q, ctx); return Math.max(...r.map(Math.abs)) <= 0.5; };
  const solveC = (ctx, qPrev) => { const q = solve(ctx); return (!qPrev || closes(q, ctx)) ? q : K.dls(C, ctx, qPrev, { iters: 40 }).q; };
  const C = {
    id: 'desmo-vrocker-longdyad-knuckle-3r', name: 'Desmo V-rocker long dyad: 32/48 K dyad, conjugate open lobes on hub 2 + pinned-horn slot, no spring (3 active, K not read; dead at gate 3)',
    dof: { active: 3, passive: 3 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'K (passive, slaved to q2: conjugate lobes - V crank - slotted tip on the nose)', 'J2', 'J3', 'knee pin a', 'knee pin b'], qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve: solveC,
    residual: (q, ctx) => { const F = fk(q); return M.rotErrDeg(F.R5, Qof(ctx)).concat(F.t5); },
    check,
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), F = fk(q);
      const on = (R, p) => W(M.mulv(R, p)), I = M.I3();
      const h1 = { kind: 'hub', role: 'active', name: 'J1 (axis on a GH ray)', c: W(V.scale(u[0], G.f[0])), axis: Wd(u[0]), r: rad, h: hub };
      const hK = { kind: 'hub', role: 'passive', name: 'K (O20, passive, slaved both ways by the desmodromic crank; no spring)', c: on(F.R1, V.scale(uK, G.fK)), axis: Wd(M.mulv(F.R1, uK)), r: rad, h: hub + (G.capK || 0) };
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
        { kind: 'hub', role: 'passive', name: 'V crank boss (MR63ZZ pair on an O3 pin in link 1b beside hub 2)', c: on(F.R1b, G.vrPV), axis: Wd(M.mulv(F.R1b, G.vrAx)), r: 5, h: 6 },
        { kind: 'link', role: 'link', name: 'V short arm A (3 mm Ti) -> pin A (opening lobe)', a: on(F.R1b, G.vrPV), b: on(F.R1b, G.pinA), r: 1.5 },
        { kind: 'link', role: 'link', name: 'V short arm B (3 mm Ti) -> pin B (closing lobe, one track lower)', a: on(F.R1b, G.vrPV), b: on(F.R1b, G.pinB), r: 1.5 },
        { kind: 'hub', role: 'passive', name: 'pin A (ISO 8734 O2.5, crowned) on lobe track A', c: on(F.R1b, G.pinA), axis: Wd(M.mulv(F.R1b, G.vrAx)), r: 1.25, h: 3 },
        { kind: 'hub', role: 'passive', name: 'pin B (ISO 8734 O2.5, crowned) on lobe track B', c: on(F.R1b, G.pinB), axis: Wd(M.mulv(F.R1b, G.vrAx)), r: 1.25, h: 3 },
        { kind: 'hub', role: 'link', name: 'two stacked conjugate lobe tracks (1.5 mm each) on hub 2\'s cap ring (link 2)', c: on(F.R12, G.track), axis: Wd(M.mulv(F.R12, u[1])), r: 9.1, h: 3 },
        { kind: 'link', role: 'link', name: 'V crank long arm (3 mm Ti) with the swept slot at its tip', a: on(F.R1b, G.vrPV), b: on(F.R1, G.nose), r: 1.5 },
        { kind: 'link', role: 'link', name: 'nose boss arm of link 1a (O5 boss)', a: on(F.R1, G.noseRoot), b: on(F.R1, G.nose), r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'nose dowel (ISO 8734 O2.5) in the crank slot', c: on(F.R1, G.nose), axis: Wd(M.mulv(F.R1, uK)), r: 1.25, h: 4 },
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
