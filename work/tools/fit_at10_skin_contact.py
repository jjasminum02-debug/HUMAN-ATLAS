"""Collision-aware source-unit fit. Writes a new candidate, never native or QA input.

Native surface samples constrain barycentric skin facets from the outside. The
source unit and helper controls are explicit immutable addresses. Gaussian fields
have exact zero displacement at shared boundary/helper anchors. Native/self BVH
and exact triangle tests participate in line search; positive sampled 3D Jacobian
is an independent requirement, not whole-skin/landmark approval.
"""
from pathlib import Path
import argparse
import collections
import hashlib
import importlib.util
import json
import sys
import os
import numpy as np
from mathutils import Vector
from mathutils.geometry import closest_point_on_tri
from mathutils.bvhtree import BVHTree

R = Path(__file__).resolve().parents[2]
p = argparse.ArgumentParser()
p.add_argument('--evidence', required=True)
p.add_argument('--revision', required=True)
p.add_argument('--side', choices=['left', 'right','bilateral'], default='right')
p.add_argument('--unit', choices=['hand','foot','head'], default='hand')
p.add_argument('--field-manifest',help='Explicit source/native cage record, default is preserved r31 extremities.')
p.add_argument('--initial-candidate',help='Candidate providing this unit initial positions, default is r31.')
p.add_argument('--base-candidate', help='Previously preserved candidate, outside this source unit remains exact.')
p.add_argument('--minimum-margin', type=float, default=.001,
    help='Numerical source/native sample clearance in metres; not anatomical skin thickness.')
p.add_argument('--target-clearance', type=float, default=.0015,
    help='Numerical solve target, choose explicitly for thin local surface pairs.')
p.add_argument('--floor-m', type=float,
    help='Optional fixed pose reference floor; solved jointly, not a post-fit clamp.')
p.add_argument('--distal-width',type=float,default=.011,
    help='Gaussian length scale in local distal units, recorded per field center.')
p.add_argument('--self-margin',type=float,default=.0002,
    help='Numerical non-intersection margin for non-adjacent skin facets, metres.')
p.add_argument('--helper-mode',choices=['fixed','bounded-soft'],default='fixed',
    help='Source rig handles guide static pose; native bones are always immutable.')
p.add_argument('--maximum-helper-drift',type=float,default=.005)
p.add_argument('--hard-helper-ids',nargs='*',default=[])
p.add_argument('--steps', type=int, default=30)
p.add_argument('--centers', type=int, default=360)
p.add_argument('--resume')
p.add_argument('--reference-exceptions',help='Explicit user-authorized source/facet exceptions; raw full-reference QA remains mandatory.')
p.add_argument('--jacobian-barriers',action='store_true',help='Add first-order positive-volume inequalities to the same constrained solve; exact trial Jacobian guard still applies.')
p.add_argument('--hard-contacts',action='store_true',help='Use addressed native clearance inequalities in the QP, not only its soft objective.')
p.add_argument('--collision-priority',action='store_true',help='Prioritize strict reduction of actual native crossings over clearance energy; do not permit more crossing facets.')
p.add_argument('--shape-target',help='Explicit source-topology shape prior; does not replace correspondence, collision or volume checks.')
p.add_argument('--shape-weight',type=float,default=3.)
args = p.parse_args(sys.argv[sys.argv.index('--')+1:])
assert 0 < args.minimum_margin <= args.target_clearance
E = R / args.evidence
(E / 'candidates').mkdir(parents=True, exist_ok=True)
output = E / f'candidates/fit-{args.revision}.json'
assert not output.exists(), 'Preserve previous candidates: choose a fresh revision.'
load = lambda path: json.loads(path.read_text())
B1 = R / 'work/evidence/AT10/2026-10-13-skin-fit-r1'
B2 = R / 'work/evidence/AT10/2026-10-13-skin-fit-r2'
B4 = R / 'work/evidence/AT10/2026-10-14-skin-fit-r4'
d = load(B2 / 'candidates/fit-r22.json')
if args.base_candidate:
    d = load(R/args.base_candidate)
source = np.array(d['sourceVertices'])
v = np.array(d['positions'])
tri = np.array([[f['derivedVertices'][0], f['derivedVertices'][j], f['derivedVertices'][j+1]]
                for f in d['faces'] for j in range(1, len(f['derivedVertices'])-1)])
if not args.field_manifest and args.unit!='hand':
    raise ValueError('An explicit corrected source/native manifest is required. Archived three-handle foot data is not an active default.')
