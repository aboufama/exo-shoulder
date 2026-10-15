/* lazy-tongs-j2 - spherical 3R with a12 = a23 = 90 deg whose J2 is a 1-DOF spherical lazy-tongs instead of a folding
 * knee (catalogue lazy-tongs-j2; no model / sweep yet). J1 ACTIVE hub on the dome pole p* (S-local lat 66 / lon -68),
 * J3 ACTIVE hub on an arm-fixed axis through the lateral deltoid (arm point s 50, th 0 - picked so the J1-J3 angle stays
 * inside the tongs' range 49-139 deg over the whole loop). J2 ACTIVE = rotation about the remote axis u2 = unit(u1 x w):
 * a scissor of n = 6 cells (link 24 deg) lying ON the J1 -> J3 great circle, between an end block on each hub (one fixed
 * pivot + one pivot in a short arc slot), every pivot radial through GH; J2 is sensed at the first centre pivot. No metal
 * at the u2 piercing point: the excess J1-J3 swing becomes band width (~8 mm long, ~26 mm short) instead of a knee thrown
 * sideways. Closed form (KIN.sph3r with 90 / 90 arcs); the tongs geometry follows the spec's planar cell approximation
 * (cell L = theta / n, half-width h = sqrt(lambda^2 - L^2) / 2). 3 ACTIVE + 21 PASSIVE (scissor pivots and slots). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = K.D2R;
  const P = { u1: [66, -68], j3: [50, 0, 55], n: 6, lam: 24, branch: 1, rho: [65, 71], layer: 2.5, faces: [50, 57],
              block: 12, hub_r: 10, stack: 12.25, neck_deg: 25, cuff_at: 165 };
  const sl = (lat, lon) => [Math.cos(lat * D2R) * Math.sin(lon * D2R), Math.sin(lat * D2R), Math.cos(lat * D2R) * Math.cos(lon * D2R)];
  const AX = V.unit(K.BODY.elbow), ZL = V.unit(V.reject(M.col(K.BODY.rest_humerus, 2), AX)), YL = V.cross(AX, ZL);
  const [s3, th3, r3] = P.j3, j3 = V.unit(V.add(V.scale(AX, s3), V.add(V.scale(ZL, r3 * Math.cos(th3 * D2R)), V.scale(YL, r3 * Math.sin(th3 * D2R)))));
  const w = M.mulv(M.T(K.BODY.rest_humerus), j3);                                 // bind coords -> humerus (H) frame
  const C = K.sph3r(sl(P.u1[0], P.u1[1]), w, 90, 90, P.branch), n = P.n, lam = P.lam;
  const hMax = 0.5 * lam * Math.cos(20 * D2R);
  function tongs(f) {                                                              // arc frame on the J1 -> J3 great circle
    const u = f.p1, th = V.angle(f.p1, f.p3), g = V.unit(V.reject(f.p3, u)), e = V.unit(V.cross(u, g));
    const L = th / n, h = 0.5 * Math.sqrt(Math.max(0, lam * lam - L * L));
    const rho = t => P.rho[0] + (P.rho[1] - P.rho[0]) * Math.max(0, Math.min(1, t / th));
    const d = (t, c, dz) => V.scale(V.add(V.scale(V.add(V.scale(u, Math.cos(t * D2R)), V.scale(g, Math.sin(t * D2R))), Math.cos(c * D2R)), V.scale(e, Math.sin(c * D2R))), rho(t) + (dz || 0));
    return { th, L, h, g, e, d };
  }
  const line = (T, t0, c0, t1, c1, dz) => [0, 0.25, 0.5, 0.75, 1].map(s => T.d(t0 + (t1 - t0) * s, c0 + (c1 - c0) * s, dz));

  K.register({
    id: 'lazy-tongs-j2',
    name: 'Lazy-tongs J2 (scissor arc instead of a knee)',
    dof: { active: 3, passive: 21 },
    params: P,
    q0: ctx => C.solve(ctx),
    qNames: ['J1', 'J2 (tongs, remote axis u2)', 'J3'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => C.solve(ctx),
    residual: (q, ctx) => C.residual(q, ctx),
    check: (q, ctx) => {
      const th = V.angle(M.mulv(ctx.S, C.u1), M.mulv(ctx.H, C.u3));
      if (th < 25 || th > 165) return 'end blocks collide / J1-J3 margin';
      if (th / n > lam * Math.cos(15 * D2R)) return 'tongs at its toggle (fully stretched)';
      if (th / n < lam * Math.sin(20 * D2R)) return 'tongs fully closed';
      return null;
    },
    parts: (q, ctx) => {
      const f = C.fk(q, ctx), T = tongs(f), out = [], L = T.L, h = T.h, F = P.faces, dz = P.layer;
      const blk = (t0, t1, nm, rr) => ({ kind: 'plate', role: 'link', name: nm, c: V.scale(V.unit(T.d((t0 + t1) / 2, 0)), rr), z: V.unit(T.d((t0 + t1) / 2, 0)),
        x: T.g, size: [P.block * D2R * rr, 2 * hMax * D2R * rr], t: 3 });
      out.push({ kind: 'plate', role: 'fixed-scapula', name: 'base on the scapula handler', c: V.scale(f.p1, F[0] - 3), z: f.p1, x: ctx.attach.scapDir([1, 0, 0]), size: [44, 32], t: 3 });
      out.push({ kind: 'hub', role: 'active', name: 'J1', c: V.scale(f.p1, F[0]), axis: f.p1, r: P.hub_r, h: P.stack });
      out.push(blk(-P.block, 0, 'end block 1 (link 1)', P.rho[0] - 3));
      for (let k = 0; k < n; k++) {
        out.push({ kind: 'arc', role: 'link', name: `tongs link A${k}`, pts: line(T, k * L, h, (k + 1) * L, -h, 0), r: 1.6 });
        out.push({ kind: 'arc', role: 'link', name: `tongs link B${k}`, pts: line(T, k * L, -h, (k + 1) * L, h, dz), r: 1.6 });
      }
      for (let k = 0; k <= n; k++) for (const c of [h, -h]) {
        const p = T.d(k * L, c, dz / 2), slot = (k === 0 || k === n) && c < 0;
        out.push({ kind: 'hub', role: 'passive', name: slot ? `end pivot ${k} (in the arc slot)` : `side pivot ${k}${c > 0 ? '+' : '-'}`,
                   c: V.madd(p, V.unit(p), -3), axis: V.unit(p), p0: p, r: 2.6, h: 6 });
      }
      for (let k = 0; k < n; k++) {
        const p = T.d((k + 0.5) * L, 0, dz / 2);
        out.push({ kind: 'hub', role: k === 0 ? 'active' : 'passive', name: k === 0 ? 'J2 sensor (first centre pivot)' : `centre pivot ${k}`,
                   c: V.madd(p, V.unit(p), -3), axis: V.unit(p), p0: p, r: k === 0 ? 3.4 : 2.6, h: 6 });
      }
      out.push(blk(T.th, T.th + P.block, 'end block 2 (link 2)', P.rho[1] - 3));
      out.push({ kind: 'hub', role: 'active', name: 'J3', c: V.scale(f.p3, F[1]), axis: f.p3, r: P.hub_r, h: P.stack });
      const harm = ctx.armAxis, ng = P.neck_deg * D2R;
      const nk = V.unit(V.add(V.scale(f.p3, Math.cos(ng)), V.scale(V.unit(V.reject(harm, f.p3)), Math.sin(ng))));
      const neckEnd = V.scale(nk, F[1] + 1), cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47);
      out.push({ kind: 'arc', role: 'fixed-arm', name: 'neck', u: f.p3, v: nk, r0: F[1] + 1, r1: F[1] + 1, r: 3 });
      out.push({ kind: 'link', role: 'fixed-arm', name: 'neck to cuff', a: neckEnd, b: cuffTop, r: 3 });
      out.push({ kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 });
      out.push({ kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 });
      return out;
    }
  });
})();
