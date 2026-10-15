/* lone-helix-humeral - a 2R POINTING chain over the top of the shoulder + a HELICAL, skin-profiled humeral-rotation rail
 * on the arm (catalogue entry lone-helix-humeral; no bench model yet). J1 hub on a1 = bvec(125, 45) (the 2R
 * singularity's home, anterior-superior), J2 hub on a2 = circ_int(a1, 90, u, 90, sigma): 90 deg off the humerus axis u,
 * so link 2 holds the arm's direction (not its twist) and runs down the lateral arm. J3 = a carriage on an ARM-FIXED
 * helix (a line of non-extension of the skin, BioSuit-style) spanning Psi = 150 deg around the arm: its station along
 * the arm s(psi) = s0 + p (psi - psi_c) and its radius r(psi) change with the angle, so humeral rotation runs the
 * carriage up / down the arm by the pitch. Two PASSIVE slides on link 2 (along u, radial) follow the helix: set by the
 * profile at the current J3 angle (closure), never free. 3 active + 2 passive. q = [q1, q2, psi, slide along, slide
 * radial]; closed form (residual: arm direction, carriage on the helix, slide values). Spec seeds (s0 90, p 0.3 mm/deg,
 * psi_c 0 = lateral, chi set so psi = psi_c at rest); the radius profile r(psi) is schematic (the model fits it on the
 * non-round arm skin + 2.5 mm). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const P = { az: 125, el: 45, a12: 90, sigma: -1, sing: 10, s0: 90, pitch: 0.3, Psi: 150, psi_c: 0, clear: 2.5, car: [24, 20, 9],
              R1: 54, R2: 62, hub_r: 10, stack: 12.25, ax_travel: 25, cuff_at: 165 };
  const a1L = K.bvec(P.az, P.el), D2R = K.D2R;
  const station = psi => P.s0 + P.pitch * (psi - P.psi_c);
  const radius = psi => 47 + 4 * Math.sin(psi * D2R) + 3 * Math.cos(2 * psi * D2R) + P.clear;   // schematic non-round arm
  const armDir = psi => [Math.sin(psi * D2R), 0, Math.cos(psi * D2R)];                           // arm frame, 0 lateral, +90 anterior
  const helixPt = (ctx, psi, dr) => M.mulv(ctx.H, V.add([0, -station(psi), 0], V.scale(armDir(psi), radius(psi) + (dr || 0))));
  const halfCar = (P.car[0] / 2) / 50 * K.R2D;
  let rMax = 0; for (let a = -P.Psi / 2; a <= P.Psi / 2; a += 5) rMax = Math.max(rMax, radius(P.psi_c + a));

  function pointer(ctx) {
    const A1 = M.mulv(ctx.S, a1L), u = ctx.armAxis, a2 = K.circInt(A1, P.a12, u, 90, P.sigma).p;
    return { A1, u, a2, e2: V.cross(u, a2) };
  }
  let CHI = null;                                   // carriage azimuth on link 2 (about u from a2): psi = psi_c at rest
  function chi() {
    if (CHI != null) return CHI;
    const ctx = K.makeCtx(K.KEYS[0].pose), f = pointer(ctx), d = M.mulv(ctx.H, armDir(P.psi_c));
    return (CHI = Math.atan2(V.dot(d, f.e2), V.dot(d, f.a2)) * K.R2D);
  }
  const carDir = (f, c) => V.add(V.scale(f.a2, Math.cos(c * D2R)), V.scale(f.e2, Math.sin(c * D2R)));
  function solve(ctx) {
    const f = pointer(ctx), d = carDir(f, chi());
    const psi = Math.atan2(V.dot(d, M.mulv(ctx.H, [1, 0, 0])), V.dot(d, M.mulv(ctx.H, [0, 0, 1]))) * K.R2D;
    return [K.axisAngle(f.A1, ctx.attach.scapDir([1, 0, 0]), f.a2), K.axisAngle(f.a2, f.A1, f.u), psi, station(psi), radius(psi)];
  }
  function fk(q, ctx) {
    const A1 = M.mulv(ctx.S, a1L), a2 = M.mulv(M.rot(A1, q[0]), V.unit(V.reject(ctx.attach.scapDir([1, 0, 0]), A1)));
    const u = M.mulv(M.rot(a2, q[1]), A1);
    return { A1, a2, u, e2: V.cross(u, a2) };
  }

  K.register({
    id: 'lone-helix-humeral',
    name: '2R pointer + helical humeral-rotation rail',
    dof: { active: 3, passive: 2 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'J2', 'J3 carriage on the helix (psi)', 'slide along the arm', 'slide radial'],
    qUnits: ['deg', 'deg', 'deg', 'mm', 'mm'], resUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg', 'mm', 'mm'],
    solve,
    residual: (q, ctx) => {
      const f = fk(q, ctx), d = carDir(f, chi()), h = M.mulv(ctx.H, armDir(q[2]));
      return V.scale(V.sub(f.u, ctx.armAxis), K.R2D).concat(V.scale(V.sub(d, h), K.R2D), [q[3] - station(q[2]), q[4] - radius(q[2])]);
    },
    check: (q, ctx) => {
      const f = pointer(ctx), g = V.angle(f.A1, f.u), lo = Math.abs(90 - P.a12) + P.sing, hi = 90 + P.a12 - P.sing;
      if (g < lo || g > hi) return `2R pointer within ${P.sing} deg of its singular cone`;
      if (Math.abs(K.wrap180(q[2] - P.psi_c)) > P.Psi / 2 - halfCar) return 'carriage past the end of the helix';
      return null;
    },
    parts: (q, ctx) => {
      const f = fk(q, ctx), c = chi(), d = carDir(f, c), psi = q[2], h = P.stack;
      const Rl = rMax + P.car[2] + 9, sEnd = P.s0 + P.ax_travel, l2 = [];                 // link 2: J2 hub -> strip at azimuth chi -> slide stage
      for (let i = 0; i <= 24; i++) {
        const s = sEnd * i / 24, az = c * Math.min(1, s / 35), R = P.R2 + h + 1 + (Rl - P.R2 - h - 1) * Math.min(1, s / 60);
        l2.push(V.madd(V.scale(f.u, s), carDir(f, az), R));
      }
      const rails = [];
      for (let i = 0; i <= 40; i++) rails.push(helixPt(ctx, P.psi_c - P.Psi / 2 + P.Psi * i / 40, 0));
      const carC = helixPt(ctx, psi, 4.5), carX = V.unit(V.sub(helixPt(ctx, psi + 2, 0), helixPt(ctx, psi - 2, 0)));
      const st = q[3], top = V.madd(V.scale(f.u, st), d, radius(psi) + P.car[2]);
      const axA = V.madd(V.scale(f.u, P.s0 - P.ax_travel), d, Rl - 3), axB = V.madd(V.scale(f.u, P.s0 + P.ax_travel), d, Rl - 3);
      const axAt = V.madd(V.scale(f.u, st), d, Rl - 3);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base (anterior-superior acromion)', c: V.scale(f.A1, P.R1 - 3), z: f.A1, x: ctx.attach.scapDir([1, 0, 0]), size: [40, 32], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1', c: V.scale(f.A1, P.R1), axis: f.A1, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 1', u: f.A1, v: f.a2, r0: P.R1 + 7, r1: P.R2 + 2, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2', c: V.scale(f.a2, P.R2), axis: f.a2, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 2 (pointing link down the lateral arm)', pts: l2, r: 3 },
        { kind: 'slider', role: 'passive', name: 'slide along the arm (set by the helix pitch)', a: axA, b: axB, at: axAt, z: d, size: [14, 14, 5] },
        { kind: 'slider', role: 'passive', name: 'slide radial (set by the helix radius)', a: axAt, b: top, at: top, z: V.unit(V.sub(axB, axA)), size: [10, 10, 4] },
        { kind: 'carriage', role: 'active', name: 'J3 carriage on the helix', c: carC, x: carX, z: d, size: P.car },
        { kind: 'arc', role: 'fixed-arm', name: 'helical rail (arm-fixed, 150 deg)', pts: rails, r: 2.5, w: 10 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: V.scale(ctx.armAxis, P.cuff_at), axis: ctx.armAxis, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
