"""Alignment probe (read-only): how much of a desmo-family claim lives in the stage-1 blend, where the 'built' groove
reading leaves the cap (back-drive) side ungated?

desmo-conecut-knuckle-3r reads stage 1 on the BUILT blended groove: the pin side is gated wherever the pin moves, the cap
side only outside the blend (x >= half-blend); inside the blend the cap-side pressure angle is reported, not gated. This
probe runs the claim model UNCHANGED (best_params of the row; fast Bench(60,160) for the groove arrays, and the frozen
claim wear for the per-pose K), and reports:
  * the built cap-side pressure angle against K over the blend: where it is above the family gate 43 - atan(mu) and above
    the self-locking line 90 - atan(mu) (locals of DCModel._desmo_build_B captured with a return-trace, nothing patched);
  * the taken poses' |dK| histogram on the frozen claim wear (PK.audit wrapped to capture (M, B), as
    tools/alignment_wear_probe_model.py does): how many taken poses sit with K inside the ungated band.
It changes no score, no bench, no model and no row.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice python3 tools/alignment_blend_band_probe.py <id> <out.json> [--no-wear]
"""
import json, math, os, sys, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import alignment_wear_probe as W                              # noqa: E402


def groove_profile(mod, P):
    import concept_bench as CB
    grab = {}
    code = mod.DCModel._desmo_build_B.__code__

    def tr(frame, event, arg):
        if frame.f_code is code:
            def loc(fr, ev, a):
                if ev == "return":
                    for k in ("capb", "Kbb", "xb", "hb_", "PAC", "mvb"):
                        if k in fr.f_locals: grab[k] = fr.f_locals[k]
                return loc
            return loc
        return None
    sys.settrace(tr)
    try:
        B = CB.Bench(n_clip=60, n_ws=160); mod._report_dc(B, dict(P))
    finally:
        sys.settrace(None)
    if "capb" not in grab: return dict(error="built-groove locals not captured")
    capb, Kbb, xb, hb = np.asarray(grab["capb"]), np.degrees(np.asarray(grab["Kbb"])), np.degrees(np.asarray(grab["xb"])), math.degrees(float(grab["hb_"]))
    mu = float(P.get("mu", 0.087)); gate = 43.0 - math.degrees(math.atan(mu)); lock = 90.0 - math.degrees(math.atan(mu))
    inb = (xb > -hb) & (xb < hb) & (Kbb > 1e-9)
    def band(th):
        m = inb & (capb > th)
        return [round(float(Kbb[m].min()), 3), round(float(Kbb[m].max()), 3)] if m.any() else None
    rows = [(round(float(k), 3), round(float(c), 2)) for k, c in zip(Kbb[inb][::25], capb[inb][::25])]
    return dict(mu=mu, gate_deg=round(gate, 2), self_lock_deg=round(lock, 2), half_blend_K_deg=round(hb, 3),
                blend_K_span_deg=[round(float(Kbb[inb].min()), 3), round(float(Kbb[inb].max()), 3)] if inb.any() else None,
                cap_above_gate_K=band(gate), cap_above_self_lock_K=band(lock), cap_above_60_K=band(60.0),
                cap_outside_blend_max=round(float(capb[xb >= hb].max()), 2) if (xb >= hb).any() else None, rows_K_cap=rows)


def wear_dk(mod, P):
    pk = getattr(mod, "PK", None)
    cap = W._capture(pk)
    out = mod.frozen(dict(P)); M, B = cap[-1]
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    d = np.degrees(np.abs(np.asarray(M.dK, float)))
    edges = [0.0, 1e-6, 2.0, 5.0, 10.0, 15.0, 20.0, 30.0, 40.0, 1e9]
    def hist(ix):
        v = d[ix]; return {(f"{a:g}-{b:g}" if b < 1e8 else f">{a:g}") if a > 0 else "0 (rest)": int(((v >= a) & (v < b)).sum()) if a > 0 else int((v < b).sum())
                           for a, b in zip(edges[:-1], edges[1:])}
    kind = np.array(B.kind); el = np.array([p["elev"] for p in B.poses])
    T = np.array(taken)
    return dict(frozen=out.get("frozen"), n_taken=len(taken), hist_all=hist(T), hist_ws=hist(T[kind[T] == "ws"]), hist_clip=hist(T[kind[T] == "clip"]),
                hist_ws_elev90=hist(T[(kind[T] == "ws") & (el[T] >= 90)]), dK_taken=d[T].round(3).tolist())


if __name__ == "__main__":
    rid, outp = sys.argv[1], sys.argv[2]
    row = json.load(open(os.path.join(W.REPO, "docs", "concepts", "rows", rid + ".json")))
    P = dict(row.get("best_params") or {})
    mod = W._load("abbp_" + rid.replace("-", "_"), os.path.join(W.REPO, "docs", "concepts", "models", rid + ".py"))
    t = time.time(); r = dict(design=rid, params=P, groove=groove_profile(mod, P))
    if "--no-wear" not in sys.argv:
        r["wear"] = wear_dk(mod, P)
    r["secs"] = round(time.time() - t, 1); r["exact"] = os.environ.get("CB_EXACT") == "1"
    json.dump(r, open(outp, "w"), indent=1, default=float)
    print(json.dumps(dict(groove={k: v for k, v in r["groove"].items() if k != "rows_K_cap"},
                          wear={k: v for k, v in (r.get("wear") or {}).items() if k != "dK_taken"}, secs=r["secs"]), default=float))
