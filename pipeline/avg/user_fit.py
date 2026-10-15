"""The user-fitted rig (BODY_FIT=user in body_pose.py): bound the rig's forearm and elbow by the user's own arm parts.

Data wins over the generic model: the user's forearm cuff, MIDDLE, the cuff screws and the elbow stack (TOP, thrust
washers, bearing, screws, magnet) were made for and are worn on the user's own arm, over a thin base layer, so the
user's skin lies at least LAYER mm inside every skin-facing surface of them. The generic rig (174.7 cm) does not: its
proximal forearm sits up to ~10 mm outside the forearm cuff's 49 mm inner radius (lateral side, where its flesh is
centred ~11 mm lateral of the elbow -> ulnar-head line the cuff is coaxial with) and its lateral elbow ~2 mm into the
elbow stack, in every pose. The user-fitted rig is the rig, except that each skin vertex is pulled radially towards the
limb axis just far enough to sit LAYER mm inside the user's parts - the smallest change to the rig that agrees with the
data (nothing moves where the rig already fits; nothing is invented where no user part bounds the skin).

Tables (written to user_fit.npz by this script; body_pose.py reads them):
  F  forearm-segment frame (the F group's rest frame): axis = rest elbow centre -> ulnar head, 0 deg = the elbow axis
     (lateral); parts MIDDLE, FOREARM CUFF, the countersunk cuff screws.
  H  humerus frame (the H group's rest frame): axis = GH -> elbow centre; the elbow stack (every user part in group H;
     BOTTOM is excluded: this project modifies it).
  bound(s, theta) = the smallest radius of any of those parts' surface along that ray (1 mm x 2 deg bins), then
  held MARGIN (8) mm past a part's edge (the rig's coarse skin triangles must not cut a part's rim), then relaxed at
  45 deg (R <= R_neighbour + distance: the tissue does not step at a cuff edge).
The user parts come from a design's exo.glb (all designs place them the same way: build_full_exo.py, fit_arm.py); the
script checks that against a second design.
    python3 pipeline/avg/user_fit.py [design id] [check design id]  -> pipeline/avg/user_fit.npz"""
import json, os, sys
import numpy as np, trimesh
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(HERE, "user_fit.npz")
DS, DTH = 1.0, 2.0                                    # bin sizes: mm along the axis, deg around it
CAP = 80.0                                            # bounds beyond this radius (mm) are dropped: wider than the rig's arm anywhere
SLOPE = 1.0                                           # 45 deg relaxation beyond a part's edge ...
MARGIN = float(os.environ.get("USER_FIT_MARGIN", 8.0))   # ... after holding the bound this far past the edge (mm): the rig's arm skin
                                                      # triangles are 6-8 mm (median) to 16-19 mm (p90) long, and a triangle
                                                      # that spans a part's rim must not cut through it


def frames(L):
    """(origin, axis, lateral) of the F and H tables in the rest frame (thorax mm, origin GH)"""
    E = np.array(L["elbow"]); EA = np.array(L["elbow_axis"]); EA = EA / np.linalg.norm(EA); UH = np.array(L["ulnar_head"])
    def fr(O, a): a = a / np.linalg.norm(a); u = EA - (EA @ a) * a; u /= np.linalg.norm(u); return O, a, u
    return dict(F=fr(E, UH - E), H=fr(np.zeros(3), E))


def polar(P, O, a, u):
    q = np.asarray(P, float) - O; s = q @ a; v = np.cross(a, u); x, y = q @ u, q @ v
    return s, np.degrees(np.arctan2(y, x)), np.hypot(x, y)


def user_parts(dd):
    sys.path.insert(0, os.path.join(REPO, "judge")); from common import load_parts
    own = {(p["group"], p["name"]) for p in json.load(open(os.path.join(dd, "parts_full.json")))["parts"] if p.get("material") == "user part"}
    return [(g, n, V, F) for g, n, V, F in load_parts(dd) if (g, n) in own and g in ("F", "H") and not n.startswith("BOTTOM")]


