/* acromial-rocker-3r - fold lever on the pin-knee leader: J1 rides a PASSIVE acromial rocker whose angle the arm sets
 * through an S-U tie rod (bench model docs/concepts/models/acromial-rocker-3r.py on skin-normal-3r-pin-knee.py on
 * offset-skin-normal-3r.py; rotations only, 0 passive translations). Screened, kill test FAILS: best config k22
 * (rows/acromial-rocker-3r.json best_params) 125.84 fast, reach 0.20 - the rod passes its dead point / the rocker cap /
 * the U-joint bend over most of the workspace. Every constant below is the model's Design at k22 (dumped from
 * acromial-rocker-3r.py with rA / rC = the fitted 70.6 / 75.8; the seats come from ray casts on the rest skin, which
 * the page cannot do), in the model's scapula frame (u, c, cp, A0) or arm frame (C0, B2, sn / sa / st, c3).
 * Chain: scapula -> J0 PASSIVE pivot (MR63ZZ pair, axis cp through GH) -> rocker -> J1 ACTIVE (axis u1 on a GH ray) ->
 * link 1 -> J2 ACTIVE (GH ray) -> link 2 -> J3 ACTIVE (axis tilted b3 0.23 toward the skin normal: its line misses GH by
 * ~7 mm) -> member 3 = hub 3's lower plate + the E strap -> pin a -> knee link -> pin b -> arm pad on the cuff/BOTTOM
 * (the pin-knee closure: member 3 moves on the arm by a rotation about J3 + a translation in hub 3's plane, closed by
 * the planar RRR C - a - b). Tie: rocker stud A -> ball link (3 rot) -> O4 Ti rod -> miniature U-joint (2 rot) -> stud C
 * on an arm bracket from the arm pad. Rocker angle q0 in closed form from |R(cp, q0) A0 - Q C0| = L on the rest
 * branch; taken only if transmission >= 25 deg, |q0| <= 75, ball tilt <= 30, U bend <= 40 (red otherwise, with the
 * reason; past the cap the rocker is drawn on its end stop and the rod residual shows the mismatch). 3 ACTIVE + 8 PASSIVE rotations (rocker 1, knee pins 2, ball 3, U 2). Levels = the model's fitted levels at
 * k22 (hubs F 49.8 / 61.1 / 71.9, knee stack 76.0, pivot 50.7, rocker straps 53.9, bracket 65.1); links schematic
 * between their hub levels. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = K.D2R;
  const P = { beta: 23.0, psi: 220.0, gam: 29.3, psiA: 13.9, dl: 22.9, psiC: 199.9, q0r: 13.7, rA: 70.6, rC: 75.8,
              cap: 75, trans: 25, ball: 30, uj: 40, lE: 30, lc: 25, phiE: 0, phib: -90, ang_min: 30, stk: 5, tp: 2.25, b3: 0.2282,
              u: [[0.04278, 0.90785, 0.41712], [-0.60493, 0.76227, 0.23024], [-0.19634, -0.09064, 0.97634]],
              c3: [-1.42291, -6.80193, -0.91758], A: [0.70413, 1.29275], branch: -1,
              sn: [-0.19634, -0.09064, 0.97634], sa: [0.01787, -0.99588, -0.08886], st: [0.98037, 0, 0.19715], m: [-3.0451, -1.36394],
              cp: [0.42961, 0.82499, 0.36719], dA: [0.025, 0.74973, 0.66127], A0: [1.76465, 52.93107, 46.68563],
              C0: [12.77705, -12.07031, 73.73394], dCh: [0.16856, -0.15924, 0.97274], L: 66.1927367539929, s0: -1,
              stud: [0.25175, 0.44937, 0.85714], ubase: [0.07615, 0.86983, -0.48743],
              f: [49.79, 61.11, 71.92], tr: 75.96, lv: { pvt: 50.7, rk1: 53.9, rk2: 53.9, brk: 65.1 }, UP: 3.15, RUN: 0.5,
              sing: 10, cuff_at: 165 };
  const u1 = P.u[0], u3 = P.u[2], cp = V.unit(P.cp);
  const C = K.sph3r(u1, u3, P.A[0] / D2R, P.A[1] / D2R, P.branch);          // orientation of the chain on the rocker
  const Ap = V.scale(cp, V.dot(cp, P.A0)), Aq = V.sub(P.A0, Ap), Ar = V.cross(cp, Aq);
  const pe = P.phiE * D2R, eE = [Math.cos(pe), Math.sin(pe)], A0k = [P.m[0] + P.lE * eE[0], P.m[1] + P.lE * eE[1]];
  const B2 = [A0k[0] + P.lc * Math.cos(P.phib * D2R), A0k[1] + P.lc * Math.sin(P.phib * D2R)];
  const wrap = a => Math.atan2(Math.sin(a), Math.cos(a));
  const kbr = Math.sign(wrap(pe - Math.atan2(B2[1] - P.m[1], B2[0] - P.m[0]))) || 1;
  const Qof = ctx => M.mul(M.T(ctx.S), ctx.H);                               // the model's Q (band HG)
  const Arot = q0 => V.add(Ap, V.add(V.scale(Aq, Math.cos(q0)), V.scale(Ar, Math.sin(q0))));
  /** the tie rod (model Design._rod / rocker): q0 (rad), x, transmission / cap / ball / U flags */
  function rod(Q) {
    const Cs = M.mulv(Q, P.C0), k = 0.5 * (V.dot(P.A0, P.A0) + V.dot(Cs, Cs) - P.L * P.L);
    const a = V.dot(Cs, Ap), xx = V.dot(Cs, Aq), yy = V.dot(Cs, Ar), x = (k - a) / Math.max(Math.hypot(xx, yy), 1e-9);
    const q0 = wrap(Math.atan2(yy, xx) + P.s0 * Math.acos(Math.max(-1, Math.min(1, x))));
    const A = Arot(q0), d = V.unit(V.sub(Cs, A)), cq = Math.cos(q0), sq = Math.sin(q0);
    const rr = V.add(V.add(V.scale(cp, V.dot(d, cp)), V.scale(V.reject(d, cp), cq)), V.scale(V.cross(cp, d), -sq));
    const rl = M.mulv(M.T(Q), V.scale(d, -1));
    const tb = Math.asin(Math.min(1, Math.abs(V.dot(rr, P.stud)))) / D2R, tu = V.angle(rl, P.ubase);
    return { q0, x, A, Cs, tb, tu };
  }
  /** pin-knee closure for a J3-centre drift s (plane coords [a, t] in the arm frame): pin a angle th (rad) */
  function knee(s) {
    const v = [B2[0] - s[0], B2[1] - s[1]], d = Math.hypot(v[0], v[1]), gam = Math.atan2(v[1], v[0]);
    const ca = (P.lE * P.lE + d * d - P.lc * P.lc) / (2 * P.lE * Math.max(d, 1e-9)), al = Math.acos(Math.max(-1, Math.min(1, ca)));
    const th = gam + kbr * al, pa = [s[0] + P.lE * Math.cos(th), s[1] + P.lE * Math.sin(th)];
    const w = [B2[0] - pa[0], B2[1] - pa[1]], ang = Math.acos(Math.max(-1, Math.min(1, ((s[0] - pa[0]) * w[0] + (s[1] - pa[1]) * w[1]) / (P.lE * P.lc)))) / D2R;
    const ok = d >= Math.abs(P.lE - P.lc) + 1 && d <= P.lE + P.lc - 1 && ang >= P.ang_min && ang <= 180 - P.ang_min;
    return { th, pa, d, ang, ok };
  }
  const onRocker = (ctx, q0deg) => ({ S: M.mul(ctx.S, M.rot(cp, q0deg)), H: ctx.H });
  /** chain state for q = [q0, J1, J2, J3, pin a angle] (deg): J3-centre drift s, member transforms */
  function chain(q, ctx) {
    const f = C.fk(q.slice(1, 4), onRocker(ctx, q[0]));
    const sv = V.sub(M.mulv(M.T(M.rot(u3, q[3])), P.c3), P.c3);       // = R3^T c3 - c3 (c1 = c2 = 0)
    return { f, s: [V.dot(sv, P.sa), V.dot(sv, P.st), V.dot(sv, P.sn)] };
  }
  const plane = (p2, h) => V.add(P.c3, V.add(V.add(V.scale(P.sa, p2[0]), V.scale(P.st, p2[1])), V.scale(P.sn, h)));   // arm frame

  K.register({
    id: 'acromial-rocker-3r',
    name: 'Acromial rocker 3R (pin-knee leader, J1 on a rod-driven rocker)',
    dof: { active: 3, passive: 8 },
    params: P,
    q0: ctx => K.concepts['acromial-rocker-3r'].solve(ctx),
    qNames: ['J0 rocker (passive)', 'J1', 'J2', 'J3', 'pin a (passive)'], qUnits: ['deg', 'deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm'],
    solve: (ctx, qPrev) => {
      // past its cap (or with no rod closure) the rocker is drawn on its end stop, on the side it came from: the rod
      // residual then shows the mismatch (red), instead of the closed form's free swing through +-180 deg
      const r = rod(Qof(ctx)); let q0 = r.q0 / D2R;
      if (Math.abs(q0) > P.cap) q0 = (Math.sign(qPrev ? qPrev[0] : q0) || 1) * P.cap;
      const q123 = C.solve(onRocker(ctx, q0)), s = chain([q0].concat(q123, [0]), ctx).s;
      return [q0].concat(q123, [knee(s).th / D2R]);
    },
    residual: (q, ctx) => {
      const ch = chain(q, ctx), e = C.residual(q.slice(1, 4), onRocker(ctx, q[0]));
      const A = Arot(q[0] * D2R), Cs = M.mulv(Qof(ctx), P.C0), th = q[4] * D2R;
      const pa = [ch.s[0] + P.lE * Math.cos(th), ch.s[1] + P.lE * Math.sin(th)];
      return e.concat([V.norm(V.sub(Cs, A)) - P.L, Math.hypot(B2[0] - pa[0], B2[1] - pa[1]) - P.lc]);
    },
    check: (q, ctx) => {
      const Q = Qof(ctx), r = rod(Q), m = C.margin(onRocker(ctx, q[0]));
      if (Math.abs(r.x) > Math.cos(P.trans * D2R)) return Math.abs(r.x) > 1 ? 'the tie rod cannot reach (no rocker angle closes it)' : `tie rod within ${P.trans} deg of its dead point`;
      if (Math.abs(r.q0 / D2R) > P.cap) return `rocker past its +-${P.cap} deg cap (drawn on its end stop)`;
      if (r.tb > P.ball) return `ball link tilted ${r.tb.toFixed(0)} deg (> ${P.ball})`;
      if (r.tu > P.uj) return `U-joint bent ${r.tu.toFixed(0)} deg (> ${P.uj})`;
      if (m < 0) return 'J2 cannot close (the fold)';
      if (m < P.sing) return `J2 within ${m.toFixed(0)} deg of its fold`;
      const kn = knee(chain(q, ctx).s);
      if (!kn.ok) return `knee out of its window (angle ${kn.ang.toFixed(0)} deg, drift ${kn.d.toFixed(0)} mm)`;
      return null;
    },
    parts: (q, ctx) => {
      const S = ctx.S, H = ctx.H, W = p => M.mulv(S, p), Wa = p => M.mulv(H, p), R0 = M.rot(cp, q[0]);
      const ch = chain(q, ctx), f = ch.f, F = P.f, th = q[4] * D2R;
      const cW = W(cp), u1W = f.p1, u2W = f.p2, u3W = f.p3;
      const h1 = V.scale(u1W, F[0]), h2 = V.scale(u2W, F[1]);
      const h3 = Wa(plane(ch.s, F[2])), sn = Wa(P.sn);
      const pa = Wa(plane([ch.s[0] + P.lE * Math.cos(th), ch.s[1] + P.lE * Math.sin(th)], P.tr));
      const pb = Wa(plane(B2, P.tr)), kneeZ = V.scale(sn, P.tp + P.RUN);
      const dAW = W(M.mulv(R0, P.dA)), A = W(Arot(q[0] * D2R)), Cw = Wa(P.C0), dCW = Wa(P.dCh);
      const ga = K.greatArc(h2, h3, V.norm(h2) + P.UP, V.norm(h3) + P.UP, 20), err = V.sub(V.add(h3, V.scale(sn, P.UP)), ga[ga.length - 1]);
      const link2 = ga.map((p, i) => V.madd(p, err, i / (ga.length - 1)));
      const harm = ctx.armAxis, cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(pb, harm)), 47);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base (scapula handler)', c: V.scale(cW, P.lv.pvt - 3), z: cW, x: ctx.attach.scapDir([1, 0, 0]), size: [36, 26], t: 3 },
        { kind: 'hub', role: 'passive', name: 'J0 rocker pivot (O14, MR63ZZ pair)', c: V.scale(cW, P.lv.pvt), axis: cW, r: 7, h: 9 },
        { kind: 'arc', role: 'link', name: 'rocker strap to J1 (8 x 3 Ti)', u: cW, v: u1W, r0: P.lv.rk1 + 1.5, r1: P.lv.rk1 + 1.5, r: 2.5 },
        { kind: 'arc', role: 'link', name: 'rocker strap to stud A (8 x 3 Ti)', u: cW, v: dAW, r0: P.lv.rk2 + 1.5, r1: P.lv.rk2 + 1.5, r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'ball link at stud A (3 rot)', c: V.scale(dAW, P.rA - 6), axis: dAW, r: 4, h: 12 },
        { kind: 'link', role: 'link', name: 'tie rod (O4 Ti)', a: A, b: Cw, r: 2 },
        { kind: 'hub', role: 'passive', name: 'miniature U-joint at stud C (2 rot)', c: V.scale(dCW, P.rC - 6), axis: dCW, r: 4, h: 12 },
        { kind: 'link', role: 'fixed-arm', name: 'arm bracket (pad to stud C)', a: V.madd(pb, sn, -3), b: V.scale(dCW, P.lv.brk), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J1 (O20, on the rocker)', c: h1, axis: u1W, r: 10, h: 12.25 },
        { kind: 'arc', role: 'link', name: 'link 1 (8 x 3 Ti)', u: u1W, v: u2W, r0: F[0] + P.UP + 1.5, r1: F[1] + 1.5, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2 (O20)', c: h2, axis: u2W, r: 10, h: 12.25 },
        { kind: 'arc', role: 'link', name: 'link 2 (8 x 3 Ti)', pts: link2, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3 (O20, axis tilted to the skin normal: misses GH)', c: h3, axis: u3W, r: 10, h: 12.25, p0: Wa(P.c3) },
        { kind: 'link', role: 'link', name: 'E strap (member 3, 8 x 3 Ti)', a: V.madd(h3, sn, 1.5), b: pa, r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'knee pin a (iglidur)', c: pa, axis: sn, r: 6, h: P.stk },
        { kind: 'link', role: 'link', name: 'knee link (flat Ti)', a: V.add(pa, kneeZ), b: V.add(pb, kneeZ), r: 3 },
        { kind: 'hub', role: 'passive', name: 'knee pin b (iglidur)', c: pb, axis: sn, r: 6, h: P.stk },
        { kind: 'plate', role: 'fixed-arm', name: 'arm pad (O12, on the cuff / BOTTOM)', c: V.madd(pb, sn, -1.5), z: sn, x: Wa(P.sa), size: [12, 12], t: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'pad to cuff (BOTTOM)', a: V.madd(pb, sn, -3), b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
