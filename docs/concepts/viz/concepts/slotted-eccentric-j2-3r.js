/* slotted-eccentric-j2-3r - default config (preview test)
 * Zero-passive spherical 3R at O20 with link 2 split at a passive knee K whose angle is slaved to q2 by a roller in a
 * slot: J1 (O20, scapula seat az/el) -> link 1 (+ a spoke and a curved slotted TRACK around hub 2, all one body) -> J2
 * (O20) -> crank 2a (arc b) -> knee K (passive pin, MR63ZZ pair) -> link 2b (K -> J3, arc c) + an arm to the roller
 * stud G (MR52ZZ roller riding in link 1's track) -> J3 (O20, humerus seat wd/wa) -> the neck to BOTTOM's bar.
 * The spec put the roller on link 1 and the slot on 2b: that is singular wherever the crank's azimuth about J2 passes the
 * roller's (q2 spans ~200 deg), so the model inverts it (roller on 2b, track on link 1: singular only if G, K, J2
 * align, which depends on the knee angle alone). Per frame: th = angle(J1, J3) -> the law a2e(th) (soft clip into
 * [Amin, Amax]) -> J2 by the two-circle closure (a1, a2e) -> K by the closure (b, c). Outside the track's ends (where the
 * slot's lock angle would fall under 50 deg) the chain is not taken (red). Levels: the kit's fitted profiles on
 * Bench(60,160). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az": 97.7506, "el": 65.294, "a1": 38.0901, "wd": 90.0506, "wa": -9.2038, "sigma": -1, "margin": 5.0, "Amin": 60.0, "Amax": 90.0, "w": 3.0, "sl": 1.0, "b": 25.0, "c": 72.0, "sk": 1, "psi_lo": 15.0, "rad1": 10.0, "rad2": 10.0, "rad3": 10.0, "rpin": 5.0};
  const G = {"lo": 27.0, "hi": 117.75, "dG": 23.0, "gG": 7.5, "tr_e": [25.06810921527672, 25.06895645773497, 25.25531670246337, 29.936703978970673, 37.20582282547264, 42.93246326748105, 44.99209542388112, 45.18189002165416, 45.192072565580204, 45.1926292508926], "tr_eta": [35.59536462037321, 18.131012786619003, -8.68646048505233, -31.213257788149214, -47.005054240265515, -61.54254665283335, -76.45398785330019, -91.37354741029273, -106.27586666471656, -115.9633812546142], "spoke": 2, "lv": {"hub1": {"F": 52.0, "t": 12.25}, "hub2": {"F": 62.21, "t": 13.1}, "hub3": {"F": 69.0, "t": 15.25}, "pinK": {"F": 58.42, "t": 14.301}, "studG": {"F": 61.42, "t": 6.0}, "link1": {"r0": 55.15, "r1": 62.21, "mid": 51.43}, "spoke": {"r0": 62.21, "r1": 49.0, "mid": 55.28}, "trk1": {"r0": 53.68, "r1": 50.84, "mid": 52.08}, "trk2": {"r0": 50.84, "r1": 49.2, "mid": 49.28}, "trk3": {"r0": 49.2, "r1": 51.04, "mid": 50.0}, "trk4": {"r0": 51.04, "r1": 55.17, "mid": 53.04}, "trk5": {"r0": 55.48, "r1": 59.37, "mid": 57.41}, "trk6": {"r0": 59.13, "r1": 61.88, "mid": 60.13}, "trk7": {"r0": 62.0, "r1": 69.75, "mid": 64.29}, "trk8": {"r0": 70.16, "r1": 76.68, "mid": 74.23}, "trk9": {"r0": 76.92, "r1": 84.42, "mid": 79.17}, "neck": {"r0": 69.0, "r1": 95.43, "mid": 77.93}, "crank": {"r0": 65.36, "r1": 58.63, "mid": 65.22}, "L2b": {"r0": 61.57, "r1": 72.15, "mid": 82.34}, "armG": {"r0": 61.57, "r1": 64.42, "mid": 59.64}}};
  const lv = G.lv, BAR0 = [0, -0.56984, 0.82175], W = K.wrap180;
  const sp = x => Math.log1p(Math.exp(-Math.abs(x))) + Math.max(x, 0);
  function a2e(th) {
    const lo = P.Amin, hi = Math.max(P.Amax, P.Amin + 0.5), w = Math.max(0.3, P.w), x = 0.5 * (lo + hi) + P.sl * (th - 0.5 * (lo + hi));
    return lo + w * sp((x - lo) / w) - w * sp((x - hi) / w);
  }
  const axes = ctx => ({ p1: M.mulv(ctx.S, K.bvec(P.az, P.el)), p3: M.mulv(ctx.H, K.wdir(P.wd, P.wa)) });
  function chain(ctx) {
    const { p1, p3 } = axes(ctx), th = V.angle(p1, p3), ae = a2e(th);
    const c2 = K.circInt(p1, P.a1, p3, ae, P.sigma), p2 = c2.p, ck = K.circInt(p2, P.b, p3, P.c, P.sk), Kw = ck.p;
    const Gw = K.onCone(Kw, p3, G.dG, G.gG);
    return { p1, p3, p2, Kw, Gw, th, ae, ok: c2.ok && ck.ok };
  }
  function solve(ctx) {
    const X = chain(ctx);
    return [K.axisAngle(X.p1, ctx.attach.scapDir([1, 0, 0]), X.p2), K.axisAngle(X.p2, X.p1, X.Kw), K.axisAngle(X.Kw, X.p2, X.p3),
            K.axisAngle(X.p3, ctx.armAxis, X.Kw)];
  }
  /** forward kinematics from q (J1 azimuth of J2 about J1, crank q2 about J2 from link 1, knee about K) */
  function fk(q, ctx) {
    const { p1, p3 } = axes(ctx), e = V.unit(V.reject(ctx.attach.scapDir([1, 0, 0]), p1)), f = V.cross(p1, e), a = P.a1 * D2R, j = q[0] * D2R;
    const p2 = V.add(V.scale(p1, Math.cos(a)), V.scale(V.add(V.scale(e, Math.cos(j)), V.scale(f, Math.sin(j))), Math.sin(a)));
    const Kw = K.onCone(p2, p1, P.b, q[1]), u3 = K.onCone(Kw, p2, P.c, q[2]);
    return { p1, p3, p2, Kw, u3, Gw: K.onCone(Kw, u3, G.dG, G.gG) };
  }
  K.register({
    id: 'slotted-eccentric-j2-3r', name: 'Eccentric J2 crank + slotted track: knee slaved to q2 by a roller (inverted slot), O20',
    dof: { active: 3, passive: 1 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'J2 (crank)', 'knee K (slaved)', 'J3'], qUnits: ['deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'deg', 'deg'],
    solve,
    residual: (q, ctx) => {
      const X = fk(q, ctx), cr = V.cross(X.u3, X.p3), n = V.norm(cr), an = V.angle(X.u3, X.p3);
      const rv = n > 1e-12 ? V.scale(cr, an / n) : [0, 0, 0];
      return rv.concat([W(K.axisAngle(X.p3, ctx.armAxis, X.Kw) - q[3]), V.angle(X.p2, X.p3) - a2e(V.angle(X.p1, X.p3))]);
    },
    check: (q, ctx) => {
      const X = chain(ctx);
      if (X.th < G.lo || X.th > G.hi) return `J1-J3 angle ${X.th.toFixed(0)} deg outside the slot track [${G.lo.toFixed(0)}, ${G.hi.toFixed(0)}]`;
      if (!X.ok) return 'closure fails';
      return null;
    },
    parts: (q, ctx) => {
      const X = fk(q, ctx), h = 1.5, arc = (name, role, a, b, m, r) => ({ kind: 'arc', role, name, u: a, v: b, r0: lv[m].r0 + h, r1: lv[m].r1 + h, r: r || 2.5 });
      const hubD = (name, role, ax, m, r) => ({ kind: 'hub', role, name, c: V.scale(ax, lv[m].F), axis: ax, r, h: lv[m].t });
      const h1 = hubD('J1 (O20, axis through GH)', 'active', X.p1, 'hub1', P.rad1);
      const N = G.tr_e.map((e, i) => K.onCone(X.p2, X.p1, e, G.tr_eta[i]));
      const trk = [];
      for (let i = 0; i + 1 < N.length; i++) trk.push(arc(`slotted track ${i + 1} (link 1)`, 'link', N[i], N[i + 1], `trk${i + 1}`, 3));
      const neckEnd = M.mulv(ctx.Hb, BAR0);
      const DB = [0, -0.9975, -0.0713], barDn = M.mulv(ctx.Hb, DB), neckPt = V.scale(V.unit(neckEnd), lv.neck.r1 + h);
      const cuffC = V.scale(ctx.armAxis, 155), cuffTop = V.madd(cuffC, V.unit(V.reject(neckPt, ctx.armAxis)), 47);
      const barEnd = V.madd(neckPt, barDn, Math.max(20, V.dot(V.sub(cuffTop, neckPt), barDn)));
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base on the scapula handler', c: V.madd(h1.c, X.p1, -3), z: X.p1, x: ctx.attach.scapDir([1, 0, 0]), size: [40, 30], t: 3 },
        h1,
        arc('link 1 (12 x 3 Ti)', 'link', X.p1, X.p2, 'link1'),
        arc('spoke to the track (link 1)', 'link', X.p2, N[G.spoke], 'spoke'),
        ...trk,
        hubD('J2 (O20, through GH)', 'active', X.p2, 'hub2', P.rad2),
        arc('crank 2a (J2 -> knee)', 'link', X.p2, X.Kw, 'crank'),
        hubD('knee K (passive pin, slaved)', 'passive', X.Kw, 'pinK', P.rpin),
        arc('link 2b (knee -> J3)', 'link', X.Kw, X.u3, 'L2b'),
        arc('2b arm to the roller stud', 'link', X.Kw, X.Gw, 'armG', 2),
        hubD('roller stud G (MR52ZZ in the track)', 'passive', X.Gw, 'studG', 3.5),
        hubD('J3 (O20, through GH)', 'active', X.u3, 'hub3', P.rad3),
        arc('neck to BOTTOM\'s bar (14 x 6)', 'fixed-arm', X.p3, neckEnd, 'neck', 3),
        { kind: 'link', role: 'fixed-arm', name: "BOTTOM's bar", a: neckPt, b: barEnd, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'bar to cuff', a: barEnd, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: ctx.armAxis, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
