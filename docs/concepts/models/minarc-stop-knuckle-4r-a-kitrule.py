"""minarc-stop-knuckle-4r, VARIANT A (plain spherical chain + spring knuckle, complexity 13.5) under THE KIT'S J1-J3 FOLD
RULE (2026-10-16 re-optimisation after docs/concepts/verify/minarc-stop-knuckle-4r-remeasure.md).

Variant A's model (docs/concepts/models/minarc-stop-knuckle-4r.py) is loaded UNCHANGED as its own module copy; its law
read the fold as a J2 interior-angle clamp phi in [m, 180 - m] (its screened best, phi_hi 166.89 with a1 42.99 / a2 70.31,
puts the stretched stop at 1.04 deg of J1-J3 margin). Here (as in minarc-stop-knuckle-4r-kitrule.py for variant B):

  * stops parametrised in the kit's metric: smhi / smlo = the J1-J3 fold margin (deg, >= FOLD_MARGIN, design variables)
    at which J2 meets its stretched / folded stop with K on stop A; phi_hi / phi_lo derived from (a1, a2);
  * every state keeps the kit's margin: the effective dyad (a1e, a2) needs th in [|a1e - a2| + m, min(a1e + a2,
    360 - a1e - a2) - m] (+ the forced sub-chain J1-K-J3 and K's own range, as before);
  * `near` 1 (default): the search objective is the near-touch gap;
  * `frozen` mode: fit Bench(60,160) fast -> wear Bench(110,360) (CB_EXACT=1) or the pin knee's held-out bench, frozen
    profiles, with the WORKSPACE CONTINUITY flood fill (CLAUDE.md "Reach must be reachable by moving": 2-deg slerp edges
    over the full 1432-pose workspace grid, no joint among J1 / K / J2 / J3 stepping > 10 deg, seeds at elevation 0 with
    K on stop A) applied: reach on the connected set only.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/minarc-stop-knuckle-4r-a-kitrule.py check '<json>'
    CB_EXACT=1 python3 docs/concepts/models/minarc-stop-knuckle-4r-a-kitrule.py frozen '<json>' <bench|held> out.json
"""
import functools, importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial.transform import Rotation as Rot, Slerp

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
import concept_kit as K                                      # noqa: E402

_sp = importlib.util.spec_from_file_location("minarc_a_for_kitrule", os.path.join(HERE, "minarc-stop-knuckle-4r.py"))
KA = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(KA)
SP = KA.SP; D2R = math.pi / 180
ID = "minarc-stop-knuckle-4r"; VARIANT = "A kit rule"
PARAMS = dict(KA.PARAMS, smhi=8.0, smlo=8.0, near=1, phys=0, capK=0.0)
REPORT_KEYS = KA.REPORT_KEYS + ("kitrule", "plain")
STEP, JUMP = 2.0, 10.0


def dyad_phi(a1, a2, th):
    c = (math.cos(th * D2R) - math.cos(a1 * D2R) * math.cos(a2 * D2R)) / (math.sin(a1 * D2R) * math.sin(a2 * D2R))
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def stops(p):
    """-> p with phi_lo / phi_hi derived from the kit-metric stop margins (and stops_ok)"""
    p = dict(p); m = K.FOLD_MARGIN; a1, a2 = float(p["a1"]), float(p["a2"])
    p["smhi"] = max(m, float(p["smhi"])); p["smlo"] = max(m, float(p["smlo"]))
    th_hi = min(a1 + a2, 360 - a1 - a2) - p["smhi"]; th_lo = abs(a1 - a2) + p["smlo"]
    p["stops_ok"] = int(th_lo < th_hi - 1.0)
    p["phi_hi"] = dyad_phi(a1, a2, th_hi) if p["stops_ok"] else 170.0
    p["phi_lo"] = dyad_phi(a1, a2, th_lo) if p["stops_ok"] else 10.0
    p["mstop"] = 0; p["th_lo"], p["th_hi"] = th_lo, th_hi
    return p


