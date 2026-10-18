"""Adversarial verifier for the crest-knee-3r JOGGLED cuff-knee claim (kj=1, 2026-10-18). Re-measures the claimed
configuration (row key best_params_joggle) with the crest-knee verifier harness (docs/concepts/verify/crest-knee-3r.py)
switched to CK.JogModel, frozen-shape protocol (fit on Bench(60,160) FAST, worn without refit on Bench(110,360) and the
disjoint held-out bench, CB_EXACT=1), plus this verifier's joggle checks:

  * every slice of the joggled knee link (pin-a flat, 4 ramp pieces, pin-b flat) vs: the E strap mid-surface WITHOUT any
    exemption near pin a (adjacent, 0.15 mm), hub 3's FULL can (adjacent at pin a, 0.15 mm) and hub 3 above its lower
    plate (rides with link 2: non-adjacent, >= 1 mm), hubs 1 / 2 and links 1 / 2 (non-adjacent, >= 1 mm);
  * the arm pad (cuff, at tr_b) vs the E boss and the E strap (member 3, non-adjacent, >= 1 mm);
  * the knee link's skin samples recomputed from the joggle law (level(x) = tr_a .. tr_b between the pin flats) and
    compared with the model's rigid knee set; the joggle's step, ramp run and angle, and whether a bent 3 mm bar with
    15 mm inner bend radius (user's CAD ruling) can make it (else the part is machined, as claimed);
  * per-pose dumps (tools/alignment_paired.py format) under docs/alignment/remeasure/crest-knee-3r-joggle_v_<wear>_perpose.json
    (the flat verified dumps are left untouched);
  * the continuity flood (the harness's flood) at the joggle parameters.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/crest-knee-3r-joggle.py wear <bench|held> <out.json>
    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/crest-knee-3r-joggle.py flood <out.json> <bench_wear.json>
"""
import importlib.util, json, math, os, subprocess, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
_sp = importlib.util.spec_from_file_location("ck_verifier_for_joggle", os.path.join(HERE, "crest-knee-3r.py"))
V = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(V)
CB, CK, PK, PV, KIT = V.CB, V.CK, V.PK, V.PV, V.KIT
S = PK.S
V.CK.Model = V.CK.JogModel                                   # the claimed knee: fit, frozen wear and every check
ROW = V.ROW; P_JOG = dict(ROW["best_params_joggle"]); assert P_JOG.get("kj") == 1
V.ROW = dict(ROW); V.ROW["best_params"] = P_JOG             # the harness's flood reads ROW["best_params"]
KEYS = V.KEYS; REM = V.REM


