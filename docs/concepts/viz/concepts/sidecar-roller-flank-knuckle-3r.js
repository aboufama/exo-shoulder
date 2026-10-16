/* sidecar-roller-flank-knuckle-3r at its best measured configuration: the lead's slaved knuckle (pin knee, link 1 split by a
 * passive O20 knuckle K SLAVED to q2 past the onset) with a RODLESS sidecar drive. The hub-2 rim lobe pushes the short arm
 * of a bell crank (MR63ZZ pair, pin in link 1b, boss stacked on link 1b); its BENT long arm (straight run, then an arc
 * concentric with hub K at r_c 16.0 mm) carries an MR63ZZ roller that pushes a conjugate flank cut in a lateral horn lug
 * of link 1a (azimuth -170.0 deg). Law: crank angle = sig |dK| / g, g 2.3; the flank works to dK 56.0 deg
 * (pressure_horn beyond). J1, J2, J3 encoders give the pose (3 active, K never read, 0 passive translations).
 * hand pick: fast Bench(60,160) near-touch 32.1, plain 32.1.
 * Geometry exported from docs/concepts/models/sidecar-roller-flank-knuckle-3r.py (mode viz). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 95.3594, "el1": 67.6187, "az2": 42.7487, "el2": 43.9031, "wd": 63.5262, "wa": -10.5604, "b3": 0.3825, "lE": 67.832, "lc": 25.8149, "phiE": -2.7863, "phib": -65.6717, "stk": 4.8534, "ang_min": 27.8606, "bk1": 30.05, "bk2": 37.57, "sK": -1, "a1max": 61.72, "smhi": 14.7672, "smlo": 5.1723, "capK": 6.0, "law_mode": "seg", "kA": 2.0, "t1": 6.0, "kB": 2.0, "smt": 12.0, "kK": 2.0, "i_rock": 2.3, "r_horn": 5.0, "r_lobe": 7.5, "arm_lo": 1.0};
  const G = {"u": [[0.03556, 0.92467, 0.3791], [-0.48034, 0.65119, 0.58756], [-0.11461, -0.2375, 0.9646]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-1.9766, -17.1149, -4.44881]], "uK": [-0.34493, 0.93824, 0.02716], "sa": [0.02802, -0.97139, -0.23584], "st": [0.99302, 0.0, 0.11798], "sn": [-0.11461, -0.2375, 0.9646], "A": [36.119, 62.15], "branch": -1.0, "m": [-14.16462, 2.46517, 0.0], "f": [49.74, 60.06, 80.9], "fK": 56.16, "capK": 6.0, "tr": 89.06, "tp": 2.177, "RUN": 0.5, "A0": [-3.35245, -82.92815, -20.81657], "A0m": [-1.3014, -69.16882, -17.1851], "Bm": [-24.36164, -79.49935, -22.46854], "eE": [-0.02028, -0.97024, -0.2413], "psiA": -66.5052, "thLo": 31.2038, "thHi": 83.5019, "q2s": [93.3473, -3.6121], "lawTh": [83.502, 84.554, 85.62, 86.7, 87.793, 88.896, 90.009, 91.13, 92.258, 93.391, 94.529, 95.669, 96.811, 97.953, 99.094, 100.231, 101.365, 102.493, 103.613, 104.725, 105.826, 106.916, 107.992, 109.053, 110.096, 111.121, 112.126, 113.108, 114.065, 114.996, 115.899, 116.772, 117.612, 118.418, 119.187, 119.917, 120.607, 121.254, 121.856, 122.411, 122.917, 123.373], "lawDK": [-0.0, -1.6, -3.2, -4.8, -6.4, -8.0, -9.6, -11.2, -12.8, -14.4, -16.0, -17.6, -19.2, -20.8, -22.4, -24.0, -25.6, -27.2, -28.8, -30.4, -32.0, -33.6, -35.2, -36.8, -38.4, -40.0, -41.6, -43.2, -44.8, -46.4, -48.0, -49.6, -51.2, -52.8, -54.4, -56.0, -57.6, -59.2, -60.8, -62.4, -64.0, -65.6], "lawQ2": [-3.612, -4.412, -5.212, -6.012, -6.812, -7.612, -8.412, -9.212, -10.012, -10.812, -11.612, -12.412, -13.212, -14.012, -14.812, -15.612, -16.412, -17.212, -18.012, -18.812, -19.612, -20.412, -21.212, -22.012, -22.812, -23.612, -24.412, -25.212, -26.012, -26.812, -27.612, -28.412, -29.212, -30.012, -30.812, -31.612, -32.412, -33.212, -34.012, -34.812, -35.612, -36.412], "emb": "rod", "rocker": [-27.257, 49.315, 22.97], "rockerAx": [-0.44795, 0.81046, 0.3775], "rodA": [-19.093, 61.395, -13.925], "rodB": [-19.093, 61.395, -13.925], "armA": [-27.257, 49.315, 22.97], "armB": [-36.465, 56.189, 7.795], "L1a": [[-3.19, 49.26, 11.35], [-8.13, 52.32, 7.63], [-7.96, 52.22, 10.61], [-9.3, 51.69, 12.05], [-8.29, 46.79, 13.7], [-14.63, 54.16, 11.12]], "L1b": [[-27.05, 52.95, 11.03], [-26.56, 47.01, 15.44], [-28.12, 44.95, 20.74], [-25.23, 53.6, 11.8], [-24.65, 47.19, 16.01], [-26.2, 45.21, 21.3], [-23.42, 54.24, 12.57], [-22.74, 47.3, 16.55], [-24.16, 45.18, 21.71], [-21.6, 54.89, 13.35], [-20.74, 47.11, 16.97], [-22.12, 45.03, 22.06]], "L2": [[-32.63, 33.63, 43.64], [-31.03, 24.78, 49.52], [-30.98, 16.61, 58.25], [-29.56, 6.52, 65.44], [-26.63, -4.98, 70.17], [-21.92, -16.79, 70.62], [-31.06, 34.28, 44.21], [-29.21, 25.2, 49.63], [-28.93, 17.07, 58.08], [-27.37, 7.15, 65.07], [-24.34, -4.14, 69.55], [-19.63, -15.67, 69.74], [-29.49, 34.93, 44.77], [-27.72, 25.89, 50.27], [-26.9, 17.51, 57.84], [-25.19, 7.73, 64.57], [-22.16, -3.33, 69.05], [-17.39, -14.57, 68.76], [-27.91, 35.58, 45.33], [-26.21, 26.57, 50.91], [-24.9, 17.91, 57.57], [-23.07, 8.3, 64.03], [-19.84, -2.52, 67.86], [-15.27, -13.52, 67.86]], "armPts": [[-27.929, 50.53, 23.536], [-28.053, 49.678, 21.114], [-28.926, 50.188, 19.346], [-29.643, 50.444, 17.508], [-30.183, 50.422, 15.622], [-30.666, 50.332, 13.773], [-31.825, 51.363, 12.249], [-32.371, 51.408, 10.503], [-34.805, 54.428, 9.311], [-37.276, 57.438, 7.968], [-37.903, 57.264, 6.03], [-38.299, 57.176, 4.026], [-38.458, 57.177, 1.987], [-38.377, 57.266, -0.054], [-38.057, 57.442, -2.066], [-37.505, 57.701, -4.017], [-36.727, 58.041, -5.877], [-35.737, 58.455, -7.617], [-34.549, 58.938, -9.21], [-33.183, 59.482, -10.631], [-31.659, 60.077, -11.857], [-30.002, 60.716, -12.87], [-28.237, 61.387, -13.654], [-26.392, 62.081, -14.197], [-24.495, 62.787, -14.489], [-22.577, 63.493, -14.527], [-20.667, 64.189, -14.31], [-20.114, 64.389, -14.199]], "lugPts": [[-20.847, 57.389, -9.104], [-24.685, 59.633, -12.74], [-24.539, 59.102, -15.251], [-23.785, 58.84, -17.318], [-22.722, 58.723, -19.055], [-21.467, 58.694, -20.542], [-20.113, 58.723, -21.791], [-18.638, 58.795, -22.881], [-17.219, 58.889, -23.735]], "roller": [-19.093, 61.395, -13.925], "rollerAx": [-0.29023, 0.93325, -0.21167], "sig": 1.0, "g": 2.3, "dKlim": 56.0};
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
    if (Math.abs(k.dK) > G.dKlim + 1e-6) return `past the flank's working range (|dK| ${Math.abs(k.dK).toFixed(1)} > ${G.dKlim} deg): stop B`;
    const F = fk(q), sv = M.mulv(M.T(Q), F.t3), kn = knee([V.dot(sv, sa), V.dot(sv, st)]);
    if (!kn.span) return 'knee span: the drift is beyond lE + lc';
    if (kn.ang < P.ang_min || kn.ang > 180 - P.ang_min) return `knee angle ${kn.ang.toFixed(0)} deg outside [${P.ang_min}, ${180 - P.ang_min}]`;
    return null;
  };
  const closes = (q, ctx) => { const r = C.residual(q, ctx); return Math.max(...r.map(Math.abs)) <= 0.5; };
  const solveC = (ctx, qPrev) => { const q = solve(ctx); return (!qPrev || closes(q, ctx)) ? q : K.dls(C, ctx, qPrev, { iters: 40 }).q; };
  const C = {
    id: 'sidecar-roller-flank-knuckle-3r', name: 'Rodless sidecar: hub-2 lobe -> bell crank on link 1b -> bent arm + MR63 roller -> conjugate flank on link 1a horn slaves K to q2 (3 active, K not read)',
    dof: { active: 3, passive: 5 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'K (passive, slaved to q2 by the lobe - bell crank - roller - flank sidecar)', 'J2', 'J3', 'knee pin a', 'knee pin b'], qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve: solveC,
    residual: (q, ctx) => { const F = fk(q); return M.rotErrDeg(F.R5, Qof(ctx)).concat(F.t5); },
    check,
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), F = fk(q);
      const Rc = M.mul(F.R1b, M.rot(G.rockerAx, G.sig * Math.abs(q[1]) / G.g));
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
        { kind: 'hub', role: 'passive', name: 'bell crank boss (MR63ZZ pair, pin in link 1b beside hub 2; short arm rides the hub-2 rim lobe)', c: on(Rc, G.rocker), axis: Wd(M.mulv(Rc, G.rockerAx)), r: 5, h: 6 },
        { kind: 'arc', role: 'link', name: 'bell crank bent long arm (3 mm Ti: straight run, then an arc concentric with hub K)', pts: G.armPts.map(p => on(Rc, p)), r: 1.5 },
        { kind: 'hub', role: 'passive', name: 'MR63ZZ roller (O6 x 2.5, radial axis) on the arm tip', c: on(Rc, G.roller), axis: Wd(M.mulv(Rc, G.rollerAx)), r: 3, h: 2.5 },
        { kind: 'arc', role: 'link', name: 'horn lug of link 1a with the conjugate flank (wire-EDM)', pts: G.lugPts.map(p => on(F.R1, p)), r: 1.5 },
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
