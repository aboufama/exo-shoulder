"""Build the exo viewer's body from BodyParts3D (DBCLS, CC BY-SA 2.1 JP): real bone, muscle and skin meshes, rigged.

Frame (as anatomy.js / the searches): thorax, x anterior, y up, z right, origin = right glenohumeral centre, mm, scaled
so the shoulder-to-elbow length matches the exo (411 mm, or H_LEN).
Segments: 0 thorax (incl. left arm, legs, head), 1 right scapula, 2 right humerus, 3 right ulna (elbow flexion),
4 right radius + hand (flexion + pronation). The right clavicle blends thorax -> scapula along its length.

Legacy fields (unchanged, read by the collision-map tools): every part's pos/idx, the skin's 2-bone linear-blend
weights wi/ww and briefs mask, the muscles' wi/ww. The viewer (body.js) uses the newer rig fields instead:
  * skin render mesh (rpos/ridx/rsrc): the outer shell of the skin only (BodyParts3D's skin is a 3 mm solid), the axilla
    unzipped (the hanging arm is fused to the chest wall below the armpit; rig.unzip_axilla) with a relaxed shape for
    raised arms (rlxi/rlxd), and a full-resolution head joined on a neck seam (y = Y_CUT); head features (feat: hair,
    hair height, lips, flush; J.head: eyes, eyebrow lines) and an eyeball part (cls "eye", appended last).
  * weights: harmonic (exact sparse solve) from bone seeds plus the weights of the tissue under the skin; fan muscles
    over the shoulder weighted along their fibres; 4 influences (w4i/w4w) and centres of rotation (cor) for
    centre-of-rotation skinning.
  * muscle models (mdl): spindle muscles (centreline, belly profile, bowstring/insertion for the length change) and flat
    muscles (fibre probes, superficial side, thickness); the skin binds to the muscle under it (foj/fov/fow).
See rig.py for the methods.

    python3 build_body.py      -> ../body_mesh.json (+ body_rig.npz for the collision grids)
"""
import base64, json, math, os, re, sys
import numpy as np
from scipy.spatial import cKDTree
import pyfqmr
import bp3d
import rig

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache"); os.makedirs(CACHE, exist_ok=True)
H_LEN = float(os.environ.get("H_LEN", 411.0))          # shoulder-to-elbow (mm); 411 = the original exo, 325 = average adult (1.75 m)
RATIO = dict(muscle=0.10, bone=0.20, cartilage=0.15, skin=0.30)
DEEP = re.compile(r"intercostal|transversus|rotator|interspinal|intertransvers|levatores|multifidus|semispinalis|spinalis|longus colli|longus capitis|pterygoid|lumbrical|interosse|quadratus|obturator|gemellus|piriformis|psoas|iliacus|levator ani|coccygeus|iliococcygeus|pubococcygeus|puborectalis|diaphragm|subscapularis|serratus posterior|scalenus", re.I)
# muscle-tendon architecture (Holzbaur, Murray & Delp 2005 upper-limb model, approximate): optimal fibre length,
# tendon slack length (mm), pennation (deg); activation group: 1 shoulder (carries the arm), 2 elbow flexor, 3 extensor
ARCH = [
    (r"clavicular part of right deltoid", 98, 93, 22, 1), (r"acromial part of right deltoid", 108, 110, 15, 1), (r"spinal part of right deltoid", 137, 38, 18, 1),
    (r"right supraspinatus", 68, 40, 7, 1), (r"right infraspinatus", 76, 31, 19, 1), (r"right teres minor", 74, 71, 24, 1), (r"right teres major", 162, 20, 16, 0),
    (r"right subscapularis", 87, 33, 20, 1), (r"right coracobrachialis", 93, 97, 0, 1),
    (r"clavicular part of right pectoralis major", 144, 3, 17, 1), (r"sternocostal part of right pectoralis major", 138, 89, 25, 0), (r"abdominal part of right pectoralis major", 138, 132, 25, 0),
    (r"right latissimus dorsi", 254, 161, 25, 0), (r"long head of right biceps brachii", 116, 272, 0, 2), (r"short head of right biceps brachii", 132, 192, 0, 2),
    (r"right brachialis", 86, 54, 0, 2), (r"long head of right triceps", 134, 143, 12, 3), (r"lateral head of right triceps", 114, 100, 9, 3), (r"medial head of right triceps", 114, 90, 9, 3),
    (r"right anconeus", 27, 18, 0, 3), (r"right brachioradialis", 173, 133, 0, 2), (r"right pronator teres", 49, 130, 10, 0), (r"right supinator", 33, 28, 0, 0),
    (r"right extensor carpi radialis longus", 81, 224, 0, 0), (r"right extensor carpi radialis brevis", 59, 222, 9, 0), (r"right extensor carpi ulnaris", 62, 228, 4, 0),
    (r"right flexor carpi radialis", 63, 244, 3, 0), (r"right flexor carpi ulnaris", 51, 265, 12, 0), (r"right palmaris longus", 64, 270, 4, 0),
    (r"right flexor digitorum superficialis", 75, 250, 5, 0), (r"right flexor digitorum profundus", 75, 250, 7, 0), (r"right extensor digitorum", 70, 320, 3, 0),
    (r"right trapezius", 150, 20, 0, 1), (r"right serratus anterior", 150, 20, 0, 1), (r"right rhomboid", 120, 15, 0, 0), (r"right levator scapulae", 130, 20, 0, 1),
]
# origin -> insertion segment (T thorax, S scapula/clavicle, H humerus, F ulna, P radius/hand), standard anatomy
ATTACH = [(r"biceps brachii", "S", "P"), (r"brachialis$", "H", "F"), (r"brachioradialis", "H", "P"), (r"long head of right triceps", "S", "F"),
          (r"(lateral|medial) head of right triceps", "H", "F"), (r"anconeus", "H", "F"), (r"deltoid", "S", "H"), (r"pectoralis major", "T", "H"),
          (r"pectoralis minor", "T", "S"), (r"latissimus", "T", "H"), (r"teres (major|minor)|spinatus|subscapularis|coracobrachialis", "S", "H"),
          (r"trapezius|rhomboid|levator scapulae|serratus anterior|subclavius|omohyoid", "T", "S"), (r"pronator teres|supinator|pronator quadratus", "H", "P"),
          (r"(flexor|extensor) carpi|palmaris|flexor digitorum|extensor digitorum|extensor digiti|extensor indicis|pollicis longus|abductor pollicis longus|extensor pollicis brevis", "H", "P")]
