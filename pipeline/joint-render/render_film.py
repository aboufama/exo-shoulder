"""Blender Cycles: the mannequin film (film_frames.py chunk -> PNG frames).

Matte-black mannequin (film_frames.py / mannequin.py: smooth featureless display head, muscle relief from the rig), every design's exo parts parented to one empty per
(design, group) whose world matrix comes from the chunk file each frame; the showing design swaps with a shrink/grow
about the shoulder. Dark studio: charcoal gradient seen by the camera, cool rim softboxes that draw the black body's
outline, a warm key for the metal. Exo look = the user's: bead-blasted metal with grain, polished screws, iglidur orange.

    blender -b -P render_film.py -- --glb designs.glb --out frames --w 1920 --h 1080 --spp 128 --frames a-b
(motion.json next to the GLB = this chunk's motion file)
"""
import argparse, base64, gzip, json, math, os, sys
import bpy, numpy as np
from mathutils import Matrix, Vector

ap = argparse.ArgumentParser()
ap.add_argument("--glb"); ap.add_argument("--out", default="frames"); ap.add_argument("--w", type=int, default=1920); ap.add_argument("--h", type=int, default=1080)
ap.add_argument("--spp", type=int, default=128); ap.add_argument("--frames", default="")
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])
here = os.path.dirname(os.path.abspath(args.glb)); MO = json.load(open(os.path.join(here, "motion.json")))
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=os.path.abspath(args.glb))
# glTF importer converts Y-up to Z-up and metres; our GLB is mm: undo the importer's axis change per object and keep raw mm
Yup = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))            # Blender = Yup @ viewer (x, y, z) -> (x, -z, y)
parts = [o for o in sc.objects if o.type == "MESH"]
empties = {}
for o in parts:
    key = "|".join(o.name.split("|")[:2])                                              # D<k>|<group>
    if key not in empties:
        e = bpy.data.objects.new("E_" + key, None); sc.collection.objects.link(e); e.matrix_world = Matrix.Identity(4); empties[key] = e
    mw = o.matrix_world.copy(); o.parent = None
    # mesh vertices back to raw glTF (Y-up mm): local = Yup^-1 @ mw
    o.data.transform(Yup.inverted() @ mw); o.matrix_world = Matrix.Identity(4); o.parent = empties[key]
    for p in o.data.polygons: p.use_smooth = True

