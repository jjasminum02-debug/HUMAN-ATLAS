"""Source-topology-aware deformation weights for T66 authored motion.

This module derives engineering weights from the exact source vertices, triangles,
endpoint masks, and pinned moving/fixed source bone surfaces. It does not create
attachment landmarks or a measured physiological axis.
"""
import hashlib, json
from pathlib import Path
import numpy as np
from source_surface_constraints import inside

GRID_STEPS = 40
DEFAULT_SMOOTHNESS = 0.5


def _candidate_frame(rest, pivot, axis, degrees, phase, weight, method):
    if method == 'fractional_rotation':
        theta = np.radians(degrees) * phase * weight
        vec = rest - pivot
        cos = np.cos(theta)[:, None]
        sin = np.sin(theta)[:, None]
        return pivot + vec * cos + np.cross(axis, vec) * sin + (vec @ axis)[:, None] * axis * (1 - cos)
    rotated = (rest - pivot) @ _rotation(axis, np.radians(degrees) * phase).T + pivot
    return rest + weight[:, None] * (rotated - rest)


def _rotation(axis, theta):
    x, y, z = axis
    c, s = np.cos(theta), np.sin(theta)
    C = 1 - c
    return np.array([[x*x*C+c, x*y*C-z*s, x*z*C+y*s],
                     [y*x*C+z*s, y*y*C+c, y*z*C-x*s],
                     [z*x*C-y*s, z*y*C+x*s, z*z*C+c]])


def _bounded_inside(points, vertices, triangles):
    result = np.zeros(len(points), dtype=bool)
    ids = np.flatnonzero(((points >= vertices.min(0) - 1e-8) & (points <= vertices.max(0) + 1e-8)).all(1))
    if len(ids):
        result[ids] = inside(points[ids], vertices, triangles)
    return result


def _intervals(row):
    good = np.flatnonzero(row)
    runs = []
    for index in good:
        if not runs or index > runs[-1][-1] + 1:
            runs.append([int(index)])
        else:
            runs[-1].append(int(index))
    return [[run[0], run[-1]] for run in runs]


def _smooth_feasible_field(allowed, initial, fixed, moving, edges, edge_weights, grid, smoothness):
    n = len(initial)
    if not allowed.any(axis=1).all():
        raise ValueError('source-frame contact feasibility has no weight solution for one or more vertices')
    for ids, value, name in ((fixed, 0.0, 'fixed'), (moving, 1.0, 'moving')):
        grid_index = int(round(value * (len(grid) - 1)))
        if not allowed[np.asarray(ids, dtype=int), grid_index].all():
            raise ValueError(f'authored {name} endpoint mask conflicts with source contact feasibility')
    if set(fixed) & set(moving):
        raise ValueError('fixed/moving endpoint masks overlap')
    neighbors = [[] for _ in range(n)]
    for (a, b), weight in zip(edges, edge_weights):
        neighbors[int(a)].append((int(b), float(weight)))
        neighbors[int(b)].append((int(a), float(weight)))
    endpoint = np.full(n, np.nan)
    endpoint[fixed] = 0.0
    endpoint[moving] = 1.0
    labels = np.zeros(n, dtype=int)
    for i in range(n):
        choices = np.flatnonzero(allowed[i])
        labels[i] = int(choices[np.argmin(np.abs(grid[choices] - initial[i]))])
    labels[fixed] = 0
    labels[moving] = len(grid) - 1
    # Deterministic coordinate minimization over the exact allowed values. The
    # convex terms preserve the source-authored field and reduce mesh-edge jumps;
    # per-vertex feasibility remains a hard constraint throughout.
    for sweep in range(500):
        changed = 0
        for order in (range(n), range(n - 1, -1, -1)):
            for i in order:
                if np.isfinite(endpoint[i]):
                    continue
                options = np.flatnonzero(allowed[i])
                adjacent = neighbors[i]
                costs = (grid[options] - initial[i]) ** 2
                if adjacent:
                    ids = np.array([j for j, _ in adjacent], dtype=int)
                    weights = np.array([weight for _, weight in adjacent], dtype=float)
                    neighbor_values = grid[labels[ids]]
                    costs += smoothness * (weights[None, :] * (grid[options, None] - neighbor_values[None, :]) ** 2).sum(axis=1)
                best = int(options[int(np.argmin(costs))])
                if labels[i] != best:
                    labels[i] = best
                    changed += 1
        if changed == 0:
            return grid[labels], sweep + 1
    raise ValueError('source-frame contact-weight solver failed to converge')


