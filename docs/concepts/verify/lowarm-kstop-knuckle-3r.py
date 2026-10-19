#!/usr/bin/env python3
"""Independent verifier harness for lowarm-kstop-knuckle-3r (round 15, lens B, pick 1).

The claim's model (docs/concepts/models/lowarm-kstop-knuckle-3r.py) is loaded UNCHANGED and worn through its own frozen protocol
(fit Bench(60,160) fast -> shape frozen -> worn on Bench(110,360) exact / held out, dwell K = law + delta, J2 dowel cut at 46.35).
The verifier adds ONE metal correction (V-ARM) on top, selectable:

  V-ARM  the crank's short arm is sampled by the parent (desmo-conecut-knuckle-3r.py line 267) as ONE sheet at the pin centre
         - 1.0 mm along u2. The claim's own write-up reads that sheet as the arm's TOP face and gives the arm a thickness
         (build spec t <= 1.38 at the tip; the gen-9 CAD's S1_T = 1.5), so the arm's skin-facing underside, t below the sheet,
         was never sampled. --arm-t T adds the underside: the same 8 x 3 stations, shifted -T along u2 (crank frame, member 9,
         contact list = skin-checked metal), i.e. the real envelope of the short arm. T = 0 reproduces the claim.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/lowarm-kstop-knuckle-3r.py wear <delta> <bench|held> <out.json>
        [--arm-t 1.38] [--dump PATH] [--flood]   (--flood: the continuity flood, connected() of minarc-stop-knuckle-4r-mechanism.py,
        on the post-dowel bench)
"""
import importlib.util, json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


KM = _load("kstop_claim_for_verify", os.path.join(REPO, "docs", "concepts", "models", "lowarm-kstop-knuckle-3r.py"))
ARM_T = [0.0]
INFO = {}
_orig_h = KM._harness


def _h():
    T, V, LM, DS, S, PLAY = _orig_h()
    INFO["_V"] = V
    b0 = LM.LHModel._desmo_build_B

    def b_arm(self):
        out = b0(self)
        if ARM_T[0] > 0:
            g = self._scg; dm = self._desmo; dR = np.asarray(g["dR"], float); F0 = np.asarray(dm["F0"], float); s0 = float(dm["s0"])
            u2 = np.asarray(self.D.u[1], float); A0 = s0 * dR; seg = np.linspace(0, 1, 8)
            bn = np.cross(dR, F0 - A0); bn = bn / np.linalg.norm(bn); W = 3.0
            try: W = float(DS.ARM_W)
            except Exception: pass
            lo = np.array([A0 + t_ * (F0 - A0) + w_ * bn - (1.0 + ARM_T[0]) * u2 for t_ in seg for w_ in (-W / 2, 0.0, W / 2)])
            self.contact.append((9, lo))
            H2 = float(np.asarray(self.D.c[1], float) @ u2 + float(self.f[1]))
            INFO.update(arm_t=ARM_T[0], n_added=len(lo), arm_W=W, underside_level_over_F=[round(float((lo @ u2).min() - H2), 3), round(float((lo @ u2).max() - H2), 3)],
                        sheet_level_over_F=[round(float((A0 @ u2) - 1.0 - H2), 3), round(float((F0 @ u2) - 1.0 - H2), 3)])
        return out

    LM.LHModel._desmo_build_B = b_arm
    return T, V, LM, DS, S, PLAY


KM._harness = _h


