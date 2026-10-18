"""underpass-bridge-relay-4r (round 107, J7 track jump): offset-shortcar-relay-4r's one-sided arm-fixed relay with the
in-band term removed - the E strap / knee / boss keep the lead's verified heights (NO rigid bump, no knee link raised over
the boss) and pass UNDER the arm-fixed Ti shell, which becomes a BRIDGE held at its ends.

  * NO BUMP: PT.bump_amounts returns {} (every chain point at its verified height).
  * BRIDGE HEIGHT (frozen at selection): R_under (shell underside about a_r) = max(skin rule p90 + 4 + rt_extra,
    max chain radius in the shell footprint + up_clr, max chain radius in the T-nut flange footprint + 3), the maxima over
    the fit-bench kin_ok poses (phi 0) and the envsel FRESH workspace poses (relayed frames). The claim / held benches wear
    the selection's R_under (rl_fix) unchanged; they never re-place the bridge.
  * SHELL: Ti 12 wide (8 net), thickness tsh (1.5 simply supported; tshc for the cantilever); carriage, T-nut flange
    (1 mm under the underside), bracket and lug coil ride the real shell top / underside.
  * SUPPORTS (sampled metal, arm-fixed, contact list AND jam sectors):
      posterior: Ti block 12 (s) x postL (arc) x postH under the shell's zero end [lo - postL/R, lo] (E never reaches it:
                 E's arm-frame azimuth starts at +6.4 deg rel pad); a soft liner pad (not metal) under it.
      ant='i':   the shell extended over E's envelope to hiE + 1 mm and a Ti block [hiE + 1 mm, hiE + 5 mm] x postH.
      ant='ii':  no anterior support: the shell cantilevers from the posterior support, stiffened by its own thickness
                 tshc (underside fixed, the top and everything on it rises); 4 N tip deflection of the curved cantilever
                 reported (P R^3 / (E I) (a/2 - sin 2a / 4)), required <= 0.5 x up_clr.
  * COIL: the CF coil on the carriage's posterior-proximal lug (coil='lug', D 12, L 10) - carriage-frame jam list.
  * Jam rule unchanged (the parent's sector rule reads points from below: dr = max(0, r - r1, r0 - r)), extended to the
    supports and the extension.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/underpass-bridge-relay-4r.py hwsweep '<base>' '<hw list>' -2 0 out.json   # envsel (selection)
    CB_EXACT=1 ... hwsweep '<base>' '<hw list with rl_fix, hiE>' 110 360 out.json                                       # claim bench (frozen)
    CB_EXACT=1 ... held '<json with rl_fix, hiE>' out.json                                                               # held-out bench
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
_sp = importlib.util.spec_from_file_location("offset_for_underpass", os.path.join(HERE, "offset-shortcar-relay-4r.py"))
OS = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(OS)      # installs envsel first when argv is 'hwsweep ... -2'
PT, BV, AA, CB = OS.PT, OS.BV, OS.AA, OS.CB
ID = "underpass-bridge-relay-4r"
D2R = math.pi / 180
VDIR = os.path.join(REPO, "docs", "concepts", "verify", ID); os.makedirs(VDIR, exist_ok=True); PT.VDIR = VDIR; OS.VDIR = VDIR
PT.DEF.update(up_clr=1.2, postH=2.0, postL=4.0, ant="ii", tshc=2.5, rl_fix=0.0, hiE=0.0, P_load=4.0)
CLAIM_PARENT = dict(OS.CLAIM_PARENT)
HW0 = dict(carw=14.0, pre=0.0, ds=31.0, delta=4.5, coil="lug", coilD=12.0, coilL=10.0, flange=1, lean=0)
E_TI = 114000.0                                                       # Ti-6Al-4V, N/mm2


def _nobump(M1, G, ax):
    G["ramp"] = G["ramp_req"]; G["ramp_floor"] = 0.0; return {}


PT.bump_amounts = _nobump
_GEOM_OS = OS.geometry
_RELAY_OS = OS.relay_points


def _tsh(rp):
    return float(rp.get("tshc", 2.5)) if str(rp.get("ant", "ii")) == "ii" else 1.5


def geometry(M1, B1, ax, rp):
    """the parent's offset geometry with the shell underside at rl_fix (frozen) and the top at rl_fix + tsh"""
    rp = dict(rp); rl = float(rp.get("rl_fix", 0.0)); tsh = _tsh(rp)
    G = _GEOM_OS(M1, B1, ax, rp); skin = G["R_liner"]
    if rl > 0:
        rl = max(rl, skin)
        for _ in range(4):                                            # OS: R_liner = p90max(arc) + 4 + rt_extra, R_t = R_liner + 1.5
            p90max = G["R_liner"] - 4.0 - float(rp.get("rt_extra", 2.5))
            rp["rt_extra"] = rl + tsh - 1.5 - p90max - 4.0; G = _GEOM_OS(M1, B1, ax, rp)
            if abs(G["R_t"] - (rl + tsh)) < 0.01: break
        G["skin_R_liner"] = skin
    else: rl = G["R_t"] - 1.5; G["skin_R_liner"] = skin
    G["R_under"] = rl; G["R_liner"] = rl; G["tsh"] = G["R_t"] - rl; G["ant"] = str(rp.get("ant", "ii"))
    G["postH"] = float(rp.get("postH", 2.0)); G["postL"] = float(rp.get("postL", 4.0)); G["hiE"] = float(rp.get("hiE", 0.0))
    G["up_clr"] = float(rp.get("up_clr", 1.2)); G["P_load"] = float(rp.get("P_load", 4.0))
    # bridge deflection at the carriage's far end (4 N): ii = curved cantilever, i = simply supported
    t = G["tsh"]; I = 8.0 * t ** 3 / 12.0; R = rl + 0.5 * t
    if G["ant"] == "ii":
        a = (G["hi"] - G["lo"]) * D2R; G["defl_mm"] = G["P_load"] * R ** 3 / (E_TI * I) * (0.5 * a - 0.25 * math.sin(2 * a))
        G["root_Nmm"] = G["P_load"] * R * math.sin(a)
    else:
        L = (G["th0_pad"] + G["hiE"] + math.degrees(3.0 / rl) - G["lo"]) * D2R * R
        G["defl_mm"] = G["P_load"] * L ** 3 / (48 * E_TI * I); G["root_Nmm"] = 0.0
    return G


