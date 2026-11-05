"""Skin weights for soft tissue (ROADMAP M2): muscles, tendons, ligaments, capsules, fascia, vessels and nerves follow the rig.

  blender --background --factory-startup --python atlas-data/pipeline/build_skin.py
(Blender only for numpy + mathutils.kdtree.) Reads the exact runtime geometry chunks, so vertex order
matches what the app renders. Writes source-cache/datasets/za-v2/skin/<chunk>.bin.

Per vertex: distance to the bones of each allowed rig segment; weight ∝ exp(-(d - d_min) / SIGMA), the two
largest kept. Allowed segments are the rig chain between the bones a structure attaches to (muscles: ZA
origin/insertion patches; ligaments, capsules, fascia: surface contacts); with none, every segment.
Left/right meshes share geometry, so weights are stored by segment role ("femur") and resolved per side.
Approximation for teaching (linear blend), not soft-tissue mechanics.

Binary layout: uint32 header length, UTF-8 JSON header {resources: {key: {offset, vertices, roles}}},
then per vertex a little-endian uint16: slotA << 12 | slotB << 8 | round(255 * weightA).
"""
import json
from pathlib import Path
import struct

import numpy as np
from mathutils import Vector
from mathutils.kdtree import KDTree

ROOT = Path(__file__).resolve().parents[2]
D1 = ROOT / 'atlas-data/source-cache/datasets/za-full'
GEOMETRY = ROOT / 'atlas-data/source-cache/datasets/za-v2'
OUT = GEOMETRY / 'skin'
SIGMA = .012
NEAR, NEAR_SHARE = .02, .03  # a segment is "near" when >= 3 % of a structure's vertices lie within 2 cm of its bones
ROLE_ORDER = ['pelvis', 'torso', 'femur', 'patella', 'tibia', 'talus', 'calcn', 'toes', 'humerus', 'ulna', 'radius', 'hand']
SOFT_LAYERS = {'muscle', 'fascia', 'joint', 'vessel', 'nerve'}  # vessels (Q2-1) and nerves follow the bones they run along


def role(segment):
    return segment if segment in ('pelvis', 'torso') else segment[:-2]


def chunk_positions(path):
    """resource key -> local positions, from a packed chunk GLB (one mesh per resource)."""
    data = path.read_bytes(); size = struct.unpack_from('<I', data, 12)[0]
    doc = json.loads(data[20:20 + size]); binary = data[20 + size + 8:]
    out = {}
    for mesh in doc['meshes']:
        a = doc['accessors'][mesh['primitives'][0]['attributes']['POSITION']]; view = doc['bufferViews'][a['bufferView']]
        out[mesh['name']] = np.frombuffer(binary, dtype='<f4', count=a['count'] * 3,
                                          offset=view.get('byteOffset', 0) + a.get('byteOffset', 0)).reshape(-1, 3).astype('f8')
    return out


def world(points, matrix):
    m = np.array(matrix, dtype='f8').reshape(4, 4).T
    return points @ m[:3, :3].T + m[:3, 3]


def d1_positions(s):
    data = (D1 / s['lods']['detail']['path']).read_bytes(); size = struct.unpack_from('<I', data, 12)[0]
    doc = json.loads(data[20:20 + size]); binary = data[20 + size + 8:]
    a = doc['accessors'][0]; view = doc['bufferViews'][a['bufferView']]
    return world(np.frombuffer(binary, dtype='<f4', count=a['count'] * 3, offset=view.get('byteOffset', 0)).reshape(-1, 3).astype('f8'), s['matrix'])