def joggle_checks(M, B):
    D = M.D; P = D.p; tp = P["tp"]; fr = M.fr; sn = D.sn; h = S.T_LINK / 2
    tra, trb = float(M.tr), float(M.tr_b); lc = float(P["lc"])
    run = max(lc - 2 * PK.BOSS_R, 0.0); step = abs(tra - trb); ang = math.degrees(math.atan2(step, run)) if run > 0 else 90.0
    # bent-bar S-bend with two tangent arcs of mid radius 15 + 1.5 mm and no straight: largest rise inside the run
    Rm = 15.0 + 1.5; th = math.asin(min(1.0, run / (2 * Rm))); rise_bent = 2 * Rm * (1 - math.cos(th))
    out = dict(tr_a=round(tra, 3), tr_b=round(trb, 3), step_mm=round(step, 3), ramp_run_mm=round(run, 2), ramp_deg=round(ang, 2),
               bent_bar_R15_max_rise_mm=round(rise_bent, 2), bent_bar_ok=bool(rise_bent >= step), tp=round(tp, 3))
    # knee skin samples vs the joggle law
    s = (M.g["knee"][1] - fr["A0m"]) @ fr["eK"]; a0, b0 = PK.BOSS_R, max(lc - PK.BOSS_R, PK.BOSS_R + 1e-6)
    w = np.clip((b0 - s) / (b0 - a0), 0, 1); lev = tra * w + trb * (1 - w)
    exp = M.g["knee"][1] + (lev + tp + S.RUN)[:, None] * sn; out["knee_samples_vs_law_max_mm"] = round(float(np.abs(exp - M.rigid["knee"][1]).max()), 4)
    out["pad_samples_level_err_mm"] = round(float(np.abs((M.rigid["pad"][1] - M.g["pad"][1]) @ sn - trb).max()), 4)
    out["boss_samples_level_err_mm"] = round(float(np.abs((M.rigid["boss"][1] - M.g["boss"][1]) @ sn - tra).max()), 4)
    # E boss solid (member 3) and E strap mid-surface, home frame
    e, f = S.frame_of(sn); angs = np.linspace(0, 2 * np.pi, 24, endpoint=False); dd = S.disc(PK.BOSS_R, 1.0)
    boss = np.concatenate([fr["A0"] + z * sn + PK.BOSS_R * (np.cos(angs)[:, None] * e + np.sin(angs)[:, None] * f) for z in (tra, tra + tp / 2, tra + tp)]
                          + [fr["A0"] + z * sn + dd[:, :1] * e + dd[:, 1:] * f for z in (tra, tra + tp)])
    sl = M._knee_slices()
    _, X3 = M.cyl_surf["hub3"]; cen3 = D.c[2] + M.f[2] * D.u[2]; zz = (X3 - cen3) @ D.u[2]; H3up = X3[zz >= S.UP - 1e-6]
    taken = V.taken_list(B); low = {}; bad = {}
    def note(key, v, i, lim):
        if v < low.get(key, (1e9, None))[0]: low[key] = (v, i)
        if v < lim: bad.setdefault(key, set()).add(i)
    for i in taken:
        def tf(m, X): R, t = M.T(m, i); return X @ R.T + t
        R6, t6 = M.T(6, i); Em = tf(*M.Emid); surf = {k: tf(m, X) for k, (m, X) in M.cyl_surf.items()}
        strap = {k: tf(m, X) for k, (m, X) in M.strap.items()}; h3u = tf(3, H3up)
        for cen, Rk, half in sl:
            box = (R6 @ cen + t6, R6 @ Rk, half)
            vb = lambda X, extra=0.0: float(M.sd_box(X, *box).min()) - extra if len(X) else 1e9
            note("knee-E(all)", vb(Em, h), i, M.ADJ); note("knee-hub3(full)", vb(surf["hub3"]), i, M.ADJ)
            note("knee-hub3(upper)", vb(h3u), i, S.PART_CLEAR)
            for k in ("hub1", "hub2"): note(f"knee-{k}", vb(surf[k]), i, S.PART_CLEAR)
            for k in ("L1", "L2"):
                if k in strap: note(f"knee-{k}", vb(strap[k], h), i, S.PART_CLEAR)
        bx = M._boxes_at_final(i); pc, pR, ph = bx["pad"]
        note("pad-boss", float(M.sd_box(tf(3, boss), pc, pR, ph).min()), i, S.PART_CLEAR)
        note("pad-E(all)", float(M.sd_box(Em, pc, pR, ph).min()) - h, i, S.PART_CLEAR)
    lab = lambda i: dict(i=int(i), kind=B.kind[i], plane=B.poses[i]["plane"], elev=B.poses[i]["elev"], axial=B.poses[i]["axial"])
    out["low"] = {k: dict(mm=round(v, 3), **lab(i)) for k, (v, i) in low.items() if i is not None}
    out["bad"] = {k: len(v) for k, v in bad.items()}
    allbad = set().union(*bad.values()) if bad else set()
    return out, allbad


