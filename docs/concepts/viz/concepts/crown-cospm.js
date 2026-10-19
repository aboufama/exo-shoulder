/* crown-cospm - coaxial spherical parallel manipulator driven from a nested ring stack on the crown (catalogue
 * crown-cospm, ideated: no bench model or sweep). Three thin-section rings nested on the crown, all coaxial with a0
 * (S-local, c* = (-0.38, 0.91, 0.16)), are the 3 ACTIVE joints; each rotor carries a proximal arc (ap) -> passive
 * micro-hub w_i -> distal arc (ad) -> passive micro-hub on the arm platform, axes v_i humerus-fixed through GH, 120 deg
 * apart on a cone gamma about v0 (a C-saddle on the lateral upper arm). 3 legs x RRR = 9 joints, mobility 3: 3 ACTIVE
 * ring angles + 6 PASSIVE, every passive set by closure (w_i = the two-cone intersection {angle(a0, w) = ap} x
 * {angle(w, v_i) = ad}, branch s_i). Parameters: no model exists, so this preview uses a loop-only kinematic screen
 * inside the spec's sweep ranges (ap, ad 60-100; gamma 30-70; platform axis v0; branches), keeping the catalogue's
 * fan (at rest one leg over the front of the deltoid, one over the back): ap 80, ad 70, gamma 30, v0 = wdir(80, -20),
 * phase 90, branches (-1, -1, +1); 207 / 240 loop frames close past both singularity margins (a direction test also
 * flags frames where an elbow swings medial over the neck or down over the chest: none here). Kept out (spec): leg serial
 * singular |a0 . (w_i x v_i)| < 0.15, parallel singular |det[w_i x v_i]| < 0.05. Ring pitch radii 28.6 / 34.9 / 41.3
 * mm (RBC KA020 / 025 / 030) at 52 mm up a0; micro-hubs O12 (r 6, 7 mm stack); radii schematic. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D = K.D2R;
  const P = { a0: V.unit([-0.38, 0.91, 0.16]), ap: 80, ad: 70, gamma: 30, v0: [80, -20], phase: 90, s: [-1, -1, 1],
              crown: 52, pitch: [28.6, 34.9, 41.3], elbowR: 70, skinR: 56, minR: 62, serial: 0.15, par: 0.05, cuff_at: 165 };
  const vc = K.wdir(P.v0[0], P.v0[1]), vref = V.perp(vc);
  const v0s = [0, 1, 2].map(i => K.onCone(vc, vref, P.gamma, P.phase + 120 * i));            // platform axes (humerus frame)
  const platR = v0s.map(v => Math.max(P.minR, P.skinR / Math.sin(Math.acos(-v[1]))));          // hub radius: ~56 mm off the arm axis
  const aref = V.perp(P.a0);                                                                   // ring angle zero (scapula frame)
  function frame(ctx) {
    const A = M.mulv(ctx.S, P.a0), ref = M.mulv(ctx.S, aref), Vv = v0s.map(v => M.mulv(ctx.H, v));
    const legs = Vv.map((v, i) => { const c = K.circInt(A, P.ap, v, P.ad, P.s[i]); return { v, w: c.p, ok: c.ok }; });
    return { A, ref, legs };
  }
  const solve = ctx => { const f = frame(ctx); return f.legs.map(l => K.axisAngle(f.A, f.ref, l.w)); };

  K.register({
    id: 'crown-cospm',
    name: 'Crown coaxial SPM (nested ring stack)',
    dof: { active: 3, passive: 6 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['ring 1 (inner)', 'ring 2', 'ring 3 (outer)'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => solve(ctx),
    residual: (q, ctx) => {                                       // each leg's loop: elbow on its ring cone, ad from v_i
      const f = frame(ctx);
      return f.legs.map((l, i) => V.angle(K.onCone(f.A, f.ref, P.ap, q[i]), l.v) - P.ad);
    },
    check: (q, ctx) => {
      const f = frame(ctx), n = [];
      for (let i = 0; i < 3; i++) {
        const l = f.legs[i]; if (!l.ok) return `leg ${i + 1} cannot reach the platform`;
        const x = V.cross(l.w, l.v); if (Math.abs(V.dot(f.A, x)) < P.serial) return `leg ${i + 1} near its serial singularity`;
        n.push(x);
        const ws = M.mulv(M.T(ctx.S), l.w); if (ws[2] < -0.25 || ws[1] < -0.5) return `elbow ${i + 1} swings over the neck / chest side`;
      }
      return Math.abs(V.dot(n[0], V.cross(n[1], n[2]))) < P.par ? 'parallel singularity: the platform goes loose' : null;
    },
    parts: (q, ctx) => {
      const f = frame(ctx), A = f.A, out = [], h = P.crown;
      out.push({ kind: 'ring', role: 'fixed-scapula', name: 'ring stack stator', c: V.scale(A, h - 4), axis: A, ref: f.ref, r: P.pitch[2] + 4, t: 2.5 },
        { kind: 'plate', role: 'fixed-scapula', name: 'crown base', c: V.scale(A, h - 7), z: A, x: f.ref, size: [30, 30], t: 3 });
      for (let i = 0; i < 3; i++) {
        const w = K.onCone(A, f.ref, P.ap, q[i]), v = f.legs[i].v, rr = P.pitch[i];
        const root = V.scale(K.onCone(A, f.ref, Math.atan2(rr, h) * K.R2D, q[i]), Math.hypot(rr, h));
        out.push({ kind: 'ring', role: 'active', name: `ring rotor ${i + 1}`, c: V.scale(A, h), axis: A, ref: f.ref, r: rr, t: 2.2 },
          { kind: 'arc', role: 'link', name: `proximal arc ${i + 1}`, pts: K.greatArc(V.unit(root), w, V.norm(root), P.elbowR), r: 2.2 },
          { kind: 'hub', role: 'passive', name: `elbow micro-hub ${i + 1}`, c: V.scale(w, P.elbowR), axis: w, r: 6, h: 7 },
          { kind: 'arc', role: 'link', name: `distal arc ${i + 1}`, u: w, v, r0: P.elbowR + 3.5, r1: platR[i] + 3.5, r: 2.2 },
          { kind: 'hub', role: 'passive', name: `platform micro-hub ${i + 1}`, c: V.scale(v, platR[i] - 3.5), axis: v, r: 6, h: 7 });
      }
      const Vv = f.legs.map(l => l.v), pr = platR.map(r => r - 4);
      out.push({ kind: 'arc', role: 'fixed-arm', name: 'arm platform (C-saddle)', pts: K.greatArc(Vv[0], Vv[1], pr[0], pr[1]).concat(K.greatArc(Vv[1], Vv[2], pr[1], pr[2]), K.greatArc(Vv[2], Vv[0], pr[2], pr[0])), r: 3.5 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: V.scale(ctx.armAxis, P.cuff_at), axis: ctx.armAxis, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 });
      return out;
    }
  });
})();
