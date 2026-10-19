"""write docs/concepts/viz/concepts/inband-rssr-knuckle-3r.js from this row's own viz export, on the long-stroke row's
preview code (same topology: bell crank on link 1b, O3 rod with M2 ball links, horn lug of link 1a at hub K) plus the
crank's EAR (a joggled tab of link 1b one layer down, carrying the crank pin) when clay = 1.
    python3 docs/research/inband_drive/make_viz.py '<params json>' '<header note>'"""
import json, os, re, subprocess, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
ID = "inband-rssr-knuckle-3r"
par = sys.argv[1]; note = sys.argv[2] if len(sys.argv) > 2 else ""
o = subprocess.run([sys.executable, os.path.join(REPO, f"docs/concepts/models/{ID}.py"), "viz", par],
                   capture_output=True, text=True, env=dict(os.environ, OMP_NUM_THREADS="1")).stdout
X = json.loads(o[o.find("{"):]); P, G = X["P"], X["G"]
P = dict(json.loads(par), **P)
uK = G["uK"]; H = G["rodB"]; hz = sum(a * b for a, b in zip(H, uK)); rr = [h - hz * u for h, u in zip(H, uK)]
nr = sum(x * x for x in rr) ** 0.5; G["hornA"] = [round(hz * u + 10.5 * x / nr, 3) for u, x in zip(uK, rr)]; G["hornB"] = [round(x, 3) for x in H]
clay = int(P.get("clay", 0))
if clay:                                                       # the ear: from hub 2's rim to the crank pin, one layer under the crank
    ax = G["rockerAx"]; pv = G["rocker"]; u2 = G["u"][1]
    e = [p - (1.5 + 0.15) * a for p, a in zip(pv, ax)]          # ear mid-plane under the crank boss
    z = sum(a * b for a, b in zip(e, u2)); w = [p - z * u for p, u in zip(e, u2)]; nw = sum(x * x for x in w) ** 0.5
    G["earA"] = [round(x, 3) for x in e]; G["earB"] = [round(z * u + 10.5 * x / nw, 3) for u, x in zip(u2, w)]
src = open(os.path.join(REPO, "docs/concepts/viz/concepts/longstroke-slipper-knuckle-3r.js")).read()
head = ("/* %s at its claimed configuration: the long-stroke row's chain (slipper-nose's seats, pin knee, link 1 split by a\n"
        " * passive O20 knuckle K SLAVED to q2; K sub-dyad bk1 %.2f / bk2 %.2f, stop B %.2f) and its phased RSSR K drive on the\n"
        " * steep lobe law (kK %.2f), REPACKAGED in the band: the bell crank (MR63ZZ pair, long arm La %.1f, phase gam %.1f) sits\n"
        " * %s; crank-tip M2 ball %s; O3 rod to the horn lug of link 1a at hub K (r_h %.1f, beta %.1f).\n"
        " * Every pressure angle <= 42 deg (transmission >= 48 at both ball ends). %s\n"
        " * Geometry exported from docs/concepts/models/%s.py (mode viz). */\n") % (
    ID, P["bk1"], P["bk2"], P["a1max"], P.get("kK", 0.0), P["La"], P.get("gam", 0.0),
    "on an EAR of link 1b joggled one layer down, so it runs in link 1b's own layer" if clay else "stacked on link 1b",
    {0: "on a stud over the arm", 1: "under the arm", 2: "on a radial stud in the arm's end face (rod in the arm's mid-plane)"}[int(P.get("bl_c", 0))],
    P["r_h"], P["beta"], note, ID)
body = src[src.index("(function () {"):]
body = re.sub(r"const P = \{.*?\};\n", "const P = " + json.dumps({k: v for k, v in P.items() if isinstance(v, (int, float, str))}) + ";\n", body, count=1, flags=re.S)
body = re.sub(r"const G = \{.*?\};\n", "const G = " + json.dumps(G) + ";\n", body, count=1, flags=re.S)
body = body.replace("longstroke-slipper-knuckle-3r", ID)
body = re.sub(r"(id: '%s', name: ')[^']*'" % ID, lambda m: m.group(1) + "In-band RSSR knuckle: long K dyad, steep hub-2 lobe law, bell crank on a joggled ear in the layer of link 1b -> O3 rod -> horn of link 1a (3 active, K not read)'", body, count=1)
if clay:
    body = body.replace("        { kind: 'link', role: 'link', name: 'bell crank long arm (3 mm Ti, joggled down beside link 1b)'",
                        "        { kind: 'link', role: 'link', name: 'ear of link 1b (3 mm Ti tab, one layer down, carries the crank pin)', a: on(F.R1b, G.earB), b: on(F.R1b, G.earA), r: 2.5 },\n"
                        "        { kind: 'link', role: 'link', name: 'bell crank long arm (3 mm Ti, in link 1b\\'s layer beside the strap)'", 1)
out = os.path.join(REPO, f"docs/concepts/viz/concepts/{ID}.js"); open(out, "w").write(head + body); print(out)
