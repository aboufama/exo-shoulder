/* cam-unfold-4th - the pin-knee chain (J1 / J2 on GH rays, J3 tilted toward the skin normal, a flat two-pin knee closing
 * member 3 on the cuff) with LINK 2 split by a 4th, PASSIVE, SLAVED O20 hub K: a groove face cam (O30 flange on link 1
 * around hub 2) drives K through a follower lever and a pushrod on link 2a, so K = c(q2) - no sensor, no spring, no spare
 * coordinate (3 active). The coupled chain's J1-J3 angle th is a function of q2 alone; the model's exact table th(x),
 * x = position of q2 on the design's branch, is inverted per frame, then K = sign(psiA) c(x), q1 and q3 in closed form.
 * Exactly docs/concepts/models/cam-unfold-4th.py at a provisional screening config (axis directions, line points, hub levels, knee level,
 * link centrelines and the th(x) table exported from the model's fit on Bench(60,160)). Red = th outside the cam window
 * (J2 on a slot end) / the knee outside its window. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 95.4669, "el1": 67.7011, "az2": 47.212, "el2": 39.8943, "wd": 59.8224, "wa": -9.0298, "b3": 0.4579, "lE": 64.6617, "lc": 30.3886, "phiE": -1.5412, "phib": -69.7597, "stk": 5.2691, "ang_min": 24.9512, "bk1": 30.0, "bk2": 45.0, "sK": 1, "mons": 8.0, "ws": 45.0, "cs": 40.0, "monf": 8.0, "wf": 25.0, "cf": 0.0};
  const G = {"u": [[0.03615, 0.92522, 0.37771], [-0.45199, 0.5985, 0.66144], [-0.064, -0.24941, 0.96628]], "uK": [0.01545, 0.5048, 0.8631], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-3.25576, -21.89016, -5.86581]], "sa": [0.01648, -0.9684, -0.24887], "st": [0.99781, 0.0, 0.06609], "sn": [-0.064, -0.24941, 0.96628], "A": [38.072, 58.749], "branch": -1.0, "m": [-18.60078, 3.62885, 0.0], "f": [49.71, 60.92, 80.63], "fK": 70.09, "tr": 88.27, "tp": 2.385, "RUN": 0.5, "SING": 5.0, "camR": 15.0, "A0": [-3.92563, -84.48575, -22.067], "A0m": [-0.61131, -66.4728, -17.19808], "Bm": [-28.88779, -76.65375, -21.69877], "eE": [-0.01036, -0.96805, -0.25055], "eK": [-0.9305, -0.33503, -0.1481], "psiA": 105.3486, "q2f": 121.65, "d": -1.0, "xs": 137.379, "xf": 27.203, "cam": {"cs": 40.0, "ws": 45.0, "cf": 0.0, "wf": 25.0}, "tx": [20.9, 21.8, 22.7, 23.6, 24.5, 25.4, 26.3, 27.2, 28.1, 29.0, 29.9, 30.8, 31.7, 32.6, 33.5, 34.4, 35.3, 36.2, 37.1, 38.0, 38.9, 39.8, 40.7, 41.6, 42.5, 43.4, 44.3, 45.2, 46.1, 47.0, 47.9, 48.8, 49.7, 50.6, 51.5, 52.4, 53.3, 54.2, 55.1, 56.0, 56.9, 57.8, 58.7, 59.6, 60.5, 61.4, 62.3, 63.2, 64.1, 65.0, 65.9, 66.8, 67.7, 68.6, 69.5, 70.4, 71.3, 72.2, 73.1, 74.0, 74.9, 75.8, 76.7, 77.6, 78.5, 79.4, 80.3, 81.2, 82.1, 83.0, 83.9, 84.8, 85.7, 86.6, 87.5, 88.4, 89.3, 90.2, 91.1, 92.0, 92.9, 93.8, 94.7, 95.6, 96.5, 97.4, 98.3, 99.2, 100.1, 101.0, 101.9, 102.8, 103.7, 104.6, 105.5, 106.4, 107.3, 108.2, 109.1, 110.0, 110.9, 111.8, 112.7, 113.6, 114.5, 115.4, 116.3, 117.2, 118.1, 119.0, 119.9, 120.8, 121.7, 122.6, 123.5, 124.4, 125.3, 126.2, 127.1, 128.0, 128.9, 129.8, 130.7, 131.6, 132.5, 133.4, 134.3, 135.2, 136.1, 137.0, 137.9, 138.8, 139.7, 140.6, 141.5, 142.4, 143.3, 144.2, 145.1, 146.0, 146.9, 147.8, 148.7, 149.6, 150.5, 151.4, 152.3, 153.2, 154.1, 155.0, 155.9, 156.8, 157.7, 158.6, 159.5, 160.4, 161.3, 162.2, 163.1, 164.0, 164.9, 165.8, 166.7, 167.6, 168.5, 169.4, 170.3, 171.2, 172.1, 173.0, 173.9], "tth": [25.717, 26.112, 26.517, 26.932, 27.355, 27.787, 28.228, 28.676, 29.131, 29.593, 30.062, 30.537, 31.018, 31.504, 31.996, 32.492, 32.993, 33.499, 34.008, 34.522, 35.039, 35.559, 36.083, 36.609, 37.139, 37.671, 38.205, 38.742, 39.281, 39.822, 40.364, 40.909, 41.454, 42.001, 42.55, 43.099, 43.65, 44.201, 44.754, 45.306, 45.86, 46.414, 46.968, 47.523, 48.078, 48.633, 49.188, 49.743, 50.297, 50.852, 51.406, 51.96, 52.513, 53.066, 53.619, 54.17, 54.721, 55.271, 55.82, 56.369, 56.916, 57.462, 58.007, 58.551, 59.093, 59.634, 60.174, 60.712, 61.249, 61.784, 62.318, 62.85, 63.38, 63.908, 64.435, 64.959, 65.482, 66.002, 66.52, 67.036, 67.55, 68.062, 68.571, 69.078, 69.582, 70.084, 70.583, 71.079, 71.573, 72.064, 72.552, 73.037, 73.52, 73.999, 74.475, 74.948, 75.418, 75.884, 76.347, 76.807, 77.263, 77.716, 78.165, 78.61, 79.052, 79.49, 79.924, 80.354, 80.78, 81.202, 81.62, 82.034, 82.443, 82.848, 83.249, 83.645, 84.037, 84.424, 84.806, 85.184, 85.557, 85.925, 86.288, 86.646, 86.999, 87.346, 87.689, 88.026, 88.358, 88.685, 89.008, 89.336, 89.671, 90.015, 90.366, 90.725, 91.092, 91.466, 91.848, 92.236, 92.63, 93.029, 93.432, 93.838, 94.247, 94.658, 95.068, 95.478, 95.887, 96.294, 96.697, 97.096, 97.49, 97.879, 98.262, 98.639, 99.009, 99.371, 99.727, 100.074, 100.415, 100.748, 101.074, 101.393, 101.705, 102.011, 102.311, 102.606, 102.896, 103.181, 103.463], "th_win": [25.72, 103.49], "L1": [[1.03, 43.3, 18.27], [-1.71, 43.11, 20.58], [-4.55, 42.88, 22.97], [-7.54, 42.65, 25.49], [-10.65, 42.13, 27.99], [-14.02, 41.74, 30.78], [-17.59, 41.09, 33.62], [-21.22, 39.88, 36.27], [-24.62, 37.77, 38.32]], "L2a": [[-26.22, 35.69, 40.0], [-23.24, 35.61, 42.16], [-20.13, 35.38, 44.16], [-16.98, 35.1, 46.12], [-13.74, 34.73, 47.99], [-10.45, 34.36, 49.9], [-7.1, 34.14, 52.11], [-3.61, 33.88, 54.36], [0.07, 33.58, 56.67]], "L2b": [[0.92, 32.73, 57.69], [0.48, 29.73, 59.51], [0.04, 26.81, 61.57], [-0.41, 23.89, 63.86], [-0.86, 20.74, 65.79], [-1.33, 17.44, 67.56], [-1.8, 13.96, 68.91], [-2.27, 10.39, 70.09], [-2.74, 6.74, 71.14], [-3.22, 3.01, 72.05], [-3.72, -0.81, 73.36], [-4.23, -4.76, 74.47], [-4.67, -8.69, 74.12], [-5.06, -12.52, 73.1], [-5.44, -16.28, 71.95], [-5.79, -19.95, 70.55], [-6.12, -23.48, 68.87], [-6.58, -27.56, 68.68], [-7.12, -32.08, 69.08], [-7.67, -36.75, 69.25]]};
  const u = G.u, c = G.c, uK = G.uK, sn = G.sn, sa = G.sa, st = G.st, hub = 12.25, rad = 10;
  const wrapR = a => { a = (a + Math.PI) % (2 * Math.PI); return (a < 0 ? a + 2 * Math.PI : a) - Math.PI; };
  const pe = P.phiE * D2R, pb = P.phib * D2R, lE = P.lE, lc = P.lc;
  const A02 = [G.m[0] + lE * Math.cos(pe), G.m[1] + lE * Math.sin(pe)], B2 = [A02[0] + lc * Math.cos(pb), A02[1] + lc * Math.sin(pb)];
  const kbr = Math.sign(wrapR(pe - Math.atan2(B2[1] - G.m[1], B2[0] - G.m[0]))) || 1;
  const vref = V.unit(V.cross(u[2], [0.3, 0.5, 0.8]));
  const sm = t => { t = Math.max(0, Math.min(1, t)); return t * t * (3 - 2 * t); };
  const camC = x => G.cam.cs * sm((x - G.xs) / Math.max(1, G.cam.ws)) - G.cam.cf * sm((G.xf - x) / Math.max(1, G.cam.wf));
  function interp(v, xs, ys) {
    if (v <= xs[0]) return ys[0];
    if (v >= xs[xs.length - 1]) return ys[ys.length - 1];
    let lo = 0, hi = xs.length - 1;
    while (hi - lo > 1) { const mid = (lo + hi) >> 1; if (xs[mid] <= v) lo = mid; else hi = mid; }
    const f = (v - xs[lo]) / (xs[hi] - xs[lo]); return ys[lo] + f * (ys[hi] - ys[lo]);
  }
  /** the cam law: th -> x (table) -> q2, K = sign(psiA) c(x); q1 from Paden-Kahan about u1 */
  function ik(Q) {
    const [u1, u2, u3] = u, w = M.mulv(Q, u3), th = V.angle(w, u1);
    const inWin = th >= G.th_win[0] && th <= G.th_win[1];
    const x = interp(th, G.tth, G.tx), cc = camC(x), dK = Math.sign(G.psiA) * cc, q2 = G.q2f + G.d * x;
    const p = M.mulv(M.rot(u2, q2), M.mulv(M.rot(uK, dK), u3)), q1 = K.axisAngle(u1, p, w);
    return { q1, q2, dK, ok: inWin, L: { state: cc > 1e-6 ? 1 : (cc < -1e-6 ? -1 : 0), th } };
  }
  function chain(q1, q2, dK, q3) {
    const R1 = M.rot(u[0], q1), R2a = M.mul(R1, M.rot(u[1], q2)), R12 = M.mul(R2a, M.rot(uK, dK)), R3 = M.rot(u[2], q3), R123 = M.mul(R12, R3);
    const t3 = M.mulv(R12, V.sub(c[2], M.mulv(R3, c[2])));
    return { R1, R2a, R12, R123, t3 };
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
    const Q = Qof(ctx), k = ik(Q), R12 = M.mul(M.mul(M.rot(u[0], k.q1), M.rot(u[1], k.q2)), M.rot(uK, k.dK));
    const q3 = K.axisAngle(u[2], vref, M.mulv(M.T(R12), M.mulv(Q, vref))), X = chain(k.q1, k.q2, k.dK, q3);
    const sv = M.mulv(M.T(Q), X.t3), s = [V.dot(sv, sa), V.dot(sv, st), V.dot(sv, sn)], kn = knee(s);
    const R = x => K.wrap180(x / D2R);
    return [k.q1, k.q2, k.dK, K.wrap180(q3 + kn.phi / D2R), R(wrapR(kn.psi - pb - kn.phi)), R(wrapR(kn.psi - pb))];
  }
  function fk(q) {
    const X = chain(q[0], q[1], q[2], q[3]), Rm3 = X.R123, pa = V.add(M.mulv(Rm3, G.A0), X.t3);
    const R6 = M.mul(Rm3, M.rot(sn, q[4])), t6 = V.sub(pa, M.mulv(R6, G.A0m));
    const pbW = V.add(M.mulv(R6, G.Bm), t6), R5 = M.mul(R6, M.rot(sn, -q[5])), t5 = V.sub(pbW, M.mulv(R5, G.Bm));
    return Object.assign(X, { Rm3, R6, t6, R5, t5, pa, pb: pbW });
  }
  const check = (q, ctx) => {
    const Q = Qof(ctx), k = ik(Q);
    if (!k.ok) return `J2 on a slot end: J1-J3 angle ${k.L.th.toFixed(0)} deg outside the cam window [${G.th_win[0]}, ${G.th_win[1]}]`;
    const F = fk(q), sv = M.mulv(M.T(Q), F.t3), kn = knee([V.dot(sv, sa), V.dot(sv, st)]);
    if (!kn.span) return 'knee span: the drift is beyond lE + lc';
    if (kn.ang < P.ang_min || kn.ang > 180 - P.ang_min) return `knee angle ${kn.ang.toFixed(0)} deg outside [${P.ang_min}, ${180 - P.ang_min}]`;
    return null;
  };
  const closes = (q, ctx) => { const r = C.residual(q, ctx); return Math.max(...r.map(Math.abs)) <= 0.5; };
  const solveC = (ctx, qPrev) => { const q = solve(ctx); return (!qPrev || closes(q, ctx)) ? q : K.dls(C, ctx, qPrev, { iters: 40 }).q; };
  const C = {
    id: 'cam-unfold-4th', name: 'Cam-unfolding link: a cam-slaved knee K = c(q2) in link 2 (pin knee closure, sensor-free)',
    dof: { active: 3, passive: 3 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'J2', 'K (passive, slaved by the cam: K = c(q2))', 'J3', 'knee pin a', 'knee pin b'], qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve: solveC,
    residual: (q, ctx) => { const F = fk(q); return M.rotErrDeg(F.R5, Qof(ctx)).concat(F.t5); },
    check,
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), F = fk(q);
      const on = (R, p) => W(M.mulv(R, p));
      const h1 = { kind: 'hub', role: 'active', name: 'J1 (axis on a GH ray)', c: W(V.scale(u[0], G.f[0])), axis: Wd(u[0]), r: rad, h: hub };
      const cam = { kind: 'hub', role: 'link', name: 'cam flange O30 x 3.5 on link 1 (groove 10.6-13.7 mm, outside hub 2 housing)', c: on(F.R1, V.scale(u[1], G.f[1])), axis: Wd(M.mulv(F.R1, u[1])), r: G.camR, h: 3.5 };
      const h2 = { kind: 'hub', role: 'active', name: 'J2 (axis on a GH ray, dowel stops at the cam window ends)', c: on(F.R1, V.scale(u[1], G.f[1])), axis: Wd(M.mulv(F.R1, u[1])), r: rad, h: hub };
      const hK = { kind: 'hub', role: 'passive', name: 'K (O20 pin on a bearing pair, slaved by the cam, not sensed)', c: on(F.R2a, V.scale(uK, G.fK)), axis: Wd(M.mulv(F.R2a, uK)), r: rad, h: hub };
      const h3 = { kind: 'hub', role: 'active', name: 'J3 (skin-normal tilt, line misses GH)', c: on(F.R12, V.madd(c[2], u[2], G.f[2])), axis: Wd(M.mulv(F.R12, u[2])), r: rad, h: hub,
                   p0: on(F.R12, c[2]) };
      const n3 = Wd(M.mulv(F.Rm3, sn)), lvl = (p, h) => V.madd(W(p), n3, h), kz = G.tr + G.tp + G.RUN + G.tp / 2;
      const rim = W(V.add(M.mulv(F.Rm3, V.add(V.madd(c[2], sn, G.f[2] + 1.5), V.scale(G.eE, rad))), F.t3));
      const arm = p => M.mulv(ctx.H, p), padC = arm(V.madd(G.Bm, sn, G.tr + G.tp / 2)), padN = M.mulv(ctx.H, sn), lat = arm([G.Bm[0], -150, 50]);
      const up = (p, h) => V.scale(V.unit(p), V.norm(p) + h);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base on the scapula handler', c: V.madd(h1.c, h1.axis, -3), z: h1.axis, x: ctx.attach.scapDir([1, 0, 0]), size: [40, 30], t: 3 },
        h1,
        { kind: 'arc', role: 'link', name: 'link 1 (8 x 3 strap, J1 -> J2)', pts: G.L1.map(p => on(F.R1, p)), r: 2.5 },
        cam,
        h2,
        { kind: 'arc', role: 'link', name: 'link 2a (8 x 3 strap, J2 -> K; follower lever at J2)', pts: G.L2a.map(p => on(F.R2a, p)), r: 2.5 },
        { kind: 'arc', role: 'link', name: 'pushrod O2 Ti (cam follower -> 4 mm crank on link 2b)', pts: G.L2a.map(p => on(F.R2a, up(p, 4))), r: 1 },
        hK,
        { kind: 'arc', role: 'link', name: 'link 2b (8 x 3 strap, K -> J3)', pts: G.L2b.map(p => on(F.R12, p)), r: 2.5 },
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
