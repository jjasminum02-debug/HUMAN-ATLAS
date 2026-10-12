"""Validate recorded Q02 evidence and project only this ended unit's state."""
from pathlib import Path
import json,hashlib,math,copy
R=Path(__file__).resolve().parents[4];E=Path(__file__).parent;P=R/'work/evidence/MV2/2026-10-12-q01-learning-quality-r1'
load=lambda p:json.loads(p.read_text())
def save(p,value):p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def dom(name):
 j=load(E/(name+'.json'));assert len(j['canvas'])==1
 c=j['canvas'][0].get('data',j['canvas'][0]);return j,json.loads(c['scene']),json.loads(c['dataset'])
def dist(a,b):return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))
base=load(E/'original-glb-structure.json');raw=(R/base['uri']).read_bytes()
assert hashlib.sha256(raw).hexdigest()==base['sha256'] and len(raw)==31306820
loader=load(E/'real-loader-validation.json');assert loader['passed'] and len(loader['rows'])==2
geometry=load(E/'current-geometry-probe.json');assert geometry['allGeometryPassed']
layers=load(E/'adjacent-layers-full-vertex-probe.json');assert len(layers['rows'])==6
build=load(E/'build-final-r2.json');assert len(build)==13 and all(s['exitCode']==0 for s in build)
tests=(E/'related-tests-final.log').read_text();assert 'pass 21' in tests and 'fail 0' in tests
assert load(E/'browser-console-final.json')==[]
http=load(E/'actual-http-delivery-final.json');assert http['status']==200 and http['cachedStatus']==304 and http['sha256']==base['sha256']
root,renderer=None,None
browser=[]
for side in ['left','right']:
 index=load(E/f'final-{side}-loop-index.json');assert index
 assert any('복귀' in x['phase'] for x in index) and any('몸통 굽힘' in x['phase'] for x in index)
 assert min(int(x['progress']) for x in index)<=2 and max(int(x['progress']) for x in index)>=97
 for x in index:
  _,s,d=dom(x['name']);root=root or s['root'];renderer=renderer or s['renderer']
  assert s['root']==root and s['renderer']==renderer and d['motion']['surfaceCount']==365
  assert d['motionBytes']==61882524 and s['registeredUpdates']==1
 _,s,d=dom('final-'+side+'-original-restored');assert s['root']==root and s['renderer']==renderer
 assert d['motion'] is None and d['motionBytes']==0 and s['registeredUpdates']==0
 assert s['geometryBuffersBytes']==9313398 and s['cameraOwner'] is None
 browser.append({'side':side,'captured1xFrames':len(index),'preparationActionReturnAndRepeatObserved':True,'motionSourceBytes':31306820,'nativeGeometryRestoredBytes':s['geometryBuffersBytes']})
_,s,d=dom('final-fast-switch-other-muscle');assert d['motion'] is None and d['motionBytes']==0
# The existing camera transition can still own one update immediately after a
# rapid selection. It is not retained motion memory; require zero after settling.
transientUpdatesAtSwitch=s['registeredUpdates']
_,s,d=dom('final-other-original-restored');assert d['motion'] is None and d['motionBytes']==0 and s['registeredUpdates']==0
_,s,d=dom('final-acupoint-territory-reentry');assert d['motion'] is None and d['motionBytes']==0
assert s['root']==root and s['renderer']==renderer
_,s,d=dom('final-acupoint-closed-original');assert d['motion'] is None and s['registeredUpdates']==0
off=[]
for n in ['final-layer-off-before-r2','final-layer-off-during-r2','final-layer-off-restored-r2']:
 j,s,d=dom(n);assert '뼈' not in j['pressed'];off.append((s,d))
