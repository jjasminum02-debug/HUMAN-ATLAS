"""Rectus-only native attachment-role/weight repair. Keep all other emitted streams."""
import sys,json,copy,math
from pathlib import Path
import numpy as np
R=Path.cwd();E=R/'work/evidence/MV2/2026-10-12-q01-r1'
sys.path[:0]=[str(R/'work/tools'),str(R/'work/evidence/T66/serial-completion-2026-10-02/unit-01')]
from verify_glb_interpolation import read_glb,channel_data,node_positions,verify
from author_source_surface_motion import array,normals,container,rotation
from author_t66_family_motion import deform
from derive_source_surface_motion import append_bytes,sha
names={r['sourceKey']:r['name'] for r in json.loads((R/'atlas-data/source-cache/datasets/za/compiled/manifest.json').read_text())['instances']}
results=[]
for side in ['left','right']:
 oldpath=R/f'atlas-data/assets/motion/t66-priority-s05-{side}-knee/motion.glb';raw,old,ob=read_glb(oldpath);tr=channel_data(old,ob);d=copy.deepcopy(old);buf=bytearray(ob);nodes={n['extras']['sourceKey']:i for i,n in enumerate(d['nodes'])};p=json.loads((R/f'work/evidence/T66/priority-integration-2026-10-05/adopted-knee-{side}/input.json').read_text());e=next(e for e in p['members'] if e['role']=='deforming_muscle_surface');key=e['sourceKey'];ni=nodes[key];prim=d['meshes'][d['nodes'][ni]['mesh']]['primitives'][0];pos=array(old,ob,prim['attributes']['POSITION']);tri=array(old,ob,prim['indices']).reshape(-1,3);normal=array(old,ob,prim['attributes']['NORMAL']);M=np.array(d['nodes'][ni]['matrix']).reshape(4,4).T;w=node_positions(old,ob,tr,ni,0);fam=p['family'];pivot=np.array(fam['pivotMetres']);axis=np.array(fam['axis'])
 patkey=next(k for k in nodes if names[k]=='Patella.'+side[0]);hipkey=next(k for k in nodes if names[k]=='Hip bone.'+side[0]);femkey=next(k for k in nodes if names[k]=='Femur.'+side[0]);tibkey=next(k for k in nodes if names[k]=='Tibia.'+side[0]);pat=node_positions(old,ob,tr,nodes[patkey],0)
 # Inspectable source-addressed longitudinal landmarks: patellar-contact sleeve
 # ends at vertex 521, free distal taper reaches vertex closest to y=.55.
 # Neither marker is claimed as a measured histologic footprint.
 sleeve=521; taper=int(np.argmin(abs(w[:,1]-.55))); distal_y=w[sleeve,1];prox_y=w[taper,1]; assert .43<distal_y<.50 and .53<prox_y<.57
 u=np.clip((prox_y-w[:,1])/(prox_y-distal_y),0,1);weights=u*u*(3-2*u);fixed=np.flatnonzero(weights==0);moving=np.flatnonzero(weights==1)
 locked=set(fixed)|set(moving); base=w[tri];baseN=np.cross(base[:,1]-base[:,0],base[:,2]-base[:,0]);baseArea=np.linalg.norm(baseN,axis=1);good=baseArea>=1e-12; corrections=[]
 # Reuse the existing authorer's local weight relaxation, within new exact masks.
 for iteration in range(128):
  bad=set()
  for phase in [.25,.5,.75,1]:
   trial=deform(w,pivot,axis,fam['endDegrees'],phase,weights,'fractional_rotation');t=trial[tri];N=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);bad.update(np.flatnonzero(good&(((N*baseN).sum(1)<0)|(np.linalg.norm(N,axis=1)<baseArea*.1))).tolist())
  if not bad:break
  for ti in sorted(bad):
   vertices=tri[ti];pins=[v for v in vertices if v in locked];value=float(np.mean(weights[pins if pins else vertices]))
   for v in vertices:
    if v not in locked:weights[v]=value
  corrections.append({'iteration':iteration,'triangleIds':sorted(bad)})
 print(side,'landmarks',sleeve,w[sleeve],taper,w[taper], 'masks',len(fixed),len(moving))
 def put(a):
  off,ln=append_bytes(buf,a.astype('<f4').tobytes());d['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':ln});ai=len(d['accessors']);d['accessors'].append({'bufferView':len(d['bufferViews'])-1,'componentType':5126,'count':len(a),'type':'VEC3','min':a.min(0).tolist(),'max':a.max(0).tolist()});return ai
 prim['targets']=[]
 for step in range(1,13):
  frame=deform(w,pivot,axis,fam['endDegrees'],step/12,weights,'fractional_rotation');local=(frame-M[:3,3])@np.linalg.inv(M[:3,:3]).T;local[fixed]=pos[fixed];prim['targets'].append({'POSITION':put(local-pos),'NORMAL':put(normals(local,tri)-normal)})
 dest=E/(side+'-candidate-r2');dest.mkdir(exist_ok=True);new=container(d,buf);(dest/'motion.glb').write_bytes(new);rr,nd,nb=read_glb(dest/'motion.glb');nt=channel_data(nd,nb);checks={}
 for ck in [hipkey,femkey,patkey,tibkey]:
  q=verify(dest/'motion.glb',key,[ck],subdivisions=8);checks[names[ck]]=q;(dest/('qc-'+names[ck].replace(' ','-')+'.json')).write_text(json.dumps(q,indent=2)+'\n')
 reuse={k:max(float(np.linalg.norm(node_positions(old,ob,tr,n,t)-node_positions(nd,nb,nt,n,t),axis=1).max()) for t in [0,.125,1.5,2.375,3]) for k,n in nodes.items() if k!=key};assert max(reuse.values())==0
 f=node_positions(nd,nb,nt,ni,3);body=np.flatnonzero(w[:,1]>=prox_y);r={'side':side,'key':key,'originalSha256':sha(raw),'candidateSha256':sha(new),'bytesBefore':len(raw),'bytesAfter':len(new),'changedNode':ni,'changedStreams':'rectus POSITION/NORMAL morph targets only; same topology/source/frame/pivot/angle/duration/LINEAR tracks','reuseMaxMetres':max(reuse.values()),'unchangedNodes':len(reuse),'sourceLandmarks':[{'sourceKey':key,'vertexIndex':sleeve,'worldMetres':w[sleeve].tolist(),'meaning':'inspected sleeve near superior patella; transported with patella/tibia'},{'sourceKey':key,'vertexIndex':taper,'worldMetres':w[taper].tolist(),'meaning':'inspected distal taper-to-belly transition; proximal thigh stays in fixed hip/femur frame'}],'fixedVertexIndices':fixed.tolist(),'movingVertexIndices':moving.tolist(),'weights':weights.tolist(),'weightRelaxation':corrections,'fixedBoneKeys':[hipkey,femkey],'movingBoneKeys':[patkey,tibkey],'bodyMaxDisplacementMm':float(np.linalg.norm(f[body]-w[body],axis=1).max()*1000),'maxDisplacementMm':float(np.linalg.norm(f-w,axis=1).max()*1000),'checks':{k:{'passed':v['passed'],'flips':v['geometry']['flippedFaceSamples'],'minArea':v['geometry']['minimumAreaRatio'],'newContactMax':v['contact']['newContainmentMaximum']} for k,v in checks.items()},'rights':p['rights'],'measuredFootprints':False,'physiologicalNaturalnessApproved':False}
 (dest/'repair-record.json').write_text(json.dumps(r,indent=2)+'\n');results.append({k:v for k,v in r.items() if k not in ['weights','fixedVertexIndices','movingVertexIndices']})
(E/'candidate-summary-r2.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
