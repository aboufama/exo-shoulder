"""cap-plateau-knuckle-3r (round 14, pick 2: the cap-seat lens gate 0). The lead's slaved-knuckle chain moved to the
posterolateral CAP POLE (J1's O20 hub on top of the shoulder over the lateral scapular spine / posterior acromion), measured
in the fold-ceiling PAIRED KIT instrument (docs/research/fold_ceiling/kit_paired.py: O20 hubs, K3-march skin-fitted
3 x 12 mm Ti straps, neck to BOTTOM, K2 dense continuity, K6 part collisions, exact signed distance on Bench(110,360))
with the K law replaced per cell:

  cell A (routed U-law):      a1e = clip(max(lo, th - off), lo, cap)            lo 40, off 62, cap 62, a2 70
  cell B (short stop A):      the same one-sided law with a short stop A        lo 31.2 -> cap 56.37, off = a2 - m, a2 50.56
  cell C (two-sided dwell):   a1e = clip(max(lo, th - off, lo + (f - th)), lo, cap)   lo 28.03, off 38.18, cap 52.51, f 29.64

th = angle(J1, J3) (the ONE fold metric, tools/concept_kit.py FOLD_MARGIN); a pose is taken by the dyad only when
th in [|a1e - a2| + m, min(a1e + a2, 360 - a1e - a2) - m] at the law's a1e (m = 5 deg + K_PLAY, so the ~0.23 deg K play
cannot eat the user's 5 deg). K's own dyad (link 1a arc bk1, link 1b arc bk2) closes a1e; stop A (a1e = lo) sits
>= 5 deg from K's own fold (|bk1 - bk2| + 5 <= lo) and stop B (a1e = cap) >= 5 deg from its stretched fold
(bk1 + bk2 >= cap + 5).

HONESTY (read before quoting a number):
  - GHOST: the K DRIVE is not modelled (ideal slaved law; cells A / B would borrow desmo-conecut's one-sided drive on a
    pass, cell C's two-lobe drive does not exist). The cuff KNEE is not modelled either: in this instrument every axis
    passes through GH (no drift). Both arms of the PAIRED comparison (this model and CONTROL = the lead's seats / law in
    the same instrument) carry the same omissions, so compare paired, never against the lead's verified 18.28.
  - DOF: 3 ACTIVE (J1, J2, J3), K slaved (passive R, determined by the law), knee pins outside the count, 0 passive
    translations. No gears / pulleys / cables.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/cap-plateau-knuckle-3r.py kin [A|B|C|control]
    ... fit <cell> ['<json overrides>']          Bench(60,160) fast, K.evaluate (the screen number)
    ... frozen <cell> ['<json>'] [out.json]      fit fast, shape frozen, worn on Bench(110,360) EXACT (+ per-pose dump)
    ... held <cell> ...                          the same worn on the held-out set (claims only; never in search)
    ... jrate <cell>                              red team: J1 rate per unit arm rotation near the fold (cell C lobe)
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402
import concept_bench as CB                                   # noqa: E402

_sp = importlib.util.spec_from_file_location("kit_paired_cap", os.path.join(REPO, "docs", "research", "fold_ceiling", "kit_paired.py"))
KP = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(KP)

ID = "cap-plateau-knuckle-3r"
NAME = "Cap-pole slaved knuckle 3R (U-law / short-stop-A plateau / two-sided dwell cells)"
K_PLAY = 0.23                                                # deg: K's running play, added to the 5 deg fold margin
COMMON = dict(margin=K.FOLD_MARGIN + K_PLAY, width=12.0, t_link=3.0, q=1.0)
CELLS = {
    "A": dict(az1=43.2, el1=59.9, d3=90.0, a3=10.0, lo=40.0, off=62.0, cap=62.0, a2=70.0, f=None, bk1=30.0, bk2=None, sK=-1.0, sigma=-1.0),
    "B": dict(az1=56.17, el1=61.38, d3=91.05, a3=-9.21, lo=31.2, off=50.56 - 5.0 - K_PLAY - 0.01, cap=56.37, a2=50.56, f=None, bk1=32.11, bk2=None, sK=-1.0, sigma=-1.0),
    "C": dict(az1=61.22, el1=63.20, d3=100.17, a3=-4.12, lo=28.03, off=38.18, cap=52.51, a2=45.19, f=29.64, bk1=27.50, bk2=30.46, sK=-1.0, sigma=-1.0),
    # the lead's seats / law in this instrument (kit_paired CONTROL: a1 37.552, a2 57.218, a1max 58.768, bk1 26.0)
    "control": dict(az1=95.39, el1=67.90, d3=77.25, a3=-8.2, lo=37.552, off=57.218 - 5.0 - K_PLAY - 0.01, cap=58.768, a2=57.218, f=None, bk1=26.0, bk2=None, sK=-1.0, sigma=-1.0),
}
for _c in CELLS.values(): _c.update(COMMON)
PARAMS = dict(CELLS["C"], cell="C")


def law(th, p):
    lo, cap, off = float(p["lo"]), float(p["cap"]), float(p["off"])
    a = np.maximum(lo, th - off)
    if p.get("f") is not None: a = np.maximum(a, lo + (float(p["f"]) - th))       # cell C's folded-side lobe
    return np.clip(a, lo, cap)


def fold_ok(th, a1e, a2, m):
    lo = np.abs(a1e - a2) + m; hi = np.minimum(a1e + a2, 360.0 - a1e - a2) - m
    return (th >= lo) & (th <= hi), np.minimum(th - lo, hi - th)


def build(B, F, p):
    m = float(p["margin"]); a2 = float(p["a2"]); lo, cap = float(p["lo"]), float(p["cap"])
    bk1 = float(p["bk1"]); bk2 = float(p["bk2"]) if p.get("bk2") is not None else cap + 5.0 - bk1
    p1 = F.S(K.bvec(p["az1"], p["el1"])); p3 = F.HG(K.wdir(p["d3"], p["a3"]))
    th = np.degrees(np.arccos(np.clip((p1 * p3).sum(-1), -1, 1)))
    a1e = law(th, p); ok, marg = fold_ok(th, a1e, a2, m)
    ok &= (abs(bk1 - bk2) + 5.0 <= lo) & (bk1 + bk2 >= cap + 5.0 - 1e-9)      # K's own dyad: both stops >= 5 deg from its folds
    p2, okc = KP.closure_v(p1, p3, a1e, a2, float(p["sigma"])); ok &= okc
    pK, okK, _ = K.closure(p1, p2, bk1, bk2, float(p["sK"]), margin_deg=0.0); ok &= okK
    q = np.stack([K.axis_angle(p1, F.S([1.0, 0, 0]), pK), K.axis_angle(pK, p1, p2), K.axis_angle(p2, pK, p3),
                  K.axis_angle(p3, F.HG([0.0, -1, 0]), p2)], -1)
    for j, (s_lo, s_hi) in (p.get("stops") or {}).items():      # own-angle hard stops (dowel in an arc groove)
        ok &= ((q[:, int(j)] - s_lo) % 360.0) <= ((s_hi - s_lo) % 360.0)
    # link 2 rides over link 1a and the neck (kit); l2_over_hubK adds hub K (the spec's list; link 1b cannot be listed: the
    # kit forbids 'over' onto a member that itself has 'over' - its K6 clearance is then checked by K.collisions)
    hubs = [K.hub_member("hub1", p1, "J1"), K.hub_member("hubK", pK, "K"), K.hub_member("hub2", p2, "J2"), K.hub_member("hub3", p3, "J3")]
    w, t = p["width"], p["t_link"]
    links = [K.strap_member("link1a", p1, pK, ("J1", "K"), width=w, t=t, ramp_to=(("hub1", K.STACK), ("hubK", 0.0))),
             K.strap_member("link1b", pK, p2, ("K", "J2"), width=w, t=t, ramp_to=(("hubK", K.STACK), ("hub2", 0.0)), over=[("link1a", 1.0)]),
             K.strap_member("link2", p2, p3, ("J2", "J3"), width=w, t=t, ramp_to=(("hub2", K.STACK), ("hub3", K.STACK)),
                            over=[("link1a", 1.0), ("neck", 1.0)] + ([("hubK", 1.0)] if p.get("l2_over_hubK") else [])),
             K.neck_member(F, p3, joints=("J3",), ramps=(("hub3", 0.0), (None, 0)))]
    okm = np.asarray(ok, bool)
    return K.Chain(members=hubs + links, ok=ok, q=q, joints=dict(J1=p1, K=pK, J2=p2, J3=p3),
                   info=dict(min_margin=round(float(np.min(marg[okm])) + m, 2) if okm.any() else None,      # th distance from the dyad's fold (incl. the play allowance)
                             a1e_range=[round(float(np.min(a1e[okm])), 2), round(float(np.max(a1e[okm])), 2)] if okm.any() else None))


def P_of(cell, over=None):
    p = dict(CELLS[cell], cell=cell); p.update(over or {}); return p


def kin(cell, over=None, n=(110, 360)):
    """gate 0, kinematic half: fold / closure takes on Bench(n) (no metal; metal only removes takes)"""
    B = CB.Bench(*n); F = K.frames(B); p = P_of(cell, over); th_all = None
    ch = build(B, F, p); ok = np.asarray(ch.ok, bool); kind = np.array(B.kind); ws = kind == "ws"
    elev = np.array([B.poses[i]["elev"] for i in range(len(B.idx))])
    return dict(cell=cell, ws=f"{int((ok & ws).sum())}/{int(ws.sum())}", clip=f"{int((ok & ~ws).sum())}/{int((~ws).sum())}",
                overhead=f"{int((ok & ws & (elev >= 140)).sum())}/{int((ws & (elev >= 140)).sum())}", **ch.info)


def jrate(cell, over=None, n=(110, 360), eps=0.5):
    """red team (judge addition 1): J1 angle change per unit arm rotation on the taken low-th poses (J3 passing under J1)"""
    B = CB.Bench(*n); F = K.frames(B); p = P_of(cell, over); ch = build(B, F, p); ok = np.asarray(ch.ok, bool)
    p1 = np.asarray(ch.joints["J1"]); p3 = np.asarray(ch.joints["J3"]); th = np.degrees(np.arccos(np.clip((p1 * p3).sum(-1), -1, 1)))
    I = np.nonzero(ok & (th < 20))[0]; out = []
    rng = np.random.default_rng(0)
    for i in I:
        best = 0.0
        for _ in range(12):                                     # rotate J3's axis by eps deg about a random axis
            ax = K.unit(rng.normal(size=3)); ax = K.unit(ax - (ax @ p3[i]) * p3[i]); e = math.radians(eps)
            w2 = K.unit(p3[i] * math.cos(e) + np.cross(ax, p3[i]) * math.sin(e))
            t2 = math.degrees(math.acos(np.clip(p1[i] @ w2, -1, 1))); a = law(np.array([th[i], t2]), p)
            u2, okc = KP.closure_v(np.stack([p1[i], p1[i]]), np.stack([p3[i], w2]), a, float(p["a2"]), float(p["sigma"]))
            if not okc.all(): continue
            ref = F.S([1.0, 0, 0])[i]; q1 = K.axis_angle(np.stack([p1[i], p1[i]]), np.stack([ref, ref]), u2)
            best = max(best, abs(((q1[1] - q1[0] + 180) % 360) - 180) / eps)
        out.append((int(i), round(float(th[i]), 2), round(best, 2)))
    out.sort(key=lambda x: -x[2])
    return dict(n_lowth=len(I), worst=out[:8], th_5_12=[o for o in out if o[1] <= 12][:8])


def j2exit(cell, over=None, n=(110, 360)):
    """the J2-ray skin exit (K3 march, the kit requirement incl. its 2 mm clearance) on every fold-taken pose: where hub 2
    must sit on that pose (scratchpad judge102/j2exit.py's measure, with this cell's K law)"""
    B = K.bench(*n); F = K.frames(B); p = P_of(cell, over); ch = build(B, F, p); ok = np.asarray(ch.ok, bool)
    ws = np.array(B.kind) == "ws"; I = np.nonzero(ok)[0]; R = K.requirement(B, I, np.asarray(ch.joints["J2"])[I])
    R = np.where(np.isfinite(R), R, 400.0); out = dict(cell=cell, bench=list(n), mode=B.mode)
    for lab, msk in (("ws", ws[I]), ("clip", ~ws[I])):
        r = R[msk]
        if not len(r): continue
        lev = float(np.percentile(r, 90))
        out[lab] = dict(n=int(len(r)), pct_5_25_50_75_90_95_max=np.round(np.percentile(r, [5, 25, 50, 75, 90, 95, 100]), 1).tolist(),
                        gt75=int((r > 75).sum()), share_gt75=round(float((r > 75).mean()), 3))
    # one-level test: the hub-2 level that keeps the most taken poses with a 12 mm band (lev - exit <= 12 means in band)
    best = None
    for lev in range(50, 131):
        clear = R <= lev; inb = clear & (lev - R <= 12)
        cand = (int((clear & ws[I]).sum()), round(float(inb[clear].mean()) if clear.any() else 0.0, 3), lev)
        if cand[1] >= 0.8 and (best is None or cand[0] > best[0]): best = cand
    out["one_level_ib0.8"] = dict(ws_clear=best[0], ib=best[1], level=best[2]) if best else None
    out["per_pose"] = [(int(i), str(B.kind[i]), round(float(r), 1)) for i, r in zip(I, R)]
    return out


def levels(cell, over=None):
    """the Bench(60,160) fit's member levels (for the motion preview): hub cap radii, link underside medians"""
    B = K.bench(60, 160); r = K.evaluate(B, build, P_of(cell, over)); prof = B._kit_last["prof"]
    lv = {k: round(float(np.max(v)) if k.startswith("hub") else float(np.median(v)), 1) for k, v in prof.items()}
    return dict(levels=lv, fit={k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}, inband_member=r["inband_member"])


