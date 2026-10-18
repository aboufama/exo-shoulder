"""tools/stop_engage.py - where each built K / J2 stop dowel really meets its slot end (an outside check of the drawn stop windows).

For a built full CAD (pipeline/full-exo/designs/<id>/exo.glb + build.json "stops"): each joint's axis is the smallest-variance
PCA direction of its MR117 bearing meshes (through their volume centroids), each stop dowel mesh is turned about that axis
against the slotted part (K: link 1a, J2: link 1b) and the first contact angle is bisected in both senses. Contact = metal
past 0 either way: dowel vertices inside the part, or the part's slot-band vertices inside the dowel (igl.signed_distance).
The GLB is exported in the build pose (dowel at its home angle = joint angle 0, user_style_minarc.dowel_at / build_links),
so the engagement error past a window end q_e (build.json stops[j]["q_deg"]) is (first contact angle toward q_e) - |q_e|.
The PCA axis sign is arbitrary: both signs are scored, the one with the smaller |error| sum is the joint's sense, the
other is kept in the record. travel_excess (free travel - window) needs neither the sign nor the build-pose assumption.
Expected (build_minarc_l1 line 60: r_d 1.5, rs 7.75, slot half width w 1.55, end clearance 0.02): the gen 4..7
user_style_minarc.arc_slot_cutter (end centres (w - r_d + clr) / rs BEYOND the stop) engages (2 (w - r_d) + clr) / rs =
0.887 deg late; the fixed cutter (end centres (w - r_d - clr) / rs INSIDE the stop) clr / rs = 0.148 deg.

    nice -n 10 python3 tools/stop_engage.py [design id ...] [--jobs 2] [--out docs/research/stop_engage/results.json]
    (no ids: every pipeline/full-exo/designs/user_* that has stop dowels)
"""
import argparse, glob, json, math, os, re, subprocess, time
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import igl, trimesh

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DES = os.path.join(REPO, "pipeline", "full-exo", "designs")
DOWEL_R, SLOT_RS, SLOT_CLR, END_CLR = 1.5, 7.75, 0.05, 0.02                     # build_minarc_l1.py line 60 (the model's stop dowel)
W = DOWEL_R + SLOT_CLR
EXPECT = dict(old_cutter_deg=round(math.degrees((2 * (W - DOWEL_R) + END_CLR) / SLOT_RS), 4), fixed_cutter_deg=round(math.degrees(END_CLR / SLOT_RS), 4))
JOINTS = {"K": dict(bearing=r"\|K bearing \d MR117", dowel=r"\|K stop dowel", part=r"\|D8-02a link 1a"),
          "J2": dict(bearing=r"\|J2 bearing \d MR117", dowel=r"\|J2 stop dowel", part=r"\|D8-02b link 1b")}
STEP, TOL_DEG, PEN = 0.5, 1e-4, -1e-5                                         # scan step, bisection tolerance (deg), contact = depth < -0.01 um
SD_TIGHT, SD_LOOSE = igl.SIGNED_DISTANCE_TYPE_PSEUDONORMAL, igl.SIGNED_DISTANCE_TYPE_WINDING_NUMBER   # pseudonormal (2.7x faster, same depths) on closed meshes


def unit(v): return np.asarray(v, float) / np.linalg.norm(v)


def scene_meshes(glb):
    s = trimesh.load(glb, force="scene"); out = {}
    for n in s.graph.nodes_geometry:
        T, g = s.graph[n]; m = s.geometry[g].copy(); m.apply_transform(T); out[n] = m
    return out


def pick(meshes, pat): return [(n, m) for n, m in meshes.items() if re.search(pat, n)]


def centroid(m): return np.asarray(m.center_mass if m.is_volume else m.triangles_center.T @ m.area_faces / m.area, float)


def bearing_axis(ms):
    """joint axis (centre, unit k) from the bearing meshes: smallest-variance PCA direction of each, sign-aligned and averaged"""
    ks, cs = [], []
    for _, m in ms:
        V = m.vertices - m.vertices.mean(0); w, U = np.linalg.eigh(V.T @ V); k = U[:, 0]
        ks.append(k if not ks or k @ ks[0] > 0 else -k); cs.append(centroid(m))
    k = unit(np.mean(ks, 0)); c = np.mean(cs, 0)
    spread = max(math.degrees(math.acos(min(1.0, abs(float(a @ k))))) for a in ks)
    off = max(float(np.linalg.norm((x - c) - ((x - c) @ k) * k)) for x in cs)            # bearing centres off the common axis
    return c, k, dict(n_bearings=len(ms), axis_spread_deg=round(spread, 4), centre_off_axis_mm=round(off, 4))


