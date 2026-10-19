/* sliding-rivet-pauldron - a HUBLESS spherical 3R: nested 2 mm Ti plates over the shoulder, each joint a pair of
 * needle-roller followers on one plate running in two coaxial circular slots of the next (docs/concepts/
 * sliding-rivet-pauldron.md, models/sliding-rivet-pauldron.py; verdict dead, best k35 gap 177). Two rollers in two
 * slots about one axis = a revolute through GH, so the axes are the champion's b, p2, W (r20 s1414 #4, branch -1) and
 * the angles are the plain 3R closure (closed form). Chain: S cap (scapula, slots about b at polar 8 / 19 deg) ->
 * L1 guide disc (followers 90 deg apart, model correction) -> L2 band (two slots on circles about p2 at polar A1 +- 6,
 * L1's followers ride them at b's meridian, 30 deg apart) + ramped strap + arm-end disc (slots about W at polar 8 / 17,
 * a full ring track when the travel needs it) -> H saddle on the arm (its followers) -> BOTTOM stub, cuff.
 * Slot spans = the loop's travel + 8 deg (a full ring past 330 deg). Radii: S cap 59.5, L1 +2.5, band +5 (the spec's
 * nesting), saddle 65.3, arm-end disc +2.5. The measured limiter shows on the loop: the band must store the change of
 * the b-W angle PAST b, so overhead its tail runs over the neck (the model had to lift the band to 152 mm). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const P = { b_az: 2.4305, b_el: 80.6763, w_d: 86.3277, w_az: 21.8297, A1: 76.9018, A2: 66.7492, branch: -1, sing: 5,
              RS: 59.5, RH: 65.3, g1: [8, 19], fsep1: 90, d2: 6, D2: 30, g3: [8, 17], fsep3: 90, band_half: 12,
              rhoS: 20, rho1: 21.6, rho3: 15.1, car: [8, 5, 4], neck_deg: 25, cuff_at: 165 };
  const C = K.sph3r(K.bvec(P.b_az, P.b_el), K.wdir(P.w_d, P.w_az), P.A1, P.A2, P.branch);
  const u1 = C.u1, u2 = C.u2, u3 = C.u3, R1 = P.RS + 2.5, RB = P.RS + 5, RA = P.RH + 2.5;
  const ref1 = V.unit(V.reject(u2, u1)), ref2 = V.unit(V.reject(u1, u2)), ref3 = V.unit(V.reject(u2, u3));
  const azW = K.axisAngle(u2, ref2, u3);                                   // W's azimuth about p2 in the band frame
  // slot spans from the loop's travel (q1 for J1, -q2 = b's azimuth in the band, q3 for J3)
  const span = [[1e9, -1e9], [1e9, -1e9], [1e9, -1e9]];
  for (const fr of K.motion(240)) {
    const q = C.solve(K.makeCtx(fr.pose)), v = [q[0], -q[1], q[2]];
    v.forEach((x, k) => { span[k][0] = Math.min(span[k][0], x); span[k][1] = Math.max(span[k][1], x); });
  }
  const pad = [8, 8, 8], lim = span.map(([a, b], k) => (b - a + 2 * pad[k] > 330 ? [-180, 180] : [a - pad[k], b + pad[k]]));
  const sh = (a, d) => (a[1] - a[0] >= 360 ? a : [a[0] + d, a[1] + d]);   // slot span for a follower at azimuth offset d
  /** a slot / band edge: circle of polar angle pol about the member-fixed axis k (home coords), radius R, mapped by X */
  const slot = (X, k, ref, pol, R, a, role, name, r) => ({ kind: 'rail', role, name, c: M.mulv(X, V.scale(k, R * Math.cos(pol * K.D2R))),
    axis: M.mulv(X, k), ref: M.mulv(X, ref), rho: R * Math.sin(pol * K.D2R), a0: a[0], a1: a[1], r: r || 2 });
  const fol = (X, k, ref, pol, az, R, name) => {
    const d = M.mulv(X, K.onCone(k, ref, pol, az)), t = V.unit(V.cross(M.mulv(X, k), d));
    return { kind: 'carriage', role: 'active', name, c: V.scale(d, R + 2), x: t, z: d, size: P.car };
  };

  K.register({
    id: 'sliding-rivet-pauldron',
    name: 'Sliding-rivet pauldron (hubless nested plates)',
    dof: { active: 3, passive: 0 },
    params: P,
    q0: ctx => C.solve(ctx),
    qNames: ['J1 (cap slots)', 'J2 (band slots)', 'J3 (arm-end slots)'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => C.solve(ctx),
    residual: (q, ctx) => C.residual(q, ctx),
    check: (q, ctx) => {
      const m = C.margin(ctx);
      if (m < 0) return 'J2 cannot close: the arm axis is out of reach';
      if (m < P.sing) return `J2 within ${m.toFixed(0)} deg of its fold`;
      return null;
    },
    parts: (q, ctx) => {
      const f = C.fk(q, ctx), S = ctx.S, X1 = M.mul(S, f.R1), X2 = M.mul(S, f.R12), XH = M.mul(S, f.E);   // S cap, L1, L2, saddle
      const sz = (R, rho) => 2 * R * Math.sin(rho * K.D2R);
      const harm = ctx.armAxis, ng = P.neck_deg * K.D2R;
      const nk = V.unit(V.add(V.scale(f.p3, Math.cos(ng)), V.scale(V.unit(V.reject(harm, f.p3)), Math.sin(ng))));
      const stubEnd = V.scale(nk, P.RH + 1), cuffC = V.scale(harm, P.cuff_at);
      const azB = -q[1], strapFrom = M.mulv(X2, K.onCone(u2, ref2, P.A1, azW));
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'S cap (2 mm Ti)', c: V.scale(f.p1, P.RS), z: f.p1, x: M.mulv(S, ref1), size: [sz(P.RS, P.rhoS), sz(P.RS, P.rhoS)], t: 2 },
        slot(S, u1, ref1, P.g1[0], P.RS, lim[0], 'fixed-scapula', 'J1 slot (inner)'),
        slot(S, u1, ref1, P.g1[1], P.RS, sh(lim[0], P.fsep1), 'fixed-scapula', 'J1 slot (outer)'),
        { kind: 'plate', role: 'link', name: 'L1 guide disc', c: V.scale(f.p1, R1), z: f.p1, x: M.mulv(X1, ref1), size: [sz(R1, P.rho1) * 0.8, sz(R1, P.rho1) * 0.8], t: 2 },
        fol(X1, u1, ref1, P.g1[0], 0, P.RS, 'J1 follower a'),
        fol(X1, u1, ref1, P.g1[1], P.fsep1, P.RS, 'J1 follower b'),
        slot(X2, u2, ref2, P.A1 - P.band_half, RB, [lim[1][0] - P.D2 / 2 - 4, lim[1][1] + P.D2 / 2 + 4], 'link', 'L2 band edge', 1),
        slot(X2, u2, ref2, P.A1 + P.band_half, RB, [lim[1][0] - P.D2 / 2 - 4, lim[1][1] + P.D2 / 2 + 4], 'link', 'L2 band edge', 1),
        slot(X2, u2, ref2, P.A1 - P.d2, RB, sh(lim[1], -P.D2 / 2), 'link', 'J2 slot (band)'),
        slot(X2, u2, ref2, P.A1 + P.d2, RB, sh(lim[1], P.D2 / 2), 'link', 'J2 slot (band)'),
        fol(X2, u2, ref2, P.A1 - P.d2, azB - P.D2 / 2, RB, 'J2 follower (on L1) a'),
        fol(X2, u2, ref2, P.A1 + P.d2, azB + P.D2 / 2, RB, 'J2 follower (on L1) b'),
        { kind: 'arc', role: 'link', name: 'ramped strap band -> arm-end disc', u: strapFrom, v: f.p3, r0: RB, r1: RA, r: 2.5 },
        { kind: 'plate', role: 'link', name: 'L2 arm-end disc', c: V.scale(f.p3, RA), z: f.p3, x: M.mulv(X2, ref3), size: [sz(RA, 20), sz(RA, 20)], t: 2 },
        slot(X2, u3, ref3, P.g3[0], RA, lim[2], 'link', 'J3 slot (inner)'),
        slot(X2, u3, ref3, P.g3[1], RA, sh(lim[2], P.fsep3), 'link', 'J3 slot (outer)'),
        { kind: 'plate', role: 'fixed-arm', name: 'H saddle (deltoid)', c: V.scale(f.p3, P.RH), z: f.p3, x: M.mulv(XH, ref3), size: [sz(P.RH, P.rho3) * 1.6, sz(P.RH, P.rho3) * 1.6], t: 2 },
        fol(XH, u3, ref3, P.g3[0], 0, P.RH, 'J3 follower (saddle) a'),
        fol(XH, u3, ref3, P.g3[1], P.fsep3, P.RH, 'J3 follower (saddle) b'),
        { kind: 'arc', role: 'fixed-arm', name: 'BOTTOM stub', u: f.p3, v: nk, r0: P.RH + 1, r1: P.RH + 1, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'stub to cuff', a: stubEnd, b: V.madd(cuffC, V.unit(V.reject(stubEnd, harm)), 47), r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
