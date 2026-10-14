"""Blender Cycles render of the EXO joint + cuff assembly film (film_v7.json + joint_v7.glb).

Look: links and cuff raw 7075 bead blasted (metallic, satin, fine blast grain); every screw polished stainless;
6704 bearing steel; iglide washers and sleeve; nickel magnet. No floor: a seamless studio backdrop seen by the camera
(lighting comes from a darker studio world and area-light softboxes, including one from below for the underside).
Camera lens, focus distance and aperture are animated from the film file (depth of field), true motion blur.

    blender -b -P render_v7.py -- --glb joint_v7.glb --out frames --w 1920 --h 1080 --spp 160 [--frames a-b] [--still t]
The film file is read from motion.json next to the GLB (the serverless worker names it so); falls back to film_v7.json.
"""
import argparse
import json
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

ap = argparse.ArgumentParser()
ap.add_argument("--glb", default="joint_v7.glb"); ap.add_argument("--out", default="frames")
ap.add_argument("--w", type=int, default=1920); ap.add_argument("--h", type=int, default=1080)
ap.add_argument("--spp", type=int, default=160); ap.add_argument("--frames", default="")
ap.add_argument("--still", type=float, default=None)
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])

here = os.path.dirname(os.path.abspath(args.glb))
film_path = next(p for p in (os.path.join(here, "motion.json"), os.path.join(here, "film_v7.json")) if os.path.exists(p))
FILM = json.load(open(film_path)); FPS = FILM["fps"]; NF = len(FILM["frames"])

# ------------------------------------------------------------------ scene
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=os.path.abspath(args.glb))
obj = {o.name.split(".")[0]: o for o in sc.objects if o.type == "MESH"}
for o in obj.values():
    o.rotation_mode = "XYZ"; o.parent = None
    for p in o.data.polygons:
        p.use_smooth = True


def principled(name, color, metal, rough, bump=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    if bump:                                                       # bead-blast grain in object space
        tc = nt.nodes.new("ShaderNodeTexCoord"); nz = nt.nodes.new("ShaderNodeTexNoise"); bp = nt.nodes.new("ShaderNodeBump")
        nz.inputs["Scale"].default_value = bump[0]; nz.inputs["Detail"].default_value = 6; nz.inputs["Roughness"].default_value = 0.7
        bp.inputs["Strength"].default_value = bump[1]; bp.inputs["Distance"].default_value = 0.00005
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"]); nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
        mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = rough - 0.04; mr.inputs["To Max"].default_value = rough + 0.04
        nt.links.new(nz.outputs["Fac"], mr.inputs["Value"]); nt.links.new(mr.outputs["Result"], b.inputs["Roughness"])
    return m


alu = principled("blasted_7075", (0.60, 0.615, 0.635), 1.0, 0.38, bump=(9000, 0.18))
stainless = principled("stainless", (0.80, 0.80, 0.81), 1.0, 0.09)
steel = principled("bearing_steel", (0.82, 0.83, 0.85), 1.0, 0.13)
shield = principled("shield", (0.62, 0.64, 0.67), 1.0, 0.28)
iglide = principled("iglide", (0.80, 0.42, 0.03), 0.0, 0.42)
nickel = principled("nickel", (0.80, 0.78, 0.74), 1.0, 0.12)


def mat_for(n):
    if "SCREW" in n: return stainless
    if n == "SHIELDS": return shield
    if n.startswith("BEARING"): return steel
    if n.startswith("WASHER") or n == "SLEEVE": return iglide
    if n == "MAGNET": return nickel
    return alu


for n, o in obj.items():
    o.data.materials.clear(); o.data.materials.append(mat_for(n))
    if "SCREW" in n:                                              # instances share a mesh: keep per-object material
        o.material_slots[0].link = "OBJECT"; o.material_slots[0].material = stainless

# world: a darker studio for lighting and reflections; the camera sees a soft light-grey vertical gradient
w = bpy.data.worlds.new("studio"); sc.world = w; w.use_nodes = True
nt = w.node_tree; nt.nodes.clear()
outn = nt.nodes.new("ShaderNodeOutputWorld")
light_bg = nt.nodes.new("ShaderNodeBackground"); light_bg.inputs["Color"].default_value = (0.30, 0.30, 0.31, 1); light_bg.inputs["Strength"].default_value = 0.35
cam_bg = nt.nodes.new("ShaderNodeBackground"); cam_bg.inputs["Strength"].default_value = 1.0
tcw = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ"); ramp = nt.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].color = (0.40, 0.395, 0.385, 1); ramp.color_ramp.elements[1].color = (0.80, 0.79, 0.77, 1)
nt.links.new(tcw.outputs["Window"], sep.inputs["Vector"]); nt.links.new(sep.outputs["Y"], ramp.inputs["Fac"])
nt.links.new(ramp.outputs["Color"], cam_bg.inputs["Color"])
lp = nt.nodes.new("ShaderNodeLightPath"); mix = nt.nodes.new("ShaderNodeMixShader")
nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs["Fac"])
nt.links.new(light_bg.outputs["Background"], mix.inputs[1]); nt.links.new(cam_bg.outputs["Background"], mix.inputs[2])
nt.links.new(mix.outputs["Shader"], outn.inputs["Surface"])


