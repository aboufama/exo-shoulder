"""print a screen.py jsonl as a table: python3 docs/research/inband_drive/show.py out/screen*.jsonl"""
import json, sys
for fn in sys.argv[1:]:
    print("==", fn)
    for l in open(fn):
        d = json.loads(l)
        if "error" in d: print(json.dumps(d["ov"]), "ERROR", d["error"][:200]); continue
        p = d["parts"]; w = d["why"]
        f = lambda v: "-" if v is None else f"{v[0]:.2f}/{v[1]:.1f}"
        print(f"{json.dumps(d['ov']):42s} near2 {d['gap']:7.2f} plain {d['plain']:6.2f} reach {d['reach']:.3f} ib {d['inband14']:.4f} cont {d['contact']:.4f} "
              f"(c{w.get('contact')}+s{w.get('skin')} p{w.get('parts')}) dK {d['dK_lim']} {d['why_lim']:12s} crank {f(p['crank'])} rod {f(p['rod'])} "
              f"ends {f(p['rodends'])} horn {f(p['horn'])} ear {f(p['ear'])} tilt {d.get('tilt')} tr {d.get('trans')}")
