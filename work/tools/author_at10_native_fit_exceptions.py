"""Freeze addressed forefoot fascia reference exceptions explicitly authorized by user.

Native source geometry is unchanged. This identifies only a connected distal
template sheet spanning actual digit axes, never all fascia/accessories. Full
raw native and self QA is still required and no skin is approved here.
"""
from pathlib import Path
import argparse,json,hashlib,collections
import numpy as np
R=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--evidence',required=True);p.add_argument('--side',choices=['right','left'],required=True);p.add_argument('--revision',required=True);a=p.parse_args()
E=R/a.evidence;B=R/'work/evidence/AT10/2026-10-14-skin-fit-r5';load=lambda p:json.loads(p.read_text())
field=load(B/'surface-bands-r52.json') if a.side=='right' else load(E/'surface-bands-left-chain.json');f=next(x for x in field['patches'] if x['patch']=='foot-'+a.side);letter='r' if a.side=='right' else 'l'
ctrl={x['id']:x for x in f['nativeJointControls']};roots=np.array([ctrl[f'joint-{letter}-toe-{d}-1']['target'] for d in range(1,6)]);tips=np.array([ctrl[f'joint-{letter}-toe-{d}-{3 if d==1 else 4}']['target'] for d in range(1,6)]);axis=(tips-roots).mean(0);axis/=np.linalg.norm(axis)
native=load(R/'work/evidence/AT10/2026-10-13-skin-fit-r1/native-surfaces-r1.json');key=next(k for k,x in native.items() if x['name']=='Crural fascia' and x['side']==a.side);item=native[key];v=np.array(item['v']);t=np.array(item['t']);plane=float((roots@axis).min());allowed=(v[t].mean(1)@axis)>plane
dist=[]
for root,tip in zip(roots,tips):
 d=tip-root;u=np.clip((v-root)@d/(d@d),0,1);dist.append(np.linalg.norm(v-root-u[:,None]*d,axis=1))
owner=np.array(dist).argmin(0);seeds=np.flatnonzero(allowed&(np.max(owner[t],axis=1)!=np.min(owner[t],axis=1)))
edge_faces=collections.defaultdict(list)
for fi,tt in enumerate(t):
 for x,y in zip(tt,np.roll(tt,-1)):edge_faces[tuple(sorted([int(x),int(y)]))].append(fi)
graph=collections.defaultdict(set)
for faces in edge_faces.values():
 for fi in faces:graph[fi].update(f for f in faces if f!=fi)
selected=set(map(int,seeds));stack=list(selected)
while stack:
 for fi in graph[stack.pop()]:
  if allowed[fi] and fi not in selected:selected.add(fi);stack.append(fi)
selected=sorted(selected);assert len(selected)>0 and len(selected)<len(t)//2
record={'sourceKey':key,'sourceName':item['name'],'side':a.side,'geometrySha256':hashlib.sha256(v.astype('<f8').tobytes()+t.astype('<u4').tobytes()).hexdigest(),'triangleIds':selected,'nativeReferenceTriangles':len(t),'crossDigitSeedTriangleIds':seeds.tolist(),'selection':'connected distal template sheet containing cross-digit facet seeds; proximal boundary is the minimum addressed five-MTP-cap axial plane','boundaryPlane':{'axis':axis.tolist(),'offsetM':plane,'sourceControls':[ctrl[f'joint-{letter}-toe-{i}-1'] for i in range(1,6)]},'disposition':'simplified_fascia_forefoot_template_not_homologous_individual_skin','reason':'Actual native-only view has a continuous forefoot sleeve. Ordered native sections merge digit axes; no observed individual toe web is supplied by this sheet. Not removed because of default layer-OFF.','sourceEdited':False,'allOtherFacetsRemainInFit':True,'skinGeometryApproval':False}
out={'schemaVersion':1,'revision':a.revision,'userAuthorized':True,'authorization':'2026-10-14 user: 주소별 근거를 남겨 단순화된 fascia 구역을 정합 기준에서 분리','rawFullReferenceQaRequired':True,'frameId':'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR','poseId':'za-c7010a9-9f08a17ea011-frame0-static','unit':'m','facets':[record],'notClinicalBoundary':True,'learnerEligible':False}
path=E/f'{a.revision}.json';assert not path.exists();path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print({'source':key,'excludedFacets':len(selected),'retainedFacets':len(t)-len(selected),'crossDigitSeeds':len(seeds),'rawFullReferenceQaRequired':True})
