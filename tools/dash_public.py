#!/usr/bin/env python3
"""Build the PUBLIC mirror of the production dashboard: a plain, self-contained page anyone with the link can open.

The production dashboard (https://claude.ai/artifact/AMhjuE83FBhGXxu8vQBN7r) is an Artifact made from the Dashboard
type: its page and data live in the artifact's own store, which a viewer who is not signed in to claude.ai may not be
able to read (user report 2026-10-16: "the artifact isn't loading online even though I selected anyone can view it").
This mirror runs the SAME page (docs/dashboard/simple/index.html) on a small stand-in for the type's `dash` API
(dash.data / dash.calc / dash.onData / dash.colors), with the type's theme tokens written out, d3 from cdnjs and the
same dataset files fetched from beside the page - no store, no capabilities, no sign-in.

    python3 tools/dash_public.py [STATE.json]   # writes docs/dashboard/public/index.html; prints what changed
Then publish docs/dashboard/public/index.html with files {"data/<id>.json": "docs/dashboard/data/<id>.json"} - the
same dataset files tools/dash_build.py writes for the production page, so both show the same numbers (only the changed
ones on a refresh: STATE.json holds the sha256 of each file as last published; this script lists the ones that differ
and, with --mark, records the current shas after a publish).
"""
import hashlib, json, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "docs/dashboard/simple/index.html")
DATA = os.path.join(REPO, "docs/dashboard/data")
OUT = os.path.join(REPO, "docs/dashboard/public")
DATASETS = ["morphs", "sweeps", "events", "reqs", "cad", "motion"]   # every dataset the page reads

# The Dashboard type's theme tokens as its runtime computes them (read from the type's own app.css in the local
# harness, 2026-10-16), light then dark. Relative colors (hsl(from ...)) are written as rgb with alpha.
LIGHT = {
    "--color-fg": "#0b0b0b", "--color-fg-muted": "#898781", "--color-bg": "#f9f9f7", "--color-panel": "#fff",
    "--color-border-line": "rgb(11 11 11 / 10%)", "--color-ok": "#006300", "--color-warn": "#734500", "--color-bad": "#8e2626",
    "--cds-chart-muted": "#c3c2b7", "--cds-chart-status-critical": "#d03b3b", "--cds-chart-reference": "#898781",
    "--cds-surface-popover": "#fff", "--cds-shadow-popover": "0 8px 24px #0000001f, 0 2px 6px #00000014",
    "--cds-border": "rgb(11 11 11 / 10%)",
    "--cat-1": "rgb(42 120 214)", "--cat-2": "rgb(235 104 52)", "--cat-3": "rgb(27 175 122)", "--cat-4": "rgb(237 161 0)",
    "--cat-5": "rgb(232 123 164)", "--cat-6": "rgb(0 131 0)", "--cat-7": "rgb(98 80 214)", "--cat-8": "rgb(227 73 72)",
}
DARK = {
    "--color-fg": "#f0efec", "--color-fg-muted": "#898781", "--color-bg": "#0b0b0b", "--color-panel": "#1a1a19",
    "--color-border-line": "rgb(255 255 255 / 10%)", "--color-ok": "#0ca30c", "--color-warn": "#db9300", "--color-bad": "#ec7e7e",
    "--cds-chart-muted": "#5f5e5a", "--cds-chart-status-critical": "#d03b3b", "--cds-chart-reference": "#97958d",
    "--cds-surface-popover": "#20201f", "--cds-shadow-popover": "0 8px 24px #00000052, 0 2px 6px #0003",
    "--cds-border": "rgb(255 255 255 / 10%)",
    "--cat-1": "rgb(57 135 229)", "--cat-2": "rgb(217 89 38)", "--cat-3": "rgb(25 158 112)", "--cat-4": "rgb(201 133 0)",
    "--cat-5": "rgb(213 81 129)", "--cat-6": "rgb(0 131 0)", "--cat-7": "rgb(144 133 233)", "--cat-8": "rgb(230 103 103)",
}
FIXED = {   # theme-independent tokens
    "--cds-radius": ".5rem", "--cds-pad-lg": "1rem", "--cds-gap-md": "1rem", "--cds-gap-xl": "2.5rem",
    "--cds-font-weight-medium": "500", "--cds-font-size-caption": ".75rem", "--cds-font-size-title": "1.375rem",
    "--cds-font-size-heading": ".9375rem",
    "--font-anthropic-sans": 'ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif',
    "--font-anthropic-serif": 'ui-serif, Georgia, "Times New Roman", serif',
}

