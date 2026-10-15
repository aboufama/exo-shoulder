// thumbs.mjs - tiny monochrome motion previews of every concept for the dashboard leaderboard
// (docs/DASHBOARD.md, "Motion previews"). Node only, no browser.
//
//   node docs/concepts/viz/thumbs.mjs [--out docs/dashboard/data/motion.json] [--n 40] [--sheet file.svg] [--stats] [id ...]
//
// Each concept runs exactly as the gallery runs it (viewer.js: KIN.run over KIN.motion(240), so the numeric IK keeps
// its continuity from frame to frame); --n evenly spaced frames of that loop (rest -> forward raise -> overhead ->
// abduction -> across -> behind -> rest) are projected with ONE fixed orthographic camera shared by every concept
// (same direction, centre and scale, so designs compare) into a 0..100 viewBox, quantised to integers and written as
// compact SVG path strings, one per frame, frames separated by '|':
//   mech   links, arcs, rails, straps / rings (the cuff), plate and carriage outlines: single strokes
//   joint  hubs as short bars along their axis (a dot when the axis faces the camera), slider blocks, telescope splits
//   body   the shoulder only (one shared row, id "_shoulder"): deltoid circle, the upper arm clipped 200 mm down the
//          arm, the shoulder line toward the neck (moves with ctx.lift)
// Output: an array of row objects, all with the same columns {id, kind, n, still, view, closes, body, mech, joint},
// sorted by id (deterministic: unchanged sources -> unchanged bytes). `still` is the sampled frame nearest the
// overhead key pose (what a reduced-motion reader sees); `closes` has one character per frame, 1 = the chain closes.
// A concept whose module or run throws is skipped and listed on stderr (exit code stays 0 unless nothing was drawn).
import { createRequire } from 'module';
import fs from 'fs';
import path from 'path';
import url from 'url';
import vm from 'vm';

const HERE = path.dirname(url.fileURLToPath(import.meta.url));
const REPO = path.resolve(HERE, '..', '..', '..');
const require = createRequire(import.meta.url);
const KIN = require(path.join(HERE, 'kin.js'));
const V = KIN.V;

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); if (i < 0) return d; const v = args[i + 1]; args.splice(i, 2); return v; };
const flag = (k) => { const i = args.indexOf(k); if (i < 0) return false; args.splice(i, 1); return true; };
const OUT = opt('--out', path.join(REPO, 'docs', 'dashboard', 'data', 'motion.json'));
const N = Number(opt('--n', 40));
const SHEET = opt('--sheet', null);
const STATS = flag('--stats');
const CAM_ARG = opt('--cam', null);       // tuning only: dx,dy,dz,pan_right,pan_down,half
const ONLY = args.filter((a) => !a.startsWith('--'));

// ---------------------------------------------------------------- the one camera (orthographic)
// From front-right-above: x anterior, y up, z lateral (right shoulder). `pan` moves the frame (mm on the screen: right,
// down) off GH, `half` is its half-width in mm: tuned on every concept's drawn points so the overhead arm, the cuff in
// every pose and the scapular bases stay inside the frame (thumbs.mjs --stats prints what still falls outside).
const CAM = { dir: V.unit([0.42, 0.5, 0.76]), pan: [5, 10], half: 175, view: 100 };
if (CAM_ARG) { const v = CAM_ARG.split(',').map(Number); CAM.dir = V.unit(v.slice(0, 3)); CAM.pan = v.slice(3, 5); CAM.half = v[5]; }
const Zc = CAM.dir, Xc = V.unit(V.cross([0, 1, 0], Zc)), Yc = V.cross(Zc, Xc);
const S = CAM.view / (2 * CAM.half);
const proj = (p) => [CAM.view / 2 + (V.dot(p, Xc) - CAM.pan[0]) * S, CAM.view / 2 + (-V.dot(p, Yc) - CAM.pan[1]) * S];

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
/** polyline (screen pts) -> "M x y l dx dy ..." on the integer grid; closed adds z */
let dropped = 0;                          // parts whose points are not finite (a concept's own NaN: the gallery hides them too)
function poly(pts, closed) {
  if (pts.some((p) => !Number.isFinite(p[0]) || !Number.isFinite(p[1]))) { dropped++; return ''; }
  let P = rdp(pts, 0.45).map(([x, y]) => [q(x), q(y)]);
  P = P.filter((p, i) => i === 0 || p[0] !== P[i - 1][0] || p[1] !== P[i - 1][1]);
  if (closed && P.length > 1 && P[0][0] === P[P.length - 1][0] && P[0][1] === P[P.length - 1][1]) P.pop();
  if (!P.length) return '';
  let s = 'M' + nums(P[0]);
  if (P.length === 1) return s + 'l0 0';
  const d = [];
  for (let i = 1; i < P.length; i++) d.push(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]);
  return s + 'l' + nums(d) + (closed ? 'z' : '');
}
const seg = (a, b) => poly([proj(a), proj(b)], false);

