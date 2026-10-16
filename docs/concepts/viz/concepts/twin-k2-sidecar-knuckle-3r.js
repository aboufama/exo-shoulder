/* twin-k2-sidecar-knuckle-3r: the verified lead sidecar-longdyad-knuckle-3r (K on link 1 slaved by the strap-level sidecar:
 * hub-2 rim lobe -> bell crank on link 1b -> O3 rod -> horn lug on link 1a) PLUS a second slaved knuckle K2 on link 2,
 * bk3 from J2 on the bend side: lobe 2 on link 1b's side of hub 2 -> crank 2 on link 2a -> O3 rod 2 -> horn lug on link 2b.
 * Up to the lead's drive wall (m3e = 5 at th ~109.5) the chain is the lead pose for pose; past it K dwells at dK1cap and K2
 * opens (track law, monotone in q2), so a2e = arc(J2, J3) grows and th reaches ~122. J1, J2, J3 encoders give the pose
 * (3 active; K and K2 never read). Geometry exported from docs/concepts/models/twin-k2-sidecar-knuckle-3r.py (viz mode);
 * at its best honest configuration (CMA run A, drive-2 metal on: Bench(60,160) fast 60.86); screened DEAD (hub K2 parks 0.09-0.34 in band, crank 1 / crank 2 / hub 1 collisions - see the .md). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 96.6954, "el1": 67.5865, "az2": 42.0125, "el2": 46.6363, "wd": 64.7883, "wa": -4.751, "b3": 0.3283, "lE": 67.832, "lc": 25.6915, "phiE": -2.7863, "phib": -60.7036, "stk": 4.8534, "ang_min": 26.8823, "bk1": 28.9414, "bk2": 39.236, "sK": -1, "a1max": 63.177400000000006, "smhi": 16.5464, "smlo": 5.0, "capK": 6.0, "kK": 1.6232, "r_h": 16.4668, "La": 18.4032, "s_arm": 4.3872, "bk3": 24.5926, "bk4": 49.1561, "sK2": 1, "kK2": 0.7934, "smt2": 5.0, "dK1cap": 38.035, "dK2max": 40.0, "capK2": 6.0, "r_h2": 16.6924, "La2": 16.4865, "s_arm2": 4.4};
  const G = {"u": [[0.04445, 0.92446, 0.37869], [-0.46683, 0.68311, 0.56163], [-0.03034, -0.25108, 0.96749]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-1.80556, -13.80253, -3.63863]], "uK": [-0.2633, 0.96463, -0.01303], "uK2": [-0.14897, 0.55826, 0.81618], "sa": [0.00787, -0.96797, -0.25096], "st": [0.99951, 0.0, 0.03135], "sn": [-0.03034, -0.25108, 0.96749], "A": [34.57, 67.293], "branch": -1.0, "m": [-13.05579, 1.9181, 0.0], "f": [48.89, 60.44, 80.39], "fK": 55.34, "fK2": 64.18, "capK": 6.0, "capK2": 6.0, "tr": 88.61, "tp": 2.177, "RUN": 0.5, "A0": [-4.56809, -79.38397, -20.74484], "A0m": [-2.75369, -66.74641, -17.40826], "Bm": [-25.04929, -78.91525, -21.2655], "eE": [-0.04073, -0.96682, -0.25218], "psiA": -61.5918, "thLo": 37.7235, "thHi": 85.3164, "q2s": [85.3631, -6.1336], "lawTh": [85.316, 85.73, 86.148, 86.57, 86.996, 87.425, 87.857, 88.293, 88.732, 89.175, 89.62, 90.068, 90.52, 90.974, 91.43, 91.89, 92.351, 92.815, 93.282, 93.75, 94.221, 94.693, 95.168, 95.644, 96.122, 96.601, 97.082, 97.564, 98.047, 98.531, 99.016, 99.503, 99.99, 100.477, 100.965, 101.454, 101.943, 102.432, 102.921, 103.41, 103.899, 104.388, 104.876, 105.364, 105.851, 106.338, 106.823, 107.308, 107.791, 108.274, 108.754, 109.234, 109.711, 110.187, 110.661, 111.133, 111.603, 112.07, 112.535, 112.866, 113.015, 113.163, 113.308, 113.452, 113.578, 113.699, 113.819, 113.939, 114.057, 114.174], "lawDK": [-0.0, -0.649, -1.299, -1.948, -2.597, -3.246, -3.896, -4.545, -5.194, -5.844, -6.493, -7.142, -7.791, -8.441, -9.09, -9.739, -10.388, -11.038, -11.687, -12.336, -12.986, -13.635, -14.284, -14.933, -15.583, -16.232, -16.881, -17.531, -18.18, -18.829, -19.478, -20.128, -20.777, -21.426, -22.076, -22.725, -23.374, -24.023, -24.673, -25.322, -25.971, -26.62, -27.27, -27.919, -28.568, -29.218, -29.867, -30.516, -31.165, -31.815, -32.464, -33.113, -33.763, -34.412, -35.061, -35.71, -36.36, -37.009, -37.658, -38.035, -38.035, -38.035, -38.035, -38.035, -38.035, -38.035, -38.035, -38.035, -38.035, -38.035], "lawDK2": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.419, 0.92, 1.421, 1.921, 2.422, 2.923], "lawQ2": [-6.134, -6.534, -6.934, -7.334, -7.734, -8.134, -8.534, -8.934, -9.334, -9.734, -10.134, -10.534, -10.934, -11.334, -11.734, -12.134, -12.534, -12.934, -13.334, -13.734, -14.134, -14.534, -14.934, -15.334, -15.734, -16.134, -16.534, -16.934, -17.334, -17.734, -18.134, -18.534, -18.934, -19.334, -19.734, -20.134, -20.534, -20.934, -21.334, -21.734, -22.134, -22.534, -22.934, -23.334, -23.734, -24.134, -24.534, -24.934, -25.334, -25.734, -26.134, -26.534, -26.934, -27.334, -27.734, -28.134, -28.534, -28.934, -29.334, -29.734, -30.134, -30.534, -30.934, -31.334, -31.734, -32.134, -32.534, -32.934, -33.334, -33.734], "rocker": [-25.085, 51.371, 21.83], "rockerAx": [-0.40992, 0.83947, 0.35674], "rodA": [-42.312, 49.216, 15.095], "rodB": [-31.373, 58.189, -7.757], "L1a": [[1.62, 46.55, 18.25], [-0.82, 47.59, 15.4], [-3.24, 48.34, 12.46], [-5.65, 48.8, 9.45], [-8.14, 49.61, 6.46], [-10.74, 50.62, 3.38], [-13.31, 51.07, 0.14]], "L1b": [[-14.4, 51.2, 0.17], [-15.98, 50.75, 3.64], [-17.53, 50.15, 7.13], [-19.01, 49.32, 10.63], [-20.47, 48.34, 14.14], [-21.82, 47.06, 17.63], [-23.15, 45.64, 21.14], [-24.51, 44.18, 24.74], [-25.75, 42.39, 28.3], [-26.95, 40.39, 31.87]], "L2a": [[-28.12, 41.98, 35.39], [-25.33, 41.23, 38.26], [-22.44, 40.3, 40.97], [-19.44, 39.19, 43.5], [-16.36, 37.91, 45.84], [-13.21, 36.47, 47.97], [-10.02, 34.95, 50.02]], "L2b": [[-9.46, 34.82, 52.47], [-9.33, 31.83, 54.36], [-9.18, 28.74, 56.08], [-9.0, 25.56, 57.62], [-8.86, 22.5, 59.5], [-8.73, 19.38, 61.45], [-8.54, 16.08, 63.07], [-8.35, 12.7, 64.72], [-8.15, 9.23, 66.45], [-7.83, 5.54, 67.21], [-7.49, 1.81, 67.89], [-7.16, -1.99, 68.64], [-6.86, -5.91, 69.82], [-6.46, -9.89, 70.23], [-6.03, -13.91, 70.34], [-5.55, -17.9, 69.93], [-5.08, -22.02, 69.75], [-4.66, -26.62, 70.53], [-4.19, -31.39, 71.05]], "rocker2": [-15.033, 50.076, 44.228], "rocker2Ax": [-0.21952, 0.73124, 0.64583], "rod2A": [-5.96, 64.707, 39.959], "rod2B": [-1.137, 52.865, 53.481]};
  const u = G.u, c = G.c, uK = G.uK, uK2 = G.uK2, sn = G.sn, sa = G.sa, st = G.st, a1 = G.A[0], a2 = G.A[1], hub = 12.25, rad = 10;
  const wrapR = a => { a = (a + Math.PI) % (2 * Math.PI); return (a < 0 ? a + 2 * Math.PI : a) - Math.PI; };
  const pe = P.phiE * D2R, pb = P.phib * D2R, lE = P.lE, lc = P.lc;
  const A02 = [G.m[0] + lE * Math.cos(pe), G.m[1] + lE * Math.sin(pe)], B2 = [A02[0] + lc * Math.cos(pb), A02[1] + lc * Math.sin(pb)];
  const kbr = Math.sign(wrapR(pe - Math.atan2(B2[1] - G.m[1], B2[0] - G.m[0]))) || 1;
  const vref = V.unit(V.cross(u[2], [0.3, 0.5, 0.8]));
  const cb = x => Math.cos(x * D2R);
  const dot = V.dot;
  function interp(T, A, B, Cc, th) {
    const n = T.length; let j = 0;
    while (j < n - 2 && T[j + 1] < th) j++;
    const a = Math.max(0, Math.min(1, (th - T[j]) / ((T[j + 1] - T[j]) || 1e-9)));
    return [A[j] + a * (A[j + 1] - A[j]), B[j] + a * (B[j + 1] - B[j]), Cc[j] + a * (Cc[j + 1] - Cc[j])];
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
      const [q2s, dK, dK2] = interp(G.lawTh, G.lawQ2, G.lawDK, G.lawDK2, th), ok = th <= G.lawTh[G.lawTh.length - 1];
      const p = M.mulv(M.rot(u2, q2s), M.mulv(M.rot(uK2, dK2), u3)), q1 = K.axisAngle(u1, M.mulv(M.rot(uK, dK), p), w);
      return { q1, dK, q2: q2s, dK2, ok, L: { state: dK2 > 1e-6 ? 2 : 1 } };
    }
    /* folded past the lead's physical q2 stop (th < thLo): no folded law in this design */
    const p = M.mulv(M.rot(u2, G.q2s[0]), u3);
    return { q1: K.axisAngle(u1, p, w), dK: 0, q2: G.q2s[0], dK2: 0, ok: false, L: { state: -1 } };
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
    if (!k.ok) return k.L.state >= 1 ? 'stretched past the twin law end (K2 rate / dyad margin / dK2max)' : (k.L.state === -1 ? 'folded past the lead q2 stop' : 'chain cannot close');
    const F = fk(q), sv = M.mulv(M.T(Q), F.t3), kn = knee([V.dot(sv, sa), V.dot(sv, st)]);
    if (!kn.span) return 'knee span: the drift is beyond lE + lc';
    if (kn.ang < P.ang_min || kn.ang > 180 - P.ang_min) return `knee angle ${kn.ang.toFixed(0)} deg outside [${P.ang_min}, ${180 - P.ang_min}]`;
    return null;
  };
  const closes = (q, ctx) => { const r = C.residual(q, ctx); return Math.max(...r.map(Math.abs)) <= 0.5; };
  const solveC = (ctx, qPrev) => { const q = solve(ctx); return (!qPrev || closes(q, ctx)) ? q : K.dls(C, ctx, qPrev, { iters: 40 }).q; };
  const C = {
    id: 'twin-k2-sidecar-knuckle-3r', name: 'Twin knuckle: the sidecar lead + K2 on link 2 opened past the drive wall by lobe 2 (3 active)',
    dof: { active: 3, passive: 4 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'K (passive, slaved: sidecar RSSR)', 'J2', 'K2 (passive, slaved: lobe 2 + rod 2, stretched end)', 'J3', 'knee pin a', 'knee pin b'],
    qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve: solveC,
    residual: (q, ctx) => { const F = fk(q); return M.rotErrDeg(F.R5, Qof(ctx)).concat(F.t5); },
    check,
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), F = fk(q);
      const on = (R, p) => W(M.mulv(R, p));
      const h1 = { kind: 'hub', role: 'active', name: 'J1 (axis on a GH ray)', c: W(V.scale(u[0], G.f[0])), axis: Wd(u[0]), r: rad, h: hub };
      const hK = { kind: 'hub', role: 'passive', name: 'K (O20, slaved by the sidecar RSSR; clock-spring cap)', c: on(F.R1, V.scale(uK, G.fK)), axis: Wd(M.mulv(F.R1, uK)), r: rad, h: hub + (G.capK || 0) };
      const h2 = { kind: 'hub', role: 'active', name: 'J2 (rotor-rim lobe 1 for K, stator-side lobe 2 for K2)', c: on(F.R1b, V.scale(u[1], G.f[1])), axis: Wd(M.mulv(F.R1b, u[1])), r: rad, h: hub };
      const hK2 = { kind: 'hub', role: 'passive', name: 'K2 (O20, slaved by lobe 2 + rod 2; clock-spring cap, opens past the drive wall)', c: on(F.R2a, V.scale(uK2, G.fK2)), axis: Wd(M.mulv(F.R2a, uK2)), r: rad, h: hub + (G.capK2 || 0) };
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
        { kind: 'hub', role: 'passive', name: 'bell crank 1 (MR63ZZ pair on link 1b; follows lobe 1 on hub 2 rim)', c: on(F.R1b, G.rocker), axis: Wd(M.mulv(F.R1b, G.rockerAx)), r: 5, h: 6 },
        { kind: 'link', role: 'link', name: 'O3 rod 1 + M2 ball links (crank 1 -> horn lug of link 1a at K)', a: on(F.R1b, G.rodA), b: on(F.R1, G.rodB), r: 1.5 },
        { kind: 'hub', role: 'passive', name: 'bell crank 2 (MR63ZZ pair on link 2a; follows lobe 2 on link 1b side of hub 2)', c: on(F.R2a, G.rocker2), axis: Wd(M.mulv(F.R2a, G.rocker2Ax)), r: 5, h: 6 },
        { kind: 'link', role: 'link', name: 'O3 rod 2 + M2 ball links (crank 2 -> horn lug of link 2b at K2)', a: on(F.R2a, G.rod2A), b: on(F.R12, G.rod2B), r: 1.5 },
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
