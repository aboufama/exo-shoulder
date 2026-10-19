"""L1 keep-out CAD of the generation-8 winner conecut-knee-knuckle-3r (round 12; the NEW VERIFIED LEAD 2026-10-17 ~18:21 UTC by
the user's plain-verified-gap rule: frozen exact Bench(110,360) 18.28 / score 93.35, held out 22.38; ledger WATCH,
docs/alignment/conecut-knee-knuckle-3r.md) -> a judge-ready design dir pipeline/full-exo/designs/<out>/ (exo.glb, clips.json,
workspace.json, design.json, parts_full.json, build.json).

conecut = the gen-7 lead slipper-nose-knuckle-3r (rows best_params of docs/concepts/rows/slipper-nose-knuckle-3r.json, flank beta
-176.684, stock r 1.25 nose, mu 0.087) with exactly two changes, both carried here and nothing else:
  (a) the pin knee RE-PROPORTIONED so it never binds: rows best_params of docs/concepts/rows/conecut-knee-knuckle-3r.json -
      stk 6.0 (MR63ZZ pairs), lE 97.1443, lc 24.3508, phiE 0.7526, phib -91.8041 (ang_min 25.2189 = the model's KNEE);
  (b) a J3 HARD STOP on J3's own angle q3' = q3 + phi (the link 2 -> member 3 angle; the verifier's C1: R2^T R3 = rot(u3, q3'),
      offset 0.000, spread 0.0001 deg): an ISO 8734 O2 m6 440C dowel pressed through hub 3's lower plate (member 3) at r 7.5,
      running in a 2.1 x 1.0 mm arc groove under link 2's ring (the J3 upper boss), window [J3MIN -111.9036, J3MAX 122.7417].

HOW: build_slipper_l1.py (gen 7) is IMPORTED unchanged and its module globals are retargeted at the conecut claim model (the
verified CCModel, docs/concepts/models/conecut-knee-knuckle-3r.py, SN_CELL=lead, loaded unchanged) and the conecut config; its
main() then builds every gen-7 part (hubs, link 1a chain, straps, K / J2 stops, the slipper-nose drive, E strap, knee link with the
MR63ZZ-pair bosses, knee stop tooth, pad, retainers, BOTTOM cut, pad mount) from THIS model's fitted shape. What this file adds:
  * L1Model = the claim's CCModel + the gen-7 drive-frame hook (crank posed from the current K opening, the model's own law);
  * chain(): the gen-7 chain + the J3 stop (a frame past [J3MIN, J3MAX] in q3' is not taken: clips hold it as 'j3stop', the
    workspace pose does not close) - the same rule CCModel applies before fit / run;
  * build_parts(): the J3 upper boss split into its 1.0 mm groove ring (F+3.15..F+4.15, the arc groove cut through it: one valid
    genus-1 solid) + the boss above it (F+4.15..F+12.25), and the stop dowel (F+0.10..F+4.00, 0.85 mm into the groove, 0.15 off its
    floor: the J3 red team's build spec, docs/research/conecut_mechanism_redteam.md section 6); the groove's
    home angle is placed so the dowel's swept arc keeps the most angle from link 2's own strap root in the groove layer;
  * the J3 stop checks: dowel vs groove ends over the window (contact at J3MIN / J3MAX, penetration past them = a real stop),
    dowel-in-groove at every check pose from the posed member frames, the stop tolerance stack vs the 0.74 deg held margin, a
    dowel hand calc at 6 and 10 N.m;
  * check poses: the gen-7 ten + the J3-stop extremes (min / max q3' taken) and the knee extremes (min / max knee angle taken);
  * fits table: the gen-7 L1 table with the gen-7 CAD verifier's D1 fix (the duplicate 'crank-to-link 1a / 1b running faces
    ISO 2768-f' entry REPLACED by +-0.02), D2 (K-phase band stated RSS), D3 (crank inner-ring spacer + wave-washer room), the
    knee stop +-0.02, the wear-test pass line mu <= 0.105, and the J3 stop dowel / groove fits.

    SN_CELL=lead OMP_NUM_THREADS=1 nice -n 10 python3 pipeline/concept_l1/build_conecut_l1.py [--out l1_conecut-knee] [--jobs 2] [--no-clips]
    ... --post-only     (re-run the J3-stop post-processing on an existing build: clip relabel, design.json, build.json)
    ... --patch-j3      (rewrite only the J3 dowel of an existing build to the current spec, re-run its sweep, then --post-only)
"""
import json, math, os, sys, time
import numpy as np, trimesh
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
os.environ["SN_CELL"] = "lead"
os.environ.pop("CB_EXACT", None)                                                # the frozen protocol's fit bench is FAST (Bench(60,160))
import build_slipper_l1 as SL                                                    # noqa: E402  (gen-7 L1 builder, imported unchanged)
MIN, BASE = SL.MIN, SL.BASE; CB, REF = BASE.CB, BASE.REF

ID = "conecut-knee-knuckle-3r"
CC = MIN._load("conecut_for_l1", os.path.join(REPO, "docs", "concepts", "models", ID + ".py"))
ROW = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", ID + ".json")))
BEST = ROW["best_params"]
if isinstance(BEST, str): BEST = json.loads(BEST)
CFG = dict(CC.LEAD_ROW, **BEST); CFG["ang_min"] = float(CC.PARAMS["ang_min"])  # the verified config (the verifier's: CC.PARAMS + BEST)
S = CC.S; unit = S.unit; UP, CROWN, T_LINK, W_LINK = S.UP, S.CROWN, S.T_LINK, S.W_LINK
J3MIN, J3MAX = float(CFG["J3MIN"]), float(CFG["J3MAX"])
J3_RS, J3_DR, J3_GW, J3_GD, J3_DTOP, J3_DBOT, J3_END_R = float(CC.DOWEL_R), 1.0, 2.1, 1.0, 0.85, 0.10, 1.05
# r 7.5, O2 dowel, groove 2.1 x 1.0 (F+3.15..4.15), dowel F+0.10..F+4.00 (top 0.85 above the boss underside: 0.15 tip clearance), R1.05 ends -
# the J3 red team's build spec (docs/research/conecut_mechanism_redteam.md section 6)
REDTEAM = "docs/research/conecut_mechanism_redteam.md"
VERIFIED = dict(bench=dict(gap=18.28, score=93.35, reach=0.7278, follow=1.0, inband14=0.9012, inband10=0.5739, contact=0.0106),
                held=dict(gap=22.38, reach=0.6922, follow=1.0, inband14=0.9, contact=0.016),
                knee=dict(ang_bench=[59.27, 105.94], ang_held=[59.27, 107.07], margin_mm=[11.42, 13.18], knee_N_per_Nm_max=12.0),
                j3=dict(q3p_bench=[-109.2, 116.1], q3p_held=[-111.16, 119.44], margin_held_deg=[0.74, 3.3], stopped_bench=6, stopped_held=19),
                c1_offset_deg=0.0, harness="docs/concepts/verify/conecut-knee-knuckle-3r.py",
                dumps=["docs/concepts/verify/conecut-knee-knuckle-3r_v_bench_frozen.json", "docs/concepts/verify/conecut-knee-knuckle-3r_v_held_frozen.json"])

