"""ikring-thinstack-knuckle-4r (round 301, O1 track overhead, lens rocker-redundant-4r): the verified lead
conecut-knee-knuckle-3r UNCHANGED plus phi40-thinstack-relay-4r's verified arm-fixed hardware (1.0 mm slotted Ti shell on a
4 mm liner, 14 x 14 T-nut carriage h_c 1.4, L-lug bracket at the pad azimuth, flange, band 8 / bump 1.2, lean slot-end
stops) with the constant-force coil DELETED: J4 is an ACTIVE, counted ring joint (psi in [0, PHI] about a GH-through axis
tilted 8.5 deg toward taz 243) whose value is set per pose by a LEAD-FIRST PROXIMITY IK:

  * k-TABLE: for every k in 0, 2.5, ..., PHI the frozen lead (shape fitted at k = 0 on Bench(60,160) fast) is worn exact
    with the arm-side frame turned k about a_r, INCLUDING the shell / carriage / bracket / flange metal and the jam rule
    (phi40's rerecord; one pose = one k, carriage at th0 + delta + k in the arm frame).
  * IK: psi = 0 where k = 0 takes the pose (metal >= 0, no jam); else the k with the LARGEST min metal among the k that
    take it (ties -> smaller k); a pose no k takes: the k with the largest min metal among the k that close (a contact),
    else 0 (lost). Clip frames: psi = 0 (lead-first; the claim-bench lead follows 1.0).
  * FINAL WEAR: one frozen exact wear of the whole bench with the chosen psi per pose (the same rerecord), so every
    number (in-band, chain-only gate, 1 / 2 mm readings, contacts, th margin, per-pose dump) comes from ONE wear.
  * CONTINUITY (the IK flood): the 1432-node envelope grid; per node and per k the lead's kinematic gates (AA.gate);
    a node's states are its contiguous feasible-k runs (J4 is active: self-motion inside a run at a fixed arm pose,
    every 2.5-deg step checked for K / knee pins <= 10 and actives <= 25); an edge from a state is valid if a greedy k
    path (nearest feasible k to the previous frame, ties -> smaller) along the 2-deg slerp keeps |dk| <= 10, K / knee
    pins <= 10 and actives <= 25 at every frame; seeds = k = 0 state-A nodes at elev 0. A relayed bench take counts only
    if its node's reached runs contain the IK's k (PT.wear's cmap drop).
  * CONTROL (unpowered, the same hardware): phi40's least-phi relay at the same axis (PT.prepare with flood).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/ikring-thinstack-knuckle-4r.py flood '<json>'          # IK flood (kinematic, cached)
    CB_EXACT=1 ... ik '<json>' bench out.json        # k-table + IK + final wear on Bench(110,360) exact (frozen)
    CB_EXACT=1 ... ik '<json>' held out.json         # the same on the held-out bench (report only)
    CB_EXACT=1 ... control '<json>' out.json         # least-phi unpowered control, Bench(110,360) exact
    CB_EXACT=1 ... rechoose '<json>' bench out.json prev.json   # final wear only, a previous run's k-table choice under IK_RULE
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
_sp = importlib.util.spec_from_file_location("phi40_for_ikring", os.path.join(HERE, "phi40-thinstack-relay-4r.py"))
P4 = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(P4)
OS, PT, BV, AA, CB = P4.OS, P4.PT, P4.BV, P4.AA, P4.CB
CC = PT.CC
ID = "ikring-thinstack-knuckle-4r"
D2R = math.pi / 180
VDIR = os.path.join(REPO, "docs", "concepts", "verify", ID); os.makedirs(VDIR, exist_ok=True)
PT.VDIR = VDIR; OS.VDIR = VDIR; P4.VDIR = VDIR
CLAIM = dict(P4.CLAIM_PARENT, **P4.HW0)
CLAIM.update(PHI=40.0, tilt=8.5, taz=243.0, delta=3.5, coil="none", flood=0)     # pre-registered cell (judge): coil deleted
KSTEP = 2.5
RULE = os.environ.get("IK_RULE", "take-only")       # 'take-only' (the spec: the ring moves only for a take) | 'closest-contact'
ATTR = ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
        "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info", "_wedge_info", "cyl_r")


def kgrid(PHI): return [round(float(k), 3) for k in np.arange(0.0, PHI + 1e-9, KSTEP)]


def fit(base):
    """the lead fit (Bench(60,160) fast, k = 0) + the relay axis; returns the fit context"""
    rp = dict(PT.DEF); rp.update({k: base[k] for k in PT.DEF if k in base})
    P = CC._clamp(dict(CC.PARAMS, **AA.LEAD, **{k: v for k, v in base.items() if k not in PT.DEF}))
    old = os.environ.pop("CB_EXACT", None)
    try:
        B1 = CB.Bench(n_clip=60, n_ws=160); M1 = CC.CCModel(B1, dict(P)); r1 = M1.run()
        fitr = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    ax = AA.raxis(rp["tilt"], rp["taz"]); P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(CC.CCModel):
        def fit(self):
            for a in ATTR:
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self._sc = None; self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]
            self.drop = np.zeros(len(self.poses_fit), bool); self._truncate()
    return dict(rp=rp, M1=M1, B1=B1, P2=P2, ax=ax, fit=fitr, Frozen=Frozen)


def subbench(Bf, sel):
    """a bench of the poses sel of Bf with unbounded skin / distance caches (the k-table re-wears the same poses)"""
    class Sub(CB.Bench):
        def __init__(s):
            s.__dict__.update({k: v for k, v in Bf.__dict__.items() if k not in ("_skin", "_ex", "_frames")})
            s.idx = Bf.idx[sel]; s.kind = [Bf.kind[j] for j in sel]; s.clip = [Bf.clip[j] for j in sel]; s.poses = [Bf.poses[j] for j in sel]
            s.res = [None] * len(sel); s._skin = {}; s._ex = {}; s._frames = {}; s.grid = None; s._V = None; s.mode = "exact"

        def _verts(s, i):
            if i not in s._skin: s._skin[i] = CB.BP.posed(s.poses[i])
            return s._skin[i]

        def _exact(s, i, Pp):
            if i not in s._ex: s._ex[i] = CB._Exact(s._verts(i))
            return s._ex[i](Pp)
    return Sub()


def wear_phi(F, B, phi_glob, hw, cmap=None):
    """frozen wear of bench B with the per-archive-pose relay angle phi_glob + phi40's hardware rerecord -> (o, S)"""
    Zr = AA.relayed_Z(phi_glob, F["ax"]); B.reset()
    with AA.patched(Zr):
        M = F["Frozen"](B, F["P2"]); r = M.run()
    ideal = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    S = dict(rp=dict(F["rp"]), M1=F["M1"], B1=F["B1"], M=M, B=B, ax=F["ax"], phi_b=phi_glob[B.idx], fit=F["fit"], ideal=ideal,
             cmap=cmap, flood=None, res0=[None if x is None else np.array(x) for x in B.res], why0=np.asarray(M.why, dtype=object).copy(),
             nc=0, nw=0)
    o = P4.wear(S, hw); return o, S


