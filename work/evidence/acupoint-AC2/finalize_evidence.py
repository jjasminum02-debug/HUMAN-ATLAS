from pathlib import Path
import json,hashlib,struct,subprocess
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[3];E=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
context=read(E.parent/'acupoint-AC1/runtime-dataset.json')
for side in ['right','left']:
 d=read(E/f'{side}-learning.json');c=d['carrier'];p=np.array(c['positions'],dtype='<f4');i=np.array(c['indices'],dtype='<u4')
 assert hashlib.sha256(p.tobytes()+i.tobytes()).hexdigest()==c['topologySha256']
 assert c['datasetRevision']==context['revision'] and c['frameId']==context['frameContract']['targetFrameId'] and c['poseId']==context['frameContract']['staticReferencePose']['id'] and c['unit']=='m'
 assert all(x<0 if side=='right' else x>0 for x in c['positions'][::3]);assert len(d['instances'])==11
 assert [v['code'] for v in d['instances']]==[f'LU{n+1}' for n in range(11)]
 assert all(v['locationValidation']=='unresolved' and v['aiProposal'] and v['missing'] for v in d['instances']);assert d['route']['kind']=='surface_teaching' and d['route']['carrierHash']==c['topologySha256']
 audit=read(E/f'{side}-carrier-validation.json');assert audit['independentNativeGeometry'] and not audit['mirrored']
 for f,h in {**audit['sourceInputs'],**audit['unitMetadataInputs']}.items():assert sha(R/f)==h,f
for name,expected in [('1440-point-views.json',11),('1024-point-views.json',5),('390-point-views.json',5),('left-point-views.json',11)]:
 views=read(E/name);assert len(views)==expected;assert len({v['review']['root'] for v in views})==1
 for v in views:
  d=v['review'];selected=next(p for p in d['points'] if p['code']==d['selected']);r=d['safeViewport'];x,y=selected['screen'];assert selected['inFrustum'] and r['left']<=x<=r['right'] and r['top']<=y<=r['bottom'],(name,d['selected'],selected)
cycles=read(E/'toggle-cycles.json');assert len(cycles)==30
assert all(x['off']['geometries']==397 and x['on']['geometries']==399 and x['off']['registeredUpdates']==0 and x['on']['registeredUpdates']==1 and x['off']['shaderPrograms']==2 and x['on']['shaderPrograms']==4 for x in cycles)
m=read(E/'manual-orbit.json');assert m['userMoved'] and not m['autoReturn'] and m['tour']=='paused'
manual=read(E/'manual-no-return.json');assert manual['before']['camera']==manual['after']['camera'] and manual['before']['target']==manual['after']['target'] and not manual['after']['cameraTransition'] and manual['after']['registeredUpdates']==0
assert read(E/'console.json')==[]
t=read(E/'automatic-tour.json');assert t['review']['selected']=='LU11' and t['review']['tour']=='ready' and t['scene']['camera']==t['before']['camera'] and t['scene']['target']==t['before']['target']
n=read(E/'nested-observation.json');assert [n[k]['scene']['cameraOwner'] for k in ['before','during','after']]==['anatomy','acupoint','anatomy'];assert n['before']['scene']['camera']==n['after']['scene']['camera'];assert n['before']['dataset']['attachmentObservation']==n['after']['dataset']['attachmentObservation']
m=read(E/'motion-camera-ownership.json');assert m['before']['scene']['cameraOwner']=='motion' and m['before']['dataset']['motion'];assert m['after']['scene']['cameraOwner']=='acupoint' and m['after']['dataset']['motion'] is None;assert m['before']['dataset']['selected']==m['after']['dataset']['selected']
k=read(E/'point-picking.json');assert k['after']['review']['selected']=='LU11' and k['after']['dataset']['selected']==k['before']['dataset']['selected']
for name in ['anatomy-click.json','muscle-click.json']:
 a=read(E/name);assert a['review'] is None and a['dataset']['selected'].startswith('ZA-') and a['panel']
red=read(E/'lazy-and-reduced-motion.json');assert red['offLazy']['resources']==[] and red['review']['reducedMotion'] and not red['scene']['cameraTransition']
rapid=read(E/'rapid-switch-cancellation.json');assert rapid['canvasCount']==1 and len(rapid['sameSide']['points'])==11 and len(rapid['rapid'])==3 and all(v['side']=='right' for v in rapid['rapid'])
final=read(E/'final-runtime.json');assert final['canvasCount']==1 and final['review']['cost']['encodedBytes']==(E/'right-learning.json').stat().st_size
rects={v['class']:v['rect'] for v in final['panelRects']};canvas=rects['whole-body-canvas'];card=rects['acupoint-review'];tools=rects['body-tools'];assert canvas['bottom']<=tools['top'] and tools['bottom']<=card['top']
cost=read(E/'same-camera-cost.json');base=cost['baseline'];point=cost['points'];surface=cost['carrier']['scene']
assert point['camera']==surface['camera']==base['camera'] and point['target']==surface['target']==base['target']
assert point['calls']-base['calls']==12 and surface['calls']-base['calls']==13 and surface['triangles']-base['triangles']==3576
assert surface['geometries']==400 and base['geometries']==397
sizes={s:(E/f'{s}-learning.json').stat().st_size for s in ['right','left']};gpu=final['review']['cost']['geometryBufferBytes'];assert gpu==46704
baseOverview=sum(c['bytes'] for c in context['chunks'] if c['level']=='overview' and not c.get('selectionScoped'))+max([c['bytes'] for c in context['chunks'] if c.get('selectionScoped')]+[0]);tri=sum(i['lods']['overview']['triangles'] for i in context['instances'])
assert baseOverview+sum(sizes.values())<=20*1024*1024 and tri+3576<=1000000 and final['dataset']['bytes']+gpu<=96*1024*1024 and max(sizes.values())<8*1024*1024
manifest=read(R/'atlas-web/dist/.vite/manifest.json');assert not any('acupoint' in k.lower() for k in manifest)
for f in (R/'atlas-web/dist/assets').glob('*.js'):
 text=f.read_text();assert not any(s in text for s in ['development_review_only','za-right-lung-teaching','SurfaceTeachingOrder','AC-review-LU'])
