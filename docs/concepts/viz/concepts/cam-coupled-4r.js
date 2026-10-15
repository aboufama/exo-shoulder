/* cam-coupled-4r - a spherical 4R whose spare is scheduled by a pin-in-slot cam on the base (catalogue cam-coupled-4r,
 * models/cam-coupled-4r.py; modelling interrupted, no sweep yet: the model's defaults). The r13 4R axes with every
 * arc >= 35 deg; link 2 carries a short tail (tail_r 30 deg, straight back past J2) whose roller pin runs in a circular
 * slot on an S-fixed plate. The slot is the small circle through the pin at three key poses (rest / overhead / behind
 * the back) at the J1 angles `keys` (pin representation: azimuth of p2 about p1). Mobility 3 x 4 - 2 x 4 - 1 = 3:
 * J1, J3, J4 ACTIVE; J2, the pin's slide and its roll PASSIVE, set by the slot. Closed form = the model's IK: a 1-D
 * root scan of G(theta) = pi . n_s - cos beta_s over the J1 azimuth, bisection, root on the design's mode (sign of
 * dG/dtheta) nearest the previous frame. Joint values are measured from the rest pose. Hub faces are schematic. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const P = { az: 61.04, el: 57.77, a: [35.0, 56.13, 35.0], w: [84.08, -10.84], branch: -1, tail_r: 30, tail_phi: 180,
              keys: [-170, -170, 60], sigma: 1, pa_min: 0.25, hold_min: 0.1, sing: 10,
              faces: [55, 64, 70, 66], hub_r: 10, stack: 12.25, pin_r: 5, slot_w: 14, neck_deg: 25, cuff_at: 165 };
  const p1 = K.bvec(P.az, P.el), W0 = K.wdir(P.w[0], P.w[1]), e = V.unit(V.cross(p1, [0, 1, 0]));
  /** pin-representation state for J1 azimuth th (deg) and arm axis p4 (scapula frame) */
  function state(th, p4) {
    const p2 = K.onCone(p1, e, P.a[0], th), c = K.circInt(p2, P.a[1], p4, P.a[2], P.branch), p3 = c.p;
    const pin = K.onCone(p2, p3, P.tail_r, P.tail_phi);
    return { p2, p3, p4, pin, ok: c.ok };
  }
  const Qof = ctx => M.mul(M.T(ctx.S), ctx.H);
  // slot: small circle through the pin at the three key poses (KIN.KEYS rest, overhead, behind)
  const keyPose = k => K.KEYS.find(x => x.key === k).pose;
  const keyQ = ['rest', 'overhead', 'behind'].map(k => { const c = K.makeCtx(keyPose(k)); return Qof(c); });
  const Pk = keyQ.map((Q, i) => state(P.keys[i], M.mulv(Q, W0)).pin);
  let ns = V.unit(V.cross(V.sub(Pk[1], Pk[0]), V.sub(Pk[2], Pk[0]))), cb = V.dot(ns, Pk[0]);
  if (cb < 0) { ns = V.scale(ns, -1); cb = -cb; }
  const beta = Math.acos(cb) * K.R2D, sref = V.perp(ns);
  // home = the rest key configuration: axes u1..u4 and the chain end Qh
  const Qh = keyQ[0], H0 = state(P.keys[0], M.mulv(Qh, W0)), U = [p1, H0.p2, H0.p3, H0.p4];
  const pin0 = H0.pin;                                                    // pin in link 2 at home (scapula frame)
  const G = (th, p4) => { const s = state(th, p4); return { g: V.dot(s.pin, ns) - cb, s }; };

  /** joint values (deg, from home) of posed axes Pa = [p1..p4] and chain end Q */
  function angles(Pa, Q) {
    const q = []; let R = M.I3();
    for (let k = 0; k < 3; k++) { q.push(K.axisAngle(U[k], U[k + 1], M.mulv(M.T(R), Pa[k + 1]))); R = M.mul(R, M.rot(U[k], q[k])); }
    const v = V.perp(U[3]), RL = M.mul(M.mul(M.T(R), Q), M.T(Qh));
    q.push(K.axisAngle(U[3], v, M.mulv(RL, v))); return q;
  }
  function fk(q) {                                                         // scapula frame
    const Rs = [M.rot(U[0], q[0])]; for (let k = 1; k < 4; k++) Rs.push(M.mul(Rs[k - 1], M.rot(U[k], q[k])));
    return { p: [U[0], M.mulv(Rs[0], U[1]), M.mulv(Rs[1], U[2]), M.mulv(Rs[2], U[3])], pin: M.mulv(Rs[1], pin0), E: M.mul(Rs[3], Qh) };
  }
  const slotPsi = pin => K.axisAngle(ns, sref, pin);

  function solve(ctx, qPrev) {
    const Q = Qof(ctx), p4 = M.mulv(Q, W0);
    const thPrev = qPrev ? K.axisAngle(p1, e, M.mulv(M.rot(U[0], qPrev[0]), U[1])) : P.keys[0];
    let best = null, gPrev = G(-180, p4);
    for (let t = -179; t <= 180; t++) {
      const gc = G(t, p4);
      if (gPrev.s.ok && gc.s.ok && Math.sign(gPrev.g) !== Math.sign(gc.g) && Math.sign(gc.g - gPrev.g) === P.sigma) {
        let lo = t - 1, hi = t, glo = gPrev.g;
        for (let i = 0; i < 40; i++) { const m = (lo + hi) / 2, gm = G(m, p4).g; if (Math.sign(gm) === Math.sign(glo)) { lo = m; glo = gm; } else hi = m; }
        const r = (lo + hi) / 2, d = Math.abs(K.wrap180(r - thPrev));
        if (!best || d < best.d) best = { th: r, d };
      }
      gPrev = gc;
    }
    if (!best) return qPrev ? qPrev.slice() : [0, 0, 0, 0, 0];
    const s = state(best.th, p4);
    return angles([p1, s.p2, s.p3, s.p4], Q).concat([slotPsi(s.pin)]);
  }
  // slot cut: the pin's travel over the motion loop (+ the pin pad), computed once
  let cut = null;
  function slotCut() {
    if (cut) return cut;
    let q = null, lo = 1e9, hi = -1e9;
    for (const f of K.motion(120)) {
      const c = K.makeCtx(f.pose), fq = fk(q = solve(c, q));
      if (V.norm(M.rotErrDeg(M.mul(c.S, fq.E), c.H)) > 0.5) continue;      // only where the chain closes
      const ps = slotPsi(fq.pin); lo = Math.min(lo, ps); hi = Math.max(hi, ps);
    }
    const pad = (P.pin_r + 2) / ((P.faces[0] - 2) * Math.sin(beta * K.D2R)) * K.R2D;
    return (cut = lo > hi ? [-20, 20] : [lo - pad, hi + pad]);
  }

  K.register({
    id: 'cam-coupled-4r',
    name: 'Cam-scheduled 4R (pin-in-slot)',
    dof: { active: 3, passive: 3 },
    params: P,
    q0: ctx => solve(ctx, null),
    qNames: ['J1', 'J2 (passive, slot-scheduled)', 'J3', 'J4', 'pin along the slot (passive)'],
    qUnits: ['deg', 'deg', 'deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg', 'deg', 'deg'],
    solve,
    residual: (q, ctx) => {
      const f = fk(q);
      return M.rotErrDeg(M.mul(ctx.S, f.E), ctx.H).concat([V.angle(f.pin, ns) - beta, K.wrap180(slotPsi(f.pin) - q[4])]);
    },
    check: (q, ctx) => {
      const f = fk(q), p = f.p;
      const m = Math.min(K.foldMargin(p[0], p[2], P.a[0], P.a[1]), K.foldMargin(p[1], p[3], P.a[1], P.a[2]));
      if (m < 0) return 'the 4R cannot close on the slot here';
      if (m < P.sing) return `J2 / J3 within ${m.toFixed(0)} deg of a fold`;
      const nt = V.unit(V.reject(ns, f.pin)), t2 = V.cross(p[1], f.pin);
      const pa = Math.abs(V.dot(t2, nt)) / (V.norm(t2) || 1e-9);
      if (pa < P.pa_min) return `cam pressure angle: pin transmits ${pa.toFixed(2)} < ${P.pa_min}`;
      return null;
    },
    parts: (q, ctx) => {
      const f = fk(q), S = ctx.S, W = d => M.mulv(S, d), F = P.faces, h = P.stack;
      const p = f.p.map(W), pin = W(f.pin), harm = ctx.armAxis, ng = P.neck_deg * K.D2R;
      const nk = V.unit(V.add(V.scale(p[3], Math.cos(ng)), V.scale(V.unit(V.reject(harm, p[3])), Math.sin(ng))));
      const neckEnd = V.scale(nk, F[3] + 1), cuffC = V.scale(harm, P.cuff_at);
      const cuffTop = V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47), RS = F[0] - 2, [a0, a1] = slotCut();
      const nsW = W(ns), rho = RS * Math.sin(beta * K.D2R);
      return [
        { kind: 'plate', role: 'fixed-scapula', c: V.scale(p[0], F[0] - 3), z: p[0], x: W([1, 0, 0]), size: [46, 32], t: 3 },
        { kind: 'rail', role: 'fixed-scapula', name: 'cam slot (S-fixed plate)', c: V.scale(nsW, RS * Math.cos(beta * K.D2R)), axis: nsW,
          ref: W(sref), rho, a0, a1, r: 3, w: P.slot_w },
        { kind: 'hub', role: 'active', name: 'J1', c: V.scale(p[0], F[0]), axis: p[0], r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 1', u: p[0], v: p[1], r0: F[0] + 7, r1: F[1] + 2, r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'J2 (scheduled by the slot)', c: V.scale(p[1], F[1]), axis: p[1], r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 2', u: p[1], v: p[2], r0: F[1] + 9, r1: F[2] + 2, r: 2.5 },
        { kind: 'arc', role: 'link', name: 'link 2 tail', u: p[1], v: pin, r0: F[1] + 9, r1: RS + 6, r: 2.2 },
        { kind: 'hub', role: 'passive', name: 'roller pin in the slot', c: V.scale(pin, RS), axis: pin, r: P.pin_r, h: 6 },
        { kind: 'hub', role: 'active', name: 'J3', c: V.scale(p[2], F[2]), axis: p[2], r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 3', u: p[2], v: p[3], r0: F[2] + 9, r1: F[3] + 2, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J4 (arm hub)', c: V.scale(p[3], F[3]), axis: p[3], r: P.hub_r, h },
        { kind: 'arc', role: 'fixed-arm', name: 'neck', u: p[3], v: nk, r0: F[3] + 1, r1: F[3] + 1, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'neck to cuff', a: neckEnd, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
