from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
E = Path(__file__).resolve().parent
def read(name):
    return json.loads((E / name).read_text())
def same_vector(a, b):
    return max(abs(x-y) for x,y in zip(a,b)) < 1e-9

base = read('delivery-baseline.json')
off = read('delivery-off.json')
names = ['delivery-LU1', 'delivery-LU9', 'delivery-LU11', 'delivery-left-LU11']
views = [read(n+'.json') for n in names]
root = base['data-scene']['root']
assert off['data-scene']['root'] == root
for name, d in zip(names, views):
    assert d['canvasCount'] == 1 and d['data-scene']['root'] == root
    assert d['data-acupoint-review']['groupParent'] == 'AnatomySceneRoot'
    p = d['data-acupoint-projection']
    assert p['localLearnerEligible'] == p['fixtureExports'] == 0 and p['authors'] == ['ai']
    selected = d['data-acupoint-review']['selected']
    point = next(p for p in d['data-acupoint-review']['points'] if p['code'] == selected)
    assert point['locationValidation'] == 'unresolved' and point['inFrustum']
    rect = d['data-acupoint-review']['safeViewport']
    assert rect['left'] <= point['screen'][0] <= rect['right']
    assert rect['top'] <= point['screen'][1] <= rect['bottom']
    assert (E / (name+'.png')).stat().st_size > 10000
    assert d['data-dataset']['selected'] == base['data-dataset']['selected']
assert same_vector(base['data-scene']['camera'], off['data-scene']['camera'])
assert same_vector(base['data-scene']['target'], off['data-scene']['target'])
assert not off['data-scene']['cameraTransition'] and off['data-scene']['cameraOwner'] is None
assert off['data-scene']['geometryBuffersBytes'] == base['data-scene']['geometryBuffersBytes']
assert off['data-scene']['registeredUpdates'] == 0 and off['data-acupoint-projection'] is None
assert off['data-acupoint-review'] is None
assert off['data-dataset']['selected'] == base['data-dataset']['selected']
for k in ['hidden','translucent','nerveLayer','motion']:
    assert off['data-dataset'][k] == base['data-dataset'][k]

manual = read('manual-stop.json')['data-acupoint-review']
assert manual['tour'] == 'paused' and manual['userMoved'] and not manual['autoReturn']
closed = read('after-manual-close.json')
assert same_vector(read('manual-stop.json')['data-scene']['camera'], closed['data-scene']['camera'])
assert closed['data-scene']['registeredUpdates'] == 0
rapid = read('rapid-last-right.json')['data-acupoint-projection']
assert rapid['side'] == 'right' and rapid['localLearnerEligible'] == 0
native_pick = read('native-click.json')['data-dataset']['selected']
assert native_pick.startswith('ZA-c7010a9-') and native_pick != base['data-dataset']['selected']
assert len(read('console.json')) == 0

summary = read('compiler-validation.json')
assert summary['passed'] and summary['realInputCount'] == 22 and summary['realInputAccepted'] == 0
assert summary['positiveTechnicalFixtures'] == 4 and summary['fixturesExported'] == 0
assert summary['resume']['second']['executed'] == ['failed-retry']
assert len(summary['resume']['second']['reused']) == 1
preservation = read('preservation.json'); assert preservation['passed']

dist = ROOT / 'atlas-web/dist'
manifest = json.loads((dist / '.vite/manifest.json').read_text())
js = list(dist.rglob('*.js'))
markers = ['explicit-landmarks-2.0','fixture-surface','Synthetic source original','migration-only-v2','work/evidence/AT5','acupointProjection']
found = {m:[str(f.relative_to(dist)) for f in js if m in f.read_text()] for m in markers}
assert not any(found.values())
initial = sum((dist / manifest[k]['file']).stat().st_size for k in ['index.html','src/ui/App.tsx'])
assert initial == 1324012
(E / 'distribution-check.json').write_text(json.dumps({'passed':True,'excludedMarkers':found,'initialJSBytes':initial,
    'initialJSDeltaFromAT4':0,'privateEvidenceNotBundled':True,'additionalProductionGeometryBytes':0},indent=2)+'\n')
cost = views[0]['data-acupoint-review']['cost']
assert cost['geometryBufferBytes'] == 46704 and cost['triangles'] == 3576
assert 20042516 + cost['encodedBytes'] <= 20*1024*1024
assert 897212 + cost['triangles'] <= 1000000
assert base['data-dataset']['bytes'] + cost['geometryBufferBytes'] <= 96*1024*1024
at4 = json.loads((ROOT / 'atlas-data/acupoints/carriers/education-r1/manifest.json').read_text())
report = {'passed':True,'finalRoot':root,'finalScreenCount':4,'sameSceneRendererCamera':True,'localLearnerEligible':0,
    'fixtureExports':0,'exactEntryCameraRestoredAfterSideSwitch':True,'selectionLayersPreserved':True,
    'gpuBuffersReturnedToBaseline':True,'registeredUpdatesAfterOff':0,'manualStopsTourAndReturn':True,
    'nativePickPreserved':True,'finalConsoleWarningsErrors':0,'viewportScope':'1280x720 existing desktop; no responsive UI change',
    'staticOwnerFreeMotionGuard':'automated common-overlay/resource override test; no claim of new motion animation visual QA',
    'carrierReuse':{'registeredChunks':len(at4['chunks']),'bytes':at4['totalBytes'],'triangles':at4['totalTriangles'],'newAT5GeometryBytes':0},
    'existingReviewCost':cost,'AT5AdditionalGPUBytes':0,'initialJSBytes':initial,
    'preFixCameraFailureRetained':'pre-camera-fix-delivery-off.json; camera-regression.txt',
    'earlierInteractionRoot':closed['data-scene']['root'],'allLocationPrecision':'unresolved for actual LU; no exact skin claim'}
(E / 'runtime-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':True,'root':root,'screens':4,'localLearnerEligible':0,'exactCameraReturn':True}))
