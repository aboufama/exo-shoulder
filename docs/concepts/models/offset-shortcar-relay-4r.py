"""offset-shortcar-relay-4r (round 106, J6 track jump): proxtrack-relay-knuckle-4r's one-sided arm-fixed relay re-priced
under the BUILDABLE pin-a stack (the knee link rides over the bumped boss: the verifier's stackfix_amounts, 18c4b46, in
EVERY reading), with three hardware changes:

  * STATION: ds (track station proximal of the pad) is a hardware parameter, chosen on envsel (the pin-a boss leaves
    the shell window as ds grows; the bracket gets a longer, legal run).
  * SHORT, OFFSET CARRIAGE: carriage width carw (14 mm Ti T-nut) with the pre-arc at its floor; the carriage RESTS
    delta deg anterior (+az, the relay's sense) of the pad's azimuth th0: shell [th0 + delta - a0, th0 + delta + PHI + aP],
    carriage centre th0 + delta (+ phi in the arm frame); the pad bracket turns delta deg in planform from the carriage's
    distal edge to the pad's proximal edge.
  * HARDWARE METAL the parent did not carry: the T-nut's retaining flange under the shell (1 mm Ti, 8 wide key, the
    verifier's flange sampling, skin-facing); the constant-force coil (8 OD x 8 wide cylinder, axis along s) sampled as
    metal (contact list) AND on the jam list (chain metal < 1 mm -> pose lost): coil='arm' arm-fixed beyond the moved
    zero end (az lo - (D/2 + 1)/R_t, underside R_t + 1), coil='lug' on the carriage's posterior-proximal lug (anterior
    edge at az <= th0 + 2, proximal of the shell, underside at the carriage top), coil='none' (controls only).
  * LEAN FLAG (lean=1): h_c 1.4, the slot end as the PHI stop ((CAR_W/2 + 1.5)/R_t) and one dowel at the zero end
    ((CAR_W/2 + 2 + 1.5)/R_t); bracket integral with BOTTOM (same sampling).

The parent model is imported READ-ONLY through the buildability verifier (one module instance, so the verifier's stack rule
and the parent's bump / weights / rerecord see the same patched geometry). VDIR is this row's own verify dir.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/offset-shortcar-relay-4r.py controls out.json      # 3 controls, claim bench
    ... hwsweep '<base json>' '<list of hw overrides>' -2 0 out.json                                              # envsel (selection)
    CB_EXACT=1 ... hwsweep '<base>' '<list>' 110 360 out.json                                                     # claim bench
    CB_EXACT=1 ... held '<json>' out.json                                                                          # held-out bench
    ... gravity '<json>'                                                                                           # R17
"""
import importlib.util, inspect, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
if len(sys.argv) > 4 and sys.argv[1] == "hwsweep" and sys.argv[4] == "-2":
    import env_bench as _EB; _EB.install()                 # envsel poses appended to the archive BEFORE armarc reads Z0 (the parent's -2 path needs it)

    class _NZ(dict):                                         # armarc reads the archive as an NpzFile (.files)
        @property
        def files(self): return list(self.keys())
    _EB._ZX["Z"] = _NZ(_EB._ZX["Z"])
_sp = importlib.util.spec_from_file_location("proxtrack_build_for_offset", os.path.join(REPO, "docs", "concepts", "verify",
                                                                                         "proxtrack-relay-knuckle-4r-buildability.py"))
BV = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(BV)
PT = BV.PT; AA, CB, CC = PT.AA, PT.CB, PT.CC
ID = "offset-shortcar-relay-4r"
D2R = math.pi / 180
VDIR = os.path.join(REPO, "docs", "concepts", "verify", ID); PT.VDIR = VDIR
# hardware keys this row adds (PT.wear copies only keys in PT.DEF into rp)
PT.DEF.update(delta=0.0, carw=24.0, coil="arm", flange=1, lean=0, h_c=1.7, coilD=8.0, coilL=8.0)
DEF = dict(PT.DEF)
CLAIM_PARENT = dict(BV.CLAIM)                                # proxtrack's claim (PHI 35, ds 19.538, rt 1.5, pre 10.41, ...)
_GEOM0 = PT.geometry
_RELAY0 = BV._ORIG["relay_points"]
PT.bump_amounts = BV.stackfix_amounts                        # the buildable knee-over-boss stack in every reading


