#!/usr/bin/env python3
"""Add only the four T66 unit-01 short-head pose-observation relations.

Consumes the common author_t66_family_motion output contract. Source-only,
local-use inheritance, public-rights hold and human-review state remain as-is.
The per-family GLB contains the exact family context, but only the repaired
short-head member receives a learner action/asset relation in this unit.
"""
import copy
import json
import shutil
from pathlib import Path

from derive_source_surface_motion import sha
from validate_t66_source_family_helpers import value_hash

ROOT = Path('.')
UNIT = Path('work/evidence/T66/serial-completion-2026-10-02/unit-01')
BASE = Path('atlas-data')
TARGETS = {
    'shoulder-flexion-left': 'ZA-c7010a9-b20b574e456449c5d571c7a1',
    'elbow-flexion-left': 'ZA-c7010a9-b20b574e456449c5d571c7a1',
    'shoulder-flexion-right': 'ZA-c7010a9-a0c2ea00609e874a7faa926d',
    'elbow-flexion-right': 'ZA-c7010a9-a0c2ea00609e874a7faa926d',
}
CASE_DIRS = {
    'shoulder-flexion-left': UNIT / 't66-unit01-source-frame-feasible-short-head-r8/shoulder-flexion-left',
    'shoulder-flexion-right': UNIT / 't66-unit01-source-frame-feasible-short-head-r8/shoulder-flexion-right',
    'elbow-flexion-left': UNIT / 't66-unit01-short-head-sixteen-phase-contact-shape-r3/elbow-flexion-left',
    'elbow-flexion-right': UNIT / 't66-unit01-short-head-sixteen-phase-contact-shape-r3/elbow-flexion-right',
}
PREFIX = 'T66-FAMILY-'


def read(path):
    return json.loads(Path(path).read_text())


def write_json(path, value):
    path = Path(path)
    raw = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()
    if path.exists() and path.read_bytes() == raw:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


def copy_verified(source, destination, expected_sha):
    source = Path(source); destination = Path(destination)
    if sha(source.read_bytes()) != expected_sha:
        raise ValueError(f'source GLB hash mismatch: {source}')
    if destination.exists():
        if sha(destination.read_bytes()) != expected_sha:
            raise ValueError(f'existing destination differs, preserving it: {destination}')
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def verify_candidate(family_id, target_key):
    case = CASE_DIRS[family_id]
    payload = read(case / 'input.json')
    record = read(case / 'authoring-record.json')
    contact = read(case / 'contact-qc.json')
    key_qc = read(case / 'glb-pose-qc.json')
    interp = read(case / 'glb-interpolation-qc.json')
    motion_path = case / 'motion.glb'; reference_path = case / 'reference.glb'
    metric = next((row for row in record['surfaceMetrics'] if row['sourceKey'] == target_key), None)
    if metric is None or payload['family']['id'] != family_id or payload['side'] not in ('left', 'right'):
        raise ValueError(f'candidate identity mismatch: {family_id}')
    if record['rights'] != payload['rights'] or not record['rights'].get('sourceOnly') \
            or record['rights'].get('publicRedistribution') != 'held' \
            or record['rights'].get('humanReview') != 'not_performed':
        raise ValueError(f'candidate authority state changed: {family_id}')
    if contact['failures'] or contact['newContainmentMaximum'] != 0:
        raise ValueError(f'key contact QC failed: {family_id}')
    if not key_qc['passed'] or not interp['passed']:
        raise ValueError(f'emitted GLB replay failed: {family_id}')
    if metric['flips'] != 0 or metric['minimumAreaRatio'] < .1 or metric['contactPins']:
        raise ValueError(f'target geometry or binary pin QC failed: {family_id}')
    if not interp['geometry']['passed'] or not interp['contact']['passed']:
        raise ValueError(f'interpolation substep QC failed: {family_id}')
    if sha(motion_path.read_bytes()) != record['motionSha256'] or sha(reference_path.read_bytes()) != record['restSha256']:
        raise ValueError(f'GLB bytes drifted after authoring: {family_id}')
    source_path = Path('work/evidence/T66/implementation-2026-10-02/contact-production-r6') / family_id / 'input.json'
    return {'familyId': family_id, 'targetSourceKey': target_key, 'payload': payload, 'record': record,
        'contactQcPath': str(case / 'contact-qc.json'), 'keyQcPath': str(case / 'glb-pose-qc.json'),
        'interpolationQcPath': str(case / 'glb-interpolation-qc.json'), 'recordPath': str(case / 'authoring-record.json'),
        'inputPath': str(case / 'input.json'), 'sourceInputPath': str(source_path),
        'motionPath': motion_path, 'referencePath': reference_path,
        'motionSha256': sha(motion_path.read_bytes()), 'referenceSha256': sha(reference_path.read_bytes()),
        'targetMetric': metric, 'interpolation': interp}


