"""Render read-only T97 OBJ QA extracts in a fresh, script-controlled scene.

The untrusted source Startup.blend is never opened. Blender's autoexec switch
is still passed by the invocation; this explicit script imports only the six
locally extracted OBJ candidates and writes internal QA renders.
"""

import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "work/evidence/T97"
OBJ_DIR = ROOT / "atlas-data/source-cache/z-anatomy/t97/latissimus-obj"

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x = 1280
scene.render.resolution_y = 960
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.render.image_settings.color_mode = "RGBA"
scene.render.resolution_percentage = 100
scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.view_settings.view_transform = "AgX"
scene.world = bpy.data.worlds.new("T97 neutral QA world")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.035, 0.045, 0.06, 1)
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6

mat = bpy.data.materials.new("Neutral QA surface")
mat.diffuse_color = (0.31, 0.49, 0.62, 1)
mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.22, 0.43, 0.58, 1)
mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.68

objects = []
for obj_path in sorted(OBJ_DIR.glob("Latissimus_dorsi_muscle.*.obj")):
    verts, faces = [], []
    for line in obj_path.read_text(encoding="ascii").splitlines():
        if line.startswith("v "):
            verts.append(tuple(float(v) for v in line.split()[1:4]))
        elif line.startswith("f "):
            faces.append(tuple(int(v.split("/")[0]) - 1 for v in line.split()[1:4]))
    if not verts or not faces:
        raise RuntimeError("empty OBJ surface: " + obj_path.name)
    mesh = bpy.data.meshes.new(obj_path.stem + " QA mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    mesh.materials.append(mat)
    obj = bpy.data.objects.new(obj_path.stem, mesh)
    scene.collection.objects.link(obj)
    objects.append(obj)

def point_camera(camera, target):
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()

camera_data = bpy.data.cameras.new("T97 QA camera")
camera = bpy.data.objects.new("T97 QA camera", camera_data)
scene.collection.objects.link(camera)
scene.camera = camera
camera_data.type = "ORTHO"
camera_data.ortho_scale = 0.56

def area_light(name, location, power, size):
    light_data = bpy.data.lights.new(name, "AREA")
    light_data.energy = power
    light_data.shape = "DISK"
    light_data.size = size
    light = bpy.data.objects.new(name, light_data)
    scene.collection.objects.link(light)
    light.location = location
    point_camera(light, (0, 0.07, 1.14))

area_light("Key softbox", (1.8, -2.2, 2.5), 340, 2.1)
area_light("Fill softbox", (-1.7, -1.3, 1.4), 180, 1.8)
area_light("Rim softbox", (0.2, 2.0, 1.9), 280, 1.7)

views = {
    "surface-front.png": ((0, -2.7, 1.15), (0, 0.07, 1.14)),
    "surface-back.png": ((0, 2.7, 1.15), (0, 0.07, 1.14)),
    "surface-side.png": ((2.7, 0.07, 1.15), (0, 0.07, 1.14)),
}
camera_data.lens = 50
for name, (position, target) in views.items():
    camera.location = position
    point_camera(camera, target)
    scene.render.filepath = str(EVIDENCE / name)
    bpy.ops.render.render(write_still=True)

print(json.dumps({"blenderVersion": bpy.app.version_string, "objects": len(objects), "renders": list(views)}))
