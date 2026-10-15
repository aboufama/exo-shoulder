"""Concept model: FLOATING-CENTRE 3R (id floating-centre-3r) - the champion spherical 3R (every joint axis through the
GH centre, tools/concept_baseline.py kinematics, parts and sampling) whose J1 hub sits on a passive 3-axis FLOAT on
the scapula base plate, with a RIGID arm member on the user's cuff (no cuff slides).

Chain (scapula handler -> user's upper-arm cuff):
    base plate on the handler --[X slide]--[Y slide] (tangent plane, normal = J1's axis b) --[normal slide along b]-->
    J1 lower member --J1 R--> link 1 --J2 R--> link 2 --J3 R--> arm member, rigid on the cuff.
DOF: 3 ACTIVE (J1-J3) + 3 PASSIVE (the float). A spherical 3R with concurrent axes, rigid on the arm, is mobile only
if its centre c sits on the arm's rotation centre; the float's 3 translations are exactly the 3 equations c = GH, so
the serial chain (3 P + 3 R = 6) matches the cuff's 6 DOF relative to the handler one to one: no spare coordinate,
the float is set by closure (it cannot sag on its own: gravity on the chain is carried through the cuff by the arm).

Parts at real size (mm) - the parent's parts exactly as tools/concept_baseline.py (O20 hubs r 10 at r_ref 70, 6.15
per stacked level, 8 x 3 straps on the great circles, the 25 deg humerus-fixed neck; profiles = p-th percentile of
the outermost skin radius under each sample over the valid poses + 2 mm) plus what the float adds:
  * float LOWER PLATE (on the handler, fixed in the scapula frame): a disc about b of lateral radius
    plate_r = hub_r + 4 (moving top plate around the hub) + trav_t (tangent travel). Its underside is contoured to
    the skin like a link (p-th percentile + clear, sampled at the baseline's hub density: 2.5 mm at r_ref 70), its
    upper face is the flat slide face normal to b at h_s = max(underside height along b) + t_low (1.5).
  * the XY stage on it: h_xy (5.5: two V-groove ball slides on a shared middle plate - 0.8 gap + 2.2 plate + 0.8 gap
    + 1.7 top plate, 2 mm balls; a catalogue crossed-roller XY table is ~12-16 mm), occupying the plate's footprint.
  * the NORMAL slide: J1's hub rests n_down + 0.5 above the XY top, so it can descend n_down along b.
  -> J1's hub underside (the O20 skin face) at L_j = h_s + h_xy + n_down + 0.5 along b (the spec's '5 mm raise' is
     t_low + h_xy + n_down + 0.5 ~ 14 mm once the travel the slip law needs is in; both are swept).
  * link 1 over the float footprint (lateral <= plate_r + 1, optionally + trav_t) clears the XY top by 1 mm with J1
    at its lowest: underside height along b >= h_s + h_xy + n_down + 1.
Metal sampled: as the baseline (strap / hub undersides at its density) + the lower plate's underside.
Taken iff (per pose): the parent's closure on its branch with the evaluator's 10 deg fold margin; along each fit clip
at full rate no joint steps > 25 deg between consecutive frames (a flip = that frame not followed); no metal of a part
not adjacent to the float (link 1, hub 2, link 2, hub 3, neck) inside the float's volume (footprint + 1 mm, below the
XY top + 1 mm), with the float displaced by the pose's slip; with pp=1 also no two non-adjacent chain parts closer
than 1 mm (radial slabs: straps 3 mm, hubs 12.25 mm); with slip, the float inside its travel; then the bench's
contact rule.

SLIP EXTENSION (the rig has no GH-vs-handler translation): judge/base_slip.py's error angles th (about the ISB scapula
axes Xs, Ys, Zs) and slip d for each pose's (plane, elevation), lever r = base_slip.lever()[0]; ISB -> bench scapula
frame: Zs = unit(0.5, 0, 0.87), Ys = y, Xs = Ys x Zs. delta = (Rx(th0) Ry(th1) Rz(th2) - I) r + d t_hat (t_hat
superior), all + signs ('central'), or per pose the worst of the 8 sign patterns ('high'). Each sample is classed by
the skin it rides (its skin point's nearest posed vertex in BP.ARMV = arm skin; else scapula / trunk skin, which slips
with the handler). mode 'parent' (rigid base + cuff slides): chain samples over arm skin +delta, others 0; mode
'float': the lower plate 0, chain samples over scapula / trunk skin -delta, over arm skin 0, and the pose is not taken
if the float leaves its travel (|delta tangent| > trav_t, delta along b outside [-n_up, n_down]).

    OMP_NUM_THREADS=1 nice -n 5 python3 docs/concepts/models/floating-centre-3r.py [check|sweep|sketch|slipstats]
"""
import json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools")); sys.path.insert(0, os.path.join(REPO, "judge"))
import concept_bench as CB                                   # noqa: E402
import concept_baseline as BL                                # noqa: E402
import base_slip as BS                                       # noqa: E402
BP = CB.BP

