"""fold-ceiling: the drive-stroke parking table from the farm outputs parking_k_{bench,held}_{lead,k2850,k3248}.json
(exact skin; every part at its clip-frame max + d; R_est = workspace poses closed AND cleared by every modelled part)."""
import glob, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); src = sys.argv[1] if len(sys.argv) > 1 else HERE
rows = []
for f in sorted(glob.glob(os.path.join(src, "parking_k_*_*.json"))):
    if f.endswith("_3opt.json") or f.endswith("_fast.json"): continue
    d = json.load(open(f))
    for o in d["options"]:
        rows.append((d["bench"], o))
print("| wear | K dyad | a2 | stroke | window | in window | R_est +0 / +4 / +8 | parts in-band +0 / +4 | new poses cleared +4 | binding parts at +4 (new cleared / new) |")
print("|---|---|---|---|---|---|---|---|---|---|")
for wear, o in rows:
    parts = ("hubK", "hub2", "link1a_mid", "link1b_mid", "hub3_ray", "link2_1/3", "link2_2/3")
    worst = sorted(parts, key=lambda k: o[k]["new_clear_plus4"])[:2]
    print(f"| {wear} | {o['bk1']:g} / {o['bk2']:g} | {o['a2']:.1f} | {o.get('dkmax')} | {o['window'][0]}-{o['window'][1]} | {o['in_window_ws']} | "
          f"{o['R_est_+0']:.3f} / {o['R_est_+4']:.3f} / {o['R_est_+8']:.3f} | {o['ib_parts_+0']:.3f} / {o['ib_parts_+4']:.3f} | "
          f"{o['new_clear_all_parts_+4']} of {o['n_new_ws']} | " + ", ".join(f"{k} {o[k]['new_clear_plus4']}/{o['n_new_ws']}" for k in worst) + " |")
