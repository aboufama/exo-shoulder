// thumbs.mjs - tiny monochrome motion previews of every concept for the dashboard leaderboard
// (docs/DASHBOARD.md, "Motion previews"). Node only, no browser.
//
//   node docs/concepts/viz/thumbs.mjs [--out docs/dashboard/data/motion.json] [--n 60] [--sheet file.svg] [--stats] [id ...]
//   (tools/dash_build.py runs it when kin.js, this file or a concepts/*.js is newer than motion.json, or the concept
//    files and the rows disagree)
//
// Each concept runs as the gallery runs it (viewer.js: KIN.run over KIN.motion(240), the numeric IK warm-started from
// frame to frame), over two laps so the warm start carries across the loop's wrap (an IK branch that drifts during
// lap 1 would otherwise jump back at every repeat); lap 2 is drawn. The loop (rest -> forward raise -> overhead ->
// abduction -> across -> behind -> rest) is sampled at --n frames spaced by equal TRAVEL, not equal time (KIN.motion
// holds at each key pose and moves fast in between: equal-time frames jump up to half the thumbnail in one tick): every
// key pose is shown twice (one short hold) and the frames between two keys are spread evenly over the distance moved,
// per loop step the larger of the upper arm's (its end 200 mm down and four points around it) and the mechanisms' (the
// 90th percentile over all concepts of their parts' largest move: spherical chains swing their hubs ~2.5x as far as the
// arm end near overhead -> abduction, and with arm travel alone 6 leaderboard rows jumped > 15 units in the same tick);
// a frame that falls between two loop frames is solved there, warm-started from the loop frame before it. ONE fixed
// orthographic camera, shared by every concept (same direction, centre and scale, so designs compare), projects into a
// 0..100 viewBox, quantised to integers and written as compact SVG path strings, one per frame, frames separated by '|'
// ('=' stands for a frame identical to the one before it: the key-pose holds cost nothing):
//   mech   links, arcs, rails, straps / rings (the cuff), plate and carriage outlines: single strokes. Construction
//          geometry (a part named "construction line", "not metal" or "trace", or a link / arc / rail thinner than
//          1.5 mm) is not metal and is not drawn.
//   joint  hubs as short bars along their axis (a dot when the axis faces the camera), slider blocks, telescope splits,
//          rolling-contact axes (a link named "contact ...": the moving joint line of rolling cones / fins)
//   body   the shoulder only (one shared row, id "_shoulder"): deltoid circle, the upper arm clipped 200 mm down the
//          arm, the shoulder line toward the neck (moves with ctx.lift)
// Output: an array of row objects, all with the same columns {id, kind, n, still, view, closes, body, mech, joint,
// note}, sorted by id (deterministic: unchanged sources -> unchanged bytes). `still` is the frame a reduced-motion
// reader sees (on the way up to overhead); `closes` has one character per frame, 1 = the chain closes. A concept file
// whose module or run throws, that registers nothing, or that registers an id other than its file name gets a row of
// kind "skipped" keyed by the file name, with the reason in `note` (no drawing), so a reader sees which modules have no
// preview and tools/dash_build.py does not re-run for an unchanged broken module. The file's mtime is the newest mtime
// of the sources, each stat'ed before it is read, so a source saved after its read is newer and triggers the next build.
import { createRequire } from 'module';
import fs from 'fs';
import path from 'path';
import url from 'url';
import vm from 'vm';

const HERE = path.dirname(url.fileURLToPath(import.meta.url));
const REPO = path.resolve(HERE, '..', '..', '..');
const require = createRequire(import.meta.url);
const SELF = url.fileURLToPath(import.meta.url), KIN_FILE = path.join(HERE, 'kin.js');
const mtimeOf = (f) => { try { return fs.statSync(f).mtimeMs; } catch { return 0; } };
const MT0 = { kin: mtimeOf(KIN_FILE), self: mtimeOf(SELF) };   // stat'ed BEFORE kin.js is read (the motion.json stamp)
export const KIN = require(KIN_FILE);
const V = KIN.V;

