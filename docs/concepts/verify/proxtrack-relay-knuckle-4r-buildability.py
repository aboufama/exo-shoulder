"""Independent verifier, lens BUILDABILITY AND RED TEAM, for proxtrack-relay-knuckle-4r (claim: frozen exact
Bench(110,360) gate 14.40 / plain 14.02 at PHI 35, ds 19.538, rt_extra 1.5, pre 10.41, bump 1.002, band 9.272, ramp 6.0).

The claim model is imported unchanged (docs/concepts/models/proxtrack-relay-knuckle-4r.py); each pricing variant patches
ONE thing and re-records the same prepared wear (one fit, one relay solve, one frozen claim-bench run):

  base    the claim as modelled (reproduction)
  rigid1  the 'rigid bump' made rigid: the claim's bumped point moves RADIALLY ABOUT a_r AT EVERY POSE (a per-pose
          direction = a deforming part); here each point gets ONE displacement vector fixed in its member's frame, along
          the radial direction at the fit pose that set its amount, same amounts
  rigid2  rigid1 with the amounts re-sized so the fixed vector still meets the claim's clearance target at every fit
          pose (a = max_j need_j / cos(angle between the fixed vector and pose j's radial), cos floored at 0.3)
  flange  base + the T-nut's retaining flange under the shell (1 mm Ti, 8 wide key, carriage length, skin-facing metal,
          the armarc family's own 'flange' sampling, dropped by this model)
  coil    (diagnostic, base metal) the constant-force spring's coil as an arm-fixed cylinder beyond the zero dowel: chain
          metal within 1 mm of it = jam

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/proxtrack-relay-knuckle-4r-buildability.py price base,rigid2 out.json
    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/proxtrack-relay-knuckle-4r-buildability.py diag out.json
"""
import importlib.util, inspect, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
_sp = importlib.util.spec_from_file_location("proxtrack_for_build_v", os.path.join(REPO, "docs", "concepts", "models", "proxtrack-relay-knuckle-4r.py"))
PT = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(PT)
AA, CB, CC = PT.AA, PT.CB, PT.CC
D2R = math.pi / 180
CLAIM = dict(PHI=35.0, ds=19.538, rt_extra=1.5, pre=10.41, bump=1.002, band=9.272, ramp=6.0, tilt=12, taz=235, sgn=1, flood=1, hw=1, hwv="plain")
OUT = {}

_ORIG = dict(bump_amounts=PT.bump_amounts, rerecord=PT.rerecord, relay_points=PT.relay_points)

# --- the rigid-bump rerecord: the same source with bumped() reading member-frame displaced points ----------------------
_src = inspect.getsource(_ORIG["rerecord"])
_old = """        a = bumps.get(key)
        if a is None or not np.any(a > 0): return w
        h = (w @ RS) @ Qp; r = AA._rad(h, ax); n = np.linalg.norm(r, axis=1, keepdims=True); n[n < 1e-9] = 1.0
        h = h + a[:, None] * r / n; return (h @ Qp.T) @ RS.T"""
_new = """        xv = XV.get(key)
        if xv is None: return w
        return M.world(m, i, xv)"""
assert _old in _src, "rerecord source changed"
_ns = dict(PT.__dict__); _ns["XV"] = {}
exec(compile(_src.replace(_old, _new).replace("def rerecord(", "def rerecord_rigid("), "rerecord_rigid", "exec"), _ns)
rerecord_rigid = _ns["rerecord_rigid"]


def _sets(M1):
    s = [(("rigid", nm), m, X) for nm, (m, X) in M1.rigid.items() if m in PT.BUMP_MEMBERS]
    s += [(("link", nm), m, X) for nm, (m, X) in M1.link_pts.items() if m in PT.BUMP_MEMBERS]
    return s


