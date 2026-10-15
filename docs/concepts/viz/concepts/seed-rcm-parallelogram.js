/* seed-rcm-parallelogram - scapula base -> R1 (O20 hub on u1 through GH) -> a planar DOUBLE PARALLELOGRAM whose remote
 * centre of motion is an axis through GH (all 7 pivots parallel to it) -> full ring bearing round the upper arm -> cuff
 * (models/seed-rcm-parallelogram.py, order "yaw"; modelling interrupted: 12 screen entries, none reaches; k8 used, the
 * only one with a real measurement: gap 329, valid 0.945 - k1's 275 is the all-zero screen value). Axes: u1 =
 * dirvec(-50, 160) (scapula), a2 = unit(u1 x d) (alpha1 = alpha2 = 90, branch +1) = the linkage plane's normal, which
 * turns with R1; in that plane (origin O = GH, ground direction u1) the output O-link C-C2 turns exactly like link 1
 * about O, i.e. it swings the arm direction d about a2 although no metal sits at GH. Pivots (plane coords): A = rho_A
 * u(psi_A) the ACTIVE input (O20), A' = (1 - lam) A, B = A + C, B' = A' + C, B2 = A + (1 + mu) C, C = r_C u(th + phi_C),
 * C2 = (1 + mu) C (rho_A 63.4, r_C 47.4, lam 0.57, mu 0.56, phi_C -0.2, gamma0 -81.4); bars in two layers 60 / 64.5 mm
 * along the plane normal (schematic: the model fits them on the skin). The output arm runs to the ring's outer race at
 * a2 (114.9 mm down the arm, r 82.5, thin section); the inner race is bolted to the cuff: J3 = the arm's twist.
 * psi_A from the window of 160 deg holding most of this loop's th (the model: of the bench's). 3 ACTIVE (R1, the
 * parallelogram input at A, the ring) + 6 PASSIVE pivots (A', B, B', B2, C, C2, each set by the two loop closures; the
 * catalogue's 4 counts a single parallelogram + a cuff slide, which this model does not have). Closed form; the residual
 * re-checks the arm frame the chain builds from (q1, th, q3). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = K.D2R;
  const P = { u_plane: -50, u_elev: 160, branch: 1, hub_end: 1, rho_A: 63.4, r_C: 47.4, lam: 0.57, mu: 0.56, phi_C: -0.2,
              gamma0: -81.4, eps: 10, ring_l: 114.9, r_ring: 82.5, ring_t: 6.35, h: 60, up: 4.5, R1: 62, sing: 10,
              hub_r: 10, stack: 12.25, piv_r: 7, piv_h: 8.5, cuff_at: 150 };
  const dirvec = (pl, el) => [Math.sin(el * D2R) * Math.sin(pl * D2R), -Math.cos(el * D2R), Math.sin(el * D2R) * Math.cos(pl * D2R)];
  const u1 = V.unit(dirvec(P.u_plane, P.u_elev)), e1u = V.perp(u1), e2u = V.cross(u1, e1u);     // scapula frame
  const u = a => [Math.cos(a * D2R), Math.sin(a * D2R)];
  /** closed form in the scapula frame: a2 (plane normal), th (arm direction in the plane), q */
  function kin(ctx) {
    const Q = M.mul(M.T(ctx.S), ctx.H), d = M.mulv(Q, [0, -1, 0]), a2 = K.circInt(u1, 90, d, 90, P.branch).p;
    const g2 = V.cross(a2, u1), th = Math.atan2(V.dot(d, g2), V.dot(d, u1)) * K.R2D;
    const loc = M.mulv(M.T(Q), a2), th3 = Math.atan2(loc[2], loc[0]) * K.R2D;
    return { Q, d, a2, th, q: [K.axisAngle(u1, e1u, a2), th, th3] };
  }
  /** the arm frame (scapula frame) the chain builds from q: a2 = R1 turn of e1u, d in the plane at th, twist q3 */
  function fk(q) {
    const a2 = V.add(V.scale(e1u, Math.cos(q[0] * D2R)), V.scale(e2u, Math.sin(q[0] * D2R))), g2 = V.cross(a2, u1);
    const d = V.add(V.scale(u1, Math.cos(q[1] * D2R)), V.scale(g2, Math.sin(q[1] * D2R)));
    const cL = [Math.cos(q[2] * D2R), 0, Math.sin(q[2] * D2R)], yL = [0, -1, 0];
    const Wm = M.fromCols(a2, d, V.cross(a2, d)), Lm = M.fromCols(cL, yL, V.cross(cL, yL));
    return { a2, g2, d, Q: M.mul(Wm, M.T(Lm)) };
  }
  let PSI = null;
  function psiA() {                                        // th_mid: the 160 deg window holding most of the loop's th
    if (PSI != null) return PSI;
    const th = K.motion(120).map(f => kin(K.makeCtx(f.pose)).th); let best = -1, c0 = 0;
    for (let c = -180; c < 180; c += 2) { const k = th.filter(x => Math.abs(K.wrap180(x - c)) <= 90 - P.eps).length; if (k > best) { best = k; c0 = c; } }
    return (PSI = c0 + P.phi_C + P.gamma0);
  }
  function pivots(th) {
    const Cp = u(th + P.phi_C).map(x => x * P.r_C), A = u(psiA()).map(x => x * P.rho_A), s = (p, k) => p.map(x => x * k);
    const add = (p, r) => [p[0] + r[0], p[1] + r[1]], Ap = s(A, 1 - P.lam);
    return { A, Ap, B: add(A, Cp), Bp: add(Ap, Cp), B2: add(A, s(Cp, 1 + P.mu)), C: Cp, C2: s(Cp, 1 + P.mu) };
  }

  K.register({
    id: 'seed-rcm-parallelogram',
    name: 'R1 + RCM double parallelogram + arm ring',
    dof: { active: 3, passive: 6 },
    params: P,
    q0: ctx => kin(ctx).q,
    qNames: ['J1 hub (turns the linkage plane)', 'J2 parallelogram input at A (= arm swing about a2)', 'J3 arm ring (twist)'],
    qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => kin(ctx).q,
    residual: (q, ctx) => M.rotErrDeg(fk(q).Q, M.mul(M.T(ctx.S), ctx.H)),
    check: (q, ctx) => {
      const k = kin(ctx), g = V.angle(u1, k.d), m = Math.min(g, 180 - g);
      if (m < P.sing) return `arm within ${m.toFixed(0)} deg of the R1 axis (linkage plane undefined)`;
      const gam = psiA() - (q[1] + P.phi_C), sg = Math.sin(P.gamma0 * D2R) >= 0 ? 1 : -1;
      if (sg * Math.sin(gam * D2R) < Math.sin(P.eps * D2R)) return 'parallelogram opening outside [10, 170] deg (collapse / flip)';
      return null;
    },
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), f = fk(q), J = pivots(q[1]), p = f.a2;
      const at = (xy, lay) => W(V.add(V.add(V.scale(u1, xy[0]), V.scale(f.g2, xy[1])), V.scale(p, P.h + lay * P.up)));
      const bar = (a, b, lay, name) => ({ kind: 'link', role: 'link', name, a: at(J[a], lay), b: at(J[b], lay), r: 3 });
      const piv = (j, lay) => ({ kind: 'hub', role: 'passive', name: `pivot ${j}`, c: at(J[j], lay - 0.5), axis: W(p), p0: at(J[j], lay - 0.5), r: P.piv_r, h: P.piv_h });
      const pW = W(p), dW = W(f.d), harm = ctx.armAxis, ringC = V.scale(dW, P.ring_l);
      const carW = V.madd(ringC, pW, P.r_ring + P.ring_t), lat = V.unit(V.reject(ctx.attach.armDir([0, 0, 1]), harm));
      const hub1 = V.scale(W(u1), P.hub_end * P.R1), cuffC = V.scale(harm, P.cuff_at);
      const spoke = s => ({ kind: 'link', role: 'fixed-arm', name: 'inner race to cuff', a: V.madd(V.madd(ringC, harm, 4), lat, s * (P.r_ring - 1)),
        b: V.madd(cuffC, lat, s * 48), r: 3 });
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base (scapula handler)', c: V.scale(W(u1), P.R1 - 3), z: W(u1), x: ctx.attach.scapDir([1, 0, 0]), size: [40, 34], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1 (R1, axis u1)', c: hub1, axis: W(u1), r: P.hub_r, h: P.stack },
        { kind: 'arc', role: 'link', name: 'ground arm (R1 to the linkage)', pts: K.greatArc(V.madd(hub1, W(u1), P.stack + 1), at(J.Ap, 0), P.R1 + P.stack + 1, V.norm(at(J.Ap, 0))), r: 3 },
        bar('A', 'Ap', 0, 'ground bar A-A\''), bar('A', 'B2', 1, 'link 1 A-B-B2'), bar('Ap', 'Bp', 1, 'crank A\'-B\''),
        bar('B', 'C', 0, 'link 2 B-B\'-C'), bar('B2', 'C2', 0, 'link 2\' B2-C2'), bar('C', 'C2', 1, 'output O-link C-C2'),
        { kind: 'hub', role: 'active', name: 'J2 input A (O20)', c: at(J.A, -0.5), axis: pW, p0: at(J.A, -0.5), r: P.hub_r, h: P.stack },
        piv('Ap', 0), piv('B', 0), piv('Bp', 0), piv('B2', 0), piv('C', 0), piv('C2', 0),
        { kind: 'arc', role: 'link', name: 'output arm (to the ring)', pts: K.greatArc(at(J.C2, 1), carW, V.norm(at(J.C2, 1)), V.norm(carW)), r: 3 },
        { kind: 'rail', role: 'active', name: 'J3 full ring bearing (thin section)', c: ringC, axis: harm, ref: pW, rho: P.r_ring + P.ring_t / 2, a0: 0, a1: 360, r: P.ring_t / 2 },
        spoke(1), spoke(-1),
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre (remote centre)', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
