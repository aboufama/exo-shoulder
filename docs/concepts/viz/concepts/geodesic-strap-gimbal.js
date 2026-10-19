/* geodesic-strap-gimbal - a 90/90 spherical 3R (a gimbal) whose middle joint J2 is a self-stowing STRAP between two
 * hubs (catalogue entry; not modelled yet, so the catalogue's model_spec is the source). J1 hub on the acromion top
 * (b = bvec(70, 35)), J3 hub on the anterolateral deltoid (W = wdir(55, 30)), the best hub-able pair (22.5 deg
 * singular margin). J2's axis p2 = unit(b x w) is perpendicular to both, so every point of link 2 on the great circle
 * G through b and w moves ALONG G when J2 turns: J2 is realised as the extension s = angle(b, w) of a 20 mm strap laid
 * on G, anchored to J1's rotor (link 1). Link 2 = a guide block pinching the strap (encoder roller) at s - s_c, a
 * constant-force spool beside it (tail wound in) and a short arm to J3's rotor. Passive: the spool turn (set by s) and
 * the guide block's radial slide (set by the strap's link-1-fixed radius profile r_S(s), here SCHEMATIC: 56 -> 63 mm
 * over the lateral shoulder). 3 ACTIVE + 2 PASSIVE; closed form (KIN.sph3r with a1 = a2 = 90, sigma +1). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const P = { b_az: 70, b_el: 35, w_d: 55, w_a: 30, sigma: 1, s_lo: 20, s_hi: 160, s_c: 20, s_rim: 7,
              F1: 52, F3: 60, strap_w: 20, r_spool: 9, slide: 14, hub_r: 10, stack: 12.25, neck_deg: 25, cuff_at: 165 };
  const C = K.sph3r(K.bvec(P.b_az, P.b_el), K.wdir(P.w_d, P.w_a), 90, 90, P.sigma);
  const th0 = V.angle(C.u1, C.u3);
  const sgn = Math.sign(V.angle(C.u1, M.mulv(M.rot(C.u2, 10), C.u3)) - th0);    // J2 turn -> strap extension
  const rS = s => 56 + 7 * (1 - Math.cos(Math.min(s, 160) * Math.PI / 160)) / 2;  // strap radius profile (link 1)
  const Mmount = 63 + 9;                                                          // guide mount on link 2: max r_S + 9
  /** deployed strap length (mm) from J1's rim to station s */
  const deployed = s => { let L = 0; const n = 24, ds = (s - P.s_rim) / n; for (let i = 0; i < n; i++) L += rS(P.s_rim + (i + 0.5) * ds) * ds * K.D2R; return L; };
  const spoolOf = s => -deployed(s - P.s_c) / P.r_spool * K.R2D, slideOf = s => Mmount - rS(s - P.s_c) - 9;
  const toSph = q => [q[0], sgn * (q[1] - th0), q[2]];
  const solve = ctx => { const qs = C.solve(ctx), s = th0 + sgn * qs[1]; return [qs[0], s, qs[2], spoolOf(s), slideOf(s)]; };

  K.register({
    id: 'geodesic-strap-gimbal',
    name: 'Geodesic strap gimbal (J2 = a strap)',
    dof: { active: 3, passive: 2 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'J2 (strap extension)', 'J3', 'spool turn', 'guide radial slide'], qUnits: ['deg', 'deg', 'deg', 'deg', 'mm'],
    resUnits: ['deg', 'deg', 'deg', 'deg', 'mm'],
    solve,
    residual: (q, ctx) => C.residual(toSph(q), ctx).concat([q[3] - spoolOf(q[1]), q[4] - slideOf(q[1])]),
    check: (q, ctx) => {
      if (q[1] < P.s_lo) return `hubs ${q[1].toFixed(0)} deg apart: gimbal lock zone`;
      if (q[1] > P.s_hi) return `hubs ${q[1].toFixed(0)} deg apart: strap past its length`;
      if (q[4] < 0 || q[4] > P.slide) return 'guide slide past its travel';
      return null;
    },
    parts: (q, ctx) => {
      const f = C.fk(toSph(q), ctx), s = q[1], h = P.stack, b = f.p1, p3 = f.p3, p2 = f.p2;
      const t = V.unit(V.reject(p3, b)), u = d => V.add(V.scale(b, Math.cos(d * K.D2R)), V.scale(t, Math.sin(d * K.D2R)));   // G
      const sg = s - P.s_c, dg = u(sg), tg = V.unit(V.sub(u(sg + 1), u(sg - 1))), n = 26;
      const strap = []; for (let i = 0; i <= n; i++) { const si = P.s_rim + (sg - P.s_rim) * i / n; strap.push(V.scale(u(si), rS(si))); }
      const spC = V.scale(u(s - P.s_c / 2), rS(sg) + 9 + 2);
      const harm = ctx.armAxis, ng = P.neck_deg * K.D2R;
      const nk = V.unit(V.add(V.scale(p3, Math.cos(ng)), V.scale(V.unit(V.reject(harm, p3)), Math.sin(ng))));
      const neckEnd = V.scale(nk, P.F3 + 1), cuffC = V.scale(harm, P.cuff_at);
      return [
        { kind: 'plate', role: 'fixed-scapula', c: V.scale(b, P.F1 - 3), z: b, x: ctx.attach.scapDir([1, 0, 0]), size: [40, 30], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1 (acromion top)', c: V.scale(b, P.F1), axis: b, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'J2 strap (link 1, deployed on G)', pts: strap, r: 1.6 },
        { kind: 'carriage', role: 'active', name: 'J2 guide block on the strap (encoder roller)', c: V.scale(dg, rS(sg) + 5), x: tg, z: dg, size: [24, 24, 9] },
        { kind: 'slider', role: 'passive', name: 'guide radial slide', a: V.scale(dg, Mmount - P.slide - 2), b: V.scale(dg, Mmount + 2),
          at: V.scale(dg, rS(sg) + 9), z: p2, size: [8, 8, 4] },
        { kind: 'hub', role: 'passive', name: 'constant-force spool (strap tail)', c: V.madd(spC, p2, -11), axis: p2, r: P.r_spool, h: 22 },
        { kind: 'arc', role: 'link', name: 'link 2 arm (spool -> J3 rotor)', u: u(s - P.s_c / 2), v: p3, r0: rS(sg) + 11, r1: P.F3 + h + 1, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3 (anterolateral deltoid)', c: V.scale(p3, P.F3), axis: p3, r: P.hub_r, h },
        { kind: 'arc', role: 'fixed-arm', name: 'arm end (BOTTOM)', u: p3, v: nk, r0: P.F3 + 1, r1: P.F3 + 1, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'neck to cuff', a: neckEnd, b: V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47), r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
