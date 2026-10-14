"""Ordered, addressed interdigit chart boundaries for local fit investigation.

Bone axes delimit the two adjacent digit charts. Their shared surface curve is
traced through source/native facets, rather than assigning unrelated nearest
vertices independently. These are AI-authored model guides, not anatomical or
acupoint landmark approval. The output must be visually and geometrically checked.
"""
from pathlib import Path
import json, collections, argparse
import numpy as np
R=Path(__file__).resolve().parents[2];E=R/'work/evidence/AT10/2026-10-14-skin-fit-r5'
p=argparse.ArgumentParser();p.add_argument('--revision',required=True);p.add_argument('--pairwise',action='store_true');p.add_argument('--candidate',default='r50');a=p.parse_args()
load=lambda p:json.loads(p.read_text())
d=load(E/f'candidates/fit-{a.candidate}.json');f=load(E/f'surface-bands-{a.candidate}.json')['patches'][0]
c={x['id']:x for x in f['nativeJointControls']}
source=np.array(d['sourceVertices']);skin_tri=np.array([[z['derivedVertices'][0],z['derivedVertices'][j],z['derivedVertices'][j+1]] for z in d['faces'] for j in range(1,len(z['derivedVertices'])-1)])
native=load(R/'work/evidence/AT10/2026-10-13-skin-fit-r1/native-surfaces-r1.json');key='ZA-c7010a9-97a5556947c926b0b5483338'
nv=np.array(native[key]['v']);nt=np.array(native[key]['t']);unit=set(f['sourceVertices'])
st_ids=np.flatnonzero(np.array([all(int(i) in unit for i in tri) for tri in skin_tri]));st=skin_tri[st_ids]
def axes(space,digit):
    count=4 if f'joint-r-toe-{digit}-4' in c else 3
    return np.array([c[f'joint-r-toe-{digit}-{j}'].get('sourceOriginalHelperM',c[f'joint-r-toe-{digit}-{j}']['source'])
        if space=='source' else c[f'joint-r-toe-{digit}-{j}']['target'] for j in range(1,count+1)])
def distances(points,space):
    distances=[]
    for digit in range(1,6):
        joints=axes(space,digit);options=[]
        for a,b in zip(joints[:-1],joints[1:]):
            u=np.clip((points-a)@(b-a)/np.dot(b-a,b-a),0,1)
            options.append(np.linalg.norm(points-a-u[:,None]*(b-a),axis=1)**2)
        distances.append(np.min(options,axis=0))
    return np.array(distances).T
def curve(points,tri,tri_ids,space,digit):
    dist=distances(points,space);owner=dist.argmin(1)+1
    if a.pairwise:owner=np.where(dist[:,digit-1]<dist[:,digit],digit,digit+1)
    roots=(axes(space,digit)[0]+axes(space,digit+1)[0])/2
    tips=(axes(space,digit)[-1]+axes(space,digit+1)[-1])/2
    axis=tips-roots;axis/=np.linalg.norm(axis)
    nodes={};address={};graph=collections.defaultdict(set)
    for ti,tt in enumerate(tri):
        lab=set(owner[tt]);cross=[]
        if not {digit,digit+1}<=lab:continue
        for aa,bb in zip(tt,np.roll(tt,-1)):
            if set([owner[aa],owner[bb]])!={digit,digit+1}:continue
            edge=tuple(sorted((int(aa),int(bb))))
            if edge not in nodes:
                lo,hi=0.,1.;va,vb=points[edge[0]],points[edge[1]]
                sign=(dist[edge[0],digit-1]-dist[edge[0],digit])>0
                for _ in range(24):
                    mid=(lo+hi)*.5;p=va*(1-mid)+vb*mid;dd=distances(p[None],space)[0]
                    if (dd[digit-1]-dd[digit]>0)==sign:lo=mid
                    else:hi=mid
                u=(lo+hi)*.5;point=va*(1-u)+vb*u
                if np.dot(point-roots,axis)<-.007:continue
                nodes[edge]=point;address[edge]={'edgeVertices':list(edge),'weights':[1-u,u],'triangle':int(tri_ids[ti]),'pointM':point.tolist()}
            cross.append(edge)
        if len(cross)==2:
            graph[cross[0]].add(cross[1]);graph[cross[1]].add(cross[0])
    # Connected curve containing the most distal shared-chart point.
    assert graph,(space,digit)
    tip=max(graph,key=lambda k:np.dot(nodes[k]-roots,axis))
    component=set([tip]);stack=[tip]
    while stack:
        for x in graph[stack.pop()]:
            if x not in component:component.add(x);stack.append(x)
    endpoints=[x for x in component if len(graph[x]&component)==1]
    start=max(endpoints or list(component),key=lambda x:nodes[x][1])
    ordered=[];previous=None;current=start
    while current not in ordered:
        ordered.append(current);next_nodes=[x for x in graph[current]&component if x!=previous]
        if not next_nodes:break
        previous,current=current,sorted(next_nodes)[0]
    tip_index=ordered.index(tip) if tip in ordered else -1
    return {'nodes':[address[x] for x in ordered],'tipIndex':tip_index,'componentNodes':len(component),
        'branchNodes':sum(len(graph[x]&component)>2 for x in component),'orientation':'dorsal-positive-height endpoint toward plantar endpoint',
        'rootMidpointM':roots.tolist(),'distalAxis':axis.tolist()}
rows=[]
for digit in range(1,5):
    sc=curve(source,st,st_ids,'source',digit);nc=curve(nv,nt,np.arange(len(nt)),'target',digit)
    rows.append({'betweenDigits':[digit,digit+1],'sourceCurve':sc,'nativeCurve':nc,'nativeSourceKey':key,
        'sourceOriginalVertexIdsRetained':True,'nativeFrameAlreadyWorldMetres':True,'homologyApproved':False,'placementVerified':False,
        'meaning':'AI-authored adjacent-digit chart boundary, pending actual surface inspection; not an observed crease or acupoint'})
    print(digit,{'sourceNodes':len(sc['nodes']),'sourceTipIndex':sc['tipIndex'],'nativeNodes':len(nc['nodes']),'nativeTipIndex':nc['tipIndex'],'branches':[sc['branchNodes'],nc['branchNodes']]})
out={'revision':a.revision,'sourceCandidate':a.candidate,'pairwiseBisector':a.pairwise,'curves':rows,'anatomicalLandmarkApproved':False,'learnerEligible':False}
path=E/f'{a.revision}.json';assert not path.exists();path.write_text(json.dumps(out,indent=2)+'\n')
