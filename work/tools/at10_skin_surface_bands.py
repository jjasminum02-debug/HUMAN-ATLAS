"""Offline source-addressed continuous volumetric field trials. Never approve skin.

Raw source helpers, authored surface-band proposals and fixed native facet addresses
remain separate. The field's analytic 3D Jacobian is diagnostic; exact emitted
native/self-intersection and visual QA are independent and required.
"""
from pathlib import Path
import argparse
import json
import sys
import numpy as np

R = Path(__file__).resolve().parents[2]
p = argparse.ArgumentParser()
p.add_argument('--evidence', required=True)
p.add_argument('--revision', required=True)
p.add_argument('--surface-weight', type=float, default=0)
p.add_argument('--contact-steps', type=int, default=0)
p.add_argument('--extras', action='store_true')
p.add_argument('--skip-extremities', action='store_true')
args = p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else None)
E = R / args.evidence
E.mkdir(parents=True, exist_ok=True)
(E / 'candidates').mkdir(exist_ok=True)
for output in [E / f'candidates/fit-{args.revision}.json', E / f'surface-bands-{args.revision}.json']:
    if output.exists():
        raise FileExistsError(f'Preserve existing evidence; choose a fresh revision/directory: {output}')
B = R / 'work/evidence/AT10/2026-10-13-skin-fit-r1'
B2 = R / 'work/evidence/AT10/2026-10-13-skin-fit-r2'
B3 = R / 'work/evidence/AT10/2026-10-13-skin-fit-r3'
load = lambda f: json.loads(f.read_text())
d = load(B2 / 'candidates/fit-r22.json')
s = np.array(d['sourceVertices'])
v = np.array(d['positions'])
baseline = v.copy()
controls = {x['id']: x for x in load(B / 'native-controls-r2.json')['controls']}
prior = load(B3 / 'fold-aware-correspondence-r30.json')
edges = np.array(sorted({tuple(sorted((a, b))) for f in d['faces']
                       for a, b in zip(f['derivedVertices'], f['derivedVertices'][1:] + f['derivedVertices'][:1])}))
records = []
native = load(B / 'native-surfaces-r1.json') if args.contact_steps or args.extras else None

