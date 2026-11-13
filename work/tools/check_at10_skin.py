"""Scoped AT10 candidate format, source preservation and gate checks; geometry remains failed."""
from pathlib import Path
import json,hashlib,struct
import numpy as np
R=Path(__file__).resolve().parents[2];E=R/'work/evidence/AT10/2026-10-13-skin-fit-r1';O=R/'atlas-data/anatomy/skin/at10-fit-r1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
start=read(E/'start.json');mapping=read(O/'source-to-derived-r9.json');cost=read(O/'cost-r9.json');manifest=read(O/'manifest-r9.json');d=read(E/'candidates/fit-r9.json');v=np.array(d['positions'],dtype='<f4');ids=mapping['originalVertexIds'];assert len(set(ids))==13380
assert len(mapping['sourceFaceIds'])==13378 and len(set(mapping['sourceFaceIds']))==13378
assert len(mapping['logicalTriangles'])==26756 and max(max(x) for x in mapping['logicalTriangles'])<13380
assert mapping['helperExported'] is False and len(mapping['emittedVertices'])==14517
for p,h in mapping['sourceInputHashes'].items():assert sha(R/p)==h,(p,'source drift')
for p,h in read(E/'native-controls-r2.json')['nativeInputHashes'].items():assert sha(R/p)==h,(p,'native drift')
startup=R/'atlas-data/source-cache/z-anatomy/t97/extracted/Z-Anatomy/Startup.blend';assert sha(startup)=='9f08a17ea0115fed80b2a73ecdf0a1bc2ab2f6956f37c593ce23d513ea35afcd'
for side,frame in d['articulatedFrames'].items():
 assert np.linalg.det(np.array(frame['targetPalmFrame'])@np.array(frame['sourcePalmFrame']).T)>.999
 for bone in frame['bones']:assert np.linalg.det(np.array(bone['targetFrame'])@np.array(bone['sourceFrame']).T)>.999
controls=read(E/'native-controls-r2.json')['controls'];c={x['id']:x for x in controls}
for letter,sign in [('l',1),('r',-1)]:
 assert c[f'joint-{letter}-hand']['source'][0]*sign>0 and c[f'joint-{letter}-hand']['target'][0]*sign>0
 assert c[f'joint-{letter}-ankle']['source'][0]*sign>0 and c[f'joint-{letter}-ankle']['target'][0]*sign>0
# Verify actual original corner UV and source vertex addressing in emitted bytes.
b=(O/'skin-candidate-r9.glb').read_bytes();jsize=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+jsize]);data=b[28+jsize:]
for a,e in enumerate(mapping['emittedVertices']):
 pos=np.frombuffer(data,dtype='<f4',count=3,offset=g['bufferViews'][0]['byteOffset']+a*12);assert np.array_equal(pos,v[e['logicalVertex']])
 uv=np.frombuffer(data,dtype='<f4',count=2,offset=g['bufferViews'][2]['byteOffset']+a*8);assert np.array_equal(uv,np.array(d['uv'][e['sourceUv']],dtype='<f4'))
repro=Path('/private/tmp/at10-skin-fit-repro-r9/artifacts/skin-candidate-r9.glb');assert sha(repro)==sha(O/'skin-candidate-r9.glb')
assert manifest['learnerEligible'] is False and manifest['fitAcceptancePassed'] is False
assert read(E/'candidates/fit-r9-intersections.json')['crossingSkinTriangles']==5197
# Existing learner packages stay pinned; no point/route modification is authorized.
registry=read(R/'atlas-data/acupoints/learner/registry-r1.json')
for package in registry['packages']:
 assert sha(R/'atlas-data/acupoints/learner'/package['learnerFile'])==package['learnerSha256']
 assert sha(R/'atlas-data/acupoints/observation'/package['observationFile'])==package['observationSha256']
wip=start.get('wip',start.get('trackedWip',{}));print('start fields',list(start))
# The baseline schema records all tracked user WIP hashes, compared without staging.
if isinstance(wip,dict):
 for p,h in wip.items():assert sha(R/p)==(h.get('sha256') if isinstance(h,dict) else h),(p,'WIP changed')
for p in (R/'work/tools').glob('*at10_skin*'):
 if p.suffix=='.py':compile(p.read_text(),str(p),'exec')
result={'formatSourceMappingChecksPassed':True,'independentReproductionPassed':True,'sourceOriginalsUnchanged':True,'existingPackageHashesUnchanged':True,'nativeSideAndProperRotationChecksPassed':True,'geometryAcceptancePassed':False,'crossingSkinTriangles':5197,'learnerImported':0,'glbSha256':sha(O/'skin-candidate-r9.glb')}
(E/'scoped-checks-r9.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
