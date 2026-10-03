#!/usr/bin/env python3
"""Source-to-derived rest/mid/end vertex containment diagnostic, independent of renderer/AABB."""
import argparse,json,math
from pathlib import Path
import numpy as np
from author_source_surface_motion import read,source_geometry,rotation,ROOT,dump
from derive_source_surface_motion import load_glb,accessor_bytes,sha

from source_surface_constraints import inside
def main():
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--record',required=True);p.add_argument('--asset',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    inp=read(a.input);rec=read(a.record);manifest=read(inp['dataset']['path']);src={r['sourceKey']:r for r in manifest['instances']}
    # load_glb intentionally rejects animations for static export; decode a validated self-contained candidate separately.
    import struct
    raw=(ROOT/a.asset).read_bytes();jlen=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+jlen]);off=20+jlen;blen=struct.unpack_from('<I',raw,off)[0];buf=raw[off+8:off+8+blen]
    members={m['sourceKey']:m for m in rec['members']};pivot=np.array(rec['poseRange']['pivotMetres']);axis=inp['joint']['axis'];angle=inp['joint']['angleRadians'];clearance=np.array(rec['poseRange'].get('coupledClearanceMetres',[0,0,0]))
    meshes={}
    for key,member in members.items():
        source,binary,primitive,pos,idx,M,world=source_geometry(src[key],member['lod'])
        prim=doc['meshes'][int(member['nodeId'].split('_')[-1])]['primitives'][0];deltas=[]
        for target in prim.get('targets',[]):
            rawD=accessor_bytes(doc,buf,target['POSITION'])[-1];delta=np.frombuffer(rawD,dtype='<f4').reshape(-1,3);deltas.append((delta@M[:3,:3].T)/M[3,3])
        meshes[key]=(world,idx,deltas)
    passiveChecks=[]
    checks=[];subject=inp['subjectSourceKey']
    for t in [0,.5,1]:
        R=rotation(axis,angle*t)
        def current(key):
            world,_,deltas=meshes[key];role=members[key]['role']
            if role in ['moving_structure','co_moving_context']:return (world-pivot)@R.T+pivot+clearance*t
            if not deltas or t==0:return world
            phase=t*len(deltas);lower=int(phase);frac=phase-lower
            before=np.zeros_like(world) if lower==0 else deltas[lower-1]
            after=deltas[min(lower,len(deltas)-1)]
            return world+before*(1-frac)+after*frac
        for passiveKey, passiveMember in members.items():
            if passiveMember['role']!='deforming_passive_surface':continue
            points=current(passiveKey)
            for boneKey,boneMember in members.items():
                if boneMember['role'] not in ['fixed_structure','moving_structure']:continue
                ids=np.flatnonzero(inside(points,current(boneKey),meshes[boneKey][1])).tolist()
                passiveChecks.append({'poseFraction':t,'testedSourceKey':passiveKey,'contextSourceKey':boneKey,'insideVertexIds':ids,'count':len(ids)})
        points=current(subject)
        for key,m in members.items():
            if key==subject:continue
            count=np.flatnonzero(inside(points,current(key),meshes[key][1])).tolist()
            checks.append({'poseFraction':t,'testedSourceKey':subject,'contextSourceKey':key,'contextRole':m['role'],'insideVertexIds':count,'count':len(count)})
    passiveBaseline={(x['testedSourceKey'],x['contextSourceKey']):set(x['insideVertexIds']) for x in passiveChecks if x['poseFraction']==0}
    for x in passiveChecks:x['newInsideVertexIds']=sorted(set(x['insideVertexIds'])-passiveBaseline[x['testedSourceKey'],x['contextSourceKey']]);x['newCount']=len(x['newInsideVertexIds'])
    baseline={x['contextSourceKey']:set(x['insideVertexIds']) for x in checks if x['poseFraction']==0}
    for x in checks:x['newInsideVertexIds']=sorted(set(x['insideVertexIds'])-baseline[x['contextSourceKey']]);x['newCount']=len(x['newInsideVertexIds'])
    # Check moving talus at fixed tibial/fibular surfaces as well. Bone kinematics are not inferred from mesh labels.
    talus=inp['joint']['landmark']['sourceKey'];boneChecks=[]
    for t in [0,.5,1]:
        R=rotation(axis,angle*t);points=(meshes[talus][0]-pivot)@R.T+pivot+clearance*t
        for key,m in members.items():
            if m['role']!='fixed_structure':continue
            ids=np.flatnonzero(inside(points,meshes[key][0],meshes[key][1])).tolist();boneChecks.append({'poseFraction':t,'contextSourceKey':key,'insideVertexIds':ids,'count':len(ids)})
    bbase={x['contextSourceKey']:set(x['insideVertexIds']) for x in boneChecks if x['poseFraction']==0}
    for x in boneChecks:x['newInsideVertexIds']=sorted(set(x['insideVertexIds'])-bbase[x['contextSourceKey']]);x['newCount']=len(x['newInsideVertexIds'])
    summary={'passiveBoneChecks':len(passiveChecks),'newPassiveContainmentMaximum':max(x['newCount'] for x in passiveChecks),'newSubjectContainmentMaximum':max(x['newCount'] for x in checks),'newTalusContainmentMaximum':max(x['newCount'] for x in boneChecks),'subjectContextChecks':len(checks),'talusFixedBoneChecks':len(boneChecks)}
    result={'schemaVersion':'t59-authored-surface-geometry-qc-v1','assetSha256':sha(raw),'method':'generalized triangle winding; all selected source vertices, all package context surfaces, three poses','summary':summary,'subjectChecks':checks,'passiveChecks':passiveChecks,'talusChecks':boneChecks,
       'limitations':['Vertex containment is not exhaustive triangle/triangle collision or cartilage contact simulation. Source surfaces may overlap or be open; retain baseline and differences.', 'Exact anatomical attachment footprints/instantaneous helical axis remain unresolved; authored masks constrain continuity only.']}
    dump(a.output,result);print(json.dumps(summary))
if __name__=='__main__':main()
