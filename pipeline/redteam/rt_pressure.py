"""ATTACK 3 - pressure points on the reference design: where does metal come within 2 mm of the skin, or enter it?
Exact signed distance (judge/sdist.py) of every exo part (vertices, near-filtered at 15 mm) to the exact posed, closed body
mesh (avg/body_pose.py posed(), at the frame's actual pose p, as judge/body_contact.py), every STEP-th frame of every clip.
The closest skin point is labelled with a body region (rt_common.skin_regions: nearest named structure at rest).
Parts are split into the user's own (group F, TOP and the elbow hardware - not ours to change), BOTTOM (the one user part
we may modify, now BOTTOM + neck + JN hub) and custom parts.

Second part: the base on a THORAX-fixed back plate (physical truth): base vertices in the canonical scapula frame
(G0 = scap(elev0)^T G_base(frame 0)), placed at x - lift(elev) instead of scap(elev) x, vs the body posed at the person's
wanted pose. Where (region, part, elevation) does it enter the body?
    python3 rt_pressure.py [STEP=4]  -> results/pressure.json
"""
import json, os, sys, time
import numpy as np
from scipy.spatial import cKDTree
import rt_common as RC
from rt_common import BP, GD
from common import load_parts
from sdist import signed_distance
import scene_export as SE

STEP = int(sys.argv[1]) if len(sys.argv) > 1 else 4; NEAR = 15.0; t0 = time.time()
REG = RC.skin_regions()["region"]
USER_H = ("TOP", "CirPattern", "Revolve", "M4 ULTRA", "5mm D", "IGUS THRUST")
def owner(g, n):
    if g == "F" or n.startswith(USER_H): return "user"
    if n.startswith("BOTTOM"): return "BOTTOM (user part, modifiable)"
    return "custom"
