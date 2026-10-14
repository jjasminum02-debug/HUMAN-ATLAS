"""Read-only exact native intersections for a fitted source topology."""
from pathlib import Path
import os,json,sys,importlib.util,collections,hashlib,struct
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];E=Path(os.environ.get('AT10_SKIN_EVIDENCE',str(R/'work/evidence/AT10/2026-10-13-skin-fit-r1')))
rev=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'r5'
candidateDirectory=Path(os.environ.get('AT10_SKIN_CANDIDATE_DIRECTORY',str(E/'candidates')))
candidatePath=candidateDirectory/f'fit-{rev}.json'
d=json.loads(candidatePath.read_text());v=np.array(d['positions']);faces=[f['derivedVertices'] for f in d['faces']];t=np.array([[f[0],f[i],f[i+1]] for f in faces for i in range(1,len(f)-1)])
O=Path(os.environ.get('AT10_SKIN_ARTIFACTS',str(R/'atlas-data/anatomy/skin/at10-fit-r1')))
emitted=O/f'skin-candidate-{rev}.glb';candidateHash=hashlib.sha256(candidatePath.read_bytes()).hexdigest()
if emitted.exists():
    raw=emitted.read_bytes();jl=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+jl]);binstart=28+jl;ac=g['accessors'][0];vw=g['bufferViews'][ac['bufferView']];pos=np.frombuffer(raw,dtype='<f4',count=ac['count']*3,offset=binstart+vw.get('byteOffset',0)+ac.get('byteOffset',0)).reshape(-1,3)
    mp=json.loads((O/f'source-to-derived-{rev}.json').read_text());v=np.zeros_like(v)
    for i,mapping in enumerate(mp['emittedVertices']):v[mapping['logicalVertex']]=pos[i]
    assert hashlib.sha256(raw).hexdigest()==mp['glbSha256']
nativePath=E/'native-surfaces-r1.json'
if not nativePath.exists():nativePath=R/'work/evidence/AT10/2026-10-13-skin-fit-r1/native-surfaces-r1.json'
native=json.loads(nativePath.read_text());nv=[];nt=[];sources=[];localTriangleIds=[];names={}
for key,s in native.items():
    off=len(nv);nv.extend(s['v']);nt.extend([[a+off,b+off,c+off] for a,b,c in s['t']]);sources.extend([key]*len(s['t']));localTriangleIds.extend(range(len(s['t'])));names[key]=s['name']
print('build bvh',flush=True);skin=BVHTree.FromPolygons(v.tolist(),t.tolist(),all_triangles=True);nb=BVHTree.FromPolygons(nv,nt,all_triangles=True)
pairs=np.array(skin.overlap(nb),dtype=np.int32).reshape(-1,2);print('candidate pairs',len(pairs),flush=True)
s=importlib.util.spec_from_file_location('intersections',R/'atlas-web/scripts/nativeSurfaceIntersections.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
nt=np.array(nt);nv=np.array(nv);st=v[t[pairs[:,0]]];nat=nv[nt[pairs[:,1]]];hits=np.zeros(len(pairs),dtype=bool)
for a,b in [(0,1),(1,2),(2,0)]:
    hits|=m.SurfaceIndex.crosses(st[:,a],st[:,b]-st[:,a],nat)
    hits|=m.SurfaceIndex.crosses(nat[:,a],nat[:,b]-nat[:,a],st)
actual=pairs[hits];r=np.array(d['vertexRegions']);regions=r[t[actual[:,0],0]]
selfPairs=np.array(skin.overlap(skin),dtype=np.int32);selfPairs=selfPairs[selfPairs[:,0]<selfPairs[:,1]]
if len(selfPairs):
    adjacent=(t[selfPairs[:,0],:,None]==t[selfPairs[:,1],None,:]).any((1,2));selfPairs=selfPairs[~adjacent]
if len(selfPairs):
    sa=v[t[selfPairs[:,0]]];sb=v[t[selfPairs[:,1]]];selfHits=np.zeros(len(selfPairs),bool)
    for a,b in [(0,1),(1,2),(2,0)]:
        selfHits|=m.SurfaceIndex.crosses(sa[:,a],sa[:,b]-sa[:,a],sb);selfHits|=m.SurfaceIndex.crosses(sb[:,a],sb[:,b]-sb[:,a],sa)
    selfPairs=selfPairs[selfHits]
out={'revision':rev,'nativeTriangles':len(nt),'skinTriangles':len(t),'sourceTopologyPreserved':True,'exactSegmentTriangleCrossingPairs':len(actual),'crossingSkinTriangles':len(set(actual[:,0].tolist())),'countsByRegion':dict(collections.Counter(regions)),'countsByNativeSurface':dict(collections.Counter(names[sources[i]] for i in actual[:,1])),'sourceVolumeM3':float(np.einsum('ij,ij->i',v[t[:,0]],np.cross(v[t[:,1]],v[t[:,2]])).sum()/6),'crossingSkinTriangleIds':sorted(set(actual[:,0].tolist())),'method':'BVH candidate pairs -> shared nativeSurfaceIntersections Moller-Trumbore edges in both directions; no nearest-normal acceptance','acceptancePassed':False}
probes=[];seen=collections.Counter()
for si,ni in actual:
    region=str(r[t[si,0]]);key=sources[ni]
    if seen[region]>=16:continue
    seen[region]+=1;verts=t[si]
    faceIndex=int(si//2)
    probes.append({'region':region,'skinTriangle':int(si),'sourceObjFace':d['faces'][faceIndex]['sourceFace'],'sourceVertexIds':[d['originalVertexIds'][int(x)] for x in verts],'skinWorldM':v[verts].tolist(),'nativeSourceKey':key,'nativeName':names[key],'nativeTriangle':localTriangleIds[ni],'nativeWorldM':nv[nt[ni]].tolist(),'finding':'proper segment-triangle crossing; does not establish acupoint location'})
(E/f'candidates/fit-{rev}-remaining-probes.json').write_text(json.dumps(probes,indent=2)+'\n')
out['emittedGlbSha256']=hashlib.sha256(emitted.read_bytes()).hexdigest() if emitted.exists() else None
out['uniqueCrossingTrianglesByRegion']={region:len(set(actual[regions==region,0].tolist())) for region in sorted(set(regions))}
returnVertices=np.zeros(len(v),bool);returnVertices[d.get('sourceReturnVertices',[])]=True
returnTriangles=returnVertices[t].any(1)
out['sourceReturnCrossingTriangles']=int(returnTriangles[np.unique(actual[:,0])].sum())
out['outerCrossingTriangles']=out['crossingSkinTriangles']-out['sourceReturnCrossingTriangles']
out['returnCohortExcludedFromTotal']=False
out['nonAdjacentSelfCrossingPairs']=len(selfPairs)
out['selfCrossingSkinTriangleIds']=sorted(set(selfPairs.ravel().tolist()))
out['candidateUnchanged']=candidateHash==hashlib.sha256(candidatePath.read_bytes()).hexdigest();assert out['candidateUnchanged']
np.savez_compressed(E/f'candidates/fit-{rev}-contact-addresses.npz',skinTriangle=actual[:,0],nativeSourceIndex=np.array([list(native).index(sources[i]) for i in actual[:,1]]),nativeLocalTriangle=np.array([localTriangleIds[i] for i in actual[:,1]]),nativeSourceKeys=np.array(list(native)),selfCrossingTrianglePairs=selfPairs)
(E/f'candidates/fit-{rev}-intersections.json').write_text(json.dumps(out,indent=2)+'\n');print(out['countsByRegion'],flush=True)
