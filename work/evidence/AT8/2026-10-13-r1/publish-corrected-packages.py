"""Compact compiler-only local projections. Historical failures and provenance remain development-only."""
from pathlib import Path
E=Path(__file__).parent
exec((E/'author-corrections-r3.py').read_text().split("\nfor side in ['right','left']:")[0])
VERSION='r13';d=read(E/f'rules-{VERSION}.json');carriers=d['inputs']['carriers'];native=d['inputs']['native'];ledger=read(E/f'compiler-{VERSION}/ledger.json');projections=read(E/f'compiler-{VERSION}/runtime-projection.json');catalog=read(R/'atlas-data/acupoints/observation/catalog-r1.json');failures=read(E/f'author-failures-r11.json');audits=[];pathsAudit=[]
regions=[('hand',{'LI1','LI2','LI3','LI4','TE1','TE2','TE3'},[.03,.04,.03],['Second metacarpal bone','Fourth metacarpal bone','Fifth metacarpal bone','Proximal phalanx of second finger of hand','Distal phalanx of second finger of hand','Distal phalanx of fourth finger of hand','Extensor digitorum']),('wrist',{'LI5','TE4'},[.045,.045,.04],['Radius','Ulna','Scaphoid bone','Extensor digitorum','Extensor pollicis longus','Extensor pollicis brevis','Extensor retinaculum of wrist']),('forearm',{'LI6','LI7','LI8','LI9','LI10','TE5','TE6','TE7','TE8','TE9'},[.045,.055,.045],['Radius','Ulna','Brachioradialis muscle','Extensor digitorum','Antebrachial fascia']),('elbow',{'LI11','LI12','TE10'},[.05,.06,.045],['Humerus','Ulna','Radius','Brachioradialis muscle','Anconeus muscle','Long head of triceps brachii']),('upper-arm',{'LI13','LI14','TE11','TE12','TE13'},[.055,.07,.045],['Humerus','Acromial part of deltoid muscle','Clavicular part of deltoid muscle','Long head of triceps brachii','Brachial fascia']),('shoulder',{'LI15','LI16','TE14','TE15'},[.065,.06,.06],['Humerus','Scapula','Clavicle','Clavicular part of deltoid muscle','Scapular spinal part of deltoid muscle','Acromial part of deltoid muscle','Descending part of trapezius muscle']),('neck',{'LI17','LI18','TE16'},[.038,.043,.043],['Sternocleidomastoid muscle','Platysma','Cricoid cartilage','Thyroid cartilage','Mandible']),('face',{'LI19','LI20','TE23'},[.032,.033,.025],['Nasalis muscle','Orbicularis oris muscle','Orbital part of orbicularis oculi','Maxilla','Zygomatic bone'])]
registry=read(R/'atlas-data/acupoints/learner/registry-r1.json');registry['packages']=[p for p in registry['packages'] if p['channel']=='LU']
remaining=[]
for channel,n in [('LI',20),('TE',23)]:
 accepted={ (i['code'],i['side']) for p in projections for i in p['instances'] if i['code'].startswith(channel)};availability=[];contexts=[];teaching=[];coords={};concepts=[]
 for i in range(1,n+1):
  code=f'{channel}{i}';reg,_,half,names=next(r for r in regions if code in r[1]) if any(code in r[1] for r in regions) else ('ear',set(),[.03,.04,.03],['Temporal bone'])
  concept=next(c for c in catalog['concepts'] if c['code']==code);concepts.append({'code':code,'nameKo':concept['nameKo'],'romanization':'','channel':channel,'location':facts['locations'][code],'landmarkLabel':' · '.join(names[:3]),'textbook':'pending'})
  for side in ['right','left']:
   key=(code,side);success=key in accepted;err=ledger['units'].get(f'{code}-{side}',{}).get('errors',[]);attempts=[f for f in failures if f['code']==code and f['side']==side];reason='' if success else '현재 모형에서 필요한 기준점과 체표 정합을 확인하지 못했습니다.'
   availability.append({'code':code,'side':side,'display':'educational_approximation' if success else 'unavailable','reason':reason})
   if not success:remaining.append({'code':code,'side':side,'locationRule':facts['locations'][code],'status':'unresolved','compilerErrors':err,'attempts':attempts,'inputRequired':(attempts[-1]['neededInput'] if attempts else 'Failed source-bound compiler correspondence; see errors')});continue
   u=ledger['units'][f'{code}-{side}'];inst=u['instance'];c=carriers[inst['carrierId']];p=at(c,inst);coords[key]={**inst,'carrierId':c['id']};lo=p-np.array(half);hi=p+np.array(half);parts=[]
   for name in names:
    ks=[k for k,r in rows.items() if r['names']['en']==name and r['side'] in [side,None]]
    if len(ks)!=1:continue
    k=ks[0];v,t=world(k);ids=np.flatnonzero(((v[t]>=lo)&(v[t]<=hi)).all(axis=(1,2)))
    if not len(ids):continue
    vv=v[np.unique(t[ids])];unit=read(R/'atlas-data/source-cache/datasets/za/units'/f'{k}.json');parts.append({'sourceKey':k,'name':name,'bounds':[vv.min(0).tolist(),vv.max(0).tolist()],'samplePositions':v[t[ids[np.linspace(0,len(ids)-1,min(3,len(ids))).astype(int)]]].mean(1).tolist(),'sourceSha256':unit['lods']['detail']['sha256'],'role':'bone' if ('bone' in name.lower() or 'phalanx' in name.lower() or name in ['Humerus','Radius','Ulna','Scapula','Clavicle','Mandible','Maxilla']) else 'muscle_tendon'});audits.append({'code':code,'side':side,'sourceKey':k,'triangleIds':ids.tolist(),'bounds':parts[-1]['bounds'],'clipBounds':[lo.tolist(),hi.tolist()],'sourceHash':parts[-1]['sourceSha256']})
   assert len(parts)>=2,(code,side,len(parts))
   normal=[(-.35 if side=='right' else .35),.04,-1] if reg in ['hand','wrist','forearm','elbow','upper-arm'] else [(-.55 if side=='right' else .55),.04,1]
   if code in ['TE14','TE15']:normal=[-.35 if side=='right' else .35,.04,-1]
   contexts.append({'code':code,'side':side,'point':p.tolist(),'placementBinding':{k:inst[k] for k in ['carrierId','carrierHash','triangle','barycentric']},'region':reg,'structures':parts,'preferredNormal':normal,'minimumSpan':float(max(np.ptp(np.concatenate([np.array(s['bounds']) for s in parts]),axis=0))),'mode':'point_and_structures','limitations':['Actual native local structure samples; point is AI educational structural approximation, not precise skin or professor-approved.']})
 for side in ['right','left']:
  for i in range(1,n):
   a=(channel+str(i),side);b=(channel+str(i+1),side)
   if a not in coords or b not in coords:continue
   ids={coords[a]['carrierId'],coords[b]['carrierId']};ids|={cid for cid in carriers if cid.startswith('arm-'+side) or cid=='wrist-link-'+side+'-0'}
   try:
    segments=path(sorted(ids),coords[a],coords[b],side)
    for s in segments:
     c=carriers[s['carrierId']];v,t=arrays(c);tri=v[t[s['triangle']]];normal=np.cross(tri[1]-tri[0],tri[2]-tri[0]);normal/=np.linalg.norm(normal);p0=np.array(s['from'])@tri+normal*.001;p1=np.array(s['to'])@tri+normal*.001
     teaching.append({'side':side,'fromCode':a[0],'toCode':b[0],'carrierId':c['id'],'carrierHash':c['topologySha256'],'triangle':s['triangle'],'fromBarycentric':s['from'],'toBarycentric':s['to'],'from':p0.tolist(),'to':p1.tolist()})
    pathsAudit.append({'from':a,'to':b,'segments':len(segments),'status':'source_surface_connected','noInteriorBranch':True})
   except Exception as ex:pathsAudit.append({'from':a,'to':b,'status':'gap_not_bridged','error':str(ex)})
 out={'schemaVersion':2,'usage':'local_learner_eligible',**context,'channel':channel,'concepts':concepts,'projections':[dict(p,instances=[i for i in p['instances'] if i['code'].startswith(channel)]) for p in projections if any(i['code'].startswith(channel) for i in p['instances'])],'availability':availability,'precisionCounts':{'precise':0,'educationalApproximation':len(accepted),'unresolved':2*n-len(accepted)}}
 obs={'schemaVersion':1,**context,'contexts':contexts,'teachingPaths':teaching,'placementInputSha256':sha((E/f'rules-{VERSION}.json').read_bytes())}
 lf=channel.lower()+'-r1.json';of=channel.lower()+'-context-r1.json';(R/'atlas-data/acupoints/learner'/lf).write_text(json.dumps(out,ensure_ascii=False,separators=(',',':'))+'\n');(R/'atlas-data/acupoints/observation'/of).write_text(json.dumps(obs,ensure_ascii=False,separators=(',',':'))+'\n')
 codes=[c['code'] for c in concepts];sections=[]
 for label,group in [('손끝·손등',range(1,5)),('손목·아래팔',range(5,11)),('팔꿈치·위팔',range(11,15)),('어깨',range(15,17)),('목·얼굴',range(17,n+1))] if channel=='LI' else [('손끝·손등',range(1,4)),('손목·아래팔',range(4,10)),('팔꿈치·위팔',range(10,14)),('어깨·목',range(14,17)),('귀·머리',range(17,n+1))]:sections.append({'name':label,'codes':[channel+str(i) for i in group]})
 registry['packages'].append({'id':channel.lower()+'-r1','channel':channel,'codes':codes,'learnerFile':lf,'observationFile':of,'sections':sections});print(channel,len(accepted),'contexts',len(contexts),'segments',len(teaching))
(R/'atlas-data/acupoints/learner/registry-r1.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n')
for name,data in [('remaining-units-r4',remaining),('context-geometry-audit-r4',audits),('route-audit-r4',pathsAudit)]:
 (E/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
