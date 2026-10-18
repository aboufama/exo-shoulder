"""phi40-thinstack-relay-4r (round 107, J7 track jump, lens A fallback): offset-shortcar-relay-4r's one-sided arm-fixed
over-pass relay on the UNCHANGED verified lead chain (conecut-knee-knuckle-3r, buildable pin-a stack in every reading),
with the measured hardware levers of round 107 and a longer travel:

  * PHI 40 (parent 35): the shell runs [th0_pad + delta - a0, th0_pad + delta + PHI + aP]; a new prepare and a new
    continuity flood per PHI (cached in this row's VDIR, kinematic only).
  * THIN STACK: shell thickness tsh 1.0 (Ti on the 4 mm liner, supported along its length): the underside stays at
    R_liner, the shell top R_t = R_liner + tsh, the carriage, bump target R_b = R_t + h_c + bump and the lug coil drop
    with it. Lean flag: h_c 1.4, slot end = PHI stop, one zero dowel. The pre-arc floors (carriage half-arc + dowel /
    slot end) are re-read at the THIN shell's R_t (the proposer's patch read them at R_liner + 1.5: 0.04 deg shorter).
  * LUG COIL 12 x 10 (constant-force strip, carriage's posterior-proximal lug; carriage-frame jam list + contact list).
  * BAND 8 (the floor), BUMP 1.2 (0.2 mm build margin over the 1.0 mm non-adjacent rule).
  * L-LUG BRACKET: the 2 x 10 Ti bracket runs at the PAD's azimuth for every s (no planform turn), anchored at the
    carriage's posterior-distal corner (with delta 3.5-4.0 the pad azimuth lies inside the carriage's posterior half).

The parent model is imported READ-ONLY (one module instance; the source patches are applied to that instance only).
Envsel is installed by the parent when argv is 'hwsweep <base> <list> -2 ...' (its lesson 7).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/phi40-thinstack-relay-4r.py hwsweep '<base>' '<hw list>' -2 0 out.json   # envsel (selection)
    CB_EXACT=1 ... pickrun '<base>' '<pre list>' 110 360 <pickfile> out.json ['<post list>']    # claim bench: prepare + flood, wear the pick once written, then post (diagnostics)
    CB_EXACT=1 ... pickrun '<base>' '[]' -1 -1 <pickfile> out.json                              # held-out bench
    ... gravity '<json>'                                                                         # R17 (relay preload)
"""
import importlib.util, inspect, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
_sp = importlib.util.spec_from_file_location("offset_for_phi40", os.path.join(HERE, "offset-shortcar-relay-4r.py"))
OS = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(OS)      # installs envsel first when argv is 'hwsweep ... -2'
PT, BV, AA, CB = OS.PT, OS.BV, OS.AA, OS.CB
ID = "phi40-thinstack-relay-4r"
D2R = math.pi / 180
VDIR = os.path.join(REPO, "docs", "concepts", "verify", ID); os.makedirs(VDIR, exist_ok=True); PT.VDIR = VDIR; OS.VDIR = VDIR
PT.DEF.update(tsh=1.5, lbr=0)
HW0 = dict(carw=14.0, pre=0.0, ds=31.0, delta=3.5, coil="lug", coilD=12.0, coilL=10.0, flange=1, lean=1, band=8.0, bump=1.2,
           tsh=1.0, lbr=1)
CLAIM_PARENT = dict(OS.CLAIM_PARENT, PHI=40.0)                       # proxtrack's claim chain / axis (tilt 12, az 235), PHI 40

# ---- thin stack + L-lug: source patches of the parent's relay_points and rerecord (this module's instance only) ----
_rs = inspect.getsource(OS.relay_points)
for a, b in (("(Rt - 1.5) * d", "(Rt - G.get('tsh', 1.5)) * d"), ("(Rt - 1.5 - 1.0) * d", "(Rt - G.get('tsh', 1.5) - 1.0) * d"),
             ("ta, tb = tc, G[\"th0_pad\"]", "ta, tb = (G[\"th0_pad\"], G[\"th0_pad\"]) if G.get('lbr', 0) else (tc, G[\"th0_pad\"])")):
    assert a in _rs, f"parent relay_points changed: {a}"; _rs = _rs.replace(a, b)
