#!/usr/bin/env python3
"""Idempotently register the source-bound T24 demonstration, never alter T44 originals."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / 'atlas-data/catalog/canonical-catalog.json'
BUNDLE = ROOT / 'atlas-data/motion/motion-learning.json'
SOURCES = ROOT / 'atlas-data/motion/motion-asset-sources.json'
SCENES = ROOT / 'atlas-data/motion/motion-scenes.json'
CLIP_MANIFEST = ROOT / 'atlas-data/assets/motion/t24-right-tibialis-anterior/ankle-dorsiflexion.json'
JOINT = 'HA-S-JOINT-R-ANKLE-TALOCRURAL'
TALUS = 'HA-S-TALUS'
ACTION = 'T24-ACTION-HA-M-000003-R-ANKLE-DF'
DEFINITION = 'HA-MOTION-T24-R-TIBANT-ANKLE-DF'
ASSET = 'HA-ASSET-T24-R-TIBANT-ANKLE-DF-V1'
SCENE = 'HA-SCENE-OSIM-GAIT2392-R-ANKLE-T44'
POSE0 = 'HA-POSE-OSIM-R-ANKLE-Q0'
POSE1 = 'HA-POSE-OSIM-R-ANKLE-Q012'
CLAIM = 'HA-C-T24-R-ANKLE-DEMO-POSE'


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def write(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def hash_value(value: object) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def upsert(rows: list[dict], item: dict) -> None:
    old = next((i for i, row in enumerate(rows) if row['id'] == item['id']), None)
    if old is None:
        rows.append(item)
    elif rows[old] != item:
        raise ValueError(f'Existing registration changed: {item["id"]}')


def main() -> None:
    catalog, bundle, sources, clip = map(read, (CATALOG, BUNDLE, SOURCES, CLIP_MANIFEST))
    e = catalog['entities']
    assert clip['sourceStaticSha256'] == 'a33f043be46c7b628bc649777e190c9e7d7cba345f07795e080820545261bed0'
    assert [row['id'] for row in bundle['motionAssets']] in ([], [ASSET])
    upsert(e['sources'], {
        'id': 'KMLE-TALUS-TERMINOLOGY-T24', 'title': 'KMLE Korean medical terminology: talus',
        'authors': ['KMLE'], 'edition': 'KMLE terminology lookup, talus entry', 'year': None,
        'urlOrLocalRef': 'https://m.kmle.co.kr/search.php?Page=1&Search=talus&SpecialSearch=DictKma',
        'accessDate': '2026-09-27',
        'license': {'id': 'LIC-KMLE-TERM-INTERNAL-UNRESOLVED', 'name': 'Reuse terms unverified; internal terminology reference only',
                    'spdxId': None, 'allowedUses': ['internal'], 'attributionRequired': True,
                    'attributionText': 'KMLE talus terminology lookup, accessed 2026-09-27.',
                    'derivativesAllowed': False, 'redistributionAllowed': False},
    })
    upsert(e['evidence'], {'id': 'EV-T24-KMLE-TALUS-TERMS', 'sourceId': 'KMLE-TALUS-TERMINOLOGY-T24',
                           'locator': 'talus: 목말뼈, 거골; terminology only; no mapping to BodyParts3D FJ3385',
                           'supportedClaimIds': [], 'evidenceKind': 'secondary'})
    upsert(e['structures'], {'id': TALUS, 'kind': 'bone', 'termIds': ['HA-T-T24-TALUS-KO', 'HA-T-T24-TALUS-HANJA', 'HA-T-T24-TALUS-EN']})
    for id_, text, language, script in [
        ('HA-T-T24-TALUS-KO', '목말뼈', 'ko', 'Hang'),
        ('HA-T-T24-TALUS-HANJA', '거골', 'ko', 'Hang'),
        ('HA-T-T24-TALUS-EN', 'Talus', 'en', 'Latn'),
    ]:
        upsert(e['terms'], {'id': id_, 'conceptId': TALUS, 'language': language, 'script': script,
                            'text': text, 'termRole': 'preferred' if id_.endswith('KO') else 'synonym',
                            'edition': 'KMLE talus terminology lookup / OpenSim talus_r model',
                            'evidenceIds': ['EV-T24-KMLE-TALUS-TERMS'] if language == 'ko' else ['EV-T44-OSIM-ANKLE-R'],
                            'reviewState': 'needs_review'})
    value = {
        'sourceCoordinate': 'OpenSim Gait2392 ankle_angle_r', 'sourceRestRadians': 0,
        'illustrativeSamplesRadians': [0, 0.06, 0.12], 'durationSeconds': 2,
        'meaning': 'T24 author-selected positive direction demonstration within the source joint coordinate; not clinical normal range, measured force or observed human movement',
    }
    upsert(e['claims'], {'id': CLAIM, 'subjectId': JOINT, 'field': 'motion_pose_range', 'value': value,
                         'evidenceIds': ['EV-T44-OSIM-ANKLE-R'], 'attribution': 'ai_interpretation',
                         'reviewState': 'needs_review'})
    catalog['revision'] = 'T24-2026-09-27-motion-pose-v1'
    ref = {'sceneId': SCENE, 'sceneRevision': 'T44-rest-v1', 'modelId': 'HA-MODEL-OSIM-GAIT2392-R-ANKLE',
           'sourceAssetSha256': clip['sourceStaticSha256'],
           'frameId': 'HA_OSIM_GAIT2392_TIBIA_LOCAL_XLEFT_YHEAD_ZANTERIOR_M', 'units': 'm', 'poseId': POSE0}
    scenes = {'schemaVersion': '1.0.0', 'revision': 'T24-2026-09-27-v1', 'sceneManifests': [{
        'id': SCENE, 'revision': ref['sceneRevision'], 'modelId': ref['modelId'],
        'sourceAssetSha256': ref['sourceAssetSha256'], 'frameId': ref['frameId'],
        'units': 'm', 'poseId': POSE0, 'assetUri': clip['sourceStaticGlb'],
        'side': 'right', 'sourceJoint': 'ankle_r',
        'separateFromNavigationFrame': True,
        'annotationPolicy': clip['annotationPolicy'],
    }]}
    original = next(row for row in bundle['muscleActions'] if row['id'] == 'T21-ACTION-HA-M-000003')
    action = copy.deepcopy(original)
    action.update({'id': ACTION, 'sideApplicability': 'right', 'jointBindingState': 'canonical_bound',
                   'jointBindingNote': None,
                   'targetJointIds': [JOINT], 'actionLabel': '오른쪽 발목 등쪽굽힘',
                   'explanation': '앞정강근은 오른쪽 발목을 등쪽으로 굽히는 데 관여합니다. 이 시범은 발과 발목의 작용 방향을 보여 주며, 한 근육이 움직임 전체를 단독으로 만든다는 뜻은 아닙니다.',
                   'legacyJointActionId': 'HA-JA-T44-R-TIBANT-ANKLE-DF'})
    upsert(bundle['muscleActions'], action)
    pose_ref = {'layer': 'canonical_claim', 'field': 'motion_pose_range', 'appliesTo': 'motion_pose_range',
                'contextId': None, 'claimId': CLAIM, 'valueHash': hash_value(value),
                'evidenceId': 'EV-T44-OSIM-ANKLE-R', 'fieldEvidenceId': None}
    upsert(bundle['motionDefinitions'], {
        'id': DEFINITION, 'actionId': ACTION, 'instanceId': 'HA-I-R-HA-M-000003', 'side': 'right',
        'targetJointIds': [JOINT], 'movingStructureIds': [TALUS], 'fixedStructureIds': ['HA-S-TIBIA'],
        'staticReference': ref, 'startPoseId': POSE0, 'endPoseId': POSE1,
        'poseSourceRefs': [pose_ref],
    })
    upsert(bundle['motionAssets'], {
        'id': ASSET, 'motionDefinitionId': DEFINITION, 'uri': clip['outputGlb'],
        'revision': 'T24-2026-09-27-v1', 'sha256': clip['outputSha256'],
        'sourceId': 'OPENSIM_GAIT2392_T44', 'licenseId': 'LIC-OPENSIM-GAIT2392-CC-BY-3.0',
        'representationType': 'bone_motion_with_illustrative_path',
        'staticBinding': {**{k: v for k, v in ref.items() if k != 'poseId'}, 'side': 'right', 'referencePoseId': POSE0},
        'rig': {'id': 'HA-RIG-T24-ANKLE-R', 'nodeBindings': [{'structureId': TALUS, 'nodeId': 'ankle_r_pivot_q0'}]},
        'illustration': {'id': 'HA-PATH-T24-TIBANT-R', 'trajectoryBindings': [
            {'structureId': 'HA-M-000003', 'trajectoryId': 'tib_ant_r_model_path_q0'}]},
        'clip': {'id': clip['clipId'], 'durationSeconds': 2.0, 'startPoseId': POSE0, 'endPoseId': POSE1},
        'technicalStatus': 'candidate',
    })
    bundle['revision'] = 'T24-2026-09-27-right-ankle-demo-v1'
    ids = sources['productionMotionAssetIds']
    if ids not in ([], [ASSET]):
        raise ValueError('Unexpected production asset registry contents')
    sources['productionMotionAssetIds'] = [ASSET]
    sources['revision'] = 'T24-2026-09-27-motion-assets-v1'
    for path, obj in ((CATALOG, catalog), (BUNDLE, bundle), (SOURCES, sources), (SCENES, scenes)):
        write(path, obj)


if __name__ == '__main__':
    main()
