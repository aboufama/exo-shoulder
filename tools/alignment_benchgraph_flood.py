"""Bench-graph flood UPPER BOUND from a re-wear's per-pose dump (skeptic tool, read-only).

Same graph as connected() in docs/concepts/models/stop-relay-rocker-3r.py (nodes = taken workspace poses of the worn
bench, an edge joins grid neighbours one step in plane, elevation or axial), seeds = taken workspace poses at elevation
<= SEED (30 deg, as cap-nullspace-4r flood), but WITHOUT the edges' 2-deg slerp closure / jump checks - so the connected
count is an upper bound and the loss a lower bound, for the bench-graph flood only. The bench samples 360 of the 4488
grid cells, so this graph is sparse: it is NOT the rule's envelope flood (connected_full), which uses the whole
envelope as stepping stones.

    python3 tools/alignment_benchgraph_flood.py <id> [bench|held]
"""
import json, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = 30.0


def run(rid, wear="bench"):
    P = json.load(open(os.path.join(REPO, "docs/alignment/remeasure", f"{rid}_{wear}_perpose.json")))["poses"]
    WS = [q for q in P if q["kind"] == "ws"]
    vals = [sorted({q[k] for q in WS}) for k in ("plane", "elev", "axial")]
    cells = {(q["plane"], q["elev"], q["axial"]) for q in WS}
    key = {(q["plane"], q["elev"], q["axial"]): q for q in WS if q["taken"]}

    def nb(x, S):
        for d in range(3):
            j = vals[d].index(x[d])
            for jj in (j - 1, j + 1):
                if 0 <= jj < len(vals[d]):
                    y = list(x); y[d] = vals[d][jj]
                    if tuple(y) in S: yield tuple(y)
    conn = {x for x, q in key.items() if q["elev"] <= SEED}; front = list(conn)
    while front:
        nxt = []
        for a in front:
            for b in nb(a, key):
                if b not in conn: conn.add(b); nxt.append(b)
        front = nxt
    deg = [sum(1 for _ in nb(x, cells)) for x in cells]
    out = dict(id=rid, wear=wear, ws=len(WS), taken=len(key), seeds=sum(1 for q in key.values() if q["elev"] <= SEED),
               connected_upper=len(conn), reach_static=round(len(key) / len(WS), 4), reach_connected_upper=round(len(conn) / len(WS), 4),
               gap_loss_lower=round(100 * (len(key) - len(conn)) / len(WS), 2), bench_neighbours_mean=round(sum(deg) / len(deg), 3),
               ws_cells_without_neighbour=sum(1 for d in deg if d == 0), grid_cells=len(vals[0]) * len(vals[1]) * len(vals[2]))
    print(json.dumps(out)); return out


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "bench")
