/* spiral-lobe-longdyad-knuckle-3r at its best gate-0 cell (DEAD at gate 0): inband-rssr pick3's chain and RSSR K drive on the
 * efficient 34/48 K dyad (stop B 76.5), linear hub-2 lobe law kK 2.8 with the onset at margin 14 (frozen exact ghost 17.86,
 * 269 ws taken, 8 contact poses: link 2 / hub 2 into the posterior deltoid at plane -90..-75, elev 45-60, axial 120-135).
 * Bell crank on a joggled ear of link 1b, O3 rod to the horn lug of link 1a at hub K; pin knee; 3 active, K slaved, not read.
 * Geometry exported from docs/concepts/models/spiral-lobe-longdyad-knuckle-3r.py (mode viz). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 95.3275, "el1": 67.6601, "az2": 46.3741, "el2": 41.5718, "wd": 66.0692, "wa": -10.7812, "b3": 0.3246, "lE": 67.832, "lc": 21.5474, "phiE": -2.7863, "phib": -57.916, "stk": 4.8534, "ang_min": 25.2189, "bk1": 34.0, "bk2": 48.0, "sK": -1, "a1max": 76.5, "smhi": 14.0, "smlo": 5.0333, "capK": 6.0, "law_mode": "seg", "kA": 2.8, "t1": 6.0, "kB": 2.8, "smt": 8.0, "kK": 2.8, "i_rock": 6.0, "r_horn": 15.25, "r_lobe": 8.0, "arm_lo": 1.0};
  const G = {"u": [[0.03529, 0.92495, 0.37846], [-0.45858, 0.62409, 0.63262], [-0.13867, -0.23452, 0.96217]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-0.8423, -13.51955, -3.41666]], "uK": [-0.30372, 0.94777, -0.09744], "sa": [0.03345, -0.97211, -0.23212], "st": [0.98977, -0.0, 0.14265], "sn": [-0.13867, -0.23452, 0.96217], "A": [36.823, 58.27], "branch": -1.0, "m": [-11.56648, 1.32111, 0.0], "f": [50.55, 61.59, 80.61], "fK": 58.59, "capK": 6.0, "tr": 88.82, "tp": 2.177, "RUN": 0.5, "A0": [-1.83935, -79.38185, -19.61369], "A0m": [-0.9187, -68.13795, -16.7404], "Bm": [-18.60557, -79.26391, -22.00138], "eE": [-0.0147, -0.97096, -0.23878], "psiA": -53.7452, "thLo": 26.4797, "thHi": 81.093, "q2s": [101.5774, 1.6627], "lawTh": [81.093, 82.333, 83.618, 84.943, 86.307, 87.706, 89.139, 90.601, 92.09, 93.604, 95.14, 96.694, 98.266, 99.851, 101.447, 103.051, 104.661, 106.274, 107.887, 109.496, 111.099, 112.693, 114.273, 115.837, 117.382, 118.902, 120.394, 121.853, 123.276, 124.656, 125.989, 127.269, 128.491, 129.649, 130.736, 131.746], "lawDK": [-0.0, -2.24, -4.48, -6.72, -8.96, -11.2, -13.44, -15.68, -17.92, -20.16, -22.4, -24.64, -26.88, -29.12, -31.36, -33.6, -35.84, -38.08, -40.32, -42.56, -44.8, -47.04, -49.28, -51.52, -53.76, -56.0, -58.24, -60.48, -62.72, -64.96, -67.2, -69.44, -71.68, -73.92, -76.16, -78.4], "lawQ2": [1.663, 0.863, 0.063, -0.737, -1.537, -2.337, -3.137, -3.937, -4.737, -5.537, -6.337, -7.137, -7.937, -8.737, -9.537, -10.337, -11.137, -11.937, -12.737, -13.537, -14.337, -15.137, -15.937, -16.737, -17.537, -18.337, -19.137, -19.937, -20.737, -21.537, -22.337, -23.137, -23.937, -24.737, -25.537, -26.337], "emb": "rod", "rocker": [-23.936, 48.028, 27.125], "rockerAx": [-0.39808, 0.79876, 0.45112], "rodA": [-42.234, 49.556, 11.598], "rodB": [-26.403, 60.926, -20.306], "armA": [-23.936, 48.028, 27.125], "armB": [-39.845, 44.763, 8.891], "L1a": [[-2.16, 50.7, 9.85], [-5.65, 52.34, 5.33], [-3.68, 50.32, 10.91], [-7.2, 51.94, 6.42], [-5.2, 49.95, 11.97], [-8.76, 51.56, 7.51], [-6.72, 49.57, 13.04], [-10.31, 51.18, 8.6]], "L1b": [[-25.49, 57.36, 3.76], [-23.96, 49.32, 8.53], [-25.78, 48.58, 13.95], [-27.26, 46.98, 19.34], [-28.45, 44.7, 24.63], [-23.64, 58.03, 4.45], [-22.25, 49.73, 9.1], [-24.02, 49.0, 14.52], [-25.53, 47.54, 19.95], [-26.78, 45.42, 25.32], [-21.78, 58.69, 5.14], [-20.51, 50.07, 9.66], [-22.28, 49.44, 15.09], [-23.77, 48.03, 20.53], [-25.03, 45.99, 25.94], [-19.92, 59.36, 5.83], [-18.77, 50.33, 10.2], [-20.53, 49.84, 15.65], [-21.98, 48.43, 21.07], [-23.21, 46.44, 26.48]], "L2": [[-31.75, 32.31, 47.44], [-29.44, 22.54, 52.29], [-28.32, 13.42, 59.29], [-25.71, 2.9, 63.68], [-22.23, -8.24, 66.2], [-20.22, -22.14, 75.12], [-28.12, 25.94, 50.38], [-27.67, 17.58, 58.71], [-25.41, 7.28, 64.03], [-21.77, -3.8, 66.21], [-18.26, -15.64, 69.52], [-26.9, 29.34, 48.63], [-26.31, 21.22, 56.6], [-24.71, 11.56, 63.36], [-21.6, 0.61, 67.08], [-17.35, -10.63, 67.64], [-26.88, 34.23, 49.07], [-24.98, 24.72, 54.53], [-23.84, 15.71, 62.25], [-21.33, 5.09, 67.65], [-17.39, -6.32, 69.49], [-14.12, -19.63, 76.59]], "earA": [-23.2792, 46.71, 26.3807], "earB": [-24.0732, 43.2667, 29.2018], "hornA": [-24.5877, 61.9468, -16.0375], "hornB": [-26.403, 60.926, -20.306]};
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
    id: 'spiral-lobe-longdyad-knuckle-3r', name: 'Spiral-lobe long-dyad knuckle: 34/48 K dyad, hub-2 lobe law (onset 14), in-band RSSR crank -> O3 rod -> horn of link 1a (3 active, K not read; dead at gate 0)',
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
        { kind: 'link', role: 'link', name: 'ear of link 1b (3 mm Ti tab, one layer down, carries the crank pin)', a: on(F.R1b, G.earB), b: on(F.R1b, G.earA), r: 2.5 },
        { kind: 'link', role: 'link', name: 'bell crank long arm (3 mm Ti, in link 1b\'s layer beside the strap)', a: on(F.R1b, G.armA), b: on(F.R1b, G.armB), r: 1.5 },
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