def _solve_contact_and_shape_field(allowed, initial, fixed, moving, triangles, rest, candidate_frames,
                                   edges, edge_weights, grid, smoothness, coupled_vertex_groups=()):
    """Choose contact-feasible weights while retaining each original face shape.

    Candidate weights are first filtered against actual source contact triangles.
    This deterministic coordinate solve additionally imposes the author's existing
    orientation and 10% area limits at every sampled phase, including phase samples
    between output keys. It does not interpret the field as measured physiology.
    """
    n = len(initial)
    if not allowed.any(axis=1).all():
        raise ValueError('source-frame contact feasibility has no weight solution for one or more vertices')
    if set(fixed) & set(moving):
        raise ValueError('fixed/moving endpoint masks overlap')
    for ids, endpoint_index, name in ((fixed, 0, 'fixed'), (moving, len(grid) - 1, 'moving')):
        if not allowed[np.asarray(ids, dtype=int), endpoint_index].all():
            raise ValueError(f'authored {name} endpoint mask conflicts with source contact feasibility')
    labels = np.zeros(n, dtype=np.int32)
    for i in range(n):
        options = np.flatnonzero(allowed[i])
        labels[i] = int(options[np.argmin(np.abs(grid[options] - initial[i]))])
    labels[np.asarray(fixed, dtype=int)] = 0
    labels[np.asarray(moving, dtype=int)] = len(grid) - 1
    locked = set(int(i) for i in fixed) | set(int(i) for i in moving)
    neighbors = [[] for _ in range(n)]
    for (a, b), ew in zip(edges, edge_weights):
        neighbors[int(a)].append((int(b), float(ew)))
        neighbors[int(b)].append((int(a), float(ew)))
    rest_tri = rest[triangles]
    base_normals = np.cross(rest_tri[:, 1] - rest_tri[:, 0], rest_tri[:, 2] - rest_tri[:, 0])
    base_areas = np.linalg.norm(base_normals, axis=1)
    phase_ids = np.arange(candidate_frames.shape[0], dtype=np.int32)
    incident = [np.flatnonzero(np.any(triangles == i, axis=1)) for i in range(n)]

    def local_energy(vertex, options, field):
        tri_ids = incident[vertex]
        result = (grid[options] - initial[vertex]) ** 2
        if neighbors[vertex]:
            ids = np.array([j for j, _ in neighbors[vertex]], dtype=int)
            ew = np.array([weight for _, weight in neighbors[vertex]], dtype=float)
            result += smoothness * (ew[None, :] * (grid[options, None] - grid[field[ids]][None, :]) ** 2).sum(1)
        if len(tri_ids):
            tri_vertices = triangles[tri_ids]
            base = candidate_frames[phase_ids[:, None, None], field[tri_vertices][None, :, :], tri_vertices[None, :, :], :]
            trial = np.broadcast_to(base[:, None, :, :, :], (base.shape[0], len(options), len(tri_ids), 3, 3)).copy()
            for j, triangle in enumerate(tri_vertices):
                loc = int(np.flatnonzero(triangle == vertex)[0])
                trial[:, :, j, loc, :] = candidate_frames[:, options, vertex, :]
            normal = np.cross(trial[:, :, :, 1] - trial[:, :, :, 0], trial[:, :, :, 2] - trial[:, :, :, 0])
            area = np.linalg.norm(normal, axis=3)
            dot = (normal * base_normals[None, None, tri_ids, :]).sum(3)
            valid_area = base_areas[tri_ids][None, None, :] >= 1e-12
            flip = (dot < 0) & valid_area
            collapse = (area < base_areas[tri_ids][None, None, :] * .1) & valid_area
            severity = np.maximum(0.0, -dot / np.maximum(base_areas[tri_ids][None, None, :] ** 2, 1e-24)) ** 2
            severity += np.maximum(0.0, .1 - area / np.maximum(base_areas[tri_ids][None, None, :], 1e-12)) ** 2
            shape_cost = (flip.astype(float) * 1e6 + collapse.astype(float) * 1e6 + severity * 1e3).sum(axis=(0, 2))
            result += shape_cost
        return result

    def joint_triangle_choices(triangle_id, field, limit=12):
        vertices = [int(v) for v in triangles[triangle_id]]
        options = [np.flatnonzero(allowed[v]) if v not in locked else np.array([field[v]]) for v in vertices]
        if any(len(row) == 0 for row in options):
            return []
        base_area = base_areas[triangle_id]
        base_normal = base_normals[triangle_id]
        good = np.ones(tuple(len(row) for row in options), dtype=bool)
        for phase in range(candidate_frames.shape[0]):
            p0 = candidate_frames[phase, options[0], vertices[0]]
            p1 = candidate_frames[phase, options[1], vertices[1]]
            p2 = candidate_frames[phase, options[2], vertices[2]]
            normal = np.cross(p1[None, :, None, :] - p0[:, None, None, :],
                              p2[None, None, :, :] - p0[:, None, None, :])
            area = np.linalg.norm(normal, axis=3)
            good &= (normal * base_normal).sum(3) >= 0
            good &= area >= base_area * .1
            if not good.any():
                return []
        if not good.any():
            return []
        w0, w1, w2 = grid[options[0]], grid[options[1]], grid[options[2]]
        costs = (((w0 - initial[vertices[0]]) ** 2)[:, None, None]
                 + ((w1 - initial[vertices[1]]) ** 2)[None, :, None]
                 + ((w2 - initial[vertices[2]]) ** 2)[None, None, :])
        vertex_values = [w0[:, None, None], w1[None, :, None], w2[None, None, :]]
        incident_edges = np.flatnonzero(np.any(np.isin(edges, vertices), axis=1))
        for edge_index in incident_edges:
            a, b = map(int, edges[edge_index])
            ia = vertices.index(a) if a in vertices else None
            ib = vertices.index(b) if b in vertices else None
            wa = vertex_values[ia] if ia is not None else float(grid[field[a]])
            wb = vertex_values[ib] if ib is not None else float(grid[field[b]])
            costs += smoothness * edge_weights[edge_index] * (wa - wb) ** 2
        costs[~good] = np.inf
        order = np.argsort(costs, axis=None)
        choices = []
        seen = set()
        for flat_index in order:
            if not np.isfinite(costs.flat[int(flat_index)]):
                break
            indices = np.unravel_index(int(flat_index), costs.shape)
            choice = tuple(int(options[i][indices[i]]) for i in range(3))
            if choice not in seen:
                seen.add(choice)
                choices.append(choice)
            if len(choices) >= limit:
                break
        return choices

    def shape_quality(field):
        points = candidate_frames[phase_ids[:, None], field[None, :], np.arange(n)[None, :], :]
        posed = points[:, triangles, :]
        normals = np.cross(posed[:, :, 1] - posed[:, :, 0], posed[:, :, 2] - posed[:, :, 0])
        areas = np.linalg.norm(normals, axis=2)
        valid = ((normals * base_normals[None, :, :]).sum(2) >= 0) & (areas >= base_areas[None, :] * .1)
        valid[:, base_areas < 1e-12] = True
        bad = ~valid
        normalized_area = areas / np.maximum(base_areas[None, :], 1e-12)
        dot_ratio = (normals * base_normals[None, :, :]).sum(2) / np.maximum(base_areas[None, :] ** 2, 1e-24)
        severity = np.maximum(0.0, -dot_ratio) ** 2 + np.maximum(0.0, .1 - normalized_area) ** 2
        return (int(bad.sum()), float(severity[bad].sum()) if bad.any() else 0.0), np.flatnonzero(bad.any(0)).tolist()

    def coordinate_descent(field, field_locked, max_sweeps):
        sweeps = 0
        for _ in range(max_sweeps):
            changed = 0
            for order in (range(n), range(n - 1, -1, -1)):
                for vertex in order:
                    if vertex in field_locked:
                        continue
                    options = np.flatnonzero(allowed[vertex])
                    best = int(options[int(np.argmin(local_energy(vertex, options, field)))])
                    if field[vertex] != best:
                        field[vertex] = best
                        changed += 1
            sweeps += 1
            if changed == 0:
                break
        return field, sweeps

    labels, sweeps = coordinate_descent(labels, locked, 256)
    coupled_records = []
    # Some source meshes contain topology-linked vertices whose rest separation is
    # below the source's local surface resolution. Independent scalar weights can
    # turn those tiny edges into a visible tear. Keep such groups coupled, but only
    # when one shared contact-feasible value also preserves every source face.
    for group_index, raw_group in enumerate(coupled_vertex_groups):
        group = sorted(set(int(v) for v in raw_group))
        if len(group) < 2 or min(group) < 0 or max(group) >= n:
            raise ValueError(f'invalid source-topology coupled group {group_index}: {group}')
        if set(group) & locked:
            raise ValueError(f'source-topology coupled group overlaps a fixed/moving endpoint mask: {group}')
        # A topology-coupled seam may need one subsequent vector contact
        # corrective when its shared scalar trajectory intersects a source bone.
        # Do not make two adjacent source vertices tear merely to satisfy scalar
        # contact independently; retain the actual bone surfaces for the explicit
        # projection pass after this field solve.
        common = np.arange(len(grid), dtype=int)
        incident_ids = np.unique(np.concatenate([incident[v] for v in group])).astype(int)
        best = None
        current_quality, _ = shape_quality(labels)
        for option in common:
            trial = labels.copy()
            trial[np.asarray(group, dtype=int)] = int(option)
            # Let the surrounding free source vertices adapt to this shared seam
            # value before deciding feasibility. Testing a group against a frozen
            # local field can reject a valid source-topology solution prematurely.
            trial, trial_sweeps = coordinate_descent(trial, locked | set(group), 64)
            sweeps += trial_sweeps
            quality, bad = shape_quality(trial)
            if quality[0]:
                continue
            group_weights = grid[option]
            # Choose the feasible shared value closest to the source-derived target
            # and neighboring field; a weak temporal carry-forward is already in
            # `initial`, so this does not make the group jump to a new pose family.
            cost = float(np.sum((group_weights - initial[np.asarray(group, dtype=int)]) ** 2))
            neighbor_terms = 0.0
            for vertex in group:
                tri_ids = incident[vertex]
                if neighbors[vertex]:
                    for other, weight in neighbors[vertex]:
                        if other not in group:
                            neighbor_terms += float(weight) * (group_weights - grid[labels[other]]) ** 2
            cost += smoothness * neighbor_terms
            choice = (cost, int(option), trial, quality, bad)
            if best is None or choice[0] < best[0]:
                best = choice
        if best is None:
            raise ValueError(f'no shared contact/shape-feasible weight for source-topology coupled group {group_index}: {group}; incidentFaces={incident_ids.tolist()}')
        labels = best[2]
        locked |= set(group)
        group_contact_allowed = bool(np.all(allowed[np.asarray(group, dtype=int), best[1]]))
        coupled_records.append({'groupIndex': group_index, 'vertexIndices': group,
            'incidentTriangleIds': incident_ids.tolist(), 'selectedWeight': float(grid[best[1]]),
            'sharedCandidateGridIndex': best[1], 'beforeInvalidPhaseFaceCount': current_quality[0],
            'afterInvalidPhaseFaceCount': best[3][0],
            'contactFeasibleAtAllSampledPhases': group_contact_allowed,
            'contactCorrectiveRequired': not group_contact_allowed})
    if coupled_vertex_groups:
        labels, extra_sweeps = coordinate_descent(labels, locked, 128)
        sweeps += extra_sweeps
    quality, bad_triangles = shape_quality(labels)
    repairs = []
    attempts = 0
    # When a thin source face has a valid joint weight combination but per-vertex
    # descent repeatedly returns to its local minimum, hold the selected three-face
    # patch while the surrounding field relaxes. Accept only a strict whole-surface
    # geometry improvement; all candidate weights remain contact-feasible.
    while quality[0] and attempts < 256:
        best_field = None
        best_quality = quality
        best_repair = None
        for triangle_id in bad_triangles:
            triangle = triangles[int(triangle_id)].astype(int)
            for choice in joint_triangle_choices(int(triangle_id), labels, limit=16):
                attempts += 1
                trial = labels.copy()
                trial[triangle] = np.asarray(choice, dtype=np.int32)
                trial, trial_sweeps = coordinate_descent(trial, locked | set(map(int, triangle)), 64)
                trial_quality, _ = shape_quality(trial)
                sweeps += trial_sweeps
                if trial_quality < best_quality:
                    best_field = trial
                    best_quality = trial_quality
                    best_repair = {'triangleId': int(triangle_id), 'vertexIndices': triangle.tolist(),
                        'chosenGridIndices': list(choice), 'chosenWeights': [float(grid[index]) for index in choice],
                        'beforeInvalidPhaseFaceCount': quality[0], 'afterInvalidPhaseFaceCount': trial_quality[0],
                        'beforeSeverity': quality[1], 'afterSeverity': trial_quality[1]}
                if best_quality[0] == 0 or attempts >= 256:
                    break
            if best_quality[0] == 0 or attempts >= 256:
                break
        # If isolated face blocks cannot clear a connected fold patch, solve the
        # currently failing faces together. Shared source vertices must receive one
        # identical weight, and the selected patch is held while its neighborhood
        # relaxes; this avoids one repaired face undoing another shared-face choice.
        patch_rows = [(int(t), joint_triangle_choices(int(t), labels, limit=16)) for t in bad_triangles]
        if patch_rows and all(choices for _, choices in patch_rows):
            patch_rows.sort(key=lambda row: (len(row[1]), row[0]))
            complete_blocks = []

            def collect_patch(index, assigned):
                if len(complete_blocks) >= 24:
                    return
                if index == len(patch_rows):
                    complete_blocks.append(dict(assigned))
                    return
                _, choices = patch_rows[index]
                for choice in choices:
                    triangle = triangles[patch_rows[index][0]].astype(int)
                    additions = {int(vertex): int(value) for vertex, value in zip(triangle, choice)}
                    if any(vertex in assigned and assigned[vertex] != value for vertex, value in additions.items()):
                        continue
                    updated = dict(assigned)
                    updated.update(additions)
                    collect_patch(index + 1, updated)
                    if len(complete_blocks) >= 24:
                        return

            collect_patch(0, {})
            for block in complete_blocks:
                attempts += 1
                trial = labels.copy()
                for vertex, value in block.items():
                    trial[vertex] = value
                trial, trial_sweeps = coordinate_descent(trial, locked | set(block), 96)
                trial_quality, _ = shape_quality(trial)
                sweeps += trial_sweeps
                if trial_quality < best_quality:
                    best_field = trial
                    best_quality = trial_quality
                    best_repair = {'triangleIds': [triangle_id for triangle_id in bad_triangles],
                        'vertexIndices': sorted(block), 'chosenGridIndices': {str(k): int(v) for k, v in sorted(block.items())},
                        'chosenWeights': {str(k): float(grid[v]) for k, v in sorted(block.items())},
                        'beforeInvalidPhaseFaceCount': quality[0], 'afterInvalidPhaseFaceCount': trial_quality[0],
                        'beforeSeverity': quality[1], 'afterSeverity': trial_quality[1], 'repairKind': 'shared-face-block'}
                if best_quality[0] == 0:
                    break
        if best_field is None:
            raise ValueError(f'contact-feasible field has no improving source-topology block; invalid triangles={bad_triangles[:32]}, invalidPhaseFaceCount={quality[0]}, attempts={attempts}')
        labels = best_field
        repairs.append(best_repair)
        quality, bad_triangles = shape_quality(labels)
    if quality[0]:
        raise ValueError(f'contact-feasible field did not converge after source-topology blocks; invalid triangles={bad_triangles[:32]}, invalidPhaseFaceCount={quality[0]}, attempts={attempts}, repairs={repairs}')
    return grid[labels], sweeps, repairs, coupled_records