def _radial(P, ax):
    r = AA._rad(P, ax); n = np.linalg.norm(r, axis=1, keepdims=True); n[n < 1e-9] = 1.0; return r / n


def _sector_surface(G, ax, r0, r1, sa, sb, ta, tb, under=True, top=False, step=2.0):
    """surface samples (~1 pt / 4 mm2) of an annular sector about ax: underside r0 (in band), optional top r1, the four
    side faces; returns pts, in-band mask, az tags"""
    e, f = G["e"], G["f"]; P = []; ib = []; az = []
    nt = max(2, int(math.ceil(abs(tb - ta) * D2R * r1 / step)) + 1); ns = max(2, int(math.ceil((sb - sa) / step)) + 1)
    nr = max(2, int(math.ceil((r1 - r0) / step)) + 1)
    ts = np.linspace(ta, tb, nt); ss = np.linspace(sa, sb, ns); rs = np.linspace(r0, r1, nr)
    for t in ts:
        d = math.cos(t * D2R) * e + math.sin(t * D2R) * f
        for sv in ss:
            if under: P.append(sv * ax + r0 * d); ib.append(True); az.append(t)
            if top: P.append(sv * ax + r1 * d); ib.append(False); az.append(t)
        for r in rs[1:-1]:
            for sv in (sa, sb): P.append(sv * ax + r * d); ib.append(False); az.append(t)
    for t in (ta, tb):
        d = math.cos(t * D2R) * e + math.sin(t * D2R) * f
        for sv in ss:
            for r in rs[1:-1]: P.append(sv * ax + r * d); ib.append(False); az.append(t)
    return P, ib, az


