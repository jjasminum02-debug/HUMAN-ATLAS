#!/usr/bin/env python3
"""Adopt the unit-01 exact source-frame rigid-track GLBs in the existing scene registry."""
from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path

from derive_source_surface_motion import sha

ROOT = Path(__file__).resolve().parents[2]
UNIT = Path('work/evidence/T66/serial-completion-2026-10-02/unit-01')
REVISION = 't66-unit01-source-frame-exact-r4'
FAMILIES = {
    'shoulder-flexion-left': 't66-unit01-shoulder-flexion-contact-r3/shoulder-flexion-left/input.json',
    'shoulder-flexion-right': 't66-unit01-shoulder-flexion-contact-r3/shoulder-flexion-right/input.json',
    'elbow-flexion-left': 't66-unit01-short-head-triangle-seed-corrective-r32/elbow-flexion-left/input.json',
    'elbow-flexion-right': 't66-unit01-short-head-triangle-seed-corrective-r33/elbow-flexion-right/input.json',
}


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value, replace_owned=False):
    path = Path(path)
    raw = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()
    if path.exists() and path.read_bytes() != raw and not replace_owned:
        raise ValueError(f'preserving existing nonmatching file: {path}')
    if not path.exists() or replace_owned:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)


def copy_hash(source, destination, expected_hash):
    source = Path(source); destination = Path(destination)
    if sha(source.read_bytes()) != expected_hash:
        raise ValueError(f'new revision GLB hash mismatch: {source}')
    if destination.exists():
        if sha(destination.read_bytes()) != expected_hash:
            raise ValueError(f'preserving existing nonmatching asset: {destination}')
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def main():
    bundle_path = Path('atlas-data/motion/motion-learning.json')
    registry_path = Path('atlas-data/motion/authoring/registry.json')
    bundle = read(bundle_path); registry = read(registry_path)
    assets_by_id = {row['id']: row for row in bundle['motionAssets']}
    registry_by_id = {row['id']: row for row in registry['records']}
    results = []
    for family, input_rel in FAMILIES.items():
        case_input = read(UNIT / input_rel)
        unit_record_path = UNIT / 'source-frame-exact-r4' / family / 'rigid-trajectory-qc.json'
        interp_path = UNIT / 'source-frame-exact-r4' / family / 'glb-interpolation-qc.json'
        pose_path = UNIT / 'source-frame-exact-r4' / family / 'final-glb-pose-qc.json'
        unit_record = read(unit_record_path)
        interp = read(interp_path)
        if not interp.get('passed') or not interp.get('geometry', {}).get('passed') or not interp.get('contact', {}).get('passed'):
            raise ValueError(f'final geometry/contact interpolation QC failed: {family}')
        if unit_record['familyId'] != family or unit_record['side'] != case_input['side']:
            raise ValueError(f'family/side mismatch: {family}')
        if unit_record['outputGlbSha256'] != interp['motionGlbSha256']:
            raise ValueError(f'rigid track and interpolation QC hashes differ: {family}')
        if not pose_path.is_file():
            # Created immediately by refresh_final_glb_pose_qc.py after registration.
            pass

        asset_id = f'T66-FAMILY-{family}-{case_input["unitTargetSourceKey"]}-ASSET'
        record_id = f'T66-FAMILY-{family}-AUTHORING'
        asset = assets_by_id[asset_id]
        registry_entry = registry_by_id[record_id]
        current_record_path = Path(registry_entry['path'])
        current_record = read(current_record_path)
        record_revision_path = Path(f'atlas-data/motion/authoring/t66-unit01-{family}-source-frame-r4.json')
        target_uri = f'atlas-data/assets/motion/t66-unit01-{family}-source-frame-r4/motion.glb'
        source_glb = UNIT / 'source-frame-exact-r4' / family / 'motion.glb'
        glb_hash = unit_record['outputGlbSha256']

        if current_record_path == record_revision_path:
            if current_record.get('motionSha256') != glb_hash or asset.get('sha256') != glb_hash or asset.get('uri') != target_uri:
                raise ValueError(f'already adopted revision differs; preserving current state: {family}')
            record = current_record
        else:
            if asset.get('sha256') != current_record.get('motionSha256'):
                raise ValueError(f'current asset/authoring baseline mismatch: {family}')
            record = copy.deepcopy(current_record)
            record['candidateGlbPoseQcPath'] = record.get('glbPoseQcPath')
            record['glbPoseQcPath'] = str(pose_path)
            record['glbInterpolationQcPath'] = str(interp_path)
            record['rigidTrajectoryQcPath'] = str(unit_record_path)
            record['rigidTrajectoryQcSha256'] = sha(unit_record_path.read_bytes())
            record['motionSha256'] = glb_hash
            record['motionAssetRevision'] = REVISION
            dependencies = {row['path']: row for row in record.get('verificationDependencies', [])}
            for dep in (unit_record_path, interp_path, source_glb):
                dependencies[str(dep)] = {'path': str(dep), 'sha256': sha(Path(dep).read_bytes())}
            record['verificationDependencies'] = list(dependencies.values())
            write(record_revision_path, record)
            registry_entry['path'] = str(record_revision_path)
            registry_entry['sha256'] = sha(record_revision_path.read_bytes())
            copy_hash(source_glb, target_uri, glb_hash)
            asset['uri'] = target_uri
            asset['sha256'] = glb_hash
            asset['revision'] = REVISION
        results.append({'familyId': family, 'assetId': asset_id, 'authoringRecordId': record_id,
            'motionGlbPath': asset['uri'], 'motionGlbSha256': asset['sha256'],
            'authoringRecordPath': registry_entry['path'], 'side': case_input['side']})

    write(bundle_path, bundle, replace_owned=True)
    write(registry_path, registry, replace_owned=True)
    print(json.dumps({'revision': REVISION, 'registeredCount': len(results), 'results': results}, ensure_ascii=False))


if __name__ == '__main__':
    main()
