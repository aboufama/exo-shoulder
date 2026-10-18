"""Builds docs/drawings/index.html (a plain viewer of the drawing sheets, set B first) and docs/drawings/files.json
(the supporting-file map for publishing) from docs/drawings/<set>/sheets.json.

    python3 docs/drawings/build_index.py
"""
import html, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
SETS = [("A", "Set A · Cone-cut pin knee (the 3-joint lead)", "3 powered hubs, a cam-slaved knuckle in link 1, a J3 stop and a two-pin knee on ball bearings. Verified score 93.35, held-out gap 22.38."),
        ("B", "Set B · Pin knee H1b (simpler)", "3 hubs, 3 links and a two-pin knee, nothing else. Verified score 90.11, complexity 0.")]


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
