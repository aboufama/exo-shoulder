"""Independent verifier (skeptic) for phi40-thinstack-relay-4r (claim: frozen exact Bench(110,360) chain-only buildable
gate 14.06 / plain 13.52 at PHI 40, delta 3.5, tsh 1.0, lean, band 8, bump 1.2, lug coil 12 x 10, L-lug bracket).

The claim model is imported UNCHANGED (docs/concepts/models/phi40-thinstack-relay-4r.py, which patches
offset-shortcar-relay-4r -> the proxtrack buildability verifier). On the same prepared wear this verifier adds the checks
the model leaves out, then re-scores:

  X1  every chain part (rigid + link sets AND the contact-only top / crown sets, bumped as the model bumps them) against
      every relay body: shell sector (THIN: [R_t - tsh, R_t], the parent verifier's 1.5 replaced), carriage sector, coil
      cylinder (carriage frame for the lug coil), bracket. Non-adjacent < 1 mm -> pose lost (a contact stays a contact);
      the knee link vs bracket / carriage is the adjacent 0.15 mm pair; the pad (the bracket's body) is skipped.
  X2  the bracket's TOP layer (underside + 2 mm radially out) is sampled too.
  X3  (red team, new hardware the model does not carry) the lug coil's constant-force STRIP. The drum rides on the
      carriage's posterior-proximal lug, s in [s0 + SH_W/2 + 1, + coilL], i.e. entirely PROXIMAL of the 12 mm shell, so
      the strip has no shell under it. It must run from the drum (carriage frame) to an arm-fixed anchor (the drum's
      phi-0 bottom point). Two realisations are priced:
        chord  - the strip under tension, straight from anchor to the drum's bottom point (no guide: as specified);
        guide  - a 1 mm arm-fixed guide arc under the strip (top at R_t + h_c - 0.1, s band coilL + 2, az from the
                 anchor to the drum at PHI): the strip lies on it; the guide's underside is sampled vs skin.
      Strip / guide metal < 0 in the skin -> contact; chain metal (non-adjacent) < 1 mm of it (nearest 2 mm sample - 1)
      -> pose lost.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/phi40-thinstack-relay-4r-verify.py claim out.json
    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/phi40-thinstack-relay-4r-verify.py held out.json
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
_sp = importlib.util.spec_from_file_location("phi40_for_verify", os.path.join(REPO, "docs", "concepts", "models", "phi40-thinstack-relay-4r.py"))
OM = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(OM)
OS, PT, AA, CB, BV = OM.OS, OM.PT, OM.AA, OM.CB, OM.BV
D2R = math.pi / 180
PICK = json.load(open(os.path.join(REPO, "docs", "concepts", "verify", "phi40-thinstack-relay-4r", "pick.json")))
BASE = dict(OM.CLAIM_PARENT, **OM.HW0)
OUTD = os.path.join(REPO, "docs", "concepts", "verify", "phi40-thinstack-relay-4r")


def _sector(Xw, RS, Qf, G, ax, r0, r1, sa, sb, ta, tb):
    h = (Xw @ RS) @ Qf; sv = h @ ax; rr = np.linalg.norm(AA._rad(h, ax), axis=1)
    az = np.degrees(np.arctan2(h @ G["f"], h @ G["e"])); mid = 0.5 * (ta + tb); azr = (az - mid + 180.0) % 360.0 - 180.0 + mid
    dr = np.maximum(0.0, np.maximum(rr - r1, r0 - rr)); dss = np.maximum(0.0, np.maximum(sa - sv, sv - sb))
    da = np.maximum(0.0, np.maximum(ta - azr, azr - tb)) * D2R * np.minimum(rr, r1)
    return float(np.sqrt(dr ** 2 + dss ** 2 + da ** 2).min())


def _dirv(G, t):
    return math.cos(t * D2R) * G["e"] + math.sin(t * D2R) * G["f"]


def strip_geom(G, ax):
    """local (frame) points: drum bottom line (carriage frame), anchor line (arm frame), guide arc (arm frame)"""
    s_c, az_c, r_c = G["coil_c"]; D, L = G["coilD"], G["coilL"]; rb = r_c - 0.5 * D
    ss = np.arange(s_c - 0.5 * L, s_c + 0.5 * L + 0.01, 2.0)
    d0 = _dirv(G, az_c); line = np.array([sv * ax + rb * d0 for sv in ss])
    gd = []; dt = 2.0 / rb / D2R
    for t in np.arange(az_c, az_c + G["sg"] * G["PHI"] + G["sg"] * 1e-9, G["sg"] * dt):
        d = _dirv(G, t)
        for sv in np.arange(s_c - 0.5 * L - 1.0, s_c + 0.5 * L + 1.01, 2.0):
            gd.append(sv * ax + (rb - 1.1) * d)
    return line, np.array(gd), rb


def xcheck(S, hw, o):
    from scipy.spatial import cKDTree
    M, B, ax = S["M"], S["B"], S["ax"]
    rp = dict(S["rp"]); rp.update({k: hw[k] for k in hw if k in PT.DEF})
    G = PT.geometry(S["M1"], S["B1"], ax, rp); bumps = PT.bump_amounts(S["M1"], G, ax)
    arm, car = PT.relay_points(G, ax); tsh = float(G.get("tsh", 1.5))
    br = car[G["car_tag"] == "bracket"]; rad = AA._rad(br, ax); rad /= np.maximum(np.linalg.norm(rad, axis=1, keepdims=True), 1e-9)
    br2 = np.r_[br, br + 2.0 * rad]
    HG0 = AA.Z0["HG"][B.idx].astype(float)
    names = list(M.rigid) + list(M.link_pts); kinds = ["rigid"] * len(M.rigid) + ["link"] * len(M.link_pts)
    parts = list(M.rigid.values()) + list(M.link_pts.values())
    sets = [((kd, nm), nm, m, X) for nm, kd, (m, X) in zip(names, kinds, parts)]
    sets += [(("contact", k), f"c{k}:m{m}", m, Pc) for k, (m, Pc) in enumerate(M.contact) if len(Pc)]
    pad_m = M.rigid["pad"][0] if "pad" in M.rigid else None; knee_m = M.rigid["knee"][0] if "knee" in M.rigid else None
    nC = sum(len(X) for _, _, (m, X) in zip(names, kinds, parts))
    Rt = G["R_t"]; hcar = 0.5 * PT.CAR_W / Rt / D2R; rows = []; worst = {}; pmin = {}
    line, guide, rb = strip_geom(G, ax) if G.get("coil_frame") == "car" else (None, None, None)
    X3 = {}
    for i in range(len(B.idx)):
        if B.res[i] is None: continue
        mn = float(np.min(B.res[i])); RS, Qp, Q0 = M.RS[i], M.Q[i], HG0[i]
        wbr = (br2 @ Qp.T) @ RS.T; tb_ = cKDTree(wbr); per = {}; wall = []
        for key, nm, m, X in sets:
            w = M.world(m, i, X); a = bumps.get(key)
            if a is not None and np.any(a > 0):
                h = (w @ RS) @ Qp; r = AA._rad(h, ax); n = np.linalg.norm(r, axis=1, keepdims=True); n[n < 1e-9] = 1.0
                w = ((h + a[:, None] * r / n) @ Qp.T) @ RS.T
            if m == pad_m: continue
            wall.append(w)
            d_sh = _sector(w, RS, Q0, G, ax, Rt - tsh, Rt, G["s0"] - 0.5 * PT.SH_W, G["s0"] + 0.5 * PT.SH_W, G["lo"], G["hi"])
            d_ca = _sector(w, RS, Qp, G, ax, Rt + 0.2, Rt + G["h_c"], G["s0"] - 0.5 * PT.CAR_L, G["s0"] + 0.5 * PT.CAR_L, G["th0"] - hcar, G["th0"] + hcar)
            d_br = float(tb_.query(w)[0].min()) - 1.0
            d_co = OS._coil_d(w, RS, Q0 if G["coil_frame"] == "arm" else Qp, G, ax) if G.get("coil_frame") else 1e9
            adj = (m == knee_m)
            per[nm] = dict(shell=d_sh, car=d_ca, bracket=d_br, coil=d_co, adj=adj)
            for hwn, dv in (("shell", d_sh), ("car", d_ca), ("bracket", d_br), ("coil", d_co)):
                kk = f"{nm}|{hwn}"
                if dv < worst.get(kk, (1e9,))[0]: worst[kk] = (round(dv, 3), i)
        cl_na = [(dd[hwn], nm, hwn) for nm, dd in per.items() for hwn in ("shell", "car", "bracket", "coil") if not (dd["adj"] and hwn in ("car", "bracket"))]
        if cl_na:
            c0 = min(cl_na); pmin[i] = dict(mm=round(c0[0], 3), part=c0[1], hw=c0[2], metal=round(mn, 2))
        jam = []
        for nm, dd in per.items():
            for hwn in ("shell", "car", "bracket", "coil"):
                lim = 0.15 if (dd["adj"] and hwn in ("car", "bracket")) else 1.0
                if dd[hwn] < lim: jam.append((nm, hwn, round(dd[hwn], 3)))
        if jam: rows.append(dict(i=i, kind=B.kind[i], pose=[B.poses[i][k] for k in ("plane", "elev", "axial")], metal_min=round(mn, 2),
                                 why=str(M.why[i]), jam=sorted(jam, key=lambda x: x[2])[:6]))
        # X3: the CF strip (chord and guided) - skin distance and chain clearance
        if line is not None:
            T = (line @ Qp.T) @ RS.T; A = (line @ Q0.T) @ RS.T; Ln = float(np.linalg.norm(T[0] - A[0]))
            nu = max(2, int(math.ceil(Ln / 2.0)) + 1); u = np.linspace(0.0, 1.0, nu)
            chord = (A[None, :, :] + u[:, None, None] * (T - A)[None, :, :]).reshape(-1, 3)
            # guided: the strip on the guide top from the anchor to the drum (arm frame arc up to the drum's current az)
            hT = (T[0] @ RS) @ Q0; azT = math.degrees(math.atan2(float(hT @ G["f"]), float(hT @ G["e"])))
            s_c, az_c, _ = G["coil_c"]; dphi = ((azT - az_c + 180.0) % 360.0) - 180.0
            ts = np.linspace(az_c, az_c + dphi, max(2, int(abs(dphi) * D2R * rb / 2.0) + 1))
            sarc = np.array([sv * ax + (rb - 0.05) * _dirv(G, t) for t in ts for sv in line @ ax])
            garc = (sarc @ Q0.T) @ RS.T; gpl = (guide @ Q0.T) @ RS.T
            dch = B.dist(i, chord); dgp = B.dist(i, np.r_[gpl, garc])
            wc_ = np.concatenate(wall); tc_ = cKDTree(chord); tg_ = cKDTree(np.r_[gpl, garc])
            cch = float(tc_.query(wc_)[0].min()) - 1.0; cgu = float(tg_.query(wc_)[0].min()) - 1.0
            # chord sag below the drum-bottom radius (local, arm frame)
            hc = (chord @ RS) @ Q0; rch = np.linalg.norm(AA._rad(hc, ax), axis=1)
            X3[i] = dict(phi=round(dphi, 2), chord_skin=round(float(dch.min()), 3), chord_chain=round(cch, 3), chord_rmin=round(float(rch.min()), 2),
                         guide_skin=round(float(dgp.min()), 3), guide_chain=round(cgu, 3), metal=round(mn, 2))
    lost = [r["i"] for r in rows if r["metal_min"] >= 0]
    res_keep = {j: B.res[j] for j in range(len(B.idx))}
    for j in lost: B.res[j] = None

    def score(tag):
        rr_ = B.report(); rep = {k: rr_[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
        ch = [B.res[j][:nC] for j in range(len(B.idx)) if B.kind[j] == "clip" and B.res[j] is not None and float(np.min(B.res[j])) >= 0]
        lc = np.concatenate(ch) if ch else np.zeros(0); ibc = round(float(((lc >= 2) & (lc <= 14)).mean()), 4) if len(lc) else 0.0
        gate = CB.gap_of(min(rep["inband14"], ibc), rep["follow"], rep["reach"], rep["contact"])
        ws = np.array(B.kind) == "ws"; tk = np.array([B.res[j] is not None and float(np.min(B.res[j])) >= 0 for j in range(len(B.idx))])
        ncon = int(sum(1 for j in range(len(B.idx)) if B.res[j] is not None and float(np.min(B.res[j])) < 0))
        elev = np.array([p["elev"] for p in B.poses])
        return dict(tag=tag, wear=rep, ib14_chain_only=ibc, gate_gap=round(gate, 2), ws_taken=int((ws & tk).sum()), n_contact=ncon,
                    overhead=[int((ws & tk & (elev >= 140)).sum()), int((ws & (elev >= 140)).sum())])
    sc = dict(x12=score("X1+X2"))
    # X3 re-scores on top of X1 + X2
    for kind in ("chord", "guide"):
        base_res = {j: B.res[j] for j in range(len(B.idx))}; nl = nc_ = 0
        for j, v in X3.items():
            if B.res[j] is None: continue
            sk, cl = v[f"{kind}_skin"], v[f"{kind}_chain"]
            if sk < 0: B.res[j] = np.r_[B.res[j], sk]; nc_ += 1
            elif cl < 1.0 and float(np.min(B.res[j])) >= 0: B.res[j] = None; nl += 1
        sc[kind] = dict(score(f"X1+X2+X3 {kind}"), new_contacts=nc_, new_lost=nl)
        for j, v in base_res.items(): B.res[j] = v
    tkd = [j for j, v in pmin.items() if v["metal"] >= 0]
    margin = {f"lt{t:g}": int(sum(1 for j in tkd if pmin[j]["mm"] < t)) for t in (1.0, 1.1, 1.2, 1.5, 2.0)}
    margin["lowest"] = [dict(i=j, kind=B.kind[j], **pmin[j]) for j in sorted(tkd, key=lambda j: pmin[j]["mm"])[:15]]
    x3s = None
    if X3:
        tk3 = {j: v for j, v in X3.items() if v["metal"] >= 0}
        x3s = dict(n=len(X3), chord_skin_lt0=sum(1 for v in tk3.values() if v["chord_skin"] < 0), chord_skin_lt2=sum(1 for v in tk3.values() if v["chord_skin"] < 2),
                   chord_chain_lt1=sum(1 for v in tk3.values() if v["chord_chain"] < 1), guide_skin_lt0=sum(1 for v in tk3.values() if v["guide_skin"] < 0),
                   guide_chain_lt1=sum(1 for v in tk3.values() if v["guide_chain"] < 1),
                   chord_rmin=min(v["chord_rmin"] for v in X3.values()), rb=round(rb, 2), R_liner=round(G["R_liner"], 2),
                   worst_chord=sorted(([j, v] for j, v in tk3.items()), key=lambda kv: kv[1]["chord_skin"])[:10],
                   worst_guide=sorted(([j, v] for j, v in tk3.items()), key=lambda kv: kv[1]["guide_skin"])[:10],
                   worst_chord_chain=sorted(([j, v] for j, v in tk3.items()), key=lambda kv: kv[1]["chord_chain"])[:5],
                   worst_guide_chain=sorted(([j, v] for j, v in tk3.items()), key=lambda kv: kv[1]["guide_chain"])[:5])
    out = dict(nC=nC, tsh=tsh, R_t=round(Rt, 2), clearance_margin_taken=margin, extra_jam_rows=rows, n_extra_jam=len(rows), lost_new=len(lost),
               rescored=sc, closest={k: v for k, v in sorted(worst.items(), key=lambda kv: kv[1][0])[:40]}, X3=x3s,
               X3_all={str(j): v for j, v in X3.items()})
    for j, v in res_keep.items(): B.res[j] = v
    return out


def run(mode, outp, nc=110, nw=360, post=()):
    t0 = time.time(); S = OM.prepare(BASE, nc, nw, exact=True); res = dict(prepare_secs=round(time.time() - t0, 1), ideal=S["ideal"], params=BASE, pick=PICK)
    print(json.dumps(dict(prepared=True, ideal=S["ideal"], secs=res["prepare_secs"])), flush=True)
    for tag, hw in [("pick", PICK)] + [(f"post{k}", dict(PICK, **h)) for k, h in enumerate(post)]:
        o = OM.wear(S, dict(BASE, **hw)); sm = OM.summary(o)
        print(json.dumps(dict(tag=tag, **sm), default=float), flush=True)
        try: thm = BV.th_margin(S["M"], S["B"])
        except Exception as ex: thm = dict(err=repr(ex)[:200])
        if tag == "pick":
            pp = OM.perpose(S); pp.update(wear=("held" if nc == -1 else f"bench({nc},{nw})"), params=dict(BASE, **hw), exact=True, verifier=True)
            json.dump(pp, open(outp.replace(".json", "_perpose.json"), "w"), default=float)
        x = xcheck(S, dict(BASE, **hw), o)
        print(json.dumps(dict(tag=tag, n_extra_jam=x["n_extra_jam"], lost_new=x["lost_new"], rescored=x["rescored"], X3={k: v for k, v in (x["X3"] or {}).items() if not k.startswith("worst")}), default=float), flush=True)
        res[tag] = dict(hw=hw, summary=sm, contacts=o["contacts"], th_margin=thm, xcheck=x, why=o["why"],
                        continuity={k: v for k, v in (o["continuity"] or {}).items() if k != "dropped"})
        json.dump(res, open(outp, "w"), indent=1, default=float)
    print("done", round(time.time() - t0, 1), flush=True)


if __name__ == "__main__":
    os.environ["CB_EXACT"] = "1"
    if sys.argv[1] == "held": run("held", sys.argv[2], -1, -1)
    elif sys.argv[1] == "claim": run("claim", sys.argv[2], 110, 360, post=[dict(delta=3.0)])
    else: print("modes: claim | held")
