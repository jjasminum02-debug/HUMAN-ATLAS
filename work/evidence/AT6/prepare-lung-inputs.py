"""Read-only AC2 proposals -> actual AT3/4 topology probe. Ray replay is NOT anatomical approval."""
from pathlib import Path
import json,hashlib
import numpy as np
R=Path(__file__).resolve().parents[3];E=Path(__file__).parent;read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
m=read(R/'atlas-data/acupoints/carriers/education-r1/manifest.json');context={k:m[k] for k in ['datasetRevision','frameId','unit','poseId']}
reasons={
'LU1':'첫째늑간 체표 지표와 앞정중선 기준 6 비례촌을 확인할 자료가 없습니다.',
'LU2':'쇄골 아래 오목·부리돌기 안쪽 지표와 6 비례촌을 확인할 자료가 없습니다.',
'LU3':'겨드랑 앞주름과 팔꿈치 주름의 위치·3 비례촌 기준이 없습니다.',
'LU4':'겨드랑 앞주름과 팔꿈치 주름의 위치·4 비례촌 기준이 없습니다.',
'LU5':'팔꿈치 주름·힘줄 가쪽 오목과 굽힌 팔꿈치 자세의 대응이 확인되지 않았습니다.',
'LU6':'팔꿈치·손목 주름 사이의 비례 기준과 7 비례촌 경로가 없습니다.',
'LU7':'힘줄 사이 오목·손목 주름과 1.5 비례촌 기준이 확인되지 않았습니다.',
'LU8':'노동맥·손목 주름과 1 비례촌 기준이 확인되지 않았습니다.',
'LU9':'손목 주름·노동맥·힘줄 안쪽 오목의 체표 대응이 확인되지 않았습니다.',
'LU10':'첫째중수골의 기준은 있지만 손바닥·손등 피부 경계가 없습니다.',
'LU11':'엄지 손톱은 확인했으나 노쪽 조갑각·피부와 0.1 손가락촌 기준이 없습니다.'}
carriers={};units=[];evidence=[];audits=[];concepts=[]
for side in ['right','left']:
 oldpath=R/f'work/evidence/acupoint-AC2/{side}-learning.json';old=read(oldpath)
 if side=='right':concepts=[{'code':c['code'],'nameKo':c['nameKo'],'romanization':c['romanization'],'channel':'LU','location':c['location']['text'],'landmarkLabel':c['landmarkLabel'],'textbook':'pending'} for c in old['concepts']]
 for c in m['chunks']:
  if c['id'] not in ['trunk-2',f'arm-{side}-0',f'arm-{side}-1',f'hand-{side}-0',f'finger-{side}-1-0',f'nail-fold-{side}-3-0']:continue
  raw=(R/'atlas-data/acupoints/carriers/education-r1'/c['file']).read_bytes();assert sha(raw)==c['sha256']
  pos=np.frombuffer(raw,dtype='<f4',count=c['vertices']*3).reshape(-1,3);idx=np.frombuffer(raw,dtype='<u2',offset=c['vertices']*24).reshape(-1,3).astype('<u4')
  ident=c['id']
  carriers[ident]={'id':ident,'revision':c['revision'],'topologySha256':sha(pos.tobytes()+idx.tobytes()),**context,'side':c['side'],'kind':m['kind'],'precision':m['precision'],'rights':m['rights'],'positions':pos.reshape(-1).tolist(),'indices':idx.reshape(-1).tolist()}
 for i in old['instances']:
  code=i['code'];oc=old['carrier'];p=np.array(oc['positions']).reshape(-1,3)[np.array(oc['indices']).reshape(-1,3)[i['triangle']]];p=np.array(i['barycentric'])@p
  family='trunk-2' if int(code[2:])<=2 else f'arm-{side}-1' if int(code[2:])<=4 else f'arm-{side}-0' if int(code[2:])<=9 else f'hand-{side}-0' if code=='LU10' else f'nail-fold-{side}-3-0'
  c=carriers[family];v=np.array(c['positions']).reshape(-1,3);t=np.array(c['indices']).reshape(-1,3);tri=v[t]
  # Exact front ray at original proposal XY. No nearest fallback or coordinate approval.
  den=(tri[:,1,1]-tri[:,2,1])*(tri[:,0,0]-tri[:,2,0])+(tri[:,2,0]-tri[:,1,0])*(tri[:,0,1]-tri[:,2,1]);valid=abs(den)>1e-12
  aa=np.divide((tri[:,1,1]-tri[:,2,1])*(p[0]-tri[:,2,0])+(tri[:,2,0]-tri[:,1,0])*(p[1]-tri[:,2,1]),den,out=np.zeros(len(den)),where=valid)
  bb=np.divide((tri[:,2,1]-tri[:,0,1])*(p[0]-tri[:,2,0])+(tri[:,0,0]-tri[:,2,0])*(p[1]-tri[:,2,1]),den,out=np.zeros(len(den)),where=valid);cc=1-aa-bb
  hits=np.flatnonzero(valid&(aa>=0)&(bb>=0)&(cc>=0));addr=None
  if len(hits):
   j=int(hits[np.argmax((aa[:,None]*tri[:,0]+bb[:,None]*tri[:,1]+cc[:,None]*tri[:,2])[hits,2])]);addr={'triangle':j,'barycentric':[float(aa[j]),float(bb[j]),float(cc[j])]}
  concept=next(x for x in old['concepts'] if x['code']==code)
  uid=code+'-'+side;eid=uid+'-relation'
  evidence.append({'id':eid,'purpose':'location_relation','source':concept['standard'],'originalText':concept['location']['text']+' '+reasons[code], 'author':'ai','status':'unresolved','method':'none','side':side,'frameId':m['frameId'],'poseId':m['poseId'],'carrierHash':c['topologySha256'],'pointCode':code,'rights':{'localObservation':'supported','publicRedistribution':'held'}})
  units.append({'id':uid,'scope':'real_input','code':code,'side':side,'revision':'lung-location-at6-r1','context':context,'carrierId':family,'originalText':concept['location']['text'],'originalSources':concept['location']['sources'],'author':'ai','professorReview':'not_performed','landmarks':[],'rule':{'kind':'landmark','landmark':'unresolved-anatomical-point'},'relationEvidenceId':eid,'surfaceEvidenceId':uid+'-surface'})
  audits.append({'id':uid,'code':code,'side':side,'legacySourceSha256':sha(oldpath.read_bytes()),'legacyAiProposal':i['aiProposal'],'legacyCoordinateBasis':'AC2 bounds/envelope proposal, retained as proposal only','legacyWorld':p.tolist(),'actualCarrierId':family,'carrierHash':c['topologySha256'],'surfaceProbe':addr,'surfaceProbeMethod':'exact +Z ray at legacy XY, no nearest fallback; not anatomical evidence','learnerEligible':False,'missingInput':reasons[code],'nextAction':'Source-bound anatomical annotation and actual proportion/pose inputs; a regional envelope alone cannot supply these','nativeLandmarkKeys':i['landmarkSourceKeys']})
(E/'lung-rules.json').write_text(json.dumps({'schemaVersion':2,'context':context,'units':units,'inputs':{'domain':'real_input','carriers':carriers,'native':{},'evidence':evidence}},ensure_ascii=False,separators=(',',':'))+'\n')
(E/'surface-probes.json').write_text(json.dumps(audits,ensure_ascii=False,indent=2)+'\n')
out=R/'atlas-data/acupoints/learner';out.mkdir(parents=True,exist_ok=True)
(out/'lung.json').write_text(json.dumps({'schemaVersion':2,'usage':'local_learner_eligible',**context,'channel':'LU','concepts':concepts,'projections':[],'availability':[{'code':x['code'],'side':x['side'],'display':'unavailable','reason':x['missingInput']} for x in audits],'precisionCounts':{'precise':0,'educationalApproximation':0,'unresolved':22}},ensure_ascii=False,separators=(',',':'))+'\n')
print('units',len(units),'actual carrier views',len(carriers),'exact ray addresses',sum(a['surfaceProbe'] is not None for a in audits),'approved',0)
