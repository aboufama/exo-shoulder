"""Round 15 lens A (take-bound-3dof): the decisive take-bound table, built from files on disk.

Every number below is either READ from a cited JSON on disk (cite = [file, json path], checked here to +-0.005) or
quoted from a cited markdown line (cite = [file, "line N"], not machine-checked). Derived columns are arithmetic only:

    gap = 100 [(0.90 - ib14)+ + (0.95 - follow)+ + (0.90 - reach)+ + contact]          (tools/concept_bench.py gap_of)
    zero-contact floor(takes)      = 100 (0.90 - takes/360)          (ib14 >= 0.90, follow >= 0.95, contact 0)
    gap at the family's proximity  = floor(takes) + 100 [(0.90 - ib14)+ + (0.95 - follow)+ + contact]
    takes 95 needs at that proximity = ceil(360 [0.90 - (13.75 - 100 [(0.90 - ib14)+ + (0.95 - follow)+ + contact]) / 100])

No bench was run by this script (it reads files); fills run separately are cited to their own output files.

    python3 docs/research/take_bound_3dof.py          # writes docs/research/take_bound_3dof.json and prints the table
"""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
BAR = 13.75                                  # score 95


def rd(f, path):
    d = json.load(open(os.path.join(REPO, f)))
    for k in path.strip("/").split("/"):
        d = d[int(k)] if isinstance(d, list) else d[k]
    return d


def floor(t): return round(100 * (0.90 - t / 360), 2)


def prox(ib14, contact, follow=1.0):
    return 100 * (max(0.0, 0.90 - ib14) + max(0.0, 0.95 - follow) + contact)


def need(ib14, contact, follow=1.0):
    return math.ceil(360 * (0.90 - (BAR - prox(ib14, contact, follow)) / 100) - 1e-9)


def M(gap, takes, ib14=None, contact=None, follow=1.0, cite=None, note=""):
    return dict(gap=gap, takes=takes, ib14=ib14, contact=contact, follow=follow, cite=cite, note=note)


