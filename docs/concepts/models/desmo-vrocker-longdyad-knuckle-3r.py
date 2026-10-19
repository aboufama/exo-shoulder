"""desmo-vrocker-longdyad-knuckle-3r (round 12, pick 4): the long 32/48 K dyad driven by a desmodromic V-rocker.

Morphology (docs/concepts/desmo-vrocker-longdyad-knuckle-3r.md): scapula handler -> J1 (ACTIVE, O20) -> link 1a (bk1 32)
-> K (PASSIVE, slaved) -> link 1b (bk2 48) -> J2 (ACTIVE, O20) -> link 2 -> J3 (ACTIVE, O20) -> member 3 -> two-pin knee
-> arm pad. K is slaved to q2 by a crank on link 1b (MR63ZZ pair): stage 1 = two conjugate open lobes on hub 2's cap ring
riding two crowned pins on the crank's V short arm (each lobe pushes its pin outward; together they hold the crank both
ways); stage 2 = a nose dowel on link 1a in a swept slot in the crank tip (the pinned-horn inversion). No spring, roller,
rod or ball link. 3 ACTIVE DOF, 0 passive translations.

WHAT THIS FILE MODELS (and what it does not):
  * the chain, K dyad, knee, seats and law are spiral-lobe-longdyad-knuckle-3r.py's (loaded UNCHANGED; it loads
    inband-rssr-knuckle-3r.py unchanged), switched to the V-rocker's cell: 32/48, stop B a1max <= bk1 + bk2 - 5.5 = 74.5,
    a linear law kK 2.5 past the onset margin smhi;
  * the RSSR of the parent does not exist in this morphology: its metal is deleted (IB_GHOST=all) and its range limiter
    (transmission / rod clearances) is REPLACED by the V-rocker's own stroke: dK_lim = min(kcap, s2cap), kcap = the
    conjugate-lobe pair's stroke (judge: 56 robust, 60 / 64 knife-edge at PA 36.4 / 37.9 vs 38.03), s2cap = the re-seated
    pinned-horn slot's stroke on 32/48 (judge, round12_ideation.md section 4: 78.5);
  * the V-rocker's OWN metal (V arm, two pins, two stacked lobe tracks on hub 2's cap ring, slotted crank plate, nose
    boss on link 1a) is NOT sampled. Every number from this file is therefore a GHOST (the chain's ceiling before the
    drive's metal), the round-12 judge's gate 3 for this row - never a claim. The drive can only add metal.

    IB_GHOST is forced to 'all' here.
    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/desmo-vrocker-longdyad-knuckle-3r.py [check] ['<json>']
    CB_EXACT=1 ... frozen '<json>' [out.json]      (fit Bench(60,160) fast, shape frozen, worn on Bench(110,360) exact)
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np

os.environ["IB_GHOST"] = "all"                               # the parent's RSSR is not part of this morphology
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

_sp = importlib.util.spec_from_file_location("spiral_for_vrocker", os.path.join(HERE, "spiral-lobe-longdyad-knuckle-3r.py"))
SLm = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(SLm)
IB, LS, SC, FL, S = SLm.IB, SLm.LS, SLm.SC, SLm.FL, SLm.S
D2R = math.pi / 180
ID = "desmo-vrocker-longdyad-knuckle-3r"
GHOST = IB.GHOST
GHOST_ONLY = True                                            # the V-rocker's own metal is not sampled: every number is a ghost
# the cell: spiral-lobe's chain (pick3's seats, knee, placement) on 32/48, stop B 74.5, linear kK 2.5 (the judge's V-rocker cell)
SEED = dict(SLm.SEED, bk1=32.0, bk2=48.0, a1max=74.5, kK=2.5, smhi=16.84)
PARAMS = dict(SLm.PARAMS, **SEED); PARAMS.update(law_in="lin", kcap=56.0, s2cap=78.5)
_sl_clamp = SLm._clamp


def _clamp(p):
    kcap = p.get("kcap", 56.0); s2cap = p.get("s2cap", 78.5)
    p = _sl_clamp(p)
    p["kcap"] = min(max(float(kcap if kcap is not None else 56.0), 0.0), 90.0)
    p["s2cap"] = min(max(float(s2cap if s2cap is not None else 78.5), 0.0), 90.0)
    return p


class VRModel(SLm.SLModel):
    """the spiral-lobe chain with the V-rocker's stroke as the drive's range (RSSR limiter replaced, RSSR metal deleted)"""
    def _rod_metal(self):
        super()._rod_metal()
        g = getattr(self, "_scg", None)
        if g is None: return
        P = self.D.p
        lim_deg = min(float(P.get("kcap", 56.0)), float(P.get("s2cap", 78.5)))
        why = "conj_lobes" if float(P.get("kcap", 56.0)) <= float(P.get("s2cap", 78.5)) else "slot"
        info = getattr(self, "_sc_info", None) or {}
        info["dK_lim_rssr_ignored"] = info.get("dK_lim"); info["why_lim_rssr_ignored"] = info.get("why_lim")
        g["dK_lim"] = math.radians(lim_deg); g["why_lim"] = why
        info["dK_lim"] = round(lim_deg, 1); info["why_lim"] = why; info["vr_ghost"] = True
        self._sc_info = info


LS.LSModel = VRModel; LS._clamp = _clamp; LS.PARAMS = PARAMS
SC.SCModel = VRModel; SC._clamp = _clamp; SC.PARAMS = PARAMS; LS.RF.PARAMS = PARAMS; LS.BM.PARAMS = PARAMS
FL.G.KR.KB.KModel = VRModel; FL.FLModel_SC = VRModel
IB._clamp = _clamp; IB.PARAMS = PARAMS; SLm._clamp = _clamp; SLm.PARAMS = PARAMS
_report = LS._report; _frozen_model = LS._frozen_model; frozen = LS.frozen; frozen_held = LS.frozen_held; frozen_flood = LS.frozen_flood
viz_export = LS.viz_export


def evaluate(B, params):
    p, r = IB.evaluate(B, params); r["ghost"] = True; return p, r


def bench_eval(B, params):
    r = IB.bench_eval(B, params); r["ghost"] = True; return r


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "viz":
        print(json.dumps(viz_export(par), default=float)); sys.exit()
    if mode in ("frozen", "held", "flood"):
        t = time.time(); out = {"frozen": frozen, "held": frozen_held, "flood": frozen_flood}[mode](par); out["params"] = par
        out["row"] = ID; out["ghost"] = "V-rocker metal not sampled; RSSR deleted"; out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        print(json.dumps(dict(row=ID, fit=out.get("fit_fast"), frozen=out["frozen"], why=out.get("why"), ovh=out.get("overhead"),
                              cam=out.get("cam"), secs=out["secs"]), default=float)); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report(B, par)
    info = getattr(M, "_sc_info", None) or {}
    print(json.dumps(dict(row=ID, ghost=True, gap=r["gap"], reach=r["reach"], follow=r["follow"], inband14=r["inband14"], inband10=r["inband10"],
                          contact=r["contact"], honest=r.get("honest"), why=r.get("why"), ovh=r.get("overhead140"),
                          dK_lim=info.get("dK_lim"), why_lim=info.get("why_lim"),
                          law={k: v for k, v in M.D.law().items() if isinstance(v, (int, float, str)) or v is None}, secs=round(time.time() - t)),
                     default=float))