def area(name, size, energy, az, el, dist, centre=(0.0, 0.0, 0.0), color=(1, 1, 1)):
    d = bpy.data.lights.new(name, "AREA"); d.shape = "RECTANGLE"; d.size, d.size_y = size; d.energy = energy; d.color = color
    o = bpy.data.objects.new(name, d); sc.collection.objects.link(o)
    a, e = math.radians(az), math.radians(el); c = Vector(centre)
    o.location = c + Vector((dist * math.cos(e) * math.cos(a), dist * math.cos(e) * math.sin(a), dist * math.sin(e)))
    o.rotation_euler = (c - o.location).to_track_quat("-Z", "Y").to_euler()


C = (0.0, 0.0, -0.03)
area("key", (0.8, 0.5), 8.0, 150, 70, 0.85, C, (1.0, 0.97, 0.93))
area("fill", (1.2, 0.7), 2.0, -20, 15, 1.0, C, (0.96, 0.98, 1.0))
area("rim", (0.2, 1.0), 7.0, 60, 20, 0.8, C, (0.92, 0.96, 1.0))
area("under", (0.9, 0.6), 4.0, -70, -60, 0.8, C, (1.0, 0.98, 0.95))

cam_d = bpy.data.cameras.new("cam"); cam_d.sensor_fit = "VERTICAL"; cam_d.clip_start = 0.005; cam_d.clip_end = 20
cam_d.dof.use_dof = True
cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
tgt = bpy.data.objects.new("target", None); sc.collection.objects.link(tgt)
tc = cam.constraints.new("TRACK_TO"); tc.target = tgt; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"

# ------------------------------------------------------------------ animation from the film file
base = {n: o.location.copy() for n, o in obj.items()}
key_of = lambda n: "BEARING" if (n.startswith("BEARING") or n == "SHIELDS") else n
flexes = lambda n: n in ("MIDDLE", "CUFF") or n.startswith("CSCREW")

for i, f in enumerate(FILM["frames"]):
    for n, o in obj.items():
        a = math.radians(f["flex"]) if flexes(n) else 0.0
        p = Matrix.Rotation(a, 3, "Z") @ base[n]
        o.location = p + Vector((0, 0, f["z"].get(key_of(n), 0.0) / 1000))
        o.rotation_euler = (0, 0, a + math.radians(f["spin"].get(n, 0.0)))
        o.hide_render = n in f.get("hidden", [])
        o.keyframe_insert("location", frame=i); o.keyframe_insert("rotation_euler", frame=i); o.keyframe_insert("hide_render", frame=i)
    c = f["cam"]
    cam.location = Vector(c["pos"]) / 1000; tgt.location = Vector(c["target"]) / 1000
    cam_d.angle_y = math.radians(c["fov"]); cam_d.dof.focus_distance = c["focus"] / 1000; cam_d.dof.aperture_fstop = c["fstop"]
    cam.keyframe_insert("location", frame=i); tgt.keyframe_insert("location", frame=i)
    cam_d.keyframe_insert("lens", frame=i); cam_d.dof.keyframe_insert("focus_distance", frame=i); cam_d.dof.keyframe_insert("aperture_fstop", frame=i)

for idb in list(obj.values()) + [cam, tgt, cam_d]:
    ad = idb.animation_data
    if ad and ad.action:
        for fc in ad.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT" if fc.data_path == "hide_render" else "LINEAR"

# ------------------------------------------------------------------ render settings
sc.render.engine = "CYCLES"
prefs = bpy.context.preferences.addons["cycles"].preferences
for kind in ("OPTIX", "CUDA"):
    try:
        prefs.compute_device_type = kind; prefs.get_devices()
        if any(d.type == kind for d in prefs.devices):
            break
    except TypeError:
        continue
for d in prefs.devices:
    d.use = d.type != "CPU"
sc.cycles.device = "GPU"
print("devices:", [(d.name, d.type, d.use) for d in prefs.devices], flush=True)
print("compute:", prefs.compute_device_type, flush=True)
sc.cycles.samples = args.spp; sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.01
sc.cycles.use_denoising = True
sc.cycles.denoiser = "OPTIX" if prefs.compute_device_type == "OPTIX" else "OPENIMAGEDENOISE"
sc.cycles.max_bounces = 8; sc.cycles.glossy_bounces = 6; sc.cycles.caustics_reflective = False; sc.cycles.caustics_refractive = False
sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.5
for n, o in obj.items():
    if "SCREW" in n:
        o.cycles.motion_steps = 4
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = args.w, args.h, 100
sc.render.fps = FPS
sc.view_settings.view_transform = "AgX"; sc.view_settings.exposure = -0.1
for look in ("AgX - Medium High Contrast", "Medium High Contrast"):
    try:
        sc.view_settings.look = look; break
    except TypeError:
        pass
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_depth = "8"
os.makedirs(args.out, exist_ok=True)

if args.still is not None:
    f = round(args.still * FPS); sc.frame_set(f)
    sc.render.filepath = os.path.abspath(os.path.join(args.out, f"still_{f:04d}.png"))
    bpy.ops.render.render(write_still=True)
else:
    a, b = (map(int, args.frames.split("-")) if args.frames else (0, NF - 1))
    sc.frame_start, sc.frame_end = a, b
    sc.render.filepath = os.path.abspath(args.out) + "/"
    bpy.ops.render.render(animation=True)
print("RENDER DONE", flush=True)
