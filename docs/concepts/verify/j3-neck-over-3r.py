"""j3-neck-over-3r - skeptic verifier (round 6).

Wears the claim's C6 shape with the claim's own frozen protocol (fit Bench(60,160) fast -> freeze every profile -> wear
Bench(110,360), CB_EXACT=1, K6 radial overlap 1 mm, continuity flood fill) and then audits every taken pose of the wear
INDEPENDENTLY of the model's law, from the built chain's joint axes alone:
  * link rigidity: angle(J1, K) = b1, angle(K, J2) = b2, angle(J2, J3) = a2 on every taken pose (closure);
  * J1 fixed in the scapula frame, J3 fixed in the humerus frame (the chain really carries the arm);
  * K one-sided: a1e = angle(J1, J2) in [a1, a1max]; K on stop A (a1e = a1) in the free state;
  * J2's OWN angle q2 inside its physical stops (the stop values recomputed from th_lo / th_hi with K on stop A);
  * the J1-J3 dyad margin of the effective chain >= the 5-deg fold margin;
  * K2 along the clips: no joint (J1, K, J2, J3) steps > 25 deg between consecutive taken frames of a clip.
Variants: claim (C6 as claimed, neck 13.41 wide), nw14 (the K7 neck at its 14 x 6 catalogue section).
    CB_EXACT=1 OMP_NUM_THREADS=1 python3 docs/concepts/verify/j3-neck-over-3r.py <claim|nw14> out.json
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
sp = importlib.util.spec_from_file_location("j3neck_v", os.path.join(REPO, "docs/concepts/models/j3-neck-over-3r.py"))
J = importlib.util.module_from_spec(sp); sp.loader.exec_module(J)
K, AK = J.K, J.AK
ROW = json.load(open(os.path.join(REPO, "docs/concepts/rows/j3-neck-over-3r.json")))
BP = ROW["best_params"]
ang = lambda a, b: np.degrees(np.arccos(np.clip((K.unit(a) * K.unit(b)).sum(-1), -1, 1)))


def run(variant, out):
    t0 = time.time(); par = dict(BP)
    if variant == "nw14": par["nw"] = 14.0
    benches = []; kb = K.bench
    K.bench = lambda *a, **k: benches.append(kb(*a, **k)) or benches[-1]
    try: d = J.frozen(par, "bench")
    finally: K.bench = kb
    Bb = benches[-1]; ch = Bb._kit_last["chain"]; F = Bb._kitF
    p = AK.stops(dict(J.PARAMS, **par)); a1, a2, b1, b2 = (float(p[k]) for k in ("a1", "a2", "b1", "b2"))
    tk = np.array([Bb.res[i] is not None and float(np.min(Bb.res[i])) >= 0 for i in range(len(Bb.idx))])
    taken = np.array([Bb.res[i] is not None for i in range(len(Bb.idx))])
    j = {k: np.asarray(v, float) for k, v in ch.joints.items()}; T = np.nonzero(taken)[0]
    e_b1 = np.abs(ang(j["J1"], j["K"]) - b1)[T].max(); e_b2 = np.abs(ang(j["K"], j["J2"]) - b2)[T].max()
    e_a2 = np.abs(ang(j["J2"], j["J3"]) - a2)[T].max()
    u1s = np.einsum("pji,pj->pi", F.RS, j["J1"]); u3h = np.einsum("pji,pj->pi", F.RHG, j["J3"])
    e_u1 = ang(u1s[T], u1s[T][:1]).max(); e_u3 = ang(u3h[T], u3h[T][:1]).max()
    a1e = ang(j["J1"], j["J2"]); th = ang(j["J1"], j["J3"])
    m3 = np.minimum(th - np.abs(a1e - a2), np.minimum(a1e + a2, 360 - a1e - a2) - th)
    kin = AK.kinematics(F, p); st = kin["state"]
    q2s_hi = float(AK._q2_of(np.array([p["th_hi"]]), a1, p)[0][0]); q2s_lo = float(AK._q2_of(np.array([p["th_lo"]]), a1, p)[0][0])
    q2 = np.asarray(ch.q, float)[:, 2]
    # the free window is the arc from q2s_lo to q2s_hi that contains q2 at mid-window (q2 is a signed, wrapping angle)
    q2m = float(AK._q2_of(np.array([0.5 * (p["th_lo"] + p["th_hi"])]), a1, p)[0][0])
    w = lambda x: (np.asarray(x) - q2s_lo) % 360.0; span = float(w(q2s_hi)); inside_mid = float(w(q2m)) <= span
    rel = w(q2[T]); ins = (rel <= span + 0.05) | (rel >= 360 - 0.05) if inside_mid else (rel >= span - 0.05) | (rel <= 0.05)
    q2_out = int((~ins).sum()); lo, hi = q2s_lo, q2s_hi
    a1e_bad = int(((a1e[T] < a1 - 0.05) | (a1e[T] > float(p["a1max"]) + 0.05)).sum())
    freeA_bad = int((np.abs(a1e[T] - a1)[st[T] == 0] > 0.05).sum())
    # K2 along the clips between consecutive taken frames
    q = np.asarray(ch.q, float); flips = 0; maxstep = 0.0; fl = []
    RA = np.einsum("pji,pjk->pik", F.RS, F.RHG)                 # humerus in the scapula frame
    clip = np.array([k == "clip" for k in Bb.kind]); cid = [Bb.clip[i] if clip[i] else None for i in range(len(Bb.idx))]
    for c in set(x for x in cid if x is not None):
        ii = [i for i in range(len(Bb.idx)) if cid[i] == c and taken[i]]
        for a, b in zip(ii[:-1], ii[1:]):
            dq = np.abs((q[b] - q[a] + 180) % 360 - 180); s = float(dq.max()); maxstep = max(maxstep, s); flips += s > 25
            if s > 25:
                arm = math.degrees(math.acos(max(-1.0, min(1.0, (np.trace(RA[a].T @ RA[b]) - 1) / 2))))
                fl.append(dict(clip=c, i=[int(a), int(b)], joint=["J1", "K", "J2", "J3"][int(dq.argmax())], step=round(s, 1), arm_rot_deg=round(arm, 1),
                               steps=[round(float(x), 1) for x in dq], th=[round(float(th[a]), 1), round(float(th[b]), 1)], margin=[round(float(m3[a]), 1), round(float(m3[b]), 1)]))
    aud = dict(n_taken=int(len(T)), n_taken_no_contact=int(tk.sum()), arc_err_deg=dict(b1=round(float(e_b1), 4), b2=round(float(e_b2), 4), a2=round(float(e_a2), 4)),
               J1_drift_in_scapula_deg=round(float(e_u1), 4), J3_drift_in_humerus_deg=round(float(e_u3), 4),
               min_J1J3_margin_deg=round(float(m3[T].min()), 3), a1e_range=[round(float(a1e[T].min()), 3), round(float(a1e[T].max()), 3)],
               a1max=round(float(p["a1max"]), 3), a1e_out_of_K_range=a1e_bad, free_state_K_off_stopA=freeA_bad,
               q2_stops_deg=[round(lo, 3), round(hi, 3)], q2_mid=round(q2m, 3), q2_window_wraps=bool(inside_mid), q2_range_taken=[round(float(q2[T].min()), 3), round(float(q2[T].max()), 3)], q2_outside_stops=q2_out,
               states_taken=dict(free=int((st[T] == 0).sum()), stretched=int((st[T] == 1).sum()), folded=int((st[T] == -1).sum())),
               clip_max_joint_step_deg=round(maxstep, 2), clip_flips_gt25=int(flips), clip_big_steps=fl, audit_problems=Bb._kit_last.get("audit"),
               neck_width=float(min(14.0, max(10.0, float(par.get("nw", 14.0))))))
    d["variant"] = variant; d["independent_audit"] = aud; d["secs_total"] = round(time.time() - t0, 1)
    json.dump(d, open(out, "w"), indent=1, default=float)
    print(json.dumps(dict(variant=variant, static=d["static"], connected=d["connected"], audit=aud), default=float), flush=True)


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "claim", sys.argv[2] if len(sys.argv) > 2 else "/dev/null")
