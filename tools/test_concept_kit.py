"""pytest for tools/concept_kit.py: each kit helper against a brute-force reference.
    OMP_NUM_THREADS=1 python3 -m pytest -q tools/test_concept_kit.py"""
import math, os, sys
import numpy as np
import pytest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import concept_kit as K                                       # noqa: E402
import concept_baseline as BL                                 # noqa: E402

RNG = np.random.default_rng(3)


@pytest.fixture(scope="module")
def B():
    return K.bench(60, 160)                                   # fast grid cache if built, else the exact libigl path


def ang(x, y): return np.degrees(np.arccos(np.clip((K.unit(x) * K.unit(y)).sum(-1), -1, 1)))


# ---- K0 ------------------------------------------------------------------------------------------------------------
def test_directions_match_band_impl():
    for az, el in ((0, 0), (90, 30), (-120, 75), (2.43, 80.7)):
        assert np.allclose(K.bvec(az, el), BL.bvec(az, el))
    for d, a in ((86.3, 21.8), (10, -90), (150, 180)):
        assert np.allclose(K.wdir(d, a), BL.w_dir(d, a))
    assert np.allclose(K.bvec(0, 0), [-1, 0, 0]) and np.allclose(K.bvec(90, 0), [0, 0, 1])   # posterior, lateral


def test_frames_match_bench(B):
    F = K.frames(B)
    for i in (0, 37, 150):
        f = B.frames(i); assert np.allclose(F.RS[i], f["S"][0], atol=1e-6) and np.allclose(F.RH[i], f["H"][0], atol=1e-6)


# ---- K1 ------------------------------------------------------------------------------------------------------------
def brute_closure(b, w, a1, a2, n=200000):
    """all points on the circle at a1 from b whose angle to w is a2 (sign changes on a fine circle)"""
    e1 = K.unit(np.cross(b, [0.3, 0.5, 0.7])); e2 = np.cross(b, e1); t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    C = math.cos(a1 * K.D2R) * b + math.sin(a1 * K.D2R) * (np.cos(t)[:, None] * e1 + np.sin(t)[:, None] * e2)
    f = ang(C, w) - a2; s = np.nonzero(np.sign(f) != np.sign(np.roll(f, -1)))[0]
    return C[s]


@pytest.mark.parametrize("seed", range(6))
def test_closure_vs_brute_force(seed):
    rng = np.random.default_rng(seed); P = 300
    b = K.unit(rng.normal(size=(P, 3))); w = K.unit(rng.normal(size=(P, 3))); a1, a2 = rng.uniform(20, 120, 2)
    for sigma in (1, -1):
        p, ok, margin = K.closure(b, w, a1, a2, sigma, margin_deg=0.5)
        assert ok.any() and (~ok).any()
        assert K.closure_residual(b, w, p, a1, a2)[ok].max() < 1e-5
        assert np.all(np.sign((p * np.cross(b, w)).sum(-1))[ok] == sigma)
        th = ang(b, w); geo = (th > abs(a1 - a2)) & (th < min(a1 + a2, 360 - a1 - a2))
        assert np.all(ok <= geo) and np.all(geo[margin >= 0.5] == ok[margin >= 0.5])
        for k in np.nonzero(ok)[0][:15]:                     # the brute-force roots contain p
            R = brute_closure(b[k], w[k], a1, a2); assert len(R) == 2 and np.min(np.linalg.norm(R - p[k], axis=1)) < 2e-4


def test_closure_near_degenerate():
    b = np.array([[0, 1.0, 0]] * 4); a1, a2 = 60.0, 40.0
    w = K.unit(np.array([[1e-7, 1, 0], [math.sin(20.05 * K.D2R), math.cos(20.05 * K.D2R), 0],     # b ~ w; |a1-a2| + 0.05
                         [math.sin(99.9 * K.D2R), math.cos(99.9 * K.D2R), 0], [math.sin(60 * K.D2R), math.cos(60 * K.D2R), 0]]))
    p, ok, margin = K.closure(b, w, a1, a2, 1, margin_deg=5.0)
    assert list(ok) == [False, False, False, True]
    p0, ok0, _ = K.closure(b, w, a1, a2, 1, margin_deg=0.0)  # tangent cases still accurate when allowed
    assert ok0[1] and ok0[2] and K.closure_residual(b, w, p0, a1, a2)[1:].max() < 1e-3


