from pathlib import Path
E=Path(__file__).parent
exec((E/'author-corrections-r3.py').read_text().split("\nfor side in ['right','left']:")[0])
d=read(E/'rules-r7.json');units=d['units'];carriers=d['inputs']['carriers'];native=d['inputs']['native'];evidence=d['inputs']['evidence'];annotations=read(E/'annotations-r7.json');failures=read(E/'author-failures-r7.json');manifests['upper-yang-boundary-AT8-r2']=read(R/'atlas-data/acupoints/carriers/upper-yang-boundary-AT8-r2/manifest.json');prepared={}
for u in units:
 if u['rule']['kind']=='landmark':prepared[u['side'],u['code']]=(carriers[u['carrierId']],u['landmarks'][0]['surface'],u['landmarks'])
for side in ['right','left']:
 sign=-1 if side=='right' else 1;post=[0,0,-1];radial=[sign,0,-.4]
 mc,head,hp=facet('Second metacarpal bone',side,1,'min');ph,pb,pp=facet('Proximal phalanx of second finger of hand',side,1,'max')
 replace('LI2',side,lambda:direct('LI2',side,'mcp-link-'+side+'-0',(hp+pp)/2,radial,[('Proximal phalanx of second finger of hand',pb,'Radial distal MCP2 joint interval')],'Native MCP2 distal phalangeal base at actual MC2 articulation. Education red-white contour correspondence; no source skin-colour assertion.'))
 m4,h4,p4=facet('Fourth metacarpal bone',side,1,'min');m5,h5,p5=facet('Fifth metacarpal bone',side,near=p4)
 if side=='left':replace('TE3',side,lambda:direct('TE3',side,'mcp-link-'+side+'-0',(p4+p5)/2+np.array([0,.006,0]),post,[('Fourth metacarpal bone',h4,'MCP4 proximal interval'),('Fifth metacarpal bone',h5,'Intermetacarpal space MC4/MC5')],'Independently addressed left MC4/MC5 dorsal interval; no reflection or coordinate transplant.'))
 cg,ca,cp=facet('Clavicle',side,0,'min' if side=='right' else 'max');sg,sa,sp=facet('Scapula',side,near=cp+np.array([0,-.008,-.015]))
 replace('LI16',side,lambda:surface_direct('LI16',side,'girdle-link-0',(cp+sp)/2,[0,1,-.5],[('Clavicle',ca,'Acromial clavicle end'),('Scapula',sa,'Scapular spine adjoining acromial region')],'Acromial part of deltoid muscle','Local native-sampled shoulder cap supports actual acromial clavicle/scapular spine interval. No shoulder copy or fake depression.'))
 sg,sa,sp=facet('Scapula',side,1,'max',mask=lambda c:np.abs(c[:,0])<.10)
 replace('TE15',side,lambda:direct('TE15',side,'girdle-link-0',sp+np.array([0,.003,0]),post,[('Scapula',sa,'Superior medial scapular angle')],'Actual scapular superior angle and3mm superior teaching-contour correspondence. Independent lower-clearance native envelope remains outside original anatomy; not skin or precise palpable depression.'))
 mg,ma,mp=facet('Mandible',None,2,'min',mask=lambda c:(c[:,0]*sign>.025)&(c[:,1]<1.54));sg,sa,sp=slice_point('Sternocleidomastoid muscle',side,mp[1],2,'min')
 replace('TE16',side,lambda:surface_direct('TE16',side,'neck-upper-link-0',sp,[sign,0,-.3],[('Sternocleidomastoid muscle',sa,'Posterior SCM at native mandibular angle level')],'Sternocleidomastoid muscle','Native ipsilateral mandibular-angle plane at posterior SCM; verified local upper-neck carrier, no invented fold.'))
 uu=next((u for u in units if u['code']=='TE16' and u['side']==side),None)
 if uu:uu['observedReferences']=[reference('TE16',side,carriers[uu['carrierId']],'Mandible',ma,'Actual ipsilateral mandibular angle on unpaired source')]
 # Nasal ala is present as original cartilage. Model groove and philtrum are explicitly authored, not source skin.
 ag,aa,ap=facet('Major alar cartilage',side,0,'min' if side=='right' else 'max');_,aTop,pTop=facet('Major alar cartilage',side,1,'max');_,aBottom,pBottom=facet('Major alar cartilage',side,1,'min');mid=(pTop[1]+pBottom[1])/2;ag,ala,pAla=slice_point('Major alar cartilage',side,mid,0,'min' if side=='right' else 'max')
 replace('LI20',side,lambda:surface_direct('LI20',side,'head-0',pAla+np.array([sign*.001,0,0]),[0,0,1],[('Major alar cartilage',ala,'Actual lateral alar cartilage contour at named superior/inferior midpoint')],'Nasalis muscle','Native lateral alar cartilage midpoint; model nasolabial groove at adjacent lateral muscular contour. Source skin sulcus absent; structural education only.'))
 og,oa,op=facet('Orbicularis oris muscle',side,1,'max',mask=lambda c:np.abs(c[:,0])<.012);target=np.array([pBottom[0],(pBottom[1]+op[1])/2,(pBottom[2]+op[2])/2])
 replace('LI19',side,lambda:surface_direct('LI19',side,'head-0',target,[0,0,1],[('Major alar cartilage',aBottom,'Native nostril-base lateral cartilaginous boundary'),('Orbicularis oris muscle',oa,'Native upper-lip muscular margin')],'Depressor septi nasi','Explicit model philtrum midpoint between actual alar base and upper-lip margin, below lateral nostril boundary. Not observed nostril skin aperture or philtral crease; AI construction and uncertainty retained.'))
 # TE13 uses original posterior axillary9 B-cun to calibrate, not a guessed acromion denominator.
 ug,ua,up=facet('Ulna',side,1,'max');tg,ta,tp=facet('Teres major muscle',side,0,'min' if side=='right' else 'max');sg,ac,ap=facet('Scapula',side,0,'min' if side=='right' else 'max',mask=lambda c:c[:,1]>1.38);one=(tp[1]-up[1])/9
 if one>0:
  y=ap[1]-3*one;ng,na,np0=slice_point('Scapular spinal part of deltoid muscle',side,y,2,'min')
  replace('TE13',side,lambda:surface_direct('TE13',side,'arm-'+side+'-1',np0,post,[('Scapular spinal part of deltoid muscle',na,'Posteroinferior deltoid edge at derived anatomical3 B-cun plane')],'Scapular spinal part of deltoid muscle','Actual olecranon-to-teres-major posterior axillary9 B-cun calibrates3 B-cun below acromial-angle plane. Model calibration, not whole-arm bounds; static source deltoid edge addressed.'))
  uu=next((u for u in units if u['code']=='TE13' and u['side']==side),None)
  if uu:uu['observedReferences']=[reference('TE13',side,carriers[uu['carrierId']],'Scapula',ac,'Actual acromial-angle region'),reference('TE13',side,carriers[uu['carrierId']],'Teres major muscle',ta,'Native posterior axillary insertion'),reference('TE13',side,carriers[uu['carrierId']],'Ulna',ua,'Actual olecranon measurement endpoint')]
for name,data in [('rules-r8',{'schemaVersion':2,'context':context,'units':units,'inputs':{'domain':'real_input','carriers':carriers,'native':native,'evidence':evidence}}),('annotations-r8',annotations),('author-failures-r8',failures)]:
 (E/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