VB = "docs/concepts/verify/"
ROWS = [
    # ------------------------------------------------------------------------------------------------ back of the shoulder
    dict(family="back of the shoulder (J1 bvec ~97-102 / 62-65, the lead's seats)", realisation="plain O20 3R (no K)",
         kin=dict(takes=250, cite=["docs/concepts/ROUNDS.md", "line 2595"],
                  note="planner measurement (Bench(110,360) ws, th window at the 5-deg margin, no metal; bvec(97.3, 64.6), a1/a2 41.7/72.1); no script saved"),
         law=None,
         ghost=None, ghost_why="unmeasured: not needed - the kinematic bound (250 -> floor 20.56) already exceeds 13.75",
         metal=M(39.80, None, cite=["docs/FINDINGS.md", "line 3386 (Round J4 item 4)"],
                 note="welded plain 3R at the lead's seats, FAST Bench(60,160) only (23.65-31.83 with the psi2 J2 window shift); no frozen exact on file"),
         verified=None, verified_why="no verified row at this realisation",
         reach95=False, reason="kinematic: 250 takes < 275 even at zero contact and perfect in-band (floor 20.56)"),
    dict(family="back of the shoulder", realisation="knuckle (K coupled to J2 by a drive law; 3 active) - the lead's family",
         kin=dict(takes=272, cite=["docs/research/fold_ceiling.md", "line 175 (kin_ceiling.py)"],
                  note="the leader's own window [24.67, 106.6] at the K drive's 46-deg stroke: 272 = 261 taken + 9 knee + 2 contact; a2 shift to 60 holds 271"),
         law=dict(takes="267-272", cite=["docs/concepts/ROUNDS.md", "line 1583"],
                  note="law-only kinematics: linear law kK 1.96 closes 267, kK 2.3 closes 272; kK >= 2.7 kills the lobe at its base radius (PA <= 42)"),
         oracle=M(17.69, 277, 0.8862, 0.0325, cite=[VB + "seatoracle-erwall-knuckle-3r/cell_L0b.json", "/oracle/gap"],
                  note="free-K ORACLE (best K per pose, ANY law; kit metal) at the lead's seats with stop B 76 (K dyad 32/52, not buildable with bk1 26): 277 takes, 13 contacts. At the lead's own stroke 58.77: 20.52 (255 takes, 5 contacts; docs/concepts/seatoracle-erwall-knuckle-3r.md)"),
         ghost=M(16.91, 269, 0.8941, 0.0104, cite=["docs/concepts/rows/proximal-j3-geodesic-knuckle-3r.json", "/audit/at_knee_rule/gap"],
                 note="ideal drive (no drive metal), at the knee rule; ~40 ghost cells over rounds 12-13 read 269-271 (round-12 max 270); 16.52 / 271 only with the knee floor below the rule (margin leak)"),
         metal=M(18.28, 262, 0.9012, 0.0106, cite=[VB + "conecut-knee-knuckle-3r_v_bench_frozen.json", "/frozen/gap"]),
         verified=dict(id="conecut-knee-knuckle-3r", gap=18.28, held=22.38, ledger="watch", cx=18.5,
                       cite=[VB + "conecut-knee-knuckle-3r_v_held_frozen.json", "/frozen/gap"]),
         reach95=False,
         reason="ghosts cap at 269-271 (floor 14.72-15.28 > 13.75 even at zero contact); the free-K oracle reaches 277 only with a non-buildable 76-deg stroke and 13 contacts (9 newly closed ER poses 4.6-13.2 mm in the skin at the best K); the stretched-wall fold (73 poses, dK 52.6 of 57) is the drive's stroke"),
    dict(family="back / acromion boundary (the k33 seats, J1 az ~95)", realisation="knuckle, any K law (free-K oracle bound)",
         kin=None, kin_why="not separately recorded; the oracle's connected takes bound it from above for metal",
         law=None,
         oracle=M(17.25, 280, 0.8990, 0.0448, follow=0.9455, cite=["docs/concepts/freek-oracle-route-knuckle-4r.md", "line 85"],
                  note="per-pose oracle K over the legal self-motion, each sample a full frozen model run; ~21 contacts (ER binders 117/119/129 touch at every legal K). This bounds every 3-joint K law AND the sensed 4th-joint K at these seats"),
         ghost=None, ghost_why="the oracle is the ghost bound here",
         metal=None, metal_why="no 3-joint metal at these seats (the realised cell is the 4-joint freek-oracle-route-knuckle-4r)",
         verified=None, verified_why="none 3-joint",
         reach95=False, reason="even the per-pose oracle K reads 17.25 (21 contacts); J1 forward +15 / +25 along the acromion top reads 21.73 / 22.91 (seatoracle-erwall)"),
    # ------------------------------------------------------------------------------------------------ cap pole (acromion top)
    dict(family="cap pole (acromion top, J1 bvec(43.2, 59.9))", realisation="plain O20 3R",
         kin=dict(takes=281, cite=["docs/concepts/ROUNDS.md", "line 2596"],
                  note="planner measurement, a1/a2 50.2/60.3, J3 wdir(92, -9); best-placed window W 90 / 100 / 110 / 120 -> 0.803 / 0.844 / 0.878 / 0.911"),
         law=None,
         ghost=None, ghost_why="hub-2-free bound measured instead: hub 2 <= 0.12 in band over 668 cap configs (ROUNDS.md line 2600); its axis exits the skin 107-116 mm from GH",
         metal=M(56.40, 267, 0.502, 0.008, cite=["docs/concepts/acromion-relay-4r.md", "line 238"],
                 note="T-0 control (J0 locked = plain O20 3R), frozen exact; cap-nullspace's searched plain 3R control 60.61 frozen (rows/cap-nullspace-4r.json)"),
         verified=None, verified_why="no verified 3-joint row (controls only)",
         reach95=False, reason="in-band: hub 2 must sit on the J2 axis 107-116 mm from GH (ib14 0.50); the in-band term alone (39.8) is 3x the 95 budget"),
    dict(family="cap pole", realisation="knuckle (cap-plateau cells A/B/C)",
         kin=dict(takes=275, cite=["docs/FINDINGS.md", "line 3122-3125 (Round 14 item 1); box best 299 in docs/concepts/verify/cap-plateau-knuckle-3r_kinscan_C.json [0].ws"],
                  note="cell C 275 kinematic at the metal search's end; the kinematic box best is 299 (kinscan_C[0].ws), cell B 270; a metal search started at 299 walked back to 275"),
         law=None, law_why="ghost drive only (one-sided buildable law in the metal column)",
         ghost=M(32.08, 247, 0.8232, 0.0301, follow=0.9818, cite=[VB + "cap-plateau-knuckle-3r_frozen97_C2best.json", "/frozen/gap"],
                 note="ghost drive, kit metal; same-kit control at the lead's seats 30.59 / 259 takes (frozen97_ctrlbest.json)"),
         metal=M(33.94, 245, 0.7994, 0.0194, follow=0.9909, cite=[VB + "cap-plateau-knuckle-3r_frozen97_A3onesided.json", "/frozen/gap"],
                 note="buildable one-sided law, 200 tries; optimum 1 deg from a K6 collision cliff"),
         verified=dict(id="cap-plateau-knuckle-3r", gap=32.08, held=35.16, ledger="no entry (dead)", cx=17.5,
                       cite=["docs/concepts/rows/cap-plateau-knuckle-3r.json", "/held_self/frozen/gap"], note="verified as a DEAD gate-0 number (ghost drive)"),
         reach95=False, reason="metal keeps ~40 % of the kinematic surplus; at its measured in-band / contact 95 would need 313 takes, more than the kinematic 275"),
    dict(family="cap pole", realisation="virtual J2 (spherical four-bar / slaved elbow, no metal on the J2 axis)",
         kin=None, kin_why="not recorded per cell",
         law=None, ghost=None, ghost_why="fast-only screens",
         metal=M(86.95, None, cite=["docs/FINDINGS.md", "line 2929 (Round J2)"],
                 note="FAST Bench(60,160): open 90.11, crossed 86.95, slaved elbow 107.61-108.22 vs the plain cap 3R's 63.18 through the same kit"),
         verified=None, verified_why="dead at gate 0",
         reach95=False, reason="every virtual-J2 cell is 24-45 fast points worse than the plain cap 3R it was meant to fix"),
    # ------------------------------------------------------------------------------------------------ acromion top + deltoid crest
    dict(family="crest (J1 acromion top az 100 / el 62, J3 on the deltoid crest)", realisation="plain O20 3R, no knee",
         kin=dict(takes=291, cite=[VB + "deltoid-crest-j3-3r_audit3_kinscan.json", "kin360_max_hub2_inband"],
                  note="max over 6676 honest configs with hub 2 in band (0.8083); 336 (0.9333) with hub 2 anywhere; p95 with hub 2 in band 272 (0.7556)"),
         law=None,
         ghost=None, ghost_why="unmeasured (no knuckle at the crest); the kinematic scan is the bound",
         metal=M(34.98, 218, 0.8971, 0.0389, follow=0.9364, cite=[VB + "deltoid-crest-j3-3r_audit_frozen_s12_ee8.json", "/wear/gap"]),
         verified=dict(id="deltoid-crest-j3-3r", gap=34.98, held=39.27, ledger="watch", cx=0,
                       cite=["docs/FINDINGS.md", "line 3480 (re-dispatch item 7)"], note="claim 47.86 verified, later best 40.17, audit re-wear 34.98 upheld; dead"),
         reach95=False, reason="fold-free poses and clearance trade ~1:1 inside the crest basin (closure <= 0.81 with hub 2 in band); overhead skin at elev 150 is 6.9 mm from the chain"),
    dict(family="crest", realisation="pin knee (cx 0; flat and joggled knee)",
         kin=None, kin_why="the knee does not change th: same bound as the crest 3R row (<= 291 with hub 2 in band)",
         law=None,
         ghost=None, ghost_why="unmeasured; a joggle was bounded at ~25-27 frozen before it was built (FINDINGS line 3133)",
         metal=M(31.50, 226, 0.8719, 0.0147, cite=[VB + "crest-knee-3r-joggle_v_bench_frozen.json", "/model/gap"],
                 note="joggled knee; flat cell 32.84 / 228 (crest-knee-3r_v_bench_frozen.json /model)"),
         verified=dict(id="crest-knee-3r", gap=31.50, held=28.45, ledger="watch", cx=0,
                       cite=[VB + "crest-knee-3r-joggle_v_held_frozen.json", "/model/gap"], note="WATCH: NEW-tolcliff (+0.2 mm strap error -> 39.90)"),
         reach95=False, reason="J3-window stops replace the fold losses (fold 48 -> 16-24 of 220, stops 5 -> 17); total losses 48-55 of 220"),
    dict(family="crest", realisation="knuckle with an ideal K law",
         kin=None, kin_why="unmeasured: the known hole of the 03:15 plan; no model combines the crest J3 seat with a knuckle (a new model, > 15 min)",
         law=None, ghost=None, ghost_why="unmeasured (same reason). Nearest measured: proximal-j3 moved J3 up the lateral deltoid at the back seat - 269-271 for every seat",
         metal=None, metal_why="unmeasured", verified=None, verified_why="none",
         reach95=None, reason="unmeasured; the proximal-j3 J3-seat sweep (269-271 takes) is the nearest evidence and says no"),
    # ------------------------------------------------------------------------------------------------ H1 seats (acromion top)
    dict(family="H1 seats (J1 acromion top, anterior 0.05-0.09)", realisation="pin knee (cx 0) - H1 skin-normal-3r-pin-knee",
         kin=None, kin_why="fill pending (section 2 note)",
         law=None,
         ghost=None, ghost_why="GPU knee polish 20.26 bench was REFUTED held out (27.65 vs H1 28.55): not a ghost bound",
         metal=M(27.20, 237, 0.8953, 0.0256, follow=0.9636, cite=["docs/concepts/rows/skin-normal-3r-pin-knee.json", "v_gap"]),
         verified=dict(id="skin-normal-3r-pin-knee", gap=27.20, held=28.55, ledger="watch", cx=0,
                       cite=["docs/concepts/rows/skin-normal-3r-pin-knee.json", "v_polish2_h1_held_gap"],
                       note="fitted without the pin-a stack rule (ROUNDS.md re-dispatch: a hidden constraint of every pin-knee model)"),
         reach95=False, reason="237 metal takes; 95 at its proximity needs 299"),
    dict(family="antcrest (J1 acromion top, J3 anterior crest)", realisation="pin knee with H1's knee",
         kin=None, kin_why="not recorded",
         law=None, ghost=None, ghost_why="hub-2 need 50-400 mm over the skin (ROUNDS.md line 3768)",
         metal=M(61.12, 212, 0.7209, 0.0346, follow=0.8636, cite=[VB + "../rows/crest-knee-3r.json", "/antcrest_2026_10_18/frozen_exact_bench/gap"]),
         verified=None, verified_why="dead at screen",
         reach95=False, reason="hub 2 cannot sit in band"),
]

