"""Owned trunk refinement of the existing source-topology solver.

Acceptance minima and fixed masks are unchanged. The added switch forces the
near-bone inequalities to be solved at adjacent keys even when those keys
currently pass, because actual emitted intermediate contact has been observed.
The existing helper predicates/projection are reused, not a relaxed validator.
"""
from collections import deque
import numpy as np
from t66_contact_correctives import (bounded_inside, nearest_surface_details, inside,
    outward_surface_direction)

def _weighted_halfspace_projection(A,b,E,e,weights,max_cycles=5000,tolerance=1e-10):
    """Weighted active-set QP; certify every normalized constraint before return."""
    A=np.asarray(A,dtype=float).reshape((-1,len(weights)));b=np.asarray(b,dtype=float)
    E=np.asarray(E,dtype=float).reshape((-1,len(weights)));e=np.asarray(e,dtype=float)
    norm=np.linalg.norm(A,axis=1);live=norm>1e-25
    if np.any((~live)&(b>1e-15)):raise ValueError('infeasible constant geometry constraint')
    A=A[live]/norm[live,None];b=b[live]/norm[live]
    if len(E):en=np.linalg.norm(E,axis=1);E=E/en[:,None];e=e/en
    inverse=1/np.asarray(weights);active=[];C=E.copy();rhs=e.copy()
    gram=(C*inverse)@C.T
    multipliers=np.linalg.lstsq(gram,rhs,rcond=1e-13)[0] if len(C) else np.empty(0)
    x=inverse*(C.T@multipliers) if len(C) else np.zeros(len(weights));pivots=0
    for cycle in range(max_cycles):
        residual=b-A@x;worst=max(0.,float(residual.max())) if len(A) else 0.;eq=float(np.max(np.abs(E@x-e))) if len(E) else 0.
        if worst<tolerance and eq<tolerance:return x,pivots+1,worst,eq
        new=int(np.argmax(residual));row=A[new];pending_multiplier=0.
        while True:
            pivots+=1
            if pivots>max_cycles:return x,pivots,worst,eq
            direction=inverse*row
            v=np.linalg.lstsq((C*inverse)@C.T,C@direction,rcond=1e-13)[0] if len(C) else np.empty(0)
            z=direction-inverse*(C.T@v) if len(C) else direction
            denom=float(row@z);need=(b[new]-row@x)/denom if denom>1e-20 else np.inf
            ratios=[(float(multipliers[j]/v[j]),j) for j in range(len(E),len(C)) if v[j]>1e-14]
            dual_step,drop=min(ratios,default=(np.inf,None));step=min(need,dual_step)
            if not np.isfinite(step):raise ValueError(('infeasible native contact planes',worst,len(active)))
            step=max(0.,float(step));x+=step*z;multipliers-=step*v;pending_multiplier+=step
            if need<=dual_step+1e-12:
                C=np.concatenate([C,row[None,:]],axis=0);multipliers=np.r_[multipliers,pending_multiplier];active.append(new);break
            C=np.delete(C,drop,axis=0);multipliers=np.delete(multipliers,drop);del active[drop-len(E)]
    return x,pivots,worst,eq


