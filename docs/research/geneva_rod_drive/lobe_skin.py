"""Lobe-ring skin check for the gen-5 geneva rod CAD (docs/research/geneva-rod-gen5_fix.md): the D9-01 lobe ring (group l2)
and the follower roller (group dk) posed by the judged frames of user_geneva_rod/clips.json against the judges' skin
(pipeline/avg body_pose, signed: inside = negative; igl winding number), for the as-built ring and for candidate fixes
built with the CAD builder's OWN lobe_ring() (pipeline/conformal/param_cad/user_style_geneva.py) on a re-solved drive
(docs/research/geneva_rod_drive/drive.py run()).

    nice python3 docs/research/geneva_rod_drive/lobe_skin.py probe            # where the as-built ring enters the skin
    nice python3 docs/research/geneva_rod_drive/lobe_skin.py candidates       # min signed skin distance per candidate
"""
import json, math, os, sys
MODE = sys.argv[1] if len(sys.argv) > 1 else "probe"; sys.argv = sys.argv[:1]
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
for p in ("pipeline/full-exo", "pipeline/avg", "pipeline/conformal/param_cad"): sys.path.insert(0, os.path.join(REPO, p))
import numpy as np, trimesh, igl, body_pose as BP
import user_style_geneva as USG                                                              # the builder (read-only use)
DV = USG.DV; DD = os.path.join(REPO, "pipeline/full-exo/designs/user_geneva_rod")
C = json.load(open(os.path.join(DD, "clips.json"))); BF = np.ascontiguousarray(BP.F, np.int64)

def dv_variant(r_h=2.493, a_f=9.0, a_c=9.0, rr=3.0, r_base=10.1):
    """the builder's drive_solution() without the fit check (the fit is asserted equal in the build; geo.npz is that fit)"""
    r = DV.run(r_h=r_h, a_f=a_f, a_c=a_c, rr=rr, r_base=r_base, side=+1); arr = r.pop("_arrays")
    u2 = DV.u2; bx = USG.unit(DV.axis_off); by = np.cross(u2, bx)
    return dict(rep=r, arr=arr, u2=u2, uK=DV.uK, bx=bx, by=by, PT=DV.axis_off + DV.hT * u2, PL=DV.axis_off + DV.hL * u2,
                A0=arr["As"][0], B0=arr["Bs"][0], C0=arr["Cs"][0], axis=DV.axis_off, f2=DV.f2, fK=DV.fK)

def samples(solid, n=40000, seed=1):
    m = USG.tess_safe(solid); pts = np.concatenate([trimesh.sample.sample_surface(m, n, seed=seed)[0], m.vertices]); return pts

def polar(dv, P):
    u2, bx, by = dv["u2"], dv["bx"], dv["by"]; h = P @ u2 - dv["f2"]; Q = P - np.outer(P @ u2, u2)
    return h, np.linalg.norm(Q, axis=1), np.degrees(np.arctan2(Q @ by, Q @ bx))

def frames(every=1, clips=None):
    for cl in C["clips"]:
        if clips and cl["name"] not in clips: continue
        for k, f in enumerate(cl["frames"]):
            if k % every == 0: yield cl["name"], k, f

def sd_frame(f, pts_by_group):
    V = np.ascontiguousarray(BP.posed(dict(zip(["plane", "elev", "axial", "flex", "pron"], f["p"]))), float); out = {}
    for g, P in pts_by_group.items():
        Q = np.ascontiguousarray(P @ np.array(f["G"][g]).reshape(3, 3).T + np.array(f.get("T", {}).get(g, [0, 0, 0])), float)
        d = np.sqrt(igl.point_mesh_squared_distance(Q, V, BF)[0]); w = igl.fast_winding_number(V, BF, Q) > 0.5; out[g] = np.where(w, -d, d)
    return out

def lobe_variant(dv, rr=3.0, dz=0.0):
    """the builder's lobe ring on drive dv, its band moved dz along u2 (the roller plane moves with it: same law)"""
    USG.RR = rr; USG.LOBE_Z = (6.15 + dz, 8.75 + dz)
    try: ring, info = USG.lobe_ring(dv)
    finally: USG.RR = 3.0; USG.LOBE_Z = (6.15, 8.75)
    return ring, info

CANDS = [("as built (exo.glb)", None), ("rebuilt baseline V0", dict()),
         ("(ii) band up 0.5", dict(dz=0.5)), ("(ii) band up 1.0", dict(dz=1.0)), ("(ii) band up 1.5", dict(dz=1.5)), ("(ii) band up 2.0", dict(dz=2.0)),
         ("(iii) follower arm 8.0", dict(a_f=8.0)), ("(iii) follower arm 7.5", dict(a_f=7.5)), ("(iii) follower arm 7.0", dict(a_f=7.0)),
         ("(iii) crank arm 10", dict(a_c=10.0)), ("(iii) follower 7.0 + crank 10", dict(a_f=7.0, a_c=10.0)), ("(iii) roller O5 (MR52ZZ 2x5x2.5)", dict(rr=2.5))]

