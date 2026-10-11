"""Assert actual browser artifacts; never synthesize UI states."""
from pathlib import Path
import hashlib,json
E=Path(__file__).resolve().parent
read=lambda n:json.loads((E/(n+'.json')).read_text())
g=read('geometry-validation');assert g['status']=='passed'
root=read('cycle-1-off')['scene']['root'];cycles=[]
for i in range(1,4):
    on,off=read(f'cycle-{i}-on'),read(f'cycle-{i}-off')
    for s in [on,off]:
        assert s['canvasCount']==1 and s['scene']['root']==root
        assert s['scene']['camera']==on['scene']['camera'] and s['scene']['target']==on['scene']['target']
        assert s['dataset']==on['dataset']
    assert on['sample']['meshCount']==83 and on['sample']['parent']=='AnatomySceneRoot'
    assert off['sample'] is None
    for k,v in [('geometryBuffersBytes',813096),('geometries',83),('calls',83),('triangles',40520),('registeredUpdates',1)]:
        assert on['scene'][k]-off['scene'][k]==v,(i,k)
    assert off['scene']['geometryBuffersBytes']==6947334 and off['scene']['registeredUpdates']==0
    cycles.extend([on,off])
pairs=[f'head-{v}' for v in ['front','right','back','left']]
pairs += [f'hand-{s}-{v}' for s in ['left','right'] for v in ['palmar','dorsal']]
pairs += [f'foot-{s}-{v}' for s in ['left','right'] for v in ['dorsal','plantar']]
pairs += ['oral-access','perineum-inferior','perineum-isolated']
views=[]
for name in pairs:
    a,b=read(name+'-proposal'),read(name+'-native')
    assert a['scene']['root']==b['scene']['root']==root and a['canvasCount']==b['canvasCount']==1
    assert max(abs(x-y) for x,y in zip(a['scene']['camera'],b['scene']['camera']))<1e-10,name
    assert a['scene']['target']==b['scene']['target'] and a['dataset']==b['dataset'],name
    assert a['sample']['mode']=='authored_teaching_surface' and b['sample']['mode']=='native_surface_samples',name
    views.append({'name':name,'camera':a['scene']['camera'],'target':a['scene']['target'],'chunks':a['sample']['meshCount'],
      'acceptedAcupoints':0,'png':name+'-proposal.png','nativePng':name+'-native.png','proposalNativeSameCamera':True,
      'occlusionPolicy':'Actual PNG inspected; projected samples are not an occlusion or skin-accuracy test'})
for name in ['nails-left-hand-dorsal','nails-right-hand-dorsal','nails-left-foot-dorsal','nails-right-foot-dorsal','oral-closed-proposal','perineum-default-proposal']:
    s=read(name);assert s['scene']['root']==root and s['sample']['acceptedAcupoints']==0
    views.append({'name':name,'camera':s['scene']['camera'],'target':s['scene']['target'],'chunks':s['sample']['meshCount'],'png':name+'.png','acceptedAcupoints':0})
layers=read('layer-off-preservation')
assert len(layers)==3 and all(s['buttons']['뼈']==s['buttons']['근육']=='false' for s in layers)
rapid=read('rapid-last-foot');assert rapid['sample']['meshCount']==12
assert all(c['id'].startswith(('foot-','toe-')) for c in rapid['sample']['chunks'])
cancel=read('rapid-cancel-off');assert cancel['sample'] is None and cancel['scene']['registeredUpdates']==0
for name in ['motion-guard','motion-manual-guard']:
    s=read(name);assert s['sample'] is None and s['dataset']['motion'] is not None
manual,closed=read('manual-fit-takeover'),read('manual-fit-closed')
assert manual['scene']['cameraOwner'] is None and not manual['scene']['cameraTransition']
assert manual['scene']['camera']==closed['scene']['camera'] and manual['scene']['target']==closed['scene']['target']
click=read('native-click')
assert click['before']['sample'] is not None and click['after']['sample'] is None
assert click['before']['dataset']['selected']!=click['after']['dataset']['selected']
assert click['before']['scene']['root']==click['after']['scene']['root']
assert click['before']['canvasCount']==click['after']['canvasCount']==1
assert '대흉근 흉늑부' in click['card']
assert read('console')==[] and read('distribution-check')['passed']
final=read('delivery-runtime');assert final['dataset']['selected']=='ZA-c7010a9-eb0a993e09d73159468116ce'
assert final['sample']['meshCount']==83 and final['dataset']['motion'] is None
R=E.parents[2];manifest=json.loads((R/'atlas-data/acupoints/carriers/education-r1/manifest.json').read_text());a=manifest['accessManifest'];p=R/'atlas-data/acupoints/carriers/education-r1'/a['file']
assert len(p.read_bytes())==a['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256']
out={'passed':True,'oneSceneRendererCamera':True,'root':root,'coldRecheckRoot':click['before']['scene']['root'],'actualAccessViewCount':len(views),'exactProposalNativePairs':len(pairs),
 'nativeLandmarkExtremaChecked':len(g['landmarks']),'newReferenceVerticesReplayed':g['replayedChunkVertices'],
 'runtimeWholeCarrierBufferDeltaBytes':813096,'runtimeWholeCarrierDrawCallDelta':83,'runtimeWholeCarrierTriangleDelta':40520,
 'registeredCarrierChunks':83,'newCarrierChunks':72,'toggleCycles':3,'noResidualCarrierGeometry':True,'cameraSelectionPreserved':True,
 'manualFitTakeoverStopsAndNoReturn':True,'layerOffPreserved':True,'rapidLastRequest':'foot bilateral','loadingCloseCancelled':True,
 'nativePickFlowPreserved':True,'motionStopsStaticCarrier':True,'motionOverridesGuard':'additional automated owner-free deformed-state contract case',
 'consoleWarningsErrors':0,'productionInitialJSBytes':1324012,'acceptedAcupoints':0,'wholeBodySkinComplete':False,'professorReview':'not_performed'}
(E/'actual-access-views.json').write_text(json.dumps(views,ensure_ascii=False,indent=2)+'\n')
(E/'runtime-validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out,ensure_ascii=False))
