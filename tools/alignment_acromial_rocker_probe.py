"""Alignment wear probe for acromial-rocker-3r: what the claim gives the wearer, read from the model's own run.

Two wears, both through the model UNCHANGED (only its audit() is wrapped, to capture (M, B)):
  fit60  : the row's claim itself - _report() on Bench(60,160) FAST (the stud refit included): reproduces v_gap 125.84
  bench  : the frozen shape - the model's frozen(): fit Bench(60,160) fast, worn on Bench(110,360) (CB_EXACT=1 -> exact)
Per wear it reads:
  - the fold margin in th (tools/concept_kit.py lines 25-30: th = angle(J1, J3) of the dyad, in the frame R0(q0)^T Q the
    model's ik() folds in) over the taken poses: min distance to either fold edge, poses within 5 / 10 deg;
  - the rod: q0 over taken poses vs its cap, the transmission angle (acos|x|, deg from the dead point; the model takes
    >= 25), U-joint bend vs its 40 deg rating, ball tilt vs 30;
  - overhead (elevation >= 140): taken / total for ws and clip, and the loss labels incl. 'rod' (the pin-knee audit's
    overhead why_not has no 'rod' key, so its counts read 0 while every overhead pose is lost);
  - contact poses: depth (-min metal) per pose with its plane / elevation / axial and the part that holds the minimum
    (rigid groups, link groups, the rod, or the model's contact walls), summed and max (T5);
  - a kinematic continuity flood (S5): nodes = taken workspace poses, edges = bench grid neighbours (one step in plane,
    elevation or axial, as tools/alignment_benchgraph_flood.py), each edge slerped in <= 2 deg steps and refused when
    any step leaves the rod limits (transmission / cap / ball / U) or the fold window, or moves q0, a knee pin or an
    active joint by > 10 deg (branch change / jump). Skin and part clashes along the edge are NOT checked, so the
    connected count is an upper bound. Seeds: taken workspace poses at elevation <= 30.
Writes docs/alignment/remeasure/acromial-rocker-3r_probe_<wear>.json (summary + the full per-pose dump) and
docs/alignment/remeasure/acromial-rocker-3r_bench_perpose[_fit60].json (the per-pose format tools/alignment_audit.py T5
and tools/alignment_benchgraph_flood.py read). Nothing is edited.

    OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_acromial_rocker_probe.py fit60
    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_acromial_rocker_probe.py bench
"""
import json, math, os, sys, time
import numpy as np
from scipy.spatial.transform import Rotation as Rot, Slerp

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import alignment_audit as AA                                  # noqa: E402
import concept_kit as KIT                                     # noqa: E402

RID = "acromial-rocker-3r"
JUMP, STEP, SEED = 10.0, 2.0, 30.0


def kin(D, Q):
    """per pose: ok (fold + knee + rod limits, as the model's ik), joint vector [q1, q2, q3 + phi, qa, qb, q0] (rad)"""
    q, ok, _, _, _, s = D.ik(Q); K = D.knee(s); ok = ok & K["ok"]
    q0 = D.rocker(Q)[0]
    return ok, np.c_[q[:, :2], q[:, 2] + K["phi"], K["qa"], K["qb"], q0]


def flood(D, B, tk, mod):
    ws = [i for i in range(len(B.idx)) if B.kind[i] == "ws"]
    P = {i: (B.poses[i]["plane"], B.poses[i]["elev"], B.poses[i]["axial"]) for i in ws}
    vals = [sorted({P[i][d] for i in ws}) for d in range(3)]
    node = {P[i]: i for i in ws if tk[i]}
    Qall = mod.CB._poses_all()["HG"][B.idx].astype(float)
    wrap = lambda a: (a + np.pi) % (2 * np.pi) - np.pi
    cache = {}

    def edge(a, b):
        k = (min(a, b), max(a, b))
        if k in cache: return cache[k]
        Ra, Rb = Rot.from_matrix(Qall[a]), Rot.from_matrix(Qall[b])
        ang = float(np.degrees((Ra.inv() * Rb).magnitude())); n = max(2, int(math.ceil(ang / STEP)) + 1)
        sl = Slerp([0.0, 1.0], Rot.concatenate([Ra, Rb])); Qs = sl(np.linspace(0, 1, n)).as_matrix()
        ok, qq = kin(D, Qs)
        good = bool(ok.all()) and float(np.degrees(np.abs(wrap(np.diff(qq, axis=0)))).max()) <= JUMP
        cache[k] = good; return good

    def nb(x):
        for d in range(3):
            j = vals[d].index(x[d])
            for jj in (j - 1, j + 1):
                if 0 <= jj < len(vals[d]):
                    y = list(x); y[d] = vals[d][jj]; y = tuple(y)
                    if y in node: yield y
    seeds = {x for x in node if x[1] <= SEED}
    def run(check):
        conn = set(seeds); front = list(conn)
        while front:
            nxt = []
            for a in front:
                for b in nb(a):
                    if b not in conn and (not check or edge(node[a], node[b])): conn.add(b); nxt.append(b)
            front = nxt
        return conn
    up = run(False); kc = run(True)
    nws = len(ws); lost = sorted(set(node) - kc)
    return dict(ws=nws, taken=len(node), seeds=len(seeds), graph_upper=len(up), kin_connected=len(kc),
                reach_static=round(len(node) / nws, 4), reach_graph_upper=round(len(up) / nws, 4), reach_kin_connected=round(len(kc) / nws, 4),
                edges_checked=len(cache), edges_refused=int(sum(1 for v in cache.values() if not v)),
                islands=[dict(plane=x[0], elev=x[1], axial=x[2]) for x in lost][:40],
                note="upper bound: skin / part clashes along the slerped edges are not checked; bench grid graph (sparse), not the envelope flood")


