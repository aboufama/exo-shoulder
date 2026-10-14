// Anatomical body for the exo viewer, from BodyParts3D (c) The Database Center for Life Science, CC BY-SA 2.1 JP.
// Real bone, muscle and skin meshes (anatomy-build/build_body.py), rigged to the same kinematics as the searches:
// thorax, scapula (scapulohumeral rhythm + girdle elevation), humerus (ISB plane / elevation / axial), ulna (elbow
// flexion), radius + hand (pronation).
// Skinning: centre-of-rotation skinning (Le & Hodgins 2016): each vertex turns with the quaternion blend of up to four
// bones about its own precomputed centre, which moves by linear blending -> no collapse at the axilla or elbow.
// Muscles that cross the right shoulder or elbow keep their volume:
//   spindle muscles (biceps, brachialis, brachioradialis, triceps, ...): the posed centreline length change goes into
//   the fleshy belly only (tendons inextensible), each slice keeps its volume, and the extra cross-section goes mostly
//   to the superficial side, so the belly shortens toward its origin, thickens and peaks; activation stretches the
//   tendons a little (series elasticity) and rounds the belly.
//   flat muscles (deltoid, pectoralis major, latissimus, ...): the superficial face moves out with the local fibre
//   stretch measured on the posed mesh.
// The skin follows the bones and, over the muscles, their shape change (a height field over the spindle muscles).
// Frame: thorax mm (x anterior, y up, z right, origin = right shoulder centre); place it with setFrame(worldFromThorax).
// Older body_mesh.json files (without the new rig fields) still load and use the previous linear-blend rig.

const D2R = Math.PI / 180;
const MUSH_IT = 10;                                   // Delta Mush smoothing iterations
const FR = new Float64Array(9);                       // scratch frame
const b64 = (s, T) => { const bin = atob(s), u = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i); return new T(u.buffer); };
function rot(ax, a) { const n = Math.hypot(...ax), x = ax[0] / n, y = ax[1] / n, z = ax[2] / n, c = Math.cos(a), s = Math.sin(a), t = 1 - c;
  return [[c + x * x * t, x * y * t - z * s, x * z * t + y * s], [y * x * t + z * s, c + y * y * t, y * z * t - x * s], [z * x * t - y * s, z * y * t + x * s, c + z * z * t]]; }
const mul = (A, B) => A.map(r => [0, 1, 2].map(j => r[0] * B[0][j] + r[1] * B[1][j] + r[2] * B[2][j]));
const mv = (A, v) => [A[0][0] * v[0] + A[0][1] * v[1] + A[0][2] * v[2], A[1][0] * v[0] + A[1][1] * v[1] + A[1][2] * v[2], A[2][0] * v[0] + A[2][1] * v[1] + A[2][2] * v[2]];
const T3 = A => [0, 1, 2].map(i => [A[0][i], A[1][i], A[2][i]]);
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]], add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]], sc = (a, k) => [a[0] * k, a[1] * k, a[2] * k];
// affine = [R (3x3), t]: p -> R p + t
const aff = (R, t = [0, 0, 0]) => ({ R, t });
const apply = (A, p) => add(mv(A.R, p), A.t);
const compose = (A, B) => aff(mul(A.R, B.R), add(mv(A.R, B.t), A.t));       // A after B
const about = (R, c) => aff(R, sub(c, mv(R, c)));                             // rotation R about point c
function quat(R) {                                                             // rotation matrix -> unit quaternion [w, x, y, z]
  const m00 = R[0][0], m11 = R[1][1], m22 = R[2][2], tr = m00 + m11 + m22; let w, x, y, z, S;
  if (tr > 0) { S = Math.sqrt(tr + 1) * 2; w = 0.25 * S; x = (R[2][1] - R[1][2]) / S; y = (R[0][2] - R[2][0]) / S; z = (R[1][0] - R[0][1]) / S; }
  else if (m00 > m11 && m00 > m22) { S = Math.sqrt(1 + m00 - m11 - m22) * 2; w = (R[2][1] - R[1][2]) / S; x = 0.25 * S; y = (R[0][1] + R[1][0]) / S; z = (R[0][2] + R[2][0]) / S; }
  else if (m11 > m22) { S = Math.sqrt(1 + m11 - m00 - m22) * 2; w = (R[0][2] - R[2][0]) / S; x = (R[0][1] + R[1][0]) / S; y = 0.25 * S; z = (R[1][2] + R[2][1]) / S; }
  else { S = Math.sqrt(1 + m22 - m00 - m11) * 2; w = (R[1][0] - R[0][1]) / S; x = (R[0][2] + R[2][0]) / S; y = (R[1][2] + R[2][1]) / S; z = 0.25 * S; }
  const n = Math.hypot(w, x, y, z); return [w / n, x / n, y / n, z / n];
}
const smooth01 = (a, b, x) => { const t = Math.max(0, Math.min(1, (x - a) / (b - a))); return t * t * (3 - 2 * t); };

export function scapulaRot(elev) {                    // same rhythm as the exo analysis
  const n = [Math.cos(30 * D2R), 0, -Math.sin(30 * D2R)];
  return mul(rot([0, 0, 1], 0.12 * elev * D2R), rot(n, -0.36 * Math.max(0, elev - 20) * D2R));
}
export const girdleLift = (elev, s) => [0, 0.2 * Math.max(0, elev - 30) * s, 0];

// segment transforms for a pose; shared with the collision-grid builder
export function segmentTransforms(L, pose, { girdle = true, scale = 1.335 } = {}) {
  const lift = girdle ? girdleLift(pose.elev, scale) : [0, 0, 0];
  const Rh = mul(rot([0, 1, 0], pose.plane * D2R), mul(rot([1, 0, 0], -pose.elev * D2R), rot([0, 1, 0], pose.axial * D2R)));
  const T = aff([[1, 0, 0], [0, 1, 0], [0, 0, 1]], sc(lift, -1));
  const S = aff(scapulaRot(pose.elev));
  const H = aff(mul(Rh, T3(L.rest_humerus)));
  const E = apply(H, L.elbow), ax = mv(H.R, L.elbow_axis);
  const F = compose(about(rot(ax, (pose.flex - L.rest_flex) * D2R), E), H);
  const rh = apply(F, L.radial_head), uh = apply(F, L.ulnar_head);
  const P = compose(about(rot(sub(rh, uh), (pose.pron + 90) * D2R), rh), F);      // rest = anatomical position (supinated)
  return { segs: [T, S, H, F, P], lift };
}

