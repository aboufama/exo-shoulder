/* inband-rssr-knuckle-3r at its claimed configuration: the long-stroke row's chain (slipper-nose's seats, pin knee, link 1 split by a
 * passive O20 knuckle K SLAVED to q2; K sub-dyad bk1 26.00 / bk2 38.00, stop B 59.00) and its phased RSSR K drive on the
 * steep lobe law (kK 1.79), REPACKAGED in the band: the bell crank (MR63ZZ pair, long arm La 19.5, phase gam 7.7) sits
 * on an EAR of link 1b joggled one layer down, so it runs in link 1b's own layer; crank-tip M2 ball on a radial stud in the arm's end face (rod in the arm's mid-plane); O3 rod to the horn lug of link 1a at hub K (r_h 14.6, beta -140.4).
 * Every pressure angle <= 42 deg (transmission >= 48 at both ball ends). Pick (leak-free cma3 p, fit-bench 2 mm objective 16.47); frozen / held claim in docs/research/inband_drive.md.
 * Geometry exported from docs/concepts/models/inband-rssr-knuckle-3r.py (mode viz). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"La": 19.5042, "s_arm": 4.0515, "r_h": 14.6248, "beta": -140.3863, "gam": 7.7146, "hl": 3.15, "zr": 0.0, "kK": 1.7901, "r_lobe": 7.0, "bk1": 26.0, "bk2": 38.0, "a1max": 59.0, "smhi": 19.0991, "eta": -12.4092, "clay": 1, "zc": 0.8032, "bl_c": 2, "bl_h": 0, "az1": 95.3929, "el1": 67.8974, "az2": 45.8211, "el2": 41.0855, "wd": 66.8662, "wa": -10.6559, "b3": 0.329, "lE": 67.832, "lc": 21.1499, "phiE": -2.7863, "phib": -58.8084, "stk": 4.8534, "ang_min": 25.2189, "sK": -1, "smlo": 5.0, "capK": 6.0, "law_mode": "seg", "kA": 1.7901, "t1": 6.0, "kB": 1.7901, "smt": 12.0, "i_rock": 4.814068863383932, "r_horn": 14.6248, "arm_lo": 1.0};
  const G = {"u": [[0.03536, 0.92651, 0.3746], [-0.46545, 0.61682, 0.63474], [-0.13912, -0.22062, 0.96539]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-0.73949, -13.44608, -3.17939]], "uK": [-0.31479, 0.94463, 0.09268], "sa": [0.03147, -0.97536, -0.21836], "st": [0.98978, 0.0, 0.14263], "sn": [-0.13912, -0.22062, 0.96539], "A": [37.552, 57.218], "branch": -1.0, "m": [-11.73927, 1.16861, 0.0], "f": [50.45, 62.08, 78.2], "fK": 55.12, "capK": 6.0, "tr": 88.63, "tp": 2.177, "RUN": 0.5, "A0": [-1.8712, -79.52847, -18.44428], "A0m": [-1.08394, -68.07846, -15.71417], "Bm": [-18.64676, -78.76213, -20.68657], "eE": [-0.01668, -0.97421, -0.22504], "psiA": -71.7443, "thLo": 24.6667, "thHi": 75.671, "q2s": [102.0679, 11.9395], "lawTh": [75.671, 76.569, 77.481, 78.404, 79.339, 80.285, 81.239, 82.203, 83.173, 84.151, 85.134, 86.122, 87.114, 88.109, 89.106, 90.104, 91.103, 92.1, 93.096, 94.09, 95.079, 96.065, 97.044, 98.017, 98.982, 99.939, 100.886, 101.822, 102.746, 103.657, 104.554, 105.436, 106.302, 107.15, 107.978, 108.787, 109.575, 110.34, 111.081, 111.798, 112.488, 113.15, 113.784, 114.387, 114.959], "lawDK": [-0.0, -1.432, -2.864, -4.296, -5.728, -7.16, -8.592, -10.025, -11.457, -12.889, -14.321, -15.753, -17.185, -18.617, -20.049, -21.481, -22.913, -24.345, -25.777, -27.21, -28.642, -30.074, -31.506, -32.938, -34.37, -35.802, -37.234, -38.666, -40.098, -41.53, -42.962, -44.394, -45.827, -47.259, -48.691, -50.123, -51.555, -52.987, -54.419, -55.851, -57.283, -58.715, -60.147, -61.579, -63.012], "lawQ2": [11.94, 11.14, 10.34, 9.54, 8.74, 7.94, 7.14, 6.34, 5.54, 4.74, 3.94, 3.14, 2.34, 1.54, 0.74, -0.06, -0.86, -1.66, -2.46, -3.26, -4.06, -4.86, -5.66, -6.46, -7.26, -8.06, -8.86, -9.66, -10.46, -11.26, -12.06, -12.86, -13.66, -14.46, -15.26, -16.06, -16.86, -17.66, -18.46, -19.26, -20.06, -20.86, -21.66, -22.46, -23.26], "emb": "rod", "rocker": [-23.073, 48.217, 28.53], "rockerAx": [-0.3808, 0.79579, 0.47087], "rodA": [-36.317, 51.985, 14.635], "rodB": [-26.226, 60.02, -7.365], "armA": [-23.073, 48.217, 28.53], "armB": [-34.032, 47.21, 11.81], "L1a": [[-3.92, 49.97, 11.46], [-7.46, 54.61, 12.77], [-9.32, 49.41, 14.75]], "L1b": [[-25.02, 51.92, 14.52], [-25.05, 46.25, 18.67], [-26.77, 43.9, 23.86], [-23.23, 52.44, 15.33], [-23.09, 46.18, 19.2], [-24.87, 44.04, 24.43], [-21.45, 52.95, 16.14], [-21.09, 45.89, 19.62], [-23.18, 44.53, 25.19], [-19.66, 53.47, 16.95], [-19.3, 45.99, 20.19], [-21.49, 45.03, 25.96]], "L2": [[-32.34, 31.95, 48.01], [-30.03, 22.16, 53.26], [-29.14, 12.96, 61.29], [-26.78, 2.06, 67.12], [-22.77, -9.72, 69.37], [-19.66, -23.7, 76.02], [-28.37, 24.08, 52.17], [-27.28, 15.1, 59.76], [-25.11, 4.63, 65.97], [-21.26, -6.86, 68.48], [-17.76, -19.81, 73.57], [-26.93, 26.14, 51.46], [-26.15, 17.59, 59.81], [-23.69, 7.16, 65.33], [-19.75, -4.09, 67.36], [-15.94, -16.17, 70.98], [-25.4, 28.06, 50.56], [-24.93, 20.02, 59.63], [-22.64, 9.77, 65.7], [-18.9, -1.5, 68.49], [-14.3, -12.88, 68.72]], "hornA": [-24.535, 60.215, -3.608], "hornB": [-26.226, 60.02, -7.365], "earA": [-22.445, 46.904, 27.753], "earB": [-23.674, 43.367, 30.289]};
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
    if (!k.ok) return k.L.state === 1 ? 'past the drive stop B (stop B / pressure angle / lift-off)' : (k.L.state === -1 ? 'folded side: J2 on its dowel (no tooth)' : 'chain cannot close');
    const F = fk(q), sv = M.mulv(M.T(Q), F.t3), kn = knee([V.dot(sv, sa), V.dot(sv, st)]);
    if (!kn.span) return 'knee span: the drift is beyond lE + lc';
    if (kn.ang < P.ang_min || kn.ang > 180 - P.ang_min) return `knee angle ${kn.ang.toFixed(0)} deg outside [${P.ang_min}, ${180 - P.ang_min}]`;
    return null;
  };
  const closes = (q, ctx) => { const r = C.residual(q, ctx); return Math.max(...r.map(Math.abs)) <= 0.5; };
  const solveC = (ctx, qPrev) => { const q = solve(ctx); return (!qPrev || closes(q, ctx)) ? q : K.dls(C, ctx, qPrev, { iters: 40 }).q; };
  const C = {
    id: 'inband-rssr-knuckle-3r', name: 'In-band RSSR knuckle: long K dyad, steep hub-2 lobe law, bell crank on a joggled ear in the layer of link 1b -> O3 rod -> horn of link 1a (3 active, K not read)',
    dof: { active: 3, passive: 3 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'K (passive, slaved to q2 by the lobe - bell crank - rod - horn sidecar)', 'J2', 'J3', 'knee pin a', 'knee pin b'], qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
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
        { kind: 'hub', role: 'passive', name: 'bell crank boss (MR63ZZ pair, pin in link 1b beside hub 2; short arm rides the hub-2 rim lobe)', c: on(F.R1b, G.rocker), axis: Wd(M.mulv(F.R1b, G.rockerAx)), r: 5, h: 6 },
        { kind: 'link', role: 'link', name: 'ear of link 1b (3 mm Ti tab, one layer down, carries the crank pin)', a: on(F.R1b, G.earB), b: on(F.R1b, G.earA), r: 2.5 },
        { kind: 'link', role: 'link', name: 'bell crank long arm (3 mm Ti, in link 1b\'s layer beside the strap)', a: on(F.R1b, G.armA), b: on(F.R1b, G.armB), r: 1.5 },
        { kind: 'link', role: 'link', name: 'horn lug of link 1a at hub K (strap level)', a: on(F.R1, G.hornA), b: on(F.R1, G.hornB), r: 1.5 },
        { kind: 'link', role: 'link', name: 'O3 Ti rod with M2 ball links (crank tip -> horn ball, beside link 1b)', a: on(F.R1b, G.rodA), b: on(F.R1, G.rodB), r: 1.5 },
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
