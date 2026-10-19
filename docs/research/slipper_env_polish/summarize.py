"""summary tables of the slipper-nose-knuckle-3r final polish claims (claim_<cfg>_<fit>_<wear>_<p|u>.json + per-pose dumps,
written by tools/slipper_env_polish.py claim): the claim table, the gain over the verified config (BEST) on the same
protocol AND the same reading, contact depth by class (low-arm extreme rotation elev < 60 with |axial| >= 120;
overhead elev >= 140; across-body; |axial| >= 150).
    python3 docs/research/slipper_env_polish/summarize.py [dir ...]   (default: farm/ and local/ next to this file)"""
import json, os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
DIRS = sys.argv[1:] or [os.path.join(HERE, "farm"), os.path.join(HERE, "local")]
C = {}
for F in DIRS:
    for f in sorted(glob.glob(os.path.join(F, "claim_*.json"))):
        if f.endswith("_perpose.json"): continue
        try: d = json.load(open(f))
        except Exception: continue
        nm = os.path.basename(f)[6:-5]
        if nm in C: continue                                   # farm first, local only fills gaps
        d["_pp"] = f.replace(".json", "_perpose.json"); C[nm] = d


def cls(p):
    el, pl, ax = p["elev"], p["plane"], p["axial"]
    out = []
    if el < 60 and abs(ax) >= 120: out.append("lowarm_xrot")
    if el >= 140: out.append("overhead")
    if pl >= 100 and el >= 40: out.append("across")
    if abs(ax) >= 150: out.append("ax150")
    return out


rows = {}
for nm, d in C.items():
    fr = d["frozen"]; au = d["audit"]; ex = d["extra"]; dep = ex.get("depth") or {}; th = ex.get("th_margin_own_state") or {}
    cn = (d.get("connected") or {}).get("connected_full") or {}
    byc = {}
    if os.path.exists(d["_pp"]):
        for r in json.load(open(d["_pp"]))["poses"]:
            if r["kind"] != "ws": continue
            for c in cls(r):
                b = byc.setdefault(c, dict(n=0, taken=0, contact=0, depth=0.0))
                b["n"] += 1; b["taken"] += int(r["taken"]); b["contact"] += int(r["contact"]); b["depth"] += (-r["min_mm"] if r["contact"] else 0.0)
    rows[nm] = dict(nm=nm, gap=fr["gap"], conn=cn.get("gap"), dropped=cn.get("dropped"), n1=au.get("gap_near1"), n2=au.get("gap_near2"),
                    reach=fr["reach"], follow=fr["follow"], ib14=fr["inband14"], contact=fr["contact"], depth_n=dep.get("n"), depth_sum=dep.get("sum"),
                    depth_max=dep.get("max"), ovh_depth_n=dep.get("ovh140"), th=th.get("min"), why=d.get("why"), dK=ex.get("dK_taken_max_deg"),
                    dK_lim=ex.get("dK_lim_deg"), pa=[ex.get("pa_crank_max"), ex.get("pa_horn_max")], failing=ex.get("poses_failing"), byc=byc,
                    ws90=(ex.get("ws_inband") or {}).get("e90_140"), margin=d.get("margin"), price=d.get("price"))
print("| config / protocol / reading | gap (full-flood connected) | 1 mm / 2 mm | reach | follow | ib14 | contact poses | depth sum / max (mm) | fold / slide | min th | dK taken / lim | PA kin crank / horn | failing |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for nm in sorted(rows):
    r = rows[nm]; w = r["why"] or {}
    print(f"| {nm} | {r['gap']} ({r['conn']}) | {r['n1']} / {r['n2']} | {r['reach']:.4f} | {r['follow']} | {r['ib14']:.4f} | {r['depth_n']} | {r['depth_sum']} / {r['depth_max']} | "
          f"{w.get('fold')} / {w.get('slide')} | {r['th']} | {r['dK']} / {r['dK_lim']} | {r['pa'][0]} / {r['pa'][1]} | {r['failing']} |")
print()
print("classes (workspace poses): taken / n, contact poses, summed depth mm")
for nm in sorted(rows):
    r = rows[nm]
    print(nm, {k: f"{v['taken']}/{v['n']} c{v['contact']} {v['depth']:.1f}" for k, v in sorted(r["byc"].items())})
print()
print("gain over the verified config (BEST), same protocol and reading (positive = better): gap, 1 mm, 2 mm, depth (mm, positive = deeper)")
gains = {}
for nm in sorted(rows):
    if nm.startswith("BEST_"): continue
    cfg, rest = nm.split("_", 1); b = rows.get("BEST_" + rest)
    if not b: continue
    r = rows[nm]; g = dict(gap=round(b["gap"] - r["gap"], 2), n1=round(b["n1"] - r["n1"], 2), n2=round(b["n2"] - r["n2"], 2),
                           depth=round((r["depth_sum"] or 0) - (b["depth_sum"] or 0), 2))
    gains[nm] = g; print(nm, g)
json.dump(dict(rows=rows, gains=gains), open(os.path.join(HERE, "summary.json"), "w"), indent=1, default=float)