assert len({s['root'] for s,d in off})==1 and len({s['renderer'] for s,d in off})==1
assert off[1][1]['motionBytes']==61882524 and off[2][1]['motionBytes']==0 and off[2][0]['registeredUpdates']==0
before,bs,bd=dom('final-review-before-r2');after,as_,ad=dom('final-review-closed-r2')
assert bs['root']==as_['root'] and bs['renderer']==as_['renderer']
assert bs['geometryBuffersBytes']==as_['geometryBuffersBytes']==6947334
assert as_['registeredUpdates']==0 and as_['cameraOwner'] is None
assert bd['selected']==ad['selected'] and before['pressed']==after['pressed']
reviewError=max(dist(bs['camera'],as_['camera']),dist(bs['target'],as_['target']));assert reviewError<1e-8
preserved=load(E/'preservation-check.json');assert preserved['passed']
limits={'sourceEOInsideIOBaselineUniqueVerticesPerSide':291,'sampledNewEOInsideIOVerticesPerSide':3,
 'maximumNewSampledNearestSurfaceDepthMm':max(s['newNearestDepthMaxMm'] for r in layers['rows'] for s in r['samples']),
 'layerProbePosesPerSide':5,'uniqueSourceVerticesPerSide':2665,'allSurfaceIntersectionsExcluded':False,
 'measuredAttachmentFootprints':False,'physiologicalCertification':False,
 'interpretation':'Native rough/overlapping surfaces retained. Small new sampled soft-layer overlaps are disclosed; local teaching/legibility acceptance is not anatomical normality or zero intersection approval.'}
result={'task':'MV2','unit':'MV1-Q02-left-external-oblique-lateral-layering','owner':'Sol xhigh',
 'acceptancePassed':True,'engineeringContractPassed':True,'learningExpressionAssessment':'passed_model_demo_with_native_surface_limits',
 'geometryDisposition':'no_target_geometry_repair_required_by_observed_teaching_scope','geometryModified':False,
 'confirmedNewGeometryDefects':0,'sourceOnly':True,'humanReview':'not_performed','publicRedistribution':'held',
 'source':base,'actualFinalAuthoring':'work/evidence/T66/priority-trunk-2026-10-05/flex',
 'reusedExactBaseBoneContactQcSamplesPerSide':65,'newActualGlbGeometrySamplesPerSide':129,
 'actualLoaderSamplesPerSide':129,'geometryAndMorphBytes':30384012,'animationBytes':191692,
 'memoryEstimateBytes':61882524,'motionTriangles':320362,'motionDrawCalls':365,
 'driverVramMeasured':False,'sourceBudgetBytesBeforeAndAfter':31306820,'unrelatedAssetBudgetBytes':8388608,
 'browser':browser,'visuallyReviewedSelected1xFrames':len(load(E/'visually-reviewed-frame-selection.json')),
 'otherMuscleSwitchAndResourceRelease':True,'transientSceneUpdatesAtRapidSelection':transientUpdatesAtSwitch,
 'staticAcupointGuardAndTerritoryReentry':True,
 'AT22ReviewRestoreCameraErrorMetres':reviewError,'AT22ReviewEditedOrSaved':False,
 'layerOffPreserved':True,'relatedTestsPassed':21,'packageBuildChecksPassed':13,'consoleErrorsAndWarnings':0,
 'limits':limits,'bundleRemainingRequiredUnits':[],'wholeMV2Complete':False,
 'remainingGroups':3,'remainingMappings':31,'nextRepairUnit':'MV1-Q03-biceps-lateral-contour-and-visibility',
 'nextScheduledTask':'AT8','automaticExecution':False}
save(E/'validation-final.json',result)
# Preserve the frozen source queue and all other groups; add only Q02's disposition.
queue=load(P/'repair-queue.json');q=next(x for x in queue['candidateGroups'] if x['queueId']==result['unit'])
q['previousObservationState']=q['status'];q['status']='resolved_local_teaching_with_native_surface_limits'
q['resolution']={'acceptancePassed':True,'geometryModified':False,
 'causeAssessment':'Existing native folded/overlapping sheet plus viewing-side occlusion and source-context transparency; no visible Q02-specific detached/popping/flip defect demonstrated. Actual small soft-layer overlap retained and measured separately.',
 'implementedCauseFix':'Common exact-base asset budget contract in resolver/delivery, exact repair length/base file validation and repair-chain rejection.',
 'evidence':'work/evidence/MV2/2026-10-12-q02-r1/validation-final.json','limits':limits}
