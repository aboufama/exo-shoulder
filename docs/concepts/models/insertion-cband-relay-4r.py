"""insertion-cband-relay-4r (round 401 K1, judge pick 2, lens C): knee-less O20 3R at the lead's J1 / J2 seats (K WELDED:
plain 3R, no knuckle drive), J3 re-aimed to wdir(95, -8.2) with b3 0 (J3 on a GH ray), member 3 = hub 3's lower plate + a
~93 mm 12 x 3 Ti strap down the lateral arm to a roller carriage at s 0.30 that rides an ARM-FIXED C-band about a GH axis
tilted 8.75 deg (raxis(8.75, -90): its distal end 15 mm posterior of the GH-elbow line at s 0.30). The relay is the
counted 4th revolute J4: one-sided [0, PHI], a constant-force strip on its zero dowel (least-phi physics: the arm turns
the carriage only when the plain dyad leaves its window, to the least phi at which it closes).

STEP 1 (this file's scored reading, the judge's pre-registered gate: ideal bound > 14.0 kills): the LEAD-QUALITY chain
(kfree-armarc-relay-4r.py lead_eval: conecut-knee-knuckle-3r's own fitted metal, frozen protocol, K welded at stop A via
the |dK| <= 0.1 deg gate, drive metal deleted) with
  * the J3 re-aim asserted in the fitted model (M1.p wd 95 / wa -8.2 / b3 0),
  * a2 placed by psi2 (J2's rest axis turned about J1; a1 37.552 kept): psi2 -36.5 / -45 / -53 -> a2 62.0 / 67.3 / 72.0,
  * NO J4 metal (hw 0: no band, carriage or strap) - the ideal bound,
  * KNEE-LESS readings: the knee-side samples (E strap, O12 boss, pad, knee link; contact-only re-read without pad /
    knee) are dropped, as round 401 lens A's k1.py did (a knee-less row keeps only the metal it builds; the round-401
    judge's new-knowledge item 1),
  * benches: envsel (tools/env_bench.py, exact, pick selection) and Bench(110,360) exact frozen (the claim bench);
    held-out never used here.
The kinematic axis convention was checked against the judge's kin_static.py: raxis(8.75, -90) sgn +1 at a2 67 reproduces
312 / 360 static ws and 22 / 28 overhead (scratch icb/axsign.py; sgn -1 gives 285 / 18).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/insertion-cband-relay-4r.py ideal '<json>' envsel|b110|fast [out.json]
    ... kin '<json list>'        (static least-phi kinematics on Bench(110,360) ws, the judge's reading)
"""
import importlib.util, json, math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
os.environ.setdefault("SN_CELL", "lead")
import env_bench as EB                                       # noqa: E402
EB.install()                                                 # envsel poses in the archive BEFORE armarc reads Z0


class _NZ(dict):                                             # armarc reads the archive as an NpzFile (.files)
    @property
    def files(self): return list(self.keys())


EB._ZX["Z"] = _NZ(EB._ZX["Z"])
import concept_bench as CB                                   # noqa: E402
import concept_kit as K                                      # noqa: E402
_sp = importlib.util.spec_from_file_location("kfree_for_icb", os.path.join(HERE, "kfree-armarc-relay-4r.py"))
KF = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(KF)

ID = "insertion-cband-relay-4r"
NAME = "Short-strap ring at the deltoid insertion: knee-less O20 3R, J3 re-aimed, one-sided relay on an arm-fixed C-band at s 0.30"
BASE = dict(PHI=45.0, tilt=8.75, taz=-90.0, sgn=1.0, hw=0, drive=0, wd=95.0, wa=-8.2, b3=0.0, psi2=-45.0)
KNEE_PARTS = ("E", "boss", "pad", "knee")
D2R = math.pi / 180


def _bench(which):
    if which == "envsel": return EB.bench("envsel", exact=True)
    if which == "b110":
        os.environ["CB_EXACT"] = "1"; return CB.Bench(110, 360)
    if which == "fast":
        os.environ.pop("CB_EXACT", None); return CB.Bench(60, 160)
    raise SystemExit(f"bench {which}: envsel | b110 | fast (held-out is the verifier's)")


