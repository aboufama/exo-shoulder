/* armarc-relay-knuckle-4r: the verified lead conecut-knee-knuckle-3r UNCHANGED (seats, knuckle K and its drive, pin knee, J3 dowel
 * stop) with a one-sided ARM-ARC RELAY at the cuff: the arm pad (knee pin b's boss) rides a carriage on a circular track about an
 * arm-fixed axis through GH (tilted from the humeral long axis so the circle hugs the arm), held on its zero dowel by a
 * constant-force spring. Per frame the relay takes the LEAST phi in [0, PHI] at which the lead's gates pass (closure, drive range,
 * knee window, J3 stop); the arm-side frame turns by phi about the relay axis; every chain axis still passes through GH.
 * 4 counted joints (J1, J2, J3 + the relay), K / bell crank / knee pins passive. Schematic: the knee stack's lift onto the
 * carriage is not drawn. Geometry RL from docs/concepts/models/armarc-relay-knuckle-4r.py relay_geometry() at the best config. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 95.3929, "el1": 67.8974, "az2": 45.8211, "el2": 41.0855, "wd": 66.8662, "wa": -10.6559, "b3": 0.329, "lE": 97.1443, "lc": 24.3508, "phiE": 0.7526, "phib": -91.8041, "stk": 6.0, "ang_min": 25.2189, "bk1": 26.0, "bk2": 38.0336, "sK": -1, "a1max": 58.7678, "smhi": 16.8433, "smlo": 5.0, "capK": 6.0, "law_mode": "seg", "kA": 2.1534, "t1": 6.0, "kB": 2.1534, "smt": 12.0, "kK": 2.1534, "i_rock": 2.3934, "r_horn": 4.0, "r_lobe": 8.2661, "arm_lo": 1.0, "J3MIN": -111.9036, "J3MAX": 122.7417};
  const G = {"u": [[0.03536, 0.92651, 0.3746], [-0.46545, 0.61682, 0.63474], [-0.13912, -0.22062, 0.96539]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-0.73949, -13.44608, -3.17939]], "uK": [-0.31441, 0.9448, 0.09223], "sa": [0.03147, -0.97536, -0.21836], "st": [0.98978, 0.0, 0.14263], "sn": [-0.13912, -0.22062, 0.96539], "A": [37.552, 57.218], "branch": -1.0, "m": [-11.73931, 1.16262, 0.0], "f": [50.47, 62.52, 78.17], "fK": 55.12, "capK": 6.0, "tr": 86.97, "tp": 2.75, "RUN": 0.5, "A0": [3.58004, -108.18856, -24.20843], "A0m": [4.36137, -96.73851, -21.47916], "Bm": [-19.75265, -95.99078, -24.78319], "eE": [0.04447, -0.97528, -0.21647], "psiA": -71.6859, "thLo": 24.6667, "thHi": 77.9268, "q2s": [102.0679, 7.2787], "lawTh": [77.927, 78.936, 79.961, 81.001, 82.054, 83.12, 84.197, 85.283, 86.377, 87.477, 88.583, 89.693, 90.806, 91.919, 93.032, 94.144, 95.252, 96.356, 97.453, 98.544, 99.625, 100.695, 101.753, 102.798, 103.827, 104.839, 105.833, 106.806, 107.757, 108.684, 109.585, 110.459, 111.304, 112.117, 112.898, 113.643, 114.352], "lawDK": [-0.0, -1.723, -3.445, -5.168, -6.891, -8.614, -10.336, -12.059, -13.782, -15.504, -17.227, -18.95, -20.673, -22.395, -24.118, -25.841, -27.564, -29.286, -31.009, -32.732, -34.454, -36.177, -37.9, -39.623, -41.345, -43.068, -44.791, -46.513, -48.236, -49.959, -51.682, -53.404, -55.127, -56.85, -58.572, -60.295, -62.018], "lawQ2": [7.279, 6.479, 5.679, 4.879, 4.079, 3.279, 2.479, 1.679, 0.879, 0.079, -0.721, -1.521, -2.321, -3.121, -3.921, -4.721, -5.521, -6.321, -7.121, -7.921, -8.721, -9.521, -10.321, -11.121, -11.921, -12.721, -13.521, -14.321, -15.121, -15.921, -16.721, -17.521, -18.321, -19.121, -19.921, -20.721, -21.521], "emb": "rod", "rocker": [-27.14, 49.7, 28.261], "rockerAx": [-0.42884, 0.7853, 0.44654], "rodA": [-14.018, 59.019, -8.884], "rodB": [-14.018, 59.019, -8.884], "armA": [-27.14, 49.7, 28.261], "armB": [-33.242, 52.639, 9.374], "L1a": [[-3.91, 49.99, 11.46], [-7.44, 54.61, 12.76], [-9.31, 49.41, 14.73]], "L1b": [[-24.99, 51.94, 14.51], [-25.02, 46.25, 18.66], [-26.75, 43.91, 23.85], [-23.22, 52.45, 15.31], [-23.08, 46.18, 19.18], [-25.04, 44.37, 24.6], [-21.44, 52.96, 16.12], [-21.08, 45.9, 19.61], [-23.34, 44.86, 25.37], [-19.66, 53.48, 16.92], [-19.3, 45.99, 20.18], [-21.65, 45.36, 26.14]], "L2": [[-32.55, 32.16, 48.33], [-29.95, 22.1, 53.12], [-29.06, 12.93, 61.13], [-26.72, 2.05, 67.0], [-22.74, -9.71, 69.3], [-19.64, -23.69, 75.99], [-28.39, 24.11, 52.23], [-27.37, 15.15, 59.97], [-25.06, 4.62, 65.84], [-21.23, -6.85, 68.39], [-17.74, -19.8, 73.53], [-26.94, 26.15, 51.49], [-26.19, 17.61, 59.88], [-23.75, 7.17, 65.48], [-19.78, -4.1, 67.46], [-15.93, -16.16, 70.92], [-25.42, 28.06, 50.57], [-24.98, 20.05, 59.73], [-22.7, 9.78, 65.85], [-18.94, -1.51, 68.6], [-14.32, -12.9, 68.77]], "armPts": [[-27.784, 50.878, 28.931], [-26.56, 47.85, 25.241], [-27.628, 48.989, 23.851], [-28.152, 49.153, 21.956], [-28.663, 49.298, 20.064], [-29.285, 49.635, 18.253], [-29.722, 49.661, 16.336], [-30.519, 50.287, 14.613], [-32.829, 53.363, 13.483], [-33.809, 54.234, 11.669], [-34.302, 54.317, 9.673], [-34.444, 53.952, 7.592], [-34.604, 54.098, 5.555], [-34.511, 54.327, 3.522], [-34.167, 54.636, 1.527], [-33.578, 55.02, -0.396], [-32.754, 55.472, -2.215], [-31.708, 55.985, -3.9], [-30.458, 56.549, -5.421], [-29.026, 57.156, -6.753], [-27.435, 57.794, -7.873], [-25.713, 58.454, -8.763], [-23.888, 59.124, -9.408], [-21.992, 59.793, -9.796], [-20.056, 60.45, -9.921], [-18.114, 61.083, -9.781], [-16.197, 61.681, -9.379], [-14.895, 62.072, -8.947]], "lugPts": [[-15.829, 57.167, -4.893], [-18.011, 58.032, -8.162], [-17.122, 57.713, -11.608], [-15.709, 57.747, -13.31], [-14.159, 57.844, -14.571], [-12.809, 57.945, -15.395]], "roller": [-14.018, 59.019, -8.884], "rollerAx": [-0.22865, 0.96267, -0.1449], "sig": 1.0, "g": 2.3934, "cprog": 0.0, "dKlim": 50.0};
  const RL = {"ax": [0.1632, 0.9848, 0.0594], "e": [0.9865, -0.1635, 0.0], "f": [0.0097, 0.0586, -0.9982], "s0": -115.11, "Rt": 69.6, "lo": -114.2, "hi": -67.37, "th0": -100.78, "hc": 1.7, "dh": 5.3, "PHI": 20.0, "sgn": 1.0, "rpad": 66.0, "sw": 12.0, "cw": 24.0, "cl": 14.0};
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
  const check = (q, ctx) => checkQ(q, Qof(ctx));
  function checkQ(q, Q) {
    const k = ik(Q);
    if (!k.ok) return k.L.state === 1 ? 'past the drive stop B (stop B / pressure angle / lift-off)' : (k.L.state === -1 ? 'folded side: J2 on its dowel (no tooth)' : 'chain cannot close');
    if (Math.abs(k.dK) > G.dKlim + 1e-6) return `past the flank's working range (|dK| ${Math.abs(k.dK).toFixed(1)} > ${G.dKlim} deg): stop B`;
    const F = fk(q), sv = M.mulv(M.T(Q), F.t3), kn = knee([V.dot(sv, sa), V.dot(sv, st)]);
    if (!kn.span) return 'knee span: the drift is beyond lE + lc';
    if (kn.ang < P.ang_min || kn.ang > 180 - P.ang_min) return `knee angle ${kn.ang.toFixed(0)} deg outside [${P.ang_min}, ${180 - P.ang_min}]`;
    if (q[3] < P.J3MIN) return `J3 on its hard stop (q3' ${q[3].toFixed(1)} < ${P.J3MIN} deg: dowel in hub 3's lower plate at the end of its arc groove)`;
    if (P.J3MAX < 180 && q[3] > P.J3MAX) return `J3 on its upper hard stop (q3' ${q[3].toFixed(1)} > ${P.J3MAX} deg)`;
    return null;
  }
  const closes = (q, ctx) => { const r = C.residual(q, ctx); return Math.max(...r.map(Math.abs)) <= 0.5; };
  const solveC = (ctx, qPrev) => { const q = solve(ctx); return (!qPrev || closes(q, ctx)) ? q : K.dls(C, ctx, qPrev, { iters: 40 }).q; };
  const C = {
    id: 'armarc-relay-knuckle-4r', name: 'Lead + one-sided arm-arc relay: the pad rides a spring-held carriage on a circular track about a GH-through arm axis (4 counted joints)',
    dof: { active: 4, passive: 4 },   // J1, J2, J3 + the counted relay; K, bell crank, knee pins a and b passive
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'K (passive, slaved to q2 by the lobe - bell crank - sliding nose - flank sidecar)', 'J2', 'J3', 'knee pin a', 'knee pin b', 'relay phi (carriage on the arm arc; spring on its zero dowel)'], qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm', 'deg'],
    solve: solveC,
    residual: (q, ctx) => { const F = fk(q); return M.rotErrDeg(F.R5, Qof(ctx)).concat(F.t5, [q[6] - phiOf(ctx)]); },
    check,
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), F = fk(q);
      const Rc = M.mul(F.R1b, M.rot(G.rockerAx, G.sig * (Math.abs(q[1]) / G.g) * (1 + (G.cprog || 0) * Math.abs(q[1]) * D2R)));
      const on = (R, p) => W(M.mulv(R, p)), I = M.I3();
      const h1 = { kind: 'hub', role: 'active', name: 'J1 (axis on a GH ray)', c: W(V.scale(u[0], G.f[0])), axis: Wd(u[0]), r: rad, h: hub };
      const hK = { kind: 'hub', role: 'passive', name: 'K (O20, passive, slaved; clock-spring cap, stop A; the horn is a lateral lug of link 1a)', c: on(F.R1, V.scale(uK, G.fK)), axis: Wd(M.mulv(F.R1, uK)), r: rad, h: hub + (G.capK || 0) };
      const h2 = { kind: 'hub', role: 'active', name: 'J2 (axis on a GH ray; folded dowel stop, drive stop B)', c: on(F.R1b, V.scale(u[1], G.f[1])), axis: Wd(M.mulv(F.R1b, u[1])), r: rad, h: hub };
      const h3 = { kind: 'hub', role: 'active', name: 'J3 (skin-normal tilt, line misses GH; hard stop: 2 mm dowel in hub 3 lower plate at r 7.5 in an arc groove under link 2, q3p >= ' + P.J3MIN + (P.J3MAX < 180 ? ', <= ' + P.J3MAX : '') + ')', c: on(F.R12, V.madd(c[2], u[2], G.f[2])), axis: Wd(M.mulv(F.R12, u[2])), r: rad, h: hub,
                   p0: on(F.R12, c[2]) };
      const n3 = Wd(M.mulv(F.Rm3, sn)), lvl = (p, h) => V.madd(W(p), n3, h), kz = G.tr + G.tp + G.RUN + G.tp / 2;
      const rim = W(V.add(M.mulv(F.Rm3, V.add(V.madd(c[2], sn, G.f[2] + 1.5), V.scale(G.eE, rad))), F.t3));
      const Hc = M.mul(ctx.S, Qof(ctx)), arm = p => M.mulv(Hc, p), padC = arm(V.madd(G.Bm, sn, G.tr + G.tp / 2)), padN = M.mulv(Hc, sn);
      const dTh = t => V.add(V.scale(RL.e, Math.cos(t * D2R)), V.scale(RL.f, Math.sin(t * D2R)));
      const trk = []; for (let t = RL.lo; t <= RL.hi + 1e-9; t += (RL.hi - RL.lo) / 24) trk.push(M.mulv(ctx.H, V.madd(V.scale(RL.ax, RL.s0), dTh(t), RL.Rt)));
      const dC = M.mulv(Hc, dTh(RL.th0)), carC = M.mulv(Hc, V.madd(V.scale(RL.ax, RL.s0), dTh(RL.th0), RL.Rt + RL.hc / 2));
      const axW = M.mulv(ctx.H, RL.ax);
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
        { kind: 'link', role: 'link', name: 'E strap (member 3: hub 3 lower plate -> pin a)', a: rim, b: lvl(F.pa, G.tr + 1.5), r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'knee pin a (MR63ZZ pair, parallel to J3)', c: lvl(F.pa, G.tr), axis: n3, r: 6, h: P.stk, p0: lvl(F.pa, G.tr) },
        { kind: 'link', role: 'link', name: 'knee link (flat Ti plate)', a: lvl(F.pa, kz), b: lvl(F.pb, kz), r: 3 },
        { kind: 'hub', role: 'passive', name: 'knee pin b (MR63ZZ pair, parallel to J3)', c: lvl(F.pb, G.tr), axis: n3, r: 6, h: P.stk, p0: lvl(F.pb, G.tr) },
        { kind: 'plate', role: 'fixed-arm', name: 'arm pad (on the cuff / BOTTOM)', c: padC, z: padN, x: arm(sa), size: [14, 14], t: G.tp },
        { kind: 'link', role: 'passive', name: 'pad mount: carriage -> arm pad (schematic)', a: V.madd(padC, padN, -2), b: carC, r: 2 },
        { kind: 'plate', role: 'passive', name: 'relay carriage (COUNTED 4th joint: T-nut carriage in the slotted circular shell, iglidur strip; constant-force spring onto the zero dowel, end dowel at PHI)', c: carC, z: dC, x: axW, size: [RL.cl, RL.cw], t: RL.hc },
        { kind: 'arc', role: 'fixed-arm', name: 'circular track: slotted Ti shell about the relay axis (one radius), on a 4 mm liner, strapped to the arm', pts: trk, r: 2 },
        { kind: 'link', role: 'fixed-arm', name: 'relay axis through GH (construction line)', a: [0, 0, 0], b: V.scale(axW, -170), r: 0.5 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: V.scale(ctx.armAxis, 155), axis: ctx.armAxis, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  };
  K.register(C);
})();