# --- the fits table: gen-7 L1's, with the gen-7 CAD verifier's open items closed (pipeline/full-exo/designs/user_slipper_nose/VERIFY.md,
#     docs/research/user_slipper_nose_fix.md) and the conecut additions
FITS = [dict(f) for f in SL.FITS if not f["where"].startswith("crank-to-link 1a / 1b running faces")]          # D1: the 2768-f duplicate removed
FITS += [
    dict(where="crank-to-link 1a / link 1b running faces (D1)", fit="+-0.02 mm profile on these 5-axis Ti faces (NOT ISO 2768-f: +-0.05 each, stack 0.10, could close "
         "the 0.086 mm smallest posed running gap); the gen-7 L1's 2768-f line is removed, this is the only entry for these faces"),
    dict(where="K-phase band (D2)", fit="onset +0.75 +0.15 / -0.10 deg is an RSS band of the stack (key dowel position, lobe profile, crank pivot, flank profile); "
         "the worst-case linear stack is +-0.30 deg wider - if the drawing is read linear, the low end becomes -0.02 deg; shim the key dowel"),
    dict(where="crank pivot axial stack (D3)", fit="ground stainless inner-ring spacer O3.1 x O4.5 x 0.15-0.20 under the lower bearing (683ZZ in the full CAD) so the "
         "preload cannot drop the crank onto link 1b; wave washer 5-10 N with its own 0.3 mm room under the DIN 6799 RS 2.3 clip; re-run the posed drive-pair check "
         "(gen-7 running gaps 0.086 / 0.123 / 0.108 mm) on the full CAD"),
    dict(where="knee stop tooth vs E strap side", fit="+-0.02 mm on the tooth face and the E strap side face (stop at 180 - ang_min = 154.78 deg; conecut's taken knee "
         "max 107.07 deg held out: 47.7 deg / 12.8 mm in d below it)"),
    dict(where="slipper nose / DLC flank wear test", fit="pass line mu <= 0.105 after the wear run (the claim's PA budget at mu 0.087; R17 / M5 re-run at 0.087 / 0.105 / 0.12)"),
    dict(where="J3 stop dowel in hub 3's lower plate", fit="ISO 8734 (DIN 6325) 2 m6 x 5 (or x 4), 440C grade >= 56 HRC with cert, surface-ground to 3.90 +-0.02, "
         "edges re-broken; through hole reamed O2.000 -0.005/0 (2-13 um interference: H7/m6 is a transition fit), at r 7.500, true position 0.02 (+-0.01 "
         "tangential) to the J3 bore and member 3's angular datum, perpendicular 0.01 to the J3 face, 0.1 x 45 top chamfer; pressed from the top to a gauge: "
         "top 0.85 +-0.02 above the plate (F+4.00), skin end recessed 0.10 (never proud)"),
    dict(where="J3 stop groove under link 2's ring", fit="arc slot 2.10 +0.02/0 wide x 1.00 +0.05/0 deep (F+3.15..4.15) at centre radius 7.500, walls concentric "
         "to the J3 bore within 0.02 (dowel floats 0.046 per side, >= 0.026 running), FULL R1.05 ends; end-arc centres 0.382 deg beyond the dowel-centre stop "
         "angles, true position 0.02 (+-0.01 tangential); 3+2-axis from below with an O2.0 / O1.5 end mill; cut BEFORE the bearing-1 seat finish bore (0.95 wall)"),
    dict(where="J3 stop acceptance + rating", fit="assembled stop -112.40 <= J3MIN <= -111.25 and 119.85 <= J3MAX <= 123.78 deg on the J3 encoder (the windows "
         "that keep the verified bench and held numbers); stop rated 1.8 N.m about J3 (J3 bearing-1 s0 = 1); dowel / groove good to 10 N.m (dowel shear SF 2.6, "
         "bending 1.95, groove-end bearing 1.66) - docs/research/conecut_mechanism_redteam.md"),
]
GROUPS = SL.GROUPS


def wr(a): return (a + 180.0) % 360.0 - 180.0


# ---------------------------------------------------------------------------------------------------- the verified model
class L1Model(CC.CCModel):
    """the claim's CCModel (J3 stop applied before fit / run); once fitted (self._l1), the crank (9) frame comes from the K
    opening read off the CURRENT member frames X[1], X[7] (gen-7 L1Model's hook, copied: the clip / workspace swaps pose the
    drive exactly through the model's own law)"""
    def T(self, m, i):
        if m in (8, 9) and getattr(self, "_l1", False):
            X7 = self.X[7][0]; c = getattr(self, "_l1c", None)
            if c is None or c[0] is not X7: self._l1c = (X7, self._drive_frames(self.X[1][0], X7))
            Rb, tb = self._l1c[1][m]; R7, t7 = self.X[7][0][i], self.X[7][1][i]
            return R7 @ Rb[i], R7 @ tb[i] + t7
        return super().T(m, i)

    def dK_of(self, X1, X7):
        from scipy.spatial.transform import Rotation as Rot
        RK = np.einsum("nji,njk->nik", X1, X7); bad = ~np.isfinite(RK).all(axis=(1, 2)); RK[bad] = np.eye(3)
        return Rot.from_matrix(RK).as_rotvec() @ self._scg["uK"]

    def _drive_frames(self, X1, X7):
        save = (self.dK, self._sc); self.dK = self.dK_of(X1, X7); self._sc = None
        try: self._sc_pose(); X = self._sc["X"]
        finally: self.dK, self._sc = save
        return X


