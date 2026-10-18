"""(usage: python3 docs/concepts/verify/cap-plateau-knuckle-3r_kinscan.py C|B <seed> <n> <outdir>; the Cwide branch is unused)
kinematic ceiling over each cell's sweep box on Bench(110,360) (fold + closure + K dyad only; metal only removes takes)"""
import sys, json, importlib.util, numpy as np, time
REPO = "/home/user/exo-shoulder"; sys.path.insert(0, REPO + "/tools")
import concept_kit as K, concept_bench as CB
sp = importlib.util.spec_from_file_location("cap", REPO + "/docs/concepts/models/cap-plateau-knuckle-3r.py"); M = importlib.util.module_from_spec(sp); sp.loader.exec_module(M)
B = CB.Bench(110, 360); F = K.frames(B); kind = np.array(B.kind); ws = kind == "ws"
elev = np.array([B.poses[i]["elev"] for i in range(len(B.idx))]); ov = ws & (elev >= 140)

def kin_ok(p):
    m = float(p["margin"]); a2 = float(p["a2"]); lo, cap = float(p["lo"]), float(p["cap"])
    bk1 = float(p["bk1"]); bk2 = float(p["bk2"]) if p.get("bk2") is not None else cap + 5.0 - bk1
    if not ((abs(bk1 - bk2) + 5.0 <= lo) and (bk1 + bk2 >= cap + 5.0 - 1e-9)): return None
    p1 = F.S(K.bvec(p["az1"], p["el1"])); p3 = F.HG(K.wdir(p["d3"], p["a3"]))
    th = np.degrees(np.arccos(np.clip((p1 * p3).sum(-1), -1, 1)))
    a1e = M.law(th, p); ok, _ = M.fold_ok(th, a1e, a2, m)
    p2, okc = M.KP.closure_v(p1, p3, a1e, a2, float(p["sigma"])); ok &= okc
    return ok

rng = np.random.default_rng(int(sys.argv[2]) if len(sys.argv) > 2 else 0); cell = sys.argv[1]; n = int(sys.argv[3]) if len(sys.argv) > 3 else 3000
rows = []; t0 = time.time()
for k in range(n):
    p = dict(M.CELLS[cell])
    if cell == "C":
        p.update(az1=rng.uniform(56, 66), el1=rng.uniform(60, 67), d3=rng.uniform(96, 104), a3=rng.uniform(-8, 0), lo=rng.uniform(26, 31),
                 f=rng.uniform(26, 34), a2=rng.uniform(43, 48), cap=rng.uniform(50, 56), bk1=rng.uniform(25, 30))
        p["off"] = p["a2"] - rng.uniform(6, 8); p["bk2"] = p["cap"] + 5 - p["bk1"] + rng.uniform(0, 1)
    elif cell == "B":
        p.update(az1=rng.uniform(52, 62), el1=rng.uniform(58, 66), d3=rng.uniform(88, 98), a3=rng.uniform(-14, -4), lo=rng.uniform(29, 34),
                 a2=rng.uniform(48, 54), cap=rng.uniform(52, 60), bk1=rng.uniform(28, 34))
        p["off"] = p["a2"] - p["margin"] - 0.01
    elif cell == "A":
        p.update(d3=rng.uniform(88, 94), a3=rng.uniform(-10, 12), sigma=float(rng.choice([-1, 1])), bk1=rng.uniform(26, 34), lo=rng.uniform(38, 42),
                 off=rng.uniform(60, 64), cap=rng.uniform(60, 64))
    elif cell == "Cwide":                                    # cell C's law family over the whole cap region (o.py's 'cap' box)
        p = dict(M.CELLS["C"]); p.update(az1=rng.uniform(30, 66), el1=rng.uniform(52, 68), d3=rng.uniform(85, 106), a3=rng.uniform(-15, 20),
                 lo=rng.uniform(24, 46), a2=rng.uniform(40, 80), sigma=float(rng.choice([-1, 1])))
        p["cap"] = p["lo"] + rng.uniform(8, 35); p["off"] = p["a2"] - rng.uniform(5.3, 10); p["f"] = abs(p["a2"] - p["lo"]) + 5 + rng.uniform(0, 40)
        p["bk1"] = rng.uniform(15, 35); p["bk2"] = p["cap"] + 5 - p["bk1"] + rng.uniform(0, 6)
    ok = kin_ok(p)
    if ok is None: continue
    rows.append(dict(p={k_: (float(v) if isinstance(v, (int, float, np.floating)) and v is not None else v) for k_, v in p.items()},
                     ws=int((ok & ws).sum()), clip=int((ok & ~ws).sum()), ov=int((ok & ov).sum())))
rows.sort(key=lambda r: (-r["ws"], -r["clip"]))
print(cell, "n", len(rows), "secs", round(time.time() - t0), "max ws", rows[0]["ws"], "clip", rows[0]["clip"], "ov", rows[0]["ov"])
print(" ws p50/p90/p99/max", np.percentile([r["ws"] for r in rows], [50, 90, 99, 100]).round(1).tolist(),
      " n >= 279 with clips 110:", sum(1 for r in rows if r["ws"] >= 279 and r["clip"] == 110), " n >= 279 any:", sum(1 for r in rows if r["ws"] >= 279))
for r in rows[:3]: print("  ", r["ws"], r["clip"], r["ov"], {k: round(v, 2) for k, v in r["p"].items() if isinstance(v, float)})
json.dump(rows[:200], open(f"{sys.argv[4] if len(sys.argv) > 4 else '.'}/kin_{cell}.json", "w"), default=float)
