"""Alignment re-wear + probe for cam-coupled-4r (a kit model with no pin-knee-style audit(M, B), no snap() and no
fixed_prof hook, so neither tools/alignment_audit.py remeasure nor tools/alignment_kit_rewear.py can wrap it).

Read-only on every claim: the model file runs UNCHANGED. The fit is the model's own evaluate() on Bench(60,160) fast
(the row's claim bench: the gap must reproduce 50.67). The wear is the model's own frozen() (fit fast, every level and
the slot arc frozen, worn on Bench(110,360), exact with CB_EXACT=1); its module-level evaluate() is wrapped only to keep
the worn bench. Each bench is then read by the audit's own instruments (alignment_audit.deep_audit: near-touch 1 / 2 /
3 mm, clip metal histogram, band 3-14; alignment_wear_probe.analyse: unscored workspace in-band, overhead, clearance
floors, contact depths) plus a kinematic read of the taken poses:
  * th margin of the J1-J2-J3 dyad (angle(J1, J3) from its fold, tools/concept_kit.py lines 25-30) - the model never
    clamps it (J2 is placed by the slot law); the J3 dyad (J2-J3-J4) margin, which the model clamps at m3 = 0.5 deg;
  * the slaved-map singularity distance (sing), cam transmission (pa, hold), J2 span (idle), J3-dyad branch mix;
  * the roller post: clearance of the pin axis from link 1's centreline (deg and mm at link 1's level);
  * a workspace continuity flood (S5): kNN-8 edges among taken workspace poses by frame angle, 2-deg slerp, the model's
    own build() at every step (closure, cam rules, slot arc), no joint value or joint axis stepping > 10 deg (the
    continuity rule; 25 deg = the kit's K2 reported too); seeds = taken workspace poses at the lowest elevation.

    OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_cam_coupled_probe.py fast      -> remeasure/cam-coupled-4r_fast.json
    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_cam_coupled_probe.py bench -> remeasure/cam-coupled-4r_bench.json
"""
import importlib.util, json, math, os, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import alignment_audit as AA                                     # noqa: E402
import alignment_wear_probe as WP                                # noqa: E402

RID = "cam-coupled-4r"


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp)
    sys.modules[name] = m; sp.loader.exec_module(m); return m


class _M:
    cmin = {}


def _r(x, n=3):
    return None if x is None or not np.isfinite(x) else round(float(x), n)


def kin_diag(mod, B, p):
    K = mod.K; F = B._kitF; L = B._kit_last; take = np.asarray(L["take"], bool)
    k = mod.kinematics(F, p); kn = k["kn"]; u1, u4, p2, p3, pin = kn.u1, kn.u4, k["p2"], k["p3"], k["pin"]
    a1, a2 = p["a1"], p["a2"]
    th = np.degrees(np.arccos(np.clip((u1 * p3).sum(-1), -1, 1)))
    m12 = np.minimum.reduce([th - abs(a1 - a2), a1 + a2 - th, 360 - a1 - a2 - th])
    q2 = K.axis_angle(p2, u1, p3); el = np.array([q["elev"] for q in B.poses]); kind = np.array(B.kind)
    # pin axis vs link 1 centreline (great-circle arc u1 -> p2): angular distance, and its foot inside the arc?
    nrm = K.unit(np.cross(u1, p2)); dperp = np.degrees(np.arcsin(np.clip(np.abs((pin * nrm).sum(-1)), 0, 1)))
    proj = K.unit(pin - (pin * nrm).sum(-1, keepdims=True) * nrm)
    t_along = np.degrees(np.arccos(np.clip((proj * u1).sum(-1), -1, 1)))
    inside = (t_along <= a1) & (np.degrees(np.arccos(np.clip((proj * p2).sum(-1), -1, 1))) <= a1)
    dpin_l1 = np.where(inside, dperp, np.degrees(np.minimum(np.arccos(np.clip((pin * u1).sum(-1), -1, 1)),
                                                            np.arccos(np.clip((pin * p2).sum(-1), -1, 1)))))
    prof = {kk: np.asarray(v, float) for kk, v in L["prof"].items()}
    r_l1 = float(np.median(prof["link1"])) if "link1" in prof else 90.0
    T = take
    def st(x, m):
        x = np.asarray(x, float)[m]; return None if not len(x) else dict(min=_r(x.min(), 2), p05=_r(np.percentile(x, 5), 2), median=_r(np.median(x), 2), max=_r(x.max(), 2))
    out = dict(n_taken=int(T.sum()), n_taken_ws=int((T & (kind == "ws")).sum()), n_taken_clip=int((T & (kind == "clip")).sum()),
               th_margin_J1J3_deg=st(m12, T), th_margin_lt5=int((m12[T] < 5).sum()), th_margin_lt5_share=_r(float((m12[T] < 5).mean()) if T.any() else None, 4),
               j3_dyad_margin_deg=st(k["margin"], T), j3_dyad_lt5=int((k["margin"][T] < 5).sum()), j3_dyad_lt5_share=_r(float((k["margin"][T] < 5).mean()) if T.any() else None, 4),
               sing_deg=st(k["sing"], T), pa=st(k["pa"], T), hold_mm_per_rad=st(k["hold"], T),
               J2_deg=st(q2, T), J2_span_deg=_r(float(np.ptp(q2[T])) if T.any() else None, 1),
               s3_share_plus=_r(float((k["s3"][T] > 0).mean()) if T.any() else None, 4),
               slot_coord_span_deg=_r(float(np.ptp(k["ds"][T])) if T.any() else None, 1), slot_cut_deg=_r(2 * p["s_half"], 1),
               pin_to_link1_deg=st(dpin_l1, T), pin_to_link1_mm_at_link1_level=st(np.radians(dpin_l1) * r_l1, T), link1_level_mm=_r(r_l1, 1),
               post_clash_lt_8mm=int(((np.radians(dpin_l1) * r_l1)[T] < 8.0).sum()),
               overhead_taken=int((T & (el >= 140) & (kind == "ws")).sum()), overhead_total=int(((el >= 140) & (kind == "ws")).sum()),
               raised_taken=int((T & (el >= 120) & (kind == "ws")).sum()), raised_total=int(((el >= 120) & (kind == "ws")).sum()),
               levels_mm={kk: _r(float(np.median(v)), 1) for kk, v in prof.items()})
    return out, dict(m12=m12, jm=k["margin"], sing=k["sing"])


