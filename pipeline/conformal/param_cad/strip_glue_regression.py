"""R7 regression of the shared strip glue (user_style_minarc.glue_strips / sliver_free): run a full-CAD builder up to its links,
then judge every link part with judge/part_validity.py's own test (STEP write + read back + BRepCheck per face, solid count)
plus the zero-area face count. Nothing is written to the design directories (the builder stops after its links).

    OMP_NUM_THREADS=1 nice -n 10 python3 pipeline/conformal/param_cad/strip_glue_regression.py minarc --out user_minarc_bdp --l1 l1_minarc-bdp \
        --params-file docs/concepts/verify/minarc-kitrule/params_floorBD5_phys_cap6.json --a1max 54.748            # gen 4b
    ... minarc --out user_minarc_pick1 --l1 l1_minarc-pick1 --params-file docs/research/minarc_final_polish/picks/pick1_priced.json --a1max 66.4696
    ... geneva --out user_geneva_rod --l1 l1_geneva-rod                                                              # gen 5
    ... roller                                                                                                      # gen 6 (links 1a / 1b / 2)
-> docs/research/roller-longdyad-gen6_fix/strip_glue_regression_<which>_<out>.json"""
import os, sys, json
which, args = sys.argv[1], sys.argv[2:]
sys.argv = [sys.argv[0]] + args
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
import user_style_minarc as USM                                                            # noqa: E402
OUT = os.path.join(REPO, "docs", "research", "roller-longdyad-gen6_fix")


def judge_links(lk, tag):
    out = []
    for g, n, s in lk:
        bad, zero, ns = USM.step_bad_faces(s)
        out.append(dict(part=n[:70], group=g, valid=bool(s.isValid()), step_bad_faces=bad, zero_area_faces=zero, solids_after_step=ns,
                        passes_R7=bool(s.isValid() and bad == 0 and ns == 1)))
        print(f"REGRESS {tag} {n[:50]:50s} valid {s.isValid()} STEP bad {bad} zero-area {zero} solids {ns}", flush=True)
    os.makedirs(OUT, exist_ok=True)
    json.dump(dict(builder=which, args=args, parts=out, all_pass=all(r["passes_R7"] for r in out)),
              open(os.path.join(OUT, f"strip_glue_regression_{tag}.json"), "w"), indent=1)


if which in ("minarc", "geneva"):
    orig = USM.build_links
    def wrapped(M, stops, *a, **k):
        lk, rep = orig(M, stops, *a, **k)
        o = args[args.index("--out") + 1] if "--out" in args else which
        judge_links(lk, f"{which}_{o}"); raise SystemExit(0)
    USM.build_links = wrapped
    if which == "minarc": USM.MY_ARGV = args; USM.main()
    else:
        import user_style_geneva as G; G.MY_ARGV = args; G.main()
elif which == "roller":
    import math, numpy as np
    import user_style_roller as R
    M, rep0 = R.RL1.fit(); lg = R.RL1.law_geom(M); M._lg = lg; dg = R.RL1.drive_geom(M)
    l1d = json.load(open(os.path.join(REPO, "pipeline", "full-exo", "designs", "l1_roller-longdyad", "design.json")))
    stops = {}
    for key in ("K", "J2"):
        q_lo, q_hi, meta = lg[key]; homes = [math.radians(x) for x in l1d["stack_mm"]["stops"][key]["dowel_home_angles_deg"]]
        stops[key] = dict(q=(q_lo, q_hi), meta=meta, homes=homes, pair_placed_in_l1=bool(l1d["stack_mm"]["stops"][key].get("pair")))
    lug, _ = R.flank_lug(M, dg); lk, _ = R.build_links(M, stops, lug); judge_links(lk, "roller_user_roller_longdyad")