# ---- K2 ------------------------------------------------------------------------------------------------------------
class FakeB:
    def clip_order(self): return {"a": [0, 1, 2, 3, 4], "b": [5, 6, 7]}


def test_continuity_flags_constructed_flip():
    q = np.array([[0, 0], [10, 5], [80, 6], [20, 7], [30, 8], [170, 0], [-175, 3], [-160, 4]], float)
    ok, flips = K.continuity(FakeB(), q, np.ones(8, bool))
    assert list(ok) == [True, True, False, True, True, True, True, True] and flips == 1   # 170 -> -175 wraps: 15 deg
    ok, flips = K.continuity(FakeB(), q, np.array([1, 0, 1, 1, 1, 1, 1, 1], bool))
    assert not ok[2] and ok[3] and flips == 1                # compared with the previous TAKEN frame


def test_dense_continuity_catches_branch_flip(B):
    """a chain that takes branch +1 when the arm is high and -1 when low flips along the clips; on one branch it does not"""
    F = K.frames(B); thr = float(np.median(F.HG(K.wdir(86, 22))[F.clip, 1]))
    def build(switch):
        def f(_B, Fr, p):
            p1 = Fr.S(K.bvec(0, 80)); p3 = Fr.HG(K.wdir(86, 22))
            pa, oka, _ = K.closure(p1, p3, 77, 67, 1, 0); pb, okb, _ = K.closure(p1, p3, 77, 67, -1, 0)
            hi = (p3[:, 1] > thr) if switch else np.zeros(len(p3), bool)
            p2 = np.where(hi[:, None], pa, pb)
            return K.Chain(members=[], ok=oka & okb, q=K.axis_angle(p1, Fr.S([1.0, 0, 0]), p2)[:, None])
        return f
    ok = build(False)(B, F, {}).ok
    ok0, f0 = K.continuity_dense(B, F, build(False), {}, ok)
    ok1, f1 = K.continuity_dense(B, F, build(True), {}, ok)
    assert f1 > f0 and ok1.sum() < ok0.sum()


# ---- K3 ------------------------------------------------------------------------------------------------------------
def brute_requirement(B, i, D, t0=15, t1=220, clr=2.0, win=15):
    t = np.arange(t0, t1 + win + 1, 1.0); d = B.dist(i, D[:, None, :] * t[None, :, None]); out = np.full(len(D), np.inf)
    for k in range(len(D)):
        for j in range(t1 - t0 + 1):
            if d[k, j] >= clr and d[k, j:j + win + 1].min() >= 0: out[k] = t[j]; break
    return out


def test_requirement_march_vs_brute_force(B):
    rng = np.random.default_rng(5); n = 150
    for i in (0, 25, 70, 190):                                # rest, clip, workspace poses
        D = K.unit(rng.normal(size=(n, 3)) + np.array([0, 0.6, 0.4]))
        r = K.requirement(B, np.full(n, i), D); rb = brute_requirement(B, i, D)
        same = (r == rb) | (np.isinf(r) & np.isinf(rb))
        assert same.mean() >= 0.98, (i, same.mean())
        fin = np.isfinite(r) & np.isfinite(rb); assert np.abs(r - rb)[fin].max() <= 2.0


def test_requirement_outer_matches_baseline(B):
    rng = np.random.default_rng(6); D = K.unit(rng.normal(size=(200, 3)) + np.array([0, 0.6, 0.4]))
    for i in (3, 120):
        assert np.allclose(K.requirement(B, np.full(200, i), D, mode="outer"), BL.skin_radius(B, i, D) + 2.0)