def flood(mod, B, p, step_deg=2.0, knn=8, jumps=(10.0, 25.0)):
    K = mod.K; F = B._kitF; take = np.asarray(B._kit_last["take"], bool); kind = np.array(B.kind)
    el = np.array([q["elev"] for q in B.poses]); W = np.nonzero(take & (kind == "ws"))[0]
    if len(W) < 2: return None
    from scipy.spatial.transform import Rotation as R
    def ang(i, J):
        a = np.degrees(R.from_matrix(np.einsum("ji,njk->nik", F.RS[i], F.RS[J])).magnitude())
        b = np.degrees(R.from_matrix(np.einsum("ji,njk->nik", F.RHG[i], F.RHG[J])).magnitude()); return np.maximum(a, b)
    E = set()
    for a_, i in enumerate(W):
        d = ang(i, W); d[a_] = 1e9
        for b_ in np.argsort(d)[:knn]: E.add((min(a_, int(b_)), max(a_, int(b_))))
    E = sorted(E); res = {}
    edge_ok = {j: [] for j in jumps}; t0 = time.time()
    for a_, b_ in E:
        i, j = int(W[a_]), int(W[b_]); Fs = K._slerp_frames(F, i, j, step_deg); ch = mod.build(B, Fs, p); n = len(Fs.RS)
        jmp = 0.0
        d = np.diff(np.asarray(ch.q, float).reshape(n, -1), axis=0); d = (d + 180) % 360 - 180; jmp = float(np.abs(d).max(initial=0))
        for ax in ch.joints.values():
            ax = K.unit(np.asarray(ax, float).reshape(n, 3))
            jmp = max(jmp, float(np.degrees(np.arccos(np.clip((ax[1:] * ax[:-1]).sum(-1), -1, 1))).max(initial=0)))
        okall = bool(np.all(ch.ok))
        for jt in jumps: edge_ok[jt].append(okall and jmp <= jt)
    seeds = [a_ for a_, i in enumerate(W) if el[i] <= el[W].min() + 1e-6]
    for jt in jumps:
        adj = {a_: [] for a_ in range(len(W))}
        for (a_, b_), ok in zip(E, edge_ok[jt]):
            if ok: adj[a_].append(b_); adj[b_].append(a_)
        seen = set(seeds); st = list(seeds)
        while st:
            x = st.pop()
            for y in adj[x]:
                if y not in seen: seen.add(y); st.append(y)
        nws = int((kind == "ws").sum()); ov = (el >= 140) & (kind == "ws")
        res[f"jump{jt:g}"] = dict(edges=len(E), edges_ok=int(sum(edge_ok[jt])), seeds=len(seeds), seed_elev=_r(float(el[W].min()), 1),
                                  static_taken_ws=len(W), connected_ws=len(seen), static_reach_ws=_r(len(W) / nws, 4), connected_reach_ws=_r(len(seen) / nws, 4),
                                  overhead_static=int(ov[W].sum()), overhead_connected=int(sum(1 for a_ in seen if ov[W[a_]])), overhead_total=int(ov.sum()))
    res["secs"] = round(time.time() - t0, 1)
    return res