def source_topology_contact_patch_corrective(frame,rest,triangles,contacts,locked,edge_targets,
        patch_rings=3,margin_metres=.0002,contact_guard_metres=.01,shape_floor=.1,
        max_outer_iterations=8,max_projection_cycles=5000,shape_seed_vertices=(),topology_groups=(),force_contact_guard=False,contact_rest_bones=None,preserve_group_pose_vectors=False,branch_guards=()):
    """Repair a derived contact pose in a source-topology-local patch.

    `edge_targets` are source-geometry continuity constraints computed by the
    authoring caller from the exact source edge and current per-vertex motion
    field. Contact inequalities use nearest points on the actual pinned source
    bone triangles. A minimum-displacement local correction is projected against
    source winding/area constraints; no attachment coordinate or normal is
    inferred from the corrective. This is an educational derivation, not a
    measured physiological deformation.
    """
    product_minimum_area_ratio=.1
    original=np.asarray(frame,dtype=float).copy();x=original.copy();rest=np.asarray(rest,dtype=float)
    group_reference=original if preserve_group_pose_vectors else rest
    triangles=np.asarray(triangles,dtype=np.int64);locked=set(map(int,locked))
    if patch_rings<2 or margin_metres<=0 or contact_guard_metres<margin_metres or not 0<shape_floor<=1:
        raise ValueError('invalid source-topology patch bounds')
    edges=[];seeds=set()
    for row in edge_targets:
        vertices=list(map(int,row['vertices']));desired=np.asarray(row['desiredVectorMetres'],dtype=float)
        if len(vertices)!=2 or vertices[0]==vertices[1] or desired.shape!=(3,) or not np.isfinite(desired).all():
            raise ValueError('invalid exact source-topology edge target')
        if min(vertices)<0 or max(vertices)>=len(x) or set(vertices)&locked:
            raise ValueError('source topology edge target is invalid or overlaps fixed/moving endpoint masks')
        edges.append({'vertices':vertices,'desired':desired})
        seeds.update(vertices)
    group_rows=[sorted(set(map(int,group))) for group in topology_groups if len(set(group))>1]
    group_vertices=set()
    for group in group_rows:
        if min(group)<0 or max(group)>=len(x):raise ValueError('source-topology displacement group index outside target mesh')
        if set(group)&locked:raise ValueError('source-topology displacement group overlaps fixed/moving endpoint mask')
        if group_vertices.intersection(group):raise ValueError('overlapping source-topology displacement groups')
        group_vertices.update(group);seeds.update(group)
    shape_seeds=set(map(int,shape_seed_vertices))
    if shape_seeds and (min(shape_seeds)<0 or max(shape_seeds)>=len(x)):
        raise ValueError('source-triangle shape seed index outside target mesh')
    seeds.update(shape_seeds)
    seeds.update(int(g[0]) for g in branch_guards)
    contact_seeds=set()
    for key,bone,bone_triangles,baseline in contacts:
        fresh=np.flatnonzero(bounded_inside(x,bone,bone_triangles)&~np.asarray(baseline,dtype=bool))
        if set(map(int,fresh))&locked:
            raise ValueError(f'new bone contact intersects a fixed/moving endpoint mask: {key} {fresh.tolist()}')
        contact_seeds.update(map(int,fresh))
        seeds.update(map(int,fresh))
    # Avoid building and projecting a large constraint system at a pose that
    # already satisfies the exact source contact, topology, and winding tests.
    # This is an equivalent no-op branch: all acceptance predicates are checked
    # against the unmodified frame before returning it.
    source_triangles=rest[triangles]
    source_normals=np.cross(source_triangles[:,1]-source_triangles[:,0],
        source_triangles[:,2]-source_triangles[:,0])
    source_area=np.linalg.norm(source_normals,axis=1);nondegenerate=source_area>=1e-12
    posed_triangles=x[triangles]
    posed_normals=np.cross(posed_triangles[:,1]-posed_triangles[:,0],
        posed_triangles[:,2]-posed_triangles[:,0])
    posed_area=np.linalg.norm(posed_normals,axis=1)
    no_op_flips=int((((posed_normals*source_normals).sum(axis=1)<0)&nondegenerate).sum())
    no_op_minimum=(float((posed_area[nondegenerate]/np.maximum(source_area[nondegenerate],1e-12)).min())
        if nondegenerate.any() else 1.0)
    no_op_contacts=[]
    for key,bone,bone_triangles,baseline in contacts:
        fresh=np.flatnonzero(bounded_inside(x,bone,bone_triangles)&~np.asarray(baseline,dtype=bool))
        if len(fresh):no_op_contacts.append({'boneSourceKey':key,'sourceVertexIndices':fresh.tolist()})
    no_op_edge_errors=[float(np.linalg.norm((x[row['vertices'][1]]-x[row['vertices'][0]])-row['desired']))
        for row in edges]
    no_op_group_errors=[float(np.max(np.linalg.norm((x[group]-group_reference[group])-
        (x[group[0]]-group_reference[group[0]]),axis=1))) for group in group_rows]
    if (not force_contact_guard and not no_op_contacts and no_op_flips==0 and no_op_minimum>=shape_floor
            and max(no_op_edge_errors,default=0.0)<=1e-5
            and max(no_op_group_errors,default=0.0)<=1e-9):
        return x,{'method':'source-topology-local-minimum-displacement-contact-patch-v1-no-op-verified',
            'marginMetres':margin_metres,'contactCorrectiveRecords':[],
            'topologyGroups':[{'vertices':group,'maximumDisplacementResidualMetres':error,
                'constraintStatus':'already-satisfied'} for group,error in zip(group_rows,no_op_group_errors)],
            'correctedVertexIndices':[],'maximumCorrectiveMetres':0.0,
            'triangleOrientationFlips':no_op_flips,'minimumSourceAreaRatio':no_op_minimum,
            'shapeCorrectiveTargetRatio':shape_floor,'productMinimumAreaRatio':product_minimum_area_ratio,
            'remainingNewContactVertices':[],'sourceTopologyEdgeErrorsMetres':no_op_edge_errors,
            'sourceTopologyGroupErrorsMetres':no_op_group_errors}
    if not edges and not group_rows and not shape_seeds and not contact_seeds:
        raise ValueError('source-topology contact patch requires a source contact, shape seed, edge, or displacement group')
    adjacency=[set() for _ in x]
    for a,b,c in triangles:
        for u,v in ((a,b),(b,c),(c,a)):
            adjacency[int(u)].add(int(v));adjacency[int(v)].add(int(u))
    distance={vertex:0 for vertex in seeds};queue=deque(sorted(seeds))
    while queue:
        vertex=queue.popleft()
        for neighbor in adjacency[vertex]:
            if neighbor not in distance:
                distance[neighbor]=distance[vertex]+1;queue.append(neighbor)
    variable=np.asarray(sorted(vertex for vertex,depth in distance.items()
        if depth<patch_rings and vertex not in locked),dtype=np.int64)
    # Eliminate exact seam equalities instead of thousands of redundant rows.
    # Every cluster receives one shared displacement; this is the same feasible
    # set and sum-of-vertex weighted objective as the original equality solver.
    grouped=set(v for group in group_rows for v in group)
    clusters=group_rows+[[int(v)] for v in variable if int(v) not in grouped]
    index={int(vertex):offset for offset,cluster in enumerate(clusters) for vertex in cluster}
    for group in group_rows:
        x[group]=group_reference[group]+(x[group]-group_reference[group]).mean(axis=0)

    if not seeds.issubset(index):
        raise ValueError('source-topology contact edge intersects fixed or out-of-patch vertices')
    affected=np.flatnonzero(np.isin(triangles,variable).any(axis=1));patch_triangles=triangles[affected]
    rest_triangles=rest[patch_triangles]
    rest_normals=np.cross(rest_triangles[:,1]-rest_triangles[:,0],rest_triangles[:,2]-rest_triangles[:,0])
    rest_areas=np.linalg.norm(rest_normals,axis=1);nondegenerate=rest_areas>=1e-12
    patch_triangles=patch_triangles[nondegenerate];rest_normals=rest_normals[nondegenerate]
    minimum_projected_area=shape_floor*np.sum(rest_normals*rest_normals,axis=1)
    objective_weights=np.repeat(np.asarray([sum(1+.25*distance[int(v)] for v in cluster) for cluster in clusters]),3)
    baseline_by_contact=[np.asarray(contact[3],dtype=bool) for contact in contacts]
    source_planes={}
    if contact_rest_bones:
        for key,bone,bone_triangles,baseline in contacts:
            native=np.asarray(contact_rest_bones[key]);q,fi=nearest_surface_details(rest[variable],native,bone_triangles)
            delta=rest[variable]-q;length=np.linalg.norm(delta,axis=1)
            unit=delta/np.maximum(length[:,None],1e-30)
            for j in np.flatnonzero(length<1e-8):unit[j],_=outward_surface_direction(rest[variable[j]],q[j],native,bone_triangles,fi[j])
            transform=np.linalg.lstsq(np.c_[native,np.ones(len(native))],bone,rcond=None)[0]
            posed_unit=unit@transform[:3];posed_unit/=np.maximum(np.linalg.norm(posed_unit,axis=1)[:,None],1e-30)
            source_planes[key]={int(v):(q[j]@transform[:3]+transform[3],posed_unit[j]) for j,v in enumerate(variable)}
    records=[];last_projection=(0,0.0,0.0);remaining=[]
    for outer in range(max_outer_iterations):
        rows=[];bounds=[];equalities=[];equality_bounds=[]
        for vertex,q,unit in branch_guards:
            row=np.zeros(len(clusters)*3);offset=index[int(vertex)]*3;row[offset:offset+3]=unit
            rows.append(row);bounds.append(float(contact_guard_metres-unit@(x[vertex]-q)))
        for key,bone,bone_triangles,baseline in contacts:
            fresh=np.flatnonzero(bounded_inside(x,bone,bone_triangles)&~np.asarray(baseline,dtype=bool))
            if any(int(vertex) not in index for vertex in fresh):
                raise ValueError(f'contact vertex outside source-topology patch: {key} {fresh.tolist()}')
            bone_min=bone.min(axis=0)-contact_guard_metres;bone_max=bone.max(axis=0)+contact_guard_metres
            candidates=np.flatnonzero(((x[variable]>=bone_min)&(x[variable]<=bone_max)).all(axis=1))
            candidates=np.asarray([int(variable[row]) for row in candidates
                if not bool(np.asarray(baseline,dtype=bool)[int(variable[row])])],dtype=np.int64)
            if len(candidates):
                surface,face_indices=nearest_surface_details(x[candidates],bone,bone_triangles)
                vector=surface-x[candidates];length=np.linalg.norm(vector,axis=1)
                in_surface=inside(x[candidates],bone,bone_triangles)
                for vertex,q,face_index,distance,is_inside in zip(candidates,surface,face_indices,length,in_surface):
                    # The guard limits outside candidates, never an actual
                    # fresh penetration that is already inside the bone.
                    if distance>contact_guard_metres and not is_inside:continue
                    if distance>1e-8:
                        unit=(q-x[vertex])/distance if is_inside else (x[vertex]-q)/distance
                    else:
                        unit,_=outward_surface_direction(x[vertex],q,bone,bone_triangles,face_index)
                    signed=-float(distance) if is_inside else float(distance)
                    if key in source_planes and is_inside:
                        # Preserve the observed source side of a thin bone;
                        # nearest-face switching would interpolate through it.
                        q,unit=source_planes[key][int(vertex)]
                        signed=float(unit@(x[vertex]-q))
                        if is_inside:
                            # A curved/concave bone can remain inside beyond
                            # its original tangent plane. Exit along the
                            # preserved native side, rather than switching to
                            # the opposite nearest face of a thin rib.
                            lo=0.;hi=.0001
                            while bounded_inside((x[vertex]+unit*hi)[None,:],bone,bone_triangles)[0] and hi<.032:hi*=2
                            if bounded_inside((x[vertex]+unit*hi)[None,:],bone,bone_triangles)[0]:raise ValueError('native-side exit exceeds authored local contact range')
                            for _ in range(16):
                                mid=(lo+hi)/2
                                if bounded_inside((x[vertex]+unit*mid)[None,:],bone,bone_triangles)[0]:lo=mid
                                else:hi=mid
                            signed=-hi
                    row=np.zeros(len(clusters)*3);offset=index[int(vertex)]*3
                    row[offset:offset+3]=unit
                    rows.append(row);bounds.append(float(margin_metres-signed))
                    records.append({'outerIteration':outer+1,'kind':'bone_surface_nonpenetration_guard',
                        'boneSourceKey':key,'sourceVertexIndex':int(vertex),
                        'insideAtSolve':bool(is_inside),'signedDistanceMetres':signed,
                        'guardDistanceMetres':contact_guard_metres})
        for edge in edges:
            a,b=edge['vertices'];desired=edge['desired'];current=x[b]-x[a]
            for component in range(3):
                row=np.zeros(len(clusters)*3)
                row[index[b]*3+component]=1;row[index[a]*3+component]=-1
                equalities.append(row);equality_bounds.append(float(desired[component]-current[component]))
        # Near-coincident source vertices that were shown by emitted-GLB
        # evidence to separate catastrophically share one authored displacement
        # from the exact rest geometry. This is an engineering seam constraint,
        # not a muscle attachment or anatomical region. It is integrable for an
        # entire connected source component, unlike averaging incompatible
        # per-edge target vectors around a cycle.
        # Shared cluster coordinates satisfy all seam displacement equalities exactly.
        for face_index,(a,b,c) in enumerate(patch_triangles):
            p0,p1,p2=x[[a,b,c]];normal=rest_normals[face_index]
            current_normal=np.cross(p1-p0,p2-p0)
            current_area=float(normal@current_normal)
            gradients=(np.cross(p1-p2,normal),np.cross(p2-p0,normal),np.cross(normal,p1-p0))
            row=np.zeros(len(clusters)*3)
            for vertex,gradient in zip((int(a),int(b),int(c)),gradients):
                if vertex in index:
                    row[index[vertex]*3:index[vertex]*3+3]+=gradient
            if np.linalg.norm(row)>1e-18:
                rows.append(row);bounds.append(float(minimum_projected_area[face_index]-current_area))
        correction,cycles,worst,equality_error=_weighted_halfspace_projection(
            rows,bounds,equalities,equality_bounds,objective_weights,max_cycles=max_projection_cycles)
        last_projection=(cycles,worst,equality_error)
        for vertex,offset in index.items():
            x[vertex]+=correction[offset*3:offset*3+3]
        # Reapply the exact source-derived seam vector after numerical projection.
        for edge in edges:
            a,b=edge['vertices'];error=edge['desired']-(x[b]-x[a])
            x[a]-=error/2;x[b]+=error/2
        # Enforce the connected source-component displacement equalities exactly
        # after the iterative half-space solve. The solver remains responsible
        # for restoring area/contact feasibility on the next outer pass.
        for group in group_rows:
            shared_displacement=np.mean(x[group]-group_reference[group],axis=0)
            x[group]=group_reference[group]+shared_displacement
        posed_triangles=x[triangles]
        normals=np.cross(posed_triangles[:,1]-posed_triangles[:,0],posed_triangles[:,2]-posed_triangles[:,0])
        source_triangles=rest[triangles]
        source_normals=np.cross(source_triangles[:,1]-source_triangles[:,0],source_triangles[:,2]-source_triangles[:,0])
        source_area=np.linalg.norm(source_normals,axis=1);nondegenerate=source_area>=1e-12
        area=np.linalg.norm(normals,axis=1)
        flips=int((((normals*source_normals).sum(axis=1)<0)&nondegenerate).sum())
        minimum=float((area[nondegenerate]/np.maximum(source_area[nondegenerate],1e-12)).min()) if nondegenerate.any() else 1.0
        remaining=[]
        for contact_index,(key,bone,bone_triangles,baseline) in enumerate(contacts):
            fresh=np.flatnonzero(bounded_inside(x,bone,bone_triangles)&~baseline_by_contact[contact_index])
            if len(fresh):remaining.append({'boneSourceKey':key,'sourceVertexIndices':fresh.tolist()})
        edge_errors=[float(np.linalg.norm((x[row['vertices'][1]]-x[row['vertices'][0]])-row['desired'])) for row in edges]
        group_errors=[float(np.max(np.linalg.norm((x[group]-group_reference[group])-(x[group[0]]-group_reference[group[0]]),axis=1))) for group in group_rows]
        if (not remaining and flips==0 and minimum>=product_minimum_area_ratio and max(edge_errors,default=0.0)<=1e-5
                and max(group_errors,default=0.0)<=1e-9):
            break
    if (remaining or flips or minimum<product_minimum_area_ratio or max(edge_errors,default=0.0)>1e-5
            or max(group_errors,default=0.0)>1e-9):
        raise ValueError('source-topology contact patch did not satisfy source geometry constraints: '
            f'contacts={remaining[:8]}, flips={flips}, minimumAreaRatio={minimum}, edgeErrors={edge_errors}, '
            f'topologyGroupErrors={group_errors}, projection={last_projection}')
    if locked and np.max(np.linalg.norm(x[list(locked)]-original[list(locked)],axis=1))>1e-9:
        raise ValueError('source-topology patch moved an authored fixed/moving endpoint mask')
    displacement=x-original
    return x,{'method':'trunk-source-topology-contact-patch-with-interpolation-guard-v1',
        'forceContactGuard':force_contact_guard,'preservedAuthoredPatchPoseVectors':preserve_group_pose_vectors,'nativeContactSideTransport':bool(contact_rest_bones),
        'patchRings':patch_rings,'patchVertexCount':int(len(variable)),
        'independentDisplacementClusters':len(clusters),'seamEqualityElimination':True,
        'shapeSeedSourceVertexIndices':sorted(shape_seeds),
        'sourceTopologyDisplacementGroups':group_rows,
        'affectedSourceTriangleCount':int(len(patch_triangles)),'marginMetres':margin_metres,
        'shapeCorrectiveTargetRatio':shape_floor,'productMinimumAreaRatio':product_minimum_area_ratio,
        'projectionCycles':last_projection[0],
        'linearizedInequalityResidual':last_projection[1],'edgeEqualityResidualMetres':last_projection[2],
        'edgeTargets':[{'vertices':edge['vertices'],'desiredVectorMetres':edge['desired'].tolist(),
            'sourceEdgeLengthMetres':float(np.linalg.norm(rest[edge['vertices'][1]]-rest[edge['vertices'][0]])),
            'posedEdgeLengthMetres':float(np.linalg.norm(x[edge['vertices'][1]]-x[edge['vertices'][0]])),
            'vectorErrorMetres':error} for edge,error in zip(edges,edge_errors)],
        'sourceTopologyGroupDisplacementErrorMetres':group_errors,
        'correctedContactRecords':records,'maximumCorrectiveMetres':float(np.linalg.norm(displacement,axis=1).max()),
        'correctedVertexIndices':np.flatnonzero(np.linalg.norm(displacement,axis=1)>1e-10).tolist(),
        'triangleOrientationFlips':flips,'minimumSourceAreaRatio':minimum,'remainingNewContactVertices':[]}
