"""TEMPLATE for a new morphology model on the shared kit (tools/concept_kit.py, docs/concepts/KIT.md).
Copy to docs/concepts/models/<id>.py, set ID / PARAMS / SWEEP, rewrite build(). Everything else (fitting the undersides,
contact, continuity, collisions, scoring, sweep file, row, events) is the kit's job - do not re-implement it.

This file is the champion spherical 3R (same kinematics as baseline-3r-kit.py) built with the KIT conventions instead
of the baseline's: flat O20 hubs at their fitted level F with the real stack (K4), 12 x 3 mm straps with the 60 deg
climb limit (K5), the K7 neck to BOTTOM's bar, K3 march, K2 continuity along the motion and K6 collisions on.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/<id>.py [--sweep] [--write]
"""
import itertools, os, sys
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402

ID = "_template"                                             # = the catalogue id (docs/concepts/catalogue.json)
NAME = "Template: spherical 3R on kit conventions"
# PARAMS: every number the design has. Angles in deg, lengths in mm. 'q' = underside quantile over the fit poses
# (1.0 = never touches in any pose it takes; 0.95 lets the worst 5 % of poses become contact poses - they then count
# as NOT taken, so q trades reach against closeness).
PARAMS = dict(az=2.4305071427308924, el=80.67633718429899, a1=76.90180446920043, a2=66.74921235407174,
              wd=86.32769021001913, wa=21.829657347343378, sigma=-1, margin=10.0, width=12.0, t_link=3.0, q=0.95)
# SWEEP: the few parameters that matter, coarse first. Keep it small (the bench costs ~2-3 s per configuration).
SWEEP = dict(q=[0.93, 0.97, 1.0], el=[76.0, 80.7, 85.0], a1=[72.0, 76.9, 82.0])


def build(B, F, p):
    """-> K.Chain. Use ONLY F for geometry (continuity calls build again on interpolated frames). All arrays are per
    pose (P, ...) in the thorax frame: F.S(u) maps a scapula-frame direction, F.HG(u) a humerus (band) direction,
    F.H(u) a body_pose humerus direction (BOTTOM's bar)."""
    # ---- 1. kinematics: the axes, the closure, the joint values -----------------------------------------------------
    p1 = F.S(K.bvec(p["az"], p["el"]))                        # J1 fixed in the scapula
    p3 = F.HG(K.wdir(p["wd"], p["wa"]))                       # J3 fixed in the humerus
    p2, ok, margin = K.closure(p1, p3, p["a1"], p["a2"], p["sigma"], margin_deg=p["margin"])   # K1 (J2)
    # joint values for K2 (deg; add slides in mm as extra columns and set q_period=None in the Chain if you have them)
    q = np.stack([K.axis_angle(p1, F.S([1.0, 0, 0]), p2), K.axis_angle(p2, p1, p3),
                  K.axis_angle(p3, F.HG([0.0, -1, 0]), p2)], -1)
    # joint / slide RANGES go into ok here, e.g. ok &= np.abs(q[:, 1]) < 170

    # ---- 2. members: every part at real size ------------------------------------------------------------------------
    # hubs (K4): flat O20 discs; their level F_k is fitted. At each joint the LOWER member's skin face sits at F, the
    # UPPER member's underside at F + 3.15 (K.STACK): ramp_to (hub, dz) says which.
    hubs = [K.hub_member("hub1", p1, "J1"), K.hub_member("hub2", p2, "J2"), K.hub_member("hub3", p3, "J3")]
    w, t = p["width"], p["t_link"]
    links = [K.strap_member("link1", p1, p2, ("J1", "J2"), width=w, t=t, ramp_to=(("hub1", K.STACK), ("hub2", 0.0))),
             K.strap_member("link2", p2, p3, ("J2", "J3"), width=w, t=t, ramp_to=(("hub2", K.STACK), ("hub3", K.STACK)),
                            over=[("link1", 1.0), ("neck", 1.0)]),   # link 2 passes OVER link 1 and the neck (>= 1 mm) - else K6 rejects those poses
             K.neck_member(F, p3, joints=("J3",), ramps=(("hub3", 0.0), (None, 0)))]   # arm-end plate -> BOTTOM (K7)
    return K.Chain(members=hubs + links, ok=ok, q=q, joints=dict(J1=p1, J2=p2, J3=p3),
                   info=dict(residual_deg=round(float(K.closure_residual(p1, p3, p2, p["a1"], p["a2"])[ok].max()), 5) if ok.any() else None,
                             min_margin=round(float(margin[ok].min()), 2) if ok.any() else None))


def configs():
    keys = list(SWEEP)
    return [dict(PARAMS, **dict(zip(keys, v))) for v in itertools.product(*(SWEEP[k] for k in keys))]


if __name__ == "__main__":
    a = sys.argv[1:]
    B = K.bench(60, 160)                                     # the screening bench (fast grid cache)
    r = K.evaluate(B, build, PARAMS, verbose=True)            # honest defaults: mode 'march', cont, collide
    if "--sweep" in a:
        best, rows = K.sweep(B, build, configs(), os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json"))
        r = K.evaluate(B, build, best["params"]); print("BEST", best["params"], r)
        if "--write" in a:
            K.write_row(ID, NAME, r, lens="", family="spherical 3R", active_dof=3, passive_dof=0, n_configs=len(rows),
                        verdict="", note=f"kit conventions; best {best['params']}")
            K.log_event(f"screened {NAME}: gap {r['gap']} (baseline 68.93)")