// circle of radius r about unit axis k at c (a0..a1 deg from ref, full when absent), as projected screen points
function circlePts(c, axis, ref, r, a0, a1) {
  const k = V.unit(axis), e = V.unit(V.reject(ref && V.norm(V.reject(ref, k)) > 1e-6 ? ref : V.perp(k), k)), f = V.cross(k, e);
  const full = a0 == null || a1 == null, A0 = full ? 0 : a0, A1 = full ? 360 : a1, n = Math.max(4, Math.ceil(Math.abs(A1 - A0) / 20));
  const out = [];
  for (let i = 0; i <= (full ? n - 1 : n); i++) {
    const a = (A0 + (A1 - A0) * i / n) * KIN.D2R;
    out.push(proj(V.add(c, V.add(V.scale(e, r * Math.cos(a)), V.scale(f, r * Math.sin(a))))));
  }
  return { pts: out, full };
}
const arcPts = (d) => (d.pts || KIN.greatArc(d.u, d.v, d.r0, d.r1, Math.max(3, Math.ceil(V.angle(d.u, d.v) / 8))).map((p) => V.add(p, d.c || [0, 0, 0]))).map(proj);
function railPts(d) {
  const k = V.unit(d.axis), e = V.unit(V.reject(d.ref, k)), f = V.cross(k, e), n = Math.max(3, Math.ceil(Math.abs(d.a1 - d.a0) / 8)), o = [];
  for (let i = 0; i <= n; i++) { const a = (d.a0 + (d.a1 - d.a0) * i / n) * KIN.D2R; o.push(proj(V.add(d.c, V.add(V.scale(e, d.rho * Math.cos(a)), V.scale(f, d.rho * Math.sin(a)))))); }
  return o;
}
/** basis of a box: z normal, x in-plane reference (viewer.js basisZX) */
function basisZX(z, x) { const ez = V.unit(z), ex = V.unit(V.norm(V.reject(x, ez)) > 1e-6 ? V.reject(x, ez) : V.perp(ez)); return [ex, V.cross(ez, ex), ez]; }
function rectPts(c, ex, ey, sx, sy) {
  return [[-1, -1], [1, -1], [1, 1], [-1, 1]].map(([i, j]) => proj(V.add(c, V.add(V.scale(ex, i * sx / 2), V.scale(ey, j * sy / 2)))));
}

const BIG_HUB = 18;               // mm: a hub this wide is a sleeve around the arm: drawn as its ring, not a dot
/** one frame of a concept -> {mech, joint} path strings */
function drawParts(parts) {
  const mech = [], joint = [];
  for (const d of parts) {
    switch (d.kind) {
      case 'link': mech.push(seg(d.a, d.b)); break;
      case 'arc': mech.push(poly(arcPts(d), false)); break;
      case 'rail': mech.push(poly(railPts(d), false)); break;
      case 'strap': case 'ring': { const c = circlePts(d.c, d.axis, d.ref, d.r, d.kind === 'strap' ? d.a0 : null, d.kind === 'strap' ? d.a1 : null); mech.push(poly(c.pts, c.full)); break; }
      case 'plate': case 'carriage': {
        const [ex, ey] = basisZX(d.z, d.x), s = d.size || [20, 16];
        mech.push(poly(rectPts(d.c, ex, ey, s[0], s[1]), true)); break;
      }
      case 'hub': {
        const ax = V.unit(d.axis), h = d.h || 12, r = d.r || 10;
        if (r > BIG_HUB) { const c = circlePts(V.madd(d.c, ax, h / 2), ax, null, r); mech.push(poly(c.pts, true)); }
        else joint.push(seg(d.c, V.madd(d.c, ax, h)));
        break;
      }
      case 'slider': mech.push(seg(d.a, d.b)); joint.push(seg(d.at, d.at)); break;
      case 'telescope': { mech.push(seg(d.a, d.b)); joint.push(seg(V.madd(d.a, V.unit(V.sub(d.b, d.a)), d.split), V.madd(d.a, V.unit(V.sub(d.b, d.a)), d.split))); break; }
      default: break;                // point: markers (the GH centre), not metal
    }
  }
  return { mech: mech.filter(Boolean).join(''), joint: joint.filter(Boolean).join('') };
}

