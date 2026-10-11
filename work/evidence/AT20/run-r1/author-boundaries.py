"""AT20 offline boundary authoring. Reads frozen carriers; emits no face mask/geometry."""
from pathlib import Path
from collections import Counter, defaultdict
import json, hashlib, subprocess
import numpy as np

R = Path(__file__).resolve().parents[4]
E = Path(__file__).parent
OUT = R/'atlas-data/acupoints/territories/AT20-r1'
OUT.mkdir(parents=True, exist_ok=True)
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
write = lambda p,d: p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
rules_path = R/'work/evidence/AT6/resume-r1/bilateral-rules-r9.json'
rules = read(rules_path)
generation = read(R/'work/evidence/AT3/generation.json')
catalog = read(R/'atlas-data/acupoints/who-361-catalog.json')

# Each short source claim is a point-location indicator, not a territorial polygon.
claims = {
 'LU':('LU6','팔꿈치–손목의 앞가쪽 연결 구간이 기본 위치 지표다.'),
 'LI':('LI15','어깨봉우리 앞끝과 위팔뼈 큰결절 사이가 위치 지표다.'),
 'ST':('ST36','정강이 앞쪽, 앞정강근과 무릎–발목 비례 구간이 지표다.'),
 'SP':('SP9','정강뼈 안쪽관절융기 아래와 안쪽모서리가 지표다.'),
 'HT':('HT3','팔꿈치 앞안쪽과 위팔뼈 안쪽위관절융기가 지표다.'),
 'SI':('SI11','어깨뼈가시 중점–아래각 사이의 비례 구간이 지표다.'),
 'BL':('BL40','무릎 뒤 오금주름과 양쪽 힘줄 사이가 지표다.'),
 'KI':('KI3','안쪽복사와 발꿈치힘줄 사이가 지표다.'),
 'PC':('PC7','손바닥쪽 손목의 긴손바닥근–노쪽손목굽힘근 힘줄 사이가 지표다.'),
 'TE':('TE5','아래팔 뒤쪽 노뼈–자뼈 사이와 손등쪽 손목주름이 지표다.'),
 'GB':('GB34','종아리뼈머리의 앞·먼쪽이 지표다.'),
 'LR':('LR3','발등 첫째–둘째 발허리뼈 바닥의 먼쪽 사이가 지표다.'),
 'CV':('CV12','배꼽과 칼몸통결합 사이, 앞정중선이 지표다.'),
 'GV':('GV14','제7목뼈 가시돌기 아래, 뒤정중선이 지표다.'),
}
sources = []
for channel,(code,summary) in claims.items():
 sources.append({'id':f'kmcric-{code}','title':f'KMCRIC 표준경혈 DB — {code}', 'edition':'public web, checked 2026-10-12','locator':'부위 / 취혈 (위치 관계만 사용)','url':f'https://www.kmcric.com/database/acupoint/{channel}/{code}',
  'retrievedDate':'2026-10-12','access':'primary_page_read','claim':summary,'claimKind':'point_landmark_relation','definesAreaBoundary':False,
  'rights':{'notice':'Copyright KMCRIC. All Rights Reserved.','localResearch':'short attributed factual paraphrase','fullTextRedistribution':'held','illustrationsRedistribution':'held'},'treatmentTextUsed':False})