HEAD = """<title>Shoulder Exo Progress</title>
<meta name="claude:viewport-fit-sides" content="cover">
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
<style>
/* Public mirror of the shoulder-exo dashboard: the production page on the Dashboard type's tokens, no store. */
:root { %(light)s %(fixed)s }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { %(dark)s color-scheme: dark; } }
:root[data-theme="dark"] { %(dark)s color-scheme: dark; }
body { background: var(--color-bg); color: var(--color-fg); font-family: var(--font-anthropic-sans); font-size: 14px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 24px 40px; }
#dash-root { min-width: 0; }
.pub-note { max-width: 1100px; margin: 0 auto 16px; font-size: .75rem; color: var(--color-fg-muted); }
.pub-err { max-width: 1100px; margin: 0 auto 16px; font-size: .8125rem; color: var(--color-bad); }
</style>
"""

SHIM = r"""<script>
/* A small stand-in for the Dashboard type's `dash` API: the same datasets, fetched from the files beside this page. */
window.dash = (() => {
  const IDS = %(ids)s, state = {}, calcs = [], cbs = [];
  IDS.forEach((id) => { state[id] = { status: 'loading', data: [] }; });
  const colors = [1, 2, 3, 4, 5, 6, 7, 8].map((i) => `var(--cat-${i})`);
  const data = (id) => state[id] || { status: 'missing', data: [] };
  const calc = (id, spec) => { calcs.push([id, spec]); state[id] = { status: 'loading', data: [] }; };
  const recompute = () => {
    for (const [id, s] of calcs) {
      const ins = s.inputs.map((i) => data(i));
      if (ins.every((x) => x.status === 'ok')) {
        try { state[id] = { status: 'ok', data: s.fn(...ins.map((x) => x.data)) }; }
        catch (e) { state[id] = { status: 'error', data: [], message: String(e) }; console.error(e); }
      } else if (ins.some((x) => x.status === 'error')) state[id] = { status: 'error', data: [] };
    }
  };
  const run = (f) => { try { f(); } catch (e) { console.error(e); } };
  let queued = 0;
  const fire = () => { if (queued) return; queued = requestAnimationFrame(() => { queued = 0; recompute(); cbs.forEach(run); }); };
  const onData = (f) => { cbs.push(f); recompute(); run(f); };
  const failed = [];
  IDS.forEach((id) => {
    fetch(`data/${id}.json`).then((r) => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
      .then((j) => { state[id] = { status: 'ok', data: Array.isArray(j) ? j : (j.rows || j.data || j.results || []) }; fire(); })
      .catch((e) => {
        state[id] = { status: 'error', data: [], message: String(e) }; failed.push(id); fire();
        const n = document.getElementById('pub-err'); if (n) { n.hidden = false; n.textContent = `Could not load: ${failed.join(', ')}. Reload the page to try again.`; }
      });
  });
  let w = 0;
  if ('ResizeObserver' in window) new ResizeObserver((es) => { const nw = Math.round(es[0].contentRect.width); if (nw !== w) { w = nw; fire(); } }).observe(document.documentElement);
  return { data, calc, onData, colors, refresh: () => {}, params: () => ({}), setParams: () => {}, resetParams: () => {}, setLink: () => {} };
})();
</script>
"""


def css(d):
    return " ".join(f"{k}: {v};" for k, v in d.items())


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    state_path = args[0] if args else None
    state = json.load(open(state_path)) if state_path and os.path.exists(state_path) else {}
    page = open(SRC).read()
    os.makedirs(OUT, exist_ok=True)
    html = (HEAD % {"light": css(LIGHT), "fixed": css(FIXED), "dark": css(DARK)}
            + '<p class="pub-note">Public copy of the shoulder-exo dashboard, refreshed about every 15 minutes.</p>\n'
            + '<p class="pub-err" id="pub-err" hidden></p>\n'
            + SHIM % {"ids": json.dumps(DATASETS)}
            + '<div id="dash-root">\n' + page + "\n</div>\n")
    out = os.path.join(OUT, "index.html")
    if not os.path.exists(out) or open(out).read() != html:
        open(out, "w").write(html)
    now = {"index.html": sha(out), **{f"data/{i}.json": sha(os.path.join(DATA, f"{i}.json")) for i in DATASETS}}
    changed = [k for k, v in now.items() if state.get(k) != v]
    files = {k: os.path.relpath(os.path.join(DATA, os.path.basename(k)), REPO) for k in changed if k.startswith("data/")}
    if "--mark" in sys.argv and state_path:
        json.dump(now, open(state_path, "w"), indent=1)
    print(json.dumps({"changed": changed, "files": files}))


if __name__ == "__main__":
    sys.exit(main())
