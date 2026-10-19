"""Rebase of the verified leaders to the user's 2026-10-16 rulings (fold margin 5 deg, O20 hubs only): MERGES each leader's
re-measurement (its own verifier harness, Bench(110,360) exact, shape frozen from the Bench(60,160) fast fit made at the
same margin) into docs/concepts/rows/<id>.json. A MEASUREMENT change, not a design change: the old v_* (margin 10) move to
v_*_m10, v_* become the margin-5 / O20 numbers, every other key (mechanism, polish, notes) is kept.

    python3 docs/research/rebase/merge_rows.py [ids...]        (reads docs/research/rebase/<run>.json)
"""
import datetime, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
K = ("gap", "reach", "follow", "inband14", "inband10", "contact")
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
NOTE = "margin 5 (user 2026-10-16), measurement change"


def run(name):
    d = json.load(open(os.path.join(HERE, name + ".json")))
    if "run" in d:                                            # spine-parked verifier
        r = d["run"]; o = {k: r.get(k) for k in K}; o["near1"] = r.get("gap_near1"); o["min_margin_taken"] = r.get("min_margin")
        o["fit_gap"] = d.get("fit", {}).get("gap"); o["overhead"] = r.get("overhead"); o["fold_margin"] = d.get("fold_margin")
    elif "audit" in d and "corrected" in d.get("audit", {}):  # osn verifier
        c = d["audit"]["corrected"]; o = {k: c.get(k) for k in K}; o["near1"] = d["audit"].get("gap_near1"); o["fit_gap"] = (d.get("fit") or {}).get("gap")
    else:                                                     # pin knee / raglan / knuckle verifiers
        c = d["corrected"]; o = {k: c.get(k) for k in K}; a = d.get("corrected_audit") or d.get("corrected_redteam") or {}
        o["near1"] = a.get("gap_near1"); o["near_min_mm"] = a.get("near_touch_min_mm", a.get("near_min"))
        o["fit_gap"] = (d.get("fit_fast") or {}).get("gap")
        if "gap_fixed_n" in c: o["gap_fixed_n"] = c["gap_fixed_n"]
        ov = a.get("overhead140") or (a.get("groups") or {}).get("overhead140")
        if ov: o["overhead140"] = ov
    o["file"] = f"docs/research/rebase/{name}.json"; o["score"] = round(100 - o["gap"] / 2.75, 2)
    return o


# id -> (harness, config label, margin-10 run, margin-5 run, extra runs, remark)
PLAN = {
    "skin-normal-3r-pin-knee": ("docs/concepts/verify/skin-normal-3r-pin-knee.py", "H1 = H-g107-1 (polish winner, O20 x3)", "pkH1_m10", "pkH1_m5",
                                {"k4598_m10": "pk_m10", "k4598_m5": "pk_m5"},
                                "H1 replaced k4598 at 06:29 UTC (polish verifier); k4598 re-measured too"),
    "raglan-knee-3r": ("docs/concepts/verify/raglan-knee-3r.py big", "k1284 (cma-A2)", "rg_m10", "rg_m5", {},
                       "the model routes its links again (PK._Geo fix in the rebase track): 31.52 reproduces exactly at margin 10"),
    "skin-normal-3r-knuckle-cufflink": ("docs/concepts/verify/skin-normal-3r-knuckle-cufflink.py", "k1187", "kn_m10", "kn_m5", {}, ""),
    "offset-skin-normal-3r": ("docs/concepts/verify/offset-skin-normal-3r.py osnbig_frozen", "k4216 (cma2-F)", "osn_m10", "osn_m5", {}, ""),
    "spine-parked-j2-3r": ("docs/concepts/verify/spine-parked-j2-3r.py frozen", "k7008 seats, hubs O20 x3 (the verified 34.29 used O15 J2 / J3)", "sp20_m10", "sp20_m5",
                           {"o15_m10_as_verified": "sp15_m10"},
                           "the O15 claim 34.29 reproduces exactly (CB_ALLOW_SLIM=1) but does not stand under 'Keep O20 only'"),
}


def merge(rid):
    harness, cfg, r10, r5, extra, remark = PLAN[rid]
    if not all(os.path.exists(os.path.join(HERE, n + ".json")) for n in [r10, r5] + list(extra.values())):
        print("skip (runs missing)", rid); return
    p = os.path.join(REPO, "docs", "concepts", "rows", rid + ".json"); row = json.load(open(p))
    m10, m5 = run(r10), run(r5)
    if "v_gap_m10" not in row:                                # first rebase: keep the old verified numbers
        for k in K: row[f"v_{k}_m10"] = row.get(f"v_{k}")
        for k in ("v_score", "v_near_touch", "v_overhead140", "v_gap_fixed_n"):
            if k in row: row[k + "_m10"] = row[k]
    for k in K: row[f"v_{k}"] = m5[k]
    row["v_score"] = m5["score"]
    if "gap_fixed_n" in m5: row["v_gap_fixed_n"] = m5["gap_fixed_n"]
    if m5.get("near1") is not None:
        row["v_near_touch"] = dict(row.get("v_near_touch") or {}, gap_metal_lt1_as_contact=m5["near1"], min_mm=m5.get("near_min_mm"), margin=5)
    if m5.get("overhead140"): row["v_overhead140"] = m5["overhead140"]
    row["v_rebase"] = dict(t=NOW, note=NOTE, rule="fold margin 5 deg (tools/concept_kit.py FOLD_MARGIN), O20 hubs only", harness=harness,
                           protocol="fit Bench(60,160) fast AT the margin, shape frozen, worn on Bench(110,360) exact, verifier checks (farm)",
                           config=cfg, m10=m10, m5=m5, extra={k: run(v) for k, v in extra.items()}, remark=remark,
                           delta_gap=round(m5["gap"] - m10["gap"], 2))
    row["note"] = (row.get("note") or "") + (f" || REBASE {NOW[:16]} UTC ({NOTE}): {cfg}, own verifier, Bench(110,360) exact frozen: margin 10 "
                                             f"{m10['gap']} -> margin 5 {m5['gap']} (reach {m10['reach']} -> {m5['reach']}, in-band14 {m10['inband14']} -> "
                                             f"{m5['inband14']}, follow {m10['follow']} -> {m5['follow']}); v_* = margin 5, v_*_m10 = before. {remark}")
    json.dump(row, open(p, "w"), indent=1)
    print(rid, "m10", m10["gap"], "-> m5", m5["gap"])


if __name__ == "__main__":
    for rid in (sys.argv[1:] or PLAN): merge(rid)
