"""Skin envelope service for the fair CAD pipeline: exact per-frame skin maps (band evaluator's 0.5 deg maps, built from the
posed skin mesh with a 3 mm ball splat) queried in any part's own frame over the frames a design actually follows.

    E = Envelope(<band design dir>)                 # clips.json of the band design (10 fps frames, member frames G)
    E.min_radius(group, dirs)  -> per direction, the largest radius over followed frames at which metal would still be
                                  inside the 2 mm clearance (r1c - 1): metal must sit beyond it
"""
import json, math, os, io, gzip, base64
import numpy as np, torch
HERE = os.path.dirname(os.path.abspath(__file__)); CONF = os.path.join(HERE, "..")
MAPS = os.environ.get("MAPS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".cache", "maps_s1.pt"))   # tools/build_maps.py
LAT_LO, LAT_HI, MRES = None, None, 0.5
import sys; sys.path.insert(0, os.path.join(CONF, "gpu")); import band_impl as BI
LAT_LO, LAT_HI, MRES, MH, MW = BI.LAT_LO, BI.LAT_HI, BI.MRES, BI.MH, BI.MW
_M = None
def maps():
    global _M
    if _M is None: _M = torch.load(MAPS)
    return _M

class Envelope:
    def __init__(self, design_dir):
        Z = np.load(io.BytesIO(gzip.decompress(base64.b64decode(open(os.path.join(CONF, "band_poses.b64")).read()))))
        self.HG, self.RS, P = Z["HG"], Z["RS"], Z["POSE"]
        C = json.load(open(os.path.join(design_dir, "clips.json"))); self.frames = []
        for cl in C["clips"]:
            for k, f in enumerate(cl["frames"]):
                if k % 3 or f["held"]: continue
                p = int(np.argmin(np.abs(P - np.array(f["p"])).sum(1)))
                self.frames.append((p, {g: np.array(v).reshape(3, 3) for g, v in f["G"].items()}))
        self.C = C
    def world(self, group, dirs):
        """(F, N, 3) world (thorax) directions of local dirs over the followed frames; group 'can' = canonical humerus frame"""
        d = np.asarray(dirs, float)
        Rs = [(self.RS[p] @ self.HG[p]) if group == "can" else G[group] for p, G in self.frames]
        return np.einsum("fij,nj->fni", np.array(Rs), d), np.array([p for p, _ in self.frames])
    def lookup(self, name, W, pidx):
        lon = np.arctan2(W[..., 2], W[..., 0]); lat = np.arcsin(np.clip(W[..., 1], -1, 1))
        j = np.floor((lon + math.pi) / (MRES * math.pi / 180)).astype(int) % MW
        i = np.clip(np.floor((lat - LAT_LO * math.pi / 180) / (MRES * math.pi / 180)).astype(int), 0, MH - 1)
        M = maps()[name]; flat = torch.from_numpy((pidx[:, None] * (MH * MW) + i * MW + j).reshape(-1))
        return M.view(-1)[flat].float().numpy().reshape(W.shape[:-1])
    def min_radius(self, group, dirs, clear=2.0, chunk=4000):
        """max over followed frames of the radius metal must exceed along each local direction (skin + `clear`)"""
        out = []
        for k in range(0, len(dirs), chunk):
            W, pidx = self.world(group, dirs[k:k + chunk]); r1c = self.lookup("r1c", W, pidx)
            out.append((r1c - (3.0 - clear)).max(0))
        return np.concatenate(out)
    def skin_radius(self, group, dirs, chunk=4000):
        """(F, N) skin first-exit radius per followed frame (0 = no skin along that direction)"""
        out = []
        for k in range(0, len(dirs), chunk):
            W, pidx = self.world(group, dirs[k:k + chunk]); out.append(self.lookup("r1", W, pidx))
        return np.concatenate(out, 1)
