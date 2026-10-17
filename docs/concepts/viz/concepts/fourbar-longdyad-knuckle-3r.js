/* fourbar-longdyad-knuckle-3r at its best screened configuration (family-reading best of the coarse farm sweep, Bench(60,160) fast gap 55.94): the lead's chain on the 28/50 K dyad (J1, link 1a,
 * passive O20 knuckle K, link 1b, J2, link 2, J3 with b3, member 3, the two-pin knee) with the K drive replaced by a POSITIVE
 * SPHERICAL FOUR-BAR on ground link 1b: a crank pin on a lug of link 2 (turns with q2), a Ti coupler arc concentric with GH
 * stacked over link 1b, and a horn pin on a lug of link 1a beside hub K. All four axes through GH; K = f(q2) both ways, no spring,
 * no sliding pair. 3 active (J1, J2, J3), K slaved and never read, 0 passive translations.
 * Geometry exported from docs/concepts/models/fourbar-longdyad-knuckle-3r.py (mode viz). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 95.3929, "el1": 67.8974, "az2": 45.8211, "el2": 41.0855, "wd": 66.8662, "wa": -10.6559, "b3": 0.329, "lE": 70.3417, "lc": 22.9611, "phiE": -3.0093, "phib": -54.13, "stk": 4.8534, "ang_min": 26.88, "bk1": 32.0, "bk2": 48.0, "sK": -1, "a1max": 74.5, "smhi": 16.8433, "smlo": 5.0, "capK": 6.0, "rc": 11.4671, "gc": 37.0997, "rh": 21.3376, "c": 36.9376, "br": 1.0, "k0": 33.645, "hl": 0.0, "zc": 0.0, "zcp": 0.306, "b1read": "family", "clay": 0};
  const G = {"u": [[0.03536, 0.92651, 0.3746], [-0.46545, 0.61682, 0.63474], [-0.13912, -0.22062, 0.96539]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-0.73949, -13.44608, -3.17939]], "uK": [-0.27616, 0.95785, -0.07913], "sa": [0.03147, -0.97536, -0.21836], "st": [0.98978, 0.0, 0.14263], "sn": [-0.13912, -0.22062, 0.96539], "A": [37.552, 57.218], "branch": -1.0, "m": [-13.68552, 1.18367, 0.0], "f": [50.47, 80.07, 79.13], "fK": 57.39, "capK": 6.0, "tr": 87.68, "tp": 2.177, "RUN": 0.5, "A0": [-2.18414, -81.95994, -19.04504], "A0m": [-1.44321, -68.61163, -15.88778], "Bm": [-19.43611, -81.73414, -21.47951], "eE": [-0.02054, -0.97401, -0.22555], "lawTh": [10.967, 11.64, 12.357, 13.111, 13.898, 14.712, 15.55, 16.409, 17.286, 18.18, 19.087, 20.007, 20.939, 21.88, 22.83, 23.789, 24.755, 25.728, 26.706, 27.69, 28.679, 29.672, 30.669, 31.669, 32.672, 33.678, 34.686, 35.696, 36.707, 37.719, 38.733, 39.746, 40.76, 41.774, 42.787, 43.8, 44.812, 45.822, 46.831, 47.837, 48.842, 49.844, 50.844, 51.84, 52.834, 53.824, 54.81, 55.792, 56.77, 57.744, 58.713, 59.677, 60.636, 61.59, 62.538, 63.48, 64.417, 65.347, 66.271, 67.188, 68.099, 69.003, 69.9, 70.789, 71.671, 72.546, 73.413, 74.272, 75.123, 75.966, 76.801, 77.627, 78.445, 79.254, 80.054, 80.846, 81.628, 82.402, 83.166, 83.921, 84.667, 85.403, 86.13, 86.847, 87.554, 88.251, 88.938, 89.616, 90.283, 90.94, 91.587, 92.223, 92.849, 93.464, 94.069, 94.663, 95.246, 95.819, 96.38, 96.93, 97.47, 97.998, 98.514, 99.02, 99.514, 99.996, 100.467, 100.925, 101.373, 101.808, 102.231, 102.642, 103.041, 103.427, 103.802, 104.163, 104.513, 104.849, 105.173, 105.484, 105.782], "lawDK": [-26.817, -27.363, -27.91, -28.457, -29.005, -29.552, -30.1, -30.647, -31.194, -31.74, -32.285, -32.83, -33.374, -33.916, -34.457, -34.996, -35.534, -36.07, -36.603, -37.134, -37.662, -38.188, -38.71, -39.229, -39.744, -40.256, -40.763, -41.266, -41.765, -42.259, -42.748, -43.231, -43.709, -44.181, -44.647, -45.106, -45.559, -46.005, -46.444, -46.876, -47.3, -47.716, -48.124, -48.524, -48.915, -49.297, -49.67, -50.034, -50.389, -50.734, -51.069, -51.394, -51.708, -52.012, -52.306, -52.589, -52.861, -53.121, -53.371, -53.609, -53.836, -54.052, -54.255, -54.447, -54.627, -54.795, -54.951, -55.095, -55.227, -55.347, -55.455, -55.55, -55.634, -55.705, -55.764, -55.811, -55.845, -55.868, -55.878, -55.876, -55.862, -55.837, -55.799, -55.749, -55.688, -55.614, -55.529, -55.433, -55.325, -55.205, -55.074, -54.932, -54.778, -54.614, -54.438, -54.252, -54.054, -53.846, -53.628, -53.398, -53.159, -52.909, -52.649, -52.379, -52.099, -51.809, -51.51, -51.2, -50.881, -50.553, -50.216, -49.869, -49.513, -49.148, -48.774, -48.391, -48.0, -47.6, -47.191, -46.775, -46.349], "lawQ2": [114.568, 113.568, 112.568, 111.568, 110.568, 109.568, 108.568, 107.568, 106.568, 105.568, 104.568, 103.568, 102.568, 101.568, 100.568, 99.568, 98.568, 97.568, 96.568, 95.568, 94.568, 93.568, 92.568, 91.568, 90.568, 89.568, 88.568, 87.568, 86.568, 85.568, 84.568, 83.568, 82.568, 81.568, 80.568, 79.568, 78.568, 77.568, 76.568, 75.568, 74.568, 73.568, 72.568, 71.568, 70.568, 69.568, 68.568, 67.568, 66.568, 65.568, 64.568, 63.568, 62.568, 61.568, 60.568, 59.568, 58.568, 57.568, 56.568, 55.568, 54.568, 53.568, 52.568, 51.568, 50.568, 49.568, 48.568, 47.568, 46.568, 45.568, 44.568, 43.568, 42.568, 41.568, 40.568, 39.568, 38.568, 37.568, 36.568, 35.568, 34.568, 33.568, 32.568, 31.568, 30.568, 29.568, 28.568, 27.568, 26.568, 25.568, 24.568, 23.568, 22.568, 21.568, 20.568, 19.568, 18.568, 17.568, 16.568, 15.568, 14.568, 13.568, 12.568, 11.568, 10.568, 9.568, 8.568, 7.568, 6.568, 5.568, 4.568, 3.568, 2.568, 1.568, 0.568, -0.432, -1.432, -2.432, -3.432, -4.432, -5.432], "pcB": [-0.29296, 0.71763, 0.63181], "ph0": [-0.24291, 0.92622, 0.28828], "levC": 83.2, "levH": 57.4, "cplC": 86.7, "cplH": 64.8, "L1a": [[-1.93, 50.71, 9.49], [-5.56, 54.71, 5.1], [-4.45, 49.02, 8.7], [-8.9, 57.75, 4.8], [-7.25, 50.45, 8.46], [-6.61, 49.62, 12.62], [-10.56, 53.55, 8.46]], "L1b": [[-22.52, 56.96, 2.93], [-23.08, 53.36, 7.33], [-25.0, 53.0, 12.05], [-26.9, 52.36, 16.91], [-30.28, 54.1, 23.07], [-34.33, 56.22, 30.39], [-37.71, 56.4, 37.73], [-20.35, 53.88, 4.86], [-22.18, 53.52, 9.46], [-24.03, 53.03, 14.2], [-25.66, 51.87, 18.95], [-27.88, 51.62, 24.33], [-32.03, 54.23, 31.94], [-37.68, 58.16, 42.0], [-19.4, 53.89, 6.93], [-21.26, 53.65, 11.59], [-23.04, 53.03, 16.36], [-24.43, 51.38, 20.96], [-26.71, 51.35, 26.54], [-32.09, 56.29, 35.94], [-18.0, 58.42, 4.83], [-18.53, 54.12, 9.04], [-20.31, 53.71, 13.71], [-21.96, 52.83, 18.46], [-23.16, 50.8, 22.92], [-26.85, 53.69, 30.24], [-31.97, 58.25, 40.13]], "L2": [[-40.86, 42.37, 59.97], [-34.45, 28.54, 59.0], [-32.84, 19.49, 65.13], [-29.92, 9.45, 68.73], [-25.94, -0.82, 69.63], [-21.41, -10.66, 68.38], [-19.58, -23.23, 77.1], [-32.31, 29.89, 57.04], [-30.92, 21.28, 63.4], [-28.31, 11.59, 67.5], [-24.63, 1.5, 68.92], [-20.32, -8.3, 68.15], [-17.83, -19.78, 74.52], [-30.21, 31.11, 55.06], [-29.05, 22.95, 61.68], [-26.68, 13.61, 66.11], [-23.28, 3.74, 68.05], [-19.27, -5.99, 67.97], [-16.16, -16.53, 71.81], [-30.36, 34.69, 57.2], [-27.22, 24.51, 59.94], [-25.13, 15.55, 64.81], [-21.95, 5.91, 67.11], [-18.19, -3.72, 67.6], [-14.56, -13.51, 69.0]]};
  const u = G.u, c = G.c, uK = G.uK, sn = G.sn, sa = G.sa, st = G.st, hub = 12.25, rad = 10;
  const wrapR = a => { a = (a + Math.PI) % (2 * Math.PI); return (a < 0 ? a + 2 * Math.PI : a) - Math.PI; };
  const pe = P.phiE * D2R, pb = P.phib * D2R, lE = P.lE, lc = P.lc;
  const A02 = [G.m[0] + lE * Math.cos(pe), G.m[1] + lE * Math.sin(pe)], B2 = [A02[0] + lc * Math.cos(pb), A02[1] + lc * Math.sin(pb)];
  const kbr = Math.sign(wrapR(pe - Math.atan2(B2[1] - G.m[1], B2[0] - G.m[0]))) || 1;
  const vref = V.unit(V.cross(u[2], [0.3, 0.5, 0.8]));
  /** the four-bar law: th (deg) -> (q2, dK) on the window, every pose forced (K never parked on a stop) */
  function ik(Q) {
    const [u1, u2, u3] = u, w = M.mulv(Q, u3), th = V.angle(w, u1);
    const T = G.lawTh, n = T.length; let j = 0;
    while (j < n - 2 && T[j + 1] < th) j++;
    const ok = th >= T[0] && th <= T[n - 1], a = Math.max(0, Math.min(1, (th - T[j]) / Math.max(T[j + 1] - T[j], 1e-9)));
    const q2s = G.lawQ2[j] + a * (G.lawQ2[j + 1] - G.lawQ2[j]), dK = G.lawDK[j] + a * (G.lawDK[j + 1] - G.lawDK[j]);
    const p = M.mulv(M.rot(u2, q2s), u3), q1 = K.axisAngle(u1, M.mulv(M.rot(uK, dK), p), w);
    return { q1, dK, q2: q2s, ok };
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
    if (!k.ok) return 'outside the four-bar window (horn transmission < 48, K stops, rate or dyad margin)';
    const F = fk(q), sv = M.mulv(M.T(Q), F.t3), kn = knee([V.dot(sv, sa), V.dot(sv, st)]);
    if (!kn.span) return 'knee span: the drift is beyond lE + lc';
    if (kn.ang < P.ang_min || kn.ang > 180 - P.ang_min) return `knee angle ${kn.ang.toFixed(0)} deg outside [${P.ang_min}, ${180 - P.ang_min}]`;
    return null;
  };
  const closes = (q, ctx) => { const r = C.residual(q, ctx); return Math.max(...r.map(Math.abs)) <= 0.5; };
  const solveC = (ctx, qPrev) => { const q = solve(ctx); return (!qPrev || closes(q, ctx)) ? q : K.dls(C, ctx, qPrev, { iters: 40 }).q; };
  const slerp = (a, b, f) => { const om = Math.acos(Math.max(-1, Math.min(1, V.dot(a, b)))) || 1e-9; return V.add(V.scale(a, Math.sin((1 - f) * om) / Math.sin(om)), V.scale(b, Math.sin(f * om) / Math.sin(om))); };
  const C = {
    id: 'fourbar-longdyad-knuckle-3r', name: 'Toggle four-bar knuckle: crank pin on link 2 -> Ti coupler arc over link 1b -> horn pin on link 1a; K slaved to q2 (3 active, K not read)',
    dof: { active: 3, passive: 5 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'K (passive, slaved to q2 by the spherical four-bar)', 'J2', 'J3', 'knee pin a', 'knee pin b'], qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve: solveC,
    residual: (q, ctx) => { const F = fk(q); return M.rotErrDeg(F.R5, Qof(ctx)).concat(F.t5); },
    check,
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), F = fk(q);
      const on = (R, p) => W(M.mulv(R, p));
      const h1 = { kind: 'hub', role: 'active', name: 'J1 (axis on a GH ray)', c: W(V.scale(u[0], G.f[0])), axis: Wd(u[0]), r: rad, h: hub };
      const hK = { kind: 'hub', role: 'passive', name: 'K (O20, passive, slaved by the four-bar; plain cap, stops A / B as over-travel stops only)', c: on(F.R1, V.scale(uK, G.fK)), axis: Wd(M.mulv(F.R1, uK)), r: rad, h: hub };
      const h2 = { kind: 'hub', role: 'active', name: 'J2 (axis on a GH ray)', c: on(F.R1b, V.scale(u[1], G.f[1])), axis: Wd(M.mulv(F.R1b, u[1])), r: rad, h: hub };
      const h3 = { kind: 'hub', role: 'active', name: 'J3 (skin-normal tilt, line misses GH)', c: on(F.R12, V.madd(c[2], u[2], G.f[2])), axis: Wd(M.mulv(F.R12, u[2])), r: rad, h: hub,
                   p0: on(F.R12, c[2]) };
      const n3 = Wd(M.mulv(F.Rm3, sn)), lvl = (p, h) => V.madd(W(p), n3, h), kz = G.tr + G.tp + G.RUN + G.tp / 2;
      const rim = W(V.add(M.mulv(F.Rm3, V.add(V.madd(c[2], sn, G.f[2] + 1.5), V.scale(G.eE, rad))), F.t3));
      const arm = p => M.mulv(ctx.H, p), padC = arm(V.madd(G.Bm, sn, G.tr + G.tp / 2)), padN = M.mulv(ctx.H, sn), lat = arm([G.Bm[0], -150, 50]);
      // four-bar: crank pin rigid with link 2, horn pin rigid with link 1a, coupler between them (a rigid arc about GH)
      const pcW = V.unit(on(F.R12, G.pcB)), phW = V.unit(on(F.R1, G.ph0)), u2W = V.unit(on(F.R1b, u[1])), uKW = V.unit(on(F.R1, uK));
      const cpl = [0, 0.25, 0.5, 0.75, 1].map(f => V.scale(V.unit(slerp(pcW, phW, f)), G.cplC * (1 - f) + G.cplH * f + 1.5));
      const lugC0 = V.scale(V.unit(V.madd(V.scale(u2W, G.levC), V.unit(V.sub(pcW, V.scale(u2W, V.dot(pcW, u2W)))), rad + 0.5)), Math.hypot(G.levC, rad + 0.5) + 1.5);
      const lugH0 = V.scale(V.unit(V.madd(V.scale(uKW, G.levH), V.unit(V.sub(phW, V.scale(uKW, V.dot(phW, uKW)))), rad + 0.5)), Math.hypot(G.levH, rad + 0.5) + 1.5);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base on the scapula handler', c: V.madd(h1.c, h1.axis, -3), z: h1.axis, x: ctx.attach.scapDir([1, 0, 0]), size: [40, 30], t: 3 },
        h1,
        { kind: 'arc', role: 'link', name: 'link 1a (8 x 3 strap, J1 -> K)', pts: (G.L1a.length ? G.L1a : [V.scale(u[0], G.f[0]), V.scale(uK, G.fK)]).map(p => on(F.R1, p)), r: 2.5 },
        hK,
        { kind: 'arc', role: 'link', name: 'link 1b (8 x 3 strap, K -> J2; ground link of the four-bar)', pts: G.L1b.map(p => on(F.R1b, p)), r: 2.5 },
        h2,
        { kind: 'arc', role: 'link', name: 'link 2 (8 x 3 strap, fitted)', pts: G.L2.map(p => on(F.R12, p)), r: 2.5 },
        { kind: 'link', role: 'link', name: 'crank lug of link 2 (3 mm Ti, formed, turns with q2)', a: lugC0, b: V.scale(pcW, Math.hypot(G.levC, rad + 0.5) + 1.5), r: 1.5 },
        { kind: 'hub', role: 'passive', name: 'crank pin (ISO 8734 3 m6 dowel, MR63ZZ eye, radial through GH)', c: V.scale(pcW, G.levC), axis: pcW, r: 4.5, h: G.cplC + 3 - G.levC },
        { kind: 'arc', role: 'link', name: 'coupler (3 x 4 mm Ti arc concentric with GH, stacked over link 1b with 1 mm clearance)', pts: cpl, r: 1.5 },
        { kind: 'hub', role: 'passive', name: 'horn pin (ISO 8734 3 m6 dowel, MR63ZZ eye, radial through GH)', c: V.scale(phW, G.levH), axis: phW, r: 4.5, h: G.cplH + 3 - G.levH },
        { kind: 'link', role: 'link', name: 'horn lug of link 1a at hub K (3 mm Ti, formed)', a: lugH0, b: V.scale(phW, Math.hypot(G.levH, rad + 0.5) + 1.5), r: 1.5 },
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
