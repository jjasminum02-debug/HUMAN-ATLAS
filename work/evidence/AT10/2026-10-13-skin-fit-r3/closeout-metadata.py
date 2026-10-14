"""Record failed local fit trials without promoting them or changing geometry."""
from pathlib import Path
import hashlib
import json
import numpy as np

R = Path(__file__).resolve().parents[4]
E = Path(__file__).resolve().parent
O = R / 'atlas-data/anatomy/skin/at10-fit-r3'
B = R / 'atlas-data/anatomy/skin/at10-fit-r2'
rel = lambda p: str(p.relative_to(R))
load = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def save(p, data):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

start = load(E / 'start.json')
d = load(E / 'candidates/fit-r30.json')
qa = load(E / 'candidates/fit-r30-intersections.json')
cost = load(O / 'cost-r30.json')
old = load(B / 'manifest-r22.json')
reasons = {
    23: 'Strict one-ring guard stalls target fitting; residual about 51-56 mm.',
    24: 'Revised local context still stalls under one-ring guard; not emitted/accepted.',
    25: 'Positive skin-prism ratios coexist with negative one-ring diagnostics and visible wrist/thumb/foot mismatch.',
    26: 'Proper ankle-MTP frame and digit ownership still leave actual crossings and negative ground clearance.',
    27: 'Six pinna controls per side reach 0.081 mm residual while the whole native rim protrudes. Pelvis also fails; neither patch selected.',
    28: 'Final rotation update leaves one negative skin prism per patch; rejected.',
    29: 'Final rotation guard repaired; native/self crossings and visible wrist/foot mismatch remain.',
    30: 'Extended forearm/calf reference increases native crossing total to 4339; not selected.'
}
metric_keys = ['patch', 'vertices', 'constraints', 'minimumSignedSkinPrismJacobian',
               'nonPositiveSkinPrisms', 'finalMinimumDeterminant',
               'nonPositiveOneRingCount', 'maximumTargetResidualM']
trials = []
for r in range(23, 31):
    cp = E / f'fold-aware-correspondence-r{r}.json'
    p = load(cp)
    qp = E / f'candidates/fit-r{r}-intersections.json'
    q = load(qp) if qp.exists() else None
    trials.append({
        'revision': f'r{r}', 'disposition': 'rejected_not_selected', 'reason': reasons[r],
        'patchMetrics': [{k: x.get(k) for k in metric_keys} for x in p['patches']],
        'emittedGeometryChecked': q is not None,
        'crossingSkinTriangles': q['crossingSkinTriangles'] if q else None,
        'nonAdjacentSelfCrossingPairs': q['nonAdjacentSelfCrossingPairs'] if q else None,
        'correspondenceSha256': sha(cp),
        'candidateSha256': sha(E / f'candidates/fit-r{r}.json'),
        'glbSha256': q.get('emittedGlbSha256') if q else None,
        'acceptancePassed': False
    })
save(E / 'attempt-ledger.json', {
    'date': '2026-10-14', 'started': '2026-10-13', 'retainedPrimary': 'r22',
    'noTrialPromoted': True, 'trials': trials,
    'failureLog': 'arap-r30.log initial syntax error; arap-r30-run2.log corrected run',
    'reproductionLimitation': 'Current tool captures final r30 algorithm. Historical intermediate outputs/metrics do not imply the final script recreates all prior algorithm versions.'
})
manifest = dict(old)
manifest.update({
    'asset': 'skin-candidate-r30.glb', 'sha256': cost['sha256'],
    'mapping': 'source-to-derived-r30.json', 'recipe': 'recipe-r30.json',
    'cost': 'cost-r30.json', 'landmarks': '../at10-fit-r2/landmarks-r22.json',
    'kind': 'rejected_local_registration_trial',
    'scope': 'hand/foot/adjacent forearm/calf trial, rejected; primary r22 unchanged',
    'aiAuthorship': 'AI-authored source joint/ring roles and native facet proposals; source helper joints are not observed skin creases or approved anatomical homologues',
    'geometryValidation': {'crossingSkinTriangles': 4339, 'selfCrossingPairs': 1211,
                           'acceptancePassed': False, 'positive3DDeformationEstablished': False},
    'candidateSelection': 'Not selected. Reduced self count does not offset native crossings or visible mismatch.',
    'educationalLandmarkApprovalAdded': 0, 'technicalSourceNativeCorrespondences': 1236,
    'baselineManifest': '../at10-fit-r2/manifest-r22.json',
    'independentFullGenerationReproductionPassed': False
})
save(O / 'manifest-r30.json', manifest)
tools = ['work/tools/at10_skin_arap.py', 'work/tools/export_at10_skin.py',
         'work/tools/validate_at10_skin_blender.py', 'work/tools/inspect_at10_skin_blender.py']
