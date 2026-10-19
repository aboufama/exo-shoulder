"""Usage: OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/lead-relay-backbridge-4r-audit-scan.py out.json 60 0,30,60,90,120,150,180,210,240,270,300,330 0,-30,30
audit: seat scan over the FULL azimuth circle (the screen measured azu 285-0 only): per seat, seat rule, hub 0 skin-set
r0 + chain clash count, hub 0 in-band on fit clips, and link 0 (great circle + planform turns) chain-set vs skin-set
stations and in-band on fit clips"""
import json, sys, time, importlib.util, numpy as np
import os; REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sp = importlib.util.spec_from_file_location("bb", REPO + "/docs/concepts/models/lead-relay-backbridge-4r.py")
BB = importlib.util.module_from_spec(sp); sp.loader.exec_module(BB)
t0 = time.time()
M1, P2, r = BB.fit_lead(); B1 = M1.B; u1 = M1.D.u[0]; r1 = float(M1.f[0])
print("fit", r["gap"], round(time.time() - t0), flush=True)
tk = list(np.nonzero(M1.kin_ok)[0]); clips = [i for i in range(len(B1.idx)) if B1.kind[i] == "clip"]
out = []
a0s = [float(x) for x in sys.argv[2].split(",")]; azs = [float(x) for x in sys.argv[3].split(",")]; sides = [float(x) for x in sys.argv[4].split(",")]
for a0 in a0s:
    for azu in azs:
        c = BB.seat_axis(u1, a0, azu); ok = bool(BB.seat_ok(c)[0])
        row = dict(a0=a0, azu=azu, seat_ok=ok, c_bvec=[round(float(np.degrees(np.arctan2(c[2], -c[0]))), 1), round(float(np.degrees(np.arcsin(c[1]))), 1)])
        if not ok: out.append(row); print(json.dumps(row), flush=True); continue
        row["travel"] = BB.travel(c, u1)
        r0, rs, rcn = BB.build_metal(M1, B1, c); row.update(r0=r0, r0_chain=rcn, clash_fit=BB.build_metal.clash_at_skin)
        hu, _ = BB.hub0_metal(c, r0)
        dd = np.concatenate([B1.dist(i, hu @ M1.RS[i].T) for i in clips])
        row["hub0_ib"] = round(float(((dd >= 2) & (dd <= 14)).mean()), 3); row["hub0_med"] = round(float(np.median(dd)), 1)
        rt = []
        for side in sides:
            d, lat, s, rho, ns, nc = BB.fit_link0(M1, B1, c, r0, u1, r1, tk, {}, side)
            under, mid, cont = BB.link0_metal(d, lat, rho)
            dl = np.concatenate([B1.dist(i, under @ M1.RS[i].T) for i in clips])
            rt.append(dict(side=side, len=round(float(s[-1]), 1), n=len(under), chain_sets=int((nc > ns).sum()), skin_sets=int((ns >= nc).sum()),
                           ib=round(float(((dl >= 2) & (dl <= 14)).mean()), 3), med=round(float(np.median(dl)), 1)))
        row["routes"] = rt
        # in-band ceiling with this hub 0 + best route (chain 884/981 on the claim pool scale, fit-clip shares as proxies)
        best = max(rt, key=lambda x: x["ib"] * 0 - (1 - x["ib"]) * x["n"])
        row["ib_est"] = round((884 + 81 * row["hub0_ib"] + best["n"] * best["ib"]) / (981 + 81 + best["n"]), 4)
        out.append(row); print(json.dumps(row), round(time.time() - t0), flush=True)
        json.dump(out, open(sys.argv[1], "w"), indent=1)
json.dump(out, open(sys.argv[1], "w"), indent=1)
