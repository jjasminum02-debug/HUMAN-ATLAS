#!/usr/bin/env python3
"""Author a source-local surface morph and rigid context from explicit pinned vertex regions.

No anatomical regions are inferred here. Input regions and roles are authored selections supported
by a separately retained anatomical/geometry inspection record. This is educational kinematics,
not measured contraction, a physiological simulator, an upstream bind pose, or human approval.
Requires numpy (bundled workspace Python). Original source buffers are read only.
"""
from __future__ import annotations
import argparse, copy, json, math, struct
from pathlib import Path
import numpy as np
from derive_source_surface_motion import load_glb, accessor_bytes, geometry_hash, append_bytes, sha
ROOT=Path(__file__).resolve().parents[2]
RIGHTS={'sourceOnly':True,'localUseRights':'inherits_pinned_source_decision','publicRedistribution':'held','humanReview':'not_performed'}

def read(path): return json.loads((ROOT/path).read_text())
def dump(path,value):
    path=ROOT/path;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def array(doc,binary,index):
    name,size,count,normalized,raw=accessor_bytes(doc,binary,index)
    dtype={'Float32Array':'<f4','Uint16Array':'<u2','Uint32Array':'<u4'}[name]
    return np.frombuffer(raw,dtype=dtype).reshape(count,size).copy()
def source_geometry(row,lod):
    res=row['lods'][lod]['resource'];path=ROOT/f'atlas-data/source-cache/datasets/za/resources/{res}.glb'
    if sha(path.read_bytes())!=res: raise ValueError('immutable source resource hash drift')
    doc,binary=load_glb(path);primitive=doc['meshes'][0]['primitives'][0]
    pos=array(doc,binary,primitive['attributes']['POSITION']);idx=array(doc,binary,primitive['indices']).reshape(-1,3)
    matrix=np.array(row['matrix']).reshape(4,4).T
    world=(pos@matrix[:3,:3].T+matrix[:3,3])/matrix[3,3]
    return doc,binary,primitive,pos,idx,matrix,world

def normals(pos,idx):
    normal=np.zeros_like(pos,dtype=np.float64);tri=pos[idx]
    face=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
    for corner in range(3):np.add.at(normal,idx[:,corner],face)
    length=np.linalg.norm(normal,axis=1);normal/=np.maximum(length,1e-15)[:,None]
    return normal.astype('<f4')
def quat(matrix):
    # Stable matrix -> quaternion; no axis/name inference.
    r=matrix[:3,:3];scale=np.linalg.norm(r,axis=0);r=r/scale
    K=np.array([[r[0,0]-r[1,1]-r[2,2],r[1,0]+r[0,1],r[2,0]+r[0,2],r[2,1]-r[1,2]],
                [r[1,0]+r[0,1],r[1,1]-r[0,0]-r[2,2],r[2,1]+r[1,2],r[0,2]-r[2,0]],
                [r[2,0]+r[0,2],r[2,1]+r[1,2],r[2,2]-r[0,0]-r[1,1],r[1,0]-r[0,1]],
                [r[2,1]-r[1,2],r[0,2]-r[2,0],r[1,0]-r[0,1],r[0,0]+r[1,1]+r[2,2]]])/3
    val,v=np.linalg.eigh(K);q=v[:,np.argmax(val)];return (q if q[3]>=0 else -q).tolist(),scale.tolist()
def rotation(axis,angle):
    axis=np.array(axis,dtype=float);axis/=np.linalg.norm(axis);x,y,z=axis;c=math.cos(angle);s=math.sin(angle);C=1-c
    return np.array([[c+x*x*C,x*y*C-z*s,x*z*C+y*s],[y*x*C+z*s,c+y*y*C,y*z*C-x*s],[z*x*C-y*s,z*y*C+x*s,c+z*z*C]])
