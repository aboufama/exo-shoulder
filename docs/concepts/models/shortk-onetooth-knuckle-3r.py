"""shortk-onetooth-knuckle-3r (round 107, cell B 'just outside the O20 rim': move K, not the law): the verified lead
conecut-knee-knuckle-3r (seats, knee, J3 dowel stop, O20 stacks, part pairs, near-touch rules loaded UNCHANGED) with its K
dyad RE-SEATED from bk1 / bk2 26 / 38.03 to 34 / 30 (J1 and J2 seats unchanged, so the rest arc a1 = 37.55 and the K = 0
chain are the lead's) and its two-stage K drive replaced by ONE higher pair (a crowned pin on link 1a's horn pushed by one
link-2 tooth flank, held by the lead's clock spring + stop A) at a law rho = dK / d(-q2) ~ 1.05-1.1.

Built on docs/concepts/models/onetooth-slowlaw-knuckle-3r.py (its ghost cell and its exact built-flank check `flank()` are
reused unchanged); this file changes three things:

  (1) THE DYAD. The lead's parent clamps (roller-longdyad: bk1 in [26, 32], bk2 in [38, 48]) are SEARCH BOUNDS of an older
      morphology, not physics: bk1 / bk2 are restored after the chain clamp, with the K dyad's own fold rule enforced here
      (|bk1 - bk2| + 5 <= a1 at rest, a1e at the drive's end <= bk1 + bk2 - 5).
  (2) THE ANCHOR. The law is anchored on the lead's END STATE, not on the lead's K value: the K that gives the lead's end
      arc a1e = 54.27 (lead K 45.62) is reached at the lead's end th (106.3 on the lead's own kinematics, read here from
      the lead's dyad, never typed in); onset th_on solved on the new dyad's exact spherical kinematics
      th(q2, K) = angle(u1, R(uK, sp K) R(u2, q2) u3).
  (3) THE STRETCHED WALL (DKCAP caps it at the built one-pair drive range from `flank` - the buildable bound). The drive range DKLIM is the K that gives the lead's stretched arc a1e(K = 50 on the lead's dyad)
      = 55.52 (WALL=lead, default), or the spec's a1max 58.77 (WALL=a1max; K dyad then 5.23 deg from its own stretch).

CELLS (env OT_CELL, as the parent): ghost (STEP 0, default: every drive part deleted, a BOUND for this morphology).

DOF: 3 ACTIVE (J1, J2, J3 encoded), K slaved (passive R, determined by the law), knee pins outside the count, 0 passive
translations. No gears / pulleys / cables (MVP1).

    OT_CELL=ghost OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/shortk-onetooth-knuckle-3r.py [check] ['<json>']
    ... wear <envsel|bench|held> '<json>' [out.json]      ... flank '<json>' '<flank kw json>'      ... law '<json>'
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np

os.environ.setdefault("OT_CELL", "ghost")
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
_sp = importlib.util.spec_from_file_location("onetooth_for_shortk", os.path.join(HERE, "onetooth-slowlaw-knuckle-3r.py"))
OT = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(OT)
CC, SN, SC, FL, S, CB = OT.CC, OT.SN, OT.SC, OT.FL, OT.S, OT.CB
ID = "shortk-onetooth-knuckle-3r"
LEAD_DYAD = (26.0, 38.0336)
LEAD_K_END, LEAD_DKLIM = 45.62, 50.0                         # the lead's end-state K and its fitted drive range (deg)
LEADP = dict(OT.PARAMS); _OT_CLAMP = OT._clamp                # the lead's parameters and the parent's clamp (lead dyad)
PARAMS = dict(OT.PARAMS); PARAMS.update(bk1=34.0, bk2=30.0, rho=1.1, WALL="lead")
_cache = {}


def _geo(bk1, bk2):
    """exact spherical kinematics of the lead's K = 0 chain with K seated at (bk1, bk2); same convention as the model's law"""
    key = (round(bk1, 6), round(bk2, 6))
    if key in _cache: return _cache[key]
    p = CC._clamp(dict(LEADP, rho=2.1534)); p["bk1"], p["bk2"] = float(bk1), float(bk2)
    p["kK"] = OT.LEAD_K; p["smhi"] = SN.LEAD_BEST["smhi"]
    D = FL.G.KR.KB.KDesign(p)
    u1, u2, u3 = D.u; uK = D.uK; spn = float(np.sign(D.psiA)) or 1.0

    def a1e(k): return np.degrees(np.arccos(np.clip(np.einsum("nij,j->ni", S.rotm(uK, spn * np.radians(np.atleast_1d(k))), u2) @ u1, -1, 1)))

    def th(q2, k):
        R = S.rotm(uK, spn * np.radians(np.atleast_1d(k))); R2 = S.rotm(u2, np.atleast_1d(q2))
        return np.degrees(np.arccos(np.clip(np.einsum("nij,nj->ni", R, np.einsum("nij,j->ni", R2, u3)) @ u1, -1, 1)))
    ks = np.arange(0.0, 90.0, 0.01); A = a1e(ks); im = int(np.argmax(A))

    def k_at(a): return float(np.interp(a, A[:im + 1], ks[:im + 1]))
    out = dict(D=D, a1e=a1e, th=th, k_at=k_at, a1=D.a1, a2=D.a2, A_max=float(A.max()), A=D._q2c)
    _cache[key] = out; return out


def anchor():
    """the lead's end state on the lead's own kinematics: a1e at K 45.62, th there, a1e at the lead's wall K = 50"""
    if "anchor" in _cache: return _cache["anchor"]
    G = _geo(*LEAD_DYAD)
    p = CC._clamp(dict(LEADP)); p.update(rho=OT.LEAD_K, kK=OT.LEAD_K, kA=OT.LEAD_K, kB=OT.LEAD_K, smhi=SN.LEAD_BEST["smhi"], DKLIM=LEAD_DKLIM)
    p["t_end"] = max(float(p.get("t_end", 75.0)), LEAD_DKLIM / OT.LEAD_K + 2.0); D = FL.G.KR.KB.KDesign(p); D.q2sgn = -1.0
    L = D.law(); q2hi, s_q = float(L["q2hi"]), float(L["s_q"])
    q2e = q2hi + s_q * math.radians(LEAD_K_END / OT.LEAD_K)
    th_end = float(G["th"](q2e, LEAD_K_END)[0])
    out = dict(a1e_end=float(G["a1e"](LEAD_K_END)[0]), th_end=th_end, a1e_wall=float(G["a1e"](LEAD_DKLIM)[0]), s_q=s_q, q2hi_lead=q2hi,
               th_on_lead=float(D.th_hi))
    _cache["anchor"] = out; return out


