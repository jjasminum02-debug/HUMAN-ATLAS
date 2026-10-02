#!/usr/bin/env python3
"""Register the exact T59 engine-validation candidate; shared authoring is separate."""
import json,hashlib,copy,shutil
from pathlib import Path
r=Path(__file__).resolve().parents[2]
def read(p):return json.loads((r/p).read_text())
def dump(p,v):f=r/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256((r/p).read_bytes()).hexdigest()
s=read('atlas-data/schemas/motion-learning.schema.json');s['$defs']['EvidenceRef']['properties']['layer']['enum']=list(dict.fromkeys(s['$defs']['EvidenceRef']['properties']['layer']['enum']+['authoring_record']));s['$defs']['SourceMotionMember']['properties']['role']['enum']=list(dict.fromkeys(s['$defs']['SourceMotionMember']['properties']['role']['enum']+['deforming_passive_surface','co_moving_context']));dump('atlas-data/schemas/motion-learning.schema.json',s)
record=read('work/evidence/T59/resume-2026-10-02/candidate/authoring-record.json')
# Actual static source subset; retained for binding verification, never a second viewer.
for src,dst in [('reference.glb','atlas-data/assets/derived-glb/t59-za-right-ankle/reference.glb'),('motion.glb','atlas-data/assets/motion/t59-za-right-ankle/motion.glb')]:
 f=r/dst;f.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(r/'work/evidence/T59/resume-2026-10-02/candidate'/src,f)
recordPath='atlas-data/motion/authoring/t59-za-right-ankle.json';dump(recordPath,record)
m=read('atlas-data/source-cache/datasets/za/compiled/manifest.json');o=read('atlas-data/overlays/za-local-integration.json')
reg={'schemaVersion':'t59-motion-authoring-registry-v1','records':[{'id':record['id'],'path':recordPath,'sha256':sha(recordPath)}],
 'sources':[{'id':'ZA-c7010a9-PINNED-LOCAL','licenseId':'LIC-ZA-PINNED-LOCAL-DECISION','datasetPath':'atlas-data/source-cache/datasets/za/compiled/manifest.json','datasetSha256':sha('atlas-data/source-cache/datasets/za/compiled/manifest.json'),
 'rightsEvidencePath':o['policy']['rightsEvidence'],'rightsEvidenceSha256':o['policy']['rightsEvidenceSha256'],'localUse':'inherits_pinned_source_decision','publicRedistribution':'held','humanReview':'not_performed'}]};dump('atlas-data/motion/authoring/registry.json',reg)
scene={'sceneId':'ZA-T59-R-ANKLE-SOURCE-SNAPSHOT','sceneRevision':m['revision'],'modelId':m['namespace'],'sourceAssetSha256':record['restSha256'],'frameId':m['frameContract']['targetFrameId'],'units':'m','poseId':m['frameContract']['staticReferencePose']['id']}
scenes=read('atlas-data/motion/motion-scenes.json');scenes['sceneManifests']=[x for x in scenes['sceneManifests'] if x['id']!=scene['sceneId']];scenes['sceneManifests'].append({'id':scene['sceneId'],'revision':scene['sceneRevision'],'modelId':scene['modelId'],'sourceAssetSha256':scene['sourceAssetSha256'],'frameId':scene['frameId'],'units':'m','poseId':scene['poseId'],'assetUri':'atlas-data/assets/derived-glb/t59-za-right-ankle/reference.glb','side':'right','sourceJoint':'authored-talar-dome-hinge-not-measured-axis','separateFromNavigationFrame':False,'annotationPolicy':{'verifiedBoneLocalBindings':[],'hideAllSpatialAnnotationsDuringMotion':True}});dump('atlas-data/motion/motion-scenes.json',scenes)
bundle=read('atlas-data/motion/motion-learning.json');bundle['muscleActions']=[x for x in bundle['muscleActions'] if not x['id'].startswith('T59-')];bundle['motionDefinitions']=[x for x in bundle['motionDefinitions'] if not x['id'].startswith('T59-')];bundle['motionAssets']=[x for x in bundle['motionAssets'] if not x['id'].startswith('T59-')];action=copy.deepcopy(next(x for x in bundle['muscleActions'] if x['id']=='T24-ACTION-HA-M-000003-R-ANKLE-DF'));action['id']='T59-ACTION-ZA-R-TIBANT-DF';action['sourceSubjectKeys']=['ZA-c7010a9-54ae5266082b61f48ed8e83e'];action['learnerActionKey']='option-003';action['explanation']='앞정강근의 발목 등쪽굽힘 방향을 보여 주는 교육용 표면 변형입니다. 실제 수축량이나 개인의 운동 범위를 재현하지 않습니다.'
bundle['muscleActions'].append(action)
defn={'id':'T59-MOTION-ZA-R-TIBANT-DF','actionId':action['id'],'instanceId':action['sourceSubjectKeys'][0],'side':'right','targetJointIds':action['targetJointIds'],
 'movingStructureIds':[x['sourceKey'] for x in record['members'] if x['role']=='moving_structure'],'fixedStructureIds':[x['sourceKey'] for x in record['members'] if x['role']=='fixed_structure'],
 'staticReference':scene,'startPoseId':scene['poseId'],'endPoseId':record['poseRange']['endPoseId'],
 'poseSourceRefs':[{'layer':'authoring_record','field':'motion_pose_range','appliesTo':'motion_pose_range','contextId':None,'claimId':record['id'],'valueHash':hashlib.sha256(json.dumps(record['poseRange'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'evidenceId':record['id'],'fieldEvidenceId':None}]}
bundle['motionDefinitions'].append(defn)
asset={'id':'T59-ASSET-ZA-R-TIBANT-DF','motionDefinitionId':defn['id'],'uri':'atlas-data/assets/motion/t59-za-right-ankle/motion.glb','revision':'T59-2026-10-02-source-derived-r2','sha256':record['motionSha256'],
 'sourceId':reg['sources'][0]['id'],'licenseId':reg['sources'][0]['licenseId'],'representationType':'source_bound_surface',
 'staticBinding':{**{k:v for k,v in scene.items() if k!='poseId'},'side':'right','referencePoseId':scene['poseId']},
 'rig':{'id':'T59-AUTHORED-RIG-ZA-R-ANKLE','nodeBindings':[{'structureId':x['sourceKey'],'nodeId':x['nodeId']} for x in record['members'] if x['role']=='moving_structure']},'illustration':None,
 'clip':{'id':'T59-ZA-R-ANKLE-DF5','durationSeconds':2,'startPoseId':scene['poseId'],'endPoseId':defn['endPoseId']},
 'sourceBinding':{'contractVersion':'t59-source-motion-binding-v1','datasetNamespace':m['namespace'],'datasetRevision':m['revision'],'integrationRevision':o['revision'],'sourceOverlaySha256':sha('atlas-data/overlays/za-local-integration.json'),
 'subjectSourceKey':defn['instanceId'],'frameId':scene['frameId'],'units':'m','referencePoseId':scene['poseId'],'deformation':'morph_targets','members':record['members']},
 'technicalStatus':'binding_verified'};bundle['motionAssets'].append(asset);bundle['revision']='T59-2026-10-02-source-derived-r2';dump('atlas-data/motion/motion-learning.json',bundle)
p=read('atlas-data/motion/motion-asset-sources.json');p['productionMotionAssetIds']=[x for x in p['productionMotionAssetIds'] if x!=asset['id']];p['productionMotionAssetIds'].append(asset['id']);dump('atlas-data/motion/motion-asset-sources.json',p)
