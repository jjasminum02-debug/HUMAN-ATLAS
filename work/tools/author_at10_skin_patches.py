"""Continuous native-joint/source-helper patch deformation, offline only.

Builds a candidate in a new evidence directory; does not grant fit acceptance.
"""
from pathlib import Path
import json, argparse, numpy as np
R=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--evidence',required=True);p.add_argument('--revision',default='r14-base');a=p.parse_args()
E=R/a.evidence;B=R/'work/evidence/AT10/2026-10-13-skin-fit-r1'
d=json.loads((B/'candidates/fit-r9.json').read_text());src=np.array(d['sourceVertices']);v=np.array(d['positions']);before=v.copy()
ctrl={x['id']:x for x in json.loads((B/'native-controls-r2.json').read_text())['controls']}
native=json.loads((B/'native-surfaces-r1.json').read_text());cohorts=[]
def smoothstep(x):
 x=np.clip(x,0,1);return x*x*(3-2*x)
def gaussian(p,c,r):return np.exp(-np.sum((p[:,None,:]-c[None,:,:])**2,axis=2)/(2*r*r))
def warp(ids,controls,reference,radius,regularization=1e-5):
 cs=np.array([c['source'] for c in controls]);ct=np.array([c['target'] for c in controls]);residual=ct-reference(cs)
 k=gaussian(cs,cs,radius);w=np.linalg.solve(k+np.eye(len(cs))*regularization,residual)
 out=reference(src[ids])+gaussian(src[ids],cs,radius)@w
 return out,float(np.linalg.norm(k@w-residual,axis=1).max())
for side,letter in [('left','l'),('right','r')]:
 fr=d['articulatedFrames'][side];s=np.array(fr['sourceWrist']);target=np.array(fr['targetWrist']);ps=np.array(fr['sourcePalmFrame']);pt=np.array(fr['targetPalmFrame']);scale=np.array(fr['palmScale']);scale[2]=1.45
 progress=(src-s)@ps[:,0]
 ids=np.flatnonzero((src[:,0]*(1 if side=='left' else -1)>.37)&(progress>-.065))
 controls=[ctrl[f'joint-{letter}-hand']]+[ctrl[f'joint-{letter}-finger-{di}-{pa}'] for di in range(1,6) for pa in range(1,5)]
 reference=lambda x:target+((x-s)@ps*scale)@pt.T
 out,residual=warp(ids,controls,reference,.026)
 w=smoothstep((progress[ids]+.065)/.045);v[ids]=v[ids]*(1-w[:,None])+out*w[:,None]
 cohorts.append({'id':'continuous-hand-'+side,'sourceVertices':np.array(d['originalVertexIds'])[ids].tolist(),'controls':controls,'sourcePalmFrame':ps.tolist(),'nativePalmFrame':pt.tolist(),'scale':scale.tolist(),'gaussianRadiusM':.026,'regularization':1e-5,'controlResidualMaxM':residual,'sourceTransitionIntervalM':[-.065,-.020],'rotationDeterminant':float(np.linalg.det(pt@ps.T))})
 # Feet are fitted as one continuous ankle/heel/forefoot/toe field. Source toe
 # joints remain independent controls; the exact native heel is a real surface.
 ankle=ctrl[f'joint-{letter}-ankle'];s=np.array(ankle['source']);target=np.array(ankle['target'])
 sourceheel=src[(src[:,0]*(1 if side=='left' else -1)>.1)&(src[:,1]<-.765)&(src[:,2]<-.035)].mean(0)
 calc=next((k,b) for k,b in native.items() if b['side']==side and b['name']=='Calcaneus');cv=np.array(calc[1]['v']);heelids=np.flatnonzero(cv[:,2]<cv[:,2].min()+.006);targetheel=cv[heelids].mean(0)+[0,-.004,-.005]
 controls=[ankle]+[ctrl[f'joint-{letter}-toe-{di}-{pa}'] for di in range(1,6) for pa in range(1,4)]
 controls.append({'id':'heel-'+side,'source':sourceheel.tolist(),'target':targetheel.tolist(),'nativeReferences':[{'sourceKey':calc[0],'nativeVertexIds':heelids.tolist(),'operator':'posterior calcaneus cap plus authored 4 mm plantar/5 mm posterior skin allowance'}]})
 # Heel control changes shape and ankle transition, rather than copying native faces.
 ids=np.flatnonzero((src[:,0]*(1 if side=='left' else -1)>.06)&(src[:,1]<-.68))
 # Initial metre-to-metre local frame is identity with independently fitted regional dimensions.
 reference=lambda x:target+(x-s)*[.78,.83,.92]
 out,residual=warp(ids,controls,reference,.033)
 w=smoothstep((-.68-src[ids,1])/.055);v[ids]=v[ids]*(1-w[:,None])+out*w[:,None]
 cohorts.append({'id':'continuous-foot-'+side,'sourceVertices':np.array(d['originalVertexIds'])[ids].tolist(),'controls':controls,'scale':[.78,.83,.92],'gaussianRadiusM':.033,'regularization':1e-5,'controlResidualMaxM':residual,'sourceCalfTransitionY':[-.68,-.735]})
d['positions']=v.tolist();d['candidateRevision']=a.revision;d['continuousPatchRecipe']=cohorts;d['fitAcceptancePassed']=False;d['learnerEligible']=False
(E/f'candidates/fit-{a.revision}.json').write_text(json.dumps(d,separators=(',',':')))
(E/f'patch-controls-{a.revision}.json').write_text(json.dumps({'cohorts':cohorts,'nativePoseUnchanged':True,'maxDisplacementM':float(np.linalg.norm(v-before,axis=1).max())},indent=2)+'\n')
print('CONTINUOUS_PATCHES',a.revision,[(c['id'],c['controlResidualMaxM']) for c in cohorts])
