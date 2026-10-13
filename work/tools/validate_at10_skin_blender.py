"""Read-only exact native intersections for a fitted source topology."""
from pathlib import Path
import os,json,sys,importlib.util,collections
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];E=Path(os.environ.get('AT10_SKIN_EVIDENCE',str(R/'work/evidence/AT10/2026-10-13-skin-fit-r1')))
rev=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'r5'
d=json.loads((E/f'candidates/fit-{rev}.json').read_text());v=np.array(d['positions']);faces=[f['derivedVertices'] for f in d['faces']];t=np.array([[f[0],f[i],f[i+1]] for f in faces for i in range(1,len(f)-1)])
native=json.loads((E/'native-surfaces-r1.json').read_text());nv=[];nt=[];sources=[];localTriangleIds=[];names={}
for key,s in native.items():
    off=len(nv);nv.extend(s['v']);nt.extend([[a+off,b+off,c+off] for a,b,c in s['t']]);sources.extend([key]*len(s['t']));localTriangleIds.extend(range(len(s['t'])));names[key]=s['name']
print('build bvh',flush=True);skin=BVHTree.FromPolygons(v.tolist(),t.tolist(),all_triangles=True);nb=BVHTree.FromPolygons(nv,nt,all_triangles=True)
pairs=np.array(skin.overlap(nb));print('candidate pairs',len(pairs),flush=True)
s=importlib.util.spec_from_file_location('intersections',R/'atlas-web/scripts/nativeSurfaceIntersections.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
nt=np.array(nt);nv=np.array(nv);st=v[t[pairs[:,0]]];nat=nv[nt[pairs[:,1]]];hits=np.zeros(len(pairs),dtype=bool)
for a,b in [(0,1),(1,2),(2,0)]:
    hits|=m.SurfaceIndex.crosses(st[:,a],st[:,b]-st[:,a],nat)
    hits|=m.SurfaceIndex.crosses(nat[:,a],nat[:,b]-nat[:,a],st)
actual=pairs[hits];r=np.array(d['vertexRegions']);regions=r[t[actual[:,0],0]]
out={'revision':rev,'nativeTriangles':len(nt),'skinTriangles':len(t),'sourceTopologyPreserved':True,'exactSegmentTriangleCrossingPairs':len(actual),'crossingSkinTriangles':len(set(actual[:,0].tolist())),'countsByRegion':dict(collections.Counter(regions)),'countsByNativeSurface':dict(collections.Counter(names[sources[i]] for i in actual[:,1])),'sourceVolumeM3':float(np.einsum('ij,ij->i',v[t[:,0]],np.cross(v[t[:,1]],v[t[:,2]])).sum()/6),'crossingSkinTriangleIds':sorted(set(actual[:,0].tolist())),'method':'BVH candidate pairs -> shared nativeSurfaceIntersections Moller-Trumbore edges in both directions; no nearest-normal acceptance','acceptancePassed':False}
probes=[];seen=collections.Counter()
for si,ni in actual:
    region=str(r[t[si,0]]);key=sources[ni]
    if seen[region]>=16:continue
    seen[region]+=1;verts=t[si]
    faceIndex=int(si//2)
    probes.append({'region':region,'skinTriangle':int(si),'sourceObjFace':d['faces'][faceIndex]['sourceFace'],'sourceVertexIds':[d['originalVertexIds'][int(x)] for x in verts],'skinWorldM':v[verts].tolist(),'nativeSourceKey':key,'nativeName':names[key],'nativeTriangle':localTriangleIds[ni],'nativeWorldM':nv[nt[ni]].tolist(),'finding':'proper segment-triangle crossing; does not establish acupoint location'})
(E/f'candidates/fit-{rev}-remaining-probes.json').write_text(json.dumps(probes,indent=2)+'\n')
(E/f'candidates/fit-{rev}-intersections.json').write_text(json.dumps(out,indent=2)+'\n');print(out['countsByRegion'],flush=True)
