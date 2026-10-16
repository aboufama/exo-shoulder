/* dwell-fourbar-knee-3r - BEING MODELLED RIGHT NOW by a screening agent: drawn from the CURRENT model file
 * docs/concepts/models/dwell-fourbar-knee-3r.py (uncommitted edits as of 2026-10-16 05:30 UTC) at the best UNLOCKED config of
 * docs/concepts/sweeps/dwell-fourbar-knee-3r.json (k58: 41.88 on Bench(60,160) fast, re-run here with the current file:
 * 41.88; no row / verdict yet; the sweep's 31.40 is the LOCKED control, the plain spherical 3R with the knee rigid).
 * A spherical Watt six-bar, every axis through GH, pins only: J1 (O20, scapula seat az/el) -> link 1 (+ a plate to
 * pin P) -> J2 (O15 slim) -> L2a -> knee K (PASSIVE pin) -> L2b (strap K -> J3 + a tail K -> Q) -> J3 (O15, humerus seat
 * wd/wa) -> the neck to BOTTOM's bar; loop link 1 -> P -> rocker C (arc 41.1 deg) -> Q -> L2b. Mobility 3: the knee
 * angle is a fixed function of the crank q2 (no spring, no sensed passive); passive P, K, Q are MR63ZZ pairs. Per
 * frame (model solve): th = angle(J1, J3) -> crank s on the loop's monotone valid arc (secant-refined), clipped to the
 * arc's ends (a pose outside the window [33.0, 104.7] deg shows the chain parked at its end, red); the rotation taking
 * (u1, u3(s)) to (J1, J3) places every axis. Hub / pin face levels and strap end radii are the kit's fitted profiles on
 * Bench(60,160) (pin posts raised where a strap lands on them, as adjust_stacks). The residual: the J3 axis the loop
 * implies vs the arm's (rotation vector), the J3 / knee / pin angles vs the q given, the four-bar arcs. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az": 101.6207, "el": 65.2638, "a1": 41.7763, "a2": 74.6316, "wd": 86.0976, "wa": -12.1676, "b": 38.9124, "chi": -8.0552, "gP": 15.0, "phP": 25.114, "k": 17.3744, "alq": -149.994, "sref": 199.9776, "margin": 10.0, "tq_lo": 30.0, "tk_lo": 20.0, "rad1": 10.0, "rad2": 7.5, "rad3": 7.5, "rpin": 5.0, "width": 12.0};
  const G = {"u1":[0.666224,0.0,0.745752],"u2":[0.0,0.0,1.0],"K0":[0.621934,-0.088018,0.778107],"Q0":[0.397202,-0.26266,0.879341],"P":[0.234352,0.109848,0.965926],"r":41.142709725922536,"sgn":-1.0,"c3":[0.805912,-0.512687,0.296071],"lo":32.9748542833079,"hi":104.72399884131721,"s0":187.25,"s1":342.25,"su":[187.25,188.25,189.25,190.25,191.25,192.25,193.25,194.25,195.25,196.25,197.25,198.25,199.25,200.25,201.25,202.25,203.25,204.25,205.25,206.25,207.25,208.25,209.25,210.25,211.25,212.25,213.25,214.25,215.25,216.25,217.25,218.25,219.25,220.25,221.25,222.25,223.25,224.25,225.25,226.25,227.25,228.25,229.25,230.25,231.25,232.25,233.25,234.25,235.25,236.25,237.25,238.25,239.25,240.25,241.25,242.25,243.25,244.25,245.25,246.25,247.25,248.25,249.25,250.25,251.25,252.25,253.25,254.25,255.25,256.25,257.25,258.25,259.25,260.25,261.25,262.25,263.25,264.25,265.25,266.25,267.25,268.25,269.25,270.25,271.25,272.25,273.25,274.25,275.25,276.25,277.25,278.25,279.25,280.25,281.25,282.25,283.25,284.25,285.25,286.25,287.25,288.25,289.25,290.25,291.25,292.25,293.25,294.25,295.25,296.25,297.25,298.25,299.25,300.25,301.25,302.25,303.25,304.25,305.25,306.25,307.25,308.25,309.25,310.25,311.25,312.25,313.25,314.25,315.25,316.25,317.25,318.25,319.25,320.25,321.25,322.25,323.25,324.25,325.25,326.25,327.25,328.25,329.25,330.25,331.25,332.25,333.25,334.25,335.25,336.25,337.25,338.25,339.25,340.25,341.25,342.25],"tp":[114.724,114.7204,114.7073,114.6848,114.6528,114.6112,114.56,114.499,114.4284,114.3479,114.2575,114.1572,114.0468,113.9265,113.796,113.6553,113.5044,113.3432,113.1715,112.9895,112.797,112.5939,112.3803,112.1559,111.9209,111.675,111.4184,111.1509,110.8725,110.5832,110.2829,109.9715,109.6492,109.3158,108.9713,108.6158,108.2491,107.8714,107.4826,107.0827,106.6718,106.2499,105.8169,105.3731,104.9183,104.4526,103.9761,103.4889,102.991,102.4824,101.9633,101.4338,100.8938,100.3436,99.7832,99.2127,98.6322,98.0418,97.4417,96.8318,96.2124,95.5836,94.9454,94.2981,93.6416,92.9762,92.302,91.6191,90.9276,90.2276,89.5194,88.8029,88.0784,87.3459,86.6057,85.8578,85.1023,84.3395,83.5693,82.7921,82.0078,81.2166,80.4186,79.6141,78.803,77.9856,77.1619,76.3322,75.4965,74.6549,73.8076,72.9548,72.0965,71.2329,70.3642,69.4904,68.6118,67.7285,66.8405,65.9482,65.0515,64.1508,63.2461,62.3376,61.4256,60.5101,59.5915,58.6698,57.7453,56.8182,55.8888,54.9573,54.0239,53.089,52.1528,51.2157,50.278,49.34,48.4021,47.4648,46.5284,45.5935,44.6607,43.7303,42.8031,41.8797,40.9609,40.0473,39.1399,38.2396,37.3473,36.4642,35.5914,34.7302,33.8821,33.0486,32.2314,31.4321,30.6529,29.8959,29.1632,28.4574,27.7809,27.1367,26.5275,25.9562,25.4261,24.9401,24.5014,24.1129,23.7775,23.4978,23.276,23.1141,23.0134,22.9749],"lv":{"hub1":{"F":51.0,"t":12.25},"hub2":{"F":61.0,"t":13.099999999939001},"hub3":{"F":70.0,"t":16.25},"pinP":{"F":55.5,"t":23.393097444669486},"pinK":{"F":63.5,"t":13.00200000000001},"pinQ":{"F":70.0,"t":8.495999999999981},"link1":{"r0":54.15,"r1":61.0,"mid":52.0,"kind":"free"},"link1p":{"r0":61.0,"r1":55.5,"mid":61.0,"kind":"free"},"neck":{"r0":70.0,"r1":100.0,"mid":82.0,"kind":"free"},"L2a":{"r0":64.15,"r1":64.0,"mid":61.0,"kind":"free"},"rocker":{"r0":65.15,"r1":72.0,"mid":75.55,"kind":"free"},"L2bJ":{"r0":66.65,"r1":73.15,"mid":66.0,"kind":"free"},"L2bQ":{"r0":66.65,"r1":73.5,"mid":73.15,"kind":"free"}}};
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
