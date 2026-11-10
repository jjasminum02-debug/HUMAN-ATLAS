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

# Segment membership by Z-Anatomy bone name (first rule wins); anything skeletal not listed rides with the torso.
ORD = {2: 'second', 3: 'third', 4: 'fourth', 5: 'fifth'}
SEGMENT_BONES = [
    ('pelvis', r'^(Hip bone|Sacrum|Coccyx)$'),
    # 4-1 step 4: head and cervical vertebrae (hyoid and laryngeal cartilages stay with the torso).
    ('head', r'^((Frontal|Parietal|Occipital|Temporal|Sphenoid|Ethmoid|Lacrimal|Nasal|Palatine|Zygomatic|Inferior nasal concha) bone'
             r'|Maxilla|Mandible|Vomer|Malleus|Incus|Stapes|Nasal septal cartilage|Lateral process of nasal septal cartilage|Major alar cartilage'
             r'|(Upper|Lower) .*(incisor|canine|premolar|molar).*)$'),
    ('c1', r'^Atlas \(C1\)$'), ('c2', r'^Axis \(C2\)$'), *[(f'c{n}', rf'^Vertebra C{n}$') for n in range(3, 8)],
    ('clavicle', r'^Clavicle$'), ('scapula', r'^Scapula$'),
    ('femur', r'^Femur$'),
    ('tibia', r'^(Tibia|Fibula)$'),
    ('patella', r'^Patella$'),
    ('talus', r'^Talus$'),
    ('calcn', r'^(Calcaneus|Navicular bone|Cuboid bone|(Medial|Intermediate|Lateral) cuneiform bone|\w+ metatarsal bone|Sesamoid bones of foot)$'),
    ('hallux_p', r'^Proximal phalanx of first finger of foot$'), ('hallux_d', r'^Distal phalanx of first finger of foot$'),
    *[(f'toe{n}_{p[0].lower()}', rf'^{p} phalanx of {ORD[n]} finger of foot$') for n in range(2, 6) for p in ('Proximal', 'Middle', 'Distal')],
    ('humerus', r'^Humerus$'),
    ('ulna', r'^Ulna$'),
    ('radius', r'^Radius$'),
    ('mc1', r'^First metacarpal bone$'),
    ('thumb_p', r'^Proximal phalanx of first finger of hand$'), ('thumb_d', r'^Distal phalanx of first finger of hand$'),
    *[(f'finger{n}_{p[0].lower()}', rf'^{p} phalanx of {ORD[n]} finger of hand$') for n in range(2, 6) for p in ('Proximal', 'Middle', 'Distal')],
    ('hand', r'^((Scaphoid|Lunate|Triquetrum|Pisiform|Trapezium|Trapezoid|Capitate|Hamate) bone|\w+ metacarpal bone)$'),
]
UNPAIRED = ['pelvis', 'torso', 'c7', 'c6', 'c5', 'c4', 'c3', 'c2', 'c1', 'head']
UNPAIRED_PARENT = {'torso': 'pelvis', 'c7': 'torso', 'c6': 'c7', 'c5': 'c6', 'c4': 'c5', 'c3': 'c4', 'c2': 'c3', 'c1': 'c2', 'head': 'c1'}
UNPAIRED_JOINT = {'torso': 'back', 'c7': 'c7t1', 'c6': 'c6c7', 'c5': 'c5c6', 'c4': 'c4c5', 'c3': 'c3c4', 'c2': 'c2c3', 'c1': 'atlantoaxial', 'head': 'atlantooccipital'}
PARENT = {'femur': 'pelvis', 'tibia': 'femur', 'patella': 'femur', 'talus': 'tibia', 'calcn': 'talus',
          'hallux_p': 'calcn', 'hallux_d': 'hallux_p',
          **{f'toe{n}_{k}': p for n in range(2, 6) for k, p in (('p', 'calcn'), ('m', f'toe{n}_p'), ('d', f'toe{n}_m'))},
          'clavicle': 'torso', 'scapula': 'clavicle', 'humerus': 'scapula', 'ulna': 'humerus', 'radius': 'ulna', 'hand': 'radius',
          'mc1': 'hand', 'thumb_p': 'mc1', 'thumb_d': 'thumb_p',
          **{f'finger{n}_{k}': p for n in range(2, 6) for k, p in (('p', 'hand'), ('m', f'finger{n}_p'), ('d', f'finger{n}_m'))}}
