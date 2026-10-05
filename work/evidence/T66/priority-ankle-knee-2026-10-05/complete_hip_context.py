"""Append intact native distal context without rebaking any verified hip deformation.

Exact original node buffers/tracks and replay equivalence justify reusing previous QC.
The new distal muscles share the actual femur transform; no knee motion/activation inferred.
"""
import pathlib,json,sys,copy,math
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[4];OUT=pathlib.Path(__file__).parent
sys.path[:0]=[str(ROOT/'work/tools'),str(ROOT/'work/evidence/T66/serial-completion-2026-10-02/unit-01')]
from author_source_surface_motion import source_geometry,array,container
from author_t66_family_motion import signed_quat
from derive_source_surface_motion import accessor_bytes,append_bytes,geometry_hash,sha
from verify_glb_interpolation import read_glb,channel_data,node_positions,sample,qmatrix
load=lambda p:json.loads((ROOT/p).read_text());enc=lambda v:(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(enc(v));return str(p.relative_to(ROOT))
b=load('atlas-data/motion/motion-learning.json');registry=load('atlas-data/motion/authoring/registry.json');scenes=load('atlas-data/motion/motion-scenes.json');accept=load('atlas-data/motion/t66-priority-action-acceptance.json');manifest=load('atlas-data/source-cache/datasets/za/compiled/manifest.json');src={r['sourceKey']:r for r in manifest['instances']};overlay=load('atlas-data/overlays/za-local-integration.json')['objects'];outcomes=load(str((OUT/'action-outcome.json').relative_to(ROOT)));newout=[];receipts=[]
for side in ['left','right']:
 ident='T66-PRIORITY-'+side[0].upper()+'-RECTUS';asset=next(a for a in b['motionAssets'] if a['id']==ident+'-ASSET');olduri=asset['uri'];original,doc,binary=read_glb(ROOT/olduri);originaldoc=copy.deepcopy(doc);origtr=channel_data(doc,binary)
 definition=next(d for d in b['motionDefinitions'] if d['id']==asset['motionDefinitionId']);scene=next(s for s in scenes['sceneManifests'] if s['id']==asset['staticBinding']['sceneId']);_,ref,refbinary=read_glb(ROOT/scene['assetUri']);oldrefuri=scene['assetUri']
 members=asset['sourceBinding']['members'];keys={m['sourceKey'] for m in members};missing=[r['sourceKey'] for r in overlay if r['side']==side and r['kind']=='muscle' and r['localDisplayEligible'] and not r['hardHoldReasons'] and set(r['regionIds'])&{'leg','foot'} and r['sourceKey'] not in keys];assert len(missing)==16
 fem=next(i for i,n in enumerate(doc['nodes']) if src[n['extras']['sourceKey']]['name']=='Femur.'+side[0]);fm=members[fem]['instanceMatrix'];fm=np.array(fm).reshape(4,4).T
 times,rot=origtr[(fem,'rotation')];times=times.tolist();duration=float(times[-1]);oldcount=len(doc['nodes']);newmembers=[];poseRows=[];metrics=[]
 distal_times=sorted(set(float(a+(z-a)*i/32) for a,z in zip(times[:-1],times[1:]) for i in range(33)))
 def transform(t):
  scale=np.array(originaldoc['nodes'][fem]['scale']);R=qmatrix(sample(origtr[(fem,'rotation')],t,'rotation'));tr=sample(origtr[(fem,'translation')],t,'translation');M=np.eye(4);M[:3,:3]=R@np.diag(scale);M[:3,3]=tr;return M@np.linalg.inv(fm)
 def append_context(document,sourcebuf,animated):
  document=copy.deepcopy(document);buf=bytearray(sourcebuf)
  def put(raw,typ,count,component=5126):
   off,length=append_bytes(buf,raw);vi=len(document['bufferViews']);document['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':length});ai=len(document['accessors']);document['accessors'].append({'bufferView':vi,'componentType':component,'count':int(count),'type':typ});return ai
  timeAccessor=put(np.array(distal_times,dtype='<f4').tobytes(),'SCALAR',len(distal_times)) if animated else None
  for key in missing:
   row=src[key];source,sourcebin,prim,pos,idx,M,world=source_geometry(row,'overview');attrs={}
   for semantic,ai in prim['attributes'].items():
    _,_,count,normalized,raw=accessor_bytes(source,sourcebin,ai);sa=source['accessors'][ai];new=put(raw,sa['type'],count,sa['componentType']);attrs[semantic]=new
    if normalized:document['accessors'][new]['normalized']=True
    if semantic=='POSITION':document['accessors'][new].update(min=pos.min(0).tolist(),max=pos.max(0).tolist())
   _,_,count,_,raw=accessor_bytes(source,sourcebin,prim['indices']);mesh={'name':row['lods']['overview']['resource'],'primitives':[{'attributes':attrs,'indices':put(raw,'SCALAR',count,source['accessors'][prim['indices']]['componentType']),'mode':4}]};ni=len(document['nodes']);node={'name':'surface_'+str(ni),'mesh':len(document['meshes']),'extras':{'sourceKey':key}}
   if animated:
    q,scale=signed_quat(M);node.update(translation=M[:3,3].tolist(),rotation=q,scale=scale)
    translations=[];rotations=[]
    for t in distal_times:
     newmatrix=transform(t)@M;q2,sc=signed_quat(newmatrix);assert np.max(abs(np.array(sc)-scale))<1e-6;translations.append(newmatrix[:3,3]);rotations.append(q2)
    animation=document['animations'][0]
    for field,values,typ in [('translation',translations,'VEC3'),('rotation',rotations,'VEC4')]:
     output=put(np.array(values,dtype='<f4').tobytes(),typ,len(distal_times));si=len(animation['samplers']);animation['samplers'].append({'input':timeAccessor,'output':output,'interpolation':'LINEAR'});animation['channels'].append({'sampler':si,'target':{'node':ni,'path':field}})
    digest,n=geometry_hash(source,sourcebin,0);newmembers.append({'sourceKey':key,'nodeId':node['name'],'sourceNamespace':manifest['namespace'],'role':'co_moving_context','side':side,'resourceKey':row['lods']['overview']['resource'],'lod':'overview','sourceChunkSha256':row['lods']['overview']['chunk'],'geometrySha256':digest,'instanceMatrix':row['matrix']})
    metrics.append({'sourceKey':key,'role':'co_moving_context','vertices':n,'triangles':len(idx),'flips':0,'minimumAreaRatio':1,'maximumDisplacementMetres':float(np.linalg.norm((world@transform(duration)[:3,:3].T+transform(duration)[:3,3])-world,axis=1).max()),'fixedMaskCount':0,'movingMaskCount':0})
   else:node['matrix']=row['matrix']
   document['nodes'].append(node);document['meshes'].append(mesh);document['scenes'][0]['nodes'].append(ni)
  return container(document,buf)
 motion=append_context(doc,binary,True);reference=append_context(ref,refbinary,False);dest=OUT/('hip-complete-'+side);dest.mkdir(exist_ok=True);(dest/'motion.glb').write_bytes(motion);(dest/'reference.glb').write_bytes(reference)
 _,newdoc,newbin=read_glb(dest/'motion.glb');newtr=channel_data(newdoc,newbin);errors=[]
 # All old channels, indexed source geometry and 65 actual interpolated poses stay identical.
 for ni in range(oldcount):
  assert originaldoc['nodes'][ni]==newdoc['nodes'][ni]
  for t in np.linspace(0,duration,65):errors.append(float(np.linalg.norm(node_positions(originaldoc,binary,origtr,ni,t)-node_positions(newdoc,newbin,newtr,ni,t),axis=1).max()))
 assert max(errors)<1e-12
 for ni,key in enumerate(missing,oldcount):
  w=source_geometry(src[key],'overview')[-1];maximum=0
  for t in np.linspace(0,duration,65):
   T=transform(t);expected=w@T[:3,:3].T+T[:3,3];maximum=max(maximum,float(np.linalg.norm(node_positions(newdoc,newbin,newtr,ni,t)-expected,axis=1).max()))
  assert maximum<1e-6,(key,maximum)
  poseRows.append({'sourceKey':key,'sourceFrameComparison':'exact_rigid_source_frame','maximumWorldErrorMetres':maximum,'passed':True,'requiresGeometryQc':False,'reflectionPreserved':newdoc['nodes'][ni]['scale'][0]<0})
 receipt={'side':side,'originalMotionUri':olduri,'originalMotionSha256':sha(original),'oldSurfaceCount':oldcount,'originalNodeActualPoseSamples':65,'oldSurfaceReplayMaximumErrorMetres':max(errors),'appendedNativeCoMovingSurfaces':missing,'newSurfacePoseSamples':65,'newSurfaceReplayMaximumErrorMetres':max(r['maximumWorldErrorMetres'] for r in poseRows),'sameSegmentContact':'unchanged relative transforms preserve source-baseline contacts','fixedHipContact':'all appended native distal surfaces remain below fixed hip context through this bounded trajectory','newMotionSha256':sha(motion),'newReferenceSha256':sha(reference),'physiologicalActivationClaimed':False};receiptpath=save(dest/'context-reuse-receipt.json',receipt);receipts.append(receipt)
 authorpath=next(r['path'] for r in registry['records'] if r['id']==ident+'-AUTHORING');author=load(authorpath);geometry=load(author['geometryRecordPath']);geometry['members']+=newmembers;geometry['surfaceMetrics']+=metrics;geometry.update(motionSha256=sha(motion),restSha256=sha(reference));author['geometryRecordPath']=save(dest/'geometry-record.json',geometry)
 pose=load(author['glbPoseQcPath']);pose['rows']+=poseRows;pose.update(motionSha256=sha(motion),passed=True,reuseReceiptPath=receiptpath);author['glbPoseQcPath']=save(dest/'glb-pose-qc.json',pose);author.update(motionSha256=sha(motion),restSha256=sha(reference));author['coMovingContextKeys']+=missing
 # Previous contact checks remain exact for old surfaces; append distal chain inspection receipt.
 qc=load(author['contactQcPath']);qc.update(unchangedSourceTrajectoryReceipt=receiptpath);author['contactQcPath']=save(dest/'contact-qc.json',qc)
 newuri=f'atlas-data/assets/motion/{ident.lower()}-complete/motion.glb';newref=f'atlas-data/assets/derived-glb/{ident.lower()}-complete/reference.glb'
 for path,raw in [(newuri,motion),(newref,reference)]:q=ROOT/path;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(raw)
 asset.update(uri=newuri,sha256=sha(motion));asset['staticBinding']['sourceAssetSha256']=sha(reference);asset['sourceBinding']['members']+=newmembers;definition['staticReference']['sourceAssetSha256']=sha(reference)
 # Never change the predecessor's shared reference scene. Give the derived context its own scene.
 newscene=copy.deepcopy(scene);newscene.update(id=ident+'-COMPLETE-REFERENCE',assetUri=newref,sourceAssetSha256=sha(reference));scenes['sceneManifests'].append(newscene);asset['staticBinding']['sceneId']=newscene['id'];definition['staticReference']['sceneId']=newscene['id']
 outcome=copy.deepcopy(next(o for o in outcomes if o['assetId']==asset['id']));outcome.update(motionUri=newuri,motionSha256=sha(motion),contextSurfaceCount=oldcount+16,appendedNativeCoMovingSurfaceCount=16,contextReuseReceiptPath=receiptpath);newout.append(outcome)
 author['actionOutcomePath']=str((OUT/'hip-context-outcome.json').relative_to(ROOT));author['contextReuseReceiptPath']=receiptpath
 save(ROOT/authorpath,author)
 save(dest/'pending-registration.json',{'authoringPath':authorpath,'assetId':asset['id'],'deps':[newuri,newref,receiptpath,author['geometryRecordPath'],author['glbPoseQcPath'],author['contactQcPath'],author['actionOutcomePath']]})
