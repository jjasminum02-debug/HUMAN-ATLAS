"""T98 source-feasibility probe only. No source save, product GLB, or app changes."""
import bpy
import hashlib
import json
import math
from pathlib import Path
import resource
import struct
import time
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / 'atlas-data/source-cache/z-anatomy/t97/extracted/Z-Anatomy/Startup.blend'
EXPECTED = '9f08a17ea0115fed80b2a73ecdf0a1bc2ab2f6956f37c593ce23d513ea35afcd'
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def write(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

assert sha(SOURCE) == EXPECTED
start = time.perf_counter()
assert bpy.context.preferences.filepaths.use_scripts_auto_execute is False
bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False, use_scripts=False)
scene = bpy.context.scene
assert scene.frame_current == 0
inventory = json.loads((ROOT / 'work/evidence/T98/blender-raw-object-inventory.json').read_text())
frozen = {r['sourceObjectLocator']['objectIdName']: r for r in inventory['allObjects']}
depsgraph = bpy.context.evaluated_depsgraph_get()
depsgraph.update()
old_path = ROOT / 'work/evidence/T98/resume-2026-09-28/export_evaluated_t98.py'
def v3(v):
    return [float(v.x), float(v.y), float(v.z)]
def canonical_geometry_hash(points, triangles):
    # Reuse the previous spike's binary hash contract without importing its CLI entrypoint.
    h = hashlib.sha256(b'HUMAN-ATLAS-T98-EVALUATED-WORLD-GEOMETRY-V1\0')
    h.update(struct.pack('<QQ', len(points), len(triangles)))
    for point in points: h.update(struct.pack('<3d', *point))
    for triangle in triangles: h.update(struct.pack('<3I', *triangle))
    return h.hexdigest()
old = json.loads((old_path.parent / 'evaluated-export-manifest.json').read_text())
sample_before = {r['objectName']: r for r in old['sample']['objects']}
qa = bpy.data.scenes.new('T98 feasibility QA - never saved')
qa.world = bpy.data.worlds.new('T98 QA world')
materials = {}
for system, color in [('bone', (0.82, 0.79, 0.65, 1)), ('muscle', (0.55, 0.20, 0.15, 1))]:
    material = bpy.data.materials.new('T98 QA ' + system)
    material.diffuse_color = color
    material.use_nodes = True
    material.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value = color
    material.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value = 0.85
    materials[system] = material
