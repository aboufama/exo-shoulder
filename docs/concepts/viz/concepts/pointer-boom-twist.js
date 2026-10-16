/* pointer-boom-twist - 2R POINTING BOOM at the shoulder + the humeral twist farther down the arm (catalogue
 * pointer-boom-twist, ideated; marked a duplicate of seed-2r-cring): the user's 2026-10-14 suggestion 'put upper arm
 * rotation in its own DOF farther down'. J1 (O20, active) on the top-front of the acromion / lateral clavicle, axis u1 =
 * S-local (lat 46, lon 32), whose line stays >= ~32 deg from every humerus direction -> link 1 (a12 = 90) -> J2 (O20,
 * active), axis u2 = unit(u1 x h) -> link 2 = a BOOM along the lateral arm in the frame (h, u2): it follows the humerus
 * direction but not its axial rotation -> J3 (active) about the humerus axis h: a boom-fixed C-shaped arc rail round the
 * arm (thin-section ring segment, 180 deg, at s 170 mm, radius 53 = arm skin + 6) carrying a short ARM-FIXED carriage
 * (25 deg) on the user's cuff saddle. Azimuth-elevation-roll gimbal, non-redundant: spherical 3R with a1 = a2 = 90 and
 * the last axis = h (KIN.sph3r, closed form, 0 passive). The arc's opening (medial, toward the trunk) is centred on the
 * carriage azimuths of this loop (smallest arc holding 85 % of the closing frames); red = within 10 deg of the boom's
 * singular line or the carriage past an arc end (the spec's main risk: twist travel). Hub levels schematic. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D = K.D2R;
  const lat = 46 * D, lon = 32 * D;
  const P = { u: [Math.cos(lat) * Math.sin(lon), Math.sin(lat), Math.cos(lat) * Math.cos(lon)], a1: 90, a2: 90, sigma: -1, margin: 10,
              s: 170, R: 53, span: 90, cov: 0.85, car_deg: 25, faces: [54, 64], hub_r: 10, stack: 12.25, cuff_at: 175 };
  const dL = [0, -1, 0], latL = [0, 0, 1];
  const C = K.sph3r(V.unit(P.u), dL, P.a1, P.a2, P.sigma), carHalf = P.car_deg / 2;
  const psiOf = (ctx, f) => { const d = f.p3, e1 = f.p2, e2 = V.cross(d, e1), L = M.mulv(ctx.H, latL); return Math.atan2(V.dot(L, e2), V.dot(L, e1)) * K.R2D; };
  let C0 = null;
  function c0() {
    if (C0 != null) return C0;
    const s = [];
    for (const fr of K.motion(120)) { const ctx = K.makeCtx(fr.pose); if (C.margin(ctx) < P.margin) continue; s.push(psiOf(ctx, C.fk(C.solve(ctx), ctx))); }
    s.sort((a, b) => a - b); const n = s.length, m = Math.max(1, Math.ceil(P.cov * n)), s2 = s.concat(s.map(x => x + 360));
    let best = 1e9, c = 0; for (let i = 0; i < n; i++) { const w = s2[i + m - 1] - s2[i]; if (w < best) { best = w; c = s2[i] + w / 2; } }
    return (C0 = K.wrap180(c));
  }

  K.register({
    id: 'pointer-boom-twist',
    name: '2R pointing boom + humeral-twist C-arc on the arm',
    dof: { active: 3, passive: 0 },
    params: P,
    q0: ctx => C.solve(ctx),
    qNames: ['J1 (boom azimuth)', 'J2 (boom elevation)', 'J3 carriage on the C-arc (twist)'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => C.solve(ctx),
    residual: (q, ctx) => C.residual(q, ctx),
    check: (q, ctx) => {
      const m = C.margin(ctx);
      if (m < P.margin) return `humerus within ${m.toFixed(0)} deg of the boom's singular line`;
      const a = K.wrap180(psiOf(ctx, C.fk(q, ctx)) - c0());
      if (Math.abs(a) > P.span - carHalf) return `carriage past the C-arc end (${a.toFixed(0)} deg, arc +-${P.span})`;
      return null;
    },
    parts: (q, ctx) => {
      const f = C.fk(q, ctx), F = P.faces, h = P.stack, d = f.p3, e1 = f.p2, e2 = V.cross(d, e1), o = V.scale(d, P.s);
      const at = a => V.add(V.scale(e1, Math.cos(a * D)), V.scale(e2, Math.sin(a * D)));
      const root = V.madd(o, at(c0()), P.R + 5), L = M.mulv(ctx.H, latL), latA = V.unit(V.reject(L, d));
      const carC = V.madd(o, latA, P.R + 4), tang = V.unit(V.cross(d, latA));
      const boomTop = V.scale(f.p2, F[1] + h + 1), elbowPt = V.madd(V.scale(d, 60), at(c0()), P.R + 14);
      const harm = ctx.armAxis, cuffC = V.scale(harm, P.cuff_at);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base (scapula handler)', c: V.scale(f.p1, F[0] - 3), z: f.p1, x: ctx.attach.scapDir([1, 0, 0]), size: [40, 30], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1 (O20, top-front acromion)', c: V.scale(f.p1, F[0]), axis: f.p1, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 1 (a12 90)', u: f.p1, v: f.p2, r0: F[0] + 7, r1: F[1] + 2, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2 (O20, axis u1 x h)', c: V.scale(f.p2, F[1]), axis: f.p2, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'boom root (over the shoulder)', pts: K.greatArc(f.p2, V.unit(elbowPt), V.norm(boomTop), V.norm(elbowPt)), r: 2.6 },
        { kind: 'link', role: 'link', name: 'boom down the arm (no twist)', a: elbowPt, b: root, r: 2.6 },
        { kind: 'rail', role: 'link', name: 'C-arc rail on the boom (180 deg, open toward the trunk)', c: o, axis: d, ref: e1, rho: P.R + 4, a0: c0() - P.span, a1: c0() + P.span, r: 2.6 },
        { kind: 'carriage', role: 'active', name: 'J3 arm-fixed carriage (25 deg, on the cuff saddle)', c: carC, x: tang, z: latA, size: [P.car_deg * D * (P.R + 4), 12, 6] },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff (carries the carriage)', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
