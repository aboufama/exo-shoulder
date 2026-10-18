"""acroant-conecut-knuckle-3r (round 105, pick 3; lens B seat lever on the lead's coupled K): the verified lead
conecut-knee-knuckle-3r (docs/concepts/models/conecut-knee-knuckle-3r.py imported UNCHANGED: slipper-nose K drive,
conecut knee, J3 own-angle dowel stop, O20 hubs, metal, near-touch rules) with ONE seat move:

  J1 slides FORWARD on the acromion top by d_az1 deg of azimuth (az 90 lateral, 180 anterior; the lead's az1 95.3929 at
  el1 67.8974). J2's seat ray is RE-SOLVED for every d_az1 so the dyad keeps the lead's a1 (J1-J2 rays) and a2 (J2-J3
  rays) exactly, on the lead's branch: d2 = circ_int(d1, a1, d3, a2, branch) on the unit sphere (b1 = b2 = 0, so the seat
  axes ARE the rays; d3 = OSN.seat of the lead's J3 seat, unchanged). So the th fold window and the K dyad (bk1 / bk2 /
  a1max) are the lead's; only where the window sits in the arm's workspace and where the metal rides change.

DOF: 3 ACTIVE (J1, J2, J3), K slaved by the slipper-nose drive and never read, knee pins a / b passive rotations
(outside the count), 0 passive translations, no gears / pulleys / cables. The seat move adds no part (complexity 18.5,
the lead's record). J1 stays on the acromion top (ruling 4: back of the shoulder + acromion top only): +12 deg of az at
el1 67.9 is 4.5 deg of arc on the sphere.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/acroant-conecut-knuckle-3r.py [check] ['<json>']
    CB_EXACT=1 ... frozen|held|flood '<json>' [out.json]
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
_sp = importlib.util.spec_from_file_location("conecut_for_acroant", os.path.join(HERE, "conecut-knee-knuckle-3r.py"))
CC = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(CC)
CB, S, SN, PK = CC.CB, CC.S, CC.SN, CC.PK           # PK: tools/alignment_paired.py dump wraps PK.audit
OSN = CC.PK.OSN
ID = "acroant-conecut-knuckle-3r"
LEAD = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "conecut-knee-knuckle-3r.json")))["best_params"]
BASE = CC._clamp(dict(CC.PARAMS, **LEAD))                    # the verified lead, every parameter
AZ1_0 = float(BASE["az1"])
D_AZ1_MAX = 12.0
PARAMS = dict(BASE, d_az1=0.0)
_DYAD = {}


def _dyad():
    """the lead's seat rays: a1 = angle(d1, d2), a2 = angle(d2, d3), branch = sign(d2 . (d1 x d3)) (scapula frame)"""
    if not _DYAD:
        P = BASE; R = OSN.rest()
        d1 = OSN.seat(S.bvec(P["az1"], P["el1"]), P["b1"])[1]; d2 = OSN.seat(S.bvec(P["az2"], P["el2"]), P["b2"])[1]
        d3 = OSN.seat(R["Q0"] @ S.w_dir(P["wd"], P["wa"]), P["b3"])[1]
        _DYAD.update(a1=math.acos(float(np.clip(d1 @ d2, -1, 1))), a2=math.acos(float(np.clip(d2 @ d3, -1, 1))),
                     br=float(np.sign(d2 @ np.cross(d1, d3)) or 1.0), d3=d3)
    return _DYAD


def resolve_j2(az1, el1):
    """J2's seat (az2, el2) on the lead's branch keeping a1 / a2 (b1 = b2 = 0: seat axis = ray)"""
    Y = _dyad(); d1 = S.bvec(az1, el1)
    c = math.cos(Y["a1"]), math.cos(Y["a2"]); dd = float(np.clip(d1 @ Y["d3"], -1, 1)); n = np.cross(d1, Y["d3"]); n = n / np.linalg.norm(n)
    den = 1 - dd ** 2; a = (c[0] - dd * c[1]) / den; b = (c[1] - dd * c[0]) / den; p_ = a * d1 + b * Y["d3"]; h2 = 1 - float(p_ @ p_)
    ok = h2 > 0; d2 = p_ + Y["br"] * math.sqrt(max(h2, 0.0)) * n; d2 = d2 / np.linalg.norm(d2)
    el2 = math.degrees(math.asin(float(np.clip(d2[1], -1, 1)))); az2 = math.degrees(math.atan2(float(d2[2]), float(-d2[0])))
    return az2, el2, bool(ok)


