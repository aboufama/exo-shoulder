/* insertion-cband-relay-4r (round 401 K1, judge pick 2): a KNEE-LESS plain O20 spherical 3R at the lead's J1 seat (back of the
 * shoulder / acromion top, bvec(95.39, 67.90)), J2 placed by psi2 -45 (a1 37.55, a2 67.34), J3 re-aimed to wdir(95, -8.2) on the
 * lateral cap (b3 0: the J3 line passes through GH), K welded (no knuckle, no drive). Member 3 = hub 3's lower plate + a ~93 mm
 * 12 x 3 Ti strap straight down the lateral arm to a roller carriage at s 0.30 (97.5 mm down the GH-elbow line). The carriage
 * rides an ARM-FIXED C-band (psi -28..+42 about the relay axis raxis(8.75, -90) through GH, fused into BOTTOM's cut end) and is
 * held on its zero dowel (psi -15) by a constant-force strip. When the arm leaves the plain dyad's window (th outside
 * [|a1 - a2| + 5, a1 + a2 - 5]) the arm turns the carriage to the LEAST phi in [0, PHI 45] at which the dyad closes (one-sided).
 * 4 counted joints (J1, J2, J3, J4 = the carriage), 0 passive joints, 0 passive translations. Hub heights are schematic
 * (the scored model wears the lead's fitted metal); the band / carriage are drawn at the race radius. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = { az1: 95.3929, el1: 67.8974, a1: 37.552, a2: 67.341, wd: 95.0, wa: -8.2, branch: -1, PHI: 45, margin: 5,
              ax: [0.1521, 0.9884, 0.0], s_mm: 97.5, psi0: -15, band: [-28, 42], Rb: 46, faces: [50.5, 62.5, 58.0],
              hub_r: 10, stack: 12.25 };
  const C3 = K.sph3r(K.bvec(P.az1, P.el1), K.wdir(P.wd, P.wa), P.a1, P.a2, P.branch);
  const ax = V.unit(P.ax), lat = K.wdir(90, 0), e = V.unit(V.reject(lat, ax)), f = V.cross(ax, e);
  const sAx = -Math.hypot(P.s_mm, P.s_mm * Math.tan(8.75 * D2R));          // band station on the axis (below GH)
  const dPsi = t => V.add(V.scale(e, Math.cos(t * D2R)), V.scale(f, Math.sin(t * D2R)));
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
    id: 'insertion-cband-relay-4r',
    name: 'Knee-less O20 3R (J3 re-aimed square) + one-sided relay on an arm-fixed C-band at the deltoid insertion (s 0.30)',
    dof: { active: 4, passive: 0 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'J2', 'J3', 'J4 relay phi (roller carriage on the C-band; CF strip on the zero dowel)'], qUnits: ['deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'deg'],
    solve: ctx => solve(ctx),
    residual: (q, ctx) => C3.residual(q.slice(0, 3), relayed(ctx, q[3])).concat([q[3] - phiUse(ctx)]),
    check: (q, ctx) => {
      if (phiOf(ctx) === null) return `J2 on its dowel and the carriage on its end dowel (PHI ${P.PHI}): the dyad cannot close`;
      const m = C3.margin(relayed(ctx, q[3]));
      if (m < P.margin - 1e-6) return `J2 within ${m.toFixed(1)} deg of its fold`;
      return null;
    },
    parts: (q, ctx) => {
      const c2 = relayed(ctx, q[3]), F = C3.fk(q.slice(0, 3), c2), Fh = P.faces, h = P.stack;
      const Hc = c2.H, arm = p => M.mulv(ctx.H, p), mem3 = p => M.mulv(Hc, p);
      const bandPts = []; for (let t = P.band[0]; t <= P.band[1] + 1e-9; t += 5) bandPts.push(arm(V.madd(V.scale(ax, sAx), dPsi(t), P.Rb)));
      const carC = mem3(V.madd(V.scale(ax, sAx), dPsi(P.psi0), P.Rb + 3)), carN = mem3(dPsi(P.psi0));
      const strapTop = V.scale(F.p3, Fh[2] - 1);
      const axW = M.mulv(ctx.H, ax);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base on the scapula handler (at the J1 hub ring)', c: V.scale(F.p1, Fh[0] - 3), z: F.p1, x: ctx.attach.scapDir([1, 0, 0]), size: [40, 30], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1 (O20, axis on a GH ray)', c: V.scale(F.p1, Fh[0]), axis: F.p1, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 1 (12 x 3 Ti, K welded: one bar)', u: F.p1, v: F.p2, r0: Fh[0] + 7, r1: Fh[1] + 2, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2 (O20; own-angle dowel stops at the 5-deg th margin)', c: V.scale(F.p2, Fh[1]), axis: F.p2, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 2 (12 x 3 Ti)', u: F.p2, v: F.p3, r0: Fh[1] + 9, r1: Fh[2] + 2, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3 (O20, re-aimed wdir(95, -8.2), b3 0)', c: V.scale(F.p3, Fh[2]), axis: F.p3, r: P.hub_r, h },
        { kind: 'link', role: 'link', name: 'member 3 strap (12 x 3 Ti, ~93 mm, hub 3 lower plate -> carriage)', a: strapTop, b: carC, r: 2 },
        { kind: 'plate', role: 'passive', name: 'J4 carriage (COUNTED 4th joint: 4 x MR63ZZ V-wheels on the band edges; CF strip to the zero dowel at psi -15, end dowel at +30)', c: carC, z: carN, x: axW, size: [16, 34], t: 2.5 },
        { kind: 'arc', role: 'fixed-arm', name: 'arm-fixed C-band (17-4PH race about the relay axis, psi -28..+42, on a 2D-contoured Ti saddle fused into BOTTOM)', pts: bandPts, r: 2 },
        { kind: 'link', role: 'fixed-arm', name: 'relay axis through GH (construction line)', a: V.scale(axW, 10), b: V.scale(axW, -150), r: 0.5 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff (BOTTOM, from s 0.30 to the elbow)', c: V.scale(ctx.armAxis, 155), axis: ctx.armAxis, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
