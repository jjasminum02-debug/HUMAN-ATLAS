"""Read-only separation of authorized reference exceptions from raw emitted QA."""
from pathlib import Path
import argparse,json,hashlib,collections
import numpy as np
R=Path(__file__).resolve().parents[2];p=argparse.ArgumentParser();p.add_argument('--evidence',required=True);p.add_argument('--revision',required=True);p.add_argument('--policy',required=True);a=p.parse_args()
E=R/a.evidence;path=E/f'candidates/fit-{a.revision}.json';before=hashlib.sha256(path.read_bytes()).hexdigest();d=json.loads(path.read_text());policy=json.loads((R/a.policy).read_text());assert policy['userAuthorized'] and policy['rawFullReferenceQaRequired']
n=np.load(E/f'candidates/fit-{a.revision}-contact-addresses.npz');keys=n['nativeSourceKeys'];source=[str(keys[i]) for i in n['nativeSourceIndex']];exceptions={x['sourceKey']:set(x['triangleIds']) for x in policy['facets']}
exception=np.array([int(t) in exceptions.get(k,set()) for k,t in zip(source,n['nativeLocalTriangle'])]);t=np.array([[f['derivedVertices'][0],f['derivedVertices'][j],f['derivedVertices'][j+1]] for f in d['faces'] for j in range(1,len(f['derivedVertices'])-1)]);regions=np.array(d['vertexRegions']);skin=n['skinTriangle'];kept=skin[~exception]
allkeys=list(json.loads((R/'work/evidence/AT10/2026-10-13-skin-fit-r1/native-surfaces-r1.json').read_text()));native=json.loads((R/'work/evidence/AT10/2026-10-13-skin-fit-r1/native-surfaces-r1.json').read_text());native.update(json.loads((R/'work/evidence/AT10/2026-10-14-skin-fit-r5/native-supplement-r1.json').read_text()))
for item in policy['facets']:
 ref=native[item['sourceKey']]
 actual=hashlib.sha256(np.asarray(ref['v'],dtype='<f8').tobytes()+np.asarray(ref['t'],dtype='<u4').tobytes()).hexdigest()
 assert actual==item['geometrySha256'] and ref['name']==item['sourceName'] and ref['side']==item['side']
 assert all(0<=i<len(ref['t']) for i in item['triangleIds'])
out={'revision':a.revision,'policy':a.policy,'rawPairs':len(skin),'rawCrossingSkinTriangles':len(set(skin.tolist())),'referenceExceptionPairs':int(exception.sum()),'exceptionSkinTriangles':len(set(skin[exception].tolist())),'actionablePairs':int((~exception).sum()),'actionableSkinTriangles':len(set(kept.tolist())),'actionableUniqueByRegion':{r:len(set(kept[regions[t[kept,0]]==r].tolist())) for r in sorted(set(regions[t[kept,0]]))},'actionableByNativeSurface':dict(collections.Counter(native[k]['name'] for k,q in zip(source,exception) if not q)),'rawSelfPairs':len(n['selfCrossingTrianglePairs']),'sourceOrCandidateChanged':False,'geometryAcceptance':False,'learnerEligible':False,'actionableAddresses':[{'skinTriangle':int(s),'sourceKey':k,'nativeTriangle':int(f),'region':str(regions[t[s,0]])} for s,k,f,q in zip(skin,source,n['nativeLocalTriangle'],exception) if not q]}
assert before==hashlib.sha256(path.read_bytes()).hexdigest();outpath=E/f'reference-assessment-{a.revision}.json';assert not outpath.exists();outpath.write_text(json.dumps(out,indent=2)+'\n');print({k:v for k,v in out.items() if k!='actionableAddresses'})
