"""fivebar-roll: spherical five-bar pointer (two scapula-driven cranks + two couplers closing on one arm hub at the
arm-fixed axis W) plus an active roll of the arm about W. Spec: docs/concepts/catalogue.json entry "fivebar-roll";
notes and results: docs/concepts/fivebar-roll.md. Built on the shared kit (tools/concept_kit.py, docs/concepts/KIT.md).

Topology (scapula handler -> user's upper-arm cuff), every joint axis through the GH centre:
    S -- A1 O20 hub, axis u1 (ACTIVE) -> crank 1 (arc a1) -- B1 elbow pin, axis e1 (passive) -> coupler 1 (arc c1) --+
    S -- A2 O20 hub, axis u2 (ACTIVE) -> crank 2 (arc a2) -- B2 elbow pin, axis e2 (passive) -> coupler 2 (arc c2) --+
         arm hub at W (two bearing rows): C = coupler 2 about coupler 1 (passive), D = arm about coupler 1 (ACTIVE roll)
         -> arm-end plate + K7 neck to BOTTOM's bar.
    coaxial variant (coax=True): u1 = u2, one double-row base hub (r 12, crown 16), crank 2 stacked over crank 1.
DOF (spherical Gruebler): 6 bodies (S, crank 1, crank 2, coupler 1, coupler 2, arm), 6 revolutes: 3 (6-1-6) + 6 = 3.
Given the arm pose, W = RS HG w0 is known; e_k = two-cone closure (a_k about u_k, c_k about W, branch s_k); C and D
follow, so every passive coordinate (B1, B2, C) is set by the closure (R17). Kept out: leg singularities (closure
margin `margin`), the loop's parallel singularity (|n1 x n2| >= sin `par`, n_k = unit(e_k x W)), elbows < `sep` apart.

Hardware at real size: base hubs O20 (kit K4, r 10, crown 12.25; coaxial: r 12, crown 16); elbows P14 pins (one MR126
in an O14 housing: flat disc r 7, crown 8, crank the lower member at F, coupler at F + 3.15) - declared hubless
(they are not O20 hubs, they are smaller pins by design; the disc is a member at its real size); arm hub at W r 12,
crown 16.3 (arm plate at F, coupler 1 at F + 3.15, coupler 2 at F + 6.3); cranks 12 x 3 straps, couplers `wc` x 3
straps (default 10), K7 neck 14 x 6. Couplers pass OVER the cranks and the neck (and coupler 2 over coupler 1) by
construction (`over`); K6 then checks every pair anyway.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/fivebar-roll.py            # PARAMS on Bench(60,160)
    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/fivebar-roll.py kin        # kinematic prefilter (no skin)
    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/fivebar-roll.py sweep [--write]
"""
import itertools, json, os, sys
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402

ID = "fivebar-roll"
NAME = "Spherical five-bar pointer plus an active arm roll"
SWEEP_JSON = os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json")
PIN_R, PIN_T = 7.0, 8.0                                      # P14 elbow pin disc
WH_R, WH_T = 11.9, 2 * K.STACK + 10.0                        # arm hub at W: two rows, crown 16.3
CX_R, CX_T = 11.9, 16.0                                      # coaxial double base hub

PARAMS = dict(u1az=-60.0, u1el=40.0, u2az=-40.0, u2el=40.0, coax=False, a1=60.0, a2=60.0, c1=120.0, c2=120.0,
              wd=60.0, wa=30.0, s1=1, s2=-1, margin=8.0, par=12.0, sep=17.0, wc=10.0, q=1.0)
SWEEP = "coarse kinematic prefilter over u1, u2 (incl. coaxial), a, c, W, branches -> bench sweep of the best ~60, refined"


def _ref(u):
    """a scapula-frame direction orthogonal to u (the zero of the base joint angle)"""
    u = np.asarray(u, float); r = np.cross(u, [0.0, 0.0, 1.0])
    return K.unit(r if np.linalg.norm(r) > 0.2 else np.cross(u, [1.0, 0.0, 0.0]))


