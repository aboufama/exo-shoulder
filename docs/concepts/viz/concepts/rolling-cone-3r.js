/* rolling-cone-3r - hubless spherical rolling-contact joints: three strap-held conical rolling pairs with their apex
 * at GH, rigid cuff (catalogue rolling-cone-3r; model docs/concepts/models/rolling-cone-3r.py, step-0 law-only ghost).
 * Joint k: a SUN cone band (axis c_k, half-angle ga, fixed in the proximal member) and a PLANET cone band (axis m0_k,
 * half-angle gb, fixed in the distal member) touching along the contact generator w_k; crossed flexure straps make it
 * roll without slip: relative rotation T_k(t) = R(c_k, t / (1 + r)) R(m0_k, t r / (1 + r)), r = +-sin ga / sin gb
 * (J2 is an INTERNAL pair: the planet rolls inside a concave sun ring, r < 0). The instantaneous joint axis is the
 * contact line R(c_k, x) w_k: it walks along both bands as the joint turns. FK: M3 = T1 T2 T3 (reference Q = I), the
 * arm = M3. 3 ACTIVE (t1..t3), 0 passive. Seats: H1 (skin-normal-3r-pin-knee H-g107-1) with J3 on its GH ray (b3 0),
 * the best all-rolling cell of the step-0 search (seeded CMA on Bench(60,160) ws, read on Bench(110,360): 292 ws /
 * 104 clip / 14 overhead kinematic, vs 265 / 110 / 12 for the same seats with three pins). Rim arcs = the joint
 * values over the taken Bench(110,360) poses (+-5 deg); band radii are the schematic one-level R of the step-0 band
 * check. Red = the instantaneous-dyad fold (contact lines w1, w2, w3 within 5 deg of coplanar, or the other branch)
 * or a contact rolled off its band. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  // exported by `python3 docs/concepts/models/rolling-cone-3r.py viz '<cell>'` (scapula frame at the reference Q = I)
  const G = {"J": [{"kind": "roll", "c": [0.08665, 0.98976, 0.11344], "m0": [0.08432, 0.87921, 0.46891], "w": [0.08518, 0.89802, 0.43164], "r": 7.82187, "ga": 19.062, "gb": 2.393},
                   {"kind": "roll", "c": [-0.92657, 0.25697, 0.27466], "m0": [-0.66129, 0.61576, 0.4284], "w": [-0.58009, 0.67877, 0.4503], "r": -5.23458, "ga": 33.322, "gb": 6.024},
                   {"kind": "roll", "c": [-0.0222, -0.18886, 0.98175], "m0": [-0.1759, -0.39051, 0.90364], "w": [-0.13314, -0.33557, 0.93256], "r": 2.51544, "ga": 10.925, "gb": 4.321}],
             "branch": -1.0, "t_rest_deg": [-10.661, -4.292, 6.99]};
  const P = { R: [58, 60, 60], rim_h: 8, margin: 5, pad: 5, range: [[-103.6, 142.7], [-67.1, 87.6], [-146.0, 150.5]], neck_deg: 25, cuff_at: 165,
              cell: { J1: [19.062, 2.393, 78.869, 1], J2: [33.322, 6.024, -129.74, -1], J3: [10.925, 4.321, 51.966, 1] } };
  const J = G.J.map((j, k) => {
    const lo = P.range[k][0] - P.pad, hi = P.range[k][1] + P.pad, f = 1 / (1 + j.r), xs = [lo * f, hi * f], ys = [lo * j.r * f, hi * j.r * f];
    return Object.assign({}, j, { f, lo, hi, x: [Math.min(...xs), Math.max(...xs)], y: [Math.min(...ys), Math.max(...ys)] });
  });
  const Tk = (j, t) => M.mul(M.rot(j.c, t * j.f), M.rot(j.m0, t * j.r * j.f));
  const wk = (j, t) => M.mulv(M.rot(j.c, t * j.f), j.w);            // contact line, proximal frame
  function bodies(q) { const B = [M.I3()]; let T = B[0]; for (let k = 0; k < 3; k++) { T = M.mul(T, Tk(J[k], q[k])); B.push(T); } return B; }
  function margin(q) {
    const B = bodies(q), w = [0, 1, 2].map(k => V.unit(M.mulv(B[k], wk(J[k], q[k]))));
    const th = V.angle(w[0], w[2]), a1 = V.angle(w[0], w[1]), a2 = V.angle(w[1], w[2]);
    return { m: Math.min(th - Math.abs(a1 - a2), a1 + a2 - th, 360 - a1 - a2 - th), br: Math.sign(V.dot(w[1], V.cross(w[0], w[2]))) };
  }
  const rimPart = (S, B, ax, w, R, g, a0, a1, name) => {
    const axis = M.mulv(S, M.mulv(B, ax)), ref = M.mulv(S, M.mulv(B, V.unit(V.reject(w, ax))));
    return { kind: 'rail', role: 'active', name, c: V.scale(axis, (R + P.rim_h / 2) * Math.cos(g * K.D2R)), axis, ref,
             rho: (R + P.rim_h / 2) * Math.sin(g * K.D2R), a0, a1, r: 1.6 };
  };
  K.register({
    id: 'rolling-cone-3r',
    name: 'Rolling-cone 3R: three strap-held cone pairs, apex GH, no hubs (rigid cuff)',
    dof: { active: 3, passive: 0 },
    params: P,
    q0: () => G.t_rest_deg.slice(),
    qNames: ['t1 (roll J1)', 't2 (roll J2, internal)', 't3 (roll J3)'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    residual: (q, ctx) => M.rotErrDeg(bodies(q)[3], M.mul(M.T(ctx.S), ctx.H)),
    check: (q) => {
      for (let k = 0; k < 3; k++) if (q[k] < J[k].lo || q[k] > J[k].hi) return `contact ${k + 1} rolled off its bands (${q[k].toFixed(0)} deg)`;
      const mg = margin(q);
      if (mg.br !== G.branch) return 'contact lines crossed to the other branch';
      return mg.m < P.margin ? `contact lines within ${Math.max(0, mg.m).toFixed(1)} deg of the fold (>= ${P.margin})` : null;
    },
    parts: (q, ctx) => {
      const B = bodies(q), S = ctx.S, Wd = (b, d) => M.mulv(S, M.mulv(B[b], d)), out = [];
      const sunMid = k => M.mulv(M.rot(J[k].c, (J[k].x[0] + J[k].x[1]) / 2), J[k].w);       // body k
      const plMid = k => M.mulv(M.rot(J[k].m0, -(J[k].y[0] + J[k].y[1]) / 2), J[k].w);      // body k + 1
      out.push({ kind: 'plate', role: 'fixed-scapula', name: 'base pad (scapula handler)', c: V.scale(Wd(0, sunMid(0)), P.R[0] - 2),
                 z: Wd(0, sunMid(0)), x: ctx.attach.scapDir([1, 0, 0]), size: [30, 22], t: 3 });
      for (let k = 0; k < 3; k++) {
        const j = J[k], ct = Wd(k, wk(j, q[k]));
        out.push(rimPart(S, B[k], j.c, j.w, P.R[k], j.ga, j.x[0], j.x[1], `J${k + 1} sun band (cone ${j.ga.toFixed(0)} deg about c${k + 1})`));
        out.push(rimPart(S, B[k + 1], j.m0, j.w, P.R[k], j.gb, -j.y[1], -j.y[0], `J${k + 1} planet band (cone ${j.gb.toFixed(0)} deg about m${k + 1})`));
        out.push({ kind: 'link', role: 'active', name: `J${k + 1} contact line = instantaneous axis (crossed straps)`, a: V.scale(ct, P.R[k] - 1), b: V.scale(ct, P.R[k] + P.rim_h + 1), r: 1.2 });
        if (k < 2) out.push({ kind: 'arc', role: 'link', name: `link ${k + 1} (strap)`, u: Wd(k + 1, plMid(k)), v: Wd(k + 1, sunMid(k + 1)), r0: P.R[k] + 2, r1: P.R[k + 1] + 2, r: 2.5 });
      }
      const harm = ctx.armAxis, rb = V.unit(Wd(3, plMid(2))), ng = P.neck_deg * K.D2R;
      const nk = V.unit(V.add(V.scale(rb, Math.cos(ng)), V.scale(V.unit(V.reject(harm, rb)), Math.sin(ng)))), neckEnd = V.scale(nk, P.R[2] + 2);
      const cuffC = V.scale(harm, P.cuff_at);
      out.push({ kind: 'arc', role: 'fixed-arm', name: 'arm saddle (member 3)', u: rb, v: nk, r0: P.R[2] + 2, r1: P.R[2] + 2, r: 2.5 });
      out.push({ kind: 'link', role: 'fixed-arm', name: 'saddle to cuff', a: neckEnd, b: V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47), r: 3 });
      out.push({ kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 });
      out.push({ kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 });
      return out;
    }
  });
})();
