"""J3 hard stop red team: loads, stresses, bearings, impact, tolerance window and CAD numbers for the ISO 8734 2 m6 440C dowel
(pressed in hub 3's lower plate = member 3, r 7.5) running in an arc groove under link 2's boss (conecut-knee-knuckle-3r).
Reads stop_geo.json (extract.py). Every number in docs/research/conecut_mechanism_redteam.md comes from here.

    python3 docs/research/conecut_mechanism/stop.py [stop_geo.json] -> results.json next to it
"""
import json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "stop_geo.json")))
R = {}
P = G["params"]; J3MIN, J3MAX = P["J3MIN"], P["J3MAX"]

# ---------------- geometry (v5 O20 stack levels from the pad's skin face F, docs/HARDWARE.md) ----------------
RD, D_PIN = 7.5, 2.0                      # dowel radius from the J3 axis, dowel diameter
S_, U0, L1, B1, B2, H1, U1 = 3.00, 3.15, 3.65, 6.65, 7.25, 8.75, 10.25
GAP = U0 - S_                             # 0.15 running gap
W_G = 2.10                                # groove width (end radius 1.05)
BRG_BORE_R, HUB_R = 5.5, 10.0             # MR117 OD seat, boss rim
D_PERP_MIN = 83.5                         # knee transmission arm (verifier, taken poses)
C0R_MR117, CR_MR117 = 280.0, 700.0        # N, 7 x 11 x 3 deep groove (docs/HARDWARE.md: ~0.28 / ~0.7 kN, confirm with supplier)
PC1, PC2 = 3.95, 9.95                     # DB pair pressure centres (bearing centres 5.15 / 8.75 +- 1.2; ~6 mm apart, HARDWARE.md)
deg_per_mm = 180 / math.pi / RD
R["deg_per_um_at_rd"] = round(deg_per_mm / 1000, 5)

# ---------------- materials ----------------
E_ST, NU_ST, SY_440C = 200e3, 0.28, 1900.0      # 440C (1.4125) hardened >= 56 HRC: yield ~1.9 GPa
TAU_Y_440C = 0.58 * SY_440C
E_TI, NU_TI, SY_TI, FBRY_TI = 114e3, 0.34, 830.0, 1300.0   # Ti-6Al-4V annealed; bearing yield (MMPDS class, e/D 1.5) ~1.3-1.4 GPa
E_STAR = 1 / ((1 - NU_ST ** 2) / E_ST + (1 - NU_TI ** 2) / E_TI)

# ---------------- moment about J3 that reaches the stop ----------------
# (a) chain path: J1 / J2 free, J3 on the stop -> the arm's moment about GH that the chain passes to the base lies along
#     u1 x u2; its J3 share is s3 = |unit(u1 x u2) . u3| at the stopped / near-stop poses (extract.py)
stops = {lab: [r for r in G[lab] if r["why"] == "j3stop"] for lab in ("bench110", "held", "fit_bench")}
near = {lab: [r for r in G[lab] if r["kin"] and abs(r["q3p"] - J3MIN) < 6] for lab in ("bench110", "held")}
s3_all = [r["s3"] for lab in stops for r in stops[lab]] + [r["s3"] for lab in near for r in near[lab]]
s3max = max(s3_all)
R["s3"] = dict(max=s3max, min=min(s3_all), n=len(s3_all),
               note="J3 moment per N.m of GH moment through the stopped chain (stopped + kin-ok poses within 6 deg of J3MIN)")
# (b) cuff twist path: liner friction on the skin limits the twist moment: mu * p * A * r_arm
A_CUFF, R_ARM = 68e-4, 0.048              # m2 (dynamics judge's cuff shell), upper-arm radius at the cuff for 185 cm
slip = {f"mu{mu}_p{p / 1000:g}kPa": round(mu * p * A_CUFF * R_ARM, 2) for mu in (0.5, 1.0) for p in (6500.0, 14000.0)}
R["cuff_slip_Nm"] = slip
CASES = {"felt (judge free-moment line 1 N.m at GH x s3)": 1.0 * s3max,
         "cuff slip, fabric liner at strap preload (mu 0.5, 6.5 kPa)": slip["mu0.5_p6.5kPa"],
         "cuff slip, silicone liner at the 14 kPa budget (mu 1.0)": slip["mu1.0_p14kPa"],
         "lock (judge lock line 10 N.m at GH x s3)": 10.0 * s3max,
         "abuse / sizing (claim): 10 N.m about J3": 10.0}

