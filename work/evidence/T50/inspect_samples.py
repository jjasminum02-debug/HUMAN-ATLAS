#!/usr/bin/env python3
"""Inspect real T50 sample files without changing source assets."""
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'work/evidence/T50/asset-sample-inspection.json'


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect_obj(rel):
    path = ROOT / rel
    vertices = []
    faces = []
    for line in path.read_text(errors='replace').splitlines():
        if line.startswith('v '):
            values = [float(value) for value in line.split()[1:4]]
            if len(values) == 3:
                vertices.append(values)
        elif line.startswith('f '):
            indices = [int(value.split('/')[0]) - 1 for value in line.split()[1:]]
            if len(indices) >= 3:
                faces.append(indices)
    minimum = [min(vertex[i] for vertex in vertices) for i in range(3)]
    maximum = [max(vertex[i] for vertex in vertices) for i in range(3)]
    edge_use = {}
    welded_edge_use = {}
    parent = list(range(len(vertices)))
    # This is deterministic coordinate quantization, not a geometric-radius weld.
    # Keep that distinction explicit in both the output field names and report.
    coordinate_keys = [tuple(round(value, 3) for value in vertex) for vertex in vertices]
    key_ids = {key: index for index, key in enumerate(sorted(set(coordinate_keys)))}
    welded_parent = list(range(len(key_ids)))

    def find(item):
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    def welded_find(item):
        while welded_parent[item] != item:
            welded_parent[item] = welded_parent[welded_parent[item]]
            item = welded_parent[item]
        return item

    def welded_union(a, b):
        ra, rb = welded_find(a), welded_find(b)
        if ra != rb:
            welded_parent[rb] = ra

    degenerate_triangles = 0
    triangulated_count = 0
    for face in faces:
        for a, b in zip(face, face[1:] + face[:1]):
            edge = tuple(sorted((a, b)))
            edge_use[edge] = edge_use.get(edge, 0) + 1
            wa, wb = key_ids[coordinate_keys[a]], key_ids[coordinate_keys[b]]
            welded_edge = tuple(sorted((wa, wb)))
            welded_edge_use[welded_edge] = welded_edge_use.get(welded_edge, 0) + 1
        for a, b in zip(face[1:-1], face[2:]):
            triangulated_count += 1
            va, vb, vc = vertices[face[0]], vertices[a], vertices[b]
            ab = [vb[i] - va[i] for i in range(3)]
            ac = [vc[i] - va[i] for i in range(3)]
            cross = [ab[1]*ac[2]-ab[2]*ac[1], ab[2]*ac[0]-ab[0]*ac[2], ab[0]*ac[1]-ab[1]*ac[0]]
            if sum(component*component for component in cross) < 1e-18:
                degenerate_triangles += 1
        for index in face[1:]:
            union(face[0], index)
            welded_union(key_ids[coordinate_keys[face[0]]], key_ids[coordinate_keys[index]])

    return {
        'file': rel,
        'bytes': path.stat().st_size,
        'sha256': sha256(path),
        'vertexCount': len(vertices),
        'polygonCount': len(faces),
        'fanTriangleCount': triangulated_count,
        'connectedVertexComponents': len({find(index) for index in range(len(vertices))}),
        'quantizedCoordinateComponentsAt001mm': len({welded_find(index) for index in range(len(key_ids))}),
        'duplicateCoordinateVertexCountAt001mm': len(vertices) - len(key_ids),
        'boundaryEdgeCount': sum(count == 1 for count in edge_use.values()),
        'quantizedCoordinateBoundaryEdgeCountAt001mm': sum(count == 1 for count in welded_edge_use.values()),
        'nonManifoldEdgeCount': sum(count > 2 for count in edge_use.values()),
        'quantizedCoordinateNonManifoldEdgeCountAt001mm': sum(count > 2 for count in welded_edge_use.values()),
        'degenerateTriangleCount': degenerate_triangles,
        'sourceBounds': {'min': minimum, 'max': maximum, 'unit': 'mm'},
        'topologyReview': 'computational QA only; anatomical identity and surface suitability remain unreviewed',
    }


