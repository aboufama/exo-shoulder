/* slowpole-slot-knuckle-3r: the verified lead conecut-knee-knuckle-3r (J1 / J2 / J3 seats, knee, J3 dowel stop unchanged) with the K dyad
 * re-seated and the two-stage K drive (lobe, bell crank, nose, clock spring, stop A) replaced by ONE crowned pin on hub 2's rotor ring
 * running in a form-closed dwell-and-rise slot on a link-1a plate (no spring, no crank). Drawn at the best measured cell: K dyad 32 / 38
 * (uK 6.4 deg off the lead's), law rho 0.84 from th 65.8 (the variable-ratio law a pin at r 18 mm / phase 5 carries at PA <= 38:
 * rho 0.62-0.94, dwell lock <= 36 deg), drive range = the slot's rise end K 38.1. Measured (law-only ghost, drive metal deleted,
 * frozen exact Bench(110,360)): 18.83, 261 ws takes, 5 contacts, overhead 8/28 (lead 18.28 / 262); the spec cell (40/40, rho 0.5)
 * 40.17 (hub K 45.7 mm off the skin). The slot locus is drawn from the constant-ratio law (schematic).
 * Geometry exported from docs/concepts/models/slowpole-slot-knuckle-3r.py (ghost fit on Bench(60,160)). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 95.3929, "el1": 67.8974, "az2": 45.8211, "el2": 41.0855, "wd": 66.8662, "wa": -10.6559, "b3": 0.329, "lE": 97.1443, "lc": 24.3508, "phiE": 0.7526, "phib": -91.8041, "stk": 6.0, "ang_min": 25.2189, "bk1": 32.0, "bk2": 38.0, "sK": -1, "a1max": 58.7678, "smhi": 29.001567, "smlo": 5.0, "capK": 6.0, "law_mode": "seg", "kA": 0.84, "t1": 6.0, "kB": 0.84, "smt": 12.0, "kK": 0.84, "i_rock": 2.3934, "r_horn": 4.0, "r_lobe": 8.2661, "arm_lo": 1.0};
  const G = {"u": [[0.03536, 0.92651, 0.3746], [-0.46545, 0.61682, 0.63474], [-0.13912, -0.22062, 0.96539]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-0.73949, -13.44608, -3.17939]], "uK": [-0.41352, 0.90883, 0.05507], "sa": [0.03147, -0.97536, -0.21836], "st": [0.98978, 0.0, 0.14263], "sn": [-0.13912, -0.22062, 0.96539], "A": [37.552, 57.218], "branch": -1.0, "m": [-11.73928, 1.17774, 0.0], "f": [50.45, 62.2, 79.86], "fK": 57.36, "capK": 6.0, "tr": 86.97, "tp": 2.75, "RUN": 0.5, "A0": [3.58004, -108.18856, -24.20843], "A0m": [4.37634, -96.73854, -21.47701], "Bm": [-19.73767, -95.99081, -24.78104], "eE": [0.04447, -0.97528, -0.21647], "psiA": -67.5604, "thLo": 24.6667, "thHi": 65.7685, "q2s": [102.0679, 30.61], "lawTh": [65.769, 66.468, 67.172, 67.883, 68.599, 69.32, 70.045, 70.775, 71.51, 72.248, 72.99, 73.736, 74.484, 75.236, 75.99, 76.746, 77.505, 78.265, 79.027, 79.791, 80.555, 81.321, 82.086, 82.853, 83.619, 84.385, 85.151, 85.916, 86.68, 87.443, 88.204, 88.963, 89.721, 90.476, 91.228, 91.978, 92.725, 93.468, 94.207, 94.942, 95.673, 96.399, 97.121, 97.837, 98.547, 99.252, 99.95, 100.642, 101.327, 102.004, 102.674, 103.336, 103.99, 104.634, 105.27, 105.896, 106.513, 107.119, 107.714, 108.299, 108.872, 109.433, 109.982, 110.518, 111.041, 111.55, 112.046, 112.527, 112.993, 113.444, 113.879, 114.298, 114.701, 115.086, 115.455], "lawDK": [-0.0, -0.672, -1.344, -2.016, -2.688, -3.36, -4.032, -4.704, -5.376, -6.048, -6.72, -7.392, -8.064, -8.736, -9.408, -10.08, -10.752, -11.424, -12.096, -12.768, -13.44, -14.112, -14.784, -15.456, -16.128, -16.8, -17.472, -18.144, -18.816, -19.488, -20.16, -20.832, -21.504, -22.176, -22.848, -23.52, -24.192, -24.864, -25.536, -26.208, -26.88, -27.552, -28.224, -28.896, -29.568, -30.24, -30.912, -31.584, -32.256, -32.928, -33.6, -34.272, -34.944, -35.616, -36.288, -36.96, -37.632, -38.304, -38.976, -39.648, -40.32, -40.992, -41.664, -42.336, -43.008, -43.68, -44.352, -45.024, -45.696, -46.368, -47.04, -47.712, -48.384, -49.056, -49.728], "lawQ2": [30.61, 29.81, 29.01, 28.21, 27.41, 26.61, 25.81, 25.01, 24.21, 23.41, 22.61, 21.81, 21.01, 20.21, 19.41, 18.61, 17.81, 17.01, 16.21, 15.41, 14.61, 13.81, 13.01, 12.21, 11.41, 10.61, 9.81, 9.01, 8.21, 7.41, 6.61, 5.81, 5.01, 4.21, 3.41, 2.61, 1.81, 1.01, 0.21, -0.59, -1.39, -2.19, -2.99, -3.79, -4.59, -5.39, -6.19, -6.99, -7.79, -8.59, -9.39, -10.19, -10.99, -11.79, -12.59, -13.39, -14.19, -14.99, -15.79, -16.59, -17.39, -18.19, -18.99, -19.79, -20.59, -21.39, -22.19, -22.99, -23.79, -24.59, -25.39, -26.19, -26.99, -27.79, -28.59], "emb": "rod", "rocker": [-29.533, 48.518, 27.047], "rockerAx": [-0.46945, 0.77122, 0.42993], "rodA": [-22.776, 58.116, -11.592], "rodB": [-22.776, 58.116, -11.592], "armA": [-29.533, 48.518, 27.047], "armB": [-38.989, 51.337, 9.333], "L1a": [[-5.42, 50.03, 11.46], [-10.83, 53.42, 8.72], [-7.74, 47.62, 11.42], [-14.45, 55.96, 9.68], [-10.68, 49.01, 12.29], [-8.55, 48.33, 15.95], [-14.18, 51.61, 13.52]], "L1b": [[-30.42, 51.91, 13.79], [-28.79, 45.67, 18.2], [-29.47, 43.29, 23.67], [-28.6, 52.7, 14.35], [-26.89, 46.03, 18.57], [-27.55, 43.66, 23.99], [-26.78, 53.5, 14.91], [-24.93, 46.19, 18.85], [-25.6, 43.93, 24.25], [-24.96, 54.29, 15.47], [-22.95, 46.24, 19.08], [-23.86, 44.51, 24.69]], "L2": [[-32.37, 32.22, 47.91], [-30.1, 22.69, 53.04], [-29.29, 13.84, 60.98], [-27.05, 3.32, 66.8], [-23.31, -8.12, 69.48], [-20.01, -21.14, 74.73], [-28.38, 25.73, 50.38], [-27.67, 17.45, 58.29], [-25.79, 7.57, 64.7], [-22.55, -3.47, 68.51], [-18.1, -14.82, 69.15], [-27.04, 28.93, 48.36], [-26.52, 21.16, 56.57], [-24.73, 11.67, 63.05], [-21.61, 1.0, 66.92], [-17.32, -9.99, 67.64], [-27.47, 34.24, 49.54], [-25.19, 24.58, 54.44], [-23.91, 15.76, 61.96], [-21.17, 5.38, 66.86], [-17.22, -5.67, 68.78], [-13.97, -18.56, 76.16]], "armPts": [[-30.237, 49.674, 27.692], [-29.777, 47.677, 24.694], [-30.953, 48.345, 23.152], [-31.783, 48.469, 21.339], [-32.568, 48.532, 19.514], [-33.241, 48.441, 17.649], [-34.02, 48.517, 15.865], [-35.619, 49.747, 14.431], [-38.362, 52.504, 13.315], [-39.587, 53.127, 11.555], [-40.257, 53.006, 9.636], [-40.527, 52.346, 7.612], [-40.934, 52.282, 5.608], [-41.102, 52.329, 3.569], [-41.028, 52.486, 1.53], [-40.713, 52.751, -0.474], [-40.162, 53.119, -2.41], [-39.386, 53.583, -4.245], [-38.396, 54.137, -5.948], [-37.209, 54.77, -7.49], [-35.847, 55.472, -8.846], [-34.331, 56.231, -9.991], [-32.688, 57.035, -10.908], [-30.944, 57.869, -11.58], [-29.13, 58.719, -11.996], [-27.277, 59.572, -12.149], [-25.414, 60.412, -12.036], [-24.016, 61.033, -11.775]], "lugPts": [[-23.775, 56.505, -7.253], [-26.058, 57.157, -9.194]], "roller": [-22.776, 58.116, -11.592], "rollerAx": [-0.35875, 0.9154, -0.18259], "sig": 1.0, "g": 2.3934, "cprog": 0.0, "dKlim": 38.1, "pin": [-37.202, 50.205, 28.309], "pinAx": [-0.5423, 0.73186, 0.41267], "slot": [[-45.174, 30.33, 41.778], [-45.393, 30.658, 41.298], [-45.594, 30.999, 40.82], [-45.777, 31.352, 40.343], [-45.941, 31.716, 39.867], [-46.088, 32.092, 39.395], [-46.216, 32.478, 38.926], [-46.325, 32.875, 38.46], [-46.415, 33.281, 37.999], [-46.486, 33.697, 37.543], [-46.538, 34.121, 37.093], [-46.572, 34.554, 36.648], [-46.585, 34.994, 36.21], [-46.58, 35.441, 35.779], [-46.556, 35.895, 35.356], [-46.512, 36.355, 34.941], [-46.449, 36.821, 34.535], [-46.368, 37.291, 34.138], [-46.267, 37.766, 33.75], [-46.147, 38.245, 33.373], [-46.009, 38.726, 33.006], [-45.853, 39.211, 32.65], [-45.678, 39.697, 32.305], [-45.485, 40.185, 31.973], [-45.274, 40.673, 31.653], [-45.046, 41.162, 31.345], [-44.8, 41.651, 31.051], [-44.537, 42.138, 30.77], [-44.258, 42.624, 30.502], [-43.962, 43.108, 30.249], [-43.65, 43.589, 30.01], [-44.037, 43.78, 29.154], [-44.38, 43.98, 28.321], [-44.682, 44.187, 27.514], [-44.945, 44.399, 26.733], [-45.171, 44.615, 25.981], [-45.364, 44.833, 25.261], [-45.525, 45.052, 24.572], [-45.658, 45.27, 23.916], [-45.765, 45.485, 23.295], [-45.85, 45.695, 22.708], [-45.916, 45.9, 22.157], [-45.964, 46.097, 21.641], [-45.999, 46.285, 21.161], [-46.023, 46.462, 20.715], [-46.039, 46.627, 20.304], [-46.05, 46.779, 19.927], [-46.059, 46.915, 19.583], [-46.068, 47.036, 19.271], [-46.08, 47.139, 18.988], [-46.098, 47.223, 18.734], [-46.123, 47.287, 18.507], [-46.159, 47.331, 18.305]]};
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
    if (!k.ok) return k.L.state === 1 ? `past the slot's rise end (K ${G.dKlim} deg: the slot end is the stretched stop)` : (k.L.state === -1 ? 'folded side: J2 on its dowel (the pin rides the dwell arc, K locked)' : 'chain cannot close');
    if (Math.abs(k.dK) > G.dKlim + 1e-6) return `past the slot's working range (|dK| ${Math.abs(k.dK).toFixed(1)} > ${G.dKlim} deg)`;
    const F = fk(q), sv = M.mulv(M.T(Q), F.t3), kn = knee([V.dot(sv, sa), V.dot(sv, st)]);
    if (!kn.span) return 'knee span: the drift is beyond lE + lc';
    if (kn.ang < P.ang_min || kn.ang > 180 - P.ang_min) return `knee angle ${kn.ang.toFixed(0)} deg outside [${P.ang_min}, ${180 - P.ang_min}]`;
    if (q[3] < P.J3MIN) return `J3 on its hard stop (q3' ${q[3].toFixed(1)} < ${P.J3MIN} deg: dowel in hub 3's lower plate at the end of its arc groove)`;
    if (P.J3MAX < 180 && q[3] > P.J3MAX) return `J3 on its upper hard stop (q3' ${q[3].toFixed(1)} > ${P.J3MAX} deg)`;
    return null;
  };
  const closes = (q, ctx) => { const r = C.residual(q, ctx); return Math.max(...r.map(Math.abs)) <= 0.5; };
  const solveC = (ctx, qPrev) => { const q = solve(ctx); return (!qPrev || closes(q, ctx)) ? q : K.dls(C, ctx, qPrev, { iters: 40 }).q; };
  const C = {
    id: 'slowpole-slot-knuckle-3r', name: 'Slow-pole cam-slot knuckle: the lead with a 40 / 40 K dyad, a slow law (rho 0.5) and one crowned pin on hub 2s rotor in a form-closed slot on link 1a (3 active, K not read; ghost law)',
    dof: { active: 3, passive: 3 },   // K (slaved by the pin / tooth pair), knee pins a and b
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'K (passive, slaved to q2 by the pin on hub 2s rotor in the link-1a slot, both ways)', 'J2', 'J3', 'knee pin a', 'knee pin b'], qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve: solveC,
    residual: (q, ctx) => { const F = fk(q); return M.rotErrDeg(F.R5, Qof(ctx)).concat(F.t5); },
    check,
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), F = fk(q);
      const on = (R, p) => W(M.mulv(R, p)), I = M.I3();
      const h1 = { kind: 'hub', role: 'active', name: 'J1 (axis on a GH ray)', c: W(V.scale(u[0], G.f[0])), axis: Wd(u[0]), r: rad, h: hub };
      const hK = { kind: 'hub', role: 'passive', name: 'K (O20, passive, slaved, re-seated 40 / 40; plain cap: no clock spring, no stop-A pin - the slot holds K both ways)', c: on(F.R1, V.scale(uK, G.fK)), axis: Wd(M.mulv(F.R1, uK)), r: rad, h: hub + (G.capK || 0) };
      const h2 = { kind: 'hub', role: 'active', name: 'J2 (axis on a GH ray; folded dowel stop; its rotor ring carries the O6 x 3 pin lug)', c: on(F.R1b, V.scale(u[1], G.f[1])), axis: Wd(M.mulv(F.R1b, u[1])), r: rad, h: hub };
      const h3 = { kind: 'hub', role: 'active', name: 'J3 (skin-normal tilt, line misses GH; hard stop: 2 mm dowel in hub 3 lower plate at r 7.5 in an arc groove under link 2, q3p >= ' + P.J3MIN + (P.J3MAX < 180 ? ', <= ' + P.J3MAX : '') + ')', c: on(F.R12, V.madd(c[2], u[2], G.f[2])), axis: Wd(M.mulv(F.R12, u[2])), r: rad, h: hub,
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
        { kind: 'hub', role: 'link', name: 'drive pin (O2.5 crowned 440C dowel in an O6 x 3 lug on hub 2s rotor ring, r 13.5 mm from J2)', c: on(F.R12, G.pin), axis: Wd(M.mulv(F.R12, G.pinAx)), r: 1.25, h: 3 },
        { kind: 'arc', role: 'link', name: 'slot plate on the link-1a horn (1.5 mm Ti, DLC walls: dwell arc about J2 + the conjugate rise)', pts: G.slot.map(p => on(F.R1, p)), r: 1.5 },
        h3,
        { kind: 'link', role: 'link', name: 'E strap (member 3: hub 3 lower plate -> pin a)', a: rim, b: lvl(F.pa, G.tr + 1.5), r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'knee pin a (MR63ZZ pair, parallel to J3)', c: lvl(F.pa, G.tr), axis: n3, r: 6, h: P.stk, p0: lvl(F.pa, G.tr) },
        { kind: 'link', role: 'link', name: 'knee link (flat Ti plate)', a: lvl(F.pa, kz), b: lvl(F.pb, kz), r: 3 },
        { kind: 'hub', role: 'passive', name: 'knee pin b (MR63ZZ pair, parallel to J3)', c: lvl(F.pb, G.tr), axis: n3, r: 6, h: P.stk, p0: lvl(F.pb, G.tr) },
        { kind: 'plate', role: 'fixed-arm', name: 'arm pad (on the cuff / BOTTOM)', c: padC, z: padN, x: arm(sa), size: [14, 14], t: G.tp },
        { kind: 'link', role: 'fixed-arm', name: 'BOTTOM bar to the cuff (schematic)', a: V.madd(padC, padN, -2), b: lat, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: V.scale(ctx.armAxis, 155), axis: ctx.armAxis, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  };
  K.register(C);
})();
