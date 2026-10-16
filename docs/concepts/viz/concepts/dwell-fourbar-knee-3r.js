/* dwell-fourbar-knee-3r - best screened config (CMA stream D: 26.86 on Bench(60,160) fast, score 90.2; window [35.9, 102.5] deg vs the plain chain's [46.2, 102.4] at these seats).
 * A spherical Watt six-bar, every axis through GH, pins only: J1 (O20, scapula seat az/el) -> link 1 (+ a plate to
 * pin P) -> J2 (O15 slim) -> L2a -> knee K (PASSIVE pin) -> L2b (strap K -> J3 + a tail K -> Q) -> J3 (O15, humerus seat
 * wd/wa) -> the neck to BOTTOM's bar; loop link 1 -> P -> rocker C -> Q -> L2b. Mobility 3: the knee angle is a fixed
 * function of the crank q2 (no spring, no sensed passive); P, K, Q are MR63ZZ pairs. Per frame (model solve): th =
 * angle(J1, J3) -> crank s on the loop's monotone valid arc (secant-refined), clipped to the arc's ends (outside the
 * window the chain is drawn parked at its end, red); the rotation taking (u1, u3(s)) to (J1, J3) places every axis.
 * Levels: the kit's fitted profiles on Bench(60,160) (pin posts raised where a strap lands on them, adjust_stacks). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az": 97.7506, "el": 65.294, "a1": 38.0901, "a2": 74.2679, "wd": 90.0506, "wa": -9.2038, "b": 40.787, "chi": 6.5374, "gP": 22.4391, "phP": 28.4902, "k": 18.7416, "alq": -141.0145, "sref": 196.2443, "margin": 10.0, "tq_lo": 30.0, "tk_lo": 20.0, "rad1": 10.0, "rad2": 7.5, "rad3": 7.5, "rpin": 5.0, "width": 12.0};
  const G = {"u1": [0.6169, 0.0, 0.787042], "u2": [0.0, 0.0, 1.0], "K0": [0.649001, 0.074374, 0.757143], "Q0": [0.417491, -0.102264, 0.902908], "P": [0.335477, 0.182075, 0.924286], "r": 46.599475466937136, "sgn": -1.0, "c3": [0.829981, -0.433574, 0.35092], "lo": 35.90758011911379, "hi": 102.52821527867157, "s0": 176.75, "s1": 329.75, "su": [176.75, 177.75, 178.75, 179.75, 180.75, 181.75, 182.75, 183.75, 184.75, 185.75, 186.75, 187.75, 188.75, 189.75, 190.75, 191.75, 192.75, 193.75, 194.75, 195.75, 196.75, 197.75, 198.75, 199.75, 200.75, 201.75, 202.75, 203.75, 204.75, 205.75, 206.75, 207.75, 208.75, 209.75, 210.75, 211.75, 212.75, 213.75, 214.75, 215.75, 216.75, 217.75, 218.75, 219.75, 220.75, 221.75, 222.75, 223.75, 224.75, 225.75, 226.75, 227.75, 228.75, 229.75, 230.75, 231.75, 232.75, 233.75, 234.75, 235.75, 236.75, 237.75, 238.75, 239.75, 240.75, 241.75, 242.75, 243.75, 244.75, 245.75, 246.75, 247.75, 248.75, 249.75, 250.75, 251.75, 252.75, 253.75, 254.75, 255.75, 256.75, 257.75, 258.75, 259.75, 260.75, 261.75, 262.75, 263.75, 264.75, 265.75, 266.75, 267.75, 268.75, 269.75, 270.75, 271.75, 272.75, 273.75, 274.75, 275.75, 276.75, 277.75, 278.75, 279.75, 280.75, 281.75, 282.75, 283.75, 284.75, 285.75, 286.75, 287.75, 288.75, 289.75, 290.75, 291.75, 292.75, 293.75, 294.75, 295.75, 296.75, 297.75, 298.75, 299.75, 300.75, 301.75, 302.75, 303.75, 304.75, 305.75, 306.75, 307.75, 308.75, 309.75, 310.75, 311.75, 312.75, 313.75, 314.75, 315.75, 316.75, 317.75, 318.75, 319.75, 320.75, 321.75, 322.75, 323.75, 324.75, 325.75, 326.75, 327.75, 328.75, 329.75], "tp": [112.5282, 112.5227, 112.5082, 112.4847, 112.4524, 112.4114, 112.3617, 112.3035, 112.2369, 112.162, 112.0788, 111.9875, 111.8882, 111.7809, 111.6658, 111.543, 111.4125, 111.2743, 111.1286, 110.9754, 110.8146, 110.6464, 110.4706, 110.2873, 110.0964, 109.8979, 109.6916, 109.4775, 109.2555, 109.0253, 108.787, 108.5403, 108.2852, 108.0213, 107.7486, 107.4669, 107.1761, 106.876, 106.5664, 106.2472, 105.9182, 105.5795, 105.2307, 104.8719, 104.5029, 104.1236, 103.7341, 103.3343, 102.924, 102.5034, 102.0723, 101.6309, 101.179, 100.7168, 100.2443, 99.7615, 99.2684, 98.7652, 98.2519, 97.7285, 97.1952, 96.6521, 96.0992, 95.5367, 94.9646, 94.3831, 93.7923, 93.1923, 92.5832, 91.9651, 91.3381, 90.7025, 90.0582, 89.4055, 88.7444, 88.0751, 87.3977, 86.7124, 86.0192, 85.3183, 84.6099, 83.8939, 83.1707, 82.4402, 81.7027, 80.9582, 80.2069, 79.4488, 78.6842, 77.9132, 77.1358, 76.3521, 75.5624, 74.7667, 73.9652, 73.1579, 72.3451, 71.5267, 70.703, 69.8741, 69.04, 68.201, 67.3572, 66.5086, 65.6555, 64.7979, 63.9361, 63.0702, 62.2002, 61.3265, 60.4491, 59.5683, 58.6842, 57.797, 56.9069, 56.0141, 55.119, 54.2216, 53.3223, 52.4214, 51.5192, 50.6159, 49.712, 48.8079, 47.9038, 47.0003, 46.0979, 45.197, 44.2983, 43.4024, 42.5099, 41.6216, 40.7382, 39.8608, 38.9902, 38.1275, 37.2739, 36.4306, 35.599, 34.7806, 33.9771, 33.1903, 32.422, 31.6745, 30.9499, 30.2507, 29.5795, 28.9391, 28.3322, 27.7619, 27.2313, 26.7433, 26.3011, 25.9076], "lv": {"hub1": {"F": 51.0, "t": 12.25}, "hub2": {"F": 58.36, "t": 12.891}, "hub3": {"F": 68.0, "t": 16.25}, "pinP": {"F": 53.0, "t": 16.137}, "pinK": {"F": 62.0, "t": 11.35}, "pinQ": {"F": 63.36, "t": 9.991}, "link1": {"r0": 54.15, "r1": 58.54, "mid": 51.82, "kind": "free"}, "link1p": {"r0": 58.36, "r1": 53.0, "mid": 54.99, "kind": "free"}, "neck": {"r0": 68.0, "r1": 94.01, "mid": 77.67, "kind": "free"}, "L2a": {"r0": 61.51, "r1": 62.0, "mid": 58.21, "kind": "free"}, "rocker": {"r0": 56.15, "r1": 63.49, "mid": 72.72, "kind": "free"}, "L2bJ": {"r0": 65.15, "r1": 71.15, "mid": 64.91, "kind": "free"}, "L2bQ": {"r0": 65.15, "r1": 66.51, "mid": 66.51, "kind": "free"}}};
  const lv = G.lv, BAR0 = [0, -0.56984, 0.82175], z = [0, 0, 1], W = K.wrap180;
  const tang = (a, b) => V.unit(V.reject(b, a));
  const frame = (a, b) => { const e = tang(a, b); return M.fromCols(a, e, V.cross(a, e)); };
  /** the loop at crank s (deg), link 1's frame: knee K, pin Q, J3 axis u3, J1-J3 angle th, validity */
  function loopAt(s) {
    const Ks = M.mulv(M.rot(z, s), G.K0), cq = K.circInt(G.P, G.r, Ks, P.k, G.sgn), Q = cq.p;
    const u3 = M.mulv(frame(Ks, Q), G.c3), th = V.angle(u3, G.u1);
    const tq = V.angle(tang(Q, Ks), tang(Q, G.P)), tk = V.angle(tang(Ks, G.u2), tang(Ks, Q));
    const ok = cq.ok && tq >= P.tq_lo && tq <= 180 - P.tq_lo && tk >= P.tk_lo && tk <= 180 - P.tk_lo;
    return { s, K: Ks, Q, u3, th, ok };
  }
  const order = G.tp.map((t, i) => i).sort((a, b) => G.tp[a] - G.tp[b]), TH = order.map(i => G.tp[i]), SS = order.map(i => G.su[i]);
  const interp = (x, X, Y) => { if (x <= X[0]) return Y[0]; if (x >= X[X.length - 1]) return Y[Y.length - 1];
    let lo = 0, hi = X.length - 1; while (hi - lo > 1) { const m = (lo + hi) >> 1; if (X[m] <= x) lo = m; else hi = m; }
    return Y[lo] + (Y[hi] - Y[lo]) * (x - X[lo]) / ((X[hi] - X[lo]) || 1e-9); };
  function crank(th) {                                                // model solve(): interp + 3 secant / Newton steps
    let s = interp(th, TH, SS);
    for (let i = 0; i < 3; i++) {
      const a = loopAt(s), b = loopAt(s + 0.05), g = (b.th - a.th) / 0.05;
      s = Math.min(G.s1, Math.max(G.s0, s - (a.th - th) / (Math.abs(g) < 1e-6 ? 1e-6 : g)));
    }
    return s;
  }
  const axes = ctx => ({ p1: M.mulv(ctx.S, K.bvec(P.az, P.el)), p3: M.mulv(ctx.H, K.wdir(P.wd, P.wa)) });
  function place(R, L) { const f = v => M.mulv(R, v); return { p2: f(G.u2), Kw: f(L.K), Qw: f(L.Q), Pw: f(G.P), u3w: f(L.u3) }; }
  function solve(ctx) {
    const { p1, p3 } = axes(ctx), th = V.angle(p1, p3), L = loopAt(crank(th));
    const R = M.mul(frame(p1, p3), M.T(frame(G.u1, L.u3))), X = place(R, L);
    return [K.axisAngle(p1, ctx.attach.scapDir([1, 0, 0]), X.p2), L.s, K.axisAngle(X.Kw, X.p2, p3), K.axisAngle(p3, ctx.armAxis, X.Kw),
            K.axisAngle(X.Pw, X.p2, X.Qw), K.axisAngle(X.Qw, X.Pw, X.Kw)];
  }
  /** forward kinematics from J1 (azimuth of J2 about J1) and the crank: link 1's frame, then the loop */
  function fk(q, ctx) {
    const { p1, p3 } = axes(ctx), e = V.unit(V.reject(ctx.attach.scapDir([1, 0, 0]), p1)), f = V.cross(p1, e), a = P.a1 * D2R, j = q[0] * D2R;
    const p2 = V.add(V.scale(p1, Math.cos(a)), V.scale(V.add(V.scale(e, Math.cos(j)), V.scale(f, Math.sin(j))), Math.sin(a)));
    const R1 = M.mul(frame(p1, p2), M.T(frame(G.u1, G.u2))), L = loopAt(q[1]);
    return Object.assign(place(R1, L), { p1, p3, L });
  }
  K.register({
    id: 'dwell-fourbar-knee-3r', name: 'Dwell four-bar knee 3R: spherical Watt six-bar, rocker from link 1 to a split link 2 (in screening)',
    dof: { active: 3, passive: 3 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'J2 (crank)', 'knee K', 'J3', 'pin P (rocker)', 'pin Q'], qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
    solve,
    residual: (q, ctx) => {
      const X = fk(q, ctx), cr = V.cross(X.u3w, X.p3), n = V.norm(cr), an = V.angle(X.u3w, X.p3);
      const rv = n > 1e-12 ? V.scale(cr, an / n) : [0, 0, 0];
      return rv.concat([W(K.axisAngle(X.p3, ctx.armAxis, X.Kw) - q[3]), W(K.axisAngle(X.Kw, X.p2, X.u3w) - q[2]),
                        W(K.axisAngle(X.Pw, X.p2, X.Qw) - q[4]), W(K.axisAngle(X.Qw, X.Pw, X.Kw) - q[5]),
                        V.angle(X.Pw, X.Qw) - G.r, V.angle(X.Kw, X.Qw) - P.k]);
    },
    check: (q, ctx) => {
      const { p1, p3 } = axes(ctx), th = V.angle(p1, p3), L = loopAt(q[1]);
      if (th < G.lo || th > G.hi) return `J1-J3 angle ${th.toFixed(0)} deg outside the loop window [${G.lo.toFixed(0)}, ${G.hi.toFixed(0)}]`;
      if (!L.ok) return 'loop transmission angle out of range';
      return null;
    },
    parts: (q, ctx) => {
      const X = fk(q, ctx), h = 1.5, arc = (name, role, a, b, m, r) => ({ kind: 'arc', role, name, u: a, v: b, r0: lv[m].r0 + h, r1: lv[m].r1 + h, r: r || 2.5 });
      const hubD = (name, role, ax, m, r) => ({ kind: 'hub', role, name, c: V.scale(ax, lv[m].F), axis: ax, r, h: lv[m].t });
      const h1 = hubD('J1 (axis through GH)', 'active', X.p1, 'hub1', P.rad1);
      const neckEnd = M.mulv(ctx.Hb, BAR0);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base on the scapula handler', c: V.madd(h1.c, X.p1, -3), z: X.p1, x: ctx.attach.scapDir([1, 0, 0]), size: [40, 30], t: 3 },
        h1,
        arc('link 1 (12 x 3 Ti)', 'link', X.p1, X.p2, 'link1'),
        arc('link 1 plate to pin P', 'link', X.p2, X.Pw, 'link1p'),
        hubD('J2 (O15 slim, through GH)', 'active', X.p2, 'hub2', P.rad2),
        hubD('pin P (MR63ZZ pair; post raised under the rocker)', 'passive', X.Pw, 'pinP', P.rpin),
        arc('L2a (J2 -> knee)', 'link', X.p2, X.Kw, 'L2a'),
        hubD('knee K (passive pin)', 'passive', X.Kw, 'pinK', P.rpin),
        arc('rocker C (P -> Q)', 'link', X.Pw, X.Qw, 'rocker', 2),
        hubD('pin Q (passive)', 'passive', X.Qw, 'pinQ', P.rpin),
        arc('L2b strap (knee -> J3)', 'link', X.Kw, X.u3w, 'L2bJ'),
        arc('L2b tail (knee -> Q)', 'link', X.Kw, X.Qw, 'L2bQ'),
        hubD('J3 (O15 slim, through GH)', 'active', X.u3w, 'hub3', P.rad3),
        arc('neck to BOTTOM\'s bar (14 x 6)', 'fixed-arm', X.p3, neckEnd, 'neck', 3),
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: V.scale(ctx.armAxis, 155), axis: ctx.armAxis, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
