"""distal-cband-sq95-relay-4r (round 401 K1, judge pick, lens C at the distal station): knee-less O20 3R at the lead's
J1 / J2 seats (K WELDED: plain 3R, no knuckle drive), J3 re-aimed square to the arm wdir(95, -8.2) with b3 0, member 3 =
hub 3's lower plate + a ~220 mm 12 x 3 Ti strap down the lateral-posterior arm to a 20-deg V-wheel carriage at s 0.70
(227.5 mm) that rides an ARM-FIXED hardened C-band (psi -58..+28) about the GH axis raxis(2.74, -116.6) (= unit(10, 234,
5) in HG: its distal end 10 mm posterior, 5 mm medial of the GH-elbow line at s 0.70). The relay is the counted 4th
revolute J4: one-sided [0, PHI], a CF strip on its zero dowel at psi -45 (least-phi physics: the arm turns the carriage
only when the welded dyad leaves its window, to the least phi at which it closes; the carriage rolls -45 -> -45 + phi).

Same layout as insertion-cband-relay-4r.py (its readings / th margin / J4 geometry / J4 wear are imported, not copied):
this file changes the station (s 0.70, axis offset 11.18 mm), the race arc, the sampling radius (r_ref 60: the race
radius here is 45-65 mm, so a 2 mm step at r_ref 45 under-sampled the outer race) and adds the judge's re-registered
STRAP GATE (step 0) and per-part in-band arrays.

STEPS (the judge's pre-registered order):
  step 0  strap gate on the frozen PHI-0 fit (Bench(60,160) fast): kill if the strap's own in-band on the taken clip
          frames < 0.85, or strap + band torso / other-skin losses on Bench(60,160) > 11 poses, or the strap deflects
          > 1 mm at the carriage under a 3 N relay load (fixed at hub 3, pinned on the band; analytic, below);
  step 1  ideal bound (no J4 metal, knee-less readings; kill > 14.0): envsel exact (selection), then frozen exact
          Bench(110,360) (the claim bench);
  step 2  hardware (every J4 part sampled at its real envelope): band underside 2D-contoured per (psi, w) at q 1, race a
          surface of revolution R(w), carriage plate 2.5 mm at R + 0.5, 4 wheel blocks at the band edges, strap.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/distal-cband-sq95-relay-4r.py ideal '<json>' fast|envsel|b110 [out.json]
    (j4: 1 in the json adds the hardware reading and the strap gate; flood: 1 adds the continuity flood)
"""
import importlib.util, json, math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
_src = open(os.path.join(HERE, "insertion-cband-relay-4r.py")).read()
_old = "r_ref = 45.0; dpsi = math.degrees(st / r_ref)"
assert _src.count(_old) == 1
_src = _src.replace(_old, "r_ref = float(h.get('r_ref', 45.0)); dpsi = math.degrees(st / r_ref)")
_oldc = 'med = np.nanmedian(t, 0); t = np.where(t <= med[None, :] + float(h["out_mm"]), t, np.nan)'
assert _src.count(_oldc) == 1                               # pose_cut 1: a fit pose with OTHER skin (> median + out_mm) over
_src = _src.replace(_oldc, _oldc + "; _bp = (np.nan_to_num(t, nan=-1e9) > -1e8).sum(1) < np.isfinite(med).sum(); "   # any band ray leaves
                    "t = np.where(_bp[:, None] & bool(h.get('pose_cut', 0)), np.nan, t)")                            # the band's fit set whole (it is LOST in the wear)
