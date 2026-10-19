"""Regression test of the R6 judge (judge/part_contact.py): it must see two parts whose EDGES cross with no vertex of
either inside the other - the case the vertex-only judge (every other vertex, step 12) scored 0.0 mm until 2026-10-16.
  1. synthetic: two slabs crossed like a plus sign (and the same with one slab turned 37 deg and tilted 9 deg); every
     vertex of each is far outside the other, the exact depth of A's surface inside B is 1.0 mm (A's top face in B's
     slab, B's bottom face in A's). The dense judge must find >= 0.9 mm both ways; the vertex-only test finds 0.
  2. the FIRST build of l1_offset-skin-normal-3r (git 06b5a59, read with git show): link 2 sits ~1.1 mm inside the J3
     plate at every frame (verifier: 1.12 mm at Raise overhead 24, dense samples at 0.7 mm) and link 1 / link 2 cross
     by ~0.66 mm in Wave 71-79 and 95-103 (9 frames each, measured at step 1). It must FAIL R6 with >= 1.0 mm.
  3. the final build (the committed design dir): the same frames plus every 12th frame must PASS (<= 0.15 mm).
  4. (synthetic, in --quick) OPEN containers: a pin fully embedded in a slab whose tessellation is open - T-junction cracks
     on its top face, and a 2 x 2 mm hole - must be caught at the exact depth (3.0 mm), by the capped chain and by the
     generalized-winding-number fallback; until 2026-10-16 an open part was never a container and this read 0. A pad
     resting 0.5 mm above the hole must stay clean (the cap does not inflate the slab).
    python3 judge/test_part_contact.py [--quick]     (exit 1 on a failure; --quick: the synthetic cases only)"""
import os, subprocess, sys, tempfile, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE); sys.path.insert(0, HERE)
import part_contact as PC
from common import design_dir, load_parts

FAIL = []
def check(ok, msg):
    print(("  PASS  " if ok else "  FAIL  ") + msg)
    if not ok: FAIL.append(msg)


def box(lo, hi):
    """closed, outward-oriented box: 8 vertices, 12 triangles (a vertex-only test sees only these 8 points)"""
    import trimesh
    m = trimesh.creation.box(extents=np.subtract(hi, lo)); m.apply_translation(0.5 * (np.add(lo, hi)))
    return np.asarray(m.vertices, float), np.asarray(m.faces)


def rot(axis, deg):
    a = np.radians(deg); u = np.asarray(axis, float) / np.linalg.norm(axis); K = np.array([[0, -u[2], u[1]], [u[2], 0, -u[0]], [-u[1], u[0], 0]])
    return np.eye(3) + np.sin(a) * K + (1 - np.cos(a)) * K @ K


def vertex_only(info, W, tol=0.15):
    """the old judge's measurement: vertices of A (every other one) inside B, nothing else"""
    best = 0.0
    for i, j in PC.candidates(info, W, PC.pair_ok(info), tol):
        A, B = info[i], info[j]; (Ra, ta), (Rb, tb) = W[A["g"]], W[B["g"]]; S = A["S"][A["kind"] == 0][::2]
        P = S @ (Ra.T @ Rb) + (ta - tb) @ Rb; m = np.all((P > B["lo"]) & (P < B["hi"]), 1)
        if m.any(): best = max(best, PC.max_depth(B, P[m], tol)[0])
    return best


