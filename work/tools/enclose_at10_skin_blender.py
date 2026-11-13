"""EXPERIMENTAL unselected constraint method; geometry validation failed; no learner use."""
from pathlib import Path
import json,sys,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];E=R/'work/evidence/AT10/2026-10-13-skin-fit-r1'
d=json.loads((E/'candidates/fit-r9.json').read_text());v=np.array(d['positions']);source=np.array(d['sourceVertices']);faces=[f['derivedVertices'] for f in d['faces']];t=np.array([[f[0],f[i],f[i+1]] for f in faces for i in range(1,len(f)-1)]);regions=np.array(d['vertexRegions']);adj=[set() for _ in v]
for f in faces:
    for a,b in zip(f,f[1:]+f[:1]):adj[a].add(b);adj[b].add(a)
# Original source inner oral/eyelid returns are retained, independently ineligible
# for exterior-skin point anchoring. Their source IDs are an inspectable cohort.
snorm=np.zeros_like(source)
for a,b,c in t:
    n=np.cross(source[b]-source[a],source[c]-source[a]);snorm[[a,b,c]]+=n
inner=(source[:,1]>.59)&(source[:,1]<.725)&(source[:,2]>.1)&(snorm[:,2]<-1e-8)
inner_tri=inner[t].all(1)
native=json.loads((E/'native-surfaces-r1.json').read_text());points=[]
for s in native.values():
    p=np.array(s['v']);tri=np.array(s['t']);points.extend(p[::4].tolist());points.extend(p[tri[::12]].mean(1).tolist())
points=np.array(points);print('constraint samples',len(points),flush=True);iterations=[];initial=v.copy()
ctrl={c['id']:c for c in json.loads((E/'native-controls-r2.json').read_text())['controls']}
def closest_center(p,pairs):
    options=[]
    for aa,bb in pairs:
        a=np.array(ctrl[aa]['target']);b=np.array(ctrl[bb]['target']);u=np.clip(np.dot(p-a,b-a)/np.dot(b-a,b-a),0,1);c=a+u*(b-a);options.append((np.linalg.norm(p-c),c))
    return min(options,key=lambda x:x[0])[1]
dirs=[]
for i,p in enumerate(v):
    side='left' if source[i,0]>0 else 'right';letter='l' if side=='left' else 'r';r=regions[i]
    if r.startswith('hand'):
        pairs=[(f'joint-{letter}-hand',f'joint-{letter}-finger-{di}-1') for di in range(1,6)]+[(f'joint-{letter}-finger-{di}-{pa}',f'joint-{letter}-finger-{di}-{pa+1}') for di in range(1,6) for pa in range(1,4)];c=closest_center(p,pairs)
    elif r.startswith('foot'):c=np.array([.085 if side=='left' else -.085,.036,p[2]])
    elif r.startswith('arm'):c=closest_center(p,[(f'joint-{letter}-shoulder',f'joint-{letter}-elbow'),(f'joint-{letter}-elbow',f'joint-{letter}-hand')])
    elif r.startswith('leg') or (source[i,1]<.09 and abs(source[i,0])>.035):c=closest_center(p,[(f'joint-{letter}-upper-leg',f'joint-{letter}-knee'),(f'joint-{letter}-knee',f'joint-{letter}-ankle')])
    else:c=np.array([0,p[1],-.012])
    direction=p-c;direction/=max(np.linalg.norm(direction),1e-8);dirs.append(direction)
dirs=np.array(dirs);offset=np.zeros(len(v));base=v.copy()
for iteration in range(12):
    tree=BVHTree.FromPolygons(v.tolist(),t.tolist(),all_triangles=True);needed=np.zeros(len(v));counts=0;omitted=0
    for p in points:
        q,n,ti,dist=tree.find_nearest(Vector(p));direction=dirs[t[ti]].mean(0);direction/=max(np.linalg.norm(direction),1e-8);signed=np.dot(p-np.array(q),direction)
        if signed<.0003:continue
        if inner_tri[ti]:omitted+=1;continue
        for vert in t[ti]:needed[vert]=max(needed[vert],min(signed+.003,.008))
        counts+=1
    for _ in range(3):needed=.75*needed+.25*np.array([needed[list(ns)].mean(0) if ns else needed[i] for i,ns in enumerate(adj)])
    offset=np.minimum(offset+needed,.040);v=base+dirs*offset[:,None]
    iterations.append({'iteration':iteration,'outsideSamples':counts,'innerReturnSamplesOmitted':omitted,'maxStepM':float(needed.max()),'saturatedVertices':int((offset>=.04).sum())});print(iterations[-1],flush=True)
# Slight whole-surface fairing is local and constrained, not a new mesh or global scale.
d['positions']=v.tolist();d['sourceInnerReturnVertices']=np.flatnonzero(inner).tolist();d['enclosureRecipe']={'sampling':'every fourth native vertex and every twelfth facet centre','maximumStepM':.008,'clearanceM':.003,'smoothingIterationsPerStep':3,'maximumOffsetM':.04,'iterations':12,'orientation':'fixed anatomical radial directions from independently observed native joint controls; original native fixed','nativeNormalUsed':False,'innerReturnCohort':'source anatomical eyelid/oral returns, excluded from exterior anchor eligibility'}
(E/'candidates/fit-r11.json').write_text(json.dumps(d,separators=(',',':')));(E/'candidates/fit-r11-enclosure.json').write_text(json.dumps({'iterations':iterations,'maxDisplacementM':float(np.linalg.norm(v-initial,axis=1).max()),'innerReturnVertexCount':int(inner.sum()),'validationPending':True},indent=2));print('ENCLOSURE_DONE',flush=True)