field_path=R/args.field_manifest if args.field_manifest else E/'initial-hand-fields-r31.json'
record = next(x for x in load(field_path)['patches'] if x['patch'] == args.unit+'-'+args.side)
ids = np.array(record['sourceVertices'])
roots = np.array([r['sourceVertex'] for r in record['sharedBoundary']])
mask = np.zeros(len(v), bool); mask[ids] = True
unit_tri_ids = np.flatnonzero(mask[tri].any(1))
unit_tri = tri[unit_tri_ids]
if args.initial_candidate:
    initial_path=R/args.initial_candidate
    v[ids] = np.array(load(initial_path)['positions'])[ids]
elif 'initialUnitPositionsM' in record:
    initial_path=str(field_path)+'#'+record['patch']+'/initialUnitPositionsM'
    v[ids]=np.array(record['initialUnitPositionsM'])
else:
    raise ValueError('Explicit initial candidate or frozen initial unit positions required.')
v[roots] = np.array(d['positions'])[roots]
initial = v.copy()
shape_target=np.array(load(R/args.shape_target)['positions']) if args.shape_target else initial
assert shape_target.shape==v.shape and np.isfinite(shape_target).all()
native = load(B1 / 'native-surfaces-r1.json')
supplement=os.environ.get('AT10_NATIVE_SUPPLEMENT')
if supplement:
    extra=load(R/supplement);assert not set(extra)&set(native);native.update(extra)
native_vertices, native_triangles, native_keys, native_local = [], [], [], []
sample_points, sample_addresses = [], []
exceptions={}
if args.reference_exceptions:
    policy=load(R/args.reference_exceptions)
    assert policy['schemaVersion']==1 and policy['userAuthorized'] is True and policy['rawFullReferenceQaRequired'] is True
    for item in policy['facets']:
        n=native[item['sourceKey']]
        digest=hashlib.sha256(np.asarray(n['v'],dtype='<f8').tobytes()+np.asarray(n['t'],dtype='<u4').tobytes()).hexdigest()
        assert digest==item['geometrySha256'] and n['name']==item['sourceName'] and n['side']==item['side']
        exceptions[item['sourceKey']]=set(item['triangleIds'])
lower, upper = v[ids].min(0)-.035, v[ids].max(0)+.035
for key, item in native.items():
    nv = np.array(item['v']); nt = np.array(item['t']); off = len(native_vertices)
    kept=np.array([i for i in range(len(nt)) if i not in exceptions.get(key,set())],dtype=int)
    native_vertices.extend(nv.tolist()); native_triangles.extend((nt[kept]+off).tolist())
    native_keys.extend([key]*len(kept)); native_local.extend(kept.tolist())
    if args.side!='bilateral' and item['side'] not in [args.side, None, 'midline', 'bilateral', 'unspecified']:
        continue
    vertex_ids = np.intersect1d(np.unique(nt[kept]),np.flatnonzero(((nv >= lower) & (nv <= upper)).all(1)))
    sample_points.extend(nv[vertex_ids].tolist())
    sample_addresses.extend({'nativeSourceKey': key, 'nativeVertex': int(i)} for i in vertex_ids)
    centroids = nv[nt].mean(1)
    face_ids = np.intersect1d(kept,np.flatnonzero(((centroids >= lower) & (centroids <= upper)).all(1)))
    sample_points.extend(centroids[face_ids].tolist())
    sample_addresses.extend({'nativeSourceKey': key, 'nativeTriangle': int(i), 'barycentric': [1/3]*3} for i in face_ids)
nv, nt = np.array(native_vertices), np.array(native_triangles)
samples = np.array(sample_points)
print('NATIVE', len(nt), 'samples', len(samples), 'source unit', len(ids), flush=True)
native_bvh = BVHTree.FromPolygons(native_vertices, native_triangles, all_triangles=True)
spec = importlib.util.spec_from_file_location('native_intersections', R / 'atlas-web/scripts/nativeSurfaceIntersections.py')
common = importlib.util.module_from_spec(spec); spec.loader.exec_module(common)

def exact_pairs(a, b):
    hits = np.zeros(len(a), bool)
    for x, y in [(0, 1), (1, 2), (2, 0)]:
        hits |= common.SurfaceIndex.crosses(a[:, x], a[:, y]-a[:, x], b)
        hits |= common.SurfaceIndex.crosses(b[:, x], b[:, y]-b[:, x], a)
    return hits

