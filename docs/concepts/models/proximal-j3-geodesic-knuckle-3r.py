"""proximal-j3-geodesic-knuckle-3r (round 13): the long-dyad 32/48 knuckle chain with J3's seat moved up and back the
lateral deltoid (the J1-J3 geodesic's ARM end), the knee re-fit at the MR63ZZ build stack (stk 6.0), and the K law
re-tuned where a shorter link 2 moves the stretched wall.

Morphology (docs/concepts/proximal-j3-geodesic-knuckle-3r.md): scapula handler -> J1 (ACTIVE, O20, acromion-top seat)
-> link 1a (bk1 32) -> K (PASSIVE, slaved to th by the K drive) -> link 1b (bk2 48) -> J2 (ACTIVE, O20, posterolateral cap)
-> link 2 (3 mm Ti bar) -> J3 (ACTIVE, O20, seat wd ~71-76 deg from the humeral shaft) -> member 3 / E strap -> two-pin
knee (MR63ZZ pairs, outside the count) -> arm pad on BOTTOM. 3 ACTIVE DOF, 0 passive translations.

WHAT THIS FILE MODELS (and what it does not):
  * the chain, K dyad, knee, seats, law and every member's metal are desmo-vrocker-longdyad-knuckle-3r.py's (loaded
    UNCHANGED; it loads spiral-lobe -> inband-rssr unchanged) at the round-12 best long-dyad cell (32/48, kK 2.4, onset
    smhi 14, cap 56, pick3's J1 / hub-2 seats), with wd / wa (J3's seat), the knee (lE, lc, phiE, phib, ang_min at stk
    6.0) and the K law (smhi, kK, kcap) free;
  * the K DRIVE's metal is NOT sampled (IB_GHOST=all): every number from this file is a GHOST - the chain's ceiling
    before the drive's metal (gate 1 of the round-13 plan). It is never a claim; gate 2 must place a real drive on 32/48.
  * search objective: the 1 mm near-touch gap (LS_OBJ=near1, CLAUDE.md "search on the near-touch gap").

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/proximal-j3-geodesic-knuckle-3r.py [check] ['<json>']
    CB_EXACT=1 ... frozen '<json>' [out.json]      (fit Bench(60,160) fast, shape frozen, worn on Bench(110,360) exact)
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, os, sys, time

os.environ["IB_GHOST"] = "all"
os.environ.setdefault("LS_OBJ", "near1")                    # the 1 mm near-touch search objective (read at import below)
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

_sp = importlib.util.spec_from_file_location("vr_for_proximal_j3", os.path.join(HERE, "desmo-vrocker-longdyad-knuckle-3r.py"))
VR = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(VR)
LS, IB = VR.LS, VR.IB
ID = "proximal-j3-geodesic-knuckle-3r"
GHOST_ONLY = True
# the round-12 best long-dyad ghost cell (desmo-vrocker g0_s14c56k24: frozen exact 17.23, 269 taken, 6 contacts) ...
BASE = dict(bk1=32.0, bk2=48.0, a1max=74.5, kK=2.4, La=24.0, s_arm=4.0, r_h=15.25, beta=-140.3619, gam=11.9079, hl=3.15, zc=0.8878,
            eta=-11.1256, r_lobe=8.0, smlo=5.0333, az1=95.3275, el1=67.6601, az2=46.3741, el2=41.5718, wd=66.0692, wa=-10.7812,
            b3=0.3246, ang_min=25.2189, lc=21.5474, phib=-57.916, clay=1, bl_c=2, bl_h=0, smhi=14.0, kcap=56.0,
            lE=67.832, phiE=-2.7863, stk=4.8534)
# ... with this row's change: J3's seat up the geodesic (the judge's wd 73 cell) and the knee at the MR63ZZ build stack
SEED = dict(BASE, wd=73.0, stk=6.0, l2v=0.0)
PARAMS = dict(VR.PARAMS, **SEED)
_vr_clamp = VR._clamp
L2V_MAX = 2.0                                                # link-2 bar offset bound (mm): the 8 mm bar stays on the O20 hub faces


def _clamp(p):
    l2v = p.get("l2v", 0.0)
    p = _vr_clamp(p); p["l2v"] = min(max(float(l2v or 0.0), -L2V_MAX), L2V_MAX)
    return p


# --- the posterior-edge column: link 2's 8 mm bar offset l2v mm across its great circle (+ = toward cross(hub2, hub3),
#     anterior on this chain; the round-13 binder sits on the bar's v -3 row). The bar keeps its real width and section.
import numpy as _np                                          # noqa: E402
KB = VR.FL.G.KR.KB
_orig_add_links = KB.KGeo.add_links


def _unit(v): v = _np.asarray(v, float); return v / (_np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


def _add_links(self, f1, fK, f2, f3):
    out = _orig_add_links(self, f1, fK, f2, f3)
    P = getattr(self.D, "p", None) or {}
    off = float(P.get("l2v", 0.0) or 0.0)
    if abs(off) < 1e-9: return out
    D = self.D; U = [D.u[0], D.uK, D.u[1], D.u[2]]; Cc = [D.c[0], _np.zeros(3), D.c[1], D.c[2]]; F = [f1, fK, f2, f3]
    hr = [self.hr[0], KB.S.HUB_R, self.hr[1], self.hr[2]]; SP = KB.S.SPACING
    C = [Cc[k] + F[k] * U[k] for k in range(4)]
    for L in out:
        if L["name"] != "L2": continue
        ka, kb = L["ka"], L["kb"]; da, db = _unit(C[ka]), _unit(C[kb]); R = 0.5 * (_np.linalg.norm(C[ka]) + _np.linalg.norm(C[kb]))
        ang = float(_np.arccos(_np.clip(da @ db, -1, 1))); bn = _unit(_np.cross(da, db))
        nn = max(4, int(R * ang / SP)); ts = (_np.arange(nn) + 0.5) / nn
        dirs = _np.array([_unit(_np.sin((1 - t) * ang) * da + _np.sin(t * ang) * db) for t in ts])
        rows = []
        for v in (-3.0, -1.0, 1.0, 3.0):
            dv = _unit(dirs + ((v + off) / R) * bn); pts = R * dv
            def off_axis(k): w = pts - Cc[k]; return _np.linalg.norm(w - (w @ U[k])[:, None] * U[k], axis=1)
            keep = (off_axis(ka) > hr[ka]) & (off_axis(kb) > hr[kb])
            rows.append((dv, keep, ts * R * ang))
        L["rows"] = rows
    self.links = out
    return out


KB.KGeo.add_links = _add_links
LS.PARAMS = PARAMS; IB.PARAMS = PARAMS; VR.PARAMS = PARAMS
LS._clamp = _clamp; IB._clamp = _clamp; VR._clamp = _clamp; VR.SLm._clamp = _clamp; VR.SC._clamp = _clamp
_report = VR._report; frozen = VR.frozen; frozen_held = VR.frozen_held; frozen_flood = VR.frozen_flood; viz_export = VR.viz_export


def _full(params): return dict(SEED, **params)


def evaluate(B, params):
    p, r = VR.evaluate(B, _full(params)); r["ghost"] = True; return p, r


def bench_eval(B, params):
    r = VR.bench_eval(B, _full(params)); r["ghost"] = True; return r


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = _full(json.loads(sys.argv[2]) if len(sys.argv) > 2 else {})
    if mode == "viz":
        print(json.dumps(viz_export(par), default=float)); sys.exit()
    if mode in ("frozen", "held", "flood"):
        t = time.time(); out = {"frozen": frozen, "held": frozen_held, "flood": frozen_flood}[mode](par); out["params"] = par
        out["row"] = ID; out["ghost"] = "K drive metal not sampled (gate 1 ghost)"; out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        a = out.get("audit", {})
        print(json.dumps(dict(row=ID, fit=out.get("fit_fast"), frozen=out["frozen"], why=out.get("why"), near1=a.get("gap_near1"),
                              near2=a.get("gap_near2"), minmetal=a.get("near_touch_min_mm"), ovh=out.get("overhead"),
                              depth={k: v for k, v in (out.get("contact_depth") or {}).items()}, th_margin=out.get("th_margin"),
                              parts=out.get("parts_ib14"), connected=out.get("connected"), secs=out["secs"]), default=float)); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    p, r = evaluate(B, par)
    print(json.dumps(dict(row=ID, ghost=True, gap=r["gap"], plain=r.get("plain"), near1=r.get("gap_near1"), near2=r.get("gap_near2"),
                          min_metal=r.get("min_metal_mm"), reach=r["reach"], inband14=r["inband14"], contact=r["contact"], honest=r.get("honest"),
                          why=r.get("why"), ovh=r.get("overhead140"), parts=r.get("parts_ib14"), secs=round(time.time() - t)), default=float))
