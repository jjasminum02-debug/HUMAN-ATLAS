"""Interpolate the source-shaped articulated foot as a continuous 3D field.

This probes an alternative to the sparse joint cage, which collapsed toe cross
sections. Positive samples and correspondence metadata remain separate from
geometry and landmark acceptance. Original source and native are never edited.
"""
from pathlib import Path
import argparse,json,copy
import numpy as np
R=Path(__file__).resolve().parents[2];p=argparse.ArgumentParser();p.add_argument('--evidence',required=True);p.add_argument('--base',required=True);p.add_argument('--revision',required=True);p.add_argument('--shape-blend',type=float,default=1.);a=p.parse_args();E=R/a.evidence;read=lambda p:json.loads(p.read_text());assert 0<a.shape_blend<=1
d=read(E/f'candidates/fit-{a.base}.json');f=copy.deepcopy(read(R/'work/evidence/AT10/2026-10-14-skin-fit-r5/surface-bands-r52.json')['patches'][0]);assert f['patch']=='foot-right'
s=np.array(d['sourceVertices']);v=np.array(d['positions']);ids=np.array(f['sourceVertices']);roots=np.array([x['sourceVertex'] for x in f['sharedBoundary']]);tri=np.array([[ff['derivedVertices'][0],ff['derivedVertices'][j],ff['derivedVertices'][j+1]] for ff in d['faces'] for j in range(1,len(ff['derivedVertices'])-1)])
centers=s[ids];targets=v[ids]
if a.shape_blend<1:
 prior=read(R/'work/evidence/AT10/2026-10-14-skin-fit-r5/candidates/fit-r52.json');targets=targets*a.shape_blend+np.array(prior['positions'])[ids]*(1-a.shape_blend)
center=centers.mean(0);x=(centers-center)/.1;rr=np.linalg.norm(x[:,None]-x[None,:],axis=2);poly=np.c_[np.ones(len(x)),x];reg=np.full(len(x),1e-10)
coef=np.linalg.solve(np.block([[rr**3+np.diag(reg),poly],[poly.T,np.zeros((4,4))]]),np.vstack([targets,np.zeros((4,3))]))
def ev(points):
 mapped=[];jacs=[]
 for i in range(0,len(points),96):
  q=(points[i:i+96]-center)/.1;delta=q[:,None]-x[None];rad=np.linalg.norm(delta,axis=2)
  mapped.append(np.einsum('qn,no->qo',rad**3,coef[:-4])+np.c_[np.ones(len(q)),q]@coef[-4:]);jacs.append((np.einsum('qnk,no->qok',3*rad[:,:,None]*delta,coef[:-4])+coef[-3:].T)/.1)
 return np.concatenate(mapped),np.concatenate(jacs)
local=tri[np.isin(tri,ids).all(1)];queries=np.vstack([s[ids],s[local].mean(1)]);mapped,jac=ev(queries);det=np.linalg.det(jac);surface=mapped[:len(ids)];err=np.linalg.norm(surface-targets,axis=1)
report={'revision':a.revision,'sourceShapeCandidate':a.base,'sourceVertexConstraints':len(ids),'surfaceAndFaceCentroidSamples':len(det),'minimumSampled3DFieldJacobian':float(det.min()),'nonPositiveJacobianCount':int((det<=0).sum()),'maximumInterpolationErrorM':float(err.max()),'method':'dense source-surface cubic field interpolates harmonic toe-chain shape; not native nearest fit','geometryAcceptance':False,'learnerEligible':False,'finiteSamplesProveGlobalInjectivity':False}
report['shapeBlend']=a.shape_blend;report['nonPositiveSourceQueries']=[{'query':int(i),'sourceM':queries[i].tolist(),'jacobianDeterminant':float(det[i])} for i in np.flatnonzero(det<=0)]
print(json.dumps(report),flush=True);(E/f'dense-field-{a.revision}.json').write_text(json.dumps(report,indent=2)+'\n')
if det.min()<=.004: print('INITIAL_FIELD_REJECTED',flush=True);raise SystemExit(0)
f.update(sourceFieldCentersM=centers.tolist(),nativeFieldTargetsM=targets.tolist(),regularization=reg.tolist(),initialUnitPositionsM=surface.tolist(),sourceShapeCandidate=a.base,denseSourceShapeInterpolation=True,minimumInitialSampledJacobian=float(det.min()),nonPositiveJacobianCount=0,acceptancePassed=False)
d['positions']=v.tolist()
for i,vi in enumerate(ids):d['positions'][int(vi)]=surface[i].tolist()
d.update(candidateRevision=a.revision,fitAcceptancePassed=False,learnerEligible=False)
for path,data in [(E/f'dense-foot-field-{a.revision}.json',{'patches':[f]}),(E/f'candidates/fit-{a.revision}.json',d)]:
 assert not path.exists();path.write_text(json.dumps(data,separators=(',',':')))
