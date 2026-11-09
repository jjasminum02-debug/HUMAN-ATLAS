"""Authored surface wrapping against actual pinned source triangles, no new anatomy."""
from collections import deque
import numpy as np
from source_surface_constraints import inside

def bounded_inside(points,vertices,triangles):
    result=np.zeros(len(points),dtype=bool)
    ids=np.flatnonzero(((points>=vertices.min(0)-1e-8)&(points<=vertices.max(0)+1e-8)).all(1))
    if len(ids):result[ids]=inside(points[ids],vertices,triangles)
    return result

def nearest_surface_details(points,vertices,triangles):
    tri=vertices[triangles];a,b,c=tri[:,0],tri[:,1],tri[:,2];ab=b-a;ac=c-a
    normal=np.cross(ab,ac);nn=(normal*normal).sum(1)
    out=[];face_ids=[]
    for p in points:
        projection=p-normal*((normal*(p-a)).sum(1)/np.maximum(nn,1e-30))[:,None]
        ap=projection-a;d00=(ab*ab).sum(1);d01=(ab*ac).sum(1);d11=(ac*ac).sum(1)
        d20=(ap*ab).sum(1);d21=(ap*ac).sum(1);den=d00*d11-d01*d01
        v=(d11*d20-d01*d21)/np.maximum(den,1e-30);w=(d00*d21-d01*d20)/np.maximum(den,1e-30)
        candidates=[projection];valid=(v>=0)&(w>=0)&(v+w<=1)&(nn>1e-25)
        distances=[np.where(valid,((projection-p)**2).sum(1),np.inf)]
        for start,end in [(a,b),(b,c),(c,a)]:
            edge=end-start;t=np.clip(((p-start)*edge).sum(1)/np.maximum((edge*edge).sum(1),1e-30),0,1)
            q=start+t[:,None]*edge;candidates.append(q);distances.append(((q-p)**2).sum(1))
        distances=np.stack(distances);ci,ti=np.unravel_index(np.argmin(distances),distances.shape);out.append(candidates[ci][ti]);face_ids.append(ti)
    return np.array(out),np.asarray(face_ids,dtype=np.int64)

def nearest_surface(points,vertices,triangles):
    return nearest_surface_details(points,vertices,triangles)[0]

def outward_surface_direction(point,surface_point,vertices,triangles,face_index):
    """Use the exact source-face normal only to disambiguate a zero-distance contact."""
    delta=surface_point-point;length=float(np.linalg.norm(delta))
    if length>1e-8:return delta/length,length
    face=vertices[triangles[int(face_index)]]
    normal=np.cross(face[1]-face[0],face[2]-face[0]);norm=float(np.linalg.norm(normal))
    if norm<1e-15:raise ValueError('nearest contact source triangle has no stable geometric normal')
    normal/=norm
    for epsilon in (1e-6,1e-5,1e-4,1e-3):
        plus=bool(inside((surface_point+normal*epsilon)[None,:],vertices,triangles)[0])
        minus=bool(inside((surface_point-normal*epsilon)[None,:],vertices,triangles)[0])
        if plus!=minus:return (normal if minus else -normal),length
    raise ValueError('source-surface outward side is ambiguous at a zero-distance contact')