ID = "floating-centre-3r"; NAME = "Floating-centre 3R: the spherical chain on a closure-set 3-axis float under J1"
D2R = math.pi / 180
SWEEP_JSON = os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json")
SING, JUMP = 10.0, 25.0                   # fold margin (deg), largest joint step between full-rate frames (deg)
HUB_STACK = 12.25                         # O20 v5 hub: skin face F to the cap crown (docs/HARDWARE.md)
R_REF = 70.0                              # the baseline's nominal radius of its direction grids

# parents: the top band / CAD 3R picks (pipeline/conformal/band_cad/inputs/*.json, kinematics only)
PARENTS = {
    "r20_s1414_4": dict(az=2.4305071427308924, el=80.67633718429899, a=[76.90180446920043, 66.74921235407174], w=[86.32769021001913, 21.829657347343378], branch=-1),
    "r18_s1392_1": dict(az=32.55159237005438, el=80.5631251310032, a=[77.40737955825345, 81.44799921589232], w=[71.38254048198503, 4.778729451604692], branch=-1),
    "r20_s1414_0": dict(az=14.334325229499703, el=82.3438225055715, a=[73.14527820556887, 66.11369579887129], w=[85.02889058725152, 26.032150845040853], branch=-1),
    "r20_s1411_2": dict(az=77.7131348211075, el=85.10998577949123, a=[76.60886566496094, 77.72756967198949], w=[69.22974128541614, 4.398159892313142], branch=-1),
    "r17_s1381_0": dict(az=21.572004256164064, el=74.65677070921748, a=[76.6942876679089, 77.02221721376192], w=[72.53676340483199, 19.169823974377792], branch=-1),
    "r18_s1394_1": dict(az=57.9420534734179, el=78.4471717690747, a=[69.3505972727849, 80.165684701384], w=[66.87006930589727, 4.083931436659226], branch=-1),
}
PARAMS = dict(parent="r20_s1414_4", mode="float", slip="none", pct=95.0, hub_r=10.0, stack=3.15, t_link=3.0, width=8.0, clear=2.0,
              neck_deg=25.0, trav_t=20.0, n_down=6.8, n_up=8.0, h_xy=5.5, t_low=1.5, cover=1, pp=1)
SWEEP = dict(parent=list(PARENTS), pct=[60, 70, 80, 90, 95, 98, 100], trav_t=[8, 12, 16, 20], n_down=[0, 4, 6.8], h_xy=[3.5, 5.5, 8],
             cover=[0, 1], slip=["none", "central", "high"], mode=["parent", "float"])


def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-12)
def now(): return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
def plog(*a): print(*a, flush=True)


# ---- slip law (judge/base_slip.py, mapped to the bench scapula frame) ----------------------------------------------------
ZS = unit(np.array([0.5, 0.0, 0.87])); YS = np.array([0.0, 1.0, 0.0]); XS = np.cross(YS, ZS)
ISB2S = np.c_[XS, YS, ZS]


def slip_delta(poses, law="central", t_hat=YS):
    """(n, 3) handler-vs-bone offset of the chain centre in the bench SCAPULA frame for each pose (plane, elev)"""
    P = np.array([[p["plane"], p["elev"]] for p in poses]); r = ISB2S @ BS.lever()[0]
    th, d = BS.angles(P, "central" if law == "central" else "high"); th = th * D2R; out = np.zeros((len(P), 3))
    signs = [np.ones(3)] if law == "central" else [np.array(s) for s in np.array(np.meshgrid([-1, 1], [-1, 1], [-1, 1])).T.reshape(-1, 3)]
    for k in range(len(P)):
        best = None
        for s in signs:
            R = BS.rot(XS, s[0] * th[k, 0]) @ BS.rot(YS, s[1] * th[k, 1]) @ BS.rot(ZS, s[2] * th[k, 2])
            v = (R - np.eye(3)) @ r + d[k] * t_hat
            if best is None or np.linalg.norm(v) > np.linalg.norm(best): best = v
        out[k] = best
    return out


