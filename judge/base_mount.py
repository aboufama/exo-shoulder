"""JUDGE R10. Girdle mount (design.json base.mount = "girdle": the base rides the scapula on the user's scapula handler,
the decided architecture): the GH-centre misalignment from the handler slipping over the bone, from the literature
skin-slip model in judge/base_slip.py (docs/research/base_slip_model.md) - the central law's worst frame is R10's
number, low / high laws bracket it. Thorax mount (below): the base bolts to a thorax back plate. How far is the arm's GH centre from where the chain carries it, and
does the base part stay out of the body, when the base is THORAX-fixed (whatever frame the design pipeline assumed)?

Girdle motion: the WORST over three laws (girdle.lift_laws): the body rig's (avg/body_pose.py segs()), the published
bone-pin chain (docs/research/gh_translation_literature.md) and the OpenSim Seth 2016 model driven by published angles
(pipeline/girdle/opensim_seth, scaled to the rig) - until the user's OpenCap trajectories exist (data/raw). The base-part
contact check uses the rig's skin (the only posed skin there is). Frames: every step-th frame of
every clip, the person's motion ("want" poses: the girdle moves whether or not the exo follows).
Chain model from design.json "base" (default for designs without one: a spherical chain centred on the GH centre at
rest, i.e. every axis through the GH centre):
    {"mount": "thorax", "chain": "spherical", "centre_mm": [x, y, z]}
    {"mount": "thorax", "chain": "offset3", "prm": {b, a1, a2, branch, w}, "axis_points_mm": [o1, o2, o3]}  (girdle.Chain3)
    + optional "slider": [ex, ey, ez]: one torque-free passive slider (the user's exception): misalignment along it is free
    {"mount": "girdle", "chain": "spherical", "stage": {"kind": "follower", "gh_minus_p_mm": [x, y, z], "f_ang": 1, "f_slip": 1}}
      a 3-axis torque-free stage between the handler and J1 set by a bony follower at P (ISB scapula frame, GH - P;
      lateral acromion right above GH: [0, -32, 0]; optional "normal": [nx, ny, nz] -> a 2-axis stage across it, the
      handler holding the centre along it); f_ang / f_slip < 1 only with the user's measured calibrated law
      (judge/base_stage.py, docs/FINDINGS.md "R10 on the scapula handler")
    python3 judge/base_mount.py <design dir|id> [--step 3]  -> <design>/judge/base_mount.json"""