def wrap(frame,rest,idx,contacts,locked):
    original=frame.copy();correction=np.zeros_like(frame);pins={};records=[]
    edges=np.unique(np.sort(np.r_[idx[:,[0,1]],idx[:,[1,2]],idx[:,[2,0]]],axis=1),axis=0)
    weights=1/np.maximum(np.linalg.norm(rest[edges[:,0]]-rest[edges[:,1]],axis=1),1e-8)
    degree=np.bincount(edges.ravel(),weights=np.repeat(weights,2),minlength=len(frame))
    for iteration in range(12):
        added=False
        for key,bone,tri,baseline in contacts:
            fresh=np.flatnonzero(bounded_inside(frame,bone,tri)&~baseline)
            free=np.array([v for v in fresh if int(v) not in locked],dtype=int)
            if not len(free):continue
            q=nearest_surface(frame[free],bone,tri);direction=q-frame[free];length=np.linalg.norm(direction,axis=1)
            q+=direction/np.maximum(length,1e-15)[:,None]*.00015
            for v,target in zip(free,q):pins[int(v)]=target-original[v]
            records.append({'sourceKey':key,'iteration':iteration,'vertexIndices':free.tolist(),'maximumPushMetres':float(length.max())});added=True
        if not added:break
        for v,value in pins.items():correction[v]=value
        for relax in range(400):
            sums=np.zeros_like(correction)
            np.add.at(sums,edges[:,0],weights[:,None]*correction[edges[:,1]]);np.add.at(sums,edges[:,1],weights[:,None]*correction[edges[:,0]])
            correction=.5*correction+.5*sums/np.maximum(degree,1)[:,None]
            for v,value in pins.items():correction[v]=value
            correction[list(locked)]=0
        frame=original+correction
    return frame,{'contactPushes':records,'maximumCorrectiveMetres':float(np.linalg.norm(correction,axis=1).max()),'correctiveVectors':correction.tolist()}

def arap_wrap(frame,rest,idx,contacts,locked,force_shape=False):
    """Local rest-edge-preserving corrective with exact authored endpoint constraints.

    Contact targets derive only from actual source triangles. The independent
    orientation/area and source-containment verifier still decides acceptance.
    """
    edges=np.unique(np.sort(np.r_[idx[:,[0,1]],idx[:,[1,2]],idx[:,[2,0]]],axis=1),axis=0)
    i,j=edges.T;d=rest[i]-rest[j];w=1/np.maximum(np.linalg.norm(d,axis=1),1e-8)
    degree=np.bincount(edges.ravel(),weights=np.repeat(w,2),minlength=len(rest))
    original=frame.copy();x=frame.copy();pins={int(v):frame[v].copy() for v in locked};records=[]
    for contactPass in range(8):
        for key,bone,tri,baseline in contacts:
            fresh=np.flatnonzero(bounded_inside(x,bone,tri)&~baseline)
            free=np.array([v for v in fresh if int(v) not in locked],dtype=int)
            if not len(free):continue
            q=nearest_surface(x[free],bone,tri);direction=q-x[free];length=np.linalg.norm(direction,axis=1)
            q+=direction/np.maximum(length,1e-15)[:,None]*.00015
            for v,target in zip(free,q):pins[int(v)]=target
            records.append({'sourceKey':key,'pass':contactPass,'vertexIndices':free.tolist(),'maximumPushMetres':float(length.max())})
        if not records and not force_shape:break
        for iteration in range(300 if force_shape else 100):
            current=x[i]-x[j];cov=np.zeros((len(x),3,3));outer=w[:,None,None]*current[:,:,None]*d[:,None,:]
            np.add.at(cov,i,outer);np.add.at(cov,j,outer)
            u,_,vt=np.linalg.svd(cov);rot=u@vt;bad=np.linalg.det(rot)<0;u[bad,:,-1]*=-1;rot=u@vt
            desired=np.einsum('nij,nj->ni',(rot[i]+rot[j])*.5,d)
            sums=np.zeros_like(x);np.add.at(sums,i,w[:,None]*(x[j]+desired));np.add.at(sums,j,w[:,None]*(x[i]-desired))
            target=sums/np.maximum(degree,1)[:,None]
            x=.5*x+.5*(.98*target+.02*original)
            for v,value in pins.items():x[v]=value
        if force_shape and not contacts:break
    return x,{'contactPushes':records,'correctiveVectors':(x-original).tolist(),'maximumCorrectiveMetres':float(np.linalg.norm(x-original,axis=1).max()),'method':'authored_rest_edge_arap_not_measured_physiology'}

