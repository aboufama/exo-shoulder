"""Add the plausible everyday workspace to a pose payload as an ENVELOPE clip: poses the links must clear the skin in
(the user's goal: "over the full range of motion", never touching the skin), but that are not scored. Without it the
shape is fitted to the training clips only and hits the skin in motions it never saw (fit-only shape: held-out Wave
followed 15.8 %, Walking arm swing 69.2 %, smoke13 2026-10-15).
Workspace: the red team's plausible everyday ROM (pipeline/redteam/rt_common.plausible), plane -90..150, elevation
0..170, humeral rotation r = ax + plane -90..90, on a step-deg grid; elbow at 90 deg flexion, forearm neutral. Nothing is
filtered here: an arm-fixed hub can truly press into the chest in extreme cross-body poses (smoke14: one pose put
BOTTOM's hub 268 mm out), and the rig's upper arm already overlaps its trunk at low elevation, so a self-intersection
test cannot tell impossible poses from natural ones. The evaluator (band_impl w) gives such poses up instead, at a
price: the score is multiplied by the share of the workspace the design can move through.
    python3 pack_envelope.py <in poses .b64> <out poses .b64> [step=15] [--functional]
--functional (user 2026-10-15: "Functional range"): the plausible envelope narrowed to everyday function until the
user's OpenCap max-ROM exists - daily-living studies need about 60 deg external / 100 deg internal rotation and
120-130 deg elevation (Namdari et al. 2012, J Shoulder Elbow Surg 21:1177); elevation is kept to 170 deg in the
forward / side planes (overhead matters most to the user), humeral rotation r = ax + plane is limited to -65..90 deg up
to 100 deg elevation, -45..30 deg above it (the overhead clips use -30..11), -20..90 deg in extension planes (< -30,
behind the back) and -30..90 deg across the body (> 120). Every clip pose lies inside (checked at run time)."""
import base64, gzip, io, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); EXO = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(EXO, "avg")); sys.path.insert(0, os.path.join(EXO, "redteam"))
os.environ.setdefault("CLEAR", "4"); os.environ.setdefault("POST_HALF", "180"); os.environ.setdefault("H_LEN", "325")
_c = os.getcwd(); os.chdir(os.path.join(EXO, "avg")); import design_search as D; os.chdir(_c)
from rt_common import plausible
NAME = "Workspace (envelope)"
args = [a for a in sys.argv[1:] if not a.startswith("--")]; FUNC = "--functional" in sys.argv
src, dst = args[0], args[1]; step = float(args[2]) if len(args) > 2 else 15.0
def functional(pl, el, r):
    lo = np.where(pl < -30, -20.0, np.where(pl > 120, -30.0, np.where(el > 100, -45.0, -65.0)))
    hi = np.where((pl >= -30) & (pl <= 120) & (el > 100), 30.0, 90.0)
    return (r >= lo) & (r <= hi)
Z = dict(np.load(io.BytesIO(gzip.decompress(base64.b64decode(open(src).read()))), allow_pickle=False))
names = [str(x) for x in Z["NAMES"]]; assert NAME not in names, "already has an envelope clip"
pl, el, r = np.meshgrid(np.arange(-90, 151, step), np.arange(0, 171, step), np.arange(-90, 91, step), indexing="ij")
pl, el, r = pl.ravel(), el.ravel(), r.ravel(); k = plausible(pl, el)
if FUNC:
    k &= functional(pl, el, r)
    cp = Z["POSE"]; inside = plausible(cp[:, 0], cp[:, 1]) & functional(cp[:, 0], cp[:, 1], cp[:, 2] + cp[:, 0])
    print(f"functional range: {100 * inside.mean():.1f} % of the {len(cp)} clip poses inside it")
pl, el, ax = pl[k], el[k], r[k] - pl[k]
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
