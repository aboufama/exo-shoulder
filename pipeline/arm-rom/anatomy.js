// Anatomical human for the exo viewer: skeleton landmarks, ~70 named muscles and a blended skin, raymarched on the GPU.
//
// Frame: thorax, x anterior, y up, z to the right; mm; origin = right glenohumeral centre; adult male (1.75 m, GH
// centre 1.40 m above the floor) scaled by `scale` so the shoulder-elbow length matches the exo.
// Bones: rib cage (core), sternum, clavicle (SC joint fixed, AC end carried by the scapula), scapula (scapulohumeral
// rhythm, as in the exo analysis), humerus, ulna (elbow flexion), radius + hand (pronation), pelvis, legs.
// Muscles: each is a group of strands (polylines of round cones) running origin -> via points -> insertion on the
// bones they attach to, so they stretch, slide and wrap with the joints. Volume is kept: a strand's belly radius
// scales with sqrt(rest length / length), so it thickens as it shortens; a gravity-load activation (arm and forearm
// moments) adds tone to the deltoid, cuff, trapezius, serratus and the elbow flexors or triceps.
// Skin = smooth union (per-muscle blend, then a softer blend between muscles) of every muscle and subcutaneous bone,
// inflated by a regional fat layer, so the relief under the skin is the relief of the muscles underneath.
// Rendering: sphere tracing in a box around the body; each ray first culls the primitives whose bounds it crosses,
// then marches only those. Modes: 0 skin, 1 muscles (ecorche), 2 muscles seen through translucent skin.

const D2R = Math.PI / 180;
const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]], sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const sc = (a, k) => [a[0] * k, a[1] * k, a[2] * k], lerp = (a, b, t) => add(a, sc(sub(b, a), t));
const len = a => Math.hypot(a[0], a[1], a[2]), dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
function rot(ax, ang) { const n = len(ax), x = ax[0] / n, y = ax[1] / n, z = ax[2] / n, c = Math.cos(ang), s = Math.sin(ang), t = 1 - c;
  return [[c + x * x * t, x * y * t - z * s, x * z * t + y * s], [y * x * t + z * s, c + y * y * t, y * z * t - x * s], [z * x * t - y * s, z * y * t + x * s, c + z * z * t]]; }
const mv = (A, v) => [A[0][0] * v[0] + A[0][1] * v[1] + A[0][2] * v[2], A[1][0] * v[0] + A[1][1] * v[1] + A[1][2] * v[2], A[2][0] * v[0] + A[2][1] * v[1] + A[2][2] * v[2]];
const mul = (A, B) => A.map(r => [0, 1, 2].map(j => r[0] * B[0][j] + r[1] * B[1][j] + r[2] * B[2][j]));
const I3 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]];

// colours (linear): muscle reds, deep muscle, tendon, bone, rib cage (procedural ribs), fascia, head skin, eye
export const PALETTE = [
  [0.46, 0.075, 0.06], [0.54, 0.10, 0.08], [0.40, 0.06, 0.055], [0.50, 0.085, 0.075], [0.28, 0.04, 0.04],
  [0.78, 0.70, 0.60], [0.74, 0.66, 0.52], [0.74, 0.66, 0.52], [0.66, 0.50, 0.44], [0.62, 0.40, 0.31], [0.86, 0.86, 0.84],
];
const C_TENDON = 5, C_BONE = 6, C_RIB = 7, C_FASCIA = 8, C_HEAD = 9, C_EYE = 10;

export const MID = -188;                                   // body midline (z) from the right shoulder centre
const M_ = MID;

// ------------------------------------------------------------------ trunk core (rib cage, abdomen, pelvis)
const CORE = [
  { c: [-20, -22, M_], r: [84, 100, 108], col: C_RIB },     // upper thorax
  { c: [-8, -150, M_], r: [106, 150, 138], col: C_RIB },    // rib cage
  { c: [6, -330, M_], r: [86, 118, 120], col: C_FASCIA },   // abdomen
  { c: [-10, -470, M_], r: [100, 86, 158], col: C_FASCIA }, // pelvis
];
const CORE_K = 40;
function sminJ(a, b, k) { const h = Math.max(k - Math.abs(a - b), 0) / k; return Math.min(a, b) - h * h * k * 0.25; }
function sdEllJ(p, c, r) { const q = sub(p, c), k0 = len([q[0] / r[0], q[1] / r[1], q[2] / r[2]]), k1 = len([q[0] / r[0] ** 2, q[1] / r[1] ** 2, q[2] / r[2] ** 2]); return k0 * (k0 - 1) / Math.max(k1, 1e-6); }
const coreSD = p => CORE.reduce((d, e) => sminJ(d, sdEllJ(p, e.c, e.r), CORE_K), 1e9);
// point on the trunk surface at height y, angle th (0 = front midline, 90 = right side, 180 = back midline), plus offset
const surfCache = new Map();
function surf(y, th, off) {
  const key = y + ',' + th; let r = surfCache.get(key);
  if (r === undefined) {
    const d = [Math.cos(th * D2R), 0, Math.sin(th * D2R)], o = [-8, y, M_];
    let lo = 0, hi = 400;
    for (let i = 0; i < 40; i++) { const m = (lo + hi) / 2; if (coreSD(add(o, sc(d, m))) < 0) lo = m; else hi = m; }
    r = lo; surfCache.set(key, r);
  }
  return [-8 + (r + off) * Math.cos(th * D2R), y, M_ + (r + off) * Math.sin(th * D2R)];
}

// ------------------------------------------------------------------ landmarks (right side, neutral pose)
const L = {
  SC: [52, 12, M_ + 22], AC: [-12, 38, -14], ACRO: [-2, 41, 14], ACRO_POST: [-34, 36, 4],
  SPINE_ROOT: [-86, 14, -110], SUP_ANGLE: [-74, 44, -118], INF_ANGLE: [-80, -140, -102],
  SGT: [2, 22, -22], IGT: [-10, -26, -24], CORA: [32, 6, -28],
  ELBOW: [0, -310, 0],
};

