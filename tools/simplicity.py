"""Complexity count per design (the user's "simplicity number"): LOWER = SIMPLER, 0 = the simplest buildable 3-DOF exo.

User, 2026-10-16: "it would be cool to have a simplicity score for each design impacted by degrees of freedom moving
parts, etc. ... for now shouldn't impact overall score but should show in the chart", then "when score start capping
out around 95+ over the night, prioritize lowering that simplicity number". So this is a points count that only goes
up as a design gets more complicated, and it never enters the bench score / gap.

0 points = the anchor: three revolute hubs (pins on bearing pairs), three moving links, no passive freedom, nothing
sensed but the three hubs, no loop beyond the one every exo closes through the wearer's shoulder - the champion
spherical 3R (rows/baseline-3r.json: 7 made parts = base adapter, 2 straps, arm-end neck, 3 hub shafts; 6 bought =
3 MR117 pairs; fasteners and sensing parts left out). Every item a design has beyond that ADDS explicit points (no cap). Method, weights and the worked examples: docs/SIMPLICITY.md
(Grubler-Kutzbach mobility, Boothroyd-Dewhurst part count, Pahl & Beitz simplicity / clarity, CLAUDE.md's
manufacturable-joint rule).

Input: the "mechanism" record of each design, in docs/concepts/rows/<id>.json:
  {active_dof, passive_trans, crossed_rails, passive_rot, moving_bodies, joints, closed_loops, sliding_pairs,
   rolling_pairs, sensed_passive, springs_or_flexures, custom_parts, catalogue_parts, notes, source, confidence}

    python3 tools/simplicity.py              # table of every rows/*.json mechanism record, simplest first
    python3 tools/simplicity.py --json       # {id: {complexity, items, kutzbach_M, redundant, flags, ...}} (dashboard)
    python3 tools/simplicity.py --examples   # the worked examples of docs/SIMPLICITY.md, item by item
    python3 tools/simplicity.py --check      # self-test (anchor = 0, worked examples, topology checks)
    python3 tools/simplicity.py --score '<json mechanism record>'
"""
import glob, json, os, sys

VERSION = "2.1 (2026-10-17)"          # bump when a weight or a rule changes; the dashboard shows it
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ROWS = os.path.join(REPO, "docs", "concepts", "rows")

# Weights (points). Why each one: docs/SIMPLICITY.md section 2.
W = dict(
    active_extra=25,       # each active DOF beyond 3 (motor + cable + encoder in MVP2, a spare freedom in MVP1)
    ptrans=2,              # each passive translation (a guide: rail + block + stops). User 2026-10-16: "slider should count pretty low" (was 5)
    crossed=5,             # two translations stacked on each other (adapter, 10.5-11.5 mm stack, squareness)
    ptrans_over_cap=20,    # each passive translation beyond 2: no compact component exists (CLAUDE.md: never)
    prot=1,                # each passive rotation (a pin on a bearing pair). User 2026-10-16: "extra rotation degrees is not huge for me" (was 2)
    sensed=5,              # each passive coordinate that must be measured (an encoder without a motor)
    loop=4,                # each closed loop inside the mechanism (beyond the one through the wearer's GH)
    body_extra=1,          # each moving rigid body beyond 3
    joint_extra=1,         # each kinematic pair beyond 3
    sliding=1,             # each track pair (rail, carriage, arc track, sleeve on a rod, slot) vs a sealed bearing (was 2; a slider counts low)
    spring=3,              # each spring or flexure (fatigue, centring force, hysteresis)
    custom_extra=0.5,      # each made part beyond the anchor's 7 (a drawing, a set-up, a tolerance chain)
    catalogue_extra=0.25,  # each bought part beyond the anchor's 6 (handling + insertion, Boothroyd-Dewhurst)
)
ANCHOR = dict(active_dof=3, moving_bodies=3, joints=3, custom_parts=7, catalogue_parts=6)   # = rows/baseline-3r.json
PTRANS_CAP = 2                       # CLAUDE.md "Manufacturable joints only": 2 passive translations is the hard maximum
FIELDS = ("active_dof", "passive_trans", "crossed_rails", "passive_rot", "moving_bodies", "joints", "closed_loops",
          "sliding_pairs", "rolling_pairs", "sensed_passive", "springs_or_flexures", "custom_parts", "catalogue_parts")


def _n(m, k, default=0):
    v = m.get(k, default)
    if v is None: return default
    if isinstance(v, bool): return int(v)
    try: return float(v) if isinstance(v, float) and v != int(v) else int(v)
    except (TypeError, ValueError): return default