def container(doc,binary):
    doc=copy.deepcopy(doc);doc['buffers']=[{'byteLength':len(binary)}]
    j=json.dumps(doc,separators=(',',':'),allow_nan=False).encode();j+=b' '*((-len(j))%4)
    b=bytes(binary)+b'\0'*((-len(binary))%4);total=12+8+len(j)+8+len(b)
    return struct.pack('<III',0x46546c67,2,total)+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(b),0x004e4942)+b

def author(payload):
    if payload['schemaVersion']!='t59-source-surface-authoring-v1' or payload['rights']!=RIGHTS or payload.get('fixtureOnly'):
        raise ValueError('source-only authoring contract/rights required')
    manifest=read(payload['dataset']['path'])
    if sha((ROOT/payload['dataset']['path']).read_bytes())!=payload['dataset']['sha256']:raise ValueError('dataset snapshot drift')
    rows={r['sourceKey']:r for r in manifest['instances']};subject=payload['subjectSourceKey']
    if subject not in rows or rows[subject]['sourceLabelSide']!=payload['side']:raise ValueError('subject side/source mismatch')
    landmark=payload['joint']['landmark'];lr=rows[landmark['sourceKey']]
    if lr['sourceLabelSide']!=payload['side']:raise ValueError('landmark side mismatch')
    *_,world=source_geometry(lr,landmark['lod']);region=world[landmark['vertexIndices']]
    # Fit the inspected talar sagittal dome arc. This is an authoring hinge approximation, not
    # the anatomical instantaneous helical axis; transverse direction explicitly authored.
    yz=region[:,[1,2]];A=np.c_[2*yz,np.ones(len(yz))];b=(yz*yz).sum(axis=1)
    sol,_,rank,_=np.linalg.lstsq(A,b,rcond=None)
    if rank!=3:raise ValueError('insufficient landmark arc for reproducible pivot fit')
    pivot=np.array([region[:,0].mean(),sol[0],sol[1]])
    radius=math.sqrt(float(sol[2]+sol[0]**2+sol[1]**2));residual=float(np.sqrt(np.mean((np.linalg.norm(yz-sol[:2],axis=1)-radius)**2)))
    angle=payload['joint']['angleRadians'];axis=payload['joint']['axis'];R=rotation(axis,angle)
    if not (0<abs(angle)<=math.radians(10)):raise ValueError('authoring range must be explicit, finite, conservative <=10 degrees')
    doc={'asset':{'version':'2.0','generator':'HUMAN ATLAS T59 source-surface authoring'},'scene':0,'scenes':[{'nodes':[]}],
         'nodes':[],'meshes':[],'accessors':[],'bufferViews':[],'buffers':[{'byteLength':0}]};buf=bytearray();members=[];metrics=[]
    tracks=[]
    def put(raw,type,count,component=5126,minimum=None,maximum=None):
        offset,length=append_bytes(buf,raw);vi=len(doc['bufferViews']);doc['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':length})
        ai=len(doc['accessors']);a={'bufferView':vi,'componentType':component,'count':int(count),'type':type}
        if minimum is not None:a.update(min=minimum,max=maximum)
        doc['accessors'].append(a);return ai
    seen=set()
    for entry in payload['members']:
        key=entry['sourceKey'];row=rows[key];lod=entry['lod'];role=entry['role']
        if key in seen or row['sourceLabelSide']!=payload['side']:raise ValueError('duplicate or wrong-side context')
        seen.add(key);src,binary,prim,pos,idx,M,world=source_geometry(row,lod);digest,n=geometry_hash(src,binary,0)
        ni=len(doc['nodes']);mi=len(doc['meshes']);nodeId=f'surface_{ni}'
        attrs={}
        for semantic,aidx in prim['attributes'].items():
            arr,size,count,normalized,raw=accessor_bytes(src,binary,aidx);component=src['accessors'][aidx]['componentType']
            ai=put(raw,src['accessors'][aidx]['type'],count,component)
            if normalized:doc['accessors'][ai]['normalized']=True
            if semantic=='POSITION':doc['accessors'][ai].update(min=pos.min(axis=0).tolist(),max=pos.max(axis=0).tolist())
            attrs[semantic]=ai
        arr,size,count,_,raw=accessor_bytes(src,binary,prim['indices']);indices=put(raw,'SCALAR',count,src['accessors'][prim['indices']]['componentType'])
        primitive={'attributes':attrs,'indices':indices,'mode':4};mesh={'name':row['lods'][lod]['resource'],'primitives':[primitive]}
        node={'name':nodeId,'mesh':mi,'matrix':row['matrix'],'extras':{'sourceKey':key}}
        end=world.copy();fixedIds=entry.get('fixedVertexIndices',[]);movingIds=entry.get('movingVertexIndices',[])
        if role in ('deforming_muscle_surface','deforming_passive_surface'):
            if not fixedIds or not movingIds or set(fixedIds)&set(movingIds):raise ValueError('explicit disjoint fixed/moving source vertex regions required')
            # Smooth displacement field constrained by authored distal/proximal masks; rest untouched.
            lower=entry['transitionMetres'][0];upper=entry['transitionMetres'][1]
            w=np.clip((upper-world[:,1])/(upper-lower),0,1);w=w*w*(3-2*w)
            w[fixedIds]=0;w[movingIds]=1
            end=world+w[:,None]*((world-pivot)@R.T+pivot-world)
            local=(end*M[3,3]-M[:3,3])@np.linalg.inv(M[:3,:3]).T
            local[fixedIds]=pos[fixedIds]
            delta=(local-pos).astype('<f4');normal=array(src,binary,prim['attributes']['NORMAL'])
            normalDelta=(normals(local,idx)-normal).astype('<f4')
            primitive['targets']=[{'POSITION':put(delta.tobytes(),'VEC3',n,minimum=delta.min(axis=0).tolist(),maximum=delta.max(axis=0).tolist()),'NORMAL':put(normalDelta.tobytes(),'VEC3',n)}]
            mesh['weights']=[0];node['weights']=[0];tracks.append((ni,'weights',payload['clip']['weights'],'SCALAR'))
        elif role in ('moving_structure','co_moving_context'):
            node.pop('matrix');q,scale=quat(M);node.update(translation=M[:3,3].tolist(),rotation=q,scale=scale)
            translations=[];rotations=[]
            for weight in payload['clip']['weights']:
                RR=rotation(axis,angle*weight);MM=M.copy();MM[:3,:3]=RR@M[:3,:3];MM[:3,3]=(M[:3,3]-pivot)@RR.T+pivot
                translations.extend(MM[:3,3].tolist());rotations.extend(quat(MM)[0])
            tracks.extend([(ni,'translation',translations,'VEC3'),(ni,'rotation',rotations,'VEC4')]);end=(world-pivot)@R.T+pivot
        elif role not in ('fixed_structure','passive_context'):raise ValueError('unknown role')
        edge=np.unique(np.sort(np.r_[idx[:,[0,1]],idx[:,[1,2]],idx[:,[2,0]]],axis=1),axis=0)
        startlen=np.linalg.norm(world[edge[:,0]]-world[edge[:,1]],axis=1);endlen=np.linalg.norm(end[edge[:,0]]-end[edge[:,1]],axis=1)
        relative=np.abs(endlen-startlen)/np.maximum(startlen,1e-12)
        tri0=world[idx];tri1=end[idx];n0=np.cross(tri0[:,1]-tri0[:,0],tri0[:,2]-tri0[:,0]);n1=np.cross(tri1[:,1]-tri1[:,0],tri1[:,2]-tri1[:,0])
        flips=int(((n0*n1).sum(axis=1)<0).sum())
        if flips or not np.isfinite(end).all():raise ValueError(f'invalid flipped/nonfinite authored surface: {key}')
        metrics.append({'sourceKey':key,'sourceName':row['sourceName'],'role':role,'vertices':n,'triangles':len(idx),
                        'maximumDisplacementMetres':float(np.linalg.norm(end-world,axis=1).max()),'maxRelativeEdgeLengthChange':float(relative.max()),
                        'flippedTriangles':flips,'fixedRegionCount':len(fixedIds),'movingRegionCount':len(movingIds),
                        'fixedRegionErrorMetres':float(np.linalg.norm(end[fixedIds]-world[fixedIds],axis=1).max()) if fixedIds else None,
                        'movingRegionErrorMetres':float(np.linalg.norm(end[movingIds]-((world[movingIds]-pivot)@R.T+pivot),axis=1).max()) if movingIds else None})
        members.append({'sourceKey':key,'nodeId':nodeId,'sourceNamespace':manifest['namespace'],'role':role,'side':row['sourceLabelSide'],
                        'resourceKey':row['lods'][lod]['resource'],'lod':lod,'sourceChunkSha256':row['lods'][lod]['chunk'],
                        'geometrySha256':digest,'instanceMatrix':row['matrix']})
        doc['nodes'].append(node);doc['meshes'].append(mesh);doc['scenes'][0]['nodes'].append(ni)
    if subject not in seen or not any(m['sourceKey']==subject and m['role']=='deforming_muscle_surface' for m in members):raise ValueError('missing deforming subject')
    rest=container(doc,buf) # Source base POSITION/NORMAL/index identical; weights=0 and original matrices.
    times=payload['clip']['timesSeconds'];ta=put(struct.pack('<'+'f'*len(times),*times),'SCALAR',len(times),minimum=[min(times)],maximum=[max(times)])
    samplers=[];channels=[]
    for ni,path,values,type in tracks:
        count=len(values)//{'SCALAR':1,'VEC3':3,'VEC4':4}[type];ai=put(struct.pack('<'+'f'*len(values),*values),type,count)
        channels.append({'sampler':len(samplers),'target':{'node':ni,'path':path}});samplers.append({'input':ta,'output':ai,'interpolation':'LINEAR'})
    doc['animations']=[{'name':payload['clip']['id'],'samplers':samplers,'channels':channels}]
    motion=container(doc,buf)
    record={'schemaVersion':'t59-authoring-record-v1','id':payload['id'],'inputSha256':sha(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()),
            'sourceClaimVsAuthoring':{'sourceMeasured':['immutable source POSITION/NORMAL/index, instance matrices, explicit labels, units/frame/static snapshot'],
            'authored':['inspected vertex masks, conservative hinge approximation, clip timing and smooth deformation field'],
            'notClaimed':['source-provided neutral/bind pose','physiological strain or calibrated contraction','human approval','clinical motion range']},
            'rights':RIGHTS,'poseRange':{'referencePoseId':manifest['frameContract']['staticReferencePose']['id'],'endPoseId':payload['endPoseId'],
            'angleRadians':angle,'axis':axis,'pivotMetres':pivot.tolist(),'domeArcFitRadiusMetres':radius,'domeArcFitRmsMetres':residual},
            'anatomicalEvidence':payload['anatomicalEvidence'],'geometryInspection':payload['geometryInspection'],
            'unresolved':payload['unresolved'],'members':members,'surfaceMetrics':metrics,'restSha256':sha(rest),'motionSha256':sha(motion),
            'motionBytes':len(motion),'sourceGeometryModified':False}
    return rest,motion,record

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output-directory',type=Path,required=True);args=p.parse_args()
    payload=json.loads(args.input.read_text());rest,motion,record=author(payload)
    out=args.output_directory;out.mkdir(parents=True,exist_ok=True);(out/'reference.glb').write_bytes(rest);(out/'motion.glb').write_bytes(motion)
    (out/'authoring-record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'status':'authored_candidate','members':len(record['members']),'bytes':len(motion),'motionSha256':sha(motion),'upstreamRigOrHumanApprovalCreated':False}))
if __name__=='__main__':main()
