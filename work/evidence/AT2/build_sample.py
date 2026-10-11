"""Bounded native-surface feasibility sample. Reuse AC1 reader; no upstream writes."""
from pathlib import Path
import ast, hashlib, json, struct
import numpy as np

R = Path(__file__).resolve().parents[3]
E = Path(__file__).resolve().parent
A = R / 'work/evidence/acupoint-AC1'
read = lambda p: json.loads(p.read_text())
sha = lambda b: hashlib.sha256(b).hexdigest()
dataset = read(A / 'runtime-dataset.json')
integration = read(A / 'runtime-integration.json')
rows = {v['sourceKey']: v for v in integration['objects']}
cache = R / 'atlas-data/source-cache/datasets/za'
inputs, meshes = {}, {}
# Compile ONLY the previously verified read-only world() function, never its old writer.
original = A / 'build_carrier.py'
tree = ast.parse(original.read_text())
reader = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'world')
exec(compile(ast.Module(body=[reader], type_ignores=[]), str(original), 'exec'), globals())

def key(name):
    found = [k for k, v in rows.items() if v['side'] == 'right' and v['names']['en'] == name]
    assert len(found) == 1, (name, found)
    return found[0]

names = ['Fascia lata', 'Rectus femoris muscle', 'Vastus lateralis muscle',
         'Vastus medialis muscle', 'Sartorius muscle', 'Adductor longus',
         'Long head of biceps femoris', 'Semitendinosus muscle']
source_keys = [key(n) for n in names]
axis_key = key('Femur')
unit_inputs = {}
geometry_audit = []
for k in source_keys + [axis_key]:
    unit = cache / 'units' / f'{k}.json'
    u = read(unit)
    assert u['geometrySpace'] == 'source_local' and not u['transformAppliedToGeometry']
    assert u['sourceKey'] == k and rows[k]['side'] == 'right'
    unit_inputs[str(unit.relative_to(R))] = sha(unit.read_bytes())
    v, t = world(k)
    bounds = np.array([v.min(axis=0), v.max(axis=0)])
    assert np.max(np.abs(bounds - np.array(rows[k]['bounds']))) < .0001, k
    geometry_audit.append({'sourceKey': k, 'name': rows[k]['names']['en'], 'side': 'right',
                           'bounds': bounds.tolist(), 'vertices': len(v), 'triangles': len(t),
                           'matrixAppliedOnce': True, 'unitMetadataSha256': unit_inputs[str(unit.relative_to(R))]})

vs, ids, face_indices = [], [], []
for number, k in enumerate(source_keys):
    v, t = meshes[k]
    vs.append(v[t]); ids.extend([number] * len(t)); face_indices.extend(range(len(t)))
triangles = np.concatenate(vs)
ids = np.array(ids); face_indices = np.array(face_indices)
edge1 = triangles[:, 1] - triangles[:, 0]
edge2 = triangles[:, 2] - triangles[:, 0]

femur_v, femur_t = meshes[axis_key]
ymin, ymax = femur_v[:, 1].min(), femur_v[:, 1].max()
# One mid-shaft strip, not the whole limb/body. Fractions choose sampling domain, not points/cun.
levels = np.linspace(ymin + .35 * (ymax - ymin), ymin + .65 * (ymax - ymin), 16)

def center(y):
    native = femur_v[femur_t]
    p, q = native[:, [0, 1, 2]], native[:, [1, 2, 0]]
    den = q[:, :, 1] - p[:, :, 1]
    valid = (np.abs(den) > 1e-12) & ((p[:, :, 1] <= y) != (q[:, :, 1] <= y))
    amount = np.divide(y - p[:, :, 1], den, out=np.zeros_like(den), where=np.abs(den) > 1e-12)
    hits = (p + amount[:, :, None] * (q-p))[valid]
    assert len(hits) > 3, y
    c = (hits.min(axis=0) + hits.max(axis=0)) / 2
    c[1] = y
    return c

