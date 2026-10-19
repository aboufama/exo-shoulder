"""Independent verifier (skeptic) for offset-shortcar-relay-4r (claim: frozen exact Bench(110,360) chain-only buildable
gate 14.76 / plain 13.74 at PHI 35, ds 31, delta 4.5, carw 14, pre 0, arm-fixed CF coil, flange 1).

The claim model is imported UNCHANGED (docs/concepts/models/offset-shortcar-relay-4r.py, which itself patches the
proxtrack model through the buildability verifier's stackfix). On the same prepared wear this verifier adds the checks
the model leaves out, then re-scores:

  X1  every chain part (all rigid and link sets AND the contact-only top / crown sets, bumped as the model bumps them)
      against every relay body: shell sector, carriage sector, arm-fixed coil cylinder, bracket. The model checks the
      shell against 6 parts, the carriage against 4, the bracket against E and boss only, the coil against 6.
  X2  the bracket as a 2 mm plate: its TOP layer (underside + 2 mm radially out about a_r) is sampled too (the model
      samples the underside only, so a part passing over the bracket is read 2 mm too far away).
  rule: non-adjacent < 1 mm -> pose lost (unless its metal is in the skin: then it stays a contact, as the model does);
      the knee link vs the bracket / carriage (one body with the pad, which the knee link pins to through pin b) is read
      with the adjacent 0.15 mm running gap; the pad itself is the bracket's own body and is skipped.
  tab (diagnostic) the coil mounted on a shell tab: the shell continued at R_t from the zero end to the coil's far edge
      (the most conservative mount; a cheek mount from the shell end face to the coil axle stays above the coil
      underside except within ~2 deg of the end).

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/offset-shortcar-relay-4r-verify.py claim out.json
    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/offset-shortcar-relay-4r-verify.py tab out.json
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
_sp = importlib.util.spec_from_file_location("offset_shortcar_for_verify", os.path.join(REPO, "docs", "concepts", "models", "offset-shortcar-relay-4r.py"))
OM = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(OM)
PT, AA, CB = OM.PT, OM.AA, OM.CB
D2R = math.pi / 180
PICK = dict(carw=14.0, pre=0.0, ds=31.0, delta=4.5, coil="arm", flange=1, lean=0)
BASE = dict(OM.CLAIM_PARENT, **PICK)


def _sector(Xw, RS, Qf, G, ax, r0, r1, sa, sb, ta, tb):
    h = (Xw @ RS) @ Qf; sv = h @ ax; rr = np.linalg.norm(AA._rad(h, ax), axis=1)
    az = np.degrees(np.arctan2(h @ G["f"], h @ G["e"])); mid = 0.5 * (ta + tb); azr = (az - mid + 180.0) % 360.0 - 180.0 + mid
    dr = np.maximum(0.0, np.maximum(rr - r1, r0 - rr)); dss = np.maximum(0.0, np.maximum(sa - sv, sv - sb))
    da = np.maximum(0.0, np.maximum(ta - azr, azr - tb)) * D2R * np.minimum(rr, r1)
    return float(np.sqrt(dr ** 2 + dss ** 2 + da ** 2).min())


def xcheck(S, hw, o):
    """X1 + X2 on the wear just recorded (B.res / M.why as the model left them); returns the extra jams and the re-score"""
    from scipy.spatial import cKDTree
    M, B, ax = S["M"], S["B"], S["ax"]
    rp = dict(S["rp"]); rp.update({k: hw[k] for k in hw if k in PT.DEF})
    G = PT.geometry(S["M1"], S["B1"], ax, rp); bumps = PT.bump_amounts(S["M1"], G, ax)
    arm, car = PT.relay_points(G, ax)
    br = car[G["car_tag"] == "bracket"]; rad = AA._rad(br, ax); rad /= np.maximum(np.linalg.norm(rad, axis=1, keepdims=True), 1e-9)
    br2 = np.r_[br, br + 2.0 * rad]                          # X2: bracket underside + top
    HG0 = AA.Z0["HG"][B.idx].astype(float)
    names = list(M.rigid) + list(M.link_pts); kinds = ["rigid"] * len(M.rigid) + ["link"] * len(M.link_pts)
    parts = list(M.rigid.values()) + list(M.link_pts.values())
    sets = [((kd, nm), nm, m, X) for nm, kd, (m, X) in zip(names, kinds, parts)]
    sets += [(("contact", k), f"c{k}:m{m}", m, Pc) for k, (m, Pc) in enumerate(M.contact) if len(Pc)]
    pad_m = M.rigid["pad"][0] if "pad" in M.rigid else None; knee_m = M.rigid["knee"][0] if "knee" in M.rigid else None
    nC = sum(len(X) for _, _, (m, X) in zip(names, kinds, parts))
    Rt = G["R_t"]; hcar = 0.5 * PT.CAR_W / Rt / D2R; rows = []; worst = {}; pmin = {}
    for i in range(len(B.idx)):
        if B.res[i] is None: continue
        mn = float(np.min(B.res[i])); RS, Qp, Q0 = M.RS[i], M.Q[i], HG0[i]
        wbr = (br2 @ Qp.T) @ RS.T; tb_ = cKDTree(wbr); per = {}
        for key, nm, m, X in sets:
            w = M.world(m, i, X); a = bumps.get(key)
            if a is not None and np.any(a > 0):
                h = (w @ RS) @ Qp; r = AA._rad(h, ax); n = np.linalg.norm(r, axis=1, keepdims=True); n[n < 1e-9] = 1.0
                w = ((h + a[:, None] * r / n) @ Qp.T) @ RS.T
            if m == pad_m: continue                          # the pad is the bracket / carriage body
            d_sh = _sector(w, RS, Q0, G, ax, Rt - 1.5, Rt, G["s0"] - 0.5 * PT.SH_W, G["s0"] + 0.5 * PT.SH_W, G["lo"], G["hi"])
            d_ca = _sector(w, RS, Qp, G, ax, Rt + 0.2, Rt + G["h_c"], G["s0"] - 0.5 * PT.CAR_L, G["s0"] + 0.5 * PT.CAR_L, G["th0"] - hcar, G["th0"] + hcar)
            d_br = float(tb_.query(w)[0].min()) - 1.0
            d_co = OM._coil_d(w, RS, Q0 if G["coil_frame"] == "arm" else Qp, G, ax) if G.get("coil_frame") else 1e9
            adj = (m == knee_m)
            per[nm] = dict(shell=d_sh, car=d_ca, bracket=d_br, coil=d_co, adj=adj)
            for hwn, dv in (("shell", d_sh), ("car", d_ca), ("bracket", d_br), ("coil", d_co)):
                kk = f"{nm}|{hwn}"
                if dv < worst.get(kk, (1e9,))[0]: worst[kk] = (round(dv, 3), i)
        cl_na = [(dd[hwn], nm, hwn) for nm, dd in per.items() for hwn in ("shell", "car", "bracket", "coil") if not (dd["adj"] and hwn in ("car", "bracket"))]
        cl_ad = [(dd[hwn], nm, hwn) for nm, dd in per.items() for hwn in ("car", "bracket") if dd["adj"]]
        if cl_na:
            c0 = min(cl_na); pmin[i] = dict(mm=round(c0[0], 3), part=c0[1], hw=c0[2], metal=round(mn, 2), adj_mm=round(min(cl_ad)[0], 3) if cl_ad else None)
        jam = []
        for nm, dd in per.items():
            for hwn in ("shell", "car", "bracket", "coil"):
                lim = 0.15 if (dd["adj"] and hwn in ("car", "bracket")) else 1.0
                if dd[hwn] < lim: jam.append((nm, hwn, round(dd[hwn], 3)))
        if jam: rows.append(dict(i=i, kind=B.kind[i], pose=[B.poses[i][k] for k in ("plane", "elev", "axial")], metal_min=round(mn, 2),
                                 why=str(M.why[i]), jam=sorted(jam, key=lambda x: x[2])[:6]))
    # re-score: a NEW jam on a taken pose (metal >= 0) -> pose lost; a jam on a contact pose stays a contact
    lost = [r["i"] for r in rows if r["metal_min"] >= 0]
    res_keep = {j: B.res[j] for j in lost}
    for j in lost: B.res[j] = None
    rr_ = B.report(); rep = {k: rr_[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    ch = [B.res[j][:nC] for j in range(len(B.idx)) if B.kind[j] == "clip" and B.res[j] is not None and float(np.min(B.res[j])) >= 0]
    lc = np.concatenate(ch) if ch else np.zeros(0); ibc = round(float(((lc >= 2) & (lc <= 14)).mean()), 4) if len(lc) else 0.0
    gate = CB.gap_of(min(rep["inband14"], ibc), rep["follow"], rep["reach"], rep["contact"])
    ws = np.array(B.kind) == "ws"; tk = np.array([B.res[j] is not None and float(np.min(B.res[j])) >= 0 for j in range(len(B.idx))])
    elev = np.array([p["elev"] for p in B.poses])
    tkd = [j for j, v in pmin.items() if v["metal"] >= 0]
    margin = {f"lt{t:g}": int(sum(1 for j in tkd if pmin[j]["mm"] < t)) for t in (1.0, 1.1, 1.2, 1.5, 2.0)}
    margin.update({f"ws_lt{t:g}": int(sum(1 for j in tkd if pmin[j]["mm"] < t and B.kind[j] == "ws")) for t in (1.0, 1.1, 1.2, 1.5, 2.0)})
    margin["lowest"] = [dict(i=j, kind=B.kind[j], **pmin[j]) for j in sorted(tkd, key=lambda j: pmin[j]["mm"])[:15]]
    out = dict(nC=nC, clearance_margin_taken=margin, extra_jam_rows=rows, n_extra_jam=len(rows), lost_new=len(lost), lost_new_ws=int(sum(ws[j] for j in lost)),
               rescored=dict(wear=rep, ib14_chain_only=ibc, gate_gap=round(gate, 2), ws_taken=int((ws & tk).sum()),
                             overhead=[int((ws & tk & (elev >= 140)).sum()), int((ws & (elev >= 140)).sum())]),
               closest={k: v for k, v in sorted(worst.items(), key=lambda kv: kv[1][0])[:40]},
               bracket=dict(n_under=int(len(br)), ramp_deg=G.get("bracket_ramp_deg"), turn_mm=G.get("bracket_turn_mm")))
    for j, v in res_keep.items(): B.res[j] = v
    return out


def tab_geometry(orig):
    def geo(M1, B1, ax, rp):
        G = orig(M1, B1, ax, rp)
        if G.get("coil_frame") == "arm":
            ext = math.degrees((G["coilD"] + 1.0) / G["R_t"])
            if G["sg"] > 0: G["lo_shell0"] = G["lo"]; G["lo"] = G["lo"] - ext
            else: G["hi_shell0"] = G["hi"]; G["hi"] = G["hi"] + ext
            G["tab_deg"] = round(ext, 2)
        return G
    return geo


def run(mode, outp, nc=110, nw=360):
    t0 = time.time(); S = OM.prepare(BASE, nc, nw, exact=os.environ.get("CB_EXACT") == "1"); res = dict(prepare_secs=round(time.time() - t0, 1), ideal=S["ideal"], params=BASE)
    print(json.dumps(dict(prepared=True, ideal=S["ideal"], secs=res["prepare_secs"])), flush=True)
    variants = [("tab", PICK)] if mode == "tab" else [("pick", PICK)]
    if mode == "tab": PT.geometry = tab_geometry(OM.geometry)
    for tag, hw in variants:
        o = OM.wear(S, dict(BASE, **hw)); sm = OM.summary(o)
        print(json.dumps(dict(tag=tag, **sm), default=float), flush=True)
        x = xcheck(S, dict(BASE, **hw), o)
        print(json.dumps(dict(tag=tag, n_extra_jam=x["n_extra_jam"], lost_new=x["lost_new"], rescored=x["rescored"]), default=float), flush=True)
        res[tag] = dict(summary=sm, contacts=o["contacts"], th_margin=None, xcheck=x, why=o["why"], relayed=o["relayed"],
                        continuity={k: v for k, v in (o["continuity"] or {}).items() if k != "dropped"})
        try:
            res[tag]["th_margin"] = OM.BV.th_margin(S["M"], S["B"])
        except Exception as ex: res[tag]["th_margin"] = dict(err=repr(ex)[:200])
        json.dump(res, open(outp, "w"), indent=1, default=float)
        if mode in ("claim", "held"):
            pp = OM.perpose(S); pp.update(wear=("held" if nc == -1 else f"bench({nc},{nw})"), params=dict(BASE, **hw), exact=True, verifier=True)
            json.dump(pp, open(outp.replace(".json", "_perpose.json"), "w"), default=float)
    print("done", round(time.time() - t0, 1), flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "held": os.environ["CB_EXACT"] = "1"; run("held", sys.argv[2], -1, -1)
    elif len(sys.argv) > 4: run(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    else: os.environ["CB_EXACT"] = "1"; run(sys.argv[1], sys.argv[2])