// muscles: name -> { c colour, fat (skin), s: strands [[points], [radii], [tendon segment indices]] }
// point frames: T thorax, R trunk surface [y, angle, offset], S scapula, C clavicle [t SC->AC, dx, dy, dz],
// H humerus, F ulna (flexion), P radius / hand (flexion + pronation). Neutral = arm hanging, mid-prone forearm.
const R = (y, th, off) => ['R', y, th, off];
const MUSCLES = {
  'deltoid': { c: 1, fat: 2, act: 'delt', fan: 2, flat: [1.9, 'head'], s: [
    [[['C', 0.66, 10, -6, 4], ['H', 29, -28, 5], ['H', 14, -120, 22]], [7, 17, 6]],
    [[['C', 0.84, 8, -4, 6], ['H', 27, -26, 19], ['H', 12, -122, 23]], [7, 18, 6]],
    [[['S', 6, 37, 18], ['H', 14, -22, 33], ['H', 10, -124, 24]], [7, 19, 6]],
    [[['S', -12, 35, 15], ['H', -5, -22, 34], ['H', 8, -126, 24]], [7, 19, 6]],
    [[['S', -32, 31, 8], ['H', -21, -26, 27], ['H', 6, -127, 22]], [7, 17, 6]],
    [[['S', -54, 26, -24], ['H', -31, -34, 12], ['H', 4, -128, 20]], [7, 15, 6]]] },
  'supraspinatus': { c: 2, fat: 3, act: 'cuff', s: [[[['S', -70, 34, -100], ['S', -30, 30, -40], ['H', 6, 20, 16]], [7, 13, 6]]] },
  'infraspinatus / teres minor': { c: 0, fat: 3, act: 'cuff', fan: 1, flat: [2.0, 'core'], s: [
    [[['S', -80, -40, -96], ['S', -50, -20, -52], ['H', -14, 4, 22]], [10, 18, 8]],
    [[['S', -80, -100, -98], ['S', -52, -60, -60], ['H', -18, -8, 20]], [10, 18, 8]],
    [[['S', -62, -120, -80], ['S', -38, -62, -42], ['H', -20, -20, 18]], [8, 14, 7]]] },
  'teres major': { c: 3, fat: 3, flat: [1.3, 'core'], s: [[[['S', -82, -130, -98], ['S', -46, -92, -56], ['H', 8, -60, -10]], [8, 17, 7]]] },
  'latissimus dorsi': { c: 2, fat: 4, fan: 2, flat: [2.8, 'core'], s: [
    [[R(-120, 166, 3), R(-110, 128, 9), ['H', -46, -76, -44], ['H', 10, -58, -12]], [14, 22, 18, 7]],
    [[R(-220, 170, 3), R(-170, 126, 9), ['H', -44, -88, -48], ['H', 11, -62, -12]], [14, 22, 18, 7]],
    [[R(-320, 172, 3), R(-240, 122, 9), ['H', -40, -100, -50], ['H', 12, -66, -12]], [14, 22, 18, 7]],
    [[R(-380, 138, 2), R(-280, 108, 8), ['H', -34, -108, -48], ['H', 13, -70, -12]], [13, 20, 16, 7]]] },
  'pectoralis major': { c: 0, fat: 4, fan: 2, flat: [2.0, 'core'], s: [
    [[['C', 0.14, 10, -6, 0], R(-26, 40, 6), ['H', 26, -56, 12]], [11, 18, 8]],
    [[['C', 0.5, 10, -8, 0], R(-42, 62, 8), ['H', 25, -60, 12]], [11, 19, 8]],
    [[R(-20, 6, 2), R(-70, 44, 10), ['H', 24, -64, 11]], [11, 20, 8]],
    [[R(-80, 7, 2), R(-104, 44, 10), ['H', 22, -62, 10]], [11, 21, 8]],
    [[R(-140, 9, 2), R(-140, 48, 9), ['H', 20, -58, 9]], [11, 20, 8]],
    [[R(-190, 20, 2), R(-166, 60, 8), ['H', 18, -54, 8]], [10, 16, 7]]] },
  'trapezius': { c: 3, fat: 3, act: 'trap', fan: 2, flat: [2.8, 'core'], s: [
    [[['T', -70, 172, M_ + 16], ['T', -55, 104, M_ + 62], ['C', 0.9, -6, 3, 0]], [14, 16, 8]],
    [[['T', -84, 128, M_ + 6], ['T', -62, 70, -110], ['S', -14, 37, 2]], [14, 17, 8]],
    [[['T', -94, 70, M_ + 4], ['T', -80, 50, -98], ['S', -34, 38, 2]], [13, 20, 9]],
    [[R(15, 180, 3), R(25, 150, 6), ['S', -56, 32, -36]], [10, 20, 9]],
    [[R(-50, 180, 3), R(-20, 158, 6), ['S', -80, 22, -96]], [10, 18, 8]],
    [[R(-130, 180, 3), R(-80, 165, 5), ['S', -86, 14, -110]], [9, 15, 7]]] },
  'serratus anterior': { c: 1, fat: 3, kSkin: 14, act: 'serr', flat: [2.2, 'core'], s: [10, -30, -70, -105, -135].map((yb, i) => {
    const y = -70 - 38 * i; return [[R(y - 22, 56 + 3 * i, 2), R(y, 100, 7), R(yb * 0.7 - 70, 132, -4)], [9, 15, 6]]; }) },
  'external oblique': { c: 2, fat: 6, kSkin: 22, fan: 1, flat: [3.2, 'core'], s: [
    [[R(-150, 62, 2), R(-230, 40, 4), R(-270, 26, 2)], [22, 32, 18]],
    [[R(-190, 82, 2), R(-280, 56, 5), R(-330, 30, 2)], [22, 34, 18]],
    [[R(-225, 100, 2), R(-320, 74, 6), R(-400, 40, 2)], [22, 34, 18]],
    [[R(-260, 118, 2), R(-350, 100, 6), R(-420, 70, 2)], [22, 34, 18]],
    [[R(-290, 135, 2), R(-360, 128, 5), ['T', -30, -405, M_ + 142]], [20, 30, 18]]] },
  'rectus abdominis': { c: 0, fat: 5, flat: [2.7, 'core'], s: [[-160, -214], [-222, -278], [-286, -348], [-356, -520]].map(([a, b], i) =>
    [[R(a, 20, -4), R(b, 20, -4)], [27, i === 3 ? 18 : 27]]) },
  'erector spinae': { c: 3, fat: 4, flat: [1.4, 'core'], s: [[[R(-470, 166, -4), R(-350, 165, 0), R(-220, 166, -2), R(-60, 166, -6), R(30, 170, -10)], [24, 32, 28, 18, 11]]] },
  'gluteus maximus': { c: 3, fat: 10, fan: 1, flat: [1.5, 'core'], s: [
    [[R(-440, 170, 0), ['T', -100, -500, M_ + 88], ['T', -40, -560, M_ + 140]], [14, 38, 16]],
    [[R(-500, 175, -5), ['T', -94, -572, M_ + 82], ['T', -45, -612, M_ + 132]], [14, 36, 15]]] },
  'gluteus medius / TFL': { c: 1, fat: 8, flat: [1.3, 'core'], s: [
    [[['T', -50, -390, M_ + 125], ['T', -40, -440, M_ + 140], ['T', -20, -500, M_ + 150]], [18, 30, 14]],
    [[['T', 40, -430, M_ + 125], ['T', 25, -520, M_ + 138], ['T', 10, -600, M_ + 146]], [12, 20, 10]]] },
  'quadriceps': { c: 1, fat: 5, flat: [1.25, 'leg'], s: [
    [[['T', 45, -440, M_ + 100], ['T', 60, -650, M_ + 96], ['T', 55, -880, M_ + 92]], [10, 32, 14], [1]],
    [[['T', -5, -520, M_ + 132], ['T', 25, -690, M_ + 128], ['T', 45, -880, M_ + 110]], [16, 40, 14]],
    [[['T', 15, -640, M_ + 60], ['T', 40, -840, M_ + 68], ['T', 48, -900, M_ + 80]], [16, 34, 12]]] },
  'adductors / sartorius': { c: 2, fat: 6, flat: [1.2, 'leg'], s: [
    [[['T', 25, -540, M_ + 22], ['T', 0, -650, M_ + 46], ['T', -15, -820, M_ + 60]], [18, 42, 18]],
    [[['T', 50, -440, M_ + 140], ['T', 40, -650, M_ + 72], ['T', -5, -930, M_ + 56]], [7, 12, 7]]] },
  'hamstrings': { c: 0, fat: 5, flat: [1.2, 'leg'], s: [
    [[['T', -72, -560, M_ + 62], ['T', -56, -720, M_ + 100], ['T', -40, -900, M_ + 116]], [16, 34, 12]],
    [[['T', -72, -560, M_ + 50], ['T', -56, -720, M_ + 64], ['T', -40, -910, M_ + 54]], [16, 32, 12]]] },
  'gastrocnemius / soleus': { c: 1, fat: 4, flat: [1.2, 'leg'], s: [
    [[['T', -30, -930, M_ + 66], ['T', -55, -1040, M_ + 70], ['T', -48, -1170, M_ + 82], ['T', -50, -1340, M_ + 84]], [14, 36, 16, 10], [2]],
    [[['T', -30, -930, M_ + 106], ['T', -50, -1035, M_ + 102], ['T', -48, -1170, M_ + 86]], [14, 32, 14]],
    [[['T', -20, -1000, M_ + 86], ['T', -35, -1150, M_ + 82], ['T', -48, -1280, M_ + 82]], [16, 32, 12]]] },
  'tibialis / peronei': { c: 2, fat: 4, flat: [1.2, 'leg'], s: [
    [[['T', 34, -960, M_ + 100], ['T', 38, -1100, M_ + 98], ['T', 40, -1300, M_ + 76]], [16, 22, 8], [1]],
    [[['T', 0, -960, M_ + 120], ['T', -5, -1150, M_ + 118], ['T', -20, -1320, M_ + 112]], [12, 18, 7], [1]]] },
  'biceps brachii': { c: 1, fat: 3, act: 'flex', flat: [1.25, 'arm'], s: [
    [[['S', ...L.SGT], ['H', 24, -22, 12], ['H', 34, -150, 6], ['H', 24, -268, 6], ['P', 8, -340, 6]], [4, 7, 23, 10, 5], [0, 3]],
    [[['S', ...L.CORA], ['H', 26, -60, -8], ['H', 34, -155, -6], ['H', 24, -268, 2], ['P', 8, -340, 4]], [5, 12, 22, 10, 5], [3]]] },
  'brachialis': { c: 3, fat: 3, act: 'flex', flat: [1.3, 'arm'], s: [[[['H', 14, -150, 8], ['H', 20, -230, 4], ['F', 10, -335, -4]], [10, 19, 8]]] },
  'coracobrachialis': { c: 2, fat: 3, s: [[[['S', ...L.CORA], ['H', 12, -100, -16], ['H', 8, -150, -14]], [5, 11, 6]]] },
  'triceps brachii': { c: 0, fat: 3, act: 'ext', flat: [1.25, 'arm'], s: [
    [[['S', ...L.IGT], ['H', -30, -80, -14], ['H', -40, -170, -10], ['H', -32, -270, -4], ['F', -26, -305, -4]], [5, 16, 23, 13, 8], [3]],
    [[['H', -14, -50, 18], ['H', -36, -150, 16], ['H', -30, -260, 6], ['F', -26, -305, -2]], [10, 22, 13, 8], [2]],
    [[['H', -18, -150, -16], ['H', -30, -235, -12], ['F', -26, -305, -6]], [11, 17, 8]]] },
  'brachioradialis / wrist extensors (radial)': { c: 1, fat: 3, act: 'flex', flat: [1.1, 'fore'], s: [
    [[['H', 12, -215, 30], ['F', 28, -380, 18], ['P', 22, -470, 12], ['P', 24, -550, 6]], [10, 23, 11, 5], [2]],
    [[['H', 6, -262, 36], ['F', 14, -390, 30], ['P', 12, -480, 18], ['P', 14, -560, 12]], [10, 19, 8, 5], [2]]] },
  'finger / wrist extensors': { c: 2, fat: 3, flat: [1.1, 'fore'], s: [
    [[['H', -6, -298, 36], ['F', -6, -405, 26], ['F', -6, -500, 16], ['P', 0, -565, 12]], [10, 19, 10, 5], [2]],
    [[['H', -14, -300, 32], ['F', -22, -405, 12], ['F', -22, -540, -2]], [9, 16, 6]],
    [[['F', -24, -300, 10], ['F', -30, -340, 12]], [9, 10]]] },
  'forearm flexors': { c: 3, fat: 3, flat: [1.1, 'fore'], s: [
    [[['H', -2, -292, -40], ['P', 18, -390, 0], ['P', 22, -440, 6]], [9, 15, 7]],
    [[['H', -4, -304, -42], ['F', 16, -410, -22], ['P', 10, -500, -14], ['P', 10, -560, -12]], [10, 18, 8, 5], [2]],
    [[['H', -8, -306, -40], ['F', 4, -420, -28], ['P', 2, -510, -18], ['P', 4, -565, -14]], [10, 20, 10, 5], [2]],
    [[['H', -12, -304, -40], ['F', -16, -410, -24], ['F', -18, -540, -14]], [9, 17, 7]],
    [[['F', -18, -330, -20], ['F', -6, -430, -16], ['P', 0, -540, -10]], [10, 18, 8]]] },
  'sternocleidomastoid': { c: 2, fat: 2, flat: [1.3, 'none'], s: [
    [[['T', 58, 22, M_ + 14], ['T', 34, 100, M_ + 40], ['T', -28, 195, M_ + 58]], [6, 13, 9]],
    [[['T', 50, 18, M_ + 42], ['T', 30, 95, M_ + 48], ['T', -28, 195, M_ + 58]], [6, 12, 9]]] },
};
const ORDER = Object.keys(MUSCLES);

