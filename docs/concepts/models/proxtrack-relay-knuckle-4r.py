"""proxtrack-relay-knuckle-4r (round 105, J5 track jump): the verified lead conecut-knee-knuckle-3r UNCHANGED (seats, K drive,
metal, knee, J3 dowel stop) with a one-sided ARM-FIXED RELAY TRACK moved 16 mm PROXIMAL of BOTTOM's pad (station
s0 = s_pad + ds about the relay axis a_r through GH, tilt 12 / az 235). The armarc relay model is re-used by import (relay
solve on the lead's own gates, flood continuity, gravity check); what changes is the hardware:

  * ZERO LIFT: the pad keeps the lead's radius (rpad 73.2). It hangs from the carriage on a 2 mm x 10 Ti bracket that
    leaves the carriage's distal edge (s0 - 7) at the carriage top and drops to the pad's proximal edge.
  * TRACK: a slotted circular Ti shell (1.5 mm, 12 wide, T-nut carriage 24 x 14 on an iglidur strip, h_c 1.7), arm-fixed,
    underside R_liner = max clip-p90 skin radius over the arc + 4 liner + rt_extra, spanning [th0 - a, th0 + PHI + a];
    the pre-arc a has a HARD FLOOR = carriage half-arc + stop dowel (2 mm) at R_t (~10 deg): a < floor is clamped.
  * LOCAL RIGID BUMP: member 3 (E strap, pin-a boss, every member-3 contact set) and the knee link (member 6) are bumped
    radially (about a_r) to R_t + bump (bump = clearance over the shell top, floor 1 mm, the non-adjacent rule) and to
    R_t + h_c + bump over the carriage footprint (fixed in the carriage frame, +1 mm, ramped) over the station band [s0 - 10, s0 + 10] and the track's azimuth
    window seen from the carriage at ANY relay angle ([lo - PHI, hi] for sgn +1), with 10 mm ramps in s and in arc.
    The bump is RIGID: one amount per sampled point = the max over every fit-bench pose (lead fit, phi 0) of
    ramp-weight x max(0, R_b - r); contact-only sets take the amount of the nearest sampled point of the same member.
    Bumped points stay sampled metal in ib14.
  * JAMS: shell / track vs knee link, E strap, boss, hub 3, link 2, pad < 1 mm -> pose lost (unless its metal is in the
    skin: then it stays a CONTACT); carriage + bracket vs E,
    boss, hub 3, link 2 < 1 mm -> lost. Arm-fixed shell metal in the skin is a CONTACT (it cannot refuse a pose).
  * GATE (pre-registered by the judge): read on the LOWER of pooled ib14 and chain-only ib14 (shell / carriage / bracket
    out of the share): pass <= 15, kill > 17.5 on frozen exact Bench(110,360).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/proxtrack-relay-knuckle-4r.py check '<json>' [out.json]   # Bench(60,160) fast
    CB_EXACT=1 ... frozen '<json>' [out.json]          # Bench(110,360) exact, frozen (fit Bench(60,160) fast, phi 0)
    CB_EXACT=1 ... held '<json>' [out.json]            # the lead family's held-out bench
    ... hwsweep '<base json>' '<list of hw overrides json>' [bench nc nw] [out.json]   # one fit + relay solve, many hardware configs
    ... hwsweep '<base>' '<list>' -2 0 [out.json]      # the same on envsel (pick selection, exact, static reading)
    ... gravity '<json>'                               # R17: spring preload needed (armarc gravity_check)
params (relay): PHI, tilt, taz, sgn, ds (station offset, + = proximal), rt_extra (mm over p90 + 4), pre (pre-arc deg, floored),
        bump (mm over the carriage top), band (bump half-band in s, floor carriage half-length + 1), ramp (mm,
        floor climb / tan 60 + 2), flood (1 = continuity flood, reach on the connected set; cached per PHI/axis)
"""
import importlib.util, json, math, os, sys, time, copy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
_sp = importlib.util.spec_from_file_location("armarc_for_proxtrack", os.path.join(HERE, "armarc-relay-knuckle-4r.py"))
AA = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(AA)
CB, CC = AA.CB, AA.CC
ID = "proxtrack-relay-knuckle-4r"
D2R = math.pi / 180
AA.RELAY.update(PHI=30.0, tilt=12.0, taz=235.0, sgn=1.0, hw=1, hwv="plain", ds=16.0, rt_extra=2.5, pre=10.0, bump=1.0, band=10.0, ramp=10.0, flood=1)
DEF = dict(AA.RELAY)
CAR_W, CAR_L, SH_W = AA.CAR_W, AA.CAR_L, AA.SH_W
DOWEL = 2.0                                       # ISO 8734 2 m6 stop dowel: the carriage end stops on it
BAND_FLOOR = 0.5 * max(SH_W, CAR_L) + 1.0         # bump band half-width floor: carriage half-length + 1 mm clearance
TAN_MAX = math.tan(60 * D2R)                      # the 60-deg climb ruling: ramp >= climb / tan 60 (+ 2 mm for the bend arcs)
VDIR = os.path.join(REPO, "docs", "concepts", "verify", ID)
BUMP_MEMBERS = (3, 6)


