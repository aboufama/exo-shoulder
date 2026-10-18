/* crest-knee-3r - the verified pin knee (skin-normal-3r-pin-knee) moved to the DELTOID-CREST seats (round-14 lens 3, screened 2026-10-18). Chain: scapula handler -> J1 (ACTIVE, O20, GH ray, bvec(106.3, 62.9)) -> link 1 (8 x 3 Ti) -> J2 (ACTIVE, O20, GH ray, home bvec(30.4, 50.4)) -> link 2 (flies over the WHOLE member 3: E strap, E boss, knee link, pad) -> J3 (ACTIVE, O20 on the crest wdir(93.0, -1.4), the fold-free end of the crest basin; axis tilted b3 0.33 toward the skin normal so its line misses GH; a dowel-in-slot J3 own-angle stop, frozen window 265.6 + 239.5 deg, not drawn) -> member 3 = hub 3's lower plate + E strap (lE 72.2) -> pin a (PASSIVE, MR63ZZ pair, parallel to J3) -> knee link (lc 27.8) -> pin b (PASSIVE) -> O12 arm pad on the cuff / BOTTOM. 3 active, 2 passive rotations, 0 passive translations, cx 0. Best claimed configuration: near-touch 28.74 / plain 26.34 fast on Bench(60,160); frozen exact Bench(110,360) 32.84 (H1 27.20). The home geometry (axes, lines, hub 3's plane, arcs, mid drift, knee level, pin homes, fitted link centrelines) is exported from docs/concepts/models/crest-knee-3r.py's fit on Bench(60,160). Red = the J2 fold (the J1-J3 axis-angle window) or the knee outside [ang_min, 180 - ang_min] / its span. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  // best configuration (bench model parameters) and the home-frame geometry the model builds from it (exported from the
  // model's Design / fit on Bench(60,160): axis directions u, line points c, hub face levels f along u, hub 3's plane
  // basis sa / st / sn = u3, mid drift m, knee level tr, pin a / pin b home points, fitted link centrelines)
  const P = {"az1": 106.3227, "el1": 62.8675, "az2": 30.3747, "el2": 50.3693, "wd": 93.0446, "wa": -1.3682, "b3": 0.3312, "lE": 72.1786, "lc": 27.7609, "phiE": -3.5194, "phib": -89.085, "stk": 6.0, "ang_min": 25.22};
  const G = {"u":[[0.12817,0.88995,0.43767],[-0.54306,0.69872,0.4657],[-0.00043,0.16271,0.98667]],"c":[[0.0,0.0,0.0],[-0.0,0.0,-0.0],[-0.43,-6.644,1.096]],"sa":[-7e-05,-0.98667,0.16271],"st":[1.0,0.0,0.00043],"sn":[-0.00043,0.16271,0.98667],"A":[40.883,55.011],"branch":-1.0,"m":[-6.469,0.43,0.0],"f":[51.55,60.73,64.92],"tr":61.22,"tp":2.75,"RUN":0.5,"SING":5.0,"hr":[10.0,10.0,10.0],"A0":[-4.866,-77.727,12.816],"A0m":[-4.436,-71.344,11.763],"Bm":[-32.193,-71.781,11.823],"eE":[-0.06146,-0.98481,0.16238],"eK":[-0.99987,-0.01576,0.00216],"L1":[[-3.493,45.998,23.094],[-3.792,43.171,24.575],[-5.949,42.334,23.115],[-7.624,42.35,23.441],[-9.337,42.404,23.792],[-11.097,42.495,24.171],[-12.896,42.559,24.54],[-14.734,42.595,24.899],[-17.409,44.639,26.474],[-20.37,46.784,28.149],[-23.529,48.782,29.785]],"L2":[[-30.952,39.496,39.092],[-26.824,36.265,38.112],[-26.201,33.686,40.038],[-24.41,33.431,42.041],[-24.099,31.288,44.483],[-22.201,30.933,46.464],[-21.803,28.732,48.551],[-20.496,27.762,50.147],[-19.162,26.771,51.748],[-17.766,25.716,53.269],[-17.153,23.27,54.594],[-15.594,21.971,55.644],[-14.005,20.633,56.605],[-12.419,19.315,57.631],[-11.486,17.006,58.856],[-9.425,16.265,60.458],[-9.414,14.614,64.601],[-8.762,13.318,69.361]]};
  const u = G.u, c = G.c, sn = G.sn, sa = G.sa, st = G.st, a1 = G.A[0], a2 = G.A[1], hub = 12.25, rad = 10;
  const wrapR = a => { a = (a + Math.PI) % (2 * Math.PI); return (a < 0 ? a + 2 * Math.PI : a) - Math.PI; };
  const pe = P.phiE * D2R, pb = P.phib * D2R, lE = P.lE, lc = P.lc;
  const A02 = [G.m[0] + lE * Math.cos(pe), G.m[1] + lE * Math.sin(pe)], B2 = [A02[0] + lc * Math.cos(pb), A02[1] + lc * Math.sin(pb)];
  const kbr = Math.sign(wrapR(pe - Math.atan2(B2[1] - G.m[1], B2[0] - G.m[0]))) || 1;     // knee assembly branch (build posture)
  const vref = V.unit(V.cross(u[2], [0.3, 0.5, 0.8]));
  /** the model's closed-form IK (seed S.Design.ik): Q = band HG -> q1..q3 (deg), fold ok, member transforms, drift s */
  function ik(Q) {
    const [u1, u2, u3] = u, w = M.mulv(Q, u3), c12 = V.dot(u1, u2), b1 = V.dot(w, u1), b2 = V.dot(u2, u3), det = 1 - c12 * c12;
    const al = (b1 - c12 * b2) / det, be = (b2 - c12 * b1) / det, cr = V.cross(u1, u2);
    const g2 = (1 - al * al - be * be - 2 * al * be * c12) / V.dot(cr, cr), th = V.angle(w, u1);
    const margin = Math.min(th - Math.abs(a1 - a2), Math.min(a1 + a2, 360 - a1 - a2) - th);
    let pick = null;
    for (const sg of [1, -1]) {
      const z = V.madd(V.add(V.scale(u1, al), V.scale(u2, be)), cr, sg * Math.sqrt(Math.max(g2, 0)));
      const q1 = K.axisAngle(u1, z, w), q2 = K.axisAngle(u2, u3, z), p2 = M.mulv(M.rot(u1, q1), u2);
      const br = Math.sign(V.dot(p2, V.cross(u1, w)));
      if (pick === null || br === G.branch) pick = [q1, q2];
    }
    return { q1: pick[0], q2: pick[1], ok: margin >= G.SING && g2 > 0, margin };
  }
  /** member transforms from joint angles (deg): lines through c1, c2, c3 (J1 / J2 lines pass GH) */
  function chain(q1, q2, q3) {
    const R1 = M.rot(u[0], q1), R2 = M.rot(u[1], q2), R12 = M.mul(R1, R2), R3 = M.rot(u[2], q3), R123 = M.mul(R12, R3);
    const t1 = V.sub(c[0], M.mulv(R1, c[0]));
    const t2 = V.add(M.mulv(R1, V.sub(V.sub(c[1], M.mulv(R2, c[1])), c[0])), c[0]);
    const t3 = V.add(M.mulv(R12, V.sub(c[2], M.mulv(R3, c[2]))), t2);
    return { R1, t1, R12, t2, R123, t3 };
  }
  /** planar RRR knee in hub 3's plane (model Design.knee): drift s -> E angle th, pin a, knee link angle psi, knee angle */
  function knee(s) {
    const vx = B2[0] - s[0], vy = B2[1] - s[1], d = Math.hypot(vx, vy), gam = Math.atan2(vy, vx);
    const ca = (lE * lE + d * d - lc * lc) / (2 * lE * Math.max(d, 1e-9)), al = Math.acos(Math.max(-1, Math.min(1, ca)));
    const th = gam + kbr * al, pa = [s[0] + lE * Math.cos(th), s[1] + lE * Math.sin(th)];
    const wx = B2[0] - pa[0], wy = B2[1] - pa[1], psi = Math.atan2(wy, wx);
    const cosk = ((s[0] - pa[0]) * wx + (s[1] - pa[1]) * wy) / (lE * lc), ang = Math.acos(Math.max(-1, Math.min(1, cosk))) / D2R;
    return { th, pa, psi, ang, d, phi: wrapR(th - pe), span: d >= Math.abs(lE - lc) + 1 && d <= lE + lc - 1 };
  }
  const Qof = ctx => M.mul(M.T(ctx.S), ctx.H);                      // band HG: the arm's rotation in the scapula frame
  function solve(ctx) {
    const Q = Qof(ctx), k = ik(Q), R12 = M.mul(M.rot(u[0], k.q1), M.rot(u[1], k.q2));
    const q3 = K.axisAngle(u[2], vref, M.mulv(M.T(R12), M.mulv(Q, vref))), X = chain(k.q1, k.q2, q3);
    const sv = M.mulv(M.T(Q), X.t3), s = [V.dot(sv, sa), V.dot(sv, st), V.dot(sv, sn)], kn = knee(s);
    const R = x => K.wrap180(x / D2R);
    // q: J1, J2, J3 (link 2 -> member 3 = q3 + phi), pin a (member 3 -> knee link), pin b (knee link -> arm), from home
    return [k.q1, k.q2, K.wrap180(q3 + kn.phi / D2R), R(wrapR(kn.psi - pb - kn.phi)), R(wrapR(kn.psi - pb))];
  }
  /** forward kinematics of the whole loop from q: every member, pin a, pin b and the arm it implies */
  function fk(q) {
    const X = chain(q[0], q[1], q[2]), Rm3 = X.R123;                // member 3 = hub 3's lower plate + E strap + E boss
    const pa = V.add(M.mulv(Rm3, G.A0), X.t3);
    const R6 = M.mul(Rm3, M.rot(sn, q[3])), t6 = V.sub(pa, M.mulv(R6, G.A0m));
    const pbW = V.add(M.mulv(R6, G.Bm), t6), R5 = M.mul(R6, M.rot(sn, -q[4])), t5 = V.sub(pbW, M.mulv(R5, G.Bm));
    return Object.assign(X, { Rm3, R6, t6, R5, t5, pa, pb: pbW });
  }
  const check = (q, ctx) => {
    const Q = Qof(ctx), k = ik(Q);
    if (!k.ok) return k.margin < 0 ? 'J2 fold: the J1-J3 axis angle is outside the 3R window' : `J2 within ${k.margin.toFixed(0)} deg of its fold (>= ${G.SING})`;
    const F = fk(q), sv = M.mulv(M.T(Q), F.t3), kn = knee([V.dot(sv, sa), V.dot(sv, st)]);
    if (!kn.span) return 'knee span: the drift is beyond lE + lc';
    if (kn.ang < P.ang_min || kn.ang > 180 - P.ang_min) return `knee angle ${kn.ang.toFixed(0)} deg outside [${P.ang_min}, ${180 - P.ang_min}]`;
    if (Math.abs(V.dot(sv, sn)) > 0.5) return 'radial drift > 0.5 mm';
    return null;
  };
  /** a frame the loop cannot close (fold, knee out of span) is shown at the least-squares nearest configuration
   *  warm-started from the previous frame (continuous, drawn red), not at the clipped closed form */
  const closes = (q, ctx) => { const r = C.residual(q, ctx); return Math.max(...r.map(Math.abs)) <= 0.5; };
  const solveC = (ctx, qPrev) => { const q = solve(ctx); return (!qPrev || closes(q, ctx)) ? q : K.dls(C, ctx, qPrev, { iters: 40 }).q; };
  const C = {
    id: 'crest-knee-3r', name: 'Crest pin-knee 3R: crest seats, link 2 over member 3, flat two-pin MR63ZZ knee (0 passive translations)',
    dof: { active: 3, passive: 2 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'J2', 'J3', 'knee pin a', 'knee pin b'], qUnits: ['deg', 'deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve: solveC,
    residual: (q, ctx) => { const F = fk(q); return M.rotErrDeg(F.R5, Qof(ctx)).concat(F.t5); },   // arm pose implied by the loop vs the arm
    check,
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), F = fk(q);
      const on = (R, t, p) => W(V.add(M.mulv(R, p), t)), I = M.I3(), Z = [0, 0, 0];
      const hp = (R, t, k) => on(R, t, V.madd(c[k], u[k], G.f[k]));
      const h1 = { kind: 'hub', role: 'active', name: 'J1 (axis on a GH ray)', c: hp(I, Z, 0), axis: Wd(u[0]), r: rad, h: hub };
      const h2 = { kind: 'hub', role: 'active', name: 'J2 (axis on a GH ray)', c: hp(F.R1, F.t1, 1), axis: Wd(M.mulv(F.R1, u[1])), r: rad, h: hub };
      const ax3 = Wd(M.mulv(F.R12, u[2]));
      const h3 = { kind: 'hub', role: 'active', name: 'J3 (skin-normal tilt, line misses GH)', c: hp(F.R12, F.t2, 2), axis: ax3, r: rad, h: hub,
                   p0: on(F.R12, F.t2, c[2]) };
      const n3 = Wd(M.mulv(F.Rm3, sn));                              // pin axis direction (all pins parallel to J3)
      const lvl = (p, h) => V.madd(W(p), n3, h);
      const paW = F.pa, pbW = F.pb, kz = G.tr + G.tp + G.RUN + G.tp / 2;
      const rim = on(F.Rm3, F.t3, V.add(V.madd(c[2], sn, G.f[2] + 1.5), V.scale(G.eE, rad)));
      const arm = p => M.mulv(ctx.H, p);                             // arm-fixed home point -> world (= S Q p)
      const padC = arm(V.madd(G.Bm, sn, G.tr + G.tp / 2)), padN = M.mulv(ctx.H, sn);
      const lat = arm([G.Bm[0], -150, 50]);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base on the scapula handler', c: V.madd(h1.c, h1.axis, -3), z: h1.axis, x: ctx.attach.scapDir([1, 0, 0]), size: [40, 30], t: 3 },
        h1,
        { kind: 'arc', role: 'link', name: 'link 1 (8 x 3 strap, fitted)', pts: G.L1.map(p => on(F.R1, F.t1, p)), r: 2.5 },
        h2,
        { kind: 'arc', role: 'link', name: 'link 2 (8 x 3 strap, fitted)', pts: G.L2.map(p => on(F.R12, F.t2, p)), r: 2.5 },
        h3,
        { kind: 'link', role: 'link', name: 'E strap (member 3: hub 3 lower plate -> pin a)', a: rim, b: lvl(paW, G.tr + 1.5), r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'knee pin a (MR63ZZ pair, parallel to J3)', c: lvl(paW, G.tr), axis: n3, r: 6, h: P.stk, p0: lvl(paW, G.tr) },
        { kind: 'link', role: 'link', name: 'knee link (flat Ti plate)', a: lvl(paW, kz), b: lvl(pbW, kz), r: 3 },
        { kind: 'hub', role: 'passive', name: 'knee pin b (MR63ZZ pair, parallel to J3)', c: lvl(pbW, G.tr), axis: n3, r: 6, h: P.stk, p0: lvl(pbW, G.tr) },
        { kind: 'plate', role: 'fixed-arm', name: 'arm pad (on the cuff / BOTTOM)', c: padC, z: padN, x: arm(sa), size: [14, 14], t: G.tp },
        { kind: 'link', role: 'fixed-arm', name: 'BOTTOM bar to the cuff (schematic)', a: V.madd(padC, padN, -2), b: lat, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: V.scale(ctx.armAxis, 155), axis: ctx.armAxis, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  };
  K.register(C);
})();
