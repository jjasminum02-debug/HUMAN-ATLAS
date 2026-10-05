"""Add only failed interpolation instants as source-specific corrective keys.

The bone trajectory and every already accepted surface remain unchanged.
New key geometry is solved against the actual emitted bone pose, avoiding a
large coarse-key margin as a substitute for the observed intermediate pose.
"""
import pathlib,sys,json,copy,numpy as np
R=pathlib.Path(__file__).resolve().parents[4];O=pathlib.Path(__file__).parent
sys.path[:0]=[str(R/'work/tools'),str(R/'work/evidence/T66/serial-completion-2026-10-02/unit-01')]
from verify_glb_interpolation import read_glb,channel_data,node_positions,verify,bounded_inside
from author_source_surface_motion import array,normals,container
from derive_source_surface_motion import append_bytes,sha
from trunk_contact_patch import source_topology_contact_patch_corrective
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
src={r['sourceKey']:r for r in json.loads((R/'atlas-data/source-cache/datasets/za/compiled/manifest.json').read_text())['instances']}
for kind in sys.argv[1:] or ['flex']:
 d=O/kind;oldraw,old,oldbuf=read_glb(d/'motion.glb');tr=channel_data(old,oldbuf);nodes={n['extras']['sourceKey']:i for i,n in enumerate(old['nodes'])};doc=copy.deepcopy(old);buf=bytearray(oldbuf);geo=json.loads((d/'geometry-record.json').read_text());pose=json.loads((d/'glb-pose-qc.json').read_text());inp=json.loads((d/'authored-input.json').read_text());entries={e['sourceKey']:e for e in inp['surfaceFields']};oldq={k:json.loads((d/('interpolation-'+k+'.json')).read_text()) for k in entries};changed=[k for k,q in oldq.items() if not q['passed']];assert changed
 print(kind,'targeted failures',[src[k]['name'] for k in changed],flush=True);repairs=[]
 def put(raw,typ,count):
  off,ln=append_bytes(buf,raw);doc['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':ln});ai=len(doc['accessors']);doc['accessors'].append({'bufferView':len(doc['bufferViews'])-1,'componentType':5126,'count':int(count),'type':typ});return ai
 for k in changed:
  ni=nodes[k];node=doc['nodes'][ni];primitive=doc['meshes'][node['mesh']]['primitives'][0];pos=array(old,oldbuf,primitive['attributes']['POSITION']);tri=array(old,oldbuf,primitive['indices']).reshape(-1,3);normal=array(old,oldbuf,primitive['attributes']['NORMAL']);M=np.array(node['matrix']).reshape(4,4).T;rest=node_positions(old,oldbuf,tr,ni,0);e=entries[k];locked=set(e['fixedVertexIndices']);contacts=[];groups=[g for g in e['sourceTopologyCoupledVertexGroups'] if not set(g)&locked]
  for bk in e['contactBoneKeys']:
   bn=nodes[bk];bt=array(old,oldbuf,old['meshes'][old['nodes'][bn]['mesh']]['primitives'][0]['indices']).reshape(-1,3);bw=node_positions(old,oldbuf,tr,bn,0);contacts.append((bk,bn,bt,bounded_inside(rest,bw,bt)))
  times=set(float(t) for t in tr[(ni,'weights')][0])
  for row in oldq[k]['contact']['failures']:times.add(float(row['seconds']))
  for row in oldq[k]['perSampleGeometry']:
   if row['flippedFaces'] or (row['minimumAreaRatio'] is not None and row['minimumAreaRatio']<.2):times.add(float(row['seconds']))
  times=sorted(times);failed_times=set(float(row['seconds']) for row in oldq[k]['contact']['failures'])
  primitive['targets']=[];records=[]
  for step,t in enumerate(times[1:],start=1):
   frame=node_positions(old,oldbuf,tr,ni,t);active=[(bk,node_positions(old,oldbuf,tr,bn,t),bt,baseline) for bk,bn,bt,baseline in contacts]
   if True:
    # Guard vertices near the failed source bone at the real adjacent key, then
    # solve only a small source-topology patch. The guard is numerical clearance,
    # not a new attachment or normal anatomy spacing assertion.
    from t66_contact_correctives import nearest_surface
    failedbones={r['boneSourceKey'] for r in oldq[k]['contact']['failures']};seeds=set()
    for bk,bw,bt,baseline in active:
     if bk not in failedbones:continue
     eligible=np.flatnonzero(~baseline & ((frame>=bw.min(0)-.003)&(frame<=bw.max(0)+.003)).all(1))
     if not len(eligible):continue
     q=nearest_surface(frame[eligible],bw,bt);dist=np.linalg.norm(q-frame[eligible],axis=1);near=eligible[dist<.003];seeds.update(int(v) for v in near if int(v) not in locked)
    rt=rest[tri];rn=np.cross(rt[:,1]-rt[:,0],rt[:,2]-rt[:,0]);ra=np.linalg.norm(rn,axis=1);ft=frame[tri];fn=np.cross(ft[:,1]-ft[:,0],ft[:,2]-ft[:,0]);bad=np.flatnonzero((ra>=1e-12)&(((rn*fn).sum(1)<0)|(np.linalg.norm(fn,axis=1)<ra*.3)));seeds.update(int(v) for v in tri[bad].ravel() if int(v) not in locked)
    for group in groups:
     if set(group)&seeds:frame[group]=rest[group]+(frame[group]-rest[group]).mean(0)
    frame,c=source_topology_contact_patch_corrective(frame,rest,tri,active,locked,[],margin_metres=.0004,contact_guard_metres=.0012,shape_floor=.3,patch_rings=3,shape_seed_vertices=sorted(seeds),topology_groups=groups,force_contact_guard=bool(seeds));records.append({'step':step,'seconds':t,'sourceVertexSeeds':sorted(seeds),'corrective':c})
   local=(frame-M[:3,3])@np.linalg.inv(M[:3,:3]).T;local[list(locked)]=pos[list(locked)];delta=(local-pos).astype('<f4');pa=put(delta.tobytes(),'VEC3',len(pos));doc['accessors'][pa].update(min=delta.min(0).tolist(),max=delta.max(0).tolist());primitive['targets'].append({'POSITION':pa,'NORMAL':put((normals(local,tri)-normal).astype('<f4').tobytes(),'VEC3',len(pos))})
  n=len(times)-1;node['weights']=[0]*n;doc['meshes'][node['mesh']]['weights']=[0]*n
  values=np.zeros((n+1,n),dtype='<f4');values[1:]=np.eye(n)
  channel=next(ch for ch in doc['animations'][0]['channels'] if ch['target']=={'node':ni,'path':'weights'})
  sampler=doc['animations'][0]['samplers'][channel['sampler']]
  ta=put(np.array(times,dtype='<f4').tobytes(),'SCALAR',len(times));doc['accessors'][ta].update(min=[0],max=[2.5]);sampler['input']=ta;sampler['output']=put(values.ravel().tobytes(),'SCALAR',values.size)
  repairs.append({'sourceKey':k,'failedQcBefore':oldq[k],'oldKeyTimes':tr[(ni,'weights')][0].tolist(),'adaptiveKeyTimes':times,'repairs':records})
 motion=container(doc,buf);(d/'motion.glb').write_bytes(motion);_,nd,nb=read_glb(d/'motion.glb');nt=channel_data(nd,nb);failures=[];qcpaths={};reuse=[]
 for k in entries:
  qp=d/('interpolation-'+k+'.json')
  if k in changed:q=verify(d/'motion.glb',k,entries[k]['contactBoneKeys'],4)
  else:
   err=max(float(np.linalg.norm(node_positions(old,oldbuf,tr,nodes[k],t)-node_positions(nd,nb,nt,nodes[k],t),axis=1).max()) for t in np.linspace(0,2.5,65));assert err==0;reuse.append({'sourceKey':k,'emittedVertexReplaySamples':65,'maximumDifferenceMetres':err});q=oldq[k];assert q['passed'];q['motionGlbSha256']=sha(motion);q['unchangedEmittedInputReuseReceipt']='refinement-receipt.json'
  q['motionGlbSha256']=sha(motion);save(qp,q);qcpaths[k]=str(qp.relative_to(R));row=next(r for r in pose['rows'] if r['sourceKey']==k);row.update(passed=q['passed'],geometryQcPath=qcpaths[k],geometryQcSha256=sha(qp.read_bytes()));metric=next(r for r in geo['surfaceMetrics'] if r['sourceKey']==k);metric.update(flips=q['geometry']['flippedFaceSamples'],minimumAreaRatio=q['geometry']['minimumAreaRatio']);failures.extend(q['contact']['failures']);print(kind,src[k]['name'],q['passed'],q['contact']['newContainmentMaximum'],flush=True)
 pose.update(passed=all(r['passed'] for r in pose['rows']),motionSha256=sha(motion));geo['motionSha256']=sha(motion);save(d/'geometry-record.json',geo);save(d/'glb-pose-qc.json',pose);save(d/'contact-qc.json',{'failures':failures,'newContainmentMaximum':max((r['newContainedVertexCount'] for r in failures),default=0),'passed':not failures,'baselineOverlapPreserved':True,'continuousCollisionFreedomClaimed':False});save(d/'refinement-receipt.json',{'oldMotionSha256':sha(oldraw),'newMotionSha256':sha(motion),'changedSourceKeys':changed,'unchangedDeformerReplay':reuse,'targetedRepairs':repairs,'measuredAnatomyOrNormalSpacingClaimed':False})
 assert pose['passed'],'targeted emitted repair remains incomplete'
 save(d/'complete.json',{'kind':kind,'clipId':doc['animations'][0]['name'],'family':geo['family'],'members':geo['members'],'motionSha256':sha(motion),'restSha256':geo['restSha256'],'glbInterpolationQcPaths':qcpaths,'contextSurfaces':len(geo['members']),'deformingSurfaces':len(entries)})