rows, excluded, failures, qa_objects, sample_checks = [], [], [], [], []
systems = {'1: Skeletal system': 'bone', '4: Muscular system': 'muscle'}
for name, raw in sorted(frozen.items()):
    membership = sorted({systems[p[1]] for p in raw['collectionPaths'] if len(p) > 1 and p[1] in systems})
    if not membership:
        continue
    obj = bpy.data.objects.get(name)
    assert obj is not None, name
    if obj.type != 'MESH' or name.endswith(('.j', '.t', '.g', '.i')):
        excluded.append({'name': name, 'type': obj.type, 'dataName': obj.data.name if obj.data else None,
                         'reason': 'label_or_group_or_landmark_representation', 'systems': membership})
        continue
    assert obj.data.name == raw['dataBlockName'], name
    assert (obj.parent.name if obj.parent else None) == raw['parentObjectName'], name
    expected_leaves = {p[-1] for p in raw['collectionPaths']}
    assert set(c.name for c in obj.users_collection) <= expected_leaves, name
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
    try:
        mesh.calc_loop_triangles()
        positions = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
        mesh.vertices.foreach_get('co', positions)
        positions = positions.reshape((-1, 3))
        triangles = np.empty(len(mesh.loop_triangles) * 3, dtype=np.int32)
        mesh.loop_triangles.foreach_get('vertices', triangles)
        matrix = np.array(evaluated.matrix_world, dtype=np.float64)
        points = positions.astype(np.float64) @ matrix[:3, :3].T + matrix[:3, 3]
        finite = bool(np.isfinite(points).all() and np.isfinite(matrix).all())
        if not finite or not len(triangles):
            failures.append({'name': name, 'finite': finite, 'triangles': len(triangles)//3})
        drivers = [] if not obj.animation_data else [
            {'path': d.data_path, 'type': d.driver.type, 'expression': d.driver.expression,
             'valid': bool(d.driver.is_valid), 'mute': bool(d.mute)} for d in obj.animation_data.drivers]
        row = {'name': name, 'systems': membership, 'sourceLocator': raw['sourceObjectLocator'],
               'dataName': obj.data.name, 'parent': raw['parentObjectName'],
               'collections': sorted(c.name for c in obj.users_collection),
               'vertices': len(mesh.vertices), 'triangles': len(triangles)//3,
               'indexedPositionNormalIndexBytes': len(mesh.vertices)*24 + len(triangles)*4,
               'flatPositionNormalIndexBytes': len(triangles)*28,
               'geometrySha256': hashlib.sha256(positions.tobytes()+triangles.tobytes()).hexdigest(),
               'matrixWorld': matrix.tolist(), 'determinant': float(np.linalg.det(matrix[:3,:3])),
               'bounds': [points.min(axis=0).tolist(), points.max(axis=0).tolist()] if len(points) else None,
               'modifiers': [{'type': m.type, 'viewport': m.show_viewport, 'render': m.show_render} for m in obj.modifiers],
               'drivers': drivers, 'hideRender': obj.hide_render, 'hideViewport': obj.hide_viewport,
               'canonicalConceptId': None, 'upstreamFjId': None, 'defaultLearnerVisible': False}
        rows.append(row)
        if name in sample_before:
            world = [v3(evaluated.matrix_world @ v.co) for v in mesh.vertices]
            tris = [list(t.vertices) for t in mesh.loop_triangles]
            if row['determinant'] < 0:
                for t in tris: t[1], t[2] = t[2], t[1]
            actual = canonical_geometry_hash(world, tris)
            sample_checks.append({'name': name, 'hash': actual,
                                  'matchesPrevious': actual == sample_before[name]['evaluatedGeometrySha256']})
        if len(triangles) and finite:
            copy = mesh.copy()
            copy.transform(evaluated.matrix_world)
            if row['determinant'] < 0: copy.flip_normals()
            copy.materials.clear()
            copy.materials.append(materials[membership[0]])
            preview = bpy.data.objects.new('QA:' + name, copy)
            preview['source_object_name'] = name
            qa.collection.objects.link(preview)
            qa_objects.append(preview)
    finally:
        evaluated.to_mesh_clear()
    if len(rows) % 100 == 0: print('T98_PROBE', len(rows), flush=True)

# Verify remaining frozen insertion patch and helper without counting them as body surfaces.
for name in sorted(set(sample_before) - {r['name'] for r in sample_checks}):
    obj = bpy.data.objects[name]
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
    try:
        mesh.calc_loop_triangles()
        world = [v3(evaluated.matrix_world @ v.co) for v in mesh.vertices]
        tris = [list(t.vertices) for t in mesh.loop_triangles]
        if evaluated.matrix_world.to_3x3().determinant() < 0:
            for t in tris: t[1], t[2] = t[2], t[1]
        actual = canonical_geometry_hash(world, tris)
        sample_checks.append({'name': name, 'hash': actual,
                              'matchesPrevious': actual == sample_before[name]['evaluatedGeometrySha256']})
    finally:
        evaluated.to_mesh_clear()

totals = {key: sum(row[key] for row in rows) for key in
          ['vertices','triangles','indexedPositionNormalIndexBytes','flatPositionNormalIndexBytes']}
all_bounds = [r['bounds'] for r in rows if r['bounds']]
bounds = [np.min([b[0] for b in all_bounds], axis=0).tolist(), np.max([b[1] for b in all_bounds], axis=0).tolist()]
metadata = {'sourceSha256': EXPECTED, 'runtimeVersion': bpy.app.version_string,
            'runtimeBinarySha256': sha(Path(bpy.app.binary_path)),
            'sourceReadOnly': True, 'autoexecDisabled': not bpy.context.preferences.filepaths.use_scripts_auto_execute,
            'frame': scene.frame_current, 'unit': {'system': scene.unit_settings.system,
            'scaleLength': scene.unit_settings.scale_length, 'lengthUnit': scene.unit_settings.length_unit,
            'oneSourceUnitFormatted': bpy.utils.units.to_string('METRIC', 'LENGTH', scene.unit_settings.scale_length)},
            'candidateObjects':len(rows), 'excludedRepresentations':len(excluded), 'bounds':bounds,
            'totals': totals, 'failures':failures, 'sampleReproducibility':sample_checks,
            'probeSecondsBeforePreview':time.perf_counter()-start,
            'maxRssBytesBeforePreview':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'notes':['Source systems include associated fascia/bursae/cartilage, not only named muscles or bones.',
                     'No runtime manifest or learner visibility is created. QA deliberately exposes source-hidden surfaces.',
                     'Byte estimates are vertex/index layouts, not downloaded GLB sizes or GPU memory.'],
            'objects':rows, 'excluded':excluded}
write('evaluated-base-probe.json', metadata)
assert not failures, failures
assert len(sample_checks) == 12 and all(c['matchesPrevious'] for c in sample_checks)

# Independent QA renders from evaluated copies, with anatomical orientation recorded later after inspection.
qa.render.engine = 'BLENDER_EEVEE'
qa.render.resolution_x = 900; qa.render.resolution_y = 1200; qa.render.resolution_percentage = 100
qa.render.image_settings.file_format = 'PNG'
qa.eevee.taa_render_samples = 16
qa.world.use_nodes = True
qa.world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.8,0.8,0.8,1)
qa.world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.65
qa.view_settings.view_transform = 'Standard'
lo, hi = Vector(bounds[0]), Vector(bounds[1]); center=(lo+hi)/2; extent=max(hi-lo)
camera=bpy.data.objects.new('T98 camera',bpy.data.cameras.new('T98 camera'))
qa.collection.objects.link(camera); qa.camera=camera
camera.data.type='ORTHO'; camera.data.ortho_scale=extent*1.12
for i,direction in enumerate([(1,-2,2),(-1,1,2)]):
    data=bpy.data.lights.new('T98 light','AREA'); data.energy=250; data.size=extent*2
    light=bpy.data.objects.new('T98 light',data); qa.collection.objects.link(light)
    light.location=center+Vector(direction)*extent
    light.rotation_euler=(center-light.location).to_track_quat('-Z','Y').to_euler()
previews=[]
rows_by_name={row['name']:row for row in rows}
views=[('source-minus-y',(0,-1,0),'all'),('source-plus-y',(0,1,0),'all'),
       ('source-plus-x',(1,0,0),'all'),('muscle-bone-front',(0,-1,0),'muscle_bone'),
       ('muscle-bone-back',(0,1,0),'muscle_bone'),('bone-front',(0,-1,0),'bone')]
for label,direction,policy in views:
    for obj in qa_objects:
        row=rows_by_name[obj['source_object_name']]
        obj.hide_render=(policy=='bone' and 'bone' not in row['systems']) or (
            policy=='muscle_bone' and 'bone' not in row['systems'] and 'Muscles' not in row['collections'])
    camera.location=center+Vector(direction)*extent*3
    camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
    qa.render.filepath=str(OUT/(label+'.png'))
    bpy.ops.render.render(write_still=True,scene=qa.name)
    previews.append({'path':label+'.png','sha256':sha(Path(qa.render.filepath)),
                     'qaVisibilityPolicy':policy,'sourceVisibilityNotChanged':True})
metadata['preview']=previews
metadata['totalSecondsIncludingPreview']=time.perf_counter()-start
metadata['sourceHashAfter']=sha(SOURCE)
assert metadata['sourceHashAfter']==EXPECTED
write('evaluated-base-probe.json',metadata)
print('T98_BASE_PROBE_OK',len(rows),totals,flush=True)
