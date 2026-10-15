#!/usr/bin/env python3
"""RunPod cost guard for the exo-shoulder search endpoints (stdlib only; the API key is never printed or stored).

    python3 tools/runpod_guard.py audit                 table of endpoints, scaling, queue/workers, spend/hr, balance + flags
    python3 tools/runpod_guard.py enforce [--dry]       fix ONLY the safe things on our exo-* endpoints (see below)
    python3 tools/runpod_guard.py watch [--interval 300] [--max-hours 2.5] [--max-secs 3000] [--ep exo-band11]
                                        [--start-balance B] [--mute kind,kind] [--log FILE]
                                        [--baseline 0.078] [--seen-jobs]
                                        poll health + spend; exits 2 on an anomaly (message on stdout), 0 when the work
                                        is done (queue empty + no workers for 3 polls -> runs enforce), 3 at the time limit

Key: RUNPOD_API_KEY, else ~/.runpod_key. Never touches pods (crl-* are the user's) and never deletes anything.
enforce rules: any exo-* endpoint: workersMin -> 0, idleTimeout -> min(current, 30); superseded exo-band8/9/10/11:
workersMax -> 0; exo-blender-cycles (the user's render endpoint): ONLY workersMin -> 0. Everything else is left alone.
"""
import argparse, json, os, sys, time, urllib.error, urllib.request

REST = "https://rest.runpod.io/v1"
GQL = "https://api.runpod.io/graphql"
RUN = "https://api.runpod.ai/v2"
OLD = {"exo-band8", "exo-band9", "exo-band10", "exo-band11", "exo-band12", "exo-band13", "exo-band14", "exo-band15", "exo-band16", "exo-band17", "exo-band18", "exo-band20", "exo-band21", "exo-band22"}   # superseded search endpoints: keep at workersMax 0
USER_EP = {"exo-blender-cycles"}                        # the user's render endpoint: only workersMin -> 0
IDLE_MAX = 60                                           # s; above this is flagged
IDLE_SET = 30                                           # s; enforce lowers idleTimeout to at most this
STATE = os.path.expanduser("~/.cache/runpod_guard.json")  # only timestamps/counters, no secrets


def _key():
    k = os.environ.get("RUNPOD_API_KEY", "").strip()
    if not k:
        try:
            k = open(os.path.expanduser("~/.runpod_key")).read().strip()
        except OSError:
            sys.exit("no API key: set RUNPOD_API_KEY or create ~/.runpod_key")
    return k


def _call(url, body=None, method=None, retries=2):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method or ("POST" if data else "GET"),
                                 headers={"Authorization": "Bearer " + _key(), "Content-Type": "application/json",
                                          "User-Agent": "exo-runpod-guard/1"})
    for i in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read() or b"null")
        except urllib.error.HTTPError as e:
            if e.code >= 500 and i < retries:
                time.sleep(2 * (i + 1)); continue
            raise RuntimeError(f"HTTP {e.code} {url.split('//')[1].split('?')[0]}: {e.read()[:200]!r}")
        except (urllib.error.URLError, TimeoutError) as e:
            if i < retries:
                time.sleep(2 * (i + 1)); continue
            raise RuntimeError(f"{type(e).__name__} {url.split('//')[1].split('?')[0]}")


def gql(q):
    d = _call(GQL, {"query": q})
    if d.get("errors"):
        raise RuntimeError("graphql: " + str(d["errors"][0].get("message"))[:200])
    return d["data"]


def account():
    """One GraphQL call: balance, spend/hr, limit and all endpoints (min/max/idle/exec timeout/gpu groups)."""
    return gql("query { myself { clientBalance currentSpendPerHr spendLimit endpoints { id name workersMin workersMax "
               "idleTimeout executionTimeoutMs scalerType scalerValue gpuIds } } }")["myself"]


def health(eid):
    try:
        return _call(f"{RUN}/{eid}/health")
    except RuntimeError as e:
        return {"error": str(e)}


def _short_gpus(g):
    return (g or "").replace("NVIDIA ", "").replace("GeForce ", "").replace(" Generation", "")


def _hsum(h):
    if not h or "error" in h:
        return dict(q=0, prog=0, run=0, idle=0, init=0, unh=0, done=0, ok=False)
    j, w = h.get("jobs", {}), h.get("workers", {})
    return dict(q=j.get("inQueue", 0), prog=j.get("inProgress", 0), run=w.get("running", 0), idle=w.get("idle", 0),
                init=w.get("initializing", 0), unh=w.get("unhealthy", 0), done=j.get("completed", 0), ok=True)


def _state():
    try:
        return json.load(open(STATE))
    except (OSError, ValueError):
        return {}


def _save_state(s):
    try:
        os.makedirs(os.path.dirname(STATE), exist_ok=True)
        json.dump(s, open(STATE, "w"))
    except OSError:
        pass


