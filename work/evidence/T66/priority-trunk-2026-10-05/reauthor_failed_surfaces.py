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
  times=set(float(t) for t in np.linspace(0,2.5,17))
  # Rebuild only the failing native surface field, not unrelated families.
  times=sorted(times);centers=np.array(inp['segmentCentroids']);tsframes=np.array(inp['segmentTransformsAtKeys']);y=rest[:,1];a=np.clip(np.searchsorted(centers[:,1],y)-1,0,len(centers)-2);v=np.clip((y-centers[a,1])/(centers[a+1,1]-centers[a,1]),0,1);v=v*v*(3-2*v);frames=[]
  for ts in tsframes:
   frame=np.zeros_like(rest)
   for i,T in enumerate(ts):
    weight=np.where(a==i,1-v,0)+np.where(a+1==i,v,0);weight[y<=centers[0,1]]=1 if i==0 else 0;weight[y>=centers[-1,1]]=1 if i==len(centers)-1 else 0;frame+=weight[:,None]*(rest@T[:3,:3].T+T[:3,3])
   frames.append(frame)
  # Native near-bone geometry receives the actual observed bone motion.
  # This authors a smooth contact transport field, not measured attachments.
  from t66_contact_correctives import nearest_surface_details
  distances=np.full(len(rest),np.inf);owners=np.full(len(rest),-1,dtype=int);units=np.zeros_like(rest)
  for ci,(bk,bn,bt,baseline) in enumerate(contacts):
   bw=node_positions(old,oldbuf,tr,bn,0);ix=np.flatnonzero(((rest>=bw.min(0)-.012)&(rest<=bw.max(0)+.012)).all(1))
   if not len(ix):continue
   points,_=nearest_surface_details(rest[ix],bw,bt);delta=rest[ix]-points;ds=np.linalg.norm(delta,axis=1);take=ds<distances[ix];ids=ix[take];distances[ids]=ds[take];owners[ids]=ci;units[ids]=delta[take]/np.maximum(ds[take,None],1e-30)
  f=np.clip((distances-.003)/.009,0,1);weights=1-f*f*(3-2*f);weights[list(locked)]=0
  for step,t in enumerate(times):
   for ci,(bk,bn,bt,baseline) in enumerate(contacts):
    ix=np.flatnonzero((owners==ci)&(weights>0))
    if not len(ix):continue
    bw=node_positions(old,oldbuf,tr,bn,0);posed=node_positions(old,oldbuf,tr,bn,t);A=np.linalg.lstsq(np.c_[bw,np.ones(len(bw))],posed,rcond=None)[0];anchored=rest[ix]@A[:3]+A[3]
    # Micrometre derived numerical clearance only, retaining source overlaps.
    guard=(~baseline[ix])[:,None]*units[ix]@A[:3]*(.00003*min(1,(t/2.5)**.25))
    anchored+=guard;frames[step][ix]=frames[step][ix]*(1-weights[ix,None])+anchored*weights[ix,None]
  e['nativeGeometricContactTransport']={'innerDistanceMetres':.003,'outerDistanceMetres':.012,'sourceVertexIndices':np.flatnonzero(weights>0).tolist(),'weightValues':weights[weights>0].tolist(),'contactBoneSourceKeys':[c[0] for c in contacts],'measuredAnatomicalAttachments':False,'maximumNumericalClearanceMetres':.00003}
  groups=[];rt=rest[tri];rn=np.cross(rt[:,1]-rt[:,0],rt[:,2]-rt[:,0]);ra=np.linalg.norm(rn,axis=1)
  for iteration in range(64):
   bad=set()
   for frame in frames[1:]:
    ft=frame[tri];fn=np.cross(ft[:,1]-ft[:,0],ft[:,2]-ft[:,0]);bad.update(np.flatnonzero((ra>=1e-12)&(((rn*fn).sum(1)<0)|(np.linalg.norm(fn,axis=1)<ra*.15))).tolist())
   if not bad:break
   # Connected components only. Separate failing faces never become one slab.
   components=[set(map(int,tri[j])) for j in sorted(bad)]+[set(g) for g in groups]
   merged=[]
   for component in components:
    while any(component&g for g in merged):
     hit=next(g for g in merged if component&g);component|=hit;merged.remove(hit)
    merged.append(component)
   groups=[sorted(g) for g in merged]
   for step,frame in enumerate(frames[1:],start=1):
    for group in groups:
     if set(group)&locked:frame[group]=rest[group];continue
     level=int(np.argmin(abs(centers[:,1]-rest[group,1].mean())));rotation=tsframes[step,level,:3,:3];center=frame[group].mean(0);frame[group]=(rest[group]-rest[group].mean(0))@rotation.T+center
  assert not bad,('native field topology not converged',k)
  e['sourceTopologyCoupledVertexGroups']=groups;e['topologyGroupingRevision']='connected_bad_face_components_with_native_patch_rotation_v3';e['contactCorrectiveEqualTranslationGroupConstraint']=False;groups=[g for g in groups if not set(g)&locked]
  contactrest={bk:node_positions(old,oldbuf,tr,bn,0) for bk,bn,bt,baseline in contacts}
  primitive['targets']=[];records=[]
  for step,t in enumerate(times[1:],start=1):
   frame=frames[step].copy();active=[(bk,node_positions(old,oldbuf,tr,bn,t),bt,baseline) for bk,bn,bt,baseline in contacts]
   if True:
    # Guard vertices near the failed source bone at the real adjacent key, then
    # solve only a small source-topology patch. The guard is numerical clearance,
    # not a new attachment or normal anatomy spacing assertion.
    from t66_contact_correctives import nearest_surface
    failedbones={bk for bk,bn,bt,baseline in contacts};seeds=set()
    for bk,bw,bt,baseline in active:
     if bk not in failedbones:continue
     eligible=np.flatnonzero(~baseline & ((frame>=bw.min(0)-.003)&(frame<=bw.max(0)+.003)).all(1))
     if not len(eligible):continue
     q=nearest_surface(frame[eligible],bw,bt);dist=np.linalg.norm(q-frame[eligible],axis=1);near=eligible[dist<.003];seeds.update(int(v) for v in near if int(v) not in locked)
    rt=rest[tri];rn=np.cross(rt[:,1]-rt[:,0],rt[:,2]-rt[:,0]);ra=np.linalg.norm(rn,axis=1);ft=frame[tri];fn=np.cross(ft[:,1]-ft[:,0],ft[:,2]-ft[:,0]);bad=np.flatnonzero((ra>=1e-12)&(((rn*fn).sum(1)<0)|(np.linalg.norm(fn,axis=1)<ra*.3)));seeds.update(int(v) for v in tri[bad].ravel() if int(v) not in locked)

    frame,c=source_topology_contact_patch_corrective(frame,rest,tri,active,locked,[],margin_metres=.00003,contact_guard_metres=.0012,shape_floor=.3,patch_rings=5,max_outer_iterations=16,shape_seed_vertices=sorted(seeds),topology_groups=[],force_contact_guard=False,contact_rest_bones=contactrest,preserve_group_pose_vectors=True);records.append({'step':step,'seconds':t,'sourceVertexSeeds':sorted(seeds),'corrective':c})
   local=(frame-M[:3,3])@np.linalg.inv(M[:3,:3]).T;local[list(locked)]=pos[list(locked)];delta=(local-pos).astype('<f4');pa=put(delta.tobytes(),'VEC3',len(pos));doc['accessors'][pa].update(min=delta.min(0).tolist(),max=delta.max(0).tolist());primitive['targets'].append({'POSITION':pa,'NORMAL':put((normals(local,tri)-normal).astype('<f4').tobytes(),'VEC3',len(pos))})
  n=len(times)-1;node['weights']=[0]*n;doc['meshes'][node['mesh']]['weights']=[0]*n
  values=np.zeros((n+1,n),dtype='<f4');values[1:]=np.eye(n)
  channel=next(ch for ch in doc['animations'][0]['channels'] if ch['target']=={'node':ni,'path':'weights'})
  sampler=doc['animations'][0]['samplers'][channel['sampler']]
  ta=put(np.array(times,dtype='<f4').tobytes(),'SCALAR',len(times));doc['accessors'][ta].update(min=[0],max=[2.5]);sampler['input']=ta;sampler['output']=put(values.ravel().tobytes(),'SCALAR',values.size)
  repairs.append({'sourceKey':k,'failedQcBefore':oldq[k],'oldKeyTimes':tr[(ni,'weights')][0].tolist(),'adaptiveKeyTimes':times,'repairs':records})
 save(d/'authored-input.json',inp)
 motion=container(doc,buf);(d/'motion.glb').write_bytes(motion);_,nd,nb=read_glb(d/'motion.glb');nt=channel_data(nd,nb);failures=[];qcpaths={};reuse=[]
 for k in entries:
  qp=d/('interpolation-'+k+'.json')
  if k in changed:q=verify(d/'motion.glb',k,entries[k]['contactBoneKeys'],4)
  else:
   err=max(float(np.linalg.norm(node_positions(old,oldbuf,tr,nodes[k],t)-node_positions(nd,nb,nt,nodes[k],t),axis=1).max()) for t in np.linspace(0,2.5,65));assert err==0;reuse.append({'sourceKey':k,'emittedVertexReplaySamples':65,'maximumDifferenceMetres':err});q=oldq[k];assert q['passed'];q['motionGlbSha256']=sha(motion);q['unchangedEmittedInputReuseReceipt']='native-field-repair-receipt.json'
  q['motionGlbSha256']=sha(motion);save(qp,q);qcpaths[k]=str(qp.relative_to(R));row=next(r for r in pose['rows'] if r['sourceKey']==k);row.update(passed=q['passed'],geometryQcPath=qcpaths[k],geometryQcSha256=sha(qp.read_bytes()));metric=next(r for r in geo['surfaceMetrics'] if r['sourceKey']==k);metric.update(flips=q['geometry']['flippedFaceSamples'],minimumAreaRatio=q['geometry']['minimumAreaRatio']);failures.extend(q['contact']['failures']);print(kind,src[k]['name'],q['passed'],q['contact']['newContainmentMaximum'],flush=True)
 pose.update(passed=all(r['passed'] for r in pose['rows']),motionSha256=sha(motion));geo['motionSha256']=sha(motion);save(d/'geometry-record.json',geo);save(d/'glb-pose-qc.json',pose);save(d/'contact-qc.json',{'failures':failures,'newContainmentMaximum':max((r['newContainedVertexCount'] for r in failures),default=0),'passed':not failures,'baselineOverlapPreserved':True,'continuousCollisionFreedomClaimed':False});save(d/'native-field-repair-receipt.json',{'oldMotionSha256':sha(oldraw),'newMotionSha256':sha(motion),'changedSourceKeys':changed,'unchangedDeformerReplay':reuse,'targetedRepairs':repairs,'measuredAnatomyOrNormalSpacingClaimed':False})
 assert pose['passed'],'targeted emitted repair remains incomplete'
 save(d/'complete.json',{'kind':kind,'clipId':doc['animations'][0]['name'],'family':geo['family'],'members':geo['members'],'motionSha256':sha(motion),'restSha256':geo['restSha256'],'glbInterpolationQcPaths':qcpaths,'contextSurfaces':len(geo['members']),'deformingSurfaces':len(entries)})
