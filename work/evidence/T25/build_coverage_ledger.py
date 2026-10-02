#!/usr/bin/env python3
"""Build the T25 all-muscle content/route disposition ledger from pinned project records."""
from __future__ import annotations
import hashlib, json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path('.')
INPUTS = {
    'productScope': 'work/product-scope.json',
    'targetScope': 'atlas-data/catalog/target-scope-t96.json',
    'motionReadiness': 'work/evidence/T35/motion-readiness-ledger.json',
    'structureSourceContent': 'atlas-data/terminology/learner-structure-source-content.json',
    'learnerCardRuntime': 'atlas-data/terminology/learner-card-runtime.json',
    'functionCoverage': 'work/evidence/T83/function-card-coverage.json',
    'authoringManifest': 'work/evidence/T59/authoring-run-manifest-r2.json',
    'motionVerification': 'work/evidence/T59/resume-2026-10-02/verification.json',
    'nerveSupport': 'atlas-data/overlays/nerve-support-t63.json',
    'nerveLearning': 'atlas-data/terminology/nerve-learning-content-t65.json',
    'nerveGraph': 'atlas-data/terminology/learner-nerve-graph-t25.json',
}

def read(path): return json.loads(Path(path).read_text())
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def value_hash(value): return hashlib.sha256(value.encode('utf-8')).hexdigest()

for path in INPUTS.values():
    if not Path(path).is_file(): raise SystemExit(f'missing input: {path}')
data = {key: read(path) for key, path in INPUTS.items()}
product = data['productScope']; t96 = data['targetScope']; motion = data['motionReadiness']
source = data['structureSourceContent']; runtime = data['learnerCardRuntime']; actions = data['functionCoverage']; authoring = data['authoringManifest']
source_concepts = motion['rows']['sourceConcepts']; source_instances = motion['rows']['sourceInstances']
target_rows = motion['rows']['targets']; membership_rows = motion['rows']['memberships']
concept_by_key = {r['conceptKey']: r for r in source_concepts}
instance_by_key = {r['sourceKey']: r for r in source_instances}
source_content_by_key = {key: row for row in source['records'] for key in row['sourceKeys']}
source_content_by_target = {row['targetId']: row for row in source['records'] if row.get('targetId')}
runtime_by_source = runtime['structure']['bySource']
action_by_source = {key: row for row in actions['records'] for key in row['sourceKeys']}
relations_by_source = defaultdict(list)
relations_by_nerve = defaultdict(list)
for relation in data['nerveGraph']['motorRelations']:
    relations_by_nerve[relation['nerveKey']].append(relation)
    for key in relation['targetSourceKeys']:
        relations_by_source[key].append(relation)

ready_source_keys = set()
for rows in __import__('re').findall(r'"subjectSourceKey"\s*:\s*"([^"]+)"', Path('atlas-web/src/data/learnerMotionRuntime.generated.ts').read_text()):
    ready_source_keys.add(rows)
exact_target_for_source = {}
for row in source['records']:
    if row.get('targetId'):
        for key in row['sourceKeys']:
            exact_target_for_source[key] = row['targetId']
for row in actions['records']:
    if row.get('targetContentScope'):
        for key in row['sourceKeys']:
            exact_target_for_source.setdefault(key, row['targetContentScope'])

# Targets and memberships are the full frozen motion denominator; context-only candidates stay unresolved.
targets = []
for row in target_rows:
    tid = row['targetId']
    exact_source_content = source_content_by_target.get(tid)
    exact_action = next((r for r in actions['records'] if r.get('targetContentScope') == tid and r['verifiedActionIds']), None)
    exact_motor = any(exact_target_for_source.get(key) == tid for key in relations_by_source)
    field_status = {}
    for field in ('origin', 'insertion'):
        if exact_source_content:
            field_status[field] = exact_source_content['fieldDisposition'][field]['status']
        else:
            field_status[field] = 'no_exact_target_scope_projection'
    field_status['actions'] = 'verified_target_scoped_text' if exact_action else 'no_exact_target_scoped_action_text'
    field_status['motorInnervation'] = 'verified_source_side_or_named_concept_relation' if exact_motor else 'no_verified_target_scoped_motor_relation'
    exact_motion_key = next((k for k in ready_source_keys if exact_target_for_source.get(k) == tid), None)
    field_status['motion'] = 'one_source_bound_playable_surface' if exact_motion_key else 'not_supported_by_current_clip'
    targets.append({
        'targetId': tid, 'semanticKind': row['semanticKind'], 'primaryOwner': row['primaryOwner'],
        'regionIds': row['regionIds'], 'membershipKeys': row['membershipKeys'],
        'identityAndExtent': 'unresolved_unless_separately_source_bound; candidate/context rows are not binding',
        'fields': field_status,
        'exactContentSourceKeys': exact_source_content['sourceKeys'] if exact_source_content else [],
        'exactMotionSourceKey': exact_motion_key,
        'contentDoesNotProveFullExtent': True,
    })

