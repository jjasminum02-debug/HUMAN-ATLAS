#!/usr/bin/env python3
"""Replay registered, corrected unit-01 GLBs against source-frame trajectories.

Rigid bones/context are compared exactly. The one intentionally deforming short-
head surface is checked by the same-hash, actual-GLB interpolation geometry and
contact QC rather than incorrectly requiring its corrected shape to remain rigid.
"""
import hashlib
import json
import sys
from pathlib import Path
import numpy as np

ROOT = Path('.')
UNIT = Path('work/evidence/T66/serial-completion-2026-10-02/unit-01')
sys.path.insert(0, 'work/tools')
sys.path.insert(0, str(UNIT))
from author_t66_family_motion import rotation
from author_source_surface_motion import source_geometry, read as read_source
from derive_source_surface_motion import sha
from verify_t66_glb_pose import verify_glb

FAMILIES = {
    'shoulder-flexion-left': ('t66-unit01-shoulder-flexion-contact-r3/shoulder-flexion-left/input.json',
        'source-frame-exact-r4/shoulder-flexion-left/motion.glb',
        'atlas-data/motion/authoring/t66-unit01-shoulder-flexion-left-source-frame-r4.json',
        'ZA-c7010a9-b20b574e456449c5d571c7a1'),
    'shoulder-flexion-right': ('t66-unit01-shoulder-flexion-contact-r3/shoulder-flexion-right/input.json',
        'source-frame-exact-r4/shoulder-flexion-right/motion.glb',
        'atlas-data/motion/authoring/t66-unit01-shoulder-flexion-right-source-frame-r4.json',
        'ZA-c7010a9-a0c2ea00609e874a7faa926d'),
    'elbow-flexion-left': ('t66-unit01-short-head-triangle-seed-corrective-r32/elbow-flexion-left/input.json',
        'source-frame-exact-r4/elbow-flexion-left/motion.glb',
        'atlas-data/motion/authoring/t66-unit01-elbow-flexion-left-source-frame-r4.json',
        'ZA-c7010a9-b20b574e456449c5d571c7a1'),
    'elbow-flexion-right': ('t66-unit01-short-head-triangle-seed-corrective-r33/elbow-flexion-right/input.json',
        'source-frame-exact-r4/elbow-flexion-right/motion.glb',
        'atlas-data/motion/authoring/t66-unit01-elbow-flexion-right-source-frame-r4.json',
        'ZA-c7010a9-a0c2ea00609e874a7faa926d'),
}


def read(path):
    return json.loads(Path(path).read_text())


def digest(data):
    return sha(data)


def source_frame_references(payload):
    """Rebuild rigid expected poses from pinned source geometry without rerunning deformation optimization."""
    manifest_path = Path(payload['dataset']['path'])
    if digest(manifest_path.read_bytes()) != payload['dataset']['sha256']:
        raise ValueError('Pinned source manifest drifted')
    manifest = read_source(str(manifest_path))
    source_rows = {row['sourceKey']: row for row in manifest['instances']}
    family = payload['family']; samples = int(family['samples'])
    axis = np.asarray(family['axis'], dtype=float); pivot = np.asarray(family['pivotMetres'], dtype=float)
    frames = {}
    for member in payload['members']:
        key = member['sourceKey']
        row = source_rows.get(key)
        if row is None:
            raise ValueError(f'Pinned source member missing: {key}')
        if row.get('sourceLabelSide') not in [payload['side'], None]:
            raise ValueError(f'Source side conflicts with authoring family: {key}')
        *_, triangles, _, world = source_geometry(row, member['lod'])
        if member['role'] in ('moving_structure', 'co_moving_context'):
            poses = []
            for step in range(samples + 1):
                R = rotation(axis, np.radians(float(family['endDegrees'])) * step / samples)
                poses.append((world - pivot) @ R.T + pivot)
        else:
            poses = [world] * (samples + 1)
        frames[key] = (poses, triangles)
    return frames


