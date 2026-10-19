"""Concept model: BACK-ANCHORED RING-ENDED 3R (id back-anchored-ring-3r, docs/concepts/catalogue.json, ideation E),
built on the shared kit (tools/concept_kit.py, docs/concepts/KIT.md). Doc: docs/concepts/back-anchored-ring-3r.md.

A spherical 3R (every joint axis through the GH centre) that leaves the top of the shoulder bare:
    scapula handler -> J1 thin-section RING (axis u1 fixed in the scapula, posterior-medial-down, ring on the
    infraspinous fossa) -> link 1 (strap over the posterior deltoid) -> J2 O20 v5 hub (axis by closure) -> link 2
    (strap down the back of the arm) -> J3 thin-section RING (axis j3 fixed in the humerus, through the arm point
    (s3, th3, 60) of the rig's arm frame) -> bracket to the user's BOTTOM bar (only when the ring sits off the bar line).
DOF: 3 ACTIVE (J1-J3), 0 PASSIVE: J2 is fixed by the two-cone closure on branch br, the three angles follow.

Parts at real size (honesty rule 1):
  * ring k (pitch radius pk > 0): housed 4.76-section Reali-Slim (KAA type) as a FLAT annulus normal to its axis,
    radial width 9 (pitch +-4.5), stack 8 (lower housing 0..4.8 = stator, rotating housing 4.8..8), open centre;
    kind 'flat' (K4 fit: every annulus sample marched along the axis from its true offset, level = max over samples
    of the q-quantile). pk = 0 makes the joint an O20 hub (K.hub_member) - the in-model control.
  * links: 14 x 5.5 Ti straps (spec) on the great circle between the joint axes, K3 underside, K5 60 deg climb. At a
    ring a link leaves from a LUG on the rotating housing: the strap starts LUG mm outside the ring's outer race (the
    kit's K6 exempts joint partners only within 12 mm of the axis, so a strap root lying on the annulus would be
    flagged as a collision; the 4-5 mm x 14 mm lug itself is the only unsampled metal) at the rotating housing level
    (ring F + 4.8). At J2 link 1 is the lower member (F), link 2 the upper (F + 3.15) and passes over link 1 (1 mm).
  * J3 bracket: BOTTOM's bar runs down the lateral arm (body_pose frame, 67.5 mm out along Wb). If the J3 ring's
    centre is more than RING_ON_BAR deg from the bar point at the same depth, a 14 x 6 strap joins the ring's stator
    lug to the bar (K3 underside, climb), else the ring sits on BOTTOM's saddle.
Checks: K3 march, K2 dense continuity (joint values + axes), K6 collisions, kit audit; serial singular margin >= 5 deg
and the closure's fold / stretch margin >= `margin` deg.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/back-anchored-ring-3r.py [--seed] [--small]
        evaluates BEST (or the catalogue seed with --seed) on Bench(60, 160) (Bench(20, 40) with --small)
    ... --sweep j3,j1,hub,arc,q,combo,final   appends the stages (in that order they were run, j3 cut after k7) to the
        sweep file, skipping configurations already in it
"""
import itertools, json, math, os, sys
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402
import concept_bench as CB                                   # noqa: E402

ID = "back-anchored-ring-3r"
NAME = "Back-anchored ring-ended 3R (top of the shoulder left bare)"
SWEEP_JSON = os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json")
D2R = math.pi / 180
RING_W, RING_H, RING_UP = 9.0, 8.0, 4.8                      # housed 4.76-section thin ring: radial width, stack, rotating housing
LUG = 4.5                                                     # mm from the outer race to the strap root (K6 lateral clearance)
RING_ON_BAR = 18.0                                            # deg: ring centre this close to the bar point -> it sits on the saddle

PARAMS = dict(lat1=-10.0, lon1=-120.0, R1=110.0, p1=24.6, a12=90.0, a23=90.0, d3=26.6, th3=40.0, R3=75.0, p3=24.6,
              br=1, margin=10.0, width=14.0, t_link=5.5, q=0.97)
# d3 = angle of the J3 axis from the humerus axis (the spec's arm point (s, th, 60) has d3 = atan(60 / s): s 120 -> 26.6,
# s 100-160 -> 31-21 deg). The spec places J3 there; an axis through GH then meets the arm skin ~63 deg off its normal, so a
# flat ring stands on edge (measured: ring 3 at a median 138 mm, worst > 189 mm). d3 near 90 puts J3 at the GH level.
# best honest configuration of the sweep (k18, gap 116.31; docs/concepts/back-anchored-ring-3r.md). PARAMS is the
# catalogue seed (spec J1 / J3 sites, rings) the sweep started from.
BEST = dict(PARAMS, p1=0.0, p3=0.0, d3=50.0, th3=30.0, q=0.92)
SWEEPS = {   # stages (coarse then refined); configs() expands one stage
    "seed": [dict()],
    "j3": [dict(d3=[26.6, 50.0, 70.0, 88.0], th3=[0.0, 30.0, 60.0])],
}


