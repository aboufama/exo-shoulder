/* frontload-lobe-stopb-knuckle-3r at its best measured configuration: the verified winner's chain (pin knee, link 1 split by a
 * passive O20 knuckle K SLAVED to q2) with the hub-2 rim lobe re-cut FRONT-LOADED (seg law: K opens fast just past
 * the onset, then slower) and K's stop B raised toward the K dyad's 5-deg margin (a1max 64.20, bk1 + bk2 - 5 =
 * 64.24). The lobe drives a 2.00:1 rocker on link 1b; an O3 pushrod with M3 rod ends turns a horn
 * (r 2.50) on K's cap. J1, J2, J3 encoders give the pose (3 active, K never read, 0 passive translations).
 * First check configuration. Fast Bench(60,160) near-touch gap 19.66; geometry exported from
 * docs/concepts/models/frontload-lobe-stopb-knuckle-3r.py (mode viz). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 93.5546, "el1": 67.3642, "az2": 43.4586, "el2": 43.3068, "wd": 63.337, "wa": -9.6473, "b3": 0.3837, "lE": 67.832, "lc": 25.8149, "phiE": -2.7863, "phib": -65.6717, "stk": 4.8534, "ang_min": 27.8544, "bk1": 31.2491, "bk2": 37.9937, "sK": -1, "a1max": 64.2, "smhi": 13.6865, "smlo": 5.2777, "capK": 6.0, "law_mode": "seg", "kA": 6.0, "t1": 6.0, "kB": 3.0, "smt": 12.0, "kK": 3.1796, "i_rock": 2.0, "r_horn": 2.5, "r_lobe": 8.0, "arm_lo": 1.0};
  const G = {"u": [[0.02386, 0.92297, 0.38413], [-0.47582, 0.64318, 0.59993], [-0.09951, -0.23654, 0.96651]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-1.97854, -17.4181, -4.46644]], "uK": [-0.37536, 0.92661, 0.02251], "sa": [0.02422, -0.97162, -0.23529], "st": [0.99474, 0.0, 0.10241], "sn": [-0.09951, -0.23654, 0.96651], "A": [35.636, 61.637], "branch": -1.0, "m": [-15.01125, 2.40912, 0.0], "f": [49.87, 60.61, 81.1], "fK": 58.02, "capK": 6.0, "tr": 88.13, "tp": 2.177, "RUN": 0.5, "A0": [-3.61735, -83.24731, -20.74558], "A0m": [-1.58453, -68.66203, -16.96683], "Bm": [-24.72577, -78.99507, -21.87811], "eE": [-0.02416, -0.97047, -0.23999], "psiA": -64.199, "thLo": 31.2787, "thHi": 83.5867, "q2s": [93.3985, -5.0112], "lawTh": [83.587, 86.137, 88.786, 91.513, 94.3, 97.128, 99.979, 102.833, 105.053, 106.638, 108.205, 109.75, 111.27, 112.76, 114.215, 115.631, 117.004, 118.327, 119.596, 120.806, 121.951, 123.025, 124.023, 124.94], "lawDK": [-0.0, -4.8, -9.6, -14.4, -19.2, -24.0, -28.8, -33.6, -37.2, -39.6, -42.0, -44.4, -46.8, -49.2, -51.6, -54.0, -56.4, -58.8, -61.2, -63.6, -66.0, -68.4, -70.8, -73.2], "lawQ2": [-5.011, -5.811, -6.611, -7.411, -8.211, -9.011, -9.811, -10.611, -11.411, -12.211, -13.011, -13.811, -14.611, -15.411, -16.211, -17.011, -17.811, -18.611, -19.411, -20.211, -21.011, -21.811, -22.611, -23.411], "emb": "rod", "rocker": [-28.104, 48.857, 23.749], "rockerAx": [-0.45949, 0.79881, 0.38829], "rodA": [-43.893, 58.161, 25.842], "rodB": [-25.185, 68.83, 1.649], "armA": [-35.226, 61.239, 29.767], "armB": [-43.893, 58.161, 25.842], "L1a": [[-5.25, 49.69, 10.74], [-11.25, 57.87, 7.84], [-10.31, 53.81, 10.3], [-9.38, 49.74, 12.36], [-8.92, 48.11, 14.77], [-15.52, 56.02, 12.53]], "L1b": [[-29.2, 53.9, 11.6], [-27.54, 46.6, 15.87], [-28.72, 44.45, 21.3], [-27.36, 54.63, 12.28], [-25.66, 46.87, 16.35], [-26.83, 44.77, 21.75], [-25.51, 55.36, 12.96], [-23.75, 47.02, 16.77], [-24.85, 44.87, 22.09], [-23.67, 56.09, 13.64], [-21.81, 47.02, 17.14], [-23.13, 45.39, 22.63]], "L2": [[-32.44, 33.39, 44.76], [-30.85, 24.63, 50.86], [-30.15, 16.1, 58.74], [-28.16, 5.97, 64.9], [-24.74, -5.2, 68.3], [-19.85, -16.33, 67.73], [-30.86, 34.05, 45.3], [-29.0, 25.05, 50.92], [-28.2, 16.62, 58.7], [-26.06, 6.6, 64.56], [-22.58, -4.38, 67.78], [-17.79, -15.33, 67.23], [-29.29, 34.71, 45.84], [-27.16, 25.43, 50.91], [-26.27, 17.12, 58.63], [-24.05, 7.23, 64.36], [-20.49, -3.59, 67.27], [-15.79, -14.36, 66.71], [-27.71, 35.37, 46.39], [-25.59, 26.05, 51.38], [-24.61, 17.78, 59.11], [-22.4, 7.95, 65.05], [-18.84, -2.88, 68.12], [-14.19, -13.76, 67.85]]};
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
    id: 'frontload-lobe-stopb-knuckle-3r', name: 'Front-loaded rim lobe + stop B at the K dyad margin: hub-2 lobe -> 2:1 rocker -> pushrod slaves K to q2 (3 active, K not read)',
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
        { kind: 'hub', role: 'passive', name: 'rocker (O10 x 9 on link 1b; follows the lobe on hub 2 rotor rim)', c: on(F.R1b, G.rocker), axis: Wd(M.mulv(F.R1b, G.rockerAx)), r: 5, h: 9 },
        { kind: 'link', role: 'link', name: 'rocker long arm (clevis fork, ' + (5 * P.i_rock).toFixed(0) + ' mm)', a: on(F.R1b, G.armA), b: on(F.R1b, G.armB), r: 2 },
        { kind: 'link', role: 'link', name: 'O3 pushrod with M3 rod ends (rocker arm -> horn on K cap)', a: on(F.R1b, G.rodA), b: on(F.R1b, G.rodB), r: 1.5 },
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
