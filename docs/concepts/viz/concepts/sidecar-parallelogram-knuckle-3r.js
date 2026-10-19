/* sidecar-parallelogram-knuckle-3r (round 8, pick 1) at its best measured configuration: the verified lead's slaved
 * knuckle chain UNCHANGED (pin knee, link 1 split by a passive O20 knuckle K SLAVED to q2 past the onset, K dyad
 * bk1 30.05 / bk2 37.57, stop B a1max 61.72) with only the K drive rebuilt at strap level. The hub-2 rim lobe pushes the short arm of a bell crank
 * (MR63ZZ pair, pin in link 1b, boss stacked on link 1b; long arm La 14.9 mm, phase 0.0 deg); an O3 rod with M2 ball links
 * runs beside link 1b to a lateral horn lug of link 1a at hub K (r_h 15.5 mm). J1, J2, J3 encoders give the pose
 * (3 active, K never read, 0 passive translations). Best: CMA P3 (near-touch objective, lead dyad held, RC M2 ball links, r_h at the 15.5 socket floor), fast Bench(60,160) 10.63 near-touch = plain.
 * Geometry exported from docs/concepts/models/sidecar-parallelogram-knuckle-3r.py (mode viz). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 97.8797, "el1": 67.0092, "az2": 40.8897, "el2": 44.7465, "wd": 69.9552, "wa": -10.525, "b3": 0.3702, "lE": 67.832, "lc": 28.8341, "phiE": -2.7863, "phib": -59.0793, "stk": 4.8534, "ang_min": 24.7893, "bk1": 30.05, "bk2": 37.57, "sK": -1, "a1max": 61.72, "smhi": 19.3517, "smlo": 5.0, "capK": 6.0, "law_mode": "seg", "kA": 1.3487, "t1": 6.0, "kB": 1.3487, "smt": 12.0, "kK": 1.3487, "i_rock": 3.386307846167833, "r_horn": 15.5, "r_lobe": 7.0578, "arm_lo": 1.0, "La": 14.8984, "r_h": 15.5, "beta": -95.8268, "gam": 0.0, "s_arm": 4.3996, "hl": 3.15, "zr": 0.0};
  const G = {"u": [[0.05355, 0.92057, 0.3869], [-0.494, 0.65803, 0.5683], [-0.12506, -0.16019, 0.97913]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-1.81204, -13.82536, -2.4934]], "uK": [-0.31429, 0.94906, 0.0226], "sa": [0.0203, -0.98709, -0.1589], "st": [0.99194, 0.0, 0.1267], "sn": [-0.12506, -0.16019, 0.97913], "A": [36.948, 59.149], "branch": -1.0, "m": [-11.62055, 2.09305, 0.0], "f": [50.05, 60.68, 77.01], "fK": 55.91, "capK": 6.0, "tr": 83.07, "tp": 2.177, "RUN": 0.5, "A0": [-3.70771, -80.70219, -13.67714], "A0m": [-1.86739, -69.23171, -11.56541], "Bm": [-26.1035, -83.85681, -17.05387], "eE": [-0.02795, -0.98592, -0.16487], "psiA": -68.2572, "thLo": 27.2007, "thHi": 76.7455, "q2s": [89.3629, 0.5487], "lawTh": [76.746, 77.584, 78.431, 79.286, 80.148, 81.017, 81.893, 82.774, 83.661, 84.552, 85.447, 86.345, 87.246, 88.149, 89.054, 89.959, 90.865, 91.771, 92.676, 93.58, 94.481, 95.38, 96.275, 97.166, 98.053, 98.934, 99.81, 100.679, 101.54, 102.393, 103.238, 104.073, 104.898, 105.711, 106.513, 107.303, 108.079, 108.84, 109.587, 110.318, 111.032, 111.728, 112.406, 113.064, 113.703, 114.32, 114.915, 115.487, 116.035, 116.558, 117.056, 117.528], "lawDK": [-0.0, -1.079, -2.158, -3.237, -4.316, -5.395, -6.474, -7.553, -8.632, -9.711, -10.79, -11.869, -12.948, -14.026, -15.105, -16.184, -17.263, -18.342, -19.421, -20.5, -21.579, -22.658, -23.737, -24.816, -25.895, -26.974, -28.053, -29.132, -30.211, -31.29, -32.369, -33.448, -34.527, -35.606, -36.685, -37.764, -38.843, -39.922, -41.0, -42.079, -43.158, -44.237, -45.316, -46.395, -47.474, -48.553, -49.632, -50.711, -51.79, -52.869, -53.948, -55.027], "lawQ2": [0.549, -0.251, -1.051, -1.851, -2.651, -3.451, -4.251, -5.051, -5.851, -6.651, -7.451, -8.251, -9.051, -9.851, -10.651, -11.451, -12.251, -13.051, -13.851, -14.651, -15.451, -16.251, -17.051, -17.851, -18.651, -19.451, -20.251, -21.051, -21.851, -22.651, -23.451, -24.251, -25.051, -25.851, -26.651, -27.451, -28.251, -29.051, -29.851, -30.651, -31.451, -32.251, -33.051, -33.851, -34.651, -35.451, -36.251, -37.051, -37.851, -38.651, -39.451, -40.251], "emb": "rod", "rocker": [-27.286, 50.282, 22.484], "rockerAx": [-0.4439, 0.81801, 0.36579], "rodA": [-40.958, 49.247, 15.998], "rodB": [-33.08, 57.757, -6.577], "armA": [-27.286, 50.282, 22.484], "armB": [-38.295, 44.339, 13.803], "L1a": [[-1.94, 49.58, 11.68], [-6.61, 52.26, 7.71], [-6.54, 52.14, 10.68], [-7.94, 51.65, 12.05], [-7.17, 46.86, 13.73], [-13.13, 54.31, 10.98]], "L1b": [[-25.78, 53.45, 10.25], [-26.15, 48.18, 14.77], [-28.04, 45.92, 19.92], [-24.01, 54.02, 11.13], [-24.27, 48.3, 15.48], [-26.13, 46.07, 20.59], [-22.23, 54.58, 12.02], [-22.3, 48.15, 16.08], [-24.14, 46.02, 21.16], [-20.46, 55.15, 12.91], [-20.35, 47.94, 16.64], [-22.02, 45.57, 21.52]], "L2": [[-33.48, 34.25, 43.56], [-30.94, 24.88, 49.5], [-29.69, 16.19, 57.65], [-27.14, 5.89, 64.21], [-22.81, -5.47, 67.12], [-19.84, -19.14, 76.2], [-29.53, 26.95, 48.64], [-28.09, 18.38, 56.45], [-25.53, 8.39, 62.85], [-21.4, -2.66, 66.05], [-18.0, -15.31, 73.47], [-28.17, 29.02, 47.85], [-27.11, 20.93, 56.46], [-24.39, 10.96, 62.59], [-20.05, 0.02, 65.05], [-16.24, -11.76, 70.6], [-26.85, 31.13, 47.14], [-25.87, 23.29, 55.92], [-23.46, 13.63, 62.86], [-19.36, 2.69, 66.12], [-14.55, -8.49, 67.6]], "hornA": [-27.184, 54.903, -3.823], "hornB": [-31.666, 53.486, -6.679]};
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
    id: 'sidecar-parallelogram-knuckle-3r', name: 'Sidecar parallelogram K drive on the lead chain: hub-2 lobe -> bell crank on link 1b -> strap-level O3 rod on M2 ball links -> horn of link 1a slaves K to q2 (3 active, K not read)',
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
