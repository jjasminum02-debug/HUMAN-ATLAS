#!/usr/bin/env python3
"""Explicit family/vertex authoring. Source buffers stay immutable; no anatomical measurements implied.

T59's sagittal talar arc/range verifier is deliberately not changed or reused as a universal joint.
Each input pins its own source landmarks, pose trajectory, source masks/weights and context roles.
"""
import copy, json, math, struct
from pathlib import Path
import numpy as np
from author_source_surface_motion import ROOT, RIGHTS, read, dump, source_geometry, array, normals, quat, rotation, container
from derive_source_surface_motion import accessor_bytes, geometry_hash, append_bytes, sha
from source_surface_constraints import inside
from t66_contact_correctives import (
    wrap,
    arap_wrap,
    source_bone_projection_corrective,
    source_topology_contact_patch_corrective,
)
from t66_contact_weights import (
    source_frame_contact_feasible_weights,
    source_phase_contact_feasible_weight_fields,
)

def signed_quat(matrix):
    """Preserve actual reflected source frames when glTF uses animated TRS.

    A reflection cannot be represented by a quaternion. Keep its determinant
    sign on X scale, matching Three.js Matrix4.decompose, then rotate the proper
    orthonormal matrix. This changes derived T66 assets only.
    """
    proper=matrix.copy()
    reflected=np.linalg.det(proper[:3,:3])<0
    if reflected:proper[:3,0]*=-1
    q,scale=quat(proper)
    if reflected:scale[0]*=-1
    return q,scale

def bounded_inside(points,vertices,triangles):
    result=np.zeros(len(points),dtype=bool)
    ids=np.flatnonzero(((points>=vertices.min(0)-1e-8)&(points<=vertices.max(0)+1e-8)).all(1))
    if len(ids):result[ids]=inside(points[ids],vertices,triangles)
    return result

def deform(world,pivot,axis,degrees,phase,weights,method):
    if method == 'fractional_rotation':
        # Vertex-wise quaternion-equivalent single-axis rotation avoids the volume
        # loss of linear position blending. This is authored engineering, not anatomy.
        theta=np.radians(degrees)*phase*weights
        v=world-pivot;cos=np.cos(theta)[:,None];sin=np.sin(theta)[:,None]
        return pivot+v*cos+np.cross(axis,v)*sin+(v@axis)[:,None]*axis*(1-cos)
    R=rotation(axis,math.radians(degrees)*phase)
    return world+weights[:,None]*((world-pivot)@R.T+pivot-world)

