"""isoceles-shortdyad-pinknee-3r (round 501, G1 golden, lens A): H1's cx-0 morphology - a plain O20 spherical-ish 3R
through GH (J1, J2 on GH rays, J3 tilted b3 toward the skin normal) closed at the cuff by the flat MR63ZZ two-pin knee
(outside the DOF count, user decision 5) - RE-SEATED in the three knee-class cells the round-501 proposer found:

  A  isoceles short dyad  a1 40.5 / a2 44.9, J1 lateral acromion top bvec(87.4, 57.3), hub 2 posterolateral
  B  posterior slot       a1 47.5 / a2 73.4, J1 bvec(104.7, 60.3), J2 rest seat on the scapular-spine root
  C  pole-J1              a1 64.3 / a2 45.8, J1 bvec(137.6, 78.2) near the acromion pole, hub 2 low lateral

Built on docs/concepts/models/crest-knee-3r.py imported UNCHANGED (which is docs/concepts/models/skin-normal-3r-pin-knee.py
- H1's Design / IK / two-circle knee closure / VModel rules / part-part clearances / near-touch / contact-only walls and
crowns - plus link 2 flying over member 3 (fly), the J3 own-angle dowel stop (j3stop, window fitted on the search bench and
FROZEN for every other bench), h2cap, the joggled knee kj and frozen()). What this file adds:

  * THE a1 / a2 RE-SOLVE (round-501 judge's rule): the J2 seat ray (az2, el2) is not a free parameter. It is solved from
    J1's ray, J3's TILTED axis (wd, wa, b3) and the cell's arcs a1, a2 on branch br (sign d2 . (d1 x d3)), so every b3
    change keeps a1 / a2 at the cell's values (the proposer's 45.82 read ran b3 0.2 at a2 43.8, not 44.9).
    (b1 = b2 = 0: J1 / J2 axes are their GH rays; J3's line misses GH by b3, as in H1.)
  * h2clip (optional, mm): REFUSE the poses whose hub-2 need is above the clip level (the max hub-2 need over the clip
    frames the greedy drop keeps, + h2clip) instead of raising hub 2 for them - the spec's guard against a search that
    buys reach by floating hub 2 (the 1 cm rule). It sets h2cap from the clips; None = off (h2cap, if given, applies).
  * conditioning and fold-margin report: |u1 . (u2 x w)| over the taken poses (u1 J1, u2 posed J2, w posed J3 axis;
    the judge's red-team number, H1's worst 0.233) and the min th margin (th = angle(u1, w), the ONE fold metric,
    tools/concept_kit.py lines 25-30) over the taken poses.
  * evaluate(): the search objective is the 1 mm near-touch gap (CLAUDE.md search rule); r['plain'] keeps the plain gap.

DOF: 3 ACTIVE (J1, J2, J3, O20 v5 hubs, MR117-2RS pairs), knee pins a / b passive rotations (MR63ZZ pairs, outside the
count, set by closure - no undetermined coordinate, R17), 0 passive translations, no springs / loops / slides, no gears,
pulleys or cables. Complexity 0 (tools/simplicity.py v2.2: H1's record; the J3 stop dowel is a bought part).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/isoceles-shortdyad-pinknee-3r.py check '<json>' [--big]
    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/isoceles-shortdyad-pinknee-3r.py seeds
    OMP_NUM_THREADS=1 nice -n 10 CB_EXACT=1 python3 docs/concepts/models/isoceles-shortdyad-pinknee-3r.py frozen '<json>' out.json
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
_sp = importlib.util.spec_from_file_location("crest_for_isoceles", os.path.join(HERE, "crest-knee-3r.py"))
CK = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(CK)
PK, S, CB = CK.PK, CK.S, CK.CB
OSN = PK.OSN
ID = "isoceles-shortdyad-pinknee-3r"
NAME = "Isoceles short-dyad pin knee (cx-0 knee-class frontier, seeds A isoceles / B posterior slot / C pole-J1)"

# pre-registered seats (round501_ideation.md lens A / catalogue model_spec), branch -1 for all; a1 / a2 are the cells'
# arcs at b3 = 0 (computed from these seats by cell_arcs(), printed by `seeds`)
SEEDS = {
    "A":   dict(az1=87.43, el1=57.31, az2=36.72, el2=34.75, wd=99.63, wa=2.5, lE=97.0, lc=24.4, phiE=15.0, phib=-60.0),
    "B":   dict(az1=104.67, el1=60.32, az2=7.92, el2=54.66, wd=92.45, wa=-2.85, lE=97.0, lc=24.4, phiE=15.0, phib=-92.0),
    "B2b": dict(az1=82.37, el1=56.14, az2=-0.74, el2=52.04, wd=103.62, wa=-13.01, lE=97.0, lc=24.4, phiE=15.0, phib=-92.0),
    "C":   dict(az1=137.61, el1=78.24, az2=78.44, el2=20.0, wd=78.29, wa=37.03, lE=97.0, lc=24.4, phiE=15.0, phib=120.0),
}
PARAMS = dict(CK.PARAMS)
PARAMS.update(SEEDS["A"], b1=0.0, b2=0.0, b3=0.2, br=-1.0, a1=None, a2=None, ang_min=25.22, stk=6.0, fly=1, j3stop=1,
              j3stop_margin=1.0, h2cap=None, h2clip=None, kj=0)
ANG_MIN_RULE = 25.22


def _rays(az1, el1, az2, el2, wd, wa, b3):
    R = OSN.rest()
    d1 = OSN.seat(S.bvec(az1, el1), 0.0)[1]; d2 = OSN.seat(S.bvec(az2, el2), 0.0)[1]
    d3 = OSN.seat(R["Q0"] @ S.w_dir(wd, wa), b3)[1]
    return d1, d2, d3


def _ang(a, b): return math.degrees(math.acos(float(np.clip(a @ b, -1, 1))))


_ARCS = {}
def cell_arcs(seed):
    """the seed cell's arcs a1 = angle(d1, d2), a2 = angle(d2, d3) at b3 = 0 and its branch"""
    if seed not in _ARCS:
        s = SEEDS[seed]; d1, d2, d3 = _rays(s["az1"], s["el1"], s["az2"], s["el2"], s["wd"], s["wa"], 0.0)
        _ARCS[seed] = dict(a1=_ang(d1, d2), a2=_ang(d2, d3), br=float(np.sign(d2 @ np.cross(d1, d3)) or 1.0))
    return _ARCS[seed]


