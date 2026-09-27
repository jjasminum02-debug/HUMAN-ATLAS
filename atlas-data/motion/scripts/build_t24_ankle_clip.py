#!/usr/bin/env python3
"""Deterministically derive the T24 illustrative ankle clip from the exact T44 GLB.

Only the source ankle_r joint rotates. The three-point OpenSim model path is
animated with endpoint-local morph targets; it is not a muscle surface model.
"""
from __future__ import annotations

import hashlib
import json
import math
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'atlas-data/assets/derived-glb/opensim-gait2392-t44-right-ankle/right-ankle-rest.glb'
BINDING = ROOT / 'atlas-data/assets/derived-glb/opensim-gait2392-t44-right-ankle/joint-binding-t44.json'
OUTPUT = ROOT / 'atlas-data/assets/motion/t24-right-tibialis-anterior/ankle-dorsiflexion.glb'
MANIFEST = OUTPUT.with_suffix('.json')
SOURCE_SHA = 'a33f043be46c7b628bc649777e190c9e7d7cba345f07795e080820545261bed0'
ANGLES = (0.0, 0.06, 0.12)  # radians, editorial demonstration only; not a normal clinical range
TIMES = (0.0, 1.0, 2.0)
CLIP_ID = 'HA-CLIP-T24-R-TIBANT-ANKLE-DF-V1'


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_glb(data: bytes) -> tuple[dict, bytearray]:
    magic, version, length = struct.unpack_from('<III', data)
    assert (magic, version, length) == (0x46546c67, 2, len(data))
    jlen, jkind = struct.unpack_from('<II', data, 12)
    assert jkind == 0x4e4f534a
    document = json.loads(data[20:20+jlen])
    offset = 20 + jlen
    blen, bkind = struct.unpack_from('<II', data, offset)
    assert bkind == 0x004e4942
    blob = bytearray(data[offset+8:offset+8+blen])
    assert not any('uri' in row for row in document['buffers'])
    assert not any('uri' in row for row in document.get('images', []))
    return document, blob


