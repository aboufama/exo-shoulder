"""lead-relay-wobble-4r (round 103, lens 1 'J0 inside J1's footprint', 4 counted joints): the verified lead
conecut-knee-knuckle-3r UNCHANGED from J1 to the cuff (SN_CELL=lead, row best_params, frozen shape fitted on Bench(60,160)
fast), with a fourth O20 v5 hub (hub 0, J0) STACKED UNDER hub 1 on the acromion top, its axis c through GH tilted a0 from
u1 at azimuth azu; hub 1 rides on hub 0's output through a Ti wedge plate of angle a0, so J1's axis wobbles on a cone of
half-angle a0 about c as J0 turns.

Honest metal (what the spec draws, plus what it has to be to build):
  hub 0   a GROUNDED O20 x 12.25 cylinder on c (axisymmetric about c, so it is the same body at every q0). Its underside
          rides at r0 = the lowest radius >= 38 mm that clears the skin by 2 mm on every FIT-bench pose (derived, never free):
          it takes hub 1's old place on the skin. 80 skin-facing underside samples (disc 2 mm pitch), wall + crown samples
          for skin contact. Its ground path (a skin-level bracket from its lower plate to the handler) is NOT modelled:
          generous to the design.
  wedge   Ti plate on hub 0's crown, >= 1.5 mm thick at its thin edge (WEDGE_MIN); hub 1's lower plate sits on it.
  hub 1   LIFTED along u1 by h = the least lift at which its lower plate clears hub 0's crown plane by WEDGE_MIN over the two
          discs' overlap (12.25 + 1.5 + tilt). Samples of hub 1's underside that hub 0's crown disc covers are dropped (not
          skin-facing); the exposed crescent counts.
  L1a     the lead's L1a (member 1). In the lead L1a leaves hub 1's LOWER plate; in the stack the lower plate is the relayed
          body (it sits on the wedge) so L1a must ride hub 1's UPPER member (the boss, as the kit's flip3: underside F + 7.25).
          L1a's 8 samples lift by h + FLIP. It then drops to hub K's lower plate (fK) as a 3 mm RISER wall at hub 1's rim,
          5-axis machined from solid (the 60-deg ramp rule cannot fit in the 5 mm between hub 1's rim and hub K's).
          The riser is member 1 metal: checked against hub 0 (1 mm) and the skin.
  checks  per pose: the lead's own collide (unchanged), hub 0 vs every chain sample except hub 1 / L1a (1 mm), the riser
          vs hub 0 (1 mm), the lifted hub 1 vs every non-adjacent chain sample (1 mm). A part clash loses the pose; metal
          in the skin is a contact.

Relay (policy (ii), the sibling lead-relay-j0-4r's composition): q0 = 0 wherever the lead closes, else the least |q0| in the
stop window [lo, hi] at which the chain closes (lead IK, knee window, closure, J3 stop, |dK| <= dK_lim, J0-J1-J3 sub-chain
>= 5 deg from its fold). Window chosen on the FIT bench, claimed frozen on exact Bench(110,360).

DOF: 4 counted joints (J0 spring-centred + J1 J2 J3 active; the user prefers 3), K slaved, knee pins outside the count,
0 passive translations, no gears / pulleys / cables.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/lead-relay-wobble-4r.py census [sweep.json]   # q0 = 0 metal price per seat, fit bench
    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/lead-relay-wobble-4r.py relay a0 azu [sweep.json]  # fit-bench window (REAL + GHOST)
    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/lead-relay-wobble-4r.py claim a0 azu lo hi [out.json]
"""
import datetime, importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
_sp = importlib.util.spec_from_file_location("lrj0_for_wobble", os.path.join(HERE, "lead-relay-j0-4r.py"))
L = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(L)
CB = L.CB
import concept_kit as CK                                      # noqa: E402

ID = "lead-relay-wobble-4r"
HUB_R, HUB_H = L.HUB_R, L.HUB_H
WEDGE_MIN, FLIP, RISER_T = 1.5, 7.25, 3.0
SKIN_CLR, PART_CLR = 2.0, 1.0


