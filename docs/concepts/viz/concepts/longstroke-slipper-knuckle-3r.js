/* longstroke-slipper-knuckle-3r at its claimed configuration: slipper-nose's chain (the verified seats, pin knee, link 1
 * split by a passive O20 knuckle K SLAVED to q2) with the K sub-dyad re-seated long (bk1 26.00 / bk2 47.22, stop B 68.22) and
 * a phased RSSR K drive: the hub-2 rim lobe pushes the short arm of a bell crank (MR63ZZ pair on link 1b, long arm La 19.7,
 * phase gam 14.6); an O3 rod with M2 ball links runs to a lateral horn lug of link 1a at hub K (r_h 14.7, beta -124.1).
 * Every pressure angle <= 42 deg (transmission >= 48 at both ball ends). Claim (CMA s65n2d, stroke held >= 65): frozen exact Bench(110,360) 21.27, held out 26.19; K used 41.6 deg of its 65.
 * Geometry exported from docs/concepts/models/longstroke-slipper-knuckle-3r.py (LS_DRIVE=rssr, mode viz). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"La": 19.654, "s_arm": 4.0, "r_h": 14.6689, "beta": -124.0829, "gam": 14.5934, "hl": 3.15, "zr": 0.0, "kK": 1.957, "r_lobe": 7.0, "bk1": 26.0, "bk2": 47.2225, "a1max": 68.2225, "smhi": 12.1012, "az1": 95.3929, "el1": 67.8974, "az2": 45.8211, "el2": 41.0855, "wd": 66.8662, "wa": -10.6559, "b3": 0.329, "lE": 67.832, "lc": 21.1499, "phiE": -2.7863, "phib": -58.8084, "stk": 4.8534, "ang_min": 25.2189, "sK": -1, "smlo": 5.0, "capK": 6.0, "law_mode": "seg", "kA": 1.957, "t1": 6.0, "kB": 1.957, "smt": 12.0, "i_rock": 4.9135, "r_horn": 14.6689, "arm_lo": 1.0};
  const G = {"u": [[0.03536, 0.92651, 0.3746], [-0.46545, 0.61682, 0.63474], [-0.13912, -0.22062, 0.96539]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-0.73949, -13.44608, -3.17939]], "uK": [-0.17861, 0.98377, -0.017], "sa": [0.03147, -0.97536, -0.21836], "st": [0.98978, 0.0, 0.14263], "sn": [-0.13912, -0.22062, 0.96539], "A": [37.552, 57.218], "branch": -1.0, "m": [-11.73931, 1.14565, 0.0], "f": [50.45, 61.94, 78.24], "fK": 54.08, "capK": 6.0, "tr": 88.63, "tp": 2.177, "RUN": 0.5, "A0": [-1.8712, -79.52847, -18.44428], "A0m": [-1.10666, -68.07842, -15.71743], "Bm": [-18.66948, -78.76209, -20.68984], "eE": [-0.01668, -0.97421, -0.22504], "psiA": -55.4704, "thLo": 24.6667, "thHi": 82.6689, "q2s": [102.0679, -3.348], "lawTh": [82.669, 83.45, 84.252, 85.072, 85.91, 86.766, 87.637, 88.524, 89.424, 90.338, 91.263, 92.199, 93.146, 94.101, 95.064, 96.033, 97.009, 97.988, 98.972, 99.957, 100.944, 101.93, 102.916, 103.899, 104.878, 105.852, 106.82, 107.781, 108.733, 109.675, 110.605, 111.522, 112.424, 113.31, 114.179, 115.029, 115.858, 116.664, 117.447, 118.204, 118.933, 119.634, 120.304, 120.941, 121.543, 122.11, 122.64, 123.13, 123.579], "lawDK": [-0.0, -1.566, -3.131, -4.697, -6.262, -7.828, -9.394, -10.959, -12.525, -14.09, -15.656, -17.222, -18.787, -20.353, -21.918, -23.484, -25.05, -26.615, -28.181, -29.746, -31.312, -32.878, -34.443, -36.009, -37.574, -39.14, -40.706, -42.271, -43.837, -45.402, -46.968, -48.534, -50.099, -51.665, -53.23, -54.796, -56.362, -57.927, -59.493, -61.058, -62.624, -64.19, -65.755, -67.321, -68.886, -70.452, -72.018, -73.583, -75.149], "lawQ2": [-3.348, -4.148, -4.948, -5.748, -6.548, -7.348, -8.148, -8.948, -9.748, -10.548, -11.348, -12.148, -12.948, -13.748, -14.548, -15.348, -16.148, -16.948, -17.748, -18.548, -19.348, -20.148, -20.948, -21.748, -22.548, -23.348, -24.148, -24.948, -25.748, -26.548, -27.348, -28.148, -28.948, -29.748, -30.548, -31.348, -32.148, -32.948, -33.748, -34.548, -35.348, -36.148, -36.948, -37.748, -38.548, -39.348, -40.148, -40.948, -41.748], "emb": "rod", "rocker": [-25.224, 49.735, 28.711], "rockerAx": [-0.40215, 0.79294, 0.45774], "rodA": [-41.241, 51.871, 17.166], "rodB": [-17.948, 60.767, -14.068], "armA": [-25.224, 49.735, 28.711], "armB": [-38.829, 47.113, 14.419], "L1a": [[-0.18, 50.46, 9.91], [-3.15, 54.56, 9.7], [-6.35, 49.84, 10.76]], "L1b": [[-18.19, 55.0, 7.66], [-19.07, 48.73, 11.97], [-21.54, 47.02, 17.0], [-23.97, 44.92, 22.05], [-29.34, 47.19, 30.22], [-16.44, 48.9, 11.04], [-18.85, 47.3, 15.98], [-21.32, 45.56, 21.06], [-25.29, 46.16, 27.91], [-14.62, 51.68, 10.67], [-16.28, 47.63, 15.03], [-18.83, 46.35, 20.18], [-21.49, 44.88, 25.63], [-12.97, 56.0, 10.52], [-13.76, 47.85, 14.07], [-16.31, 46.89, 19.22], [-18.76, 45.26, 24.44], [-23.69, 48.26, 33.31]], "L2": [[-32.27, 31.88, 47.9], [-29.83, 22.01, 52.89], [-28.94, 12.87, 60.86], [-26.65, 2.05, 66.8], [-22.71, -9.69, 69.19], [-19.67, -23.7, 76.05], [-27.95, 23.73, 51.4], [-27.1, 15.01, 59.37], [-24.98, 4.61, 65.62], [-21.19, -6.83, 68.23], [-17.77, -19.81, 73.61], [-26.77, 25.99, 51.16], [-25.29, 17.02, 57.84], [-23.25, 7.03, 64.13], [-19.69, -4.08, 67.16], [-15.94, -16.17, 71.02], [-25.55, 28.23, 50.86], [-23.73, 19.06, 56.76], [-21.75, 9.39, 63.13], [-18.76, -1.49, 67.97], [-14.33, -12.9, 68.85]], "hornA": [-16.057, 61.174, -10.376], "hornB": [-17.948, 60.767, -14.068]};
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
    id: 'longstroke-slipper-knuckle-3r', name: 'Long-stroke knuckle: K sub-dyad re-seated long, hub-2 lobe -> bell crank -> phased RSSR rod -> horn of link 1a, every PA <= 42 (3 active, K not read)',
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
