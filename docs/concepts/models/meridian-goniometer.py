"""meridian-goniometer: J2 is an arc rail running beside the arm's elevation path about a VIRTUAL axis a2 (no J2 hub);
3 ACTIVE DOF, 0 passive. Built on the shared kit (tools/concept_kit.py, docs/concepts/KIT.md).

Topology (scapula handler -> user's upper-arm cuff):
    scapula base --J1 (O20 hub on a1, S-fixed)--> root (strap) + rail (one rigid part, the J1 rotor)
    --J2 (carriage riding the rail = rotation about the virtual axis a2)--> carriage + bridge (strap)
    --J3--> arm.   j3='hub':    J3 an O20 hub on p3 = HG(wdir(wd, wa)) (general spherical 3R, K7 neck to BOTTOM's bar)
                   j3='cslide': the spec - pointer (A1 = A2 = 90, p3 = the humerus axis) + pointer-cslide's humeral
                                C-slide (band in the pointing frame, arm-fixed shoe, neck down the arm), reused verbatim.
Kinematics: a2 = K1 closure(a1, p3, A1, A2, sigma) (A1 = A2 = 90: a2 = unit(a1 x t), the spec). In the J1 rotor frame a2
is fixed; e0 = a1 projected normal to a2, e1 = a2 x e0. q2 = the angle about a2 from a1 to p3 (axis_angle).

SPEC FIX (kinematic): the spec lets the rail radius follow the skin along phi (Rr(phi) = ENV + 2). A 30-50 deg
carriage is rigid, so its track must be a CIRCLE about a2 (any radius change along phi breaks the rotation about a2):
the rail is a spherical zone about GH (one radius Rr, 'cap' member: the max of the K3 march over its samples and the
fit poses), between cone angles alpha +- bw/2 about side*a2 (side = +-1), over phi in [window of q2] + dphi
+- (Lc/2 + 3 mm stop). Rail: bw x t_rail (26 x 6), skin face at Rr. Carriage: Lc deg x bw at Rr + t_rail + 0.15
(the running gap), t_car thick, centred at phi = q2 + dphi (dphi lets it lead / lag the arm). Bridge: 12 x 3 strap from
the carriage centre to J3 (hub3, or the C-slide band's proximal edge), passing over the rail, root and neck (`over`).
Root: 12 x 3 strap from hub 1 to the rail's end nearest a1 (one part with the rail).
q2 window: the smallest arc of q2 holding a share qcov of the closing bench poses (a design decision from the data,
cached, then fixed - like pointer-cslide's twist window); poses outside it are out of J2's range (not taken).
By-construction pairs (exempt from K6): rail-carriage (the bearing, 0.15 running gap), carriage-bridge and root-rail
(one part each), bridge-band (one part, cslide). Every other pair: K6 >= 1 mm lateral / 0.5 radial, or `over`.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/meridian-goniometer.py [check|redteam] ['{json params}']
"""
import importlib.util, itertools, json, math, os, sys
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402

# pointer-cslide's C-slide (band / shoe / neck, its fixed-geometry _levels and the exempt-pair K6) - reused, not copied
_sp = importlib.util.spec_from_file_location("pointer_cslide_model", os.path.join(os.path.dirname(os.path.abspath(__file__)), "pointer-cslide.py"))
PC = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(PC)
PC.EXEMPT |= {frozenset(x) for x in (("rail", "carriage"), ("carriage", "bridge"), ("root", "rail"), ("bridge", "band"))}