def now(): return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def geometry(M1, a0, azu, r0_set=None):
    """hub 0 / wedge / lifted hub 1 / L1a + riser for seat (a0, azu); r0 from the FIT bench skin only (2 mm on every pose the
    lead takes), or r0_set (a design variable: hub 0 kept low, its skin hits counted as contacts)"""
    B1 = M1.B; u1 = M1.D.u[0]; c = L.relay_axis(u1, a0, azu); e, f = L.frame_of(c)
    if not bool(L.seat_ok(c)[0]): raise RuntimeError("seat-illegal: hub 0's axis (the grounded base hub) is outside the J1 seat rule")
    dxy = CK.disc_xy(HUB_R, 2.0); ang = np.linspace(0, 2 * np.pi, 24, endpoint=False)
    rim = np.array([r * (math.cos(a) * e + math.sin(a) * f) for r in (5.0, 10.0) for a in ang] + [np.zeros(3)])
    tk = [i for i in range(len(B1.idx)) if B1.res[i] is not None]   # the poses the lead takes at q0 = 0 (relayed hits count later)
    r0 = None if r0_set is None else float(r0_set)
    for r in (np.arange(38.0, 130.0, 0.25) if r0_set is None else []):
        if all(float(B1.dist(i, (r * c + rim) @ M1.RS[i].T).min()) >= SKIN_CLR for i in tk): r0 = float(r); break
    if r0 is None: raise RuntimeError("no hub-0 underside clears the skin")
    under0 = r0 * c + dxy[:, :1] * e + dxy[:, 1:] * f
    wall0 = np.array([r0 * c + z * c + HUB_R * (math.cos(a) * e + math.sin(a) * f) for z in (0.0, 4.0, 8.0, HUB_H) for a in ang]
                     + [(r0 + HUB_H) * c + x * e + y * f for x, y in dxy])
    # hub 1's lift: its lower plate (disc on u1) clears hub 0's crown plane by WEDGE_MIN wherever the two discs overlap
    f1 = float(M1.f[0]); m1, X1 = M1.rigid["hub1"]; crown = r0 + HUB_H
    lat0 = lambda P: np.linalg.norm(P - (P @ c)[:, None] * c, axis=1)
    h = None                                                   # never less than a hub (the wedge sits on hub 0's crown)
    for hh in np.arange(HUB_H, 90.0, 0.05):
        P = X1 + hh * u1; ov = lat0(P) <= HUB_R
        if (f1 + hh) * float(u1 @ c) - crown >= WEDGE_MIN and (not ov.any() or float((P[ov] @ c).min()) - crown >= WEDGE_MIN): h = float(hh); break
    if h is None: raise RuntimeError("no stack: hub 1 cannot sit on hub 0's crown")
    X1l = X1 + h * u1; exposed = lat0(X1l) > HUB_R             # covered samples sit on the wedge: not skin-facing
    # L1a on hub 1's boss (flip): lifted h + FLIP; riser wall from the lifted root down to hub K's plate level
    mL, XL = M1.link_pts["L1a"]; XLl = XL + (h + FLIP) * u1
    latL = np.linalg.norm(XL - (XL @ u1)[:, None] * u1, axis=1); jn = int(np.argmin(latL))
    dirr = XL[jn] - (XL[jn] @ u1) * u1; dirr = dirr / np.linalg.norm(dirr); side = np.cross(u1, dirr)
    z_lo = float(M1.fK); z_hi = f1 + h + FLIP + 3.0
    riser = np.array([z * u1 + (HUB_R + 0.5 + t) * dirr + w * side for z in np.arange(z_lo, z_hi + 1e-6, 1.5)
                      for t in (0.0, RISER_T / 2, RISER_T) for w in (-4.0, -2.0, 0.0, 2.0, 4.0)])
    return dict(c=c, r0=r0, h=round(h, 2), under0=under0, wall0=wall0, X1l=X1l, exposed=exposed, m1=m1, XLl=XLl, mL=mL,
                riser=riser, u1=u1, f1=f1, n_exposed=int(exposed.sum()), riser_h=round(z_hi - z_lo, 1),
                hub0_off=round(float(np.linalg.norm(r0 * c - (r0 * c @ u1) * u1)), 1))


