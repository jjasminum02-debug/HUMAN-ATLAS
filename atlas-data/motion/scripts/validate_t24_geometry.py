#!/usr/bin/env python3
"""Reproduce T24 three-pose geometry, endpoint and coarse collision checks."""
from __future__ import annotations

import hashlib
import json
import math
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ASSET = ROOT / 'atlas-data/assets/motion/t24-right-tibialis-anterior/ankle-dorsiflexion.glb'
MANIFEST = ASSET.with_suffix('.json')
BINDING = ROOT / 'atlas-data/assets/derived-glb/opensim-gait2392-t44-right-ankle/joint-binding-t44.json'
RESULT = ROOT / 'work/evidence/T24/geometry-qa.json'


def sub(a, b): return tuple(a[i]-b[i] for i in range(3))
def add(a, b): return tuple(a[i]+b[i] for i in range(3))
def dot(a, b): return sum(a[i]*b[i] for i in range(3))
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def norm(a): return math.sqrt(dot(a, a))


def rotate(v, axis, angle):
    co, si = math.cos(angle), math.sin(angle)
    return add(add(tuple(x*co for x in v), tuple(x*si for x in cross(axis, v))), tuple(x*dot(axis, v)*(1-co) for x in axis))


def segment_triangle(p, q, triangle) -> bool:
    a, b, c = triangle
    direction = sub(q, p)
    e1, e2 = sub(b, a), sub(c, a)
    h = cross(direction, e2)
    det = dot(e1, h)
    if abs(det) < 1e-11: return False
    inv = 1/det
    s = sub(p, a)
    u = inv*dot(s, h)
    if u < -1e-8 or u > 1+1e-8: return False
    v = inv*dot(direction, cross(s, e1))
    if v < -1e-8 or u+v > 1+1e-8: return False
    t = inv*dot(e2, cross(s, e1))
    return -1e-8 <= t <= 1+1e-8


def triangle_intersection(a, b) -> bool:
    return any(segment_triangle(a[i], a[(i+1)%3], b) for i in range(3)) or any(segment_triangle(b[i], b[(i+1)%3], a) for i in range(3))


def bounds(points): return tuple((min(p[i] for p in points), max(p[i] for p in points)) for i in range(3))
def overlap(a, b): return tuple(max(0, min(a[i][1], b[i][1])-max(a[i][0], b[i][0])) for i in range(3))