def kin(F, p):
    """axes (P, 3) thorax and validity: u1, u2, e1, e2, W, ok, q (P, 6) deg, closure residual"""
    l1 = K.bvec(p["u1az"], p["u1el"]); l2 = l1 if p["coax"] else K.bvec(p["u2az"], p["u2el"])
    u1, u2 = F.S(l1), F.S(l2); W = F.HG(K.wdir(p["wd"], p["wa"]))
    e1, ok1, m1 = K.closure(u1, W, p["a1"], p["c1"], p["s1"], margin_deg=p["margin"])
    e2, ok2, m2 = K.closure(u2, W, p["a2"], p["c2"], p["s2"], margin_deg=p["margin"])
    n1, n2 = K.unit(np.cross(e1, W)), K.unit(np.cross(e2, W))
    okp = np.linalg.norm(np.cross(n1, n2), axis=-1) >= np.sin(np.radians(p["par"]))
    oks = np.degrees(np.arccos(np.clip((e1 * e2).sum(-1), -1, 1))) >= p["sep"]
    ok = ok1 & ok2 & okp & oks
    q = np.stack([K.axis_angle(u1, F.S(_ref(l1)), e1), K.axis_angle(u2, F.S(_ref(l2)), e2),
                  K.axis_angle(e1, u1, W), K.axis_angle(e2, u2, W),
                  K.axis_angle(W, e1, e2), K.axis_angle(W, F.HG([0.0, -1.0, 0.0]), e1)], -1)
    res = np.maximum(K.closure_residual(u1, W, e1, p["a1"], p["c1"]), K.closure_residual(u2, W, e2, p["a2"], p["c2"]))
    return dict(u1=u1, u2=u2, e1=e1, e2=e2, W=W, ok=ok, q=q, res=res, okl=ok1 & ok2, okp=okp, oks=oks,
                margin=np.minimum(m1, m2))


def build(B, F, p):
    k = kin(F, p); u1, u2, e1, e2, W, ok = (k[x] for x in ("u1", "u2", "e1", "e2", "W", "ok"))
    if p["coax"]:
        hubs = [K.hub_member("hubA", u1, "A1", t=CX_T, rad=CX_R)]
        hubs[0].joints = ("A1", "A2"); hA1, hA2, dz2 = "hubA", "hubA", 2 * K.STACK
    else:
        hubs = [K.hub_member("hubA1", u1, "A1"), K.hub_member("hubA2", u2, "A2")]; hA1, hA2, dz2 = "hubA1", "hubA2", K.STACK
    hubs += [K.hub_member("pinB1", e1, "B1", t=PIN_T, rad=PIN_R), K.hub_member("pinB2", e2, "B2", t=PIN_T, rad=PIN_R),
             K.hub_member("hubW", W, "W", t=WH_T, rad=WH_R)]
    cr = [K.strap_member("crank1", u1, e1, ("A1", "B1"), ramp_to=((hA1, K.STACK), ("pinB1", 0.0))),
          K.strap_member("crank2", u2, e2, ("A2", "B2"), ramp_to=((hA2, dz2), ("pinB2", 0.0)),
                         over=[("crank1", 1.0)] if p["coax"] else [])]
    neck = K.neck_member(F, W, joints=("W",), ramps=(("hubW", 0.0), (None, 0)))
    cp = [K.strap_member("coupler1", e1, W, ("B1", "W"), width=p["wc"], ramp_to=(("pinB1", K.STACK), ("hubW", K.STACK)),
                         over=[("crank1", 1.0), ("crank2", 1.0), ("neck", 1.0)]),
          K.strap_member("coupler2", e2, W, ("B2", "W"), width=p["wc"], ramp_to=(("pinB2", K.STACK), ("hubW", 2 * K.STACK)),
                         over=[("crank1", 1.0), ("crank2", 1.0), ("neck", 1.0), ("coupler1", 1.0)])]
    info = dict(residual_deg=round(float(k["res"][ok].max()), 6) if ok.any() else None,
                min_margin=round(float(k["margin"][ok].min()), 2) if ok.any() else None)
    return K.Chain(members=hubs + cr + [neck] + cp, ok=ok, q=k["q"], info=info, hubless=("B1", "B2"),
                   joints=dict(A1=u1, A2=u2, B1=e1, B2=e2, W=W))


