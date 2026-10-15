/* risley-turret - J1 and J2 as two overlapping FLAT RING BEARINGS on the scapula top cap (Risley-prism / tilting
 * turntable pair), one strap down to an O20 hub on the lateral deltoid (docs/concepts/risley-turret.md,
 * models/risley-turret.py). Spherical 3R with a short first link: b fixed in the scapula, W fixed in the humerus, p2 by
 * the two-circle closure on branch -1; 3 active, 0 passive. Shown: the two-ring turret of the sweep (k62, gap 75.79:
 * b = bvec(90, 75), W0 = wdir(71.38, 4.78), A1 45, A2 75, rings r 15-24 x 8, ring 1 at 48 mm, ring 2 at 82.5 mm). The
 * best subtype (k42, gap 63.17) keeps ring 1 and swaps ring 2 for an O20 hub: set P.j2hub = 1. L1 is a 14 x 3 bridge
 * strap between lugs on J1's upper race and J2's lower race (the races share no bolting lens, measured); link 2 leaves
 * a lug on ring 2's outer wall toward W. J3 face 72 mm (schematic: the model fits it). Closed form (KIN.sph3r). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V;
  const P = { az: 90, el: 75, wd: 71.38, wa: 4.78, a1: 45, a2: 75, sigma: -1, margin: 5, r_in: 15, r_out: 24, ring_h: 8,
              h1: 48, h2: 82.5, F3: 72, hub_r: 10, stack: 12.25, j2hub: 0, neck_deg: 25, cuff_at: 165 };
  const C = K.sph3r(K.bvec(P.az, P.el), K.wdir(P.wd, P.wa), P.a1, P.a2, P.sigma);
  const rm = 0.5 * (P.r_in + P.r_out);
  // lug on a ring about axis k at axial level h, at its outer wall toward direction d
  const lug = (k, h, d, r) => V.madd(V.scale(k, h), V.unit(V.reject(d, k)), r);

  K.register({
    id: 'risley-turret',
    name: 'Risley turret (two flat rings on the scapula top)',
    dof: { active: 3, passive: 0 },
    params: P,
    q0: ctx => C.solve(ctx),
    qNames: ['J1 ring', 'J2 ring', 'J3'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => C.solve(ctx),
    residual: (q, ctx) => C.residual(q, ctx),
    check: (q, ctx) => {
      const m = C.margin(ctx);
      if (m < 0) return 'no closure: angle(b, W) outside the band [|A1 - A2|, A1 + A2]';
      if (m < P.margin) return `J2 within ${m.toFixed(0)} deg of its fold`;
      return null;
    },
    parts: (q, ctx) => {
      const f = C.fk(q, ctx), h = P.stack, harm = ctx.armAxis;
      const r2 = P.j2hub ? P.hub_r : P.r_out, h2 = P.j2hub ? P.h2 - 10.5 : P.h2;
      const ring2 = P.j2hub
        ? { kind: 'hub', role: 'active', name: 'J2 hub (k42 subtype)', c: V.scale(f.p2, h2), axis: f.p2, r: P.hub_r, h }
        : { kind: 'ring', role: 'active', name: 'J2 ring', c: V.scale(f.p2, h2 + P.ring_h / 2), axis: f.p2, r: rm, w: P.r_out - P.r_in, t: P.ring_h };
      const bridgeA = lug(f.p1, P.h1 + P.ring_h * 0.75, f.p2, P.r_out + 2);          // J1 upper race, toward p2
      const bridgeB = lug(f.p2, h2 + 2, f.p1, r2 + 2);                               // J2 lower race, toward b
      const l2From = lug(f.p2, h2 + (P.j2hub ? h : P.ring_h / 2), f.p3, r2 + 2);     // J2 upper race lug, toward W
      const ng = P.neck_deg * K.D2R;
      const nk = V.unit(V.add(V.scale(f.p3, Math.cos(ng)), V.scale(V.unit(V.reject(harm, f.p3)), Math.sin(ng))));
      const neckEnd = V.scale(nk, P.F3 + 1), cuffC = V.scale(harm, P.cuff_at);
      const cuffTop = V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base (J1 lower race)', c: V.scale(f.p1, P.h1 - 2), z: f.p1, x: ctx.attach.scapDir([1, 0, 0]), size: [56, 56], t: 2 },
        { kind: 'ring', role: 'active', name: 'J1 ring', c: V.scale(f.p1, P.h1 + P.ring_h / 2), axis: f.p1, r: rm, w: P.r_out - P.r_in, t: P.ring_h },
        { kind: 'link', role: 'link', name: 'L1 bridge (J1 upper race to J2 lower race)', a: bridgeA, b: bridgeB, r: 3 },
        ring2,
        { kind: 'arc', role: 'link', name: 'link 2 (ring-2 lug to J3)', pts: K.greatArc(l2From, f.p3, V.norm(l2From), P.F3 + h + 1), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3', c: V.scale(f.p3, P.F3), axis: f.p3, r: P.hub_r, h },
        { kind: 'arc', role: 'fixed-arm', name: 'neck', u: f.p3, v: nk, r0: P.F3 + 1, r1: P.F3 + 1, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'neck to cuff', a: neckEnd, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
