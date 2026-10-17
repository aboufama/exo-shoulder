/* dogring-draglink-knuckle-3r at its claimed configuration (frozen exact Bench(110,360) gap 22.64): the slipper-nose lead's
 * chain (seats, pin knee, b3 tilt) on a long K dyad (bk1 34 / bk2 46, stop B a1max 74.5); link 1 split by a passive O20 knuckle K
 * SLAVED to q2 by a POSITIVE coaxial drive: past the onset link 2's root flank (the dog) turns a 17-4PH dog C-sector riding hub 2's
 * housing IN LINK 1B'S SKIN-FACE LAYER 1:1 with q2; the sector's Ti arm joggles up over link 1b's root (link 2 never comes ahead of
 * the lug face) and runs stacked along link 1b to an O8 eye; a spherical Ti drag link runs to a horn lug on hub K's housing (link 1a)
 * stacked above link 1b's root (hl 7.7). Spherical 4R, every axis through GH, PA <= 42 deg; drive range dK_lim 46 deg.
 * 3 active, K never read, 0 passive translations. Geometry from docs/concepts/models/dogring-draglink-knuckle-3r.py (mode viz). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 95.3929, "el1": 67.8974, "az2": 45.8211, "el2": 41.0855, "wd": 66.8662, "wa": -10.6559, "b3": 0.329, "lE": 67.832, "lc": 21.1499, "phiE": -2.7863, "phib": -58.8084, "stk": 4.8534, "ang_min": 25.2189, "bk1": 34.0, "bk2": 46.0, "a1max": 74.5, "smhi": 20.132, "smlo": 5.0, "capK": 6.0, "dr_a1": 26.324, "dr_t1": 3.687, "dr_a3": 17.707, "dr_t3": -43.936, "root_off": -59.3, "ring_layer": 0, "dr_hl": 7.715, "dr_zr": 0.0, "dl_a": 1, "dl_h": -1, "dl_lift": 0.0, "sector_gap": 0.5};
  const G = {"u": [[0.03536, 0.92651, 0.3746], [-0.46545, 0.61682, 0.63474], [-0.13912, -0.22062, 0.96539]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-0.73949, -13.44608, -3.17939]], "uK": [-0.34596, 0.93574, -0.06861], "sa": [0.03147, -0.97536, -0.21836], "st": [0.98978, 0.0, 0.14263], "sn": [-0.13912, -0.22062, 0.96539], "A": [37.552, 57.218], "branch": -1.0, "m": [-11.73931, 1.18538, 0.0], "f": [49.37, 61.46, 80.05], "fK": 58.65, "capK": 6.0, "tr": 87.71, "tp": 2.177, "RUN": 0.5, "A0": [-1.8712, -79.52847, -18.44428], "A0m": [-1.06734, -68.07842, -15.71176], "Bm": [-18.63016, -78.76209, -20.68417], "eE": [-0.01668, -0.97421, -0.22504], "psiA": -57.3686, "thLo": 24.6667, "thHi": 74.6381, "q2s": [102.0679, 14.0098], "lawTh": [74.638, 75.401, 76.185, 76.987, 77.809, 78.649, 79.506, 80.381, 81.271, 82.177, 83.096, 84.029, 84.974, 85.931, 86.898, 87.874, 88.859, 89.851, 90.849, 91.853, 92.862, 93.875, 94.891, 95.909, 96.929, 97.949, 98.971, 99.992, 101.012, 102.031, 103.049, 104.065, 105.079, 106.09, 107.098, 108.103, 109.105, 110.104, 111.1, 112.093, 113.082, 114.069, 115.053, 116.035, 117.016, 117.996, 118.977, 119.96], "lawDK": [-0.0, -0.974, -1.971, -2.987, -4.021, -5.073, -6.141, -7.222, -8.316, -9.422, -10.538, -11.662, -12.794, -13.933, -15.077, -16.226, -17.379, -18.534, -19.693, -20.853, -22.014, -23.177, -24.34, -25.504, -26.669, -27.835, -29.001, -30.169, -31.338, -32.509, -33.683, -34.86, -36.042, -37.228, -38.421, -39.621, -40.83, -42.049, -43.281, -44.527, -45.791, -47.074, -48.38, -49.714, -51.079, -52.482, -53.93, -55.431], "lawQ2": [14.01, 13.21, 12.41, 11.61, 10.81, 10.01, 9.21, 8.41, 7.61, 6.81, 6.01, 5.21, 4.41, 3.61, 2.81, 2.01, 1.21, 0.41, -0.39, -1.19, -1.99, -2.79, -3.59, -4.39, -5.19, -5.99, -6.79, -7.59, -8.39, -9.19, -9.99, -10.79, -11.59, -12.39, -13.19, -13.99, -14.79, -15.59, -16.39, -17.19, -17.99, -18.79, -19.59, -20.39, -21.19, -21.99, -22.79, -23.59], "emb": "rod", "dogK": [0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 22.0, 24.0, 26.0, 28.0, 30.0, 32.0, 34.0, 36.0, 38.0, 40.0, 42.0, 44.0, 46.0, 48.0, 50.0, 52.0, 54.0, 56.0], "dogPhi": [0.0, -1.623, -3.184, -4.695, -6.17, -7.615, -9.039, -10.447, -11.843, -13.23, -14.612, -15.99, -17.366, -18.741, -20.114, -21.484, -22.852, -24.216, -25.572, -26.918, -28.252, -29.568, -30.863, -32.131, -33.369, -34.569, -35.728, -36.838, -37.895], "dKlim": 46.0, "ring": [-28.606, 37.909, 39.01], "ringAx": [-0.46545, 0.61682, 0.63474], "armA": [-37.862, 37.255, 30.914], "armB": [-27.177, 50.918, 14.69], "rodA": [-28.615, 53.611, 15.467], "rodB": [-36.967, 51.046, 4.883], "horn": [-38.809, 53.59, 5.127], "hornRoot": [-31.77, 59.204, 0.37], "L1a": [[-3.03, 49.44, 9.8], [-7.06, 52.24, 5.87], [-4.42, 49.02, 10.98], [-8.51, 51.79, 7.11], [-5.8, 48.59, 12.16], [-9.96, 51.34, 8.35], [-7.18, 48.17, 13.34], [-11.42, 50.91, 9.59]], "L1b": [[-27.76, 56.2, 5.7], [-25.83, 48.3, 10.29], [-27.11, 46.8, 15.57], [-28.2, 44.83, 20.81], [-29.84, 43.51, 26.66], [-24.94, 53.32, 7.87], [-24.43, 48.11, 12.52], [-25.62, 46.47, 17.76], [-26.87, 44.79, 23.16], [-29.89, 45.61, 30.59], [-22.25, 50.36, 9.74], [-23.0, 47.83, 14.71], [-24.33, 46.49, 20.08], [-25.52, 44.74, 25.53], [-22.2, 58.4, 7.64], [-20.29, 48.77, 11.65], [-21.71, 47.81, 16.96], [-23.05, 46.56, 22.44], [-24.62, 45.57, 28.48]], "L2": [[-31.99, 31.68, 47.54], [-29.68, 22.01, 52.72], [-28.17, 12.67, 59.34], [-25.37, 2.12, 63.74], [-21.63, -9.05, 66.11], [-20.05, -23.94, 77.82], [-28.26, 24.09, 52.02], [-27.0, 15.08, 59.23], [-24.35, 4.66, 64.06], [-20.35, -6.37, 65.66], [-18.14, -20.0, 75.36], [-26.87, 26.15, 51.36], [-26.01, 17.61, 59.51], [-23.51, 7.26, 64.9], [-19.66, -3.89, 67.14], [-16.31, -16.31, 72.74], [-25.4, 28.1, 50.53], [-24.82, 20.03, 59.35], [-22.5, 9.85, 65.31], [-18.82, -1.32, 68.2], [-14.56, -12.88, 69.99]]};
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