def slices(M):
    """index ranges of hub1 and L1a inside the lead's metal_points order (rigid..., link_pts...)"""
    off = 0; out = {}
    for k, (m, X) in M.rigid.items(): out["rigid:" + k] = (off, off + len(X)); off += len(X)
    for k, (m, X) in M.link_pts.items(): out["link:" + k] = (off, off + len(X)); off += len(X)
    return out


def real_eval(M, B, i, G, sl):
    """REAL record of pose i on model M (base or relayed): None if the lead's chain does not take it there, 'parts' if a
    stack part clashes, else the per-sample distance array (+ the min contact sample when it is in the skin)"""
    r = B.res[i]
    if r is None: return None, {}
    a, b = sl["rigid:hub1"]; la, lb = sl["link:L1a"]
    P = M.metal_points(i); assert P.shape[0] >= lb
    keep = np.r_[np.arange(0, a), np.arange(b, la), np.arange(lb, len(P))]
    RS = M.RS[i]; R0, t0 = M.T(0, i); R1, t1 = M.T(1, i)
    hub1 = (G["X1l"][G["exposed"]] @ R0.T + t0) @ RS.T
    l1a = (G["XLl"] @ R1.T + t1) @ RS.T
    hub0 = G["under0"] @ RS.T
    Pn = np.concatenate([P[keep], hub1, l1a, hub0])
    d = B.dist(i, Pn)
    # contact samples: the lead's (hub 1's own ones lifted), hub 0's wall + crown, the riser
    riser_w = G["riser"] @ R1.T + t1                         # one signed-distance call for every contact sample
    PC = [M.world(m, i, Pc + G["h"] * G["u1"] if m == 0 else Pc) for m, Pc in M.contact] + [G["wall0"] @ RS.T, riser_w @ RS.T]
    dc = float(B.dist(i, np.concatenate(PC)).min())
    # stack clashes (scapula frame)
    c, r0 = G["c"], G["r0"]; cmin, who = 1e9, None
    for k, X, hh in L.member_pts(M, i):
        if k in ("hub1", "L1a"): continue
        dd = float(L.sd_cyl(X, r0 * c, c).min()) - hh
        if dd < cmin: cmin, who = dd, k
    rcl = float(L.sd_cyl(riser_w, r0 * c, c).min()) if not os.environ.get("WOB_NORISER") else 1e9   # counterfactual only
    u1r = R0 @ G["u1"]; h1c = (G["f1"] + G["h"]) * u1r; h1min, h1who = 1e9, None
    for k, X, hh in L.member_pts(M, i):
        if k in ("hub1", "L1a") or M._mem.get(k) in (0, 1): continue
        dd = float(L.sd_cyl(X, h1c, u1r).min()) - hh
        if dd < h1min: h1min, h1who = dd, k
    x = dict(hub0_clear=round(cmin, 2), hub0_who=who, riser_clear=round(rcl, 2), hub1_clear=round(h1min, 2), hub1_who=h1who,
             dc=round(dc, 2))
    if min(cmin, rcl, h1min) < PART_CLR: return "parts", x
    res = np.r_[d, dc] if dc < 0 else d
    return res, x


def base_real(M0, B, G, sl):
    out = {}; xs = {}
    for i in range(len(B.idx)):
        r, x = real_eval(M0, B, i, G, sl); out[i] = r; xs[i] = x
    return out, xs


def report(B, recs):
    out = [None if (r is None or isinstance(r, str)) else r for r in (recs[i] for i in range(len(B.idx)))]
    old = B.res; B.res = out
    try: rep = B.report()
    finally: B.res = old
    ws = np.array(B.kind) == "ws"; el = np.array([B.poses[j]["elev"] for j in range(len(B.idx))])
    tk = np.array([r is not None and float(np.min(r)) >= 0 for r in out]); ct = np.array([r is not None and float(np.min(r)) < 0 for r in out])
    rep.update(ws_taken=int((tk & ws).sum()), contacts=int(ct.sum()), parts=int(sum(isinstance(recs[i], str) for i in recs)),
               overhead=f"{int((tk & ws & (el >= 140)).sum())}/{int((ws & (el >= 140)).sum())}")
    tkm = [float(np.min(r)) for r in out if r is not None and float(np.min(r)) >= 0]
    rep["near_touch_min_mm"] = round(min(tkm), 3) if tkm else None
    return rep