def relay_points(G, ax):
    """the parent's offset relay hardware, with the shell underside / T-nut flange moved to the real underside R_under, plus
    the bridge supports (and the anterior extension for ant='i') as arm-fixed sampled metal; G['supports'] = jam sectors"""
    arm, car = _RELAY_OS(G, ax); arm = np.array(arm, float); car = np.array(car, float)
    aib = G["arm_ib"].copy(); aaz = G["arm_az"].copy(); tag = G["car_tag"]
    Ru, Rt, s0 = G["R_under"], G["R_t"], G["s0"]; shift = (Rt - 1.5) - Ru
    if abs(shift) > 1e-9:
        m = aib & np.isfinite(aaz); arm[m] -= shift * _radial(arm[m], ax)
        mf = tag == "flange"
        if mf.any(): car[mf] -= shift * _radial(car[mf], ax)
    sup = []; extra = []; xib = []; xaz = []; xnm = []
    H, Lp = G["postH"], G["postL"]; dA = math.degrees(Lp / Ru); hw_ = 0.5 * PT.SH_W
    sup.append(("post", Ru - H, Ru, s0 - hw_, s0 + hw_, G["lo"] - dA, G["lo"]))
    P, ib, az = _sector_surface(G, ax, Ru - H, Ru, s0 - hw_, s0 + hw_, G["lo"] - dA, G["lo"]); extra += P; xib += ib; xaz += az; xnm += ["post"] * len(P)
    if G["ant"] == "i":
        a_ext0 = G["hi"]; a_b0 = G["th0_pad"] + G["hiE"] + math.degrees(1.0 / Ru); a_b1 = a_b0 + math.degrees(4.0 / Ru)
        if a_b0 > a_ext0:
            sup.append(("ext", Ru, Rt, s0 - hw_, s0 + hw_, a_ext0, a_b1))
            P, ib, az = _sector_surface(G, ax, Ru, Rt, s0 - hw_, s0 + hw_, a_ext0, a_b1, top=True); extra += P; xib += ib; xaz += az; xnm += ["ext"] * len(P)
        sup.append(("ant", Ru - H, Ru, s0 - hw_, s0 + hw_, a_b0, a_b1))
        P, ib, az = _sector_surface(G, ax, Ru - H, Ru, s0 - hw_, s0 + hw_, a_b0, a_b1); extra += P; xib += ib; xaz += az; xnm += ["ant"] * len(P)
    G["supports"] = sup
    na = len(arm)
    if extra: arm = np.r_[arm, np.array(extra)]
    G["arm_ib"] = np.r_[aib, np.array(xib, bool)]; G["arm_az"] = np.r_[aaz, np.array(xaz, float)]
    G["arm_name"] = np.array(["shell" if np.isfinite(x) else "coil_arm" for x in aaz] + xnm)
    return arm, car


_ATTRIB_OS = OS._attrib


def _attrib(i, dall, nC, na, G):
    _ATTRIB_OS(i, dall, nC, na, G); da = dall[nC:nC + na]; nm = G.get("arm_name")
    if nm is None or len(nm) != na: return
    for k in ("post", "ext", "ant"):
        m = nm == k
        if m.any(): OS.PARTS[i][k] = float(da[m].min())
    m = nm == "shell"
    if m.any(): OS.PARTS[i]["shell_only"] = float(da[m].min())