def contact_bands(kind, side, letter, ids, mapped, map_source):
    """Source bone/face cohort -> named native surface band, never acupoint meaning."""
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    def joint(name):
        c = controls[f'joint-{letter}-{name}']
        return np.array(c['source']), np.array(c['target'])
    beams = []
    if kind == 'hand':
        sa, ta = joint('elbow'); sb, tb = joint('hand')
        beams.append(('forearm', sa, sb, ta, tb, ['antebrachial fascia', 'radius', 'ulna', 'flexor', 'extensor', 'brachioradialis'], .085))
        sa, ta = joint('hand')
        sb = np.mean([joint(f'finger-{i}-1')[0] for i in range(2, 6)], 0)
        tb = np.mean([joint(f'finger-{i}-1')[1] for i in range(2, 6)], 0)
        beams.append(('palm', sa, sb, ta, tb, ['carpal', 'palmar', 'metacarpal', 'dorsal fascia of hand', 'tendon sheath', 'lumbrical'], .065))
        prefix, count, digit_radius = 'finger', 4, .017
    else:
        sa, ta = joint('knee'); sb, tb = joint('ankle')
        beams.append(('calf', sa, sb, ta, tb, ['crural fascia', 'tibia', 'fibula', 'tibialis', 'fibularis', 'calcaneal', 'retinaculum'], .09))
        heel_ids = ids[(s[ids, 1] < -.76) & (s[ids, 2] < .015)]
        sa = s[heel_ids].mean(0)
        calc = next(n for n in native.values() if n['side'] == side and n['name'] == 'Calcaneus')
        ta = np.array(calc['v']).mean(0)
        sb = np.mean([joint(f'toe-{i}-1')[0] for i in range(1, 6)], 0)
        tb = np.mean([joint(f'toe-{i}-1')[1] for i in range(1, 6)], 0)
        beams.append(('heel-dorsal-plantar-MTP', sa, sb, ta, tb, ['foot', 'plantar', 'metatarsal', 'calcaneus', 'talus', 'cuneiform', 'cuboid', 'navicular', 'tendon', 'retinaculum'], .073))
        prefix, count, digit_radius = 'toe', 3, .016
    for digit in range(1, 6):
        word = ['first', 'second', 'third', 'fourth', 'fifth'][digit-1]
        for part in range(1, count):
            sa, ta = joint(f'{prefix}-{digit}-{part}'); sb, tb = joint(f'{prefix}-{digit}-{part+1}')
            terms = [f'phalanx of {word} finger of '+('hand' if kind == 'hand' else 'foot')]
            # Shared fascia/tendons are clipped by the actual digit axis and radius.
            terms += ['tendon sheath', 'tendon of extensor digitorum', 'dorsal fascia of hand', 'lumbrical']
            if digit == 1 and kind == 'hand': terms.append('first metacarpal')
            beams.append((f'{prefix}-{digit}-{part}', sa, sb, ta, tb, terms, digit_radius))
    contexts = []
    for role, sa, sb, ta, tb, terms, radius in beams:
        verts, triangles, addresses = [], [], []
        axis = tb-ta; length = np.linalg.norm(axis); axis /= length
        for key, n in native.items():
            if n['side'] != side or not any(t in n['name'].lower() for t in terms): continue
            nv = np.array(n['v']); nt = np.array(n['t'])
            assert np.isfinite(nv).all()
            q = nv[nt].mean(1)-ta
            with np.errstate(over='ignore', invalid='ignore'):
                along = q@axis
            assert np.isfinite(along).all(), key
            radial = np.linalg.norm(q-along[:, None]*axis, axis=1)
            selected = np.flatnonzero((along > -.02) & (along < length+.02) & (radial < radius))
            off = len(verts); verts.extend(nv.tolist()); triangles.extend((nt[selected]+off).tolist())
            addresses.extend((key, int(i)) for i in selected)
        contexts.append((BVHTree.FromPolygons(verts, triangles, all_triangles=True), addresses))
    # Correspondences form complete source-face bands, not a few extrema controls.
    rows = []
    for local, i in enumerate(ids):
        options = []
        for bi, (_, sa, sb, ta, tb, _, radius) in enumerate(beams):
            axis = sb-sa; u = np.dot(s[i]-sa, axis)/np.dot(axis, axis)
            center = sa+np.clip(u, 0, 1)*axis
            dist = np.linalg.norm(s[i]-center)
            if bi >= 2 and (u < -.08 or dist > (.023 if kind == 'hand' else .019)): continue
            options.append((dist, bi, u, center))
        if not options: continue
        _, bi, u, center = min(options, key=lambda x: x[0])
        role, sa, sb, ta, tb, _, radius = beams[bi]
        source_axis = sb-sa
        # Distinguish calf/forearm from their adjoining foot/palm in source space.
        if bi == 0 and u > 1.01: bi = 1
        role, sa, sb, ta, tb, _, radius = beams[bi]
        source_axis = sb-sa
        u = np.clip(np.dot(s[i]-sa, source_axis)/np.dot(source_axis, source_axis), 0, 1)
        source_center = sa+u*source_axis
        mapped_center = map_source(source_center[None, :])[0]
        direction = mapped[local]-mapped_center
        if np.linalg.norm(direction) < .0005: continue
        direction /= np.linalg.norm(direction)
        native_center = ta+u*(tb-ta)
        origin = native_center+direction*.18; remaining = .30
        for _ in range(48):
            hit, normal, ti, distance = contexts[bi][0].ray_cast(Vector(origin), Vector(-direction), remaining)
            if hit is None: break
            hit = np.array(hit); axis = tb-ta; length = np.linalg.norm(axis); axis /= length
            q = hit-ta; along = np.dot(q, axis)
            if np.linalg.norm(q-along*axis) < radius and along > -.018 and along < length+.018:
                key, native_tri = contexts[bi][1][ti]
                allowance = .003 if bi >= 2 else .005
                target = hit+direction*allowance
                if np.linalg.norm(target-mapped[local]) > .045: break
                facet = np.array(native[key]['v'])[native[key]['t'][native_tri]]
                rows.append({'vertex': int(i), 'sourceVertex': d['originalVertexIds'][int(i)],
                    'sourceObjFaces': [f['sourceFace'] for f in d['faces'] if int(i) in f['derivedVertices']],
                    'sourceM': s[i].tolist(), 'mappedM': mapped[local].tolist(), 'targetM': target.tolist(),
                    'sourceAxisCenterM': source_center.tolist(),
                    'sourceBandRole': role, 'sourceAxialFraction': float(u),
                    'sourceNormalHemisphere': 'positive-source-Y' if s[i, 1] >= source_center[1] else 'negative-source-Y',
                    'nativeSourceKey': key, 'nativeTriangle': native_tri, 'nativeWorldM': facet.tolist(),
                    'allowanceM': allowance, 'placementVerified': False,
                    'meaning': 'geometric surface pair after source/native joint registration; no acupoint or homology approval'})
                break
            remaining -= distance+.00001; origin = hit-direction*.00001
            if remaining <= 0: break
    return rows