def geometry(M1, B1, ax, rp):
    """HG-frame geometry from the fitted lead (phi 0): pad centroid azimuth th0 / station s_pad about ax; the track at
    s0 = s_pad + ds; skin radius profile about ax (first exit of a ray, p90 over the fit-bench clip poses) over a wide
    window; R_liner = max p90 over the TRACK arc + 4 + rt_extra; R_t = R_liner + 1.5 (shell top); pre-arc floored."""
    e, f = AA._basis(ax)
    i0 = [j for j in range(len(B1.idx)) if B1.kind[j] == "clip" and M1.kin_ok[j]][0]
    m, X = M1.rigid["pad"]; padH = (M1.world(m, i0, X) @ M1.RS[i0]) @ M1.Q[i0]
    c = padH.mean(0); s_pad = float(c @ ax); ds = float(rp["ds"]); s0 = s_pad + ds
    s_pe = float((padH @ ax).max()) if ds > 0 else float((padH @ ax).min())          # pad edge facing the track
    th0 = math.degrees(math.atan2(float(c @ f), float(c @ e)))
    rpad = float(np.linalg.norm(AA._rad(padH, ax), axis=1).min())
    PHI = abs(float(rp["PHI"])); sg = 1.0 if float(rp.get("sgn", 1)) >= 0 else -1.0
    wlo, whi = (th0 - 18.0, th0 + PHI + 18.0) if sg > 0 else (th0 - PHI - 18.0, th0 + 18.0)
    ths = np.arange(wlo, whi + 1e-9, 2.0); ss = np.arange(s0 - 0.5 * SH_W, s0 + 0.5 * SH_W + 1e-9, 2.0)
    clips = [j for j in range(len(B1.idx)) if B1.kind[j] == "clip"]
    rr = np.arange(10.0, 110.0, 1.0); prof = np.full((len(clips), len(ss), len(ths)), np.nan)
    for a_, j in enumerate(clips):
        R = M1.RS[j] @ M1.Q[j]; pts = []
        for sv in ss:
            for t in ths:
                d = math.cos(t * D2R) * e + math.sin(t * D2R) * f; pts.append((sv * ax)[None] + rr[:, None] * d[None])
        pts = np.concatenate(pts); dd = B1.dist(j, pts @ R.T).reshape(len(ss), len(ths), len(rr)); inside = dd < 0
        for b in range(len(ss)):
            for k in range(len(ths)):
                ins = np.nonzero(inside[b, k])[0]
                if not len(ins): continue
                tail = ~inside[b, k, ins[0]:]
                fo = ins[0] + int(np.argmax(tail)) if tail.any() else len(rr) - 1
                prof[a_, b, k] = rr[fo] - dd[b, k, fo]
    p90 = np.nanpercentile(prof, 90, axis=0)
    # pre-arc floor: carriage half-arc + the stop dowel, at the track radius (iterate: R_t depends on the arc)
    pre = float(rp.get("pre", 10.0)); R_t = 80.0
    for _ in range(3):
        floor = math.degrees((0.5 * CAR_W + DOWEL) / R_t); a = max(pre, floor)
        lo, hi = (th0 - a, th0 + PHI + a) if sg > 0 else (th0 - PHI - a, th0 + a)
        sel = (ths >= lo - 1.0) & (ths <= hi + 1.0)
        R_liner = float(np.nanmax(p90[:, sel])) + 4.0 + float(rp.get("rt_extra", 2.5)); R_t = R_liner + 1.5
    h_c = 1.7
    return dict(e=e, f=f, s0=s0, s_pad=s_pad, s_pe=s_pe, ds=ds, th0=th0, lo=lo, hi=hi, pre=a, pre_floor=floor, ths=ths, ss=ss, p90=p90,
                R_liner=R_liner, R_t=R_t, h_c=h_c, dh=0.0, rpad=rpad, hw="plain", sg=sg, PHI=PHI,
                R_b=R_t + h_c + max(1.0, float(rp.get("bump", 1.0))), clr=max(1.0, float(rp.get("bump", 1.0))), band=max(float(rp.get("band", 10.0)), BAND_FLOOR), ramp_req=float(rp.get("ramp", 10.0)))


