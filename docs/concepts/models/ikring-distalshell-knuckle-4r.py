"""ikring-distalshell-knuckle-4r (round 301, O1 track overhead, lens rocker-redundant-4r, judge pick 3): the verified lead
conecut-knee-knuckle-3r with its long knee (lE 97: E strap / boss / knee link down to s ~134 in the humerus frame) replaced
by a SHORT knee re-centred on the lead's fit (every mover above the shell band), plus an ACTIVE one-sided J4 ring about a
GH-through axis (tilt 8.5 toward taz 243) built as a slotted circular Ti shell DISTAL of every mover (ds < 0: the shell
centre lies distal of the pad; nothing passes over the shell band, so NO E bump and NO knee lift), T-nut carriage, L-lug
bracket up to the pad at the pad's own fitted level.

Machinery: ikring-thinstack-knuckle-4r (pick 1) is imported READ-ONLY: its k-table, lead-first take-only proximity IK, the
1432-grid IK continuity flood and the single final wear are pick 1's code. This file changes only:

  * fit(): the lead fit (Bench(60,160) fast, k = 0) with the knee keys (lE, lc, phiE, phib, ang_min) overridable;
  * NO BUMP: PT.bump_amounts returns zero amounts (the spec: nothing passes over the shell band). The jam rule in
    PT.rerecord still runs (shell / carriage / bracket within 1 mm of the knee link, E strap, boss, hub 3, link 2, pad
    -> the pose is lost; metal in the skin stays a contact), so a mover that does reach the shell is never free;
  * a private verify dir (the IK flood is re-built: the knee changes the lead's kinematic gates).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/ikring-distalshell-knuckle-4r.py fit '<json>'       # Bench(60,160) fast, psi 0, chain only
    CB_EXACT=1 ... chain '<json>' out.json      # Bench(110,360) exact frozen, psi 0, chain only (step-1 kill test)
    CB_EXACT=1 ... k0 '<json>' out.json         # the same with the ring hardware parked at psi 0 (step-2 shell read)
    CB_EXACT=1 ... ik '<json>' bench out.json   # pick 1's k-table + IK + flood + final wear (claim bench)
    CB_EXACT=1 ... ik '<json>' heldws out.json  # held ws (report only)
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
_sp = importlib.util.spec_from_file_location("ikring_for_distal", os.path.join(HERE, "ikring-thinstack-knuckle-4r.py"))
IK = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(IK)
P4, OS, PT, BV, AA, CB, CC = IK.P4, IK.OS, IK.PT, IK.BV, IK.AA, IK.CB, IK.CC
ID = "ikring-distalshell-knuckle-4r"
VDIR = os.path.join(REPO, "docs", "concepts", "verify", ID); os.makedirs(VDIR, exist_ok=True)
IK.VDIR = VDIR; PT.VDIR = VDIR; OS.VDIR = VDIR; P4.VDIR = VDIR
KNEE_KEYS = ("lE", "lc", "phiE", "phib", "ang_min")
# best short knee of the re-centre sweep (Bench(60,160) fast, psi 0; set by the sweep) and the distal shell cell
KNEE = dict(lE=69.52, lc=18.63, phiE=-5.44, phib=-80.96, ang_min=25.64)
CLAIM = dict(IK.CLAIM); CLAIM.update(KNEE); CLAIM.update(ds=-24.0, delta=12.0, bump=1.0, band=8.0)
LEAD = dict(AA.LEAD)


def fit(base):
    """pick 1's fit with the knee keys overridable (pick 1's dict(**AA.LEAD, **base) cannot take them)"""
    rp = dict(PT.DEF); rp.update({k: base[k] for k in PT.DEF if k in base})
    P = CC._clamp(dict(CC.PARAMS, **{**LEAD, **{k: v for k, v in base.items() if k not in PT.DEF}}))
    old = os.environ.pop("CB_EXACT", None)
    try:
        B1 = CB.Bench(n_clip=60, n_ws=160); M1 = CC.CCModel(B1, dict(P)); r1 = M1.run()
        fitr = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    ax = AA.raxis(rp["tilt"], rp["taz"]); P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(CC.CCModel):
        def fit(self):
            for a in IK.ATTR:
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self._sc = None; self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]
            self.drop = np.zeros(len(self.poses_fit), bool); self._truncate()
    return dict(rp=rp, M1=M1, B1=B1, P2=P2, ax=ax, fit=fitr, Frozen=Frozen)


IK.fit = fit


def nobump(M1, G, ax):
    """distal shell: no member is bumped (zero amounts); the jam rule stays the guard"""
    G["ramp"] = float(G.get("ramp_req", 6.0)); G["ramp_floor"] = 2.0
    out = {}
    for nm, (m, X) in M1.rigid.items():
        if m in PT.BUMP_MEMBERS: out[("rigid", nm)] = np.zeros(len(X))
    for nm, (m, X) in M1.link_pts.items():
        if m in PT.BUMP_MEMBERS: out[("link", nm)] = np.zeros(len(X))
    return out


PT.bump_amounts = nobump


def stations(M, B, names=("E", "boss", "knee", "pad", "hub3")):
    """humerus-frame station s = -y (mm down the arm from GH) of each mover over the taken poses: [min, max]"""
    tk = np.nonzero(M.kin_ok)[0]; out = {}
    for nm in names:
        src = M.rigid if nm in M.rigid else M.link_pts
        if nm not in src: continue
        m, X = src[nm]
        if not len(X): continue
        s = np.concatenate([-((M.world(m, j, X) @ M.RS[j]) @ M.Q[j])[:, 1] for j in tk[::2]])
        out[nm] = [round(float(s.min()), 1), round(float(s.max()), 1)]
    return out


def chain(base, outp, hw=False):
    """Bench(110,360) exact frozen at psi 0: chain only (hw False) or with the ring hardware parked (hw True)"""
    t0 = time.time(); F = fit(base); os.environ["CB_EXACT"] = "1"
    Bf = CB.Bench(110, 360); Bf = IK.subbench(Bf, np.arange(len(Bf.idx)))
    if hw:
        o, S = IK.wear_phi(F, Bf, np.zeros(len(AA.Z0["HG"])), dict(base)); M = S["M"]; B = S["B"]; r = o["wear"]
    else:
        M = F["Frozen"](Bf, F["P2"]); r = M.run(); B = Bf; o = {}
    ws = np.array(B.kind) == "ws"; el = np.array([p["elev"] for p in B.poses])
    mm = [None if B.res[j] is None else float(np.min(B.res[j])) for j in range(len(B.idx))]
    tk = np.array([m is not None and m >= 0 for m in mm]); why = np.asarray(M.why).astype(str)
    e = dict(params=base, fit=F["fit"], exact={k: round(float(r[k]), 4) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")},
             ws_taken=int((ws & tk).sum()), overhead=int((ws & tk & (el >= 140)).sum()), mid=int((ws & tk & (el >= 90) & (el < 140)).sum()),
             contacts=[[int(j)] + [B.poses[j][q] for q in ("plane", "elev", "axial")] + [round(mm[j], 2)] for j in range(len(mm)) if mm[j] is not None and mm[j] < 0],
             taken=[int(j) for j in np.nonzero(ws & tk)[0]], why={w: int(((why == w) & ws).sum()) for w in set(why[ws].tolist())},
             stations_fit=stations(F["M1"], F["B1"]), secs=round(time.time() - t0, 1))
    if hw: e["ring"] = {k: o[k] for k in ("gate_gap", "chain_only_gap", "near1_gap", "near2_gap", "relay_hw", "hw") if k in o}
    try: e["th"] = BV.th_margin(M, B)
    except Exception as ex: e["th"] = repr(ex)[:200]
    json.dump(e, open(outp, "w"), default=float); print(json.dumps({k: v for k, v in e.items() if k != "taken"}, default=float), flush=True)
    return e


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "help"
    par = dict(CLAIM, **(json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}))
    if mode == "fit":
        F = fit(par); print(json.dumps(dict(fit=F["fit"], stations=stations(F["M1"], F["B1"])))); sys.exit(0)
    if mode == "chain": chain(par, sys.argv[3]); sys.exit(0)
    if mode == "k0": chain(par, sys.argv[3], hw=True); sys.exit(0)
    if mode == "ik": IK.ik_run(par, sys.argv[3], sys.argv[4]); sys.exit(0)
    print(__doc__)
