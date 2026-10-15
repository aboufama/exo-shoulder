/* offset-arc-selfalign - the trombone with its curvature freed: S -> J1 thin-section RING about a line parallel to b
 * (offset o1) -> L1 = a GUIDE box -> J2 = an L2-fixed BAND bent to a circle about a line parallel to p2 (offset o2 from
 * GH, NOT a GH sphere) that SLIDES THROUGH the guide -> L2 = band + connector strap -> J3 O20 hub about a line parallel to
 * W (offset o3) -> hub lower plate on a PASSIVE 3-slide self-aligning cuff stage (along the humerus / around it /
 * normal) -> arm (docs/concepts/offset-arc-selfalign.md, models/offset-arc-selfalign.py; status dead, best k38 gap
 * 133.12). Orientations compose independently of where the axes sit, so q1..q3 are the spherical closure of b and W
 * (branch -1); the offsets only translate the chain end by t_E = (I - R1) o1 + R1 (I - R2) o2 + R12 (I - R3) o3, and the
 * three slides take it up: 3 active + 3 passive, all fixed by closure (closed form; residual = orientation + slide
 * translation). Best entry: champion trombone axes, o2 = -6 mm toward -W's azimuth, arc shifted 6 mm along the J2 line,
 * J1 / J3 offsets from the minimax LP, stage +-25 / +-10 / +-5 mm. Fitted geometry (k38): ring underside 55 mm along b,
 * band radius 114 mm from the J2 line (the GH sphere would be ~57: the tail past the guide cannot clear the neck
 * overhead at any lower radius - the measured reason it is dead), band spans 22-126 deg from W about p2, guide >= 12 deg
 * inside both ends, hub at 87.9 mm along W, stage rail 70 mm along its normal. Slides centred on this loop. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = K.D2R, R2D = K.R2D;
  const P = { az: 32.55, el: 80.56, wd: 71.38, wa: 4.78, A1: 77.41, A2: 81.45, branch: -1, o1m: -0.12, o1t: -0.16, o2w: -6, o2n: 0,
              o3a: 1.16, o3t: -0.64, dza: 6, S_a: 25, S_t: 10, R_r: 5, z1: 55, rho: 114.4, arc: [22.2, 126.2], gmarg: 12, sing: 5,
              lam: 70.3, f3: 87.9, ring: [19, 26, 6], guide: [30, 22, 10], band: [10, 4], hub_r: 10, stack: 12.25, cuff_at: 165 };
  const C = K.sph3r(K.bvec(P.az, P.el), K.wdir(P.wd, P.wa), P.A1, P.A2, P.branch);
  const b = C.u1, p2 = C.u2, W = C.u3, hum = [0, -1, 0];                       // reference = home (arm at H = S)
  const m1 = V.unit(V.reject(p2, b)), t1 = V.cross(b, m1), e2 = V.unit(V.reject(W, p2)), e3 = V.cross(p2, e2);
  const al3 = V.unit(V.reject(hum, W)), tg3 = V.cross(W, al3);
  const o1 = V.add(V.scale(m1, P.o1m), V.scale(t1, P.o1t)), o2 = V.add(V.scale(e2, P.o2w), V.scale(e3, P.o2n));
  const o3 = V.add(V.scale(al3, P.o3a), V.scale(tg3, P.o3t));
  const sn = V.unit(V.reject(W, hum)), sa = hum, st = V.cross(sn, sa);           // stage axes (frame 'arm')
  const za = 58 * Math.cos(P.A1 * D2R) + P.dza;                                  // band circle centre along the J2 line
  const g0 = V.sub(V.add(o1, V.scale(b, 58)), o2), phiG = Math.atan2(V.dot(g0, e3), V.dot(g0, e2)) * R2D;
  const uAt = ph => V.add(V.scale(e2, Math.cos(ph * D2R)), V.scale(e3, Math.sin(ph * D2R)));

  function fk(q) {                                   // member transforms [R, t] in the scapula frame (p -> R p + t)
    const R1 = M.rot(b, q[0]), R12 = M.mul(R1, M.rot(p2, q[1])), R123 = M.mul(R12, M.rot(W, q[2]));
    const t1_ = V.sub(o1, M.mulv(R1, o1)), t2_ = V.add(t1_, M.mulv(R1, V.sub(o2, M.mulv(M.rot(p2, q[1]), o2))));
    const tE = V.add(t2_, M.mulv(R12, V.sub(o3, M.mulv(M.rot(W, q[2]), o3))));
    return { X1: [R1, t1_], X2: [R12, t2_], X3: [R123, tE] };
  }
  const ap = (X, p) => V.add(M.mulv(X[0], p), X[1]);
  const sRaw = (ctx, q) => { const Q = M.mul(M.T(ctx.S), ctx.H), d = M.mulv(M.T(Q), fk(q).X3[1]); return [V.dot(d, sa), V.dot(d, st), V.dot(d, sn)]; };
  let CEN = null;                                    // slide centring: mid-range over this loop's closing frames
  function centre() {
    if (CEN) return CEN;
    const S = K.motion(120).map(f => { const ctx = K.makeCtx(f.pose); return C.margin(ctx) >= 0 ? sRaw(ctx, C.solve(ctx)) : null; }).filter(Boolean);
    return (CEN = [0, 1, 2].map(i => 0.5 * (Math.max(...S.map(s => s[i])) + Math.min(...S.map(s => s[i])))));
  }
  function solve(ctx) { const q = C.solve(ctx), s = sRaw(ctx, q), c = centre(); return q.concat([s[0] - c[0], s[1] - c[1], s[2] - c[2]]); }

  K.register({
    id: 'offset-arc-selfalign',
    name: 'Offset arc + self-aligning cuff (non-spherical trombone)',
    dof: { active: 3, passive: 3 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1 ring', 'J2 band through the guide', 'J3 hub', 'slide along', 'slide around', 'slide normal'],
    qUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'], resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve,
    residual: (q, ctx) => {
      const X = fk(q).X3, Q = M.mul(M.T(ctx.S), ctx.H), c = centre();
      const sv = V.add(V.add(V.scale(sa, q[3] + c[0]), V.scale(st, q[4] + c[1])), V.scale(sn, q[5] + c[2]));
      return M.rotErrDeg(X[0], Q).concat(V.sub(X[1], M.mulv(Q, sv)));
    },
    check: (q, ctx) => {
      const sep = V.angle(M.mulv(ctx.S, b), M.mulv(ctx.H, W));
      if (sep < Math.abs(P.A1 - P.A2) + P.sing || sep > P.A1 + P.A2 - P.sing) return 'closure fold: angle(b, W) outside the band';
      const pg = phiG - q[1];
      if (pg < P.arc[0] + P.gmarg || pg > P.arc[1] - P.gmarg) return 'guide off the end of the band';
      const lim = [P.S_a, P.S_t, P.R_r], nm = ['along', 'around', 'normal'];
      for (let i = 0; i < 3; i++) if (Math.abs(q[3 + i]) > lim[i]) return `slide ${nm[i]} past its stop (${q[3 + i].toFixed(1)} mm)`;
      return null;
    },
    parts: (q, ctx) => {
      const S = ctx.S, Wp = p => M.mulv(S, p), Wd = d => M.mulv(S, d), { X1, X2, X3 } = fk(q);
      const Q = M.mul(M.T(S), ctx.H), arm = p => Wp(M.mulv(Q, p)), c = centre(), h = P.stack;
      const uG = uAt(phiG), tG = uAt(phiG + 90), gc = V.add(V.add(o2, V.scale(p2, za)), V.scale(uG, P.rho + P.guide[2] / 2 - 3));
      const ringTop = V.add(o1, V.scale(b, P.z1 + P.ring[2]));
      const bandEnd = V.add(V.add(o2, V.scale(p2, za)), V.scale(uAt(P.arc[0]), P.rho + P.band[1] / 2));
      const P3 = V.add(o3, V.scale(W, P.f3)), vp = V.unit(V.reject(V.sub(bandEnd, P3), W));
      // stage (arm side, reference coords): footprint centre Os, rail level lam along sn
      const Os = V.add(V.add(V.reject(P3, sn), V.scale(sa, c[0])), V.scale(st, c[1]));
      const lv = z => V.add(Os, V.scale(sn, z)), sA = V.scale(sa, q[3]), sT = V.scale(st, q[4]);
      const zA = P.lam + 3.5, zC = zA + 3;
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base', c: Wp(V.add(o1, V.scale(b, P.z1 - 2))), z: Wd(b), x: Wd([1, 0, 0]), size: [58, 58], t: 2 },
        { kind: 'ring', role: 'active', name: 'J1 thin-section ring (offset line)', c: Wp(V.add(o1, V.scale(b, P.z1 + P.ring[2] / 2))), axis: Wd(b), r: (P.ring[0] + P.ring[1]) / 2, w: P.ring[1] - P.ring[0], t: P.ring[2] },
        { kind: 'link', role: 'link', name: 'L1 post (ring upper race to the guide)', a: Wp(ap(X1, V.add(ringTop, V.scale(m1, P.ring[1] - 4)))), b: Wp(ap(X1, V.sub(gc, V.scale(uG, P.guide[2] / 2)))), r: 3.5 },
        { kind: 'carriage', role: 'active', name: 'J2 guide (L1): the band slides through it', c: Wp(ap(X1, gc)), x: Wd(M.mulv(X1[0], tG)), z: Wd(M.mulv(X1[0], uG)), size: P.guide },
        { kind: 'rail', role: 'link', name: 'band (L2): circle about the offset J2 line', c: Wp(ap(X2, V.add(o2, V.scale(p2, za)))), axis: Wd(M.mulv(X2[0], p2)),
          ref: Wd(M.mulv(X2[0], e2)), rho: P.rho + P.band[1] / 2, a0: P.arc[0], a1: P.arc[1], r: 2.5, w: P.band[0] },
        { kind: 'link', role: 'link', name: 'connector (band end to J3)', a: Wp(ap(X2, bandEnd)), b: Wp(ap(X2, V.add(V.add(P3, V.scale(W, 3.15)), V.scale(vp, P.hub_r)))), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3 (offset line)', c: Wp(ap(X2, P3)), axis: Wd(M.mulv(X2[0], W)), r: P.hub_r, h },
        { kind: 'plate', role: 'fixed-arm', name: 'stage rail on the arm', c: arm(lv(P.lam + 1.5)), z: arm(sn), x: arm(sa), size: [20 + 2 * P.S_a, 8], t: 3 },
        { kind: 'slider', role: 'passive', name: 'slide along the humerus', a: arm(V.add(lv(zA), V.scale(sa, -P.S_a))), b: arm(V.add(lv(zA), V.scale(sa, P.S_a))), at: arm(V.add(lv(zA), sA)), z: arm(sn), size: [20, 20, 2.5] },
        { kind: 'slider', role: 'passive', name: 'slide around the arm', a: arm(V.add(V.add(lv(zC), sA), V.scale(st, -P.S_t))), b: arm(V.add(V.add(lv(zC), sA), V.scale(st, P.S_t))), at: arm(V.add(V.add(lv(zC), sA), sT)), z: arm(sn), size: [20, 20, 1.5] },
        { kind: 'slider', role: 'passive', name: 'slide normal (radial)', a: arm(V.add(V.add(lv(zC + 1), sA), sT)), b: arm(V.add(V.add(lv(zC + 2 + 2 * P.R_r), sA), sT)), at: Wp(ap(X3, P3)), z: arm(sa), size: [10, 10, 4] },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: arm(V.scale(hum, P.cuff_at)), axis: arm(hum), r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
