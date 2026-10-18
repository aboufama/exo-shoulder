"""slotted-eccentric-pin-knee-3r: the eccentric slotted-lever J2 (link 2 split at a passive knee K slaved to q2 by a roller
in a slot; docs/concepts/models/slotted-eccentric-j2-3r.py, the INVERTED cam: roller G on link 2b, the track on link 1)
put on the pin-knee chain's J1 / J3 axis directions (skin-normal-3r-pin-knee H1, or lens 3's crest seats), with the knee
hub K at O20 (v5 stack, MR117-2RS pair, 12.25 mm; O20-only rule) - round 14, lens 3 cell B.

What this file measures (and why it is enough to decide the cell). The eccentric's metal - crank 2a, knee hub K, link 2b,
the slot track on link 1, the roller stud G - sits between J2 and J3, upstream of member 3. The pin knee only changes
member 3's motion relative to the arm (planar about d3, docs/concepts/skin-normal-3r-pin-knee.md); it does not change
the J1 / J2 / K / J3 axis directions per pose (J1, J2, K on GH rays; J3's direction d3 = the H1 tilted axis). So the
eccentric is judged PAIRED: slot (lock=0) vs its own locked control (lock=1: the same chain with link 2 rigid through K,
i.e. the plain 3R), through identical code (the parent's kit model: K3 march, K2 dense incl. axes K and G, K6 with the
same-body exemption, honest posts, crowns + walls, declared pins, the slot gate: lock angle of the internal four-bar
mode >= lock_min, normal component >= g_min, G-K-J2 alignment >= 10 deg, track self-overlap), at the pin-knee's axis
directions. Member 3 is the kit's neck in both arms of the pair; the pin-knee number of a cell is its own verified
control plus the paired delta (the cuff closure is downstream of every eccentric part).

Rules enforced as hard search-box edges (round-13 process lesson): O20 at J1 / J2 / J3 AND at K (rad 10, stack 12.25),
fold margin >= 5.23 (5 + the ~0.23 deg K play) in the ONE metric th (tools/concept_kit.py), knee transmission psi in
[psi_lo, 180 - psi_lo] with psi_lo >= 15, slot lock >= 50 deg (pressure angle <= 40), no gears / pulleys / cables.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/slotted-eccentric-pin-knee-3r.py check '<json>'
    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/slotted-eccentric-pin-knee-3r.py scan  [H1|crest]
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
    big:   CB_EXACT=1 python3 docs/concepts/models/slotted-eccentric-pin-knee-3r.py frozen '<json>' --out R.json
"""
import importlib.util, itertools, json, math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402
_sp = importlib.util.spec_from_file_location("slotted_eccentric_parent", os.path.join(HERE, "slotted-eccentric-j2-3r.py"))
SE = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(SE)

ID = "slotted-eccentric-pin-knee-3r"
NAME = "Pin knee 3R with the eccentric slotted-lever J2 (moving fold boundary), O20 knee hub"
MARGIN_RULE, PSI_RULE, LOCK_RULE = 5.23, 15.0, 50.0
# axis directions of the pin-knee chain (computed from the verified rows' Design: J1 = bvec(az, el); J3 = the H1 TILTED
# axis d3 expressed as wdir(wd, wa) in the humerus frame; a1 = angle(J1, J2 home), a2 = angle(J2 home, J3); branch -1)
SEATS = dict(H1=dict(az=101.1634, el=63.8986, a1=41.018, a2=68.259, wd=78.5492, wa=-5.3421, sigma=-1),
             crest=dict(az=106.3227, el=62.8675, a1=40.883, a2=55.011, wd=99.3641, wa=-0.0249, sigma=-1))
PARAMS = dict(SE.PARAMS)
PARAMS.update(SEATS["H1"])
PARAMS.update(rpin=10.0, pin_t=K.CROWN, margin=MARGIN_RULE, psi_lo=PSI_RULE, lock_min=LOCK_RULE,
              Amin=62.0, Amax=96.0, w=3.0, sl=1.0, b=24.0, c=74.0, sk=1, lock=0)
build = SE.build


def _clean(params):
    p = dict(PARAMS, **params)
    p.update(rpin=10.0, pin_t=K.CROWN, rad1=10.0, rad2=10.0, rad3=10.0)          # O20 at every joint incl. K (rule)
    if os.environ.get("SEPK_O10_PROBE") == "1":       # ATTRIBUTION PROBE ONLY (never a claim): the parent's O10 MR63ZZ knee
        p.update(rpin=5.0, pin_t=6.5)
    p["margin"] = max(MARGIN_RULE, float(p["margin"])); p["psi_lo"] = max(PSI_RULE, float(p["psi_lo"]))
    p["lock_min"] = max(LOCK_RULE, float(p["lock_min"]))
    p["b"] = max(20.0, float(p["b"]))                       # two O20 hubs (J2, K) side by side: >= 21.6 mm at r 62
    return p


def evaluate(B, params):
    return SE.evaluate(B, _clean(params))


def bench_eval(B, params):
    _, r = evaluate(B, params)
    return {k: v for k, v in r.items() if SE._jsonable(v)}


