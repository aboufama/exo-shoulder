"""Independent RE-MEASURE verifier (skeptic) of proxtrack-relay-knuckle-4r (round 105 screened row).

The claim's model (docs/concepts/models/proxtrack-relay-knuckle-4r.py) is the mechanism under test and is loaded UNCHANGED
for the mechanism (lead fit Bench(60,160) fast at phi 0 -> shape frozen -> relay solve -> wear exact -> relay hardware
re-record). Everything the score is READ from is re-derived here from the per-pose metal arrays (B.res):

  R1. Frozen exact Bench(110,360) gap from B.res with my own taken / contact / in-band counts: plain (pooled in-band),
      chain-only in-band (relay shell / carriage / bracket metal out), the gate (lower of the two), near-touch 1 mm
      (metal < 1 mm counted as contact) on both in-band readings; the claim's own flood switched OFF (flood=0) so the
      static wear is read before any continuity knock-out.
  R2. J1-J3 fold margin th measured from the member frames (u1 . R2 u3; own state: forced -> min of the K sub-dyad and the
      effective dyad, else the plain dyad) on EVERY taken pose (clip + ws, relayed or not) of the wear.
  R3. Continuity: my own flood on the 15-deg workspace-envelope grid (1432 poses): 2-deg slerp edges with the least-phi
      relay solved at every frame, NO step > 10 deg in the relay, dK, knee pins qa / qb AND the actives (strict reading;
      the family's 25-deg active reading reported too), no stretched <-> folded state change inside an edge (branch);
      seeds = phi 0, state A. Kinematic version (nodes = closing poses) and contact-aware version (nodes = poses TAKEN on
      the exact benches I wore: Bench(110,360) + held-out; the few envelope poses on neither bench are kinematic-only,
      counted and stated). Reach on the CONNECTED set (every taken ws pose not connected is dropped, relayed or not).
  R4. Held out (the lead family's disjoint held-out bench, exact) with the verified 3-joint lead conecut-knee-knuckle-3r
      worn side by side on the SAME bench object from the SAME fit (the claim's phi-0 fit IS the lead's frozen fit).

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/proxtrack-relay-knuckle-4r-remeasure.py wear bench OUT.json [--edges EDGES.json]
    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/proxtrack-relay-knuckle-4r-remeasure.py wear held  OUT.json
    OMP_NUM_THREADS=1 python3 docs/concepts/verify/proxtrack-relay-knuckle-4r-remeasure.py combine BENCH.json HELD.json EDGES.json OUT.json
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
_sp = importlib.util.spec_from_file_location("proxtrack_for_remeasure", os.path.join(REPO, "docs", "concepts", "models", "proxtrack-relay-knuckle-4r.py"))
PT = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(PT)
AA, CB, CC = PT.AA, PT.CB, PT.CC
D2R = math.pi / 180
ROW = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "proxtrack-relay-knuckle-4r.json")))
CLAIM = dict(ROW["best_params"])
FM = 5.0


def _ang(a, b): return float(np.degrees(np.arccos(np.clip(float(np.dot(a, b)), -1, 1))))
def _dm(th, a, b): return min(th - abs(a - b), min(a + b, 360 - a - b) - th)


def readings(B, nC, n_rel_ib):
    """gap readings re-derived from B.res: pooled / chain-only in-band, plain / gate / near1 (both in-band readings)"""
    n = len(B.kind); cl = [j for j in range(n) if B.kind[j] == "clip"]; ws = [j for j in range(n) if B.kind[j] == "ws"]
    nz = [j for j in range(n) if B.res[j] is not None]
    mn = {j: float(np.min(B.res[j])) for j in nz}
    tk = lambda j, t=0.0: j in mn and mn[j] >= t
    tc = [j for j in cl if tk(j)]
    pooled = np.concatenate([B.res[j] for j in tc]) if tc else np.zeros(0)
    chain = np.concatenate([np.asarray(B.res[j])[:nC] for j in tc]) if tc else np.zeros(0)
    relay = np.concatenate([np.asarray(B.res[j])[nC:nC + n_rel_ib] for j in tc]) if tc else np.zeros(0)
    ib = lambda a: float(((a >= 2) & (a <= 14)).mean()) if len(a) else 0.0
    out = dict(n=n, n_clip=len(cl), n_ws=len(ws), evaluated=len(nz))
    for t, nm in ((0.0, "plain"), (1.0, "near1"), (2.0, "near2")):
        fol = float(np.mean([tk(j, t) for j in cl])); rea = float(np.mean([tk(j, t) for j in ws]))
        con = float(np.mean([mn[j] < t for j in nz])) if nz else 0.0
        out[nm] = dict(follow=round(fol, 4), reach=round(rea, 4), contact=round(con, 4), ws_taken=int(sum(tk(j, t) for j in ws)),
                       contact_poses=int(sum(mn[j] < t for j in nz)),
                       gap_pooled=CB.gap_of(round(ib(pooled), 4), round(fol, 4), round(rea, 4), round(con, 4)),
                       gap_chain=CB.gap_of(round(ib(chain), 4), round(fol, 4), round(rea, 4), round(con, 4)))
        out[nm]["gap_gate"] = max(out[nm]["gap_pooled"], out[nm]["gap_chain"])
    out["ib14_pooled"] = round(ib(pooled), 4); out["ib14_chain"] = round(ib(chain), 4); out["ib14_relay_metal"] = round(ib(relay), 4)
    out["n_pts_pooled"] = int(len(pooled)); out["n_pts_chain"] = int(len(chain)); out["n_pts_relay"] = int(len(relay))
    out["ib10_pooled"] = round(float(((pooled >= 2) & (pooled <= 10)).mean()), 4) if len(pooled) else 0.0
    out["min_metal_taken"] = round(min(mn[j] for j in nz if mn[j] >= 0), 3) if any(mn[j] >= 0 for j in nz) else None
    out["contacts"] = sorted([dict(i=j, kind=B.kind[j], pose=[B.poses[j][k] for k in ("plane", "elev", "axial")], mm=round(mn[j], 2)) for j in nz if mn[j] < 0], key=lambda r: r["mm"])
    return out


def th_margin(M, B, phi_b=None):
    """R2: fold margin from the member frames on every taken pose (own state)"""
    D = M.D; u1, u2, u3 = D.u; uK = D.uK
    a1 = math.degrees(D.a1) if D.a1 < 4 else D.a1; a2 = math.degrees(D.a2) if D.a2 < 4 else D.a2
    dK = np.asarray(M.dK, float)
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]; rows = []
    for i in taken:
        R1, _ = M.T(1, i); R1b, _ = M.T(7, i); R2, _ = M.T(2, i)
        jK = R1 @ uK; j2 = R1b @ u2; j3 = R2 @ u3
        th = _ang(u1, j3); a1e = _ang(u1, j2); a2e = _ang(j2, j3); b1 = _ang(u1, jK); c = _ang(jK, j3)
        forced = abs(float(dK[i])) > 1e-6
        own = min(_dm(th, b1, c), _dm(th, a1e, a2e)) if forced else _dm(th, a1, a2)
        rel = bool(phi_b is not None and abs(float(phi_b[i])) > 1e-9)
        rows.append(dict(own=own, forced=forced, relayed=rel, i=i, th=th, plain=_dm(th, a1, a2)))
    if not rows: return dict(min=None, n=0)
    own = np.array([r["own"] for r in rows]); lo = sorted(rows, key=lambda r: r["own"])[:6]
    sub = lambda f: [r["own"] for r in rows if f(r)]
    mm = lambda a: round(min(a), 3) if a else None
    return dict(min=round(float(own.min()), 3), n=len(rows), lt5=int((own < FM - 1e-6).sum()), forced=int(sum(r["forced"] for r in rows)),
                relayed=int(sum(r["relayed"] for r in rows)), min_relayed=mm(sub(lambda r: r["relayed"])), min_phi0=mm(sub(lambda r: not r["relayed"])),
                min_forced=mm(sub(lambda r: r["forced"])), min_stateA=mm(sub(lambda r: not r["forced"])),
                lowest=[dict(own=round(r["own"], 3), th=round(r["th"], 2), forced=r["forced"], relayed=r["relayed"], kind=B.kind[r["i"]],
                             **{k: B.poses[r["i"]][k] for k in ("plane", "elev", "axial")}) for r in lo])


def lead_wear(S):
    """the verified lead conecut-knee-knuckle-3r, frozen from the SAME phi-0 fit, worn on the SAME bench (no relay, no hardware)"""
    M1, B = S["M1"], S["B"]
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(CC.CCModel):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info", "_wedge_info", "cyl_r"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self._sc = None; self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]
            self.drop = np.zeros(len(self.poses_fit), bool); self._truncate()
    B.res = [None] * len(B.idx)
    ML = Frozen(B, P2); r = ML.run()
    nC = sum(len(X) for _, X in ML.rigid.values()) + sum(len(X) for _, X in ML.link_pts.values())
    rd = readings(B, nC, 0); rd["report"] = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    rd["th"] = th_margin(ML, B)
    rd["taken"] = {int(B.idx[j]): bool(B.res[j] is not None and float(np.min(B.res[j])) >= 0) for j in range(len(B.idx)) if B.kind[j] == "ws"}
    rd["state"] = {int(B.idx[j]): int(np.asarray(ML.kstate)[j]) for j in range(len(B.idx)) if B.kind[j] == "ws"} if hasattr(ML, "kstate") else None
    return rd


def kin_edges(M, rp, step_deg=2.0):
    """R3 kinematic: per envelope node least phi + state; per grid edge the max steps (relay, passives, actives) and branch flag"""
    from scipy.spatial.transform import Rotation as Rot, Slerp
    Z0 = AA.Z0; names = list(Z0["NAMES"]); allw = np.nonzero(Z0["CID"] == names.index("Workspace (envelope)"))[0]
    Ha = Z0["HG"][allw].astype(float); ph, ax = AA.solve_phi_Q(M, rp, Ha); feas = np.isfinite(ph)
    D = M.D; Qa = Ha.copy(); Qa[feas] = Ha[feas] @ AA.rotm(ax, ph[feas] * D2R)
    D.ik(Qa); sta = np.asarray(getattr(D, "_state", np.zeros(len(Qa))), float).copy()
    Pz = Z0["POSE"][allw]; keyf = {tuple(np.round(Pz[k, :3], 1)): k for k in range(len(allw)) if feas[k]}
    valsf = [sorted(set(np.round(Pz[:, d], 1))) for d in range(3)]
    edges = []
    for a in keyf.values():
        x = tuple(np.round(Pz[a, :3], 1))
        for d in range(3):
            j = valsf[d].index(x[d])
            for jj in (j - 1, j + 1):
                if 0 <= jj < len(valsf[d]):
                    y = list(x); y[d] = valsf[d][jj]; b = keyf.get(tuple(y))
                    if b is not None and a < b: edges.append((a, b))
    segs, Hs_all, off = [], [], 0
    for a, b in edges:
        R2 = Rot.from_matrix(np.stack([Ha[a], Ha[b]])); ang = np.degrees((R2[0].inv() * R2[1]).magnitude())
        m = max(2, int(math.ceil(ang / step_deg)) + 1); Hs = Slerp([0, 1], R2)(np.linspace(0, 1, m)).as_matrix()
        segs.append((off, m)); Hs_all.append(Hs); off += m
    H = np.concatenate(Hs_all); phs, _ = AA.solve_phi_Q(M, rp, H); okf = np.isfinite(phs)
    Qs = H.copy(); Qs[okf] = H[okf] @ AA.rotm(ax, phs[okf] * D2R)
    q, ok, _, _, _, s = D.ik(Qs); dK = np.asarray(getattr(D, "_dK", np.zeros(len(Qs))), float); Kn = D.knee(s)
    st = np.asarray(getattr(D, "_state", np.zeros(len(Qs))), float).copy()
    act = [np.degrees(q[:, 0]), np.degrees(q[:, 1]), np.degrees(q[:, 2] + Kn["phi"])]
    pas = [np.degrees(dK)] + [np.degrees(np.asarray(Kn[k], float)) for k in ("qa", "qb") if k in Kn]
    E = []
    for e, (o, m) in enumerate(segs):
        sl = slice(o, o + m)
        if not okf[sl].all(): E.append([int(allw[edges[e][0]]), int(allw[edges[e][1]]), 0, 99.0, 99.0, 99.0, 0]); continue
        dphi = float(np.abs(np.diff(phs[sl])).max())
        dpas = max(float(np.abs(AA.wr(np.diff(c[sl]))).max()) for c in pas)
        dact = max(float(np.abs(AA.wr(np.diff(c[sl]))).max()) for c in act)
        ss = st[sl]; branch = int(bool(((ss == 1).any() and (ss == -1).any())))
        E.append([int(allw[edges[e][0]]), int(allw[edges[e][1]]), 1, round(dphi, 3), round(dpas, 3), round(dact, 3), branch])
    nodes = {int(allw[k]): dict(feas=bool(feas[k]), phi=(round(float(ph[k]), 2) if feas[k] else None), state=int(sta[k])) for k in range(len(allw))}
    return dict(nodes=nodes, edges=E, cols=["a", "b", "closes", "dphi", "dpas", "dact", "branch"], n_frames=int(len(H)))


def flood(nodes, edges, allowed, act_lim=10.0, pas_lim=10.0):
    """flood from phi-0 state-A allowed nodes over edges passing the limits; -> set of connected nodes"""
    adj = {}
    for a, b, cl, dphi, dpas, dact, br in edges:
        if not cl or dphi > pas_lim or dpas > pas_lim or dact > act_lim or br: continue
        if a in allowed and b in allowed: adj.setdefault(a, []).append(b); adj.setdefault(b, []).append(a)
    seeds = [k for k in allowed if nodes[k]["feas"] and nodes[k]["phi"] == 0 and nodes[k]["state"] == 0]
    conn = set(seeds); front = list(seeds)
    while front:
        nxt = []
        for a in front:
            for b in adj.get(a, []):
                if b not in conn: conn.add(b); nxt.append(b)
        front = nxt
    return conn, len(seeds)


def wear_mode(which, outp, edges_out=None):
    t0 = time.time(); params = dict(CLAIM); params["flood"] = 0           # static wear; continuity is mine (R3)
    nc, nw = {"bench": (110, 360), "held": (-1, -1), "fast": (60, 160)}[which]
    if which != "fast": os.environ["CB_EXACT"] = "1"
    S = PT.prepare(params, nc, nw, exact=(which != "fast")); t1 = time.time()
    o = PT.wear(S, params); t2 = time.time()
    M, B = S["M"], S["B"]
    nC = sum(len(X) for _, X in M.rigid.values()) + sum(len(X) for _, X in M.link_pts.values())
    n_rel_ib = int(o["hw"]["n_relay_ib_pts"])
    out = dict(row=PT.ID, which=which, params=params, mode=B.mode, claim_model_static=dict(wear=o["wear"], gate_gap=o["gate_gap"], near1_gap=o["near1_gap"],
               ib14_chain_only=o["hw"]["ib14_chain_only"], jams=len(o["hw"]["jams"]), ws_taken=o["ws_taken"], overhead=o["overhead"], relayed=o["relayed"],
               relay_hw=o["relay_hw"], why=o["why"], bump_max_mm=o["hw"]["bump_max_mm"], bracket_ramp_deg=o["hw"]["bracket_ramp_deg"]),
               fit_fast=S["fit"], ideal_relay=S["ideal"], nC=nC, n_rel_ib=n_rel_ib)
    out["mine"] = readings(B, nC, n_rel_ib)
    phi_b = S["phi_b"]
    try: out["th"] = th_margin(M, B, phi_b)
    except Exception as e: out["th"] = dict(error=repr(e)[:300])
    out["taken"] = {int(B.idx[j]): bool(B.res[j] is not None and float(np.min(B.res[j])) >= 0) for j in range(len(B.idx)) if B.kind[j] == "ws"}
    out["phi_ws"] = {int(B.idx[j]): round(float(phi_b[j]), 2) for j in range(len(B.idx)) if B.kind[j] == "ws"}
    ws = np.array(B.kind) == "ws"; elev = np.array([p["elev"] for p in B.poses])
    tk = np.array([B.res[j] is not None and float(np.min(B.res[j])) >= 0 for j in range(len(B.idx))])
    out["overhead"] = [int((ws & tk & (elev >= 140)).sum()), int((ws & (elev >= 140)).sum())]
    out["clip_relayed"] = int(((~ws) & (np.abs(phi_b) > 1e-9)).sum())
    # per-pose metal minima of the claim (for the paired comparison)
    out["min_ws"] = {int(B.idx[j]): (round(float(np.min(B.res[j])), 2) if B.res[j] is not None else None) for j in range(len(B.idx)) if B.kind[j] == "ws"}
    out["secs_prepare"] = round(t1 - t0, 1); out["secs_wear"] = round(t2 - t1, 1)
    json.dump(out, open(outp, "w"), indent=1, default=float); print("claim done", round(time.time() - t0), json.dumps(out["mine"]["plain"]), flush=True)
    if edges_out:
        t3 = time.time(); rp = dict(S["rp"])
        KE = kin_edges(M, rp); KE["secs"] = round(time.time() - t3, 1)
        json.dump(KE, open(edges_out, "w"), default=float); print("edges done", KE["secs"], flush=True)
    # the lead side by side, same bench, same fit
    t4 = time.time()
    try:
        L = lead_wear(S); L["secs"] = round(time.time() - t4, 1); out["lead"] = L
        print("lead done", L["secs"], json.dumps(L["plain"]), flush=True)
    except Exception as e:
        import traceback; out["lead"] = dict(error=traceback.format_exc()[-1500:])
    out["min_ws_lead"] = None
    json.dump(out, open(outp, "w"), indent=1, default=float)


def combine(bench_p, held_p, edges_p, outp):
    Bn = json.load(open(bench_p)); Hd = json.load(open(held_p)) if held_p != "-" else None; KE = json.load(open(edges_p))
    nodes = {int(k): v for k, v in KE["nodes"].items()}; edges = KE["edges"]
    taken = {int(k): v for k, v in Bn["taken"].items()}
    if Hd: taken.update({int(k): v for k, v in Hd["taken"].items()})
    feas = {k for k, v in nodes.items() if v["feas"]}
    meas = {k for k in nodes if k in taken}
    allowed_ca = {k for k in feas if (taken.get(k, True))}                 # contact-aware: measured nodes must be taken; unmeasured kinematic only
    unmeasured = sorted(k for k in feas if k not in meas)
    out = dict(env=len(nodes), feasible=len(feas), measured=len(meas), unmeasured_feasible=len(unmeasured), edges=len(edges),
               edge_closes=sum(1 for e in edges if e[2]), edge_branch=sum(1 for e in edges if e[2] and e[6]),
               edge_fail_strict=dict(dphi=sum(1 for e in edges if e[2] and e[3] > 10), dpas=sum(1 for e in edges if e[2] and e[4] > 10),
                                     dact10=sum(1 for e in edges if e[2] and e[5] > 10), dact25=sum(1 for e in edges if e[2] and e[5] > 25)))
    for nm, allowed, alim in (("kin_family", feas, 25.0), ("kin_strict", feas, 10.0), ("contact_family", allowed_ca, 25.0), ("contact_strict", allowed_ca, 10.0)):
        conn, nseed = flood(nodes, edges, allowed, act_lim=alim)
        rr = dict(seeds=nseed, connected=len(conn))
        for tag, D_ in (("bench", Bn), ("held", Hd)):
            if not D_: continue
            tk = {int(k): v for k, v in D_["taken"].items()}; ph = {int(k): v for k, v in D_["phi_ws"].items()}
            ws_taken = [k for k, v in tk.items() if v]
            notc = [k for k in ws_taken if k not in conn]
            rr[tag] = dict(ws=len(tk), static_taken=len(ws_taken), connected_taken=len(ws_taken) - len(notc),
                           dropped=len(notc), dropped_relayed=sum(1 for k in notc if ph.get(k, 0) != 0), dropped_phi0=sum(1 for k in notc if ph.get(k, 0) == 0),
                           not_on_grid=sum(1 for k in ws_taken if k not in nodes))
            m = D_["mine"]["plain"]; reach_c = (len(ws_taken) - len(notc)) / len(tk)
            ibp, ibc = D_["mine"]["ib14_pooled"], D_["mine"]["ib14_chain"]
            # dropped poses become lost (not evaluated? no: a dropped pose is unreachable = not taken; it was taken so no contact)
            rr[tag]["reach_connected"] = round(reach_c, 4)
            rr[tag]["gap_plain_connected"] = CB.gap_of(ibp, m["follow"], round(reach_c, 4), m["contact"])
            rr[tag]["gap_gate_connected"] = max(rr[tag]["gap_plain_connected"], CB.gap_of(ibc, m["follow"], round(reach_c, 4), m["contact"]))
        out[nm] = rr
    json.dump(out, open(outp, "w"), indent=1, default=float); print(json.dumps(out, default=float))


def bumpcheck(outp):
    """is the 'rigid' bump rigid? the model displaces each bumped member-3 / knee-link point by a fixed AMOUNT along the
    radial direction about a_r in the carriage frame AT EACH POSE; a real rigid bump is a fixed vector in the member's own
    frame. Per bumped point: the spread of that direction seen from the member frame over the fit-bench poses + the fast
    bench's taken poses -> the displacement error a * |d - d_ref| (mm) a rigid part would show."""
    params = dict(CLAIM); params["flood"] = 0
    S = PT.prepare(params, 60, 160, exact=False); o = PT.wear(S, params)
    M1, B1, ax = S["M1"], S["B1"], S["ax"]
    G = PT.geometry(M1, B1, ax, dict(S["rp"])); bumps = PT.bump_amounts(M1, G, ax)
    rows = {}
    for (kd, nm), amt in bumps.items():
        if kd == "contact" or not np.any(amt > 0): continue
        m, X = (M1.rigid if kd == "rigid" else M1.link_pts)[nm]; sel = np.nonzero(amt > 0)[0]
        dirs = []
        for j in np.nonzero(M1.kin_ok)[0]:
            w = M1.world(m, j, X[sel]); h = (w @ M1.RS[j]) @ M1.Q[j]; r = AA._rad(h, ax); r = r / np.linalg.norm(r, axis=1, keepdims=True)
            Rm, _ = M1.T(m, j); dirs.append((r @ M1.Q[j].T) @ Rm)                            # scapula frame -> member frame (M.T is the scapula-frame transform; world = scap @ RS.T)
        Dd = np.stack(dirs)                                                                     # (poses, pts, 3)
        ref = Dd.mean(0); ref = ref / np.linalg.norm(ref, axis=1, keepdims=True)
        ang = np.degrees(np.arccos(np.clip(np.einsum("npk,pk->np", Dd, ref), -1, 1)))
        err = amt[sel][None] * 2 * np.sin(np.radians(ang) / 2)
        rows[f"{kd}:{nm}"] = dict(n_bumped=int(len(sel)), amt_max=round(float(amt.max()), 2), dir_spread_deg_max=round(float(ang.max()), 2),
                                  dir_spread_deg_p90=round(float(np.percentile(ang, 90)), 2), err_mm_max=round(float(err.max()), 2),
                                  err_mm_p90=round(float(np.percentile(err, 90)), 2))
    from scipy.spatial.transform import Rotation as Rot
    rel = {}
    for m in (3, 6, 5):                                     # rotation of each member relative to the carriage frame HG' over the fit poses
        Rs = [M1.T(m, j)[0].T @ M1.Q[j] for j in np.nonzero(M1.kin_ok)[0]]; Rr = Rot.from_matrix(np.stack(Rs))
        ang = np.degrees((Rr.mean().inv() * Rr).magnitude()); rel[m] = dict(max=round(float(ang.max()), 2), p90=round(float(np.percentile(ang, 90)), 2))
    out = dict(fast_wear=o["wear"], gate=o["gate_gap"], parts=rows, member_rot_vs_carriage_deg=rel)
    json.dump(out, open(outp, "w"), indent=1, default=float); print(json.dumps(out, default=float))


if __name__ == "__main__":
    md = sys.argv[1]
    if md == "wear":
        eo = None
        if "--edges" in sys.argv: eo = sys.argv[sys.argv.index("--edges") + 1]
        wear_mode(sys.argv[2], sys.argv[3], eo)
    elif md == "bumpcheck":
        bumpcheck(sys.argv[2])
    elif md == "combine":
        combine(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
