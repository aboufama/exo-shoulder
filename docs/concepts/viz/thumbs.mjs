// thumbs.mjs - tiny monochrome motion previews of every concept for the dashboard leaderboard
// (docs/DASHBOARD.md, "Motion previews"). Node only, no browser.
//
//   node docs/concepts/viz/thumbs.mjs [--out docs/dashboard/data/motion.json] [--n 56] [--sheet file.svg] [--stats] [id ...]
//   (tools/dash_build.py runs it when kin.js, this file or a concepts/*.js is newer than motion.json, or a concept
//    module has no row)
//
// Each concept runs as the gallery runs it (viewer.js: KIN.run over KIN.motion(240), the numeric IK warm-started from
// frame to frame), over two laps so the warm start carries across the loop's wrap (an IK branch that drifts during
// lap 1 would otherwise jump back at every repeat); lap 2 is drawn. The loop (rest -> forward raise -> overhead ->
// abduction -> across -> behind -> rest) is sampled at --n frames spaced by equal ARM TRAVEL, not equal time
// (KIN.motion holds at each key pose and moves fast in between: equal-time frames jump up to half the thumbnail in one
// tick): every key pose is shown twice (one short hold) and the frames between two keys are spread evenly over the
// distance the upper arm (its end 200 mm down and four points around it) moves; a frame that falls between two loop
// frames is solved there, warm-started from the loop frame before it. ONE fixed orthographic camera, shared by every
// concept (same direction, centre and scale, so designs compare), projects into a 0..100 viewBox, quantised to
// integers and written as compact SVG path strings, one per frame, frames separated by '|' ('=' stands for a frame
// identical to the one before it: the key-pose holds cost nothing):
//   mech   links, arcs, rails, straps / rings (the cuff), plate and carriage outlines: single strokes. Construction
//          geometry (a part named "construction line", "not metal" or "trace", or a link / arc / rail thinner than
//          1.5 mm) is not metal and is not drawn.
//   joint  hubs as short bars along their axis (a dot when the axis faces the camera), slider blocks, telescope splits
//   body   the shoulder only (one shared row, id "_shoulder"): deltoid circle, the upper arm clipped 200 mm down the
//          arm, the shoulder line toward the neck (moves with ctx.lift)
// Output: an array of row objects, all with the same columns {id, kind, n, still, view, closes, body, mech, joint,
// note}, sorted by id (deterministic: unchanged sources -> unchanged bytes). `still` is the frame a reduced-motion
// reader sees (on the way up to overhead); `closes` has one character per frame, 1 = the chain closes. A concept whose
// module or run throws gets a row of kind "skipped" with the reason in `note` (no drawing), so a reader sees which
// modules have no preview and tools/dash_build.py does not re-run for an unchanged broken module. The file's mtime is
// set to the newest source it read, so a source written during a run is newer and triggers the next build.
import { createRequire } from 'module';
import fs from 'fs';
import path from 'path';
import url from 'url';
import vm from 'vm';

const HERE = path.dirname(url.fileURLToPath(import.meta.url));
const REPO = path.resolve(HERE, '..', '..', '..');
const require = createRequire(import.meta.url);
export const KIN = require(path.join(HERE, 'kin.js'));
const V = KIN.V;

// ---------------------------------------------------------------- the one camera (orthographic)
// From the front-right (45 deg between anterior x and lateral z) and 12 deg above (y up): the overhead arm points up
// the thumbnail (77 % of its length on screen; the earlier 30 deg-high camera showed 48 %: overhead read as a ring over
// a circle), and forward raise and abduction show 72 % each. `pan` moves the frame (mm on the screen: right, down) off
// GH, `half` is its half-width in mm: fitted on 2026-10-15 so every leaderboard design's drawing stays inside the frame
// in every sampled pose (thumbs.mjs --stats prints what falls out; designs with a cuff stage far down the arm set it).
export const CAM = { dir: [1, 0.3, 1], pan: [25, 12], half: 215, view: 100 };
export function camera(spec = CAM) {
  const Zc = V.unit(spec.dir), Xc = V.unit(V.cross([0, 1, 0], Zc)), Yc = V.cross(Zc, Xc), S = spec.view / (2 * spec.half);
  const proj = (p) => [spec.view / 2 + (V.dot(p, Xc) - spec.pan[0]) * S, spec.view / 2 + (-V.dot(p, Yc) - spec.pan[1]) * S];
  return { ...spec, Xc, Yc, Zc, S, proj };
}

