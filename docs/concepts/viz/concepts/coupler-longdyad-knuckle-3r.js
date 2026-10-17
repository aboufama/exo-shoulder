/* coupler-longdyad-knuckle-3r at its CMA best (Bench(60,160) fast plain gap 19.66, objective 24.46; spec side, arm swung back to t1 +25): the slipper-nose lead's chain (seats, pin knee, b3 tilt) on a long K dyad
 * (bk1 32 / bk2 48, stop B a1max 74.5); link 1 split by a passive O20 knuckle K SLAVED to q2 by a TWO-STAGE drive: past the onset
 * link 2's hub-2 rim lobe pushes an O2.5 DLC dowel nose on the short lug of a bell crank (2 x 683ZZ, axis dR on link 1b beside
 * hub 2, through GH); the crank's long Ti arm swings sideways and a spherical Ti coupler (O8 eyes on MR63ZZ, radial pins through
 * GH) runs to a horn lug of link 1a at hub K. Spherical 4R, PA <= 42; drive range dK_lim 60.25 deg. 3 active, K never read, 0 passive
 * translations. Geometry from docs/concepts/models/coupler-longdyad-knuckle-3r.py (mode viz). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 95.3929, "el1": 67.8974, "az2": 45.8211, "el2": 41.0855, "wd": 66.8662, "wa": -10.6559, "b3": 0.329, "lE": 67.832, "lc": 21.1499, "phiE": -2.7863, "phib": -58.8084, "stk": 4.8534, "ang_min": 25.2189, "bk1": 32.0, "bk2": 48.0, "a1max": 74.5, "smhi": 12.8342, "smlo": 5.0, "capK": 6.0, "kK": 3.3021, "cr_tilt": 16.3689, "cr_a1": 33.2904, "cr_t1": 24.8213, "cr_a3": 14.0484, "cr_t3": -157.4569, "cr_zr": 8.0, "s_nose": 3.6903, "r_base": 11.2, "dr_hl": 6.5965, "dl_a": 1, "dl_h": 1, "dl_lift": 0.0};
  const G = {"u": [[0.03536, 0.92651, 0.3746], [-0.46545, 0.61682, 0.63474], [-0.13912, -0.22062, 0.96539]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-0.73949, -13.44608, -3.17939]], "uK": [-0.27616, 0.95785, -0.07913], "sa": [0.03147, -0.97536, -0.21836], "st": [0.98978, 0.0, 0.14263], "sn": [-0.13912, -0.22062, 0.96539], "A": [37.552, 57.218], "branch": -1.0, "m": [-11.73931, 1.18257, 0.0], "f": [50.45, 61.97, 80.06], "fK": 57.33, "capK": 6.0, "tr": 87.71, "tp": 2.177, "RUN": 0.5, "A0": [-1.8712, -79.52847, -18.44428], "A0m": [-1.07012, -68.07842, -15.71217], "Bm": [-18.63294, -78.76209, -20.68457], "eE": [-0.01668, -0.97421, -0.22504], "psiA": -55.0939, "thLo": 24.6667, "thHi": 81.9359, "q2s": [102.0679, -1.6132], "lawTh": [81.936, 83.294, 84.707, 86.169, 87.677, 89.227, 90.814, 92.436, 94.088, 95.766, 97.467, 99.186, 100.919, 102.663, 104.414, 106.167, 107.919, 109.664, 111.399, 113.119, 114.818, 116.492, 118.135], "lawDK": [-0.0, -2.642, -5.283, -7.925, -10.567, -13.208, -15.85, -18.492, -21.133, -23.775, -26.417, -29.058, -31.7, -34.342, -36.984, -39.625, -42.267, -44.909, -47.55, -50.192, -52.834, -55.475, -58.117], "lawQ2": [-1.613, -2.413, -3.213, -4.013, -4.813, -5.613, -6.413, -7.213, -8.013, -8.813, -9.613, -10.413, -11.213, -12.013, -12.813, -13.613, -14.413, -15.213, -16.013, -16.813, -17.613, -18.413, -19.213], "emb": "rod", "dogK": [0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 22.0, 24.0, 26.0, 28.0, 30.0, 32.0, 34.0, 36.0, 38.0, 40.0, 42.0, 44.0, 46.0, 48.0, 50.0, 52.0, 54.0, 56.0, 58.0, 60.0], "dogPhi": [-0.0, 0.929, 1.871, 2.823, 3.784, 4.753, 5.727, 6.705, 7.686, 8.668, 9.649, 10.629, 11.605, 12.576, 13.541, 14.498, 15.446, 16.384, 17.31, 18.223, 19.122, 20.005, 20.87, 21.718, 22.545, 23.352, 24.136, 24.895, 25.63, 26.337, 27.015], "dKlim": 60.25, "crankAx": [-0.4332, 0.79854, 0.41794], "boss": [-26.232, 48.354, 25.307], "armA": [-26.232, 48.354, 25.307], "armB": [-33.247, 60.252, -10.387], "rodA": [-34.752, 62.979, -10.858], "rodB": [-17.807, 61.03, -21.378], "horn": [-16.971, 58.164, -20.374], "hornRoot": [-17.549, 60.394, -15.525], "L1a": [[-1.93, 50.69, 9.48], [-5.55, 54.65, 5.1], [-4.39, 48.37, 8.58], [-8.89, 57.68, 4.79], [-7.24, 50.39, 8.45], [-6.61, 49.6, 12.62], [-10.55, 53.48, 8.45]], "L1b": [[-23.69, 56.68, 4.5], [-22.81, 49.17, 9.08], [-24.5, 47.69, 14.17], [-26.15, 45.98, 19.32], [-27.69, 43.85, 24.49], [-21.87, 57.27, 5.27], [-20.98, 49.21, 9.67], [-22.75, 47.99, 14.79], [-24.49, 46.52, 20.02], [-26.03, 44.45, 25.23], [-20.05, 57.86, 6.03], [-19.17, 49.22, 10.24], [-21.06, 48.38, 15.43], [-22.78, 46.97, 20.68], [-24.35, 45.03, 25.97], [-18.23, 58.44, 6.79], [-17.47, 49.44, 10.84], [-19.33, 48.66, 16.03], [-21.08, 47.42, 21.34], [-22.64, 45.56, 26.66]], "L2": [[-32.25, 32.11, 47.74], [-29.74, 22.43, 52.41], [-28.4, 13.43, 59.13], [-25.66, 3.17, 63.39], [-22.03, -7.65, 65.68], [-20.05, -21.16, 74.92], [-28.46, 25.81, 50.51], [-27.84, 17.57, 58.65], [-25.43, 7.49, 63.81], [-21.69, -3.32, 65.92], [-18.14, -14.83, 69.33], [-27.22, 29.12, 48.68], [-26.6, 21.23, 56.74], [-24.84, 11.74, 63.32], [-21.56, 1.02, 66.79], [-17.22, -9.9, 67.24], [-27.37, 34.12, 49.36], [-25.3, 24.69, 54.66], [-24.0, 15.83, 62.2], [-21.31, 5.43, 67.33], [-17.31, -5.67, 69.11], [-14.01, -18.58, 76.35]]};
  const u = G.u, c = G.c, uK = G.uK, sn = G.sn, sa = G.sa, st = G.st, a1 = G.A[0], a2 = G.A[1], hub = 12.25, rad = 10;
  const wrapR = a => { a = (a + Math.PI) % (2 * Math.PI); return (a < 0 ? a + 2 * Math.PI : a) - Math.PI; };
  const pe = P.phiE * D2R, pb = P.phib * D2R, lE = P.lE, lc = P.lc;
  const A02 = [G.m[0] + lE * Math.cos(pe), G.m[1] + lE * Math.sin(pe)], B2 = [A02[0] + lc * Math.cos(pb), A02[1] + lc * Math.sin(pb)];
  const kbr = Math.sign(wrapR(pe - Math.atan2(B2[1] - G.m[1], B2[0] - G.m[0]))) || 1;
  const vref = V.unit(V.cross(u[2], [0.3, 0.5, 0.8]));
  const cb = x => Math.cos(x * D2R), sb = x => Math.sin(x * D2R);
  /** physical J2 stop: th (deg) inside [thLo, thHi] -> K on stop A (state 0); else J2 locked on its q2 stop, K opens */
  const dot = V.dot;
  const phiOf = dK => { const k = Math.abs(dK), X = G.dogK, Y = G.dogPhi, n = X.length; if (k <= X[0]) return 0; let j = 0;
    while (j < n - 2 && X[j + 1] < k) j++; const a = Math.max(0, Math.min(1, (k - X[j]) / Math.max(X[j + 1] - X[j], 1e-9))); return Y[j] + a * (Y[j + 1] - Y[j]); };
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
    return { q1, dK, q2: q2s, ok: ok && Math.abs(dK) <= G.dKlim, L: { state } };
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
    if (!k.ok) return k.L.state === 1 ? 'past the drive stop B (drive range dK_lim / pressure angle / lift-off)' : (k.L.state === -1 ? 'folded side: J2 on its dowel (lobe dwell)' : 'chain cannot close');
    const F = fk(q), sv = M.mulv(M.T(Q), F.t3), kn = knee([V.dot(sv, sa), V.dot(sv, st)]);
    if (!kn.span) return 'knee span: the drift is beyond lE + lc';
    if (kn.ang < P.ang_min || kn.ang > 180 - P.ang_min) return `knee angle ${kn.ang.toFixed(0)} deg outside [${P.ang_min}, ${180 - P.ang_min}]`;
    return null;
  };
  const closes = (q, ctx) => { const r = C.residual(q, ctx); return Math.max(...r.map(Math.abs)) <= 0.5; };
  const solveC = (ctx, qPrev) => { const q = solve(ctx); return (!qPrev || closes(q, ctx)) ? q : K.dls(C, ctx, qPrev, { iters: 40 }).q; };
  const C = {
    id: 'coupler-longdyad-knuckle-3r', name: 'Spherical-coupler knuckle: hub-2 lobe -> O2.5 nose -> bell crank on dR -> spherical coupler -> horn of link 1a on hub K (3 active, K not read)',
    dof: { active: 3, passive: 6 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'K (passive, slaved to q2 by lobe - nose - crank - coupler - horn)', 'J2', 'J3', 'knee pin a', 'knee pin b'], qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve: solveC,
    residual: (q, ctx) => { const F = fk(q); return M.rotErrDeg(F.R5, Qof(ctx)).concat(F.t5); },
    check,
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), F = fk(q);
      const on = (R, p) => W(M.mulv(R, p)), I = M.I3();
      const h1 = { kind: 'hub', role: 'active', name: 'J1 (axis on a GH ray)', c: W(V.scale(u[0], G.f[0])), axis: Wd(u[0]), r: rad, h: hub };
      const hK = { kind: 'hub', role: 'passive', name: 'K (O20, passive, slaved; clock-spring cap, stop A; the horn is a lateral lug of link 1a)', c: on(F.R1, V.scale(uK, G.fK)), axis: Wd(M.mulv(F.R1, uK)), r: rad, h: hub + (G.capK || 0) };
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
        { kind: 'hub', role: 'passive', name: 'bell crank boss (O10 x 6 on 2 x 683ZZ, axis dR through GH, stacked on link 1b; O2.5 DLC nose on the hub-2 lobe)', c: on(F.R1b, G.boss), axis: Wd(M.mulv(F.R1b, G.crankAx)), r: 5, h: 6 },
        { kind: 'link', role: 'link', name: 'crank long arm (6 x 3 Ti, turns about dR by phi(K))', a: on(F.R1b, M.mulv(M.rot(G.crankAx, phiOf(q[1])), G.armA)), b: on(F.R1b, M.mulv(M.rot(G.crankAx, phiOf(q[1])), G.armB)), r: 1.5 },
        { kind: 'link', role: 'link', name: 'spherical coupler (6 x 3 Ti, O8 eyes on MR63ZZ, radial pins through GH)', a: on(F.R1b, M.mulv(M.rot(G.crankAx, phiOf(q[1])), G.rodA)), b: on(F.R1, G.rodB), r: 1.5 },
        { kind: 'link', role: 'link', name: 'horn lug of link 1a at hub K', a: on(F.R1, G.hornRoot), b: on(F.R1, G.horn), r: 1.5 },
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
