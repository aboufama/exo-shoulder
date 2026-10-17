"""trimlug-k165-knuckle-3r (round 11, lens 3 lever c, a polish of the lead's T5 watch reason): the slipper-nose lead
(docs/concepts/models/slipper-nose-knuckle-3r.py, SN_CELL=lead) unchanged except for features on the drive metal near K and
hub 2, aimed at the two elev-165 bench contacts (ws 237 (15, 165, -60), ws 264 (30, 165, -60)).
3 ACTIVE DOF (J1, J2, J3 encoded), K slaved and never read, 0 passive translations; the drive law, beta, g, r_c, nose and
every seat stay at the lead's verified values (the frozen claim protocol re-fits nothing: it is the lead's own).

FEATURES (all default OFF = the lead exactly; each is a cut, never added metal, except the optimistic lift):
  * trim_wall (mm): the horn lug's band is cut at r_K <= r_trim = max contact radius over the drive's own range
    [0, dK_lim] + trim_wall (r_K = radius from K's axis); trim_wall >= 50 = no trim. The flank face over the whole drive
    range is kept, so the cam table, dK_lim and the stroke are unchanged.
  * back_t (mm, default 6 = the lead's LUG_BACK): the lug band's thickness behind the flank (along the flank normal).
  * rlift / lift_r0 (mm): the spec's radial lift of the lug band dz = clip(r_K - lift_r0, 0, lift) along unit(X).
    OPTIMISTIC on purpose: the nose is not lengthened and the arm tip is not raised over the lifted lug (both would be
    needed in metal), so if the lift hurts here it hurts a fortiori.
  * crank_cut (mm): the spec's underside cut of the crank arm's arc over hub K (arc samples moved radially out).
  * crank_edge (mm): a chamfer on the arc's OUTER-LOWER edge (the edge row at r_K > r_c + 3 - crank_edge pulled in
    toward K's axis), the cut the measured contact direction asks for (the skin comes in laterally at 264).
  * cap_break (mm): hub 2's top-ring edge break (top ring pulled in by cap_break; a new ring at cap_break below the top).
  * dense (0/1, default 1): a DENSE contact-only copy of the lug (0.5 mm grid along the flank and behind it, underside,
    mid layer and top, same cuts), skin-checked like every contact-only sample and not scored for in-band. The lead's
    lug is 23 samples (~1.5 mm along the flank x 4 rows); a trim edge needs the dense copy to be sampled at its edge.
    It is a MEASUREMENT change: the lead with dense=1 and no cuts is reported as its own column.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/trimlug-k165-knuckle-3r.py [check] ['<json>']
    CB_EXACT=1 ... frozen|held '<json>' [out.json];  ... claims '[{tag, mode, params}]' outdir  (farm)
    ... k165 '<json>'   (the two elev-165 poses only, exact, per part)
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

os.environ.setdefault("SN_CELL", "lead")
_sp = importlib.util.spec_from_file_location("slipper_for_trimlug", os.path.join(HERE, "slipper-nose-knuckle-3r.py"))
SN = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(SN)
RF, SC, FL, S, BM = SN.RF, SN.SC, SN.FL, SN.S, SN.BM
unit = S.unit
ID = "trimlug-k165-knuckle-3r"
LEAD_ROW = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "slipper-nose-knuckle-3r.json")))["best_params"]
TRIM = dict(trim_wall=99.0, back_t=6.0, rlift=0.0, lift_r0=17.3, crank_cut=0.0, crank_edge=0.0, cap_break=0.0, dense=1)
PARAMS = dict(SN.PARAMS, **LEAD_ROW, **TRIM)
K165 = (237, 264)
_SN_CLAMP = SN._clamp


def _clamp(p):
    p = _SN_CLAMP(p)
    for k, lo, hi in (("trim_wall", 0.8, 99.0), ("back_t", 2.0, 6.0), ("rlift", 0.0, 4.0), ("crank_cut", 0.0, 1.0),
                      ("crank_edge", 0.0, 2.0), ("cap_break", 0.0, 1.0)):
        p[k] = min(max(float(p.get(k, TRIM[k])), lo), hi)
    p["lift_r0"] = float(p.get("lift_r0", 17.3)); p["dense"] = int(p.get("dense", 1))
    return p


def _rK(X, uK): return np.linalg.norm(X - (X @ uK)[:, None] * uK, axis=1)


class TLModel(SN.SNModel):
    def _rod_metal(self):
        super()._rod_metal()
        self._trimlug()

    def _flank(self):
        """the nose-centre path P1, contact points Q1 and flank normals N1 in link 1a's frame over [0, dK_lim] (the parent's
        synthesis loop, repeated: the parent does not keep them)"""
        g = self._scg; uK, dR, PV, sp, sig = g["uK"], g["dR"], g["PV"], g["sp"], g["sig"]; kg = g["kgrid"]
        jl = int(np.searchsorted(kg, g["dK_lim"] + 1e-9)); kg = kg[:max(jl, 2)]
        C0 = np.asarray(self._viz_rod["roller"], float); gg, cc = g["g"], g.get("c", 0.0)
        Rk = S.rotm(uK, sp * kg); Rcg = S.rotm(dR, sig * RF.phi_of(kg, gg, cc)); Cg = np.einsum("nij,j->ni", Rcg, C0 - PV) + PV
        ng = np.zeros_like(Cg); nprev = None
        for j in range(len(kg)):
            C = Cg[j]; vC = sig * float(RF.dphi_of(kg[j], gg, cc)) * np.cross(dR, C); vh = -sp * np.cross(uK, C); vr = vC - vh
            n = np.cross(unit(C), vr); nn = float(np.linalg.norm(n)); n = n / nn if nn > 1e-9 else (nprev if nprev is not None else unit(vh))
            n = (n if float(n @ vh) >= 0 else -n) if nprev is None else (n if float(n @ nprev) >= 0 else -n)
            nprev = n; ng[j] = n
        Qg = Cg + RF.ROLL_R * ng
        return (np.einsum("nij,nj->ni", Rk, Cg), np.einsum("nij,nj->ni", Rk, Qg), np.einsum("nij,nj->ni", Rk, ng), float(np.linalg.norm(C0)))

    def _trimlug(self):
        P = self.D.p; g = self._scg; uK = g["uK"]
        P1, Q1, N1, R0 = self._flank(); rL = R0 - 1.5
        rQ = _rK(Q1, uK); r_trim = float(rQ.max()) + float(P["trim_wall"]); bt = float(P["back_t"])
        lift, r0 = float(P["rlift"]), float(P["lift_r0"])

        def plane(X): return X / np.linalg.norm(X, axis=1)[:, None] * rL
        def lifted(X): return X + np.clip(_rK(X, uK) - r0, 0.0, lift)[:, None] * unit(X) if lift > 0 else X
        tree = cKDTree(P1)
        def keep(X):                                                     # the trim, the back thickness, the nose's swept path
            s = tree.query(X)[0] - RF.ROLL_R                            # back_t >= 6 = the lead's band, kept whole
            return (_rK(X, uK) <= r_trim + 1e-9) & ((s <= bt + 0.35 + 1e-9) | (bt >= 6.0 - 1e-9))
        m, lug = self.rigid["horn"]; k = keep(lug); lug_k = lug[k] if k.any() else lug[:1]
        self._trim_info = dict(r_trim=round(r_trim, 2), contact_r_max=round(float(rQ.max()), 2), back_t=bt, rlift=lift, lift_r0=r0,
                               horn_n=[int(len(lug)), int(len(lug_k))])
        new = lifted(lug_k); self.rigid["horn"] = (1, new)
        top_old = lug + S.T_LINK * unit(lug)
        for ci, (mm, X) in enumerate(self.contact):                      # the lug's top samples (parent: lug + T_LINK unit)
            if mm == 1 and len(X) == len(lug) and np.allclose(X, top_old): self.contact[ci] = (1, new + S.T_LINK * unit(new))
        g["lugM"] = new + 1.5 * unit(new); self.strap["HORN"] = (1, g["lugM"])
        if int(P["dense"]):
            d = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(Q1, axis=0), axis=1))])
            js = np.unique(np.searchsorted(d, np.arange(0.0, d[-1] + 1e-6, 0.5)).clip(0, len(Q1) - 1))
            ss = np.unique(np.r_[np.arange(0.3, bt + 1e-6, 0.5), bt])
            band = np.concatenate([plane(Q1[js] + s * N1[js]) for s in ss])
            root = []
            for b in plane(Q1[js[:1]] + ss[:, None] * N1[js[0]][None]):
                rb = float(_rK(b[None], uK)[0]); db = unit(b - (b @ uK) * uK)
                for r_ in np.arange(S.HUB_R + 0.5, rb, 0.5):
                    x_ = uK * (self.fK + float(P["hl"])) + r_ * db; t_ = (r_ - S.HUB_R) / max(rb - S.HUB_R, 1e-6)
                    root.append(unit(x_) * ((1 - t_) * float(np.linalg.norm(x_)) + t_ * rL))
            dl = np.concatenate([band, np.array(root)]) if root else band
            dl = dl[tree.query(dl + 1.5 * unit(dl))[0] >= RF.ROLL_R + 0.3 - 1e-6]
            dl = dl[keep(dl)]; dl = lifted(dl)
            dense = np.concatenate([dl, dl + 1.5 * unit(dl), dl + S.T_LINK * unit(dl)]) if len(dl) else np.zeros((0, 3))
            if len(dense): self.contact.append((1, dense))
            self._trim_info["dense_n"] = int(len(dense))
        # crank arm: underside cut over hub K (spec) and the outer-lower edge chamfer (measured direction)
        mc, X = self.rigid["crank"]; rc = float(P["r_c"]); rK = _rK(X, uK)
        arc = (np.abs(np.linalg.norm(X, axis=1) - (R0 + 1.5 + RF.RUNG)) < 0.05) & (rK > rc - 3.2)
        Y = X.copy(); cut = float(P["crank_cut"]); ce = float(P["crank_edge"])
        if cut > 0: Y[arc] = Y[arc] + cut * unit(Y[arc])
        if ce > 0:
            ia = np.nonzero(arc)[0]; edge = np.zeros(len(X), bool)
            if len(ia) and len(ia) % 4 == 0 and ia[-1] == len(X) - 1 and np.all(np.diff(ia) == 1):
                edge[ia[3::4]] = True                                    # the arc block: per psi the rows w = -3, -1, 1, 3 (outer)
            if edge.any():
                X0 = X[edge]; er = unit(X0 - (X0 @ uK)[:, None] * uK); Y[edge] = Y[edge] - ce * er
                wall = np.concatenate([X0 + z * unit(X0) for z in np.unique(np.r_[ce, np.arange(ce, S.T_LINK + 1e-6, 1.0), S.T_LINK])]
                                      + [X0 - (ce / 2) * er + (ce / 2) * unit(X0)])
                self.contact.append((9, wall))                           # the side wall above the 45-deg chamfer + the chamfer face
            self._trim_info["crank_edge_n"] = int(edge.sum())
        self.rigid["crank"] = (9, Y); self._trim_info["crank_arc_n"] = int(arc.sum())
        # hub 2's top ring: edge break
        cb = float(P["cap_break"])
        if cb > 0:
            mem2, cen2, ax2 = self.cyl["hub2"]; u2 = unit(ax2); rr = self.cyl_r["hub2"]
            rings = [ci for ci, (mm, X) in enumerate(self.contact) if mm == mem2 and len(X) == 32 and np.ptp((X - cen2) @ u2) < 1e-6
                     and abs(float(np.linalg.norm((X - cen2) - (((X - cen2) @ u2)[:, None] * u2), axis=1).mean()) - rr) < 1e-3]
            if rings:
                top = max(rings, key=lambda ci: float(((self.contact[ci][1] - cen2) @ u2).mean())); X = self.contact[top][1]
                w = X - cen2; h = w @ u2; radial = unit(w - h[:, None] * u2)
                self.contact[top] = (mem2, cen2 + h[:, None] * u2 + (rr - cb) * radial)
                self.contact.append((mem2, cen2 + (h - cb)[:, None] * u2 + rr * radial))
                self._trim_info["cap_ring_h"] = [round(float(((self.contact[ci][1] - cen2) @ u2).mean()), 2) for ci in rings]
        self._sc_info["trim"] = self._trim_info; self._rod_info = self._sc_info


# the lead's module and its parents build models through these names: point them at TLModel
SN.SNModel = TLModel; SN.PARAMS = PARAMS; SN._clamp = _clamp
SC.SCModel = TLModel; SC._clamp = _clamp; SC.PARAMS = PARAMS; RF.PARAMS = PARAMS
FL.G.KR.KB.KModel = TLModel; FL.FLModel_SC = TLModel; BM.PARAMS = PARAMS


def _report(B, params):
    r, M = SN._report(B, _clamp(dict(PARAMS, **params)))
    ti = (getattr(M, "_sc_info", None) or {}).get("trim")
    if ti: r.setdefault("cam", {})["trim"] = ti
    return r, M


def evaluate(B, params):
    r, M = _report(B, params)
    if r.get("sidecar_fail") or r.get("drive_idle") or r.get("pa_fail") or r.get("knee_moved"): r["honest"] = False
    p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); return r


def t5(B, M):
    """contact depth: per contact pose its deepest metal (rigid or contact-only), summed (T5) + the parts at that pose"""
    mem = {}
    for nm, (m, X) in M.rigid.items(): mem.setdefault(m, []).append(nm)
    out = []
    for j in range(len(B.idx)):
        if B.res[j] is None or float(np.min(B.res[j])) >= 0: continue
        per = {}
        for nm, (m, X) in M.rigid.items():
            if len(X): per[nm] = round(float(B.dist(j, M.world(m, j, X)).min()), 2)
        for ci, (m, X) in enumerate(M.contact):
            if len(X):
                kk = "c%d:%s" % (m, "/".join(mem.get(m, ["?"]))); per[kk] = min(per.get(kk, 99.0), round(float(B.dist(j, M.world(m, j, X)).min()), 2))
        po = B.poses[j]; out.append(dict(j=j, kind=B.kind[j], pose=[po.get("plane"), po.get("elev"), po.get("axial")] if isinstance(po, dict) else None,
                                         depth=round(-float(np.min(B.res[j])), 2), parts={k: v for k, v in sorted(per.items(), key=lambda kv: kv[1]) if v < 0}))
    return dict(n=len(out), sum_mm=round(sum(o["depth"] for o in out), 2), poses=out)


def frozen(P, nc=110, nw=360, keep=None):
    """the lead's claim protocol (fit Bench(60,160) fast, shape frozen, worn on Bench(nc, nw); nc == -1: held out); keep =
    optional list of ws indices of Bench(110,360) (with the 110 clip frames) for the reduced cone / k165 sets"""
    P = _clamp(dict(PARAMS, **P))
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    M1 = TLModel(B1, dict(P)); r1 = M1.run(); fit = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(TLModel):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info", "_wedge_info", "_trim_info"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self._sc = None
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
            self._truncate()
    if nc == -1:
        sp_ = importlib.util.spec_from_file_location("pk_polish_v_trimlug", os.path.join(REPO, "docs", "concepts", "verify", "skin-normal-3r-pin-knee-polish.py"))
        PVm = importlib.util.module_from_spec(sp_); sp_.loader.exec_module(PVm); B = PVm.held_bench()
    else:
        B = CB.Bench(n_clip=nc, n_ws=nw)
        if keep is not None:
            kk = np.r_[np.arange(nc), np.asarray(keep, int)] if keep != "k165" else np.asarray(K165, int)
            B.idx = B.idx[kk]; B.kind = [B.kind[j] for j in kk]; B.clip = [B.clip[j] for j in kk]; B.poses = [B.poses[j] for j in kk]
            B.res = [None] * len(B.idx)
    M = Frozen(B, P2); r = M.run()
    rep = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    ws = np.array(B.kind) == "ws"; elev = np.array([B.poses[j]["elev"] if isinstance(B.poses[j], dict) and "elev" in B.poses[j] else 0 for j in range(len(B.idx))])
    mins = np.array([float(np.min(B.res[j])) if B.res[j] is not None else np.nan for j in range(len(B.idx))])
    ov = ws & (elev >= 140); cl = ~ws
    dd = np.concatenate([B.res[j] for j in np.nonzero(cl & (mins >= 0))[0]]) if (cl & (mins >= 0)).any() else np.zeros(0)
    out = dict(fit_fast=fit, frozen=rep, mode=B.mode, bench=[nc, nw], why=r.get("why"), parts_ib14=r.get("parts_ib14"),
               audit=SN.PK.audit(M, B), t5=t5(B, M), overhead=dict(ws=int(ov.sum()), taken=int((ov & (mins >= 0)).sum())),
               clip_ib14=round(float(np.mean((dd >= 2) & (dd <= 14))), 5) if len(dd) else None, min_taken_mm=[round(float(x), 2) if x == x else None for x in mins],
               trim=getattr(M1, "_trim_info", None), cam={k: (M1._sc_info or {}).get(k) for k in ("dK_lim", "why_lim", "pa_horn_max_taken", "pa_eff_horn", "contact_r", "clear_lowarm_lug_min", "lug_r_max")})
    return out


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "claims":
        import subprocess
        od = sys.argv[3] if len(sys.argv) > 3 else "tl_out"; os.makedirs(od, exist_ok=True); procs = []
        for c in par:
            env = dict(os.environ, SN_CELL="lead", CB_EXACT="1", OMP_NUM_THREADS="1", IGL_NUM_THREADS="1", CB_QUIET_EXACT="1")
            lg = open(os.path.join(od, c["tag"] + ".log"), "w")
            procs.append(subprocess.Popen([sys.executable, os.path.abspath(__file__), c.get("mode", "frozen"), json.dumps(c.get("params", {})),
                                           os.path.join(od, c["tag"] + ".json")] + ([json.dumps(c["keep"])] if "keep" in c else []),
                                          env=env, stdout=lg, stderr=subprocess.STDOUT))
        for pr in procs: pr.wait()
        print("claims done", [pr.returncode for pr in procs]); sys.exit()
    if mode in ("frozen", "held", "k165"):
        t = time.time()
        if mode == "held": out = frozen(par, -1, -1)
        elif mode == "k165": out = frozen(par, 110, 360, keep="k165")
        else: out = frozen(par, 110, 360, keep=json.loads(sys.argv[4]) if len(sys.argv) > 4 else None)
        out["params"] = par; out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        a = out.get("audit", {})
        print(json.dumps(dict(frozen=out["frozen"], why=out["why"], t5={k: out["t5"][k] for k in ("n", "sum_mm")}, t5_poses=[(p["pose"], p["depth"], list(p["parts"].items())[:4]) for p in out["t5"]["poses"]],
                              near1=a.get("gap_near1"), minmetal=a.get("near_touch_min_mm"), ovh=out["overhead"], clip_ib14=out["clip_ib14"],
                              parts=out["parts_ib14"], trim=out["trim"], cam=out["cam"], secs=out["secs"]), default=float)); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report(B, par)
    print(json.dumps(dict(gap=r["gap"], reach=r["reach"], follow=r["follow"], inband14=r["inband14"], inband10=r["inband10"], contact=r["contact"],
                          near2=r.get("gap_near2"), why=r.get("why"), parts=r.get("parts_ib14"), trim=(r.get("cam") or {}).get("trim"), secs=round(time.time() - t)), default=float))
