"""Local native-face branch guard with source-coincident seams and shape constraints.

Refine an overly broad engineering displacement group into actual coincident
vertex seams. No source vertex/triangle is removed, merged or reclassified.
"""
import pathlib,sys,json,copy,numpy as np
R=pathlib.Path(__file__).resolve().parents[4];O=pathlib.Path(__file__).parent;d=O/'enlargement-trunk/flex'
sys.path[:0]=[str(R/'work/tools'),str(R/'work/evidence/T66/serial-completion-2026-10-02/unit-01'),str(R/'work/evidence/T66/priority-trunk-2026-10-05')]
from verify_glb_interpolation import read_glb,channel_data,node_positions,verify,bounded_inside
from author_source_surface_motion import array,normals,container
from derive_source_surface_motion import append_bytes,sha
from t66_contact_correctives import nearest_surface
from trunk_contact_patch import source_topology_contact_patch_corrective
save=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
raw,old,ob=read_glb(d/'motion.glb');tr=channel_data(old,ob);doc=copy.deepcopy(old);buf=bytearray(ob);nodes={n['extras']['sourceKey']:i for i,n in enumerate(old['nodes'])};inp=json.loads((d/'authored-input.json').read_text());entries={e['sourceKey']:e for e in inp['surfaceFields']};changed=[];records=[]
def put(v,typ,count):
 off,ln=append_bytes(buf,v);doc['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':ln});ai=len(doc['accessors']);doc['accessors'].append({'bufferView':len(doc['bufferViews'])-1,'componentType':5126,'count':int(count),'type':typ});return ai
for key in ['ZA-c7010a9-62a4fba42674f5d453c6e277','ZA-c7010a9-bef3937bee85a8c7bcc77d9c']:
 e=entries[key];q=verify(d/'motion.glb',key,e['contactBoneKeys'],4);assert q['geometry']['passed'];ni=nodes[key];node=doc['nodes'][ni];prim=doc['meshes'][node['mesh']]['primitives'][0];pos=array(old,ob,prim['attributes']['POSITION']);tri=array(old,ob,prim['indices']).reshape(-1,3);normal=array(old,ob,prim['attributes']['NORMAL']);M=np.array(node['matrix']).reshape(4,4).T;rest=node_positions(old,ob,tr,ni,0);locked=set(e['fixedVertexIndices']);seammap={}
 for v in range(len(rest)):seammap.setdefault(tuple(np.round(rest[v],7)),[]).append(v)
 groups=[g for g in seammap.values() if len(g)>1 and not set(g)&locked];contacts=[];guards=[]
 for bk in e['contactBoneKeys']:
  bn=nodes[bk];bt=array(old,ob,old['meshes'][old['nodes'][bn]['mesh']]['primitives'][0]['indices']).reshape(-1,3);bw=node_positions(old,ob,tr,bn,0);contacts.append((bk,bn,bt,bounded_inside(rest,bw,bt)))
 for bk,v in sorted({(r['boneSourceKey'],v) for r in q['contact']['failures'] for v in r['sourceVertexIndices']}):
  assert v not in locked;bn=nodes[bk];bt=next(c[2] for c in contacts if c[0]==bk);bw=node_positions(old,ob,tr,bn,0);dist=[]
  for tt in bt:dist.append(float(np.linalg.norm(nearest_surface(rest[[v]],bw,np.asarray([tt]))[0]-rest[v])))
  ti=int(np.argmin(dist));ids=bt[ti];nn=np.cross(bw[ids[1]]-bw[ids[0]],bw[ids[2]]-bw[ids[0]]);nn/=np.linalg.norm(nn);sign=1 if np.dot(rest[v]-bw[ids[0]],nn)>=0 else -1;guards.append({'boneSourceKey':bk,'vertex':v,'boneTriangleId':ti,'indices':ids.tolist(),'exteriorSign':sign,'seam':next((g for g in groups if v in g),[v])})
 prim['targets']=[];steps=[];print('branch-aware patch',key,'coincident seams',len(groups),'native face guards',len(guards),flush=True)
 for step in range(1,65):
  t=2.5*step/64;frame=node_positions(old,ob,tr,ni,t).copy();active=[(bk,node_positions(old,ob,tr,bn,t),bt,baseline) for bk,bn,bt,baseline in contacts];anchors=set();seeds=set()
  # Preserve actual native near-sternum points in the moving sternum frame.
  # This is a local passive engineering carrier, not a measured footprint.
  carrier=next(c for c in contacts if c[0]=='ZA-c7010a9-a7c8e4f4119fede30c949007');bk,bn,bt,baseline=carrier;nativebone=node_positions(old,ob,tr,bn,0);posedbone=node_positions(old,ob,tr,bn,t);T=np.linalg.lstsq(np.c_[nativebone,np.ones(len(nativebone))],posedbone,rcond=None)[0]
  for vertex in [2306,2391]:
   assert vertex not in locked;frame[vertex]=np.r_[rest[vertex],1.]@T;anchors.add(vertex);seeds.add(vertex)
  # Temporary directional anchors constrain the corrective, not anatomical
  # attachment masks. The actual fixed source mask remains unchanged.
  frame,c=source_topology_contact_patch_corrective(frame,rest,tri,active,locked|anchors,[],margin_metres=.0002,contact_guard_metres=.0007,shape_floor=.12,patch_rings=8,shape_seed_vertices=sorted(set(map(int,tri[np.isin(tri,list(anchors)).any(axis=1)].ravel()))-(locked|anchors)),topology_groups=[g for g in groups if not set(g)&(locked|anchors)],force_contact_guard=bool(seeds));print('carrier step',step,flush=True);steps.append({'step':step,'directionalGuardSourceVertices':sorted(anchors),'corrective':c});local=(frame-M[:3,3])@np.linalg.inv(M[:3,:3]).T;local[list(locked)]=pos[list(locked)];delta=(local-pos).astype('<f4');pa=put(delta.tobytes(),'VEC3',len(pos));doc['accessors'][pa].update(min=delta.min(0).tolist(),max=delta.max(0).tolist());prim['targets'].append({'POSITION':pa,'NORMAL':put((normals(local,tri)-normal).astype('<f4').tobytes(),'VEC3',len(pos))})
 doc['meshes'][node['mesh']]['weights']=[0]*64;node['weights']=[0]*64;ta=put(np.linspace(0,2.5,65).astype('<f4').tobytes(),'SCALAR',65);doc['accessors'][ta].update(min=[0],max=[2.5]);wo=np.zeros((65,64),dtype='<f4');wo[1:]=np.eye(64);wa=put(wo.tobytes(),'SCALAR',wo.size);anim=doc['animations'][0];anim['channels']=[c for c in anim['channels'] if c['target']['node']!=ni];si=len(anim['samplers']);anim['samplers'].append({'input':ta,'output':wa,'interpolation':'LINEAR'});anim['channels'].append({'sampler':si,'target':{'node':ni,'path':'weights'}});changed.append(key);records.append({'sourceKey':key,'nativeFaceGuards':guards,'sourceCoincidentSeams':groups,'steps':steps,'sourceRestAndFixedMasksPreserved':True,'measuredSpacingClaimed':False})
