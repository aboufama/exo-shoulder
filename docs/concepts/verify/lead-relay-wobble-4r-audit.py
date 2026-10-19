"""Audit of lead-relay-wobble-4r (round 103, lens 1): a LOWER BOUND on the cell with every stack clash forgiven.

The death rests on stack clashes (the riser link 1a needs, hub 0 vs hub K). If those were a modelling artefact - a better
L1a routing, a flipped hub K, a re-clocked riser - the cell could in principle get under the lead. This probe removes them
all: PART_CLR = -inf (no stack part ever loses a pose), the riser deleted (no clash, no skin samples), and keeps only what
the stack cannot avoid: hub 1 lifted onto the wedge (its exposed crescent counts in band), link 1a lifted onto hub 1's boss,
hub 0's 80 underside samples at its seat, hub 0's skin contacts. Relayed poses (policy (ii), the model's own relay_wear and
an exhaustive window) are scored with the same forgiveness. If even this bound sits above the lead (12.50 on the fit bench
Bench(60,160) fast), no routing fix can refute the death.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/lead-relay-wobble-4r-audit.py census out.json
    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/lead-relay-wobble-4r-audit.py relay out.json '[[a0, azu, r0|null], ...]'
"""
import importlib.util, json, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if os.environ.get("AUD_FORGIVE", "1") == "1": os.environ["WOB_NORISER"] = "1"
_sp = importlib.util.spec_from_file_location("wobble_audit", os.path.join(HERE, "..", "models", "lead-relay-wobble-4r.py"))
W = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(W)
L = W.L
FORGIVE = os.environ.get("AUD_FORGIVE", "1") == "1"
if FORGIVE: W.PART_CLR = -1e9                                 # no stack clash ever loses a pose (counterfactual)
DROP_L1A = os.environ.get("AUD_DROP_L1A", "0") == "1"         # even more generous: link 1a's lifted samples not skin-facing


def geo(M1, a0, azu, r0):
    G = W.geometry(M1, a0, azu, r0)
    if FORGIVE: G["riser"] = np.zeros((0, 3))
    if DROP_L1A: G["XLl"] = np.zeros((0, 3))
    return G


def setup():
    M1, P2, fit = L.fit_lead(); B = M1.B; M0 = L.make_model(M1, P2, B); r_lead = M0.run(); sl = W.slices(M0)
    M0._mem = {k: m for k, (m, X) in list(M0.cyl_surf.items()) + list(M0.rigid.items()) + list(M0.strap.items())}
    return M1, P2, B, M0, r_lead, sl


if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]; t0 = time.time()
    M1, P2, B, M0, r_lead, sl = setup()
    print("lead q0=0 (fit bench):", {k: r_lead[k] for k in ("gap", "reach", "inband14", "contact")}, "forgive", FORGIVE, "drop_L1a", DROP_L1A, flush=True)
    res = json.load(open(out)) if os.path.exists(out) else []
    if mode == "census":
        seats = [(a0, azu, None) for a0 in (5.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 20.0) for azu in range(0, 360, 15)]
        seats += [(a0, float(azu), r0) for a0 in (5.0, 6.0, 8.0, 10.0) for azu in range(120, 240, 15) for r0 in (48.5, 50.5, 53.0)]
        if len(sys.argv) > 3: seats = [tuple(s) for s in json.loads(sys.argv[3])]
        for a0, azu, r0 in seats:
            try: G = geo(M1, a0, float(azu), r0)
            except RuntimeError as ex: res.append(dict(a0=a0, azu=azu, r0=r0, status=str(ex)[:40])); continue
            base, xs = W.base_real(M0, B, G, sl); rep = W.report(B, base)
            e = dict(a0=a0, azu=float(azu), r0_set=r0, r0=G["r0"], h=G["h"], gap=rep["gap"], inband14=rep["inband14"], reach=rep["reach"],
                     follow=rep["follow"], contact=rep["contact"], ws_taken=rep["ws_taken"], contacts=rep["contacts"], parts=rep["parts"],
                     hub1_exposed=G["n_exposed"])
            res.append(e); print(json.dumps(e), flush=True)
            json.dump(res, open(out, "w"), indent=1, default=float)
    else:
        for a0, azu, r0 in json.loads(sys.argv[3]):
            t = time.time(); G = geo(M1, a0, float(azu), r0); base, xs = W.base_real(M0, B, G, sl); z = W.report(B, base)
            cand, side, Teff = W.relay_wear(B, M1, P2, G, a0, M0, sl, base)
            qs = sorted(set([0.0] + [q for v in cand.values() for q in v[:2] if q is not None]))
            rows = []
            for lo in [q for q in qs if q <= 0]:
                for hi in [q for q in qs if q >= 0]:
                    r, _ = W.compose(B, base, cand, side, lo, hi); g, _ = W.compose(B, base, cand, side, lo, hi, ghost=True)
                    rows.append(dict(lo=lo, hi=hi, gap=r["gap"], ghost=g["gap"], inband14=r["inband14"], reach=r["reach"], follow=r["follow"],
                                     relay_taken=r["relay_taken"], relay_contact=r["relay_contact"]))
            best = min(rows, key=lambda x: (x["gap"], x["hi"] - x["lo"])); gb = min(rows, key=lambda x: x["ghost"])
            e = dict(a0=a0, azu=azu, r0_set=r0, r0=G["r0"], q0_zero=z["gap"], cand=len(cand), best=best, ghost_best=gb, secs=round(time.time() - t))
            res.append(e); print(json.dumps(e, default=float), flush=True)
            json.dump(res, open(out, "w"), indent=1, default=float)
    print("done", round(time.time() - t0), "s", flush=True)
