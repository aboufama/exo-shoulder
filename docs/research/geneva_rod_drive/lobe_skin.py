"""Lobe-ring skin check for the gen-5 geneva rod CAD (docs/research/geneva-rod-gen5_fix.md): the D9-01 lobe ring (group l2)
and the follower roller (group dk) posed by the judged frames of user_geneva_rod/clips.json against the judges' skin
(pipeline/avg body_pose, signed: inside = negative; igl winding number), for the as-built ring and for candidate fixes
built with the CAD builder's OWN lobe_ring() (pipeline/conformal/param_cad/user_style_geneva.py) on a re-solved drive
(docs/research/geneva_rod_drive/drive.py run()).

    nice python3 docs/research/geneva_rod_drive/lobe_skin.py probe            # where the as-built ring enters the skin
    nice python3 docs/research/geneva_rod_drive/lobe_skin.py candidates       # min signed skin distance per candidate
    nice python3 docs/research/geneva_rod_drive/lobe_skin.py real [all]       # gen-5 fix, round 3: every candidate on the REAL-SIZE
        drive (igus igubal 6 mm eyes + the 3.8 mm horn hub raise the horn rod end by RISE 3.6 mm, as user_style_geneva_fix.py
        builds it), the posed skin cached per frame; "all" = every frame of every clip (1337) for the short list + the as-built
        user_geneva_rod_v2 ring. Writes lobe_skin_real[_all].json.
"""
import json, math, os, sys
MODE = sys.argv[1] if len(sys.argv) > 1 else "probe"; sys.argv_extra = sys.argv[2:]; sys.argv = sys.argv[:1]
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
for p in ("pipeline/full-exo", "pipeline/avg", "pipeline/conformal/param_cad"): sys.path.insert(0, os.path.join(REPO, p))
import numpy as np, trimesh, igl, body_pose as BP
import user_style_geneva as USG                                                              # the builder (read-only use)
DV = USG.DV; DD = os.path.join(REPO, "pipeline/full-exo/designs/user_geneva_rod")
C = json.load(open(os.path.join(DD, "clips.json"))); BF = np.ascontiguousarray(BP.F, np.int64)

def dv_variant(r_h=2.493, a_f=9.0, a_c=9.0, rr=3.0, r_base=10.1, side=+1, dk_end=None):
    """the builder's drive_solution() without the fit check (the fit is asserted equal in the build; geo.npz is that fit).
    dk_end: stop B moved earlier - the law (and so the lobe profile) ends at |dK| = dk_end deg (the arrays' prefix)"""
    r = DV.run(r_h=r_h, a_f=a_f, a_c=a_c, rr=rr, r_base=r_base, side=side)
    if "_arrays" not in r: raise ValueError(f"drive.py finds no push/outward branch for {dict(r_h=r_h, a_f=a_f, a_c=a_c, rr=rr, r_base=r_base, side=side)}")
    arr = r.pop("_arrays")
    if dk_end is not None:
        n = int(np.searchsorted(DV.kK * np.degrees(arr["ts"]), dk_end + 1e-9)); arr = {k: (v[:n] if hasattr(v, "__len__") and len(v) == len(DV.ts) else v) for k, v in arr.items()}
        r = dict(r, lobe_r_end=round(float(arr["rprof"][-1]), 2), dK_end=round(float(DV.kK * np.degrees(arr["ts"][-1])), 2), pa_deg=[round(float(arr["pa"].min()), 1), round(float(arr["pa"].max()), 1)])
    u2 = DV.u2; bx = USG.unit(DV.axis_off); by = np.cross(u2, bx)       # (a mirrored follower, side -1, still advances the profile the same way round u2: q2 sets it)
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

def lobe_variant(dv, rr=3.0, dz=0.0, band=None):
    """the builder's lobe ring on drive dv, its band moved dz along u2 (the roller plane moves with it: same law); band = (z0, z1)
    replaces the band (a thinner band). A mirrored drive (side -1) flips lobe_ring's sketch normal to -u2, so its band is given
    from the top: the sketch plane sits at the band top and extrudes down over the same heights"""
    z0, z1 = band if band else (6.15 + dz, 8.75 + dz)
    flip = float(np.cross(dv["bx"], dv["by"]) @ dv["u2"]) < 0
    USG.RR = rr; USG.LOBE_Z = (z1, z1 + (z1 - z0)) if flip else (z0, z1)
    try: ring, info = USG.lobe_ring(dv)
    finally: USG.RR = 3.0; USG.LOBE_Z = (6.15, 8.75)
    return ring, info

