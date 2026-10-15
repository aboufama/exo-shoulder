"""clavicular-front-route: spherical 3R with J1 on the bony acromio-clavicular FRONT, a scapula-fixed bridge strap from
the handler over the acromion top to the J1 seat, short links over the anterior shoulder, J3 on the anterolateral
upper-arm strip, K7 neck to BOTTOM. Built on the shared kit (tools/concept_kit.py, docs/concepts/KIT.md).

Spec (docs/concepts/catalogue.json 'clavicular-front-route') -> model, and where the model departs from it:
  * sdir(lat, lon) = (-cos lat sin lon, sin lat, cos lat cos lon) in the scapula frame (x anterior, y up, z lateral).
  * armpt(s, th, r) = s e + r (cos th l + sin th b) in the body_pose humerus frame (F.H; e, l, b from the spec); J3's
    axis is its direction. th < 0 is anterior (b = -x).
  * Hubs: kit K4 flat O20 discs (not the spec's ray-fit caps); straps 12 x 3 (links), bridge 14 x 3, neck 14 x 6 (K7,
    straight to BOTTOM's bar start - the kit standard - instead of the spec's dog-leg down the strip).
  * The bridge is part of the base but is metal between the handler and the cuff, so it is in `members` and scored.
  * Order of `over`: link 1 passes over the bridge, link 2 over link 1 and the neck (link 1 is fitted first).
  * Every honesty check on: K3 march, K2 dense continuity on every joint axis, K6 collisions, audit.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/clavicular-front-route.py [poses]
"""
import os, sys
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402

ID = "clavicular-front-route"
NAME = "Front route: J1 on the bony acromio-clavicular front (spherical 3R + scapula bridge)"
D2R = np.pi / 180
E_ = K.unit(np.array([-0.023, -0.986, 0.164])); L_ = np.array([0.004, 0.164, 0.986]); B_ = np.array([-1.0, 0.023, 0.0])
PARAMS = dict(j1lat=40.0, j1lon=-100.0, a12=60.0, a23=60.0, s3=30.0, th3=-40.0, r3=76.0, sigma=1, margin=8.0,
              q=1.0, width=12.0, t_link=3.0, br_lat=45.0, br_lon=90.0, bw_lat=65.0, bw_lon=20.0, br_w=14.0,
              link1_over_bridge=1)


def sdir(lat, lon):
    la, lo = lat * D2R, lon * D2R
    return np.array([-np.cos(la) * np.sin(lo), np.sin(la), np.cos(la) * np.cos(lo)])


def armdir(s, th, r):
    t = th * D2R
    return K.unit(s * E_ + r * (np.cos(t) * L_ + np.sin(t) * B_))


def build(B, F, p):
    a1 = sdir(p["j1lat"], p["j1lon"])
    p1 = F.S(a1)                                              # J1: scapula-fixed, AC front
    p3 = F.H(armdir(p["s3"], p["th3"], p["r3"]))              # J3: humerus-fixed, anterolateral strip
    p2, ok, margin = K.closure(p1, p3, p["a12"], p["a23"], p["sigma"], margin_deg=p["margin"])
    q = np.stack([K.axis_angle(p1, F.S([0.0, 0, 1]), p2), K.axis_angle(p2, p1, p3),
                  K.axis_angle(p3, F.H(E_), p2)], -1)
    hubs = [K.hub_member("hub1", p1, "J1"), K.hub_member("hub2", p2, "J2"), K.hub_member("hub3", p3, "J3")]
    # base bridge (scapula-fixed): handler mount -> over the acromion top -> J1 seat (lower member at J1)
    b0, bw = F.S(sdir(p["br_lat"], p["br_lon"])), F.S(sdir(p["bw_lat"], p["bw_lon"]))
    # two straps bolted at the waypoint as a lap joint: bridge_a passes OVER bridge_b there (>= 1 mm, by construction);
    # without it K6 flagged their shared end in every pose (v1 bug: 'collide 1.0' whenever both sat at one level)
    bridge = [K.strap_member("bridge_b", bw, p1, ("J1",), width=p["br_w"], t=3.0, ramp_to=((None, 0), ("hub1", 0.0))),
              K.strap_member("bridge_a", b0, bw, (), width=p["br_w"], t=3.0, over=[("bridge_b", 1.0)])]
    w, t = p["width"], p["t_link"]
    o1 = [("bridge_b", 1.0)] if p.get("link1_over_bridge", 1) else []   # link 1 sweeps about J1: over the bridge's J1 end
    links = [K.strap_member("link1", p1, p2, ("J1", "J2"), width=w, t=t, ramp_to=(("hub1", K.STACK), ("hub2", 0.0)),
                            **({"over": o1} if o1 else {})),
             K.strap_member("link2", p2, p3, ("J2", "J3"), width=w, t=t, ramp_to=(("hub2", K.STACK), ("hub3", K.STACK)),
                            over=[("link1", 1.0), ("neck", 1.0)]),
             K.neck_member(F, p3, joints=("J3",), ramps=(("hub3", 0.0), (None, 0)))]
    info = dict(residual_deg=round(float(K.closure_residual(p1, p3, p2, p["a12"], p["a23"])[ok].max()), 5) if ok.any() else None,
                min_margin=round(float(margin[ok].min()), 2) if ok.any() else None)
    return K.Chain(members=hubs + bridge + links, ok=ok, q=q, joints=dict(J1=p1, J2=p2, J3=p3), info=info)


def pose_report(B, rep):
    """per named pose class: taken / contact / collision / closure (red team)"""
    L = B._kit_last; out = {}
    for name, sel in dict(rest=lambda P: P["elev"] < 25, overhead=lambda P: P["elev"] >= 140,
                          across=lambda P: P["plane"] >= 110 and P["elev"] >= 60,
                          behind=lambda P: P["plane"] <= -20).items():
        I = [i for i, P in enumerate(B.poses) if sel(P)]
        if not I: continue
        res = [B.res[i] for i in I]
        out[name] = dict(n=len(I), closes=int(L["ok"][I].sum()), collide=int(L["hit"][I].sum()),
                         taken=int(sum(r is not None and np.min(r) >= 0 for r in res)))
    return out


if __name__ == "__main__":
    B = K.bench(60, 160)
    r = K.evaluate(B, build, PARAMS)
    print({k: r[k] for k in ("reach", "follow", "inband14", "inband10", "contact", "gap", "closure", "flips", "collide",
                             "inband_member", "mass_g", "honest", "audit", "residual_deg", "min_margin")})
    print(pose_report(B, r))
