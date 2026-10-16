"""fold-sph3r: Spherical 3R on fold-frontier axes (catalogue id fold-sph3r, lens "fold-frontier", family "spherical 3R").

The most buildable morphology: three pins, each on a preloaded bearing pair in an O20 hub (docs/HARDWARE.md v5 joint:
MR117-2RS pair, 12.25 mm stack F -> crown), whose axes meet at GH. The chain has NO passive translation and NO cuff
slide: the bench's arm rotates about a fixed GH in the scapula frame (tools/concept_bench.py, origin = GH), so the
spherical chain closes exactly and member 3 is the arm-end plate + the K7 neck rigid to BOTTOM's bar. Passive
translations 0; cuff liner compliance claimed 0 mm (none is needed by the kinematics).

Kinematics and members = docs/concepts/models/_template.py build() verbatim (flat O20 hubs at their fitted level F
with the real stack, 12 x 3 mm straps with the 60 deg climb limit, K7 neck, K3 march, dense K2, K6, link 2 over link 1
and the neck). Seeds: docs/research/fold/frontier.json (az1, el1 -> az, el = J1 bvec; a1, a2; wd, wa = J3 wdir; both
branches sigma = +-1), tools/fold_frontier.py.

What this file adds over the template (the red-team lessons; the verifier checks them):
  * crowns and walls skin-checked: every hub is a solid O20 cylinder F .. F + 12.25 along its axis. The kit fits and
    scores only the skin face (the disc at F). Here the crown disc (F + 12.25) and the cylinder wall (r 10, 32 angles x
    7 levels) are measured in every taken pose; a pose where any of them is inside the skin becomes a contact pose
    (its min crown/wall distance is appended to the pose's record, so B.report counts it as contact and not taken;
    in-band is unchanged otherwise: the crown is not a skin-facing surface). Reported: crown_contact_poses, crown_min.
  * near-touch (lesson d): min metal-skin distance over taken poses (skin face + crowns + walls), and the bench gap
    with any metal < 1 mm counted as contact (gap_near1).
  * overhead (lesson e): reach over workspace poses with elevation >= 140, and in-band 2-14 / 2-10 over every taken
    pose (clip + workspace) with elevation >= 140 (+ counts).
  * per part (redteam): in-band per member, the fitted level of each hub (mm from GH), where it sits on the body, and
    which poses push it out of band.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/fold-sph3r.py [check|redteam] ['<json params>']
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) -> (params, report) (tools/concept_cma.py)
    big:   python3 docs/concepts/models/fold-sph3r.py frozen '<json params>' --out R.json   (CB_EXACT=1: Bench(110,360) exact,
           the geometry fitted on Bench(60,160) and frozen, K6 at 1 mm radial = tools/concept_bigbench.py frozen + the
           crown / near-touch / overhead checks above)
"""
import functools, json, math, os, sys, time
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402

ID = "fold-sph3r"
NAME = "Spherical 3R on fold-frontier axes"
# defaults = the frontier's best 50/50 layout (frontier.json best_by_sum[100])
PARAMS = dict(az=132.0, el=16.0, a1=50.0, a2=50.0, wd=75.0, wa=24.0, sigma=1, margin=10.0, width=12.0, t_link=3.0, q=1.0)
ELEV_OVER = 140.0
CROWN_LEVELS = (2.0, 4.0, 6.0, 8.0, 10.0, 12.25)


