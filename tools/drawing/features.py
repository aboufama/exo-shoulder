"""Feature recognition on the exo parts' B-rep (user-style parts: bent bars swept along line/arc paths, planform pads,
joint hubs about axes through GH). Everything returns probes (points on faces) so the drawing can build measurement
specs (brep.evaluate) that the validator re-runs.
"""
import math
import numpy as np
from brep import unit, closest_points


def coaxial_groups(part, axis, kinds=("cyl",), tol=1e-4):
    """faces of the given kinds whose axis is parallel to `axis`, grouped by common axis line"""
    G = []
    for f in part.where():
        if f["kind"] not in kinds or "axis" not in f or abs(abs(f["axis"] @ unit(axis)) - 1) > 1e-6: continue
        p = f["point"] - (f["point"] @ unit(axis)) * unit(axis)
        for g in G:
            if np.linalg.norm(g["p"] - p) < tol: g["faces"].append(f); break
        else: G.append(dict(p=p, faces=[f]))
    return G


def bar_path(part, n, t, plane_point=None):
    """the path of a bar bent in the plane normal to n: every coaxial cylinder group (axis // n) holding a pair of
    radii t apart is one arc (inner + outer face); arcs are ordered by tangency. Returns a list of dicts
    {c (centre in the plane), R (path radius), cyls [probe_in, probe_out], floor probe or None}"""
    n = unit(n); p0 = np.zeros(3) if plane_point is None else np.asarray(plane_point, float)
    arcs = []
    for g in coaxial_groups(part, n):
        rs = sorted({round(f["r"], 4) for f in g["faces"]})
        pair = [(a, b) for a in rs for b in rs if abs(b - a - t) < 1e-3]
        if not pair: continue
        ri, ro = pair[0]
        fi = max((f for f in g["faces"] if abs(f["r"] - ri) < 1e-3), key=lambda f: f["area"])
        fo = max((f for f in g["faces"] if abs(f["r"] - ro) < 1e-3), key=lambda f: f["area"])
        floor = [f for f in g["faces"] if ri + 1e-3 < f["r"] < ro - 1e-3]
        c = g["p"] + ((p0 - g["p"]) @ n) * n
        arcs.append(dict(c=c, R=(ri + ro) / 2, ri=ri, ro=ro, cyls=[probe(part, fi, p0, n), probe(part, fo, p0, n)],
                         floor=probe(part, max(floor, key=lambda f: f["area"]), p0, n) if floor else None,
                         floor_r=floor[0]["r"] if floor else None))
    # order by tangency
    def tangent(a, b):
        L = np.linalg.norm(a["c"] - b["c"]); return min(abs(L - a["R"] - b["R"]), abs(L - abs(a["R"] - b["R"]))) < 1e-3
    nb = {i: [j for j in range(len(arcs)) if j != i and tangent(arcs[i], arcs[j])] for i in range(len(arcs))}
    ends = [i for i in nb if len(nb[i]) == 1]
    if len(arcs) == 1: return arcs
    assert len(ends) == 2, f"bar path: not a simple chain of tangent arcs (ends {ends})"
    order = [ends[0]]
    while len(order) < len(arcs): order.append([j for j in nb[order[-1]] if j not in order][0])
    return [arcs[i] for i in order]


def probe(part, f, p0, n):
    """a point on face f, preferably in the plane (p0, n) (so path probes sit on the bend plane)"""
    q = part.point_on(f)
    q2 = q - ((q - p0) @ n) * n
    if part.dist_to_face(f, q2) < 1e-4: q = q2
    return [round(float(x), 6) for x in q]


def joint_axes(part, origin=np.zeros(3)):
    """revolution axes through `origin` (GH): {axis dir: {"cyl": {r: face}, "planes": [faces normal to it]}}"""
    out = []
    for f in part.where():
        if f["kind"] not in ("cyl", "torus") or "axis" not in f: continue
        q1, q2, m = closest_points(f["point"], f["axis"], origin, f["axis"])
        if np.linalg.norm(f["point"] - ((f["point"] - origin) @ f["axis"]) * f["axis"] - origin) > 1e-4: continue
        for a in out:
            if abs(abs(a["k"] @ f["axis"]) - 1) < 1e-6: a["faces"].append(f); break
        else: out.append(dict(k=f["axis"], faces=[f]))
    for a in out:
        a["planes"] = sorted([f for f in part.where("plane") if abs(abs(f["normal"] @ a["k"]) - 1) < 1e-6
                              and np.linalg.norm(np.cross(f["centre"] - origin, a["k"])) < 12.0],
                             key=lambda f: (f["centre"] - origin) @ a["k"])
    return out
