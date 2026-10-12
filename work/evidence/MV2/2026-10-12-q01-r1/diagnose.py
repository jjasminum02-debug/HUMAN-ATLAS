import sys,json
from pathlib import Path
import numpy as np
R=Path.cwd(); E=R/'work/evidence/MV2/2026-10-12-q01-r1'
sys.path[:0]=[str(R/'work/tools'),str(R/'work/evidence/T66/serial-completion-2026-10-02/unit-01')]
from verify_glb_interpolation import read_glb,channel_data,node_positions
from author_t66_family_motion import deform
out=[]
for side in ['left','right']:
 p=json.loads((R/f'work/evidence/T66/priority-integration-2026-10-05/adopted-knee-{side}/input.json').read_text()); g=json.loads((R/f'work/evidence/T66/priority-integration-2026-10-05/adopted-knee-{side}/geometry-record.json').read_text())
 e=next(e for e in p['members'] if e['role']=='deforming_muscle_surface'); m=next(m for m in g['surfaceMetrics'] if m['sourceKey']==e['sourceKey']); raw,d,b=read_glb(R/f'atlas-data/assets/motion/t66-priority-s05-{side}-knee/motion.glb');tr=channel_data(d,b);ni=next(i for i,n in enumerate(d['nodes']) if n['extras']['sourceKey']==e['sourceKey']);w=node_positions(d,b,tr,ni,0); f=node_positions(d,b,tr,ni,3);weights=np.array(m['authoredFinalWeights']);a=np.array(e['weights']);fam=p['family']; pivot=np.array(fam['pivotMetres']);ax=np.array(fam['axis'])
 model=deform(w,pivot,ax,fam['endDegrees'],1,weights,p['deformationMethod']);bins=[]
 for lo,hi in zip(np.linspace(w[:,1].min(),w[:,1].max(),8)[:-1],np.linspace(w[:,1].min(),w[:,1].max(),8)[1:]):
  ids=np.flatnonzero((w[:,1]>=lo)&(w[:,1]<=hi));bins.append({'yMetres':[lo,hi],'vertices':len(ids),'meanInputWeight':float(a[ids].mean()),'meanFinalWeight':float(weights[ids].mean()),'maxDisplacementMm':float(np.linalg.norm(f[ids]-w[ids],axis=1).max()*1000),'maxAnteriorMm':float((f[ids,2]-w[ids,2]).max()*1000)})
 print(side,'pins',m['contactPins'],'bins',bins)
 out.append({'side':side,'sourceKey':e['sourceKey'],'clip':p['clipId'],'frame':fam['frameId'],'units':'m','pose':fam['referencePoseId'],'pivot':pivot.tolist(),'axis':ax.tolist(),'angle':fam['endDegrees'],'nodeMatrix':d['nodes'][ni]['matrix'],'sourceBounds':[w.min(0).tolist(),w.max(0).tolist()],'weightsBins':bins,'finalWeightDeformVsEmittedMaxMm':float(np.linalg.norm(model-f,axis=1).max()*1000),'vectorCorrectives':m['vectorCorrectives'],'contactPins':m['contactPins'],'fixedMaskMaxErrorMm':float(np.linalg.norm(f[e['fixedVertexIndices']]-w[e['fixedVertexIndices']],axis=1).max()*1000),'weightCorrections':m['weightCorrections'],'phaseSamples':len(tr[(ni,'weights')][0]),'interpolation':'LINEAR one-hot adjacent morphs; no overshoot spline','actionDirection':'reverse; bent clip-end is preparation, extension ends at source rest'})
(E/'diagnosis-numeric.json').write_text(json.dumps(out,indent=2)+'\n')