def collision_state(vertices):
    tree = BVHTree.FromPolygons(vertices.tolist(), tri.tolist(), all_triangles=True)
    local = BVHTree.FromPolygons(vertices.tolist(), unit_tri.tolist(), all_triangles=True)
    possible = np.array(local.overlap(native_bvh), dtype=int).reshape(-1, 2)
    if len(possible):
        hits = exact_pairs(vertices[unit_tri[possible[:, 0]]], nv[nt[possible[:, 1]]])
        pairs = np.column_stack([unit_tri_ids[possible[hits, 0]], possible[hits, 1]])
    else:
        pairs = np.empty((0, 2), int)
    possible_self = np.array(local.overlap(tree), dtype=int).reshape(-1, 2)
    self_pairs = np.column_stack([unit_tri_ids[possible_self[:, 0]], possible_self[:, 1]])
    self_pairs = np.unique(np.sort(self_pairs, 1), axis=0)
    self_pairs = self_pairs[self_pairs[:, 0] != self_pairs[:, 1]]
    if len(self_pairs):
        adjacent = (tri[self_pairs[:, 0], :, None] == tri[self_pairs[:, 1], None, :]).any((1, 2))
        self_pairs = self_pairs[~adjacent]
        self_pairs = self_pairs[exact_pairs(vertices[tri[self_pairs[:, 0]]], vertices[tri[self_pairs[:, 1]]])]
    return tree, pairs, self_pairs

def barycentric(point, points):
    a, b, c = points
    ab, ac, ap = b-a, c-a, point-a
    aa, bb, cc = np.dot(ab, ab), np.dot(ab, ac), np.dot(ac, ac)
    den = aa*cc-bb*bb
    if den < 1e-20: return np.array([1., 0, 0])
    u = (cc*np.dot(ap, ab)-bb*np.dot(ap, ac))/den
    w = (aa*np.dot(ap, ac)-bb*np.dot(ap, ab))/den
    weights = np.maximum([1-u-w, u, w], 0)
    return weights/weights.sum()

def separated_triangle_witness(a, b):
    """Closest feature pair of two currently disjoint, non-adjacent facets."""
    best = (np.inf, None, None)
    def consider(pa, pb):
        nonlocal best
        distance = np.linalg.norm(pa-pb)
        if distance < best[0]: best = (distance, pa, pb)
    for point in a:
        consider(point, np.array(closest_point_on_tri(Vector(point), *(Vector(x) for x in b))))
    for point in b:
        consider(np.array(closest_point_on_tri(Vector(point), *(Vector(x) for x in a))), point)
    for i, j in [(0,1), (1,2), (2,0)]:
        for k, l in [(0,1), (1,2), (2,0)]:
            u, w, z = a[j]-a[i], b[l]-b[k], a[i]-b[k]
            aa, bb, cc = u@u, u@w, w@w
            dd, ee = u@z, w@z
            denominator = aa*cc-bb*bb
            ss = np.clip((bb*ee-cc*dd)/denominator, 0, 1) if denominator > 1e-20 else 0.
            tt = np.clip((bb*ss+ee)/max(cc,1e-20), 0, 1)
            ss = np.clip((bb*tt-dd)/max(aa,1e-20), 0, 1)
            consider(a[i]+ss*u, b[k]+tt*w)
    return best