def pose_state(B, M):
    mm = [None if B.res[j] is None else float(np.min(B.res[j])) for j in range(len(B.idx))]
    return mm, [str(w) for w in np.asarray(M.why)]


# ---------------------------------------------------------------- the IK flood (kinematic) --------------------------------
def gate_vals(M, Q):
    """AA.gate's lead gates + the joint columns the continuity rule reads (q1, q2, q3', dK, qa, qb, kstate)"""
    D = M.D; P = M.p
    q, ok, X1, X2, X3, s = D.ik(Q); K = D.knee(s)
    ok = ok & K["ok"] & (np.abs(s[:, 2]) <= P["R_tol"])
    q3p = AA.wr(np.degrees(q[:, 2] + K["phi"])); lo, hi = float(P.get("J3MIN", -105)), float(P.get("J3MAX", 999))
    ok &= (q3p >= lo) & ((q3p <= hi) if hi < 180 else True)
    c = (np.einsum("nij,nij->n", X3[0], Q) - 1) / 2; ok &= np.degrees(np.arccos(np.clip(c, -1, 1))) < 0.5
    g = getattr(M, "_scg", None); dK = getattr(D, "_dK", None)
    if g is not None and "dK_lim" in g and dK is not None and len(dK) == len(Q):
        ok &= np.abs(np.asarray(dK, float)) <= float(g["dK_lim"]) + 1e-9
    act = np.c_[np.degrees(q[:, 0]), np.degrees(q[:, 1]), q3p]
    pas = [np.degrees(np.asarray(dK, float))] if dK is not None and len(dK) == len(Q) else []
    for k in ("qa", "qb"):
        if k in K: pas.append(np.degrees(np.asarray(K[k], float)))
    pas = np.stack(pas, 1) if pas else np.zeros((len(Q), 0))
    st = np.asarray(getattr(D, "_state", np.zeros(len(Q))), float).copy()
    return ok, act, pas, st


