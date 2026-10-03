#!/usr/bin/env python3
"""Rebuild moving-structure TRS keys from the pinned source instance transform.

This utility rewrites only translation/rotation animation outputs. Mesh topology,
source positions, morph/corrective tracks, side, axis, pivot, and duration remain
as authored in the input family package. The axis and pivot remain authored
educational values, not measured anatomical data.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import numpy as np

from author_t66_family_motion import rotation, signed_quat
from author_source_surface_motion import array, container, read as read_source_manifest
from derive_source_surface_motion import sha
from verify_glb_interpolation import channel_data, read_glb

ROOT = Path(__file__).resolve().parents[2]


def add_float_accessor(doc, binary, values, kind):
    raw = np.asarray(values, dtype='<f4').reshape(-1).tobytes()
    while len(binary) % 4:
        binary.append(0)
    offset = len(binary)
    binary.extend(raw)
    view_index = len(doc['bufferViews'])
    doc['bufferViews'].append({'buffer': 0, 'byteOffset': offset, 'byteLength': len(raw)})
    count = len(values)
    accessor_index = len(doc['accessors'])
    doc['accessors'].append({'bufferView': view_index, 'componentType': 5126,
        'count': count, 'type': kind})
    return accessor_index


def rewrite(input_path, authoring_record_path, source_glb_path, output_path, evidence_path,
        interpolation_qc_path=None):
    input_path = Path(input_path)
    record_path = Path(authoring_record_path)
    source_glb_path = Path(source_glb_path)
    output_path = Path(output_path)
    evidence_path = Path(evidence_path)
    payload = json.loads(input_path.read_text())
    record = json.loads(record_path.read_text())
    raw, original_doc, original_binary = read_glb(source_glb_path)
    interpolation_qc = None
    if record.get('motionSha256') != sha(raw):
        if interpolation_qc_path is None:
            raise ValueError('refined input needs its exact passing interpolation QC')
        interpolation_qc_path = Path(interpolation_qc_path)
        interpolation_qc = json.loads(interpolation_qc_path.read_text())
        if not interpolation_qc.get('passed') or interpolation_qc.get('motionGlbSha256') != sha(raw):
            raise ValueError('input GLB hash is not the exact passing interpolation-QC asset')
    if record.get('rights') != payload.get('rights'):
        raise ValueError('authoring record and family rights differ')
    dataset_path = ROOT / payload['dataset']['path']
    if sha(dataset_path.read_bytes()) != payload['dataset']['sha256']:
        raise ValueError('pinned source manifest hash changed')
    manifest = read_source_manifest(payload['dataset']['path'])
    source_rows = {row['sourceKey']: row for row in manifest['instances']}
    record_members = {row['sourceKey']: row for row in record['members']}

    doc = copy.deepcopy(original_doc)
    binary = bytearray(original_binary)
    position_bounds_added = 0
    for mesh in original_doc.get('meshes', []):
        for primitive in mesh.get('primitives', []):
            position_accessors = []
            base_position = primitive.get('attributes', {}).get('POSITION')
            if base_position is not None:
                position_accessors.append(base_position)
            position_accessors.extend(target['POSITION'] for target in primitive.get('targets', [])
                if 'POSITION' in target)
            for accessor_index in position_accessors:
                accessor = doc['accessors'][accessor_index]
                if 'min' in accessor and 'max' in accessor:
                    continue
                values = np.asarray(array(original_doc, original_binary, accessor_index), dtype=float)
                accessor['min'] = values.min(axis=0).tolist()
                accessor['max'] = values.max(axis=0).tolist()
                position_bounds_added += 1
    tracks = channel_data(original_doc, original_binary)
    nodes_by_source = {}
    for index, node in enumerate(original_doc['nodes']):
        key = node.get('extras', {}).get('sourceKey')
        if key:
            if key in nodes_by_source:
                raise ValueError(f'duplicate sourceKey in GLB: {key}')
            nodes_by_source[key] = index

    target_key = payload['unitTargetSourceKey']
    target_node = nodes_by_source.get(target_key)
    if target_node is None or (target_node, 'weights') not in tracks:
        raise ValueError('exact deforming source node/morph track missing')
    times = np.asarray(tracks[(target_node, 'weights')][0], dtype=float)
    family = payload['family']
    duration = float(family['durationSeconds'])
    if len(times) < 2 or abs(float(times[0])) > 1e-9 or abs(float(times[-1]) - duration) > 1e-6:
        raise ValueError('morph track does not span the declared family duration')
    axis = np.asarray(family['axis'], dtype=float)
    pivot = np.asarray(family['pivotMetres'], dtype=float)
    angle = np.radians(float(family['endDegrees']))

    expected_keys = set()
    updated_channels = []
    transform_error_by_source = {}
    for source_key, member in record_members.items():
        if member.get('role') not in ('moving_structure', 'co_moving_context'):
            continue
        if source_key not in nodes_by_source or source_key not in source_rows:
            raise ValueError(f'moving source member missing from GLB/manifest: {source_key}')
        if not np.allclose(np.asarray(member['instanceMatrix'], dtype=float),
                np.asarray(source_rows[source_key]['matrix'], dtype=float), rtol=0.0, atol=1e-12):
            raise ValueError(f'authoring record matrix differs from pinned source: {source_key}')
        node_index = nodes_by_source[source_key]
        node = original_doc['nodes'][node_index]
        instance = np.asarray(member['instanceMatrix'], dtype=float).reshape(4, 4).T
        base_q, base_scale = signed_quat(instance)
        if 'matrix' in node:
            raise ValueError(f'moving node still has static matrix with animated TRS: {source_key}')
        if not np.allclose(node.get('translation', [0, 0, 0]), instance[:3, 3], rtol=0.0, atol=2e-6):
            raise ValueError(f'moving node rest translation differs from source frame: {source_key}')
        node_q = np.asarray(node.get('rotation', [0, 0, 0, 1]), dtype=float)
        if abs(float(np.dot(node_q, np.asarray(base_q, dtype=float)))) < 1 - 1e-6:
            raise ValueError(f'moving node rest rotation differs from source frame: {source_key}')
        if not np.allclose(node.get('scale', [1, 1, 1]), base_scale, rtol=0.0, atol=2e-6):
            raise ValueError(f'moving node signed rest scale differs from source frame: {source_key}')

        translations = []
        quaternions = []
        linear_errors = []
        for time in times:
            phase = min(1.0, max(0.0, float(time) / duration))
            turn = rotation(axis, angle * phase)
            moved = instance.copy()
            moved[:3, :3] = turn @ instance[:3, :3]
            moved[:3, 3] = (instance[:3, 3] - pivot) @ turn.T + pivot
            quaternion, signed_scale = signed_quat(moved)
            translations.append(moved[:3, 3])
            quaternions.append(quaternion)
            # Matrix reconstruction check for each written source-frame key.
            q = np.asarray(quaternion, dtype=float)
            x, y, z, w = q
            qmat = np.array([
                [1 - 2*(y*y + z*z), 2*(x*y - z*w), 2*(x*z + y*w)],
                [2*(x*y + z*w), 1 - 2*(x*x + z*z), 2*(y*z - x*w)],
                [2*(x*z - y*w), 2*(y*z + x*w), 1 - 2*(x*x + y*y)],
            ])
            linear_errors.append(float(np.max(np.abs(qmat @ np.diag(signed_scale) - moved[:3, :3]))))

        for path, values, kind in (
            ('translation', translations, 'VEC3'),
            ('rotation', quaternions, 'VEC4'),
        ):
            track_key = (node_index, path)
            if track_key not in tracks:
                raise ValueError(f'moving node missing {path} track: {source_key}')
            channel = next((row for row in doc['animations'][0]['channels']
                if row['target']['node'] == node_index and row['target']['path'] == path), None)
            if channel is None:
                raise ValueError(f'moving node missing {path} animation channel: {source_key}')
            sampler = doc['animations'][0]['samplers'][channel['sampler']]
            sampler['output'] = add_float_accessor(doc, binary, values, kind)
            updated_channels.append({'sourceKey': source_key, 'path': path,
                'keyCount': len(times), 'outputAccessor': sampler['output']})
        expected_keys.add(source_key)
        transform_error_by_source[source_key] = max(linear_errors, default=0.0)

    if not expected_keys:
        raise ValueError('family has no moving/co-moving source structures')
    output_bytes = container(doc, binary)
    if output_path.exists() and output_path.read_bytes() != output_bytes:
        raise ValueError(f'revision output exists with different bytes; preserving it: {output_path}')
    if not output_path.exists():
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(output_bytes)

    result = {
        'schemaVersion': 't66-source-frame-rigid-track-rewrite-v1',
        'familyId': family['id'], 'side': payload['side'],
        'inputPath': str(input_path), 'inputSha256': sha(input_path.read_bytes()),
        'authoringRecordPath': str(record_path), 'authoringRecordSha256': sha(record_path.read_bytes()),
        'inputGlbPath': str(source_glb_path), 'inputGlbSha256': sha(raw),
        'upstreamInterpolationQcPath': str(interpolation_qc_path) if interpolation_qc_path else None,
        'upstreamInterpolationQcSha256': sha(interpolation_qc_path.read_bytes()) if interpolation_qc_path else None,
        'outputGlbPath': str(output_path), 'outputGlbSha256': sha(output_bytes),
        'sourceManifestPath': payload['dataset']['path'], 'sourceManifestSha256': payload['dataset']['sha256'],
        'targetSourceKey': target_key, 'sourceGeometryModified': False,
        'morphAndGeometryTracksPreserved': True,
        'positionAccessorBoundsAdded': position_bounds_added,
        'positionCoordinatesChanged': False,
        'axisAndPivotMeasuredAnatomicalValues': False,
        'measuredAttachmentFootprints': False,
        'sourceFrameTimelineSeconds': times.astype(float).tolist(),
        'movingSourceKeys': sorted(expected_keys), 'updatedChannels': updated_channels,
        'maximumRigidLinearTransformRecompositionError': max(transform_error_by_source.values(), default=0.0),
        'rigidLinearTransformRecompositionErrorBySource': transform_error_by_source,
        'continuousCollisionFreedomClaimed': False,
        'limitations': [
            'The pose axis and pivot are authored educational values, not measured anatomical axes.',
            'This rewrites only moving/co-moving structure transforms; unchanged target morph geometry remains subject to the emitted-GLB contact and surface verifiers.',
        ],
    }
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--authoring-record', required=True)
    parser.add_argument('--source-glb', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--evidence', required=True)
    parser.add_argument('--interpolation-qc')
    args = parser.parse_args()
    result = rewrite(args.input, args.authoring_record, args.source_glb, args.output,
        args.evidence, args.interpolation_qc)
    print(json.dumps({'status': 'rewritten', 'family': result['familyId'], 'side': result['side'],
        'keys': len(result['sourceFrameTimelineSeconds']), 'sha256': result['outputGlbSha256']}))
