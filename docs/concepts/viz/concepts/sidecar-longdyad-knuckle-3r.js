/* sidecar-longdyad-knuckle-3r at its best measured configuration: the lead's slaved knuckle (pin knee, link 1 split by a
 * passive O20 knuckle K SLAVED to q2 past the onset) with the SIDECAR drive at strap level and a LONGER K dyad
 * (bk1 28.94 / bk2 39.24, stop B a1max 63.18). The hub-2 rim lobe pushes the short arm of a bell crank
 * (MR63ZZ pair, pin in link 1b, boss stacked on link 1b; long arm La 16.5 mm, phase 0.0 deg); an O3 rod with M2 ball links
 * runs beside link 1b to a lateral horn lug of link 1a at hub K (r_h 14.9 mm). J1, J2, J3 encoders give the pose
 * (3 active, K never read, 0 passive translations). Best: CMA A1 (near-touch objective), fast Bench(60,160) 10.30 near-touch = plain.
 * Geometry exported from docs/concepts/models/sidecar-longdyad-knuckle-3r.py (mode viz). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 96.6954, "el1": 67.5865, "az2": 42.2031, "el2": 44.4209, "wd": 67.5003, "wa": -7.3175, "b3": 0.345, "lE": 67.832, "lc": 25.6915, "phiE": -2.7863, "phib": -60.7036, "stk": 4.8534, "ang_min": 26.8823, "bk1": 28.9414, "bk2": 39.236, "sK": -1, "a1max": 63.177400000000006, "smhi": 16.5464, "smlo": 5.0, "capK": 6.0, "law_mode": "seg", "kA": 1.6232, "t1": 6.0, "kB": 1.6232, "smt": 12.0, "kK": 1.6232, "i_rock": 3.771585521517141, "r_horn": 14.8706, "r_lobe": 7.7447, "arm_lo": 1.0, "La": 16.5467, "r_h": 14.8706, "beta": -86.447, "gam": 0.0, "s_arm": 4.3872, "hl": 3.15, "zr": 0.0};
  const G = {"u": [[0.04445, 0.92446, 0.37869], [-0.4799, 0.65501, 0.58366], [-0.07591, -0.20566, 0.97567]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-1.54432, -13.6309, -2.99343]], "uK": [-0.29434, 0.95562, 0.0126], "sa": [0.01595, -0.97862, -0.20504], "st": [0.99699, 0.0, 0.07757], "sn": [-0.07591, -0.20566, 0.97567], "A": [36.369, 61.889], "branch": -1.0, "m": [-12.1603, 1.76235, 0.0], "f": [49.72, 60.34, 78.56], "fK": 55.38, "capK": 6.0, "tr": 86.14, "tp": 2.177, "RUN": 0.5, "A0": [-3.75088, -79.93436, -17.14129], "A0m": [-2.18784, -68.03401, -14.51119], "Bm": [-24.32532, -80.33683, -18.82694], "eE": [-0.03253, -0.97747, -0.20857], "psiA": -65.4036, "thLo": 30.5201, "thHi": 81.7112, "q2s": [90.0564, -3.8399], "lawTh": [81.711, 82.586, 83.474, 84.373, 85.283, 86.203, 87.133, 88.071, 89.017, 89.969, 90.928, 91.892, 92.86, 93.831, 94.806, 95.781, 96.758, 97.735, 98.711, 99.685, 100.657, 101.625, 102.588, 103.546, 104.498, 105.442, 106.377, 107.303, 108.218, 109.122, 110.012, 110.889, 111.751, 112.596, 113.424, 114.233, 115.022, 115.789, 116.534, 117.255, 117.95, 118.619, 119.26], "lawDK": [-0.0, -1.299, -2.597, -3.896, -5.194, -6.493, -7.791, -9.09, -10.388, -11.687, -12.986, -14.284, -15.583, -16.881, -18.18, -19.478, -20.777, -22.076, -23.374, -24.673, -25.971, -27.27, -28.568, -29.867, -31.165, -32.464, -33.763, -35.061, -36.36, -37.658, -38.957, -40.255, -41.554, -42.852, -44.151, -45.45, -46.748, -48.047, -49.345, -50.644, -51.942, -53.241, -54.54], "lawQ2": [-3.84, -4.64, -5.44, -6.24, -7.04, -7.84, -8.64, -9.44, -10.24, -11.04, -11.84, -12.64, -13.44, -14.24, -15.04, -15.84, -16.64, -17.44, -18.24, -19.04, -19.84, -20.64, -21.44, -22.24, -23.04, -23.84, -24.64, -25.44, -26.24, -27.04, -27.84, -28.64, -29.44, -30.24, -31.04, -31.84, -32.64, -33.44, -34.24, -35.04, -35.84, -36.64, -37.44], "emb": "rod", "rocker": [-26.336, 49.965, 23.288], "rockerAx": [-0.43107, 0.81785, 0.38118], "rodA": [-42.145, 47.487, 18.203], "rodB": [-32.254, 57.648, -4.588], "armA": [-26.336, 49.965, 23.288], "armB": [-39.558, 42.58, 15.916], "L1a": [[-3.12, 49.91, 9.83], [-4.52, 49.46, 11.09], [-5.92, 49.01, 12.35], [-7.32, 48.56, 13.61]], "L1b": [[-24.6, 53.53, 10.1], [-24.91, 47.88, 14.74], [-26.91, 45.73, 20.13], [-22.8, 54.07, 10.97], [-22.99, 47.89, 15.4], [-24.98, 45.82, 20.76], [-21.01, 54.62, 11.84], [-21.05, 47.76, 15.99], [-22.88, 45.51, 21.19], [-19.22, 55.16, 12.7], [-19.03, 47.31, 16.45], [-21.05, 45.62, 21.81]], "L2": [[-32.13, 33.95, 44.27], [-29.64, 24.94, 50.42], [-28.37, 16.51, 59.01], [-25.74, 6.31, 65.9], [-21.43, -5.1, 69.26], [-16.55, -17.17, 71.6], [-28.28, 29.14, 46.2], [-27.2, 21.48, 54.7], [-25.05, 12.2, 62.11], [-21.57, 1.5, 67.33], [-16.54, -9.77, 68.29], [-28.92, 35.46, 45.21], [-26.12, 26.08, 50.67], [-24.33, 17.61, 58.38], [-21.47, 7.72, 64.74], [-17.08, -3.25, 67.48], [-12.71, -15.3, 72.25], [-25.38, 30.8, 47.43], [-23.63, 22.68, 54.86], [-21.57, 13.75, 62.85], [-17.9, 3.14, 67.83], [-12.91, -8.04, 68.86]], "hornA": [-26.586, 54.662, -2.876], "hornB": [-30.929, 53.348, -4.645]};
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
    id: 'sidecar-longdyad-knuckle-3r', name: 'Sidecar drive on a longer K dyad: hub-2 lobe -> bell crank on link 1b -> strap-level rod -> horn of link 1a slaves K to q2 (3 active, K not read)',
    dof: { active: 3, passive: 3 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'K (passive, slaved to q2 by the lobe - bell crank - rod - horn sidecar)', 'J2', 'J3', 'knee pin a', 'knee pin b'], qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve: solveC,
    residual: (q, ctx) => { const F = fk(q); return M.rotErrDeg(F.R5, Qof(ctx)).concat(F.t5); },
    check,
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), F = fk(q);
      const on = (R, p) => W(M.mulv(R, p)), I = M.I3();
      const h1 = { kind: 'hub', role: 'active', name: 'J1 (axis on a GH ray)', c: W(V.scale(u[0], G.f[0])), axis: Wd(u[0]), r: rad, h: hub };
      const hK = { kind: 'hub', role: 'passive', name: 'K (O20, passive, slaved; clock-spring cap, stop A; the horn is a lateral lug of link 1a)', c: on(F.R1, V.scale(uK, G.fK)), axis: Wd(M.mulv(F.R1, uK)), r: rad, h: hub + (G.capK || 0) };
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
        { kind: 'hub', role: 'passive', name: 'bell crank boss (MR63ZZ pair, pin in link 1b beside hub 2; short arm rides the hub-2 rim lobe)', c: on(F.R1b, G.rocker), axis: Wd(M.mulv(F.R1b, G.rockerAx)), r: 5, h: 6 },
        { kind: 'link', role: 'link', name: 'bell crank long arm (3 mm Ti, joggled down beside link 1b)', a: on(F.R1b, G.armA), b: on(F.R1b, G.armB), r: 1.5 },
        { kind: 'link', role: 'link', name: 'horn lug of link 1a at hub K (strap level)', a: on(F.R1, G.hornA), b: on(F.R1, G.hornB), r: 1.5 },
        { kind: 'link', role: 'link', name: 'O3 Ti rod with M2 ball links (crank tip -> horn ball, beside link 1b)', a: on(F.R1b, G.rodA), b: on(F.R1, G.rodB), r: 1.5 },
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
