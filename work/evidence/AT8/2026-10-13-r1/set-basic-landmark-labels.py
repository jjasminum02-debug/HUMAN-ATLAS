from pathlib import Path
import json,hashlib
R=Path('/Users/daniel/Downloads/SIM /HUMAN ATLAS');labels={'LI1':'검지 손톱 뿌리 · 검지 끝마디뼈 · 엄지 관절 너비','LI2':'둘째 손허리손가락관절 · 검지 첫마디뼈','LI3':'둘째 손허리손가락관절 · 둘째 손허리뼈','LI4':'둘째 손허리뼈 중점 · 손등 뼈사이근','LI5':'노뼈 붓돌기 · 긴엄지폄근·짧은엄지폄근 힘줄','LI6':'노쪽 손목·팔꿈치 기준 · 노뼈','LI7':'노쪽 손목·팔꿈치 기준 · 노뼈','LI8':'노쪽 팔꿈치·손목 기준 · 위팔노근','LI9':'노쪽 팔꿈치·손목 기준 · 위팔노근','LI10':'노쪽 팔꿈치·손목 기준 · 위팔노근','LI11':'가쪽위관절융기 · 원위 이두근 힘줄','LI12':'가쪽위관절융기 · 위관절융기능선','LI13':'팔꿈치·겨드랑 기준 · 어깨세모근 앞 경계','LI14':'팔꿈치·겨드랑 기준 · 어깨세모근 앞 경계','LI15':'봉우리 앞끝 · 위팔뼈 큰결절','LI16':'빗장뼈 봉우리끝 · 어깨뼈 가시','LI17':'반지연골 높이 · 목빗근 뒤 경계','LI18':'방패연골 위 경계 · 목빗근','LI19':'인중·콧구멍 경계 (모형 대응 미확정)','LI20':'콧방울·코입술고랑 (모형 대응 미확정)','TE1':'약지 손톱 뿌리 · 약지 끝마디뼈 · 엄지 관절 너비','TE2':'약지·새끼손가락 물갈퀴 경계 (표면 미확보)','TE3':'넷째·다섯째 손허리뼈 · 손허리손가락관절','TE4':'손가락폄근 힘줄 · 손목관절','TE5':'노뼈·자뼈 · 손목·팔꿈치머리 기준','TE6':'노뼈·자뼈 · 손목·팔꿈치머리 기준','TE7':'자뼈 노쪽 경계 · 아래팔 근막','TE8':'노뼈·자뼈 · 손목·팔꿈치머리 기준','TE9':'노뼈·자뼈 · 손목·팔꿈치머리 기준','TE10':'팔꿈치머리 · 뒤쪽 겨드랑 기준','TE11':'팔꿈치머리 · 뒤쪽 겨드랑·봉우리 기준','TE12':'팔꿈치머리 · 뒤쪽 겨드랑·봉우리 기준','TE13':'어깨세모근 뒤 경계 · 봉우리각·팔꿈치머리','TE14':'봉우리 뒤끝 · 위팔뼈 큰결절','TE15':'어깨뼈 위각 · 가로 승모근','TE16':'아래턱각 높이 · 목빗근 뒤 경계 (체표 정합 미확정)','TE17':'귓불 · 꼭지돌기 (귀 기준 미확보)','TE18':'꼭지돌기 · 귓불·이첨 곡선 (귀 기준 미확보)','TE19':'귓불·이첨 곡선 (귀 기준 미확보)','TE20':'이첨 (귀 기준 미확보)','TE21':'이주위패임 · 턱관절돌기 (귀 기준 미확보)','TE22':'귓바퀴 뿌리 · 관자머리털 경계 (미확보)','TE23':'안륜근 위가쪽 경계 · 모형 눈썹꼬리 지표'}
for channel in ['li','te']:
 p=R/f'atlas-data/acupoints/learner/{channel}-r1.json';d=json.loads(p.read_text())
 for c in d['concepts']:c['landmarkLabel']=labels[c['code']]
 p.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n')
p=R/'atlas-data/acupoints/learner/registry-r1.json';d=json.loads(p.read_text())
for r in d['packages']:
 for key,folder,file in [('learnerSha256','learner','learnerFile'),('observationSha256','observation','observationFile')]:r[key]=hashlib.sha256((R/'atlas-data/acupoints'/folder/r[file]).read_bytes()).hexdigest()
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
p=R/'atlas-web/src/viewer/acupoints/AcupointReview.tsx';s=p.read_text().replace("{concept?.romanization} · {catalog?", "{concept?.romanization&&`${concept.romanization} · `}{catalog?");p.write_text(s)
