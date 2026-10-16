/* minarc-stop-knuckle-4r (variant B) under the KIT fold rule with the BUILDABLE J2 stop - the pin-knee chain (J1 / J2 on GH
 * rays, J3 tilted toward the skin normal, a flat two-pin knee closing member 3 on the cuff) with link 1 split by a 4th,
 * PASSIVE, sensed O20 hub K held on its stop A by a preloaded clock spring (0.3 x 5 mm strip, cap 6 mm taller), and a
 * dowel-in-slot stop on J2's OWN angle q2. While the J1-J3 angle th stays inside [thLo, thHi] (5+ deg of J1-J3 fold
 * margin, the kit's rule) K stays on stop A (a rigid 3R); past it J2 sits on its stop and the arm opens K to the smallest
 * rotation that closes the chain (closed form, <= stop B). Exactly docs/concepts/models/minarc-stop-knuckle-4r-kitrule.py
 * (phys 1) at CMA stream LB1 best (11.22 near-touch on Bench(60,160) fast; kit fold rule, physical q2 stop, hub K cap +6 mm) (axis directions, line points, hub levels, knee level, link centrelines exported from the
 * model's fit on Bench(60,160)). Red = K would pass stop B / the knee outside its window. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 94.7751, "el1": 67.1851, "az2": 44.7138, "el2": 43.097, "wd": 54.2545, "wa": -11.0155, "b3": 0.4056, "lE": 63.8584, "lc": 25.501, "phiE": 1.5965, "phib": -74.4542, "stk": 4.8639, "ang_min": 27.7418, "bk1": 28.3208, "bk2": 46.7062, "sK": -1.0, "a1max": 67.5814, "smlo": 5.0, "smhi": 7.2738, "capK": 6.0};
  const G = {"u": [[0.03228, 0.92176, 0.38641], [-0.47039, 0.64397, 0.60335], [-0.11085, -0.3546, 0.92842]], "uK": [-0.17806, 0.98269, -0.05112], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-1.4097, -21.53524, -8.39347]], "sa": [0.04204, -0.93502, -0.3521], "st": [0.99295, 0.0, 0.11855], "sn": [-0.11085, -0.3546, 0.92842], "A": [35.753, 67.421], "branch": -1.0, "m": [-21.31778, 2.31562, 0.0], "f": [49.91, 59.91, 88.65], "fK": 55.17, "capK": 6.0, "tr": 97.97, "tp": 2.182, "RUN": 0.5, "SING": 5.0, "hr": [10.0, 10.0, 10.0], "A0": [3.04035, -81.22078, -30.65844], "A0m": [4.44347, -61.28829, -22.8779], "Bm": [-19.66404, -67.67865, -28.1969], "eE": [0.06969, -0.93465, -0.34866], "eK": [-0.94536, -0.25059, -0.20858], "psiA": -52.983, "dKB": 77.0901, "thLo": 36.6687, "thHi": 95.9003, "q2s": [97.0657, -18.5102], "L1a": [[-3.51, 51.77, 10.11], [-4.76, 55.73, 8.74]], "L1b": [[-15.89, 56.84, 7.12], [-15.78, 49.73, 9.61], [-17.54, 49.14, 12.99], [-19.26, 48.33, 16.41], [-20.96, 47.26, 19.85], [-22.63, 46.01, 23.34], [-25.83, 47.37, 28.59]], "L2": [[-30.06, 34.04, 44.75], [-28.24, 29.53, 44.16], [-28.62, 27.43, 46.94], [-28.67, 24.92, 49.25], [-28.55, 22.21, 51.31], [-28.25, 19.32, 53.09], [-28.09, 16.46, 55.17], [-28.12, 13.62, 57.72], [-27.98, 10.55, 60.06], [-27.61, 7.28, 61.98], [-27.19, 3.88, 63.91], [-26.76, 0.33, 65.91], [-26.12, -3.37, 67.57], [-25.19, -7.15, 68.56], [-24.08, -10.96, 69.09], [-22.97, -14.86, 69.76], [-21.7, -18.76, 69.99], [-20.35, -22.7, 70.1], [-18.96, -26.71, 70.14], [-17.46, -30.72, 69.92], [-16.55, -36.24, 72.48], [-15.87, -43.34, 76.99]]};
  const u = G.u, c = G.c, uK = G.uK, sn = G.sn, sa = G.sa, st = G.st, a1 = G.A[0], a2 = G.A[1], hub = 12.25, rad = 10;
  const wrapR = a => { a = (a + Math.PI) % (2 * Math.PI); return (a < 0 ? a + 2 * Math.PI : a) - Math.PI; };
  const pe = P.phiE * D2R, pb = P.phib * D2R, lE = P.lE, lc = P.lc;
  const A02 = [G.m[0] + lE * Math.cos(pe), G.m[1] + lE * Math.sin(pe)], B2 = [A02[0] + lc * Math.cos(pb), A02[1] + lc * Math.sin(pb)];
  const kbr = Math.sign(wrapR(pe - Math.atan2(B2[1] - G.m[1], B2[0] - G.m[0]))) || 1;
  const vref = V.unit(V.cross(u[2], [0.3, 0.5, 0.8]));
  const cb = x => Math.cos(x * D2R), sb = x => Math.sin(x * D2R);
  /** physical J2 stop: th (deg) inside [thLo, thHi] -> K on stop A (state 0); else J2 locked on its q2 stop, K opens */
  const dot = V.dot;
  function ik(Q) {
    const [u1, u2, u3] = u, w = M.mulv(Q, u3), th = V.angle(w, u1);
    if (th >= G.thLo && th <= G.thHi) {
      const c12 = dot(u1, u2), b1 = dot(w, u1), b2 = cb(a2), det = 1 - c12 * c12;
      const al = (b1 - c12 * b2) / det, be = (b2 - c12 * b1) / det, cr = V.cross(u1, u2);
      const g2 = (1 - al * al - be * be - 2 * al * be * c12) / dot(cr, cr);
      let pick = null;
      for (const sg of [1, -1]) {
        const z = V.madd(V.add(V.scale(u1, al), V.scale(u2, be)), cr, sg * Math.sqrt(Math.max(g2, 0)));
        const q1 = K.axisAngle(u1, z, w), q2 = K.axisAngle(u2, u3, z), p2 = M.mulv(M.rot(u1, q1), u2);
        const br = Math.sign(dot(p2, V.cross(u1, w)));
        if (pick === null || br === G.branch) pick = [q1, q2];
      }
      return { q1: pick[0], dK: 0, q2: pick[1], ok: g2 > 0, L: { state: 0 } };
    }
    const state = th > G.thHi ? 1 : -1, q2s = state === 1 ? G.q2s[1] : G.q2s[0], p = M.mulv(M.rot(u2, q2s), u3);
    const A0 = dot(u1, uK) * dot(uK, p), Bk = dot(u1, p) - A0, Ck = dot(u1, V.cross(uK, p));
    const x = (cb(th) - A0) / Math.hypot(Bk, Ck), f0 = Math.atan2(Ck, Bk) / D2R, sp = Math.sign(G.psiA);
    let dK = sp * G.dKB, ok = false;
    if (Math.abs(x) <= 1) {
      const g = Math.acos(x) / D2R; let best = Infinity;
      for (const r0 of [f0 - g, f0 + g]) { const r = K.wrap180(r0); if (r * sp >= -1e-9 && Math.abs(r) < best) best = Math.abs(r); }
      if (best <= G.dKB + 1e-9) { dK = sp * best; ok = true; }
    }
    const q1 = K.axisAngle(u1, M.mulv(M.rot(uK, dK), p), w);
    return { q1, dK, q2: q2s, ok, L: { state } };
  }
  function chain(q1, dK, q2, q3) {
    const R1 = M.rot(u[0], q1), R1b = M.mul(R1, M.rot(uK, dK)), R12 = M.mul(R1b, M.rot(u[1], q2)), R3 = M.rot(u[2], q3), R123 = M.mul(R12, R3);
    const t3 = M.mulv(R12, V.sub(c[2], M.mulv(R3, c[2])));
    return { R1, R1b, R12, R123, t3 };
  }
  function knee(s) {
    const vx = B2[0] - s[0], vy = B2[1] - s[1], d = Math.hypot(vx, vy), gam = Math.atan2(vy, vx);
    const ca = (lE * lE + d * d - lc * lc) / (2 * lE * Math.max(d, 1e-9)), al = Math.acos(Math.max(-1, Math.min(1, ca)));
    const th = gam + kbr * al, pa = [s[0] + lE * Math.cos(th), s[1] + lE * Math.sin(th)];
    const wx = B2[0] - pa[0], wy = B2[1] - pa[1], psi = Math.atan2(wy, wx);
    const cosk = ((s[0] - pa[0]) * wx + (s[1] - pa[1]) * wy) / (lE * lc), ang = Math.acos(Math.max(-1, Math.min(1, cosk))) / D2R;
    return { th, pa, psi, ang, d, phi: wrapR(th - pe), span: d >= Math.abs(lE - lc) + 1 && d <= lE + lc - 1 };
  }
  const Qof = ctx => M.mul(M.T(ctx.S), ctx.H);
  function solve(ctx) {
    const Q = Qof(ctx), k = ik(Q), R12 = M.mul(M.mul(M.rot(u[0], k.q1), M.rot(uK, k.dK)), M.rot(u[1], k.q2));
    const q3 = K.axisAngle(u[2], vref, M.mulv(M.T(R12), M.mulv(Q, vref))), X = chain(k.q1, k.dK, k.q2, q3);
    const sv = M.mulv(M.T(Q), X.t3), s = [V.dot(sv, sa), V.dot(sv, st), V.dot(sv, sn)], kn = knee(s);
    const R = x => K.wrap180(x / D2R);
    return [k.q1, k.dK, k.q2, K.wrap180(q3 + kn.phi / D2R), R(wrapR(kn.psi - pb - kn.phi)), R(wrapR(kn.psi - pb))];
  }
  function fk(q) {
    const X = chain(q[0], q[1], q[2], q[3]), Rm3 = X.R123, pa = V.add(M.mulv(Rm3, G.A0), X.t3);
    const R6 = M.mul(Rm3, M.rot(sn, q[4])), t6 = V.sub(pa, M.mulv(R6, G.A0m));
    const pbW = V.add(M.mulv(R6, G.Bm), t6), R5 = M.mul(R6, M.rot(sn, -q[5])), t5 = V.sub(pbW, M.mulv(R5, G.Bm));
    return Object.assign(X, { Rm3, R6, t6, R5, t5, pa, pb: pbW });
  }
  const check = (q, ctx) => {
    const Q = Qof(ctx), k = ik(Q);
    if (!k.ok) return k.L.state ? `J2 on its q2 stop: K would pass stop B (a1max ${P.a1max} deg)` : 'chain cannot close';
    const F = fk(q), sv = M.mulv(M.T(Q), F.t3), kn = knee([V.dot(sv, sa), V.dot(sv, st)]);
    if (!kn.span) return 'knee span: the drift is beyond lE + lc';
    if (kn.ang < P.ang_min || kn.ang > 180 - P.ang_min) return `knee angle ${kn.ang.toFixed(0)} deg outside [${P.ang_min}, ${180 - P.ang_min}]`;
    return null;
  };
  const closes = (q, ctx) => { const r = C.residual(q, ctx); return Math.max(...r.map(Math.abs)) <= 0.5; };
  const solveC = (ctx, qPrev) => { const q = solve(ctx); return (!qPrev || closes(q, ctx)) ? q : K.dls(C, ctx, qPrev, { iters: 40 }).q; };
  const C = {
    id: 'minarc-stop-knuckle-4r', name: 'Min-arc stop knuckle on the pin knee: spring-held passive K in link 1, J2 dowel stop on q2 (kit fold rule)',
    dof: { active: 3, passive: 3 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'K (passive, spring + stops)', 'J2', 'J3', 'knee pin a', 'knee pin b'], qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve: solveC,
    residual: (q, ctx) => { const F = fk(q); return M.rotErrDeg(F.R5, Qof(ctx)).concat(F.t5); },
    check,
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), F = fk(q);
      const on = (R, p) => W(M.mulv(R, p)), I = M.I3();
      const h1 = { kind: 'hub', role: 'active', name: 'J1 (axis on a GH ray)', c: W(V.scale(u[0], G.f[0])), axis: Wd(u[0]), r: rad, h: hub };
      const hK = { kind: 'hub', role: 'passive', name: 'K (O20, passive, sensed; clock-spring cap, stop A)', c: on(F.R1, V.scale(uK, G.fK)), axis: Wd(M.mulv(F.R1, uK)), r: rad, h: hub + (G.capK || 0) };
      const h2 = { kind: 'hub', role: 'active', name: 'J2 (axis on a GH ray, dowel-in-slot stop on q2)', c: on(F.R1b, V.scale(u[1], G.f[1])), axis: Wd(M.mulv(F.R1b, u[1])), r: rad, h: hub };
      const h3 = { kind: 'hub', role: 'active', name: 'J3 (skin-normal tilt, line misses GH)', c: on(F.R12, V.madd(c[2], u[2], G.f[2])), axis: Wd(M.mulv(F.R12, u[2])), r: rad, h: hub,
                   p0: on(F.R12, c[2]) };
      const n3 = Wd(M.mulv(F.Rm3, sn)), lvl = (p, h) => V.madd(W(p), n3, h), kz = G.tr + G.tp + G.RUN + G.tp / 2;
      const rim = W(V.add(M.mulv(F.Rm3, V.add(V.madd(c[2], sn, G.f[2] + 1.5), V.scale(G.eE, rad))), F.t3));
      const arm = p => M.mulv(ctx.H, p), padC = arm(V.madd(G.Bm, sn, G.tr + G.tp / 2)), padN = M.mulv(ctx.H, sn), lat = arm([G.Bm[0], -150, 50]);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base on the scapula handler', c: V.madd(h1.c, h1.axis, -3), z: h1.axis, x: ctx.attach.scapDir([1, 0, 0]), size: [40, 30], t: 3 },
        h1,
        { kind: 'arc', role: 'link', name: 'link 1a (8 x 3 strap, J1 -> K)', pts: (G.L1a.length ? G.L1a : [V.scale(u[0], G.f[0]), V.scale(uK, G.fK)]).map(p => on(F.R1, p)), r: 2.5 },
        hK,
        { kind: 'arc', role: 'link', name: 'link 1b (8 x 3 strap, K -> J2)', pts: G.L1b.map(p => on(F.R1b, p)), r: 2.5 },
        h2,
        { kind: 'arc', role: 'link', name: 'link 2 (8 x 3 strap, fitted)', pts: G.L2.map(p => on(F.R12, p)), r: 2.5 },
        h3,
        { kind: 'link', role: 'link', name: 'E strap (member 3: hub 3 lower plate -> pin a)', a: rim, b: lvl(F.pa, G.tr + 1.5), r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'knee pin a (iglidur pin, parallel to J3)', c: lvl(F.pa, G.tr), axis: n3, r: 6, h: P.stk, p0: lvl(F.pa, G.tr) },
        { kind: 'link', role: 'link', name: 'knee link (flat Ti plate)', a: lvl(F.pa, kz), b: lvl(F.pb, kz), r: 3 },
        { kind: 'hub', role: 'passive', name: 'knee pin b (iglidur pin, parallel to J3)', c: lvl(F.pb, G.tr), axis: n3, r: 6, h: P.stk, p0: lvl(F.pb, G.tr) },
        { kind: 'plate', role: 'fixed-arm', name: 'arm pad (on the cuff / BOTTOM)', c: padC, z: padN, x: arm(sa), size: [14, 14], t: G.tp },
        { kind: 'link', role: 'fixed-arm', name: 'BOTTOM bar to the cuff (schematic)', a: V.madd(padC, padN, -2), b: lat, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: V.scale(ctx.armAxis, 155), axis: ctx.armAxis, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  };
  K.register(C);
})();
