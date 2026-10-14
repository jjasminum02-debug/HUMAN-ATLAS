"""Read-only ambiguity audit. Nearest loop never substitutes for identity."""
from pathlib import Path
import sys,json,numpy as np
R=Path.cwd();E=R/'work/evidence/AT10/2026-10-14-f2-left-foot-r1';sys.path.insert(0,str(R/'work/tools'));from at10_surface_sections import section_loops
load=lambda p:json.loads(p.read_text());d=load(E/'candidates/fit-f2c1.json');s=np.array(d['sourceVertices']);t=np.array([[f['derivedVertices'][0],f['derivedVertices'][j],f['derivedVertices'][j+1]] for f in d['faces'] for j in range(1,len(f['derivedVertices'])-1)]);f=load(E/'surface-bands-f2controls1.json')['patches'][0];local=np.flatnonzero(np.isin(t,f['sourceVertices']).all(1));out=[]
for digit in range(1,6):
 chain=[x for x in f['nativeJointControls'] if x['id'].startswith(f'joint-l-toe-{digit}-')]
 for part,(ca,cb) in enumerate(zip(chain[:-1],chain[1:])):
  aa=np.array(ca['sourceOriginalHelperM']);bb=np.array(cb['sourceOriginalHelperM']);axis=bb-aa;axis/=np.linalg.norm(axis);up=np.array([0.,1.,0.]);up-=axis*(up@axis);up/=np.linalg.norm(up);right=np.cross(up,axis)
  for u in [.35,.5,.72]:
   so=aa*(1-u)+bb*u;loops,opened=section_loops(s,t,so,axis,local);rows=[]
   for loop in loops:
    pts=np.array([x['pointM'] for x in loop['nodes']]);q=pts-so;xx=q@right;yy=q@up;cross=xx*np.roll(yy,-1)-np.roll(xx,-1)*yy;area=cross.sum()/2
    if abs(area)<1e-12:continue
    centre=so+right*((xx+np.roll(xx,-1))*cross).sum()/(6*area)+up*((yy+np.roll(yy,-1))*cross).sum()/(6*area)
    length=float(np.linalg.norm(pts-np.roll(pts,1,axis=0),axis=1).sum());lateral=float(abs((centre-so)@right));ok=length<(.105 if digit==1 else .082) and lateral<(.010 if digit==1 else .0055)
    rows.append({'acceptedForAuthoredAxis':bool(ok),'ringLengthM':length,'lateralCentreDistanceM':lateral,'areaCentroidM':centre.tolist(),'sourceTriangleIds':loop['segmentTriangles'],'sourceObjFaceIds':sorted(set(d['faces'][int(i)//2]['sourceFace'] for i in loop['segmentTriangles']))})
   count=sum(x['acceptedForAuthoredAxis'] for x in rows);assert count<=1,('ambiguous own-digit loops',digit,part,u)
   out.append({'digit':digit,'segment':part,'fraction':u,'sourcePlaneOriginM':so.tolist(),'plausibleOwnDigitLoopCount':count,'ambiguous':count>1,'loops':rows})
assert all(any(x['plausibleOwnDigitLoopCount']==1 for x in out if x['digit']==digit) for digit in range(1,6))
(E/'source-section-identity-audit.json').write_text(json.dumps({'checks':out,'ambiguousSections':sum(x['ambiguous'] for x in out),'acceptedOwnDigitSections':sum(x['plausibleOwnDigitLoopCount']==1 for x in out),'zeroMeansRejectedNotNearestFallback':True,'notProviderBoneOrClinicalLandmark':True,'sourceUnmodified':True},indent=2)+'\n');print('unique own-digit sections',sum(x['plausibleOwnDigitLoopCount']==1 for x in out),'ambiguous 0')
