"""Local source-facet chord diagnostic/refinement, without changing native input.

New logical vertices retain an explicit source face/triangle barycentric ancestry.
The original OBJ vertices, helper records and UV corners are retained verbatim.
The already authored continuous field is evaluated; there is no normal push.
"""
from pathlib import Path
import argparse, copy, json, sys, importlib.util, hashlib
import numpy as np
from mathutils.bvhtree import BVHTree

R = Path(__file__).resolve().parents[2]
p = argparse.ArgumentParser()
p.add_argument('--evidence', required=True)
p.add_argument('--base', default='r38')
p.add_argument('--revision', required=True)
p.add_argument('--levels', type=int, default=2)
p.add_argument('--field-manifest')
p.add_argument('--native-supplement')
p.add_argument('--reference-exceptions')
a = p.parse_args(sys.argv[sys.argv.index('--')+1:])
E = R/a.evidence
load = lambda x: json.loads(x.read_text())
d = load(E/f'candidates/fit-{a.base}.json')
assert not (E/f'candidates/fit-{a.revision}.json').exists()
log = load(E/f'contact-fit-{a.base}.json')
unit_name=log['sourceUnit'].get('unit','hand')+'-'+log['sourceUnit']['side']
field = next(x for x in load(R/a.field_manifest if a.field_manifest else R/'work/evidence/AT10/2026-10-14-skin-fit-r4/surface-bands-r31.json')['patches'] if x['patch']==unit_name)
centers = np.array(field['sourceFieldCentersM']); targets=np.array(field['nativeFieldTargetsM'])
center=centers.mean(0); x=(centers-center)/.1
rr=np.linalg.norm(x[:,None]-x[None,:],axis=2); poly=np.column_stack([np.ones(len(x)),x])
coef=np.linalg.solve(np.block([[rr**3+np.diag(field['regularization']),poly],[poly.T,np.zeros((4,4))]]),np.vstack([targets,np.zeros((4,3))]))
def evaluate(points):
    q=(np.array(points)-center)/.1; radius=np.linalg.norm(q[:,None]-x[None,:],axis=2)
    result=radius**3@coef[:-4]+np.column_stack([np.ones(len(q)),q])@coef[-4:]
    for stage in log['steps']:
        delta=result[:,None]-np.array(stage['fieldCentersM'])[None]
        phi=np.exp(-np.einsum('qnk,qnk->qn',delta,delta)/(2*np.array(stage['sigmaM'])**2))
        result+=phi@np.array(stage['rawFieldCoefficients'])
    return result

v=list(d['positions']); source=list(d['sourceVertices']); uv=list(d['uv'])
faces=[]
for f in d['faces']:
    for j in range(1,len(f['derivedVertices'])-1):
        corners=[0,j,j+1]
        faces.append({**f,**{key:[f[key][k] for k in corners] for key in ['v','uv','derivedVertices']},
            'originalSourceCorners':corners})
native=load(R/'work/evidence/AT10/2026-10-13-skin-fit-r1/native-surfaces-r1.json')
if a.native_supplement:
    supplement=load(R/a.native_supplement);assert not set(supplement)&set(native);native.update(supplement)
exceptions={}
if a.reference_exceptions:
    policy=load(R/a.reference_exceptions);assert policy['userAuthorized'] and policy['rawFullReferenceQaRequired']
    for item in policy['facets']:
        ref=native[item['sourceKey']]
        assert item['geometrySha256']==hashlib.sha256(np.asarray(ref['v'],dtype='<f8').tobytes()+np.asarray(ref['t'],dtype='<u4').tobytes()).hexdigest()
        exceptions[item['sourceKey']]=set(item['triangleIds'])
nv=[];nt=[]
for key,item in native.items():
    off=len(nv);nv.extend(item['v']);kept=[f for i,f in enumerate(item['t']) if i not in exceptions.get(key,set())];nt.extend((np.array(kept)+off).tolist())
