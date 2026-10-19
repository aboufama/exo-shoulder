/* rollcone-hubspot-pinknee-3r - H1's pin-knee 3R (O20 J1 on the acromion top, O20 J3 on the lateral arm, flat two-pin
 * MR63ZZ cuff knee) with hub 2 DELETED: J2 is a strap-held ROLLING CONE PAIR, apex at GH, at H1's hub-2 spot. The SUN
 * band (cone about uK, fixed in link 1) and the PLANET band (cone about v2, fixed in link 2) touch along one radial line
 * (drawn) = the instantaneous J2 axis; crossed straps make them roll without slip: link 2 = link 1 R(uK, rho y) R(v2, y)
 * R(u2, q2_rest). 3 ACTIVE (q1, the roll y, q3) + 2 passive knee pins; no hub, crank, spring or loop at J2.
 * Exactly the model docs/concepts/models/rollcone-hubspot-pinknee-3r.py at the shown configuration (geometry exported by
 * its 'viz' mode on Bench(60,160): axes, rest roll, rho, band levels, knee, fitted link points). IK = the model's: th(y)
 * = angle(u1, J3 direction) tabulated on the rest segment, y interpolated, q1 / q3 / knee closed form. Red = the
 * instantaneous dyad (u1, contact line, J3) within the 5 deg fold margin or off the segment, or the knee out of its window. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"alpha_s": 8.73, "alpha_p": 14.23, "beta": 42.0, "lE": 59.5534, "lc": 28.2401, "phiE": -5.8107, "phib": -54.914, "stk": 6.0, "ang_min": 30.4611};
  const G = {"u": [[0.08518, 0.898017, 0.431637], [-0.577607, 0.672703, 0.462429], [-0.09125, -0.198527, 0.975838]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-1.793, -10.319, -2.267]], "sa": [0.018483, -0.980095, -0.197664], "st": [0.995656, 0.0, 0.093103], "sn": [-0.09125, -0.198527, 0.975838], "m": [-9.95, 1.99, 0.0], "f": [49.91, 61.84, 76.1], "Rb": [61.09, 62.59], "bh": 8.0, "tr": 84.72, "tp": 2.75, "RUN": 0.5, "uK": [-0.500706, 0.776691, 0.382157], "v2": [-0.673592, 0.471025, 0.56957], "cK": [-0.577607, 0.672703, 0.462429], "q2r": -4.3316, "rho": 1.61957, "alpha": [8.73, 14.23], "ylim": [-36.25, 40.75], "yspan": [-26.08, 34.12], "A0": [-6.7, -68.39, -14.54], "A0m": [-4.9, -58.63, -12.39], "Bm": [-27.61, -74.54, -17.75], "eE": [-0.082414, -0.97506, -0.206075], "eK": [-0.804112, -0.563364, -0.189804], "FM": 5.0, "L1": [[-5.71, 46.03, 21.01], [-12.98, 45.77, 22.15], [-21.41, 46.69, 23.95], [-29.38, 44.56, 24.26], [-8.91, 44.72, 22.96], [-16.68, 45.26, 24.62], [-25.39, 45.46, 26.28], [-5.12, 44.47, 24.13], [-12.48, 44.54, 25.59], [-20.64, 44.69, 27.26], [-28.9, 43.05, 28.04], [-8.4, 43.53, 26.32], [-16.22, 44.07, 28.25], [-24.59, 43.45, 29.7]], "L2": [[-39.34, 37.97, 30.46], [-36.92, 27.8, 42.58], [-34.52, 16.77, 55.72], [-28.68, 2.55, 65.3], [-19.7, -13.17, 69.16], [-35.44, 31.35, 38.06], [-33.77, 21.55, 51.45], [-29.01, 8.48, 62.27], [-20.57, -6.57, 66.61], [-34.35, 35.0, 34.09], [-32.89, 25.87, 47.18], [-29.18, 14.03, 59.08], [-21.88, -0.48, 65.75], [-35.17, 40.74, 31.95], [-31.86, 29.78, 42.91], [-29.01, 19.12, 55.42], [-22.92, 5.48, 64.21], [-13.97, -9.35, 66.81]], "gap": 18.92, "reach": 0.7438};
  const u = G.u, c = G.c, sn = G.sn, sa = G.sa, st = G.st, hub = 12.25, rad = 10;
  const wrapR = a => { a = (a + Math.PI) % (2 * Math.PI); return (a < 0 ? a + 2 * Math.PI : a) - Math.PI; };
  const pe = P.phiE * D2R, pb = P.phib * D2R, lE = P.lE, lc = P.lc;
  const A02 = [G.m[0] + lE * Math.cos(pe), G.m[1] + lE * Math.sin(pe)], B2 = [A02[0] + lc * Math.cos(pb), A02[1] + lc * Math.sin(pb)];
  const kbr = Math.sign(wrapR(pe - Math.atan2(B2[1] - G.m[1], B2[0] - G.m[0]))) || 1;
  const vref = V.unit(V.cross(u[2], [0.3, 0.5, 0.8]));
  const R2r = M.rot(u[1], G.q2r), w0 = M.mulv(R2r, u[2]), v2h = M.mulv(M.T(R2r), G.v2);
  const Rroll = y => M.mul(M.rot(G.uK, G.rho * y), M.rot(G.v2, y));
  const ys = [], ths = [];
  for (let y = G.ylim[0]; y <= G.ylim[1] + 1e-9; y += 0.25) { ys.push(y); ths.push(V.angle(u[0], M.mulv(Rroll(y), w0))); }
  const inc = ths[ths.length - 1] > ths[0], TH = inc ? ths : ths.slice().reverse(), YS = inc ? ys : ys.slice().reverse();
  function yOf(th) {
    if (th <= TH[0]) return { y: YS[0], out: true };
    if (th >= TH[TH.length - 1]) return { y: YS[YS.length - 1], out: true };
    let lo = 0, hi = TH.length - 1;
    while (hi - lo > 1) { const mid = (lo + hi) >> 1; if (TH[mid] <= th) lo = mid; else hi = mid; }
    const f = (th - TH[lo]) / (TH[hi] - TH[lo]); return { y: YS[lo] + f * (YS[hi] - YS[lo]), out: false, mseg: Math.min(th - TH[0], TH[TH.length - 1] - th) };
  }
  const Qof = ctx => M.mul(M.T(ctx.S), ctx.H);
  function ik(Q) {
    const w = M.mulv(Q, u[2]), th = V.angle(w, u[0]), r = yOf(th), wl = M.mulv(Rroll(r.y), w0);
    const q1 = K.axisAngle(u[0], wl, w), cx = M.mulv(M.rot(G.uK, G.rho * r.y), G.cK);
    const a1 = V.angle(cx, u[0]), a2 = V.angle(cx, wl), tl = V.angle(wl, u[0]);
    const mdy = Math.min(tl - Math.abs(a1 - a2), Math.min(a1 + a2, 360 - a1 - a2) - tl);
    return { q1, y: r.y, ok: !r.out && mdy >= G.FM && r.mseg >= G.FM, margin: r.out ? -1 : Math.min(mdy, r.mseg) };
  }
  function chain(q1, y, q3) {
    const R1 = M.rot(u[0], q1), R12 = M.mul(M.mul(R1, Rroll(y)), R2r), R3 = M.rot(u[2], q3), R123 = M.mul(R12, R3);
    const t3 = M.mulv(R12, V.sub(c[2], M.mulv(R3, c[2])));
    return { R1, t1: [0, 0, 0], R12, t2: [0, 0, 0], R123, t3 };
  }
  function knee(s) {
    const vx = B2[0] - s[0], vy = B2[1] - s[1], d = Math.hypot(vx, vy), gam = Math.atan2(vy, vx);
    const ca = (lE * lE + d * d - lc * lc) / (2 * lE * Math.max(d, 1e-9)), al = Math.acos(Math.max(-1, Math.min(1, ca)));
    const th = gam + kbr * al, pa = [s[0] + lE * Math.cos(th), s[1] + lE * Math.sin(th)];
    const wx = B2[0] - pa[0], wy = B2[1] - pa[1], psi = Math.atan2(wy, wx);
    const cosk = ((s[0] - pa[0]) * wx + (s[1] - pa[1]) * wy) / (lE * lc), ang = Math.acos(Math.max(-1, Math.min(1, cosk))) / D2R;
    return { th, pa, psi, ang, d, phi: wrapR(th - pe), span: d >= Math.abs(lE - lc) + 1 && d <= lE + lc - 1 };
  }
  function solve(ctx) {
    const Q = Qof(ctx), k = ik(Q), R12 = M.mul(M.mul(M.rot(u[0], k.q1), Rroll(k.y)), R2r);
    const q3 = K.axisAngle(u[2], vref, M.mulv(M.T(R12), M.mulv(Q, vref))), X = chain(k.q1, k.y, q3);
    const sv = M.mulv(M.T(Q), X.t3), s = [V.dot(sv, sa), V.dot(sv, st), V.dot(sv, sn)], kn = knee(s);
    const R = x => K.wrap180(x / D2R);
    return [k.q1, k.y, K.wrap180(q3 + kn.phi / D2R), R(wrapR(kn.psi - pb - kn.phi)), R(wrapR(kn.psi - pb))];
  }
  function fk(q) {
    const X = chain(q[0], q[1], q[2]), Rm3 = X.R123;
    const pa = V.add(M.mulv(Rm3, G.A0), X.t3);
    const R6 = M.mul(Rm3, M.rot(sn, q[3])), t6 = V.sub(pa, M.mulv(R6, G.A0m));
    const pbW = V.add(M.mulv(R6, G.Bm), t6), R5 = M.mul(R6, M.rot(sn, -q[4])), t5 = V.sub(pbW, M.mulv(R5, G.Bm));
    return Object.assign(X, { Rm3, R6, t6, R5, t5, pa, pb: pbW });
  }
  const check = (q, ctx) => {
    const Q = Qof(ctx), k = ik(Q);
    if (!k.ok) return k.margin < 0 ? 'J2 roll fold: the J1-J3 angle is off the rolling segment' : `rolling J2 within ${k.margin.toFixed(1)} deg of its fold (>= ${G.FM})`;
    const F = fk(q), sv = M.mulv(M.T(Q), F.t3), kn = knee([V.dot(sv, sa), V.dot(sv, st)]);
    if (!kn.span) return 'knee span: the drift is beyond lE + lc';
    if (kn.ang < P.ang_min || kn.ang > 180 - P.ang_min) return `knee angle ${kn.ang.toFixed(0)} deg outside [${P.ang_min.toFixed(0)}, ${(180 - P.ang_min).toFixed(0)}]`;
    if (Math.abs(V.dot(sv, sn)) > 0.5) return 'radial drift > 0.5 mm';
    return null;
  };
  const closes = (q, ctx) => { const r = C.residual(q, ctx); return Math.max(...r.map(Math.abs)) <= 0.5; };
  const solveC = (ctx, qPrev) => { const q = solve(ctx); return (!qPrev || closes(q, ctx)) ? q : K.dls(C, ctx, qPrev, { iters: 40 }).q; };
  const band = (S, R, ax, ref, Rb, g, a0, a1, name) => {
    const axis = M.mulv(S, M.mulv(R, ax)), rf = M.mulv(S, M.mulv(R, V.unit(V.reject(ref, ax)))), Rm = Rb + G.bh / 2;
    return { kind: 'rail', role: 'active', name, c: V.scale(axis, Rm * Math.cos(g * D2R)), axis, ref: rf, rho: Rm * Math.sin(g * D2R), a0, a1, r: 1.4 };
  };
  const C = {
    id: 'rollcone-hubspot-pinknee-3r', name: 'Rolling-cone J2 at the hub-2 spot on the pin-knee 3R (strap-held cone pair, apex GH)',
    dof: { active: 3, passive: 2 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'J2 roll y (planet)', 'J3', 'knee pin a', 'knee pin b'], qUnits: ['deg', 'deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve: solveC,
    residual: (q, ctx) => { const F = fk(q); return M.rotErrDeg(F.R5, Qof(ctx)).concat(F.t5); },
    check,
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), F = fk(q);
      const on = (R, t, p) => W(V.add(M.mulv(R, p), t)), I = M.I3(), Z = [0, 0, 0];
      const h1 = { kind: 'hub', role: 'active', name: 'J1 (O20, axis on a GH ray)', c: W(V.scale(u[0], G.f[0])), axis: Wd(u[0]), r: rad, h: hub };
      const ax3 = Wd(M.mulv(F.R12, u[2]));
      const h3 = { kind: 'hub', role: 'active', name: 'J3 (O20, skin-normal tilt, line misses GH)', c: on(F.R12, F.t2, V.madd(c[2], u[2], G.f[2])), axis: ax3, r: rad, h: hub,
                   p0: on(F.R12, F.t2, c[2]) };
      const x0 = Math.min(G.rho * G.yspan[0], G.rho * G.yspan[1]), x1 = Math.max(G.rho * G.yspan[0], G.rho * G.yspan[1]);
      const sun = band(S, F.R1, G.uK, G.cK, G.Rb[0], G.alpha[0], x0, x1, `sun band (cone ${G.alpha[0].toFixed(0)} deg about uK, link 1)`);
      const pl = band(S, F.R12, v2h, G.cK, G.Rb[1], G.alpha[1], -G.yspan[1], -G.yspan[0], `planet band (cone ${G.alpha[1].toFixed(0)} deg about v2, link 2)`);
      const ct = V.unit(Wd(M.mulv(F.R1, M.mulv(M.rot(G.uK, G.rho * q[1]), G.cK))));
      const n3 = Wd(M.mulv(F.Rm3, sn)), lvl = (p, h) => V.madd(W(p), n3, h);
      const kz = G.tr + G.tp + G.RUN + G.tp / 2;
      const rim = on(F.Rm3, F.t3, V.add(V.madd(c[2], sn, G.f[2] + 1.5), V.scale(G.eE, rad)));
      const arm = p => M.mulv(ctx.H, p);
      const padC = arm(V.madd(G.Bm, sn, G.tr + G.tp / 2)), padN = M.mulv(ctx.H, sn), lat = arm([G.Bm[0], -150, 50]);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base on the scapula handler', c: V.madd(h1.c, h1.axis, -3), z: h1.axis, x: ctx.attach.scapDir([1, 0, 0]), size: [40, 30], t: 3 },
        h1,
        { kind: 'arc', role: 'link', name: 'link 1 (8 x 3 strap, fitted)', pts: G.L1.map(p => on(F.R1, Z, p)), r: 2.5 },
        sun, pl,
        { kind: 'link', role: 'active', name: 'contact line = instantaneous J2 axis (crossed straps)', a: V.scale(ct, G.Rb[0] - 1), b: V.scale(ct, G.Rb[0] + G.bh + 1), r: 1.0 },
        { kind: 'arc', role: 'link', name: 'link 2 (8 x 3 strap, fitted)', pts: G.L2.map(p => on(F.R12, Z, p)), r: 2.5 },
        h3,
        { kind: 'link', role: 'link', name: 'E strap (member 3: hub 3 lower plate -> pin a)', a: rim, b: lvl(F.pa, G.tr + 1.5), r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'knee pin a (MR63ZZ pair, parallel to J3)', c: lvl(F.pa, G.tr), axis: n3, r: 6, h: P.stk, p0: lvl(F.pa, G.tr) },
        { kind: 'link', role: 'link', name: 'knee link (flat Ti plate)', a: lvl(F.pa, kz), b: lvl(F.pb, kz), r: 3 },
        { kind: 'hub', role: 'passive', name: 'knee pin b (MR63ZZ pair, parallel to J3)', c: lvl(F.pb, G.tr), axis: n3, r: 6, h: P.stk, p0: lvl(F.pb, G.tr) },
        { kind: 'plate', role: 'fixed-arm', name: 'arm pad (on the cuff / BOTTOM)', c: padC, z: padN, x: arm(sa), size: [14, 14], t: G.tp },
        { kind: 'link', role: 'fixed-arm', name: 'BOTTOM bar to the cuff (schematic)', a: V.madd(padC, padN, -2), b: lat, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: V.scale(ctx.armAxis, 155), axis: ctx.armAxis, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  };
  K.register(C);
})();
