"""seatoracle-erwall-knuckle-3r: SEAT ORACLE at the second wall (round 105 lens B, instrument; leadseat-longstop-oracle merged in).

An INSTRUMENT, never a claim. It runs the verified free-K oracle harness (docs/concepts/models/freek-oracle-route-knuckle-4r.py:
skinnormal-shortk-knuckle-4r's minarc kitrule chain, O20 hubs at J1 / K / J2 / J3, 3 mm bent Ti bars, two-pin cuff knee on MR63ZZ
pairs, ISO 8734 dowels in arc grooves) UNCHANGED on a few seat cells. At each cell the oracle picks, per stretched pose, the best K
in [5.5-deg fold floor, stop B] by composed runs of the frozen model (every check of the model applies), so a cell's number is a
BOUND on every coupled / sprung / stopped K law at 3 active DOF at those seats (no unpowered mechanism picks K per pose).

What this wrapper adds to the oracle harness:
  * CELLS: L0 = the 3-joint lead's own seats with stop B 76.04 (bk1 26 / bk2 55.04); C0 = the same seats at the lead's own stroke
    (a1max 58.7678 / bk2 38.0336, the control that isolates the stroke); S1 / S2 = the k33 seats with J1 slid forward along the
    acromion-top band (az1 +15 / +25), J2 re-solved by closure(J1, J3 rest, a1 37.912, a2 58.500, branch -1), K dyad held.
    SPEC CORRECTION (measured 2026-10-18): the plan's bk2 55.04 (L0) and 38.0336 (C0) break the model's K-dyad rule
    a1max <= bk1 + bk2 - 5.5 (KRDesign.k_ok False -> every pose refused, the fit finds no closed pose); the plan checked only
    the a1 side. bk2 is raised by the least amount that keeps the planned stroke: 55.56 (L0, L1) and 38.28 (C0); stop B stays
    at a1max 76.044 / 58.7678. Low-end margin |bk1 - bk2| + 5.5 <= a1: 35.06 <= 37.55 (L0), 17.78 (C0).
    Everything else = the verified k33 priced params (knee, metal rules, kit K law, J3 seat for the S cells).
  * CONNECTED reading per cell: the kinematic flood fill (RM.kin_nodes + RM.flood: 2-deg slerp edges, 10-deg jump incl. dK, no
    branch change) is RE-RUN on THIS cell's frozen kit design and written to the cell's own conn file, which the oracle's
    connected filter then reads (the k33 conn file is never reused).
  * per-pose outcome table (taken min mm / contact depth / refusal reason), the binder / overhead / IR groups of the round-105
    plan, the min J1-J3 fold margin over taken poses in each pose's own state, the oracle-moved count.

    CB_EXACT=1 CB_FOLD_MARGIN=5.5 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/seatoracle-erwall-knuckle-3r.py cell L0
    ... fast L0      (Bench(60,160) fast, fit = wear, no flood: the sweep entry)
"""
import copy, importlib.util, json, math, os, sys, time
import numpy as np

os.environ.setdefault("CB_FOLD_MARGIN", "5.5")
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ID = "seatoracle-erwall-knuckle-3r"
OUTD = os.path.join(REPO, "docs", "concepts", "verify", ID)


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


FO = _load("fo_for_seatoracle", os.path.join(HERE, "freek-oracle-route-knuckle-4r.py"))
RM, CB, KIT = FO.RM, FO.CB, FO.KIT
K33_ORIG = FO.K33

LEAD = dict(az1=95.3929, el1=67.8974, az2=45.8211, el2=41.0855, wd=66.8662, wa=-10.6559, b3=0.329, bk1=26.0)
CELLS = {
    "L0": dict(LEAD, bk2=55.56, a1max=76.044),                                   # lead seats, stop B 76.04 (bk2 55.04 -> 55.56: K-dyad rule)
    "L0b": dict(LEAD, bk1=32.0, bk2=52.0, a1max=76.044),                        # lead seats, stop B 76.04, k33's K dyad (L0's K triangle jams)
    "C0": dict(LEAD, bk2=38.28, a1max=58.7678),                                  # lead seats, the lead's own stroke (control; bk2 38.0336 -> 38.28)
    "S1": dict(az1=116.6411, az2=53.5141, el2=46.478),                           # k33 seats, J1 az +15 (5.6 deg on the sphere)
    "S2": dict(az1=126.6411, az2=61.0385, el2=47.5979),                          # k33 seats, J1 az +25 (9.4 deg)
    "L1": dict(LEAD, az1=105.3929, az2=51.7141, el2=42.775, bk2=55.56, a1max=76.044),
}
EXPECT = {"L0": (37.552, 57.218), "L0b": (37.552, 57.218), "C0": (37.552, 57.218), "L1": (37.552, 57.218), "S1": (37.912, 58.5), "S2": (37.912, 58.5)}
GROUPS = {"ER binders": (117, 119, 129, 148), "overhead clip + drive-metal poses": (7, 8, 9, 10, 11, 234, 237, 264, 290),
          "IR": (343, 423, 316, 369), "never clear": (405, 459), "other binders": (127, 139)}


