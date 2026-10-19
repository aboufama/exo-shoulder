#!/bin/bash
# Build the harness for a data dir and screenshot each tab (1400 / 420 px, full page; dark at 1400) into shots/.
# usage: shoot.sh [data dir (default sample_data)] [tag (default: the dir name)]
D=$(cd "$(dirname "$0")" && pwd)
DATA=${1:-$D/sample_data}; TAG=${2:-$(basename "$DATA")}
python3 "$D/harness/build.py" "$DATA" || exit 1
PORT=$(python3 -c 'import socket; s = socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1])')
python3 -m http.server "$PORT" --bind 127.0.0.1 --directory "$D/harness" >/dev/null 2>&1 &
SRV=$!
trap 'kill $SRV 2>/dev/null' EXIT
for i in 1 2 3 4 5 6 7 8 9 10; do curl -s -o /dev/null "http://127.0.0.1:$PORT/index.html" && break; python3 -c "import time; time.sleep(0.3)"; done
mkdir -p "$D/shots"
node "$D/harness/shot.mjs" "http://127.0.0.1:$PORT" "$D/shots" "$TAG"
