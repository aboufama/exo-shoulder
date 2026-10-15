"""Fair CAD build of a band design (new pipeline): members as G2 sheets, v3.1 flush joint stacks, arm end merged into BOTTOM.

    python3 fair_build.py <key: 4c_best | 5r_thin> [stage: members | all]
"""
import json, math, os, sys, time, pickle
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); CONF = os.path.join(HERE, ".."); EXO = os.path.join(CONF, "..")
sys.path.insert(0, HERE)
import members as MB, envelope as EV
KEY = sys.argv[1]; STAGE = sys.argv[2] if len(sys.argv) > 2 else "all"
CAD_DIR = os.path.join(EXO, "full-exo", "designs", f"cad_{KEY}")                    # clips with the scapula-fixed base frame
R = json.load(open(os.path.join(CONF, "band_cad", "inputs", f"{KEY}.json")))["results"][0]
OUT = os.path.join(HERE, f"out_{KEY}"); os.makedirs(OUT, exist_ok=True)
# build with the geometry the evaluator scored (job keys copied into the input: t_link, ramp_deg, hw); r13 inputs carry
# t_link 5.5 = the old constant and no ramp_deg, so their builds do not change. Env RAMP_DEG / RAMP_TOP still override.
if "t_link" in R: MB.T_LINK = float(R["t_link"])
if "hw" in R: MB.HW = float(R["hw"])
if "ramp_deg" in R:
    if "RAMP_DEG" not in os.environ: MB.RAMP_DEG = float(R["ramp_deg"])                  # band floor cap out of every hub plane
    if "RAMP_TOP" not in os.environ: MB.RAMP_TOP = float(R["ramp_deg"])                  # ramp out of a hub plane before a joint is raised
N = R["n"]; A = [x * math.pi / 180 for x in R["a"]]; ZJ4 = float(R["zj4"])
FACES = {int(k): v for k, v in R["faces"].items() if k.isdigit()}; LOWER = {int(k): v for k, v in R["lower"].items()}
if os.environ.get("SWAP_J1") == "1" and LOWER[1] != 0:                              # base under link 1 at J1 (skin side), same stack height
    LOWER[1] = 0; R["lower"]["1"] = 0
BASE_TOP_MOUNT = (LOWER[1] != 0)                                              # base outer at J1
STANDOFF_MM = float(os.environ.get("STANDOFF_MM", 25.0))                              # hub plane this far over its skin need: flagged (a stand-off design)
MOUNT_LEN = 6.0                                                                     # base arm beyond the hub, toward the back plate
def log(*a): print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)

def hub_axis(mi, end):
    if mi == 0: return np.array([1.0, 0, 0])
    th = A[mi - 1]; return np.array([1.0, 0, 0]) if end == 0 else np.array([math.cos(th), math.sin(th), 0.0])
def joint_lv(J): return MB.stack_levels(ZJ4, MB.T_BOT) if J == N else MB.stack_levels(FACES[J])
def role(mi, J): return "upper" if J == N else ("lower" if LOWER[J] == mi else "upper")

def make_members():
    mem = {}
    lv1 = joint_lv(1)
    bt = math.radians(float(os.environ.get("TAB_BETA", 0.0))); sd = math.cos(bt) * np.array([0, -1.0, 0]) + math.sin(bt) * np.cross([1.0, 0, 0], [0, -1.0, 0])
    mem["base"] = MB.Member("D4-01 scapula base", "base", [dict(axis=hub_axis(0, 1), role=role(0, 1), lv=lv1, joint=1)],
                            strip_dir=sd, strip_len=MOUNT_LEN, R0=lv1["S"], flat=True)
    if BASE_TOP_MOUNT:                                                                  # 4c: base is the outer member at J1 -> anchored from above
        mem["base"] = MB.Member("D4-01 scapula base", "base", [dict(axis=hub_axis(0, 1), role=role(0, 1), lv=lv1, joint=1)],
                                strip_dir=sd, strip_len=0.0, R0=lv1["S"], flat=True); mem["base"].disc_r = 14.0   # O28: the 3 M2 back-plate holes need a wall outside the O22 cap
    for mi in range(1, N):
        hubs = [dict(axis=hub_axis(mi, 0), role=role(mi, mi), lv=joint_lv(mi), joint=mi), dict(axis=hub_axis(mi, 1), role=role(mi, mi + 1), lv=joint_lv(mi + 1), joint=mi + 1)]
        mem[f"l{mi}"] = MB.Member(f"D4-{mi + 1:02d} link {mi}", f"l{mi}", hubs, theta=A[mi - 1])
    if BASE_TOP_MOUNT:                                                                  # link 1 stays flat under the base disc's overhang
        for h in mem["l1"].hubs:
            if h["joint"] == 1: h["flat_r"] = mem["base"].disc_r + 1.0
    return mem

