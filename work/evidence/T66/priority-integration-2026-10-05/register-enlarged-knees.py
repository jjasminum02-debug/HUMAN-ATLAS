"""Adopt independently verified bilateral 19.5-degree native knee teaching assets.

Keep prior source/authoring evidence immutable; version only the current binding.
"""
import pathlib,json,hashlib,copy,shutil
R=pathlib.Path(__file__).resolve().parents[4];O=pathlib.Path(__file__).parent
load=lambda p:json.loads((R/p).read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
vhash=lambda v:sha(json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode())
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');return str(p.relative_to(R))
b=load('atlas-data/motion/motion-learning.json');registry=load('atlas-data/motion/authoring/registry.json');scenes=load('atlas-data/motion/motion-scenes.json');accept=load('atlas-data/motion/t66-priority-action-acceptance.json');outcomes=[];adoptions=[]
for side in ['left','right']:
 letter=side[0].upper();ident='T66-PRIORITY-'+letter+'-RECTUS-KNEE';asset=next(a for a in b['motionAssets'] if a['id']==ident+'-ASSET');assert asset['poseControl']['endDegrees']==15
 oldarpath='atlas-data/motion/authoring/'+ident.lower()+'.json';author=copy.deepcopy(load(oldarpath));candidate=O/('enlargement-knee-'+side+'-r4');outcome=json.loads((O/('enlargement-knee-action-outcome-'+('left-r4' if side=='left' else 'r4')+'.json')).read_text())[0];assert outcome['passed'] and outcome['endDegrees']==19.5
 dest=O/('adopted-knee-'+side);dest.mkdir(exist_ok=True)
 for fn in ['input.json','geometry-record.json','contact-qc.json','glb-pose-qc.json','repair-receipt.json']:
  shutil.copyfile(candidate/fn,dest/fn)
 fid='priority-knee-extension-'+side+'-amplitude-r2';arid='T66-PRIORITY-S05-'+letter+'-RECTUS-KNEE-AUTHORING';inp=json.loads((dest/'input.json').read_text());inp['family']['id']=fid;inp['revision']='t66-priority-knee-amplitude-r2';save(dest/'input.json',inp)
 geometry=json.loads((dest/'geometry-record.json').read_text());geometry['family']=inp['family'];geometry['inputSha256']=sha(json.dumps(inp,sort_keys=True,separators=(',',':')).encode())
 pose=json.loads((dest/'glb-pose-qc.json').read_text());pose['familyId']=fid;qcpaths={}
 for k,qp in outcome['geometryQcPaths'].items():
  target=dest/pathlib.Path(qp).name;shutil.copyfile(R/qp,target);qcpaths[k]=str(target.relative_to(R));q=json.loads(target.read_text());assert q['passed'] and q['motionGlbSha256']==outcome['motionSha256'];metric=next(m for m in geometry['surfaceMetrics'] if m['sourceKey']==k);metric.update(flips=q['geometry']['flippedFaceSamples'],minimumAreaRatio=q['geometry']['minimumAreaRatio'])
  row=next(r for r in pose['rows'] if r['sourceKey']==k);row.update(geometryQcPath=qcpaths[k],geometryQcSha256=sha(target.read_bytes()))
 save(dest/'geometry-record.json',geometry);save(dest/'glb-pose-qc.json',pose);cq=json.loads((dest/'contact-qc.json').read_text());cq['familyId']=fid;save(dest/'contact-qc.json',cq)
 uri='atlas-data/assets/motion/t66-priority-s05-'+side+'-knee/motion.glb';refuri='atlas-data/assets/derived-glb/t66-priority-s05-'+side+'-knee/reference.glb'
 for dst,src in [(uri,'motion.glb'),(refuri,'reference.glb')]:
  target=R/dst;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(candidate/src,target)
 assert sha((R/uri).read_bytes())==outcome['motionSha256']==geometry['motionSha256']
 oldsha=asset['sha256'];asset.update(uri=uri,sha256=outcome['motionSha256'],revision='t66-priority-knee-amplitude-r2');asset['sourceBinding']['sourceFamilyId']=fid;asset['poseControl']['endDegrees']=19.5;asset['staticBinding']['sourceAssetSha256']=geometry['restSha256']
 scene=next(s for s in scenes['sceneManifests'] if s['id']==asset['staticBinding']['sceneId']);scene.update(assetUri=refuri,sourceAssetSha256=geometry['restSha256'])
 definition=next(d for d in b['motionDefinitions'] if d['id']==asset['motionDefinitionId']);definition['sourceFamilyId']=fid;definition['staticReference']['sourceAssetSha256']=geometry['restSha256']
 action=next(a for a in b['muscleActions'] if a['id']==definition['actionId']);action['sourceFamilyId']=fid
 for ref in action['sourceRefs']:
  if ref['evidenceId']==author['id']:ref['evidenceId']=arid
 author.update(id=arid,sourceFamilyId=fid,motionSha256=geometry['motionSha256'],restSha256=geometry['restSha256'],geometryRecordPath=str((dest/'geometry-record.json').relative_to(R)),contactQcPath=str((dest/'contact-qc.json').relative_to(R)),glbPoseQcPath=str((dest/'glb-pose-qc.json').relative_to(R)),glbInterpolationQcPaths=qcpaths,actionOutcomePath=str((O/'current-knee-action-outcome.json').relative_to(R)))
 author['poseRange']['endDegrees']=19.5;definition['poseSourceRefs']=[{'layer':'authoring_record','field':'motion_pose_range','appliesTo':'motion_pose_range','contextId':None,'claimId':arid,'valueHash':vhash(author['poseRange']),'evidenceId':arid,'fieldEvidenceId':None}]
 outcome.update(motionUri=uri,geometryQcPaths=qcpaths,previousEndDegrees=15,angleMultiplier=1.3,previousMotionSha256=oldsha);outcomes.append(outcome)
 authorpath='atlas-data/motion/authoring/t66-priority-s05-'+side+'-knee.json';adoptions.append((author,authorpath,dest,uri,refuri))
save(O/'current-knee-action-outcome.json',outcomes)
for author,authorpath,dest,uri,refuri in adoptions:
 deps=[uri,refuri,'atlas-data/source-cache/datasets/za/compiled/manifest.json','atlas-data/overlays/za-local-integration.json',author['geometryRecordPath'],author['contactQcPath'],author['glbPoseQcPath'],author['actionOutcomePath'],*author['glbInterpolationQcPaths'].values(),str((dest/'input.json').relative_to(R)),str((dest/'repair-receipt.json').relative_to(R))]
 author['verificationDependencies']=[{'path':p,'sha256':sha((R/p).read_bytes())} for p in deps];save(R/authorpath,author);registry['records'].append({'id':author['id'],'path':authorpath,'sha256':sha((R/authorpath).read_bytes())})
 row=next(r for r in accept['rows'] if r['sourceKey']==author['supportedSubjectKeys'][0] and r['assetId'].endswith('KNEE-ASSET'));row.update(motionSha256=author['motionSha256'],authoringPath=authorpath,authoringSha256=sha((R/authorpath).read_bytes()),outcomePath=author['actionOutcomePath'],outcomeSha256=sha((R/author['actionOutcomePath']).read_bytes()))
for p,v in [('atlas-data/motion/motion-learning.json',b),('atlas-data/motion/motion-scenes.json',scenes),('atlas-data/motion/authoring/registry.json',registry),('atlas-data/motion/t66-priority-action-acceptance.json',accept)]:save(R/p,v)
save(O/'knee-adoption-receipt.json',{'adopted':outcomes,'priorAssetsAndEvidencePreserved':True,'sourceModified':False,'physiologicalROMClaimed':False,'otherPriorityAmplitudeClaimed':False})
print('bilateral native knee amplitude adopted; other asset amplitudes unchanged')