def smooth(x):
    x = np.clip(x, 0, 1)
    return x*x*(3-2*x)

def field(source, target, soft, query, scale=.10):
    origin = source.mean(0)
    x = (source-origin)/scale
    q = (query-origin)/scale
    radius = np.linalg.norm(x[:, None]-x[None, :], axis=2)
    poly = np.column_stack([np.ones(len(x)), x])
    matrix = np.block([[radius**3 + np.diag(soft), poly], [poly.T, np.zeros((4, 4))]])
    coefficients = np.linalg.solve(matrix, np.vstack([target, np.zeros((4, 3))]))
    assert np.isfinite(coefficients).all()
    delta = q[:, None]-x[None, :]
    rr = np.linalg.norm(delta, axis=2)
    out = rr**3 @ coefficients[:-4] + np.column_stack([np.ones(len(q)), q]) @ coefficients[-4:]
    jac = np.einsum('qnk,no->qok', 3*rr[:, :, None]*delta, coefficients[:-4])
    jac += coefficients[-3:].T
    assert np.isfinite(out).all() and np.isfinite(jac).all()
    return out, jac/scale

for side, letter, sign in [('left', 'l', 1), ('right', 'r', -1)]:
    for kind in ([] if args.skip_extremities else ['hand', 'foot']):
        if kind == 'hand':
            a = np.array(controls[f'joint-{letter}-elbow']['source'])
            b = np.array(controls[f'joint-{letter}-hand']['source'])
            axis = b-a
            u = (s-a) @ axis / np.dot(axis, axis)
            radial = np.linalg.norm(s-(a+np.clip(u, 0, 1)[:, None]*axis), axis=1)
            ids = np.flatnonzero(((s[:, 0]*sign > .22) & (u > .15) & (radial < .07)) | (s[:, 0]*sign > .40))
            names = [f'joint-{letter}-hand'] + [f'joint-{letter}-finger-{di}-{j}' for di in range(1, 6) for j in range(1, 5)]
        else:
            knee = np.array(controls[f'joint-{letter}-knee']['source'])
            ids = np.flatnonzero((s[:, 0]*sign > .04) & (s[:, 1] < knee[1]-.06))
            names = [f'joint-{letter}-ankle'] + [f'joint-{letter}-toe-{di}-{j}' for di in range(1, 6) for j in range(1, 4)]
        mask = np.zeros(len(s), bool)
        mask[ids] = True
        crossing = edges[mask[edges].any(1) & ~mask[edges].all(1)]
        roots = np.unique(crossing[mask[crossing]])
        neighbours = np.unique(edges[np.isin(edges, roots).any(1)])
        roots = np.unique(np.r_[roots, neighbours[mask[neighbours]]])
        root_rows = [{'sourceVertex': d['originalVertexIds'][int(i)], 'sourceM': s[i].tolist(),
                      'targetM': baseline[i].tolist(), 'kind': 'shared boundary, r22 retained'} for i in roots]
        source = [s[i] for i in roots]
        target = [baseline[i] for i in roots]
        soft = [1e-10]*len(roots)
        for name in names:
            source.append(controls[name]['source'])
            target.append(controls[name]['target'])
            soft.append(1e-6)
        patch = next(x for x in prior['patches'] if x['patch'] == kind+'-'+side)
        selected = []
        if args.surface_weight:
            for c in patch['constraintsData'][::2]:
                if not mask[c['vertex']] or c['vertex'] in roots:
                    continue
                source.append(c['sourceM'])
                target.append(c['targetM'])
                soft.append(.003/args.surface_weight)
                selected.append(c)
        out, jac = field(np.array(source), np.array(target), np.array(soft), s[ids])
        source_controls, targets, regularization = np.array(source), np.array(target), np.array(soft)
        surface_rows = []
        contact_log = []
        if args.contact_steps:
            mapper = lambda points: field(source_controls, targets, regularization, points)[0]
            surface_rows = contact_bands(kind, side, letter, ids, out, mapper)
            # A single smooth volumetric correction per stage shares all seam nodes.
            selected_rows = surface_rows[::max(1, len(surface_rows)//360)]
            joint_query, _ = field(source_controls, targets, regularization, np.array([controls[k]['source'] for k in names]))
            for stage in range(args.contact_steps):
                lookup = {int(i): j for j, i in enumerate(ids)}
                control_ids = [r['vertex'] for r in selected_rows if r['vertex'] not in roots]
                control_targets = [r['targetM'] for r in selected_rows if r['vertex'] not in roots]
                cs = np.vstack([out[[lookup[i] for i in control_ids]], out[[lookup[int(i)] for i in roots]], joint_query])
                ct = np.vstack([np.array(control_targets)-out[[lookup[i] for i in control_ids]], np.zeros((len(roots)+len(joint_query), 3))])
                reg = np.r_[np.full(len(control_ids), .015), np.full(len(roots), 1e-9), np.full(len(joint_query), 1e-6)]
                displacement, dj = field(cs, ct, reg, out)
                prior_error = np.array([np.linalg.norm(out[lookup[r['vertex']]]-r['targetM']) for r in surface_rows])
                step = 1.
                while step > 1/4096:
                    trial_j = (np.eye(3)[None]+step*dj)@jac
                    trial_out = out+step*displacement
                    trial_error = np.array([np.linalg.norm(trial_out[lookup[r['vertex']]]-r['targetM']) for r in surface_rows])
                    if np.linalg.det(trial_j).min() > .003 and trial_error.mean() <= prior_error.mean() and trial_error.max() <= prior_error.max()+.001: break
                    step *= .5
                if step <= 1/4096: break
                out += step*displacement; jac = trial_j
                joint_query += step*field(cs, ct, reg, joint_query)[0]
                residuals = [np.linalg.norm(out[lookup[r['vertex']]]-r['targetM']) for r in surface_rows]
                contact_log.append({'stage': stage, 'step': step, 'minimumJacobian': float(np.linalg.det(jac).min()),
                    'maximumSurfacePairResidualM': float(max(residuals)), 'meanSurfacePairResidualM': float(np.mean(residuals)),
                    'fieldCentersM': cs.tolist(), 'displacementTargetsM': ct.tolist(), 'regularization': reg.tolist()})
        determinants = np.linalg.det(jac)
        v[ids] = out
        # Explicit shared source vertices are continuous with the unchanged body.
        boundary_error = np.max(np.linalg.norm(v[roots]-baseline[roots], axis=1))
        v[roots] = baseline[roots]
        predicted, _ = field(np.array(source), np.array(target), np.array(soft), np.array(source))
        residual = np.linalg.norm(predicted-np.array(target), axis=1)
        record = {'patch': kind+'-'+side, 'sourceVertices': [d['originalVertexIds'][int(i)] for i in ids],
                  'sharedBoundary': root_rows, 'nativeJointControls': [controls[k] for k in names],
                  'surfaceBandProposalsUsed': selected,
                  'surfaceBandMeaning': 'authored proposal, not verified homology/skin landmark/acupoint',
                  'sourceFieldCentersM': np.array(source).tolist(), 'nativeFieldTargetsM': np.array(target).tolist(),
                  'regularization': soft, 'sourceFieldScaleM': .1,
                  'continuousSurfaceBandPairs': surface_rows, 'contactCorrectionStages': contact_log,
                  'minimumAnalyticFieldJacobian': float(determinants.min()),
                  'nonPositiveAnalyticJacobianCount': int((determinants <= 0).sum()),
                  'maximumSharedBoundaryResidualBeforeExactJoinM': float(boundary_error),
                  'initialHelperBoundaryResidualM': float(residual.max()),
                  'finalHelperCenterDriftM': float(np.linalg.norm(joint_query-np.array([controls[k]['target'] for k in names]), axis=1).max()) if args.contact_steps else None,
                  'sourceBodyPreserved': True, 'nativeModified': False, 'acceptancePassed': False}
        records.append(record)
        print({k: record[k] for k in ['patch', 'minimumAnalyticFieldJacobian', 'nonPositiveAnalyticJacobianCount', 'initialHelperBoundaryResidualM']}, flush=True)

if args.extras:
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    source_normals = np.zeros_like(s)
    for f in d['faces']:
        a, b, c = f['derivedVertices'][:3]
        n = np.cross(s[b]-s[a], s[c]-s[a])
        for i in f['derivedVertices']: source_normals[i] += n
    source_normals /= np.maximum(np.linalg.norm(source_normals, axis=1)[:, None], 1e-12)
    extra_configs = [
        ('ear-left', np.flatnonzero((s[:, 0] > .058) & (s[:, 1] > .638) & (s[:, 1] < .75) & (s[:, 2] < .078)), []),
        ('ear-right', np.flatnonzero((s[:, 0] < -.058) & (s[:, 1] > .638) & (s[:, 1] < .75) & (s[:, 2] < .078)), []),
        ('pelvis-bilateral', np.flatnonzero((np.abs(s[:, 0]) < .25) & (s[:, 1] > -.30) & (s[:, 1] < .12)), ['joint-pelvis', 'joint-l-upper-leg', 'joint-r-upper-leg'])
    ]
    ear_prior = load(B3 / 'fold-aware-correspondence-r27.json')
    for label, ids, joint_names in extra_configs:
        mask = np.zeros(len(s), bool); mask[ids] = True
        crossing = edges[mask[edges].any(1) & ~mask[edges].all(1)]
        roots = np.unique(crossing[mask[crossing]])
        neighbours = np.unique(edges[np.isin(edges, roots).any(1)])
        roots = np.unique(np.r_[roots, neighbours[mask[neighbours]]])
        sources = [s[i] for i in roots]; targets = [baseline[i] for i in roots]; soft = [1e-9]*len(roots)
        if label.startswith('ear'):
            original = next(x for x in ear_prior['patches'] if x['patch'] == label)
            for row in original['constraintsData']:
                sources.append(row['sourceM']); targets.append(row['targetM']); soft.append(.002)
            context_keys = [k for k, n in native.items() if n['side'] == label.split('-')[1] and any(t in n['name'] for t in ['Helix.', 'Lobule of auricle.', 'Tragus.', 'Auricular region.'])]
        else:
            for name in joint_names:
                sources.append(controls[name]['source']); targets.append(controls[name]['target']); soft.append(1e-6)
            context_keys = [k for k, n in native.items() if any(t in n['name'].lower() for t in ['gluteus maximus', 'fascia lata', 'adductor', 'gracilis', 'pectineus', 'investing abdominal fascia'])]
        sources, targets, soft = np.array(sources), np.array(targets), np.array(soft)
        out, jac = field(sources, targets, soft, s[ids])
        verts, triangles, addresses = [], [], []
        for key in context_keys:
            n = native[key]; nv = np.array(n['v']); nt = np.array(n['t']); off = len(verts)
            verts.extend(nv.tolist()); triangles.extend((nt+off).tolist()); addresses.extend((key, j) for j in range(len(nt)))
        bvh = BVHTree.FromPolygons(verts, triangles, all_triangles=True)
        rows = []
        for local, i in enumerate(ids):
            if i in roots: continue
            point, normal, tri, distance = bvh.find_nearest(Vector(out[local]))
            if distance > (.014 if label.startswith('ear') else .035): continue
            key, local_tri = addresses[tri]
            transported = np.linalg.solve(jac[local].T, source_normals[i]); transported /= np.linalg.norm(transported)
            target = np.array(point)+transported*(.0025 if label.startswith('ear') else .006)
            facet = np.array(native[key]['v'])[native[key]['t'][local_tri]]
            rows.append({'vertex': int(i), 'sourceVertex': d['originalVertexIds'][int(i)],
                'sourceObjFaces': [f['sourceFace'] for f in d['faces'] if int(i) in f['derivedVertices']],
                'sourceM': s[i].tolist(), 'mappedM': out[local].tolist(), 'targetM': target.tolist(),
                'nativeSourceKey': key, 'nativeTriangle': local_tri, 'nativeWorldM': facet.tolist(),
                'sourceBandRole': label+'-source-face-normal-cohort', 'placementVerified': False,
                'meaning': 'named-surface geometric registration proposal; not approved homology/acupoint'})
        stages = []; lookup = {int(i): j for j, i in enumerate(ids)}
        for stage in range(6):
            chosen = rows[::max(1, len(rows)//300)]
            cs = np.vstack([[out[lookup[r['vertex']]] for r in chosen], out[[lookup[int(i)] for i in roots]]])
            ct = np.vstack([[np.array(r['targetM'])-out[lookup[r['vertex']]] for r in chosen], np.zeros((len(roots), 3))])
            reg = np.r_[np.full(len(chosen), .02), np.full(len(roots), 1e-9)]
            delta, dj = field(cs, ct, reg, out); step = 1.
            while step > 1/4096:
                tj = (np.eye(3)[None]+step*dj)@jac
                if np.linalg.det(tj).min() > .002: break
                step *= .5
            if step <= 1/4096: break
            out += step*delta; jac = tj
            stages.append({'stage': stage, 'step': step, 'minimumJacobian': float(np.linalg.det(jac).min()),
                'fieldCentersM': cs.tolist(), 'displacementTargetsM': ct.tolist(), 'regularization': reg.tolist()})
        v[ids] = out; v[roots] = baseline[roots]
        det = np.linalg.det(jac)
        record = {'patch': label, 'sourceVertices': [d['originalVertexIds'][int(i)] for i in ids],
            'sharedBoundaryVertices': roots.tolist(), 'sourceFieldCentersM': sources.tolist(),
            'nativeFieldTargetsM': targets.tolist(), 'regularization': soft.tolist(),
            'sourceFieldScaleM': .1, 'continuousSurfaceBandPairs': rows,
            'contactCorrectionStages': stages, 'nativeJointControls': [controls[k] for k in joint_names],
            'minimumAnalyticFieldJacobian': float(det.min()), 'nonPositiveAnalyticJacobianCount': int((det <= 0).sum()),
            'nativeModified': False, 'acceptancePassed': False,
            'sourceBandMeaning': 'surface registration proposal; source extrema prior retained as unverified; actual whole patch QA required'}
        records.append(record)
        print({k: record[k] for k in ['patch', 'minimumAnalyticFieldJacobian', 'nonPositiveAnalyticJacobianCount']}, flush=True)
d['positions'] = v.tolist()
d['candidateRevision'] = args.revision
d['fitAcceptancePassed'] = False
d['learnerEligible'] = False
d['continuousSurfaceField'] = {'method': 'cubic volumetric radial-basis field, source helper controls and common Dirichlet surface seam',
                                'sourceTopologyPreserved': True, 'geometryAcceptance': False}
(E / f'candidates/fit-{args.revision}.json').write_text(json.dumps(d, separators=(',', ':')))
(E / f'surface-bands-{args.revision}.json').write_text(json.dumps({'patches': records, 'surfaceWeight': args.surface_weight,
    'primaryR22Unchanged': True, 'geometryAcceptance': False, 'learnerEligible': False}, indent=2)+'\n')
