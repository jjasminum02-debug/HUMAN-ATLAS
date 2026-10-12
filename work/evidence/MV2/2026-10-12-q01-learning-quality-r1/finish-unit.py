"""Write the one-unit result; preserve other queue groups and latest EXECUTION."""
from pathlib import Path
import json,copy,hashlib,subprocess
R=Path.cwd();E=Path(__file__).resolve().parent;relative=str(E.relative_to(R))
def read(p):return json.loads(Path(p).read_text())
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
records=[read(E/f'{s}-candidate-r9/record.json') for s in ['left','right']]
loader=read(E/'real-loader-validation-r9.json');independent=read(E/'actual-independent-replay-r9.json')
assert loader['passed'] and independent['passed']
assert all(all(v['passed'] and v['flips']==0 and v['newContactMax']==0 for v in r['checks'].values()) for r in records)
assert all(r['other70NodesMaxChangeMetres']==0 and r['compactReplayMaxMetres']==0 for r in records)
assert all(r['proximalFixedErrorMetres']==0 and r['distalMovingPathErrorMetres']<1e-7 for r in records)
assert all(r['rights']['publicRedistribution']=='held' and r['rights']['humanReview']=='not_performed' for r in records)
build=read(E/'build-final-r2.json');assert len(build)==13 and all(r['exitCode']==0 for r in build)
assert '\u2113 pass 17' in (E/'related-tests-r9.log').read_text() or '\u2139 pass 17' in (E/'related-tests-r9.log').read_text()
assert read(E/'AT22-restoration-r1.json')['passed'] and read(E/'acupoint-restoration-r1.json')['passed']
assert read(E/'browser-console-r1.json')['passed']
assert read(E/'browser-console-final-r2.json')['passed'] and read(E/'q01-acupoint-restoration-r1.json')['passed']
manifest=read(R/'atlas-data/motion/source-motion-repairs-r1.json')
unit={'unit':'q01-learning-quality','acceptancePassed':True,'engineeringValidationPassed':True,
 'learningExpressionAssessment':'passed_model_demo','scope':'source-addressed bilateral rectus knee teaching demo; source-axis excursion and return, not physiological certification',
 'selectedCandidate':'r9','finalAssets':[{k:v for k,v in x.items() if k!='bindingSignature'} for x in manifest['rows']],
 'denseTimesPerSide':193,'sameSceneLearnerSidesVerified':2,'actualIndependentReplay':independent,
 'proximalSourceVerticesHeldPerSide':len(records[0]['fixedVertexIndices']),
 'distalPriorMovingVerticesPerSide':len(records[0]['movingVertexIndices']),
 'mainBellyProxyShorteningMm':[r['metrics'][-1]['mainBellySectionCentroidPathMm']-r['metrics'][0]['mainBellySectionCentroidPathMm'] for r in records],
 'bodyMaximumDisplacementMm':[r['metrics'][-1]['bodyMaxDisplacementMm'] for r in records],
 'visualEvidence':{'oneSpeedSeries':['final-left-cycle-ledger.json','final-right-cycle-ledger.json','final-left-attachment-cycle-ledger.json'],'capturedSeriesFrames':175,
   'selectedRepresentatives':'visual-representatives-r1.json','staticPoses':['final-left-comparison100-r4','final-left-comparison50-r4','final-left-comparison0-r4','final-left-complete-attachment100-r1','final-left-complete-attachment50-r1','final-left-complete-attachment0-r1','final-right-context100-r1','final-right-context50-r1','final-right-context0-r1','final-right-side100-r1','final-right-side90-r1','final-right-side0-r1'],
   'captureCountIsNotVisualInspectionCount':True,'actualViewports':[[1280,720]],'cameraComparison':'actual-camera-comparison-r1.json'},
 'relatedTestsPassed':17,'packageBuildChecksPassed':13,'noProductCameraOrUIChange':True,
 'existingEngineeringPassPreserved':True,'autoRunNext':False,'humanReview':'not_performed','publicRedistribution':'held','physiologicalCertification':False,
 'limits':{'newSampledVastusContainmentMaximaPerSide':[3,3,2],'newSampledNearestSurfaceDepthMaximumMm':1.8498557955100856,
   'evidence':'neighbor-contact-comparison-r9.json / neighbor-new-depth-r9.json',
   'interpretation':'coarse source surfaces already overlap; r9 adds small local residual vertex overlap. Existing four-bone contact criterion remains zero. This is not a claim of zero surface intersections or physiological contact.',
   'measuredFascicleOrAttachmentFootprint':False,'volumeClaim':False,'automaticFraming':'unchanged; presentation deferred to user-requested later UI work; local manual observations completed'},
 'remainingRequiredUnitsInThisScope':[],'wholeMV2Complete':False}
