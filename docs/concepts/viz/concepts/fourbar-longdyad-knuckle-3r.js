/* fourbar-longdyad-knuckle-3r at its best screened configuration (family-reading (today's B1 reading) best after coarse farm sweeps + CMA-ES, Bench(60,160) fast gap 53.26; coupled-reading best 34.56 is listed for B1): the lead's chain on the 28/50 K dyad (J1, link 1a,
 * passive O20 knuckle K, link 1b, J2, link 2, J3 with b3, member 3, the two-pin knee) with the K drive replaced by a POSITIVE
 * SPHERICAL FOUR-BAR on ground link 1b: a crank pin on a lug of link 2 (turns with q2), a Ti coupler arc concentric with GH
 * stacked over link 1b, and a horn pin on a lug of link 1a beside hub K. All four axes through GH; K = f(q2) both ways, no spring,
 * no sliding pair. 3 active (J1, J2, J3), K slaved and never read, 0 passive translations.
 * Geometry exported from docs/concepts/models/fourbar-longdyad-knuckle-3r.py (mode viz). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 95.3929, "el1": 67.8974, "az2": 45.8211, "el2": 41.0855, "wd": 66.8662, "wa": -10.6559, "b3": 0.329, "lE": 74.6624, "lc": 23.6082, "phiE": -5.6614, "phib": -60.1937, "stk": 4.8534, "ang_min": 26.88, "bk1": 32.0, "bk2": 48.0, "sK": -1, "a1max": 74.5, "smhi": 16.8433, "smlo": 5.0, "capK": 6.0, "rc": 10.4867, "gc": 35.9713, "rh": 21.1051, "c": 37.1553, "br": 1.0, "k0": 34.2689, "hl": 0.0, "zc": 0.0, "zcp": 0.7024, "b1read": "family", "clay": 0};
  const G = {"u": [[0.03536, 0.92651, 0.3746], [-0.46545, 0.61682, 0.63474], [-0.13912, -0.22062, 0.96539]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-0.73949, -13.44608, -3.17939]], "uK": [-0.27616, 0.95785, -0.07913], "sa": [0.03147, -0.97536, -0.21836], "st": [0.98978, 0.0, 0.14263], "sn": [-0.13912, -0.22062, 0.96539], "A": [37.552, 57.218], "branch": -1.0, "m": [-13.68315, 1.18367, 0.0], "f": [50.47, 80.16, 79.11], "fK": 57.41, "capK": 6.0, "tr": 87.47, "tp": 2.177, "RUN": 0.5, "A0": [-5.69163, -85.91358, -20.45401], "A0m": [-4.95064, -72.56759, -17.29727], "Bm": [-24.85702, -84.01335, -22.78155], "eE": [-0.06633, -0.9706, -0.23137], "lawTh": [10.39, 11.076, 11.804, 12.568, 13.361, 14.18, 15.02, 15.88, 16.756, 17.646, 18.549, 19.463, 20.387, 21.32, 22.26, 23.208, 24.162, 25.121, 26.085, 27.054, 28.027, 29.004, 29.983, 30.965, 31.95, 32.937, 33.925, 34.915, 35.906, 36.897, 37.889, 38.881, 39.873, 40.865, 41.856, 42.846, 43.835, 44.822, 45.808, 46.792, 47.774, 48.754, 49.731, 50.705, 51.676, 52.644, 53.608, 54.569, 55.526, 56.478, 57.427, 58.37, 59.31, 60.244, 61.173, 62.097, 63.015, 63.928, 64.835, 65.736, 66.631, 67.52, 68.402, 69.278, 70.147, 71.009, 71.864, 72.712, 73.553, 74.386, 75.212, 76.03, 76.84, 77.642, 78.436, 79.222, 80.0, 80.77, 81.531, 82.283, 83.027, 83.762, 84.488, 85.205, 85.913, 86.612, 87.302, 87.982, 88.653, 89.314, 89.966, 90.608, 91.241, 91.863, 92.475, 93.078, 93.67, 94.252, 94.824, 95.385, 95.935, 96.475, 97.005, 97.523, 98.031, 98.528, 99.013, 99.488, 99.951, 100.403, 100.843, 101.272, 101.689, 102.094, 102.488, 102.869, 103.239, 103.597, 103.942, 104.275, 104.596, 104.904], "lawDK": [-27.611, -28.117, -28.622, -29.128, -29.633, -30.138, -30.642, -31.145, -31.648, -32.15, -32.651, -33.15, -33.649, -34.145, -34.64, -35.133, -35.623, -36.112, -36.597, -37.081, -37.561, -38.038, -38.512, -38.982, -39.449, -39.912, -40.37, -40.825, -41.275, -41.72, -42.16, -42.595, -43.024, -43.448, -43.866, -44.278, -44.683, -45.082, -45.475, -45.86, -46.239, -46.61, -46.973, -47.329, -47.676, -48.016, -48.348, -48.67, -48.985, -49.29, -49.586, -49.874, -50.151, -50.42, -50.679, -50.928, -51.167, -51.396, -51.615, -51.824, -52.022, -52.211, -52.388, -52.555, -52.712, -52.857, -52.992, -53.116, -53.229, -53.332, -53.423, -53.504, -53.573, -53.632, -53.679, -53.716, -53.741, -53.756, -53.759, -53.752, -53.734, -53.705, -53.665, -53.614, -53.553, -53.481, -53.399, -53.305, -53.202, -53.088, -52.963, -52.829, -52.684, -52.529, -52.364, -52.189, -52.004, -51.809, -51.605, -51.391, -51.168, -50.935, -50.692, -50.441, -50.18, -49.911, -49.632, -49.344, -49.048, -48.743, -48.43, -48.108, -47.777, -47.439, -47.092, -46.737, -46.374, -46.003, -45.625, -45.238, -44.844, -44.443], "lawQ2": [115.318, 114.318, 113.318, 112.318, 111.318, 110.318, 109.318, 108.318, 107.318, 106.318, 105.318, 104.318, 103.318, 102.318, 101.318, 100.318, 99.318, 98.318, 97.318, 96.318, 95.318, 94.318, 93.318, 92.318, 91.318, 90.318, 89.318, 88.318, 87.318, 86.318, 85.318, 84.318, 83.318, 82.318, 81.318, 80.318, 79.318, 78.318, 77.318, 76.318, 75.318, 74.318, 73.318, 72.318, 71.318, 70.318, 69.318, 68.318, 67.318, 66.318, 65.318, 64.318, 63.318, 62.318, 61.318, 60.318, 59.318, 58.318, 57.318, 56.318, 55.318, 54.318, 53.318, 52.318, 51.318, 50.318, 49.318, 48.318, 47.318, 46.318, 45.318, 44.318, 43.318, 42.318, 41.318, 40.318, 39.318, 38.318, 37.318, 36.318, 35.318, 34.318, 33.318, 32.318, 31.318, 30.318, 29.318, 28.318, 27.318, 26.318, 25.318, 24.318, 23.318, 22.318, 21.318, 20.318, 19.318, 18.318, 17.318, 16.318, 15.318, 14.318, 13.318, 12.318, 11.318, 10.318, 9.318, 8.318, 7.318, 6.318, 5.318, 4.318, 3.318, 2.318, 1.318, 0.318, -0.682, -1.682, -2.682, -3.682, -4.682, -5.682], "pcB": [-0.30711, 0.70811, 0.63582], "ph0": [-0.24291, 0.92743, 0.28436], "levC": 83.3, "levH": 57.4, "cplC": 87.2, "cplH": 65.3, "L1a": [[-1.93, 50.71, 9.49], [-5.56, 54.72, 5.1], [-4.45, 49.02, 8.7], [-8.9, 57.76, 4.8], [-7.25, 50.47, 8.47], [-6.61, 49.62, 12.62], [-10.57, 53.56, 8.46]], "L1b": [[-22.68, 56.95, 3.23], [-23.29, 53.33, 7.77], [-25.26, 52.91, 12.67], [-27.18, 52.12, 17.69], [-31.34, 54.99, 24.65], [-34.7, 55.59, 31.65], [-39.73, 57.89, 40.9], [-21.07, 53.62, 6.75], [-23.03, 53.34, 11.59], [-24.82, 52.46, 16.49], [-26.68, 51.49, 21.6], [-29.97, 52.8, 28.26], [-35.77, 57.36, 38.18], [-19.03, 54.25, 5.79], [-20.84, 53.73, 10.53], [-22.69, 53.16, 15.44], [-24.11, 51.44, 20.17], [-26.48, 51.47, 25.9], [-31.99, 56.6, 35.51], [-18.1, 58.43, 5.15], [-18.7, 54.13, 9.5], [-20.5, 53.6, 14.34], [-22.16, 52.54, 19.22], [-23.4, 50.43, 23.85], [-28.39, 55.62, 32.9], [-33.67, 59.84, 43.44]], "L2": [[-40.93, 42.4, 60.03], [-33.92, 28.08, 58.06], [-32.45, 19.24, 64.32], [-29.69, 9.36, 68.16], [-25.87, -0.82, 69.38], [-21.4, -10.66, 68.29], [-19.59, -23.24, 77.07], [-31.83, 29.43, 56.17], [-30.55, 21.02, 62.64], [-28.07, 11.48, 66.91], [-24.53, 1.49, 68.63], [-20.3, -8.29, 68.04], [-17.84, -19.78, 74.52], [-30.21, 31.11, 55.07], [-28.71, 22.69, 60.97], [-26.44, 13.49, 65.52], [-23.17, 3.73, 67.74], [-19.23, -5.98, 67.84], [-16.16, -16.54, 71.85], [-30.41, 34.78, 57.34], [-26.88, 24.23, 59.24], [-24.9, 15.43, 64.26], [-21.83, 5.89, 66.8], [-18.12, -3.71, 67.43], [-14.56, -13.52, 69.07]]};
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