nb=BVHTree.FromPolygons(nv,nt,all_triangles=True);nv=np.array(nv);nt=np.array(nt)
spec=importlib.util.spec_from_file_location('crosses',R/'atlas-web/scripts/nativeSurfaceIntersections.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
unit=set(log['sourceUnit']['sourceVertices']); ancestry=[]; records=[]
def inspect():
    tv=np.array([f['derivedVertices'] for f in faces]); vv=np.array(v)
    local_ids=np.array([i for i,t in enumerate(tv) if any(int(k) in unit for k in t)])
    local=BVHTree.FromPolygons(v,tv[local_ids].tolist(),all_triangles=True)
    bvh=BVHTree.FromPolygons(v,tv.tolist(),all_triangles=True)
    pairs=np.array(local.overlap(nb),int).reshape(-1,2)
    def exact(aa,bb):
        result=np.zeros(len(aa),bool)
        for i,j in [(0,1),(1,2),(2,0)]:
            result|=m.SurfaceIndex.crosses(aa[:,i],aa[:,j]-aa[:,i],bb)
            result|=m.SurfaceIndex.crosses(bb[:,i],bb[:,j]-bb[:,i],aa)
        return result
    if len(pairs): pairs=pairs[exact(vv[tv[local_ids[pairs[:,0]]]],nv[nt[pairs[:,1]]])]
    bad=local_ids[pairs[:,0]] if len(pairs) else np.array([],int)
    sp=np.array(local.overlap(bvh),int).reshape(-1,2)
    sp=np.unique(np.sort(np.column_stack([local_ids[sp[:,0]],sp[:,1]]),axis=1),axis=0)
    if len(sp): sp=sp[~(tv[sp[:,0],:,None]==tv[sp[:,1],None,:]).any((1,2))]
    if len(sp): sp=sp[exact(vv[tv[sp[:,0]]],vv[tv[sp[:,1]]])]
    return sorted(set(bad.tolist())),len(pairs),len(sp)

for level in range(a.levels+1):
    bad,pairs,self_pairs=inspect()
    records.append({'level':level,'logicalVertices':len(v),'triangles':len(faces),'nativeCrossingSkinTrianglesInUnit':len(bad),'nativePairsInUnit':pairs,'selfPairsTouchingUnit':self_pairs})
    print(records[-1],flush=True)
    if not bad or level==a.levels:break
    selected=set(bad)
    # One shared-vertex ring keeps the coarse/fine boundary away from the contacts.
    affected=set(k for i in bad for k in faces[i]['derivedVertices'])
    selected.update(i for i,f in enumerate(faces) if any(k in affected for k in f['derivedVertices']) and all(k in unit for k in f['derivedVertices']))
    split_edges=set()
    for i in selected:
        t=faces[i]['derivedVertices']
        split_edges.update(tuple(sorted((t[k],t[(k+1)%3]))) for k in range(3))
    edge_ids={}; new_source=[]
    for edge in sorted(split_edges):
        vi=len(v)+len(new_source);edge_ids[edge]=vi
        new_source.append(((np.array(source[edge[0]])+source[edge[1]])*.5).tolist())
        ancestry.append({'logicalVertex':vi,'originalSourceVertex':None,'parentLogicalEdge':list(edge),'weights':[.5,.5],'sourceCoordinatesM':new_source[-1]})
        unit.add(vi)
    v.extend(evaluate(new_source).tolist());source.extend(new_source)
    d['originalVertexIds'].extend([None]*len(new_source))
    d['vertexRegions'].extend([unit_name]*len(new_source))
    next_faces=[]
    for f in faces:
        t=f['derivedVertices']; perimeter=[];uvs=[];old=[]
        for k in range(3):
            perimeter.append(t[k]);uvs.append(f['uv'][k]);old.append(f['v'][k])
            edge=tuple(sorted((t[k],t[(k+1)%3])))
            if edge in edge_ids:
                perimeter.append(edge_ids[edge]);old.append(None)
                u=(np.array(uv[f['uv'][k]])+uv[f['uv'][(k+1)%3]])*.5
                uvs.append(len(uv));uv.append(u.tolist())
        # Fan from an existing corner when only one edge is split can degenerate.
        # Explicit red/green patterns retain the original triangle orientation.
        mid=[edge_ids.get(tuple(sorted((t[k],t[(k+1)%3])))) for k in range(3)]
        n=sum(z is not None for z in mid)
        if n==0:next_faces.append(f);continue
        if n==3:
            patterns=[[0,1,5],[1,2,3],[5,3,4],[1,3,5]]
        elif n==1:
            k=next(k for k,z in enumerate(mid) if z is not None)
            # Perimeter is [a,m,b,c] rotated to the split edge.
            start=perimeter.index(t[k]); idx=[(start+j)%4 for j in range(4)]
            patterns=[[idx[0],idx[1],idx[3]],[idx[1],idx[2],idx[3]]]
        else:
            k=next(k for k,z in enumerate(mid) if z is None)
            # Unsplit a-b, then b-m-c-m-a.
            start=perimeter.index(t[k]);idx=[(start+j)%5 for j in range(5)]
            patterns=[[idx[0],idx[1],idx[2]],[idx[0],idx[2],idx[4]],[idx[2],idx[3],idx[4]]]
        for ix in patterns:
            next_faces.append({**f,'derivedVertices':[perimeter[k] for k in ix],'uv':[uvs[k] for k in ix],
                'v':[old[k] for k in ix],'subdivisionLevel':level+1})
    faces=next_faces

d['positions']=v;d['sourceVertices']=source;d['uv']=uv;d['faces']=faces
d['candidateRevision']=a.revision;d['fitAcceptancePassed']=False;d['learnerEligible']=False
d['derivedVertexAncestry']=ancestry
d['localRefinement']={'baseRevision':a.base,'method':'conforming triangle red/green subdivision; existing source field evaluated at edge midpoints',
    'originalLogicalVerticesRetained':13380,'originalObjSourceFacesRetainedAsAncestry':True,'originalUvValuesRetained':True,
    'records':records,'wholeSkinAcceptance':False}
d['localRefinement'].update(fieldManifest=a.field_manifest,nativeSupplement=a.native_supplement,referenceExceptions=a.reference_exceptions,rawFullReferenceQaRequired=True)
(E/f'candidates/fit-{a.revision}.json').write_text(json.dumps(d,separators=(',',':')))
(E/f'refinement-{a.revision}.json').write_text(json.dumps(d['localRefinement'],indent=2)+'\n')