memberships = [{
    'membershipKey': row['membershipKey'], 'targetId': row['targetId'], 'regionId': row['regionId'],
    'targetFieldStatus': next(t['fields'] for t in targets if t['targetId'] == row['targetId']),
    'regionSpecificExtent': 'not_independently_verified',
    'targetTextIsNotMembershipExtentApproval': True,
} for row in membership_rows]

concepts = []
surfaces = []
for concept in source_concepts:
    ckey = concept['conceptKey']
    evidence_records = concept.get('latestAttachmentEvidence', {}).get('records', [])
    field_evidence = {field: [] for field in ('origin', 'insertion')}
    for evidence in evidence_records:
        for field in field_evidence:
            ref = evidence.get('fieldEvidence', {}).get(field)
            if ref:
                field_evidence[field].append({
                    'sourceIds': ref.get('sourceIds', []), 'locator': ref.get('locator'),
                    'learnerValueSha256': ref.get('learnerValueSha256'),
                    'recordSha256': evidence.get('recordSha256'), 'evidenceState': evidence.get('evidenceState'),
                })
    concept_surface_status = {}
    for field in ('origin', 'insertion'):
        rows = []
        for key in concept['sourceKeys']:
            text = runtime_by_source.get(key, {}).get(field)
            if text is None: status = 'missing_projection'
            elif text == '설명 정리 중': status = 'conflict_or_placeholder'
            else: status = 'learner_projection_present'
            rows.append({'sourceKey': key, 'status': status, 'valueSha256': value_hash(text) if text is not None else None})
        concept_surface_status[field] = rows
    action = next((r for r in actions['records'] if r['conceptKey'] == ckey), None)
    edges = []
    for key in concept['sourceKeys']:
        for rel in relations_by_source.get(key, []):
            if rel not in edges: edges.append(rel)
    text_rows = [r for r in data['nerveLearning']['records'] if r['nerveName'] == concept['sourceDataName']]
    concepts.append({
        'conceptKey': ckey, 'sourceDataName': concept['sourceDataName'], 'sourceKeys': concept['sourceKeys'],
        'sourceSides': concept['sourceSides'], 'regionIds': concept['regionIds'],
        'sourceOnly': concept['sourceOnly'], 'humanReview': concept['humanReview'], 'publicRedistribution': concept['publicRedistribution'],
        'historicalAttachmentDisposition': concept.get('historicalAttachmentDisposition', {}),
        'latestAttachmentEvidence': {'records': len(evidence_records), 'states': [r.get('evidenceState') for r in evidence_records], 'fields': field_evidence},
        'learnerProjection': concept_surface_status,
        'actions': {'disposition': action.get('actionDisposition') if action else 'no_record', 'verifiedActionIds': action.get('verifiedActionIds', []) if action else [], 'sourceKeys': action.get('sourceKeys', []) if action else []},
        'motorInnervationRelations': edges,
        'motion': {'readySurfaceCount': sum(k in ready_source_keys for k in concept['sourceKeys']), 'surfaceCount': len(concept['sourceKeys'])},
        'targetIdsContextOnly': concept.get('targetIdsContextOnly', []),
        'contextOnlyTargetsAreNotExactBindings': True,
    })
    for key in concept['sourceKeys']:
        inst = instance_by_key[key]
        content = source_content_by_key.get(key)
        rt = runtime_by_source.get(key, {})
        action_row = action_by_source.get(key)
        surfaces.append({
            'sourceKey': key, 'sourceName': inst['sourceName'], 'side': inst['side'],
            'regionIds': concept['regionIds'], 'conceptKey': ckey,
            'targetIdsContextOnly': concept.get('targetIdsContextOnly', []),
            'exactTargetId': exact_target_for_source.get(key),
            'origin': {'status': 'missing_projection' if rt.get('origin') is None else 'conflict_or_placeholder' if rt.get('origin') == '설명 정리 중' else 'learner_projection_present', 'valueSha256': value_hash(rt['origin']) if rt.get('origin') is not None else None},
            'insertion': {'status': 'missing_projection' if rt.get('insertion') is None else 'conflict_or_placeholder' if rt.get('insertion') == '설명 정리 중' else 'learner_projection_present', 'valueSha256': value_hash(rt['insertion']) if rt.get('insertion') is not None else None},
            'fieldEvidenceState': content['fieldDisposition'] if content else None,
            'action': {'status': action_row['actionDisposition'] if action_row else 'no_exact_verified_action_text', 'verifiedActionIds': action_row['verifiedActionIds'] if action_row else []},
            'motorInnervation': relations_by_source.get(key, []),
            'motion': 'source_bound_playable_surface' if key in ready_source_keys else 'no_current_playable_surface',
            'geometryHash': inst['geometryIdentity'].get('evaluatedGeometrySha256'),
            'sideIsNotInferred': True,
            'sourceOnly': inst['sourceOnly'], 'humanReview': inst['humanReview'], 'publicRedistribution': inst['publicRedistribution'],
        })

