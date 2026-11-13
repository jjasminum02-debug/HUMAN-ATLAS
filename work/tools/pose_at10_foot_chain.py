"""Source/native articulated foot correspondence, preserving source toe shape.

Uses the actual 3/4-handle toe chains. Each bone frame preserves transverse
shape; source-topology harmonic weights blend digit poses across shared webs.
No native/source file is edited and this does not grant placement acceptance.
"""
from pathlib import Path
import argparse,json,sys
import numpy as np
R=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--evidence',required=True);p.add_argument('--revision',required=True);p.add_argument('--side',choices=['left','right'],required=True);a=p.parse_args()
E=R/a.evidence;B=R/'work/evidence/AT10/2026-10-14-skin-fit-r5';load=lambda p:json.loads(p.read_text())
d=load(B/'candidates/fit-r41.json');fields=load(B/'surface-bands-r52.json') if a.side=='right' else load(E/'surface-bands-left-chain.json');f=next(x for x in fields['patches'] if x['patch']=='foot-'+a.side)
s=np.array(d['sourceVertices']);v=np.array(d['positions']);initial=v.copy();ids=np.array(f['sourceVertices']);roots=np.array([x['sourceVertex'] for x in f['sharedBoundary']]);lookup={int(x):i for i,x in enumerate(ids)}
ctrl={x['id']:x for x in f['nativeJointControls']};letter='r' if a.side=='right' else 'l';tri=np.array([[ff['derivedVertices'][0],ff['derivedVertices'][j],ff['derivedVertices'][j+1]] for ff in d['faces'] for j in range(1,len(ff['derivedVertices'])-1)])
edges=np.array(sorted({tuple(sorted((int(x),int(y)))) for tt in tri for x,y in zip(tt,np.roll(tt,-1)) if int(x) in lookup and int(y) in lookup}));local=np.array([[lookup[int(x)] for x in e] for e in edges]);degree=np.bincount(local.ravel(),minlength=len(ids))
def frame(axis,up):
 axis=np.array(axis);axis/=np.linalg.norm(axis);up=np.array(up,dtype=float);up-=axis*(up@axis);up/=np.linalg.norm(up);return np.column_stack([np.cross(up,axis),up,axis])
def transform(points,sa,sb,ta,tb):
 sa,sb,ta,tb=map(np.array,[sa,sb,ta,tb]);sf=frame(sb-sa,[0,1,0]);tf=frame(tb-ta,[0,1,0]);local=(points-sa)@sf;local[:,2]*=np.linalg.norm(tb-ta)/np.linalg.norm(sb-sa);return local@tf.T+ta
ankle=ctrl[f'joint-{letter}-ankle'];mtp=[ctrl[f'joint-{letter}-toe-{i}-1'] for i in range(1,6)];sroot=np.mean([x['source'] for x in mtp],axis=0);troot=np.mean([x['target'] for x in mtp],axis=0)
base=transform(s[ids],ankle['source'],sroot,ankle['target'],troot)
seeds=np.full(len(ids),-1,int);seeds[s[ids,2]<sroot[2]-.025]=0;seeds[[lookup[int(i)] for i in roots]]=0
digit_maps=[];chain_audit=[]
for digit in range(1,6):
 chain=[ctrl[f'joint-{letter}-toe-{digit}-{i}'] for i in range(1,4 if digit==1 else 5)];maps=[];distances=[]
 for ca,cb in zip(chain[:-1],chain[1:]):
  sa=np.array(ca.get('sourceOriginalHelperM',ca['source']));sb=np.array(cb.get('sourceOriginalHelperM',cb['source']));axis=sb-sa;u=(s[ids]-sa)@axis/(axis@axis);near=sa+np.clip(u,0,1)[:,None]*axis;dist=np.linalg.norm(s[ids]-near,axis=1)
  distances.append(dist);maps.append(transform(s[ids],sa,sb,ca['target'],cb['target']))
 D=np.array(distances).T;W=np.exp(-(D-D.min(1)[:,None])**2/(2*.006**2));W/=W.sum(1)[:,None];digit_maps.append(np.einsum('nk,nkj->nj',W,np.array(maps).transpose(1,0,2)))
 # Distal single-digit shaft seeds; ambiguous proximal/web vertices remain harmonic unknowns.
 sa=np.array(chain[1].get('sourceOriginalHelperM',chain[1]['source']));sb=np.array(chain[-1].get('sourceOriginalHelperM',chain[-1]['source']));axis=sb-sa;u=(s[ids]-sa)@axis/(axis@axis);distance=np.linalg.norm(s[ids]-(sa+np.clip(u,0,1)[:,None]*axis),axis=1)
 seed=(distance<.009)&(u>-.05);seeds[seed]=digit
 chain_audit.append({'digit':digit,'actualSourceHandles':[c['id'] for c in chain],'nativeReferences':[c['nativeReferences'] for c in chain],'sourceSeedOriginalVertexIds':[d['originalVertexIds'][int(i)] for i in ids[seed]]})
fixed=np.flatnonzero(seeds>=0);free=np.flatnonzero(seeds<0);L=np.diag(degree.astype(float));L[local[:,0],local[:,1]]=-1;L[local[:,1],local[:,0]]=-1
weights=np.zeros((len(ids),6));weights[fixed,seeds[fixed]]=1
weights[free]=np.linalg.solve(L[np.ix_(free,free)],-L[np.ix_(free,fixed)]@weights[fixed]);assert weights.min()>-1e-9;assert np.abs(weights.sum(1)-1).max()<1e-8
mapped=np.einsum('nk,nkj->nj',weights,np.array([base]+digit_maps).transpose(1,0,2))
# Source ankle-to-calf collar preserves both positions and tangent at the shared boundary.
source_ankle=ankle['source'][1];collar_top=np.min(s[roots,1]);u=np.clip((collar_top-s[ids,1])/max(collar_top-source_ankle,.01),0,1);blend=u*u*(3-2*u);v[ids]=v[ids]*(1-blend[:,None])+mapped*blend[:,None];v[roots]=initial[roots]
d.update(positions=v.tolist(),candidateRevision=a.revision,fitAcceptancePassed=False,learnerEligible=False)
out=E/f'candidates/fit-{a.revision}.json';assert not out.exists();out.write_text(json.dumps(d,separators=(',',':')))
recipe={'revision':a.revision,'side':a.side,'method':'actual toe chain local frames + source-topology harmonic digit weights + C1 calf collar','base':'r41','sourceFieldInput':'surface-bands-r52.json','sourceUnitVertices':ids.tolist(),'sourceSharedBoundary':roots.tolist(),'digitChains':chain_audit,'weightRows':weights.tolist(),'collarWeight':blend.tolist(),'minimumWeight':float(weights.min()),'maximumWeightSumError':float(np.abs(weights.sum(1)-1).max()),'outsideUnitUnchanged':bool(np.array_equal(v[~np.isin(np.arange(len(v)),ids)],initial[~np.isin(np.arange(len(v)),ids)])),'geometryAcceptance':False,'clinicalLandmarkApproval':False,'learnerEligible':False}
(E/f'articulated-foot-{a.revision}.json').write_text(json.dumps(recipe,indent=2)+'\n');print({'revision':a.revision,'seedCounts':np.bincount(seeds[fixed],minlength=6).tolist(),'minimumWeight':recipe['minimumWeight'],'outsideUnitUnchanged':recipe['outsideUnitUnchanged']})