def _clamp(p):
    p = dict(p); d = min(max(float(p.get("d_az1", 0.0)), -5.0), D_AZ1_MAX); p["d_az1"] = d
    p["az1"] = AZ1_0 + d; p["el1"] = float(BASE["el1"])
    p["az2"], p["el2"], _ = resolve_j2(p["az1"], p["el1"])
    return CC._clamp(p)


def probe(M, B, thrs=(0.1, 0.2)):
    """tolerance probe (round-15 rule): the gap with every taken pose whose lowest metal (walls / crowns / tops / edges,
    PK.audit's reading) is under thr mm counted as contact = the claim if the metal sat thr mm lower"""
    taken = lambda i: B.res[i] is not None and float(np.min(B.res[i])) >= 0
    mins = [(min(float(np.min(B.res[i])), M.cmin.get(i, 1e9)), i) for i in range(len(B.idx)) if taken(i)]
    res0 = list(B.res); out = {}
    for t in thrs:
        for d, i in mins:
            if d < t: B.res[i] = np.r_[B.res[i], -1e-3]
        out[f"gap_probe{t:g}"] = B.report()["gap"]; out[f"probe{t:g}_poses"] = int(sum(1 for d, i in mins if d < t)); B.res = list(res0)
    sh = [d for d, i in mins if 1.0 <= d < 2.0]
    out["shell12_poses"] = len(sh)
    return out


def _report(B, params):
    p = _clamp(dict(PARAMS, **params))
    r, M = CC._report(B, p)
    try: r.update(probe(M, B))
    except Exception as e: r["probe_err"] = str(e)[:100]
    try:
        r["seats"] = dict(d_az1=p["d_az1"], az1=round(p["az1"], 4), el1=round(p["el1"], 4), az2=round(p["az2"], 4), el2=round(p["el2"], 4),
                          a1=round(float(getattr(M.D, "a1", float("nan"))), 3), a2=round(float(getattr(M.D, "a2", float("nan"))), 3))
    except Exception as e: r["seats"] = dict(err=str(e)[:100])
    return r, M


def evaluate(B, params):
    """objective = the 1 mm near-touch gap (CLAUDE.md search rule); r['plain'] keeps the plain gap"""
    r, M = _report(B, params)
    if r.get("gap_near1") is not None: r["gap"] = r["gap_near1"]
    if r.get("sidecar_fail") or r.get("drive_idle") or r.get("pa_fail") or r.get("knee_moved"): r["honest"] = False
    p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    p["d_az1"] = float(_clamp(dict(PARAMS, **params))["d_az1"])
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); return r


def bench_envh():
    """envh (tools/freek_env_polish.py bench_envh, re-built here without importing the freek verifier): Bench(60,160)'s 60
    clip frames + 210 fresh env workspace poses, local fast cache .cache/concept_bench/envh-491cc8b49f3d; no held-out pose"""
    import env_bench as EB
    E = json.load(open(os.path.join(REPO, "docs", "research", "freek_env_polish", "envh.json")))
    old = os.environ.pop("CB_EXACT", None)
    try: B60 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    cl = [i for i, k in enumerate(B60.kind) if k == "clip"]
    Benv = EB.bench("env", exact=True); ws_pos = E["env_ws_positions"]
    idx = np.r_[np.asarray(B60.idx)[cl], np.asarray(Benv.idx)[ws_pos]]; key = "envh-" + CB._key(idx); assert key == E["key"]
    Z = CB._poses_all(); names = list(Z["NAMES"]); cid = Z["CID"]
    old = os.environ.get("CB_EXACT"); os.environ["CB_EXACT"] = "1"; os.environ["CB_QUIET_EXACT"] = "1"
    try: B = CB.Bench(20, 20)
    finally:
        if old is None: os.environ.pop("CB_EXACT")
        else: os.environ["CB_EXACT"] = old
    B.idx = idx; B.kind = ["clip"] * len(cl) + ["ws"] * len(ws_pos); B.clip = [str(names[c]) for c in cid[idx]]
    B.poses = [dict(plane=float(p[0]), elev=float(p[1]), axial=float(p[2]), flex=float(p[3]), pron=float(p[4])) for p in Z["POSE"][idx]]
    B.res = [None] * len(idx); B._skin = {}; B._ex = {}; B._frames = {}; B.key = key
    d = os.path.join(CB.CACHE, key)
    B.meta = json.load(open(os.path.join(d, "meta.json"))); B.grid = np.load(os.path.join(d, "grid.npy"), mmap_mode="r")
    B._V = np.load(os.path.join(d, "skins.npy"), mmap_mode="r"); B.mode = "fast"
    hidx, _ = EB.held_idx(); assert not (set(idx.tolist()) & set(hidx.tolist())), "a held-out pose in envh"
    return B