save(O / 'recipe-r30.json', {
    'schemaVersion': 3, 'kind': 'rejected_trial_recipe_not_production_character',
    'baselineManifest': rel(B / 'manifest-r22.json'), 'baselineGlbSha256': old['sha256'],
    'baselineRecipe': rel(B / 'recipe-r22.json'),
    'baselineCandidate': 'work/evidence/AT10/2026-10-13-skin-fit-r2/candidates/fit-r22.json',
    'nativeSnapshot': load(B / 'recipe-r22.json')['nativeSnapshot'],
    'sourceInputHashes': d['inputHashes'],
    'sourceUnitConversion': 'official dm->m 0.1 already applied; no second scale/native world matrix',
    'worldFrame': old['frameId'], 'poseId': old['poseId'],
    'method': 'source joint-local rings, named native facet constraints, proper local reference, positive edge-weight ARAP, staged targets and transported tangent-normal skin-prism line search',
    'guardLimitation': 'Positive constructed prisms do not prove positive 3D deformation/global injectivity. One-ring negatives and actual native/self crossings remain.',
    'bodyHelpersUvPolicy': 'original body IDs/quads/face-corner UV retained; original helpers unchanged and excluded from GLB',
    'sourceVersusAuthoredIndicators': 'Raw helper joint IDs and native facet/cap addresses retained. Source radial/ulnar and tibial/fibular directions are authored model indicators, not observed skin landmarks.',
    'numericConstraints': rel(E / 'fold-aware-correspondence-r30.json'),
    'constraintSha256': sha(E / 'fold-aware-correspondence-r30.json'),
    'steps': 12, 'parts': ['hand', 'foot'], 'guard': 'active-prism', 'extendedReference': True,
    'commands': [
        '/Volumes/Blender/Blender.app/Contents/MacOS/Blender --background --factory-startup --disable-autoexec --python work/tools/at10_skin_arap.py -- --evidence <fresh-evidence> --revision r30 --parts hand,foot --guard active-prism --extended-reference',
        'AT10_SKIN_EVIDENCE=<fresh-evidence> AT10_SKIN_ARTIFACTS=<fresh-artifacts> python3 work/tools/export_at10_skin.py --revision r30',
        'AT10_SKIN_EVIDENCE=<fresh-evidence> AT10_SKIN_ARTIFACTS=<fresh-artifacts> <blender> --background --factory-startup --disable-autoexec --python work/tools/validate_at10_skin_blender.py -- r30'
    ],
    'toolHashes': {p: sha(R / p) for p in tools}, 'observedGlbSha256': cost['sha256'],
    'independentFullGenerationReproductionPerformed': False,
    'priorR22IndependentReproductionReused': True, 'fitAcceptancePassed': False,
    'learnerEligible': False, 'webRuntimeGeneratorIncluded': False
})
units = [
    {'id': 'bilateral-wrist-palm-thumb', 'remainingInput': 'Explicit source palmar/dorsal wrist, thumb CMC/MCP and web-space surface bands against Radius/Ulna/carpal/metacarpal/fascia facets with continuous shared boundaries and native/self contact constraints.',
     'attempted': 'digit ownership, role-scoped facet rays, staged ARAP, active prism guard, extended forearm frame',
     'observed': 'r30 hand 617 crossings/side; arm 214/side; residual max27.35mm; negative one-ring109/hand.'},
    {'id': 'bilateral-ankle-foot-mtp-toes', 'remainingInput': 'Source/native dorsal, plantar, heel, MTP and every toe surface-band pairs with malleolar/calf transition and ground-clearance constraints; resolve dorsal/plantar ownership beyond ring angle.',
     'attempted': 'digit/part ownership, proper ankle-MTP/calf frames, actual cap/facet constraints',
     'observed': 'r30 foot785 crossings/side; leg227/226; residual19.62mm; negative one-ring68/foot; ymin -7.70mm.'},
    {'id': 'ear-attachment-head-neck-return', 'remainingInput': 'Whole helix/concha/lobule/tragus attachment bands against actual original native facets, not six extrema points; finish neck seam and separately classify original eyelid/oral return.',
     'attempted': 'r27 source vertex/face to native Helix/Lobule/Tragus ARAP constraints',
     'observed': '0.081mm point residual still leaves native rim exposed; rejected. r30 retains r22 head412 crossings; return cohort remains counted.',
     'genuineLocalAbsentInput': 'AT4 partial tongue only; gingiva/frenulum/sublingual mucosa absent, not replaced by outer skin.'},
    {'id': 'pelvis-perineal-thigh-and-residual-seams', 'remainingInput': 'Source gluteal/perineal/adductor and femoral-root surface bands, continuous shared seam boundary conditions and native/self contact constraints.',
     'attempted': 'r27 femur-axis/thigh ring and named Gluteus maximus native facet constraints',
     'observed': 'r27 pelvis residual28.46mm, negative one-ring9/7, visible seam; rejected. r22 retained. r30 groin30/trunk212 crossings.'},
    {'id': 'final-whole-body-geometry-and-landmarks', 'remainingInput': 'After local fixes, validate actual emitted native/self intersections, positive deformation, distances, all views and source/AI-authored navel/nipple/crease/nail registry; actual learner verification before runtime acceptance.',
     'attempted': 'actual emitted loader and 46 offline views; independent old format reproduction reused',
     'observed': 'r30 native4339/self1211. Actual learner import0; approved fitted skin0.'}
]
for u in units:
    u.update(status='unresolved', sourceMissing=False)
