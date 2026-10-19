/* kneeless-steer-midbracket-relay-4r: the knee-less steered relay at its best measured configuration (envsel). phi40-thinstack-relay-4r's chain
 * (J1 - K slaved by the slipper nose - J2 - J3) with J3 re-seated on a GH ray and the two-pin cuff knee DELETED: member 3
 * (hub 3 lower plate + one bent Ti bracket + a 14 x 14 T-nut carriage) is rigid with the relayed arm frame. Own-angle
 * stops (J2 dowel slot q2 <= Q2MAX, J3 groove [J3MIN, J3MAX]) steer the relay: per frame the relay takes the LEAST phi in
 * [0, PHI] at which the lead's gates and the stops pass. 4 counted joints, K passive (slaved), 0 passive translations.
 * Geometry: CC.viz_export at this seat + the relay geometry of the metal wear record. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 95.3929, "el1": 67.8974, "az2": 45.8211, "el2": 41.0855, "wd": 80.0, "wa": -15.0, "b3": 0.0, "lE": 97.1443, "lc": 24.3508, "phiE": 0.7526, "phib": -91.8041, "stk": 6.0, "ang_min": 25.2189, "bk1": 26.0, "bk2": 38.0336, "sK": -1, "a1max": 58.7678, "smhi": 16.8433, "smlo": 5.0, "capK": 6.0, "law_mode": "seg", "kA": 2.1534, "t1": 6.0, "kB": 2.1534, "smt": 12.0, "kK": 2.1534, "i_rock": 2.3934, "r_horn": 4.0, "r_lobe": 8.2661, "arm_lo": 1.0, "J3MIN": -100.0, "J3MAX": 115.0, "Q2MAX": 100.0};
  const G = {"u": [[0.03536, 0.92651, 0.3746], [-0.47446, 0.62192, 0.62298], [-0.25489, -0.17365, 0.95125]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-0.0, 0.0, 0.0]], "uK": [-0.30739, 0.94787, 0.08396], "sa": [0.04494, -0.98481, -0.16773], "st": [0.96593, 0.0, 0.25882], "sn": [-0.25489, -0.17365, 0.95125], "A": [37.552, 52.732], "branch": -1.0, "m": [0.0, 0.0, 0.0], "f": [50.47, 61.65, 75.28], "fK": 55.05, "capK": 6.0, "tr": 85.44, "tp": 2.75, "RUN": 0.5, "A0": [5.59813, -95.66021, -15.96248], "A0m": [5.59813, -95.66021, -15.96248], "Bm": [-17.94573, -94.90523, -22.13322], "eE": [0.05763, -0.98472, -0.16432], "psiA": -71.6859, "thLo": 20.1801, "thHi": 73.4402, "q2s": [108.2332, 13.5446], "lawTh": [73.44, 74.451, 75.478, 76.518, 77.571, 78.636, 79.71, 80.793, 81.883, 82.979, 84.079, 85.182, 86.287, 87.393, 88.497, 89.599, 90.698, 91.791, 92.878, 93.958, 95.028, 96.087, 97.134, 98.167, 99.186, 100.187, 101.171, 102.135, 103.077, 103.997, 104.892, 105.761, 106.602, 107.414, 108.195, 108.943, 109.657], "lawDK": [-0.0, -1.723, -3.445, -5.168, -6.891, -8.614, -10.336, -12.059, -13.782, -15.504, -17.227, -18.95, -20.673, -22.395, -24.118, -25.841, -27.564, -29.286, -31.009, -32.732, -34.454, -36.177, -37.9, -39.623, -41.345, -43.068, -44.791, -46.513, -48.236, -49.959, -51.682, -53.404, -55.127, -56.85, -58.572, -60.295, -62.018], "lawQ2": [13.545, 12.745, 11.945, 11.145, 10.345, 9.545, 8.745, 7.945, 7.145, 6.345, 5.545, 4.745, 3.945, 3.145, 2.345, 1.545, 0.745, -0.055, -0.855, -1.655, -2.455, -3.255, -4.055, -4.855, -5.655, -6.455, -7.255, -8.055, -8.855, -9.655, -10.455, -11.255, -12.055, -12.855, -13.655, -14.455, -15.255], "emb": "rod", "rocker": [-26.905, 49.438, 27.014], "rockerAx": [-0.43095, 0.79187, 0.43269], "rodA": [-13.212, 59.078, -9.268], "rodB": [-13.212, 59.078, -9.268], "armA": [-26.905, 49.438, 27.014], "armB": [-32.86, 52.9, 8.791], "L1a": [[-3.7, 50.04, 11.32], [-7.21, 54.63, 12.52], [-9.17, 49.45, 14.45]], "L1b": [[-24.82, 52.12, 13.84], [-24.99, 46.43, 17.98], [-26.91, 44.19, 23.16], [-23.05, 52.62, 14.69], [-23.09, 46.42, 18.59], [-24.94, 44.19, 23.72], [-21.27, 53.12, 15.55], [-21.1, 46.15, 19.08], [-23.16, 44.45, 24.41], [-19.5, 53.62, 16.4], [-19.36, 46.32, 19.73], [-21.49, 44.93, 25.22]], "L2": [[-32.84, 31.86, 47.2], [-30.55, 21.9, 52.76], [-28.93, 12.14, 59.56], [-27.24, 1.18, 67.2], [-29.18, 26.78, 49.18], [-28.42, 18.05, 57.41], [-26.3, 7.61, 63.82], [-29.47, 33.27, 48.36], [-27.46, 23.5, 54.39], [-25.98, 13.85, 61.96], [-23.51, 2.74, 68.47], [-26.06, 28.28, 50.55], [-25.42, 19.81, 59.58], [-23.23, 9.3, 66.47]], "armPts": [[-27.551, 50.625, 27.663], [-26.723, 48.299, 24.225], [-27.795, 49.437, 22.612], [-28.338, 49.624, 20.539], [-28.822, 49.718, 18.448], [-29.303, 49.814, 16.381], [-30.091, 50.432, 14.488], [-30.971, 51.195, 12.61], [-33.411, 54.493, 11.223], [-33.908, 54.587, 9.071], [-34.039, 54.212, 6.991], [-34.182, 54.346, 4.953], [-34.073, 54.561, 2.919], [-33.712, 54.855, 0.925], [-33.105, 55.222, -0.997], [-32.264, 55.655, -2.812], [-31.202, 56.149, -4.492], [-29.936, 56.693, -6.008], [-28.489, 57.28, -7.333], [-26.885, 57.899, -8.446], [-25.151, 58.539, -9.327], [-23.316, 59.19, -9.962], [-21.412, 59.842, -10.34], [-19.47, 60.482, -10.455], [-17.523, 61.1, -10.305], [-15.605, 61.685, -9.892], [-14.058, 62.139, -9.355]], "lugPts": [[-15.168, 57.237, -5.332], [-17.257, 58.053, -9.092], [-16.091, 57.804, -12.264], [-14.616, 57.839, -13.844], [-13.0, 57.929, -15.031], [-11.903, 58.001, -15.646]], "roller": [-13.212, 59.078, -9.268], "rollerAx": [-0.21573, 0.96466, -0.15133], "sig": 1.0, "g": 2.3934, "cprog": 0.0, "dKlim": 49.5};
  const RL = {"ax": [0.17031, 0.97815, 0.11925], "e": [0.98518, -0.17154, 0.0], "f": [0.02046, 0.11749, -0.99286], "s0": -80, "Rt": 80.12, "lo": -100.72, "hi": -29.13, "th0": -105.66, "hc": 1.4, "PHI": 58.0, "sgn": 1.0, "sw": 12.0, "cw": 14.0, "cl": 14.0, "thc": -93.21, "coil": -107.96, "coilS": -68.0, "coilR": 87.52, "coilD": 12.0, "coilL": 10.0, "bump": 1.2};
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
  const Q0of = ctx => M.mul(M.T(ctx.S), ctx.H);
  const relayOK = Q => checkQ(solveQ(Q), Q) === null;
  function phiOf(ctx) {
    if (ctx._rphi !== undefined) return ctx._rphi;
    const Q0 = Q0of(ctx), at = f => M.mul(Q0, M.rot(RL.ax, RL.sgn * f)); let ph = 0;
    if (!relayOK(Q0)) {
      let hit = null;
      for (let f = 1; f <= RL.PHI + 1e-9; f += 1) { if (relayOK(at(f))) { hit = f; break; } }
      if (hit !== null) { let lo = hit - 1, hi = hit; for (let k = 0; k < 5; k++) { const mid = (lo + hi) / 2; if (relayOK(at(mid))) hi = mid; else lo = mid; } ph = hi; }
    }
    ctx._rphi = ph; return ph;
  }
  const Qof = ctx => M.mul(Q0of(ctx), M.rot(RL.ax, RL.sgn * phiOf(ctx)));
  function solve(ctx) { return solveQ(Qof(ctx)).concat([phiOf(ctx)]); }
  function solveQ(Q) {
    const k = ik(Q), R12 = M.mul(M.mul(M.rot(u[0], k.q1), M.rot(uK, k.dK)), M.rot(u[1], k.q2));
    const q3 = K.axisAngle(u[2], vref, M.mulv(M.T(R12), M.mulv(Q, vref)));
    return [k.q1, k.dK, k.q2, K.wrap180(q3)];
  }
  function fk(q) { const X = chain(q[0], q[1], q[2], q[3]); return Object.assign(X, { Rm3: X.R123 }); }
  const check = (q, ctx) => checkQ(q, Qof(ctx));
  function checkQ(q, Q) {
    const k = ik(Q);
    if (!k.ok) return k.L.state === 1 ? 'past the drive stop B (stop B / pressure angle / lift-off)' : (k.L.state === -1 ? 'folded side: J2 on its dowel (no tooth)' : 'chain cannot close');
    if (Math.abs(k.dK) > G.dKlim + 1e-6) return `past the flank's working range (|dK| ${Math.abs(k.dK).toFixed(1)} > ${G.dKlim} deg): stop B`;
    if (k.L.state === 0 && k.q2 > P.Q2MAX) return `J2 on its stretched dowel stop (q2 ${k.q2.toFixed(1)} > ${P.Q2MAX} deg: own-angle slot in hub 2's lower member)`;
    if (q[3] < P.J3MIN) return `J3 on its hard stop (q3' ${q[3].toFixed(1)} < ${P.J3MIN} deg: dowel in hub 3's lower plate at the end of its arc groove)`;
    if (P.J3MAX < 180 && q[3] > P.J3MAX) return `J3 on its upper hard stop (q3' ${q[3].toFixed(1)} > ${P.J3MAX} deg)`;
    return null;
  }
  const closes = (q, ctx) => { const r = C.residual(q, ctx); return Math.max(...r.map(Math.abs)) <= 0.5; };
  const solveC = (ctx, qPrev) => { const q = solve(ctx); return (!qPrev || closes(q, ctx)) ? q : K.dls(C, ctx, qPrev, { iters: 40 }).q; };
  const C = {
    id: 'kneeless-steer-midbracket-relay-4r', name: 'Knee-less steered relay: phi40 chain with the cuff knee deleted, J3 on a GH ray (80, -15), own-angle stops q2 <= 100 / J3 [-100, 115], one rigid member 3 (hub 3 + bracket + T-nut carriage) on an arm-fixed 1.0 mm shell at s0 -80, PHI 58 (4 counted joints)',
    dof: { active: 4, passive: 1 },   // J1, J2, J3 + the counted relay; K slaved (slipper nose); no knee, no cuff slides
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'K (passive, slaved to q2 by the lobe - bell crank - sliding nose - flank)', 'J2', 'J3', 'relay phi (carriage on the arm arc; constant-force strip on its zero dowel)'], qUnits: ['deg', 'deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm', 'deg'],
    solve: solveC,
    residual: (q, ctx) => { const F = fk(q); return M.rotErrDeg(F.Rm3, Qof(ctx)).concat(F.t3, [q[4] - phiOf(ctx)]); },
    check,
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), F = fk(q);
      const Rc = M.mul(F.R1b, M.rot(G.rockerAx, G.sig * (Math.abs(q[1]) / G.g) * (1 + (G.cprog || 0) * Math.abs(q[1]) * D2R)));
      const on = (R, p) => W(M.mulv(R, p)), I = M.I3();
      const h1 = { kind: 'hub', role: 'active', name: 'J1 (axis on a GH ray)', c: W(V.scale(u[0], G.f[0])), axis: Wd(u[0]), r: rad, h: hub };
      const hK = { kind: 'hub', role: 'passive', name: 'K (O20, passive, slaved; clock-spring cap, stop A; the horn is a lateral lug of link 1a)', c: on(F.R1, V.scale(uK, G.fK)), axis: Wd(M.mulv(F.R1, uK)), r: rad, h: hub + (G.capK || 0) };
      const h2 = { kind: 'hub', role: 'active', name: 'J2 (axis on a GH ray; folded dowel stop, drive stop B)', c: on(F.R1b, V.scale(u[1], G.f[1])), axis: Wd(M.mulv(F.R1b, u[1])), r: rad, h: hub };
      const h3 = { kind: 'hub', role: 'active', name: 'J3 (axis on a GH ray, re-seated; hard stop: 2 mm dowel in hub 3 lower plate at r 7.5 in an arc groove under link 2, q3p >= ' + P.J3MIN + (P.J3MAX < 180 ? ', <= ' + P.J3MAX : '') + ')', c: on(F.R12, V.madd(c[2], u[2], G.f[2])), axis: Wd(M.mulv(F.R12, u[2])), r: rad, h: hub,
                   p0: on(F.R12, c[2]) };
      const rim = W(V.add(M.mulv(F.Rm3, V.add(V.madd(c[2], sn, G.f[2] + 1.5), V.scale(G.eE, rad))), F.t3));
      const Hc = M.mul(ctx.S, Qof(ctx)), arm = p => M.mulv(Hc, p);
      const dTh = t => V.add(V.scale(RL.e, Math.cos(t * D2R)), V.scale(RL.f, Math.sin(t * D2R)));
      const trk = []; for (let t = RL.lo; t <= RL.hi + 1e-9; t += (RL.hi - RL.lo) / 24) trk.push(M.mulv(ctx.H, V.madd(V.scale(RL.ax, RL.s0), dTh(t), RL.Rt)));
      const dC = M.mulv(Hc, dTh(RL.thc)), carC = M.mulv(Hc, V.madd(V.scale(RL.ax, RL.s0), dTh(RL.thc), RL.Rt + RL.hc / 2));
      const coilC = M.mulv(Hc, V.madd(V.scale(RL.ax, RL.coilS), dTh(RL.coil), RL.coilR));
      const axW = M.mulv(ctx.H, RL.ax), lug = M.mulv(Hc, V.madd(V.scale(RL.ax, RL.s0 + RL.cl / 2), dTh(RL.thc), RL.Rt + RL.hc + RL.bump));
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
        { kind: 'hub', role: 'passive', name: 'O2 hardened 440C nose (ISO 8734 dowel pressed in the arm tip; slides on the flank, DLC + grease)', c: on(Rc, G.roller), axis: Wd(M.mulv(Rc, G.rollerAx)), r: 1.18, h: 2.5 },
        { kind: 'arc', role: 'link', name: 'horn lug of link 1a with the conjugate flank (wire-EDM)', pts: G.lugPts.map(p => on(F.R1, p)), r: 1.5 },
        h3,
        { kind: 'link', role: 'link', name: 'member 3 bracket: one bent 3 x 10 Ti-6Al-4V bar down E\'s fitted line, hub 3 lower plate -> the carriage posterior-proximal lug (60-deg climb, bend R >= 15)', a: rim, b: lug, r: 2.5 },
        { kind: 'plate', role: 'passive', name: 'relay carriage (COUNTED 4th joint: 14 x 14 Ti T-nut, h_c 1.4, in the 1.0 mm slotted circular shell, iglidur tape, retaining flange under the shell; lug coil onto the zero dowel, slot end = PHI stop)', c: carC, z: dC, x: axW, size: [RL.cl, RL.cw], t: RL.hc },
        { kind: 'arc', role: 'fixed-arm', name: 'circular track: 1.0 mm slotted Ti shell about the relay axis (one radius), 31 mm proximal of the pad, arc [-4.0, +50.4] deg rel the pad azimuth, on the arm liner', pts: trk, r: 2 },
        { kind: 'hub', role: 'passive', name: 'constant-force coil (12 OD x 10 wide, 301 SS, on the carriage posterior-proximal lug; strip to the zero end)', c: coilC, axis: axW, r: RL.coilD / 2, h: RL.coilL },
        { kind: 'link', role: 'fixed-arm', name: 'relay axis through GH (construction line)', a: V.scale(axW, -20), b: V.scale(axW, -170), r: 0.5 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: V.scale(ctx.armAxis, 155), axis: ctx.armAxis, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  };
  K.register(C);
})();
