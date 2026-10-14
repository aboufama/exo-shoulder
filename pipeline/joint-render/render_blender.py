"""Blender Cycles render of the EXO elbow joint, exploded and reassembled, from joint.glb (same scene as rt.html).

Raw 7075 bead blasted (metallic, satin roughness, fine blast grain), threaded M4 screws whose spin is locked to the
0.7 mm pitch while engaged, a studio of area-light softboxes over a seamless floor, true motion blur, OptiX denoise.

    python render_blender.py --glb joint.glb --out frames --w 1920 --h 1080 --spp 160 [--frames 0-365] [--still 4.6]
"""
import argparse
import math
import os
import sys

import bpy
from mathutils import Vector

ap = argparse.ArgumentParser()
ap.add_argument("--glb", default="joint.glb"); ap.add_argument("--out", default="frames")
ap.add_argument("--w", type=int, default=1920); ap.add_argument("--h", type=int, default=1080)
ap.add_argument("--spp", type=int, default=160); ap.add_argument("--frames", default="")
ap.add_argument("--still", type=float, default=None)
ap.add_argument("--start", type=int, default=0); ap.add_argument("--step", type=int, default=1)
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])


# ------------------------------------------------------------------ scene
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=os.path.abspath(args.glb))
obj = {o.name.split(".")[0]: o for o in sc.objects if o.type == "MESH"}
for o in obj.values():
    o.rotation_mode = "XYZ"
    for p in o.data.polygons:
        p.use_smooth = True


def principled(name, color, metal, rough, coat=0.0, bump=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    if coat:
        b.inputs["Coat Weight"].default_value = coat
    if bump:                                                    # fine bead-blast grain in object space
        tc = nt.nodes.new("ShaderNodeTexCoord"); nz = nt.nodes.new("ShaderNodeTexNoise"); bp = nt.nodes.new("ShaderNodeBump")
        nz.inputs["Scale"].default_value = bump[0]; nz.inputs["Detail"].default_value = 6; nz.inputs["Roughness"].default_value = 0.7
        bp.inputs["Strength"].default_value = bump[1]; bp.inputs["Distance"].default_value = 0.00005
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"]); nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
        # a touch of roughness variation from the same grain
        mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = rough - 0.04; mr.inputs["To Max"].default_value = rough + 0.04
        nt.links.new(nz.outputs["Fac"], mr.inputs["Value"]); nt.links.new(mr.outputs["Result"], b.inputs["Roughness"])
    return m


alu = principled("blasted_7075", (0.60, 0.615, 0.635), 1.0, 0.38, bump=(9000, 0.18))
steel = principled("bearing_steel", (0.82, 0.83, 0.85), 1.0, 0.12)
shield = principled("shield", (0.62, 0.64, 0.67), 1.0, 0.28)
iglide = principled("iglide_J", (0.80, 0.42, 0.03), 0.0, 0.42)
screw = principled("screw_steel", (0.55, 0.56, 0.58), 1.0, 0.2)
nickel = principled("nickel", (0.80, 0.78, 0.74), 1.0, 0.12)
MAT = dict(BOTTOM=alu, MIDDLE=alu, TOP=alu, BEARING=steel, SHIELDS=shield, WASHER_LO=iglide, WASHER_UP=iglide, MAGNET=nickel)
for n, o in obj.items():
    o.data.materials.clear(); o.data.materials.append(screw if n.startswith("SCREW") else MAT.get(n, alu))

# seamless floor
bpy.ops.mesh.primitive_plane_add(size=12, location=(0, 0, -0.026))
floor = bpy.context.object; floor.data.materials.append(principled("floor", (0.85, 0.845, 0.83), 0.0, 0.9))

# world: soft grey dome
w = bpy.data.worlds.new("studio"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.36, 0.36, 0.37, 1)
w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.32


def area(name, size, energy, az, el, dist, color=(1, 1, 1)):
    d = bpy.data.lights.new(name, "AREA"); d.shape = "RECTANGLE"; d.size, d.size_y = size; d.energy = energy; d.color = color
    o = bpy.data.objects.new(name, d); sc.collection.objects.link(o)
    a, e = math.radians(az), math.radians(el)
    o.location = (dist * math.cos(e) * math.cos(a), dist * math.cos(e) * math.sin(a), dist * math.sin(e))
    o.rotation_euler = (Vector((0, 0, 0.02)) - o.location).to_track_quat("-Z", "Y").to_euler()
    return o


# camera sits around azimuth -45..-10 deg (Blender XY); key softbox high and behind, fill on camera side, rim strip
area("key", (0.7, 0.45), 7, 150, 74, 0.8, (1.0, 0.97, 0.93))
area("fill", (1.2, 0.7), 1.6, -20, 18, 0.95, (0.96, 0.98, 1.0))
area("rim", (0.18, 0.9), 6, 60, 22, 0.7, (0.92, 0.96, 1.0))

cam_d = bpy.data.cameras.new("cam"); cam_d.sensor_fit = "VERTICAL"; cam_d.angle_y = math.radians(26)
cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
tgt = bpy.data.objects.new("target", None); sc.collection.objects.link(tgt)
tc = cam.constraints.new("TRACK_TO"); tc.target = tgt; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"

# ------------------------------------------------------------------ motion: played back from motion.json (motion.py)
import json
MOTION = json.load(open(os.path.join(os.path.dirname(os.path.abspath(args.glb)), "motion.json")))
FPS, DUR = MOTION["fps"], MOTION["dur"]; NF = len(MOTION["frames"])
base = {n: o.location.copy() for n, o in obj.items()}


def pose(i):
    f = MOTION["frames"][i]
    for n, o in obj.items():
        k = "SCREW" if n.startswith("SCREW") else n
        o.location = base[n] + Vector((0, 0, f["lift"].get(k, 0.0) / 1000))
        o.rotation_euler = (0, 0, math.radians(f["spin"]) if n.startswith("SCREW") else 0.0)
    obj["MIDDLE"].rotation_euler = (0, 0, math.radians(f["flex"]))
    cam.location = [c / 1000 for c in f["cam"]["pos"]]; tgt.location = [c / 1000 for c in f["cam"]["target"]]


def keyall(f):
    for o in list(obj.values()) + [cam, tgt]:
        o.keyframe_insert("location", frame=f)
        if o in obj.values():
            o.keyframe_insert("rotation_euler", frame=f)


for f in range(NF):
    pose(f); keyall(f)
for o in list(obj.values()) + [cam, tgt]:
    if o.animation_data and o.animation_data.action:
        for fc in o.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"

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
sc.cycles.samples = args.spp; sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.01
sc.cycles.use_denoising = True
kind_used = prefs.compute_device_type
sc.cycles.denoiser = "OPTIX" if kind_used == "OPTIX" else "OPENIMAGEDENOISE"
try:
    sc.cycles.denoising_use_gpu = True
except AttributeError:
    pass
print("compute:", kind_used, "denoiser:", sc.cycles.denoiser, flush=True)
sc.cycles.max_bounces = 8; sc.cycles.glossy_bounces = 6; sc.cycles.caustics_reflective = False; sc.cycles.caustics_refractive = False
sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.5
for n, o in obj.items():
    if n.startswith("SCREW"):
        o.cycles.motion_steps = 4                                # follow the spin, not a straight chord
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
    a, b = (map(int, args.frames.split("-")) if args.frames else (args.start, NF - 1))
    sc.frame_start, sc.frame_end, sc.frame_step = a, b, args.step
    sc.render.filepath = os.path.abspath(args.out) + "/"
    bpy.ops.render.render(animation=True)
print("RENDER DONE", flush=True)