def table(parts, O, a, u, s_rng):
    s0, s1 = s_rng; ns = int((s1 - s0) / DS); nt = int(360 / DTH); R = np.full((ns, nt), np.inf)
    for g, n, V, F in parts:
        m = trimesh.Trimesh(V, F, process=False); k = int(np.clip(m.area / 0.1, 2000, 400000))
        P, _ = trimesh.sample.sample_surface(m, k, seed=1); P = np.r_[P, V]
        s, th, r = polar(P, O, a, u); i = np.floor((s - s0) / DS).astype(int); j = np.floor((th + 180) / DTH).astype(int) % nt
        ok = (i >= 0) & (i < ns); np.minimum.at(R, (i[ok], j[ok]), r[ok])
    raw = R.copy()
    ms, mt = int(round(MARGIN / DS)), None                                        # hold: min over neighbours within MARGIN mm
    H = R.copy()
    for di in range(-ms, ms + 1):
        Rs = np.roll(R, di, axis=0)
        if di > 0: Rs[:di] = np.inf
        elif di < 0: Rs[di:] = np.inf
        H = np.minimum(H, Rs)
    R = H.copy(); arc = np.where(np.isfinite(H), H, np.inf) * np.radians(DTH)            # mm per angular bin at that radius
    for dj in range(1, int(np.ceil(MARGIN / (40.0 * np.radians(DTH)))) + 1):
        for sg in (-1, 1):
            Rs = np.roll(H, sg * dj, axis=1); R = np.where(dj * np.roll(arc, sg * dj, axis=1) <= MARGIN, np.minimum(R, Rs), R)
    for _ in range(4):                                                            # chamfer: R <= R_neighbour + SLOPE * step
        for i in range(1, ns): R[i] = np.minimum(R[i], R[i - 1] + SLOPE * DS)
        for i in range(ns - 2, -1, -1): R[i] = np.minimum(R[i], R[i + 1] + SLOPE * DS)
        step = SLOPE * np.where(np.isfinite(R), R, 60.0) * np.radians(DTH)
        for j in range(nt): R[:, j] = np.minimum(R[:, j], R[:, j - 1] + step[:, j - 1])
        for j in range(nt - 1, -1, -1): R[:, j] = np.minimum(R[:, j], R[:, (j + 1) % nt] + step[:, (j + 1) % nt])
    R[R > CAP] = np.inf                                                           # no bound where it is wider than any limb
    return R, raw


def build(design="cad_r18_n3_s1392_1_f300", check="cad_r13_n4_s1343_1"):
    L = json.load(open(os.path.join(HERE, "body_mesh.json")))["landmarks"]; FR = frames(L)
    dd = os.path.join(REPO, "pipeline", "full-exo", "designs", design); parts = user_parts(dd)
    if check and os.path.isdir(os.path.join(REPO, "pipeline", "full-exo", "designs", check)):
        other = {(g, n): V for g, n, V, _ in user_parts(os.path.join(REPO, "pipeline", "full-exo", "designs", check))}
        dev = max((np.abs(V - other[(g, n)]).max() for g, n, V, _ in parts if (g, n) in other and other[(g, n)].shape == V.shape), default=None)
        print(f"user parts in {design} vs {check}: {sum((g, n) in other for g, n, _, _ in parts)} of {len(parts)} matched, max vertex deviation {dev} mm")
    out = dict(design=design, ds=DS, dth=DTH, slope=SLOPE, margin=MARGIN)
    for key, grp, rng in (("F", "F", (-40.0, 200.0)), ("H", "H", (240.0, 380.0))):
        O, a, u = FR[key]; R, raw = table([p for p in parts if p[0] == grp], O, a, u, rng)
        out.update({f"{key}_R": R.astype(np.float32), f"{key}_s0": rng[0], f"{key}_O": O, f"{key}_a": a, f"{key}_u": u})
        fin = np.isfinite(raw); s_idx = np.where(fin.any(1))[0]
        print(f"{key}: {', '.join(sorted({n[:24] for g, n, _, _ in parts if g == grp}))}")
        print(f"   bounded s {rng[0] + s_idx.min() * DS:.0f}..{rng[0] + (s_idx.max() + 1) * DS:.0f} mm, {fin.mean() * 100:.1f}% of bins hit, min radius {raw[fin].min():.1f} mm")
    np.savez_compressed(OUT, **out); print("wrote", OUT)


if __name__ == "__main__":
    build(*sys.argv[1:3])