def rigid_vectors(M1, G, ax, amts, resize):
    """member-frame displacement per bumped point; returns XV (key -> X + V) and the direction-spread statistics"""
    from scipy.spatial import cKDTree
    kin = np.nonzero(M1.kin_ok)[0]; XV = {}; Vs = {}; spread = []; grow = []
    for key, m, X in _sets(M1):
        a = amts.get(key)
        if a is None or not np.any(a > 0): Vs[key] = np.zeros_like(X); continue
        best = np.zeros(len(X)); U = np.zeros((len(X), 3)); rec = []
        for j in kin:
            w = M1.world(m, j, X); RS, Q = M1.RS[j], M1.Q[j]; h = (w @ RS) @ Q
            nd = PT._need(h, G, ax); rad = AA._rad(h, ax); rh = rad / np.maximum(np.linalg.norm(rad, axis=1, keepdims=True), 1e-9)
            rw = (rh @ Q.T) @ RS.T; A = M1.world(m, j, np.eye(3)) - M1.world(m, j, np.zeros((1, 3))); ul = rw @ A.T
            ul /= np.maximum(np.linalg.norm(ul, axis=1, keepdims=True), 1e-9)
            up = nd > best; best[up] = nd[up]; U[up] = ul[up]; rec.append((nd, ul))
        aa = np.array(a, float); sel = aa > 0
        if resize:
            req = aa.copy()
            for nd, ul in rec:
                c = np.maximum((U * ul).sum(1), 0.3); req = np.maximum(req, np.where(nd > 0, nd / c, 0.0))
            grow.append(float((req - aa)[sel].max())); aa = req
        spr = np.zeros(len(X))
        for nd, ul in rec:                                    # angle between the fixed vector and the radial at poses that need lift
            c = np.clip((U * ul).sum(1), -1, 1); ang = np.degrees(np.arccos(c)); spr = np.maximum(spr, np.where(sel & (nd > 0), ang, 0.0))
        spread.append(spr)
        V = aa[:, None] * U; Vs[key] = V; XV[key] = X + V
        OUT.setdefault("amount_check", {})[f"{key[0]}:{key[1]}"] = dict(n_bumped=int(sel.sum()), max_amt=round(float(aa.max()), 2),
                                                                       best_vs_claim_max_diff=round(float(np.abs(best - np.asarray(a))[sel].max()), 3))
    for k, (m, Pc) in enumerate(M1.contact):
        if m not in PT.BUMP_MEMBERS or not len(Pc): continue
        ref = [(X, Vs[key]) for key, mm, X in _sets(M1) if mm == m]
        RX = np.concatenate([x for x, _ in ref]); RV = np.concatenate([v for _, v in ref])
        _, nn = cKDTree(RX).query(Pc); XV[("contact", k)] = Pc + RV[nn]
    sp = np.concatenate(spread) if spread else np.zeros(1)
    return XV, dict(dir_spread_deg_max=round(float(np.max(sp)), 2), dir_spread_deg_p90=round(float(np.percentile(sp[sp > 0], 90)), 2) if (sp > 0).any() else 0.0,
                    resize_growth_mm=round(max(grow), 2) if grow else 0.0)


def flange_points(orig):
    def rp(G, ax):
        arm, car = orig(G, ax); e, f, s0, Rt = G["e"], G["f"], G["s0"], G["R_t"]; half = 0.5 * PT.CAR_W / Rt / D2R; tc = G["th0"]; add = []
        for t in np.arange(tc - half, tc + half + 1e-9, 2.0 / Rt / D2R):
            d = math.cos(t * D2R) * e + math.sin(t * D2R) * f
            for sv in np.arange(s0 - 4.0, s0 + 4.0 + 0.01, 2.0): add.append(sv * ax + (Rt - 1.5 - 1.0) * d)
        G["car_ib"] = np.r_[G["car_ib"], np.ones(len(add), bool)]; G["flange_pts"] = len(add)
        return arm, np.r_[car, np.array(add)]
    return rp