BOX = {  # the pre-registered sweep boxes (catalogue sweep_params); every bound is a hard edge
    "C": dict(az1=(56, 66), el1=(60, 67), d3=(96, 104), a3=(-8, 0), lo=(26, 31), f=(26, 34), cap=(50, 56), a2=(43, 48), bk1=(25, 30),
              doff=(6, 8), q=(0.95, 0.99)),
    "B": dict(az1=(52, 62), el1=(58, 66), d3=(88, 98), a3=(-14, -4), lo=(29, 34), a2=(48, 54), cap=(52, 60), bk1=(28, 34), q=(0.95, 0.99)),
    # equal-effort red team of the PAIRING: the control (lead seats / law) searched in a box of the same widths around it
    "control": dict(az1=(90, 100), el1=(64, 71), d3=(73, 81), a3=(-12, -4), lo=(35, 40), a2=(54, 60), cap=(56, 62), bk1=(24, 28), q=(0.95, 0.99)),
}
STEP = dict(az1=2.0, el1=2.0, d3=2.0, a3=2.0, lo=1.0, f=1.5, cap=1.5, a2=1.5, bk1=1.0, doff=0.5, q=0.01)


def near_gap(B, p):
    """the fit's 1 mm near-touch gap (the CLAUDE.md search objective) + the plain report"""
    r = K.evaluate(B, build, p); take = B._kit_last["take"]; Pi = np.nonzero(take)[0]
    ws = np.array(B.kind) == "ws"; good = np.zeros(len(ws), bool)
    if len(Pi): good[Pi[np.array([float(np.min(B.res[i])) >= 1.0 for i in Pi])]] = True
    return CB.gap_of(r["inband14"], good[~ws].mean(), good[ws].mean(), 0.0), r


