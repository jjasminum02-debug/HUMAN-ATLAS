"""Whole-body skeleton rig (ROADMAP M1): bone segments, joint centres, axes and ranges.

  blender --background --factory-startup --python atlas-data/pipeline/build_rig.py
(Blender only for numpy; no .blend is opened.) Writes atlas-data/runtime/rig.json.

Hierarchy and most ranges follow OpenSim Rajagopal2016 (MIT; OpenSim_Models/Models/Rajagopal).
Centres and axes are estimated from the Z-Anatomy bone surfaces in the app frame (x = subject left,
y = up, z = anterior, metres), so no cross-model registration is needed. Each axis sign is fixed by a
probe point that a small positive rotation must move in an anatomical direction (e.g. knee flexion
moves the ankle backwards). Estimates are geometric approximations for teaching, not measured joint kinematics.
"""
import hashlib
import json
from pathlib import Path
import re
import struct

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
D1 = ROOT / 'atlas-data/source-cache/datasets/za-full'
OUT = ROOT / 'atlas-data/runtime/rig.json'

# Segment membership by Z-Anatomy bone name; anything skeletal not listed rides with the torso.
SEGMENT_BONES = [
    ('pelvis', r'^(Hip bone|Sacrum|Coccyx)$'),
    ('femur', r'^Femur$'),
    ('tibia', r'^(Tibia|Fibula)$'),
    ('patella', r'^Patella$'),
    ('talus', r'^Talus$'),
    ('calcn', r'^(Calcaneus|Navicular bone|Cuboid bone|(Medial|Intermediate|Lateral) cuneiform bone|\w+ metatarsal bone|Sesamoid bones of foot)$'),
    ('toes', r'phalanx of .* finger of foot$'),
    ('humerus', r'^Humerus$'),
    ('ulna', r'^Ulna$'),
    ('radius', r'^Radius$'),
    ('hand', r'^((Scaphoid|Lunate|Triquetrum|Pisiform|Trapezium|Trapezoid|Capitate|Hamate) bone|\w+ metacarpal bone|.*phalanx of .* finger of hand)$'),
]
PARENT = {'femur': 'pelvis', 'tibia': 'femur', 'patella': 'femur', 'talus': 'tibia', 'calcn': 'talus', 'toes': 'calcn',
          'humerus': 'torso', 'ulna': 'humerus', 'radius': 'ulna', 'hand': 'radius'}
JOINT_OF = {'femur': 'hip', 'tibia': 'knee', 'patella': 'patellofemoral', 'talus': 'ankle', 'calcn': 'subtalar', 'toes': 'mtp',
            'humerus': 'shoulder', 'ulna': 'elbow', 'radius': 'radioulnar', 'hand': 'wrist'}

# (dof, Korean label for +/-, range in degrees, range source)
DOFS = {
    'back': [('flexion', ('굽힘', '폄'), (-30, 60), 'educational'), ('bending', ('왼쪽 옆굽힘', '오른쪽 옆굽힘'), (-30, 30), 'educational'),
             ('rotation', ('왼쪽 돌림', '오른쪽 돌림'), (-40, 40), 'educational')],
    'hip': [('flexion', ('굽힘', '폄'), (-30, 120), 'Rajagopal2016'), ('adduction', ('모음', '벌림'), (-50, 30), 'Rajagopal2016'),
            ('rotation', ('안쪽돌림', '가쪽돌림'), (-40, 40), 'Rajagopal2016')],
    'knee': [('flexion', ('굽힘', '폄'), (0, 120), 'Rajagopal2016')],
    # Patella rides on the femoral groove: rotates about the knee axis by a fixed share of knee flexion (approximation).
    'patellofemoral': [('flexion', ('굽힘', '폄'), (0, 120), 'coupled to knee flexion (fitted ratio)')],
    'ankle': [('dorsiflexion', ('발등굽힘', '발바닥굽힘'), (-40, 30), 'Rajagopal2016')],
    'subtalar': [('inversion', ('안쪽번짐', '가쪽번짐'), (-20, 20), 'Rajagopal2016')],
    'mtp': [('extension', ('폄', '굽힘'), (-30, 30), 'Rajagopal2016')],
    'shoulder': [('flexion', ('굽힘', '폄'), (-60, 170), 'educational'), ('abduction', ('벌림', '모음'), (-30, 170), 'educational'),
                 ('rotation', ('안쪽돌림', '가쪽돌림'), (-90, 90), 'Rajagopal2016')],
    'elbow': [('flexion', ('굽힘', '폄'), (0, 150), 'Rajagopal2016')],
    'radioulnar': [('pronation', ('엎침', '뒤침'), (0, 85), 'educational')],
    'wrist': [('flexion', ('굽힘(손바닥쪽)', '폄(손등쪽)'), (-70, 70), 'Rajagopal2016'), ('deviation', ('자쪽굽힘', '노쪽굽힘'), (-25, 35), 'Rajagopal2016')],
}
JOINT_NAMES = {'back': '허리', 'hip': '엉덩관절', 'knee': '무릎관절', 'patellofemoral': '무릎넙다리관절', 'ankle': '발목관절', 'subtalar': '목말밑관절', 'mtp': '발허리발가락관절',
               'shoulder': '어깨관절', 'elbow': '팔꿉관절', 'radioulnar': '노자관절', 'wrist': '손목관절'}


