"""Proximity levers on one design, measured with the band evaluator on CPU (cached clip-frame skin maps .cache/maps_s1.pt,
band_poses.b64: the 8 clips, no workspace envelope - so the shape is fitted to the fit clips only; compare variants with
each other, not with GPU wsf results). One change at a time from the design's own geometry; per variant at G = 14 and
10 mm: score, follow, in-band (the evaluator's own numbers), and per sample class (ribbon of each link, the lower
hub of each joint, BOTTOM's hub at JN, the arm-end neck) the area share, in-band achieved, in-band ceiling (that class
at its lowest legal underside on this path: inband_ceiling.py's bound), the lift over it (shape slack) and the radial
skin motion under it (max - min over the followed frames of the lower bound, median over the class).

    THREADS=2 python3 proximity_variants.py <cad input json | designs json> <geo json> [set] [design index]
    sets: hub (hub / stack / relief / margin), link (hw / ramp), order, all
-> pipeline/conformal/analysis/proximity_variants_<tag>.json"""
import json, os, sys, time, copy
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "gpu"))
os.environ["BAND_STASH"] = "1"
import band_impl as BI, torch
torch.set_num_threads(int(os.environ.get("THREADS", 2)))
SRC = json.load(open(sys.argv[1])); GEO = json.load(open(sys.argv[2])); SET = sys.argv[3] if len(sys.argv) > 3 else "all"
k_ = int(sys.argv[4]) if len(sys.argv) > 4 else 0
d_src = SRC["results"][k_] if "results" in SRC else SRC["designs"][k_]
D0 = {k: d_src[k] for k in ("n", "az", "el", "a", "w", "branch", "order", "cuff", "hm", "_src") if k in d_src}
POSES = open(os.path.join(HERE, "..", os.environ.get("POSES_FILE", "band_poses.b64"))).read()
MAPS = os.path.join(HERE, "..", "..", "..", ".cache", "maps_s1.pt")
GLOB = ("HUB_R", "HW", "T_LINK", "STACK", "T_W", "T_BOT", "T_LO", "HUB_UP", "CAP_UP", "RAIL_D")
BASE = {g: getattr(BI, g) for g in GLOB}

def analyse(B, d):
    t0 = time.time(); r = B.evaluate(dict(d), detail=False)
    if r.get("err"): return dict(err=r["err"])
    S = B._stash; t = torch; ar = t.arange(S["LO"].shape[0])
    fe = S["feas"]; LO = S["LO"][ar, S["cfg"]][fe]; CAP = S["CAP"][ar, S["cfg"]][fe]; WT = B.WT[fe]
    h = t.where(S["is_bot"], S["bot_under"], S["h"]); m = S["scored"] & (S["wS"] > 0); w = S["wS"]
    hmin = LO.max(0).values
    def rng_(L):                                                                         # radial motion of the skin's lower bound (frames with skin there)
        sk = L > 1.0; return t.where(sk.any(0), L.max(0).values - t.where(sk, L, t.full_like(L, 1e4)).min(0).values, t.zeros_like(L[0]))
    lo_rng = rng_(LO)
    kind, mem = S["kindA"], S["memA"]; N = d["n"]
    J = t.where(kind == 1, mem, mem + 1); J = t.where((mem == 0) & (kind == 2), t.ones_like(J), J)
    def share(H, sel):
        ok = (H[None] <= CAP + 1e-3).float(); ww = (w * sel.float())[None] * WT[:, None]
        return float((ok * ww).sum() / ww.sum()) if float(ww.sum()) > 0 else float("nan")
    def med(x, sel): return float(x[sel].median()) if bool(sel.any()) else float("nan")
    cls = {}
    for mi in range(1, N): cls[f"ribbon link {mi}"] = m & (kind == 0) & (mem == mi)
    for Jj in range(1, N): cls[f"lower hub J{Jj}"] = m & (kind > 0) & S["is_low"] & (J == Jj)
    cls[f"BOTTOM hub J{N}"] = m & S["is_bot"]
    out = dict(score=r["score"], follow=r["follow"], in_band=r["in_band"], zj4=r["zj4"], arm_mm=r.get("arm_mm"), achieved=share(h, m), ceiling=share(hmin, m),
               classes={}, clips={k: round(v["score"], 3) for k, v in r.get("clips", {}).items()}, follow_clips={k: round(v["follow"], 3) for k, v in r.get("clips", {}).items()},
               faces={str(k): (round(v, 2) if v is not None else None) for k, v in B._faces.items()}, secs=round(time.time() - t0, 1))
    tot = float(w[m].sum())
    for name, sel in cls.items():
        if not bool(sel.any()): continue
        out["classes"][name] = dict(area=round(float(w[sel].sum()) / tot, 3), achieved=round(share(h, sel), 3), ceiling=round(share(hmin, sel), 3),
                                    lift_mm=round(med(h - hmin, sel), 2), skin_motion_mm=round(med(lo_rng, sel), 2))
    aux = getattr(B, "_aux", []); fu = B._faces_full.get("aux_under", [])
    for ax_, u_ in zip(aux, fu):                                                        # the neck / tab: their own in-band share
        LOa = ax_["LO"][fe]; CAPa = ax_["CAP"][fe]; wa = ax_["w"]
        ina = float((((u_[None] <= CAPa + 1e-3).float() * wa[None]) * WT[:, None]).sum() / (wa.sum() * WT.sum()))
        cea = float((((LOa.max(0).values[None] <= CAPa + 1e-3).float() * wa[None]) * WT[:, None]).sum() / (wa.sum() * WT.sum()))
        out["classes"][ax_["name"]] = dict(area_vs_scored=round(float(wa.sum()) / tot, 3), achieved=round(ina, 3), ceiling=round(cea, 3),
                                           lift_mm=round(float((u_ - LOa.max(0).values).median()), 2), skin_motion_mm=round(float(rng_(LOa).median()), 2))
    return out