def test_dist_many_equals_bench_dist(B):
    rng = np.random.default_rng(7); I = rng.integers(0, len(B.kind), 3000); P = rng.normal(size=(3000, 3)) * 90
    P[:20] *= 4                                               # some outside the grid box -> exact fallback
    d = K.dist_many(B, I, P)
    ref = np.empty(3000)
    for i in np.unique(I): ref[I == i] = B.dist(int(i), P[I == i])
    assert np.allclose(d, ref, atol=1e-4)


# ---- K6 ------------------------------------------------------------------------------------------------------------
def two_members(sep_deg, r_a, r_b, shared=False):
    P = 2; k = np.tile([0, 1.0, 0], (P, 1)); a, b = K.plane_frame(k)
    def strap(az0):
        t = np.radians(np.linspace(-20, 20, 21)); c = np.radians(az0)
        return K.unit(np.cos(t)[None, :, None] * k[:, None] + np.sin(t)[None, :, None] * (math.cos(c) * a + math.sin(c) * b)[:, None])
    A = K.Member("A", strap(0), joints=("J",) if shared else ("J1",)); Bm = K.Member("B", strap(sep_deg), joints=("J",) if shared else ("J2",))
    ch = K.Chain(members=[A, Bm], ok=np.ones(P, bool), joints=dict(J=k))
    pts = {"A": A.D * r_a, "B": Bm.D * r_b}
    return K.collisions(ch, pts, ch.ok)


def test_collisions_constructed():
    assert two_members(0, 70, 71).all()                      # same place, overlapping radial intervals: hit
    assert not two_members(0, 70, 80).any()                  # stacked 10 mm apart: miss
    assert not two_members(0, 70, 74).any()                  # 4 mm apart (3 mm thick + 0.5): miss
    assert two_members(0, 70, 73.4).all()                    # 3.4 mm apart: within the 0.5 mm overlap margin: hit
    # crossing straps at 90 deg share only the centre region (the joint): exempt when partners, hit when not
    assert two_members(90, 70, 70.5).all() and not two_members(90, 70, 70.5, shared=True).any()


def test_baseline_kit_reproduces_row(B):
    import importlib.util, json
    p = os.path.join(K.REPO, "docs", "concepts", "models", "baseline-3r-kit.py")
    spec = importlib.util.spec_from_file_location("bk", p); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
    r = K.evaluate(B, M.build, M.PARAMS, **M.BASELINE)
    row = json.load(open(os.path.join(K.REPO, "docs", "concepts", "rows", "baseline-3r.json")))
    if B.mode == "fast" and len(B.kind) == 220: assert abs(r["gap"] - row["gap"]) <= 1.0
    assert r["closure"] > 0.9 and r["flips"] == 0


def test_over_clears_by_construction():
    P = 2; k = np.tile([0, 1.0, 0], (P, 1)); a, b = K.plane_frame(k); t = np.radians(np.linspace(-20, 20, 21))
    D = K.unit(np.cos(t)[None, :, None] * k[:, None] + np.sin(t)[None, :, None] * a[:, None])
    A = K.Member("A", D, joints=("J1",)); Bm = K.Member("B", D.copy(), joints=("J2",), over=[("A", 1.0)])
    ch = K.Chain(members=[A, Bm], ok=np.ones(P, bool), joints={})
    r = K._over(ch, Bm, np.full(21, 70.0), {"A": np.full(21, 70.0)}, ch.ok)
    assert np.allclose(r, 74.0)                              # A's top (70 + 3) + 1 mm
    pts = {"A": D * 70.0, "B": D * r[None, :, None]}
    assert not K.collisions(ch, pts, ch.ok).any() and K.collisions(ch, {"A": D * 70.0, "B": D * 71.0}, ch.ok).all()


def _fixed_levels(monkeypatch, raw):
    """fit_profiles on given raw undersides (no bench): K._levels returns copies of raw {member name: rho (m,)}"""
    monkeypatch.setattr(K, "_levels", lambda B, chain, fit, q, mode: {n: np.array(r, float) for n, r in raw.items()})


