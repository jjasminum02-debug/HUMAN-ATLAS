#!/usr/bin/env python3
"""Register every passing source-family package as scoped pose observation.

Source-surface pose observation does not assert agonist activation, normal ROM,
whole-muscle extent or a canonical joint identity. Full target and source queues
remain independent. The retained candidates need representative scene QA too.
"""
import copy
import json
import shutil
from author_source_surface_motion import ROOT, RIGHTS, read, dump
from derive_source_surface_motion import sha
from validate_t66_source_family_helpers import value_hash

BASE = 'work/evidence/T66/implementation-2026-10-02'
PREFIX = 'T66-FAMILY-'

def register():
    production = {r['id']: r for r in read(BASE + '/contact-production-r6/production.json')}
    production.update({r['id']: r for r in read(BASE + '/rotation-direction-r7/production.json')})
    production.update({r['id']: r for r in read(BASE + '/signed-trs-r13/production.json')})
    bundle = read('atlas-data/motion/motion-learning.json')
    base = next(a for a in bundle['motionAssets'] if a['id'] == 'T59-ASSET-ZA-R-TIBANT-DF')
    registry = read('atlas-data/motion/authoring/registry.json')
    scenes = read('atlas-data/motion/motion-scenes.json')
    for group in ('muscleActions', 'motionDefinitions', 'motionAssets'):
        bundle[group] = [r for r in bundle[group] if not r['id'].startswith(PREFIX)]
    registry['records'] = [r for r in registry['records'] if not r['id'].startswith(PREFIX)]
    scenes['sceneManifests'] = [r for r in scenes['sceneManifests'] if not r['id'].startswith(PREFIX)]
    registrations = []
    for family_id, result in production.items():
        if result['status'] != 'candidate_geometry_contact_pass':
            continue
        payload = read(result['inputPath'])
        record = read(result['recordPath'])
        qc = read(result['qcPath'])
        if qc['failures'] or any(m['flips'] or m['minimumAreaRatio'] < .1 for m in record['surfaceMetrics']):
            raise ValueError('Rejected source geometry cannot register')
        family, side = payload['family'], payload['side']
        stem = PREFIX + family_id
        members = record['members']
        moving = [m for m in members if m['role'] == 'moving_structure']
        fixed = [m for m in members if m['role'] == 'fixed_structure']
        deforming = [m for m in members if m['role'] == 'deforming_passive_surface']
        subjects = moving + deforming
        destination = 'atlas-data/assets/motion/t66-' + family_id + '/motion.glb'
        reference = 'atlas-data/assets/derived-glb/t66-' + family_id + '/reference.glb'
        source_dir = (ROOT / result['recordPath']).parent
        for source_name, dest in [('motion.glb', destination), ('reference.glb', reference)]:
            target = ROOT / dest
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_dir / source_name, target)
        motion_sha, rest_sha = sha((ROOT / destination).read_bytes()), sha((ROOT / reference).read_bytes())
        end_pose = stem + '-END'
        context_id = stem + '-POSE-CONTEXT'
        action_value = family['label'] + '의 교육용 자세에서 선택한 표면과 주변 구조의 변화를 관찰합니다.'
        posture_value = '현재 모형의 기본 자세에서 시작하는 단일 관절 조절 시범입니다.'
        context_value = '표면의 자세 변화와 주변 뼈의 공동 이동을 보여 줍니다. 개별 근육의 활성도나 수축량은 계산하지 않습니다.'
        claims = [{'id': stem + '-ACTION-FIELD', 'field': 'action', 'appliesTo': 'action_explanation', 'contextId': None, 'value': action_value},
            {'id': stem + '-POSTURE-FIELD', 'field': 'model_posture', 'appliesTo': 'posture_condition', 'contextId': None, 'value': posture_value},
            {'id': stem + '-CONTEXT-FIELD', 'field': 'model_context', 'appliesTo': 'context_role', 'contextId': context_id, 'value': context_value}]
        deps = [result['inputPath'], result['recordPath'], result['qcPath'], result['glbQcPath'], destination, reference]
        adoption = {'schemaVersion': 't66-authoring-family-record-v1', 'id': stem + '-AUTHORING',
            'sourceFamilyId': family_id, 'side': side, 'rights': RIGHTS, 'claims': claims,
            'supportedSubjectKeys': [m['sourceKey'] for m in subjects],
            'movingBoneKeys': [m['sourceKey'] for m in moving], 'fixedBoneKeys': [m['sourceKey'] for m in fixed],
            'poseRange': {'referencePoseId': family['referencePoseId'], 'endPoseId': end_pose,
                'axis': family['axis'], 'pivotMetres': family['pivotMetres'], 'endDegrees': family['endDegrees'],
                'meaning': 'authored educational pose; not source measured axis or physiological normal ROM'},
            'motionSha256': motion_sha, 'restSha256': rest_sha, 'measuredAnatomicalAxis': False,
            'qualitativeDirectionEvidence': family['qualitativeEvidence'],
            'anatomicalMotorRoleClaimed': False, 'scope': 'exact_source_surface_pose_observation',
            'geometryRecordPath': result['recordPath'], 'contactQcPath': result['qcPath'],
            'glbPoseQcPath': result['glbQcPath'],
            'verificationDependencies': [{'path': p, 'sha256': sha((ROOT / p).read_bytes())} for p in deps]}
        author_path = 'atlas-data/motion/authoring/t66-' + family_id + '.json'
        dump(author_path, adoption)
        registry['records'].append({'id': adoption['id'], 'path': author_path, 'sha256': sha((ROOT / author_path).read_bytes())})
        scene = {'id': stem + '-REFERENCE', 'revision': base['sourceBinding']['datasetRevision'],
            'modelId': base['staticBinding']['modelId'], 'sourceAssetSha256': rest_sha,
            'frameId': family['frameId'], 'units': 'm', 'poseId': family['referencePoseId'], 'assetUri': reference,
            'side': side, 'sourceJoint': 'authored-source-family-not-canonical-joint', 'separateFromNavigationFrame': False,
            'annotationPolicy': {'verifiedBoneLocalBindings': [], 'hideAllSpatialAnnotationsDuringMotion': True}}
        scenes['sceneManifests'].append(scene)
        static = {k: scene[k] for k in ('revision', 'modelId', 'sourceAssetSha256', 'frameId', 'units')}
        static['sceneRevision'] = static.pop('revision')
        static.update(sceneId=scene['id'], poseId=scene['poseId'])
        for subject in subjects:
            kind = 'bone' if subject['role'] == 'moving_structure' else 'muscle'
            key = subject['sourceKey']
            ident = stem + '-' + key
            refs = [{'layer': 'source_family_record', 'field': c['field'], 'appliesTo': c['appliesTo'],
                'contextId': c['contextId'], 'claimId': c['id'], 'valueHash': value_hash(c['value']),
                'evidenceId': adoption['id'], 'fieldEvidenceId': None} for c in claims[:1] if kind == 'bone']
            if kind == 'muscle':
                refs = [{'layer': 'source_family_record', 'field': c['field'], 'appliesTo': c['appliesTo'],
                    'contextId': c['contextId'], 'claimId': c['id'], 'valueHash': value_hash(c['value']),
                    'evidenceId': adoption['id'], 'fieldEvidenceId': None} for c in claims]
            action = {'id': ident + '-ACTION', 'subjectKind': kind, 'subjectIds': [], 'sourceSubjectKeys': [key],
                'sideApplicability': side, 'jointBindingState': 'source_family_bound', 'sourceFamilyId': family_id,
                'jointBindingNote': 'Exact source family pose observation; no canonical joint binding created', 'targetJointIds': [],
                'actionLabel': family['label'] + ' 자세에서 관찰', 'explanation': action_value,
                'postureConditions': [posture_value] if kind == 'muscle' else [], 'stabilizationConditions': [],
                'stabilizationNote': '주변 고정 문맥을 유지한 교육용 자세입니다. 개인의 정상 운동 범위를 나타내지 않습니다.',
                'contextRoles': [{'contextId': context_id, 'role': 'unspecified', 'contractionRole': 'unspecified', 'explanation': context_value}] if kind == 'muscle' else [],
                'sourceRefs': refs, 'legacyJointActionId': None}
            definition = {'id': ident + '-MOTION', 'actionId': action['id'], 'instanceId': key, 'side': side,
                'sourceFamilyId': family_id, 'targetJointIds': [], 'movingStructureIds': adoption['movingBoneKeys'],
                'fixedStructureIds': adoption['fixedBoneKeys'], 'staticReference': static,
                'startPoseId': family['referencePoseId'], 'endPoseId': end_pose,
                'poseSourceRefs': [{'layer': 'authoring_record', 'field': 'motion_pose_range', 'appliesTo': 'motion_pose_range',
                    'contextId': None, 'claimId': adoption['id'], 'valueHash': value_hash(adoption['poseRange']),
                    'evidenceId': adoption['id'], 'fieldEvidenceId': None}]}
            asset = copy.deepcopy(base)
            asset.update(id=ident + '-ASSET', motionDefinitionId=definition['id'], uri=destination,
                sha256=motion_sha, revision='t66-source-family-signed-trs-r13',
                staticBinding={k: v for k, v in static.items() if k != 'poseId'},
                rig={'id': stem + '-RIG', 'nodeBindings': [{'structureId': m['sourceKey'], 'nodeId': m['nodeId']} for m in moving]},
                clip={'id': payload['clipId'], 'durationSeconds': family['durationSeconds'], 'startPoseId': family['referencePoseId'], 'endPoseId': end_pose},
                poseControl={'label': family['label'], 'startDegrees': 0, 'endDegrees': family['endDegrees'], 'combination': 'single_dof_only'})
            asset['staticBinding'].update(side=side, referencePoseId=family['referencePoseId'])
            asset['sourceBinding'].update(contractVersion='t66-typed-source-motion-v2', subjectKind=kind,
                sourceFamilyId=family_id, subjectSourceKey=key, members=copy.deepcopy(members))
            if kind == 'muscle':
                next(m for m in asset['sourceBinding']['members'] if m['sourceKey'] == key)['role'] = 'deforming_muscle_surface'
            bundle['muscleActions'].append(action)
            bundle['motionDefinitions'].append(definition)
            bundle['motionAssets'].append(asset)
            registrations.append({'familyId': family_id, 'sourceKey': key, 'subjectKind': kind,
                'scope': 'exact_source_surface_pose_observation', 'assetId': asset['id'], 'geometryQc': result['qcPath'], 'actualUI': 'pending'})
    bundle['revision'] = 't66-source-family-pose-observation-r7'
    dump('atlas-data/motion/motion-learning.json', bundle)
    dump('atlas-data/motion/authoring/registry.json', registry)
    dump('atlas-data/motion/motion-scenes.json', scenes)
    sources = read('atlas-data/motion/motion-asset-sources.json')
    sources['productionMotionAssetIds'] = [a['id'] for a in bundle['motionAssets']]
    dump('atlas-data/motion/motion-asset-sources.json', sources)
    dump(BASE + '/source-family-registrations-r7.json', {'rows': registrations,
        'normalPhysiologicalROMApproved': False, 'canonicalBindingCreated': False, 'anatomicalMotorRolesInferred': False})
    print(json.dumps({'families': len({r['familyId'] for r in registrations}), 'registeredSourceFamilySelectors': len(registrations),
        'musclePoseObservations': len([r for r in registrations if r['subjectKind'] == 'muscle']),
        'boneFamilyBindings': len([r for r in registrations if r['subjectKind'] == 'bone'])}))

if __name__ == '__main__':
    register()
