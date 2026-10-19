"""K play / K offset -> the one fold-margin metric th (tools/concept_kit.py), per TAKEN pose of the verified desmo-conecut wear,
exact re-solve on the slaved law (the slipper red team's fold_rows, docs/research/slipper_mechanism/drive.py section 7, copied).
The J1-K-J2-J3 chain (seats, dyad, law kK 2.1534) of desmo-conecut is slipper-nose's unchanged, and th is set by the J3 axis,
which the arm pose fixes (the pin knee moves in J3's plane), so the chain state per pose is read from the slipper red team's
geo dumps (same benches, same pose order) and the TAKEN mask from the desmo verifier's per-pose dumps (+blend = verified).
The offset-0 row must reproduce the verifier's th minima (5.181 bench / 5.006 held) or the transfer is not valid.
    python3 docs/research/desmo_mechanism/fold_offset.py  -> fold_offset.json
"""
import json, math, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
D = math.degrees; R_ = math.radians
def unit(v): return v / np.linalg.norm(v, axis=-1, keepdims=True)
def rotm(ax, a):
    ax = unit(np.asarray(ax, float)); K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    return np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * K @ K
def ang(a, b): return D(math.acos(max(-1.0, min(1.0, float(a @ b) / (np.linalg.norm(a) * np.linalg.norm(b))))))
def dm(th, a, b): return np.minimum(th - np.abs(a - b), np.minimum(a + b, 360 - a - b) - th)
def angv(a, B_): return np.degrees(np.arccos(np.clip(B_ @ a, -1, 1)))


def fold_rows(Zx, tk_, offs):
    u1, u2, u3, uK, sp = Zx["u1"], Zx["u2"], Zx["u3"], Zx["uK"], float(Zx["sp"])
    st_, dK_ = Zx["kstate"], np.asarray(Zx["dK"], float)
    a1d, a2d = (D(float(Zx["a1"])) if float(Zx["a1"]) < 4 else float(Zx["a1"])), (D(float(Zx["a2"])) if float(Zx["a2"]) < 4 else float(Zx["a2"]))
    R2 = Zx["R2"]; b1 = ang(u1, uK)
    tsL, dKL, q2L = Zx["law_ts"], Zx["law_dK"], Zx["law_q2t"]
    tf = np.linspace(0, float(tsL[-1]), 4001); dKf = np.interp(tf, tsL, dKL); q2f = np.interp(tf, tsL, q2L)
    U3 = np.array([rotm(u2, q) @ u3 for q in q2f]); cf = angv(uK, U3)
    out = {}
    for off in offs:
        RK = np.array([rotm(uK, k + sp * R_(off) * (t > 0)) for k, t in zip(dKf, tf)])
        J2 = RK @ u2; J3 = np.einsum("nij,nj->ni", RK, U3)
        thf = angv(u1, J3); a1e = angv(u1, J2); a2e = np.array([ang(a_, b_) for a_, b_ in zip(J2, J3)])
        mf = np.minimum(dm(thf, b1, cf), dm(thf, a1e, a2e))
        own, idx = [], []
        for i in np.nonzero(tk_)[0]:
            j3 = R2[i] @ u3; th_i = ang(u1, j3)
            if abs(dK_[i]) <= 1e-6:
                own.append(float(dm(np.array([th_i]), a1d, a2d)[0])); idx.append(int(i)); continue
            t_i = float(np.interp(abs(dK_[i]), np.abs(dKL), tsL))
            w = np.nonzero(np.abs(tf - t_i) <= R_(6.0))[0]; jj = w[int(np.argmin(np.abs(thf[w] - th_i)))]
            own.append(float(mf[jj])); idx.append(int(i))
        own = np.array(own); j = int(np.argmin(own))
        out["%+.2f" % off] = dict(min=round(float(own.min()), 3), at_pose=idx[j], dK_at=round(D(abs(float(dK_[idx[j]]))), 2),
                                  lt5=int((own < 5 - 1e-6).sum()), n=int(len(own)))
    return out


OFFS = (-0.5, -0.3, -0.25, -0.2, -0.15, -0.1, -0.05, 0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.5)
res = {}
for wear in ("bench", "held"):
    Zx = dict(np.load(os.path.join(REPO, f"docs/research/slipper_mechanism/geo_{wear}.npz")))
    pp = json.load(open(os.path.join(REPO, f"docs/alignment/remeasure/desmo-conecut-knuckle-3r+blend_{wear}_perpose.json")))
    poses = pp["poses"]; n = len(Zx["taken"]); assert len(poses) == n, (len(poses), n)
    pz = Zx["poses"]; mis = 0
    for p in poses:
        q = pz[p["i"]]
        if abs(q[0] - p["plane"]) > 1e-3 or abs(q[1] - p["elev"]) > 1e-3 or abs(q[2] - p["axial"]) > 1e-3: mis += 1
    tk = np.array([bool(p["taken"]) for p in poses])
    both = tk & Zx["taken"].astype(bool); only_d = tk & ~Zx["taken"].astype(bool)
    rows = fold_rows(Zx, tk & Zx["kin_ok"].astype(bool), OFFS)
    res[wear] = dict(pose_order_mismatch=mis, desmo_taken=int(tk.sum()), slipper_taken=int(Zx["taken"].sum()), both=int(both.sum()),
                     desmo_only=int(only_d.sum()), desmo_only_not_kin_in_slipper=int((only_d & ~Zx["kin_ok"].astype(bool)).sum()), rows=rows)
    print(wear, json.dumps(res[wear])[:1500], flush=True)
res["note"] = ("K offset deg: + = K more open than the law (lead), - = K lags (closer to stop A). A free play band of width w around the law "
               "puts K anywhere in [-w/2, +w/2] if centred, [-w, 0] if the law is cut at the band's open edge.")
json.dump(res, open(os.path.join(HERE, "fold_offset.json"), "w"), indent=1)
