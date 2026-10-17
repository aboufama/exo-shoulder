"""pressure-angle map of a longstroke-slipper-knuckle-3r drive per 0.25 deg of K (fit on Bench(60,160) fast):
rssr: the rod's angle to the crank-tip velocity and to the horn-ball velocity (3D, both ends), the rod's elevation over the
horn's plane, the crank angle phi; cam drives: the parents' own table (pa_crank, pa_horn, contact radius, flank radius).
    LS_DRIVE=rssr python3 docs/research/longstroke_drive/pa_map.py '<params json>' [out.json]"""
import importlib.util, json, math, os, sys
import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB  # noqa: E402

sp_ = importlib.util.spec_from_file_location("ls_model", os.path.join(REPO, "docs", "concepts", "models", "longstroke-slipper-knuckle-3r.py"))
LS = importlib.util.module_from_spec(sp_); sp_.loader.exec_module(LS)
S = LS.S; unit = S.unit


def ang(a, b): return math.degrees(math.acos(max(-1.0, min(1.0, abs(float(a @ b)) / max(float(np.linalg.norm(a) * np.linalg.norm(b)), 1e-12)))))


def pa_map(par):
    B = CB.Bench(n_clip=60, n_ws=160); r, M = LS._report(B, par); g = M._scg; info = M._sc_info
    out = dict(drive=LS.DRIVE, dK_lim=info.get("dK_lim"), why_lim=info.get("why_lim"), gap=r.get("gap"), plain=(r.get("plain") or {}).get("gap"),
               reach=r.get("reach"), dK_taken_max=(r.get("drive") or {}).get("dK_taken_max"), rows=[])
    if LS.DRIVE == "rssr":
        PV, dR, tip0, H0, uK, spn = g["PV"], g["dR"], g["tip0"], g["H0"], g["uK"], g["sp"]
        for kk, ph in zip(g["kgrid"], g["phig"]):
            tp = S.rotm(dR, ph)[0] @ (tip0 - PV) + PV; H = S.rotm(uK, spn * kk)[0].T @ H0; rod = unit(H - tp)
            vt = np.cross(dR, tp - PV); vh = np.cross(uK, H)
            elev = 90.0 - ang(rod, uK)                       # rod vs the horn's plane (perpendicular to uK)
            out["rows"].append(dict(dK=round(math.degrees(kk), 2), phi=round(math.degrees(ph), 2), pa_tip=round(ang(rod, vt), 2),
                                    pa_horn=round(ang(rod, vh), 2), rod_elev_horn=round(elev, 2), rod_elev_crank=round(90.0 - ang(rod, dR), 2)))
        # C4 pricing: the same crank / horn seats with the rod made a SPHERICAL coupler (an arc on two radial pins, all four
        # axes through GH): closure = constant angle between the pin directions; the force acts along the coupler's great
        # circle, i.e. in each pin's tangent plane, so the chord's elevation penalty disappears
        t0, h0 = unit(tip0), unit(H0); ca = float(t0 @ h0); prev = 0.0; sph = []
        pg = np.radians(np.arange(-120.0, 120.0 + 1e-6, 0.05)); TG = np.einsum("nij,j->ni", S.rotm(dR, pg), t0)
        for kk in np.radians(np.arange(0.0, 100.0 + 1e-6, 0.25)):
            h = S.rotm(uK, spn * kk)[0].T @ h0; f = TG @ h - ca; sg = np.nonzero(np.diff(np.sign(f)) != 0)[0]
            if not len(sg): break
            rts = pg[sg] - f[sg] * (pg[sg + 1] - pg[sg]) / (f[sg + 1] - f[sg]); ph = float(rts[np.argmin(np.abs(rts - prev))]); prev = ph
            t = S.rotm(dR, ph)[0] @ t0
            tH = unit(t - (t @ h) * h); tT = unit(h - (h @ t) * t)
            sph.append(dict(dK=round(math.degrees(kk), 2), phi=round(math.degrees(ph), 2), pa_tip=round(ang(tT, np.cross(dR, t)), 2), pa_horn=round(ang(tH, np.cross(uK, h)), 2)))
        lim = next((r_["dK"] for r_ in sph if max(r_["pa_tip"], r_["pa_horn"]) > LS.PA_GATE), sph[-1]["dK"] if sph else 0.0)
        out["sph4r"] = dict(dK_lim_pa42=lim, coupler_arc_deg=round(math.degrees(math.acos(max(-1, min(1, ca)))), 2), rows=sph[::8])
    else:
        T = M._cam_table
        for j in range(len(T["k"])):
            out["rows"].append(dict(dK=round(float(T["k"][j]), 2), phi=round(float(T["phi"][j]), 2), pa_crank=round(float(T["pa_crank"][j]), 2),
                                    pa_horn=round(float(T["pa_horn"][j]), 2), contact_r=round(float(T["contact_r"][j]), 2),
                                    flank_rho=round(float(T["flank_rho"][j]), 2), clear_hubK=round(float(T["clear_hubK"][j]), 2)))
    return out


if __name__ == "__main__":
    par = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    o = pa_map(par)
    if len(sys.argv) > 2: json.dump(o, open(sys.argv[2], "w"), indent=1)
    rows = o.pop("rows"); sp4 = o.pop("sph4r", None); print(json.dumps(o))
    if sp4: print("sph4r", json.dumps({k: v for k, v in sp4.items() if k != "rows"})); [print("  ", json.dumps(r_)) for r_ in sp4["rows"]]
    for rw in rows[:: max(1, len(rows) // 25)]: print(json.dumps(rw))
