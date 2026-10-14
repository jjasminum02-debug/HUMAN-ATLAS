"""Independent read-only replay of an authored contact field and its volume.

Finite source-volume samples supplement, and never replace, emitted collision
tests. No sample is an acupoint or newly approved anatomical landmark.
"""
from pathlib import Path
import argparse, hashlib, json, sys
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

R=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--evidence',required=True);p.add_argument('--revision',required=True)
p.add_argument('--field-manifest',help='Frozen record override for portable independent inspection.')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);E=R/a.evidence
load=lambda p:json.loads(p.read_text())
path=E/f'candidates/fit-{a.revision}.json';before=hashlib.sha256(path.read_bytes()).hexdigest()
d=load(path);record=load(E/f'contact-fit-{a.revision}.json');unit=record['sourceUnit']
base=load(R/a.field_manifest if a.field_manifest else Path(unit.get('initialFieldInput',R/'work/evidence/AT10/2026-10-14-skin-fit-r4/surface-bands-r31.json')))
field=next(x for x in base['patches'] if x['patch']==unit.get('unit','hand')+'-'+unit['side'])
s=np.array(d['sourceVertices']);v=np.array(d['positions']);ids=np.array(unit['sourceVertices'])
tri=np.array([[f['derivedVertices'][0],f['derivedVertices'][j],f['derivedVertices'][j+1]]
    for f in d['faces'] for j in range(1,len(f['derivedVertices'])-1)])
mask=np.zeros(len(s),bool);mask[ids]=True;fi=np.flatnonzero(mask[tri].all(1))
centers=np.array(field['sourceFieldCentersM']);target=np.array(field['nativeFieldTargetsM'])
center=centers.mean(0);x=(centers-center)/.1
r=np.linalg.norm(x[:,None]-x[None],axis=2);poly=np.column_stack([np.ones(len(x)),x])
coef=np.linalg.solve(np.block([[r**3+np.diag(field['regularization']),poly],[poly.T,np.zeros((4,4))]]),np.vstack([target,np.zeros((4,3))]))
def replay(points):
    values=[];derivatives=[]
    for start in range(0,len(points),256):
        q=(points[start:start+256]-center)/.1;delta=q[:,None]-x[None];radius=np.linalg.norm(delta,axis=2)
        mapped=np.einsum('qn,no->qo',radius**3,coef[:-4])+np.column_stack([np.ones(len(q)),q])@coef[-4:]
        jac=(np.einsum('qnk,no->qok',3*radius[:,:,None]*delta,coef[:-4])+coef[-3:].T)/.1
        for stage in record['steps']:
            sigma=np.array(stage['sigmaM']);c=np.array(stage['rawFieldCoefficients'])
            delta=mapped[:,None]-np.array(stage['fieldCentersM'])[None]
            phi=np.exp(-np.einsum('qnk,qnk->qn',delta,delta)/(2*sigma**2))
            gradient=-phi[:,:,None]*delta/sigma[None,:,None]**2
            mapped+=np.einsum('qn,no->qo',phi,c)
            jac=(np.eye(3)[None]+np.einsum('qnk,no->qok',gradient,c))@jac
        values.append(mapped);derivatives.append(jac)
    return np.concatenate(values),np.concatenate(derivatives)

# A deterministic grid fills the actual source volume. Rays determine which
# grid locations are inside source skin with nearest ownership in this unit.
tree=BVHTree.FromPolygons(s.tolist(),tri.tolist(),all_triangles=True)
lo,hi=s[ids].min(0),s[ids].max(0)
interior=[]
for point in np.array(np.meshgrid(*(np.linspace(lo[k],hi[k],15) for k in range(3)),indexing='ij')).reshape(3,-1).T:
    _,_,face,_=tree.find_nearest(Vector(point))
    if not mask[tri[face]].all():continue
    votes=[]
    for dr in [(-1,.137,.231),(-1,-.217,.113),(-1,.219,-.117)]:
        direction=Vector(dr).normalized();origin=Vector(point);count=0
        for _ in range(40):
            hit,_,_,_=tree.ray_cast(origin,direction,4.)
            if hit is None:break
            count+=1;origin=hit+direction*.000002
        votes.append(count%2)
    if sum(votes)>=2:interior.append(point.tolist())
source_queries=np.vstack([s[ids],s[tri[fi]].mean(1),np.array(interior).reshape(-1,3)])
mapped,jac=replay(source_queries);det=np.linalg.det(jac)
assert np.isfinite(mapped).all() and np.isfinite(jac).all()
error=np.linalg.norm(mapped[:len(ids)]-v[ids],axis=1)
sample=source_queries[::max(1,len(source_queries)//96)]
analytic=replay(sample)[1];fd=np.empty_like(analytic)
for k in range(3):
    h=np.zeros(3);h[k]=1e-6
    fd[:,:,k]=(replay(sample+h)[0]-replay(sample-h)[0])/(2e-6)
helper_source=np.array([x['source'] for x in field['nativeJointControls']])
helper_target=np.array([x['target'] for x in field['nativeJointControls']])
initial_query=(helper_source-center)/.1
initial_radius=np.linalg.norm(initial_query[:,None]-x[None],axis=2)
initial_helper=np.einsum('qn,no->qo',initial_radius**3,coef[:-4])+np.column_stack([np.ones(len(helper_source)),initial_query])@coef[-4:]
result={'revision':a.revision,'sourceUnitSide':unit['side'],'sourceVertexQueries':len(ids),'sourceFaceCentroidQueries':len(fi),
    'sourceVolumeGridQueries':len(interior),'minimumSampled3DFieldJacobian':float(det.min()),'nonPositiveJacobianCount':int((det<=0).sum()),
    'minimumVolumeJacobian':float(det[len(ids)+len(fi):].min()),'maximumReplayPositionErrorM':float(error.max()),
    'finiteDifferenceMaximumError':float(np.abs(fd-analytic).max()),
    'maximumHelperMovementFromInitialFieldM':float(np.linalg.norm(replay(helper_source)[0]-initial_helper,axis=1).max()),
    'initialJointCorrespondenceErrorM':float(np.linalg.norm(initial_helper-helper_target,axis=1).max()),
    'candidateReadOnly':before==hashlib.sha256(path.read_bytes()).hexdigest(),
    'finiteSamplesProveGlobalInjectivity':False,'geometryAcceptance':False,'learnerEligible':False}
result['numericalChecksPassed']=result['nonPositiveJacobianCount']==0 and result['maximumReplayPositionErrorM']<1e-7 and result['finiteDifferenceMaximumError']<.002 and result['candidateReadOnly']
assert result['candidateReadOnly']
(E/f'contact-field-inspection-{a.revision}.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result),flush=True)