CANDS = [("as built (exo.glb)", None), ("rebuilt baseline V0", dict()),
         ("(ii) band up 0.5", dict(dz=0.5)), ("(ii) band up 1.0", dict(dz=1.0)), ("(ii) band up 1.5", dict(dz=1.5)), ("(ii) band up 2.0", dict(dz=2.0)),
         ("(iii) follower arm 8.0", dict(a_f=8.0)), ("(iii) follower arm 7.5", dict(a_f=7.5)), ("(iii) follower arm 7.0", dict(a_f=7.0)),
         ("(iii) crank arm 10", dict(a_c=10.0)), ("(iii) follower 7.0 + crank 10", dict(a_f=7.0, a_c=10.0)), ("(iii) roller O5 (MR52ZZ 2x5x2.5)", dict(rr=2.5)),
         # round 2 (the follower arm stays 9.0: a shorter one puts the O6 roller into the O10 bell-crank tube, a_f >= 5 + 3 + 0.3)
         ("(iii) crank 12, horn r 2.0", dict(a_c=12.0, r_h=2.0)), ("(iii) crank 13, horn r 2.0", dict(a_c=13.0, r_h=2.0)),
         ("(iii) crank 14, horn r 1.8", dict(a_c=14.0, r_h=1.8)), ("(iii) crank 14, horn r 2.493", dict(a_c=14.0))]

RISE = (6.0 - 4.0) / 2 + (3.8 - 1.2)           # user_style_geneva_fix.py: rod-end centre rise at the horn (igubal 6 mm eyes, 3.8 mm horn hub)
REAL = [("R0 real parts, no lobe fix (a_c 9, r_h 2.493)", dict()),
        ("(i) stop B at dK 50", dict(dk_end=50.0)), ("(i) stop B at dK 47", dict(dk_end=47.0)), ("(i) stop B at dK 44", dict(dk_end=44.0)),
        ("(i) stop B at dK 40", dict(dk_end=40.0)), ("(i) stop B at dK 35", dict(dk_end=35.0)),
        ("(iv) radial offset: dwell r 9.6", dict(r_base=9.6)), ("(iv) radial offset: dwell r 9.1", dict(r_base=9.1)),
        ("(iv) phase: mirrored follower (side -1)", dict(side=-1)),
        ("(v) thinner band 6.65-8.75 (2.1)", dict(band=(6.65, 8.75))), ("(v) thinner band 7.15-8.75 (1.6)", dict(band=(7.15, 8.75))),
        ("(iii) crank 12, horn r 2.0", dict(a_c=12.0, r_h=2.0)), ("(iii) crank 13, horn r 2.0", dict(a_c=13.0, r_h=2.0)),
        ("(iii) crank 14, horn r 2.493", dict(a_c=14.0)), ("(iii) crank 14, horn r 1.8", dict(a_c=14.0, r_h=1.8))]


