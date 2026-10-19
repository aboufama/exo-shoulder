"""sidecar-parallelogram-knuckle-3r (round 8, pick 1): the verified lead frontload-lobe-stopb-knuckle-3r chain (J1 acromion
top, link 1a, K knuckle slaved and never read, link 1b, J2, link 2, J3, pin knee + cuff) with ONLY the K drive rebuilt at
strap level: a lateral horn lug of link 1a at hub K, a bell crank on an MR63ZZ pair stacked on link 1b beside hub 2
(short arm s_arm on the hub-2 rim lobe, long arm La), and an O3 Ti rod on two M2 ball links beside link 1b. Nothing
crosses K's crown. 3 ACTIVE DOF (J1, J2, J3), 0 passive translations, no gears / pulleys / cables.

THE MECHANISM CODE IS SHARED, NOT COPIED: the per-pose RSSR placement, the drive-range truncation (transmission >= 30,
rod / crank >= 1 mm off hub 2 and link 1b), the stacking rule and every part pair live in
docs/concepts/models/sidecar-longdyad-knuckle-3r.py (pick 4 built the sidecar drive first and carries pick 1's cell as
its control D). This file is pick 1's own morphology on top of it:
  * chain='lead' (default): the lead's K dyad UNCHANGED (bk1 30.05 / bk2 37.57 / a1max 61.72, the spec's "lead chain
    unchanged"); chain='free' lets the dyad float as the spec's sweep list allows (= pick 4's control D);
  * the horn ball-link socket keeps >= 1 mm + the socket's catalogue tolerance off hub K: r_h >= R_H_MIN (15.5; the
    judge's pinch: at r_h 14.5 the O7 socket sits exactly 1.0 mm off hub K's cylinder; pick 4's best r_h 14.87 measured
    1.37 mm);
  * ends='rc' (default): RC-class M2 ball link, steel ball O4.8 on an M2 stud + acetal socket O7 x 7 (ER 3.5, ball centre
    ZB 3.0 over the lug / arm top); ends='ge4e': the all-metal fallback, a GE4E-class spherical plain bearing
    4 x 12 x 5 in a 1.5 mm eye (ER 6.0 + 1.5 = 7.5, ZB 5.0: ~2 mm taller) - measured as its own cell;
  * the idle-drive rule (spec MUST ADD 4): a configuration whose drive takes no stretched pose, or carries < 30 deg of K
    over the taken stretched poses, is dishonest (+100 in the CMA): it is a plain 3R with a spare passive joint.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/sidecar-parallelogram-knuckle-3r.py [check] ['<json>']
    CB_EXACT=1 python3 docs/concepts/models/sidecar-parallelogram-knuckle-3r.py frozen|held|flood '<json>' [out.json]
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

_sp = importlib.util.spec_from_file_location("sidecar_core_for_parallelogram", os.path.join(HERE, "sidecar-longdyad-knuckle-3r.py"))
SC = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(SC)
ID = "sidecar-parallelogram-knuckle-3r"
R_H_MIN = 15.5                                               # rc ends; ge4e: 19.5 (HUB_R + ER + 2)
LEAD_DYAD = {"bk1": 30.05, "bk2": 37.57, "a1max": 61.72}
ENDS = {"rc": dict(ER=3.5, ZB=3.0), "ge4e": dict(ER=7.5, ZB=5.0)}
DK_IDLE = 30.0

# the judge's seed for pick 1: the lead's seats, r_h 15 (-> 15.5 floor), beta -110, hl 3.15, zr 1.5, La 18, kK 2.0
SEED = dict(SC.LEAD, **LEAD_DYAD, law_mode="lin", kK=2.0, r_h=15.5, beta=-110.0, hl=3.15, zr=1.5, La=18.0, s_arm=5.0,
            r_lobe=7.5, gam=0.0, chain="lead", ends="rc")
PARAMS = dict(SC.PARAMS, **SEED)


def _prep(params):
    p = dict(PARAMS, **params)
    if p.get("chain", "lead") == "lead": p.update(LEAD_DYAD)
    e = ENDS[p.get("ends", "rc")]; SC.ER, SC.ZB = e["ER"], e["ZB"]       # module constants read by SCModel._rod_metal
    p["r_h"] = max(float(p["r_h"]), SC.S.HUB_R + e["ER"] + 2.0)          # socket >= 1 mm + 1 mm tolerance off hub K (rc 15.5, ge4e 19.5)
    return p


def _report(B, params):
    p = _prep(params)
    r, M = SC._report(B, p)
    d = r.get("drive") or {}
    if d and not r.get("drive_idle") and d.get("dK_taken_max", 99.0) < DK_IDLE:
        r["drive_idle"] = True; r["honest"] = False                    # the drive carries < 30 deg: a spare passive joint
    if d: d.update(chain=p.get("chain"), ends=p.get("ends"), r_h_floor=round(SC.S.HUB_R + SC.ER + 2.0, 2))
    return r, M


def evaluate(B, params):
    r, M = _report(B, params)
    if r.get("sidecar_fail") or r.get("drive_idle"): r["honest"] = False
    p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); return r


def frozen(P, nc=110, nw=360): return SC.frozen(_prep(P), nc, nw)
def frozen_held(P): return SC.frozen(_prep(P), -1, -1)
def frozen_flood(P, nc=110, nw=360): return SC.frozen_flood(_prep(P), nc, nw)


def viz_export(par):
    SC.FL._report = lambda B, p: SC._report(B, _prep(p))
    return SC.FL.viz_export(_prep(par))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "viz":
        print(json.dumps(viz_export(par), default=float)); sys.exit()
    if mode == "flood":
        t = time.time(); out = frozen_flood(par); out["params"] = par; out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        print(json.dumps(out, default=float)[:3000]); sys.exit()
    if mode in ("frozen", "held"):
        t = time.time(); out = frozen(par) if mode == "frozen" else frozen_held(par); out["params"] = par; out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        a = out.get("audit", {})
        print(json.dumps(dict(fit=out["fit_fast"], frozen=out["frozen"], why=out["why"], near1=a.get("gap_near1"), minmetal=a.get("near_touch_min_mm"),
                              ovh=a.get("overhead140"), parts=out.get("parts_ib14"), sidecar=out.get("sidecar"), secs=out["secs"]), default=float)); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report(B, par)
    print(json.dumps(dict(gap=r["gap"], plain=r.get("plain"), near1=r.get("gap_near1"), min_metal=r.get("min_metal_mm"), reach=r["reach"],
                          inband14=r["inband14"], contact=r["contact"], honest=r.get("honest"), idle=r.get("drive_idle"), why=r.get("why"),
                          ovh=r.get("overhead140"), drive=r.get("drive"), parts=r.get("parts_ib14"), clear=getattr(M, "last_clear", None),
                          secs=round(time.time() - t)), default=float))