def recipe_parts(m):
    """Part counts by the standard recipe (docs/SIMPLICITY.md section 3), used when a record leaves them out.
    Made: the base + one per moving body + 1 shaft / pin per revolute + 1 per track pair (adapter or end stop).
    Bought: 2 per revolute (the bearing pair), 2 per track pair (rail + block), 1 per other pair (rod end, ball stud,
    miniature U-joint). Fasteners and sensing parts are left out. The anchor gives 7 made + 6 bought, the census count
    of the champion (rows/baseline-3r.json)."""
    B, J = _n(m, "moving_bodies", 3), _n(m, "joints", 3)
    rol, sl = _n(m, "rolling_pairs", 0), _n(m, "sliding_pairs", 0)
    other = max(0, J - rol - sl)
    return 1 + B + rol + sl, 2 * rol + 2 * sl + other


def score(mech):
    """mechanism record -> {complexity, items: [(item, points)], kutzbach_M, redundant, flags, version}.
    complexity = sum of the item points (lower = simpler, 0 = the anchor). Nothing here touches the bench gap."""
    m = dict(mech or {})
    # user 2026-10-17: "if no encoders are needed, it doesn't count as added complexity" - an UNSENSED two-pin cuff knee
    # (pins a, b; the arm's pose is read from the hub encoders) is cuff alignment like the cuff slides: its own items
    # (record "cuff_knee": passive_rot, moving_bodies, joints, custom_parts, catalogue_parts) are taken out before scoring
    ck = m.get("cuff_knee") if isinstance(m.get("cuff_knee"), dict) and not m["cuff_knee"].get("sensed") else None
    full = dict(m)
    if ck:
        for k in ("passive_rot", "moving_bodies", "joints", "custom_parts", "catalogue_parts", "closed_loops"):
            if m.get(k) is not None: m[k] = max(0, _n(m, k) - _n(ck, k))
    A, P, R = _n(m, "active_dof", 3), _n(m, "passive_trans"), _n(m, "passive_rot")
    X = bool(m.get("crossed_rails")) and P >= 2
    B, J, L = _n(m, "moving_bodies", 3), _n(m, "joints", 3), _n(m, "closed_loops")
    SL, SE, SP = _n(m, "sliding_pairs"), _n(m, "sensed_passive"), _n(m, "springs_or_flexures")
    est = m.get("custom_parts") is None or m.get("catalogue_parts") is None
    rc, rk = recipe_parts(m)
    C = rc if m.get("custom_parts") is None else _n(m, "custom_parts")
    K = rk if m.get("catalogue_parts") is None else _n(m, "catalogue_parts")
    items, flags = [], []

    def add(label, pts):
        if pts: items.append((label, round(float(pts), 2)))

    a_x = max(0, A - ANCHOR["active_dof"])
    add(f"{a_x} active DOF beyond 3 x {W['active_extra']}", a_x * W["active_extra"])
    add(f"{P} passive translation{'s' if P != 1 else ''} x {W['ptrans']}", P * W["ptrans"])
    if X: add(f"crossed rails (2 translations stacked) +{W['crossed']}", W["crossed"])
    over = max(0, P - PTRANS_CAP)
    if over:
        add(f"{over} passive translation{'s' if over != 1 else ''} beyond the cap of 2 x {W['ptrans_over_cap']}",
            over * W["ptrans_over_cap"])
        flags.append(f"NOT BUILDABLE: {P} passive translations (CLAUDE.md: 2 is the hard maximum, 3 never)")
    add(f"{R} passive rotation{'s' if R != 1 else ''} x {W['prot']}", R * W["prot"])
    add(f"{SE} sensed passive coordinate{'s' if SE != 1 else ''} x {W['sensed']}", SE * W["sensed"])
    add(f"{L} closed loop{'s' if L != 1 else ''} in the mechanism x {W['loop']}", L * W["loop"])
    b_x, j_x = max(0, B - ANCHOR["moving_bodies"]), max(0, J - ANCHOR["joints"])
    add(f"{b_x} moving bod{'ies' if b_x != 1 else 'y'} beyond 3 x {W['body_extra']}", b_x * W["body_extra"])
    add(f"{j_x} joint{'s' if j_x != 1 else ''} beyond 3 x {W['joint_extra']}", j_x * W["joint_extra"])
    add(f"{SL} track (sliding) pair{'s' if SL != 1 else ''} x {W['sliding']}", SL * W["sliding"])
    add(f"{SP} spring{'s' if SP != 1 else ''} / flexure{'s' if SP != 1 else ''} x {W['spring']}", SP * W["spring"])
    c_x, k_x = max(0, C - ANCHOR["custom_parts"]), max(0, K - ANCHOR["catalogue_parts"])
    tag = " (recipe)" if est else ""
    add(f"{c_x} made parts beyond 7 x {W['custom_extra']}{tag}", c_x * W["custom_extra"])
    add(f"{k_x} bought parts beyond 6 x {W['catalogue_extra']}{tag}", k_x * W["catalogue_extra"])
    if ck: items.append(("unsensed two-pin cuff knee: 0 (user 2026-10-17, cuff alignment like the cuff slides)", 0.0))
    # Kutzbach and the topology checks below read the FULL mechanism (the knee is still there, it just costs nothing)
    R, B, J, L = _n(full, "passive_rot"), _n(full, "moving_bodies", 3), _n(full, "joints", 3), _n(full, "closed_loops")

    # Grubler-Kutzbach (spatial) for the whole loop set, the wearer's GH taken as a ball joint (3 freedoms) and the
    # arm-side end fixed to the cuff: L_total = closed_loops + 1, M = sum f - 6 L_total. The arm has 3 DOF, so
    # M < 3 means 3 - M redundant constraints (taken by axis concurrency, the cuff liner or the user's cuff slides on a
    # body), M > 3 an undetermined spare freedom (R17: it sags unless a spring or a loop sets it). Reported, not scored.
    M = A + P + R + 3 - 6 * (L + 1)
    redundant = max(0, 3 - M)
    if M > 3 and not SP:
        flags.append(f"Kutzbach M = {M} > 3: {M - 3} spare freedom(s) not set by closure (R17) - check the record")
    if B and J and L != J - B:
        flags.append(f"topology: closed_loops {L} != joints {J} - moving_bodies {B} (count the arm-side end as one body, "
                     f"a U-joint as one joint without its cross or as two joints with it)")
    if bool(m.get("crossed_rails")) and P < 2: flags.append("crossed_rails set with fewer than 2 passive translations")
    if SL + _n(m, "rolling_pairs") > J: flags.append("sliding_pairs + rolling_pairs > joints")
    if A < 3: flags.append(f"active_dof {A} < 3: not a 3-DOF shoulder chain")
    total = round(sum(p for _, p in items), 2)
    return dict(complexity=total, items=items, kutzbach_M=M, redundant=redundant, flags=flags,
                parts=dict(custom=C, catalogue=K, estimated=est), version=VERSION)