def _with_fit_bench(fn):
    """ACRO_FIT=envh: the claim protocol's fit bench is envh instead of Bench(60,160) (a config searched on envh is frozen
    from its own fit, as the freek polish's 'claim envh'); default: the lead's protocol unchanged"""
    def run(*a):
        if os.environ.get("ACRO_FIT") != "envh": return fn(*a)
        orig = CC.CB.Bench; Be = bench_envh()
        def Bench(n_clip=60, n_ws=160, *k, **kw):
            if n_clip == 60 and n_ws == 160 and os.environ.get("CB_EXACT") != "1":
                Be.res = [None] * len(Be.idx); return Be
            return orig(n_clip, n_ws, *k, **kw)
        CC.CB.Bench = Bench
        try: return fn(*a)
        finally: CC.CB.Bench = orig
    return run


@_with_fit_bench
def frozen(P, nc=110, nw=360): return CC.frozen(_clamp(dict(PARAMS, **P)), nc, nw)
@_with_fit_bench
def frozen_held(P): return CC.frozen(_clamp(dict(PARAMS, **P)), -1, -1)
def frozen_flood(P, nc=110, nw=360): return CC.frozen_flood(_clamp(dict(PARAMS, **P)), nc, nw)
def viz_export(par): return CC.viz_export(_clamp(dict(PARAMS, **par)))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "seats":
        for d in (-5, 0, 2.5, 5, 7.5, 10, 12):
            print(d, [round(x, 4) if isinstance(x, float) else x for x in resolve_j2(AZ1_0 + d, BASE["el1"])])
        sys.exit()
    if mode == "viz":
        print(json.dumps(viz_export(par), default=float)); sys.exit()
    if mode in ("frozen", "held", "flood"):
        t = time.time(); out = {"frozen": frozen, "held": frozen_held, "flood": frozen_flood}[mode](par); out["params"] = par
        out["row"] = ID; out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        a = out.get("audit", {})
        print(json.dumps(dict(row=ID, fit=out.get("fit_fast"), frozen=out["frozen"], why=out.get("why"), near1=a.get("gap_near1"),
                              near2=a.get("gap_near2"), minmetal=a.get("near_touch_min_mm"), ovh=out.get("overhead"), knee=out.get("knee"),
                              clips=out.get("clips"), contacts=out.get("contact_poses"), stopped=out.get("stopped"),
                              connected=out.get("connected"), cam=out.get("cam"), secs=out["secs"]), default=float)); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report(B, par)
    print(json.dumps(dict(row=ID, gap=r["gap"], plain=r.get("plain"), near1=r.get("gap_near1"), near2=r.get("gap_near2"), min_metal=r.get("min_metal_mm"),
                          reach=r["reach"], follow=r["follow"], inband14=r["inband14"], inband10=r.get("inband10"), contact=r["contact"], honest=r.get("honest"),
                          why=r.get("why"), ovh=r.get("overhead140"), seats=r.get("seats"), cam={k: (r.get("cam") or {}).get(k) for k in ("dK_lim", "pa_crank_max_taken", "pa_horn_max_taken", "pa_eff_horn", "pa_eff_crank")},
                          knee=r.get("knee"), secs=round(time.time() - t)), default=float))
