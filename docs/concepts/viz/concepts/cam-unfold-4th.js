/* cam-unfold-4th - the pin-knee chain (J1 / J2 on GH rays, J3 tilted toward the skin normal, a flat two-pin knee closing
 * member 3 on the cuff) with LINK 2 split by a 4th, PASSIVE, SLAVED O20 hub K: a groove face cam (O30 flange on link 1
 * around hub 2) drives K through a follower lever and a pushrod on link 2a, so K = c(q2) - no sensor, no spring, no spare
 * coordinate (3 active). The coupled chain's J1-J3 angle th is a function of q2 alone; the model's exact table th(x),
 * x = position of q2 on the design's branch, is inverted per frame, then K = sign(psiA) c(x), q1 and q3 in closed form.
 * Exactly docs/concepts/models/cam-unfold-4th.py at the CMA best S2 (27.07 near-touch fast on Bench(60,160)) (axis directions, line points, hub levels, knee level,
 * link centrelines and the th(x) table exported from the model's fit on Bench(60,160)). Red = th outside the cam window
 * (J2 on a slot end) / the knee outside its window. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 93.5249, "el1": 60.8297, "az2": 35.3296, "el2": 41.5211, "wd": 62.1057, "wa": -9.9748, "b3": 0.2393, "lE": 63.5787, "lc": 25.6805, "phiE": -8.8629, "phib": -51.5292, "stk": 5.6815, "ang_min": 30.4611, "bk1": 29.1547, "bk2": 45.9392, "sK": 1, "mons": 20.8695, "ws": 74.835, "cs": 24.9671, "monf": 5.0, "wf": 19.5935, "cf": 1.7785};
  const G = {"u": [[0.02997, 0.87317, 0.48649], [-0.58802, 0.60295, 0.53916], [-0.12919, -0.34, 0.93151]], "uK": [-0.2495, 0.42857, 0.86838], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-0.42004, -10.59507, -3.92543]], "sa": [0.04671, -0.94043, -0.33677], "st": [0.99052, 0.0, 0.13738], "sn": [-0.12919, -0.34, 0.93151], "A": [39.543, 68.087], "branch": -1.0, "m": [-9.59357, 0.94701, 0.0], "f": [51.47, 61.16, 83.03], "fK": 65.58, "tr": 97.59, "tp": 2.591, "RUN": 0.5, "SING": 5.0, "camR": 15.0, "A0": [-7.18858, -69.67222, -26.42717], "A0m": [-6.69865, -60.65018, -23.0662], "Bm": [-25.86771, -75.67465, -31.2087], "eE": [-0.10646, -0.9292, -0.35392], "eK": [-0.74644, -0.58505, -0.31707], "psiA": 131.9708, "q2f": 103.25, "d": -1.0, "xs": 113.052, "xf": 22.507, "cam": {"cs": 24.9671, "ws": 74.835, "cf": 1.7785, "wf": 19.5935}, "tx": [22.6, 23.4, 24.2, 25.0, 25.8, 26.6, 27.4, 28.2, 29.0, 29.8, 30.6, 31.4, 32.2, 33.0, 33.8, 34.6, 35.4, 36.2, 37.0, 37.8, 38.6, 39.4, 40.2, 41.0, 41.8, 42.6, 43.4, 44.2, 45.0, 45.8, 46.6, 47.4, 48.2, 49.0, 49.8, 50.6, 51.4, 52.2, 53.0, 53.8, 54.6, 55.4, 56.2, 57.0, 57.8, 58.6, 59.4, 60.2, 61.0, 61.8, 62.6, 63.4, 64.2, 65.0, 65.8, 66.6, 67.4, 68.2, 69.0, 69.8, 70.6, 71.4, 72.2, 73.0, 73.8, 74.6, 75.4, 76.2, 77.0, 77.8, 78.6, 79.4, 80.2, 81.0, 81.8, 82.6, 83.4, 84.2, 85.0, 85.8, 86.6, 87.4, 88.2, 89.0, 89.8, 90.6, 91.4, 92.2, 93.0, 93.8, 94.6, 95.4, 96.2, 97.0, 97.8, 98.6, 99.4, 100.2, 101.0, 101.8, 102.6, 103.4, 104.2, 105.0, 105.8, 106.6, 107.4, 108.2, 109.0, 109.8, 110.6, 111.4, 112.2, 113.0, 113.8, 114.6, 115.4, 116.2, 117.0, 117.8, 118.6, 119.4, 120.2, 121.0, 121.8, 122.6, 123.4, 124.2, 125.0, 125.8, 126.6, 127.4, 128.2, 129.0, 129.8, 130.6, 131.4, 132.2, 133.0, 133.8, 134.6, 135.4, 136.2, 137.0, 137.8, 138.6, 139.4, 140.2, 141.0, 141.8, 142.6, 143.4, 144.2, 145.0, 145.8, 146.6, 147.4, 148.2, 149.0, 149.8, 150.6, 151.4, 152.2, 153.0, 153.8, 154.6, 155.4, 156.2, 157.0, 157.8], "tth": [33.582, 33.915, 34.255, 34.603, 34.958, 35.32, 35.69, 36.066, 36.448, 36.837, 37.232, 37.632, 38.038, 38.449, 38.866, 39.287, 39.713, 40.144, 40.579, 41.018, 41.461, 41.908, 42.359, 42.814, 43.272, 43.733, 44.197, 44.664, 45.134, 45.607, 46.082, 46.56, 47.04, 47.523, 48.007, 48.494, 48.982, 49.473, 49.965, 50.458, 50.954, 51.45, 51.948, 52.447, 52.948, 53.449, 53.952, 54.456, 54.96, 55.465, 55.971, 56.477, 56.984, 57.492, 58.0, 58.508, 59.017, 59.526, 60.035, 60.545, 61.054, 61.563, 62.072, 62.582, 63.091, 63.599, 64.108, 64.616, 65.124, 65.631, 66.138, 66.644, 67.149, 67.654, 68.159, 68.662, 69.165, 69.666, 70.167, 70.667, 71.166, 71.664, 72.161, 72.656, 73.151, 73.644, 74.135, 74.626, 75.115, 75.602, 76.088, 76.573, 77.056, 77.537, 78.016, 78.494, 78.97, 79.444, 79.916, 80.386, 80.854, 81.32, 81.784, 82.246, 82.705, 83.163, 83.618, 84.07, 84.52, 84.968, 85.413, 85.855, 86.295, 86.732, 87.165, 87.593, 88.015, 88.433, 88.845, 89.253, 89.656, 90.055, 90.449, 90.839, 91.225, 91.607, 91.984, 92.358, 92.729, 93.095, 93.458, 93.817, 94.173, 94.526, 94.875, 95.221, 95.564, 95.904, 96.24, 96.574, 96.904, 97.232, 97.556, 97.878, 98.197, 98.513, 98.826, 99.136, 99.444, 99.749, 100.051, 100.351, 100.647, 100.941, 101.233, 101.522, 101.808, 102.092, 102.373, 102.651, 102.927, 103.2, 103.471, 103.739, 104.004, 104.267, 104.527, 104.785, 105.04, 105.293], "th_win": [33.58, 105.48], "L1": [[0.61, 42.21, 23.8], [-2.84, 42.73, 25.24], [-6.46, 43.06, 26.64], [-10.31, 43.43, 28.14], [-14.41, 43.7, 29.66], [-18.63, 43.51, 30.96], [-22.83, 42.65, 31.88], [-26.76, 40.99, 32.24], [-30.61, 39.01, 32.4], [-34.43, 36.85, 32.45]], "L2a": [[-34.75, 35.97, 33.12], [-32.24, 34.73, 35.75], [-29.81, 33.56, 38.4], [-27.63, 32.66, 41.37], [-25.48, 31.84, 44.54], [-23.13, 30.82, 47.54], [-20.57, 29.59, 50.33], [-17.93, 28.3, 53.15]], "L2b": [[-15.9, 26.56, 55.8], [-16.02, 23.7, 58.05], [-16.11, 20.71, 60.25], [-16.06, 17.46, 61.97], [-15.97, 14.1, 63.57], [-15.9, 10.67, 65.29], [-15.75, 7.09, 66.75], [-15.49, 3.38, 67.82], [-15.24, -0.41, 68.96], [-14.98, -4.33, 70.1], [-14.66, -8.36, 71.06], [-14.2, -12.44, 71.45], [-13.72, -16.61, 71.75], [-13.16, -20.81, 71.76], [-12.46, -24.89, 71.04], [-11.67, -28.83, 69.84], [-11.05, -33.32, 69.73]]};
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
