"""Skeptic probe (desmo-slipper-knuckle-3r audit 2026-10-17, read-only): stage-1 pressure angles over the BLENDED onset groove the model builds (Kb(x)),
instead of the linear law on kgrid the model's gate reads. The model file is unchanged: _desmo_build is re-executed in
memory with one read-only block inserted after the line that builds Cq. Fast Bench(60,160).

    OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_skeptic_blend_pa.py <params.json> <out.json>
(params = the row best_params with the verified a_s 9.5 / psi 150)"""
import importlib.util, inspect, json, math, os, sys, textwrap
import numpy as np
REPO = "/home/user/exo-shoulder"
spec = importlib.util.spec_from_file_location("desmo_m", os.path.join(REPO, "docs/concepts/models/desmo-slipper-knuckle-3r.py"))
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
src = textwrap.dedent(inspect.getsource(M.DSModel._desmo_build))
anchor = 'G2 = np.einsum("nij,nj->ni", S.rotm(u2, -(qs - q_on)), Cq)'
assert anchor in src
extra = '''
        _s = np.gradient(Kb, x)
        _dphb = sig * RF.dphi_of(Kb, gg, cc)
        _vFb = (_s * _dphb)[:, None] * np.cross(np.tile(dR, (len(x), 1)), Cq)
        _vcb = s_th * np.cross(np.tile(u2, (len(x), 1)), Cq)
        _vr = _vFb - _vcb
        _n = unit(np.cross(_vr, np.tile(u2, (len(x), 1))))
        _paF = _fold(_angv(_n, _vFb)); _paC = _fold(_angv(_n, _vcb))
        self._blend_probe = dict(x_deg=np.degrees(x).tolist(), Kb_deg=np.degrees(Kb).tolist(), s=_s.tolist(), paF=_paF.tolist(), paC=_paC.tolist(),
                                 PAC=PAC, hb_deg=float(np.degrees(hb)) if bw > 0 else 0.0, s_th=s_th)
'''
src = src.replace(anchor, anchor + "\n" + textwrap.indent(textwrap.dedent(extra), "    "))
ns = dict(vars(M)); exec(src, ns); M.DSModel._desmo_build = ns["_desmo_build"]
par = json.loads(open(sys.argv[1]).read())
B = M.CB.Bench(n_clip=60, n_ws=160)
r, Mod = M._report(B, par)
bp = Mod._blend_probe; x = np.array(bp["x_deg"]); Kb = np.array(bp["Kb_deg"]); paF = np.array(bp["paF"]); paC = np.array(bp["paC"]); s = np.array(bp["s"])
mv = (Kb > 1e-6) & (Kb <= 46.0)
blend = mv & (x <= bp["hb_deg"] + 1e-6)
rise = mv & (x > bp["hb_deg"] + 1e-6)
out = dict(params={k: par.get(k) for k in ("a_s", "psi", "blend", "mu")}, PAC=round(bp["PAC"], 3), hb_K_deg=round(bp["hb_deg"], 3), s_th=round(bp["s_th"], 4),
           dK_lim=r.get("cam", {}).get("dK_lim"), why=r.get("cam", {}).get("why_lim"),
           linear_law=dict(pa_cap_max=r["cam"]["desmo"]["stage1"]["pa_cap_max"], pa_pin_max=r["cam"]["desmo"]["stage1"]["pa_pin_max"]),
           blend_region=dict(n=int(blend.sum()), K_range=[round(float(Kb[blend].min()), 3), round(float(Kb[blend].max()), 3)] if blend.any() else None,
                             paC_max=round(float(paC[blend].max()), 2), paC_min=round(float(paC[blend].min()), 2),
                             paF_max=round(float(paF[blend].max()), 2), paF_min=round(float(paF[blend].min()), 2),
                             K_where_paC_over_gate=[round(float(k), 3) for k in Kb[blend & (paC > bp["PAC"])]][:60],
                             K_where_paF_over_gate=[round(float(k), 3) for k in Kb[blend & (paF > bp["PAC"])]][:60]),
           rise_region=dict(n=int(rise.sum()), paC_max=round(float(paC[rise].max()), 2) if rise.any() else None, paF_max=round(float(paF[rise].max()), 2) if rise.any() else None),
           table=[dict(x=round(float(a), 2), Kb=round(float(b), 3), s=round(float(c), 3), paF=round(float(d), 2), paC=round(float(e), 2))
                  for a, b, c, d, e in zip(x, Kb, s, paF, paC) if -bp["hb_deg"] - 1 <= a <= bp["hb_deg"] + 3])
json.dump(out, open(sys.argv[2], "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "table"}))
