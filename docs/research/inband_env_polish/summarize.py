"""summary tables of docs/research/inband_env_polish/farm/claim_*.json (+ per-pose dumps): the claim table, the held-out gain
over the row's pick on the same protocol, contact depth by class (low-arm extreme rotation: elev < 60, |axial| >= 120;
overhead elev >= 140), the fold-limited classes.
    python3 docs/research/inband_env_polish/summarize.py [farm dir]"""
import json, os, sys, glob
F = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "farm")
C = {}
for f in sorted(glob.glob(os.path.join(F, "claim_*.json"))):
    if f.endswith("_perpose.json") or f.endswith("_params.json"): continue
    try: d = json.load(open(f))
    except Exception: continue
    nm = os.path.basename(f)[6:-5]; C[nm] = d


def cls(p):
    el, pl, ax = p["elev"], p["plane"], p["axial"]
    out = []
    if el < 60 and abs(ax) >= 120: out.append("lowarm_xrot")
    if el >= 140: out.append("overhead")
    if pl >= 100 and el >= 40: out.append("across")
    if abs(ax) >= 150: out.append("ax150")
    return out


rows = []
for nm, d in C.items():
    f = d["final"]; dep = d["depth"]; th = d["th_margin"]; cam = d["cam"]
    pp = os.path.join(F, f"claim_{nm}_perpose.json"); byc = {}
    if os.path.exists(pp):
        P = json.load(open(pp))["poses"]
        for r in P:
            if r["kind"] != "ws": continue
            for c in cls(r):
                b = byc.setdefault(c, dict(n=0, taken=0, contact=0, depth=0.0))
                b["n"] += 1; b["taken"] += int(r["taken"]); b["contact"] += int(r["contact"]); b["depth"] += (-r["min_mm"] if r["contact"] else 0.0)
    rows.append(dict(nm=nm, gap=f["gap"], static=d["static"]["gap"], n1=f["gap_near1"], n2=f["gap_near2"], reach=f["reach"], follow=f["follow"],
                     ib14=f["inband14"], contact=f["contact"], depth_n=dep.get("n"), depth_sum=dep.get("sum"), depth_max=dep.get("max"), th=th.get("min"),
                     why=d.get("why"), dK=d.get("dK_taken_max"), dK_lim=cam.get("dK_lim"), tilt=cam.get("tilt_max_taken"), trans=cam.get("trans_min_taken"),
                     spring=d.get("spring"), dropped=(d.get("conn") or {}).get("dropped"), fresh=(d.get("conn") or {}).get("fresh"), byc=byc,
                     ovh=d.get("overhead"), ws90=(d.get("ws_inband") or {}).get("e90_140"), bk=[d["priced"]["bk1"], d["priced"]["bk2"], d["priced"]["a1max"]],
                     kK=d["priced"]["kK"], margin=d.get("margin")))
print("| config_protocol | gap (static) | 1 mm / 2 mm | reach | follow | ib14 | contact poses | depth sum / max | fold / slide | min th | dK taken / lim | tilt crank / horn | trans | dropped | K dyad / kK |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for r in sorted(rows, key=lambda r: r["nm"]):
    w = r["why"] or {}
    print(f"| {r['nm']} | {r['gap']} ({r['static']}) | {r['n1']} / {r['n2']} | {r['reach']:.4f} | {r['follow']} | {r['ib14']:.4f} | {r['depth_n']} | {r['depth_sum']} / {r['depth_max']} | "
          f"{w.get('fold')} / {w.get('slide')} | {r['th']} | {r['dK']} / {r['dK_lim']} | {r['tilt']} | {r['trans']} | {r['dropped']} | "
          f"{'/'.join(str(round(x, 1)) for x in r['bk'])} / {round(r['kK'], 2)} |")
print()
print("classes (workspace poses): taken / n, contact, summed depth mm")
for r in sorted(rows, key=lambda r: r["nm"]):
    if "held" in r["nm"]:
        print(r["nm"], {k: f"{v['taken']}/{v['n']} c{v['contact']} {v['depth']:.1f}" for k, v in sorted(r["byc"].items())}, "spring", (r["spring"] or {}).get("J2_Nm"), (r["spring"] or {}).get("cuff_N_120"))
ref = {r["nm"].replace("PICK_", ""): r for r in rows if r["nm"].startswith("PICK_")}
print()
print("gain over the row's pick (priced), same protocol (positive = better)")
for r in sorted(rows, key=lambda r: r["nm"]):
    if r["nm"].startswith("pick"):
        prot = r["nm"].split("_", 1)[1]; b = ref.get(prot)
        if b: print(r["nm"], "gap", round(b["gap"] - r["gap"], 2), "1mm", round(b["n1"] - r["n1"], 2), "2mm", round(b["n2"] - r["n2"], 2), "depth", round(r["depth_sum"] - b["depth_sum"], 1))
json.dump(rows, open(os.path.join(F, "summary.json"), "w"), indent=1, default=float)