sources += [
 {'id':'lingshu-jingjin-incipits','title':'靈樞 經筋 — classical Chinese incipits','edition':'Chinese Text Project parallel passages; full chapter fetch unavailable','locator':'node 81198, parallel incipits lines 861–896','url':'https://ctext.org/text.pl?node=81198&if=en&show=parallel','retrievedDate':'2026-10-12','access':'primary_chinese_incipits_read','claim':'12경근의 시작·결절 관계를 읽었다. 현대 근육 일대일 대응과 색 면 폭은 이 원문에서 확정하지 않는다.','claimKind':'sinew_text','definesAreaBoundary':False,'rights':{'localResearch':'attributed paraphrase of ancient text','digitalEditionRedistribution':'held','translationUsed':False}},
 {'id':'suwen-pibu','title':'素問 皮部論','edition':'Chinese Text Project, 四部叢刊 重廣補註黃帝內經素問','locator':'皮部論 — twelve skin divisions','url':'https://ctext.org/huangdi-neijing/pi-bu-lun/zh','retrievedDate':'2026-10-12','access':'primary_chinese_search_passage_read; direct open 403','claim':'피부 분부를 경맥과 연관하여 서술한다. 연속 외곽 polygon의 수치 경계는 확인되지 않았다.','claimKind':'cutaneous_text','definesAreaBoundary':False,'rights':{'localResearch':'attributed short paraphrase','digitalEditionRedistribution':'held','translationUsed':False}},
 {'id':'suwen-gukong','title':'素問 骨空論','edition':'Chinese Text Project, 四部叢刊 重廣補註黃帝內經素問','locator':'任脈 / 督脈 passages','url':'https://ctext.org/huangdi-neijing/gu-kong-lun/zh','retrievedDate':'2026-10-12','access':'primary_chinese_search_passage_read; direct open 403','claim':'임독맥의 주행·분지를 별도로 다룬다. 현재 전후 정중 학습 강조면과 전통 전체 유주를 동일시하지 않는다.','claimKind':'extraordinary_vessel_text','definesAreaBoundary':False,'rights':{'localResearch':'attributed short paraphrase','digitalEditionRedistribution':'held','translationUsed':False}},
 {'id':'kmcric-LU8','title':'KMCRIC 표준경혈 DB — LU8','edition':'public web, checked 2026-10-12','locator':'부위 / Note','url':'https://www.kmcric.com/database/acupoint/LU/LU8','retrievedDate':'2026-10-12','access':'primary_page_read','claim':'경거는 아래팔 앞가쪽의 노뼈붓돌기–노동맥 사이, 태연보다 몸쪽인 관계다.','claimKind':'point_landmark_relation','definesAreaBoundary':False,'rights':{'localResearch':'short attributed factual paraphrase','fullTextRedistribution':'held'},'treatmentTextUsed':False},
]
write(E/'source-register-r1.json', {'sources':sources,'attachmentPhotos':{'suppliedThisTask':False,'allowedUse':'colour expression only','boundaryEvidence':False},'publicSourceFailures':[{'url':'https://www.kmcric.com/database/acupoint/CV/CV17','failure':'web fetch unavailable','alternativeUsed':'verified CV12 primary page'}, {'url':'https://ctext.org/huangdi-neijing/jing-jin/zh','failure':'403','alternativeUsed':'readable primary Chinese parallel incipits; complete branch coverage not claimed'}]})

