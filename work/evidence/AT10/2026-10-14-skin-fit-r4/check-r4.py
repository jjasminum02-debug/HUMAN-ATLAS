"""Read-only artifact/provenance checks; geometry failure remains mandatory."""
from pathlib import Path
import hashlib
import json
import struct
import numpy as np

R = Path(__file__).resolve().parents[4]
E = Path(__file__).resolve().parent
O = R / 'atlas-data/anatomy/skin/at10-fit-r4'
B = R / 'work/evidence/AT10/2026-10-13-skin-fit-r2'
load = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
start = load(E / 'start.json')
baseline = load(B / 'candidates/fit-r22.json')
native = load(R / 'work/evidence/AT10/2026-10-13-skin-fit-r1/native-surfaces-r1.json')
prior_controls = {x['id']: x for x in load(R / 'work/evidence/AT10/2026-10-13-skin-fit-r1/native-controls-r2.json')['controls']}
assert sha(R / 'atlas-data/anatomy/skin/at10-fit-r2/skin-candidate-r22.glb') == start['baselineSha256']
assert all(sha(R / p) == h for p, h in start['trackedWipHashes'].items())
summaries = []
for rev in ['r34', 'r35']:
    path = E / f'candidates/fit-{rev}.json'
    before = sha(path)
    d = load(path)
    for k in ['sourceVertices', 'originalVertexIds', 'uv', 'faces', 'sourceGroupCounts', 'inputHashes', 'sourceReturnVertices']:
        assert d[k] == baseline[k], k
    m = load(O / f'source-to-derived-{rev}.json')
    cost = load(O / f'cost-{rev}.json')
    manifest = load(O / f'manifest-{rev}.json')
    assert not manifest['fitAcceptancePassed'] and not manifest['learnerEligible']
    assert not manifest['registeredInLearnerPackage'] and not d['fitAcceptancePassed']
    for k in ['asset', 'mapping', 'landmarks', 'recipe', 'cost']:
        assert (O / manifest[k]).exists()
    raw = (O / f'skin-candidate-{rev}.glb').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == m['glbSha256'] == cost['sha256'] == manifest['sha256']
    jl = struct.unpack_from('<I', raw, 12)[0]
    g = json.loads(raw[20:20+jl])
    def accessor(index):
        a = g['accessors'][index]; view = g['bufferViews'][a['bufferView']]
        width = {'VEC3': 3, 'VEC2': 2, 'SCALAR': 1}[a['type']]
        dtype = {5126: '<f4', 5123: '<u2', 5125: '<u4'}[a['componentType']]
        return np.frombuffer(raw, dtype=dtype, count=a['count']*width, offset=28+jl+view.get('byteOffset', 0)+a.get('byteOffset', 0)).reshape(-1, width)
    primitive = g['meshes'][0]['primitives'][0]
    position = accessor(primitive['attributes']['POSITION'])
    uv = accessor(primitive['attributes']['TEXCOORD_0'])
    indices = accessor(primitive['indices']).ravel()
    logical = np.array(d['positions'], dtype='<f4')
    suv = np.array(d['uv'], dtype='<f4')
    for i, em in enumerate(m['emittedVertices']):
        assert np.array_equal(position[i], logical[em['logicalVertex']])
        assert np.array_equal(uv[i], suv[em['sourceUv']])
        assert em['sourceVertex'] == d['originalVertexIds'][em['logicalVertex']]
    source_corners = [f['uv'][k] for f in d['faces'] for j in range(1, len(f['v'])-1) for k in (0, j, j+1)]
    assert source_corners == [m['emittedVertices'][int(i)]['sourceUv'] for i in indices]
    assert not m['helperExported'] and len(indices)//3 == 26756
    incidence = [[] for _ in d['positions']]
    for f in d['faces']:
        for i in f['derivedVertices']: incidence[i].append(f['sourceFace'])
    pair_count = 0
    for patch in load(E / f'surface-bands-{rev}.json')['patches']:
        for ctrl in patch['nativeJointControls']:
            assert ctrl == prior_controls[ctrl['id']]
        for row in patch['continuousSurfaceBandPairs']:
            pair_count += 1
            i = row['vertex']
            assert row['sourceVertex'] == d['originalVertexIds'][i]
            assert row['sourceM'] == d['sourceVertices'][i]
            assert row['sourceObjFaces'] == incidence[i]
            n = native[row['nativeSourceKey']]
            assert np.array_equal(np.array(n['v'])[n['t'][row['nativeTriangle']]], row['nativeWorldM'])
            if patch['patch'] != 'pelvis-bilateral':
                assert n['side'] == patch['patch'].rsplit('-', 1)[1]
            assert row['placementVerified'] is False
    geometry = load(E / f'candidates/fit-{rev}-intersections.json')
    replay = load(E / f'field-inspection-{rev}.json')
    loader = load(E / f'loader-validation-{rev}.json')
    assert geometry['candidateUnchanged'] and replay['candidateReadOnly']
    assert replay['allNumericalReplayAndFiniteDifferenceChecksPassed']
    assert loader['formatValidationPassed'] and loader['actualLearnerImportCount'] == 0
    assert not geometry['acceptancePassed'] and geometry['crossingSkinTriangles'] > 0
    assert geometry['nonAdjacentSelfCrossingPairs'] > 0 and not loader['fitAcceptancePassed']
    assert sha(path) == before
    summaries.append({'revision': rev, 'sourceNativeFacetPairsChecked': pair_count,
        'emittedMappingAndAllFaceCornerUvPassed': True, 'sourceHelperControlsPreserved': True,
        'candidateReadOnly': True, 'crossingSkinTriangles': geometry['crossingSkinTriangles'],
        'selfCrossingPairs': geometry['nonAdjacentSelfCrossingPairs'],
        'formatValidationPassed': True, 'groundClearancePassed': loader['groundClearancePassed'],
        'geometryAcceptance': False, 'actualLearnerImportCount': 0})
result = {'date': '2026-10-14', 'checksPassed': True,
    'checkMeaning': 'Artifact/provenance/read-only checks pass; actual geometry acceptance fails.',
    'geometryAcceptance': False, 'learnerEligible': False, 'primaryR22Unchanged': True,
    'sourceRightsHashesAndR22ReproductionReused': start['reusedValidation'],
    'fullSourceDiscoveryOrFormatReproductionRepeated': False,
    'newFullGenerationIndependentReproductionPerformed': False,
    'trackedWipCount': len(start['trackedWipHashes']), 'trackedWipHashesUnchanged': True,
    'trials': summaries, 'actualLatestOfflineFrames': len(list((E / 'screens').glob('emitted-r35-*.png'))),
    'actualLearnerImportCount': 0, 'noCameraUiRuntimeChanges': True}
assert result['actualLatestOfflineFrames'] == 46
(E / 'scoped-checks-r35.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
