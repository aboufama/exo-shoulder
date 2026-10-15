"""Scorecard: every requirement in judge/requirements.json against the judges' outputs for one design.
Runs nothing heavy itself; run the judges first (README "Judge a design"). Writes <design>/judge/scorecard.md + .json.
    python3 judge/scorecard.py <design dir|id>"""
import json, os, sys
from common import design_dir, REPO
dd = design_dir(sys.argv[1]); J = os.path.join(dd, "judge"); REQ = json.load(open(os.path.join(REPO, "judge", "requirements.json")))
def load(p):
    try: return json.load(open(p))
    except Exception: return None
src = dict(score=load(os.path.join(dd, "score.json")), score14=load(os.path.join(dd, "score_14mm.json")), body_contact=load(os.path.join(J, "body_contact.json")), part_contact=load(os.path.join(J, "part_contact.json")),
           part_validity=load(os.path.join(J, "part_validity.json")), base_mount=load(os.path.join(J, "base_mount.json")), workspace=load(os.path.join(J, "workspace.json")), dynamics=load(os.path.join(J, "dynamics.json")), design=load(os.path.join(dd, "design.json")), parts=load(os.path.join(dd, "parts_full.json")))
ISO_TS_15066 = dict(upper_arm_force_N=150.0, deltoid_N_cm2=190.0, humerus_N_cm2=220.0, forearm_force_N=160.0, forearm_muscle_N_cm2=180.0)  # Annex A, Table A.2
CAPILLARY_KPA = 4.3          # 32 mmHg capillary closing pressure (Landis 1930): the conservative all-day tissue-perfusion bound (aim, not the threshold)
EDGE_FACTOR = 2.0            # local edge peak / mean pressure under a rigid shell (dynamics.py's stated rule)
def interface_pressure(dyn):
    """R11 (simulation part), from judge/dynamics.json: worst mean pressure the exo adds on the upper-arm cuff over the
    MVP1 cases (rolling bearings, every mu_eff x speed the judge ran), including the arm-side parts' weight hanging on
    the cuff; against the sustained budget (14 kPa all-day minus the strap preload) and ISO/TS 15066 Annex A quasi-static
    limits for the upper arm (force 150 N; pressure 190 N/cm2 deltoid, the lower of deltoid / humerus, on the 2x edge peak)"""
    if not dyn or "cases" not in dyn: return None
    cp = dyn["model"]["cuff_pressure"]; ro = dyn["load_friction"]["rolling"]; A = cp["area_cm2"]; Wt = cp["arm_parts_weight_N"]
    def key_mu(k):
        p = k.split("|"); return (float(p[1][2:]), float(p[2][1:])) if len(p) >= 5 and p[1].startswith("mu") and p[2].startswith("t") else (None, None)
    judged = {k: c for k, c in dyn["cases"].items() if key_mu(k)[0] in ro["mu_eff"] and abs(key_mu(k)[1] - ro["tau0_Nm"]) < 1e-9}
    plain = {k: c for k, c in dyn["cases"].items() if key_mu(k)[0] is not None and k not in judged}
    if not judged: return None
    kpa = lambda c: (c["force_peak_N"] + Wt) / A * 10.0
    per = {k: round(kpa(c), 3) for k, c in judged.items()}; wk = max(per, key=per.get); F = judged[wk]["force_peak_N"] + Wt
    budget = cp["sustained_budget_kPa"] - cp["strap_preload_kPa"]; local = EDGE_FACTOR * per[wk]
    iso_ok = bool(F <= ISO_TS_15066["upper_arm_force_N"] and local <= 10.0 * ISO_TS_15066["deltoid_N_cm2"])
    return dict(exo_kPa_worst=per[wk], worst_case=wk, per_case_kPa=per, total_with_strap_kPa_worst=round(per[wk] + cp["strap_preload_kPa"], 3),
                budget_exo_kPa=budget, sustained_budget_kPa=cp["sustained_budget_kPa"], strap_preload_kPa=cp["strap_preload_kPa"], area_cm2=A, arm_parts_weight_N=Wt,
                iso_ok=iso_ok, iso=dict(force_N_worst=round(F, 2), force_limit_N=ISO_TS_15066["upper_arm_force_N"], local_peak_kPa_est=round(local, 3),
                                        pressure_limit_kPa=10.0 * ISO_TS_15066["deltoid_N_cm2"], basis="ISO/TS 15066:2016 Annex A Table A.2, upper arm and elbow: 150 N; deltoid 190 / humerus 220 N/cm2"),
                aim_capillary_kPa=CAPILLARY_KPA, exo_under_capillary=bool(per[wk] <= CAPILLARY_KPA),
                plain_bearing_worst_kPa=(round(max(kpa(c) for c in plain.values()), 2) if plain else None),
                note="mean pressure on the cuff's skin side (dynamics.py rule); the forearm cuff shares the load (upper-cuff values are upper bounds); base-side (scapula handler) pressure is not simulated; the prototype pressure-film / FSR check remains part of R11")