def part_ib(B, recs, n_keep, n_h1, n_l1a, n_h0):
    """in-band (2-14) share per stack group over taken clip frames: chain (lead minus hub1/L1a), hub 1 crescent, L1a, hub 0"""
    acc = dict(chain=[], hub1=[], L1a=[], hub0=[])
    for i, r in recs.items():
        if B.kind[i] != "clip" or r is None or isinstance(r, str) or float(np.min(r)) < 0: continue
        acc["chain"].append(r[:n_keep]); acc["hub1"].append(r[n_keep:n_keep + n_h1])
        acc["L1a"].append(r[n_keep + n_h1:n_keep + n_h1 + n_l1a]); acc["hub0"].append(r[n_keep + n_h1 + n_l1a:n_keep + n_h1 + n_l1a + n_h0])
    f = lambda d: [round(float(((d >= 2) & (d <= 14)).mean()), 3), round(float(np.median(d)), 1), round(float(d.min()), 1), int(d.size)] if d.size else None
    return {k: f(np.concatenate(v)) if v else None for k, v in acc.items()}


def relay_wear(B, M1, P2, G, a0, M0, sl, base, log=print):
    """relay candidates for every pose the lead loses (policy (ii) both sides), each evaluated GHOST and REAL"""
    t = time.time(); c = G["c"]
    lost = [i for i in range(len(B.idx)) if i not in set(M0.poses_fit.tolist())]
    cand, Teff = L.relay_candidates(M0, c, a0, B, lost)
    side = {}
    for sgn, col in (("neg", 0), ("pos", 1)):
        Rc = {i: L.rot_mats(c, [v[col]])[0] for i, v in cand.items() if v[col] is not None}
        if not Rc: continue
        M2 = L.make_model(M1, P2, B, Rc, None); pf = set(M2.poses_fit.tolist())
        for i in Rc:
            q = cand[i][col]
            if not M2.kin_ok[i] or i not in pf: side[(i, sgn)] = dict(st="kin", q0=q); continue
            g = L.eval_pose(M2, B, i)
            if g["st"] != "ok": side[(i, sgn)] = dict(st="parts", q0=q, ghost=None, real="parts"); continue
            old = B.res[i]; B.res[i] = g["res"]
            try: rr, x = real_eval(M2, B, i, G, sl)
            finally: B.res[i] = old
            side[(i, sgn)] = dict(st="ok", q0=q, ghost=g["res"], real=rr, x=x)
    log(f"relay: lost {len(lost)}, candidates {len(cand)}, sides {len(side)}, Teff {Teff} ({time.time() - t:.0f} s)")
    return cand, side, Teff


def compose(B, base, cand, side, lo, hi, ghost=False):
    recs = {}; st = dict(relay_taken=0, relay_contact=0, relay_parts=0, relay_stop=0)
    for i in range(len(B.idx)):
        if i in cand:
            qn, qp = cand[i][:2]; opts = [(abs(q), s) for q, s in ((qn, "neg"), (qp, "pos")) if q is not None and lo <= q <= hi]
            if not opts: recs[i] = None; st["relay_stop"] += 1; continue
            e = side.get((i, min(opts)[1]))
            if e is None or e["st"] != "ok": recs[i] = None; st["relay_parts"] += 1; continue
            r = e["ghost"] if ghost else e["real"]
            if isinstance(r, str) or r is None: recs[i] = "parts"; st["relay_parts"] += 1; continue
            recs[i] = r; st["relay_contact" if float(np.min(r)) < 0 else "relay_taken"] += 1
        else:
            recs[i] = (B.res[i] if ghost else base[i])
    rep = report(B, recs); rep.update(st, window=[lo, hi]); return rep, recs


