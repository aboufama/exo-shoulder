/* kfree-o20pin-highexit-relay-4r (round 401 K1, judge pick 3, lens B): a KNEE-LESS plain O20 spherical 3R at the lead's J1 seat
 * (back of the shoulder / acromion top, bvec(95.39, 67.90)), J2 placed by psi2 -14 (a1 37.55, a2 64.56), J3 on a GH ray at the
 * champion seat wdir(77.25, -8.2) (b3 0), K welded (no knuckle, no drive). Member 3 = hub 3's lower plate + ONE bent 10 x 3 Ti
 * bar forward and down over the anterolateral deltoid to a FOURTH O20 v5 stack R4 whose axis is the GH-through line wdir(55, 45):
 * R4 sits where that line leaves the arm (max skin exit + 2 mm) and its lower plate is carried by BOTTOM through a 10 x 3 Ti lug.
 * R4 is the counted 4th joint, one-sided [0, PHI 75]: a clock spring holds member 3 on its zero dowel; when the arm leaves the
 * plain dyad's window (th outside [|a1 - a2| + 5, a1 + a2 - 5]) the arm turns member 3 about R4 to the LEAST phi at which the
 * dyad closes. 4 counted joints (J1, J2, J3, R4), 0 passive joints, 0 passive translations. Hub heights are schematic (the
 * scored model wears the lead's fitted metal); R4 is drawn at the measured exit radius. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const P = { az1: 95.3929, el1: 67.8974, a1: 37.552, a2: 64.556, wd: 77.25, wa: -8.2, branch: -1, PHI: 75, margin: 5,
              ax: [-0.5792, 0.5736, -0.5792], rB: 81.0, faces: [50.5, 62.5, 67.0], hub_r: 10, stack: 12.25 };
  const C3 = K.sph3r(K.bvec(P.az1, P.el1), K.wdir(P.wd, P.wa), P.a1, P.a2, P.branch);
  const ax = V.unit(P.ax), exitDir = V.scale(ax, -1);                     // R4 sits on -ax = wdir(55, 45), the anterolateral exit
  const relayed = (ctx, ph) => Object.assign({}, ctx, { H: M.mul(ctx.H, M.rot(ax, ph)) });
  const inWin = c => C3.margin(c) >= P.margin;
  function phiOf(ctx) {
    if (ctx._rphi !== undefined) return ctx._rphi;
    let ph = null;
    if (inWin(ctx)) ph = 0;
    else {
      for (let k = 1; k <= P.PHI + 1e-9; k += 1) { if (inWin(relayed(ctx, k))) { ph = k; break; } }
      if (ph !== null) { let lo = ph - 1, hi = ph; for (let i = 0; i < 6; i++) { const m = (lo + hi) / 2; if (inWin(relayed(ctx, m))) hi = m; else lo = m; } ph = hi; }
    }
    ctx._rphi = ph; return ph;
  }
  const phiUse = ctx => { const p = phiOf(ctx); return p === null ? P.PHI : p; };
  function solve(ctx) { return C3.solve(relayed(ctx, phiUse(ctx))).concat([phiUse(ctx)]); }
  K.register({
    id: 'kfree-o20pin-highexit-relay-4r',
    name: 'Knee-less O20 3R + O20 pin relay R4 on the GH-through line wdir(55, 45) at the anterolateral arm exit',
    dof: { active: 4, passive: 0 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'J2', 'J3', 'R4 relay phi (member 3 about the GH-through line; clock spring on the zero dowel)'], qUnits: ['deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'deg'],
    solve: ctx => solve(ctx),
    residual: (q, ctx) => C3.residual(q.slice(0, 3), relayed(ctx, q[3])).concat([q[3] - phiUse(ctx)]),
    check: (q, ctx) => {
      if (phiOf(ctx) === null) return `J2 on its dowel and member 3 on R4's end dowel (PHI ${P.PHI}): the dyad cannot close`;
      const m = C3.margin(relayed(ctx, q[3]));
      if (m < P.margin - 1e-6) return `J2 within ${m.toFixed(1)} deg of its fold`;
      return null;
    },
    parts: (q, ctx) => {
      const c2 = relayed(ctx, q[3]), F = C3.fk(q.slice(0, 3), c2), Fh = P.faces, h = P.stack;
      const exW = M.mulv(ctx.H, exitDir);                                // the line is fixed in the arm (and in member 3)
      const r4c = V.scale(exW, P.rB), r4low = V.scale(exW, P.rB + 1.5);
      const lugA = M.mulv(ctx.H, V.scale(K.wdir(35, 20), 70));            // BOTTOM's bar top (schematic)
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base on the scapula handler (at the J1 hub ring)', c: V.scale(F.p1, Fh[0] - 3), z: F.p1, x: ctx.attach.scapDir([1, 0, 0]), size: [40, 30], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1 (O20, axis on a GH ray)', c: V.scale(F.p1, Fh[0]), axis: F.p1, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 1 (12 x 3 Ti, K welded: one bar)', u: F.p1, v: F.p2, r0: Fh[0] + 7, r1: Fh[1] + 2, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2 (O20; own-angle dowel stops at the 5-deg th margin)', c: V.scale(F.p2, Fh[1]), axis: F.p2, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 2 (12 x 3 Ti)', u: F.p2, v: F.p3, r0: Fh[1] + 9, r1: Fh[2] + 2, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3 (O20 on a GH ray, wdir(77.25, -8.2), b3 0)', c: V.scale(F.p3, Fh[2]), axis: F.p3, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'member 3 bar (10 x 3 Ti, hub 3 lower plate -> R4 crown plate)', u: F.p3, v: exW, r0: Fh[2] - 3, r1: P.rB + h - 1.5, r: 2 },
        { kind: 'hub', role: 'passive', name: 'R4 relay (COUNTED 4th joint: O20 v5 stack on an MR117-2RS pair, axis = the GH-through line wdir(55, 45); clock spring to the zero dowel, PHI 75 dowel on its own angle)', c: r4c, axis: exW, r: P.hub_r, h },
        { kind: 'link', role: 'fixed-arm', name: 'lug (10 x 3 Ti, part of BOTTOM) -> R4 lower plate', a: lugA, b: r4low, r: 2 },
        { kind: 'link', role: 'fixed-arm', name: 'relay axis through GH (construction line)', a: V.scale(exW, -10), b: V.scale(exW, P.rB + 30), r: 0.5 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff (BOTTOM)', c: V.scale(ctx.armAxis, 150), axis: ctx.armAxis, r: 47, w: 30 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