exec(compile(_rs, "relay_points_phi40", "exec"), OS.__dict__); PT.relay_points = OS.relay_points
_rr = OS._src.replace("Rt - 1.5, Rt,", "Rt - G.get('tsh', 1.5), Rt,"); assert _rr != OS._src, "parent rerecord changed"
exec(compile(_rr, "rerecord_phi40", "exec"), PT.__dict__); PT.rerecord = PT.rerecord_offset
_GE = OS.geometry


def geometry(M1, B1, ax, rp):
    """the parent's offset geometry, then the thin shell: R_t = R_liner + tsh (underside unchanged), the pre-arc floors
    and the arc ends re-read at that R_t, R_b / coil centre recomputed; G['lbr'] = L-lug bracket flag"""
    G = _GE(M1, B1, ax, rp); t = float(rp.get("tsh", 1.5)); G["tsh"] = t; G["lbr"] = int(rp.get("lbr", 0))
    if abs(t - 1.5) > 1e-9:
        Rt = G["R_liner"] + t; G["R_t"] = Rt; G["R_b"] = Rt + G["h_c"] + G["clr"]
        if G["lean"]: f0, fP = (0.5 * PT.CAR_W + PT.DOWEL + 1.5) / Rt, (0.5 * PT.CAR_W + 1.5) / Rt
        else: f0 = fP = (0.5 * PT.CAR_W + PT.DOWEL) / Rt
        pre = float(rp.get("pre", 0.0)); a0, aP = max(pre, math.degrees(f0)), max(pre, math.degrees(fP)); tc = G["th0"]; PHI = G["PHI"]
        G["lo"], G["hi"] = (tc - a0, tc + PHI + aP) if G["sg"] > 0 else (tc - PHI - aP, tc + a0)
        G.update(pre=a0, pre_phi=aP, pre_floor=math.degrees(f0)); D = G["coilD"]
        if G["coil_c"] is not None:
            s_c, az_c, _ = G["coil_c"]
            if G["coil"] == "lug": az_c = G["th0_pad"] + 2.0 - math.degrees(0.5 * D / Rt); r_c = Rt + G["h_c"] + 0.5 * D
            else: az_c = (G["lo"] - math.degrees((0.5 * D + 1.0) / Rt)) if G["sg"] > 0 else (G["hi"] + math.degrees((0.5 * D + 1.0) / Rt)); r_c = Rt + 1.0 + 0.5 * D
            G["coil_c"] = (s_c, az_c, r_c); d = math.cos(az_c * D2R) * G["e"] + math.sin(az_c * D2R) * G["f"]; G["coil_xyz"] = s_c * ax + r_c * d
    return G


PT.geometry = geometry

# ---- anterior-end clearance per 2-deg bin (the judge's red-team item: the arm-fixed shell end vs behind-back ER) ----
BINS = {}
_ATT = PT._attrib


def _attrib(i, dall, nC, na, G):
    _ATT(i, dall, nC, na, G); da = dall[nC:nC + na]; az = G["arm_az"] - G["th0_pad"]; sh = np.isfinite(az)
    b = np.floor(az[sh] / 2.0) * 2.0; dd = da[sh]; out = {}
    for k in np.unique(b):
        if k >= 36.0 or k <= -4.0: out[float(k)] = float(dd[b == k].min())
    BINS[i] = out


PT._attrib = _attrib


def prepare(base, nc=60, nw=160, exact=False):
    return OS.prepare(base, nc, nw, exact)


