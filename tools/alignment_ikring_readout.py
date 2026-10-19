"""Alignment readout for ikring-thinstack-knuckle-4r (read-only): what the wearer gets, from the per-pose dumps on file, plus a
controller-transfer test of the design's oracle IK. Changes no score, no row, no model, no bench.

1. readout: per dump, taken clip / ws poses with metal < 1 / 2 / 3 mm, overhead (elev >= 140) and raised-arm (elev >= 90)
   reach, contact poses with their depth (sum, deepest) - for the claim (bench + held ws sample), the verified lead
   conecut-knee-knuckle-3r and phi40-thinstack-relay-4r (the same ring hardware with its coil, the MVP1-determinate twin).
2. controller transfer: the claim's psi is chosen per pose ON the scored bench (max min metal among the k that take the
   pose), and the held reading re-chooses psi per HELD pose the same way. A controller learned off the held poses is the
   honest held test: psi(held pose) = the claim-bench choice of the nearest bench ws pose (humerus direction angle and
   axial difference, hypot; ties -> the median tied psi). Whether that psi takes the held pose is read straight from the
   held k-table's per-pose take sets (docs/concepts/verify/ikring-thinstack-knuckle-4r/ik_heldws.json ik.choice[j].takes);
   a held pose k = 0 takes whose controller psi is not 0 was never worn at that psi: counted 'unknown'.

    python3 tools/alignment_ikring_readout.py <out.json>
"""
import json, os, sys
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = "docs/concepts/verify/ikring-thinstack-knuckle-4r/"
DUMPS = [("ikring_bench_verifier", V + "verifier/v_bench_full_perpose.json"), ("ikring_bench_claim", V + "ik_bench_spec_perpose.json"),
         ("ikring_heldws_spec", V + "ik_heldws_specrule_perpose.json"),
         ("lead_bench", "docs/alignment/remeasure/conecut-knee-knuckle-3r_bench_perpose.json"),
         ("lead_held", "docs/alignment/remeasure/conecut-knee-knuckle-3r_held_perpose.json"),
         ("phi40_bench", "docs/alignment/remeasure/phi40-thinstack-relay-4r_bench_perpose.json"),
         ("phi40_held", "docs/alignment/remeasure/phi40-thinstack-relay-4r_held_perpose.json")]


def readout(f):
    d = json.load(open(os.path.join(REPO, f))); P = d["poses"]
    out = dict(src=f, report=d.get("report"), recomputed=d.get("recomputed"))
    for kind in ("clip", "ws"):
        Q = [p for p in P if p["kind"] == kind]; tk = [p for p in Q if p.get("taken")]
        mm = np.array([p["min_mm"] for p in tk if p.get("min_mm") is not None])
        o = dict(n=len(Q), taken=len(tk), under1=int((mm < 1).sum()), under2=int((mm < 2).sum()), under3=int((mm < 3).sum()),
                 median_min_mm=round(float(np.median(mm)), 2) if len(mm) else None)
        if kind == "ws":
            for lab, lo in (("overhead140", 140), ("raised90", 90)):
                QQ = [p for p in Q if p["elev"] >= lo]; TT = [p for p in QQ if p.get("taken")]
                o[lab] = [len(TT), len(QQ)]; o[lab + "_under2"] = sum(1 for p in TT if p.get("min_mm") is not None and p["min_mm"] < 2)
        out[kind] = o
    C = [p for p in P if p.get("contact")]
    out["contacts"] = sorted([dict(i=p["i"], kind=p["kind"], pose=[round(p["plane"], 1), round(p["elev"], 1), round(p["axial"], 1)], mm=p["min_mm"]) for p in C],
                             key=lambda x: x["mm"])
    dd = [-p["min_mm"] for p in C]
    out.update(contact_sum_mm=round(sum(dd), 2), contact_max_mm=round(max(dd), 2) if dd else 0.0, contact_overhead140=sum(1 for p in C if p["elev"] >= 140))
    return out


def _dir(pl, el):
    pl, el = np.radians([pl, el]); return np.array([np.sin(el) * np.cos(pl), np.sin(el) * np.sin(pl), -np.cos(el)])


