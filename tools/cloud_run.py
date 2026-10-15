#!/usr/bin/env python3
"""Run this repo's CPU-heavy commands on the RunPod serverless CPU farm (endpoint exo-cpu1, pipeline/cloud/) - stdlib only.

    python3 tools/cloud_run.py judge <design id> [fast]          tools/judge_all.sh on the farm; judge/*.json, score*.json back
    python3 tools/cloud_run.py run [opts] -- "<bash command>"     one job
    python3 tools/cloud_run.py batch jobs.json [opts]             N jobs at once: [{"cmd", "tag"?, "design"?: [ids], "include"?: [paths],
                                                                  "out"?: [globs], "env"?: {}, "shared"?: [dirs]}, ...]
    python3 tools/cloud_run.py ping                               worker facts (python, packages, CPU, volume)
opts: --design ID (ship pipeline/full-exo/designs/ID, git-ignored parts/ included)   --include PATH (file or dir, repeatable)
      --out GLOB (files to bring back, relative to the repo; only created/changed ones come back)   --env K=V
      --outdir DIR (write returned files under DIR instead of the tree)   --timeout S (default 3000)   --bench-cache
      (ship .cache/concept_bench, the concept bench's signed-distance grids)   --no-base (ship only --include/--design files)
What is shipped (content-addressed, each file uploaded once ever, docs/CLOUD_RUN.md): git-tracked + untracked-not-ignored
files, minus renders/, media, other designs, .claude/; plus what --design/--include name. NEVER shipped (hard deny, also
for --include): data/raw/private/, anything named like a key (.runpod_key, *.key, .env, *.pem, id_*), the user's
personal-shoulder-diagnosis folder, symlinks leaving the repo. The API key (RUNPOD_API_KEY or ~/.runpod_key) is never printed.
Cost: every job prints its seconds and $ (cpu3c-8-16 serverless $0.288/h per worker = $0.036/vCPU-h, up to 4 jobs per
worker; cpu5c-8-16 fallback $0.336/h); the batch line bills each worker for the span of its jobs + the 10 s idle timeout.
Rule (user 2026-10-15, cheap-if-big-speed-up): send a job here only when the batch saves >= 3x wall-clock over this box.
"""
import argparse, base64, concurrent.futures as cf, fnmatch, gzip, hashlib, json, os, subprocess, sys, threading, time
import urllib.error, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GQL = "https://api.runpod.io/graphql"; RUN = "https://api.runpod.ai/v2"
EP_NAME = os.environ.get("CLOUD_EP_NAME", "exo-cpu1")
RATE = {"cpu3c-8-16": 0.288 / 3600, "cpu5c-8-16": 0.336 / 3600}      # $/s per worker, serverless (GraphQL slsPrice, EU-RO-1, 2026-10-15)
SLOTS = 4                                                               # jobs per worker (max_concurrency): a job pays 1/4 of a busy worker
IDLE_S = 10                                                             # endpoint idle timeout: billed once per worker per batch
CHUNK = 6 * 1024 * 1024                                                 # gzip bytes per put job (base64 ~8 MB < the 10 MB /run limit)
MAX_INFLIGHT = int(os.environ.get("CLOUD_MAX_INFLIGHT", 16))           # = workersMax 4 x 4 slots
CACHE = os.path.expanduser("~/.cache/cloud_run"); os.makedirs(CACHE, exist_ok=True)
DENY_DIRS = ("data/raw/private/", ".git/", ".claude/", "renders/")
DENY_NAMES = (".runpod_key", ".env", "id_rsa", "id_ed25519", ".netrc", "credentials", ".pypirc")
DENY_EXT = (".key", ".pem", ".p12", ".mp4", ".mov", ".webm", ".blend", ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".pyc")
_lock = threading.Lock()
REMAP = {}                                                              # manifest sha -> sha actually uploaded (file changed meanwhile)


def _key():
    k = os.environ.get("RUNPOD_API_KEY", "").strip()
    if not k:
        try:
            k = open(os.path.expanduser("~/.runpod_key")).read().strip()
        except OSError:
            sys.exit("no API key: set RUNPOD_API_KEY or create ~/.runpod_key")
    return k