def build_order():
    """inner member of every joint first (the chain's stacking order is a DAG)"""
    names = ["base"] + [f"l{k}" for k in range(1, N)]; idx = {n: i for i, n in enumerate(names)}
    before = {n: set() for n in names}
    for J in range(1, N):
        lo = names[LOWER[J]]; up = names[J] if LOWER[J] == J - 1 else names[J - 1]; before[up].add(lo)
    order, done = [], set()
    while len(order) < len(names):
        for n in names:
            if n not in done and before[n] <= done: order.append(n); done.add(n)
    return order

def shared_core(outer, inner):
    """grid mask of `outer` inside the hub core of a joint it shares with `inner` (the stack zone: washers decide there)"""
    m = np.zeros(outer.D.shape[:-1], bool)
    for ho in outer.hubs:
        for hi in inner.hubs:
            if ho["joint"] == hi["joint"]:
                c = np.clip(outer.D @ ho["axis"], 1e-3, 1); m |= ho["lv"]["S"] * np.sqrt(1 - c * c) / c <= MB.HUB_R + 1.0
    return m

def rim_raise(mem):
    """top-mounted base (Ø32 disc over J1): link 1's top within the base disc (r <= disc + 1) must stay under the base's
    underside by the stack gap; raise J1 by the shortfall (returns mm)"""
    if not BASE_TOP_MOUNT or mem["base"].disc_r <= MB.HUB_R + 0.5: return 0.0
    L1, B0 = mem["l1"], mem["base"]; h1 = [h_ for h_ in L1.hubs if h_["joint"] == 1][0]; a = h1["axis"]; lv = h1["lv"]
    c = np.clip(L1.D @ a, 1e-3, 1); r_ = lv["S"] * np.sqrt(1 - c * c) / c; zone = (r_ > MB.HUB_R + 0.5) & (r_ <= B0.disc_r + 1.0) & (L1.sdf2(L1.X, L1.Y) <= 0)
    if not zone.any(): return 0.0
    top_axial = (L1.top * c)[zone].max()                                              # axial height of link 1's top in the zone
    return max(0.0, float(top_axial - (lv["U0"] - 0.1)) + 0.1)

def adjacent(m, o): return any(h1["joint"] == h2["joint"] for h1 in m.hubs for h2 in o.hubs)

def plan_order(mem, E, frames):
    """provisional fields (skin + band floor only) -> required lift for every ordering of every overlapping pair;
    adjacent pairs follow the joint stack, other pairs take the cheaper order; returns (order, outer_of dict)"""
    names = list(mem); off = np.r_[0, np.cumsum(R["sizes"])]; h = np.array(R["h"]); kd = np.array(R["kind"])
    for i, n in enumerate(names):
        m = mem[n]; m.grid(); m.env = E.min_radius(n, m.D.reshape(-1, 3)).reshape(m.D.shape[:-1])
        mi = 0 if n == "base" else int(n[1:]); m.base_floor = MB.band_baseline(m, R["dirs_local"][mi], h[off[mi]:off[mi + 1]], kd[off[mi]:off[mi + 1]])
        m.fields(m.env, baseline=m.base_floor)
    above = {}                                                                         # (outer, inner) -> lift
    for i, n in enumerate(names):
        for o in names[i + 1:]:
            m1, m2 = mem[n], mem[o]
            if adjacent(m1, m2):
                J = [h1["joint"] for h1 in m1.hubs for h2 in m2.hubs if h1["joint"] == h2["joint"]][0]
                up = n if [hh for hh in m1.hubs if hh["joint"] == J][0]["role"] == "upper" else o
                lo = o if up == n else n
                L, share, _ = MB.pair_lift(mem[up], mem[lo], frames, shared_core(mem[up], mem[lo])); above[(up, lo)] = (L, share, "stack")
            else:
                L12, s12, _ = MB.pair_lift(m1, m2, frames); L21, s21, _ = MB.pair_lift(m2, m1, frames)
                if L12 == 0 and L21 == 0 and s12 == 0 and s21 == 0: continue
                if L12 <= L21: above[(n, o)] = (L12, s12, f"chosen (other way {L21:.1f})")
                else: above[(o, n)] = (L21, s21, f"chosen (other way {L12:.1f})")
    for (u, l), (L, s, why) in above.items(): log(f"  {u} over {l}: lift {L:.1f} mm on {100 * s:.0f}% of {u}  [{why}]")
    before = {n: {l for (u, l) in above if u == n} for n in names}; order, done = [], set()
    while len(order) < len(names):
        prog = False
        for n in names:
            if n not in done and before[n] <= done: order.append(n); done.add(n); prog = True
        if not prog: raise RuntimeError(f"stacking cycle: {before}")
    return order, before

