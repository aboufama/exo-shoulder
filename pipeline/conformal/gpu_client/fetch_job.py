"""Fetch a finished RunPod job's output by id (when the client died on a transient API error) -> band_eval_<tag>.json
    python3 fetch_job.py <endpoint id> <job id> <tag>"""
import json, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "tools")); import runpod_guard as G
ep, job, tag = sys.argv[1:4]
for _ in range(120):
    try: d = G._call(f"{G.RUN}/{ep}/status/{job}")
    except Exception as e: print("status error", str(e)[:120], flush=True); time.sleep(20); continue
    st = d.get("status"); print(st, flush=True)
    if st == "COMPLETED":
        out = d["output"]; json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"band_eval_{tag}.json"), "w")); print("saved", tag); break
    if st in ("FAILED", "CANCELLED", "TIMED_OUT"): print(json.dumps(d)[:500]); break
    time.sleep(30)