def _http(url, body=None, timeout=60, retries=4):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method="POST" if data else "GET",
                                 headers={"Authorization": "Bearer " + _key(), "Content-Type": "application/json", "User-Agent": "exo-cloud-run/1"})
    for i in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read() or b"null")
        except urllib.error.HTTPError as e:
            msg = e.read()[:300]
            if (e.code >= 500 or e.code == 429) and i < retries:
                time.sleep(2 * (i + 1)); continue
            raise RuntimeError(f"HTTP {e.code} {url.split('//')[1].split('?')[0]}: {msg!r}")
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if i < retries:
                time.sleep(2 * (i + 1)); continue
            raise RuntimeError(f"{type(e).__name__} {url.split('//')[1].split('?')[0]}")


def endpoint_id():
    if os.environ.get("CLOUD_EP"):
        return os.environ["CLOUD_EP"]
    d = _http(GQL, {"query": "query { myself { endpoints { id name } } }"})
    ids = [e["id"] for e in d["data"]["myself"]["endpoints"] if e["name"] == EP_NAME or e["name"].startswith(EP_NAME + "-")]
    if not ids:
        sys.exit(f"no endpoint named {EP_NAME}: deploy pipeline/cloud (docs/CLOUD_RUN.md)")
    return ids[0]


# ------------------------------------------------------------------ what to ship
def _denied(rel):
    r = rel.replace(os.sep, "/"); b = os.path.basename(r).lower()
    if any(r.startswith(d) or ("/" + d) in r for d in DENY_DIRS) or "personal-shoulder-diagnosis" in r:
        return True
    if b in DENY_NAMES or b.startswith("id_") or b.endswith(DENY_EXT) or b.startswith(".env"):
        return True
    p = os.path.join(REPO, rel)
    if os.path.islink(p):
        real = os.path.realpath(p)
        if not real.startswith(REPO + os.sep) or _denied(os.path.relpath(real, REPO)):
            return True
    return False


def base_files():
    out = subprocess.run(["git", "-C", REPO, "ls-files", "-co", "--exclude-standard", "-z"], capture_output=True, check=True).stdout
    rels = [r for r in out.decode().split("\0") if r]
    return [r for r in rels if not r.startswith("pipeline/full-exo/designs/") and not _denied(r) and os.path.isfile(os.path.join(REPO, r))]


def walk(rel, skip=()):
    p = os.path.join(REPO, rel)
    if os.path.isfile(p):
        return [] if _denied(rel) else [os.path.relpath(p, REPO)]
    out = []
    for d, dirs, fs in os.walk(p):
        dirs[:] = [x for x in dirs if x not in ("preview", "preview_test", ".flash", "__pycache__", ".git") + tuple(skip)]
        for f in fs:
            r = os.path.relpath(os.path.join(d, f), REPO)
            if not _denied(r) and not f.endswith(".tmp"):
                out.append(r)
    return out


_HC = None
def file_sha(rel):
    """sha256 of a file, cached by (size, mtime) in ~/.cache/cloud_run/hash.json"""
    global _HC
    with _lock:
        if _HC is None:
            try:
                _HC = json.load(open(os.path.join(CACHE, "hash.json")))
            except (OSError, ValueError):
                _HC = {}
    p = os.path.join(REPO, rel); st = os.stat(p); k = f"{st.st_size}:{st.st_mtime_ns}"
    c = _HC.get(rel)
    if c and c[0] == k:
        return c[1]
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    with _lock:
        _HC[rel] = [k, h.hexdigest()]
    return h.hexdigest()


def save_hash_cache():
    if _HC is not None:
        json.dump(_HC, open(os.path.join(CACHE, "hash.json"), "w"))


def manifest(job, base):
    rels = list(base) if job.get("base", True) else []
    for d in job.get("design", []):
        rels += walk(os.path.join("pipeline", "full-exo", "designs", d), skip=("parts",))   # parts/*.glb: viewer meshes, no judge reads them
    for p in job.get("include", []):
        rels += walk(p)
    rels = sorted(set(rels))
    return {r: [file_sha(r), os.stat(os.path.join(REPO, r)).st_mode & 0o777] for r in rels}


