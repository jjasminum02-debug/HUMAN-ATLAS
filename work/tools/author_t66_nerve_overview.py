"""Native Curve tessellation LOD; original control points, radius, branch and full detail retained."""
import ast, hashlib, json, struct
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2]
PROOF=ROOT/'work/evidence/T66/implementation-2026-10-02/nerve-evaluated-surfaces.json'
proof=json.loads(PROOF.read_text())
assert hashlib.sha256((ROOT/proof['sourcePath']).read_bytes()).hexdigest()==proof['sourceSha256']
assert not bpy.context.preferences.filepaths.use_scripts_auto_execute
tree=ast.parse((ROOT/'atlas-data/tools/datasets/compile_za.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['arrays','glb','sampled_error']],type_ignores=[]),'<pinned-serializer>','exec'))
bpy.ops.wm.open_mainfile(filepath=str(ROOT/proof['sourcePath']),load_ui=False,use_scripts=False)
dg=bpy.context.evaluated_depsgraph_get()
for row in proof['rows']:
    obj=bpy.data.objects[row['name']]
    evaluated=obj.evaluated_get(dg); mesh=evaluated.to_mesh()
    try: original,tri,_,_,_=arrays(mesh)
    finally: evaluated.to_mesh_clear()
    curve=obj.data.copy(); curve.resolution_u=6;curve.bevel_resolution=1
    for spline in curve.splines: spline.resolution_u=6
    temp=bpy.data.objects.new('T66 temporary native curve LOD',curve)
    bpy.context.scene.collection.objects.link(temp);temp.matrix_world=obj.matrix_world.copy();dg.update()
    e=temp.evaluated_get(dg);m=e.to_mesh()
    try:
        p,t,ip,n,it=arrays(m);matrix=np.array(obj.matrix_world,dtype='f8')
        error=sampled_error(original,tri,p,t,matrix)
        # Surface tessellation error only. No centerline fitting, shortening or new branches.
        assert error<=0.0015,(row['name'],error)
        world=np.array([tuple(obj.matrix_world @ Vector(v)) for v in ip],dtype='<f4')
        nm=obj.matrix_world.to_3x3().inverted().transposed()
        normals=np.array([tuple((nm @ Vector(v)).normalized()) for v in n],dtype='<f4')
        if obj.matrix_world.to_3x3().determinant()<0:it=it[:,[0,2,1]].copy()
        data=glb(world,normals,it);path=ROOT/row['path'].replace('.glb','-overview.glb');path.write_bytes(data)
        row['overview']={'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(data).hexdigest(),
            'vertices':len(world),'triangles':len(it),'geometryBytes':len(world)*24+it.size*(2 if len(world)<=65535 else 4),
            'sampledSymmetricSurfaceErrorMeters':error,'sampleCountEachDirection':min(192,len(original)),
            'resolution':6,'bevelResolution':1,'nativeControlPointsPreserved':True,'nativeRadiusPreserved':True,'nativeSplineCountPreserved':True}
        print('NERVE_LOD',row['name'],len(it),error,flush=True)
    finally:
        e.to_mesh_clear();bpy.data.objects.remove(temp,do_unlink=True);bpy.data.curves.remove(curve)
proof['overviewMeaning']='Native original Curve tessellation at resolution 6/bevel 1, unchanged control points/radius/splines; symmetric deterministic sampled surface error <=1.5mm, not a Hausdorff guarantee. Full original tessellation retained for detail.'
assert hashlib.sha256((ROOT/proof['sourcePath']).read_bytes()).hexdigest()==proof['sourceSha256']
PROOF.write_text(json.dumps(proof,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