import argparse, json, os, sys
import numpy as np
from common import design_dir, load_parts, frames, PIPE
from sdist import max_depth
sys.path.insert(0, os.path.join(PIPE, "girdle")); import girdle as GD
from girdle import BP
ap = argparse.ArgumentParser(); ap.add_argument("design"); ap.add_argument("--step", type=int, default=3)
a = ap.parse_args(); dd = design_dir(a.design)
D = json.load(open(os.path.join(dd, "design.json"))); base = D.get("base", {"mount": "thorax", "chain": "spherical", "centre_mm": [0, 0, 0]})
FR = list(frames(dd, a.step)); W = np.array([fr["want"] for _, _, fr in FR], float); M = GD.Motion(W)
if base.get("mount") == "girdle":                                           # the base rides the scapula on the user's handler: skin slip over the bone
    import base_slip as BS                                                   # literature model (docs/research/base_slip_model.md)
    names = [f[0] for f in FR]
    st = base.get("stage")
    if st and st.get("kind") == "follower" and base.get("chain", "spherical") == "spherical":
        import base_stage as BST
        P = BS.lever()[0] - np.asarray(st["gh_minus_p_mm"], float); fa, fs = float(st.get("f_ang", 1.0)), float(st.get("f_slip", 1.0))
        mis = {law: BST.follower(W, P, law, fa, fs, normal=st.get("normal")) for law in ("central", "low")}; m = mis["central"]; ev = W[:, 1]
        out = dict(base=base, model="base_stage.py follower: seen = (R_err - I)(GH - P) + d_f, handler angles and slip from base_slip.py (central law unchanged), x f_ang / f_slip",
                   law="central", frames_checked=len(FR), step=a.step, max_mm=round(float(m.max()), 2), p95_mm=round(float(np.percentile(m, 95)), 2), share_over_4mm=round(float((m > 4).mean()), 3),
                   per_law_max_mm={l: round(float(v.max()), 2) for l, v in mis.items()} | {"high": None}, central_max_by_elevation_mm={f"<= {hi}": (round(float(m[ev <= hi].max()), 2) if (ev <= hi).any() else None) for hi in (60, 90, 100, 120, 150, 180)},
                   worst=[names[int(np.argmax(m))], FR[int(np.argmax(m))][1], [round(v) for v in W[int(np.argmax(m))][:3]]],
                   per_clip={n: round(float(m[[k for k, q in enumerate(names) if q == n]].max()), 2) for n in dict.fromkeys(names)},
                   note="girdle mount + follower stage (no active DOF): the handler's IR/ER swing no longer moves the centre; f < 1 claims a per-user calibrated law")
        print(f"base mount (girdle + follower stage, f_ang {fa}, f_slip {fs}): GH misalignment max {out['max_mm']} mm (low {out['per_law_max_mm']['low']}), p95 {out['p95_mm']} mm, {100 * out['share_over_4mm']:.0f}% of frames > 4 mm")
        os.makedirs(os.path.join(dd, "judge"), exist_ok=True); json.dump(out, open(os.path.join(dd, "judge", "base_mount.json"), "w"), indent=1); sys.exit(0)
    if base.get("chain", "spherical") != "spherical" or base.get("slider"):
        out = dict(base=base, max_mm=None, note="girdle mount: the skin-slip model (judge/base_slip.py) handles a spherical chain centred on the GH centre without a slider; this design needs the lever / slider mapping first")
        print("base mount: girdle mount with an offset chain or a slider -> R10 NOT RUN (base_slip.py handles a spherical chain only)")
    else:
        r, sc = BS.lever(); c0 = np.asarray(base.get("centre_mm", [0, 0, 0]), float)
        if np.linalg.norm(c0) > 1e-6: print(f"  note: chain centre {c0} mm from GH at rest; the slip model uses the lever to GH (the centre offset is a fixed error R1 already sees)")
        mis = BS.misalignment(W[:, :2], r); law = "central"; m = mis[law]
        alt = {an: float(BS.misalignment(W[:, :2], BS.lever(an)[0], laws=(law,))[law].max()) for an in ("aa", "ac")}
        ev = W[:, 1]
        out = dict(base=base, model="base_slip.py: handler = acromion marker cluster analogue; per-axis ISB scapula error angles vs humeral elevation/plane from Karduna 2001, "
                   "van Andel 2009, Lempereur 2014 + 4.2 mm translation slip (McQuade & Smidt 1998); lever GH - flat of the acromion from the OpenSim Seth 2016 scapula, scaled to the rig",
                   law=law, frames_checked=len(FR), step=a.step, lever_mm=[round(float(x), 1) for x in r], lever_scale=round(float(sc), 3),
                   max_mm=round(float(m.max()), 2), p95_mm=round(float(np.percentile(m, 95)), 2), share_over_4mm=round(float((m > 4).mean()), 3),
                   per_law_max_mm={l: round(float(v.max()), 2) for l, v in mis.items()}, per_law_share_over_4mm={l: round(float((v > 4).mean()), 3) for l, v in mis.items()},
                   central_max_by_elevation_mm={f"<= {hi}": (round(float(m[ev <= hi].max()), 2) if (ev <= hi).any() else None) for hi in (60, 90, 100, 120, 150, 180)},
                   central_max_anchor_sensitivity_mm=dict(mid=round(float(m.max()), 2), aa=round(alt["aa"], 2), ac=round(alt["ac"], 2)),
                   worst=[names[int(np.argmax(m))], FR[int(np.argmax(m))][1], [round(v) for v in W[int(np.argmax(m))][:3]]],
                   per_clip={n: round(float(m[[k for k, q in enumerate(names) if q == n]].max()), 2) for n in dict.fromkeys(names)},
                   note="design-independent for a spherical chain on a girdle mount: only the handler (grip, footprint), the motions and a passive slider can change it")
        print(f"base mount (girdle, skin slip over the scapula, central law): GH misalignment max {out['max_mm']} mm (low {out['per_law_max_mm']['low']}, high {out['per_law_max_mm']['high']}), "
              f"p95 {out['p95_mm']} mm, {100 * out['share_over_4mm']:.0f}% of frames > 4 mm; by elevation {out['central_max_by_elevation_mm']}")
    os.makedirs(os.path.join(dd, "judge"), exist_ok=True); json.dump(out, open(os.path.join(dd, "judge", "base_mount.json"), "w"), indent=1); sys.exit(0)