def law_for(P):
    """onset (smhi) and drive range (DKLIM) for (bk1, bk2, rho, WALL): K reaches the lead's end arc at the lead's end th"""
    bk1, bk2, rho = float(P["bk1"]), float(P["bk2"]), float(P["rho"])
    key = ("law", round(bk1, 6), round(bk2, 6), round(rho, 6), str(P.get("WALL", "lead")))
    if key in _cache: return _cache[key]
    an = anchor(); G = _geo(bk1, bk2); s_q = an["s_q"]
    k_end = G["k_at"](an["a1e_end"])
    from scipy.optimize import brentq
    # q2 at the end state: th(q2, k_end) = th_end on the branch the lead's law runs (q2 decreasing past the onset, s_q)
    qs = np.radians(np.arange(-120.0, 120.0, 0.25)); ths = G["th"](qs, np.full(len(qs), k_end)) if False else np.array([G["th"](q, k_end)[0] for q in qs])
    f = ths - an["th_end"]; cand = [i for i in range(len(qs) - 1) if f[i] * f[i + 1] < 0]
    q2e = None
    for i in cand:                                           # the root nearest the lead's end q2 (same branch)
        r = brentq(lambda q: G["th"](q, k_end)[0] - an["th_end"], qs[i], qs[i + 1], xtol=1e-10)
        ref = an["q2hi_lead"] + s_q * math.radians(LEAD_K_END / OT.LEAD_K)
        if q2e is None or abs(r - ref) < abs(q2e - ref): q2e = r
    q2on = q2e - s_q * math.radians(k_end / rho)
    th_on = float(G["th"](q2on, 0.0)[0]); s12 = min(G["a1"] + G["a2"], 360 - G["a1"] - G["a2"])
    wall = an["a1e_wall"] if str(P.get("WALL", "lead")) == "lead" else float(P.get("a1max", 58.7678))
    dkl = G["k_at"](min(wall, bk1 + bk2 - 5.0))
    out = dict(k_end=k_end, q2_end=math.degrees(q2e), q2_on=math.degrees(q2on), th_on=th_on, smhi=s12 - th_on, DKLIM=dkl, a1e_wall=wall,
               kdyad_margin_wall=bk1 + bk2 - wall, kdyad_margin_rest=G["a1"] - abs(bk1 - bk2), th_end=an["th_end"], a1e_end=an["a1e_end"])
    _cache[key] = out; return out