// ---------------------------------------------------------------- compact path writer
const q = (x) => Math.round(x);
function nums(a) {                        // numbers joined with the fewest separators ("3-4 5" not "3,-4,5")
  let s = '';
  for (const v of a) { const t = String(v); s += (s && t[0] !== '-' ? ' ' : '') + t; }
  return s;
}
// Ramer-Douglas-Peucker on projected points (screen units)
function rdp(pts, eps) {
  if (pts.length < 3) return pts;
  const [a, b] = [pts[0], pts[pts.length - 1]];
  const dx = b[0] - a[0], dy = b[1] - a[1], L = Math.hypot(dx, dy);
  let k = -1, dm = 0;
  for (let i = 1; i < pts.length - 1; i++) {
    const p = pts[i], d = L < 1e-9 ? Math.hypot(p[0] - a[0], p[1] - a[1]) : Math.abs(dy * p[0] - dx * p[1] + b[0] * a[1] - b[1] * a[0]) / L;
    if (d > dm) { dm = d; k = i; }
  }
  if (dm <= eps) return [a, b];
  return rdp(pts.slice(0, k + 1), eps).slice(0, -1).concat(rdp(pts.slice(k), eps));
}
let dropped = 0;                          // parts whose points are not finite (a concept's own NaN: the gallery hides them too)
/** polyline (screen pts) -> "M x y l dx dy ..." on the integer grid; closed adds z */
function poly(pts, closed) {
  if (pts.some((p) => !Number.isFinite(p[0]) || !Number.isFinite(p[1]))) { dropped++; return ''; }
  let P = rdp(pts, 0.45).map(([x, y]) => [q(x), q(y)]);
  P = P.filter((p, i) => i === 0 || p[0] !== P[i - 1][0] || p[1] !== P[i - 1][1]);
  if (closed && P.length > 1 && P[0][0] === P[P.length - 1][0] && P[0][1] === P[P.length - 1][1]) P.pop();
  if (!P.length) return '';
  const s = 'M' + nums(P[0]);
  if (P.length === 1) return s + 'l0 0';
  const d = [];
  for (let i = 1; i < P.length; i++) d.push(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]);
  return s + 'l' + nums(d) + (closed ? 'z' : '');
}

// ---------------------------------------------------------------- 3-D line geometry of the parts (camera-free)
// circle of radius r about unit axis k at c (a0..a1 deg from ref, full when absent)
function circle3(c, axis, ref, r, a0, a1) {
  const k = V.unit(axis), e = V.unit(V.reject(ref && V.norm(V.reject(ref, k)) > 1e-6 ? ref : V.perp(k), k)), f = V.cross(k, e);
  const full = a0 == null || a1 == null, A0 = full ? 0 : a0, A1 = full ? 360 : a1, n = Math.max(4, Math.ceil(Math.abs(A1 - A0) / 20));
  const pts = [];
  for (let i = 0; i <= (full ? n - 1 : n); i++) {
    const a = (A0 + (A1 - A0) * i / n) * KIN.D2R;
    pts.push(V.add(c, V.add(V.scale(e, r * Math.cos(a)), V.scale(f, r * Math.sin(a)))));
  }
  return { pts, closed: full };
}
const arc3 = (d) => d.pts || KIN.greatArc(d.u, d.v, d.r0, d.r1, Math.max(3, Math.ceil(V.angle(d.u, d.v) / 8))).map((p) => V.add(p, d.c || [0, 0, 0]));
function rail3(d) {
  const k = V.unit(d.axis), e = V.unit(V.reject(d.ref, k)), f = V.cross(k, e), n = Math.max(3, Math.ceil(Math.abs(d.a1 - d.a0) / 8)), o = [];
  for (let i = 0; i <= n; i++) { const a = (d.a0 + (d.a1 - d.a0) * i / n) * KIN.D2R; o.push(V.add(d.c, V.add(V.scale(e, d.rho * Math.cos(a)), V.scale(f, d.rho * Math.sin(a))))); }
  return o;
}
/** basis of a box: z normal, x in-plane reference (viewer.js basisZX) */
function basisZX(z, x) { const ez = V.unit(z), ex = V.unit(V.norm(V.reject(x, ez)) > 1e-6 ? V.reject(x, ez) : V.perp(ez)); return [ex, V.cross(ez, ex), ez]; }
const rect3 = (c, ex, ey, sx, sy) => [[-1, -1], [1, -1], [1, 1], [-1, 1]].map(([i, j]) => V.add(c, V.add(V.scale(ex, i * sx / 2), V.scale(ey, j * sy / 2))));

