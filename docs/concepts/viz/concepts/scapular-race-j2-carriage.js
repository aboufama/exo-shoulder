/* scapular-race-j2-carriage - J1 is a RACE: a fixed arc rail on the scapula base, laid on the bony acromion / spine /
 * clavicle rim, a circle of angular radius gamma about a1 (through GH); its rolling carriage IS link 1 and carries the
 * J2 O20 hub, whose axis is the carriage's own direction from GH (alpha12 = gamma). One strap L2 (the only moving-frame
 * link) runs over the deltoid to J3, a posterolateral septum barrel on its own arm cuff (catalogue entry
 * scapular-race-j2-carriage; no bench model yet). Spherical 3R, axes concurrent at GH: 3 active, 0 passive (the
 * rollers only realise J1); closed form (KIN.sph3r). Spec geometry (bench frame): a1 = sdir(0, 20), gamma 50, rail
 * phi in [-115, 75] (phi 0 up, +90 posterior), J3 axis w = unit(armpt(150, 35, R_env + 9)) on the rest arm, alpha23 80,
 * branch +1; poses with the carriage within 8 deg of a rail end, or J2 within 8 deg of its fold, are not reachable (the
 * spec's precheck: a high-band, low-reach overhead specialist). Red-team check added: the race must stay on skin the
 * arm never enters (rail > 42 mm from the arm axis). Rail radius 64 mm and R_env 45 mm are schematic. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = K.D2R;
  const P = { lat: 0, lon: 20, gamma: 50, a23: 80, branch: 1, phi_lo: -115, phi_hi: 75, car_deg: 8, tri: 8, rho_r: 64,
              s3: 150, th3: 35, r_env: 45, barrel: [7, 24], car: [26, 22, 8], hub_r: 10, stack: 12.25, arm_r: 42 };
  const sdir = (lat, lon) => [-Math.cos(lat * D2R) * Math.sin(lon * D2R), Math.sin(lat * D2R), Math.cos(lat * D2R) * Math.cos(lon * D2R)];
  const e = V.unit(K.BODY.elbow), l = [0.004, 0.164, 0.986], bb = [-1, 0.023, 0];                     // rest-arm axes
  const armpt = (s, th, r) => V.add(V.scale(e, s), V.scale(V.add(V.scale(l, Math.cos(th * D2R)), V.scale(bb, Math.sin(th * D2R))), r));
  const a1 = V.unit(sdir(P.lat, P.lon)), m = V.unit(V.reject([0, 1, 0], a1)), n = V.cross(a1, m);
  const wRest = armpt(P.s3, P.th3, P.r_env + 9), wBand = M.mulv(M.T(K.BODY.rest_humerus), V.unit(wRest));   // band humerus frame
  const R3 = V.norm(armpt(P.s3, P.th3, P.r_env + 2));                                           // barrel's proximal end
  const C = K.sph3r(a1, wBand, P.gamma, P.a23, P.branch);
  /** smallest distance (mm) from the race to the arm axis (s >= 20 mm): the race must stay on skin the arm never enters */
  function raceToArm(ctx) {
    let best = 1e9;
    for (let ph = P.phi_lo; ph <= P.phi_hi; ph += 3) {
      const d = V.scale(V.add(V.scale(a1, Math.cos(P.gamma * D2R)), V.scale(V.add(V.scale(m, Math.cos(ph * D2R)), V.scale(n, Math.sin(ph * D2R))), Math.sin(P.gamma * D2R))), P.rho_r);
      const x = M.mulv(ctx.S, d), s = Math.max(20, V.dot(x, ctx.armAxis));
      best = Math.min(best, V.norm(V.sub(x, V.scale(ctx.armAxis, s))));
    }
    return best;
  }
  const phiOf = (q, ctx) => { const u2 = M.mulv(M.T(ctx.S), C.fk(q, ctx).p2); return Math.atan2(V.dot(u2, n), V.dot(u2, m)) / D2R; };

  K.register({
    id: 'scapular-race-j2-carriage',
    name: 'Scapular race (J1 rail on the rim, J2 on its carriage)',
    dof: { active: 3, passive: 0 },
    params: P,
    q0: ctx => C.solve(ctx),
    qNames: ['J1 carriage on the race', 'J2 hub on the carriage', 'J3 septum barrel'], qUnits: ['deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => C.solve(ctx),
    residual: (q, ctx) => C.residual(q, ctx),
    check: (q, ctx) => {
      const mg = C.margin(ctx);
      if (mg < 0) return 'J2 cannot close: the arm is out of the race\'s reach';
      if (mg < P.tri) return `J2 within ${mg.toFixed(0)} deg of its fold`;
      const ra = raceToArm(ctx);
      if (ra < P.arm_r) return `the arm runs into the race (rail ${ra.toFixed(0)} mm from the arm axis)`;
      const ph = phiOf(q, ctx);
      if (ph < P.phi_lo + P.car_deg || ph > P.phi_hi - P.car_deg) return 'carriage off the end of the race (J2 would leave the rim)';
      return null;
    },
    parts: (q, ctx) => {
      const f = C.fk(q, ctx), S = ctx.S, h = P.stack, ph = phiOf(q, ctx) * D2R;
      const tang = M.mulv(S, V.add(V.scale(m, -Math.sin(ph)), V.scale(n, Math.cos(ph))));
      const cuffC = M.mulv(ctx.Hb, V.scale(e, P.s3)), cuffAx = M.mulv(ctx.Hb, e);
      const mount = M.mulv(ctx.Hb, armpt(P.s3, P.th3, 47));
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base (scapula handler)', c: M.mulv(S, V.scale(sdir(25, 60), P.rho_r - 6)), z: M.mulv(S, sdir(25, 60)), x: M.mulv(S, [1, 0, 0]), size: [40, 30], t: 3 },
        { kind: 'rail', role: 'fixed-scapula', name: 'J1 race (rail on the bony rim)', c: M.mulv(S, V.scale(a1, P.rho_r * Math.cos(P.gamma * D2R))), axis: M.mulv(S, a1),
          ref: M.mulv(S, m), rho: P.rho_r * Math.sin(P.gamma * D2R), a0: P.phi_lo, a1: P.phi_hi, r: 3, w: 10 },
        { kind: 'carriage', role: 'active', name: 'J1 carriage (= link 1)', c: V.scale(f.p2, P.rho_r + 2), x: tang, z: f.p2, size: P.car },
        { kind: 'hub', role: 'active', name: 'J2 (O20 on the carriage)', c: V.scale(f.p2, P.rho_r + 6), axis: f.p2, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'L2 strap (the only moving link)', pts: K.greatArc(f.p2, f.p3, P.rho_r + 6 + h + 1, R3 + P.barrel[1] / 2), r: 3 },
        { kind: 'hub', role: 'active', name: 'J3 septum barrel', c: V.scale(f.p3, R3), axis: f.p3, r: P.barrel[0], h: P.barrel[1] },
        { kind: 'link', role: 'fixed-arm', name: 'barrel mount', a: mount, b: V.scale(f.p3, R3), r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'barrel cuff', c: cuffC, axis: cuffAx, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
