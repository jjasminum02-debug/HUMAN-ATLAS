"""Derive T98 source identity, frame evidence and bounded base selection from actual probe."""
import collections
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
def read(path): return json.loads((ROOT / path).read_text())
def write(name, data): (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

probe = json.loads((OUT / 'evaluated-base-probe.json').read_text())
raw = read('work/evidence/T98/blender-raw-object-inventory.json')
reconciliation = read('work/evidence/T98/target-reconciliation-t98.json')
baseline = read('work/evidence/2026-09-28-whole-body-reset/audit-metrics.json')
raw_by_name = {r['sourceObjectLocator']['objectIdName']: r for r in raw['allObjects']}
by_name = {r['name']: r for r in probe['objects']}
source_hash = probe['sourceSha256']
objects = []
for name, row in sorted(by_name.items()):
    source = raw_by_name[name]
    assert row['sourceLocator'] == source['sourceObjectLocator']
    key_input = {'memberSha256': source_hash, 'name':name, 'dataName':row['dataName'],
                 'serializedFileBlockOffset':row['sourceLocator']['serializedFileBlockOffset']}
    source_key = 'ZA-c7010a9-' + hashlib.sha256(json.dumps(key_input,sort_keys=True).encode()).hexdigest()[:24]
    kind = 'skeletal_surface' if 'bone' in row['systems'] else (
        'muscle_surface_or_part' if 'Muscles' in row['collections'] else 'musculoskeletal_accessory')
    objects.append({'sourceKey':source_key, 'identityKind':'derived_source_object_key_not_upstream_or_canonical_id',
        'sourceLocator':row['sourceLocator'], 'name':name, 'dataName':row['dataName'],
        'parent':row['parent'], 'collections':row['collections'], 'kind':kind,
        'evaluatedGeometrySha256':row['geometrySha256'], 'sourceLocalBounds':row['bounds'],
        'sourceLabelSide': 'left' if name.endswith('.l') else 'right' if name.endswith('.r') else None,
        'sourceOnly':True, 'canonicalConceptId':None, 'upstreamFjId':None,
        'learnerBinding':'source_only_unbound', 'defaultLearnerVisible':False,
        'sourceHiddenStatePreserved':{'hideRender':row['hideRender'],'hideViewport':row['hideViewport']},
        'localTechnicalEvaluation':'supported_by_package_access_and_derivative_grant',
        'appDisplayRights':'held_not_approved_by_this_task', 'publicRedistribution':'held',
        'humanReview':'not_performed', 'rightsGroup':'ZA_PINNED_PACKAGE_WITH_EXCEPTIONS',
        'upstreamPerObjectAncestry':'unresolved_not_required_to_identify_this_ZA_object'})
object_index = {r['name']:r['sourceKey'] for r in objects}
pairs=[]
for name,left in by_name.items():
    if not name.endswith('.l') or name[:-2]+'.r' not in by_name: continue
    right=by_name[name[:-2]+'.r']
    lx=sum(b[0] for b in left['bounds'])/2
    rx=sum(b[0] for b in right['bounds'])/2
    pairs.append({'left':name,'right':right['name'],'leftCenterX':lx,'rightCenterX':rx,
                  'sourceLabelAndPositionConsistent':lx>0 and rx<0})
assert pairs and all(p['sourceLabelAndPositionConsistent'] for p in pairs)
targets=[]
for target in reconciliation['targets']:
    names=[c['objectLabel'] for c in target['zAnatomyObjectNameCandidates']]
    keys=[object_index[name] for name in names if name in object_index]
    targets.append({'targetId':target['targetId'],'semanticKind':target['semanticKind'],
                    'regionIds':target['regionIds'], 'candidateSourceKeys':keys,
                    'status':'lexical_candidate_with_evaluated_geometry' if keys else (
                        'lexical_group_or_other_representation_needs_reconciliation' if names else 'no_ZA_lexical_candidate'),
                    'canonicalIdentityVerified':False,'learnerBindingAdded':False})
catalog={'sourceHash':source_hash,'sourceRevision':'c7010a903b75a2fd24a13b1c2c4c3546a9223780',
         'sourceKeyContract':'snapshot/member hash + serialized locator + exact runtime name/data/parent/collection validation',
         'objects':objects, 'exclusions':probe['excluded'], 'canonicalTargetCount':542,
         'regionMembershipCount':563,'targetOverlay':targets,
         'targetStatusCounts':dict(collections.Counter(t['status'] for t in targets)),
         'requiredTargetListUnchanged':True,'muscleUniqueDenominator':None}
write('source-catalog.json',catalog)

frame={'sourceFrameId':'ZA-c7010a9-native-XYZ-frame0-m',
       'sourceUnit':'m','metersPerSourceUnit':1.0,
       'unitEvidence':{'runtime':probe['unit'],'officialImplementation':
           'https://github.com/blender/blender/blob/v3.5.0/source/blender/makesrna/intern/rna_scene.c#L4220',
           'interpretation':'METRIC scale_length=1 maps one source unit to 1 m; CENTIMETERS controls display, not a 0.01 geometry scale.',
           'calibratedPhysicalSubjectMeasurement':False},
       'sourceAxes':{'positiveX':'subject_left','positiveY':'posterior','positiveZ':'superior'},
       'evidence':{'bilateralPairsChecked':len(pairs),'sideCenterConflicts':0,
                   'pairs':pairs,'frontView':'source-minus-y.png','backView':'source-plus-y.png',
                   'sideView':'source-plus-x.png','heightMeters':probe['bounds'][1][2]-probe['bounds'][0][2],
                   'assessment':'AI inspection of source label/collection/geometry and full-body images; not human anatomy approval'},
       'sourceToProjectConvention':[[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1]],
       'targetFrameId':'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR',
       'transformScope':'axis convention only; no inter-model registration, translation, fit, or mm-to-m scaling',
       'registeredToBP3DGeometry':False,
       'staticReferencePose':{'id':'ZA-'+source_hash[:16]+'-frame0-autoexec-off',
           'sourceFrame':0,'kind':'hash-bound evaluated static snapshot; not a rig bind pose',
           'sourceProvidedRestPoseId':None,'rigBindingVerified':False,
           'geometryAffectingObjectDriversInCandidateSet':sum(len(r['drivers']) for r in probe['objects']),
           'knownGlobalDependencyWarning':'Oesophagus/profile cycle outside selected bone/muscle source systems; whole source depsgraph not certified'},
       'learnerBindingOrHumanReviewGranted':False}
write('frame-contract.json',frame)

rights={'sourceRevision':catalog['sourceRevision'],'sourceMemberSha256':source_hash,
        'pinnedReadme':'source-readme.md','pinnedReadmeSha256':sha(OUT/'source-readme.md'),
        'defaultPublisherDeclaration':'CC-BY-SA-4.0 with separate upstream attributions/exceptions',
        'upstreamDeclaration':'BodyParts3D CC-BY-SA-2.1-Japan attribution retained; no guessed FJ crosswalk',
        'exceptionGroups':['Brainder/White matter','Dundee cranial nerves/foramina CC-BY-4.0',
                           'Dundee inner ear CC-BY-NC-SA-4.0','Kidney CC-BY-NC-4.0'],
        'localTechnicalEvaluationBasis':'Pinned README explicitly permits database access/acquisition and derivative work; bounded non-distributed source evaluation with original attribution preserved.',
        'localTechnicalEvaluation':'supported','commercialOrPublicReleaseAuthorized':False,
        'appDisplayRights':'held','publicRedistribution':'held','humanReview':'not_performed',
        'perObjectRightsPolicy':'Every exact object inherits the package review record, not a fabricated upstream authorship. Exceptions/unresolved upstream ancestry remain held for display/release. T99 may compile local held data but must not publish or silently expose it.',
        'bp3dCurrentPageVersusLegacyHeader':'unresolved; unchanged; not required to choose the separate pinned ZA namespace for local compiler development'}
write('rights-scope.json',rights)

core=[r for r in probe['objects'] if 'bone' in r['systems'] or 'Muscles' in r['collections']]
core_cost={k:sum(r[k] for r in core) for k in ['vertices','triangles','indexedPositionNormalIndexBytes','flatPositionNormalIndexBytes']}
decision={'task':'T98','decision':'select_Z_Anatomy_as_primary_local_offline_compilation_base',
          'selectionScope':'source engineering feasibility and input freeze; NOT complete anatomy, learner binding, rig, public rights, or production release approval',
          'selectedSourceRevision':catalog['sourceRevision'],'selectedSourceMemberSha256':source_hash,
          'exactSourceObjects':len(objects),'corePreviewObjects':len(core),
          'coreKindCounts':dict(collections.Counter(r['kind'] for r in objects)),
          'corePreviewPolicy':'277 skeletal surfaces plus 509 source Muscles collection surfaces/parts; associated fascia/bursae etc retained in catalog but excluded from core QA view, not deleted.',
          'cost':{'ZAAllEvaluatedCandidates':probe['totals'],'ZACoreQA':core_cost,
                  'BP3DCurrentSubset':{'source':'work/evidence/2026-09-28-whole-body-reset/audit-metrics.json',
                      'scope':'existing partial app subset; not equivalent complete anatomy coverage',
                      'vertices':baseline['vertices'],'triangles':baseline['sourceTriangles'],
                      'actualGlbBytes':baseline['glbBytes'],
                      'samePositionNormalIndexLayoutBytes':baseline['vertices']*24+baseline['sourceTriangles']*12},
                  'interpretation':'Compare counts and identical uncompressed vertex/index layouts only. ZA byte values are estimates, BP3D GLB is measured. No whole-body download, mobile FPS or GPU-memory pass.'},
          'whySelected':['One consistent evaluated static pose contains visible head/face, limbs, bilateral scapulae, lumbar/sacral structures and latissimus candidates.',
                         '960 exact source objects evaluated with finite geometry; all 12 frozen hashes reproduced.',
                         'Source coordinate convention and source metric scale verified; no per-muscle fitting required to preserve this single-source pose.',
                         'The current BP3D app subset is retained as a regression/reference source, not blindly overlaid on ZA.',
                         'The technical input is usable for a generic compiler while distinct anatomy/rights release checks remain enforced.'],
          'targetReconciliation':catalog['targetStatusCounts'],
          'remainingResponsibilities':{'T99':['generic source namespace/compiler','indexed geometry, smoothing, LOD/chunks/cache','do not use flat expanded QA GLB as product','enforce held/visibility source state','retain all 542 target dispositions'],
                                     'T100':['canonical names/group/part/region crosswalk','missing target source resolution','per-item display eligibility','cross-source fitting only for verified gaps'],
                                     'T80':['all required target coverage and laterality audit'],
                                     'T58':['final visual and measured runtime performance']},
          'publicRedistribution':'held','humanReview':'not_performed','learnerBindingsAdded':0,
          'wholeBodyCoverageComplete':False,'productionReleaseApproved':False,'T99Started':False,
          'inputHashes':{name:sha(OUT/name) for name in ['evaluated-base-probe.json','source-catalog.json','frame-contract.json','rights-scope.json','runtime-integrity.json']}}
write('base-selection.json',decision)
print('T98 decision inputs generated',len(objects),len(core),catalog['targetStatusCounts'])
