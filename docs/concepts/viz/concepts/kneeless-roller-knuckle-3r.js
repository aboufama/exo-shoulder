/* kneeless-roller-knuckle-3r at its best measured configuration: the verified roller-flank knuckle (J1 acromion top, link 1a
 * with the conjugate flank lug, passive O20 knuckle K SLAVED to q2 by the hub-2 rim lobe -> bell crank (MR63ZZ pair on link
 * 1b) -> bent long arm -> MR63ZZ roller -> flank, link 1b, J2, link 2, J3) with J3's axis ON A GH RAY (b3 0): member 3 moves
 * with the arm, the drift is identically 0, so the two-pin knee carried nothing and is DELETED - hub 3's lower plate, the
 * E strap and the former knee link are ONE rigid Ti bracket bolted to the arm pad on BOTTOM. 3 active (J1, J2, J3 encoded),
 * K slaved and never read, 0 passive translations, 0 sensed passives.
 * Seed (b3 0, wd 75, wa -9; drive = the verified roller row): fast Bench(60,160) plain 15.81, 1 mm 19.03, 2 mm 45.89.
 * Geometry exported from docs/concepts/models/kneeless-roller-knuckle-3r.py (mode viz). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 95.3929, "el1": 67.8974, "az2": 44.0485, "el2": 41.9575, "wd": 75.0, "wa": -9.0, "b3": 0.0, "lE": 67.832, "lc": 20.7075, "phiE": -2.7863, "phib": -66.0451, "stk": 4.8534, "ang_min": 0.0, "bk1": 27.7251, "bk2": 35.7114, "sK": -1, "a1max": 56.5633, "smhi": 19.4644, "smlo": 5.0, "capK": 6.0, "law_mode": "seg", "kA": 2.5246, "t1": 6.0, "kB": 2.5246, "smt": 12.0, "kK": 2.5246, "i_rock": 2.2817, "r_horn": 4.4442, "r_lobe": 8.1395, "arm_lo": 1.0};
  const G = {"u": [[0.03536, 0.92651, 0.3746], [-0.48108, 0.62845, 0.61124], [-0.1511, -0.25882, 0.95403]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-0.0, 0.0, 0.0]], "uK": [-0.35271, 0.93105, 0.09353], "sa": [0.04049, -0.96593, -0.25563], "st": [0.98769, 0.0, 0.15643], "sn": [-0.1511, -0.25882, 0.95403], "A": [37.418, 60.45], "branch": -1.0, "m": [0.0, 0.0, 0.0], "f": [49.37, 61.34, 78.55], "fK": 55.35, "capK": 6.0, "tr": 91.82, "tp": 2.177, "RUN": 0.5, "A0": [-0.51363, -65.44322, -17.83539], "A0m": [-0.51363, -65.44322, -17.83539], "Bm": [-18.8641, -73.56434, -22.94499], "eE": [-0.00757, -0.96478, -0.26293], "psiA": -73.8621, "thLo": 28.0319, "thHi": 78.4034, "q2s": [100.1756, 10.7717], "lawTh": [78.403, 79.604, 80.827, 82.07, 83.332, 84.609, 85.901, 87.205, 88.519, 89.84, 91.168, 92.499, 93.832, 95.164, 96.494, 97.819, 99.137, 100.446, 101.744, 103.027, 104.295, 105.544, 106.772, 107.977, 109.155, 110.305, 111.423], "lawDK": [-0.0, -2.02, -4.039, -6.059, -8.079, -10.098, -12.118, -14.138, -16.157, -18.177, -20.197, -22.216, -24.236, -26.256, -28.276, -30.295, -32.315, -34.335, -36.354, -38.374, -40.394, -42.413, -44.433, -46.453, -48.472, -50.492, -52.512], "lawQ2": [10.772, 9.972, 9.172, 8.372, 7.572, 6.772, 5.972, 5.172, 4.372, 3.572, 2.772, 1.972, 1.172, 0.372, -0.428, -1.228, -2.028, -2.828, -3.628, -4.428, -5.228, -6.028, -6.828, -7.628, -8.428, -9.228, -10.028], "emb": "rod", "rocker": [-27.837, 49.273, 25.634], "rockerAx": [-0.44805, 0.7931, 0.41261], "rodA": [-17.082, 58.491, -9.293], "rodB": [-17.082, 58.491, -9.293], "armA": [-27.837, 49.273, 25.634], "armB": [-34.984, 51.428, 11.696], "L1a": [[-6.1, 51.64, 11.08], [-9.59, 54.59, 12.17], [-9.52, 49.87, 15.77]], "L1b": [[-27.07, 51.11, 14.63], [-26.95, 45.7, 18.88], [-29.45, 44.73, 24.88], [-24.3, 47.88, 16.22], [-25.61, 45.18, 21.21], [-29.68, 46.76, 28.92], [-22.58, 46.56, 18.24], [-24.11, 44.37, 23.38], [-21.72, 52.9, 17.0], [-21.09, 45.64, 20.34], [-24.15, 46.5, 27.23]], "L2": [[-32.44, 32.69, 46.36], [-29.82, 23.71, 52.39], [-28.25, 15.14, 60.65], [-25.17, 4.89, 66.66], [-21.52, -6.55, 72.43], [-28.63, 28.09, 48.36], [-27.14, 20.15, 56.33], [-24.73, 10.84, 63.4], [-20.88, 0.22, 67.73], [-29.2, 34.25, 47.3], [-25.98, 24.67, 52.06], [-24.08, 16.27, 59.73], [-20.85, 6.36, 65.25], [-17.77, -4.73, 73.52], [-25.54, 29.63, 49.32], [-23.28, 21.18, 55.83], [-20.52, 12.03, 61.98], [-17.13, 1.89, 67.82]], "armPts": [[-28.509, 50.463, 26.253], [-28.252, 48.54, 23.147], [-29.356, 49.017, 21.273], [-30.318, 49.251, 19.29], [-31.064, 49.149, 17.195], [-32.023, 49.394, 15.241], [-34.733, 52.278, 13.997], [-35.813, 52.646, 11.973], [-36.494, 52.582, 10.043], [-36.942, 52.614, 8.045], [-37.148, 52.74, 6.011], [-37.111, 52.958, 3.976], [-36.83, 53.266, 1.971], [-36.31, 53.658, 0.03], [-35.559, 54.128, -1.817], [-34.59, 54.668, -3.538], [-33.419, 55.269, -5.106], [-32.064, 55.922, -6.496], [-30.548, 56.616, -7.685], [-28.895, 57.34, -8.653], [-27.132, 58.081, -9.385], [-25.288, 58.828, -9.868], [-23.392, 59.569, -10.096], [-21.477, 60.292, -10.064], [-19.572, 60.984, -9.773], [-18.098, 61.501, -9.364]], "lugPts": [[-19.671, 55.554, -5.208], [-22.325, 56.35, -11.21], [-21.205, 56.345, -13.226], [-19.872, 56.45, -14.761], [-18.421, 56.605, -15.998], [-16.856, 56.792, -17.025], [-16.602, 56.824, -17.169]], "roller": [-17.082, 58.491, -9.293], "rollerAx": [-0.27713, 0.94893, -0.15077], "sig": 1.0, "g": 2.2817, "cprog": 0.0, "dKlim": 49.0};
  const u = G.u, c = G.c, uK = G.uK, sn = G.sn, a2 = G.A[1], hub = 12.25, rad = 10;
  const vref = V.unit(V.cross(u[2], [0.3, 0.5, 0.8]));
  const cb = x => Math.cos(x * D2R);
  const dot = V.dot;
  /** physical J2 stop: th (deg) inside [thLo, thHi] -> K on stop A (state 0); else J2 locked on its q2 stop, K opens */
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
    const T = G.lawTh, n = T.length; let j = 0;
    while (j < n - 2 && T[j + 1] < th) j++;
    const ok = th <= T[n - 1], a = Math.max(0, Math.min(1, (th - T[j]) / Math.max(T[j + 1] - T[j], 1e-9)));
    const q2s = G.lawQ2[j] + a * (G.lawQ2[j + 1] - G.lawQ2[j]), dK = G.lawDK[j] + a * (G.lawDK[j + 1] - G.lawDK[j]);
    const p = M.mulv(M.rot(u2, q2s), u3), q1 = K.axisAngle(u1, M.mulv(M.rot(uK, dK), p), w);
    return { q1, dK, q2: q2s, ok, L: { state } };
  }
  function chain(q1, dK, q2, q3) {
    const R1 = M.rot(u[0], q1), R1b = M.mul(R1, M.rot(uK, dK)), R12 = M.mul(R1b, M.rot(u[1], q2)), R3 = M.rot(u[2], q3), R123 = M.mul(R12, R3);
    const t3 = M.mulv(R12, V.sub(c[2], M.mulv(R3, c[2])));        // c3 = 0 (J3 on a GH ray): t3 = 0
    return { R1, R1b, R12, R123, t3 };
  }
  const Qof = ctx => M.mul(M.T(ctx.S), ctx.H);
  function solve(ctx) {
    const Q = Qof(ctx), k = ik(Q), R12 = M.mul(M.mul(M.rot(u[0], k.q1), M.rot(uK, k.dK)), M.rot(u[1], k.q2));
    const q3 = K.axisAngle(u[2], vref, M.mulv(M.T(R12), M.mulv(Q, vref)));
    return [k.q1, k.dK, k.q2, K.wrap180(q3)];
  }
  const fk = q => chain(q[0], q[1], q[2], q[3]);
  const check = (q, ctx) => {
    const k = ik(Qof(ctx));
    if (!k.ok) return k.L.state === 1 ? 'past the drive stop B (stop B / pressure angle / lift-off)' : (k.L.state === -1 ? 'folded side: J2 on its dowel' : 'chain cannot close');
    if (Math.abs(k.dK) > G.dKlim + 1e-6) return `past the flank's working range (|dK| ${Math.abs(k.dK).toFixed(1)} > ${G.dKlim} deg): stop B`;
    return null;
  };
  const closes = (q, ctx) => { const r = C.residual(q, ctx); return Math.max(...r.map(Math.abs)) <= 0.5; };
  const solveC = (ctx, qPrev) => { const q = solve(ctx); return (!qPrev || closes(q, ctx)) ? q : K.dls(C, ctx, qPrev, { iters: 40 }).q; };
  const C = {
    id: 'kneeless-roller-knuckle-3r', name: 'Knee-free roller-flank knuckle: J3 on a GH ray, the pin knee replaced by one rigid bracket (3 active, K slaved, not read)',
    dof: { active: 3, passive: 3 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'K (passive, slaved to q2 by the lobe - bell crank - roller - flank drive)', 'J2', 'J3'], qUnits: ['deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve: solveC,
    residual: (q, ctx) => { const F = fk(q); return M.rotErrDeg(F.R123, Qof(ctx)).concat(F.t3); },
    check,
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), F = fk(q);
      const Rc = M.mul(F.R1b, M.rot(G.rockerAx, G.sig * (Math.abs(q[1]) / G.g) * (1 + (G.cprog || 0) * Math.abs(q[1]) * D2R)));
      const on = (R, p) => W(M.mulv(R, p));
      const h1 = { kind: 'hub', role: 'active', name: 'J1 (axis on a GH ray)', c: W(V.scale(u[0], G.f[0])), axis: Wd(u[0]), r: rad, h: hub };
      const hK = { kind: 'hub', role: 'passive', name: 'K (O20, passive, slaved; clock-spring cap, stop A; the flank is a lateral lug of link 1a)', c: on(F.R1, V.scale(uK, G.fK)), axis: Wd(M.mulv(F.R1, uK)), r: rad, h: hub + (G.capK || 0) };
      const h2 = { kind: 'hub', role: 'active', name: 'J2 (axis on a GH ray; folded dowel stop, drive stop B)', c: on(F.R1b, V.scale(u[1], G.f[1])), axis: Wd(M.mulv(F.R1b, u[1])), r: rad, h: hub };
      const h3 = { kind: 'hub', role: 'active', name: 'J3 (axis ON a GH ray, b3 0: member 3 moves with the arm)', c: on(F.R12, V.scale(u[2], G.f[2])), axis: Wd(M.mulv(F.R12, u[2])), r: rad, h: hub };
      const Rm = F.R123, n3 = Wd(M.mulv(Rm, sn)), lv = (p, h) => V.madd(on(Rm, p), n3, h);
      const rim = on(Rm, V.add(V.scale(sn, G.f[2] + 1.5), V.scale(G.eE, rad)));
      const arm = p => M.mulv(ctx.H, p), padC = lv(G.Bm, G.tr + G.tp / 2), lat = arm([G.Bm[0], -150, 50]);
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
        { kind: 'arc', role: 'link', name: 'flank lug of link 1a (conjugate flank, wire-EDM)', pts: G.lugPts.map(p => on(F.R1, p)), r: 1.5 },
        h3,
        { kind: 'link', role: 'fixed-arm', name: 'rigid bracket, E run (hub 3 lower plate -> corner), 3 mm Ti, moves with the arm', a: rim, b: lv(G.A0, G.tr + 1.5), r: 2.5 },
        { kind: 'link', role: 'fixed-arm', name: 'rigid bracket, arm run (corner -> pad; the former knee link, no pins)', a: lv(G.A0, G.tr + 1.5), b: lv(G.Bm, G.tr + 1.5), r: 3 },
        { kind: 'plate', role: 'fixed-arm', name: 'arm pad (bracket bolted to the cuff / BOTTOM)', c: padC, z: n3, x: Wd(M.mulv(Rm, G.sa)), size: [14, 14], t: G.tp },
        { kind: 'link', role: 'fixed-arm', name: 'BOTTOM bar to the cuff (schematic)', a: V.madd(padC, n3, -2), b: lat, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: V.scale(ctx.armAxis, 155), axis: ctx.armAxis, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  };
  K.register(C);
})();
