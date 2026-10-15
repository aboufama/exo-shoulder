"""CPU farm job runner (RunPod serverless CPU, endpoint exo-cpu1; client tools/cloud_run.py, docs/CLOUD_RUN.md).

Files travel content-addressed: every input file is a blob named by its sha256 in a CAS on the endpoint's network volume
(/runpod-volume/exo-farm/cas), uploaded once by "put" jobs (gzip, chunked to stay under RunPod's 10 MB /run payload)
and reused by every later job and worker. A "run" job names its tree as {relpath: [sha, mode]}; the worker copies the
blobs into a fresh work dir (copies, never links: a job may rewrite its inputs), runs one bash command there with this
worker's python first on PATH, and returns the files matching the job's output globs that it created or changed.

Modes (job dict -> result dict):
  ping                                  -> python / cpu / volume facts
  have  {shas}                          -> {missing}
  put   {blobs: [{sha, i, n, data}]}    -> {stored, pending, bad}   data = base64 of chunk i of n of gzip(file)
  run   {files, cmd, out, env, timeout, link} -> {rc, log, secs, files: {rel: {sha, size, data | in_cas}}} | {missing}
        link: path prefixes (e.g. ".cache/concept_bench/") whose files are READ-ONLY inputs: symlinked to a per-worker local
        copy of the blob (copied from the CAS once per worker, then shared by every job on it) instead of copied per job
  get   {sha, i, chunk}                 -> {i, n, data}             chunk i of gzip(blob) (outputs too big to inline)
Never handles keys: the job env is whatever the client sends (the client refuses key-like names), and the RunPod
environment's own secrets are stripped from the command's environment.
"""
import base64, glob, gzip, hashlib, os, shutil, subprocess, sys, tempfile, time, uuid

VERSION = "farm-3 2026-10-15"
ROOT = "/runpod-volume/exo-farm" if os.path.isdir("/runpod-volume") else os.path.join(tempfile.gettempdir(), "exo-farm")
CAS = os.path.join(ROOT, "cas"); PARTS = os.path.join(ROOT, "parts"); SHARED = os.path.join(ROOT, "shared")
INLINE_MAX = 6 * 1024 * 1024          # bytes of gzip returned inline per job; bigger outputs stay in the CAS for "get"
CHUNK = 6 * 1024 * 1024


def _blob(sha):
    return os.path.join(CAS, sha[:2], sha)


LOCAL = "/tmp/farm-blobs"                                      # worker-local disk: read-only blobs used by `link` files


def _local_blob(sha):
    """path of a worker-local copy of blob sha (copied from the network volume once, atomic)"""
    p = os.path.join(LOCAL, sha)
    if not os.path.exists(p):
        os.makedirs(LOCAL, exist_ok=True); tmp = p + "." + uuid.uuid4().hex[:8]
        shutil.copyfile(_blob(sha), tmp); os.chmod(tmp, 0o444); os.replace(tmp, p)
    return p


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _store(sha, raw):
    """write raw bytes as blob sha (verified, atomic)"""
    if hashlib.sha256(raw).hexdigest() != sha:
        return False
    p = _blob(sha); os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + "." + uuid.uuid4().hex[:8]
    with open(tmp, "wb") as f:
        f.write(raw)
    os.replace(tmp, p); return True


def _vcpus():
    try:                                                       # cgroup v2 quota (what the instance type gives us)
        q, per = open("/sys/fs/cgroup/cpu.max").read().split()[:2]
        if q != "max":
            return round(int(q) / int(per), 2)
    except (OSError, ValueError):
        pass
    try:
        return len(os.sched_getaffinity(0))
    except AttributeError:
        return os.cpu_count()


def _cpu_model():
    try:
        for ln in open("/proc/cpuinfo"):
            if ln.startswith("model name"):
                return ln.split(":", 1)[1].strip()
    except OSError:
        pass
    return "?"


def facts():
    import platform
    v = {}
    for m in ("numpy", "scipy", "trimesh", "igl", "mujoco", "networkx", "rtree"):
        try:
            mod = __import__(m); v[m] = getattr(mod, "__version__", "?")
        except Exception as e:                                 # noqa: BLE001
            v[m] = "missing: " + type(e).__name__
    n = sum(len(fs) for _, _, fs in os.walk(CAS)) if os.path.isdir(CAS) else 0
    return dict(version=VERSION, python=platform.python_version(), exe=sys.executable, vcpus=_vcpus(), os_cpus=os.cpu_count(),
                cpu=_cpu_model(), volume=os.path.isdir("/runpod-volume"), cas_blobs=n, packages=v,
                dc=os.environ.get("RUNPOD_DC_ID", "?"), mem_gb=round(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 2 ** 30, 1))


def put(blobs):
    stored, pending, bad = [], [], []
    for b in blobs:
        sha, i, n = b["sha"], int(b.get("i", 0)), int(b.get("n", 1))
        if os.path.exists(_blob(sha)):
            stored.append(sha); continue
        data = base64.b64decode(b["data"])
        if n == 1:
            try:
                (stored if _store(sha, gzip.decompress(data)) else bad).append(sha)
            except OSError:
                bad.append(sha)
            continue
        d = os.path.join(PARTS, sha); os.makedirs(d, exist_ok=True)
        tmp = os.path.join(d, f"{i}.{uuid.uuid4().hex[:8]}")
        with open(tmp, "wb") as f:
            f.write(data)
        os.replace(tmp, os.path.join(d, str(i)))
        have = [os.path.exists(os.path.join(d, str(k))) for k in range(n)]
        if all(have):
            try:
                gz = b"".join(open(os.path.join(d, str(k)), "rb").read() for k in range(n))
                ok = _store(sha, gzip.decompress(gz))
            except (OSError, EOFError):
                ok = False
            if ok:
                stored.append(sha); shutil.rmtree(d, ignore_errors=True)
            elif not os.path.exists(_blob(sha)):
                bad.append(sha); shutil.rmtree(d, ignore_errors=True)
            else:
                stored.append(sha)                             # another worker assembled it first
        else:
            pending.append(f"{sha}:{sum(have)}/{n}")
    return dict(stored=stored, pending=pending, bad=bad)