def _q2_of(th, a1e, p):
    """J2's OWN joint angle (deg, signed, about J2 from link 1b's arc to link 2's arc) of the variant-A chain at J1-J3 angle th
    and J1-J2 arc a1e (per-pose arrays); rotation invariant, so built on a canonical frame. -> q2, valid"""
    th = np.asarray(th, float); n = len(th); a1e = np.broadcast_to(np.asarray(a1e, float), (n,))
    P1 = np.broadcast_to(np.array([0.0, 0.0, 1.0]), (n, 3)); P3 = np.stack([np.sin(th * D2R), np.zeros(n), np.cos(th * D2R)], -1)
    sg = 1 if float(p["sigma"]) >= 0 else -1; sK = 1 if float(p["sK"]) >= 0 else -1
    p2, h2 = KA.closure_v(P1, P3, a1e, float(p["a2"]), sg); pK, hK = KA.closure_v(P1, p2, np.full(n, float(p["b1"])), np.full(n, float(p["b2"])), sK)
    return K.axis_angle(p2, pK, P3), (h2 > 0) & (hK > 0)


_law0 = KA.law


def law(p1, p3, p):
    """phys 1: J2's stop acts on its own joint angle q2 (a dowel in an arc slot); past the window J2 is locked on the stop and
    K opens to the smallest a1e >= a1 (<= a1max) that closes the chain with q2 on the stop (scan 0.25 deg + bisection).
    phys 0: the variant-A model's virtual interior-angle law (unchanged)."""
    if not p.get("phys"): return _law0(p1, p3, p)
    a1 = float(p["a1"]); th = np.degrees(np.arccos(np.clip((K.unit(p1) * K.unit(p3)).sum(-1), -1, 1)))
    a1e = np.full(len(th), a1); state = np.zeros(len(th), int)
    for m, thb, s in ((th > p["th_hi"], p["th_hi"], 1), (th < p["th_lo"], p["th_lo"], -1)):
        ii = np.nonzero(m)[0]
        if not len(ii): continue
        q2s = float(_q2_of(np.array([thb]), a1, p)[0][0]); state[ii] = s
        grid = np.arange(a1, float(p["a1max"]) + 1e-9, 0.25)
        if grid[-1] < float(p["a1max"]) - 1e-9: grid = np.r_[grid, float(p["a1max"])]
        t = th[ii]; found = np.full(len(ii), np.nan); lo = np.full(len(ii), np.nan)
        fprev, vprev = _q2_of(t, grid[0], p); fprev = (fprev - q2s + 180) % 360 - 180
        for g in grid[1:]:
            f, v = _q2_of(t, g, p); f = (f - q2s + 180) % 360 - 180
            hit = np.isnan(found) & v & vprev & (np.sign(f) != np.sign(fprev)) & (np.abs(f - fprev) < 90)
            found[hit] = g; lo[hit] = g - (grid[1] - grid[0]) if g - (grid[1] - grid[0]) >= a1 else a1
            fprev, vprev = f, v
        k = np.nonzero(np.isfinite(found))[0]
        if len(k):
            A, Bv = lo[k].copy(), found[k].copy(); fa = (_q2_of(t[k], A, p)[0] - q2s + 180) % 360 - 180
            for _ in range(14):
                mid = 0.5 * (A + Bv); fm = (_q2_of(t[k], mid, p)[0] - q2s + 180) % 360 - 180
                left = np.sign(fm) == np.sign(fa); A = np.where(left, mid, A); fa = np.where(left, fm, fa); Bv = np.where(left, Bv, mid)
            found[k] = Bv
        a1e[ii] = found
    return a1e, state, th


KA.law = law                                                  # KA.kinematics looks it up as a module global