def fit():
    """the claim's model on the verified config, fit on Bench(60,160) FAST = CC._frozen_model's hand-over (the shape the verifier
    wore frozen on Bench(110,360) exact and held out)"""
    B = CB.Bench(60, 160); P = CC._clamp(dict(CC.PARAMS, **CFG)); M = L1Model(B, P); r = M.run()
    a = CC.PK.audit(M, B); r["gap_near1"] = a.get("gap_near1"); r["gap_near2"] = a.get("gap_near2"); r["near_touch_min_mm"] = a.get("near_touch_min_mm")
    try: r["knee_report"] = CC.knee_report(M, B)
    except Exception as e: r["knee_report"] = dict(err=str(e)[:200])
    M._bench = (M.Q, M.s, M.RS, M.X, M.K, M.q); M._l1 = True; M._l1c = None
    return M, r


_chain0 = SL.chain


def chain(M, poses):
    """the gen-7 chain (drive group dk, drive-range stop) + the J3 HARD STOP: a frame with q3' = q3 + phi outside [J3MIN, J3MAX]
    is not taken (CCModel's rule, the same numbers)"""
    K = _chain0(M, poses)
    q3p = wr(np.degrees(np.asarray(K["qr"], float)[:, 2] + np.asarray(K["Kn"]["phi"], float)))
    with np.errstate(invalid="ignore"): out = (q3p < J3MIN) | (q3p > J3MAX)
    stop = np.asarray(K["ok"], bool) & np.isfinite(q3p) & out
    K["ok"] = np.asarray(K["ok"], bool) & ~stop; K["j3stop"] = stop; K["q3p"] = q3p
    return K


# ---------------------------------------------------------------------------------------------------- the J3 stop
def j3_frame(M):
    U, C, F4, hr = MIN.joints4(M); u3 = unit(U[3]); H3 = C[3] + F4[3] * u3; e, f = S.frame_of(u3); f = np.cross(u3, e)
    return u3, H3, e, f, float(hr[3])


def j3_place(M, strap2):
    """the dowel's home angle th (rad, frame_of(u3), member 3 at home = member 2 at home: q3' = 0) maximising the angle between the
    dowel's swept arc (th + q3', q3' in the window, +- its angular half-width + 0.3 mm) and link 2's own strap points in the groove layer"""
    u3, H3, e, f, R3 = j3_frame(M)
    X = np.r_[np.asarray(strap2.vertices), trimesh.sample.sample_surface_even(strap2, 20000, seed=21)[0]]
    w = X - H3; z = w @ u3; pl = w - np.outer(z, u3); r = np.linalg.norm(pl, axis=1)
    band = (z > UP - 0.3) & (z < UP + J3_GD + 0.3) & (r > J3_RS - J3_GW / 2 - 0.6) & (r < J3_RS + J3_GW / 2 + 0.6)
    phi = np.arctan2(pl[band] @ f, pl[band] @ e)
    d = math.asin(min(1.0, (J3_GW / 2 + 0.3) / J3_RS)); lo, hi = math.radians(J3MIN), math.radians(J3MAX); best = None
    for th in np.radians(np.arange(0.0, 360.0, 0.5)):
        a_lo, a_hi = th + lo - d, th + hi + d; mid, half = 0.5 * (a_lo + a_hi), 0.5 * (a_hi - a_lo)
        gap = np.abs((phi - mid + np.pi) % (2 * np.pi) - np.pi) - half
        c = float(gap.min()) if len(gap) else np.pi
        if best is None or c > best[1]: best = (th, c)
    return best[0], math.degrees(best[1]), int(band.sum())


def j3_stop_parts(M, parts):
    """replace the J3 upper boss with its groove ring + the boss above it, add the stop dowel (member 3). Returns (parts, info)"""
    u3, H3, e, f, R3 = j3_frame(M)
    strap2 = next(p for p in parts if p[2].startswith("link 2 strap"))[3]
    th, clr_deg, nb = j3_place(M, strap2)
    d_touch = math.asin(J3_DR / J3_RS)                                            # radial groove end in the L1 mesh: the O2 dowel touches it at the stop
    a_lo, a_hi = th + math.radians(J3MIN) - d_touch, th + math.radians(J3MAX) + d_touch
    k = next(i for i, p in enumerate(parts) if p[2].startswith("J3 upper boss"))
    up_name = f"J3 upper boss + cap keep-out (O20, F+{UP + J3_GD:.2f}..F+{CROWN:.2f}, link 2; above the J3 stop groove ring)"
    ring = MIN.slotted_plate(H3, u3, UP, UP + J3_GD, R3, J3_RS, J3_GW / 2, a_lo, a_hi, n_ang=360)
    ring_name = (f"J3 upper boss groove ring keep-out (O20 x {J3_GD:g}, F+{UP:.2f}..F+{UP + J3_GD:.2f}, link 2: the J3 stop's arc groove {J3_GW:g} wide at r {J3_RS:g} over "
                 f"{math.degrees(a_hi - a_lo):.1f} deg; its ends = the stops at q3' {J3MIN:.2f} / {J3MAX:.2f} deg)")
    pd = H3 + J3_RS * (math.cos(th) * e + math.sin(th) * f)
    dowel, dname = j3_dowel(pd, u3)
    parts = list(parts[:k]) + [("l2", 2, up_name, REF.cyl(H3, u3, UP + J3_GD, CROWN, r=R3), "ti"), ("l2", 2, ring_name, ring, "ti")] + list(parts[k + 1:])
    parts.append(("l3", 3, dname, dowel, "steel"))
    info = dict(window_deg=[J3MIN, J3MAX], dowel_home_angle_deg=round(math.degrees(th), 2), groove_deg=[round(math.degrees(a_lo), 3), round(math.degrees(a_hi), 3)],
                groove_arc_deg=round(math.degrees(a_hi - a_lo), 2), web_deg=round(360 - math.degrees(a_hi - a_lo), 2), dowel_touch_half_deg=round(math.degrees(d_touch), 3),
                r_mm=J3_RS, dowel_d_mm=2 * J3_DR, groove_w_mm=J3_GW, groove_depth_mm=J3_GD, groove_layer_mm=[UP, UP + J3_GD], dowel_z_mm=[J3_DBOT, UP + J3_DTOP],
                dowel_into_groove_mm=J3_DTOP, groove_floor_clear_mm=round(J3_GD - J3_DTOP, 3), bearing_od_r_mm=5.5, rim_r_mm=R3,
                clearance_to_link2_strap_deg=round(clr_deg, 2), link2_strap_samples_in_band=nb,
                frame="angles in frame_of(u3); dowel centre in link 2's frame = home angle + q3' (C1: R2^T R3 = rot(u3, q3'), offset 0)",
                end_shape="L1 mesh: radial groove ends where the O2 dowel touches at the window edge; drawing: full-radius R1.05 ends, end centres 0.36 deg past the stop angle")
    return parts, info


