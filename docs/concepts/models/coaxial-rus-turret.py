"""coaxial-rus-turret: the human-closed 3-RUS truss with all three active crank bearings STACKED on ONE axis at one
quiet scapula seat (a coaxial spherical parallel mechanism - the "coaxial-input SPM" of the parallel-kinematics
literature - with the user's humerus as the moving platform and the user's GH as its centre).

Why (docs/concepts/coaxial-rus-turret.md): in foldfree-rus-truss every leg has its own fold band
angle(c_k, Q_k) in [|beta_k - gamma_k|, beta_k + gamma_k]; ends.json says ONE crank axis (posterior-horizontal,
bvec(-30..-24, 4..8), hub band 100 %) is fold-free with MANY arm-stud directions. A coaxial turret puts all three legs on
that one best seat:
  * no base brackets between hubs, one hub footprint on the quietest scapula skin;
  * MVP2: three motors on one axis at one place (one cable bundle);
  * conditioning: a coaxial SPM is non-singular when the three moment lines T_k x Q_k span 3-space (det >= 0.10).
Mobility (bench, GH fixed): 3 x (R 1 + U 2 + S 3) + GH 3 - 3 x 6 = 3 (rod spins killed by the U pitch pins); the 3
crank angles are the only coordinates; 0 passive translations.

Real stack: crank k rides its own thin-section bearing on the common O20 hub shaft, one layer per crank:
3 mm Ti plate + 1.5 mm (bearing shoulder / iglidur thrust washer) -> LAYER 4.5 mm; hub stack 12.25 + 2 x 4.5 = 21.25 mm.
Each crank's whole profile is layered over the one below it (rho_k(alpha) >= rho_{k-1}(alpha) + LAYER), so crank plates
never meet; U housings, rods and everything else go through the 1 mm part-clearance check.

Implementation: the verified-in-structure base model docs/concepts/models/human-closed-crank-rods.py is loaded from its
source with the explicit PATCHES below (each must match exactly once; the loader asserts it), so the diff to the base is
these few lines. Bench hooks / frozen wear / red team come from foldfree-rus-truss.py.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/coaxial-rus-turret.py check '<params json>'
    ... frozen '<params json>' out.json --big
"""
import importlib.util, json, os, sys, time, types

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))

ID = "coaxial-rus-turret"
NAME = "Coaxial RUS turret: three stacked crank bearings on one posterior scapula seat, O5 rods to arm studs, the user's GH closes the loop"
LAYER = 4.5

PATCHES = [
    # 1. coaxial: one hub face; crank k's plate one LAYER above crank k-1 (F[k] is the crank-plate reference)
    ("        # brackets: the two shortest edges between hubs\n",
     "        if P.get('coax'):\n"
     "            F0 = max(D['F']); D['F'] = [F0 + kk * LAYER for kk in range(3)]\n"
     "        # brackets: the two shortest edges between hubs\n"),
    # 2. coaxial: no base brackets (one hub)
    ("        pairs = sorted([(math.acos(np.clip(D[\"c\"][a] @ D[\"c\"][b], -1, 1)), a, b) for a, b in ((0, 1), (0, 2), (1, 2))])[:2]\n",
     "        pairs = [] if P.get('coax') else sorted([(math.acos(np.clip(D[\"c\"][a] @ D[\"c\"][b], -1, 1)), a, b) for a, b in ((0, 1), (0, 2), (1, 2))])[:2]\n"),
    # 3. coaxial: every crank profile layered over the crank below it wherever both exist
    ("            tip = int(np.argmin(np.abs(alphas - b)))\n",
     "            if P.get('coax') and k > 0:\n"
     "                lo_ = D['cr'][k - 1]; rl = np.interp(alphas, lo_['alphas'], lo_['rho'], right=-1e9); prof = np.maximum(prof, rl + LAYER)\n"
     "            tip = int(np.argmin(np.abs(alphas - b)))\n"),
    # 4. coaxial: one hub member, its stack 2 layers taller (wall and crown contact-checked up to the real top)
    ("        for k in range(3):                                               # hubs\n"
     "            c = RS @ D[\"c\"][k]; e1 = RS @ D[\"e1\"][k]; e2 = RS @ D[\"e2\"][k]; F = D[\"F\"][k]\n"
     "            disc = F * c + GX[:, None] * e1 + GY[:, None] * e2\n"
     "            a = np.linspace(0, 2 * math.pi, 16, endpoint=False); rim = HUB_R * (np.cos(a)[:, None] * e1 + np.sin(a)[:, None] * e2)\n"
     "            lv = np.array([0.0, 4.0, 8.0, HUB_TOP]); cyl = (F + lv[:, None, None]) * c + rim[None]\n"
     "            core = np.concatenate([cyl.reshape(-1, 3), (F + HUB_TOP) * c + 0.6 * GX[:, None] * e1 + 0.6 * GY[:, None] * e2, disc])\n"
     "            M[f\"hub{k}\"] = dict(score=disc, extra=np.concatenate([cyl.reshape(-1, 3), (F + HUB_TOP) * c + 0.8 * GX[:, None] * e1 + 0.8 * GY[:, None] * e2]),\n",
     "        coax = D['P'].get('coax'); TOP_ = HUB_TOP + (2 * LAYER if coax else 0.0)\n"
     "        for k in (range(1) if coax else range(3)):                     # hubs (coaxial: ONE stacked hub)\n"
     "            c = RS @ D[\"c\"][k]; e1 = RS @ D[\"e1\"][k]; e2 = RS @ D[\"e2\"][k]; F = D[\"F\"][k]\n"
     "            disc = F * c + GX[:, None] * e1 + GY[:, None] * e2\n"
     "            a = np.linspace(0, 2 * math.pi, 16, endpoint=False); rim = HUB_R * (np.cos(a)[:, None] * e1 + np.sin(a)[:, None] * e2)\n"
     "            lv = np.arange(0.0, TOP_ + 1e-6, 4.0); lv[-1] = TOP_; cyl = (F + lv[:, None, None]) * c + rim[None]\n"
     "            core = np.concatenate([cyl.reshape(-1, 3), (F + TOP_) * c + 0.6 * GX[:, None] * e1 + 0.6 * GY[:, None] * e2, disc])\n"
     "            M[f\"hub{k}\"] = dict(score=disc, extra=np.concatenate([cyl.reshape(-1, 3), (F + TOP_) * c + 0.8 * GX[:, None] * e1 + 0.8 * GY[:, None] * e2]),\n"),
    # 5. coaxial: every crank is the hub's joint partner
    ("        if x.startswith(\"hub\") and y == \"crank\" + x[3:]: return True\n",
     "        if x.startswith(\"hub\") and y == \"crank\" + x[3:]: return True\n"
     "        if D['P'].get('coax') and x == 'hub0' and y.startswith('crank'): return True\n"),
]


