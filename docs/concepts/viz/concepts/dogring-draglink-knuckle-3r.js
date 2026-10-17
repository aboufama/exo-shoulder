/* dogring-draglink-knuckle-3r at its best fast configuration: the slipper-nose lead's chain (seats, pin knee, b3 tilt) on a
 * long K dyad (bk1 34.0 / bk2 46.0, stop B a1max 74.5), link 1 split by a passive O20 knuckle K SLAVED to q2 by a POSITIVE
 * coaxial drive: past the onset link 2's root flank (the dog) turns a 17-4PH dog sector on hub 2's housing 1:1 with q2
 * (ring layer 1: above link 2's root, f2 + 6.3), the sector's Ti arm carries an O8 eye, a spherical Ti drag link runs to a horn lug on hub K's
 * housing (link 1a) stacked above link 1b's root (hl 7.61). Spherical 4R, every axis through GH, PA <= 42 deg; drive range
 * dK_lim 60.8 deg. 3 active, K never read, 0 passive translations. Geometry from docs/concepts/models/dogring-draglink-knuckle-3r.py (mode viz). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 95.3929, "el1": 67.8974, "az2": 45.8211, "el2": 41.0855, "wd": 66.8662, "wa": -10.6559, "b3": 0.329, "lE": 67.832, "lc": 21.1499, "phiE": -2.7863, "phib": -58.8084, "stk": 4.8534, "ang_min": 25.2189, "bk1": 34.0, "bk2": 46.0, "a1max": 74.5, "smhi": 19.29, "smlo": 5.0, "capK": 6.0, "dr_a1": 26.6, "dr_t1": 4.06, "dr_a3": 17.57, "dr_t3": -48.09, "root_off": -23.1, "ring_layer": 1, "dr_hl": 7.61, "dr_zr": 0.0, "dl_a": 1, "dl_h": -1, "dl_lift": 0.58, "sector_gap": 0.5};
  const G = {"u": [[0.03536, 0.92651, 0.3746], [-0.46545, 0.61682, 0.63474], [-0.13912, -0.22062, 0.96539]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-0.73949, -13.44608, -3.17939]], "uK": [-0.34596, 0.93574, -0.06861], "sa": [0.03147, -0.97536, -0.21836], "st": [0.98978, 0.0, 0.14263], "sn": [-0.13912, -0.22062, 0.96539], "A": [37.552, 57.218], "branch": -1.0, "m": [-11.73928, 1.1848, 0.0], "f": [49.37, 61.5, 80.04], "fK": 58.64, "capK": 6.0, "tr": 87.71, "tp": 2.177, "RUN": 0.5, "A0": [-1.8712, -79.52847, -18.44428], "A0m": [-1.06791, -68.07845, -15.71185], "Bm": [-18.63073, -78.76212, -20.68426], "eE": [-0.01668, -0.97421, -0.22504], "psiA": -57.3686, "thLo": 24.6667, "thHi": 75.4801, "q2s": [102.0679, 12.3249], "lawTh": [75.48, 76.249, 77.039, 77.85, 78.679, 79.528, 80.395, 81.28, 82.181, 83.098, 84.03, 84.975, 85.934, 86.903, 87.883, 88.873, 89.87, 90.875, 91.886, 92.902, 93.923, 94.946, 95.971, 96.998, 98.026, 99.053, 100.079, 101.103, 102.125, 103.143, 104.158, 105.169, 106.175, 107.176, 108.171, 109.16, 110.143, 111.119, 112.087, 113.049, 114.002, 114.948, 115.886, 116.815, 117.736, 118.648, 119.552, 120.448, 121.335, 122.214, 123.086], "lawDK": [-0.0, -0.983, -1.99, -3.019, -4.069, -5.137, -6.223, -7.324, -8.439, -9.567, -10.707, -11.856, -13.013, -14.179, -15.35, -16.526, -17.706, -18.89, -20.075, -21.263, -22.451, -23.64, -24.829, -26.018, -27.206, -28.394, -29.581, -30.768, -31.955, -33.142, -34.329, -35.517, -36.706, -37.897, -39.092, -40.29, -41.494, -42.703, -43.92, -45.146, -46.382, -47.631, -48.895, -50.176, -51.478, -52.804, -54.157, -55.543, -56.968, -58.439, -59.965], "lawQ2": [12.325, 11.525, 10.725, 9.925, 9.125, 8.325, 7.525, 6.725, 5.925, 5.125, 4.325, 3.525, 2.725, 1.925, 1.125, 0.325, -0.475, -1.275, -2.075, -2.875, -3.675, -4.475, -5.275, -6.075, -6.875, -7.675, -8.475, -9.275, -10.075, -10.875, -11.675, -12.475, -13.275, -14.075, -14.875, -15.675, -16.475, -17.275, -18.075, -18.875, -19.675, -20.475, -21.275, -22.075, -22.875, -23.675, -24.475, -25.275, -26.075, -26.875, -27.675], "emb": "rod", "dogK": [0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 22.0, 24.0, 26.0, 28.0, 30.0, 32.0, 34.0, 36.0, 38.0, 40.0, 42.0, 44.0, 46.0, 48.0, 50.0, 52.0, 54.0, 56.0, 58.0, 60.0], "dogPhi": [0.0, -1.608, -3.148, -4.637, -6.086, -7.505, -8.9, -10.278, -11.643, -12.999, -14.349, -15.696, -17.042, -18.388, -19.735, -21.082, -22.43, -23.779, -25.125, -26.469, -27.806, -29.136, -30.453, -31.754, -33.035, -34.291, -35.517, -36.708, -37.859, -38.964, -40.018], "dKlim": 60.75, "ring": [-31.556, 41.818, 43.033], "ringAx": [-0.46545, 0.61682, 0.63474], "armA": [-36.758, 47.302, 31.745], "armB": [-27.293, 50.945, 14.377], "rodA": [-29.003, 54.136, 15.277], "rodB": [-37.674, 51.211, 3.598], "horn": [-39.194, 53.278, 3.743], "hornRoot": [-32.026, 58.935, -0.305], "L1a": [[-3.03, 49.44, 9.8], [-7.06, 52.23, 5.87], [-4.42, 49.02, 10.98], [-8.51, 51.78, 7.1], [-5.8, 48.59, 12.16], [-9.96, 51.33, 8.34], [-7.18, 48.17, 13.34], [-11.42, 50.9, 9.59]], "L1b": [[-27.75, 56.19, 5.7], [-25.83, 48.3, 10.29], [-27.11, 46.8, 15.57], [-28.2, 44.83, 20.81], [-29.86, 43.54, 26.68], [-24.94, 53.31, 7.87], [-24.43, 48.11, 12.52], [-25.62, 46.47, 17.76], [-26.61, 44.37, 22.94], [-29.9, 45.64, 30.61], [-22.25, 50.34, 9.74], [-23.01, 47.83, 14.71], [-24.0, 45.86, 19.81], [-25.1, 44.02, 25.11], [-22.2, 58.38, 7.64], [-20.3, 48.77, 11.65], [-21.4, 47.12, 16.72], [-22.46, 45.37, 21.87], [-24.64, 45.6, 28.5]], "L2": [[-32.01, 31.7, 47.57], [-29.69, 22.01, 52.72], [-28.07, 12.63, 59.14], [-25.31, 2.12, 63.58], [-21.6, -9.04, 66.02], [-20.05, -23.94, 77.81], [-28.28, 24.1, 52.05], [-27.06, 15.11, 59.35], [-24.39, 4.66, 64.16], [-20.37, -6.38, 65.75], [-18.14, -20.0, 75.35], [-26.89, 26.17, 51.39], [-26.07, 17.65, 59.65], [-23.55, 7.27, 65.0], [-19.67, -3.89, 67.21], [-16.3, -16.31, 72.74], [-25.4, 28.1, 50.52], [-24.84, 20.05, 59.41], [-22.53, 9.86, 65.39], [-18.84, -1.32, 68.28], [-14.56, -12.88, 69.99]]};
  const u = G.u, c = G.c, uK = G.uK, sn = G.sn, sa = G.sa, st = G.st, a1 = G.A[0], a2 = G.A[1], hub = 12.25, rad = 10;
  const wrapR = a => { a = (a + Math.PI) % (2 * Math.PI); return (a < 0 ? a + 2 * Math.PI : a) - Math.PI; };
  const pe = P.phiE * D2R, pb = P.phib * D2R, lE = P.lE, lc = P.lc;
  const A02 = [G.m[0] + lE * Math.cos(pe), G.m[1] + lE * Math.sin(pe)], B2 = [A02[0] + lc * Math.cos(pb), A02[1] + lc * Math.sin(pb)];
  const kbr = Math.sign(wrapR(pe - Math.atan2(B2[1] - G.m[1], B2[0] - G.m[0]))) || 1;
  const vref = V.unit(V.cross(u[2], [0.3, 0.5, 0.8]));
  const cb = x => Math.cos(x * D2R), sb = x => Math.sin(x * D2R);
  /** physical J2 stop: th (deg) inside [thLo, thHi] -> K on stop A (state 0); else J2 locked on its q2 stop, K opens */
  const dot = V.dot;
  const phiOf = dK => { const k = Math.abs(dK), X = G.dogK, Y = G.dogPhi, n = X.length; if (k <= X[0]) return 0; let j = 0;
    while (j < n - 2 && X[j + 1] < k) j++; const a = Math.max(0, Math.min(1, (k - X[j]) / Math.max(X[j + 1] - X[j], 1e-9))); return Y[j] + a * (Y[j + 1] - Y[j]); };
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
    return { q1, dK, q2: q2s, ok: ok && Math.abs(dK) <= G.dKlim, L: { state } };
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
    if (!k.ok) return k.L.state === 1 ? 'past the drive stop B (drive range dK_lim / pressure angle / lift-off)' : (k.L.state === -1 ? 'folded side: J2 on its dowel (no tooth)' : 'chain cannot close');
    const F = fk(q), sv = M.mulv(M.T(Q), F.t3), kn = knee([V.dot(sv, sa), V.dot(sv, st)]);
    if (!kn.span) return 'knee span: the drift is beyond lE + lc';
    if (kn.ang < P.ang_min || kn.ang > 180 - P.ang_min) return `knee angle ${kn.ang.toFixed(0)} deg outside [${P.ang_min}, ${180 - P.ang_min}]`;
    return null;
  };
  const closes = (q, ctx) => { const r = C.residual(q, ctx); return Math.max(...r.map(Math.abs)) <= 0.5; };
  const solveC = (ctx, qPrev) => { const q = solve(ctx); return (!qPrev || closes(q, ctx)) ? q : K.dls(C, ctx, qPrev, { iters: 40 }).q; };
  const C = {
    id: 'dogring-draglink-knuckle-3r', name: 'Dog-ring drag-link knuckle: link 2 root flank turns a dog sector on hub 2 -> Ti arm -> spherical drag link -> horn of link 1a on hub K (3 active, K not read)',
    dof: { active: 3, passive: 6 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'K (passive, slaved to q2 by dog sector - arm - drag link - horn)', 'J2', 'J3', 'knee pin a', 'knee pin b'], qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
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
        { kind: 'hub', role: 'passive', name: 'dog sector (17-4PH C-sector on hub 2 housing, turned by link 2 root flank past the onset)', c: on(F.R1b, M.mulv(M.rot(u[1], phiOf(q[1])), G.ring)), axis: Wd(M.mulv(F.R1b, u[1])), r: 12.5, h: 3 },
        { kind: 'link', role: 'link', name: 'sector arm (6 x 3 Ti, turns with the sector)', a: on(F.R1b, M.mulv(M.rot(u[1], phiOf(q[1])), G.armA)), b: on(F.R1b, M.mulv(M.rot(u[1], phiOf(q[1])), G.armB)), r: 1.5 },
        { kind: 'link', role: 'link', name: 'spherical drag link (6 x 3 Ti, O8 eyes on MR63ZZ, radial pins through GH)', a: on(F.R1b, M.mulv(M.rot(u[1], phiOf(q[1])), G.rodA)), b: on(F.R1, G.rodB), r: 1.5 },
        { kind: 'link', role: 'link', name: 'horn lug on hub K housing (link 1a), above link 1b root', a: on(F.R1, G.hornRoot), b: on(F.R1, G.horn), r: 1.5 },
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
