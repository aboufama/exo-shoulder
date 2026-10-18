/* posteromedial-knuckle-3r at its best fit configuration (NOT honest: the K drive cannot open): the verified lead conecut-knee-knuckle-3r
 * (slipper-nose K drive, conecut two-pin knee, J3 own-angle dowel stop, O20 hubs; loaded unchanged) with J1 RE-SEATED on the back of the
 * shoulder at bvec(-26.25, 40) (75 mm from GH vs the lead's 42), J3 on the high lateral arm (wd 113.1 / wa -18.2) and J2 re-solved
 * (a1 40.53 / a2 53.94, branch +1). Stage-1 CMA best of 73 (fit Bench(60,160) fast): near-1 225.38 / plain 223.16, reach 0.081,
 * fold 130 / skin 30 / parts 24 of 220 - the drive's crank pressure angle is past its 38 deg gate, so K stays on stop A.
 * DEAD for the cell (docs/research/posteromedial_seat.md). Geometry exported from docs/concepts/models/posteromedial-knuckle-3r.py (mode viz). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": -26.25, "el1": 40.0, "az2": 10.659278421427375, "el2": 77.50259207136568, "wd": 113.0939, "wa": -18.156200000000013, "b3": 0.329, "lE": 97.587, "lc": 23.8867, "phiE": 0.7526, "phib": -88.5026, "stk": 6.0, "ang_min": 25.2189, "bk1": 26.0, "bk2": 38.0336, "sK": -1, "a1max": 58.7678, "smhi": 16.8433, "smlo": 5.0, "capK": 6.0, "law_mode": "seg", "kA": 2.1534, "t1": 6.0, "kB": 2.1534, "smt": 12.0, "kK": 2.1534, "i_rock": 2.451, "r_horn": 4.0, "r_lobe": 8.2661, "arm_lo": 1.0};
  const G = {"u": [[-0.68704, 0.64279, -0.33881], [-0.24436, 0.96598, 0.08472], [-0.25274, 0.47127, 0.845]], "c": [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [-1.6538, -4.34812, 1.93038]], "uK": [-0.78835, 0.60736, 0.0981], "sa": [-0.13505, -0.88199, 0.45151], "st": [0.95806, 0.0, 0.28656], "sn": [-0.25274, 0.47127, 0.845], "A": [40.527, 53.943], "branch": 1.0, "m": [-4.22207, -0.5626, 0.0], "f": [97.34, 77.95, 62.59], "fK": 67.96, "capK": 6.0, "tr": 34.8, "tp": 2.75, "RUN": 0.5, "A0": [-13.60348, -90.41122, 46.35528], "A0m": [-13.5723, -86.68741, 44.28776], "Bm": [-36.53374, -87.23794, 37.72699], "eE": [-0.12245, -0.88191, 0.45523], "psiA": -78.8631, "thLo": 18.4167, "thHi": 77.6268, "q2s": [-101.9448, -2.9605], "lawTh": [77.627, 78.274, 78.915, 79.547, 80.171, 80.787, 81.394, 81.993, 82.583, 83.163, 83.734, 84.295, 84.846, 85.387, 85.918, 86.439, 86.948, 87.447, 87.935, 88.411, 88.876, 89.33, 89.771, 90.201, 90.619, 91.025, 91.418, 91.799, 92.168, 92.524, 92.867, 93.197, 93.515], "lawDK": [-0.0, -1.723, -3.445, -5.168, -6.891, -8.614, -10.336, -12.059, -13.782, -15.504, -17.227, -18.95, -20.673, -22.395, -24.118, -25.841, -27.564, -29.286, -31.009, -32.732, -34.454, -36.177, -37.9, -39.623, -41.345, -43.068, -44.791, -46.513, -48.236, -49.959, -51.682, -53.404, -55.127], "lawQ2": [-2.96, -2.16, -1.36, -0.56, 0.24, 1.04, 1.84, 2.64, 3.44, 4.24, 5.04, 5.84, 6.64, 7.44, 8.24, 9.04, 9.84, 10.64, 11.44, 12.24, 13.04, 13.84, 14.64, 15.44, 16.24, 17.04, 17.84, 18.64, 19.44, 20.24, 21.04, 21.84, 22.64], "emb": "rod", "rocker": [-34.264, 70.272, 7.328], "rockerAx": [-0.43636, 0.89492, 0.09332], "rodA": [-67.084, 30.941, 7.605], "rodB": [-67.084, 30.941, 7.605], "armA": [-34.264, 70.272, 7.328], "armB": [-52.654, 50.162, 21.785], "L1a": [[-74.36, 60.77, -21.23], [-67.91, 53.77, -12.52], [-60.71, 46.57, -5.33], [-70.9, 60.21, -17.7], [-64.34, 52.93, -9.54], [-57.06, 45.48, -2.92], [-67.45, 59.49, -14.36], [-60.8, 51.94, -6.76], [-69.99, 66.21, -19.78], [-64.02, 58.62, -11.23], [-57.3, 50.82, -4.19]], "L1b": [[-49.19, 51.61, 10.05], [-38.19, 47.46, 8.55], [-31.21, 46.22, 7.76], [-31.43, 56.15, 8.82], [-30.94, 68.06, 10.05], [-45.54, 50.52, 7.69], [-34.87, 45.85, 6.46], [-30.89, 48.55, 6.37], [-31.59, 60.2, 7.38], [-30.53, 72.25, 8.29], [-41.99, 49.25, 5.51], [-33.22, 46.26, 4.79], [-31.43, 52.5, 5.04], [-31.57, 64.32, 5.73], [-49.6, 52.02, 4.16], [-38.55, 47.81, 3.52], [-32.68, 48.22, 3.27], [-31.8, 56.52, 3.51], [-31.37, 68.49, 3.88]], "L2": [[-25.4, 75.87, 18.87], [-19.98, 52.38, 23.74], [-19.32, 44.04, 30.72], [-19.96, 38.74, 39.35], [-22.0, 34.91, 51.74], [-19.24, 56.63, 23.81], [-17.6, 45.04, 29.49], [-18.12, 39.67, 37.88], [-19.24, 34.85, 48.2], [-18.28, 60.97, 23.71], [-16.02, 46.33, 28.46], [-16.62, 41.27, 37.07], [-16.64, 34.55, 44.7], [-17.1, 65.39, 23.46], [-14.43, 47.65, 27.45], [-15.09, 42.82, 36.21], [-14.93, 35.74, 43.35]], "armPts": [[-34.919, 71.615, 7.468], [-33.242, 64.564, 7.766], [-32.955, 60.667, 8.307], [-34.283, 59.861, 9.233], [-33.787, 55.991, 9.646], [-33.15, 52.168, 9.968], [-33.383, 49.913, 10.516], [-34.721, 49.342, 11.406], [-36.537, 49.366, 12.467], [-38.021, 48.855, 13.431], [-41.281, 50.458, 15.054], [-44.631, 51.898, 16.759], [-48.061, 53.172, 18.541], [-51.52, 54.231, 20.379], [-52.668, 52.744, 21.323], [-53.772, 51.227, 22.248], [-54.766, 49.628, 23.043], [-55.91, 48.048, 23.638], [-57.107, 46.436, 23.994], [-58.341, 44.816, 24.105], [-59.594, 43.213, 23.969], [-60.846, 41.649, 23.589], [-62.079, 40.148, 22.969], [-63.276, 38.732, 22.119], [-64.418, 37.422, 21.052], [-65.489, 36.237, 19.783], [-66.472, 35.196, 18.331], [-67.353, 34.312, 16.718], [-68.119, 33.6, 14.968], [-68.759, 33.07, 13.105], [-69.264, 32.73, 11.159], [-69.625, 32.584, 9.157], [-69.773, 32.592, 7.924]], "lugPts": [[-62.773, 34.841, 7.504], [-65.186, 34.569, 8.44]], "roller": [-67.084, 30.941, 7.605], "rollerAx": [-0.90329, 0.41663, 0.1024], "sig": 1.0, "g": 2.451, "cprog": 0.0, "dKlim": 0.0};
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
    if (Math.abs(k.dK) > G.dKlim + 1e-6) return `past the flank's working range (|dK| ${Math.abs(k.dK).toFixed(1)} > ${G.dKlim} deg): stop B`;
    const F = fk(q), sv = M.mulv(M.T(Q), F.t3), kn = knee([V.dot(sv, sa), V.dot(sv, st)]);
    if (!kn.span) return 'knee span: the drift is beyond lE + lc';
    if (kn.ang < P.ang_min || kn.ang > 180 - P.ang_min) return `knee angle ${kn.ang.toFixed(0)} deg outside [${P.ang_min}, ${180 - P.ang_min}]`;
    if (q[3] < P.J3MIN) return `J3 on its hard stop (q3' ${q[3].toFixed(1)} < ${P.J3MIN} deg: dowel in hub 3's lower plate at the end of its arc groove)`;
    if (P.J3MAX < 180 && q[3] > P.J3MAX) return `J3 on its upper hard stop (q3' ${q[3].toFixed(1)} > ${P.J3MAX} deg)`;
    return null;
  };
  const closes = (q, ctx) => { const r = C.residual(q, ctx); return Math.max(...r.map(Math.abs)) <= 0.5; };
  const solveC = (ctx, qPrev) => { const q = solve(ctx); return (!qPrev || closes(q, ctx)) ? q : K.dls(C, ctx, qPrev, { iters: 40 }).q; };
  const C = {
    id: 'posteromedial-knuckle-3r', name: 'The lead knuckle with J1 re-seated on the back of the shoulder (az -26.25 / el 40; J3 seat and J2 re-solved; slipper-nose K drive, conecut knee, J3 dowel stop; 3 active, K not read)',
    dof: { active: 3, passive: 4 },   // K, bell crank, knee pins a and b (the roller is gone)
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'K (passive, slaved to q2 by the lobe - bell crank - sliding nose - flank sidecar)', 'J2', 'J3', 'knee pin a', 'knee pin b'], qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve: solveC,
    residual: (q, ctx) => { const F = fk(q); return M.rotErrDeg(F.R5, Qof(ctx)).concat(F.t5); },
    check,
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), F = fk(q);
      const Rc = M.mul(F.R1b, M.rot(G.rockerAx, G.sig * (Math.abs(q[1]) / G.g) * (1 + (G.cprog || 0) * Math.abs(q[1]) * D2R)));
      const on = (R, p) => W(M.mulv(R, p)), I = M.I3();
      const h1 = { kind: 'hub', role: 'active', name: 'J1 (axis on a GH ray)', c: W(V.scale(u[0], G.f[0])), axis: Wd(u[0]), r: rad, h: hub };
      const hK = { kind: 'hub', role: 'passive', name: 'K (O20, passive, slaved; clock-spring cap, stop A; the horn is a lateral lug of link 1a)', c: on(F.R1, V.scale(uK, G.fK)), axis: Wd(M.mulv(F.R1, uK)), r: rad, h: hub + (G.capK || 0) };
      const h2 = { kind: 'hub', role: 'active', name: 'J2 (axis on a GH ray; folded dowel stop, drive stop B)', c: on(F.R1b, V.scale(u[1], G.f[1])), axis: Wd(M.mulv(F.R1b, u[1])), r: rad, h: hub };
      const h3 = { kind: 'hub', role: 'active', name: 'J3 (skin-normal tilt, line misses GH; hard stop: 2 mm dowel in hub 3 lower plate at r 7.5 in an arc groove under link 2, q3p >= ' + P.J3MIN + (P.J3MAX < 180 ? ', <= ' + P.J3MAX : '') + ')', c: on(F.R12, V.madd(c[2], u[2], G.f[2])), axis: Wd(M.mulv(F.R12, u[2])), r: rad, h: hub,
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
        { kind: 'hub', role: 'passive', name: 'bell crank boss (MR63ZZ pair, pin in link 1b beside hub 2; short arm rides the hub-2 rim lobe)', c: on(Rc, G.rocker), axis: Wd(M.mulv(Rc, G.rockerAx)), r: 5, h: 6 },
        { kind: 'arc', role: 'link', name: 'bell crank bent long arm (3 mm Ti: straight run, then an arc concentric with hub K)', pts: G.armPts.map(p => on(Rc, p)), r: 1.5 },
        { kind: 'hub', role: 'passive', name: 'O2 hardened 440C nose (ISO 8734 dowel pressed in the arm tip; slides on the flank, DLC + grease)', c: on(Rc, G.roller), axis: Wd(M.mulv(Rc, G.rollerAx)), r: 1.18, h: 2.5 },
        { kind: 'arc', role: 'link', name: 'horn lug of link 1a with the conjugate flank (wire-EDM)', pts: G.lugPts.map(p => on(F.R1, p)), r: 1.5 },
        h3,
        { kind: 'link', role: 'link', name: 'E strap (member 3: hub 3 lower plate -> pin a)', a: rim, b: lvl(F.pa, G.tr + 1.5), r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'knee pin a (MR63ZZ pair, parallel to J3)', c: lvl(F.pa, G.tr), axis: n3, r: 6, h: P.stk, p0: lvl(F.pa, G.tr) },
        { kind: 'link', role: 'link', name: 'knee link (flat Ti plate)', a: lvl(F.pa, kz), b: lvl(F.pb, kz), r: 3 },
        { kind: 'hub', role: 'passive', name: 'knee pin b (MR63ZZ pair, parallel to J3)', c: lvl(F.pb, G.tr), axis: n3, r: 6, h: P.stk, p0: lvl(F.pb, G.tr) },
        { kind: 'plate', role: 'fixed-arm', name: 'arm pad (on the cuff / BOTTOM)', c: padC, z: padN, x: arm(sa), size: [14, 14], t: G.tp },
        { kind: 'link', role: 'fixed-arm', name: 'BOTTOM bar to the cuff (schematic)', a: V.madd(padC, padN, -2), b: lat, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: V.scale(ctx.armAxis, 155), axis: ctx.armAxis, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  };
  K.register(C);
})();
