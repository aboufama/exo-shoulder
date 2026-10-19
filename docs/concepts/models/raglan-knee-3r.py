"""Concept model: RAGLAN-KNEE 3R (id raglan-knee-3r).

The best zero-passive-translation design (skin-normal-3r-pin-knee: the leader osn k4216 seats, J1 / J2 hubs on GH rays,
J3 an offset skin-normal hub on the deltoid, closed by a flat two-pin knee instead of the crossed cuff slides) with its
two links cut like a tailor's raglan seam instead of on the shortest line:

  RAGLAN ROUTING. Link k runs hub -> W_k -> hub: two great-circle legs joined by ONE tangent arc in the planform
  (radius rc), W_k = cos(d) slerp(C_a, C_b, t) + sin(d) n_ab, FIXED in the link (one rigid bent bar, constant 8 x 3
  section, lines + one tangent arc, no loft, no twist). d = 0 is the pin knee's own great-circle link (parity). The turn
  is chosen from the measured RAGLAN MAP (mode `map`): the K3-style need of every direction of the link's own moving
  frame over every pose the chain takes, and the share of poses one height keeps within 2-14 mm.

Everything else is the pin-knee model, imported (a private copy of its module, so its live file is not touched):
real O20 hubs with the 12.25 stack, the 5 mm pin stack, E strap / boss / pad / knee link, skin-fitted undersides with
60 deg ramps, closed-form spherical IK, knee closure in [30, 150] deg, 10 fps continuity, jam rule, every part pair,
hub walls / crowns / strap tops skin-checked, greedy pose dropping recorded as contact, `frozen` (lesson c), `audit`
(near-touch, overhead).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/raglan-knee-3r.py [check|redteam|map|frozen] ['<json params>'] [out.json]
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
_spec = importlib.util.spec_from_file_location("pin_knee_for_raglan", os.path.join(HERE, "skin-normal-3r-pin-knee.py"))
PK = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(PK)
S = PK.S; unit = S.unit; D2R = math.pi / 180
ID = "raglan-knee-3r"
NAME = "Raglan-knee 3R (pin-knee leader with links bent along the lines of least skin motion)"

PARAMS = dict(PK.PARAMS)
PARAMS.update(phib=-90.0,                 # the pin knee's best k10 (knee link posterior)
              r1t=0.5, r1d=0.0,           # link 1 turn: fraction along C1 -> C2, deg off the great circle (+ = n_ab side)
              r2t=0.5, r2d=0.0,           # link 2 turn: fraction along C2 -> C3
              rc=10.0)                    # planform radius of the tangent arc at the turn (mm, centreline)

_base_add_links = S.Geometry.add_links


def _path(da, db, R, t_w, d_w, rc):
    """centreline directions hub a -> W -> hub b: great-circle legs + one tangent arc of planform radius rc (mm at R),
    resampled every SPACING mm; returns dirs (n,3), arc length (n,), row normals (n,3)"""
    ang = math.acos(float(np.clip(da @ db, -1, 1))); bn = unit(np.cross(da, db))
    g = unit(math.sin((1 - t_w) * ang) * da + math.sin(t_w * ang) * db) / 1.0
    g = unit(g); dr = d_w * D2R; W = unit(math.cos(dr) * g + math.sin(dr) * bn)
    Wp = R * W
    def tang(frm, to):                                        # unit tangent at frm toward to (great circle)
        v = to - (to @ frm) * frm; return unit(v)
    ta, tb = tang(W, da), tang(W, db)
    th = math.acos(float(np.clip(ta @ tb, -1, 1)))            # interior angle at W (pi = straight)
    la = R * math.acos(float(np.clip(W @ da, -1, 1))); lb = R * math.acos(float(np.clip(W @ db, -1, 1)))
    L = rc / math.tan(th / 2) if th < math.pi - 1e-3 else 0.0
    L = min(L, 0.45 * la, 0.45 * lb); rc_eff = L * math.tan(th / 2) if L > 0 else 0.0
    pts = []
    def gc(a, b, n):                                          # great-circle points a -> b (unit), n+1 incl. ends
        w = math.acos(float(np.clip(a @ b, -1, 1)))
        if w < 1e-9: return np.repeat(a[None], n + 1, 0)
        s = np.linspace(0, 1, n + 1)[:, None]; return unit((np.sin((1 - s) * w) * a + np.sin(s * w) * b) / math.sin(w))
    Ta = unit(Wp + L * ta); Tb = unit(Wp + L * tb)
    pts.append(gc(da, Ta, 400))
    if L > 0:
        bis = unit(ta + tb); O = Wp + (rc_eff / math.sin(th / 2)) * bis
        a0 = unit(Wp + L * ta - O); a1 = unit(Wp + L * tb - O); phi = math.acos(float(np.clip(a0 @ a1, -1, 1)))
        s = np.linspace(0, 1, 60)[:, None]
        arc = O + rc_eff * unit((np.sin((1 - s) * phi) * a0 + np.sin(s * phi) * a1) / max(math.sin(phi), 1e-9))
        pts.append(unit(arc))
    pts.append(gc(Tb, db, 400))
    P = np.concatenate(pts); seg = R * np.arccos(np.clip((P[1:] * P[:-1]).sum(1), -1, 1)); s = np.r_[0, np.cumsum(seg)]
    tot = s[-1]; n = max(4, int(tot / S.SPACING)); st = (np.arange(n) + 0.5) / n * tot
    dirs = unit(np.stack([np.interp(st, s, P[:, k]) for k in range(3)], 1))
    T = np.gradient(dirs, axis=0); T = unit(T - (T * dirs).sum(1, keepdims=True) * dirs)
    nrm = unit(np.cross(dirs, T))
    return dirs, st, nrm, dict(W=W, turn_deg=round(180 - math.degrees(th), 1), rc=round(rc_eff, 1), length=round(tot, 1))


def routed_add_links(self, f1, f2, f3):
    """the pin knee's links (8 mm strap = 4 sample rows at -3, -1, 1, 3 mm, outside both hub footprints) on a routed path"""
    P = self.D.p
    if all(abs(float(P.get(k, 0.0) or 0.0)) < 0.25 for k in ("r1d", "r2d")):
        return _base_add_links(self, f1, f2, f3)              # parity: the great-circle links, bit for bit
    D = self.D; u, c = D.u, D.c
    C = [c[0] + f1 * u[0], c[1] + f2 * u[1], c[2] + f3 * u[2]]
    out = []; self.route_info = {}
    for li, (ka, kb, mem) in enumerate(((0, 1, 1), (1, 2, 2))):
        da, db = unit(C[ka]), unit(C[kb]); R = 0.5 * (np.linalg.norm(C[ka]) + np.linalg.norm(C[kb]))
        t_w = float(P.get(f"r{li + 1}t", 0.5)); d_w = float(P.get(f"r{li + 1}d", 0.0))
        if abs(d_w) < 0.25:
            ang = math.acos(float(np.clip(da @ db, -1, 1))); bn = unit(np.cross(da, db))
            n = max(4, int(R * ang / S.SPACING)); ts = (np.arange(n) + 0.5) / n
            dirs = np.array([unit(math.sin((1 - t) * ang) * da + math.sin(t * ang) * db) for t in ts])
            sarc = ts * R * ang; nrm = np.repeat(bn[None], n, 0); info = dict(turn_deg=0.0, length=round(R * ang, 1))
        else:
            dirs, sarc, nrm, info = _path(da, db, R, t_w, d_w, float(P.get("rc", 10.0)))
            info["W"] = [round(float(x), 4) for x in info["W"]]
        def rows_of(dirs, sarc, nrm):
            rows = []
            for v in (-3.0, -1.0, 1.0, 3.0):
                dv = unit(dirs + (v / R) * nrm); pts = R * dv
                def off_axis(k): w = pts - c[k]; return np.linalg.norm(w - (w @ u[k])[:, None] * u[k], axis=1)
                keep = (off_axis(ka) > S.HUB_R) & (off_axis(kb) > S.HUB_R)
                rows.append((dv, keep, sarc))
            return rows
        rows = rows_of(dirs, sarc, nrm)
        ang0 = math.acos(float(np.clip(da @ db, -1, 1))); bn0 = unit(np.cross(da, db)); n0 = max(4, int(R * ang0 / S.SPACING))
        ts0 = (np.arange(n0) + 0.5) / n0; dirs0 = np.array([unit(math.sin((1 - t) * ang0) * da + math.sin(t * ang0) * db) for t in ts0])
        info["n_samples"] = int(sum(int(r[1].sum()) for r in rows))
        info["n_great_circle"] = int(sum(int(r[1].sum()) for r in rows_of(dirs0, ts0 * R * ang0, np.repeat(bn0[None], n0, 0))))
        out.append(dict(name=f"L{li + 1}", mem=mem, ka=ka, kb=kb, rows=rows)); self.route_info[f"L{li + 1}"] = info
    self.links = out
    return out


