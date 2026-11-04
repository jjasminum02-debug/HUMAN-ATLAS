"""Validate the extract_za.py output: files, geometry, counts, frame, side and attachment sanity.

  python3 atlas-data/pipeline/validate_za_full.py
Exit code 1 on any failure. Checks are independent of Blender.
"""
import hashlib
import json
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'atlas-data/source-cache/datasets/za-full'
LEGACY_UNITS = ROOT / 'atlas-data/source-cache/datasets/za/units'

# Lower bounds for the systems D1 must deliver (ROADMAP D1: "hundreds" of ligaments etc.).
MINIMUM = {'joint/ligament': 250, 'joint/capsule': 25, 'joint/disc': 40, 'muscular/fascia': 50, 'muscular/bursa': 50,
           'muscular/sheath': 20, 'muscular/retinaculum': 10, 'muscular/muscle': 450, 'skeletal/bone': 200,
           'attachment/origin': 300, 'attachment/insertion': 300, 'nervous/nerve': 200}
SIDE_TOLERANCE = 0.015  # metres; mirrored left/right centres
ATTACH_TOLERANCE = 0.01  # metres; attachment patch must sit on its bone's bounds


def glb_counts(data):
    magic, version, length = struct.unpack_from('<III', data)
    assert magic == 0x46546c67 and version == 2 and length == len(data), 'bad GLB header'
    size, kind = struct.unpack_from('<I4s', data, 12); assert kind == b'JSON'
    doc = json.loads(data[20:20 + size])
    acc = doc['accessors']
    return acc[0]['count'], acc[2]['count'] // 3


def centre(s):
    return [(a + b) / 2 for a, b in zip(s['bounds']['min'], s['bounds']['max'])]


def main():
    doc = json.loads((OUT / 'structures.json').read_text())
    structures = doc['structures']
    failures, notes = [], []
    ids = [s['id'] for s in structures]
    if len(ids) != len(set(ids)):
        failures.append('duplicate ids')

    checked = set()
    for s in structures:
        for level, lod in s['lods'].items():
            if lod['path'] in checked:
                continue
            checked.add(lod['path'])
            data = (OUT / lod['path']).read_bytes()
            if hashlib.sha256(data).hexdigest() != lod['sha256']:
                failures.append(f"{s['id']} {level}: sha mismatch"); continue
            vertices, triangles = glb_counts(data)
            if (vertices, triangles) != (lod['vertices'], lod['triangles']):
                failures.append(f"{s['id']} {level}: GLB counts differ from record")

    counts = doc['run']['counts']
    for key, minimum in MINIMUM.items():
        if counts.get(key, 0) < minimum:
            failures.append(f'{key}: {counts.get(key, 0)} < {minimum}')

    # Frame: whole body ~1.5-2 m tall along +y, head up; left side at +x (HUMAN_ATLAS ... XLEFT).
    lo = [min(s['bounds']['min'][i] for s in structures) for i in range(3)]
    hi = [max(s['bounds']['max'][i] for s in structures) for i in range(3)]
    height = hi[1] - lo[1]
    if not 1.5 <= height <= 2.0:
        failures.append(f'body height {height:.3f} m out of range')
    skull = [s for s in structures if s['kind'] == 'bone' and 'skull' in s['name'].lower() or s['name'] == 'Frontal bone']
    feet = [s for s in structures if s['name'] == 'Calcaneus']
    if skull and feet and centre(skull[0])[1] <= centre(feet[0])[1]:
        failures.append('head is not above feet on +y')
    lefts = [centre(s)[0] for s in structures if s['side'] == 'left']
    if sum(x > 0 for x in lefts) < 0.95 * len(lefts):
        failures.append('left structures are not on +x')

    by_name_side = {(s['name'], s['side'], s['kind'], s.get('patch')): s for s in structures}
    asym = []
    for (name, side, kind, patch), s in by_name_side.items():
        if side != 'left':
            continue
        r = by_name_side.get((name, 'right', kind, patch))
        if not r:
            continue
        a, b = centre(s), centre(r)
        if abs(a[0] + b[0]) > SIDE_TOLERANCE or abs(a[1] - b[1]) > SIDE_TOLERANCE or abs(a[2] - b[2]) > SIDE_TOLERANCE:
            asym.append(s['id'])
    notes.append(f'left/right pairs off-mirror by >{SIDE_TOLERANCE * 100:.1f} cm: {len(asym)} {asym[:8]}')

    by_id = {s['id']: s for s in structures}
    attachments = [s for s in structures if s['system'] == 'attachment']
    dangling = [s['id'] for s in attachments for o in s['ownerIds'] if o not in by_id]
    if dangling:
        failures.append(f'attachment owners missing: {dangling[:8]}')
    ownerless = [s['id'] for s in attachments if not s['ownerIds']]
    # ~3% are source gaps: group concepts (quadriceps, triceps surae, erector spinae) and tendons with no mesh.
    if len(ownerless) > 0.05 * len(attachments):
        failures.append(f'attachments without owner: {len(ownerless)}')
    notes.append(f'attachments without owner: {len(ownerless)} {ownerless[:8]}')
    detached = []
    for s in structures:
        if s['system'] != 'attachment' or not s.get('boneId'):
            continue
        bone = by_id[s['boneId']]['bounds']
        inside = all(s['bounds']['max'][i] >= bone['min'][i] - ATTACH_TOLERANCE and s['bounds']['min'][i] <= bone['max'][i] + ATTACH_TOLERANCE
                     for i in range(3))
        if not inside:
            detached.append(s['id'])
    if len(detached) > 0.02 * counts.get('attachment/origin', 1):
        failures.append(f'attachment patches away from their bone: {len(detached)}')
    notes.append(f'attachment patches away from their bone: {len(detached)} {detached[:8]}')

    # Regression against the earlier verified 3.5 extraction: same objects must keep the same transform.
    legacy = {}
    for path in LEGACY_UNITS.glob('*.json'):
        unit = json.loads(path.read_text()); legacy[unit['sourceName']] = unit['matrix']
    compared = moved = 0
    for s in structures:
        old = legacy.get(s['sourceName'])
        if old is None:
            continue
        compared += 1
        if max(abs(a - b) for a, b in zip(old, s['matrix'])) > 1e-5:
            moved += 1
    if compared and moved:
        failures.append(f'{moved}/{compared} objects differ in transform from the earlier extraction')
    notes.append(f'transform regression vs earlier extraction: {compared} compared, {moved} differ')

    exceptions = json.loads((OUT / 'exceptions.json').read_text())['exceptions']
    reasons = {}
    for e in exceptions:
        reasons[e['reason']] = reasons.get(e['reason'], 0) + 1
    report = {'structures': len(structures), 'files': len(checked), 'counts': counts, 'bodyBounds': {'min': lo, 'max': hi},
              'exceptions': reasons, 'notes': notes, 'failures': failures}
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