_olds = "rS = np.where(np.isfinite(rq), blend * np.maximum(rq, 0) + (1 - blend) * rlin, rlin)"
assert _src.count(_olds) == 1                               # strap_floor 1: the strap underside never below its own fitted
_src = _src.replace(_olds, _olds + "; rS = np.where(np.isfinite(rq) & bool(h.get('strap_floor', 0)), np.maximum(rS, rq), rS)")  # requirement:
# the hub-3 end is a joggle onto the OUTER face of hub 3's lower plate where the deltoid stands above the plate's underside
# (the insertion row's 10-mm ramp to the plate underside put 27 of 38 Bench(60,160) strap contacts at t = 0, 0.1-1.6 mm)
_oldt = 't = K.requirement(B1, I, np.einsum("pij,nj->pni", Rw_, sdir).reshape(-1, 3), clr=float(h["clr"]))'
assert _src.count(_oldt) == 1                               # t1_strap: the strap's GH rays reach 240 mm at s 0.70; the kit's
_src = _src.replace(_oldt, _oldt[:-1] + ', t1=float(h.get("t1_strap", 220.0)))')   # default march end (220) left its distal ~20 mm
# UNFITTED (inf -> the straight radius interpolation, through or above the arm by luck: the first sweep's strap losses
# jumped 12 -> 49 between neighbouring cells; q_band 0.9 put the strap in every pose)
ICB = type(sys)("icb_for_dcb"); ICB.__file__ = os.path.join(HERE, "insertion-cband-relay-4r.py")
exec(compile(_src, ICB.__file__, "exec"), ICB.__dict__)
K, KF, CB, EB = ICB.K, ICB.KF, ICB.CB, ICB.EB

ID = "distal-cband-sq95-relay-4r"
NAME = ("Knee-less O20 3R, J3 square to the arm wdir(95, -8.2), one-sided relay PHI 60 on an arm-fixed C-band at s 0.70 "
        "about raxis(2.74, -116.6), ~220 mm strap, V-wheel carriage")
BASE = dict(PHI=60.0, tilt=2.74, taz=-116.6, sgn=1.0, hw=0, drive=0, wd=95.0, wa=-8.2, b3=0.0, psi2=-45.0)
HW = dict(ICB.HW, s_frac=0.70, L_arm=325.0, post=math.hypot(10.0, 5.0), psi0=-45.0, band_lo=-58.0, band_hi=28.0,
          car_half=10.0, wheel_psi=7.0, q_band=1.0, q_strap=1.0, r_ref=60.0, t1_strap=300.0)
ICB.ID, ICB.BASE, ICB.HW = ID, BASE, HW
D2R = math.pi / 180

# strap stiffness (step-0 gate item 3): 12 x 3 Ti-6Al-4V, cantilever from hub 3's plate, load at the carriage
E_TI, G_TI = 114e3, 44e3                                     # N/mm2


def strap_deflection(L, F=3.0, w=12.0, t=3.0, ecc=5.0):
    """tip deflection (mm) of the strap under the relay load: the load is tangential to the race at the carriage, i.e.
    in the strap's WIDTH direction (strong axis, I = t w^3 / 12); the weak-axis figure (radial load, reacted by the
    wheels' radial capture, not by the strap) and the twist from the load's radial offset ecc are reported too"""
    Is, Iw = t * w ** 3 / 12, w * t ** 3 / 12; J = (1 / 3 - 0.21 * t / w * (1 - (t / w) ** 4 / 12)) * w * t ** 3
    return dict(L=round(L, 1), strong_mm=round(F * L ** 3 / (3 * E_TI * Is), 3), weak_mm=round(F * L ** 3 / (3 * E_TI * Iw), 3),
                twist_deg=round(math.degrees(F * ecc * L / (G_TI * J)), 3), twist_mm_at_car=round(F * ecc * L / (G_TI * J) * ecc, 4))


def _geom_hook(AR, M1, B1, phi, ax, h):
    """strap_rim (default 10 mm): the strap's samples inside hub 3's O20 footprint (arc length < 10 mm from hub 3's
    centre) ARE hub 3's lower plate (already sampled as hub3); the strap starts at the plate's rim. Measured reason: with
    the insertion row's ramp to the plate centre's underside, 27 of 38 Bench(60,160) strap contacts sat on the first row
    (t = 0, 0.1-1.6 mm, inside the hub's footprint, where hub 3's own samples clear)"""
    G = ICB._j4_geometry0(AR, M1, B1, phi, ax, h); rim = float(h.get("strap_rim", 10.0))
    nw = len(np.arange(-h["strap_w"] / 2, h["strap_w"] / 2 + 1e-6, h["step"])); ns = len(G["strap"]); nst = ns // nw
    tS = np.repeat(np.linspace(0, 1, nst), nw) * float(G["strap_len_mm"]); G["strap"] = G["strap"][tS >= rim]
    G["n"]["strap"] = len(G["strap"]); return G


