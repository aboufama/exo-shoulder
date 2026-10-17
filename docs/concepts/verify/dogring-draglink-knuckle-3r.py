"""Independent verifier (skeptic) of dogring-draglink-knuckle-3r (the slipper-nose lead's chain on a 34/46 K dyad, the
lead's lobe / crank / nose deleted; a dog SECTOR on hub 2's skin-face layer pushed by link 2's root flank, an up-joggled
Ti ARM, a spherical DRAG LINK to a HORN on link 1a at hub K).

The claim's model (docs/concepts/models/dogring-draglink-knuckle-3r.py) is loaded UNCHANGED and worn by its own claim
protocol (LS._frozen_model: fit Bench(60,160) fast -> shape frozen -> worn on Bench(110,360) exact / held out). No other
model is imported in this process (the parents patch shared core modules).

What the verifier found and adds:

  0. RING-L2 RE-INSTATED (--ring). The claim's own sector-vs-link-2 check (DRModel.collide, RING-L2) reads self._dogg /
     self._L2ring, which LS._frozen_model's Frozen.fit does NOT copy from the fitted model, so on every frozen bench
     (the claim's Bench(110,360) and held out) the check silently returns early. With --ring the attributes are carried
     over (stash from the fit model) and the claim's own rule runs inside the worn bench (a failing pose -> 'parts').
  Checks on every TAKEN pose of the worn bench (frames read through M.T, never through the model's own tables):
  1. DOG CLOSURE: link 2's leading edge in the sector layer (the claim's own _L2ring points) vs the sector's lug face, in
     link 1b's frame, push coordinate: K > 0 -> |edge - face| <= 0.5 mm at r 12.5 (the drive loop closes through the
     dog); K = 0 -> edge <= face + 0.5 mm (link 2 is not inside the sector).
  2. DRAG-LINK CLOSURE: the drag link's two pins carried by member 8 vs the arm pin carried by member 9 and the horn pin
     carried by link 1a (member 1) <= 0.5 mm.
  3. ARM ROOT vs LINK 2 (new pair): the claim's per-pose part check uses only the arm points farther than r 14.5 from
     J2's axis (strap CRK = arm_mid[far_root]); the up-joggled arm root (arm_up = 1: underside f2 + 4, i.e. inside link
     2's hub layer f2 + 3.15 .. f2 + 6.15) is never checked against link 2. Here: every arm mid-plane point vs link 2's
     mid-plane strap with the plate rule slab() (stacked OR side by side), >= 0.15 (adjacent through the dog: lenient).
  4. MEMBER 9 vs LINK 1B per pose (the claim checks the sector only on its own K grid at the design stage, and the arm's
     'stacked over link 1b' level is read at the nearest link-1b point to the arm's centreline, so near hub 2 the arm can
     sit level with link 1b's root): sector + arm mid points vs link 1b's strap with slab(), >= 0.15 (adjacent: the
     sector turns on link 1b's hub housing).
  5. FOLD MARGIN (the lead verifier's th_margin, through the claim's LS.th_margin).
Corrected gap: poses failing 1-4 dropped (B.res -> None), the bench re-reported.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/dogring-draglink-knuckle-3r.py wear <bench|held|fit> <out.json> [--ring] [--champ]
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


DR = _load("dogring_claim_v", os.path.join(REPO, "docs", "concepts", "models", "dogring-draglink-knuckle-3r.py"))
LS, S, PK, CB = DR.LS, DR.S, DR.PK, DR.CB
unit = S.unit; D2R = math.pi / 180
ROW = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "dogring-draglink-knuckle-3r.json")))
BEST = ROW["best_params"]; BEST = json.loads(BEST) if isinstance(BEST, str) else BEST
CLOSE_TOL, RUNG = 0.5, 0.15
STASH = {}


def taken_of(B): return [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]


def install_ring_fix():
    orig_rm = DR.DRModel._rod_metal; orig_col = DR.DRModel.collide

    def _rm(self):
        orig_rm(self)
        STASH.update(_dogg=self._dogg, _L2ring=self._L2ring, _ring_mid=self._ring_mid)

    def _col(self, i):
        if getattr(self, "_dogg", None) is None and STASH:
            for k, v in STASH.items(): setattr(self, k, v)
        return orig_col(self, i)
    DR.DRModel._rod_metal = _rm; DR.DRModel.collide = _col


def install_stash_only():
    orig_rm = DR.DRModel._rod_metal

    def _rm(self):
        orig_rm(self)
        STASH.update(_dogg=self._dogg, _L2ring=self._L2ring, _ring_mid=self._ring_mid)
    DR.DRModel._rod_metal = _rm


def _az(X, u2, e2, g2):
    X = np.atleast_2d(X); w = X - (X @ u2)[:, None] * u2; return np.degrees(np.arctan2(w @ g2, w @ e2))


def slab(A, Bp, inset):
    """clearance between two 3-mm plates sampled on their mid-planes (radial levels through GH): for every pair within 8 mm,
    separated if stacked (|radial gap| - T_LINK) or side by side (tangential gap - the two edge-row insets, link straps 1.0,
    arm 0.5 / sector ends 0); clearance = min over pairs of the larger of the two (lenient: a diagonal pair counts its full
    tangential distance)"""
    t = cKDTree(Bp); out = np.full(len(A), 99.0)
    for j, nb in enumerate(t.query_ball_point(A, 8.0)):
        if not nb: continue
        a = A[j]; b = Bp[nb]; ra = np.linalg.norm(a); rb = np.linalg.norm(b, axis=1)
        dr = np.abs(ra - rb) - S.T_LINK; dl = np.linalg.norm(a / ra - b / rb[:, None], axis=1) * 0.5 * (ra + rb) - (1.0 + inset)
        out[j] = float(np.max(np.stack([dr, dl]), 0).min())
    return out


def checks(M, B, taken):
    D = M.D; u1, u2, u3 = D.u; uK = D.uK; e2, g2 = S.frame_of(u2)
    g = STASH["_dogg"]; X2r = STASH["_L2ring"]; secm = STASH["_ring_mid"]
    dg = M._scg["dog"]; s_q = g["s_q"]; psi0 = g["psi0"]; span = g["span"]
    m9, X9 = M.rigid["crank"]; nsec = len(secm); arm = X9[nsec:]
    arm_mid = arm + 1.5 * np.array([unit(x) for x in arm])
    rr_arm = np.linalg.norm(arm_mid - (arm_mid @ u2)[:, None] * u2, axis=1)
    m2, L2s = M.strap["L2"]; m7, L1bs = M.strap["L1b"]
    m8, Xdl = M.rigid["rod"]
    c1_0, c2_0 = dg["c1_0"], dg["c2_0"]; lv_tip = float(np.linalg.norm(M._viz_rod["armB"])); lvK = float(np.linalg.norm(M._viz_rod["horn"]))
    la = float(np.linalg.norm(M._viz_rod["rodA"])); lh = float(np.linalg.norm(M._viz_rod["rodB"]))
    dK = np.asarray(M.dK, float); bad = {}; rows = []
    ref = None
    for i in taken:
        R7, t7 = M.T(7, i); R2, t2 = M.T(2, i); R9, t9 = M.T(9, i); R8, t8 = M.T(8, i); R1, t1 = M.T(1, i)
        k = abs(float(dK[i]))
        push = float(np.interp(k, dg["K"], dg["push"])) if dg["ok"] else 0.0
        # 1. dog closure (link 1b frame, push coordinate)
        Xl = (R7.T @ ((R2 @ X2r.T).T + t2 - t7).T).T
        ps = s_q * _az(Xl, u2, e2, g2)
        if ref is None: ref = psi0
        ps = ref + ((ps - ref + 180) % 360 - 180)
        lead = float(ps.max()); face = psi0 + math.degrees(push)
        res_dog = (lead - face) * D2R * DR.RING_RO
        # 2. drag-link closure (world)
        A9 = R9 @ (c1_0 * lv_tip) + t9; A8 = R8 @ (c1_0 * lv_tip) + t8
        H1 = R1 @ (c2_0 * lvK) + t1; H8 = R8 @ (c2_0 * lvK) + t8
        res_dl = max(float(np.linalg.norm(A9 - A8)), float(np.linalg.norm(H1 - H8)))
        # 3. arm (all mid points incl. the up-joggled root) vs link 2 strap; 4. member 9 vs link 1b strap
        AW = (R9 @ arm_mid.T).T + t9; L2w = (R2 @ L2s.T).T + t2; L1bw = (R7 @ L1bs.T).T + t7; SW = (R9 @ secm.T).T + t9
        dA2 = slab(AW, L2w, 0.5)
        c_arm_l2 = float(dA2.min()); c_root_l2 = float(dA2[rr_arm <= DR.RING_RO + 2.0].min()) if (rr_arm <= DR.RING_RO + 2.0).any() else 99.0
        sA = slab(AW, L1bw, 0.5); sS = slab(SW, L1bw, 0.0); c9_l1b = float(min(sA.min(), sS.min()))
        ja = int(np.argmin(sA)); arm_where = dict(r_u2=round(float(rr_arm[ja]), 2), h_rel_f2=round(float(arm_mid[ja] @ u2) - float(M.f[1]), 2))
        rs = []
        if k > 1e-6 and abs(res_dog) > CLOSE_TOL: rs.append("dog_open")
        if k <= 1e-6 and res_dog > CLOSE_TOL: rs.append("dog_inside")
        if res_dl > CLOSE_TOL: rs.append("draglink_open")
        if c_arm_l2 < RUNG: rs.append("arm_L2")
        if c9_l1b < RUNG: rs.append("m9_L1b")
        if rs: bad[i] = rs
        rows.append(dict(i=i, k=math.degrees(k), res_dog=res_dog, res_dl=res_dl, arm_l2=c_arm_l2, root_l2=c_root_l2, m9_l1b=c9_l1b,
                         arm_l1b=float(sA.min()), sec_l1b=float(sS.min()), arm_where=arm_where))
    if not rows: return bad, dict(n=0)
    A = lambda key: np.array([r[key] for r in rows])
    kk = A("k"); on = kk > 1e-6
    out = dict(n=len(rows), n_K_open=int(on.sum()), psi0=round(psi0, 2), sector_span_deg=round(span, 1), s_q=s_q,
               dog_res_open_mm=[round(float(A("res_dog")[on].min()), 3), round(float(A("res_dog")[on].max()), 3)] if on.any() else None,
               dog_res_rest_max_mm=round(float(A("res_dog")[~on].max()), 3) if (~on).any() else None,
               draglink_res_max_mm=round(float(A("res_dl").max()), 4),
               arm_L2_min_mm=round(float(A("arm_l2").min()), 2), arm_root_L2_min_mm=round(float(A("root_l2").min()), 2),
               arm_L2_lt1=int((A("arm_l2") < 1.0).sum()), arm_L2_lt015=int((A("arm_l2") < RUNG).sum()),
               m9_L1b_min_mm=round(float(A("m9_l1b").min()), 2), m9_L1b_lt015=int((A("m9_l1b") < RUNG).sum()),
               arm_L1b_min_mm=round(float(A("arm_l1b").min()), 2), arm_L1b_lt015=int((A("arm_l1b") < RUNG).sum()), arm_L1b_lt1=int((A("arm_l1b") < 1.0).sum()),
               sec_L1b_min_mm=round(float(A("sec_l1b").min()), 2), sec_L1b_lt015=int((A("sec_l1b") < RUNG).sum()),
               arm_L1b_fail_K_deg=[round(float(A("k")[A("arm_l1b") < RUNG].min()), 1), round(float(A("k")[A("arm_l1b") < RUNG].max()), 1)] if (A("arm_l1b") < RUNG).any() else None,
               arm_L1b_pass_K_max_deg=round(float(A("k")[A("arm_l1b") >= RUNG].max()), 1) if (A("arm_l1b") >= RUNG).any() else None,
               worst_arm_L1b=sorted([(round(r["arm_l1b"], 2), r["i"], round(r["k"], 1), r["arm_where"]) for r in rows], key=lambda x: x[0])[:5],
               worst_arm_L2=sorted([(round(r["arm_l2"], 2), r["i"], round(r["k"], 1)) for r in rows])[:6],
               worst_dog=sorted([(round(r["res_dog"], 2), r["i"], round(r["k"], 1)) for r in rows], reverse=True)[:6])
    return bad, out


def geometry(M):
    """sampling density and part envelope of the drive (for the honesty audit)"""
    m9, X9 = M.rigid["crank"]; nsec = len(STASH["_ring_mid"]); m8, Xdl = M.rigid["rod"]; m1, Xh = M.rigid["horn"]
    def nn(X):
        if len(X) < 2: return None
        d = cKDTree(X).query(X, k=2)[0][:, 1]; return round(float(np.median(d)), 2)
    info = getattr(M, "_sc_info", {}) or {}
    return dict(n_sector=nsec, n_arm=len(X9) - nsec, n_draglink=len(Xdl), n_horn=len(Xh), nn_sector_mm=nn(X9[:nsec]), nn_arm_mm=nn(X9[nsec:]),
                nn_draglink_mm=nn(Xdl), nn_horn_mm=nn(Xh), sc_info={k: info.get(k) for k in ("dK_lim", "why_lim", "sector_span", "arm_beside", "arm_tip_level",
                                                                                         "dl_levels", "horn_level", "r_h", "dl_len", "arm_len", "clear_min", "ring_level_rel_f2")})


def wear(P, which="bench", ring=False):
    if ring: install_ring_fix()
    else: install_stash_only()
    nc, nw = {"bench": (110, 360), "held": (-1, -1), "fit": (60, 160)}[which]
    fit, M1, M, B, r = LS._frozen_model(dict(P), nc, nw)
    rep = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    for k_, v in STASH.items(): setattr(M, "_v_" + k_, v)
    taken = taken_of(B)
    bad, o = checks(M, B, taken)
    why = {}
    for rs in bad.values():
        for x in set(rs): why[x] = why.get(x, 0) + 1
    res0 = list(B.res)
    for i in bad: B.res[i] = None
    corr = {k: B.report()[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    ws = np.array(B.kind) == "ws"; elev = np.array([B.poses[j]["elev"] for j in range(len(B.idx))])
    ok = np.array([B.res[j] is not None and float(np.min(B.res[j])) >= 0 for j in range(len(B.idx))])
    ov = ws & (elev >= 140)
    corr_ovh = dict(ws=int(ov.sum()), taken=int((ov & ok).sum()), reach_ovh=round(float((ov & ok).sum() / max(ov.sum(), 1)), 4))
    mins = np.array([float(np.min(B.res[j])) if B.res[j] is not None else np.nan for j in range(len(B.idx))])
    depth = [round(-float(mins[j]), 3) for j in range(len(B.idx)) if np.isfinite(mins[j]) and mins[j] < 0]
    aud_c = PK.audit(M, B)
    B.res = res0
    aud = PK.audit(M, B)
    try: thm = LS.th_margin(M, B)
    except Exception as e: thm = dict(error=repr(e)[:300])
    out = dict(which=which, mode=B.mode, n=len(B.idx), ring_fix=ring, fit_fast=fit, frozen=rep, why=r.get("why"), parts_pairs=r.get("parts_pairs"),
               parts_ib14=r.get("parts_ib14"), audit={k: aud.get(k) for k in ("gap_near1", "gap_near2", "near_touch_min_mm") if k in aud},
               checks=o, poses_failing=len(bad), why_failing=why, failing_ids=sorted(bad)[:80], corrected=corr, corrected_overhead=corr_ovh,
               corrected_audit={k: aud_c.get(k) for k in ("gap_near1", "gap_near2", "near_touch_min_mm") if k in aud_c},
               corrected_contact_depth=dict(n=len(depth), sum_mm=round(float(np.sum(depth)), 3), max_mm=round(float(max(depth)), 3) if depth else 0.0),
               th_margin=thm, geometry=geometry(M1))
    return out


if __name__ == "__main__":
    if sys.argv[1] == "wear":
        which, path = sys.argv[2], sys.argv[3]
        t = time.time(); out = wear(dict(BEST), which, "--ring" in sys.argv)
        out.update(secs=round(time.time() - t, 1), exact=os.environ.get("CB_EXACT") == "1", params=BEST)
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        json.dump(out, open(path, "w"), indent=1, default=float)
        print(json.dumps({k: out.get(k) for k in ("which", "mode", "ring_fix", "fit_fast", "frozen", "why", "parts_pairs", "corrected", "corrected_overhead",
                                                   "poses_failing", "why_failing", "audit", "corrected_audit", "corrected_contact_depth", "checks", "th_margin",
                                                   "geometry", "secs")}, default=float))
