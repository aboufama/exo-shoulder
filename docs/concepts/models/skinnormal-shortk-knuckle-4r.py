"""skinnormal-shortk-knuckle-4r: near-touch-robust redundant 4R (Keemink layout, determined spare).

pick1's verified sensed-knuckle 4R (minarc-stop-knuckle-4r, 18.40 frozen Bench(110,360) exact) with only the knuckle and the
seats moved. The chain, scapula -> cuff:

  J1 (ACTIVE R, O20, bvec(az1, el1), sensed) -> link 1a (arc bk1) -> K (ACTIVE R, SENSED; clock spring preloaded onto stop A,
  stop B at dK_B) -> link 1b (arc bk2) -> J2 (ACTIVE R, O20; own-angle q2 dowel stops at smhi / smlo deg of J1-J3 margin)
  -> link 2 -> J3 (ACTIVE R, O20, wdir(wd, wa), tilt b3) -> member 3 -> pin knee (2 PASSIVE pins, closed by the cuff) -> cuff.
  4 active, 2 passive rotations, 0 passive translations; no gears, pulleys or cables.

The physics is pick1's verified harness, imported UNCHANGED: docs/concepts/models/minarc-stop-knuckle-4r-kitrule.py
(KRDesign phys 1: J2 stopped on its own angle q2, K opens in closed form past it; kit J1-J3 fold margin in every state;
capK 6 mm clock-spring cap; near 1 = metal < 1 mm counted as contact; the seed's VModel checks through the pin-knee model).
What this file adds:
  * the search coordinates of the catalogue sweep: rest arcs a1 / a2 replace az2 / el2 (J2's seat is SOLVED from the arcs
    with the design's own J1 / J3 seats by a 2-D Newton on KRDesign's arcs - never searched directly);
  * the judge's built-stop PRICING before any number (tools/env_polish.priced: J2 slots +0.5 deg read at CB_FOLD_MARGIN 5.5,
    stop B cut where the 5-deg rule refuses the stretched branch);
  * dK_B (the stop-B opening, deg) as a search coordinate: a1max is derived from it on the K dyad (bk1, bk2).

    CB_FOLD_MARGIN=5.5 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/skinnormal-shortk-knuckle-4r.py ['<json>']
    hooks: bench_eval(B, params) -> report (tools/concept_sweep.py), evaluate(B, params) -> (params, report)
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import env_polish as EP                                      # noqa: E402  (installs env poses first, as the verifier does)
CB, KIT = EP.CB, EP.KIT

_sp = importlib.util.spec_from_file_location("kr_for_shortk", os.path.join(HERE, "minarc-stop-knuckle-4r-kitrule.py"))
KR = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(KR)
D2R = math.pi / 180
ID = "skinnormal-shortk-knuckle-4r"

# pick1's priced base (pin knee lE / lc / phiE / phib / stk / ang_min unchanged) + the skinnormal seed, UNROUNDED (the judge's
# reproduction: 11.38 = near1 nominal, 12.49 priced on Bench(60,160) fast). Stops / a1max NOMINAL: bench_eval prices them.
BASE = dict(KR.PARAMS, phys=1, kitrule=1, m3e=1, near=1, capK=6.0, sK=-1, lE=73.8692, lc=28.6946, phiE=1.3552, phib=-53.1496,
            stk=5.791, ang_min=26.1449, rad1=10.0, rad2=10.0, rad3=10.0, phi_lo=15.0, phi_hi=170.0, mstop=0,
            az1=94.89664439400039, el1=68.01689176746288, az2=46.34803263767242, el2=43.1622595328811, wd=66.2812831334182,
            wa=-9.540248426114447, b3=0.3653366568878202, bk1=29.652730536136104, bk2=40.7017002497022, a1max=65.3544307858383,
            smhi=10.826, smlo=6.4468)
PARAMS = dict(BASE)
SEEDS = {
    "skinnormal": {},
    "stopb80": dict(az1=101.6411, el1=67.8564, az2=45.91, el2=43.22, wd=66.5965, wa=-9.6278, b3=0.4, bk1=32.0, bk2=52.0, a1max=75.5,
                    smhi=7.377, smlo=7.3286),
    # az2 = el2 = 42.70 is NOT a copy slip: KRDesign gives rest arcs 40.78 / 59.45 = the proposer's 40.8 / 59.4
    "earlystop": dict(az1=105.29, el1=65.9, az2=42.7, el2=42.7, wd=65.01, wa=-12.08, b3=0.37, bk1=37.71, bk2=37.44, a1max=70.15,
                      smhi=15.96, smlo=6.99),
}


def arcs(P):
    D = KR.KRDesign(dict(P)); return D.a1, D.a2


def solve_seat(P, a1, a2, it=12):
    """(az2, el2) giving rest arcs (a1, a2) with the design's own J1 / J3 seats: Newton from P's own (az2, el2)"""
    x = np.array([float(P["az2"]), float(P["el2"])])
    for _ in range(it):
        Q = dict(P, az2=x[0], el2=x[1]); f = np.array(arcs(Q)) - [a1, a2]
        if np.abs(f).max() < 1e-4: break
        J = np.zeros((2, 2)); h = 1e-3
        for j in range(2):
            dx = np.zeros(2); dx[j] = h; J[:, j] = (np.array(arcs(dict(P, az2=x[0] + dx[0], el2=x[1] + dx[1]))) - [a1, a2] - f) / h
        step = np.linalg.lstsq(J, -f, rcond=None)[0]; s = np.abs(step).max()
        x = x + (step if s < 8 else step * 8 / s)
    return float(x[0]), float(x[1]), float(np.abs(f).max())


def a1max_from_dKB(P, dKB):
    """a1max (deg) whose stop-B opening is dKB (deg) on the K dyad (bk1, bk2): a1e(psiA + dKB)"""
    D = KR.KRDesign(dict(P)); b1, b2 = float(P["bk1"]) * D2R, float(P["bk2"]) * D2R
    c = math.cos(b1) * math.cos(b2) + math.sin(b1) * math.sin(b2) * math.cos(abs(D.psiA) + dKB * D2R)
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def full(params):
    """nominal design from search coordinates (a1 / a2 -> az2 / el2; dKB -> a1max); returns (P, info)"""
    p = dict(params); seed = p.pop("seed", None); info = {}
    P = dict(BASE, **SEEDS.get(seed, {})) if seed else dict(BASE)
    a1 = p.pop("a1", None); a2 = p.pop("a2", None); dKB = p.pop("dKB", None)
    P.update({k: v for k, v in p.items() if not k.startswith("_")})
    if a1 is not None or a2 is not None:
        A1, A2 = arcs(P); a1 = A1 if a1 is None else float(a1); a2 = A2 if a2 is None else float(a2)
        az2, el2, res = solve_seat(P, a1, a2); P.update(az2=az2, el2=el2); info["seat"] = dict(az2=round(az2, 4), el2=round(el2, 4), res=res)
    if dKB is not None:
        P["a1max"] = a1max_from_dKB(P, float(dKB)); info["a1max_nominal"] = round(P["a1max"], 4)
    return P, info


def _report(B, params):
    P, info = full(params)
    if os.environ.get("SK4R_NOPRICE") == "1": Pp, pinfo = dict(P), dict(why="unpriced")
    else: Pp, pinfo = EP.priced(KR, P)
    r, M = KR._report(B, Pp)
    D = M.D; r["arcs"] = [round(D.a1, 3), round(D.a2, 3)]; r["price"] = pinfo; r["solve"] = info
    r["priced_params"] = {k: v for k, v in Pp.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return r, M


def evaluate(B, params):
    r, M = _report(B, params); return r["priced_params"], r


def bench_eval(B, params):
    r, M = _report(B, {k: v for k, v in params.items() if k not in BASE or v != BASE[k]})
    r.pop("params", None); return r


if __name__ == "__main__":
    par = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report(B, par)
    print(json.dumps({k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "plain", "gap_near1", "min_metal_mm",
                                            "why", "arcs", "price", "solve", "overhead140")}, default=float), f"{time.time() - t:.0f}s", B.mode)
