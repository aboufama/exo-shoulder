/* rus-tripod-gh-centre - 3-RUS tripod that uses the wearer's own GH as the spherical centre (catalogue
 * rus-tripod-gh-centre, models/rus-tripod-gh-centre.py PARAMS; no sweep yet). Three ACTIVE crank hubs on stable
 * scapula skin whose axes are the outward skin normals and do NOT pass through GH: the dome near p* (lat 66 / lon -68),
 * the posterior scapula (0 / -112) and the top-front of the acromion (50 / 10) -> crank rc 40 -> passive U (2; first
 * axis parallel to the crank axis, second normal to it and the chord, so the strut cannot spin) -> rigid curved strut,
 * bent to hug the deltoid -> passive ball (3) on the arm strip (lateral s 150, posterior s 120 th +70, anterior s 110
 * th -70). The wearer's GH closes the loop. Per leg the closed form cos(phi - atan2(y, x)) = (rc^2 + |X|^2 - L^2) /
 * (2 rc rho) on branch br; the chord L is the model's best_L (most loop frames closed with the crank >= 15 deg off
 * collinear with the strut). 3 ACTIVE (cranks) + 15 PASSIVE. Pivot radii are schematic (rest skin + 8 mm). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = K.D2R;
  const P = { legs: [{ site: [66, -68], R: 62, rc: 40, ball: [150, 0, 52], br: 1 },
                     { site: [0, -112], R: 80, rc: 40, ball: [120, 70, 55], br: 1 },
                     { site: [50, 10], R: 56, rc: 40, ball: [110, -70, 57], br: 1 }],
              bow: 22, dead: 15, sig: 0.15, hub_r: 10, stack: 12.25, h_u: 9.15 };
  const dS = (la, lo) => [Math.cos(la * D2R) * Math.sin(lo * D2R), Math.sin(la * D2R), Math.cos(la * D2R) * Math.cos(lo * D2R)];
  const AX = V.unit(K.BODY.elbow), ZL = V.unit(V.reject(M.col(K.BODY.rest_humerus, 2), AX)), YL = V.cross(AX, ZL);
  const armPt = (s, th, r) => V.add(V.scale(AX, s), V.add(V.scale(ZL, r * Math.cos(th * D2R)), V.scale(YL, r * Math.sin(th * D2R))));
  const legs = P.legs.map(g => {
    const n = V.unit(dS(...g.site)), a = Math.abs(n[0]) < 0.9 ? [1, 0, 0] : [0, 1, 0], e1 = V.unit(V.reject(a, n));
    return { P0: V.scale(n, g.R), n, e1, e2: V.cross(n, e1), rc: g.rc, b0: armPt(...g.ball), br: g.br, L: 0, side: 1 };
  });
  function leg(g, ctx, L, phiIn) {                       // world crank centre, crank tip, ball; phi from the closed form
    const Pw = M.mulv(ctx.S, g.P0), n = M.mulv(ctx.S, g.n), e1 = M.mulv(ctx.S, g.e1), e2 = M.mulv(ctx.S, g.e2), B = M.mulv(ctx.Hb, g.b0);
    const X = V.sub(B, Pw), x = V.dot(X, e1), y = V.dot(X, e2), rho = Math.hypot(x, y);
    const rhs = (g.rc * g.rc + V.dot(X, X) - L * L) / (2 * g.rc * Math.max(rho, 1e-9));
    const phi = phiIn != null ? phiIn : (Math.atan2(y, x) + g.br * Math.acos(Math.max(-1, Math.min(1, rhs)))) * K.R2D;
    const r = V.add(V.scale(e1, Math.cos(phi * D2R)), V.scale(e2, Math.sin(phi * D2R))), c = V.madd(Pw, r, g.rc);
    const es = V.unit(V.sub(B, c)), dead = Math.acos(Math.min(1, Math.abs(V.dot(es, r)))) * K.R2D;
    return { Pw, n, c, B, phi, ok: Math.abs(rhs) <= 1, dead, es };
  }
  const loop = K.motion(90).map(f => K.makeCtx(f.pose, f.t));
  legs.forEach(g => {                                    // model best_L: closure and >= dead margin on the most frames
    const d = loop.map(ctx => V.norm(V.sub(M.mulv(ctx.Hb, g.b0), M.mulv(ctx.S, g.P0)))); let best = -1;
    for (let L = Math.max(20, Math.min(...d) - g.rc); L <= Math.max(...d) + g.rc; L += 1) {
      const s = loop.filter(ctx => { const k = leg(g, ctx, L); return k.ok && k.dead >= P.dead; }).length;
      if (s > best) { best = s; g.L = L; }
    }
    const k0 = leg(g, loop[0], g.L), w0 = V.unit(V.cross(k0.es, k0.n)), t0 = V.cross(k0.es, w0);   // bow away from GH at rest
    g.side = V.dot(t0, V.lerp(k0.c, k0.B, 0.5)) >= 0 ? 1 : -1;
  });
  function sigmaMin(m) {                                 // smallest singular value of the 3 x 3 matrix with columns m
    const A = [0, 1, 2].map(i => [0, 1, 2].map(j => V.dot(m[i], m[j]))), q = (A[0][0] + A[1][1] + A[2][2]) / 3;
    const p1 = A[0][1] ** 2 + A[0][2] ** 2 + A[1][2] ** 2, p2 = (A[0][0] - q) ** 2 + (A[1][1] - q) ** 2 + (A[2][2] - q) ** 2 + 2 * p1;
    const p = Math.sqrt(p2 / 6) || 1e-12, B = A.map((r, i) => r.map((x, j) => (x - (i === j ? q : 0)) / p));
    const det = B[0][0] * (B[1][1] * B[2][2] - B[1][2] * B[2][1]) - B[0][1] * (B[1][0] * B[2][2] - B[1][2] * B[2][0]) + B[0][2] * (B[1][0] * B[2][1] - B[1][1] * B[2][0]);
    const ph = Math.acos(Math.max(-1, Math.min(1, det / 2))) / 3;
    return Math.sqrt(Math.max(0, q + 2 * p * Math.cos(ph + 2 * Math.PI / 3)));
  }

  K.register({
    id: 'rus-tripod-gh-centre',
    name: '3-RUS tripod on the wearer\'s GH',
    dof: { active: 3, passive: 15 },
    params: Object.assign({ L: legs.map(g => g.L) }, P),
    q0: ctx => legs.map(g => leg(g, ctx, g.L).phi),
    qNames: ['crank 1 (dome)', 'crank 2 (posterior scapula)', 'crank 3 (acromion front)'], qUnits: ['deg', 'deg', 'deg'],
    resUnits: ['mm', 'mm', 'mm'],
    solve: (ctx, qp) => legs.map((g, k) => { const p = leg(g, ctx, g.L).phi; return qp ? qp[k] + K.wrap180(p - qp[k]) : p; }),
    residual: (q, ctx) => legs.map((g, k) => { const s = leg(g, ctx, g.L, q[k]); return V.norm(V.sub(s.B, s.c)) - g.L; }),
    check: (q, ctx) => {
      const s = legs.map((g, k) => leg(g, ctx, g.L, q[k]));
      for (let k = 0; k < 3; k++) if (s[k].dead < P.dead) return `crank ${k + 1} near its dead centre (in line with the strut)`;
      if (sigmaMin(s.map(x => V.cross(x.B, x.es))) / 100 < P.sig) return 'struts ill-conditioned about GH';
      return null;
    },
    parts: (q, ctx) => {
      const out = [], s = legs.map((g, k) => leg(g, ctx, g.L, q[k]));
      out.push({ kind: 'arc', role: 'fixed-scapula', name: 'base bracket (dome - posterior)', u: V.unit(s[0].Pw), v: V.unit(s[1].Pw), r0: V.norm(s[0].Pw) - 12, r1: V.norm(s[1].Pw) - 12, r: 3 });
      out.push({ kind: 'arc', role: 'fixed-scapula', name: 'base bracket (dome - acromion)', u: V.unit(s[0].Pw), v: V.unit(s[2].Pw), r0: V.norm(s[0].Pw) - 12, r1: V.norm(s[2].Pw) - 12, r: 3 });
      s.forEach((x, k) => {
        const g = legs[k], E = V.madd(x.c, V.unit(V.sub(x.B, x.c)), g.L);          // strut keeps its length: a gap shows a miss
        const ws = V.unit(V.cross(x.es, x.n)), t = V.scale(V.cross(x.es, ws), g.side);
        const pts = [0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1].map(u => V.madd(V.lerp(x.c, E, u), t, P.bow * Math.sin(Math.PI * u)));
        out.push({ kind: 'hub', role: 'active', name: `crank hub ${k + 1} (axis off GH)`, c: V.madd(x.Pw, x.n, -P.h_u), axis: x.n, p0: x.Pw, r: P.hub_r, h: P.stack });
        out.push({ kind: 'link', role: 'link', name: `crank ${k + 1}`, a: x.Pw, b: x.c, r: 4 });
        out.push({ kind: 'hub', role: 'passive', name: `U-joint ${k + 1}`, c: V.madd(x.c, x.n, -4), axis: x.n, p0: x.c, r: 6, h: 8 });
        out.push({ kind: 'arc', role: 'link', name: `curved strut ${k + 1}`, pts, r: 3 });
        out.push({ kind: 'point', role: 'passive', name: `ball ${k + 1}`, p: E, r: 7 });
        out.push({ kind: 'link', role: 'fixed-arm', name: `ball cup ${k + 1}`, a: M.mulv(ctx.Hb, armPt(P.legs[k].ball[0], P.legs[k].ball[1], P.legs[k].ball[2] - 9)), b: x.B, r: 4 });
      });
      out.push({ kind: 'strap', role: 'fixed-arm', name: 'arm strip (user cuff)', c: M.mulv(ctx.Hb, V.scale(AX, 130)), axis: M.mulv(ctx.Hb, AX),
                 ref: M.mulv(ctx.Hb, ZL), a0: -85, a1: 85, r: 48, w: 50 });
      out.push({ kind: 'point', role: 'link', name: 'GH centre (the wearer\'s joint closes the loop)', p: [0, 0, 0], r: 4 });
      return out;
    }
  });
})();
