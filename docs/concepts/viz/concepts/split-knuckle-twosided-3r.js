/* split-knuckle-twosided-3r at its best K2-engaged configuration (Bench(60,160) fast near-touch 30.88; reach 0.7875,
 * in-band 0.7143). The verified winner (pin knee + K on link 1 slaved by the hub-2 rotor-rim lobe -> rocker -> O3 pushrod ->
 * horn on K's cap, stretched end) PLUS a second slaved knuckle K2 on link 2, bK2a from J2: a lobe on hub 2's STATOR side
 * (link 1b) drives a rocker on link 2a and a second pushrod to a horn on K2, so past the folded onset q2lo K2 bends by
 * dK2 = kK2 t and the effective arc a2e = arc(J2, J3) shortens (th_min drops from thLo to the law's end). J1, J2, J3
 * encoders give the pose (3 active; K and K2 never read). Geometry exported from
 * docs/concepts/models/split-knuckle-twosided-3r.py (viz mode). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 93.5546, "el1": 67.3642, "az2": 43.4586, "el2": 43.3068, "wd": 63.337, "wa": -9.6473, "b3": 0.3837, "lE": 67.832, "lc": 25.8149, "phiE": -2.7863, "phib": -65.6717, "stk": 4.8534, "ang_min": 27.8544, "bk1": 31.2491, "bk2": 37.9937, "sK": -1, "a1max": 58.3565, "smhi": 13.6865, "smlo": 7.404, "capK": 6.0, "emb_mode": "rod", "kK": 3.1796, "r_horn": 2.4932, "bK2a": 28.95, "bK2b": 39.73, "sK2": 1, "kK2": 0.876, "t0K2": 0.0, "B2": 38.2, "capK2": 6.0, "k2_low": 0, "r_horn2": 2.63};
  const G = {"u": [[0.02386, 0.92297, 0.38413], [-0.47582, 0.64318, 0.59993], [-0.09951, -0.23654, 0.96651]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-1.97854, -17.4181, -4.46644]], "uK": [-0.37536, 0.92661, 0.02251], "uK2": [-0.12412, 0.43833, 0.8902], "sa": [0.02422, -0.97162, -0.23529], "st": [0.99474, 0.0, 0.10241], "sn": [-0.09951, -0.23654, 0.96651], "A": [35.636, 61.637], "branch": -1.0, "m": [-15.31502, 2.40882, 0.0], "f": [50.12, 60.24, 80.93], "fK": 56.71, "fK2": 68.36, "capK": 6.0, "capK2": 6.0, "tr": 88.76, "tp": 2.177, "RUN": 0.5, "A0": [-3.61735, -83.24731, -20.74558], "A0m": [-1.59219, -68.36688, -16.89539], "Bm": [-24.73342, -78.69992, -21.80667], "eE": [-0.02416, -0.97047, -0.23999], "psiA": -64.199, "thLo": 33.405, "thHi": 83.5867, "q2s": [88.4143, -5.0112], "lawTh": [83.587, 84.334, 85.091, 85.856, 86.628, 87.409, 88.195, 88.989, 89.788, 90.593, 91.402, 92.216, 93.034, 93.855, 94.68, 95.507, 96.336, 97.166, 97.998, 98.83, 99.662, 100.494, 101.325, 102.154, 102.982, 103.807, 104.629, 105.447, 106.261, 107.071, 107.876, 108.674, 109.467, 110.252, 111.03, 111.799, 112.56, 113.311, 114.052, 114.783, 115.501, 116.208, 116.902], "lawDK": [-0.0, -1.272, -2.544, -3.816, -5.087, -6.359, -7.631, -8.903, -10.175, -11.447, -12.718, -13.99, -15.262, -16.534, -17.806, -19.078, -20.349, -21.621, -22.893, -24.165, -25.437, -26.709, -27.98, -29.252, -30.524, -31.796, -33.068, -34.34, -35.612, -36.883, -38.155, -39.427, -40.699, -41.971, -43.243, -44.514, -45.786, -47.058, -48.33, -49.602, -50.874, -52.145, -53.417], "lawQ2": [-5.011, -5.411, -5.811, -6.211, -6.611, -7.011, -7.411, -7.811, -8.211, -8.611, -9.011, -9.411, -9.811, -10.211, -10.611, -11.011, -11.411, -11.811, -12.211, -12.611, -13.011, -13.411, -13.811, -14.211, -14.611, -15.011, -15.411, -15.811, -16.211, -16.611, -17.011, -17.411, -17.811, -18.211, -18.611, -19.011, -19.411, -19.811, -20.211, -20.611, -21.011, -21.411, -21.811], "lawThF": [33.405, 33.247, 33.089, 32.93, 32.771, 32.612, 32.452, 32.292, 32.131, 31.97, 31.809, 31.647, 31.485, 31.322, 31.159, 30.996, 30.832, 30.668, 30.504, 30.339, 30.174, 30.009, 29.843, 29.677, 29.51, 29.343, 29.176, 29.009, 28.841, 28.672, 28.504, 28.335, 28.166, 27.996, 27.826, 27.656, 27.485, 27.315, 27.143, 26.972, 26.8], "lawDK2F": [-0.0, -0.35, -0.701, -1.051, -1.402, -1.752, -2.102, -2.453, -2.803, -3.154, -3.504, -3.854, -4.205, -4.555, -4.906, -5.256, -5.606, -5.957, -6.307, -6.658, -7.008, -7.358, -7.709, -8.059, -8.41, -8.76, -9.11, -9.461, -9.811, -10.162, -10.512, -10.862, -11.213, -11.563, -11.914, -12.264, -12.614, -12.965, -13.315, -13.666, -14.016], "lawQ2F": [88.414, 88.814, 89.214, 89.614, 90.014, 90.414, 90.814, 91.214, 91.614, 92.014, 92.414, 92.814, 93.214, 93.614, 94.014, 94.414, 94.814, 95.214, 95.614, 96.014, 96.414, 96.814, 97.214, 97.614, 98.014, 98.414, 98.814, 99.214, 99.614, 100.014, 100.414, 100.814, 101.214, 101.614, 102.014, 102.414, 102.814, 103.214, 103.614, 104.014, 104.414], "rocker": [-27.923, 48.614, 23.52], "rockerAx": [-0.45929, 0.79962, 0.38687], "rodA": [-32.057, 55.811, 27.002], "rodB": [-24.699, 67.612, 1.62], "L1a": [[0.42, 43.39, 17.42], [-2.39, 44.81, 15.42], [-5.33, 46.48, 13.4], [-8.4, 48.02, 11.21], [-11.6, 49.32, 8.82], [-14.87, 50.28, 6.23], [-18.1, 50.64, 3.43]], "L1b": [[-20.82, 50.56, 2.13], [-21.93, 50.0, 5.75], [-22.93, 49.16, 9.36], [-23.86, 48.15, 12.97], [-24.7, 46.95, 16.56], [-25.49, 45.59, 20.15], [-26.23, 44.12, 23.76], [-26.94, 42.52, 27.4], [-27.62, 40.79, 31.1], [-28.01, 38.56, 34.56]], "L2a": [[-27.56, 37.77, 36.16], [-25.45, 37.04, 39.23], [-23.23, 36.17, 42.22], [-20.92, 35.24, 45.24], [-18.41, 34.02, 47.98], [-15.81, 32.71, 50.71], [-13.09, 31.28, 53.36], [-10.3, 29.83, 56.13]], "L2b": [[-8.17, 27.94, 58.67], [-8.41, 25.01, 60.49], [-8.6, 21.89, 61.94], [-8.8, 18.74, 63.45], [-9.0, 15.54, 64.98], [-9.15, 12.19, 66.13], [-9.26, 8.75, 67.04], [-9.4, 5.28, 68.16], [-9.58, 1.73, 69.53], [-9.7, -1.95, 70.5], [-9.74, -5.7, 70.88], [-9.75, -9.48, 71.06], [-9.68, -13.24, 70.66], [-9.53, -16.87, 69.65], [-9.54, -20.82, 69.77], [-9.6, -25.09, 70.37], [-9.65, -29.51, 70.82], [-9.7, -34.19, 71.3]], "rocker2": [-20.67, 38.029, 53.421], "rocker2Ax": [-0.30064, 0.55311, 0.77697], "rod2A": [-23.376, 43.007, 60.413], "rod2B": [-7.848, 37.367, 74.434]};
  const u = G.u, c = G.c, uK = G.uK, uK2 = G.uK2, sn = G.sn, sa = G.sa, st = G.st, a1 = G.A[0], a2 = G.A[1], hub = 12.25, rad = 10;
  const wrapR = a => { a = (a + Math.PI) % (2 * Math.PI); return (a < 0 ? a + 2 * Math.PI : a) - Math.PI; };
  const pe = P.phiE * D2R, pb = P.phib * D2R, lE = P.lE, lc = P.lc;
  const A02 = [G.m[0] + lE * Math.cos(pe), G.m[1] + lE * Math.sin(pe)], B2 = [A02[0] + lc * Math.cos(pb), A02[1] + lc * Math.sin(pb)];
  const kbr = Math.sign(wrapR(pe - Math.atan2(B2[1] - G.m[1], B2[0] - G.m[0]))) || 1;
  const vref = V.unit(V.cross(u[2], [0.3, 0.5, 0.8]));
  const cb = x => Math.cos(x * D2R);
  const dot = V.dot;
  function interp(T, A, B, th, rising) {
    const n = T.length; let j = 0;
    if (rising) { while (j < n - 2 && T[j + 1] < th) j++; } else { while (j < n - 2 && T[j + 1] > th) j++; }
    const a = Math.max(0, Math.min(1, (th - T[j]) / ((T[j + 1] - T[j]) || 1e-9)));
    return [A[j] + a * (A[j + 1] - A[j]), B[j] + a * (B[j + 1] - B[j])];
  }
  /** state 0: K and K2 on stop A (plain 3R); state 1: K opens (stretched law); state -1: K2 bends (folded law) */
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
      return { q1: pick[0], dK: 0, q2: pick[1], dK2: 0, ok: g2 > 0, L: { state: 0 } };
    }
    if (th > G.thHi) {
      const [q2s, dK] = interp(G.lawTh, G.lawQ2, G.lawDK, th, true), ok = th <= G.lawTh[G.lawTh.length - 1];
      const p = M.mulv(M.rot(u2, q2s), u3), q1 = K.axisAngle(u1, M.mulv(M.rot(uK, dK), p), w);
      return { q1, dK, q2: q2s, dK2: 0, ok, L: { state: 1 } };
    }
    const T = G.lawThF; const ok = T.length > 1 && th >= T[T.length - 1];
    const [q2s, dK2] = T.length > 1 ? interp(T, G.lawQ2F, G.lawDK2F, th, false) : [G.q2s[0], 0];
    const p = M.mulv(M.rot(u2, q2s), M.mulv(M.rot(uK2, dK2), u3));
    return { q1: K.axisAngle(u1, p, w), dK: 0, q2: q2s, dK2, ok, L: { state: -1 } };
  }
  function chain(q1, dK, q2, dK2, q3) {
    const R1 = M.rot(u[0], q1), R1b = M.mul(R1, M.rot(uK, dK)), R2a = M.mul(R1b, M.rot(u[1], q2)), R12 = M.mul(R2a, M.rot(uK2, dK2));
    const R3 = M.rot(u[2], q3), R123 = M.mul(R12, R3), t3 = M.mulv(R12, V.sub(c[2], M.mulv(R3, c[2])));
    return { R1, R1b, R2a, R12, R123, t3 };
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
    const Q = Qof(ctx), k = ik(Q), R12 = chain(k.q1, k.dK, k.q2, k.dK2, 0).R12;
    const q3 = K.axisAngle(u[2], vref, M.mulv(M.T(R12), M.mulv(Q, vref))), X = chain(k.q1, k.dK, k.q2, k.dK2, q3);
    const sv = M.mulv(M.T(Q), X.t3), s = [V.dot(sv, sa), V.dot(sv, st), V.dot(sv, sn)], kn = knee(s);
    const R = x => K.wrap180(x / D2R);
    return [k.q1, k.dK, k.q2, k.dK2, K.wrap180(q3 + kn.phi / D2R), R(wrapR(kn.psi - pb - kn.phi)), R(wrapR(kn.psi - pb))];
  }
  function fk(q) {
    const X = chain(q[0], q[1], q[2], q[3], q[4]), Rm3 = X.R123, pa = V.add(M.mulv(Rm3, G.A0), X.t3);
    const R6 = M.mul(Rm3, M.rot(sn, q[5])), t6 = V.sub(pa, M.mulv(R6, G.A0m));
    const pbW = V.add(M.mulv(R6, G.Bm), t6), R5 = M.mul(R6, M.rot(sn, -q[6])), t5 = V.sub(pbW, M.mulv(R5, G.Bm));
    return Object.assign(X, { Rm3, R6, t6, R5, t5, pa, pb: pbW });
  }
  const check = (q, ctx) => {
    const Q = Qof(ctx), k = ik(Q);
    if (!k.ok) return k.L.state === 1 ? 'past the K drive stop B' : (k.L.state === -1 ? 'folded past the K2 law end (rate / margin / stop B2)' : 'chain cannot close');
    const F = fk(q), sv = M.mulv(M.T(Q), F.t3), kn = knee([V.dot(sv, sa), V.dot(sv, st)]);
    if (!kn.span) return 'knee span: the drift is beyond lE + lc';
    if (kn.ang < P.ang_min || kn.ang > 180 - P.ang_min) return `knee angle ${kn.ang.toFixed(0)} deg outside [${P.ang_min}, ${180 - P.ang_min}]`;
    return null;
  };
  const closes = (q, ctx) => { const r = C.residual(q, ctx); return Math.max(...r.map(Math.abs)) <= 0.5; };
  const solveC = (ctx, qPrev) => { const q = solve(ctx); return (!qPrev || closes(q, ctx)) ? q : K.dls(C, ctx, qPrev, { iters: 40 }).q; };
  const C = {
    id: 'split-knuckle-twosided-3r', name: 'Split two-sided knuckle: K (link 1, stretched) + K2 (link 2, folded), both slaved to q2 by pushrods (3 active)',
    dof: { active: 3, passive: 4 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'K (passive, slaved: stretched lobe)', 'J2', 'K2 (passive, slaved: folded lobe)', 'J3', 'knee pin a', 'knee pin b'],
    qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve: solveC,
    residual: (q, ctx) => { const F = fk(q); return M.rotErrDeg(F.R5, Qof(ctx)).concat(F.t5); },
    check,
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), F = fk(q);
      const on = (R, p) => W(M.mulv(R, p));
      const h1 = { kind: 'hub', role: 'active', name: 'J1 (axis on a GH ray)', c: W(V.scale(u[0], G.f[0])), axis: Wd(u[0]), r: rad, h: hub };
      const hK = { kind: 'hub', role: 'passive', name: 'K (O20, slaved; clock-spring cap + pushrod horn, stretched end)', c: on(F.R1, V.scale(uK, G.fK)), axis: Wd(M.mulv(F.R1, uK)), r: rad, h: hub + (G.capK || 0) };
      const h2 = { kind: 'hub', role: 'active', name: 'J2 (rotor-rim lobe for K, stator lobe for K2)', c: on(F.R1b, V.scale(u[1], G.f[1])), axis: Wd(M.mulv(F.R1b, u[1])), r: rad, h: hub };
      const hK2 = { kind: 'hub', role: 'passive', name: 'K2 (O20, slaved; clock-spring cap + pushrod horn, folded end)', c: on(F.R2a, V.scale(uK2, G.fK2)), axis: Wd(M.mulv(F.R2a, uK2)), r: rad, h: hub + (G.capK2 || 0) };
      const h3 = { kind: 'hub', role: 'active', name: 'J3 (skin-normal tilt, line misses GH)', c: on(F.R12, V.madd(c[2], u[2], G.f[2])), axis: Wd(M.mulv(F.R12, u[2])), r: rad, h: hub, p0: on(F.R12, c[2]) };
      const n3 = Wd(M.mulv(F.Rm3, sn)), lvl = (p, h) => V.madd(W(p), n3, h), kz = G.tr + G.tp + G.RUN + G.tp / 2;
      const rim = W(V.add(M.mulv(F.Rm3, V.add(V.madd(c[2], sn, G.f[2] + 1.5), V.scale(G.eE, rad))), F.t3));
      const arm = p => M.mulv(ctx.H, p), padC = arm(V.madd(G.Bm, sn, G.tr + G.tp / 2)), padN = M.mulv(ctx.H, sn), lat = arm([G.Bm[0], -150, 50]);
      const out = [
        { kind: 'plate', role: 'fixed-scapula', name: 'base on the scapula handler', c: V.madd(h1.c, h1.axis, -3), z: h1.axis, x: ctx.attach.scapDir([1, 0, 0]), size: [40, 30], t: 3 },
        h1,
        { kind: 'arc', role: 'link', name: 'link 1a (8 x 3 strap, J1 -> K)', pts: G.L1a.map(p => on(F.R1, p)), r: 2.5 },
        hK,
        { kind: 'arc', role: 'link', name: 'link 1b (8 x 3 strap, K -> J2)', pts: G.L1b.map(p => on(F.R1b, p)), r: 2.5 },
        h2,
        { kind: 'arc', role: 'link', name: 'link 2a (8 x 3 strap, J2 -> K2)', pts: G.L2a.map(p => on(F.R2a, p)), r: 2.5 },
        hK2,
        { kind: 'arc', role: 'link', name: 'link 2b (8 x 3 strap, K2 -> J3)', pts: G.L2b.map(p => on(F.R12, p)), r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'rocker (on link 1b; follows the K lobe on hub 2 rotor rim)', c: on(F.R1b, G.rocker), axis: Wd(M.mulv(F.R1b, G.rockerAx)), r: 5, h: 9 },
        { kind: 'link', role: 'link', name: 'O3 pushrod + M3 rod ends (rocker -> horn on K cap)', a: on(F.R1b, G.rodA), b: on(F.R1b, G.rodB), r: 1.5 },
        { kind: 'hub', role: 'passive', name: 'rocker 2 (on link 2a; follows the K2 lobe on hub 2 stator)', c: on(F.R2a, G.rocker2), axis: Wd(M.mulv(F.R2a, G.rocker2Ax)), r: 5, h: 9 },
        { kind: 'link', role: 'link', name: 'O3 pushrod 2 + M3 rod ends (rocker 2 -> horn on K2)', a: on(F.R2a, G.rod2A), b: on(F.R2a, G.rod2B), r: 1.5 },
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
      return out;
    }
  };
  K.register(C);
})();
