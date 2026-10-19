"""Local harness: run docs/dashboard/ with the Dashboard type's REAL runtime, offline.

    python3 docs/dashboard/harness/serve.py [--port 8765] [--runtime DIR] [--data DIR] [--status ok|loading|error]

It serves, from memory (nothing is copied into the repo):
  /                       the type's own host page (RUNTIME/index.html) with one extra <script> before app.js
  /artifact-type/app.js   RUNTIME/artifact-type/app.js and app.css, read at run time
  /__fake_claude.js       a stand-in for the platform's `window.claude` (db + user only): a Firestore-like store that
                          holds what the lead writes with ArtifactData - dash/meta, datasets/<id> (file sources),
                          files/<name> {text} for index.html and every part file - and keeps what the page writes
                          (data/users/local/runs: the runtime's own report of flagged marks and page errors)
  /_blob/<32 hex>         each dataset file named in docs/dashboard/manifest.json (the url the runtime fetches)
--status loading|error makes every /_blob/ request hang (loading) or fail with 500 (error) to see the page's states.
RUNTIME defaults to $DASH_RUNTIME, else the session scratchpad copy of the type (see docs/DASHBOARD.md)."""
import argparse, hashlib, http.server, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
DASH = os.path.dirname(HERE)
DEF_RT = os.environ.get("DASH_RUNTIME", "/tmp/claude-0/-home-user-exo-shoulder/029f38fb-570e-5d7a-bebc-fc64e6215529/scratchpad/artifact-files/4bc63ae4-822a-498a-8d40-e325912a4e61")
TITLE = "Shoulder exo: progress by benchmark"

FAKE = r"""
(function () {
  const STORE = %s;
  const docs = new Map(Object.entries(STORE));
  window.__store = docs;
  const listeners = new Set();
  const kids = (name) => [...docs].filter(([p]) => p.startsWith(name + '/') && !p.slice(name.length + 1).includes('/'));
  const snap = (name, changes) => ({ docChanges: () => changes, metadata: { fromCache: false, hasPendingWrites: false } });
  function collection(name) {
    const q = {
      limit() { return q; }, where() { return q; }, orderBy() { return q; },
      onSnapshot(cb, err) {
        const l = { name, cb };
        listeners.add(l);
        setTimeout(() => cb(snap(name, kids(name).map(([p, d]) => ({ type: 'added', doc: { id: p.slice(name.length + 1), data: () => JSON.parse(JSON.stringify(d)) } })))), 0);
        return () => listeners.delete(l);
      },
      async get() { return { docs: kids(name).map(([p, d]) => ({ id: p.slice(name.length + 1), data: () => d })) }; }
    };
    return q;
  }
  function changed(path, type) {
    const i = path.lastIndexOf('/'), name = path.slice(0, i), id = path.slice(i + 1);
    listeners.forEach((l) => { if (l.name === name) l.cb(snap(name, [{ type, doc: { id, data: () => JSON.parse(JSON.stringify(docs.get(path) || {})) } }])); });
  }
  function doc(path) {
    return {
      async get() { const d = docs.get(path); return { exists: d !== undefined, id: path.split('/').pop(), data: () => d, metadata: { fromCache: false } }; },
      async set(d) { const had = docs.has(path); docs.set(path, JSON.parse(JSON.stringify(d))); changed(path, had ? 'modified' : 'added'); },
      async update(d) { const o = Object.assign({}, docs.get(path) || {}); for (const [k, v] of Object.entries(d)) { if (v === null) delete o[k]; else o[k] = v; } docs.set(path, o); changed(path, 'modified'); },
      async delete() { docs.delete(path); changed(path, 'removed'); },
      onSnapshot(cb) { setTimeout(() => cb({ exists: docs.has(path), data: () => docs.get(path), metadata: {} }), 0); return () => {}; }
    };
  }
  window.claude = {
    db: { collection, doc },
    user: { id: async () => 'local', name: async () => 'Local harness', canEdit: async () => true, can: async () => true }
  };
})();
"""


def build(rt, data_dir, files):
    man = json.load(open(os.path.join(DASH, "manifest.json")))
    store, blobs = {"dash/meta": {"title": TITLE}}, {}
    for d in man:
        p = os.path.join(data_dir, os.path.basename(d["file"]))
        raw = open(p, "rb").read()
        h = hashlib.sha256(raw).hexdigest()[:32]
        blobs[h] = raw
        store["datasets/" + d["id"]] = {"title": d["title"], "description": d["description"],
                                        "source": {"kind": "file", "url": "/_blob/" + h, "name": d["id"] + ".json"},
                                        "updated": {"at": d.get("updated") or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "by": "dash_build.py"}}
    for f in files:
        store["files/" + f] = {"text": open(os.path.join(DASH, f)).read()}
    host = open(os.path.join(rt, "index.html")).read()
    host = host.replace('<script src="artifact-type/app.js"></script>', '<script src="/__fake_claude.js"></script>\n<script src="artifact-type/app.js"></script>')
    return host, FAKE % json.dumps(store), blobs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--runtime", default=DEF_RT)
    ap.add_argument("--data", default=os.path.join(DASH, "data"))
    ap.add_argument("--status", default="ok")
    a = ap.parse_args()
    files = ["index.html"] + sorted(f for f in os.listdir(DASH) if f.endswith((".js", ".css")))
    for f in files:
        n = os.path.getsize(os.path.join(DASH, f))
        if n > 262144: sys.exit(f"{f} is {n} bytes: over the store's 256 KB per file")

    class H(http.server.BaseHTTPRequestHandler):
        def log_message(self, *x): pass

        def send(self, body, ctype, code=200):
            self.send_response(code); self.send_header("Content-Type", ctype); self.send_header("Cache-Control", "no-store")
            self.end_headers(); self.wfile.write(body if isinstance(body, bytes) else body.encode())

        def do_GET(self):
            host, fake, blobs = build(a.runtime, a.data, files)    # rebuilt per request: edits show on reload
            p = self.path.split("?")[0].split("#")[0]
            if p in ("/", "/index.html"): return self.send(host, "text/html; charset=utf-8")
            if p == "/__fake_claude.js": return self.send(fake, "text/javascript")
            if p.startswith("/artifact-type/"):
                f = os.path.join(a.runtime, "artifact-type", os.path.basename(p))
                if os.path.exists(f): return self.send(open(f, "rb").read(), "text/javascript" if f.endswith(".js") else "text/css")
            if p.startswith("/_blob/") and p[7:] in blobs:
                if a.status == "loading": time.sleep(60)
                if a.status == "error": return self.send("{}", "application/json", 500)
                return self.send(blobs[p[7:]], "application/json")
            self.send("not found", "text/plain", 404)

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", a.port), H)
    print(f"harness on http://127.0.0.1:{a.port}/  runtime {a.runtime}  files {files}", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