def _wcar(h, G, ax, r):
    """ramp weight of the carriage footprint (fixed in the carriage frame HG'): s0 +- (CAR_L/2 + 1), th0 +- (CAR_W/2 + 1) mm"""
    e, f = G["e"], G["f"]; sv = h @ ax; az = np.degrees(np.arctan2(h @ f, h @ e)); azr = (az - G["th0"] + 180.0) % 360.0 - 180.0
    d_az = np.maximum(0.0, np.abs(azr) * D2R * np.maximum(r, 1.0) - (0.5 * CAR_W + 1.0))
    d_s = np.maximum(0.0, np.abs(sv - G["s0"]) - (0.5 * CAR_L + 1.0))
    return np.clip(1.0 - d_s / G["ramp"], 0, 1) * np.clip(1.0 - d_az / G["ramp"], 0, 1)


def _need(h, G, ax):
    """bump needed at HG'-frame points h: ramp weight x max(0, target - r); target = R_t + clr over the shell, + h_c over
    the carriage footprint"""
    w, r = _weights(h, G, ax); tgt = G["R_t"] + G["clr"] + G["h_c"] * _wcar(h, G, ax, r)
    return w * np.maximum(0.0, tgt - r)


def _weights(h, G, ax):
    """ramp weight of HG'-frame points h (n,3) for the bump: 1 inside the station band x the track window seen from the
    carriage at any relay angle, linear to 0 over RAMP mm in s and in arc"""
    e, f = G["e"], G["f"]; sv = h @ ax; r = np.linalg.norm(AA._rad(h, ax), axis=1)
    az = np.degrees(np.arctan2(h @ f, h @ e))
    wlo, whi = (G["lo"] - G["PHI"], G["hi"]) if G["sg"] > 0 else (G["lo"], G["hi"] + G["PHI"])
    mid = 0.5 * (wlo + whi); azr = (az - mid + 180.0) % 360.0 - 180.0 + mid
    d_az = np.maximum(0.0, np.maximum(wlo - azr, azr - whi)) * D2R * np.maximum(r, 1.0)
    d_s = np.maximum(0.0, np.abs(sv - G["s0"]) - G["band"]); RAMP = G["ramp"]
    w = np.clip(1.0 - d_s / RAMP, 0, 1) * np.clip(1.0 - d_az / RAMP, 0, 1)
    return w, r


def bump_amounts(M1, G, ax):
    """rigid bump per sampled point of members 3 / 6: max over the fit-bench kin_ok poses of w x max(0, R_b - r).
    -> {('rigid', name) | ('link', name) | ('contact', k): amounts}"""
    from scipy.spatial import cKDTree
    kin = np.nonzero(M1.kin_ok)[0]; out = {}; Rb = G["R_b"]
    G["ramp"] = max(G["ramp_req"], 12.0 / TAN_MAX + 2.0)                     # first pass at a ~12 mm climb bound; then the floor at the real climb
    sets = [(("rigid", nm), m, X) for nm, (m, X) in M1.rigid.items() if m in BUMP_MEMBERS]
    sets += [(("link", nm), m, X) for nm, (m, X) in M1.link_pts.items() if m in BUMP_MEMBERS]
    for key, m, X in sets:
        amt = np.zeros(len(X))
        for j in kin:
            h = (M1.world(m, j, X) @ M1.RS[j]) @ M1.Q[j]
            amt = np.maximum(amt, _need(h, G, ax))
        out[key] = amt
    climb = max([float(a.max()) for a in out.values()] + [0.0]); rfl = climb / TAN_MAX + 2.0
    if abs(max(G["ramp_req"], rfl) - G["ramp"]) > 0.25:                          # re-run once at the real floor
        G["ramp"] = max(G["ramp_req"], rfl)
        for key, m, X in sets:
            amt = np.zeros(len(X))
            for j in kin:
                h = (M1.world(m, j, X) @ M1.RS[j]) @ M1.Q[j]
                amt = np.maximum(amt, _need(h, G, ax))
            out[key] = amt
    G["ramp_floor"] = rfl
    # contact-only sets: nearest sampled point of the same member (local frame)
    for k, (m, Pc) in enumerate(M1.contact):
        if m not in BUMP_MEMBERS or not len(Pc): continue
        ref = [(X, out[key]) for key, mm, X in sets if mm == m]
        RX = np.concatenate([x for x, _ in ref]); RA = np.concatenate([a for _, a in ref])
        _, nn = cKDTree(RX).query(Pc); out[("contact", k)] = RA[nn]
    return out