def contacts(vertices, tree, crossing_pairs):
    # Full source surface determines nearest ownership. Fixed source-unit faces
    # prevent another body region being silently used as the hand carrier.
    face_normals = np.cross(vertices[tri[:, 1]]-vertices[tri[:, 0]], vertices[tri[:, 2]]-vertices[tri[:, 0]])
    face_normals /= np.maximum(np.linalg.norm(face_normals, axis=1)[:, None], 1e-15)
    rows = {}
    for i, point in enumerate(samples):
        nearest, _, face, distance = tree.find_nearest(Vector(point))
        if not mask[tri[face]].any() or distance > .05: continue
        q = np.array(nearest); normal = face_normals[face]
        # A flat nearest-face normal is unreliable at vertices/concave webs.
        # Three non-axis rays directed away from the trunk classify containment.
        # No diagnostic cap or new carrier surface is exported.
        sign = -1 if args.side == 'right' else 1
        votes = []
        for dr in [(sign, .111, .213), (sign, -.173, .307), (sign, .251, -.113)]:
            direction = Vector(dr).normalized(); origin = Vector(point); count = 0
            for _ in range(40):
                hit, _, _, _ = tree.ray_cast(origin, direction, 4.)
                if hit is None: break
                count += 1; origin = hit+direction*.000002
            votes.append(count % 2)
        inside = sum(votes) >= 2
        gap = args.target_clearance
        violation = (gap-distance) if inside else (gap+distance)
        if violation <= .00003: continue
        if distance > 1e-7:
            normal = (q-point if inside else point-q)/distance
        weights = barycentric(q, vertices[tri[face]])
        slot = (face, int(weights.argmax()))
        if slot in rows and rows[slot]['violationM'] >= violation: continue
        rows[slot] = {'skinTriangle': int(face), 'sourceObjFace': d['faces'][face//2]['sourceFace'],
            'sourceVertexIds': [d['originalVertexIds'][int(x)] for x in tri[face]],
            'barycentric': weights.tolist(),
            'skinPointM': q.tolist(), 'nativePointM': point.tolist(), 'skinOutwardNormal': normal.tolist(),
            'violationM': float(violation), 'clearanceM': gap, 'containmentRayVotes': votes,
            'nativePointInsideSkin': bool(inside), **sample_addresses[i],
            'meaning': 'native containment inequality at an addressed skin facet, not an acupoint/skin landmark'}
    # Exact crossing contacts also cover long native facets whose vertices and
    # centroids are inside while an edge cuts the skin between those samples.
    if len(crossing_pairs):
        skin_points = vertices[tri[crossing_pairs[:, 0]]]
        native_points = nv[nt[crossing_pairs[:, 1]]]
        for from_native in [True, False]:
            target_tri = skin_points if from_native else native_points
            from_tri = native_points if from_native else skin_points
            e1, e2 = target_tri[:, 1]-target_tri[:, 0], target_tri[:, 2]-target_tri[:, 0]
            for a, b in [(0, 1), (1, 2), (2, 0)]:
                direction = from_tri[:, b]-from_tri[:, a]
                pv = np.cross(direction, e2); determinant = np.einsum('ij,ij->i', e1, pv)
                denominator = np.where(np.abs(determinant) > 1e-14, determinant, 1)
                delta = from_tri[:, a]-target_tri[:, 0]
                u = np.einsum('ij,ij->i', delta, pv)/denominator
                qv = np.cross(delta, e1)
                w = np.einsum('ij,ij->i', direction, qv)/denominator
                along = np.einsum('ij,ij->i', e2, qv)/denominator
                selected = np.flatnonzero((np.abs(determinant) > 1e-14) & (u >= -1e-8) & (w >= -1e-8) & (u+w <= 1+1e-8) & (along >= 0) & (along <= 1))
                for k in selected:
                    face, native_face = map(int, crossing_pairs[k])
                    point = from_tri[k, a]+along[k]*direction[k]
                    weights = barycentric(point, vertices[tri[face]])
                    slot = (face, int(weights.argmax()))
                    if slot in rows and rows[slot]['violationM'] >= args.target_clearance: continue
                    rows[slot] = {'skinTriangle': face, 'sourceObjFace': d['faces'][face//2]['sourceFace'],
                        'sourceVertexIds': [d['originalVertexIds'][int(i)] for i in tri[face]],
                        'barycentric': weights.tolist(), 'skinPointM': point.tolist(), 'nativePointM': point.tolist(),
                        'skinOutwardNormal': face_normals[face].tolist(), 'violationM': args.target_clearance, 'clearanceM': args.target_clearance,
                        'nativeSourceKey': native_keys[native_face], 'nativeTriangle': native_local[native_face],
                        'kind': 'exact_native_skin_edge_intersection', 'meaning': 'addressed collision contact, not landmark approval'}
    rows = list(rows.values())
    energy = sum(x['violationM']**2 for x in rows)
    return rows, energy

def cubic_field(points):
    centers = np.array(record['sourceFieldCentersM']); targets = np.array(record['nativeFieldTargetsM'])
    center = centers.mean(0); x = (centers-center)/.1; q = (points-center)/.1
    rr = np.linalg.norm(x[:, None]-x[None, :], axis=2)
    poly = np.column_stack([np.ones(len(x)), x])
    matrix = np.block([[rr**3+np.diag(record['regularization']), poly], [poly.T, np.zeros((4, 4))]])
    coef = np.linalg.solve(matrix, np.vstack([targets, np.zeros((4, 3))]))
    delta = q[:, None]-x[None, :]; radius = np.linalg.norm(delta, axis=2)
    values = np.einsum('qn,no->qo', radius**3, coef[:-4])+np.column_stack([np.ones(len(q)), q])@coef[-4:]
    jac = (np.einsum('qnk,no->qok', 3*radius[:, :, None]*delta, coef[:-4])+coef[-3:].T)/.1
    return values, jac

inside_faces = np.flatnonzero(mask[tri].all(1))
fixed_helpers=[x for x in record['nativeJointControls'] if x['id'].startswith('joint-')]
helper_source=np.array([x['source'] for x in fixed_helpers])
helper_start=len(ids)+len(inside_faces)
query_source = np.vstack([source[ids], source[tri[inside_faces]].mean(1),helper_source])
query, jac = cubic_field(query_source)
query[:len(ids)] = v[ids]
initial_helper_query=query[helper_start:].copy()
hard_helpers=[x for x in fixed_helpers if args.helper_mode=='fixed' or x['id'] in args.hard_helper_ids]
helper_points = np.array([x['target'] for x in hard_helpers]).reshape(-1,3)
steps = []; accepted_contacts = []
if args.resume:
    previous = load(E / f'contact-fit-{args.resume}.json')
    candidate = load(E / f'candidates/fit-{args.resume}.json')
    assert previous['sourceUnit']['side'] == args.side
    assert previous['sourceUnit'].get('unit','hand') == args.unit
    v[ids] = np.array(candidate['positions'])[ids]
    for stage in previous['steps']:
        centers = np.array(stage['fieldCentersM']); sigma = np.array(stage['sigmaM'])
        coefficients = np.array(stage['rawFieldCoefficients'])
        delta = query[:, None]-centers[None]
        phi = np.exp(-np.einsum('qnk,qnk->qn', delta, delta)/(2*sigma**2))
        gradient = -phi[:, :, None]*delta/sigma[None, :, None]**2
        query += phi@coefficients
        jac = (np.eye(3)[None]+np.einsum('qnk,no->qok', gradient, coefficients))@jac
    replay_error = np.linalg.norm(query[:len(ids)]-v[ids], axis=1).max()
    assert replay_error < 1e-6, replay_error
    query[:len(ids)] = v[ids]
    steps = previous['steps'].copy()
    print('RESUMED', args.resume, 'field replay error', replay_error, flush=True)
tree, native_pairs, self_pairs = collision_state(v)
rows, energy = contacts(v, tree, native_pairs)
print('INITIAL', len(set(native_pairs[:, 0])), 'native', len(self_pairs), 'self', len(rows), 'contact faces', energy, flush=True)
source_unit = {'side': args.side, 'sourceVertices': ids.tolist(), 'sharedBoundaryVertices': roots.tolist(),
    'unit': args.unit, 'baseCandidate': args.base_candidate or str(B2/'candidates/fit-r22.json'),
    'sourceObjFaces': [d['faces'][i]['sourceFace'] for i in sorted(set(unit_tri_ids//2))],
    'nativeHelperControls': record['nativeJointControls'], 'initialFieldInput': str(field_path),'initialCandidate':str(initial_path),'nativeSupplement':supplement,
    'hardFixedHelperIds':[x['id'] for x in hard_helpers],
    'sourceHelperPolicy':{'mode':args.helper_mode,'maximumDerivedHandleDriftM':args.maximum_helper_drift,
        'originalSourceHelpersChanged':False,'nativeBonesChanged':False,'meaning':'static skin recipe handles, not claimed anatomical bone points'},
    'sourceTopologyAndUvPreserved': True, 'acupointMeaningApproved': False}
source_unit['referenceExceptions']=args.reference_exceptions
source_unit['rawFullReferenceQaRequired']=True
source_unit['shapeTarget']=args.shape_target
source_unit['shapeWeight']=args.shape_weight
if args.resume:
    source_unit['resumedFromRevision'] = args.resume
    source_unit['resumedCandidateSha256'] = hashlib.sha256((E / f'candidates/fit-{args.resume}.json').read_bytes()).hexdigest()
constraint_weight = 1.
barrier_pairs = set()

for iteration in range(args.steps):
    if not len(native_pairs) and not rows:
        print('UNIT_CONTACT_SOLVED', iteration, flush=True); break
    # Deterministic farthest-point surface centers; source IDs remain explicit.
    centers_ids = [int(np.argmax(v[ids, 1]))]
    lookup_global = {int(i): k for k, i in enumerate(ids)}
    for row in sorted(rows, key=lambda r: -r['violationM']):
        vertex = int(tri[row['skinTriangle']][np.array(row['barycentric']).argmax()])
        if vertex not in lookup_global: continue
        local_vertex = lookup_global[vertex]
        if np.linalg.norm(v[ids[centers_ids]]-v[vertex], axis=1).min() < .002: continue
        centers_ids.append(local_vertex)
        if len(centers_ids) >= args.centers//2: break
    nearest = np.full(len(ids), np.inf)
    for local in centers_ids[:-1]:
        nearest = np.minimum(nearest, np.linalg.norm(v[ids]-v[ids[local]], axis=1))
    for _ in range(min(args.centers, len(ids))-len(centers_ids)):
        nearest = np.minimum(nearest, np.linalg.norm(v[ids]-v[ids[centers_ids[-1]]], axis=1))
        centers_ids.append(int(nearest.argmax()))
    centers = v[ids[centers_ids]]
    sigma = (np.where(centers[:, 1] > .90, .030, np.where(centers[:, 1] > .78, .020, .011)) if args.unit=='hand'
        else np.where(centers[:,1]>.20,.030,np.where(centers[:,1]>.10,.020,args.distal_width)) if args.unit=='foot'
        else np.full(len(centers),args.distal_width))
    def gaussian(points):
        delta = points[:, None]-centers[None, :]
        phi = np.exp(-np.einsum('qnk,qnk->qn', delta, delta)/(2*sigma**2))
        derivative = -phi[:, :, None]*delta/sigma[None, :, None]**2
        return phi, derivative
    anchors = np.vstack([v[roots], helper_points])
    constraint_basis = gaussian(anchors)[0]
    _, singular, vh = np.linalg.svd(constraint_basis, full_matrices=True)
    rank = int((singular > singular[0]*1e-9).sum())
    null = vh[rank:].T
    phi, derivative = gaussian(v)
    basis = phi@null
    matrix_rows, rhs = [], []
    for row in rows:
        weights = np.array(row['barycentric'])
        feature = weights@basis[tri[row['skinTriangle']]]
        matrix_rows.append(np.outer(feature, row['skinOutwardNormal']).ravel())
        rhs.append(row['violationM'])
    matrix_rows = np.array(matrix_rows); rhs = np.array(rhs)
    if not len(rows): break
    # Preserve the posed source's differential shape, not merely small field
    # coefficients. All shared source edges contribute to the same solve.
    edges = np.array(sorted({tuple(sorted((int(x), int(y)))) for f in unit_tri
                            for x, y in zip(f, np.roll(f, -1))}))
    lookup = np.full(len(v), -1); lookup[ids] = np.arange(len(ids))
    interior_edges = edges[(lookup[edges] >= 0).all(1)]
    aa, bb = lookup[interior_edges[:, 0]], lookup[interior_edges[:, 1]]
    degree = np.bincount(np.r_[aa, bb], minlength=len(ids))
    def laplacian(values):
        neighbours = np.zeros_like(values)
        np.add.at(neighbours, aa, values[bb]); np.add.at(neighbours, bb, values[aa])
        return values-neighbours/np.maximum(degree[:, None], 1)
    unit_basis = basis[ids]; lap_basis = laplacian(unit_basis)
    prior_delta = v[ids]-shape_target[ids]; lap_prior = laplacian(prior_delta)
    regularizer = np.eye(null.shape[1])*.015 + unit_basis.T@unit_basis*.002 + lap_basis.T@lap_basis*args.shape_weight
    helper_basis=gaussian(query[helper_start:])[0]@null
    helper_prior=query[helper_start:]-initial_helper_query
    if args.helper_mode=='bounded-soft':regularizer+=helper_basis.T@helper_basis*10.
    system = constraint_weight*(matrix_rows.T@matrix_rows) + np.kron(regularizer, np.eye(3))
    target_rhs = constraint_weight*(matrix_rows.T@rhs) - (.002*unit_basis.T@prior_delta+args.shape_weight*lap_basis.T@lap_prior).ravel()
    if args.helper_mode=='bounded-soft':target_rhs-=(10.*helper_basis.T@helper_prior).ravel()
    coefficients = np.linalg.solve(system, target_rhs)
    # Rejected trials reveal the actual non-adjacent skin feature pairs. Their
    # current separation enters this same solve as a hard linear inequality;
    # rejecting a self-intersection alone provides no feasible escape direction.
    barrier_rows, barrier_rhs = [], []
    if args.hard_contacts:
        barrier_rows.extend(matrix_rows.tolist());barrier_rhs.extend(rhs.tolist())
    for fa, fb in sorted(barrier_pairs):
        ta, tb = tri[fa], tri[fb]
        distance, pa, pb = separated_triangle_witness(v[ta], v[tb])
        if distance < 1e-8 or distance > .012: continue
        direction = (pa-pb)/distance
        feature = barycentric(pa,v[ta])@basis[ta]-barycentric(pb,v[tb])@basis[tb]
        barrier_rows.append(np.outer(feature,direction).ravel())
        barrier_rhs.append(min(args.self_margin,distance*.5)-distance)
    if args.floor_m is not None:
        for vi in ids[v[ids,1] < args.floor_m+.008]:
            barrier_rows.append(np.outer(basis[vi],[0.,1.,0.]).ravel())
            barrier_rhs.append(args.floor_m-v[vi,1])
    if args.jacobian_barriers:
        _,query_gradient=gaussian(query)
        gradient_basis=np.einsum('qnk,nm->qmk',query_gradient,null)
        determinant=np.linalg.det(jac)
        predicted_trace=np.einsum('qmk,mk->q',gradient_basis,coefficients.reshape(-1,3))
        limits=.005/np.maximum(determinant,1e-12)-1
        active=np.flatnonzero((predicted_trace<limits+.1)|(determinant<.015))
        for qi in active:
            barrier_rows.append(gradient_basis[qi].ravel());barrier_rhs.append(float(limits[qi]))
        print('JACOBIAN_BARRIERS',len(active),flush=True)
    if barrier_rows:
        constraints=np.array(barrier_rows); limits=np.array(barrier_rhs)
        inverse=np.linalg.solve(system,constraints.T)
        gram=constraints@inverse
        # Hildreth dual coordinate descent solves the convex inequality QP
        # without a fixed-size active-set repair that can stop while infeasible.
        multiplier=np.zeros(len(limits)); residual=limits-constraints@coefficients
        diagonal=np.diag(gram)
        for qp_sweep in range(2000):
            maximum_change=0.
            for k in range(len(limits)):
                if diagonal[k]<1e-18:continue
                updated=max(0.,multiplier[k]+residual[k]/diagonal[k])
                change=updated-multiplier[k]
                if change:
                    multiplier[k]=updated;residual-=gram[:,k]*change
                    maximum_change=max(maximum_change,abs(change)*diagonal[k])
            if residual.max()<1e-8 and maximum_change<1e-8:break
        if not np.isfinite(multiplier).all() or not np.isfinite(residual).all():
            print('QP_NONFINITE_REJECTED',iteration,flush=True);break
        coefficients+=inverse@multiplier
        print('QP',qp_sweep,'constraints',len(limits),'maximum_violation',float(max(0,residual.max())),flush=True)
    if not np.isfinite(coefficients).all():
        print('NONFINITE_COEFFICIENTS_REJECTED',iteration,flush=True);break
    coefficients = coefficients.reshape(-1, 3)
    raw_coefficients = null@coefficients
    delta = phi@raw_coefficients
    # Only the authored source unit changes. Exact anchors also fix seam nodes.
    delta[~mask] = 0
    delta[roots] = 0
    qphi, qderivative = gaussian(query)
    qdelta = qphi@raw_coefficients
    qgradient = np.einsum('qnk,no->qok', qderivative, raw_coefficients)
    step = min(1., .008/max(float(np.linalg.norm(delta[ids], axis=1).max()), 1e-12))
    accepted = False; rejected = collections.Counter(); added_barrier=False
    while step >= 1/2048:
        trial = v+step*delta
        trial_jac = (np.eye(3)[None]+step*qgradient)@jac
        if not np.isfinite(trial).all() or not np.isfinite(trial_jac).all():
            rejected['nonfinite']+=1;step*=.5;continue
        if args.helper_mode=='bounded-soft' and np.linalg.norm(query[helper_start:]+step*qdelta[helper_start:]-initial_helper_query,axis=1).max()>args.maximum_helper_drift:
            rejected['model_handle_drift']+=1;step*=.5;continue
        if np.linalg.det(trial_jac).min() <= .004:
            rejected['jacobian'] += 1; step *= .5; continue
        next_tree, next_native, next_self = collision_state(trial)
        if len(next_self) > len(self_pairs):
            for pair in next_self:
                key=tuple(map(int,pair))
                if key not in barrier_pairs: barrier_pairs.add(key);added_barrier=True
            rejected['self_contact'] += 1; step *= .5; continue
        next_rows, next_energy = contacts(trial, next_tree, next_native)
        # Initial native penetration may have to pass nested surfaces to escape.
        # Once collision-free, exact native tests forbid its reintroduction.
        old_count=len(set(native_pairs[:,0]));next_count=len(set(next_native[:,0]))
        not_improved=(next_energy >= energy*(1-1e-7)) if not args.collision_priority else (next_count>old_count or next_count==old_count and next_energy>=energy*(1-1e-7))
        if args.shape_target:
            # The line search must use the same shape/contact objective as the
            # solve. Contact-only descent otherwise freezes the collapsed pose.
            def shape_energy(points):
                diff=points[ids]-shape_target[ids]
                return .002*float((diff*diff).sum())+args.shape_weight*float((laplacian(diff)**2).sum())
            not_improved=constraint_weight*next_energy+shape_energy(trial)>=constraint_weight*energy+shape_energy(v)
        if not_improved or (not len(native_pairs) and len(next_native)):
            rejected['contact_energy'] += 1; step *= .5; continue
        accepted = True; break
    if not accepted:
        print('RETRY_CONTACT_WEIGHT', iteration, constraint_weight, dict(rejected), flush=True)
        if added_barrier:
            print('ADDED_SELF_BARRIERS',len(barrier_pairs),flush=True)
            continue
        constraint_weight *= 5
        if constraint_weight > 100000: break
        continue
    v = trial; tree = next_tree; native_pairs = next_native; self_pairs = next_self
    rows = next_rows; energy = next_energy; query += step*qdelta; query[:len(ids)] = v[ids]; jac = trial_jac
    log = {'iteration': iteration, 'step': step, 'constraintWeight': constraint_weight, 'crossingSkinTrianglesInUnit': len(set(native_pairs[:, 0])),
        'nativeCrossingPairsInUnit': len(native_pairs), 'selfPairsTouchingUnit': len(self_pairs),
        'contactFaces': len(rows), 'contactEnergyM2': float(energy),
        'selfSeparationConstraintCount':len(barrier_rows),
        'maximumDerivedModelHelperDriftM':float(np.linalg.norm(query[helper_start:]-initial_helper_query,axis=1).max()),
        'maximumContactViolationM': max((x['violationM'] for x in rows), default=0),
        'minimumSampled3DFieldJacobian': float(np.linalg.det(jac).min()),
        'maximumBoundaryDisplacementM': float(np.linalg.norm(v[roots]-initial[roots], axis=1).max()),
        'centersSourceVertexIds': ids[centers_ids].tolist(), 'sigmaM': sigma.tolist(),
        'fieldCentersM': centers.tolist(), 'rawFieldCoefficients': (step*raw_coefficients).tolist()}
    steps.append(log); print({k: val for k, val in log.items() if not isinstance(val, list)}, flush=True)
    # 1.5mm is the solve target, 1mm the numerical source/native sample margin.
    # Neither is an anatomical skin-thickness assertion or whole-body approval.
    if not len(native_pairs) and not len(self_pairs) and max((r['violationM'] for r in rows), default=0) < args.target_clearance-args.minimum_margin:
        break

d['positions'] = v.tolist(); d['candidateRevision'] = args.revision
d['fitAcceptancePassed'] = False; d['learnerEligible'] = False
d['collisionAwareLocalField'] = {'unit': args.unit+'-'+args.side, 'method': 'native-to-addressed-skin barycentric containment inequalities; boundary/helper-null Gaussian field; exact native/self line search',
    'localCrossingTriangles': len(set(native_pairs[:, 0])), 'localSelfPairs': len(self_pairs),
    'localGeometryCandidatePassed': not len(native_pairs) and not len(self_pairs) and max((r['violationM'] for r in rows), default=0) < args.target_clearance-args.minimum_margin,
    'solveTargetClearanceM':args.target_clearance,'minimumNumericalSampleMarginM':args.minimum_margin,'wholeSkinAcceptance': False}
output.write_text(json.dumps(d, separators=(',', ':')))
result = {'revision': args.revision, 'sourceUnit': source_unit, 'steps': steps,
    'remainingContacts': rows, 'localCrossingTriangles': len(set(native_pairs[:, 0])),
    'localSelfPairs': len(self_pairs), 'wholeSkinAcceptance': False, 'learnerEligible': False,
    'localGeometryCandidatePassed': d['collisionAwareLocalField']['localGeometryCandidatePassed'],
    'nativeTriangleAddresses': [{'skinTriangle': int(a), 'nativeSourceKey': native_keys[b], 'nativeTriangle': native_local[b]} for a, b in native_pairs],
    'discoveredSelfBarrierPairs': [list(x) for x in sorted(barrier_pairs)],
    'selfBarrierWitnesses': [{'skinTriangles':[a,b], 'distanceM':float(separated_triangle_witness(v[tri[a]],v[tri[b]])[0])} for a,b in sorted(barrier_pairs)],
    'numericalMargins':{'nativeSolveTargetM':args.target_clearance,'nativeMinimumSampleMarginM':args.minimum_margin,'selfSeparationTargetM':args.self_margin,'referenceFloorM':args.floor_m},
    'limitations': 'Finite Jacobian samples do not prove global injectivity. Float32 emitted and visual QA still required.'}
(E / f'contact-fit-{args.revision}.json').write_text(json.dumps(result, indent=2)+'\n')
print('WROTE', output, result['localCrossingTriangles'], result['localSelfPairs'], flush=True)
