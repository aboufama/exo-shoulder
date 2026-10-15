/* deltoid-trilateration - muscle-arc trilateration: three telescoping 'deltoid' arcs whose angular lengths are the
 * active joints (catalogue deltoid-trilateration; ideated, no bench model yet: the model_spec seeds). Leg k is R-P-R on
 * a great circle about GH, from a scapula pad A_k (the anterior / middle / posterior deltoid ORIGIN: bvec (120, 60),
 * (60, 70), (0, 50)) to an arm pad B_k (the INSERTION on the cap band: wdir (95, 15), (112, -15), (100, -55)):
 * radial pivot at A_k (passive) -> 3-stage curved telescope, theta_k = angle(A_k, B_k) (ACTIVE, the 'muscle length')
 * -> radial pivot at B_k (passive). Base pads tied by a base bridge, arm pads by an arm bridge with a 14 mm strip to
 * BOTTOM's cut end (canonical (0, -70, 67.5)). 3 ACTIVE + 6 PASSIVE (each leg's plane and pivots follow its ends).
 * Range per leg: the 'telescope3' realisation covers at most 2.6x inside [20, 160]; the loop needs more (the
 * catalogue's span-ratio risk), so each leg's stroke [lo, 2.6 lo] is placed where it covers the most loop frames and
 * the frames past it are flagged. Sensing index:
 * |det[n1 n2 n3]| (n_k = unit(A_k x B_k)) < 0.1 = taken but unsensable. Radii schematic (pads ~55, legs 62-66 mm). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D = K.D2R;
  const P = { A: [[120, 60], [60, 70], [0, 50]], B: [[95, 15], [112, -15], [100, -55]], ratio: 2.6, det: 0.1,
              padR: [56, 54], legR: [62, 62, 66], piv: [7, 6], tube: [4.5, 3.4, 2.4], bottom: [0, -70, 67.5], cuff_at: 165 };
  const A0 = P.A.map(([az, el]) => K.bvec(az, el)), B0 = P.B.map(([d, a]) => K.wdir(d, a));
  const legs = ctx => [0, 1, 2].map(k => ({ A: M.mulv(ctx.S, A0[k]), B: M.mulv(ctx.H, B0[k]) }));
  const thetas = ctx => legs(ctx).map(l => V.angle(l.A, l.B));
  const along = (b, a, s) => { const e = V.unit(V.reject(a, b)), r = s * D; return V.add(V.scale(b, Math.cos(r)), V.scale(e, Math.sin(r))); };
  const span = (b, a, s0, s1, R) => K.greatArc(along(b, a, s0), along(b, a, s1), R, R);
  // per-leg stroke: the loop's range is 2.6x+ wider than telescope3 can cover, so each leg gets the window
  // [lo, min(160, 2.6 lo)] (lo >= 20) that covers the most loop frames; the rest are flagged
  const TH = K.motion(120).map(f => thetas(K.makeCtx(f.pose)));
  const lo = [0, 1, 2].map(k => {
    let best = 20, nb = -1;
    for (let l = 20; l <= 100; l++) { const n = TH.filter(t => t[k] >= l && t[k] <= Math.min(160, P.ratio * l)).length; if (n > nb) { nb = n; best = l; } }
    return best;
  });
  const hi = lo.map(x => Math.min(160, P.ratio * x)), st = lo.map(x => 0.97 * x);
  const nm = ['anterior', 'middle', 'posterior'];

  K.register({
    id: 'deltoid-trilateration',
    name: 'Deltoid trilateration: telescoping muscle arcs',
    dof: { active: 3, passive: 6 },
    params: Object.assign({ stroke: lo.map((x, k) => [x, hi[k]]) }, P),
    q0: ctx => thetas(ctx),
    qNames: nm.map(n => `${n} arc (deg)`), qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => thetas(ctx),
    residual: (q, ctx) => thetas(ctx).map((x, k) => x - q[k]),
    check: (q, ctx) => {
      for (let k = 0; k < 3; k++) if (q[k] < lo[k] || q[k] > hi[k]) return `${nm[k]} arc past its 2.6x telescope (${q[k].toFixed(0)} deg)`;
      const n = legs(ctx).map(l => V.unit(V.cross(l.A, l.B))), d = Math.abs(V.dot(n[0], V.cross(n[1], n[2])));
      return d < P.det ? `lengths stop fixing the pose (|det| ${d.toFixed(2)})` : null;
    },
    parts: (q, ctx) => {
      const L = legs(ctx), out = [], [ra, rb] = P.padR, bot = M.mulv(ctx.H, P.bottom);
      out.push({ kind: 'arc', role: 'fixed-scapula', name: 'base bridge', pts: K.greatArc(L[0].A, L[1].A, ra, ra).concat(K.greatArc(L[1].A, L[2].A, ra, ra)), r: 3 },
        { kind: 'arc', role: 'fixed-arm', name: 'arm bridge', pts: K.greatArc(L[0].B, L[1].B, rb, rb).concat(K.greatArc(L[1].B, L[2].B, rb, rb)), r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'strip to BOTTOM', a: V.scale(L[1].B, rb), b: bot, r: 3 });
      L.forEach((l, k) => {
        const R = P.legR[k], th = q[k], s = st[k], mouth = along(l.A, l.B, s), tan = V.unit(V.sub(along(l.A, l.B, s + 1), mouth));
        out.push({ kind: 'plate', role: 'fixed-scapula', name: `${nm[k]} origin pad`, c: V.scale(l.A, ra), z: l.A, x: tan, size: [24, 24], t: 3 },
          { kind: 'hub', role: 'passive', name: `${nm[k]} origin pivot`, c: V.scale(l.A, ra + 1.5), axis: l.A, r: P.piv[0], h: R - ra - 1.5 },
          { kind: 'arc', role: 'link', name: `${nm[k]} stage 1`, pts: span(l.A, l.B, 0, s, R), r: P.tube[0] },
          { kind: 'arc', role: 'link', name: `${nm[k]} stage 2`, pts: span(l.A, l.B, th / 2 - s / 2, th / 2 + s / 2, R), r: P.tube[1] },
          { kind: 'arc', role: 'link', name: `${nm[k]} stage 3`, pts: span(l.A, l.B, th - s, th, R), r: P.tube[2] },
          { kind: 'carriage', role: 'active', name: `${nm[k]} length (active)`, c: V.scale(mouth, R), x: tan, z: mouth, size: [9, 15, 9] },
          { kind: 'hub', role: 'passive', name: `${nm[k]} insertion pivot`, c: V.scale(l.B, rb + 1.5), axis: l.B, r: P.piv[0], h: R - rb - 1.5 },
          { kind: 'plate', role: 'fixed-arm', name: `${nm[k]} insertion pad`, c: V.scale(l.B, rb), z: l.B, x: tan, size: [24, 24], t: 3 });
      });
      out.push({ kind: 'strap', role: 'fixed-arm', name: 'BOTTOM / cuff', c: V.scale(ctx.armAxis, P.cuff_at), axis: ctx.armAxis, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 });
      return out;
    }
  });
})();