# ---------------- impact at the stop: 3-body lumped torsion model about the J3 axis ----------------
# arm (bone, forearm + hand, elbow 90) --tissue k_t, c_t-- pad group (arm pad + cuff + BOTTOM) --knee k_k-- member 3 --stop k_s (unilateral)-- link 2
I_ARM, K_T, C_T = 0.065, 1.72, 0.02       # kg m2 (1.36 kg forearm at 0.12 m + 0.51 kg hand at 0.30 m + own); judge tissue torsion N.m/rad, N.m.s/rad
I_PAD = 0.1176 * 0.05 ** 2                 # judge's arm parts 117.6 g on a r 50 mm shell (upper bound)
mE = 0.008 * 0.003 * 4430 * (P["lE"] - 4.5 - 11.0) / 1000   # E strap 8 x 3 Ti from r 11 to the boss
I3 = (mE * ((P["lE"] - 4.5) ** 3 - 11.0 ** 3) / (3 * (P["lE"] - 4.5 - 11.0)) * 1e-6 + 1.4e-3 * (P["lE"] / 1000) ** 2
      + 2.5e-3 * ((P["lE"] + 3) / 1000) ** 2 + 0.5 * 4.2e-3 * 0.010 ** 2)
# stop stiffness (series): J3 MR117 DB pair radial ~10 N/um at bearing 1 (cantilevered load), dowel shear, contact, boss web
k_brg, k_dowel_sh = 1.0e4, 0.9 * 77e3 * math.pi / (GAP + 0.85 / 2)
k_contact, k_web = E_STAR * 0.85, 2.0e5
k_lin = 1 / (1 / k_brg + 1 / k_dowel_sh + 1 / k_contact + 1 / k_web)
K_S = k_lin * RD ** 2 / 1000               # N.m/rad
# knee path (member 3 <-> pad group): E strap in-plane bending (I = 3 x 8^3 / 12) at its tip, MR63ZZ pairs at pins a / b
L_E = P["lE"] - 11.0; k_strap = 3 * E_TI * (3 * 8 ** 3 / 12) / L_E ** 3; k_pins = 2500.0
K_K = 1 / (1 / k_strap + 1 / k_pins) * D_PERP_MIN ** 2 / 1000
R["impact_model"] = dict(I3_kgm2=round(I3, 7), I_pad=I_PAD, I_arm=I_ARM, k_stop_Nm_rad=round(K_S, 1), k_lin_N_mm=round(k_lin, 0),
                         k_knee_Nm_rad=round(K_K, 1), k_tissue=K_T, knee_twist_deg_per_Nm=round(math.degrees(1 / K_K), 3))


def impact(w0, t_react=0.15, t_stop=0.10, slip_Nm=None, dt=2e-6, T=0.6):
    """arm driven at w0 into the stop for t_react, then decelerated to rest over t_stop (the wearer reacts); returns the
    peak stop moment and the peak cuff twist. x = rotation past first contact (rad), member 3 at the stop when x3 > 0"""
    xa = xp = x3 = 0.0; va = vp = v3 = w0; peak = 0.0; tw = 0.0; t = 0.0
    while t < T:
        if t < t_react: aa = 0.0
        elif t < t_react + t_stop: aa = -w0 / t_stop
        else: aa = 0.0; va = 0.0
        Mt = K_T * (xa - xp) + C_T * (va - vp)
        if slip_Nm is not None and abs(Mt) > slip_Nm: Mt = math.copysign(slip_Nm, Mt)
        Mk = K_K * (xp - x3)
        Ms = K_S * x3 if x3 > 0 else 0.0
        vp += (Mt - Mk) / I_PAD * dt; v3 += (Mk - Ms) / I3 * dt
        va += aa * dt
        xa += va * dt; xp += vp * dt; x3 += v3 * dt
        peak = max(peak, Ms); tw = max(tw, abs(xa - xp)); t += dt
    return round(peak, 3), round(math.degrees(tw), 1)