def _dist(a, b):
    g = np.degrees(np.arccos(np.clip(_dir(a[0], a[1]) @ _dir(b[0], b[1]), -1, 1))); s = abs(((a[2] - b[2] + 180) % 360) - 180)
    return float(np.hypot(g, s))


def controller_transfer():
    bp = json.load(open(os.path.join(REPO, V + "ik_bench_spec_perpose.json")))["poses"]
    bc = json.load(open(os.path.join(REPO, V + "ik_bench_spec.json")))["ik"]["choice"]
    hp = json.load(open(os.path.join(REPO, V + "ik_heldws_specrule_perpose.json")))["poses"]
    hc = json.load(open(os.path.join(REPO, V + "ik_heldws.json")))["ik"]["choice"]
    key = lambda p: (float(p["plane"]), float(p["elev"]), float(p["axial"]))
    B = [(p["i"], key(p)) for p in bp if p["kind"] == "ws"]; bpsi = {i: (float(bc[str(i)]["k"]) if str(i) in bc else 0.0) for i, _ in B}
    res = dict(rule="psi(held) = claim-bench psi of the nearest bench ws pose (ties -> median tied psi)", new_held_oracle=0, kept=0, kept_any_tied=0,
               kept_all_tied=0, lost=[], k0_held_taken=0, k0_ctrl0=0, k0_unknown=0)
    nd = []
    for p in hp:
        if p["kind"] != "ws": continue
        j = str(p["i"]); x = key(p); d = np.array([_dist(x, b) for _, b in B]); dm = d.min(); nd.append(dm)
        near = [B[q][0] for q in np.nonzero(d <= dm + 1e-6)[0]]; ps = sorted({bpsi[i] for i in near})
        med = float(np.median([bpsi[i] for i in near])); pc = min(ps, key=lambda v: abs(v - med))
        if j in hc:
            tk = hc[j]["takes"]
            if not tk: continue
            ok = lambda v: any(abs(float(kk) - v) < 1e-6 for kk in tk)
            res["new_held_oracle"] += 1; res["kept"] += int(ok(pc)); res["kept_any_tied"] += int(any(ok(v) for v in ps)); res["kept_all_tied"] += int(all(ok(v) for v in ps))
            if not ok(pc):
                res["lost"].append(dict(i=p["i"], pose=[round(v, 1) for v in x], oracle_k=hc[j]["k"], ctrl_k=pc, takes=sorted(float(k) for k in tk)))
        elif p["taken"]:
            res["k0_held_taken"] += 1
            if all(v == 0 for v in ps): res["k0_ctrl0"] += 1
            else: res["k0_unknown"] += 1
    nd = np.array(nd); res["nn_dist_deg"] = dict(median=round(float(np.median(nd)), 1), p90=round(float(np.percentile(nd, 90)), 1))
    res["n_lost"] = len(res["lost"]); res["lost_overhead140"] = sum(1 for q in res["lost"] if q["pose"][1] >= 140)
    n_ws = sum(1 for p in hp if p["kind"] == "ws")
    lo, hi = res["k0_ctrl0"] + res["kept"], res["k0_held_taken"] + res["kept"]
    res["held_ws_taken_ctrl"] = [lo, hi, n_ws]; res["held_reach_ctrl"] = [round(lo / n_ws, 4), round(hi / n_ws, 4)]
    res["held_ws_taken_oracle"] = res["k0_held_taken"] + res["new_held_oracle"]
    return res


if __name__ == "__main__":
    res = {}
    for lab, f in DUMPS:
        try: res[lab] = readout(f)
        except Exception as e: res[lab] = dict(err=repr(e)[:200])
    res["controller_transfer"] = controller_transfer()
    json.dump(res, open(sys.argv[1], "w"), indent=1, default=float)
    for k, v in res.items():
        if k == "controller_transfer": print(k, {a: b for a, b in v.items() if a != "lost"}); continue
        if "err" in v: print(k, v); continue
        print(k, "clip", {a: v["clip"][a] for a in ("taken", "under1", "under2", "under3")}, "ws", v["ws"], "contacts", len(v["contacts"]), v["contact_sum_mm"], v["contact_max_mm"])
