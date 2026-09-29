"""Pinned Blender adapter. Writes derived cache only; never saves the source .blend.
Run with the verified Blender --background --factory-startup --disable-autoexec.
Object checkpoints are content-verified; a bad object is isolated, never silently omitted.
"""
import hashlib
import json
from pathlib import Path
import struct
import time
import bpy
import numpy as np
from mathutils.bvhtree import BVHTree
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
INPUT = ROOT / 'work/evidence/T98/astra-resolution-2026-09-29'
OUT = ROOT / 'atlas-data/source-cache/datasets/za'
SOURCE = ROOT / 'atlas-data/source-cache/z-anatomy/t97/extracted/Z-Anatomy/Startup.blend'
def sha(data): return hashlib.sha256(data).hexdigest()
def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp'); tmp.write_text(json.dumps(obj, ensure_ascii=False, separators=(',', ':'))+'\n'); tmp.replace(path)
def arrays(mesh):
    mesh.calc_loop_triangles(); mesh.calc_normals_split()
    p=np.empty((len(mesh.vertices),3),dtype='<f4'); mesh.vertices.foreach_get('co',p.ravel())
    t=np.empty((len(mesh.loop_triangles),3),dtype='<i4'); mesh.loop_triangles.foreach_get('vertices',t.ravel())
    loops=np.empty((len(mesh.loop_triangles),3),dtype='<i4'); mesh.loop_triangles.foreach_get('loops',loops.ravel())
    normals=np.empty((len(mesh.loops),3),dtype='<f4'); mesh.loops.foreach_get('normal',normals.ravel())
    # One indexed vertex per distinct position/normal pair, preserving source smoothing seams.
    packed=np.concatenate((p[t.ravel()],normals[loops.ravel()]),axis=1)
    vertices,index=np.unique(packed,axis=0,return_inverse=True)
    return p,t,vertices[:,:3].copy(),vertices[:,3:].copy(),index.astype('<u4').reshape((-1,3))
def glb(p,n,t):
    assert len(p) and len(t) and np.isfinite(p).all() and np.isfinite(n).all()
    idx=t.astype('<u2') if len(p)<=65535 else t.astype('<u4')
    blobs=[p.astype('<f4').tobytes(),n.astype('<f4').tobytes(),idx.tobytes()]
    binary=bytearray(); views=[]
    for b in blobs:
        views.append({'buffer':0,'byteOffset':len(binary),'byteLength':len(b)})
        binary.extend(b); binary.extend(b'\0'*((-len(binary))%4))
    doc={'asset':{'version':'2.0','generator':'HUMAN ATLAS generic indexed adapter'},'scene':0,'scenes':[{'nodes':[0]}],
         'nodes':[{'mesh':0,'name':'resource'}], 'meshes':[{'primitives':[{'attributes':{'POSITION':0,'NORMAL':1},'indices':2}]}],
         'buffers':[{'byteLength':len(binary)}],'bufferViews':views,'accessors':[
             {'bufferView':0,'componentType':5126,'count':len(p),'type':'VEC3','min':p.min(0).tolist(),'max':p.max(0).tolist()},
             {'bufferView':1,'componentType':5126,'count':len(n),'type':'VEC3'},
             {'bufferView':2,'componentType':5123 if idx.dtype.itemsize==2 else 5125,'count':idx.size,'type':'SCALAR'}]}
    j=json.dumps(doc,separators=(',',':')).encode(); j+=b' '*((-len(j))%4)
    return struct.pack('<III',0x46546c67,2,28+len(j)+len(binary))+struct.pack('<I4s',len(j),b'JSON')+j+struct.pack('<I4s',len(binary),b'BIN\0')+binary

def sampled_error(a,at,b,bt,matrix):
    # Deterministic symmetric sampled surface distance, not a Hausdorff guarantee.
    def world(p): return p.astype('f8') @ matrix[:3,:3].T + matrix[:3,3]
    a,b=world(a),world(b)
    ta=BVHTree.FromPolygons(a.tolist(),at.tolist(),all_triangles=True)
    tb=BVHTree.FromPolygons(b.tolist(),bt.tolist(),all_triangles=True)
    worst=0.
    for points,tree in [(a,tb),(b,ta)]:
        for i in np.linspace(0,len(points)-1,min(192,len(points)),dtype=int):
            hit=tree.find_nearest(Vector(points[i])); worst=max(worst,float(hit[3]))
    return worst

