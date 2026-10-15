"""Fit-pose skin cache for docs/concepts/models/seed-2r-cring.py: posed render-skin vertices of the shoulder region
(within R_REG mm of GH in the rest pose or any probe pose) for every fit-clip frame (held-out clips excluded) and a
workspace subsample (every 4th workspace pose + the bench's own n_ws=160 / 40 picks). The link / hub / ring envelopes
of the concept are fitted on these poses (the training set; held-out clips are never posed here)."""
import base64, gzip, io, json, os, sys, time
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "pipeline", "avg"))
import body_pose as BP                                                     # noqa: E402
OUT = os.path.join(REPO, ".cache", "concept_models", "seed-2r-cring", "fit_skin.npz")
R_REG = 300.0


def fit_indices():
    Z = np.load(io.BytesIO(gzip.decompress(base64.b64decode(open(os.path.join(REPO, "pipeline", "conformal", "band_poses_wsf.b64")).read()))))
    names = list(Z["NAMES"]); cid = Z["CID"]; P = Z["POSE"]
    FIT = json.load(open(os.path.join(REPO, "data", "raw", "split.json")))["motions"]["fit"]
    clip_idx = np.nonzero(np.isin(cid, [names.index(n) for n in FIT]))[0]
    ws_idx = np.nonzero(cid == names.index("Workspace (envelope)"))[0]
    pick = set(ws_idx[::4].tolist())
    for n in (160, 40):
        pick |= set(ws_idx[np.linspace(0, len(ws_idx) - 1, n).round().astype(int)].tolist())
    return np.r_[clip_idx, np.array(sorted(pick))], P, cid, names


def build():
    idx, P, cid, names = fit_indices()
    pose = lambda p: dict(plane=float(p[0]), elev=float(p[1]), axial=float(p[2]), flex=float(p[3]), pron=float(p[4]))
    probes = [dict(plane=0, elev=0, axial=0, flex=12, pron=0), dict(plane=30, elev=160, axial=0, flex=12, pron=0),
              dict(plane=90, elev=90, axial=0, flex=12, pron=0), dict(plane=0, elev=90, axial=0, flex=12, pron=0)]
    keep = np.zeros(len(BP.V0), bool)
    for q in probes: keep |= np.linalg.norm(BP.posed(q), axis=1) < R_REG
    vid = np.nonzero(keep)[0]; t = time.time(); V = np.zeros((len(idx), len(vid), 3), np.float32)
    for k, j in enumerate(idx):
        V[k] = BP.posed(pose(P[j]))[vid]
        if k % 50 == 0: print(k, len(idx), round(time.time() - t), flush=True)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    np.savez(OUT + ".tmp.npz", idx=idx, vid=vid, V=V, POSE=P[idx], CID=cid[idx])
    os.replace(OUT + ".tmp.npz", OUT); print("saved", OUT, V.shape, round(time.time() - t))


if __name__ == "__main__":
    build()
