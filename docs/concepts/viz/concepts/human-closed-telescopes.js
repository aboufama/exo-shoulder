/* human-closed-telescopes - the 'artificial deltoid': human-closed 3-UPS (catalogue human-closed-telescopes,
 * models/human-closed-telescopes.py PARAMS; no sweep yet). Three S-fixed dome brackets (clavicle end bvec(150,35),
 * acromion bvec(85,70), scapular spine bvec(-15,40)) joined into one base part -> passive U-joint (2) -> a straight
 * single-stage telescope O10 / O8 (ACTIVE prismatic, its length sensed) -> passive arm-end joint (3) on studs around the
 * deltoid insertion (anterolateral -20 deg at 95 mm, on BOTTOM's bar at 85 mm, posterolateral +55 deg at 105 mm; humerus
 * frame, + posterior). No rotary hub at all and no exo joint at GH: the wearer's shoulder closes the loop.
 * Closed form L_k = |B_k - A_k|; the stroke is the model's single-stage limit [L_lo, 2 L_lo - 43] with L_lo picked to
 * cover the most loop frames - a strut past its stroke stops there and the gap to its stud is the reported residual.
 * 3 ACTIVE (strokes) + 15 PASSIVE (2 U + 3 arm-end per strut). Radii are schematic (dome skin + pad + joint). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = K.D2R;
  const P = { a: [[150, 35], [85, 70], [-15, 40]], b: [[95, -20], [85, 0], [105, 55]], anchorR: [66, 56, 71],
              studR: [63, 89.6, 61], det: 0.10, r_joint: 7 };
  const WB = [0, -0.0713, 0.9975], DB = [0, -0.9975, -0.0713], BAR_Z = 67.5;
  const names = ['anterior (clavicle)', 'middle (acromion)', 'posterior (spine)'];
  const A0 = P.a.map(([az, el], k) => V.scale(V.unit(K.bvec(az, el)), P.anchorR[k]));              // S frame
  const hPt = (s, th, r) => [-r * Math.sin(th * D2R), -s, r * Math.cos(th * D2R)];               // humerus frame (H)
  const B0 = P.b.map(([s, th], k) => hPt(s, th, P.studR[k]));
  const ends = ctx => ({ A: A0.map(a => M.mulv(ctx.S, a)), B: B0.map(b => M.mulv(ctx.H, b)) });
  // single-stage stroke per strut: L_lo picked to keep the most loop frames inside [L_lo, 2 L_lo - 43]
  const loop = K.motion(120).map(f => ends(K.makeCtx(f.pose, f.t)));
  const stroke = [0, 1, 2].map(k => {
    const L = loop.map(e => V.norm(V.sub(e.B[k], e.A[k]))); let best = [-1, 0];
    for (let lo = Math.min(...L) - 10; lo <= Math.max(...L); lo += 0.5) {
      const n = L.filter(x => x >= lo && x <= 2 * lo - 43).length; if (n > best[0]) best = [n, lo];
    }
    return [best[1], 2 * best[1] - 43];
  });
  const clampL = (k, x) => Math.max(stroke[k][0], Math.min(stroke[k][1], x));

  K.register({
    id: 'human-closed-telescopes',
    name: 'Human-closed telescopes (artificial deltoid, 3-UPS)',
    dof: { active: 3, passive: 15 },
    params: Object.assign({ stroke: stroke.map(s => s.map(x => +x.toFixed(1))) }, P),
    q0: ctx => { const e = ends(ctx); return [0, 1, 2].map(k => clampL(k, V.norm(V.sub(e.B[k], e.A[k])))); },
    qNames: names.map(n => `stroke ${n}`), qUnits: ['mm', 'mm', 'mm'], resUnits: ['mm', 'mm', 'mm'],
    solve: ctx => { const e = ends(ctx); return [0, 1, 2].map(k => clampL(k, V.norm(V.sub(e.B[k], e.A[k])))); },
    residual: (q, ctx) => { const e = ends(ctx); return [0, 1, 2].map(k => V.norm(V.sub(e.B[k], e.A[k])) - q[k]); },
    check: (q, ctx) => {
      const e = ends(ctx), m = [0, 1, 2].map(k => V.unit(V.cross(e.B[k], V.sub(e.B[k], e.A[k]))));
      if (Math.abs(V.dot(m[0], V.cross(m[1], m[2]))) < P.det) return 'struts near a line singularity (moments about GH coplanar)';
      return null;
    },
    parts: (q, ctx) => {
      const e = ends(ctx), S = ctx.S, out = [];
      const ad = A0.map(a => M.mulv(S, V.unit(a)));
      out.push({ kind: 'arc', role: 'fixed-scapula', name: 'bracket strap (acromion - clavicle)', u: ad[1], v: ad[0], r0: P.anchorR[1] - 9, r1: P.anchorR[0] - 9, r: 3 });
      out.push({ kind: 'arc', role: 'fixed-scapula', name: 'bracket strap (acromion - spine)', u: ad[1], v: ad[2], r0: P.anchorR[1] - 9, r1: P.anchorR[2] - 9, r: 3 });
      [0, 1, 2].forEach(k => {
        const A = e.A[k], dir = V.unit(V.sub(e.B[k], A)), tip = V.madd(A, dir, q[k]);
        out.push({ kind: 'plate', role: 'fixed-scapula', name: `bracket ${names[k]}`, c: V.madd(A, ad[k], -9), z: ad[k], x: S[0] ? M.mulv(S, [1, 0, 0]) : [1, 0, 0], size: [18, 18], t: 4 });
        out.push({ kind: 'hub', role: 'passive', name: `U-joint ${k + 1}`, c: V.madd(A, ad[k], -5), axis: ad[k], p0: A, r: P.r_joint, h: 10 });
        out.push({ kind: 'telescope', role: 'active', name: `telescope ${names[k]}`, a: A, b: tip, split: stroke[k][0] - 16, r0: 5, r1: 4 });
        out.push({ kind: 'point', role: 'passive', name: `arm-end joint ${k + 1}`, p: tip, r: P.r_joint });
        const foot = M.mulv(ctx.H, k === 1 ? hPt(P.b[k][0], 0, 82.6) : hPt(P.b[k][0], P.b[k][1], P.studR[k] - 11));
        out.push({ kind: 'link', role: 'fixed-arm', name: `stud ${k + 1}`, a: foot, b: e.B[k], r: 3.5 });
      });
      out.push({ kind: 'strap', role: 'fixed-arm', name: 'arm saddle', c: M.mulv(ctx.H, [0, -97, 0]), axis: ctx.armAxis,
                 ref: M.mulv(ctx.H, [0, 0, 1]), a0: -30, a1: 65, r: 54, w: 12 });
      out.push({ kind: 'link', role: 'fixed-arm', name: 'BOTTOM bar (user part)', a: M.mulv(ctx.Hb, V.add(V.scale(WB, BAR_Z + 3), V.scale(DB, 40))),
                 b: M.mulv(ctx.Hb, V.add(V.scale(WB, BAR_Z + 3), V.scale(DB, 170))), r: 4 });
      out.push({ kind: 'point', role: 'link', name: 'GH centre (the wearer\'s joint closes the loop)', p: [0, 0, 0], r: 4 });
      return out;
    }
  });
})();