# muscles whose shape change is modelled in detail (rig.fusiform / rig.sheet): decimated less, debris islands removed
KEY = re.compile(r"(right |of right )(biceps brachii|brachialis$|brachioradialis|triceps brachii|deltoid|pectoralis major|latissimus dorsi|coracobrachialis|teres major)", re.I)
# (path shape tautness, free point along the muscle, length tautness): biceps / brachialis / brachioradialis moment
# arms ~40 / ~25 / ~50 mm near 90 deg (Murray et al. 1995, 2000)
TAUT = [(r"biceps brachii", 0.7, 0.55, 1.0), (r"brachialis$", 0.4, 0.5, 0.45), (r"brachioradialis", 0.25, 0.08, 0.6), (r"flexor carpi radialis|extensor carpi radialis", 0.25, 0.2, 0.5)]
SPAN = re.compile(r"pectoralis major|latissimus dorsi|teres major|deltoid", re.I)
FUS = re.compile(r"biceps brachii|brachialis$|brachioradialis|triceps brachii|coracobrachialis|anconeus|flexor carpi radialis|extensor carpi radialis", re.I)
HAND = re.compile(r"scaphoid|lunate|triquetr|pisiform|trapezium|trapezoid|capitate|hamate|metacarpal|phalanx of (right|left) (thumb|index|middle|ring|little) finger|phalanx of (right|left) thumb|sesamoid bone of (right|left) (thumb|hand)", re.I)


def decimated(fid, cls):
    key = cls == "muscle" and KEY.search(NAMES[fid]) is not None
    path = os.path.join(CACHE, fid + ("_k.npz" if key else ".npz"))
    if os.path.exists(path):
        z = np.load(path); return z["V"], z["F"]
    V, F = bp3d.load_obj(fid)
    _, first, inv = np.unique(np.round(V, 3), axis=0, return_index=True, return_inverse=True)   # weld duplicate vertices
    V, F = V[first], inv.ravel()[F]
    F = F[(F[:, 0] != F[:, 1]) & (F[:, 1] != F[:, 2]) & (F[:, 0] != F[:, 2])]
    r = RATIO[cls] * (0.35 if cls == "muscle" and DEEP.search(NAMES[fid]) else 1)
    if key: r = 0.15 if "latissimus" in NAMES[fid] else 0.25
    target = max(120, int(len(F) * r))
    if target < len(F):
        s = pyfqmr.Simplify(); s.setMesh(V, F); s.simplify_mesh(target_count=target, aggressiveness=7, preserve_border=False, verbose=0)
        V, F, _ = s.getMesh()
    if key: V, F = rig.drop_debris(V, F)
    np.savez(path, V=V.astype(np.float32), F=F.astype(np.int32)); return V, F


def to_thorax(V):                                         # BP3D: x = patient left, y = posterior, z = up (mm)
    return np.stack([-V[:, 1], V[:, 2], -V[:, 0]], 1)


def sphere_fit(P):
    A = np.c_[2 * P, np.ones(len(P))]; b = (P ** 2).sum(1)
    x = np.linalg.lstsq(A, b, rcond=None)[0]; c = x[:3]; return c, math.sqrt(x[3] + c @ c)


def rot(ax, a):
    ax = np.asarray(ax, float); ax = ax / np.linalg.norm(ax)
    K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    return np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * K @ K


def vertex_neighbours(F, n):
    from scipy.sparse import coo_matrix, diags
    r = np.r_[F[:, 0], F[:, 1], F[:, 2], F[:, 1], F[:, 2], F[:, 0]]; c = np.r_[F[:, 1], F[:, 2], F[:, 0], F[:, 0], F[:, 1], F[:, 2]]
    A = coo_matrix((np.ones(len(r)), (r, c)), shape=(n, n)).tocsr(); A.data[:] = 1
    deg = np.asarray(A.sum(1)).ravel(); deg[deg == 0] = 1
    return diags(1 / deg) @ A


def smooth(W, A, it):
    for _ in range(it): W = 0.5 * W + 0.5 * (A @ W)
    return W