def geometry(M1, B1, ax, rp):
    """the parent's geometry (pad azimuth th0, station, p90 skin profile) with the carriage resting delta deg anterior,
    the carriage width carw, per-end pre-arc floors and the lean flag; G['th0'] = the CARRIAGE centre (the parent's
    _wcar / carriage sector read it), G['th0_pad'] = the pad's azimuth"""
    PT.CAR_W = float(rp.get("carw", 24.0))
    G = _GEOM0(M1, B1, ax, dict(rp, pre=0.0))
    delta = float(rp.get("delta", 0.0)); th0 = G["th0"]; PHI = G["PHI"]; sg = G["sg"]; lean = int(rp.get("lean", 0))
    pre = float(rp.get("pre", 0.0)); ths, p90 = G["ths"], G["p90"]; R_t = G["R_t"]
    for _ in range(3):
        if lean: f0, fP = (0.5 * PT.CAR_W + PT.DOWEL + 1.5) / R_t, (0.5 * PT.CAR_W + 1.5) / R_t
        else: f0 = fP = (0.5 * PT.CAR_W + PT.DOWEL) / R_t
        a0, aP = max(pre, math.degrees(f0)), max(pre, math.degrees(fP)); tc = th0 + sg * delta
        lo, hi = (tc - a0, tc + PHI + aP) if sg > 0 else (tc - PHI - aP, tc + a0)
        sel = (ths >= lo - 1.0) & (ths <= hi + 1.0)
        R_liner = float(np.nanmax(p90[:, sel])) + 4.0 + float(rp.get("rt_extra", 2.5)); R_t = R_liner + 1.5
    h_c = 1.4 if lean else float(rp.get("h_c", 1.7)); clr = max(1.0, float(rp.get("bump", 1.0)))
    G.update(th0=tc, th0_pad=th0, delta=delta, lo=lo, hi=hi, pre=a0, pre_phi=aP, pre_floor=math.degrees(f0), R_liner=R_liner, R_t=R_t,
             h_c=h_c, R_b=R_t + h_c + clr, clr=clr, coil=str(rp.get("coil", "arm")), flange=int(rp.get("flange", 1)), lean=lean,
             coilD=float(rp.get("coilD", 8.0)), coilL=float(rp.get("coilL", 8.0)))
    # the coil cylinder (axis along ax): centre, frame ('arm' = arm-fixed HG0, 'car' = carriage frame HG')
    e, f, Rt, D, L = G["e"], G["f"], R_t, G["coilD"], G["coilL"]
    if G["coil"] == "arm":
        az = (lo - math.degrees((0.5 * D + 1.0) / Rt)) if sg > 0 else (hi + math.degrees((0.5 * D + 1.0) / Rt))
        G["coil_c"] = (G["s0"], az, Rt + 1.0 + 0.5 * D); G["coil_frame"] = "arm"
    elif G["coil"] == "lug":
        az = th0 + 2.0 - math.degrees(0.5 * D / Rt)          # anterior edge at th0 + 2 (the judge's 0/184 footprint)
        G["coil_c"] = (G["s0"] + 0.5 * PT.SH_W + 1.0 + 0.5 * L, az, Rt + h_c + 0.5 * D); G["coil_frame"] = "car"
    else: G["coil_c"] = None; G["coil_frame"] = None
    if G["coil_c"] is not None:
        s_c, az_c, r_c = G["coil_c"]; d = math.cos(az_c * D2R) * e + math.sin(az_c * D2R) * f; G["coil_xyz"] = s_c * ax + r_c * d
    return G


def _coil_surface(G, ax):
    """coil cylinder surface (~2 mm sampling): rim circles + end discs"""
    e, f = G["e"], G["f"]; s_c, az_c, r_c = G["coil_c"]; D, L = G["coilD"], G["coilL"]
    d = math.cos(az_c * D2R) * e + math.sin(az_c * D2R) * f; t = np.cross(ax, d); c = s_c * ax + r_c * d; pts = []
    nth = max(8, int(math.ceil(math.pi * D / 2.0)))
    for sv in np.arange(-0.5 * L, 0.5 * L + 0.01, 2.0):
        for k in range(nth):
            a = 2 * math.pi * k / nth; pts.append(c + sv * ax + 0.5 * D * (math.cos(a) * d + math.sin(a) * t))
    for sv in (-0.5 * L, 0.5 * L):
        for rr in np.arange(1.0, 0.5 * D, 2.0):
            nk = max(4, int(math.ceil(2 * math.pi * rr / 2.0)))
            for k in range(nk):
                a = 2 * math.pi * k / nk; pts.append(c + sv * ax + rr * (math.cos(a) * d + math.sin(a) * t))
    return np.array(pts)


