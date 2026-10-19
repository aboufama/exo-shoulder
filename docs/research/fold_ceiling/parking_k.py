"""fold-ceiling step 2d: the K-DYAD parking at the leader's seats (exact skin, Bench(110,360)). parking.py showed hub 2 can
sit over most stretched-lost poses at its current level; the stretched wall is a1max + a2 - 5 with a1max <= bk1 + bk2 - 5.
Here: for K dyads (bk1, bk2) long enough to open a1e to a1max = bk1 + bk2 - 5, the exact requirement of hub K (O20 disc)
and of link 1a / 1b (a 6 mm-radius disc at each strap's mid-arc: the strap's centre line +- 6 mm) on EVERY pose the
extended chain closes (clip frames at stop A, the leader's taken workspace poses, the newly closed lost poses), with the
IDEAL slaved law (a1e = a1 on stop A while th <= a1 + a2 - 5, else th - a2 + 5). Hub 2 is re-read on the same poses.
Each part's level must clear every closed pose (else contact); in band on a clip frame iff level - req <= 12.
    OMP_NUM_THREADS=1 nice -n 10 python3 docs/research/fold_ceiling/parking_k.py '[[26,38],[28,45],[30,50]]'
"""
import importlib.util, json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools")); import concept_bench as CB; import concept_kit as K  # noqa: E402
L = json.load(open(os.path.join(HERE, "lost_poses_roller-longdyad-knuckle-3r.json")))
WHICH = os.environ.get("FC_WEAR", "bench")
if WHICH == "fast":                                          # screening: Bench(60,160) fast grid (taken / th from the model's own IK)
    B = CB.Bench(60, 160); assert B.grid is not None
    sp0 = importlib.util.spec_from_file_location("lead_fast", os.path.join(REPO, "docs", "concepts", "models", "roller-longdyad-knuckle-3r.py"))
    M0 = importlib.util.module_from_spec(sp0); sp0.loader.exec_module(M0)
    r0, Mf = M0._report(B, M0._clamp(dict(M0.PARAMS, **L["params"])))
    Zf = CB._poses_all()["HG"][B.idx].astype(float)
    thf = np.degrees(np.arccos(np.clip((Zf @ np.array(L["u3"])) @ np.array(L["u1"]), -1, 1)))
    tk = [Mf.why[i] in (None, "ok", "") if hasattr(Mf, "why") else False for i in range(len(B.idx))]
    rows = [dict(th=float(thf[i]), taken=bool(B.res[i] is not None and float(np.min(B.res[i])) >= 0)) for i in range(len(B.idx))]
elif WHICH == "held":
    pv = importlib.util.spec_from_file_location("pkpol", os.path.join(REPO, "docs", "concepts", "verify", "skin-normal-3r-pin-knee-polish.py"))
    PV = importlib.util.module_from_spec(pv); pv.loader.exec_module(PV); B = PV.held_bench(); rows = L["held"]
else:
    os.environ["CB_EXACT"] = "1"; B = CB.Bench(110, 360); rows = L["bench"]
F = K.frames(B); Z = CB._poses_all(); Q = Z["HG"][B.idx].astype(float)
u1, u3 = np.array(L["u1"]), np.array(L["u3"]); a1, a2 = L["a1"], L["a2"]; uKL = np.array(L["uK"]); u2r = np.array(L["u2"])
sK = float(np.sign(np.cross(u1, u2r) @ uKL)) or 1.0                         # the leader's K side
kind = np.array(B.kind); taken = np.array([r["taken"] for r in rows]); th = np.array([r["th"] for r in rows])
w = Q @ u3
sp = importlib.util.spec_from_file_location("pk_core", os.path.join(HERE, "parking.py"))
src = open(os.path.join(HERE, "parking.py")).read(); s0 = src.index("def brute_req"); s1 = src.index("def world(i, v)")
G = dict(np=np, K=K, B=B, os=os, xy=K.disc_xy(10.0, 2.0)); exec(src[s0:s1], G)
brute_req = G["brute_req"]


