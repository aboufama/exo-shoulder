/* twin-rail-one-hub - twin rails, one hub (catalogue entry; ideated, no bench model yet). A spherical 3R whose J1 and J3
 * have VIRTUAL axes: J1 = carriage 1 on a scapula-fixed crown rail (26 mm wire-race band, circle about a1 at cone
 * alpha12, laid over the acromion / supraspinatus at R 57 = the S-fixed crown skin 48-55 + 2), J2 = the ONLY hub (a
 * KAA15-class donut on carriage 1, axis a2 = the carriage's ray through GH, at the rail's level), link 2 = a short strap
 * to carriage 3 on an ARM-fixed rail (circle about a3 at cone alpha32) along the lateral upper arm, fixed to the cuff
 * saddle under BOTTOM: J3 = carriage 3's place on it. No hub at the J1 / J3 poles, so they point into the body.
 * Axes (no sweep exists; chosen by a search on this loop, 20k designs, with the crown circle through the crown patch
 * c* = bvec(22.8, 65.6) and the arm circle through the lateral upper arm wdir(25, 20)): a1 = c* turned 65.3 deg
 * (posteromedial, into the body), a3 = an anterior arm axis (the rail circle at cone 76.6 runs down the lateral arm),
 * alpha12 65.3, a2-a3 98.1, branch +1. Rails: J1 travel 70 deg (the crown patch, +-35) + the 50 mm shoe, J3 travel
 * 82 deg (the arm sector) + the shoe, windows centred where this loop needs them; circular arm rail at one radius
 * (2 + the highest schematic arm-skin estimate along its window): here the J3 window lands on the lateral deltoid at
 * ~72 mm, not the catalogue's 100-200 mm down the arm. The catalogue's main risk is real: frames whose carriages leave
 * the windows are reported (behind the back the crown carriage would also run over the arm). 3 active, 0 passive; closed form (KIN.sph3r). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = K.D2R;
  const P = { psi1: 49.2, a12: 65.3, psi3: -74.8, a32: 76.6, a23: 98.1, branch: 1, margin: 10, T1: 70, T3: 82, Lc: 50,
              R1: 57, band_w: 26, donut: [19, 26], cuff_at: 175 };
  const cstar = K.bvec(22.8, 65.6), Lstar = K.wdir(25, 20);
  const a1L = K.onCone(cstar, V.perp(cstar), P.a12, P.psi1), a3L = K.onCone(Lstar, V.perp(Lstar), P.a32, P.psi3);
  const C = K.sph3r(a1L, a3L, P.a12, P.a23, P.branch);
  const e3 = V.unit(V.reject(C.u2, C.u3)), c3L = V.add(V.scale(C.u3, Math.cos(P.a32 * D2R)), V.scale(e3, Math.sin(P.a32 * D2R)));
  const ref3L = V.unit(V.reject([0, -1, 0], a3L));                        // arm rail azimuth 0 (humerus frame, down the arm)
  const skinR = c3H => { const th = V.angle(c3H, [0, -1, 0]) * D2R; return Math.max(58, 50 / Math.max(Math.sin(th), 0.2)); };   // schematic arm skin
  function frame(q, ctx) {
    const f = C.fk(q, ctx), c3 = M.mulv(M.mul(ctx.S, f.R12), c3L), ref3 = M.mulv(ctx.H, ref3L);
    return Object.assign(f, { c3, ref1: M.mulv(ctx.S, C.u2), ref3, az3: K.axisAngle(f.p3, ref3, c3) });
  }
  let WIN = null;
  function win() {                                         // travel windows (best T1 / T3 window over this loop) + arm rail radius
    if (WIN) return WIN;
    const Q = [];
    for (const fr of K.motion(120)) { const ctx = K.makeCtx(fr.pose); if (C.margin(ctx) < P.margin) continue;
      const q = C.solve(ctx), f = frame(q, ctx); Q.push({ q1: q[0], az3: f.az3, c3H: M.mulv(M.T(ctx.H), f.c3) }); }
    const best = (a, w) => { let b = -1, c0 = 0; for (let c = -180; c < 180; c += 2) { const k = a.filter(x => Math.abs(K.wrap180(x - c)) <= w / 2).length; if (k > b) { b = k; c0 = c; } } return c0; };
    const w1 = best(Q.map(x => x.q1), P.T1), w3 = best(Q.map(x => x.az3), P.T3);
    const R3 = 2 + Math.max(...Q.filter(x => Math.abs(K.wrap180(x.az3 - w3)) <= P.T3 / 2).map(x => skinR(x.c3H)));
    return (WIN = { w1, w3, R3, h1: P.Lc / 2 / (P.R1 * Math.sin(P.a12 * D2R)) * K.R2D, h3: P.Lc / 2 / (R3 * Math.sin(P.a32 * D2R)) * K.R2D });
  }

  K.register({
    id: 'twin-rail-one-hub',
    name: 'Twin rails, one hub (virtual J1 and J3)',
    dof: { active: 3, passive: 0 },
    params: P,
    q0: ctx => C.solve(ctx),
    qNames: ['J1 carriage on the crown rail', 'J2 donut (the only hub)', 'J3 carriage on the arm rail'], qUnits: ['deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => C.solve(ctx),
    residual: (q, ctx) => C.residual(q, ctx),
    check: (q, ctx) => {
      const m = C.margin(ctx);
      if (m < 0) return 'J2 cannot close: the arm is out of the chain\'s reach';
      if (m < P.margin) return `J2 within ${m.toFixed(0)} deg of its fold`;
      const w = win();
      if (Math.abs(K.wrap180(q[0] - w.w1)) > P.T1 / 2) return 'carriage 1 past the end of the crown rail (crown patch +-35 deg)';
      if (Math.abs(K.wrap180(frame(q, ctx).az3 - w.w3)) > P.T3 / 2) return 'carriage 3 past the end of the arm rail (82 deg sector)';
      return null;
    },
    parts: (q, ctx) => {
      const f = frame(q, ctx), w = win(), R1 = P.R1, R3 = w.R3, a12 = P.a12 * D2R, a32 = P.a32 * D2R;
      const rail = (role, name, k, R, cone, ref, a0, a1, r) => ({ kind: 'rail', role, name, c: V.scale(k, R * Math.cos(cone)), axis: k, ref,
        rho: R * Math.sin(cone), a0, a1, r });
      const t1 = V.unit(V.cross(f.p1, f.p2)), t3 = V.unit(V.cross(f.p3, f.c3));
      const dn = V.scale(f.p2, R1 + 6), c3top = V.scale(f.c3, R3 + 9), harm = ctx.armAxis, cuffC = V.scale(harm, P.cuff_at);
      const s3 = (a) => V.scale(K.onCone(f.p3, f.ref3, P.a32, a), R3 + 3);
      const railEnd = s3(w.w3 + Math.sign(K.wrap180(V.dot(s3(w.w3 + 41), harm) - V.dot(s3(w.w3 - 41), harm)) || 1) * (P.T3 / 2 + w.h3));
      const cuffTop = V.madd(cuffC, V.unit(V.reject(railEnd, harm)), 47);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'crown base (scapula handler)', c: V.scale(M.mulv(ctx.S, cstar), R1 - 6), z: M.mulv(ctx.S, cstar), x: ctx.attach.scapDir([1, 0, 0]), size: [40, 30], t: 3 },
        rail('fixed-scapula', 'crown rail (circle about the virtual J1 axis)', f.p1, R1, a12, f.ref1, w.w1 - P.T1 / 2 - w.h1, w.w1 + P.T1 / 2 + w.h1, 4),
        { kind: 'carriage', role: 'active', name: 'J1 carriage 1 (50 mm shoe)', c: V.scale(f.p2, R1 + 4), x: t1, z: f.p2, size: [P.Lc, 30, 6] },
        { kind: 'ring', role: 'active', name: 'J2 donut (the only hub, axis a2)', c: dn, axis: f.p2, r: (P.donut[0] + P.donut[1]) / 2, t: (P.donut[1] - P.donut[0]) / 2, h: 9 },
        { kind: 'arc', role: 'link', name: 'link 2 (short strap)', pts: K.greatArc(V.madd(dn, V.unit(V.reject(f.c3, f.p2)), P.donut[1]), c3top, R1 + 9, R3 + 9), r: 3 },
        { kind: 'carriage', role: 'active', name: 'J3 carriage 3 (50 mm shoe)', c: V.scale(f.c3, R3 + 6), x: t3, z: f.c3, size: [P.Lc, 30, 6] },
        rail('fixed-arm', 'arm rail (circle about the virtual J3 axis)', f.p3, R3 + 3, a32, f.ref3, w.w3 - P.T3 / 2 - w.h3, w.w3 + P.T3 / 2 + w.h3, 4),
        { kind: 'link', role: 'fixed-arm', name: 'cuff saddle (under BOTTOM)', a: railEnd, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
