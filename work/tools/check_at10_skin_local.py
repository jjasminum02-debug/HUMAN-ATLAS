"""Scoped source/format/QA preservation checks, independent of fit acceptance."""
from pathlib import Path
import argparse,json,hashlib,struct,numpy as np
R=Path(__file__).resolve().parents[2];p=argparse.ArgumentParser();p.add_argument('--evidence',required=True);p.add_argument('--artifacts',required=True);p.add_argument('--revision',default='r22');a=p.parse_args();E=R/a.evidence;O=R/a.artifacts;B=R/'work/evidence/AT10/2026-10-13-skin-fit-r1';read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
start=read(E/'start.json');d=read(E/f'candidates/fit-{a.revision}.json');baseline=read(B/'candidates/fit-r9.json');mp=read(O/f'source-to-derived-{a.revision}.json');cost=read(O/f'cost-{a.revision}.json');manifest=read(O/f'manifest-{a.revision}.json')
for path,h in start['trackedWipHashes'].items():assert sha(R/path)==h,('WIP drift',path)
for path,info in start['inputs'].items():assert sha(R/path)==info['sha256'],('baseline drift',path)
for path,h in mp['sourceInputHashes'].items():assert sha(R/path)==h,('source drift',path)
for path,h in read(B/'native-controls-r2.json')['nativeInputHashes'].items():assert sha(R/path)==h,('native drift',path)
for key,u in read(B/'native-unit-provenance-r9.json').items():assert sha(R/u['unitFile'])==u['unitSha256'],('unit/matrix drift',key)
for field in ['sourceVertices','originalVertexIds','uv','faces','inputHashes','sourceGroupCounts']:
 assert d[field]==baseline[field],('original correspondence drift',field)
assert len(set(mp['originalVertexIds']))==13380 and len(mp['logicalTriangles'])==26756
assert mp['helperExported'] is False and mp['canonicalTopologySha256']=='d00ab149f431064d25e49a561abcba639abcafc59801d98ead1c57a19a998010'
assert all(x['sourceVertex']<13380 for x in mp['emittedVertices'])
raw=(O/f'skin-candidate-{a.revision}.glb').read_bytes();jl=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+jl]);data=raw[28+jl:];v=np.array(d['positions'],dtype='<f4')
for i,m in enumerate(mp['emittedVertices']):
 pos=np.frombuffer(data,dtype='<f4',count=3,offset=g['bufferViews'][0]['byteOffset']+i*12);assert np.array_equal(pos,v[m['logicalVertex']])
 uv=np.frombuffer(data,dtype='<f4',count=2,offset=g['bufferViews'][2]['byteOffset']+i*8);assert np.array_equal(uv,np.array(d['uv'][m['sourceUv']],dtype='<f4'))
for side,f in d['articulatedFrames'].items():assert np.linalg.det(np.array(f['targetPalmFrame'])@np.array(f['sourcePalmFrame']).T)>.999
for patch in d['checkpointComposition']['continuousHandRecipe']:
 assert patch['rotationDeterminant']>.999
 assert all(c['source'][0]*c['target'][0]>0 for c in patch['controls'])
registry=read(R/'atlas-data/acupoints/learner/registry-r1.json')
for pkg in registry['packages']:
 assert sha(R/'atlas-data/acupoints/learner'/pkg['learnerFile'])==pkg['learnerSha256']
 assert sha(R/'atlas-data/acupoints/observation'/pkg['observationFile'])==pkg['observationSha256']
for tool in (R/'work/tools').glob('*at10_skin*.py'):compile(tool.read_text(),str(tool),'exec')
repro=read(E/f'reproduction-{a.revision}.json');assert repro['exactBytesEqual'] and repro['glbSha256']==sha(O/f'skin-candidate-{a.revision}.glb')
qa=read(E/f'candidates/fit-{a.revision}-intersections.json');assert qa['candidateUnchanged'] and qa['emittedGlbSha256']==repro['glbSha256']
assert cost['glbBytes']<8*1024**2 and cost['triangles']==26756 and cost['decodedGpuGeometryBytes']==625080
assert manifest['learnerEligible'] is False and manifest['fitAcceptancePassed'] is False and manifest['registeredInLearnerPackage'] is False
assert qa['crossingSkinTriangles']>0 and qa['nonAdjacentSelfCrossingPairs']>0
result={'sourceAndFormatChecksPassed':True,'nativeInputHashesUnchanged':True,'nativeUnitMatricesUnchanged':True,'originalHelpersFacesVerticesCornerUVPreserved':True,'properSideAndRotationPassed':True,'existingPackagesUnchanged':True,'trackedWipHashesPreserved':len(start['trackedWipHashes']),'independentReproductionPassed':True,'validatorReadOnlyPassed':True,'geometryAcceptancePassed':False,'nativeCrossingSkinTriangles':qa['crossingSkinTriangles'],'selfCrossingPairs':qa['nonAdjacentSelfCrossingPairs'],'actualLearnerImports':0,'glbSha256':repro['glbSha256']}
(E/f'scoped-checks-{a.revision}.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
