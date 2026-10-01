"""Read-only pinned Blender evaluation. Never saves or changes the source scene."""
import ast
import hashlib
import json
from pathlib import Path
import struct
import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'atlas-data/assets/derived-glb/za-nerve-t63'
SOURCE = ROOT / 'atlas-data/source-cache/z-anatomy/t97/extracted/Z-Anatomy/Startup.blend'
def sha(b): return hashlib.sha256(b).hexdigest()
# Reuse only the existing indexed surface serialization functions, never its main().
compiler = ast.parse((ROOT / 'atlas-data/tools/datasets/compile_za.py').read_text())
exec(compile(ast.Module(body=[n for n in compiler.body if isinstance(n, ast.FunctionDef) and n.name in ['arrays', 'glb']], type_ignores=[]), '<existing-indexed-adapter>', 'exec'))
assert not bpy.context.preferences.filepaths.use_scripts_auto_execute
assert bpy.app.version[:2] == (3, 5)
assert sha(Path(bpy.app.binary_path).read_bytes()) == '23171ca8704539b44c94cb370894cb3b38908530c012267bed079326d7be95b0'
assert sha(SOURCE.read_bytes()) == '9f08a17ea0115fed80b2a73ecdf0a1bc2ab2f6956f37c593ce23d513ea35afcd'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False, use_scripts=False)
assert bpy.context.scene.frame_current == 0 and bpy.context.scene.unit_settings.scale_length == 1
registry = json.loads((ROOT / 'atlas-data/overlays/nerve-support-t62.json').read_text())
dg = bpy.context.evaluated_depsgraph_get(); dg.update()
rows = []
C = np.array([[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1]], dtype='f8')
for n in registry['instances']:
    if n['localSelection'] != 'text_only': continue
    name = n['names']['en'] + ('.l' if n['side'] == 'left' else '.r')
    obj = bpy.data.objects[name]
    assert obj.type == 'CURVE' and not obj.modifiers and not obj.constraints and obj.animation_data is None
    evaluated = obj.evaluated_get(dg)
    mesh = evaluated.to_mesh(preserve_all_data_layers=True, depsgraph=dg)
    try:
        raw, raw_tri, p, normals, triangles = arrays(mesh)
        matrix = np.array(obj.matrix_world, dtype='f8')
        world = (p.astype('f8') @ matrix[:3,:3].T + matrix[:3,3]).astype('<f4')
        normal_matrix = np.linalg.inv(matrix[:3,:3]).T
        normals = normals.astype('f8') @ normal_matrix.T
        normals = (normals / np.linalg.norm(normals, axis=1)[:,None]).astype('<f4')
        if np.linalg.det(matrix[:3,:3]) < 0: triangles = triangles[:,[0,2,1]].copy()
        atlas = world.astype('f8') @ C[:3,:3].T
        assert (atlas[:,0] > 0).all() if n['side'] == 'left' else (atlas[:,0] < 0).all()
        key = 'ZA-NERVE-' + n['sourceObjectId'].replace('0x','')
        data = glb(world, normals, triangles)
        path = OUT / (key + '.glb'); path.write_bytes(data)
        rows.append({'instanceId':n['id'], 'sourceObjectId':n['sourceObjectId'], 'sourceKey':key, 'name':name, 'side':n['side'],
            'path':str(path.relative_to(ROOT)), 'sha256':sha(data),
            'topologySha256':sha(world.tobytes()+normals.tobytes()+triangles.astype('<u4').tobytes()),
            'vertices':len(world),'triangles':len(triangles),'geometryBytes':len(world)*24+triangles.size*(2 if len(world)<=65535 else 4),
            'bounds':[atlas.min(0).tolist(),atlas.max(0).tolist()], 'sourceWorldBounds':[world.min(0).tolist(),world.max(0).tolist()],
            'originalObjectToWorld':matrix.ravel().tolist(),'sourceToAtlas':C.ravel().tolist(),
            'parent':obj.parent.name if obj.parent else None, 'collections':[c.name for c in obj.users_collection],
            'curve':{'dimensions':obj.data.dimensions,'bevelDepth':obj.data.bevel_depth,'bevelResolution':obj.data.bevel_resolution,
                'resolution':obj.data.resolution_u,'splines':len(obj.data.splines), 'cyclic':[s.use_cyclic_u for s in obj.data.splines]},
            'modifiers':0,'constraints':0,'animationData':False,'hideViewport':obj.hide_viewport,'hideRender':obj.hide_render})
        print('NERVE_EXPORT', name, len(world), len(triangles), flush=True)
    finally: evaluated.to_mesh_clear()
proof = {'sourcePath':str(SOURCE.relative_to(ROOT)), 'sourceSha256':sha(SOURCE.read_bytes()), 'runtimeSha256':sha(Path(bpy.app.binary_path).read_bytes()),
    'scriptsAutoExecute':False,'loadUI':False,'sourceFrame':0,'unitScale':1,'sourceModified':False,
    'geometryMeaning':'Evaluated original bevelled Curve surface in source-world coordinates. Original branch topology and radius; no synthetic centerline or endpoint interpolation.',
    'rows':rows}
(ROOT / 'work/evidence/T63/evaluated-surfaces.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
