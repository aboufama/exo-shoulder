// Sample the anatomy's skin field (anatomy.js, same maths as the viewer) on grids around the right shoulder, for the
// morphology searches:  trunk grids (everything but the right arm) per arm elevation (the scapula moves), and one arm
// grid in the humerus frame (arm hanging; the arm's muscles are taken as moving rigidly with the humerus).
//   node make_skin_grids.mjs   ->  skin_grids.bin + skin_grids.json
import { writeFileSync } from 'node:fs';
import { buildAnatomy } from './anatomy.js';

class M4 { constructor() { this.e = new Array(16).fill(0); } copy() { return this; } invert() { return this; } multiply() { return this; }
  makeTranslation() { return this; } makeScale() { return this; } set() { return this; } }
const THREE = {
  DataTexture: class { constructor(d) { this.image = { data: d }; } }, RGBAFormat: 0, FloatType: 0, NearestFilter: 0,
  Vector3: class { constructor(...a) { this.v = a; } normalize() { return this; } }, Matrix4: M4, BackSide: 1,
  ShaderMaterial: class { constructor(o) { Object.assign(this, o); } }, BoxGeometry: class {}, Mesh: class { constructor() { this.matrix = new M4(); } },
};
const S = 411 / 310, H = 175, STEP = 5;                         // grid half-size and step, mm (scaled body)
const N = Math.round(2 * H / STEP) + 1;
const A = buildAnatomy(THREE, { scale: S });
const ELEVS = []; for (let e = 0; e <= 180; e += 15) ELEVS.push(e);
const grids = [];
function sample(which) {
  const g = new Float32Array(N * N * N); let k = 0;
  for (let i = 0; i < N; i++) for (let j = 0; j < N; j++) for (let l = 0; l < N; l++)
    g[k++] = A.skinDistance([-H + i * STEP, -H + j * STEP, -H + l * STEP], which);
  return g;
}
const t0 = Date.now();
for (const e of ELEVS) { A.update({ plane: 30, elev: e, axial: 0, flex: 30, pron: 0 }, 0); grids.push(sample('trunk')); console.log('trunk', e, ((Date.now() - t0) / 1000).toFixed(0) + 's'); }
A.update({ plane: 0, elev: 0, axial: 0, flex: 30, pron: 0 }, 0); grids.push(sample('arm')); console.log('arm', ((Date.now() - t0) / 1000).toFixed(0) + 's');
const out = new Float32Array(grids.length * N * N * N); grids.forEach((g, i) => out.set(g, i * N * N * N));
writeFileSync('skin_grids.bin', Buffer.from(out.buffer));
writeFileSync('skin_grids.json', JSON.stringify({ N, H, STEP, scale: S, elevs: ELEVS, order: 'trunk per elev, then arm (humerus frame)', frame: 'thorax mm: x anterior, y up, z right, origin right GH; axis order i=x j=y k=z' }));
console.log('done');