const BIG_HUB = 18;               // mm: a hub this wide is a sleeve around the arm: drawn as its ring, not a dot
const THIN = 0.75;                // mm: a link / arc / rail thinner than this (radius) is a drawn guide, not a part
/** construction geometry the gallery draws as hairlines (axis lines, coupler traces): not metal, not in the preview */
export const isConstruction = (d) => /construction|not metal|\btrace\b/i.test(d.name || '') || (['link', 'arc', 'rail'].includes(d.kind) && d.r != null && d.r < THIN);
/** one frame's parts -> 3-D polylines {pts, closed}: mech (strokes) and joint (bars / dots) */
export function partLines(parts) {
  const mech = [], joint = [], L = (pts, closed = false) => ({ pts, closed });
  for (const d of parts) {
    if (isConstruction(d)) continue;
    switch (d.kind) {
      case 'link': mech.push(L([d.a, d.b])); break;
      case 'arc': mech.push(L(arc3(d))); break;
      case 'rail': mech.push(L(rail3(d))); break;
      case 'strap': case 'ring': mech.push(circle3(d.c, d.axis, d.ref, d.r, d.kind === 'strap' ? d.a0 : null, d.kind === 'strap' ? d.a1 : null)); break;
      case 'plate': case 'carriage': { const [ex, ey] = basisZX(d.z, d.x), s = d.size || [20, 16]; mech.push(L(rect3(d.c, ex, ey, s[0], s[1]), true)); break; }
      case 'hub': {
        const ax = V.unit(d.axis), h = d.h || 12, r = d.r || 10;
        if (r > BIG_HUB) mech.push(circle3(V.madd(d.c, ax, h / 2), ax, null, r));
        else joint.push(L([d.c, V.madd(d.c, ax, h)]));
        break;
      }
      case 'slider': mech.push(L([d.a, d.b])); joint.push(L([d.at])); break;
      case 'telescope': { mech.push(L([d.a, d.b])); joint.push(L([V.madd(d.a, V.unit(V.sub(d.b, d.a)), d.split)])); break; }
      default: break;                // point: markers (the GH centre), not metal
    }
  }
  return { mech, joint };
}
const linesPath = (lines, cam) => lines.map((l) => poly(l.pts.map(cam.proj), l.closed)).join('');
/** frames -> one string: '|' between frames, '=' for a frame identical to the one before (unpack reverses it) */
export const pack = (frames) => frames.map((d, k) => (k > 0 && d === frames[k - 1] ? '=' : d)).join('|');
export const unpack = (s) => { const o = []; String(s).split('|').forEach((d, k) => o.push(d === '=' && k > 0 ? o[k - 1] : d)); return o; };