class RGeometry(S.Geometry):
    add_links = routed_add_links


S.Geometry = RGeometry          # this module's PRIVATE copy of the seed / osn / pin-knee chain builds the routed links
# Since the pin knee's per-hub-radius change (2026-10-16 04:07 UTC) its Model builds links with its own PK._Geo, a subclass
# of the seed's Geometry bound at import (before the swap above), so the routed links were silently dropped (red team,
# docs/research/reach_attribution.md section 1: 32.37 instead of the verified 31.52). Route PK._Geo too; parity (r1d = r2d
# = 0) keeps the pin knee's own add_links bit for bit. Fixed in the rebase track 2026-10-16.
_pk_add_links = PK._Geo.add_links


def _pk_routed_add_links(self, f1, f2, f3):
    P = self.D.p
    if all(abs(float(P.get(k, 0.0) or 0.0)) < 0.25 for k in ("r1d", "r2d")):
        return _pk_add_links(self, f1, f2, f3)
    return routed_add_links(self, f1, f2, f3)


PK._Geo.add_links = _pk_routed_add_links


def clean(params):
    p = dict(PARAMS); p.update(params or {})
    for k in ("r1t", "r2t"): p[k] = min(0.85, max(0.15, float(p[k])))
    for k in ("r1d", "r2d"): p[k] = min(60.0, max(-60.0, float(p[k])))
    p["rc"] = min(40.0, max(6.0, float(p.get("rc", 10.0))))      # inner edge radius >= 2 mm on the 8 mm strap
    return p