def append_sweep(path, entry):
    log = json.load(open(path)) if os.path.exists(path) else []
    entry = dict(k=len(log), t=now(), **entry); log.append(entry); json.dump(log, open(path, "w"), indent=1, default=float)
    return entry


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "census"
    t = time.time(); M1, P2, fit = L.fit_lead(); print("lead fit (Bench(60,160) fast):", fit, flush=True)
    SW = os.path.join(REPO, "docs", "concepts", "sweeps", ID + ".json")
    if mode == "census":
        sw = sys.argv[2] if len(sys.argv) > 2 else SW
        B = M1.B; M0 = L.make_model(M1, P2, B); r_lead = M0.run(); sl = slices(M0)
        M0._mem = {k: m for k, (m, X) in list(M0.cyl_surf.items()) + list(M0.rigid.items()) + list(M0.strap.items())}
        print("lead q0=0 rerun:", {k: r_lead[k] for k in ("gap", "reach", "inband14", "contact")}, flush=True)
        seats = [(a, z) for a in (6.0, 8.0, 10.0, 12.0) for z in range(0, 360, 30)]
        if len(sys.argv) > 3: seats = [tuple(map(float, s)) for s in json.loads(sys.argv[3])]
        for seat in seats:
            a0, azu = seat[0], seat[1]; r0s = seat[2] if len(seat) > 2 else None
            try: G = geometry(M1, a0, azu, r0s)
            except RuntimeError as ex:
                e = append_sweep(sw, dict(params=dict(a0=a0, azu=float(azu)), bench="Bench(60,160) fast", status=str(ex), gap=None, inband14=None,
                                          inband10=None, reach=None, follow=None, contact=None)); print(json.dumps(e), flush=True); continue
            base, xs = base_real(M0, B, G, sl); rep = report(B, base)
            nk = sl["rigid:hub1"][0] + (sl["link:L1a"][0] - sl["rigid:hub1"][1]) + (len(M0.metal_points(0)) - sl["link:L1a"][1])
            pib = part_ib(B, base, nk, G["n_exposed"], len(G["XLl"]), len(G["under0"]))
            why = {}
            for i, x in xs.items():
                if isinstance(base[i], str):
                    k = "hub0:" + str(x["hub0_who"]) if x["hub0_clear"] < PART_CLR else ("riser" if x["riser_clear"] < PART_CLR else "hub1:" + str(x["hub1_who"]))
                    why[k] = why.get(k, 0) + 1
            e = append_sweep(sw, dict(params=dict(a0=a0, azu=float(azu), q0="0 (no relay: metal price)", r0=G["r0"], r0_rule="set" if r0s else "2 mm skin on fit poses", h_lift=G["h"],
                                                  hub0_offset_mm=G["hub0_off"], riser_h=G["riser_h"], hub1_exposed=G["n_exposed"]),
                                      bench="Bench(60,160) fast", **{k: rep[k] for k in ("inband14", "inband10", "reach", "follow", "contact", "gap")},
                                      ws_taken=rep["ws_taken"], contacts=rep["contacts"], parts_lost=rep["parts"], parts_why=why, part_inband=pib,
                                      lead_same_bench=r_lead["gap"]))
            print(json.dumps({k: e[k] for k in ("k", "params", "gap", "inband14", "reach", "ws_taken", "parts_lost", "parts_why", "part_inband")}, default=float), flush=True)
    elif mode in ("relay", "claim"):
        a0, azu = float(sys.argv[2]), float(sys.argv[3])
        if mode == "relay": B = M1.B
        else: B = CB.Bench(n_clip=110, n_ws=360)
        M0 = L.make_model(M1, P2, B); r_lead = M0.run(); sl = slices(M0)
        M0._mem = {k: m for k, (m, X) in list(M0.cyl_surf.items()) + list(M0.rigid.items()) + list(M0.strap.items())}
        print(f"lead q0=0 on {B.mode} Bench({len([k for k in B.kind if k == 'clip'])},{len([k for k in B.kind if k == 'ws'])}):",
              {k: r_lead[k] for k in ("gap", "reach", "inband14", "contact")}, flush=True)
        G = geometry(M1, a0, azu, float(os.environ["WOB_R0"]) if os.environ.get("WOB_R0") else None); base, xs = base_real(M0, B, G, sl); z = report(B, base)
        print("q0=0 REAL:", {k: z[k] for k in ("gap", "reach", "inband14", "contact", "ws_taken", "parts")}, flush=True)
        cand, side, Teff = relay_wear(B, M1, P2, G, a0, M0, sl, base)
        nk = sl["rigid:hub1"][0] + (sl["link:L1a"][0] - sl["rigid:hub1"][1]) + (len(M0.metal_points(0)) - sl["link:L1a"][1])
        if mode == "relay":
            qs = sorted(set([0.0] + [q for v in cand.values() for q in v[:2] if q is not None]))
            rows = []
            for lo in [q for q in qs if q <= 0]:
                for hi in [q for q in qs if q >= 0]:
                    r, _ = compose(B, base, cand, side, lo, hi); g, _ = compose(B, base, cand, side, lo, hi, ghost=True)
                    rows.append(dict(lo=lo, hi=hi, gap=r["gap"], ghost=g["gap"], **{k: r[k] for k in ("reach", "inband14", "contact", "ws_taken", "contacts", "relay_taken", "relay_contact", "relay_parts")}))
            rows.sort(key=lambda x: (x["gap"], x["hi"] - x["lo"])); best = rows[0]; gb = min(rows, key=lambda x: x["ghost"])
            sw = sys.argv[4] if len(sys.argv) > 4 else SW
            e = append_sweep(sw, dict(params=dict(a0=a0, azu=azu, lo=best["lo"], hi=best["hi"], r0=G["r0"], h_lift=G["h"], q0="policy (ii) relay"),
                                      bench="Bench(60,160) fast", **{k: best[k] for k in ("inband14", "reach", "contact", "gap")},
                                      inband10=None, follow=None, ghost_gap=best["ghost"], ghost_best=gb, q0_zero_gap=z["gap"], cand=len(cand),
                                      relay_taken=best["relay_taken"], relay_contact=best["relay_contact"], relay_parts=best["relay_parts"], n_windows=len(rows)))
            r, recs = compose(B, base, cand, side, best["lo"], best["hi"]); e["inband10"] = r["inband10"]; e["follow"] = r["follow"]
            log = json.load(open(sw)); log[-1] = e; json.dump(log, open(sw, "w"), indent=1, default=float)
            print(json.dumps(dict(best=best, ghost_best=gb, top=rows[:5], q0_zero=z["gap"], cand=len(cand)), default=float), flush=True)
        else:
            lo, hi = float(sys.argv[4]), float(sys.argv[5])
            r, recs = compose(B, base, cand, side, lo, hi); g, _ = compose(B, base, cand, side, lo, hi, ghost=True)
            pib = part_ib(B, recs, nk, G["n_exposed"], len(G["XLl"]), len(G["under0"]))
            why = {}
            for i, x in xs.items():
                if isinstance(base[i], str):
                    k = "hub0:" + str(x["hub0_who"]) if x["hub0_clear"] < PART_CLR else ("riser" if x["riser_clear"] < PART_CLR else "hub1:" + str(x["hub1_who"]))
                    why[k] = why.get(k, 0) + 1
            rel = sorted([dict(i=i, side=s, q0=e_["q0"], st=e_["st"], real=("parts" if isinstance(e_.get("real"), str) else
                                (round(float(np.min(e_["real"])), 2) if e_.get("real") is not None else None)),
                               ghost=(round(float(np.min(e_["ghost"])), 2) if e_.get("ghost") is not None else None), x=e_.get("x"),
                               pose=[B.poses[i][k] for k in ("plane", "elev", "axial")]) for (i, s), e_ in side.items()], key=lambda d: d["i"])
            out = dict(row=ID, a0=a0, azu=azu, window=[lo, hi], bench=[110, 360], mode=B.mode, fit_fast=fit, lead=r_lead["gap"],
                       real={k: v for k, v in r.items()}, ghost=g, q0_zero=z, parts_inband=pib, parts_why_q0=why,
                       geo=dict(r0=G["r0"], h_lift=G["h"], hub0_off=G["hub0_off"], riser_h=G["riser_h"], hub1_exposed=G["n_exposed"]),
                       relays=rel, Teff=Teff, secs=round(time.time() - t))
            print(json.dumps({k: out[k] for k in ("real", "ghost", "q0_zero", "parts_inband", "parts_why_q0", "geo", "secs")}, default=float))
            if len(sys.argv) > 6: json.dump(out, open(sys.argv[6], "w"), indent=1, default=float)