def resolve_j2(d1, d3, a1, a2, br):
    """J2's seat ray with angle(d1, d2) = a1, angle(d2, d3) = a2 on branch br = sign(d2 . (d1 x d3)) -> az2, el2, ok
    (same algebra as docs/concepts/models/posteromedial-knuckle-3r.py resolve_j2)"""
    c1, c2 = math.cos(math.radians(a1)), math.cos(math.radians(a2)); dd = float(np.clip(d1 @ d3, -1, 1))
    n = np.cross(d1, d3); n = n / (np.linalg.norm(n) + 1e-12); den = max(1 - dd ** 2, 1e-9)
    a = (c1 - dd * c2) / den; b = (c2 - dd * c1) / den; p_ = a * d1 + b * d3; h2 = 1 - float(p_ @ p_)
    d2 = p_ + br * math.sqrt(max(h2, 0.0)) * n; d2 = d2 / np.linalg.norm(d2)
    el2 = math.degrees(math.asin(float(np.clip(d2[1], -1, 1)))); az2 = math.degrees(math.atan2(float(d2[2]), float(-d2[0])))
    th0 = math.degrees(math.acos(dd))
    return az2, el2, bool(h2 > 1e-4 and abs(a1 - a2) + 5.5 <= th0 <= a1 + a2 - 5.5)