def read_bench(mod, B, p, r):
    kind = np.array(B.kind); el = np.array([q["elev"] for q in B.poses]); WP.kind, WP.el = kind, el
    deep = AA.deep_audit(_M, B)
    try: probe = WP.analyse(_M, B)
    except Exception as e: probe = dict(error=repr(e))
    kd, _ = kin_diag(mod, B, p)
    rep = {kk: r.get(kk) for kk in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "gap_near1", "near1", "min_metal_skin",
                                    "overhead", "inband_member", "min_margin", "pa_min_taken", "hold_min_taken", "sing_min_taken", "cut_noroot",
                                    "cut_cam", "cut_slot", "groove_inner_mm", "groove_on_hub1", "slot_arc_deg", "slot_len_mm", "pin_len_mm",
                                    "crown_contact_poses", "crown_min", "mass_g", "flips", "closure")}
    return rep, deep, probe, kd


def main(wear):
    row = json.load(open(os.path.join(AA.ROWS, RID + ".json"))); P = dict(row["best_params"])
    mod = _load("acc_" + RID.replace("-", "_"), os.path.join(AA.MODELS, RID + ".py")); K = mod.K; t0 = time.time()
    out = dict(id=RID, wear=wear, params=P, exact=os.environ.get("CB_EXACT") == "1", git=AA._git("rev-parse", "--short", "HEAD"))
    if wear == "fast":
        B = K.bench(60, 160); p, r = mod.evaluate(B, dict(mod.PARAMS, **P))
        rep, deep, probe, kd = read_bench(mod, B, p, r)
        out.update(frozen=rep, deep=deep, probe=probe, kin=kd, flood=flood(mod, B, p), mode=B.mode,
                   source="tools/alignment_cam_coupled_probe.py: the model's evaluate() unchanged on Bench(60,160) fast (the row's claim bench)")
    else:
        box = []; ev = mod.evaluate
        def wrapped(B, params, preset=False):
            pp, rr = ev(B, params, preset=preset); box.append((B, pp, rr)); return pp, rr
        mod.evaluate = wrapped
        tmp = os.path.join(AA.REM, f"{RID}_{wear}_frozen_raw.json"); os.makedirs(AA.REM, exist_ok=True)
        try: res = mod.frozen(dict(mod.PARAMS, **P), tmp)
        finally: mod.evaluate = ev
        (Bf, pf, rf), (B, p, r) = box[0], box[-1]
        rep, deep, probe, kd = read_bench(mod, B, p, r)
        fit = {kk: rf.get(kk) for kk in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "gap_near1", "min_metal_skin", "overhead")}
        out.update(fit_fast=fit, frozen=rep, deep=deep, probe=probe, kin=kd, parts_ib14=r.get("inband_member"), mode=B.mode,
                   flood=flood(mod, B, p) if "--noflood" not in sys.argv else None,
                   audit=dict(gap_near1=r.get("gap_near1"), near_touch_min_mm=r.get("min_metal_skin")),
                   source="tools/alignment_cam_coupled_probe.py: the model's frozen() unchanged (fit Bench(60,160) fast, levels + slot frozen, worn Bench(110,360))")
        try: os.remove(tmp)
        except OSError: pass
    out["secs"] = round(time.time() - t0, 1)
    path = os.path.join(AA.REM, f"{RID}_{wear}.json"); json.dump(out, open(path, "w"), indent=1, default=float)
    print(json.dumps(dict(frozen={kk: out["frozen"].get(kk) for kk in ("gap", "reach", "follow", "inband14", "contact", "gap_near1", "min_metal_skin", "overhead")},
                          deep={kk: v for kk, v in out["deep"].items() if kk not in ("coord_spans",)}, kin=out["kin"], flood=out["flood"], secs=out["secs"], out=path), default=float))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "fast")
