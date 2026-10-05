"""Register only independently verified current native priority action assets.
Retain historical assets/author records, same exact selectors and shared families.
"""
import json,pathlib,hashlib,copy,shutil,sys
R=pathlib.Path(__file__).resolve().parents[4];O=pathlib.Path(__file__).parent
load=lambda p:json.loads((R/p).read_text());sha=lambda b:hashlib.sha256(b).hexdigest();vh=lambda v:sha(json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode())
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');return str(p.relative_to(R))
b=load('atlas-data/motion/motion-learning.json');sc=load('atlas-data/motion/motion-scenes.json');rg=load('atlas-data/motion/authoring/registry.json');ac=load('atlas-data/motion/t66-priority-action-acceptance.json');receipt=[]
for label in sys.argv[1:]:
 kind,side=label.split('-');candidate=O/('enlargement-'+label+'-r2');inp=json.loads((candidate/'input.json').read_text());geo=json.loads((candidate/'geometry-record.json').read_text());pose=json.loads((candidate/'glb-pose-qc.json').read_text());outcome=json.loads((candidate/'action-outcome.json').read_text());assert pose['passed'] and all(o['passed'] for o in outcome);oldarpath='atlas-data/motion/authoring/t66-priority-s03-'+side[0]+'-'+kind+'-authoring.json';ar=copy.deepcopy(load(oldarpath));oldfid=ar['sourceFamilyId'];fid=oldfid+'-amplitude-r2';arid='T66-PRIORITY-S05-'+side[0].upper()+'-'+kind.upper()+'-AUTHORING';assert not any(r['id']==arid for r in rg['records']);dest=O/('adopted-'+label);dest.mkdir(exist_ok=True)
 for name in ['input.json','geometry-record.json','glb-pose-qc.json','contact-qc.json','stationary-neck-receipt.json']:
  if (candidate/name).exists():shutil.copyfile(candidate/name,dest/name)
 inp['family']['id']=fid;inp['revision']='priority-amplitude-r2';save(dest/'input.json',inp);geo['family']=inp['family'];geo['inputSha256']=sha(json.dumps(inp,sort_keys=True,separators=(',',':')).encode());pose['familyId']=fid;qps={}
 for qp in candidate.glob('interpolation-*.json'):
  q=json.loads(qp.read_text());assert q['passed'] and q['motionGlbSha256']==geo['motionSha256'];target=dest/qp.name;shutil.copyfile(qp,target);key=q['targetSourceKey'];qps[key]=str(target.relative_to(R));row=next(r for r in pose['rows'] if r['sourceKey']==key);row.update(passed=True,geometryQcPath=qps[key],geometryQcSha256=sha(target.read_bytes()));metric=next(m for m in geo['surfaceMetrics'] if m['sourceKey']==key);metric.update(flips=q['geometry']['flippedFaceSamples'],minimumAreaRatio=q['geometry']['minimumAreaRatio'])
 save(dest/'geometry-record.json',geo);save(dest/'glb-pose-qc.json',pose);cq=json.loads((dest/'contact-qc.json').read_text());cq['familyId']=fid;assert cq['passed'];save(dest/'contact-qc.json',cq)
 uri='atlas-data/assets/motion/t66-priority-s05-'+label+'/motion.glb';refuri='atlas-data/assets/derived-glb/t66-priority-s05-'+label+'/reference.glb'
 for target,name in [(uri,'motion.glb'),(refuri,'reference.glb')]:
  path=R/target;path.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(candidate/name,path)
 assert sha((R/uri).read_bytes())==geo['motionSha256'];assert sha((R/refuri).read_bytes())==geo['restSha256'];assets=[a for a in b['motionAssets'] if a.get('sourceBinding',{}).get('sourceFamilyId')==oldfid];assert len(assets)==len(ar['motorRoleSourceKeys']);oldshas={a['id']:a['sha256'] for a in assets}
 for a in assets:
  a.update(uri=uri,sha256=geo['motionSha256'],revision='t66-priority-amplitude-r2');a['sourceBinding']['sourceFamilyId']=fid;a['poseControl']['endDegrees']=inp['family']['endDegrees'];a['staticBinding']['sourceAssetSha256']=geo['restSha256'];d=next(d for d in b['motionDefinitions'] if d['id']==a['motionDefinitionId']);d['sourceFamilyId']=fid;d['staticReference']['sourceAssetSha256']=geo['restSha256'];action=next(x for x in b['muscleActions'] if x['id']==d['actionId']);action['sourceFamilyId']=fid
  for ref in action['sourceRefs']:
   if ref['evidenceId']==ar['id']:ref['evidenceId']=arid
  d['poseSourceRefs']=[{'layer':'authoring_record','field':'motion_pose_range','appliesTo':'motion_pose_range','contextId':None,'claimId':arid,'valueHash':vh({**ar['poseRange'],'endDegrees':inp['family']['endDegrees']}),'evidenceId':arid,'fieldEvidenceId':None}]
  oldscene=next(s for s in sc['sceneManifests'] if s['id']==a['staticBinding']['sceneId']);newsceneid='T66-PRIORITY-S05-'+side[0].upper()+'-'+kind.upper()+'-REFERENCE'
  if not any(s['id']==newsceneid for s in sc['sceneManifests']):
   scene=copy.deepcopy(oldscene);scene.update(id=newsceneid,assetUri=refuri,sourceAssetSha256=geo['restSha256']);sc['sceneManifests'].append(scene)
  a['staticBinding']['sceneId']=newsceneid;d['staticReference']['sceneId']=newsceneid
 for o in outcome:o.update(motionUri=uri,geometryQcPaths=qps,sourceFamilyId=fid,previousEndDegrees=ar['poseRange']['endDegrees'])
 outcomePath=save(dest/'action-outcome.json',outcome);ar.update(id=arid,sourceFamilyId=fid,motionSha256=geo['motionSha256'],restSha256=geo['restSha256'],geometryRecordPath=str((dest/'geometry-record.json').relative_to(R)),contactQcPath=str((dest/'contact-qc.json').relative_to(R)),glbPoseQcPath=str((dest/'glb-pose-qc.json').relative_to(R)),glbInterpolationQcPaths=qps,actionOutcomePath=outcomePath);ar['poseRange']['endDegrees']=inp['family']['endDegrees'];ar['coMovingContextKeys']=[e['sourceKey'] for e in inp['members'] if e['role']=='co_moving_context'];ar['passiveDeformationKeys']=[e['sourceKey'] for e in inp['members'] if e['role'].startswith('deforming')];roles={e['sourceKey']:e['role'] for e in inp['members']}
 for row in ar['sourceRows']:
  if row.get('sourceKey') in roles:row['role']=roles[row['sourceKey']]
 deps=[uri,refuri,'atlas-data/source-cache/datasets/za/compiled/manifest.json','atlas-data/overlays/za-local-integration.json',ar['geometryRecordPath'],ar['contactQcPath'],ar['glbPoseQcPath'],outcomePath,*qps.values(),str((dest/'input.json').relative_to(R)),'work/evidence/T66/priority-integration-2026-10-05/latissimus-passive-source-fields.json',ar['qualitativeActionEvidencePath']]
 if (dest/'stationary-neck-receipt.json').exists():deps.append(str((dest/'stationary-neck-receipt.json').relative_to(R)))
 ar['verificationDependencies']=[{'path':p,'sha256':sha((R/p).read_bytes())} for p in deps];ap='atlas-data/motion/authoring/t66-priority-s05-'+label+'.json';save(R/ap,ar);rg['records'].append({'id':arid,'path':ap,'sha256':sha((R/ap).read_bytes())})
 for row in ac['rows']:
  if row['assetId'] in oldshas:row.update(motionSha256=ar['motionSha256'],authoringPath=ap,authoringSha256=sha((R/ap).read_bytes()),outcomePath=outcomePath,outcomeSha256=sha((R/outcomePath).read_bytes()))
 receipt.append({'familyId':fid,'assets':list(oldshas),'exactMotorSourceKeys':ar['motorRoleSourceKeys'],'previousMotionHashes':oldshas,'motionUri':uri,'motionSha256':ar['motionSha256'],'range':ar['poseRange']['endDegrees'],'angleMultiplier':1.3,'nativeSurroundingContextCount':len(inp['members']),'anatomicalApprovalAdded':False})
for p,v in [('atlas-data/motion/motion-learning.json',b),('atlas-data/motion/motion-scenes.json',sc),('atlas-data/motion/authoring/registry.json',rg),('atlas-data/motion/t66-priority-action-acceptance.json',ac)]:save(R/p,v)
save(O/('shoulder-adoption-'+('-'.join(sys.argv[1:]))+'.json'),receipt);print('Adopted',len(receipt),'native shoulder families')