# ---- kinematics + continuity (baseline pins(); joint angles for the branch-flip check) -----------------------------------
def kin_S(d, HG):
    A = [x * D2R for x in d["a"]]; b = BL.bvec(d["az"], d["el"]); W0 = BL.w_dir(*d["w"]); n = len(HG)
    p1 = np.ascontiguousarray(np.broadcast_to(b, (n, 3))); p3 = HG @ W0
    p2, ok = BL.circ_int(p1, A[0], p3, A[1], float(d["branch"])); ok = ok & BL.tri_ok(p1, p3, A[0], A[1], SING * D2R)

    def ang(ax, a, c):
        a_ = a - (a * ax).sum(-1, keepdims=True) * ax; c_ = c - (c * ax).sum(-1, keepdims=True) * ax
        return np.arctan2((np.cross(a_, c_) * ax).sum(-1), (a_ * c_).sum(-1))
    r1 = np.broadcast_to(unit(np.cross(b, [1.0, 0.0, 0.0])), (n, 3)); hv = HG @ unit(np.cross(W0, [0.0, 1.0, 0.0]))
    return ok, np.stack([ang(p1, r1, p2), ang(p2, p1, p3), ang(p3, p2, hv)], 1)


def continuity(d, Z, idx):
    names = list(Z["NAMES"]); cid = Z["CID"]; good = {}; flips = 0
    for nm in CB.FIT:
        ii = np.nonzero(cid == names.index(nm))[0]; ii = ii[np.argsort(Z["FI"][ii], kind="stable")]
        ok, q = kin_S(d, Z["HG"][ii].astype(float)); prev = None
        for j, gi in enumerate(ii):
            g = bool(ok[j])
            if g and prev is not None:
                dq = np.degrees(np.abs((q[j] - q[prev] + np.pi) % (2 * np.pi) - np.pi))
                if dq.max() > JUMP: g = False; flips += 1
            good[int(gi)] = g; prev = j if ok[j] else None
    return np.array([good.get(int(g), True) for g in idx]), flips