// ---------------------------------------------------------------- the shoulder (shared by every concept)
export const ARM = { s0: 8, s1: 200, r0: 41, r1: 34, delt: 45 };
// trunk-fixed points of the shoulder line: lateral trapezius edge -> neck base -> up the side of the neck
const TRAP = [[-8, 46, -48], [-4, 70, -108], [2, 128, -124]];
/** the shoulder in 3-D: deltoid centre + radius (drawn as a screen circle), the arm axis ends, the shoulder line */
export function bodyGeom(ctx) {
  return { c: V.scale(ctx.armAxis, 6), r: ARM.delt, p0: V.scale(ctx.armAxis, ARM.s0), p1: V.scale(ctx.armAxis, ARM.s1), trap: TRAP.map((p) => V.sub(p, ctx.lift)) };
}
function bodyPath(ctx, cam) {
  const b = bodyGeom(ctx), S = cam.S, c = cam.proj(b.c), r = b.r * S;
  const circle = `M${nums([q(c[0] - r), q(c[1])])}a${nums([q(r), q(r), 0, 1, 0, q(2 * r), 0])}a${nums([q(r), q(r), 0, 1, 0, -q(2 * r), 0])}`;
  const p0 = cam.proj(b.p0), p1 = cam.proj(b.p1);
  let dx = p1[0] - p0[0], dy = p1[1] - p0[1]; const L = Math.hypot(dx, dy) || 1e-9; dx /= L; dy /= L;
  const nx = -dy, ny = dx, side = (s) => poly([[p0[0] + s * nx * ARM.r0 * S, p0[1] + s * ny * ARM.r0 * S], [p1[0] + s * nx * ARM.r1 * S, p1[1] + s * ny * ARM.r1 * S]], false);
  return circle + side(1) + side(-1) + poly(b.trap.map(cam.proj), false);
}

// ---------------------------------------------------------------- the sampled loop (shared by every concept)
// probe points on the upper arm (arm frame, mm): its end 200 mm down and four points around it 160 mm down
const PROBE = [[0, -200, 0], [40, -160, 0], [-40, -160, 0], [0, -160, 40], [0, -160, -40]];
/** --n frames of KIN.motion(240) spaced by equal arm travel, every key pose twice (a short hold). Returns
 * {frames (the loop), samples: [{i, f, pose, t, key}] (between loop frames i and i+1 at fraction f), still, travel} */