def req_parts(I, axes, rad):
    """per pose in I: requirement of a disc of radius rad on each axis (n, 3) world -> max over its samples"""
    xy = K.disc_xy(rad, 2.0); k = K.unit(axes); A, Bv = K.plane_frame(k); m = len(xy); out = np.empty(len(I))
    O = xy[None, :, :1] * A[:, None, :] + xy[None, :, 1:] * Bv[:, None, :]
    for c in np.unique(I):
        sel = np.nonzero(I == c)[0]
        R = brute_req(c, np.repeat(k[sel], m, 0), O[sel].reshape(-1, 3)).reshape(len(sel), m)
        out[sel] = np.where(np.isfinite(R), R, 400.0).max(1)
    return out


def slerp(a, b, f):
    c = np.clip((a * b).sum(-1), -1, 1); om = np.arccos(c)[:, None] + 1e-9
    return K.unit((np.sin((1 - f) * om) * a + np.sin(f * om) * b) / np.sin(om))


out = dict(bench=WHICH, sK=sK, options=[])
OPTS = json.loads(sys.argv[1]) if len(sys.argv) > 1 else [[26, 38], [28, 45], [30, 50]]
a1_0, a2_0 = a1, a2; U1 = np.broadcast_to(u1, w.shape)
PARTN = ("hubK", "hub2", "link1a_mid", "link1b_mid", "hub3_ray", "link2_1/3", "link2_2/3"); RAD = (10.0, 10.0, 6.0, 6.0, 10.0, 6.0, 6.0)
geo = []                                                    # per option: closed mask + the 7 part axes (scapula frame)
for opt in OPTS:
    if isinstance(opt, dict): bk1, bk2, a1, a2 = opt["bk1"], opt["bk2"], opt.get("a1", a1_0), opt.get("a2", a2_0)
    else: (bk1, bk2), a1, a2 = opt, a1_0, a2_0
    amax = bk1 + bk2 - 5.0
    dkmax = opt.get("dkmax") if isinstance(opt, dict) else None
    if dkmax is not None:                                     # the K drive's stroke caps a1e through the K sub-dyad law
        r_ = math.radians; cpsi = (math.cos(r_(a1)) - math.cos(r_(bk1)) * math.cos(r_(bk2))) / (math.sin(r_(bk1)) * math.sin(r_(bk2)))
        psiA = math.degrees(math.acos(max(-1.0, min(1.0, cpsi)))); ps = min(180.0, psiA + float(dkmax))
        a1e_dk = math.degrees(math.acos(math.cos(r_(bk1)) * math.cos(r_(bk2)) + math.sin(r_(bk1)) * math.sin(r_(bk2)) * math.cos(r_(ps))))
        amax = min(amax, a1e_dk)
    hi = amax + a2 - 5.0; lo = abs(a1 - a2) + 5.0
    a1e = np.where(th <= a1 + a2 - 5.0, a1, th - a2 + 5.0)
    clos = (th >= lo) & (th <= hi) & (abs(bk1 - bk2) + 5.0 <= a1)
    c = np.clip((U1 * w).sum(-1), -1, 1); n = K.unit(np.cross(U1, w)); A1, A2 = np.radians(a1e), math.radians(a2)
    den = 1 - c ** 2 + 1e-12; Aq = (np.cos(A1) - c * math.cos(A2)) / den; Bq = (math.cos(A2) - c * np.cos(A1)) / den
    p0 = Aq[:, None] * U1 + Bq[:, None] * w; h2 = 1 - (p0 * p0).sum(-1)
    u2 = K.unit(p0 - 1.0 * np.sqrt(np.clip(h2, 0, None))[:, None] * n); clos &= h2 > 0          # branch -1 (the leader's)
    uK, okK, _ = K.closure(U1, u2, bk1, bk2, sK, margin_deg=0.0); clos &= okK
    axes = [uK, u2, slerp(U1, uK, 0.5), slerp(uK, u2, 0.5), w, slerp(u2, w, 1 / 3), slerp(u2, w, 2 / 3)]
    geo.append(dict(bk1=bk1, bk2=bk2, a1=a1, a2=a2, amax=amax, lo=lo, hi=hi, clos=clos, axes=axes, dkmax=dkmax))
