"""Write-up page for the CAD designs (full-exo/report.html): per design the honest score, per-motion results, kinematics,
the v4 joint stack, custom parts with materials and masses, verification and links to the 3D viewer.

    python3 report_gen.py <key>[:label] [...]
"""
import json, os, sys, html, math
HERE = os.path.dirname(os.path.abspath(__file__)); FC = os.path.join(HERE, "..", "conformal", "fair_cad"); IN = os.path.join(HERE, "..", "conformal", "band_cad", "inputs")
LV = json.load(open(os.path.join(HERE, "designs", "joint_v4", "levels.json")))
def esc(s): return html.escape(str(s))
cards = []
for arg in sys.argv[1:]:
    key, label = (arg.split(":", 1) + [None])[:2]; dd = os.path.join(HERE, "designs", f"cad_{key}")
    sc = json.load(open(os.path.join(dd, "score.json"))); parts = json.load(open(os.path.join(FC, f"out_{key}", "parts.json")))
    R = json.load(open(os.path.join(IN, f"{key}.json")))["results"][0]; N = R["n"]; cuff = R.get("cuff")
    label = label or (f"{N} joints + sliding cuff" if cuff else f"{N} joints")
    custom = [p for p in parts["parts"] if p["mass_g"]]; mass = sum(p["mass_g"] for p in custom)
    big = sorted([p for p in custom if p["name"].startswith(("D4-", "BOTTOM +"))], key=lambda p: p["name"])
    hw = {}
    for p in custom:
        if p["name"].startswith(("D4-", "BOTTOM +")): continue
        k = p["name"].split(" ", 1)[1] if p["name"].startswith("J") else p["name"]; k = k.split(" (")[0]
        hw.setdefault(k, [0, 0.0]); hw[k][0] += 1; hw[k][1] += p["mass_g"]
    clips = "".join(f'<div class="bar"><span>{esc(c["name"])}</span><i style="--v:{100 * c["score"]:.0f}%"></i><b>{100 * c["score"]:.0f}%</b></div>' for c in sc["clips"])
    stills = [f for f in sorted(os.listdir(os.path.join(dd, "stills"))) if f.endswith(".png")] if os.path.isdir(os.path.join(dd, "stills")) else []
    gal = "".join(f'<img src="designs/cad_{key}/stills/{f}" alt="{esc(label)} render {i + 1}" loading="lazy">' for i, f in enumerate(stills))
    kin = (f'J1 axis az {R["az"]:.0f}° / el {R["el"]:.0f}° (base on the {"top/back" if R["el"] > 30 else "back"} of the shoulder) · arcs {", ".join(f"{x:.0f}°" for x in R["a"])} · '
           f'J{N} axis {R["w"][0]:.0f}° / {R["w"][1]:.0f}° on the arm' + (f' · sliding cuff ±{cuff["range"]:.0f}° on a curved dovetail' if cuff else ''))
    rows = "".join(f'<tr><td>{esc(p["name"])}</td><td>{esc(p["material"])}</td><td class="n">{p["mass_g"]:.1f}</td></tr>' for p in big)
    rows += "".join(f'<tr class="hw"><td>{esc(k)} × {v[0]}</td><td></td><td class="n">{v[1]:.1f}</td></tr>' for k, v in sorted(hw.items(), key=lambda kv: -kv[1][1]))
    cards.append(f'''<section class="card"><header><h2>{esc(label)}</h2><a class="btn" href="index.html?d=cad_{key}">Open in 3D viewer</a></header>
<div class="kpis"><div><b>{100 * sc["overall"]:.1f}%</b><span>honest score</span></div><div><b>{100 * sc["follow"]:.0f}%</b><span>frames followed</span></div>
<div><b>{100 * sc["in_band"]:.0f}%</b><span>covered skin 2–10 mm</span></div><div><b>{mass:.0f} g</b><span>custom parts</span></div><div><b>{N + (1 if cuff else 0) - 3 + 3}</b><span>DOF</span></div></div>
{f'<div class="gal">{gal}</div>' if gal else ''}
<h3>Per motion</h3><div class="bars">{clips}</div>
<h3>Kinematics</h3><p>{kin}</p>
<h3>Parts</h3><table><thead><tr><th>part</th><th>material</th><th class="n">g</th></tr></thead><tbody>{rows}</tbody></table>
<h3>Verification</h3><p>Every member pair and the arm-end parts checked for interpenetration in every followed frame (real joint stacks and caps included); frames that could not clear are held, not hidden. Skin clearance ≥ 2 mm in every followed frame from the dense per-frame skin maps.</p></section>''')
stack = (f'Lower plate {LV["S"] - LV["F"]:.1f} mm · washer A recessed (0.15 proud) · upper hub {LV["U1"] - LV["U0"]:.2f} mm · washer B · ring nut on an M8×0.5 stub (sets 0.02 mm float) · '
         f'magnet Ø4×2 N52 under the sensor IC (0.40 mm gap) · Ø22 G2 dome cap · <b>{LV["top"] - LV["F"]:.2f} mm</b> above the skin face on a Ø23 hub')
