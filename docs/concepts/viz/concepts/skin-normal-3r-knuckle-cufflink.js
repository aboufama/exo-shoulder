/* skin-normal-3r-knuckle-cufflink - an all-skin-normal 3R closed by THREE passive pins (0 passive translations;
 * verified 31.89 on Bench(110,360) exact frozen, k1187, CMA B1). J1 (O20 hub on the dome) drives a crank strap (lk 21.4)
 * on its rotor whose end carries a KNUCKLE pin parallel to J1 (kat 1: the J1-site knuckle); link 1 hangs from the
 * knuckle to J2 (O20); link 2 to J3 (O20 on the deltoid, axis tilted b3 toward the skin normal); J3's rotor plate
 * carries the E arm (LE 41.1) to pin a; a flat cuff link (lc 23.9) to pin b on the arm pad (cuff / BOTTOM). Pins a, b
 * parallel to J3. J1 / J2 axes are tilted b1 0.011 / b2 -0.084 off the GH rays, so their lines miss GH by ~1 mm and
 * the J3 line by ~7 mm (each faint axis line starts at its line's foot). Closure (the model's closed form,
 * Design.solve): spherical IK of the axis directions; the knuckle angle qk from the RADIAL closure (member 3 must stay
 * c0 above the arm along J3's axis: lk rho cos(Phi - qk) = c0 - s_n + lk rho cos Phi, one assembly root, authority
 * >= 5 mm/rad, swing <= 35 deg); pins a / b from the in-plane two-circle closure (elbow 25-155 deg). Exactly the model
 * docs/concepts/models/skin-normal-3r-knuckle-cufflink.py at rows best_params: axis directions, line points, levels
 * and the fitted link centrelines are exported from its design step + fit on Bench(60,160). The residual is the
 * full-loop forward kinematics from the 6 joint values (arm rotation + GH position implied vs the arm). Red = the J2
 * fold, the knuckle (no root / toggle / swing) or the cuff dyad out of its elbow window. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 92.6852, "el1": 67.3199, "az2": 16.5662, "el2": 52.0128, "wd": 77.5099, "wa": -10.4922, "b1": 0.011, "b2": -0.084, "b3": 0.2393, "lk": 21.4188, "alk": -22.1892, "LE": 41.1128, "lc": 23.8502, "phE": -5.7556, "dB": -57.6675, "crank_strap": 1, "kat": 1};
  const G = {"u":[[0.021801,0.922717,0.38486],[-0.627685,0.722277,0.290392],[-0.150108,-0.110441,0.982482]],"c":[[-0.1581,-0.0016,0.0129],[1.094,0.6563,0.7322],[-1.1998,-7.4178,-1.0171]],"sa":[0.01668,-0.993883,-0.109175],"st":[0.988529,0.0,0.151032],"sn":[-0.150108,-0.110441,0.982482],"A":[40.1345,72.5571],"branch":-1.0,"kj":0,"ku":[0.021801,0.922717,0.38486],"kc":[-0.1581,-0.0016,0.0129],"ke":[-0.999748,0.022153,0.003519],"kf":[-0.005279,-0.38484,0.922968],"alk":-22.1892,"lk":21.4188,"k_c0":0.567,"k_sk":-1.0,"k_mid":0.0,"cuff_m":[-5.668,1.27],"cuff_sig":1.0,"LE":41.1128,"lc":23.8502,"phE":-5.7556,"dB":-57.6675,"gmin":25.0,"auth":5.0,"kswing":35.0,"crank_strap":1,"lv":{"hub1":49.899,"hub2":62.169,"h3":73.186,"Earm":78.301,"crank":49.535,"pad":79.2,"clink":82.35},"eE":[-0.082539,-0.988872,-0.12377],"eB":[-0.876613,-0.444662,-0.183917],"Pb3":[-24.3397,-53.045,-9.6816],"e0":[-19.7849,3.5524,-7.3963],"SING":10.0,"L1":[[-26.71,53.11,15.78],[-30.11,55.02,17.2]],"L2":[[-41.07,44.71,30.02],[-38.64,40.48,31.64],[-36.27,35.71,34.62],[-35.7,33.6,37.43],[-35.62,31.9,40.83],[-34.7,28.57,45.19],[-34.09,26.31,48.2],[-33.46,23.96,51.31],[-31.57,19.71,54.66],[-30.25,16.81,56.85],[-28.88,13.85,59.0],[-26.28,9.12,61.21],[-24.43,5.91,62.41],[-22.43,2.68,63.23],[-19.56,-2.19,64.89],[-17.41,-5.45,65.31]]};
  const u = G.u, c = G.c, sn = G.sn, sa = G.sa, st = G.st, a1 = G.A[0], a2 = G.A[1], lv = G.lv, rad = 10, hub = 12.25;
  const UP = 3.15, TL = 3.0, HEAD = 1.0;
  const wrapR = a => { a = (a + Math.PI) % (2 * Math.PI); return (a < 0 ? a + 2 * Math.PI : a) - Math.PI; };
  const pe = G.phE * D2R, pb = (G.phE + G.dB) * D2R, LE = G.LE, lc = G.lc;
  const Pb2 = [G.cuff_m[0] + LE * Math.cos(pe) + lc * Math.cos(pb), G.cuff_m[1] + LE * Math.sin(pe) + lc * Math.sin(pb)];
  const vref = V.unit(V.cross(u[2], [0.3, 0.5, 0.8]));
  const e0at = th => { const a = G.alk * D2R + th; return V.add(V.scale(G.ke, G.lk * Math.cos(a)), V.scale(G.kf, G.lk * Math.sin(a))); };
  function chain(q1, q2, q3) {                                       // the spherical-direction chain on lines c1, c2, c3
    const R1 = M.rot(u[0], q1), R2 = M.rot(u[1], q2), R12 = M.mul(R1, R2), R3 = M.rot(u[2], q3), R123 = M.mul(R12, R3);
    const t1 = V.sub(c[0], M.mulv(R1, c[0]));
    const t2 = V.add(M.mulv(R1, V.sub(V.sub(c[1], M.mulv(R2, c[1])), c[0])), c[0]);
    const t3 = V.add(M.mulv(R12, V.sub(c[2], M.mulv(R3, c[2]))), t2);
    return { R1, t1, R12, t2, R123, t3 };
  }
  /** Design.solve: q6 [J1 (crank), J2, J3, knuckle, pin a, pin b] (deg) + its closure flags */
  function solveQ(Q) {
    const [u1, u2, u3] = u, w = M.mulv(Q, u3), c12 = V.dot(u1, u2), b1 = V.dot(w, u1), b2 = V.dot(u2, u3), det = 1 - c12 * c12;
    const al = (b1 - c12 * b2) / det, be = (b2 - c12 * b1) / det, cr = V.cross(u1, u2);
    const g2 = (1 - al * al - be * be - 2 * al * be * c12) / V.dot(cr, cr), th0 = V.angle(w, u1);
    const margin = Math.min(th0 - Math.abs(a1 - a2), Math.min(a1 + a2, 360 - a1 - a2) - th0);
    let pick = null;
    for (const sg of [1, -1]) {
      const z = V.madd(V.add(V.scale(u1, al), V.scale(u2, be)), cr, sg * Math.sqrt(Math.max(g2, 0)));
      const q1 = K.axisAngle(u1, z, w), q2 = K.axisAngle(u2, u3, z), br = Math.sign(V.dot(M.mulv(M.rot(u1, q1), u2), V.cross(u1, w)));
      if (pick === null || br === G.branch) pick = [q1, q2];
    }
    const [q1, q2] = pick, R12 = M.mul(M.rot(u1, q1), M.rot(u2, q2));
    const q3 = K.axisAngle(u3, vref, M.mulv(M.T(R12), M.mulv(Q, vref))), X = chain(q1, q2, q3);
    const sv0 = M.mulv(M.T(Q), X.t3), s = [V.dot(sv0, sa), V.dot(sv0, st), V.dot(sv0, sn)];
    // knuckle (radial closure), J1-site (kj 0): J3's axis seen in J1's stator frame
    const wv = M.mulv(Q, sn), ve = V.dot(wv, G.ke), vf = V.dot(wv, G.kf), rho = Math.hypot(ve, vf), chi = Math.atan2(vf, ve);
    const Phi = G.alk * D2R + q1 * D2R - chi, Lr = G.lk * rho;
    const kap = (G.k_c0 - s[2]) / Math.max(Lr, 1e-9) + Math.cos(Phi), th = Math.acos(Math.max(-1, Math.min(1, kap)));
    const qk = wrapR(Phi - G.k_sk * th), auth = Lr * Math.sin(th);
    const okk = Math.abs(kap) <= 1 && auth >= G.auth && Math.abs(wrapR(qk - G.k_mid * D2R)) <= G.kswing * D2R;
    const Delta = V.sub(e0at(q1 * D2R - qk), e0at(q1 * D2R)), dl = M.mulv(M.T(Q), Delta);
    const sv = [s[0] + V.dot(dl, sa), s[1] + V.dot(dl, st), s[2] + V.dot(dl, sn)];
    // cuff dyad in hub 3's plane: circles (J3 line, LE) and (pin b, lc)
    const dx = Pb2[0] - sv[0], dy = Pb2[1] - sv[1], Dn = Math.hypot(dx, dy), ux = dx / Math.max(Dn, 1e-9), uy = dy / Math.max(Dn, 1e-9);
    const a_ = (LE * LE - lc * lc + Dn * Dn) / (2 * Math.max(Dn, 1e-9)), h = Math.sqrt(Math.max(LE * LE - a_ * a_, 0));
    const Ax = sv[0] + a_ * ux - G.cuff_sig * h * uy, Ay = sv[1] + a_ * uy + G.cuff_sig * h * ux;
    const psi = wrapR(Math.atan2(Ay - sv[1], Ax - sv[0]) - pe), beta = wrapR(Math.atan2(Ay - Pb2[1], Ax - Pb2[0]) - (pb + Math.PI));
    const ca = ((sv[0] - Ax) * (Pb2[0] - Ax) + (sv[1] - Ay) * (Pb2[1] - Ay)) / (LE * lc), gam = Math.acos(Math.max(-1, Math.min(1, ca))) / D2R;
    const okc = Dn > Math.abs(LE - lc) && Dn < LE + lc && gam >= G.gmin && gam <= 180 - G.gmin;
    const d = x => K.wrap180(x / D2R);
    const q6 = [K.wrap180(q1 - qk / D2R), q2, K.wrap180(q3 + psi / D2R), d(qk), d(wrapR(beta - psi)), d(beta)];
    return { q6, fold: margin >= G.SING && g2 > 0, margin, okk, kap, auth, qk, okc, gam, Dn };
  }
  const Qof = ctx => M.mul(M.T(ctx.S), ctx.H);
  /** the loop's forward kinematics from the 6 joint values: base -> J1 crank -> knuckle -> link 1 -> J2 -> link 2 -> J3
   *  rotor -> pin a -> cuff link -> pin b -> arm (home coordinates of each member as in the model's T) */
  const pa3 = V.madd(V.madd(c[2], G.eE, LE), sn, lv.clink - G.k_c0);          // pin a, member 3 (rides c0 along sn)
  const pa6 = V.madd(V.madd(G.Pb3, G.eB, -lc), sn, lv.clink), pb6 = V.madd(G.Pb3, sn, lv.clink);
  function fk(q) {
    const Rc = M.rot(u[0], q[0]), kp = V.add(G.kc, M.mulv(Rc, G.e0));            // crank (J1 rotor) and the knuckle point
    const R1 = M.mul(Rc, M.rot(u[0], q[3])), t1 = V.sub(kp, M.mulv(R1, V.add(G.kc, G.e0)));
    const R12 = M.mul(R1, M.rot(u[1], q[1])), t2 = V.add(M.mulv(R1, V.sub(c[1], M.mulv(M.rot(u[1], q[1]), c[1]))), t1);
    const R3 = M.rot(u[2], q[2]), Rm3 = M.mul(R12, R3), t3 = V.add(M.mulv(R12, V.sub(c[2], M.mulv(R3, c[2]))), t2);
    const pa = V.add(M.mulv(Rm3, pa3), t3);
    const R6 = M.mul(Rm3, M.rot(sn, q[4])), t6 = V.sub(pa, M.mulv(R6, pa6)), pbw = V.add(M.mulv(R6, pb6), t6);
    const R5 = M.mul(R6, M.rot(sn, -q[5])), t5 = V.sub(pbw, M.mulv(R5, pb6));
    return { Rc, kp, R1, t1, R12, t2, Rm3, t3, R6, t6, pa, pb: pbw, R5, t5 };
  }
  /** a frame the loop cannot close (fold, no knuckle root, cuff dyad out of span) is shown at the least-squares nearest
   *  configuration warm-started from the previous frame (continuous, drawn red), not at the clipped closed form */
  function solve(ctx, qPrev) {
    const q = solveQ(Qof(ctx)).q6;
    if (!qPrev || closes(q, ctx)) return q;
    const r = K.dls(C, ctx, qPrev, { iters: 40 });
    return r.q;
  }
  const closes = (q, ctx) => { const r = C.residual(q, ctx); return Math.max(...r.slice(0, 3).map(Math.abs)) <= 0.5 && Math.max(...r.slice(3).map(Math.abs)) <= 0.5; };
  const C = {
    id: 'skin-normal-3r-knuckle-cufflink', name: 'Knuckle-cufflink 3R: J1-site knuckle pin + two-pin cuff link (3 passive pins)',
    dof: { active: 3, passive: 3 },
    params: P,
    q0: ctx => solveQ(Qof(ctx)).q6,
    qNames: ['J1 (crank)', 'J2', 'J3', 'knuckle pin', 'pin a', 'pin b'], qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve,
    residual: (q, ctx) => { const F = fk(q); return M.rotErrDeg(F.R5, Qof(ctx)).concat(F.t5); },
    check: (q, ctx) => {
      const s = solveQ(Qof(ctx));
      if (!s.fold) return s.margin < 0 ? 'J2 fold: the J1-J3 axis angle is outside the 3R window' : `J2 within ${s.margin.toFixed(0)} deg of its fold (>= ${G.SING})`;
      if (!s.okk) return Math.abs(s.kap) > 1 ? 'knuckle: no radial-closure root' : (s.auth < G.auth ? 'knuckle near toggle' : 'knuckle swing past its window');
      if (!s.okc) return `cuff dyad elbow ${s.gam.toFixed(0)} deg outside [${G.gmin}, ${180 - G.gmin}] or out of span`;
      return null;
    },
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), F = fk(q), I = M.I3(), Z = [0, 0, 0];
      const on = (R, t, p) => W(V.add(M.mulv(R, p), t));
      const tC = V.sub(G.kc, M.mulv(F.Rc, G.kc));
      const h1 = { kind: 'hub', role: 'active', name: 'J1 (dome, axis ~GH ray)', c: W(V.madd(c[0], u[0], lv.hub1)), axis: Wd(u[0]), r: rad, h: hub, p0: W(c[0]) };
      const h2 = { kind: 'hub', role: 'active', name: 'J2 (axis ~GH ray)', c: on(F.R1, F.t1, V.madd(c[1], u[1], lv.hub2)), axis: Wd(M.mulv(F.R1, u[1])), r: rad, h: hub, p0: on(F.R1, F.t1, c[1]) };
      const h3 = { kind: 'hub', role: 'active', name: 'J3 (skin-normal tilt, line misses GH)', c: on(F.Rm3, F.t3, V.madd(c[2], sn, lv.h3)), axis: Wd(M.mulv(F.R12, u[2])), r: rad, h: hub, p0: on(F.Rm3, F.t3, c[2]) };
      const ku = Wd(M.mulv(F.Rc, u[0])), kb = V.add(G.kc, G.e0), n3 = Wd(M.mulv(F.Rm3, sn));
      const arm = p => M.mulv(ctx.H, p);
      const lvl = (p, h) => V.madd(W(p), n3, h);
      const padC = arm(V.madd(G.Pb3, sn, lv.pad + 1.5)), padN = M.mulv(ctx.H, sn);
      const zl3 = lv.clink - G.k_c0, paLo = Math.min(lv.Earm, zl3), paH = Math.abs(lv.Earm - zl3) + TL + HEAD;
      const paFoot = V.add(M.mulv(F.Rm3, V.madd(c[2], G.eE, LE)), F.t3);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base on the scapula handler', c: V.madd(h1.c, h1.axis, -3), z: h1.axis, x: ctx.attach.scapDir([1, 0, 0]), size: [40, 30], t: 3 },
        h1,
        { kind: 'link', role: 'link', name: 'crank strap on J1\'s rotor', a: on(F.Rc, tC, V.madd(V.madd(G.kc, V.unit(G.e0), rad), u[0], lv.hub1 + UP + 1.5)),
          b: on(F.Rc, tC, V.madd(kb, u[0], lv.crank + 1.5)), r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'knuckle pin (parallel to J1)', c: on(F.Rc, tC, V.madd(kb, u[0], lv.crank)), axis: ku, r: 6, h: 2 * TL + 0.15 + HEAD,
          p0: on(F.Rc, tC, kb) },
        { kind: 'arc', role: 'link', name: 'link 1 (knuckle -> J2, 8 x 3 strap, fitted)', pts: G.L1.map(p => on(F.R1, F.t1, p)), r: 2.5 },
        h2,
        { kind: 'arc', role: 'link', name: 'link 2 (8 x 3 strap, fitted)', pts: G.L2.map(p => on(F.R12, F.t2, p)), r: 2.5 },
        h3,
        { kind: 'link', role: 'link', name: 'E arm (J3 rotor plate)', a: on(F.Rm3, F.t3, V.madd(V.madd(c[2], G.eE, rad), sn, lv.Earm + 1.5)),
          b: on(F.Rm3, F.t3, V.madd(V.madd(c[2], G.eE, LE), sn, lv.Earm + 1.5)), r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'pin a (parallel to J3)', c: lvl(paFoot, paLo), axis: n3, r: 6, h: paH, p0: lvl(paFoot, paLo) },
        { kind: 'link', role: 'link', name: 'cuff link (flat, pin a -> pin b)', a: lvl(paFoot, zl3 + 1.5), b: V.madd(arm(V.madd(G.Pb3, sn, lv.clink + 1.5)), n3, 0), r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'pin b (parallel to J3, on the pad)', c: arm(V.madd(G.Pb3, sn, lv.pad)), axis: padN, r: 6, h: lv.clink - lv.pad + TL + HEAD,
          p0: arm(V.madd(G.Pb3, sn, lv.pad)) },
        { kind: 'plate', role: 'fixed-arm', name: 'arm pad 16 x 16 (on the cuff / BOTTOM)', c: padC, z: padN, x: arm(sa), size: [16, 16], t: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'BOTTOM bar to the cuff (schematic)', a: V.madd(padC, padN, -2), b: arm([G.Pb3[0], -150, 50]), r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: V.scale(ctx.armAxis, 155), axis: ctx.armAxis, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: Z, r: 4 }
      ];
    }
  };
  K.register(C);
})();
