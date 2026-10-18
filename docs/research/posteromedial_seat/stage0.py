"""stage 0 (amended; PM_WA_MAX=90: the lateral-J3 variant, J3 seat |wa| <= 90 = the lateral half of the arm, tag _lat), docs/research/posteromedial_seat.md): per cell the best seed (seat, branch) by fit-bench window share
with the lead's rest th (amendment 1) and a skin-borne J2 seat (amendment 2); ONE fast evaluation on Bench(60,160);
-> stage0_<cell>.json (seed list, report, cam, why, parts, seconds). Fit bench only.
    OMP_NUM_THREADS=1 nice -n 10 python3 docs/research/posteromedial_seat/stage0.py -52.5,17.5 ...
"""
import importlib.util, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
MP = os.path.join(REPO, "docs", "concepts", "models", "posteromedial-knuckle-3r.py")
sp = importlib.util.spec_from_file_location("pm_model", MP); PM = importlib.util.module_from_spec(sp); sp.loader.exec_module(PM)
B = PM.CB.Bench(n_clip=60, n_ws=160)
for cell in sys.argv[1:]:
    az, el = (float(x) for x in cell.split(",")); tag = f"az{az:g}_el{el:g}"; t0 = time.time()
    WAX = float(os.environ.get("PM_WA_MAX", 180.0)); tag += "_lat" if WAX < 180 else ""
    sd = PM.seed(az, el, top=3, wa_abs_max=WAX); res = dict(cell=[az, el], seed=sd, wa_abs_max=WAX)
    if sd:
        s0 = sd[0]; par = dict(az1=az, el1=el, wd=s0["wd"], wa=s0["wa"], br=s0["br"]); B.reset()
        try: r, M = PM._report(B, par)
        except AssertionError as e:                                  # an off-ray hub offset above the 1e-3 mm snap
            import numpy as np
            D = PM._KB.PK.Design(PM._clamp(dict(PM.PARAMS, **par)))
            res.update(params=par, error=str(e), c_norm_mm=[float(np.linalg.norm(c)) for c in D.c[:2]], rest_err_deg=float(D.rest_err))
            json.dump(res, open(os.path.join(HERE, f"stage0_{tag}.json"), "w"), indent=1, default=float)
            print(tag, json.dumps({k: res.get(k) for k in ("error", "c_norm_mm", "rest_err_deg")}), flush=True); continue
        res.update(params=par, near1=r.get("gap_near1"), plain=r.get("plain"), gap_near2=r.get("gap_near2"), reach=r.get("reach"),
                   inband14=r.get("inband14"), contact=r.get("contact"), why=r.get("why"), cam=r.get("cam"), seats=r.get("seats"),
                   parts=r.get("parts_ib14"), knee=r.get("knee"),
                   honest=not (r.get("sidecar_fail") or r.get("drive_idle") or r.get("pa_fail") or r.get("knee_moved")),
                   flags={k: r.get(k) for k in ("sidecar_fail", "drive_idle", "pa_fail", "knee_moved")})
    res["secs"] = round(time.time() - t0, 1)
    json.dump(res, open(os.path.join(HERE, f"stage0_{tag}.json"), "w"), indent=1, default=float)
    print(tag, json.dumps({k: res.get(k) for k in ("near1", "plain", "honest", "flags", "why", "secs")}, default=float), flush=True)