def sdir(lat, lon):
    """S-local direction (spec): lon 0 lateral, +90 anterior, -90 posterior; lat up (x anterior, y up, z lateral)"""
    la, lo = lat * D2R, lon * D2R
    return np.array([math.cos(la) * math.sin(lo), math.sin(la), math.cos(la) * math.cos(lo)])


_AF = None
def arm_frame():
    """(a humerus axis, z lateral, y posterior) in the rig's (body_pose) humerus frame (spec)"""
    global _AF
    if _AF is None:
        L = CB.BP._rig().L; a = K.unit(np.array(L["elbow"], float)); z = np.array(L["rest_humerus"], float) @ np.array([0.0, 0.0, 1.0])
        z = K.unit(z - (z @ a) * a); _AF = (a, z, np.cross(a, z))
    return _AF


def arm_dir(d, th):
    """unit direction at angle d from the humerus axis, azimuth th (0 lateral, +90 posterior), rig arm frame"""
    a, z, y = arm_frame(); d, t = d * D2R, th * D2R
    return math.cos(d) * a + math.sin(d) * (math.cos(t) * z + math.sin(t) * y)


def toward(u, v, phi):
    """rotate unit u (P, 3) toward v by phi rad on their great circle"""
    e = K.unit(v - (u * v).sum(-1, keepdims=True) * u)
    return math.cos(phi) * u + math.sin(phi) * e


def annulus_xy(p, step=2.0):
    ro, ri = p + RING_W / 2, p - RING_W / 2
    g = np.arange(-ro, ro + 1e-6, step); X, Y = np.meshgrid(g, g); r2 = X ** 2 + Y ** 2
    keep = (r2 <= ro ** 2 + 1e-9) & (r2 >= ri ** 2 - 1e-9); return np.stack([X[keep], Y[keep]], -1)


def joint_member(name, axis, joint, p):
    """thin-section ring (p > 0, flat annulus, stack 8) or O20 hub (p = 0); returns (member, link level dz, lug angle fn)"""
    if p <= 0: return K.hub_member(name, axis, joint), None
    k = K.unit(axis); a, b = K.plane_frame(k); xy = annulus_xy(p)
    D = K.unit(70.0 * k[:, None] + xy[None, :, :1] * a[:, None] + xy[None, :, 1:] * b[:, None])
    return K.Member(name, D, kind="flat", t=RING_H, width=2 * (p + RING_W / 2), joints=(joint,), K=k, A=a, Bv=b, xy=xy, cell=4.0), p


def build(B, F, p):
    u = F.S(sdir(p["lat1"], p["lon1"]))                                   # J1 axis, scapula-fixed
    j3d = arm_dir(p["d3"], p["th3"]); w = F.H(j3d)                         # J3 axis, humerus-fixed (rig arm frame)
    v, ok, fold = K.closure(u, w, p["a12"], p["a23"], p["br"], margin_deg=p["margin"])   # J2 by closure
    serial = np.degrees(np.arcsin(np.clip(np.abs((u * np.cross(v, w)).sum(-1)) / math.sin(p["a23"] * D2R), 0, 1)))
    ok = ok & (serial >= 5.0)
    # joint values (K2): J3 measured from the humerus axis (>= d3 away from w, so never degenerate; the sweep's runs
    # before this line read F.H([0, 0, 1]), >= 20 deg from w for every configuration run, same geometry)
    q = np.stack([K.axis_angle(u, F.S([0.0, 1.0, 0.0]), v), K.axis_angle(v, u, w), K.axis_angle(w, F.H(arm_frame()[0]), v)], -1)

    j1, r1 = joint_member("ring1" if p["p1"] > 0 else "hub1", u, "J1", p["p1"])
    j2 = K.hub_member("hub2", v, "J2")
    j3, r3 = joint_member("ring3" if p["p3"] > 0 else "hub3", w, "J3", p["p3"])
    W, T = p["width"], p["t_link"]
    # link roots: at a ring, from a lug LUG mm outside the outer race on the rotating housing (level F + 4.8)
    u0 = toward(u, v, math.atan2(r1 + RING_W / 2 + LUG, p["R1"])) if r1 else u
    w0 = toward(w, v, math.atan2(r3 + RING_W / 2 + LUG, p["R3"])) if r3 else w
    lv1 = (j1.name, RING_UP if r1 else K.STACK); lv3 = (j3.name, RING_UP if r3 else K.STACK)
    link1 = K.strap_member("link1", u0, v, ("J1", "J2"), width=W, t=T, ramp_to=(lv1, ("hub2", 0.0)))
    link2 = K.strap_member("link2", v, w0, ("J2", "J3"), width=W, t=T, ramp_to=(("hub2", K.STACK), lv3), over=[("link1", 1.0)])
    members = [j1, j2, j3, link1, link2]
    # J3 stator to BOTTOM's bar (body_pose frame) at the same depth down the arm
    sb = max(40.0, 65.0 / math.tan(max(p["d3"], 1.0) * D2R))            # depth of the ring down the arm; the bar starts at 40
    barl = K.unit(67.5 * K.WB + sb * K.DB); bar = F.H(barl)
    off = float(np.degrees(np.arccos(np.clip((j3d * barl).sum(), -1, 1))))
    if off > RING_ON_BAR:
        m0 = toward(w, bar, math.atan2((r3 or K.HUB_R) + (RING_W / 2 if r3 else 0) + LUG, p["R3"]))
        members.append(K.strap_member("bracket", m0, bar, ("J3",), width=14.0, t=6.0, ramp_to=((j3.name, 0.0), (None, 0))))
    hubless = tuple(j for j, r in (("J1", r1), ("J3", r3)) if r)
    return K.Chain(members=members, ok=ok, q=q, joints=dict(J1=u, J2=v, J3=w), hubless=hubless,
                   info=dict(residual_deg=round(float(K.closure_residual(u, w, v, p["a12"], p["a23"])[ok].max()), 5) if ok.any() else None,
                             serial_p5=round(float(np.percentile(serial[ok], 5)), 1) if ok.any() else None,
                             serial_min=round(float(serial[ok].min()), 1) if ok.any() else None, bar_off_deg=round(off, 1)))


