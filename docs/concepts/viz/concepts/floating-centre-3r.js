/* floating-centre-3r - the champion spherical 3R (r20 s1414 #4) whose base sits on a passive 3-axis FLOAT instead of
 * self-aligning slides at the cuff (docs/concepts/floating-centre-3r.md, models/floating-centre-3r.py). The cuff is
 * rigid. Best measured layout: the float BESIDE J1 (stage at az 0 / el 35 on the scapula, a bracket carries J1), and
 * under the slip law the travel that covers it is +-15 mm in plane / +-6 mm normal (sweep k28 / slip runs).
 * The bench rig has no slip, so on it the float would sit at 0: this preview adds the model's SLIP EXTENSION (central
 * law, judge/base_slip.py: error angles about the ISB scapula axes + 4.2 mm superior translation, Seth 2016 lever) to
 * the handler, as the model does: the handler offset delta = (Re - I) r + d moves the base plate (the model keeps the
 * kinematics unchanged by slip, so the plate translates and the chain orientation is the plain 3R closure). The
 * float's 3 slides take whatever brings the chain centre back onto the real GH (closure c = GH: f = -delta), so they
 * are PASSIVE, set by closure. 3 ACTIVE + 3 PASSIVE. Overhead the law needs ~18 mm in plane: past the +-15 travel. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const P = { az: 2.4305071427308924, el: 80.67633718429899, a: [76.90180446920043, 66.74921235407174],
              w: [86.32769021001913, 21.829657347343378], branch: -1, faces: [54, 93.18, 71.85, 78.50],
              stage_az: 0, stage_el: 35, plate_r: 60, trav_t: 15, trav_n: 6, hub_r: 10, stack: 12.25,
              neck_deg: 25, cuff_at: 165, sing_deg: 10, lever: [20.1233, -33.9998, 21.0870] };
  const C = K.sph3r(K.bvec(P.az, P.el), K.wdir(P.w[0], P.w[1]), P.a[0], P.a[1], P.branch);
  // ISB scapula axes in the bench scapula frame (model: Zs = unit(0.5, 0, 0.87), Ys = y, Xs = Ys x Zs)
  const ZS = V.unit([0.5, 0, 0.87]), YS = [0, 1, 0], XS = V.cross(YS, ZS);
  const A = V.scale(V.add(V.add(V.scale(XS, P.lever[0]), V.scale(YS, P.lever[1])), V.scale(ZS, P.lever[2])), -1); // handler anchor
  /** central slip law (judge/base_slip.py angles + translation) -> handler offset delta (scapula frame, mm) */
  function slip(p) {
    const pl = Math.min(90, Math.max(0, p.plane)), e = Math.max(0, p.elev), base = (7 - 2 * pl / 90) * Math.min(e, 100) / 100;
    const u = Math.min(1, Math.max(0, (e - 100) / 20)), hi = [6.3, 11.4, 8.6];
    const th = hi.map(h => base + u * (h - base));
    th[1] += Math.min(1, Math.max(0, (e - 120) / 30)) * (25 - 11.4);
    const Re = M.mul(M.mul(M.rot(XS, th[0]), M.rot(YS, th[1])), M.rot(ZS, th[2]));
    return V.add(V.sub(M.mulv(Re, V.scale(A, -1)), V.scale(A, -1)), V.scale(YS, 4.2 * Math.min(e, 150) / 150));   // delta
  }
  // float frame on the plate: normal n (radial at the stage site), in-plane t1 (lateral-ish), t2
  const n = K.bvec(P.stage_az, P.stage_el), t1 = V.unit(V.reject([0, 0, 1], n)), t2 = V.cross(n, t1);
  const Pc = V.scale(n, P.plate_r);
  const fvec = q => V.add(V.add(V.scale(t1, q[3]), V.scale(t2, q[4])), V.scale(n, q[5]));
  function frame(ctx) {
    const dl = slip(ctx.pose), hand = x => M.mulv(ctx.S, V.add(x, dl));                // handler-fixed point -> world
    return { dl, SR: ctx.S, hand, ctxE: ctx };
  }
  const solve = ctx => {
    const F = frame(ctx), f = V.scale(F.dl, -1);                                       // closure: chain centre on GH
    return C.solve(ctx).concat([V.dot(f, t1), V.dot(f, t2), V.dot(f, n)]);
  };

  K.register({
    id: 'floating-centre-3r',
    name: 'Floating-centre 3R (float under the base)',
    dof: { active: 3, passive: 3 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'J2', 'J3', 'float t1', 'float t2', 'float normal'], qUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve,
    residual: (q, ctx) => {
      const F = frame(ctx);
      return C.residual(q, F.ctxE).concat(F.hand(fvec(q)));                              // chain centre must sit on GH
    },
    check: (q, ctx) => {
      const m = C.margin(frame(ctx).ctxE);
      if (m < 0) return 'J2 cannot close: the arm axis is out of the chain\'s reach';
      if (m < P.sing_deg) return `J2 within ${m.toFixed(0)} deg of its fold`;
      if (Math.abs(q[3]) > P.trav_t || Math.abs(q[4]) > P.trav_t) return 'float past its in-plane travel';
      if (Math.abs(q[5]) > P.trav_n) return 'float past its normal travel';
      return null;
    },
    parts: (q, ctx) => {
      const F = frame(ctx), f = C.fk(q, F.ctxE), Fc = P.faces, h = P.stack, hand = F.hand, fv = fvec(q);
      const o = hand(fv), at = (d, r) => V.madd(o, d, r);                                   // chain centre (= GH when closed)
      const chain = x => hand(V.add(x, fv)), nW = M.mulv(F.SR, n), tW = M.mulv(F.SR, t1);
      const harm = ctx.armAxis, ng = P.neck_deg * K.D2R;
      const nk = V.unit(V.add(V.scale(f.p3, Math.cos(ng)), V.scale(V.unit(V.reject(harm, f.p3)), Math.sin(ng))));
      const neckEnd = at(nk, Fc[2] + 1), cuffC = V.scale(harm, P.cuff_at);
      const cuffTop = V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47);
      const T = P.trav_t, x1 = V.scale(t1, q[3]), x12 = V.add(x1, V.scale(t2, q[4]));
      const pin = p => hand(V.add(Pc, p));                                                  // plate / stage point
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base plate (rides the slipping handler)', c: pin([0, 0, 0]), z: nW, x: tW, size: [2 * T + 18, 2 * T + 14], t: 2.5 },
        { kind: 'slider', role: 'passive', name: 'float slide t1', a: pin(V.madd(V.scale(t1, -T), n, 2)), b: pin(V.madd(V.scale(t1, T), n, 2)), at: pin(V.madd(x1, n, 3)), z: nW, size: [14, 12, 3] },
        { kind: 'slider', role: 'passive', name: 'float slide t2', a: pin(V.madd(V.madd(x1, t2, -T), n, 5)), b: pin(V.madd(V.madd(x1, t2, T), n, 5)), at: pin(V.madd(x12, n, 6)), z: nW, size: [12, 12, 3] },
        { kind: 'slider', role: 'passive', name: 'float slide normal', a: pin(V.madd(x12, n, 8 - P.trav_n)), b: pin(V.madd(x12, n, 10 + P.trav_n)), at: chain(V.madd(Pc, n, 9)), z: tW, size: [10, 10, 4] },
        { kind: 'link', role: 'link', name: 'bracket float -> J1', a: chain(V.madd(Pc, n, 11)), b: at(f.p1, Fc[0] - 1), r: 3 },
        { kind: 'hub', role: 'active', name: 'J1', c: at(f.p1, Fc[0]), axis: f.p1, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 1', pts: K.greatArc(f.p1, f.p2, Fc[0] + 7, Fc[1] + 2).map(p => V.add(p, o)), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2', c: at(f.p2, Fc[1]), axis: f.p2, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 2', pts: K.greatArc(f.p2, f.p3, Fc[1] + 9, Fc[3] + 2).map(p => V.add(p, o)), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3', c: at(f.p3, Fc[2]), axis: f.p3, r: P.hub_r, h },
        { kind: 'arc', role: 'fixed-arm', name: 'neck', pts: K.greatArc(f.p3, nk, Fc[2] + 1, Fc[2] + 1).map(p => V.add(p, o)), r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'neck to rigid cuff', a: neckEnd, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff (rigid, no slides)', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'passive', name: 'parent chain centre without the float (slipped)', p: hand([0, 0, 0]), r: 2.5 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