def rot(k, a):
    """rotation by a (rad) about unit k (Rodrigues)"""
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * K @ K


class Pair:
    """one stop dowel against its slotted part about the joint axis (c, k)"""
    def __init__(self, dowel, part, c, k):
        self.c, self.k = c, k
        self.Vd, self.Fd = np.asarray(dowel.vertices, float), np.asarray(dowel.faces, np.int64)
        self.Vp, self.Fp = np.asarray(part.vertices, float), np.asarray(part.faces, np.int64)
        closed = lambda m: m.is_watertight and m.is_winding_consistent
        self.sd_p, self.sd_d = (SD_TIGHT if closed(part) else SD_LOOSE), (SD_TIGHT if closed(dowel) else SD_LOOSE)
        rel = self.Vd - c; z = rel @ k; pl = rel - np.outer(z, k); self.z = (float(z.min()), float(z.max()))
        dc = pl.mean(0); self.rs = float(np.linalg.norm(dc))                      # dowel centre radius from the bearing axis
        self.rd = float(np.linalg.norm(pl - dc, axis=1).max())                    # the shank (chamfers and end centres sit inside)
        self.e = dc / self.rs; self.f = np.cross(k, self.e)                       # e: build-pose dowel direction, f: +rotation tangent
        rp = self.Vp - c; zp = rp @ k; rr = np.linalg.norm(rp - np.outer(zp, k), axis=1)
        band = (rr > self.rs - self.rd - 1.0) & (rr < self.rs + self.rd + 1.0) & (zp > self.z[0] - 1.0) & (zp < self.z[1] + 1.0)
        self.Pl = self.Vp[band]                                                   # the part's vertices the dowel can sweep over

    def depth(self, a_deg):
        """min signed distance (mm, < 0 = metal overlap) at rotation a_deg of the dowel about +k, and the deepest point (part frame)"""
        a = math.radians(a_deg); R = rot(self.k, a)
        P = (self.Vd - self.c) @ R.T + self.c
        s1, _, c1, _ = igl.signed_distance(P, self.Vp, self.Fp, self.sd_p)
        Q = (self.Pl - self.c) @ R + self.c                                       # part vertices into the dowel's frame
        s2, _, _, _ = igl.signed_distance(Q, self.Vd, self.Fd, self.sd_d) if len(Q) else (np.array([np.inf]), 0, 0, 0)
        i1, i2 = int(np.argmin(s1)), int(np.argmin(s2))
        return (float(s1[i1]), P[i1]) if s1[i1] <= s2[i2] else (float(s2[i2]), self.Pl[i2])

    def first_contact(self, sense, a_max):
        """first contact angle (deg >= 0) turning the dowel by sense * a about +k, None if free up to a_max"""
        a0, d0 = 0.0, self.depth(0.0)[0]
        if d0 < PEN: return dict(angle_deg=0.0, at_build_pose=True, depth0_mm=round(d0, 5))
        a = STEP
        while a <= a_max + 1e-9:
            if self.depth(sense * a)[0] < PEN: break
            a0, a = a, a + STEP
        else: return None
        lo, hi = a0, a
        while hi - lo > TOL_DEG:
            m = 0.5 * (lo + hi); lo, hi = (lo, m) if self.depth(sense * m)[0] < PEN else (m, hi)
        d, p = self.depth(sense * hi); R = rot(self.k, math.radians(sense * hi))
        dc = self.c + R @ (self.rs * self.e) + 0.5 * (self.z[0] + self.z[1]) * self.k     # dowel centre at contact
        v = p - dc; v -= (v @ self.k) * self.k; er = R @ self.e; ft = R @ self.f
        radial, tangential = float(v @ er), float(v @ ft) * sense                # tangential > 0: ahead of the dowel (an end)
        return dict(angle_deg=round(hi, 4), clearance0_mm=round(d0, 4), contact_radial_mm=round(radial, 3),
                    contact_ahead_mm=round(tangential, 3), kind="end" if tangential > abs(radial) else "wall")