def _clamp(p):
    """bounds + the a1 / a2 re-solve. a1 / a2 None -> the arcs of the given az2 / el2 at b3 = 0 (the seed's cell)"""
    p = dict(p); p["b1"] = 0.0; p["b2"] = 0.0; p["stk"] = 6.0
    p["ang_min"] = max(float(p.get("ang_min", ANG_MIN_RULE)), ANG_MIN_RULE)
    p["b3"] = min(max(float(p.get("b3", 0.2)), 0.0), 0.45)
    p["lE"] = min(max(float(p["lE"]), 40.0), 115.0); p["lc"] = min(max(float(p["lc"]), 14.0), 48.0)
    br = 1.0 if float(p.get("br", -1.0)) >= 0 else -1.0; p["br"] = br
    if p.get("a1") is None or p.get("a2") is None:
        d1, d2, d3 = _rays(p["az1"], p["el1"], p["az2"], p["el2"], p["wd"], p["wa"], 0.0)
        p["a1"], p["a2"] = round(_ang(d1, d2), 4), round(_ang(d2, d3), 4)
    d1, _, d3 = _rays(p["az1"], p["el1"], 0.0, 0.0, p["wd"], p["wa"], p["b3"])
    az2, el2, ok = resolve_j2(d1, d3, float(p["a1"]), float(p["a2"]), br)
    p["az2"], p["el2"] = round(az2, 5), round(el2, 5); p["unresolved"] = not ok
    p["legal_j1"] = bool(S.bvec(p["az1"], p["el1"])[0] <= 0.20)      # ruling 4: no front / clavicle seat (anterior <= 0.20)
    return p


class Iso(CK.Model):
    """crest-knee Model + h2clip (refuse poses whose hub-2 need is above the clip level)"""

    def greedy_drop(self, keep0=None, links=True):
        super().greedy_drop(keep0, links)
        tol = self.p.get("h2clip")
        if links or tol is None or "hub2" not in self.Hneed: return
        keep = ~self.drop; kind = np.array([self.B.kind[i] for i in self.poses_fit]); cl = keep & (kind == "clip")
        if cl.any(): self.p["h2cap"] = float(self.Hneed["hub2"][cl].max() + float(tol))


CK._FlatModel = Iso                                           # CK._factory / CK.frozen / PK._report build this model


def conditioning(M, B):
    """over the TAKEN poses: min |u1 . (u2 x w)|, the min th margin to the window [|a1-a2| + 0, a1 + a2] edges (deg),
    and the takes below H1's worst conditioning (0.233)"""
    D = M.D; u1, u2, u3 = D.u; w = M.Q @ u3
    R1 = S.rotm(u1, M.q[:, 0]); p2 = R1 @ u2
    det = np.abs(np.einsum("j,nj->n", u1, np.cross(p2, w)))
    th = np.degrees(np.arccos(np.clip(w @ u1, -1, 1))); a1, a2 = np.degrees(D.A[0]), np.degrees(D.A[1])
    marg = np.minimum(th - abs(a1 - a2), a1 + a2 - th)
    tk = np.array([B.res[i] is not None and float(np.min(B.res[i])) >= 0 for i in range(len(B.idx))])
    if not tk.any(): return dict(det_min=None)
    kind = np.array(B.kind)
    lowc = tk & (det < 0.233)
    return dict(det_min=round(float(det[tk].min()), 4), th_margin_min=round(float(marg[tk].min()), 3),
                th_taken=[round(float(th[tk].min()), 1), round(float(th[tk].max()), 1)], window=[round(abs(a1 - a2), 2), round(a1 + a2, 2)],
                below_h1=int(lowc.sum()), below_h1_clip=int((lowc & (kind == "clip")).sum()))


def report(B, params):
    p = _clamp(dict(PARAMS, **params))
    r, M = CK.report(B, p)
    if M.kin_ok.any() and r.get("f") is not None:
        r["audit"] = PK.audit(M, B); r["cond"] = conditioning(M, B)
    D = M.D
    r["seats2"] = dict(az2=p["az2"], el2=p["el2"], a=[round(math.degrees(a), 3) for a in D.A], unresolved=p["unresolved"],
                       legal_j1=p["legal_j1"], h2cap=M.p.get("h2cap"))
    return r, M


def evaluate(B, params):
    """tools/concept_cma.py hook: objective = the 1 mm near-touch gap; plain gap kept in r['plain']"""
    r, M = report(B, params)
    r["plain"] = r["gap"]
    a = r.get("audit") or {}
    if a.get("gap_near1") is not None: r["gap"] = a["gap_near1"]
    q = _clamp(dict(PARAMS, **params))
    if q["unresolved"] or not q["legal_j1"]: r["honest"] = False
    p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