// ---------------------------------------------------------------- the one camera (orthographic)
// From the front-right (45 deg between anterior x and lateral z) and 12 deg above (y up): the overhead arm points up
// the thumbnail (77 % of its length on screen; the earlier 30 deg-high camera showed 48 %: overhead read as a ring over
// a circle), and forward raise and abduction show 72 % each. `pan` moves the frame (mm on the screen: right, down) off
// GH, `half` is its half-width in mm: fitted on 2026-10-16 so every leaderboard design's drawing stays inside the frame
// in every sampled pose with about a unit to spare (thumbs.mjs --stats prints what falls out and the closest approach to
// the edge; offset-axis-skin-hubs, whose cuff stage reaches 224 mm down the arm, spans the full height and sets it).
export const CAM = { dir: [1, 0.3, 1], pan: [25, 12], half: 218, view: 100 };
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
// Ramer-Douglas-Peucker on projected points (screen units). The distance is to the SEGMENT first -> last point, not the
// infinite line through them: a ring is an open chain whose ends are neighbours on the circle, so seen edge-on every
// point lies near that line and a line test kept only the two neighbours (round-2 review: the cuff became a 3-unit dash
// at the behind-the-back pose in 69 of 74 concepts, the whole column blinking once per loop).
export function rdp(pts, eps) {
  if (pts.length < 3) return pts;
  const [a, b] = [pts[0], pts[pts.length - 1]];
  const dx = b[0] - a[0], dy = b[1] - a[1], L2 = dx * dx + dy * dy;
  let k = -1, dm = 0;
  for (let i = 1; i < pts.length - 1; i++) {
    const p = pts[i], t = L2 < 1e-18 ? 0 : Math.max(0, Math.min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2));
    const d = Math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy);
    if (d > dm) { dm = d; k = i; }
  }
  if (dm <= eps) return [a, b];
  return rdp(pts.slice(0, k + 1), eps).slice(0, -1).concat(rdp(pts.slice(k), eps));
}
let dropped = 0;                          // parts whose points are not finite (a concept's own NaN: the gallery hides them too)
const collapsed = [];                     // drawn polylines that came out under half their projected size (must stay empty)
let drawing = '';                         // the concept / frame being drawn (for the collapse census)
const extent = (P) => { let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity; for (const [x, y] of P) { x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y); } return Math.hypot(x1 - x0, y1 - y0); };
/** polyline (screen pts) -> "M x y l dx dy ..." on the integer grid; closed adds z */
function poly(pts, closed) {
  if (pts.some((p) => !Number.isFinite(p[0]) || !Number.isFinite(p[1]))) { dropped++; return ''; }
  let P = rdp(pts, 0.45).map(([x, y]) => [q(x), q(y)]);
  if (pts.length > 2) { const e0 = extent(pts); if (e0 >= 5 && extent(P) < 0.5 * e0) collapsed.push(`${drawing}: ${e0.toFixed(0)} -> ${extent(P).toFixed(0)}`); }
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
/** a rolling-contact joint drawn by its concept as a thin link along the contact line (the moving joint axis: rolling
 * cones / fins on crossed straps): a joint, drawn as a joint bar, not as a metal link */
export const isContactAxis = (d) => d.kind === 'link' && /\bcontact\b/i.test(d.name || '');
/** one frame's parts -> 3-D polylines {pts, closed}: mech (strokes) and joint (bars / dots) */
export function partLines(parts) {
  const mech = [], joint = [], L = (pts, closed = false) => ({ pts, closed });
  for (const d of parts) {
    if (isConstruction(d)) continue;
    switch (d.kind) {
      case 'link': (isContactAxis(d) ? joint : mech).push(L([d.a, d.b])); break;
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
/** points that move with the parts (hub / carriage / ring centres, link / slider / telescope / arc / rail ends): the
 * mechanism's travel between frames */
export function partKeys(parts) {
  const o = [], ends = (P) => o.push(P[0], P[P.length - 1]);
  for (const d of parts) {
    if (isConstruction(d)) continue;
    switch (d.kind) {
      case 'hub': case 'plate': case 'carriage': case 'strap': case 'ring': o.push(d.c); break;
      case 'link': case 'slider': case 'telescope': o.push(d.a, d.b); break;
      case 'arc': ends(arc3(d)); break;
      case 'rail': ends(rail3(d)); break;
      default: break;
    }
  }
  return o;
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
/** --n frames of KIN.motion(240) spaced by equal travel, every key pose twice (a short hold). The travel of a loop step is
 * the larger of the arm's (the probe points) and `mech[i]` (mm, optional: the typical mechanism's move over that step,
 * see mechTravel), so the frames also crowd where the chains swing fast (near overhead -> abduction a spherical 3R hub
 * moves ~2.5x as far as the arm end). Returns {frames (the loop), samples: [{i, f, pose, t, key}] (between loop frames i
 * and i+1 at fraction f), still, travel} */
export function samplePlan(N, frames = KIN.motion(240), mech = null) {
  const M = frames.length, P = frames.map((fr) => { const c = KIN.makeCtx(fr.pose, fr.t); return PROBE.map((p) => c.attach.armPt(p)); });
  const arm = (i, j) => Math.max(...P[i].map((p, k) => V.norm(V.sub(p, P[j][k]))));
  const step = (i, j) => Math.max(arm(i, j), mech && mech[i] > 0 ? mech[i] : 0);
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
/** one concept over the loop: two laps of KIN.run (lap 2 kept: the warm start carries across the wrap) and the warm
 * start of every loop frame (for samples between loop frames) */
export function runLaps(c, frames) {
  const M = frames.length, r = KIN.run(c, frames.concat(frames)), sol = r.frames.slice(M);
  const warm = []; let last = r.frames[M - 1].nan ? r.q0 : r.frames[M - 1].q;
  sol.forEach((s, i) => { if (!s.nan) last = s.q; warm[i] = last; });
  return { sol, warm, q0: r.q0 };
}
/** the largest move (mm) of any part key point from loop frame i to i + 1 (the wrap included); -1 when not comparable */
export function mechSteps(c, sol) {
  const K = sol.map((s) => { try { return partKeys(c.parts(s.q, s.ctx)); } catch { return null; } });
  return K.map((A, i) => {
    const B = K[(i + 1) % K.length]; if (!A || !B || A.length !== B.length) return -1;
    let m = 0; A.forEach((p, k) => { const d = V.norm(V.sub(p, B[k])); if (Number.isFinite(d) && d > m) m = d; }); return m;
  });
}
export const MECH_Q = 0.9;    // the mechanism travel of a loop step = this quantile over the concepts (a lone IK flip does not count)
/** per loop step, the MECH_Q quantile of the concepts' mechSteps */
export function mechTravel(stepsList, M) {
  return Array.from({ length: M }, (_, i) => {
    const v = stepsList.map((s) => s[i]).filter((x) => x >= 0).sort((a, b) => a - b);
    return v.length ? v[Math.min(v.length - 1, Math.floor(MECH_Q * v.length))] : 0;
  });
}
/** one concept over the plan (lap 2 of KIN.run), in-between samples solved warm from the loop frame before */
export function runConcept(c, plan, laps = runLaps(c, plan.frames)) {
  const { sol, warm, q0 } = laps;
  return plan.samples.map((s) => {
    if (!s.f) return sol[s.i];
    const ctx = KIN.makeCtx(s.pose, s.t), x = KIN.solveFrame(c, ctx, warm[s.i], q0); x.ctx = ctx; return x;
  });
}

// ---------------------------------------------------------------- run
export const listConcepts = () => fs.readdirSync(path.join(HERE, 'concepts')).filter((f) => f.endsWith('.js')).sort();
/** load every concept module (or the given ids). A file must register exactly the id of its name (README: file name =
 * id): `byId` maps each such id to the object ITS file registered (a later file that re-registers the id cannot replace
 * it); `bad` lists {id: the file name, reason} for a module that threw, registered nothing or registered another id, so
 * the rows and the files agree (tools/dash_build.py compares them) */
export function loadConcepts(only = [], files = listConcepts()) {
  const bad = [], byId = new Map(), owner = new Map(), reg0 = KIN.register;
  for (const f of files) {
    const id = f.replace(/\.js$/, '');
    if (only.length && !only.includes(id)) continue;
    const got = [];
    KIN.register = (c) => { const r = reg0(c); got.push(c); return r; };
    try { vm.runInThisContext(fs.readFileSync(path.join(HERE, 'concepts', f), 'utf8'), { filename: f }); }
    catch (e) { bad.push({ id, reason: `module threw: ${String(e.message || e).split('\n')[0]}` }); continue; }
    finally { KIN.register = reg0; }
    got.forEach((c) => { if (!owner.has(c.id)) owner.set(c.id, f); });
    const mine = got.find((c) => c.id === id);
    if (mine) { byId.set(id, mine); continue; }
    if (!got.length) { bad.push({ id, reason: 'module registered no concept' }); continue; }
    const other = got[0].id, by = owner.get(other);
    bad.push({ id, reason: `registers id "${other}", not its file name${by && by !== f ? ` (${by} registers it too)` : ''}: rename the file or the id` });
  }
  return { files, bad, byId };
}
/** the motion.json stamp: the newest mtime of the sources, each stat'ed BEFORE it is read (kin.js at import, the concept
 * modules before they load), so a source saved after its read is newer than the stamp and the next build re-runs. Node
 * reads this script before any stat: if it changed after the process started, the stamp stays older than it. */
function srcStamp(files) {
  let s = Math.max(MT0.kin, MT0.self, ...files.map((f) => mtimeOf(path.join(HERE, 'concepts', f))));
  if (MT0.self > performance.timeOrigin) s = Math.min(s, MT0.self - 1);
  return s;
}

function main() {
  const args = process.argv.slice(2);
  const opt = (k, d) => { const i = args.indexOf(k); if (i < 0) return d; const v = args[i + 1]; args.splice(i, 2); return v; };
  const flag = (k) => { const i = args.indexOf(k); if (i < 0) return false; args.splice(i, 1); return true; };
  const OUT_ARG = opt('--out', null), OUT = OUT_ARG || path.join(REPO, 'docs', 'dashboard', 'data', 'motion.json');
  const N = Number(opt('--n', 60));
  const SHEET = opt('--sheet', null);
  const STATS = flag('--stats');
  const ARM_ONLY = flag('--arm-only');      // tuning only: space the frames by the arm's travel alone
  const CAM_ARG = opt('--cam', null);       // tuning only: dx,dy,dz,pan_right,pan_down,half
  const ONLY = args.filter((a) => !a.startsWith('--'));
  const cam = camera(CAM_ARG ? (() => { const v = CAM_ARG.split(',').map(Number); return { dir: v.slice(0, 3), pan: v.slice(3, 5), half: v[5], view: CAM.view }; })() : CAM);

  const t0 = Date.now(), files = listConcepts(), stamp = srcStamp(files);   // every source stat'ed before it is read
  const { bad, byId } = loadConcepts(ONLY, files);
  // pass 1: every concept's two laps over the loop, and how far its parts move per loop step (the shared frame spacing)
  const loop = KIN.motion(240), runs = [], fails = bad.map((b) => [b.id, b.reason]);
  for (const id of [...byId.keys()].sort()) {
    const c = byId.get(id);
    try { const laps = runLaps(c, loop); runs.push({ id, c, laps, steps: mechSteps(c, laps.sol) }); }
    catch (e) { fails.push([id, `run threw: ${String(e.message || e).split('\n')[0]}`]); }
  }
  const plan = samplePlan(N, loop, ARM_ONLY ? null : mechTravel(runs.map((r) => r.steps), loop.length)), still = plan.still;
  const base = { n: N, still, view: `0 0 ${cam.view} ${cam.view}` }, blank = { closes: '', body: '', mech: '', joint: '', note: '' };
  const rows = [{ id: '_shoulder', kind: 'shoulder', ...base, ...blank, body: pack(plan.samples.map((s) => bodyPath(KIN.makeCtx(s.pose, s.t), cam))) }];
  // pass 2: draw the samples
  const armScr = plan.samples.map((s) => { const x = KIN.makeCtx(s.pose, s.t); return PROBE.map((p) => cam.proj(x.attach.armPt(p))); });
  const notes = [], jumps = []; collapsed.length = 0;
  for (const { id, c, laps } of runs) {
    const t1 = Date.now(); dropped = 0;
    try {
      const sol = runConcept(c, plan, laps), mech = [], joint = [], closes = [], keys = [];
      sol.forEach((s, k) => {
        drawing = `${id} f${k}`;
        const parts = c.parts(s.q, s.ctx), L = partLines(parts), m = linesPath(L.mech, cam), j = linesPath(L.joint, cam);
        if (/NaN|Infinity/.test(m + j)) throw new Error('NaN in the drawing');
        mech.push(m); joint.push(j); closes.push(s.closes ? '1' : '0'); keys.push(partKeys(parts).map(cam.proj));
      });
      rows.push({ id, kind: 'mechanism', ...base, ...blank, closes: closes.join(''), mech: pack(mech), joint: pack(joint) });
      jumps.push([id, ...tickJump(keys, armScr)]);
      if (dropped) { notes.push(`${id}: ${dropped} part drawing(s) with non-finite points left out`); dropped = 0; }
      if (STATS) process.stderr.write(`${id} ${Date.now() - t1} ms\n`);
    } catch (e) { fails.push([id, `run threw: ${String(e.message || e).split('\n')[0]}`]); }
  }
  const skipped = fails.map(([id, note]) => ({ id, kind: 'skipped', ...base, ...blank, note }));
  const all = rows.concat(skipped).sort((a, b) => (a.id < b.id ? -1 : a.id > b.id ? 1 : 0));
  const raw = JSON.stringify(all), nDrawn = rows.length - 1;
  // a run on chosen ids never overwrites the dashboard's file unless --out names one; the file's mtime is the stamp
  // (srcStamp: sources stat'ed before they were read), so a source saved during the run is newer and the next build re-runs
  const write = nDrawn > 0 && (!ONLY.length || OUT_ARG);
  if (write) {
    fs.mkdirSync(path.dirname(OUT), { recursive: true }); fs.writeFileSync(OUT, raw);
    const t = Math.ceil(stamp) / 1000; fs.utimesSync(OUT, t, t);    // ceil to the ms: never older than a source stat
  }
  const tr = plan.travel;
  console.log(`motion previews: ${nDrawn} concept(s), ${N} frames each (travel ${tr.total.toFixed(0)} mm, longest step ${Math.max(...tr.len.map((l, k) => l / (tr.n[k] + 1))).toFixed(0)} mm; frames per stretch ${tr.n.map((x) => x + 2).join(' ')}), still = frame ${still}, ${raw.length} bytes${write ? ' -> ' + path.relative(process.cwd(), OUT) : ' (not written)'} (${((Date.now() - t0) / 1000).toFixed(1)} s)`);
  if (skipped.length) console.log(`skipped ${skipped.length}:\n` + skipped.map((s) => `  ${s.id}: ${s.note}`).join('\n'));
  if (notes.length) console.log(notes.join('\n'));
  if (collapsed.length) console.log(`WARNING ${collapsed.length} part drawing(s) under half their projected size (rdp): ${collapsed.slice(0, 6).join('; ')}`);
  if (STATS) stats(all, cam, still, jumps);
  if (SHEET) sheet(all, SHEET);
  if (nDrawn <= 0) process.exit(1);
}
/** the largest move (screen units) of any part key point in one tick, its tick, and the arm's move in that tick */
function tickJump(keys, arm) {
  let worst = 0, at = -1;
  keys.forEach((A, k) => { const B = keys[(k + 1) % keys.length]; if (A.length !== B.length) return;
    A.forEach((p, i) => { const d = Math.hypot(p[0] - B[i][0], p[1] - B[i][1]); if (Number.isFinite(d) && d > worst) { worst = d; at = k; } }); });
  const a = at < 0 ? 0 : Math.max(...arm[at].map((p, i) => Math.hypot(p[0] - arm[(at + 1) % arm.length][i][0], p[1] - arm[(at + 1) % arm.length][i][1])));
  return [+worst.toFixed(1), at, +a.toFixed(1)];
}

// --stats: how much of the drawing the fixed camera keeps (and the closest approach to the frame edge), the largest
// part move in one tick (a move far beyond the arm's is an IK branch flip or a singular swing in the concept's own
// solution), the collapse census (must be empty)
const pathPts = (d) => { const o = []; let x = 0, y = 0; for (const m of d.matchAll(/([Ml])([^Mlaz]*)/g)) { const n = (m[2].match(/-?\d+/g) || []).map(Number);
  if (m[1] === 'M') { x = n[0]; y = n[1]; o.push([x, y]); } else for (let i = 0; i + 1 < n.length; i += 2) { x += n[i]; y += n[i + 1]; o.push([x, y]); } } return o; };
function stats(rows, cam, still, jumps) {
  const inside = ([x, y]) => x >= 0 && x <= cam.view && y >= 0 && y <= cam.view;
  let nc = 0, ff = 0, nf = 0, pin = 0, np = 0, okStill = 0; const out = {}, margin = [];
  for (const r of rows) {
    if (r.kind !== 'mechanism') continue;
    nc++; const m = unpack(r.mech), j = unpack(r.joint), F = m.map((d, k) => pathPts(d).concat(pathPts(j[k])));
    if (F[still].every(inside)) okStill++;
    let mg = Infinity;
    F.forEach((P) => { nf++; if (P.every(inside)) ff++; else out[r.id] = (out[r.id] || 0) + 1; P.forEach((p) => { np++; if (inside(p)) pin++; mg = Math.min(mg, p[0], p[1], cam.view - p[0], cam.view - p[1]); }); });
    margin.push([r.id, mg]);
  }
  console.log(`inside the frame: still frame of ${okStill}/${nc} concepts, ${(100 * ff / nf).toFixed(1)} % of frames whole, ${(100 * pin / np).toFixed(1)} % of points`);
  console.log('frames with something outside, by concept:', JSON.stringify(out));
  margin.sort((a, b) => a[1] - b[1]);
  console.log('closest to the frame edge (units):', margin.slice(0, 10).map((x) => `${x[0]} ${x[1]}`).join(', '));
  jumps.sort((a, b) => b[1] - a[1]);
  console.log('largest part move in one tick (units of 100, tick, arm move in that tick):', jumps.slice(0, 12).map((x) => `${x[0]} ${x[1]} @${x[2]} (arm ${x[3]})`).join(', '));
  const flips = jumps.filter((x) => x[1] > 15 && x[1] > 2.5 * Math.max(x[3], 1));
  console.log(`part moves > 15 units and > 2.5x the arm's in one tick (IK branch flip / singular swing in the concept's own solution): ${flips.length ? flips.map((x) => `${x[0]} ${x[1]} @${x[2]} (arm ${x[3]})`).join(', ') : 'none'}`);
  console.log(`collapse census (parts drawn under half their projected size): ${collapsed.length}`);
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