def encode_glb(document: dict, blob: bytearray) -> bytes:
    document['buffers'][0]['byteLength'] = len(blob)
    jb = json.dumps(document, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    jb += b' ' * (-len(jb) % 4)
    bb = bytes(blob) + b'\0' * (-len(blob) % 4)
    length = 12 + 8 + len(jb) + 8 + len(bb)
    return struct.pack('<III', 0x46546c67, 2, length) + struct.pack('<II', len(jb), 0x4e4f534a) + jb + struct.pack('<II', len(bb), 0x004e4942) + bb


def append_accessor(document: dict, blob: bytearray, values: tuple[float, ...], kind: str) -> int:
    assert kind in ('SCALAR', 'VEC3', 'VEC4')
    count = len(values) // {'SCALAR': 1, 'VEC3': 3, 'VEC4': 4}[kind]
    assert count * {'SCALAR': 1, 'VEC3': 3, 'VEC4': 4}[kind] == len(values)
    blob.extend(b'\0' * (-len(blob) % 4))
    offset = len(blob)
    blob.extend(struct.pack('<' + 'f' * len(values), *values))
    view = len(document['bufferViews'])
    document['bufferViews'].append({'buffer': 0, 'byteOffset': offset, 'byteLength': len(values)*4})
    accessor = len(document['accessors'])
    row = {'bufferView': view, 'componentType': 5126, 'count': count, 'type': kind}
    if kind == 'SCALAR':
        row['min'] = [min(values)]
        row['max'] = [max(values)]
    elif kind == 'VEC3':
        row['min'] = [min(values[i::3]) for i in range(3)]
        row['max'] = [max(values[i::3]) for i in range(3)]
    document['accessors'].append(row)
    return accessor


def rotate(point: tuple[float, ...], pivot: tuple[float, ...], axis: tuple[float, ...], angle: float) -> tuple[float, float, float]:
    v = [point[i] - pivot[i] for i in range(3)]
    co, si = math.cos(angle), math.sin(angle)
    cross = (axis[1]*v[2]-axis[2]*v[1], axis[2]*v[0]-axis[0]*v[2], axis[0]*v[1]-axis[1]*v[0])
    dot = sum(axis[i]*v[i] for i in range(3))
    return tuple(pivot[i] + v[i]*co + cross[i]*si + axis[i]*dot*(1-co) for i in range(3))


def main() -> None:
    data = SOURCE.read_bytes()
    if sha(data) != SOURCE_SHA:
        raise SystemExit('T44 GLB hash changed; derivation is stopped')
    binding = json.loads(BINDING.read_text())
    document, blob = read_glb(data)
    assert len(document['nodes']) == 10 and not document.get('animations')
    assert document['nodes'][3]['name'] == 'ankle_r_pivot_q0'
    assert document['nodes'][9]['name'] == 'tib_ant_r_model_path_q0'
    assert document['meshes'][5]['primitives'][0]['mode'] == 1
    joint = binding['jointBinding']
    axis = tuple(joint['axisSceneJointFrame'])
    norm = math.sqrt(sum(x*x for x in axis))
    axis = tuple(x/norm for x in axis)
    pivot = tuple(joint['pivotSceneTibiaLocalM'])
    p = [tuple(row['restWorldSceneM']) for row in binding['modelPath']['points']]
    assert len(p) == 3
    base = document['accessors'][10]
    view = document['bufferViews'][base['bufferView']]
    off = view.get('byteOffset', 0) + base.get('byteOffset', 0)
    actual = struct.unpack_from('<9f', blob, off)
    assert max(abs(actual[i]-p[i//3][i%3]) for i in range(9)) < 1e-6

    samples = [rotate(p[2], pivot, axis, angle) for angle in ANGLES]
    targets = []
    for endpoint in samples[1:]:
        delta = tuple(endpoint[i]-p[2][i] for i in range(3))
        targets.append({'POSITION': append_accessor(document, blob, (0.,)*6 + delta, 'VEC3')})
    path_mesh = document['meshes'][5]
    path_mesh['primitives'][0]['targets'] = targets
    path_mesh['weights'] = [0.0, 0.0]
    path_mesh['extras'] = {'meaning': 'OpenSim tib_ant_r simplified model path, not attachment surface or muscle contraction'}
    time_accessor = append_accessor(document, blob, TIMES, 'SCALAR')
    quats = tuple(value for angle in ANGLES for value in (*[v*math.sin(angle/2) for v in axis], math.cos(angle/2)))
    rot_accessor = append_accessor(document, blob, quats, 'VEC4')
    weight_accessor = append_accessor(document, blob, (0., 0., 1., 0., 0., 1.), 'SCALAR')
    document['animations'] = [{
        'name': CLIP_ID,
        'samplers': [
            {'input': time_accessor, 'output': rot_accessor, 'interpolation': 'LINEAR'},
            {'input': time_accessor, 'output': weight_accessor, 'interpolation': 'LINEAR'},
        ],
        'channels': [
            {'sampler': 0, 'target': {'node': 3, 'path': 'rotation'}},
            {'sampler': 1, 'target': {'node': 9, 'path': 'weights'}},
        ],
    }]
    document.setdefault('asset', {})['generator'] = 'HUMAN ATLAS build_t24_ankle_clip.py v1; T44 GLB SHA-256 pinned'
    document['nodes'][3]['extras'] = {'joint': 'ankle_r', 'coordinate': 'ankle_angle_r', 'positiveDirection': 'dorsiflexion'}
    output = encode_glb(document, blob)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(output)
    manifest = {
        'revision': 'T24-2026-09-27-v1', 'script': 'atlas-data/motion/scripts/build_t24_ankle_clip.py',
        'scriptVersion': 't24-stdlib-glb-v1', 'scriptSha256': sha(Path(__file__).read_bytes()),
        'sourceStaticGlb': str(SOURCE.relative_to(ROOT)), 'sourceStaticSha256': SOURCE_SHA,
        'jointBinding': str(BINDING.relative_to(ROOT)), 'jointBindingSha256': sha(BINDING.read_bytes()),
        'sourceModel': binding['source']['modelPath'] if 'modelPath' in binding.get('source', {}) else 'OpenSim_Models/Models/Gait2392_Simbody/gait2392_thelen2003muscle.osim',
        'sourceModelSha256': '3af1ca20aa87bc88b0b8cd54f2504331afa2aa03537cc868f1175fa1f50f3c0f',
        'outputGlb': str(OUTPUT.relative_to(ROOT)), 'outputSha256': sha(output),
        'clipId': CLIP_ID, 'timesSeconds': TIMES, 'anglesRadians': ANGLES,
        'jointPivotSceneM': pivot, 'jointAxisScene': axis,
        'endpointSceneM': samples,
        'interpretation': 'Illustrative positive ankle_r coordinate from the T44 OpenSim model; not a normal angle, force, isolated-muscle movement, surface attachment or human review.',
        'annotationPolicy': {'verifiedBoneLocalBindings': [], 'hideAllSpatialAnnotationsDuringMotion': True},
        'sourceLicenseId': 'LIC-OPENSIM-GAIT2392-CC-BY-3.0',
        'sourceGeometryReuseNote': 'T44 model-derived GLB. Verify per-file VTP redistribution rights before public deployment.',
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(manifest['outputSha256'])


if __name__ == '__main__':
    main()
