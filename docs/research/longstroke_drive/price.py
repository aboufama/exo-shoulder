"""price a drive sweep: stroke (dK_lim at every PA <= 42 incl. friction), what ends it, fast gap / reach / contact, drive
metal in band and skin clearance.   python3 docs/research/longstroke_drive/price.py res_coarse_<drive>.json [...]"""
import json, sys
import numpy as np

for fn in sys.argv[1:]:
    R = json.load(open(fn)); ok = [r for r in R if r.get("report") and "error" not in r]
    print(f"== {fn}: {len(ok)}/{len(R)} evaluated")
    if not ok: continue
    dk = np.array([float((r["report"].get("cam") or {}).get("dK_lim") or 0) for r in ok])
    why = {}
    for r in ok: w = (r["report"].get("cam") or {}).get("why_lim"); why[w] = why.get(w, 0) + 1
    print("  dK_lim: max %.1f, p90 %.1f, median %.1f; >= 57.5: %d, >= 60: %d" % (dk.max(), np.percentile(dk, 90), np.median(dk), (dk >= 57.5).sum(), (dk >= 60).sum()))
    print("  ended by:", dict(sorted(why.items(), key=lambda kv: -kv[1])))
    def row(r):
        rep = r["report"]; c = rep.get("cam") or {}; pl = rep.get("plain") or {}; parts = rep.get("parts_ib14") or {}
        drv = {k: parts.get(k, [None])[0] for k in ("crank", "roller", "horn", "rod", "rodends") if k in parts}
        return dict(gap2=rep.get("gap"), plain=pl.get("gap"), reach=rep.get("reach"), ib=rep.get("inband14"), contact=rep.get("contact"),
                    honest=rep.get("honest"), dK=c.get("dK_lim"), why=c.get("why_lim"), pa=(c.get("pa_crank_max_taken"), c.get("pa_horn_max_taken"), c.get("pa_eff_horn")),
                    trans=c.get("trans_min_taken"), cr=c.get("contact_r"), lug=c.get("lug_r_max"), mm=rep.get("min_metal_mm"), drive_ib=drv,
                    fold=(rep.get("why") or {}).get("fold"), cfg={k: v for k, v in r["config"].items() if k not in ("bk1", "bk2", "a1max")})
    hon = [r for r in ok if r["report"].get("honest") is not False]
    print("  honest:", len(hon))
    for lab, sel in (("best plain (honest)", sorted(hon, key=lambda r: (r["report"].get("plain") or {}).get("gap", 999))[:5]),
                     ("longest stroke (honest)", sorted(hon, key=lambda r: -float((r["report"].get("cam") or {}).get("dK_lim") or 0))[:5]),
                     ("best plain with dK >= 57.5", sorted([r for r in hon if float((r["report"].get("cam") or {}).get("dK_lim") or 0) >= 57.5],
                                                          key=lambda r: (r["report"].get("plain") or {}).get("gap", 999))[:5])):
        print("  --", lab)
        for r in sel: print("    ", json.dumps(row(r), default=float))