def author(payload):
    if payload['schemaVersion'] != 't66-family-surface-authoring-v1' or payload['rights'] != RIGHTS:
        raise ValueError('explicit T66 authoring/rights required')
    dataset = payload['dataset']; manifest = read(dataset['path'])
    if sha((ROOT / dataset['path']).read_bytes()) != dataset['sha256']: raise ValueError('dataset drift')
    rows = {r['sourceKey']:r for r in manifest['instances']}
    family = payload['family']; pivot = np.array(family['pivotMetres'],float)
    axis = np.array(family['axis'],float); degrees = family['endDegrees']; samples = family['samples']
    if not np.isfinite(pivot).all() or not np.isfinite(axis).all() or abs(np.linalg.norm(axis)-1)>1e-6:
        raise ValueError('finite authored pivot/unit axis required')
    if not math.isfinite(degrees) or not 0 < abs(degrees) <= family['validatedAuthoringLimitDegrees']:
        raise ValueError('family-specific explicit pose range')
    if samples < 4 or samples > 16 or not family['landmarks'] or not family['qualitativeEvidence']:
        raise ValueError('observed landmarks and qualitative source locator required')
    for landmark in family['landmarks']:
        row=rows[landmark['sourceKey']]; *_,world=source_geometry(row,landmark['lod'])
        ids=landmark['vertexIndices']
        if not ids or min(ids)<0 or max(ids)>=len(world):raise ValueError('invalid source landmark indices')
    contacts={e['sourceKey']:(e,source_geometry(rows[e['sourceKey']],e['lod'])) for e in payload['members'] if e['role'] in ['fixed_structure','moving_structure']}
    doc={'asset':{'version':'2.0','generator':'HUMAN ATLAS authored educational family v1'},'scene':0,'scenes':[{'nodes':[]}],
         'nodes':[],'meshes':[],'accessors':[],'bufferViews':[],'buffers':[{'byteLength':0}]}
    buf=bytearray();tracks=[];members=[];metrics=[];frames={};seen=set()
    def put(raw,typ,count,component=5126,minimum=None,maximum=None):
        offset,length=append_bytes(buf,raw);vi=len(doc['bufferViews']);doc['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':length})
        ai=len(doc['accessors']);a={'bufferView':vi,'componentType':component,'count':int(count),'type':typ}
        if minimum is not None:a.update(min=minimum,max=maximum)
        doc['accessors'].append(a);return ai
    for entry in payload['members']:
        key=entry['sourceKey'];row=rows[key];lod=entry['lod'];role=entry['role']
        if key in seen:raise ValueError('duplicate member')
        seen.add(key)
        if row['sourceLabelSide'] not in [payload['side'],None]:raise ValueError('wrong side member')
        src,binary,prim,pos,idx,M,world=source_geometry(row,lod);digest,n=geometry_hash(src,binary,0)
        ni=len(doc['nodes']);nodeId=f'surface_{ni}';attrs={}
        for semantic,ai in prim['attributes'].items():
            _,_,count,normalized,raw=accessor_bytes(src,binary,ai);a=src['accessors'][ai]
            out=put(raw,a['type'],count,a['componentType']);attrs[semantic]=out
            if normalized:doc['accessors'][out]['normalized']=True
            if semantic=='POSITION':doc['accessors'][out].update(min=pos.min(0).tolist(),max=pos.max(0).tolist())
        _,_,count,_,raw=accessor_bytes(src,binary,prim['indices'])
        primitive={'attributes':attrs,'indices':put(raw,'SCALAR',count,src['accessors'][prim['indices']]['componentType']),'mode':4}
        mesh={'name':row['lods'][lod]['resource'],'primitives':[primitive]}
        node={'name':nodeId,'mesh':len(doc['meshes']),'matrix':row['matrix'],'extras':{'sourceKey':key}}
        phaseFrames=[world];fixed=[];moving=[];weights=None;weightsByPhase=None;vectorCorrectives=[];contactWeightSolve=None
        if role in ['deforming_muscle_surface','deforming_passive_surface']:
            weights=np.array(entry['weights'],float);fixed=entry['fixedVertexIndices'];moving=entry['movingVertexIndices']
            if len(weights)!=n or not np.isfinite(weights).all() or weights.min()<0 or weights.max()>1 or not fixed or not moving or set(fixed)&set(moving):
                raise ValueError('explicit disjoint source masks and finite vertex weights required')
            if np.max(np.abs(weights[fixed]))>1e-9 or np.max(np.abs(weights[moving]-1))>1e-9:
                raise ValueError('mask/weight mismatch')
            # Relax only free engineering weights around very thin source tapers; retain
            # both authored masks. Failed locked triangles remain a geometry rejection.
            base=world[idx];baseN=np.cross(base[:,1]-base[:,0],base[:,2]-base[:,0]);good=np.linalg.norm(baseN,axis=1)>=1e-12
            locked=set(fixed)|set(moving)
            contactPins=[];lock0=set(fixed);lock1=set(moving)
            relevant={}
            for ck,(ce,cg) in contacts.items():
                cw=cg[-1]
                if any(world.max(0)[i]<cw.min(0)[i]-.025 or world.min(0)[i]>cw.max(0)[i]+.025 for i in range(3)):continue
                relevant[ck]=(ce,cg,bounded_inside(world,cw,cg[4]))
            edges=np.unique(np.sort(np.r_[idx[:,[0,1]],idx[:,[1,2]],idx[:,[2,0]]],axis=1),axis=0)
            ew=1/np.maximum(np.linalg.norm(world[edges[:,0]]-world[edges[:,1]],axis=1),1e-8)
            degree=np.bincount(edges.ravel(),weights=np.repeat(ew,2),minlength=n)
            # Contact pinning is a convenience for broad surfaces, not a universal
            # rule for every source topology. A small tendon-connected surface can
            # already have a continuous, source-specific blend field. Turning a
            # handful of contact-crossing vertices into binary 0/1 weights may
            # introduce a discontinuity across an authored attachment boundary.
            # In that case the input can explicitly retain its authored transition
            # field; the independent emitted-geometry and contact validators still
            # decide whether the candidate passes.
            contact_weight_policy = entry.get('contactWeightPolicy', 'auto-pin-and-relax')
            if contact_weight_policy not in ('auto-pin-and-relax', 'preserve-authored-mask-transition', 'source-frame-contact-feasible-smooth-field', 'source-phase-contact-and-shape-feasible-weight-fields'):
                raise ValueError('unknown source contact-weight policy')
            if contact_weight_policy in ('preserve-authored-mask-transition', 'source-frame-contact-feasible-smooth-field', 'source-phase-contact-and-shape-feasible-weight-fields') and not payload.get('correctContactWeights', False):
                raise ValueError('preserve-authored-mask-transition is only meaningful when family contact correction is enabled')
            if contact_weight_policy == 'source-frame-contact-feasible-smooth-field':
                contactRows=[(ck,ce['role'],cg[-1],cg[4],baseline) for ck,(ce,cg,baseline) in relevant.items()]
                weights,contactWeightSolve=source_frame_contact_feasible_weights(
                    world,idx,weights,fixed,moving,pivot,axis,degrees,samples,contactRows,
                    method=payload.get('deformationMethod','linear_blend'),
                    phase_subdivisions_per_segment=payload.get('contactFieldPhaseSubdivisions',4),
                    smoothness=payload.get('contactFieldSmoothness',0.5),
                    cache_path=(ROOT / payload['contactWeightCachePath']) if payload.get('contactWeightCachePath') else None)
            elif contact_weight_policy == 'source-phase-contact-and-shape-feasible-weight-fields':
                contactRows=[(ck,ce['role'],cg[-1],cg[4],baseline) for ck,(ce,cg,baseline) in relevant.items()]
                weightsByPhase,contactWeightSolve=source_phase_contact_feasible_weight_fields(
                    world,idx,weights,fixed,moving,pivot,axis,degrees,samples,contactRows,
                    method=payload.get('deformationMethod','linear_blend'),
                    smoothness=payload.get('contactFieldSmoothness',0.5),
                    interpolation_subdivisions=payload.get('phaseInterpolationSubdivisions',4),
                    coupled_vertex_groups=entry.get('sourceTopologyCoupledVertexGroups',()),
                    coupled_group_active_steps=entry.get('sourceTopologyCoupledActiveSteps'))
                weights=weightsByPhase[-1]
            for correctivePass in range(12 if payload.get('correctContactWeights',False) and contact_weight_policy == 'auto-pin-and-relax' else 0):
                added=False
                for ck,(ce,cg,baseline) in relevant.items():
                    isMoving=ce['role']=='moving_structure'
                    pins=set()
                    for phase in [.25,.5,.75,1]:
                        R=rotation(axis,math.radians(degrees)*phase)
                        trial=deform(world,pivot,axis,degrees,phase,weights,payload.get('deformationMethod','linear_blend'))
                        cw=(cg[-1]-pivot)@R.T+pivot if isMoving else cg[-1]
                        pins.update(np.flatnonzero(bounded_inside(trial,cw,cg[4])&~baseline).tolist())
                    # Exact authored source masks are retained; conflicts are exposed by
                    # the independent verifier rather than quietly moving an attachment.
                    pins-=lock0 if isMoving else lock1
                    fresh=pins-(lock1 if isMoving else lock0)
                    if fresh:
                        (lock1 if isMoving else lock0).update(fresh);added=True
                        contactPins.append({'boneSourceKey':ck,'weight':1 if isMoving else 0,'vertexIndices':sorted(fresh),'pass':correctivePass})
                if not added:break
                for relax in range(800):
                    sums=np.zeros(n);np.add.at(sums,edges[:,0],ew*weights[edges[:,1]]);np.add.at(sums,edges[:,1],ew*weights[edges[:,0]])
                    weights=.5*weights+.5*sums/np.maximum(degree,1);weights[list(lock0)]=0;weights[list(lock1)]=1
            locked=lock0|lock1
            corrections=[]
            for iteration in range(128):
                bad=set()
                for phase in [.25,.5,.75,1]:
                    R=rotation(axis,math.radians(degrees)*phase);trial=deform(world,pivot,axis,degrees,phase,weights,payload.get('deformationMethod','linear_blend'))
                    t=trial[idx];N=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);areas=np.linalg.norm(N,axis=1)
                    bad.update(np.flatnonzero(good&(((N*baseN).sum(1)<0)|(areas<np.linalg.norm(baseN,axis=1)*.1))).tolist())
                if not bad:break
                for ti in sorted(bad):
                    vertices=idx[ti];pins=[v for v in vertices if v in locked];value=float(np.mean(weights[pins if pins else vertices]))
                    for v in vertices:
                        if v not in locked:weights[v]=value
                corrections.append({'iteration':iteration,'triangleIds':sorted(bad)})
            normal=array(src,binary,prim['attributes']['NORMAL']);primitive['targets']=[]
            for step in range(1,samples+1):
                R=rotation(axis,math.radians(degrees)*step/samples)
                step_weights=weightsByPhase[step-1] if weightsByPhase is not None else weights
                frame=deform(world,pivot,axis,degrees,step/samples,step_weights,payload.get('deformationMethod','linear_blend'))
                if payload.get('sourceTopologyContactPatchCorrectives',False):
                    phaseContacts=[(ck,(cg[-1]-pivot)@R.T+pivot if ce['role']=='moving_structure' else cg[-1],cg[4],baseline)
                        for ck,(ce,cg,baseline) in relevant.items()]
                    edge_targets=[]
                    for edge in entry.get('sourceTopologyCoupledEdges',()):
                        a,b=map(int,edge['vertices']);source_edge=world[b]-world[a]
                        mean_weight=float(np.mean(step_weights[[a,b]]))
                        desired=source_edge+mean_weight*(R@source_edge-source_edge)
                        edge_targets.append({'vertices':[a,b],'desiredVectorMetres':desired.tolist()})
                    repair_ids=sorted(set(int(i) for i in payload.get('sourceTopologyShapeRepairTriangleIds',[])))
                    if repair_ids and (min(repair_ids)<0 or max(repair_ids)>=len(idx)):
                        raise ValueError('source-topology shape-repair triangle ID outside exact target topology')
                    shape_seeds=sorted(set(int(v) for v in idx[repair_ids].reshape(-1))) if repair_ids else []
                    frame,corrective=source_topology_contact_patch_corrective(frame,world,idx,phaseContacts,
                        set(fixed)|set(moving),edge_targets,
                        patch_rings=payload.get('sourceTopologyContactPatchRings',3),
                        margin_metres=payload.get('sourceBoneProjectionMarginMetres',.0002),
                        shape_floor=payload.get('sourceTopologyShapeFloor',.1),
                        shape_seed_vertices=shape_seeds,
                        topology_groups=entry.get('sourceTopologyCoupledVertexGroups',()))
                    vectorCorrectives.append(corrective)
                elif payload.get('sourceBoneProjectionCorrectives',False):
                    phaseContacts=[(ck,(cg[-1]-pivot)@R.T+pivot if ce['role']=='moving_structure' else cg[-1],cg[4],baseline)
                        for ck,(ce,cg,baseline) in relevant.items()]
                    frame,corrective=source_bone_projection_corrective(frame,world,idx,phaseContacts,
                        set(fixed)|set(moving),entry.get('sourceTopologyCoupledVertexGroups',()),
                        margin_metres=payload.get('sourceBoneProjectionMarginMetres',.0002))
                    vectorCorrectives.append(corrective)
                if payload.get('arapShapeCorrectives',False):
                    frame,corrective=arap_wrap(frame,world,idx,[],locked,force_shape=True)
                    vectorCorrectives.append(corrective)
                if payload.get('surfaceWrapCorrectives',False) or payload.get('arapContactCorrectives',False):
                    phaseContacts=[(ck,(cg[-1]-pivot)@R.T+pivot if ce['role']=='moving_structure' else cg[-1],cg[4],baseline)
                        for ck,(ce,cg,baseline) in relevant.items()]
                    frame,corrective=(arap_wrap if payload.get('arapContactCorrectives',False) else wrap)(frame,world,idx,phaseContacts,set(fixed)|set(moving));vectorCorrectives.append(corrective)
                local=(frame*M[3,3]-M[:3,3])@np.linalg.inv(M[:3,:3]).T;local[fixed]=pos[fixed]
                delta=(local-pos).astype('<f4');nd=(normals(local,idx)-normal).astype('<f4')
                primitive['targets'].append({'POSITION':put(delta.tobytes(),'VEC3',n,minimum=delta.min(0).tolist(),maximum=delta.max(0).tolist()),'NORMAL':put(nd.tobytes(),'VEC3',n)})
                phaseFrames.append(frame)
            mesh['weights']=[0]*samples;node['weights']=[0]*samples
            values=[0.]*(samples*(samples+1))
            for step in range(1,samples+1):values[step*samples+step-1]=1
            tracks.append((ni,'weights',values,'SCALAR'))
        elif role in ['moving_structure','co_moving_context']:
            node.pop('matrix');q,sc=signed_quat(M);node.update(translation=M[:3,3].tolist(),rotation=q,scale=sc)
            ts=[];qs=[]
            for step in range(samples+1):
                R=rotation(axis,math.radians(degrees)*step/samples);MM=M.copy();MM[:3,:3]=R@M[:3,:3];MM[:3,3]=(M[:3,3]-pivot)@R.T+pivot
                ts.extend(MM[:3,3].tolist());qs.extend(signed_quat(MM)[0])
                if step:phaseFrames.append((world-pivot)@R.T+pivot)
            tracks.extend([(ni,'translation',ts,'VEC3'),(ni,'rotation',qs,'VEC4')])
        elif role not in ['fixed_structure','passive_context']:raise ValueError('unknown role')
        else:phaseFrames=[world]*(samples+1)
        # Include interpolated middle samples; relative normal test against local trajectory,
        # not a fixed world normal which would falsely classify a rotating rigid bone as folded.
        tri=world[idx];baseNormal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);baseArea=np.linalg.norm(baseNormal,axis=1);nondeg=baseArea>=1e-12
        keyFlips=0;keyMinimumAreaRatio=1.;interpolationFlips=0;interpolationMinimumAreaRatio=1.;maxEdgeRatio=0.
        edges=np.unique(np.sort(np.r_[idx[:,[0,1]],idx[:,[1,2]],idx[:,[2,0]]],axis=1),axis=0)
        baseLength=np.linalg.norm(world[edges[:,0]]-world[edges[:,1]],axis=1)
        # Exact authored keys and the interpolation between those keys are
        # reported independently. A candidate may be emitted only for a
        # mandatory downstream GLB repair pass; interpolation failures never
        # count as acceptance and remain subject to the unchanged strict GLB
        # verifier after resampling/correctives.
        for frame in phaseFrames:
            t=frame[idx];normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);area=np.linalg.norm(normal,axis=1)
            keyFlips+=int(((normal*baseNormal).sum(1)[nondeg]<0).sum())
            if nondeg.any():keyMinimumAreaRatio=min(keyMinimumAreaRatio,float((area[nondeg]/baseArea[nondeg]).min()))
        for a,b in zip(phaseFrames[:-1],phaseFrames[1:]):
            for f in [.25,.5,.75]:
                frame=a*(1-f)+b*f;t=frame[idx];normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);area=np.linalg.norm(normal,axis=1)
                interpolationFlips+=int(((normal*baseNormal).sum(1)[nondeg]<0).sum())
                if nondeg.any():interpolationMinimumAreaRatio=min(interpolationMinimumAreaRatio,float((area[nondeg]/baseArea[nondeg]).min()))
                ratio=np.linalg.norm(frame[edges[:,0]]-frame[edges[:,1]],axis=1)/np.maximum(baseLength,1e-12)
                maxEdgeRatio=max(maxEdgeRatio,float(np.max(abs(ratio-1))))
                if not np.isfinite(frame).all():raise ValueError('nonfinite geometry')
        if keyFlips or keyMinimumAreaRatio<.1:raise ValueError(f'folded/collapsed authored key geometry {key}: {keyFlips}/{keyMinimumAreaRatio}')
        interpolation_repair_needed=bool(interpolationFlips or interpolationMinimumAreaRatio<.1)
        if interpolation_repair_needed and not payload.get('candidateOnlyForMandatoryGlbInterpolationRepair',False):
            raise ValueError(f'folded/collapsed authored interpolation {key}: {interpolationFlips}/{interpolationMinimumAreaRatio}')
        metrics.append({'sourceKey':key,'role':role,'vertices':n,'triangles':len(idx),'flips':keyFlips,'minimumAreaRatio':keyMinimumAreaRatio,
            'preRefinementInterpolationFlips':interpolationFlips,
            'preRefinementInterpolationMinimumAreaRatio':interpolationMinimumAreaRatio,
            'requiresMandatoryGlbInterpolationRepair':interpolation_repair_needed,
            'maximumRelativeEdgeChange':maxEdgeRatio,'maximumDisplacementMetres':float(np.linalg.norm(phaseFrames[-1]-world,axis=1).max()),
            'sourceDegenerateTriangles':int((~nondeg).sum()),'fixedMaskCount':len(fixed),'movingMaskCount':len(moving),
            'weightCorrections':corrections if weights is not None else [],'fixedMaskErrorMetres':float(np.linalg.norm(phaseFrames[-1][fixed]-world[fixed],axis=1).max()) if fixed else None})
        if weights is not None:
            metrics[-1].update(authoredFinalWeights=weights.tolist(),contactPins=contactPins,vectorCorrectives=vectorCorrectives,
                contactWeightPolicy=entry.get('contactWeightPolicy', 'auto-pin-and-relax'),
                authoredWeightFieldSha256=sha(np.asarray(entry['weights'],dtype='<f8').tobytes()),
                finalWeightFieldSha256=sha(np.asarray(weightsByPhase if weightsByPhase is not None else weights,dtype='<f8').tobytes()),
                contactWeightSolve=contactWeightSolve)
            if weightsByPhase is not None:
                metrics[-1]['authoredFinalWeightsByPhase']=[field.tolist() for field in weightsByPhase]
        frames[key]=(phaseFrames,idx);members.append({'sourceKey':key,'nodeId':nodeId,'sourceNamespace':manifest['namespace'],'role':role,
            'side':row['sourceLabelSide'],'resourceKey':row['lods'][lod]['resource'],'lod':lod,'sourceChunkSha256':row['lods'][lod]['chunk'],
            'geometrySha256':digest,'instanceMatrix':row['matrix']})
        doc['nodes'].append(node);doc['meshes'].append(mesh);doc['scenes'][0]['nodes'].append(ni)
    rest=container(doc,buf)
    times=np.linspace(0,family['durationSeconds'],samples+1).astype('<f4');ta=put(times.tobytes(),'SCALAR',len(times),minimum=[0],maximum=[family['durationSeconds']])
    samplers=[];channels=[]
    for ni,path,values,typ in tracks:
        ai=put(np.array(values,dtype='<f4').tobytes(),typ,len(values)//{'SCALAR':1,'VEC3':3,'VEC4':4}[typ]);channels.append({'sampler':len(samplers),'target':{'node':ni,'path':path}});samplers.append({'input':ta,'output':ai,'interpolation':'LINEAR'})
    doc['animations']=[{'name':payload['clipId'],'samplers':samplers,'channels':channels}];motion=container(doc,buf)
    record={'schemaVersion':'t66-authored-family-record-v1','id':payload['id'],'family':family,'rights':RIGHTS,'inputSha256':sha(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()),
        'members':members,'surfaceMetrics':metrics,'restSha256':sha(rest),'motionSha256':sha(motion),'motionBytes':len(motion),
        'sourceGeometryModified':False,'measuredAnatomicalAxis':False,'measuredAttachmentFootprints':False,'physiologicalROM':False,
        'validationLimitations':['Vertex masks and kinematics are authored educational approximations, not source measured attachment footprints.',
            'Intermediate discrete area/orientation checks do not prove continuous collision freedom. Context containment review is separate before registration.']}
    return rest,motion,record,frames

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output-directory',required=True);args=p.parse_args()
    payload=json.loads(Path(args.input).read_text());rest,motion,record,_=author(payload);out=Path(args.output_directory);out.mkdir(parents=True,exist_ok=True)
    (out/'reference.glb').write_bytes(rest);(out/'motion.glb').write_bytes(motion);(out/'authoring-record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':'authored_candidate','bytes':len(motion),'sha256':sha(motion)}))