ID = "meridian-goniometer"
NAME = "Goniometer pointer: J2 is an arc rail running beside the arm's elevation path, no J2 hub"
PARAMS = dict(j3="hub", az=2.43, el=80.68, A1=76.9, A2=66.75, wd=86.33, wa=21.83, sigma=-1, sing=K.FOLD_MARGIN,
              side=1, alpha=45.0, dphi=0.0, Lc=40.0, qcov=0.95, bw=26.0, t_rail=6.0, t_car=3.0, r_lay=0.0,
              width=12.0, t_link=3.0, q=0.95,
              # j3='cslide' (pointer-cslide's C-slide; its best params)
              tilt=11.887, tilt_a=-89.719, s=111.051, phi_s=-18.349, Ls=39.464, cov=0.661, c_off=0.0, q_ring=0.991,
              r_block=87.767, saddle=1, neck="down", hub="o20")
RUN = 0.15


def wrap(x): return (np.asarray(x, float) + 180.0) % 360.0 - 180.0


def kin(F, p):
    """a1, a2, p3, e0, e1, q2 (deg), ok, margin (+ the C-slide's th for cslide)"""
    th = None
    if p["j3"] == "cslide":
        a1, a2, p3, xP, yP, E1, E2, th, ok, margin = PC.kin(F, p)
    else:
        a1 = F.S(K.bvec(p["az"], p["el"])); p3 = F.HG(K.wdir(p["wd"], p["wa"]))
        a2, ok, margin = K.closure(a1, p3, p["A1"], p["A2"], p["sigma"], margin_deg=p["sing"])
    a2 = K.unit(a2)
    e0 = K.unit(a1 - (a1 * a2).sum(-1, keepdims=True) * a2); e1 = np.cross(a2, e0)
    q2 = K.axis_angle(a2, a1, p3)
    return a1, a2, p3, e0, e1, q2, ok, margin, th


_CACHE = {}


def design(B, p):
    """fixed design decisions from the full bench (cached): the q2 window (c2, T2) and the rail's phi extent"""
    key = json.dumps(sorted((k, v) for k, v in p.items() if k != "_bench"), default=str)
    if key in _CACHE: return _CACHE[key]
    F = B._kitF; a1, a2, p3, e0, e1, q2, ok, margin, th = kin(F, p)
    if p["j3"] == "cslide":
        Dd = PC.design(B, p); ok = ok & (np.abs(wrap(th - Dd["c"])) <= Dd["T"] / 2 + 1e-9)
    c2, T2 = PC.window(q2, ok, p["qcov"])
    rl = p["r_lay"] if p["r_lay"] > 0 else 70.0
    for it in range(3 if p["r_lay"] <= 0 else 1):   # r_lay <= 0: lay the rail out at its own fitted radius (fixed point)
        sa = math.sin(math.radians(p["alpha"])); stop = math.degrees(3.0 / max(5.0, rl * sa))
        lo = c2 - T2 / 2 + p["dphi"] - p["Lc"] / 2 - stop; hi = c2 + T2 / 2 + p["dphi"] + p["Lc"] / 2 + stop
        if p["r_lay"] > 0 or it == 2: break
        okw = ok & (np.abs(wrap(q2 - c2)) <= T2 / 2 + 1e-9); Pi = np.nonzero(okw)[0]
        if not len(Pi): break
        pl = dict(p, r_lay=rl); ph = np.linspace(lo, hi, ncols(hi - lo, pl))
        Dz = zone(p["side"] * a2[Pi], e0[Pi], e1[Pi], ph, pl); n = Dz.shape[1]
        R = K.requirement(B, np.repeat(Pi, n), Dz.reshape(-1, 3)).reshape(len(Pi), n)
        rl = float(np.clip(K.quantile(R, p["q"]).max(), 40.0, 220.0))
    _CACHE[key] = dict(c2=c2, T2=T2, lo=lo, hi=hi, rl=rl)
    return _CACHE[key]