def _report(B, params):
    p = clean(params); r, M = PK._report(B, p)
    geo = getattr(M, "geo", None)
    r["route"] = getattr(geo, "route_info", None) if geo is not None else None
    if geo is not None and not hasattr(geo, "route_info"): r["route"] = "great circle"
    try: r["parts_ib14"] = M.part_inband()
    except Exception: pass
    # red team (dilution): in-band 14 is a SHARE of metal samples, so a longer link that sits in band lowers the gap by
    # diluting the out-of-band parts. Recompute it with each routed link weighted at its great-circle sample count.
    ri = r.get("route") if isinstance(r.get("route"), dict) else None; pib = r.get("parts_ib14") or {}
    if pib:
        w = {k: v[2] for k, v in pib.items()}
        if ri:
            for k, inf in ri.items():
                if k in w and inf.get("n_great_circle"): w[k] = inf["n_great_circle"]
        ib = sum(w[k] * pib[k][0] for k in w) / max(1, sum(w.values()))
        r["inband14_fixed_n"] = round(float(ib), 4)
        r["gap_fixed_n"] = CB.gap_of(ib, r["follow"], r["reach"], r["contact"])
        r["inband_member"] = dict({k: v[0] for k, v in pib.items()}, n={k: v[2] for k, v in pib.items()}, gap_fixed_n=r["gap_fixed_n"])   # kept by concept_cma
    return r, M


def evaluate(B, params):
    """tools/concept_cma.py hook: (params, report)"""
    r, M = _report(B, params); p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    """tools/concept_sweep.py hook"""
    r, M = _report(B, params); r.pop("params", None); return r


def window_share(N, w=12.0):
    """N (poses, cells) need radii: share of poses within w below the max (q = 1 'top') and the best w window ('ceiling')"""
    big = N >= S.BIG * 0.5 if hasattr(S, "BIG") else ~np.isfinite(N)
    Nf = np.where(big, np.nan, N); top = np.nanmax(Nf, 0)
    t = np.nanmean(np.where(big, 0.0, (Nf >= top[None] - w).astype(float)), 0)
    srt = np.sort(np.where(big, np.inf, N), 0); n = len(N); ceil = np.zeros(N.shape[1])
    for j in range(N.shape[1]):
        v = srt[:, j][np.isfinite(srt[:, j])]
        if len(v): ceil[j] = (np.searchsorted(v, v + w, side="right") - np.arange(len(v))).max() / n
    return t, ceil, big.mean(0)