def relay_points(G, ax):
    """shell (arm frame, the parent's sampling at the offset arc) + arm-fixed coil; carriage at th0 + delta, lug coil,
    bracket with the planform turn (underside, in band), T-nut flange (in band). Order in the carriage list: non-in-band
    (carriage, lug coil) first, then in-band (bracket, flange) - the parent's bracket jam check reads wc[n_non_ib:]."""
    e, f, s0, Rt = G["e"], G["f"], G["s0"], G["R_t"]; dt = 2.0 / Rt / D2R
    arm = []; aib = []; atag = []; car = []; cib = []; ctag = []
    for t in np.arange(G["lo"], G["hi"] + 1e-9, dt):
        d = math.cos(t * D2R) * e + math.sin(t * D2R) * f
        for sv in np.arange(s0 - 0.5 * PT.SH_W, s0 + 0.5 * PT.SH_W + 0.01, 2.0):
            arm.append(sv * ax + (Rt - 1.5) * d); aib.append(True); atag.append(t)
            arm.append(sv * ax + Rt * d); aib.append(False); atag.append(t)
    if G["coil_frame"] == "arm":
        cs = _coil_surface(G, ax); arm += list(cs); aib += [False] * len(cs); atag += [np.nan] * len(cs)
    half = 0.5 * PT.CAR_W / Rt / D2R; tc = G["th0"]
    for t in np.arange(tc - half, tc + half + 1e-9, dt):
        d = math.cos(t * D2R) * e + math.sin(t * D2R) * f
        for sv in np.arange(s0 - 0.5 * PT.CAR_L, s0 + 0.5 * PT.CAR_L + 0.01, 2.0):
            car.append(sv * ax + (Rt + 0.2) * d); cib.append(False); ctag.append("car")
            car.append(sv * ax + (Rt + G["h_c"]) * d); cib.append(False); ctag.append("car")
    if G["coil_frame"] == "car":
        cs = _coil_surface(G, ax); car += list(cs); cib += [False] * len(cs); ctag += ["coil"] * len(cs)
    # bracket: 2 x 10 Ti, carriage's pad-side edge at the carriage top (az th0 + delta) -> pad's facing edge (az th0)
    sg_ = 1.0 if G["s_pad"] > s0 else -1.0; s_a = s0 + sg_ * 0.5 * PT.CAR_L; s_b = G["s_pe"]
    r_a = Rt + G["h_c"]; r_b = G["rpad"]; hb = 5.0 / Rt / D2R; ta, tb = tc, G["th0_pad"]
    n_s = max(2, int(math.ceil(abs(s_b - s_a) / 2.0)) + 1)
    for sv in np.linspace(s_a, s_b, n_s):
        u = (sv - s_a) / (s_b - s_a) if abs(s_b - s_a) > 1e-9 else 1.0
        r = r_a + (r_b - r_a) * u; tm = ta + (tb - ta) * u
        for t in np.arange(tm - hb, tm + hb + 1e-9, dt):
            d = math.cos(t * D2R) * e + math.sin(t * D2R) * f; car.append(sv * ax + r * d); cib.append(True); ctag.append("bracket")
    if G["flange"]:
        for t in np.arange(tc - half, tc + half + 1e-9, dt):
            d = math.cos(t * D2R) * e + math.sin(t * D2R) * f
            for sv in np.arange(s0 - 4.0, s0 + 4.0 + 0.01, 2.0): car.append(sv * ax + (Rt - 1.5 - 1.0) * d); cib.append(True); ctag.append("flange")
    G["arm_ib"] = np.array(aib, bool); G["car_ib"] = np.array(cib, bool); G["arm_az"] = np.array(atag, float); G["car_tag"] = np.array(ctag)
    run = math.hypot(abs(s_b - s_a), abs(tb - ta) * D2R * 0.5 * (r_a + r_b))
    G["bracket_ramp_deg"] = round(math.degrees(math.atan2(abs(r_a - r_b), run)), 1); G["bracket_turn_mm"] = round(abs(tb - ta) * D2R * r_a, 2)
    return np.array(arm), np.array(car)