def positions(s):
    path = D1 / s['lods']['detail']['path']
    data = path.read_bytes(); size = struct.unpack_from('<I', data, 12)[0]
    doc = json.loads(data[20:20 + size]); binary = data[20 + size + 8:]
    a = doc['accessors'][0]; view = doc['bufferViews'][a['bufferView']]
    p = np.frombuffer(binary, dtype='<f4', count=a['count'] * 3, offset=view.get('byteOffset', 0)).reshape(-1, 3).astype('f8')
    m = np.array(s['matrix'], dtype='f8').reshape(4, 4).T
    return p @ m[:3, :3].T + m[:3, 3]


def sphere(points):
    a = np.c_[2 * points, np.ones(len(points))]
    c, *_ = np.linalg.lstsq(a, (points ** 2).sum(1), rcond=None)
    return c[:3], float(np.sqrt(c[3] + (c[:3] ** 2).sum()))


def unit(v):
    v = np.asarray(v, dtype='f8'); return v / np.linalg.norm(v)


def rotate(point, centre, axis, degrees):
    """Rodrigues rotation of a point about the line (centre, axis)."""
    k = unit(axis); v = point - centre; t = np.radians(degrees)
    return centre + v * np.cos(t) + np.cross(k, v) * np.sin(t) + k * np.dot(k, v) * (1 - np.cos(t))


def signed(axis, centre, probe, direction):
    """Flip the axis so that a small positive rotation moves `probe` along `direction`."""
    moved = rotate(probe, centre, axis, 5) - probe
    return unit(axis) * (1 if np.dot(moved, direction) > 0 else -1)


def knee_offset(knees):
    """One sagittal offset (±10 mm) for both fixed knee axes, chosen so femur-tibia contact stays closest to the
    rest contact through flexion. Shared so the rig stays left/right symmetric. A real knee rolls and glides;
    one fixed axis can only approximate it."""
    from mathutils import Vector
    from mathutils.kdtree import KDTree
    prepared = []
    for femur, tibia, centre, axis in knees:
        distal = femur[femur[:, 1] < femur[:, 1].min() + .05]
        kd = KDTree(len(distal))
        for i, co in enumerate(distal): kd.insert(Vector(co), i)
        kd.balance()
        prepared.append((kd, tibia[tibia[:, 1] > tibia[:, 1].max() - .04][::2], centre, axis))
    gap = lambda kd, plateau, c, axis, a: min(kd.find(Vector(rotate(p, c, axis, a)))[2] for p in plateau)
    rests = [gap(kd, pl, c, ax, 0) for kd, pl, c, ax in prepared]
    best = (float('inf'), np.zeros(3))
    for dy in np.arange(-.010, .0101, .001):
        for dz in np.arange(-.010, .0101, .001):
            off = np.array([0, dy, dz])
            score = sum(abs(gap(kd, pl, c + off, ax, a) - rest) for (kd, pl, c, ax), rest in zip(prepared, rests) for a in (20, 60, 100))
            if score < best[0]: best = (score, off)
    gaps = [[round(gap(kd, pl, c + best[1], ax, a) * 1000, 1) for a in (0, 30, 70, 110)] for kd, pl, c, ax in prepared]
    return best[1], gaps