def source_bone_projection_corrective(frame,rest,triangles,contacts,locked,topology_groups=(),margin_metres=.0002):
    """Project new bone-contained source vertices through their nearest source surface.

    This is a deterministic local contact repair, not a measured attachment or
    anatomical normal. Near-zero source-topology groups translate together so a
    source-linked seam does not split while one member is moved clear of a bone.
    """
    original=np.asarray(frame,dtype=float).copy();x=original.copy();rest=np.asarray(rest,dtype=float)
    triangles=np.asarray(triangles,dtype=np.int64);locked=set(map(int,locked))
    if margin_metres<=0:raise ValueError('positive numerical source-surface clearance required')
    group_rows=[sorted(set(map(int,g))) for g in topology_groups if len(set(map(int,g)))>1]
    group_by_vertex={}
    for group_index,group in enumerate(group_rows):
        if min(group)<0 or max(group)>=len(x):raise ValueError('source-topology corrective group index outside target mesh')
        if set(group)&locked:raise ValueError('source-topology corrective group overlaps fixed/moving endpoint mask')
        for vertex in group:
            if vertex in group_by_vertex:raise ValueError('overlapping source-topology corrective groups')
            group_by_vertex[vertex]=group_index
    base=rest[triangles];base_n=np.cross(base[:,1]-base[:,0],base[:,2]-base[:,0]);base_a=np.linalg.norm(base_n,axis=1);nondeg=base_a>=1e-12
    records=[]
    for iteration in range(12):
        proposals={}; blockers=[]
        for key,bone,bone_triangles,baseline in contacts:
            fresh=np.flatnonzero(bounded_inside(x,bone,bone_triangles)&~np.asarray(baseline,dtype=bool))
            if not len(fresh):continue
            locked_hits=[int(v) for v in fresh if int(v) in locked]
            if locked_hits:
                blockers.append({'boneSourceKey':key,'lockedSourceVertexIndices':locked_hits});continue
            q=nearest_surface(x[fresh],bone,bone_triangles);direction=q-x[fresh];length=np.linalg.norm(direction,axis=1)
            unit=direction/np.maximum(length,1e-15)[:,None]
            for vertex,vector,dist in zip(fresh,unit,length):
                group_index=group_by_vertex.get(int(vertex))
                delta=vector*(float(dist)+margin_metres)
                token=('group',group_index) if group_index is not None else ('vertex',int(vertex))
                proposals.setdefault(token,[]).append({'boneSourceKey':key,'vertexIndex':int(vertex),'delta':delta})
        if blockers:
            raise ValueError(f'source bone collision intersects authored fixed/moving endpoint masks: {blockers[:8]}')
        if not proposals:
            break
        before=x.copy();pending=np.zeros_like(x)
        for token,items in proposals.items():
            delta=np.mean([item['delta'] for item in items],axis=0)
            vertex_ids=group_rows[token[1]] if token[0]=='group' else [token[1]]
            for vertex in vertex_ids:pending[vertex]+=delta
            records.append({'iteration':iteration,'kind':'topology_group_translation' if token[0]=='group' else 'single_vertex_projection',
                'groupIndex':token[1] if token[0]=='group' else None,'sourceVertexIndices':vertex_ids,
                'contactSamples':[{'boneSourceKey':item['boneSourceKey'],'vertexIndex':item['vertexIndex']} for item in items],
                'requestedDeltaMetres':delta.tolist()})
        chosen=None
        for scale in (1.0,1.25,1.5,2.0,0.75,0.5):
            candidate=before+pending*scale
            posed=candidate[triangles];n=np.cross(posed[:,1]-posed[:,0],posed[:,2]-posed[:,0]);area=np.linalg.norm(n,axis=1)
            bad=int((((n*base_n).sum(1)<0)&nondeg).sum())
            minimum=float((area[nondeg]/np.maximum(base_a[nondeg],1e-12)).min()) if nondeg.any() else 1.0
            after_count=sum(int((bounded_inside(candidate,bone,bt)&~np.asarray(baseline,dtype=bool)).sum()) for _,bone,bt,baseline in contacts)
            before_count=sum(int((bounded_inside(before,bone,bt)&~np.asarray(baseline,dtype=bool)).sum()) for _,bone,bt,baseline in contacts)
            if bad==0 and minimum>=.1 and after_count<before_count:
                chosen=(candidate,scale,after_count,bad,minimum);break
        if chosen is None:
            raise ValueError('source-bone projection corrective cannot clear contact while retaining source triangle orientation/10% area')
        x=chosen[0]
        records[-1]['acceptedScale']=chosen[1]
        records[-1]['remainingNewContainedVertexCount']=chosen[2]
        records[-1]['triangleOrientationFlips']=chosen[3]
        records[-1]['minimumSourceAreaRatio']=chosen[4]
    remaining=[]
    for key,bone,bone_triangles,baseline in contacts:
        fresh=np.flatnonzero(bounded_inside(x,bone,bone_triangles)&~np.asarray(baseline,dtype=bool))
        if len(fresh):remaining.append({'boneSourceKey':key,'sourceVertexIndices':fresh.tolist()})
    if remaining:raise ValueError(f'source-bone projection corrective did not converge: {remaining[:8]}')
    posed=x[triangles];n=np.cross(posed[:,1]-posed[:,0],posed[:,2]-posed[:,0]);area=np.linalg.norm(n,axis=1)
    flips=int((((n*base_n).sum(1)<0)&nondeg).sum())
    minimum=float((area[nondeg]/np.maximum(base_a[nondeg],1e-12)).min()) if nondeg.any() else 1.0
    if flips or minimum<.1:raise ValueError(f'source-bone projection geometry rejected: flips={flips}, minimumAreaRatio={minimum}')
    if locked and np.max(np.linalg.norm(x[list(locked)]-original[list(locked)],axis=1))>1e-9:
        raise ValueError('source-bone corrective moved an authored endpoint mask')
    corrective=x-original
    return x,{'method':'nearest-pinned-source-bone-surface-projection-with-source-topology-group-translation',
        'marginMetres':margin_metres,'contactCorrectiveRecords':records,'topologyGroups':group_rows,
        'correctedVertexIndices':np.flatnonzero(np.linalg.norm(corrective,axis=1)>1e-10).tolist(),
        'maximumCorrectiveMetres':float(np.linalg.norm(corrective,axis=1).max()),
        'triangleOrientationFlips':flips,'minimumSourceAreaRatio':minimum,'remainingNewContactVertices':[]}