def cell_params(name):
    P = FO.params(dict(CELLS[name])); return P


def kcheck(D, P, name):
    """assert the cell's dyad (a1, a2 within 0.05 of the plan) and K's dyad legality (k_ok)"""
    a1, a2 = float(D.a1) if abs(D.a1) > 3.2 else math.degrees(D.a1), float(D.a2) if abs(D.a2) > 3.2 else math.degrees(D.a2)
    e1, e2 = EXPECT[name]; m = KIT.FOLD_MARGIN
    kok = (abs(P["bk1"] - P["bk2"]) + m <= a1 <= P["bk1"] + P["bk2"] - m) and (P["a1max"] <= P["bk1"] + P["bk2"] - m)
    return dict(a1=round(a1, 3), a2=round(a2, 3), a1_ok=abs(a1 - e1) < 0.05, a2_ok=abs(a2 - e2) < 0.05,
                k_ok_rule=bool(kok), k_ok_model=bool(getattr(D, "k_ok", True)), stops_ok=bool(getattr(D, "stops_ok", True)),
                k_low_margin=round(a1 - (abs(P["bk1"] - P["bk2"]) + m), 2), dKB=round(float(D.dKB()), 2))


def flood_conn(Mk, P, connfile):
    """the cell's own kinematic flood (kit K law, frozen design), written as the oracle's conn file"""
    t1 = time.time(); D = copy.deepcopy(Mk.D); R_tol = float(P["R_tol"]); Z, Wg, POSE, HG = RM.ws_grid(); _ = D.ik(HG[:2])
    okn, qq, sgn, st, own = RM.kin_nodes(D, HG, R_tol); seeds = okn & (POSE[:, 1] == 0) & (st == 0)
    cn, stats = RM.flood(POSE, HG, okn, seeds, D, R_tol)
    ck = [[float(POSE[i, 0]), float(POSE[i, 1]), float(POSE[i, 2])] for i in np.nonzero(cn)[0]]
    info = dict(nodes=int(okn.sum()), seeds=int(seeds.sum()), connected=int(cn.sum()), islands=int((okn & ~cn).sum()), edges=stats,
                secs=round(time.time() - t1, 1))
    json.dump(dict(connected_keys=ck, **info), open(connfile, "w"), default=float)
    return info


def pose_out(B, Mo, i):
    r = B.res[i]
    if r is None: return dict(st="refused", why=str(Mo.why[i]))
    d = min(float(np.min(r)), float(getattr(Mo, "cmin", {}).get(i, 1e9)))
    return dict(st="taken" if d >= 0 else "contact", mm=round(d, 3))


def margins(Mo, tab, tk):
    """min J1-J3 fold margin (deg) over taken poses, each pose in its own state (oracle table re-applied)"""
    D = copy.deepcopy(Mo.D); FO.ODesign.TAB = {FO.qkeys(Mo.Q[[i]])[0]: v for i, v in tab.items()}
    try: ok, qq, sg, st, own = RM.kin_nodes(D, Mo.Q, float(Mo.p["R_tol"]))
    finally: FO.ODesign.TAB = None
    vals = [(float(own[i]), int(i)) for i in tk]
    return dict(min_th_margin=round(min(vals)[0], 3) if vals else None, at_pose=min(vals)[1] if vals else None,
                below_5_5=int(sum(1 for v, _ in vals if v < 5.5 - 1e-6)))


