/* skin-cam-rails - the crossed muscle-line rails with PROFILED radii and a telescoping crossing (catalogue
 * skin-cam-rails; ideated, no bench model or sweep yet). Same spherical 3R as crossed-muscle-rails (seed 1: az1 64.9,
 * el1 56.1, a12 57.4, d3 147.1, az3 -119, a23 87.9, sigma -1): carriage 1 on the scapula-fixed arch (directions on the
 * cone a12 about a1) = J1 ACTIVE; a cylindrical joint on the radial crossing axis a2 = J2 rotation ACTIVE + radial
 * ball-spline slide PASSIVE; carriage 2 on the arm-fixed collar (cone a23 about a3), which runs on to BOTTOM = J3
 * ACTIVE. The rails are 3-D curves: rail 1 at r1(phi) = skin under it + 2.5 mm in the scapula frame (low over the
 * acromion, high over the supraspinatus / spine), rail 2 at r2(psi) = max(its own skin + 2.5, r1 + Delta 12 at the
 * crossings that use it), each smoothed by a +-6 mm moving max (spec PROFILES). A radial slide does not change the
 * orientation a spherical chain passes on, so the slide s = r2(psi) - r1(phi) - Delta is set by the two profiles at the
 * crossing: 3 ACTIVE + 1 PASSIVE. Skin proxy (no fit yet): scapula frame 40 mm at the acromion rising to 58 / 68 mm
 * medially (catalogue: arch 37-45 over the acromion, 55-60 over the spine); arm frame 46 mm over the cap, 43 / sin
 * (angle from the arm axis) down the arm, + up to 6 mm medially. Rail extents = the crossing's travel over this loop
 * (as crossed-muscle-rails). Out of range: no crossing, rails crossing at < 25 deg, a carriage past its rail end, the
 * slide past its 15 mm stroke, a rail direction whose skin needs > 85 mm. Closed form (KIN.sph3r) + the profile slide. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, R2D = K.R2D, D2R = K.D2R;
  const P = { az1: 64.9, el1: 56.1, a12: 57.4, d3: 147.1, az3: -119.0, a23: 87.9, sigma: -1, clear: 2.5, delta: 12,
              stroke: 15, r_max: 85, smooth_mm: 6, car: [26, 14, 6], gamma_min: 25, Lmax: 200, hub_r: 10,
              bar: [0, -70, 67.5], cuff_at: 165 };
  const a1 = V.unit(K.bvec(P.az1, P.el1)), a3 = V.unit(K.wdir(P.d3, P.az3)), ref1 = V.perp(a1), ref3 = V.perp(a3);
  const C = K.sph3r(a1, a3, P.a12, P.a23, P.sigma);
  // skin proxies (mm from GH) in the scapula frame and in the arm (band humerus) frame
  const acr = V.unit([-0.3, 0.9, 0.3]), sstep = x => { x = Math.max(0, Math.min(1, x)); return x * x * (3 - 2 * x); };
  const skinS = d => 40 + 18 * sstep(V.angle(d, acr) / 55) + 10 * Math.max(0, -d[2]);
  const skinA = d => Math.max(46, 43 / Math.max(Math.sin(V.angle(d, [0, -1, 0]) * D2R), 0.3)) + 6 * Math.max(0, -d[2]);
  const dir1 = phi => K.onCone(a1, ref1, P.a12, phi), dir3 = psi => K.onCone(a3, ref3, P.a23, psi);
  const idx = a => (((Math.round(a) + 180) % 360) + 360) % 360;                       // 1-deg table index of an angle (deg)
  const tab = f => { const t = []; for (let i = 0; i < 360; i++) t.push(f(i - 180)); return t; };
  function smooth(t, rho) {                                                             // +-6 mm moving max, then a mean
    const w = Math.max(1, Math.round(P.smooth_mm / rho * R2D)), mx = t.map((_, i) => { let m = -1e9; for (let k = -w; k <= w; k++) m = Math.max(m, t[(i + k + 360) % 360]); return m; });
    return mx.map((_, i) => { let s = 0; for (let k = -w; k <= w; k++) s += mx[(i + k + 360) % 360]; return s / (2 * w + 1) + 0.5; });
  }
  const rho1 = 50 * Math.sin(P.a12 * D2R), rho2 = 60 * Math.sin(P.a23 * D2R);
  const need1 = tab(phi => skinS(dir1(phi)) + P.clear), r1t = smooth(need1, rho1);
  function cross(ctx, q) {                                                              // crossing coordinates (crossed-muscle-rails)
    const f = C.fk(q, ctx), A1 = M.mulv(ctx.S, a1), A3 = M.mulv(ctx.H, a3);
    const phi = K.axisAngle(a1, ref1, M.mulv(M.T(ctx.S), f.p2)), psi = K.axisAngle(a3, ref3, M.mulv(M.T(ctx.H), f.p2));
    const t1 = V.unit(V.cross(A1, f.p2)), t3 = V.unit(V.cross(A3, f.p2));
    return { f, A1, A3, phi, psi, t1, t3, gamma: Math.acos(Math.min(1, Math.abs(V.dot(t1, t3)))) * R2D };
  }
  const half = rho => P.car[0] / 2 / rho * R2D + 2;
  const { ext, r2t, need2 } = (() => {
    const out = { phi: [], psi: [] }, need2 = tab(psi => skinA(dir3(psi)) + P.clear), up = need2.slice();
    for (const fr of K.motion(240)) {
      const ctx = K.makeCtx(fr.pose, fr.t); if (C.margin(ctx) < 0) continue;
      const c = cross(ctx, C.solve(ctx)); if (c.gamma < P.gamma_min) continue;
      for (const k of ['phi', 'psi']) { const a = out[k], v = c[k]; a.push(a.length ? a[a.length - 1] + K.wrap180(v - a[a.length - 1]) : v); }
      const j = idx(c.psi); up[j] = Math.max(up[j], r1t[idx(c.phi)] + P.delta);
    }
    const span = (a, h) => {
      const s = [...a].sort((x, y) => x - y), med = s[s.length >> 1];
      let lo = s[0] - h, hi = s[s.length - 1] + h;
      if (hi - lo > P.Lmax) { lo = Math.max(lo, med - P.Lmax / 2); hi = Math.min(hi, lo + P.Lmax); }
      return [lo, hi];
    };
    return { ext: { phi: span(out.phi, half(rho1)), psi: span(out.psi, half(rho2)) }, r2t: smooth(up, rho2), need2 };
  })();
  const r1 = phi => r1t[idx(phi)], r2 = psi => r2t[idx(psi)];
  const inside = (v, [lo, hi], h) => { const m = (lo + hi) / 2, d = K.wrap180(v - m); return Math.abs(d) <= (hi - lo) / 2 - h; };
  const slide = c => r2(c.psi) - r1(c.phi) - P.delta;
  const railPts = (lo, hi, dir, r, frame) => { const o = [], n = Math.max(8, Math.ceil((hi - lo) / 3));
    for (let i = 0; i <= n; i++) { const a = lo + (hi - lo) * i / n; o.push(V.scale(M.mulv(frame, dir(a)), r(K.wrap180(a)))); } return o; };

  K.register({
    id: 'skin-cam-rails',
    name: 'Skin-profiled cam rails + sliding crossing',
    dof: { active: 3, passive: 1 },
    params: Object.assign({ rail1_extent_deg: ext.phi, rail2_extent_deg: ext.psi }, P),
    q0: ctx => { const q = C.solve(ctx); return q.concat([slide(cross(ctx, q))]); },
    qNames: ['J1 carriage on the arch', 'J2 crossing rotation', 'J3 carriage on the collar', 'J2 radial slide'],
    qUnits: ['deg', 'deg', 'deg', 'mm'], resUnits: ['deg', 'deg', 'deg', 'mm'],
    solve: ctx => { const q = C.solve(ctx); return q.concat([slide(cross(ctx, q))]); },
    residual: (q, ctx) => C.residual(q, ctx).concat([q[3] - slide(cross(ctx, q))]),
    check: (q, ctx) => {
      if (C.margin(ctx) < 0) return 'the rails do not cross: the arm is out of the chain\'s reach';
      const c = cross(ctx, q);
      if (c.gamma < P.gamma_min) return `rails cross at ${c.gamma.toFixed(0)} deg (tangent = 3R singularity)`;
      if (!inside(c.phi, ext.phi, half(rho1) - 2)) return 'carriage 1 past the end of the arch';
      if (!inside(c.psi, ext.psi, half(rho2) - 2)) return 'carriage 2 past the end of the collar';
      if (need1[idx(c.phi)] > P.r_max || need2[idx(c.psi)] > P.r_max) return 'crossing over skin deeper than 85 mm (rail unusable there)';
      if (q[3] > P.stroke) return `slide post ${q[3].toFixed(0)} mm (stroke 15)`;
      if (q[3] < -0.5) return 'carriages collide (negative slide)';
      return null;
    },
    parts: (q, ctx) => {
      const c = cross(ctx, q), p2 = c.f.p2, harm = ctx.armAxis, R1 = r1(c.phi), R2 = R1 + P.delta + q[3];
      const pts1 = railPts(ext.phi[0], ext.phi[1], dir1, r1, ctx.S), pts2 = railPts(ext.psi[0], ext.psi[1], dir3, r2, ctx.H);
      const bar = M.mulv(ctx.H, P.bar), end = V.norm(V.sub(pts2[0], bar)) < V.norm(V.sub(pts2[pts2.length - 1], bar)) ? pts2[0] : pts2[pts2.length - 1];
      const cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(bar, harm)), 47);
      return [
        { kind: 'arc', role: 'fixed-scapula', name: 'rail 1: profiled acromial arch (exo-scapula)', pts: pts1, r: 3 },
        { kind: 'carriage', role: 'active', name: 'J1: carriage 1 on the arch', c: V.scale(p2, R1 + 3), x: c.t1, z: p2, size: P.car },
        { kind: 'hub', role: 'active', name: 'J2: crossing bearing', c: V.scale(p2, R1 + 6), axis: p2, r: P.hub_r, h: 4 },
        { kind: 'telescope', role: 'passive', name: 'J2 radial ball-spline slide (set by the profiles)', a: V.scale(p2, R1 + 10), b: V.scale(p2, R2 - 3), split: 4 + Math.max(0, q[3]) / 2, r0: 6, r1: 4 },
        { kind: 'carriage', role: 'active', name: 'J3: carriage 2 on the collar', c: V.scale(p2, R2 - 3), x: c.t3, z: p2, size: P.car },
        { kind: 'arc', role: 'fixed-arm', name: 'rail 2: profiled humeral-head collar (arm piece)', pts: pts2, r: 3 },
        { kind: 'arc', role: 'fixed-arm', name: 'collar runs on to BOTTOM', u: V.unit(end), v: V.unit(bar), r0: V.norm(end), r1: V.norm(bar), r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'BOTTOM to the cuff', a: bar, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
