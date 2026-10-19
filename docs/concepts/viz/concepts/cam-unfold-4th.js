/* cam-unfold-4th - the pin-knee chain (J1 / J2 on GH rays, J3 tilted toward the skin normal, a flat two-pin knee closing
 * member 3 on the cuff) with LINK 2 split by a 4th, PASSIVE, SLAVED O20 hub K: a groove face cam (O30 flange on link 1
 * around hub 2) drives K through a follower lever and a pushrod on link 2a, so K = c(q2) - no sensor, no spring, no spare
 * coordinate (3 active). The coupled chain's J1-J3 angle th is a function of q2 alone; the model's exact table th(x),
 * x = position of q2 on the design's branch, is inverted per frame, then K = sign(psiA) c(x), q1 and q3 in closed form.
 * Exactly docs/concepts/models/cam-unfold-4th.py at the CMA best C3 (crown cam, two-sided lobe; 23.23 near-touch fast on Bench(60,160)) (axis directions, line points, hub levels, knee level,
 * link centrelines and the th(x) table exported from the model's fit on Bench(60,160)). Red = th outside the cam window
 * (J2 on a slot end) / the knee outside its window. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 93.002, "el1": 67.5189, "az2": 35.8113, "el2": 48.1385, "wd": 71.5803, "wa": -5.6949, "b3": 0.3015, "lE": 66.4782, "lc": 31.4648, "phiE": -2.9631, "phib": -60.4027, "stk": 5.6815, "ang_min": 30.4611, "bk1": 21.1777, "bk2": 50.6827, "sK": -1, "mons": 13.6962, "ws": 47.4064, "cs": 31.5898, "monf": 15.2912, "wf": 12.8935, "cf": 12.8835};
  const G = {"u": [[0.02003, 0.92401, 0.38185], [-0.50928, 0.69658, 0.50537], [-0.03635, -0.17594, 0.98373]], "uK": [-0.60402, 0.3947, 0.69236], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-2.96191, -10.40077, -1.96958]], "sa": [0.0065, -0.9844, -0.17582], "st": [0.99932, 0.0, 0.03693], "sn": [-0.03635, -0.17594, 0.98373], "A": [34.267, 66.852], "branch": -1.0, "m": [-9.84772, 3.02839, 0.0], "f": [50.68, 59.74, 74.05], "fK": 65.85, "tr": 81.77, "tp": 2.591, "RUN": 0.5, "SING": 5.0, "camR": 10.0, "camH": 3.0, "A0": [-5.96468, -75.75453, -13.76875], "A0m": [-3.00233, -66.06042, -11.92553], "Bm": [-30.24192, -81.35851, -15.66811], "eE": [-0.04517, -0.98309, -0.17749], "eK": [-0.86572, -0.4862, -0.11895], "psiA": -135.0236, "q2f": 102.55000000000001, "d": -1.0, "xs": 122.724, "xf": 48.08, "cam": {"cs": 31.5898, "ws": 47.4064, "cf": 12.8835, "wf": 12.8935}, "tx": [35.2, 35.8, 36.4, 37.0, 37.6, 38.2, 38.8, 39.4, 40.0, 40.6, 41.2, 41.8, 42.4, 43.0, 43.6, 44.2, 44.8, 45.4, 46.0, 46.6, 47.2, 47.8, 48.4, 49.0, 49.6, 50.2, 50.8, 51.4, 52.0, 52.6, 53.2, 53.8, 54.4, 55.0, 55.6, 56.2, 56.8, 57.4, 58.0, 58.6, 59.2, 59.8, 60.4, 61.0, 61.6, 62.2, 62.8, 63.4, 64.0, 64.6, 65.2, 65.8, 66.4, 67.0, 67.6, 68.2, 68.8, 69.4, 70.0, 70.6, 71.2, 71.8, 72.4, 73.0, 73.6, 74.2, 74.8, 75.4, 76.0, 76.6, 77.2, 77.8, 78.4, 79.0, 79.6, 80.2, 80.8, 81.4, 82.0, 82.6, 83.2, 83.8, 84.4, 85.0, 85.6, 86.2, 86.8, 87.4, 88.0, 88.6, 89.2, 89.8, 90.4, 91.0, 91.6, 92.2, 92.8, 93.4, 94.0, 94.6, 95.2, 95.8, 96.4, 97.0, 97.6, 98.2, 98.8, 99.4, 100.0, 100.6, 101.2, 101.8, 102.4, 103.0, 103.6, 104.2, 104.8, 105.4, 106.0, 106.6, 107.2, 107.8, 108.4, 109.0, 109.6, 110.2, 110.8, 111.4, 112.0, 112.6, 113.2, 113.8, 114.4, 115.0, 115.6, 116.2, 116.8, 117.4, 118.0, 118.6, 119.2, 119.8, 120.4, 121.0, 121.6, 122.2, 122.8, 123.4, 124.0, 124.6, 125.2, 125.8, 126.4, 127.0, 127.6, 128.2, 128.8, 129.4, 130.0, 130.6, 131.2, 131.8, 132.4, 133.0, 133.6, 134.2, 134.8, 135.4, 136.0, 136.6, 137.2, 137.8, 138.4, 139.0], "tth": [34.521, 34.794, 35.154, 35.595, 36.111, 36.692, 37.332, 38.022, 38.753, 39.517, 40.304, 41.104, 41.908, 42.706, 43.49, 44.248, 44.971, 45.649, 46.273, 46.833, 47.319, 47.72, 48.043, 48.356, 48.67, 48.986, 49.303, 49.621, 49.94, 50.261, 50.582, 50.905, 51.228, 51.553, 51.878, 52.204, 52.531, 52.859, 53.188, 53.517, 53.847, 54.178, 54.51, 54.842, 55.174, 55.507, 55.841, 56.175, 56.51, 56.845, 57.18, 57.516, 57.852, 58.188, 58.525, 58.862, 59.199, 59.536, 59.873, 60.211, 60.549, 60.886, 61.224, 61.562, 61.9, 62.238, 62.575, 62.913, 63.251, 63.588, 63.925, 64.263, 64.599, 64.936, 65.273, 65.609, 65.945, 66.281, 66.616, 66.951, 67.285, 67.62, 67.953, 68.287, 68.619, 68.952, 69.284, 69.615, 69.946, 70.276, 70.606, 70.934, 71.263, 71.59, 71.917, 72.244, 72.569, 72.894, 73.218, 73.541, 73.864, 74.185, 74.506, 74.826, 75.145, 75.463, 75.78, 76.097, 76.412, 76.726, 77.039, 77.351, 77.662, 77.972, 78.281, 78.589, 78.896, 79.201, 79.505, 79.809, 80.11, 80.411, 80.71, 81.008, 81.305, 81.6, 81.894, 82.187, 82.478, 82.768, 83.056, 83.343, 83.628, 83.912, 84.195, 84.475, 84.755, 85.032, 85.308, 85.583, 85.855, 86.126, 86.396, 86.663, 86.929, 87.193, 87.455, 87.726, 88.011, 88.308, 88.619, 88.941, 89.275, 89.619, 89.973, 90.336, 90.707, 91.086, 91.472, 91.864, 92.262, 92.664, 93.071, 93.48, 93.892, 94.306, 94.72, 95.135, 95.549, 95.962, 96.373, 96.781, 97.185, 97.586], "th_win": [34.52, 97.85], "L1": [[0.12, 43.46, 18.3], [-3.23, 43.71, 19.8], [-6.73, 43.87, 21.31], [-10.35, 43.79, 22.79], [-14.19, 43.74, 24.36], [-18.18, 43.38, 25.86], [-22.24, 42.6, 27.22], [-26.27, 41.29, 28.34]], "L2a": [[-29.82, 39.62, 29.84], [-31.39, 37.07, 32.4], [-32.82, 34.29, 34.84], [-34.16, 31.34, 37.21], [-35.31, 28.14, 39.38], [-36.39, 24.8, 41.49]], "L2b": [[-36.32, 23.34, 42.55], [-35.01, 20.93, 44.73], [-34.21, 18.8, 47.64], [-33.25, 16.52, 50.44], [-32.07, 14.08, 53.08], [-30.75, 11.51, 55.6], [-29.23, 8.81, 57.91], [-27.5, 5.99, 59.95], [-25.74, 3.09, 62.07], [-23.66, 0.09, 63.58], [-21.42, -2.96, 64.76], [-18.96, -6.0, 65.35], [-16.53, -9.07, 66.08], [-13.95, -12.09, 66.31], [-11.31, -15.08, 66.27], [-8.76, -18.3, 67.05], [-6.11, -21.65, 67.89]]};
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
      const cam = G.camH > 0
        ? { kind: 'hub', role: 'link', name: 'crown cam ring on hub 2 (link 1 side, 3 mm grooved ring; follower lever from link 2a)', c: on(F.R1, V.scale(u[1], G.f[1] + hub)), axis: Wd(M.mulv(F.R1, u[1])), r: G.camR, h: G.camH }
        : { kind: 'hub', role: 'link', name: 'cam flange O30 x 3.5 on link 1 (groove 10.6-13.7 mm, outside hub 2 housing)', c: on(F.R1, V.scale(u[1], G.f[1])), axis: Wd(M.mulv(F.R1, u[1])), r: G.camR, h: 3.5 };
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