def main() -> None:
    manifest, binding = [json.loads(p.read_text()) for p in (MANIFEST, BINDING)]
    data = ASSET.read_bytes()
    assert hashlib.sha256(data).hexdigest() == manifest['outputSha256']
    n = struct.unpack_from('<I', data, 12)[0]
    doc = json.loads(data[20:20+n])
    binary_offset = 20+n+8
    assert len(doc['animations']) == 1 and len(doc['animations'][0]['channels']) == 2
    assert all('uri' not in b for b in doc['buffers']) and all('uri' not in b for b in doc.get('images', []))
    parent = {child: index for index, node in enumerate(doc['nodes']) for child in node.get('children', [])}
    node_by_mesh = {node['mesh']: i for i, node in enumerate(doc['nodes']) if 'mesh' in node}
    axis = tuple(manifest['jointAxisScene'])
    meshes = []
    for mesh_index, mesh in enumerate(doc['meshes'][:5]):
        primitive = mesh['primitives'][0]
        def accessor(index):
            a = doc['accessors'][index]
            v = doc['bufferViews'][a['bufferView']]
            offset = binary_offset + v.get('byteOffset', 0) + a.get('byteOffset', 0)
            return a, offset
        pa, po = accessor(primitive['attributes']['POSITION'])
        positions = [struct.unpack_from('<fff', data, po+12*i) for i in range(pa['count'])]
        ia, io = accessor(primitive['indices'])
        code, stride = {5121: ('B', 1), 5123: ('H', 2), 5125: ('I', 4)}[ia['componentType']]
        indices = struct.unpack_from('<' + code*ia['count'], data, io)
        assert len(indices)%3 == 0
        meshes.append((positions, indices, node_by_mesh[mesh_index]))

    def transform(point, node_index, angle):
        while True:
            node = doc['nodes'][node_index]
            if node_index == 3: point = rotate(point, axis, angle)
            point = add(point, node.get('translation', (0, 0, 0)))
            if node_index not in parent: return point
            node_index = parent[node_index]

    rows = []
    for sample_index, angle in enumerate(manifest['anglesRadians']):
        world = [[transform(v, node_index, angle) for v in positions] for positions, _, node_index in meshes]
        fixed, moving = world[:2], world[2:]
        # Source P3 is calcn_r-local, so compare its transformed output to the path morph sample.
        rest_p3 = tuple(binding['modelPath']['points'][2]['restWorldSceneM'])
        pivot = tuple(binding['jointBinding']['pivotSceneTibiaLocalM'])
        p3 = add(pivot, rotate(sub(rest_p3, pivot), axis, angle))
        expected = tuple(manifest['endpointSceneM'][sample_index])
        endpoint_gap = norm(sub(p3, expected))
        assert endpoint_gap < 1e-7
        p1 = tuple(binding['modelPath']['points'][0]['restWorldSceneM'])
        p2 = tuple(binding['modelPath']['points'][1]['restWorldSceneM'])
        path_length = norm(sub(p2, p1)) + norm(sub(p3, p2))
        toe_pivot = transform((0, 0, 0), 7, angle)
        pairs = []
        for f in range(2):
            for m in range(2, 5):
                fb, mb = bounds(world[f]), bounds(world[m])
                extents = overlap(fb, mb)
                # AABB is deliberately conservative; mesh-level contact is assessed below.
                intersection_count = 0
                if all(v > 0 for v in extents):
                    fi, mi = meshes[f][1], meshes[m][1]
                    ft = [(world[f][fi[i]], world[f][fi[i+1]], world[f][fi[i+2]]) for i in range(0, len(fi), 3)]
                    mt = [(world[m][mi[i]], world[m][mi[i+1]], world[m][mi[i+2]]) for i in range(0, len(mi), 3)]
                    ftb = [bounds(t) for t in ft]
                    mtb = [bounds(t) for t in mt]
                    for i, ta in enumerate(ft):
                        for j, tb in enumerate(mt):
                            if all(v > 0 for v in overlap(ftb[i], mtb[j])) and triangle_intersection(ta, tb):
                                intersection_count += 1
                pairs.append({'fixedMesh': doc['meshes'][f]['name'], 'movingMesh': doc['meshes'][m]['name'],
                              'aabbOverlapM': extents, 'triangleIntersectionPairs': intersection_count})
        rows.append({'timeSeconds': manifest['timesSeconds'][sample_index], 'ankleAngleRadians': angle,
                     'anteriorFootPivotY': toe_pivot[1], 'pathEndpointGapM': endpoint_gap,
                     'illustrativeModelPathLengthM': path_length,
                     'fixedTibiaOrigin': transform((0, 0, 0), 0, angle), 'pairs': pairs})
    assert rows[0]['anteriorFootPivotY'] < rows[1]['anteriorFootPivotY'] < rows[2]['anteriorFootPivotY']
    assert rows[2]['anteriorFootPivotY'] - rows[0]['anteriorFootPivotY'] > 0.01
    assert rows[0]['illustrativeModelPathLengthM'] > rows[1]['illustrativeModelPathLengthM'] > rows[2]['illustrativeModelPathLengthM']
    assert all(row['fixedTibiaOrigin'] == (0, 0, 0) for row in rows)
    baseline = {(p['fixedMesh'], p['movingMesh']): p['triangleIntersectionPairs'] for p in rows[0]['pairs']}
    new_intersections = []
    for row in rows[1:]:
        for pair in row['pairs']:
            key = (pair['fixedMesh'], pair['movingMesh'])
            if pair['triangleIntersectionPairs'] > baseline[key]:
                new_intersections.append({'timeSeconds': row['timeSeconds'], **pair, 'baseline': baseline[key]})
    result = {'assetSha256': manifest['outputSha256'], 'sourceStaticSha256': manifest['sourceStaticSha256'],
              'poseChecks': rows, 'newFixedMovingIntersections': new_intersections,
              'majorPenetrationPass': not new_intersections,
              'method': 'sample all fixed tibia/fibula vs moving talus/foot/toes triangles at three poses; broad AABB then 3D edge/triangle intersection; planar or inside-only contacts can escape this check'}
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'majorPenetrationPass': result['majorPenetrationPass'], 'newFixedMovingIntersections': len(new_intersections),
                      'toeY': [row['anteriorFootPivotY'] for row in rows],
                      'pairCounts': [[p['triangleIntersectionPairs'] for p in row['pairs']] for row in rows]}))
    if new_intersections:
        raise SystemExit('New fixed-moving mesh triangle intersections require review')


if __name__ == '__main__': main()
