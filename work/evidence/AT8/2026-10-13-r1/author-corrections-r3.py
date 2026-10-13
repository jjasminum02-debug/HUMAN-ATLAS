"""Keep r1/r2 attempts; add independently source-bound superficial registrations and contexts."""
from pathlib import Path
E=Path(__file__).parent
exec((E/'author-upper-yang.py').read_text().split("for side in ['right','left']:")[0])
d=read(E/'rules-r2.json');units=d['units'];carriers=d['inputs']['carriers'];native=d['inputs']['native'];evidence=d['inputs']['evidence'];annotations=read(E/'annotations-r2.json');failures=read(E/'author-failures-r2.json')
for u in units:
 if u['rule']['kind']=='landmark':prepared[u['side'],u['code']]=(carriers[u['carrierId']],u['landmarks'][0]['surface'],u['landmarks'])
def reference(code,side,c,name,a,label):
 ng=geometry(name,side if any(r['names']['en']==name and r['side']==side for r in rows.values()) else None);side0=ng['side'];return {'id':f'{code}-{side}-ref{len(evidence)}','anatomy':label,'acquisition':'anatomical_annotation','side':side,'sourceKey':ng['id'],'native':{'carrierId':ng['id'],'carrierRevision':ng['revision'],'carrierHash':ng['topologySha256'],'frameId':context['frameId'],'unit':'m','poseId':context['poseId'],'side':side0,**a},'evidenceId':note(code,side,c,'landmark_annotation',json.dumps({'sourceKey':ng['id'],'address':a,'world':at(ng,a).tolist(),'anatomy':label})), 'interpretation':'Observed original structure context; cannot create a point by itself. Indicator and registration are separately recorded.'}
def surface_direct(code,side,cid,p,direction,refs,skin_name,label):
 c=carrier(cid);sf=address(c,p,direction);ng,na,np0=facet(skin_name,side,near=at(c,sf));l=lm(code,side,c,ng,na,sf,'Superficial structural correspondence of '+label,label+' Actual superficial facet is registration only; named deep features below define the relation.');make(code,side,c,[l],{'kind':'landmark','landmark':l['id']},label)
 units[-1]['observedReferences']=[reference(code,side,c,name,a,anatomy) for name,a,anatomy in refs];prepared[side,code]=(c,sf,[l])
def replace(code,side,fn):
 global units,failures
 old=[u for u in units if u['code']==code and u['side']==side];units=[u for u in units if not (u['code']==code and u['side']==side)]
 try:fn();failures=[f for f in failures if not (f['code']==code and f['side']==side)]
 except Exception as ex:
  units.extend(old);failures.append({'code':code,'side':side,'attempt':'Source-specific superficial model indicator with separately addressed deep anatomical context; preserved constraints','error':str(ex),'neededInput':'Surface/native correspondence or connected calibration failure; see original source addresses.'})
