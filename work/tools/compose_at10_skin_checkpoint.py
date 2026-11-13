"""Keep independent local improvements, reject failed foot/contact trials.

This checkpoint remains ineligible. Composition does not constitute acceptance.
"""
from pathlib import Path
import argparse,json,numpy as np
R=Path(__file__).resolve().parents[2];p=argparse.ArgumentParser();p.add_argument('--evidence',required=True);p.add_argument('--revision',default='r22');a=p.parse_args();E=R/a.evidence;B=R/'work/evidence/AT10/2026-10-13-skin-fit-r1'
d=json.loads((B/'candidates/fit-r9.json').read_text());r14=json.loads((E/'candidates/fit-r14-base.json').read_text());r19=json.loads((E/'candidates/fit-r19.json').read_text());src=np.array(d['sourceVertices']);v=np.array(d['positions']);v14=np.array(r14['positions']);v19=np.array(r19['positions']);masks={}
head=(src[:,1]>.54)&(np.abs(src[:,0])<.16);hip=(src[:,1]>-.40)&(src[:,1]<.08)&(np.abs(src[:,0])<.225);v[head|hip]=v19[head|hip];masks['r19-head-neck']=head;masks['r19-pelvis-medial-thigh']=hip
for side,sign in [('left',1),('right',-1)]:
 f=d['articulatedFrames'][side];s=np.array(f['sourceWrist']);ps=np.array(f['sourcePalmFrame']);progress=(src-s)@ps[:,0];mask=(src[:,0]*sign>.37)&(progress>-.065);v[mask]=v14[mask];masks['r14-continuous-hand-'+side]=mask
d['positions']=v.tolist();d['candidateRevision']=a.revision;d['sourceReturnVertices']=r19['sourceReturnVertices'];d['vertexRegions']=r19['vertexRegions'];d['fitAcceptancePassed']=False;d['learnerEligible']=False
d['checkpointComposition']={'base':'r9','sourceMaskPolicy':'unchanged source coordinates and original IDs, explicit anatomical source cohorts','patches':{key:{'sourceVertexIds':np.array(d['originalVertexIds'])[mask].tolist(),'appliedFrom':key.split('-')[0]} for key,mask in masks.items()},'continuousHandRecipe':[p for p in r14['continuousPatchRecipe'] if 'hand' in p['id']], 'headHipRecipe':[p for p in r19['patchEnvelopeRecipe'] if p['id'].startswith(('pelvis','outer-head','source-pinna'))], 'failedFootTrials':['r14-base','r16','r18','r19','r20','r21'],'feetPreservedFrom':'r9','localFitPassed':False,'rejectedContactTrials':['r12','r13','r14','r15'],'scope':'review checkpoint, not final fitted skin'}
(E/f'candidates/fit-{a.revision}.json').write_text(json.dumps(d,separators=(',',':')))
(E/f'composition-{a.revision}.json').write_text(json.dumps(d['checkpointComposition'],separators=(',',':'))+'\n')
print('CHECKPOINT',a.revision,'preserved source topology; no eligibility')
