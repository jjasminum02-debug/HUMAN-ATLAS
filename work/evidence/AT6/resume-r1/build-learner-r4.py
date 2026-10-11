from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[4];E=Path(__file__).parent
base=R/'atlas-data/acupoints/learner/lung.json';p=json.loads(base.read_text());projections=json.loads((E/'bilateral-compiler-r6/runtime-projection.json').read_text());found={(i['code'],i['side']) for x in projections for i in x['instances']};assert len(found)==22
p['projections']=projections
for a in p['availability']:a.update(display='educational_approximation',reason='교육용 모형 위치 · 정밀 취혈 위치는 미확정')
p['precisionCounts']={'precise':0,'educationalApproximation':22,'unresolved':0}
out=R/'atlas-data/acupoints/learner/lung-r4.json';assert not out.exists();out.write_text(json.dumps(p,ensure_ascii=False,separators=(',',':'))+'\n')
(E/'learner-build-r4.json').write_text(json.dumps({'original':str(base.relative_to(R)),'originalSha256':hashlib.sha256(base.read_bytes()).hexdigest(),'output':str(out.relative_to(R)),'outputSha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bytes':out.stat().st_size,'conceptsUnchanged':p['concepts']==json.loads(base.read_text())['concepts'],'actualEducationalPositions':len(found),'preciseClinicalPositions':0,'fixtureExports':0,'compilerInputSha256':json.loads((E/'bilateral-compiler-r6/receipt.json').read_text())['sourceSha256']},indent=2)+'\n')