def relay_points(G, ax):
    """(shell underside + top, arm-fixed HG frame), (carriage + bracket, carriage frame) ~1 pt / 4 mm2; masks of in-band
    (skin-facing) samples in G['arm_ib'] / G['car_ib']"""
    e, f, s0, Rt = G["e"], G["f"], G["s0"], G["R_t"]; arm = []; aib = []; car = []; cib = []
    dt = 2.0 / Rt / D2R
    for t in np.arange(G["lo"], G["hi"] + 1e-9, dt):
        d = math.cos(t * D2R) * e + math.sin(t * D2R) * f
        for sv in np.arange(s0 - 0.5 * SH_W, s0 + 0.5 * SH_W + 0.01, 2.0):
            arm.append(sv * ax + (Rt - 1.5) * d); aib.append(True)          # shell underside (in band, contact)
            arm.append(sv * ax + Rt * d); aib.append(False)                 # shell top (contact / jam only)
    half = 0.5 * CAR_W / Rt / D2R; tc = G["th0"]
    for t in np.arange(tc - half, tc + half + 1e-9, dt):
        d = math.cos(t * D2R) * e + math.sin(t * D2R) * f
        for sv in np.arange(s0 - 0.5 * CAR_L, s0 + 0.5 * CAR_L + 0.01, 2.0):
            car.append(sv * ax + (Rt + 0.2) * d); cib.append(False); car.append(sv * ax + (Rt + G["h_c"]) * d); cib.append(False)
    # bracket: 2 mm Ti, 10 wide, from the carriage's pad-side edge at the carriage top to the pad's facing edge (underside sampled)
    sg_ = 1.0 if G["s_pad"] > s0 else -1.0; s_a = s0 + sg_ * 0.5 * CAR_L; s_b = G["s_pe"]
    r_a = Rt + G["h_c"]; r_b = G["rpad"]; hb = 5.0 / Rt / D2R
    n_s = max(2, int(math.ceil(abs(s_b - s_a) / 2.0)) + 1)
    for sv in np.linspace(s_a, s_b, n_s):
        r = r_a + (r_b - r_a) * (sv - s_a) / (s_b - s_a) if abs(s_b - s_a) > 1e-9 else r_b
        for t in np.arange(tc - hb, tc + hb + 1e-9, dt):
            d = math.cos(t * D2R) * e + math.sin(t * D2R) * f; car.append(sv * ax + r * d); cib.append(True)
    G["arm_ib"] = np.array(aib, bool); G["car_ib"] = np.array(cib, bool)
    G["bracket_ramp_deg"] = round(math.degrees(math.atan2(abs(r_a - r_b), abs(s_b - s_a))), 1)
    return np.array(arm), np.array(car)