export function samplePlan(N, frames = KIN.motion(240)) {
  const M = frames.length, P = frames.map((fr) => { const c = KIN.makeCtx(fr.pose, fr.t); return PROBE.map((p) => c.attach.armPt(p)); });
  const step = (i, j) => Math.max(...P[i].map((p, k) => V.norm(V.sub(p, P[j][k]))));
  const D = [0]; for (let i = 1; i < M; i++) D.push(D[i - 1] + step(i - 1, i));
  const total = D[M - 1] + step(M - 1, 0), Dx = (i) => (i === M ? total : D[i]);
  const keys = []; frames.forEach((fr, i) => { if (fr.key && (i === 0 || frames[i - 1].key !== fr.key)) keys.push(i); });
  const K = keys.length, len = keys.map((i, k) => Dx(k + 1 < K ? keys[k + 1] : M) - D[i]), n = keys.map(() => 0);
  if (N < 2 * K + 1) throw new Error(`--n ${N}: at least ${2 * K + 1} frames for ${K} key poses`);
  for (let left = N - 2 * K; left > 0; left--) {   // each extra frame to the stretch with the longest step (ties: first)
    let b = 0; for (let k = 1; k < K; k++) if (len[k] / (n[k] + 1) > len[b] / (n[b] + 1) + 1e-9) b = k;
    n[b]++;
  }
  const lerp = (a, b, f) => a + (b - a) * f, samples = [];
  const at = (target) => {                         // loop frame i and fraction f where the travel reaches `target`
    let i = 0; while (i + 1 <= M - 1 && D[i + 1] <= target) i++;
    const j = (i + 1) % M, span = Dx(i + 1) - D[i], f = span > 1e-9 ? (target - D[i]) / span : 0;
    if (f < 1e-6) return { i, f: 0 };
    if (f > 1 - 1e-6) return j === 0 ? { i: 0, f: 0 } : { i: j, f: 0 };
    return { i, f };
  };
  keys.forEach((i, k) => {
    const key = { i, f: 0, key: frames[i].key }; samples.push(key, { ...key });
    for (let s = 1; s <= n[k]; s++) samples.push(at(D[i] + len[k] * s / (n[k] + 1)));
  });
  samples.forEach((s) => {
    const a = frames[s.i], b = frames[(s.i + 1) % M], tb = s.i + 1 === M ? 1 : b.t;
    s.pose = s.f ? Object.fromEntries(Object.keys(a.pose).map((k) => [k, lerp(a.pose[k], b.pose[k], s.f)])) : a.pose;
    s.t = s.f ? lerp(a.t, tb, s.f) : a.t;
  });
  // the reduced-motion still: on the way up to overhead (arm and cuff both clear of the shoulder), not the overhead
  // key itself, which from any camera that also shows abduction stacks the cuff on the shoulder
  const kOver = samples.findIndex((s) => s.key === 'overhead'), still = Math.max(0, kOver - Math.max(1, Math.round(n[keys.findIndex((i) => frames[i].key === 'reach')] * 0.3)));
  return { frames, samples, still, travel: { total, len, n, keys } };
}
/** one concept over the plan: two laps of KIN.run (lap 2 kept), in-between samples solved warm from the loop frame before */
export function runConcept(c, plan) {
  const { frames, samples } = plan, M = frames.length, r = KIN.run(c, frames.concat(frames)), sol = r.frames.slice(M);
  const warm = []; let last = r.frames[M - 1].nan ? r.q0 : r.frames[M - 1].q;
  sol.forEach((s, i) => { if (!s.nan) last = s.q; warm[i] = last; });
  return samples.map((s) => {
    if (!s.f) return sol[s.i];
    const ctx = KIN.makeCtx(s.pose, s.t), x = KIN.solveFrame(c, ctx, warm[s.i], r.q0); x.ctx = ctx; return x;
  });
}

// ---------------------------------------------------------------- run
/** load every concept module (or the given ids); returns [{id, file, reason}] for modules that threw or registered nothing */
export function loadConcepts(only = []) {
  const files = fs.readdirSync(path.join(HERE, 'concepts')).filter((f) => f.endsWith('.js')).sort(), bad = [];
  for (const f of files) {
    const id = f.replace(/\.js$/, '');
    if (only.length && !only.includes(id)) continue;
    const before = KIN.order.length;
    try { vm.runInThisContext(fs.readFileSync(path.join(HERE, 'concepts', f), 'utf8'), { filename: f }); }
    catch (e) { bad.push({ id, reason: `module threw: ${String(e.message || e).split('\n')[0]}` }); continue; }
    if (KIN.order.length === before && !KIN.concepts[id]) bad.push({ id, reason: 'module registered no concept' });
  }
  return { files, bad };
}
const srcMtime = (files) => Math.max(...[path.join(HERE, 'kin.js'), url.fileURLToPath(import.meta.url), ...files.map((f) => path.join(HERE, 'concepts', f))]
  .map((f) => { try { return fs.statSync(f).mtimeMs; } catch { return 0; } }));

