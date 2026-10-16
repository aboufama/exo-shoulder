/* pointing-gimbal-humeral-crail - the user's split (catalogue pointing-gimbal-humeral-crail, ideated; marked a duplicate
 * of seed-2r-cring): a 2R POINTING GIMBAL whose singular line sits where the humerus never goes, plus humeral rotation
 * on a C-RAIL on the deltoid sphere. J1 (O20, active) on the anterior-superior-lateral acromion, axis u_S = (0.37, 0.74,
 * 0.56) in the scapula frame (the line the humerus stays >= 32 deg from) -> link 1 (90 deg arc) -> J2 (O20, active),
 * axis v = u x d, perpendicular to J1 and to the humerus axis d -> link 2 = a YOKE that points along the humerus but does
 * not twist with it, carrying a C-rail: the latitude circle about d on the sphere round GH at 60 deg from the distal
 * humerus axis, radius 62 mm (centre 31 mm down d, rho 53.7), 200 deg long, open on the medial (axilla) side -> J3
 * (active) = an ARM-FIXED carriage on the cuff / BOTTOM top block at the lateral deltoid running on that rail.
 * Kinematically a spherical 3R with a1 = a2 = 90 and the last axis = d (KIN.sph3r, closed form, 0 passive). The rail's
 * opening is centred on the carriage azimuths of this loop (smallest arc holding 90 % of the closing frames); red = the
 * gimbal within 10 deg of its singular line, or the carriage past a rail end. Hub levels schematic. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const P = { u: [0.37, 0.74, 0.56], a1: 90, a2: 90, sigma: -1, margin: 10, phi: 60, R: 62, span: 100, cov: 0.9,
              car: [22, 12, 7], faces: [52, 62], hub_r: 10, stack: 12.25, cuff_at: 165 };
  const dL = [0, -1, 0], latL = [0, 0, 1];
  const C = K.sph3r(V.unit(P.u), dL, P.a1, P.a2, P.sigma);
  const sc = P.R * Math.cos(P.phi * K.D2R), rho = P.R * Math.sin(P.phi * K.D2R), carHalf = (P.car[0] / 2 + 3) / rho * K.R2D;
  /** carriage azimuth in the yoke frame (e1 = J2 axis, e2 = d x e1), deg */
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
    id: 'pointing-gimbal-humeral-crail',
    name: '2R pointing gimbal + humeral C-rail on the deltoid sphere',
    dof: { active: 3, passive: 0 },
    params: P,
    q0: ctx => C.solve(ctx),
    qNames: ['J1 (gimbal azimuth)', 'J2 (gimbal tilt)', 'J3 carriage on the C-rail (twist)'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => C.solve(ctx),
    residual: (q, ctx) => C.residual(q, ctx),
    check: (q, ctx) => {
      const m = C.margin(ctx);
      if (m < P.margin) return `humerus within ${m.toFixed(0)} deg of the gimbal's singular line`;
      const a = K.wrap180(psiOf(ctx, C.fk(q, ctx)) - c0());
      if (Math.abs(a) > P.span - carHalf) return `carriage past the C-rail end (${a.toFixed(0)} deg, rail +-${P.span})`;
      return null;
    },
    parts: (q, ctx) => {
      const f = C.fk(q, ctx), F = P.faces, h = P.stack, d = f.p3, e1 = f.p2, e2 = V.cross(d, e1), o = V.scale(d, sc);
      const at = a => V.add(V.scale(e1, Math.cos(a * K.D2R)), V.scale(e2, Math.sin(a * K.D2R)));
      const mid = V.madd(o, at(c0()), rho + 4), L = M.mulv(ctx.H, latL), lat = V.unit(V.reject(L, d));
      const carC = V.madd(o, lat, rho + 4), tang = V.unit(V.cross(d, lat));
      const harm = ctx.armAxis, cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, lat, 47);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base (scapula handler)', c: V.scale(f.p1, F[0] - 3), z: f.p1, x: ctx.attach.scapDir([1, 0, 0]), size: [40, 30], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1 (O20, singular line where the arm never goes)', c: V.scale(f.p1, F[0]), axis: f.p1, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 1 (90 deg arc)', u: f.p1, v: f.p2, r0: F[0] + 7, r1: F[1] + 2, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2 (O20, axis u x d)', c: V.scale(f.p2, F[1]), axis: f.p2, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 2: yoke over the deltoid cap (no twist)', pts: K.greatArc(f.p2, V.unit(mid), F[1] + h + 1, V.norm(mid)), r: 2.5 },
        { kind: 'rail', role: 'link', name: 'C-rail on the yoke (latitude circle about d, open medially)', c: o, axis: d, ref: e1, rho: rho + 4, a0: c0() - P.span, a1: c0() + P.span, r: 2.6 },
        { kind: 'carriage', role: 'active', name: 'J3 arm-fixed carriage (lateral deltoid)', c: carC, x: tang, z: lat, size: P.car },
        { kind: 'link', role: 'fixed-arm', name: 'carriage block to the cuff / BOTTOM', a: V.madd(carC, lat, P.car[2] / 2), b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