# The worked examples of docs/SIMPLICITY.md. A design's census record (rows/<id>.json "mechanism") wins over the entry
# here in --examples; the entries keyed by a design id are this doc's own count, kept for the designs the census has
# not reached. --check holds the doc's numbers to these.
EXAMPLES = {
    "anchor (three pins on bearing pairs, three links)": dict(
        active_dof=3, passive_trans=0, crossed_rails=False, passive_rot=0, moving_bodies=3, joints=3, closed_loops=0,
        sliding_pairs=0, rolling_pairs=3, sensed_passive=0, springs_or_flexures=0, custom_parts=7, catalogue_parts=6),
    "skin-normal-3r-pin-knee": dict(
        active_dof=3, passive_trans=0, crossed_rails=False, passive_rot=2, moving_bodies=5, joints=5, closed_loops=0,
        sliding_pairs=0, rolling_pairs=5, sensed_passive=2, springs_or_flexures=0, custom_parts=11, catalogue_parts=12,
        notes="bodies: link 1, link 2, member 3 (hub-3 lower plate + E strap), knee link, arm pad (arm-end, on BOTTOM). "
              "joints: J1-J3 O20 hubs, pins a, b parallel to J3 (iglidur GSM sleeve + 2 GTM washers on a Ti pin). "
              "sensed: both pins - the arm's twist = q3 + qa + qb, exact under GH translation only if all three are read "
              "(manufacturability_summary.md section 3, option 2). made: base, 2 straps, member 3, knee link, pad, "
              "3 hub shafts, 2 pins; bought: 3 MR117 pairs + 2 x (sleeve + 2 washers).",
        source="docs/concepts/models/skin-normal-3r-pin-knee.py:1-21", confidence="counted"),
    "closure-set-arc-knee-3r": dict(
        active_dof=3, passive_trans=0, crossed_rails=False, passive_rot=3, moving_bodies=6, joints=6, closed_loops=0,
        sliding_pairs=0, rolling_pairs=6, sensed_passive=3, springs_or_flexures=0, custom_parts=14, catalogue_parts=16,
        notes="bodies: link 1, link 2 + fork, yoke (hub-3 housing), J3 rotor + E arm, cuff link, arm pad (arm-end). "
              "joints: J1, J2, J3 O20 hubs, K trunnion pair (one axis, one joint), pins a, b. sensed: psi (it tilts J3's "
              "axis, so it enters the arm's orientation; set by the radial closure at 2-5 deg per mm of GH translation) "
              "+ both pins (twist). made: base, link 1, link 2 + fork, yoke, E arm, cuff link, pad, 3 hub shafts, "
              "2 trunnion pins, 2 knee pins; bought: 3 MR117 pairs, 2 MR63ZZ pairs, 2 x (sleeve + 2 washers).",
        source="docs/concepts/models/closure-set-arc-knee-3r.py:1-25", confidence="counted"),
    "4R (the anchor + a 4th active hub and link)": dict(
        active_dof=4, passive_trans=0, crossed_rails=False, passive_rot=0, moving_bodies=4, joints=4, closed_loops=0,
        sliding_pairs=0, rolling_pairs=4, sensed_passive=0, springs_or_flexures=0, custom_parts=9, catalogue_parts=8),
    "3P cuff stage (seed-offset-3r-slides, not buildable)": dict(
        active_dof=3, passive_trans=3, crossed_rails=True, passive_rot=0, moving_bodies=6, joints=6, closed_loops=0,
        sliding_pairs=3, rolling_pairs=3, sensed_passive=0, springs_or_flexures=0, custom_parts=None, catalogue_parts=None),
    "spherical parallel 3-RRR (seed-spm-3rrr)": dict(
        active_dof=3, passive_trans=0, crossed_rails=False, passive_rot=6, moving_bodies=7, joints=9, closed_loops=2,
        sliding_pairs=0, rolling_pairs=9, sensed_passive=0, springs_or_flexures=0, custom_parts=None, catalogue_parts=None),
}
WORKED = ("baseline-3r", "offset-skin-normal-3r", "skin-normal-3r-pin-knee", "closure-set-arc-knee-3r")