if __name__ == "__main__":
    src = trimesh.load(os.path.join(DD, "exo.glb")); built = {}
    for node in src.graph.nodes_geometry:
        g, n = node.split("|")[:2]
        if n.startswith("D9-01") or "MR63ZZ" in n:
            T_, gn = src.graph[node]; m = src.geometry[gn].copy(); m.apply_transform(T_); built[g] = np.concatenate([trimesh.sample.sample_surface(m, 40000, seed=1)[0], m.vertices])
    dv0 = dv_variant()
    if MODE == "probe":
        worst = []
        for name, k, f in frames(1, ["Raise overhead"]):
            sd = sd_frame(f, {"l2": built["l2"]}); i = int(np.argmin(sd["l2"])); worst.append((float(sd["l2"][i]), k))
        worst.sort(); print("worst frames (Raise overhead):", [(round(a, 3), b) for a, b in worst[:6]], flush=True)
        f = C["clips"][[c["name"] for c in C["clips"]].index("Raise overhead")]["frames"][worst[0][1]]
        sd = sd_frame(f, {"l2": built["l2"]})["l2"]; h, r, az = polar(dv0, built["l2"]); o = np.argsort(sd)[:40]
        print("as-built ring at frame", worst[0][1], ": points within 0.3 mm of the skin or inside (h over F2, r, az):")
        for i in o[:15]: print(f"  sd {sd[i]:7.3f}  h {h[i]:5.2f}  r {r[i]:6.3f}  az {az[i]:7.2f}")
        sel = sd < 0.3; print("  share of ring samples with sd < 0.3:", round(float(sel.mean()), 4), " h range", np.round([h[sel].min(), h[sel].max()], 2) if sel.any() else None,
                              " r range", np.round([r[sel].min(), r[sel].max()], 2) if sel.any() else None, " az range", np.round([az[sel].min(), az[sel].max()], 1) if sel.any() else None)
        lo = json.load(open(os.path.join(DD, "build.json")))["lobe"]; print("  build: profile az", lo["profile_az_deg"], "flank end az", lo["flank_end_az_deg"])

    if MODE.startswith("candidates"):
        part = int(sys.argv_part) if hasattr(sys, "argv_part") else None
        out = {}; todo = CANDS if ":" not in MODE else [c for i, c in enumerate(CANDS) if i % int(MODE.split(":")[2]) == int(MODE.split(":")[1])]
        fl = list(frames(1, ["Raise overhead"])) + list(frames(4, ["Reach a high shelf", "Comb hair"])) + list(frames(8, ["Drink from a cup", "Wash opposite shoulder", "Reach back pocket", "Wave", "Walking arm swing"]))
        for label, kw in todo:
            if kw is None: P = built["l2"][::3]; info = {}; dvv = dv0; rep = {}
            else:
                kw = dict(kw); dz = kw.pop("dz", 0.0); rr = kw.get("rr", 3.0); dvv = dv_variant(**kw); ring, info = lobe_variant(dvv, rr=rr, dz=dz); P = samples(ring, 12000)
                rep = {k: dvv["rep"].get(k) for k in ("lobe_r_onset", "lobe_r_end", "pa_deg", "lift_mm", "rocker_turn_deg", "rod_cap_clear_min")}
            h, r, az = polar(dvv, P); keep = r > 10.05; P, h, r, az = P[keep], h[keep], r[keep], az[keep]   # r <= 10.05: inside the O20 skirt's own envelope
            worst = (9.0, None); n2 = 0; flank = dwell = 9.0
            for name, k, f in fl:
                sd = sd_frame(f, {"l2": P})["l2"]; i = int(np.argmin(sd))
                if sd[i] < worst[0]: worst = (float(sd[i]), f"{name} {k}", round(float(h[i]), 2), round(float(r[i]), 2), round(float(az[i]), 1))
                n2 += int(sd[i] < 2.0)
                if name == "Raise overhead":
                    pe = info.get("profile_az_deg", [0, 60.73])[1]
                    mf = (az > pe + 1.0) & (r > 10.2); md = r <= 10.2   # flank past the profile end / dwell circle
                    if mf.any(): flank = min(flank, float(sd[mf].min()))
                    if md.any(): dwell = min(dwell, float(sd[md].min()))
            out[label] = dict(min_sd_mm=round(worst[0], 3), where=worst[1:], frames_under_2mm=n2, frames=len(fl), raise_overhead_flank_min_mm=round(flank, 3),
                              raise_overhead_dwell_min_mm=round(dwell, 3), lobe=dict(profile_r=info.get("profile_r"), profile_az=info.get("profile_az_deg"),
                              past_skirt=info.get("past_O20_skirt_max_mm"), flank_to_roller_at_stopB=info.get("flank_to_roller_at_stopB_mm"), band=info.get("band_mm")), drive=rep)
            print(label, json.dumps(out[label]), flush=True)
        tag = MODE.replace(":", "_"); json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"lobe_skin_{tag}.json"), "w"), indent=1)