imp = {}
for dps in (30, 90, 152.5, 286):
    w0 = math.radians(dps)
    imp[f"{dps}dps"] = dict(free=impact(w0), slip_1p1=impact(w0, slip_Nm=slip["mu0.5_p6.5kPa"]),
                            inertia_only_Nm=round(w0 * math.sqrt(I3 * K_S), 3))
R["impact"] = imp
R["impact_note"] = ("J3 speed: nominal-case clip peaks of the closest built design (user_slipper_nose dynamics.json): 42.6-152.5 dps "
                    "(Comb hair 152.5); 286 dps = the judge's all-joint peak. The 4347 dps reading is the mu 0.37 plain-bearing stick-slip "
                    "case, not a swing. No fit-clip frame comes within 49 deg of the stop (clips q3' -62.4..101.4).")

# ---------------- dowel and groove at each load case, for three engagement depths ----------------
def stress(M3, e):
    F = M3 * 1000 / RD                                   # N at the dowel
    Fk = M3 * 1000 / D_PERP_MIN
    arm = GAP + e / 2                                    # bending arm from the pad face (uniform load along e)
    sig_b = 32 * F * arm / (math.pi * D_PIN ** 3); tau = F / (math.pi * D_PIN ** 2 / 4)
    p_proj = F / (D_PIN * e)                             # groove end, projected (conformal: Hertz b ~ R here)
    Reff = 1 / (1 / 1.0 - 1 / 1.05); b = math.sqrt(4 * F / e * Reff / (math.pi * E_STAR))
    p_hz = math.sqrt(F / e * E_STAR / (math.pi * Reff))
    # pad hole (Ti, 3.0 press length): force + moment couple, linear distribution
    p_hole = F / (D_PIN * 3.0) + 6 * F * GAP / (D_PIN * 3.0 ** 2)
    zd = U0 + e / 2                                      # contact centroid level
    Fb = F + Fk                                          # J3 bearings take the dowel force + the knee link force (upper bound)
    r1 = Fb * (PC2 - zd) / (PC2 - PC1); r2 = Fb * (zd - PC1) / (PC2 - PC1)
    return dict(F_dowel_N=round(F, 1), F_knee_N=round(Fk, 1), dowel_shear_MPa=round(tau, 1), SF_shear=round(TAU_Y_440C / tau, 2),
                dowel_bend_MPa=round(sig_b, 1), SF_bend=round(SY_440C / sig_b, 2), groove_proj_MPa=round(p_proj, 1),
                SF_groove=round(FBRY_TI / p_proj, 2), hertz_p0_MPa=round(p_hz, 0), hertz_b_mm=round(b, 3), pad_hole_MPa=round(p_hole, 1),
                J3_brg1_N=round(r1, 1), J3_brg2_N=round(r2, 1), s0_brg1=round(C0R_MR117 / abs(r1), 2),
                J12_tilt_per_brg_N=round(M3 / max(s3max, 1e-6) * 1000 / 6.0, 1))


R["cases"] = {k: {"M3_Nm": round(v, 3), **{f"e{e}": stress(v, e) for e in (0.85, 1.35, 1.85)}} for k, v in CASES.items()}
# the moment about J3 at which J3's bearing 1 reaches s0 = 1 (C0r), and J1 / J2 tilt reaches C0r per bearing
f1 = (1000 / RD + 1000 / D_PERP_MIN) * (PC2 - (U0 + 0.425)) / (PC2 - PC1)
R["M3_at_s0_1_J3_brg1_Nm"] = round(C0R_MR117 / f1, 2)
R["M_GH_at_C0r_J1J2_tilt_Nm"] = round(C0R_MR117 * 6.0 / 1000, 2)