def source_frame_contact_feasible_weights(rest, triangles, initial, fixed, moving, pivot, axis,
                                          degrees, samples, contacts, method='linear_blend',
                                          phase_subdivisions_per_segment=4,
                                          smoothness=DEFAULT_SMOOTHNESS, cache_path=None):
    """Solve a source-specific blend field feasible against sampled source bones.

    `contacts` rows are (sourceKey, role, boneRestWorld, boneTriangles, baselineInside).
    The baseline allows only the exact pre-existing containment points; every new
    sampled inside point is disallowed. Authored fixed/moving endpoint masks remain
    exact. Contact-feasible values are selected as a topology-smoothed field while
    minimizing departure from the input per-vertex weights.
    """
    rest = np.asarray(rest, dtype=float)
    triangles = np.asarray(triangles, dtype=np.int64)
    initial = np.asarray(initial, dtype=float)
    pivot = np.asarray(pivot, dtype=float)
    axis = np.asarray(axis, dtype=float)
    if len(initial) != len(rest) or not np.isfinite(initial).all() or initial.min() < 0 or initial.max() > 1:
        raise ValueError('finite authored [0,1] source weight field required')
    if samples < 4 or samples > 16:
        raise ValueError('motion sampling count outside the T66 authoring contract')
    if phase_subdivisions_per_segment < 1 or phase_subdivisions_per_segment > 8:
        raise ValueError('contact phase subdivisions outside the T66 authoring contract')
    grid = np.linspace(0.0, 1.0, GRID_STEPS + 1)
    allowed = np.ones((len(rest), len(grid)), dtype=bool)
    candidate_frames_by_phase = []
    # GLTF LINEAR morph weights and bone TRS are also inspected between authored
    # keys. Constrain a denser source trajectory here so the chosen field is not
    # only feasible at the sparse export keys.
    phase_count = samples * phase_subdivisions_per_segment
    tested_phases = [step / phase_count for step in range(1, phase_count + 1)]
    cache_material = [rest.astype('<f8').tobytes(), triangles.astype('<i8').tobytes(),
        np.asarray(fixed, dtype='<i8').tobytes(), np.asarray(moving, dtype='<i8').tobytes(),
        pivot.astype('<f8').tobytes(), axis.astype('<f8').tobytes(),
        json.dumps({'degrees': degrees, 'samples': samples, 'subdivisions': phase_subdivisions_per_segment,
                    'method': method, 'contactKeys': [row[0] for row in contacts]}, sort_keys=True).encode()]
    for key, role, bone_rest, bone_triangles, baseline in contacts:
        cache_material.extend([key.encode(), role.encode(), np.asarray(bone_rest, dtype='<f8').tobytes(),
            np.asarray(bone_triangles, dtype='<i8').tobytes(), np.asarray(baseline, dtype=np.uint8).tobytes()])
    cache_key = hashlib.sha256(b''.join(cache_material)).hexdigest()
    cached = False
    cache_file = Path(cache_path) if cache_path else None
    if cache_file and cache_file.exists():
        cache_doc = json.loads(cache_file.read_text())
        if cache_doc.get('schemaVersion') != 't66-contact-feasibility-cache-v1' or cache_doc.get('cacheKey') != cache_key:
            raise ValueError(f'contact feasibility cache hash mismatch: {cache_file}')
        allowed = np.asarray(cache_doc.get('allowed'), dtype=bool)
        if allowed.shape != (len(rest), len(grid)):
            raise ValueError(f'contact feasibility cache dimensions changed: {cache_file}')
        cached = True
    else:
        for phase in tested_phases:
            matrix = _rotation(axis, np.radians(degrees) * phase)
            if method == 'fractional_rotation':
                candidate_frames = np.vstack([_candidate_frame(rest, pivot, axis, degrees, phase,
                                                                  np.full(len(rest), weight), method)
                                              for weight in grid])
            else:
                rotated = (rest - pivot) @ matrix.T + pivot
                candidate_frames = np.vstack([rest + weight * (rotated - rest) for weight in grid])
            candidate_frames_by_phase.append(candidate_frames.reshape(len(grid), len(rest), 3))
            for _, role, bone_rest, bone_triangles, baseline in contacts:
                bone_pose = (bone_rest - pivot) @ matrix.T + pivot if role == 'moving_structure' else bone_rest
                inside_rows = _bounded_inside(candidate_frames, bone_pose,
                    np.asarray(bone_triangles, dtype=np.int64)).reshape(len(grid), len(rest)).T
                allowed &= ~(inside_rows & ~baseline[:, None])
        if cache_file:
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            if cache_file.exists():
                raise ValueError(f'contact feasibility cache appeared during write; preserving existing file: {cache_file}')
            cache_file.write_text(json.dumps({'schemaVersion':'t66-contact-feasibility-cache-v1',
                'cacheKey':cache_key, 'testedPhases':tested_phases, 'contactSourceKeys':[row[0] for row in contacts],
                'allowed':allowed.astype(int).tolist()}, separators=(',',':'))+'\n')
    if cached:
        for phase in tested_phases:
            matrix = _rotation(axis, np.radians(degrees) * phase)
            if method == 'fractional_rotation':
                candidate_frames = np.vstack([_candidate_frame(rest, pivot, axis, degrees, phase,
                                                                  np.full(len(rest), weight), method)
                                              for weight in grid])
            else:
                rotated = (rest - pivot) @ matrix.T + pivot
                candidate_frames = np.vstack([rest + weight * (rotated - rest) for weight in grid])
            candidate_frames_by_phase.append(candidate_frames.reshape(len(grid), len(rest), 3))
    rows = np.unique(np.sort(np.concatenate((triangles[:, [0, 1]], triangles[:, [1, 2]], triangles[:, [2, 0]]), axis=0), axis=1), axis=0)
    lengths = np.maximum(np.linalg.norm(rest[rows[:, 0]] - rest[rows[:, 1]], axis=1), 1e-8)
    weights = 1.0 / lengths
    weights /= weights.mean()
    candidate_frames_by_phase = np.stack(candidate_frames_by_phase, axis=0)
    # Geometry optimization uses every output key and the actual key midpoints
    # (1/16 in this eight-key authoring contract). Contact feasibility above was
    # evaluated more densely at 1/32 intervals.
    shape_candidate_frames = candidate_frames_by_phase[1::2]
    final, sweeps, repairs, _ = _solve_contact_and_shape_field(allowed, initial, fixed, moving,
        triangles, rest, shape_candidate_frames, rows, weights, grid, smoothness)
    intervals = [_intervals(row) for row in allowed]
    metric = {
        'method': 'source_frame_contact_feasible_topology_smoothed_weight_field',
        'testedPhases': tested_phases,
        'contactFeasibilityCacheKey': cache_key,
        'contactFeasibilityCachePath': str(cache_file) if cache_file else None,
        'contactFeasibilityCacheReused': cached,
        'contactSourceKeys': [row[0] for row in contacts],
        'verticesWithoutFeasibleWeight': np.flatnonzero(~allowed.any(axis=1)).tolist(),
        'verticesWithMultipleFeasibleIntervals': [i for i, row in enumerate(intervals) if len(row) > 1],
        'feasibleIntervalsByVertex': intervals,
        'gridSteps': GRID_STEPS,
        'phaseSubdivisionsPerSegment': phase_subdivisions_per_segment,
        'smoothnessCoefficient': smoothness,
        'shapeConstraints': {'normalOrientationPreserved': True, 'minimumAreaRatio': 0.1,
            'testedTriangleCount': int(len(triangles)), 'testedPhaseCount': int(len(tested_phases))},
        'convergedSweeps': sweeps,
        'shapeRepairBlocks': repairs,
        'authoredWeightFieldSha256': __import__('hashlib').sha256(np.asarray(initial, dtype='<f8').tobytes()).hexdigest(),
        'finalWeightFieldSha256': __import__('hashlib').sha256(np.asarray(final, dtype='<f8').tobytes()).hexdigest(),
        'changedVertexCount': int((np.abs(final - initial) > 1e-9).sum()),
        'changedOver025VertexCount': int((np.abs(final - initial) > 0.025).sum()),
        'meanAbsoluteWeightChange': float(np.abs(final - initial).mean()),
        'maximumAbsoluteWeightChange': float(np.abs(final - initial).max()),
        'authoredMaxAdjacentWeightDifference': float(np.abs(initial[rows[:, 0]] - initial[rows[:, 1]]).max()),
        'finalMaxAdjacentWeightDifference': float(np.abs(final[rows[:, 0]] - final[rows[:, 1]]).max()),
        'endpointMasksPreserved': bool(np.all(final[fixed] == 0) and np.all(final[moving] == 1)),
        'measuredAnatomicalAxis': False,
        'measuredAttachmentFootprints': False,
    }
    return final, metric


