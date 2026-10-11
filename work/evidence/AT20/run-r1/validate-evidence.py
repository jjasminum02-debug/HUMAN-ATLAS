"""Read-only AT20 acceptance audit; no source writes, approvals or mask production."""
from pathlib import Path
import hashlib,json,subprocess
R=Path(__file__).resolve().parents[4];E=Path(__file__).parent
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
defs=read(R/'atlas-data/acupoints/territories/AT20-r1/definitions-r1.json')
channels={c['code'] for c in read(R/'atlas-data/acupoints/who-361-catalog.json')['channels']}
assert len(defs['definitions'])==14 and {d['channel'] for d in defs['definitions']}==channels
sources=read(E/'source-register-r1.json')['sources'];sourceIds={s['id'] for s in sources}
for d in defs['definitions']:
 assert d['canonicalBoundaryClaim'] is False and d['interpretation']=='ai_proposal' and d['author']=='ai' and d['finalMasks']==0
 assert d['uncertainties'] and d['sourceRelations'] and all(s['sourceId'] in sourceIds for s in d['sourceRelations'])
 assert set(d['viewDrafts'])=={'anterior','posterior','lateral'}
 assert all(v['sourceBoundary'] is False and v['boundaryRule'] for v in d['viewDrafts'].values())
 assert {v['kind'] for v in d['types'].values()}=={'surface_learning_connection','sinew_projection','cutaneous','professor_interpretation'}
 assert d['professorReview']=='not_performed' and d['publicRedistribution']=='held'
 if d['channel'] in ['CV','GV']:assert d['types']['sinew']['status']=='not_applicable' and d['sideRule']=='midline'
 else:assert d['types']['sinew']['status']=='incipit_only_no_mask' and d['sideRule']=='independent_bilateral_annotations'
assert sum(d['status']=='boundary_input_ready_partial' for d in defs['definitions'])==1
assert defs['finalMaskCount']==0 and all(s['definesAreaBoundary'] is False for s in sources)
surface=read(E/'surface-inspection-r1.json');assert set(surface['linkedPointsCovered'])=={'LU6','LU7','LU8'}
assert surface['examinedFaces']==351 and surface['loops']==[55,6,4] and len(surface['boundaryNativeSupport'])==65
assert surface['properNativeTriangleIntersections']==0 and len(surface['nativeLandmarkReplay'])==4
for p,h in surface['sourceReadHashes'].items():assert sha(R/p)==h
base=read(E/'baseline.json')
for p,h in {**base['trackedWipHashes'],**base['criticalReadOnlyHashes']}.items():assert sha(R/p)==h,p
positions=read(R/'atlas-data/acupoints/learner/lung-r7.json');assert sum(len(g['instances']) for g in positions['projections'])==22
assert positions['precisionCounts']=={'precise':0,'educationalApproximation':22,'unresolved':0}
cases=read(E/'actual-screen-cases-final-r3.json');assert len(cases)==9
assert {c['viewport'] for c in cases}=={390,1024,1440} and {c['code'] for c in cases}=={'LU6','LU7','LU8'}
assert len({c['result']['scene']['root'] for c in cases})==1
for c in cases:
 d=c['result'];assert d['review']['actualObservation']['inside'] and not d['review']['observation']['pointOccluded']
 assert d['projection']['selection']=={'code':c['code'],'kind':'acupoint','side':'right'}
 assert len(d['labels'])==1 and d['labels'][0]['hidden'] is False and c['code'] in d['card']
 assert .5<d['review']['actualObservation']['occupancy']<.7
 assert max(abs(a-b) for a,b in zip(d['scene']['camera'],d['review']['observation']['cameraTarget']['position']))<1e-10
 assert d['scene']['renderer']=='anatomy-'+d['scene']['root'] and d['projection']['fixtureExports']==0
 assert (E/(c['file']+'.png')).is_file()
before=read(E/'browser-before-r1.json');after=read(E/'browser-restored-r1.json')
assert before['scene']['root']==after['scene']['root'] and before['url']==after['url']
for k in ['camera','target','geometryBuffersBytes']:assert before['scene'][k]==after['scene'][k]
for k in ['selected','hidden','translucent','nerve','region','pose']:
 if k in before['dataset']:assert before['dataset'][k]==after['dataset'][k]
assert after['review'] is None and after['scene']['cameraOwner'] is None and after['scene']['registeredUpdates']==0
assert not read(E/'console-final-r1.json')
assert 'ℹ pass 20' in (E/'tests-final-r2.log').read_text() and 'ℹ fail 0' in (E/'tests-final-r2.log').read_text()
assert not (E/'typecheck-final-r1.log').read_text().strip()
assert (E/'boundary-native-three-views-r1.png').is_file()
# This module/data must remain offline; no app import or runtime data routing was added.
imports=subprocess.run(['rg','-n','territoryBoundary|territories/AT20-r1','atlas-web/src','atlas-web/scripts','atlas-web/plugins'],cwd=R,capture_output=True,text=True).stdout.splitlines()
assert all('territoryBoundary.ts:' in l or 'territoryBoundary.test.ts:' in l for l in imports),imports
out={'task':'AT20','acceptancePassed':True,'AT6AT7ConditionalGate':'passed_current_evidence','definitions':14,'maskReadyPartialLUTerritories':1,'otherEvidenceLedgers':13,'sinewIncipits':12,'CVGVAddedJingjin':0,'finalMasks':0,'canonicalBoundariesConfirmed':0,'nativeLandmarks':4,'actualBoundaryControls':65,'outerLoops':1,'holeLoops':2,'replayedEnclosedFaces':351,'properNativeIntersections':0,'actualScreenCases':9,'screenViewports':[390,1024,1440],'screenCodes':['LU6','LU7','LU8'],'sceneRoot':after['scene']['root'],'cameraReturnExact':True,'layerSelectionPreserved':True,'newPointApprovals':0,'unchangedEducationalPoints':22,'preciseSkinPoints':0,'fixtureExports':0,'professorReviewedTerritories':0,'publicRedistributionEligibleTerritories':0,'userTextbookAvailable':False,'automatedTests':20,'typecheck':'passed','fullHistoricalSuiteRepeated':False,'cost':surface['graphicsCost'],'budgetsChanged':False,'baselineWipPreserved':len(base['trackedWipHashes']),'frozenFileHashesPreserved':len(base['criticalReadOnlyHashes']),'sourceDownloads':0,'runtimeRendererChanges':0,'UIChanges':0,'AT20RemainingUnits':[],'outsideScope':['remaining LU region controls','13 final masks','complete 12 jingjin branch/muscle correspondence','precise cutaneous boundaries','professor/textbook interpretation','AT21 renderer integration/depth/alpha QA'],'nextPlannedUnit':'AT21','autoRunNext':False}
(E/'validation-r1.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('PASS: 14 independent territory ledgers, executable LU contour351/65/3, 9 actual views, 20 tests, frozen source/WIP, no mask or approval exports')
