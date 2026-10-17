/* dipped-law-groove-knuckle-3r at its best measured configuration: the lead's slaved knuckle (roller-longdyad-knuckle-3r: pin
 * knee, link 1 split by a passive O20 knuckle K slaved to q2 by the hub-2 lobe -> bell crank -> roller -> flank drive) with a
 * DIPPED K law: in the mid-folded band (th_c +- w) the lobe lets the clock spring close K below the old stop A, so the
 * effective first link a1e = a1 - dipD (1 - x^2)^2 shortens and hub 2 rides up off the bunched deltoid; stop A sits at
 * the dip floor, the crank swings backward through the dip. J1, J2, J3 encoders give the pose (3 active, K never read,
 * 0 passive translations).
 * Best measured dip (dipD 1.0, th_c 50, w 8, C1 bump, crank built at the dip floor): fast Bench(60,160) plain 15.26 vs the D = 0 control 14.28 (the dip spends flank stroke: dK_lim 46.2 -> 43.5). Frozen exact Bench(110,360) at dipD 4: 21.10 vs the control 19.33 and the lead 18.67.
 * Geometry exported from docs/concepts/models/dipped-law-groove-knuckle-3r.py (mode viz). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 95.3929, "el1": 67.8974, "az2": 45.8211, "el2": 41.0855, "wd": 66.8662, "wa": -10.6559, "b3": 0.329, "lE": 82.0, "lc": 27.0, "phiE": 3.8, "phib": -96.6, "stk": 4.8534, "ang_min": 20.0, "bk1": 26.0, "bk2": 38.0336, "sK": -1, "a1max": 58.7678, "smhi": 16.8433, "smlo": 5.0, "capK": 6.0, "law_mode": "seg", "kA": 2.1534, "t1": 6.0, "kB": 2.1534, "smt": 12.0, "kK": 2.1534, "i_rock": 2.4696, "r_horn": 4.0484, "r_lobe": 8.2409, "arm_lo": 1.0};
  const G = {"u": [[0.03536, 0.92651, 0.3746], [-0.46545, 0.61682, 0.63474], [-0.13912, -0.22062, 0.96539]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-0.73949, -13.44608, -3.17939]], "uK": [-0.31441, 0.9448, 0.09223], "sa": [0.03147, -0.97536, -0.21836], "st": [0.98978, 0.0, 0.14263], "sn": [-0.13912, -0.22062, 0.96539], "A": [37.552, 57.218], "branch": -1.0, "m": [-11.73932, 1.16259, 0.0], "f": [50.45, 61.83, 78.16], "fK": 55.12, "capK": 6.0, "tr": 88.63, "tp": 2.177, "RUN": 0.5, "A0": [7.21404, -93.24975, -20.27079], "A0m": [7.99534, -81.79969, -17.54152], "Bm": [-18.64916, -78.77285, -20.68936], "eE": [0.09699, -0.97322, -0.20843], "psiA": -71.6859, "thLo": 24.6667, "thHi": 77.9268, "q2s": [102.0679, 7.2787], "lawTh": [77.927, 78.936, 79.961, 81.001, 82.054, 83.12, 84.197, 85.283, 86.377, 87.477, 88.583, 89.693, 90.806, 91.919, 93.032, 94.144, 95.252, 96.356, 97.453, 98.544, 99.625, 100.695, 101.753, 102.798, 103.827, 104.839, 105.833, 106.806, 107.757, 108.684, 109.585, 110.459, 111.304, 112.117, 112.898, 113.643, 114.352], "lawDK": [-0.0, -1.723, -3.445, -5.168, -6.891, -8.614, -10.336, -12.059, -13.782, -15.504, -17.227, -18.95, -20.673, -22.395, -24.118, -25.841, -27.564, -29.286, -31.009, -32.732, -34.454, -36.177, -37.9, -39.623, -41.345, -43.068, -44.791, -46.513, -48.236, -49.959, -51.682, -53.404, -55.127, -56.85, -58.572, -60.295, -62.018], "lawQ2": [7.279, 6.479, 5.679, 4.879, 4.079, 3.279, 2.479, 1.679, 0.879, 0.079, -0.721, -1.521, -2.321, -3.121, -3.921, -4.721, -5.521, -6.321, -7.121, -7.921, -8.721, -9.521, -10.321, -11.121, -11.921, -12.721, -13.521, -14.321, -15.121, -15.921, -16.721, -17.521, -18.321, -19.121, -19.921, -20.721, -21.521], "emb": "rod", "rocker": [-26.815, 49.269, 27.816], "rockerAx": [-0.42827, 0.7869, 0.44427], "rodA": [-14.982, 59.182, -8.973], "rodB": [-14.982, 59.182, -8.973], "armA": [-26.815, 49.269, 27.816], "armB": [-33.219, 53.11, 9.462], "L1a": [[-3.91, 49.97, 11.45], [-7.44, 54.61, 12.76], [-9.31, 49.42, 14.73]], "L1b": [[-25.01, 51.93, 14.5], [-25.04, 46.25, 18.65], [-26.77, 43.91, 23.84], [-23.22, 52.45, 15.31], [-23.08, 46.18, 19.18], [-24.75, 43.86, 24.31], [-21.43, 52.97, 16.12], [-21.07, 45.89, 19.61], [-23.07, 44.34, 25.08], [-19.64, 53.48, 16.93], [-19.28, 45.99, 20.18], [-21.39, 44.84, 25.84]], "L2": [[-32.22, 31.82, 47.82], [-29.96, 22.1, 53.12], [-29.08, 12.92, 61.13], [-26.74, 2.05, 67.0], [-22.75, -9.72, 69.31], [-19.66, -23.7, 75.98], [-28.4, 24.11, 52.22], [-27.37, 15.15, 59.97], [-25.07, 4.62, 65.84], [-21.24, -6.85, 68.39], [-17.75, -19.81, 73.54], [-26.94, 26.15, 51.49], [-26.19, 17.61, 59.88], [-23.74, 7.17, 65.49], [-19.78, -4.1, 67.47], [-15.93, -16.17, 70.95], [-25.4, 28.06, 50.57], [-24.97, 20.06, 59.74], [-22.68, 9.79, 65.86], [-18.93, -1.51, 68.61], [-14.31, -12.89, 68.78]], "armPts": [[-27.457, 50.449, 28.483], [-26.593, 48.012, 24.903], [-27.568, 48.933, 23.174], [-28.296, 49.408, 21.208], [-28.845, 49.574, 19.118], [-29.344, 49.662, 17.023], [-30.156, 50.282, 15.115], [-32.525, 53.455, 13.851], [-33.539, 54.354, 11.866], [-34.062, 54.458, 9.702], [-34.425, 54.424, 7.683], [-34.593, 54.567, 5.647], [-34.505, 54.795, 3.614], [-34.163, 55.103, 1.619], [-33.574, 55.487, -0.304], [-32.747, 55.939, -2.121], [-31.697, 56.453, -3.802], [-30.441, 57.019, -5.318], [-29.002, 57.627, -6.641], [-27.404, 58.267, -7.75], [-25.675, 58.928, -8.625], [-23.845, 59.598, -9.252], [-21.945, 60.266, -9.618], [-20.007, 60.921, -9.719], [-18.066, 61.55, -9.553], [-16.155, 62.144, -9.121], [-15.88, 62.227, -9.036]], "lugPts": [[-18.128, 56.661, -5.285], [-20.91, 57.016, -10.924], [-19.866, 56.968, -12.94], [-18.609, 57.018, -14.496], [-17.207, 57.116, -15.784], [-15.692, 57.244, -16.862]], "roller": [-14.982, 59.182, -8.973], "rollerAx": [-0.2428, 0.95912, -0.14541], "sig": 1.0, "g": 2.4696, "cprog": 0.0, "dKlim": 43.5};
  const u = G.u, c = G.c, uK = G.uK, sn = G.sn, sa = G.sa, st = G.st, a1 = G.A[0], a2 = G.A[1], hub = 12.25, rad = 10;
  const wrapR = a => { a = (a + Math.PI) % (2 * Math.PI); return (a < 0 ? a + 2 * Math.PI : a) - Math.PI; };
  const pe = P.phiE * D2R, pb = P.phib * D2R, lE = P.lE, lc = P.lc;
  const A02 = [G.m[0] + lE * Math.cos(pe), G.m[1] + lE * Math.sin(pe)], B2 = [A02[0] + lc * Math.cos(pb), A02[1] + lc * Math.sin(pb)];
  const kbr = Math.sign(wrapR(pe - Math.atan2(B2[1] - G.m[1], B2[0] - G.m[0]))) || 1;
  const vref = V.unit(V.cross(u[2], [0.3, 0.5, 0.8]));
  const cb = x => Math.cos(x * D2R), sb = x => Math.sin(x * D2R);
  const spK = Math.sign(G.psiA) || 1, cbk = (a, b) => (Math.cos(a * D2R) - cb(P.bk1) * cb(P.bk2)) / (sb(P.bk1) * sb(P.bk2));
  const kopen = a1e => Math.acos(Math.max(-1, Math.min(1, cbk(a1e)))) / D2R - Math.abs(G.psiA);   // deg, - = closing
  const dipOf = th => { if (!(P.dipD > 0)) return 0; const x = (th - P.dip_thc) / P.dip_w; let b = Math.max(0, 1 - x * x); if (P.dip_shape) b = b * b; return P.dipD * b; };
  const dipK = th => spK * kopen(a1 - dipOf(th));
  const kref = (P.dipD > 0 ? kopen(a1 - P.dipD) : 0) * (P.dip_ref || 0);       // the crank's build phase (deg of K)
  /** physical J2 stop: th (deg) inside [thLo, thHi] -> K on stop A (state 0); else J2 locked on its q2 stop, K opens */
  const dot = V.dot;
  function ik(Q) {
    const [u1, u2, u3] = u, w = M.mulv(Q, u3), th = V.angle(w, u1);
    if (th >= G.thLo && th <= G.thHi) {
      const dK = dipK(th), RK = M.rot(uK, dK), v2 = M.mulv(RK, u2);          // DIP: K closed below stop A in the band
      const c12 = dot(u1, v2), b1 = dot(w, u1), b2 = cb(a2), det = 1 - c12 * c12;
      const al = (b1 - c12 * b2) / det, be = (b2 - c12 * b1) / det, cr = V.cross(u1, v2);
      const g2 = (1 - al * al - be * be - 2 * al * be * c12) / dot(cr, cr);
      let pick = null;
      for (const sg of [1, -1]) {
        const z = V.madd(V.add(V.scale(u1, al), V.scale(v2, be)), cr, sg * Math.sqrt(Math.max(g2, 0)));
        const q1 = K.axisAngle(u1, z, w), q2 = K.axisAngle(u2, u3, M.mulv(M.T(RK), z)), p2 = M.mulv(M.rot(u1, q1), v2);
        const br = Math.sign(dot(p2, V.cross(u1, w)));
        if (pick === null || br === G.branch) pick = [q1, q2];
      }
      return { q1: pick[0], dK, q2: pick[1], ok: g2 > 0, L: { state: 0 } };
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
    return null;
  };
  const closes = (q, ctx) => { const r = C.residual(q, ctx); return Math.max(...r.map(Math.abs)) <= 0.5; };
  const solveC = (ctx, qPrev) => { const q = solve(ctx); return (!qPrev || closes(q, ctx)) ? q : K.dls(C, ctx, qPrev, { iters: 40 }).q; };
  const C = {
    id: 'dipped-law-groove-knuckle-3r', name: 'Dipped K law: the slaved knuckle closes below stop A in the mid-folded band to lift hub 2 off the deltoid (lead + centred knee; 3 active, K not read)',
    dof: { active: 3, passive: 5 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'K (passive, slaved to q2 by the dipped lobe - bell crank - roller - flank; closes below stop A in the dip)', 'J2', 'J3', 'knee pin a', 'knee pin b'], qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve: solveC,
    residual: (q, ctx) => { const F = fk(q); return M.rotErrDeg(F.R5, Qof(ctx)).concat(F.t5); },
    check,
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), F = fk(q);
      const Rc = M.mul(F.R1b, M.rot(G.rockerAx, G.sig * ((spK * q[1] - kref) / G.g)));
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
        { kind: 'hub', role: 'passive', name: 'bell crank boss (MR63ZZ pair, pin in link 1b beside hub 2; short arm rides the hub-2 rim lobe)', c: on(Rc, G.rocker), axis: Wd(M.mulv(Rc, G.rockerAx)), r: 5, h: 6 },
        { kind: 'arc', role: 'link', name: 'bell crank bent long arm (3 mm Ti: straight run, then an arc concentric with hub K)', pts: G.armPts.map(p => on(Rc, p)), r: 1.5 },
        { kind: 'hub', role: 'passive', name: 'MR63ZZ roller (O6 x 2.5, radial axis) on the arm tip', c: on(Rc, G.roller), axis: Wd(M.mulv(Rc, G.rollerAx)), r: 3, h: 2.5 },
        { kind: 'arc', role: 'link', name: 'horn lug of link 1a with the conjugate flank (wire-EDM)', pts: G.lugPts.map(p => on(F.R1, p)), r: 1.5 },
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
