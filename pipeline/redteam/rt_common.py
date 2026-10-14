"""Red-team helpers: clips, the reference 4R chain, the lead's 3-DOF candidates (pipeline/girdle/p0_results.json), an
everyday-task label for an arm pose, and body-region labels for skin vertices. Read-only on the rest of the repo.

Frames and conventions are the rig's (avg/body_pose.py): thorax frame, mm, x anterior, y up, z right, origin = right GH
centre; arm pose (plane, elev, axial) with Rh = Ry(plane) Rx(-elev) Ry(axial). axial = -plane is the twist-free
(Codman-free) humeral rotation, so r = axial + plane is the humeral rotation relative to that neutral (clips use
r = -65 (wave, external) .. +90 (wash opposite shoulder, internal)).
"""
import json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(os.path.dirname(HERE))
for p in ("pipeline/girdle", "pipeline/avg", "pipeline/full-exo", "judge"):
    sys.path.insert(0, os.path.join(REPO, p))
import girdle as GD                                    # noqa: E402
from girdle import BP, D2R, unit                       # noqa: E402
DES = "cad_r13_n4_s1343_1"; DD = os.path.join(REPO, "pipeline", "full-exo", "designs", DES)
HOLD_OUT = ("Wave", "Walking arm swing")
OUT = os.path.join(HERE, "results"); os.makedirs(OUT, exist_ok=True)


def clips():
    """[(clip, i, want(5), p(5), held, G dict, q)]"""
    C = json.load(open(os.path.join(DD, "clips.json")))
    return [(c["name"], i, f["want"], f["p"], f["held"], f["G"], f["q"]) for c in C["clips"] for i, f in enumerate(c["frames"])]


# ------------------------------------------------------------------ reference 4R (spherical, all axes through GH)
class Ref4R:
    """b (base axis) fixed in the base frame; J2 on the a1-cone round b at spare angle q; J4 = Hg w (arm-fixed);
    J3 = circle intersection (a2 from J2, a3 from J4, branch). valid = both inner triangles >= SING from straight/folded
    (make_clips_full.pins_for / design_search_families.triangle_ok, SING = 12 deg)."""
    SING = 12.0

    def __init__(self):
        K = json.load(open(os.path.join(DD, "design.json")))["kinematics"]; self.K = K
        self.b = GD.bvec(K["az"], K["el"]); self.a = [x * D2R for x in K["a"]]; self.w = GD.w_dir(*K["w"]); self.br = K["branch"]
        e = np.cross(self.b, [0.0, 1, 0]); self.e = e / np.linalg.norm(e); self.f = np.cross(self.b, self.e)

    def configs(self, Hg, qs):
        """Hg (P,3,3) humerus rotation in the base frame, qs (Q,) rad -> dict of (P,Q,...) arrays"""
        a1, a2, a3 = self.a; P, Q = len(Hg), len(qs)
        u4 = np.einsum("pij,j->pi", Hg, self.w)                                   # (P,3)
        c2 = math.cos(a1) * self.b + math.sin(a1) * (np.cos(qs)[:, None] * self.e + np.sin(qs)[:, None] * self.f)   # (Q,3)
        C2 = np.broadcast_to(c2[None], (P, Q, 3)); U4 = np.broadcast_to(u4[:, None], (P, Q, 3))
        d = np.clip((C2 * U4).sum(-1), -1, 1); n = np.cross(C2, U4); nn = np.linalg.norm(n, axis=-1, keepdims=True); n = n / (nn + 1e-12)
        den = 1 - d ** 2 + 1e-12; ca = (math.cos(a2) - d * math.cos(a3)) / den; cb = (math.cos(a3) - d * math.cos(a2)) / den
        p = ca[..., None] * C2 + cb[..., None] * U4; h2 = 1 - (p * p).sum(-1)
        c3 = p + self.br * np.sqrt(np.clip(h2, 0, None))[..., None] * n; c3 = c3 / np.linalg.norm(c3, axis=-1, keepdims=True)
        def margin(x, z, A, B):
            t = np.degrees(np.arccos(np.clip((x * z).sum(-1), -1, 1))); A, B = math.degrees(A), math.degrees(B)
            return np.minimum(t - abs(A - B), min(A + B, 360 - A - B) - t)
        m3 = margin(C2, U4, a2, a3); m2 = margin(np.broadcast_to(self.b, (P, Q, 3)), c3, a1, a2)
        closes = (h2 > 0) & (m3 >= 0) & (m2 >= 0); valid = closes & (m3 >= self.SING) & (m2 >= self.SING)
        J = np.stack([np.broadcast_to(self.b, (P, Q, 3)), C2, c3, U4], -1)        # (P,Q,3,4) joint axes
        sv = np.sqrt(np.clip(np.linalg.eigvalsh(J @ np.swapaxes(J, -1, -2))[..., 0], 0, None))
        J3 = J[..., 1:]; sv3 = np.sqrt(np.clip(np.linalg.eigvalsh(J3 @ np.swapaxes(J3, -1, -2))[..., 0], 0, None))   # J1 locked
        return dict(sv=sv, sv3=sv3, m2=m2, m3=m3, closes=closes, valid=valid)


