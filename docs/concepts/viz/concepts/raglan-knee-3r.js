/* raglan-knee-3r - the pin-knee 3R (J1 / J2 O20 hubs on GH rays, J3 an offset skin-normal hub on the deltoid, closed by
 * a flat two-pin knee: E strap -> pin a -> knee link -> pin b -> arm pad; pins PASSIVE, parallel to J3; 0 passive
 * translations) with its links cut like a raglan seam: link 1 runs hub 1 -> W1 -> hub 2 as two great-circle legs joined
 * by ONE tangent arc (t 0.80, d -30.6 deg off the great circle: a 114 deg planform turn, arc r 8.9 mm), link 2 nearly
 * straight (t 0.55, d -1.3). Verified 31.52 on Bench(110,360) exact frozen (CMA A2, k1284). Exactly the model
 * docs/concepts/models/raglan-knee-3r.py at rows best_params: the axis directions, line points, hub face levels (51.2 /
 * 61.2 / 73.7 mm along the axes), mid drift, knee level (79.2 mm) and the routed, skin-fitted link centrelines are
 * exported from the model's fit on Bench(60,160) (with the routed links: in the current files the pin knee's _Geo,
 * added after the raglan verification, would draw great-circle links instead); the IK is the model's closed form
 * (spherical IK of the axis directions + the two-circle knee on its build branch); the residual is the full-loop
 * forward kinematics. Red = the J2 fold (the J1-J3 axis-angle window) or the knee outside [30, 150] deg / its span. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  // best configuration (bench model parameters) and the home-frame geometry the model builds from it (exported from the
  // model's Design / fit on Bench(60,160): axis directions u, line points c, hub face levels f along u, hub 3's plane
  // basis sa / st / sn = u3, mid drift m, knee level tr, pin a / pin b home points, fitted link centrelines)
  const P = {"az1": 96.9222, "el1": 66.1536, "az2": 12.9801, "el2": 54.6982, "wd": 75.8669, "wa": -13.9683, "b3": 0.2391, "lE": 30.0, "lc": 25.0, "phiE": 0.0, "phib": -90.0, "stk": 5.0, "ang_min": 30.0, "r1t": 0.8048, "r1d": -30.5908, "r2t": 0.549, "r2d": -1.2849, "rc": 10.0};
  const G = {"u":[[0.04873,0.91463,0.40134],[-0.59297,0.76675,0.24593],[-0.21421,-0.13517,0.96739]],"c":[[0.0,0.0,0.0],[0.0,0.0,-0.0],[-0.686,-7.736,-1.233]],"sa":[0.02922,-0.99082,-0.13197],"st":[0.97635,0.0,0.21619],"sn":[-0.21421,-0.13517,0.96739],"A":[39.547,74.854],"branch":-1.0,"m":[-6.125,0.919,0.0],"f":[51.21,61.24,73.69],"tr":79.17,"tp":2.25,"RUN":0.5,"SING":10.0,"hr":[10.0,10.0,10.0],"A0":[0.19,-37.46,-5.192],"A0m":[0.909,-31.391,-4.185],"Bm":[-23.5,-31.391,-9.59],"eE":[0.02922,-0.99082,-0.13197],"eK":[-0.97635,-0.0,-0.21619],"L1":[[-3.42,51.99,13.2],[-4.29,49.77,11.05],[-5.37,50.44,9.61],[-7.64,52.08,6.68],[-8.79,52.71,5.12],[-9.94,53.21,3.52],[-11.07,53.51,1.87],[-12.13,53.42,0.19],[-13.38,53.89,-1.48],[-16.66,53.73,-3.94],[-18.73,53.71,-4.58],[-20.8,53.36,-4.74],[-22.9,53.06,-4.43],[-24.75,52.45,-3.62],[-26.25,51.7,-2.36],[-28.58,50.87,1.06],[-30.58,52.07,2.96],[-33.35,54.37,5.1]],"L2":[[-40.6,46.18,25.98],[-36.92,39.96,26.58],[-37.4,38.41,29.9],[-37.64,36.57,33.11],[-37.69,34.5,36.22],[-37.97,31.48,41.24],[-37.88,29.14,44.41],[-37.82,26.75,47.74],[-36.91,23.71,50.06],[-36.07,20.69,52.49],[-35.15,17.67,54.99],[-33.91,14.56,57.27],[-32.24,11.26,58.85],[-29.96,6.35,61.72],[-27.95,2.93,62.67],[-26.0,-0.47,63.75],[-24.97,-4.05,67.36],[-24.81,-8.31,74.24]]};
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
    id: 'raglan-knee-3r', name: 'Raglan-knee 3R: pin-knee chain with a bent (raglan) link 1',
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
        { kind: 'arc', role: 'link', name: 'link 1 (8 x 3 strap, raglan route: one tangent arc, fitted)', pts: G.L1.map(p => on(F.R1, F.t1, p)), r: 2.5 },
        h2,
        { kind: 'arc', role: 'link', name: 'link 2 (8 x 3 strap, raglan route, fitted)', pts: G.L2.map(p => on(F.R12, F.t2, p)), r: 2.5 },
        h3,
        { kind: 'link', role: 'link', name: 'E strap (member 3: hub 3 lower plate -> pin a)', a: rim, b: lvl(paW, G.tr + 1.5), r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'knee pin a (iglidur pin, parallel to J3)', c: lvl(paW, G.tr), axis: n3, r: 6, h: P.stk, p0: lvl(paW, G.tr) },
        { kind: 'link', role: 'link', name: 'knee link (flat Ti plate)', a: lvl(paW, kz), b: lvl(pbW, kz), r: 3 },
        { kind: 'hub', role: 'passive', name: 'knee pin b (iglidur pin, parallel to J3)', c: lvl(pbW, G.tr), axis: n3, r: 6, h: P.stk, p0: lvl(pbW, G.tr) },
        { kind: 'plate', role: 'fixed-arm', name: 'arm pad (on the cuff / BOTTOM)', c: padC, z: padN, x: arm(sa), size: [14, 14], t: G.tp },
        { kind: 'link', role: 'fixed-arm', name: 'BOTTOM bar to the cuff (schematic)', a: V.madd(padC, padN, -2), b: lat, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: V.scale(ctx.armAxis, 155), axis: ctx.armAxis, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  };
  K.register(C);
})();
