"""Independent verifier (skeptic) of trimlug-k165-knuckle-3r: the verified slipper-nose lead with its horn lug trimmed at
r_K <= (farthest flank contact over [0, dK_lim]) + trim_wall (best 1.5 mm), a dense 0.5 mm contact-only lug copy, all other
features off. Claim: frozen exact Bench(110,360) 18.51 (lead 18.49), held 23.47, T5 14.74 -> 13.18 mm (held 46.35 -> 40.59).

The claim's model (docs/concepts/models/trimlug-k165-knuckle-3r.py) is loaded UNCHANGED. This harness re-uses the lead's
verifier (docs/concepts/verify/slipper-nose-knuckle-3r.py: frozen protocol fit Bench(60,160) fast -> shape frozen -> worn
on Bench(110,360) exact / held out; cam closure in the world, nose vs lug, K sense, PA + friction per taken pose, lobe PA,
drive-idle, th margin, conjugate undercut, relative pole) retargeted at the claim's TLModel (its patched SN module: model
class, clamp, params, the row's best_params). It ADDS, for the trim:

  T1. CONTACT LINE ON RETAINED METAL: the dowel's contact line (nose rings at -1.25 / 0 / +1.25 mm along the GH ray, i.e.
      the flank ruling through Q) at every K step up to the largest |dK| taken, read at the trim's own radius (the trim is
      decided on the lug underside |X| = rL and carried up the GH ray): edge margin = r_trim - r_K(contact) >= 0.5 mm.
  T2. BACK THICKNESS behind every used contact after the trim (along the flank normal, LUG_BACK 6 mm before the trim).
  T3. LUG CONNECTIVITY: the trimmed lug's rigid samples (underside) form one piece with its root (graph at 2.5 mm).
  T4. TRIM CONSISTENCY: no member-1 contact-only sample of the lug's layers left outside r_trim (an untrimmed top layer
      would be conservative; a trimmed rigid lug with an untrimmed scored copy elsewhere would be inconsistent).
  T5. DENSE LUG PART-PART: the dense lug copy (contact-only in the claim, i.e. never part-checked) worn against every
      other member's rigid samples at every taken pose; min distance per member (the crank arm runs over the lug at RUNG).
  --edge: the lead verifier's flank-edge strip (nose_r + 0.1 from the nose path), TRIMMED at the same r_trim.

    CB_EXACT=1 python3 docs/concepts/verify/trimlug-k165-knuckle-3r.py wear <bench|held> <out.json> [--edge] [--set k=v ...]
    python3 docs/concepts/verify/trimlug-k165-knuckle-3r.py cam [--set k=v ...]      (fit bench only: base + T1-T4)
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

os.environ.setdefault("SN_CELL", "lead")
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


V = _load("slipper_verifier_for_trimlug_v", os.path.join(HERE, "slipper-nose-knuckle-3r.py"))      # the lead's verifier
TL = _load("trimlug_claim_v", os.path.join(REPO, "docs", "concepts", "models", "trimlug-k165-knuckle-3r.py"))   # loaded LAST
V.SN = TL.SN                       # TL patched its SN instance: SNModel = TLModel, _clamp / PARAMS = the claim's
H = V.H
ROW = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "trimlug-k165-knuckle-3r.json")))
BEST = ROW["best_params"]
if isinstance(BEST, str): BEST = json.loads(BEST)
V.BEST = dict(BEST)
assert V.SN.SNModel is TL.TLModel and V.SN._clamp is TL._clamp


def _rK(X, uK): return np.linalg.norm(X - (X @ uK)[:, None] * uK, axis=1)


def trim_checks(Mfit, kmax_deg):
    g = Mfit._scg; uK = g["uK"]; ti = getattr(Mfit, "_trim_info", None) or {}
    P1, Q1, N1, R0 = Mfit._flank(); rL = R0 - 1.5; r_trim = float(ti.get("r_trim", 99.0))
    kg = np.degrees(g["kgrid"][: len(Q1)])
    use = kg <= min(kmax_deg, math.degrees(g["dK_lim"])) + 1e-9
    nr = float(Mfit.D.p.get("nose_r", 1.5)); C0 = np.asarray(Mfit._viz_rod["roller"], float); cr0 = float(np.linalg.norm(C0))
    out = dict(r_trim=r_trim, rL=round(rL, 2), R0=round(R0, 2), k_used_deg=round(float(kg[use].max()), 2) if use.any() else None)
    # T1: contact line along the GH ray, read at the underside radius rL (where the trim is decided)
    rQ = _rK(Q1, uK); nQ = np.linalg.norm(Q1, axis=1)
    lines = [rQ * (nQ + z) / nQ for z in (-1.25, 0.0, 1.25)]               # r_K along the dowel's contact line
    at_rL = rQ * rL / nQ                                                     # the same ruling at the trim's own radius
    out["T1"] = dict(contact_rK_max_mid=round(float(rQ[use].max()), 3), contact_rK_max_top=round(float(lines[2][use].max()), 3),
                     contact_rK_max_at_rL=round(float(at_rL[use].max()), 3), edge_margin_at_rL=round(r_trim - float(at_rL[use].max()), 3),
                     edge_margin_full_stroke=round(r_trim - float(at_rL.max()), 3), ok=bool(r_trim - float(at_rL.max()) >= 0.5))
    # T2: back thickness behind each used contact after the trim
    ss = np.arange(0.0, 6.0 + 1e-9, 0.05); th = []
    for j in np.nonzero(use)[0]:
        Xs = Q1[j][None] + ss[:, None] * N1[j][None]; Xs = Xs / np.linalg.norm(Xs, axis=1)[:, None] * rL
        ok = _rK(Xs, uK) <= r_trim + 1e-9
        th.append(float(ss[np.argmin(ok)] if not ok.all() else 6.0))
    th = np.array(th)
    out["T2"] = dict(back_min_mm=round(float(th.min()), 2) if len(th) else None, back_at_k=round(float(kg[use][int(np.argmin(th))]), 2) if len(th) else None,
                     n_below_4mm=int((th < 4.0).sum()), n_below_3mm=int((th < 3.0).sum()), n=int(len(th)))
    # T3: connectivity of the rigid trimmed lug
    m, lug = Mfit.rigid["horn"]; tree = cKDTree(lug); pairs = tree.query_pairs(2.5)
    par = list(range(len(lug)))
    def f(a):
        while par[a] != a: par[a] = par[par[a]]; a = par[a]
        return a
    for a, b in pairs: par[f(a)] = f(b)
    comps = len({f(i) for i in range(len(lug))})
    out["T3"] = dict(horn_n=int(len(lug)), components_2p5mm=comps, rK_range=[round(float(_rK(lug, uK).min()), 2), round(float(_rK(lug, uK).max()), 2)])
    # T4: contact-only member-1 samples near the lug shell outside the trim (read at rL along the GH ray)
    bad = []
    for ci, (mm, X) in enumerate(Mfit.contact):
        if mm != 1 or not len(X): continue
        nX = np.linalg.norm(X, axis=1); shell = (nX > rL - 0.2) & (nX < rL + S_T() + 0.2)
        rr = _rK(X, uK) * rL / nX; near = shell & (rr < r_trim + 6.0) & (rr > r_trim + 0.05)
        # only samples of the lug's neighbourhood (within 3 mm of the untrimmed lug band path) count
        if near.any():
            dP = cKDTree(P1).query(X[near] / nX[near][:, None] * cr0)[0]
            nb = int((dP < 6.5 + nr).sum())
            if nb: bad.append(dict(ci=ci, n=int(len(X)), outside=nb, rK_max_at_rL=round(float(rr[near].max()), 2)))
    out["T4"] = dict(outside_trim=bad, ok=not bad)
    return out


def S_T(): return float(TL.S.T_LINK)


def dense_partpart(M, B, Mfit):
    """T5: the claim's dense lug copy (contact-only) vs every other member's rigid samples at every taken pose"""
    dense = [X for (mm, X) in M.contact if mm == 1 and len(X) == int((getattr(Mfit, "_trim_info", None) or {}).get("dense_n", -1))]
    if not dense: return dict(error="dense copy not found")
    D = dense[0]; taken = [j for j in range(len(B.idx)) if B.res[j] is not None and float(np.min(B.res[j])) >= 0]
    per = {}
    for nm, (m, X) in M.rigid.items():
        if m == 1 or not len(X): continue
        best = (99.0, None)
        for j in taken:
            d = float(cKDTree(M.world(m, j, X)).query(M.world(1, j, D))[0].min())
            if d < best[0]: best = (d, j)
        k = "%s(m%d)" % (nm, m); per[k] = dict(min_mm=round(best[0], 3), j=best[1])
    sparse = {}
    m1, lug = M.rigid["horn"]
    for nm, (m, X) in M.rigid.items():
        if m == 1 or not len(X): continue
        sparse["%s(m%d)" % (nm, m)] = round(min(float(cKDTree(M.world(m, j, X)).query(M.world(1, j, np.concatenate([lug, lug + S_T() * TL.S.unit(lug)])))[0].min()) for j in taken), 3)
    return dict(n_taken=len(taken), dense_n=int(len(D)), dense_min=per, sparse_lug_min=sparse)


_extra_lead = V.extra_checks


def extra_checks(M, Mfit, B):
    out = _extra_lead(M, Mfit, B)
    try: out["trim"] = trim_checks(Mfit, float(out.get("dK_taken_max_deg") or 0.0))
    except Exception as e: out["trim"] = dict(error=repr(e)[:400])
    if M is not Mfit:                                                   # worn bench only
        try: out["dense_partpart"] = dense_partpart(M, B, Mfit)
        except Exception as e: out["dense_partpart"] = dict(error=repr(e)[:400])
        try: out["t5"] = TL.t5(B, M)
        except Exception as e: out["t5"] = dict(error=repr(e)[:400])
    return out


def add_edge_trimmed(M):
    V.add_edge(M)                                                       # the lead verifier's flank-edge strip (rigid + top contact)
    ti = getattr(M, "_trim_info", None) or {}; r_trim = float(ti.get("r_trim", 99.0)); uK = M._scg["uK"]  # called on the fit model (M1)
    m1, lug = M.rigid["horn"]; n_e = int(M._env_info["edge_pts"]); body, edge = lug[: len(lug) - n_e], lug[len(lug) - n_e:]
    keep = _rK(edge, uK) <= r_trim + 1e-9; edge = edge[keep]
    M.rigid["horn"] = (m1, np.concatenate([body, edge]))
    M.contact[-1] = (1, edge + TL.S.T_LINK * TL.S.unit(edge)) if len(edge) else (1, np.zeros((0, 3)))
    M._env_info = dict(head_pts=0, edge_pts=int(len(edge)), edge_trimmed=int((~keep).sum()))


H.extra_checks = extra_checks
H.add_envelope = add_edge_trimmed


if __name__ == "__main__":
    sets = [a for a in sys.argv if a.startswith("--set=")]
    P = V._params(sets); nr = V.retarget(P)
    H.extra_checks = extra_checks; H.add_envelope = add_edge_trimmed
    if sys.argv[1] == "cam":
        old = os.environ.pop("CB_EXACT", None)
        B1 = CB.Bench(n_clip=60, n_ws=160); t = time.time()
        M1 = V.SN.SNModel(B1, V.SN._clamp(dict(V.SN.PARAMS, **P))); r1 = M1.run()
        ex = extra_checks(M1, M1, B1)
        print(json.dumps(dict(params=P, cls=type(M1).__name__, trim_info=getattr(M1, "_trim_info", None),
                              fit={k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")},
                              why=r1.get("why"), extra=ex, secs=round(time.time() - t, 1)), default=float)); sys.exit()
    if sys.argv[1] == "wear":
        wear, path = sys.argv[2], sys.argv[3]
        t = time.time(); out = H.frozen_wear(dict(P), wear, "--flood" in sys.argv, "--edge" in sys.argv)
        out.update(wear=wear, secs=round(time.time() - t, 1), exact=os.environ.get("CB_EXACT") == "1", params=P, sets=sets)
        json.dump(out, open(path, "w"), indent=1, default=float)
        ex = out["extra"]
        print(json.dumps(dict(wear=wear, sets=sets, edge=out["head"], env=out.get("env"), fit=out["fit_fast"]["gap"], frozen=out["frozen"],
                              near1=out["audit"].get("gap_near1"), near2=out["audit"].get("gap_near2"), minmetal=out["audit"].get("near_touch_min_mm"),
                              ovh=out["audit"].get("overhead140"), why=out["why"],
                              base={k: ex.get(k) for k in ("poses_failing", "why_failing", "corrected", "at_pa45_friction", "pa_rule", "dK_taken_max_deg")},
                              th=ex.get("th_margin"), nose=ex.get("nose"), trim=ex.get("trim"), dense=ex.get("dense_partpart"),
                              t5=({k: ex["t5"].get(k) for k in ("n", "sum_mm")} if isinstance(ex.get("t5"), dict) else None), secs=out["secs"]), default=float))