# ------------------------------------------------------------------ the lead's 3-DOF candidates
CAND_KEYS = {"ring": "3 DOF: 2R shoulder (offset axes) + humeral-rotation ring", "3R": "3 DOF: 3R, offset axes"}


def load_candidates(path=os.path.join(REPO, "pipeline", "girdle", "p0_results.json"), with_mintravel=True):
    """{'ring': (prm, x, entry), '3R': ...}. x = the lead's published axis points (_x); refit (same LP, fit clips) if absent"""
    R = json.load(open(path)); A = R["architectures"]; out = {}
    for tag, key in CAND_KEYS.items():
        k = next((k for k in A if "params" in A[k] and "offset" in k and "no offsets" not in k and (("ring" in k) if tag == "ring" else ("3R" in k))), None)
        if k is None: continue
        e = A[k]; pr = e["params"]
        if "b" in pr: prm = dict(b=tuple(pr["b"]), a1=pr["a1"], a2=pr["a2"], branch=pr["branch"], w=None if pr.get("w") is None else tuple(pr["w"]))
        else: prm = dict(b=(pr["b_az"], pr["b_el"]), a1=pr["a1"], a2=pr["a2"], branch=pr["branch"], w=None if "w_delta" not in pr else (pr["w_delta"], pr["w_az"]))
        if "_x" in e: x = np.array(e["_x"], float); src = "published _x"
        else:
            W = np.array([f[2] for f in clips()], float); names = np.array([f[0] for f in clips()])
            MF = GD.Motion(W[~np.isin(names, HOLD_OUT)]); ch = GD.Chain3(prm); Am, *_ = ch.kin(MF)
            x, _ = GD.fit_minimax(Am, MF.lift, ch.coax, 60.0); src = "refit (minimax LP, fit clips)"
        out[tag] = dict(prm=prm, x=x, entry=e, key=k, x_source=src)
    rt = os.path.join(REPO, "pipeline", "girdle", "ring_travel.json")
    if with_mintravel and os.path.exists(rt):                     # the lead's least-ring-travel 2R + ring (ring_travel.py): x refit here
        b = json.load(open(rt))["best"]; prm = dict(b=tuple(b["b"]), a1=b["a1"], a2=b["a2"], branch=b["branch"], w=None)
        W = np.array([f[2] for f in clips()], float); names = np.array([f[0] for f in clips()])
        MF = GD.Motion(W[~np.isin(names, HOLD_OUT)]); ch = GD.Chain3(prm); Am, *_ = ch.kin(MF)
        x, _ = GD.fit_minimax(Am, MF.lift, True, 60.0)
        out["ring_mt"] = dict(prm=prm, x=x, entry=dict(), key="ring_travel.json best (least ring travel)", x_source="refit (minimax LP, fit clips)")
    return out


def chain3_metrics(ch, M):
    """per pose: sigma_min of the 3 joint axes, the lead's singular margin (deg), closes"""
    r = ch.kin(M)
    if r is None: return None
    A, mg, ok, R1, R2, RA = r; W = M.RH @ ch.w
    J = np.stack([np.broadcast_to(ch.b, W.shape), ch.c, W], -1)
    sv = np.sqrt(np.clip(np.linalg.eigvalsh(J @ np.swapaxes(J, -1, -2))[:, 0], 0, None))
    return dict(A=A, margin=mg, ok=ok, sv=sv, R1=R1, R2=R2, RA=RA)


# ------------------------------------------------------------------ what everyday task is this arm pose?
def hand_pos(pl, el, ax, flex=90.0):
    """approximate hand position (thorax frame, mm) for an arm pose and elbow flexion, upper arm 300 mm, forearm+hand 330 mm"""
    Rh = GD.Rh_of(pl, el, ax); h = Rh @ np.array([0, -1.0, 0]); f0 = np.array([math.sin(flex * D2R), -math.cos(flex * D2R), 0.0])
    return 300 * h + 330 * (Rh @ f0)


