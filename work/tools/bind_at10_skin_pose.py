"""Canonical static-pose metadata binding; geometry and acceptance stay unchanged."""
from pathlib import Path
import argparse,json,hashlib,importlib.util
import numpy as np
R=Path(__file__).resolve().parents[2];p=argparse.ArgumentParser();p.add_argument('--evidence',required=True);p.add_argument('--base',required=True);p.add_argument('--base-candidate');p.add_argument('--revision',required=True);a=p.parse_args();E=R/a.evidence
load=lambda p:json.loads(p.read_text());base=R/a.base_candidate if a.base_candidate else E/f'candidates/fit-{a.base}.json';out=E/f'candidates/fit-{a.revision}.json';assert not out.exists();d=load(base);dataset=load(R/'atlas-data/source-cache/datasets/za/compiled/manifest.json');pose=dataset['frameContract']['staticReferencePose']
assert dataset['sourceHash']=='9f08a17ea0115fed80b2a73ecdf0a1bc2ab2f6956f37c593ce23d513ea35afcd'
assert pose['sourceFrame']==0 and pose['rigBindingVerified'] is False
reader=R/'work/evidence/AT8/2026-10-13-r1/native-reader.py'
spec=importlib.util.spec_from_file_location('native_reader',reader);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
native=load(R/'work/evidence/AT10/2026-10-13-skin-fit-r1/native-surfaces-r1.json');checks=[]
for name,side in [('Crural fascia','right'),('Radius','right'),('Mandible',None)]:
 key=module.find(name,side);v,t=module.world(key);old=native[key]
 assert np.array_equal(v,np.array(old['v'])) and np.array_equal(t,np.array(old['t']))
 checks.append({'sourceKey':key,'name':name,'side':side,'worldGeometryExact':True,'geometrySha256':hashlib.sha256(v.astype('<f8').tobytes()+t.astype('<u4').tobytes()).hexdigest()})
old_geometry=hashlib.sha256(json.dumps({k:d[k] for k in ['sourceVertices','positions','originalVertexIds','faces','uv']},sort_keys=True).encode()).hexdigest()
d['candidateRevision']=a.revision;d['referencePoseBinding']={'priorMetadataPoseId':'za-c7010a9-9f08a17ea011-frame0-static','canonicalPoseId':pose['id'],'sourceHash':dataset['sourceHash'],'sourceFrame':0,'frameId':dataset['frameContract']['targetFrameId'],'nativeReader':str(reader.relative_to(R)),'nativeReaderSha256':hashlib.sha256(reader.read_bytes()).hexdigest(),'baseCandidateSha256':hashlib.sha256(base.read_bytes()).hexdigest(),'geometrySha256':old_geometry,'meaning':'Same hash-bound frame-0 snapshot. Corrects inconsistent metadata alias only; no rig/rest-pose or geometry acceptance.'}
d['referencePoseBinding']['actualCurrentNativeChecks']=checks
d['referencePoseBinding']['actualCurrentDetailInputs']=module.inputs
assert old_geometry==hashlib.sha256(json.dumps({k:d[k] for k in ['sourceVertices','positions','originalVertexIds','faces','uv']},sort_keys=True).encode()).hexdigest();assert d['fitAcceptancePassed'] is False and d['learnerEligible'] is False
out.write_text(json.dumps(d,separators=(',',':')));(E/f'pose-binding-{a.revision}.json').write_text(json.dumps(d['referencePoseBinding'],indent=2)+'\n');print(json.dumps(d['referencePoseBinding']))