def rerecord(M, B, G, ax, phi_b, HG0, bumps):
    """recompute every evaluated pose's metal: chain metal with the rigid bump + relay hardware; jams -> pose lost
    ('jam'); any metal < 0 (shell included) -> contact"""
    from scipy.spatial import cKDTree
    arm, car = relay_points(G, ax)
    names = list(M.rigid) + list(M.link_pts); kinds = ["rigid"] * len(M.rigid) + ["link"] * len(M.link_pts)
    parts = list(M.rigid.values()) + list(M.link_pts.values())
    why = np.asarray(M.why, dtype=object).copy(); jam = []; ch_ib = []; rel_ib = []

    def bumped(key, m, w, RS, Qp):
        a = bumps.get(key)
        if a is None or not np.any(a > 0): return w
        h = (w @ RS) @ Qp; r = AA._rad(h, ax); n = np.linalg.norm(r, axis=1, keepdims=True); n[n < 1e-9] = 1.0
        h = h + a[:, None] * r / n; return (h @ Qp.T) @ RS.T
    for i in range(len(B.idx)):
        if B.res[i] is None: continue
        RS = M.RS[i]; Qp = M.Q[i]; Q0 = HG0[i]; P = []; per = {}
        for nm, kd, (m, X) in zip(names, kinds, parts):
            w = bumped((kd, nm), m, M.world(m, i, X), RS, Qp); per[nm] = w; P.append(w)
        chain = np.concatenate(P)
        wa = (arm @ Q0.T) @ RS.T; wc = (car @ Qp.T) @ RS.T
        # clearances: shell and carriage are annular sectors about ax -> exact distance in (r, s, arc); the bracket by
        # nearest sample - 1 mm (2 mm sampling)
        def sector(Xw, Qf, r0, r1, sa, sb, ta, tb):
            h = (Xw @ RS) @ Qf; sv = h @ ax; rr = np.linalg.norm(AA._rad(h, ax), axis=1)
            az = np.degrees(np.arctan2(h @ G["f"], h @ G["e"])); mid = 0.5 * (ta + tb); azr = (az - mid + 180.0) % 360.0 - 180.0 + mid
            dr = np.maximum(0.0, np.maximum(rr - r1, r0 - rr)); dss = np.maximum(0.0, np.maximum(sa - sv, sv - sb))
            da = np.maximum(0.0, np.maximum(ta - azr, azr - tb)) * D2R * np.minimum(rr, r1)
            return float(np.sqrt(dr ** 2 + dss ** 2 + da ** 2).min())
        Rt = G["R_t"]; hcar = 0.5 * CAR_W / Rt / D2R
        dpt = {n: sector(per[n], Q0, Rt - 1.5, Rt, G["s0"] - 0.5 * SH_W, G["s0"] + 0.5 * SH_W, G["lo"], G["hi"])
               for n in ("knee", "E", "boss", "hub3", "L2", "pad") if n in per}
        dpc = {n: sector(per[n], Qp, Rt + 0.2, Rt + G["h_c"], G["s0"] - 0.5 * CAR_L, G["s0"] + 0.5 * CAR_L, G["th0"] - hcar, G["th0"] + hcar)
               for n in ("E", "boss", "hub3", "L2") if n in per}
        nb = int((~G["car_ib"]).sum()); wbr = wc[nb:] if len(wc) > nb else None
        if wbr is not None and len(wbr):
            tb_ = cKDTree(wbr)
            for n in ("E", "boss"):
                if n in per: dpc[n] = min(dpc[n], float(tb_.query(per[n])[0].min()) - 1.0)
        dmin, dcar = min(dpt.values()), min(dpc.values())
        dall = B.dist(i, np.r_[chain, wa, wc]); nC = len(chain)
        rib = np.r_[G["arm_ib"], G["car_ib"]]
        d = np.r_[dall[:nC], dall[nC:][rib]]
        dtop = dall[nC:][~rib]; dc = [float(dtop.min())] if len(dtop) else []
        Wc = []
        for k, (m, Pc) in enumerate(M.contact):
            if not len(Pc): continue
            Wc.append(bumped(("contact", k), m, M.world(m, i, Pc), RS, Qp))
        if Wc: dc.append(float(B.dist(i, np.concatenate(Wc)).min()))
        dc = min(dc) if dc else 1e9
        if min(dmin, dcar) < 1.0:
            jam.append(dict(i=i, kind=B.kind[i], pose=[B.poses[i][k] for k in ("plane", "elev", "axial")], track_mm=round(dmin, 2),
                            track_part=min(dpt, key=dpt.get), carriage_mm=round(dcar, 2), carriage_part=min(dpc, key=dpc.get),
                            phi=round(float(phi_b[i]), 1), metal_min_mm=round(min(dc, float(d.min())), 2)))
            if min(dc, float(d.min())) >= 0:                # a jam with metal in the skin stays a CONTACT (never laundered into a lost pose)
                B.res[i] = None; why[i] = "jam"; continue
            B.res[i] = np.r_[d, dc] if dc < 0 else d; why[i] = "contact"; continue
        B.res[i] = np.r_[d, dc] if dc < 0 else d
        if min(dc, float(d.min())) < 0: why[i] = "contact"
        elif why[i] == "contact": why[i] = ""
        if B.kind[i] == "clip" and min(dc, float(d.min())) >= 0:
            ch_ib.append(d[:nC]); rel_ib.append(d[nC:])
    M.why = why
    ib = lambda a: round(float(((a >= 2) & (a <= 14)).mean()), 4) if len(a) else None
    lc = np.concatenate(ch_ib) if ch_ib else np.zeros(0); rc = np.concatenate(rel_ib) if rel_ib else np.zeros(0)
    nb = {f"{k[0]}:{k[1]}": int((v > 0).sum()) for k, v in bumps.items() if np.any(v > 0)}
    return dict(jams=jam, ib14_chain_only=ib(lc), ib14_relay_metal=ib(rc), n_relay_pts=int(len(arm) + len(car)),
                n_relay_ib_pts=int(G["arm_ib"].sum() + G["car_ib"].sum()), relay_median_mm=round(float(np.median(rc)), 2) if len(rc) else None,
                chain_median_mm=round(float(np.median(lc)), 2) if len(lc) else None,
                bumped_points=nb, bump_max_mm=round(max(float(v.max()) for v in bumps.values()), 2) if bumps else 0.0,
                bracket_ramp_deg=G.get("bracket_ramp_deg"))