if __name__ == "__main__":
    cat = bp3d.catalogue(); NAMES = {fid: n for fid, n, _ in cat}
    parts = []
    for k, (fid, n, c) in enumerate(cat):
        V, F = decimated(fid, c); parts.append(dict(fid=fid, name=n, cls=c, V=to_thorax(V.astype(float)), F=F))
        if k % 60 == 0: print(f"  {k}/{len(cat)} parts", flush=True)
    by = {p["name"]: p for p in parts}
    # ---- landmarks (raw BP3D mm, thorax axes)
    hum = by["right humerus"]["V"]; top = hum[hum[:, 1] > hum[:, 1].max() - 45]
    c, r = sphere_fit(top)
    for _ in range(4):                                     # trim the tubercles: keep points near the sphere
        d = np.abs(np.linalg.norm(top - c, axis=1) - r); top = top[d < np.percentile(d, 60)]; c, r = sphere_fit(top)
    GH = c
    dist = hum[hum[:, 1] < hum[:, 1].min() + 60]
    epi_l, epi_m = dist[np.argmax(dist[:, 2])], dist[np.argmin(dist[:, 2])]
    art = hum[hum[:, 1] < hum[:, 1].min() + 22]
    ELB = art.mean(0); EAX = (epi_l - epi_m) / np.linalg.norm(epi_l - epi_m)
    rad, uln = by["right radius"]["V"], by["right ulna"]["V"]
    RH = rad[rad[:, 1] > rad[:, 1].max() - 14].mean(0); UH = uln[uln[:, 1] < uln[:, 1].min() + 14].mean(0)
    height = by["skin"]["V"][:, 1].max() - by["skin"]["V"][:, 1].min()
    S = (H_LEN / 0.186) / height                            # body sized for a person whose humerus is H_LEN (humerus ~ 0.186 x height)
    k_arm = H_LEN / (np.linalg.norm(ELB - GH) * S)          # then the upper arms are stretched to exactly H_LEN
    print(f"GH {GH.round(1)} r {r:.1f}  elbow {ELB.round(1)}  humerus {np.linalg.norm(ELB - GH):.0f} mm, height {height:.0f} mm -> scale {S:.3f}, upper-arm stretch {k_arm:.3f}", flush=True)
    # left shoulder centre and arm bones (for the matching stretch of the left arm)
    lhum = by["left humerus"]["V"]; ltop = lhum[lhum[:, 1] > lhum[:, 1].max() - 45]; lc, lr = sphere_fit(ltop)
    for _ in range(4):
        d = np.abs(np.linalg.norm(ltop - lc, axis=1) - lr); ltop = ltop[d < np.percentile(d, 60)]; lc, lr = sphere_fit(ltop)
    lart = lhum[lhum[:, 1] < lhum[:, 1].min() + 22].mean(0)
    for p in parts: p["V"] = (p["V"] - GH) * S
    ELB, RH, UH, EPI_L, EPI_M, LGH, LELB = [(x - GH) * S for x in (ELB, RH, UH, epi_l, epi_m, lc, lart)]
    def arm_bone(n, side): return n == f"{side} humerus" or n == f"{side} radius" or n == f"{side} ulna" or (side in n and HAND.search(n) is not None)
    armset = {s: np.concatenate([p["V"] for p in parts if p["cls"] == "bone" and arm_bone(p["name"], s)]) for s in ("right", "left")}
    other = cKDTree(np.concatenate([p["V"] for p in parts if p["cls"] == "bone" and not arm_bone(p["name"], "right") and not arm_bone(p["name"], "left") and "scapula" not in p["name"] and "clavicle" not in p["name"]]))
    girdle = cKDTree(np.concatenate([p["V"] for p in parts if p["cls"] == "bone" and ("scapula" in p["name"] or "clavicle" in p["name"])]))
    atree = {s: cKDTree(v) for s, v in armset.items()}
    for side, g0, e0 in (("right", np.zeros(3), ELB), ("left", LGH, LELB)):
        d = (e0 - g0) / np.linalg.norm(e0 - g0); Le = np.linalg.norm(e0 - g0)
        for p in parts:
            V = p["V"]
            if p["cls"] in ("bone", "cartilage"): a_ = np.full(len(V), 1.0 if arm_bone(p["name"], side) else 0.0)
            else:
                da = atree[side].query(V)[0]; do = np.minimum(other.query(V)[0], girdle.query(V)[0])
                a_ = (1 / (da + 3) ** 4) / (1 / (da + 3) ** 4 + 1 / (do + 3) ** 4)
            along = np.clip((V - g0) @ d, 0, Le)
            p["V"] = V + np.outer(a_ * (k_arm - 1) * along, d)
        if side == "right":
            ELB = ELB + d * (k_arm - 1) * Le; RH = RH + d * (k_arm - 1) * Le; UH = UH + d * (k_arm - 1) * Le
            EPI_L = EPI_L + d * (k_arm - 1) * np.clip(EPI_L @ d, 0, Le); EPI_M = EPI_M + d * (k_arm - 1) * np.clip(EPI_M @ d, 0, Le)
    S = S  # uniform part of the scale
    print("elbow after stretch", np.linalg.norm(ELB).round(1), flush=True)
    # ---- modesty: fair the genital region of the skin into a smooth surface and dress it in fitted briefs
    nm_all = bp3d.names(); inv_nm = {v: k for k, v in nm_all.items()}
    gen = np.concatenate([(to_thorax(bp3d.load_obj(inv_nm[n])[0]) - GH) * S for n in ("corpus cavernosum of penis", "glans penis") if n in inv_nm])
    gc = gen.mean(0); skin_p = by["skin"]; SV = skin_p["V"]; SF = skin_p["F"]
    hips = np.concatenate([p["V"] for p in parts if p["name"] in ("left hip bone", "right hip bone")])
    mid_z = hips[:, 2].mean(); y_crest = hips[:, 1].max(); y_isch = hips[:, 1].min()
    reg = (np.linalg.norm(SV - gc, axis=1) < 95 * S) & (np.abs(SV[:, 2] - mid_z) < 75 * S) & (SV[:, 1] > y_isch - 60 * S)
    A = vertex_neighbours(SF, len(SV))
    for _ in range(400):                                       # membrane fairing of the region, boundary fixed
        SV[reg] = (A @ SV)[reg]
    skin_p["V"] = SV
    # briefs: from just below the iliac crest to the upper thigh, cut higher at the sides
    lat = np.abs(SV[:, 2] - mid_z) / (np.abs(SV[:, 2] - mid_z).max() + 1e-9)
    top = y_crest - 55 * S; bottom = y_isch - (35 - 25 * lat) * S
    atree = {s: cKDTree(np.concatenate([p["V"] for p in parts if p["cls"] == "bone" and arm_bone(p["name"], s)])) for s in ("right", "left")}   # after the stretch
    d_other = other.query(SV)[0]
    skin_p["cloth"] = (atree["right"].query(SV)[0] > d_other) & (atree["left"].query(SV)[0] > d_other)   # trunk mask; the band is cut in the shader
    BRIEFS = dict(top=float(top), isch=float(y_isch), mid=float(mid_z), latmax=float(np.abs(SV[:, 2] - mid_z).max()), s=float(S))
    print(f"fairing {reg.sum()} skin verts, briefs {skin_p['cloth'].sum()} verts", flush=True)
    # rest frames: humerus (y up the bone, z lateral elbow axis), forearm flexion, pronation axis
    yh = -ELB / np.linalg.norm(ELB); zh = EAX - (EAX @ yh) * yh; zh /= np.linalg.norm(zh); HR = np.c_[np.cross(yh, zh), yh, zh]
    fore = (UH - ELB); f0 = math.degrees(math.acos(np.clip(fore @ (-yh) / np.linalg.norm(fore), -1, 1)))
    print(f"rest humerus dir {(-yh).round(3)}  rest elbow flexion {f0:.1f} deg", flush=True)
    # ---- segment of every bone
    SEG = dict(T=0, S=1, H=2, F=3, P=4)
    for p in parts:
        n = p["name"]; p["seg"] = None
        if p["cls"] in ("bone", "cartilage"):
            if n == "right scapula": p["seg"] = "S"
            elif n == "right humerus": p["seg"] = "H"
            elif n == "right ulna": p["seg"] = "F"
            elif n == "right radius" or ("right" in n and HAND.search(n)): p["seg"] = "P"
            elif n == "right clavicle": p["seg"] = "C"
            else: p["seg"] = "T"
    LEG = re.compile(r"femur|tibia|fibula|patella|hip bone|sacrum|coccyx|calcaneus|talus|metatarsal|cuneiform|cuboid|navicular|toe|sesamoid", re.I)
    bone_pts = {s: np.concatenate([p["V"] for p in parts if p["seg"] == s and not (s == "T" and LEG.search(p["name"]))]) for s in "TSHFP"}
    leg_tree = cKDTree(np.concatenate([p["V"] for p in parts if p["seg"] == "T" and LEG.search(p["name"])]))
    bone_pts["S"] = np.concatenate([bone_pts["S"], by["right clavicle"]["V"][by["right clavicle"]["V"][:, 2] > -60 * S]])
    trees = {s: cKDTree(v) for s, v in bone_pts.items()}
    arm_tree = cKDTree(np.concatenate([bone_pts[s] for s in "SHFP"] + [by["right clavicle"]["V"]]))
    # ---- moving muscles: weights + muscle axis
    def prox_weights(V, pw=4.0, eps=3.0):
        D = np.stack([trees[s].query(V)[0] for s in "TSHFP"], 1)
        W = 1.0 / (D + eps) ** pw; return W / W.sum(1, keepdims=True), D
    bone_all = cKDTree(np.concatenate([p["V"] for p in parts if p["cls"] == "bone"]))
    TIS = []                                              # (points, weights) of every tissue part, filled in the loop
    Y_CUT = 109.0 * S                                     # neck seam between the decimated body skin and the full-res head
    inv_nm2 = {v: k for k, v in bp3d.names().items()}

    def bp3d_thorax(name, weld=True):
        V_, F_ = bp3d.load_obj(inv_nm2[name])
        if weld:
            _, first, inv = np.unique(np.round(V_, 3), axis=0, return_index=True, return_inverse=True)
            V_, F_ = V_[first], inv.ravel()[F_]; F_ = F_[(F_[:, 0] != F_[:, 1]) & (F_[:, 1] != F_[:, 2]) & (F_[:, 0] != F_[:, 2])]
        return (to_thorax(V_.astype(float)) - GH) * S, F_

    def hires_head():
        Vh, Fh = bp3d_thorax("skin"); o = rig.outer_shell(Vh, Fh); Vh, Fh, _ = rig.submesh(Vh, Fh, o)
        keep = Vh[:, 1] > Y_CUT - 15 * S; Vh, Fh, _ = rig.submesh(Vh, Fh, keep)
        return Vh, Fh

    def surface_points(name, k):
        import trimesh
        V_, F_ = bp3d_thorax(name, weld=False); return trimesh.sample.sample_surface(trimesh.Trimesh(V_, F_, process=False), k, seed=1)[0], V_, F_

    def head_features(Vr, Fr, head):
        """per render vertex: hair cover, hair height (short cut, shaped by the BodyParts3D hair sculpt), lips, flush
        (ears, nose, cheeks); plus eye centres and eyebrow lines for the shaders"""
        n = len(Vr); feat = np.zeros((n, 4)); H = np.flatnonzero(head); nrm = rig.vertex_normals(Vr, Fr); A_ = vertex_neighbours(Fr, n)
        P, _, _ = surface_points("set of head hairs", 250000); tree = cKDTree(P); hair = np.zeros(n); hh = np.zeros(n)
        for i in H:
            idx = tree.query_ball_point(Vr[i] + nrm[i] * 15 * S, r=25 * S)
            if not idx: continue
            R_ = P[idx] - Vr[i]; t_ = R_ @ nrm[i]; rad_ = np.linalg.norm(R_ - np.outer(t_, nrm[i]), axis=1)
            m_ = (rad_ < 5 * S) & (t_ > -4 * S) & (t_ < 45 * S)
            if m_.sum() >= 3: hair[i] = 1; hh[i] = t_[m_].max()
        hgt = np.where(hair > 0, np.clip(0.3 * hh + 1.0 * S, 0, 8 * S), 0)
        hair = smooth(hair, A_, 3); hgt = smooth(hgt, A_, 4)
        feat[:, 0] = np.where(head, hair, 0); feat[:, 1] = np.where(head, hgt / (10 * S), 0)
        Pl, _, _ = surface_points("labial part of mouth, nsn", 80000); d_ = cKDTree(Pl).query(Vr[H])[0]
        feat[H, 2] = np.clip((2.6 * S - d_) / (1.6 * S), 0, 1)
        Ve, Fe = bp3d_thorax("eyeball"); zmid = Ve[:, 2].mean(); eyes = []
        for side in (Ve[:, 2] > zmid, Ve[:, 2] <= zmid):
            c_, r_ = sphere_fit(Ve[side]); eyes.append([*c_.tolist(), float(r_)])
        Pe, _, _ = surface_points("ear", 60000); d_ = cKDTree(Pe).query(Vr[H])[0]; flush = np.zeros(n)
        flush[H] = 0.55 * np.clip((5 * S - d_) / (4 * S), 0, 1)
        ec = np.array([e[:3] for e in eyes]); mid = ec.mean(0)
        lips_c = Pl.mean(0)
        face = H[(np.abs(Vr[H, 2] - mid[2]) < 8 * S) & (Vr[H, 1] < mid[1] - 10 * S) & (Vr[H, 1] > lips_c[1] + 8 * S)]
        tip = Vr[face[np.argmax(Vr[face, 0])]] if len(face) else mid
        blobs = [(tip, 14 * S, 0.35)]
        for e in ec:                                       # cheeks: below and lateral of the eyes, on the face
            c_ = e + np.array([0, -30 * S, 0]) + (e - mid) * 0.25
            front = H[(Vr[H, 0] > c_[0] - 30 * S)]; c_ = Vr[front[np.argmin(np.linalg.norm(Vr[front] - c_, axis=1))]]
            blobs.append((c_, 24 * S, 0.3))
        for c_, r_, a_ in blobs:
            d_ = np.linalg.norm(Vr[H] - c_, axis=1); flush[H] = np.maximum(flush[H], a_ * np.clip(1 - (d_ / r_) ** 2, 0, 1))
        feat[:, 3] = smooth(flush, A_, 2)
        Vb_, _ = bp3d_thorax("set of eyebrows"); brows = []
        for side in (Vb_[:, 2] > zmid, Vb_[:, 2] <= zmid):
            X = Vb_[side]; zz = X[:, 2]; o_ = np.argsort(np.abs(zz - zmid)); edges_ = np.quantile(np.abs(zz - zmid), np.linspace(0, 1, 9))
            pl = []
            for k in range(8):
                m_ = (np.abs(zz - zmid) >= edges_[k]) & (np.abs(zz - zmid) <= edges_[k + 1])
                if m_.sum() < 3: continue
                c_ = X[m_].mean(0); w_ = np.percentile(np.abs(X[m_, 1] - c_[1]), 85)
                pl.append([*c_.tolist(), float(max(w_, 0.8 * S))])
            brows.append(pl)
        return feat, dict(eyes=eyes, brows=brows, gaze=[1.0, 0.0, 0.0], mid=mid.tolist())
    # the biceps' common distal tendon reaches the radial tuberosity in the long-head mesh only: both heads use it
    _lh = by["long head of right biceps brachii"]["V"]; _dp = trees["P"].query(_lh)[0]
    BICEPS_INS = _lh[np.argsort(_dp)[:max(12, len(_lh) // 40)]].mean(0)

    def tissue_seeds(Vs, Fs, reach=14.0):
        """skin vertices with tissue right under them (inward of the skin normal, within reach mm): their weights"""
        P = np.concatenate([t[0] for t in TIS]); Wt = np.concatenate([t[1] for t in TIS]); tree = cKDTree(P)
        nrm = rig.vertex_normals(Vs, Fs); dd, ii = tree.query(Vs, k=12)
        rel = P[ii] - Vs[:, None]; inward = (rel * nrm[:, None]).sum(2) < -0.35 * dd
        dd = np.where(inward, dd, np.inf); dmin = dd.min(1)
        use = np.isfinite(dd) & (dd < dmin[:, None] + 3.0)
        w = np.where(use, 1 / (dd + 1.0), 0); W = (w[:, :, None] * Wt[ii]).sum(1) / (w.sum(1, keepdims=True) + 1e-12)
        return dmin < reach * S, W
    recs, nmov = {}, 0
    order = [i for i, p in enumerate(parts) if p["cls"] != "skin"] + [i for i, p in enumerate(parts) if p["cls"] == "skin"]   # skin last (it reads the tissue)
    for pi in order:
        p = parts[pi]
        V, F = p["V"], p["F"]; rec = dict(name=p["name"], cls=p["cls"])
        if p["cls"] in ("bone", "cartilage"):
            if p["seg"] == "C":                              # clavicle: thorax at the SC end -> scapula at the AC end
                t = np.clip((V[:, 2] - V[:, 2].min()) / (np.ptp(V[:, 2]) + 1e-9), 0, 1); t = t * t * (3 - 2 * t)
                W = np.zeros((len(V), 5)); W[:, 0] = 1 - t; W[:, 1] = t; rec["W"] = W
            else: rec["seg"] = SEG[p["seg"]]
        elif p["cls"] == "muscle":
            d = arm_tree.query(V)[0].min()
            if d < 6 * S:
                A_m = vertex_neighbours(F, len(V)); W, D = prox_weights(V); W = smooth(W, A_m, 6); rec["W"] = W
                att = [s for k, s in enumerate("TSHFP") if (D[:, k] < 5 * S).sum() >= 3]
                cen = {s: V[D[:, "TSHFP".index(s)] < 5 * S].mean(0) for s in att}
                fixed = next(((a, b) for rx, a, b in ATTACH if re.search(rx, p["name"])), None)
                if fixed:                                     # anatomical origin / insertion: the vertices closest to those bones
                    att = list(fixed)
                    for s_ in fixed:
                        k = "TSHFP".index(s_); near = np.argsort(D[:, k])[:max(12, len(V) // 40)]; cen[s_] = V[near].mean(0)
                if len(att) >= 2:
                    pairs = [(np.linalg.norm(cen[a] - cen[b]), a, b) for i, a in enumerate(att) for b in att[i + 1:]]
                    _, a, b = max(pairs) if not fixed else (0, fixed[0], fixed[1])
                    # if the attachment line is short against the muscle's extent, use the ends of its principal axis
                    c0 = V.mean(0); ev = np.linalg.eigh(np.cov((V - c0).T))[1][:, -1]; pr = (V - c0) @ ev
                    lo, hi = V[pr <= np.percentile(pr, 3)].mean(0), V[pr >= np.percentile(pr, 97)].mean(0)
                    if np.linalg.norm(cen[b] - cen[a]) < 0.6 * np.linalg.norm(hi - lo):
                        ka = "TSHFP".index(a)
                        near_lo = D[pr <= np.percentile(pr, 3), ka].mean(); near_hi = D[pr >= np.percentile(pr, 97), ka].mean()
                        cen[a], cen[b] = (lo, hi) if near_lo < near_hi else (hi, lo)
                    rec["axis"] = [SEG[a], cen[a].tolist(), SEG[b], cen[b].tolist()]
                    w_, E_ = np.linalg.eigh(np.cov((V - c0).T))
                    # rest offset that the bulge scales: fusiform -> from the muscle line; flat sheet -> half the local
                    # thickness along the vertex normal (distance to the opposite face), so only thickness changes
                    u_ = cen[b] - cen[a]; t_ = np.clip((V - cen[a]) @ u_ / (u_ @ u_), 0, 1); rr = (V - cen[a]) - np.outer(t_, u_)
                    if w_[1] > 6 * w_[0] or re.search(r"deltoid|trapezius|pectoralis|latissimus|serratus|infraspinatus|subscapularis|supraspinatus|rhomboid|oblique|transversus|teres", p["name"]):
                        fn = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]]); vn = np.zeros_like(V)
                        for k_ in range(3): np.add.at(vn, F[:, k_], fn)
                        vn /= np.linalg.norm(vn, axis=1, keepdims=True) + 1e-12
                        dd, ii = cKDTree(V).query(V, k=min(24, len(V)))
                        th = np.full(len(V), 6.0 * S)
                        for r_ in range(len(V)):
                            opp = (vn[ii[r_]] @ vn[r_]) < -0.3
                            if opp.any(): th[r_] = min(np.abs((V[ii[r_][opp]] - V[r_]) @ vn[r_]).min(), 25 * S)
                        rr = vn * (th / 2)[:, None]; rec["sheet"] = True; rec["th"] = th
                    rec["rr"] = rr
                    # belly weight: local thickness about the line, normalised (tendons ~0, belly 1)
                    o_, e_ = cen[a], cen[b]; u = e_ - o_; t = np.clip((V - o_) @ u / (u @ u), 0, 1)
                    rad = np.linalg.norm((V - o_) - np.outer(t, u), axis=1); bins = np.minimum((t * 20).astype(int), 19)
                    prof = np.array([np.percentile(rad[bins == k], 90) if (bins == k).any() else 0 for k in range(20)])
                    prof = np.convolve(np.r_[prof[0], prof, prof[-1]], [0.25, 0.5, 0.25], "valid")
                    thick = prof[bins] / (prof.max() + 1e-9); rec["belly"] = np.clip((thick - 0.25) / 0.55, 0, 1) ** 1.5
                    arch = next(((lf, ts, al, g) for rx, lf, ts, al, g in ARCH if re.search(rx, p["name"])), (100, 60, 5, 0))
                    rec["arch"] = [arch[1] / (arch[0] + arch[1]), arch[2], arch[3]]
                    if SPAN.search(p["name"]):
                        # fan muscles crossing the shoulder: weight to the insertion bone falls off along the fibres
                        # (distance from the insertion), the rest keeps the bone-proximity split -> even fibre stretch
                        # (only the part within ~16 cm of the insertion lifts with the arm: the rest of a broad sheet like
                        # the latissimus stays bound to the chest wall by its fascia)
                        kb = "TSHFP".index(b); dI = np.linalg.norm(V - cen[b], axis=1); hs = H_LEN / 325.0
                        wI = np.clip((160 * hs - dI) / (120 * hs), 0, 1); wI = wI * wI * (3 - 2 * wI)
                        Wo_ = W.copy(); Wo_[:, kb] = 0; Wo_ /= Wo_.sum(1, keepdims=True) + 1e-12
                        W2 = (1 - wI)[:, None] * Wo_; W2[:, kb] += wI; W2 = smooth(W2, A_m, 4); W2 /= W2.sum(1, keepdims=True)
                        rec["W2"] = W2
                    W2 = rec.get("W2", W)
                    if rec.get("sheet"): rec["mdl"] = ("sheet", rig.sheet(V, F, cen[b], bone_all, rec["th"], rec["belly"]))
                    elif FUS.search(p["name"]) and len(V) >= 60:
                        rec["mdl"] = ("fus", rig.fusiform(V, F, W2, cen[a], cen[b], bone_all))
                        # anterior elbow crossers take the chord (bowstring) beyond a free point instead of wrapping the
                        # joint like the bones' blend does: (tautness, free point as a fraction of the length)
                        rec["mdl"][1]["taut"] = next(((t_, f_, l_) for rx, t_, f_, l_ in TAUT if re.search(rx, p["name"])), (0.0, 1.0, 0.0))
                        rec["mdl"][1]["ins"] = [SEG[b], (BICEPS_INS if "biceps" in p["name"] else cen[b]).tolist()]
                        rec["mdl"][1]["free_end"] = "short head of right biceps" in p["name"]   # ends in the common tendon
                # centre-of-rotation skinning data (4 influences)
                W2 = rec.get("W2", W); rec["w4"] = rig.topk(W2, 4); rec["cor"] = rig.cor_centres(V, F, W2, A=A_m)
                nmov += 1
            else: rec["seg"] = 0
        else:                                                 # skin: harmonic weights diffused over the surface from unambiguous seeds
            _, D = prox_weights(V); D[:, 0] = np.minimum(D[:, 0], leg_tree.query(V)[0])
            A = vertex_neighbours(F, len(V)); best = D.argmin(1); srt = np.sort(D, 1)
            seed = (srt[:, 0] < 22 * S) & (srt[:, 0] < 0.6 * srt[:, 1])
            W = np.zeros((len(V), 5)); W[seed, best[seed]] = 1; W[~seed] = 0.2
            for _ in range(700): W = A @ W; W[seed] = 0; W[seed, best[seed]] = 1
            W = smooth(W, A, 10); W /= W.sum(1, keepdims=True); rec["W"] = W     # legacy weights (wi/ww), kept as they were
            rec["cloth"] = p["cloth"]
            # new rig on the outer shell only (the BodyParts3D skin is a ~3 mm solid: the inner shell is never seen)
            outer = rig.outer_shell(V, F); Vo, Fo, oid = rig.submesh(V, F, outer)
            Vo, Fo, xsrc, zinfo, relax, anchor = rig.unzip_axilla(Vo, Fo, trees, H_LEN)
            cutp = zinfo.pop("path") if zinfo else np.zeros(0, int); ridge = zinfo.pop("ridge") if zinfo else np.zeros(0, int)
            print("axilla unzip:", zinfo, flush=True)
            # full-resolution head (the decimated skin is too coarse for the face), joined on a neck seam
            Vh_, Fh_ = hires_head()
            nz = len(Vo); Vr, Fr, hsrc, head = rig.replace_head(Vo, Fo, Vh_, Fh_, Y_CUT)
            back = -np.ones(nz, int); back[hsrc[hsrc >= 0]] = np.flatnonzero(hsrc >= 0)       # unzipped index -> render index
            usrc = np.where(hsrc >= 0, xsrc[np.maximum(hsrc, 0)], -1)                         # render -> outer-shell index
            pocket = (hsrc >= 0) & (usrc < 0)
            rsrc = np.where(usrc >= 0, oid[np.maximum(usrc, 0)], -1)                          # render -> legacy skin index
            relax = np.where((hsrc >= 0)[:, None], relax[np.maximum(hsrc, 0)], 0.0)
            anchor = np.c_[back[anchor[:, 0]], anchor[:, 1]] if len(anchor) else anchor; anchor = anchor[anchor[:, 0] >= 0]
            cutp = back[cutp]; cutp = cutp[cutp >= 0]; ridge = back[ridge]; ridge = ridge[ridge >= 0]
            Vo, Fo = Vr, Fr
            print(f"head: {head.sum()} full-resolution vertices above y = {Y_CUT:.0f} mm, render skin {len(Vo)} verts", flush=True)
            _, Do = prox_weights(Vo); Do[:, 0] = np.minimum(Do[:, 0], leg_tree.query(Vo)[0])
            best = Do.argmin(1); srt = np.sort(Do, 1)
            seed = (srt[:, 0] < 22 * S) & (srt[:, 0] < 0.6 * srt[:, 1])
            SW = np.zeros((len(Vo), 5)); SW[seed, best[seed]] = 1
            # skin lying on tissue takes that tissue's weights (muscles keep their bone-proximity weights), so the chest
            # wall stays on the thorax and only the axillary folds and dome blend toward the arm
            tseed, TW = tissue_seeds(Vo, Fo)
            tseed &= ~pocket                                  # the axilla pocket takes its weights from its edges ...
            if len(cutp):                                     # (near the cut the inward direction is ambiguous)
                Ac = vertex_neighbours(Fo, len(Vo)); near_cut = np.zeros(len(Vo)); near_cut[cutp] = 1
                for _ in range(3): near_cut = np.maximum(near_cut, (Ac @ near_cut > 0).astype(float))
                tseed &= near_cut == 0
            SW[tseed] = TW[tseed]; seed |= tseed
            pk = np.flatnonzero(pocket); seed[pk] = False; SW[pk] = 0
            if len(anchor): SW[anchor[:, 0]] = np.eye(5)[anchor[:, 1]]; seed[anchor[:, 0]] = True   # ... and its middle
            neck = Vo[:, 1] > Y_CUT - 35 * S; SW[neck] = np.eye(5)[0]; seed |= neck             # head + upper neck: thorax
            Wo = rig.harmonic(Vo, Fo, seed, SW)
            print(f"skin seeds: {tseed.sum()} on tissue, {seed.sum()} total", flush=True)
            Ao = vertex_neighbours(Fo, len(Vo))
            feat, HEAD = head_features(Vo, Fo, head)
            rcloth = (Wo[:, 2:].sum(1) < 0.5) & (atree["left"].query(Vo)[0] > other.query(Vo)[0])
            rec.update(rsm=np.unique(np.r_[ridge, cutp]), rcloth=rcloth, oid=oid, Fo=Fo, Wo=Wo, w4=rig.topk(Wo, 4), cor=rig.cor_centres(Vo, Fo, Wo, A=Ao), Vr=Vo, relax=relax, rsrc=rsrc, feat=feat)
            print(f"skin: render mesh {len(Vo)} verts (legacy {len(V)}), {seed.sum()} seeds", flush=True)
        rec["V"], rec["F"] = V, F; recs[pi] = rec
        if p["cls"] in ("bone", "cartilage", "muscle"):
            Wp = rec.get("W2", rec.get("W")) if "W" in rec else np.eye(5)[np.full(len(V), rec.get("seg", 0))]
            TIS.append((V[::2], Wp[::2]))
    out_parts = [recs[i] for i in range(len(parts))]
    Ve_, Fe_ = bp3d_thorax("eyeball"); extra_parts = [dict(name="eyeballs", cls="eye", seg=0, V=Ve_, F=Fe_)]   # kept out of parts: indices and old readers unchanged
    print(f"{len(out_parts)} parts, {nmov} moving muscles, {sum(len(p['V']) for p in out_parts)} verts, {sum(len(p['F']) for p in out_parts)} tris", flush=True)
    # skin -> nearest moving-muscle vertex (for the bulge showing through)
    mov = [(i, p) for i, p in enumerate(out_parts) if p["cls"] == "muscle" and "W" in p]
    MV = np.concatenate([p["V"] for _, p in mov]); MI = np.concatenate([np.c_[np.full(len(p["V"]), j), np.arange(len(p["V"]))] for j, (_, p) in enumerate(mov)])
    skin = [p for p in out_parts if p["cls"] == "skin"][0]
    dd, ii = cKDTree(MV).query(skin["V"]); near = dd < 22 * S
    oV = skin["Vr"]; dd, ii = cKDTree(MV).query(oV); near = dd < 26 * S
    fw_ = np.clip((26 * S - dd) / (18 * S), 0, 1); fw_ = fw_ * fw_ * (3 - 2 * fw_)          # full within ~8 mm, none past ~26 mm
    skin["fo"] = (np.where(near, MI[ii, 0], 255).astype(np.uint8), np.where(near, MI[ii, 1], 0).astype(np.uint16), np.round(fw_ * near * 255).astype(np.uint8))
    # ---- export
    b64 = lambda a: base64.b64encode(np.ascontiguousarray(a).tobytes()).decode()
    js = dict(frame="thorax mm: x anterior, y up, z right, origin right GH; scaled", scale=float(S), h_len=H_LEN,
              landmarks=dict(elbow=ELB.tolist(), elbow_axis=zh.tolist(), radial_head=RH.tolist(), ulnar_head=UH.tolist(), rest_humerus=HR.tolist(), rest_flex=f0, epi_l=EPI_L.tolist(), epi_m=EPI_M.tolist()),
              credit="BodyParts3D, (C) The Database Center for Life Science, licensed under CC Attribution-Share Alike 2.1 Japan", moving=[j for j, _ in mov], parts=[])
    for k_p, p in enumerate(out_parts + extra_parts):
        q = dict(name=p["name"], cls=p["cls"], n=len(p["V"]), pos=b64(np.round(p["V"] * 10).astype(np.int16)), idx=b64(p["F"].astype(np.uint16 if len(p["V"]) < 65536 else np.uint32)), i32=len(p["V"]) >= 65536)
        if "seg" in p: q["seg"] = p["seg"]
        if "W" in p:
            top2 = np.argsort(-p["W"], 1)[:, :2]; w = np.take_along_axis(p["W"], top2, 1); w = w / w.sum(1, keepdims=True)
            q["wi"] = b64(top2.astype(np.uint8)); q["ww"] = b64(np.round(w[:, 0] * 255).astype(np.uint8))
        if "axis" in p: q["axis"] = p["axis"]
        if "belly" in p: q["belly"] = b64(np.round(p["belly"] * 255).astype(np.uint8)); q["arch"] = p["arch"]
        if "sheet" in p: q["sheet"] = True
        if "rr" in p: q["rr"] = b64(np.round(p["rr"] * 10).astype(np.int16))
        if "cloth" in p: q["cloth"] = b64(np.packbits(p["cloth"].astype(np.uint8)))
        # ---- new rig (body.js falls back to the legacy fields above when these are missing)
        if "w4" in p: q["w4i"] = b64(p["w4"][0]); q["w4w"] = b64(p["w4"][1]); q["cor"] = b64(np.round(p["cor"] * 10).astype(np.int16))
        if "Vr" in p:
            # render mesh: outer shell, axilla pocket, full-resolution head; rsrc = legacy skin vertex (65535: new)
            q["rpos"] = b64(np.round(p["Vr"] * 10).astype(np.int16)); q["rsrc"] = b64(np.where(p["rsrc"] >= 0, p["rsrc"], 65535).astype(np.uint16))
            q["ridx"] = b64(p["Fo"].astype(np.uint16 if len(p["Vr"]) < 65536 else np.uint32)); q["ri32"] = len(p["Vr"]) >= 65536
            q["feat"] = b64(np.round(np.clip(p["feat"], 0, 1) * 255).astype(np.uint8))              # hair, hair height, lips, flush
            q["rcloth"] = b64(np.packbits(p["rcloth"].astype(np.uint8)))                           # briefs mask: trunk, not the arms
            ri = np.flatnonzero(np.linalg.norm(p["relax"], axis=1) > 0.05)        # relaxed axilla shape (blended with elevation)
            q["rlxi"] = b64(ri.astype(np.uint32)); q["rlxd"] = b64(np.round(p["relax"][ri] * 10).astype(np.int16))
            q["rsm"] = b64(p["rsm"].astype(np.uint32))                                             # pocket ridge + cut: ironed too
        if "fo" in p: q["foj"], q["fov"], q["fow"] = (b64(a) for a in p["fo"])
        if "mdl" in p:
            kind, m = p["mdl"]
            if kind == "fus":
                q["mdl"] = dict(type="fus", K=int(m["K"]), L0=float(m["L0"]), sk=np.round(m["sk"], 2).tolist(), C=np.round(m["Ck"], 2).tolist(),
                                E=np.round(m["Ek"], 4).tolist(), phi=np.round(m["phi"], 3).tolist(), NW=np.round(m["NW"], 3).tolist(), RT=np.round(m["RT"], 1).tolist(),
                                s=b64(np.round(m["s"] / m["L0"] * 65535).astype(np.uint16)), x=b64(np.round(m["X"] * 10).astype(np.int16)),
                                mu=b64(np.round(m["mu"] * 255).astype(np.uint8)), k=b64(m["kv"].astype(np.uint8)), taut=list(m.get("taut", (0.0, 1.0, 0.0))), ins=m.get("ins"), free_end=bool(m.get("free_end")))
            else:
                q["mdl"] = dict(type="sheet", n=b64(np.round(m["nrm"] * 127).astype(np.int8)), sup=b64(np.round(m["sup"] * 255).astype(np.uint8)),
                                pf=b64(m["pf"].astype(np.uint16)), pb=b64(m["pb"].astype(np.uint16)), l0=b64(np.round(m["l0"] * 10).astype(np.uint16)),
                                th=b64(np.round(np.clip(m["th"], 0, 31.8) * 8).astype(np.uint8)))
        (js["parts"] if k_p < len(out_parts) else js.setdefault("extra_parts", [])).append(q)
    js["arm_stretch"] = float(k_arm); js["briefs"] = BRIEFS; js["head"] = HEAD
    OUT = os.environ.get("BODY_OUT", os.path.join(HERE, "..", "body_mesh.json"))
    json.dump(js, open(OUT, "w"))
    np.savez_compressed(os.environ.get("RIG_OUT", os.path.join(HERE, "body_rig.npz")), **{f"V{i}": p["V"] for i, p in enumerate(out_parts)}, **{f"F{i}": p["F"] for i, p in enumerate(out_parts)})
    print("size", os.path.getsize(OUT) / 1e6, "MB")