def strap(name, u, v, joints, rl, width=12.0, t=3.0, ramp_to=(), climb_deg=60.0, **kw):
    """K.strap_member with its layout at r_ref = rl (the straps here sit near the rail's radius, not at 70 mm)"""
    D = K.strap_dirs(u, v, None, width=width, r_ref=rl); ns, nc = D.shape[1:3]
    n_end = int(math.ceil((K.HUB_R + 2.0) / 2.0)) + 1; s = np.repeat(np.arange(ns), nc); ramps = []
    for (h, dz), m in zip(ramp_to, (s < n_end, s >= ns - n_end)):
        if h: ramps.append((m, h, dz))
    return K.Member(name, D.reshape(len(D), -1, 3), t=t, width=width, joints=tuple(joints), grid=(ns, nc), climb_deg=climb_deg,
                    ramps=ramps, strap=True, r_ref=rl, **kw)


def zone(a2s, e0, e1, phi_deg, p):
    """directions (P, rows * cols, 3) of a spherical zone about a2s: cone alpha +- bw/2 (2 mm rows at r_lay), phi columns
    (P, n) or (n,) deg"""
    rl = p["r_lay"]; hb = p["bw"] / 2 / rl
    beta = math.radians(p["alpha"]) + np.linspace(-hb, hb, int(round(p["bw"] / 2.0)) + 1)
    ph = np.radians(np.broadcast_to(np.asarray(phi_deg, float), (len(e0), np.shape(phi_deg)[-1])))
    u = np.cos(ph)[..., None] * e0[:, None] + np.sin(ph)[..., None] * e1[:, None]                      # (P, n, 3)
    D = np.cos(beta)[None, :, None, None] * a2s[:, None, None] + np.sin(beta)[None, :, None, None] * u[:, None]
    return D.reshape(len(e0), -1, 3)


def ncols(span_deg, p, step=2.0):
    return max(2, int(math.ceil(math.radians(abs(span_deg)) * p["r_lay"] * math.sin(math.radians(p["alpha"])) / step)) + 1)