_src = OS._src
_b1 = 'sector(per[n], Q0, Rt - 1.5, Rt, G["s0"] - 0.5 * SH_W'
_b2 = '               for n in ("knee", "E", "boss", "hub3", "L2", "pad") if n in per}\n'
assert _b1 in _src and _src.count(_b2) == 1, "parent rerecord source changed"
_src = _src.replace(_b1, 'sector(per[n], Q0, G.get("R_under", Rt - 1.5), Rt, G["s0"] - 0.5 * SH_W')
_src = _src.replace(_b2, _b2 + """        for _sp_ in G.get("supports", []):
            for _n in ("knee", "E", "boss", "hub3", "L2", "pad"):
                if _n in per: dpt[_n + "@" + _sp_[0]] = sector(per[_n], Q0, *_sp_[1:])
""")
_src = _src.replace("def rerecord_offset(", "def rerecord_underpass(")
PT._attrib = _attrib
exec(compile(_src, "rerecord_underpass", "exec"), PT.__dict__)
PT.geometry = geometry; PT.relay_points = relay_points; PT.rerecord = PT.rerecord_underpass


def need_scan(S, hw):
    """max chain radius about a_r in the shell footprint (arm frame) per 1-deg azimuth bin rel pad and in the T-nut flange
    footprint (carriage frame), over the fit kin_ok poses (phi 0) + the envsel fresh ws poses (relayed); E's arm-frame
    azimuth envelope at the station (|s - s0| <= 7)"""
    M1, B1, M, B, ax = S["M1"], S["B1"], S["M"], S["B"], S["ax"]
    rp = dict(S["rp"]); rp.update({k: v for k, v in hw.items() if k in PT.DEF}); rp["rl_fix"] = 0.0
    G = geometry(M1, B1, ax, rp); e, f, s0, lo, hi, tc, th0p = G["e"], G["f"], G["s0"], G["lo"], G["hi"], G["th0"], G["th0_pad"]
    HG0 = AA.Z0["HG"]; frames = [("fit", M1, int(j), M1.Q[j]) for j in np.nonzero(M1.kin_ok)[0]]
    if S["nc"] == -2:
        frames += [("env", M, j, HG0[B.idx[j]].astype(float)) for j in range(len(B.idx))
                   if B.kind[j] == "ws" and B.clip[j] == "Envelope sample (fresh)" and S["res0"][j] is not None]
    names = list(M1.rigid) + list(M1.link_pts); parts = list(M1.rigid.values()) + list(M1.link_pts.values())
    bins = np.arange(-40.0, 91.0, 1.0); rmax = np.full(len(bins) - 1, -1.0); who = [None] * (len(bins) - 1)
    hcar = math.degrees(0.5 * PT.CAR_W / G["R_t"]); fl = -1.0; fl_who = None; eaz = [1e9, -1e9]
    for src, MM, j, Q0 in frames:
        RS = MM.RS[j]; Qp = MM.Q[j]
        for nm, (m, X) in zip(names, parts):
            w = MM.world(m, j, X) @ RS; h = w @ Q0; sv = h @ ax
            ins = np.abs(sv - s0) <= 0.5 * PT.SH_W + 1.0
            if ins.any():
                r = np.linalg.norm(AA._rad(h[ins], ax), axis=1); az = np.degrees(np.arctan2(h[ins] @ f, h[ins] @ e))
                azr = (az - th0p + 180.0) % 360.0 - 180.0; k = np.digitize(azr, bins) - 1; ok = (k >= 0) & (k < len(rmax))
                for kk, rr in zip(k[ok], r[ok]):
                    if rr > rmax[kk]: rmax[kk] = rr; who[kk] = (nm, src, j)
                if nm == "E":
                    a7 = azr[np.abs(sv[ins] - s0) <= 7.0]
                    if len(a7): eaz = [min(eaz[0], float(a7.min())), max(eaz[1], float(a7.max()))]
            hc = w @ Qp; svc = hc @ ax; inf_ = np.abs(svc - s0) <= 5.0
            if inf_.any():
                azc = np.degrees(np.arctan2(hc[inf_] @ f, hc[inf_] @ e)); azcr = (azc - tc + 180.0) % 360.0 - 180.0; q = np.abs(azcr) <= hcar + 0.8
                if q.any():
                    rc = np.linalg.norm(AA._rad(hc[inf_][q], ax), axis=1)
                    if rc.max() > fl: fl = float(rc.max()); fl_who = (nm, src, j)
    c = 0.5 * (bins[:-1] + bins[1:])

    def win(a0, a1):
        sel = (c >= a0 - 0.5) & (c <= a1 + 0.5) & (rmax > 0)
        if not sel.any(): return -1.0, None
        k = int(np.argmax(np.where(sel, rmax, -1))); return float(rmax[k]), (who[k], round(float(c[k]), 1))
    sh, sh_who = win(lo - th0p, hi - th0p)
    return dict(skin_R_liner=G["skin_R_liner"], sh_max=sh, sh_who=sh_who, fl_max=fl, fl_who=fl_who, E_az=eaz, lo=lo - th0p, hi=hi - th0p,
                rmax_bins={str(round(float(x), 1)): round(float(y), 2) for x, y in zip(c, rmax) if y > 0}, win=win, n_frames=len(frames))