def main():
    wear = sys.argv[1] if len(sys.argv) > 1 else "bench"
    assert wear in ("fit60", "bench")
    P = dict(json.load(open(os.path.join(AA.ROWS, RID + ".json"))).get("best_params") or {})
    mod = AA._load("aa_acr_probe", os.path.join(AA.MODELS, RID + ".py"))
    pk = mod.PK; orig = pk.audit; box = {}

    def wrapped(M, B):
        box["M"], box["B"] = M, B; return orig(M, B)
    pk.audit = wrapped
    t = time.time()
    try:
        if wear == "bench":
            r = mod.frozen(P); head = r.get("frozen")
        else:
            old = os.environ.pop("CB_EXACT", None)
            try: B0 = mod.CB.Bench(n_clip=60, n_ws=160)
            finally:
                if old is not None: os.environ["CB_EXACT"] = old
            r0, _ = mod._report(B0, dict(P)); head = {k: r0[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
            r = dict(frozen=head, why=r0.get("why"))
    finally:
        pk.audit = orig
    M, B = box["M"], box["B"]; D = M.D; n = len(B.idx)
    taken = np.array([B.res[i] is not None and float(np.min(B.res[i])) >= 0 for i in range(n)])
    nonnull = np.array([B.res[i] is not None for i in range(n)])
    mins = np.array([float(np.min(B.res[i])) if B.res[i] is not None else np.nan for i in range(n)])
    q0, okr, A, C, tb, tu = D.rocker(M.Q); R0 = mod.S.rotm(D.cp, q0)
    Qp = np.einsum("nji,njk->nik", R0, M.Q); u1, u2, u3 = D.u
    th = np.degrees(np.arccos(np.clip((Qp @ u3) @ u1, -1, 1)))
    a1, a2 = np.degrees(D.A[0]), np.degrees(D.A[1]); lo = abs(a1 - a2); hi = min(a1 + a2, 360 - a1 - a2)
    marg = np.minimum(th - lo, hi - th)
    x, _ = D._x(M.Q @ D.C0); trans = np.degrees(np.arccos(np.clip(np.abs(x), 0, 1)))
    el = np.array([p["elev"] for p in B.poses]); pl = np.array([p["plane"] for p in B.poses]); ax = np.array([p["axial"] for p in B.poses])
    kind = np.array(B.kind); why = np.array([str(w) for w in M.why]); tk = taken
    # sample layout of B.res[i]: rigid groups, link groups, rod (2 rows), [+ the contact-wall minimum when it was < 0]
    names = list(M.rigid) + list(M.link_pts); sizes = [len(X) for _, X in M.rigid.values()] + [len(X) for _, X in M.link_pts.values()]
    cut = np.cumsum([0] + sizes); nb_ = int(cut[-1])

    def part_of(i):
        d = B.res[i]; j = int(np.argmin(d))
        if j < nb_: return names[int(np.searchsorted(cut, j, side="right") - 1)]
        nrod = 2 * max(2, int(np.linalg.norm(M.Crod[i] - M.Arod[i]) / mod.S.SPACING))
        return "rod" if j < nb_ + nrod else "contact-wall"

    def rng(a):
        return [round(float(np.nanmin(a[tk])), 2), round(float(np.nanmax(a[tk])), 2)] if tk.any() else None
    ov = el >= 140; raised = el >= 90
    over = dict(ws=[int((tk & ov & (kind == "ws")).sum()), int((ov & (kind == "ws")).sum())],
                clip=[int((tk & ov & (kind == "clip")).sum()), int((ov & (kind == "clip")).sum())],
                why={w: int(((why == w) & ov & ~tk).sum()) for w in sorted(set(why[ov & ~tk]))},
                q0_lost_deg=[round(float(np.degrees(np.nanmin(q0[ov]))), 1), round(float(np.degrees(np.nanmax(q0[ov]))), 1)] if ov.any() else None,
                u_bend_lost_p50=round(float(np.median(tu[ov])), 1) if ov.any() else None,
                trans_lost_p50=round(float(np.median(trans[ov])), 1) if ov.any() else None)
    cont = nonnull & (mins < 0)
    depths = sorted(([round(-float(mins[i]), 2), dict(i=int(i), kind=str(kind[i]), plane=round(float(pl[i]), 1), elev=round(float(el[i]), 1),
                                                      axial=round(float(ax[i]), 1), part=part_of(i))] for i in np.nonzero(cont)[0]), key=lambda z: -z[0])
    parts_hit = {}
    for d_, p_ in depths: parts_hit[p_["part"]] = parts_hit.get(p_["part"], 0) + 1
    fl = flood(D, B, tk, mod)
    dump = [dict(i=int(i), kind=str(kind[i]), plane=round(float(pl[i]), 1), elev=round(float(el[i]), 1), axial=round(float(ax[i]), 1),
                 taken=bool(tk[i]), contact=bool(cont[i]), why=str(why[i]), min_mm=None if np.isnan(mins[i]) else round(float(mins[i]), 3),
                 th_margin=round(float(marg[i]), 2), q0=round(float(np.degrees(q0[i])), 2), u_bend=round(float(tu[i]), 2), trans=round(float(trans[i]), 2),
                 part_min=part_of(i) if B.res[i] is not None else None) for i in range(n)]
    out = dict(id=RID, wear="bench", protocol=wear, mode=B.mode, frozen=head, fit_fast=r.get("fit_fast"), why=r.get("why"), fold_margin_rule=KIT.FOLD_MARGIN,
               dyad=dict(a1=round(a1, 2), a2=round(a2, 2), window_no_margin=[round(lo, 2), round(hi, 2)]),
               th_margin_taken=dict(min=round(float(marg[tk].min()), 2) if tk.any() else None, within5=int((tk & (marg < 5)).sum()),
                                    within10=int((tk & (marg < 10)).sum()), n_taken=int(tk.sum())),
               rod_taken=dict(q0_deg=rng(np.degrees(q0)), cap=P.get("cap"), u_bend_deg=rng(tu), u_rating=P.get("uj"),
                              u_bend_ge35=int((tk & (tu >= 35)).sum()), u_bend_ge38=int((tk & (tu >= 38)).sum()), ball_tilt_deg=rng(tb), ball_rating=P.get("ball"),
                              transmission_min_deg=round(float(trans[tk].min()), 2) if tk.any() else None, transmission_rule=P.get("trans"),
                              trans_lt30=int((tk & (trans < 30)).sum())),
               overhead140=over, raised90=dict(ws=[int((tk & raised & (kind == "ws")).sum()), int((raised & (kind == "ws")).sum())],
                                               clip=[int((tk & raised & (kind == "clip")).sum()), int((raised & (kind == "clip")).sum())]),
               contact=dict(n=int(cont.sum()), of=int(nonnull.sum()), sum_mm=round(float(sum(d for d, _ in depths)), 2),
                            max_mm=depths[0][0] if depths else 0.0, deeper3=int(sum(1 for d, _ in depths if d > 3)), parts=parts_hit, poses=depths),
               continuity=fl, secs=round(time.time() - t, 1), exact=os.environ.get("CB_EXACT") == "1", git=AA._git("rev-parse", "--short", "HEAD"))
    os.makedirs(AA.REM, exist_ok=True)
    json.dump(dict(out, dump=dump), open(os.path.join(AA.REM, f"{RID}_probe_{wear}.json"), "w"), indent=1, default=float)
    suf = "_fit60" if wear == "fit60" else ""
    json.dump(dict(id=RID, wear="bench", protocol=wear, mode=B.mode, frozen=head, poses=dump, src="tools/alignment_acromial_rocker_probe.py"),
              open(os.path.join(AA.REM, f"{RID}_bench_perpose{suf}.json"), "w"), default=float)
    print(json.dumps({k: v for k, v in out.items() if k != "contact"}, default=float)[:3500])
    print(json.dumps({k: v for k, v in out["contact"].items() if k != "poses"}, default=float), out["contact"]["poses"][:6])


if __name__ == "__main__":
    main()