# pose-major: ONE exact signed-distance call per pose for every part of every option
REQ = [np.full((len(PARTN), len(th)), np.nan) for _ in geo]
for i in range(len(th)):
    rays, origs, tags = [], [], []
    for gi, g in enumerate(geo):
        if not g["clos"][i]: continue
        for k, (ax, rad) in enumerate(zip(g["axes"], RAD)):
            xy = K.disc_xy(rad, 2.0); kk = K.unit(F.RS[i] @ ax[i]); A, Bv = K.plane_frame(kk[None]); A, Bv = A[0], Bv[0]
            rays.append(np.repeat(kk[None], len(xy), 0)); origs.append(xy[:, :1] * A + xy[:, 1:] * Bv); tags.append((gi, k, len(xy)))
    if not rays: continue
    R = brute_req(i, np.concatenate(rays), np.concatenate(origs)); R = np.where(np.isfinite(R), R, 400.0); o = 0
    for gi, k, m in tags: REQ[gi][k, i] = R[o:o + m].max(); o += m
    if i % 50 == 0: print("pose", i, flush=True)
for g, Rq in zip(geo, REQ):
    clos = g["clos"]; I = np.nonzero(clos)[0]; ck = kind[I] == "clip"; new = (kind[I] == "ws") & ~taken[I]; old = (kind[I] == "ws") & taken[I]
    PARTS = [(nm, Rq[k, I]) for k, nm in enumerate(PARTN)]
    res = dict(bk1=g["bk1"], bk2=g["bk2"], a1=g["a1"], a2=g["a2"], dkmax=g["dkmax"], a1max=round(g["amax"], 2), window=[round(g["lo"], 2), round(g["hi"], 2)],
               n_closed_ws=int((kind[I] == "ws").sum()), n_new_ws=int(new.sum()), n_clip=int(ck.sum()), in_window_ws=int(((kind == "ws") & clos).sum()))
    for nm, r in PARTS:
        res[nm] = dict(clip=np.percentile(r[ck], [0, 50, 100]).round(1).tolist(), old_ws_max=round(float(r[old].max()), 1) if old.any() else None,
                       new_ws=np.percentile(r[new], [0, 25, 50, 75, 100]).round(1).tolist() if new.any() else None,
                       new_clear_at_clip_level=int((r[new] <= r[ck].max()).sum()), new_clear_plus4=int((r[new] <= r[ck].max() + 4).sum()))
    for d in (0.0, 4.0, 8.0):
        okall = np.ones(len(I), bool)
        for _, r in PARTS: okall &= r <= r[ck].max() + d
        res[f"new_clear_all_parts_+{int(d)}"] = int((okall & new).sum()); res[f"old_lost_+{int(d)}"] = int((~okall & old).sum())
        res[f"R_est_+{int(d)}"] = round(float((okall & (kind[I] == "ws")).sum() / (kind == "ws").sum()), 4)
        res[f"ib_parts_+{int(d)}"] = round(float(np.mean([np.mean(r[ck].max() + d - r[ck] <= 12) for _, r in PARTS])), 3)
        res[f"clip_follow_+{int(d)}"] = round(float((okall & ck).sum() / max(1, ck.sum())), 3)
    out["options"].append(res); print(json.dumps(res), flush=True)
json.dump(out, open(os.path.join(HERE, f"parking_k_{WHICH}{os.environ.get('FC_TAG', '')}.json"), "w"), indent=1, default=float)
