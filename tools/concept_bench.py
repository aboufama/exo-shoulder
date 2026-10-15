"""Common quick benchmark for mechanism CONCEPTS (the wide-tree stage before any GPU search), so different families
are compared on the same body, the same poses and the same two numbers. Idealised geometry is fine here (no CAD):
a concept supplies, per pose, the 3-D sample points of its metal (skin-facing surfaces at their real height, hubs at
their real size and stack) or None when it cannot take the pose (chain does not close / joint limit / self-collision).

    import sys; sys.path.insert(0, "tools"); import concept_bench as CB
    B = CB.Bench(n_clip=110, n_ws=360)                # poses: fit-clip frames (held-out clips excluded) + everyday workspace
    for i, pose in enumerate(B.poses):                # pose = dict(plane, elev, axial, flex, pron) (deg), + B.kind[i] 'clip'/'ws'
        P = my_concept_metal_points(pose, B.frames(i))   # (k, 3) mm in the thorax frame, or None
        B.record(i, P)
    print(B.report())                                  # reach (share of workspace poses taken), follow (share of clip frames
                                                       # taken), in-band 2-14 / 2-10 (share of metal samples), contact (any < 0)
Frame (pipeline/avg/body_pose.py): thorax mm, x anterior, y up, z right, origin = right GH centre (the trunk moves by
-lift with elevation, the arm rotates about GH). B.frames(i) gives the humerus / forearm rotation (H, F) and the
scapula rotation S of pose i, so a concept can attach parts to the upper arm or to the scapula. The skin of pose i is
B.skin(i) (vertices V, faces F of the rig's posed render skin) and B.dist(i, P) the signed distance of points P to it
(judge/sdist.py: exact closest point + winding number; < 0 = inside the body).

Metrics (the judges' definitions, simplified):
  reach   = share of everyday-workspace poses the concept takes with no metal inside the body (R16's idea);
  follow  = share of fit-clip frames taken (R3's idea);
  inband14 / inband10 = over the clip frames taken, the share of metal sample points whose distance to the skin is
            2-14 mm / 2-10 mm (a metal-centric proxy of R1: sample the skin-facing surfaces evenly, ~1 point / 4 mm2);
  contact = share of taken poses with any metal point < 0 mm (inside the body) - those poses count as NOT taken.
Held-out clips (Wave, Walking) are never used here. Light on CPU: posing the rig costs ~0.1 s per pose; the default
470 poses take ~1 min to pose + your geometry; use one process.
"""
import base64, gzip, io, json, os, sys
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "pipeline", "avg")); sys.path.insert(0, os.path.join(REPO, "judge"))
import body_pose as BP                                      # noqa: E402
from sdist import Mesh                                      # noqa: E402

FIT = json.load(open(os.path.join(REPO, "data", "raw", "split.json")))["motions"]["fit"]


class Bench:
    def __init__(self, n_clip=110, n_ws=360, seed=0):
        Z = np.load(io.BytesIO(gzip.decompress(base64.b64decode(open(os.path.join(REPO, "pipeline", "conformal", "band_poses_wsf.b64")).read()))))
        names = list(Z["NAMES"]); cid = Z["CID"]; P = Z["POSE"]
        fit_ids = [names.index(n) for n in FIT]; ws_id = names.index("Workspace (envelope)")
        clip_idx = np.nonzero(np.isin(cid, fit_ids))[0]; ws_idx = np.nonzero(cid == ws_id)[0]
        clip_idx = clip_idx[np.linspace(0, len(clip_idx) - 1, min(n_clip, len(clip_idx))).round().astype(int)]
        ws_idx = ws_idx[np.linspace(0, len(ws_idx) - 1, min(n_ws, len(ws_idx))).round().astype(int)]
        self.idx = np.r_[clip_idx, ws_idx]; self.kind = ["clip"] * len(clip_idx) + ["ws"] * len(ws_idx)
        self.clip = [names[c] for c in cid[self.idx]]
        self.poses = [dict(plane=float(p[0]), elev=float(p[1]), axial=float(p[2]), flex=float(p[3]), pron=float(p[4])) for p in P[self.idx]]
        self.res = [None] * len(self.idx); self._skin = {}

    def frames(self, i):
        """dict(T=(R, t) thorax, S=(R, t) scapula, H=(R, t) humerus, F=(R, t) forearm) of pose i (body_pose.segs)"""
        r = BP._rig(); (T, S, H, Fa, Pr), lift = BP.segs(r.L, r.s, self.poses[i])
        return dict(T=T, S=S, H=H, F=Fa, lift=lift)

    def skin(self, i):
        if i not in self._skin:
            if len(self._skin) > 8: self._skin.clear()
            V = BP.posed(self.poses[i]); self._skin[i] = (V, Mesh(V, BP.F, 2.0).build_grid(2.5, np.array([-320.0] * 3), np.array([320.0] * 3)))   # shoulder region; outside: brute-force winding
        return self._skin[i][0], BP.F

    def dist(self, i, P):
        """signed distance (mm) of points P (k, 3) to the posed skin of pose i; < 0 = inside the body"""
        self.skin(i); M = self._skin[i][1]
        d = np.abs(M.closest(np.asarray(P, float))[0])
        inside = M.winding_at(np.asarray(P, float)) >= 1
        return np.where(inside, -d, d)

    def record(self, i, P):
        """P: (k, 3) metal sample points in the thorax frame for pose i, or None (pose not taken)"""
        if P is None or not len(P): self.res[i] = None; return None
        d = self.dist(i, P); self.res[i] = d; return d

    def report(self):
        ws = [j for j, k in enumerate(self.kind) if k == "ws"]; cl = [j for j, k in enumerate(self.kind) if k == "clip"]
        ok = lambda j: self.res[j] is not None and float(np.min(self.res[j])) >= 0.0
        taken = [j for j in cl if ok(j)]; d = np.concatenate([self.res[j] for j in taken]) if taken else np.zeros(0)
        nz = [j for j in range(len(self.kind)) if self.res[j] is not None]
        return dict(reach=round(float(np.mean([ok(j) for j in ws])), 4), follow=round(float(np.mean([ok(j) for j in cl])), 4),
                    inband14=round(float(np.mean((d >= 2) & (d <= 14))), 4) if len(d) else 0.0,
                    inband10=round(float(np.mean((d >= 2) & (d <= 10))), 4) if len(d) else 0.0,
                    contact=round(float(np.mean([float(np.min(self.res[j])) < 0 for j in nz])), 4) if nz else 0.0,
                    poses=dict(clip=len(cl), ws=len(ws)))


if __name__ == "__main__":                                   # self-check: a shell 8 mm off the rest skin around the shoulder, fixed to the thorax
    B = Bench(n_clip=20, n_ws=20)
    V0 = BP.posed(B.poses[0]); sel = np.linalg.norm(V0, axis=1) < 90
    for i in range(len(B.poses)):
        Vi = BP.posed(B.poses[i]); N = Vi[sel] / (np.linalg.norm(Vi[sel], axis=1, keepdims=True) + 1e-9)
        B.record(i, Vi[sel][::7] + 8.0 * N[::7])
    print(B.report())