def patella_fit(femur, patella, centre, axis):
    """Patella tracks the femoral groove, an arc about a different centre than the condyles. Fit that
    centre (sagittal offset ±30 mm from the knee axis) and the share of knee flexion it turns, keeping
    patella-femur contact closest to rest at 30/70/110° knee flexion."""
    from mathutils import Vector
    from mathutils.kdtree import KDTree
    kd = KDTree(len(femur))
    for i, co in enumerate(femur): kd.insert(Vector(co), i)
    kd.balance()
    pts = patella[::3]
    gap = lambda c, deg: min(kd.find(Vector(rotate(p, c, axis, deg)))[2] for p in pts)
    rest = gap(centre, 0)
    best = (float('inf'), np.zeros(3), .7)
    for dy in np.arange(-.03, .0301, .003):
        for dz in np.arange(-.03, .0301, .003):
            c = centre + [0, dy, dz]
            for ratio in (.5, .6, .7, .8, .9, 1.0):
                score = sum(abs(gap(c, k * ratio) - rest) for k in (30, 70, 110))
                if score < best[0]: best = (score, np.array([0, dy, dz]), ratio)
    _, offset, ratio = best
    gaps = [round(gap(centre + offset, k * ratio) * 1000, 1) for k in (0, 30, 70, 110)]
    return offset, ratio, gaps