def audit(quiet=False):
    me = account(); st = _state(); now = time.time(); rows, flags = [], []
    for e in sorted(me["endpoints"], key=lambda e: e["name"]):
        n = e["name"]
        if not n.startswith("exo-"):
            continue
        live = e["workersMax"] > 0 or e["workersMin"] > 0
        h = _hsum(health(e["id"])) if live else _hsum(None)
        rows.append((n, e, h, live))
        if e["workersMin"] > 0:
            flags.append(f"{n}: workersMin={e['workersMin']} (always-on billing) -> 0")
        if n in OLD and e["workersMax"] > 0:
            flags.append(f"{n}: superseded endpoint has workersMax={e['workersMax']} -> 0")
        if e["idleTimeout"] > IDLE_MAX and e["workersMax"] > 0:
            flags.append(f"{n}: idleTimeout={e['idleTimeout']}s > {IDLE_MAX}s -> {IDLE_SET}")
        if live:
            busy = h["q"] + h["prog"]
            if h["ok"] and busy == 0 and (h["idle"] + h["run"] + h["init"]) > 0:
                ghost = me["currentSpendPerHr"] <= 0.078 + 0.15      # account counter at the idle-storage baseline: not billing
                flags.append(f"{n}: {h['idle']} idle/{h['run']} running/{h['init']} init workers, empty queue"
                             + (" (spend/hr at baseline: listed but not billed)" if ghost else " (BILLING: check idleTimeout)")
                             + (" (user's render endpoint: report only)" if n in USER_EP else ""))
            if h["ok"] and 0 < busy < e["workersMax"] and n not in OLD:
                flags.append(f"{n}: workersMax={e['workersMax']} but only {busy} job(s) -> {busy} worker(s) is enough")
            if h["unh"]:
                flags.append(f"{n}: {h['unh']} unhealthy worker(s)")
            # stuck queue: jobs waiting, none running, for > 10 min (first-seen time kept in a state file)
            k = "stuck_" + e["id"]
            if h["q"] > 0 and h["prog"] == 0 and h["run"] == 0:
                t0 = st.setdefault(k, now)
                if now - t0 > 600:
                    flags.append(f"{n}: {h['q']} job(s) queued with nothing running for {(now - t0) / 60:.0f} min (stuck)")
            else:
                st.pop(k, None)
        if n not in OLD and n not in USER_EP and e["workersMax"] > 0:
            if not e.get("executionTimeoutMs"):
                flags.append(f"{n}: executionTimeoutMs=0 (no server-side runaway limit; decorator value was not applied)")
    _save_state(st)
    if me["currentSpendPerHr"] > 4:
        flags.append(f"account spend/hr ${me['currentSpendPerHr']:.2f} > $4")
    if quiet:
        return me, rows, flags
    print(f"RunPod audit {time.strftime('%Y-%m-%d %H:%M', time.gmtime())} UTC | balance ${me['clientBalance']:.2f} | "
          f"spend/hr ${me['currentSpendPerHr']:.3f} | limit ${me['spendLimit']}")
    print(f"{'endpoint':19s} {'min':>3s} {'max':>3s} {'idle':>4s} {'exec':>5s} {'queue':>5s} {'prog':>4s} {'run':>3s} {'idl':>3s} gpu groups")
    for n, e, h, live in rows:
        q = f"{h['q']:5d} {h['prog']:4d} {h['run']:3d} {h['idle']:3d}" if live and h["ok"] else f"{'-':>5s} {'-':>4s} {'-':>3s} {'-':>3s}"
        print(f"{n:19s} {e['workersMin']:3d} {e['workersMax']:3d} {e['idleTimeout']:3d}s {e.get('executionTimeoutMs') or 0:5d} {q} {e['gpuIds']}")
    print("FLAGS:" if flags else "no inefficiencies flagged")
    for f in flags:
        print("  - " + f)
    return me, rows, flags


def _patch(eid, body, dry):
    if dry:
        return
    _call(f"{REST}/endpoints/{eid}", body, method="PATCH")


def enforce(dry=False):
    me = account(); done = []
    for e in me["endpoints"]:
        n = e["name"]
        if not n.startswith("exo-"):
            continue                                   # never touch anything that is not ours (crl-*, others)
        body = {}
        if e["workersMin"] > 0:
            body["workersMin"] = 0
        if n in USER_EP:
            pass                                       # the user's render endpoint: workersMin only
        else:
            if e["idleTimeout"] > IDLE_SET:
                body["idleTimeout"] = min(e["idleTimeout"], IDLE_SET)
            if n in OLD and e["workersMax"] > 0:
                body["workersMax"] = 0
        if body:
            _patch(e["id"], body, dry)
            done.append(f"{n}: {body}{' (dry run)' if dry else ''}")
    print("enforce: " + ("; ".join(done) if done else "nothing to fix (all exo-* endpoints already safe)"))
    return done