# ---------------- press fit (pad: Ti-6Al-4V, through hole, 3.0 long, 1.5 mm ligament to the rim) ----------------
a, c = D_PIN / 2, D_PIN / 2 + 1.5
geo = (c ** 2 + a ** 2) / (c ** 2 - a ** 2)
pf = {}
for lab, delta in (("H7_m6_loose (-8 um clearance .. )", -0.008), ("ream 1.995-2.000 min (2 um)", 0.002), ("ream max (13 um)", 0.013)):
    if delta <= 0: pf[lab] = dict(p_MPa=0.0, pull_N=0.0); continue
    p = (delta / D_PIN) / ((geo + NU_TI) / E_TI + (1 - NU_ST) / E_ST)
    pf[lab] = dict(p_MPa=round(p, 1), hoop_MPa=round(p * geo, 1), SF_hoop=round(SY_TI / (p * geo), 2),
                   pull_N_mu0p2=round(0.2 * p * math.pi * D_PIN * 3.0, 0), pull_N_mu0p3=round(0.3 * p * math.pi * D_PIN * 3.0, 0))
R["press_fit"] = pf
R["axial_load_on_dowel_N"] = "~0 by design: the contact force is tangential; axial only by friction during axial play (preloaded DB pair: none). Upward the groove floor caps it at 0.15 mm."

# ---------------- groove vs the boss (link 2) ----------------
gr = dict(r_in=RD - W_G / 2, r_out=RD + W_G / 2)
gr["wall_to_bearing_seat_mm"] = round(gr["r_in"] - BRG_BORE_R, 3); gr["wall_to_rim_mm"] = round(HUB_R - gr["r_out"], 3)
for e in (0.85, 1.35, 1.85):
    depth = e + 0.15
    gr[f"e{e}"] = dict(depth=depth, z_bottom=round(U0 + depth, 2), overlap_bearing1_seat_mm=round(max(0.0, U0 + depth - L1), 2),
                       boss_section_removed=round(W_G * depth / ((HUB_R - BRG_BORE_R) * (H1 - U0) + 0.6 * 0.5), 3))
R["groove_vs_boss"] = gr

# ---------------- angular window and tolerance stack ----------------
def nearest(lab):
    rows = G[lab]; taken_lo = [r for r in rows if r["kin"] and r["q3p"] < 0]; stop_lo = [r for r in rows if r["why"] == "j3stop" and r["q3p"] < 0]
    taken_hi = [r for r in rows if r["kin"] and r["q3p"] > 0]; stop_hi = [r for r in rows if r["why"] == "j3stop" and r["q3p"] > 0]
    o = {}
    if taken_lo: t = min(taken_lo, key=lambda r: r["q3p"]); o["lo_kin_ok_deepest"] = (t["i"], t["pose"], t["q3p"])
    if stop_lo: s = max(stop_lo, key=lambda r: r["q3p"]); o["lo_stopped_nearest"] = (s["i"], s["pose"], s["q3p"])
    if taken_hi: t = max(taken_hi, key=lambda r: r["q3p"]); o["hi_kin_ok_deepest"] = (t["i"], t["pose"], t["q3p"])
    if stop_hi: s = min(stop_hi, key=lambda r: r["q3p"]); o["hi_stopped_nearest"] = (s["i"], s["pose"], s["q3p"])
    return o
R["window"] = {lab: nearest(lab) for lab in ("bench110", "held", "fit_bench")}
sw = np.array(G["E_L2_clear_vs_q3p"], float); lo = sw[sw[:, 0] < 0]
def q_at(cl): i = np.nonzero(lo[:, 1] >= cl)[0]; return float(lo[i[0], 0]) if len(i) else None
R["E_L2"] = dict(clear_at_J3MIN=float(np.interp(J3MIN, lo[:, 0], lo[:, 1])), q3p_at_ADJ_0p15=q_at(0.15), q3p_at_touch=q_at(0.0),
                 clear_at_J3MAX=float(np.interp(J3MAX, sw[sw[:, 0] > 0][:, 0], sw[sw[:, 0] > 0][:, 1])))
