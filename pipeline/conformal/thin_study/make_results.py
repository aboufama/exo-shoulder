"""Collect links_fea.json, bracket_track.json, joint_hw.json, validate.json into results.json and print the tables used
in REPORT.md.

    python3 -B make_results.py
"""
import sys, json, math, os
sys.dont_write_bytecode = True
import numpy as np

SY, SE = 880.0, 500.0
L = json.load(open("links_fea.json"))
BT = json.load(open("bracket_track.json")) if os.path.exists("bracket_track.json") else None
JH = json.load(open("joint_hw.json")) if os.path.exists("joint_hw.json") else None
VA = json.load(open("validate.json")) if os.path.exists("validate.json") else None
BREP_MASS = {("4c_best", 1): 43.7, ("4c_best", 2): 47.4, ("4c_best", 3): 18.7, ("5r_thin", 1): 22.9, ("5r_thin", 2): 33.7,
             ("5r_thin", 3): 29.3, ("5r_thin", 4): 26.4, ("4r_thin", 1): 18.8, ("4r_thin", 2): 48.0, ("4r_thin", 3): 23.3}


def seat_max(z):
    """worst seat-zone value: lower hubs' pin-root ring (>= 0.67 mm off the pin) and upper hubs' washer seat"""
    v = [x for k, x in z.items() if k.endswith("_pinroot") or k.endswith("_seat")]
    return max(v) if v else float("nan")


def row(r):
    z1, z2, zd = r["zones"]["D1"], r["zones"]["D2"], r["zones"]["des"]
    return dict(design=r["design"], member=r["member"], variant=r["variant"], kind=r["kind"], gen_path=r["gen_path"],
                roles="/".join(f"{a}{t:g}" for a, t in zip(r["roles"], r["hub_t"])), thick=r["thick"],
                body_D1=z1["body"], body_D2=z2["body"], body_des=zd["body"], body_des_p995=zd["body_p995"],
                seat_D1=seat_max(z1), seat_des=seat_max(zd), ribbon_D1=z1.get("ribbon"),
                SF_y_D1=SY / z1["body"], SF_y_D2=SY / z2["body"], SF_y_des=SY / zd["body"], SF_fat_D1=SE / z1["body"],
                M_allow_SF15_Nm=25.0 * (SY / 1.5) / z1["body"], M_inf_life_Nm=25.0 * SE / z1["body"],
                k_link_soft=r["k_link_Nm_deg"][0], k_link_stiff=r["k_link_Nm_deg"][1], mass_mesh_g=r["mass_g"],
                mass_brep_g=BREP_MASS.get((r["design"], r["member"])) if r["variant"] == "V0" else None,
                neck_as_built_mm=r.get("neck_as_built_mm"), peak_at=r["zones"]["peak_at"])


rows = [row(r) for r in L]
res = dict(meta=dict(date="2026-10-14", material="Ti-6Al-4V annealed: E 113.8 GPa, nu 0.342, yield 880 MPa, smooth endurance ~500 MPa (R=-1)",
                     loads="D1 25 N.m worst direction perp. to the loaded joint axis; D2 200 N through the shoulder centre (worst direction); "
                           "design = D1 + D2 (vm bound); hub A held through bonded washers (locked joint), hub B loaded through its own joint model",
                     element="hex8 + incompatible modes (fe_core.py), 4 layers through the thickness; validated vs beam theory (validate.json)",
                     geometry="re-derived from band_cad/build_band_cad.py (snapshot in snapshot/), see link_geom.py"),
           validation=VA, links=rows, joint_hardware=JH, neck_track=BT)

# ------------------------------------------------------------------ as-built table
print("AS BUILT (V0)")
print(f"{'part':18s} {'kind':6s} {'hubs':14s} {'D1 body':>8s} {'SF_y':>5s} {'D2':>5s} {'D1+D2':>6s} {'SF':>5s} {'seat D1':>7s} {'k soft':>6s} {'M@1.5':>6s} {'g':>5s}")
for r in rows:
    if r["variant"] != "V0": continue
    nm = f"{r['design']} {'base' if r['member'] == 0 else 'link ' + str(r['member'])}"
    print(f"{nm:18s} {r['kind']:6s} {r['roles']:14s} {r['body_D1']:8.0f} {r['SF_y_D1']:5.2f} {r['body_D2']:5.0f} {r['body_des']:6.0f} {r['SF_y_des']:5.2f}"
          f" {r['seat_D1']:7.0f} {r['k_link_soft']:6.2f} {r['M_allow_SF15_Nm']:6.1f} {(r['mass_brep_g'] or r['mass_mesh_g']):5.1f}")

