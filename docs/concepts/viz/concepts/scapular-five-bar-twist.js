/* scapular-five-bar-twist - both pointing joints are scapula-fixed hubs on the two quietest seats (catalogue
 * scapular-five-bar-twist; no model / sweep yet, so the spec's chain). A spherical 2-DOF five-bar plus a coaxial twist,
 * every axis through GH: ACTIVE hub A on the acromion top (sdir(55, 15)) and ACTIVE hub B on the posterior-superior zone
 * (sdir(40, 100)), both fixed to the scapula -> proximal straps L_A (72 deg) and L_B (110 deg) -> PASSIVE elbow hubs
 * E_A, E_B -> distal straps D_A (72) and D_B (55) -> meet at C, an arm-fixed site (armpt(30, 0, 80), lateral deltoid)
 * with a stacked double hub: D_B - arm = the ACTIVE twist about GH-C, D_A - D_B PASSIVE -> neck down the lateral strip
 * to the cuff. Closed form: E = circ_int(u, alpha, C, beta) on the branches fixed at rest (elbows outside the arm's
 * path), hub angles from the home pose; the residual is the five-bar's forward kinematics (C from the two elbows, the
 * assembly mode nearer the arm's C; twist from D_B's tangent at C) against the arm frame. 3 ACTIVE + 3 PASSIVE. Hub radii
 * are schematic (acromion 52, posterior 60, elbows 70, C at the spec's 80 mm). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = K.D2R;
  const P = { uA: [55, 15], uB: [40, 100], C: [30, 0, 80], alA: 72, beA: 72, alB: 110, beB: 55, tri: 8, trans: [20, 160],
              faces: [52, 60], rE: 70, rC: 80, hub_r: 10, stack: 12.25, neck: [65, 0, 62], cuff_at: 165 };
  const sdir = (la, lo) => [-Math.cos(la * D2R) * Math.sin(lo * D2R), Math.sin(la * D2R), Math.cos(la * D2R) * Math.cos(lo * D2R)];
  const ea = [-0.023, -0.986, 0.164], el = [0.004, 0.164, 0.986], eb = [-1, 0.023, 0];
  const armpt = (s, th, r) => V.add(V.scale(ea, s), V.scale(V.add(V.scale(el, Math.cos(th * D2R)), V.scale(eb, Math.sin(th * D2R))), r));
  const uA = V.unit(sdir(...P.uA)), uB = V.unit(sdir(...P.uB)), w = V.unit(armpt(...P.C));
  const Qs = ctx => M.mul(M.T(ctx.S), ctx.Hb);                                       // arm (bind) -> scapula frame
  // branches fixed at the loop's rest pose: each elbow on the side farther from the arm axis; the five-bar's assembly mode
  const ctx0 = K.makeCtx(K.KEYS[0].pose), uC0 = M.mulv(Qs(ctx0), w), arm0 = M.mulv(Qs(ctx0), ea);
  const side = (u, a, b) => [1, -1].sort((x, y) => V.angle(K.circInt(u, a, uC0, b, y).p, arm0) - V.angle(K.circInt(u, a, uC0, b, x).p, arm0))[0];
  const sA = side(uA, P.alA, P.beA), sB = side(uB, P.alB, P.beB);
  const EA0 = K.circInt(uA, P.alA, w, P.beA, sA).p, EB0 = K.circInt(uB, P.alB, w, P.beB, sB).p;   // home (arm = scapula frame)
  const EAr = K.circInt(uA, P.alA, uC0, P.beA, sA).p, EBr = K.circInt(uB, P.alB, uC0, P.beB, sB).p;
  const sC = [1, -1].sort((x, y) => V.angle(K.circInt(EAr, P.beA, EBr, P.beB, x).p, uC0) - V.angle(K.circInt(EAr, P.beA, EBr, P.beB, y).p, uC0))[0];
  const tan = (C, X) => V.unit(V.reject(V.sub(X, C), C));
  function fk(q, near) {                    // scapula frame; assembly mode = the one nearer the arm's C (modes swap only
    const EA = M.mulv(M.rot(uA, q[0]), EA0), EB = M.mulv(M.rot(uB, q[1]), EB0);      // through the transmission singularity)
    const cs = [sC, -sC].map(s => K.circInt(EA, P.beA, EB, P.beB, s)), c = near && V.angle(cs[1].p, near) < V.angle(cs[0].p, near) ? cs[1] : cs[0];
    const t = M.mulv(M.rot(c.p, q[2]), tan(c.p, EB));
    return { EA, EB, C: c.p, ok: c.ok, F: M.fromCols(c.p, t, V.cross(c.p, t)) };
  }
  function solveRaw(ctx) {
    const Q = Qs(ctx), uC = M.mulv(Q, w), EA = K.circInt(uA, P.alA, uC, P.beA, sA).p, EB = K.circInt(uB, P.alB, uC, P.beB, sB).p;
    return [K.axisAngle(uA, EA0, EA), K.axisAngle(uB, EB0, EB), K.axisAngle(uC, tan(uC, EB), M.mulv(Q, el))];
  }

  K.register({
    id: 'scapular-five-bar-twist',
    name: 'Scapular five-bar + twist',
    dof: { active: 3, passive: 3 },
    params: Object.assign({ branches: { sA, sB, sC } }, P),
    q0: ctx => solveRaw(ctx),
    qNames: ['A (acromion hub)', 'B (posterior hub)', 'twist at C'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: (ctx, qp) => { const q = solveRaw(ctx); return qp ? q.map((x, i) => qp[i] + K.wrap180(x - qp[i])) : q; },
    residual: (q, ctx) => {
      const Q = Qs(ctx), uC = M.mulv(Q, w), t = V.unit(V.reject(M.mulv(Q, el), uC));
      return M.rotErrDeg(fk(q, uC).F, M.fromCols(uC, t, V.cross(uC, t)));
    },
    check: (q, ctx) => {
      const uC = M.mulv(Qs(ctx), w);
      if (K.foldMargin(uA, uC, P.alA, P.beA) < P.tri) return 'leg A cannot close or is near its fold';
      if (K.foldMargin(uB, uC, P.alB, P.beB) < P.tri) return 'leg B cannot close or is near its fold';
      const f = fk(q, uC), tr = V.angle(tan(f.C, f.EA), tan(f.C, f.EB));
      if (tr < P.trans[0] || tr > P.trans[1]) return `five-bar singularity at C (transmission ${tr.toFixed(0)} deg)`;
      return null;
    },
    parts: (q, ctx) => {
      const f = fk(q, M.mulv(Qs(ctx), w)), W = d => M.mulv(ctx.S, d), A = W(uA), B = W(uB), EA = W(f.EA), EB = W(f.EB), C = W(f.C), F = P.faces, h = P.stack;
      const Ca = M.mulv(ctx.Hb, w), neckEnd = M.mulv(ctx.Hb, armpt(...P.neck)), cuffC = V.scale(ctx.armAxis, P.cuff_at);
      return [
        { kind: 'arc', role: 'fixed-scapula', name: 'base (both hubs on the scapula handler)', u: A, v: B, r0: F[0] - 3, r1: F[1] - 3, r: 4 },
        { kind: 'hub', role: 'active', name: 'A (acromion top)', c: V.scale(A, F[0]), axis: A, r: P.hub_r, h },
        { kind: 'hub', role: 'active', name: 'B (posterior-superior)', c: V.scale(B, F[1]), axis: B, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'L_A', u: A, v: EA, r0: F[0] + 4.6, r1: P.rE, r: 2.5 },
        { kind: 'arc', role: 'link', name: 'L_B', u: B, v: EB, r0: F[1] + 4.6, r1: P.rE, r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'elbow E_A', c: V.scale(EA, P.rE - 4), axis: EA, r: P.hub_r, h },
        { kind: 'hub', role: 'passive', name: 'elbow E_B', c: V.scale(EB, P.rE - 4), axis: EB, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'D_A', u: EA, v: C, r0: P.rE + 6, r1: P.rC + 9.5, r: 2.5 },
        { kind: 'arc', role: 'link', name: 'D_B', u: EB, v: C, r0: P.rE + 6, r1: P.rC + 4, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'twist at C (D_B - arm)', c: V.scale(C, P.rC), axis: C, r: P.hub_r, h: 6.3 },
        { kind: 'hub', role: 'passive', name: 'C (D_A - D_B)', c: V.scale(C, P.rC + 6.3), axis: C, r: P.hub_r - 1, h: 6.3 },
        { kind: 'link', role: 'fixed-arm', name: 'neck down the lateral strip', a: V.scale(Ca, P.rC - 1), b: neckEnd, r: 3.5 },
        { kind: 'link', role: 'fixed-arm', name: 'neck to cuff', a: neckEnd, b: V.madd(cuffC, V.unit(V.reject(neckEnd, ctx.armAxis)), 47), r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: ctx.armAxis, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
