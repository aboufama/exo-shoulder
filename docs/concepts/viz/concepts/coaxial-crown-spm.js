/* coaxial-crown-spm - coaxial-input 3-RRR spherical parallel manipulator on the dome (catalogue coaxial-crown-spm,
 * ideated; marked a duplicate of spm-coaxial-turret; same machine class as crown-cospm). S -> crown: three concentric
 * thin-section ring bearings stacked on ONE axis u0 through GH at the dome pole p* = (-0.377, 0.914, 0.152) (the humerus
 * never comes within 82 deg of it), pitch radii 18 / 24 / 30 mm at ~52 mm up u0 (dome skin + 3): the 3 ACTIVE inputs,
 * rotation about u0 unlimited -> proximal arc i (a1) -> PASSIVE R hub at v_i (O16-20, drawn O17) -> distal arc i (a2) ->
 * PASSIVE R hub on the arm platform at w_i (three arm-fixed axes through GH, 120 deg apart about a platform axis j_p at
 * cone angle beta) -> arm platform on the user's cuff. 3 active + 6 passive, every passive set by closure (two-cone
 * intersection per leg). No bench model or sweep exists: the leg geometry is crown-cospm's loop-screened set, inside
 * this spec's ranges (a1 80, a2 70 within 55-100; beta 30 within 30-80; j_p = wdir(80, -20), phase 90, branches -1 / -1 /
 * +1). Kept out: leg serial singular |u0 . (v_i x w_i)| < 0.15, parallel singular |det[v_i x w_i]| < 0.05, an elbow
 * swinging medial over the neck or down over the chest. Radii schematic. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D = K.D2R;
  const P = { a0: V.unit([-0.377, 0.914, 0.152]), ap: 80, ad: 70, gamma: 30, v0: [80, -20], phase: 90, s: [-1, -1, 1],
              crown: 52, pitch: [18, 24, 30], elbowR: 72, skinR: 56, minR: 62, serial: 0.15, par: 0.05, cuff_at: 165 };
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
    id: 'coaxial-crown-spm',
    name: 'Coaxial-input SPM on the dome (crown ring stack, O17 passive hubs)',
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
          { kind: 'hub', role: 'passive', name: `elbow hub ${i + 1} (passive, O17)`, c: V.scale(w, P.elbowR), axis: w, r: 8.5, h: 10 },
          { kind: 'arc', role: 'link', name: `distal arc ${i + 1}`, u: w, v, r0: P.elbowR + 3.5, r1: platR[i] + 3.5, r: 2.2 },
          { kind: 'hub', role: 'passive', name: `platform hub ${i + 1} (passive, O17)`, c: V.scale(v, platR[i] - 3.5), axis: v, r: 8.5, h: 10 });
      }
      const Vv = f.legs.map(l => l.v), pr = platR.map(r => r - 4);
      out.push({ kind: 'arc', role: 'fixed-arm', name: 'arm platform (C-saddle)', pts: K.greatArc(Vv[0], Vv[1], pr[0], pr[1]).concat(K.greatArc(Vv[1], Vv[2], pr[1], pr[2]), K.greatArc(Vv[2], Vv[0], pr[2], pr[0])), r: 3.5 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: V.scale(ctx.armAxis, P.cuff_at), axis: ctx.armAxis, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 });
      return out;
    }
  });
})();
