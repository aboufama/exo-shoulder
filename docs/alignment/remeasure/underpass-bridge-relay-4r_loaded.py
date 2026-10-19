"""Alignment auditor's own check (2026-10-18): the CORRECTED bridge (verifier's A_up1.2, R_under 84.222) read with the
verifier's X1 clash check on the LOADED shell (underside, foot and flange lowered by the bridge's own 4 N tip deflection,
uniform: an upper bound), which the verifier ran only at the claimed height (81.307). Imports the model and the verifier
UNCHANGED; it only calls their functions. Also records the wear's continuity flood and the relay coordinate's range.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/alignment/remeasure/underpass-bridge-relay-4r_loaded.py bench|held
        -> docs/alignment/remeasure/underpass-bridge-relay-4r_loaded_<wear>.json
"""
import importlib.util, json, os, sys, time

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
os.environ["CB_EXACT"] = "1"
_sp = importlib.util.spec_from_file_location("underpass_verify_ro", os.path.join(REPO, "docs", "concepts", "verify", "underpass-bridge-relay-4r-verify.py"))
V = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(V)
UP = V.UP
RL_A = 84.222   # verifier_fix.json A_up1.2 rl_fix (the design's own up_clr 1.2 over every chain set)


def main(wear):
    nc, nw = (-1, -1) if wear == "held" else (110, 360)
    t0 = time.time(); S = UP.prepare(V.BASE, nc, nw, exact=True)
    out = dict(id="underpass-bridge-relay-4r", wear=wear, rl_fix=RL_A, ideal=S["ideal"], prepare_secs=round(time.time() - t0, 1))
    print(json.dumps(dict(prepared=True, ideal=S["ideal"])), flush=True)
    hw = dict(V.BASE, **dict(V.PICK, rl_fix=RL_A))
    o = UP.wear(S, hw); sm = UP.summary(o); out["summary"] = sm
    out["continuity"] = {k: v for k, v in (o.get("continuity") or {}).items() if k != "dropped"}
    out["relayed"] = o.get("relayed"); out["why"] = o.get("why")
    defl = float(o["underpass"]["defl_mm"]); out["defl_mm"] = defl
    print(json.dumps(dict(summary=sm, continuity=out["continuity"], relayed=out["relayed"]), default=float), flush=True)
    for dr in (0.0, defl):
        x = V.xcheck(S, hw, drop=dr)
        r = dict(drop=dr, n_extra_jam=x["n_extra_jam"], lost_new=x["lost_new"], new_contacts=x["new_contacts"], rescored=x["rescored"],
                 margin={k: v for k, v in x["clearance_margin_taken"].items() if k != "lowest"},
                 lowest=x["clearance_margin_taken"]["lowest"][:10],
                 jam_rows=[dict(i=j["i"], pose=j["pose"], metal_min=j["metal_min"], jam=j["jam"][:3]) for j in x["extra_jam_rows"]])
        out[f"xcheck_drop{dr:g}"] = r
        print(json.dumps(dict(drop=dr, n_extra_jam=r["n_extra_jam"], lost_new=r["lost_new"], rescored=r["rescored"], margin=r["margin"]), default=float), flush=True)
        json.dump(out, open(os.path.join(REPO, "docs", "alignment", "remeasure", f"underpass-bridge-relay-4r_loaded_{wear}.json"), "w"), indent=1, default=float)
    out["secs"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(REPO, "docs", "alignment", "remeasure", f"underpass-bridge-relay-4r_loaded_{wear}.json"), "w"), indent=1, default=float)
    print("done", out["secs"], flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
