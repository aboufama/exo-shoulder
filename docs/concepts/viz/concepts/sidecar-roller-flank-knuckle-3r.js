/* sidecar-roller-flank-knuckle-3r at its best measured configuration: the lead's slaved knuckle (pin knee, link 1 split by a
 * passive O20 knuckle K SLAVED to q2 past the onset) with a RODLESS sidecar drive. The hub-2 rim lobe pushes the short arm
 * of a bell crank (MR63ZZ pair, pin in link 1b, boss stacked on link 1b); its BENT long arm (straight run, then an arc
 * concentric with hub K at r_c 15.67 mm) carries an MR63ZZ roller that pushes a conjugate flank cut in a lateral horn lug
 * of link 1a (azimuth -174.72 deg). Law: crank angle = sig (|dK| / g)(1 + c |dK|), g 2.282, c 0.021; the flank works to dK 56.2 deg
 * (law beyond). J1, J2, J3 encoders give the pose (3 active, K never read, 0 passive translations).
 * Best: CMA P1 (near-touch objective, 6702 farm tries); frozen exact Bench(110,360) plain 20.08 / near-touch 21.17: fast Bench(60,160) near-touch 11.73, plain 11.73.
 * Geometry exported from docs/concepts/models/sidecar-roller-flank-knuckle-3r.py (mode viz). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 95.3929, "el1": 67.8974, "az2": 44.0485, "el2": 41.9575, "wd": 66.8053, "wa": -11.4207, "b3": 0.3621, "lE": 67.832, "lc": 20.7075, "phiE": -2.7863, "phib": -66.0451, "stk": 4.8534, "ang_min": 26.5397, "bk1": 27.7251, "bk2": 35.7114, "sK": -1, "a1max": 56.5633, "smhi": 19.4644, "smlo": 5.0, "capK": 6.0, "law_mode": "seg", "kA": 2.5246, "t1": 6.0, "kB": 2.5246, "smt": 12.0, "kK": 2.5246, "i_rock": 2.1999169583668636, "r_horn": 4.4442, "r_lobe": 8.1395, "arm_lo": 1.0, "g": 2.2817, "r_c": 15.6711, "beta": -174.7209, "lift": 1.414, "hl": 1.3491, "zr": 3.0123, "s_arm": 4.4442};
  const G = {"u": [[0.03536, 0.92651, 0.3746], [-0.47856, 0.62692, 0.61477], [-0.14361, -0.20293, 0.9686]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-1.19384, -14.97702, -3.31485]], "uK": [-0.35468, 0.93002, 0.09626], "sa": [0.02976, -0.97919, -0.20074], "st": [0.98919, 0.0, 0.14667], "sn": [-0.14361, -0.20293, 0.9686], "A": [37.418, 57.522], "branch": -1.0, "m": [-12.88622, 1.64241, 0.0], "f": [49.64, 61.45, 79.52], "fK": 55.75, "capK": 6.0, "tr": 87.35, "tp": 2.177, "RUN": 0.5, "A0": [-2.43906, -81.3191, -17.3988], "A0m": [-1.19794, -68.701, -14.57117], "Bm": [-19.66693, -76.93367, -19.03436], "eE": [-0.01836, -0.97804, -0.20763], "psiA": -73.8621, "thLo": 25.104, "thHi": 75.4755, "q2s": [99.2184, 10.0132], "lawTh": [75.475, 76.679, 77.905, 79.15, 80.413, 81.691, 82.982, 84.284, 85.596, 86.914, 88.238, 89.564, 90.892, 92.218, 93.541, 94.859, 96.169, 97.469, 98.758, 100.033, 101.292, 102.531, 103.75, 104.946, 106.116, 107.257, 108.368], "lawDK": [-0.0, -2.02, -4.039, -6.059, -8.079, -10.098, -12.118, -14.138, -16.157, -18.177, -20.197, -22.216, -24.236, -26.256, -28.276, -30.295, -32.315, -34.335, -36.354, -38.374, -40.394, -42.413, -44.433, -46.453, -48.472, -50.492, -52.512], "lawQ2": [10.013, 9.213, 8.413, 7.613, 6.813, 6.013, 5.213, 4.413, 3.613, 2.813, 2.013, 1.213, 0.413, -0.387, -1.187, -1.987, -2.787, -3.587, -4.387, -5.187, -5.987, -6.787, -7.587, -8.387, -9.187, -9.987, -10.787], "emb": "rod", "rocker": [-27.843, 49.247, 25.905], "rockerAx": [-0.44748, 0.79147, 0.41633], "rodA": [-17.455, 58.818, -9.119], "rodB": [-17.455, 58.818, -9.119], "armA": [-27.843, 49.247, 25.905], "armB": [-35.206, 51.696, 11.954], "L1a": [[-6.22, 52.0, 11.23], [-9.73, 54.96, 12.34], [-9.61, 50.22, 15.96]], "L1b": [[-27.29, 51.38, 14.94], [-27.05, 45.81, 19.16], [-29.44, 44.71, 25.14], [-24.48, 48.14, 16.52], [-25.62, 45.17, 21.43], [-29.65, 46.75, 29.19], [-22.6, 46.52, 18.42], [-24.15, 44.44, 23.63], [-21.91, 53.19, 17.28], [-21.15, 45.71, 20.55], [-24.14, 46.5, 27.45]], "L2": [[-32.97, 32.49, 46.28], [-31.21, 23.32, 52.35], [-30.5, 14.37, 60.53], [-28.22, 3.69, 66.48], [-24.33, -7.91, 69.14], [-20.91, -21.04, 74.31], [-29.35, 26.29, 49.47], [-28.83, 18.03, 57.78], [-26.96, 8.01, 64.37], [-23.61, -3.2, 68.21], [-18.95, -14.64, 68.64], [-28.03, 29.58, 47.51], [-27.54, 21.7, 55.77], [-25.69, 12.08, 62.18], [-22.7, 1.34, 66.68], [-18.24, -9.79, 67.33], [-28.14, 34.52, 47.96], [-26.22, 25.18, 53.67], [-24.98, 16.26, 61.32], [-22.07, 5.73, 65.93], [-17.95, -5.33, 67.51], [-14.87, -18.39, 75.73]], "armPts": [[-28.514, 50.434, 26.529], [-28.266, 48.518, 23.392], [-29.45, 49.118, 21.555], [-30.422, 49.362, 19.556], [-31.239, 49.364, 17.479], [-32.232, 49.656, 15.521], [-34.959, 52.556, 14.276], [-36.035, 52.914, 12.236], [-36.725, 52.85, 10.309], [-37.181, 52.883, 8.313], [-37.397, 53.011, 6.281], [-37.369, 53.232, 4.246], [-37.098, 53.543, 2.241], [-36.587, 53.939, 0.298], [-35.846, 54.413, -1.551], [-34.887, 54.957, -3.276], [-33.724, 55.564, -4.848], [-32.377, 56.222, -6.243], [-30.868, 56.921, -7.437], [-29.222, 57.649, -8.412], [-27.464, 58.396, -9.15], [-25.625, 59.149, -9.641], [-23.733, 59.895, -9.877], [-21.819, 60.622, -9.852], [-19.915, 61.319, -9.569], [-18.48, 61.825, -9.178]], "lugPts": [[-20.033, 55.864, -5.017], [-22.859, 56.691, -10.539], [-21.898, 56.636, -12.659], [-20.718, 56.698, -14.266], [-19.374, 56.816, -15.621], [-17.898, 56.97, -16.778], [-16.354, 57.144, -17.736], [-16.018, 57.182, -17.917]], "roller": [-17.455, 58.818, -9.119], "rollerAx": [-0.28141, 0.94826, -0.14701], "sig": 1.0, "g": 2.2817, "cprog": 0.0213, "dKlim": 56.2};
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
