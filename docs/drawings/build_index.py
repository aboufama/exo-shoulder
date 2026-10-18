"""Builds docs/drawings/index.html (a plain viewer of the drawing sheets, set B first) and docs/drawings/files.json
(the supporting-file map for publishing) from docs/drawings/<set>/sheets.json.

    python3 docs/drawings/build_index.py
"""
import html, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
SETS = [("B", "Set B · Pin knee H1b", "3 hubs, 3 links, a two-pin knee to the arm pad. Verified score 90.11, complexity 0. The design to build."),
        ("A", "Set A · Cone-cut chain (reference)", "The 3-joint lead's chain (score 93.35). Design A adds a cuff relay that is not modelled in CAD yet.")]


def main():
    files, sets = {}, []
    for key, title, sub in SETS:
        p = os.path.join(HERE, key, "sheets.json")
        if not os.path.exists(p):
            continue
        sj = json.load(open(p))
        sheets = []
        for i, s in enumerate(sj["sheets"], 1):
            pub = f"{key}/{s['file']}"
            files[pub] = os.path.relpath(os.path.join(HERE, key, s["file"]), os.path.dirname(os.path.dirname(HERE)))
            sheets.append({"src": pub, "n": i, "t": s["title"], "pn": s.get("pn", "")})
        sets.append({"key": key, "title": title, "sub": sub, "sheets": sheets, "pdf": sj["pdf"]})
    page = open(os.path.join(HERE, "template.html")).read().replace("%%DATA%%", json.dumps(sets).replace("</", "<\\/"))
    open(os.path.join(HERE, "index.html"), "w").write(page)
    json.dump(files, open(os.path.join(HERE, "files.json"), "w"), indent=0)
    print("index.html:", sum(len(s["sheets"]) for s in sets), "sheets")


if __name__ == "__main__":
    main()