# View entries below are explicitly AI construction plans. They are not source transcriptions.
# Ordered lists are candidate landmarks to annotate in future packages, not new positions.
views = {
 'LU':(['쇄골 아래 흉부','위팔 앞가쪽','아래팔 앞가쪽','무지구'],[],['요측 아래팔','엄지']),
 'LI':(['검지 요측','위팔 앞가쪽','어깨 앞쪽','콧방울 옆'],['뒷목 교차 범위 미확인'],['노뼈 쪽 아래팔','어깨봉우리']),
 'ST':(['눈 아래','앞가슴','배 앞면','넙다리 앞면','정강이 앞면'],[],['턱·목 옆','둘째발가락']),
 'SP':(['안쪽 다리','배·가슴 앞면'],[],['엄지발가락 안쪽','정강뼈 안쪽','옆가슴']),
 'HT':(['위팔·팔꿈치 앞안쪽','손바닥 새끼손가락 쪽'],[],['겨드랑','자쪽 손목']),
 'SI':(['얼굴·귀 앞 연결 후보'],['어깨뼈 구간','위팔 뒤쪽'],['새끼손가락 자측','팔꿈치 안쪽뒤','목 옆']),
 'BL':(['눈 안쪽·이마 후보'],['척추 양옆 두 줄','넙다리 뒤','오금','종아리 뒤'],['뒤가쪽 발목','새끼발가락']),
 'KI':(['앞몸통','안쪽 넙다리 후보'],['안쪽 종아리 뒤 후보'],['안쪽복사–발꿈치힘줄','발바닥 접근']),
 'PC':(['가슴·위팔 안쪽','아래팔 앞 중앙','손바닥·중지'],[],['겨드랑 아래 연결 후보']),
 'TE':([],['손등·아래팔 뒤 중앙','위팔 뒤','어깨 뒤'],['약지','귀 뒤·관자·눈썹끝']),
 'GB':(['이마·골반 앞가쪽 후보'],['후두·어깨 뒤 후보'],['관자·귀 주변','옆가슴','넙다리 가쪽','종아리뼈쪽','넷째발가락']),
 'LR':(['안쪽 다리','서혜부·아랫배','앞가쪽 가슴'],[],['첫째–둘째 발허리뼈','안쪽 무릎']),
 'CV':(['앞정중 배·가슴·목·턱'],[],['정중 폭을 확인하는 측면 점검','회음 접근']),
 'GV':(['코·윗입술 연결 후보'],['뒤정중 천골·척추·목','머리 정중'],['두피 경계·구강·회음 접근']),
}
uncertainties = {
 'LU':'경맥의 검지 분지와 경근의 흉부·횡격막 관계는 이 아래팔 학습 면에 포함하지 않는다. 흉부/손목/엄지 다른 carrier와의 연속 경계는 별도 작성이 필요하다.',
 'LI':'검지–팔–얼굴 구간의 폭, 입 주변 좌우 교차와 어깨봉우리 앞뒤 분리 미작성. 내행을 앞몸통에 투사하지 않는다.',
 'ST':'흉부/배 폭과 머리·목 분지 외곽선 미확정. 무릎 아래 지표 하나로 얼굴·복부 전체 면을 확정할 수 없다.',
 'SP':'안쪽복사/무릎의 지표와 가슴·옆가슴 연결 폭을 분리해야 한다. 간·신경과 겹침을 강제로 배타 분할하지 않는다.',
 'HT':'소장/심포와의 팔 안쪽 폭 분할 미확정. 굽힌 팔오금 주름은 정지 모형의 실제 주름으로 관찰되지 않는다.',
 'SI':'어깨뼈의 지표를 확인할 수 있는 규칙과 귀·얼굴 분지 폭은 별개다. 어깨 전체를 자동 채우지 않는다.',
 'BL':'척추 양옆 두 줄 사이/바깥 폭 및 후두·둔부 분지의 합류 경계 미확정. 뒤쪽 전부를 방광경으로 배정하지 않는다.',
 'KI':'발바닥/발뒤꿈치의 지원 영역과 실제 발바닥 피부 결손을 대조해야 한다. 내부 신장·흉부 연결을 피부 띠로 만들지 않는다.',
 'PC':'힘줄 사이 위치 지표가 손바닥/가슴 전체의 경계는 아니다. 심경/폐경과 사이의 폭과 손바닥 분지 미작성.',
 'TE':'손등–귀 주변의 분지와 얼굴 외곽선 미확정. PC6 앞뒤 관계를 두 점 사이 관통 면으로 만들지 않는다.',
 'GB':'머리의 여러 교차/분지를 하나의 큰 얼굴 면으로 병합하지 않는다. 몸통 옆/둔부/다리 가쪽 폭 미확정.',
 'LR':'서혜·외생식/내부 주행과 실제 외피 구간을 분리해야 한다. 회음 피부 결손을 허벅지로 대체하지 않는다.',
 'CV':'회음 피부가 없고 구강 점막 일부가 없다. 앞정중 강조 폭은 AI 디자인 값이며 13번째 경근이 아니다.',
 'GV':'구강 잇몸·소대 표면이 없다. 뒤정중/두피 강조 폭과 전통 분지는 별도이며 14번째 경근이 아니다.',
}
incipits = {'LU':'엄지·무지구·손목·팔꿈치','LI':'검지·손목·팔꿈치 바깥','ST':'발가락·발등·무릎 바깥','SP':'엄지발가락 안쪽·안쪽복사','HT':'새끼손가락 안쪽·손목·팔꿈치 안쪽','SI':'새끼손가락·손목·팔꿈치 뒤','BL':'새끼발가락·복사','KI':'작은 발가락 아래','PC':'중지·팔꿈치 안쪽','TE':'약지·손목·팔꿈치','GB':'넷째발가락·바깥복사','LR':'엄지발가락·안쪽복사 앞'}
definitions=[]
for ch in catalog['channels']:
 code=ch['code'];sample,claim=claims[code];vf,vb,vs=views[code]
 definitions.append({'channel':code,'nameKo':ch['nameKo'],'sideRule':'midline' if code in ['CV','GV'] else 'independent_bilateral_annotations','revision':'AT20-r1','kind':'teaching_region','basisKind':'surface_learning_connection',
  'status':'boundary_input_ready_partial' if code=='LU' else 'evidence_ledger_only','canonicalBoundaryClaim':False,'interpretation':'ai_proposal','author':'ai','professorReview':'not_performed','publicRedistribution':'held',
  'sourceRelations':[{'sourceId':f'kmcric-{sample}','summary':claim,'scope':'single-point landmark indicator, no continuous boundary'}],
  'types':{'surfaceLearning':{'kind':'surface_learning_connection','status':'authored_draft','scope':'external supported surface only'},'sinew':{'kind':'sinew_projection','status':'incipit_only_no_mask','sourceId':'lingshu-jingjin-incipits','indicator':incipits[code],'remaining':'full branches, joints and modern muscle correspondence not reviewed'} if code in incipits else {'kind':'sinew_projection','status':'not_applicable','reason':'임독맥은 12경근 원장에 추가하지 않음'},'cutaneous':{'kind':'cutaneous','status':'boundary_unresolved','sourceId':'suwen-pibu','remaining':'classical skin division does not establish polygon edges; no observed skin territories'},'professorInterpretation':{'kind':'professor_interpretation','status':'not_supplied','sourceId':None,'remaining':'교수 원문·판본·지정 경계 피드백 없음'}},
  'viewDrafts':{v:{'indicators':terms,'status':'ai_plan_unregistered' if terms else 'no_area_authored','boundaryRule':'Annotate these local landmarks on the actual side/pose; close on one connected carrier. Empty lists mean no proposed posterior/anterior area, not proof of absence.','sourceBoundary':False} for v,terms in [('anterior',vf),('posterior',vb),('lateral',vs)]},
  'branchRule':{'external':'independent contour for each supported branch; overlap allowed','internal':'text-only separate relation, never projected onto outer skin','sinew':'independent source/branch relation, never inferred from point order','unresolved':uncertainties[code]},
  'boundaryRule':{'width':'AI local interpretation, requires separate controls; no nearest-line buffer or canonical fixed width','seams':'split contour at missing faces/components; no spatial bridges','sides':'read each actual side; reflection is not validation','overlap':'do not assign exclusivity to another channel or dermatome'},
  'carrierPlanning':{'manifest':'atlas-data/acupoints/carriers/education-r1/manifest.json','grade':'native-derived educational envelope, not skin scan','registeredControls':'lung-forearm-right-boundary-r1.json' if code=='LU' else None,'supportedSurfaceLimits':uncertainties[code]},'uncertainties':[uncertainties[code],'본 task의 표본 밖 native annotation·최종 face mask 미작성','교재 판본·교수 검토·공개 재배포 미확정'],'finalMasks':0})