# Enforce frozen denominators, graph relation symmetry inputs, and conservation policy.
assert (len(t96['targets']), product['denominators']['memberships'], product['denominators']['regions']) == (542, 563, 12)
assert len(targets) == 429 and len(memberships) == 447 and len(concepts) == 232 and len(surfaces) == 462
assert len({r['sourceKey'] for r in surfaces}) == 462
assert len({r['membershipKey'] for r in memberships}) == 447
assert sum(r['motion'] == 'source_bound_playable_surface' for r in surfaces) == 1
assert sum(r['action']['status'] == 'verified_text_available' for r in surfaces) == 10
assert all(r['humanReview'] == 'not_performed' and r['publicRedistribution'] == 'held' for r in surfaces)
assert Counter(r['sourceOnly'] for r in surfaces) == Counter(r['sourceOnly'] for r in source_instances)

counts = {
    'exactTargetScopeOriginInsertionRows': sum(r.get('targetId') is not None for r in source['records']),
    'projectedOriginSurfaces': sum(s['origin']['status'] == 'learner_projection_present' for s in surfaces),
    'originPlaceholderSurfaces': sum(s['origin']['status'] == 'conflict_or_placeholder' for s in surfaces),
    'missingOriginSurfaces': sum(s['origin']['status'] == 'missing_projection' for s in surfaces),
    'projectedInsertionSurfaces': sum(s['insertion']['status'] == 'learner_projection_present' for s in surfaces),
    'originInsertionConflictAttachmentRecords': sum('conflict' in state for c in concepts for state in c['latestAttachmentEvidence']['states']),
    'latestAttachmentEvidenceRecords': sum(c['latestAttachmentEvidence']['records'] for c in concepts),
    'actionVerifiedConcepts': sum(c['actions']['disposition'] == 'verified_text_available' for c in concepts),
    'actionVerifiedSurfaces': sum(s['action']['status'] == 'verified_text_available' for s in surfaces),
    'motorRelationEdges': len(data['nerveGraph']['motorRelations']),
    'motorRelationSurfaces': sum(bool(relations_by_source.get(s['sourceKey'])) for s in surfaces),
    'motionReadySurfaces': sum(s['motion'] == 'source_bound_playable_surface' for s in surfaces),
    'conceptsWithAnyMotionReadySurface': sum(c['motion']['readySurfaceCount'] > 0 for c in concepts),
}
result = {
    'schemaVersion': 't25-all-muscle-content-and-motion-coverage-v1',
    'task': 'T25', 'asOf': '2026-10-02',
    'denominators': {
        'productTargets': 542, 'productMemberships': 563, 'regions': 12,
        'muscleTargets': 429, 'muscleMemberships': 447, 'sourceConcepts': 232, 'sourceSurfaces': 462,
        'existingCanonicalHaBindings': 130, 'historical163': {'total': 163, 'categories': {'6': 6, '20': 20, '135': 135, '2': 2}},
        'workbookRows': 257,
    },
    'policy': {'sourceOnlyStatusPreserved': True, 'humanReview': 'not_performed', 'publicRedistribution': 'held', 'canonicalBindingsCreated': 0, 'geometryCreated': 0, 'sideInferred': False, 'motionTargetedByInitialShortlist': False},
    'inputs': {key: {'path': path, 'sha256': sha(path)} for key, path in INPUTS.items()},
    'counts': counts,
    'nerveLearning': {
        'conceptCount': len(data['nerveGraph']['concepts']),
        'sourceNativeConcepts': [r['key'] for r in data['nerveGraph']['concepts'] if r['sourceNativeEnglishName']],
        'textOnlyConcepts': [r['key'] for r in data['nerveGraph']['concepts'] if not r['sourceNativeEnglishName']],
        'motorRelationEdges': data['nerveGraph']['motorRelations'],
        'sourceNerveGeometryInstances': {'verifiedGeometry': sum((x.get('geometry') or {}).get('assetPath') is not None and x.get('identity') == 'verified_local' for x in data['nerveSupport']['instances']), 'contextOnlyWithoutGeometry': sum((x.get('geometry') or {}).get('assetPath') is None for x in data['nerveSupport']['instances'])},
    },
    'motionAuthoringReadiness': authoring.get('currentReadiness'),
    'targets': targets,
    'memberships': memberships,
    'sourceConcepts': concepts,
    'sourceSurfaces': surfaces,
    'limitations': [
        'A source concept/context target is not an exact target binding; target identity, member completeness, and regional extent remain separate.',
        'A displayed origin/insertion summary is not a coordinate or motion anchor and does not prove exhaustive attachment extent.',
        'Verified motor relations list only the examined relationship; absence from this graph is not proof of absent innervation.',
        'Action text and motion clip readiness are independent; one playable source surface does not represent an entire target or group.',
        'Sensory/proprioception claims are not motor relations and remain unprojected in this task.',
    ],
}
out = Path('work/evidence/T25/all-muscle-content-and-motion-coverage.json')
out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'output':str(out),'denominators':result['denominators'],'counts':counts},ensure_ascii=False,indent=2))