def _clamp(p):
    b1 = min(max(float(p.get("bk1", 34.0)), 20.0), 45.0); b2 = min(max(float(p.get("bk2", 30.0)), 20.0), 45.0)
    rho = min(max(float(p.get("rho", 1.1)), 0.5), 4.0); wall = str(p.get("WALL", "lead"))
    p = CC._clamp(p)                                         # the lead's chain clamp (it clamps bk1 / bk2 to an old search box)
    p["bk1"], p["bk2"], p["rho"], p["WALL"] = b1, b2, rho, wall   # restored: the re-seat IS this morphology
    L = law_for(p)
    p["kK"] = p["kA"] = p["kB"] = rho
    p["smhi"] = round(L["smhi"], 6); p["DKLIM"] = round(L["DKLIM"], 6)
    if p.get("DKCAP") is not None: p["DKLIM"] = min(p["DKLIM"], max(float(p["DKCAP"]), 5.0))   # the BUILT pair's drive range
    p["a1max"] = min(float(p.get("a1max", 58.7678)), b1 + b2 - 5.0)
    p["t_end"] = max(float(p.get("t_end", 75.0)), p["DKLIM"] / rho + 2.0)
    p["kdyad_ok"] = int((abs(b1 - b2) + 5.0 <= _geo(b1, b2)["a1"] + 1e-9) and (L["a1e_wall"] <= b1 + b2 - 5.0 + 1e-9))
    return p


def _smhi_report(P):
    L = law_for(P); G = _geo(float(P["bk1"]), float(P["bk2"]))
    return dict(smhi=L["smhi"], th_on=L["th_on"], th_hi_lead=anchor()["th_on_lead"], a1=G["a1"], a2=G["a2"])


OT._clamp = _clamp; SC._clamp = _clamp; OT.PARAMS = PARAMS; OT.smhi_for = _smhi_report


def kdyad_margin(M):
    """K's own dyad margin (deg) over the taken poses: min(bk1 + bk2 - a1e, a1e - |bk1 - bk2|)"""
    P = M.p; G = _geo(float(P["bk1"]), float(P["bk2"]))
    dK = np.degrees(np.abs(np.asarray(M.dK, float)))
    a = G["a1e"](dK)
    m = np.minimum(float(P["bk1"]) + float(P["bk2"]) - a, a - abs(float(P["bk1"]) - float(P["bk2"])))
    return m


def wear(P, bench="envsel"):
    out, M, B = OT.wear(dict(PARAMS, **P), bench)
    kind = np.array(B.kind)
    taken = np.array([B.res[j] is not None and float(np.min(B.res[j])) >= 0 for j in range(len(B.idx))])
    m = kdyad_margin(M)
    out["kdyad_margin_min_taken"] = round(float(m[taken].min()), 3) if taken.any() else None
    out["law_shortk"] = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in law_for(_clamp(dict(PARAMS, **P))).items()}
    out["id"] = ID
    return out, M, B


def bench_eval(B, params):
    r, M = OT._report(B, dict(PARAMS, **params)); r.pop("params", None); return r


def evaluate(B, params):
    r, M = OT._report(B, dict(PARAMS, **params))
    if r.get("sidecar_fail") or r.get("drive_idle") or r.get("pa_fail") or r.get("knee_moved"): r["honest"] = False
    p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def flank(P=None, **kw):
    """the parent's exact built-flank check of the one pair on THIS dyad and law (pin r0 mm from u2, az0 deg from K about u2)"""
    old = OT._clamp
    try:
        OT._clamp = _clamp; return OT.flank(dict(PARAMS, **(P or {})), **kw)
    finally: OT._clamp = old


def viz_export(par): return CC.viz_export(_clamp(dict(PARAMS, **par)))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[3] if mode == "wear" and len(sys.argv) > 3 else (sys.argv[2] if len(sys.argv) > 2 and mode != "wear" else "{}"))
    if mode == "wear":
        bench = sys.argv[2]; t = time.time(); out, M, B = wear(par, bench); out["params"] = par; out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 4: json.dump(out, open(sys.argv[4], "w"), indent=1, default=float)
        print(json.dumps({k: out.get(k) for k in ("cell", "bench", "fit_fast", "frozen", "why", "near1", "near2", "min_metal", "ws_taken", "n_ws", "ws_contact",
                                                   "overhead", "K_open", "law_shortk", "kdyad_margin_min_taken", "contact_poses", "secs")}, default=float))
        sys.exit()
    if mode == "law":
        print(json.dumps(dict(anchor=anchor(), law=law_for(_clamp(dict(PARAMS, **par)))), default=float)); sys.exit()
    if mode == "flank":
        kw = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        print(json.dumps(flank(par, **kw), default=float)); sys.exit()
    if mode == "viz":
        print(json.dumps(viz_export(par), default=float)); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = OT._report(B, dict(PARAMS, **par))
    print(json.dumps(dict(cell=OT.CELL, gap=r["gap"], near1=r.get("gap_near1"), near2=r.get("gap_near2"), reach=r["reach"], follow=r["follow"],
                          inband14=r["inband14"], contact=r["contact"], honest=r.get("honest"), why=r.get("why"), ovh=r.get("overhead140"),
                          law=r.get("law"), secs=round(time.time() - t, 1)), default=float))