# ------------------------------------------------------------------ trade curves (uniform t)
print("\nTRADE CURVES (U-series: ribbon = lower plate = t, upper hub = t + 0.05)")
curves = {}
for r in rows:
    if not r["variant"].startswith("U") and not r["variant"].startswith("W9"): continue
    key = (r["design"], r["member"], "W9" if r["variant"].startswith("W9") else "U")
    curves.setdefault(key, []).append(r)
fits = {}
for key, rs in sorted(curves.items()):
    rs = sorted(rs, key=lambda r: r["thick"]["t_link"])
    print(f"{key[0]} {'base' if key[1] == 0 else 'link ' + str(key[1])} {key[2]}")
    for r in rs:
        print(f"   t {r['thick']['t_link']:.1f}: D1 body {r['body_D1']:5.0f} (SF {r['SF_y_D1']:.2f}, M_allow@1.5 {r['M_allow_SF15_Nm']:.1f} N.m, inf-life {r['M_inf_life_Nm']:.1f})"
              f"  D1+D2 {r['body_des']:5.0f} (SF {r['SF_y_des']:.2f})  seat D1 {r['seat_D1']:4.0f} des {r['seat_des']:4.0f}  k {r['k_link_soft']:5.2f}/{r['k_link_stiff']:5.2f}  {r['mass_mesh_g']:5.1f} g")
    if key[2] == "U" and len(rs) >= 3:
        t = np.array([r["thick"]["t_link"] for r in rs]); out = {}
        for nm in ("body_D1", "body_des", "seat_D1", "seat_des", "k_link_soft", "mass_mesh_g"):
            y = np.array([r[nm] for r in rs]); p = np.polyfit(np.log(t), np.log(y), 1); out[nm] = dict(exp=float(p[0]), coef=float(math.exp(p[1])))
        def t_for(nm, target):
            f = out[nm]; return (target / f["coef"]) ** (1 / f["exp"])
        mins = dict(t_body_SF15_D1=t_for("body_D1", SY / 1.5), t_body_SF12_des=t_for("body_des", SY / 1.2),
                    t_body_inf_life_D1=t_for("body_D1", SE), t_seat_SF15_D1=t_for("seat_D1", SY / 1.5), t_seat_SF12_des=t_for("seat_des", SY / 1.2))
        fits[f"{key[0]} m{key[1]}"] = dict(fit=out, min_t=mins)
        print("   power fits: " + ", ".join(f"{k} ~ t^{v['exp']:.2f}" for k, v in out.items()))
        print("   min t: " + ", ".join(f"{k} {v:.2f}" for k, v in mins.items()))
res["trade_fits"] = fits

if BT:
    print("\nNECK (straight bar, clamp at the lap edge, load at the hub)")
    for r in BT["neck"]:
        print(f"   w {r['w']:.0f} L {r['L']:.0f} t {r['t']}: D1 {r['D1']:.0f} D2 {r['D2']:.0f} des {r['des']:.0f} (SF {SY / r['des']:.2f}; clamp edge {r['des_clamp_edge']:.0f})"
              f"  k {r['k_soft']:.1f} N.m/deg  defl {r['defl_200N']:.2f} mm  {r['mass_g_per_span']:.1f} g")
    print("TRACK (ring segment, cantilever arc S, keel depth D)")
    for r in BT["track"]:
        print(f"   S {r['S_arc']:.0f} D {r['D']:.0f}: D1 {r['D1']:.0f} D2 {r['D2']:.0f} des {r['des']:.0f}  SF Ti {SY / r['des']:.2f} 17-4 {1170 / r['des']:.2f} 7075 {503 / r['des']:.2f}"
              f"  k(Ti) {r['k_soft']:.1f}  defl {r['defl_200N']:.2f}  mass Ti {r['mass_g']['Ti-6Al-4V']:.0f} g")