def build(B, F, p):
    """= docs/concepts/models/_template.py build() (kinematics, members, ranges), unchanged"""
    p1 = F.S(K.bvec(p["az"], p["el"]))                        # J1 fixed in the scapula
    p3 = F.HG(K.wdir(p["wd"], p["wa"]))                       # J3 fixed in the humerus
    p2, ok, margin = K.closure(p1, p3, p["a1"], p["a2"], p["sigma"], margin_deg=p["margin"])   # K1 (J2)
    q = np.stack([K.axis_angle(p1, F.S([1.0, 0, 0]), p2), K.axis_angle(p2, p1, p3),
                  K.axis_angle(p3, F.HG([0.0, -1, 0]), p2)], -1)
    hubs = [K.hub_member("hub1", p1, "J1"), K.hub_member("hub2", p2, "J2"), K.hub_member("hub3", p3, "J3")]
    w, t = p["width"], p["t_link"]
    links = [K.strap_member("link1", p1, p2, ("J1", "J2"), width=w, t=t, ramp_to=(("hub1", K.STACK), ("hub2", 0.0))),
             K.strap_member("link2", p2, p3, ("J2", "J3"), width=w, t=t, ramp_to=(("hub2", K.STACK), ("hub3", K.STACK)),
                            over=[("link1", 1.0), ("neck", 1.0)]),
             K.neck_member(F, p3, joints=("J3",), ramps=(("hub3", 0.0), (None, 0)))]
    return K.Chain(members=hubs + links, ok=ok, q=q, joints=dict(J1=p1, J2=p2, J3=p3),
                   info=dict(residual_deg=round(float(K.closure_residual(p1, p3, p2, p["a1"], p["a2"])[ok].max()), 5) if ok.any() else None,
                             min_margin=round(float(margin[ok].min()), 2) if ok.any() else None))


def crown_points(m, rho):
    """(P, k, 3) crown disc + cylinder wall samples of a flat hub member fitted at level rho[0] (F)"""
    F0 = float(rho[0]); k = m.K[:, None, :]
    crown = (F0 + K.CROWN) * k + m.xy[None, :, :1] * m.A[:, None, :] + m.xy[None, :, 1:] * m.Bv[:, None, :]
    ang = np.linspace(0, 2 * math.pi, 32, endpoint=False); c, s = K.HUB_R * np.cos(ang), K.HUB_R * np.sin(ang)
    wall = [(F0 + h) * k + c[None, :, None] * m.A[:, None, :] + s[None, :, None] * m.Bv[:, None, :] for h in CROWN_LEVELS]
    return np.concatenate([crown] + wall, 1)


def _taken(B, j): return B.res[j] is not None and float(np.min(B.res[j])) >= 0.0


def extras(B, r):
    """crown / wall check (turns poses with a crown or wall inside the skin into contact poses), near-touch, overhead"""
    L = B._kit_last; ch, prof, take = L["chain"], L["prof"], L["take"]
    Pi = np.array([j for j in np.nonzero(take)[0] if B.res[j] is not None], int)
    hubs = [m for m in ch.members if m.kind == "flat"]
    cmin = np.full(len(B.res), np.inf)
    if len(Pi):
        C = np.concatenate([crown_points(m, prof[m.name])[Pi] for m in hubs], 1)
        dc = K.dist_many(B, np.repeat(Pi, C.shape[1]), C.reshape(-1, 3)).reshape(len(Pi), C.shape[1])
        cmin[Pi] = dc.min(1)
    bad = np.nonzero(cmin < 0)[0]
    for j in bad: B.res[j] = np.append(B.res[j], cmin[j])
    rr = B.report()
    face_min = [float(np.min(B.res[j])) for j in range(len(B.res)) if _taken(B, j)]
    allmin = [min(float(np.min(B.res[j])), cmin[j]) for j in range(len(B.res)) if _taken(B, j)]
    # near-touch: any metal < 1 mm = contact
    save = list(B.res)
    for j in range(len(B.res)):                               # any metal (face, crown, wall) < 1 mm -> a contact pose
        if B.res[j] is not None and min(float(np.min(B.res[j])), cmin[j]) < 1.0: B.res[j] = np.append(B.res[j], -1e-3)
    rn = B.report(); B.res = save
    el = np.array([p["elev"] for p in B.poses]); ws = np.array([k == "ws" for k in B.kind])
    ov = np.nonzero(el >= ELEV_OVER)[0]; ovw = ov[ws[ov]]
    tk = [j for j in ov if _taken(B, j)]; d = np.concatenate([B.res[j] for j in tk]) if tk else np.zeros(0)
    over = dict(n_ws=int(len(ovw)), reach=round(float(np.mean([_taken(B, j) for j in ovw])), 4) if len(ovw) else None,
                n_taken=len(tk), inband14=round(float(((d >= 2) & (d <= 14)).mean()), 4) if len(d) else None,
                inband10=round(float(((d >= 2) & (d <= 10)).mean()), 4) if len(d) else None)
    for k in ("reach", "follow", "inband14", "inband10", "contact", "gap"): r[k] = rr[k]
    r.update(crown_contact_poses=int(len(bad)), crown_min=round(float(np.min(cmin[np.isfinite(cmin)])), 2) if np.isfinite(cmin).any() else None,
             min_metal_skin=round(float(min(allmin)), 2) if allmin else None, min_face_skin=round(float(min(face_min)), 2) if face_min else None,
             gap_near1=rn["gap"], near1=dict(reach=rn["reach"], follow=rn["follow"], inband14=rn["inband14"], contact=rn["contact"]),
             overhead=over)
    return r