# contributors (deg at r 7.5): (name, +-random, bias range)
tol_um = 10.0
contrib = [("dowel hole true position in the pad, tangential, +-%g um" % tol_um, tol_um * deg_per_mm / 1000, 0.0, 0.0),
           ("groove end (end-arc centre) position in the boss, tangential, +-%g um" % tol_um, tol_um * deg_per_mm / 1000, 0.0, 0.0),
           ("groove width 2.10 +0.02/0 -> end radius 1.05..1.06 (stop later)", 0.0, 0.0, 0.010 * deg_per_mm),
           ("dowel m6 2.002..2.008 -> radius +1..+4 um (stop earlier)", 0.0, -0.004 * deg_per_mm, -0.001 * deg_per_mm),
           ("pin a bore position +-0.02 at lE 97 (member 3's angular datum)", math.degrees(0.02 / P["lE"]), 0.0, 0.0),
           ("link 2 J2 / J3 bore angular relation, +-0.02 over ~60 mm", math.degrees(0.02 / 60.0), 0.0, 0.0),
           ("J3 DB pair radial play (preloaded: 0) / unloaded deflection", 0.0, 0.0, 0.0)]
rss = math.sqrt(sum(x[1] ** 2 for x in contrib)); wc = sum(x[1] for x in contrib)
bias_lo = sum(x[2] for x in contrib); bias_hi = sum(x[3] for x in contrib)
R["tolerance_stack_deg"] = dict(contributors=[(n, round(r_, 3), round(b0, 3), round(b1, 3)) for n, r_, b0, b1 in contrib], rss=round(rss, 3),
                                worst_linear=round(wc, 3), bias=[round(bias_lo, 3), round(bias_hi, 3)],
                                worst_in=round(wc - bias_lo, 3), worst_out=round(wc + bias_hi, 3))
for tl in (5.0, 20.0, 50.0):                                    # what a looser drawing tolerance does
    w_ = 2 * tl * deg_per_mm / 1000 + math.degrees(0.02 / P["lE"]) + math.degrees(0.02 / 60.0)
    R["tolerance_stack_deg"][f"worst_linear_at_pm{tl:g}um"] = round(w_ + 0.076, 3)

# ---------------- CAD numbers: dowel and groove angles in link 2's hub-3 frame ----------------
ca = G["cad_angles_l2frame_deg"]; L2r = ca["L2_root"][0]; Er0 = ca["E_root_at_q3p0"][0]; sg = ca["q3p_sense"]
mid = (J3MIN + J3MAX) / 2
th_d = (L2r - 180.0 - sg * mid + 180) % 360 - 180          # web centred under link 2's bar root
off_end = math.degrees(0.05 / RD)                            # end-arc centre beyond the dowel-centre stop angle (R 1.05 vs r 1.0)
half_w = math.degrees(W_G / 2 / RD)
g_lo = (th_d + sg * J3MIN) % 360; g_hi = (th_d + sg * J3MAX) % 360
R["cad"] = dict(frame=ca["frame"], L2_root_deg=round(L2r, 2), E_root_at_q3p0_deg=round(Er0, 2), q3p_sense=sg,
                dowel_theta_in_member3_rel_E_root_deg=round(((th_d - Er0) + 180) % 360 - 180, 2),
                dowel_theta_l2frame_at_q3p0_deg=round(th_d, 2),
                dowel_centre_at_J3MIN_l2frame_deg=round(g_lo, 2), dowel_centre_at_J3MAX_l2frame_deg=round(g_hi, 2),
                end_arc_centre_lo_deg=round((g_lo - sg * off_end) % 360, 3), end_arc_centre_hi_deg=round((g_hi + sg * off_end) % 360, 3),
                end_arc_offset_deg=round(off_end, 3), groove_half_width_deg=round(half_w, 2),
                groove_total_arc_deg=round(J3MAX - J3MIN + 2 * off_end + 2 * half_w, 2), web_deg=round(360 - (J3MAX - J3MIN + 2 * off_end + 2 * half_w), 2),
                E_vs_L2_root_at_J3MIN_deg=round(((Er0 + sg * J3MIN) - L2r + 180) % 360 - 180, 2))
json.dump(R, open(os.path.join(HERE, "results.json"), "w"), indent=1, default=float)
print(json.dumps(R, indent=1, default=float))