def check_design(did):
    dd = os.path.join(DES, did); b = json.load(open(os.path.join(dd, "build.json"))); st = b.get("stops") or {}
    rec = dict(design=did, glb_commit=subprocess.run(["git", "-C", REPO, "log", "-1", "--format=%h %cI", "--", os.path.join(dd, "exo.glb")],
                                                       capture_output=True, text=True).stdout.strip() or None, joints={})
    if not st: rec["skipped"] = "build.json has no stops (no K / J2 stop dowels)"; return rec
    t0 = time.time(); meshes = scene_meshes(os.path.join(dd, "exo.glb"))
    for j, pat in JOINTS.items():
        if j not in st: continue
        q_lo, q_hi = sorted(st[j]["q_deg"]); brg = pick(meshes, pat["bearing"]); dws = pick(meshes, pat["dowel"]); parts = pick(meshes, pat["part"])
        if not brg or not dws or len(parts) != 1:
            rec["joints"][j] = dict(skipped=f"meshes not found: bearings {len(brg)}, dowels {len(dws)}, slotted parts {len(parts)}"); continue
        c, k, ax = bearing_axis(brg); a_max = max(abs(q_lo), abs(q_hi)) + 5.0; jr = dict(window_deg=[q_lo, q_hi], axis=ax, slotted_part=parts[0][0], dowels=[])
        for dn, dm in sorted(dws):
            pr = Pair(dm, parts[0][1], c, k)
            fp, fm = pr.first_contact(+1, a_max), pr.first_contact(-1, a_max)    # turning about +k / -k
            ap = fp["angle_deg"] if fp else None; am = fm["angle_deg"] if fm else None
            senses = {}
            for s in (+1, -1):
                hi_c, lo_c = (fp, fm) if s > 0 else (fm, fp)                       # s: joint q increases turning about s * k
                e_hi = None if hi_c is None else round(hi_c["angle_deg"] - q_hi, 4)
                e_lo = None if lo_c is None else round(lo_c["angle_deg"] + q_lo, 4)
                senses[s] = dict(err_hi_deg=e_hi, err_lo_deg=e_lo, contact_hi=hi_c, contact_lo=lo_c,
                                 score=(abs(e_hi) if e_hi is not None else 999) + (abs(e_lo) if e_lo is not None else 999))
            s_best = min(senses, key=lambda s: senses[s]["score"]); best = senses[s_best]
            ex = None if ap is None or am is None else round(ap + am - (q_hi - q_lo), 4)
            mm = lambda x: None if x is None else round(math.radians(x) * pr.rs, 4)
            jr["dowels"].append(dict(dowel=dn, rs_mm=round(pr.rs, 4), dowel_r_mm=round(pr.rd, 4), sense=s_best,
                                     err_hi_deg=best["err_hi_deg"], err_lo_deg=best["err_lo_deg"],
                                     err_hi_mm=mm(best["err_hi_deg"]), err_lo_mm=mm(best["err_lo_deg"]),
                                     travel_excess_deg=ex, contact_hi=best["contact_hi"], contact_lo=best["contact_lo"],
                                     other_sense=dict(err_hi_deg=senses[-s_best]["err_hi_deg"], err_lo_deg=senses[-s_best]["err_lo_deg"])))
        rec["joints"][j] = jr
    rec["seconds"] = round(time.time() - t0, 1); return rec


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("ids", nargs="*"); ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--out", default=os.path.join(REPO, "docs", "research", "stop_engage", "results.json")); a = ap.parse_args()
    ids = a.ids or sorted(os.path.basename(d) for d in glob.glob(os.path.join(DES, "user_*")) if os.path.exists(os.path.join(d, "exo.glb")))
    jobs = max(1, min(2, a.jobs))                                                 # local, niced, <= 2 processes (CLAUDE.md)
    with ProcessPoolExecutor(jobs) as ex: recs = list(ex.map(check_design, ids))
    for r in recs:
        print(f"== {r['design']}" + (f": {r['skipped']}" if r.get("skipped") else f" ({r['seconds']} s)"))
        for j, jr in r["joints"].items():
            if jr.get("skipped"): print(f"   {j}: {jr['skipped']}"); continue
            for d in jr["dowels"]:
                print(f"   {j} {d['dowel'].split('|')[1][:22]:22s} window {jr['window_deg']}: past hi {d['err_hi_deg']} deg ({d['err_hi_mm']} mm), "
                      f"past lo {d['err_lo_deg']} deg ({d['err_lo_mm']} mm), travel excess {d['travel_excess_deg']} deg; "
                      f"contacts {(d['contact_hi'] or {}).get('kind')}/{(d['contact_lo'] or {}).get('kind')}; other sense {d['other_sense']}")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(dict(tool="tools/stop_engage.py", expected=EXPECT, method=__doc__.split("\n\n")[0], designs=recs), open(a.out, "w"), indent=1)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