def coil_check(S, G, bumps, D=8.0, L=7.0):
    """constant-force spring coil (OD D, width L) arm-fixed beyond the zero dowel: cylinder axis along a_r direction?
    No - a constant-force strip coils about an axis across the strip, i.e. along s (a_r): centre at radius R_t + D/2,
    azimuth lo - (D/2 + 1) / R_t. Chain metal (claim's radial bump) within 1 mm of the coil surface = jam."""
    M, B, ax = S["M"], S["B"], S["ax"]; e, f = G["e"], G["f"]; Rt = G["R_t"]; HG0 = AA.Z0["HG"][B.idx].astype(float)
    tc = (G["lo"] - math.degrees((0.5 * D + 1.0) / Rt)) if G["sg"] > 0 else (G["hi"] + math.degrees((0.5 * D + 1.0) / Rt))
    cdir = math.cos(tc * D2R) * e + math.sin(tc * D2R) * f; cen = (Rt + 0.5 * D) * cdir
    rows = []
    for i in range(len(B.idx)):
        if B.res[i] is None or float(np.min(B.res[i])) < 0: continue
        RS, Qp, Q0 = M.RS[i], M.Q[i], HG0[i]; best = 1e9; who = None
        for nm, (m, X) in list(M.rigid.items()) + list(M.link_pts.items()):
            if m not in (2, 3, 6) and nm not in ("hub3", "L2"): continue
            w = M.world(m, i, X); a = bumps.get(("rigid", nm), bumps.get(("link", nm)))
            h = (w @ RS) @ Qp
            if a is not None and np.any(a > 0):
                r = AA._rad(h, ax); n = np.linalg.norm(r, axis=1, keepdims=True); n[n < 1e-9] = 1.0; h = h + a[:, None] * r / n
            h0 = ((h @ Qp.T) @ RS.T @ RS) @ Q0                  # -> arm-fixed HG frame
            rel = h0 - cen; sv = rel @ ax; rr = np.linalg.norm(rel - sv[:, None] * ax[None], axis=1)
            dd = np.sqrt(np.maximum(0, rr - 0.5 * D) ** 2 + np.maximum(0, np.abs(sv) - 0.5 * L) ** 2)
            if float(dd.min()) < best: best = float(dd.min()); who = nm
        rows.append((best, i, who))
    jam = [r for r in rows if r[0] < 1.0]
    return dict(D=D, L=L, coil_az=round(tc, 1), n_taken=len(rows), jams=len(jam), jams_ws=sum(1 for r in jam if B.kind[r[1]] == "ws"),
                closest=[dict(mm=round(r[0], 2), i=r[1], part=r[2], kind=B.kind[r[1]], pose=[B.poses[r[1]][k] for k in ("plane", "elev", "axial")]) for r in sorted(rows)[:8]])


