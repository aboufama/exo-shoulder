/* coaxial-spm-scapula - co-axial spherical parallel manipulator on a scapula pole, Agile-Eye legs, all three drives in
 * ONE base hub (catalogue coaxial-spm-scapula, ideated; marked a duplicate of spm-coaxial-turret, whose code this reuses).
 * Base pole u = unit(-0.67, 0.56, -0.49) (scapula frame, over the supraspinatus / scapular spine): three concentric
 * thin-section rings about u (radii 9 / 15 / 21 mm, 6 mm tall), each ACTIVE (phi_1..3), rotation about u unlimited ->
 * three proximal 90 deg arcs (nested, stacked +4 mm per outer ring crossed) -> PASSIVE elbow R (axis v_i through GH) ->
 * three distal 90 deg arcs -> PASSIVE platform R (axis w_i through GH) on one arm plate across the anterior / top-lateral
 * / posterior deltoid. Spherical mobility 3: 3 active + 6 passive, every elbow set by its two-cone closure on a fixed
 * branch. Platform axes per the spec: three arm-fixed directions on the great circle perpendicular to e_p0 = unit(-0.3,
 * 0.75, -0.59) (rest frame): top-lateral and +-75 deg toward the anterior / posterior deltoid. Branches (-1, +1, +1) =
 * the best of the 8 x spread 60/75/90 on a loop screen (91 of 141 frames in range): the spec's main risk (tilts near 90
 * deg; legs crossing / sweeping the arm) is what turns the rest red. Kept out as spm-coaxial-turret: a leg within 8 deg
 * of its fold, the type-2 index |det| < 0.10 or flipped, elbows < 17 deg apart, a distal arc sweeping across the upper
 * arm. Levels schematic (turret 52 mm up u, elbows 66 mm, platform pins 58 mm). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D = K.D2R;
  const P = { A: [-0.67, 0.56, -0.49], ep: [-0.3, 0.75, -0.59], spread: 75, a1: 90, a2: 90, br: [-1, 1, 1], ring_r: [9, 15, 21],
              margin: 8, det_min: 0.10, el_sep: 17, turret: 52, ring_t: 6, lift: 4, rE: 66, rV: 58, pin_r: 7, pin_h: 8,
              neck_deg: 25, cuff_at: 165 };
  const A0 = V.unit(P.A), aref = V.perp(A0);
  // platform axes: three arm-fixed directions on the great circle perpendicular to e_p0 (rest frame = humerus frame at
  // plane = elev = axial = 0): top-lateral, and +-spread toward the anterior / posterior deltoid
  const Ep = V.unit(P.ep), tl = V.unit(V.reject([0, -0.35, 1], Ep)), sgA = M.mulv(M.rot(Ep, P.spread), tl)[0] > 0 ? 1 : -1;
  const Vh = [0, 1, -1].map(k => M.mulv(M.rot(Ep, sgA * k * P.spread), tl));          // top-lateral, anterior, posterior
  const Wc = Vh[0];
  function frame(ctx) {                                                                // scapula frame
    const Q = M.mul(M.T(ctx.S), ctx.H), Vs = Vh.map(v => M.mulv(Q, v));
    const legs = Vs.map((v, k) => { const c = K.circInt(A0, P.a1, v, P.a2, P.br[k]); return { v, e: c.p, ok: c.ok, th: V.angle(A0, v) }; });
    return { Vs, legs };
  }
  const elbow = (q, k) => K.onCone(A0, aref, P.a1, q[k]);
  function overArm(pts, ctx) {                                                         // lift samples above the upper arm
    return pts.map(p => { const s = V.dot(p, ctx.armAxis), d = V.norm(V.reject(p, ctx.armAxis));
      return s > 0 && s < 330 && d < 48 ? V.scale(V.unit(p), Math.min(130, 48 / Math.max(d / V.norm(p), 0.2))) : p; });
  }
  const crossesArm = (e, v, ctx) => K.greatArc(e, v, 1, 1, 24).some(d => V.angle(d, ctx.armAxis) < 22);
  const det3 = (a, b, c) => V.dot(a, V.cross(b, c));
  const typ2 = (E, Vs) => det3(...[0, 1, 2].map(k => V.unit(V.cross(E[k], Vs[k]))));
  const solve = ctx => frame(ctx).legs.map(l => K.axisAngle(A0, aref, l.e));
  const s0 = (() => { const c = K.makeCtx(K.KEYS[0].pose, 0), f = frame(c); return Math.sign(typ2(f.legs.map(l => l.e), f.Vs)) || 1; })();

  K.register({
    id: 'coaxial-spm-scapula',
    name: 'Co-axial SPM on a scapula pole (Agile-Eye legs, one base hub)',
    dof: { active: 3, passive: 6 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['ring 1 (inner)', 'ring 2', 'ring 3 (outer)'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => solve(ctx),
    residual: (q, ctx) => { const f = frame(ctx); return f.legs.map((l, k) => V.angle(elbow(q, k), l.v) - P.a2); },
    check: (q, ctx) => {
      const f = frame(ctx), lo = Math.abs(P.a1 - P.a2) + P.margin, hi = Math.min(P.a1 + P.a2, 360 - P.a1 - P.a2) - P.margin;
      for (let k = 0; k < 3; k++) {
        const l = f.legs[k]; if (!l.ok) return `leg ${k + 1} cannot reach the saddle`;
        if (l.th < lo || l.th > hi) return `leg ${k + 1} within ${P.margin} deg of its fold / stretch`;
      }
      const E = [0, 1, 2].map(k => elbow(q, k)), d = typ2(E, f.Vs);
      if (d * s0 < P.det_min) return d * s0 < 0 ? 'assembly mode flips (type-2 singularity crossed)' : 'near the type-2 singularity: the saddle goes loose';
      for (const [i, j] of [[0, 1], [0, 2], [1, 2]]) if (V.angle(E[i], E[j]) < P.el_sep) return `elbows ${i + 1} and ${j + 1} collide`;
      for (let k = 0; k < 3; k++) if (crossesArm(E[k], f.Vs[k], { armAxis: M.mulv(M.T(ctx.S), ctx.armAxis) })) return `distal strap ${k + 1} sweeps across the upper arm`;
      return null;
    },
    parts: (q, ctx) => {
      const f = frame(ctx), S = x => M.mulv(ctx.S, x), A = S(A0), ref = S(aref), h = P.turret, out = [];
      const ringTop = j => h + P.ring_t + (2 - j) * P.lift;                            // crank level: +lift per outer ring crossed
      out.push({ kind: 'ring', role: 'fixed-scapula', name: 'turret housing (scapula)', c: V.scale(A, h - 2), axis: A, ref, r: P.ring_r[2] + 5, t: 2.5 },
        { kind: 'plate', role: 'fixed-scapula', name: 'turret base on the handler', c: V.scale(A, h - 5), z: A, x: ref, size: [52, 52], t: 3 });
      for (let k = 0; k < 3; k++) {
        const e = S(elbow(q, k)), v = S(f.legs[k].v), rr = P.ring_r[k], lv = ringTop(k);
        const az = K.axisAngle(A, ref, e), root = V.add(V.scale(A, lv), V.scale(K.onCone(A, ref, 90, az), rr));
        out.push({ kind: 'ring', role: 'active', name: `ring ${k + 1} (O${Math.round(2 * rr)}, active)`, c: V.scale(A, h + P.ring_t / 2), axis: A, ref, r: rr, t: 1.8 },
          { kind: 'arc', role: 'link', name: `crank ${k + 1}`, pts: K.greatArc(V.unit(root), e, V.norm(root), P.rE + 2, 10), r: 2.2 },
          { kind: 'hub', role: 'passive', name: `elbow pin ${k + 1}`, c: V.scale(e, P.rE), axis: e, r: P.pin_r, h: P.pin_h },
          { kind: 'arc', role: 'link', name: `distal strap ${k + 1} (two-force)`, pts: overArm(K.greatArc(e, v, P.rE + 5, P.rV + 5, 24), ctx), r: 2.2 },
          { kind: 'hub', role: 'passive', name: `saddle pin ${k + 1}`, c: V.scale(v, P.rV), axis: v, r: P.pin_r, h: P.pin_h });
      }
      const Vw = f.legs.map(l => S(l.v)), rs = P.rV - 3, harm = ctx.armAxis, wc = V.unit(M.mulv(ctx.H, Wc)), ng = P.neck_deg * D;
      const nk = V.unit(V.add(V.scale(wc, Math.cos(ng)), V.scale(V.unit(V.reject(harm, wc)), Math.sin(ng)))), neckEnd = V.scale(nk, P.rV + 2);
      const cuffC = V.scale(harm, P.cuff_at);
      out.push({ kind: 'arc', role: 'fixed-arm', name: 'arm saddle (carries the 3 pins)', pts: K.greatArc(Vw[0], Vw[1], rs, rs, 8).concat(K.greatArc(Vw[1], Vw[2], rs, rs, 8), K.greatArc(Vw[2], Vw[0], rs, rs, 8)), r: 3.5 },
        { kind: 'arc', role: 'fixed-arm', name: 'neck', u: wc, v: nk, r0: rs, r1: P.rV + 2, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'neck to BOTTOM / cuff', a: neckEnd, b: V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47), r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 });
      return out;
    }
  });
})();