def _jump_ok(a0, p0, a1, p1, pj=10.0, aj=25.0):
    if p0.size and float(np.abs(AA.wr(p1 - p0)).max()) > pj: return False
    return float(np.abs(AA.wr(a1 - a0)).max()) <= aj


def ik_flood(F, step_deg=2.0, pj=10.0, aj=25.0, dkmax=10.0):
    """the IK continuity flood (module docstring); cached per PHI / axis in VDIR"""
    rp = F["rp"]; key = f"ikflood_PHI{float(rp['PHI']):g}_t{float(rp['tilt']):g}_a{float(rp['taz']):g}_k{KSTEP:g}.json"; path = os.path.join(VDIR, key)
    lock = path + ".running"
    while os.path.exists(lock) and not os.path.exists(path): time.sleep(10)      # another process is building it
    if os.path.exists(path): return json.load(open(path))
    open(lock, "w").write(str(os.getpid()))
    from scipy.spatial.transform import Rotation as Rot, Slerp
    t0 = time.time(); Z0 = AA.Z0; ax = F["ax"]; M = F["M1"]; KS = kgrid(float(rp["PHI"])); nk = len(KS)
    names = list(Z0["NAMES"]); allw = np.nonzero(Z0["CID"] == names.index("Workspace (envelope)"))[0]
    Ha = Z0["HG"][allw].astype(float); Pz = Z0["POSE"][allw]; n = len(allw)
    R = [AA.rotm(ax, np.full(1, k * D2R))[0] for k in KS]

    def table(H):
        okk = np.zeros((len(H), nk), bool); A = np.zeros((len(H), nk, 3)); Pp = None; St = np.zeros((len(H), nk))
        for c, Rk in enumerate(R):
            ok, act, pas, st = gate_vals(M, H @ Rk); okk[:, c] = ok; A[:, c] = act; St[:, c] = st
            if Pp is None: Pp = np.zeros((len(H), nk, pas.shape[1]))
            Pp[:, c] = pas
        return okk, A, Pp, St
    okN, AN, PN, SN = table(Ha)
    # node states: contiguous feasible-k runs, each 2.5-deg self-motion step jump-checked
    run_of = -np.ones((n, nk), int); runs = []
    for a in range(n):
        c = 0
        while c < nk:
            if not okN[a, c]: c += 1; continue
            r0 = c
            while c + 1 < nk and okN[a, c + 1] and _jump_ok(AN[a, c], PN[a, c], AN[a, c + 1], PN[a, c + 1], pj, aj): c += 1
            rid = len(runs); runs.append((a, r0, c)); run_of[a, r0:c + 1] = rid; c += 1
    keyf = {tuple(np.round(Pz[k, :3], 1)): k for k in range(n) if okN[k].any()}
    valsf = [sorted(set(np.round(Pz[:, d], 1))) for d in range(3)]
    edges = []
    for a in keyf.values():
        x = tuple(np.round(Pz[a, :3], 1))
        for d in range(3):
            j = valsf[d].index(x[d])
            for jj in (j - 1, j + 1):
                if 0 <= jj < len(valsf[d]):
                    y = list(x); y[d] = valsf[d][jj]; b = keyf.get(tuple(y))
                    if b is not None and a < b: edges.append((a, b))
    segs = []; Hs_all = []; off = 0
    for a, b in edges:
        R2 = Rot.from_matrix(np.stack([Ha[a], Ha[b]])); ang = np.degrees((R2[0].inv() * R2[1]).magnitude())
        m = max(2, int(math.ceil(ang / step_deg)) + 1); Hs = Slerp([0, 1], R2)(np.linspace(0, 1, m)).as_matrix()
        segs.append((off, m)); Hs_all.append(Hs); off += m
    H = np.concatenate(Hs_all); okE, AE, PE, SE = table(H)
    print(json.dumps(dict(flood_tables=True, nodes=n, edges=len(edges), frames=len(H), secs=round(time.time() - t0, 1))), flush=True)
    KA = np.array(KS)

    def greedy(o, m, c0, rev):
        fr = list(range(o, o + m)); fr = fr[::-1] if rev else fr
        if not okE[fr[0], c0]: return None
        c = c0
        for f0, f1 in zip(fr[:-1], fr[1:]):
            cand = np.nonzero(okE[f1])[0]
            if not len(cand): return None
            dd = np.abs(KA[cand] - KA[c]); c1 = int(cand[np.argmin(dd + 1e-6 * KA[cand])])
            if abs(KS[c1] - KS[c]) > dkmax + 1e-9 or not _jump_ok(AE[f0, c], PE[f0, c], AE[f1, c1], PE[f1, c1], pj, aj): return None
            c = c1
        return c
    adj = {}                                                           # run id -> set of run ids
    why = dict(open=0, ok=0)
    for e, ((a, b), (o, m)) in enumerate(zip(edges, segs)):
        for (u, v, rev) in ((a, b, False), (b, a, True)):
            for (uu, r0, r1) in [runs[r] for r in sorted(set(run_of[u][run_of[u] >= 0].tolist()))]:
                rid = int(run_of[u, r0]); hit = False
                for c0 in range(r0, r1 + 1):                      # any start inside the run (self-motion), every end run
                    cend = greedy(o, m, c0, rev)
                    if cend is None or run_of[v, cend] < 0: continue
                    adj.setdefault(rid, set()).add(int(run_of[v, cend])); hit = True
                why["ok" if hit else "open"] += 1
    # seeds: the verified convention (AA.flood_relay, the lead's / phi40's floods): every k = 0 node in the lead's state A;
    # the spec's 'state A at elev 0' set is EMPTY (all 171 elev-0 nodes close at k = 0 but none in state A: the hanging arm
    # sits outside the stop-A window), so the second reading seeds every k = 0 node at elev 0 in any state
    el = np.round(Pz[:, 1], 1); seeds = [int(run_of[a, 0]) for a in range(n) if okN[a, 0] and SN[a, 0] == 0]
    seeds_any = [int(run_of[a, 0]) for a in range(n) if okN[a, 0] and el[a] == el.min()]

    def flood(sd):
        reached = set(sd); front = list(sd)
        while front:
            nx = []
            for r in front:
                for r2 in adj.get(r, ()):
                    if r2 not in reached: reached.add(r2); nx.append(r2)
            front = nx
        return reached
    rch = flood(seeds); rch_any = flood(seeds_any)
    node_k = {}
    for a in range(n):
        ks = [KS[c] for c in range(nk) if run_of[a, c] >= 0 and int(run_of[a, c]) in rch]
        ks_any = [KS[c] for c in range(nk) if run_of[a, c] >= 0 and int(run_of[a, c]) in rch_any]
        node_k[str(int(allw[a]))] = dict(feas=[KS[c] for c in range(nk) if okN[a, c]], conn=ks, conn_elev0=ks_any, elev=float(Pz[a, 1]))
    st = dict(nodes=n, feasible_nodes=int(okN.any(1).sum()), feasible_k0=int(okN[:, 0].sum()), runs=len(runs), edges=len(edges),
              seeds_stateA_k0=len(seeds), seeds_elev0_k0=len(seeds_any), nodes_conn=int(sum(1 for v in node_k.values() if v["conn"])),
              nodes_conn_elev0=int(sum(1 for v in node_k.values() if v["conn_elev0"])),
              relayed_only_nodes=int(sum(1 for v in node_k.values() if v["feas"] and 0.0 not in v["feas"])),
              relayed_only_conn=int(sum(1 for v in node_k.values() if v["feas"] and 0.0 not in v["feas"] and v["conn"])), edge_dirs=why, secs=round(time.time() - t0, 1),
              rule=dict(step_deg=step_deg, passive_jump=pj, active_jump=aj, dk_max=dkmax, kstep=KSTEP))
    out = dict(stats=st, nodes=node_k, rp={k: rp[k] for k in ("PHI", "tilt", "taz", "sgn")}); json.dump(out, open(path, "w"))
    if os.path.exists(lock): os.remove(lock)
    return out