def wear(S, hw):
    BINS.clear(); o = OS.wear(S, hw); B = S["B"]; G = OS.PARTS["_G"]
    tk = [j for j in range(len(B.idx)) if B.res[j] is not None and float(np.min(B.res[j])) >= 0]
    ends = {}
    for j in tk:
        for k, v in BINS.get(j, {}).items():
            if k not in ends or v < ends[k][0]: ends[k] = (round(v, 2), j)
    o["shell_end_bins_taken"] = {f"{k:+.0f}": v for k, v in sorted(ends.items())}
    allb = {}
    for j, bb in BINS.items():
        for k, v in bb.items():
            if k not in allb or v < allb[k][0]: allb[k] = (round(v, 2), j)
    o["shell_end_bins_all"] = {f"{k:+.0f}": v for k, v in sorted(allb.items())}
    o["thin_hw"] = dict(tsh=G["tsh"], lbr=G["lbr"], R_t=round(G["R_t"], 2), R_b=round(G["R_b"], 2), arc=[round(G["lo"] - G["th0_pad"], 2), round(G["hi"] - G["th0_pad"], 2)],
                        PHI=G["PHI"], pre=round(G["pre"], 2), pre_phi=round(G["pre_phi"], 2), coil_c=None if G["coil_c"] is None else [round(float(x), 2) for x in G["coil_c"]])
    return o


def perpose(S):
    o = PT.perpose(S); o["id"] = ID; return o


def summary(o):
    s = OS.summary(o); s.update(arc=o["thin_hw"]["arc"], R_t=o["thin_hw"]["R_t"], R_b=o["thin_hw"]["R_b"],
                                ends=o["shell_end_bins_taken"],
             conn=(None if o.get("continuity") is None else dict(dropped_relayed=o["continuity"]["dropped_relayed"], phi0_not_conn=o["continuity"]["phi0_taken_not_connected"],
                                                                 static_gap=o["continuity"]["static"]["gap"])))
    return s


def _run(base, nc, nw, exact, items, outp, tagger):
    S = prepare(base, nc, nw, exact=exact); res = []
    print(json.dumps(dict(prepared=True, ideal=S["ideal"], flood=S.get("flood"), n=len(S["B"].idx))), flush=True)

    def one(hw, tag):
        o = wear(S, dict(base, **hw)); o["hw_override"] = hw; o["tag"] = tag; res.append(o)
        print(json.dumps(dict(tag=tag, hw=hw, **summary(o)), default=float), flush=True)
        if outp:
            json.dump(res, open(outp, "w"), default=float)
            if nc != -2:
                pp = perpose(S); pp.update(wear=("held" if nc == -1 else f"bench({nc},{nw})"), params=dict(base, **hw), exact=exact, tag=tag)
                json.dump(pp, open(outp.replace(".json", f"_{tag}_perpose.json"), "w"), default=float)
    return S, one, tagger(one)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    if mode == "hwsweep":                                   # hwsweep base list nc nw out
        base = dict(CLAIM_PARENT, **HW0, **json.loads(sys.argv[2])); hwl = json.loads(sys.argv[3]); nc, nw = int(sys.argv[4]), int(sys.argv[5])
        outp = sys.argv[6] if len(sys.argv) > 6 else None; ex = os.environ.get("CB_EXACT") == "1" or nc == -2

        def tg(one):
            for k, hw in enumerate(hwl): one(hw, f"s{k}")
        _run(base, nc, nw, ex, hwl, outp, tg); sys.exit(0)
    if mode == "pickrun":                                   # pickrun base pre nc nw pickfile out [post]: wear pre, then the pick once written, then post
        base = dict(CLAIM_PARENT, **HW0, **json.loads(sys.argv[2])); pre = json.loads(sys.argv[3]); nc, nw = int(sys.argv[4]), int(sys.argv[5])
        pickf, outp = sys.argv[6], sys.argv[7]; post = json.loads(sys.argv[8]) if len(sys.argv) > 8 else []; ex = os.environ.get("CB_EXACT") == "1"

        def tg(one):
            for k, hw in enumerate(pre): one(hw, f"pre{k}")
            while not os.path.exists(pickf): time.sleep(5)
            one(json.load(open(pickf)), "pick")
            for k, hw in enumerate(post): one(hw, f"post{k}")
        _run(base, nc, nw, ex, pre, outp, tg); sys.exit(0)
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "gravity": print(json.dumps(AA.gravity_check(dict(CLAIM_PARENT, **HW0, **par)))); sys.exit(0)
    print("modes: hwsweep | pickrun | gravity")