def rows_dir_records(rows_dir=ROWS):
    """[(id, row, mechanism or None)] for every rows/*.json, sorted by id."""
    out = []
    for p in sorted(glob.glob(os.path.join(rows_dir, "*.json"))):
        try:
            with open(p) as f: r = json.load(f)
        except Exception as e:
            print(f"WARNING {os.path.relpath(p, REPO)}: {e}", file=sys.stderr); continue
        if not isinstance(r, dict): continue
        mid = r.get("id") or os.path.splitext(os.path.basename(p))[0]
        mech = r.get("mechanism") if isinstance(r.get("mechanism"), dict) else None
        out.append((mid, r, mech))
    return out


def table(rows_dir=ROWS):
    """{id: score(mechanism) + confidence, source, gap} for every row that carries a mechanism record."""
    T = {}
    for mid, r, mech in rows_dir_records(rows_dir):
        if mech is None: continue
        s = score(mech)
        s.update(confidence=mech.get("confidence"), source=mech.get("source"),
                 passive_trans=_n(mech, "passive_trans"), active_dof=_n(mech, "active_dof", 3),
                 gap=r.get("v_gap") if r.get("v_gap") is not None else r.get("gap"),
                 gap_verified=r.get("v_gap") is not None)
        T[mid] = s
    return T


def _fmt(v):
    return ("%g" % v) if isinstance(v, (int, float)) else str(v)