def raglan_map(B, params, T=np.linspace(0.05, 0.95, 19), Dg=np.arange(-50.0, 50.1, 5.0)):
    """the measurement: for every cell (t, d) of each link's own frame (direction cos(d) slerp(C_a, C_b, t) + sin(d) n_ab,
    a ray from GH), the need over every pose the chain takes (sphere trace to 2 mm clearance, link 2 over the knee / pad)
    and the share of poses one height keeps in 2-14 mm"""
    p = clean(params); M = PK.Model(B, p); M.run()
    D = M.D; u, c = D.u, D.c; F = M.f
    C = [c[0] + F[0] * u[0], c[1] + F[1] * u[1], c[2] + F[2] * u[2]]
    poses = np.nonzero(M.kin_ok)[0]; out = dict(T=T.tolist(), D=Dg.tolist(), n_poses=int(len(poses)))
    for li, (ka, kb, mem) in enumerate(((0, 1, 1), (1, 2, 2))):
        da, db = unit(C[ka]), unit(C[kb]); ang = math.acos(float(np.clip(da @ db, -1, 1))); bn = unit(np.cross(da, db))
        dirs = []
        for t in T:
            g = unit(math.sin((1 - t) * ang) * da + math.sin(t * ang) * db)
            for d in Dg: dirs.append(unit(math.cos(d * D2R) * g + math.sin(d * D2R) * bn))
        dirs = np.array(dirs); avoid = ("knee", "pad") if li == 1 else ()
        N = M.needed([(mem, np.zeros_like(dirs), dirs, 170.0, avoid)], poses)[0]
        top, ceil, inf = window_share(N)
        R0 = 0.5 * (np.linalg.norm(C[ka]) + np.linalg.norm(C[kb]))
        out[f"link{li + 1}"] = dict(top=top.reshape(len(T), len(Dg)).round(3).tolist(), ceiling=ceil.reshape(len(T), len(Dg)).round(3).tolist(),
                                    inf=inf.reshape(len(T), len(Dg)).round(3).tolist(), span_deg=round(math.degrees(ang), 1), R=round(float(R0), 1),
                                    need_p50=np.nanmedian(np.where(N >= 1e5, np.nan, N), 0).reshape(len(T), len(Dg)).round(1).tolist())
    return out


def frozen(params, out=None):
    """lesson (c): fit on Bench(60,160) fast, wear that exact shape on Bench(110,360) (CB_EXACT=1 -> exact)"""
    p = clean(params); t = time.time(); o = PK.frozen(p); o["params"] = p; o["secs"] = round(time.time() - t, 1)
    if out: json.dump(o, open(out, "w"), indent=1, default=float)
    return o


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "frozen":
        o = frozen(par, sys.argv[3] if len(sys.argv) > 3 else None); print(json.dumps(o, default=float)); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t0 = time.time()
    if mode == "map":
        M = raglan_map(B, par); M["params"] = clean(par)
        if len(sys.argv) > 3: json.dump(M, open(sys.argv[3], "w"))
        for lk in ("link1", "link2"):
            top = np.array(M[lk]["top"]); i0 = len(M["D"]) // 2
            print(lk, "span", M[lk]["span_deg"], "great circle top", top[:, i0].round(2).tolist())
            print("   best d per t:", [(round(M["T"][a], 2), M["D"][int(np.argmax(top[a]))], round(float(top[a].max()), 2)) for a in range(len(M["T"]))])
        print(f"{time.time() - t0:.0f}s"); sys.exit()
    r, M = _report(B, par)
    print({k: r.get(k) for k in ("gap", "gap_fixed_n", "inband14_fixed_n", "reach", "follow", "inband14", "inband10", "contact", "why", "route")}, f"{time.time() - t0:.0f}s", B.mode)
    print("parts", r.get("parts_ib14"))