# ---- per parent precompute: directions, skin radii under every sample, skin class ---------------------------------------
class Pre:
    PARTS = ("link1", "link2", "neck", "hub1", "hub2", "hub3", "plate")

    def __init__(self, B, parent, hub_r=10.0, width=8.0, neck_deg=25.0, plate_max=40.0, log=plog, limit=None):
        t0 = time.time(); Z = CB._poses_all(); self.B = B; d = dict(PARENTS[parent], sing_deg=SING); self.d = d
        HG = Z["HG"][B.idx].astype(float); RS = Z["RS"][B.idx].astype(float); self.RS = RS; n = len(B.idx)
        Pt, ok, harm = BL.pins(d, HG, RS)
        cont, flips = continuity(d, Z, B.idx); self.ok_kin = ok.copy(); self.cont = cont; self.flips = flips
        self.ok = ok & cont
        if limit is not None: self.ok &= limit
        self.Pt = Pt; A = [x * D2R for x in d["a"]]; self.A = A
        self.bT = Pt[:, 0]                                    # J1 axis b in the thorax frame per pose (= RS b)
        D = {}
        D["link1"] = BL.arc_dirs(Pt[:, 0], Pt[:, 1], A[0], width=width); D["link2"] = BL.arc_dirs(Pt[:, 1], Pt[:, 2], A[1], width=width)
        ng = neck_deg * D2R
        nk_v = unit(np.cos(ng) * Pt[:, 2] + np.sin(ng) * unit(harm - (harm * Pt[:, 2]).sum(-1, keepdims=True) * Pt[:, 2]))
        D["neck"] = BL.arc_dirs(Pt[:, 2], nk_v, ng, width=width)
        self.ns = {k: D[k].shape[1] for k in ("link1", "link2", "neck")}
        for k in range(3): D[f"hub{k + 1}"] = BL.disc_dirs(Pt[:, k], hub_r)
        # float lower plate: directions on the hub's angular grid out to plate_max lateral at the plate's height
        i0 = int(np.argmax(self.ok)); h0 = float(BL.skin_radius(B, i0, Pt[i0, 0][None])[0]) + 4.0; self.h0 = h0
        rad = plate_max * R_REF / h0
        D["plate"] = BL.disc_dirs(Pt[:, 0], rad, r_ref=R_REF, step=2.5)
        self.plate_lat = h0 * np.tan(np.arccos(np.clip((D["plate"][i0] * Pt[i0, 0]).sum(-1), -1, 1)))   # lateral mm at h0
        self.D = {k: v.reshape(n, -1, 3) for k, v in D.items()}
        # link-1 samples: angle from b (fixed in link 1, which turns about b)
        self.l1_alpha = np.arccos(np.clip((self.D["link1"][i0] * Pt[i0, 0]).sum(-1), -1, 1))
        self.R = {k: np.zeros(v.shape[:2]) for k, v in self.D.items()}; self.arm = {k: np.zeros(v.shape[:2], bool) for k, v in self.D.items()}
        valid = np.nonzero(self.ok)[0]
        for i in valid:
            allD = np.concatenate([self.D[k][i] for k in self.PARTS]); rr = BL.skin_radius(B, int(i), allD)
            V = np.asarray(B.skin(int(i))[0]); near = np.linalg.norm(V, axis=1) < 300
            tree = cKDTree(V[near]); armv = np.asarray(BP.ARMV)[near]
            _, j = tree.query(allD * rr[:, None]); cls = armv[j] & (rr > 0)
            o = 0
            for k in self.PARTS:
                m = self.D[k].shape[1]; self.R[k][i] = rr[o:o + m]; self.arm[k][i] = cls[o:o + m]; o += m
        self.valid = valid; self.slip = {}
        log(f"  pre {parent}: {len(valid)}/{n} poses valid (fold {int((~ok).sum())}, flips {int((ok & ~cont).sum())} bench / {flips} full-rate), "
            f"plate h0 {h0:.1f} mm, arm-skin share link1 {self.arm['link1'][valid].mean():.2f} link2 {self.arm['link2'][valid].mean():.2f} "
            f"neck {self.arm['neck'][valid].mean():.2f} hub2 {self.arm['hub2'][valid].mean():.2f} hub3 {self.arm['hub3'][valid].mean():.2f}, "
            f"{time.time() - t0:.0f} s ({B.mode})")

    def delta(self, law):
        """(n, 3) slip offset in the THORAX frame per bench pose"""
        if law not in self.slip:
            dS = slip_delta(self.B.poses, law); self.slip[law] = np.einsum("pij,pj->pi", self.RS, dS)
        return self.slip[law]


# ---- one configuration --------------------------------------------------------------------------------------------------
def design(pre, prm):
    """fixed part shapes (radial profiles) for the configuration: {part: (radius per sample, slab thickness)} + float"""
    v = pre.valid; p = prm["pct"]; up = prm["stack"] + prm["t_link"]
    prof = {k: np.percentile(pre.R[k][v], p, axis=0) + prm["clear"] for k in pre.PARTS}
    for k in ("hub1", "hub2", "hub3"): prof[k] = np.full_like(prof[k], prof[k].max())
    off = dict(link1=0.0, link2=up, neck=2 * up, hub1=0.0, hub2=0.0, hub3=up, plate=0.0)
    fl = None
    if prm["mode"] == "float":
        plate_r = prm["hub_r"] + 4.0 + prm["trav_t"]
        sel = pre.plate_lat <= plate_r + 1e-6
        alpha = np.arccos(np.clip((pre.D["plate"][pre.valid[0]] * pre.bT[pre.valid[0]]).sum(-1), -1, 1))
        under = prof["plate"]; h_s = float((under * np.cos(alpha))[sel].max()) + prm["t_low"]
        top = h_s + prm["h_xy"]; L_j = top + prm["n_down"] + 0.5
        a_hub = math.atan(prm["hub_r"] / R_REF)
        prof["hub1"] = np.full_like(prof["hub1"], max(prof["hub1"].max(), L_j / math.cos(a_hub)))
        # link 1 over the float footprint clears the XY top by 1 mm with J1 at its lowest
        lat = L_j * np.tan(pre.l1_alpha); cov = plate_r + 1 + (prm["trav_t"] if prm["cover"] else 0)
        need = (top + prm["n_down"] + 1.0) / np.cos(np.minimum(pre.l1_alpha, 1.4))
        prof["link1"] = np.where(lat <= cov, np.maximum(prof["link1"], need), prof["link1"])
        fl = dict(plate_r=plate_r, sel=sel, h_s=h_s, top=top, L_j=L_j)
    hub_of = {"link1": ("hub1", "hub2"), "link2": ("hub2", "hub3"), "neck": ("hub3", None)}
    for nm, (h0, h1) in hub_of.items():                      # link ends sit on their hubs (distal link on top) - baseline
        n_s = pre.ns[nm]; nc = prof[nm].size // n_s; pr = prof[nm].reshape(n_s, nc).copy(); end = max(2, n_s // 6)
        pr[:end] = np.maximum(pr[:end], prof[h0].max() + off[nm] - off[h0])
        if h1: pr[-end:] = np.maximum(pr[-end:], prof[h1].max() + off[nm] - off[h1])
        prof[nm] = pr.reshape(-1)
    parts = [k for k in pre.PARTS if k != "plate" or fl is not None]
    th = dict(link1=prm["t_link"], link2=prm["t_link"], neck=prm["t_link"], hub1=HUB_STACK, hub2=HUB_STACK, hub3=HUB_STACK)
    return dict(prof=prof, off=off, fl=fl, parts=parts, th=th)