ICB._j4_geometry0 = ICB.j4_geometry
ICB.j4_geometry = _geom_hook


_WEAR = {}


def _wear_hook(AR, M, B, G, phi_b, ax):
    ex, jam = ICB._j4_wear0(AR, M, B, G, phi_b, ax); _WEAR.update(G=G, ex=ex, jam=jam, B=B, M=M, phi_b=phi_b); return ex, jam


ICB._j4_wear0 = ICB.j4_wear
ICB.j4_wear = _wear_hook


def strap_gate(o):
    """the judge's re-registered strap gate from the stored hardware wear: strap own in-band on the hardware-taken clip
    frames, strap / band losses (poses the IDEAL takes that the strap or band makes contacts), deflection"""
    G, ex, jam, B = _WEAR["G"], _WEAR["ex"], _WEAR["jam"], _WEAR["B"]
    ns = len(G["strap"]); kind = np.array(B.kind); out = {}
    ideal_taken = set(o["_ideal_taken"]); hw_taken = set(o["_hw_taken"])
    sd = [ex[j]["d"][-ns:] for j in ex if j in hw_taken and kind[j] == "clip"]
    sd = np.concatenate(sd) if sd else np.zeros(1)
    out["strap_ib14_taken_clip"] = round(float(((sd >= 2) & (sd <= 14)).mean()), 3)
    out["strap_ib10_taken_clip"] = round(float(((sd >= 2) & (sd <= 10)).mean()), 3)
    out["strap_p5_50_95"] = np.percentile(sd, [5, 50, 95]).round(2).tolist()
    lost = {"strap": [0, 0], "band": [0, 0], "car_wheels": [0, 0], "jam": [0, 0]}
    for j in ideal_taken:
        if j not in ex: continue
        c = 0 if kind[j] == "ws" else 1
        if jam.get(j, 9) < 1.0: lost["jam"][c] += 1; continue
        if ex[j]["strap"] < 0: lost["strap"][c] += 1
        elif ex[j]["band"] < 0: lost["band"][c] += 1
        elif min(ex[j]["car"], ex[j]["wheels"]) < 0: lost["car_wheels"][c] += 1
    out["losses_ws_clip"] = lost; out["strap_band_losses"] = sum(lost["strap"]) + sum(lost["band"])
    out["deflection_3N"] = strap_deflection(float(G["strap_len_mm"]))
    out["kill"] = bool(out["strap_ib14_taken_clip"] < 0.85 or out["strap_band_losses"] > 11 or out["deflection_3N"]["strong_mm"] > 1.0)
    return out


def ideal(params, which="envsel", flood=False):
    """ICB.ideal with this row's BASE / HW, plus the taken masks for the strap gate"""
    prm = dict(BASE, **params); _WEAR.clear()
    o = ICB.ideal(prm, which, flood=flood)
    if "J4" in o and _WEAR:
        B, M, phi_b = _WEAR["B"], _WEAR["M"], _WEAR["phi_b"]
        # ideal-taken = the knee-less chain reading closes without contact; hardware-taken = + every J4 part >= 0, no jam
        res = [None if x is None else np.asarray(x) for x in B.res]
        names = list(M.rigid) + list(M.link_pts); sizes = [len(X) for _, X in M.rigid.values()] + [len(X) for _, X in M.link_pts.values()]
        cut = np.cumsum([0] + sizes); keep = np.ones(cut[-1], bool)
        for k, n in enumerate(names):
            if n in ICB.KNEE_PARTS: keep[cut[k]:cut[k + 1]] = False
        it, ht = [], []
        for j, d in enumerate(res):
            if d is None: continue
            dd = d[:-1][keep] if len(d) == len(keep) + 1 else d[keep]
            if dd.min() >= 0:
                it.append(j)
                e = _WEAR["ex"].get(j)
                if e is not None and _WEAR["jam"].get(j, 9) >= 1.0 and e["d"].min() >= 0: ht.append(j)
        o["_ideal_taken"], o["_hw_taken"] = it, ht
        o["strap_gate"] = strap_gate(o)
        G = _WEAR["G"]; o["J4"]["race_psi"] = [HW["band_lo"], HW["band_hi"]]
    return o


