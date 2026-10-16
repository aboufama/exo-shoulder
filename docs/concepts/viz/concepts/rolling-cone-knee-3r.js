/* rolling-cone-knee-3r - spherical 3R whose middle joint J2 is a ROLLING-CONE pair: no hub and no stack at the knee
 * (catalogue rolling-cone-knee-3r, ideated; marked a duplicate of rolling-cone-elbow, same machinery). Chain: scapula ->
 * J1 (O20 hub, ACTIVE, axis u1 through GH) -> link 1 ending in conical rocker C1 (apex GH, axis c1, cap half-angle kappa)
 * =J2= rocker C2 on link 2 (same kappa) rolling on C1 without slip, held by crossed thin metal bands (Jacob's-ladder /
 * CORE joint): R_rel(t) = Rot(c1, t) Rot(c2_0, t) (equal cones: equal spin), a 1-DOF ACTIVE joint sensed across the
 * contact -> link 2 -> J3 (O20 hub, ACTIVE, arm-fixed axis j3 through GH) -> cuff. 3 active, 0 passive (the bands are
 * part of the joint). This preview: the spec's mid-range kappa 20, b1 = angle(u1, c1) 75, b2 = angle(c2, j3) 75
 * (both 50-100), u1 / j3 = the champion's dome J1 and humerus J3 axes; a kinematic loop screen over kappa 15-25,
 * b1 / b2 55-95 and the rocker phases closed every loop frame at these values. Closed form as rolling-cone-elbow: t =
 * the root of angle(u1, R_rel(t) j3) = angle(u1, arm j3) on the monotone segment holding t = 0, 10 deg margin at a fold
 * end; both rockers in ONE 5.5 mm layer at 66 mm (schematic), spanning the contact range used on the loop +- 10 deg.
 * As in rolling-cone-elbow, a rocker passes ~21 mm from the humerus axis line (inside the deltoid) somewhere on the loop:
 * the spec's phase / site sweep has to trade that against closure. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const P = Object.assign({}, { az: 2.43, el: 80.68, wd: 86.33, wa: 21.83, kappa: 20, beta1: 75, beta2: 75, gamma: 0, gamma2: 180,
              sing: 10, pad: 10, faces: [53, 72], hub_r: 10, stack: 12.25, rim_R: 66, rim_h: 5.5, neck_deg: 25, cuff_at: 165 });
  P.a1 = P.kappa; P.a2 = P.kappa;
  const D = K.D2R, b = K.bvec(P.az, P.el), Wh = K.wdir(P.wd, P.wa), k = Math.sin(P.a1 * D) / Math.sin(P.a2 * D);
  const s0 = V.unit(V.add(V.scale(b, Math.cos(P.beta1 * D)), V.scale(V.unit(V.reject([1, 0, 0], b)), Math.sin(P.beta1 * D))));
  const f = V.unit(V.reject(b, s0)), cref = V.sub(V.scale(s0, Math.cos((P.a1 + P.a2) * D)), V.scale(f, Math.sin((P.a1 + P.a2) * D)));
  const c0 = M.mulv(M.rot(s0, P.gamma), cref), g0 = V.unit(V.add(V.scale(s0, Math.sin(P.a2 * D)), V.scale(c0, Math.sin(P.a1 * D))));
  const w2 = K.onCone(c0, V.reject(s0, c0), P.beta2, P.gamma2), A0 = M.rot(V.cross(Wh, w2), V.angle(Wh, w2));   // A0 Wh = w2
  const Mp = psi => M.mul(M.rot(s0, psi), M.rot(c0, k * psi));
  const th = psi => V.angle(b, M.mulv(Mp(psi), w2));
  // monotone segment of theta(psi) holding psi = 0 (0.5 deg grid), its fold ends and the usable theta window
  const grid = []; for (let p = -360; p <= 360; p += 0.5) grid.push([p, th(p)]);
  const i0 = 720, sg = Math.sign(grid[i0 + 1][1] - grid[i0][1]) || 1; let lo = i0, hi = i0 + 1;
  while (lo > 0 && Math.sign(grid[lo][1] - grid[lo - 1][1]) === sg) lo--;
  while (hi < grid.length - 1 && Math.sign(grid[hi + 1][1] - grid[hi][1]) === sg) hi++;
  const thA = grid[lo][1] + (lo > 0 ? sg * P.sing : 0), thB = grid[hi][1] - (hi < grid.length - 1 ? sg * P.sing : 0);
  function rootPsi(t) {                                           // bisection on [grid lo, grid hi] (theta monotone)
    let a = grid[lo][0], z = grid[hi][0];
    if ((t - grid[lo][1]) * sg <= 0) return a; if ((t - grid[hi][1]) * sg >= 0) return z;
    for (let i = 0; i < 50; i++) { const m = (a + z) / 2; if ((th(m) - t) * sg < 0) a = m; else z = m; }
    return (a + z) / 2;
  }
  const chainR = q => M.mul(M.mul(M.mul(M.rot(b, q[0]), Mp(q[1])), M.rot(w2, q[2])), A0);
  function solve(ctx) {
    const Q = M.mul(M.T(ctx.S), ctx.H), w = M.mulv(Q, Wh), psi = rootPsi(V.angle(b, w));
    const q1 = K.axisAngle(b, M.mulv(Mp(psi), w2), w), R3 = M.mul(M.T(M.mul(M.rot(b, q1), Mp(psi))), M.mul(Q, M.T(A0)));
    const r = V.perp(w2); return [q1, psi, K.axisAngle(w2, r, M.mulv(R3, r))];
  }
  const inWin = ctx => { const t = V.angle(b, M.mulv(M.mul(M.T(ctx.S), ctx.H), Wh)); return (t - thA) * sg >= 0 && (t - thB) * sg <= 0; };
  const ps = K.motion(240).map(fr => K.makeCtx(fr.pose, fr.t)).filter(inWin).map(c => solve(c)[1]);
  const pLo = Math.min(...ps) - P.pad, pHi = Math.max(...ps) + P.pad;
  const u0s = V.reject(g0, s0), u0p = V.reject(g0, c0);
  const rim = (axis, ref, half, a0, a1, role, name, R) => ({ kind: 'rail', role, name, c: V.scale(axis, R * Math.cos(half * D)), axis, ref,
                                                          rho: R * Math.sin(half * D), a0, a1, r: 2.2 });

  K.register({
    id: 'rolling-cone-knee-3r',
    name: '3R with a rolling-cone J2 knee (equal cones, no knee hub)',
    dof: { active: 3, passive: 0 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'psi (J2 roll)', 'J3'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => solve(ctx),
    residual: (q, ctx) => M.rotErrDeg(chainR(q), M.mul(M.T(ctx.S), ctx.H)),
    check: (q, ctx) => {
      return inWin(ctx) ? null : 'the rims cannot roll far enough (arm axis outside the J2 window)';
    },
    parts: (q, ctx) => {
      const S = ctx.S, L1 = M.mul(S, M.rot(b, q[0])), L2 = M.mul(L1, Mp(q[1])), F = P.faces, h = P.stack, R = P.rim_R + P.rim_h / 2;
      const B = M.mulv(S, b), Wa = M.mulv(L2, w2), sA = M.mulv(L1, s0), cA = M.mulv(L2, c0), g = M.mulv(L1, M.mulv(M.rot(s0, q[1]), g0));
      const sunMid = M.mulv(L1, K.onCone(s0, u0s, P.a1, (pLo + pHi) / 2)), plMid = M.mulv(L2, K.onCone(c0, u0p, P.a2, -k * (pLo + pHi) / 2));
      const harm = ctx.armAxis, ng = P.neck_deg * D, nk = V.unit(V.add(V.scale(Wa, Math.cos(ng)), V.scale(V.unit(V.reject(harm, Wa)), Math.sin(ng))));
      const neckEnd = V.scale(nk, F[1] + 1), cuffC = V.scale(harm, P.cuff_at);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base plate', c: V.scale(B, F[0] - 3), z: B, x: M.mulv(S, [1, 0, 0]), size: [46, 32], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1 (O20 hub)', c: V.scale(B, F[0]), axis: B, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 1', u: B, v: sunMid, r0: F[0] + 7, r1: P.rim_R + 1, r: 2.5 },
        rim(sA, M.mulv(L1, u0s), P.a1, pLo, pHi, 'active', 'J2 rocker C1 (link 1, cone kappa about c1)', R),
        rim(cA, M.mulv(L2, u0p), P.a2, -k * pHi, -k * pLo, 'active', 'J2 rocker C2 (link 2, same kappa, same layer, rolls on C1)', R),
        { kind: 'link', role: 'active', name: 'J2 contact line = moving axis (crossed thin bands, Jacob\'s ladder)', a: V.scale(g, P.rim_R - 1), b: V.scale(g, P.rim_R + P.rim_h + 1), r: 1.3 },
        { kind: 'arc', role: 'link', name: 'link 2', u: plMid, v: Wa, r0: P.rim_R + 1, r1: F[1] + h + 1, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3 (O20 hub)', c: V.scale(Wa, F[1]), axis: Wa, r: P.hub_r, h },
        { kind: 'arc', role: 'fixed-arm', name: 'arm-end neck', u: Wa, v: nk, r0: F[1] + 1, r1: F[1] + 1, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'neck to cuff', a: neckEnd, b: V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47), r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
