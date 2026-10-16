/* rim-lobe-arm-knuckle-3r (round 7, KILLED at its gate - drawn at its best measured configuration). The pin-knee chain with
 * link 1 split by a passive O20 knuckle K that is SLAVED to q2 by a DIRECT higher pair: link 1a grows an integral lug that
 * carries an O5 roller at L_arm 26 mm from K's axis (aimed a0 20 deg off the K-J2 line: at a0 ~ 0 the pressure angle is
 * 90 deg), and link 2 carries a flat 3 mm lobe plate around hub 2 whose edge pushes the roller, so past thHi K opens by
 * dK = kK t (kK 0.6, t = q2 travel past the onset) until the follower reaches rho_max 27 mm from u2 (the q2 dowel stop B).
 * No rocker, pushrod or rod ends. J1, J2, J3 encoders give the pose (3 active, K never read). Fast Bench(60,160) best
 * near-touch 26.05 against the gate 15.5: the lobe's outer end sweeps over skin 6-14 mm higher than under hub 2, so the
 * plate and the lug sit 20-30 mm over the skin (0 % in band); lowered, the lug collides with link 1b.
 * Geometry exported from docs/concepts/models/rim-lobe-arm-knuckle-3r.py (mode viz). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 93.5546, "el1": 67.3642, "az2": 43.4586, "el2": 43.3068, "wd": 63.337, "wa": -9.6473, "b3": 0.3837, "lE": 67.832, "lc": 25.8149, "phiE": -2.7863, "phib": -65.6717, "stk": 4.8534, "ang_min": 27.8544, "bk1": 31.2491, "bk2": 37.9937, "sK": -1, "a1max": 58.3565, "smhi": 28.0, "smlo": 5.2777, "capK": 6.0, "emb": "roller", "lay": "low", "kK": 0.6, "L_arm": 26, "a0": 20, "rr": 2.5, "rho_max": 27};
  const G = {"u": [[0.02386, 0.92297, 0.38413], [-0.47582, 0.64318, 0.59993], [-0.09951, -0.23654, 0.96651]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-1.97854, -17.4181, -4.46644]], "uK": [-0.37536, 0.92661, 0.02251], "sa": [0.02422, -0.97162, -0.23529], "st": [0.99474, 0.0, 0.10241], "sn": [-0.09951, -0.23654, 0.96651], "A": [35.636, 61.637], "branch": -1.0, "m": [-13.48348, 2.38302, 0.0], "f": [49.87, 60.24, 79.65], "fK": 56.82, "capK": 6.0, "tr": 88.05, "tp": 2.177, "RUN": 0.5, "A0": [-3.61735, -83.24731, -20.74558], "A0m": [-1.57349, -70.14645, -17.32898], "Bm": [-24.71472, -80.47949, -22.24026], "eE": [-0.02416, -0.97047, -0.23999], "psiA": -64.199, "thLo": 31.2787, "thHi": 69.2732, "q2s": [93.3985, 23.7475], "lawTh": [69.273, 70.764, 72.276, 73.809, 75.359, 76.923, 78.499, 80.085, 81.677, 83.272, 84.869, 86.464, 88.055, 89.639, 91.213, 92.774, 94.319, 95.845, 97.348], "lawDK": [-0.0, -1.2, -2.4, -3.6, -4.8, -6.0, -7.2, -8.4, -9.6, -10.8, -12.0, -13.2, -14.4, -15.6, -16.8, -18.0, -19.2, -20.4, -21.6], "lawQ2": [23.748, 21.748, 19.748, 17.748, 15.748, 13.748, 11.748, 9.748, 7.748, 5.748, 3.748, 1.748, -0.252, -2.252, -4.252, -6.252, -8.252, -10.252, -12.252], "emb": "roller", "foll": [-51.93, 131.41, 66.83], "lug": [[-47.65, 118.36, 17.39], [-51.32, 128.5, 39.07], [-50.96, 128.73, 60.99], [-49.22, 122.97, 32.07], [-51.88, 130.73, 55.73], [-46.98, 117.14, 25.57], [-50.11, 125.97, 47.9], [-49.22, 124.88, 69.78], [-48.19, 120.86, 40.53], [-50.26, 127.19, 64.68]], "plate": [[-54.89, 114.04, 81.8], [-46.98, 123.31, 78.13], [-48.73, 125.06, 74.88], [-54.4, 118.37, 77.55], [-43.59, 135.34, 67.92], [-49.46, 130.35, 68.63], [-45.36, 140.35, 61.15], [-52.78, 130.1, 66.26], [-57.85, 121.71, 71.23]], "L1a": [[-5.23, 49.7, 10.72], [-11.0, 56.68, 7.65], [-10.08, 52.67, 10.08], [-9.18, 48.65, 12.1], [-8.94, 48.1, 14.8], [-15.22, 54.86, 12.3]], "L1b": [[-28.67, 52.83, 11.36], [-27.58, 46.59, 15.85], [-28.77, 44.44, 21.29], [-26.84, 53.56, 12.04], [-25.67, 46.87, 16.34], [-26.84, 44.76, 21.75], [-25.0, 54.29, 12.71], [-23.74, 47.02, 16.78], [-24.81, 44.84, 22.08], [-23.17, 55.01, 13.39], [-21.77, 47.02, 17.15], [-22.74, 44.73, 22.31]], "L2": [[-32.29, 33.0, 44.66], [-29.74, 23.31, 49.3], [-29.02, 14.78, 57.01], [-27.12, 4.69, 63.24], [-23.84, -6.54, 67.01], [-19.44, -18.21, 68.13], [-28.83, 30.48, 43.82], [-27.89, 22.45, 50.73], [-26.89, 13.76, 58.18], [-24.45, 3.53, 63.37], [-21.04, -7.6, 66.83], [-16.75, -19.34, 68.5], [-27.27, 29.9, 45.64], [-26.13, 21.66, 52.35], [-24.72, 12.71, 59.24], [-21.89, 2.39, 63.61], [-18.26, -8.62, 66.52], [-14.67, -21.35, 71.84], [-25.82, 29.46, 47.71], [-24.31, 20.84, 53.91], [-22.3, 11.53, 59.62], [-19.6, 1.3, 64.55], [-15.89, -9.81, 67.61], [-12.33, -23.45, 75.14]]};
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
    if (!k.ok) return k.L.state === 1 ? 'past the drive stop B (rho_max / rate / stop B)' : (k.L.state === -1 ? 'folded side: J2 on its dowel (no tooth)' : 'chain cannot close');
    const F = fk(q), sv = M.mulv(M.T(Q), F.t3), kn = knee([V.dot(sv, sa), V.dot(sv, st)]);
    if (!kn.span) return 'knee span: the drift is beyond lE + lc';
    if (kn.ang < P.ang_min || kn.ang > 180 - P.ang_min) return `knee angle ${kn.ang.toFixed(0)} deg outside [${P.ang_min}, ${180 - P.ang_min}]`;
    return null;
  };
  const closes = (q, ctx) => { const r = C.residual(q, ctx); return Math.max(...r.map(Math.abs)) <= 0.5; };
  const solveC = (ctx, qPrev) => { const q = solve(ctx); return (!qPrev || closes(q, ctx)) ? q : K.dls(C, ctx, qPrev, { iters: 40 }).q; };
  const C = {
    id: 'rim-lobe-arm-knuckle-3r', name: 'Direct-pair knuckle: a lug on link 1a rides a lobe plate on link 2, so q2 drives K (3 active, K not read; killed at its gate)',
    dof: { active: 3, passive: 3 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'K (passive, slaved to q2 by the lug roller on the link-2 lobe plate)', 'J2', 'J3', 'knee pin a', 'knee pin b'], qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve: solveC,
    residual: (q, ctx) => { const F = fk(q); return M.rotErrDeg(F.R5, Qof(ctx)).concat(F.t5); },
    check,
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), F = fk(q);
      const on = (R, p) => W(M.mulv(R, p)), I = M.I3();
      const h1 = { kind: 'hub', role: 'active', name: 'J1 (axis on a GH ray)', c: W(V.scale(u[0], G.f[0])), axis: Wd(u[0]), r: rad, h: hub };
      const hK = { kind: 'hub', role: 'passive', name: 'K (O20, passive, slaved; clock-spring cap holds the roller on the lobe, stop A)', c: on(F.R1, V.scale(uK, G.fK)), axis: Wd(M.mulv(F.R1, uK)), r: rad, h: hub + (G.capK || 0) };
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
        { kind: 'arc', role: 'link', name: 'lug of link 1a (8 x 3, K -> roller; skin-fitted)', pts: G.lug.map(p => on(F.R1, p)), r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'O5 roller (MR52ZZ) on the lug tip', c: on(F.R1, G.foll), axis: Wd(M.mulv(F.R1, V.unit(G.foll))), r: 2.5, h: 3 },
        { kind: 'arc', role: 'link', name: 'lobe plate of link 2 (flat 3 mm Ti, wire-EDM edge drives the roller)', pts: G.plate.map(p => on(F.R12, p)), r: 2.5 },
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
