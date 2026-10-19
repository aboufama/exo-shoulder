"""the K law table and the stroke -> reach curve (kinematics only: law + K + knee + slide tolerance, no metal), from the
fitted design's own IK on every workspace pose of Bench(110,360) and of the 952 held-out poses: per pose |dK| needed,
th, and the share of workspace poses closable with the drive's stroke capped at X deg.
    LS_DRIVE=... python3 docs/research/longstroke_drive/stroke_curve.py '<params json>' [out.json]"""
import importlib.util, json, math, os, sys
import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB  # noqa: E402

sp_ = importlib.util.spec_from_file_location("ls_model", os.path.join(REPO, "docs", "concepts", "models", "longstroke-slipper-knuckle-3r.py"))
LS = importlib.util.module_from_spec(sp_); sp_.loader.exec_module(LS)
CAPS = (40, 46.25, 50, 52, 55, 57.5, 60, 62.5, 65, 70, 75, 90)


def curve(par):
    p = LS._clamp(dict(LS.PARAMS, **par))
    B1 = CB.Bench(n_clip=60, n_ws=160); r1, M1 = LS._report(B1, p); D = M1.D
    Z = CB._poses_all(); out = dict(drive=LS.DRIVE, dK_lim=M1._sc_info.get("dK_lim"), a1=round(D.a1, 2), a2=round(D.a2, 2),
                                    bk=[p["bk1"], p["bk2"]], a1max=p["a1max"], law=dict(dK_max=round(D.law().get("dK_max", 0), 1)))
    sp2 = importlib.util.spec_from_file_location("pk_polish_v_ls_curve", os.path.join(REPO, "docs", "concepts", "verify", "skin-normal-3r-pin-knee-polish.py"))
    PVm = importlib.util.module_from_spec(sp2); sp2.loader.exec_module(PVm)
    for nm, B in (("bench", CB.Bench(n_clip=110, n_ws=360)), ("held", PVm.held_bench())):
        ws = np.array(B.kind) == "ws"; Q = Z["HG"][B.idx].astype(float)
        q, ok, X1, X2, X3, s = D.ik(Q); Kn = D.knee(s); dK = np.degrees(np.abs(np.asarray(D._dK, float)))
        kin = ok & Kn["ok"] & (np.abs(s[:, 2]) <= float(D.p["R_tol"]))
        elev = np.array([B.poses[i]["elev"] for i in range(len(B.idx))]); ov = ws & (elev >= 140)
        th = np.degrees(np.arccos(np.clip((Q @ D.u[2]) @ D.u[0], -1, 1)))
        out[nm] = dict(n_ws=int(ws.sum()), kin_law=int((kin & ws).sum()),
                       by_cap={str(c): [int((kin & ws & (dK <= c + 1e-6)).sum()), int((kin & ov & (dK <= c + 1e-6)).sum())] for c in CAPS},
                       n_ovh=int(ov.sum()), dK_hist=np.histogram(dK[kin & ws], bins=[0, 1e-6, 10, 20, 30, 40, 46.25, 50, 55, 57.5, 60, 65, 70, 80, 90])[0].tolist(),
                       th_taken_max={str(c): round(float(th[kin & ws & (dK <= c + 1e-6)].max()), 1) for c in CAPS if (kin & ws & (dK <= c + 1e-6)).any()})
        if nm == "bench":
            out["bench"]["law_table"] = [dict(pose=int(B.idx[i]), plane=B.poses[i]["plane"], elev=B.poses[i]["elev"], axial=B.poses[i]["axial"],
                                              th=round(float(th[i]), 2), dK=round(float(dK[i]), 2), kin=bool(kin[i]), closed=bool(ok[i]),
                                              knee=bool(Kn["ok"][i]), slide_mm=round(float(abs(s[i, 2])), 2)) for i in np.nonzero(ws)[0]]
            out["bench"]["R_tol"] = float(D.p["R_tol"])
    return out


if __name__ == "__main__":
    par = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    o = curve(par)
    if len(sys.argv) > 2: json.dump(o, open(sys.argv[2], "w"), indent=1, default=float)
    o["bench"].pop("law_table", None); print(json.dumps(o, default=float))
