"""Correct an authored rig-handle embedding, preserving the actual source.

An exterior source rig handle is not equated to an interior native bone point.
This writes a derived, addressed interior model control; it approves no acupoint.
"""
from pathlib import Path
import argparse,json,sys,copy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'work/tools'))
from at10_skin_field_math import cubic_operator
p=argparse.ArgumentParser();p.add_argument('--evidence',required=True);p.add_argument('--revision',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
E=R/a.evidence;load=lambda p:json.loads(p.read_text())
d=load(E/'candidates/fit-r41.json');s=np.array(d['sourceVertices']);v=np.array(d['positions'])
f=copy.deepcopy(next(x for x in load(E/'initial-foot-fields-r31.json')['patches'] if x['patch']=='foot-right'))
t=np.array([[x['derivedVertices'][0],x['derivedVertices'][j],x['derivedVertices'][j+1]] for x in d['faces'] for j in range(1,len(x['derivedVertices'])-1)])
tree=BVHTree.FromPolygons(s.tolist(),t.tolist(),all_triangles=True)
audit=next(x for x in load(E/'helper-embedding-r1.json') if x['revision']=='r44' and x['handleId']=='joint-r-toe-1-3')
assert audit['sourceEmbedding']['insideVotes']==[0,0,0]
face=audit['sourceEmbedding']['nearestTriangle'];vertices=t[face];q=np.array(audit['sourceEmbedding']['nearestM'])
normal=np.cross(s[vertices[1]]-s[vertices[0]],s[vertices[2]]-s[vertices[0]]);normal/=np.linalg.norm(normal)
derived=q-normal*.0015
def inside(point):
    result=[]
    for dr in [(-1,.137,.231),(-1,-.217,.113),(-1,.219,-.117)]:
        direction=Vector(dr).normalized();origin=Vector(point);count=0
        for _ in range(40):
            hit,_,_,_=tree.ray_cast(origin,direction,4.)
            if hit is None:break
            count+=1;origin=hit+direction*.000002
        result.append(count%2)
    return result
assert inside(derived)==[1,1,1],inside(derived)
c=next(x for x in f['nativeJointControls'] if x['id']=='joint-r-toe-1-3');old=np.array(c['source'])
centers=np.array(f['sourceFieldCentersM']);index=np.argmin(np.linalg.norm(centers-old,axis=1));assert np.linalg.norm(centers[index]-old)<1e-10
c['originalSourceHelper']=copy.deepcopy(c);c['source']=derived.tolist()
c['role']='authored interior distal big-toe model handle; original rig helper outside skin is retained separately'
c['authoredSourceControl']={'sourceTriangle':int(face),'sourceObjFace':d['faces'][face//2]['sourceFace'],'originalSourceVertexIds':[d['originalVertexIds'][int(i)] for i in vertices],
    'sourceFacetM':s[vertices].tolist(),'closestFacetPointM':q.tolist(),'inwardDirection':(-normal).tolist(),'inwardModelOffsetM':.0015,
    'sourceInsideVotes':[1,1,1],'originalHandleOutsideDistanceM':audit['sourceEmbedding']['distanceM'],'anatomicalLandmarkApproval':False,'meaning':'geometric interior control, not observed source bone or acupoint'}
centers[index]=derived;f['sourceFieldCentersM']=centers.tolist();f['embeddingCorrection']=c['authoredSourceControl']
ids=np.array(f['sourceVertices']);roots=np.array([x['sourceVertex'] for x in f['sharedBoundary']])
op=cubic_operator(centers,f['nativeFieldTargetsM'],f['regularization']);mapped,jac=op(s[ids]);old_v=v.copy();v[ids]=mapped;v[roots]=old_v[roots]
f['minimumInitialSampledJacobian']=float(np.linalg.det(jac).min());f['nonPositiveJacobianCount']=int((np.linalg.det(jac)<=0).sum())
d['positions']=v.tolist();d['candidateRevision']=a.revision;d['fitAcceptancePassed']=False;d['learnerEligible']=False;d['embeddingCorrection']=f['embeddingCorrection']
for path,payload in [(E/f'candidates/fit-{a.revision}.json',d),(E/f'surface-bands-{a.revision}.json',{'patches':[f]})]:
    assert not path.exists();path.write_text(json.dumps(payload,separators=(',',':')))
print({'revision':a.revision,'sourceHelperUnchanged':True,'derivedHandleInsideSource':inside(derived),'minimumInitialJacobian':f['minimumInitialSampledJacobian'],'nonPositive':f['nonPositiveJacobianCount']},flush=True)
