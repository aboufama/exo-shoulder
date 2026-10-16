/* twin-k2-sidecar-knuckle-3r: the verified lead sidecar-longdyad-knuckle-3r (K on link 1 slaved by the strap-level sidecar:
 * hub-2 rim lobe -> bell crank on link 1b -> O3 rod -> horn lug on link 1a) PLUS a second slaved knuckle K2 on link 2,
 * bk3 from J2 on the bend side: lobe 2 on link 1b's side of hub 2 -> crank 2 on link 2a -> O3 rod 2 -> horn lug on link 2b.
 * Up to the lead's drive wall (m3e = 5 at th ~109.5) the chain is the lead pose for pose; past it K dwells at dK1cap and K2
 * opens (track law, monotone in q2), so a2e = arc(J2, J3) grows and th reaches ~122. J1, J2, J3 encoders give the pose
 * (3 active; K and K2 never read). Geometry exported from docs/concepts/models/twin-k2-sidecar-knuckle-3r.py (viz mode);
 * screened DEAD (hub K2 parks 0.09-0.34 in band, crank 1 / crank 2 / hub 1 collisions - see the .md). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 96.6954, "el1": 67.5865, "az2": 42.2031, "el2": 44.4209, "wd": 67.5003, "wa": -7.3175, "b3": 0.345, "lE": 67.832, "lc": 25.6915, "phiE": -2.7863, "phib": -60.7036, "stk": 4.8534, "ang_min": 26.8823, "bk1": 28.9414, "bk2": 39.236, "sK": -1, "a1max": 63.177400000000006, "smhi": 16.5464, "smlo": 5.0, "capK": 6.0, "kK": 1.6232, "r_h": 14.8706, "La": 16.5467, "s_arm": 4.3872, "bk3": 22.0, "bk4": 59.0, "sK2": 1, "kK2": 0.0, "smt2": 5.0, "dK1cap": 43.0, "dK2max": 40.0, "capK2": 6.0, "r_h2": 15.5, "La2": 16.5, "s_arm2": 4.4};
  const G = {"u": [[0.04445, 0.92446, 0.37869], [-0.4799, 0.65501, 0.58366], [-0.07591, -0.20566, 0.97567]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-1.54432, -13.6309, -2.99343]], "uK": [-0.29434, 0.95562, 0.0126], "uK2": [-0.11662, 0.73057, 0.6728], "sa": [0.01595, -0.97862, -0.20504], "st": [0.99699, 0.0, 0.07757], "sn": [-0.07591, -0.20566, 0.97567], "A": [36.369, 61.889], "branch": -1.0, "m": [-12.57011, 1.76235, 0.0], "f": [49.72, 60.34, 78.56], "fK": 55.38, "fK2": 59.55, "capK": 6.0, "capK2": 6.0, "tr": 86.17, "tp": 2.177, "RUN": 0.5, "A0": [-3.75088, -79.93436, -17.14129], "A0m": [-2.19438, -67.63296, -14.42716], "Bm": [-24.33186, -79.93578, -18.74291], "eE": [-0.03253, -0.97747, -0.20857], "psiA": -65.4036, "thLo": 30.5201, "thHi": 81.7112, "q2s": [90.0564, -3.8399], "lawTh": [81.711, 82.696, 83.697, 84.713, 85.742, 86.783, 87.836, 88.898, 89.969, 91.048, 92.133, 93.224, 94.318, 95.415, 96.514, 97.613, 98.711, 99.807, 100.899, 101.987, 103.068, 104.142, 105.206, 106.261, 107.303, 108.332, 109.346, 110.372, 111.404, 112.432, 113.066, 113.403, 113.739, 114.073, 114.407, 114.738, 115.07, 115.399, 115.728, 116.054, 116.379, 116.702, 117.025, 117.345, 117.662, 117.977, 118.289, 118.6, 118.908, 119.213, 119.516, 119.825, 120.123, 120.417, 120.709, 120.998, 121.284, 121.566, 121.846, 122.122, 122.395], "lawDK": [-0.0, -1.461, -2.922, -4.383, -5.844, -7.304, -8.765, -10.226, -11.687, -13.148, -14.609, -16.07, -17.531, -18.991, -20.452, -21.913, -23.374, -24.835, -26.296, -27.757, -29.218, -30.678, -32.139, -33.6, -35.061, -36.522, -37.983, -39.444, -40.905, -42.366, -43.0, -43.0, -43.0, -43.0, -43.0, -43.0, -43.0, -43.0, -43.0, -43.0, -43.0, -43.0, -43.0, -43.0, -43.0, -43.0, -43.0, -43.0, -43.0, -43.0, -43.0, -43.0, -43.0, -43.0, -43.0, -43.0, -43.0, -43.0, -43.0, -43.0, -43.0], "lawDK2": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.933, 2.25, 3.688, 4.75, 5.75, 6.75, 7.695, 8.696, 9.5, 10.5, 11.5, 12.5, 13.455, 14.456, 15.458, 16.25, 17.25, 18.25, 19.25, 20.25, 21.218, 22.22, 23.222, 24.223, 25.0, 26.0, 27.0, 28.0, 29.0, 30.0, 31.0, 32.0, 33.0, 33.99], "lawQ2": [-3.84, -4.74, -5.64, -6.54, -7.44, -8.34, -9.24, -10.14, -11.04, -11.94, -12.84, -13.74, -14.64, -15.54, -16.44, -17.34, -18.24, -19.14, -20.04, -20.94, -21.84, -22.74, -23.64, -24.54, -25.44, -26.34, -27.24, -28.14, -29.04, -29.94, -30.84, -31.74, -32.64, -33.54, -34.44, -35.34, -36.24, -37.14, -38.04, -38.94, -39.84, -40.74, -41.64, -42.54, -43.44, -44.34, -45.24, -46.14, -47.04, -47.94, -48.84, -49.74, -50.64, -51.54, -52.44, -53.34, -54.24, -55.14, -56.04, -56.94, -57.84], "rocker": [-26.336, 49.965, 23.288], "rockerAx": [-0.43107, 0.81785, 0.38118], "rodA": [-42.145, 47.487, 18.203], "rodB": [-32.254, 57.648, -4.588], "L1a": [[1.58, 47.33, 18.61], [-1.15, 48.31, 15.93], [-3.87, 49.0, 13.14], [-6.57, 49.4, 10.28], [-9.25, 49.64, 7.38], [-12.18, 50.75, 4.52], [-15.08, 51.24, 1.46]], "L1b": [[-16.22, 51.26, 1.56], [-17.78, 50.76, 5.09], [-19.25, 49.97, 8.62], [-20.69, 49.06, 12.17], [-22.02, 47.83, 15.69], [-23.3, 46.42, 19.21], [-24.51, 44.81, 22.71], [-25.65, 42.99, 26.2], [-26.76, 41.03, 29.72], [-27.83, 38.9, 33.27]], "L2a": [[-28.42, 40.27, 35.94], [-24.91, 41.43, 37.2], [-21.3, 42.42, 38.31], [-17.6, 43.24, 39.26], [-13.84, 43.88, 40.05], [-10.01, 44.34, 40.68]], "L2b": [[-7.08, 43.46, 41.17], [-7.25, 41.06, 43.53], [-7.4, 38.53, 45.76], [-7.58, 36.18, 48.24], [-7.85, 34.11, 51.27], [-8.03, 31.56, 53.79], [-8.23, 28.97, 56.43], [-8.39, 26.13, 58.85], [-8.48, 22.99, 60.83], [-8.52, 19.68, 62.51], [-8.55, 16.26, 64.07], [-8.63, 12.85, 66.1], [-8.67, 9.27, 67.89], [-8.67, 5.51, 69.38], [-8.65, 1.62, 70.74], [-8.58, -2.39, 71.76], [-8.34, -6.41, 71.3], [-8.06, -10.37, 70.62], [-7.75, -14.25, 69.59], [-7.52, -18.29, 69.24], [-7.41, -22.79, 70.12], [-7.25, -27.41, 70.61]], "rocker2": [-19.819, 55.698, 33.01], "rocker2Ax": [-0.2927, 0.82259, 0.48751], "rod2A": [-19.911, 69.512, 21.842], "rod2B": [-7.421, 60.737, 34.878]};
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
