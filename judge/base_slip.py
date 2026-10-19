"""R10 model for a GIRDLE-RIDING base (the base rides the scapula on the user's scapula handler): how far the chain's
centre moves from the true GH centre because the handler, held on skin, slips over the bone. Literature model, not a
fit; assumptions, sources and uncertainty in docs/research/base_slip_model.md.

The handler is treated like an acromion marker cluster (AMC: a rigid body strapped to the skin over the flat of the
acromion - the measured analogue): relative to the bone it rotates by small angles about the three ISB scapula axes
(Wu et al. 2005: Xs anterior, Ys superior, Zs lateral along the spine; internal / external rotation about Ys, upward
rotation about Xs, posterior tilt about Zs) about its own centre on the acromion, and its centre translates by d. A
spherical chain centred on the GH centre at rest (fixed in the handler) then carries its centre to
    c(t) = A + R_err(t) (GH - A) + d(t)        ->  misalignment = |(R_err - I) r + d|,  r = GH - A (scapula frame)
r does not depend on the pose (GH and A both ride the scapula), so the misalignment is a function of the per-axis
error angles (which depend on humeral elevation and plane: published AMC-vs-bone errors) and of the lever r (the
OpenSim Seth 2016 scapula: markers aa, ac and the GH joint centre, scaled to the rig's AC-GH distance).

Laws (error angles in deg vs humerothoracic elevation e and plane of elevation p, 0 = abduction .. 90 = flexion):
  central  0 at rest (the handler is fitted with the arm hanging, as an AMC is calibrated), growing linearly to
           7 (abduction) .. 5 (flexion) deg on every axis at 100 deg (Lempereur 2014 review; van Andel 2009: <= 6 deg);
           100 -> 120: linear to the upper ends of Karduna 2001's RMS errors (UR 6.3, PT 8.6, IR/ER 11.4 deg);
           120 -> 150: IR/ER linear to 25 deg (Karduna 2001: "up to 25 deg at maximal elevation"); UR, PT held;
           translation |d| = 4.2 mm x min(e, 150) / 150 (McQuade & Smidt 1998 acromial-module skin slip, via Matsui 2006);
           axes combined root-sum-square (independent errors).
  low      the review's best case: 0 at rest growing to 5 deg on every axis at 100 deg, held there (no overhead
           growth), no translation; RSS.
  high     the central angles read as errors that are already there just above rest (no ramp from 0: the 5-7 deg
           apply from e = 0), combined with the worst signs (exact composite rotation, 8 sign patterns), translation
           added in the worst direction - an upper bound (correlated errors).
R10's metric is the central law's worst frame; low / high bracket it.

    import base_slip as BS
    m = BS.misalignment(P)          # P (T, >=2): plane, elevation (deg)  ->  {law: (T,) mm}
    python3 judge/base_slip.py      # the model's self-checks (simple cases with known answers) + a table
"""
import json, math, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); SETH = os.path.join(HERE, "..", "pipeline", "girdle", "opensim_seth")
D2R = math.pi / 180
AXES = ("UR", "IR", "PT")                                   # rotation about Xs, Ys, Zs (ISB scapula)
KARDUNA_RMS_HI = dict(UR=6.3, PT=8.6, IR=11.4)              # upper ends of the acromion method's RMS errors (deg)
KARDUNA_MAX_IR = 25.0                                       # "up to 25 degrees at maximal elevation" (IR/ER)
LEMPEREUR = dict(abduction=7.0, flexion=5.0)                # AMC, single calibration, below 90-100 deg (deg)
SLIP_MM = 4.2                                               # acromial-module skin slip (McQuade & Smidt 1998)
E_LO, E_MID, E_MAX = 100.0, 120.0, 150.0


def lever(anchor="mid", scale=None):
    """r = GH - A in the ISB scapula frame (mm) from the Seth 2016 model's own markers, scaled to the rig's AC-GH
    distance (compare.json) unless scale is given. anchor: 'mid' (flat of the acromion: midpoint of the acromial angle
    aa and the AC joint ac), 'aa' or 'ac'."""
    mf = json.load(open(os.path.join(SETH, "model_facts.json"))); M = mf["markers"]
    A = np.array(mf["frame_mapping"]["scapula_isb_axes_in_scapula_body"])           # columns = Xs, Ys, Zs in body coords
    gh = np.array(mf["check_gh_centre"]["gh_joint_location_in_scapula_mm"]); aa = 1000 * np.array(M["aa"]["loc_m"]); ac = 1000 * np.array(M["ac"]["loc_m"])
    P = dict(mid=0.5 * (aa + ac), aa=aa, ac=ac)[anchor]
    if scale is None:
        g = json.load(open(os.path.join(SETH, "compare.json")))["geometry"]; scale = np.linalg.norm(g["rig_AC_GH_mm"]) / np.linalg.norm(gh - ac)
    return scale * ((gh - P) @ A), scale


def angles(P, law="central"):
    """(T, 3) error angles in deg about (Xs, Ys, Zs) = (UR, IR, PT) and (T,) translation slip in mm"""
    P = np.atleast_2d(np.asarray(P, float)); pl = np.clip(P[:, 0], 0, 90); e = np.clip(P[:, 1], 0, None); T = len(P)
    ramp = np.minimum(e, E_LO) / E_LO                                             # 0 at the fitting posture (arm hanging)
    if law == "low": return np.repeat((5.0 * ramp)[:, None], 3, 1), np.zeros(T)
    base = LEMPEREUR["abduction"] + (LEMPEREUR["flexion"] - LEMPEREUR["abduction"]) * pl / 90.0
    if law == "central": base = base * ramp
    out = np.zeros((T, 3))
    for k, ax in enumerate(AXES):
        hi = KARDUNA_RMS_HI[ax]; u = np.clip((e - E_LO) / (E_MID - E_LO), 0, 1)
        out[:, k] = base + u * (hi - base)
        if ax == "IR": out[:, k] += np.clip((e - E_MID) / (E_MAX - E_MID), 0, 1) * (KARDUNA_MAX_IR - hi)
    return out, SLIP_MM * np.minimum(e, E_MAX) / E_MAX


