"""the slaved K law as the hub-2 lobe cuts it (rawest material): per q2 step past the onset, K's opening, a1e, th, the
dyad margin m3e = a1e + a2 - th (>= 5 is the fold rule), the lobe pressure angle and th's rate per q2 degree, and
the IDEAL opening the parking test assumes (a1e = th - a2 + 5).
    LS_DRIVE=rssr python3 docs/research/longstroke_drive/law_table.py '<params json>' [out.json]"""
import importlib.util, json, math, os, sys
import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB  # noqa: E402

sp_ = importlib.util.spec_from_file_location("ls_model_lt", os.path.join(REPO, "docs", "concepts", "models", "longstroke-slipper-knuckle-3r.py"))
LS = importlib.util.module_from_spec(sp_); sp_.loader.exec_module(LS)
par = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
p = LS._clamp(dict(LS.PARAMS, **par)); B = CB.Bench(60, 160); r, M = LS._report(B, p); D = M.D; L = D.law()
u1, u2, uK = D.u[0], D.u[1], D.uK; sp = float(np.sign(D.psiA)) or 1.0
dK = np.radians(np.abs(np.asarray(L["dK"], float))); th = np.asarray(L["th"], float); q2 = np.degrees(np.asarray(L["q2t"], float))
a1e = np.degrees(np.arccos(np.clip(np.einsum("nij,j->ni", LS.S.rotm(uK, sp * dK), u2) @ u1, -1, 1)))
m3e = a1e + D.a2 - th; dth = np.gradient(th, q2)
rows = [dict(q2_past_onset=round(abs(float(q - q2[0])), 2), dK=round(float(np.degrees(k)), 2), a1e=round(float(a), 2), th=round(float(t), 2), m3e=round(float(m), 2),
             dth_per_dq2=round(abs(float(d)), 3), pa_lobe=round(float(pa), 2), a1e_ideal=round(float(t - D.a2 + 5.0), 2))
        for q, k, a, t, m, d, pa in zip(q2, dK, a1e, th, m3e, dth, L["pa"])]
out = dict(params=par, why_end=L.get("why_end"), dK_max=round(float(L.get("dK_max", 0)), 2), th_max=L.get("th_max"), a2=round(D.a2, 2), rows=rows[::5])
if len(sys.argv) > 2: json.dump(out, open(sys.argv[2], "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "rows"}))
for rw in out["rows"][:: max(1, len(out["rows"]) // 16)]: print(json.dumps(rw))
