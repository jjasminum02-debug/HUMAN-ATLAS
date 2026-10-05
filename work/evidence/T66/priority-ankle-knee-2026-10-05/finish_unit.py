"""Record scoped unit acceptance; never close the parent T66."""
from pathlib import Path
import json,hashlib,subprocess
R=Path(__file__).resolve().parents[4];O=Path(__file__).parent;P=str(O.relative_to(R));load=lambda p:json.loads((R/p).read_text());save=lambda p,v:(R/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');digest=lambda p:hashlib.sha256((R/p).read_bytes()).hexdigest()
common=[]
for p in ['atlas-data/motion/motion-learning.json','atlas-data/motion/authoring/registry.json','atlas-data/motion/motion-scenes.json','atlas-data/motion/motion-asset-sources.json']:
 before=json.loads((O/'baseline'/p).read_text());after=load(p);rows=[]
 for key,values in before.items():
  if isinstance(values,list):
   if values and isinstance(values[0],dict) and 'id' in values[0]:
    current={v['id']:v for v in after[key]};assert all(current.get(v['id'])==v for v in values),(p,key)
   else: assert all(v in after[key] for v in values),(p,key)
   rows.append({'field':key,'before':len(values),'after':len(after[key]),'preexistingRowsUnchanged':True})
  else:assert after[key]==values,(p,key)
 common.append({'path':p,'rows':rows})
save(P+'/common-input-preservation.json',common)
obs=load(P+'/browser/observations.json'); logs=load(P+'/browser/console-log.json'); cutoff='2026-10-05T06:47:34.756Z';final_logs=[l for l in logs if l['timestamp']>=cutoff];assert not [l for l in final_logs if l['level'] in ['error','warn'] or 'Motion package unavailable' in l['message']]
imgs=[{'path':str(p.relative_to(R)),'sha256':digest(str(p.relative_to(R))),'bytes':p.stat().st_size} for p in (O/'browser').glob('*.png')];save(P+'/browser/capture-manifest.json',imgs)
validation={'status':'passed','acceptanceScope':'T66 step02 bilateral tibialis anterior dorsiflexion and bilateral rectus femoris knee extension/hip flexion, native surrounding context and same-scene controls','contractRevision':'app-completion-2026-10-01','relatedTests':{'passed':50,'failed':0,'log':P+'/verification/final-related-tests.log'},'typecheck':'passed','productionSchema':load(P+'/verification/final-schema.log'),'productionViteBuild':'passed_with_existing_chunk_size_warning','buildLog':P+'/verification/final-build.log','browser':{'observations':len(obs),'viewportCssPx':[1280,720],'singleCanvas':True,'finalConsoleErrors':0,'finalConsoleWarnings':0,'consoleCutoffUtc':cutoff,'initialCaughtHipLoadFailureRepaired':True,'observationsPath':P+'/browser/observations.json','consolePath':P+'/browser/console-log.json','pngCount':len(imgs),'mobileDeviceValidationClaimed':False,'otherRequestedViewportValidationClaimed':False},'geometry':{'leftTADeformers':10,'TAInterpolationSamples':33,'kneeDeformersPerSide':14,'kneeInterpolationSamples':49,'hipAddedNativeCoMovingSurfacesPerSide':16,'hipContactPairsPerSide':241,'hipContactSamples':65,'hipCorrectiveSurfacesPerSide':5,'hipCorrectiveInterpolationSamples':129,'hipMaximumLocalPassiveCorrectionMetres':.0000395,'newContainment':0,'strictShapeQcPassed':True,'metadataOnlyChangeReceipt':P+'/hip-metadata-reuse-receipt.json'},'unresolvedProductBlockers':[],'knownVerificationLimitations':['Historical t66NerveScene test expects 199 bone bindings while the pre-unit baseline and current workspace have 865. The widened suite failed that one preexisting fixture; it is not counted as passed. Relevant 50-test suite passes.','Preexisting worker/runtime/validator/tool WIP is preserved. Selective local commit is a checkpoint of this unit on the existing workspace, not a claim that a clean HEAD checkout includes every preexisting dependency.','No GPU/memory/performance profile repeated; no continuous collision freedom or physiological ROM/activation/force claim.']}
save(P+'/final-validation.json',validation)
assets=load('atlas-data/motion/motion-learning.json')['motionAssets'];rows=[]
for a in assets:
 if a['id'].startswith('T66-PRIORITY-') or a['id']=='T59-ASSET-ZA-R-TIBANT-DF':
  rows.append({'assetId':a['id'],'sourceKey':a['sourceBinding']['subjectSourceKey'],'side':a['staticBinding']['side'],'uri':a['uri'],'sha256':a['sha256'],'sourceMembers':len(a['sourceBinding']['members']),'poseControl':a.get('poseControl')})
assert len(rows)==6; save(P+'/supported-actions.json',rows)
unit={'executionStatus':'completed','acceptance':'passed','contractRevision':'app-completion-2026-10-01','acceptanceScope':validation['acceptanceScope'],'productReadiness':'local_supported_ankle_knee_actions_ready','contentCompleteness':'partial','knownContentGaps':['TA inversion is not animated; full normal ROM and physiological muscle force/activation are not supported.','RF clips use bounded authored educational ranges; exact measured footprints and physiological patellar tracking are not claimed.','Five other priority groups and final T66 integration remain for subsequent authorized internal steps.','Whole-body target/part extent and deferred engineering backlog are unchanged.'],'unresolvedProductBlockers':[],'actualMuscleSourceSurfaces':4,'completedPriorityGroups':2,'priorityGroupDenominator':7,'exactSourceActionBindings':6,'uniqueGlbAssets':6,'newDerivedGlbAssets':5,'reusedUnchangedT59RightAsset':True,'kneeExtension':{'educationalPreparationDegrees':15,'actionDirection':'reverse','maximumHeelExcursionMetres':.1032,'membersPerSide':71,'allQuadricepsAndSupportedDistalMusclesPresent':True},'hipFlexion':{'educationalDegrees':12,'kneeHeld':True,'membersPerSide':88},'sourceOnly':True,'publicRedistribution':'held','humanReview':'not_performed','evidence':[P+'/REPORT.md',P+'/final-validation.json',P+'/supported-actions.json',P+'/action-outcome.json',P+'/knee-action-outcome.json',P+'/hip-context-outcome.json',P+'/browser/observations.json'],'nextManualFile':'work/plans/t66-priority-atlas-2026-10-05/03-shoulder-scapula.txt'}
e=load('work/EXECUTION.json');baseline=json.loads((O/'baseline/work/EXECUTION.json').read_text()); t=e['tasks']['T66']; assert t['executionStatus']=='in_progress' and t['acceptance']=='partial';t['progress']['priorityAnkleKneeUnit']=unit
pa=t['progress']['productAcceptance'];g=pa['knownContentGaps'];g['primaryPlayableMuscleSourceSurfaces']=4;g['priorityActualPlayableSources']={'Tibialis anterior muscle:right':1,'Tibialis anterior muscle:left':1,'Rectus femoris muscle:right':1,'Rectus femoris muscle:left':1};g['priorityVerifiedSourceActionBindings']=6;g['priorityVerifiedGlbAssets']=6;g['priorityNewDerivedAssetsThisUnit']=5;g['priorityGroupsWithRepresentativeActions']=2;g['priorityGroupsRemaining']=5;pa['unresolvedProductBlockers'][0]='우선7근육군 중 앞정강근·대퇴직근 양측 대표 작용은 완료했다. 대흉근·견갑거근·복직근·외복사근·능형근의 source/측/part별 작용 제작·연결·검증은 다음 내부 단계다.'
pa['evidence'].extend(unit['evidence']); t['progress']['priorityScopeAmendment2026-10-05']['nextManualPrompt']=unit['nextManualFile']
assert t['progress']['nextUnit']=='author-and-integrate-normal-motion-bone-and-nerve'
for k,v in baseline['tasks'].items():
 if k!='T66':assert e['tasks'][k]==v,k
for k,v in baseline.items():
 if k!='tasks':assert e[k]==v,k
save('work/EXECUTION.json',e);save(P+'/scoped-acceptance.json',unit)
print('step02 passed; parent T66 unchanged partial; six exact source actions')
