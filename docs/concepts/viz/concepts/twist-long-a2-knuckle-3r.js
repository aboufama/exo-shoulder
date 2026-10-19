/* twist-long-a2-knuckle-3r at its best measured configuration: the verified lead's knuckle chain (pin knee, link 1 split by a
 * passive O20 knuckle K SLAVED to q2 by the hub-2 rim lobe -> rocker -> O3 pushrod -> horn on K's cap) with the J3 axis
 * re-seated (turned about the humerus), a2 re-chosen and the K dyad widened on the bk2 side. 3 active (J1, J2, J3), K never
 * read, 0 passive translations. Best frozen config (CMA C0): fast 17.29 near-touch, frozen exact Bench(110,360) 24.46 (lead 22.82); the twist walked back to wdir(74.4, -1.1).
 * Geometry exported from docs/concepts/models/twist-long-a2-knuckle-3r.py (mode viz). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 101.3027, "el1": 68.3795, "az2": 52.87113799484253, "el2": 42.25827760209621, "wd": 58.48304975914951, "wa": -5.871703907291355, "b3": 0.4531, "lE": 72.638, "lc": 28.3246, "phiE": -1.6851, "phib": -65.2692, "stk": 4.8534, "ang_min": 27.6322, "bk1": 30.5224, "bk2": 45.2163, "sK": -1, "a1max": 70.7387, "smhi": 16.5335, "smlo": 5.6146, "capK": 6.0, "law_mode": "seg", "kA": 2.0293, "t1": 11.1114, "kB": 1.8211, "smt": 12.0, "kK": 3.1796, "i_rock": 1.0, "r_horn": 2.5321, "r_lobe": 7.4633, "arm_lo": 1.0};
  const G = {"u": [[0.07221, 0.92964, 0.36131], [-0.3793, 0.63503, 0.67296], [-0.02081, -0.26925, 0.96285]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-2.66901, -21.99815, -6.20926]], "uK": [-0.29014, 0.95678, -0.01961], "sa": [0.00582, -0.96307, -0.26919], "st": [0.99977, 0.0, 0.02161], "sn": [-0.02081, -0.26925, 0.96285], "A": [36.283, 60.996], "branch": -1.0, "m": [-20.11969, 2.7862, 0.0], "f": [49.71, 60.44, 82.83], "fK": 56.31, "capK": 6.0, "tr": 88.97, "tp": 2.177, "RUN": 0.5, "A0": [-4.38201, -91.9234, -25.80018], "A0m": [-1.71355, -72.54672, -20.324], "Bm": [-27.36534, -83.95886, -24.06984], "eE": [-0.02358, -0.96265, -0.26971], "psiA": -56.4381, "thLo": 30.3277, "thHi": 80.7456, "q2s": [100.5793, 8.3301], "lawTh": [80.746, 81.658, 82.596, 83.558, 84.544, 85.552, 86.58, 87.628, 88.695, 89.778, 90.877, 91.991, 93.118, 94.257, 95.398, 96.478, 97.564, 98.656, 99.752, 100.851, 101.952, 103.055, 104.157, 105.258, 106.357, 107.452, 108.543, 109.627, 110.705, 111.774, 112.832, 113.88, 114.915, 115.935, 116.94, 117.927, 118.895, 119.842, 120.767, 121.667, 122.541, 123.386, 124.202, 124.985, 125.734, 126.447, 127.121, 127.755, 128.347, 128.894, 129.395, 129.847], "lawDK": [-0.0, -1.623, -3.247, -4.87, -6.494, -8.117, -9.741, -11.364, -12.988, -14.611, -16.234, -17.858, -19.481, -21.105, -22.71, -24.167, -25.623, -27.08, -28.537, -29.994, -31.451, -32.908, -34.365, -35.822, -37.279, -38.735, -40.192, -41.649, -43.106, -44.563, -46.02, -47.477, -48.934, -50.39, -51.847, -53.304, -54.761, -56.218, -57.675, -59.132, -60.589, -62.045, -63.502, -64.959, -66.416, -67.873, -69.33, -70.787, -72.244, -73.701, -75.157, -76.614], "lawQ2": [8.33, 7.53, 6.73, 5.93, 5.13, 4.33, 3.53, 2.73, 1.93, 1.13, 0.33, -0.47, -1.27, -2.07, -2.87, -3.67, -4.47, -5.27, -6.07, -6.87, -7.67, -8.47, -9.27, -10.07, -10.87, -11.67, -12.47, -13.27, -14.07, -14.87, -15.67, -16.47, -17.27, -18.07, -18.87, -19.67, -20.47, -21.27, -22.07, -22.87, -23.67, -24.47, -25.27, -26.07, -26.87, -27.67, -28.47, -29.27, -30.07, -30.87, -31.67, -32.47], "emb": "rod", "rocker": [-22.873, 48.899, 28.551], "rockerAx": [-0.37455, 0.80071, 0.46752], "rodA": [-29.616, 63.312, 36.967], "rodB": [-18.338, 69.199, -1.404], "armA": [-29.615, 63.312, 36.967], "armB": [-29.616, 63.312, 36.967], "L1a": [[-1.67, 50.04, 9.16], [-6.42, 57.02, 5.63], [-6.08, 53.12, 8.15], [-5.73, 49.2, 10.29], [-5.8, 48.87, 13.0], [-11.09, 55.69, 9.97]], "L1b": [[-22.93, 55.38, 9.04], [-21.64, 48.39, 13.46], [-22.63, 46.76, 18.81], [-23.65, 45.04, 24.3], [-26.22, 45.76, 31.85], [-19.33, 48.79, 12.0], [-20.32, 47.3, 17.29], [-21.49, 46.06, 22.88], [-22.81, 44.89, 28.92], [-18.35, 52.83, 11.37], [-18.06, 47.77, 15.8], [-19.22, 46.74, 21.33], [-20.22, 45.13, 26.92], [-17.17, 57.15, 10.6], [-15.79, 47.96, 14.27], [-16.97, 47.24, 19.76], [-18.0, 45.92, 25.33], [-20.37, 47.57, 33.44]], "L2": [[-26.04, 32.65, 49.0], [-24.28, 23.44, 53.99], [-23.72, 14.86, 61.94], [-21.87, 4.46, 67.43], [-18.98, -6.96, 70.33], [-15.24, -18.65, 70.36], [-11.82, -32.43, 73.4], [-22.71, 27.54, 50.08], [-22.13, 19.64, 57.7], [-20.8, 10.22, 64.27], [-18.47, -0.57, 68.74], [-15.07, -12.0, 69.95], [-11.07, -23.38, 68.73], [-21.36, 30.52, 48.09], [-20.55, 22.69, 54.99], [-19.44, 13.93, 62.01], [-17.22, 3.65, 66.6], [-14.21, -7.44, 69.04], [-10.34, -18.54, 68.1], [-7.15, -34.21, 76.3], [-19.33, 27.07, 51.67], [-18.32, 18.9, 58.63], [-16.71, 9.47, 64.94], [-14.15, -1.26, 69.08], [-10.59, -12.5, 69.63], [-6.7, -24.24, 69.86]]};
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
    const F = fk(q), sv = M.mulv(M.T(Q), F.t3), kn = knee([V.dot(sv, sa), V.dot(sv, st)]);
    if (!kn.span) return 'knee span: the drift is beyond lE + lc';
    if (kn.ang < P.ang_min || kn.ang > 180 - P.ang_min) return `knee angle ${kn.ang.toFixed(0)} deg outside [${P.ang_min}, ${180 - P.ang_min}]`;
    return null;
  };
  const closes = (q, ctx) => { const r = C.residual(q, ctx); return Math.max(...r.map(Math.abs)) <= 0.5; };
  const solveC = (ctx, qPrev) => { const q = solve(ctx); return (!qPrev || closes(q, ctx)) ? q : K.dls(C, ctx, qPrev, { iters: 40 }).q; };
  const C = {
    id: 'twist-long-a2-knuckle-3r', name: 'J3 re-seat for reach on the knuckle drive: J3 axis turned about the humerus, a2 re-chosen, K dyad widened (3 active, K slaved, not read)',
    dof: { active: 3, passive: 3 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'K (passive, slaved to q2 by the lobe-rocker-pushrod drive)', 'J2', 'J3', 'knee pin a', 'knee pin b'], qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve: solveC,
    residual: (q, ctx) => { const F = fk(q); return M.rotErrDeg(F.R5, Qof(ctx)).concat(F.t5); },
    check,
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), F = fk(q);
      const on = (R, p) => W(M.mulv(R, p)), I = M.I3();
      const h1 = { kind: 'hub', role: 'active', name: 'J1 (axis on a GH ray)', c: W(V.scale(u[0], G.f[0])), axis: Wd(u[0]), r: rad, h: hub };
      const hK = { kind: 'hub', role: 'passive', name: 'K (O20, passive, slaved; clock-spring cap with the pushrod horn, stop A)', c: on(F.R1, V.scale(uK, G.fK)), axis: Wd(M.mulv(F.R1, uK)), r: rad, h: hub + (G.capK || 0) };
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
        { kind: 'hub', role: 'passive', name: 'follower post (O10 on link 1b, 1:1; rides the lobe on hub 2 rotor rim; its rod end raised to clear hub K crown)', c: on(F.R1b, G.rocker), axis: Wd(M.mulv(F.R1b, G.rockerAx)), r: 5, h: 9 },
        { kind: 'link', role: 'link', name: 'O3 pushrod with M3 rod ends (post -> horn on K cap, over hub K crown)', a: on(F.R1b, G.rodA), b: on(F.R1b, G.rodB), r: 1.5 },
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
