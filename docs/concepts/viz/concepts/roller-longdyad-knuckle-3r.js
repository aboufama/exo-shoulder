/* roller-longdyad-knuckle-3r at its best measured configuration: the lead's slaved knuckle (pin knee, link 1 split by a
 * passive O20 knuckle K SLAVED to q2 past the onset) on the LONGER K dyad (bk1 28.9414, bk2 46.0) with the rodless
 * roller-flank drive RE-CUT for a longer stroke: the hub-2 rim lobe pushes the short arm of a bell crank (MR63ZZ pair, pin in
 * link 1b); its bent long arm (straight run, then an arc concentric with hub K at r_c 19.5 mm) carries an MR63ZZ
 * roller that pushes a conjugate flank milled into a boss of link 1a (azimuth -165.0 deg). Law: crank angle =
 * sig |dK| / g, g 2.1; the flank works to dK 57.5 deg (pressure_horn beyond, both pressure angles <= 43).
 * J1, J2, J3 encoders give the pose (3 active, K never read, 0 passive translations).
 * Gate cell (not the claim): fast Bench(60,160) gap 200.25, near-touch 1 mm 200.25.
 * Geometry exported from docs/concepts/models/roller-longdyad-knuckle-3r.py (mode viz). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 96.6954, "el1": 67.5865, "az2": 42.2031, "el2": 44.4209, "wd": 67.5003, "wa": -7.3175, "b3": 0.345, "lE": 67.832, "lc": 25.6915, "phiE": -2.7863, "phib": -60.7036, "stk": 4.8534, "ang_min": 26.8823, "bk1": 28.9414, "bk2": 46.0, "sK": -1, "a1max": 69.9414, "smhi": 16.5464, "smlo": 5.0, "capK": 6.0, "law_mode": "seg", "kA": 2.4, "t1": 6.0, "kB": 2.4, "smt": 12.0, "kK": 2.4, "i_rock": 2.1, "r_horn": 4.3872, "r_lobe": 7.7447, "arm_lo": 1.0};
  const G = {"u": [[0.04445, 0.92446, 0.37869], [-0.4799, 0.65501, 0.58366], [-0.07591, -0.20566, 0.97567]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-1.54432, -13.6309, -2.99343]], "uK": [-0.18419, 0.98093, -0.06211], "sa": [0.01595, -0.97862, -0.20504], "st": [0.99699, 0.0, 0.07757], "sn": [-0.07591, -0.20566, 0.97567], "A": [36.369, 61.889], "branch": -1.0, "m": [-12.48281, 1.76235, 0.0], "f": [49.72, 60.34, 78.81], "fK": 55.18, "capK": 6.0, "tr": 85.25, "tp": 2.177, "RUN": 0.5, "A0": [-3.75088, -79.93436, -17.14129], "A0m": [-2.19298, -67.7184, -14.44506], "Bm": [-24.33047, -80.02121, -18.76081], "eE": [-0.03253, -0.97747, -0.20857], "psiA": -55.4709, "thLo": 30.5201, "thHi": 81.7112, "q2s": [90.0564, -3.8399], "lawTh": [81.711, 82.643, 83.61, 84.61, 85.642, 86.705, 87.795, 88.913, 90.055, 91.221, 92.408, 93.616, 94.841, 96.083, 97.34, 98.61, 99.891, 101.182, 102.48, 103.785, 105.093, 106.403, 107.714, 109.023, 110.328, 111.627, 112.918, 114.198, 115.466, 116.718, 117.953, 119.167, 120.358, 121.523, 122.659, 123.762, 124.829, 125.858, 126.844, 127.784, 128.675, 129.512, 130.292, 131.01], "lawDK": [-0.0, -1.92, -3.84, -5.76, -7.68, -9.6, -11.52, -13.44, -15.36, -17.28, -19.2, -21.12, -23.04, -24.96, -26.88, -28.8, -30.72, -32.64, -34.56, -36.48, -38.4, -40.32, -42.24, -44.16, -46.08, -48.0, -49.92, -51.84, -53.76, -55.68, -57.6, -59.52, -61.44, -63.36, -65.28, -67.2, -69.12, -71.04, -72.96, -74.88, -76.8, -78.72, -80.64, -82.56], "lawQ2": [-3.84, -4.64, -5.44, -6.24, -7.04, -7.84, -8.64, -9.44, -10.24, -11.04, -11.84, -12.64, -13.44, -14.24, -15.04, -15.84, -16.64, -17.44, -18.24, -19.04, -19.84, -20.64, -21.44, -22.24, -23.04, -23.84, -24.64, -25.44, -26.24, -27.04, -27.84, -28.64, -29.44, -30.24, -31.04, -31.84, -32.64, -33.44, -34.24, -35.04, -35.84, -36.64, -37.44, -38.24], "emb": "rod", "rocker": [-24.992, 50.36, 24.023], "rockerAx": [-0.40878, 0.82371, 0.39293], "rodA": [-6.033, 58.022, -22.56], "rodB": [-6.033, 58.022, -22.56], "armA": [-24.992, 50.36, 24.023], "armB": [-30.235, 56.625, -0.638], "L1a": [[-0.19, 50.2, 8.77], [-1.9, 49.94, 9.63], [-3.62, 49.67, 10.48], [-5.34, 49.4, 11.34]], "L1b": [[-18.92, 56.21, 4.75], [-19.73, 49.81, 9.23], [-22.44, 48.68, 14.29], [-25.14, 47.16, 19.48], [-29.25, 47.49, 26.04], [-17.18, 50.29, 8.45], [-19.84, 49.27, 13.47], [-22.53, 47.99, 18.64], [-25.26, 46.35, 24.01], [-15.37, 53.18, 8.05], [-17.23, 49.68, 12.62], [-19.94, 48.7, 17.8], [-22.48, 46.95, 22.98], [-13.66, 57.39, 7.76], [-14.63, 49.88, 11.74], [-17.32, 49.18, 16.89], [-19.92, 47.84, 22.14], [-23.8, 48.71, 29.15]], "L2": [[-32.12, 33.95, 44.27], [-29.31, 24.68, 49.88], [-27.84, 16.23, 57.93], [-24.74, 6.09, 63.37], [-20.63, -4.88, 66.72], [-16.6, -17.19, 71.84], [-28.17, 29.04, 46.03], [-26.68, 21.08, 53.66], [-24.43, 11.92, 60.58], [-20.86, 1.48, 65.13], [-16.16, -9.52, 66.76], [-28.91, 35.47, 45.2], [-26.11, 26.09, 50.66], [-24.26, 17.58, 58.22], [-21.35, 7.69, 64.37], [-16.96, -3.2, 67.03], [-12.75, -15.31, 72.49], [-25.39, 30.81, 47.43], [-23.59, 22.65, 54.77], [-21.51, 13.73, 62.68], [-17.83, 3.15, 67.54], [-12.88, -7.99, 68.7]], "armPts": [[-25.605, 51.595, 24.612], [-25.563, 51.15, 22.083], [-25.924, 51.519, 19.957], [-26.176, 51.675, 17.771], [-26.58, 52.135, 15.708], [-26.742, 52.123, 13.527], [-26.861, 52.033, 11.373], [-26.974, 51.941, 9.267], [-27.119, 51.917, 7.218], [-27.269, 51.908, 5.211], [-27.363, 51.798, 3.236], [-29.05, 54.694, 1.382], [-30.942, 57.948, -0.653], [-31.143, 57.782, -2.684], [-31.138, 57.654, -4.729], [-30.926, 57.564, -6.764], [-30.511, 57.515, -8.77], [-29.896, 57.507, -10.724], [-29.088, 57.54, -12.606], [-28.096, 57.613, -14.396], [-26.929, 57.725, -16.076], [-25.601, 57.876, -17.628], [-24.125, 58.065, -19.035], [-22.516, 58.288, -20.284], [-20.792, 58.543, -21.36], [-18.97, 58.829, -22.252], [-17.07, 59.141, -22.951], [-15.112, 59.477, -23.45], [-13.116, 59.834, -23.743], [-11.104, 60.206, -23.828], [-9.096, 60.591, -23.703], [-7.114, 60.984, -23.37], [-6.493, 61.11, -23.221]], "lugPts": [[-9.428, 56.455, -14.294], [-11.755, 57.788, -20.839], [-12.003, 56.898, -23.031], [-11.671, 56.123, -25.019], [-10.977, 55.447, -26.778], [-10.015, 54.828, -28.381], [-8.882, 54.273, -29.79], [-7.64, 53.772, -31.018], [-6.275, 53.299, -32.121], [-4.815, 52.853, -33.095], [-3.287, 52.433, -33.939], [-1.897, 52.082, -34.58]], "roller": [-6.033, 58.022, -22.56], "rollerAx": [-0.09646, 0.92768, -0.3607], "sig": 1.0, "g": 2.1, "cprog": 0.0, "dKlim": 57.5};
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
    id: 'roller-longdyad-knuckle-3r', name: 'Roller-flank knuckle on the long K dyad: re-cut flank (both pressure angles <= 43) on link 1a slaves K to q2 over a longer stroke (3 active, K not read)',
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
      const Rc = M.mul(F.R1b, M.rot(G.rockerAx, G.sig * (Math.abs(q[1]) / G.g) * (1 + (G.cprog || 0) * Math.abs(q[1]) * D2R)));
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