def main():
    runtime = json.loads((ROOT / 'atlas-data/runtime/structures.json').read_text())['structures']
    relations = json.loads((ROOT / 'atlas-data/runtime/relations.json').read_text())['relations']
    rig = json.loads((ROOT / 'atlas-data/runtime/rig.json').read_text())
    contacts = json.loads((D1 / 'contacts.json').read_text())['contacts']
    geometry = json.loads((GEOMETRY / 'geometry.json').read_text())
    d1 = {s['id']: s for s in json.loads((D1 / 'structures.json').read_text())['structures']}
    by_id = {s['id']: s for s in runtime}
    segment_of = {bone: seg for seg, v in rig['segments'].items() for bone in v['bones']}
    parent = {seg: v['parent'] for seg, v in rig['segments'].items()}

    def chain(segments):
        """All segments on the rig paths between the given segments (their union with the tree paths)."""
        segments = set(segments)
        if len(segments) < 2: return segments
        ancestors = lambda s: [s] + (ancestors(parent[s]) if parent[s] else [])
        out = set()
        for a in segments:
            for b in segments:
                pa, pb = ancestors(a), ancestors(b)
                common = next(x for x in pa if x in pb)
                out |= set(pa[:pa.index(common) + 1]) | set(pb[:pb.index(common) + 1])
        return out

    # Bone surfaces per segment.
    trees = {}
    for seg, v in rig['segments'].items():
        pts = [d1_positions(d1[s['id']]) for s in runtime if s['key'] in set(v['bones'])]
        pts = np.concatenate(pts)[::2]
        kd = KDTree(len(pts))
        for i, co in enumerate(pts): kd.insert(Vector(co), i)
        kd.balance(); trees[seg] = kd

    attach = {}
    for r in relations:
        if r['type'] in ('origin', 'insertion') and r.get('bone') and by_id.get(r['bone']):
            seg = segment_of.get(by_id[r['bone']]['key'])
            for owner in r['owners']:
                if seg: attach.setdefault(owner, set()).add(seg)

    def near_segments(s):
        """Segments whose bones lie close to the structure's own surface (catches attachments ZA files under a
        group, e.g. gastrocnemius inserting through the calcaneal tendon)."""
        pts = d1_positions(d1[s['id']])[::4]
        counts = {seg: sum(tree.find(Vector(p))[2] <= NEAR for p in pts) for seg, tree in trees.items()}
        return {seg for seg, n in counts.items() if n >= max(3, NEAR_SHARE * len(pts))}

    def allowed(s):
        segs = attach.get(s['id'], set()) | {segment_of[by_id[b['id']]['key']] for b in contacts.get(s['id'], {}).get('bones', [])
                                             if by_id.get(b['id']) and by_id[b['id']]['key'] in segment_of}
        segs |= near_segments(s)
        return chain(segs) if segs else set(rig['segments'])

    chunks = {c['id']: c for c in geometry['chunks']}
    per_chunk, done, stats = {}, {}, {'resources': 0, 'vertices': 0, 'allPossible': 0}
    soft = [s for s in runtime if s['learner']['visible'] and s['layer'] in SOFT_LAYERS]
    # Mirrored twins share one mesh: its roles are the union over every instance that uses it.
    resource_roles = {}
    for s in soft:
        segs = allowed(s)
        if segs == set(rig['segments']): stats['allPossible'] += 1
        for level in ('overview', 'detail'):
            resource_roles.setdefault(s['geometry']['lods'][level]['resource'], set()).update(role(x) for x in segs)
    positions_cache, placed = {}, set()
    for s in soft:
        side = s['side'][0] if s['side'] in ('left', 'right') else None
        for level in ('overview', 'detail'):
            lod = s['geometry']['lods'][level]
            if lod['resource'] in done:  # mirrored twin, or overview == detail: reuse, but list it in this chunk too
                if (lod['chunk'], lod['resource']) not in placed:
                    per_chunk.setdefault(lod['chunk'], []).append((lod['resource'], *done[lod['resource']]))
                    placed.add((lod['chunk'], lod['resource']))
                continue
            roles = sorted(resource_roles[lod['resource']], key=ROLE_ORDER.index)
            if lod['chunk'] not in positions_cache: positions_cache[lod['chunk']] = chunk_positions(GEOMETRY / 'chunks' / f"{lod['chunk']}.glb")
            pts = world(positions_cache[lod['chunk']][lod['resource']], s['geometry']['matrix'])
            resolve = lambda r: r if r in ('pelvis', 'torso') else f'{r}_{side or "r"}'
            d = np.array([[trees[resolve(r)].find(Vector(p))[2] for r in roles] for p in pts])
            w = np.exp(-(d - d.min(1, keepdims=True)) / SIGMA)
            order = np.argsort(-w, 1)
            a, b = order[:, 0], order[:, 1] if len(roles) > 1 else order[:, 0]
            wa, wb = w[np.arange(len(w)), a], w[np.arange(len(w)), b]
            share = np.where(a == b, 1., wa / (wa + wb))
            packed = (a.astype('<u2') << 12) | (b.astype('<u2') << 8) | np.round(share * 255).astype('<u2')
            per_chunk.setdefault(lod['chunk'], []).append((lod['resource'], roles, packed.astype('<u2')))
            placed.add((lod['chunk'], lod['resource']))
            done[lod['resource']] = (roles, packed.astype('<u2'))
            stats['resources'] += 1; stats['vertices'] += len(pts)

    OUT.mkdir(parents=True, exist_ok=True)
    for chunk, rows in per_chunk.items():
        header, blobs, offset = {'resources': {}}, [], 0
        for key, roles, packed in rows:
            header['resources'][key] = {'offset': offset, 'vertices': len(packed), 'roles': roles}
            blobs.append(packed.tobytes()); offset += len(packed) * 2
        text = json.dumps(header, separators=(',', ':')).encode(); text += b' ' * ((-len(text)) % 4)
        (OUT / f'{chunk}.bin').write_bytes(struct.pack('<I', len(text)) + text + b''.join(blobs))
    (OUT / 'index.json').write_text(json.dumps({'schemaVersion': 1, 'sigmaMetres': SIGMA, 'chunks': sorted(per_chunk), **stats}) + '\n')
    print('SKIN', json.dumps({**stats, 'chunks': len(per_chunk)}), flush=True)


main()
