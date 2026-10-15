/* offset-skin-normal-3r - a NON-concurrent 3R: each hub sits flat on its skin with its axis along the local skin
 * normal, so the three axis LINES miss GH (catalogue entry; not modelled yet: the catalogue's model_spec is the
 * source). J1 on the dome, J2 over the posterior acromion, J3 on the lateral deltoid; flat straps between hub centres;
 * at the cuff a passive self-aligning module: P_s, a rolling rail along the humerus (+-20 mm), and P_t, a rail across
 * the lateral arm (+-15 mm). Orientation depends only on the axis DIRECTIONS, so the 3 active angles are those of the
 * spherical chain with the same directions (closed form, exact). The translation mismatch e the offsets create at the
 * cuff point goes into the 2 slides (PASSIVE, set by closure); its RADIAL part cannot be absorbed and must stay small by
 * design (the spec allows <= 3 mm): it is the third mm residual, reported as is (a frame with more than 0.5 mm does not
 * close). Layout of this preview: hub sites = the champion 3R's hubs in the rest pose (faces 53 / 93 / 72 mm), cuff
 * point 150 mm down the lateral arm; axis tilts off the radial and their directions from a random search over the loop
 * that minimises the radial mismatch (the spec's sweep constraint): tilts 11.9 / 5 / 6.9 deg, so the axes miss GH by
 * 11 / 8 / 9 mm, radial mismatch <= 3.2 mm, slides <= 16 / 14 mm. Tilting every axis 14 deg instead (misses 13-22 mm)
 * gives up to 21 mm of radial mismatch: the offset is bounded by what the 2 slides cannot take. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const CH = { az: 2.4305071427308924, el: 80.67633718429899, a: [76.90180446920043, 66.74921235407174], w: [86.32769021001913, 21.829657347343378] };
  const P = { faces: [53, 93, 72], tilt: [11.9, 5, 6.9], tdir: [43, 38, 157], cuff: [0, -150, 50], slide_s: 20, slide_t: 15, rad_ok: 3,
              sing: 5, hub_r: 10, stack: 12.25 };
  function design(P) {
    // the champion's joint directions in the REST pose (scapula frame): the hub sites
    const champ = K.sph3r(K.bvec(CH.az, CH.el), K.wdir(CH.w[0], CH.w[1]), CH.a[0], CH.a[1], -1);
    const rest = K.makeCtx(K.KEYS[0].pose), f = champ.fk(champ.solve(rest), { S: M.I3(), H: M.I3() });
    const Qr = M.mul(M.T(rest.S), rest.H), radial = [f.p1, f.p2, f.p3];
    const c = radial.map((r, k) => V.scale(r, P.faces[k]));                                   // anchors (lines pass here)
    const d = radial.map((r, k) => K.onCone(r, V.perp(r), P.tilt[k], P.tdir[k]));          // axis directions (skin normals)
    const br = Math.sign(V.dot(d[1], V.cross(d[0], d[2]))) || 1;
    const sph = K.sph3r(d[0], d[2], V.angle(d[0], d[1]), V.angle(d[1], d[2]), br);        // spherical-equivalent chain
    const Cr = M.mulv(Qr, P.cuff);                                                          // cuff point, rest (scapula frame)
    return { Qr, c, d, sph, Cr };
  }
  const D = design(P), u = D.d, c = D.c;
  const G = ctx => M.mul(M.mul(M.T(ctx.S), ctx.H), M.T(D.Qr));                              // arm motion since rest (scap frame)
  const gctx = ctx => ({ S: M.I3(), H: G(ctx) });
  function fk(q) {                                                                          // screw motions about the axis lines
    const R1 = M.rot(u[0], q[0]), R2 = M.rot(u[1], q[1]), R3 = M.rot(u[2], q[2]), R12 = M.mul(R1, R2), R123 = M.mul(R12, R3);
    const t1 = V.sub(c[0], M.mulv(R1, c[0]));
    const t2 = V.add(M.mulv(R1, V.sub(V.sub(c[1], M.mulv(R2, c[1])), c[0])), c[0]);
    const t3 = V.add(M.mulv(R12, V.sub(c[2], M.mulv(R3, c[2]))), t2);
    return { X1: [R1, t1], X2: [R12, t2], X3: [R123, t3] };
  }
  const ap = (X, p) => V.add(M.mulv(X[0], p), X[1]);
  /** mismatch at the cuff in the arm's slide frame (along the humerus, across the strip, radial) */
  function mismatch(q, ctx) {
    const X = fk(q).X3, Q = M.mul(M.T(ctx.S), ctx.H), e = V.sub(ap(X, D.Cr), M.mulv(G(ctx), D.Cr));
    return [V.dot(e, M.mulv(Q, [0, -1, 0])), V.dot(e, M.mulv(Q, [1, 0, 0])), V.dot(e, M.mulv(Q, [0, 0, 1]))];
  }
  const solve = ctx => { const q = D.sph.solve(gctx(ctx)), e = mismatch(q, ctx); return q.concat([e[0], e[1]]); };

  K.register({
    id: 'offset-skin-normal-3r',
    name: 'Non-concurrent 3R on skin-normal hubs + 2 cuff slides',
    dof: { active: 3, passive: 2 },
    params: P, design,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'J2', 'J3', 'cuff slide along the arm', 'cuff slide across'], qUnits: ['deg', 'deg', 'deg', 'mm', 'mm'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve,
    residual: (q, ctx) => {
      const e = mismatch(q, ctx);
      return M.rotErrDeg(fk(q).X3[0], G(ctx)).concat([e[0] - q[3], e[1] - q[4], e[2]]);   // e[2]: radial, unabsorbed
    },
    check: (q, ctx) => {
      const m = D.sph.margin(gctx(ctx));
      if (m < 0) return 'J2 cannot close: the arm axis is out of reach';
      if (m < P.sing) return `J2 within ${m.toFixed(0)} deg of its fold`;
      const e = mismatch(q, ctx);
      if (Math.abs(e[2]) > P.rad_ok) return `radial mismatch ${e[2].toFixed(1)} mm at the cuff (cuff padding takes <= ${P.rad_ok})`;
      if (Math.abs(q[3]) > P.slide_s) return 'slide along the arm past its travel';
      if (Math.abs(q[4]) > P.slide_t) return 'slide across the arm past its travel';
      return null;
    },
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), F = fk(q), h = P.stack;
      const Xs = [[M.I3(), [0, 0, 0]], F.X1, F.X2];
      const hubs = Xs.map((X, k) => ({ kind: 'hub', role: 'active', name: `J${k + 1} (skin-normal axis)`, c: W(ap(X, c[k])), axis: Wd(M.mulv(X[0], u[k])), r: P.hub_r, h }));
      const top = (k, dz) => V.madd(hubs[k].c, hubs[k].axis, dz);
      const Q = M.mul(M.T(S), ctx.H), arm = v => W(M.mulv(Q, v)), carm = ctx.attach.armPt(P.cuff);
      const e = mismatch(q, ctx), Cend = W(ap(F.X3, D.Cr));                                    // member 3's cuff point
      const along = ctx.attach.armDir([0, -1, 0]), across = ctx.attach.armDir([1, 0, 0]), out = ctx.attach.armDir([0, 0, 1]);
      const sA = V.madd(carm, out, 6), sT = V.madd(sA, along, q[3]);
      const strap = (a, b) => { const n = 10, pts = []; for (let i = 0; i <= n; i++) { const p = V.lerp(a, b, i / n); pts.push(V.scale(V.unit(p), Math.max(V.norm(p), V.norm(a) + (V.norm(b) - V.norm(a)) * i / n))); } return pts; };
      return [
        { kind: 'plate', role: 'fixed-scapula', c: V.madd(hubs[0].c, hubs[0].axis, -3), z: hubs[0].axis, x: ctx.attach.scapDir([1, 0, 0]), size: [40, 30], t: 3 },
        hubs[0],
        { kind: 'arc', role: 'link', name: 'link 1 (flat strap, hub to hub)', pts: strap(top(0, 7), top(1, 2)), r: 2.5 },
        hubs[1],
        { kind: 'arc', role: 'link', name: 'link 2 (flat strap)', pts: strap(top(1, 9), top(2, h + 1)), r: 2.5 },
        hubs[2],
        { kind: 'link', role: 'link', name: 'member 3 to the cuff module', a: top(2, h + 1), b: V.madd(Cend, out, 10), r: 3 },
        { kind: 'slider', role: 'passive', name: 'P_s: rail along the humerus', a: V.madd(sA, along, -P.slide_s), b: V.madd(sA, along, P.slide_s), at: sT, z: out, size: [14, 12, 4] },
        { kind: 'slider', role: 'passive', name: 'P_t: rail across the arm', a: V.madd(V.madd(sT, across, -P.slide_t), out, 3), b: V.madd(V.madd(sT, across, P.slide_t), out, 3),
          at: V.madd(V.madd(sT, across, q[4]), out, 4 + e[2]), z: out, size: [12, 12, 4] },
        { kind: 'plate', role: 'fixed-arm', name: 'cuff module base', c: V.madd(carm, out, 2), z: out, x: along, size: [40, 30], t: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: V.scale(ctx.armAxis, -P.cuff[1]), axis: ctx.armAxis, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
