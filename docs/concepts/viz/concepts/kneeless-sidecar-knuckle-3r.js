/* kneeless-sidecar-knuckle-3r at its best measured configuration (seed wd 75 / wa -7): the verified lead's slaved knuckle and
 * strap-level sidecar drive (hub-2 rim lobe -> bell crank on link 1b -> O3 rod with M2 ball links -> horn lug of link 1a),
 * with J3 on a GH ray (b3 0) and the two-pin knee DELETED: every active axis passes through GH, so member 3 has no drift
 * relative to the arm and hub 3's lower plate carries ONE rigid bent 3 mm Ti bracket (E strap -> bend -> plate -> arm pad).
 * 3 active (J1, J2, J3 encoded), K slaved and never read, 0 passive translations, 0 sensed passives.
 * Geometry exported from docs/concepts/models/kneeless-sidecar-knuckle-3r.py (mode viz). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 96.6954, "el1": 67.5865, "az2": 42.2031, "el2": 44.4209, "wd": 75.0, "wa": -7.0, "b3": 0.0, "lE": 67.832, "lc": 25.6915, "phiE": -2.7863, "phib": -60.7036, "stk": 6.5, "ang_min": 0.0, "bk1": 28.9414, "bk2": 39.236, "sK": -1, "a1max": 63.1774, "smhi": 16.5464, "smlo": 5.0, "capK": 6.0, "law_mode": "seg", "kA": 1.6232, "t1": 6.0, "kB": 1.6232, "smt": 12.0, "kK": 1.6232, "i_rock": 3.771585521517141, "r_horn": 14.8706, "r_lobe": 7.7447, "arm_lo": 1.0};
  const G = {"u": [[0.04445, 0.92446, 0.37869], [-0.48388, 0.65788, 0.57711], [-0.11772, -0.25882, 0.95873]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-0.0, 0.0, 0.0]], "uK": [-0.28947, 0.95715, 0.00829], "sa": [0.03154, -0.96593, -0.25689], "st": [0.99255, -0.0, 0.12187], "sn": [-0.11772, -0.25882, 0.95873], "A": [36.369, 63.898], "branch": -1.0, "m": [0.0, 0.0, 0.0], "f": [49.72, 60.2, 79.5], "fK": 55.32, "capK": 6.0, "tr": 91.14, "tp": 3.0, "RUN": 0.5, "A0": [-1.13576, -65.44322, -17.8066], "A0m": [-1.13576, -65.44322, -17.8066], "Bm": [-22.97778, -77.58642, -23.76666], "eE": [-0.01674, -0.96478, -0.26251], "psiA": -65.4036, "thLo": 32.5289, "thHi": 83.72, "q2s": [92.9113, -1.1058], "lawTh": [83.72, 84.594, 85.481, 86.379, 87.289, 88.21, 89.14, 90.079, 91.025, 91.979, 92.939, 93.904, 94.874, 95.848, 96.825, 97.803, 98.783, 99.763, 100.742, 101.72, 102.695, 103.667, 104.634, 105.596, 106.551, 107.499, 108.438, 109.368, 110.287, 111.194, 112.089, 112.968, 113.833, 114.681, 115.511, 116.321, 117.112, 117.88, 118.624, 119.344, 120.038, 120.705, 121.342], "lawDK": [-0.0, -1.299, -2.597, -3.896, -5.194, -6.493, -7.791, -9.09, -10.388, -11.687, -12.986, -14.284, -15.583, -16.881, -18.18, -19.478, -20.777, -22.076, -23.374, -24.673, -25.971, -27.27, -28.568, -29.867, -31.165, -32.464, -33.763, -35.061, -36.36, -37.658, -38.957, -40.255, -41.554, -42.852, -44.151, -45.45, -46.748, -48.047, -49.345, -50.644, -51.942, -53.241, -54.54], "lawQ2": [-1.106, -1.906, -2.706, -3.506, -4.306, -5.106, -5.906, -6.706, -7.506, -8.306, -9.106, -9.906, -10.706, -11.506, -12.306, -13.106, -13.906, -14.706, -15.506, -16.306, -17.106, -17.906, -18.706, -19.506, -20.306, -21.106, -21.906, -22.706, -23.506, -24.306, -25.106, -25.906, -26.706, -27.506, -28.306, -29.106, -29.906, -30.706, -31.506, -32.306, -33.106, -33.906, -34.706], "emb": "rod", "rocker": [-26.3, 50.024, 22.838], "rockerAx": [-0.43146, 0.82065, 0.37467], "rodA": [-42.056, 47.626, 17.553], "rodB": [-31.874, 57.758, -5.033], "armA": [-26.3, 50.024, 22.838], "armB": [-39.467, 42.703, 15.305], "L1a": [[-2.98, 49.93, 9.76], [-4.4, 49.49, 11.0], [-5.82, 49.05, 12.25], [-7.24, 48.61, 13.49]], "L1b": [[-24.42, 53.61, 9.75], [-24.67, 47.67, 14.29], [-26.86, 45.76, 19.7], [-22.64, 54.15, 10.64], [-22.85, 47.84, 15.02], [-24.95, 45.86, 20.37], [-20.85, 54.68, 11.53], [-20.96, 47.77, 15.65], [-22.96, 45.74, 20.92], [-19.07, 55.21, 12.42], [-19.03, 47.51, 16.21], [-21.14, 45.87, 21.57]], "L2": [[-31.96, 34.16, 44.03], [-28.83, 25.12, 49.95], [-27.18, 16.98, 58.72], [-24.0, 7.0, 65.38], [-19.75, -4.21, 70.32], [-28.46, 30.98, 45.1], [-26.53, 23.17, 52.82], [-24.2, 14.45, 60.65], [-20.5, 4.19, 66.29], [-17.58, -7.82, 77.85], [-26.47, 29.41, 48.36], [-23.99, 21.01, 55.34], [-21.02, 11.81, 62.06], [-17.2, 1.42, 67.88], [-27.17, 36.59, 45.28], [-24.24, 27.61, 51.37], [-21.4, 18.82, 57.87], [-18.0, 9.25, 63.98], [-14.29, -1.44, 71.74]], "hornA": [-26.688, 54.611, -3.434], "hornB": [-34.125, 52.389, -6.568]};
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
    const q3 = K.axisAngle(u[2], vref, M.mulv(M.T(R12), M.mulv(Q, vref)));
    return [k.q1, k.dK, k.q2, K.wrap180(q3)];
  }
  function fk(q) {
    const X = chain(q[0], q[1], q[2], q[3]), Rm3 = X.R123;
    const pa = V.add(M.mulv(Rm3, G.A0), X.t3), pb = V.add(M.mulv(Rm3, G.Bm), X.t3);
    return Object.assign(X, { Rm3, pa, pb });
  }
  const check = (q, ctx) => {
    const Q = Qof(ctx), k = ik(Q);
    if (!k.ok) return k.L.state === 1 ? 'past the drive stop B (stop B / pressure angle / lift-off)' : (k.L.state === -1 ? 'folded side: J2 on its dowel (no tooth)' : 'chain cannot close');
    return null;
  };
  const closes = (q, ctx) => { const r = C.residual(q, ctx); return Math.max(...r.map(Math.abs)) <= 0.5; };
  const solveC = (ctx, qPrev) => { const q = solve(ctx); return (!qPrev || closes(q, ctx)) ? q : K.dls(C, ctx, qPrev, { iters: 40 }).q; };
  const C = {
    id: 'kneeless-sidecar-knuckle-3r', name: 'The lead with its knee deleted: J3 on a GH ray, strap-level sidecar slaving K, one rigid bracket to the arm pad (3 active, K not read)',
    dof: { active: 3, passive: 1 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'K (passive, slaved to q2 by the lobe - bell crank - rod - horn sidecar)', 'J2', 'J3'], qUnits: ['deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve: solveC,
    residual: (q, ctx) => { const F = fk(q); return M.rotErrDeg(F.Rm3, Qof(ctx)).concat(F.t3); },
    check,
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), F = fk(q);
      const on = (R, p) => W(M.mulv(R, p)), I = M.I3();
      const h1 = { kind: 'hub', role: 'active', name: 'J1 (axis on a GH ray)', c: W(V.scale(u[0], G.f[0])), axis: Wd(u[0]), r: rad, h: hub };
      const hK = { kind: 'hub', role: 'passive', name: 'K (O20, passive, slaved; clock-spring cap, stop A; the horn is a lateral lug of link 1a)', c: on(F.R1, V.scale(uK, G.fK)), axis: Wd(M.mulv(F.R1, uK)), r: rad, h: hub + (G.capK || 0) };
      const h2 = { kind: 'hub', role: 'active', name: 'J2 (axis on a GH ray; folded dowel stop, drive stop B)', c: on(F.R1b, V.scale(u[1], G.f[1])), axis: Wd(M.mulv(F.R1b, u[1])), r: rad, h: hub };
      const h3 = { kind: 'hub', role: 'active', name: 'J3 (axis on a GH ray: member 3 rigid with the arm)', c: on(F.R12, V.madd(c[2], u[2], G.f[2])), axis: Wd(M.mulv(F.R12, u[2])), r: rad, h: hub,
                   p0: on(F.R12, c[2]) };
      const n3 = Wd(M.mulv(F.Rm3, sn)), lvl = (p, h) => V.madd(W(p), n3, h), kz = G.tr + 1.5;
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
        { kind: 'link', role: 'link', name: 'bracket, E leg (3 mm Ti, hub 3 lower plate -> bend)', a: rim, b: lvl(F.pa, G.tr + 1.5), r: 2.5 },
        { kind: 'link', role: 'link', name: 'bracket, flat leg (3 mm Ti, bend -> arm pad; replaces the knee link and both pins)', a: lvl(F.pa, G.tr + 1.5), b: lvl(F.pb, G.tr + 1.5), r: 3 },
        { kind: 'plate', role: 'fixed-arm', name: 'arm pad (on the cuff / BOTTOM)', c: padC, z: padN, x: arm(sa), size: [14, 14], t: G.tp },
        { kind: 'link', role: 'fixed-arm', name: 'BOTTOM bar to the cuff (schematic)', a: V.madd(padC, padN, -2), b: lat, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: V.scale(ctx.armAxis, 155), axis: ctx.armAxis, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  };
  K.register(C);
})();