function main() {
  const args = process.argv.slice(2);
  const opt = (k, d) => { const i = args.indexOf(k); if (i < 0) return d; const v = args[i + 1]; args.splice(i, 2); return v; };
  const flag = (k) => { const i = args.indexOf(k); if (i < 0) return false; args.splice(i, 1); return true; };
  const OUT_ARG = opt('--out', null), OUT = OUT_ARG || path.join(REPO, 'docs', 'dashboard', 'data', 'motion.json');
  const N = Number(opt('--n', 56));
  const SHEET = opt('--sheet', null);
  const STATS = flag('--stats');
  const CAM_ARG = opt('--cam', null);       // tuning only: dx,dy,dz,pan_right,pan_down,half
  const ONLY = args.filter((a) => !a.startsWith('--'));
  const cam = camera(CAM_ARG ? (() => { const v = CAM_ARG.split(',').map(Number); return { dir: v.slice(0, 3), pan: v.slice(3, 5), half: v[5], view: CAM.view }; })() : CAM);

  const t0 = Date.now(), { files, bad } = loadConcepts(ONLY), mtime = srcMtime(files);   // mtime read BEFORE the run
  const plan = samplePlan(N), still = plan.still;
  const base = { n: N, still, view: `0 0 ${cam.view} ${cam.view}` }, blank = { closes: '', body: '', mech: '', joint: '', note: '' };
  const rows = [{ id: '_shoulder', kind: 'shoulder', ...base, ...blank, body: pack(plan.samples.map((s) => bodyPath(KIN.makeCtx(s.pose, s.t), cam))) }];
  const skipped = bad.map((b) => ({ id: b.id, kind: 'skipped', ...base, ...blank, note: b.reason }));
  const notes = [];
  for (const id of [...KIN.order].sort()) {
    if (ONLY.length && !ONLY.includes(id)) continue;
    const c = KIN.concepts[id], t1 = Date.now(); dropped = 0;
    try {
      const sol = runConcept(c, plan), mech = [], joint = [], closes = [];
      for (const s of sol) {
        const L = partLines(c.parts(s.q, s.ctx)), m = linesPath(L.mech, cam), j = linesPath(L.joint, cam);
        if (/NaN|Infinity/.test(m + j)) throw new Error('NaN in the drawing');
        mech.push(m); joint.push(j); closes.push(s.closes ? '1' : '0');
      }
      rows.push({ id, kind: 'mechanism', ...base, ...blank, closes: closes.join(''), mech: pack(mech), joint: pack(joint) });
      if (dropped) { notes.push(`${id}: ${dropped} part drawing(s) with non-finite points left out`); dropped = 0; }
      if (STATS) process.stderr.write(`${id} ${Date.now() - t1} ms\n`);
    } catch (e) { skipped.push({ id, kind: 'skipped', ...base, ...blank, note: `run threw: ${String(e.message || e).split('\n')[0]}` }); }
  }
  const all = rows.concat(skipped).sort((a, b) => (a.id < b.id ? -1 : a.id > b.id ? 1 : 0));
  const raw = JSON.stringify(all), nDrawn = rows.length - 1;
  // a run on chosen ids never overwrites the dashboard's file unless --out names one; the file's mtime is the newest
  // source read at the start, so anything written during the run is newer (tools/dash_build.py re-runs then)
  const write = nDrawn > 0 && (!ONLY.length || OUT_ARG);
  if (write) {
    fs.mkdirSync(path.dirname(OUT), { recursive: true }); fs.writeFileSync(OUT, raw);
    const t = Math.ceil(mtime) / 1000; fs.utimesSync(OUT, t, t);    // ceil to the ms: never older than a source read
  }
  const tr = plan.travel;
  console.log(`motion previews: ${nDrawn} concept(s), ${N} frames each (arm travel ${tr.total.toFixed(0)} mm, longest step ${Math.max(...tr.len.map((l, k) => l / (tr.n[k] + 1))).toFixed(0)} mm), still = frame ${still}, ${raw.length} bytes${write ? ' -> ' + path.relative(process.cwd(), OUT) : ' (not written)'} (${((Date.now() - t0) / 1000).toFixed(1)} s)`);
  if (skipped.length) console.log(`skipped ${skipped.length}:\n` + skipped.map((s) => `  ${s.id}: ${s.note}`).join('\n'));
  if (notes.length) console.log(notes.join('\n'));
  if (STATS) stats(all, cam, still);
  if (SHEET) sheet(all, SHEET);
  if (nDrawn <= 0) process.exit(1);
}