def main():
    rows = [verify_candidate(family_id, target) for family_id, target in TARGETS.items()]
    bundle = read(BASE / 'motion/motion-learning.json')
    registry = read(BASE / 'motion/authoring/registry.json')
    scenes = read(BASE / 'motion/motion-scenes.json')
    sources = read(BASE / 'motion/motion-asset-sources.json')
    base_asset = next(row for row in bundle['motionAssets'] if row['id'] == 'T59-ASSET-ZA-R-TIBANT-DF')
    action_ids = {row['id'] for row in bundle['muscleActions']}
    definition_ids = {row['id'] for row in bundle['motionDefinitions']}
    asset_ids = {row['id'] for row in bundle['motionAssets']}
    scene_ids = {row['id'] for row in scenes['sceneManifests']}
    registry_ids = {row['id'] for row in registry['records']}
    registrations = []
    new_actions = []; new_definitions = []; new_assets = []; new_scenes = []; new_records = []
    for result in rows:
        family_id = result['familyId']; target_key = result['targetSourceKey']
        payload, record = result['payload'], result['record']
        family, side = payload['family'], payload['side']
        stem = PREFIX + family_id
        member = next(row for row in record['members'] if row['sourceKey'] == target_key)
        if member['side'] != side or member['role'] != 'deforming_passive_surface':
            raise ValueError(f'exact target member/side mismatch: {family_id}')
        subject_id = f'{stem}-{target_key}'
        action_id = subject_id + '-ACTION'; definition_id = subject_id + '-MOTION'; asset_id = subject_id + '-ASSET'
        scene_id = stem + '-REFERENCE'; author_id = stem + '-AUTHORING'
        if any(v in existing for v, existing in ((action_id, action_ids), (definition_id, definition_ids),
                                                   (asset_id, asset_ids), (scene_id, scene_ids), (author_id, registry_ids))):
            raise ValueError(f'unit-01 registration ID already exists; inspect before modifying: {family_id}')
        context_id = stem + '-POSE-CONTEXT'
        action_value = family['label'] + ' 자세에서 이 표면과 주변 구조의 변화를 관찰합니다.'
        posture_value = '고정된 시작 자세에서 같은 장면의 관절 자세를 따라 표면 변화를 보는 교육용 관찰입니다.'
        context_value = '이 시범은 근육 활성도·수축량·개인의 정상 운동 범위를 계산하지 않습니다.'
        claims = [
            {'id': stem + '-ACTION-FIELD', 'field': 'action', 'appliesTo': 'pose_observation', 'contextId': None, 'value': action_value},
            {'id': stem + '-POSTURE-FIELD', 'field': 'model_posture', 'appliesTo': 'posture_condition', 'contextId': None, 'value': posture_value},
            {'id': stem + '-CONTEXT-FIELD', 'field': 'model_context', 'appliesTo': 'context_role', 'contextId': context_id, 'value': context_value},
        ]
        evidence = {'schemaVersion': 't66-authoring-family-record-v1', 'id': author_id,
            'sourceFamilyId': family_id, 'side': side, 'rights': payload['rights'], 'claims': claims,
            'supportedSubjectKeys': [target_key],
            'movingBoneKeys': [m['sourceKey'] for m in record['members'] if m['role'] == 'moving_structure'],
            'fixedBoneKeys': [m['sourceKey'] for m in record['members'] if m['role'] == 'fixed_structure'],
            'poseRange': {'referencePoseId': family['referencePoseId'], 'endPoseId': stem + '-END',
                'axis': family['axis'], 'pivotMetres': family['pivotMetres'], 'endDegrees': family['endDegrees'],
                'meaning': 'source-frame-derived educational pose observation; not a measured anatomical axis or physiological ROM'},
            'motionSha256': result['motionSha256'], 'restSha256': result['referenceSha256'],
            'measuredAnatomicalAxis': False, 'measuredAttachmentFootprints': False,
            'anatomicalMotorRoleClaimed': False, 'scope': 'exact_short_head_source_surface_pose_observation',
            'geometryRecordPath': result['recordPath'], 'contactQcPath': result['contactQcPath'],
            'glbPoseQcPath': result['keyQcPath'], 'glbInterpolationQcPath': result['interpolationQcPath'],
            'verificationDependencies': []}
        deps = [result['sourceInputPath'], result['inputPath'], result['recordPath'], result['contactQcPath'],
            result['keyQcPath'], result['interpolationQcPath'], str(result['motionPath']), str(result['referencePath'])]
        evidence['verificationDependencies'] = [{'path': p, 'sha256': sha(Path(p).read_bytes())} for p in deps]
        author_path = f'atlas-data/motion/authoring/t66-unit01-{family_id}.json'
        author_raw = (json.dumps(evidence, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()
        if (BASE / 'motion/authoring' / Path(author_path).name).exists():
            raise ValueError(f'authoring evidence already exists; preserving it: {author_path}')
        registry_row = {'id': author_id, 'path': author_path, 'sha256': sha(author_raw)}
        new_records.append((author_path, evidence, registry_row))
        scene = {'id': scene_id, 'revision': base_asset['sourceBinding']['datasetRevision'],
            'modelId': base_asset['staticBinding']['modelId'], 'sourceAssetSha256': result['referenceSha256'],
            'frameId': family['frameId'], 'units': 'm', 'poseId': family['referencePoseId'],
            'assetUri': f'atlas-data/assets/derived-glb/t66-unit01-{family_id}/reference.glb', 'side': side,
            'sourceJoint': 'authored-source-family-not-canonical-joint', 'separateFromNavigationFrame': False,
            'annotationPolicy': {'verifiedBoneLocalBindings': [], 'hideAllSpatialAnnotationsDuringMotion': True}}
        new_scenes.append(scene)
        static = {k: scene[k] for k in ('revision', 'modelId', 'sourceAssetSha256', 'frameId', 'units')}
        static['sceneRevision'] = static.pop('revision'); static.update(sceneId=scene_id, poseId=scene['poseId'])
        refs = [{'layer': 'source_family_record', 'field': claim['field'], 'appliesTo': claim['appliesTo'],
            'contextId': claim['contextId'], 'claimId': claim['id'], 'valueHash': value_hash(claim['value']),
            'evidenceId': author_id, 'fieldEvidenceId': None} for claim in claims]
        action = {'id': action_id, 'subjectKind': 'muscle', 'subjectIds': [], 'sourceSubjectKeys': [target_key],
            'sideApplicability': side, 'jointBindingState': 'source_family_bound', 'sourceFamilyId': family_id,
            'jointBindingNote': 'Exact source-family pose observation; no canonical joint binding or agonist claim.',
            'targetJointIds': [], 'actionLabel': family['label'] + ' 자세에서 관찰', 'explanation': action_value,
            'postureConditions': [posture_value], 'stabilizationConditions': [],
            'stabilizationNote': '주변 고정 문맥을 함께 표시합니다. 근육 활성도와 생리적 운동 범위를 뜻하지 않습니다.',
            'contextRoles': [{'contextId': context_id, 'role': 'unspecified', 'contractionRole': 'unspecified', 'explanation': context_value}],
            'sourceRefs': refs, 'legacyJointActionId': None}
        definition = {'id': definition_id, 'actionId': action_id, 'instanceId': target_key, 'side': side,
            'sourceFamilyId': family_id, 'targetJointIds': [], 'movingStructureIds': evidence['movingBoneKeys'],
            'fixedStructureIds': evidence['fixedBoneKeys'], 'staticReference': static,
            'startPoseId': family['referencePoseId'], 'endPoseId': stem + '-END',
            'poseSourceRefs': [{'layer': 'authoring_record', 'field': 'motion_pose_range', 'appliesTo': 'motion_pose_range',
                'contextId': None, 'claimId': author_id, 'valueHash': value_hash(evidence['poseRange']),
                'evidenceId': author_id, 'fieldEvidenceId': None}]}
        destination = f'atlas-data/assets/motion/t66-unit01-{family_id}/motion.glb'
        reference_destination = scene['assetUri']
        copy_verified(result['motionPath'], destination, result['motionSha256'])
        copy_verified(result['referencePath'], reference_destination, result['referenceSha256'])
        asset = copy.deepcopy(base_asset)
        asset.update(id=asset_id, motionDefinitionId=definition_id, uri=destination,
            sha256=result['motionSha256'], revision='t66-unit01-short-head-r3',
            staticBinding={k: v for k, v in static.items() if k != 'poseId'},
            rig={'id': stem + '-RIG', 'nodeBindings': [{'structureId': m['sourceKey'], 'nodeId': m['nodeId']}
                for m in record['members'] if m['role'] == 'moving_structure']},
            clip={'id': payload['clipId'], 'durationSeconds': family['durationSeconds'],
                'startPoseId': family['referencePoseId'], 'endPoseId': stem + '-END'},
            poseControl={'label': family['label'], 'startDegrees': 0, 'endDegrees': family['endDegrees'],
                'combination': 'single_dof_only'})
        asset['staticBinding'].update(side=side, referencePoseId=family['referencePoseId'])
        asset['sourceBinding'].update(contractVersion='t66-typed-source-motion-v2', subjectKind='muscle',
            sourceFamilyId=family_id, subjectSourceKey=target_key, members=copy.deepcopy(record['members']))
        next(m for m in asset['sourceBinding']['members'] if m['sourceKey'] == target_key)['role'] = 'deforming_muscle_surface'
        new_actions.append(action); new_definitions.append(definition); new_assets.append(asset)
        registrations.append({'familyId': family_id, 'sourceKey': target_key, 'side': side,
            'subjectKind': 'muscle', 'scope': 'exact_source_surface_pose_observation',
            'actionId': action_id, 'motionDefinitionId': definition_id, 'assetId': asset_id,
            'motionGlbSha256': result['motionSha256'], 'referenceGlbSha256': result['referenceSha256'],
            'interpolationQcPath': result['interpolationQcPath'], 'status': 'registered_local_source_observation'})
    bundle['muscleActions'].extend(new_actions)
    bundle['motionDefinitions'].extend(new_definitions)
    bundle['motionAssets'].extend(new_assets)
    bundle['revision'] = 't66-unit01-short-head-r3'
    registry['records'].extend(row[2] for row in new_records)
    scenes['sceneManifests'].extend(new_scenes)
    scenes['revision'] = 't66-unit01-short-head-r3'
    sources['productionMotionAssetIds'].extend(row['id'] for row in new_assets)
    if len(sources['productionMotionAssetIds']) != len(set(sources['productionMotionAssetIds'])):
        raise ValueError('duplicate production motion asset identity')
    for path, evidence, _ in new_records: write_json(path, evidence)
    write_json(BASE / 'motion/motion-learning.json', bundle)
    write_json(BASE / 'motion/authoring/registry.json', registry)
    write_json(BASE / 'motion/motion-scenes.json', scenes)
    write_json(BASE / 'motion/motion-asset-sources.json', sources)
    write_json(UNIT / 'source-family-registration.json', {
        'schemaVersion': 't66-unit01-short-head-registration-v1', 'families': registrations,
        'addedLearnerActions': len(new_actions), 'addedDefinitions': len(new_definitions),
        'addedMotionAssets': len(new_assets), 'sameSceneRenderer': True,
        'canonicalBindingsCreated': False, 'anatomicalMotorRolesClaimed': False,
        'sourceOnly': True, 'localUseRights': 'inherits_pinned_source_decision',
        'publicRedistribution': 'held', 'humanReview': 'not_performed'})
    print(json.dumps({'registered': len(registrations), 'actions': len(new_actions),
        'definitions': len(new_definitions), 'assets': len(new_assets)}))


if __name__ == '__main__':
    main()