def _flood_cached(M1, rp):
    """the armarc continuity flood (kinematic: depends on PHI / axis / sense only), cached in the verify dir"""
    os.makedirs(VDIR, exist_ok=True)
    key = f"flood_PHI{float(rp['PHI']):g}_t{float(rp['tilt']):g}_a{float(rp['taz']):g}_s{int(np.sign(float(rp.get('sgn', 1))))}.json"
    path = os.path.join(VDIR, key)
    if os.path.exists(path):
        d = json.load(open(path)); return {int(k): bool(v) for k, v in d["conn"].items()}, d["stats"]
    cmap, _, st = AA.flood_relay(M1, rp)
    json.dump(dict(conn={str(k): v for k, v in cmap.items()}, stats=st, rp={k: rp[k] for k in ("PHI", "tilt", "taz", "sgn")}), open(path, "w"))
    return cmap, st


def prepare(base, nc=60, nw=160, exact=False):
    """one lead fit (Bench(60,160) fast, phi 0, frozen) + relay solve + frozen wear on Bench(nc, nw) with the relayed
    arm frames (ideal relay, no hardware); returns a state the hardware configs are re-recorded on"""
    rp = dict(DEF); rp.update({k: base[k] for k in DEF if k in base})
    P = CC._clamp(dict(CC.PARAMS, **AA.LEAD, **{k: v for k, v in base.items() if k not in DEF}))
    old = os.environ.pop("CB_EXACT", None)
    try:
        B1 = CB.Bench(n_clip=60, n_ws=160); M1 = CC.CCModel(B1, dict(P)); r1 = M1.run()
        fit = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
        ax = AA.raxis(rp["tilt"], rp["taz"])
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]
    phi, ax = AA.solve_phi(M1, rp); phi_fill = np.where(np.isfinite(phi), phi, 0.0); Zr = AA.relayed_Z(phi_fill, ax)

    class Frozen(CC.CCModel):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info", "_wedge_info", "cyl_r"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self._sc = None; self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]
            self.drop = np.zeros(len(self.poses_fit), bool); self._truncate()
    if exact: os.environ["CB_EXACT"] = "1"
    if nc == -2:                                            # the pick-selection bench (tools/env_bench.py envsel; exact, never the claim bench)
        import env_bench as EB; B = EB.bench("envsel", exact=True)
        if int(rp.get("flood", 1)): rp["flood"] = 0          # envsel poses are off the flood's envelope grid: static reading
    else:
        B = AA.held_bench() if nc == -1 else CB.Bench(n_clip=nc, n_ws=nw)
    phi_b = phi_fill[B.idx]
    with AA.patched(Zr):
        M = Frozen(B, P2); r = M.run()
    ideal = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    cmap, fst = (_flood_cached(M1, rp) if int(rp.get("flood", 1)) and float(rp["PHI"]) > 0 else (None, None))
    return dict(rp=rp, M1=M1, B1=B1, M=M, B=B, ax=ax, phi_b=phi_b, fit=fit, ideal=ideal, cmap=cmap, flood=fst,
                res0=[None if x is None else np.array(x) for x in B.res], why0=np.asarray(M.why, dtype=object).copy(), nc=nc, nw=nw)


