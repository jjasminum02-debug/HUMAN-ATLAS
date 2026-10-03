#!/usr/bin/env python3
"""Resample an authored T66 GLB and repair source-topology-local contact poses.

This derives only from a pinned source-family GLB, its exact source manifest, and
the unit's explicit topology edge constraints. It is not a measured attachment,
anatomical normal, physiological solver, or continuous collision proof.
"""
import argparse
import copy
import json
from pathlib import Path

import numpy as np

from author_source_surface_motion import (
    ROOT,
    array,
    container,
    normals,
    read,
    source_geometry,
)
from derive_source_surface_motion import append_bytes, geometry_hash, sha
from author_t66_family_motion import rotation, signed_quat
from source_surface_constraints import inside
from t66_contact_correctives import source_topology_contact_patch_corrective
from verify_glb_interpolation import channel_data, node_positions, read_glb, sample


def _add_accessor(doc, binary, raw, kind, count, minimum=None, maximum=None):
    offset, length = append_bytes(binary, raw)
    view_index = len(doc['bufferViews'])
    doc['bufferViews'].append({'buffer': 0, 'byteOffset': offset, 'byteLength': length})
    accessor_index = len(doc['accessors'])
    accessor = {'bufferView': view_index, 'componentType': 5126, 'count': int(count), 'type': kind}
    if minimum is not None:
        accessor['min'] = np.asarray(minimum, dtype=float).tolist()
        accessor['max'] = np.asarray(maximum, dtype=float).tolist()
    doc['accessors'].append(accessor)
    return accessor_index


def _track(doc, binary, channels, node_index, path):
    if (node_index, path) not in channels:
        return None
    return channels[(node_index, path)]