def main():
    start=time.time(); catalog=json.loads((INPUT/'source-catalog.json').read_text())
    assert sha(SOURCE.read_bytes())==catalog['sourceHash']
    assert not bpy.context.preferences.filepaths.use_scripts_auto_execute
    assert bpy.app.version[:2]==(3,5)
    runtime=sha(Path(bpy.app.binary_path).read_bytes())
    assert runtime=='23171ca8704539b44c94cb370894cb3b38908530c012267bed079326d7be95b0'
    fingerprint=sha(Path(__file__).read_bytes()+(INPUT/'source-catalog.json').read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    assert bpy.context.scene.frame_current==0 and bpy.context.scene.unit_settings.scale_length==1
    dg=bpy.context.evaluated_depsgraph_get(); dg.update()
    temporary=bpy.data.scenes.new('compiler temporary - never saved')
    C=np.array([[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1]],dtype='f8')
    done=[]; failures=[]; reused=0
    for row in catalog['objects']:
        key=row['sourceKey']; checkpoint=OUT/'units'/f'{key}.json'
        try:
            if checkpoint.exists():
                try:
                    prev=json.loads(checkpoint.read_text())
                    reusable=prev['fingerprint']==fingerprint and all(sha((OUT/r['path']).read_bytes())==r['sha256'] for r in prev['lods'].values())
                except (OSError, ValueError, KeyError):
                    reusable=False
                if reusable:
                    done.append(prev); reused+=1; continue
            obj=bpy.data.objects[row['name']]
            assert obj.data.name==row['dataName'] and (obj.parent.name if obj.parent else None)==row['parent']
            assert sorted(c.name for c in obj.users_collection)==row['collections']
            evaluated=obj.evaluated_get(dg); mesh=evaluated.to_mesh(preserve_all_data_layers=True,depsgraph=dg)
            try:
                p,t,ip,n,it=arrays(mesh)
                assert sha(p.tobytes()+t.tobytes())==row['evaluatedGeometrySha256'], 'evaluated snapshot changed'
                matrix=np.array(evaluated.matrix_world,dtype='f8'); assert np.isfinite(matrix).all()
                lods={}; quality=None
                def emit(level,pp,nn,tt):
                    data=glb(pp,nn,tt); h=sha(data); path=f'resources/{h}.glb'
                    target=OUT/path; target.parent.mkdir(parents=True,exist_ok=True)
                    if not target.exists() or sha(target.read_bytes())!=h: target.write_bytes(data)
                    return {'resource':h,'path':path,'sha256':h,'bytes':len(data),'geometryBytes':len(pp)*24+tt.size*(2 if len(pp)<=65535 else 4),'vertices':len(pp),'triangles':len(tt)}
                lods['detail']=emit('detail',ip,n,it)
                world=p.astype('f8')@matrix[:3,:3].T+matrix[:3,3]
                tolerance=max(.00015,min(.002,float(np.linalg.norm(world.max(0)-world.min(0)))*.01))
                for ratio in [.18,.32,.5,.75,1.]:
                    if ratio==1. or len(t)<=256:
                        op,on,ot=ip,n,it; error=0.; ratio=1.
                    else:
                        copy=mesh.copy(); temp=bpy.data.objects.new('compiler-copy',copy); temporary.collection.objects.link(temp)
                        try:
                            mod=temp.modifiers.new('overview','DECIMATE'); mod.ratio=max(ratio,256/len(t)); mod.use_collapse_triangulate=True
                            with bpy.context.temp_override(scene=temporary,view_layer=temporary.view_layers[0]):
                                td=bpy.context.evaluated_depsgraph_get(); td.update(); ev=temp.evaluated_get(td); reduced=ev.to_mesh()
                                try:
                                    rp,rt,op,on,ot=arrays(reduced); error=sampled_error(p,t,rp,rt,matrix)
                                finally: ev.to_mesh_clear()
                        finally:
                            bpy.data.objects.remove(temp,do_unlink=True); bpy.data.meshes.remove(copy)
                    if error<=tolerance:
                        lods['overview']=emit('overview',op,on,ot)
                        quality={'ratio':ratio,'sampledSymmetricErrorMetres':error,'toleranceMetres':tolerance,'samplesEachDirection':192}; break
                assert 'overview' in lods
                result={'sourceKey':key,'sourceName':row['name'],'fingerprint':fingerprint,'matrix':(C@matrix).T.ravel().tolist(),
                        'geometrySpace':'source_local','transformAppliedToGeometry':False,'lods':lods,'quality':quality}
                save(checkpoint,result); done.append(result)
            finally: evaluated.to_mesh_clear()
        except Exception as e:
            failures.append({'sourceKey':key,'name':row['name'],'error':repr(e)})
        if (len(done)+len(failures))%50==0: print('COMPILER',len(done),'ok',len(failures),'failed',flush=True)
    save(OUT/'progress.json',{'fingerprint':fingerprint,'sourceHash':catalog['sourceHash'],'runtimeHash':runtime,'completed':len(done),'reused':reused,'failures':failures,'seconds':time.time()-start})
    print('COMPILER_DONE',len(done),len(failures),flush=True)
    if failures: raise RuntimeError('Failed units are recorded in progress.json; resume same compiler')
main()
