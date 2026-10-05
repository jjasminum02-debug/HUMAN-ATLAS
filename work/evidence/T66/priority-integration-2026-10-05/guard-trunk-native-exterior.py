"""Keep a contact corrective on the native observed exterior side of a thin bone.

Closest-face projection can jump from the anterior to posterior sternum face
between valid keys. Author a continuous native-face half-plane guard for the
two failing passive internal-oblique patches. No normal spacing is measured.
"""
import pathlib,sys,json,copy,numpy as np
R=pathlib.Path(__file__).resolve().parents[4];O=pathlib.Path(__file__).parent;d=O/'enlargement-trunk/flex'
sys.path[:0]=[str(R/'work/tools'),str(R/'work/evidence/T66/serial-completion-2026-10-02/unit-01')]
from verify_glb_interpolation import read_glb,channel_data,node_positions,verify
from author_source_surface_motion import array,normals,container
from derive_source_surface_motion import append_bytes,sha
from t66_contact_correctives import nearest_surface
save=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
raw,old,oldbuf=read_glb(d/'motion.glb');oldtr=channel_data(old,oldbuf);doc=copy.deepcopy(old);buf=bytearray(oldbuf);nodes={n['extras']['sourceKey']:i for i,n in enumerate(old['nodes'])};inp=json.loads((d/'authored-input.json').read_text());entries={e['sourceKey']:e for e in inp['surfaceFields']};changed=[];records=[]
def put(v,typ,count):
 off,ln=append_bytes(buf,v);doc['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':ln});ai=len(doc['accessors']);doc['accessors'].append({'bufferView':len(doc['bufferViews'])-1,'componentType':5126,'count':int(count),'type':typ});return ai
for key,e in entries.items():
 q=json.loads((d/('interpolation-'+key+'.json')).read_text())
 if q['passed']:continue
 assert q['geometry']['passed'];ni=nodes[key];node=doc['nodes'][ni];prim=doc['meshes'][node['mesh']]['primitives'][0];pos=array(old,oldbuf,prim['attributes']['POSITION']);tri=array(old,oldbuf,prim['indices']).reshape(-1,3);normal=array(old,oldbuf,prim['attributes']['NORMAL']);M=np.array(node['matrix']).reshape(4,4).T;rest=node_positions(old,oldbuf,oldtr,ni,0);locked=set(e['fixedVertexIndices']);groups=[g for g in e['sourceTopologyCoupledVertexGroups'] if not set(g)&locked];guards=[]
 pairs=sorted({(r['boneSourceKey'],v) for r in q['contact']['failures'] for v in r['sourceVertexIndices']})
 for bk,v in pairs:
  assert v not in locked;bn=nodes[bk];bprim=old['meshes'][old['nodes'][bn]['mesh']]['primitives'][0];bt=array(old,oldbuf,bprim['indices']).reshape(-1,3);bw=node_positions(old,oldbuf,oldtr,bn,0);dist=[]
  for t in bt:
   closest=nearest_surface(rest[[v]],bw,np.asarray([t]))[0];dist.append(float(np.linalg.norm(closest-rest[v])))
  ti=int(np.argmin(dist));t=bt[ti];nn=np.cross(bw[t[1]]-bw[t[0]],bw[t[2]]-bw[t[0]]);nn/=np.linalg.norm(nn);sign=1 if np.dot(rest[v]-bw[t[0]],nn)>=0 else -1;group=next((g for g in groups if v in g),[v]);guards.append({'boneSourceKey':bk,'sourceVertexIndex':v,'boneTriangleId':ti,'boneTriangleVertexIndices':t.tolist(),'exteriorSign':sign,'affectedSourceVertices':group,'sourceRestDistanceMetres':dist[ti]})
 prim['targets']=[];maxCorrection=0.
 for step in range(1,65):
  t=2.5*step/64;frame=node_positions(old,oldbuf,oldtr,ni,t).copy();before=frame.copy()
  for iteration in range(64):
   largest=0.
   for g in guards:
    bw=node_positions(old,oldbuf,oldtr,nodes[g['boneSourceKey']],t);ids=g['boneTriangleVertexIndices'];nn=np.cross(bw[ids[1]]-bw[ids[0]],bw[ids[2]]-bw[ids[0]]);nn=nn/np.linalg.norm(nn)*g['exteriorSign'];deficit=.0024-float(np.dot(frame[g['sourceVertexIndex']]-bw[ids[0]],nn))
    if deficit>0:frame[g['affectedSourceVertices']]+=nn*(deficit+1e-8);largest=max(largest,deficit)
   if largest<1e-9:break
  assert np.max(np.linalg.norm(frame[list(locked)]-rest[list(locked)],axis=1))<1e-6;maxCorrection=max(maxCorrection,float(np.linalg.norm(frame-before,axis=1).max()));local=(frame-M[:3,3])@np.linalg.inv(M[:3,:3]).T;local[list(locked)]=pos[list(locked)];delta=(local-pos).astype('<f4');pa=put(delta.tobytes(),'VEC3',len(pos));doc['accessors'][pa].update(min=delta.min(0).tolist(),max=delta.max(0).tolist());prim['targets'].append({'POSITION':pa,'NORMAL':put((normals(local,tri)-normal).astype('<f4').tobytes(),'VEC3',len(pos))})
 doc['meshes'][node['mesh']]['weights']=[0]*64;node['weights']=[0]*64;ta=put(np.linspace(0,2.5,65).astype('<f4').tobytes(),'SCALAR',65);doc['accessors'][ta].update(min=[0],max=[2.5]);wo=np.zeros((65,64),dtype='<f4');wo[1:]=np.eye(64);wa=put(wo.tobytes(),'SCALAR',wo.size);anim=doc['animations'][0];anim['channels']=[c for c in anim['channels'] if c['target']['node']!=ni];si=len(anim['samplers']);anim['samplers'].append({'input':ta,'output':wa,'interpolation':'LINEAR'});anim['channels'].append({'sampler':si,'target':{'node':ni,'path':'weights'}});changed.append(key);records.append({'sourceKey':key,'guards':guards,'maximumAdditionalCorrectiveMetres':maxCorrection,'sourceRestAndHeldMasksPreserved':True,'measuredSpacingClaimed':False})