if __name__ == "__main__" and STAGE == "members":
    E = EV.Envelope(CAD_DIR); frames = [G for _, G in E.frames]; log(f"{KEY}: {len(frames)} followed frames")
    off = np.r_[0, np.cumsum(R["sizes"])]; hh = np.array(R["h"]); kd = np.array(R["kind"])
    def provisional(mem):
        for n, m in mem.items():
            m.grid(); m.env = E.min_radius(n, m.D.reshape(-1, 3)).reshape(m.D.shape[:-1]); mi = 0 if n == "base" else int(n[1:])
            m.base_floor = MB.band_baseline(m, R["dirs_local"][mi], hh[off[mi]:off[mi + 1]], kd[off[mi]:off[mi + 1]]); m.extra = []; m.fields(m.env, baseline=m.base_floor)
    mem = make_members(); provisional(mem)
    raise_ = {}
    for n, m in mem.items():
        for j, r, g in m.hub_report:
            if r == "lower" and g < 0 and j < N: raise_[j] = max(raise_.get(j, 0.0), -g + 0.05)
    if raise_:
        for j, d in raise_.items(): FACES[j] += d
        log("raised joint faces (mm):", {j: round(d, 2) for j, d in raise_.items()}); mem = make_members(); provisional(mem)
    for _ in range(3):
        rr = rim_raise(mem)
        if rr < 0.05: break
        FACES[1] += rr; log(f"raised J1 by {rr:.2f} mm so link 1's rim fits under the top-mounted base"); mem = make_members(); provisional(mem)
    def stack_pass(mem):
        names = list(mem); new = {n: [] for n in names}
        for a in names:
            for b in names:
                if a == b: continue
                core = shared_core(mem[a], mem[b]) if adjacent(mem[a], mem[b]) else None
                c = MB.location_constraint(mem[a], mem[b], frames, core, clear=MB.CLEAR_MM + 1.0)
                if c is not None: new[a].append(c)
        return new
    if MB.FAIR:                                                                        # joints high enough that every link leaves its hubs at <= 35 deg
        for it in range(3):
            MB._DECIDE.clear(); MB.HARD.clear(); MB.CE.clear()
            nw = stack_pass(mem)
            for n, m in mem.items(): m.extra = nw[n]; m.fields(m.env, baseline=m.base_floor)
            rz = {}
            for n, m in mem.items():
                for j, ex in getattr(m, "ramp_excess", {}).items():
                    if ex > 0.1: rz[j] = max(rz.get(j, 0.0), ex + 0.05)
            if not rz: break
            for j, d in rz.items(): FACES[j] += min(d, 4.0)
            log(f"ramp raises (mm): { {j: round(min(d, 4.0), 2) for j, d in rz.items()} }"); mem = make_members(); provisional(mem)
    names = list(mem)
    t0 = time.time(); new = {n: [] for n in names}                                     # one pass: stacking decided on the provisional shapes
    for a in names:
        for b in names:
            if a == b: continue
            core = shared_core(mem[a], mem[b]) if adjacent(mem[a], mem[b]) else None
            c = MB.location_constraint(mem[a], mem[b], frames, core, clear=MB.CLEAR_MM + 1.0)
            if c is not None: new[a].append(c)
    lifts = {}
    for n in names:
        m = mem[n]; old_bot = m.bot.copy(); m.extra = new[n]; m.fields(m.env, baseline=m.base_floor)
        ins = m.sdf2(m.X, m.Y) <= 0; lifts[n] = round(float((m.bot - old_bot)[ins].max()), 2)
    log(f"stacking lifts {lifts} ({time.time() - t0:.0f}s)")
    hard = np.zeros(len(frames), bool)
    for k, v in MB.HARD.items():
        if v.any(): log(f"  unresolvable overlap {k[0]} x {k[1]} in {int(v.sum())} frames")
        hard |= v
    np.save(os.path.join(OUT, "hard_frames.npy"), np.array([p for (p, _), h_ in zip(E.frames, hard) if h_], int))
    for n in names:
        m = mem[n]; log(f"{n}: hubs {[(j, r, round(g, 2)) for j, r, g in m.hub_report]} (hub plane - need)  min gap {m.gap_min:.2f}  t {m.t_min:.2f}  Lt {[round(x['Lt'], 1) for x in m.hubs]}")
        for j, r, g in m.hub_report:                                                 # r18 s1394 #1: J3 168 mm over its need, l2 twisted (0.52 cm3)
            if g > STANDOFF_MM: log(f"WARNING stand-off: {n} hub {j} ({r}) rides {g:.0f} mm above its need (> {STANDOFF_MM:.0f}): not a close-fitting design, the ribbon may twist")
    sol = {}
    for n in names:
        t0 = time.time(); s = mem[n].solid(); sol[n] = s
        log(f"{n}: solid valid {s.isValid()} faces {len(s.Faces())} vol {s.Volume() / 1000:.2f} cm3 thickness {np.round(mem[n].info['thickness'], 2)} ({time.time() - t0:.1f}s)")
        if s.Volume() <= 0: log(f"WARNING inside-out: {n} has volume {s.Volume() / 1000:.2f} cm3 (reversed or self-intersecting shell: contact judges would miss penetrations)")
    from OCP.BRepTools import BRepTools
    for n, s in sol.items(): BRepTools.Write_s(s.wrapped, os.path.join(OUT, f"{n}.brep"))
    pickle.dump(dict(FACES=FACES, mem={n: dict(bot=m.bot, top=m.top, top_hw=m.top_hw, xs=m.xs, ys=m.ys, c0=m.chart.c0, e1=m.chart.e1, R0=m.chart.R0, hubs=m.hubs) for n, m in mem.items()}), open(os.path.join(OUT, "fields.pkl"), "wb"))
    log("members done")