JOINT_OF = {'femur': 'hip', 'tibia': 'knee', 'patella': 'patellofemoral', 'talus': 'ankle', 'calcn': 'subtalar',
            'hallux_p': 'mtp1', 'hallux_d': 'iphallux', **{f'toe{n}_{k}': f'{j}{n}' for n in range(2, 6) for k, j in (('p', 'mtpt'), ('m', 'pipt'), ('d', 'dipt'))},
            'clavicle': 'sternoclavicular', 'scapula': 'acromioclavicular', 'humerus': 'shoulder', 'ulna': 'elbow', 'radius': 'radioulnar', 'hand': 'wrist',
            'mc1': 'cmc1', 'thumb_p': 'mcp1', 'thumb_d': 'ip1', **{f'finger{n}_{k}': f'{j}{n}' for n in range(2, 6) for k, j in (('p', 'mcp'), ('m', 'pip'), ('d', 'dip'))}}
# Controls without a segment of their own: the joints listed in COUPLED follow them by a fixed share.
CONTROLS = {'neck', 'head', 'fingers', 'mtp', 'toes'}
# Share of the whole-neck movement per level, C2-C3 ... C7-T1 (teaching approximation of the usual segmental
# distribution: flexion peaks at C5-C6, rotation is spread through the lower neck; most head rotation is atlanto-axial).
NECK_LEVELS = ['c2c3', 'c3c4', 'c4c5', 'c5c6', 'c6c7', 'c7t1']
NECK_SHARE = {'flexion': [.10, .15, .20, .22, .20, .13], 'bending': [.15, .20, .20, .20, .15, .10], 'rotation': [.12, .18, .20, .20, .18, .12]}

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
    # 4-1 step 4. Ranges are textbook active ranges of motion (educational).
    'neck': [('flexion', ('굽힘', '폄'), (-50, 40), 'educational'), ('bending', ('왼쪽 옆굽힘', '오른쪽 옆굽힘'), (-35, 35), 'educational'),
             ('rotation', ('왼쪽 돌림', '오른쪽 돌림'), (-45, 45), 'educational')],
    'head': [('flexion', ('끄덕임(굽힘)', '젖힘(폄)'), (-20, 20), 'educational'), ('rotation', ('왼쪽 돌림', '오른쪽 돌림'), (-40, 40), 'educational')],
    'sternoclavicular': [('elevation', ('올림', '내림'), (-10, 40), 'educational'), ('protraction', ('내밈', '들임'), (-25, 25), 'educational')],
    'acromioclavicular': [('upwardRotation', ('위쪽돌림', '아래쪽돌림'), (-10, 50), 'educational')],
    'cmc1': [('flexion', ('굽힘', '폄'), (-20, 45), 'educational'), ('abduction', ('벌림(손바닥쪽)', '모음'), (-10, 60), 'educational')],
    'mcp1': [('flexion', ('굽힘', '폄'), (-10, 55), 'educational')],
    'ip1': [('flexion', ('굽힘', '폄'), (-10, 80), 'educational')],
    'fingers': [('mcpFlexion', ('손허리손가락관절 굽힘', '손허리손가락관절 폄'), (-20, 90), 'educational'),
                ('spread', ('벌림', '모음'), (-5, 20), 'educational'),
                ('pipFlexion', ('몸쪽마디 굽힘', '몸쪽마디 폄'), (0, 100), 'educational'), ('dipFlexion', ('먼쪽마디 굽힘', '먼쪽마디 폄'), (0, 80), 'educational')],
    'mtp1': [('extension', ('폄', '굽힘'), (-30, 60), 'educational')],
    'iphallux': [('flexion', ('굽힘', '폄'), (0, 60), 'educational')],
    'toes': [('ipFlexion', ('발가락뼈사이관절 굽힘', '발가락뼈사이관절 폄'), (0, 60), 'educational')],
}
JOINT_NAMES = {'back': '허리', 'hip': '엉덩관절', 'knee': '무릎관절', 'patellofemoral': '무릎넙다리관절', 'ankle': '발목관절', 'subtalar': '목말밑관절', 'mtp': '발허리발가락관절',
               'shoulder': '어깨관절', 'elbow': '팔꿉관절', 'radioulnar': '노자관절', 'wrist': '손목관절',
               'neck': '목', 'head': '머리(위목뼈관절)', 'atlantoaxial': '고리중쇠관절', 'atlantooccipital': '고리뒤통수관절',
               **{j: f'목뼈 C{j[1]}–C{j[3]}' for j in ('c2c3', 'c3c4', 'c4c5', 'c5c6', 'c6c7')}, 'c7t1': '목뼈 C7–T1',
               'sternoclavicular': '복장빗장관절', 'acromioclavicular': '봉우리빗장관절(어깨뼈 돌림)',
               'cmc1': '엄지 손목손허리관절', 'mcp1': '엄지 손허리손가락관절', 'ip1': '엄지 손가락뼈사이관절', 'fingers': '손가락(둘째–다섯째)',
               **{f'{j}{n}': f'{ko} {name}' for n, ko in ((2, '둘째'), (3, '셋째'), (4, '넷째'), (5, '다섯째'))
                  for j, name in (('mcp', '손허리손가락관절'), ('pip', '몸쪽손가락뼈사이관절'), ('dip', '먼쪽손가락뼈사이관절'))},
               'mtp': '발허리발가락관절(둘째–다섯째)', 'mtp1': '엄지발가락 발허리발가락관절', 'iphallux': '엄지발가락 발가락뼈사이관절',
               'toes': '발가락(둘째–다섯째)',
               **{f'{j}{n}': f'{ko}발가락 {name}' for n, ko in ((2, '둘째'), (3, '셋째'), (4, '넷째'), (5, '다섯째'))
                  for j, name in (('mtpt', '발허리발가락관절'), ('pipt', '몸쪽발가락뼈사이관절'), ('dipt', '먼쪽발가락뼈사이관절'))}}


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