def metric(m):
    s, k = m.split(".", 1); d = src.get(s if s != "mass" else "parts")
    if d is None: return None
    if s in ("score", "score14") and k.startswith("clip:"): return next((c["score"] for c in d["clips"] if c["name"] == k[5:]), None)
    if s == "mass": return round(sum(p["mass_g"] or 0 for p in d["parts"] if p.get("material") != "user part"), 1)
    for part in k.split("."):                                                       # nested keys (dynamics.verdict.x)
        d = d.get(part) if isinstance(d, dict) else None
    return d
OPS = {">=": lambda a, b: a >= b, "<=": lambda a, b: a <= b, "==": lambda a, b: a == b}
src["interface_pressure"] = interface_pressure(src["dynamics"])                    # derived from dynamics.json (R11)
src["fea"] = load(os.path.join(J, "fea.json"))                                      # R9 (judge/fea.py)
rows = []
for rid, r in REQ.items():
    if rid.startswith("_"): continue
    if "metric" in r:
        v = metric(r["metric"]); st = "NOT RUN" if v is None else ("PASS" if OPS[r["op"]](v, r["value"]) else "FAIL")
        for c in r.get("and", []):                                                  # extra conditions: all must hold
            cv = metric(c["metric"])
            if cv is None: st = "NOT RUN"
            elif st == "PASS" and not OPS[c["op"]](cv, c["value"]): st = "FAIL"
        tgt = f"{r['op']} {r['value']}{(' ' + r['unit']) if 'unit' in r else ''}" + "".join(f" and {c.get('label', c['metric'])} {c['op']} {c['value']}" for c in r.get("and", []))
        row = dict(id=rid, name=r["name"], value=v, unit=r.get("unit"), target=tgt, status=st, judge=r["judge"])
        if r.get("details"): row["details"] = src.get(r["details"])
        rows.append(row)
    else: rows.append(dict(id=rid, name=r["name"], value=None, target="", status=r["status"], judge=r["judge"]))
fmt = lambda v, u=None: "-" if v is None else (f"{v} {u}" if u else (f"{100 * v:.1f}%" if isinstance(v, float) and 0 <= v <= 1.0 and not isinstance(v, bool) else str(v)))
md = [f"# Scorecard: {os.path.basename(os.path.normpath(dd))}", "", "| | requirement | value | target | status | judge |", "|---|---|---|---|---|---|"]
md += [f"| {r['id']} | {r['name']} | {fmt(r['value'], r.get('unit'))} | {r['target']} | **{r['status']}** | {r['judge']} |" for r in rows]
n_pass = sum(r["status"] == "PASS" for r in rows); md += ["", f"{n_pass} of {len(rows)} requirements pass."]
notes = []                                                                          # what is behind the numbers that need it
bc = src["body_contact"]
if bc and "attributable" in bc:
    at = bc["attributable"]
    notes.append(f"- R2 ({bc.get('body_model', 'rig')} body): this project's parts {bc['max_depth_ours']} mm, the user's own arm parts {bc['max_depth_user']} mm; "
                 f"beyond the rig's own self-intersection (judge/body_regions.py): ours {at['max_depth_ours']} mm ({at['worst_part_ours']}), the user's {at['max_depth_user']} mm ({at['worst_part_user']})")
