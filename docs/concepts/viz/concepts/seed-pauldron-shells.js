/* seed-pauldron-shells - nested sliding shells (a pauldron): no hub at any axis, every revolute is a large sliding pair
 * concentric with GH = a T-slot channel (7 mm stack, 12 wide) on a band at colatitude g about its axis, spread over the
 * arc its slider travels (docs/concepts/seed-pauldron-shells.md, models/seed-pauldron-shells.py; DEAD, best honest k88,
 * gap 79.46). Spherical 3R on axes p1 = bvec(2.84, 86.1) (scapula), p2 (two-cone closure: a1 83.0, a2 64.2, branch -1),
 * p3 = wdir(83.9, 13.9) (humerus). Tracks on the DISTAL bodies (side1 = side2 = 1): track 1 rides shell 1 round p1
 * (g1 16, R 58, 334 deg) with the scapula's slider in it; track 2 rides shell 2 round p2 (g2 14, ~120 mm: it clears the
 * deltoid / acromion over a 253 deg sweep, the measured limiter) with shell 1's slider in it; the C-ring (6 x 8) is on
 * the humerus round p3 (gamma 16, 239 deg, cov 0.9) with shell 2's carriage on it. Web 1 (shell 1) runs from track 1 to
 * shell 1's slider, lifted over track 2; web 2 (shell 2) from track 2 to the carriage. The neck leaves the ring in the
 * middle of the C's gap to the cuff, which holds the ring on a PASSIVE slide along the humerus (set by the GH
 * translation, 0 on this rig). Track windows = the bench arcs centred on this loop's slider range (+ the weld at 0).
 * Ring radius 74 is schematic. 3 active + 1 passive; closed form (KIN.sph3r). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = K.D2R;
  const P = { az: 2.841, el: 86.115, a1: 83.025, a2: 64.198, sigma: -1, margin: 10, wd: 83.944, wa: 13.919,
              g: [16, 14, 16], R: [58, 120, 74], arcs: [334, 253, 239], band_w: 12, slider: [30, 12, 4], car: [25, 12, 6],
              slide: 30, cuff_at: 165 };
  const b0 = K.bvec(P.az, P.el), r0 = V.unit(Math.abs(b0[1]) < 0.95 ? V.cross(b0, [0, 1, 0]) : V.cross(b0, [1, 0, 0]));
  const C = K.sph3r(b0, K.wdir(P.wd, P.wa), P.a1, P.a2, P.sigma), hlL = K.wdir(90, 0);
  /** axes + moving-element azimuths in each track's frame (track on the distal body: ref = toward the next axis) */
  function frame(q, ctx) {
    const f = C.fk(q, ctx), base = M.mulv(ctx.S, r0), hl = M.mulv(ctx.H, hlL);
    const T = [[f.p1, f.p2, base], [f.p2, f.p3, f.p1], [f.p3, hl, f.p2]];     // [axis, track ref (az 0), moving element]
    return Object.assign(f, { T, az: T.map(([k, ref, m]) => K.axisAngle(k, ref, m)) });
  }
  let WIN = null;
  function win() {                                         // window centre per track: middle of the loop range (and the weld at 0)
    if (WIN) return WIN;
    const A = [[0], [0], []];
    for (const fr of K.motion(120)) { const ctx = K.makeCtx(fr.pose); if (C.margin(ctx) < P.margin) continue;
      frame(C.solve(ctx), ctx).az.forEach((a, j) => A[j].push(a)); }
    return (WIN = A.map(a => { const r = a[a.length - 1], rel = a.map(x => K.wrap180(x - r)); return K.wrap180(r + 0.5 * (Math.max(...rel) + Math.min(...rel))); }));
  }
  const half = j => (j < 2 ? P.slider[0] : P.car[0]) / 2 / (P.R[j] * Math.sin(P.g[j] * D2R)) * K.R2D;
  const onBand = (k, ref, j, az, dz) => {                  // point on band j at azimuth az (deg), dz mm over the band
    const a = K.onCone(k, ref, P.g[j], az); return V.scale(a, P.R[j] + dz);
  };

  K.register({
    id: 'seed-pauldron-shells',
    name: 'Nested sliding shells (pauldron) + arm ring',
    dof: { active: 3, passive: 1 },
    params: P,
    q0: ctx => C.solve(ctx).concat([0]),
    qNames: ['J1 (shell 1 on track 1)', 'J2 (shell 2 on track 2)', 'J3 (carriage on the arm ring)', 'cuff slide (passive)'],
    qUnits: ['deg', 'deg', 'deg', 'mm'], resUnits: ['deg', 'deg', 'deg', 'mm'],
    solve: ctx => C.solve(ctx).concat([0]),
    residual: (q, ctx) => C.residual(q, ctx).concat([q[3]]),   // all axes through GH: the slide = GH translation (0 here)
    check: (q, ctx) => {
      const m = C.margin(ctx);
      if (m < 0) return 'J2 cannot close: the arm is out of the chain\'s reach';
      if (m < P.margin) return `J2 within ${m.toFixed(0)} deg of its fold`;
      const f = frame(q, ctx), w = win(), nm = ['the base slider leaves track 1', 'shell 1\'s slider leaves track 2', 'carriage in the arm ring\'s gap'];
      for (let j = 0; j < 3; j++) if (Math.abs(K.wrap180(f.az[j] - w[j])) > P.arcs[j] / 2 - half(j)) return nm[j];
      return null;
    },
    parts: (q, ctx) => {
      const f = frame(q, ctx), w = win(), R = P.R, g = P.g, T = f.T;
      const track = (j, role, name) => { const [k, ref] = T[j]; return { kind: 'rail', role, name, c: V.scale(k, R[j] * Math.cos(g[j] * D2R)), axis: k, ref,
        rho: R[j] * Math.sin(g[j] * D2R), a0: w[j] - P.arcs[j] / 2, a1: w[j] + P.arcs[j] / 2, r: 3.5 }; };
      const elem = (j, name, size, dz) => { const [k, ref] = T[j], d = K.onCone(k, ref, g[j], f.az[j]);
        return { kind: 'carriage', role: 'active', name, c: V.scale(d, R[j] + dz), x: V.unit(V.cross(k, d)), z: d, size }; };
      const w1a = onBand(T[0][0], T[0][1], 0, 0, 2), w1b = onBand(T[1][0], T[1][1], 1, f.az[1], 8);
      const w2a = onBand(T[1][0], T[1][1], 1, 0, 2), w2b = onBand(T[2][0], T[2][1], 2, f.az[2], 9);
      const harm = ctx.armAxis, nk = onBand(T[2][0], T[2][1], 2, w[2] + 180, 3), lat = V.unit(V.reject(nk, harm));
      const s0 = V.madd(V.scale(harm, P.cuff_at - P.slide - 12), lat, 52), s1 = V.madd(V.scale(harm, P.cuff_at - 12), lat, 50);
      const stud = onBand(T[0][0], T[0][1], 0, f.az[0], -6);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base (scapula handler)', c: V.scale(f.p1, R[0] - 12), z: f.p1, x: ctx.attach.scapDir([1, 0, 0]), size: [36, 30], t: 3 },
        { kind: 'link', role: 'fixed-scapula', name: 'base stud to its slider', a: V.scale(f.p1, R[0] - 10), b: stud, r: 2.5 },
        track(0, 'link', 'track 1 (channel on shell 1, round p1)'),
        elem(0, 'J1 slider (scapula, inside track 1)', P.slider, 1),
        { kind: 'arc', role: 'link', name: 'web 1 (shell 1)', pts: K.greatArc(w1a, w1b, V.norm(w1a), V.norm(w1b)), r: 3 },
        track(1, 'link', 'track 2 (channel on shell 2, round p2)'),
        elem(1, 'J2 slider (shell 1, inside track 2)', P.slider, 1),
        { kind: 'arc', role: 'link', name: 'web 2 (shell 2)', pts: K.greatArc(w2a, w2b, V.norm(w2a), V.norm(w2b)), r: 3 },
        track(2, 'fixed-arm', 'arm C-ring (round p3)'),
        elem(2, 'J3 carriage (shell 2)', P.car, 4.5),
        { kind: 'link', role: 'fixed-arm', name: 'neck (from the C\'s gap)', a: nk, b: s0, r: 3 },
        { kind: 'slider', role: 'passive', name: 'cuff slide along the humerus (passive)', a: s0, b: s1, at: V.madd(V.lerp(s0, s1, 0.5), harm, q[3]), z: lat, size: [14, 10, 5] },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: V.scale(harm, P.cuff_at), axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
