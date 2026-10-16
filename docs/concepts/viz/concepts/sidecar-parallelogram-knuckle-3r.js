/* sidecar-parallelogram-knuckle-3r (round 8, pick 1) at its best measured configuration: the verified lead's slaved
 * knuckle chain UNCHANGED (pin knee, link 1 split by a passive O20 knuckle K SLAVED to q2 past the onset, K dyad
 * bk1 30.05 / bk2 37.57, stop B a1max 61.72) with only the K drive rebuilt at strap level. The hub-2 rim lobe pushes the short arm of a bell crank
 * (MR63ZZ pair, pin in link 1b, boss stacked on link 1b; long arm La 17.4 mm, phase 0.0 deg); an O3 rod with M2 ball links
 * runs beside link 1b to a lateral horn lug of link 1a at hub K (r_h 16.2 mm). J1, J2, J3 encoders give the pose
 * (3 active, K never read, 0 passive translations). Coarse LHS best (placeholder).
 * Geometry exported from docs/concepts/models/sidecar-parallelogram-knuckle-3r.py (mode viz). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 98.0555, "el1": 67.4863, "az2": 41.4565, "el2": 44.4981, "wd": 64.8727, "wa": -10.4373, "b3": 0.4478, "lE": 67.832, "lc": 24.9347, "phiE": -2.7863, "phib": -72.0315, "stk": 4.8534, "ang_min": 26.7778, "bk1": 30.05, "bk2": 37.57, "sK": -1, "a1max": 61.72, "smhi": 17.7672, "smlo": 5.0, "capK": 6.0, "law_mode": "seg", "kA": 1.324, "t1": 6.0, "kB": 1.324, "smt": 12.0, "kK": 1.324, "i_rock": 4.010574469552424, "r_horn": 16.2374, "r_lobe": 7.0673, "arm_lo": 1.0, "La": 17.4464, "r_h": 16.2374, "beta": -82.8168, "gam": 0.0, "s_arm": 4.3501, "hl": 2.7283, "zr": 0.9924};
  const G = {"u": [[0.05366, 0.92379, 0.37913], [-0.48876, 0.65598, 0.57516], [-0.11531, -0.17779, 0.97729]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-1.59673, -19.79096, -3.78873]], "uK": [-0.32369, 0.94585, 0.02424], "sa": [0.02083, -0.98407, -0.17656], "st": [0.99311, 0.0, 0.11718], "sn": [-0.11531, -0.17779, 0.97729], "A": [37.078, 59.879], "branch": -1.0, "m": [-16.73099, 1.96261, 0.0], "f": [49.87, 60.52, 78.82], "fK": 55.84, "capK": 6.0, "tr": 84.8, "tp": 2.177, "RUN": 0.5, "A0": [-3.45992, -86.46342, -16.13747], "A0m": [-1.85939, -69.99897, -12.95345], "Bm": [-25.25427, -77.56863, -17.09093], "eE": [-0.02747, -0.98291, -0.18205], "psiA": -68.5317, "thLo": 27.8012, "thHi": 79.1894, "q2s": [90.7877, -1.4992], "lawTh": [79.189, 80.022, 80.862, 81.709, 82.563, 83.422, 84.286, 85.155, 86.028, 86.905, 87.784, 88.666, 89.549, 90.434, 91.319, 92.204, 93.088, 93.971, 94.852, 95.73, 96.606, 97.478, 98.345, 99.207, 100.064, 100.914, 101.757, 102.593, 103.42, 104.238, 105.046, 105.843, 106.629, 107.402, 108.163, 108.91, 109.642, 110.359, 111.06, 111.743, 112.409, 113.056, 113.683, 114.29, 114.875, 115.438, 115.978, 116.494, 116.985, 117.45, 117.889, 118.3, 118.683, 119.038, 119.362], "lawDK": [-0.0, -1.059, -2.118, -3.178, -4.237, -5.296, -6.355, -7.414, -8.474, -9.533, -10.592, -11.651, -12.71, -13.77, -14.829, -15.888, -16.947, -18.006, -19.066, -20.125, -21.184, -22.243, -23.302, -24.362, -25.421, -26.48, -27.539, -28.598, -29.658, -30.717, -31.776, -32.835, -33.894, -34.954, -36.013, -37.072, -38.131, -39.19, -40.25, -41.309, -42.368, -43.427, -44.486, -45.546, -46.605, -47.664, -48.723, -49.782, -50.842, -51.901, -52.96, -54.019, -55.078, -56.138, -57.197], "lawQ2": [-1.499, -2.299, -3.099, -3.899, -4.699, -5.499, -6.299, -7.099, -7.899, -8.699, -9.499, -10.299, -11.099, -11.899, -12.699, -13.499, -14.299, -15.099, -15.899, -16.699, -17.499, -18.299, -19.099, -19.899, -20.699, -21.499, -22.299, -23.099, -23.899, -24.699, -25.499, -26.299, -27.099, -27.899, -28.699, -29.499, -30.299, -31.099, -31.899, -32.699, -33.499, -34.299, -35.099, -35.899, -36.699, -37.499, -38.299, -39.099, -39.899, -40.699, -41.499, -42.299, -43.099, -43.899, -44.699], "emb": "rod", "rocker": [-27.248, 50.007, 22.693], "rockerAx": [-0.44447, 0.81573, 0.37017], "rodA": [-44.427, 47.172, 18.694], "rodB": [-35.626, 56.151, -3.188], "armA": [-27.248, 50.007, 22.693], "armB": [-41.76, 42.278, 16.473], "L1a": [[-3.69, 50.08, 10.05], [-4.99, 49.6, 11.4], [-6.29, 49.12, 12.75], [-7.59, 48.64, 14.11]], "L1b": [[-26.09, 53.17, 10.49], [-26.26, 47.83, 15.02], [-28.03, 45.62, 20.21], [-24.3, 53.76, 11.34], [-24.36, 47.95, 15.67], [-26.12, 45.81, 20.85], [-22.51, 54.35, 12.19], [-22.39, 47.87, 16.25], [-24.09, 45.72, 21.35], [-20.73, 54.94, 13.03], [-20.41, 47.62, 16.75], [-21.97, 45.33, 21.69]], "L2": [[-33.28, 34.16, 43.44], [-31.03, 24.88, 48.9], [-30.45, 16.57, 57.17], [-28.71, 6.58, 64.22], [-25.23, -4.71, 68.16], [-20.14, -16.05, 67.91], [-29.79, 31.65, 42.73], [-29.35, 24.22, 50.72], [-28.11, 15.48, 58.03], [-25.99, 5.43, 64.47], [-22.18, -5.72, 67.51], [-17.48, -17.14, 68.36], [-28.41, 31.33, 44.86], [-27.78, 23.68, 52.82], [-26.22, 14.64, 59.85], [-23.3, 4.29, 64.59], [-19.3, -6.7, 67.05], [-15.44, -19.0, 71.75], [-26.98, 30.98, 47.0], [-26.16, 23.1, 54.96], [-24.41, 13.85, 61.99], [-20.93, 3.22, 65.53], [-16.47, -7.64, 66.44], [-12.61, -20.08, 72.01]], "hornA": [-28.512, 53.784, -1.471], "hornB": [-34.169, 51.895, -3.297]};
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