def inspect_glb(rel):
    path = ROOT / rel
    data = path.read_bytes()
    magic, version, total_length = struct.unpack_from('<4sII', data, 0)
    if magic != b'glTF' or version != 2 or total_length != len(data):
        raise ValueError(f'Invalid GLB header: {rel}')
    offset = 12
    gltf = None
    binary_chunk_bytes = 0
    external_uris = []
    while offset < len(data):
        chunk_length, chunk_type = struct.unpack_from('<II', data, offset)
        offset += 8
        chunk = data[offset:offset + chunk_length]
        offset += chunk_length
        if chunk_type == 0x4E4F534A:
            gltf = json.loads(chunk.rstrip(b' \t\r\n\0'))
        elif chunk_type == 0x004E4942:
            binary_chunk_bytes = len(chunk)
    if gltf is None:
        raise ValueError(f'Missing JSON chunk: {rel}')
    for item in gltf.get('buffers', []) + gltf.get('images', []):
        uri = item.get('uri')
        if uri:
            external_uris.append(uri)
    nodes = gltf.get('nodes', [])
    meshes = gltf.get('meshes', [])
    node_rows = []
    for index, node in enumerate(nodes):
        if 'mesh' in node or 'children' in node or 'skin' in node:
            mesh_index = node.get('mesh')
            mesh_name = meshes[mesh_index].get('name') if mesh_index is not None else None
            primitive_rows = []
            if mesh_index is not None:
                for primitive in meshes[mesh_index].get('primitives', []):
                    position_accessor = primitive.get('attributes', {}).get('POSITION')
                    count = gltf.get('accessors', [])[position_accessor].get('count') if position_accessor is not None else None
                    primitive_rows.append({
                        'vertexCount': count,
                        'morphTargetCount': len(primitive.get('targets', [])),
                        'mode': primitive.get('mode', 4),
                    })
            node_rows.append({
                'index': index,
                'name': node.get('name'),
                'meshName': mesh_name,
                'meshIndex': mesh_index,
                'skinIndex': node.get('skin'),
                'children': node.get('children', []),
                'primitives': primitive_rows,
            })
    return {
        'file': rel,
        'bytes': len(data),
        'sha256': sha256(path),
        'glbVersion': version,
        'binaryChunkBytes': binary_chunk_bytes,
        'sceneCount': len(gltf.get('scenes', [])),
        'nodeCount': len(nodes),
        'meshCount': len(meshes),
        'skinCount': len(gltf.get('skins', [])),
        'animationCount': len(gltf.get('animations', [])),
        'externalUris': external_uris,
        'materialCount': len(gltf.get('materials', [])),
        'nodes': node_rows,
    }


obj_files = [
    'atlas-data/assets/bodyparts3d-v4-pilot/FJ1439.obj',  # right tibialis anterior
    'atlas-data/assets/bodyparts3d-v4-pilot/FJ3387.obj',  # right tibia
    'atlas-data/assets/bodyparts3d-v4-pilot/FJ3366.obj',  # right fibula
    'atlas-data/assets/bodyparts3d-v4-pilot/FJ3385.obj',  # right talus
    'atlas-data/assets/bodyparts3d-v4-pilot/FJ3360.obj',  # right calcaneus
]
glb_files = [
    'atlas-data/assets/derived-glb/bodyparts3d-r4-right-lower-leg/right-lower-leg.glb',
    'atlas-data/assets/derived-glb/bodyparts3d-r4-t13-right-bones/right-bones.glb',
    'atlas-data/assets/derived-glb/opensim-gait2392-t44-right-ankle/right-ankle-rest.glb',
    'atlas-data/assets/motion/t24-right-tibialis-anterior/ankle-dorsiflexion.glb',
]

result = {
    'task': 'T50',
    'checkedOn': '2026-09-27',
    'scope': 'actual local source and derived samples; read-only inspection',
    'objSamples': [inspect_obj(rel) for rel in obj_files],
    'glbSamples': [inspect_glb(rel) for rel in glb_files],
    'interpretation': {
        'bodyparts3dRightLowerLeg': '11 independent named nodes; same source-native scene frame; no hierarchy, skin, animation, or morph targets.',
        'opensimT44AndT24': 'T44 has nested joint-pivot hierarchy in a separate model frame; T24 animates that frame/path. The only morph targets belong to tib_ant_r_model_path_q0, a line/path mesh, not the BodyParts3D muscle surface.',
        'humanAnatomy': 'No anatomical suitability, standardized pose, attachment site, or motion was approved by this computational inspection.',
    },
}
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({
            'obj': [{k: row[k] for k in ('file', 'bytes', 'sha256', 'vertexCount', 'polygonCount', 'connectedVertexComponents', 'quantizedCoordinateComponentsAt001mm', 'boundaryEdgeCount', 'quantizedCoordinateBoundaryEdgeCountAt001mm', 'nonManifoldEdgeCount', 'quantizedCoordinateNonManifoldEdgeCountAt001mm', 'degenerateTriangleCount')} for row in result['objSamples']],
    'glb': [{k: row[k] for k in ('file', 'bytes', 'sha256', 'nodeCount', 'meshCount', 'skinCount', 'animationCount', 'externalUris')} for row in result['glbSamples']],
}, ensure_ascii=False, indent=2))
