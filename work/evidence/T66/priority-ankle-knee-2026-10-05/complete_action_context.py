"""Retain explicit pose and context evidence for exact source muscle actions."""
import json,pathlib,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[4]
sha=lambda b:hashlib.sha256(b).hexdigest()
enc=lambda v:(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
vhash=lambda v:sha(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
bp=ROOT/'atlas-data/motion/motion-learning.json';b=json.loads(bp.read_text());rp=ROOT/'atlas-data/motion/authoring/registry.json';r=json.loads(rp.read_text());ap=ROOT/'atlas-data/motion/t66-priority-action-acceptance.json';a=json.loads(ap.read_text())
for row in a['rows']:
 action=next(x for x in b['muscleActions'] if x['id']==row['actionId']);p=ROOT/row['authoringPath'];rec=json.loads(p.read_text());stem=action['id'].removesuffix('-ACTION');contextid=stem+'-CONTEXT'
 posture='시작 모형의 고정된 자세에서 발목 등쪽굽힘을 보여 줍니다.' if 'TIBANT' in stem else '무릎 각도를 유지한 채 허벅지를 앞으로 들어 올립니다.'
 context='연결된 뼈와 근육 표면이 함께 움직이는 교육용 시범이며, 주변 근육의 개별 활성도·힘·수축 비중은 표시하지 않습니다.'
 for field,scope,value,cid in [('model_posture','posture_condition',posture,None),('model_context','context_role',context,contextid)]:
  claim={'id':stem+'-'+field.upper(),'field':field,'appliesTo':scope,'contextId':cid,'value':value}
  rec['claims'].append(claim);action['sourceRefs'].append({'layer':'source_family_record','field':field,'appliesTo':scope,'contextId':cid,'claimId':claim['id'],'valueHash':vhash(value),'evidenceId':rec['id'],'fieldEvidenceId':None})
 action['postureConditions']=[posture];action['contextRoles']=[{'contextId':contextid,'role':'unspecified','contractionRole':'unspecified','explanation':context}]
 p.write_bytes(enc(rec));digest=sha(p.read_bytes());next(x for x in r['records'] if x['id']==rec['id'])['sha256']=digest;row['authoringSha256']=digest
bp.write_bytes(enc(b));rp.write_bytes(enc(r));ap.write_bytes(enc(a))