def cast(origin, direction):
    # Exact triangle intersection on the native surface; no nearest-vertex height fallback.
    pvec = np.cross(np.broadcast_to(direction, edge2.shape), edge2)
    det = np.einsum('ij,ij->i', edge1, pvec)
    valid = np.abs(det) > 1e-12
    inv = np.divide(1, det, out=np.zeros_like(det), where=valid)
    tvec = origin - triangles[:, 0]
    u = np.einsum('ij,ij->i', tvec, pvec) * inv
    qvec = np.cross(tvec, edge1)
    v = np.einsum('j,ij->i', direction, qvec) * inv
    distance = np.einsum('ij,ij->i', edge2, qvec) * inv
    valid &= (u >= -1e-9) & (v >= -1e-9) & (u+v <= 1+1e-9) & (distance > 0) & (distance < .20)
    indices = np.flatnonzero(valid)
    if not len(indices):
        return None
    index = indices[np.argmax(distance[indices])]
    return {'point': origin + distance[index]*direction, 'distance': distance[index],
            'sourceKey': source_keys[ids[index]], 'triangle': int(face_indices[index]),
            'barycentric': [float(1-u[index]-v[index]), float(u[index]), float(v[index])],
            'intersectionCount': len(indices)}

angles = 64
reference, directions, hits, missing = [], [], [], []
for j, y in enumerate(levels):
    origin = center(y)
    for a in range(angles):
        theta = a / angles * 2*np.pi
        direction = np.array([-np.sin(theta), 0, np.cos(theta)])
        hit = cast(origin, direction)
        if hit is None:
            missing.append([j, a]); reference.append([np.nan]*3); directions.append(direction); hits.append(None)
        else:
            reference.append(hit.pop('point')); directions.append(direction)
            hits.append({'sample': j*angles+a, 'level': j, 'angle': a, **hit})
assert not missing, f'native input gaps {missing}; do not fill or bridge them'
reference = np.array(reference)
directions = np.array(directions)
indices = []
for j in range(len(levels)-1):
    for a in range(angles):
        n = (a+1) % angles
        lower, following = j*angles+a, j*angles+n
        upper, upper_next = (j+1)*angles+a, (j+1)*angles+n
        indices.extend([lower, upper, following, following, upper, upper_next])
indices = np.array(indices, dtype='<u4')
clearance = .006  # visual authoring offset, never an assertion of skin/subcutaneous thickness
positions = np.array(reference + clearance*directions, dtype='<f4')
reference = np.array(reference, dtype='<f4')
faces = positions[indices.reshape(-1, 3)]
normals = np.cross(faces[:, 1]-faces[:, 0], faces[:, 2]-faces[:, 0])
assert np.all(np.linalg.norm(normals, axis=1) > 1e-8)
centroids = faces.mean(axis=1)
radial = np.array([p-center(p[1]) for p in centroids])
assert np.all(np.einsum('ij,ij->i', normals, radial) > 0), 'inward winding'
clearances = []
for p in centroids:
    origin = center(p[1]);direction = p-origin;radius = np.linalg.norm(direction);direction /= radius
    hit = cast(origin, direction)
    assert hit is not None
    clearances.append(float(radius-hit['distance']))
assert min(clearances) > 0, ('interpolated carrier penetrates native envelope', min(clearances))
edges = np.concatenate([faces[:, 1]-faces[:, 0], faces[:, 2]-faces[:, 1], faces[:, 0]-faces[:, 2]])
assert np.max(np.linalg.norm(edges, axis=1)) < .03

def topology(p):
    return sha(p.astype('<f4').tobytes() + indices.tobytes())

rights = {'source': 'Z-Anatomy pinned CC BY-SA 4.0; BodyParts3D CC BY-SA 2.1 Japan attribution retained; exact ancestry not invented',
          'localObservation': 'supported', 'publicRedistribution': 'held', 'professorReview': 'not_performed'}
carrier = {'id': 'za-right-middle-thigh-teaching-sample', 'revision': 'surface-sample-r1',
           'topologySha256': topology(positions), 'datasetRevision': dataset['revision'],
           'frameId': dataset['frameContract']['targetFrameId'], 'unit': 'm',
           'poseId': dataset['frameContract']['staticReferencePose']['id'], 'side': 'right',
           'kind': 'authored_teaching_surface', 'precision': 'coarse_not_skin',
           'positions': positions.ravel().tolist(), 'indices': indices.tolist(), 'rights': rights}
