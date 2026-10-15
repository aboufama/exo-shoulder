"""Validation of the R2 attribution (judge/body_regions.py) on a synthetic self-intersecting body with known answers:
a trunk (box x -100..0, y -100..100, z -100..100) and an arm (cylinder r 40 along y, axis at x = 20, y -150..50) that
sinks 20 mm into the trunk - one closed mesh per region, concatenated into one self-intersecting body, as the posed rig
is where its arm passes into its chest. A part riding on the arm is judged at single points:
  (a) 5 mm outside the arm, away from the trunk: outside the body, never judged
  (b) 4 mm inside the arm, clear of the trunk: 4 mm (own limb, full)
  (c) 4 mm inside the arm where the arm lies in the trunk: 4 mm (own limb, full)
  (d) 7 mm beyond the buried medial arm skin, straight into the trunk: 7 mm (all of it deeper than the skin under it)
  (e) 5 mm out from buried arm skin at 41 deg to the trunk depth: 3.75 mm (the component into the trunk)
  (f) 5 mm above the buried end cap, towards the trunk surface: 0 mm (raw 5 mm: the rig's overlap, not the part)
  (g) 10 mm out from arm skin that is NOT buried, 3.75 mm into the trunk: 3.75 mm (unchanged where the rig is valid)
  (h) a part with no own limb (base / links): the plain depth
Also on the real rig at a pose where its arm is clear of the trunk (elevation 45, elbow 60): points under the upper-arm
skin all round count at least their plain depth (own limb).
    python3 judge/test_body_contact.py"""
import math, os, sys
import numpy as np, trimesh
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from sdist import Mesh
import body_regions as BR


def body():
    box = trimesh.creation.box(extents=[100, 200, 200]); box.apply_translation([-50, 0, 0])
    cyl = trimesh.creation.cylinder(radius=40, height=200, sections=720); cyl.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0]))
    cyl.apply_translation([20, -50, 0])                                         # y -150..50
    V = np.r_[box.vertices, cyl.vertices]; F = np.r_[box.faces, cyl.faces + len(box.vertices)]
    freg = np.r_[np.zeros(len(box.faces), int), np.ones(len(cyl.faces), int)]
    return V, F, freg


def judge_points(V, F, freg, P, own):
    M = Mesh(V, F, 2.0).build_grid(1.0); R = BR.Regions(V, F, freg, h=2.0); out = []
    for p in np.atleast_2d(P):
        p = p[None]; s, _ = M.tree.query(p); wn = M.winding_at(p, s)[0]
        if wn < 1: out.append((0.0, "outside", 0.0)); continue
        d = M.closest(p)[0]; a, _, kind = BR.attributable_depth(M, R, own, p, d, tol=0.0)
        out.append((a, kind, float(d[0])))
    return out


def main():
    V, F, freg = body(); ok = True
    zq = math.sqrt(40 ** 2 - 30 ** 2); n = np.array([-30.0, 0, zq]) / 40
    zg = math.sqrt(40 ** 2 - 19 ** 2); ng = np.array([-19.0, 0, zg]) / 40
    cases = [("a", [65, 0, 0], 1, 0.0), ("b", [56, 0, 0], 1, 4.0), ("c", [-16, 0, 0], 1, 4.0), ("d", [-27, 0, 0], 1, 7.0),
             ("e", list(np.array([-10, 0, zq]) + 5 * n), 1, 3.75), ("f", [-10, 55, 0], 1, 0.0),
             ("g", list(np.array([1, 0, zg]) + 10 * ng), 1, 3.75), ("h", [-27, 0, 0], None, 7.0)]
    print("synthetic self-intersecting body (trunk box + arm cylinder sunk 20 mm):")
    for name, p, own, want in cases:
        got, kind, raw = judge_points(V, F, freg, np.array([p], float), own)[0]
        good = abs(got - want) < 0.05 + 0.01 * want; ok &= good
        print(f"  {'ok ' if good else 'BAD'} ({name}) attributable {got:6.3f} mm (expected {want:5.2f}); plain depth {raw:6.3f}; {kind}")
    # the real rig, a pose without self-intersection near the arm parts: attribution must equal the plain depth
    sys.path.insert(0, os.path.join(HERE, "..", "pipeline", "avg")); sys.path.insert(0, os.path.join(HERE, "..", "pipeline", "full-exo"))
    import body_pose as BP
    rig = BP._rig(); sk = rig.skin; nn = sk["n"]; W = np.zeros((nn, 5)); np.add.at(W, (np.repeat(np.arange(nn), 4), sk["wi"].ravel()), sk["ww"].ravel())
    freg_r = BR.face_regions(BP.F, BR.vertex_regions(W)); pose = dict(plane=0, elev=45, axial=0, flex=60, pron=0); Vp = BP.posed(pose)
    sg, _ = BP.segs(rig.L, rig.s, pose); E = sg[2][0] @ np.array(rig.L["elbow"]); EA = sg[2][0] @ np.array(rig.L["elbow_axis"]); EA /= np.linalg.norm(EA)
    Ps = []
    for s in np.linspace(60, 300, 9):                                           # points 1-6 mm under the upper-arm skin, all round
        c = s * E / np.linalg.norm(E); u = EA - (EA @ E) * E / (E @ E); u /= np.linalg.norm(u); v = np.cross(E / np.linalg.norm(E), u)
        for th in np.linspace(0, 2 * np.pi, 24, endpoint=False):
            dirn = np.cos(th) * u + np.sin(th) * v; Ps.append(c + dirn * 30.0)        # ~30 mm out from the humerus axis: under the skin
    Ps = np.array(Ps); M = Mesh(Vp, BP.F, 2.0).build_grid(1.0, Ps.min(0) - 5, Ps.max(0) + 5); R = BR.Regions(Vp, BP.F, freg_r)
    s0, _ = M.tree.query(Ps); wn = M.winding_at(Ps, s0); P = Ps[wn == 1]; d = M.closest(P)[0]
    tot = 0; worst = 0.0
    for p, dd in zip(P, d):
        a, _, kind = BR.attributable_depth(M, R, 1, p[None], np.array([dd]), tol=0.0); tot += 1; worst = max(worst, dd - a)
    good = tot > 20 and worst < 1e-6; ok &= good
    print(f"  {'ok ' if good else 'BAD'} real rig, elev 45 / flex 60: {tot} points inside the upper arm, attributable >= plain depth at all of them (max shortfall {worst:.2e} mm)")
    print("PASS" if ok else "FAIL"); return ok


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