def run(name, geo_ch, d_ch, Gs=(14.0, 10.0)):
    row = dict(variant=name, geo=geo_ch, design=d_ch)
    for G in Gs:
        for g, v in BASE.items(): setattr(BI, g, v)
        job = dict(GEO, mode="band_eval", poses=POSES, maps_cache=MAPS, q_step=GEO.get("q_step", 12), G=G); job.update(geo_ch)
        for g in GLOB:
            if g.lower() in job: setattr(BI, g, float(job[g.lower()]))
        d = dict(D0); d.update(d_ch)
        B = BI.Band(job, torch.device("cpu"))
        if os.environ.get("FILL_HOLES") == "1" and not getattr(BI, "_filled", False):      # measurement change: map_holes.py
            import map_holes; key = next(iter(BI._CACHE)); Mx, Px = BI._CACHE[key]; BI._CACHE[key] = (map_holes.fill(Mx), Px); BI._filled = True
            B = BI.Band(job, torch.device("cpu"))
        a = analyse(B, d); row[f"G{G:g}"] = a
        if a.get("err"): print(f"{name:34s} G{G:g}: REJECTED {a['err'][:150]}", flush=True); continue
        print(f"{name:34s} G{G:2g}: score {100 * a['score']:5.1f}  follow {100 * a['follow']:5.1f}  in-band {100 * a['in_band']:5.1f} (scored {100 * a['achieved']:5.1f} / ceiling {100 * a['ceiling']:5.1f})  {a['secs']:.0f}s", flush=True)
        for c, v in a["classes"].items():
            print(f"      {c:18s} area {v.get('area', v.get('area_vs_scored', 0)):5.2f}  in-band {100 * v['achieved']:5.1f} / ceiling {100 * v['ceiling']:5.1f}   lift {v['lift_mm']:5.1f} mm   skin motion {v['skin_motion_mm']:5.1f} mm", flush=True)
    return row

V = [("baseline", {}, {})]
if SET in ("hub", "all"):
    V += [("v5 stack (hub_up 7.1, cap_up 2.0)", dict(hub_up=7.1, cap_up=2.0), {}),
          ("hub_r 10 + v5 (O20)", dict(hub_r=10.0, hub_relief=10.0, hub_up=7.1, cap_up=2.0), {}),
          ("hub_r 8.5 (O17)", dict(hub_r=8.5, hub_relief=8.5), {}),
          ("flat lower hubs (relief 0)", dict(hub_relief=0.0), {}),
          ("CAD contour limit (relief 3.65)", dict(hub_relief=3.65), {}),
          ("hub margin 1.0", {}, dict(hm=1.0)),
          ("hub margin 0.5", {}, dict(hm=0.5))]
if SET in ("link", "all"):
    V += [("hw 4", dict(hw=4.0), {}), ("hw 3", dict(hw=3.0), {}),
          ("ramp 70", dict(ramp_deg=70.0), {}), ("ramp 80", dict(ramp_deg=80.0), {})]
if SET in ("order", "all"):
    for o in ([0, 1, 0], [1, 0, 0], [0, 0, 0]):
        if o != D0.get("order"): V.append((f"order {o}", {}, dict(order=o)))
if SET == "combo":
    V = [("baseline", {}, {}),
         ("O20 v5 + hw 4", dict(hub_r=10.0, hub_relief=10.0, hub_up=7.1, cap_up=2.0, hw=4.0), {}),
         ("O20 v5 + hw 4 + ramp 75 + hm 1", dict(hub_r=10.0, hub_relief=10.0, hub_up=7.1, cap_up=2.0, hw=4.0, ramp_deg=75.0), dict(hm=1.0))]
tag = os.environ.get("TAG", f"{os.path.splitext(os.path.basename(sys.argv[1]))[0]}_{SET}")
print(f"design {D0.get('_src', '')}; geo {sys.argv[2]}; {len(V)} variants", flush=True)
rows = []
for name, gc, dc in V:
    rows.append(run(name, gc, dc))
    json.dump(dict(design=D0, geo=GEO, rows=rows, poses=os.environ.get("POSES_FILE", "band_poses.b64"), filled_maps=os.environ.get("FILL_HOLES") == "1"), open(os.path.join(HERE, f"proximity_variants_{tag}.json"), "w"), indent=1)
