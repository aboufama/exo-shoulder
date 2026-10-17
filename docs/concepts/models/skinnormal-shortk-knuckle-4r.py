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
KMARGIN = 5.5                                                # K-dyad margin at stop B, the priced reading
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
    # REPAIR (measured 2026-10-17): the K dyad (bk1, bk2) must keep the margin read at CB_FOLD_MARGIN 5.5 (the verifier's
    # priced reading) at stop B: a1max <= bk1 + bk2 - 5.5. The skinnormal seed drew stop B at a1max 65.35 (priced 64.95)
    # > 70.35 - 5.5 = 64.85, so at 5.5 KRDesign.k_ok is False and EVERY pose is refused (gap 275); stop B is drawn 0.1 deg
    # earlier instead (dK_B 75.84 -> ~75.6).
    cap = float(P["bk1"]) + float(P["bk2"]) - KMARGIN - 0.01
    if float(P["a1max"]) > cap: info["a1max_capped"] = [round(float(P["a1max"]), 4), round(cap, 4)]; P["a1max"] = cap
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


def viz_export(params):
    """geometry of the fitted design (Bench(60,160)) for docs/concepts/viz/concepts/skinnormal-shortk-knuckle-4r.js (same G
    layout as minarc-stop-knuckle-4r.js: axes, hub levels, knee frames, q2 stops, strap centrelines in member frames)"""
    B = CB.Bench(n_clip=60, n_ws=160); r, M = _report(B, params); D = M.D; P = D.p; S = KR.S
    def line(nm, k=18):
        pts = np.asarray(M.link_pts.get(nm, (0, np.zeros((0, 3))))[1], float)
        if not len(pts): return []
        a = pts[:, :1] * 0; d = pts - pts.mean(0); ax = np.linalg.svd(d, full_matrices=False)[2][0]; t = d @ ax
        bins = np.linspace(t.min(), t.max(), k + 1); out = []
        for j in range(k):
            sel = (t >= bins[j]) & (t <= bins[j + 1])
            if sel.any(): out.append([round(float(x), 2) for x in pts[sel].mean(0)])
        return out
    fr = M.fr; cb = lambda x: math.cos(x * D2R)
    b1, b2 = float(P["bk1"]) * D2R, float(P["bk2"]) * D2R
    cps = (math.cos(float(P["a1max"]) * D2R) - math.cos(b1) * math.cos(b2)) / (math.sin(b1) * math.sin(b2))
    G = dict(u=[[round(float(x), 5) for x in v] for v in D.u], uK=[round(float(x), 5) for x in D.uK], c=[[round(float(x), 5) for x in v] for v in D.c],
             sa=[round(float(x), 5) for x in D.sa], st=[round(float(x), 5) for x in D.st], sn=[round(float(x), 5) for x in D.sn],
             A=[round(D.a1, 3), round(D.a2, 3)], branch=float(getattr(D, "q2sgn", 1.0) or 1.0), m=[round(float(x), 5) for x in D.m],
             f=[round(float(x), 2) for x in M.f], fK=round(float(M.fK), 2), capK=float(P.get("capK", 0)), tr=round(float(M.tr), 2), tp=round(float(P["tp"]), 3),
             RUN=S.RUN, SING=S.SING, hr=[float(x) for x in M.hr], A0=[round(float(x), 5) for x in fr["A0"]], A0m=[round(float(x), 5) for x in fr["A0m"]],
             Bm=[round(float(x), 5) for x in fr["Bm"]], eE=[round(float(x), 5) for x in fr["eE"]], eK=[round(float(x), 5) for x in fr["eK"]],
             psiA=round(math.degrees(D.psiA), 4), dKB=round(math.degrees(abs(math.acos(max(-1, min(1, cps))) - abs(D.psiA))), 4),
             thLo=round(D.th_lo, 4), thHi=round(D.th_hi, 4), q2s=[round(float(x), 4) for x in D.q2_stops],
             L1a=line("L1a", 3), L1b=line("L1b", 7), L2=line("L2", 18))
    keys = ("az1", "el1", "az2", "el2", "wd", "wa", "b3", "lE", "lc", "phiE", "phib", "stk", "ang_min", "bk1", "bk2", "sK", "a1max", "smlo", "smhi", "capK")
    return dict(P={k: round(float(P[k]), 4) for k in keys}, G=G, report={k: r[k] for k in ("gap", "reach", "follow", "inband14", "contact")},
                links=sorted(M.link_pts))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "viz":
        print(json.dumps(viz_export(json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}), default=float)); sys.exit()
    par = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report(B, par)
    print(json.dumps({k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "plain", "gap_near1", "min_metal_mm",
                                            "why", "arcs", "price", "solve", "overhead140")}, default=float), f"{time.time() - t:.0f}s", B.mode)
