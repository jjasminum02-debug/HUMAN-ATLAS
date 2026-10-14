"""Pair the frozen ordered toe-web branches using actual facet ancestry.

Source/native graph topology and dorsal/web/plantar order must already agree.
This writes an AI model-surface guide, never learner or acupoint coordinates.
"""
from pathlib import Path
import json,numpy as np
R=Path(__file__).resolve().parents[2];E=R/'work/evidence/AT10/2026-10-14-skin-fit-r5'
load=lambda p:json.loads(p.read_text())
curves=load(E/'foot-webs-r3.json');d=load(E/'candidates/fit-r52.json');fields=load(E/'surface-bands-r52.json')['patches'][0]
source=np.array(d['sourceVertices']);st=np.array([[f['derivedVertices'][0],f['derivedVertices'][j],f['derivedVertices'][j+1]] for f in d['faces'] for j in range(1,len(f['derivedVertices'])-1)])
native=load(R/'work/evidence/AT10/2026-10-13-skin-fit-r1/native-surfaces-r1.json');key=curves['curves'][0]['nativeSourceKey'];nv=np.array(native[key]['v']);nt=np.array(native[key]['t'])
triangle_index={tuple(sorted(map(int,t))):i for i,t in enumerate(nt)}
source_index={tuple(sorted(map(int,t))):i for i,t in enumerate(st)}
def branch_nodes(curve,side):
    tip=curve['tipIndex'];assert 0<tip<len(curve['nodes'])-1 and curve['branchNodes']==0
    return curve['nodes'][:tip+1][::-1] if side=='dorsal' else curve['nodes'][tip:]
def sample(nodes,fraction):
    p=np.array([x['pointM'] for x in nodes]);dist=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))]
    length=min(.012,dist[-1]);at=fraction*length;i=min(np.searchsorted(dist,at,side='right')-1,len(p)-2);i=max(i,0)
    u=(at-dist[i])/max(dist[i+1]-dist[i],1e-15)
    weights={}
    for node,w in [(nodes[i],1-u),(nodes[i+1],u)]:
        for vi,q in zip(node['edgeVertices'],node['weights']):weights[vi]=weights.get(vi,0)+q*w
    weights={k:v for k,v in weights.items() if abs(v)>1e-12}
    return weights,(1-u)*p[i]+u*p[i+1],length
rows=[]
for curve in curves['curves']:
    for branch in ['dorsal','plantar']:
        sn=branch_nodes(curve['sourceCurve'],branch);nn=branch_nodes(curve['nativeCurve'],branch)
        for fraction in np.linspace(0,1,7):
            sw,sp,sl=sample(sn,float(fraction));nw,np_,nl=sample(nn,float(fraction))
            # Curve segment lies in the shared triangle of its two edge nodes.
            if len(nw)==2:
                ni=next(i for i,t in enumerate(nt) if set(nw)<=set(t))
            else:ni=triangle_index[tuple(sorted(nw))]
            if len(sw)==2:si=next(i for i,t in enumerate(st) if set(sw)<=set(t))
            else:si=source_index[tuple(sorted(sw))]
            normal=np.cross(nv[nt[ni,1]]-nv[nt[ni,0]],nv[nt[ni,2]]-nv[nt[ni,0]]);normal/=np.linalg.norm(normal)
            # Outward orientation from the addressed adjacent native bone axes.
            nearest=[]
            for digit in curve['betweenDigits']:
                cs=[c for c in fields['nativeJointControls'] if c['id'].startswith(f'joint-r-toe-{digit}-')]
                centers=np.array([x['target'] for x in cs])
                for a,b in zip(centers[:-1],centers[1:]):
                    u=np.clip(np.dot(np_-a,b-a)/np.dot(b-a,b-a),0,1);q=a+u*(b-a);nearest.append((np.linalg.norm(np_-q),q))
            _,bone_point=min(nearest,key=lambda x:x[0]);flipped=np.dot(normal,np_-bone_point)<0
            if flipped:normal=-normal
            target=np_+normal*.0005
            rows.append({'sourceLogicalVertices':list(sw),'sourceWeights':list(sw.values()),'sourceOriginalVertexIds':[d['originalVertexIds'][int(i)] for i in sw],
                'sourceTriangle':si,'sourceObjFace':d['faces'][si//2]['sourceFace'],'sourcePointM':sp.tolist(),
                'nativeSourceKey':key,'nativeTriangle':ni,'nativeTriangleVertices':nt[ni].tolist(),'nativeFacetWeights':[nw.get(int(i),0) for i in nt[ni]],
                'nativePointM':np_.tolist(),'targetPointM':target.tolist(),'nativeOutwardNormal':normal.tolist(),'normalOrientedByAdjacentBoneAxes':bool(flipped),
                'modelSkinMarginM':.0005,'betweenDigits':curve['betweenDigits'],'branch':branch,'arcFraction':float(fraction),
                'sourceBranchLengthM':sl,'nativeBranchLengthM':nl,'side':'right','frame':'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR','unit':'m',
                'poseId':'za-c7010a9-9f08a17ea011-frame0-static','pointAnatomyMeaningApproved':False,'meaning':'authored static surface-pair guide on traced adjacent-digit chart boundary'})
out={'sourceCurves':'foot-webs-r3.json','sourceCandidate':'r52','guideCount':len(rows),'guides':rows,'learnerEligible':False,'acupointsAdded':0,'requiresVisualAndGeometryQa':True}
path=E/'foot-surface-guides-r1.json';assert not path.exists();path.write_text(json.dumps(out,indent=2)+'\n');print({'guides':len(rows),'allPointMeaningsUnapproved':True})