# ------------------------------------------------------------------ recommendations + hardware options (from the tables above,
# joint_hw.json and the catalogue research; see REPORT.md)
res["recommendations"] = dict(
    basis="SF >= 1.5 on yield under D1 (25 N.m) alone and SF ~1.0-1.2 under the D1 + D2 bound; 14 mm strip unless noted",
    link_body_ribbon_stubs_waists_mm=dict(t=5.5, range_from_fits="4.8-5.9 (D1 SF 1.5: 4.8-5.3; D1+D2 SF 1.2: 5.1-6.0)", strip18_t=4.5,
                                          note="thicker than built (4.0 ribbon / 3.5 lower-hub stub); keep it outside r = 14 mm so it does not add to the joint stack"),
    lower_plate_under_washer_seat_mm=dict(t=3.0, sf_D1=round(SY / 420, 2), sf_des=round(SY / 622, 2), note="2.5 gives SF 1.75 / 1.18; base needs 4.0"),
    upper_hub_mm=dict(t=4.05, sleeve="igus GSM-1012-04", seat_D1_MPa=555, sf_D1=round(SY / 555, 2), note="3.05 (GSM-1012-03) only for joint moments <= ~14 N.m"),
    scapula_base_mm=dict(seat_t=4.0, waist_t=5.0),
    washers="2x igus GTM-1018-005 (0.5 mm)",
    cap="dome cap 2.5 (2.0 if an M4 ULP with a <= 1.5 mm head is confirmed); use 10.9 / 12.9 steel ULP, not A2-50",
    neck_bracket_mm=dict(w=30, t=4.5, note="SF 1.6-1.7 on D1+D2 for 50-90 mm span; 5.5 for >= 10 N.m/deg hub tilt at 90 mm"),
    track_keel_mm=dict(D=10, material="Ti-6Al-4V or 17-4PH H900 (17-4: D 7 gives SF 1.4)", note="4 mm V-head alone SF 0.45; 7075 needs D >= 19"),
    stack_height_mm=dict(current=13.07, recommended=round(3.0 + 0.5 + 4.05 + 0.5 + 0.02 + 2.5, 2), recommended_cap2=round(3.0 + 0.5 + 4.05 + 0.5 + 0.02 + 2.0, 2),
                         low_load_le14Nm=round(2.5 + 0.5 + 3.05 + 0.5 + 0.02 + 2.0, 2)))
res["hardware_options"] = [
    dict(option="0.5 mm thrust washers x2", part="igus GTM-1018-005 (10/18/0.5, iglidur G)", saves_mm=1.0, saves_g_per_joint=0.26,
         rating="80 MPa static; edge p at 25 N.m = 48 MPa", risk="half the wear allowance", verified=True),
    dict(option="4 mm sleeve, upper hub 4.05", part="igus GSM-1012-04", saves_mm=1.0, saves_g_per_joint=1.9, rating="200 N -> 5 MPa", risk="upper-hub seat stress 555 MPa at 25 N.m", verified=True),
    dict(option="3 mm sleeve, upper hub 3.05", part="igus GSM-1012-03", saves_mm=2.0, saves_g_per_joint=3.8, rating="200 N -> 6.7 MPa", risk="seat 1000 MPa at 25 N.m: only <= 14 N.m", verified=True),
    dict(option="lower plate 3.5 -> 3.0 under the seat", part="(machining)", saves_mm=0.5, saves_g_per_joint=1.0, rating="pin-root ring 420 MPa D1", risk="stub must be decoupled (thicker)", verified=None),
    dict(option="cap 2.5 -> 2.0", part="M4 ULP head 1.5 (Fastenright MPH07 class; head height label not explicit)", saves_mm=0.5, saves_g_per_joint=0.43,
         rating="cap 271 MPa / 518 at clamp edge at 25 N.m", risk="ULP head strength not rated; washer-B pull 2.2 kN", verified=False),
    dict(option="DIN 471-10 ring instead of cap", part="Rotor Clip DSH-10 (1.0 thick, groove 9.6 x 1.1; ring 4.0 kN, groove 1.0-2.4 kN in 200 MPa steel)", saves_mm=0.8,
         saves_g_per_joint=2.0, rating="one-sided 2.2 kN at 25 N.m", risk="0.10-0.16 mm axial lash (tilt play ~0.3-0.5 deg), eccentric load on ring", verified=True),
    dict(option="bonded PTFE-fabric liner instead of washers", part="Kaman KAron B/V (0.25-0.38 mm, 207-551 MPa)", saves_mm=0.25, saves_g_per_joint=0.2,
         rating="high", risk="custom lined parts, needs hard counterface (DLC over hardened Ti), not catalogue", verified=False),
    dict(option="Ø8 pin", part="GTM-0815-005 + GSM-0810-05 (shortest 5 mm)", saves_mm=0.0, saves_g_per_joint=1.0,
         rating="edge p 82 MPa > 80; pin-root peak 851 MPa", risk="no stack gain, overstressed at 25 N.m", verified=True),
    dict(option="needle thrust AXK1024 + 2x AS1024", part="INA/NTN", saves_mm=-6.0, saves_g_per_joint=-5.0, rating="26 kN static", risk="taller", verified=True),
]
json.dump(res, open("results.json", "w"), indent=1)
print("\nwrote results.json")
