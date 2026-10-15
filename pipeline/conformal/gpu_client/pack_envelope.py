"""Add the plausible everyday workspace to a pose payload as an ENVELOPE clip: poses the links must clear the skin in
(the user's goal: "over the full range of motion", never touching the skin), but that are not scored. Without it the
shape is fitted to the training clips only and hits the skin in motions it never saw (fit-only shape: held-out Wave
followed 15.8 %, Walking arm swing 69.2 %, smoke13 2026-10-15).
Workspace: the red team's plausible everyday ROM (pipeline/redteam/rt_common.plausible), plane -90..150, elevation
0..170, humeral rotation r = ax + plane -90..90, on a step-deg grid; elbow at 90 deg flexion, forearm neutral. Poses in
which the arm passes through the person's own trunk or head are dropped (nobody can reach them; the rig's skin is
meaningless there - one such pose put BOTTOM's hub 268 mm out, smoke14): points 5 mm inside the arm skin (more than
60 mm from the GH centre, away from the axilla blend) with a whole-body winding number > 1.5 lie inside the body twice;
a pose is dropped when > 2 % of them do.
    python3 pack_envelope.py <in poses .b64> <out poses .b64> [step=15]"""
import base64, gzip, io, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); EXO = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(EXO, "avg")); sys.path.insert(0, os.path.join(EXO, "redteam"))
os.environ.setdefault("CLEAR", "4"); os.environ.setdefault("POST_HALF", "180"); os.environ.setdefault("H_LEN", "325")
_c = os.getcwd(); os.chdir(os.path.join(EXO, "avg")); import design_search as D; os.chdir(_c)
from rt_common import plausible
NAME = "Workspace (envelope)"
src, dst = sys.argv[1], sys.argv[2]; step = float(sys.argv[3]) if len(sys.argv) > 3 else 15.0
Z = dict(np.load(io.BytesIO(gzip.decompress(base64.b64decode(open(src).read()))), allow_pickle=False))
names = [str(x) for x in Z["NAMES"]]; assert NAME not in names, "already has an envelope clip"
pl, el, r = np.meshgrid(np.arange(-90, 151, step), np.arange(0, 171, step), np.arange(-90, 91, step), indexing="ij")
pl, el, r = pl.ravel(), el.ravel(), r.ravel(); k = plausible(pl, el); pl, el, ax = pl[k], el[k], r[k] - pl[k]
import multiprocessing as mp
def _self_hit(pose):
    import body_pose as BP, trimesh
    sys.path.insert(0, os.path.join(EXO, "..", "judge")); import sdist
    p, e, a = pose; V = BP.posed(dict(plane=float(p), elev=float(e), axial=float(a), flex=90.0, pron=0.0)); F = BP.F
    m = trimesh.Trimesh(V, F, process=False); N = np.asarray(m.vertex_normals)
    idx = np.nonzero(BP.ARMV & (np.linalg.norm(V, axis=1) > 60.0))[0][::40]
    w = sdist.winding_number(V[idx] - 5.0 * N[idx], V, F); return float((w > 1.5).mean())
CACHE = os.path.join(EXO, "..", ".cache", f"envelope_selfhit_{step:g}.npy")
if os.path.exists(CACHE): hit = np.load(CACHE)
else:
    import body_pose as BP; BP.posed(dict(plane=0, elev=0, axial=0, flex=90, pron=0))            # build the rig before forking
    with mp.get_context("fork").Pool(int(os.environ.get("JOBS", 4))) as pool: hit = np.array(pool.map(_self_hit, list(zip(pl, el, ax)), chunksize=8))
    os.makedirs(os.path.dirname(CACHE), exist_ok=True); np.save(CACHE, hit)
ok = hit <= 0.02; print(f"{int((~ok).sum())} of {len(ok)} workspace poses put the arm through the body -> dropped (worst {hit.max():.2f})")
pl, el, ax = pl[ok], el[ok], ax[ok]
HG, RS = [], []
for p, e, a in zip(pl, el, ax):
    H = D.Ry(p * D.D2R) @ D.Rx(-e * D.D2R) @ D.Ry(a * D.D2R); Rs = D.scapula(e); HG.append(Rs.T @ H); RS.append(Rs)
n = len(pl); cid = len(names)
Z["HG"] = np.concatenate([Z["HG"], np.array(HG, np.float32)]); Z["RS"] = np.concatenate([Z["RS"], np.array(RS, np.float32)])
Z["EL"] = np.concatenate([Z["EL"], el.astype(np.float32)]); Z["CID"] = np.concatenate([Z["CID"], np.full(n, cid, np.int32)])
Z["FI"] = np.concatenate([Z["FI"], np.arange(n, dtype=np.int32)]); Z["WT"] = np.concatenate([Z["WT"], np.zeros(n, np.float32)])
Z["POSE"] = np.concatenate([Z["POSE"], np.c_[pl, el, ax, np.full(n, 90.0), np.zeros(n)].astype(np.float32)])
Z["NAMES"] = np.array(names + [NAME]); Z["ENVELOPE"] = np.array([NAME])
buf = io.BytesIO(); np.savez_compressed(buf, **Z); open(dst, "w").write(base64.b64encode(gzip.compress(buf.getvalue())).decode())
print(f"{src} + {n} workspace poses (step {step:g} deg) -> {dst}: {len(Z['HG'])} frames, {len(Z['NAMES'])} clips")