// ---------------------------------------------------------------- the shoulder (shared by every concept)
const ARM = { s0: 8, s1: 200, r0: 41, r1: 34, delt: 45 };
// trunk-fixed points of the shoulder line: lateral trapezius edge -> neck base -> up the side of the neck
const TRAP = [[-8, 46, -48], [-4, 70, -108], [2, 128, -124]];
function drawBody(ctx) {
  const ax = ctx.armAxis, c = proj(V.scale(ax, 6)), r = ARM.delt * S;
  const circle = `M${nums([q(c[0] - r), q(c[1])])}a${nums([q(r), q(r), 0, 1, 0, q(2 * r), 0])}a${nums([q(r), q(r), 0, 1, 0, -q(2 * r), 0])}`;
  const p0 = proj(V.scale(ax, ARM.s0)), p1 = proj(V.scale(ax, ARM.s1));
  let dx = p1[0] - p0[0], dy = p1[1] - p0[1]; const L = Math.hypot(dx, dy) || 1e-9; dx /= L; dy /= L;
  const nx = -dy, ny = dx, side = (s) => poly([[p0[0] + s * nx * ARM.r0 * S, p0[1] + s * ny * ARM.r0 * S], [p1[0] + s * nx * ARM.r1 * S, p1[1] + s * ny * ARM.r1 * S]], false);
  const trap = poly(TRAP.map((p) => proj(V.sub(p, ctx.lift))), false);
  return circle + side(1) + side(-1) + trap;
}

// ---------------------------------------------------------------- run
const files = fs.readdirSync(path.join(HERE, 'concepts')).filter((f) => f.endsWith('.js')).sort();
const skipped = [];
for (const f of files) {
  const id = f.replace(/\.js$/, '');
  if (ONLY.length && !ONLY.includes(id)) continue;
  try { vm.runInThisContext(fs.readFileSync(path.join(HERE, 'concepts', f), 'utf8'), { filename: f }); }
  catch (e) { skipped.push(`${id}: module threw ${e.message}`); }
}
const frames = KIN.motion(240);
const pick = []; for (let i = 0; i < N; i++) pick.push(Math.round(i * frames.length / N));
const keyIdx = frames.map((f, i) => (f.key === 'overhead' ? i : -1)).filter((i) => i >= 0);
const overheadAt = keyIdx.length ? keyIdx[Math.floor(keyIdx.length / 2)] : 0;
const still = pick.reduce((b, f, i) => (Math.abs(f - overheadAt) < Math.abs(pick[b] - overheadAt) ? i : b), 0);
const base = { n: N, still, view: `0 0 ${CAM.view} ${CAM.view}` };

const rows = [];
rows.push({ id: '_shoulder', kind: 'shoulder', ...base, closes: '', body: pick.map((i) => drawBody(KIN.makeCtx(frames[i].pose, frames[i].t))).join('|'), mech: '', joint: '' });
const notes = [];
const t0 = Date.now();
for (const id of [...KIN.order].sort()) {
  if (ONLY.length && !ONLY.includes(id)) continue;
  const c = KIN.concepts[id], t1 = Date.now();
  try {
    const sol = KIN.run(c, frames).frames, mech = [], joint = [], closes = [];
    for (const i of pick) {
      const s = sol[i], parts = c.parts(s.q, s.ctx), d = drawParts(parts);
      if (/NaN|Infinity/.test(d.mech + d.joint)) throw new Error(`frame ${i}: NaN in the drawing`);
      mech.push(d.mech); joint.push(d.joint); closes.push(s.closes ? '1' : '0');
    }
    rows.push({ id, kind: 'mechanism', ...base, closes: closes.join(''), body: '', mech: mech.join('|'), joint: joint.join('|') });
    if (dropped) { notes.push(`${id}: ${dropped} part drawing(s) with non-finite points left out`); dropped = 0; }
    if (STATS) process.stderr.write(`${id} ${Date.now() - t1} ms\n`);
  } catch (e) { skipped.push(`${id}: ${String(e.message || e).split('\n')[0]}`); }
}
rows.sort((a, b) => (a.id < b.id ? -1 : a.id > b.id ? 1 : 0));
const raw = JSON.stringify(rows);
if (rows.length > 1) {
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  const old = fs.existsSync(OUT) ? fs.readFileSync(OUT, 'utf8') : null;
  if (old !== raw) fs.writeFileSync(OUT, raw);
}
console.log(`motion previews: ${rows.length - 1} concept(s), ${N} frames each, still = frame ${still}, ${raw.length} bytes -> ${path.relative(process.cwd(), OUT)} (${((Date.now() - t0) / 1000).toFixed(1)} s)`);
if (skipped.length) console.log(`skipped ${skipped.length}:\n  ` + skipped.join('\n  '));