def kin_screen(B, F, p):
    """kinematic share (no skin): closes, all singularity margins, and dense continuity along the clips"""
    ch = build_kin(B, F, p); ok = ch.ok
    ok2, flips = K.continuity_dense(B, F, build_kin, p, ok)
    return float(ok[F.ws].mean()), float(ok2[F.clip].mean())


def build_kin(B, F, p):
    k = kin(F, p)
    return K.Chain(members=[], ok=k["ok"], q=k["q"], joints=dict(A1=k["u1"], A2=k["u2"], B1=k["e1"], B2=k["e2"], W=k["W"]))


def evaluate(B, p, **kw):
    return K.evaluate(B, build, p, **kw)


# ---- skin-aware kinematic prefilter (how the bench configurations were chosen; not a judge) ------------------------
def prefilter(B, n=9000, seed=7, out=None):
    """random configurations scored by a cheap surrogate: the K3 march requirement on a 3-deg scapula-frame direction
    grid in every bench pose (the posed skin itself), member centre lines + strap edges looked up per pose, rigid level
    = max over the closing poses, 'in band' = level - requirement + 2 in [2, 14]; + 1 per mm of any member level over
    110 mm (an over-high member drags the couplers up through `over`). Returns the sorted list."""
    F = K.frames(B); P = len(F.RS); pi = np.arange(P); AZ = np.arange(-180, 180, 3.0); EL = np.arange(-60, 90.1, 3.0)
    A_, E_ = np.meshgrid(AZ, EL, indexing="ij"); D = K.bvec(A_.ravel(), E_.ravel())
    R = K.requirement(B, np.repeat(pi, len(D)), F.S(D).reshape(-1, 3), t1=200.0).reshape(P, len(D)); R[~np.isfinite(R)] = 400.0
    HGs = np.einsum("pji,pjk->pik", F.RS, F.RHG); BAR = np.einsum("pji,pjk->pik", F.RS, F.RH) @ K.unit(K.BAR0_H)

    def look(v):
        el = np.degrees(np.arcsin(np.clip(v[..., 1], -1, 1))); az = np.degrees(np.arctan2(v[..., 2], -v[..., 0]))
        ia = np.round((az + 180) / 3).astype(int) % len(AZ); ie = np.clip(np.round((el + 60) / 3).astype(int), 0, len(EL) - 1)
        return R[pi[:, None], ia * len(EL) + ie]

    def arc(u, v):
        u, v = K.unit(u), K.unit(v); ang = np.arccos(np.clip((u * v).sum(-1), -1, 1)); m = max(3, int(np.degrees(np.median(ang)) / 3) + 1)
        th = np.linspace(0, 1, m)[None] * ang[:, None]; e2 = K.unit(np.cross(np.cross(u, v), u))
        return np.cos(th)[..., None] * u[:, None] + np.sin(th)[..., None] * e2[:, None]

    def surrogate(p):
        l1 = K.bvec(p["u1az"], p["u1el"]); l2 = l1 if p["coax"] else K.bvec(p["u2az"], p["u2el"])
        u1, u2 = np.broadcast_to(l1, (P, 3)), np.broadcast_to(l2, (P, 3)); W = HGs @ K.wdir(p["wd"], p["wa"])
        e1, o1, _ = K.closure(u1, W, p["a1"], p["c1"], p["s1"], p["margin"]); e2, o2, _ = K.closure(u2, W, p["a2"], p["c2"], p["s2"], p["margin"])
        n1, n2 = K.unit(np.cross(e1, W)), K.unit(np.cross(e2, W))
        ok = o1 & o2 & (np.linalg.norm(np.cross(n1, n2), axis=-1) >= np.sin(np.radians(p["par"]))) & \
            (np.degrees(np.arccos(np.clip((e1 * e2).sum(-1), -1, 1))) >= p["sep"])
        if ok.sum() < 10: return None
        ib, lv = [], []
        for j, m in enumerate([arc(u1, e1), arc(u2, e2), arc(e1, W), arc(e2, W), arc(W, BAR), u1[:, None], u2[:, None], e1[:, None], e2[:, None], W[:, None]]):
            r = look(m)
            if j < 5:
                nrm = K.unit(np.cross(m[:, :1], m[:, -1:]))
                for sg in (-1, 1): r = np.maximum(r, look(K.unit(m + sg * 0.086 * nrm)))
            lev = r[ok].max(0); d = lev[None] - r[ok] + 2; ib.append(((d <= 14) & (d >= 2)).reshape(ok.sum(), -1)); lv.append(float(lev.mean()))
        i14 = float(np.concatenate(ib, 1)[F.clip[ok]].mean()); ws, cl = float(ok[F.ws].mean()), float(ok[F.clip].mean())
        return dict(ws=ws, clip=cl, ib=i14, lv=lv, gap=100 * (max(0, .9 - i14) + max(0, .95 - cl) + max(0, .9 - ws)) + sum(max(0.0, x - 110) for x in lv))

    rng = np.random.default_rng(seed); res = []
    Ws = [(60, 30), (71.38, 4.78), (86.3, 21.8), (90, 0), (100, 20), (112, -15), (75, -20), (80, 45), (60, 0), (100, -30)]
    for _ in range(n):
        p = dict(PARAMS, coax=bool(rng.random() < 0.3), u1az=float(rng.uniform(-180, 180)), u1el=float(rng.uniform(-30, 85)),
                 u2az=float(rng.uniform(-180, 180)), u2el=float(rng.uniform(-30, 85)), a1=float(rng.choice(np.arange(25, 95, 5))),
                 a2=float(rng.choice(np.arange(25, 95, 5))), c1=float(rng.choice(np.arange(25, 115, 5))), c2=float(rng.choice(np.arange(25, 115, 5))),
                 s1=int(rng.choice([-1, 1])), s2=int(rng.choice([-1, 1])))
        p["wd"], p["wa"] = Ws[rng.integers(len(Ws))]
        if p["coax"]: p.update(u2az=p["u1az"], u2el=p["u1el"])
        elif np.degrees(np.arccos(np.clip(K.bvec(p["u1az"], p["u1el"]) @ K.bvec(p["u2az"], p["u2el"]), -1, 1))) < 22: continue   # two O20 hubs overlap
        sc = surrogate(p)
        if sc: res.append(dict(sc, p=p))
    res.sort(key=lambda x: x["gap"])
    if out: json.dump(res[:300], open(out, "w"))
    return res


