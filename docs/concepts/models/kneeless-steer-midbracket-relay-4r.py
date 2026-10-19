"""kneeless-steer-midbracket-relay-4r (round 401, K1 track kneeless, lens A): phi40-thinstack-relay-4r WITHOUT the cuff
knee. J3 on a GH ray (b3 0) re-seated at (wd, wa) ~ (84, -15); own-angle stops q2 <= Q2MAX (J2 dowel slot) and J3 in
[J3MIN, J3MAX] (dowel groove); member 3 = hub 3 lower plate + ONE bent Ti bracket down E's fitted line to a T-nut
carriage at station s0 on a slotted arm-fixed shell (one-sided relay, PHI, axis tilt 12 / taz 235 through GH).
4 counted joints (J1, J2, J3, relay), K slaved (slipper nose), no knee, no cuff slides, 0 passive translations.

The parent (phi40) is imported READ-ONLY through its own module; this row's VDIR holds any flood cache (the flood key
carries neither b3 nor the seat: phi40's flood_*.json is never reused).

STEP 0 (pre-registered by the judge): ideal relay (no relay metal) on envsel, three readings per cell from ONE prepare:
  'bracket'  every chain sample of the knee chain kept (the proposer's over-count: E, O12 boss, pad, knee link);
  'deleted'  E / boss / pad / knee samples dropped (no bracket at all: optimistic on metal, pessimistic on in-band);
  'honest'   the BRACKET-HONEST proxy per station s0: E's samples kept only proximal of the carriage lug
             (station >= s0 + CAR_L/2, 'lug') or of the carriage centre (>= s0, 'ctr'), E's top-face contact samples cut
             the same way, boss / pad / knee samples and member-5 / member-6 contact entries dropped.
Stations s are read along the relay axis in the HG frame (rotation about the axis leaves them unchanged), as the parent's
geometry() reads the pad's station.

    OMP_NUM_THREADS=1 nice -n 10 python3 <this> step0 '<cells json>' '<s0 list>' out.jsonl
        cell = {"PHI":58, "wd":84, "wa":-15, "q2max":100, "J3MIN":-100, "J3MAX":115, ["tilt":12, "taz":235]}
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools")); os.chdir(REPO)
ID = "kneeless-steer-midbracket-relay-4r"
MODE = sys.argv[1] if len(sys.argv) > 1 else "check"
_ARGV = list(sys.argv)
if MODE == "step0" or (MODE == "metal" and len(sys.argv) > 4 and sys.argv[4] == "-2"):
    sys.argv = [sys.argv[0], "hwsweep", "{}", "[]", "-2"]                            # the parent installs envsel on this argv
_sp = importlib.util.spec_from_file_location("phi40_for_kneeless_steer", os.path.join(HERE, "phi40-thinstack-relay-4r.py"))
P4 = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(P4)
sys.argv = _ARGV
PT, AA, CB, OS = P4.OS.PT, P4.AA, P4.CB, P4.OS
VDIR = os.path.join(REPO, "docs", "concepts", "verify", ID); os.makedirs(VDIR, exist_ok=True)
PT.VDIR = VDIR; OS.VDIR = VDIR; P4.VDIR = VDIR
KNEE_PARTS = ("E", "boss", "pad", "knee")
CAR_L = float(PT.CAR_L)
LEAD0 = dict(AA.LEAD)

# ---- own-angle stops: J2 dowel slot (q2 <= Q2MAX) wraps the lead's gate; J3 groove goes into AA.LEAD (the gate reads P) ----
ST = dict(q2max=None)
_G0 = AA.gate


def _gate(M, Q):
    ok = _G0(M, Q)
    if ST["q2max"] is not None:
        q = M.D.ik(Q)[0]; ok = ok & (np.degrees(q[:, 1]) <= ST["q2max"])
    return ok


AA.gate = _gate
RAW = {}
NEED = dict(frames=None)                                      # solve phi only on the frames the wear bench uses (speed)
_SP0 = AA.solve_phi


def _solve(M, rp, frames=None):
    phi, ax = _SP0(M, rp, NEED["frames"] if frames is None else frames); RAW["phi"] = phi.copy(); return phi, ax


AA.solve_phi = _solve


def set_cell(cell):
    AA.LEAD.clear(); AA.LEAD.update(LEAD0)
    for k in ("J3MIN", "J3MAX"):
        if cell.get(k) is not None: AA.LEAD[k] = float(cell[k])
    ST["q2max"] = None if cell.get("q2max") is None else float(cell["q2max"])
    base = dict(P4.CLAIM_PARENT, **P4.HW0, b3=0.0, PHI=float(cell["PHI"]), wd=float(cell["wd"]), wa=float(cell["wa"]))
    for k in ("tilt", "taz", "delta"):
        if k in cell: base[k] = cell[k]
    return base


def layout(M):
    names = list(M.rigid) + list(M.link_pts); sizes = [len(X) for _, X in M.rigid.values()] + [len(X) for _, X in M.link_pts.values()]
    return names, sizes, np.cumsum([0] + sizes)


def stations(S):
    """E sample stations (and the pad's) along the relay axis, HG frame, at the first kin-ok fit clip frame"""
    M1, B1, ax = S["M1"], S["B1"], S["ax"]
    i0 = [j for j in range(len(B1.idx)) if B1.kind[j] == "clip" and M1.kin_ok[j]][0]
    out = {}
    for n in ("E", "pad", "hub3", "boss"):
        if n in M1.rigid:
            m, X = M1.rigid[n]; H = (M1.world(m, i0, X) @ M1.RS[i0]) @ M1.Q[i0]; out[n] = H @ ax
    return out


def readings(S, phi_raw, masks, cmask_fn, label):
    """re-derive the bench report per sample mask (name -> bool mask over the chain layout); cmask_fn(name) -> list of
    (member, Pc) contact entries to keep for the appended contact-only minimum"""
    M, B = S["M"], S["B"]; names, sizes, cut = layout(M)
    ws = np.array(B.kind) == "ws"; elev = np.array([p["elev"] for p in B.poses])
    res0 = [None if x is None else np.array(x) for x in B.res]; out = {}
    for tag, keep in masks.items():
        Wsel = cmask_fn(tag); R = []
        for j in range(len(B.idx)):
            d = res0[j]
            if d is None or (phi_raw is not None and not np.isfinite(phi_raw[j])): R.append(None); continue
            if len(d) == len(keep) + 1:                       # appended contact-only min (dc < 0): re-read on the kept entries
                Wc = [M.world(m, j, Pc) for m, Pc in Wsel]; Wc = [w for w in Wc if len(w)]
                dck = float(B.dist(j, np.concatenate(Wc)).min()) if Wc else 1e9
                d = np.r_[d[:-1][keep], dck] if dck < 0 else d[:-1][keep]
            elif len(d) != len(keep): raise SystemExit(f"layout mismatch {len(d)} vs {len(keep)}")
            else: d = d[keep]
            R.append(d)
        B.res = R; r = B.report(); rep = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
        mins = np.array([float(np.min(x)) if x is not None else np.nan for x in R])
        tk = np.isfinite(mins) & (mins >= 0); con = np.isfinite(mins) & (mins < 0); ov = ws & (elev >= 140)
        for thr, nm in ((1.0, "near1"), (2.0, "near2")):
            B.res = [None if x is None else x - thr for x in R]; rn = B.report(); rep[nm] = CB.gap_of(rep["inband14"], rn["follow"], rn["reach"], rn["contact"])
        B.res = R
        kc = np.cumsum(np.r_[0, [int(keep[cut[k]:cut[k + 1]].sum()) for k in range(len(names))]]); cpart = {}
        for j in np.nonzero(con)[0]:
            x = R[j]; best = min(((float(x[kc[k]:kc[k + 1]].min()), n) for k, n in enumerate(names) if kc[k + 1] > kc[k]), default=(9, "?"))
            nm = best[1] if best[0] < 0 else "contact-only"; cpart[nm] = cpart.get(nm, 0) + 1
        pib = {}
        for k, n in enumerate(names):
            if kc[k + 1] == kc[k]: continue
            acc = [R[j][kc[k]:kc[k + 1]] for j in range(len(B.idx)) if B.kind[j] == "clip" and tk[j]]
            if acc: dd = np.concatenate(acc); pib[n] = [round(float(((dd >= 2) & (dd <= 14)).mean()), 3), round(float(np.median(dd)), 1), int(kc[k + 1] - kc[k])]
        rep.update(contact_parts=cpart, ws_taken=int((ws & tk).sum()), ws=int(ws.sum()), overhead=[int((ov & tk).sum()), int(ov.sum())],
                   n_contact=int(con.sum()), depth_sum=round(float(-mins[con].sum()), 2), depth_max=round(float(-mins[con].min()) if con.any() else 0.0, 2),
                   relayed_contacts=int(sum(1 for j in np.nonzero(con)[0] if phi_raw is not None and np.isfinite(phi_raw[j]) and phi_raw[j] != 0)),
                   min_taken=round(float(np.nanmin(np.where(tk, mins, np.nan))), 3) if tk.any() else None,
                   contacts=[(int(j), [round(B.poses[j][k]) for k in ("plane", "elev", "axial")], round(float(mins[j]), 2)) for j in np.nonzero(con)[0]][:40],
                   parts_ib14=pib)
        out[tag] = rep
    B.res = res0
    return out


def step0_cell(cell, s0s):
    t = time.time(); base = set_cell(cell)
    import env_bench as EB
    NEED["frames"] = np.asarray(EB.key_of("envsel")[1])
    S = P4.prepare(base, -2, 0, exact=True); M, B = S["M"], S["B"]; phr = RAW["phi"][B.idx]
    names, sizes, cut = layout(M); st = stations(S); sE = st["E"]; s_pad = float(st["pad"].mean())
    nE = len(sE); iE = names.index("E")
    ent = [(m, len(Pc)) for m, Pc in M.contact]
    e_top = [k for k, (m, Pc) in enumerate(M.contact) if m == 3 and len(Pc) == nE]
    boss_top = [k for k, (m, Pc) in enumerate(M.contact) if m == 3 and "boss" in M.rigid and len(Pc) == len(M.rigid["boss"][1])
                and e_top and k > e_top[0]]                   # the boss tops follow E's top face (hub 3's own 4 x 32 crown sets precede it)
    base_keep = np.ones(cut[-1], bool)
    masks = {"bracket": base_keep.copy()}
    kd = base_keep.copy()
    for k, n in enumerate(names):
        if n in KNEE_PARTS: kd[cut[k]:cut[k + 1]] = False
    masks["deleted"] = kd
    emask = {}
    for s0 in s0s:
        for nm, sc in (("lug", s0 + 0.5 * CAR_L), ("ctr", s0)):
            ke = kd.copy(); ee = sE >= sc; ke[cut[iE]:cut[iE + 1]] = ee; masks[f"honest_{nm}_{s0:g}"] = ke; emask[f"honest_{nm}_{s0:g}"] = ee

    def cfn(tag):
        if tag == "bracket": return [(m, Pc) for m, Pc in M.contact]
        keep = []
        for k, (m, Pc) in enumerate(M.contact):
            if m in (5, 6) or k in boss_top: continue
            if k in e_top:
                if tag == "deleted": continue
                Pc = Pc[emask[tag]]
            keep.append((m, Pc))
        return keep
    o = readings(S, phr if ST["q2max"] is not None else None, masks, cfn, f"cell {cell}")
    o["meta_cfn"] = {t: len(cfn(t)) for t in ("bracket", "deleted")}
    o["meta"] = dict(cell=cell, s_pad=round(s_pad, 2), sE=[round(float(sE.min()), 1), round(float(sE.max()), 1)], s_hub3=round(float(st["hub3"].mean()), 1),
                     nE=nE, E_kept={k: int(v.sum()) for k, v in emask.items()}, contact_entries=ent, e_top=e_top, boss_top=boss_top,
                     ideal_prepared=S["ideal"], relayed=int(np.sum(np.isfinite(phr) & (phr != 0))), nan=int(np.sum(~np.isfinite(phr))),
                     why={w: int(sum(1 for x in M.why if x == w)) for w in set(map(str, M.why)) if w}, secs=round(time.time() - t, 1))
    return o, S


# ======================= STEP 1: the knee-less metal on the phi40 relay hardware =======================
# member 3 = hub 3 + E truncated at the carriage lug (s >= s0 + CAR_L/2) + T-nut carriage (+ lug coil, flange): the
# parent's carriage->pad bracket is deleted (no pad), boss / pad / knee samples and their contact entries are deleted,
# E's bump (the parent's ramped lift over the shell band, 60-deg climb) is the bracket's climb onto the carriage lug.
# Jam rule widened: EVERY chain part (not only E / boss / hub3 / L2 / knee / pad) vs the shell sector and the carriage.
KL = dict(on=False)
_BUMP0 = PT.bump_amounts
_RP0 = PT.relay_points


def _bump(M1, G, ax):
    out = _BUMP0(M1, G, ax)
    if not KL["on"]: return out
    o2 = {}
    for key, a in out.items():
        if key[0] in ("rigid", "link"):
            if key[1] in ("boss", "pad", "knee"): continue
            o2[key] = a[KL["emask"]] if key[1] == "E" else a
    for knew, (kold, mask) in enumerate(KL["cmap"]):
        a = out.get(("contact", kold))
        if a is not None: o2[("contact", knew)] = a if mask is None else a[mask]
    return o2


def _rp(G, ax):
    arm, car = _RP0(G, ax)
    if KL["on"]:
        keep = G["car_tag"] != "bracket"
        car = car[keep]; G["car_ib"] = G["car_ib"][keep]; G["car_tag"] = G["car_tag"][keep]; G["bracket_turn_mm"] = 0.0
    return arm, car


PT.bump_amounts = _bump; PT.relay_points = _rp
_RRS = P4._rr
for _a, _b in (('for n in ("knee", "E", "boss", "hub3", "L2", "pad") if n in per}', 'for n in per}'),
               ('for n in ("E", "boss", "hub3", "L2") if n in per}', 'for n in per}'),
               ('for _n in ("knee", "E", "boss", "hub3", "L2", "pad"):', 'for _n in list(per):')):
    assert _a in _RRS, f"parent rerecord source changed: {_a}"; _RRS = _RRS.replace(_a, _b)
exec(compile(_RRS, "rerecord_kneeless", "exec"), PT.__dict__); PT.rerecord = PT.rerecord_offset


def kneeless_apply(S, s_cut):
    """re-bind M's sample sets to the knee-less member 3 (E cut at station s_cut); M1 keeps the fitted originals"""
    M = S["M"]
    if "_orig" not in S: S["_orig"] = (M.rigid, M.link_pts, M.contact)
    rig0, lp0, con0 = S["_orig"]; st = stations(S); emask = st["E"] >= s_cut; nE = len(st["E"])
    nb = len(rig0["boss"][1]) if "boss" in rig0 else -1
    rig = {n: (m, (X[emask] if n == "E" else X)) for n, (m, X) in rig0.items() if n not in ("boss", "pad", "knee")}
    lp = {n: (m, X) for n, (m, X) in lp0.items() if n not in ("boss", "pad", "knee", "E")}
    con, cmap = [], []; ke = [k for k, (m, Pc) in enumerate(con0) if m == 3 and len(Pc) == nE]
    for k, (m, Pc) in enumerate(con0):
        if m in (5, 6) or (m == 3 and len(Pc) == nb and ke and k > ke[0]): continue
        if m == 3 and len(Pc) == nE: con.append((m, Pc[emask])); cmap.append((k, emask))
        else: con.append((m, Pc)); cmap.append((k, None))
    M.rigid, M.link_pts, M.contact = rig, lp, con
    KL.update(on=True, emask=emask, cmap=cmap, s_cut=s_cut)
    return int(emask.sum()), nE


def stop_lost(S):
    """poses with no relay angle in [0, PHI] passing the gates WITH the stops are lost ('j2stop' / stop), never taken"""
    phr = RAW["phi"][S["B"].idx]; S["phi_raw"] = phr; n = 0
    for j in range(len(S["B"].idx)):
        if not np.isfinite(phr[j]) and S["res0"][j] is not None: S["res0"][j] = None; S["why0"][j] = "stop"; n += 1
    S["B"].res = [None if x is None else np.array(x) for x in S["res0"]]
    return n


def e_end_azimuth(S, s_cut):
    """E's centroid azimuth (deg, rel. the pad's th0) of the samples within 4 mm proximal of the cut, and their radius"""
    M1, B1, ax = S["M1"], S["B1"], S["ax"]; e, f = AA._basis(ax)
    i0 = [j for j in range(len(B1.idx)) if B1.kind[j] == "clip" and M1.kin_ok[j]][0]
    def az_of(n, sel=None):
        m, X = M1.rigid[n]; H = (M1.world(m, i0, X) @ M1.RS[i0]) @ M1.Q[i0]
        if sel is not None: H = H[sel(H @ ax)]
        c = H.mean(0); return math.degrees(math.atan2(float(c @ f), float(c @ e))), float(np.linalg.norm(AA._rad(H, ax), axis=1).mean())
    azp, _ = az_of("pad"); aze, re_ = az_of("E", lambda s: (s >= s_cut) & (s <= s_cut + 4.0))
    return round(aze - azp, 2), round(re_, 2)


def wear_kneeless(S, base, s0, hw):
    st = stations(S); s_pad = float(st["pad"].mean()); s_cut = s0 + 0.5 * CAR_L
    nk, nE = kneeless_apply(S, s_cut); daz, rE = e_end_azimuth(S, s_cut)
    h = dict(hw); h["ds"] = s0 - s_pad
    if h.get("delta") == "E": h["delta"] = daz                    # carriage centred under the bracket's end
    o = P4.wear(S, dict(base, **h)); o["kneeless"] = dict(s0=s0, s_cut=round(s_cut, 2), s_pad=round(s_pad, 2), ds=round(h["ds"], 2), E_kept=nk, E_all=nE,
                                                          E_end_az_rel_pad=daz, E_end_r=rE, delta=h.get("delta"))
    return o


def short(o):
    w = o["wear"]
    return dict(gate=o["gate_gap"], obj1=o["obj_near1_gate"], wear=w["gap"], reach=w["reach"], ib14=w["inband14"], ib14_chain=o.get("ib14_gate"),
                ib10=w["inband10"], follow=w["follow"], contact=w["contact"], near2=o["near2_gap"], ws=o["ws_taken"], ovh=o["overhead"],
                cause=o.get("contacts_by_cause"), why=o.get("why"), kl=o["kneeless"], arc=o.get("thin_hw", {}).get("arc"), R_t=o.get("thin_hw", {}).get("R_t"),
                conn=(None if o.get("continuity") is None else dict(dropped_relayed=o["continuity"]["dropped_relayed"], static_gap=o["continuity"]["static"]["gap"])))


def metal_run(cell, s0hw, nc, nw, outp, exact=True, flood=False):
    """one prepare at the cell, the stop rule, then the knee-less metal per (s0, hw) entry"""
    base = set_cell(cell); base["flood"] = 1 if flood else 0
    if nc == -2:
        import env_bench as EB; NEED["frames"] = np.asarray(EB.key_of("envsel")[1])
    elif nc == -1: NEED["frames"] = None
    else: NEED["frames"] = np.asarray(CB._select(nc, nw)[0]) if hasattr(CB, "_select") else None
    if flood: NEED["frames"] = None                                  # the flood reads its own grid through solve_phi_Q
    t = time.time(); S = P4.prepare(base, nc, nw, exact=exact); nl = stop_lost(S)
    print(json.dumps(dict(prepared=True, cell=cell, ideal=S["ideal"], stop_lost=nl, flood=S.get("flood"), secs=round(time.time() - t, 1)), default=float), flush=True)
    res = []
    for s0, hw in s0hw:
        o = wear_kneeless(S, base, s0, hw); o["cell"] = cell; o["tag"] = f"s0{s0:g}_{json.dumps(hw, sort_keys=True)}"
        if nc != -2:
            try: o["th_margin"] = P4.BV.th_margin(S["M"], S["B"])
            except Exception as ex: o["th_margin"] = dict(err=repr(ex)[:200])
        res.append(o); print(json.dumps(dict(tag=o["tag"], **short(o), th_margin=o.get("th_margin")), default=float), flush=True)
        if outp:
            json.dump(res, open(outp, "w"), default=float)
            if nc != -2:
                pp = P4.perpose(S); pp.update(id=ID, wear=("held" if nc == -1 else f"bench({nc},{nw})"), params=dict(base, s0=s0, **hw), cell=cell, exact=exact)
                json.dump(pp, open(outp.replace(".json", f"_{len(res) - 1}_perpose.json"), "w"), default=float)
    return S, res


def write_viz(cell, rec, outp):
    """docs/concepts/viz/concepts/<id>.js: phi40's preview (same chain, relay solve, shell / carriage / coil) with the knee
    deleted: member 3 = hub 3 + the bracket to the carriage lug, rigid with the relayed arm frame; the q2 / J3 stops in
    the check (the relay takes the least phi at which they pass)"""
    par = dict(LEAD0, b3=0.0, wd=float(cell["wd"]), wa=float(cell["wa"]), J3MIN=float(cell["J3MIN"]), J3MAX=float(cell["J3MAX"]))
    vx = PT.CC.viz_export(PT.CC._clamp(dict(PT.CC.PARAMS, **par))) if hasattr(PT.CC, "_clamp") else PT.CC.viz_export(par)
    P, G = (vx["P"], vx["G"]) if isinstance(vx, dict) and "P" in vx else vx
    P = dict(P, J3MIN=float(cell["J3MIN"]), J3MAX=float(cell["J3MAX"]), Q2MAX=float(cell["q2max"]))
    ax = AA.raxis(float(cell.get("tilt", 12)), float(cell.get("taz", 235))); e, f = AA._basis(ax)
    th, off, kl = rec["thin_hw"], rec["offset_hw"], rec["kneeless"]; th0 = off["th0_pad"]; thc = th0 + off["delta"]
    cc = th["coil_c"]
    RL = dict(ax=[round(float(x), 5) for x in ax], e=[round(float(x), 5) for x in e], f=[round(float(x), 5) for x in f], s0=kl["s0"], Rt=th["R_t"],
              lo=round(th0 + th["arc"][0], 2), hi=round(th0 + th["arc"][1], 2), th0=round(th0, 2), hc=1.4, PHI=float(cell["PHI"]), sgn=1.0, sw=12.0,
              cw=14.0, cl=CAR_L, thc=round(thc, 2), coil=(None if cc is None else cc[1]), coilS=(None if cc is None else cc[0]), coilR=(None if cc is None else cc[2]),
              coilD=12.0, coilL=10.0, bump=1.2)
    src = open(os.path.join(REPO, "docs", "concepts", "viz", "concepts", "phi40-thinstack-relay-4r.js")).read()
    lines = src.split("\n")
    i0 = next(k for k, l in enumerate(lines) if l.startswith("(function () {"))
    body = "\n".join(lines[i0:])
    import re
    body = re.sub(r"  const P = \{.*?\};\n", "  const P = " + json.dumps(P, default=float) + ";\n", body, count=1)
    body = re.sub(r"  const G = \{.*?\};\n", "  const G = " + json.dumps(G, default=float) + ";\n", body, count=1)
    body = re.sub(r"  const RL = \{.*?\};\n", "  const RL = " + json.dumps(RL, default=float) + ";\n", body, count=1)
    a = body.index("  function solveQ(Q) {"); b = body.index("  const check = (q, ctx) => checkQ(q, Qof(ctx));")
    body = body[:a] + """  function solveQ(Q) {
    const k = ik(Q), R12 = M.mul(M.mul(M.rot(u[0], k.q1), M.rot(uK, k.dK)), M.rot(u[1], k.q2));
    const q3 = K.axisAngle(u[2], vref, M.mulv(M.T(R12), M.mulv(Q, vref)));
    return [k.q1, k.dK, k.q2, K.wrap180(q3)];
  }
  function fk(q) { const X = chain(q[0], q[1], q[2], q[3]); return Object.assign(X, { Rm3: X.R123 }); }
""" + body[b:]
    a = body.index("    const F = fk(q), sv = M.mulv(M.T(Q), F.t3), kn = knee("); b = body.index("    if (q[3] < P.J3MIN)")
    body = body[:a] + "    if (k.L.state === 0 && k.q2 > P.Q2MAX) return `J2 on its stretched dowel stop (q2 ${k.q2.toFixed(1)} > ${P.Q2MAX} deg: own-angle slot in hub 2's lower member)`;\n" + body[b:]
    body = body.replace("    const F = fk(q), sv = M.mulv(M.T(Q), F.t3), kn = knee([V.dot(sv, sa), V.dot(sv, st)]);\n", "")
    a = body.index("    id: 'phi40-thinstack-relay-4r'"); b = body.index("    solve: solveC,")
    body = body[:a] + """    id: '""" + ID + """', name: 'Knee-less steered relay: phi40 chain with the cuff knee deleted, J3 on a GH ray (""" + f"{cell['wd']:g}, {cell['wa']:g}" + """), own-angle stops q2 <= """ + f"{cell['q2max']:g}" + """ / J3 [""" + f"{cell['J3MIN']:g}, {cell['J3MAX']:g}" + """], one rigid member 3 (hub 3 + bracket + T-nut carriage) on an arm-fixed 1.0 mm shell at s0 """ + f"{kl['s0']:g}" + """, PHI """ + f"{cell['PHI']:g}" + """ (4 counted joints)',
    dof: { active: 4, passive: 1 },   // J1, J2, J3 + the counted relay; K slaved (slipper nose); no knee, no cuff slides
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'K (passive, slaved to q2 by the lobe - bell crank - sliding nose - flank)', 'J2', 'J3', 'relay phi (carriage on the arm arc; constant-force strip on its zero dowel)'], qUnits: ['deg', 'deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm', 'deg'],
""" + body[b:]
    body = body.replace("residual: (q, ctx) => { const F = fk(q); return M.rotErrDeg(F.R5, Qof(ctx)).concat(F.t5, [q[6] - phiOf(ctx)]); },",
                        "residual: (q, ctx) => { const F = fk(q); return M.rotErrDeg(F.Rm3, Qof(ctx)).concat(F.t3, [q[4] - phiOf(ctx)]); },")
    body = body.replace("name: 'J3 (skin-normal tilt, line misses GH; hard stop", "name: 'J3 (axis on a GH ray, re-seated; hard stop")
    keep = []
    for l in body.split("\n"):
        if any(t in l for t in ("name: 'knee pin a", "name: 'knee link", "name: 'knee pin b", "name: 'arm pad (on the cuff", "name: 'L-lug bracket", "name: 'E strap (member 3")): continue
        keep.append(l)
    body = "\n".join(keep)
    body = body.replace("      const n3 = Wd(M.mulv(F.Rm3, sn)), lvl = (p, h) => V.madd(W(p), n3, h), kz = G.tr + G.tp + G.RUN + G.tp / 2;\n", "")
    body = body.replace(", padC = arm(V.madd(G.Bm, sn, G.tr + G.tp / 2)), padN = M.mulv(Hc, sn);", ";")
    body = body.replace("      const axW = M.mulv(ctx.H, RL.ax);",
                        "      const axW = M.mulv(ctx.H, RL.ax), lug = M.mulv(Hc, V.madd(V.scale(RL.ax, RL.s0 + RL.cl / 2), dTh(RL.thc), RL.Rt + RL.hc + RL.bump));")
    body = body.replace("        h3,\n", "        h3,\n        { kind: 'link', role: 'link', name: 'member 3 bracket: one bent 3 x 10 Ti-6Al-4V bar down E\\'s fitted line, hub 3 lower plate -> the carriage posterior-proximal lug (60-deg climb, bend R >= 15)', a: rim, b: lug, r: 2.5 },\n", 1)
    body = body.replace("RL.s0), dTh(t), RL.Rt))", "RL.s0), dTh(t), RL.Rt))")
    head = ("/* " + ID + ": the knee-less steered relay at its best measured configuration (envsel). phi40-thinstack-relay-4r's chain\n"
            " * (J1 - K slaved by the slipper nose - J2 - J3) with J3 re-seated on a GH ray and the two-pin cuff knee DELETED: member 3\n"
            " * (hub 3 lower plate + one bent Ti bracket + a 14 x 14 T-nut carriage) is rigid with the relayed arm frame. Own-angle\n"
            " * stops (J2 dowel slot q2 <= Q2MAX, J3 groove [J3MIN, J3MAX]) steer the relay: per frame the relay takes the LEAST phi in\n"
            " * [0, PHI] at which the lead's gates and the stops pass. 4 counted joints, K passive (slaved), 0 passive translations.\n"
            " * Geometry: CC.viz_export at this seat + the relay geometry of the metal wear record. */\n")
    open(outp, "w").write(head + body)
    return outp


if __name__ == "__main__":
    if MODE == "step0":
        cells = json.loads(sys.argv[2]); s0s = json.loads(sys.argv[3]); outp = sys.argv[4]
        mlist = json.loads(sys.argv[5]) if len(sys.argv) > 5 else []          # optional knee-less metal on the same prepare
        for cell in cells:
            o, S = step0_cell(cell, s0s)
            shrt = {k: (v["gap"], v["n_contact"], v["inband14"], v["reach"], v["overhead"][0]) for k, v in o.items() if not k.startswith("meta")}
            print(json.dumps(dict(cell=cell, short=shrt, meta={k: o["meta"][k] for k in ("s_pad", "sE", "s_hub3", "E_kept", "relayed", "nan", "secs", "why")}), default=float), flush=True)
            with open(outp, "a") as f: f.write(json.dumps(o, default=float) + "\n")
            if mlist:
                base = set_cell(cell); base["flood"] = 0; stop_lost(S)
                for s0, hw in mlist:
                    w = wear_kneeless(S, base, s0, hw); w["cell"] = cell; w["tag"] = f"s0{s0:g}_{json.dumps(hw, sort_keys=True)}"
                    with open(outp.replace(".jsonl", "_metal.jsonl"), "a") as f: f.write(json.dumps(w, default=float) + "\n")
                    print(json.dumps(dict(tag=w["tag"], cell=cell, **short(w)), default=float), flush=True)
                KL["on"] = False
                if "_orig" in S: S["M"].rigid, S["M"].link_pts, S["M"].contact = S["_orig"]
        sys.exit(0)
    if MODE == "metal":                                     # metal '<cell>' '<[[s0, hw], ...]>' nc nw out [flood]
        cell = json.loads(sys.argv[2]); lst = json.loads(sys.argv[3]); nc, nw = int(sys.argv[4]), int(sys.argv[5]); outp = sys.argv[6]
        fl = len(sys.argv) > 7 and sys.argv[7] == "flood"
        if fl:                                              # the flood cache key carries neither seat nor stops: one sub-dir per cell
            sub = os.path.join(VDIR, "flood_" + "_".join(f"{k}{cell[k]:g}" for k in sorted(cell) if isinstance(cell[k], (int, float))))
            os.makedirs(sub, exist_ok=True); PT.VDIR = sub; OS.VDIR = sub; P4.VDIR = sub
        metal_run(cell, lst, nc, nw, outp, exact=(nc in (-2, -1) or os.environ.get("CB_EXACT") == "1"), flood=fl); sys.exit(0)
    if MODE == "viz":                                       # viz '<cell>' metal.jsonl line
        rec = [json.loads(l) for l in open(sys.argv[3])][int(sys.argv[4])]
        print(write_viz(json.loads(sys.argv[2]), rec, os.path.join(REPO, "docs", "concepts", "viz", "concepts", ID + ".js"))); sys.exit(0)
    print("modes: step0 | metal | viz")
