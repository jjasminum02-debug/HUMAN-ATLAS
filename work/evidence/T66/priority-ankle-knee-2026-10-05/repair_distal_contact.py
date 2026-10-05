"""Bounded passive contact correctives for newly appended distal context only.

Keep all predecessor nodes/tracks unchanged. No attachment/axis/force claim.
"""
import pathlib,sys,json,numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[4];OUT=pathlib.Path(__file__).parent
sys.path[:0]=[str(ROOT/'work/tools'),str(ROOT/'work/evidence/T66/serial-completion-2026-10-02/unit-01')]
from verify_glb_interpolation import read_glb,channel_data,node_positions,bounded_inside,sample,qmatrix,verify
from author_source_surface_motion import array,container,normals
from derive_source_surface_motion import append_bytes,sha
from t66_contact_correctives import source_bone_projection_corrective
load=lambda p:json.loads((ROOT/p).read_text())
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
b=load('atlas-data/motion/motion-learning.json');reg=load('atlas-data/motion/authoring/registry.json');accept=load('atlas-data/motion/t66-priority-action-acceptance.json');outcomes=load(str((OUT/'hip-context-outcome.json').relative_to(ROOT)))
for side in ['left','right']:
 asset=next(a for a in b['motionAssets'] if a['id']=='T66-PRIORITY-'+side[0].upper()+'-RECTUS-ASSET');dest=OUT/('hip-complete-'+side);raw,doc,binary=read_glb(ROOT/asset['uri']);tracks=channel_data(doc,binary);nodes={n['extras']['sourceKey']:i for i,n in enumerate(doc['nodes'])};receipt=json.loads((dest/'context-reuse-receipt.json').read_text());buf=bytearray(binary)
 def put(raw,typ,count):
  off,length=append_bytes(buf,raw);vi=len(doc['bufferViews']);doc['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':length});ai=len(doc['accessors']);doc['accessors'].append({'bufferView':vi,'componentType':5126,'count':int(count),'type':typ});return ai
 bones=[m['sourceKey'] for m in asset['sourceBinding']['members'] if m['role'] in ['fixed_structure','moving_structure']];times=np.linspace(0,asset['clip']['durationSeconds'],65);correctives=[];changed=[]
 for key in receipt['appendedNativeCoMovingSurfaces']:
  ni=nodes[key];prim=doc['meshes'][doc['nodes'][ni]['mesh']]['primitives'][0];pos=array(doc,binary,prim['attributes']['POSITION']);tri=array(doc,binary,prim['indices']).reshape(-1,3);rest=node_positions(doc,binary,tracks,ni,0);contacts=[]
  for bone in bones:
   bi=nodes[bone];bw=node_positions(doc,binary,tracks,bi,0)
   if any(rest.max(0)[j]<bw.min(0)[j]-.025 or rest.min(0)[j]>bw.max(0)[j]+.025 for j in range(3)):continue
   bp=doc['meshes'][doc['nodes'][bi]['mesh']]['primitives'][0];bt=array(doc,binary,bp['indices']).reshape(-1,3);contacts.append((bone,bt,bounded_inside(rest,bw,bt)))
  deltas=[];records=[]
  for t in times[1:]:
   frame=node_positions(doc,binary,tracks,ni,float(t));pc=[(bone,node_positions(doc,binary,tracks,nodes[bone],float(t)),bt,base) for bone,bt,base in contacts]
   try:corrected,detail=source_bone_projection_corrective(frame,rest,tri,pc,set(),margin_metres=.000005)
   except ValueError:
    print('failed corrective',side,key,float(t),flush=True);raise
   R=qmatrix(sample(tracks[(ni,'rotation')],float(t),'rotation'))@np.diag(doc['nodes'][ni]['scale']);delta=(corrected-frame)@np.linalg.inv(R).T;deltas.append(delta);records.append(detail)
  maximum=max(float(np.linalg.norm(d,axis=1).max()) for d in deltas)
  if maximum<1e-10:continue
  assert maximum<.001,'distal correction exceeds bounded one-millimetre engineering limit'
  prim['targets']=[];baseN=normals(pos,tri)
  for delta in deltas:prim['targets'].append({'POSITION':put(np.asarray(delta,dtype='<f4').tobytes(),'VEC3',len(pos)),'NORMAL':put((normals(pos+delta,tri)-baseN).astype('<f4').tobytes(),'VEC3',len(pos))})
  doc['meshes'][doc['nodes'][ni]['mesh']]['weights']=[0]*len(deltas);weights=np.zeros((len(times),len(deltas)),dtype='<f4');weights[1:]=np.eye(len(deltas),dtype='<f4');ta=put(times.astype('<f4').tobytes(),'SCALAR',len(times));out=put(weights.tobytes(),'SCALAR',weights.size);animation=doc['animations'][0];si=len(animation['samplers']);animation['samplers'].append({'input':ta,'output':out,'interpolation':'LINEAR'});animation['channels'].append({'sampler':si,'target':{'node':ni,'path':'weights'}});changed.append(key);correctives.append({'sourceKey':key,'maximumLocalCorrectiveMetres':maximum,'records':records})
 motion=container(doc,buf);(ROOT/asset['uri']).write_bytes(motion);(dest/'motion.glb').write_bytes(motion);save(dest/'distal-contact-correctives.json',correctives)
 print(side,'corrected',len(changed),'max',max([r['maximumLocalCorrectiveMetres'] for r in correctives],default=0),flush=True)
 # Mandatory emitted interpolation QC, including all key/midpoints and nearby actual bones.
 qp={}
 for key in changed:
  rest=node_positions(doc,bytes(buf),channel_data(doc,bytes(buf)),nodes[key],0);near=[]
  for bone in bones:
   bw=node_positions(doc,bytes(buf),channel_data(doc,bytes(buf)),nodes[bone],0)
   if not any(rest.max(0)[j]<bw.min(0)[j]-.025 or rest.min(0)[j]>bw.max(0)[j]+.025 for j in range(3)):near.append(bone)
  qc=verify(ROOT/asset['uri'],key,near,2);qpath=dest/('interpolation-'+key+'.json');save(qpath,qc);print(side,key,qc['passed'],qc['contact']['newContainmentMaximum'],flush=True);assert qc['passed'];qp[key]=str(qpath.relative_to(ROOT))
 asset['sha256']=sha(motion);outcome=next(o for o in outcomes if o['assetId']==asset['id']);outcome.update(motionSha256=sha(motion),boundedPassiveCorrectiveCount=len(changed));authorpath=next(r['path'] for r in reg['records'] if r['id']=='T66-PRIORITY-'+side[0].upper()+'-RECTUS-AUTHORING');author=load(authorpath);author['motionSha256']=sha(motion);author['glbInterpolationQcPaths']=qp
 geometry=load(author['geometryRecordPath']);geometry['motionSha256']=sha(motion)
 for m in geometry['surfaceMetrics']:
  if m['sourceKey'] in qp:
   qc=load(qp[m['sourceKey']]);m.update(minimumAreaRatio=qc['geometry']['minimumAreaRatio'],flips=qc['geometry']['flippedFaceSamples'])
 save(ROOT/author['geometryRecordPath'],geometry);pose=load(author['glbPoseQcPath']);pose['motionSha256']=sha(motion)
 for row in pose['rows']:
  if row['sourceKey'] in qp:row.update(sourceFrameComparison='authored_surface_deformation',requiresGeometryQc=True,geometryQcPath=qp[row['sourceKey']],geometryQcSha256=sha((ROOT/qp[row['sourceKey']]).read_bytes()));row.pop('maximumWorldErrorMetres',None)
 save(ROOT/author['glbPoseQcPath'],pose);save(ROOT/authorpath,author)
 deps={d['path']:d for d in author['verificationDependencies']}
 for path in [asset['uri'],author['geometryRecordPath'],author['glbPoseQcPath'],*qp.values(),str((dest/'distal-contact-correctives.json').relative_to(ROOT))]:deps[path]={'path':path,'sha256':sha((ROOT/path).read_bytes())}
 author['verificationDependencies']=list(deps.values());save(ROOT/authorpath,author)
save(OUT/'hip-context-outcome.json',outcomes)
for side in ['left','right']:
 ar=next(r['path'] for r in reg['records'] if r['id']=='T66-PRIORITY-'+side[0].upper()+'-RECTUS-AUTHORING');a=load(ar)
 for d in a['verificationDependencies']:
  if d['path']==a['actionOutcomePath']:d['sha256']=sha((ROOT/d['path']).read_bytes())
 save(ROOT/ar,a);next(r for r in reg['records'] if r['path']==ar)['sha256']=sha((ROOT/ar).read_bytes());next(r for r in accept['rows'] if r['authoringPath']==ar).update(motionSha256=a['motionSha256'],authoringSha256=sha((ROOT/ar).read_bytes()),outcomeSha256=sha((ROOT/a['actionOutcomePath']).read_bytes()))
for p,v in [('atlas-data/motion/motion-learning.json',b),('atlas-data/motion/authoring/registry.json',reg),('atlas-data/motion/t66-priority-action-acceptance.json',accept)]:save(ROOT/p,v)
