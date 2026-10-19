"""crown-ring-3r judgement probes (read-only on every claim; the model runs UNCHANGED through its own bench_eval, the
two-pass ring level included, on the claim's Bench(60,160) fast). New file; no bench, kit, model or row is edited.

  root     link 1's root against the ring it is bolted to (S3 / M1: is the rotor -> strap joint continuous metal, or
           does the strap start above / outside the ring with an unsampled standoff?): per taken pose, the root row's
           height along a1 above the rotor top (F + 9) and its radial offset from a1 vs the land [p1 - 8, p1 + 8]
  sizes    the claim's ring pitch p1 = 37.51 mm is between the model's own catalogue sizes (KA025XP0 34.9, KA030XP0
           41.3, docs/concepts/models/crown-ring-3r.py lines 13-14); every other param as claimed (M2)
  margin5  the claim re-worn at the user's 5 deg fold margin (it was searched at the old 10): a MEASUREMENT change,
           reported, never a verdict input
  sing     the spherical chain's near-singularity over the taken poses: |a1 . (a2 x a3)| quantiles, min th margin
  spans    each joint angle's span over the taken poses (the chain's own q, unwrapped by the largest empty arc) (M4)

    OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_crownring_probe.py -> docs/alignment/remeasure/crown-ring-3r_probe.json
"""
import importlib.util, json, math, os, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
RID = "crown-ring-3r"


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp)
    sys.modules[name] = m; sp.loader.exec_module(m); return m


def _short(r):
    return {k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "h1_used", "ring1_F",
                                  "levels", "inband_member", "park", "park_ok", "min_margin", "mass_g")}


def taken(B):
    return np.array([B.res[i] is not None and float(np.min(B.res[i])) >= 0 for i in range(len(B.res))])


def main():
    t0 = time.time()
    row = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", RID + ".json")))
    mod = _load("acp_crown", os.path.join(REPO, "docs", "concepts", "models", RID + ".py")); K = mod.K
    P = dict(mod.PARAMS, **row["best_params"]); out = dict(id=RID, params=P)
    B = K.bench(60, 160)
    r = mod.bench_eval(B, dict(P)); out["claim"] = _short(r)
    L = B._kit_last; ch, prof = L["chain"], L["prof"]; tk = taken(B); Ti = np.nonzero(tk)[0]
    m = {x.name: x for x in ch.members}; ring, l1 = m["ring1"], m["link1"]
    a1 = K.unit(np.asarray(ch.joints["J1"], float)); a2 = K.unit(np.asarray(ch.joints["J2"], float)); a3 = K.unit(np.asarray(ch.joints["J3"], float))
    F = float(np.asarray(prof["ring1"]).max()); top = F + mod.RING_H
    # link 1 metal points (P, n, 3) = level x direction; the root row = the samples nearest a1 in angle
    lev = np.asarray(prof["link1"], float); D = l1.D; X = lev[None, :, None] * D
    ang = np.degrees(np.arccos(np.clip((D * a1[:, None, :]).sum(-1), -1, 1)))      # (P, n) angle off a1
    ax = (X * a1[:, None, :]).sum(-1); rad = np.linalg.norm(X - ax[..., None] * a1[:, None, :], axis=-1)
    root = ang <= ang.min(1, keepdims=True) + 1.0                                   # samples within 1 deg of the root end
    rows = []
    for i in Ti:
        s = root[i]; rows.append((float(ax[i][s].min()), float(ax[i][s].max()), float(rad[i][s].min()), float(rad[i][s].max())))
    R = np.array(rows)
    # the strap's underside over the land: samples whose radial offset lies on the land
    on = (rad >= P["p1"] - mod.RING_HW) & (rad <= P["p1"] + mod.RING_HW)
    over = [float((ax[i][on[i]] - top).min()) for i in Ti if on[i].any()]
    out["root"] = dict(ring_level_F=round(F, 2), rotor_top=round(top, 2), land_radial=[round(P["p1"] - mod.RING_HW, 2), round(P["p1"] + mod.RING_HW, 2)],
                       root_axial_above_top_mm=dict(min=round(float((R[:, 0] - top).min()), 2), median=round(float(np.median(R[:, 0] - top)), 2), max=round(float((R[:, 1] - top).max()), 2)),
                       root_radial_mm=dict(min=round(float(R[:, 2].min()), 2), median=round(float(np.median(R[:, 2])), 2), max=round(float(R[:, 3].max()), 2)),
                       strap_over_land_gap_mm=dict(n=len(over), min=round(min(over), 2) if over else None, median=round(float(np.median(over)), 2) if over else None,
                                                   max=round(max(over), 2) if over else None),
                       link1_level_mm=dict(min=round(float(lev.min()), 2), max=round(float(lev.max()), 2)), n_taken=int(len(Ti)),
                       root_dir_off_a1_deg=round(math.degrees(math.atan2(P["p1"], P["h1"] if r.get("h1_used") is None else r["h1_used"] + mod.RING_H)), 2))
    # singularity of the spherical chain over the taken poses
    det = np.abs((a1 * np.cross(a2, a3)).sum(-1))[Ti]
    th = np.degrees(np.arccos(np.clip((a1 * a3).sum(-1), -1, 1)))
    mm = np.minimum.reduce([th - abs(P["a12"] - P["a23"]), P["a12"] + P["a23"] - th, 360 - P["a12"] - P["a23"] - th])[Ti]
    out["sing"] = dict(det_min=round(float(det.min()), 4), det_p5=round(float(np.percentile(det, 5)), 4), det_median=round(float(np.median(det)), 4),
                       th_margin_min=round(float(mm.min()), 3), th_margin_p5=round(float(np.percentile(mm, 5)), 3), n=int(len(Ti)))
    q = np.asarray(ch.q, float)[Ti]; sp = {}                        # K.axis_angle is in deg
    for j in range(q.shape[1]):
        a = np.sort(np.mod(q[:, j], 360.0)); gaps = np.diff(np.r_[a, a[0] + 360.0]); sp[f"J{j + 1}"] = round(float(360.0 - gaps.max()), 2)
    out["spans_deg"] = sp
    print("spans", json.dumps(sp))
    print("claim", json.dumps(out["claim"], default=float), "\nroot", json.dumps(out["root"]), "\nsing", json.dumps(out["sing"]), flush=True)
    # catalogue sizes (M2) and the 5 deg margin (measurement change)
    out["sizes"] = {}
    for name, p1 in (("KA025XP0", 34.9), ("KA030XP0", 41.3), ("claim", float(P["p1"]))):
        Bk = K.bench(60, 160); rk = mod.bench_eval(Bk, dict(P, p1=p1, h1=60.0)); out["sizes"][name] = dict(p1=p1, **_short(rk))
        print("size", name, json.dumps(out["sizes"][name], default=float), flush=True)
    Bm = K.bench(60, 160); rm = mod.bench_eval(Bm, dict(P, margin=5.0, h1=60.0)); out["margin5"] = _short(rm)
    print("margin5", json.dumps(out["margin5"], default=float), flush=True)
    out["secs"] = round(time.time() - t0, 1)
    out["source"] = "tools/alignment_crownring_probe.py: model crown-ring-3r.py unchanged (bench_eval, two-pass ring level, every kit check on), Bench(60,160) fast"
    p = os.path.join(REPO, "docs", "alignment", "remeasure", f"{RID}_probe.json"); json.dump(out, open(p, "w"), indent=1, default=float); print("out", p)


if __name__ == "__main__":
    main()