def j3_dowel(pd, u3):
    """the stop dowel keep-out (member 3, home frame) and its part name: the red team's spec - ISO 8734 2 m6 x 5 ground to 3.90, F+0.10..F+4.00"""
    m = REF.cyl(pd, u3, J3_DBOT, UP + J3_DTOP, r=J3_DR)
    nm = (f"J3 stop dowel (ISO 8734 2 m6 x 5, 440C grade, ground to {UP + J3_DTOP - J3_DBOT:.2f}; pressed in a reamed O2.000 -0.005/0 hole through hub 3's lower plate "
          f"at r {J3_RS:g}, F+{J3_DBOT:.2f}..F+{UP + J3_DTOP:.2f}: {J3_DTOP:g} mm into link 2's groove, tip 0.15 off its floor; stops J3's own angle q3' at "
          f"{J3MIN:.2f} / {J3MAX:.2f} deg)")
    return m, nm


def j3_sweep(M, parts, info, dq=1.0):
    """pose-independent red team of the stop in link 2's frame: member 3 turned by q3' about J3's axis over the window and 2 deg past each
    edge; dowel samples vs the groove ring, the boss above it and link 2's strap (signed distance, mm; < 0 = inside)"""
    import igl
    u3, H3, e, f, R3 = j3_frame(M)
    dw = next(p for p in parts if p[2].startswith("J3 stop dowel"))[3]
    Xd = np.r_[np.asarray(dw.vertices), trimesh.sample.sample_surface_even(dw, 3000, seed=23)[0]]
    tgt = {nm: next(p for p in parts if p[2].startswith(nm))[3] for nm in ("J3 upper boss groove ring", "J3 upper boss + cap", "link 2 strap")}
    out = {}
    qs = np.r_[np.arange(J3MIN - 2.0, J3MAX + 2.0 + 1e-9, dq), J3MIN, J3MAX, J3MIN - 0.25, J3MAX + 0.25, J3MIN + 0.25, J3MAX - 0.25]
    for q in qs:
        R = S.rotm(u3, math.radians(float(q)))[0]; X = (Xd - H3) @ R.T + H3; row = {}
        for nm, m in tgt.items():
            row[nm] = float(igl.signed_distance(np.ascontiguousarray(X, float), np.ascontiguousarray(m.vertices, float), np.ascontiguousarray(m.faces, np.int64))[0].min())
        out[round(float(q), 3)] = row
    inside = {q: r for q, r in out.items() if J3MIN + 1e-6 < q < J3MAX - 1e-6}
    w_in = min(min(r.values()) for r in inside.values())
    return dict(rule="dowel (member 3) vs link 2's groove ring / boss / strap over q3' (signed mm, < 0 = metal in metal)",
                inside_window_min_mm=round(w_in, 4), at_J3MIN=out[round(J3MIN, 3)], at_J3MAX=out[round(J3MAX, 3)],
                past_J3MIN_0p25=out[round(J3MIN - 0.25, 3)], past_J3MAX_0p25=out[round(J3MAX + 0.25, 3)],
                inside_0p25=dict(lo=out[round(J3MIN + 0.25, 3)], hi=out[round(J3MAX - 0.25, 3)]),
                past_2deg=dict(lo=out[round(J3MIN - 2.0, 3)], hi=out[round(min(qs[qs >= J3MAX + 2.0 - 1e-9]), 3)] if (qs >= J3MAX + 2.0 - 1e-9).any() else None),
                verdict="stop" if (min(out[round(J3MIN - 0.25, 3)].values()) < -0.01 and min(out[round(J3MAX + 0.25, 3)].values()) < -0.01 and w_in > -0.005) else "CHECK")


def j3_tolerance():
    """the stop-angle stack (deg at r 7.5, 0.00764 deg per um) vs the window that keeps the verified numbers - the J3 red team's table
    (docs/research/conecut_mechanism_redteam.md section 4), restated: held low side must take pose 393 at -111.159 and must stop
    pose 392 at -112.488 (margin 0.74 in / 0.585 out of the nominal -111.904); held high side 2.99 in / 1.13 out"""
    um = 0.00764
    rnd = dict(dowel_hole_true_position_10um=10 * um, groove_end_centre_true_position_10um=10 * um, pin_a_bore_member3_datum=0.012, link2_J2_J3_bores=0.019)
    bias = dict(groove_width_2p10_plus0p02=[0.0, 10 * um], dowel_m6_radius=[-4 * um, -1 * um])
    rss = math.sqrt(sum(v * v for v in rnd.values())); lin_in = sum(rnd.values()) + 4 * um; lin_out = sum(rnd.values()) + 10 * um
    return dict(drawing="true position 0.02 (+-0.01 tangential) on the dowel hole and both groove end-arc centres, relative to the J3 bore and each part's "
                        "angular datum; groove walls concentric to the J3 bore within 0.02",
                random_deg={k: round(v, 3) for k, v in rnd.items()}, bias_deg=bias, rss_deg=round(rss, 3), worst_in_deg=round(lin_in, 3), worst_out_deg=round(lin_out, 3),
                at_pm0p02_worst_deg=0.41, at_iso2768f_worst_deg=0.87, margin_held_low_deg=[0.74, 0.585], margin_held_high_deg=[2.99, 1.13],
                acceptance="-112.40 <= J3MIN <= -111.25 and 119.85 <= J3MAX <= 123.78, read on the J3 encoder at assembly",
                verdict=("fits: worst %.2f in / %.2f out inside the 0.74 / 0.585 held margins at +-0.01; +-0.02 (0.41) still fits; ISO 2768-f (0.87) fails"
                         % (lin_in, lin_out)),
                source=REDTEAM + " section 4 (stack) / verdict 3 (acceptance bands)")