def evaluate(B, params):
    """tools/concept_cma.py hook -> (params, report)"""
    p = dict(PARAMS, **params); r = K.evaluate(B, build, p); r = extras(B, r)
    return p, r


def bench_eval(B, params):
    """tools/concept_sweep.py hook -> report (JSON-able)"""
    _, r = evaluate(B, params)
    return {k: v for k, v in r.items() if _jsonable(v)}


def _jsonable(v):
    try:
        json.dumps(v); return True
    except (TypeError, ValueError):
        return False


def where(m, F, i):
    """body location words for a hub axis in pose i (thorax frame: x anterior, y up, z right/lateral)"""
    k = m.K[i]; az = math.degrees(math.atan2(k[2], k[0])); el = math.degrees(math.asin(max(-1, min(1, k[1]))))
    return f"axis thorax az {az:6.1f} (0 ant, 90 lat) el {el:5.1f}"


def redteam(B, p, r):
    L = B._kit_last; ch, prof, pts, take = L["chain"], L["prof"], L["pts"], L["take"]
    lab = lambda i: f"#{i:3d} {B.kind[i]:4s} {B.clip[i][:20]:20s} plane {B.poses[i]['plane']:6.1f} elev {B.poses[i]['elev']:6.1f} axial {B.poses[i]['axial']:6.1f}"
    Pi = np.nonzero(take)[0]; el = np.array([q["elev"] for q in B.poses]); pl = np.array([q["plane"] for q in B.poses])
    print("-- per part: in band (clip), fitted level, median / p90 distance over taken poses, out-of-band poses --")
    for m in ch.members:
        X = pts[m.name][Pi]; d = K.dist_many(B, np.repeat(Pi, X.shape[1]), X.reshape(-1, 3)).reshape(len(Pi), -1)
        lvl = f"F {prof[m.name][0]:.1f} mm from GH" if m.kind == "flat" else f"level {np.median(prof[m.name]):.1f} (min {prof[m.name].min():.1f} max {prof[m.name].max():.1f})"
        ib = ((d >= 2) & (d <= 14)).mean(1); worst = Pi[np.argsort(ib)[:4]]
        hi = d.mean(1) > 14
        print(f"  {m.name:6s} ib14 {r['inband_member'].get(m.name)} {lvl}; dist median {np.median(d):.1f} p90 {np.percentile(d, 90):.1f}; "
              f"poses mostly > 14 mm: {int(hi.sum())}/{len(Pi)} (elev of those: median {np.median(el[Pi[hi]]) if hi.any() else float('nan'):.0f})"
              + (f"; {where(m, None, int(Pi[0]))}" if m.kind == "flat" else ""))
        for j in worst: print(f"       worst {lab(int(j))}  ib {ib[list(Pi).index(j)]:.2f} median {np.median(d[list(Pi).index(j)]):.1f}")
    print("-- poses not taken (ok = closes + K2; hit = K6; contact = crown / wall) --")
    ok, hit = L["ok"], L["hit"]
    nt = [i for i in range(len(B.res)) if not _taken(B, i)]
    for i in nt[:40]:
        why = "fold/K2" if not ok[i] else ("K6 parts" if hit[i] else "contact")
        print(f"  {why:8s} {lab(i)}")
    print(f"  ... {len(nt)} not taken: fold/K2 {sum(not ok[i] for i in nt)}, K6 {sum(bool(ok[i] and hit[i]) for i in nt)}, contact {sum(bool(ok[i] and not hit[i]) for i in nt)}")
    low = sorted((float(np.min(B.res[j])), j) for j in range(len(B.res)) if _taken(B, j))[:6]
    print("-- closest metal (skin face) over taken poses --")
    for dd, j in low: print(f"  {dd:5.2f} mm {lab(j)}")
    groups = dict(rest=np.argsort(el)[:5], overhead=np.nonzero(el >= ELEV_OVER)[0], across=np.nonzero((pl >= 100) & (el >= 40))[0],
                  behind=np.array([i for i in range(len(B.idx)) if "back" in B.clip[i].lower() or (pl[i] < -30 and el[i] > 20)], int))
    print("-- named pose groups: taken / total, median metal-skin mm, in band 2-14 --")
    for g, ii in groups.items():
        ii = list(ii); tk = [i for i in ii if _taken(B, i)]; dd = np.concatenate([B.res[i] for i in tk]) if tk else np.array([np.nan])
        print(f"  {g:9s} {len(tk)}/{len(ii)}  median {float(np.nanmedian(dd)):.1f} mm  ib14 {float(((dd >= 2) & (dd <= 14)).mean()):.3f}")