def ends(points, toward):
    """(proximal end, distal end, unit long axis) of a long bone: means of the outer 10 % along its main axis,
    proximal being the end nearer `toward`."""
    c = points.mean(0); u = np.linalg.svd(points - c, full_matrices=False)[2][0]
    s = (points - c) @ u
    lo, hi = points[s <= np.percentile(s, 10)].mean(0), points[s >= np.percentile(s, 90)].mean(0)
    if np.linalg.norm(lo - toward) > np.linalg.norm(hi - toward): lo, hi = hi, lo
    return lo, hi, unit(hi - lo)


def across(u, v):
    """Unit vector perpendicular to u lying as close to v as possible (an axis across a bone)."""
    return unit(np.cross(u, np.cross(v, u)))


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

    segments = {seg: {'parent': UNPAIRED_PARENT.get(seg), 'joint': UNPAIRED_JOINT.get(seg), 'side': 'unpaired', 'bones': []} for seg in UNPAIRED}
    for side in ('left', 'right'):
        for seg, p in PARENT.items():
            segments[f'{seg}_{side[0]}'] = {'parent': p if p in UNPAIRED else f'{p}_{side[0]}', 'joint': f'{JOINT_OF[seg]}_{side[0]}', 'side': side, 'bones': []}
    for s in bones:
        seg = next((name for name, rule in SEGMENT_BONES if re.search(rule, s['name'])), 'torso')
        target = seg if seg in UNPAIRED else f"{seg}_{s['side'][0]}"
        if seg not in UNPAIRED and s['side'] == 'unpaired': target = 'torso'
        segments[target]['bones'].append(runtime[s['id']]['key'])
    empty = [k for k, v in segments.items() if not v['bones']]
    if empty: raise SystemExit(f'segments without bones: {empty}')

    joints, notes, knee_inputs = {}, {}, []
    lumbosacral = P('Intervertebral disc L5-S1').mean(0)
    head = P('Frontal bone').mean(0)
    joints['back'] = {'centre': lumbosacral, 'axes': {
        'flexion': signed([1, 0, 0], lumbosacral, head, [0, 0, 1]),
        'bending': signed([0, 0, 1], lumbosacral, head, [1, 0, 0]),
        'rotation': signed([0, 1, 0], lumbosacral, head + [0, 0, .1], [1, 0, 0])}}
    notes['back'] = 'centre: Z-Anatomy L5-S1 disc centroid'
    specs = {}  # joint id -> explicit dof list (coupled joints and controls), else DOFS[kind]
    def coupled(jid, control, shares):
        specs[jid] = [(dof, None, None, f'follows {control}:{dof}', f'{control}:{dof}', r) for dof, r in shares.items()]
    # Neck: whole-neck control spread over C2-C3 ... C7-T1; head nodding at C0-C1 and turning at C1-C2.
    disc = {lvl: P(f"Intervertebral disc C{lvl[1]}-{'T1' if lvl == 'c7t1' else 'C' + lvl[3]}").mean(0) for lvl in NECK_LEVELS}
    C2, C1 = P('Axis (C2)'), P('Atlas (C1)')
    dens = C2[C2[:, 1] > C2[:, 1].max() - .010].mean(0); atlas_top = C1[C1[:, 1] > C1[:, 1].max() - .008].mean(0)
    face = head + [0, 0, .1]
    for i, lvl in enumerate(NECK_LEVELS):
        c = disc[lvl]; above = dens if i == 0 else disc[NECK_LEVELS[i - 1]]
        joints[lvl] = {'centre': c, 'axes': {'flexion': signed([1, 0, 0], c, head, [0, 0, 1]), 'bending': signed([0, 0, 1], c, head, [1, 0, 0]),
                                             'rotation': signed(above - c, c, face, [1, 0, 0])}}
        coupled(lvl, 'neck', {dof: NECK_SHARE[dof][i] for dof in NECK_SHARE})
        notes[lvl] = f"centre: Z-Anatomy disc centroid; share of the neck control: {', '.join(f'{d} {NECK_SHARE[d][i]:.0%}' for d in NECK_SHARE)}"
    joints['atlantoaxial'] = {'centre': dens, 'axes': {'rotation': signed(dens - disc['c2c3'], dens, face, [1, 0, 0])}}
    coupled('atlantoaxial', 'head', {'rotation': 1})
    notes['atlantoaxial'] = 'centre: tip of the dens; axis along the dens'
    joints['atlantooccipital'] = {'centre': atlas_top, 'axes': {'flexion': signed([1, 0, 0], atlas_top, head, [0, 0, 1])}}
    coupled('atlantooccipital', 'head', {'flexion': 1})
    notes['atlantooccipital'] = 'centre: superior articular surfaces of the atlas'
    joints['neck'] = {'centre': disc['c4c5'], 'axes': joints['c4c5']['axes']}
    joints['head'] = {'centre': atlas_top, 'axes': {'flexion': joints['atlantooccipital']['axes']['flexion'], 'rotation': joints['atlantoaxial']['axes']['rotation']}}
    notes['neck'] = 'control: drives C2-C3 ... C7-T1 by their shares'; notes['head'] = 'control: drives the atlanto-occipital (nodding) and atlanto-axial (turning) joints'
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
        joints[f'mtp_{s}'] = {'centre': mtp, 'axes': {'extension': signed(heads[1] - heads[0], mtp, toe, [0, 1, 0])}}  # control for toes 2-5
        joints[f'shoulder_{s}'] = {'centre': shoulder, 'axes': {
            'flexion': signed([1, 0, 0], shoulder, artic, [0, 0, 1]),
            'abduction': signed([0, 0, 1], shoulder, artic, lateral),
            'rotation': signed(artic - shoulder, shoulder, artic + [0, 0, .05], medial)}}
        joints[f'elbow_{s}'] = {'centre': (artic + (epi[0] + epi[1]) / 2) / 2, 'axes': {'flexion': signed(epi[1] - epi[0], artic, wrist, [0, 0, 1])}}
        joints[f'radioulnar_{s}'] = {'centre': radial_head, 'axes': {'pronation': signed(ulnar_head - radial_head, radial_head, styloid, [0, 0, 1])}}
        joints[f'wrist_{s}'] = {'centre': wrist, 'axes': {'flexion': signed([1, 0, 0], wrist, mc3, [0, 0, 1]),
                                                          'deviation': signed([0, 0, 1], wrist, mc3, medial)}}
        # Shoulder girdle: clavicle turns at the sternoclavicular joint (scapula rides along), scapula turns at the acromioclavicular joint.
        Cl, Sc = P('Clavicle', side), P('Scapula', side)
        cl_med = Cl[lat * Cl[:, 0] <= np.percentile(lat * Cl[:, 0], 5)].mean(0); cl_lat = Cl[lat * Cl[:, 0] >= np.percentile(lat * Cl[:, 0], 95)].mean(0)
        plane = np.linalg.svd(Sc - Sc.mean(0), full_matrices=False)[2][2]; inferior_angle = Sc[np.argmin(Sc[:, 1])]
        joints[f'sternoclavicular_{s}'] = {'centre': cl_med, 'axes': {'elevation': signed([0, 0, 1], cl_med, cl_lat, [0, 1, 0]),
                                                                       'protraction': signed([0, 1, 0], cl_med, cl_lat, [0, 0, 1])}}
        joints[f'acromioclavicular_{s}'] = {'centre': cl_lat, 'axes': {'upwardRotation': signed(plane, cl_lat, inferior_angle, lateral)}}
        notes[f'sternoclavicular_{s}'] = 'centre: medial end of the clavicle; the scapula follows the clavicle'
        notes[f'acromioclavicular_{s}'] = 'centre: lateral end of the clavicle; axis normal to the scapular plane (scapulothoracic upward rotation, simplified)'
        # Fingers 2-5 (one control for all four, per-joint axes) and the thumb. Palm faces anterior (+z) at rest.
        palm = np.array([0, 0, 1.])
        mc1b, mc1h, mc1u = ends(P('First metacarpal bone', side), wrist)
        tpp, tpd, tpu = ends(P('Proximal phalanx of first finger of hand', side), mc1h)
        tdp, tdd, tdu = ends(P('Distal phalanx of first finger of hand', side), tpd)
        joints[f'cmc1_{s}'] = {'centre': mc1b, 'axes': {'flexion': signed(palm, mc1b, tdd, medial), 'abduction': signed(across(mc1u, lateral), mc1b, tdd, palm)}}
        joints[f'mcp1_{s}'] = {'centre': (mc1h + tpp) / 2, 'axes': {'flexion': signed(across(tpu, palm), (mc1h + tpp) / 2, tdd, medial)}}
        joints[f'ip1_{s}'] = {'centre': (tpd + tdp) / 2, 'axes': {'flexion': signed(across(tdu, palm), (tpd + tdp) / 2, tdd, medial)}}
        for j in ('cmc1', 'mcp1', 'ip1'): notes[f'{j}_{s}'] = 'centre: between the facing bone ends; flexion moves the thumb tip across the palm'
        for n in range(2, 6):
            _, mch, _ = ends(P(f'{ORD[n].capitalize()} metacarpal bone', side), wrist)
            pp, pd, pu = ends(P(f'Proximal phalanx of {ORD[n]} finger of hand', side), mch)
            mp, md, mu = ends(P(f'Middle phalanx of {ORD[n]} finger of hand', side), pd)
            dp, dd, du = ends(P(f'Distal phalanx of {ORD[n]} finger of hand', side), md)
            away = None if n == 3 else lateral if n == 2 else medial
            for jid, c, u in ((f'mcp{n}_{s}', (mch + pp) / 2, pu), (f'pip{n}_{s}', (pd + mp) / 2, mu), (f'dip{n}_{s}', (md + dp) / 2, du)):
                joints[jid] = {'centre': c, 'axes': {'flexion': signed(across(u, lateral), c, dd, palm)}}
                notes[jid] = 'centre: between the facing bone ends; flexion moves the fingertip toward the palm'
            if away is not None: joints[f'mcp{n}_{s}']['axes']['spread'] = signed(palm, (mch + pp) / 2, dd, away)
            specs[f'mcp{n}_{s}'] = [('flexion', None, None, f'follows fingers_{s}:mcpFlexion', f'fingers_{s}:mcpFlexion', 1)] + \
                ([('spread', None, None, f'follows fingers_{s}:spread', f'fingers_{s}:spread', 1)] if away is not None else [])
            specs[f'pip{n}_{s}'] = [('flexion', None, None, f'follows fingers_{s}:pipFlexion', f'fingers_{s}:pipFlexion', 1)]
            specs[f'dip{n}_{s}'] = [('flexion', None, None, f'follows fingers_{s}:dipFlexion', f'fingers_{s}:dipFlexion', 1)]
        joints[f'fingers_{s}'] = {'centre': joints[f'mcp3_{s}']['centre'], 'axes': {'mcpFlexion': joints[f'mcp3_{s}']['axes']['flexion'],
            'spread': joints[f'mcp2_{s}']['axes']['spread'], 'pipFlexion': joints[f'pip3_{s}']['axes']['flexion'], 'dipFlexion': joints[f'dip3_{s}']['axes']['flexion']}}
        notes[f'fingers_{s}'] = 'control: drives the MCP, PIP and DIP joints of fingers 2-5 (spread: away from the middle finger)'
        # Toes: the big toe on its own, toes 2-5 together.
        up = np.array([0, 1., 0])
        _, m1h, _ = ends(P('First metatarsal bone', side), talus)
        hp, hd, hu = ends(P('Proximal phalanx of first finger of foot', side), m1h)
        dp_, dd_, du_ = ends(P('Distal phalanx of first finger of foot', side), hd)
        joints[f'mtp1_{s}'] = {'centre': (m1h + hp) / 2, 'axes': {'extension': signed(across(hu, lateral), (m1h + hp) / 2, dd_, up)}}
        joints[f'iphallux_{s}'] = {'centre': (hd + dp_) / 2, 'axes': {'flexion': signed(across(du_, lateral), (hd + dp_) / 2, dd_, -up)}}
        notes[f'mtp1_{s}'] = notes[f'iphallux_{s}'] = 'centre: between the facing bone ends'
        for n in range(2, 6):
            _, mth, _ = ends(P(f'{ORD[n].capitalize()} metatarsal bone', side), talus)
            pp, pd, pu = ends(P(f'Proximal phalanx of {ORD[n]} finger of foot', side), mth)
            mp, md, mu = ends(P(f'Middle phalanx of {ORD[n]} finger of foot', side), pd)
            dp, dd, du = ends(P(f'Distal phalanx of {ORD[n]} finger of foot', side), md)
            joints[f'mtpt{n}_{s}'] = {'centre': (mth + pp) / 2, 'axes': {'extension': signed(across(pu, lateral), (mth + pp) / 2, dd, up)}}
            joints[f'pipt{n}_{s}'] = {'centre': (pd + mp) / 2, 'axes': {'flexion': signed(across(mu, lateral), (pd + mp) / 2, dd, -up)}}
            joints[f'dipt{n}_{s}'] = {'centre': (md + dp) / 2, 'axes': {'flexion': signed(across(du, lateral), (md + dp) / 2, dd, -up)}}
            specs[f'mtpt{n}_{s}'] = [('extension', None, None, f'follows mtp_{s}:extension', f'mtp_{s}:extension', 1)]
            specs[f'pipt{n}_{s}'] = [('flexion', None, None, f'follows toes_{s}:ipFlexion', f'toes_{s}:ipFlexion', 1)]
            specs[f'dipt{n}_{s}'] = [('flexion', None, None, f'follows toes_{s}:ipFlexion', f'toes_{s}:ipFlexion', .6)]
            for j in ('mtpt', 'pipt', 'dipt'): notes[f'{j}{n}_{s}'] = 'centre: between the facing bone ends'
        joints[f'toes_{s}'] = {'centre': joints[f'pipt3_{s}']['centre'], 'axes': {'ipFlexion': joints[f'pipt3_{s}']['axes']['flexion']}}
        notes[f'toes_{s}'] = 'control: drives the interphalangeal joints of toes 2-5 (distal 0.6 x proximal)'
        notes[f'hip_{s}'] = f'centre: sphere fit to femoral head (radius {hip_r * 1000:.1f} mm)'
        notes[f'knee_{s}'] = f'axis: through sphere-fit centres of the posterior femoral condyles (radii {fits[0][1] * 1000:.0f}/{fits[1][1] * 1000:.0f} mm)'
        knee_inputs.append((side, F, P('Tibia', side)))
        notes[f'ankle_{s}'] = 'axis: through the malleolar tips'
        notes[f'subtalar_{s}'] = 'centre: talus centroid; axis direction from Rajagopal2016 subtalar_r'
        notes[f'mtp_{s}'] = 'control: drives the MTP joints of toes 2-5 (each about its own axis)'
        notes[f'shoulder_{s}'] = f'centre: sphere fit to humeral head (radius {shoulder_r * 1000:.1f} mm); the humerus hangs from the scapula'
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
    control_dof = lambda ref: next(d for d in DOFS[ref.split(':')[0].split('_')[0]] if d[0] == ref.split(':')[1])
    for jid, j in joints.items():
        kind = jid.split('_')[0]
        rows = []
        for dof, labels, rng, src, *link in (specs[jid] if jid in specs else [(*d, None, None) for d in DOFS[kind]]):
            if link[0]: _, labels, rng, _ = control_dof(link[0])
            if kind == 'patellofemoral': link = [f"knee_{jid[-1]}:flexion", pat_ratio]
            rows.append({'id': f'{jid}:{dof}', 'axis': [round(float(v), 5) for v in j['axes'][dof]], 'range': list(rng),
                         'positive': labels[0], 'negative': labels[1], 'rangeSource': src,
                         **({'coupledTo': link[0], 'ratio': link[1]} if link[0] else {})})
        out_joints[jid] = {'name': JOINT_NAMES[kind] + ({'_l': ' (왼쪽)', '_r': ' (오른쪽)'}.get(jid[-2:], '')),
                           'centre': [round(float(v), 5) for v in j['centre']], 'estimate': notes[jid],
                           **({'control': True} if kind in CONTROLS else {}), 'dofs': rows}
    body = {'segments': segments, 'joints': out_joints}
    revision = hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    OUT.write_text(json.dumps({'schemaVersion': 1, 'revision': revision, 'frame': 'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR, metres',
                               'composition': 'posed(segment) = posed(parent) * T(centre) * R(dof_1) * ... * T(-centre), all in the rest frame',
                               **body}, ensure_ascii=False, indent=1) + '\n')
    print('RIG', json.dumps({k: len(v['bones']) for k, v in segments.items()}), 'hip radius mm', round(hip_r * 1000, 1), flush=True)


main()