def j3_dowel_calc():
    """hand calc of the O2 440C stop dowel at a jam push of 6 N.m and a deliberate 10 N.m about J3 (force at r 7.5 mm)"""
    out = {}
    for T in (6.0, 10.0):
        F = T / (J3_RS / 1000.0); d = 2 * J3_DR; A = math.pi * d ** 2 / 4; Z = math.pi * d ** 3 / 32
        lever = 0.15 + J3_DTOP / 2; sb = F * lever / Z; tau = F / A; bear = F / (d * J3_DTOP)
        out[f"{T:g}Nm"] = dict(F_N=round(F, 0), shear_MPa=round(tau, 0), bending_MPa=round(sb, 0), bearing_on_Ti_groove_MPa=round(bear, 0),
                               SF_shear_vs_0p58x1900=round(0.58 * 1900 / tau, 2), SF_bending_vs_1900=round(1900 / sb, 2), SF_bearing_vs_Ti_880=round(880 / bear, 2),
                               J3_bearing1_s0=round(280.0 / (155.0 * T), 2))
    out["note"] = ("440C 58 HRC yield ~1900 MPa (shear 0.58 x); bearing on the Ti-6Al-4V groove end over the 0.85 mm engagement (projected; the red team "
                   "rates it on Fbry ~1.3 GPa: SF 1.66 at 10 N.m); the single-dowel force returns through J3's MR117 pair as a radial load, 155 N per N.m on "
                   "bearing 1 (C0r ~280 N): s0 = 1 at 1.81 N.m about J3 - the stop's rating; the cuff (slips ~1.06 N.m) is the torque fuse "
                   "(docs/research/conecut_mechanism_redteam.md section 1-2; the same caveat as every gen-4..7 single-dowel stop)")
    return out


# ---------------------------------------------------------------------------------------------------- hooks into the gen-7 builder
_bp0, _adj0 = SL.build_parts, SL.set_adjacent
_J3 = {}


def build_parts(M, lg, dg, knee_geom=None):
    parts, stack = _bp0(M, lg, dg, knee_geom)
    parts, info = j3_stop_parts(M, parts)
    info["sweep"] = j3_sweep(M, parts, info); info["tolerance"] = j3_tolerance(); info["dowel_calc"] = j3_dowel_calc()
    stack["stops"]["J3"] = info; _J3.update(info)
    print(f"J3 stop: home {info['dowel_home_angle_deg']} deg, groove {info['groove_arc_deg']} deg (web {info['web_deg']}), strap clearance "
          f"{info['clearance_to_link2_strap_deg']} deg; sweep {json.dumps(info['sweep'], default=float)}; tol {info['tolerance']['linear_deg']} lin / {info['tolerance']['rss_deg']} rss", flush=True)
    return parts, stack


def set_adjacent(parts):
    _adj0(parts)
    find = lambda s: next((p for p in parts if p[2].startswith(s)), None)
    pairs = [("J3 stop dowel", b) for b in ("J3 upper boss groove ring", "J3 upper boss + cap", "link 2 strap")] + \
            [(a, "J3 upper boss groove ring") for a in ("E strap", "knee link", "pad mount", "arm pad", "knee stop web", "knee stop tooth", "pin a retainer",
                                                         "knee link bearing boss a", "knee link bearing boss b")]
    for a_, b_ in pairs:
        A, Bp = find(a_), find(b_)
        if A is None or Bp is None or A[1] == Bp[1]: continue
        XA = np.r_[np.asarray(A[3].vertices), trimesh.sample.sample_surface_even(A[3], 1500, seed=3)[0]]
        BASE.ADJ_PAIRS.append((A[2][:24], A[1], XA, Bp[2][:24], Bp[1], np.ascontiguousarray(Bp[3].vertices, float), np.ascontiguousarray(Bp[3].faces, np.int64)))