SWEEPS.update({   # refined stages start from the best configuration in the sweep file so far
    "hub": [dict(p1=0.0, p3=0.0), dict(p1=0.0, p3=24.6), dict(p1=24.6, p3=0.0)],
    "arc": [dict(a12=72.0, a23=[75.0, 90.0]), dict(d3=88.0)],
    # J1 where the ray from GH meets the skin squarely (obliquity map in the doc: 52 deg at the spec's lat -10 / lon -120,
    # 12-22 deg at lat 20-50 / lon -60..-75, the posterosuperior shoulder over the scapular spine)
    "j1": [dict(lat1=[35.0, 45.0], lon1=[-100.0, -75.0])],
    "q": [dict(q=[0.92])],
    # the variant aimed at both measured limiters: J1 on its square, still seat AND a shorter link 1 that keeps J2
    # lateral overhead; O20 hubs (small seats) and rings compared
    "combo": [dict(d3=50.0, th3=30.0, a23=90.0, q=0.92, lon1=-75.0, lat1=[35.0, 45.0], a12=[66.0, 75.0], p1=0.0, p3=0.0),
              dict(d3=50.0, th3=30.0, a23=90.0, q=0.92, lon1=-75.0, lat1=45.0, a12=[66.0, 75.0], p1=24.6, p3=24.6)],
    # closure range vs seat: in-band reaches the champion's level at the posterosuperior seat, reach / follow fall with
    # the closure share, so widen the closure range (a12 + a23 large, |a12 - a23| small) and trade q
    "final": [dict(d3=50.0, th3=30.0, p1=0.0, p3=0.0, lat1=-10.0, lon1=-120.0, a12=90.0, a23=90.0, q=0.95),
              dict(d3=50.0, th3=30.0, p1=0.0, p3=0.0, lat1=35.0, lon1=-75.0, a12=90.0, a23=90.0, q=0.92),
              dict(d3=50.0, th3=30.0, p1=0.0, p3=0.0, lat1=35.0, lon1=-75.0, a12=85.0, a23=105.0, q=0.92),
              dict(d3=50.0, th3=30.0, p1=0.0, p3=0.0, lat1=20.0, lon1=-90.0, a12=90.0, a23=90.0, q=0.95)],
})


def best_so_far():
    try: rows = json.load(open(SWEEP_JSON))
    except (OSError, ValueError): return dict(PARAMS)
    return dict(min(rows, key=lambda e: e["gap"])["params"]) if rows else dict(PARAMS)


def configs(stage):
    out = []; start = dict(PARAMS) if stage in ("seed", "j3") else best_so_far()
    for d in SWEEPS[stage]:
        keys = [k for k in d if isinstance(d[k], list)]
        base = dict(start, **{k: d[k] for k in d if k not in keys})
        for vals in itertools.product(*(d[k] for k in keys)):
            out.append(dict(base, **dict(zip(keys, vals))))
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    nc, nw = (60, 160) if "--small" not in a else (20, 40)
    B = K.bench(nc, nw)
    if "--sweep" in a:
        for stage in a[a.index("--sweep") + 1].split(","):
            done = [e["params"] for e in (json.load(open(SWEEP_JSON)) if os.path.exists(SWEEP_JSON) else [])]
            cf = [c for c in configs(stage) if c not in done]
            best, rows = K.sweep(B, build, cf, SWEEP_JSON, resume=True)
            print("BEST", stage, best)
    else:
        r = K.evaluate(B, build, BEST if "--seed" not in a else PARAMS); print(json.dumps({k: r[k] for k in r if k not in ("sample_mm",)}, default=str))
