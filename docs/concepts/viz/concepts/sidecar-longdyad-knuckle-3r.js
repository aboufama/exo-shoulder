/* sidecar-longdyad-knuckle-3r at its best measured configuration: the lead's slaved knuckle (pin knee, link 1 split by a
 * passive O20 knuckle K SLAVED to q2 past the onset) with the SIDECAR drive at strap level and a LONGER K dyad
 * (bk1 30.00 / bk2 44.00, stop B a1max 66.00). The hub-2 rim lobe pushes the short arm of a bell crank
 * (MR63ZZ pair, pin in link 1b, boss stacked on link 1b; long arm La 20.0 mm, phase 15.0 deg); an O3 rod with M2 ball links
 * runs beside link 1b to a lateral horn lug of link 1a at hub K (r_h 15.0 mm). J1, J2, J3 encoders give the pose
 * (3 active, K never read, 0 passive translations). Seed (untuned).
 * Geometry exported from docs/concepts/models/sidecar-longdyad-knuckle-3r.py (mode viz). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 95.3594, "el1": 67.6187, "az2": 42.7487, "el2": 43.9031, "wd": 63.5262, "wa": -10.5604, "b3": 0.3825, "lE": 67.832, "lc": 25.8149, "phiE": -2.7863, "phib": -65.6717, "stk": 4.8534, "ang_min": 27.8606, "bk1": 30.0, "bk2": 44.0, "sK": -1, "a1max": 66.0, "smhi": 14.7672, "smlo": 5.1723, "capK": 6.0, "law_mode": "seg", "kA": 2.0, "t1": 6.0, "kB": 2.0, "smt": 12.0, "kK": 2.0, "i_rock": 4.0, "r_horn": 15.0, "r_lobe": 7.5, "arm_lo": 1.0, "La": 20.0, "r_h": 15.0, "beta": -90.0, "gam": 15.0, "s_arm": 5.0, "hl": 3.15, "zr": 1.5};
  const G = {"u": [[0.03556, 0.92467, 0.3791], [-0.48034, 0.65119, 0.58756], [-0.11461, -0.2375, 0.9646]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-1.9766, -17.1149, -4.44881]], "uK": [-0.24904, 0.96714, -0.05118], "sa": [0.02802, -0.97139, -0.23584], "st": [0.99302, 0.0, 0.11798], "sn": [-0.11461, -0.2375, 0.9646], "A": [36.119, 62.15], "branch": -1.0, "m": [-15.00266, 2.46539, 0.0], "f": [49.45, 60.07, 81.05], "fK": 56.07, "capK": 6.0, "tr": 88.56, "tp": 2.177, "RUN": 0.5, "A0": [-3.35245, -82.92815, -20.81657], "A0m": [-1.32467, -68.35476, -16.98743], "Bm": [-24.38491, -78.68529, -22.27086], "eE": [-0.02028, -0.97024, -0.2413], "psiA": -57.8494, "thLo": 31.2038, "thHi": 83.5019, "q2s": [93.3473, -3.6121], "lawTh": [83.502, 84.429, 85.378, 86.348, 87.339, 88.348, 89.376, 90.419, 91.478, 92.551, 93.637, 94.734, 95.841, 96.957, 98.081, 99.212, 100.347, 101.487, 102.629, 103.772, 104.915, 106.057, 107.195, 108.329, 109.456, 110.577, 111.688, 112.788, 113.875, 114.948, 116.005, 117.044, 118.063, 119.06, 120.033, 120.979, 121.897, 122.785, 123.639], "lawDK": [-0.0, -1.6, -3.2, -4.8, -6.4, -8.0, -9.6, -11.2, -12.8, -14.4, -16.0, -17.6, -19.2, -20.8, -22.4, -24.0, -25.6, -27.2, -28.8, -30.4, -32.0, -33.6, -35.2, -36.8, -38.4, -40.0, -41.6, -43.2, -44.8, -46.4, -48.0, -49.6, -51.2, -52.8, -54.4, -56.0, -57.6, -59.2, -60.8], "lawQ2": [-3.612, -4.412, -5.212, -6.012, -6.812, -7.612, -8.412, -9.212, -10.012, -10.812, -11.612, -12.412, -13.212, -14.012, -14.812, -15.612, -16.412, -17.212, -18.012, -18.812, -19.612, -20.412, -21.212, -22.012, -22.812, -23.612, -24.412, -25.212, -26.012, -26.812, -27.612, -28.412, -29.212, -30.012, -30.812, -31.612, -32.412, -33.212, -34.012], "emb": "rod", "rocker": [-25.971, 49.721, 23.565], "rockerAx": [-0.42684, 0.81719, 0.3873], "rodA": [-45.906, 45.825, 21.047], "rodB": [-29.233, 59.389, -9.868], "armA": [-25.971, 49.721, 23.565], "armB": [-43.345, 40.922, 18.723], "L1a": [[-2.09, 49.96, 8.77], [-3.68, 49.61, 9.78], [-5.27, 49.25, 10.8], [-6.86, 48.9, 11.82]], "L1b": [[-22.44, 55.77, 5.96], [-22.46, 48.98, 10.49], [-24.61, 47.32, 15.63], [-26.7, 45.29, 20.81], [-20.64, 56.28, 6.86], [-20.62, 48.95, 11.2], [-22.76, 47.38, 16.32], [-24.81, 45.4, 21.48], [-18.84, 56.79, 7.77], [-18.78, 48.84, 11.87], [-20.91, 47.37, 16.97], [-23.1, 45.79, 22.28], [-17.04, 57.31, 8.67], [-16.95, 48.66, 12.51], [-19.2, 47.63, 17.72], [-21.33, 46.04, 23.01]], "L2": [[-32.63, 33.64, 43.65], [-31.14, 24.88, 49.7], [-30.54, 16.39, 57.44], [-28.79, 6.37, 63.75], [-25.59, -4.77, 67.46], [-20.91, -16.0, 67.4], [-31.06, 34.29, 44.21], [-29.3, 25.29, 49.8], [-28.64, 16.92, 57.51], [-26.66, 6.98, 63.4], [-23.44, -3.96, 66.99], [-18.82, -15.0, 66.89], [-29.49, 34.94, 44.77], [-27.71, 25.89, 50.27], [-26.96, 17.56, 57.99], [-24.95, 7.67, 63.95], [-21.36, -3.19, 66.56], [-16.86, -14.1, 66.66], [-27.92, 35.59, 45.33], [-26.21, 26.58, 50.91], [-25.47, 18.33, 58.87], [-23.36, 8.41, 64.84], [-19.86, -2.51, 67.92], [-15.23, -13.46, 67.67]], "hornA": [-23.782, 56.267, -7.461], "hornB": [-28.112, 55.037, -9.638]};
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