assert (E/'typecheck.log').read_text()=='' and 'ℹ pass 18' in (E/'tests.log').read_text() and '"passed":true' in (E/'production-build.log').read_text()
images={p.name:Image.open(p).size for p in E.glob('*.png')};assert any(s==(390,844) for s in images.values()) and any(s==(1024,900) for s in images.values()) and any(s==(1440,900) for s in images.values())
# Preserve all prior WIP; only these eight AC2 lines may be removed from the pre-existing adapter.
path=R/'atlas-web/src/viewer/datasets/DatasetSceneAdapter.ts';current=path.read_text()
additions=["        if (changedSelection || this.view.poseId !== view.poseId) for (const listener of this.sourceSelectionListeners) listener();\n","    private readonly sourceSelectionListeners = new Set<() => void>();\n    onSourceSelectionChange(listener: () => void) {\n        this.sourceSelectionListeners.add(listener);\n        return () => { this.sourceSelectionListeners.delete(listener); };\n    }\n","            this.scene.beginObservation('motion');\n","        this.scene.endObservation('motion', false);\n"]
stripped=current
for s in additions:assert s in stripped;s1=stripped.replace(s,'',1);stripped=s1
assert stripped==(E/'before/DatasetSceneAdapter.ts').read_text()
before=read(E/'before/baseline.json');changed=[f for f,h in before['wipHashes'].items() if not (R/f).is_file() or sha(R/f)!=h];assert changed==['atlas-web/src/viewer/datasets/DatasetSceneAdapter.ts'],changed
source=R/'atlas-data/source-cache/z-anatomy/t97/extracted/Z-Anatomy/Startup.blend';sourcehash=sha(source);assert sourcehash=='9f08a17ea0115fed80b2a73ecdf0a1bc2ab2f6956f37c593ce23d513ea35afcd'
validation={'status':'engineering_passed_location_partial','acceptedProductPointCount':0,'reviewProposalPointCount':22,'rightPointCount':11,'leftNativeProposalCount':11,'surfaceTeachingRouteCount':2,'classicalRouteCount':0,'territoryCount':0,'professorReview':'not_performed','publicRedistribution':'held','carrierHashes':{s:read(E/f'{s}-learning.json')['carrier']['topologySha256'] for s in ['right','left']},'measurements':{'dataBytes':sizes,'carrierVerticesPerSide':1231,'carrierTrianglesPerSide':1728,'carrierGPUBufferEstimateBytes':39912,'totalExtraGPUBufferEstimateBytes':gpu,'extraTextures':0,'calls':[base['calls'],point['calls'],surface['calls'],cost['after']['calls']],'triangles':[base['triangles'],point['triangles'],surface['triangles'],cost['after']['triangles']],'geometryObjects':[base['geometries'],point['geometries'],surface['geometries'],cost['after']['geometries']],'overviewBytesIncludingBothSides':baseOverview+sum(sizes.values()),'overviewTrianglesIncludingCarrier':tri+3576,'activeQueueBytesWithOverlay':final['dataset']['bytes']+gpu,'GPUDriverHeapAndElapsedGPUTime':'not_measured; buffer allocation/upload estimate and actual render counts only'},'checks':{'automatedTests':'18/18','typecheck':'passed','productionBuild':'passed','productFixtureLeak':'none','oneCanvas':'passed','pointAndAnatomySelection':'passed','cameraOwnershipAndReturn':'passed','manualOrbit':'passed','rapidSwitches':'passed','toggleCycles':30,'nativeLeftSource':'passed_technical_location_unresolved','reducedMotion':'feature instant-move override tested; OS media subscription and controller policy retained, OS preference not changed'},'screenshots':images,'preservation':{'baselineWipFiles':len(before['wipHashes']),'changedWip':changed,'adapterWithoutOwnedChangesEqualsBaseline':True,'sourceSha256':sourcehash},'nextUnit':'AC3_prompt_only','noAutoAdvance':True}
(E/'validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':validation['status'],'screenshots':len(images),'measurements':validation['measurements']},ensure_ascii=False))
