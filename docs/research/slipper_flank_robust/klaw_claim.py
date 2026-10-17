"""Claim the verified slipper-nose config with an AS-BUILT K law on the worn bench only (questions A and C).

The claim is tools/slipper_env_polish.py claim (the verifier's harness H.frozen_wear, unchanged: fit Bench(60,160) fast,
shape frozen, worn exact, flood on, per-pose dump). The fit bench keeps the nominal law (the CAD shape is cut from it).
On the worn bench the slaved law is replaced by the as-built one: |dK| -> |dK| + e(|dK|) for every forced state (t > 0),
and th(t) is recomputed from the shifted K, so every forced pose is re-solved exactly on the as-built law (the model's
own fold rule then drops a pose whose margin falls under the reading's margin). Rest poses keep K on stop A.

    e = constant:  KLAW_OFF=0.75            (the red team's built-in K lead: lobe-ring dowel phase +0.35 deg of q2)
    e = from asbuilt.json: KLAW_CASE='beta -0.25 deg'  (the solved as-built K error of that case), KLAW_OFF adds to it
    CB_EXACT=1 CB_FOLD_MARGIN=5 ENVP_NOPRICE=1 SN_CELL=lead python3 docs/research/slipper_flank_robust/klaw_claim.py <bench|held> OUT.json
"""
import importlib.util, json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
sp_ = importlib.util.spec_from_file_location("slipper_env_polish_klaw", os.path.join(REPO, "tools", "slipper_env_polish.py"))
EP = importlib.util.module_from_spec(sp_); sp_.loader.exec_module(EP)
H = EP.H
OFF = float(os.environ.get("KLAW_OFF", "0"))
CASE = os.environ.get("KLAW_CASE", "")
if CASE:
    cs = {}
    for fn in ("asbuilt.json", "asbuilt_extra.json"): cs.update(json.load(open(os.path.join(HERE, fn)))["cases"])
    cs = cs[CASE]["err_law"]
    KL, ER = np.array(cs["k"], float), np.array(cs["err"], float)
else:
    KL, ER = np.array([0.0, 90.0]), np.zeros(2)


def efun_deg(k): return np.interp(k, KL, ER) + OFF


def rotms(ax, a):
    a = np.asarray(a, float); ax = ax / np.linalg.norm(ax); K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    return np.eye(3)[None] + np.sin(a)[:, None, None] * K[None] + (1 - np.cos(a))[:, None, None] * (K @ K)[None]


STATE = dict(on=False, patched=False, info=None)


def patch_law(cls):
    orig = cls.law

    def law(self):
        L = orig(self)
        if not STATE["on"] or not L.get("ok") or L.get("_asbuilt"): return L
        u1, u2, u3 = [np.asarray(x, float) for x in self.u]; uK = np.asarray(self.uK, float); sp = float(np.sign(self.psiA)) or 1.0
        ts = np.asarray(L["ts"], float); k = np.abs(np.asarray(L["dK"], float))
        e = np.where(ts > 0, np.radians(efun_deg(np.degrees(k))), 0.0); k2 = np.maximum(k + e, 0.0)
        RK = rotms(uK, sp * k2); R2 = rotms(u2, np.asarray(L["q2t"], float))
        th2 = np.degrees(np.arccos(np.clip(np.einsum("nij,nj->ni", RK, np.einsum("nij,j->ni", R2, u3)) @ u1, -1, 1)))
        STATE["info"] = dict(off_deg=OFF, case=CASE, e_deg_min=round(float(np.degrees(e[ts > 0]).min()), 4), e_deg_max=round(float(np.degrees(e[ts > 0]).max()), 4),
                             th_monotone=bool(np.all(np.diff(th2) > 0)), dK_max_nominal=round(float(np.degrees(k.max())), 3), dK_max_asbuilt=round(float(np.degrees(k2.max())), 3))
        L["dK"] = sp * k2; L["th"] = th2; L["_asbuilt"] = True
        return L
    cls.law = law


ex0 = H.extra_checks


def ex_flag(M, Mfit, B):
    o = ex0(M, Mfit, B)
    if not STATE["patched"]:
        patch_law(type(Mfit.D)); STATE["patched"] = True; STATE["on"] = True     # after the fit bench: the worn model's law is as-built
    o["klaw"] = dict(STATE["info"] or {}, on=STATE["on"])
    return o


H.extra_checks = ex_flag

if __name__ == "__main__":
    wb, outp = sys.argv[1], sys.argv[2]
    EP.claim("fit60", wb, "BEST", outp)
    d = json.load(open(outp)); d["klaw"] = dict(STATE["info"] or {}, off=OFF, case=CASE); json.dump(d, open(outp, "w"), indent=1, default=float)
    print("klaw", json.dumps(d["klaw"]))