def frozen(p0, out, overlap=1.0, fit=(60, 160), big=(110, 360)):
    """tools/concept_bigbench.py 'frozen' + the extras: fit on Bench(fit), freeze every underside, wear on Bench(big)"""
    coll = K.collisions; K.collisions = functools.partial(coll, overlap=overlap - 1e-4)
    res = dict(model=f"docs/concepts/models/{ID}.py", params=p0, overlap=overlap, exact=os.environ.get("CB_EXACT") == "1", runs={})
    Bf = K.bench(*fit); pf, rf = evaluate(Bf, dict(p0)); prof = {k: np.array(v) for k, v in Bf._kit_last["prof"].items()}
    keep = lambda r: {k: v for k, v in r.items() if _jsonable(v) and k not in ("checks",)}
    res["runs"]["fit"] = dict(keep(rf), bench=list(fit)); json.dump(res, open(out, "w"), indent=1, default=float)
    print("fit", {k: rf[k] for k in ("gap", "reach", "follow", "inband14", "contact", "honest")}, flush=True)
    Bb = K.bench(*big); fp = K.fit_profiles; t0 = time.time()
    K.fit_profiles = lambda B, chain, fit, q=1.0, mode="march": {k: v.copy() for k, v in prof.items()}
    try:
        r = K.evaluate(Bb, build, pf); r = extras(Bb, r)
    finally:
        K.fit_profiles = fp
    res["runs"]["frozen"] = dict(keep(r), bench=list(big), secs=round(time.time() - t0, 1))
    json.dump(res, open(out, "w"), indent=1, default=float)
    print("frozen", {k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "gap_near1", "min_metal_skin", "overhead")}, flush=True)
    if "--redteam" in sys.argv: redteam(Bb, pf, r)
    return res


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].startswith("{") else {}
    if mode == "frozen":
        o = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "frozen.json"
        frozen(dict(PARAMS, **par), o); sys.exit()
    B = K.bench(60, 160); t = time.time()
    p, r = evaluate(B, par)
    print({k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "audit", "closure", "flips", "collide")},
          f"{time.time() - t:.1f}s")
    print("per member", r["inband_member"], "mass", r["mass_g"], "res", r.get("residual_deg"), "margin", r.get("min_margin"))
    print("crowns: contact poses", r["crown_contact_poses"], "min", r["crown_min"], "| min metal-skin", r["min_metal_skin"],
          "face", r["min_face_skin"], "| gap near1", r["gap_near1"], r["near1"], "| overhead", r["overhead"])
    if mode == "redteam": redteam(B, p, r)