def th_of_bench(B, seat):
    """per-pose J1-J3 angle th (deg) on bench B at a seat's axis directions (workspace + clip frames, the bench's order)"""
    rec = []
    def bld(B_, F, p):
        p1 = F.S(K.bvec(p["az"], p["el"])); p3 = F.HG(K.wdir(p["wd"], p["wa"])); rec.append(np.atleast_1d(SE.ang(p1, p3)))
        return SE.build(B_, F, p)
    K.evaluate(B, bld, _clean(dict(SEATS[seat], lock=1)))
    return np.concatenate(rec)


def scan(seat="H1"):
    """seat-independent slot gate over the law (a1 fixed by the seat): the lock-held track's th range [lo, hi] vs the
    plain dyad window [|a1 - a2| + m, a1 + a2 - m], weighted by the bench's own th distribution at the seat"""
    B = K.bench(60, 160); th = th_of_bench(B, seat); s = SEATS[seat]; m = MARGIN_RULE
    plain = (abs(s["a1"] - s["a2"]) + m, s["a1"] + s["a2"] - m)
    cov = lambda lo, hi: float(((th >= lo) & (th <= hi)).mean())
    out = dict(seat=seat, n=len(th), th_p5_p95=[round(float(np.percentile(th, 5)), 1), round(float(np.percentile(th, 95)), 1)],
               plain=[round(plain[0], 2), round(plain[1], 2)], plain_cover=round(cov(*plain), 4), cells=[])
    grid = itertools.product((52, 58, 64, 68), (86, 94, 102), (20, 25, 30), (66, 74, 82), (0.6, 1.0), (1, -1))
    for Amin, Amax, b, c, sl, sk in grid:
        p = _clean(dict(s, Amin=Amin, Amax=Amax, b=b, c=c, sl=sl, sk=sk, w=3.0, lock=0))
        sd = SE.slot_design(p); g = sd.get("gate", {})
        lo, hi = (sd["lo"], sd["hi"]) if sd.get("passed") else (0.0, -1.0)
        out["cells"].append(dict(Amin=Amin, Amax=Amax, b=b, c=c, sl=sl, sk=sk, passed=bool(sd.get("passed")), lo=lo, hi=hi,
                                 cover=round(cov(lo, hi), 4), q2_span=g.get("q2_span"), slot_len=g.get("slot_len_mm"),
                                 lock_full=g.get("lock_full_run"), why=g.get("why")))
    out["cells"].sort(key=lambda c: -c["cover"]); return out


def attribute(params, B=None):
    """where the poses go: closure / window (not ok), part-part pairs (K6, per pair over the closing poses), contact; the
    fitted underside level of each member (mm from GH, max over the poses) and its in-band share"""
    import dataclasses
    B = B or K.bench(60, 160); p, r = evaluate(B, params); L = B._kit_last; ch, pts, ok, hit = L["chain"], L["pts"], L["ok"], L["hit"]
    M = ch.members; pairs = {}
    for a in range(len(M)):
        for b in range(a + 1, len(M)):
            h = K.collisions(dataclasses.replace(ch, members=[M[a], M[b]]), pts, ok)
            if h.any(): pairs[f"{M[a].name}|{M[b].name}"] = int(h.sum())
    lvl = {m.name: [round(float(np.min(L["prof"][m.name])), 1), round(float(np.max(L["prof"][m.name])), 1)] for m in M}
    out = dict(n=int(len(ok)), closes=int(np.sum(ch.ok)), cont_ok=int(ok.sum()), collide=int(hit[ok].sum()), taken=int(L["take"].sum()),
               pairs=dict(sorted(pairs.items(), key=lambda kv: -kv[1])[:12]), level_mm=lvl, inband_member=r.get("inband_member"),
               gap=r.get("gap"), reach=r.get("reach"), inband14=r.get("inband14"), contact=r.get("contact"), kin_reach=(r.get("th_need") or {}).get("kin_reach"))
    return out


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    if mode == "scan":
        seat = sys.argv[2] if len(sys.argv) > 2 else "H1"; t = time.time(); o = scan(seat)
        json.dump(o, open(sys.argv[3] if len(sys.argv) > 3 else f"scan_{seat}.json", "w"), indent=1, default=float)
        print({k: o[k] for k in ("seat", "n", "th_p5_p95", "plain", "plain_cover")}, f"{time.time() - t:.0f}s")
        for c in o["cells"][:12]: print(c)
        sys.exit()
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].startswith("{") else {}
    if mode == "attr":
        print(json.dumps(attribute(par), indent=1, default=float)); sys.exit()
    if mode == "frozen":
        o = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "frozen.json"
        SE.ID = ID; SE.frozen(_clean(par), o); sys.exit()
    B = K.bench(60, 160); t = time.time(); p, r = evaluate(B, par)
    print({k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "audit", "closure", "flips", "collide")},
          f"{time.time() - t:.1f}s")
    print("per member", r.get("inband_member"), "res", r.get("residual_deg"), "declared", r.get("declared_hubs"))
    print({k: r.get(k) for k in ("window", "a2eff_range", "knee_range", "psi_min", "slot_passed", "gap_near1", "min_metal_skin",
                                 "overhead", "th_need")})
    print("slot", {k: v for k, v in (r.get("slot_gate") or {}).items() if k not in ("nodes_e", "nodes_eta")})