def check_frames(M, dd, parts, stack):
    """gen-7 check_frames (copied; build_slipper_l1.check_frames) on this chain + (i) the J3-stop extremes and the knee extremes as check
    poses, (ii) J3's dowel in its groove from the posed member frames (q3' read off R2^T R3 vs the model's q3 + phi)"""
    import scene_export as SE, igl
    from scipy.spatial.transform import Rotation as Rot
    M.Q, M.s, M.RS, M.X, M.K, M.q = M._bench; B = M.B
    allp = np.array([[B.poses[i][k] for k in ("plane", "elev", "axial", "flex", "pron")] for i in range(len(B.idx))])
    K = chain(M, allp)
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    el = lambda i: B.poses[i]["elev"]; pl = lambda i: B.poses[i]["plane"]
    behind = [i for i in taken if "back" in B.clip[i].lower() or (pl(i) < -30 and el(i) > 20)]
    across = [i for i in taken if pl(i) >= 100 and el(i) >= 40]
    kin = [i for i in range(len(B.idx)) if K["ok"][i] and K["kok"][i] and K["res"][i] < 0.5]
    pick = {"arm at side": min(taken, key=el), "first": taken[0], "middle": taken[len(taken) // 2], "highest": max(taken, key=el),
            "2nd highest": next(j for j in sorted(taken, key=el)[::-1] if j != max(taken, key=el))}
    if behind: pick["behind the back"] = max(behind, key=lambda i: -pl(i))
    if across: pick["across the body"] = max(across, key=pl)
    tgt = np.array([30.0, 150.0, -60.0]); pick["overhead raise peak"] = min(kin, key=lambda i: float(np.linalg.norm(allp[i, :3] - tgt)))
    st1 = [i for i in taken if K["state"][i] == 1]
    if st1: pick["K most open, taken (drive extreme)"] = max(st1, key=lambda i: abs(K["dK"][i]))
    st1k = [i for i in kin if K["state"][i] == 1]
    if st1k: pick["K most open, closes (nearest stop B)"] = max(st1k, key=lambda i: abs(K["dK"][i]))
    pick["J3 q3' min, taken (nearest J3 stop low)"] = min(taken, key=lambda i: K["q3p"][i])
    pick["J3 q3' max, taken (nearest J3 stop high)"] = max(taken, key=lambda i: K["q3p"][i])
    pick["knee angle min, taken"] = min(taken, key=lambda i: K["Kn"]["ang"][i]); pick["knee angle max, taken"] = max(taken, key=lambda i: K["Kn"]["ang"][i])
    src = trimesh.load(os.path.join(dd, "exo.glb")); out = []
    U, C, F4, hr = MIN.joints4(M); D = M.D; st = stack["stops"]; u3, H3, e3, f3, _ = j3_frame(M)
    for lab, i in pick.items():
        pz = allp[i]; fr = MIN.frame_dict(K, i, pz, pz, False)
        X, _ = SE.frame_xforms(fr); meshes = {}; posed = {}
        for node in src.graph.nodes_geometry:
            g = node.split("|")[0]
            if g == "F" or (g == "H" and not any(s_ in node for s_ in ("arm pad", "pad mount", "pin b retainer"))): continue
            T_, gn = src.graph[node]; m = src.geometry[gn].copy(); m.apply_transform(T_); R, t = X[g]
            m.vertices = m.vertices @ np.asarray(R).T + t; meshes.setdefault(g, []).append(m); posed["|".join(node.split("|")[:2])] = m
        meshes = {g: trimesh.util.concatenate(v) for g, v in meshes.items()}
        old = (M.Q, M.s, M.RS, M.X, M.K, M.q); BASE.swap_in(M, K); res = {}
        try:
            for name, (m, Xp) in list(M.rigid.items()) + list(M.link_pts.items()):
                Pw = M.world(m, i, Xp); g = "l1a" if name == "hub1" else SL.GRP_OF[m]
                if name == "hub2": g = "l2"
                d = np.sqrt(igl.point_mesh_squared_distance(np.ascontiguousarray(Pw, float), np.ascontiguousarray(meshes[g].vertices, float),
                                                            np.ascontiguousarray(meshes[g].faces, np.int64))[0])
                win = igl.fast_winding_number(np.ascontiguousarray(meshes[g].vertices, float), np.ascontiguousarray(meshes[g].faces, np.int64), np.ascontiguousarray(Pw, float))
                dout = np.where(win > 0.5, 0.0, d)
                if name == "hub2":
                    dl = np.sqrt(igl.point_mesh_squared_distance(np.ascontiguousarray(Pw, float), np.ascontiguousarray(meshes["l1b"].vertices, float),
                                                                 np.ascontiguousarray(meshes["l1b"].faces, np.int64))[0]); d = np.minimum(d, dl)
                if name in ("hubK", "hub2", "hub3"):
                    k = {"hubK": 1, "hub2": 2, "hub3": 3}[name]; cen = C[k] + F4[k] * U[k]; w = Xp - cen; rr = np.linalg.norm(w - (w @ U[k])[:, None] * U[k], axis=1)
                    rs, hw = (MIN.SLOT_RS, MIN.DOWEL_R + MIN.SLOT_CLR) if k < 3 else (J3_RS, J3_GW / 2)
                    inslot = (rr > rs - hw - 0.6) & (rr < rs + hw + 0.6)
                    res[name + " (slot band)"] = [round(float(d[inslot].max()), 4) if inslot.any() else None, int(inslot.sum())]
                    d = d[~inslot]; dout = dout[~inslot]
                res[name] = [round(float(d.max()), 4), round(float(np.percentile(d, 95)), 4), round(float(dout.max()), 4)]
            fdev = 0.0
            for g, mem, nm, mesh, mat in parts:
                Vw = M.world(mem, i, np.asarray(mesh.vertices)); Pg = np.asarray(posed[f"{g}|{nm}"].vertices)
                fdev = max(fdev, float(np.abs(Vw - Pg).max()))
            R1, _ = M.T(1, i); R1b, _ = M.T(7, i); R2, t2 = M.T(2, i); R3, t3 = M.T(3, i)
            dK = float(np.degrees(Rot.from_matrix(R1.T @ R1b).as_rotvec() @ D.uK)); q2 = float(np.degrees(Rot.from_matrix(R1b.T @ R2).as_rotvec() @ D.u[1]))
            q3f = float(np.degrees(Rot.from_matrix(R2.T @ R3).as_rotvec() @ u3))
            inside = {}
            for key, ang in (("K", dK), ("J2", q2)):
                s_ = st[key]; c_ = s_["dowel_home_angle_deg"] + ang; a0, a1 = s_["slot_deg"]
                dd_ = math.degrees(math.asin((MIN.DOWEL_R + MIN.END_CLR) / MIN.SLOT_RS)); lo_, hi_ = a0 + dd_, a1 - dd_
                pos = (c_ - lo_) % 360.0
                inside[key] = dict(angle_deg=round(ang, 3), from_stop_lo_deg=round(pos, 3), to_stop_hi_deg=round((hi_ - lo_) - pos, 3), inside=bool(pos <= (hi_ - lo_) + 0.01 or pos >= 360.0 - 0.01))
            # J3: the dowel centre (member 3) read in link 2's posed frame, its angle vs the groove ends
            s3 = st["J3"]; th = math.radians(s3["dowel_home_angle_deg"]); pdw = H3 + J3_RS * (math.cos(th) * e3 + math.sin(th) * f3)
            pw = R3 @ pdw + t3; p2 = R2.T @ (pw - t2) - H3; a2 = math.degrees(math.atan2(float(p2 @ f3), float(p2 @ e3)))
            a0, a1 = s3["groove_deg"]; dt = s3["dowel_touch_half_deg"]; pos = (a2 - (a0 + dt)) % 360.0; span = (a1 - dt) - (a0 + dt)
            inside["J3"] = dict(angle_deg=round(q3f, 3), model_q3p_deg=round(float(K["q3p"][i]), 3), frame_vs_model_deg=round(abs(wr(q3f - float(K["q3p"][i]))), 4),
                                from_stop_lo_deg=round(pos, 3), to_stop_hi_deg=round(span - pos, 3), inside=bool(pos <= span + 0.01 or pos >= 360.0 - 0.01),
                                dowel_r_in_link2_mm=round(float(np.linalg.norm(p2 - (p2 @ u3) * u3)), 4))
        finally: M.Q, M.s, M.RS, M.X, M.K, M.q = old
        worst = max(v[0] for k, v in res.items() if not k.startswith(("L1", "L2")) and "slot band" not in k and v[0] is not None)
        worst_out = max(v[2] for k, v in res.items() if not k.startswith(("L1", "L2")) and "slot band" not in k and v[0] is not None)
        worst_l = max(v[0] for k, v in res.items() if k in ("L1a", "L1b", "L2"))
        drv = {k: res[k] for k in ("crank", "roller", "horn") if k in res}
        out.append(dict(label=lab, bench_pose=int(i), pose=[round(float(x), 2) for x in pz[:3]], taken=bool(i in set(taken)), state=int(K["state"][i]),
                        rigid_samples_max_mm=round(worst, 4), rigid_samples_outside_max_mm=round(worst_out, 4), strap_samples_max_mm=round(worst_l, 4),
                        drive_samples_mm=drv, per_part=res, frame_dev_mm=round(fdev, 6), res_deg=round(float(K["res"][i]), 4), knee_angle=round(float(K["Kn"]["ang"][i]), 2),
                        q3p_deg=round(float(K["q3p"][i]), 3), m3e=round(float(K["m3e"][i]), 2), stops=inside))
        print(f"  check {lab:42s} pose {i} {np.round(pz[:3], 1)} st {int(K['state'][i]):+d}: rigid vs glb max {worst:.4f} mm, outside {worst_out:.4f}, straps {worst_l:.3f}, "
              f"frames dev {fdev:.2e}, knee {K['Kn']['ang'][i]:.1f}, q3' {K['q3p'][i]:.2f} (frames {q3f:.2f}), dowels in slot K {inside['K']['inside']} J2 {inside['J2']['inside']} "
              f"J3 {inside['J3']['inside']} ({inside['J3']['from_stop_lo_deg']:.2f} / {inside['J3']['to_stop_hi_deg']:.2f})", flush=True)
    return out


# ---------------------------------------------------------------------------------------------------- post-processing (J3 stop labels, design.json)
def relabel_clips(M, dd):
    """clip frames held because of the J3 stop: why 'fold' -> 'j3stop' (make_clips knows only ok / kok); build.json clip reasons updated"""
    Cp = os.path.join(dd, "clips.json"); C = json.load(open(Cp)); Bp = os.path.join(dd, "build.json"); BJ = json.load(open(Bp)); tot = 0; per = {}
    for cl in C["clips"]:
        prev = sum(1 for f in cl["frames"] if f["held"] and f.get("why") == "j3stop")
        if prev: per[cl["name"]] = prev; tot += prev
        idx = [k for k, f in enumerate(cl["frames"]) if f["held"] and f.get("why") == "fold"]
        if not idx: continue
        want = np.array([cl["frames"][k]["want"] for k in idx], float); K = chain(M, want); n = 0
        for j, k in enumerate(idx):
            if K["j3stop"][j]: cl["frames"][k]["why"] = "j3stop"; n += 1
        if n:
            per[cl["name"]] = per.get(cl["name"], 0) + n; tot += n; r = BJ.get("clips", {}).get(cl["name"], {}).get("reasons")
            if r is not None: r["fold"] = r.get("fold", 0) - n; r["j3stop"] = n; r.pop("fold") if r["fold"] == 0 else None
    json.dump(C, open(Cp, "w"), separators=(",", ":"))
    BJ["j3stop_clip_frames"] = dict(total=tot, per_clip=per); json.dump(BJ, open(Bp, "w"), indent=1, default=float)
    return dict(total=tot, per_clip=per)


def j3_vs_frames(M, dd):
    """q3' and the knee angle over every non-held clip frame (the frames the judges read): range vs the stop window and the knee window"""
    C = json.load(open(os.path.join(dd, "clips.json"))); want = []; held = 0
    for cl in C["clips"]:
        for f in cl["frames"]:
            if f["held"]: held += 1; continue
            want.append(f["want"])
    K = chain(M, np.array(want, float)); o = K["ok"] & K["kok"]
    q = K["q3p"][o]; a = np.asarray(K["Kn"]["ang"])[o]
    return dict(frames=len(want), held=held, q3p_deg=[round(float(q.min()), 2), round(float(q.max()), 2)],
                margin_to_stops_deg=[round(float(q.min() - J3MIN), 2), round(float(J3MAX - q.max()), 2)],
                knee_deg=[round(float(a.min()), 2), round(float(a.max()), 2)], knee_stop_margin_deg=round(180.0 - CFG["ang_min"] - float(a.max()), 2))


def post(dd, M=None):
    if M is None: M, _ = fit()
    rl = relabel_clips(M, dd) if os.path.exists(os.path.join(dd, "clips.json")) else None
    BJ = json.load(open(os.path.join(dd, "build.json")))
    if rl is not None: BJ["j3_on_clip_frames"] = j3_vs_frames(M, dd)
    BJ["verified"] = VERIFIED
    json.dump(BJ, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    Dp = os.path.join(dd, "design.json"); D = json.load(open(Dp)); st = BJ.get("stops", {}).get("J3") or _J3
    D["source"] = (f"docs/concepts/{ID}.md (the verified config: docs/concepts/rows/{ID}.json best_params on the claim model's PARAMS (SN_CELL=lead; "
                   f"= docs/concepts/verify/{ID}.py BEST): the gen-7 lead slipper-nose-knuckle-3r row + the re-proportioned knee (stk 6.0 MR63ZZ pairs, lE "
                   f"{CFG['lE']}, lc {CFG['lc']}, phiE {CFG['phiE']}, phib {CFG['phib']}, ang_min {CFG['ang_min']}) + the J3 hard stop on q3' in [{J3MIN}, {J3MAX}]), "
                   f"fit on Bench(60,160) fast at fold margin 5 = the shape the verifier wore frozen on Bench(110,360) exact (v_gap 18.28, score 93.35; held out 22.38)")
    D["label"] = f"conecut-knee-knuckle-3r (verified config, knee re-proportioned + J3 stop [{J3MIN:.2f}, {J3MAX:.2f}], fit Bench(60,160), fold margin 5), L1 keep-out"
    D["built_with"] = ("pipeline/concept_l1/build_conecut_l1.py (imports build_slipper_l1.py unchanged: every gen-7 L1 part from THIS model's fit) + the J3 stop: "
                       "groove ring under link 2's J3 upper boss + the O2 dowel in hub 3's lower plate")
    D["params"] = dict(CFG); D["fits"] = FITS
    D.setdefault("build_fixes", {}).update(j3_stop=True, knee="re-proportioned (conecut)", d1_fits_dup_removed=True, d2_rss=True, d3_spacer_note=True)
    for j in D.get("joints", []):
        if j.get("joint") == "J3":
            j["part"] = (f"O20 x 12.25 v5 hub, MR117-2RS pair, encoder; HARD STOP on J3's own angle q3' (link 2 -> member 3) at {J3MIN:.2f} / {J3MAX:.2f} deg: "
                         f"ISO 8734 O2 m6 440C dowel pressed through hub 3's lower plate at r {J3_RS:g}, in a {J3_GW:g} x {J3_GD:g} arc groove "
                         f"({st.get('groove_arc_deg')} deg, web {st.get('web_deg')} deg) under link 2's ring - inside the O20 stack")
    D["j3_stop"] = st
    ps = D.get("passive", {})
    if "knee_stop" in ps:
        ps["knee_stop"]["note"] = (f"conecut's knee runs {VERIFIED['knee']['ang_held'][0]}..{VERIFIED['knee']['ang_held'][1]} deg held out: "
                                   f"{VERIFIED['knee']['margin_mm'][0]} / {VERIFIED['knee']['margin_mm'][1]} mm in d inside the window (gen 7: 0.33 mm)")
    D["verified"] = VERIFIED
    json.dump(D, open(Dp, "w"), indent=1, default=float)
    print(f"post: clips relabelled {rl}; J3 on clip frames {BJ.get('j3_on_clip_frames')}", flush=True)


# ---------------------------------------------------------------------------------------------------- retarget the gen-7 builder and run it
SL.RL, SL.RF, SL.SC, SL.S, SL.PK = CC, CC.RF, CC.SC, CC.S, CC.PK
SL.ID, SL.BEST, SL.CFG, SL.FITS = ID, BEST, CFG, FITS
SL.NOSE_R = float(CC._clamp(dict(CC.PARAMS, **CFG))["nose_r"])
SL.L1Model, SL.fit = L1Model, fit
SL.chain = MIN.chain = BASE.chain = chain
SL.build_parts, SL.set_adjacent, SL.check_frames = build_parts, set_adjacent, check_frames


def patch_j3(dd):
    """rewrite ONLY the J3 stop dowel in an existing build to the red team's spec (exo.glb geometry + name, parts_full.json, build.json
    stops.J3 incl. the sweep re-run on the glb meshes); every other part is untouched (the gen-8 build ran with the claim's first dowel
    F+0..F+3.95: 0.05 mm lower tip, 0.10 mm longer at the skin end - inside the plate)"""
    M, _ = fit(); BJ = json.load(open(os.path.join(dd, "build.json"))); st = BJ["stack"]["stops"]["J3"] if "stack" in BJ else BJ["stops"]["J3"]
    u3, H3, e, f, R3 = j3_frame(M); th = math.radians(st["dowel_home_angle_deg"]); pd = H3 + J3_RS * (math.cos(th) * e + math.sin(th) * f)
    dw, dname = j3_dowel(pd, u3)
    sc = trimesh.load(os.path.join(dd, "exo.glb")); old = [g for g in sc.geometry if g.split("|")[1].startswith("J3 stop dowel")]
    assert len(old) == 1, old
    k = old[0].split("|")[2]; new = f"l3|{dname}|{k}"
    node = next(n for n in sc.graph.nodes_geometry if sc.graph[n][1] == old[0]); T_ = sc.graph[node][0]
    assert np.allclose(T_, np.eye(4)), T_
    sc.delete_geometry(old[0]); sc.add_geometry(dw, node_name=new, geom_name=new); sc.export(os.path.join(dd, "exo.glb"))
    PF = json.load(open(os.path.join(dd, "parts_full.json")))
    for p in PF["parts"]:
        if p["name"].startswith("J3 stop dowel"):
            mm = dw.copy(); mm.merge_vertices(); vol = abs(mm.volume)
            p.update(name=dname, vol_cm3=round(vol / 1000, 3), mass_g=round(vol / 1000 * BASE.STEEL, 2), valid=bool(mm.is_watertight and mm.is_volume),
                     pieces=int(len(mm.split(only_watertight=False))), faces=len(dw.faces))
    json.dump(PF, open(os.path.join(dd, "parts_full.json"), "w"), indent=1)
    sc2 = trimesh.load(os.path.join(dd, "exo.glb")); parts = []
    for g in sc2.geometry:
        gp, nm = g.split("|")[:2]
        if nm.startswith(("J3 stop dowel", "J3 upper boss", "link 2 strap")): parts.append((gp, {"l2": 2, "l3": 3}[gp], nm, sc2.geometry[g], "ti"))
    st.update(dowel_z_mm=[J3_DBOT, UP + J3_DTOP], dowel_into_groove_mm=J3_DTOP, groove_floor_clear_mm=round(J3_GD - J3_DTOP, 3),
              dowel_part=dname, sweep=j3_sweep(M, parts, st), tolerance=j3_tolerance(), dowel_calc=j3_dowel_calc(),
              patched="dowel rewritten to the red team's spec by build_conecut_l1.py --patch-j3 (glb node, parts_full.json, this block)")
    for key in ("stack", None):
        tgt = BJ[key]["stops"] if key else BJ.get("stops")
        if tgt is not None: tgt["J3"] = st
    json.dump(BJ, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float); _J3.update(st)
    print(f"patched J3 dowel -> {dname}; sweep {json.dumps(st['sweep'], default=float)[:600]}", flush=True)
    return M


def main():
    out = "l1_conecut-knee"
    if "--out" in sys.argv: out = sys.argv[sys.argv.index("--out") + 1]
    else: sys.argv += ["--out", out]
    dd = os.path.join(BASE.FULL, "designs", out)
    if "--post-only" in sys.argv:
        post(dd); return
    if "--patch-j3" in sys.argv:
        M = patch_j3(dd); post(dd, M); return
    t0 = time.time()
    SL.main()
    post(dd)
    print(f"conecut L1 done in {time.time() - t0:.0f} s -> {dd}", flush=True)


if __name__ == "__main__":
    main()