bm = src["base_mount"]
if bm and bm.get("law"):
    notes.append(f"- R10 (girdle mount, skin slip, {bm['law']} law): low {bm['per_law_max_mm']['low']} / high {bm['per_law_max_mm']['high']} mm; worst frame by elevation {bm['central_max_by_elevation_mm']} mm; "
                 f"{100 * bm['share_over_4mm']:.0f} % of frames over 4 mm; design-independent for a spherical chain (docs/research/base_slip_model.md)")
ip = src["interface_pressure"]
if ip:
    notes.append(f"- R11 (simulation part): worst {ip['exo_kPa_worst']} kPa from the exo ({ip['worst_case']}, incl. {ip['arm_parts_weight_N']} N of arm parts on {ip['area_cm2']} cm2), "
                 f"{ip['total_with_strap_kPa_worst']} kPa with the strap vs {ip['sustained_budget_kPa']} kPa all-day; ISO/TS 15066 {ip['iso']['force_N_worst']} / {ip['iso']['force_limit_N']} N, "
                 f"edge peak ~{ip['iso']['local_peak_kPa_est']} / {ip['iso']['pressure_limit_kPa']} kPa; aim {ip['aim_capillary_kPa']} kPa (capillary) {'met' if ip['exo_under_capillary'] else 'not met'}; "
                 f"a plain-bearing build would reach {ip['plain_bearing_worst_kPa']} kPa; the prototype pressure-film check remains")
fe = src["fea"]
if fe and fe.get("summary"):
    sm = fe["summary"]; wp = fe["parts"][sm["worst_part"]]; c = wp["cases"]["D1F"]
    notes.append(f"- R9 (CalculiX FEA, 10 N.m + 50 N cuff wrench): min SF {sm['min_SF']} on {sm['worst_part']} ({c['vm_MPa']} MPa at {c['at_mm']}, {wp['material']}); "
                 f"pure 10 N.m worst direction SF {sm['min_SF_D1']}; MVP1 (R17 envelope) SF {sm['min_SF_MVP1']}; fatigue SF {sm['fatigue_min_SF']}; "
                 f"chain GH-point deflection {sm['chain_d_GH_mm']} mm vs 2 mm floor / {sm['min_skin_gap_mm']} mm min skin gap; parts " + ", ".join(f"{k} SF {v['cases']['D1F']['SF']}" for k, v in fe["parts"].items()))
    rt = fe.get("red_team")
    if rt:
        hw = rt["joint_hardware"]
        notes.append(f"- R9 red team: fall on the elbow (2x) SF vs fracture {rt['fall_on_elbow_2x']['min_SF_ult']}; smallest section SF {rt.get('smallest_section', {}).get('min_SF', '-')}; "
                     f"overhead covered by the worst-direction envelope; joint hardware min SF {rt['hardware_min_SF']} ({'ok' if rt['hardware_ok'] else 'FAIL'}: "
                     + ", ".join(f"{k} {j['tilt_Nm']} N.m tilt" + (f" -> {j['bearing_load_N']:.0f} N per bearing vs C0 {j['C0_N']:.0f} N" if j['ver'] == 'v5' else f" -> washer {j['washer_edge_pressure_MPa']} MPa") for k, j in hw.items())
                     + f"); MVP1 (unpowered, R17 envelope) {'passes' if sm.get('mvp1_passes') else 'fails'}")
if notes: md += ["", "Notes:", ""] + notes
open(os.path.join(J if os.path.isdir(J) else dd, "scorecard.md"), "w").write("\n".join(md) + "\n"); json.dump(rows, open(os.path.join(J if os.path.isdir(J) else dd, "scorecard.json"), "w"), indent=1)
print("\n".join(md))