def run_cell(name, mode="cell"):
    os.makedirs(OUTD, exist_ok=True); t0 = time.time()
    P = cell_params(name); P["_seed"] = name
    FO.K33 = os.path.join(OUTD, "c_k33_fit60_bench_params.json")          # the oracle's connected filter reads OUTD/c_<cell>_fit60_bench_conn.json
    connfile = os.path.join(OUTD, f"c_{name}_fit60_bench_conn.json")
    fitB = RM.PV.fast_bench(60, 160); exact = mode == "cell"
    B = CB.Bench(n_clip=110, n_ws=360) if exact else fitB
    orig = RM.freeze; info = {}

    def freeze_flood(fb, wb, PP, Model):
        out = orig(fb, wb, PP, Model)
        if "chk" not in info:
            info["chk"] = kcheck(out[0].D, PP, name)
            print("cell", name, "dyad check", info["chk"], flush=True)
            if exact: info["flood"] = flood_conn(out[0], PP, connfile); print("flood", info["flood"], flush=True)
        return out
    RM.freeze = freeze_flood
    try: r = FO.run_oracle(fitB, B, dict(P), how="runs")
    finally: RM.freeze = orig; FO.K33 = K33_ORIG
    o, k, Mo = r["oracle"], r["kit"], r["M"]
    tag = f"cell_{name}" if exact else f"fast_{name}"
    json.dump(dict(cell=name, check=info.get("chk"), flood=info.get("flood"), kit=k, oracle=o, connected=r["conn"], partial=True),
              open(os.path.join(OUTD, tag + ".json"), "w"), indent=1, default=float)      # core numbers first (post-processing below)
    tk = RM.taken_list(B); per = {int(i): pose_out(B, Mo, i) for i in range(len(B.idx))}
    for i in per: per[i].update(kind=B.kind[i], elev=float(B.poses[i]["elev"]), plane=float(B.poses[i]["plane"]), axial=float(B.poses[i]["axial"]),
                                moved=i in r["tab"])
    groups = {g: {str(i): per[i] for i in ids if i < len(B.idx)} for g, ids in GROUPS.items()}
    contacts = sorted([(v["mm"], i) for i, v in per.items() if v["st"] == "contact"])
    el = np.array([p_["elev"] for p_ in B.poses]); ws = np.array([kk == "ws" for kk in B.kind])
    oh = dict(ws=int((ws & (el >= 140)).sum()), taken=int(sum(1 for i in tk if ws[i] and el[i] >= 140)))
    try: mg = margins(Mo, r["tab"], tk) if exact else None
    except Exception as e: mg = dict(error=repr(e)[:300])
    out = dict(id=ID, cell=name, mode=mode, bench=B.mode, over=CELLS[name], check=info.get("chk"), flood=info.get("flood"),
               fold_margin=KIT.FOLD_MARGIN, nsr=FO.NSR, kit=k, oracle={kk: v for kk, v in o.items()}, connected=r["conn"],
               overhead140_ws=oh, contacts=[dict(pose=i, mm=d, kind=per[i]["kind"], elev=per[i]["elev"], plane=per[i]["plane"], axial=per[i]["axial"],
                                                 moved=per[i]["moved"]) for d, i in contacts],
               groups=groups, binders_cleared_02=[int(i) for i in (117, 119, 129, 148) if per[i]["st"] == "taken" and per[i]["mm"] >= 0.2],
               margins=mg, secs=round(time.time() - t0, 1),
               score_oracle=round(100 * (1 - o["gap"] / 275), 2), score_conn=round(100 * (1 - r["conn"]["gap"] / 275), 2) if r["conn"] else None)
    json.dump(out, open(os.path.join(OUTD, tag + ".json"), "w"), indent=1, default=float)
    json.dump(dict(per={str(i): v for i, v in per.items()}, tab={str(i): v for i, v in r["tab"].items()},
                   res={str(i): v for i, v in r["res"].items()}), open(os.path.join(OUTD, tag + "_perpose.json"), "w"), default=float)
    print(json.dumps({kk: out[kk] for kk in ("cell", "check", "kit", "oracle", "connected", "overhead140_ws", "binders_cleared_02", "margins", "secs")},
                     default=float), flush=True)
    return out


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode in ("cell", "fast"): run_cell(sys.argv[2], mode); sys.exit()
    if mode == "viz":                                        # geometry export for the motion preview (the oracle harness's exporter, kit K)
        P = dict(CELLS[sys.argv[2] if len(sys.argv) > 2 else "S2"])
        def _rep(B, pr):
            FO.ODesign.TAB = None; pp = FO.params(dict(P, **pr)); pp.pop("_seed", None); M = FO.KModel(B, pp); rr = M.run(); return dict(rr), M
        FO.SK._report = _rep
        print(json.dumps(FO.SK.viz_export({}), default=float)); sys.exit()
    raise SystemExit("modes: cell <L0|C0|S1|S2|L1> | fast <cell> | viz [cell]")
