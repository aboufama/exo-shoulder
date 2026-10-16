"""Blender Cycles product stills of a posed EXO design (scene_export.py GLB, mm, body-rig frame).

Look (the user's): every custom metal part raw bead blasted (7075 / Ti read the same: metallic satin with fine blast
grain), polished stainless screws, iglidur washers / sleeves / liners in their orange, bearing steel; no black. Seamless
light-grey studio backdrop, softboxes incl. one from below. One camera per frame from motion.json (pos, target, fov,
focus, fstop); optional mannequin (matte black, smooth head) when the GLB carries a BODY node and motion asks for it.

    blender -b -P render_stills.py -- --glb scene.glb --out frames --w 1920 --h 1080 --spp 256 --frames a-b
"""
import argparse, json, math, os, sys
import bpy
from mathutils import Vector

ap = argparse.ArgumentParser()
ap.add_argument("--glb"); ap.add_argument("--out", default="frames"); ap.add_argument("--w", type=int, default=1920); ap.add_argument("--h", type=int, default=1080)
ap.add_argument("--spp", type=int, default=256); ap.add_argument("--frames", default="")
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])
here = os.path.dirname(os.path.abspath(args.glb)); FILM = json.load(open(os.path.join(here, "motion.json")))

bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=os.path.abspath(args.glb))
from mathutils import Matrix
objs = [o for o in sc.objects if o.type == "MESH"]
Yup = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))            # rig (x, y up, z) -> Blender (x, -z, y)
for o in objs:                                                                       # mesh data back to raw rig mm, then one known transform
    mw = o.matrix_world.copy(); o.parent = None; o.data.transform(Yup.inverted() @ mw)
    o.matrix_world = Yup @ Matrix.Scale(0.001, 4)
    for p in o.data.polygons: p.use_smooth = True
    # exo parts: smooth by angle (split normals at creases > 30 deg) - with plain smooth shading the welded vertices on a
    # crease (dome cap rim, bores, plate edges) average across it and the faces next to it show radial streaks / wavy
    # highlights (the 2026-10-16 stills). The mannequin stays fully smooth.
    if not o.name.lower().startswith("body") and hasattr(o.data, "set_sharp_from_angle"): o.data.set_sharp_from_angle(angle=math.radians(30))