write(E/'validation-final-r1.json',unit)
attempts=read(E/'attempt-ledger-r1.json');attempts['rows'][-1]['disposition']='selected after actual loader and learner QA';write(E/'attempt-dispositions-final-r1.json',attempts)
queue=read(R/'work/evidence/MV2/2026-10-12-q01-r1/repair-queue.json');original=copy.deepcopy(queue)
q01=next(q for q in queue['candidateGroups'] if q['queueId'].startswith('MV1-Q01'))
q01['learningQualityRun']={'unit':'q01-learning-quality','acceptancePassed':True,'evidence':relative,'selectedCandidate':'r9','physiologicalCertification':False,'sourceSoftTissueOverlapLimit':unit['limits']}
queue['latestLearningUnit']='q01-learning-quality';queue['latestLearningEvidence']=relative
assert queue['candidateGroups'][1:]==original['candidateGroups'][1:]
write(E/'repair-queue.json',queue)
remaining=read(R/'work/evidence/MV2/2026-10-12-q01-r1/remaining-units.json');remaining.update(thisBundle='q01-learning-quality',thisBundleAcceptancePassed=True,thisBundleRemainingRequiredUnits=[],learningQualityLimits=unit['limits'],nextScheduledTask='AT8')
assert remaining['remainingMappings']==32 and len(remaining['remainingGroups'])==4
write(E/'remaining-units.json',remaining)
next_prompt='''HUMAN ATLAS에서 MV2의 MV1-Q02-left-external-oblique-lateral-layering 한 묶음만 수행해라. 담당 Sol High.
AGENTS.md, 최신 EXECUTION, work/tasks/MV2.md, work/plans/mv2-completion-2026-10-12/MV2-SOL-RESUME.md와 최신 MV2 보고서/repair-queue/remaining-units를 읽어라.
q01-learning-quality의 r9 양측 local teaching pass 및 잔여 source soft-tissue overlap 한계를 보존해라. Q01 engineering/표현 검사와 MV1 전수 조사를 반복하지 마라.
Q02의 실제 외복사근 측면 겹침·관통·가림을 분리하고 source-addressed 최소 수정을 검증해라. 기존 31,306,820-byte trunk exact-source 예외와 repair 8MiB 제한의 공통 예산 계약 불일치를 이 묶음에서 확인하고, 미사용 buffer 정리를 우선하되 범용 예산을 조용히 올리지 마라.
실제 emitted GLB/learner/주변 구조/중간 프레임/복귀를 검증하고 원본·WIP·AT21/22·카메라/UI를 보존해라. versioned evidence/report, 최신 MV2 record와 해당 motion plan만 갱신하고 sync_execution.py 및 --check 후 소유 변경만 로컬 커밋해라.
다른 묶음·AT8 자동 실행·위임·push·배포는 하지 마라.
'''
(E/'next-prompt-MV2-Q02.txt').write_text(next_prompt)
execution=read(R/'work/EXECUTION.json');before=copy.deepcopy(execution);write(E/'execution-before-final-update.json',before)
mv=execution['featureWorkUnits']['MV2'];mv.setdefault('priorEngineeringRun',copy.deepcopy(mv['lastRun']))
mv['lastRun']={'date':'2026-10-12','unit':'q01-learning-quality','acceptancePassed':True,'engineeringValidationPassed':True,'learningExpressionAssessment':'passed_model_demo',
 'selectedCandidate':'r9','finalAssets':[r['uri'] for r in manifest['rows']],'sourcePinnedRepairManifest':'atlas-data/motion/source-motion-repairs-r1.json',
 'sameSceneLearnerSidesVerified':2,'denseFinalGlbTimesPerSide':193,'relatedTestsPassed':17,'packageBuildChecksPassed':13,
 'validation':relative+'/validation-final-r1.json','humanReview':'not_performed','publicRedistribution':'held','physiologicalCertification':False,'limits':unit['limits']}
mv.update(status='partial',acceptancePassed=False,evidence=relative,updatedDate='2026-10-12',repairQueue=relative+'/repair-queue.json',remainingUnits=relative+'/remaining-units.json',
 nextRepairUnit='MV1-Q02-left-external-oblique-lateral-layering',nextScheduledTask=execution['featurePlans']['acupoint-at-361']['nextUnit'],nextPrompt=relative+'/next-prompt-MV2-Q02.txt',noAutoAdvance=True)
mv['result']['wholeMV2Complete']=False;mv['result']['learningQualityUnitsPassed']=1
execution['featurePlans']['motion-quality-review']['lastDisposition']='MV1 inspection preserved (0 uninspected); Q01 engineering pass and q01-learning-quality r9 bilateral teaching pass; MV2 partial with Q02–Q05, 4 groups/32 mappings remaining. No automatic execution.'
assert all(execution['featureWorkUnits'][k]==v for k,v in before['featureWorkUnits'].items() if k!='MV2')
assert all(execution['featurePlans'][k]==v for k,v in before['featurePlans'].items() if k!='motion-quality-review')
write(R/'work/EXECUTION.json',execution)
write(E/'execution-owned-delta.json',{'paths':['featureWorkUnits.MV2','featurePlans.motion-quality-review.lastDisposition'],'ATRecordsAndAcupointPlanUnchanged':True,'nextScheduledTask':mv['nextScheduledTask']})
print('q01-learning-quality passed_model_demo; MV2 remains partial, 4 groups/32 mappings; AT8 not run')