def search(cell, n, seed, out, start=None):
    """local (1+1) search inside the cell's box on Bench(60,160) fast, 1 mm near-touch objective; every eval appended
    to `out` (a sweep-format list) as it lands"""
    B = K.bench(60, 160); rng = np.random.default_rng(seed); box = BOX[cell]; rows = []
    def mk(x):
        p = P_of(cell, x)
        if cell == "C": p["off"] = p["a2"] - x["doff"]; p["bk2"] = p["cap"] + 5.0 - p["bk1"] + 0.45
        else: p["off"] = p["a2"] - p["margin"] - 0.01; p["bk2"] = None
        return p
    c0 = CELLS[cell]; x = {k: (float(c0[k]) if k in c0 and c0[k] is not None else None) for k in box}
    if cell == "C": x["doff"] = c0["a2"] - c0["off"]
    x["q"] = 0.97; x.update(start or {})
    def rec(p, f, r):
        e = dict(k=len(rows), t=K.now(), params={k: v for k, v in p.items()}, **{k: r[k] for k in ("inband14", "inband10", "reach", "follow", "contact", "gap")},
                 gap_near1=f, honest=r["honest"], bench="Bench(60,160) fast fit", seed=seed)
        rows.append(e); json.dump(rows, open(out + ".tmp", "w"), indent=1, default=float); os.replace(out + ".tmp", out)
    p = mk(x); f, r = near_gap(B, p); rec(p, f, r); print("start", f, r["gap"], flush=True)
    for it in range(n):
        y = dict(x)
        for k in rng.choice(list(box), size=int(rng.integers(1, 4)), replace=False):
            y[k] = float(np.clip(y[k] + rng.normal(0, STEP[k]), *box[k]))
        q = mk(y); g, rr = near_gap(B, q); rec(q, g, rr)
        if g < f: x, f = y, g; print(it, "best", round(f, 2), rr["gap"], {k: round(v, 2) for k, v in y.items()}, flush=True)
    return x, f