// --stats: how much of the drawing the fixed camera keeps, the largest step between frames, the wrap jump
const pathPts = (d) => { const o = []; let x = 0, y = 0; for (const m of d.matchAll(/([Ml])([^Mlaz]*)/g)) { const n = (m[2].match(/-?\d+/g) || []).map(Number);
  if (m[1] === 'M') { x = n[0]; y = n[1]; o.push([x, y]); } else for (let i = 0; i + 1 < n.length; i += 2) { x += n[i]; y += n[i + 1]; o.push([x, y]); } } return o; };
function stats(rows, cam, still) {
  const inside = ([x, y]) => x >= 0 && x <= cam.view && y >= 0 && y <= cam.view;
  let nc = 0, ff = 0, nf = 0, pin = 0, np = 0, okStill = 0; const out = {}, big = [];
  for (const r of rows) {
    if (r.kind !== 'mechanism') continue;
    nc++; const m = unpack(r.mech), j = unpack(r.joint), F = m.map((d, k) => pathPts(d).concat(pathPts(j[k])));
    if (F[still].every(inside)) okStill++;
    F.forEach((P) => { nf++; if (P.every(inside)) ff++; else out[r.id] = (out[r.id] || 0) + 1; P.forEach((p) => { np++; if (inside(p)) pin++; }); });
    // the largest frame-to-frame move of the drawing (mean point shift, same point count only) and the wrap
    let worst = 0, at = -1;
    for (let k = 0; k < F.length; k++) { const A = F[k], B = F[(k + 1) % F.length]; if (A.length !== B.length || !A.length) continue;
      const d = A.reduce((s, p, i) => s + Math.hypot(p[0] - B[i][0], p[1] - B[i][1]), 0) / A.length; if (d > worst) { worst = d; at = k; } }
    big.push([r.id, Math.round(worst), at]);
  }
  console.log(`inside the frame: still frame of ${okStill}/${nc} concepts, ${(100 * ff / nf).toFixed(1)} % of frames whole, ${(100 * pin / np).toFixed(1)} % of points`);
  console.log('frames with something outside, by concept:', JSON.stringify(out));
  big.sort((a, b) => b[1] - a[1]);
  console.log('largest mean drawing shift between consecutive frames (units, frame):', big.slice(0, 8).map((b) => `${b[0]} ${b[1]} @${b[2]}`).join(', '));
}
// contact sheet (SVG) for a look without a browser: one row per concept, `cols` frames across
function sheet(rows, file) {
  const sh = rows.find((r) => r.id === '_shoulder'), N = sh.n, cols = 8, cell = 56, pad = 8, lab = 150, idxs = Array.from({ length: cols }, (_, k) => Math.round(k * N / cols));
  const body = unpack(sh.body), mechs = rows.filter((r) => r.kind === 'mechanism');
  let s = `<svg xmlns="http://www.w3.org/2000/svg" width="${lab + cols * (cell + pad)}" height="${mechs.length * (cell + pad) + pad}" font-family="monospace" font-size="9"><rect width="100%" height="100%" fill="#fff"/>`;
  mechs.forEach((r, j) => {
    const m = unpack(r.mech), jt = unpack(r.joint), y = pad + j * (cell + pad);
    s += `<text x="4" y="${y + cell / 2}">${r.id.slice(0, 22)}</text>`;
    idxs.forEach((k, i) => {
      s += `<svg x="${lab + i * (cell + pad)}" y="${y}" width="${cell}" height="${cell}" viewBox="${r.view}"><rect width="100" height="100" fill="none" stroke="#ddd"/>`
        + `<g fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="${body[k]}" stroke="#777" stroke-opacity=".6" stroke-width="1" vector-effect="non-scaling-stroke"/>`
        + `<path d="${m[k]}" stroke="#111" stroke-width="1.2" vector-effect="non-scaling-stroke"/><path d="${jt[k]}" stroke="#111" stroke-width="3" vector-effect="non-scaling-stroke"/></g></svg>`;
    });
  });
  fs.writeFileSync(file, s + '</svg>');
  console.log('sheet ->', file);
}

if (process.argv[1] && path.resolve(process.argv[1]) === url.fileURLToPath(import.meta.url)) main();