def synthetic():
    print("1. synthetic: two slabs crossed, no vertex inside")
    Va, Fa = box((-20, -2, 0), (20, 2, 2)); Vb, Fb = box((-2, -20, 1), (2, 20, 3))
    parts = [("a", "slab A (40 x 4 x 2)", Va, Fa), ("b", "slab B (4 x 40 x 2)", Vb, Fb)]
    info = PC.prepare(parts, 1.0); I = (np.eye(3), np.zeros(3))
    for name, Wb in (("plus sign", I), ("B turned 37 deg about z, tilted 9 deg", (rot((0, 0, 1), 37) @ rot((1, 0, 0), 9), np.zeros(3)))):
        W = {"a": I, "b": Wb}; out = PC.frame_depths(info, PC.pair_ok(info), W, 0.15, memo={})
        ab = out.get("a|slab A (40 x 4 x 2)  IN  b|slab B (4 x 40 x 2)", (0.0, None)); ba = out.get("b|slab B (4 x 40 x 2)  IN  a|slab A (40 x 4 x 2)", (0.0, None))
        vo = vertex_only(info, W)
        print(f"     {name}: A in B {ab[0]:.3f} mm ({ab[1]}), B in A {ba[0]:.3f} mm ({ba[1]}); vertex-only {vo:.3f} mm")
        check(vo == 0.0, f"{name}: the vertex-only test sees nothing (no vertex inside)")
        if name == "plus sign":
            check(abs(ab[0] - 1.0) < 0.05 and abs(ba[0] - 1.0) < 0.05, f"{name}: the dense judge finds the exact 1.0 mm both ways")
        else:
            check(ab[0] > 0.9 and ba[0] > 0.9, f"{name}: the dense judge finds > 0.9 mm both ways")
    # the same plus sign with B's tessellation turned inside out (inverted normals) and a second, inward copy of A's box
    # as a separate body of A: re-oriented in weld(), the answers must not move
    info = PC.prepare([("a", "slab A", np.r_[Va, Va + [0, 0, -10]], np.r_[Fa, Fa[:, ::-1] + len(Va)]), ("b", "slab B inverted", Vb, Fb[:, ::-1])], 1.0)
    out = PC.frame_depths(info, PC.pair_ok(info), {"a": I, "b": I}, 0.15, memo={})
    ab = out.get("a|slab A  IN  b|slab B inverted", (0.0, None))[0]; ba = out.get("b|slab B inverted  IN  a|slab A", (0.0, None))[0]
    print(f"     inverted B, A with an inward body: A in B {ab:.3f} mm, B in A {ba:.3f} mm (re-oriented: {[x['n'] for x in info if x['reoriented']]})")
    check(abs(ab - 1.0) < 0.05 and abs(ba - 1.0) < 0.05 and all(x["reoriented"] for x in info), "inverted / inconsistently wound tessellations are re-oriented: same 1.0 mm both ways")
    # a coaxial fit within tol must stay silent: B resting on A's top face, 0.1 mm into it
    Vc, Fc = box((-5, -1.5, 1.9), (5, 1.5, 4))
    info = PC.prepare([("a", "slab A", Va, Fa), ("c", "pad on A (0.1 mm in)", Vc, Fc)], 1.0)
    out = PC.frame_depths(info, PC.pair_ok(info), {"a": (np.eye(3), np.zeros(3)), "c": (np.eye(3), np.zeros(3))}, 0.15, memo={})
    check(not out, f"a seated face 0.1 mm deep stays within tol 0.15 ({out})")


