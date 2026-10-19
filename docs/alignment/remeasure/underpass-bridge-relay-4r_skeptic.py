"""Skeptic (2026-10-18) of the underpass-bridge-relay-4r re-audit: independent re-derivation from the verifier's raw
corrected-bridge dumps (verifier_fix*_A_up1.2_perpose.json) + its X1 jam rows. No model run. Recomputes the verified 20.60 / 24.33,
near-touch 1 / 2 mm, metal < 2 mm counts, contact depth vs the lead, the 6 / 16 contact-jam poses read as lost, and the loaded
(0.336 mm) strap-top rescore.  python3 docs/alignment/remeasure/underpass-bridge-relay-4r_skeptic.py"""
import json, os, sys
REPO = "/home/user/exo-shoulder"; sys.path.insert(0, REPO + "/tools")
import alignment_paired as AP
V = REPO + "/docs/concepts/verify/underpass-bridge-relay-4r/"; REM = REPO + "/docs/alignment/remeasure/"
out = {}
def mm(p): return min(p["min_mm"], p["cmin"]) if p.get("cmin") is not None else p["min_mm"]
def lose(P, S):
    Q = []
    for p in P:
        q = dict(p)
        if q["i"] in S and q["taken"]: q["taken"] = False; q["ev"] = False; q.pop("ns", None); q.pop("nib", None)
        Q.append(q)
    return Q
def lose_contact(P, S):   # contact poses read as lost instead of contact
    Q = []
    for p in P:
        q = dict(p)
        if q["i"] in S and q["contact"]: q["contact"] = False; q["taken"] = False; q["ev"] = False; q.pop("ns", None); q.pop("nib", None)
        Q.append(q)
    return Q
def near(P, t):
    Q = []
    for p in P:
        q = dict(p)
        if q["taken"] and mm(q) < t: q["taken"] = False; q["contact"] = True
        Q.append(q)
    return AP.gap_parts(Q)["gap"]
def st(P):
    tk = [p for p in P if p["taken"]]; con = [p for p in P if p["contact"]]
    ws = [p for p in P if p["kind"] == "ws"]
    return dict(gap=AP.gap_parts(P), near1=near(P, 1.0), near2=near(P, 2.0), taken=len(tk), lt1=sum(mm(p) < 1 for p in tk), lt2=sum(mm(p) < 2 for p in tk),
                frac_lt2=round(sum(mm(p) < 2 for p in tk) / len(tk), 4), ncon=len(con), depth=round(-sum(p["min_mm"] for p in con), 2),
                deepest=round(-min(p["min_mm"] for p in con), 2) if con else 0, deeper3=sum(p["min_mm"] < -3 for p in con),
                oh=[sum(p["taken"] for p in ws if p["elev"] >= 140), sum(1 for p in ws if p["elev"] >= 140)])
for wear, dump, xf in (("bench", "verifier_fix_A_up1.2_perpose.json", "verifier_fix.json"), ("held", "verifier_fixheld_A_up1.2_perpose.json", "verifier_fixheld.json")):
    raw = json.load(open(V + dump))["poses"]; x = json.load(open(V + xf))["A_up1.2"]["xcheck"]
    rows = x["extra_jam_rows"]; idx = {p["i"]: p for p in raw}
    lost = sorted(r["i"] for r in rows if idx[r["i"]]["taken"] and not idx[r["i"]]["contact"])
    jamcon = sorted(r["i"] for r in rows if idx[r["i"]]["contact"])
    P = lose(raw, set(lost))
    o = dict(raw_model_rule=AP.gap_parts(raw)["gap"], lost=lost, jam_contacts=jamcon, verifier_rescored=x["rescored"]["gate_gap"], x1=st(P),
             jam_contacts_as_lost=AP.gap_parts(lose_contact(P, set(jamcon)))["gap"])
    if wear == "bench":
        low = x["clearance_margin_taken"]["lowest"]; d = 0.336
        new = sorted(r["i"] for r in low if r["mm"] - d < 1.0 and idx[r["i"]]["taken"] and not idx[r["i"]]["contact"])
        o["loaded_new_lost"] = new; o["loaded_gap"] = AP.gap_parts(lose(raw, set(lost) | set(new)))["gap"]
        o["E_under_min"] = x["E_under_shell_taken"]["min"][0]; o["clr_lowest"] = low[0]
    out[wear] = o
for wear in ("bench", "held"):
    L = json.load(open(REM + f"conecut-knee-knuckle-3r_{wear}_perpose.json"))["poses"]; out["lead_" + wear] = st(L)
json.dump(out, open(REM + "underpass-bridge-relay-4r_skeptic.json", "w"), indent=1, default=float); print(json.dumps(out, indent=1, default=float))