REF4 = [  # 4-joint reference rows: NOT 3-DOF, for comparison only
    dict(id="lead-relay-j0-4r", what="ghost J0 (zero-size) under the frozen lead vs the real O20 hub 0 + link 0",
         ghost=dict(takes=275, gap=16.22), real=dict(gap=22.18, takes=273, contacts=8, ib14=0.8404), cx=50.75, verified=True,
         cite=["docs/concepts/rows/lead-relay-j0-4r.json", "v_gap"], note="hub 0 + link 0 0-2 % in band at all 108 legal seats; ghost overstates by 6-9 points"),
    dict(id="freek-oracle-route-knuckle-4r (cell A, oracle)", what="free-K oracle at the k33 seats (bounds every K law and a sensed K)",
         real=dict(gap=17.25, takes=280, contacts=21), cite=["docs/concepts/freek-oracle-route-knuckle-4r.md", "line 85"], verified=True,
         note="instrument, kit metal; 21.46 near-touch"),
    dict(id="kfree-armarc ideal relay (no hardware)", what="K-free ideal 75-deg cuff relay on a plain O20 3R at the lead's seats",
         real=dict(gap=10.22, takes=304, contacts=15), cite=["docs/research/fold_ceiling/kfree_armarc_ideal_frozen_exact.json", "/wear/gap"],
         note="NO hardware: real arm-fixed tracks are capped ~45 deg by the torso; the long axis floats 49-68 mm out; real kfree-armarc-relay-4r 26.42"),
    dict(id="freek-oracle-route-knuckle-4r (cell B)", what="sensed K + J3 dowel, 4 joints",
         real=dict(gap=16.20, held=21.89, contacts=15, depth_mm=78.55), polished=dict(gap=15.40, held=20.50, held_envfit=20.24),
         cx=33.25, verified=True, ledger="watch", cite=["docs/concepts/rows/freek-oracle-route-knuckle-4r.json", "v_gap"],
         note="polish pick1 CONFIRMED by its verifier (held gain on the env-fit protocol); does not replace the verified fields"),
    dict(id="proxtrack-relay-knuckle-4r", what="relay on a proximal track, 4 joints",
         real=dict(gap=14.02, gate=14.40, held=18.01), cx=52.5, verified=False, ledger="no entry",
         cite=["docs/concepts/rows/proxtrack-relay-knuckle-4r.json", "gap/verdict"],
         note="SCREENED, UNVERIFIED: an independent verification is running in parallel (pending; not waited for)"),
    dict(id="armarc-relay-knuckle-4r", what="cuff arm-arc spring relay on the frozen lead",
         real=dict(gap=18.01, takes=275, contacts=11), cx=52.0, verified=True, cite=["docs/concepts/rows/armarc-relay-knuckle-4r.json", "v_gap"],
         note="dead (> 17.5); relays folded-side poses into the skin to -9.79 mm"),
]