LAWS = GD.lift_laws(W, M); Pe = np.eye(3)
if base.get("slider"): e = np.asarray(base["slider"], float); e /= np.linalg.norm(e); Pe = np.eye(3) - np.outer(e, e)
if base.get("chain") == "offset3":
    pr = dict(base["prm"]); pr["b"] = tuple(pr["b"]); pr["w"] = None if pr.get("w") is None else tuple(pr["w"])
    ch = GD.Chain3(pr); A, mg, ok, *_ = ch.kin(M); x = np.concatenate([np.asarray(o, float) for o in base["axis_points_mm"]])
    carried = np.einsum("tij,j->ti", A, x); extra = dict(singular_margin_deg_min=round(float(mg.min()), 1), closes=round(float(ok.mean()), 3))
else:
    carried = np.broadcast_to(np.asarray(base.get("centre_mm", [0, 0, 0]), float), M.lift.shape); extra = {}
per_law = {l: np.linalg.norm((carried - y) @ Pe.T, axis=1) for l, y in LAWS.items()}
mis = np.max(np.stack(list(per_law.values())), 0)                                        # worst law, per frame
# the base part on a thorax-fixed plate vs the exact posed skin (its pose at rest, carried by the trunk)
parts = [(n, P) for g, n, P, _ in load_parts(dd) if g == "base"]; depth = 0.0; worst = None
if parts:
    C0 = json.load(open(os.path.join(dd, "clips.json")))["clips"][0]["frames"][0]
    G0 = BP.scap(C0["p"][1]).T @ np.array(C0["G"]["base"]).reshape(3, 3)          # base group frame -> rest (thorax) frame
    B = np.concatenate([P[:: max(1, len(P) // 3000)] for _, P in parts]) @ G0.T
    for (clip, fi, fr), lf in zip(FR[::2], M.lift[::2]):
        V = BP.posed(dict(zip(["plane", "elev", "axial", "flex", "pron"], fr["want"]))); dep = max_depth(B - lf, V, BP.F, h=2.0, g=1.0)[0]
        if dep > depth: depth = dep; worst = [clip, fi, [round(v) for v in fr["want"][:3]]]
names = [f[0] for f in FR]
out = dict(girdle_law="worst of rig / literature / OpenSim Seth (girdle.lift_laws) - not yet the user's OpenCap", base=base, frames_checked=len(FR), step=a.step,
           per_law_max_mm={l: round(float(v.max()), 2) for l, v in per_law.items()},
           max_mm=round(float(mis.max()), 2), p95_mm=round(float(np.percentile(mis, 95)), 2), share_over_4mm=round(float((mis > 4).mean()), 3),
           per_clip={n: round(float(mis[[k for k, m in enumerate(names) if m == n]].max()), 2) for n in dict.fromkeys(names)},
           base_part_enters_body_mm=round(depth, 2), base_part_worst=worst, **extra)
os.makedirs(os.path.join(dd, "judge"), exist_ok=True); json.dump(out, open(os.path.join(dd, "judge", "base_mount.json"), "w"), indent=1)
print(f"base mount (thorax-fixed, {base.get('chain', 'spherical')} chain{', + slider' if base.get('slider') else ''}): GH misalignment worst-law max {out['max_mm']} mm {out['per_law_max_mm']}, p95 {out['p95_mm']} mm, "
      f"{100 * out['share_over_4mm']:.0f}% of frames > 4 mm; base part enters the body by {out['base_part_enters_body_mm']} mm (worst {worst})")
