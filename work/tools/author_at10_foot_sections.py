"""Author actual foot surface/section pairs with original edge/facet ancestry.

Bone/helper roles select sections; closed surface loops, not digit Voronoi
boundaries, provide dorsal/plantar/side bands. These remain QA proposals.
"""
from pathlib import Path
import argparse,json,sys,hashlib
import numpy as np
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'work/tools'))
from at10_surface_sections import section_loops,ordered_samples
p=argparse.ArgumentParser();p.add_argument('--evidence',required=True);p.add_argument('--side',choices=['right','left'],required=True);p.add_argument('--revision',required=True);a=p.parse_args()
E=R/a.evidence;B=R/'work/evidence/AT10/2026-10-14-skin-fit-r5';load=lambda p:json.loads(p.read_text())
d=load(B/'candidates/fit-r41.json');s=np.array(d['sourceVertices']);v=np.array(d['positions']);t=np.array([[f['derivedVertices'][0],f['derivedVertices'][j],f['derivedVertices'][j+1]] for f in d['faces'] for j in range(1,len(f['derivedVertices'])-1)])
f=next(x for x in load(B/'surface-bands-r52.json')['patches'] if x['patch']=='foot-'+a.side) if a.side=='right' else next(x for x in load(E/'surface-bands-left-chain.json')['patches'] if x['patch']=='foot-left')
controls={c['id']:c for c in f['nativeJointControls']};letter='r' if a.side=='right' else 'l';ids=np.array(f['sourceVertices']);mask=np.zeros(len(v),bool);mask[ids]=True;faces=np.flatnonzero(mask[t].all(1))
native=load(R/'work/evidence/AT10/2026-10-13-skin-fit-r1/native-surfaces-r1.json');key=next(k for k,x in native.items() if x['name']=='Crural fascia' and x['side']==a.side);nv=np.array(native[key]['v']);nt=np.array(native[key]['t']);sign=1 if np.einsum('ij,ij->i',nv[nt[:,0]],np.cross(nv[nt[:,1]],nv[nt[:,2]])).sum()>0 else -1
sections=[]
def add(name,so,to,sn,tn,up,role,refs):sections.append({'id':name,'sourceOrigin':np.array(so),'targetOrigin':np.array(to),'sourceNormal':np.array(sn),'targetNormal':np.array(tn),'up':np.array(up),'role':role,'references':refs})
for digit in range(1,6):
    chain=[controls[f'joint-{letter}-toe-{digit}-{i}'] for i in range(1,4 if digit==1 else 5)]
    for part,(ca,cb) in enumerate(zip(chain[:-1],chain[1:])):
        # MTP-side merged loops are deliberately not called independent digit contours.
        for frac in [.35,.7]:
            so=np.array(ca['source'])*(1-frac)+np.array(cb['source'])*frac;to=np.array(ca['target'])*(1-frac)+np.array(cb['target'])*frac
            add(f'toe-{digit}-segment-{part}-{frac}',so,to,np.array(cb['source'])-ca['source'],np.array(cb['target'])-ca['target'],[0,1,0],f'digit {digit} dorsal/medial/plantar/lateral ring on actual shaft segment',[ca['id'],cb['id']])
ankle=controls[f'joint-{letter}-ankle'];source_mtp=np.mean([controls[f'joint-{letter}-toe-{i}-1']['source'] for i in range(1,6)],axis=0);target_mtp=np.mean([controls[f'joint-{letter}-toe-{i}-1']['target'] for i in range(1,6)],axis=0)
for fraction in [.15,.35,.55,.75,.92]:
    so=np.array(ankle['source'])*(1-fraction)+source_mtp*fraction;to=np.array(ankle['target'])*(1-fraction)+target_mtp*fraction
    add('midfoot-'+str(fraction),so,to,[0,0,1],[0,0,1],[0,1,0],'connected dorsal/plantar midfoot section from ankle to observed MTP cap axis',[ankle['id'],'actual five MTP cap controls'])
rows=[];audit=[];loopsout=[]
for item in sections:
    sl,so=section_loops(s,t,item['sourceOrigin'],item['sourceNormal'],faces);nl,no=section_loops(nv,nt,item['targetOrigin'],item['targetNormal'])
    def choose(loops,origin):
        return min(loops,key=lambda loop:np.linalg.norm(np.array([n['pointM'] for n in loop['nodes']]).mean(0)-origin)) if loops else None
    source=choose(sl,item['sourceOrigin']);target=choose(nl,item['targetOrigin'])
    entry={'id':item['id'],'role':item['role'],'sourceLoops':len(sl),'nativeLoops':len(nl),'sourceOpen':so,'nativeOpen':no,'references':item['references'],'homologyApproved':False}
    if not source or not target:entry['status']='missing_closed_surface';audit.append(entry);continue
    ss=ordered_samples(source,s,t,item['sourceOrigin'],item['sourceNormal'],item['up']);ns=ordered_samples(target,nv,nt,item['targetOrigin'],item['targetNormal'],item['up'])
    entry.update(status='addressed_surface_pair_proposal',sourceRingLengthM=ss[0]['ringLengthM'],nativeRingLengthM=ns[0]['ringLengthM']);audit.append(entry)
    # Very large loops at a proximal fused toe are retained as explicit exceptions.
    if item['id'].startswith('toe-') and (ss[0]['ringLengthM']>.10 or ns[0]['ringLengthM']>.11):entry['status']='merged_digit_loop_not_used';continue
    for src,tar in zip(ss,ns):
        ni=tar['triangle'];normal=sign*np.cross(nv[nt[ni,1]]-nv[nt[ni,0]],nv[nt[ni,2]]-nv[nt[ni,0]]);normal/=np.linalg.norm(normal);targetpoint=np.array(tar['pointM'])+normal*.001
        si=src['triangle'];rows.append({'sectionId':item['id'],'role':item['role'],'sourceTriangle':si,'sourceOriginalVertexIds':[d['originalVertexIds'][int(i)] for i in t[si]],'sourceObjFace':d['faces'][si//2]['sourceFace'],'sourceBarycentric':src['barycentric'],'sourcePointM':src['pointM'],'nativeSourceKey':key,'nativeTriangle':ni,'nativeBarycentric':tar['barycentric'],'nativePointM':tar['pointM'],'nativeNormal':normal.tolist(),'targetPointM':targetpoint.tolist(),'arcFraction':src['arcFraction'],'modelClearanceM':.001,'clinicalLandmarkApproval':False})
    loopsout.append({'id':item['id'],'source':source,'native':target})
payload={'revision':a.revision,'side':a.side,'unit':'m','frame':'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR','poseId':d.get('poseId','za-c7010a9-9f08a17ea011-frame0-static'),'sourceInputs':d['inputHashes'],'nativeSourceKey':key,'sourceFieldInput':'surface-bands-r52.json','sections':audit,'pairs':rows,'orderedLoops':loopsout,'homologyApproved':False,'geometryAcceptance':False,'learnerEligible':False,'meaning':'AI-authored addressed surface correspondence proposals; actual shape/collision/volume/visual checks required'}
path=E/f'{a.revision}.json';assert not path.exists();path.write_text(json.dumps(payload,indent=2)+'\n');print({'sections':len(audit),'pairs':len(rows),'dispositions':[(x['id'],x['status']) for x in audit]},flush=True)
