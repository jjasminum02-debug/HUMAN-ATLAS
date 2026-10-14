"""Read-only source self-contact baseline, not a fit acceptance exclusion list."""
import sys, json, importlib.util
from pathlib import Path
import numpy as np
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];E=R/'work/evidence/AT10/2026-10-14-skin-fit-r5'
d=json.loads((R/'work/evidence/AT10/2026-10-13-skin-fit-r2/candidates/fit-r22.json').read_text())
s=np.array(d['sourceVertices']);faces=d['faces'];t=np.array([[f['derivedVertices'][0],f['derivedVertices'][i],f['derivedVertices'][i+1]] for f in faces for i in range(1,len(f['derivedVertices'])-1)])
path=R/'atlas-data/source-cache/datasets/skin-source-review-2026-10-13/base.obj'
raw=np.array([list(map(float,line.split()[1:4])) for line in path.read_text().splitlines() if line.startswith('v ')])*.1
spec=importlib.util.spec_from_file_location('crosses',R/'atlas-web/scripts/nativeSurfaceIntersections.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
result=[]
for name,v in [('core',raw[np.array(d['originalVertexIds'])]),('pinned-young-target',s)]:
    tree=BVHTree.FromPolygons(v.tolist(),t.tolist(),all_triangles=True)
    pairs=np.array(tree.overlap(tree),int).reshape(-1,2);pairs=pairs[pairs[:,0]<pairs[:,1]]
    pairs=pairs[~(t[pairs[:,0],:,None]==t[pairs[:,1],None,:]).any((1,2))]
    a,b=v[t[pairs[:,0]]],v[t[pairs[:,1]]];hit=np.zeros(len(pairs),bool)
    for i,j in [(0,1),(1,2),(2,0)]:
        hit|=m.SurfaceIndex.crosses(a[:,i],a[:,j]-a[:,i],b);hit|=m.SurfaceIndex.crosses(b[:,i],b[:,j]-b[:,i],a)
    pairs=pairs[hit];regions=np.array(d['vertexRegions'])
    from collections import Counter
    result.append({'source':name,'selfPairs':len(pairs),'regionPairs':dict(Counter('|'.join(sorted([regions[t[a,0]],regions[t[b,0]]])) for a,b in pairs)),
        'trianglePairs':pairs.tolist(),'notAnAutomaticFitExclusionList':True})
    print({k:v for k,v in result[-1].items() if k!='trianglePairs'},flush=True)
(E/'source-self-baseline-r1.json').write_text(json.dumps(result,indent=2)+'\n')