def _weighted_halfspace_projection(A,b,E,e,weights,max_cycles=5000,tolerance=1e-9):
    """Minimum weighted-norm correction satisfying linearized geometry bounds."""
    A=np.asarray(A,dtype=float).reshape((-1,len(weights)))
    b=np.asarray(b,dtype=float)
    E=np.asarray(E,dtype=float).reshape((-1,len(weights)))
    e=np.asarray(e,dtype=float)
    inverse=1/np.asarray(weights,dtype=float)
    x=np.zeros(len(weights)); inequality_correction=np.zeros_like(A); equality_correction=np.zeros_like(E)
    inequality_norm=np.sum(A*A*inverse[None,:],axis=1) if len(A) else np.empty(0)
    equality_norm=np.sum(E*E*inverse[None,:],axis=1) if len(E) else np.empty(0)
    for cycle in range(max_cycles):
        for index,row in enumerate(E):
            y=x+equality_correction[index]
            error=e[index]-float(row@y)
            projected=y+(error/max(equality_norm[index],1e-30))*inverse*row
            equality_correction[index]=y-projected
            x=projected
        worst=0.0
        for index,row in enumerate(A):
            y=x+inequality_correction[index]
            violation=b[index]-float(row@y)
            if violation>0:
                projected=y+(violation/max(inequality_norm[index],1e-30))*inverse*row
            else:
                projected=y
            inequality_correction[index]=y-projected
            x=projected
            worst=max(worst,max(0.0,float(b[index]-row@x)))
        equality_error=float(np.max(np.abs(E@x-e))) if len(E) else 0.0
        if worst<tolerance and equality_error<tolerance:
            return x,cycle+1,worst,equality_error
    return x,max_cycles,worst,equality_error