def refine(input_path, authoring_record_path, source_glb_path, output_path,
           evidence_path, subdivisions=8):
    input_path = Path(input_path)
    authoring_record_path = Path(authoring_record_path)
    source_glb_path = Path(source_glb_path)
    output_path = Path(output_path)
    evidence_path = Path(evidence_path)
    payload = json.loads(input_path.read_text())
    record = json.loads(authoring_record_path.read_text())
    dataset_path = ROOT / payload['dataset']['path']
    if sha(dataset_path.read_bytes()) != payload['dataset']['sha256']:
        raise ValueError('pinned dataset manifest hash changed')
    if subdivisions < 2 or subdivisions > 32:
        raise ValueError('refinement subdivisions must be in [2, 32]')

    raw, original_doc, original_binary = read_glb(source_glb_path)
    doc = copy.deepcopy(original_doc)
    binary = bytearray(original_binary)
    channels = channel_data(original_doc, original_binary)
    source_nodes = {}
    for index, node in enumerate(original_doc['nodes']):
        key = node.get('extras', {}).get('sourceKey')
        if key:
            if key in source_nodes:
                raise ValueError(f'duplicate sourceKey node in authored GLB: {key}')
            source_nodes[key] = index
    record_members = {row['sourceKey']: row for row in record['members']}

    target_key = payload['unitTargetSourceKey']
    if target_key not in source_nodes:
        raise ValueError('exact target sourceKey missing from authored GLB')
    target_node_index = source_nodes[target_key]
    target_node = original_doc['nodes'][target_node_index]
    target_primitive = original_doc['meshes'][target_node['mesh']]['primitives'][0]
    if 'matrix' not in target_node:
        raise ValueError('T66 target must retain its exact source instance matrix')
    matrix = np.asarray(target_node['matrix'], dtype=float).reshape(4, 4).T
    target_local_base = np.asarray(array(original_doc, original_binary,
        target_primitive['attributes']['POSITION']), dtype=float)
    target_normals_base = np.asarray(array(original_doc, original_binary,
        target_primitive['attributes']['NORMAL']), dtype=float)
    target_triangles = np.asarray(array(original_doc, original_binary,
        target_primitive['indices']), dtype=np.int64).reshape(-1, 3)

    source_manifest = read(payload['dataset']['path'])
    source_rows = {row['sourceKey']: row for row in source_manifest['instances']}
    target_entry = next(row for row in payload['members'] if row['sourceKey'] == target_key)
    source_doc, source_binary, _, _, source_triangles, _, source_rest = source_geometry(
        source_rows[target_key], target_entry['lod'])
    source_geometry_sha, source_vertex_count = geometry_hash(source_doc, source_binary, 0)
    target_geometry_record = next(row for row in record['members'] if row['sourceKey'] == target_key)
    if source_geometry_sha != target_geometry_record['geometrySha256']:
        raise ValueError('authoring record and pinned source geometry identity differ')
    if (source_vertex_count != len(target_local_base) or
            not np.array_equal(source_triangles, target_triangles)):
        raise ValueError('authored GLB target topology differs from exact source topology')

    target_rest_world = node_positions(original_doc, original_binary, channels, target_node_index,
        float(channels[(target_node_index, 'weights')][0][0]))
    if np.max(np.linalg.norm(target_rest_world - source_rest, axis=1)) > 1e-6:
        raise ValueError('authored GLB rest frame differs from exact source instance world geometry')

    initial_animation_times = np.asarray(channels[(target_node_index, 'weights')][0], dtype=float)
    dense_times = sorted(set(float(a + (b - a) * step / subdivisions)
        for a, b in zip(initial_animation_times[:-1], initial_animation_times[1:])
        for step in range(subdivisions)) | {float(initial_animation_times[-1])})
    if dense_times[0] != float(initial_animation_times[0]):
        dense_times.insert(0, float(initial_animation_times[0]))
    dense_times_array = np.asarray(dense_times, dtype=np.float32)

    metric = next(row for row in record['surfaceMetrics'] if row['sourceKey'] == target_key)
    fields = np.asarray(metric.get('authoredFinalWeightsByPhase'), dtype=float)
    if fields.ndim != 2 or len(fields) != int(payload['family']['samples']):
        raise ValueError('phase-resolved authored source weights are required to preserve source edge trajectory')
    initial_weights = np.asarray(target_entry['weights'], dtype=float)
    if fields.shape[1] != len(initial_weights):
        raise ValueError('phase-resolved source weights do not match source vertex count')
    phase_points = np.linspace(0.0, 1.0, len(fields) + 1)
    weight_rows = np.vstack([initial_weights, fields])
    edge_rows = target_entry.get('sourceTopologyCoupledEdges', [])
    topology_groups = target_entry.get('sourceTopologyCoupledVertexGroups', [])
    contact_patch_only = bool(payload.get('sourceTopologyContactPatchCorrectives')) and any(
        row.get('role') in ('fixed_structure', 'moving_structure') for row in payload['members'])
    if not edge_rows and not topology_groups and not contact_patch_only:
        raise ValueError('explicit source topology constraints or an enabled contact-only patch with pinned structures are required')
    fixed_moving_locks = set(target_entry['fixedVertexIndices']) | set(target_entry['movingVertexIndices'])
    shape_repair_triangle_ids = sorted(set(int(i) for i in
        payload.get('sourceTopologyShapeRepairTriangleIds', [])))
    if shape_repair_triangle_ids and (min(shape_repair_triangle_ids) < 0 or
            max(shape_repair_triangle_ids) >= len(target_triangles)):
        raise ValueError('source-topology shape-repair triangle ID outside exact target topology')
    shape_seed_vertices = sorted(set(int(v) for v in
        target_triangles[shape_repair_triangle_ids].reshape(-1))) if shape_repair_triangle_ids else []

    role_by_key = {row['sourceKey']: row['role'] for row in payload['members']}
    contact_keys = [key for key, role in role_by_key.items()
        if role in ('fixed_structure', 'moving_structure')]
    if any(key not in source_nodes for key in contact_keys):
        raise ValueError('an exact fixed/moving source structure is absent from the authored GLB')
    contact_triangles = {}
    contact_baseline = {}
    for key in contact_keys:
        entry = next(row for row in payload['members'] if row['sourceKey'] == key)
        _, _, _, _, source_tri, _, source_world = source_geometry(source_rows[key], entry['lod'])
        glb_node = original_doc['nodes'][source_nodes[key]]
        glb_primitive = original_doc['meshes'][glb_node['mesh']]['primitives'][0]
        glb_tri = np.asarray(array(original_doc, original_binary, glb_primitive['indices']), dtype=np.int64).reshape(-1, 3)
        if not np.array_equal(source_tri, glb_tri):
            raise ValueError(f'contact topology differs from pinned source: {key}')
        source_world_glb = node_positions(original_doc, original_binary, channels, source_nodes[key], float(dense_times_array[0]))
        if np.max(np.linalg.norm(source_world_glb - source_world, axis=1)) > 1e-6:
            raise ValueError(f'contact source rest instance differs from pinned source: {key}')
        contact_triangles[key] = glb_tri
        contact_baseline[key] = inside(target_rest_world, source_world_glb, glb_tri)

    refined_local_positions = []
    time_qc = []
    inverse_linear = np.linalg.inv(matrix[:3, :3])
    pivot = np.asarray(payload['family']['pivotMetres'], dtype=float)
    axis = np.asarray(payload['family']['axis'], dtype=float)
    duration = float(payload['family']['durationSeconds'])
    for time in dense_times_array.astype(float):
        frame = node_positions(original_doc, original_binary, channels, target_node_index, time)
        contacts = []
        for key in contact_keys:
            bone = node_positions(original_doc, original_binary, channels, source_nodes[key], time)
            contacts.append((key, bone, contact_triangles[key], contact_baseline[key]))
        phase = min(1.0, max(0.0, time / duration))
        phase_weights = np.array([np.interp(phase, phase_points, weight_rows[:, vertex])
            for vertex in range(len(initial_weights))], dtype=float)
        angle = np.radians(float(payload['family']['endDegrees'])) * phase
        transform = rotation(axis, angle)
        edge_targets = []
        for edge in edge_rows:
            a, b = map(int, edge['vertices'])
            source_edge = source_rest[b] - source_rest[a]
            mean_weight = float(np.mean(phase_weights[[a, b]]))
            desired_edge = source_edge + mean_weight * (transform @ source_edge - source_edge)
            edge_targets.append({'vertices': [a, b], 'desiredVectorMetres': desired_edge.tolist()})
        if time > float(dense_times_array[0]) + 1e-8:
            try:
                frame, correction = source_topology_contact_patch_corrective(
                    frame, source_rest, source_triangles, contacts, fixed_moving_locks, edge_targets,
                    patch_rings=int(payload.get('sourceTopologyContactPatchRings', 3)),
                    margin_metres=float(payload.get('sourceBoneProjectionMarginMetres', .0002)),
                    max_outer_iterations=24,
                    shape_floor=float(payload.get('sourceTopologyShapeFloor', .1)),
                    shape_seed_vertices=shape_seed_vertices,
                    topology_groups=topology_groups)
            except Exception as error:
                raise ValueError(f'source-topology interpolation repair failed at t={time:.9f}s: {error}') from error
        else:
            correction = {'method': 'source-rest-pose-unchanged', 'maximumCorrectiveMetres': 0.0,
                'correctedVertexIndices': [], 'remainingNewContactVertices': []}
        local = (frame * matrix[3, 3] - matrix[:3, 3]) @ inverse_linear.T
        refined_local_positions.append(local)
        time_qc.append({'seconds': float(time), 'phase': float(phase),
            'maximumCorrectiveMetres': float(correction.get('maximumCorrectiveMetres', 0.0)),
            'correctedVertexIndices': correction.get('correctedVertexIndices', []),
            'method': correction.get('method'), 'edgeTargets': correction.get('edgeTargets', []),
            'triangleOrientationFlips': correction.get('triangleOrientationFlips', 0),
            'minimumSourceAreaRatio': correction.get('minimumSourceAreaRatio'),
            'remainingNewContactVertices': correction.get('remainingNewContactVertices', [])})

    # Replace only the target's morph targets and animation weights. Resample
    # every existing transform channel at the same exact source-animation times.
    new_targets = []
    for local in refined_local_positions[1:]:
        delta_position = np.asarray(local - target_local_base, dtype='<f4')
        delta_normal = np.asarray(normals(local, target_triangles) - target_normals_base, dtype='<f4')
        new_targets.append({
            'POSITION': _add_accessor(doc, binary, delta_position.tobytes(), 'VEC3', len(local)),
            'NORMAL': _add_accessor(doc, binary, delta_normal.tobytes(), 'VEC3', len(local)),
        })
    primitive = doc['meshes'][target_node['mesh']]['primitives'][0]
    primitive['targets'] = new_targets
    doc['meshes'][target_node['mesh']]['weights'] = [0.0] * len(new_targets)
    doc['nodes'][target_node_index]['weights'] = [0.0] * len(new_targets)

    time_accessor = _add_accessor(doc, binary, dense_times_array.astype('<f4').tobytes(),
        'SCALAR', len(dense_times_array), [float(dense_times_array[0])], [float(dense_times_array[-1])])
    weight_values = np.zeros((len(dense_times_array), len(new_targets)), dtype='<f4')
    for index in range(1, len(dense_times_array)):
        weight_values[index, index - 1] = 1.0
    transform_paths = {'translation': 'VEC3', 'rotation': 'VEC4', 'scale': 'VEC3'}
    weight_track_count = 0
    rigid_trajectory_key_count = 0
    rigid_trajectory_keys = set()
    family_start = float(initial_animation_times[0])
    family_end = float(initial_animation_times[-1])
    if abs(family_start) > 1e-9 or abs(family_end - float(payload['family']['durationSeconds'])) > 1e-6:
        raise ValueError('source-family timeline must start at zero and match its declared duration')
    for channel in doc['animations'][0]['channels']:
        sampler_index = channel['sampler']
        target = channel['target']
        sampler = doc['animations'][0]['samplers'][sampler_index]
        sampler['input'] = time_accessor
        if target['node'] == target_node_index and target['path'] == 'weights':
            sampler['output'] = _add_accessor(doc, binary, weight_values.reshape(-1).tobytes(),
                'SCALAR', weight_values.size)
            weight_track_count += 1
            continue
        path = target['path']
        if path not in transform_paths:
            raise ValueError(f'unsupported animation path while resampling: {path}')
        node_source_key = original_doc['nodes'][target['node']].get('extras', {}).get('sourceKey')
        member = record_members.get(node_source_key)
        if member and member.get('role') in ('moving_structure', 'co_moving_context') and path in ('translation', 'rotation'):
            source_row = source_rows.get(node_source_key)
            if source_row is None or not np.allclose(
                    np.asarray(member['instanceMatrix'], dtype=float),
                    np.asarray(source_row['matrix'], dtype=float), rtol=0.0, atol=1e-12):
                raise ValueError(f'rigid trajectory source matrix differs from frozen instance: {node_source_key}')
            instance = np.asarray(member['instanceMatrix'], dtype=float).reshape(4, 4).T
            pivot = np.asarray(payload['family']['pivotMetres'], dtype=float)
            axis = np.asarray(payload['family']['axis'], dtype=float)
            angle = np.radians(float(payload['family']['endDegrees']))
            translations = []
            rotations = []
            for time in dense_times_array.astype(float):
                phase = min(1.0, max(0.0, (time - family_start) / float(payload['family']['durationSeconds'])))
                transform = rotation(axis, angle * phase)
                moved = instance.copy()
                moved[:3, :3] = transform @ instance[:3, :3]
                moved[:3, 3] = (instance[:3, 3] - pivot) @ transform.T + pivot
                quaternion, _ = signed_quat(moved)
                translations.append(moved[:3, 3].tolist())
                rotations.append(quaternion)
            values = np.asarray(translations if path == 'translation' else rotations, dtype='<f4')
            rigid_trajectory_keys.add(node_source_key)
            if path == 'rotation':
                rigid_trajectory_key_count += len(dense_times_array)
        else:
            track = channels[(target['node'], path)]
            values = np.asarray([sample(track, float(time), path) for time in dense_times_array], dtype='<f4')
        sampler['output'] = _add_accessor(doc, binary, values.reshape(-1).tobytes(),
            transform_paths[path], len(values))
    if weight_track_count != 1:
        raise ValueError('expected exactly one target morph weight animation channel')
    output_bytes = container(doc, binary)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists() and output_path.read_bytes() != output_bytes:
        raise ValueError(f'refined GLB already exists with different bytes: {output_path}')
    if not output_path.exists():
        output_path.write_bytes(output_bytes)

    evidence = {'schemaVersion': 't66-glb-interpolation-refinement-v1',
        'inputPath': str(input_path), 'inputSha256': sha(input_path.read_bytes()),
        'authoringRecordPath': str(authoring_record_path), 'authoringRecordSha256': sha(authoring_record_path.read_bytes()),
        'sourceMotionGlbPath': str(source_glb_path), 'sourceMotionGlbSha256': sha(raw),
        'refinedMotionGlbPath': str(output_path), 'refinedMotionGlbSha256': sha(output_bytes),
        'targetSourceKey': target_key, 'targetGeometrySha256': source_geometry_sha,
        'sourceEdgeRows': edge_rows, 'sourceTopologyDisplacementGroups': topology_groups,
        'shapeFloorRatio': float(payload.get('sourceTopologyShapeFloor', .1)),
        'subdivisionsPerOriginalSegment': subdivisions,
        'rigidSourceFrameTrajectory': {
            'method': 'recompose_source_instance_from_authored_family_axis_pivot_and_phase',
            'movingSourceKeys': sorted(rigid_trajectory_keys),
            'rotationKeyCount': rigid_trajectory_key_count,
            'sourceInstanceMatricesMatched': True,
            'measuredAnatomicalAxis': False,
            'measuredAttachmentFootprints': False,
        },
        'sourceTopologyShapeRepairTriangleIds': shape_repair_triangle_ids,
        'sourceTopologyShapeSeedVertices': shape_seed_vertices,
        'refinedKeyCount': int(len(dense_times_array)), 'sampledTimesSeconds': dense_times_array.astype(float).tolist(),
        'rights': payload['rights'], 'sourceGeometryModified': False,
        'measuredAnatomicalAxis': False, 'measuredAttachmentFootprints': False,
        'timeRows': time_qc,
        'continuousCollisionFreedomClaimed': False,
        'limitations': ['Refinement keys repair only sampled poses and do not prove continuous collision freedom.',
            'The local patch is a source-geometry engineering corrective, not a measured anatomical deformation.']}
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
    return evidence


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--authoring-record', required=True)
    parser.add_argument('--source-glb', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--evidence', required=True)
    parser.add_argument('--subdivisions', type=int, default=8)
    args = parser.parse_args()
    result = refine(args.input, args.authoring_record, args.source_glb, args.output,
        args.evidence, args.subdivisions)
    print(json.dumps({'status': 'refined_candidate', 'target': result['targetSourceKey'],
        'keys': result['refinedKeyCount'], 'motionSha256': result['refinedMotionGlbSha256']}))