def _coil_d(w, RS, Qf, G, ax):
    """distance of world points w to the coil cylinder in frame Qf"""
    h = (w @ RS) @ Qf; rel = h - G["coil_xyz"]; sv = rel @ ax; rr = np.linalg.norm(rel - sv[:, None] * ax[None], axis=1)
    return float(np.sqrt(np.maximum(0, rr - 0.5 * G["coilD"]) ** 2 + np.maximum(0, np.abs(sv) - 0.5 * G["coilL"]) ** 2).min())


PARTS = {}


def _attrib(i, dall, nC, na, G):
    """per-pose minima by part (diagnostic): chain / shell (+ az rel th0_pad of its deepest point) / coil / carriage /
    bracket / flange"""
    da = dall[nC:nC + na]; dc = dall[nC + na:]; az = G["arm_az"]; sh = np.isfinite(az); out = dict(chain=float(dall[:nC].min()))
    if sh.any():
        k = int(np.argmin(np.where(sh, da, np.inf))); out["shell"] = float(da[k]); out["shell_az"] = round(float(az[k] - G["th0_pad"]), 1)
    if (~sh).any(): out["coil_arm"] = float(da[~sh].min())
    for tg in ("car", "coil", "bracket", "flange"):
        m = G["car_tag"] == tg
        if m.any(): out[tg] = float(dc[m].min())
    PARTS[i] = out; PARTS["_G"] = G


_src = inspect.getsource(BV._ORIG["rerecord"])
_a1 = "        dall = B.dist(i, np.r_[chain, wa, wc]); nC = len(chain)\n"
_a2 = "        dmin, dcar = min(dpt.values()), min(dpc.values())\n"
assert _a1 in _src and _a2 in _src, "parent rerecord source changed"
_src = _src.replace(_a1, _a1 + "        _attrib(i, dall, nC, len(wa), G)\n")
_src = _src.replace(_a2, """        if G.get("coil_frame") is not None:
            _Qc = Q0 if G["coil_frame"] == "arm" else Qp
            for _n in ("knee", "E", "boss", "hub3", "L2", "pad"):
                if _n in per: (dpt if G["coil_frame"] == "arm" else dpc)["coil:" + _n] = _coil_d(per[_n], RS, _Qc, G, ax)
""" + _a2)
_src = _src.replace("def rerecord(", "def rerecord_offset(")
PT._attrib = _attrib; PT._coil_d = _coil_d
exec(compile(_src, "rerecord_offset", "exec"), PT.__dict__)
PT.geometry = geometry; PT.relay_points = relay_points; PT.rerecord = PT.rerecord_offset


def prepare(base, nc=60, nw=160, exact=False):
    return PT.prepare(base, nc, nw, exact)


def wear(S, hw):
    """PT.wear (buildable stack, offset hardware) + the contacts attributed by part and the bracket / coil geometry"""
    PARTS.clear(); o = PT.wear(S, hw); B = S["B"]; G = PARTS["_G"]
    o["offset_hw"] = dict(delta=G["delta"], carw=PT.CAR_W, th0_pad=round(G["th0_pad"], 2), arc_rel_th0=[round(G["lo"] - G["th0_pad"], 2), round(G["hi"] - G["th0_pad"], 2)],
                          pre_zero=round(G["pre"], 2), pre_phi=round(G["pre_phi"], 2), R_t=round(G["R_t"], 2), h_c=G["h_c"], coil=G["coil"],
                          coil_c=None if G["coil_c"] is None else [round(float(x), 2) for x in G["coil_c"]], flange=G["flange"], lean=G["lean"],
                          shell_len_mm=round((G["hi"] - G["lo"]) * D2R * G["R_t"], 1))
    o["stackfix"] = dict(BV.OUT.get("stackfix", {}))
    for c in o["contacts"]:
        p = PARTS.get(c["i"], {}); c["parts"] = {k: (round(v, 2) if isinstance(v, float) else v) for k, v in p.items()}
        hwp = {k: v for k, v in p.items() if k in ("shell", "coil_arm", "car", "coil", "bracket", "flange")}
        c["cause"] = "hardware" if hwp and min(hwp.values()) < 0 and p.get("chain", 1) >= 0 else ("chain+hw" if hwp and min(hwp.values()) < 0 else "chain")
    o["contacts_by_cause"] = {k: sum(1 for c in o["contacts"] if c["cause"] == k) for k in ("chain", "hardware", "chain+hw")}
    o["shell_min_taken"] = None
    tk = [j for j in range(len(B.idx)) if B.res[j] is not None and float(np.min(B.res[j])) >= 0 and j in PARTS and "shell" in PARTS[j]]
    o["bracket_turn_mm"] = G.get("bracket_turn_mm")
    if tk: j = min(tk, key=lambda j: PARTS[j]["shell"]); o["shell_min_taken"] = dict(i=j, mm=round(PARTS[j]["shell"], 2), az_rel=PARTS[j]["shell_az"])
    return o