def source_phase_contact_feasible_weight_fields(rest, triangles, initial, fixed, moving, pivot, axis,
                                                degrees, samples, contacts, method='linear_blend',
                                                smoothness=DEFAULT_SMOOTHNESS,
                                                interpolation_subdivisions=4,
                                                coupled_vertex_groups=(),
                                                coupled_group_active_steps=None):
    """Author a temporally blended source-specific weight field at each motion key.

    Unlike a single field constrained by the intersection of all contact states,
    each key is solved against its exact pinned source-frame pose. The original
    masks/topology remain fixed, and the preceding field is a soft carry-forward
    target so adjacent keys do not jump arbitrarily. Final GLB interpolation and
    bone containment still require independent emitted-asset verification.
    """
    rest = np.asarray(rest, dtype=float)
    triangles = np.asarray(triangles, dtype=np.int64)
    initial = np.asarray(initial, dtype=float)
    pivot = np.asarray(pivot, dtype=float)
    axis = np.asarray(axis, dtype=float)
    grid = np.linspace(0.0, 1.0, GRID_STEPS + 1)
    rows = np.unique(np.sort(np.concatenate((triangles[:, [0, 1]], triangles[:, [1, 2]],
                                             triangles[:, [2, 0]]), axis=0), axis=1), axis=0)
    lengths = np.maximum(np.linalg.norm(rest[rows[:, 0]] - rest[rows[:, 1]], axis=1), 1e-8)
    edge_weights = 1.0 / lengths
    edge_weights /= edge_weights.mean()
    if interpolation_subdivisions < 1 or interpolation_subdivisions > 8:
        raise ValueError('morph interpolation subdivisions outside the T66 authoring contract')
    fields = []
    phase_records = []
    previous = initial.copy()
    previous_points = rest.copy()
    for step in range(1, samples + 1):
        phase = step / samples
        candidate_key_frames = np.stack([_candidate_frame(rest, pivot, axis, degrees, phase,
            np.full(len(rest), weight), method) for weight in grid], axis=0)
        allowed = np.ones((len(rest), len(grid)), dtype=bool)
        candidate_pose_sets = []
        interval_contact_counts = []
        for interpolation_step in range(1, interpolation_subdivisions + 1):
            alpha = interpolation_step / interpolation_subdivisions
            interval_phase = ((step - 1) + alpha) / samples
            candidate_pose = previous_points[None, :, :] + alpha * (candidate_key_frames - previous_points[None, :, :])
            candidate_pose_sets.append(candidate_pose)
            matrix = _rotation(axis, np.radians(degrees) * interval_phase)
            contact_counts = {}
            for key, role, bone_rest, bone_triangles, baseline in contacts:
                bone_pose = (np.asarray(bone_rest, dtype=float) - pivot) @ matrix.T + pivot if role == 'moving_structure' else np.asarray(bone_rest, dtype=float)
                # The candidate weight grid produces many points that cannot be
                # inside a source bone because they lie outside its exact AABB.
                # Keep the same winding test for the remaining points, but use
                # the existing conservative bounds rejection before the expensive
                # triangle query. This makes denser interpolation constraints
                # practical without changing the accepted geometry predicate.
                occupied = _bounded_inside(candidate_pose.reshape(-1, 3), bone_pose,
                    np.asarray(bone_triangles, dtype=np.int64)).reshape(len(grid), len(rest)).T
                disallowed = occupied & ~np.asarray(baseline, dtype=bool)[:, None]
                allowed &= ~disallowed
                contact_counts[key] = int(disallowed.sum())
            interval_contact_counts.append({'alpha': alpha, 'phase': interval_phase, 'disallowedCandidatePointCountByBone': contact_counts})
        if not allowed.any(axis=1).all():
            missing = np.flatnonzero(~allowed.any(axis=1)).tolist()
            raise ValueError(f'phase-specific contact/interpolation field has no feasible value at key={step}/{samples}; source vertices={missing[:32]}')
        if not allowed[np.asarray(fixed, dtype=int), 0].all() or not allowed[np.asarray(moving, dtype=int), -1].all():
            raise ValueError(f'phase-specific source field conflicts with authored endpoint masks at key={step}/{samples}')
        # Carry forward half of the previous authored transition while retaining
        # half of the source-derived smooth field as a soft objective, not a hard
        # attachment/landmark assertion.
        target = initial.copy() if step == 1 else initial * .5 + previous * .5
        active_groups = coupled_vertex_groups if coupled_group_active_steps is None or step in set(coupled_group_active_steps) else ()
        try:
            final, sweeps, repairs, coupled_records = _solve_contact_and_shape_field(allowed, target, fixed, moving,
                triangles, rest, np.stack(candidate_pose_sets, axis=0), rows, edge_weights, grid, smoothness,
                coupled_vertex_groups=active_groups)
        except ValueError as error:
            raise ValueError(f'phase key {step}/{samples} ({phase:.6f}) interpolation-contact-shape solve: {error}') from error
        fields.append(final)
        phase_records.append({'step': step, 'phase': phase, 'testedContactSourceKeys': [row[0] for row in contacts],
            'interpolationSubdivisions': interpolation_subdivisions,
            'sourceTopologyCouplingActive': bool(active_groups),
            'intervalContactTests': interval_contact_counts, 'allowedStateCountByVertex': allowed.sum(1).astype(int).tolist(),
            'allowedFieldSha256': hashlib.sha256(allowed.astype(np.uint8).tobytes()).hexdigest(),
            'previousFieldTargetSha256': hashlib.sha256(np.asarray(target, dtype='<f8').tobytes()).hexdigest(),
            'resultFieldSha256': hashlib.sha256(np.asarray(final, dtype='<f8').tobytes()).hexdigest(),
            'shapeRepairBlocks': repairs, 'coupledSourceTopologyGroups': coupled_records,
            'solverSweeps': sweeps,
            'endpointMasksPreserved': bool(np.all(final[fixed] == 0) and np.all(final[moving] == 1))})
        previous = final
        previous_points = _candidate_frame(rest, pivot, axis, degrees, phase, final, method)
    metric = {'method': 'source_phase_contact_and_topology_feasible_weight_fields',
        'candidateGridSteps': GRID_STEPS, 'samples': samples, 'testedKeyPhases': [r['phase'] for r in phase_records],
        'interpolationSubdivisions': interpolation_subdivisions,
        'coupledVertexGroups': [sorted(set(int(v) for v in group)) for group in coupled_vertex_groups],
        'coupledGroupActiveSteps': list(coupled_group_active_steps) if coupled_group_active_steps is not None else None,
        'minimumAreaRatio': .1, 'normalOrientationPreserved': True,
        'temporallyBlendedObjective': 'half original authored field and half previous key field for keys after the first',
        'measuredAnatomicalAxis': False, 'measuredAttachmentFootprints': False,
        'phaseRecords': phase_records,
        'fieldHash': hashlib.sha256(b''.join(np.asarray(row, dtype='<f8').tobytes() for row in fields)).hexdigest(),
        'weightFields': [np.asarray(row, dtype=float).tolist() for row in fields]}
    return fields, metric