def build_chain(B, F, p):
    if getattr(B, "_kitF", None) is None: B._kitF = K.frames(B)
    a1, a2, p3, e0, e1, q2, ok, margin, th = kin(F, p); Dd = design(B, p)
    ok = ok & (np.abs(wrap(q2 - Dd["c2"])) <= Dd["T2"] / 2 + 1e-9)                           # J2 range: the q2 window
    p = dict(p, r_lay=Dd["rl"]); a2s = p["side"] * a2; rl = p["r_lay"]
    rail_phi = np.linspace(Dd["lo"], Dd["hi"], ncols(Dd["hi"] - Dd["lo"], p))
    car_phi = q2[:, None] + p["dphi"] + np.linspace(-p["Lc"] / 2, p["Lc"] / 2, ncols(p["Lc"], p))[None, :]
    rail = K.Member("rail", zone(a2s, e0, e1, rail_phi, p), kind="cap", t=p["t_rail"], width=p["bw"], joints=("J2",), r_ref=rl)
    carriage = K.Member("carriage", zone(a2s, e0, e1, car_phi, p), kind="cap", t=p["t_car"], width=p["bw"], joints=("J2",),
                        r_ref=rl, ramps=[(np.ones(0, bool), "rail", 0.0)])
    carriage.ramps = [(np.ones(carriage.D.shape[1], bool), "rail", p["t_rail"] + RUN)]
    ca = math.radians(p["alpha"]); cph = np.radians(q2 + p["dphi"])
    cdir = math.cos(ca) * a2s + math.sin(ca) * (np.cos(cph)[:, None] * e0 + np.sin(cph)[:, None] * e1)
    near = Dd["lo"] if abs(wrap(Dd["lo"])) <= abs(wrap(Dd["hi"])) else Dd["hi"]; nr = math.radians(near)
    rend = math.cos(ca) * a2s + math.sin(ca) * (math.cos(nr) * e0 + math.sin(nr) * e1)
    w, t = p["width"], p["t_link"]
    hub1 = K.hub_member("hub1", a1, "J1")
    root = strap("root", a1, rend, ("J1",), rl, width=w, t=t, ramp_to=(("hub1", K.STACK), ("rail", 0.0)))
    if p["j3"] == "cslide":
        pc = PC.build_chain(B, F, p); mem = {m.name: m for m in pc.members}
        D2 = PC.design(B, p); c, rho, s = D2["c"], D2["rho"], p["s"]
        _, _, d3, xP, yP, *_ = PC.kin(F, p)
        att = K.unit(PC.ring_pts(None, xP, yP, d3, [s - PC.BAND_W / 2 + 1], [c], rho + PC.LIP)[:, 0])
        bridge = strap("bridge", cdir, att, ("J2", "J3"), rl, width=w, t=t, ramp_to=(("carriage", 0.0), (None, 0.0)),
                                over=[("rail", 1.0), ("root", 1.0)])
        tail = [mem["band"], mem["shoe"], mem["neck"]]; ok = ok & pc.ok; q3 = th; hubless = ("J2", "J3")
        info = dict(pc.info); res = K.closure_residual(a1, p3, a2, p["A1"], p["A2"])
    else:
        hub3 = K.hub_member("hub3", p3, "J3")
        neck = K.neck_member(F, p3, joints=("J3",), ramps=(("hub3", 0.0), (None, 0)))
        bridge = strap("bridge", cdir, p3, ("J2", "J3"), rl, width=w, t=t, ramp_to=(("carriage", 0.0), ("hub3", K.STACK)),
                                over=[("rail", 1.0), ("root", 1.0), ("neck", 1.0)])
        tail = [hub3, neck]; q3 = K.axis_angle(p3, F.HG([0.0, -1, 0]), a2); hubless = ("J2",)
        info = {}; res = K.closure_residual(a1, p3, a2, p["A1"], p["A2"])
    q = np.stack([K.axis_angle(a1, F.S([1.0, 0, 0]), a2), q2, q3], -1)
    info.update(residual_deg=round(float(res[ok].max()), 5) if ok.any() else None,
                min_margin=round(float(margin[ok].min()), 2) if ok.any() else None,
                q2_c=round(float(Dd["c2"]), 1), q2_T=round(float(Dd["T2"]), 1), rail_arc=round(float(Dd["hi"] - Dd["lo"]), 1))
    return K.Chain(members=[hub1, root, rail, carriage, bridge] + tail, ok=ok, q=q, joints=dict(J1=a1, J2=a2, J3=p3),
                   hubless=hubless, info=info)


def bench_eval(B, params):
    """the sweep hook: honest kit evaluation (march, K2 dense, K6) (+ the C-slide's outer-face torso contact)"""
    p = dict(PARAMS, **params)
    if getattr(B, "_kitF", None) is None: B._kitF = K.frames(B)
    rep = K.evaluate(B, build_chain, p)
    if p["j3"] == "cslide": rep = PC.outer_contact(B, p, rep)
    L = B._kit_last; rep["rail_r"] = round(float(L["prof"]["rail"].max()), 1); rep["r_lay"] = round(design(B, p)["rl"], 1)
    if rep["rail_r"] >= 220.0:   # the K3 march found no clearance within 220 mm for a rail sample in a fit pose (inf -> 400):
        rep["honest"] = False     # the rail passes through the body there; parking it at the fallback radius is not a design
        rep["audit"] = list(rep.get("audit") or []) + [f"rail parked at the fallback radius ({rep['rail_r']} mm): a rail sample has no skin clearance within 220 mm"]
    return json.loads(json.dumps(rep, default=lambda o: o.item() if hasattr(o, "item") else str(o)))


def metal(pose, frames, params):
    L = getattr(frames, "_kit_last", None)
    if L is None or not L["take"][pose]: return None
    return np.concatenate([L["pts"][m.name][pose] for m in L["chain"].members], 0)


