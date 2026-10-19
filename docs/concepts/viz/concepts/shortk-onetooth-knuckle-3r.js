/* shortk-onetooth-knuckle-3r: the verified lead conecut-knee-knuckle-3r (J1 / J2 / J3 seats, knee, J3 dowel stop unchanged) with the K dyad
 * RE-SEATED from bk1 / bk2 26 / 38.03 to 34 / 30 (rest arc a1 37.55 kept) and the two-stage K drive replaced by ONE higher pair: a pin
 * on link 1a pushed by one link-2 tooth flank, held by the lead's clock spring + stop A. Drawn at the only one-pair law that carries
 * the whole K stroke on this dyad with the pin outside hub K's O20 rim: rho 2.0 with a ROLLING follower (pin r 28 mm / az +24 from
 * u2, 12.9 mm from uK; contact 20-28 mm from u2). The spec's slow law (rho 1.05-1.1) has no such pin: built one-pair range <= 29.7 deg
 * sliding / 37.3 rolling vs the 44.1 deg stroke. Measured: law-only ghost frozen exact Bench(110,360) 18.83 (261 ws takes; lead 18.28 /
 * 262) at rho 1.1, 2.0, 2.15 and 2.5; with the drive range the spec's sliding pair can carry (29.7 deg): 31.80 (221 takes). Step-0 kill.
 * Geometry exported from docs/concepts/models/shortk-onetooth-knuckle-3r.py (ghost fit on Bench(60,160)). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 95.3929, "el1": 67.8974, "az2": 45.8211, "el2": 41.0855, "wd": 66.8662, "wa": -10.6559, "b3": 0.329, "lE": 97.1443, "lc": 24.3508, "phiE": 0.7526, "phib": -91.8041, "stk": 6.0, "ang_min": 25.2189, "bk1": 34.0, "bk2": 30.0, "sK": -1, "a1max": 58.7678, "smhi": 22.538647, "smlo": 5.0, "capK": 6.0, "law_mode": "seg", "kA": 2.0, "t1": 6.0, "kB": 2.0, "smt": 12.0, "kK": 2.0, "i_rock": 2.3934, "r_horn": 4.0, "r_lobe": 8.2661, "arm_lo": 1.0, "J3MIN": -111.9036, "J3MAX": 122.7417, "rho": 2.0, "DKLIM": 48.432789};
  const G = {"u": [[0.03536, 0.92651, 0.3746], [-0.46545, 0.61682, 0.63474], [-0.13912, -0.22062, 0.96539]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-0.73949, -13.44608, -3.17939]], "uK": [-0.507, 0.845, 0.172], "sa": [0.03147, -0.97536, -0.21836], "st": [0.98978, 0.0, 0.14263], "sn": [-0.13912, -0.22062, 0.96539], "A": [37.552, 57.218], "branch": -1.0, "m": [-11.73931, 1.15505, 0.0], "f": [50.47, 62.59, 78.15], "fK": 58.54, "capK": 6.0, "tr": 86.97, "tp": 2.75, "RUN": 0.5, "A0": [3.58004, -108.18856, -24.20843], "A0m": [4.35388, -96.73851, -21.48023], "Bm": [-19.76013, -95.99078, -24.78427], "eE": [0.04447, -0.97528, -0.21647], "psiA": -74.475, "thLo": 24.6667, "thHi": 72.2314, "q2s": [102.0679, 18.7025], "lawTh": [72.231, 73.174, 74.122, 75.235, 76.194, 77.318, 78.286, 79.418, 80.39, 81.527, 82.502, 83.639, 84.614, 85.75, 86.722, 87.853, 88.819, 89.942, 90.9, 92.012, 92.959, 94.056, 94.99, 96.069, 96.985, 98.043, 98.94, 99.973, 100.846, 101.851, 102.698, 103.67, 104.488, 105.424, 106.209, 107.104, 107.852, 108.703, 109.411, 110.212, 110.876, 111.624, 112.24, 112.929, 113.494, 114.121, 114.631, 115.191], "lawDK": [-0.0, -1.2, -2.4, -3.8, -5.0, -6.4, -7.6, -9.0, -10.2, -11.6, -12.8, -14.2, -15.4, -16.8, -18.0, -19.4, -20.6, -22.0, -23.2, -24.6, -25.8, -27.2, -28.4, -29.8, -31.0, -32.4, -33.6, -35.0, -36.2, -37.6, -38.8, -40.2, -41.4, -42.8, -44.0, -45.4, -46.6, -48.0, -49.2, -50.6, -51.8, -53.2, -54.4, -55.8, -57.0, -58.4, -59.6, -61.0], "lawQ2": [18.702, 18.102, 17.502, 16.802, 16.202, 15.502, 14.902, 14.202, 13.602, 12.902, 12.302, 11.602, 11.002, 10.302, 9.702, 9.002, 8.402, 7.702, 7.102, 6.402, 5.802, 5.102, 4.502, 3.802, 3.202, 2.502, 1.902, 1.202, 0.602, -0.098, -0.698, -1.398, -1.998, -2.698, -3.298, -3.998, -4.598, -5.298, -5.898, -6.598, -7.198, -7.898, -8.498, -9.198, -9.798, -10.498, -11.098, -11.798], "emb": "rod", "L1a": [[-7.43, 49.183, 13.781], [-13.104, 49.757, 12.143], [-9.39, 46.532, 14.281], [-19.501, 54.731, 14.106], [-14.191, 48.391, 15.601], [-10.474, 45.523, 17.634], [-20.735, 53.194, 18.025]], "L1b": [[-34.586, 47.852, 21.752], [-32.627, 43.077, 26.474], [-30.778, 45.183, 22.69], [-32.564, 45.651, 30.362], [-27.891, 43.593, 23.958], [-29.229, 50.863, 22.754], [-28.941, 47.687, 31.04]], "L2": [[-32.585, 32.197, 48.382], [-30.027, 26.034, 48.817], [-30.061, 22.184, 53.325], [-29.813, 17.838, 57.597], [-29.172, 12.976, 61.364], [-28.194, 7.697, 64.656], [-26.79, 2.058, 67.171], [-24.361, -5.8, 69.343], [-21.933, -11.671, 69.297], [-19.734, -17.774, 70.021], [-30.927, 32.877, 48.938], [-28.53, 26.74, 49.461], [-28.261, 22.703, 53.526], [-27.564, 16.728, 58.652], [-26.718, 11.783, 62.103], [-25.588, 6.477, 65.145], [-24.014, 0.849, 67.283], [-22.044, -4.94, 68.457], [-19.674, -10.688, 68.425], [-17.823, -16.965, 70.459], [-27.484, 30.333, 47.94], [-26.922, 26.126, 51.443], [-26.643, 22.057, 55.685], [-26.133, 17.57, 59.75], [-25.035, 12.497, 62.739], [-23.644, 7.137, 65.198], [-21.192, -0.332, 67.05], [-19.029, -5.987, 67.52], [-16.685, -11.589, 67.379], [-15.755, -18.953, 73.981], [-25.916, 30.978, 48.468], [-25.373, 26.816, 52.05], [-25.102, 22.809, 56.435], [-24.169, 16.651, 61.523], [-23.02, 11.512, 64.579], [-21.519, 6.054, 66.928], [-19.567, 0.388, 68.075], [-17.472, -5.328, 68.879], [-15.066, -10.968, 68.574], [-13.426, -21.029, 77.472]], "dKlim": 48.43, "pin": [-42.23, 46.257, 15.568], "pinAx": [-0.654, 0.717, 0.241], "tooth": [[-35.07, 51.945, 15.234], [-35.715, 51.229, 16.134], [-36.228, 50.572, 17.037], [-36.615, 49.981, 17.93], [-36.885, 49.462, 18.796], [-37.047, 49.018, 19.622], [-37.114, 48.651, 20.394], [-37.097, 48.361, 21.1], [-37.011, 48.149, 21.728], [-36.868, 48.011, 22.269], [-36.684, 47.944, 22.713], [-36.473, 47.942, 23.054]]};
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
    if (!k.ok) return k.L.state === 1 ? `past the tooth end (stop B, K ${G.dKlim} deg)` : (k.L.state === -1 ? 'folded side: J2 on its dowel (no tooth)' : 'chain cannot close');
    if (Math.abs(k.dK) > G.dKlim + 1e-6) return `past the tooth's working range (|dK| ${Math.abs(k.dK).toFixed(1)} > ${G.dKlim} deg): stop B`;
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
    id: 'shortk-onetooth-knuckle-3r', name: 'Re-seated short-K one-tooth knuckle: K dyad 34 / 30, one pin on link 1a pushed by one link-2 tooth (rolling follower, rho 2.0), clock spring + stop A (3 active, K not read)',
    dof: { active: 3, passive: 3 },   // K (slaved by the pin / tooth pair), knee pins a and b
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'K (passive, slaved to q2 by the link-2 tooth on the link-1a pin)', 'J2', 'J3', 'knee pin a', 'knee pin b'], qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve: solveC,
    residual: (q, ctx) => { const F = fk(q); return M.rotErrDeg(F.R5, Qof(ctx)).concat(F.t5); },
    check,
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), F = fk(q);
      const on = (R, p) => W(M.mulv(R, p)), I = M.I3();
      const h1 = { kind: 'hub', role: 'active', name: 'J1 (axis on a GH ray)', c: W(V.scale(u[0], G.f[0])), axis: Wd(u[0]), r: rad, h: hub };
      const hK = { kind: 'hub', role: 'passive', name: 'K (O20, passive, slaved, re-seated 34 / 30; clock-spring cap, stop A; the pin horn is on link 1a)', c: on(F.R1, V.scale(uK, G.fK)), axis: Wd(M.mulv(F.R1, uK)), r: rad, h: hub + (G.capK || 0) };
      const h2 = { kind: 'hub', role: 'active', name: 'J2 (axis on a GH ray; folded dowel stop; the tooth lug rides on link 2 beside it)', c: on(F.R1b, V.scale(u[1], G.f[1])), axis: Wd(M.mulv(F.R1b, u[1])), r: rad, h: hub };
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
        { kind: 'hub', role: 'passive', name: 'pin with a rolling follower on link 1a (12.9 mm from K; the tooth flank pushes it)', c: on(F.R1, G.pin), axis: Wd(M.mulv(F.R1, G.pinAx)), r: 1.25, h: 3 },
        { kind: 'arc', role: 'link', name: 'link-2 tooth lug with the 440C DLC flank insert (stacked over link 1b)', pts: G.tooth.map(p => on(F.R12, p)), r: 1.5 },
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