export async function loadBody(THREE, url = 'body_mesh.json') {
  const J = await (await fetch(url, { cache: 'no-store' })).json();
  const L = J.landmarks, s = J.scale;
  const root = new THREE.Group(); root.matrixAutoUpdate = false;
  const mat = {
    bone: new THREE.MeshPhysicalMaterial({ color: 0xe8dcc4, roughness: 0.55, metalness: 0, clearcoat: 0.15, clearcoatRoughness: 0.6 }),
    cartilage: new THREE.MeshPhysicalMaterial({ color: 0xd9dde0, roughness: 0.32, metalness: 0, clearcoat: 0.4, sheen: 0.4, sheenColor: 0xffffff }),
    muscle: new THREE.MeshPhysicalMaterial({ vertexColors: true, roughness: 0.42, metalness: 0, clearcoat: 0.35, clearcoatRoughness: 0.35, sheen: 0.35, sheenColor: new THREE.Color(0.9, 0.35, 0.3) }),
    skin: new THREE.MeshPhysicalMaterial({ color: 0xc99780, side: THREE.DoubleSide, roughness: 0.56, metalness: 0, sheen: 0.4, sheenRoughness: 0.55, sheenColor: new THREE.Color(0.95, 0.55, 0.45), clearcoat: 0.06, clearcoatRoughness: 0.45 }),
    eye: new THREE.MeshPhysicalMaterial({ color: 0xffffff, roughness: 0.22, metalness: 0, clearcoat: 1.0, clearcoatRoughness: 0.03 }),
  };
  // muscle fibres: a fine procedural striation along the dominant local direction, in the fragment shader
  mat.muscle.onBeforeCompile = sh => {
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying vec3 vObjPos;').replace('#include <begin_vertex>', '#include <begin_vertex>\nvObjPos = position;');
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\nvarying vec3 vObjPos;')
      .replace('#include <color_fragment>', `#include <color_fragment>
        float fib = sin(dot(vObjPos, vec3(0.31, 0.93, 0.18)) * 1.9 + sin(dot(vObjPos, vec3(0.8, -0.2, 0.55)) * 0.21) * 3.0);
        diffuseColor.rgb *= 0.9 + 0.1 * fib;`);
  };
  // ---- skin: briefs, head features (short hair, eyebrows, lid margins, lips, flush), tone variation, pores and a
  // subsurface-like warm wrap of the key light. Everything is driven by the rest position, so it stays put on the body.
  const Bf = J.briefs, HD = J.head || null, S10 = (10 * s).toFixed(3);
  const brow = new Array(16).fill(0).map(() => new THREE.Vector4(0, 0, 0, 0)), eyes = [new THREE.Vector4(0, 0, 0, 1), new THREE.Vector4(0, 0, 0, 1)], gaze = [new THREE.Vector3(1, 0, 0), new THREE.Vector3(1, 0, 0)];
  if (HD) {
    HD.brows.forEach((pl, b) => pl.slice(0, 8).forEach((q, k) => brow[8 * b + k].set(q[0], q[1], q[2], q[3])));
    HD.eyes.forEach((e, k) => eyes[k].set(e[0], e[1], e[2], e[3]));
    const tg = [HD.mid[0] + 1500 * s, HD.mid[1] - 40 * s, HD.mid[2]];            // a point ahead, slightly down
    HD.eyes.forEach((e, k) => gaze[k].set(tg[0] - e[0], tg[1] - e[1], tg[2] - e[2]).normalize());
  }
  const NOISE = `
    float hash3(vec3 p) { p = fract(p * 0.3183099 + 0.1); p *= 17.0; return fract(p.x * p.y * p.z * (p.x + p.y + p.z)); }
    float vnoise(vec3 x) { vec3 i = floor(x), f = fract(x); f = f * f * (3.0 - 2.0 * f);
      return mix(mix(mix(hash3(i), hash3(i + vec3(1, 0, 0)), f.x), mix(hash3(i + vec3(0, 1, 0)), hash3(i + vec3(1, 1, 0)), f.x), f.y),
                 mix(mix(hash3(i + vec3(0, 0, 1)), hash3(i + vec3(1, 0, 1)), f.x), mix(hash3(i + vec3(0, 1, 1)), hash3(i + vec3(1, 1, 1)), f.x), f.y), f.z); }`;
  const skinChunk = (sh, xray) => {
    sh.uniforms.uBrow = { value: brow }; sh.uniforms.uEye = { value: eyes };
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nattribute vec3 restPos; attribute float cloth; attribute vec4 feat; varying vec3 vRest; varying float vCloth; varying vec4 vFeat;')
      .replace('#include <begin_vertex>', `#include <begin_vertex>
        vRest = restPos; vCloth = cloth; vFeat = feat;
        transformed += objectNormal * smoothstep(0.3, 0.75, feat.x) * feat.y * ${S10};   // short haircut volume (mm)`);
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', `#include <common>
        uniform vec4 uBrow[16]; uniform vec4 uEye[2]; varying vec3 vRest; varying float vCloth; varying vec4 vFeat;
        ${NOISE}
        float browDensity(vec3 p) {
          float best = 0.0;
          for (int b = 0; b < 2; b++) for (int k = 0; k < 7; k++) {
            vec4 a = uBrow[b * 8 + k], c = uBrow[b * 8 + k + 1]; if (a.w <= 0.0 || c.w <= 0.0) continue;
            vec3 ab = c.xyz - a.xyz; float t = clamp(dot(p - a.xyz, ab) / dot(ab, ab), 0.0, 1.0);
            float w = mix(a.w, c.w, t), u = (float(k) + t) / 7.0, d = length(p - (a.xyz + t * ab));
            float dens = (1.0 - smoothstep(0.45 * w, 1.2 * w, d)) * (1.0 - smoothstep(0.72, 1.0, u)) * (0.75 + 0.25 * smoothstep(0.0, 0.2, u));
            best = max(best, dens); }
          return best; }
        vec3 bumpN(vec3 n, vec3 pos, float h) { vec3 dpx = dFdx(pos), dpy = dFdy(pos); float dhx = dFdx(h), dhy = dFdy(h);
          vec3 r1 = cross(dpy, n), r2 = cross(n, dpx); float det = dot(dpx, r1); if (abs(det) < 1e-12) return n;
          return normalize(abs(det) * n - sign(det) * (dhx * r1 + dhy * r2)); }`)
      .replace('#include <color_fragment>', `#include <color_fragment>
        float m1 = vnoise(vRest * 0.045), m2 = vnoise(vRest * 0.16 + 7.0);
        diffuseColor.rgb *= 0.965 + 0.05 * m1 + 0.03 * m2;                                   // mottling
        diffuseColor.rgb = mix(diffuseColor.rgb, diffuseColor.rgb * vec3(1.07, 0.86, 0.84), vFeat.w);   // flush
        float lipM = smoothstep(0.2, 0.7, vFeat.z);
        diffuseColor.rgb = mix(diffuseColor.rgb, diffuseColor.rgb * vec3(0.86, 0.56, 0.56) * (0.94 + 0.12 * m2), lipM);
        float lash = 0.0;                                                                 // lid margins (lash line)
        for (int k = 0; k < 2; k++) { float de = length(vRest - uEye[k].xyz) - uEye[k].w;
          lash += smoothstep(0.1, 0.55, (vRest.x - uEye[k].x) / uEye[k].w) * (1.0 - smoothstep(0.4, 2.6, de)); }
        diffuseColor.rgb *= 1.0 - 0.6 * clamp(lash, 0.0, 1.0);
        float bro = browDensity(vRest), bs = vnoise(vRest * vec3(2.6, 2.6, 0.55) + 3.0);
        bro *= 0.55 + 0.45 * bs;
        diffuseColor.rgb = mix(diffuseColor.rgb, vec3(0.07, 0.048, 0.036), clamp(bro * 1.15, 0.0, 0.92));
        float hn = vnoise(vRest * vec3(0.7, 0.22, 0.7)), hn2 = vnoise(vRest * 2.2);
        float hairM = smoothstep(0.3, 0.62, vFeat.x + 0.24 * (hn2 - 0.5));
        diffuseColor.rgb = mix(diffuseColor.rgb, vec3(0.05, 0.034, 0.024) * (0.7 + 0.6 * hn), hairM);
        float lat = abs(vRest.z - ${Bf.mid.toFixed(2)}) / ${Bf.latmax.toFixed(2)};
        float bottom = ${Bf.isch.toFixed(2)} - (60.0 - 50.0 * lat) * ${Bf.s.toFixed(3)};
        float briefs = 0.0;
        if (vCloth > 0.5 && vRest.y < ${Bf.top.toFixed(2)} && vRest.y > bottom) {
          float rib = 0.93 + 0.07 * sin(vRest.x * 1.6) * sin(vRest.y * 1.6); briefs = 1.0;
          diffuseColor.rgb = vec3(0.035, 0.038, 0.045) * rib;
          if (vRest.y > ${Bf.top.toFixed(2)} - 14.0) diffuseColor.rgb = vec3(0.06, 0.065, 0.075);
        }`)
      .replace('#include <roughnessmap_fragment>', `#include <roughnessmap_fragment>
        roughnessFactor *= 0.9 + 0.2 * vnoise(vRest * 0.5 + 11.0);
        roughnessFactor = mix(roughnessFactor, 0.36, lipM); roughnessFactor = mix(roughnessFactor, 0.62, max(hairM, bro));
        roughnessFactor = mix(roughnessFactor, 0.7, briefs);`)
      .replace('#include <normal_fragment_maps>', `#include <normal_fragment_maps>
        { float fw = length(fwidth(vRest));                                               // mm per pixel
          float pore = vnoise(vRest * 1.7) + 0.5 * vnoise(vRest * 3.9);
          float strand = vnoise(vRest * vec3(2.4, 0.7, 2.4));
          float h = (1.0 - hairM) * (1.0 - briefs) * pore * 0.05 * (1.0 - smoothstep(0.2, 0.55, fw)) + hairM * strand * 0.3 * (1.0 - smoothstep(0.5, 1.3, fw));
          normal = bumpN(normal, -vViewPosition, h * 0.001); }`)
      .replace('#include <lights_physical_fragment>', `#include <lights_physical_fragment>
        #ifdef USE_SHEEN
        material.sheenColor *= 1.0 - 0.9 * max(hairM, bro);
        #endif
        #ifdef USE_CLEARCOAT
        material.clearcoat *= 1.0 - max(hairM, briefs);
        #endif
        material.specularF90 = mix(material.specularF90, 0.55, hairM);`)
      .replace('#include <lights_fragment_end>', `#include <lights_fragment_end>
        #if NUM_DIR_LIGHTS > 0
        { vec3 Ld = directionalLights[0].direction; float ndl = dot(normal, Ld); float wr = clamp((ndl + 0.45) / 1.45, 0.0, 1.0);
          float sss = max(0.0, wr * wr - max(ndl, 0.0)) * (1.0 - hairM) * (1.0 - briefs);
          reflectedLight.directDiffuse += sss * directionalLights[0].color * diffuseColor.rgb * vec3(0.95, 0.42, 0.32) * 0.85; }
        #endif
        reflectedLight.indirectDiffuse *= mix(vec3(1.0), vec3(1.04, 0.97, 0.95), 1.0 - briefs);`);
    if (xray) sh.fragmentShader = sh.fragmentShader.replace('#include <dithering_fragment>',
      '#include <dithering_fragment>\n float fr = pow(1.0 - abs(dot(normalize(vNormal), normalize(vViewPosition))), 2.0);\n gl_FragColor.a = clamp(0.12 + 0.75 * fr, 0.0, 0.9);');
  };
  mat.skin.onBeforeCompile = sh => skinChunk(sh, false);
  const skinX = mat.skin.clone(); skinX.side = THREE.FrontSide; skinX.transparent = true; skinX.depthWrite = false; skinX.opacity = 0.22;
  skinX.onBeforeCompile = sh => skinChunk(sh, true);
  // ---- eyes: wet cornea, iris with radial fibres and limbal ring, pupil; gaze slightly converging and down
  mat.eye.onBeforeCompile = sh => {
    sh.uniforms.uEye = { value: eyes }; sh.uniforms.uGaze = { value: gaze };
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying vec3 vRestE;').replace('#include <begin_vertex>', '#include <begin_vertex>\nvRestE = position;');
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', `#include <common>\nuniform vec4 uEye[2]; uniform vec3 uGaze[2]; varying vec3 vRestE;\n${NOISE}`)
      .replace('#include <color_fragment>', `#include <color_fragment>
        int k = distance(vRestE, uEye[0].xyz) < distance(vRestE, uEye[1].xyz) ? 0 : 1;
        vec3 c = k == 0 ? uEye[0].xyz : uEye[1].xyz; float R = k == 0 ? uEye[0].w : uEye[1].w; vec3 g = k == 0 ? uGaze[0] : uGaze[1];
        vec3 dir = normalize(vRestE - c); float ca = dot(dir, g), rr = R * sqrt(max(0.0, 1.0 - ca * ca)) * 12.0 / R;   // mm on a 12 mm eye
        vec3 e1 = normalize(cross(g, vec3(0.0, 1.0, 0.0))), e2 = cross(e1, g); float phi = atan(dot(dir, e2), dot(dir, e1));
        vec3 col = mix(vec3(0.93, 0.91, 0.88), vec3(0.88, 0.74, 0.70), 0.55 * smoothstep(0.75, 0.2, ca));          // sclera, pinker to the corners
        if (ca > 0.0) {
          float fib = 0.5 + 0.5 * sin(phi * 41.0 + 5.0 * vnoise(vec3(phi * 3.0, rr, 1.0))), fib2 = vnoise(vec3(phi * 9.0, rr * 2.0, 4.0));
          vec3 iris = mix(vec3(0.17, 0.10, 0.055), vec3(0.42, 0.29, 0.15), smoothstep(5.6, 2.4, rr)) * (0.72 + 0.28 * fib + 0.2 * fib2);
          iris = mix(iris, vec3(0.05, 0.035, 0.028), smoothstep(4.9, 5.85, rr));                                    // limbal ring
          col = mix(col, iris, 1.0 - smoothstep(5.65, 6.05, rr));
          col = mix(col, vec3(0.012, 0.01, 0.01), 1.0 - smoothstep(1.75, 2.0, rr));                                 // pupil
        }
        diffuseColor.rgb = col;`)
      .replace('#include <roughnessmap_fragment>', '#include <roughnessmap_fragment>\n        roughnessFactor = mix(roughnessFactor, 0.06, 1.0 - smoothstep(5.8, 6.4, rr));');
  };

  const groups = { bone: [], muscle: [], cartilage: [], skin: [], eye: [] };
  const segMeshes = [[], [], [], [], []];                                         // rigid parts per segment
  const dynamic = [];                                                              // skinned parts (CPU)
  const byPart = [];                                                               // part index -> dynamic entry
  // forearm twist: 0 at the elbow, 1 at the wrist and beyond (pronation is shared out along the forearm)
  const ua = sub(L.radial_head, L.ulnar_head), uu = ua[0] ** 2 + ua[1] ** 2 + ua[2] ** 2;
  const twistOf = (x, y, z) => { const al = ((x - L.ulnar_head[0]) * ua[0] + (y - L.ulnar_head[1]) * ua[1] + (z - L.ulnar_head[2]) * ua[2]) / uu;
    const t = Math.max(0, Math.min(1, 1.1 - al)); return t * t * (3 - 2 * t); };
  let hue = 0;
  const allParts = J.parts.concat(J.extra_parts || []);                          // extra: eyeballs (static, thorax)
  for (let pi = 0; pi < allParts.length; pi++) {
    const p = allParts[pi];
    let pos = new Float32Array(b64(p.pos, Int16Array)).map(v => v / 10);
    let idx = p.i32 ? b64(p.idx, Uint32Array) : b64(p.idx, Uint16Array);
    let n = p.n, keep = null;
    if (p.cls === 'skin' && p.rpos) {                                             // render mesh (outer shell + axilla pocket + full-res head)
      pos = new Float32Array(b64(p.rpos, Int16Array)).map(v => v / 10); idx = p.ri32 ? b64(p.ridx, Uint32Array) : b64(p.ridx, Uint16Array);
      keep = Array.from(b64(p.rsrc, Uint16Array), v => v === 65535 ? -1 : v); n = keep.length;   // legacy skin vertex (-1: new)
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setIndex(new THREE.BufferAttribute(idx, 1));
    if (p.cls === 'muscle') {                                                     // a slightly different red per muscle
      hue = (hue * 9301 + 49297) % 233280; const r = hue / 233280;
      const c = new THREE.Color().setHSL(0.995 + 0.02 * r, 0.62 + 0.12 * r, 0.30 + 0.07 * ((r * 7) % 1));
      const col = new Float32Array(n * 3); for (let i = 0; i < n; i++) col.set([c.r, c.g, c.b], 3 * i);
      g.setAttribute('color', new THREE.BufferAttribute(col, 3));
    }
    if (p.cls === 'skin') {                                                       // rest position + trunk mask: briefs cut in the shader
      const cloth = b64(p.cloth, Uint8Array), mask = new Float32Array(n);
      if (p.rcloth) { const rc = b64(p.rcloth, Uint8Array); for (let j = 0; j < n; j++) mask[j] = (rc[j >> 3] >> (7 - (j & 7))) & 1; }
      else for (let j = 0; j < n; j++) { const i = keep ? keep[j] : j; mask[j] = i < 0 ? 0 : (cloth[i >> 3] >> (7 - (i & 7))) & 1; }
      g.setAttribute('restPos', new THREE.BufferAttribute(pos.slice(), 3)); g.setAttribute('cloth', new THREE.BufferAttribute(mask, 1));
      const ft = new Float32Array(4 * n); if (p.feat) { const fb = b64(p.feat, Uint8Array); for (let k = 0; k < 4 * n; k++) ft[k] = fb[k] / 255; }
      g.setAttribute('feat', new THREE.BufferAttribute(ft, 4));
    }
    g.computeVertexNormals();
    const m = new THREE.Mesh(g, mat[p.cls]); m.name = p.name; m.frustumCulled = false; m.matrixAutoUpdate = false;
    groups[p.cls].push(m); root.add(m);
    if (p.wi || p.w4i) {
      const d = { mesh: m, rest: pos.slice(), n, name: p.name, cls: p.cls, axis: p.axis, base: new Float32Array(pos.length), tw: new Float32Array(n) };
      for (let i = 0; i < n; i++) d.tw[i] = twistOf(pos[3 * i], pos[3 * i + 1], pos[3 * i + 2]);
      if (p.w4i) {                                                                // centre-of-rotation skinning
        d.cor = true; d.wi = b64(p.w4i, Uint8Array); d.ww = b64(p.w4w, Uint8Array); d.c = new Float32Array(b64(p.cor, Int16Array)).map(v => v / 10);
        d.arch = p.arch || [0.4, 5, 0];
        if (p.mdl) initModel(d, p.mdl, p.belly ? b64(p.belly, Uint8Array) : null);
        if (p.foj) { d.foj = b64(p.foj, Uint8Array); d.fov = b64(p.fov, Uint16Array); d.fow = b64(p.fow, Uint8Array); }
        if (p.rlxi) { d.rlxi = b64(p.rlxi, Uint32Array); d.rlxd = new Float32Array(b64(p.rlxd, Int16Array)).map(v => v / 10); d.rest0 = d.rest.slice(); d.rlxA = 0; }
        if (p.rsm) d.rsm = b64(p.rsm, Uint32Array);
      } else {                                                                    // legacy linear blend (older body_mesh.json)
        d.wi = b64(p.wi, Uint8Array); d.ww = b64(p.ww, Uint8Array);
        if (p.belly) { d.belly = b64(p.belly, Uint8Array); d.arch = p.arch; d.sheet = !!p.sheet; d.rr = new Float32Array(b64(p.rr, Int16Array)).map(v => v / 10); }
        if (p.follow) { d.follow = b64(p.follow, Int32Array); d.followw = b64(p.followw, Uint8Array); }
      }
      dynamic.push(d); byPart[pi] = d;
    } else segMeshes[p.seg ?? 0].push(m);
  }
  const movingByIdx = J.moving.map(i => byPart[i]);
  const skin = groups.skin[0], skinDyn = dynamic.find(d => d.mesh === skin);
  const skinXMesh = new THREE.Mesh(skin.geometry, skinX); skinXMesh.frustumCulled = false; skinXMesh.matrixAutoUpdate = false; skinXMesh.renderOrder = 10; skinXMesh.visible = false; root.add(skinXMesh);
  const toM4 = A => new THREE.Matrix4().set(A.R[0][0], A.R[0][1], A.R[0][2], A.t[0], A.R[1][0], A.R[1][1], A.R[1][2], A.t[1], A.R[2][0], A.R[2][1], A.R[2][2], A.t[2], 0, 0, 0, 1);
  if (skinDyn.foj) initSkinBinding(skinDyn);
  if (skinDyn.cor) initMush(skinDyn);
  if (skinDyn.cor) {                                                               // humeral-head guard (see headGuard)
    const R = skinDyn.rest0 || skinDyn.rest, g = [], rm = [], lim = 38 * s;
    for (let i = 0; i < skinDyn.n; i++) { const r = Math.hypot(R[3 * i], R[3 * i + 1], R[3 * i + 2]); if (r < 160 * s) { g.push(i); rm.push(Math.min(r - 2, lim)); } }
    skinDyn.guard = Uint32Array.from(g); skinDyn.guardR = Float32Array.from(rm);
  }

  // ---------------------------------------------------------------- muscle models (precomputation)
  function meshVolume(P, I) { let v = 0; for (let f = 0; f < I.length; f += 3) { const a = 3 * I[f], b = 3 * I[f + 1], c = 3 * I[f + 2];
    v += P[a] * (P[b + 1] * P[c + 2] - P[b + 2] * P[c + 1]) - P[a + 1] * (P[b] * P[c + 2] - P[b + 2] * P[c]) + P[a + 2] * (P[b] * P[c + 1] - P[b + 1] * P[c]); } return v / 6; }
  // muscle volume is conserved exactly: whatever the blend and the shape model leave over or short is put back (or
  // taken off) as an even offset of the fleshy, superficial surface along its normal
  function volumeFix(d) {
    const P = d.mesh.geometry.attributes.position.array, I = d.mesh.geometry.index.array, n = d.n, W = d.vfixW;
    const N = d.vfN || (d.vfN = new Float32Array(3 * n)); N.fill(0); let v = 0;
    for (let f = 0; f < I.length; f += 3) { const a = 3 * I[f], b = 3 * I[f + 1], c = 3 * I[f + 2];
      v += P[a] * (P[b + 1] * P[c + 2] - P[b + 2] * P[c + 1]) - P[a + 1] * (P[b] * P[c + 2] - P[b + 2] * P[c]) + P[a + 2] * (P[b] * P[c + 1] - P[b + 1] * P[c]);
      const ux = P[b] - P[a], uy = P[b + 1] - P[a + 1], uz = P[b + 2] - P[a + 2], vx = P[c] - P[a], vy = P[c + 1] - P[a + 1], vz = P[c + 2] - P[a + 2];
      const nx = (uy * vz - uz * vy) / 6, ny = (uz * vx - ux * vz) / 6, nz = (ux * vy - uy * vx) / 6;   // area/3 weighted
      N[a] += nx; N[a + 1] += ny; N[a + 2] += nz; N[b] += nx; N[b + 1] += ny; N[b + 2] += nz; N[c] += nx; N[c + 1] += ny; N[c + 2] += nz; }
    v /= 6; let den = 0;                                                            // dV/d(offset) = sum w |N|
    for (let i = 0; i < n; i++) den += W[i] * Math.hypot(N[3 * i], N[3 * i + 1], N[3 * i + 2]);
    if (den < 1e-6) return 0;
    const del = Math.max(-6, Math.min(6, (d.V0 - v) / den)); d.vfix = del;
    for (let i = 0; i < n; i++) { const w = W[i] * del; if (!w) continue; const l = Math.hypot(N[3 * i], N[3 * i + 1], N[3 * i + 2]) || 1;
      P[3 * i] += w * N[3 * i] / l; P[3 * i + 1] += w * N[3 * i + 1] / l; P[3 * i + 2] += w * N[3 * i + 2] / l; }
    return Math.abs(d.V0 - v) / Math.abs(d.V0);
  }
  function initModel(d, M, p_belly) {
    const n = d.n, R = d.rest;
    if (M.type === 'sheet') {
      d.shm = { nrm: new Float32Array(b64(M.n, Int8Array)).map(v => v / 127), sup: b64(M.sup, Uint8Array), pf: b64(M.pf, Uint16Array), pb: b64(M.pb, Uint16Array),
        l0: new Float32Array(b64(M.l0, Uint16Array)).map(v => v / 10), th: new Float32Array(b64(M.th, Uint8Array)).map(v => v / 8), belly: null };
      d.q = new Float32Array(4 * n);                                               // per-vertex blended rotation (for the normal)
      d.vfixW = new Float32Array(n);
      for (let i = 0; i < n; i++) d.vfixW[i] = d.shm.sup[i] / 255;
      if (p_belly) for (let i = 0; i < n; i++) d.vfixW[i] *= p_belly[i] / 255;
      d.V0 = meshVolume(R, d.mesh.geometry.index.array);
      return;
    }
    const K = M.K, sk = M.sk, sr = b64(M.s, Uint16Array), x = new Float32Array(b64(M.x, Int16Array)).map(v => v / 10), mu = b64(M.mu, Uint8Array), kv = b64(M.k, Uint8Array);
    const f = { K, sk, L0: M.L0, C: M.C, E: M.E, phi: M.phi, NW: M.NW, RT: M.RT, x, mu, kv, s: new Float32Array(n), j: new Uint8Array(n), u: new Float32Array(n) };
    for (let i = 0; i < n; i++) { const si = sr[i] / 65535 * M.L0; f.s[i] = si; let j = 0; while (j < K - 2 && sk[j + 1] < si) j++; f.j[i] = j; f.u[i] = Math.max(0, Math.min(1, (si - sk[j]) / (sk[j + 1] - sk[j] + 1e-9))); }
    // rest slice centroids and node offsets from them; node twist
    f.cnt = new Float32Array(K); f.G = new Float32Array(3 * K);
    for (let i = 0; i < n; i++) { const k = kv[i]; f.cnt[k]++; for (let c = 0; c < 3; c++) f.G[3 * k + c] += R[3 * i + c]; }
    f.off = []; f.tw = []; for (let k = 0; k < K; k++) { const c = f.cnt[k] || 1; const G = [f.G[3 * k] / c, f.G[3 * k + 1] / c, f.G[3 * k + 2] / c];
      f.off.push(f.cnt[k] ? sub(M.C[k], G) : [0, 0, 0]); f.tw.push(twistOf(...M.C[k])); }
    let Phi = 0; for (let k = 0; k < K - 1; k++) Phi += 0.5 * (M.phi[k] + M.phi[k + 1]) * (sk[k + 1] - sk[k]);
    f.Phi = Phi; let be = K - 1; while (be > 0 && M.phi[be] < 0.05) be--; f.sBellyEnd = sk[be];
    f.biceps = /biceps brachii/.test(d.name); f.freeEnd = !!M.free_end;
    // bowstring beyond the free node: rest deviation of each distal node from the chord free node -> last node
    const [tau, fr, tauL] = M.taut || [0, 1, 0]; f.tau = tau; f.tauL = tauL ?? tau; f.kf = Math.min(K - 2, Math.max(1, Math.round(fr * (K - 1)))); f.dev = [];
    let arc = 0; for (let k = 0; k < f.kf; k++) arc += Math.hypot(...sub(M.C[k + 1], M.C[k]));
    f.ins = M.ins || [4, M.C[K - 1]];                                             // insertion on its bone (biceps: radial tuberosity)
    f.chordRes = M.L0 - arc - Math.hypot(...sub(f.ins[1], M.C[f.kf]));             // so the chord path equals L0 at rest
    // superficial / deep half-thickness of every slice (cross-sections are not symmetric about the centreline)
    f.eO = new Float32Array(K); f.eD = new Float32Array(K); const cO = new Float32Array(K), cD = new Float32Array(K);
    for (let i = 0; i < n; i++) { const k = kv[i], xe = x[3 * i + 1]; if (xe > 0) { f.eO[k] += xe; cO[k]++; } else { f.eD[k] -= xe; cD[k]++; } }
    for (let k = 0; k < K; k++) { f.eO[k] = cO[k] ? f.eO[k] / cO[k] : 1; f.eD[k] = cD[k] ? f.eD[k] / cD[k] : 1; }
    for (let k = 0; k < K; k++) { if (k <= f.kf) { f.dev.push([0, 0, 0]); continue; } const u = (sk[k] - sk[f.kf]) / (sk[K - 1] - sk[f.kf]);
      f.dev.push([0, 1, 2].map(c => M.C[k][c] - (M.C[f.kf][c] + u * (M.C[K - 1][c] - M.C[f.kf][c])))); }
    // work arrays
    f.cp = new Float32Array(3 * K); f.tp = new Float32Array(3 * K); f.ep = new Float32Array(3 * K); f.sc = new Float32Array(K); f.sn = new Float32Array(K);
    d.vfixW = new Float32Array(n);                                                  // volume fix on the fleshy, superficial side
    for (let i = 0; i < n; i++) { const j = f.j[i], u = f.u[i], ph = M.phi[j] + u * (M.phi[j + 1] - M.phi[j]); d.vfixW[i] = ph * (mu[i] / 255) * (x[3 * i + 1] > 0 ? 1 : 0.3); }
    d.V0 = meshVolume(R, d.mesh.geometry.index.array);
    f.aO = new Float32Array(K); f.aD = new Float32Array(K); f.aB = new Float32Array(K);
    d.fus = f;
  }

  // skin over the muscles: per bound vertex the muscle (and vertex) under it; spindle muscles get a height field
  function initSkinBinding(d) {
    // neighbour lists (outer shell) for a light smoothing of the bulge displacement
    const idx = d.mesh.geometry.index.array, n = d.n, deg = new Uint16Array(n);
    for (let f = 0; f < idx.length; f++) deg[idx[f]] += 2;
    const start = new Uint32Array(n + 1); for (let i = 0; i < n; i++) start[i + 1] = start[i] + deg[i];
    const nb = new Uint32Array(start[n]), fill = start.slice(0, n);
    for (let f = 0; f < idx.length; f += 3) for (let k = 0; k < 3; k++) { const a = idx[f + k], b = idx[f + (k + 1) % 3]; nb[fill[a]++] = b; nb[fill[b]++] = a; }
    d.nbStart = start; d.nb = nb; d.disp = new Float32Array(3 * n); d.disp2 = new Float32Array(3 * n);
    d.bound = []; for (let i = 0; i < n; i++) if (d.foj[i] !== 255 && d.fow[i]) d.bound.push(i);
    d.bound = Uint32Array.from(d.bound);
    d.region = new Uint8Array(n); for (const i of d.bound) d.region[i] = 1;
    // grow the region by two rings so the smoothing can feather the edge
    for (let r = 0; r < 2; r++) { const add_ = []; for (let i = 0; i < n; i++) if (d.region[i]) for (let k = start[i]; k < start[i + 1]; k++) if (!d.region[nb[k]]) add_.push(nb[k]); for (const i of add_) d.region[i] = 1; }
    d.regionList = []; for (let i = 0; i < n; i++) if (d.region[i]) d.regionList.push(i); d.regionList = Uint32Array.from(d.regionList);
    const rf = []; for (let f = 0; f < idx.length; f += 3) if (d.region[idx[f]] || d.region[idx[f + 1]] || d.region[idx[f + 2]]) rf.push(idx[f], idx[f + 1], idx[f + 2]);
    d.regionFaces = Uint32Array.from(rf);
  }

  // ---------------------------------------------------------------- per-frame
  let LIFT = [0, 0, 0];
  function update(pose, mode = 0, { girdle = true, act = null, segs: segsOverride = null, relax = null } = {}) {
    const { segs, lift } = segsOverride ? { segs: segsOverride, lift: [0, 0, 0] } : segmentTransforms(L, pose, { girdle, scale: s }); LIFT = lift;
    segMeshes.forEach((ms, k) => { const M4 = toM4(segs[k]); for (const m of ms) m.matrix.copy(M4); });
    // gravity load (0..1): shoulder muscles carry the arm; elbow flexors or the triceps carry the forearm, depending on
    // which way gravity turns it about the elbow axis; a little tone everywhere
    const arm = mv(segs[2].R, mv(T3(L.rest_humerus), [0, -1, 0]));
    const armLoad = Math.min(1, 1.1 * Math.sqrt(Math.max(0, 1 - arm[1] ** 2)));
    const fd = sub(L.ulnar_head, L.elbow), fore = mv(segs[3].R, sc(fd, 1 / Math.hypot(...fd))), eax = mv(segs[2].R, L.elbow_axis);
    const gm = (fore[1] * 0 - fore[2] * -1) * eax[0] + (fore[2] * 0 - fore[0] * 0) * eax[1] + (fore[0] * -1 - fore[1] * 0) * eax[2];   // (fore x down) . axis
    const foreLoad = Math.min(1, 1.3 * Math.sqrt(Math.max(0, 1 - fore[1] ** 2)));
    const ACT = act ? [0, act.shoulder ?? armLoad, act.flexor ?? 0, act.extensor ?? 0]
      : [0, armLoad, gm < 0 ? foreLoad : 0.1 * foreLoad, gm > 0 ? foreLoad : 0.1 * foreLoad];
    for (let k = 1; k < 4; k++) ACT[k] = Math.max(0.06, Math.min(1, ACT[k]));
    const Q = segs.map(A => quat(A.R)); Q[4] = Q[3];
    const rhP = apply(segs[3], L.radial_head), uhP = apply(segs[3], L.ulnar_head), tax = sub(rhP, uhP), tl = Math.hypot(...tax), th = (pose.pron + 90) * D2R;
    const kx = tax[0] / tl, ky = tax[1] / tl, kz = tax[2] / tl;
    const ctx = { segs, Q, rhP, kx, ky, kz, th, ACT, pose };
    // axilla: the flesh pressed into the arm-chest contact relaxes to its fair shape as the arm leaves the side
    if (skinDyn.rlxi) {
      const E = apply(segs[2], L.elbow), ang = Math.acos(Math.max(-1, Math.min(1, -E[1] / Math.hypot(...E)))) / D2R;
      const al = relax ?? smooth01(15, 55, ang);
      if (Math.abs(al - skinDyn.rlxA) > 1e-4) { const R0 = skinDyn.rest0, Rr = skinDyn.rest, ix = skinDyn.rlxi, dl = skinDyn.rlxd;
        for (let k = 0; k < ix.length; k++) { const i = 3 * ix[k]; Rr[i] = R0[i] + al * dl[3 * k]; Rr[i + 1] = R0[i + 1] + al * dl[3 * k + 1]; Rr[i + 2] = R0[i + 2] + al * dl[3 * k + 2]; }
        skinDyn.rlxA = al; }
    }
    for (const d of dynamic) {
      if (d.cor) skinCoR(d, ctx); else skinLBS(d, segs, rhP, kx, ky, kz, th, ACT);
      if (d.fus) fusiformModel(d, ctx); else if (d.shm) sheetModel(d, ctx);
      if (d.vfixW && volumeFix(d) > 0.015) volumeFix(d);                          // second pass for large changes
    }
    if (skinDyn.mush) deltaMush(skinDyn);
    if (skinDyn.cor && skinDyn.foj) skinFollow(skinDyn);
    else if (skinDyn.follow) {                                                    // legacy: the skin rides the nearest muscle's bulge
      const P = skin.geometry.attributes.position.array, F = skinDyn.follow, Fw = skinDyn.followw;
      for (let i = 0; i < Fw.length; i++) { const w = Fw[i] / 255; if (!w) continue;
        const m = movingByIdx[F[2 * i]]; if (!m) continue; const j = F[2 * i + 1], MP = m.mesh.geometry.attributes.position.array;
        for (let c = 0; c < 3; c++) P[3 * i + c] += w * (MP[3 * j + c] - m.base[3 * j + c]); }
    }
    if (skinDyn.guard) headGuard(skinDyn);
    for (const d of dynamic) { const g = d.mesh.geometry; g.attributes.position.needsUpdate = true; g.computeVertexNormals(); }
    // visibility by mode: 0 skin, 1 muscles + bones, 2 muscles seen through translucent skin
    skin.visible = mode === 0; skinXMesh.visible = mode === 2;
    for (const k of ['bone', 'muscle', 'cartilage']) for (const m of groups[k]) m.visible = mode !== 0;
  }

  // centre-of-rotation skinning, up to 4 influences; the radius + hand weight (4) turns with the ulna (3) and the
  // pronation is shared out along the forearm by the twist profile
  function skinCoR(d, { segs, Q, rhP, kx, ky, kz, th }) {
    const P = d.mesh.geometry.attributes.position.array, R = d.rest, C = d.c, n = d.n, wi = d.wi, ww = d.ww, B = d.base, Qv = d.q;
    for (let i = 0; i < n; i++) {
      const i4 = 4 * i, r0 = Q[wi[i4]];
      let qw = 0, qx = 0, qy = 0, qz = 0, cx = 0, cy = 0, cz = 0, fp = 0;
      const x = C[3 * i], y = C[3 * i + 1], z = C[3 * i + 2];
      for (let j = 0; j < 4; j++) {
        const w = ww[i4 + j]; if (!w) continue; const wf = w / 255, k = wi[i4 + j], q = Q[k], A = segs[k === 4 ? 3 : k];
        if (k >= 3) fp += wf;
        const sg = (q[0] * r0[0] + q[1] * r0[1] + q[2] * r0[2] + q[3] * r0[3]) < 0 ? -wf : wf;
        qw += sg * q[0]; qx += sg * q[1]; qy += sg * q[2]; qz += sg * q[3];
        cx += wf * (A.R[0][0] * x + A.R[0][1] * y + A.R[0][2] * z + A.t[0]); cy += wf * (A.R[1][0] * x + A.R[1][1] * y + A.R[1][2] * z + A.t[1]); cz += wf * (A.R[2][0] * x + A.R[2][1] * y + A.R[2][2] * z + A.t[2]);
      }
      const qn = 1 / Math.hypot(qw, qx, qy, qz); qw *= qn; qx *= qn; qy *= qn; qz *= qn;
      if (Qv) { Qv[i4] = qw; Qv[i4 + 1] = qx; Qv[i4 + 2] = qy; Qv[i4 + 3] = qz; }
      // v' = q (p - c) q*  (t = 2 q.xyz x v; v' = v + w t + q.xyz x t)
      const vx = R[3 * i] - x, vy = R[3 * i + 1] - y, vz = R[3 * i + 2] - z;
      const tx = 2 * (qy * vz - qz * vy), ty = 2 * (qz * vx - qx * vz), tz = 2 * (qx * vy - qy * vx);
      let px = cx + vx + qw * tx + (qy * tz - qz * ty), py = cy + vy + qw * ty + (qz * tx - qx * tz), pz = cz + vz + qw * tz + (qx * ty - qy * tx);
      const ang = th * d.tw[i] * fp;
      if (ang) {                                                            // Rodrigues about the pronation axis through the radial head
        const ux = px - rhP[0], uy = py - rhP[1], uz = pz - rhP[2], c = Math.cos(ang), s_ = Math.sin(ang), dk = (kx * ux + ky * uy + kz * uz) * (1 - c);
        px = rhP[0] + ux * c + (ky * uz - kz * uy) * s_ + kx * dk; py = rhP[1] + uy * c + (kz * ux - kx * uz) * s_ + ky * dk; pz = rhP[2] + uz * c + (kx * uy - ky * ux) * s_ + kz * dk;
        if (Qv) {                                                           // fold the twist into the stored rotation
          const h = ang / 2, sh = Math.sin(h), aw = Math.cos(h), ax = kx * sh, ay = ky * sh, az = kz * sh;
          const nw = aw * qw - ax * qx - ay * qy - az * qz, nx = aw * qx + ax * qw + ay * qz - az * qy, ny = aw * qy - ax * qz + ay * qw + az * qx, nz = aw * qz + ax * qy - ay * qx + az * qw;
          Qv[i4] = nw; Qv[i4 + 1] = nx; Qv[i4 + 2] = ny; Qv[i4 + 3] = nz;
        }
      }
      B[3 * i] = P[3 * i] = px; B[3 * i + 1] = P[3 * i + 1] = py; B[3 * i + 2] = P[3 * i + 2] = pz;
    }
  }

  // blended rotation of a weight vector (5 segments; 4 = radius/hand) applied to a direction, with the forearm twist
  function turn(Wv, v, tw, { Q, kx, ky, kz, th }) {
    let k0 = 0; for (let k = 1; k < 5; k++) if (Wv[k] > Wv[k0]) k0 = k;
    const r0 = Q[k0]; let qw = 0, qx = 0, qy = 0, qz = 0, fp = 0;
    for (let k = 0; k < 5; k++) { const w = Wv[k]; if (!w) continue; const q = Q[k]; if (k >= 3) fp += w;
      const sg = (q[0] * r0[0] + q[1] * r0[1] + q[2] * r0[2] + q[3] * r0[3]) < 0 ? -w : w; qw += sg * q[0]; qx += sg * q[1]; qy += sg * q[2]; qz += sg * q[3]; }
    const qn = 1 / Math.hypot(qw, qx, qy, qz); qw *= qn; qx *= qn; qy *= qn; qz *= qn;
    const tx = 2 * (qy * v[2] - qz * v[1]), ty = 2 * (qz * v[0] - qx * v[2]), tz = 2 * (qx * v[1] - qy * v[0]);
    let r = [v[0] + qw * tx + (qy * tz - qz * ty), v[1] + qw * ty + (qz * tx - qx * tz), v[2] + qw * tz + (qx * ty - qy * tx)];
    const ang = th * tw * fp;
    if (ang) { const c = Math.cos(ang), s_ = Math.sin(ang), dk = (kx * r[0] + ky * r[1] + kz * r[2]) * (1 - c);
      r = [r[0] * c + (ky * r[2] - kz * r[1]) * s_ + kx * dk, r[1] * c + (kz * r[0] - kx * r[2]) * s_ + ky * dk, r[2] * c + (kx * r[1] - ky * r[0]) * s_ + kz * dk]; }
    return r;
  }

  // spindle muscle: rebuild the vertices about the posed centreline (see header)
  function fusiformModel(d, ctx) {
    const f = d.fus, K = f.K, sk = f.sk, P = d.mesh.geometry.attributes.position.array, B = d.base, n = d.n;
    const a = ctx.ACT[d.arch[2]] || 0.06;
    // posed nodes: slice centroid of the CoR-posed vertices + the turned rest offset node - centroid
    const G = new Float32Array(3 * K);
    for (let i = 0; i < n; i++) { const k = f.kv[i]; G[3 * k] += B[3 * i]; G[3 * k + 1] += B[3 * i + 1]; G[3 * k + 2] += B[3 * i + 2]; }
    for (let k = 0; k < K; k++) {
      const c = f.cnt[k];
      const o = turn(f.NW[k], f.off[k], f.tw[k], ctx), e = turn(f.NW[k], f.E[k], f.tw[k], ctx);
      const base_ = c ? [G[3 * k] / c, G[3 * k + 1] / c, G[3 * k + 2] / c] : null;
      const cp = base_ ? add(base_, o) : null;
      if (cp) { f.cp[3 * k] = cp[0]; f.cp[3 * k + 1] = cp[1]; f.cp[3 * k + 2] = cp[2]; } else f.cp.fill(NaN, 3 * k, 3 * k + 3);
      f.ep[3 * k] = e[0]; f.ep[3 * k + 1] = e[1]; f.ep[3 * k + 2] = e[2];
    }
    for (let k = 0; k < K; k++) if (Number.isNaN(f.cp[3 * k])) {                // empty slice: interpolate
      let lo = k - 1, hi = k + 1; while (lo >= 0 && Number.isNaN(f.cp[3 * lo])) lo--; while (hi < K && Number.isNaN(f.cp[3 * hi])) hi++;
      for (let c = 0; c < 3; c++) f.cp[3 * k + c] = lo < 0 ? f.cp[3 * hi + c] : hi >= K ? f.cp[3 * lo + c] : f.cp[3 * lo + c] + (f.cp[3 * hi + c] - f.cp[3 * lo + c]) * (k - lo) / (hi - lo);
    }
    // path lengths before the chord blend: as the bones' blend wraps the joint, and as a bowstring beyond the free node
    let L1cor = 0, arcF = 0;
    for (let k = 1; k < K; k++) { const l = Math.hypot(f.cp[3 * k] - f.cp[3 * k - 3], f.cp[3 * k + 1] - f.cp[3 * k - 2], f.cp[3 * k + 2] - f.cp[3 * k - 1]); L1cor += l; if (k <= f.kf) arcF += l; }
    const Ip = apply(ctx.segs[f.ins[0]], f.ins[1]);
    const Lch = arcF + Math.hypot(Ip[0] - f.cp[3 * f.kf], Ip[1] - f.cp[3 * f.kf + 1], Ip[2] - f.cp[3 * f.kf + 2]) + f.chordRes;
    if (f.tau > 0) {                                                             // chord beyond the free node (+ turned rest deviation)
      const kf = f.kf, a3 = 3 * kf, b3 = 3 * (K - 1);
      for (let k = kf + 1; k < K - 1; k++) { const u = (sk[k] - sk[kf]) / (sk[K - 1] - sk[kf]), dv = turn(f.NW[k], f.dev[k], f.tw[k], ctx);
        for (let c = 0; c < 3; c++) { const t_ = f.cp[a3 + c] + u * (f.cp[b3 + c] - f.cp[a3 + c]) + dv[c]; f.cp[3 * k + c] += f.tau * (t_ - f.cp[3 * k + c]); } }
    }
    // tangents (central differences, as numpy.gradient), frames, posed arc lengths
    f.sc[0] = 0;
    for (let k = 0; k < K; k++) {
      const k0 = Math.max(0, k - 1), k1 = Math.min(K - 1, k + 1);
      let tx = f.cp[3 * k1] - f.cp[3 * k0], ty = f.cp[3 * k1 + 1] - f.cp[3 * k0 + 1], tz = f.cp[3 * k1 + 2] - f.cp[3 * k0 + 2]; const tn = Math.hypot(tx, ty, tz) || 1;
      tx /= tn; ty /= tn; tz /= tn; f.tp[3 * k] = tx; f.tp[3 * k + 1] = ty; f.tp[3 * k + 2] = tz;
      if (k) f.sc[k] = f.sc[k - 1] + Math.hypot(f.cp[3 * k] - f.cp[3 * k - 3], f.cp[3 * k + 1] - f.cp[3 * k - 2], f.cp[3 * k + 2] - f.cp[3 * k - 1]);
    }
    const L1 = f.sc[K - 1];
    // muscle-tendon length change: between the wrapped and the bowstring path (anatomical moment arm); the biceps'
    // distal tendon also winds round the radius in pronation (~5 mm/rad); tendons stretch a little under load
    const wrap = f.biceps ? 3 * s * Math.max(0, (ctx.pose.pron + 90) * D2R) : 0;
    const L1e = f.L0 + (1 - f.tauL) * (L1cor - f.L0) + f.tauL * (Lch - f.L0) + wrap, eps = 0.025 * a;
    const kap = (L1e - f.L0 - eps * (f.L0 - f.Phi)) / Math.max(1e-6, f.Phi);
    // the length change goes into the fleshy belly (phi); clamped stretch, any excess to the tendons
    let tot = 0;
    for (let k = 0; k < K; k++) { const g = 1 + kap * f.phi[k] + eps * (1 - f.phi[k]); f.sn[k] = Math.max(0.42, Math.min(1.9, g)); }
    for (let k = 0; k < K - 1; k++) tot += 0.5 * (f.sn[k] + f.sn[k + 1]) * (sk[k + 1] - sk[k]);
    const fix = (L1e - tot) / Math.max(1e-6, f.L0 - f.Phi);
    // each slice keeps its volume: area x 1/g, shared between thickness (A^gam) and width (A^(1-gam)); an active
    // muscle rounds up (more thickness, isometric firming); the deep side, on the bone or the next muscle, moves
    // little, so the extra thickness lifts the superficial side (the peak)
    const gam = 0.5 + 0.1 * a, firm = 1 + 0.06 * a;
    for (let k = 0; k < K; k++) {
      const g = f.sn[k] + fix * (1 - f.phi[k]); f.sn[k] = g;
      const A = 1 / g, fk = f.phi[k] > 0 ? firm : 1, t = Math.pow(A, gam) * fk, w = Math.pow(A, 1 - gam) / fk;
      const aD = 1 + 0.3 * (t - 1), eO = f.eO[k], eD = f.eD[k];
      f.aB[k] = w; f.aD[k] = aD; f.aO[k] = Math.max(0.3, (t * (eO + eD) - aD * eD) / eO);
    }
    // new arc length of every node (cumulative), then the distal tendon absorbs the winding
    const sN = new Float32Array(K); sN[0] = 0; for (let k = 1; k < K; k++) sN[k] = sN[k - 1] + 0.5 * (f.sn[k - 1] + f.sn[k]) * (sk[k] - sk[k - 1]);
    const endFix = f.freeEnd ? 0 : L1 - sN[K - 1];                                // a free end (short head) retracts with the belly
    for (let k = 0; k < K; k++) sN[k] += endFix * smooth01(f.sBellyEnd, f.L0, sk[k]) + (k === K - 1 ? 0 : 0);
    // vertices
    const x = f.x;
    for (let i = 0; i < n; i++) {
      const mu = f.freeEnd && f.s[i] > 0.5 * f.L0 ? 1 : f.mu[i] / 255; if (!mu) continue;
      const j = f.j[i], u = f.u[i];
      const sig = sN[j] + u * (sN[j + 1] - sN[j]);
      let m = Math.min(K - 2, j); while (m > 0 && f.sc[m] > sig) m--; while (m < K - 2 && f.sc[m + 1] < sig) m++;
      const v = Math.max(0, Math.min(1, (sig - f.sc[m]) / (f.sc[m + 1] - f.sc[m] + 1e-9))), m3 = 3 * m;
      const cx = f.cp[m3] + v * (f.cp[m3 + 3] - f.cp[m3]), cy = f.cp[m3 + 1] + v * (f.cp[m3 + 4] - f.cp[m3 + 1]), cz = f.cp[m3 + 2] + v * (f.cp[m3 + 5] - f.cp[m3 + 2]);
      let tx = f.tp[m3] + v * (f.tp[m3 + 3] - f.tp[m3]), ty = f.tp[m3 + 1] + v * (f.tp[m3 + 4] - f.tp[m3 + 1]), tz = f.tp[m3 + 2] + v * (f.tp[m3 + 5] - f.tp[m3 + 2]);
      let tn = Math.hypot(tx, ty, tz); tx /= tn; ty /= tn; tz /= tn;
      let ex = f.ep[m3] + v * (f.ep[m3 + 3] - f.ep[m3]), ey = f.ep[m3 + 1] + v * (f.ep[m3 + 4] - f.ep[m3 + 1]), ez = f.ep[m3 + 2] + v * (f.ep[m3 + 5] - f.ep[m3 + 2]);
      const de = ex * tx + ey * ty + ez * tz; ex -= de * tx; ey -= de * ty; ez -= de * tz; tn = Math.hypot(ex, ey, ez); ex /= tn; ey /= tn; ez /= tn;
      const bx = ty * ez - tz * ey, by = tz * ex - tx * ez, bz = tx * ey - ty * ex;
      const xt = x[3 * i], xe = x[3 * i + 1], xb = x[3 * i + 2];
      const aO = f.aO[j] + u * (f.aO[j + 1] - f.aO[j]), aD = f.aD[j] + u * (f.aD[j + 1] - f.aD[j]), aB = f.aB[j] + u * (f.aB[j + 1] - f.aB[j]);
      const se = xe * (xe > 0 ? aO : aD), sb = xb * aB;
      const px = cx + xt * tx + se * ex + sb * bx, py = cy + xt * ty + se * ey + sb * by, pz = cz + xt * tz + se * ez + sb * bz;
      P[3 * i] = B[3 * i] + mu * (px - B[3 * i]); P[3 * i + 1] = B[3 * i + 1] + mu * (py - B[3 * i + 1]); P[3 * i + 2] = B[3 * i + 2] + mu * (pz - B[3 * i + 2]);
    }
    f.L1 = L1e; f.L1cor = L1cor; f.Lch = Lch; f.kap = kap; f.act = a; f.sN = sN;
  }

  // flat muscle: superficial face moves out with the local fibre stretch (pennate fibres turn: cos^2 of the angle)
  function sheetModel(d, ctx) {
    const S_ = d.shm, P = d.mesh.geometry.attributes.position.array, B = d.base, n = d.n, Qv = d.q;
    const a = ctx.ACT[d.arch[2]] || 0.06, ca = Math.cos(d.arch[1] * D2R) ** 2;
    for (let i = 0; i < n; i++) {
      const sup = S_.sup[i] / 255; if (!sup) continue;
      const f_ = S_.pf[i], b_ = S_.pb[i]; if (f_ === b_) continue;
      const lam = Math.max(0.5, Math.min(1.8, Math.hypot(B[3 * f_] - B[3 * b_], B[3 * f_ + 1] - B[3 * b_ + 1], B[3 * f_ + 2] - B[3 * b_ + 2]) / S_.l0[i]));
      const k = sup * S_.th[i] * ((Math.pow(lam, -0.8 * ca) - 1) + 0.05 * a);
      if (!k) continue;
      const i4 = 4 * i, qw = Qv[i4], qx = Qv[i4 + 1], qy = Qv[i4 + 2], qz = Qv[i4 + 3];
      const vx = S_.nrm[3 * i], vy = S_.nrm[3 * i + 1], vz = S_.nrm[3 * i + 2];
      const tx = 2 * (qy * vz - qz * vy), ty = 2 * (qz * vx - qx * vz), tz = 2 * (qx * vy - qy * vx);
      P[3 * i] += k * (vx + qw * tx + (qy * tz - qz * ty)); P[3 * i + 1] += k * (vy + qw * ty + (qz * tx - qx * tz)); P[3 * i + 2] += k * (vz + qw * tz + (qx * ty - qy * tx));
    }
  }

  // Delta Mush (Mancewicz et al. 2014) over the blended joints (shoulder, axilla, elbow): the skinned mesh is smoothed
  // and the rest-pose detail is added back in local frames, which irons out the folds and pinches of the blend zones
  // while keeping the anatomy. The rest detail is taken from both the rest and the relaxed axilla shape (blended).
  function initMush(d) {
    const n = d.n, idx = d.mesh.geometry.index.array;
    if (!d.nbStart) {                                                            // neighbour lists
      const deg = new Uint16Array(n); for (let f = 0; f < idx.length; f++) deg[idx[f]] += 2;
      const start = new Uint32Array(n + 1); for (let i = 0; i < n; i++) start[i + 1] = start[i] + deg[i];
      const nb = new Uint32Array(start[n]), fill = start.slice(0, n);
      for (let f = 0; f < idx.length; f += 3) for (let k = 0; k < 3; k++) { const a = idx[f + k], b = idx[f + (k + 1) % 3]; nb[fill[a]++] = b; nb[fill[b]++] = a; }
      d.nbStart = start; d.nb = nb;
    }
    const st = d.nbStart, nb = d.nb;
    // core: vertices whose weights are blended; then three rings of feathering
    const ring = new Int8Array(n).fill(-1);
    for (let i = 0; i < n; i++) { let mx = 0; for (let j = 0; j < 4; j++) mx = Math.max(mx, d.ww[4 * i + j]); if (mx < 248) ring[i] = 0; }
    if (d.rlxi) for (const i of d.rlxi) ring[i] = 0;
    if (d.rsm) for (const i of d.rsm) ring[i] = 0;
    for (let r = 1; r <= 4; r++) for (let i = 0; i < n; i++) if (ring[i] === r - 1) for (let k = st[i]; k < st[i + 1]; k++) if (ring[nb[k]] < 0) ring[nb[k]] = r;
    const list = []; for (let i = 0; i < n; i++) if (ring[i] >= 0 && ring[i] < 4) list.push(i);   // ring 4 = fixed boundary
    const L_ = Uint32Array.from(list), amt = new Float32Array(n); for (const i of L_) amt[i] = ring[i] <= 1 ? 1 : ring[i] === 2 ? 0.66 : 0.33;
    const faces = []; const inR = new Uint8Array(n); for (const i of L_) inR[i] = 1;
    for (let f = 0; f < idx.length; f += 3) if (inR[idx[f]] || inR[idx[f + 1]] || inR[idx[f + 2]]) faces.push(idx[f], idx[f + 1], idx[f + 2]);
    d.mush = { list: L_, amt, faces: Uint32Array.from(faces), S: new Float32Array(3 * n), T: new Float32Array(3 * n), N: new Float32Array(3 * n), C0: null, C1: null };
    const rest1 = d.rest0 ? d.rest0.slice() : d.rest.slice();
    if (d.rlxi) for (let k = 0; k < d.rlxi.length; k++) { const i = 3 * d.rlxi[k]; for (let c = 0; c < 3; c++) rest1[i + c] += d.rlxd[3 * k + c]; }
    d.mush.C0 = mushCoeffs(d, d.rest0 || d.rest); d.mush.C1 = d.rlxi ? mushCoeffs(d, rest1) : d.mush.C0;
    if (d.rlxi) { const all = [...d.rlxi, ...(d.rsm || [])];
      for (const i of all) d.mush.C1[3 * i] = d.mush.C1[3 * i + 1] = d.mush.C1[3 * i + 2] = 0;   // relaxed axilla: no creases kept
      d.mush.relaxList = Uint32Array.from([...new Set(all)].filter(i => inR[i])); }
  }
  function smoothPass(S, T, L_, st, nb, iters) {
    for (let it = 0; it < iters; it++) {
      for (let q = 0; q < L_.length; q++) { const i = L_[q]; let x = 0, y = 0, z = 0; const c = st[i + 1] - st[i];
        for (let k = st[i]; k < st[i + 1]; k++) { const j = 3 * nb[k]; x += S[j]; y += S[j + 1]; z += S[j + 2]; }
        T[3 * i] = 0.5 * S[3 * i] + 0.5 * x / c; T[3 * i + 1] = 0.5 * S[3 * i + 1] + 0.5 * y / c; T[3 * i + 2] = 0.5 * S[3 * i + 2] + 0.5 * z / c; }
      for (let q = 0; q < L_.length; q++) { const i = 3 * L_[q]; S[i] = T[i]; S[i + 1] = T[i + 1]; S[i + 2] = T[i + 2]; }
    }
  }
  function mushSmooth(d, P, al = 0) {                                           // -> d.mush.S (smoothed), N (normals)
    const M = d.mush, S = M.S, T = M.T, st = d.nbStart, nb = d.nb, L_ = M.list;
    S.set(P);
    smoothPass(S, T, L_, st, nb, MUSH_IT);
    // the relaxed axilla (no creases kept) is ironed further, more as the arm leaves the side
    if (al > 0 && M.relaxList) smoothPass(S, T, M.relaxList, st, nb, Math.round(30 * al));
    const N = M.N, F = M.faces; for (const i of L_) N[3 * i] = N[3 * i + 1] = N[3 * i + 2] = 0;
    for (let f = 0; f < F.length; f += 3) { const a = 3 * F[f], b = 3 * F[f + 1], c = 3 * F[f + 2];
      const ux = S[b] - S[a], uy = S[b + 1] - S[a + 1], uz = S[b + 2] - S[a + 2], vx = S[c] - S[a], vy = S[c + 1] - S[a + 1], vz = S[c + 2] - S[a + 2];
      const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
      N[a] += nx; N[a + 1] += ny; N[a + 2] += nz; N[b] += nx; N[b + 1] += ny; N[b + 2] += nz; N[c] += nx; N[c + 1] += ny; N[c + 2] += nz; }
  }
  function mushFrame(d, i, S, N) {                                              // orthonormal frame at the smoothed vertex -> FR
    let nx = N[3 * i], ny = N[3 * i + 1], nz = N[3 * i + 2]; const nn = Math.sqrt(nx * nx + ny * ny + nz * nz) || 1; nx /= nn; ny /= nn; nz /= nn;
    const j = 3 * d.nb[d.nbStart[i]]; let tx = S[j] - S[3 * i], ty = S[j + 1] - S[3 * i + 1], tz = S[j + 2] - S[3 * i + 2];
    const dn = tx * nx + ty * ny + tz * nz; tx -= dn * nx; ty -= dn * ny; tz -= dn * nz; const tn = Math.sqrt(tx * tx + ty * ty + tz * tz) || 1; tx /= tn; ty /= tn; tz /= tn;
    FR[0] = tx; FR[1] = ty; FR[2] = tz; FR[3] = ny * tz - nz * ty; FR[4] = nz * tx - nx * tz; FR[5] = nx * ty - ny * tx; FR[6] = nx; FR[7] = ny; FR[8] = nz; return FR;
  }
  function mushCoeffs(d, R) {
    mushSmooth(d, R); const M = d.mush, S = M.S, N = M.N, C = new Float32Array(3 * d.n);
    for (const i of M.list) { const f = mushFrame(d, i, S, N), dx = R[3 * i] - S[3 * i], dy = R[3 * i + 1] - S[3 * i + 1], dz = R[3 * i + 2] - S[3 * i + 2];
      C[3 * i] = dx * f[0] + dy * f[1] + dz * f[2]; C[3 * i + 1] = dx * f[3] + dy * f[4] + dz * f[5]; C[3 * i + 2] = dx * f[6] + dy * f[7] + dz * f[8]; }
    return C;
  }
  function deltaMush(d) {
    const P = d.mesh.geometry.attributes.position.array, M = d.mush, B = d.base, al = d.rlxA || 0, C0 = M.C0, C1 = M.C1;
    mushSmooth(d, P, al); const S = M.S, N = M.N;
    for (const i of M.list) {
      const f = mushFrame(d, i, S, N), i3 = 3 * i, a = M.amt[i];
      const c0 = C0[i3] + al * (C1[i3] - C0[i3]), c1 = C0[i3 + 1] + al * (C1[i3 + 1] - C0[i3 + 1]), c2 = C0[i3 + 2] + al * (C1[i3 + 2] - C0[i3 + 2]);
      for (let c = 0; c < 3; c++) { const q = S[i3 + c] + c0 * f[c] + c1 * f[3 + c] + c2 * f[6 + c]; P[i3 + c] += a * (q - P[i3 + c]); B[i3 + c] = P[i3 + c]; }
    }
  }

  // no skin closer to the shoulder centre than it starts (or ~4 cm): the humeral head is there. A soft floor on the
  // distance from the GH centre (r' = r above rmin + w, rmin + w exp((r - rmin) / w - 1) below), so the axillary skin
  // stretched over the head at full elevation cannot sink into it
  function headGuard(d) {
    const P = d.mesh.geometry.attributes.position.array, G = d.guard, RM = d.guardR, w = 4 * s;
    for (let k = 0; k < G.length; k++) { const i3 = 3 * G[k], r = Math.hypot(P[i3], P[i3 + 1], P[i3 + 2]), rmin = RM[k];
      if (r >= rmin + w || r < 1e-6) continue; const f = (rmin + w * Math.exp((r - rmin) / w - 1)) / r;
      P[i3] *= f; P[i3 + 1] *= f; P[i3 + 2] *= f; }
  }

  // skin rides the shape change of the muscle under it: a scalar height change along the skin normal, smoothed over
  // the skin. Over a spindle muscle it is the change of the muscle's surface radius at the skin's own place (the belly
  // slides under the skin rather than dragging it); over a flat muscle the normal part of its thickness change.
  function rtAt(f, s, th) {                                                     // rest radius table, bilinear (node x 16 angles)
    const K = f.K, sk = f.sk; let k = 0; while (k < K - 2 && sk[k + 1] < s) k++;
    const u = Math.max(0, Math.min(1, (s - sk[k]) / (sk[k + 1] - sk[k] + 1e-9)));
    const a = ((th + Math.PI) / (2 * Math.PI)) * 16 - 0.5, a0 = Math.floor(a), v = a - a0, j0 = ((a0 % 16) + 16) % 16, j1 = (j0 + 1) % 16;
    const R0 = f.RT[k], R1 = f.RT[k + 1];
    return (1 - u) * ((1 - v) * R0[j0] + v * R0[j1]) + u * ((1 - v) * R1[j0] + v * R1[j1]);
  }
  function lerpAt(xs, ys, x) { const n = xs.length; if (x <= xs[0]) return ys[0]; if (x >= xs[n - 1]) return ys[n - 1];
    let k = 0; while (k < n - 2 && xs[k + 1] < x) k++; const u = (x - xs[k]) / (xs[k + 1] - xs[k] + 1e-9); return ys[k] + u * (ys[k + 1] - ys[k]); }
  function skinFollow(d) {
    const P = d.mesh.geometry.attributes.position.array, H = d.hgt || (d.hgt = new Float32Array(d.n)), H2 = d.hgt2 || (d.hgt2 = new Float32Array(d.n));
    for (const i of d.regionList) H[i] = 0;
    for (const i of d.bound) {
      const m = movingByIdx[d.foj[i]]; if (!m) continue; const j = d.fov[i], w = d.fow[i] / 255;
      let h = 0;
      if (m.fus && m.fus.sN) {
        const f = m.fus, sj = f.s[j], xe = f.x[3 * j + 1], xb = f.x[3 * j + 2], th = Math.atan2(xb, xe);
        const sig = lerpAt(f.sk, f.sc, sj), sst = lerpAt(f.sN, f.sk, sig);       // rest slice now under the skin
        const es = xe > 0 ? lerpAt(f.sk, f.aO, sst) : lerpAt(f.sk, f.aD, sst), bs = lerpAt(f.sk, f.aB, sst);
        const c = Math.cos(th), s_ = Math.sin(th);
        h = rtAt(f, sst, th) * Math.hypot(es * c, bs * s_) - rtAt(f, sj, th);
        h *= f.mu[j] / 255;
      } else if (m.shm && m.q) {
        const MP = m.mesh.geometry.attributes.position.array, MB = m.base, Q = m.q, nr = m.shm.nrm, j4 = 4 * j;
        const qw = Q[j4], qx = Q[j4 + 1], qy = Q[j4 + 2], qz = Q[j4 + 3], vx = nr[3 * j], vy = nr[3 * j + 1], vz = nr[3 * j + 2];
        const tx = 2 * (qy * vz - qz * vy), ty = 2 * (qz * vx - qx * vz), tz = 2 * (qx * vy - qy * vx);
        const nx = vx + qw * tx + (qy * tz - qz * ty), ny = vy + qw * ty + (qz * tx - qx * tz), nz = vz + qw * tz + (qx * ty - qy * tx);
        h = (MP[3 * j] - MB[3 * j]) * nx + (MP[3 * j + 1] - MB[3 * j + 1]) * ny + (MP[3 * j + 2] - MB[3 * j + 2]) * nz;
      }
      H[i] = w * h;
    }
    const st = d.nbStart, nb = d.nb, R = d.regionList;
    for (let it = 0; it < 4; it++) {
      for (let q = 0; q < R.length; q++) { const i = R[q]; let x = 0; for (let k = st[i]; k < st[i + 1]; k++) x += H[nb[k]]; H2[i] = 0.5 * H[i] + 0.5 * x / (st[i + 1] - st[i]); }
      for (let q = 0; q < R.length; q++) H[R[q]] = H2[R[q]];
    }
    // posed skin normals over the region
    const N = d.fnrm || (d.fnrm = new Float32Array(3 * d.n)), F = d.regionFaces;
    for (let q = 0; q < R.length; q++) { const i = 3 * R[q]; N[i] = N[i + 1] = N[i + 2] = 0; }
    for (let f = 0; f < F.length; f += 3) { const a = 3 * F[f], b = 3 * F[f + 1], c = 3 * F[f + 2];
      const ux = P[b] - P[a], uy = P[b + 1] - P[a + 1], uz = P[b + 2] - P[a + 2], vx = P[c] - P[a], vy = P[c + 1] - P[a + 1], vz = P[c + 2] - P[a + 2];
      const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
      N[a] += nx; N[a + 1] += ny; N[a + 2] += nz; N[b] += nx; N[b + 1] += ny; N[b + 2] += nz; N[c] += nx; N[c + 1] += ny; N[c + 2] += nz; }
    for (let q = 0; q < R.length; q++) { const i = R[q], h = H[i]; if (!h) continue; const i3 = 3 * i, l = Math.hypot(N[i3], N[i3 + 1], N[i3 + 2]) || 1;
      P[i3] += h * N[i3] / l; P[i3 + 1] += h * N[i3 + 1] / l; P[i3 + 2] += h * N[i3 + 2] / l; }
  }

  // legacy linear-blend skinning + bulge (for body_mesh.json files built before the centre-of-rotation rig)
  function skinLBS(d, segs, rhP, kx, ky, kz, th, ACT) {
    const P = d.mesh.geometry.attributes.position.array, R = d.rest, n = d.n, W = d.base;
    for (let i = 0; i < n; i++) {
      const ia = d.wi[2 * i], ib = d.wi[2 * i + 1], w = d.ww[i] / 255, x = R[3 * i], y = R[3 * i + 1], z = R[3 * i + 2];
      const a = segs[ia === 4 ? 3 : ia], b = segs[ib === 4 ? 3 : ib];
      const q = (ia >= 3 ? w : 0) + (ib >= 3 ? 1 - w : 0);
      const ax = a.R[0][0] * x + a.R[0][1] * y + a.R[0][2] * z + a.t[0], ay = a.R[1][0] * x + a.R[1][1] * y + a.R[1][2] * z + a.t[1], az = a.R[2][0] * x + a.R[2][1] * y + a.R[2][2] * z + a.t[2];
      const bx = b.R[0][0] * x + b.R[0][1] * y + b.R[0][2] * z + b.t[0], by = b.R[1][0] * x + b.R[1][1] * y + b.R[1][2] * z + b.t[1], bz = b.R[2][0] * x + b.R[2][1] * y + b.R[2][2] * z + b.t[2];
      let px = w * ax + (1 - w) * bx, py = w * ay + (1 - w) * by, pz = w * az + (1 - w) * bz;
      const ang = th * d.tw[i] * q;
      if (ang) {
        const vx = px - rhP[0], vy = py - rhP[1], vz = pz - rhP[2], c = Math.cos(ang), s_ = Math.sin(ang), dk = (kx * vx + ky * vy + kz * vz) * (1 - c);
        px = rhP[0] + vx * c + (ky * vz - kz * vy) * s_ + kx * dk; py = rhP[1] + vy * c + (kz * vx - kx * vz) * s_ + ky * dk; pz = rhP[2] + vz * c + (kx * vy - ky * vx) * s_ + kz * dk;
      }
      W[3 * i] = P[3 * i] = px; W[3 * i + 1] = P[3 * i + 1] = py; W[3 * i + 2] = P[3 * i + 2] = pz;
    }
    if (d.axis && d.belly) {
      const [sa, oa, sb, ib] = d.axis, u = sub(apply(segs[sb], ib), apply(segs[sa], oa));
      const L0 = Math.hypot(...sub(ib, oa)), L1 = Math.hypot(...u), [tau, alpha, grp] = d.arch;
      const lam = Math.max(0.55, Math.min(1.5, 1 + (L1 / L0 - 1) / (1 - tau)));
      const k = ((d.sheet ? 1 / lam : 1 / Math.sqrt(lam)) - 1) * Math.cos(alpha * D2R) ** 2 + 0.04 * ACT[grp];
      for (let i = 0; i < n; i++) {
        const f = k * d.belly[i] / 255; if (!f) continue;
        const ia = d.wi[2 * i], ib2 = d.wi[2 * i + 1], w = d.ww[i] / 255, A = segs[ia === 4 ? 3 : ia].R, Bm = segs[ib2 === 4 ? 3 : ib2].R;
        const x = d.rr[3 * i], y = d.rr[3 * i + 1], z = d.rr[3 * i + 2];
        for (let c = 0; c < 3; c++) P[3 * i + c] += f * (w * (A[c][0] * x + A[c][1] * y + A[c][2] * z) + (1 - w) * (Bm[c][0] * x + Bm[c][1] * y + Bm[c][2] * z));
      }
    }
  }
  function setFrame(worldFromThorax) { root.matrix.copy(worldFromThorax); root.matrixWorldNeedsUpdate = true; }
  return { group: root, update, setFrame, get lift() { return LIFT; }, landmarks: L, scale: s, credit: J.credit, materials: mat, _dbg: { dynamic, segMeshes, J } };
}