def equivalence(dd, n=20000, seed=0):
    """the judge's fast path (OUT reject mask, libigl AABB distance, grid winding number + segment crossings only near the
    surface) against judge/sdist.py's validated Mesh.max_depth (kd-tree cover + winding number, judge/test_sdist.py),
    point by point: random points in each part's box and near its surface, the deepest inside point must agree to 1e-6"""
    import json
    print(f"0. fast path == judge/sdist.py Mesh.max_depth on random points ({os.path.basename(dd)})")
    rng = np.random.default_rng(seed); info = PC.prepare(load_parts(dd), 1.0, build=None); worst = 0.0; nin = 0; nout = 0
    for x in sorted([x for x in info if x["closed"]], key=lambda x: -len(x["S"]))[:4] + [x for x in info if "plate" in x["n"] or "strap" in x["n"]][:4]:
        M = x["M"]; S = M.S[rng.integers(0, len(M.S), n // 2)] + rng.normal(0, 0.8, (n // 2, 3))
        P = np.r_[rng.uniform(M.lo, M.hi, (n // 2, 3)), S]
        i = np.clip(np.rint((P - M.glo) / M.g).astype(int), 0, np.asarray(M.W.shape) - 1); out = x["OUT"][i[:, 0], i[:, 1], i[:, 2]]
        wn = M.winding_at(P[out]); nout += int(out.sum())
        check(not np.any(wn != 0), f"{x['n'][:40]}: all {int(out.sum())} points the OUT mask rejects have winding number 0")
        for tol in (0.0, 0.15):
            keep = np.where(~out)[0]; d_new, k_new = PC.max_depth(x, P[keep], tol); d_ref, k_ref = M.max_depth(P, tol)
            worst = max(worst, abs(d_new - d_ref)); nin += 1
            check(abs(d_new - d_ref) < 1e-6, f"{x['n'][:40]} tol {tol}: deepest {d_new:.6f} vs sdist {d_ref:.6f} mm")


def cracked_slab():
    """slab 40 x 10 x 6 (z 0..6), tessellated (edges <= ~2.5 mm), with (a) T-junction cracks: a few top-face triangles split
    at their edge midpoints while their neighbours keep the long edge, (b) a 2 x 2 mm hole in the top face. Open both ways."""
    import trimesh
    m = trimesh.creation.box(extents=(40, 10, 6)); m.apply_translation((0, 0, 3))
    for _ in range(3): m = m.subdivide()
    m.merge_vertices(); c = m.triangles_center
    tj = trimesh.Trimesh(m.vertices, m.faces, process=False).subdivide(face_index=np.where((c[:, 2] > 5.99) & (np.abs(c[:, 0] - 8) < 2.5) & (np.abs(c[:, 1]) < 2))[0])
    keep = ~((c[:, 2] > 5.99) & (np.abs(c[:, 0] + 8) < 1.0) & (np.abs(c[:, 1]) < 1.0))
    hole = trimesh.Trimesh(m.vertices, m.faces[keep], process=False)
    return dict(tjunction=tj, hole=hole)


def open_containers():
    print("4. open containers: a pin fully inside a cracked slab (exact depth 3.0 mm)")
    import trimesh
    pin = trimesh.creation.cylinder(radius=1.0, height=10.0, sections=32); pin.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, (0, 1, 0)))
    pin.apply_translation((0, 0, 3))                                                 # axis along x at y 0, z 3: 3.0 mm from the top / bottom faces
    pad = trimesh.creation.box(extents=(4, 4, 2)); pad.apply_translation((-8, 0, 6.5 + 1.0))   # 0.5 mm above the hole
    I = (np.eye(3), np.zeros(3))
    for crack, S in cracked_slab().items():
        V, F = np.asarray(S.vertices, float), np.asarray(S.faces)
        check(not PC.weld(V, F)[2], f"{crack}: the slab's tessellation is open (the old judge never used it as a container)")
        for mode in ("cap", "gwn"):
            info = PC.prepare([("s", "slab", V, F), ("p", "pin", np.asarray(pin.vertices, float), np.asarray(pin.faces)),
                               ("q", "pad", np.asarray(pad.vertices, float), np.asarray(pad.faces))], 1.0, build=None, open_mode=mode)
            out = PC.frame_depths(info, PC.pair_ok(info), {"s": I, "p": I, "q": I}, 0.15, memo={})
            d = out.get("p|pin  IN  s|slab", (0.0, None))[0]; how = info[0]["open"]
            print(f"     {crack}, {mode}: pin in slab {d:.3f} mm; other pairs {sorted((k, round(v[0], 2)) for k, v in out.items() if k != 'p|pin  IN  s|slab')}; "
                  f"{how['how'][:60]}, boundary {how['boundary_edges']} edges, cap {how.get('cap_triangles', 0)} triangles, dev {how.get('cap_max_dev_mm', '-')} mm")
            check(abs(d - 3.0) < 0.02, f"{crack}, {mode}: the embedded pin is caught at the exact depth ({d:.3f} vs 3.000 mm)")
            check(set(out) == {"p|pin  IN  s|slab"}, f"{crack}, {mode}: nothing else interpenetrates (the pad above the hole, the slab in the pin)")
            check(bool(how.get("gwn")) == (mode == "gwn"), f"{crack}, {mode}: part_contact lists the slab as open, closed by {'the GWN fallback' if mode == 'gwn' else 'a cap'}")


SELECT = lambda c, fi: (c == "Raise overhead" and 21 <= fi <= 27) or (c == "Wave" and 72 <= fi <= 78)


def builds():
    did = "l1_offset-skin-normal-3r"; rel = f"pipeline/full-exo/designs/{did}"
    print(f"2. first build of {did} (git 06b5a59): must FAIL R6 with >= 1.0 mm")
    with tempfile.TemporaryDirectory() as td:
        try:
            for f in ("exo.glb", "clips.json"):
                open(os.path.join(td, f), "wb").write(subprocess.run(["git", "-C", REPO, "show", f"06b5a59:{rel}/{f}"], check=True, capture_output=True).stdout)
        except Exception as e:
            print(f"  SKIP  git 06b5a59 not readable here ({e})"); return
        t0 = time.time(); out = PC.run(td, step=1, select=SELECT); v = out["violations"]
        k23 = "l2|link 2 strap keep-out (8 x 3 mm Ti, fitted underside)  IN  l3|J3 lower plate keep-out (O20 x 3, member 3)"
        k12 = [k for k in v if k.startswith("l1|link 1 strap") and "IN  l2|link 2 strap" in k]
        print(f"     {out['frames_checked']} frames in {time.time() - t0:.0f} s: R6 {out['max_depth']} mm; link 2 in J3 plate "
              f"{v.get(k23, {}).get('max_depth', 0.0)} mm, link 1 in link 2 {v[k12[0]]['max_depth'] if k12 else 0.0} mm")
        check(out["max_depth"] >= 1.0, "R6 >= 1.0 mm on the first build (FAIL)")
        check(v.get(k23, {}).get("max_depth", 0.0) >= 1.0, "link 2 >= 1.0 mm inside the J3 plate at Raise overhead 21-27")
        check(bool(k12) and v[k12[0]]["max_depth"] >= 0.5, "link 1 / link 2 cross by >= 0.5 mm at Wave 72-78")
        parts = load_parts(td); info = PC.prepare(parts, 1.0, build=None); import json
        C = {c["name"]: c for c in json.load(open(os.path.join(td, "clips.json")))["clips"]}
        vo = max(vertex_only(info, PC.xforms(C[c]["frames"][fi])) for c, fi in (("Raise overhead", 24), ("Wave", 72), ("Wave", 96)))
        print(f"     the vertex-only test on Raise overhead 24, Wave 72, Wave 96: {vo:.2f} mm")
    print(f"3. final build of {did} (this checkout): must PASS R6")
    dd = design_dir(did); equivalence(dd); t0 = time.time()
    out = PC.run(dd, step=1, select=SELECT); out2 = PC.run(dd, step=12)
    print(f"     {out['frames_checked']} + {out2['frames_checked']} frames in {time.time() - t0:.0f} s: R6 {out['max_depth']} / {out2['max_depth']} mm")
    check(out["max_depth"] <= 0.15 and out2["max_depth"] <= 0.15, "final build R6 <= 0.15 mm (PASS)")


if __name__ == "__main__":
    synthetic(); open_containers()
    if "--quick" not in sys.argv: builds()
    print("FAILED: " + "; ".join(FAIL) if FAIL else "all R6 judge checks pass"); sys.exit(1 if FAIL else 0)