motion=container(doc,buf);(d/'motion.glb').write_bytes(motion);_,nd,nb=read_glb(d/'motion.glb');nt=channel_data(nd,nb);pose=json.loads((d/'glb-pose-qc.json').read_text());geo=json.loads((d/'geometry-record.json').read_text());failures=[];reuse=[]
for key,e in entries.items():
 qp=d/('interpolation-'+key+'.json')
 if key in changed:q=verify(d/'motion.glb',key,e['contactBoneKeys'],4)
 else:
  error=max(float(np.linalg.norm(node_positions(old,ob,tr,nodes[key],t)-node_positions(nd,nb,nt,nodes[key],t),axis=1).max()) for t in np.linspace(0,2.5,65));assert error==0;reuse.append({'sourceKey':key,'samples':65,'maximumDifferenceMetres':error});q=json.loads(qp.read_text());assert q['passed']
 q['motionGlbSha256']=sha(motion);save(qp,q);row=next(r for r in pose['rows'] if r['sourceKey']==key);row.update(passed=q['passed'],geometryQcSha256=sha(qp.read_bytes()));metric=next(r for r in geo['surfaceMetrics'] if r['sourceKey']==key);metric.update(flips=q['geometry']['flippedFaceSamples'],minimumAreaRatio=q['geometry']['minimumAreaRatio']);failures.extend(q['contact']['failures']);print(key,q['passed'],q['geometry']['flippedFaceSamples'],q['contact']['newContainmentMaximum'],flush=True)
pose.update(passed=all(r['passed'] for r in pose['rows']),motionSha256=sha(motion));geo.update(motionSha256=sha(motion),motionBytes=len(motion));save(d/'glb-pose-qc.json',pose);save(d/'geometry-record.json',geo);save(d/'contact-qc.json',{'passed':not failures,'failures':failures,'newContainmentMaximum':max((r['newContainedVertexCount'] for r in failures),default=0),'baselineOverlapPreserved':True});save(d/'native-sternum-carrier-receipt.json',{'oldMotionSha256':sha(raw),'newMotionSha256':sha(motion),'changedSourceKeys':changed,'authoredCorrectives':records,'unchangedDeformerReplay':reuse,'sourceModified':False,'measuredSpacingClaimed':False});assert pose['passed'],'branch-aware local source patch remains unresolved'
save(d/'complete.json',{'kind':'flex','clipId':doc['animations'][0]['name'],'family':geo['family'],'members':geo['members'],'motionSha256':sha(motion),'restSha256':geo['restSha256'],'glbInterpolationQcPaths':{e['sourceKey']:str((d/('interpolation-'+e['sourceKey']+'.json')).relative_to(R)) for e in inp['surfaceFields']},'contextSurfaces':len(geo['members']),'deformingSurfaces':len(entries)})