REPORT_KEYS = ("plain", "cond", "why", "j3stop", "seats2", "knee", "f")


def bench_eval(B, params):
    r, M = report(B, params); r.pop("params", None); return r


def frozen(P, nc=110, nw=360):
    p = _clamp(dict(PARAMS, **P)); out, M, B = CK.frozen(p, nc, nw, keep=True)
    out["cond"] = conditioning(M, B); out["params_resolved"] = {k: v for k, v in p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return out


def viz_geom(B, params):
    """the home-frame geometry the motion preview (docs/concepts/viz/concepts/<id>.js, crest-knee-3r.js layout) draws"""
    r, M = report(B, params); D = M.D; fr = M.fr; R = lambda x, n=3: [round(float(v), n) for v in np.ravel(x)]

    def centre(name, nb=14):
        mem, X = M.link_pts[name]; lk = [l for l in M.geo.links if l["name"] == name][0]
        da, db = S.unit(D.c[lk["ka"]] + M.f[lk["ka"]] * D.u[lk["ka"]]), S.unit(D.c[lk["kb"]] + M.f[lk["kb"]] * D.u[lk["kb"]])
        t = np.arctan2(np.linalg.norm(np.cross(da[None], S.unit(X)), axis=1), S.unit(X) @ da)
        e = np.linspace(t.min(), t.max() + 1e-9, nb + 1); out = []
        for k in range(nb):
            sel = (t >= e[k]) & (t < e[k + 1])
            if sel.any(): out.append(R(X[sel].mean(0)))
        return out
    G = dict(u=[R(x, 5) for x in D.u], c=[R(x) for x in D.c], sa=R(D.sa, 5), st=R(D.st, 5), sn=R(D.sn, 5),
             A=[round(math.degrees(a), 3) for a in D.A], branch=float(D.branch), m=R(D.m), f=R(M.f, 2), tr=round(float(M.tr), 2),
             trb=round(float(getattr(M, "tr_b", M.tr)), 2), BR=PK.BOSS_R, tp=round(float(M.p["tp"]), 3), RUN=S.RUN, SING=5.0, hr=list(M.hr),
             A0=R(fr["A0"]), A0m=R(fr["A0m"]), Bm=R(fr["Bm"]), eE=R(fr["eE"], 5), eK=R(fr["eK"], 5), L1=centre("L1"), L2=centre("L2"))
    P = {k: (round(float(M.p[k]), 4) if isinstance(M.p[k], (int, float)) else M.p[k]) for k in
         ("az1", "el1", "az2", "el2", "wd", "wa", "b3", "lE", "lc", "phiE", "phib", "stk", "ang_min", "kj")}
    return dict(P=P, G=G, gap=r["gap"])


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].startswith("{") else {}
    if mode == "viz":
        print(json.dumps(viz_geom(CB.Bench(n_clip=60, n_ws=160), par), default=float)); sys.exit()
    if mode == "seeds":
        for k in SEEDS: print(k, {kk: round(v, 3) for kk, v in cell_arcs(k).items()})
        sys.exit()
    if mode == "frozen":
        t = time.time(); out = frozen(par); out["params"] = par; out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        print(json.dumps(out, default=float)); sys.exit()
    nc, nw = (110, 360) if "--big" in sys.argv else (60, 160)
    B = CB.Bench(n_clip=nc, n_ws=nw); t = time.time()
    r, M = report(B, par)
    print({k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}, "why", r.get("why"), "knee", r.get("knee"),
          "f", r.get("f"), "j3stop", r.get("j3stop"), f"{time.time() - t:.0f}s", B.mode)
    print("parts", r.get("parts_ib14"), r.get("parts_pairs"), "seats2", r.get("seats2"), "cond", r.get("cond"))
    a = r.get("audit") or {}
    print("near", a.get("near_touch_min_mm"), a.get("gap_near1"), a.get("near1_poses"), "over", a.get("overhead140"))