def wear(S, hw):
    """re-record the prepared wear with hardware config hw (dict of relay params overriding the base) -> result dict"""
    t0 = time.time(); M, B = S["M"], S["B"]
    B.res = [None if x is None else np.array(x) for x in S["res0"]]; M.why = S["why0"].copy()
    rp = dict(S["rp"]); rp.update({k: hw[k] for k in hw if k in DEF})
    if any(rp[k] != S["rp"][k] for k in ("PHI", "tilt", "taz", "sgn")): raise ValueError("PHI / axis changes need a new prepare()")
    ax = S["ax"]; phi_b = S["phi_b"]
    G = geometry(S["M1"], S["B1"], ax, rp); bumps = bump_amounts(S["M1"], G, ax)
    hwrep = rerecord(M, B, G, ax, phi_b, AA.Z0["HG"][B.idx].astype(float), bumps)
    rr_ = B.report(); rep = {k: rr_[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    conn = None; ws = np.array(B.kind) == "ws"
    if S["cmap"] is not None:
        tk = [j for j in range(len(B.idx)) if B.res[j] is not None and float(np.min(B.res[j])) >= 0]
        drop = [j for j in tk if ws[j] and phi_b[j] != 0 and not S["cmap"].get(int(B.idx[j]), False)]
        drop0 = [j for j in tk if ws[j] and phi_b[j] == 0 and not S["cmap"].get(int(B.idx[j]), False)]
        static = dict(rep)
        for j in drop: B.res[j] = None
        rr_ = B.report(); rep = {k: rr_[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
        conn = dict(static=static, dropped_relayed=len(drop), phi0_taken_not_connected=len(drop0),
                    dropped=[[B.poses[j][k] for k in ("plane", "elev", "axial")] + [round(float(phi_b[j]), 1)] for j in drop], flood=S["flood"])
    mins = np.array([float(np.min(B.res[j])) if B.res[j] is not None else np.nan for j in range(len(B.idx))])
    elev = np.array([p["elev"] for p in B.poses]); taken = np.isfinite(mins) & (mins >= 0); rel = phi_b != 0
    why = np.asarray(M.why)
    cl = [j for j, k in enumerate(B.kind) if k == "clip"]; wsl = [j for j, k in enumerate(B.kind) if k == "ws"]
    nz = [j for j in range(len(B.kind)) if B.res[j] is not None]

    def near(t):
        okt = lambda j: B.res[j] is not None and float(np.min(B.res[j])) >= t
        return CB.gap_of(rep["inband14"], float(np.mean([okt(j) for j in cl])), float(np.mean([okt(j) for j in wsl])),
                         float(np.mean([float(np.min(B.res[j])) < t for j in nz])) if nz else 0.0)
    cl = [j for j, k in enumerate(B.kind) if k == "clip"]; wsl = [j for j, k in enumerate(B.kind) if k == "ws"]
    nz = [j for j in range(len(B.kind)) if B.res[j] is not None]
    ib_lo = min(rep["inband14"], hwrep["ib14_chain_only"]) if hwrep["ib14_chain_only"] is not None else rep["inband14"]
    gate_gap = CB.gap_of(ib_lo, rep["follow"], rep["reach"], rep["contact"])
    okt1 = lambda j: B.res[j] is not None and float(np.min(B.res[j])) >= 1.0
    obj = CB.gap_of(ib_lo, float(np.mean([okt1(j) for j in cl])), float(np.mean([okt1(j) for j in wsl])),
                    float(np.mean([float(np.min(B.res[j])) < 1.0 for j in nz])) if nz else 0.0)   # search objective: near-touch on the gate in-band
    out = dict(params=dict(rp), bench=[S["nc"], S["nw"]], mode=B.mode, wear=rep, gate_gap=gate_gap, ib14_gate=ib_lo, obj_near1_gate=obj,
               chain_only_gap=CB.gap_of(hwrep["ib14_chain_only"] or 0.0, rep["follow"], rep["reach"], rep["contact"]),
               near1_gap=near(1.0), near2_gap=near(2.0), fit_fast=S["fit"], wear_ideal_relay=S["ideal"],
               ws_taken=int((ws & taken).sum()), ws=int(ws.sum()), overhead=[int((ws & taken & (elev >= 140)).sum()), int((ws & (elev >= 140)).sum())],
               overhead_ib14=None,
               relayed=dict(n=int((rel & ws).sum()), taken=int((rel & ws & taken).sum()), contact=int((rel & np.isfinite(mins) & (mins < 0)).sum()),
                            jam=int((rel & (why == "jam")).sum()), clip_relayed=int((rel & ~ws).sum()),
                            phi_max=round(float(np.abs(phi_b).max()), 2) if rel.any() else 0.0),
               why={str(k): int((why == k).sum()) for k in set(why.tolist())},
               min_metal_taken=round(float(np.nanmin(np.where(taken, mins, np.nan))), 3) if taken.any() else None,
               hw=hwrep, continuity=conn,
               relay_hw=dict(R_t=round(G["R_t"], 2), R_liner=round(G["R_liner"], 2), R_bump=round(G["R_b"], 2), h_c=G["h_c"], rpad=round(G["rpad"], 2),
                             s0=round(G["s0"], 1), s_pad=round(G["s_pad"], 1), s_pad_edge=round(G["s_pe"], 1), th0=round(G["th0"], 1),
                             arc=[round(G["lo"], 1), round(G["hi"], 1)], pre_arc=round(G["pre"], 2), pre_floor=round(G["pre_floor"], 2), band=G["band"], ramp=round(G["ramp"], 2), ramp_floor=round(G["ramp_floor"], 2),
                             skin_p90_arc_max=round(G["R_liner"] - 4.0 - float(rp.get("rt_extra", 2.5)), 2)),
               contacts=[dict(i=int(j), kind=B.kind[j], pose=[B.poses[j][k] for k in ("plane", "elev", "axial")], phi=round(float(phi_b[j]), 1),
                              min_mm=round(float(mins[j]), 2)) for j in range(len(B.idx)) if np.isfinite(mins[j]) and mins[j] < 0],
               relayed_poses=[dict(i=int(j), pose=[B.poses[j][k] for k in ("plane", "elev", "axial")], phi=round(float(phi_b[j]), 1), why=str(why[j]),
                                   min_mm=(round(float(mins[j]), 2) if np.isfinite(mins[j]) else None)) for j in range(len(B.idx)) if ws[j] and rel[j]],
               secs=round(time.time() - t0, 1))
    return out


def perpose(S):
    """T5 per-pose dump of the current wear (tools/alignment_paired.py format)"""
    import alignment_paired as AP
    poses = AP._dump_bench(S["M"], S["B"]); return dict(id=ID, poses=poses, report=S["B"].report(), recomputed=AP.gap_parts(poses))


def evaluate(params, nc=60, nw=160, exact=False):
    S = prepare(params, nc, nw, exact); return wear(S, params), S


def bench_eval(B, params):
    out, _ = evaluate(params); r = dict(out["wear"]); r.update(near1=out["near1_gap"], gate_gap=out["gate_gap"]); return r


def _short(o):
    return {k: v for k, v in o.items() if k not in ("relayed_poses", "contacts")}


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "gravity":
        print(json.dumps(AA.gravity_check(par))); sys.exit(0)
    if mode == "hwsweep":                                  # hwsweep base hwlist [nc nw exact] [out.json]
        hwl = json.loads(sys.argv[3]); nc = int(sys.argv[4]) if len(sys.argv) > 4 else 60; nw = int(sys.argv[5]) if len(sys.argv) > 5 else 160
        outp = sys.argv[6] if len(sys.argv) > 6 else None
        S = prepare(par, nc, nw, exact=os.environ.get("CB_EXACT") == "1"); res = []
        for hw in hwl:
            o = wear(S, dict(par, **hw)); o["hw_override"] = hw; res.append(o)
            print(json.dumps(dict(hw=hw, gap=o["wear"]["gap"], gate=o["gate_gap"], obj=o["obj_near1_gate"], near1=o["near1_gap"], ib=o["wear"]["inband14"],
                                  ibc=o["hw"]["ib14_chain_only"], reach=o["wear"]["reach"], fol=o["wear"]["follow"], con=o["wear"]["contact"],
                                  jams=len(o["hw"]["jams"]), secs=o["secs"])), flush=True)
            if outp:
                json.dump(res, open(outp, "w"), default=float)
                pp = perpose(S); pp.update(wear=f"bench({nc},{nw})", params=dict(par, **hw), exact=os.environ.get("CB_EXACT") == "1")
                json.dump(pp, open(outp.replace(".json", f"_{len(res) - 1}_perpose.json"), "w"), default=float)
        sys.exit(0)
    if mode == "frozen": out, S = evaluate(par, 110, 360, exact=True)
    elif mode == "held": out, S = evaluate(par, -1, -1, exact=True)
    else: out, S = evaluate(par)
    out["row"] = ID
    if len(sys.argv) > 3:
        json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        if mode in ("frozen", "held"):
            pp = perpose(S); pp.update(wear="bench" if mode == "frozen" else "held", params=par, exact=True)
            json.dump(pp, open(sys.argv[3].replace(".json", "_perpose.json"), "w"), default=float)
    print(json.dumps(_short(out), default=float))
