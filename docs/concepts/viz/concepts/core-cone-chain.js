/* core-cone-chain - a spherical 3-DOF chain whose three joints are conical rolling-contact pairs (CORE) in ONE layer:
 * no pins, no stacked hubs (catalogue core-cone-chain; models/core-cone-chain.py, no sweep yet: the model's PARAMS).
 * Reference: the champion 3R (b, W, arcs, branch -1); its joint values over the loop give each joint's mid-range
 * q_mid, the axes there are the pair mean axes m1..m3 and Q0 the arm orientation there. Pair k: two cone frustums with
 * their apex at GH, cA = cos bA m - sin bA n (proximal body), cB = cos bB m + sin bB n (distal body), bA = atan(rho / F)
 * (equal cones: c = 1), n = the in-plane direction from the incoming to the outgoing member. Crossed bands make each
 * pair a one-parameter roll psi_k: distal = proximal Rot(cA, psi) Rot(cB, c psi) (disc B orbits disc A by psi, the
 * relative turn is 2 psi). Arm = B3 Q0. 3 ACTIVE (psi1..3), 0 passive. Numeric IK from the 3R seed
 * psi = (q - q_mid) / 2; working range |psi| <= 85 deg and the 3R's 10 deg fold margin (the model's acceptance).
 * Discs O14 x 4.5 mm at schematic skin faces F (the model fits them per pose). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const CH = { az: 2.4305071427308924, el: 80.67633718429899, a: [76.90180446920043, 66.74921235407174],
               w: [86.32769021001913, 21.829657347343378], branch: -1 };
  const P = { seed: 'champ', rho: 7, ratio: 1, disc_h: 4.5, psi_max: 85, n: [0, 0, 0], F: [56, 70, 64], width: 8,
              neck_deg: 25, stub: 10, sing_deg: 10, cuff_at: 165 };
  const C = K.sph3r(K.bvec(CH.az, CH.el), K.wdir(CH.w[0], CH.w[1]), CH.a[0], CH.a[1], CH.branch);
  // mid-range of each 3R joint over the loop (largest-gap rule on the circle)
  const qs = K.motion(240).map(f => K.makeCtx(f.pose, f.t)).filter(c => C.margin(c) >= P.sing_deg).map(c => C.solve(c));
  const qm = [0, 1, 2].map(k => {
    const s = qs.map(q => K.wrap180(q[k])).sort((a, b) => a - b); let g = -1, at = 0;
    s.forEach((x, i) => { const d = (i + 1 < s.length ? s[i + 1] : s[0] + 360) - x; if (d > g) { g = d; at = i; } });
    const lo = s[(at + 1) % s.length]; return K.wrap180(lo + (360 - g) / 2);
  });
  const T1 = M.rot(C.u1, qm[0]), T2 = M.mul(T1, M.rot(C.u2, qm[1]));
  const m = [C.u1, M.mulv(T1, C.u2), M.mulv(T2, C.u3)], Q0 = M.mul(T2, M.rot(C.u3, qm[2]));
  const tang = (a, v) => V.unit(V.reject(v, a));
  const h0 = M.mulv(Q0, [0, -1, 0]), ng = P.neck_deg * K.D2R;
  const e0 = V.unit(V.add(V.scale(m[2], Math.cos(ng)), V.scale(tang(m[2], h0), Math.sin(ng))));   // neck end (arm body)
  const nd = [tang(m[0], m[1]), V.unit(V.sub(tang(m[1], m[2]), tang(m[1], m[0]))), V.unit(V.sub(tang(m[2], e0), tang(m[2], m[1])))];
  const pr = [0, 1, 2].map(k => {
    const n = M.mulv(M.rot(m[k], P.n[k]), nd[k]), bA = Math.atan(P.rho / P.F[k]), bB = Math.atan(P.ratio * P.rho / P.F[k]);
    return { n, bA, bB, c: Math.sin(bA) / Math.sin(bB),
             cA: V.sub(V.scale(m[k], Math.cos(bA)), V.scale(n, Math.sin(bA))), cB: V.add(V.scale(m[k], Math.cos(bB)), V.scale(n, Math.sin(bB))) };
  });
  /** body rotations B0..B3 (scapula frame, relative to the reference configuration) */
  function bodies(q) {
    const B = [M.I3()]; let T = B[0];
    for (let k = 0; k < 3; k++) { T = M.mul(M.mul(T, M.rot(pr[k].cA, q[k])), M.rot(pr[k].cB, pr[k].c * q[k])); B.push(T); }
    return B;
  }
  const seed = ctx => C.solve(ctx).map((x, k) => K.wrap180(x - qm[k]) / (1 + pr[k].c));

  K.register({
    id: 'core-cone-chain',
    name: 'CORE cone chain (rolling discs)',
    dof: { active: 3, passive: 0 },
    params: P,
    q0: ctx => seed(ctx),
    qNames: ['psi1 (roll J1)', 'psi2 (roll J2)', 'psi3 (roll J3)'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    residual: (q, ctx) => M.rotErrDeg(M.mul(bodies(q)[3], Q0), M.mul(M.T(ctx.S), ctx.H)),
    check: (q, ctx) => {
      const mg = C.margin(ctx);
      if (mg < P.sing_deg) return mg < 0 ? 'the reference 3R cannot close here' : `within ${mg.toFixed(0)} deg of the chain's fold`;
      for (let k = 0; k < 3; k++) if (Math.abs(q[k]) > P.psi_max) return `pair ${k + 1} rolled past ${P.psi_max} deg (${q[k].toFixed(0)})`;
      return null;
    },
    parts: (q, ctx) => {
      const B = bodies(q), W = (b, d) => M.mulv(ctx.S, M.mulv(B[b], d)), F = P.F, h = P.disc_h, out = [];
      out.push({ kind: 'plate', role: 'fixed-scapula', name: 'base pad (handler)', c: V.scale(W(0, V.unit(V.sub(pr[0].cA, V.scale(pr[0].n, 0.18)))), F[0] - 3),
                 z: W(0, pr[0].cA), x: W(0, pr[0].n), size: [30, 18], t: 3 });
      for (let k = 0; k < 3; k++) {
        const a = W(k, pr[k].cA), b = W(k + 1, pr[k].cB);
        const ct = W(k, M.mulv(M.rot(pr[k].cA, q[k]), m[k]));          // contact generator: the joint's instantaneous axis
        out.push({ kind: 'hub', role: 'active', name: `J${k + 1} disc A (proximal cone)`, c: V.scale(a, F[k]), axis: a, r: P.rho, h });
        out.push({ kind: 'hub', role: 'active', name: `J${k + 1} disc B (rolls on A)`, c: V.scale(b, F[k]), axis: b, r: P.ratio * P.rho, h });
        out.push({ kind: 'link', role: 'active', name: `J${k + 1} contact line (crossed bands)`, a: V.scale(ct, F[k] - 1), b: V.scale(ct, F[k] + h + 1), r: 1.2 });
        if (k < 2) out.push({ kind: 'arc', role: 'link', name: `link ${k + 1} (Ti strap, same layer)`, u: b, v: W(k + 1, pr[k + 1].cA),
                              r0: F[k] + h / 2, r1: F[k + 1] + h / 2, r: 2.5 });
      }
      const nk = W(3, e0), neckEnd = V.scale(nk, F[2] + 2), harm = ctx.armAxis, cuffC = V.scale(harm, P.cuff_at);
      out.push({ kind: 'arc', role: 'fixed-arm', name: 'neck (arm end)', u: W(3, pr[2].cB), v: nk, r0: F[2] + h / 2, r1: F[2] + 2, r: 2.5 });
      out.push({ kind: 'link', role: 'fixed-arm', name: 'neck to cuff', a: neckEnd, b: V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47), r: 3 });
      out.push({ kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 });
      out.push({ kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 });
      return out;
    }
  });
})();