def real_mode(every_frame):
    import time
    DV.hB = DV.hB + RISE                                                        # the real-size rod end (the fix builder does the same)
    t0 = time.time(); cands = []
    short = os.environ.get("LOBE_SHORT", "")
    todo = [c for c in REAL if not every_frame or any(k in c[0] for k in short.split(";") if k)] if every_frame else REAL
    for label, kw in todo:
        kw = dict(kw); dz = kw.pop("dz", 0.0); band = kw.pop("band", None); rr = kw.get("rr", 3.0)
        try: dvv = dv_variant(**kw); ring, info = lobe_variant(dvv, rr=rr, dz=dz, band=band); P = samples(ring, 12000)
        except Exception as e: print(f"FAILED {label}: {e!r}", flush=True); continue
        h, r, az = polar(dvv, P); keep = r > 10.05
        rep = {k: dvv["rep"].get(k) for k in ("lobe_r_onset", "lobe_r_end", "dK_end", "pa_deg", "lift_mm", "rocker_turn_deg", "rod_cap_clear_min", "horn_arm_eff", "dK_per_0.05mm_rod_deg", "dK_per_0.05mm_lobe_deg")}
        cands.append(dict(label=label, P=P[keep], h=h[keep], r=r[keep], az=az[keep], info=info, rep=rep, worst=(9.0,), n2=0, flank=9.0, dwell=9.0))
        print(f"built {label}: profile r {info.get('profile_r')} az {info.get('profile_az_deg')} valid {info.get('valid')} ({time.time() - t0:.0f} s)", flush=True)
    if every_frame:                                                             # + the as-built v2 ring (exo.glb)
        dv2 = os.path.join(REPO, "pipeline/full-exo/designs/user_geneva_rod_v2"); src = trimesh.load(os.path.join(dv2, "exo.glb"))
        for node in src.graph.nodes_geometry:
            g, n = node.split("|")[:2]
            if g == "l2" and n.startswith("D9-01"):
                T_, gn = src.graph[node]; m = src.geometry[gn].copy(); m.apply_transform(T_); P = np.concatenate([trimesh.sample.sample_surface(m, 40000, seed=1)[0], m.vertices])
                dvv = dv_variant(a_c=14.0, r_h=1.8); h, r, az = polar(dvv, P); keep = r > 10.05
                cands.append(dict(label="user_geneva_rod_v2 as built (exo.glb)", P=P[keep], h=h[keep], r=r[keep], az=az[keep], info={}, rep={}, worst=(9.0,), n2=0, flank=9.0, dwell=9.0))
    fl = list(frames(1)) if every_frame else (list(frames(1, ["Raise overhead"])) + list(frames(4, ["Reach a high shelf", "Comb hair"])) +
                                              list(frames(8, ["Drink from a cup", "Wash opposite shoulder", "Reach back pocket", "Wave", "Walking arm swing"])))
    for j, (name, k, f) in enumerate(fl):
        V = np.ascontiguousarray(BP.posed(dict(zip(["plane", "elev", "axial", "flex", "pron"], f["p"]))), float)
        G = np.array(f["G"]["l2"]).reshape(3, 3); T = np.array(f.get("T", {}).get("l2", [0, 0, 0]))
        for c in cands:
            Q = np.ascontiguousarray(c["P"] @ G.T + T, float)
            d = np.sqrt(igl.point_mesh_squared_distance(Q, V, BF)[0]); w = igl.fast_winding_number(V, BF, Q) > 0.5; sd = np.where(w, -d, d); i = int(np.argmin(sd))
            if sd[i] < c["worst"][0]: c["worst"] = (float(sd[i]), f"{name} {k}", round(float(c["h"][i]), 2), round(float(c["r"][i]), 2), round(float(c["az"][i]), 1))
            c["n2"] += int(sd[i] < 2.0)
            if name == "Raise overhead":
                pe = c["info"].get("profile_az_deg", [0, 60.73])[1]; mf = (c["az"] > pe + 1.0) & (c["r"] > 10.2); md = c["r"] <= 10.2
                if mf.any(): c["flank"] = min(c["flank"], float(sd[mf].min()))
                if md.any(): c["dwell"] = min(c["dwell"], float(sd[md].min()))
        if j % 50 == 0: print(f"  frame {j}/{len(fl)} ({time.time() - t0:.0f} s)", flush=True)
    out = {}
    for c in cands:
        lb = c["info"]
        out[c["label"]] = dict(min_sd_mm=round(c["worst"][0], 3), where=list(c["worst"][1:]), frames_under_2mm=c["n2"], frames=len(fl), pass_0p3=c["worst"][0] >= 0.3,
                               raise_overhead_flank_min_mm=round(c["flank"], 3), raise_overhead_dwell_min_mm=round(c["dwell"], 3),
                               lobe=dict(profile_r=lb.get("profile_r"), profile_az=lb.get("profile_az_deg"), past_skirt=lb.get("past_O20_skirt_max_mm"),
                                         flank_to_roller_at_stopB=lb.get("flank_to_roller_at_stopB_mm"), band=lb.get("band_mm"), valid=lb.get("valid")), drive=c["rep"])
        print(c["label"], json.dumps(out[c["label"]]), flush=True)
    json.dump(dict(rise_mm=RISE, seconds=round(time.time() - t0), cands=out), open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lobe_skin_real" + ("_all" if every_frame else "") + ".json"), "w"), indent=1)


if __name__ == "__main__" and MODE == "real":
    real_mode(len(sys.argv_extra) > 0 and sys.argv_extra[0] == "all"); sys.exit(0)

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
        out = {}; todo = CANDS if ":" not in MODE else [c for i, c in enumerate(CANDS) if i % int(MODE.split(":")[2]) == int(MODE.split(":")[1]) and (len(MODE.split(":")) < 4 or i >= int(MODE.split(":")[3]))]
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