def task_label(pl, el, ax):
    """heuristic everyday-task label from where the elbow points and where the hand is at 90 deg elbow flexion"""
    r = ax + pl; hd = GD.Rh_of(pl, el, ax) @ np.array([0, -1.0, 0]); H = hand_pos(pl, el, ax)
    rot = "internal" if r > 20 else "external" if r < -20 else "neutral"
    if el < 30:
        if pl < -30 and r > 20: return f"arm by the side, behind: hand to back pocket / tuck shirt ({rot} rot)"
        return f"arm at the side (walking, carrying) ({rot} rot)"
    if pl <= -40:
        return f"reach behind the body (2nd sleeve of a jacket, back pocket, seat-belt behind) ({rot} rot)"
    if -40 < pl < 20 and 50 <= el < 125:
        return f"arm out to the side, in/behind the frontal plane (reach sideways, T-pose, arm into a jacket sleeve, hand on a door frame) ({rot} rot)"
    if pl >= 110 and el < 130:
        return f"reach across the body (wash opposite shoulder/armpit, seat belt, opposite pocket) ({rot} rot)"
    if el >= 115:
        return ("hand behind the head (comb/wash back of hair, scratch back)" if H[0] < 0 else "reach overhead (high shelf, light bulb)") + f" ({rot} rot)"
    if el >= 70:
        if r < -40: return f"arm raised, forearm up: wave / throw / hands-up ({rot} rot)"
        if H[1] > 150: return f"hand to head (hat, hair, glasses) ({rot} rot)"
        return f"reach forward-side at shoulder height (door, shelf) ({rot} rot)"
    return f"mid reach (eat/drink, table reach) ({rot} rot)"


def plausible(pl, el):
    """rough active shoulder ROM envelope for 'everyday': extension (plane -90..-30) to 60 deg elevation, cross-body
    (plane 120..150) to 170-1.5*(plane-120) deg"""
    pl, el = np.asarray(pl, float), np.asarray(el, float)
    emax = np.where(pl <= -30, 60.0, np.where(pl < 0, 60 + (pl + 30) * 110 / 30, np.where(pl <= 120, 170.0, 170 - 1.5 * (pl - 120))))
    return el <= emax


# ------------------------------------------------------------------ body regions of the render skin
_REG = None
REGION_PARTS = {
    "neck": ["right sternocleidomastoid", "descending part of right trapezius", "right levator scapulae", "right scalenus", "cervical vertebra", "atlas", "axis"],
    "acromion / top of shoulder": ["right clavicle", "right supraspinatus", "right subclavius", "acromial part of right deltoid"],
    "chest": ["clavicular part of right pectoralis major", "abdominal part of right pectoralis major", "right costal cartilage", "sternum", "right pectoralis minor"],
    "axilla / lateral chest wall": ["right latissimus dorsi", "right teres major", "right serratus anterior", "right subscapularis"],
    "back over the scapula": ["right scapula", "right infraspinatus muscle", "spinal part of right deltoid", "transverse part of right trapezius", "right rhomboid", "right teres minor", "ascending part of right trapezius"],
    "front of shoulder (anterior deltoid)": ["clavicular part of right deltoid"],
}


def skin_regions():
    """per render-skin vertex: region name (arm-driven vertices = 'upper arm' / 'forearm+hand'; others by the nearest
    of the named structures at rest within 45 mm, else 'other trunk')"""
    global _REG
    if _REG is not None: return _REG
    import base64
    from scipy.spatial import cKDTree
    rig = BP._rig(); J = rig.J; V0 = rig.V0
    dec = lambda s, t: np.frombuffer(base64.b64decode(s), dtype=t)
    pts, lab = [], []
    names = list(REGION_PARTS)
    for p in J["parts"]:
        nm = p["name"]
        for ri, reg in enumerate(names):
            if any(k in nm for k in REGION_PARTS[reg]) and not nm.startswith("left"):
                P = dec(p["pos"], np.int16).reshape(-1, 3).astype(float) / 10; pts.append(P[:: max(1, len(P) // 4000)]); lab.append(np.full(len(pts[-1]), ri))
    pts = np.concatenate(pts); lab = np.concatenate(lab); d, j = cKDTree(pts).query(V0)
    reg = np.array([names[k] for k in lab[j]], dtype=object); reg[d > 45] = "other trunk"
    sk = rig.skin; W = np.zeros((sk["n"], 5)); np.add.at(W, (np.repeat(np.arange(sk["n"]), 4), sk["wi"].ravel()), sk["ww"].ravel())
    dom = W.argmax(1); reg[dom == 2] = "upper arm"; reg[dom >= 3] = "forearm/hand"
    _REG = dict(region=reg, dom=dom, W=W); return _REG


def jdump(obj, name):
    json.dump(obj, open(os.path.join(OUT, name), "w"), indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else float(o))