def place(S, hw):
    """the bridge placement (selection bench only): rl_fix and hiE from the need scan"""
    hw = dict(HW0, **hw); nd = need_scan(S, hw); up = float(hw.get("up_clr", PT.DEF["up_clr"])); hiE = nd["E_az"][1]
    sh = nd["sh_max"]
    if str(hw.get("ant", PT.DEF["ant"])) == "i":
        Ru0 = max(nd["skin_R_liner"], sh + up); sh2, _ = nd["win"](nd["lo"], hiE + math.degrees(5.0 / Ru0)); sh = max(sh, sh2)
    rl = max(nd["skin_R_liner"], sh + up, nd["fl_max"] + 3.0)
    return dict(rl_fix=round(rl, 3), hiE=round(hiE, 2)), {k: v for k, v in nd.items() if k != "win"}


def prepare(base, nc=60, nw=160, exact=False):
    return OS.prepare(base, nc, nw, exact)


def wear(S, hw):
    hw = dict(HW0, **hw); scan = None
    if not float(hw.get("rl_fix", 0.0)):
        pl, scan = place(S, hw); hw.update(pl)
    o = OS.wear(S, hw); G = OS.PARTS.get("_G", {})
    o["underpass"] = dict(R_under=round(G.get("R_under", 0), 3), R_t=round(G.get("R_t", 0), 3), tsh=round(G.get("tsh", 0), 2), ant=G.get("ant"),
                          postH=G.get("postH"), postL=G.get("postL"), hiE=G.get("hiE"), up_clr=G.get("up_clr"), skin_R_liner=round(G.get("skin_R_liner", 0), 2),
                          defl_mm=round(G.get("defl_mm", 0), 3), root_Nmm=round(G.get("root_Nmm", 0), 1), rl_fix=hw["rl_fix"],
                          supports=[[s[0]] + [round(float(x), 2) for x in s[1:]] for s in G.get("supports", [])], scan=scan)
    B = S["B"]; tk = [j for j in range(len(B.idx)) if B.res[j] is not None and float(np.min(B.res[j])) >= 0]
    sm = {}
    for k in ("post", "ext", "ant", "shell_only", "flange", "bracket", "coil", "car"):
        v = [(OS.PARTS[j][k], j) for j in tk if j in OS.PARTS and k in OS.PARTS[j]]
        if v: d, j = min(v); sm[k] = dict(mm=round(d, 2), i=j, pose=[B.poses[j][q] for q in ("plane", "elev", "axial")])
    o["underpass"]["part_min_taken"] = sm
    o["underpass"]["n_metal_lt1_taken"] = int(sum(1 for j in tk if float(np.min(B.res[j])) < 1.0))
    o["underpass"]["n_metal_lt2_taken"] = int(sum(1 for j in tk if float(np.min(B.res[j])) < 2.0))
    o["hw_full"] = hw
    return o