function scapulaRot(elev) {                         // same rhythm as the exo analysis
  const n = [Math.cos(30 * D2R), 0, -Math.sin(30 * D2R)];
  return mul(rot([0, 0, 1], 0.12 * elev * D2R), rot(n, -0.36 * Math.max(0, elev - 20) * D2R));
}

const MAXP = 1024, MAXL = 256, MAXG = 256, TW = 6;

export function buildAnatomy(THREE, { scale = 1 } = {}) {
  const s = scale;
  const tex = new Float32Array(4 * TW * MAXP);
  const dt = new THREE.DataTexture(tex, TW, MAXP, THREE.RGBAFormat, THREE.FloatType);
  dt.minFilter = dt.magFilter = THREE.NearestFilter; dt.needsUpdate = true;
  const gtex = new Float32Array(4 * 2 * MAXG);
  const gdt = new THREE.DataTexture(gtex, 2, MAXG, THREE.RGBAFormat, THREE.FloatType);
  gdt.minFilter = gdt.magFilter = THREE.NearestFilter; gdt.needsUpdate = true;
  const box = { min: [-760, -1420, -470], max: [770, 820, 780] };
  const uniforms = {
    uPrims: { value: dt }, uGroups: { value: gdt }, uCount: { value: 0 }, uGCount: { value: 0 }, uMode: { value: 0 }, uSkinAlpha: { value: 0.16 },
    uThoraxFromWorld: { value: new THREE.Matrix4() }, uWorldFromThorax: { value: new THREE.Matrix4() },
    uBoxMin: { value: new THREE.Vector3(...sc(box.min, s)) }, uBoxMax: { value: new THREE.Vector3(...sc(box.max, s)) },
    uSkin: { value: new THREE.Vector3(0.60, 0.38, 0.28) }, uScale: { value: s },
    uPalette: { value: PALETTE.map(c => new THREE.Vector3(...c)) },
    uKey: { value: new THREE.Vector3(0.45, 0.8, 0.55).normalize() }, uFill: { value: new THREE.Vector3(-0.7, 0.25, -0.45).normalize() },
  };
  const material = new THREE.ShaderMaterial({
    uniforms, side: THREE.BackSide, depthWrite: true,
    vertexShader: /* glsl */`
      varying vec3 vWorld;
      void main() { vec4 w = modelMatrix * vec4(position, 1.0); vWorld = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }`,
    fragmentShader: /* glsl */`
      precision highp float; precision highp int; precision highp sampler2D;
      varying vec3 vWorld;
      uniform sampler2D uPrims, uGroups; uniform int uCount, uGCount; uniform int uMode; uniform float uSkinAlpha; uniform float uScale;
      uniform mat4 uThoraxFromWorld; uniform mat4 uWorldFromThorax; uniform mat4 projectionMatrix;
      uniform vec3 uBoxMin, uBoxMax, uSkin, uKey, uFill; uniform vec3 uPalette[11];
      #define MAXP ${MAXP}
      #define MAXL ${MAXL}
      #define MAXG ${MAXG}
      int LST[MAXL]; int NL;
      vec4 P(int i, int j) { return texelFetch(uPrims, ivec2(j, i), 0); }
      float smin(float a, float b, float k) { float h = max(k - abs(a - b), 0.0) / k; return min(a, b) - h * h * k * 0.25; }
      float smax(float a, float b, float k) { return -smin(-a, -b, k); }
      float sdRoundCone(vec3 p, vec3 a, vec3 b, float r1, float r2) {
        vec3 ba = b - a; float l2 = dot(ba, ba), rr = r1 - r2, a2 = l2 - rr * rr, il2 = 1.0 / l2;
        vec3 pa = p - a; float y = dot(pa, ba), z = y - l2; vec3 xv = pa * l2 - ba * y; float x2 = dot(xv, xv), y2 = y * y * l2, z2 = z * z * l2;
        float k = sign(rr) * rr * rr * x2;
        if (sign(z) * a2 * z2 > k) return sqrt(x2 + z2) * il2 - r2;
        if (sign(y) * a2 * y2 < k) return sqrt(x2 + y2) * il2 - r1;
        return (sqrt(x2 * a2 * il2) + y * rr) * il2 - r1; }
      float sdEll(vec3 p, vec3 c, vec3 r) { vec3 q = p - c; float k0 = length(q / r), k1 = length(q / (r * r)); return k0 * (k0 - 1.0) / max(k1, 1e-6); }
      // per-primitive texels: 0 a.xyz ra | 1 b.xyz rb | 2 kind colour layer fat | 3 bound centre radius | 4 group kSkin kMuscle kMerge
      // layer: 0 core, 1 muscle / bone, 2 skin only, 3 skin-only carve
      // per-primitive texels: 0 a.xyz ra | 1 b.xyz rb | 2 kind colour layer fat | 3 bound centre radius | 4 group kSkin kMuscle kMerge
      // | 5 sheet normal, flattening. layer: 0 core, 1 muscle / bone, 2 skin only, 3 skin-only carve
      bool hitSphere(vec3 ro, vec3 rd, vec3 c, float r, float t0, float t1) {
        vec3 oc = ro - c; float bb = dot(oc, rd), h = bb * bb - dot(oc, oc) + r * r;
        if (h < 0.0) return false; h = sqrt(h); return !(-bb + h < t0 || -bb - h > t1); }
      void cull(vec3 ro, vec3 rd, float t0, float t1, int mode) {
        NL = 0;
        for (int g = 0; g < MAXG; g++) {
          if (g >= uGCount) break;
          vec4 g0 = texelFetch(uGroups, ivec2(0, g), 0), g1 = texelFetch(uGroups, ivec2(1, g), 0);
          if (mode == 1 && g1.w < 0.0) continue;
          if (!hitSphere(ro, rd, g0.xyz, g0.w + (mode == 1 ? abs(g1.w) : g1.z), t0, t1)) continue;
          int i0 = int(g1.x + 0.5), i1 = i0 + int(g1.y + 0.5);
          for (int i = i0; i < i1; i++) {
            vec4 M = P(i, 2); if (mode == 1 && M.z > 1.5) continue;
            vec4 G = P(i, 4), b = P(i, 3);
            if (!hitSphere(ro, rd, b.xyz, b.w + (mode == 1 ? G.z + 1.0 : M.w + max(G.y, G.w)), t0, t1)) continue;
            if (NL < MAXL) { LST[NL] = i; NL++; }
          }
        }
      }
      float primD(vec3 p, int i, vec4 M) {
        vec4 A = P(i, 0), B = P(i, 1);
        if (M.x > 0.5) return sdEll(p, A.xyz, B.xyz);
        vec4 N = P(i, 5);
        if (N.w < 1.001) return sdRoundCone(p, A.xyz, B.xyz, A.w, B.w);
        vec3 q = p + (N.w - 1.0) * dot(p - A.xyz, N.xyz) * N.xyz;           // sheet: squash along its normal
        vec3 ba = B.xyz - A.xyz; float t = clamp(dot(q - A.xyz, ba) / dot(ba, ba), 0.0, 1.0);
        vec3 g = q - A.xyz - ba * t; float gl = length(g); float gn = gl > 1e-4 ? dot(g, N.xyz) / gl : 1.0;
        return sdRoundCone(q, A.xyz, B.xyz, A.w, B.w) / sqrt(1.0 + (N.w * N.w - 1.0) * gn * gn);   // distance / |gradient|
      }
      float map(vec3 p, int mode, out int id) {
        float d = 1e9, dg = 1e9, g = -1.0, kI = 1.0, kO = 1.0, best = 1e9; id = -1;
        for (int j = 0; j < MAXL; j++) {
          if (j >= NL) break;
          int i = LST[j]; vec4 M = P(i, 2);
          if (mode == 1 && M.z > 1.5) continue;
          vec4 G = P(i, 4);
          if (G.x != g) { if (g >= 0.0) d = smin(d, dg, kO); dg = 1e9; g = G.x; kI = mode == 1 ? G.z : G.y; kO = mode == 1 ? 0.8 * uScale : G.w; }
          vec4 bd = P(i, 3);
          float fat = mode == 1 ? 0.0 : M.w;
          if (length(p - bd.xyz) - bd.w - fat > dg + kI) continue;      // cannot change this group's distance
          float di = primD(p, i, M) - fat;
          if (M.z > 2.5) { dg = smax(dg, -di, kI); continue; }
          if (di < best) { best = di; id = i; }
          dg = smin(dg, di, kI);
        }
        if (g >= 0.0) d = smin(d, dg, kO);
        return d;
      }
      float mapd(vec3 p, int mode) { int id; return map(p, mode, id); }
      vec3 normalAt(vec3 p, int mode) { vec2 e = vec2(0.5, -0.5) * uScale;
        return normalize(e.xyy * mapd(p + e.xyy, mode) + e.yyx * mapd(p + e.yyx, mode) + e.yxy * mapd(p + e.yxy, mode) + e.xxx * mapd(p + e.xxx, mode)); }
      bool march(vec3 ro, vec3 rd, float t0, float t1, int mode, out float t, out int id) {
        t = t0;
        for (int s = 0; s < 160; s++) {
          float d = map(ro + rd * t, mode, id);
          if (d < 0.25 * uScale) return true;
          t += d * 0.92; if (t > t1) return false;
        }
        return false;
      }
      float ggx(vec3 n, vec3 v, vec3 l, float rough) { vec3 h = normalize(v + l); float a = rough * rough, nh = max(dot(n, h), 0.0), d = nh * nh * (a * a - 1.0) + 1.0; return a * a / (3.14159 * d * d) * max(dot(n, l), 0.0); }
      vec3 shade(vec3 p, vec3 rd, int mode, int id, out vec3 nW) {
        vec3 n = normalAt(p, mode);
        mat3 W = mat3(uWorldFromThorax); nW = normalize(W * n); vec3 V = normalize(-(W * rd));
        float ao = 0.0; for (int i = 1; i <= 4; i++) { float h = 5.0 * uScale * float(i); ao += max(h - mapd(p + n * h, mode), 0.0) / h; } ao = clamp(1.0 - 0.22 * ao, 0.25, 1.0);
        float sky = 0.5 + 0.5 * nW.y;
        vec4 M = id >= 0 ? P(id, 2) : vec4(0.0, 9.0, 0.0, 0.0); int ci = int(M.y + 0.5);
        if (mode == 0) {
          vec3 alb = uSkin;
          float w = 0.5, nl = dot(nW, uKey), wr = max((nl + w) / (1.0 + w), 0.0);
          vec3 diff = alb * (vec3(1.0, 0.82, 0.74) * 2.1 * wr + vec3(0.9, 0.18, 0.08) * 0.35 * max(wr - max(nl, 0.0), 0.0) * 2.0);
          diff += alb * vec3(0.55, 0.62, 0.75) * 0.5 * max((dot(nW, uFill) + 0.3) / 1.3, 0.0);
          diff += alb * mix(vec3(0.16, 0.12, 0.10), vec3(0.34, 0.38, 0.45), sky) * ao;
          float sp = ggx(nW, V, uKey, 0.48) * 0.035 * 2.0;
          float fr = pow(1.0 - max(dot(nW, V), 0.0), 4.0);
          return diff * mix(1.0, ao, 0.6) + sp + fr * 0.06 * vec3(0.8, 0.85, 1.0) * sky;
        }
        vec3 alb = uPalette[ci];
        if (ci == ${C_RIB}) {                                         // ribs over intercostals
          float ye = p.y / uScale + 0.38 * (p.x / uScale + 110.0);
          float rib = smoothstep(-0.25, 0.35, sin(ye * 6.2832 / 34.0));
          alb = mix(vec3(0.30, 0.05, 0.045), uPalette[${C_BONE}], rib);
        }
        if (M.x < 0.5 && ci < 5 && id >= 0) {                        // fibres along the strand
          vec4 A = P(id, 0), B = P(id, 1); vec3 ax = normalize(B.xyz - A.xyz), q = p - A.xyz, rad = q - ax * dot(q, ax);
          vec3 u = normalize(cross(ax, abs(ax.y) < 0.9 ? vec3(0, 1, 0) : vec3(1, 0, 0))), v = cross(ax, u);
          float f = sin(atan(dot(rad, v), dot(rad, u)) * 48.0 + 3.0 * sin(dot(q, ax) / uScale * 0.08));
          alb *= 0.86 + 0.14 * f;
        }
        float nl = dot(nW, uKey), wr = max((nl + 0.25) / 1.25, 0.0);
        vec3 col = alb * (vec3(1.0, 0.9, 0.84) * 2.0 * wr + vec3(0.55, 0.62, 0.75) * 0.45 * max((dot(nW, uFill) + 0.3) / 1.3, 0.0));
        col += alb * mix(vec3(0.14, 0.10, 0.09), vec3(0.32, 0.35, 0.42), sky) * ao;
        float wet = ci < 5 ? 0.30 : 0.42;
        col += ggx(nW, V, uKey, wet) * (ci < 5 ? 0.05 : 0.04) * 2.0 * vec3(1.0, 0.95, 0.9);
        return col * mix(1.0, ao, 0.7);
      }
      void main() {
        vec3 ro = (uThoraxFromWorld * vec4(cameraPosition, 1.0)).xyz;
        vec3 pw = (uThoraxFromWorld * vec4(vWorld, 1.0)).xyz;
        vec3 rd = normalize(pw - ro);
        vec3 inv = 1.0 / rd, ta = (uBoxMin - ro) * inv, tb = (uBoxMax - ro) * inv, tmn = min(ta, tb), tmx = max(ta, tb);
        float t0 = max(max(max(tmn.x, tmn.y), tmn.z), 0.0), t1 = min(min(tmx.x, tmx.y), tmx.z);
        if (t1 <= t0) discard;
        cull(ro, rd, t0, t1, uMode == 1 ? 1 : 0);
        if (NL == 0) discard;
        float t; int id; vec3 nW; vec3 col; vec3 ph;
        if (uMode == 2) {
          if (!march(ro, rd, t0, t1, 0, t, id)) discard;
          vec3 ps = ro + rd * t; vec3 nS; vec3 cs = shade(ps, rd, 0, id, nS);
          float ts; int idm; vec3 cm = cs * 0.3; ph = ps;
          if (march(ro, rd, t, t1, 1, ts, idm)) { vec3 nm; cm = shade(ro + rd * ts, rd, 1, idm, nm); }
          vec3 V = normalize(-(mat3(uWorldFromThorax) * rd));
          float fr = pow(1.0 - max(dot(nS, V), 0.0), 2.0);
          float a = clamp(uSkinAlpha + 0.6 * fr * fr, 0.0, 0.9);
          col = mix(cm, cs, a);
        } else {
          if (!march(ro, rd, t0, t1, uMode, t, id)) discard;
          ph = ro + rd * t; col = shade(ph, rd, uMode, id, nW);
        }
        gl_FragColor = vec4(col, 1.0);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
        vec4 clip = projectionMatrix * viewMatrix * (uWorldFromThorax * vec4(ph, 1.0));
        gl_FragDepth = clamp(0.5 * clip.z / clip.w + 0.5, 0.0, 1.0);
      }`,
  });
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), material);
  mesh.frustumCulled = false;

  // ---------------------------------------------------------------- primitive writer
  let n = 0, gid = -1, gK = [8, 3, 12], gStart = [], gArm = [], ARM = false;
  const group = (kSkin, kMus, kMerge) => { gid++; gK = [kSkin * s, kMus * s, kMerge * s]; gStart[gid] = n; gArm[gid] = ARM; };
  let NRM = null;                                                    // sheet normal for the next cones: [n, f]
  const put = (kind, a, ra, b, rb, col, layer, fat) => {
    if (n >= MAXP) return;
    const o = n * 4 * TW;
    tex.set([a[0], a[1], a[2], ra, b[0], b[1], b[2], rb, kind, col, layer, fat], o);
    let c, r;
    if (kind === 0) { c = sc(add(a, b), 0.5); r = len(sub(b, a)) / 2 + Math.max(ra, rb); }
    else { c = a; r = Math.max(b[0], b[1], b[2]); }
    tex.set([c[0], c[1], c[2], r + 1, gid, gK[0], gK[1], gK[2]], o + 12);
    let nn = [0, 0, 0], f = 1;
    if (kind === 0 && NRM) {
      const ax = sub(b, a), la = len(ax);
      if (la > 1e-6) { const u = sc(ax, 1 / la); let v = sub(NRM[0], sc(u, dot(NRM[0], u))); const lv = len(v); if (lv > 0.3) { nn = sc(v, 1 / lv); f = NRM[1]; } }
    }
    tex.set([nn[0], nn[1], nn[2], f], o + 20);
    n++;
  };
  function finishGroups() {
    for (let g = 0; g <= gid; g++) {
      const i0 = gStart[g], i1 = g < gid ? gStart[g + 1] : n;
      let lo = [1e9, 1e9, 1e9], hi = [-1e9, -1e9, -1e9], skinOnly = true, inf = 0, infm = 0;
      for (let i = i0; i < i1; i++) { const o = i * 4 * TW + 12; for (let k = 0; k < 3; k++) { lo[k] = Math.min(lo[k], tex[o + k] - tex[o + 3]); hi[k] = Math.max(hi[k], tex[o + k] + tex[o + 3]); }
        if (tex[i * 4 * TW + 10] < 1.5) skinOnly = false; inf = Math.max(inf, tex[i * 4 * TW + 11] + tex[o + 5] + tex[o + 7]); infm = Math.max(infm, tex[o + 6] + 1); }
      const c = sc(add(lo, hi), 0.5), r = len(sub(hi, lo)) / 2;
      gtex.set([c[0], c[1], c[2], r, i0, i1 - i0, inf, skinOnly ? -infm : infm], g * 8);
    }
    uniforms.uGCount.value = gid + 1; gdt.needsUpdate = true;
  }
  const cone = (a, ra, b, rb, col, layer = 1, fat = 3) => put(0, a, ra * s, b, rb * s, col, layer, fat * s);
  const ell = (c, r, col, layer = 1, fat = 0) => put(1, c, 0, sc(r, s), 0, col, layer, fat * s);

  // ---------------------------------------------------------------- frames
  // girdle elevation: as the arm rises the clavicle elevates and the shoulder centre rises ~0.2 mm per degree past 30 deg
  // (about 30 mm at full elevation). The origin stays at the shoulder centre, so the thorax moves down by LIFT instead.
  const girdleLift = elev => [0, 0.2 * Math.max(0, elev - 30) * s, 0];
  let LIFT = [0, 0, 0];
  function frames(pose, lift = [0, 0, 0], all = false) {
    const Rs = scapulaRot(pose.elev);
    const Rh = mul(rot([0, 1, 0], pose.plane * D2R), mul(rot([1, 0, 0], -pose.elev * D2R), rot([0, 1, 0], pose.axial * D2R)));
    const E0 = sc(L.ELBOW, s), Rf = rot([0, 0, 1], pose.flex * D2R), Rp = rot([0, 1, 0], pose.pron * D2R);
    const ACnow = mv(Rs, sc(L.AC, s)), SC = sub(sc(L.SC, s), lift);
    const raw = (f, x, y, z, w) => {
      if (f === 'T') return sub([x * s, y * s, z * s], lift);
      if (f === 'R') return sub(sc(surf(x, y, z), s), lift);
      if (f === 'S') return mv(Rs, [x * s, y * s, z * s]);
      if (f === 'C') return add(lerp(SC, all ? sub(ACnow, lift) : ACnow, x), [y * s, z * s, w * s]);
      if (f === 'H') return mv(Rh, [x * s, y * s, z * s]);
      const p0 = sub([x * s, y * s, z * s], E0);
      return mv(Rh, add(E0, mv(Rf, f === 'P' ? mv(Rp, p0) : p0)));
    };
    const at = all ? (f, ...c) => (f === 'T' || f === 'R' || f === 'C') ? raw(f, ...c) : sub(raw(f, ...c), lift) : raw;
    const thorax = p => sub(p, lift);                                   // thorax-fixed points given directly (scaled mm)
    // gravity moments: arm (shoulder muscles) and forearm (elbow flexors vs triceps)
    const arm = mv(Rh, [0, -1, 0]), fore = mv(Rh, mv(Rf, [0, -1, 0])), axis = mv(Rh, [0, 0, 1]);
    const armH = Math.sqrt(Math.max(0, 1 - arm[1] ** 2)), foreH = Math.sqrt(Math.max(0, 1 - fore[1] ** 2));
    const m = dot(cross(fore, [0, -1, 0]), axis);                       // > 0: gravity flexes the elbow
    const act = { delt: Math.min(1, 1.15 * armH), cuff: Math.min(1, armH), trap: Math.min(1, pose.elev / 120), serr: Math.min(1, pose.elev / 110),
      flex: m < 0 ? Math.min(1, 1.3 * foreH) : 0, ext: m > 0 ? Math.min(1, 1.3 * foreH) : 0 };
    return { at, act, Rs, thorax, lift };
  }
  const REST = { plane: 10, elev: 6, axial: 0, flex: 12, pron: 0 };
  const rest = new Map();

  // one body half (right side, posed); mirror -> left side
  function half(F, mirror, side) {
    const T = mirror ? p => [p[0], p[1], 2 * M_ * s - p[2]] : p => p;
    const at = (f, ...c) => T(F.at(f, ...c));
    const bones = () => {
      group(3, 2, 10);
      const S = (...c) => at('S', ...c), H = (...c) => at('H', ...c);
      const SCp = T(at('C', 0, 0, 0, 0)), ACp = at('C', 1, 0, 0, 0), Cm = at('C', 0.5, 8, 4, 0);
      cone(SCp, 9, Cm, 8, C_BONE, 1, 2); cone(Cm, 8, ACp, 8, C_BONE, 1, 2);                        // clavicle
      cone(S(...L.SPINE_ROOT), 5, S(...L.ACRO_POST), 9, C_BONE, 1, 2); cone(S(...L.ACRO_POST), 9, S(...L.ACRO), 8, C_BONE, 1, 2);   // spine, acromion
      cone(S(...L.SUP_ANGLE), 4, S(...L.INF_ANGLE), 5, C_BONE, 1, 3); cone(S(...L.INF_ANGLE), 5, S(...L.IGT), 7, C_BONE, 1, 3);
      cone(S(-70, -40, -94), 13, S(-30, -30, -50), 10, C_BONE, 1, 3);                               // blade
      ARM = side === 'pose'; group(3, 2, 10);
      put(1, H(0, 0, 0), 0, [24 * s, 24 * s, 24 * s], 0, C_BONE, 1, 2 * s);                             // humeral head
      cone(H(0, -30, 6), 14, H(0, -280, 2), 11, C_BONE, 1, 2);
      cone(H(-2, -302, -36), 11, H(0, -298, 30), 10, C_BONE, 1, 1.5);                              // epicondyles
      cone(at('F', -26, -300, -6), 11, at('F', -14, -360, -10), 10, C_BONE, 1, 1.5);                 // olecranon, ulna
      cone(at('F', -14, -360, -10), 8, at('F', -18, -552, -4), 7, C_BONE, 1, 2);
      cone(at('P', 6, -318, 20), 9, at('P', 16, -450, 8), 6, C_BONE, 1, 2); cone(at('P', 16, -450, 8), 6, at('P', 22, -552, 4), 11, C_BONE, 1, 2);
      // pelvis rim, knee, shin, ankles
      ARM = false; group(3, 2, 10);
      const t = (...c) => T(F.thorax(sc(c, s)));
      cone(t(-40, -385, M_ + 145), 10, t(52, -430, M_ + 125), 9, C_BONE, 1, 3);
      cone(t(-4, -920, M_ + 70), 26, t(-4, -920, M_ + 110), 26, C_BONE, 1, 3);
      cone(t(56, -888, M_ + 88), 19, t(56, -930, M_ + 88), 15, C_BONE, 1, 2);
      cone(t(30, -950, M_ + 86), 20, t(24, -1330, M_ + 80), 14, C_BONE, 1, 2);
      cone(t(10, -1340, M_ + 60), 13, t(10, -1342, M_ + 62), 12, C_BONE, 1, 2);
      cone(t(-10, -1352, M_ + 110), 12, t(-10, -1354, M_ + 111), 11, C_BONE, 1, 2);
    };
    bones();
    const headC = at('H', 0, 0, 0), armA = headC, armB = at('H', 0, -300, 0), foreA = at('F', 0, -315, 0), foreB = at('P', 0, -555, 0);
    const radial = (m, a0, b0) => { const ax = sub(b0, a0), t = Math.max(0, Math.min(1, dot(sub(m, a0), ax) / dot(ax, ax))); return sub(m, add(a0, sc(ax, t))); };
    const legAxis = y => y > -930 * s - F.lift[1] ? [T(F.thorax(sc([0, -480, M_ + 90], s))), T(F.thorax(sc([0, -920, M_ + 88], s)))] : [T(F.thorax(sc([0, -920, M_ + 86], s))), T(F.thorax(sc([0, -1340, M_ + 82], s)))];
    const normalFor = (kind, m) => {
      if (kind === 'core') { const p = sc(add(m, F.lift), 1 / s), e = 2; return [ (coreSD(add(p, [e, 0, 0])) - coreSD(sub(p, [e, 0, 0]))), (coreSD(add(p, [0, e, 0])) - coreSD(sub(p, [0, e, 0]))), (coreSD(add(p, [0, 0, e])) - coreSD(sub(p, [0, 0, e]))) ]; }
      if (kind === 'head') return sub(m, headC);
      if (kind === 'arm') return radial(m, armA, armB);
      if (kind === 'fore') return radial(m, foreA, foreB);
      if (kind === 'leg') { const [p0, p1] = legAxis(m[1]); return radial(m, p0, p1); }
      return null;
    };
    const ARM_MUSCLES = new Set(['deltoid', 'biceps brachii', 'brachialis', 'coracobrachialis', 'triceps brachii', 'brachioradialis / wrist extensors (radial)', 'finger / wrist extensors', 'forearm flexors']);
    for (const name of ORDER) {
      const mu = MUSCLES[name];
      ARM = side === 'pose' && ARM_MUSCLES.has(name);
      group(mu.kSkin || 10, 2.2, 13);
      const a = mu.act ? F.act[mu.act] : 0;
      // strands (with `fan` interpolated strands between neighbours, for sheet muscles)
      const base = mu.s.map(([pp, rr, tend = []]) => ({ pts: pp.map(q => at(...q)), rr, tend }));
      const strands = [];
      base.forEach((st, i) => {
        strands.push(st);
        const nx = base[i + 1];
        if (mu.fan && nx && nx.pts.length === st.pts.length)
          for (let j = 1; j <= mu.fan; j++) { const u = j / (mu.fan + 1);
            strands.push({ pts: st.pts.map((p, k) => lerp(p, nx.pts[k], u)), rr: st.rr.map((r, k) => r + (nx.rr[k] - r) * u), tend: st.tend }); }
      });
      strands.forEach((st, si) => {
        const pts = st.pts;
        let Lt = 0; for (let i = 1; i < pts.length; i++) Lt += len(sub(pts[i], pts[i - 1]));
        const key = name + '|' + si;
        if (side === 'rest') rest.set(key, Lt);
        const L0 = rest.get(key) || Lt;
        const k = Math.max(0.78, Math.min(1.55, Math.sqrt(L0 / Lt))) * (1 + 0.14 * a);
        for (let i = 1; i < pts.length; i++) {
          const r0 = st.rr[i - 1] * (i - 1 === 0 ? 1 : k), r1 = st.rr[i] * (i === pts.length - 1 ? 1 : k);
          const nv = mu.flat ? normalFor(mu.flat[1], sc(add(pts[i - 1], pts[i]), 0.5)) : null;
          NRM = nv && len(nv) > 1e-9 ? [sc(nv, 1 / len(nv)), mu.flat[0]] : null;
          cone(pts[i - 1], r0, pts[i], r1, st.tend.includes(i - 1) ? C_TENDON : mu.c, 1, (mu.fat + 3) * (1 - 0.2 * a));
        }
        NRM = null;
      });
    }
    // subcutaneous fat envelopes of the limbs (skin only): fill the grooves between muscles up to a smooth surface
    ARM = false;
    ARM = side === 'pose'; group(10, 2, 18);
    cone(at('H', 0, -30, 2), 33, at('H', -2, -270, 0), 27, C_HEAD, 2, 0);
    cone(at('F', -4, -330, 0), 29, at('P', 2, -540, 2), 18, C_HEAD, 2, 0);
    ARM = false; group(10, 2, 18);
    { const t = (...c) => T(F.thorax(sc(c, s)));
      cone(t(0, -520, M_ + 92), 70, t(10, -900, M_ + 88), 46, C_HEAD, 2, 0);
      cone(t(0, -950, M_ + 86), 42, t(0, -1320, M_ + 82), 26, C_HEAD, 2, 0); }
    ARM = false;
    // shoulder-girdle fat pads (skin only): infra- and supraclavicular fossae, posterior shoulder
    group(12, 2, 18);
    put(1, at('S', 30, -6, -64), 0, sc([24, 30, 44], s), 0, C_HEAD, 2, 0);
    put(1, at('S', -14, 30, -84), 0, sc([36, 22, 42], s), 0, C_HEAD, 2, 0);
    put(1, at('S', -48, -10, -56), 0, sc([30, 46, 46], s), 0, C_HEAD, 2, 0);
    put(1, T(F.thorax(sc([4, 30, M_ + 74], s))), 0, sc([40, 22, 36], s), 0, C_HEAD, 2, 0);        // supraclavicular fossa
    group(30, 2, 20);
    put(1, T(F.thorax(sc([-8, -350, M_ + 112], s))), 0, sc([70, 80, 34], s), 0, C_HEAD, 2, 0);    // flank fat over the iliac crest
    // hand (relaxed, mid-prone: palm medial, thumb forward)
    ARM = side === 'pose'; group(6, 2, 9);
    const Pp = (...c) => at('P', ...c);
    const fingers = [[24, -650, 42, 25, 20, 9], [8, -656, 46, 28, 21, 9.5], [-8, -652, 43, 27, 20, 9], [-22, -644, 34, 20, 18, 8]];
    fingers.forEach(([x, y, l1, l2, l3, r]) => {
      cone(Pp(x * 0.55, -578, 0), 12, Pp(x, y, -2), 10.5, C_HEAD, 1, 1.5);
      let p = [x, y, -2], dir = [0.06 * Math.sign(x) * (Math.abs(x) > 10 ? 1 : 0), -1, 0], ang = 0;
      [[l1, 14], [l2, 30], [l3, 22]].forEach(([l, bend], j) => {
        ang += bend * D2R; const d = [dir[0], -Math.cos(ang), -Math.sin(ang)];
        const q = add(p, sc(d, l)); cone(Pp(...p), r - j * 1.1, Pp(...q), r - (j + 1) * 1.1, C_HEAD, 1, 1.2); p = q;
      });
    });
    cone(Pp(20, -585, -10), 15, Pp(26, -628, -14), 11, C_HEAD, 1, 2);                 // thenar
    cone(Pp(-18, -590, -10), 13, Pp(-22, -634, -8), 10, C_HEAD, 1, 2);                // hypothenar
    cone(Pp(22, -585, -10), 12, Pp(40, -622, -22), 10, C_HEAD, 1, 1.5); cone(Pp(40, -622, -22), 10, Pp(50, -650, -30), 9, C_HEAD, 1, 1.2);
    cone(Pp(50, -650, -30), 9, Pp(55, -672, -34), 8, C_HEAD, 1, 1.2);
    // foot
    ARM = false; group(8, 3, 10);
    const t = (...c) => T(F.thorax(sc(c, s)));
    cone(t(-50, -1368, M_ + 84), 30, t(20, -1376, M_ + 84), 29, C_HEAD, 1, 2);
    cone(t(20, -1368, M_ + 70), 26, t(150, -1384, M_ + 62), 17, C_HEAD, 1, 2);
    cone(t(20, -1378, M_ + 105), 22, t(135, -1387, M_ + 118), 14, C_HEAD, 1, 2);
    cone(t(150, -1386, M_ + 64), 16, t(190, -1391, M_ + 70), 13, C_HEAD, 1, 1.5);
    cone(t(136, -1388, M_ + 112), 13, t(168, -1392, M_ + 110), 11, C_HEAD, 1, 1.5);
  }

  function midline() {
    const t = (...c) => sub(sc(c, s), LIFT);
    group(CORE_K, CORE_K, 14);                                                    // trunk core
    CORE.forEach(e => ell(t(...e.c), e.r, e.col, 0, 9));
    group(3, 2, 10);                                                              // sternum, C7
    cone(sub(sc(surf(-14, 0, -3), s), LIFT), 13, sub(sc(surf(-190, 0, -3), s), LIFT), 10, C_BONE, 1, 2);
    cone(t(-88, 72, M_), 9, t(-92, 42, M_), 9, C_BONE, 1, 3);
    group(20, 20, 12);                                                            // neck
    cone(t(-18, 25, M_), 62, t(-6, 165, M_), 50, C_HEAD, 0, 0);
    ell(t(-38, 72, M_), [58, 52, 82], 4, 1, 0);                                  // deep neck: splenius, levator scapulae, scalenes
    cone(t(50, 95, M_), 13, t(46, 128, M_), 13, C_EYE, 1, 1);                       // larynx
    group(14, 14, 14);                                                            // head
    ell(t(-10, 265, M_), [98, 92, 77], C_HEAD, 0); ell(t(42, 200, M_), [58, 75, 60], C_HEAD, 0); ell(t(50, 260, M_), [50, 45, 65], C_HEAD, 0);
    for (const sd of [1, -1]) cone(t(-10, 150, M_ + 52 * sd), 14, t(70, 118, M_ + 14 * sd), 13, C_HEAD, 0, 0);       // mandible
    ell(t(74, 122, M_), [16, 18, 22], C_HEAD, 0);                                                                   // chin
    for (const sd of [1, -1]) ell(t(62, 205, M_ + 48 * sd), [22, 14, 18], C_HEAD, 0);                              // zygomatic
    for (const sd of [1, -1]) ell(t(84, 236, M_ + 25 * sd), [12, 9, 26], C_HEAD, 0);                               // brow
    cone(t(92, 228, M_), 7, t(112, 192, M_), 10, C_HEAD, 0, 0); ell(t(102, 188, M_), [10, 8, 16], C_HEAD, 0);       // nose
    ell(t(94, 165, M_), [7, 6, 22], C_HEAD, 0); ell(t(92, 153, M_), [7, 5, 19], C_HEAD, 0);                        // lips
    for (const sd of [1, -1]) ell(t(-12, 215, M_ + 78 * sd), [22, 30, 9], C_HEAD, 0);                              // ears
    for (const sd of [1, -1]) ell(t(91, 212, M_ + 32 * sd), [12, 9, 16], C_HEAD, 3);                               // orbits (carve)
    group(1, 1, 3);
    for (const sd of [1, -1]) ell(t(77, 212, M_ + 32 * sd), [11.5, 11.5, 11.5], C_EYE, 0);
    group(4, 4, 6);
    ell(sub(sc(surf(-352, 0, 4), s), LIFT), [6, 8, 6], C_HEAD, 3);                            // navel (carve)
  }

  // rest lengths from the rest pose
  { const Fr = frames(REST); n = 0; gid = -1; gStart = []; half(Fr, false, 'rest'); }

  function update(pose, mode = 0, { girdle = true } = {}) {
    n = 0; gid = -1; gStart = []; gArm = []; ARM = false;
    LIFT = girdle ? girdleLift(pose.elev) : [0, 0, 0];
    midline();
    half(frames(pose, LIFT), false, 'pose');
    half(frames(REST, LIFT, true), true, 'left');
    finishGroups();
    uniforms.uCount.value = n; uniforms.uMode.value = mode; dt.needsUpdate = true;
    return n;
  }

  function setFrame(worldFromThorax) {
    uniforms.uWorldFromThorax.value.copy(worldFromThorax);
    uniforms.uThoraxFromWorld.value.copy(worldFromThorax).invert();
    const c = sc(add(box.min, box.max), 0.5 * s), d = sc(sub(box.max, box.min), s);
    const m = new THREE.Matrix4().makeTranslation(c[0], c[1], c[2]).multiply(new THREE.Matrix4().makeScale(d[0], d[1], d[2]));
    mesh.matrixAutoUpdate = false; mesh.matrix.copy(worldFromThorax).multiply(m); mesh.matrixWorldNeedsUpdate = true;
  }
  // CPU copy of the skin field (same maths as the shader, mode 0): signed distance in thorax mm, for collision checks
  function primD(p, i) {
    const o = i * 4 * TW, A = [tex[o], tex[o + 1], tex[o + 2]], ra = tex[o + 3], B = [tex[o + 4], tex[o + 5], tex[o + 6]], rb = tex[o + 7];
    if (tex[o + 8] > 0.5) return sdEllJ(p, A, B);
    const N = [tex[o + 20], tex[o + 21], tex[o + 22]], f = tex[o + 23];
    let q = p, corr = 1;
    if (f > 1.001) {
      q = add(p, sc(N, (f - 1) * dot(sub(p, A), N)));
      const ba = sub(B, A), t = Math.max(0, Math.min(1, dot(sub(q, A), ba) / dot(ba, ba))), g = sub(sub(q, A), sc(ba, t)), gl = len(g);
      const gn = gl > 1e-4 ? dot(g, N) / gl : 1; corr = Math.sqrt(1 + (f * f - 1) * gn * gn);
    }
    // round cone (exact, as in the shader)
    const ba = sub(B, A), l2 = dot(ba, ba), rr = ra - rb, a2 = l2 - rr * rr, il2 = 1 / l2, pa = sub(q, A), y = dot(pa, ba), z = y - l2;
    const xv = sub(sc(pa, l2), sc(ba, y)), x2 = dot(xv, xv), y2 = y * y * l2, z2 = z * z * l2, k = Math.sign(rr) * rr * rr * x2;
    let d;
    if (Math.sign(z) * a2 * z2 > k) d = Math.sqrt(x2 + z2) * il2 - rb;
    else if (Math.sign(y) * a2 * y2 < k) d = Math.sqrt(x2 + y2) * il2 - ra;
    else d = (Math.sqrt(x2 * a2 * il2) + y * rr) * il2 - ra;
    return d / corr;
  }
  // which: 'all' | 'trunk' (everything but the posed right arm) | 'arm' (the posed right arm only)
  function skinDistance(p, which = 'all') {
    let d = 1e9;
    for (let g = 0; g <= gid; g++) {
      if (which === 'trunk' && gArm[g]) continue;
      if (which === 'arm' && !gArm[g]) continue;
      const go = g * 8, c = [gtex[go], gtex[go + 1], gtex[go + 2]];
      const kO = gK_of(g)[1];
      if (len(sub(p, c)) - gtex[go + 3] - gtex[go + 6] > d + kO) continue;
      const i0 = gtex[go + 4], i1 = i0 + gtex[go + 5], kI = gK_of(g)[0];
      if (i1 <= i0) continue;
      let dg = 1e9;
      for (let i = i0; i < i1; i++) {
        const o = i * 4 * TW, di = primD(p, i) - tex[o + 11];
        if (tex[o + 10] > 2.5) dg = -sminJ(-dg, di, kI); else dg = sminJ(dg, di, kI);
      }
      d = sminJ(d, dg, kO);
    }
    return d;
  }
  const gK_of = g => { const o = gStart[g] * 4 * TW + 16; return [Math.max(1e-3, tex[o + 1]), Math.max(1e-3, tex[o + 3])]; };
  return { mesh, update, setFrame, uniforms, muscles: ORDER, frames, MID: M_, skinDistance, get lift() { return LIFT; }, girdleLift, _dbg: { primD, gK_of, tex, gtex, get n() { return n; }, get gid() { return gid; } } };
}