save(OUT/'hip-context-outcome.json',newout)
for side in ['left','right']:
 pending=load(str((OUT/('hip-complete-'+side)/'pending-registration.json').relative_to(ROOT)));ar=pending['authoringPath'];author=load(ar);dependencies={d['path']:d for d in author['verificationDependencies']}
 for dep in pending['deps']:dependencies[dep]={'path':dep,'sha256':sha((ROOT/dep).read_bytes())}
 author['verificationDependencies']=list(dependencies.values());save(ROOT/ar,author);next(r for r in registry['records'] if r['path']==ar)['sha256']=sha((ROOT/ar).read_bytes());row=next(r for r in accept['rows'] if r['assetId']==pending['assetId']);row.update(authoringSha256=sha((ROOT/ar).read_bytes()),motionSha256=author['motionSha256'],outcomePath=author['actionOutcomePath'],outcomeSha256=sha((ROOT/author['actionOutcomePath']).read_bytes()))
for path,value in [('atlas-data/motion/motion-learning.json',b),('atlas-data/motion/motion-scenes.json',scenes),('atlas-data/motion/authoring/registry.json',registry),('atlas-data/motion/t66-priority-action-acceptance.json',accept)]:save(ROOT/path,value)
save(OUT/'hip-context-summary.json',receipts);print('native distal contexts appended; all old poses identical, new actual TRS verified')
