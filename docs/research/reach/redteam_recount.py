"""Red team of docs/research/reach_attribution.md (2026-10-16): an independent re-count of the fold losses and two ceilings.

Shares no code with attribute.py / analyse.py / ceilings.py / frontier_mine.py / relay_parking.py. Inputs: the bench's
own pose table (tools/concept_bench.py _poses_all / _select: the SAME 110 + 360 frames the verifiers wear), the verified
parameters in docs/concepts/verify/, and the models' own Design classes for the axis directions (pin knee: the b3 tilt
toward the skin normal needs the model's rest skin). The fold test is NOT the closed-form th window: for each pose it
samples the J2 axis on its circle about J1 (radius a1, 7200 steps) and asks whether the circle comes within a2 - m and
a2 + m of the posed J3 axis (the two-circle intersection with the margin taken as an angle on the J2 circle). Folded
side = the J2 circle cannot get FAR enough from J3 (th small), stretched = it cannot get CLOSE enough.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/research/reach/redteam_recount.py [out.json]
"""
import importlib.util, json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

R2D = 180 / math.pi
NPHI = 7200


def load(name, path):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


def my_bvec(az, el):
    """scapula frame: y up, az measured from POSTERIOR (az 0) toward lateral (90): own construction from the kit docstring"""
    a, e = math.radians(az), math.radians(el)
    post, lat, up = np.array([-1.0, 0, 0]), np.array([0, 0, 1.0]), np.array([0, 1.0, 0])
    return math.cos(e) * (math.cos(a) * post + math.sin(a) * lat) + math.sin(e) * up


def my_wdir(d, a):
    """humerus band frame: d from the down-the-arm axis (-y), a 0 lateral (+z), 90 anterior (+x)"""
    d, a = math.radians(d), math.radians(a)
    return math.cos(d) * np.array([0, -1.0, 0]) + math.sin(d) * (math.cos(a) * np.array([0, 0, 1.0]) + math.sin(a) * np.array([1.0, 0, 0]))


def circle_test(u1, u3, a1, a2, Q, m):
    """grid IK of the J2 axis. Returns ok (n,), side (n,) 'f' / 's' / '' and the J1-J3 angle (deg) for the record."""
    u1 = u1 / np.linalg.norm(u1); e1 = np.cross(u1, [0.3, 0.7, 0.1]); e1 /= np.linalg.norm(e1); e2 = np.cross(u1, e1)
    ph = np.linspace(0, 2 * np.pi, NPHI, endpoint=False)
    U2 = math.cos(math.radians(a1)) * u1[None] + math.sin(math.radians(a1)) * (np.cos(ph)[:, None] * e1 + np.sin(ph)[:, None] * e2)
    W = Q @ u3                                                # posed J3 axis in the scapula frame
    ang = np.degrees(np.arccos(np.clip(W @ U2.T, -1, 1)))     # (n, NPHI) angle J2-J3 along the circle
    dmin, dmax = ang.min(1), ang.max(1)
    ok = (dmin <= a2 - m) & (dmax >= a2 + m)
    side = np.where(ok, "", np.where(dmin > a2 - m, "s", "f"))
    th = np.degrees(np.arccos(np.clip(W @ u1, -1, 1)))
    return ok, side, th, dmin, dmax


def axes_pin_knee():
    P = json.load(open(os.path.join(REPO, "docs/concepts/verify/skin-normal-3r-pin-knee_big_frozen.json")))["params"]
    MKm = load("rt_pk", os.path.join(REPO, "docs/concepts/models/skin-normal-3r-pin-knee.py"))
    D = MKm.Design(P); return D.u[0], D.u[2], math.degrees(D.A[0]), math.degrees(D.A[1])


def axes_spine():
    P = json.load(open(os.path.join(REPO, "docs/concepts/verify/spine-parked-j2-3r.results.json")))["G_frozen"]["params"]
    return my_bvec(P["az"], P["el"]), my_wdir(P["wd"], P["wa"]), P["a1"], P["a2"]


def axes_from_run(leader):
    s = json.load(open(os.path.join(HERE, "runs", f"{leader}_m10.json")))["seats"]
    return np.array(s["u1"]), np.array(s["u3_home"]), s["a1"], s["a2"]


def main(out):
    Z = CB._poses_all(); HG = Z["HG"].astype(float)
    idx, names, cid, P = CB._select(110, 360); ws = idx[110:]
    idx60, *_ = CB._select(60, 160); ws160 = idx60[60:]
    ws_all = np.nonzero(cid == names.index("Workspace (envelope)"))[0]
    pose = P[ws]; over = pose[:, 1] >= 140
    res = {}
    axes = {"pin-knee": axes_pin_knee(), "spine": axes_spine(), "raglan": axes_from_run("raglan"), "knuckle": axes_from_run("knuckle")}
    for L, (u1, u3, a1, a2) in axes.items():
        r = dict(a1=a1, a2=a2)
        ok, side, th, dmin, dmax = circle_test(u1, u3, a1, a2, HG[ws], 10.0)
        r["m10"] = dict(in_window=int(ok.sum()), folded=int((side == "f").sum()), stretched=int((side == "s").sum()),
                        overhead_in=int(ok[over].sum()), overhead_f=int((side[over] == "f").sum()), overhead_s=int((side[over] == "s").sum()),
                        clip_fold=int((~circle_test(u1, u3, a1, a2, HG[idx[:110]], 10.0)[0]).sum()))
        for m in (7, 5, 2, 0):
            r[f"m{m}_share"] = round(float(circle_test(u1, u3, a1, a2, HG[ws], m)[0].mean()), 4)
        r["share160_m10"] = round(float(circle_test(u1, u3, a1, a2, HG[ws160], 10.0)[0].mean()), 4)
        r["share_envelope_m10"] = round(float(circle_test(u1, u3, a1, a2, HG[ws_all], 10.0)[0].mean()), 4)
        # per-pose agreement with the attribution's CSV
        csvp = os.path.join(HERE, f"{L}_poses.csv")
        if os.path.exists(csvp):
            import csv
            rows = [x for x in csv.DictReader(open(csvp)) if x["kind"] == "ws"]
            cf = np.array([x["cause"] == "fold_folded" for x in rows]); cs = np.array([x["cause"] == "fold_stretched" for x in rows])
            taken = np.array([x["taken"] == "True" for x in rows])
            r["csv_agree"] = dict(folded_same=bool(np.array_equal(cf, side == "f")), stretched_same=bool(np.array_equal(cs, side == "s")),
                                  n_csv_ws=len(rows), csv_lost=int((~taken).sum()), lost_in_window=int(((~taken) & ok).sum()),
                                  taken_outside_window=int((taken & ~ok).sum()))
        # relay union (a1 -> a1'): the claim says a1' 77-84 gives 0.93-0.95
        for a1b in (77, 80, 84):
            okb = circle_test(u1, u3, a1b, a2, HG[ws], 10.0)[0]
            r[f"relay_a1_{a1b}"] = dict(union=round(float((ok | okb).mean()), 4), overhead=round(float((ok | okb)[over].mean()), 4))
        res[L] = r
        print(L, json.dumps(r), flush=True)
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "redteam_recount.json"))