def readings(M, B, phi_b):
    """full and knee-less readings of the frozen wear (lens A k1.py layout: list(rigid) + list(link_pts), optional appended
    contact-only min re-read without the pad / knee contact members)"""
    names = list(M.rigid) + list(M.link_pts); sizes = [len(X) for _, X in M.rigid.values()] + [len(X) for _, X in M.link_pts.values()]
    cut = np.cumsum([0] + sizes); keep = np.ones(cut[-1], bool); keepK = np.ones(cut[-1], bool)
    for k, n in enumerate(names):
        if n in KNEE_PARTS: keep[cut[k]:cut[k + 1]] = False
        if n in KNEE_PARTS + ("hubK",): keepK[cut[k]:cut[k + 1]] = False
    ws = np.array(B.kind) == "ws"; elev = np.array([p["elev"] for p in B.poses]); res0 = [None if x is None else np.array(x) for x in B.res]
    out = {}
    for tag, mask in (("full", None), ("kneeless", keep), ("kneeless_noK", keepK)):   # noK: the welded K's O20 stack also deleted (optimistic: link 1's bar over it unsampled)
        R = []
        for j in range(len(B.idx)):
            d = res0[j]
            if d is None: R.append(None); continue
            if mask is not None:
                if len(d) == len(mask) + 1:
                    Wc = [M.world(m, j, Pc) for m, Pc in M.contact if m not in (5, 6)]; Wc = [w for w in Wc if len(w)]
                    dck = float(B.dist(j, np.concatenate(Wc)).min()) if Wc else 1e9
                    d = np.r_[d[:-1][mask], dck] if dck < 0 else d[:-1][mask]
                elif len(d) != len(mask): raise SystemExit(f"layout mismatch {len(d)} vs {len(mask)}")
                else: d = d[mask]
            R.append(d)
        B.res = R; r = B.report(); rep = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
        mins = np.array([float(np.min(x)) if x is not None else np.nan for x in R])
        tk = np.isfinite(mins) & (mins >= 0); con = np.isfinite(mins) & (mins < 0); ov = ws & (elev >= 140)
        for thr, nm in ((1.0, "near1"), (2.0, "near2")):
            B.res = [None if x is None else x - thr for x in R]; rn = B.report(); rep[nm] = round(CB.gap_of(rep["inband14"], rn["follow"], rn["reach"], rn["contact"]), 3)
        B.res = R
        pib = {}
        for k, n in enumerate(names):
            if mask is not None and not mask[cut[k]:cut[k + 1]].any(): continue
            acc = [res0[j][cut[k]:cut[k + 1]] for j in range(len(B.idx)) if B.kind[j] == "clip" and tk[j]]
            if acc: dd = np.concatenate(acc); pib[n] = [round(float(((dd >= 2) & (dd <= 14)).mean()), 3), round(float(np.median(dd)), 1), sizes[k]]
        cpart = {}
        for j in np.nonzero(con)[0]:
            x = res0[j]; best = min(((float(x[cut[k]:cut[k + 1]].min()), n) for k, n in enumerate(names) if (mask is None or mask[cut[k]:cut[k + 1]].any())), default=(9, "?"))
            nm = best[1] if best[0] < 0 else "contact-only"; cpart[nm] = cpart.get(nm, 0) + 1
        rel = np.isfinite(phi_b) & (np.abs(phi_b) > 0)
        rep.update(contact_parts=cpart, relayed_contacts=int((con & rel).sum()), ws_taken=int((ws & tk).sum()), ws=int(ws.sum()),
                   overhead=[int((ov & tk).sum()), int(ov.sum())], n_contact=int(con.sum()), depth_sum=round(float(-mins[con].sum()), 2),
                   depth_max=round(float(-mins[con].min()) if con.any() else 0.0, 2),
                   min_metal_taken=round(float(np.nanmin(np.where(tk, mins, np.nan))), 3) if tk.any() else None,
                   contacts=[(int(j), [round(B.poses[j][k]) for k in ("plane", "elev", "axial")], round(float(mins[j]), 2)) for j in np.nonzero(con)[0]][:40],
                   relayed_taken_ws=int((ws & tk & rel).sum()), parts_ib14=pib, _mins=mins)
        out[tag] = rep
    B.res = res0
    return out


