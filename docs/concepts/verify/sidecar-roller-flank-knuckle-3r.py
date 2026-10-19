"""Independent verifier (skeptic) of sidecar-roller-flank-knuckle-3r (the lead's slaved knuckle with a rodless sidecar:
hub-2 rim lobe -> bell crank on link 1b -> bent 130-deg arm -> MR63 roller -> conjugate flank on a spherical-shell horn lug
of link 1a at hub K).

The claim's model (docs/concepts/models/sidecar-roller-flank-knuckle-3r.py, on the shared core sidecar-longdyad-knuckle-3r.py)
is loaded UNCHANGED (law, clamps, pin knee, stops, the drive-range truncation and every claimed check stay). The protocol is
the claim's frozen one (fit on Bench(60,160) fast, shape frozen, worn on Bench(110,360) exact), reproduced here so the worn
model is in hand. Checks ADDED by this harness on every TAKEN pose of the worn bench (not in the claim):

  1. CAM CLOSURE IN THE WORLD: the roller centre carried by the crank (member 9, T9 C0) must sit on the synthesised
     roller-centre path of link 1a's flank (member 1, T1 P1(|dK|)) within 0.5 mm, i.e. the model's per-pose K sense matches
     the sense the flank was cut for (the drive uses |dK|: a pose whose K opened the other way would leave the roller
     off the flank or inside the lug).
  2. ROLLER vs LUG IN THE WORLD: min distance from the roller centre to the lug's mid-shell metal >= ROLL_R (no
     interpenetration), and |dK| <= dK_lim (the flank exists there: K determined, not left to the spring stop).
  3. K SENSE: count of taken poses with dK opposite to the sense the drive pushes (sp); the roller can only push.
  4. PRESSURE ANGLES AT THE POSE: the claim's per-0.25-deg table (crank, horn) read at each taken pose's |dK| <= 45.
  5. REAL LOBE PRESSURE ANGLE: atan(s_arm |dphi/d|dK|| kK / r) with the exact phi law over the taken range <= 45.
  6. DRIVE IDLE RULE: the drive must carry >= 30 deg of K on the worn bench.
  7. CONTINUITY FLOOD FILL (connected_report of docs/concepts/verify/minarc-stop-knuckle-4r-mechanism.py, unchanged).
Optional --head (envelope correction, add_envelope): the roller pin's retaining head and the lug's flank-edge strip that
the claim's sampling deletes, added to the metal and contact sets.

    CB_EXACT=1 python3 docs/concepts/verify/sidecar-roller-flank-knuckle-3r.py wear <bench|held> <out.json> [--flood] [--head]
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


RF = _load("roller_flank_claim_v", os.path.join(REPO, "docs", "concepts", "models", "sidecar-roller-flank-knuckle-3r.py"))
SC, S, PK = RF.SC, RF.S, RF.PK
unit = S.unit
BEST = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "sidecar-roller-flank-knuckle-3r.json")))["best_params"]
if isinstance(BEST, str): BEST = json.loads(BEST)
PA_MAX, CLOSE_TOL, ROLL_R = 45.0, 0.5, RF.ROLL_R
HEAD_R, HEAD_T = 2.5, 0.8


def flank_path(M):
    """roller-centre path in link 1a's frame over the drive's own range [0, dK_lim] (the model's Rk, Rcg, C0)"""
    g = M._scg; PV, dR, uK, sp, sig, gg, cc = g["PV"], g["dR"], g["uK"], g["sp"], g["sig"], g["g"], g.get("c", 0.0)
    C0 = np.asarray(M._viz_rod["roller"], float); kg = np.arange(0.0, g["dK_lim"] + 1e-9, math.radians(0.25))
    Rc = S.rotm(dR, sig * RF.phi_of(kg, gg, cc)); Cb = np.einsum("nij,j->ni", Rc, C0 - PV) + PV
    return np.einsum("nij,nj->ni", S.rotm(uK, sp * kg), Cb)


def add_envelope(M):
    """real envelope the claim's sampling misses:
    (a) the roller pin's retaining head under the roller (member 9): O5 x 0.8 below the MR63's underside;
    (b) the lug's flank edge strip: the claim projects the 0.3-mm-behind-flank row onto the shell, which shrinks its
        chord to the roller centre below ROLL_R + 0.3, so the whole row is deleted and the sampled lug starts 1-2 mm
        behind the flank. Re-add the underside at 3.1 mm from the roller-centre path (on the lug's side)."""
    C0 = np.asarray(M._viz_rod["roller"], float); cr = unit(C0); e, f = S.frame_of(cr)
    dd = S.disc(HEAD_R, 1.5); c = C0 - (1.25 + HEAD_T) * cr
    head = c + dd[:, :1] * e + dd[:, 1:] * f
    m, X = M.rigid["roller"]; M.rigid["roller"] = (m, np.concatenate([X, head]))
    M.contact.append((9, np.concatenate([head, RF._ring(c, HEAD_R, cr)])))
    Pp = flank_path(M); R0 = float(np.linalg.norm(C0)); rL = R0 - 1.5
    m1, lug = M.rigid["horn"]; mid = lug + 1.5 * unit(lug); d, j = cKDTree(Pp).query(mid)
    sel = d < ROLL_R + 2.6                                              # the first sampled row behind the flank
    E = Pp[j[sel]] + 3.1 * unit(mid[sel] - Pp[j[sel]])
    E = E[cKDTree(Pp).query(E)[0] >= ROLL_R + 0.05]
    edge = unit(E) * rL
    M.rigid["horn"] = (m1, np.concatenate([lug, edge]))
    M.contact.append((1, edge + S.T_LINK * unit(edge)))
    M._env_info = dict(head_pts=len(head), edge_pts=len(edge))


def extra_checks(M, Mfit, B):
    g = M._scg; tab = Mfit._cam_table; P = M.D.p
    PV, dR, uK, sp, sig, gg, cc = g["PV"], g["dR"], g["uK"], g["sp"], g["sig"], g["g"], g.get("c", 0.0)
    C0 = np.asarray(M._viz_rod["roller"], float); lugM = g["lugM"]
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    dK = np.asarray(M.dK, float)
    ec, dl, pac, pah, bad, why = [], [], [], [], [], {}
    for i in taken:
        k = abs(float(dK[i])); ph = sig * float(RF.phi_of(k, gg, cc))
        R1, t1 = M.T(1, i); R9, t9 = M.T(9, i)
        Cw = R9 @ C0 + t9
        Cb = S.rotm(dR, ph)[0] @ (C0 - PV) + PV                       # link 1b frame
        Ca = S.rotm(uK, sp * k)[0] @ Cb                               # link 1a frame (the model's Rk)
        Cexp = R1 @ Ca + t1
        e = float(np.linalg.norm(Cw - Cexp)); ec.append(e)
        Lw = lugM @ R1.T + t1; d = float(cKDTree(Lw).query(Cw)[0]); dl.append(d)
        a = float(np.interp(math.degrees(k), tab["k"], tab["pa_crank"])); h = float(np.interp(math.degrees(k), tab["k"], tab["pa_horn"]))
        pac.append(a); pah.append(h)
        rs = []
        if e > CLOSE_TOL: rs.append("closure")
        if d < ROLL_R - 1e-6: rs.append("roller_in_lug")
        if k > float(g["dK_lim"]) + 1e-9: rs.append("beyond_flank")
        if a > PA_MAX or h > PA_MAX: rs.append("pressure")
        if rs:
            bad.append(i)
            for r_ in rs: why[r_] = why.get(r_, 0) + 1
    tk = np.array(taken, int)
    wrong_sense = int(np.sum((np.abs(dK[tk]) > math.radians(0.1)) & (np.sign(dK[tk]) != sp))) if len(tk) else 0
    # real lobe pressure angle over the taken range
    kmax = float(np.abs(dK[tk]).max()) if len(tk) else 0.0
    kg = np.linspace(0.0, kmax, 200); kK = float(P.get("kA", P.get("kK", 0.0))); s_arm = float(P["s_arm"]); rl0 = float(P["r_lobe"])
    r_t = rl0 + s_arm * RF.phi_of(kg, gg, cc); pa_l = np.degrees(np.arctan(s_arm * RF.dphi_of(kg, gg, cc) * kK / r_t))
    out = dict(n_taken=len(taken), closure_max_mm=round(max(ec), 4) if ec else None, roller_lug_min_mm=round(min(dl), 3) if dl else None,
               roller_lug_max_mm=round(max(dl), 3) if dl else None, pa_crank_max=round(max(pac), 1) if pac else None,
               pa_horn_max=round(max(pah), 1) if pah else None, wrong_sense=wrong_sense, sp=float(sp),
               dK_sign_counts=dict(pos=int(np.sum(dK[tk] > 1e-6)), neg=int(np.sum(dK[tk] < -1e-6)), zero=int(np.sum(np.abs(dK[tk]) <= 1e-6))),
               poses_failing=len(bad), why_failing=why, poses_failing_ids=bad[:50], pa_lobe_real_max=round(float(pa_l.max()), 2),
               dK_taken_max_deg=round(math.degrees(kmax), 2), dK_lim_deg=round(math.degrees(g.get("dK_lim", 0.0)), 2), why_lim=g.get("why_lim"),
               drive_idle=bool(math.degrees(kmax) < 30.0))
    res0 = list(B.res)
    for i in bad: B.res[i] = None
    out["corrected"] = {k: B.report()[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    B.res = res0
    return out


def frozen_wear(P, wear="bench", flood=False, head=False):
    P = RF._clamp(dict(RF.PARAMS, **P))
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    M1 = RF.RFModel(B1, dict(P))
    if head:
        orig = M1._rod_metal
        def _rm():
            orig(); add_envelope(M1)
        M1._rod_metal = _rm
    r1 = M1.run(); fit = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    fit["extra"] = extra_checks(M1, M1, B1)
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(RF.RFModel):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info", "_cam_table"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self._sc = None
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
            self._truncate()
    if wear == "held":
        PV = _load("pk_polish_v_rollerflank_v", os.path.join(HERE, "skin-normal-3r-pin-knee-polish.py")); B = PV.held_bench()
    else:
        B = CB.Bench(n_clip=110, n_ws=360)
    M = Frozen(B, P2); r = M.run()
    rep = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    aud = PK.audit(M, B)
    ex = extra_checks(M, M1, B)
    out = dict(fit_fast=fit, frozen=rep, mode=B.mode, n=len(B.idx), why=r.get("why"), parts_pairs=r.get("parts_pairs"), parts_ib14=r.get("parts_ib14"),
               audit=aud, extra=ex, sidecar=getattr(M1, "_sc_info", None), min_clear_taken=r.get("min_clear_taken"), head=head,
               env=getattr(M1, "_env_info", None))
    if flood:
        MECH = _load("minarc_mech_for_rollerflank_v", os.path.join(HERE, "minarc-stop-knuckle-4r-mechanism.py"))
        t = time.time(); out["connected"] = MECH.connected_report(M, B); out["connected"]["secs"] = round(time.time() - t, 1)
    return out


if __name__ == "__main__":
    if sys.argv[1] == "wear":
        wear, path = sys.argv[2], sys.argv[3]
        t = time.time(); out = frozen_wear(dict(BEST), wear, "--flood" in sys.argv, "--head" in sys.argv)
        out.update(wear=wear, secs=round(time.time() - t, 1), exact=os.environ.get("CB_EXACT") == "1")
        json.dump(out, open(path, "w"), indent=1, default=float)
        print(json.dumps(dict(wear=wear, head=out["head"], fit=out["fit_fast"], frozen=out["frozen"], near1=out["audit"].get("gap_near1"),
                              near2=out["audit"].get("gap_near2"), minmetal=out["audit"].get("near_touch_min_mm"), ovh=out["audit"].get("overhead140"),
                              why=out["why"], extra=out["extra"], conn=out.get("connected"), secs=out["secs"]), default=float))
