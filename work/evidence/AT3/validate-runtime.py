"""Read-only assertions over actual browser captures; no UI state fabrication."""
from pathlib import Path
import json
E=Path(__file__).resolve().parent
read=lambda name:json.loads((E/name).read_text())
geometry=read('geometry-validation.json');assert geometry['status']=='passed'
pair=read('off-on-state.json');on,off,reopened=pair
for state in pair:
    assert state['canvasCount']==1 and state['scene']['root']==on['scene']['root']
    assert state['scene']['camera']==on['scene']['camera'] and state['scene']['target']==on['scene']['target']
    assert state['dataset']==on['dataset']
for state in [on,reopened]:
    assert state['sample']['meshCount']==11 and state['sample']['parent']=='AnatomySceneRoot'
    for key,delta in [('calls',11),('triangles',33414),('geometries',11),('geometryBuffersBytes',631620),('registeredUpdates',1)]:
        assert state['scene'][key]-off['scene'][key]==delta,(key,state['step'])
assert off['sample'] is None
views=read('four-views.json');assert len(views)==8
for view in ['front','right','back','left']:
    a=next(s for s in views if s['view']==view and s['mode']=='proposal')
    b=next(s for s in views if s['view']==view and s['mode']=='native')
    assert a['scene']['camera']==b['scene']['camera'] or max(abs(x-y) for x,y in zip(a['scene']['camera'],b['scene']['camera']))<1e-10
    assert a['dataset']==b['dataset'] and a['scene']['root']==b['scene']['root']
    assert a['scene']['geometryBuffersBytes']==b['scene']['geometryBuffersBytes']
    assert a['sample']['seamVerticesWithSharedNormals']==604
    assert all(s['inFrustum'] for s in a['sample']['samples']+b['sample']['samples'])
    assert a['sample']['cost']['triangles']==33414
for s in read('toggle-cycles.json'):
    assert s['scene']['geometries']==(409 if s['on'] else 398)
    assert s['scene']['geometryBuffersBytes']==(7578954 if s['on'] else 6947334)
    assert s['scene']['registeredUpdates']==int(s['on'])
    assert s['scene']['shaderPrograms']==(3 if s['on'] else 2)
for s in read('layer-off-preservation.json'):assert s['bones']==s['muscles']=='false'
rapid=read('rapid-transition.json')
assert [c['id'] for c in rapid[0]['sample']['chunks']]==['leg-right-0','leg-right-1','leg-left-0','leg-left-1']
assert rapid[1]['sample'] is None and rapid[1]['scene']['registeredUpdates']==0
for name,word in [('anatomy-click.json','가쪽넓은근'),('bone-click.json','대퇴골')]:
    s=read(name);assert s['before']['sample']['meshCount']==11 and s['after']['sample'] is None
    assert s['after']['dataset']['selected']!=s['before']['dataset']['selected'] and word in s['card']
    assert s['after']['scene']['root']==s['before']['scene']['root']
assert read('motion-before.json')['sample']['meshCount']==11
for s in read('motion-guard.json'):assert s['sample'] is None and s['dataset']['motion'] is not None
final=read('delivery-runtime.json');assert final['dataset']['motion'] is None and final['sample']['meshCount']==11
assert final['dataset']['selected']=='ZA-c7010a9-eb0a993e09d73159468116ce'
assert read('console.json')==[] and read('distribution-check.json')['passed']
out={'passed':True,'oneSceneRendererCamera':True,'actualViews':4,'proposalNativePairs':4,
  'nativeLandmarkExtremaChecked':len(geometry['landmarks']),'gpuBufferDeltaBytes':631620,'triangleDelta':33414,'drawCallDelta':11,
  'exactOffOnCameraSelectionPreservation':True,'layerOffPreserved':True,'toggleCycles':3,'noResidualGeometry':True,
  'rapidLastRequest':'leg bilateral','nativeMuscleAndBoneClicks':True,'motionStartStopsStaticCarrier':True,
  'releasedMotionCameraGuard':'automated contract case; actual motion retained owner during keyboard orbit',
  'consoleWarningsErrors':0,'clinicalPointsApproved':0,'skinScanAccuracy':'unresolved'}
(E/'runtime-validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out,ensure_ascii=False))