parts = [(g, n, P[:: max(1, len(P) // 5000)], owner(g, n)) for g, n, P, _ in load_parts(RC.DD)]
FR = RC.clips(); C0 = FR[0]
G0 = BP.scap(C0[3][1]).T @ np.array(C0[5]["base"]).reshape(3, 3)
BASE = [(n, P[:: max(1, len(P) // 5000)] @ G0.T) for g, n, P, o in parts if g == "base"]
L = json.load(open(os.path.join(RC.REPO, "pipeline", "avg", "body_mesh.json"))); LM, S = L["landmarks"], L["scale"]
CEN = None
_cache = {}
def body(pose5):
    key = tuple(np.round(pose5, 3))
    if key not in _cache:
        _cache.clear(); V = BP.posed(dict(zip(["plane", "elev", "axial", "flex", "pron"], pose5)))
        _cache[key] = (V, cKDTree(V), cKDTree(V[BP.F].mean(1)))
    return _cache[key]

rec = {}                                     # part -> list of per-frame (sd_min, region, n_within_2mm, clip, i, pose)
base_rec = []
idx = list(range(0, len(FR), STEP))
for kk, k in enumerate(idx):
    clip, i, want, p, held, Gd, q = FR[k]
    fr = dict(p=p, G=Gd); X, pose = SE.frame_xforms(fr)
    V, vt, ct = body(p)
    for g, n, P0, o in parts:
        if g not in X: continue
        R, t = X[g]; P = P0 @ np.asarray(R).T + t; dn, jn = vt.query(P, distance_upper_bound=NEAR); near = dn < NEAR
        if not near.any(): continue
        sd = signed_distance(P[near], V, BP.F, tree=ct); j = int(np.argmin(sd)); vj = jn[near][j]
        xa = GD.Rh_of(*p[:3]).T @ P[near][j]                                  # arm frame: theta about the humerus (0 lateral, + posterior), s down the arm
        loc = dict(world=[round(float(v)) for v in P[near][j]], theta_arm=round(float(np.degrees(np.arctan2(-xa[0], xa[2])))), s_arm=round(float(-xa[1])))
        rec.setdefault((g, n, o), []).append((float(sd[j]), REG[vj], int((sd < 2.0).sum()), int((sd < 0).sum()), clip, i, [round(v) for v in p[:4]], bool(held), loc))
    # thorax-fixed base vs the body at the wanted pose (the girdle moves whether or not the exo follows)
    lift = BP.segs(LM, S, dict(zip(["plane", "elev", "axial", "flex", "pron"], want)))[1]
    Vw, vtw, ctw = body(want)
    for n, B in BASE:
        for mode, Pb in (("thorax", B - lift), ("scapula", B @ BP.scap(want[1]).T)):
            sd = signed_distance(Pb, Vw, BP.F, tree=ctw); j = int(np.argmin(sd)); _, vj = vtw.query(Pb[j])
            ins = sd < 0; regs = {}
            if ins.any():
                _, vv = vtw.query(Pb[ins])
                for r_ in REG[vv]: regs[r_] = regs.get(r_, 0) + 1
            base_rec.append(dict(part=n, mode=mode, clip=clip, i=i, want=[round(v, 1) for v in want[:3]], elev=float(want[1]), lift=float(lift[1]), sd_min=float(sd[j]),
                                 region=REG[vj], at_mm=[round(float(v)) for v in Pb[j]], inside_share=float(ins.mean()), inside_regions=regs))
    if kk % 20 == 0: print(f"{kk}/{len(idx)} frames {time.time() - t0:.0f}s", flush=True)

# ------------------------------------------------------------------ summarise
summ = {}
for (g, n, o), L_ in rec.items():
    sd = np.array([r[0] for r in L_]); k = int(np.argmin(sd)); w = L_[k]
    close = [r for r in L_ if r[0] < 2.0]; inside = [r for r in L_ if r[0] < -0.5]
    regs = {}
    for r in close: regs[r[1]] = regs.get(r[1], 0) + 1
    clips_close = {}
    for r in close: clips_close[r[4]] = clips_close.get(r[4], 0) + 1
    summ[f"{g}|{n}"] = dict(owner=o, frames_near=len(L_), min_sd_mm=round(float(sd.min()), 2), worst=dict(region=w[1], clip=w[4], frame=w[5], pose=w[6], held=w[7], **w[8]),
                            frames_within_2mm=len(close), frames_inside_0p5=len(inside), regions_within_2mm=regs, clips_within_2mm=clips_close,
                            max_vertices_within_2mm=max(r[2] for r in L_), share_frames_within_2mm=round(len(close) / len(idx), 3))
BR = {}
for mode in ("thorax", "scapula"):
    rs = [r for r in base_rec if r["mode"] == mode]; sd = np.array([r["sd_min"] for r in rs]); el = np.array([r["elev"] for r in rs])
    worst = rs[int(np.argmin(sd))]; ent = el[sd < -0.5]; cl2 = el[sd < 2.0]
    regs = {}
    for r in rs:
        for k_, v in r["inside_regions"].items(): regs[k_] = regs.get(k_, 0) + v
    bins = {}
    for a, b in ((0, 30), (30, 50), (50, 70), (70, 90), (90, 110), (110, 130), (130, 151)):
        m = (el >= a) & (el < b)
        if m.any(): bins[f"{a}-{b}"] = dict(min_sd=round(float(sd[m].min()), 1), frames=int(m.sum()), inside_frames=int((sd[m] < -0.5).sum()),
                                            region_of_deepest=rs[int(np.flatnonzero(m)[np.argmin(sd[m])])]["region"])
    per_part = {}
    for r in rs:
        pp = per_part.setdefault(r["part"], dict(min_sd=99.0))
        if r["sd_min"] < pp["min_sd"]: pp.update(min_sd=round(r["sd_min"], 1), region=r["region"], clip=r["clip"], want=r["want"], at_mm=r["at_mm"])
    BR[mode] = dict(frames=len(rs) // max(1, len(BASE)), min_sd=round(float(sd.min()), 1), worst=dict((k_, worst[k_]) for k_ in ("part", "clip", "i", "want", "region", "at_mm", "lift", "inside_share")),
                    first_elev_inside_0p5=None if not len(ent) else round(float(ent.min()), 1), first_elev_within_2mm=None if not len(cl2) else round(float(cl2.min()), 1),
                    inside_vertex_regions=regs, by_elevation=bins, per_part=per_part)
out = dict(step=STEP, frames=len(idx), near_filter_mm=NEAR, parts=dict(sorted(summ.items(), key=lambda kv: kv[1]["min_sd_mm"])), base_mount=BR,
           seconds=round(time.time() - t0))
RC.jdump(out, "pressure.json"); json.dump(base_rec, open(os.path.join(RC.OUT, "pressure_base_frames.json"), "w"))
print("->", RC.OUT + "/pressure.json", f"{time.time() - t0:.0f}s")
for k_, v in list(out["parts"].items())[:20]:
    print(f"{v['min_sd_mm']:7.2f} mm {v['owner'][:8]:8s} {k_[:60]:60s} within2: {v['frames_within_2mm']:3d} fr, inside: {v['frames_inside_0p5']:3d} fr  worst {v['worst']}  regs {v['regions_within_2mm']}")
for mode, v in BR.items(): print(mode, json.dumps(v)[:1500])