def wear(which, outp):
    P = dict(P_JOG); t0 = time.time()
    M1, P2, fit, ji = V.fit_fast(P)
    B = CB.Bench(n_clip=110, n_ws=360) if which == "bench" else V.held_bench()
    M = V.worn(M1, P2, B); r = M.run(); model = {k: r[k] for k in KEYS}
    assert type(M).__mro__[1] is CK.JogModel
    why = {k: int((M.why == k).sum()) for k in ("fold", "slide", "flip", "closure", "j3stop", "skin", "parts", "contact")}
    aud0 = PK.audit(M, B)
    ex, bad1 = PV.extra_checks(M, B)
    cc, marg = V.crest_checks(M, B, P2)
    jg, bad2 = joggle_checks(M, B)
    bad = set(bad1) | set(bad2)
    res0 = list(B.res)
    for i in bad: B.res[i] = None
    rc = B.report(); corrected = {k: rc[k] for k in KEYS}
    aud = PK.audit(M, B)
    import alignment_paired as AP
    poses = AP._dump_bench(M, B)
    for row in poses:
        i = row["i"]; row.update(why=str(M.why[i]), th_margin=round(float(marg[i]), 3), q3p=round(float(M.q3p[i]), 2), knee=round(float(M.K["ang"][i]), 2))
    try: git = subprocess.run(["git", "-C", REPO, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    except Exception: git = None
    dump = dict(id=CK.ID + "-joggle", wear=which, params=P, frozen=corrected, report=rc, poses=poses, recomputed=AP.gap_parts(poses),
                secs=round(time.time() - t0, 1), exact=os.environ.get("CB_EXACT") == "1", git=git,
                note="written by docs/concepts/verify/crest-knee-3r-joggle.py (harness + pin-knee + joggle checks applied)")
    dpath = os.path.join(REM, f"{CK.ID}-joggle_v_{which}_perpose.json"); json.dump(dump, open(dpath, "w"), default=float)
    contacts = [dict(i=int(i), kind=B.kind[i], plane=B.poses[i]["plane"], elev=B.poses[i]["elev"], axial=B.poses[i]["axial"],
                     depth=round(float(np.min(B.res[i])), 2)) for i in range(len(B.idx)) if B.res[i] is not None and len(B.res[i]) and float(np.min(B.res[i])) < 0]
    el = np.array([p["elev"] for p in B.poses]); ax = np.array([p["axial"] for p in B.poses]); kind = np.array(B.kind); tk = set(V.taken_list(B))
    ab = np.nonzero((np.abs(ax) >= 150) & (kind == "ws"))[0]; oh = np.nonzero((el >= 140) & (kind == "ws"))[0]
    B.res = res0
    out = dict(wear=which, params=P, model_class="JogModel", mode=B.mode, exact=os.environ.get("CB_EXACT") == "1", fit_fast=fit, j3stop_fit=ji,
               model=model, why=why, model_audit=aud0, extra=ex, joggle=jg, removed=sorted(int(i) for i in bad), crest=cc, corrected=corrected,
               corrected_audit=aud, contacts=contacts, contact_depth_sum=round(float(sum(c["depth"] for c in contacts)), 2),
               axial150=dict(total=int(len(ab)), taken=int(sum(1 for i in ab if i in tk))),
               overhead=dict(total=int(len(oh)), taken=int(sum(1 for i in oh if i in tk))),
               dump=dict(path=os.path.relpath(dpath, REPO), recomputed=dump["recomputed"]), secs=round(time.time() - t0, 1))
    json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps(dict(wear=which, mode=B.mode, fit=fit, model=model, corrected=corrected, removed=len(bad), near1=aud.get("gap_near1"),
                          crest=cc, joggle=jg, extra={k: ex[k] for k in ("closure_max", "closure_bad_poses", "knee_vs_hub3_upper_bad", "boss_bad", "spans_deg", "pad")},
                          recomputed=dump["recomputed"], contacts=contacts, secs=out["secs"]), default=float), flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "wear": wear(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "flood": V.flood(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
