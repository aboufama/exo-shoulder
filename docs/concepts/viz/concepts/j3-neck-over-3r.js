/* j3-neck-over-3r - the INVERTED J3 STACK screened as the J3 side of the spring-knuckle chain (round-6 lens j3-side-band;
 * bench model docs/concepts/models/j3-neck-over-3r.py on minarc variant A's kit-rule model). A plain spherical chain,
 * every axis through GH: J1 (O20, active, scapula) -> link 1a -> K (O20, PASSIVE, clock spring onto stop A, cap +6 mm)
 * -> link 1b -> J2 (O20, active, dowel-in-slot stop on its own angle q2) -> link 2 -> J3 (O20, active, humerus-fixed axis)
 * -> member 3. THE CHANGE: at hub 3, link 2 is the LOWER (face) member and member 3 (cap plate + K7 neck) the UPPER one,
 * the neck bridging over link 2's swept zone to BOTTOM's bar. While th = angle(J1, J3) stays in [thLo, thHi] (>= 5 deg of
 * J1-J3 fold margin, kit rule) K rests on stop A (a rigid 3R); past it J2 sits on its q2 stop and the arm opens K to the
 * smallest J1-J2 arc that closes (<= stop B). Levels and seats: the model's fit on Bench(60,160) at LA1 (lay 1).
 * Red = K would pass stop B / the chain cannot close. 0 passive translations, 1 passive rotation (K). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az": 100.6785, "el": 65.4034, "wd": 46.1583, "wa": -6.1871, "a1": 43.8793, "a2": 71.1868, "b1": 30.6983, "b2": 56.392, "a1max": 70.3202, "smhi": 6.0944, "smlo": 8.9158, "sigma": -1.0, "sK": -1.0, "q": 0.9694, "nw": 14.0, "lay": 1.0, "capK": 6.0};
  const G = {"F": [51.0, 55.0, 63.6, 105.0], "lv1a": [54.1, 54.1, 54.1, 54.1, 50.1, 48.1, 50.9, 55.0, 55.0, 55.0, 55.0], "lv1b": [59.0, 59.0, 59.0, 52.7, 53.3, 54.5, 55.8, 57.2, 63.6, 63.6, 63.6], "lv2": [66.8, 66.8, 67.3, 74.7, 86.3, 97.6, 104.0, 105.2, 103.4, 105.0, 105.0], "lvn": [108.2, 108.2, 108.2, 108.2, 108.2, 108.2, 108.2, 108.5, 109.5, 110.6, 111.7], "thLo": 36.223, "thHi": 108.972};
  const u1 = K.bvec(P.az, P.el), u3 = K.wdir(P.wd, P.wa), sg = P.sigma >= 0 ? 1 : -1, sK = P.sK >= 0 ? 1 : -1;
  const WB = [0, -0.0713, 0.9975], DB = [0, -0.9975, -0.0713], BAR0 = V.add(V.scale(WB, 67.5), V.scale(DB, 40));
  /** J2's own angle (deg) of the chain at J1-J3 angle th and J1-J2 arc a1e (canonical frame; = the model's _q2_of) */
  function q2of(th, a1e) {
    const P1 = [0, 0, 1], P3 = [Math.sin(th * D2R), 0, Math.cos(th * D2R)];
    const c2 = K.circInt(P1, a1e, P3, P.a2, sg), cK = K.circInt(P1, P.b1, c2.p, P.b2, sK);
    return { q: K.axisAngle(c2.p, cK.p, P3), ok: c2.ok && cK.ok };
  }
  const thLo = G.thLo, thHi = G.thHi, q2sHi = q2of(thHi, P.a1).q, q2sLo = q2of(thLo, P.a1).q;
  /** the min-arc law with the physical q2 stop -> {a1e, state, ok} */
  function law(th) {
    if (th >= thLo && th <= thHi) return { a1e: P.a1, state: 0, ok: true };
    const state = th > thHi ? 1 : -1, q2s = state === 1 ? q2sHi : q2sLo, f = x => K.wrap180(q2of(th, x).q - q2s);
    let prev = P.a1, fp = f(prev), vp = q2of(th, prev).ok;
    for (let x = P.a1 + 0.25; x <= P.a1max + 1e-9; x += 0.25) {
      const fx = f(x), vx = q2of(th, x).ok;
      if (vp && vx && Math.sign(fx) !== Math.sign(fp) && Math.abs(fx - fp) < 90) {
        let A = prev, B = x, fa = fp;
        for (let i = 0; i < 14; i++) { const m = 0.5 * (A + B), fm = f(m); if (Math.sign(fm) === Math.sign(fa)) { A = m; fa = fm; } else B = m; }
        return { a1e: B, state, ok: true };
      }
      prev = x; fp = fx; vp = vx;
    }
    return { a1e: P.a1max, state, ok: false };
  }
  const Qof = ctx => M.mul(M.T(ctx.S), ctx.H);
  const thHome = V.angle(u1, u3), home = law(thHome);
  const u2 = K.circInt(u1, home.a1e, u3, P.a2, sg).p, uK = K.circInt(u1, P.b1, u2, P.b2, sK).p, v3 = V.perp(u3);
  function ik(ctx) {
    const Q = Qof(ctx), w = M.mulv(Q, u3), th = V.angle(u1, w), L = law(th);
    const p2 = K.circInt(u1, L.a1e, w, P.a2, sg).p, pK = K.circInt(u1, P.b1, p2, P.b2, sK).p;
    const q1 = K.axisAngle(u1, uK, pK), R1 = M.rot(u1, q1);
    const dK = K.axisAngle(uK, u2, M.mulv(M.T(R1), p2)), R1b = M.mul(R1, M.rot(uK, dK));
    const q2 = K.axisAngle(u2, u3, M.mulv(M.T(R1b), w)), R12 = M.mul(R1b, M.rot(u2, q2));
    const q3 = K.axisAngle(u3, v3, M.mulv(M.mul(M.T(R12), Q), v3));
    return { q: [q1, dK, q2, q3], L, th };
  }
  function fk(q, ctx) {
    const R1 = M.rot(u1, q[0]), R1b = M.mul(R1, M.rot(uK, q[1])), R12 = M.mul(R1b, M.rot(u2, q[2])), E = M.mul(R12, M.rot(u3, q[3]));
    const W = v => M.mulv(ctx.S, v);
    return { p1: W(u1), pK: W(M.mulv(R1, uK)), p2: W(M.mulv(R1b, u2)), p3: W(M.mulv(R12, u3)), R: M.mul(ctx.S, E) };
  }
  /** polyline on the great circle u -> v whose radius follows the station levels lv (+ dz) */
  function profArc(u, v, lv, dz) {
    const n = 24, out = [], g = K.greatArc(u, v, 1, 1, n);
    for (let i = 0; i <= n; i++) {
      const s = i / n * (lv.length - 1), j = Math.min(lv.length - 2, Math.floor(s)), r = lv[j] + (lv[j + 1] - lv[j]) * (s - j);
      out.push(V.scale(V.unit(g[i]), r + dz));
    }
    return out;
  }
  K.register({
    id: 'j3-neck-over-3r',
    name: 'Inverted J3 stack (neck over link 2) on the spring-knuckle chain',
    dof: { active: 3, passive: 1 },
    params: P,
    q0: ctx => ik(ctx).q,
    qNames: ['J1', 'K (passive, spring + stops)', 'J2', 'J3'], qUnits: ['deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => ik(ctx).q,
    residual: (q, ctx) => M.rotErrDeg(fk(q, ctx).R, ctx.H),
    check: (q, ctx) => {
      const s = ik(ctx);
      if (!s.L.ok) return `J2 on its q2 stop: K would pass stop B (a1max ${P.a1max.toFixed(1)} deg)`;
      return null;
    },
    parts: (q, ctx) => {
      const f = fk(q, ctx), F = G.F, h = 12.25, st = 3.15;
      const harm = ctx.armAxis, bar0 = M.mulv(ctx.Hb, BAR0), barDn = M.mulv(ctx.Hb, DB);
      const neck = profArc(f.p3, bar0, G.lvn, 3), neckEnd = neck[neck.length - 1];
      const cuffC = V.scale(harm, 165), cuffTop = V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47);
      const barEnd = V.madd(neckEnd, barDn, Math.max(20, V.dot(V.sub(cuffTop, neckEnd), barDn)));
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base (scapula handler, directly at the J1 hub ring)', c: V.scale(f.p1, F[0] - 3), z: f.p1, x: ctx.attach.scapDir([1, 0, 0]), size: [40, 30], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1 (O20, axis on a GH ray)', c: V.scale(f.p1, F[0]), axis: f.p1, r: 10, h },
        { kind: 'arc', role: 'link', name: 'link 1a (12 x 3 Ti, J1 -> K)', pts: profArc(f.p1, f.pK, G.lv1a, 1.5), r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'K (O20, passive, clock-spring cap +6 mm, stops A / B)', c: V.scale(f.pK, F[1]), axis: f.pK, r: 10, h: h + 6 },
        { kind: 'arc', role: 'link', name: 'link 1b (12 x 3 Ti, K -> J2)', pts: profArc(f.pK, f.p2, G.lv1b, 1.5), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2 (O20, dowel-in-slot stop on q2)', c: V.scale(f.p2, F[2]), axis: f.p2, r: 10, h },
        { kind: 'arc', role: 'link', name: 'link 2 (12 x 3 Ti; LOWER face member at hub 3)', pts: profArc(f.p2, f.p3, G.lv2, 1.5), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3 (O20, humerus-fixed axis)', c: V.scale(f.p3, F[3]), axis: f.p3, r: 10, h },
        { kind: 'arc', role: 'fixed-arm', name: 'member 3: cap plate + K7 neck (UPPER member at hub 3, over link 2)', pts: neck, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: "BOTTOM's bar", a: neckEnd, b: barEnd, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'bar to cuff', a: barEnd, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