# non-adjacent chain pairs (members: hub1+lower J1 | link1 (J1 upper, J2 lower) | hub2 | link2 | hub3 | neck)
NONADJ = [("hub1", "link2"), ("hub1", "hub3"), ("hub1", "neck"), ("link1", "hub3"), ("link1", "neck"), ("hub2", "neck")]


def pp_clash(R0, Dirs, th):
    """non-adjacent chain parts closer than 1 mm: footprints overlapping (directions within 2 mm at the radius - the
    sample grids are ~2.6-3.2 mm apart) and radial slabs [r, r + thickness] within 1 mm"""
    for a, b in NONADJ:
        ta = cKDTree(Dirs[a]); r = 2.0 / max(80.0, float(np.median(R0[a])))
        hits = ta.query_ball_point(Dirs[b], r)
        for jb, js in enumerate(hits):
            if not js: continue
            ra = R0[a][js]; rb = R0[b][jb]
            if np.any((rb < ra + th[a] + 1.0) & (ra < rb + th[b] + 1.0)): return f"{a}-{b}"
    return None


def pose_metal(pre, des, prm, i, dl=None):
    """metal of bench pose i for a configuration: ({part: (k, 3) points}, None) or (None, reason not taken)"""
    fl = des["fl"]
    if not pre.ok[i]: return None, ("fold" if not pre.ok_kin[i] else "flip")
    bT = pre.bT[i]; e = np.zeros(3) if dl is None else dl[i]; slip = prm["slip"] != "none"
    pts = {}; Dirs = {}; R0 = {}
    for k in des["parts"]:
        Dk = pre.D[k][i]; prof = des["prof"][k]; arm = pre.arm[k][i]
        if k == "plate": Dk = Dk[fl["sel"]]; prof = prof[fl["sel"]]; arm = arm[fl["sel"]]
        r0 = prof + des["off"][k]; X = Dk * r0[:, None]
        if slip:                                             # offset relative to the skin each sample rides
            if prm["mode"] == "parent": X = X + np.where(arm[:, None], e[None], 0.0)
            elif k != "plate": X = X - np.where(arm[:, None], 0.0, e[None])
        pts[k] = X; Dirs[k] = Dk; R0[k] = r0
    if fl is not None and slip:                              # float travel: J1 moves by -delta relative to the plate
        en = -float(e @ bT); et = float(np.linalg.norm(-e - en * bT))
        if et > prm["trav_t"] + 1e-9 or en < -prm["n_down"] - 1e-9 or en > prm["n_up"] + 1e-9: return None, "travel"
    if fl is not None:                                       # chain parts not adjacent to the float vs its volume
        ech = -e if slip else np.zeros(3)                    # chain displacement relative to the plate
        for k in ("link1", "hub2", "link2", "hub3", "neck"):
            Y = Dirs[k] * R0[k][:, None] + ech[None]
            hgt = Y @ bT; lat = np.linalg.norm(Y - hgt[:, None] * bT[None], axis=1)
            if np.any((lat <= fl["plate_r"] + 1.0) & (hgt < fl["top"] + 1.0 - 1e-6) & (hgt >= fl["h_s"] - 25.0)): return None, "float-clash " + k
    if prm["pp"]:
        c = pp_clash(R0, Dirs, des["th"])
        if c: return None, "pp " + c
    return pts, None