def print_table(rows_dir=ROWS):
    recs = rows_dir_records(rows_dir)
    have = [(mid, r, m) for mid, r, m in recs if m is not None]
    hdr = ("id", "cx", "act", "P", "X", "R", "sens", "loop", "B", "J", "trk", "spr", "made", "buy", "M", "gap", "conf")
    lines = []
    for mid, r, m in have:
        s = score(m)
        g = r.get("v_gap") if r.get("v_gap") is not None else r.get("gap")
        gs = "-" if g is None else (("v" if r.get("v_gap") is not None else "") + "%.2f" % float(g))
        lines.append((s["complexity"], mid, [mid, _fmt(s["complexity"]), _fmt(_n(m, "active_dof", 3)), _fmt(_n(m, "passive_trans")),
                      "x" if m.get("crossed_rails") else "", _fmt(_n(m, "passive_rot")), _fmt(_n(m, "sensed_passive")),
                      _fmt(_n(m, "closed_loops")), _fmt(_n(m, "moving_bodies", 3)), _fmt(_n(m, "joints", 3)),
                      _fmt(_n(m, "sliding_pairs")), _fmt(_n(m, "springs_or_flexures")),
                      _fmt(s["parts"]["custom"]) + ("*" if s["parts"]["estimated"] else ""), _fmt(s["parts"]["catalogue"]),
                      _fmt(s["kutzbach_M"]), gs, str(m.get("confidence") or "")], s["flags"]))
    lines.sort(key=lambda x: (x[0], x[1]))
    rows = [list(hdr)] + [x[2] for x in lines]
    wid = [max(len(r[i]) for r in rows) for i in range(len(hdr))]
    print(f"complexity (lower = simpler, 0 = three pins on bearing pairs + three links), tools/simplicity.py v{VERSION}")
    for i, r in enumerate(rows):
        print("  ".join(c.ljust(wid[j]) if j == 0 else c.rjust(wid[j]) for j, c in enumerate(r)))
        if i == 0: print("  ".join("-" * w for w in wid))
    for c, mid, _, fl in lines:
        for f in fl: print(f"  ! {mid}: {f}")
    missing = [mid for mid, r, m in recs if m is None]
    print(f"\n{len(have)} of {len(recs)} rows carry a mechanism record" + (f"; missing: {', '.join(missing)}" if missing else ""))
    print("cx = complexity; P passive translations (X crossed), R passive rotations, sens sensed passive coordinates,"
          " loop closed loops, B moving bodies, J joints, trk track pairs, spr springs/flexures, made*/buy parts"
          " (* = recipe estimate), M = Grubler-Kutzbach mobility incl. the wearer's GH (3 = exact, < 3 redundant)")


def print_examples():
    ex = {k: (v, "this doc's count") for k, v in EXAMPLES.items()}
    for mid, r, m in rows_dir_records():
        if m is not None and (mid in WORKED or mid in ex): ex[mid] = (m, "census record rows/%s.json" % mid)
    order = ["anchor (three pins on bearing pairs, three links)"] + list(WORKED) + [k for k in ex if k not in WORKED and not k.startswith("anchor")]
    for name in order:
        if name not in ex: continue
        m, src = ex[name]
        s = score(m)
        print(f"{name}: complexity {_fmt(s['complexity'])}  (Kutzbach M {s['kutzbach_M']}, redundant {s['redundant']}; {src})")
        for it, p in s["items"]: print(f"    {_fmt(p):>6}  {it}")
        for f in s["flags"]: print(f"    ! {f}")


def self_check():
    ok = True
    def expect(name, got, want):
        nonlocal ok
        if abs(got - want) > 1e-9: ok = False; print(f"FAIL {name}: {got} != {want}")
        else: print(f"ok   {name}: {_fmt(got)}")
    s = score(EXAMPLES["anchor (three pins on bearing pairs, three links)"])
    expect("anchor complexity", s["complexity"], 0); expect("anchor Kutzbach M (spherical: 3 redundant)", s["kutzbach_M"], 0)
    expect("anchor recipe parts = 7 made", recipe_parts(EXAMPLES["anchor (three pins on bearing pairs, three links)"])[0], 7)
    expect("anchor recipe parts = 6 bought", recipe_parts(EXAMPLES["anchor (three pins on bearing pairs, three links)"])[1], 6)
    expect("4R", score(EXAMPLES["4R (the anchor + a 4th active hub and link)"])["complexity"], 25 + 1 + 1 + 1 + 0.5)
    expect("pin knee (doc count)", score(EXAMPLES["skin-normal-3r-pin-knee"])["complexity"], 19.5)
    expect("closure-set knee (doc count)", score(EXAMPLES["closure-set-arc-knee-3r"])["complexity"], 30)
    base = {mid: m for mid, r, m in rows_dir_records() if m is not None}.get("baseline-3r")
    if base is not None: expect("rows/baseline-3r.json (the census anchor)", score(base)["complexity"], 0)
    s3 = score(EXAMPLES["3P cuff stage (seed-offset-3r-slides, not buildable)"])
    ok &= any("NOT BUILDABLE" in f for f in s3["flags"]); print(("ok  " if s3["flags"] else "FAIL") + " 3P flagged NOT BUILDABLE")
    for mid, r, m in rows_dir_records():
        if m is None: continue
        s = score(m)
        if s["complexity"] < 0: ok = False; print(f"FAIL {mid}: negative complexity")
    print("self-check", "passed" if ok else "FAILED")
    return ok


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--json" in a: print(json.dumps(table(), indent=1))
    elif "--examples" in a: print_examples()
    elif "--check" in a: sys.exit(0 if self_check() else 1)
    elif "--score" in a: print(json.dumps(score(json.loads(a[a.index("--score") + 1])), indent=1))
    else: print_table()