LEAD = dict(id="conecut-knee-knuckle-3r", gap=18.28, held=22.38, takes=262, contacts=4, depth_mm=20.24, cx=18.5)


def check(cite, want):
    f, p = cite
    if not f.endswith(".json") or not p.startswith("/") and "/" in p and not p.startswith("v_") and not p.startswith("kin"):
        return None
    try:
        got = rd(f, p) if p.startswith("/") else rd(f, p.split("/")[0])
    except Exception as e:  # noqa: BLE001
        return f"unreadable: {e}"
    if isinstance(got, (int, float)) and isinstance(want, (int, float)):
        scale = 360 if (0 < got <= 1 and want > 1) else 1
        return "ok" if abs(got * scale - want) <= 0.5 * (scale > 1) + 0.005 else f"MISMATCH file {got} vs table {want}"
    return None


def main():
    out = dict(t="2026-10-18", bar_gap=BAR, lead=LEAD, rows=[], ref4=REF4,
               arithmetic=dict(take_worth=round(100 / 360, 3), zero_contact_95_takes=math.ceil(360 * (0.90 - BAR / 100)),
                               lead_contact_95_takes=need(0.9012, 0.0106), zero_contact_at_262=floor(262), floor_271=floor(271)))
    for r in ROWS:
        r = dict(r)
        chk = {}
        for k in ("kin", "metal", "ghost", "oracle"):
            v = r.get(k)
            if isinstance(v, dict) and v.get("cite") and str(v["cite"][0]).endswith(".json"):
                want = v.get("takes") if k == "kin" else v.get("gap")
                chk[k] = check(v["cite"], want)
        if r.get("verified") and r["verified"].get("cite"):
            chk["verified_held"] = check(r["verified"]["cite"], r["verified"]["held"])
        r["checks"] = chk
        best = None
        for k in ("metal", "ghost", "oracle"):
            v = r.get(k)
            if isinstance(v, dict) and v.get("takes"):
                v["floor_zero_contact"] = floor(v["takes"])
                if v.get("ib14") is not None and v.get("contact") is not None:
                    fol = v.get("follow") if v.get("follow") is not None else 1.0
                    v["gap_rebuilt"] = round(floor(v["takes"]) + prox(v["ib14"], v["contact"], fol), 2)
                    v["takes_for_95_at_this_proximity"] = need(v["ib14"], v["contact"], fol)
                    if k == "metal": best = v
        if isinstance(r.get("kin"), dict) and isinstance(r["kin"].get("takes"), int):
            r["kin"]["floor_zero_contact"] = floor(r["kin"]["takes"])
            if best: r["kin"]["gap_at_metal_proximity"] = round(floor(r["kin"]["takes"]) + prox(best["ib14"], best["contact"], best.get("follow") or 1.0), 2)
        out["rows"].append(r)
    json.dump(out, open(os.path.join(HERE, "take_bound_3dof.json"), "w"), indent=1)
    for r in out["rows"]:
        print(r["family"][:40], "|", r["realisation"][:40], "|", json.dumps(r["checks"]))
        for k in ("kin", "oracle", "ghost", "metal"):
            v = r.get(k)
            if isinstance(v, dict): print("    ", k, {x: v.get(x) for x in ("takes", "gap", "floor_zero_contact", "gap_rebuilt", "takes_for_95_at_this_proximity", "gap_at_metal_proximity") if v.get(x) is not None})
    print(json.dumps(out["arithmetic"]))


if __name__ == "__main__":
    main()
