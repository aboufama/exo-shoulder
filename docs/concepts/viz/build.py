"""Build the concept gallery (docs/concepts/viz).

    python3 docs/concepts/viz/build.py [--only id1,id2]     (--only: include just these concept files)

1. meta.js           window.CONCEPT_META from docs/dashboard/data/morphs.json (minus status "duplicate") + catalogue.json
                     (idea, topology, main risk) + t_ideated / t_screened for the Timeline mode
2. index.html        the dev page: the <!-- concepts:begin/end --> block is rewritten to load every concepts/*.js
3. dist/index.html   ONE self-contained page for the Artifact: every local script inlined (kin.js, concepts, meta,
                     viewer.js); only three.js r128 (cdnjs) and OrbitControls (jsDelivr) stay external.
"""
import datetime, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
MORPHS = os.path.join(REPO, "docs", "dashboard", "data", "morphs.json")
CAT = os.path.join(REPO, "docs", "concepts", "catalogue.json")

BASELINE = dict(
    description="The swarm's reference: a pure spherical 3R chain with every joint axis through the GH centre, 20 mm hubs "
                "and 8 x 3 mm strap links. The base axis is fixed on the scapula, the last axis on the humerus, and J2 "
                "follows from the two-circle closure.",
    topology="Scapula base -> J1 hub (axis b through GH) -> link 1 (great-circle strap) -> J2 hub (axis through GH) -> "
             "link 2 -> J3 hub (axis W fixed in the humerus) -> arm-end neck -> the user's cuff.",
    main_risk="J2 folds near overhead (the three axes become coplanar); hub 2 has no quiet skin under it in abduction.")


def short_name(name):
    s = name.split(": ")[0].strip()
    if len(s) <= 52: return s
    for sep in (" - ", " (", " + ", ", "):
        if sep in s and len(s.split(sep)[0]) >= 12: return s.split(sep)[0].strip()
    return s[:50].rsplit(" ", 1)[0] + "…"


def clip(s, n):
    s = (s or "").strip()
    return s if len(s) <= n else s[:n].rsplit(" ", 1)[0] + "…"


def meta():
    morphs = json.load(open(MORPHS)); cat = {c["id"]: c for c in json.load(open(CAT))}
    keep = ("id", "name", "family", "lens", "status", "active_dof", "passive_dof", "t_ideated", "t_screened", "reach", "follow",
            "inband14", "inband10", "contact", "gap", "v_gap", "v_reach", "v_follow", "v_inband14", "v_contact", "n_configs", "doc")
    out = []
    for m in morphs:
        if m.get("status") == "duplicate": continue
        c = cat.get(m["id"]) or (BASELINE if m["id"] == "baseline-3r" else {})
        r = {k: m.get(k) for k in keep}
        r["short"] = short_name(m["name"])
        r["description"] = clip(c.get("description"), 900)
        r["topology"] = clip(c.get("topology"), 1400)
        r["main_risk"] = clip(c.get("main_risk"), 700)
        r["verdict"] = clip(m.get("verdict"), 700)
        if not r["t_ideated"]: r["t_ideated"] = c.get("t_ideated")
        out.append(r)
    built = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    return dict(built=built, concepts=out)


def main():
    import sys
    concepts = sorted(f for f in os.listdir(os.path.join(HERE, "concepts")) if f.endswith(".js"))
    if "--only" in sys.argv:
        only = set(sys.argv[sys.argv.index("--only") + 1].split(","))
        concepts = [f for f in concepts if f[:-3] in only]
    M = meta()
    meta_js = "window.CONCEPT_META = " + json.dumps(M, ensure_ascii=False, separators=(",", ":")) + ";\n"
    open(os.path.join(HERE, "meta.js"), "w").write(meta_js)
    page = open(os.path.join(HERE, "index.html")).read()
    block = "<!-- concepts:begin -->\n" + "".join(f'<script src="concepts/{f}"></script>\n' for f in concepts) + "<!-- concepts:end -->"
    page = re.sub(r"<!-- concepts:begin -->.*?<!-- concepts:end -->", block, page, flags=re.S)
    open(os.path.join(HERE, "index.html"), "w").write(page)

    def inline(m):
        src = m.group(1)
        if src.startswith("http"): return m.group(0)
        js = meta_js if src == "meta.js" else open(os.path.join(HERE, src)).read()
        return f"<script>/* {src} */\n" + js.replace("</script", "<\\/script") + "\n</script>"
    dist = re.sub(r'<script src="([^"]+)"></script>', inline, page)
    dist = re.sub(r"<!-- concepts:(begin|end) -->\n?", "", dist)
    os.makedirs(os.path.join(HERE, "dist"), exist_ok=True)
    open(os.path.join(HERE, "dist", "index.html"), "w").write(dist)
    ext = re.findall(r'<script src="(http[^"]+)"', dist)
    print(f"meta: {len(M['concepts'])} concepts ({sum(1 for c in M['concepts'] if c['t_screened'])} screened); "
          f"previews: {len(concepts)}; dist/index.html {len(dist) / 1024:.0f} kB; external scripts: {ext}")


if __name__ == "__main__":
    main()