_BOUND = {}
def bind(B, pre, prm):
    """make metal(pose, frames, params) answer for this bench / precompute (the bench API of the swarm)"""
    _BOUND.update(B=B, pre=pre, prm=dict(prm), des=design(pre, prm),
                  dl=pre.delta(prm["slip"]) if prm["slip"] != "none" else None)


def metal(pose, frames, params):
    """(k, 3) metal sample points (thorax frame, mm) of a bench pose for configuration params, or None if not taken.
    The pose is located in the bound bench (bind(); the chain needs the pose file's scapula / humerus rotations and the
    profiles need every valid pose, so a lone pose cannot be evaluated in isolation)."""
    B = _BOUND["B"]
    if dict(params) != _BOUND["prm"]: bind(B, _BOUND["pre"], dict(PARAMS, **params))
    i = next(j for j, p in enumerate(B.poses) if p == pose)
    pts, _ = pose_metal(_BOUND["pre"], _BOUND["des"], _BOUND["prm"], i, _BOUND["dl"])
    return None if pts is None else np.concatenate(list(pts.values()))


def evaluate(B, pre, prm, details=False):
    des = design(pre, prm); fl = des["fl"]; B.reset(); why = {}; keep = {}
    dl = pre.delta(prm["slip"]) if prm["slip"] != "none" else None
    for i in range(len(B.idx)):
        pts, w = pose_metal(pre, des, prm, i, dl)
        if pts is None: why[w] = why.get(w, 0) + 1; B.record(i, None); continue
        d = B.record(i, np.concatenate(list(pts.values())))
        if details: keep[i] = (pts, d)
        if float(d.min()) < 0: why["contact"] = why.get("contact", 0) + 1
    r = B.report(); r["why"] = why
    if fl is not None: r["float"] = {k: round(float(v), 1) for k, v in fl.items() if k in ("plate_r", "h_s", "top", "L_j")}
    r["hub1_r"] = round(float(des["prof"]["hub1"].max()), 1)
    return (r, keep) if details else r


# ---- sweep bookkeeping -----------------------------------------------------------------------------------------------
class Runner:
    def __init__(self, B, fresh=True, log=plog):
        self.B = B; self.log = log; self.pres = {}
        self.entries = [] if fresh or not os.path.exists(SWEEP_JSON) else json.load(open(SWEEP_JSON))

    def pre(self, prm):
        key = (prm["parent"], prm["hub_r"], prm["width"], prm["neck_deg"])
        if key not in self.pres:
            if len(self.pres) > 2: self.pres.pop(next(iter(self.pres)))
            self.pres[key] = Pre(self.B, prm["parent"], prm["hub_r"], prm["width"], prm["neck_deg"], log=self.log)
        return self.pres[key]

    def run(self, over, tag=""):
        prm = dict(PARAMS); prm.update(over)
        for e in self.entries:
            if e["params"] == prm: return e
        t = time.time(); r = evaluate(self.B, self.pre(prm), prm)
        e = dict(k=len(self.entries), t=now(), params=prm, inband14=r["inband14"], inband10=r["inband10"], reach=r["reach"],
                 follow=r["follow"], contact=r["contact"], gap=r["gap"], why=r["why"], float=r.get("float"), hub1_r=r["hub1_r"], tag=tag)
        self.entries.append(e)
        os.makedirs(os.path.dirname(SWEEP_JSON), exist_ok=True)
        json.dump(self.entries, open(SWEEP_JSON + ".tmp", "w"), indent=0); os.replace(SWEEP_JSON + ".tmp", SWEEP_JSON)
        short = {k: v for k, v in prm.items() if v != PARAMS[k]}
        self.log(f"[{e['k']:3d}] gap {e['gap']:6.2f} ib14 {e['inband14']:.3f} ib10 {e['inband10']:.3f} reach {e['reach']:.3f} follow {e['follow']:.3f} "
                 f"contact {e['contact']:.3f} {short} {tag} ({time.time() - t:.1f} s) {e['why']} {e['float']}")
        return e

    def best(self, filt=lambda e: True):
        c = [e for e in self.entries if filt(e)]; return min(c, key=lambda e: e["gap"]) if c else None


