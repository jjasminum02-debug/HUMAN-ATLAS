"""Read-only closeout checks for the rejected r30 trial, not geometry approval."""
from pathlib import Path
import hashlib
import json
import struct
import sys
import numpy as np

R = Path(__file__).resolve().parents[4]
E = Path(__file__).resolve().parent
O = R / 'atlas-data/anatomy/skin/at10-fit-r3'
B = R / 'work/evidence/AT10/2026-10-13-skin-fit-r2'
load = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
d = load(E / 'candidates/fit-r30.json')
baseline = load(B / 'candidates/fit-r22.json')
start = load(E / 'start.json')
mapping = load(O / 'source-to-derived-r30.json')
cost = load(O / 'cost-r30.json')
qa = load(E / 'candidates/fit-r30-intersections.json')
corr = load(E / 'fold-aware-correspondence-r30.json')
loader = load(E / 'loader-validation-r30.json')
manifest = load(O / 'manifest-r30.json')
assert manifest['kind'] == 'rejected_local_registration_trial'
assert not manifest['fitAcceptancePassed'] and not manifest['learnerEligible']
assert not manifest['registeredInLearnerPackage']
assert manifest['geometryValidation']['crossingSkinTriangles'] == 4339
assert manifest['geometryValidation']['selfCrossingPairs'] == 1211
for key in ('asset', 'mapping', 'landmarks', 'recipe', 'cost'):
    assert (O / manifest[key]).exists()
preserved = ['sourceVertices', 'originalVertexIds', 'uv', 'faces',
             'sourceGroupCounts', 'inputHashes', 'sourceReturnVertices']
assert all(d[k] == baseline[k] for k in preserved)
assert not d['fitAcceptancePassed'] and not d['learnerEligible']
assert sha(R / 'atlas-data/anatomy/skin/at10-fit-r2/skin-candidate-r22.glb') == start['baselineGlbSha256']
changed_wip = [p for p, h in start['trackedWipHashes'].items() if sha(R / p) != h]
assert not changed_wip, changed_wip
raw = (O / 'skin-candidate-r30.glb').read_bytes()
assert hashlib.sha256(raw).hexdigest() == mapping['glbSha256'] == cost['sha256'] == qa['emittedGlbSha256']
jl = struct.unpack_from('<I', raw, 12)[0]
glb = json.loads(raw[20:20 + jl])
binary = 28 + jl

def accessor(index):
    a = glb['accessors'][index]
    view = glb['bufferViews'][a['bufferView']]
    dtype = {5126: '<f4', 5123: '<u2', 5125: '<u4'}[a['componentType']]
    width = {'VEC3': 3, 'VEC2': 2, 'SCALAR': 1}[a['type']]
    return np.frombuffer(raw, dtype=dtype, count=a['count'] * width,
                         offset=binary + view.get('byteOffset', 0) + a.get('byteOffset', 0)).reshape(-1, width)

primitive = glb['meshes'][0]['primitives'][0]
positions = accessor(primitive['attributes']['POSITION'])
uv = accessor(primitive['attributes']['TEXCOORD_0'])
indices = accessor(primitive['indices']).ravel()
logical_positions = np.array(d['positions'], dtype='<f4')
source_uv = np.array(d['uv'], dtype='<f4')
for i, m in enumerate(mapping['emittedVertices']):
    assert m['sourceVertex'] == d['originalVertexIds'][m['logicalVertex']]
    assert np.array_equal(positions[i], logical_positions[m['logicalVertex']])
    assert np.array_equal(uv[i], source_uv[m['sourceUv']])
corner_uv = [f['uv'][k] for f in d['faces'] for j in range(1, len(f['v']) - 1) for k in (0, j, j + 1)]
assert corner_uv == [mapping['emittedVertices'][int(i)]['sourceUv'] for i in indices]
assert len(indices) // 3 == 26756 and not mapping['helperExported']

native = load(R / 'work/evidence/AT10/2026-10-13-skin-fit-r1/native-surfaces-r1.json')
face_incidence = {i: [] for i in range(len(d['positions']))}
for f in d['faces']:
    for i in f['derivedVertices']:
        face_incidence[i].append(f['sourceFace'])