def th_margin(M1, B, phi_b, ax, taken):
    """the fold margin in the ONE metric (angle(J1, J3) vs the welded window [|a1-a2| + 5, a1 + a2 - 5]) per taken pose"""
    F = K.frames(B); p = M1.p; u1 = K.bvec(p["az1"], p["el1"]); u3 = K.wdir(p["wd"], p["wa"]); a1, a2 = float(M1.D.a1), float(M1.D.a2)
    ph = np.where(np.isfinite(phi_b), phi_b, 0.0); R = KF._ar().rotm(ax, ph * D2R)
    p1 = F.S(u1); p3 = np.einsum("pij,pjk,k->pi", F.RHG, R, u3)
    th = np.degrees(np.arccos(np.clip((p1 * p3).sum(-1), -1, 1))); lo, hi = abs(a1 - a2), min(a1 + a2, 360 - a1 - a2)
    m = np.minimum(th - lo, hi - th)
    return dict(min_th_margin_taken=round(float(m[taken].min()), 3) if taken.any() else None, window=[round(lo, 2), round(hi, 2)],
                n_below5=int((m[taken] < 5 - 1e-3).sum()))


def ideal(params, which="envsel", flood=False):
    """STEP 1: the lead-quality ideal bound (kfree lead_eval with the bench choice and the knee-less readings)"""
    AR = KF._ar(); CBm = AR.CB; t0 = time.time(); prm = dict(BASE, **params)
    if not hasattr(AR, "_gate_weld"): AR._gate_weld = AR.gate
    q2max = prm.get("q2max")                                        # J2 own-angle dowel (steers the least-phi solve; a design variable)
    if q2max is None: AR.gate = AR._gate_weld
    else:
        def _gq(M, Q, _g=AR._gate_weld, _m=float(q2max)):
            ok = _g(M, Q); q = M.D.ik(Q)[0]; return ok & (np.degrees(q[:, 1]) <= _m)
        AR.gate = _gq
    rp = dict(KF.LPAR); rp.update({k: prm[k] for k in KF.LPAR if k in prm})
    xp = {k: v for k, v in prm.items() if k not in KF.LPAR and k not in ("psi2", "q2max")}
    if float(prm.get("psi2", 0.0)):
        L0 = dict(AR.CC.PARAMS, **AR.LEAD); u1 = K.bvec(L0["az1"], L0["el1"]); u2 = K.bvec(L0["az2"], L0["el2"]); ps = math.radians(float(prm["psi2"]))
        v = K.unit(math.cos(ps) * u2 + math.sin(ps) * np.cross(u1, u2) + (1 - math.cos(ps)) * (u1 @ u2) * u1)
        xp.update(az2=math.degrees(math.atan2(v[2], -v[0])), el2=math.degrees(math.asin(float(np.clip(v[1], -1, 1)))))
    P = dict(AR.CC.PARAMS); P.update(AR.LEAD); P.update(smhi=5.0); P.update(xp); P = AR.CC._clamp(P)
    old = os.environ.pop("CB_EXACT", None)
    try:
        B1 = CBm.Bench(n_clip=60, n_ws=160); M1 = AR.CC.CCModel(B1, dict(P)); r1 = M1.run()
        for k in ("wd", "wa", "b3"):                                # the re-aim is asserted in the FITTED model
            assert abs(float(M1.p[k]) - float(prm[k])) < 1e-6, (k, M1.p[k], prm[k])
        assert abs(float(M1.p.get("smhi", 5.0)) - 5.0) < 1e-6
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]
    phi, ax = AR.solve_phi(M1, rp); phi_fill = np.where(np.isfinite(phi), phi, 0.0); Zr = AR.relayed_Z(phi_fill, ax)

    class Frozen(AR.CC.CCModel):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info", "_wedge_info", "cyl_r"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self.rigid = dict(M1.rigid); self._sc = None; self.contact = list(M1.contact)
            KF._strip_drive(self)
            self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool); self._truncate()
    B = _bench(which); phi_b = phi[B.idx]
    with AR.patched(Zr):
        M = Frozen(B, P2); M.run()
    why = np.asarray(M.why, dtype=object).copy(); nok = ~np.isfinite(phi_b)
    for i in np.nonzero(nok)[0]:
        B.res[i] = None
        if why[i] in ("", "contact", "skin"): why[i] = "kfold"
    M.why = why
    rd = readings(M, B, phi_b); ws = np.array(B.kind) == "ws"
    tk = np.isfinite(rd["kneeless"]["_mins"]) & (rd["kneeless"]["_mins"] >= 0)
    for t_ in rd.values(): t_.pop("_mins", None)
    out = dict(params=prm, bench=which, mode=B.mode, n=len(B.idx), a1a2=[round(float(M1.D.a1), 3), round(float(M1.D.a2), 3)],
               axis=[round(float(x), 4) for x in ax], fit_lead_phi0={k: r1[k] for k in ("gap", "reach", "inband14", "contact")},
               why_ws={str(k): int(((why == k) & ws).sum()) for k in set(why.tolist())},
               relayed_ws=int((ws & np.isfinite(phi_b) & (phi_b != 0)).sum()), kin_ws=int((ws & np.isfinite(phi_b)).sum()),
               phi_max=round(float(np.nanmax(np.abs(phi_b))), 2) if np.isfinite(phi_b).any() else 0.0,
               th=th_margin(M1, B, phi_b, ax, tk), **rd)
    if flood:
        fr = AR.flood_relay(M1, rp); out["flood"] = {k: v for k, v in fr.items() if k not in ("conn", "phi")} if isinstance(fr, dict) else str(fr)[:300]
    out["secs"] = round(time.time() - t0, 1)
    return out