# ------------------------------------------------------------------ jobs
def submit(eid, job, timeout=7200, poll=2.0):
    """one serverless job -> (output, status dict)"""
    r = _http(f"{RUN}/{eid}/run", {"input": {"job": job}}); jid = r["id"]; t0 = time.time()
    while True:
        s = _http(f"{RUN}/{eid}/status/{jid}")
        st = s.get("status")
        if st in ("COMPLETED", "FAILED", "CANCELLED", "TIMED_OUT"):
            return s.get("output"), s
        if time.time() - t0 > timeout:
            try:
                _http(f"{RUN}/{eid}/cancel/{jid}", {})
            except RuntimeError:
                pass
            return None, dict(status="CLIENT_TIMEOUT", id=jid)
        time.sleep(poll if time.time() - t0 > 20 else 1.0)


def known():
    try:
        return set(json.load(open(os.path.join(CACHE, "known_blobs.json"))))
    except (OSError, ValueError):
        return set()


def save_known(s):
    json.dump(sorted(s), open(os.path.join(CACHE, "known_blobs.json"), "w"))


def upload(eid, need, by_sha, pool):
    """make sure every sha in need is in the farm's CAS (have -> put, parallel, chunked)"""
    kn = known(); todo = sorted(set(need) - kn)
    if not todo:
        return 0
    out, _ = submit(eid, dict(mode="have", shas=todo))
    if not isinstance(out, dict) or "missing" not in out:
        raise RuntimeError(f"have job failed: {str(out)[:500]}")
    missing = out["missing"]; kn |= set(todo) - set(missing)
    if not missing:
        save_known(kn); return 0
    jobs, cur, cur_n, total = [], [], 0, 0
    for sha0 in missing:
        raw = open(os.path.join(REPO, by_sha[sha0]), "rb").read(); sha = hashlib.sha256(raw).hexdigest()
        if sha != sha0:                                  # the file changed since it was hashed (another agent wrote it)
            print(f"upload: {by_sha[sha0]} changed while shipping: sending its current content", flush=True)
            REMAP[sha0] = sha; by_sha[sha] = by_sha[sha0]
        gz = gzip.compress(raw, 6); total += len(gz)
        if len(gz) > CHUNK:
            n = -(-len(gz) // CHUNK)
            jobs += [[dict(sha=sha, i=i, n=n, data=base64.b64encode(gz[i * CHUNK:(i + 1) * CHUNK]).decode())] for i in range(n)]
            continue
        if cur and cur_n + len(gz) > CHUNK:
            jobs.append(cur); cur, cur_n = [], 0
        cur.append(dict(sha=sha, i=0, n=1, data=base64.b64encode(gz).decode())); cur_n += len(gz)
    if cur:
        jobs.append(cur)
    print(f"upload: {len(missing)} new files, {total / 1e6:.1f} MB gzip in {len(jobs)} put jobs", flush=True)
    t0 = time.time(); bad = []
    for (out, st) in pool.map(lambda b: submit(eid, dict(mode="put", blobs=b)), jobs):
        if not isinstance(out, dict):
            bad.append(str(st)[:300]); continue
        kn |= set(out.get("stored", [])); bad += out.get("bad", [])
    save_known(kn)
    left = set(REMAP.get(m, m) for m in missing) - kn
    if bad or left:
        raise RuntimeError(f"upload incomplete: bad {[by_sha.get(b, b) for b in bad[:3]]} not stored {sorted(by_sha.get(x, x) for x in left)[:5]}")
    print(f"upload done in {time.time() - t0:.0f}s", flush=True)
    return total


def fetch(eid, sha):
    parts, i, n = [], 0, 1
    while i < n:
        out, _ = submit(eid, dict(mode="get", sha=sha, i=i)); n = out["n"]; parts.append(base64.b64decode(out["data"])); i += 1
    return gzip.decompress(b"".join(parts))


def cost(st, vcpus=None):
    """(billed s, $ if it shared its worker with 3 others, $ if it had the worker alone incl. idle) for one job"""
    ex = (st.get("executionTime") or 0) / 1000.0
    return ex, ex * RATE["cpu3c-8-16"] / SLOTS, (ex + IDLE_S) * RATE["cpu5c-8-16"]


def batch_cost(outs):
    """bill per worker: union of its jobs' [start, end] spans + idle timeout, at the cpu3c (cpu5c) rate. Cold start not
    included (RunPod bills it too: ~10-60 s per new worker; shown separately as 'delay' in each job's status)."""
    spans = {}
    for o in outs:
        if isinstance(o, dict) and "t0" in o:
            spans.setdefault(o.get("worker", "?"), []).append((o["t0"], o["t1"]))
    secs = 0.0
    for w, iv in spans.items():
        iv.sort(); cur_s, cur_e = iv[0]
        for s_, e_ in iv[1:]:
            if s_ > cur_e:
                secs += cur_e - cur_s; cur_s = s_
            cur_e = max(cur_e, e_)
        secs += cur_e - cur_s + IDLE_S
    return len(spans), secs, secs * RATE["cpu3c-8-16"], secs * RATE["cpu5c-8-16"]


def run_batch(jobs, outdir=None, timeout=3000):
    eid = endpoint_id(); base = base_files() if any(j.get("base", True) for j in jobs) else []
    t0 = time.time()
    with cf.ThreadPoolExecutor(8) as hp:
        mans = list(hp.map(lambda j: manifest(j, base), jobs))
    save_hash_cache()
    by_sha = {}
    for m in mans:
        for r, (s, _) in m.items():
            by_sha.setdefault(s, r)
    load = os.getloadavg()[0]; ncpu = os.cpu_count() or 1
    print(f"farm {EP_NAME} ({eid}): {len(jobs)} job(s), {len(by_sha)} distinct files "
          f"({sum(os.path.getsize(os.path.join(REPO, r)) for r in by_sha.values()) / 1e6:.0f} MB); local load {load:.1f} on {ncpu} cores"
          + ("  [box not saturated: a single short job is likely faster locally]" if load < ncpu and len(jobs) == 1 else ""), flush=True)
    with cf.ThreadPoolExecutor(MAX_INFLIGHT) as pool:
        upload(eid, list(by_sha), by_sha, pool)
        t_up = time.time() - t0

        def one(k):
            j, m = jobs[k], mans[k]; tag = j.get("tag") or f"job{k}"
            m = {r: [REMAP.get(sv, sv), md] for r, (sv, md) in m.items()}
            body = dict(mode="run", tag=tag, cmd=j["cmd"], files=m, out=j.get("out", []), env=j.get("env", {}),
                        shared=j.get("shared", []), timeout=j.get("timeout", timeout))
            for attempt in range(2):
                out, st = submit(eid, body, timeout=float(body["timeout"]) + 900)
                if isinstance(out, dict) and out.get("missing") and attempt == 0:
                    kn = known() - set(out["missing"]); save_known(kn); upload(eid, out["missing"], by_sha, pool); continue
                return tag, j, out, st
            return tag, j, out, st

        res = list(pool.map(one, range(len(jobs))))
    wall = time.time() - t0; tot_lo = tot_hi = tot_ex = 0.0; ok = 0
    for tag, j, out, st in res:
        if not isinstance(out, dict) or "rc" not in out:
            print(f"[{tag}] FAILED: status {st.get('status')} {str(st.get('error') or out)[:1500]}"); continue
        ex, lo, hi = cost(st, out.get("vcpus")); tot_ex += ex; tot_lo += lo; tot_hi += hi
        logp = os.path.join(CACHE, "logs", f"{tag}.log"); os.makedirs(os.path.dirname(logp), exist_ok=True); open(logp, "w").write(out["log"])
        dest = outdir or REPO; wrote = []
        same = [r for r, f in out.get("files", {}).items() if f.get("unchanged")]
        for rel, f in out.get("files", {}).items():
            if f.get("unchanged") or _denied(rel) or rel.startswith("/") or ".." in rel.split("/"):
                continue
            if not any(fnmatch.fnmatch(rel, g) for g in j.get("out", [])):
                continue
            raw = gzip.decompress(base64.b64decode(f["data"])) if "data" in f else fetch(eid, f["sha"])
            if hashlib.sha256(raw).hexdigest() != f["sha"]:
                print(f"[{tag}] sha mismatch on {rel}: not written"); continue
            p = os.path.join(dest, rel); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "wb").write(raw); wrote.append(rel)
        ok += out["rc"] == 0
        print(f"[{tag}] rc {out['rc']}  run {out['secs']:.0f}s (setup {out.get('setup_secs', 0):.0f}s) on {out.get('vcpus')} vCPU {out.get('cpu', '?')[:40]}"
              f"  {ex:.0f}s on the worker = ${lo:.4f} shared / ${hi:.4f} alone  {len(wrote)} file(s) -> {dest if outdir else 'tree'}"
              + (f", {len(same)} rewritten byte-identical to the tree" if same else "") + f"  log {logp}")
        tail = out["log"].strip().splitlines()[-int(os.environ.get("CLOUD_TAIL", 12)):]
        print("    " + "\n    ".join(tail))
    nw, wsec, c3, c5 = batch_cost([o for _, _, o, _ in res])
    print(f"batch: {ok}/{len(jobs)} ok, wall {wall:.0f}s (upload {t_up:.0f}s), job time {tot_ex:.0f}s on {nw} worker(s) "
          f"(parallel speed-up {tot_ex / max(1.0, wall - t_up):.1f}x); billed ~{wsec:.0f} worker-s = ${c3:.4f} (cpu3c) / ${c5:.4f} (cpu5c) "
          f"+ cold starts (~$0.0002-0.01 per new worker)")
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("what", choices=["judge", "run", "batch", "ping"]); ap.add_argument("args", nargs="*")
    ap.add_argument("--design", action="append", default=[]); ap.add_argument("--include", action="append", default=[])
    ap.add_argument("--out", action="append", default=[]); ap.add_argument("--env", action="append", default=[])
    ap.add_argument("--shared", action="append", default=[]); ap.add_argument("--outdir"); ap.add_argument("--tag")
    ap.add_argument("--timeout", type=float, default=3000); ap.add_argument("--bench-cache", action="store_true")
    ap.add_argument("--no-base", action="store_true")
    argv = sys.argv[1:]; cmd = None
    if "--" in argv:
        k = argv.index("--"); cmd = " ".join(argv[k + 1:]); argv = argv[:k]
    a = ap.parse_args(argv)
    env = dict(e.split("=", 1) for e in a.env)
    if any(s in k.upper() for k in env for s in ("KEY", "SECRET", "TOKEN", "PASSWORD")):
        sys.exit("refusing to send secret-like env vars to the farm")
    if a.what == "ping":
        out, st = submit(endpoint_id(), dict(mode="ping"))
        print(json.dumps(out, indent=1)); ex, lo, hi = cost(st, None); print(f"billed ~{ex:.1f}s = ${lo:.5f} (<= ${hi:.5f})"); return
    extra = dict(design=a.design, include=a.include + ([".cache/concept_bench"] if a.bench_cache else []),
                 out=a.out, env=env, shared=a.shared, base=not a.no_base)
    if a.what == "judge":
        d = a.args[0]; fast = "fast" if "fast" in a.args[1:] else ""; dd = f"pipeline/full-exo/designs/{d}"
        job = dict(extra, cmd=f"tools/judge_all.sh {d} {fast}", tag=a.tag or f"judge_{d}", design=[d] + a.design,
                   env=dict({"SKIP_FEA": "1"}, **env), out=a.out + [f"{dd}/judge/*.json", f"{dd}/judge/*.md", f"{dd}/score*.json"])
        run_batch([job], a.outdir, a.timeout)
    elif a.what == "run":
        run_batch([dict(extra, cmd=cmd or " ".join(a.args), tag=a.tag or "run")], a.outdir, a.timeout)
    else:
        jobs = json.load(open(a.args[0]))
        run_batch([dict(extra, **j) for j in jobs], a.outdir, a.timeout)


if __name__ == "__main__":
    main()