assert np.all(positions[:, 0] < 0)
artifact = {'schemaVersion': 1, 'usage': 'development_review_only', 'carrier': carrier,
            'referencePositions': reference.ravel().tolist(), 'referenceHash': topology(reference),
            'label': '오른쪽 중간 넙다리', 'clearanceMetres': clearance,
            'applicability': {'verifiedSample': ['right_middle_thigh_360_degree_strip'],
              'candidateOnly': ['torso', 'upper_arm', 'remaining_leg'],
              'notSupportedByThisSample': ['head', 'hand', 'foot', 'sole', 'perineum', 'oral_mucosa', 'left_side', 'deforming_pose']},
            'acceptedAcupoints': 0}
out = R / 'atlas-data/acupoints/carriers/za-thigh-sample.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(artifact, ensure_ascii=False, separators=(',', ':'))+'\n')
probe = read(A / 'source-probe.json')
decision = read(A / 'source-decision.json')
audit = {'chosenPath': 'author segmented education carriers on current native ZA envelope; one feasibility strip only',
         'sourceRevision': 'c7010a903b75a2fd24a13b1c2c4c3546a9223780', 'sourceSha256': probe['sourceSha256'],
         'predecessorProbe': str((A/'source-probe.json').relative_to(R)), 'predecessorProbeSha256': sha((A/'source-probe.json').read_bytes()),
         'reusedReader': str(original.relative_to(R))+'::world', 'reusedReaderFileSha256': sha(original.read_bytes()),
         'sourceInputs': inputs, 'unitMetadataInputs': unit_inputs, 'nativeGeometry': geometry_audit,
         'frame': carrier['frameId'], 'unit': 'm', 'pose': carrier['poseId'],
         'method': {'origin': 'mid-shaft femur section bounds center, not acupoint landmark', 'levels': levels.tolist(),
                    'angles': angles, 'direction': '[-sin(theta),0,cos(theta)]', 'outermostNativeHit': True,
                    'nearestFallbackCount': 0, 'missingRayCount': len(missing), 'clearanceMetres': clearance,
                    'surfaceThicknessClaim': False, 'seam': 'wrapped index, no duplicate seam vertices',
                    'caps': False, 'fullBodySculpt': False, 'noLeftMirror': True},
         'cost': {'vertices': len(positions), 'triangles': len(indices)//3, 'dataBytes': out.stat().st_size,
                  'geometryBufferBytes': positions.nbytes*2 + len(indices)*2, 'textures': 0,
                  'GPUBytesBasis': 'Float32 position+normal and Uint16 index; driver heap/time unmeasured'},
         'quality': {'centroidNativeClearanceMinMetres': min(clearances), 'centroidNativeClearanceMaxMetres': max(clearances),
                     'sampleVerticesOnNativeTriangles': len(hits), 'checkedTriangleCentroids': len(centroids),
                     'largestEdgeMetres': float(np.max(np.linalg.norm(edges, axis=1))),
                     'allNormalsOutward': True, 'anatomicalSkinAccuracy': 'unresolved'},
         'carrierHash': carrier['topologySha256'], 'referenceHash': artifact['referenceHash'],
         'sampledSourceContributions': {k: sum(h['sourceKey']==k for h in hits) for k in source_keys},
         'applicability': artifact['applicability'], 'rights': rights,
         'failure': {'precise': 'No full skin/mucosa carrier in examined current cache; not a claim about all upstream assets',
                     'reusedEmptySkinCollections': decision['existingCandidateChecks']['ZA']['emptySkinCollections'],
                     'bp3d': decision['existingCandidateChecks']['BP3D'],
                     'oneSelectedAlternative': 'source-bound segmented education envelope, tested here on right middle thigh'},
         'acceptedAcupoints': 0, 'sourceDownloads': 0, 'sourceWrites': 0}
(E/'source-sample.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2)+'\n')
(E/'native-ray-hits.json').write_text(json.dumps(hits, ensure_ascii=False, separators=(',', ':'))+'\n')
print(json.dumps({'artifact':str(out.relative_to(R)), 'cost':audit['cost'], 'quality':audit['quality'],
                  'contributions':audit['sampledSourceContributions']}, ensure_ascii=False))