def summary(o):
    s = OS.summary(o); u = o["underpass"]
    s.update(R_under=u["R_under"], R_t=u["R_t"], tsh=u["tsh"], ant=u["ant"], postH=u["postH"], hiE=u["hiE"], defl=u["defl_mm"], root=u["root_Nmm"],
             parts_min=u["part_min_taken"], lt1=u["n_metal_lt1_taken"], lt2=u["n_metal_lt2_taken"],
             jam_list=[(j["i"], j["track_part"], j["track_mm"], j["carriage_part"], j["carriage_mm"]) for j in o["hw"]["jams"]][:12],
             ib_relay=o["hw"]["ib14_relay_metal"], rl_fix=u["rl_fix"])
    return s


def hwsweep(base, hwl, nc, nw, outp, exact, sweep=None):
    S = prepare(base, nc, nw, exact=exact); res = []
    print(json.dumps(dict(prepared=True, ideal=S["ideal"])), flush=True)
    for hw in hwl:
        o = wear(S, dict(base, **hw)); o["hw_override"] = hw; res.append(o)
        sm = summary(o); print(json.dumps(dict(hw=hw, **sm), default=float), flush=True)
        if outp:
            json.dump(res, open(outp, "w"), default=float)
            if nc != -2:
                pp = OS.perpose(S); pp.update(id=ID, wear=f"bench({nc},{nw})", params=dict(base, **o["hw_full"]), exact=exact)
                json.dump(pp, open(outp.replace(".json", f"_{len(res) - 1}_perpose.json"), "w"), default=float)
        if sweep:
            _append_sweep(sweep, dict(base, **o["hw_full"]), o, nc, nw)
    return res


def _append_sweep(path, params, o, nc, nw):
    import datetime
    L = json.load(open(path)) if os.path.exists(path) else []
    w = o["wear"]; ibg = o["ib14_gate"]
    L.append(dict(k=len(L), t=datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"), params={k: v for k, v in params.items()},
                  bench=("envsel exact" if nc == -2 else f"Bench({nc},{nw})"), inband14=ibg, inband14_pooled=w["inband14"], inband10=w["inband10"],
                  reach=w["reach"], follow=w["follow"], contact=w["contact"], gap=o["gate_gap"], plain=w["gap"], near1=o["near1_gap"],
                  jams=len(o["hw"]["jams"]), defl_mm=o["underpass"]["defl_mm"]))
    json.dump(L, open(path, "w"), indent=1, default=float)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    if mode == "hwsweep":
        par = json.loads(sys.argv[2]); hwl = json.loads(sys.argv[3]); nc = int(sys.argv[4]); nw = int(sys.argv[5])
        outp = sys.argv[6] if len(sys.argv) > 6 else None; sw = os.environ.get("UP_SWEEP")
        hwsweep(dict(CLAIM_PARENT, **par), hwl, nc, nw, outp, os.environ.get("CB_EXACT") == "1" or nc == -2, sweep=sw); sys.exit(0)
    if mode == "held":
        par = json.loads(sys.argv[2]); outp = sys.argv[3] if len(sys.argv) > 3 else None; base = dict(CLAIM_PARENT, **par)
        S = prepare(base, -1, -1, exact=True); o = wear(S, base); o["row"] = ID
        print(json.dumps(summary(o), default=float), flush=True)
        if outp:
            json.dump(o, open(outp, "w"), indent=1, default=float)
            pp = OS.perpose(S); pp.update(id=ID, wear="held", params=dict(base, **o["hw_full"]), exact=True)
            json.dump(pp, open(outp.replace(".json", "_perpose.json"), "w"), default=float)
        sys.exit(0)
    print("modes: hwsweep | held")