def stackfix_amounts(M1, G, ax):
    """the claim's bump with the pin-a stack kept buildable: the knee link rides ABOVE the boss on pin a (lead: 0.5 mm
    over the boss top at every pose); the claim lifts the boss 1.8-5.7 mm and the knee eye less (stack overlap 5.1 mm at
    all 184 fit poses, -stack.py). Here every knee-link point within the boss radius + 0.5 of pin a's axis is lifted by at
    least the boss's max lift, ramped to 0 at a 60-deg climb beyond the eye (machined plate); contact sets re-derived."""
    from scipy.spatial import cKDTree
    out = _ORIG["bump_amounts"](M1, G, ax)
    mb, Xb = M1.rigid["boss"]; mk, Xk = M1.rigid["knee"]; A0 = M1.fr["A0"]; sn = np.asarray(M1.D.sn, float)
    ab = out.get(("rigid", "boss")); ak = out.get(("rigid", "knee"))
    if ab is None or ak is None: return out
    R_boss = float(np.max(np.linalg.norm((Xb - A0) - ((Xb - A0) @ sn)[:, None] * sn[None], axis=1)))
    j = int(np.nonzero(M1.kin_ok)[0][0]); c = M1.world(mb, j, A0[None])[0]; u = M1.world(mb, j, (A0 + sn)[None])[0] - c; u /= np.linalg.norm(u)
    wk = M1.world(mk, j, Xk); hk = (wk - c) @ u; rk = np.linalg.norm((wk - c) - hk[:, None] * u[None], axis=1)
    lift = float(ab.max()); need = np.maximum(0.0, lift - np.maximum(0.0, rk - R_boss - 0.5) * PT.TAN_MAX)
    out[("rigid", "knee")] = np.maximum(ak, need); OUT["stackfix"] = dict(boss_lift_max=round(lift, 2), knee_pts_raised=int((need > ak).sum()), knee_pts=len(ak))
    sets = _sets(M1)
    for k, (m, Pc) in enumerate(M1.contact):
        if m != mk or not len(Pc): continue
        ref = [(X, out[key]) for key, mm, X in sets if mm == m]
        RX = np.concatenate([x for x, _ in ref]); RA = np.concatenate([a for _, a in ref])
        _, nn = cKDTree(RX).query(Pc); out[("contact", k)] = RA[nn]
    return out


def _dm(th, a, b): return min(th - abs(a - b), min(a + b, 360 - a - b) - th)


def _ang(a, b): return float(np.degrees(np.arccos(np.clip(float(np.dot(a / np.linalg.norm(a), b / np.linalg.norm(b))), -1, 1))))


def th_margin(M, B):
    D = M.D; u1, u2, u3 = D.u; uK = D.uK
    a1 = math.degrees(D.a1) if D.a1 < 4 else D.a1; a2 = math.degrees(D.a2) if D.a2 < 4 else D.a2; rows = []
    for i in range(len(B.idx)):
        if B.res[i] is None or float(np.min(B.res[i])) < 0: continue
        R1, _ = M.T(1, i); R1b, _ = M.T(7, i); R2, _ = M.T(2, i)
        jK = R1 @ uK; j2 = R1b @ u2; j3 = R2 @ u3
        th = _ang(u1, j3); a1e = _ang(u1, j2); a2e = _ang(j2, j3); b1 = _ang(u1, jK); c = _ang(jK, j3)
        forced = abs(float(M.dK[i])) > 1e-6
        own = min(_dm(th, b1, c), _dm(th, a1e, a2e)) if forced else _dm(th, a1, a2)
        rows.append((own, i))
    own = [r[0] for r in rows]
    return dict(min=round(min(own), 3), n=len(rows), lt5=int(sum(1 for x in own if x < 5 - 1e-6)),
                lowest=[dict(own=round(r[0], 3), i=r[1], pose=[B.poses[r[1]][k] for k in ("plane", "elev", "axial")]) for r in sorted(rows)[:5]])


