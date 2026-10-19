// test.mjs - headless harness for the concept gallery: loads kin.js + every concepts/*.js, runs the motion loop and
// prints per concept: frames solved (closes the loop / in working range), max / p95 residual (mm, deg), max joint jump
// between frames (continuity), NaN count, min distance of any part to the GH centre and to the arm axis (sanity),
// descriptor validity. Exits non-zero on a broken module.
//   node docs/concepts/viz/test.mjs [id ...] [--json]
import { createRequire } from 'module';
import fs from 'fs';
import path from 'path';
import url from 'url';
import vm from 'vm';

const HERE = path.dirname(url.fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
const KIN = require(path.join(HERE, 'kin.js'));
const args = process.argv.slice(2), asJson = args.includes('--json'), only = args.filter(a => !a.startsWith('--'));
let broken = 0;
const files = fs.readdirSync(path.join(HERE, 'concepts')).filter(f => f.endsWith('.js')).sort();
for (const f of files) {
  const src = fs.readFileSync(path.join(HERE, 'concepts', f), 'utf8');
  try { vm.runInThisContext(src, { filename: f }); }
  catch (e) { console.log(`BROKEN ${f}: ${e.message}`); broken++; }
  const id = f.replace(/\.js$/, '');
  if (!KIN.concepts[id]) { console.log(`BROKEN ${f}: does not register id "${id}" (file name = id)`); broken++; }
}

const KINDS = new Set(KIN.KINDS), ROLES = new Set(KIN.ROLES);
const NEED = { hub: ['c', 'axis'], link: ['a', 'b'], arc: [], rail: ['c', 'axis', 'ref', 'rho', 'a0', 'a1'], carriage: ['c', 'x', 'z', 'size'],
  slider: ['a', 'b', 'at'], telescope: ['a', 'b', 'split'], strap: ['c', 'axis', 'r'], ring: ['c', 'axis', 'r'], plate: ['c', 'z', 'size'], point: ['p'] };
const V = KIN.V;
const isVec = v => Array.isArray(v) && v.length === 3 && v.every(Number.isFinite);
// sample points of a descriptor (for the sanity distances)
function samples(d) {
  switch (d.kind) {
    case 'hub': return [d.c, V.madd(d.c, V.unit(d.axis), d.h || 12)];
    case 'link': case 'telescope': return [0, 0.25, 0.5, 0.75, 1].map(s => V.lerp(d.a, d.b, s));
    case 'arc': return d.pts || KIN.greatArc(d.u, d.v, d.r0, d.r1, 12).map(p => V.add(p, d.c || [0, 0, 0]));
    case 'rail': { const e = V.unit(V.reject(d.ref, V.unit(d.axis))), f2 = V.cross(V.unit(d.axis), e), o = [];
      for (let i = 0; i <= 12; i++) { const a = (d.a0 + (d.a1 - d.a0) * i / 12) * KIN.D2R; o.push(V.add(d.c, V.add(V.scale(e, d.rho * Math.cos(a)), V.scale(f2, d.rho * Math.sin(a))))); } return o; }
    case 'slider': return [d.a, d.b, d.at];
    case 'strap': case 'ring': case 'carriage': case 'plate': return [d.c];
    case 'point': return [d.p];
  }
  return [];
}
const distToAxis = (p, ax) => { const s = Math.max(0, V.dot(p, ax)); return V.norm(V.sub(p, V.scale(ax, s))); };
const pct = (a, q) => { if (!a.length) return 0; const s = [...a].sort((x, y) => x - y); return s[Math.min(s.length - 1, Math.floor(q * (s.length - 1) + 0.5))]; };

const frames = KIN.motion(240), report = [];
for (const id of KIN.order) {
  if (only.length && !only.includes(id)) continue;
  const c = KIN.concepts[id], t0 = Date.now();
  let res;
  try { res = KIN.run(c, frames); } catch (e) { console.log(`BROKEN ${id}: run threw ${e.stack.split('\n').slice(0, 3).join(' | ')}`); broken++; continue; }
  const F = res.frames, mm = F.map(s => s.resMm), dg = F.map(s => s.resDeg);
  let jump = 0, jumpAt = -1, nan = 0, minGH = 1e9, minAxis = 1e9, nParts = null, partErr = null, closes = 0, inRange = 0;
  const reasons = {};
  F.forEach((s, i) => {
    if (s.nan) nan++;
    if (s.closes) closes++;
    if (s.closes && s.inRange) inRange++;
    if (s.reason) reasons[s.reason.replace(/[-\d.]+/g, '#')] = (reasons[s.reason.replace(/[-\d.]+/g, '#')] || 0) + 1;
    if (i > 0) {
      const d = Math.max(...s.q.map((x, j) => {
        const u = (c.qUnits || [])[j] || 'deg', dd = x - F[i - 1].q[j];
        return Math.abs(u === 'deg' ? KIN.wrap180(dd) : dd);
      }));
      if (d > jump) { jump = d; jumpAt = i; }
    }
    let parts;
    try { parts = c.parts(s.q, s.ctx); } catch (e) { partErr = partErr || `frame ${i}: ${e.message}`; return; }
    if (nParts === null) nParts = parts.map(p => p.kind).join(',');
    else if (nParts !== parts.map(p => p.kind).join(',')) partErr = partErr || `frame ${i}: parts change count / kinds`;
    for (const p of parts) {
      if (!KINDS.has(p.kind)) partErr = partErr || `unknown kind ${p.kind}`;
      if (!ROLES.has(p.role)) partErr = partErr || `unknown role ${p.role} (${p.kind})`;
      for (const k of NEED[p.kind] || []) if (p[k] == null) partErr = partErr || `${p.kind} ${p.name || ''} lacks ${k}`;
      if (p.kind === 'arc' && !p.pts && !(p.u && p.v && p.r0 != null && p.r1 != null)) partErr = partErr || `arc ${p.name || ''} needs pts or u, v, r0, r1`;
      for (const [k, v] of Object.entries(p)) if (Array.isArray(v) && v.length === 3 && typeof v[0] === 'number' && !isVec(v)) { nan++; partErr = partErr || `NaN in ${p.kind}.${k} frame ${i}`; }
      if (p.kind === 'point') continue;                       // markers (the GH centre) are not metal
      for (const x of samples(p)) {
        if (!isVec(x)) continue;
        minGH = Math.min(minGH, V.norm(x));
        if (p.role !== 'fixed-arm') minAxis = Math.min(minAxis, distToAxis(x, s.ctx.armAxis));
      }
    }
  });
  if (partErr) broken++;
  const row = { id, dof: c.dof, path: c.solve ? 'closed form' : 'numeric IK', frames: F.length, closes, closesInRange: inRange,
    resMmMax: Math.max(...mm), resMmP95: pct(mm, 0.95), resDegMax: Math.max(...dg), resDegP95: pct(dg, 0.95),
    maxJump: jump, maxJumpFrame: jumpAt, nan, minGH, minArmAxis: minAxis, parts: nParts ? nParts.split(',').length : 0,
    kinds: nParts ? [...new Set(nParts.split(','))].join(' ') : '', outOfRange: reasons, partErr, ms: Date.now() - t0 };
  report.push(row);
}

if (asJson) console.log(JSON.stringify(report, null, 1));
else for (const r of report) {
  const f = (x, d = 2) => (x == null ? '-' : x.toFixed(d));
  console.log(`${r.id}  [${r.path}, ${r.dof.active}A+${r.dof.passive}P, ${r.parts} parts: ${r.kinds}]`);
  console.log(`  frames ${r.frames}: closes ${r.closes}, closes + in range ${r.closesInRange}; residual max ${f(r.resMmMax, 4)} mm / ${f(r.resDegMax, 4)} deg, p95 ${f(r.resMmP95, 4)} mm / ${f(r.resDegP95, 4)} deg`);
  console.log(`  max joint jump ${f(r.maxJump)} (deg|mm) at frame ${r.maxJumpFrame}; NaN ${r.nan}; min part distance to GH ${f(r.minGH, 1)} mm, to the arm axis ${f(r.minArmAxis, 1)} mm (arm-fixed parts excluded); ${r.ms} ms`);
  if (Object.keys(r.outOfRange).length) console.log(`  out of working range: ${Object.entries(r.outOfRange).map(([k, v]) => `${v}x ${k}`).join('; ')}`);
  if (r.partErr) console.log(`  BROKEN parts: ${r.partErr}`);
}
const bad = report.filter(r => r.nan > 0 || r.partErr);
if (broken || bad.length) { console.log(`FAIL: ${broken} broken module(s), ${bad.length} concept(s) with NaN / bad parts`); process.exit(1); }
console.log(`OK: ${report.length} concept(s)`);
