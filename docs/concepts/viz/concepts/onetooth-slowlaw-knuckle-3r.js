/* onetooth-slowlaw-knuckle-3r at its step-0 configuration (rho 0.8, the spec's pin r 21.5 mm / az +24 from u2): the verified lead
 * conecut-knee-knuckle-3r (seats, dyad 26 / 38.03, knee, J3 dowel stop loaded unchanged) with the two-stage K drive (bell crank,
 * rim lobe, slipper nose, flank lug) DELETED and ONE higher pair drawn: a crowned 440C pin on link 1a pushed by one link-2 tooth
 * flank, at the SLOW law |dK| = 0.8 t from the onset th 58.55 (lead: 2.1534 from th 77.93), end state = the lead's (K stop B 50).
 * K is held on the tooth by the lead's clock spring + stop A. Measured (step 0, law-only ghost, drive metal deleted): fast
 * Bench(60,160) plain 16.88 (lead-law ghost 12.50); frozen exact Bench(110,360) 22.79, 247 ws takes (kill gate 19.0 / 258);
 * envsel 27.87 (lead-law ghost 24.14). Built flank of this pin: it crosses the relative pole at K 22.4 deg, so the flank is
 * undercut 1.25 mm over K 2.5-20.3 (pin action on one side of the pitch point only). DEAD at step 0.
 * Geometry exported from docs/concepts/models/onetooth-slowlaw-knuckle-3r.py (mode viz). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 95.3929, "el1": 67.8974, "az2": 45.8211, "el2": 41.0855, "wd": 66.8662, "wa": -10.6559, "b3": 0.329, "lE": 97.1443, "lc": 24.3508, "phiE": 0.7526, "phib": -91.8041, "stk": 6.0, "ang_min": 25.2189, "bk1": 26.0, "bk2": 38.0336, "sK": -1, "a1max": 58.7678, "smhi": 36.221615, "smlo": 5.0, "capK": 6.0, "law_mode": "seg", "kA": 0.8, "t1": 6.0, "kB": 0.8, "kK": 0.8};
  const G = {"u": [[0.03536, 0.92651, 0.3746], [-0.46545, 0.61682, 0.63474], [-0.13912, -0.22062, 0.96539]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-0.73949, -13.44608, -3.17939]], "uK": [-0.31441, 0.9448, 0.09223], "sa": [0.03147, -0.97536, -0.21836], "st": [0.98978, 0.0, 0.14263], "sn": [-0.13912, -0.22062, 0.96539], "A": [37.552, 57.218], "branch": -1.0, "m": [-11.73928, 1.18254, 0.0], "f": [50.47, 63.36, 78.14], "fK": 55.32, "capK": 6.0, "tr": 86.97, "tp": 2.75, "RUN": 0.5, "A0": [3.58004, -108.18856, -24.20843], "A0m": [4.38109, -96.73853, -21.47632], "Bm": [-19.73293, -95.9908, -24.78036], "eE": [0.04447, -0.97528, -0.21647], "psiA": -71.6859, "thLo": 24.6667, "thHi": 58.5485, "q2s": [102.0679, 43.1186], "lawTh": [58.548, 59.167, 59.792, 60.423, 61.06, 61.702, 62.35, 63.004, 63.662, 64.325, 64.993, 65.665, 66.342, 67.022, 67.706, 68.394, 69.085, 69.779, 70.476, 71.176, 71.878, 72.583, 73.29, 73.999, 74.709, 75.421, 76.135, 76.849, 77.565, 78.281, 78.997, 79.715, 80.432, 81.149, 81.866, 82.582, 83.298, 84.013, 84.726, 85.439, 86.15, 86.859, 87.566, 88.272, 88.974, 89.674, 90.372, 91.066, 91.757, 92.444, 93.128, 93.808, 94.483, 95.154, 95.82, 96.481, 97.137, 97.788, 98.432, 99.071, 99.703, 100.328, 100.947, 101.558, 102.162, 102.758, 103.346, 103.925, 104.496, 105.058, 105.61, 106.153, 106.686, 107.208, 107.72, 108.221, 108.71, 109.188, 109.654, 110.107, 110.548, 110.976, 111.391, 111.791, 112.178, 112.551, 112.909, 113.252, 113.58, 113.892, 114.188, 114.469, 114.732, 114.979], "lawDK": [-0.0, -0.64, -1.28, -1.92, -2.56, -3.2, -3.84, -4.48, -5.12, -5.76, -6.4, -7.04, -7.68, -8.32, -8.96, -9.6, -10.24, -10.88, -11.52, -12.16, -12.8, -13.44, -14.08, -14.72, -15.36, -16.0, -16.64, -17.28, -17.92, -18.56, -19.2, -19.84, -20.48, -21.12, -21.76, -22.4, -23.04, -23.68, -24.32, -24.96, -25.6, -26.24, -26.88, -27.52, -28.16, -28.8, -29.44, -30.08, -30.72, -31.36, -32.0, -32.64, -33.28, -33.92, -34.56, -35.2, -35.84, -36.48, -37.12, -37.76, -38.4, -39.04, -39.68, -40.32, -40.96, -41.6, -42.24, -42.88, -43.52, -44.16, -44.8, -45.44, -46.08, -46.72, -47.36, -48.0, -48.64, -49.28, -49.92, -50.56, -51.2, -51.84, -52.48, -53.12, -53.76, -54.4, -55.04, -55.68, -56.32, -56.96, -57.6, -58.24, -58.88, -59.52], "lawQ2": [43.119, 42.319, 41.519, 40.719, 39.919, 39.119, 38.319, 37.519, 36.719, 35.919, 35.119, 34.319, 33.519, 32.719, 31.919, 31.119, 30.319, 29.519, 28.719, 27.919, 27.119, 26.319, 25.519, 24.719, 23.919, 23.119, 22.319, 21.519, 20.719, 19.919, 19.119, 18.319, 17.519, 16.719, 15.919, 15.119, 14.319, 13.519, 12.719, 11.919, 11.119, 10.319, 9.519, 8.719, 7.919, 7.119, 6.319, 5.519, 4.719, 3.919, 3.119, 2.319, 1.519, 0.719, -0.081, -0.881, -1.681, -2.481, -3.281, -4.081, -4.881, -5.681, -6.481, -7.281, -8.081, -8.881, -9.681, -10.481, -11.281, -12.081, -12.881, -13.681, -14.481, -15.281, -16.081, -16.881, -17.681, -18.481, -19.281, -20.081, -20.881, -21.681, -22.481, -23.281, -24.081, -24.881, -25.681, -26.481, -27.281, -28.081, -28.881, -29.681, -30.481, -31.281], "emb": "rod", "L1a": [[-4.98, 51.75, 11.11], [-8.27, 54.62, 12.08], [-8.66, 50.09, 15.57]], "L1b": [[-25.06, 52.13, 14.57], [-25.23, 46.69, 18.84], [-27.09, 44.52, 24.18], [-23.29, 52.64, 15.37], [-23.26, 46.57, 19.35], [-25.38, 45.0, 24.95], [-21.52, 53.15, 16.17], [-21.32, 46.4, 19.82], [-23.68, 45.5, 25.72], [-19.75, 53.66, 16.97], [-19.32, 45.98, 20.17], [-21.98, 45.99, 26.5]], "L2": [[-32.97, 32.77, 48.77], [-30.28, 22.74, 53.31], [-29.49, 13.8, 61.31], [-27.2, 3.18, 67.06], [-23.41, -8.34, 69.64], [-19.61, -20.93, 73.06], [-28.38, 25.65, 50.34], [-27.83, 17.44, 58.58], [-25.94, 7.47, 65.01], [-22.66, -3.66, 68.73], [-17.77, -14.74, 67.74], [-27.0, 28.83, 48.28], [-26.48, 21.03, 56.45], [-24.66, 11.5, 62.8], [-21.73, 0.84, 67.2], [-17.37, -10.2, 67.71], [-27.97, 34.82, 50.45], [-25.17, 24.48, 54.39], [-23.89, 15.63, 61.89], [-21.11, 5.21, 66.62], [-17.18, -5.84, 68.53], [-13.68, -18.41, 74.47]], "dKlim": 50.0, "pin": [-32.527, 47.351, 20.517], "pinAx": [-0.53322, 0.77624, 0.33634], "tooth": [[-25.585, 47.772, 34.978], [-24.558, 49.28, 33.596], [-23.5, 50.725, 32.171], [-22.413, 52.106, 30.706], [-21.297, 53.422, 29.203], [-20.154, 54.671, 27.662]]};
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
    if (!k.ok) return k.L.state === 1 ? 'past the tooth end (stop B, K 50 deg)' : (k.L.state === -1 ? 'folded side: J2 on its dowel (no tooth)' : 'chain cannot close');
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
    id: 'onetooth-slowlaw-knuckle-3r', name: 'One-tooth slow-law knuckle: the lead with its crank deleted; one crowned pin on link 1a pushed by one link-2 tooth flank at rho 0.8, clock spring + stop A (3 active, K not read)',
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
      const hK = { kind: 'hub', role: 'passive', name: 'K (O20, passive, slaved; clock-spring cap, stop A; the pin horn is on link 1a)', c: on(F.R1, V.scale(uK, G.fK)), axis: Wd(M.mulv(F.R1, uK)), r: rad, h: hub + (G.capK || 0) };
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
        { kind: 'hub', role: 'passive', name: 'crowned pin (ISO 8734 2.5 m6 440C, pressed in a horn boss of link 1a; the tooth flank pushes it)', c: on(F.R1, G.pin), axis: Wd(M.mulv(F.R1, G.pinAx)), r: 1.25, h: 3 },
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