def frozen(cell, over=None, which="bench"):
    KP.build = build                                         # the kit's wear() calls its module-level build: use this model's
    p = P_of(cell, over); t = time.time(); out = KP.wear(p, which); out["params"] = p; out["secs"] = round(time.time() - t, 1)
    return out


if __name__ == "__main__":
    a = sys.argv[1:]; mode = a[0] if a else "kin"; cell = a[1] if len(a) > 1 else "C"
    over = json.loads(a[2]) if len(a) > 2 and a[2].strip().startswith("{") else None
    if over and "doff" in over: over = dict(over, off=over.get("a2", CELLS[cell]["a2"]) - over["doff"])
    if over and cell == "C" and "cap" in over and "bk1" in over: over = dict(over, bk2=over["cap"] + 5.0 - over["bk1"] + 0.45)
    if mode == "kin": print(json.dumps(kin(cell, over)))
    elif mode == "jrate": print(json.dumps(jrate(cell, over)))
    elif mode == "j2exit":
        o = j2exit(cell, over); dst = a[-1] if a[-1].endswith(".json") else None
        if dst: json.dump(o, open(dst, "w"), indent=0)
        print(json.dumps({k: v for k, v in o.items() if k != "per_pose"}))
    elif mode == "search":
        x, f = search(cell, int(a[2]), int(a[3]), a[4], json.loads(a[5]) if len(a) > 5 else None); print("BEST", f, json.dumps(x))
    elif mode == "levels": print(json.dumps(levels(cell, over), default=float))
    elif mode == "fit":
        r = K.evaluate(K.bench(60, 160), build, P_of(cell, over))
        print(json.dumps({k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "audit", "inband_member",
                                            "mass_g", "flips", "collide", "min_margin", "a1e_range")}, default=float))
    elif mode in ("frozen", "held"):
        out = frozen(cell, over, "held" if mode == "held" else "bench"); dst = a[-1] if a[-1].endswith(".json") else None
        if dst: json.dump(out, open(dst, "w"), indent=0, default=float)
        print(json.dumps({k: v for k, v in out.items() if k != "poses"}, default=float))
