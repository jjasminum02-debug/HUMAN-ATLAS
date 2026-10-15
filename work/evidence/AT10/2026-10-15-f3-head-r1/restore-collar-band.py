"""Restore a whole addressed first-interior collar band, not position-only seam.
Positive field replay and actual emitted self/native tests remain independent.
"""
from pathlib import Path
import sys,json,gzip,numpy as np
R=Path.cwd();E=R/'work/evidence/AT10/2026-10-15-f3-head-r1';sys.path.insert(0,str(R/'work/tools'));from at10_skin_field_math import solve_landmark_flow,landmark_flow_operator
assert not (E/'candidates/fit-f3c12.json').exists() and not (E/'recipe-f3c12.json.gz').exists(), 'Historical attempt exists; use a new versioned output instead.'
load=lambda p:json.loads(p.read_text());d=load(E/'candidates/fit-f3c11.json');r=json.loads(gzip.decompress((E/'recipe-f3c11.json.gz').read_bytes()));base=load(R/r['baseCandidate']);s=np.array(d['sourceVertices']);v=np.array(d['positions']);b=np.array(base['positions']);ids=np.array(r['sourceUnitVertices']);tri=np.array([[f['derivedVertices'][0],f['derivedVertices'][j],f['derivedVertices'][j+1]] for f in d['faces'] for j in range(1,len(f['derivedVertices'])-1)]);band=set(r['actualTopologicalBoundary']);own=set(ids.tolist())
for _ in range(2):band|=set(tri[np.isin(tri,list(band)).any(1)].ravel().tolist())&own
band=np.array(sorted(band));controls=[]
def add(i,target,role):controls.append({'id':role+'-'+str(i),'source':v[i].tolist(),'target':target.tolist(),'sourceAddress':{'logicalVertex':int(i),'originalVertex':d['originalVertexIds'][i],'originalCoreM':s[i].tolist(),'sourceObjFaces':[x['sourceFace'] for x in d['faces'] if i in x['derivedVertices']]},'role':role,'sigmaM':.04})
for i in band:add(i,b[i],'restore-original-collar-band')
cohort=ids[(s[ids,1]>.64)&~np.isin(ids,band)];chosen=[];dd=np.full(len(cohort),np.inf)
for k in range(65):
 i=int(cohort[0] if not chosen else cohort[dd.argmax()]);chosen.append(i);dd=np.minimum(dd,np.linalg.norm(s[cohort]-s[i],axis=1));add(i,v[i],'preserve-current-face-pinna')
(E/'collar-band-controls-f3c12.json').write_text(json.dumps(controls,separators=(',',':'))+'\n');flow=solve_landmark_flow(controls,initial_affine=np.eye(3),initial_translation=np.zeros(3));p,j=landmark_flow_operator(flow)(v[ids]);v[ids]=p;res=float(np.linalg.norm(v[band]-b[band],axis=1).max());assert res<1e-7,res;v[band]=b[band];d['positions']=v.tolist();d['candidateRevision']='f3c12';r={**r,'initialField':r,'postFields':[],'stages':flow['stages'],'affine':np.eye(3).tolist(),'translation':[0,0,0],'collarBandControlFile':'collar-band-controls-f3c12.json','collarBandFixedLogicalVertices':band.tolist(),'collarBandResidualBeforeExactJoinM':res,'method':'Full source pinna + addressed two-ring collar restoration','boundaryResidualBeforeExactJoinM':r['boundaryResidualBeforeExactJoinM']+res};(E/'candidates/fit-f3c12.json').write_text(json.dumps(d,separators=(',',':'))+'\n');raw=(json.dumps(r,separators=(',',':'))+'\n').encode();(E/'recipe-f3c12.json.gz').write_bytes(gzip.compress(raw,mtime=0));print('COLLAR',len(band),'residual',res,'minCorrectionJ',float(np.linalg.det(j).min()),flush=True)
