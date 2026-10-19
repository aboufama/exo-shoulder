/* rail-elbow - a spherical 3R whose middle joint J2 is a curved RAIL on link 1: link 2 shrinks to a carriage beside
 * the arm-end hub (docs/concepts/rail-elbow.md, models/rail-elbow.py). Best sweep entry (sweeps/rail-elbow.json k172,
 * gap 63.72): 2-stage telescopic rail (tele 1) laid out at 105 mm, d_off -41.4 deg. Kinematics = the 3R closure of b
 * and W on branch -1 (closed form); the carriage azimuth psi about p2 is the J2 value, the rail spans the carriage
 * travel psi_c + [psi_lo, psi_hi] + half a carriage + end stops + the 12 mm tab strap 1 holds. Stage 2 rides beside
 * stage 1 at half the carriage travel (2:1 cable loop, a determined coordinate, not a DOF). Hub faces are schematic
 * (53 / 72 mm, the champion's): the model fits them per design. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V;
  const P = { az: -13.1067, el: 83.7924, a1: 76.8422, a2: 64.0444, wd: 93.2486, wa: 17.2112, sigma: -1, margin: 10,
              d_off: -41.4333, tele: 1, r_lay: 105.0, psi_c: -84.176, psi_lo: -68.961, psi_hi: 64.567,
              faces: [53, 72], hub_r: 10, stack: 12.25, car: [20, 16, 9], rail_w: 8, end_stop: 3, tab: 12, neck_deg: 25, cuff_at: 165 };
  const C = K.sph3r(K.bvec(P.az, P.el), K.wdir(P.wd, P.wa), P.a1, P.a2, P.sigma);
  const R2D = K.R2D, RL = P.r_lay;
  // rail layout (models/rail-elbow.py rail_layout + the tele branch of build), all in degrees about p2
  const alpha = P.a2 + P.d_off, rr = RL * Math.sin(alpha * K.D2R);
  const eStop = (P.car[0] / 2 + P.end_stop) / rr * R2D, eTab = eStop + P.tab / rr * R2D;
  const lo = P.psi_c + P.psi_lo, hi = P.psi_c + P.psi_hi, Tt = hi - lo;
  const rb = K.wrap180(-P.psi_c), tabLo = Math.abs(K.wrap180(rb - P.psi_lo)) <= Math.abs(K.wrap180(rb - P.psi_hi));
  const sTab = tabLo ? lo - eTab : hi + eTab, g = tabLo ? 1 : -1;          // g: direction from the anchor along the rail
  const sg = P.d_off >= 0 ? 1 : -1, hh = -sg, dW = (P.rail_w / 2) / RL * R2D;
  const o1 = alpha - hh * dW, o2 = alpha + hh * dW;                          // stage 1 / stage 2 polar angles about p2
  const carW = P.rail_w / 2 + 4, oBr = o2 - sg * carW / RL * R2D;            // bridge leaves the carriage's hub side

  function frame(q, ctx) {
    const f = C.fk(q, ctx), ref = V.unit(V.reject(f.p1, f.p2));
    const psi = K.axisAngle(f.p2, ref, f.p3);                                // J2 value: carriage azimuth about p2
    return Object.assign(f, { ref, psi });
  }
  const rail = (f, pol, a0, a1, role, name) => ({ kind: 'rail', role, name, c: V.scale(f.p2, RL * Math.cos(pol * K.D2R)),
    axis: f.p2, ref: f.ref, rho: RL * Math.sin(pol * K.D2R), a0, a1, r: 2.6 });

  K.register({
    id: 'rail-elbow',
    name: 'Rail elbow',
    dof: { active: 3, passive: 0 },
    params: P,
    q0: ctx => C.solve(ctx),
    qNames: ['J1', 'J2 (carriage)', 'J3'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => C.solve(ctx),
    residual: (q, ctx) => C.residual(q, ctx),
    check: (q, ctx) => {
      const m = C.margin(ctx); if (m < 0) return 'J2 cannot close: the arm axis is out of reach';
      if (m < P.margin) return `J2 within ${m.toFixed(0)} deg of its fold`;
      const rel = K.wrap180(frame(q, ctx).psi - P.psi_c);
      if (rel < P.psi_lo || rel > P.psi_hi) return 'carriage past the end of the rail';
      return null;
    },
    parts: (q, ctx) => {
      const f = frame(q, ctx), F = P.faces, h = P.stack;
      const rel = K.wrap180(f.psi - P.psi_c), xcar = Math.max(0, Math.min(Tt, g < 0 ? P.psi_hi - rel : rel - P.psi_lo));
      const s1a = sTab, s1b = sTab + g * (eTab + Tt / 2 + eStop);
      const s2a = sTab + g * (eTab - eStop + xcar / 2), s2b = s2a + g * (Tt / 2 + 2 * eStop);
      const xTab = V.scale(K.onCone(f.p2, f.ref, o1, sTab), RL);
      const cd = K.onCone(f.p2, f.ref, o2, f.psi), carC = V.scale(cd, RL + P.car[2] / 2);
      const tang = V.unit(V.sub(K.onCone(f.p2, f.ref, o2, f.psi + 1), K.onCone(f.p2, f.ref, o2, f.psi - 1)));
      const bFrom = K.onCone(f.p2, f.ref, oBr, f.psi);
      const harm = ctx.armAxis, ng = P.neck_deg * K.D2R;
      const nk = V.unit(V.add(V.scale(f.p3, Math.cos(ng)), V.scale(V.unit(V.reject(harm, f.p3)), Math.sin(ng))));
      const neckEnd = V.scale(nk, F[1] + 1), cuffC = V.scale(harm, P.cuff_at);
      const cuffTop = V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47);
      return [
        { kind: 'plate', role: 'fixed-scapula', c: V.scale(f.p1, F[0] - 3), z: f.p1, x: ctx.attach.scapDir([1, 0, 0]), size: [46, 32], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1', c: V.scale(f.p1, F[0]), axis: f.p1, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'strap 1', u: f.p1, v: xTab, r0: F[0] + 7, r1: RL, r: 2.5 },
        rail(f, o1, s1a, s1b, 'link', 'rail stage 1 (on link 1)'),
        rail(f, o2, s2a, s2b, 'link', 'rail stage 2 (2:1 cable)'),
        { kind: 'carriage', role: 'active', name: 'J2 carriage', c: carC, x: tang, z: cd, size: P.car },
        { kind: 'arc', role: 'link', name: 'bridge (link 2)', u: bFrom, v: f.p3, r0: RL + P.car[2], r1: F[1] + h + 1, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3', c: V.scale(f.p3, F[1]), axis: f.p3, r: P.hub_r, h },
        { kind: 'arc', role: 'fixed-arm', name: 'neck', u: f.p3, v: nk, r0: F[1] + 1, r1: F[1] + 1, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'neck to cuff', a: neckEnd, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
