"""Surface contacts between extracted structures (ROADMAP C3), computed from D1 geometry.

  blender --background --factory-startup --python atlas-data/pipeline/contacts_za.py
(Blender only for numpy + mathutils.kdtree; no .blend is opened.)
For every joint-layer structure and bursa: the bones its surface touches (nearest bone vertex within 3 mm).
For every fascia-layer structure, bursa and tendon: the muscles it touches (within 6 mm).
A target counts when it holds at least 4 % of the structure's touching vertices (and >= 3 vertices).
Writes source-cache/datasets/za-full/contacts.json keyed by structure id.
"""
import json
from pathlib import Path
import struct

import numpy as np
from mathutils import Vector
from mathutils.kdtree import KDTree

ROOT = Path(__file__).resolve().parents[2]
D1 = ROOT / 'atlas-data/source-cache/datasets/za-full'
BONE_MM, MUSCLE_MM, SHARE = 0.003, 0.006, 0.04
FASCIA_KINDS = {'fascia', 'aponeurosis', 'retinaculum', 'septum', 'raphe', 'sheath', 'connective'}


def positions(path, matrix):
    data = path.read_bytes()
    size = struct.unpack_from('<I', data, 12)[0]
    doc = json.loads(data[20:20 + size]); binary = data[20 + size + 8:]
    accessor = doc['accessors'][0]; view = doc['bufferViews'][accessor['bufferView']]
    p = np.frombuffer(binary, dtype='<f4', count=accessor['count'] * 3, offset=view.get('byteOffset', 0)).reshape(-1, 3).astype('f8')
    m = np.array(matrix, dtype='f8').reshape(4, 4).T  # column-major -> row-major
    return p @ m[:3, :3].T + m[:3, 3]


def tree(structures):
    points, owner = [], []
    for s in structures:
        p = positions(D1 / s['lods']['overview']['path'], s['matrix'])
        points.append(p); owner += [s['id']] * len(p)
    points = np.concatenate(points)
    kd = KDTree(len(points))
    for i, co in enumerate(points): kd.insert(Vector(co), i)
    kd.balance()
    return kd, owner


def contacts(s, kd, owner, radius):
    counts = {}
    for co in positions(D1 / s['lods']['detail']['path'], s['matrix']):
        _, index, distance = kd.find(Vector(co))
        if index is not None and distance <= radius:
            counts[owner[index]] = counts.get(owner[index], 0) + 1
    total = sum(counts.values())
    return [{'id': k, 'vertices': n} for k, n in sorted(counts.items(), key=lambda kv: -kv[1]) if n >= 3 and n >= SHARE * total]


def main():
    structures = json.loads((D1 / 'structures.json').read_text())['structures']
    bones = [s for s in structures if s['system'] == 'skeletal' and s['kind'] in ('bone', 'cartilage')]
    muscles = [s for s in structures if s['system'] == 'muscular' and s['kind'] in ('muscle', 'tendon')]
    bone_kd, bone_owner = tree(bones)
    muscle_kd, muscle_owner = tree(muscles)
    out = {}
    for s in structures:
        joint_like = s['system'] == 'joint' or s['kind'] in ('bursa', 'ligament')
        wraps = s['kind'] in FASCIA_KINDS or s['kind'] in ('bursa', 'tendon')
        if not (joint_like or wraps):
            continue
        row = {}
        if joint_like or s['kind'] in FASCIA_KINDS:
            row['bones'] = contacts(s, bone_kd, bone_owner, BONE_MM)
        if wraps:
            row['muscles'] = [m for m in contacts(s, muscle_kd, muscle_owner, MUSCLE_MM) if m['id'] != s['id']]
        out[s['id']] = row
    (D1 / 'contacts.json').write_text(json.dumps({'schemaVersion': 1, 'boneRadiusMetres': BONE_MM, 'muscleRadiusMetres': MUSCLE_MM,
                                                 'minimumShare': SHARE, 'contacts': out}, ensure_ascii=False) + '\n')
    print('CONTACTS', len(out), 'with bones', sum(bool(r.get('bones')) for r in out.values()),
          'with muscles', sum(bool(r.get('muscles')) for r in out.values()), flush=True)


main()
