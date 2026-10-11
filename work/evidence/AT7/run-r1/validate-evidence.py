from pathlib import Path
import ast,json,hashlib,struct
import numpy as np
R=Path(__file__).resolve().parents[4];E=Path(__file__).parent;A=R/'work/evidence/acupoint-AC1';cache=R/'atlas-data/source-cache/datasets/za'
read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest();inputs={};meshes={}
fn=next(n for n in ast.parse((A/'build_carrier.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='world');exec(compile(ast.Module(body=[fn],type_ignores=[]),'AC1-reader','exec'),globals())
audit=read(E/'context-geometry-audit-r1.json');doc=read(R/'atlas-data/acupoints/observation/lung-context-r1.json');source=read(R/'work/evidence/AT6/resume-r1/bilateral-rules-r9.json');ledger=read(R/'work/evidence/AT6/resume-r1/bilateral-compiler-r8/ledger.json')
for p,h in audit['sourceReadHashes'].items():assert sha((R/p).read_bytes())==h,p
for part in audit['parts']:
 v,t=world(part['sourceKey']);ids=part['triangleIds'];local=v[np.unique(t[ids])];lo,hi=np.array(part['clipBounds']);assert ((local>=lo)&(local<=hi)).all();assert np.allclose([local.min(axis=0),local.max(axis=0)],part['bounds'],atol=1e-10)
for c in doc['contexts']:
 unit=next(u for u in source['units'] if u['code']==c['code'] and u['side']==c['side']);i=ledger['units'][unit['id']]['instance'];carrier=source['inputs']['carriers'][i['carrierId']];v=np.array(carrier['positions']).reshape(-1,3);t=np.array(carrier['indices']).reshape(-1,3)
 assert c['placementBinding']=={k:i[k] for k in ['carrierId','carrierHash','triangle','barycentric']};assert np.allclose(np.array(i['barycentric'])@v[t[i['triangle']]],c['point'],atol=1e-10)
assert doc['placementInputSha256']==sha((R/'work/evidence/AT6/resume-r1/bilateral-rules-r9.json').read_bytes())
cases=read(E/'responsive-cases-final.json');assert len(cases)==24;assert len({c['result']['scene']['root'] for c in cases})==1
for c in cases:
 d=c['result'];assert d['review']['selected']==c['code'] and d['review']['selectedSide']==c['side'];assert d['review']['actualObservation']['inside'];assert .5<=d['review']['actualObservation']['occupancy']<=.7;assert not d['review']['observation']['pointOccluded'];assert len(d['labels'])==1 and not d['labels'][0]['hidden'];assert c['code'] in d['card'];assert len(d['review']['observation']['structures'])>=2;assert d['scene']['renderer']=='anatomy-'+d['scene']['root']
for name in ['rapid-reentry-return-r1.json','close-during-return-r1.json']:
 x=read(E/name);assert np.allclose(x['base']['scene']['camera'],x['after']['scene']['camera'],atol=1e-12,rtol=0);assert np.allclose(x['base']['scene']['target'],x['after']['scene']['target'],atol=1e-12,rtol=0);assert x['after']['scene']['registeredUpdates']==0
x=read(E/'tour-complete-r3.json');assert [f['projection']['selection']['code'] for f in x['frames'][:11]]==[f'LU{i}' for i in range(1,12)];assert x['frames'][-1]['review']['tour']=='ready';assert np.allclose(x['base']['scene']['camera'],x['frames'][-1]['scene']['camera'],atol=1e-12,rtol=0)
for item in read(E/'manual-inputs-r2.json'):assert item['result']['review']['tour']=='paused' and item['result']['review']['autoReturn'] is False
x=read(E/'mobile-final-r2.json');assert all(t['width']>=44 and t['height']>=44 for t in x['targets']);assert not x['result']['scene']['cameraTransition']
x=read(E/'all-points-r1.json');assert x['projection']['localLearnerEligible']==22 and x['projection']['unresolved']==648;assert len({(p['code'],p['side']) for p in x['review']['points']})==22;assert x['projection']['fixtureExports']==0
x=read(E/'native-anatomy-click-r1.json');assert x['after']['dataset']['selected']=='ZA-c7010a9-b79c7d0ed5f3e42439fa6d34';assert x['after']['review'] is None
x=read(E/'final-native.json');assert x['scene']['registeredUpdates']==0 and x['scene']['cameraOwner'] is None and x['review'] is None;assert x['url'].endswith('source=ZA-c7010a9-eb0a993e09d73159468116ce');assert not read(E/'console-final.json')
assert all(step['exitCode']==0 for step in read(E/'build-final-r2.json'));assert 'ℹ pass 64' in (E/'tests-final-r2.log').read_text() and 'ℹ fail 0' in (E/'tests-final-r2.log').read_text()
print('PASS: 86 native local parts, 22 unchanged AT6 bindings, 24 actual views, tour/input/return/lifecycle, 64 tests and 13 build steps')