# ================================================================ stage "assemble": features, hardware, arm end, export
MAT = {"Ti": ("Ti-6Al-4V", 4.43), "igus": ("iglidur G", 1.46), "A2": ("A2 stainless", 7.9), "174": ("17-4PH H900", 7.8), "PEEK": ("PEEK", 1.32), "brg": ("52100 bearing steel", 7.8), "Al": ("7075-T6", 2.81), "AlSi": ("AlSi10Mg (SLM)", 2.67)}
def mat_of(name):
    n = name.lower()
    for k, key in (("alsi10mg", "AlSi"), ("iso 10642", "A2"), ("igus", "igus"), ("din 7984", "A2"), ("dowel", "A2"), ("17-4", "174"), ("peek", "PEEK"), ("bearing", "brg"), ("7075", "Al"), ("ti-6al-4v", "Ti")):
        if k in n: return key
    return "Ti"

def assemble():
    import cadquery as cq, trimesh
    from OCP.BRepTools import BRepTools
    from OCP.TopoDS import TopoDS_Shape
    from OCP.BRep import BRep_Builder
    import hardware as HWR
    P = pickle.load(open(os.path.join(OUT, "fields.pkl"), "rb")); FACES.update(P["FACES"]); mem = make_members()
    parts = []
    for n, m in mem.items():
        sh = TopoDS_Shape(); BRepTools.Read_s(sh, os.path.join(OUT, f"{n}.brep"), BRep_Builder()); s = cq.Shape.cast(sh)
        d = P["mem"][n]; from scipy.interpolate import RectBivariateSpline; fb = RectBivariateSpline(d["xs"], d["ys"], d["bot"], kx=3, ky=3, s=0)
        for h in m.hubs:
            a = h["axis"]; lv = h["lv"]
            others = [h2["axis"] for h2 in m.hubs if h2 is not h]
            arm = (others[0] - (others[0] @ a) * a) if others else (m.strip_dir if m.strip_dir is not None else None)
            yref = np.cross(a, arm) if arm is not None and np.linalg.norm(arm) > 1e-6 else None   # cap screws square to the arm
            lo_parts, up_parts = HWR.v4_joint_parts(a, lv, h["joint"], yref=yref)
            if h["role"] == "lower":
                s = HWR.v4_lower_features(s, a, lv); parts += [(n, nm, hs) for nm, hs in lo_parts]
            else:
                s = HWR.v4_upper_features(s, a, lv, yref=yref); parts += [(n, nm, hs) for nm, hs in up_parts]          # cap + sensor ride the upper member
        if n == "base" and BASE_TOP_MOUNT:                                                   # back-plate interface on top: 3x M2 blind, around the cap
            a = m.hubs[0]["axis"]; lv = m.hubs[0]["lv"]; n_, x_, y_ = HWR._frame(a, yref)                # the cap screws sit at +-y_ (90 / 270 deg)
            for k in range(3):
                ang = 2 * math.pi * k / 3; p = n_ * lv["U1"] + 12.0 * (math.cos(ang) * x_ + math.sin(ang) * y_)   # 0 / 120 / 240 deg: >= 30 deg from the cap screws, wall to the O28 disc
                s = s.cut(cq.Solid.makeCylinder(0.8, 3.2, cq.Vector(*(p - 3.0 * n_)), cq.Vector(*n_)))
        s = solid_fix(s); log(f"{n}: featured valid {s.isValid()} vol {s.Volume() / 1000:.2f} cm3")
        parts.append((n, f"{m.name} (Ti-6Al-4V)", s))
    import armend_fair as AF
    E = EV.Envelope(CAD_DIR)
    if R.get("cuff") and os.environ.get("CUFF_STYLE", "dovetail") == "wheels":
        track, info = AF.build_track_neck(E); carr, hw = AF.build_carriage(info); bm = AF.bottom_merged(track)
        parts += [("H", "BOTTOM + neck + V-track (one 5-axis part; V flanks hard-anodised / nitrided)", bm), ("cuff", "D4-C cuff carriage (Ti-6Al-4V)", carr)] + hw
    elif R.get("cuff"):
        track, info = (AF.build_dovetail_track_neck if os.environ.get("RAIL_V1") == "1" else AF.build_dovetail_rail_neck)(E); sad, hw = AF.build_saddle(info); bm = AF.bottom_merged(track)
        parts += [("H", "BOTTOM + neck + curved dovetail rail (one 5-axis part, Ti-6Al-4V)", bm), ("cuff", "D4-S cuff saddle (Ti-6Al-4V)", sad)] + hw
    else:
        blk, hw = (AF.build_hub_neck_v2 if os.environ.get('HUB_V1') is None else AF.build_hub_neck)(E); bm = AF.bottom_merged(blk)
        parts += [("H", "BOTTOM + neck + JN hub (one 5-axis part, 7075-T6 bead blasted)", bm)] + hw
    parts += AF.user_parts_rest()
    sc = trimesh.Scene()
    for k_, (g, nm, s) in enumerate(parts):
        vs, tr = s.tessellate(0.05, 0.12)                                                # light enough for the viewer + render payloads
        if not len(tr): log("no mesh", nm); continue
        mm = trimesh.Trimesh(np.array([[q.x, q.y, q.z] for q in vs]), tr, process=False); _ = mm.vertex_normals
        sc.add_geometry(mm, node_name=f"{g}|{nm}|{k_}", geom_name=f"{g}|{nm}|{k_}")
    sc.export(os.path.join(OUT, "exo.glb"))
    rows = []; os.makedirs(os.path.join(OUT, "step"), exist_ok=True)
    for k_, (g, nm, s) in enumerate(parts):
        user = g in ("H", "F") and not (nm.startswith(("BOTTOM +", "J", "UPPER ARM CUFF (conformal", "M4x6 ISO 10642")))
        vs_, tr_ = s.tessellate(0.02, 0.1); vol = abs(trimesh.Trimesh(np.array([[q.x, q.y, q.z] for q in vs_]), tr_, process=True).volume) / 1000.0; mk = mat_of(nm)
        rows.append(dict(k=k_, group=g, name=nm, vol_cm3=round(vol, 3), material="user part" if user else MAT[mk][0], mass_g=None if user else round(vol * MAT[mk][1], 2), valid=bool(s.isValid()), faces=len(s.Faces())))
        if nm.startswith(("D4-", "BOTTOM +", "UPPER ARM CUFF")): cq.exporters.export(cq.Workplane().add(s), os.path.join(OUT, "step", nm.split(" ")[0].replace("/", "_") + ".step"))
    json.dump(dict(key=KEY, n=N, FACES=FACES, parts=rows), open(os.path.join(OUT, "parts.json"), "w"), indent=1)
    tot = sum(r["mass_g"] for r in rows if r["mass_g"]); log(f"assembled {len(parts)} parts; custom mass {tot:.0f} g")

def CHf(a, b):
    sys.path.insert(0, os.path.join(CONF)); import cad_helpers as CH; return CH.fuzzy_fuse(a, b, tol=0.0)
def solid_fix(s):
    if not s.isValid():
        from OCP.ShapeFix import ShapeFix_Shape
        import cadquery as cq
        sf = ShapeFix_Shape(s.wrapped); sf.Perform(); s = cq.Shape.cast(sf.Shape())
    return s

if __name__ == "__main__" and STAGE == "assemble":
    assemble()
