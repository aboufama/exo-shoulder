/* deltoid-strut-tripod - three rigid ARC STRUTS on the paths of the three deltoid heads, each sliding through a guide
 * on a scapula swivel (spherical 3-RPR parallel; catalogue deltoid-strut-tripod, models/deltoid-strut-tripod.py:
 * modelling interrupted, no sweep - its PARAMS = start set A). Leg i: S -> swivel about the radial axis b_i (passive,
 * O20 hub UNDER its guide: b1 top, b2 anterior-medial over the clavicle, b3 posterior over the scapular spine) ->
 * guide (30 x 22) through which strut i slides (ACTIVE: d_i = angle(b_i, W_i)) -> hinge about W_i (passive, O20 hub on
 * a pedestal) on a humerus-fixed saddle over the anterior / lateral / posterior deltoid (wdir(75, 60 / 0 / -60), 15 deg
 * below the GH level). 3 ACTIVE, 6 PASSIVE (each strut's frame is (W_i, n_i): swivel and hinge follow by closure).
 * The strut is a rigid arc of constant radius R_i from its hinge to d_hi + 17 mm past the guide (d_hi = the loop's
 * longest), so its TAIL sticks out d_hi - d_i past the anchor (the spec's main risk: the loop's d spans 27-162 /
 * 64-144 / 25-142 deg, the tails wrap past the dome). Not taken (spec): d_i within 3 deg of the loop's extremes, or
 * |det J| < 0.1 (rows n_i = unit(b_i x W_i): the struts stop holding the arm). Radii schematic (struts 60 / 66 / 70, saddle 54). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D = K.D2R;
  const P = { b: [[80, 300], [40, 160], [35, 275]], w: [[75, 60], [75, 0], [75, -60]], det: 0.1,
              R: [60, 66, 70], sad: 54, hub_r: 10, stack: 12.25, guide: [30, 22, 10], neck_deg: 25, cuff_at: 165 };
  const dS = (lat, lon) => [Math.cos(lat * D) * Math.sin(lon * D), Math.sin(lat * D), Math.cos(lat * D) * Math.cos(lon * D)];
  const b0 = P.b.map(([la, lo]) => dS(la, lo)), w0 = P.w.map(([d, a]) => K.wdir(d, a));
  const legs = ctx => [0, 1, 2].map(i => ({ b: M.mulv(ctx.S, b0[i]), W: M.mulv(ctx.H, w0[i]) }));
  const lens = ctx => legs(ctx).map(l => V.angle(l.b, l.W));
  const along = (u, v, s) => { const e = V.unit(V.reject(v, u)), r = s * D; return V.add(V.scale(u, Math.cos(r)), V.scale(e, Math.sin(r))); };
  const dhi = [0, 0, 0], dlo = [180, 180, 180];
  for (const f of K.motion(120)) lens(K.makeCtx(f.pose)).forEach((x, i) => { dhi[i] = Math.max(dhi[i], x); dlo[i] = Math.min(dlo[i], x); });
  const nm = ['top', 'anterior', 'posterior'];

  K.register({
    id: 'deltoid-strut-tripod',
    name: 'Deltoid-strut tripod: sliding arc struts',
    dof: { active: 3, passive: 6 },
    params: Object.assign({ d_lo: dlo, d_hi: dhi }, P),
    q0: ctx => lens(ctx),
    qNames: nm.map(n => `${n} strut d (deg)`), qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => lens(ctx),
    residual: (q, ctx) => lens(ctx).map((x, i) => x - q[i]),
    check: (q, ctx) => {
      for (let i = 0; i < 3; i++) if (q[i] < dlo[i] + 3 || q[i] > dhi[i] - 3) return `${nm[i]} strut at its end stop`;
      const n = legs(ctx).map(l => V.unit(V.cross(l.b, l.W))), d = Math.abs(V.dot(n[0], V.cross(n[1], n[2])));
      return d < P.det ? `struts near-coplanar: the arm is not held (|det| ${d.toFixed(2)})` : null;
    },
    parts: (q, ctx) => {
      const L = legs(ctx), out = [], base = P.R.map(r => r - 3 - 0.15 - P.stack);
      out.push({ kind: 'arc', role: 'fixed-scapula', name: 'base bracket', pts: K.greatArc(L[1].b, L[0].b, base[1], base[0]).concat(K.greatArc(L[0].b, L[2].b, base[0], base[2])), r: 2.5 },
        { kind: 'arc', role: 'fixed-arm', name: 'deltoid saddle', pts: K.greatArc(L[0].W, L[1].W, P.sad, P.sad).concat(K.greatArc(L[1].W, L[2].W, P.sad, P.sad)), r: 4 });
      L.forEach((l, i) => {
        const R = P.R[i], end = dhi[i] + 17 / R / D, pts = [];
        for (let k = 0; k <= 40; k++) pts.push(V.scale(along(l.W, l.b, end * k / 40), R));
        const tan = V.unit(V.sub(along(l.W, l.b, q[i] + 1), l.b));
        out.push({ kind: 'hub', role: 'passive', name: `${nm[i]} swivel`, c: V.scale(l.b, base[i]), axis: l.b, r: P.hub_r, h: P.stack },
          { kind: 'carriage', role: 'active', name: `${nm[i]} guide (strut slide, active)`, c: V.scale(l.b, R + 2), x: tan, z: l.b, size: P.guide },
          { kind: 'arc', role: 'link', name: `${nm[i]} strut (tail past the guide)`, pts, r: 2.5 },
          { kind: 'hub', role: 'passive', name: `${nm[i]} hinge`, c: V.scale(l.W, P.sad + 3), axis: l.W, r: P.hub_r, h: R - P.sad - 3 });
      });
      const harm = ctx.armAxis, ng = P.neck_deg * D, Wl = L[1].W;
      const nk = V.unit(V.add(V.scale(Wl, Math.cos(ng)), V.scale(V.unit(V.reject(harm, Wl)), Math.sin(ng))));
      const cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(nk, harm)), 47);
      out.push({ kind: 'link', role: 'fixed-arm', name: 'BOTTOM stub', a: V.scale(nk, P.sad), b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 });
      return out;
    }
  });
})();