def append_sweep(o, path=None):
    """one entry per configuration: the HARDWARE reading (every J4 part sampled) when j4 is on, else the ideal; the other
    reading rides along under 'ideal' / the strap gate under 'strap_gate'"""
    path = path or os.path.join(REPO, "docs", "concepts", "sweeps", ID + ".json")
    try: S_ = json.load(open(path))
    except Exception: S_ = []
    hw = "hw_kneeless" in o; w = o["hw_kneeless" if hw else "kneeless"]; wi = o["kneeless"]
    e = dict(k=len(S_), t=K.now(), params=o["params"], bench=o["bench"], mode=o["mode"],
             step="hardware (every J4 part sampled)" if hw else "ideal (no J4 metal, knee-less readings)",
             inband14=w["inband14"], inband10=w["inband10"], reach=w["reach"], follow=w["follow"], contact=w["contact"], gap=w["gap"],
             gap_near1=w["near1"], gap_near2=w["near2"], overhead=w["overhead"], n_contact=w["n_contact"], depth_sum=w["depth_sum"],
             min_metal_taken=w["min_metal_taken"], a1a2=o["a1a2"], why_ws=o["why_ws"], th=o["th"])
    if hw:
        e["ideal"] = {k: wi[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "near1", "overhead", "n_contact")}
        e["strap_gate"] = o.get("strap_gate"); J = o["J4"]
        e["J4"] = {k: J[k] for k in ("car_ib14", "car_p5_50_95", "band_ib14", "band_p5_50_95", "jams")}; e["J4"]["R_race"] = J["geom"]["R_race"]
        e["J4"]["contact_poses"] = {k: J[k]["contact_poses_all"] for k in ("band", "car", "wheels", "strap")}
    S_.append(e); json.dump(S_, open(path, "w"), indent=0, default=float)


def sweep(cfgs, which="fast", out=None):
    """configurations in order, one process (the fit is re-run per configuration: the chain parameters may change)"""
    for c in cfgs:
        o = ideal(dict(c), which); o.pop("_ideal_taken", None); o.pop("_hw_taken", None); append_sweep(o)
        r = o.get("hw_kneeless", o["kneeless"]); g = o.get("strap_gate", {})
        print(json.dumps(dict(cfg=c, hw=r["gap"], ideal=o["kneeless"]["gap"], reach=r["reach"], follow=r["follow"], ib14=r["inband14"], contact=r["contact"],
                              ov=r["overhead"], car_ib14=o.get("J4", {}).get("car_ib14"), losses=g.get("losses_ws_clip"), strap_ib=g.get("strap_ib14_taken_clip"))), flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "ideal":
        prm = json.loads(a[1]) if len(a) > 1 else {}; which = a[2] if len(a) > 2 else "envsel"
        fl = bool(prm.pop("flood", 0))
        o = ideal(prm, which, flood=fl); o.pop("_ideal_taken", None); o.pop("_hw_taken", None)
        if len(a) > 3: json.dump(o, open(a[3], "w"), indent=0, default=float)
        if os.environ.get("DCB_APPEND", "1") == "1": append_sweep(o)
        s = {k: v for k, v in o.items() if k not in ("full", "kneeless", "kneeless_noK", "hw_kneeless", "hw_kneeless_noK")}
        s["kneeless"] = {k: v for k, v in o["kneeless"].items() if k not in ("contacts", "parts_ib14")}
        s["parts_ib14"] = o["kneeless"]["parts_ib14"]
        if "hw_kneeless" in o: s["hw_kneeless"] = {k: v for k, v in o["hw_kneeless"].items() if k not in ("contacts",)}
        print(json.dumps(s, default=float), flush=True)
    elif a[0] == "sweep":
        sweep(json.load(open(a[1])), a[2] if len(a) > 2 else "fast")
    elif a[0] == "defl":
        print(json.dumps(strap_deflection(float(a[1]) if len(a) > 1 else 220.0)))