if __name__ == "__main__":
    a = sys.argv[1:] or ["check"]
    FARM = a[0] in ("farm", "farmcma")
    if not FARM: B = K.bench(60, 160); B._kitF = K.frames(B)
    p = dict(PARAMS, **(json.loads(a[1]) if len(a) > 1 and not FARM else {}))
    if a[0] == "check":
        import time; t0 = time.time(); r = bench_eval(B, p); print(round(time.time() - t0, 1), "s")
        print({k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "closure", "collide", "flips",
                                     "honest", "audit", "rail_r", "q2_c", "q2_T", "rail_arc", "mass_g", "residual_deg")})
        print(r["inband_member"])
        L = B._kit_last; tk = L["take"]
        for m in L["chain"].members:
            X = np.linalg.norm(L["pts"][m.name], axis=-1)
            d = K.dist_many(B, np.repeat(np.nonzero(tk)[0], X.shape[1]), L["pts"][m.name][tk].reshape(-1, 3)) if tk.any() else np.zeros(1)
            print(f"{m.name:9s} radius {X.min():6.1f} {X.max():6.1f} skin dist med/p10/p90", np.percentile(d, [50, 10, 90]).round(1))
    elif a[0] == "redteam":
        r = bench_eval(B, p); print({k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}, r["inband_member"])
        L = B._kit_last; ch = L["chain"]; F = B._kitF; a1, a2, p3, e0, e1, q2, ok0, margin, th = kin(F, p); Dd = design(B, p)
        win = np.abs(wrap(q2 - Dd["c2"])) <= Dd["T2"] / 2 + 1e-9
        pz = np.array([(x["plane"], x["elev"], x["axial"]) for x in B.poses])
        tg = dict(rest=(0, 0, 0), rest_ir=(0, 0, -80), rest_er=(0, 0, 60), abd90=(0, 90, 0), overhead_abd=(0, 160, 0),
                  overhead_flex=(90, 160, 0), across_body=(130, 90, 0), across_low=(120, 45, -40), behind_back=(-90, 40, -90),
                  ext=(-60, 50, 0), abd90_ir=(0, 90, -80), abd90_er=(0, 90, 90))
        for nm, t3 in tg.items():
            dd = np.abs(pz - np.array(t3)); dd[:, 2] = np.minimum(dd[:, 2], 360 - dd[:, 2]); i = int(np.argmin(dd @ [1, 1, 0.5]))
            why = "TAKEN" if L["take"][i] else ("singular" if not ok0[i] else "q2-window" if not win[i] else "range/K2" if not L["ok"][i] else "collide" if L["hit"][i] else "contact")
            line = f"{nm:13s} pose {i:3d} {B.kind[i]:4s} {tuple(round(float(x)) for x in pz[i])} q2 {q2[i]:7.1f} margin {margin[i]:5.1f} {why}"
            if L["take"][i] or why == "contact":
                for m in ch.members:
                    dm = K.dist_many(B, np.full(L["pts"][m.name].shape[1], i), L["pts"][m.name][i]); line += f" | {m.name} {dm.min():.1f}/{np.median(dm):.1f}"
            if why == "collide":
                pr = []
                for x, y in itertools.combinations(ch.members, 2):
                    sub = K.Chain(members=[x, y], ok=ch.ok, joints=ch.joints); msk = np.zeros(len(L["ok"]), bool); msk[i] = True
                    if K.collisions(sub, {x.name: L["pts"][x.name], y.name: L["pts"][y.name]}, msk)[i]: pr.append(f"{x.name}-{y.name}")
                line += " " + ",".join(pr)
            print(line)
    elif a[0] in ("farm", "farmcma"):
        # farm  '<configs.json>'               : evaluate a list of configs on the cloud CPU farm, append to the sweep file
        # farmcma '{overrides}' [n_gen] [pop] [sigma] [j3] : CMA-ES from the best config of the sweep (the loop to continue)
        #   RUNPOD_API_KEY="$(cat ~/.runpod_key)" python3 docs/concepts/models/meridian-goniometer.py farmcma '{}' 8 32
        import subprocess, tempfile
        SW = os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json")

        def run(cfg, where):
            td = tempfile.mkdtemp(); json.dump(cfg, open(os.path.join(td, "c.json"), "w"))
            subprocess.run([sys.executable, os.path.join(REPO, "tools", "cloud_run.py"), "sweep", os.path.abspath(__file__), "--configs",
                            os.path.join(td, "c.json"), "--out", os.path.join(td, "r.json")], cwd=REPO, check=False)
            try: res = {r["i"]: r for r in json.load(open(os.path.join(td, "r.json")))}
            except Exception: res = {}
            rows = json.load(open(SW)) if os.path.exists(SW) else []; fs = []
            for i, pp in enumerate(cfg):
                rep = (res.get(i) or {}).get("report") or {}; fs.append(rep.get("gap", 400.0) + (0 if rep.get("honest", True) else 100))
                if rep: rows.append(dict(k=len(rows), t=K.now(), params=pp, **{x: rep[x] for x in ("inband14", "inband10", "reach", "follow", "contact", "gap")},
                                        closure=rep.get("closure"), honest=rep.get("honest"), rail_r=rep.get("rail_r"), q2_T=rep.get("q2_T"),
                                        mass_g=rep.get("mass_g"), inband_member=rep.get("inband_member"), audit=rep.get("audit"), where=where))
            json.dump(rows, open(SW + ".tmp", "w"), indent=1); os.replace(SW + ".tmp", SW)
            return fs, rows
        if a[0] == "farm":
            cfg = json.load(open(a[1])); fs, rows = run(cfg, "farm-sobol"); print("best", min(fs), "overall", min(r["gap"] for r in rows))
        else:
            import cma
            rows = json.load(open(SW)); j3 = a[5] if len(a) > 5 else None
            cand = [r for r in rows if r.get("honest") and (j3 is None or r["params"].get("j3", "hub") == j3)]
            b = dict(PARAMS, **min(cand, key=lambda r: r["gap"])["params"], **(json.loads(a[1]) if len(a) > 1 else {}))
            if b["j3"] == "hub":
                SP = dict(az=(b["az"] - 30, b["az"] + 30), el=(max(0, b["el"] - 25), min(90, b["el"] + 25)), A1=(50, 110), A2=(40, 110),
                          wd=(50, 120), wa=(b["wa"] - 60, b["wa"] + 60), alpha=(8, 85), dphi=(-60, 60), Lc=(25, 50), qcov=(0.4, 1.0), q=(0.85, 1.0))
            else:
                SP = dict(az=(b["az"] - 25, b["az"] + 25), el=(b["el"] - 20, b["el"] + 20), alpha=(8, 85), dphi=(-60, 60), Lc=(25, 50),
                          qcov=(0.4, 1.0), q=(0.85, 1.0), s=(100, 200), phi_s=(-60, 60), cov=(0.5, 0.92))
            ks = list(SP); enc = lambda pp: np.clip([(pp[k] - SP[k][0]) / (SP[k][1] - SP[k][0]) for k in ks], 0, 1)
            dec = lambda x: dict(b, **{k: round(float(SP[k][0] + np.clip(x[i], 0, 1) * (SP[k][1] - SP[k][0])), 3) for i, k in enumerate(ks)})
            es = cma.CMAEvolutionStrategy(enc(b), float(a[4]) if len(a) > 4 else 0.15,
                                          dict(popsize=int(a[3]) if len(a) > 3 else 32, seed=11, bounds=[0, 1], verbose=-9))
            for g in range(int(a[2]) if len(a) > 2 else 8):
                X = es.ask(); cfg = [dec(x) for x in X]; fs, rows = run(cfg, "farm-cma"); es.tell(X, fs)
                print("gen", g, "best", round(min(fs), 2), "overall", min(r["gap"] for r in rows if r.get("honest")), flush=True)