_spec = importlib.util.spec_from_file_location("ffrus_for_coax", os.path.join(HERE, "foldfree-rus-truss.py"))
F = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(F)
H = F.load_base(PATCHES, name="hccr_coax", glb=dict(LAYER=LAYER))   # foldfree-rus-truss's patches (studs3) + the coaxial ones
F.H = H                                                            # the hooks below run on the patched base
CB = H.CB

SEAT = [-30.0, 8.0]                                                # ends.json: posterior-horizontal, hub band 1.00, fold-free
PARAMS = dict(H.PARAMS)
PARAMS.update(coax=True, hubs=[SEAT, SEAT, SEAT], beta=[65.0, 55.0, 45.0], sigma=[1, 1, 1],
              studs=[[40.0, 75.0], [110.0, 45.0]])
F.PARAMS = PARAMS
FLAT = ("az", "el", "b0", "b1", "b2", "s1", "t1", "s2", "t2", "s3", "t3", "h_stud")


def nest(p):
    q = {k: v for k, v in p.items() if k not in FLAT and not k.startswith("sg")}
    if "az" in p: q["hubs"] = [[float(p["az"]), float(p["el"])]] * 3
    if "b0" in p: q["beta"] = [float(p[f"b{k}"]) for k in range(3)]
    if "sg0" in p: q["sigma"] = [int(round(p[f"sg{k}"])) for k in range(3)]
    if "t1" in p:
        q["studs3"] = True; q["studs"] = [[float(p[f"s{k}"]), float(p[f"t{k}"])] for k in (1, 2, 3)]
    elif "s2" in p: q["studs"] = [[float(p["s2"]), float(p["t2"])], [float(p["s3"]), float(p["t3"])]]
    for k in ("h_stud",):
        if k in p: q[k] = float(p[k])
    q["coax"] = True
    return q


def bench_eval(B, params):
    P = dict(PARAMS); P.update(params or {}); P["coax"] = True
    P["hubs"] = [list(P["hubs"][0])] * 3                             # one axis for all three cranks
    return F.bench_eval(B, P)


def evaluate(B, p):
    r = bench_eval(B, nest(p)); r["honest"] = True
    for k in ("rT", "L", "F"): r.pop(k, None)
    return dict(p), r


def frozen(params, nc=110, nw=360, exact=True):
    P = dict(PARAMS); P.update(params or {}); P["coax"] = True; P["hubs"] = [list(P["hubs"][0])] * 3
    return F.frozen(P, nc, nw, exact)


if __name__ == "__main__":
    a = sys.argv[1:]; mode = a[0] if a else "check"
    par = json.loads(a[1]) if len(a) > 1 and a[1].startswith("{") else {}
    nc, nw = (110, 360) if "--big" in a else (60, 160)
    t0 = time.time()
    if mode == "frozen":
        out = frozen(par, nc, nw, exact=True)
        print(json.dumps(dict(secs=round(time.time() - t0, 1), **out), indent=1, default=float))
        if len(a) > 2 and not a[2].startswith("-"): json.dump(out, open(a[2], "w"), indent=1, default=float)
        sys.exit(0)
    B = CB.Bench(nc, nw)
    print(json.dumps(dict(mode=B.mode, secs=None, report=bench_eval(B, par)), indent=1, default=float))
