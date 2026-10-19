"""control: the SAME seats / knee with a plain O20 pin J2 (H1's model, today's kit) - is the gain the rolling pair or the seats?"""
import importlib.util, json, sys, os, time
sys.path.insert(0, "/home/user/exo-shoulder/tools")
spec = importlib.util.spec_from_file_location("pk", "/home/user/exo-shoulder/docs/concepts/models/skin-normal-3r-pin-knee.py")
PK = importlib.util.module_from_spec(spec); spec.loader.exec_module(PK)
import concept_bench as CB
B = CB.Bench(n_clip=60, n_ws=160)
best = json.load(open(sys.argv[1]))
H1 = json.load(open("/home/user/exo-shoulder/docs/concepts/rows/skin-normal-3r-pin-knee.json"))["best_params"]
out = {}
for name, par in (("H1_seats_pin_stk6", dict(H1, stk=6.0)), ("best_seats_pin", dict(H1, stk=6.0, **{k: v for k, v in best.items() if k not in ("alpha_s", "alpha_p", "beta", "bh")}))):
    r, M = PK._report(B, par); a = PK.audit(M, B)
    ws = [i for i in range(len(B.idx)) if B.kind[i] == "ws"]
    out[name] = dict({k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}, why=r["why"], gap1=a["gap_near1"],
                     kin_ws=int(M.kin_ok[ws].sum()), A=r["seats"]["a_deg"], parts=r.get("parts_ib14"))
    print(name, json.dumps(out[name], default=float), flush=True)
json.dump(out, open(sys.argv[2], "w"), indent=1, default=float)