def source_topology_contact_patch_corrective(frame,rest,triangles,contacts,locked,edge_targets,
        patch_rings=3,margin_metres=.0002,contact_guard_metres=.01,shape_floor=.1,
        max_outer_iterations=8,max_projection_cycles=5000,shape_seed_vertices=(),topology_groups=()):
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
    no_op_group_errors=[float(np.max(np.linalg.norm((x[group]-rest[group])-
        (x[group[0]]-rest[group[0]]),axis=1))) for group in group_rows]
    if (not no_op_contacts and no_op_flips==0 and no_op_minimum>=shape_floor
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
    index={int(vertex):offset for offset,vertex in enumerate(variable)}
    if not seeds.issubset(index):
        raise ValueError('source-topology contact edge intersects fixed or out-of-patch vertices')
    affected=np.flatnonzero(np.isin(triangles,variable).any(axis=1));patch_triangles=triangles[affected]
    rest_triangles=rest[patch_triangles]
    rest_normals=np.cross(rest_triangles[:,1]-rest_triangles[:,0],rest_triangles[:,2]-rest_triangles[:,0])
    rest_areas=np.linalg.norm(rest_normals,axis=1);nondegenerate=rest_areas>=1e-12
    patch_triangles=patch_triangles[nondegenerate];rest_normals=rest_normals[nondegenerate]
    minimum_projected_area=shape_floor*np.sum(rest_normals*rest_normals,axis=1)
    objective_weights=np.repeat(np.asarray([1+.25*distance[int(vertex)] for vertex in variable]),3)
    baseline_by_contact=[np.asarray(contact[3],dtype=bool) for contact in contacts]
    records=[];last_projection=(0,0.0,0.0);remaining=[]
    for outer in range(max_outer_iterations):
        rows=[];bounds=[];equalities=[];equality_bounds=[]
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
                    if distance>contact_guard_metres:continue
                    if distance>1e-8:
                        unit=(q-x[vertex])/distance if is_inside else (x[vertex]-q)/distance
                    else:
                        unit,_=outward_surface_direction(x[vertex],q,bone,bone_triangles,face_index)
                    signed=-float(distance) if is_inside else float(distance)
                    row=np.zeros(len(variable)*3);offset=index[int(vertex)]*3
                    row[offset:offset+3]=unit
                    rows.append(row);bounds.append(float(margin_metres-signed))
                    records.append({'outerIteration':outer+1,'kind':'bone_surface_nonpenetration_guard',
                        'boneSourceKey':key,'sourceVertexIndex':int(vertex),
                        'insideAtSolve':bool(is_inside),'signedDistanceMetres':signed,
                        'guardDistanceMetres':contact_guard_metres})
        for edge in edges:
            a,b=edge['vertices'];desired=edge['desired'];current=x[b]-x[a]
            for component in range(3):
                row=np.zeros(len(variable)*3)
                row[index[b]*3+component]=1;row[index[a]*3+component]=-1
                equalities.append(row);equality_bounds.append(float(desired[component]-current[component]))
        # Near-coincident source vertices that were shown by emitted-GLB
        # evidence to separate catastrophically share one authored displacement
        # from the exact rest geometry. This is an engineering seam constraint,
        # not a muscle attachment or anatomical region. It is integrable for an
        # entire connected source component, unlike averaging incompatible
        # per-edge target vectors around a cycle.
        for group in group_rows:
            anchor=group[0]
            for vertex in group[1:]:
                desired=rest[vertex]-rest[anchor]-(x[vertex]-x[anchor])
                for component in range(3):
                    row=np.zeros(len(variable)*3)
                    row[index[vertex]*3+component]=1
                    row[index[anchor]*3+component]=-1
                    equalities.append(row);equality_bounds.append(float(desired[component]))
        for face_index,(a,b,c) in enumerate(patch_triangles):
            p0,p1,p2=x[[a,b,c]];normal=rest_normals[face_index]
            current_normal=np.cross(p1-p0,p2-p0)
            current_area=float(normal@current_normal)
            gradients=(np.cross(p1-p2,normal),np.cross(p2-p0,normal),np.cross(normal,p1-p0))
            row=np.zeros(len(variable)*3)
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
            shared_displacement=np.mean(x[group]-rest[group],axis=0)
            x[group]=rest[group]+shared_displacement
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
        group_errors=[float(np.max(np.linalg.norm((x[group]-rest[group])-(x[group[0]]-rest[group[0]]),axis=1))) for group in group_rows]
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
    return x,{'method':'source-topology-local-minimum-displacement-contact-patch-v1',
        'patchRings':patch_rings,'patchVertexCount':int(len(variable)),
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