save(E / 'remaining-units.json', {
    'task': 'AT10/skin-fit', 'date': '2026-10-14', 'acceptancePassed': False,
    'resumeUnit': 'skin-fit', 'retainedPrimaryRevision': 'r22', 'latestRejectedTrial': 'r30',
    'sourceInputMissing': False, 'waitingForProfessorApproval': False, 'units': units,
    'nextAfterActualPass': 'AT10/skin-runtime', 'automaticNextExecution': False
})
npz = np.load(E / 'candidates/fit-r30-contact-addresses.npz')
t = np.array([[f['derivedVertices'][0], f['derivedVertices'][j], f['derivedVertices'][j+1]]
              for f in d['faces'] for j in range(1, len(f['derivedVertices'])-1)])
positions = np.array(d['positions'], dtype='<f4')
self_probes = []
for a, b in npz['selfCrossingTrianglePairs'][:48]:
    sides = []
    for x in (int(a), int(b)):
        sides.append({'skinTriangle': x, 'sourceObjFace': d['faces'][x//2]['sourceFace'],
                      'sourceVertexIds': [d['originalVertexIds'][int(v)] for v in t[x]],
                      'worldM': positions[t[x]].tolist()})
    self_probes.append({'triangles': sides, 'finding': 'actual emitted nonadjacent segment-triangle intersection'})
save(E / 'remaining-probes-r30.json', {
    'revision': 'r30', 'rejected': True,
    'retainedBaselineProbes': 'work/evidence/AT10/2026-10-13-skin-fit-r2/remaining-probes-r22.json',
    'nativeCrossingSkinTriangles': 4339, 'selfCrossingPairs': 1211,
    'nativeSamples': load(E / 'candidates/fit-r30-remaining-probes.json'),
    'selfSamples': self_probes, 'fullAddresses': 'candidates/fit-r30-contact-addresses.npz',
    'noPointSemanticApproval': True
})
views = sorted(p.name.removeprefix('emitted-r30-').removesuffix('-skin.png')
               for p in (E / 'screens').glob('emitted-r30-*-skin.png'))
save(E / 'visual-review-r30.json', {
    'revision': 'r30', 'date': '2026-10-14', 'actualArtifactSha256': cost['sha256'],
    'actualEmittedBlenderGltfImport': True, 'fixedNativeOverlay': True,
    'views': views, 'offlineFrames': 46,
    'contactSheets': [f'screens/review-r30-{i}.jpg' for i in range(1, 5)],
    'allSheetsInspected': True,
    'observations': {
        'wholeBody': 'native forearm/calf protrusion remains',
        'hands': 'both wrists pinched; palmar/dorsal thumb/finger correspondence and native fascia enclosure fail',
        'feet': 'both dorsal/plantar/heel surfaces expose native; toe/MTP correspondence incomplete',
        'head': 'native ear rim/attachment protrudes; eyelid/oral return not approved mucosa',
        'pelvis': 'posterior gluteal and perineal seam mismatch remains',
        'other': 'shoulder, neck, torso, sacrum, knees inspected; no whole-body fit acceptance'
    },
    'actualLearnerImportCount': 0, 'learnerG1toG8Passed': False,
    'cameraPolicyOrUiChanged': False, 'fitAcceptancePassed': False
})
save(E / 'cost-summary-r30.json', {
    'trialCost': cost, 'existingOverviewBytes': 20042516,
    'existingEducationCarrierBytes': 813096, 'combinedEncodedBytes': 21482188,
    'existingOverviewBudgetBytes': 20*1024**2, 'overBudgetBytes': 510668,
    'combinedTriangles': 964488, 'combinedDecodedGeometryBytes': 18875724,
    'actualLearnerDriverVramOrFpsMeasured': False, 'existingBudgetsChanged': False,
    'runtimeAdmission': False, 'noSurroundingNativeDeleted': True
})
save(E / 'summary.json', {
    'task': 'AT10/skin-fit', 'date': '2026-10-14', 'startHead': start['head'],
    'retainedPrimaryRevision': 'r22', 'retainedPrimarySha256': old['sha256'],
    'retainedPrimaryNativeCrossingTriangles': 3874, 'retainedPrimarySelfCrossingPairs': 1604,
    'latestTrial': 'r30', 'latestTrialManifest': rel(O / 'manifest-r30.json'),
    'latestTrialSha256': cost['sha256'], 'latestTrialNativeCrossingTriangles': 4339,
    'latestTrialSelfCrossingPairs': 1211, 'nativeCrossingDeltaVsR22': 465,
    'selfCrossingPairDeltaVsR22': -393, 'noTrialPromoted': True,
    'geometryValidationPassed': False, 'acceptancePassed': False, 'learnerEligible': False,
    'approvedFittedSkinCount': 0, 'actualLearnerImport': 0, 'actualLatestOfflineFrames': 46,
    'sourceInputMissing': False, 'professorApprovalBlocking': False,
    'wipPreserved': 45, 'resumeUnit': 'skin-fit', 'automaticNextExecution': False
})
print('Closeout metadata written. Primary r22 retained; all trials rejected.')
