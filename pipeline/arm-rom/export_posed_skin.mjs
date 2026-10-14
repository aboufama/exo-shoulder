// Posed skin of the body rig (body.js, exactly what the viewer draws, minus the GPU-only hair volume) for a list of
// poses, so collision maps can be built from the same skin the viewer shows (the legacy wi/ww linear blend in
// body_mesh.json collapses at the shoulder and webs the axilla; the viewer no longer uses it).
//   node export_posed_skin.mjs body_mesh.json poses.json out      poses.json: [{plane, elev, axial, flex, pron}, ...]
//   -> out.bin   float32 [pose][vertex][xyz], thorax mm (x anterior, y up, z right, origin right GH; trunk not lifted:
//                the girdle lift is in segs[0] like the viewer, i.e. add `lift` from out.json to get the drawn frame)
//      out.json  {n, poses, faces (base64 uint32), arm (base64 uint8: 1 = mostly on the right arm), lift per pose}
import { readFileSync, writeFileSync } from 'node:fs';
import { loadBody, segmentTransforms } from './body.js';

const [, , meshPath = 'body_mesh.json', posesPath = 'poses.json', out = 'posed_skin'] = process.argv;
globalThis.fetch = async u => ({ json: async () => JSON.parse(readFileSync(String(u).split('?')[0], 'utf8')) });
// headless stand-ins for the few three.js classes body.js touches (no rendering)
class Attr { constructor(a, k) { this.array = a; this.itemSize = k; } }
class Geom { constructor() { this.attributes = {}; this.index = null; } setAttribute(k, a) { this.attributes[k] = a; } setIndex(a) { this.index = a; } computeVertexNormals() {} }
class Obj { constructor(g, m) { this.geometry = g; this.material = m; this.children = []; this.matrix = { copy() {} }; this.visible = true; } add(o) { this.children.push(o); } }
class Mat { constructor(o = {}) { Object.assign(this, o); } clone() { return new Mat(this); } }
class Col { constructor(r = 1, g = 1, b = 1) { this.r = r; this.g = g; this.b = b; } setHSL() { return this; } }
class V { constructor(...a) { this.v = a; } set(...a) { this.v = a; return this; } normalize() { return this; } }
const THREE = { Group: Obj, Mesh: Obj, BufferGeometry: Geom, BufferAttribute: Attr, MeshPhysicalMaterial: Mat, MeshLambertMaterial: Mat, Color: Col,
  Vector3: V, Vector4: V, Matrix4: class { set() { return this; } copy() { return this; } }, DoubleSide: 2, FrontSide: 0 };

const B = await loadBody(THREE, meshPath);
const poses = JSON.parse(readFileSync(posesPath, 'utf8'));
const skin = B._dbg.dynamic.find(d => d.cls === 'skin'), n = skin.n;
const buf = new Float32Array(poses.length * n * 3), lifts = [];
poses.forEach((p, k) => {
  B.update(p, 0); buf.set(skin.mesh.geometry.attributes.position.array, k * n * 3);
  lifts.push(segmentTransforms(B.landmarks, p, { girdle: true, scale: B.scale }).lift);
});
const arm = new Uint8Array(n);
if (skin.cor) for (let i = 0; i < n; i++) { let h = 0; for (let j = 0; j < 4; j++) if (skin.wi[4 * i + j] >= 2) h += skin.ww[4 * i + j]; arm[i] = h > 127 ? 1 : 0; }
const b64 = a => Buffer.from(a.buffer, a.byteOffset, a.byteLength).toString('base64');
writeFileSync(out + '.bin', Buffer.from(buf.buffer));
writeFileSync(out + '.json', JSON.stringify({ n, poses, lift: lifts, faces: b64(Uint32Array.from(skin.mesh.geometry.index.array)), arm: b64(arm),
  frame: 'thorax mm: x anterior, y up, z right, origin right GH; positions as body.js update() leaves them (add lift for the viewer frame)' }));
console.log(`${poses.length} poses x ${n} skin vertices -> ${out}.bin / ${out}.json`);