# ---------------------------------------------------------------- the IK wear ------------------------------------------------
def ik_run(base, which, outp, ks=None, choice_from=None):
    t0 = time.time(); F = fit(base); hw = dict(base); KS = ks or kgrid(float(F["rp"]["PHI"]))
    print(json.dumps(dict(fit=F["fit"], axis=np.round(F["ax"], 4).tolist(), ks=KS)), flush=True)
    os.environ["CB_EXACT"] = "1"
    Bf = AA.held_bench() if which in ("held", "heldws") else CB.Bench(110, 360)
    if which == "heldws":                                   # every held ws pose + every 100th held clip frame (in-band / follow: a sample)
        kd = np.array(Bf.kind); Bf = subbench(Bf, np.r_[np.nonzero(kd == "clip")[0][::100], np.nonzero(kd == "ws")[0]])
    elif which != "held": Bf = subbench(Bf, np.arange(len(Bf.idx)))          # unbounded skin / distance caches (470 poses fit in RAM)
    nZ = len(AA.Z0["HG"]); kind = np.array(Bf.kind); ws = kind == "ws"
    if choice_from:                                         # RECHOOSE: a previous run's k-table choice, re-read under RULE (final wear only)
        prev = json.load(open(choice_from)); choice = {}
        for j, c in prev["ik"]["choice"].items():
            c = dict(c)
            if RULE == "take-only" and c["k"] != 0 and not c["takes"]: c.update(k=0.0, mm=None, reverted=True)
            choice[int(j)] = c
        o0 = dict(prev["ik"]["k0"]["summary"]); tk0 = np.array([bool(ws[j]) and (j not in choice) for j in range(len(Bf.idx))])   # k = 0 takes = ws poses the IK never had to move
        k0sum = prev["ik"]["k0"]
    else: choice = None
    if choice is None:
      # k = 0: the whole bench (the lead with the ring hardware parked at psi 0)
      o0, S0 = wear_phi(F, Bf, np.zeros(nZ), hw); mm0, why0 = pose_state(Bf, S0["M"])
      tk0 = np.array([m is not None and m >= 0 for m in mm0])
      print(json.dumps(dict(k=0.0, summary=P4.summary(o0), secs=round(time.time() - t0, 1)), default=float), flush=True)
      need = np.nonzero(ws & ~tk0)[0]; cl = np.nonzero(~ws)[0]; sel = np.r_[cl[::max(1, len(cl) // 6)][:6], need]
      Bs = subbench(Bf, sel); tab = {0.0: dict(mm=[mm0[j] for j in sel], why=[why0[j] for j in sel])}
      for k in KS[1:]:
          t1 = time.time(); phi = np.zeros(nZ); phi[Bf.idx[need]] = k
          ok_, Sk = wear_phi(F, Bs, phi, hw); mm, wy = pose_state(Bs, Sk["M"]); tab[k] = dict(mm=mm, why=wy)
          print(json.dumps(dict(k=k, taken_new=int(sum(1 for jj, j in enumerate(sel) if ws[j] and mm[jj] is not None and mm[jj] >= 0)),
                                secs=round(time.time() - t1, 1))), flush=True)
      # the IK: lead-first, max min metal among takes (ties -> smaller k); else the least-deep closing k (a contact); else 0
      choice = {}
      for jj, j in enumerate(sel):
          if not ws[j]: continue
          tks = [(tab[k]["mm"][jj], k) for k in KS if tab[k]["mm"][jj] is not None and tab[k]["mm"][jj] >= 0]
          cls = [(tab[k]["mm"][jj], k) for k in KS if tab[k]["mm"][jj] is not None]
          if tks: m, k = max(tks, key=lambda x: (round(x[0], 6), -x[1]))
          elif cls and RULE == "closest-contact": m, k = max(cls, key=lambda x: (round(x[0], 6), -x[1]))   # (first run's rule: closes 9 lost poses in contact)
          else: m, k = tab[0.0]["mm"][jj], 0.0                 # the spec: no take at any k -> psi stays 0 (the pose's k = 0 state, the lead's own)
          choice[int(j)] = dict(k=k, mm=m, n_take_k=len(tks), takes={str(kk): round(mv, 2) for mv, kk in tks})
    phiF = np.zeros(nZ)
    for j, c in choice.items(): phiF[Bf.idx[j]] = c["k"]
    # continuity: the IK flood (bench ws poses are envelope-grid nodes; held ws too)
    FL = ik_flood(F); nodes = FL["nodes"]; cmap = {}
    for j in np.nonzero(ws)[0]:
        g = str(int(Bf.idx[j])); kk = float(phiF[Bf.idx[j]]); nd = nodes.get(g)
        cmap[int(g)] = bool(nd is not None and any(abs(kk - x) < 1e-6 for x in nd["conn"]))
    o, S = wear_phi(F, Bf, phiF, hw, cmap=cmap)
    try: o["th_margin"] = BV.th_margin(S["M"], S["B"])
    except Exception as ex: o["th_margin"] = dict(err=repr(ex)[:200])
    B = S["B"]; el = np.array([p["elev"] for p in B.poses]); mmF = [None if B.res[j] is None else float(np.min(B.res[j])) for j in range(len(B.idx))]
    tkF = np.array([m is not None and m >= 0 for m in mmF]); new = [j for j in range(len(B.idx)) if ws[j] and tkF[j] and not tk0[j]]
    nm = np.array([mmF[j] for j in new]) if new else np.zeros(0)
    hist = {}
    for j in new: hist[str(phiF[B.idx[j]])] = hist.get(str(phiF[B.idx[j]]), 0) + 1
    o["ik"] = dict(which=which, ks=KS, rule=RULE, rechoose_from=choice_from,
                   k0=(k0sum if choice_from else dict(summary=P4.summary(o0), ws_taken=int((ws & tk0).sum()), overhead=int((ws & tk0 & (el >= 140)).sum()),
                                             mid=int((ws & tk0 & (el >= 90) & (el < 140)).sum()))),
                   static_ws_taken=o["continuity"]["static"] if o.get("continuity") else None,
                   new_takes=len(new), new_overhead=int(sum(1 for j in new if el[j] >= 140)), new_mid=int(sum(1 for j in new if 90 <= el[j] < 140)),
                   new_under1=int((nm < 1).sum()), new_1to2=int(((nm >= 1) & (nm < 2)).sum()), new_median=round(float(np.median(nm)), 2) if len(nm) else None,
                   new_overhead_under2=int(sum(1 for j in new if el[j] >= 140 and mmF[j] < 2)),
                   k_hist_new=hist, overhead=[int((ws & tkF & (el >= 140)).sum()), int((ws & (el >= 140)).sum())],
                   mid=[int((ws & tkF & (el >= 90) & (el < 140)).sum()), int((ws & (el >= 90) & (el < 140)).sum())],
                   new_list=[dict(i=int(j), g=int(B.idx[j]), pose=[B.poses[j][q] for q in ("plane", "elev", "axial")], k=float(phiF[B.idx[j]]),
                                  mm=round(mmF[j], 2), parts=OS.PARTS.get(j)) for j in new],
                   choice={str(j): c for j, c in choice.items()}, flood=FL["stats"],
                   mismatch=[int(j) for j in choice if (choice[j]["mm"] is not None and choice[j]["mm"] >= 0) != bool(tkF[j]) and cmap.get(int(B.idx[j]), True)],
                   secs=round(time.time() - t0, 1))
    print(json.dumps(dict(final=P4.summary(o), ik={k: v for k, v in o["ik"].items() if k not in ("choice", "new_list")}, th=o.get("th_margin")), default=float), flush=True)
    json.dump(o, open(outp, "w"), default=float)
    pp = P4.perpose(S); pp.update(id=ID, wear=which, params=base, exact=True, ik=True)
    json.dump(pp, open(outp.replace(".json", "_perpose.json"), "w"), default=float)
    return o


def control(base, outp):
    """the unpowered control: phi40's least-phi relay at the same axis / hardware (coil deleted), Bench(110,360) exact"""
    os.environ["CB_EXACT"] = "1"; b = dict(base, flood=1); S = P4.prepare(b, 110, 360, exact=True); o = P4.wear(S, b)
    try: o["th_margin"] = BV.th_margin(S["M"], S["B"])
    except Exception as ex: o["th_margin"] = dict(err=repr(ex)[:200])
    print(json.dumps(dict(control=P4.summary(o), th=o.get("th_margin")), default=float), flush=True); json.dump(o, open(outp, "w"), default=float)
    return o


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "help"
    par = dict(CLAIM, **(json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}))
    if mode == "flood": F = fit(par); print(json.dumps(ik_flood(F)["stats"])); sys.exit(0)
    if mode == "ik": ik_run(par, sys.argv[3], sys.argv[4]); sys.exit(0)
    if mode == "rechoose": ik_run(par, sys.argv[3], sys.argv[4], choice_from=sys.argv[5]); sys.exit(0)   # rechoose '<json>' bench out.json prev_ik.json
    if mode == "control": control(par, sys.argv[3]); sys.exit(0)
    print(__doc__)
