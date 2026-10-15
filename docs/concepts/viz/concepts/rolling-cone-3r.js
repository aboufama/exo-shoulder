/* rolling-cone-3r - hubless spherical rolling-contact joints: three conical Rolamite / CORE rim pairs with their apex
 * at GH (catalogue rolling-cone-3r; ideated, no bench model yet: the model_spec). Joint k = two Ti cone-sector RIMS
 * standing on edge (radially from skin + 2 to skin + 10 mm), like toothless bevel wheels, held by crossed flexure
 * straps: fixed-cone axis c_k in the lower member, moving-cone axis m_k0 2g from it (equal cones), relative rotation
 * T_k(phi) = R(c_k, phi) R(m_k0, phi); the contact generator R(c_k, phi) m_k (a ray from GH) is the joint's moving
 * axis and walks along both rims. FK M3 = T1 T2 T3 (POE about the reference), arm = M3 Q0. Reference (the spec leaves
 * it open): the champion 3R at each joint's mid-range over the loop, m_k = its axes there, c_k / m_k0 split m_k by
 * +-g along the chain. 3 ACTIVE (phi1..3), 0 passive; numeric IK (LM) from the 3R seed phi = (q - q_mid) / 2. Rims
 * span the seed's phi range +-8 deg on both members; radii schematic. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const CH = { az: 2.4305071427308924, el: 80.67633718429899, a: [76.90180446920043, 66.74921235407174],
               w: [86.32769021001913, 21.829657347343378], branch: -1 };
  const P = { g: [14, 14, 14], R: [56, 70, 64], rim_h: 8, rim_pad: 8, sing_deg: 10, neck_deg: 25, cuff_at: 165 };
  const C = K.sph3r(K.bvec(CH.az, CH.el), K.wdir(CH.w[0], CH.w[1]), CH.a[0], CH.a[1], CH.branch);
  const qs = K.motion(240).map(f => K.makeCtx(f.pose, f.t)).filter(c => C.margin(c) >= P.sing_deg).map(c => C.solve(c));
  const qm = [0, 1, 2].map(k => {                                    // mid-range (largest-gap rule on the circle)
    const s = qs.map(q => K.wrap180(q[k])).sort((a, b) => a - b); let g = -1, at = 0;
    s.forEach((x, i) => { const d = (i + 1 < s.length ? s[i + 1] : s[0] + 360) - x; if (d > g) { g = d; at = i; } });
    return K.wrap180(s[(at + 1) % s.length] + (360 - g) / 2);
  });
  const T1 = M.rot(C.u1, qm[0]), T2 = M.mul(T1, M.rot(C.u2, qm[1]));
  const m = [C.u1, M.mulv(T1, C.u2), M.mulv(T2, C.u3)], Q0 = M.mul(T2, M.rot(C.u3, qm[2]));
  const tang = (a, v) => V.unit(V.reject(v, a)), h0 = M.mulv(Q0, [0, -1, 0]);
  const nd = [tang(m[0], m[1]), V.unit(V.sub(tang(m[1], m[2]), tang(m[1], m[0]))), V.unit(V.sub(tang(m[2], h0), tang(m[2], m[1])))];
  const J = [0, 1, 2].map(k => {
    const g = P.g[k] * K.D2R, ph = qs.map(q => K.wrap180(q[k] - qm[k]) / 2);
    return { c: V.sub(V.scale(m[k], Math.cos(g)), V.scale(nd[k], Math.sin(g))), m0: V.add(V.scale(m[k], Math.cos(g)), V.scale(nd[k], Math.sin(g))),
             lo: Math.min(...ph) - P.rim_pad, hi: Math.max(...ph) + P.rim_pad };
  });
  function bodies(q) {
    const B = [M.I3()]; let T = B[0];
    for (let k = 0; k < 3; k++) { T = M.mul(M.mul(T, M.rot(J[k].c, q[k])), M.rot(J[k].m0, q[k])); B.push(T); }
    return B;
  }
  const rim = (S, B, ax, ref, k, a0, a1, name) => {
    const R = P.R[k] + P.rim_h / 2, g = P.g[k] * K.D2R, axis = M.mulv(S, M.mulv(B, ax));
    return { kind: 'rail', role: 'active', name, c: V.scale(axis, R * Math.cos(g)), axis, ref: M.mulv(S, M.mulv(B, ref)),
             rho: R * Math.sin(g), a0, a1, r: 2.2 };
  };

  K.register({
    id: 'rolling-cone-3r',
    name: 'Rolling-cone 3R (rims, no hubs)',
    dof: { active: 3, passive: 0 },
    params: P,
    q0: ctx => C.solve(ctx).map((x, k) => K.wrap180(x - qm[k]) / 2),
    qNames: ['phi1 (roll J1)', 'phi2 (roll J2)', 'phi3 (roll J3)'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    residual: (q, ctx) => M.rotErrDeg(M.mul(bodies(q)[3], Q0), M.mul(M.T(ctx.S), ctx.H)),
    check: (q, ctx) => {
      for (let k = 0; k < 3; k++) if (q[k] < J[k].lo || q[k] > J[k].hi) return `contact ${k + 1} rolled off its rims (${q[k].toFixed(0)} deg)`;
      const mg = C.margin(ctx); return mg < P.sing_deg ? `within ${Math.max(0, mg).toFixed(0)} deg of the chain's fold` : null;
    },
    parts: (q, ctx) => {
      const B = bodies(q), S = ctx.S, Wd = (b, d) => M.mulv(S, M.mulv(B[b], d)), out = [];
      const mid = (k, b, ax, az) => M.mulv(M.rot(ax, az), m[k]);      // rim mid-arc point (body coords)
      out.push({ kind: 'plate', role: 'fixed-scapula', name: 'base pad (handler)', c: V.scale(Wd(0, J[0].c), P.R[0] - 3), z: Wd(0, J[0].c),
                 x: Wd(0, nd[0]), size: [34, 24], t: 3 });
      for (let k = 0; k < 3; k++) {
        const ct = Wd(k, M.mulv(M.rot(J[k].c, q[k]), m[k]));       // contact generator = the moving joint axis
        out.push(rim(S, B[k], J[k].c, m[k], k, J[k].lo, J[k].hi, `J${k + 1} fixed rim (cone about c${k + 1})`));
        out.push(rim(S, B[k + 1], J[k].m0, m[k], k, -J[k].hi, -J[k].lo, `J${k + 1} rolling rim (cone about m${k + 1})`));
        out.push({ kind: 'link', role: 'active', name: `J${k + 1} contact line (flexure straps)`, a: V.scale(ct, P.R[k] - 1), b: V.scale(ct, P.R[k] + P.rim_h + 1), r: 1.3 });
        if (k < 2) {
          const u = Wd(k + 1, mid(k, k + 1, J[k].m0, -(J[k].lo + J[k].hi) / 2)), v = Wd(k + 1, mid(k + 1, k + 1, J[k + 1].c, (J[k + 1].lo + J[k + 1].hi) / 2));
          out.push({ kind: 'arc', role: 'link', name: `link ${k + 1} (strap)`, u, v, r0: P.R[k] + 2, r1: P.R[k + 1] + 2, r: 2.5 });
        }
      }
      const harm = ctx.armAxis, rb = Wd(3, mid(2, 3, J[2].m0, -(J[2].lo + J[2].hi) / 2)), ng = P.neck_deg * K.D2R;
      const nk = V.unit(V.add(V.scale(rb, Math.cos(ng)), V.scale(V.unit(V.reject(harm, rb)), Math.sin(ng)))), neckEnd = V.scale(nk, P.R[2] + 2);
      const cuffC = V.scale(harm, P.cuff_at);
      out.push({ kind: 'arc', role: 'fixed-arm', name: 'arm saddle', u: rb, v: nk, r0: P.R[2] + 2, r1: P.R[2] + 2, r: 2.5 });
      out.push({ kind: 'link', role: 'fixed-arm', name: 'saddle to cuff', a: neckEnd, b: V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47), r: 3 });
      out.push({ kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 });
      out.push({ kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 });
      return out;
    }
  });
})();
