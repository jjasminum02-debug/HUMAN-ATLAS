from pathlib import Path
E=Path(__file__).parent
exec((E/'author-corrections-r3.py').read_text().split("\nfor side in ['right','left']:")[0])
d=read(E/'rules-r3.json');units=d['units'];carriers=d['inputs']['carriers'];native=d['inputs']['native'];evidence=d['inputs']['evidence'];annotations=read(E/'annotations-r3.json');failures=read(E/'author-failures-r3.json');prepared={}
for u in units:
 if u['rule']['kind']=='landmark':prepared[u['side'],u['code']]=(carriers[u['carrierId']],u['landmarks'][0]['surface'],u['landmarks'])
def discard_failed(code,side):
 global units
 units=[u for u in units if not (u['code']==code and u['side']==side)]
for side in ['right','left']:
 sign=-1 if side=='right' else 1;post=[0,0,-1]
 # Precise deep-feature contexts remain checked; chosen superficial registration is physically local.
 sc,aca,acp=facet('Scapula',side,0,'min' if side=='right' else 'max',mask=lambda c:c[:,1]>1.38);hh,gt,gp=facet('Humerus',side,0,'min' if side=='right' else 'max',mask=lambda c:c[:,1]>1.36)
 replace('TE14',side,lambda:surface_direct('TE14',side,'arm-'+side+'-1',(acp+gp)/2,[sign,0,-1],[('Scapula',aca,'Posterior acromial-angle region'),('Humerus',gt,'Greater-tubercle facet')],'Scapular spinal part of deltoid muscle','Posterior shoulder interval between separately addressed acromion and greater tubercle; static model correspondence, no abducted depression.'))
 # Anterior versus posterior scapular views are independently addressed, never a point-bounds fit.
 cg,ca,cp=facet('Clavicle',side,0,'min' if side=='right' else 'max');sg,sa,sp=facet('Scapula',side,near=cp+np.array([0,-.008,-.015]))
 replace('LI16',side,lambda:surface_direct('LI16',side,'arm-'+side+'-1',(cp+sp)/2,[sign,0,-.3],[('Clavicle',ca,'Clavicle acromial end'),('Scapula',sa,'Scapular spine near acromial interval')],'Acromial part of deltoid muscle','Native AC-clavicle/scapular spine interval lateral to suprascapular fossa; coarse surface only.'))
 supg,supa,supp=facet('Scapula',side,1,'max',mask=lambda c:np.abs(c[:,0])<.10)
 replace('TE15',side,lambda:direct('TE15',side,'trunk-2',supp+np.array([0,.004,0]),post,[('Scapula',supa,'Superior medial scapular angle')],'Actual superior scapular angle source address plus source-supported superior contour; not whole-shoulder bounds.'))
 # LI13/14: nine-cun axillary-to-elbow native model interval, with actual lateral surface corridor.
 axdoc=read(R/'work/evidence/AT6/resume-r1/bilateral-rules-r9.json');axunit=next(u for u in axdoc['units'] if u['code']=='LU3' and u['side']==side);axref=axunit['landmarks'][0];axg=geometry('Clavicular part of deltoid muscle',side);axy=at(axg,axref['native'])[1]
 if (side,'LI11') in prepared and (side,'LI15') in prepared:
  c0,a0,l0=prepared[side,'LI11'];c1,a1,l1=prepared[side,'LI15'];p0=at(c0,a0);p1=at(c1,a1);f=(axy-p0[1])/(p1[1]-p0[1]);axp=p0+(p1-p0)*f
  try:
   c=carrier('arm-'+side+'-1');sf=address(c,axp,[sign,0,.3]);ng,na,npt=facet('Clavicular part of deltoid muscle',side,near=at(c,sf));lm0=lm('LI13',side,c,ng,na,sf,'Lateral upper-arm indicator at native axillary insertion plane','Independent AT6 native pectoral/deltoid axillary insertion plane defines9 B-cun to cubital joint; lateral LI11-LI15 corridor retained, no bounds ratio.');prepared[side,'ANTERIOR-AXILLA']=(c,sf,[lm0])
   for code,v in [('LI13',3),('LI14',7)]:replace(code,side,lambda code=code,v=v:proportion(code,side,'LI11','ANTERIOR-AXILLA',v,9,['arm-'+side+'-1'],'WHO p12 axillary-to-cubital9 B-cun and p40 LI13/14. Original static pectoral insertion proxy; source has no observed fold. Lateral corridor checked at native axillary plane.'))
  except Exception as ex:failures.append({'code':'LI13-LI14','side':side,'attempt':'Native axillary insertion plane and lateral surface calibration','error':str(ex),'neededInput':'Lateral source-supported axillary indicator and connected 9 B-cun corridor'})
 # Posterior axillary insertion is teres-major humeral end; source-specific annotation, not a generic height fraction.
 ug,ua,up=facet('Ulna',side,1,'max');tg,ta,tp=facet('Teres major muscle',side,0,'min' if side=='right' else 'max')
 try:
  c=carrier('arm-'+side+'-1');sf0=address(c,up,post);ng,na,np0=facet('Anconeus muscle',side,near=at(c,sf0));l0=lm('TE10',side,c,ng,na,sf0,'Olecranon joint plane superficial correspondence','Actual olecranon facet controls joint plane; anconeus is its local surface registration only.');prepared[side,'OLECRANON']=(c,sf0,[l0])
  sf1=address(c,tp,post);ng1,na1,np1=facet('Long head of triceps brachii',side,near=at(c,sf1));l1=lm('TE10',side,c,ng1,na1,sf1,'Posterior axillary teres-major insertion plane correspondence','Native teres-major humeral insertion defines authored posterior fold plane, distinct from observed skin crease.');prepared[side,'POSTERIOR-AXILLA']=(c,sf1,[l1])
  for code,v in [('TE10',1),('TE11',2),('TE12',5)]:
   replace(code,side,lambda code=code,v=v:proportion(code,side,'OLECRANON','POSTERIOR-AXILLA',v,9,['arm-'+side+'-1'],'WHO p12 posterior axillary-to-cubital9 B-cun; actual olecranon and teres-major insertion endpoints; source static arm, no flexed olecranon fossa.'))
   uu=next((u for u in units if u['code']==code and u['side']==side),None)
   if uu:uu['observedReferences']=[reference(code,side,carriers[uu['carrierId']],'Teres major muscle',ta,'Posterior axillary humeral insertion plane'),reference(code,side,carriers[uu['carrierId']],'Ulna',ua,'Actual olecranon anatomical joint endpoint')]
 except Exception as ex:failures.append({'code':'TE10-TE12','side':side,'attempt':'Source-addressed posterior axillary9 B-cun interval','error':str(ex),'neededInput':'Actual posterior fold/olecranon surface correspondence'})
 # TE7 exact calibrated3 B-cun plane, with independent just-radial-to-ulna path instead of TE6 duplicate.
 te6=next((u for u in units if u['code']=='TE6' and u['side']==side),None)
 if te6:
  ledger=read(E/'compiler-r3/ledger.json');inst=ledger['units'][te6['id']].get('instance')
  if inst:
   p6=at(carriers[inst['carrierId']],inst);ul,ula,ulp=slice_point('Ulna',side,p6[1],0,'min' if side=='right' else 'max');target=ulp+np.array([sign*.003,0,0])
   replace('TE7',side,lambda:surface_direct('TE7',side,inst['carrierId'],target,post,[('Ulna',ula,'Actual radial ulnar shaft border at3 B-cun plane')],'Extensor digitorum','Just radial to independently addressed ulna at native TE6 3 B-cun plane; distinct from interosseous midpoint. Original native relation and plane retained.'))
 # Mandible angle: actual ipsilateral posterior-inferior corner; paired SCM remains landmark; midline bone remains a context reference.
 mg,ma,mp=facet('Mandible',None,2,'min',mask=lambda c:(c[:,0]*sign>.025)&(c[:,1]<1.54));sg,sa,sp=slice_point('Sternocleidomastoid muscle',side,mp[1],2,'min')
 replace('TE16',side,lambda:surface_direct('TE16',side,'neck-link-0',sp,[sign,0,-.3],[('Sternocleidomastoid muscle',sa,'Posterior SCM at mandibular-angle height')],'Sternocleidomastoid muscle','Ipsilateral original mandibular angle level, posterior SCM contour; no whole-neck ratio.'))
 uu=next((u for u in units if u['code']=='TE16' and u['side']==side),None)
 if uu:uu['observedReferences']=[reference('TE16',side,carriers[uu['carrierId']],'Mandible',ma,'Actual ipsilateral mandibular angle, shared unpaired geometry retains midline identity')]
for name,data in [('rules-r4',{'schemaVersion':2,'context':context,'units':units,'inputs':{'domain':'real_input','carriers':carriers,'native':native,'evidence':evidence}}),('annotations-r4',annotations),('author-failures-r4',failures),('source-input-hashes-r4',inputs)]:
 (E/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
print('authored',len(units),'attempt failures',len(failures))