motion=container(doc,buf);(d/'motion.glb').write_bytes(motion);_,new,nb=read_glb(d/'motion.glb');nt=channel_data(new,nb);reuse=[];pose=json.loads((d/'glb-pose-qc.json').read_text());geo=json.loads((d/'geometry-record.json').read_text());failures=[]
for key,e in entries.items():
 qp=d/('interpolation-'+key+'.json')
 if key in changed:q=verify(d/'motion.glb',key,e['contactBoneKeys'],4)
 else:
  err=max(float(np.linalg.norm(node_positions(old,oldbuf,oldtr,nodes[key],t)-node_positions(new,nb,nt,nodes[key],t),axis=1).max()) for t in np.linspace(0,2.5,65));assert err==0;reuse.append({'sourceKey':key,'samples':65,'maximumDifferenceMetres':err});q=json.loads(qp.read_text());assert q['passed']
 q['motionGlbSha256']=sha(motion);save(qp,q);row=next(r for r in pose['rows'] if r['sourceKey']==key);row.update(passed=q['passed'],geometryQcSha256=sha(qp.read_bytes()));metric=next(r for r in geo['surfaceMetrics'] if r['sourceKey']==key);metric.update(flips=q['geometry']['flippedFaceSamples'],minimumAreaRatio=q['geometry']['minimumAreaRatio']);failures.extend(q['contact']['failures']);print(key,q['passed'],q['geometry']['minimumAreaRatio'],q['contact']['newContainmentMaximum'],flush=True)
pose.update(passed=all(r['passed'] for r in pose['rows']),motionSha256=sha(motion));geo.update(motionSha256=sha(motion),motionBytes=len(motion));save(d/'glb-pose-qc.json',pose);save(d/'geometry-record.json',geo);save(d/'contact-qc.json',{'passed':not failures,'failures':failures,'newContainmentMaximum':max((r['newContainedVertexCount'] for r in failures),default=0),'baselineOverlapPreserved':True,'continuousCollisionFreedomClaimed':False});save(d/'native-exterior-guard-receipt.json',{'oldMotionSha256':sha(raw),'newMotionSha256':sha(motion),'changedSourceKeys':changed,'authoredContactGuards':records,'unchangedDeformerReplay':reuse,'sourceModified':False,'measuredSpacingClaimed':False});assert pose['passed'],'native exterior contact branch still unresolved'
save(d/'complete.json',{'kind':'flex','clipId':doc['animations'][0]['name'],'family':geo['family'],'members':geo['members'],'motionSha256':sha(motion),'restSha256':geo['restSha256'],'glbInterpolationQcPaths':{e['sourceKey']:str((d/('interpolation-'+e['sourceKey']+'.json')).relative_to(R)) for e in inp['surfaceFields']},'contextSurfaces':len(geo['members']),'deformingSurfaces':len(entries)})