def save_new(path, payload):
    path = Path(path)
    raw = (json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()
    if path.exists():
        if path.read_bytes() != raw:
            raise ValueError(f'Final pose evidence already differs; preserve it and create a new revision: {path}')
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


def main():
    registry_path = Path('atlas-data/motion/authoring/registry.json')
    registry = read(registry_path)
    registry_by_id = {row['id']: row for row in registry['records']}
    summaries = []
    for family_id, (input_rel, motion_rel, record_rel, target_key) in FAMILIES.items():
        payload = read(UNIT / input_rel)
        if payload['family']['id'] != family_id or payload['side'] not in family_id:
            raise ValueError(f'Pinned family/side differs: {family_id}')
        motion_path = UNIT / motion_rel
        interpolation_path = motion_path.parent / 'glb-interpolation-qc.json'
        interpolation = read(interpolation_path)
        record_path = Path(record_rel)
        record = read(record_path)
        if record.get('sourceFamilyId') != family_id or record.get('side') != payload['side'] or record.get('supportedSubjectKeys') != [target_key]:
            raise ValueError(f'Registered source identity/side/scope differs: {family_id}')
        if interpolation.get('motionGlbSha256') != digest(motion_path.read_bytes()) or interpolation.get('targetSourceKey') != target_key:
            raise ValueError(f'Interpolation evidence does not bind the emitted GLB/source: {family_id}')
        if interpolation.get('passed') is not True or interpolation.get('geometry', {}).get('passed') is not True or interpolation.get('contact', {}).get('passed') is not True:
            raise ValueError(f'Emitted GLB geometry/contact interpolation failed: {family_id}')
        record['motionSha256'] = digest(motion_path.read_bytes())
        record['glbInterpolationQcPath'] = str(interpolation_path)
        record['motionAssetRevision'] = 't66-unit01-source-frame-exact-r4'
        frames = source_frame_references(payload)
        pose_qc = verify_glb(motion_path, payload, frames, deformation_source_keys={target_key})
        target_row = next((row for row in pose_qc['rows'] if row['sourceKey'] == target_key), None)
        if target_row is None or target_row.get('sourceFrameComparison') != 'authored_surface_deformation' or not target_row.get('requiresGeometryQc'):
            raise ValueError(f'Target deformation comparison was not marked explicitly: {family_id}')
        target_row.pop('maximumWorldErrorMetres', None)
        target_row.update(passed=True, geometryQcPath=str(interpolation_path), geometryQcSha256=digest(interpolation_path.read_bytes()))
        rigid_rows = [row for row in pose_qc['rows'] if row['sourceKey'] != target_key]
        if not rigid_rows or any(row.get('passed') is not True or row.get('maximumWorldErrorMetres', float('inf')) > 1e-6 for row in rigid_rows):
            raise ValueError(f'Rigid source-frame replay failed: {family_id}')
        pose_qc['passed'] = all(row.get('passed') is True for row in pose_qc['rows'])
        pose_qc['sourceFrameScope'] = 'all rigid bones and co-moving source context compared to authored source-frame trajectories; exact short-head target surface is intentionally deforming and validated by the linked emitted-GLB interpolation geometry/contact QC'
        pose_qc['anatomicalApproval'] = False
        if not pose_qc['passed']:
            raise ValueError(f'Final source-frame/morph geometry replay failed: {family_id}')
        final_qc_path = motion_path.parent / 'final-glb-pose-qc.json'
        save_new(final_qc_path, pose_qc)

        record.setdefault('candidateGlbPoseQcPath', record.get('glbPoseQcPath'))
        record['glbPoseQcPath'] = str(final_qc_path)
        deps = {row['path']: row for row in record.get('verificationDependencies', [])}
        deps[str(final_qc_path)] = {'path': str(final_qc_path), 'sha256': digest(final_qc_path.read_bytes())}
        deps[str(interpolation_path)] = {'path': str(interpolation_path), 'sha256': digest(interpolation_path.read_bytes())}
        record['verificationDependencies'] = list(deps.values())
        raw_record = (json.dumps(record, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()
        record_path.write_bytes(raw_record)
        record_id = record['id']
        if record_id not in registry_by_id:
            raise ValueError(f'Authoring registry row missing: {record_id}')
        registry_by_id[record_id]['sha256'] = digest(raw_record)
        summaries.append({'familyId': family_id, 'side': payload['side'], 'sourceKey': target_key,
            'motionGlbPath': str(motion_path), 'motionGlbSha256': pose_qc['motionSha256'],
            'poseQcPath': str(final_qc_path), 'poseQcSha256': digest(final_qc_path.read_bytes()),
            'testedKeys': pose_qc['testedKeys'], 'rigidSourceFrameRows': len(rigid_rows),
            'maximumRigidSourceFrameErrorMetres': max(row['maximumWorldErrorMetres'] for row in rigid_rows),
            'targetRigidCounterfactualDifferenceMetres': target_row['rigidCounterfactualDifferenceMetres'],
            'interpolationQcPath': str(interpolation_path), 'interpolationQcSha256': digest(interpolation_path.read_bytes()),
            'passed': pose_qc['passed'], 'anatomicalApproval': False})
    raw_registry = (json.dumps(registry, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()
    registry_path.write_bytes(raw_registry)
    summary = {'schemaVersion': 't66-unit01-final-glb-source-frame-validation-v1', 'candidateCount': len(summaries),
        'passedCount': sum(row['passed'] for row in summaries), 'results': summaries,
        'meaning': 'Rigid source context is compared at all authored keys; target muscle corrective is separately bound to same-hash, actual emitted GLB geometry/contact interpolation QC. This is source-local pose observation, not measured anatomy or human approval.'}
    save_new(UNIT / 'final-glb-source-frame-validation-r4.json', summary)
    print(json.dumps({'candidateCount': summary['candidateCount'], 'passedCount': summary['passedCount'], 'maxRigidErrorMetres': max(row['maximumRigidSourceFrameErrorMetres'] for row in summaries)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