write(OUT/'definitions-r1.json',{'schemaVersion':1,'usage':'offline_authoring_only','contract':'territoryBoundary.ts','sourceRegister':'work/evidence/AT20/run-r1/source-register-r1.json','definitions':definitions,'canonicalBoundaryClaim':False,'finalMaskCount':0})

# One real LU forearm boundary, intentionally stopping before the native-envelope pinch.
# Angles 0..12: anterior through the subject-right radial border. Ring1..16 includes
# the actual LU6/LU7/LU8 educational placements. Bounds ratios do not define anatomy.
c = rules['inputs']['carriers']['arm-right-0']
v=np.array(c['positions']).reshape(-1,3);t=np.array(c['indices']).reshape(-1,3)
mp=np.array(generation['chunkSourceGridMappings'][c['id']]);angle=mp%40;level=mp//40
selected=np.all((angle[t]<=12)&(level[t]>=1)&(level[t]<=16),axis=1)
faces=t[selected];counts=Counter(tuple(sorted(e)) for tri in faces for e in [(tri[0],tri[1]),(tri[1],tri[2]),(tri[2],tri[0])]);edges=[e for e,n in counts.items() if n==1]
graph=defaultdict(list)
for a,b in edges:graph[int(a)].append(int(b));graph[int(b)].append(int(a))
assert all(len(ns)==2 for ns in graph.values()),'pinched contour: split/revise before acceptance'
loops=[]
while graph:
 start=min(graph);prev=None;p=start;loop=[]
 while True:
  loop.append(p);q=next(n for n in graph[p] if n!=prev);prev,p=p,q
  if p==start:break
 for p in loop:del graph[p]
 loops.append(loop)
