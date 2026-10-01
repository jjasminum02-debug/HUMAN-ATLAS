#!/usr/bin/env python3
"""Read all frozen source ledgers; preserve raw neural candidates without anatomy promotion."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = 'atlas-data/manifests/nerve-support-t61.json'


def digest(path):
    h = hashlib.sha256()
    with (ROOT / path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def load(path):
    return json.loads((ROOT / path).read_text())


def build():
    raw_path = 'work/evidence/T98/blender-raw-object-inventory.json'
    bp_path = 'atlas-data/manifests/bodyparts3d-r4-source-manifest-t51.json'
    za_registry = 'atlas-data/source-cache/datasets/za/registry.json'
    content_path = 'atlas-data/terminology/learner-structure-source-content.json'
    exec_state = load('work/EXECUTION.json')
    records = exec_state.get('taskRecords', exec_state.get('tasks', {}))
    if not records:
        raise ValueError('EXECUTION record schema changed')
    predecessor = records['T84']
    if predecessor['executionStatus'] != 'completed' or predecessor['acceptance'] != 'passed':
        raise ValueError('T84 must finish before freezing shared predecessor data')
    raw = load(raw_path)
    bp = load(bp_path)
    inputs = [raw_path, bp_path, za_registry, content_path, 'atlas-data/catalog/canonical-catalog.json',
              'atlas-data/sources/registry.json', 'work/product-scope.json',
              'atlas-data/source-cache/datasets/za/compiled/manifest.json',
              'atlas-data/overlays/za-local-integration.json', 'work/product-acceptance.json',
              'work/reports/T58.md', 'work/reports/T81.md', 'work/reports/T83.md', 'work/reports/T84.md']
    inputs += predecessor['progress']['productAcceptance']['evidence']
    inputs += [m['path'] for m in bp['source']['metadataFiles']]
    inputs = list(dict.fromkeys(inputs))
    input_hashes = {p: digest(p) for p in inputs}
    for m in bp['source']['metadataFiles']:
        assert input_hashes[m['path']] == m['sha256'], m['path']
        assert (ROOT / m['path']).stat().st_size == m['bytes'], m['path']
    blend_path = 'atlas-data/source-cache/z-anatomy/t97/extracted/Z-Anatomy/Startup.blend'
    assert digest(blend_path) == raw['source']['memberSha256'], 'ZA original hash'
    input_hashes[blend_path] = raw['source']['memberSha256']
    rows = []
    for index, obj in enumerate(raw['allObjects']):
        paths = obj['collectionPaths']
        # Mixed source system includes sense organs. Preserve it as a broad candidate set.
        if not any('Nervous system' in p or '7: Nervous system & Sense organs' in p for p in paths):
            continue
        locator = obj['sourceObjectLocator']
        key = 'za-c7010a9:raw:' + locator['objectDataBlockPointer']
        rows.append({'id': key, 'sourceNamespace': 'za-c7010a9', 'sourceObjectId': locator['objectDataBlockPointer'],
                     'ledgerPath': raw_path, 'ledgerPointer': f'/allObjects/{index}',
                     'sourceNameObservation': locator['objectIdName'], 'representationKindObservation': obj['dataKind'],
                     'scopeDisposition': 'neural_collection_candidate' if any('Nervous system' in p for p in paths) else 'mixed_neural_sense_context',
                     'sourceParentObservation': obj['parentObjectName'], 'side': 'unknown', 'geometry': None,
                     'identity': 'candidate', 'localSelection': 'unsupported', 'sourceOnly': True,
                     'humanReview': 'not_performed', 'publicRedistribution': 'held',
                     'missing': ['evaluated_geometry', 'nerve_specific_identity_side_scope', 'placement_pose', 'branch_and_innervation_evidence']})
    # PART-OF is the source's explicit system hierarchy. Lexical extra rows are candidates only.
    graph = {}
    with (ROOT / 'atlas-data/source-cache/bodyparts3d-r4/metadata/partof_inclusion_relation_list.txt').open() as stream:
        for edge in csv.DictReader(stream, delimiter='\t'):
            graph.setdefault(edge['parent id'], set()).add(edge['child id'])
    descendants = set()
    pending = ['FMA7157']
    while pending:
        concept = pending.pop()
        if concept in descendants:
            continue
        descendants.add(concept)
        pending.extend(graph.get(concept, []))
    elements = {r['sourceElementFileId']: r for r in bp['sourceElementFiles']}
    local_objs = {}
    for base in ['atlas-data/source-cache/bodyparts3d-r4/mesh', 'atlas-data/assets']:
        for path in sorted((ROOT / base).rglob('*.obj')):
            if path.stem.startswith('FJ'):
                local_objs.setdefault(path.stem, []).append(str(path.relative_to(ROOT)))
    for index, concept in enumerate(bp['sourceConcepts']):
        in_system = concept['sourceFmaConceptId'] in descendants
        lexical = any(any(token in name.lower() for token in ('nerve', 'gangli', 'plexus', 'nervous')) for name in concept['nameObservations'])
        if not (in_system or lexical):
            continue
        availability = []
        for fj in concept['elementFileIds']:
            assert fj in elements, fj
            # Historical acquisition state is not current availability. Check actual local files.
            candidates = list(local_objs.get(fj, []))
            old_path = elements[fj]['cachedSource'].get('path')
            if old_path and old_path not in candidates:
                candidates.append(old_path)
            found = [p for p in candidates if (ROOT / p).is_file()]
            availability.append({'fileId': fj, 'localFiles': [{'path': p, 'sha256': digest(p)} for p in found],
                                 'status': 'local_source_unvalidated' if found else 'not_found_in_scanned_local_obj_roots; archive_availability_not_geometry_validation'})
        rows.append({'id': 'bp3d-r4:concept:' + concept['sourceFmaConceptId'], 'sourceNamespace': 'bp3d-r4',
                     'sourceObjectId': concept['sourceFmaConceptId'], 'ledgerPath': bp_path,
                     'ledgerPointer': f'/sourceConcepts/{index}', 'sourceNameObservation': concept['sourceNameEnglish'],
                     'scopeDisposition': 'source_nervous_system_descendant_context' if in_system else 'lexical_candidate_unconfirmed',
                     'elementAvailability': availability, 'side': 'unknown', 'geometry': None,
                     'identity': 'candidate', 'localSelection': 'unsupported', 'sourceOnly': True,
                     'humanReview': 'not_performed', 'publicRedistribution': 'held',
                     'missing': ['nerve_specific_identity_side_scope', 'evaluated_geometry_and_registration', 'branch_and_innervation_evidence']})
    content = load(content_path)
    canonical = load('atlas-data/catalog/canonical-catalog.json')
    assert not canonical['entities']['innervations'], 'New structured innervation requires explicit scope re-evaluation'
    assert all(r['fieldDisposition']['motorNerve']['status'] == 'no_verified_field_claim' for r in content['records'])
    scope = load('work/product-scope.json')
    assert {k: scope['denominators'][k] for k in ('targets', 'memberships', 'regions')} == {'targets': 542, 'memberships': 563, 'regions': 12}
    assert scope['denominators']['existingCanonicalHaBindings'] == 130
    assert sorted(scope['denominators']['historical163']['categoryCounts'].values()) == [2, 6, 20, 135]
    from collections import Counter
    counts = dict(Counter(r['sourceNamespace'] for r in rows))
    return {'schemaVersion': 't61-source-inventory-v1', 'contractRevision': 'app-completion-2026-10-01',
            'inputs': input_hashes, 'denominators': scope['denominators'],
            'preserved': {'existingHaConnections': 130, 'historical163': [6, 20, 135, 2]},
            'fullLedgerReferences': [{'path': raw_path, 'rows': len(raw['allObjects']), 'sha256': input_hashes[raw_path]},
                                     {'path': bp_path, 'conceptRows': len(bp['sourceConcepts']), 'elementRows': len(bp['sourceElementFiles']), 'sha256': input_hashes[bp_path]},
                                     {'path': content_path, 'rows': len(content['records']), 'sha256': input_hashes[content_path]}],
            'sourceComparison': {'za-c7010a9': {'original': blend_path, 'scope': 'raw mixed nervous/sense collection metadata; not evaluated nerve geometry',
                                'frameConventionRef': za_registry + '#/manifest/frameContract', 'poseValidation': 'bone_muscle_snapshot_only; no nerve certification'},
                                 'bp3d-r4': {'scope': 'official PART-OF nervous system descendants plus lexical candidates; not nerve identities',
                                'frameConvention': 'source millimeters; atlas[x,y,z]=source[x,z,-y]/1000; axis conversion is not ZA registration',
                                'poseValidation': 'source static reference, joint posture not certified'},
                                 'opensim': {'scope': 'existing musculoskeletal model; no nerve representation registered; originals unchanged'},
                                 'crossSourceEquivalence': [], 'branchEdgesInSourceMetadataAreAnatomyClaims': False,
                                 'sourceMuscleCollectionsAreInnervationClaims': False},
            'counts': {'sourceCandidateRows': len(rows), 'byNamespace': counts, 'supportedNerve3D': 0,
                       'supportedNerveCards': 0, 'verifiedBranchRelations': 0, 'verifiedMotorRelations': 0,
                       'supportedMuscleMotorText': 0, 'muscleFieldDispositionRows': len(content['records'])},
            'support': {'supportedNerveIds': [], 'supportedFeatures': ['source_inventory', 'validated_registration_contract', 'typed_card_projection', 'layer_pose_selection_policy'],
                        'unsupportedFeatures': ['nerve3D', 'nerve_picking', 'nerve_cards', 'innervation_highlight', 'cutaneous_territory', 'root_dermatome', 'meridians', 'deforming_nerve_pose'],
                        'wholeBodyResearchCompleteness': 'not_established; no finite all-nerve denominator claimed'},
            'registry': {'schemaVersion': 'nerve-support-v1', 'instances': [], 'targets': [], 'evidence': [], 'relations': []},
            'contentCompleteness': 'partial', 'candidates': rows,
            'nextActions': ['Evaluate source curves/meshes with original hash/locator and modifiers in T62; do not use raw points as validated course',
                            'Verify exact identity/side/scope and source-native frame/pose before common registration',
                            'Acquire located branch and motor-innervation evidence independently from source collections',
                            'Retain all other source contexts and unacquired elements; prioritize existing muscle-selection flow without shrinking whole-body ledger']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    result = build()
    payload = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.check:
        assert (ROOT / OUTPUT).read_text() == payload, 'Inventory stale; inspect input drift before rebuilding'
    else:
        (ROOT / OUTPUT).write_text(payload)
    print(json.dumps({'status': 'passed', 'counts': result['counts']}, ensure_ascii=False))
