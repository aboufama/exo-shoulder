/* ikring-distalshell-knuckle-4r: the verified lead conecut-knee-knuckle-3r with a SHORT knee (lE 69.52, lc 18.63: every mover
 * above s ~107 in the humerus frame) + an ACTIVE one-sided J4 ring: a 1.0 mm slotted circular Ti shell DISTAL of every mover
 * (s0 -117.1 mm along the ring axis, R_t 71.86, no E bump, no knee lift), 14 mm T-nut carriage, L-lug bracket up to the pad at
 * its own level; J4 psi in [0, 40] about a GH-through axis tilted 8.5 deg toward taz 243. Bench rule: lead-first proximity IK
 * (pick 1 ikring-thinstack-knuckle-4r imported). This preview runs the KINEMATIC controller the flood checks (psi 0 while the
 * lead gates pass, else the feasible k nearest the previous psi). Geometry: docs/concepts/verify/ikring-distalshell-knuckle-4r/. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 95.3929, "el1": 67.8974, "az2": 45.8211, "el2": 41.0855, "wd": 66.8662, "wa": -10.6559, "b3": 0.329, "lE": 69.52, "lc": 18.63, "phiE": -5.44, "phib": -80.96, "stk": 6.0, "ang_min": 25.64, "bk1": 26.0, "bk2": 38.0336, "sK": -1, "a1max": 58.7678, "smhi": 16.8433, "smlo": 5.0, "capK": 6.0, "law_mode": "seg", "kA": 2.1534, "t1": 6.0, "kB": 2.1534, "smt": 12.0, "kK": 2.1534, "i_rock": 2.3934, "r_horn": 4.0, "r_lobe": 8.2661, "arm_lo": 1.0};
  const G = {"u": [[0.03536, 0.92651, 0.3746], [-0.46545, 0.61682, 0.63474], [-0.13912, -0.22062, 0.96539]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-0.73949, -13.44608, -3.17939]], "uK": [-0.31441, 0.9448, 0.09223], "sa": [0.03147, -0.97536, -0.21836], "st": [0.98978, 0.0, 0.14263], "sn": [-0.13912, -0.22062, 0.96539], "A": [37.552, 57.218], "branch": -1.0, "m": [-11.73931, 1.16262, 0.0], "f": [50.45, 62.04, 78.18], "fK": 55.12, "capK": 6.0, "tr": 88.58, "tp": 2.75, "RUN": 0.5, "A0": [-5.08509, -80.9477, -19.23175], "A0m": [-4.30376, -69.49765, -16.50248], "Bm": [-22.42214, -72.35274, -19.76588], "eE": [-0.06251, -0.97097, -0.2309], "psiA": -71.6859, "thLo": 24.6667, "thHi": 77.9268, "q2s": [102.0679, 7.2787], "lawTh": [77.927, 78.936, 79.961, 81.001, 82.054, 83.12, 84.197, 85.283, 86.377, 87.477, 88.583, 89.693, 90.806, 91.919, 93.032, 94.144, 95.252, 96.356, 97.453, 98.544, 99.625, 100.695, 101.753, 102.798, 103.827, 104.839, 105.833, 106.806, 107.757, 108.684, 109.585, 110.459, 111.304, 112.117, 112.898, 113.643, 114.352], "lawDK": [-0.0, -1.723, -3.445, -5.168, -6.891, -8.614, -10.336, -12.059, -13.782, -15.504, -17.227, -18.95, -20.673, -22.395, -24.118, -25.841, -27.564, -29.286, -31.009, -32.732, -34.454, -36.177, -37.9, -39.623, -41.345, -43.068, -44.791, -46.513, -48.236, -49.959, -51.682, -53.404, -55.127, -56.85, -58.572, -60.295, -62.018], "lawQ2": [7.279, 6.479, 5.679, 4.879, 4.079, 3.279, 2.479, 1.679, 0.879, 0.079, -0.721, -1.521, -2.321, -3.121, -3.921, -4.721, -5.521, -6.321, -7.121, -7.921, -8.721, -9.521, -10.321, -11.121, -11.921, -12.721, -13.521, -14.321, -15.121, -15.921, -16.721, -17.521, -18.321, -19.121, -19.921, -20.721, -21.521], "emb": "rod", "rocker": [-26.916, 49.402, 27.954], "rockerAx": [-0.42845, 0.7864, 0.44498], "rodA": [-14.018, 59.019, -8.884], "rodB": [-14.018, 59.019, -8.884], "armA": [-26.916, 49.402, 27.954], "armB": [-33.204, 52.638, 9.512], "L1a": [[-3.91, 49.97, 11.45], [-7.44, 54.61, 12.76], [-9.31, 49.42, 14.73]], "L1b": [[-25.01, 51.93, 14.5], [-25.04, 46.25, 18.65], [-26.76, 43.91, 23.84], [-23.22, 52.45, 15.31], [-23.08, 46.18, 19.18], [-24.84, 44.02, 24.4], [-21.43, 52.96, 16.12], [-21.07, 45.89, 19.61], [-23.15, 44.51, 25.17], [-19.65, 53.48, 16.93], [-19.29, 45.99, 20.18], [-21.47, 45.0, 25.93]], "L2": [[-32.32, 31.93, 47.98], [-29.96, 22.1, 53.12], [-29.07, 12.93, 61.13], [-26.73, 2.05, 67.0], [-22.75, -9.71, 69.31], [-19.66, -23.7, 76.0], [-28.4, 24.11, 52.22], [-27.37, 15.15, 59.97], [-25.07, 4.62, 65.84], [-21.24, -6.85, 68.39], [-17.75, -19.81, 73.56], [-26.94, 26.15, 51.49], [-26.19, 17.61, 59.88], [-23.74, 7.17, 65.49], [-19.78, -4.1, 67.46], [-15.93, -16.17, 70.96], [-25.41, 28.06, 50.57], [-24.97, 20.06, 59.74], [-22.69, 9.79, 65.85], [-18.94, -1.51, 68.61], [-14.31, -12.89, 68.77]], "armPts": [[-27.558, 50.582, 28.621], [-26.616, 47.964, 24.969], [-27.759, 49.141, 23.389], [-28.35, 49.33, 21.309], [-28.918, 49.485, 19.231], [-29.437, 49.563, 17.143], [-30.269, 50.17, 15.237], [-31.182, 50.9, 13.343], [-33.714, 54.223, 11.992], [-34.263, 54.317, 9.816], [-34.423, 53.945, 7.737], [-34.601, 54.085, 5.702], [-34.526, 54.308, 3.667], [-34.2, 54.612, 1.669], [-33.628, 54.99, -0.261], [-32.82, 55.438, -2.089], [-31.79, 55.946, -3.784], [-30.554, 56.507, -5.318], [-29.134, 57.111, -6.664], [-27.554, 57.748, -7.8], [-25.84, 58.406, -8.708], [-24.022, 59.076, -9.37], [-22.13, 59.746, -9.777], [-20.196, 60.403, -9.921], [-18.253, 61.038, -9.8], [-16.333, 61.64, -9.416], [-14.895, 62.072, -8.947]], "lugPts": [[-15.845, 57.162, -4.898], [-18.034, 57.996, -8.365], [-17.032, 57.716, -11.724], [-15.586, 57.76, -13.398], [-14.007, 57.863, -14.641], [-12.833, 57.953, -15.345]], "roller": [-14.018, 59.019, -8.884], "rollerAx": [-0.22865, 0.96267, -0.1449], "sig": 1.0, "g": 2.3934, "cprog": 0.0, "dKlim": 49.8};
  const RL = {"ax": [0.1317, 0.989, 0.0671], "e": [0.9913, -0.132, 0.0], "f": [0.0089, 0.0665, -0.9977], "s0": -117.1, "Rt": 71.86, "lo": -115.6, "hi": -60.4, "th0": -107.2, "hc": 1.4, "dh": 0.0, "PHI": 40.0, "sgn": 1.0, "rpad": 74.03, "sw": 12.0, "cw": 14.0, "cl": 14.0, "thc": -107.2, "kstep": 2.5};
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
  function phiOf(ctx, prev) {
    if (ctx._rphi !== undefined) return ctx._rphi;
    const Q0 = Q0of(ctx), at = f => M.mul(Q0, M.rot(RL.ax, RL.sgn * f)); let ph = 0;
    if (!relayOK(Q0)) {
      const feas = []; for (let f = RL.kstep; f <= RL.PHI + 1e-9; f += RL.kstep) if (relayOK(at(f))) feas.push(f);
      if (feas.length) { const p0 = (prev == null || !(prev > 0)) ? 0 : prev; ph = feas.reduce((b, f) => (Math.abs(f - p0) < Math.abs(b - p0) - 1e-9 ? f : b), feas[0]); }
    }
    ctx._rphi = ph; return ph;
  }
  const Qof = ctx => M.mul(Q0of(ctx), M.rot(RL.ax, RL.sgn * phiOf(ctx)));
  function solve(ctx, qPrev) { phiOf(ctx, qPrev ? qPrev[6] : null); return solveQ(Qof(ctx)).concat([phiOf(ctx)]); }
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
  const solveC = (ctx, qPrev) => { const q = solve(ctx, qPrev); return (!qPrev || closes(q, ctx)) ? q : K.dls(C, ctx, qPrev, { iters: 40 }).q; };
  const C = {
    id: 'ikring-distalshell-knuckle-4r', name: 'Lead with a short knee + ACTIVE J4 ring on a round shell DISTAL of every mover (PHI 40, axis 8.5 / 243), lead-first IK (4 active joints)',
    dof: { active: 4, passive: 4 },   // J1, J2, J3, J4 (ring, ACTIVE); K, bell crank, knee pins a and b passive
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'K (passive, slaved to q2 by the lobe - bell crank - sliding nose - flank sidecar)', 'J2', 'J3', 'knee pin a', 'knee pin b', 'J4 ring psi (ACTIVE: carriage on the arm-fixed shell, slot-end stops 0 / 40)'], qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
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
      const dC = M.mulv(Hc, dTh(RL.thc)), carC = M.mulv(Hc, V.madd(V.scale(RL.ax, RL.s0), dTh(RL.thc), RL.Rt + RL.hc / 2));
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
        { kind: 'link', role: 'passive', name: 'L-lug bracket: 2 x 10 Ti at the pad azimuth (no planform turn), from the carriage proximal edge UP the arm to the pad distal edge, at the pad own fitted level', a: V.madd(padC, padN, -2), b: carC, r: 2 },
        { kind: 'plate', role: 'active', name: 'J4 carriage (ACTIVE counted 4th joint: 14 x 14 Ti T-nut, h_c 1.4, in the 1.0 mm slotted circular shell, iglidur tape, retaining flange under the shell; slot ends = psi 0 / 40 stops; no coil)', c: carC, z: dC, x: axW, size: [RL.cl, RL.cw], t: RL.hc },
        { kind: 'arc', role: 'fixed-arm', name: 'circular track: 1.0 mm slotted Ti shell about the relay axis (one radius), 26 mm DISTAL of the pad centroid (below every mover), arc [-8.4, 46.8] deg rel the pad azimuth, on the arm liner', pts: trk, r: 2 },
        { kind: 'link', role: 'fixed-arm', name: 'relay axis through GH (construction line)', a: V.scale(axW, -20), b: V.scale(axW, -170), r: 0.5 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: V.scale(ctx.armAxis, 155), axis: ctx.armAxis, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  };
  K.register(C);
})();