def th_margin_sided(V, delta):
    """V3b: the fold margin th (tools/concept_kit.py lines 25-30) with a dwell flag that does not key on dK != 0: a dwell pose
    carries dK = sp * delta exactly (PlayDesign), so it is read with the EFFECTIVE dyad (a1e = angle(u1, R1b u2), a2e) like a
    forced pose's J1-J3 dyad, and the K sub-dyad m_sub (the lead's G4 WATCH item, ~0 on rest poses) is reported apart"""
    fit, M1, M, B, r = V.CAP["res"]; D = M.D; u1, u2, u3 = D.u; uK = D.uK
    sp = float(M._scg["sp"]) if getattr(M, "_scg", None) else 1.0; dKd = sp * math.radians(delta)
    rows = []
    for i in V.taken_of(B):
        R1, _ = M.T(1, i); R1b, _ = M.T(7, i); R2, _ = M.T(2, i)
        jK = R1 @ uK; j2 = R1b @ u2; j3 = R2 @ u3
        th = V._ang(u1, j3); a1e = V._ang(u1, j2); a2e = V._ang(j2, j3); b1 = V._ang(u1, jK); c = V._ang(jK, j3)
        dk = float(M.dK[i]); dwell = abs(dk - dKd) < 1e-6
        m3 = V._dm(th, a1e, a2e); msub = V._dm(th, b1, c)
        rows.append(dict(i=int(i), dwell=bool(dwell), th=round(th, 2), dK=round(math.degrees(dk), 3), m_th=round(m3, 3), m_sub=round(msub, 3),
                         own=round(m3 if dwell else min(m3, msub), 3)))
    dw = [x for x in rows if x["dwell"]]; fo = [x for x in rows if not x["dwell"]]
    return dict(n=len(rows), n_dwell=len(dw), n_forced=len(fo), min_th_dwell=min([x["m_th"] for x in dw] or [None]),
                min_own_forced=min([x["own"] for x in fo] or [None]), lt5_dwell=sum(1 for x in dw if x["m_th"] < 5 - 1e-6),
                lt5_forced=sum(1 for x in fo if x["own"] < 5 - 1e-6), msub_lt1_dwell=sum(1 for x in dw if x["m_sub"] < 1.0),
                lowest_dwell=sorted(dw, key=lambda x: x["m_th"])[:4], lowest_forced=sorted(fo, key=lambda x: x["own"])[:4])

def worst_dump(outp, paths, note=""):
    """per-pose worst of the sided wears (the claim's combine rule: contact < not taken < taken by in-band share, then metal) written as
    an alignment_paired.py per-pose dump (docs/alignment/remeasure/<id>_<wear>_perpose.json)"""
    D = [json.load(open(p_)) for p_ in paths]; n = len(D[0]["poses"]); W = []
    eff = lambda r: None if r["min_mm"] is None else min(r["min_mm"], r["cmin"] if r["cmin"] is not None else 9e9)
    rk = lambda r: (0 if r["contact"] else (1 if not r["taken"] else 2), (r.get("nib", 0) / max(r.get("ns", 1), 1)) if r["taken"] else 0,
                    eff(r) if eff(r) is not None else 9e9)
    for i in range(n): W.append(dict(min([d["poses"][i] for d in D], key=rk)))
    rec = KM.AP.gap_parts(W)
    json.dump(dict(id=KM.ID, wear=D[0]["wear"], params=D[0]["params"], frozen=dict(gap=rec["gap"]), poses=W, recomputed=rec, sources=paths,
                   exact=all(d.get("exact") for d in D), note="per-pose worst of the sided dwell wears; written by docs/concepts/verify/lowarm-kstop-knuckle-3r.py "
                   + note), open(outp, "w"), default=float)
    print(json.dumps(rec))


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "worst":
        worst_dump(sys.argv[2], sys.argv[3:]); sys.exit(0)
    if "--arm-t" in sys.argv: ARM_T[0] = float(sys.argv[sys.argv.index("--arm-t") + 1])
    if mode == "wear":
        d, which, outp = float(sys.argv[2]), sys.argv[3], sys.argv[4]
        dump = sys.argv[sys.argv.index("--dump") + 1] if "--dump" in sys.argv else None
        o = KM.wear(d, which, dump, {})
        V = INFO.pop("_V")
        o["v3b_th_margin"] = th_margin_sided(V, d)
        if "--flood" in sys.argv:
            import time as _t
            fit, M1, M, B, r = V.CAP["res"]
            MECH = _load("minarc_mech_for_kstop_v", os.path.join(HERE, "minarc-stop-knuckle-4r-mechanism.py"))
            t1 = _t.time(); cr = MECH.connected_report(M, B); cr["secs"] = round(_t.time() - t1, 1)
            o["connected"] = {k: v for k, v in cr.items() if k != "static"}
        o["verify_arm"] = dict(INFO); o["verify_note"] = "verifier V-ARM: short-arm underside sampled at sheet - arm_t (0 = the claim's metal)"
        json.dump(o, open(outp, "w"), indent=1, default=float)
        print(json.dumps({k: o.get(k) for k in ("delta", "wear", "frozen", "dowel", "play_info", "named", "recomputed", "secs", "verify_arm", "connected", "v3b_th_margin")}
                         | {"v": {k: (o["verifier"] or {}).get(k) for k in ("why", "overhead", "near1", "minmetal", "contacts")}}, default=float))