def principled(name, color, metal, rough, bump=None, coat=0.0, sheen=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Metallic"].default_value = metal; b.inputs["Roughness"].default_value = rough
    if coat: b.inputs["Coat Weight"].default_value = coat; b.inputs["Coat Roughness"].default_value = 0.45
    if sheen: b.inputs["Sheen Weight"].default_value = sheen; b.inputs["Sheen Tint"].default_value = (0.55, 0.6, 0.68, 1)
    if bump:
        tc = nt.nodes.new("ShaderNodeTexCoord"); nz = nt.nodes.new("ShaderNodeTexNoise"); bp = nt.nodes.new("ShaderNodeBump")
        nz.inputs["Scale"].default_value = bump[0]; nz.inputs["Detail"].default_value = 6; nz.inputs["Roughness"].default_value = 0.7
        bp.inputs["Strength"].default_value = bump[1]; bp.inputs["Distance"].default_value = 0.05
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"]); nt.links.new(nz.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m
alu = principled("blasted", (0.60, 0.615, 0.635), 1.0, 0.36, bump=(9.0, 0.18)); stainless = principled("stainless", (0.80, 0.80, 0.81), 1.0, 0.09)
iglide = principled("iglide", (0.80, 0.42, 0.03), 0.0, 0.42); steel = principled("steel", (0.82, 0.83, 0.85), 1.0, 0.13)
# matte black display mannequin (user look): no coat, no sheen, very rough, low specular - face-on it stays black, the
# softbox rims draw its outline at grazing angles (Fresnel). Coat 0.04 + sheen 0.05 + roughness 0.72 read charcoal and glossy.
black = principled("mannequin", (0.014, 0.014, 0.015), 0.0, 0.9)
for nd in black.node_tree.nodes:
    if nd.type == "BSDF_PRINCIPLED" and "Specular IOR Level" in nd.inputs: nd.inputs["Specular IOR Level"].default_value = 0.12
def mat_for(n):
    l = n.lower()
    if any(k in l for k in ("din 7984", "iso 10642", "dowel", "screw")): return stainless           # every screw polished (user look)
    if any(k in l for k in ("igus", "iglidur", "liner", "gib")): return iglide
    if "bearing" in l and "igus" not in l: return steel
    return alu
for o in parts: o.data.materials.clear(); o.data.materials.append(mat_for(o.name))
# mannequin mesh
B = MO["body"]; Fc = np.frombuffer(gzip.decompress(base64.b64decode(B["faces"])), np.int32).reshape(-1, 3)
VV = np.frombuffer(gzip.decompress(base64.b64decode(B["verts"])), np.int16).reshape(-1, B["nv"], 3).astype(np.float32) * B["scale"]
me = bpy.data.meshes.new("mannequin"); v0 = VV[0] @ np.array(Yup.to_3x3()).T
me.from_pydata(v0.tolist(), [], Fc.tolist()); me.update(); body = bpy.data.objects.new("mannequin", me); sc.collection.objects.link(body)
for p in me.polygons: p.use_smooth = True
me.materials.append(black)
# world + lights
w = bpy.data.worlds.new("dark"); sc.world = w; w.use_nodes = True; nt = w.node_tree; nt.nodes.clear(); outn = nt.nodes.new("ShaderNodeOutputWorld")
lbg = nt.nodes.new("ShaderNodeBackground"); lbg.inputs["Color"].default_value = (0.16, 0.165, 0.175, 1); lbg.inputs["Strength"].default_value = 0.25
cbg = nt.nodes.new("ShaderNodeBackground"); tcw = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ"); ramp = nt.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].color = (0.018, 0.019, 0.021, 1); ramp.color_ramp.elements[1].color = (0.075, 0.078, 0.084, 1)
nt.links.new(tcw.outputs["Window"], sep.inputs["Vector"]); nt.links.new(sep.outputs["Y"], ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"], cbg.inputs["Color"])
lp = nt.nodes.new("ShaderNodeLightPath"); mix = nt.nodes.new("ShaderNodeMixShader"); nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs["Fac"])
nt.links.new(lbg.outputs["Background"], mix.inputs[1]); nt.links.new(cbg.outputs["Background"], mix.inputs[2]); nt.links.new(mix.outputs["Shader"], outn.inputs["Surface"])
def area(name, size, energy, pos, tgt, color):
    d = bpy.data.lights.new(name, "AREA"); d.shape = "RECTANGLE"; d.size, d.size_y = size; d.energy = energy; d.color = color
    o = bpy.data.objects.new(name, d); sc.collection.objects.link(o); o.location = Vector(pos); o.rotation_euler = (Vector(tgt) - o.location).to_track_quat("-Z", "Y").to_euler()
C0 = (0.0, -0.03, 0.0)
area("key", (0.9, 0.6), 60.0, (-0.9, 1.0, 1.1), C0, (1.0, 0.95, 0.9))            # Blender coords (x, -z_viewer, y_viewer)
area("rimR", (0.25, 1.6), 140.0, (1.0, 1.2, 0.5), C0, (0.82, 0.9, 1.0))
area("rimL", (0.25, 1.6), 110.0, (-1.2, -1.0, 0.6), C0, (0.82, 0.9, 1.0))
area("top", (0.8, 0.8), 25.0, (0.0, 0.2, 1.6), C0, (0.95, 0.97, 1.0))
cam_d = bpy.data.cameras.new("cam"); cam_d.sensor_fit = "VERTICAL"; cam_d.clip_start = 0.01; cam_d.clip_end = 30; cam_d.dof.use_dof = True; cam_d.dof.aperture_fstop = 4.0
cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
tgt = bpy.data.objects.new("target", None); sc.collection.objects.link(tgt); tc = cam.constraints.new("TRACK_TO"); tc.target = tgt; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
cam_d.dof.focus_object = tgt
def to_bl(p): return Vector((p[0], -p[2], p[1]))
# render settings
sc.render.engine = "CYCLES"; prefs = bpy.context.preferences.addons["cycles"].preferences
for kind in ("OPTIX", "CUDA"):
    try:
        prefs.compute_device_type = kind; prefs.get_devices()
        if any(d.type == kind for d in prefs.devices): break
    except TypeError: continue
for d in prefs.devices: d.use = d.type != "CPU"
sc.cycles.device = "GPU"; print("devices:", [(d.name, d.type, d.use) for d in prefs.devices], flush=True); print("compute:", prefs.compute_device_type, flush=True)
sc.cycles.samples = args.spp; sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.01; sc.cycles.use_denoising = True
sc.cycles.denoiser = "OPTIX" if prefs.compute_device_type == "OPTIX" else "OPENIMAGEDENOISE"; sc.cycles.max_bounces = 8; sc.cycles.glossy_bounces = 6
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = args.w, args.h, 100; sc.render.fps = MO["fps"]
sc.view_settings.view_transform = "AgX"; sc.view_settings.exposure = 0.0
for look in ("AgX - Medium High Contrast", "Medium High Contrast"):
    try: sc.view_settings.look = look; break
    except TypeError: pass
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_depth = "8"; os.makedirs(args.out, exist_ok=True)
a, b = (map(int, args.frames.split("-")) if args.frames else (MO["a"], MO["b"]))
for f in range(a, b + 1):
    fr = MO["frames"][str(f)]; k = fr["design"]
    for key, e in empties.items():
        dk, g = key.split("|"); show = int(dk[1:]) == k and g in fr["X"] and fr["scale"] > 0.02
        for ch in e.children: ch.hide_render = not show
        if show: X = np.array(fr["X"][g]).reshape(3, 4); M = Matrix([list(X[0]) , list(X[1]), list(X[2]), [0, 0, 0, 1]]); e.matrix_world = Yup @ M
    V = VV[f - MO["a"]] @ np.array(Yup.to_3x3()).T; me.vertices.foreach_set("co", V.ravel()); me.update()
    c = fr["cam"]; cam.location = to_bl(c["pos"]); tgt.location = to_bl(c["target"]); cam_d.angle_y = math.radians(c["fov"])
    sc.frame_set(f); sc.render.filepath = os.path.join(args.out, f"{f:04d}.png"); bpy.ops.render.render(write_still=True)
