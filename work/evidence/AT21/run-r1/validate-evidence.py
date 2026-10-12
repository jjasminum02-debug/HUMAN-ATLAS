"""AT21 scoped acceptance, preserving sources, proposals and user WIP."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[4];E=Path(__file__).parent
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=read(E/'baseline.json');owned={'atlas-web/src/viewer/acupoints/schema.ts','atlas-web/src/viewer/acupoints/AcupunctureOverlay.ts','atlas-web/src/viewer/acupoints/AcupointReview.tsx'}
for p,h in {**b['trackedWipHashes'],**{p:h for p,h in b['criticalReadOnlyHashes'].items() if p not in owned}}.items():assert sha(R/p)==h,p
m=read(R/'atlas-data/acupoints/territories/lung-r1/masks.json');assert len(m['masks'])==2 and {x['side'] for x in m['masks']}=={'right','left'}
for z in m['masks']:
 assert z['scope']=='real_input' and z['basisKind']=='surface_learning_connection' and z['kind']=='teaching_region'
 assert len(z['triangleIds'])==351 and z['canonicalBoundaryClaim'] is False and z['author']=='ai'
 assert z['rights']['publicRedistribution']=='held' and z['professorReview']=='not_performed'
for side,controls,loops in [('right',65,[55,6,4]),('left',67,[55,7,5])]:
 d=read(E/f'surface-inspection-{side}-r1.json');assert d['properNativeTriangleIntersections']==0 and d['examinedFaces']==351 and d['loops']==loops and len(d['boundaryNativeSupport'])==controls
 assert len(d['nativeLandmarkReplay'])==4 and d['reflectionUsed'] is False
 for p,h in d['sourceReadHashes'].items():assert sha(R/p)==h
cases=read(E/'responsive-cases-final-r7.json');assert len(cases)==18 and {c['viewport'] for c in cases}=={390,1024,1440}
assert len({c['result']['scene']['root'] for c in cases})==1
extra=read(E/'existing-context-cases-final-r6.json');assert len(extra)==6
final=read(E/'final-code-screen-check-r11.json');assert len(final)==3
for c in cases+extra+final:
 d=c['result'];assert d['review']['actualObservation']['inside'] and not d['review']['observation']['pointOccluded']
 assert len(d['labels'])==1 and not d['labels'][0]['hidden']
 assert d['projection']['selection']=={'kind':'acupoint','code':c['code'],'side':c['side']}
 assert d['territory']['fixtureMasks']==0 and d['territory']['sharedPositionBuffers'] and d['territory']['raycastTargets']==0
 assert d['territory']['depthTest'] and not d['territory']['depthWrite'] and c['code'] in d['card']
 assert (E/(c['file']+'.png')).is_file()
rot=read(E/'rotation-cases-final-r5.json');assert len(rot)==6
for c in rot:
 a,z=c['on'],c['off'];assert a['review']['userMoved'] and not a['review']['autoReturn'] and z['territory']['maskCount']==0
 for key in ['position','target']:assert max(abs(x-y) for x,y in zip(a['territory']['currentCamera'][key],z['territory']['currentCamera'][key]))<1e-10
cy=read(E/'resource-cycles-final-r7.json');assert len(cy['cycles'])==3
for c in cy['cycles']:assert c['on']['review']['cost']['geometryBufferBytes']==187790 and c['off']['review']['cost']['geometryBufferBytes']==180796 and c['off']['territory']['maskCount']==0
assert cy['rapidOff']['territory']['maskCount']==0 and cy['lastSide']['territory']['visibleMasks']==['LU-forearm-right']
ip=read(E/'input-qa-final-r6.json')
for k in ['afterDrag','afterKey']:assert ip[k]['review']['tour']=='paused' and ip[k]['review']['autoReturn'] is False
assert ip['reduced']['review']['reducedMotion'] and not ip['reduced']['scene']['cameraTransition'] and ip['keyboardOff']['territory']['maskCount']==0
q=read(E/'DEV-compositing-revision-qa-r10.json');assert q['cameraError']<1e-10 and q['pointWorldUnchanged'] and q['carrierHashesUnchanged'] and q['maskHashChanged']
assert q['before']['territory']['fixtureMasks']==q['after']['territory']['fixtureMasks']==2
native=read(E/'native-click-qa-r10.json');assert native['before']['scene']['root']==native['after']['scene']['root']
assert native['after']['dataset']['selected']=='ZA-c7010a9-2a02586fddeb2e8d493ae238' and native['after']['review'] is None and native['after']['territory'] is None
point=read(E/'actual-point-click-LU8-right-r10.json');assert point['projection']['selection']=={'kind':'acupoint','code':'LU8','side':'right'} and point['url'].endswith('source=ZA-c7010a9-eb0a993e09d73159468116ce')
ret=read(E/'final-return-r11.json');assert ret['cameraError']<1e-10 and ret['targetError']<1e-10 and ret['before']['scene']['root']==ret['after']['scene']['root']
assert ret['after']['review'] is None and ret['after']['territory'] is None and ret['after']['scene']['cameraOwner'] is None and ret['after']['scene']['registeredUpdates']==0 and ret['after']['scene']['geometryBuffersBytes']==6947334
for k in ['selected','hidden','translucent','nerve','region','pose']:
 if k in ret['before']['dataset']:assert ret['before']['dataset'][k]==ret['after']['dataset'][k]
both=read(E/'final-bilateral-real-22-mask-pair-r11.json');assert both['projection']['localLearnerEligible']==22 and both['territory']['maskCount']==2 and both['territory']['fixtureMasks']==0 and both['review']['cost']['geometryBufferBytes']==367464
assert not read(E/'console-final-r11.json')
assert 'ℹ pass 66' in (E/'tests-final-r7.log').read_text() and 'ℹ fail 0' in (E/'tests-final-r7.log').read_text()
build=read(E/'build-final-r7.json');assert len(build)==13 and all(s['exitCode']==0 for s in build)
lazy=read(E/'lazy-distribution-final-r1.json');assert not lazy['moduleInInitialImports'] and not lazy['dataInInitialImports'] and not lazy['fixtureModuleInProduction'] and not lazy['fixtureIdsInProduction']
out={'task':'AT21','acceptancePassed':True,'realChannels':1,'realPairedPartialTerritories':1,'realSideMasks':2,'realFaces':702,'fullLUTerritories':0,'other13RealMasks':0,'actualBoundaryControls':132,'nativeAnnotationsReplayed':8,'properNativeTriangleIntersections':0,'actualMainMaskScreens':18,'existingContextScreens':6,'finalCodeScreens':3,'actualRotationONOFFPairs':6,'actualCompositingFixtureMasks':2,'fixtureExports':0,'newPointApprovals':0,'unchangedEducationalPositions':22,'preciseLocations':0,'professorReviewedTerritories':0,'publicRedistributionEligibleTerritories':0,'automatedTests':66,'buildSteps':13,'moduleDataLazy':True,'lastRequestWins':True,'resourceReleaseVerified':True,'sameSceneDuringEachFeatureSession':True,'physicalTouchDeviceUsed':False,'cameraReturnError':ret['cameraError'],'targetReturnError':ret['targetError'],'nativeGeometryArrayBytesAfterClose':6947334,'baselineFrozenHashesPreserved':len(b['criticalReadOnlyHashes'])-len(owned),'trackedWipHashesPreserved':45,'AT21RemainingUnits':[],'budgetRaised':False,'cost':read(E/'cost-accounting-final-r1.json'),'nextPlannedUnit':'AT22','autoRunNext':False,'outOfScope':['triangle brush/erase/undo/redo/editor persistence AT22','full LU extent and other13 validated masks','precise cutaneous/jingjin boundaries','professor/textbook/public release approval']}
(E/'validation-final-r1.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('PASS: actual bilateral partial LU masks, shared geometry, source/position/WIP preservation, input/camera/resource/compositing QA,66 tests/13 build steps')