def rot(axis, a):
    ax = np.asarray(axis, float); K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    return np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * K @ K


E3 = np.eye(3)
def misalignment(P, r=None, laws=("central", "low", "high")):
    """{law: (T,) mm} GH misalignment of a spherical chain on a handler that slips by the law's errors (r: lever, ISB)"""
    r = lever()[0] if r is None else np.asarray(r, float); out = {}
    for law in laws:
        th, d = angles(P, law); th = th * D2R
        if law == "high":                                                         # worst signs, exact ISB Y-X-Z composite
            best = np.zeros(len(th))
            for s in np.array(np.meshgrid([-1, 1], [-1, 1], [-1, 1])).T.reshape(-1, 3):
                v = np.array([np.linalg.norm((rot(E3[1], s[1] * t[1]) @ rot(E3[0], s[0] * t[0]) @ rot(E3[2], s[2] * t[2]) - E3) @ r) for t in th])
                best = np.maximum(best, v)
            out[law] = best + d
        else:                                                                     # independent axes: root-sum-square
            per = np.stack([np.linalg.norm(np.einsum("tij,j->ti", np.stack([rot(E3[k], t) for t in th[:, k]]) - E3, r), axis=1) for k in range(3)], 1)
            out[law] = np.sqrt((per ** 2).sum(1) + d ** 2)
    return out


def selftest():
    """simple cases with known answers"""
    ok = True
    def check(name, got, want, tol=1e-6):
        nonlocal ok; good = abs(got - want) <= tol; ok &= good; print(f"  {'ok ' if good else 'BAD'} {name}: {got:.6f} (expected {want:.6f})")
    r = np.array([0.0, -40.0, 0.0])                                               # GH 40 mm straight below the anchor
    # one axis only: rotation by a about Xs moves a lever perpendicular to it by 2 |r| sin(a / 2); about Ys (parallel) by 0
    a = 10 * D2R; check("10 deg about Xs, lever 40 mm perpendicular", np.linalg.norm((rot(E3[0], a) - E3) @ r), 2 * 40 * math.sin(a / 2))
    check("10 deg about Ys, lever 40 mm parallel", np.linalg.norm((rot(E3[1], a) - E3) @ r), 0.0)
    # low law at 100 deg: 5 deg on all three axes, RSS = sqrt(2) |r| 2 sin(2.5 deg) for a lever along one axis (two axes see it)
    m = misalignment([[0, 100]], r=r, laws=("low",))["low"][0]; check("low law at 100 deg, lever along Ys", m, math.sqrt(2) * 2 * 40 * math.sin(2.5 * D2R))
    m = misalignment([[0, 0]], r=r, laws=("central", "low")); check("central at rest (fitting posture)", m["central"][0], 0.0); check("low at rest", m["low"][0], 0.0)
    # zero lever: only the translation slip remains (central at 150 deg: 4.2 mm)
    m = misalignment([[0, 150]], r=np.zeros(3), laws=("central", "high"));  check("zero lever, central, 150 deg", m["central"][0], SLIP_MM); check("zero lever, high, 150 deg", m["high"][0], SLIP_MM)
    # symmetry: below 100 deg the central angles are equal on all axes, so a Ys-lever and a Zs-lever (each perpendicular
    # to two of the axes) give the same RSS
    m1 = misalignment([[30, 60]], r=r, laws=("central",))["central"][0]; m2 = misalignment([[30, 60]], r=np.array([0, 0, -40.0]), laws=("central",))["central"][0]
    check("Ys- vs Zs-lever, central, equal angles below 100 deg", m1, m2)
    # ordering: RSS <= worst-sign composite + translation
    P = np.array([[0, 30], [0, 90], [45, 120], [90, 150], [0, 170]]); m = misalignment(P)
    good = bool(np.all(m["low"] <= m["central"] + 1e-9) and np.all(m["central"] <= m["high"] + 1e-9)); ok &= good
    print(f"  {'ok ' if good else 'BAD'} low <= central <= high on {len(P)} poses")
    return ok


if __name__ == "__main__":
    print("self-checks:"); good = selftest()
    r, s = lever(); print(f"lever GH - flat of the acromion (ISB scapula, x{s:.3f} to the rig): {np.round(r, 1)} mm, |r| {np.linalg.norm(r):.1f} mm")
    for an in ("aa", "ac"): ra, _ = lever(an); print(f"  anchor {an}: {np.round(ra, 1)} |r| {np.linalg.norm(ra):.1f}")
    print(" plane elev | angles UR IR PT (deg) slip | central  low  high (mm)")
    for p, e in [(0, 0), (0, 30), (0, 60), (0, 90), (90, 90), (0, 100), (0, 120), (40, 135), (0, 150), (90, 150)]:
        th, d = angles([[p, e]]); m = misalignment([[p, e]], r)
        print(f" {p:5.0f} {e:4.0f} | {th[0, 0]:5.1f} {th[0, 1]:5.1f} {th[0, 2]:5.1f}  {d[0]:4.1f} | {m['central'][0]:6.2f} {m['low'][0]:5.2f} {m['high'][0]:5.2f}")
    raise SystemExit(0 if good else 1)
