/* j2-arc-sector-3r - spherical 3R whose J2 has NO hub: link 1 carries a conical V-edge ARC-RAIL SECTOR revolved about
 * the virtual J2 axis p2, and link 2 rides it on a 4-roller carriage (docs/concepts/j2-arc-sector-3r.md,
 * models/j2-arc-sector-3r.py). DEAD (the rail loses 13.4 gap points to its own hub control at identical axes); drawn at
 * its best honest configuration, the audit's beta-floor entry (sweeps k295, gap 66.30 = row v_gap): bvec(23.364,
 * 61.992), a1 84.946 / a2 63.037, wdir(98.3, -8.14), sigma -1, rail cone half-angle beta 12 about p2, carriage at chi
 * 43.268 from p3's azimuth, tab on side s1 +1, rail laid out at r_lay 151 mm (fitted level 152.1 mm from GH).
 * Rail travel: k295's own travel (cov 0.99) was not logged; the rail is drawn at the travel logged for these axes at cov
 * 0.961 (k121 / k284: pc -46.944, pw 55.796 about p2 from p1's azimuth), so its span is a few deg short of k295's and a
 * carriage past an end stop shows red. Model rule (rail_extent): the sector = travel + half a carriage (16 mm) + a 3 mm
 * stop each side + the 8 mm tab where link 1 laps on. Carriage = 20 x 16 plate 4.6 mm over the rail underside (8.6 in
 * all). Hub faces J1 / J3 are schematic (53 / 72 mm): the audit entry did not log them. Every axis passes through GH;
 * 3 ACTIVE (J1 hub, J2 = carriage on the rail, J3 hub), 0 passive. Closed form (KIN.sph3r). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, D2R = K.D2R, R2D = K.R2D;
  const P = { az: 23.364, el: 61.992, a1: 84.946, a2: 63.037, wd: 98.3, wa: -8.14, sigma: -1, margin: 10, beta: 12.0,
              chi: 43.268, cov: 0.99, pc: -46.944, pw: 55.796, s1: 1, r_lay: 151.0, rail: [8, 4], car: [16, 20], plate_dz: 4.6,
              plate_t: 4, stop: 3, tab: 8, faces: [53, 72], hub_r: 10, stack: 12.25, neck_deg: 25, cuff_at: 165 };
  const C = K.sph3r(K.bvec(P.az, P.el), K.wdir(P.wd, P.wa), P.a1, P.a2, P.sigma);
  const RL = P.r_lay, rc = RL * Math.sin(P.beta * D2R);
  // rail_extent(): [lo, hi] deg about p2 from p1's azimuth, tab centre tc
  const ext = (P.car[0] / 2 + P.stop) / rc * R2D, tabd = P.tab / rc * R2D;
  let lo = P.pc - P.pw - ext, hi = P.pc + P.pw + ext, tc;
  if (P.s1 < 0) { lo -= tabd; tc = lo + tabd / 2; } else { hi += tabd; tc = hi - tabd / 2; }

  function frame(q, ctx) {
    const f = C.fk(q, ctx), e1 = V.unit(V.reject(f.p1, f.p2));
    const th2 = K.axisAngle(f.p2, f.p1, f.p3), psi = K.wrap180(th2 + P.chi);      // carriage azimuth = J2's value
    return Object.assign(f, { e1, th2, psi });
  }
  const cone = (f, pol, az) => K.onCone(f.p2, f.e1, pol, az);

  K.register({
    id: 'j2-arc-sector-3r',
    name: 'J2 arc-rail sector + roller carriage (3R)',
    dof: { active: 3, passive: 0 },
    params: P,
    q0: ctx => C.solve(ctx),
    qNames: ['J1', 'J2 (carriage on the arc rail)', 'J3'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    // closed form; overhead -> abduction the arm leaves the chain's reach (stretched J2 fold, the arm axis near the
    // antipode of p1): J1 / J3 whip ~70 deg per frame there - the nearest configuration by least squares whips the same
    // way, so it is the chain's own singularity, drawn red, not an IK branch flip (thumbs --stats: no flips)
    solve: ctx => C.solve(ctx),
    residual: (q, ctx) => C.residual(q, ctx),
    check: (q, ctx) => {
      const m = C.margin(ctx); if (m < 0) return 'J2 cannot close: the arm axis is out of reach';
      if (m < P.margin) return `J2 within ${m.toFixed(0)} deg of its fold`;
      if (Math.abs(K.wrap180(frame(q, ctx).psi - P.pc)) > P.pw) return 'carriage on a rail end stop (J2 travel exhausted)';
      return null;
    },
    parts: (q, ctx) => {
      const f = frame(q, ctx), F = P.faces, h = P.stack;
      // the carriage is drawn on the rail even past the stops (clamped to the travel) - the indicator turns red there
      const psiC = P.pc + Math.max(-P.pw, Math.min(P.pw, K.wrap180(f.psi - P.pc)));
      const uCar = cone(f, P.beta, psiC), uTab = cone(f, P.beta, tc);
      const tang = V.unit(V.sub(cone(f, P.beta, psiC + 1), cone(f, P.beta, psiC - 1)));
      const carT = P.plate_dz + P.plate_t, carC = V.scale(uCar, RL + carT / 2);
      const harm = ctx.armAxis, ng = P.neck_deg * D2R;
      const nk = V.unit(V.add(V.scale(f.p3, Math.cos(ng)), V.scale(V.unit(V.reject(harm, f.p3)), Math.sin(ng))));
      const neckEnd = V.scale(nk, F[1] + 1), cuffC = V.scale(harm, P.cuff_at);
      const cuffTop = V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base (scapula handler)', c: V.scale(f.p1, F[0] - 3), z: f.p1, x: ctx.attach.scapDir([1, 0, 0]), size: [46, 32], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1 (O20 hub)', c: V.scale(f.p1, F[0]), axis: f.p1, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 1 (strap to the rail tab)', u: f.p1, v: uTab, r0: F[0] + h + 1, r1: RL + P.rail[1] + 1.1, r: 2.5 },
        { kind: 'rail', role: 'link', name: 'J2 arc-rail sector (rigid with link 1, revolved about p2)', c: V.scale(f.p2, RL * Math.cos(P.beta * D2R)),
          axis: f.p2, ref: f.e1, rho: rc, a0: lo, a1: hi, r: 3 },
        { kind: 'carriage', role: 'active', name: 'J2 roller carriage (4 V-rollers, link 2 bolted on)', c: carC, x: tang, z: uCar, size: [P.car[0], P.car[1], carT] },
        { kind: 'link', role: 'link', name: 'J2 virtual axis (construction line)', a: V.scale(f.p2, 30), b: V.scale(f.p2, RL), r: 0.5 },
        { kind: 'arc', role: 'link', name: 'link 2 (carriage to J3)', u: uCar, v: f.p3, r0: RL + carT + 0.6, r1: F[1] + h + 1, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3 (O20 hub)', c: V.scale(f.p3, F[1]), axis: f.p3, r: P.hub_r, h },
        { kind: 'arc', role: 'fixed-arm', name: 'neck', u: f.p3, v: nk, r0: F[1] + 1, r1: F[1] + 1, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'neck to cuff', a: neckEnd, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