if (notes.length) console.log(notes.join('\n'));
// --stats: how much of the drawing the fixed camera keeps (overhead frames of every concept, whole frames, points)
if (STATS) {
  const pts = (d) => { const o = []; let x = 0, y = 0; for (const m of d.matchAll(/([Ml])([^Mlaz]*)/g)) { const n = (m[2].match(/-?\d+/g) || []).map(Number);
    if (m[1] === 'M') { x = n[0]; y = n[1]; o.push([x, y]); } else for (let i = 0; i + 1 < n.length; i += 2) { x += n[i]; y += n[i + 1]; o.push([x, y]); } } return o; };
  const inside = ([x, y]) => x >= 0 && x <= CAM.view && y >= 0 && y <= CAM.view;
  let oh = 0, nc = 0, ff = 0, nf = 0, pin = 0, np = 0; const out = {};
  for (const r of rows) {
    if (r.kind !== 'mechanism') continue;
    nc++; const m = r.mech.split('|'), j = r.joint.split('|'), F = m.map((d, k) => pts(d).concat(pts(j[k])));
    if ([still - 1, still, still + 1].every((k) => F[(k + N) % N].every(inside))) oh++;
    F.forEach((P) => { nf++; if (P.every(inside)) ff++; else out[r.id] = (out[r.id] || 0) + 1; P.forEach((p) => { np++; if (inside(p)) pin++; }); });
  }
  console.log(`inside the frame: overhead (3 frames) of ${oh}/${nc} concepts, ${(100 * ff / nf).toFixed(1)} % of frames whole, ${(100 * pin / np).toFixed(1)} % of points`);
  console.log('frames with something outside, by concept:', JSON.stringify(out));
}

// contact sheet (SVG) for a look without a browser: one row per concept, `cols` frames across
if (SHEET) {
  const cols = 8, cell = 56, pad = 8, lab = 150, idxs = Array.from({ length: cols }, (_, k) => Math.round(k * N / cols));
  const sh = rows.find((r) => r.id === '_shoulder').body.split('|'), body = rows.filter((r) => r.kind === 'mechanism');
  let s = `<svg xmlns="http://www.w3.org/2000/svg" width="${lab + cols * (cell + pad)}" height="${body.length * (cell + pad) + pad}" font-family="monospace" font-size="9"><rect width="100%" height="100%" fill="#fff"/>`;
  body.forEach((r, j) => {
    const m = r.mech.split('|'), jt = r.joint.split('|'), y = pad + j * (cell + pad);
    s += `<text x="4" y="${y + cell / 2}">${r.id.slice(0, 22)}</text>`;
    idxs.forEach((k, i) => {
      s += `<svg x="${lab + i * (cell + pad)}" y="${y}" width="${cell}" height="${cell}" viewBox="${r.view}"><rect width="100" height="100" fill="none" stroke="#ddd"/>`
        + `<path d="${sh[k]}" fill="none" stroke="#777" stroke-opacity=".5" stroke-width="1.6"/><path d="${m[k]}" fill="none" stroke="#111" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"/>`
        + `<path d="${jt[k]}" fill="none" stroke="#111" stroke-width="5" stroke-linecap="round"/></svg>`;
    });
  });
  fs.writeFileSync(SHEET, s + '</svg>');
  console.log('sheet ->', SHEET);
}
if (rows.length <= 1) process.exit(1);
