/* kneeless-roller-knuckle-3r at its best measured configuration: the verified roller-flank knuckle (J1 acromion top, link 1a
 * with the conjugate flank lug, passive O20 knuckle K SLAVED to q2 by the hub-2 rim lobe -> bell crank (MR63ZZ pair on link
 * 1b) -> bent long arm -> MR63ZZ roller -> flank, link 1b, J2, link 2, J3) with J3's axis ON A GH RAY (b3 0): member 3 moves
 * with the arm, the drift is identically 0, so the two-pin knee carried nothing and is DELETED - hub 3's lower plate, the
 * E strap and the former knee link are ONE rigid Ti bracket bolted to the arm pad on BOTTOM. 3 active (J1, J2, J3 encoded),
 * K slaved and never read, 0 passive translations, 0 sensed passives.
 * Best measured so far (CMA C, 2 mm objective, fast Bench(60,160)): 2 mm 23.29, 1 mm 19.93, plain 18.77 (reach 0.756, in-band 0.883, contact 0.027).
 * Geometry exported from docs/concepts/models/kneeless-roller-knuckle-3r.py (mode viz). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 95.3929, "el1": 67.8974, "az2": 44.456, "el2": 40.6927, "wd": 78.7485, "wa": -10.7456, "b3": 0.0, "lE": 85.3723, "lc": 20.3346, "phiE": -2.782, "phib": -114.562, "stk": 4.8534, "ang_min": 0.0, "bk1": 27.7251, "bk2": 35.7114, "sK": -1, "a1max": 56.3168, "smhi": 16.4911, "smlo": 5.0, "capK": 6.0, "law_mode": "seg", "kA": 2.2546, "t1": 6.0, "kB": 2.2546, "smt": 12.0, "kK": 2.2546, "i_rock": 2.2817, "r_horn": 4.4442, "r_lobe": 8.1395, "arm_lo": 1.0};
  const G = {"u": [[0.03536, 0.92651, 0.3746], [-0.48399, 0.61139, 0.62606], [-0.18287, -0.19512, 0.96358]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-0.0, 0.0, 0.0]], "uK": [-0.36546, 0.92406, 0.112], "sa": [0.03638, -0.98078, -0.19169], "st": [0.98246, 0.0, 0.18645], "sn": [-0.18287, -0.19512, 0.96358], "A": [38.384, 55.077], "branch": -1.0, "m": [0.0, 0.0, 0.0], "f": [50.47, 62.34, 76.09], "fK": 55.8, "capK": 6.0, "tr": 87.48, "tp": 2.177, "RUN": 0.5, "A0": [-0.96886, -83.63278, -17.11869], "A0m": [-0.96886, -83.63278, -17.11869], "Bm": [-19.44662, -75.3426, -18.94665], "eE": [-0.01135, -0.97962, -0.20052], "psiA": -76.1238, "thLo": 21.6936, "thHi": 76.9697, "q2s": [103.3748, 6.686], "lawTh": [76.97, 78.113, 79.268, 80.434, 81.609, 82.792, 83.981, 85.174, 86.37, 87.568, 88.764, 89.959, 91.15, 92.336, 93.515, 94.685, 95.845, 96.994, 98.128, 99.247, 100.35, 101.433, 102.495, 103.535, 104.55, 105.539, 106.499, 107.429, 108.327], "lawDK": [-0.0, -1.804, -3.607, -5.411, -7.215, -9.018, -10.822, -12.626, -14.429, -16.233, -18.037, -19.84, -21.644, -23.448, -25.252, -27.055, -28.859, -30.663, -32.466, -34.27, -36.074, -37.877, -39.681, -41.485, -43.288, -45.092, -46.896, -48.699, -50.503], "lawQ2": [6.686, 5.886, 5.086, 4.286, 3.486, 2.686, 1.886, 1.086, 0.286, -0.514, -1.314, -2.114, -2.914, -3.714, -4.514, -5.314, -6.114, -6.914, -7.714, -8.514, -9.314, -10.114, -10.914, -11.714, -12.514, -13.314, -14.114, -14.914, -15.714], "emb": "rod", "rocker": [-28.787, 49.055, 27.338], "rockerAx": [-0.45617, 0.77734, 0.4332], "rodA": [-18.203, 58.782, -8.132], "rodB": [-18.203, 58.782, -8.132], "armA": [-28.787, 49.055, 27.338], "armB": [-35.94, 51.102, 12.541], "L1a": [[-4.6, 49.7, 12.22], [-10.83, 54.92, 9.75], [-8.71, 50.67, 14.8], [-9.0, 46.16, 15.13]], "L1b": [[-27.85, 50.85, 15.85], [-27.6, 45.32, 20.03], [-30.31, 44.62, 26.33], [-25.0, 47.6, 17.36], [-26.21, 44.74, 22.33], [-30.55, 46.6, 30.46], [-23.18, 46.11, 19.29], [-25.08, 44.61, 24.87], [-22.52, 52.68, 18.19], [-21.95, 45.75, 21.63], [-24.99, 46.44, 28.67]], "L2": [[-32.98, 31.77, 48.09], [-29.01, 21.6, 52.26], [-26.76, 12.63, 59.33], [-23.39, 2.39, 64.75], [-29.37, 29.55, 47.26], [-27.12, 21.01, 54.02], [-24.72, 11.88, 61.12], [-21.27, 1.46, 66.84], [-27.44, 28.95, 48.88], [-25.29, 20.48, 56.01], [-22.7, 11.15, 63.17], [-19.51, 0.5, 70.64], [-25.48, 28.32, 50.45], [-23.29, 19.83, 57.75], [-20.63, 10.41, 65.33], [-17.59, -0.54, 74.8]], "armPts": [[-29.471, 50.221, 27.988], [-28.814, 47.87, 24.743], [-29.958, 48.565, 23.161], [-30.739, 48.667, 21.283], [-31.492, 48.73, 19.402], [-32.305, 48.892, 17.571], [-33.1, 49.032, 15.74], [-35.793, 51.93, 14.697], [-36.786, 52.305, 12.836], [-37.439, 52.282, 10.896], [-37.858, 52.358, 8.893], [-38.038, 52.534, 6.861], [-37.974, 52.805, 4.833], [-37.669, 53.167, 2.841], [-37.127, 53.614, 0.918], [-36.357, 54.14, -0.904], [-35.371, 54.735, -2.597], [-34.185, 55.39, -4.132], [-32.819, 56.094, -5.485], [-31.296, 56.836, -6.634], [-29.638, 57.604, -7.559], [-27.875, 58.384, -8.247], [-26.034, 59.166, -8.685], [-24.145, 59.935, -8.867], [-22.239, 60.679, -8.789], [-20.348, 61.386, -8.453], [-19.265, 61.777, -8.14]], "lugPts": [[-20.748, 55.726, -4.071], [-23.721, 56.649, -9.0], [-22.823, 56.592, -11.369], [-21.615, 56.699, -13.071], [-20.259, 56.869, -14.434], [-18.757, 57.08, -15.584], [-17.606, 57.249, -16.291]], "roller": [-18.203, 58.782, -8.132], "rollerAx": [-0.29327, 0.94701, -0.131], "sig": 1.0, "g": 2.2817, "cprog": 0.0, "dKlim": 50.5};
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