def _clean_env(extra):
    env = {k: v for k, v in os.environ.items() if not any(s in k.upper() for s in ("KEY", "SECRET", "TOKEN", "PASSWORD", "AUTH"))}
    env.update({k: str(v) for k, v in (extra or {}).items()})
    return env


def run(job):
    files = job["files"]; t0 = time.time()
    missing = sorted({v[0] for v in files.values() if not os.path.exists(_blob(v[0]))})
    if missing:
        return dict(missing=missing)
    base = "/tmp/farm" if os.path.isdir("/tmp") else tempfile.gettempdir()
    wd = os.path.join(base, job.get("tag", "job") + "-" + uuid.uuid4().hex[:8]); os.makedirs(wd)
    try:
        link = tuple(job.get("link", []))
        for rel, (sha, mode) in files.items():
            if rel.startswith("/") or ".." in rel.split("/"):
                continue
            p = os.path.join(wd, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
            if link and rel.startswith(link):
                os.symlink(_local_blob(sha), p); continue
            shutil.copyfile(_blob(sha), p); os.chmod(p, int(mode))
        for rel in job.get("shared", []):                      # persistent writable dirs on the volume (e.g. .cache/concept_bench)
            if rel.startswith("/") or ".." in rel.split("/"):
                continue
            src = os.path.join(SHARED, rel); os.makedirs(src, exist_ok=True); dst = os.path.join(wd, rel)
            if os.path.isdir(dst):                             # files shipped into it: move them into the shared dir first
                for f in os.listdir(dst):
                    if not os.path.exists(os.path.join(src, f)):
                        shutil.move(os.path.join(dst, f), os.path.join(src, f))
                shutil.rmtree(dst)
            os.makedirs(os.path.dirname(dst), exist_ok=True); os.symlink(src, dst)
        bindir = os.path.join(wd, ".farm_bin"); os.makedirs(bindir)
        for n in ("python3", "python"):
            os.symlink(sys.executable, os.path.join(bindir, n))
        env = _clean_env(job.get("env"))
        env["PATH"] = bindir + ":" + env.get("PATH", "/usr/bin:/bin")
        env["PYTHONPATH"] = ":".join(p for p in sys.path if p and os.path.isdir(p))       # where flash installed the deps
        env.setdefault("OMP_NUM_THREADS", "1"); env["FARM_VCPUS"] = str(_vcpus()); env["HOME"] = wd
        before = {rel: v[0] for rel, v in files.items()}
        t1 = time.time()
        try:
            pr = subprocess.run(["bash", "-c", job["cmd"]], cwd=wd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                timeout=float(job.get("timeout", 3000)), start_new_session=True)
            rc, log = pr.returncode, pr.stdout.decode(errors="replace")
        except subprocess.TimeoutExpired as e:
            rc, log = -9, (e.stdout or b"").decode(errors="replace") + "\n[farm] TIMEOUT"
        t2 = time.time(); secs = t2 - t1
        out, inline = {}, 0
        for pat in job.get("out", []):
            for p in sorted(glob.glob(os.path.join(wd, pat), recursive=True)):
                if not os.path.isfile(p):
                    continue
                rel = os.path.relpath(p, wd)
                if rel in out or rel.startswith(".farm_bin") or os.path.islink(p):
                    continue
                sha = _sha(p)
                if before.get(rel) == sha:
                    out[rel] = dict(sha=sha, unchanged=True); continue      # rewritten byte-identical to the input
                raw = open(p, "rb").read(); gz = gzip.compress(raw, 6)
                if inline + len(gz) <= INLINE_MAX:
                    out[rel] = dict(sha=sha, size=len(raw), data=base64.b64encode(gz).decode()); inline += len(gz)
                else:
                    _store(sha, raw); out[rel] = dict(sha=sha, size=len(raw), in_cas=True)
        return dict(rc=rc, log=log[-200000:], secs=round(secs, 2), setup_secs=round(t1 - t0, 2), files=out, vcpus=_vcpus(),
                    cpu=_cpu_model(), version=VERSION, worker=os.environ.get("RUNPOD_POD_ID", "?"), t0=t0, t1=time.time())
    finally:
        shutil.rmtree(wd, ignore_errors=True)


def get(sha, i=0, chunk=CHUNK):
    p = _blob(sha)
    if not os.path.exists(p):
        return dict(missing=[sha])
    gz = gzip.compress(open(p, "rb").read(), 6); n = max(1, -(-len(gz) // chunk))
    return dict(i=i, n=n, data=base64.b64encode(gz[i * chunk:(i + 1) * chunk]).decode())


def handle(job):
    m = job.get("mode", "run")
    if m == "ping":
        return facts()
    if m == "have":
        return dict(missing=[s for s in job["shas"] if not os.path.exists(_blob(s))])
    if m == "put":
        return put(job["blobs"])
    if m == "run":
        return run(job)
    if m == "get":
        return get(job["sha"], int(job.get("i", 0)))
    return dict(error=f"unknown mode {m!r}")
