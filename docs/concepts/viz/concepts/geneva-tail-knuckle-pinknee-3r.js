/* geneva-tail-knuckle-pinknee-3r - the pin-knee chain with link 1 split by a passive O20 knuckle K that is SLAVED to
 * q2: link 2 continues past hub 2 as a rigid tail whose roller pushes one flank on link 1a. While the J1-J3 angle th is
 * inside [thLo, thHi] K sits on stop A (a rigid 3R); past thHi the roller turns K open by the exact one-tooth contact law
 * dK(q2) (tabulated from docs/concepts/models/geneva-tail-knuckle-pinknee-3r.py), so J1, J2, J3 encoders give the pose
 * (3 active, K never read). The folded side has no tooth (J2 dowel stop). Coarse-sweep best (farm LHS, gap 30.18 fast).
 * The tail (orange-ish link 'tail') and its roller are drawn rigid with link 2. Red = past the drive's stop B. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 94.7751, "el1": 67.1851, "az2": 44.7138, "el2": 43.097, "wd": 54.2545, "wa": -11.0155, "b3": 0.4056, "lE": 63.8584, "lc": 25.501, "phiE": 1.5965, "phib": -74.4542, "stk": 4.8639, "ang_min": 27.7418, "bk1": 35.32, "bk2": 34.48, "sK": -1, "a1max": 50.77, "smhi": 9.29, "smlo": 5.0, "capK": 6.0, "d_mm": 14.97, "psi_c": 8.29};
  const G = {"u": [[0.03228, 0.92176, 0.38641], [-0.47039, 0.64397, 0.60335], [-0.11085, -0.3546, 0.92842]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-1.4097, -21.53524, -8.39347]], "uK": [-0.47628, 0.87734, 0.0585], "sa": [0.04204, -0.93502, -0.3521], "st": [0.99295, 0.0, 0.11855], "sn": [-0.11085, -0.3546, 0.92842], "A": [35.753, 67.421], "branch": -1.0, "m": [-20.13468, 2.31562, 0.0], "f": [49.38, 59.78, 87.77], "fK": 59.5, "capK": 6.0, "tr": 98.03, "tp": 2.182, "RUN": 0.5, "A0": [3.04035, -81.22078, -30.65844], "A0m": [4.49321, -62.3945, -23.29447], "Bm": [-19.61431, -68.78486, -28.61347], "eE": [0.06969, -0.93465, -0.34866], "psiA": -64.8784, "thLo": 36.6687, "thHi": 93.8841, "q2s": [97.0657, -13.0042], "lawTh": [93.884, 94.56, 95.241, 95.927, 96.617, 97.31, 98.006, 98.704, 99.404, 100.104, 100.804, 101.502, 102.199, 102.893, 103.584, 104.27, 104.951, 105.626, 106.295, 106.955, 107.608, 108.251, 108.884, 109.507, 110.119, 110.719, 111.306, 111.881, 112.442, 112.989, 113.522, 114.04, 114.543, 115.03, 115.502, 115.958, 116.398, 116.822, 117.229], "lawDK": [-0.0, -0.855, -1.718, -2.589, -3.465, -4.348, -5.235, -6.127, -7.023, -7.921, -8.821, -9.723, -10.625, -11.526, -12.426, -13.325, -14.22, -15.111, -15.998, -16.88, -17.755, -18.624, -19.486, -20.339, -21.183, -22.018, -22.842, -23.656, -24.459, -25.25, -26.029, -26.796, -27.549, -28.29, -29.017, -29.73, -30.429, -31.114, -31.785], "lawQ2": [-13.004, -13.504, -14.004, -14.504, -15.004, -15.504, -16.004, -16.504, -17.004, -17.504, -18.004, -18.504, -19.004, -19.504, -20.004, -20.504, -21.004, -21.504, -22.004, -22.504, -23.004, -23.504, -24.004, -24.504, -25.004, -25.504, -26.004, -26.504, -27.004, -27.504, -28.004, -28.504, -29.004, -29.504, -30.004, -30.504, -31.004, -31.504, -32.004], "tip": [-0.60986, 0.74879, 0.25958], "tipR": 92.49, "Lt": 22.23, "L1a": [[-6.27177, 48.71078, 12.11687], [-14.52784, 54.69993, 9.00649], [-12.86096, 50.81048, 11.15409], [-9.64843, 46.97925, 13.93718], [-9.01139, 46.92406, 16.60786], [-20.66878, 55.68009, 13.68411]], "L1b": [[-34.32367, 51.75813, 15.17703], [-32.43278, 48.11214, 16.32527], [-30.68739, 44.00622, 19.18067], [-30.79946, 43.39591, 21.12216], [-32.62578, 44.30562, 26.35644], [-32.46396, 52.74097, 15.5779], [-28.84688, 45.35492, 17.56147], [-28.94164, 43.98369, 21.33931], [-29.10881, 43.46657, 23.34037], [-30.60425, 53.72382, 15.97878], [-28.92412, 49.962, 17.08001], [-26.99827, 45.13201, 19.62301], [-27.44063, 44.34819, 23.69997], [-29.07644, 46.18142, 27.12153], [-27.17275, 50.89203, 17.45912], [-25.55711, 47.10234, 18.27407], [-25.16797, 44.9031, 21.65267], [-27.30177, 47.11932, 27.50408]], "L2": [[-32.2442, 33.17283, 43.75719], [-30.37068, 18.42003, 51.98851], [-29.95443, 2.96524, 63.52729], [-26.43156, -16.40771, 70.82232], [-19.22219, -40.79094, 73.18424], [-29.344, 23.26546, 49.95712], [-28.6226, 8.58143, 60.69883], [-25.07445, -11.42407, 69.01836], [-18.5471, -31.46303, 70.08586], [-27.91594, 27.65473, 47.23915], [-27.43289, 13.85434, 58.15933], [-24.85579, -5.05527, 68.44257], [-18.62414, -24.31903, 69.86656], [-26.19013, 31.54048, 44.03811], [-25.93119, 17.24718, 56.23613], [-24.41043, 1.12167, 67.25878], [-18.94415, -17.84908, 70.60725], [-11.95355, -45.46502, 79.14178]], "LT": [[-41.0368, 59.18027, 36.1524], [-43.87419, 62.59269, 35.36007], [-49.64366, 69.40391, 33.02755], [-52.56082, 72.78485, 31.48373], [-54.46993, 74.07783, 25.76617], [-42.94094, 57.62499, 36.45208], [-48.82366, 64.30917, 34.64107], [-54.81286, 70.95135, 31.82696], [-55.90326, 71.76278, 29.04], [-44.80626, 56.01373, 36.71756], [-47.81484, 59.28383, 35.94847], [-53.92677, 65.8104, 33.6617], [-58.1137, 69.85341, 29.3546], [-58.94235, 70.32915, 26.41975], [-49.71738, 57.54535, 36.1917], [-52.84131, 60.73808, 35.18671], [-59.16153, 67.08316, 32.42317], [-61.09499, 68.3551, 26.70908]]};
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
    const state = th > G.thHi ? 1 : -1;
    if (state === -1) { const q2s = G.q2s[0], p = M.mulv(M.rot(u2, q2s), u3); return { q1: K.axisAngle(u1, p, w), dK: 0, q2: q2s, ok: false, L: { state } }; }
    // stretched: invert the tabulated law th(t) -> (q2, dK)
    const T = G.lawTh, n = T.length; let j = 0;
    while (j < n - 2 && T[j + 1] < th) j++;
    const ok = th <= T[n - 1], a = Math.max(0, Math.min(1, (th - T[j]) / Math.max(T[j + 1] - T[j], 1e-9)));
    const q2s = G.lawQ2[j] + a * (G.lawQ2[j + 1] - G.lawQ2[j]), dK = G.lawDK[j] + a * (G.lawDK[j + 1] - G.lawDK[j]);
    const p = M.mulv(M.rot(u2, q2s), u3), q1 = K.axisAngle(u1, M.mulv(M.rot(uK, dK), p), w);
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
    if (!k.ok) return k.L.state === 1 ? 'past the drive stop B (pressure angle / stop B)' : (k.L.state === -1 ? 'folded side: J2 on its dowel (no tooth)' : 'chain cannot close');
    const F = fk(q), sv = M.mulv(M.T(Q), F.t3), kn = knee([V.dot(sv, sa), V.dot(sv, st)]);
    if (!kn.span) return 'knee span: the drift is beyond lE + lc';
    if (kn.ang < P.ang_min || kn.ang > 180 - P.ang_min) return `knee angle ${kn.ang.toFixed(0)} deg outside [${P.ang_min}, ${180 - P.ang_min}]`;
    return null;
  };
  const closes = (q, ctx) => { const r = C.residual(q, ctx); return Math.max(...r.map(Math.abs)) <= 0.5; };
  const solveC = (ctx, qPrev) => { const q = solve(ctx); return (!qPrev || closes(q, ctx)) ? q : K.dls(C, ctx, qPrev, { iters: 40 }).q; };
  const C = {
    id: 'geneva-tail-knuckle-pinknee-3r', name: 'Geneva-tail knuckle on the pin knee: link 2 tail roller slaves K to q2 (3 active, K not read)',
    dof: { active: 3, passive: 3 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'K (passive, slaved to q2 by the tail)', 'J2', 'J3', 'knee pin a', 'knee pin b'], qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve: solveC,
    residual: (q, ctx) => { const F = fk(q); return M.rotErrDeg(F.R5, Qof(ctx)).concat(F.t5); },
    check,
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), F = fk(q);
      const on = (R, p) => W(M.mulv(R, p)), I = M.I3();
      const h1 = { kind: 'hub', role: 'active', name: 'J1 (axis on a GH ray)', c: W(V.scale(u[0], G.f[0])), axis: Wd(u[0]), r: rad, h: hub };
      const hK = { kind: 'hub', role: 'passive', name: 'K (O20, passive, slaved by the tail roller; clock-spring cap, stop A)', c: on(F.R1, V.scale(uK, G.fK)), axis: Wd(M.mulv(F.R1, uK)), r: rad, h: hub + (G.capK || 0) };
      const h2 = { kind: 'hub', role: 'active', name: 'J2 (axis on a GH ray; folded dowel stop, drive stop B)', c: on(F.R1b, V.scale(u[1], G.f[1])), axis: Wd(M.mulv(F.R1b, u[1])), r: rad, h: hub };
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
        { kind: 'arc', role: 'link', name: 'tail (link 2 extension past hub 2, rigid)', pts: G.LT.map(p => on(F.R12, p)), r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'MR63ZZ roller on the tail tip (pushes the flank on link 1a)', c: on(F.R12, V.scale(G.tip, G.tipR)), axis: Wd(M.mulv(F.R12, G.tip)), r: 4, h: 3 },
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
