/* crest-knee-3r - the verified pin knee (skin-normal-3r-pin-knee) moved to the DELTOID-CREST seats with a JOGGLED knee link (round-14 lens 3, re-dispatch 2, 2026-10-18). Chain: scapula handler -> J1 (ACTIVE, O20, GH ray, bvec(103.5, 63.5)) -> link 1 (8 x 3 Ti) -> J2 (ACTIVE, O20, GH ray, home bvec(28.9, 49.7)) -> link 2 (flies over the WHOLE member 3) -> J3 (ACTIVE, O20 on the crest wdir(90.9, -3.3), axis tilted b3 0.30 toward the skin normal; a dowel-in-slot J3 own-angle stop, frozen window 268.7 + 246.0 deg, not drawn) -> member 3 = hub 3's lower plate + E strap (lE 71.6) + E boss at tr_a 65.2 -> pin a (PASSIVE, MR63ZZ pair, parallel to J3) -> knee link (lc 24.3, machined Ti, steps 1.2 mm from the pin-a flat to the pin-b flat) -> pin b (PASSIVE) -> O12 arm pad at tr_b 64.0 on the cuff / BOTTOM. 3 active, 2 passive rotations, 0 passive translations, cx 0. Best claimed configuration: fast 23.31 / near-touch 24.51 on Bench(60,160); frozen exact Bench(110,360) 31.43, held out 27.83 (flat-knee verified 32.84 / 29.81; H1 27.20). Home geometry exported from docs/concepts/models/crest-knee-3r.py (JogModel) fit on Bench(60,160). Red = the J2 fold or the knee outside [ang_min, 180 - ang_min] / its span. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  // best configuration (bench model parameters) and the home-frame geometry the model builds from it (exported from the
  // model's Design / fit on Bench(60,160): axis directions u, line points c, hub face levels f along u, hub 3's plane
  // basis sa / st / sn = u3, mid drift m, knee level tr, pin a / pin b home points, fitted link centrelines)
  const P = {"az1": 103.4555, "el1": 63.5395, "az2": 28.8728, "el2": 49.6716, "wd": 90.9089, "wa": -3.3366, "b3": 0.2965, "lE": 71.59, "lc": 24.3303, "phiE": -1.3705, "phib": -94.6763, "stk": 6.0, "ang_min": 25.9825, "kj": 1.0};
  const G = {"u":[[0.10368,0.89524,0.43335],[-0.56017,0.69369,0.45277],[-0.04124,0.11757,0.99221]],"c":[[0.0,0.0,0.0],[-0.0,0.0,-0.0],[-0.174,-6.243,0.733]],"sa":[-0.00488,-0.99306,0.11747],"st":[0.99914,0.0,0.04153],"sn":[-0.04124,0.11757,0.99221],"A":[40.611,56.365],"branch":-1.0,"m":[-6.05,0.144,0.0],"f":[51.74,61.06,65.95],"tr":65.19,"trb":64.03,"BR":6.0,"tp":2.75,"RUN":0.5,"SING":5.0,"hr":[10.0,10.0,10.0],"A0":[-2.234,-77.316,9.069],"A0m":[-2.061,-71.308,8.364],"Bm":[-26.28,-69.338,7.124],"eE":[-0.02878,-0.99278,0.11644],"eK":[-0.99541,0.08096,-0.05097],"L1":[[-4.764,46.631,22.974],[-5.091,44.299,24.755],[-7.469,44.784,23.979],[-9.319,45.194,24.525],[-11.254,45.686,25.132],[-13.242,46.092,25.705],[-15.309,46.5,26.29],[-17.509,47.034,26.959],[-19.788,47.507,27.616],[-21.991,47.58,28.054],[-24.886,48.851,29.225]],"L2":[[-32.75,39.191,38.436],[-29.102,36.526,38.233],[-28.275,33.522,39.716],[-26.452,33.044,41.598],[-26.302,30.884,44.038],[-24.542,30.499,46.14],[-24.215,28.09,48.383],[-22.29,27.535,50.35],[-21.846,24.95,52.472],[-19.745,24.218,54.236],[-19.028,21.408,55.383],[-17.552,20.089,56.541],[-16.052,18.749,57.672],[-14.508,17.368,58.702],[-13.533,14.908,59.488],[-12.016,13.519,60.627],[-10.794,12.458,63.662],[-11.091,10.684,69.192]]};
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
    id: 'crest-knee-3r', name: 'Crest pin-knee 3R: crest seats, link 2 over member 3, two-pin MR63ZZ knee with a joggled knee link (0 passive translations)',
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
      const paW = F.pa, pbW = F.pb, kz = G.tr + G.tp + G.RUN + G.tp / 2, kzb = G.trb + G.tp + G.RUN + G.tp / 2, kdir = V.unit(V.sub(pbW, paW)), kl = V.norm(V.sub(pbW, paW));
      const rim = on(F.Rm3, F.t3, V.add(V.madd(c[2], sn, G.f[2] + 1.5), V.scale(G.eE, rad)));
      const arm = p => M.mulv(ctx.H, p);                             // arm-fixed home point -> world (= S Q p)
      const padC = arm(V.madd(G.Bm, sn, G.trb + G.tp / 2)), padN = M.mulv(ctx.H, sn);
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
        { kind: 'arc', role: 'link', name: 'knee link (JOGGLED Ti link machined from solid: pin-a flat, ramp, pin-b flat)', pts: [lvl(paW, kz), lvl(V.madd(paW, kdir, G.BR), kz), lvl(V.madd(paW, kdir, kl - G.BR), kzb), lvl(pbW, kzb)], r: 3 },
        { kind: 'hub', role: 'passive', name: 'knee pin b (MR63ZZ pair, parallel to J3)', c: lvl(pbW, G.trb), axis: n3, r: 6, h: P.stk, p0: lvl(pbW, G.trb) },
        { kind: 'plate', role: 'fixed-arm', name: 'arm pad (on the cuff / BOTTOM)', c: padC, z: padN, x: arm(sa), size: [14, 14], t: G.tp },
        { kind: 'link', role: 'fixed-arm', name: 'BOTTOM bar to the cuff (schematic)', a: V.madd(padC, padN, -2), b: lat, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: V.scale(ctx.armAxis, 155), axis: ctx.armAxis, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  };
  K.register(C);
})();