loops.sort(key=len,reverse=True)
def anchor(vertex):
 fi=int(np.flatnonzero((t==vertex).any(axis=1))[0]);b=[0,0,0];b[list(t[fi]).index(vertex)]=1
 return {'carrierId':c['id'],'carrierRevision':c['revision'],'carrierHash':c['topologySha256'],'frameId':c['frameId'],'unit':'m','poseId':c['poseId'],'side':'right','triangle':fi,'barycentric':b}
landmarks=[]
for code in ['LU6','LU7','LU8']:
 u=next(x for x in rules['units'] if x['id']==code+'-right')
 for l in u['landmarks']:
  if l['id'] not in [z['id'] for z in landmarks]:landmarks.append({'id':l['id'],'anatomy':l['anatomy'],'native':l['native'],'surface':l['surface'],'sourceKey':l['sourceKey'],'modelIndicator':l.get('modelIndicator'),'inputFile':str(rules_path.relative_to(R)),'inputSha256':sha(rules_path),'locator':f'units[{u["id"]}].landmarks[{l["id"]}]'})
boundary={'schemaVersion':1,'usage':'offline_authoring_only','id':'LU-forearm-right','channel':'LU','side':'right','revision':'AT20-r1','kind':'teaching_region','basisKind':'surface_learning_connection','boundaryRevision':'LU-forearm-r1','interpretation':'ai_proposal','author':'ai','professorReview':'not_performed','canonicalBoundaryClaim':False,'precision':'educational_approximation_not_skin','context':rules['context'],
 'rights':{'localObservation':'supported','publicRedistribution':'held','sourceIds':['ZA-CC-BY-SA-4.0','BP3D-CC-BY-SA-2.1-JP']},
 'carrierBinding':{'manifest':'atlas-data/acupoints/carriers/education-r1/manifest.json','manifestSha256':sha(R/'atlas-data/acupoints/carriers/education-r1/manifest.json'),'id':c['id'],'topologySha256':c['topologySha256'],'component':'arm-right','noNewGeometry':True},
 'sources':[sources[0]|{'locator':'LU6, forearm anterior-lateral relation'}, sources[-1]],
 'landmarks':landmarks,'linkedEducationalPoints':['LU6-right','LU7-right','LU8-right'],'pointInputSha256':sha(rules_path),'learnerSha256':sha(R/'atlas-data/acupoints/learner/lung-r7.json'),
 'construction':{'anatomicalRelation':'Verified LU5 cubital structural endpoint / LU9 radiocarpal structural endpoint; LU6 lies in their anterolateral interval. LU7 APL/EPB interval and LU8 radial-styloid context are retained independently. No radial artery/crease is observed.',
 'proximalStop':'ring16 Y=1.002126932m just proximal to actual LU6; next ring17 at Y=1.010634899m has a pinched contour at angular index3. Stop rather than fill that defect.',
 'distalStop':'ring1 Y=0.874507964m just distal to actual LU8; do not bridge the wrist-link seam to LU9.',
 'widthRule':'AI anterior-to-radial-sector learning window: AT3 actual grid angular indices0..12. Deliberately broadens the source line to include separately verified LU7; no source defines this 108-degree display width.',
 'holes':'retain the two native-envelope rejected-face holes as exclusion loops','generationReference':'work/evidence/AT3/generation.json','generationSha256':sha(R/'work/evidence/AT3/generation.json'),'gridSelection':{'ringInclusive':[1,16],'angleInclusive':[0,12]},'geodesicIsAnatomicalProof':False},
 'components':[{'id':'right-forearm','carrierId':c['id'],'seedTriangle':1174,'loops':[{'role':'outer' if n==0 else 'hole','controls':[{'id':f'loop{n}-v{x}','vertex':x,'anchor':anchor(x)} for x in loop]} for n,loop in enumerate(loops)]}],
 'handoff':{'nextUnit':'AT21','operation':'Validate frozen carrier bytes and context; treat consecutive loop vertex pairs including closing edge as barriers; flood face adjacency from seed1174. Preserve holes and component boundaries. Emit compact triangleIds/weights there, using shared carrier and overlay; no duplicate body mesh.','expectedFaceCountForReplay':int(selected.sum()),'candidateFaceSetSha256':hashlib.sha256(np.flatnonzero(selected).astype('<u4').tobytes()).hexdigest(),'finalMaskCreated':False},
 'limitations':['right forearm partial region only; no complete LU territory','left control addresses not authored; do not reflect these controls','no literal skin, classical cutaneous boundary, complete jingjin or clinical/treatment radius','source controls preserve actual rejected-face holes; alpha/feather to be tested in AT21','LU1–5/LU9–11 remain valid points outside this sample; no masks claimed for those segments']}
write(OUT/'lung-forearm-right-boundary-r1.json',boundary)

# Inventory is read-only, does not traverse originals or install/download any textbook.
cmd=['rg','--files','--hidden','--no-ignore','-g','*.pdf','-g','*.epub','-g','*.docx','-g','!node_modules/**','-g','!.git/**','atlas-data','work']
p=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
write(E/'acquired-material-inventory-r1.json',{'search':cmd,'exitCode':p.returncode,'documentFiles':p.stdout.splitlines(),'currentUserAcupunctureTextbook':'not_found_in_scoped_workspace','reusedAcquiredMaterial':[{'path':'atlas-data/acupoints/who-361-catalog.json','sha256':sha(R/'atlas-data/acupoints/who-361-catalog.json'),'scope':'AT1 code/name source ledger'},{'path':str(rules_path.relative_to(R)),'sha256':sha(rules_path),'scope':'AT6 WHO 2008/reprinted2009 location relations and native annotations; original PDF bytes not present in current scoped cache, not redownloaded'}],'professorMaterial':'not_supplied','textbookExplanationImport':False,'sourceDownloads':0})
print('14 definitions; LU boundary loops',list(map(len,loops)),'seed count',selected.sum(),'new masks 0')
