"""Repair only the emitted calf contact patch; retain exact native masks and bones."""
import pathlib,sys,json,copy,numpy as np
R=pathlib.Path(__file__).resolve().parents[4];O=pathlib.Path(__file__).parent
sys.path[:0]=[str(R/'work/tools'),str(R/'work/evidence/T66/serial-completion-2026-10-02/unit-01'),str(R/'work/evidence/T66/priority-trunk-2026-10-05')]
from verify_glb_interpolation import read_glb,channel_data,node_positions,bounded_inside,verify
from author_source_surface_motion import array,normals,container
from derive_source_surface_motion import append_bytes,sha
from trunk_contact_patch import source_topology_contact_patch_corrective
d=O/'enlargement-knee-right-r4';raw,old,oldbuf=read_glb(d/'motion.glb');tr=channel_data(old,oldbuf);nodes={n['extras']['sourceKey']:i for i,n in enumerate(old['nodes'])};doc=copy.deepcopy(old);buf=bytearray(oldbuf)
p=json.loads((d/'input.json').read_text());key='ZA-c7010a9-eafc9174265a4bbc41581e2a';e=next(e for e in p['members'] if e['sourceKey']==key);ni=nodes[key];prim=doc['meshes'][doc['nodes'][ni]['mesh']]['primitives'][0];pos=array(old,oldbuf,prim['attributes']['POSITION']);tri=array(old,oldbuf,prim['indices']).reshape(-1,3);normal=array(old,oldbuf,prim['attributes']['NORMAL']);M=np.array(doc['nodes'][ni]['matrix']).reshape(4,4).T;rest=node_positions(old,oldbuf,tr,ni,0);locked=set(e['fixedVertexIndices'])|set(e['movingVertexIndices']);q=json.loads((d/('interpolation-'+key+'.json')).read_text());failed={r['boneSourceKey'] for r in q['contact']['failures']};contacts=[]
for bk in failed:
 bn=nodes[bk];bt=array(old,oldbuf,old['meshes'][old['nodes'][bn]['mesh']]['primitives'][0]['indices']).reshape(-1,3);bw=node_positions(old,oldbuf,tr,bn,0);contacts.append((bk,bn,bt,bounded_inside(rest,bw,bt)))
def put(v,typ,count):
 off,ln=append_bytes(buf,v);doc['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':ln});ai=len(doc['accessors']);doc['accessors'].append({'bufferView':len(doc['bufferViews'])-1,'componentType':5126,'count':int(count),'type':typ});return ai
repairs=[];prim['targets']=[]
for step in range(1,13):
 t=3*step/12;frame=node_positions(old,oldbuf,tr,ni,t);active=[(bk,node_positions(old,oldbuf,tr,bn,t),bt,baseline) for bk,bn,bt,baseline in contacts]
 # Explicit source-topology corrective guards the one failed free vertex and its
 # local patch, not a new attachment/normal spacing or collider exemption.
 frame,c=source_topology_contact_patch_corrective(frame,rest,tri,active,locked,[],margin_metres=.0012,contact_guard_metres=.003,shape_floor=.12,patch_rings=3,shape_seed_vertices=[323],force_contact_guard=True)
 repairs.append({'step':step,'corrective':c});local=(frame-M[:3,3])@np.linalg.inv(M[:3,:3]).T;local[e['fixedVertexIndices']]=pos[e['fixedVertexIndices']];delta=(local-pos).astype('<f4');pa=put(delta.tobytes(),'VEC3',len(pos));doc['accessors'][pa].update(min=delta.min(0).tolist(),max=delta.max(0).tolist());prim['targets'].append({'POSITION':pa,'NORMAL':put((normals(local,tri)-normal).astype('<f4').tobytes(),'VEC3',len(pos))})
motion=container(doc,buf);(d/'motion.glb').write_bytes(motion);_,nd,nb=read_glb(d/'motion.glb');nt=channel_data(nd,nb);reuse=[]
for k,n in nodes.items():
 if k==key:continue
 error=max(float(np.linalg.norm(node_positions(old,oldbuf,tr,n,t)-node_positions(nd,nb,nt,n,t),axis=1).max()) for t in np.linspace(0,3,49));assert error==0;reuse.append({'sourceKey':k,'maximumDifferenceMetres':error,'samples':49})
geo=json.loads((d/'geometry-record.json').read_text());geo.update(motionSha256=sha(motion),motionBytes=len(motion));(d/'geometry-record.json').write_text(json.dumps(geo,ensure_ascii=False,indent=2)+'\n');(d/'repair-receipt.json').write_text(json.dumps({'oldMotionSha256':sha(raw),'newMotionSha256':sha(motion),'changedSourceKey':key,'unchangedReplay':reuse,'patches':repairs,'sourceModified':False,'measuredSpacingClaimed':False},ensure_ascii=False,indent=2)+'\n')
print('targeted calf patch emitted; full final contact/pose/outcome QC still required',flush=True)