page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>EXO Shoulder Designs</title>
<style>
:root {{ --bg:#f3f2ef; --card:#fff; --ink:#1b1c1f; --dim:#6c6e74; --line:rgba(0,0,0,.08); --acc:#cc6b08; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#121315; --card:#1b1c1f; --ink:#ececef; --dim:#9a9ca3; --line:rgba(255,255,255,.09); }} }}
:root[data-theme="dark"] {{ --bg:#121315; --card:#1b1c1f; --ink:#ececef; --dim:#9a9ca3; --line:rgba(255,255,255,.09); }}
body {{ margin:0; background:var(--bg); color:var(--ink); font:15px/1.55 -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", sans-serif; }}
main {{ max-width:1080px; margin:0 auto; padding:40px 16px 80px; }}
h1 {{ font-size:28px; letter-spacing:-.02em; margin:0 0 6px; }} .lead {{ color:var(--dim); max-width:760px; margin:0 0 28px; }}
.card {{ background:var(--card); border:1px solid var(--line); border-radius:18px; padding:24px; margin:0 0 24px; }}
header {{ display:flex; justify-content:space-between; align-items:center; gap:12px; flex-wrap:wrap; }} h2 {{ margin:0; font-size:21px; letter-spacing:-.01em; }}
h3 {{ font-size:13px; text-transform:uppercase; letter-spacing:.06em; color:var(--dim); margin:22px 0 8px; }}
.btn {{ color:var(--ink); text-decoration:none; border:1px solid var(--line); border-radius:10px; padding:6px 12px; }} .btn:hover {{ border-color:var(--acc); }}
.kpis {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(120px, 1fr)); gap:12px; margin:18px 0 6px; }}
.kpis div {{ border:1px solid var(--line); border-radius:12px; padding:10px 12px; }} .kpis b {{ display:block; font-size:22px; font-variant-numeric:tabular-nums; }} .kpis span {{ color:var(--dim); font-size:12px; }}
.gal {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:10px; margin-top:14px; }} .gal img {{ width:100%; border-radius:12px; display:block; }}
.bars {{ display:grid; gap:6px; }} .bar {{ display:grid; grid-template-columns:180px 1fr 44px; align-items:center; gap:10px; font-size:13px; }}
.bar i {{ height:8px; border-radius:4px; background:linear-gradient(90deg, var(--acc) var(--v), var(--line) var(--v)); }} .bar b {{ font-weight:500; text-align:right; font-variant-numeric:tabular-nums; }}
table {{ width:100%; border-collapse:collapse; font-size:13px; }} td, th {{ text-align:left; padding:6px 4px; border-top:1px solid var(--line); }} th {{ color:var(--dim); font-weight:500; }}
.n {{ text-align:right; font-variant-numeric:tabular-nums; }} tr.hw td {{ color:var(--dim); }}
@media (max-width:600px) {{ .bar {{ grid-template-columns:110px 1fr 40px; }} }}
</style></head><body><main>
<h1>EXO shoulder: winning designs in real CAD</h1>
<p class="lead">Searched on the real part geometry (FEA-sized 5.5 mm link bodies, the v4 joint stack, skin-hugging neck merged into BOTTOM, base anchored to the back plate), built as G2 sheet bodies and checked for collisions in every frame. Scores are the honest skin-band measure over the eight daily-living motions. <a href="joint.html">Joint v4 in 3D</a> · <a href="film.html">Film preview</a></p>
<section class="card"><h2>Joint v4 (every joint)</h2><p>{stack}. Same bearing internals as v3 (igus iglidur G thrust washers 10×18×0.5, GSM-1012-04 sleeve, integral Ø10 h9 Ti pin), FEA-sized at 25 N·m worst direction.</p></section>
{"".join(cards)}
</main></body></html>'''
open(os.path.join(HERE, "report.html"), "w").write(page); print("wrote report.html with", len(cards), "designs")
