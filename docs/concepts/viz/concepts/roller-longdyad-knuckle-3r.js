/* roller-longdyad-knuckle-3r at its best measured configuration: the lead's slaved knuckle (pin knee, link 1 split by a
 * passive O20 knuckle K SLAVED to q2 past the onset) on the LONGER K dyad (bk1 26.1261, bk2 38.0) with the rodless
 * roller-flank drive RE-CUT for a longer stroke: the hub-2 rim lobe pushes the short arm of a bell crank (MR63ZZ pair, pin in
 * link 1b); its bent long arm (straight run, then an arc concentric with hub K at r_c 15.75 mm) carries an MR63ZZ
 * roller that pushes a conjugate flank milled into a boss of link 1a (azimuth -174.64 deg). Law: crank angle =
 * sig |dK| / g, g 2.429; the flank works to dK 46.8 deg (pressure_horn beyond, both pressure angles <= 43).
 * J1, J2, J3 encoders give the pose (3 active, K never read, 0 passive translations).
 * Best measured (CMA stream B, 2 mm objective): fast Bench(60,160) gap 14.0, near-touch 1 mm 14.0.
 * Geometry exported from docs/concepts/models/roller-longdyad-knuckle-3r.py (mode viz). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 96.6954, "el1": 67.5865, "az2": 42.9108, "el2": 44.3599, "wd": 69.2458, "wa": -8.2767, "b3": 0.3613, "lE": 67.832, "lc": 27.7801, "phiE": -2.7863, "phib": -60.9613, "stk": 4.8534, "ang_min": 27.0207, "bk1": 26.1261, "bk2": 38.0, "sK": -1, "a1max": 59.12610000000001, "smhi": 16.0932, "smlo": 5.0, "capK": 6.0, "law_mode": "seg", "kA": 1.5925, "t1": 6.0, "kB": 1.5925, "smt": 12.0, "kK": 1.5925, "i_rock": 2.4288, "r_horn": 4.0, "r_lobe": 7.4772, "arm_lo": 1.0};
  const G = {"u": [[0.04445, 0.92446, 0.37869], [-0.4727, 0.65432, 0.59027], [-0.08031, -0.17214, 0.98179]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-2.37744, -13.89287, -2.63032]], "uK": [-0.26796, 0.96191, 0.05413], "sa": [0.01403, -0.98507, -0.17157], "st": [0.99667, -0.0, 0.08153], "sn": [-0.08031, -0.17214, 0.98179], "A": [36.157, 59.678], "branch": -1.0, "m": [-11.81636, 2.58383, 0.0], "f": [49.72, 60.94, 77.12], "fK": 55.13, "capK": 6.0, "tr": 83.5, "tp": 2.177, "RUN": 0.5, "A0": [-4.71298, -80.63333, -14.52301], "A0m": [-2.30359, -68.99336, -12.28507], "Bm": [-26.3214, -82.27654, -16.57875], "eE": [-0.03443, -0.98391, -0.17533], "psiA": -68.375, "thLo": 28.5217, "thHi": 79.7416, "q2s": [90.5898, -3.8448], "lawTh": [79.742, 80.562, 81.393, 82.233, 83.082, 83.94, 84.805, 85.677, 86.555, 87.439, 88.327, 89.218, 90.113, 91.01, 91.908, 92.807, 93.706, 94.604, 95.5, 96.394, 97.285, 98.172, 99.053, 99.929, 100.798, 101.66, 102.513, 103.357, 104.191, 105.013, 105.824, 106.621, 107.404, 108.173, 108.925, 109.66, 110.377, 111.075, 111.752, 112.409, 113.043, 113.654, 114.24, 114.801, 115.335, 115.842, 116.32, 116.769, 117.187, 117.574, 117.929, 118.25], "lawDK": [-0.0, -1.274, -2.548, -3.822, -5.096, -6.37, -7.644, -8.918, -10.192, -11.466, -12.74, -14.014, -15.288, -16.562, -17.836, -19.11, -20.384, -21.658, -22.932, -24.206, -25.48, -26.754, -28.028, -29.302, -30.576, -31.85, -33.124, -34.398, -35.672, -36.946, -38.22, -39.494, -40.768, -42.042, -43.316, -44.59, -45.864, -47.138, -48.412, -49.686, -50.96, -52.234, -53.508, -54.782, -56.056, -57.33, -58.604, -59.878, -61.152, -62.426, -63.7, -64.974], "lawQ2": [-3.845, -4.645, -5.445, -6.245, -7.045, -7.845, -8.645, -9.445, -10.245, -11.045, -11.845, -12.645, -13.445, -14.245, -15.045, -15.845, -16.645, -17.445, -18.245, -19.045, -19.845, -20.645, -21.445, -22.245, -23.045, -23.845, -24.645, -25.445, -26.245, -27.045, -27.845, -28.645, -29.445, -30.245, -31.045, -31.845, -32.645, -33.445, -34.245, -35.045, -35.845, -36.645, -37.445, -38.245, -39.045, -39.845, -40.645, -41.445, -42.245, -43.045, -43.845, -44.645], "emb": "rod", "rocker": [-25.458, 50.62, 24.491], "rockerAx": [-0.41243, 0.82005, 0.39676], "rodA": [-10.722, 60.155, -11.361], "rodB": [-10.722, 60.155, -11.361], "armA": [-25.458, 50.62, 24.491], "armB": [-31.255, 55.164, 7.108], "L1a": [[-2.28, 49.46, 10.83], [-5.72, 55.05, 11.86], [-8.14, 49.98, 13.61]], "L1b": [[-23.08, 53.49, 11.84], [-23.6, 47.71, 16.01], [-25.79, 45.58, 21.08], [-21.31, 53.93, 12.77], [-21.67, 47.53, 16.67], [-23.68, 45.19, 21.58], [-19.55, 54.37, 13.7], [-19.67, 47.04, 17.2], [-21.9, 45.33, 22.31], [-17.78, 54.82, 14.62], [-17.72, 46.53, 17.69], [-20.26, 45.75, 23.17]], "L2": [[-31.99, 34.23, 45.0], [-29.03, 24.74, 50.25], [-27.57, 16.26, 58.17], [-24.91, 6.24, 64.48], [-20.8, -4.86, 67.73], [-17.05, -17.5, 73.79], [-27.64, 27.82, 47.69], [-26.32, 19.87, 55.69], [-23.93, 10.4, 62.37], [-20.09, -0.27, 66.06], [-15.46, -11.4, 67.75], [-26.66, 31.22, 45.85], [-25.28, 23.44, 53.62], [-23.29, 14.56, 61.11], [-19.72, 4.15, 65.51], [-15.01, -6.71, 66.57], [-27.09, 36.5, 46.42], [-24.2, 26.87, 51.5], [-22.66, 18.67, 59.91], [-19.55, 8.61, 65.6], [-15.05, -2.32, 67.54], [-11.06, -14.64, 74.75]], "armPts": [[-26.077, 51.85, 25.086], [-25.328, 49.609, 21.891], [-26.219, 50.612, 20.222], [-26.811, 51.031, 18.301], [-27.259, 51.182, 16.301], [-27.67, 51.275, 14.312], [-28.435, 52.024, 12.512], [-28.997, 52.401, 10.616], [-31.172, 55.661, 9.205], [-31.99, 56.46, 7.275], [-32.368, 56.468, 5.263], [-32.498, 56.547, 3.222], [-32.378, 56.695, 1.183], [-32.009, 56.911, -0.819], [-31.398, 57.19, -2.753], [-30.554, 57.528, -4.588], [-29.492, 57.92, -6.293], [-28.227, 58.359, -7.842], [-26.781, 58.839, -9.209], [-25.176, 59.352, -10.373], [-23.44, 59.888, -11.315], [-21.598, 60.441, -12.02], [-19.682, 61.0, -12.475], [-17.723, 61.558, -12.675], [-15.75, 62.104, -12.615], [-13.797, 62.63, -12.297], [-11.895, 63.127, -11.726], [-11.436, 63.245, -11.546]], "lugPts": [[-13.832, 57.563, -7.368], [-15.55, 58.417, -14.431], [-14.231, 58.331, -16.05], [-12.765, 58.306, -17.321], [-11.183, 58.316, -18.352], [-9.864, 58.339, -19.023]], "roller": [-10.722, 60.155, -11.361], "rollerAx": [-0.17252, 0.96789, -0.1828], "sig": 1.0, "g": 2.4288, "cprog": 0.0, "dKlim": 46.8};
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
