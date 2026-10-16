#!/bin/bash
# Dashboard refresh helper (docs/OPERATIONS.md "Dashboards"). Rebuilds the datasets and says what to publish.
#
#   tools/dash_refresh.sh                    rebuild docs/dashboard/data/*.json + manifest (tools/dash_build.py), then print
#                                            CHANGED <id> <rows> rows v<version>   one line per production dataset to re-publish
#                                            PAGE changed|unchanged v<version>     the production page (files/index.html)
#                                            PUBLIC unchanged | PUBLIC CHANGED {...} the public mirror's changed files map
#   tools/dash_refresh.sh --no-build         the same report without rebuilding
#   tools/dash_refresh.sh mark <id> <ver>    after a dataset publish: record its current sha256 + the doc's NEW version
#   tools/dash_refresh.sh mark-page <ver>    after updating the page doc files/index.html: record its sha + NEW version
#   tools/dash_refresh.sh mark-public        after republishing the public mirror: record its file shas
#   tools/dash_refresh.sh page-json          write .state/dash_pub/index_html.json = {"text": docs/dashboard/simple/index.html}
#                                            (the file_path for ArtifactData update collection "files", doc_id "index.html")
#   tools/dash_refresh.sh seed '<json>'      write versions read with ArtifactData (a new session has no state):
#                                            '{"morphs": 78, "sweeps": 74, ..., "_files_index_html": 11}'; shas stay unknown
#                                            so every dataset reports CHANGED once (re-publishing an unchanged file is harmless)
#
# State (git-ignored, per machine): .state/dash_pub/state.json   {<id>: {sha, version}, _files_index_html: {sha, version}}
#                                   .state/dash_pub/public_state.json   (tools/dash_public.py --mark)
# Override the folder with DASH_STATE_DIR. Build log: .state/logs/dash_build.log.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
ST="${DASH_STATE_DIR:-$REPO/.state/dash_pub}"
LOG="$REPO/.state/logs"
mkdir -p "$ST" "$LOG"
cd "$REPO"
export ST

case "${1:-}" in
  mark|mark-page|seed)
    python3 - "$@" <<'PY'
import hashlib, json, os, sys
st_path = os.path.join(os.environ["ST"], "state.json")
st = json.load(open(st_path)) if os.path.exists(st_path) else {}
cmd = sys.argv[1]
if cmd == "mark":
    i, v = sys.argv[2], int(sys.argv[3])
    m = {e["id"]: e for e in json.load(open("docs/dashboard/manifest.json"))}
    if i not in m: sys.exit(f"unknown dataset {i} (manifest ids: {', '.join(m)})")
    st[i] = {"sha": m[i]["sha256"], "version": v}
elif cmd == "mark-page":
    sha = hashlib.sha256(open("docs/dashboard/simple/index.html", "rb").read()).hexdigest()
    st["_files_index_html"] = {"sha": sha, "version": int(sys.argv[2])}
else:
    for k, v in json.loads(sys.argv[2]).items():
        st.setdefault(k, {})["version"] = int(v)
json.dump(st, open(st_path, "w"), indent=1)
print("state:", json.dumps({k: v.get("version") for k, v in st.items()}))
PY
    exit 0 ;;
  page-json)
    python3 -c "import json,sys; json.dump({'text': open('docs/dashboard/simple/index.html').read()}, open(sys.argv[1], 'w'))" "$ST/index_html.json"
    echo "$ST/index_html.json"; exit 0 ;;
  mark-public)
    python3 tools/dash_public.py "$ST/public_state.json" --mark >/dev/null && echo "public state marked"
    exit 0 ;;
  --no-build|"") ;;
  *) sed -n '2,20p' "$0"; exit 2 ;;
esac

if [ "${1:-}" != "--no-build" ]; then
  nice -n 10 python3 tools/dash_build.py > "$LOG/dash_build.log" 2>&1 || { echo BUILD_FAILED; tail -5 "$LOG/dash_build.log"; exit 1; }
fi

python3 - <<'PY'
import hashlib, json, os
st_path = os.path.join(os.environ["ST"], "state.json")
st = json.load(open(st_path)) if os.path.exists(st_path) else {}
if not st:
    print("NOSTATE: no", st_path, "- read each dataset's version (ArtifactData list, collection datasets) and run: tools/dash_refresh.sh seed '{...}'")
m = json.load(open("docs/dashboard/manifest.json"))
page_ids = ["morphs", "sweeps", "events", "reqs", "cad", "motion"]          # the datasets the page reads (tools/dash_public.py)
for e in m:
    if e["id"] not in page_ids: continue
    s = st.get(e["id"], {})
    if s.get("sha") != e["sha256"]:
        mb = e["bytes"] / 1e6
        print("CHANGED", e["id"], e["rows"], "rows", "v%s" % s.get("version", "?"), "%.2f MB" % mb, "(OVER 8 MB: do not publish)" if mb > 8 else "")
p = st.get("_files_index_html", {})
sha = hashlib.sha256(open("docs/dashboard/simple/index.html", "rb").read()).hexdigest()
print("PAGE", "unchanged" if p.get("sha") == sha else "changed", "v%s" % p.get("version", "?"))
PY
grep -E "baseline gap|warning" "$LOG/dash_build.log" 2>/dev/null | tail -2 || true
python3 tools/dash_public.py "$ST/public_state.json" | python3 -c "import json,sys; d=json.load(sys.stdin); print('PUBLIC', 'unchanged' if not d['changed'] else 'CHANGED ' + json.dumps(d))"