def build(B, F, p):
    """= KA.build with hub K's cap `capK` mm taller than the O20 stack (the real 0.3 x 5 mm clock spring's cap)"""
    k = kinematics(F, p); p1, p2, p3, pK, ok = k["p1"], k["p2"], k["p3"], k["pK"], k["ok"]
    q = np.stack([K.axis_angle(p1, F.S([1.0, 0, 0]), pK), k["psi"], K.axis_angle(p2, pK, p3), K.axis_angle(p3, F.HG([0.0, -1, 0]), p2)], -1)
    hubs = [K.hub_member("hub1", p1, "J1"), K.hub_member("hubK", pK, "K", t=K.CROWN + float(p.get("capK", 0) or 0)),
            K.hub_member("hub2", p2, "J2"), K.hub_member("hub3", p3, "J3")]
    w, t = p["width"], p["t_link"]
    links = [K.strap_member("link1a", p1, pK, ("J1", "K"), width=w, t=t, ramp_to=(("hub1", K.STACK), ("hubK", 0.0))),
             K.strap_member("link1b", pK, p2, ("K", "J2"), width=w, t=t, ramp_to=(("hubK", K.STACK + KA.KX), ("hub2", 0.0)),
                            over=[("link1a", 1.0)], end_mm=K.HUB_R + 6.0),
             K.strap_member("link2", p2, p3, ("J2", "J3"), width=w, t=t, ramp_to=(("hub2", K.STACK), ("hub3", K.STACK)),
                            over=[("link1a", 1.0), ("link1b", 1.0), ("neck", 1.0)]),
             K.neck_member(F, p3, joints=("J3",), ramps=(("hub3", 0.0), (None, 0)))]
    o = ok
    info = dict(residual_deg=round(float(k["res"][o].max()), 5) if o.any() else None,
                forced_share=round(float((k["state"][o] != 0).mean()), 4) if o.any() else None,
                stretched=int(((k["state"] == 1) & o).sum()), folded=int(((k["state"] == -1) & o).sum()),
                a1e_max=round(float(k["a1e"][o].max()), 2) if o.any() else None,
                psi_range=[round(float(np.abs(k["psi"][o]).min()), 1), round(float(np.abs(k["psi"][o]).max()), 1)] if o.any() else None,
                min_sub_margin=round(float(k["msub"][o & (k["state"] != 0)].min()), 2) if (o & (k["state"] != 0)).any() else None)
    return K.Chain(members=hubs + links, ok=ok, q=q, joints=dict(J1=p1, K=pK, J2=p2, J3=p3), info=info)


_kin0 = KA.kinematics


def kinematics(F, p):
    k = _kin0(F, p); m = K.FOLD_MARGIN; a2 = float(p["a2"]); a1e = k["a1e"]; th = k["th"]
    m3e = np.minimum.reduce([th - np.abs(a1e - a2), np.minimum(a1e + a2, 360 - a1e - a2) - th])
    k["m3e"] = m3e; k["ok"] = k["ok"] & (m3e >= m - 1e-6) & bool(p.get("stops_ok", 1))
    return k


KA.kinematics = kinematics                                   # build() / _extras() look it up as a module global


KA.build = build                                              # KA.evaluate builds through this module global
_crown0 = SP.crown_points


def crown_points(m, rho, rad):
    """the crown-skin samples at the member's own crown height (hub K's taller cap), not the O20 12.25"""
    t = float(getattr(m, "t", K.CROWN))
    if t <= K.CROWN + 1e-9: return _crown0(m, rho, rad)
    old = K.CROWN; K.CROWN = t
    try: return _crown0(m, rho, rad)
    finally: K.CROWN = old


SP.crown_points = crown_points


def evaluate(B, params):
    p = stops(dict(PARAMS, **params))
    p, r = KA.evaluate(B, p)
    kin = B._kit_last.get("kin"); take = B._kit_last.get("take")
    if kin is not None:
        ok = kin["ok"]
        r["kitrule"] = dict(phi_lo=round(p["phi_lo"], 2), phi_hi=round(p["phi_hi"], 2), smlo=round(p["smlo"], 2), smhi=round(p["smhi"], 2),
                            min_margin_ok=round(float(kin["m3e"][ok].min()), 2) if ok.any() else None)
    r["plain"] = {k: r.get(k + "_plain", r.get(k)) for k in ("gap", "reach", "follow", "inband14", "contact")}
    return p, r