if __name__ == "__main__":
    a = sys.argv[1:]
    B = K.bench(60, 160)
    if not a:
        r = evaluate(B, PARAMS); print(json.dumps({x: r[x] for x in r if x not in ("sample_mm",)}, default=str))
    elif a[0] == "sweep":                          # sweep <configs.json>: appends to the sweep file (resume, in order)
        cfg = [dict(PARAMS, **c) for c in json.load(open(a[1]))]
        best, rows = K.sweep(B, build, cfg, SWEEP_JSON, resume=True)
        print("BEST", best)
    elif a[0] == "prefilter":                      # prefilter <out.json> [n] [seed]
        r = prefilter(B, int(a[2]) if len(a) > 2 else 9000, int(a[3]) if len(a) > 3 else 7, a[1])
        for e in r[:15]: print(round(e["gap"], 1), round(e["ws"], 3), round(e["clip"], 3), round(e["ib"], 3), e["p"])
    elif a[0] == "write":                          # write <k>: re-evaluate sweep entry k and write the row
        rows = json.load(open(SWEEP_JSON)); e = rows[int(a[1])]
        r = evaluate(B, e["params"]); print(json.dumps({x: r[x] for x in r if x not in ("sample_mm",)}, default=str))
        K.write_row(ID, NAME, r, lens="closed-loop", family="spherical five-bar + roll", active_dof=3, passive_dof=3,
                    n_configs=len(rows), verdict=a[2] if len(a) > 2 else "", note=f"best sweep entry k={e['k']}: {e['params']}",
                    doc="docs/concepts/fivebar-roll.md", status=a[3] if len(a) > 3 else "screened",
                    limiter=a[4] if len(a) > 4 else "")
