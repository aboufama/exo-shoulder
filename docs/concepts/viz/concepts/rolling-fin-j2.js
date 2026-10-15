/* rolling-fin-j2 - J2 is two radial Ti FINS (6 mm tall walls on cones through GH) rolling on each other without slip
 * on top of the scapula, held by crossed flexure straps (catalogue rolling-fin-j2; models/rolling-fin-j2.py, no
 * sweep yet: its PARAMS - the final 3R's b and W, beta1 45, psi1 -45, chi 95, g1 25, g2 20). Chain: scapula -> J1 (O20
 * hub, axis b) -> L1 = hub plate + strap + fin F1 (cone about u1, half-angle g1) =J2 rolling= fin F2 (cone about u2,
 * angle(u1, u2) = g1 + g2) + strap = L2 -> J3 (O20 hub, axis W in the humerus) -> neck -> cuff. L2 rel. L1 =
 * M(phi) = rot(u1, phi) rot(u2, k phi), k = sin g1 / sin g2: one coordinate whose instantaneous axis is the contact
 * generator c(phi) = rot(u1, phi) c_r, walking along both fins. 3 ACTIVE (theta1, phi, theta3), 0 passive. Closed
 * form as the model: phi = the root of angle(b, M(phi) W_r) = angle(b, arm W) on the monotone piece holding phi = 0
 * (unique: no flips), |det[b, c, M W_r]| >= 0.1, the 10 deg margin at a true fold; then theta1 about b, theta3 about W.
 * Fins span the contact range used on the loop +- 6 deg (F2: k x that + 12); hub faces / fin radius schematic.
 * Measured on the loop: every frame closes inside the window, phi -40..25 deg, fins ~36 mm (F1) and ~45 mm (F2) long. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const P = { b_az: 32.55, b_el: 80.56, w_delta: 71.38, w_az: 4.78, beta1: 45, psi1: -45, chi: 95, g1: 25, g2: 20,
              det_min: 0.1, sing: 10, faces: [53, 72], hub_r: 10, stack: 12.25, fin_R: 60, fin_h: 6, neck_deg: 25, cuff_at: 165 };
  const D = K.D2R, b = K.bvec(P.b_az, P.b_el), W0 = K.wdir(P.w_delta, P.w_az);
  const ctx0 = K.makeCtx(K.motion(240)[0].pose, 0), HGr = M.mul(M.T(ctx0.S), ctx0.H), Wr = M.mulv(HGr, W0);
  const ar = M.mulv(HGr, [0, -1, 0]), ea = V.unit(V.scale(V.reject(ar, b), -1)), eb = V.cross(b, ea);
  const u1 = V.add(V.scale(b, Math.cos(P.beta1 * D)), V.scale(V.add(V.scale(ea, Math.cos(P.psi1 * D)), V.scale(eb, Math.sin(P.psi1 * D))), Math.sin(P.beta1 * D)));
  const ew = V.unit(V.reject(Wr, u1)), t = V.add(V.scale(ew, Math.cos(P.chi * D)), V.scale(V.cross(u1, ew), Math.sin(P.chi * D)));
  const g12 = (P.g1 + P.g2) * D, u2 = V.add(V.scale(u1, Math.cos(g12)), V.scale(t, Math.sin(g12)));
  const cr = V.add(V.scale(u1, Math.cos(P.g1 * D)), V.scale(t, Math.sin(P.g1 * D))), k = Math.sin(P.g1 * D) / Math.sin(P.g2 * D);
  const Mp = ph => M.mul(M.rot(u1, ph), M.rot(u2, k * ph));
  const th = ph => V.angle(b, M.mulv(Mp(ph), Wr)), det = ph => V.dot(b, V.cross(M.mulv(M.rot(u1, ph), cr), M.mulv(Mp(ph), Wr)));
  // monotone piece holding phi = 0 (sign of det), shrunk to |det| >= det_min, margin at the true folds (0.5 deg grid)
  const grid = []; for (let p = -360; p <= 360; p += 0.5) grid.push([p, th(p), det(p)]);
  const i0 = 720, s = Math.sign(grid[i0][2]) || 1; let lo = i0, hi = i0;
  while (lo > 0 && s * grid[lo - 1][2] > 0) lo--; while (hi < grid.length - 1 && s * grid[hi + 1][2] > 0) hi++;
  let a = i0, z = i0; while (a > lo && s * grid[a - 1][2] >= P.det_min) a--; while (z < hi && s * grid[z + 1][2] >= P.det_min) z++;
  const sg = Math.sign(grid[z][1] - grid[a][1]) || 1, foldA = a === lo && lo > 0, foldB = z === hi && hi < grid.length - 1;
  const thA = grid[a][1] + (foldA ? sg * P.sing : 0), thB = grid[z][1] - (foldB ? sg * P.sing : 0);
  function rootPhi(x) {
    let l = grid[a][0], r = grid[z][0];
    if ((x - grid[a][1]) * sg <= 0) return l; if ((x - grid[z][1]) * sg >= 0) return r;
    for (let i = 0; i < 50; i++) { const m = (l + r) / 2; if ((th(m) - x) * sg < 0) l = m; else r = m; }
    return (l + r) / 2;
  }
  const armW = ctx => M.mulv(M.mul(M.T(ctx.S), ctx.H), W0);
  const inWin = ctx => { const x = V.angle(b, armW(ctx)); return (x - thA) * sg >= 0 && (x - thB) * sg <= 0; };
  function solve(ctx) {
    const Q = M.mul(M.T(ctx.S), ctx.H), w = M.mulv(Q, W0), ph = rootPhi(V.angle(b, w));
    const q1 = K.axisAngle(b, M.mulv(Mp(ph), Wr), w), R3 = M.mul(M.T(M.mul(M.rot(b, q1), Mp(ph))), M.mul(Q, M.T(HGr)));
    const r = V.perp(Wr); return [q1, ph, K.axisAngle(Wr, r, M.mulv(R3, r))];
  }
  const ph = K.motion(240).map(f => K.makeCtx(f.pose, f.t)).filter(inWin).map(c => solve(c)[1]);
  const pLo = Math.min(...ph) - 6, pHi = Math.max(...ph) + 6, pMid = (pLo + pHi) / 2, half2 = k * (pHi - pLo) / 2 + 12;
  const R = P.fin_R + P.fin_h / 2, fin = (axis, ref, g, a0, a1, name) => ({ kind: 'rail', role: 'active', name,
    c: V.scale(axis, R * Math.cos(g * D)), axis, ref, rho: R * Math.sin(g * D), a0, a1, r: 2.2 });

  K.register({
    id: 'rolling-fin-j2',
    name: 'Rolling-fin J2 (scapula-top fins)',
    dof: { active: 3, passive: 0 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['theta1 (J1)', 'phi (fin roll)', 'theta3 (J3)'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => solve(ctx),
    residual: (q, ctx) => M.rotErrDeg(M.mul(M.mul(M.mul(M.rot(b, q[0]), Mp(q[1])), M.rot(Wr, q[2])), HGr), M.mul(M.T(ctx.S), ctx.H)),
    check: (q, ctx) => (inWin(ctx) ? null : 'the fins cannot roll there (arm axis outside the J2 window)'),
    parts: (q, ctx) => {
      const S = ctx.S, L1 = M.mul(S, M.rot(b, q[0])), L2 = M.mul(L1, Mp(q[1])), F = P.faces, h = P.stack;
      const B = M.mulv(S, b), Wa = M.mulv(L2, Wr), c = M.mulv(L1, M.mulv(M.rot(u1, q[1]), cr));
      const f1 = M.mulv(L1, K.onCone(u1, cr, P.g1, pMid)), f2 = M.mulv(L2, K.onCone(u2, cr, P.g2, -k * pMid));
      const harm = ctx.armAxis, ng = P.neck_deg * D, nk = V.unit(V.add(V.scale(Wa, Math.cos(ng)), V.scale(V.unit(V.reject(harm, Wa)), Math.sin(ng))));
      const neckEnd = V.scale(nk, F[1] + h), cuffC = V.scale(harm, P.cuff_at);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base plate', c: V.scale(B, F[0] - 3), z: B, x: M.mulv(S, [1, 0, 0]), size: [46, 32], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1 (O20 hub)', c: V.scale(B, F[0]), axis: B, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'L1 strap', u: B, v: f1, r0: F[0] + 3.15, r1: P.fin_R, r: 2.5 },
        fin(M.mulv(L1, u1), M.mulv(L1, cr), P.g1, pLo, pHi, 'fin F1 (L1)'),
        fin(M.mulv(L2, u2), M.mulv(L2, cr), P.g2, -k * pMid - half2, -k * pMid + half2, 'fin F2 (L2, rolls on F1)'),
        { kind: 'link', role: 'active', name: 'J2 contact = moving axis (flexure straps)', a: V.scale(c, P.fin_R - 1), b: V.scale(c, P.fin_R + P.fin_h + 1), r: 1.3 },
        { kind: 'arc', role: 'link', name: 'L2 strap', u: f2, v: Wa, r0: P.fin_R, r1: F[1] + 3.15, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3 (O20 hub)', c: V.scale(Wa, F[1]), axis: Wa, r: P.hub_r, h },
        { kind: 'arc', role: 'fixed-arm', name: 'neck', u: Wa, v: nk, r0: F[1] + h, r1: F[1] + h, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'neck to cuff', a: neckEnd, b: V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47), r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