def bench_eval(B, params):
    _, r = evaluate(B, params)
    return {k: v for k, v in r.items() if SP._jsonable(v)}


# ---------------- continuity (the re-measure verifier's flood fill, for the kit chain) ----------------
class _F:
    """Frames stand-in for arbitrary humerus orientations in the scapula frame (RS = I: every angle is relative)"""
    def __init__(self, HG): self.RHG = HG
    def S(self, u): return np.broadcast_to(np.asarray(u, float), (len(self.RHG), 3)).copy()
    def HG(self, u): return np.einsum("pij,j->pi", self.RHG, np.asarray(u, float))


def kin_q(p, HG):
    F = _F(HG); k = kinematics(F, p); p1, p2, p3, pK = k["p1"], k["p2"], k["p3"], k["pK"]
    q = np.stack([K.axis_angle(p1, F.S([1.0, 0, 0]), pK), k["psi"], K.axis_angle(p2, pK, p3), K.axis_angle(p3, F.HG([0.0, -1, 0]), p2)], -1)
    return k["ok"], np.asarray(q, float), k["state"]


def connected(p):
    """-> dict(keys=set of connected workspace pose keys (plane, elev, axial), stats)"""
    Z = CB._poses_all(); names = list(Z["NAMES"]); W = np.nonzero(Z["CID"] == names.index("Workspace (envelope)"))[0]
    POSE = Z["POSE"][W]; HG = Z["HG"][W].astype(float)
    ok, qq, st = kin_q(p, HG)
    key = {(float(x[0]), float(x[1]), float(x[2])): i for i, x in enumerate(POSE)}
    vals = [sorted(set(POSE[:, k].tolist())) for k in range(3)]

    def nbrs(i):
        x = [float(POSE[i, 0]), float(POSE[i, 1]), float(POSE[i, 2])]
        for d in range(3):
            j = vals[d].index(x[d])
            for jj in (j - 1, j + 1):
                if d == 2 and jj == len(vals[2]) and vals[2][-1] == 180.0: jj = 1
                if d == 2 and jj == -1 and vals[2][0] == -180.0: jj = len(vals[2]) - 2
                if 0 <= jj < len(vals[d]):
                    y = list(x); y[d] = vals[d][jj]; t = key.get(tuple(y))
                    if t is not None: yield t
        if x[2] in (180.0, -180.0):
            t = key.get((x[0], x[1], -x[2]))
            if t is not None: yield t
    why = {"fold_or_window": 0, "jump": 0}; n = [0]

    def edge(a, b):
        angd = np.degrees((Rot.from_matrix(HG[a]).inv() * Rot.from_matrix(HG[b])).magnitude())
        ns = max(2, int(math.ceil(angd / STEP)) + 1)
        Qs = Slerp([0, 1], Rot.from_matrix(np.stack([HG[a], HG[b]])))(np.linspace(0, 1, ns)).as_matrix()
        o, q, _ = kin_q(p, Qs); n[0] += 1
        if not o.all(): why["fold_or_window"] += 1; return False
        if np.abs((np.diff(q, axis=0) + 180) % 360 - 180).max() > JUMP: why["jump"] += 1; return False
        return True
    elev = POSE[:, 1]; cn = np.zeros(len(W), bool)
    front = [i for i in range(len(W)) if ok[i] and elev[i] == 0 and st[i] == 0]; cn[front] = True
    while front:
        nxt = []
        for a in front:
            for b in nbrs(a):
                if ok[b] and not cn[b] and edge(a, b): cn[b] = True; nxt.append(b)
        front = nxt
    keys = {(float(POSE[i, 0]), float(POSE[i, 1]), float(POSE[i, 2])) for i in np.nonzero(cn)[0]}
    return dict(keys=keys, nodes=int(ok.sum()), connected=int(cn.sum()), edges=n[0], refused=why,
                nodes_by_state={s: int((ok & (st == v)).sum()) for s, v in (("A", 0), ("stretched", 1), ("folded", -1))},
                connected_by_state={s: int((cn & (st == v)).sum()) for s, v in (("A", 0), ("stretched", 1), ("folded", -1))})


