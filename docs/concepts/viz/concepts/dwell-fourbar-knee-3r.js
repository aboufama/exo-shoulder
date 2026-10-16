/* dwell-fourbar-knee-3r - the zero-passive spherical 3R (spine-parked seats, slim J2 / J3 hubs) with link 2 split at a
 * passive knee K and closed by a rocker C from link 1: a spherical Watt six-bar, every axis through GH, pins only
 * (docs/concepts/models/dwell-fourbar-knee-3r.py). In link 1's frame (u2 = z, u1 at arc a1 / azimuth 0) the crank s
 * (= q2) turns L2a: K = Rz(s) K0; Q = the two-circle closure of (P, r) and (K, k) on the rest branch; J3 is fixed in
 * L2b's (K, K -> Q) frame. Per frame: th = angle(J1, J3) -> s on the model's monotone arc (scanned on a 0.25 deg grid,
 * then secant-refined) -> the rotation taking (u1, u3(s)) to (J1, J3). 3 ACTIVE (J1, J2, J3) + 3 PASSIVE pins (P, K, Q)
 * set by the loop. Faces: the model's fitted levels at the best configuration (schematic radii). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D = Math.PI / 180;
  const P = { az: 102.7793, el: 65.3479, a1: 40.6794, a2: 73.7554, wd: 84.4912, wa: -12.7631, b: 40.12, chi: -0.49,
              gP: 17.8, phP: 14.48, k: 15.0, alq: -152.75, sref: 188.04, margin: 10, tq_lo: 30, tk_lo: 20,
              faces: { J1: 52, J2: 62, J3: 71, P: 56, K: 66, Q: 80 }, hub_r: { J1: 10, J2: 7.5, J3: 7.5 }, pin_r: 5, pin_h: 6.5,
              neck_deg: 25, cuff_at: 165 };
  const sdir = (arc, az) => [Math.sin(arc * D) * Math.cos(az * D), Math.sin(arc * D) * Math.sin(az * D), Math.cos(arc * D)];
  const rz = s => M.rot([0, 0, 1], s);
  const tang = (a, b) => V.unit(V.reject(b, a));
  const knee = (p2, p3, b, chi) => { const t = tang(p2, p3), nn = V.cross(p2, t);
    return V.add(V.scale(p2, Math.cos(b * D)), V.scale(V.add(V.scale(t, Math.cos(chi * D)), V.scale(nn, Math.sin(chi * D))), Math.sin(b * D))); };
  const frame = (a, b) => { const e = tang(a, b); return M.fromCols(a, e, V.cross(a, e)); };
  const u2 = [0, 0, 1], u1 = sdir(P.a1, 0), J30 = sdir(P.a2, 0), K0 = knee(u2, J30, P.b, P.chi), Q0 = knee(K0, J30, P.k, P.alq);
  const PP = sdir(P.gP, P.phP), R0 = rz(P.sref), r = V.angle(PP, M.mulv(R0, Q0));
  const sgn = Math.sign(V.dot(M.mulv(R0, Q0), V.cross(PP, M.mulv(R0, K0)))) || 1;
  const c3 = M.mulv(M.T(frame(K0, Q0)), J30);
  function loopAt(s) {
    const Ks = M.mulv(rz(s), K0), c = K.circInt(PP, r, Ks, P.k, sgn), Q = c.p;
    const u3 = M.mulv(frame(Ks, Q), c3);
    const tq = V.angle(tang(Q, Ks), tang(Q, PP)), tk = V.angle(tang(Ks, u2), tang(Ks, Q));
    const ok = c.ok && tq >= P.tq_lo && tq <= 180 - P.tq_lo && tk >= P.tk_lo && tk <= 180 - P.tk_lo;
    return { K: Ks, Q, u3, th: V.angle(u3, u1), ok };
  }
  // the monotone valid arc that holds the rest posture (same rule as the model): walk both ways from sref
  const st = 0.25, arc = [];
  (function () {
    const L0 = loopAt(P.sref); arc.push({ s: P.sref, th: L0.th });
    for (const dir of [1, -1]) {
      let prev = L0.th, sgnd = 0;
      for (let s = P.sref + dir * st; Math.abs(s - P.sref) < 360; s += dir * st) {
        const L = loopAt(s); if (!L.ok) break;
        const d = Math.sign(L.th - prev); if (sgnd && d && d !== sgnd) break; if (d) sgnd = d;
        prev = L.th; if (dir > 0) arc.push({ s, th: L.th }); else arc.unshift({ s, th: L.th });
      }
    }
  })();
  const ths = arc.map(a => a.th), lo = Math.min(...ths) + P.margin, hi = Math.max(...ths) - P.margin;
  const inc = arc[arc.length - 1].th > arc[0].th;
  function crank(th) {                                       // s on the arc for J1-J3 angle th (clamped), refined
    const A = inc ? arc : arc.slice().reverse(); let i = 0;
    while (i < A.length - 2 && A[i + 1].th < th) i++;
    const f = Math.min(1, Math.max(0, (th - A[i].th) / ((A[i + 1].th - A[i].th) || 1e-9)));
    let s = A[i].s + f * (A[i + 1].s - A[i].s);
    for (let it = 0; it < 3; it++) { const g = (loopAt(s + 0.01).th - loopAt(s - 0.01).th) / 0.02; if (Math.abs(g) < 1e-6) break; s -= (loopAt(s).th - th) / g; }
    return s;
  }
  const b1 = K.bvec(P.az, P.el), w3 = K.wdir(P.wd, P.wa);
  function fk(q, ctx) {
    const p1 = M.mulv(ctx.S, b1), p3 = M.mulv(M.mul(M.T(ctx.S), ctx.H), w3), L = loopAt(q[1]);
    // world: R takes link 1's frame to the world with u1 -> p1 rotated by q1 about p1 from the closure posture
    const Rc = M.mul(frame(p1, M.mulv(ctx.S, p3)), M.T(frame(u1, L.u3)));
    const R = M.mul(M.rot(p1, q[0]), Rc);
    const W = v => M.mulv(R, v);
    return { p1, p2: W(u2), P: W(PP), K: W(L.K), Q: W(L.Q), u3: W(L.u3), p3w: M.mulv(ctx.H, w3), L };
  }
  K.register({
    id: 'dwell-fourbar-knee-3r',
    name: 'Dwell four-bar knee 3R (Watt six-bar)',
    dof: { active: 3, passive: 3 },
    params: P,
    q0: [0, P.sref, 0],
    qNames: ['J1 offset', 'J2 crank s', 'J3'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg'],
    solve: (ctx) => { const p1 = M.mulv(ctx.S, b1), p3 = M.mulv(ctx.H, w3); return [0, crank(V.angle(p1, p3)), 0]; },
    residual: (q, ctx) => { const f = fk(q, ctx); return [V.angle(f.u3, f.p3w), V.angle(f.p1, M.mulv(ctx.S, b1))]; },
    check: (q, ctx) => {
      const th = V.angle(M.mulv(ctx.S, b1), M.mulv(ctx.H, w3));
      if (th < lo) return `J1-J3 angle ${th.toFixed(0)} deg below the loop's window (${lo.toFixed(0)})`;
      if (th > hi) return `J1-J3 angle ${th.toFixed(0)} deg above the loop's window (${hi.toFixed(0)})`;
      return null;
    },
    parts: (q, ctx) => {
      const f = fk(q, ctx), F = P.faces, h = 12.25, ph = P.pin_h, harm = ctx.armAxis, ng = P.neck_deg * D;
      const nk = V.unit(V.add(V.scale(f.p3w, Math.cos(ng)), V.scale(V.unit(V.reject(harm, f.p3w)), Math.sin(ng))));
      const neckEnd = V.scale(nk, F.J3 + 1), cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base pad (handler)', c: V.scale(f.p1, F.J1 - 3), z: f.p1, x: ctx.attach.scapDir([1, 0, 0]), size: [40, 28], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1', c: V.scale(f.p1, F.J1), axis: f.p1, r: P.hub_r.J1, h },
        { kind: 'arc', role: 'link', name: 'link 1', u: f.p1, v: f.p2, r0: F.J1 + 3, r1: F.J2 + 1.5, r: 2.5 },
        { kind: 'arc', role: 'link', name: 'link 1 plate to P', u: f.p2, v: f.P, r0: F.J2 + 1.5, r1: F.P + 1.5, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2', c: V.scale(f.p2, F.J2), axis: f.p2, r: P.hub_r.J2, h },
        { kind: 'arc', role: 'link', name: 'L2a', u: f.p2, v: f.K, r0: F.J2 + 4.5, r1: F.K + 1.5, r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'knee K', c: V.scale(f.K, F.K), axis: f.K, r: P.pin_r, h: ph },
        { kind: 'hub', role: 'passive', name: 'pin P', c: V.scale(f.P, F.P), axis: f.P, r: P.pin_r, h: ph },
        { kind: 'arc', role: 'link', name: 'rocker C', u: f.P, v: f.Q, r0: F.P + 4.5, r1: F.Q + 1.5, r: 2.0 },
        { kind: 'hub', role: 'passive', name: 'pin Q', c: V.scale(f.Q, F.Q), axis: f.Q, r: P.pin_r, h: ph },
        { kind: 'arc', role: 'link', name: 'L2b to J3', u: f.K, v: f.p3w, r0: F.K + 4.5, r1: F.J3 + 4.5, r: 2.5 },
        { kind: 'arc', role: 'link', name: 'L2b tail to Q', u: f.K, v: f.Q, r0: F.K + 4.5, r1: F.Q + 4.5, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3', c: V.scale(f.p3w, F.J3), axis: f.p3w, r: P.hub_r.J3, h },
        { kind: 'arc', role: 'fixed-arm', name: 'neck', u: f.p3w, v: nk, r0: F.J3 + 1, r1: F.J3 + 1, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'neck to cuff', a: neckEnd, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
