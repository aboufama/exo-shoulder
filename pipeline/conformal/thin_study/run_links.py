"""FEA thickness sweep of the built links / scapula bases of the three band designs.

    python3 -B run_links.py [design ...] [--variants V0,V1,...] [--test]
Writes links_<design>.json (one record per member x variant). Uses 2 BLAS threads (fe_core sets them).
"""
import sys, os, json, math, time
sys.dont_write_bytecode = True
import fe_core as F
import numpy as np
import link_geom as LG
import joint_model as JM

# thickness variants applied to every member of a design (generator globals): ribbon / lower plate / upper hub / washers
VARIANTS = {
    "V0": dict(t_link=4.0, t_lo=3.5, t_seat=5.05, t_w=1.0),   # as built (GSM-1012-05, GTM-1018-010)
    "V1": dict(t_link=3.5, t_lo=3.0, t_seat=4.05, t_w=1.0),   # GSM-1012-04
    "V2": dict(t_link=3.0, t_lo=2.5, t_seat=3.05, t_w=0.5),   # GSM-1012-03 + GTM-1018-005
    "V3": dict(t_link=2.5, t_lo=2.0, t_seat=3.05, t_w=0.5),
    "V4": dict(t_link=3.0, t_lo=3.0, t_seat=3.05, t_w=0.5),   # thin stack, lower plate kept 3.0
}
# uniform-thickness series (ribbon = lower plate = t, upper hub = t + 0.05, 0.5 mm washers) for the trade curves
for _t in (2.5, 3.0, 3.5, 4.0, 5.0, 6.0):
    VARIANTS[f"U{_t}"] = dict(t_link=_t, t_lo=_t, t_seat=_t + 0.05, t_w=0.5)
# width lever: 18 mm strip (HW 9) instead of 14
for _t in (3.0, 4.0):
    VARIANTS[f"W9_U{_t}"] = dict(t_link=_t, t_lo=_t, t_seat=_t + 0.05, t_w=0.5, hw=9.0)
JOBS = ([(k, mi, "V0") for k, n in (("4c_best", 4), ("5r_thin", 5), ("4r_thin", 4)) for mi in range(n)]
        + [(k, mi, f"U{t}") for (k, mi) in (("4c_best", 2), ("4c_best", 1), ("5r_thin", 4), ("5r_thin", 3), ("4c_best", 0), ("5r_thin", 0))
           for t in (2.5, 3.0, 3.5, 4.0, 5.0, 6.0)]
        + [(k, mi, f"W9_U{t}") for (k, mi) in (("4c_best", 2), ("4c_best", 1)) for t in (3.0, 4.0)])


def member_mass(msh, G):
    v = msh["vol"]
    for h in msh["hubs"]:
        if h.low:
            dep0 = float(np.asarray(h.dep(np.zeros(1), np.zeros(1))).ravel()[0]) if h.dep is not None else 0.0
            v += math.pi * 25.0 * (h.tp + dep0)                                         # pin column through the plate
            L = G.T_W + G.T_SEAT + G.T_W + 0.02; v += math.pi * 25.0 * L - math.pi * JM.P_TAP_R ** 2 * JM.P_TAP_L
    return v * F.RHO_TI


def run_member(key, mi, var):
    G = LG.generator(key); vv = dict(VARIANTS[var]); hw = vv.pop("hw", 7.0)
    LG.set_thickness(G, **vv); G.HW = hw; G.CH.HW = hw
    d, msh = LG.mesh_member(key, mi)
    if d["kind"] == "base":
        res = JM.analyse(msh, G, None, loaded=0, fixed=None, base_bolts=d["hubs"][0].bolts)
        excl = np.zeros(len(msh["X"]), bool); hub = d["hubs"][0]
        for xb in hub.bolts:
            c = hub.n * hub.z0 + xb * hub.d; dd = msh["X"] - c; dd = dd - np.outer(dd @ hub.n, hub.n)
            excl |= np.linalg.norm(dd, axis=1) < 4.5
        for k in ("vm_D1", "vm_D2", "vm_D3", "vm_des"): res[k] = np.where(excl, 0.0, res[k])
        zones = JM.zones(msh, res, 0, None)
    else:
        res = JM.analyse(msh, G, None, loaded=1, fixed=0)
        zones = JM.zones(msh, res, 1, 0)
    rec = dict(design=key, member=mi, variant=var, thick=VARIANTS[var], kind=d["kind"], gen_path=d.get("gen_path", "base"),
               centre_dist=d.get("centre_dist"), roles=[("low" if h.low else "up") for h in d["hubs"]],
               joints=[int(h.J) for h in d["hubs"]], hub_t=[float(h.tp) for h in d["hubs"]],
               mass_g=member_mass(msh, G), mesh_vol=msh["vol"], zones=zones, k_link_Nm_deg=res["k_link"], k_tot_Nm_deg=res["k_tot"],
               defl_D3_mm=res["defl_D3"], pin=res["pin"], ndof=res["ndof"], secs=res["secs"])
    if d["kind"] == "short": rec["neck_as_built_mm"] = d["neck_as_built"] if d.get("gen_path") == "short" else None
    if d["kind"] == "long": rec["ribbon_ramp_dropped"] = d["strip"].get("dropped")
    return rec


if __name__ == "__main__":
    fn = "links_fea.json"; out = json.load(open(fn)) if os.path.exists(fn) else []
    done = {(r["design"], r["member"], r["variant"]) for r in out}
    jobs = JOBS if "--test" not in sys.argv else [("4c_best", 2, "V0")]
    for key, mi, var in jobs:
        if (key, mi, var) in done: continue
        t0 = time.time()
        try:
            r = run_member(key, mi, var)
        except Exception as e:
            print(f"{key} m{mi} {var}: FAILED {type(e).__name__}: {e}", flush=True); continue
        out.append(r)
        z = r["zones"]["des"]
        print(f"{key} m{mi} {var} {r['kind']:5s}: des body {z['body']:.0f} (p99.5 {z['body_p995']:.0f}) "
              + " ".join(f"{k} {v:.0f}" for k, v in z.items() if k.startswith("hub") and not k.endswith("corner"))
              + f" | D1 body {r['zones']['D1']['body']:.0f} D2 {r['zones']['D2']['body']:.0f} | k_link {r['k_link_Nm_deg'][0]:.2f}/{r['k_link_Nm_deg'][1]:.2f}"
              f" N.m/deg | {r['mass_g']:.1f} g | {r['ndof']} dof {time.time() - t0:.0f}s", flush=True)
        json.dump(out, open(fn, "w"), indent=1)
