"""write docs/concepts/viz/concepts/longstroke-slipper-knuckle-3r.js from the model's own viz export (LS_DRIVE=rssr) on the
sidecar RSSR preview's code (docs/concepts/viz/concepts/sidecar-longdyad-knuckle-3r.js: same topology - bell crank on
link 1b, O3 rod with M2 ball links, horn lug of link 1a at hub K).
    LS_DRIVE=rssr python3 docs/research/longstroke_drive/make_viz.py '<params json>' '<header note>'"""
import json, os, re, subprocess, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
par = sys.argv[1]; note = sys.argv[2] if len(sys.argv) > 2 else ""
o = subprocess.run([sys.executable, os.path.join(REPO, "docs/concepts/models/longstroke-slipper-knuckle-3r.py"), "viz", par],
                   capture_output=True, text=True, env=dict(os.environ, LS_DRIVE="rssr", OMP_NUM_THREADS="1")).stdout
X = json.loads(o[o.find("{"):]); P, G = X["P"], X["G"]
P = dict(json.loads(par), **P)                                # the drive params the exporter leaves out (La, gam, ...)
uK = G["uK"]; H = G["rodB"]; hz = sum(a * b for a, b in zip(H, uK)); rr = [h - hz * u for h, u in zip(H, uK)]
nr = sum(x * x for x in rr) ** 0.5; G["hornA"] = [round(hz * u + 10.5 * x / nr, 3) for u, x in zip(uK, rr)]; G["hornB"] = [round(x, 3) for x in H]
src = open(os.path.join(REPO, "docs/concepts/viz/concepts/sidecar-longdyad-knuckle-3r.js")).read()
head = ("/* longstroke-slipper-knuckle-3r at its claimed configuration: slipper-nose's chain (the verified seats, pin knee, link 1\n"
        " * split by a passive O20 knuckle K SLAVED to q2) with the K sub-dyad re-seated long (bk1 %.2f / bk2 %.2f, stop B %.2f) and\n"
        " * a phased RSSR K drive: the hub-2 rim lobe pushes the short arm of a bell crank (MR63ZZ pair on link 1b, long arm La %.1f,\n"
        " * phase gam %.1f); an O3 rod with M2 ball links runs to a lateral horn lug of link 1a at hub K (r_h %.1f, beta %.1f).\n"
        " * Every pressure angle <= 42 deg (transmission >= 48 at both ball ends). %s\n"
        " * Geometry exported from docs/concepts/models/longstroke-slipper-knuckle-3r.py (LS_DRIVE=rssr, mode viz). */\n") % (
    P["bk1"], P["bk2"], P["a1max"], P["La"], P.get("gam", 0.0), P["r_h"], P["beta"], note)
body = src[src.index("(function () {"):]
body = re.sub(r"const P = \{.*?\};\n", "const P = " + json.dumps({k: v for k, v in P.items() if isinstance(v, (int, float, str))}) + ";\n", body, count=1, flags=re.S)
body = re.sub(r"const G = \{.*?\};\n", "const G = " + json.dumps(G) + ";\n", body, count=1, flags=re.S)
body = body.replace("sidecar-longdyad-knuckle-3r", "longstroke-slipper-knuckle-3r")
body = re.sub(r"(id: 'longstroke-slipper-knuckle-3r', name: ')[^']*'", lambda m: m.group(1) + "Long-stroke knuckle: K sub-dyad re-seated long, hub-2 lobe -> bell crank -> phased RSSR rod -> horn of link 1a, every PA <= 42 (3 active, K not read)'", body, count=1)
out = os.path.join(REPO, "docs/concepts/viz/concepts/longstroke-slipper-knuckle-3r.js"); open(out, "w").write(head + body); print(out)