constraint_count = 0
patch_metrics = []
for patch in corr['patches']:
    side = patch['patch'].rsplit('-', 1)[1]
    for field in ('sourceReferenceFrame', 'nativeReferenceFrame'):
        assert abs(np.linalg.det(patch[field]) - 1) < 1e-8
    for c in patch['constraintsData']:
        constraint_count += 1
        i = c['vertex']
        assert d['originalVertexIds'][i] == c['sourceVertex']
        assert np.array_equal(d['sourceVertices'][i], c['sourceM'])
        assert c['sourceObjFaces'] == face_incidence[i]
        n = native[c['nativeSourceKey']]
        assert n['side'] == side
        tri = np.array(n['v'])[n['t'][c['nativeTriangle']]]
        assert np.array_equal(tri, c['nativeWorldM'])
        assert not c['placementVerified']
        assert np.isfinite(c['targetM']).all()
    patch_metrics.append({k: patch[k] for k in ('patch', 'vertices', 'constraints',
        'minimumSignedSkinPrismJacobian', 'nonPositiveSkinPrisms',
        'finalMinimumDeterminant', 'nonPositiveOneRingCount', 'maximumTargetResidualM')})
addresses = np.load(E / 'candidates/fit-r30-contact-addresses.npz')
assert len(addresses['skinTriangle']) == qa['exactSegmentTriangleCrossingPairs']
assert len(addresses['selfCrossingTrianglePairs']) == qa['nonAdjacentSelfCrossingPairs']
assert qa['candidateUnchanged'] and loader['formatValidationPassed']
assert not loader['groundClearancePassed']
screens = sorted((E / 'screens').glob('emitted-r30-*.png'))
assert len(screens) == 46
result = {
    'schemaVersion': 1, 'revision': 'r30', 'date': '2026-10-14',
    'sourceAndBaselineValidationReused': start['inputValidationReused'],
    'baselineIndependentReproductionReused': True,
    'newIndependentFullGenerationReproductionPerformed': False,
    'sourceDiscoveryOrFullPackageInvestigationRepeated': False,
    'sourceTopologyFaceCornerUvOriginalIdsPreserved': True,
    'sourceFieldsCompared': preserved, 'helperExported': False,
    'emittedFloat32MappingAndEveryFaceCornerUvPassed': True,
    'actualSourceNativeFacetAndSideAddressesChecked': constraint_count,
    'properReferenceFramesPassed': True,
    'nativeInputModified': False, 'validatorReadOnlyPassed': qa['candidateUnchanged'],
    'trackedWipCount': len(start['trackedWipHashes']), 'changedWip': changed_wip,
    'primaryR22GlbUnchanged': True,
    'rejectedTrialManifestAndReferencesPassed': True,
    'formatValidationPassed': True, 'groundClearancePassed': False,
    'geometryValidationPassed': False, 'acceptancePassed': False,
    'crossingSkinTriangles': qa['crossingSkinTriangles'],
    'nonAdjacentSelfCrossingPairs': qa['nonAdjacentSelfCrossingPairs'],
    'patchMetrics': patch_metrics,
    'positivityLimitation': 'Positive constructed tangent-normal skin prisms do not prove a positive 3D deformation or global injectivity. One-ring diagnostics remain negative and actual intersections fail.',
    'actualEmittedOfflineScreenFrames': len(screens), 'actualLearnerImportCount': 0,
    'learnerEligible': False, 'promotedToRuntime': False,
    'checksPassed': True, 'checksMeaning': 'Format/provenance/read-only/preservation checks only; the expected geometry failure is retained.'
}
(E / 'scoped-checks-r30.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: result[k] for k in ('checksPassed', 'geometryValidationPassed', 'acceptancePassed', 'crossingSkinTriangles', 'nonAdjacentSelfCrossingPairs', 'actualSourceNativeFacetAndSideAddressesChecked', 'trackedWipCount')}, indent=2))
