"""Independent read-only native triangle replay and AT2 acceptance checks."""
from pathlib import Path
from collections import Counter
import ast, hashlib, json, struct, subprocess
import numpy as np

R = Path(__file__).resolve().parents[3]
E = Path(__file__).resolve().parent
A = R / 'work/evidence/acupoint-AC1'
read = lambda p: json.loads(p.read_text())
sha = lambda b: hashlib.sha256(b).hexdigest()
sample_path = R / 'atlas-data/acupoints/carriers/za-thigh-sample.json'
sample = read(sample_path)
audit = read(E / 'source-sample.json')
c = sample['carrier']
p = np.array(c['positions'], dtype='<f4').reshape(-1, 3)
ref = np.array(sample['referencePositions'], dtype='<f4').reshape(-1, 3)
idx = np.array(c['indices'], dtype='<u4').reshape(-1, 3)
assert sha(p.tobytes()+idx.tobytes()) == c['topologySha256'] == audit['carrierHash']
assert sha(ref.tobytes()+idx.tobytes()) == sample['referenceHash'] == audit['referenceHash']
assert len(p) == 1024 and len(idx) == 1920 and np.all(p[:, 0] < 0)
assert c['side'] == 'right' and c['kind'] == 'authored_teaching_surface'
assert c['precision'] == 'coarse_not_skin' and sample['acceptedAcupoints'] == 0
assert sample['usage'] == 'development_review_only'
assert np.isfinite(p).all() and np.isfinite(ref).all()
assert idx.min() == 0 and idx.max() == len(p)-1
assert np.max(np.abs(np.linalg.norm(p-ref, axis=1)-.006)) < 1e-6
faces = p[idx]
normal = np.cross(faces[:, 1]-faces[:, 0], faces[:, 2]-faces[:, 0])
assert np.min(np.linalg.norm(normal, axis=1)) > 1e-8
edges = Counter(tuple(sorted(e)) for t in idx.tolist() for e in ((t[0],t[1]),(t[1],t[2]),(t[2],t[0])))
assert set(edges.values()) == {1,2}
boundary = [e for e,n in edges.items() if n == 1]
assert len(boundary) == 128
assert all((a//64 == b//64 == 0) or (a//64 == b//64 == 15) for a,b in boundary)
adj = [set() for _ in p]
for a,b in edges: adj[a].add(b); adj[b].add(a)
seen, todo = set(), [0]
while todo:
    n=todo.pop()
    if n not in seen: seen.add(n); todo.extend(adj[n]-seen)
assert len(seen) == 1024
assert len(p)-len(edges)+len(idx) == 0  # single open annulus; angular seam closed

dataset = read(A/'runtime-dataset.json')
rows = {v['sourceKey']:v for v in read(A/'runtime-integration.json')['objects']}
cache = R/'atlas-data/source-cache/datasets/za'
inputs, meshes = {}, {}
reader_path = A/'build_carrier.py'
assert sha(reader_path.read_bytes()) == audit['reusedReaderFileSha256']
tree = ast.parse(reader_path.read_text())
reader = next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name == 'world')
exec(compile(ast.Module(body=[reader],type_ignores=[]),str(reader_path),'exec'),globals())
for path,h in {**audit['sourceInputs'],**audit['unitMetadataInputs']}.items():
    assert sha((R/path).read_bytes()) == h, path
assert sha((A/'source-probe.json').read_bytes()) == audit['predecessorProbeSha256']
assert c['datasetRevision'] == dataset['revision']
assert c['frameId'] == dataset['frameContract']['targetFrameId']
assert c['poseId'] == dataset['frameContract']['staticReferencePose']['id'] and c['unit'] == dataset['unit'] == 'm'
hits=read(E/'native-ray-hits.json'); assert len(hits) == 1024
errors=[]
for i,h in enumerate(hits):
    assert h['sample'] == i and rows[h['sourceKey']]['side'] == 'right'
    v,t=world(h['sourceKey']); b=np.array(h['barycentric'])
    assert abs(b.sum()-1) < 1e-9 and b.min() >= -1e-9
    reconstructed=b@v[t[h['triangle']]]
    errors.append(float(np.linalg.norm(reconstructed-ref[i])))
assert max(errors) < 1e-6
for g in audit['nativeGeometry']:
    v,t=world(g['sourceKey'])
    assert np.max(np.abs(np.array([v.min(axis=0),v.max(axis=0)])-np.array(rows[g['sourceKey']]['bounds']))) < .0001
    u=read(cache/'units'/f"{g['sourceKey']}.json")
    assert u['geometrySpace'] == 'source_local' and not u['transformAppliedToGeometry']
    assert g['matrixAppliedOnce'] and len(v) == g['vertices'] and len(t) == g['triangles']
assert inputs == audit['sourceInputs']
assert audit['method']['nearestFallbackCount'] == audit['method']['missingRayCount'] == 0
assert audit['quality']['checkedTriangleCentroids'] == 1920
assert audit['quality']['centroidNativeClearanceMinMetres'] > 0
assert audit['quality']['allNormalsOutward'] and not audit['method']['surfaceThicknessClaim']

views=read(E/'surface-views.json')
assert {v['view'] for v in views} == {'front_oblique','right_lateral','back_oblique'}
assert len({v['scene']['root'] for v in views}) == 1
for v in views:
    s=v['sample']
    assert v['canvasCount'] == 1 and s['root'] == v['scene']['root']
    assert s['parent'] == 'AnatomySceneRoot' and s['meshCount'] == 1
    assert s['topologyHash'] == c['topologySha256'] and s['pose'] == c['poseId']
    assert s['frame'] == c['frameId'] and s['cameraOwner'] is None
    assert all(x['inFrustum'] for x in s['samples']) and len(s['samples']) == 12
cost=read(E/'same-camera-cost.json')
b,on,reference,off=[cost[k] for k in ['before','on','reference','after']]
for v in [on,reference,off]:
    assert v['canvasCount'] == 1 and v['scene']['root'] == b['scene']['root']
    assert v['scene']['camera'] == b['scene']['camera'] and v['scene']['target'] == b['scene']['target']
    assert v['dataset'] == b['dataset']
assert on['scene']['calls']-b['scene']['calls'] == 1
assert on['scene']['triangles']-b['scene']['triangles'] == 1920
assert on['scene']['geometryBuffersBytes']-b['scene']['geometryBuffersBytes'] == 36096
assert on['scene']['geometries']-b['scene']['geometries'] == 1
for k in ['calls','triangles','geometryBuffersBytes','geometries']:
    assert reference['scene'][k] == on['scene'][k]
    assert off['scene'][k] == b['scene'][k]
assert off['sample'] is None and off['scene']['registeredUpdates'] == 0
assert reference['sample']['topologyHash'] == sample['referenceHash']
cycles=read(E/'toggle-cycles.json'); assert len(cycles) == 5
assert all(v['on']['geometries'] == 399 and v['off']['geometries'] == 398 and v['off']['sample'] is None and v['off']['updates'] == 0 for v in cycles)
layers=read(E/'layer-off-preservation.json')
for k in ['on','after']:
    assert layers[k]['layers'] == layers['before']['layers']
    assert layers[k]['runtime']['scene']['camera'] == layers['before']['runtime']['scene']['camera']
    assert layers[k]['runtime']['dataset'] == layers['before']['runtime']['dataset']
click=read(E/'anatomy-click.json')
assert click['before']['sample'] and click['after']['sample'] is None
assert click['after']['dataset']['selected'] == 'ZA-c7010a9-da17fca9886014ed6ca805ee'
assert '대퇴이두근' in click['panel']
initial=read(E/'final-before-display.json'); final=read(E/'final-runtime.json')
assert not initial['loading']['requested'] and initial['loading']['resources'] == []
assert final['sample']['topologyHash'] == c['topologySha256']
assert final['canvasCount'] == 1 and final['dataset']['motion'] is None
assert read(E/'console.json') == []
tests=(E/'tests.log').read_text()
assert 'pass 9' in tests and 'fail 0' in tests
assert not (E/'typecheck.log').read_text().strip()
assert 'built in' in (E/'production-build.log').read_text()
assert read(E/'lazy-build.log')['passed']
manifest=read(R/'atlas-web/dist/.vite/manifest.json')
assert not any('CarrierSample' in k or 'za-thigh-sample' in k for k in manifest)
leaks=[]
for f in (R/'atlas-web/dist/assets').glob('*.js'):
    if any(x in f.read_text() for x in ['za-right-middle-thigh-teaching-sample',c['topologySha256'],'native-ray-hits','CarrierSurfaceSample']):leaks.append(str(f.relative_to(R)))
assert not leaks, leaks
overview=sum(v['bytes'] for v in dataset['chunks'] if v['level']=='overview' and not v.get('selectionScoped'))+max([0]+[v['bytes'] for v in dataset['chunks'] if v.get('selectionScoped')])
overview_triangles=sum(v['lods']['overview']['triangles'] for v in dataset['instances'])
assert overview+sample_path.stat().st_size <= 20*1024*1024
assert overview_triangles+1920 <= 1_000_000
assert b['dataset']['bytes']+36096 <= 96*1024*1024
baseline=read(E/'preservation-before.json')
changed=[]
for path,h in baseline['wipHashes'].items():
    f=R/path
    if not f.is_file() or sha(f.read_bytes()) != h:changed.append(path)
assert not changed, changed
source=R/'atlas-data/source-cache/z-anatomy/t97/extracted/Z-Anatomy/Startup.blend'
assert sha(source.read_bytes()) == audit['sourceSha256']
out={'status':'passed_for_AT2_path_and_bounded_sample','fullBodySkinComplete':False,'mucosaComplete':False,
     'acceptedProductInstances':0,'anchorInstancesCreated':0,'nativeSamplesReplayed':1024,
     'nativeReplayMaxErrorMetres':max(errors),'vertices':1024,'triangles':1920,'connectedComponents':1,
     'boundaryEdges':128,'angularSeamClosed':True,'centroidChecksFromBuilder':audit['quality'],
     'actualViews':3,'actualDisplayedSurfaces':1,'sampledProjectedVerticesPerView':12,
     'oneSceneRendererCanvas':True,'manualViewOnlyNoCameraCommands':True,'cameraSelectionLayerPreserved':True,
     'nativeAnatomyClickPreserved':True,'resourceReleaseCycles':5,'finalConsoleWarningsErrors':0,
     'testsPassed':9,'typecheckPassed':True,'productionBuildPassed':True,'lazyBuildCheckPassed':True,
     'productionSampleLeakCount':0,'cost':audit['cost'],
     'actualSameCameraDelta':{'drawCalls':1,'triangles':1920,'geometryBuffersBytes':36096,'geometries':1},
     'budget':{'overviewBytesWithSample':overview+sample_path.stat().st_size,'overviewLimit':20*1024*1024,
       'overviewTrianglesWithSample':overview_triangles+1920,'triangleLimit':1_000_000,
       'runtimeGeometryBytesWithSample':b['dataset']['bytes']+36096,'geometryLimit':96*1024*1024,
       'thresholdsRaised':False},
     'preservation':{'baselineWipFiles':len(baseline['wipHashes']),'changedBaselineWip':changed,
       'originalBlendSha256':audit['sourceSha256'],'startHEAD':baseline['head'],
       'preCommitHEAD':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()},
     'remainingUnits':{'AT3':'generate and register trunk/arm/leg chunks using this method; validate seams, both sides, gaps and penetration in the same scene',
       'AT4':'separately resolve head, hands/feet, hidden regions and mucosa inputs; this thigh sample supplies none of those surfaces'},
     'nextUnit':'AT3','nextUnitExecuted':False}
(E/'validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out,ensure_ascii=False))