def is_float_plain(e): return e["params"]["mode"] == "float" and e["params"]["slip"] == "none"


def sweep(B):
    R = Runner(B)
    # A: the parent itself on this model (no float, no slip, baseline rules + the part-part check on/off) vs the float
    for pct in (80, 90, 95, 98, 100):
        R.run(dict(mode="parent", pct=pct, pp=0), "A parent, baseline rules")
        R.run(dict(mode="parent", pct=pct), "A parent + pp check")
        R.run(dict(pct=pct), "A float, honest stack")
    # B: float stack and travel at the best percentile
    pbest = R.best(is_float_plain)["params"]["pct"]
    for h_xy in (3.5, 5.5, 8.0):
        for n_down in (0.0, 4.0, 6.8):
            for trav in (8.0, 12.0, 16.0, 20.0):
                R.run(dict(pct=pbest, h_xy=h_xy, n_down=n_down, trav_t=trav), "B stack/travel")
    for cover in (0,): R.run(dict(pct=pbest, cover=cover), "B cover")
    # C: parents
    for par in PARENTS:
        for pct in (90, 95, 98):
            R.run(dict(parent=par, mode="parent", pct=pct), "C parents (parent)")
            R.run(dict(parent=par, pct=pct), "C parents (float)")
    # D: the slip extension - (a) parent with cuff slides vs (b) float, central and high laws
    cand = sorted({e["params"]["parent"] for e in R.entries if e["tag"].startswith("C")},
                  key=lambda p: R.best(lambda e: e["params"]["parent"] == p and is_float_plain(e))["gap"])[:2]
    for par in cand:
        for law in ("central", "high"):
            for pct in (90, 95, 98, 100):
                R.run(dict(parent=par, mode="parent", slip=law, pct=pct), "D slip (a) parent")
                for trav, nd in ((12.0, 4.0), (20.0, 6.8)):
                    R.run(dict(parent=par, slip=law, pct=pct, trav_t=trav, n_down=nd), "D slip (b) float")
    plog("BEST float plain", json.dumps(R.best(is_float_plain)))
    plog("BEST parent plain", json.dumps(R.best(lambda e: e["params"]["mode"] == "parent" and e["params"]["slip"] == "none")))
    for law in ("central", "high"):
        plog(f"BEST float {law}", json.dumps(R.best(lambda e: e["params"]["mode"] == "float" and e["params"]["slip"] == law)))
        plog(f"BEST parent {law}", json.dumps(R.best(lambda e: e["params"]["mode"] == "parent" and e["params"]["slip"] == law)))
    return R