def _held():
    sp = importlib.util.spec_from_file_location("pk_polish_v_a", os.path.join(REPO, "docs", "concepts", "verify", "skin-normal-3r-pin-knee-polish.py"))
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m.held_bench()


def frozen(p0, wear="bench", out=None, overlap=1.0):
    """fit Bench(60,160) FAST, freeze every profile, wear on Bench(110,360) (CB_EXACT=1: exact) or the held-out bench;
    the continuity rule applied (reach on the connected set only); plain + near-touch reported"""
    t0 = time.time(); coll = K.collisions; K.collisions = functools.partial(coll, overlap=overlap - 1e-4)
    ex = os.environ.pop("CB_EXACT", None)
    try: Bf = K.bench(60, 160)
    finally:
        if ex is not None: os.environ["CB_EXACT"] = ex
    pf, rf = evaluate(Bf, dict(p0, near=0)); prof = {k: np.array(v) for k, v in Bf._kit_last["prof"].items()}
    Bb = _held() if wear == "held" else K.bench(110, 360); fp = K.fit_profiles
    K.fit_profiles = lambda B, chain, fit, q=1.0, mode="march": {k: v.copy() for k, v in prof.items()}
    try:
        r = K.evaluate(Bb, build, pf); Bb._kit_last["kin"] = kinematics(Bb._kitF, pf)
        r = SP.declared_audit(r, dict(pf, rad1=10.0, rad2=10.0, rad3=10.0)); r = KA._extras(Bb, r, pf)
    finally:
        K.fit_profiles = fp; K.collisions = coll
    keep = ("gap", "reach", "follow", "inband14", "inband10", "contact", "gap_near1", "min_metal_skin", "overhead", "honest", "forced")
    static = {k: r.get(k) for k in keep}
    kin = Bb._kit_last["kin"]; m3 = kin["m3e"]
    taken = [i for i in range(len(Bb.idx)) if SP._taken(Bb, i)]
    C = connected(pf); drop = [i for i in taken if Bb.kind[i] == "ws" and (float(Bb.poses[i]["plane"]), float(Bb.poses[i]["elev"]), float(Bb.poses[i]["axial"])) not in C["keys"]]
    res0 = list(Bb.res)
    for i in drop: Bb.res[i] = None
    rr = Bb.report(); r2 = dict(rr); r2 = KA._extras(Bb, dict(rr), pf); Bb.res = res0
    conn = {k: r2.get(k) for k in keep if k in r2}; conn["score"] = round(100 * (1 - conn["gap"] / 275), 2)
    out_d = dict(model="docs/concepts/models/minarc-stop-knuckle-4r-a-kitrule.py", params={k: v for k, v in pf.items() if isinstance(v, (int, float, str, bool))},
                 fold_margin=K.FOLD_MARGIN, wear=wear, mode=Bb.mode, n=len(Bb.idx), fit={k: rf.get(k) for k in keep if k != "forced"},
                 static=static, connected=conn, dropped_unconnected=len(drop),
                 min_margin_taken=round(float(min(m3[i] for i in taken)), 2) if taken else None,
                 conn_stats={k: v for k, v in C.items() if k != "keys"}, secs=round(time.time() - t0, 1))
    if out: json.dump(out_d, open(out, "w"), indent=1, default=float)
    print(json.dumps({k: v for k, v in out_d.items() if k != "params"}, default=float), flush=True)
    return out_d


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].startswith("{") else {}
    if mode == "frozen":
        frozen(stops(dict(PARAMS, **par)), sys.argv[3] if len(sys.argv) > 3 else "bench", sys.argv[4] if len(sys.argv) > 4 else None); sys.exit()
    B = K.bench(60, 160); t = time.time(); p, r = evaluate(B, par)
    print({k: r[k] for k in ("gap", "reach", "follow", "inband14", "contact", "honest")}, "plain", r["plain"], "kit", r.get("kitrule"),
          "forced", {k: r.get(k) for k in ("stretched", "folded", "a1e_max", "min_sub_margin")}, f"{time.time() - t:.1f}s")