def main():
    d1 = json.loads((D1 / 'structures.json').read_text())['structures']
    runtime = {s['id']: s for s in json.loads((ROOT / 'atlas-data/runtime/structures.json').read_text())['structures']}
    bones = [s for s in d1 if runtime.get(s['id'], {}).get('layer') == 'bone']
    by = {}
    for s in d1: by.setdefault((s['name'], s['side']), s)
    P = lambda name, side='unpaired': positions(by[(name, side)])

    segments = {'pelvis': {'parent': None, 'joint': None, 'side': 'unpaired', 'bones': []},
                'torso': {'parent': 'pelvis', 'joint': 'back', 'side': 'unpaired', 'bones': []}}
    for side in ('left', 'right'):
        for seg in PARENT:
            parent = PARENT[seg] if PARENT[seg] == 'torso' else f'{PARENT[seg]}_{side[0]}'
            if PARENT[seg] == 'pelvis': parent = 'pelvis'
            segments[f'{seg}_{side[0]}'] = {'parent': parent, 'joint': f'{JOINT_OF[seg]}_{side[0]}', 'side': side, 'bones': []}
    for s in bones:
        seg = next((name for name, rule in SEGMENT_BONES if re.search(rule, s['name'])), 'torso')
        target = seg if seg in ('pelvis', 'torso') else f"{seg}_{s['side'][0]}"
        if seg not in ('pelvis', 'torso') and s['side'] == 'unpaired': target = 'torso'
        segments[target]['bones'].append(runtime[s['id']]['key'])

    joints, notes, knee_inputs = {}, {}, []
    lumbosacral = P('Intervertebral disc L5-S1').mean(0)
    head = P('Frontal bone').mean(0)
    joints['back'] = {'centre': lumbosacral, 'axes': {
        'flexion': signed([1, 0, 0], lumbosacral, head, [0, 0, 1]),
        'bending': signed([0, 0, 1], lumbosacral, head, [1, 0, 0]),
        'rotation': signed([0, 1, 0], lumbosacral, head + [0, 0, .1], [1, 0, 0])}}
    notes['back'] = 'centre: Z-Anatomy L5-S1 disc centroid'
    for side in ('left', 'right'):
        s, lat = side[0], (1 if side == 'left' else -1)  # +x is the subject's left
        medial = np.array([-lat, 0, 0], dtype='f8'); lateral = -medial
        F = P('Femur', side); top = F[F[:, 1] > F[:, 1].max() - .055]
        head_pts = top[lat * top[:, 0] < np.percentile(lat * top[:, 0], 35)]
        hip, hip_r = sphere(head_pts)
        # Flexion axis through the centres of curvature of the posterior femoral condyles (sphere fit to each).
        low = F[F[:, 1] < F[:, 1].min() + .045]; split = np.median(lat * low[:, 0])
        condyles = [low[(lat * low[:, 0] < split) == inner] for inner in (True, False)]
        fits = [sphere(c[c[:, 2] < np.percentile(c[:, 2], 45)]) for c in condyles]
        cond = [fits[0][0], fits[1][0]]
        knee = (cond[0] + cond[1]) / 2
        T, Fb = P('Tibia', side), P('Fibula', side)
        med_mal = T[T[:, 1] < T[:, 1].min() + .006].mean(0); lat_mal = Fb[Fb[:, 1] < Fb[:, 1].min() + .006].mean(0)
        ankle = (med_mal + lat_mal) / 2
        talus = P('Talus', side).mean(0)
        heads = [(lambda M: M[M[:, 2] > M[:, 2].max() - .012].mean(0))(P(f'{n} metatarsal bone', side)) for n in ('First', 'Fifth')]
        mtp = (heads[0] + heads[1]) / 2
        toe = P('Distal phalanx of first finger of foot', side).mean(0)
        H = P('Humerus', side); htop = H[H[:, 1] > H[:, 1].max() - .05]
        shoulder, shoulder_r = sphere(htop[lat * htop[:, 0] < np.percentile(lat * htop[:, 0], 50)])
        hb = H[H[:, 1] < H[:, 1].min() + .05]; hl = lat * hb[:, 0]
        epi = [hb[hl <= np.percentile(hl, 3)].mean(0), hb[hl >= np.percentile(hl, 97)].mean(0)]
        artic = H[H[:, 1] < H[:, 1].min() + .02].mean(0)
        R, U = P('Radius', side), P('Ulna', side)
        radial_head = R[R[:, 1] > R[:, 1].max() - .012].mean(0); ulnar_head = U[U[:, 1] < U[:, 1].min() + .012].mean(0)
        styloid = R[lat * R[:, 0] >= np.percentile(lat * R[:, 0], 99)].mean(0)
        wrist = P('Capitate bone', side).mean(0)
        mc3 = (lambda M: M[M[:, 1] < M[:, 1].min() + .01].mean(0))(P('Third metacarpal bone', side))
        joints[f'hip_{s}'] = {'centre': hip, 'axes': {
            'flexion': signed([1, 0, 0], hip, knee, [0, 0, 1]),
            'adduction': signed([0, 0, 1], hip, knee, medial),
            'rotation': signed(knee - hip, hip, knee + [0, 0, .05], medial)}}
        joints[f'knee_{s}'] = {'centre': knee, 'axes': {'flexion': signed(cond[1] - cond[0], knee, ankle, [0, 0, -1])}}
        joints[f'patellofemoral_{s}'] = {'centre': knee, 'axes': {'flexion': joints[f'knee_{s}']['axes']['flexion']}}
        joints[f'ankle_{s}'] = {'centre': ankle, 'axes': {'dorsiflexion': signed(lat_mal - med_mal, ankle, mtp, [0, 1, 0])}}
        joints[f'subtalar_{s}'] = {'centre': talus, 'axes': {'inversion': signed([-lat * .12095, .60475, .78718], talus, heads[0], [0, 1, 0])}}
        joints[f'mtp_{s}'] = {'centre': mtp, 'axes': {'extension': signed(heads[1] - heads[0], mtp, toe, [0, 1, 0])}}
        joints[f'shoulder_{s}'] = {'centre': shoulder, 'axes': {
            'flexion': signed([1, 0, 0], shoulder, artic, [0, 0, 1]),
            'abduction': signed([0, 0, 1], shoulder, artic, lateral),
            'rotation': signed(artic - shoulder, shoulder, artic + [0, 0, .05], medial)}}
        joints[f'elbow_{s}'] = {'centre': (artic + (epi[0] + epi[1]) / 2) / 2, 'axes': {'flexion': signed(epi[1] - epi[0], artic, wrist, [0, 0, 1])}}
        joints[f'radioulnar_{s}'] = {'centre': radial_head, 'axes': {'pronation': signed(ulnar_head - radial_head, radial_head, styloid, [0, 0, 1])}}
        joints[f'wrist_{s}'] = {'centre': wrist, 'axes': {'flexion': signed([1, 0, 0], wrist, mc3, [0, 0, 1]),
                                                          'deviation': signed([0, 0, 1], wrist, mc3, medial)}}
        notes[f'hip_{s}'] = f'centre: sphere fit to femoral head (radius {hip_r * 1000:.1f} mm)'
        notes[f'knee_{s}'] = f'axis: through sphere-fit centres of the posterior femoral condyles (radii {fits[0][1] * 1000:.0f}/{fits[1][1] * 1000:.0f} mm)'
        knee_inputs.append((side, F, P('Tibia', side)))
        notes[f'ankle_{s}'] = 'axis: through the malleolar tips'
        notes[f'subtalar_{s}'] = 'centre: talus centroid; axis direction from Rajagopal2016 subtalar_r'
        notes[f'mtp_{s}'] = 'axis: through the first and fifth metatarsal heads'
        notes[f'shoulder_{s}'] = f'centre: sphere fit to humeral head (radius {shoulder_r * 1000:.1f} mm); scapula and clavicle stay with the torso'
        notes[f'elbow_{s}'] = 'axis: through the humeral epicondyles, centred on the distal articular surface'
        notes[f'radioulnar_{s}'] = 'axis: radial head centre to ulnar head centre'
        notes[f'wrist_{s}'] = 'centre: capitate centroid; axes along the body frame'

    offset, gaps = knee_offset([(F_, T_, np.array(joints[f'knee_{sd[0]}']['centre']), joints[f'knee_{sd[0]}']['axes']['flexion'])
                                for sd, F_, T_ in knee_inputs])
    for (sd, _, _), g in zip(knee_inputs, gaps):
        for jid in (f'knee_{sd[0]}', f'patellofemoral_{sd[0]}'): joints[jid]['centre'] = np.array(joints[jid]['centre']) + offset
        notes[f'knee_{sd[0]}'] += f', shifted {np.round(offset * 1000).astype(int).tolist()} mm to keep femur-tibia contact (gap mm at 0/30/70/110°: {g})'
    pat_offset, pat_ratio, pat_gaps = patella_fit(P('Femur', 'right'), P('Patella', 'right'),
                                                  np.array(joints['knee_r']['centre']), joints['knee_r']['axes']['flexion'])
    for sd in ('l', 'r'):
        joints[f'patellofemoral_{sd}']['centre'] = np.array(joints[f'knee_{sd}']['centre']) + pat_offset
        notes[f'patellofemoral_{sd}'] = (f'patella turns {pat_ratio} x knee flexion about a centre fitted to the femoral groove '
                                         f'({np.round(pat_offset * 1000).astype(int).tolist()} mm from the knee axis; patella-femur gap mm at 0/30/70/110°: {pat_gaps})')
    out_joints = {}
    for jid, j in joints.items():
        kind = jid.split('_')[0]
        out_joints[jid] = {'name': JOINT_NAMES[kind] + ({'_l': ' (왼쪽)', '_r': ' (오른쪽)'}.get(jid[-2:], '')),
                           'centre': [round(float(v), 5) for v in j['centre']], 'estimate': notes[jid],
                           'dofs': [{'id': f'{jid}:{dof}', 'axis': [round(float(v), 5) for v in j['axes'][dof]], 'range': list(rng),
                                     'positive': labels[0], 'negative': labels[1], 'rangeSource': src,
                                     **({'coupledTo': f"knee_{jid[-1]}:flexion", 'ratio': pat_ratio} if kind == 'patellofemoral' else {})}
                                    for dof, labels, rng, src in DOFS[kind]]}
    body = {'segments': segments, 'joints': out_joints}
    revision = hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    OUT.write_text(json.dumps({'schemaVersion': 1, 'revision': revision, 'frame': 'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR, metres',
                               'composition': 'posed(segment) = posed(parent) * T(centre) * R(dof_1) * ... * T(-centre), all in the rest frame',
                               **body}, ensure_ascii=False, indent=1) + '\n')
    print('RIG', json.dumps({k: len(v['bones']) for k, v in segments.items()}), 'hip radius mm', round(hip_r * 1000, 1), flush=True)


main()