def price(variants, outp):
    t0 = time.time(); S = PT.prepare(CLAIM, 110, 360, exact=True); OUT["prepare_secs"] = round(time.time() - t0, 1); res = {}
    for v in variants:
        PT.bump_amounts, PT.rerecord, PT.relay_points = _ORIG["bump_amounts"], _ORIG["rerecord"], _ORIG["relay_points"]
        if v.startswith("rigid"):
            rz = v == "rigid2"
            def ba(M1, G, ax, rz=rz):
                a = _ORIG["bump_amounts"](M1, G, ax); XV, st = rigid_vectors(M1, G, ax, a, rz); _ns["XV"].clear(); _ns["XV"].update(XV)
                OUT[f"{v}_dir"] = st; return a
            PT.bump_amounts = ba; PT.rerecord = rerecord_rigid
        if v == "flange": PT.relay_points = flange_points(_ORIG["relay_points"])
        if v == "stackfix": PT.bump_amounts = stackfix_amounts
        o = PT.wear(S, CLAIM)
        keep = {k: o[k] for k in ("wear", "gate_gap", "ib14_gate", "near1_gap", "near2_gap", "ws_taken", "overhead", "relayed", "why", "min_metal_taken", "secs")}
        keep["jams"] = len(o["hw"]["jams"]); keep["ib14_chain_only"] = o["hw"]["ib14_chain_only"]; keep["bump_max_mm"] = o["hw"]["bump_max_mm"]
        keep["contacts"] = o["contacts"]; keep["jam_list"] = o["hw"]["jams"]; keep["continuity_dropped"] = (o["continuity"] or {}).get("dropped_relayed")
        if v == "base":
            try: keep["th_margin"] = th_margin(S["M"], S["B"])
            except Exception as ex: keep["th_margin"] = dict(err=repr(ex)[:200])
            try:
                G = PT.geometry(S["M1"], S["B1"], S["ax"], dict(S["rp"], **{k: CLAIM[k] for k in CLAIM if k in PT.DEF}))
                bumps = PT.bump_amounts(S["M1"], G, S["ax"])
                keep["coil8"] = coil_check(S, G, bumps, 8.0); keep["coil5"] = coil_check(S, G, bumps, 5.0)
            except Exception as ex: keep["coil8"] = dict(err=repr(ex)[:200])
        res[v] = keep
        print(json.dumps({v: {k: keep[k] for k in ("wear", "gate_gap", "ib14_chain_only", "near1_gap", "jams", "secs")}}, default=float), flush=True)
        OUT["variants"] = res; json.dump(OUT, open(outp, "w"), indent=1, default=float)


def diag(outp):
    """fit-bench + claim-bench kinematics only: the relay's feasible phi set per pose (one interval = one state)"""
    os.environ.pop("CB_EXACT", None)
    P = CC._clamp(dict(CC.PARAMS, **AA.LEAD)); B1 = CB.Bench(n_clip=60, n_ws=160); M1 = CC.CCModel(B1, dict(P)); M1.run()
    rp = dict(PT.DEF); rp.update(CLAIM); ax = AA.raxis(rp["tilt"], rp["taz"]); Bc = CB.Bench(n_clip=110, n_ws=360)
    out = {}
    for tag, idx, kinds in (("claim", np.asarray(Bc.idx), list(Bc.kind)), ("fit", np.asarray(B1.idx), list(B1.kind))):
        HG = AA.Z0["HG"][idx].astype(float); grid = np.arange(0.0, rp["PHI"] + 1e-9, 0.25)
        F = np.stack([AA.gate(M1, HG @ AA.rotm(ax, np.full(len(HG), g * D2R))) for g in grid], 1)    # (n, len(grid))
        rows = []
        for n in range(len(HG)):
            f = F[n]
            if not f.any(): continue
            comps = int(f[0]) + int(np.sum(f[1:] & ~f[:-1]))
            first = float(grid[np.argmax(f)])
            if comps > 1:
                st = np.nonzero(f[1:] & ~f[:-1])[0] + 1
                rows.append(dict(i=int(n), kind=kinds[n], least=first, comps=comps, comp_starts=[float(grid[s]) for s in st], feasible_frac=round(float(f.mean()), 3),
                                 pose=[float(x) for x in AA.Z0["POSE"][idx[n], :3]]))
        out[tag] = dict(n=len(HG), closable=int(F.any(1).sum()), phi0=int(F[:, 0].sum()), multi_component=len(rows),
                        multi_ws=sum(1 for r in rows if r["kind"] == "ws"), multi_with_phi0=sum(1 for r in rows if r["least"] == 0.0), rows=rows[:60])
        print(tag, json.dumps({k: v for k, v in out[tag].items() if k != "rows"}), flush=True)
    json.dump(out, open(outp, "w"), indent=1, default=float)


if __name__ == "__main__":
    if sys.argv[1] == "price": price(sys.argv[2].split(","), sys.argv[3])
    else: diag(sys.argv[2])