queue.update(run='2026-10-12-q02-r1',ownerNext='MV2 / Sol xhigh',bundleAcceptancePassed=True,overallStatus='partial',remainingGroups=3,remainingMappings=31)
queue['latestResolvedUnit']=result['unit'];save(E/'repair-queue.json',queue)
remaining=load(P/'remaining-units.json');remaining.update(thisBundle=result['unit'],thisBundleAcceptancePassed=True,remainingMappings=31,nextRepairUnit=result['nextRepairUnit'])
remaining['remainingGroups']=[x for x in remaining['remainingGroups'] if x['queueId']!=result['unit']]
remaining['neededInput']='No new external input required. Next explicit MV2 request diagnoses Q03 three biceps mappings; Q04/Q05 remain observed_ambiguous and are not promoted. Existing native surface limits do not certify anatomy.'
remaining['q02NativeSurfaceLimits']=limits;save(E/'remaining-units.json',remaining)
# Re-read immediately before writing. Compare all unrelated records/plans afterward.
path=R/'work/EXECUTION.json';execution=load(path);before=copy.deepcopy(execution)
unit=execution['featureWorkUnits']['MV2'];assert unit['lastRun']['unit']=='q01-learning-quality' and unit['lastRun']['acceptancePassed']
unit['priorLearningQualityRun']=copy.deepcopy(unit['lastRun']);unit['priorLearningQualityRun']['localImplementationCommit']='2d182a6fcce068409c804f4e7391f607c14a3b20'
unit.update(owner='Sol xhigh',status='partial',acceptancePassed=False,evidence='work/evidence/MV2/2026-10-12-q02-r1',updatedDate='2026-10-12',
 repairQueue='work/evidence/MV2/2026-10-12-q02-r1/repair-queue.json',remainingUnits='work/evidence/MV2/2026-10-12-q02-r1/remaining-units.json',
 nextRepairUnit=result['nextRepairUnit'],nextScheduledTask='AT8',nextPrompt='work/evidence/MV2/2026-10-12-q02-r1/next-prompt-MV2-Q03.txt')
unit['lastRun']={'date':'2026-10-12','unit':result['unit'],'owner':'Sol xhigh','startingHead':load(E/'start.json')['head'],
 'acceptancePassed':True,'engineeringValidationPassed':True,'learningExpressionAssessment':result['learningExpressionAssessment'],
 'geometryModified':False,'finalAssets':[base['uri']],'actualSha256':base['sha256'],'actualBytes':base['bytes'],
 'sameSceneLearnerSidesVerified':2,'denseFinalGlbTimesPerSide':129,'relatedTestsPassed':21,'packageBuildChecksPassed':13,
 'validation':'work/evidence/MV2/2026-10-12-q02-r1/validation-final.json','humanReview':'not_performed','publicRedistribution':'held',
 'physiologicalCertification':False,'limits':limits,'commitReceipt':'work/evidence/MV2/2026-10-12-q02-r1/commit-receipt.json'}
unit['result'].update(resolvedGroups=2,resolvedMappings=3,remainingObservedAmbiguousGroups=3,remainingObservedAmbiguousMappings=31,wholeMV2Complete=False)
execution['featurePlans']['motion-quality-review']['lastDisposition']='Q01 engineering and q01-learning-quality r9 pass preserved; Q02 local teaching inspection/budget contract pass with explicit native-surface overlap limits and unchanged GLB. MV2 partial: Q03/Q04/Q05, 3 groups/31 mappings; next explicit repair Q03; AT next AT8. No automatic execution.'
for key in execution:
 if key not in ['featureWorkUnits','featurePlans']:assert execution[key]==before[key]
for k in execution['featureWorkUnits']:
 if k!='MV2':assert execution['featureWorkUnits'][k]==before['featureWorkUnits'][k]
for k in execution['featurePlans']:
 if k!='motion-quality-review':assert execution['featurePlans'][k]==before['featurePlans'][k]
save(E/'execution-projection-before.json',before);save(path,execution)
save(E/'execution-owned-update.json',{'onlyChangedRecords':['featureWorkUnits.MV2','featurePlans.motion-quality-review.lastDisposition'],'ATRecordsAndAcupointPlanUnchanged':True})
print('Q02 evidence assertions passed; only MV2 and related motion disposition projected; overall MV2 partial, 3 groups/31 mappings.')