def perpose(S):
    o = PT.perpose(S); o["id"] = ID; return o


def summary(o):
    return dict(gate=o["gate_gap"], chain_only=o["chain_only_gap"], plain=o["wear"]["gap"], near1=o["near1_gap"], near2=o["near2_gap"],
                ibc=o["hw"]["ib14_chain_only"], ib=o["wear"]["inband14"], ib10=o["wear"]["inband10"], reach=o["wear"]["reach"], fol=o["wear"]["follow"],
                con=o["wear"]["contact"], ncon=len(o["contacts"]), jams=len(o["hw"]["jams"]), ws_taken=o["ws_taken"], overhead=o["overhead"],
                by_cause=o["contacts_by_cause"], hwc=[(c["i"], c["min_mm"], c["parts"].get("shell_az")) for c in o["contacts"] if c["cause"] != "chain"],
                stack=o["stackfix"].get("boss_lift_max"), arc=o["offset_hw"]["arc_rel_th0"], R_t=o["offset_hw"]["R_t"], shell_min=o["shell_min_taken"],
                bracket=[o["hw"].get("bracket_ramp_deg")], secs=o["secs"])


def hwsweep(base, hwl, nc, nw, outp, exact):
    S = prepare(base, nc, nw, exact=exact); res = []
    print(json.dumps(dict(prepared=True, ideal=S["ideal"])), flush=True)
    for hw in hwl:
        o = wear(S, dict(base, **hw)); o["hw_override"] = hw; res.append(o)
        print(json.dumps(dict(hw=hw, **summary(o)), default=float), flush=True)
        if outp:
            json.dump(res, open(outp, "w"), default=float)
            if nc != -2:
                pp = perpose(S); pp.update(wear=f"bench({nc},{nw})", params=dict(base, **hw), exact=exact)
                json.dump(pp, open(outp.replace(".json", f"_{len(res) - 1}_perpose.json"), "w"), default=float)
    return res


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    if mode == "controls":                                  # the three controls on one claim-bench prepare (frozen exact)
        outp = sys.argv[2]; os.environ["CB_EXACT"] = "1"
        hwl = [dict(carw=24.0, pre=10.41, ds=19.538, delta=0.0, coil="none", flange=0),
               dict(carw=14.0, pre=0.0, ds=19.538, delta=0.0, coil="none", flange=0),
               dict(carw=14.0, pre=0.0, ds=31.0, delta=0.0, coil="none", flange=0)]
        hwl += [dict(h, **json.loads(x)) for x in sys.argv[3:] for h in [{}]]
        hwsweep(dict(CLAIM_PARENT), hwl, 110, 360, outp, True); sys.exit(0)
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "gravity": print(json.dumps(AA.gravity_check(par))); sys.exit(0)
    if mode == "hwsweep":
        hwl = json.loads(sys.argv[3]); nc = int(sys.argv[4]); nw = int(sys.argv[5]); outp = sys.argv[6] if len(sys.argv) > 6 else None
        hwsweep(dict(CLAIM_PARENT, **par), hwl, nc, nw, outp, os.environ.get("CB_EXACT") == "1"); sys.exit(0)
    if mode == "held":
        outp = sys.argv[3] if len(sys.argv) > 3 else None; base = dict(CLAIM_PARENT, **par)
        S = prepare(base, -1, -1, exact=True); o = wear(S, base); o["row"] = ID
        print(json.dumps(summary(o), default=float), flush=True)
        if outp:
            json.dump(o, open(outp, "w"), indent=1, default=float)
            pp = perpose(S); pp.update(wear="held", params=base, exact=True); json.dump(pp, open(outp.replace(".json", "_perpose.json"), "w"), default=float)
        sys.exit(0)
    print("modes: controls | hwsweep | held | gravity")
