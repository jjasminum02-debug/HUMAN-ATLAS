"""Read-only independent field replay, finite-difference and band conflict audit."""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np

p = argparse.ArgumentParser()
p.add_argument('--evidence', required=True)
p.add_argument('--revision', required=True)
a = p.parse_args()
R = Path(__file__).resolve().parents[2]
E = R / a.evidence
load = lambda p: json.loads(p.read_text())
candidate = E / f'candidates/fit-{a.revision}.json'
before = hashlib.sha256(candidate.read_bytes()).hexdigest()
d = load(candidate)
s = np.array(d['sourceVertices'])
v = np.array(d['positions'])
patches = load(E / f'surface-bands-{a.revision}.json')['patches']
faces = [f['derivedVertices'] for f in d['faces']]

def operator(source, target, regularization):
    source, target = np.array(source), np.array(target)
    center = source.mean(0)
    x = (source-center)/.1
    r = np.linalg.norm(x[:, None]-x[None, :], axis=2)
    poly = np.column_stack((np.ones(len(x)), x))
    matrix = np.block([[r**3+np.diag(regularization), poly], [poly.T, np.zeros((4, 4))]])
    coef = np.linalg.solve(matrix, np.vstack((target, np.zeros((4, 3)))))
    def evaluate(points):
        points = np.asarray(points)
        values, derivatives = [], []
        for chunk in range(0, len(points), 512):
            q = (points[chunk:chunk+512]-center)/.1
            delta = q[:, None]-x[None, :]
            r = np.linalg.norm(delta, axis=2)
            values.append(np.einsum('qn,no->qo', r**3, coef[:-4]) + np.column_stack((np.ones(len(q)), q)) @ coef[-4:])
            derivatives.append((np.einsum('qnk,no->qok', 3*r[:, :, None]*delta, coef[:-4])+coef[-3:].T)/.1)
        return np.concatenate(values), np.concatenate(derivatives)
    return evaluate

result = []
for patch in patches:
    ids = np.array(patch['sourceVertices'])
    roots = [x['sourceVertex'] for x in patch.get('sharedBoundary', [])] or patch.get('sharedBoundaryVertices', [])
    mask = np.zeros(len(s), bool); mask[ids] = True
    triangle_faces = [(i, f) for i, f in enumerate(faces) if mask[f].all()]
    # Face centroids and source-axis interior samples go beyond the vertex-only guard.
    face_points = np.array([s[f].mean(0) for _, f in triangle_faces])
    rows = patch.get('continuousSurfaceBandPairs', [])
    interior = []
    for row in rows[::max(1, len(rows)//128)]:
        if 'sourceAxisCenterM' in row:
            center, surface = np.array(row['sourceAxisCenterM']), np.array(row['sourceM'])
            interior.extend(center+(surface-center)*fraction for fraction in (.25, .5, .75))
    query = np.vstack([s[ids], face_points, np.array(interior).reshape(-1, 3)])
    initial = operator(patch['sourceFieldCentersM'], patch['nativeFieldTargetsM'], patch['regularization'])
    corrections = [(x['step'], operator(x['fieldCentersM'], x['displacementTargetsM'], x['regularization']))
                   for x in patch.get('contactCorrectionStages', [])]
    def replay(points):
        mapped, jac = initial(points)
        for step, op in corrections:
            delta, derivative = op(mapped)
            mapped += step*delta
            jac = (np.eye(3)[None]+step*derivative) @ jac
        return mapped, jac
    mapped, jac = replay(query)
    determinants = np.linalg.det(jac)
    assert np.isfinite(mapped).all() and np.isfinite(jac).all()
    interior_ids = [j for j, i in enumerate(ids) if int(i) not in roots]
    replay_error = np.linalg.norm(mapped[interior_ids]-v[ids[interior_ids]], axis=1).max()
    assert replay_error < 1e-7, replay_error
    sample = query[::max(1, len(query)//96)]
    analytic = replay(sample)[1]
    fd = np.empty_like(analytic)
    for axis in range(3):
        h = np.zeros(3); h[axis] = 1e-6
        fd[:, :, axis] = (replay(sample+h)[0]-replay(sample-h)[0])/(2e-6)
    fd_error = np.abs(fd-analytic).max()
    assert fd_error < .002, fd_error
    by_vertex = {row['vertex']: row for row in rows}
    conflicts, jumps = [], []
    for fi, f in triangle_faces:
        if not all(i in by_vertex for i in f): continue
        points = np.array([by_vertex[i]['targetM'] for i in f])
        centroid = s[f].mean(0)
        base_j = initial(centroid[None, :])[1][0]
        normal = np.cross(s[f[1]]-s[f[0]], s[f[2]]-s[f[0]])
        transported = np.linalg.solve(base_j.T, normal)
        proposed = np.cross(points[1]-points[0], points[2]-points[0])
        if np.dot(proposed, transported) < 0:
            conflicts.append({'sourceObjFace': d['faces'][fi]['sourceFace'],
                'sourceVertexIds': [d['originalVertexIds'][i] for i in f],
                'nativeTargets': [by_vertex[i] for i in f],
                'finding': 'proposed band target face reverses orientation relative to proper source field; not a verified homology'})
        for x, y in zip(range(len(f)), list(range(1, len(f)))+[0]):
            source_length = np.linalg.norm(s[f[x]]-s[f[y]])
            target_length = np.linalg.norm(points[x]-points[y])
            if target_length > .02 and target_length > source_length*4:
                jumps.append({'sourceVertices': [d['originalVertexIds'][f[x]], d['originalVertexIds'][f[y]]],
                              'sourceLengthM': float(source_length), 'targetLengthM': float(target_length),
                              'nativeTargets': [by_vertex[f[x]], by_vertex[f[y]]]})
    result.append({'patch': patch['patch'], 'vertexQueries': len(ids), 'faceCentroidQueries': len(face_points),
        'interiorQueries': len(interior), 'minimumReplayedJacobian': float(determinants.min()),
        'nonPositiveReplayedJacobianCount': int((determinants <= 0).sum()),
        'nonPositiveFaceCentroidJacobianCount': int((determinants[len(ids):len(ids)+len(face_points)] <= 0).sum()),
        'maximumReplayPositionErrorM': float(replay_error), 'finiteDifferenceJacobianMaxError': float(fd_error),
        'proposedTargetOrientationConflictCount': len(conflicts), 'proposedTargetEdgeJumpCount': len(jumps),
        'allOrientationConflictSourceObjFaces': [x['sourceObjFace'] for x in conflicts],
        'allTargetJumpSourceVertexPairs': [x['sourceVertices'] for x in jumps],
        'orientationConflictSamples': conflicts[:12], 'targetJumpSamples': jumps[:12]})
    print({k: val for k, val in result[-1].items() if not k.endswith('Samples')}, flush=True)
out = {'revision': a.revision, 'patches': result, 'candidateReadOnly': before == hashlib.sha256(candidate.read_bytes()).hexdigest(),
       'allNumericalReplayAndFiniteDifferenceChecksPassed': True, 'sourceNativeHomologyApproved': False,
       'geometryAcceptance': False, 'limitations': 'Finite sampling does not prove global injectivity. Native/self intersections and actual display remain independent gates.'}
assert out['candidateReadOnly']
(E / f'field-inspection-{a.revision}.json').write_text(json.dumps(out, indent=2)+'\n')