def watch(a):
    ep = a.ep; log = open(a.log, "a") if a.log else None
    muted = set(filter(None, (a.mute or "").split(",")))
    t_end = time.time() + a.max_hours * 3600
    start_bal = a.start_balance; seen_jobs = a.seen_jobs
    c = dict(empty=0, billing_idle=0, stuck_q=0); last_done = None; t_done = time.time(); first = True
    def emit(line):
        stamp = time.strftime("%H:%M:%S", time.gmtime())
        if log:
            log.write(f"{stamp} {line}\n"); log.flush()
    while True:
        try:
            me = account()
            e = next((x for x in me["endpoints"] if x["name"] == ep), None)
            if e is None:
                emit(f"no endpoint {ep}"); time.sleep(a.interval); continue
            h = _hsum(health(e["id"]))
        except RuntimeError as ex:
            emit("poll error " + str(ex)[:120]); time.sleep(60); continue
        bal, sp = me["clientBalance"], me["currentSpendPerHr"]
        if start_bal is None:
            start_bal = bal
        spent = start_bal - bal
        busy = h["q"] + h["prog"]; billing = h["idle"] + h["run"] + h["init"]
        if billing and sp <= a.baseline + 0.15:   # health still lists workers but the account counter shows no GPU billing: stale report
            billing = 0
        if busy or h["run"]:
            seen_jobs = True
        if h["done"] != last_done:
            last_done = h["done"]; t_done = time.time()
        emit(f"q={h['q']} prog={h['prog']} run={h['run']} idle={h['idle']} init={h['init']} unh={h['unh']} done={h['done']} "
             f"min={e['workersMin']} max={e['workersMax']} spend/hr={sp:.3f} bal={bal:.2f} spent={spent:.2f}")
        an = []
        if any(x["workersMin"] > 0 for x in me["endpoints"] if x["name"].startswith("exo-")):
            an.append(("workersMin", "workersMin > 0 on " + ",".join(x["name"] for x in me["endpoints"] if x["workersMin"] > 0)))
        if sp > 4:
            an.append(("spend", f"spend/hr ${sp:.2f} > $4"))
        if spent >= 4:
            an.append(("budget", f"spent ${spent:.2f} this session (cap $5)"))
        c["billing_idle"] = c["billing_idle"] + 1 if (busy == 0 and billing > 0) else 0
        if c["billing_idle"] > 2:
            an.append(("idle", f"{billing} workers (idle {h['idle']}/run {h['run']}) billing with an empty queue for {c['billing_idle']} polls"))
        c["stuck_q"] = c["stuck_q"] + 1 if (h["q"] > 0 and h["prog"] == 0 and h["run"] == 0) else 0
        if c["stuck_q"] > 2:
            an.append(("stuckq", f"{h['q']} job(s) queued, none running, for {c['stuck_q']} polls (~{c['stuck_q'] * a.interval / 60:.0f} min)"))
        if h["prog"] > 0 and time.time() - t_done > a.max_secs + 600:
            an.append(("stuckjob", f"jobs in progress but none completed for {(time.time() - t_done) / 60:.0f} min "
                                   f"(> max_secs {a.max_secs:.0f}s + 10 min)"))
        new = [(k, m) for k, m in an if k not in muted]
        if new:
            msg = "ANOMALY " + " | ".join(m for _, m in new) + f" | q={h['q']} prog={h['prog']} run={h['run']} idle={h['idle']} spent=${spent:.2f}"
            emit(msg); print(msg, flush=True); return 2
        # finished: work was seen, now an empty queue and no workers for 3 polls in a row
        c["empty"] = c["empty"] + 1 if (seen_jobs and busy == 0 and billing == 0) else 0
        if c["empty"] >= 3:
            emit("DONE: queue empty, 0 workers x3"); r = enforce(); emit(f"enforce -> {r}")
            print(f"DONE spent=${spent:.2f} bal=${bal:.2f}", flush=True); return 0
        if time.time() >= t_end:
            emit("time limit"); print(f"TIME-LIMIT spent=${spent:.2f} bal=${bal:.2f} q={h['q']} run={h['run']}", flush=True); return 3
        time.sleep(a.interval)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("cmd", choices=["audit", "enforce", "watch"])
    p.add_argument("--dry", action="store_true"); p.add_argument("--interval", type=int, default=300)
    p.add_argument("--max-hours", type=float, default=2.5); p.add_argument("--max-secs", type=float, default=3000)
    p.add_argument("--ep", default="exo-band11"); p.add_argument("--start-balance", type=float)
    p.add_argument("--mute", default=""); p.add_argument("--log")
    p.add_argument("--baseline", type=float, default=0.078, help="idle spend/hr with no GPU worker (crl-* storage)")
    p.add_argument("--seen-jobs", action="store_true", help="work already ran before this watch started")
    a = p.parse_args()
    try:
        if a.cmd == "audit":
            audit()
        elif a.cmd == "enforce":
            enforce(a.dry)
        else:
            sys.exit(watch(a))
    except RuntimeError as e:
        sys.exit(f"error: {e}")


if __name__ == "__main__":
    main()