def check(B, prm=None, limit=None):
    prm = dict(PARAMS, **(prm or {})); pre = Pre(B, prm["parent"], log=plog, limit=limit)
    for over in (dict(mode="parent", pp=0), dict(mode="parent"), dict(), dict(slip="central"), dict(mode="parent", slip="central")):
        p2 = dict(prm, **over); r, keep = evaluate(B, pre, p2, details=True)
        plog(json.dumps(over), json.dumps(r, default=str))
        taken = list(keep)
        if not taken: continue
        el = np.array([B.poses[i]["elev"] for i in taken]); pl = np.array([B.poses[i]["plane"] for i in taken])
        named = dict(rest=taken[int(np.argmin(el))], overhead=taken[int(np.argmax(el))], across=taken[int(np.argmax(pl))])
        bb = [i for i in taken if B.clip[i] == "Reach back pocket"]
        if bb: named["behind back"] = bb[len(bb) // 2]
        for nm, i in named.items():
            pts, d = keep[i]; o = 0; s = []
            for k, X in pts.items():
                dk = d[o:o + len(X)]; o += len(X); s.append(f"{k} {np.median(dk):.1f}/{dk.min():.1f}")
            plog(f"   {nm:12s} plane {B.poses[i]['plane']:.0f} elev {B.poses[i]['elev']:.0f}: in band 14 {np.mean((d >= 2) & (d <= 14)):.2f}  "
                 f"(median/min mm) " + ", ".join(s))
    return pre


def slipstats(B):
    Z = CB._poses_all(); pre_b = {}
    for law in ("central", "high"):
        dS = slip_delta(B.poses, law)
        for par, d in PARENTS.items():
            b = BL.bvec(d["az"], d["el"]); n = dS @ b; t = np.linalg.norm(dS - n[:, None] * b, axis=1)
            plog(f"{law:8s} {par}: |delta| max {np.linalg.norm(dS, axis=1).max():.1f}, tangent max {t.max():.1f} (p90 {np.percentile(t, 90):.1f}), "
                 f"along b min {n.min():.1f} max {n.max():.1f}; tangent > 12: {np.mean(t > 12):.3f}, > 16: {np.mean(t > 16):.3f}")


def sketch(B, prm, path):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    prm = dict(PARAMS, **prm); pre = Pre(B, prm["parent"], log=plog); r, keep = evaluate(B, pre, prm, details=True)
    taken = [i for i in keep if float(np.min(B.res[i])) >= 0]
    rest = min(taken, key=lambda i: B.poses[i]["elev"]); top = max(taken, key=lambda i: B.poses[i]["elev"])
    cols = dict(plate="#d1495b", hub1="#edae49", hub2="#e07a5f", hub3="#00798c", link1="#66a182", link2="#8d6a9f", neck="#30638e")
    fig = plt.figure(figsize=(12, 5.6))
    for k, i in enumerate((rest, top)):
        ax = fig.add_subplot(1, 2, k + 1, projection="3d"); V = np.asarray(B.skin(i)[0])
        near = V[np.linalg.norm(V, axis=1) < 150][::6]; ax.scatter(near[:, 2], near[:, 0], near[:, 1], s=0.3, c="#bbbbbb", alpha=0.3)
        pts, d = keep[i]
        for nm, X in pts.items(): ax.scatter(X[:, 2], X[:, 0], X[:, 1], s=1.0, c=cols[nm], label=nm)
        p = B.poses[i]; ax.set_title(f"{'rest' if k == 0 else 'highest pose taken'}: plane {p['plane']:.0f}, elev {p['elev']:.0f}, axial {p['axial']:.0f}", fontsize=9)
        ax.view_init(elev=22, azim=-50 if k == 0 else -30); ax.set_xlabel("z lateral"); ax.set_ylabel("x anterior"); ax.set_zlabel("y up")
        ax.set_box_aspect((1, 1, 1)); ax.set_xlim(-80, 120); ax.set_ylim(-110, 90); ax.set_zlim(-90, 110)
        if k == 0: ax.legend(fontsize=7, markerscale=5, loc="upper left")
    fig.suptitle(f"{ID}: parent {prm['parent']}, p{prm['pct']:.0f}, float +-{prm['trav_t']:.0f} / {prm['n_down']} mm, XY {prm['h_xy']} mm; "
                 f"gap {r['gap']}, in band 14 {r['inband14']}, reach {r['reach']}, follow {r['follow']}", fontsize=9)
    fig.tight_layout(); fig.savefig(path, dpi=110); plt.close(fig); return r


def dev_bench(n_clip=60, n_ws=160):
    """the bench, on the partial cache while it builds (poses whose grid is written), else as is"""
    B = CB.Bench(n_clip=n_clip, n_ws=n_ws); lim = None
    if B.grid is None:
        tmp = os.path.join(CB.CACHE, B.key, "grid.tmp.npy")
        if os.path.exists(tmp):
            g = np.load(tmp, mmap_mode="r"); B.grid = g; B.mode = "fast-partial"; lim = np.array([g[j, 0, 0, 0] != 0 for j in range(len(g))])
    return B, lim


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    if mode == "dev":
        B, lim = dev_bench(); plog("bench", B.mode, len(B.idx), "written", None if lim is None else int(lim.sum()))
        check(B, json.loads(sys.argv[2]) if len(sys.argv) > 2 else None, limit=lim)
    elif mode == "check":
        B = CB.Bench(n_clip=60, n_ws=160); plog("bench", B.mode, len(B.idx)); check(B, json.loads(sys.argv[2]) if len(sys.argv) > 2 else None)
    elif mode == "slipstats":
        B = CB.Bench(n_clip=60, n_ws=160); slipstats(B)
    elif mode == "sweep":
        B = CB.Bench(n_clip=60, n_ws=160); plog("bench", B.mode, len(B.idx)); sweep(B)
    elif mode == "sketch":
        B = CB.Bench(n_clip=60, n_ws=160); prm = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
        plog(sketch(B, prm, os.path.join(REPO, "docs", "concepts", "img", f"{ID}.png")))
