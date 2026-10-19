"""Local test page for the dashboard page: python3 build.py <data dir>  ->  index.html (light) + dark.html beside this file.
The kit's app.css and d3.min.js sit beside it; window.dash is a shim over the dataset JSON files (data, calc, onData,
setLink, params, colors). ?status=loading|error makes every dataset report that status, to see the placeholders."""
import json, os, sys
H = os.path.dirname(os.path.abspath(__file__)); D = os.path.dirname(H)
data_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(D, 'sample_data')
page = open(os.path.join(D, 'index.html')).read()
data = {}
for n in ('morphs', 'sweeps', 'judged', 'events', 'reqs', 'cov3d', 'meta'):
    p = os.path.join(data_dir, n + '.json')
    if os.path.exists(p): data[n] = json.load(open(p))
shim = """<script>
window.__DATA = %s;
(function () {
  const q = new URLSearchParams(location.search), forced = q.get('status'), calcs = {}, cache = {}, subs = [];
  if (q.get('theme') === 'dark') document.documentElement.setAttribute('data-mode', 'dark');
  const D = window.__DATA;
  window.dash = {
    colors: ['#2563eb', '#ea580c', '#16a34a', '#9333ea', '#0891b2', '#ca8a04', '#db2777', '#4b5563'],
    data(id) {
      if (forced) return { status: forced, data: [], columns: [] };
      if (id in D) return { status: 'ok', data: D[id], columns: Object.keys(D[id][0] || {}) };
      if (calcs[id]) {
        if (!cache[id]) {
          const ins = calcs[id].inputs.map((i) => this.data(i)), bad = ins.find((d) => d.status !== 'ok');
          if (bad) return { status: bad.status, data: [] };
          cache[id] = { status: 'ok', data: calcs[id].fn(...ins.map((d) => d.data)) };
        }
        return cache[id];
      }
      return { status: 'missing', data: [] };
    },
    calc(id, spec) { calcs[id] = spec; },
    onData(fn) { subs.push(fn); fn(); },
    setLink(n) { history.replaceState(null, '', '#' + n); window.__link = n; },
    params() { return {}; }, setParams() {}, resetParams() {}, refresh() {}
  };
  let t; let w = innerWidth;
  window.addEventListener('resize', () => { if (innerWidth === w) return; w = innerWidth; clearTimeout(t); t = setTimeout(() => subs.forEach((f) => f()), 60); });
})();
</script>""" % json.dumps(data, separators=(',', ':'))
for name, mode in (('index.html', ''), ('dark.html', ' data-mode="dark"')):
    html = ('<!doctype html><html class="cds-root"%s><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            '<link rel="stylesheet" href="app.css"><script src="d3.min.js"></script>%s'
            '<style>.hx-body{background:var(--color-bg);margin:0;padding:16px;}</style></head>'
            '<body class="hx-body" data-appifact-content><div id="dash-root">%s</div></body></html>') % (mode, shim, page)
    open(os.path.join(H, name), 'w').write(html)
print('harness', os.path.join(H, 'index.html'), 'page', len(page.encode()), 'bytes', {k: len(v) for k, v in data.items()})