def principled(name, color, metal, rough, bump=None, coat=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Metallic"].default_value = metal; b.inputs["Roughness"].default_value = rough
    if coat: b.inputs["Coat Weight"].default_value = coat
    if bump:
        tc = nt.nodes.new("ShaderNodeTexCoord"); nz = nt.nodes.new("ShaderNodeTexNoise"); bp = nt.nodes.new("ShaderNodeBump")
        nz.inputs["Scale"].default_value = bump[0]; nz.inputs["Detail"].default_value = 6; nz.inputs["Roughness"].default_value = 0.7
        bp.inputs["Strength"].default_value = bump[1]; bp.inputs["Distance"].default_value = 0.00005
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"]); nt.links.new(nz.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
        mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = rough - 0.04; mr.inputs["To Max"].default_value = rough + 0.04
        nt.links.new(nz.outputs["Fac"], mr.inputs["Value"]); nt.links.new(mr.outputs["Result"], b.inputs["Roughness"])
    return m
# motion.json "blast_rough" overrides the blasted metal roughness (default 0.38): at 0.38 a dome cap facing the camera mirrors
# the dark studio world and reads near-black (2026-10-16 pin-knee stills); real bead blast is satin, ~0.5.
alu = principled("blasted", (0.60, 0.615, 0.635), 1.0, float(FILM.get("blast_rough", 0.38)), bump=(9000, 0.18))
stainless = principled("stainless", (0.80, 0.80, 0.81), 1.0, 0.09)
steel = principled("bearing_steel", (0.82, 0.83, 0.85), 1.0, 0.13)
iglide = principled("iglide", (0.80, 0.42, 0.03), 0.0, 0.42)
# MATTE black display mannequin (user look). The 2026-10-15 stills (base 0.018 / rough 0.55 / coat 0.15) came out glossy;
# the film's base 0.004 / rough 0.8 (2026-10-16 first stills) reads as a flat silhouette: no muscles. Default: a matte
# charcoal-black (no coat, rough 0.9, low specular) dark enough to read black, light enough for the key / rim light to
# model the muscles. motion.json "skin" (or a frame's "skin") overrides: base, rough, spec, sheen.
SKIN = dict(base=0.028, rough=0.9, spec=0.2, sheen=0.0); SKIN.update(FILM.get("skin", {}))
skin = principled("mannequin", (0.004, 0.004, 0.0043), 0.0, 0.8)
def set_skin(sk):
    for nd in skin.node_tree.nodes:
        if nd.type != "BSDF_PRINCIPLED": continue
        b = sk["base"]; nd.inputs["Base Color"].default_value = (b, b, b * 1.06, 1); nd.inputs["Roughness"].default_value = sk["rough"]
        if "Specular IOR Level" in nd.inputs: nd.inputs["Specular IOR Level"].default_value = sk["spec"]
        if "Sheen Weight" in nd.inputs: nd.inputs["Sheen Weight"].default_value = sk["sheen"]; nd.inputs["Sheen Roughness"].default_value = 0.5
set_skin(SKIN)
def mat_for(n):
    l = n.lower()
    if l.startswith("body"): return skin
    if any(k in l for k in ("din 7984", "iso 10642", "dowel", "screw", "set screw", "din 6799", "e-clip")): return stainless   # every screw / clip polished (user look)
    if "clock spring:" in l or "magnet" in l: return stainless                    # polished spring steel strip, Ni-plated magnets
    if ("bearing" in l and "igus" not in l) or "rsr3" in l: return steel                               # bearings, ground miniature guides
    if any(k in l for k in ("igus", "iglidur", "liner", "gib", "washer", "sleeve")): return iglide
    return alu
show_body = bool(FILM.get("body", False))
for o in objs:
    o.data.materials.clear(); o.data.materials.append(mat_for(o.name))
    if o.name.lower().startswith("body"): o.hide_render = not show_body

w = bpy.data.worlds.new("studio"); sc.world = w; w.use_nodes = True; nt = w.node_tree; nt.nodes.clear()
outn = nt.nodes.new("ShaderNodeOutputWorld")
light_bg = nt.nodes.new("ShaderNodeBackground"); light_bg.inputs["Color"].default_value = (0.30, 0.30, 0.31, 1); light_bg.inputs["Strength"].default_value = 0.35
cam_bg = nt.nodes.new("ShaderNodeBackground"); cam_bg.inputs["Strength"].default_value = 1.0
tcw = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ"); ramp = nt.nodes.new("ShaderNodeValToRGB")
bgc = FILM.get("backdrop", [[0.40, 0.395, 0.385], [0.80, 0.79, 0.77]])
ramp.color_ramp.elements[0].color = (*bgc[0], 1); ramp.color_ramp.elements[1].color = (*bgc[1], 1)
nt.links.new(tcw.outputs["Window"], sep.inputs["Vector"]); nt.links.new(sep.outputs["Y"], ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"], cam_bg.inputs["Color"])
lp = nt.nodes.new("ShaderNodeLightPath"); mix = nt.nodes.new("ShaderNodeMixShader")
nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs["Fac"]); nt.links.new(light_bg.outputs["Background"], mix.inputs[1]); nt.links.new(cam_bg.outputs["Background"], mix.inputs[2])
nt.links.new(mix.outputs["Shader"], outn.inputs["Surface"])

def area(name, size, energy, dirv, dist, centre, color=(1, 1, 1)):
    d = bpy.data.lights.new(name, "AREA"); d.shape = "RECTANGLE"; d.size, d.size_y = size; d.energy = energy; d.color = color
    o = bpy.data.objects.new(name, d); sc.collection.objects.link(o)
    c = Vector(centre); v = Vector(dirv).normalized(); o.location = c + v * dist; o.rotation_euler = (c - o.location).to_track_quat("-Z", "Y").to_euler()
    return o
cam_d = bpy.data.cameras.new("cam"); cam_d.sensor_fit = "VERTICAL"; cam_d.clip_start = 0.005; cam_d.clip_end = 20; cam_d.dof.use_dof = True
cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
tgt = bpy.data.objects.new("target", None); sc.collection.objects.link(tgt)
tc = cam.constraints.new("TRACK_TO"); tc.target = tgt; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
def to_bl(p): return Vector((p[0] / 1000, -p[2] / 1000, p[1] / 1000))               # rig frame (mm, Y up) -> Blender (m, Z up)
L = FILM.get("lights_centre", [0, 0, 0]); Cb = to_bl(L); s = FILM.get("light_scale", 1.0)
key = area("key", (0.8 * s, 0.5 * s), 8.0 * s * s, (-0.4, 0.5, 0.9), 0.85 * s, Cb, (1.0, 0.97, 0.93))
fill = area("fill", (1.2 * s, 0.7 * s), 2.0 * s * s, (0.9, -0.3, 0.25), 1.0 * s, Cb, (0.96, 0.98, 1.0))
rim = area("rim", (0.2 * s, 1.0 * s), 7.0 * s * s, (-0.6, -0.8, 0.35), 0.8 * s, Cb, (0.92, 0.96, 1.0))
under = area("under", (0.9 * s, 0.6 * s), 4.0 * s * s, (0.3, 0.4, -0.85), 0.8 * s, Cb, (1.0, 0.98, 0.95))
for i, f in enumerate(FILM["frames"]):
    c = f["cam"]; cam.location = to_bl(c["pos"]); tgt.location = to_bl(c["target"])
    cam_d.angle_y = math.radians(c["fov"]); cam_d.dof.focus_distance = c["focus"] / 1000; cam_d.dof.aperture_fstop = c["fstop"]
    cam.keyframe_insert("location", frame=i); tgt.keyframe_insert("location", frame=i); cam_d.keyframe_insert("lens", frame=i)
    cam_d.dof.keyframe_insert("focus_distance", frame=i); cam_d.dof.keyframe_insert("aperture_fstop", frame=i)
for idb in (cam, tgt, cam_d):
    ad = idb.animation_data
    if ad and ad.action:
        for fc in ad.action.fcurves:
            for kp in fc.keyframe_points: kp.interpolation = "CONSTANT"
sc.render.engine = "CYCLES"; prefs = bpy.context.preferences.addons["cycles"].preferences
for kind in ("OPTIX", "CUDA"):
    try:
        prefs.compute_device_type = kind; prefs.get_devices()
        if any(d.type == kind for d in prefs.devices): break
    except TypeError: continue
for d in prefs.devices: d.use = d.type != "CPU"
sc.cycles.device = "GPU"; print("devices:", [(d.name, d.type, d.use) for d in prefs.devices], flush=True); print("compute:", prefs.compute_device_type, flush=True)
sc.cycles.samples = args.spp; sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.008
sc.cycles.use_denoising = True; sc.cycles.denoiser = "OPTIX" if prefs.compute_device_type == "OPTIX" else "OPENIMAGEDENOISE"
sc.cycles.max_bounces = 8; sc.cycles.glossy_bounces = 6; sc.cycles.caustics_reflective = False; sc.cycles.caustics_refractive = False
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = args.w, args.h, 100; sc.render.fps = FILM.get("fps", 30)
sc.view_settings.view_transform = "AgX"; sc.view_settings.exposure = FILM.get("exposure", -0.1)
for look in ("AgX - Medium High Contrast", "Medium High Contrast"):
    try: sc.view_settings.look = look; break
    except TypeError: pass
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_depth = "8"
os.makedirs(args.out, exist_ok=True)
a, b = (map(int, args.frames.split("-")) if args.frames else (0, len(FILM["frames"]) - 1))
for i in range(a, b + 1):
    if "skin" in FILM["frames"][i]: set_skin({**SKIN, **FILM["frames"][i]["skin"]})
    sc.frame_set(i); sc.render.filepath = os.path.join(args.out, f"{i:04d}.png"); bpy.ops.render.render(write_still=True)
