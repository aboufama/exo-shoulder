"""Adversarial verifier for closure-set-arc-knee-3r (2026-10-16). Re-measures one configuration with the model's own
checks (osn S.VModel + the knee / dyad / fork checks) plus the verifier's:

  * STRICT knee tracking along every FIT clip at 10 fps: the model resets its reference after a no-root frame (the next
    frame re-acquires the root nearest psi_rest with no jump check) and, after a rejected jump, carries on from the
    jumped branch. Here the reference stays the LAST FOLLOWED state: a frame is followed only if a root exists, the
    kinematic checks pass, and its step from the last followed frame is <= JUMP x (frames since) - a re-acquired branch
    after a jam is a branch the knee cannot take. Frames whose strict root differs from the model's are not taken.
  * outer-face skin check: link 1 / link 2 strap TOPS (the model checks hub walls + crowns, dyad tops and fork walls);
  * hub-axis accessibility: each hub seat (c_k + f_k u_k) within 140 mm of GH;
  * near-touch and the overhead split on the corrected set; frozen shape (fit Bench(60,160) FAST, worn on the big bench).

    CB_EXACT=1 python3 docs/concepts/verify/closure-set-arc-knee-3r.py big_frozen <out.json> ['<json params>']
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
spec = importlib.util.spec_from_file_location("csak_model", os.path.join(REPO, "docs", "concepts", "models", "closure-set-arc-knee-3r.py"))
CS = importlib.util.module_from_spec(spec); spec.loader.exec_module(CS)
S = CS.S; D2R = CS.D2R
ROW = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "closure-set-arc-knee-3r.json")))


def strict_track(M):
    """re-track the FIT clips with a reference that survives failures; returns {global frame index: (psi, good)}"""
    D = M.D; P = M.p; Z = M.Z; names = list(Z["NAMES"]); out = {}; st = dict(frames=0, good=0, diff_root=0)
    for nm in CB.FIT:
        ii = np.nonzero(Z["CID"] == names.index(nm))[0]; ii = ii[np.argsort(Z["FI"][ii], kind="stable")]
        Qc = Z["HG"][ii].astype(float); pr, au = D.roots(Qc)
        ref = P["psi_rest"] * D2R; refq = None; since = 1
        for j, gi in enumerate(ii):
            st["frames"] += 1
            psi, a, has = CS.pick(pr[:, j:j + 1], au[:, j:j + 1], np.array([ref]))
            good = bool(has[0])
            if good:
                k = D.core(Qc[j:j + 1], psi); ph, gm, bt, dok, _, _ = D.dyad(k["s"])
                good = bool(k["ok"][0]) and bool(dok[0]) and float(a[0]) >= P["auth_min"] and abs(float(psi[0])) <= (P["pmax"] - 0.5) * D2R
                qv = np.degrees(np.r_[k["q"][0, :2], k["q"][0, 2] + (ph[0] - P["phiE"]) * D2R, psi[0]]); qv = np.r_[qv, ph[0], gm[0]]
                if good and refq is not None and float(np.abs(CS.wrap(qv - refq)).max()) > S.JUMP * since: good = False
            if good: ref = float(psi[0]); refq = qv; since = 1; st["good"] += 1
            else: since += 1
            out[int(gi)] = (float(psi[0]) if has[0] else np.nan, good)
    return out, st


def apply_strict(M):
    trk, st = strict_track(M); n = 0; nd = 0
    for a, gi in enumerate(M.B.idx):
        if M.B.kind[a] != "clip" or int(gi) not in trk or not M.kin_ok[a]: continue
        ps, good = trk[int(gi)]
        if not good: M.kin_ok[a] = False; M.why[a] = "flip"; n += 1
        elif abs(ps - M.psi[a]) > 0.5 * D2R: M.kin_ok[a] = False; M.why[a] = "flip"; nd += 1
    st["clip_frames_removed"] = n; st["clip_frames_other_root"] = nd; return st


def frozen_model(B, P):
    B1 = CS._bench(60, 160, fast=True); r1, M1 = CS._report(B1, P)
    P2 = {k: v for k, v in M1.p.items() if isinstance(v, (int, float, str, bool)) or v is None}

    class Frozen(CS.Model):
        def fit(self):
            for a in ("geo", "rigid", "link_pts", "f", "lv", "contact", "cyl", "box", "strap", "cyl_surf", "Hneed", "Lneed", "trunnion_off", "trunnion_in"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
    M = Frozen(B, P2)
    keys = ("gap", "reach", "follow", "inband14", "inband10", "contact")
    return M, dict({k: r1[k] for k in keys}, mode=B1.mode, dh=M1.p.get("dh"), invalid=r1.get("invalid", False), why=r1.get("why"),
                   pinb=r1.get("pinb_along_mm"), trunnion_in=r1.get("trunnion_in_housing"))


def audit(M, B):
    taken = lambda i: B.res[i] is not None and float(np.min(B.res[i])) >= 0
    out = {}; D = M.D
    out["hub_seat_mm_from_GH"] = [round(float(np.linalg.norm(D.c[k] + M.f[k] * D.u[k])), 1) for k in range(3)]
    out["hub_f"] = [round(float(x), 1) for x in M.f]
    OS = [(nm + "top", mem, pts + S.T_LINK * S.unit(pts)) for nm, (mem, pts) in M.link_pts.items() if len(pts)]
    hit = {}; cmin = {}; low = []
    for i in range(len(B.idx)):
        if not taken(i): continue
        parts = [M.world(mem, i, X) for nm, mem, X in OS] + [M.world(m, i, Pc) for m, Pc in M.contact]
        dd = B.dist(i, np.concatenate(parts)); cut = np.cumsum([0] + [len(x) for x in parts]); worst = (1e9, None)
        for k, (nm, mem, X) in enumerate(OS):
            d = float(dd[cut[k]:cut[k + 1]].min())
            if d < worst[0]: worst = (d, nm)
        cmin[i] = min(worst[0], float(dd[cut[len(OS)]:].min()) if cut[-1] > cut[len(OS)] else 1e9)
        low.append((worst[0], i, worst[1]))
        if worst[0] < 0: hit[i] = worst
    low.sort(); out["outer_low"] = [dict(mm=round(d, 2), part=nm, elev=B.poses[i]["elev"]) for d, i, nm in low[:5]]
    out["outer_contact_poses"] = len(hit)
    res0 = list(B.res)
    for i, (d, nm) in hit.items(): B.res[i] = np.r_[B.res[i], d]
    rc = B.report(); out["corrected"] = {k: rc[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    mins = sorted((min(float(np.min(B.res[i])), cmin.get(i, 1e9)), i) for i in range(len(B.idx)) if taken(i))
    out["near_touch_min_mm"] = round(mins[0][0], 2) if mins else None
    res1 = list(B.res)
    for thr in (1.0, 2.0):
        for d, i in mins:
            if d < thr: B.res[i] = np.r_[B.res[i], -1e-3]
        out[f"gap_near{int(thr)}"] = B.report()["gap"]; out[f"near{int(thr)}_poses"] = int(sum(1 for d, i in mins if d < thr)); B.res = list(res1)
    el = np.array([p["elev"] for p in B.poses]); kind = np.array(B.kind)
    ws = np.nonzero((el >= 140) & (kind == "ws"))[0]; cl = np.nonzero((el >= 140) & (kind == "clip"))[0]; allh = np.nonzero(el >= 140)[0]
    tk = [i for i in allh if taken(i)]; d = np.concatenate([B.res[i] for i in tk]) if tk else np.zeros(0)
    out["overhead140"] = dict(ws=len(ws), reach=round(float(np.mean([taken(i) for i in ws])), 4) if len(ws) else None,
                              clip=len(cl), follow=round(float(np.mean([taken(i) for i in cl])), 4) if len(cl) else None,
                              inband14=round(float(((d >= 2) & (d <= 14)).mean()), 4) if len(d) else None,
                              inband10=round(float(((d >= 2) & (d <= 10)).mean()), 4) if len(d) else None,
                              contact_poses=int(sum(1 for i in allh if B.res[i] is not None and float(np.min(B.res[i])) < 0)),
                              why_not={k: int(sum(1 for i in allh if not taken(i) and M.why[i] == k)) for k in set(M.why[allh]) if k})
    B.res = res0
    return out


def main():
    task, outp = sys.argv[1], sys.argv[2]
    P = json.loads(sys.argv[3]) if len(sys.argv) > 3 else dict(ROW["best_params"])
    t0 = time.time(); out = dict(task=task, params=P, exact=os.environ.get("CB_EXACT") == "1")
    B = CB.Bench(110, 360) if task.startswith("big") else CB.Bench(60, 160)
    M, out["fit60"] = frozen_model(B, P) if task.endswith("frozen") else (CS.Model(B, P), None)
    out["strict"] = apply_strict(M)
    r = M.run(); out["mode"] = B.mode
    out["model"] = {k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "why", "parts_pairs", "levels", "knee")}
    out["audit"] = audit(M, B); out["secs"] = round(time.time() - t0, 1)
    os.makedirs(os.path.dirname(os.path.abspath(outp)), exist_ok=True)
    json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps(dict(task=task, mode=out["mode"], fit60=out["fit60"], strict=out["strict"],
                          model={k: out["model"][k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")},
                          corrected=out["audit"]["corrected"], near1=out["audit"]["gap_near1"], secs=out["secs"]), default=float), flush=True)


if __name__ == "__main__":
    main()