def _k6(ch, prof):
    return K.collisions(ch, {m.name: K.member_points(m, prof[m.name]) for m in ch.members}, ch.ok)


def test_over_decides_the_k6_zone_at_the_final_radius(monkeypatch):
    """KIT.md Verification bug 4 (measured on spine-parked-j2-3r: 20 of 170 closing poses). link 2 passes over link 1;
    both leave J2 along the same arc (O20 zone: 12 mm). link 2 sits at 50 mm up to row 7 (0.202 rad from J2) and at
    66.67 mm beyond. Row 7 is 10.1 mm of arc from J2 at its pre-raise 50 mm (exempt), so one `over` pass skips it; the
    K5 climb then lifts it to 63.2 mm, where it is 12.8 mm from J2 (not exempt) and inside link 1's [60.5, 63.5] + 0.5:
    K6 rejects every pose. Now `over` + climb run to a fixed point and K6 finds nothing."""
    P = 2; c, s = math.cos(0.5), math.sin(0.5); Rx = np.array([[1, 0, 0], [0, c, -s], [0, s, c]])   # pose 1: all rotated
    k = np.stack([[0, 1.0, 0], Rx @ [0, 1.0, 0]]); e = np.stack([[0, 0, 1.0], Rx @ [0, 0, 1.0]]); a = 48.5 / 70
    v = math.cos(a) * k + math.sin(a) * e
    l1 = K.strap_member("link1", k, v, ("J1", "J2")); l2 = K.strap_member("link2", k, v, ("J2", "J3"), over=[("link1", 1.0)])
    ns, nc = l2.grid; row = np.repeat(np.arange(ns), nc); ch = K.Chain(members=[l1, l2], ok=np.ones(P, bool), joints=dict(J2=k))
    raw = {"link1": np.full(ns * nc, 60.5), "link2": np.where(row <= 7, 50.0, 66.67)}
    old = K._climb(l2, K._over(ch, l2, raw["link2"], {"link1": raw["link1"]}, ch.ok))      # one pass, then the climb
    ang = np.arccos(np.clip(np.einsum("pmd,pd->pm", l2.D, k), -1, 1))[0]
    r7 = (row == 7) & (np.arange(ns * nc) % nc == nc // 2)                                  # row 7, centre column
    assert np.isclose(old[r7][0], 63.2, atol=0.01) and abs(ang[r7][0] * 50 - 10.1) < 0.05 and abs(ang[r7][0] * 63.2 - 12.8) < 0.05
    assert _k6(ch, {"link1": raw["link1"], "link2": old}).all()                             # the old construction: K6 hit
    _fixed_levels(monkeypatch, raw)
    prof = K.fit_profiles(None, ch, ch.ok)
    assert not _k6(ch, prof).any()
    assert np.allclose(K._over(ch, l2, prof["link2"], prof, ch.ok), prof["link2"])         # a fixed point of `over`
    assert np.allclose(K._climb(l2, prof["link2"]), prof["link2"]) and np.isclose(prof["link2"][r7][0], 64.5)   # link 1 top + 1


def test_k6_zone_follows_the_hub_radius(monkeypatch):
    """KIT.md Verification bug 5: the K6 exemption was HUB_R + 2 = 12 mm at every joint, so around a slim O15 hub
    (hub_member(rad=7.5)) link 1 / link 2 went unchecked between 9.5 and 12 mm (with end_mm = rad + 2 an optimistic
    hole: 35.11 vs 44.49 measured). Partners stacked 0.15 mm apart (the hub stack spacing) 10-11.5 mm from J2: exempt
    at an O20 hub, hubless or a larger hub (the zone is capped at 12), a K6 hit at the O15 hub, and `over` (which uses
    the same zones) lifts the upper one there."""
    P = 2; k = np.tile([0.0, 1, 0], (P, 1)); a_, b_ = K.plane_frame(k)
    d = np.array([10.0, 10.5, 11.0, 11.5]); y = np.array([-2.0, 0.0, 2.0])
    th, cs = (d[:, None] / 60.0 + 0 * y).ravel(), (y[None, :] / 60.0 + 0 * d[:, None]).ravel()   # mm of arc at r 60
    D = K.unit(np.cos(th)[None, :, None] * k[:, None] + np.sin(th)[None, :, None] * a_[:, None] + cs[None, :, None] * b_[:, None])

    def chain(rad, over=()):
        lo = K.Member("link1", D, joints=("J1", "J2")); up = K.Member("link2", D.copy(), joints=("J2", "J3"), over=list(over))
        hubs = [K.hub_member("hub2", k, "J2", rad=rad)] if rad else []
        return K.Chain(members=hubs + [lo, up], ok=np.ones(P, bool), joints=dict(J2=k))
    n = len(th); raw = {"hub2": np.full(1, 40.0), "link1": np.full(n, 60.0), "link2": np.full(n, 63.15)}
    for rad, zone, hit in ((10.0, 12.0, False), (None, 12.0, False), (19.5, 12.0, False), (7.5, 9.5, True)):
        ch = chain(rad); assert K.hub_zones(ch) == {"J2": zone}
        prof = {"link1": raw["link1"], "link2": raw["link2"]}
        if rad: prof["hub2"] = np.full(len(ch.members[0].xy), 40.0)
        assert _k6(ch, prof).all() == hit and _k6(ch, prof).any() == hit, rad
        pair = K.Chain(members=ch.members[-2:], ok=ch.ok, joints=ch.joints)                # a pair without the hub:
        pp = {m.name: K.member_points(m, prof[m.name]) for m in pair.members}               # O20 zone unless told
        assert not K.collisions(pair, pp, ch.ok).any() and K.collisions(pair, pp, ch.ok, zone=K.hub_zones(ch)).all() == hit
        ch = chain(rad, over=[("link1", 1.0)])
        _fixed_levels(monkeypatch, dict(raw, hub2=np.full(len(ch.members[0].xy) if rad else 1, 40.0)))
        pf = K.fit_profiles(None, ch, ch.ok); assert not _k6(ch, pf).any()
        assert np.allclose(pf["link2"], 64.0 if hit else 63.15), rad                        # 60 + 3 + 1 only at O15


def test_over_tests_the_pair_in_the_k6_order(monkeypatch):
    """KIT.md Verification bug 6: `_near` is not symmetric (arc at the first member's radius, the second's largest
    sample extent) and collisions() tests a pair in Chain.members order. Measured on spine-parked-j2-3r with O15 hubs: 5 poses where link 1 (listed
    first, 55.6 mm) and link 2 (59.0 mm, its far end at 84 mm) are 3.1 mm apart at link 1's radius (near: < 1 + 1.2 + 1)
    but 3.3 mm at link 2's (not near: > 1 + 1 + 1), 0.4 mm radial gap. `over` now asks in K6's order."""
    P = 2; t = np.radians(np.linspace(-20, 20, 21)); side = 3.1 / 55.6
    DA = np.tile(np.stack([np.sin(t), 0 * t, np.cos(t)], -1)[None], (P, 1, 1))
    DB = K.unit(np.tile(np.stack([np.sin(t), math.tan(side) + 0 * t, np.cos(t)], -1)[None], (P, 1, 1)))
    raw = {"link1": np.full(21, 55.6), "link2": np.where(np.arange(21) >= 18, 84.0, 59.0)}
    _fixed_levels(monkeypatch, raw)
    for first in (True, False):
        lo = K.Member("link1", DA, joints=("J1",)); up = K.Member("link2", DB, joints=("J2",), over=[("link1", 1.0)])
        ch = K.Chain(members=[lo, up] if first else [up, lo], ok=np.ones(P, bool), joints={})
        h = _k6(ch, raw); assert h.all() if first else not h.any()          # listed first, link 1 makes the pair near
        prof = K.fit_profiles(None, ch, ch.ok); assert not _k6(ch, prof).any()
        assert np.allclose(prof["link2"][:18], 59.6 if first else 59.0)      # raised only where K6 looks


def test_template_runs_on_kit_conventions(B):
    import importlib.util
    p = os.path.join(K.REPO, "docs", "concepts", "models", "_template.py")
    spec = importlib.util.spec_from_file_location("tp", p); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
    r = K.evaluate(B, M.build, M.PARAMS)
    assert r["collide"] == 0.0 and r["residual_deg"] < 0.5 and 0 < r["gap"] < 275 and r["mass_g"] > 50


# ---- verification (adversarial verifier, docs/concepts/KIT.md "Verification") ----------------------------------------
def test_flat_hub_level_vs_line_march(B):
    """K4: h_F = the brute 1 mm march of every disc sample along the axis from its true in-plane offset (q = 1); the
    h0 = 70 ray layout used before was 1.4 mm low at 54 mm and 400 (inf) instead of 161 mm at 108 mm"""
    F = K.frames(B); idx = np.array([0, 20, 45, 90, 150, 200]); okm = np.zeros(len(B.kind), bool); okm[idx] = True
    for ax in (F.S(K.bvec(2.4, 80.7)), F.HG(K.wdir(86.3, 21.8))):
        h = K.hub_member("H", ax, "J"); ch = K.Chain(members=[h], ok=okm)
        hF = K.fit_profiles(B, ch, okm, 1.0)["H"][0]
        t = np.arange(15, 236, 1.0); need = []
        for i in idx:
            O = h.xy[:, :1] * h.A[i] + h.xy[:, 1:] * h.Bv[i]; d = B.dist(int(i), O[:, None, :] + t[None, :, None] * h.K[i])
            good = (d[:, :206] >= 2) & np.lib.stride_tricks.sliding_window_view(d >= 0, 16, axis=1).all(-1)
            need.append(np.where(good.any(1), t[np.argmax(good, 1)], 400.0))
        assert abs(hF - np.max(need)) <= 1.0, (hF, np.max(need))


def test_dense_continuity_axis_check_ignores_fake_q(B):
    """a model that zeroes its joint values cannot hide a branch flip: the kit also follows the joint axes"""
    F = K.frames(B); W = K.wdir(86, 22); thr = float(np.median(F.HG(W)[F.clip, 1]))
    def build(_B, Fr, p):
        p1 = Fr.S(K.bvec(0, 80)); p3 = Fr.HG(W)
        pa, oka, _ = K.closure(p1, p3, 77, 67, 1, 0); pb, okb, _ = K.closure(p1, p3, 77, 67, -1, 0)
        p2 = np.where((p3[:, 1] > thr)[:, None], pa, pb)
        return K.Chain(members=[], ok=oka & okb, q=np.zeros((len(p1), 1)), joints=dict(J1=p1, J2=p2, J3=p3))
    ok = build(B, F, {}).ok
    ok1, f1 = K.continuity_dense(B, F, build, {}, ok)
    assert f1 > 0 and ok1.sum() < ok.sum()


def _tiny_chain_model(hub_rad=K.HUB_R, nonlocal_=False, hubless=(), info=None):
    def build(B, F, p):
        p1 = F.S(K.bvec(2.4, 80.7)); p3 = F.HG(K.wdir(86.3, 21.8)); p2, ok, _ = K.closure(p1, p3, 76.9, 66.7, -1, 10)
        if nonlocal_: ok = ok & (np.arange(len(p1)) % 2 == 0)                       # depends on the pose index, not on F
        q = np.stack([K.axis_angle(p1, F.S([1.0, 0, 0]), p2), K.axis_angle(p3, F.HG([0.0, -1, 0]), p2)], -1)
        mem = [K.hub_member("hub1", p1, "J1", rad=hub_rad), K.hub_member("hub3", p3, "J3"),
               K.strap_member("link1", p1, p2, ("J1", "J2"), ramp_to=(("hub1", K.STACK), (None, 0)))]
        if "J2" not in hubless: mem.append(K.hub_member("hub2", p2, "J2"))
        return K.Chain(members=mem, ok=ok, q=q, joints=dict(J1=p1, J2=p2, J3=p3), hubless=hubless, info=dict(info or {}))
    return build


def test_audit_closes_honesty_holes(B, tmp_path):
    r = K.evaluate(B, _tiny_chain_model(), {})
    assert r["honest"] and not r["audit"] and max(r["sample_mm"].values()) <= 4.0
    assert any("smaller than O20" in x for x in K.evaluate(B, _tiny_chain_model(hub_rad=5.0), {})["audit"])
    with pytest.raises(ValueError):                                   # a joint without any hub member
        K.evaluate(B, lambda b, f, p: (lambda c: (c.members.pop(), c)[1])(_tiny_chain_model()(b, f, p)), {})
    r2 = K.evaluate(B, _tiny_chain_model(hubless=("J2",)), {}); assert r2["honest"] and r2["hubless"] == ["J2"]
    assert any("pose-local" in x for x in K.evaluate(B, _tiny_chain_model(nonlocal_=True), {})["audit"])
    rb = K.evaluate(B, _tiny_chain_model(), {}, cont=False); assert not rb["honest"]
    with pytest.raises(ValueError): K.write_row("x", "x", rb)
    with pytest.raises(ValueError):                                   # K2 requested without q or joints
        K.evaluate(B, lambda b, f, p: K.Chain(members=[], ok=np.ones(len(f.RS), bool)), {})
    out = tmp_path / "s.json"; best, rows = K.sweep(B, _tiny_chain_model(), [{"q": 1.0}, {"q": 0.9}], str(out), log=None)
    import json; saved = json.load(open(out))
    assert len(saved) == 2 and all(e["gap"] == K.CB.gap_of(e["inband14"], e["follow"], e["reach"], e["contact"]) for e in saved)
    assert all(e["honest"] for e in saved)


def test_audit_declared_slim_hub(B):
    """a hub smaller than O20 is honest only as a DECLARED catalogue component: Chain.info['hub_rad'] names its radius,
    tools/hardware_catalogue.json holds it (7.5 = MR117-pair-O15-slim) and the sampled disc covers that disc"""
    assert K.catalogue_hubs()[7.5]["id"] == "MR117-pair-O15-slim" and K.catalogue_hubs()[7.5]["stack"] == K.CROWN
    r = K.evaluate(B, _tiny_chain_model(hub_rad=7.5, info=dict(hub_rad=dict(J1=7.5))), {})
    assert r["honest"] and not r["audit"] and r["declared_hubs"]["J1"]["component"] == "MR117-pair-O15-slim"
    r = K.evaluate(B, _tiny_chain_model(hub_rad=7.5), {})                                    # not declared
    assert not r["honest"] and any("hub1: hub of J1 smaller than O20" in x for x in r["audit"]) and not r["declared_hubs"]
    r = K.evaluate(B, _tiny_chain_model(hub_rad=5.0, info=dict(hub_rad=dict(J1=7.5))), {})   # declared O15, built O10
    assert not r["honest"] and any("smaller than its declared MR117-pair-O15-slim" in x for x in r["audit"])
    r = K.evaluate(B, _tiny_chain_model(hub_rad=8.5, info=dict(hub_rad=dict(J1=8.5))), {})   # O17: no catalogue entry
    assert not r["honest"] and any("smaller than O20" in x for x in r["audit"])


def test_strap_layout_pose_local():
    rng = np.random.default_rng(2); u = K.unit(rng.normal(size=(40, 3))); v = K.unit(u + 0.8 * K.unit(rng.normal(size=(40, 3))))
    D = K.strap_dirs(u, v); assert np.allclose(D[:, -1, D.shape[2] // 2], v, atol=1e-9)   # each pose's strap ends on its own v
    sub = K.strap_dirs(u[:5], v[:5], ang=np.median(np.arccos((u * v).sum(-1))))           # same count when the median is given
    assert sub.shape[1:] == D.shape[1:]