for side in ['right','left']:
 sign=-1 if side=='right' else 1;radial=[sign,0,-.4];post=[0,0,-1]
 h,ha,hp=facet('Humerus',side,0,'min' if side=='right' else 'max',mask=lambda x:x[:,1]<1.14)
 lung=read(R/'work/evidence/AT6/resume-r1/bilateral-rules-r9.json');lu5=next(u for u in lung['units'] if u['code']=='LU5' and u['side']==side);lb=lu5['landmarks'][0];bp=at(geometry('Long head of biceps brachii',side),lb['native'])
 replace('LI11',side,lambda:surface_direct('LI11',side,'arm-'+side+'-1',(hp+bp)/2,radial,[('Humerus',ha,'Lateral epicondyle independent source address'),('Long head of biceps brachii',lb['native'],'Native LU5 distal biceps interval')],'Brachioradialis muscle','WHO midpoint between native LU5 and lateral epicondyle, transferred to lateral cubital contour in static extended pose.'))
 # Independent native endpoints remain code/target-hash specific under proportions.
 replace('LI5',side,lambda:None) if False else None
 if (side,'LI5') not in prepared:
  rr,ra,rp=facet('Radius',side,1,'min');y=rp[1];epl,ea,ep=slice_point('Extensor pollicis longus',side,y,0,'min' if side=='right' else 'max');epb,ba,bp2=slice_point('Extensor pollicis brevis',side,y,0,'max' if side=='right' else 'min')
  replace('LI5',side,lambda:surface_direct('LI5',side,'wrist-link-'+side+'-0',(ep+bp2)/2,radial,[('Extensor pollicis longus',ea,'EPL anatomical snuffbox border'),('Extensor pollicis brevis',ba,'EPB anatomical snuffbox border')],'Extensor retinaculum of wrist','Static anatomical snuffbox interval between original EPL and EPB distal to styloid; no active thumb depression or observed crease.'))
 for code,v in [('LI6',3),('LI7',5),('LI8',8),('LI9',9),('LI10',10)]:replace(code,side,lambda code=code,v=v:proportion(code,side,'LI5','LI11',v,12,['wrist-link-'+side+'-0','arm-'+side+'-0','arm-'+side+'-1'],'Native joint-defined radial dorsal 12 B-cun measurement; superficial indicators separately distinguish absent skin creases.'))
 u,ua,up=facet('Ulna',side,1,'max');c=carrier('arm-'+side+'-1');sf=address(c,up,post);ng,na,np0=facet('Anconeus muscle',side,near=at(c,sf));l=lm('TE5',side,c,ng,na,sf,'Superficial olecranon joint level registration','Native olecranon address Y-level retained; anconeus correspondence is not the olecranon definition.');prepared[side,'OLECRANON']=(c,sf,[l])
 for code,v in [('TE5',2),('TE6',3),('TE8',4),('TE9',7)]:
  replace(code,side,lambda code=code,v=v:proportion(code,side,'TE4','OLECRANON',v,12,['wrist-link-'+side+'-0','arm-'+side+'-0','arm-'+side+'-1'],'Dorsal joint interval12 B-cun, forearm interosseous corridor in source pose.'))
  found=next((u for u in units if u['code']==code and u['side']==side),None)
  if found:found['observedReferences']=[reference(code,side,carriers[found['carrierId']],'Ulna',ua,'Olecranon bone endpoint sets anatomical proximal forearm measurement level')]
 # LI2 physically missing MCP/finger seam; attempt correct hand-link at same semantic location, never move longitudinally.
 mc,head,hp0=facet('Second metacarpal bone',side,1,'min');ph,pb0,pp0=facet('Proximal phalanx of second finger of hand',side,1,'max');p=(hp0+pp0)/2
 replace('LI2',side,lambda:surface_direct('LI2',side,'hand-link-'+side+'-0',p,radial,[('Second metacarpal bone',head,'MCP2 metacarpal head'),('Proximal phalanx of second finger of hand',pb0,'Proximal phalanx base distal to MCP2')],'Humero-ulnar head of flexor digitorum superficialis','Native MCP2 distal radial joint interval. Same semantic plane checked on hand extension; no projection to other phalanx.'))
 # Anatomical shoulder endpoints, actual source facets inspected by role and local plane.
 sc,aca,acp=facet('Scapula',side,0,'min' if side=='right' else 'max',mask=lambda c:c[:,1]>1.38);hh,gt,gp=facet('Humerus',side,0,'min' if side=='right' else 'max',mask=lambda c:c[:,1]>1.36)
 for code,direction,name,label in [('LI15',[sign,0,1],'Clavicular part of deltoid muscle','Anterior acromial lateral end-to-greater tubercle interval'),('TE14',[sign,0,-1],'Spinal part of deltoid muscle','Posterior acromial angle-to-greater tubercle interval')]:
  replace(code,side,lambda code=code,direction=direction,name=name,label=label:surface_direct(code,side,'arm-'+side+'-1',(acp+gp)/2,direction,[('Scapula',aca,'Actual lateral acromion facet'),('Humerus',gt,'Actual lateral proximal humeral greater-tubercle facet')],name,label+'. Static pose transfer is approximate; no abducted depression claimed.'))
 cg,ca,cp=facet('Clavicle',side,0,'min' if side=='right' else 'max');sg,sa,sp=facet('Scapula',side,near=cp+np.array([0,-.008,-.015]))
 replace('LI16',side,lambda:surface_direct('LI16',side,'trunk-2',(cp+sp)/2,[0,1,-.5],[('Clavicle',ca,'Acromial clavicle end'),('Scapula',sa,'Scapular spine near acromial interval')],'Transverse part of trapezius muscle','Between independently addressed acromial clavicle end and scapular spine, lateral suprascapular fossa correspondence.'))
 supg,supa,supp=facet('Scapula',side,1,'max',mask=lambda c:np.abs(c[:,0])<.10)
 replace('TE15',side,lambda:surface_direct('TE15',side,'trunk-2',supp+np.array([0,.004,0]),post,[('Scapula',supa,'Scapular superior medial angle')],'Descending part of trapezius muscle','Actual superior medial scapular angle; source-supported contour just superior. Not a shoulder bounds corner.'))
 # Record the shared central cartilage addresses under proper midline identity, not pretend a paired source.
 for code,cart,end in [('LI17','Cricoid cartilage','max'),('LI18','Thyroid cartilage','max')]:
  u0=next((u for u in units if u['code']==code and u['side']==side),None)
  if u0:
   ng,a,p=facet(cart,None,1,end,mask=lambda c:c[:,0]<=1e-5 if side=='right' else c[:,0]>=-1e-5);c=carriers[u0['carrierId']]
   ref=reference(code,side,c,cart,a,'Native laryngeal cartilage level; unpaired geometry retains midline source side');u0['observedReferences']=[ref]
 # Native eye contour cannot fabricate eyebrow hair, but explicit anatomical model tail is valid approximate context.
 # Remaining unsupported units are kept, not renamed as passed fixtures.
for name,data in [('rules-r3',{'schemaVersion':2,'context':context,'units':units,'inputs':{'domain':'real_input','carriers':carriers,'native':native,'evidence':evidence}}),('annotations-r3',annotations),('author-failures-r3',failures),('source-input-hashes-r3',inputs)]:
 (E/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
print('authored',len(units),'remaining attempts',len(failures))