def append_sweep(o, path=None):
    path = path or os.path.join(REPO, "docs", "concepts", "sweeps", ID + ".json")
    try: S_ = json.load(open(path))
    except Exception: S_ = []
    w = o["kneeless"]
    S_.append(dict(k=len(S_), t=K.now(), params=o["params"], bench=o["bench"], mode=o["mode"], step="ideal (no J4 metal, knee-less readings)",
                   inband14=w["inband14"], inband10=w["inband10"], reach=w["reach"], follow=w["follow"], contact=w["contact"], gap=w["gap"],
                   gap_near1=w["near1"], gap_near2=w["near2"], overhead=w["overhead"], n_contact=w["n_contact"], depth_sum=w["depth_sum"],
                   min_metal_taken=w["min_metal_taken"], full_gap=o["full"]["gap"], a1a2=o["a1a2"], why_ws=o["why_ws"], th=o["th"]))
    json.dump(S_, open(path, "w"), indent=0, default=float)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "ideal":
        prm = json.loads(a[1]) if len(a) > 1 else {}; which = a[2] if len(a) > 2 else "envsel"
        o = ideal(prm, which, flood=bool(prm.pop("flood", 0)) if isinstance(prm, dict) else False)
        if len(a) > 3: json.dump(o, open(a[3], "w"), indent=0, default=float)
        if os.environ.get("ICB_APPEND", "1") == "1": append_sweep(o)
        s = {k: v for k, v in o.items() if k not in ("full", "kneeless")}
        s["kneeless"] = {k: v for k, v in o["kneeless"].items() if k not in ("contacts", "parts_ib14")}
        s["full_gap"] = o["full"]["gap"]; s["parts_ib14"] = o["kneeless"]["parts_ib14"]
        print(json.dumps(s, default=float), flush=True)
