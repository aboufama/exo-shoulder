"""minarc-stop-knuckle-4r, VARIANT B under THE KIT'S J1-J3 FOLD RULE (2026-10-16 re-optimisation after the re-measure
docs/concepts/verify/minarc-stop-knuckle-4r-remeasure.md).

The variant-B model (docs/concepts/models/minarc-stop-knuckle-4r-pinknee.py) is loaded UNCHANGED as its own module copy;
only its design class is replaced, so the claim's model keeps its reading. What changes (opt-in, `kitrule` 1 = default here):

  * the J2 hard stops are placed in the KIT's metric (tools/concept_kit.py "THE J1-J3 FOLD MARGIN"): the stops are
    parametrised by the J1-J3 fold margin at which they engage with K on stop A,
        smhi: th_hi = min(a1 + a2, 360 - a1 - a2) - smhi      (stretched stop)
        smlo: th_lo = |a1 - a2| + smlo                        (folded stop)
    and phi_hi / phi_lo are the J2 interior angles of the (a1, a2) dyad at th_hi / th_lo. smhi, smlo >= FOLD_MARGIN
    (5 deg, the user's ruling) are design variables (CLAUDE.md "treat fold stops as a design variable"), so J2 meets its
    stop BEFORE the dyad enters the forbidden band and K opens from there on: no forbidden band between state A and the
    forced states (the island the re-measure found under the claim's phi reading cannot form).
  * EVERY state keeps the kit's margin: the effective J1-J2-J3 dyad (a1e, a2) - a1e = a1 on stop A, the opened arc in
    the forced states - takes a pose only if th lies in [|a1e - a2| + m, min(a1e + a2, 360 - a1e - a2) - m]; the forced
    sub-chain J1-K-J3 keeps its own m (as before); K's dyad (bk1, bk2) keeps m over a1e in [a1, a1max] (as before).
  * `near` 1: the search objective is the NEAR-TOUCH gap (metal < 1 mm counted as contact; CLAUDE.md "Search on the
    near-touch gap"); the plain numbers are kept as *_plain.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/minarc-stop-knuckle-4r-kitrule.py [check] ['<json>']
    hooks: evaluate(B, params) -> (params, report) for tools/concept_cma.py
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
import concept_kit as KIT                                    # noqa: E402

_sp = importlib.util.spec_from_file_location("minarc_b_for_kitrule", os.path.join(HERE, "minarc-stop-knuckle-4r-pinknee.py"))
KB = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(KB)      # own module copy: patching it leaves the claim's model alone
PK, S = KB.PK, KB.S
D2R = math.pi / 180
ID = "minarc-stop-knuckle-4r"; VARIANT = "B kit rule (pin knee + knuckle, J2 stops in the J1-J3 margin metric)"
REPORT_KEYS = KB.REPORT_KEYS + ("gap_near1", "near1_poses", "min_metal_mm", "kitrule", "plain")
PARAMS = dict(KB.PARAMS, kitrule=1, smhi=8.0, smlo=8.0, near=1)


def dyad_phi(a1, a2, th):
    """J2 interior angle (deg) of the spherical dyad (a1, a2) spanning th"""
    c = (math.cos(th * D2R) - math.cos(a1 * D2R) * math.cos(a2 * D2R)) / (math.sin(a1 * D2R) * math.sin(a2 * D2R))
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def dyad_margin(th, a1, a2):
    """the kit's J1-J3 fold margin (deg) of the dyad (a1, a2) at th (arrays ok)"""
    a1 = np.asarray(a1, float)
    return np.minimum.reduce([th - np.abs(a1 - a2), np.minimum(a1 + a2, 360 - a1 - a2) - th])


class KRDesign(KB.KDesign):
    def __init__(self, params=None):
        super().__init__(params); P = self.p
        self.kitrule = bool(P.get("kitrule", 0))
        if self.kitrule:
            m = KIT.FOLD_MARGIN
            P["smhi"] = max(m, float(P.get("smhi", 8.0))); P["smlo"] = max(m, float(P.get("smlo", 8.0)))
            th_hi = min(self.a1 + self.a2, 360 - self.a1 - self.a2) - P["smhi"]; th_lo = abs(self.a1 - self.a2) + P["smlo"]
            self.stops_ok = th_lo < th_hi - 1.0
            P["phi_hi"] = dyad_phi(self.a1, self.a2, th_hi) if self.stops_ok else 170.0
            P["phi_lo"] = dyad_phi(self.a1, self.a2, th_lo) if self.stops_ok else 10.0
            P["mstop"] = 0                                    # state A is inside [th_lo, th_hi] by construction

    def ik(self, Q):
        if not hasattr(self, "uK"): return super().ik(Q)
        q, ok, X1, X2, X3, s = super().ik(Q)
        if self.kitrule:
            w = Q @ self.u[2]; th = np.degrees(np.arccos(np.clip(w @ self.u[0], -1, 1)))
            m3e = dyad_margin(th, self._a1e, self.a2); self._m3e = m3e
            ok = ok & (m3e >= KIT.FOLD_MARGIN - 1e-6) & bool(self.stops_ok)
        return q, ok, X1, X2, X3, s


KB.KDesign = KRDesign                                         # KB.KModel builds its design through this module global
KModel, KDesign = KB.KModel, KRDesign


def _report(B, params):
    p = dict(PARAMS, **params)
    for k in ("sK",): p[k] = 1 if float(p[k]) >= 0 else -1
    r, M = KB._report(B, p)
    if M.kin_ok.any():
        a = PK.audit(M, B); r["gap_near1"] = a["gap_near1"]; r["near1_poses"] = a["near1_poses"]; r["min_metal_mm"] = a["near_touch_min_mm"]
        r["overhead140"] = a["overhead140"]
    else:
        r["gap_near1"] = r["gap"]; r["near1_poses"] = 0; r["min_metal_mm"] = None
    D = M.D
    if getattr(D, "kitrule", False):
        ko = M.kin_ok; m3 = getattr(D, "_m3e", None)
        q, okk, *_ = D.ik(M.Q); m3 = D._m3e
        r["kitrule"] = dict(phi_lo=round(D.p["phi_lo"], 2), phi_hi=round(D.p["phi_hi"], 2), smlo=round(D.p["smlo"], 2), smhi=round(D.p["smhi"], 2),
                            a_deg=[round(D.a1, 2), round(D.a2, 2)], min_margin_taken=round(float(m3[ko].min()), 2) if ko.any() else None)
    r["plain"] = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "contact")}
    if p.get("near"): r["gap"] = r["gap_near1"]
    return r, M


def evaluate(B, params):
    r, M = _report(B, params); p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); return r


if __name__ == "__main__":
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report(B, par)
    print({k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}, "plain", r["plain"], "near1", r["gap_near1"],
          "kitrule", r.get("kitrule"), "why", r["why"], "knuckle", r.get("knuckle"), f"{time.time() - t:.0f}s", B.mode)
