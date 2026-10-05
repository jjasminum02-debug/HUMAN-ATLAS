"""Keep the actual diaphragm/crura intact as passive trunk context, not respiration."""
import pathlib,sys,json,copy,numpy as np
R=pathlib.Path(__file__).resolve().parents[4];O=pathlib.Path(__file__).parent
sys.path[:0]=[str(R/'work/tools'),str(R/'work/evidence/T66/serial-completion-2026-10-02/unit-01')]
from verify_glb_interpolation import read_glb,channel_data,node_positions,bounded_inside,verify
from author_source_surface_motion import array,normals,container
from derive_source_surface_motion import append_bytes,sha
from trunk_contact_patch import source_topology_contact_patch_corrective
src={r['sourceKey']:r for r in json.loads((R/'atlas-data/source-cache/datasets/za/compiled/manifest.json').read_text())['instances']};key=next(k for k,s in src.items() if s['name']=='Diaphragm')
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
for kind in sys.argv[1:]:
 d=O/kind;oldraw,doc,binary=read_glb(d/'motion.glb');buf=bytearray(binary);tr=channel_data(doc,binary);nd={n['extras']['sourceKey']:i for i,n in enumerate(doc['nodes'])};ni=nd[key];node=doc['nodes'][ni];prim=doc['meshes'][node['mesh']]['primitives'][0];pos=array(doc,binary,prim['attributes']['POSITION']);tri=array(doc,binary,prim['indices']).reshape(-1,3);normal=array(doc,binary,prim['attributes']['NORMAL']);M=np.array(src[key]['matrix']).reshape(4,4).T;rest=pos@M[:3,:3].T+M[:3,3];inp=json.loads((d/'authored-input.json').read_text());geo=json.loads((d/'geometry-record.json').read_text());pose=json.loads((d/'glb-pose-qc.json').read_text());centers=np.array(inp['segmentCentroids']);tsframes=np.array(inp['segmentTransformsAtKeys']);bones=[m['sourceKey'] for m in geo['members'] if m['role'] in ['fixed_structure','moving_structure']];near=[b for b in bones if not any(rest.max(0)[j]<node_positions(doc,binary,tr,nd[b],0).min(0)[j]-.012 or rest.min(0)[j]>node_positions(doc,binary,tr,nd[b],0).max(0)[j]+.012 for j in range(3))];ct=[]
 for b in near:
  bt=array(doc,binary,doc['meshes'][doc['nodes'][nd[b]]['mesh']]['primitives'][0]['indices']).reshape(-1,3);ct.append((b,bt,bounded_inside(rest,node_positions(doc,binary,tr,nd[b],0),bt)))
 def put(raw,typ,count):
  off,ln=append_bytes(buf,raw);doc['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':ln});ai=len(doc['accessors']);doc['accessors'].append({'bufferView':len(doc['bufferViews'])-1,'componentType':5126,'count':int(count),'type':typ});return ai
 y=rest[:,1];a=np.clip(np.searchsorted(centers[:,1],y)-1,0,len(centers)-2);v=np.clip((y-centers[a,1])/(centers[a+1,1]-centers[a,1]),0,1);v=v*v*(3-2*v);fixed=np.flatnonzero(y<=centers[0,1]).tolist();moving=np.flatnonzero(y>=np.quantile(y,.94)).tolist();prim['targets']=[];records=[]
 for step,ts in enumerate(tsframes[1:],start=1):
  w=np.zeros_like(rest)
  for i,T in enumerate(ts):
   weight=np.where(a==i,1-v,0)+np.where(a+1==i,v,0);weight[y<=centers[0,1]]=1 if i==0 else 0;weight[y>=centers[-1,1]]=1 if i==len(centers)-1 else 0;w+=weight[:,None]*(rest@T[:3,:3].T+T[:3,3])
  contacts=[(b,node_positions(doc,binary,tr,nd[b],2.5*step/16),bt,baseline) for b,bt,baseline in ct]
  w,c=source_topology_contact_patch_corrective(w,rest,tri,contacts,set(fixed),[],shape_floor=.3,patch_rings=3,margin_metres=.0004);records.append(c);local=(w-M[:3,3])@np.linalg.inv(M[:3,:3]).T;delta=(local-pos).astype('<f4');pa=put(delta.tobytes(),'VEC3',len(pos));doc['accessors'][pa].update(min=delta.min(0).tolist(),max=delta.max(0).tolist());prim['targets'].append({'POSITION':pa,'NORMAL':put((normals(local,tri)-normal).astype('<f4').tobytes(),'VEC3',len(pos))})
 node.pop('translation',None);node.pop('rotation',None);node.pop('scale',None);node['matrix']=src[key]['matrix'];node['weights']=[0]*16;doc['meshes'][node['mesh']]['weights']=[0]*16;values=np.zeros((17,16),dtype='<f4');values[1:]=np.eye(16);animation=doc['animations'][0];animation['channels']=[ch for ch in animation['channels'] if ch['target']['node']!=ni];ta=put(np.linspace(0,2.5,17).astype('<f4').tobytes(),'SCALAR',17);doc['accessors'][ta].update(min=[0],max=[2.5]);animation['samplers'].append({'input':ta,'output':put(values.ravel().tobytes(),'SCALAR',values.size),'interpolation':'LINEAR'});animation['channels'].append({'sampler':len(animation['samplers'])-1,'target':{'node':ni,'path':'weights'}});raw=container(doc,buf);(d/'motion.glb').write_bytes(raw)
 for member in geo['members']:
  if member['sourceKey']==key:member['role']='deforming_passive_surface'
 for metric in geo['surfaceMetrics']:
  if metric['sourceKey']==key:metric['role']='deforming_passive_surface'
 entry={'sourceKey':key,'fixedVertexIndices':fixed,'movingVertexIndices':moving,'weightField':'observed source-y continuous vertebral partition for passive diaphragm/crura context','sourceTopologyCoupledVertexGroups':[],'contactBoneKeys':near,'correctives':records,'measuredAttachmentFootprints':False};inp['surfaceFields'].append(entry);save(d/'authored-input.json',inp)
 q=verify(d/'motion.glb',key,near,4);qp=d/('interpolation-'+key+'.json');save(qp,q);row=next(row for row in pose['rows'] if row['sourceKey']==key);row.clear();row.update(sourceKey=key,sourceFrameComparison='authored_passive_source_surface',passed=q['passed'],requiresGeometryQc=True,geometryQcPath=str(qp.relative_to(R)),geometryQcSha256=sha(qp.read_bytes()));failures=list(q['contact']['failures']);reuse=[]
 for oldentry in inp['surfaceFields']:
  k=oldentry['sourceKey']
  if k==key:continue
  oldpos=[node_positions(doc,binary,tr,nd[k],t) for t in np.linspace(0,2.5,65)];_,newdoc,newbin=read_glb(d/'motion.glb');newtr=channel_data(newdoc,newbin);err=max(float(np.linalg.norm(node_positions(newdoc,newbin,newtr,nd[k],t)-w,axis=1).max()) for t,w in zip(np.linspace(0,2.5,65),oldpos));assert err==0;reuse.append({'sourceKey':k,'actualReplaySamples':65,'maximumDifferenceMetres':err});p=d/('interpolation-'+k+'.json');j=json.loads(p.read_text());j['motionGlbSha256']=sha(raw);save(p,j);oldrow=next(r for r in pose['rows'] if r['sourceKey']==k);oldrow['geometryQcSha256']=sha(p.read_bytes());failures+=j['contact']['failures']
 pose.update(motionSha256=sha(raw),passed=all(r['passed'] for r in pose['rows']));geo['motionSha256']=sha(raw);save(d/'glb-pose-qc.json',pose);save(d/'geometry-record.json',geo);save(d/'contact-qc.json',{'passed':not failures,'failures':failures,'newContainmentMaximum':max((r['newContainedVertexCount'] for r in failures),default=0),'baselineOverlapPreserved':True,'continuousCollisionFreedomClaimed':False});save(d/'diaphragm-context-receipt.json',{'oldMotionSha256':sha(oldraw),'newMotionSha256':sha(raw),'sourceKey':key,'passiveContextNotBreathingAction':True,'unchangedDeformerReplay':reuse,'geometryQcPassed':q['passed']});print(kind,'diaphragm',q['passed'],q['contact']['newContainmentMaximum'],flush=True)
 if pose['passed']:save(d/'complete.json',{'kind':kind,'clipId':doc['animations'][0]['name'],'family':geo['family'],'members':geo['members'],'motionSha256':sha(raw),'restSha256':geo['restSha256'],'glbInterpolationQcPaths':{e['sourceKey']:str((d/('interpolation-'+e['sourceKey']+'.json')).relative_to(R)) for e in inp['surfaceFields']},'contextSurfaces':len(geo['members']),'deformingSurfaces':len(inp['surfaceFields'])})
